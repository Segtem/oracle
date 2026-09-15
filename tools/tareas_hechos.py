"""Extractor explícito de hechos relacionales del tracker de tareas (P3).

Genera un objeto JSON relacional que describe de forma determinista
el estado declarado de las tareas, el inventario de archivos del tracker, el
rastreo de referencias cruzadas y las omisiones justificadas.

Contrato compartido con políticas y arneses de evaluación de Oracle
(consumible por `oracle juzgar --proyecto ejemplo/seguimiento-tareas --con ARCHIVO.json`).
No realiza llamadas de red, no modifica archivos en disco y garantiza salida
idéntica byte por byte ante el mismo árbol.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import sys
import urllib.parse
from pathlib import Path, PurePosixPath
from typing import Any

from tools.tareas import (
    ARCHIVOS_AUXILIARES_PERMITIDOS,
    ParserDeSubcomando,
    RutaInsegura,
    Tarea,
    TareaError,
    auditar_tareas,
    resolver_raiz_tracker,
)

# Constantes del contrato de evidencia relacional
ESQUEMA_HECHOS = "oracle.tareas.hechos/v1"
LIMITE_MARKDOWN_BYTES = 2 * 1024 * 1024  # 2 MiB por archivo Markdown


def _lstat_seguro(path: Path) -> os.stat_result | None:
    """Ejecuta lstat y sólo considera ausencia ante FileNotFoundError o NotADirectoryError.

    Cualquier otro OSError (como PermissionError o fallos de E/S) se propaga
    como TareaError para que el comando falle con código 1 sin convertir errores
    operacionales en falsas ausencias.
    """
    try:
        return os.lstat(path)
    except (FileNotFoundError, NotADirectoryError):
        return None
    except OSError as e:
        raise TareaError(f"error operacional al acceder a {path}: {e}") from e


def _esta_escapado(linea: str, pos: int) -> bool:
    """Determina si un caracter en la posición pos está escapado por una cantidad impar de barras invertidas."""
    count = 0
    p = pos - 1
    while p >= 0 and linea[p] == "\\":
        count += 1
        p -= 1
    return count % 2 == 1


def _encontrar_spans_codigo(linea: str) -> list[tuple[int, int]]:
    """Encuentra intervalos (inicio, fin) de código en línea encerrado entre acentos graves."""
    # Una racha completa sólo cierra otra de igual longitud: tomar su sufijo
    # confundiría tres backticks con un cierre de dos. El iterador es finito.
    spans: list[tuple[int, int]] = []
    rachas = list(re.finditer(r"`+", linea))
    # Resolver la próxima racha de igual tamaño en una pasada inversa evita
    # volver a explorar todos los delimitadores por cada apertura (costo lineal).
    proximos = {}
    cierres = {}
    for racha in reversed(rachas):
        inicio = racha.start()
        if _esta_escapado(linea, inicio):
            inicio += 1
        cierre = proximos.get(racha.end() - inicio)
        if cierre is not None:
            cierres[inicio] = cierre
        # Dentro del código la barra no escapa el cierre: se conserva la racha entera.
        proximos[len(racha.group())] = racha
    consumido_hasta = 0
    for apertura in rachas:
        inicio = apertura.start()
        if _esta_escapado(linea, inicio):
            inicio += 1
        if inicio < consumido_hasta:
            continue
        cierre = cierres.get(inicio)
        if cierre is not None:
            spans.append((inicio, cierre.end()))
            consumido_hasta = cierre.end()
    return spans


def _esta_en_span(pos: int, spans: list[tuple[int, int]]) -> bool:
    """Verifica si una posición dada cae dentro de algún intervalo de código inline."""
    return any(inicio <= pos < fin for inicio, fin in spans)


def _cerrar_enlace_despues_destino(linea: str, pos: int) -> int | None:
    """Consume el cierre o un título entre comillas, sin interpretar su contenido."""
    n = len(linea)
    inicio = pos
    while pos < n and linea[pos] in " \t":
        pos += 1
    if pos < n and linea[pos] in ("'", '"') and pos > inicio:
        comilla = linea[pos]
        pos += 1
        while pos < n:
            if linea[pos] == comilla and not _esta_escapado(linea, pos):
                pos += 1
                break
            pos += 1
        else:
            return None
        while pos < n and linea[pos] in " \t":
            pos += 1
    if pos < n and linea[pos] == ")":
        return pos + 1
    return None


def _extraer_enlaces_linea(
    linea: str,
    spans_codigo: list[tuple[int, int]],
    *, spans_omitidos: list[tuple[int, int]] | None = None,
) -> tuple[list[tuple[int, int, str]], list[str]]:
    """Extrae enlaces inline y detecta enlaces por referencia no resueltos o sintaxis rota.

    Retorna:
      - Lista de tuplas (inicio, fin, destino_declarado) para enlaces inline extraídos.
      - Lista de motivos de omisión para sintaxis no soportada o incompleta.
    """
    enlaces: list[tuple[int, int, str]] = []
    omisiones: list[str] = []

    omitidos = [] if spans_omitidos is None else spans_omitidos

    # 2. Escaneo caracter por caracter de enlaces inline [texto](destino) e ![alt](destino)
    i = 0
    n = len(linea)
    while i < n:
        if _esta_en_span(i, spans_codigo):
            i += 1
            continue

        es_img = linea.startswith("![", i)
        es_link = (linea[i] == "[")
        pos_corchete = (i + 1) if es_img else i

        if (es_img or es_link) and not _esta_escapado(linea, pos_corchete):
            k = pos_corchete + 1
            encontrado_cierre = False
            while k < n:
                if _esta_en_span(k, spans_codigo):
                    k += 1
                    continue
                if linea[k] == "]" and not _esta_escapado(linea, k):
                    encontrado_cierre = True
                    break
                if linea[k] == "[" and not _esta_escapado(linea, k):
                    # Corchete anidado sin escapar
                    break
                k += 1

            if not encontrado_cierre:
                # Corchete que inicia enlace pero no cierra en la misma línea
                if k >= n:
                    omisiones.append("sintaxis de enlace incompleta o multilínea no admitida")
                i += 1
                continue

            # k está en ']'
            if k + 1 >= n or linea[k + 1] != "(":
                # No es enlace inline con destino (...)
                i = k + 1
                continue

            # Ahora k+1 es '('
            pos_par_abierto = k + 1
            m_pos = pos_par_abierto + 1
            while m_pos < n and linea[m_pos] in " \t":
                m_pos += 1

            par_cerrado = False

            if m_pos < n and linea[m_pos] == "<":
                ini_ang = m_pos + 1
                fin_ang = None
                p = ini_ang
                while p < n:
                    if linea[p] == ">" and not _esta_escapado(linea, p):
                        fin_ang = p
                        break
                    p += 1
                if fin_ang is not None:
                    destino_declarado = linea[ini_ang:fin_ang]
                    fin_link = _cerrar_enlace_despues_destino(linea, fin_ang + 1)
                    par_cerrado = fin_link is not None
            else:
                # Las parejas escapadas se consumen juntas: los paréntesis que
                # llegan a la rama siguiente necesariamente no están escapados.
                profundidad = 1
                p = m_pos
                contenido_chars: list[str] = []
                while p < n and profundidad > 0:
                    char = linea[p]
                    # Una barra final también se consume: sin carácter posterior
                    # no puede aportar el ')' obligatorio y el destino queda incompleto.
                    if char == "\\":
                        contenido_chars.append(linea[p : p + 2])
                        p += 2
                        continue
                    if char in " \t" and profundidad == 1:
                        break
                    if char == "(":
                        profundidad += 1
                        contenido_chars.append("(")
                    elif char == ")":
                        profundidad -= 1
                        if profundidad > 0:
                            contenido_chars.append(")")
                    else:
                        contenido_chars.append(char)
                    p += 1

                destino_declarado = "".join(contenido_chars)
                if profundidad == 0:
                    fin_link = p
                    par_cerrado = True
                elif p < n and linea[p] in " \t":
                    fin_link = _cerrar_enlace_despues_destino(linea, p)
                    par_cerrado = fin_link is not None

            if not par_cerrado:
                # El paréntesis '(' de destino no cierra en la misma línea (ej. [nota](\nausente.txt))
                omisiones.append("sintaxis de enlace incompleta o multilínea no admitida")
                # Sin cierre fiable no sabemos dónde termina el título. Omitir el
                # resto de esta línea también en la pasada posterior de autolinks.
                omitidos.append((i, n))
                break

            # Ambos caminos de cierre asignan destino y fin antes de llegar aquí.
            enlaces.append((i, fin_link, destino_declarado))
            i = fin_link
        else:
            i += 1

    # Las referencias por clave sólo son sintaxis fuera de destinos y títulos.
    cubiertos = [(ini, fin) for ini, fin, _ in enlaces] + omitidos + spans_codigo
    for m in re.finditer(r"(!?\[(?:\\.|[^\[\]\\])*\])\[([^\]]*)\]", linea):
        start = m.start()
        if _esta_en_span(start, cubiertos) or _esta_escapado(linea, start):
            continue
        omisiones.append(f"enlace por referencia no resuelto: {m.group(1)}[{m.group(2)}]")

    return enlaces, omisiones


def _clasificar_referencia(
    raiz: Path,
    origen_rel: str,
    num_linea: int,
    destino_declarado: str,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Clasifica una referencia extraída y evalúa su estado de presencia o alcance."""
    tarea_id = ""
    partes_origen = PurePosixPath(origen_rel).parts
    if len(partes_origen) >= 3 and partes_origen[0] == "tareas":
        tarea_id = partes_origen[1]

    base_ref: dict[str, Any] = {
        "tarea_id": tarea_id,
        "origen": origen_rel,
        "linea": num_linea,
        "destino_declarado": destino_declarado,
        "clase": "",
        "estado": "",
    }

    destino_lower = destino_declarado.lower()

    # 1. Remotas: http:// o https:// (insensible a mayúsculas/minúsculas)
    if destino_lower.startswith("http://") or destino_lower.startswith("https://"):
        base_ref["clase"] = "remota"
        base_ref["estado"] = "no_comprobado"
        return base_ref, None

    # 2. Anclas: #fragmento
    if destino_declarado.startswith("#"):
        base_ref["clase"] = "ancla"
        base_ref["estado"] = "no_comprobado"
        return base_ref, None

    # 3. Esquemas no admitidos o URLs de red (//)
    if destino_declarado.startswith("//"):
        base_ref["clase"] = "no_admitida"
        base_ref["estado"] = "no_comprobado"
        omision = {
            "ruta": origen_rel,
            "linea": num_linea,
            "motivo": f"URL de red o protocolo no admitida: {destino_declarado}",
        }
        return base_ref, omision

    match_esquema = re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", destino_declarado)
    if match_esquema:
        base_ref["clase"] = "no_admitida"
        base_ref["estado"] = "no_comprobado"
        omision = {
            "ruta": origen_rel,
            "linea": num_linea,
            "motivo": f"esquema no admitido en referencia: {destino_declarado}",
        }
        return base_ref, omision

    # 4. Referencias locales
    base_ref["clase"] = "local"

    # Quitar fragment y query string para resolver la ruta en disco
    destino_limpio = destino_declarado.split("#")[0].split("?")[0]
    # Los escapes pertenecen al Markdown original; una barra obtenida de %5C
    # forma parte del nombre y no debe reinterpretarse como sintaxis.
    destino_sin_escapes = destino_limpio.replace(r"\(", "(").replace(r"\)", ")")
    destino_decodificado = urllib.parse.unquote(destino_sin_escapes)
    if "\x00" in destino_decodificado:
        base_ref["clase"] = "no_admitida"
        base_ref["estado"] = "no_comprobado"
        return base_ref, {
            "ruta": origen_rel,
            "linea": num_linea,
            "motivo": "carácter NUL en referencia",
        }
    exige_directorio = destino_decodificado.endswith(("/", "/.")) or destino_decodificado == "."

    if destino_decodificado.startswith("//"):
        base_ref["clase"] = "no_admitida"
        base_ref["estado"] = "no_comprobado"
        omision = {
            "ruta": origen_rel,
            "linea": num_linea,
            "motivo": f"URL con host no admitida: {destino_declarado}",
        }
        return base_ref, omision

    # Determinar si es ruta absoluta en el sistema de archivos
    if destino_decodificado.startswith("/"):
        try:
            # Conservar .. hasta inspeccionar los componentes que lo preceden.
            rel_a_raiz = Path(destino_decodificado).relative_to(raiz)
            partes_recorrido = list(rel_a_raiz.parts)
            actual_partes: list[str] = []
        except ValueError:
            base_ref["estado"] = "fuera_del_proyecto"
            return base_ref, None
    else:
        dir_origen_rel = Path(origen_rel).parent
        actual_partes = list(dir_origen_rel.parts)
        partes_recorrido = [p for p in destino_decodificado.split("/") if p]

    # Ambas operaciones necesitan el mismo padre real antes de modificar la ruta.
    # Validarlo también para '.' evita convertir archivo/. en el archivo regular.
    for comp in partes_recorrido:
        ruta_actual = raiz.joinpath(*actual_partes)
        st = _lstat_seguro(ruta_actual)
        if st is None:
            base_ref["estado"] = "ausente"
            return base_ref, None
        if stat.S_ISLNK(st.st_mode):
            rel_link = ruta_actual.relative_to(raiz).as_posix()
            base_ref["estado"] = "no_comprobado"
            return base_ref, {
                "ruta": origen_rel,
                "linea": num_linea,
                "motivo": f"enlace simbólico en la ruta de referencia: {rel_link}",
            }
        if not stat.S_ISDIR(st.st_mode):
            base_ref["estado"] = "ausente"
            return base_ref, None
        if comp == ".":
            continue
        if comp == "..":
            if not actual_partes:
                base_ref["estado"] = "fuera_del_proyecto"
                return base_ref, None
            actual_partes.pop()
        else:
            actual_partes.append(comp)

    # Verificar el elemento final
    ruta_final = raiz.joinpath(*actual_partes)
    st_final = _lstat_seguro(ruta_final)
    if st_final is None:
        base_ref["estado"] = "ausente"
        return base_ref, None

    if stat.S_ISLNK(st_final.st_mode):
        rel_link = ruta_final.relative_to(raiz).as_posix()
        base_ref["estado"] = "no_comprobado"
        return base_ref, {
            "ruta": origen_rel,
            "linea": num_linea,
            "motivo": f"enlace simbólico en la ruta de referencia: {rel_link}",
        }

    if exige_directorio and not stat.S_ISDIR(st_final.st_mode):
        base_ref["estado"] = "ausente"
        return base_ref, None

    base_ref["estado"] = "presente"
    return base_ref, None


def _identidad_archivo(ruta: str) -> tuple[str, str]:
    """Clasifica rutas de tareas/ ya confinadas por el inventario o seguimiento Git."""
    partes = PurePosixPath(ruta).parts
    if len(partes) == 2:
        return "", "auxiliar"
    return partes[1], "documento" if partes[2:] == ("TAREA.md",) else "adjunto"


def _inventariar_archivos(
    raiz: Path,
    raiz_tareas: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Recorre `tareas/` de forma recursiva inventariando todos los archivos locales."""
    archivos: list[dict[str, Any]] = []
    omisiones: list[dict[str, Any]] = []

    def on_walk_error(err: OSError) -> None:
        raise TareaError(f"error operacional al recorrer el tracker de tareas: {err}")

    for dirpath_str, carpetas, filenames in os.walk(
        raiz_tareas, onerror=on_walk_error
    ):
        dirpath = Path(dirpath_str)

        carpetas_a_recorrer: list[str] = []
        for d in sorted(carpetas):
            subdir = dirpath / d
            rel_subdir = subdir.relative_to(raiz).as_posix()

            if d in (".git", ".hg", ".svn"):
                omisiones.append({
                    "ruta": rel_subdir,
                    "linea": 0,
                    "motivo": "metadatos de control de versiones",
                })
                continue

            st_subdir = _lstat_seguro(subdir)
            if st_subdir is None:
                continue

            if stat.S_ISLNK(st_subdir.st_mode):
                # os.walk clasifica estos enlaces como carpetas; inventariar el enlace sin entrar.
                filenames.append(d)
                continue

            if (subdir / ".git").exists():
                omisiones.append({
                    "ruta": rel_subdir,
                    "linea": 0,
                    "motivo": "repositorio anidado",
                })
                continue

            carpetas_a_recorrer.append(d)
        carpetas[:] = carpetas_a_recorrer

        for fname in sorted(filenames):
            archivo_path = dirpath / fname
            rel_posix = archivo_path.relative_to(raiz).as_posix()
            tarea_id, clase = _identidad_archivo(rel_posix)

            st = _lstat_seguro(archivo_path)
            if st is None:
                continue

            if stat.S_ISLNK(st.st_mode):
                tipo = "enlace"
                tamano = st.st_size
                omisiones.append({
                    "ruta": rel_posix,
                    "linea": 0,
                    "motivo": "enlace simbólico en el tracker",
                })
            elif stat.S_ISREG(st.st_mode):
                tipo = "regular"
                tamano = st.st_size
            else:
                tipo = "especial"
                tamano = 0
                omisiones.append({
                    "ruta": rel_posix,
                    "linea": 0,
                    "motivo": "archivo especial en el tracker (FIFO/dispositivo/socket)",
                })

            archivos.append({
                "tarea_id": tarea_id,
                "ruta": rel_posix,
                "clase": clase,
                "tipo": tipo,
                "tamano_bytes": tamano,
                "existe": True,
                "git_comprobado": False,
                "en_indice": False,
                "en_head": False,
                "ignorado": False,
                "indice": "",
                "trabajo": "",
            })

    return archivos, omisiones


def _prechequear_documentos_centrales(raiz: Path, raiz_tareas: Path) -> None:
    """Verifica que ningún TAREA.md central sea enlace simbólico ni supere 2 MiB antes de auditar."""
    try:
        entradas = sorted(raiz_tareas.iterdir())
    except OSError as e:
        raise TareaError(f"error operacional al listar {raiz_tareas}: {e}") from e

    for entrada in entradas:
        if entrada.name in ARCHIVOS_AUXILIARES_PERMITIDOS or entrada.name.startswith("."):
            continue
        st_dir = _lstat_seguro(entrada)
        if st_dir is not None and stat.S_ISLNK(st_dir.st_mode):
            raise RutaInsegura(f"la entrada del tracker {entrada.name} no puede ser un enlace simbólico")
        if st_dir is None or not stat.S_ISDIR(st_dir.st_mode):
            continue

        tarea_md = entrada / "TAREA.md"
        st = _lstat_seguro(tarea_md)
        if st is None:
            continue
        rel = tarea_md.relative_to(raiz).as_posix()
        if stat.S_ISLNK(st.st_mode):
            raise RutaInsegura(
                f"el documento central {rel} no puede ser un enlace simbólico"
            )
        if st.st_size > LIMITE_MARKDOWN_BYTES:
            raise TareaError(
                f"el documento central {rel} supera el límite de {LIMITE_MARKDOWN_BYTES // (1024 * 1024)} MiB"
            )


def extraer_hechos(raiz: Path, *, con_git: bool = False) -> dict[str, list[dict[str, Any]]]:
    """Extrae el conjunto de hechos relacionales del tracker de tareas bajo `raiz`."""
    raiz_tareas = raiz / "tareas"
    if not raiz_tareas.is_dir():
        raise TareaError(f"no se encontró el directorio {raiz_tareas}")
    if raiz_tareas.is_symlink():
        raise RutaInsegura(f"{raiz_tareas} no puede ser un enlace simbólico")

    # 1. Prechequeo acotado de documentos centrales TAREA.md
    _prechequear_documentos_centrales(raiz, raiz_tareas)

    # 2. Auditar tareas existentes: tareas corruptas fallan inmediatamente con código 1
    tareas_validas, problemas = auditar_tareas(raiz_tareas)
    if problemas:
        msg_problemas = "\n".join(f"  · {p}" for p in problemas)
        raise TareaError(
            f"se detectaron {len(problemas)} registro(s) inválido(s) en {raiz_tareas}:\n{msg_problemas}"
        )

    # 3. Inventariar archivos locales
    archivos, omisiones = _inventariar_archivos(raiz, raiz_tareas)

    # 4. Diagnóstico opcional de Git
    estado_git = "no_solicitado"
    head_git = ""
    if con_git:
        from tools import tareas_git

        datos_git = tareas_git.seguimiento(raiz)
        if datos_git.get("repositorio") is None:
            estado_git = "sin_repositorio"
        else:
            estado_git = "comprobado"
            head_git = datos_git.get("head") or ""

            git_por_ruta = {a["ruta"]: a for a in datos_git.get("archivos", [])}
            rutas_vistas = set()
            for arch in archivos:
                ruta_posix = arch["ruta"]
                rutas_vistas.add(ruta_posix)
                if ruta_posix in git_por_ruta:
                    g = git_por_ruta[ruta_posix]
                    arch["git_comprobado"] = True
                    arch["en_indice"] = bool(g["en_indice"])
                    arch["en_head"] = bool(g["en_head"])
                    arch["ignorado"] = bool(g["ignorado"])
                    arch["indice"] = str(g["indice"])
                    arch["trabajo"] = str(g["trabajo"])
                else:
                    arch["git_comprobado"] = True
                    # El inventario ya inicializó las seis columnas Git a vacío/falso.

            for a_git in datos_git.get("archivos", []):
                r_git = a_git["ruta"]
                if r_git not in rutas_vistas and not a_git["existe"]:
                    tarea_id, clase = _identidad_archivo(r_git)

                    archivos.append({
                        "tarea_id": tarea_id,
                        "ruta": r_git,
                        "clase": clase,
                        "tipo": "ausente",
                        "tamano_bytes": 0,
                        "existe": False,
                        "git_comprobado": True,
                        "en_indice": bool(a_git["en_indice"]),
                        "en_head": bool(a_git["en_head"]),
                        "ignorado": bool(a_git["ignorado"]),
                        "indice": str(a_git["indice"]),
                        "trabajo": str(a_git["trabajo"]),
                    })

    # 5. Generar `tarea_seguimiento`
    tarea_seguimiento: list[dict[str, Any]] = []
    for t in tareas_validas:
        ruta_md = t.ruta
        try:
            with open(ruta_md, "rb") as f:
                raw_bytes = f.read(LIMITE_MARKDOWN_BYTES + 1)
        except OSError as e:
            raise TareaError(f"error operacional al leer {ruta_md}: {e}") from e

        if len(raw_bytes) > LIMITE_MARKDOWN_BYTES:
            raise TareaError(
                f"el documento central {ruta_md.relative_to(raiz).as_posix()} supera el límite de 2 MiB"
            )

        sha256_doc = hashlib.sha256(raw_bytes).hexdigest()
        rel_md = ruta_md.relative_to(raiz).as_posix()
        tarea_seguimiento.append({
            "id": t.id,
            "titulo": t.titulo,
            "estado_declarado": t.estado,
            "prioridad_declarada": t.prioridad,
            "ruta": rel_md,
            "sha256_documento": sha256_doc,
        })

    # 6. Extraer referencias en documentos Markdown regulares dentro del tracker
    referencias: list[dict[str, Any]] = []

    for arch in archivos:
        if not arch["existe"] or arch["tipo"] != "regular":
            continue
        ruta_rel = arch["ruta"]
        if not ruta_rel.lower().endswith(".md"):
            continue

        archivo_abs = raiz / ruta_rel
        st = _lstat_seguro(archivo_abs)
        if st is None:
            continue

        if st.st_size > LIMITE_MARKDOWN_BYTES:
            omisiones.append({
                "ruta": ruta_rel,
                "linea": 0,
                "motivo": f"archivo Markdown supera el límite de {LIMITE_MARKDOWN_BYTES // (1024 * 1024)} MiB",
            })
            continue

        try:
            with open(archivo_abs, "rb") as f:
                raw = f.read(LIMITE_MARKDOWN_BYTES + 1)
        except OSError as e:
            raise TareaError(f"error operacional al leer {ruta_rel}: {e}") from e

        if len(raw) > LIMITE_MARKDOWN_BYTES:
            omisiones.append({
                "ruta": ruta_rel,
                "linea": 0,
                "motivo": f"archivo Markdown supera el límite de {LIMITE_MARKDOWN_BYTES // (1024 * 1024)} MiB",
            })
            continue

        if b"\x00" in raw:
            omisiones.append({
                "ruta": ruta_rel,
                "linea": 0,
                "motivo": "archivo Markdown contiene bytes nulos",
            })
            continue

        try:
            texto = raw.decode("utf-8")
        except UnicodeDecodeError:
            omisiones.append({
                "ruta": ruta_rel,
                "linea": 0,
                "motivo": "archivo Markdown con codificación inválida (no UTF-8)",
            })
            continue

        en_bloque_codigo = False

        for num_linea, linea in enumerate(texto.splitlines(), start=1):
            if not en_bloque_codigo:
                match_apertura = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})", linea)
                if match_apertura:
                    en_bloque_codigo = True
                    # La regex produce una racha homogénea: no hace falta indexarla.
                    delimitador_codigo = "`" if match_apertura.group(1).startswith("`") else "~"
                    tamano_delimitador = len(match_apertura.group(1))
                    continue
            else:
                # El cierre sólo admite espacios opcionales tras la cerca, sin info string
                match_cierre = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})[ \t]*$", linea)
                if (
                    match_cierre
                    and match_cierre.group(1).startswith(delimitador_codigo)
                    and len(match_cierre.group(1)) >= tamano_delimitador
                ):
                    en_bloque_codigo = False
                continue

            spans_codigo = _encontrar_spans_codigo(linea)

            # Definición de enlace por referencia [clave]: destino (con o sin espacios tras colon)
            match_def = re.match(r"^[ \t]{0,3}\[([^\]]+)\]:[ \t]*(\S*)", linea)
            if match_def:
                omisiones.append({
                    "ruta": ruta_rel,
                    "linea": num_linea,
                    "motivo": f"definición de enlace por referencia no resuelta: [{match_def.group(1)}]: ...",
                })
                continue

            spans_cubiertos: list[tuple[int, int]] = []

            # Comprobar líneas de URL agregadas por anotar: - URL: <url>
            match_url = re.match(r"^[ \t]*[-*][ \t]+URL[ \t]*:[ \t]*(\S+)", linea)
            if match_url:
                url_declarada = match_url.group(1)
                # match_url ya excluyó espacios y saltos: esta envoltura coincide
                # exactamente con un ángulo inicial y otro final, sin recortes parciales.
                envoltura_url = re.fullmatch(r"<(.*)>", url_declarada)
                if envoltura_url:
                    url_declarada = envoltura_url.group(1)
                spans_cubiertos.append(match_url.span(1))
                ref_dict, omision_opt = _clasificar_referencia(
                    raiz, ruta_rel, num_linea, url_declarada
                )
                referencias.append(ref_dict)
                if omision_opt:
                    omisiones.append(omision_opt)

            # Extraer enlaces inline y registrar omisiones de sintaxis no resuelta
            enlaces_inline, omisiones_sintaxis = _extraer_enlaces_linea(
                linea, spans_codigo, spans_omitidos=spans_cubiertos
            )
            for motivo_omision in omisiones_sintaxis:
                omisiones.append({
                    "ruta": ruta_rel,
                    "linea": num_linea,
                    "motivo": motivo_omision,
                })

            # Una fila por cada aparición encontrada
            for ini, fin, destino_declarado in enlaces_inline:
                spans_cubiertos.append((ini, fin))
                ref_dict, omision_opt = _clasificar_referencia(
                    raiz, ruta_rel, num_linea, destino_declarado
                )
                referencias.append(ref_dict)
                if omision_opt:
                    omisiones.append(omision_opt)

            # Comprobar autolinks <http...> (insensible a mayúsculas)
            for m_auto in re.finditer(r"<(https?://[^> \t\r\n]+)>", linea, re.IGNORECASE):
                start_auto, end_auto = m_auto.span()
                if _esta_en_span(start_auto, spans_codigo):
                    continue
                if any(sc[0] <= start_auto and end_auto <= sc[1] for sc in spans_cubiertos):
                    continue
                spans_cubiertos.append((start_auto, end_auto))
                url_auto = m_auto.group(1)
                ref_dict, omision_opt = _clasificar_referencia(
                    raiz, ruta_rel, num_linea, url_auto
                )
                referencias.append(ref_dict)
                if omision_opt:
                    omisiones.append(omision_opt)

    # 7. Deduplicar y ordenar omisiones
    omisiones_dedup: list[dict[str, Any]] = []
    omisiones_vistas: set[tuple[str, int, str]] = set()
    for o in omisiones:
        llave_o = (o["ruta"], o["linea"], o["motivo"])
        if llave_o not in omisiones_vistas:
            omisiones_vistas.add(llave_o)
            omisiones_dedup.append(o)

    omisiones_dedup.sort(key=lambda x: (x["ruta"], x["linea"], x["motivo"]))
    archivos.sort(key=lambda x: x["ruta"])
    tarea_seguimiento.sort(key=lambda x: x["id"])
    referencias.sort(key=lambda x: (x["origen"], x["linea"], x["destino_declarado"]))

    # 8. Construir fila única de `lectura_seguimiento`
    completa = len(omisiones_dedup) == 0
    lectura_seguimiento = [
        {
            "esquema": ESQUEMA_HECHOS,
            "completa": completa,
            "git": estado_git,
            "head": head_git,
        }
    ]

    return {
        "archivo_seguimiento": archivos,
        "lectura_seguimiento": lectura_seguimiento,
        "omision_seguimiento": omisiones_dedup,
        "referencia_seguimiento": referencias,
        "tarea_seguimiento": tarea_seguimiento,
    }


def cmd_hechos(argv: list[str], args: list[str]) -> int:
    """Punto de entrada para `oracle tarea hechos`."""
    parser = ParserDeSubcomando(
        prog="oracle tarea hechos",
        description="Emite hechos relacionales del tracker de tareas en formato JSON",
    )
    parser.add_argument(
        "--git",
        action="store_true",
        help="Comprueba estado frente al índice y HEAD de Git",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Salida en formato JSON (siempre activo)",
    )
    parser.add_argument(
        "--proyecto",
        default=None,
        help="Ruta explícita a la raíz del proyecto",
    )
    parsed = parser.parse_args(args)

    try:
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
        hechos = extraer_hechos(raiz, con_git=parsed.git)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Los nombres Unix pueden contener bytes ajenos a UTF-8, representados como surrogates.
    # El escape ASCII predeterminado conserva esos nombres dentro de JSON válido.
    salida_json = json.dumps(hechos)
    print(salida_json)
    return 0
