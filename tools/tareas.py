"""Tracker local de tareas y contexto de trabajo en Git.

Gestiona tareas en carpetas locales bajo `tareas/` usando Markdown editable y adjuntos
cercanos, con identidad estable e historia en Git. Independiente del catálogo de medidas.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.tareas_consulta import ConsultaInvalida, compilar

ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
ID_COMPLETO_RE = re.compile(r"^[0-9]{8}-[0-9]{6}(?:-[a-z0-9_-]+)*$")
LINEA_META_RE = re.compile(r"^[ \t]*[-*][ \t]+([A-Za-z0-9_-]+)[ \t]*:[ \t]*(.*)$")
ARCHIVOS_AUXILIARES_PERMITIDOS = frozenset({"README.md", "README", ".gitignore", "etiquetas"})


class TareaError(ValueError):
    """Error base del subsistema de tareas."""


class TareaInvalida(TareaError):
    """El archivo TAREA.md está mal formado o contiene datos inválidos."""


class TrackerNoEncontrado(TareaError):
    """No se encontró ningún tracker de tareas (`tareas/`) en el árbol."""


class RutaInsegura(TareaError):
    """Un identificador o ruta intenta escapar del confinamiento de tareas/."""


class TareaNoEncontrada(TareaError):
    """No se encontró la tarea especificada por ID o prefijo."""


class IdAmbiguo(TareaError):
    """El prefijo coincide con múltiples tareas candidatas."""


class ParserDeSubcomando(argparse.ArgumentParser):
    """Parser de argumentos que reporta errores sin volcar tracebacks."""

    def error(self, message: str) -> None:
        sys.stderr.write(f"ERROR: {self.prog}: {message}\n")
        sys.exit(2)


@dataclass
class Tarea:
    id: str
    titulo: str
    estado: str
    prioridad: int
    etiquetas: tuple[str, ...]
    campos_adicionales: dict[str, str]
    cuerpo: str
    ruta: Path

    def a_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "titulo": self.titulo,
            "estado": self.estado,
            "prioridad": self.prioridad,
            "etiquetas": list(self.etiquetas),
            "campos_adicionales": dict(self.campos_adicionales),
            "cuerpo": self.cuerpo,
            "ruta": str(self.ruta.resolve()),
        }


@dataclass
class ProblemaEtiquetas:
    categoria: str  # "redefinicion", "symlink", "fatal"
    mensaje: str


def _sanear_slug(texto: str) -> str:
    texto_norm = unicodedata.normalize("NFKD", texto)
    texto_ascii = "".join(c for c in texto_norm if not unicodedata.combining(c))
    limpio = re.sub(r"[^a-zA-Z0-9]+", "-", texto_ascii).strip("-").lower()
    return limpio


LARGO_SUFIJO_DERIVADO = 16


def _sufijo_del_titulo(titulo: str) -> str:
    """El sufijo que se deriva de un título cuando nadie pasó `--sufijo`.

    Eran 40 caracteres, y el ID entero es el prefijo de cada commit de ese trabajo: la tarea de
    0.18.0 salió `20260915-010206-juzgar-evidencia-real-desde-el-cli-0-18` y hubo que rehacer dos
    commits. Se corta en un límite de palabra y no a la mitad de una: el punto de tener sufijo es
    leer el listado de un vistazo, y media palabra se lee peor que una palabra menos.
    """
    slug = _sanear_slug(titulo)
    if len(slug) <= LARGO_SUFIJO_DERIVADO:
        return slug
    recortado = slug[:LARGO_SUFIJO_DERIVADO]
    # Si el corte cayó justo en un guion, la última palabra está entera y no hay nada que retroceder.
    if slug[LARGO_SUFIJO_DERIVADO] != "-" and "-" in recortado:
        recortado = recortado.rsplit("-", 1)[0]
    return recortado.rstrip("-")


def validar_seguridad_id(id_o_prefijo: str) -> None:
    if not isinstance(id_o_prefijo, str):
        raise RutaInsegura("el identificador de tarea debe ser texto")
    # El alfabeto cerrado de ID_RE excluye vacío, puntos, separadores y bytes nulos.
    if not ID_RE.fullmatch(id_o_prefijo):
        raise RutaInsegura(f"identificador inválido: {id_o_prefijo!r}")


def asegurar_confinamiento(raiz_tareas: Path, ruta_destino: Path) -> None:
    raiz_res = raiz_tareas.resolve()
    try:
        dest_res = ruta_destino.resolve(strict=True)
        dest_res.relative_to(raiz_res)
    except (FileNotFoundError, OSError, ValueError, RuntimeError) as e:
        raise RutaInsegura(f"la ruta {ruta_destino} escapa del directorio de tareas o es inválida") from e


def asegurar_confinamiento_archivo(raiz_tareas: Path, ruta_archivo: Path) -> None:
    raiz_res = raiz_tareas.resolve()
    try:
        dest_res = ruta_archivo.resolve(strict=True)
        dest_res.relative_to(raiz_res)
    except (FileNotFoundError, OSError, ValueError, RuntimeError) as e:
        raise RutaInsegura(
            f"el archivo {ruta_archivo} es un enlace simbólico que apunta fuera de tareas/ o está roto"
        ) from e


def resolver_raiz_tracker(
    argv: list[str] | None = None,
    *,
    permitir_crear: bool = False,
    ruta_explicita: str | Path | None = None,
) -> Path:
    """Resuelve la raíz del proyecto que aloja `tareas/`.

    Precedencia:
    1. `ruta_explicita`
    2. `--proyecto <ruta>` en `argv`
    3. `$ORACLE_PROYECTO` en variables de entorno
    4. Búsqueda local ascendente desde `Path.cwd()`, deteniéndose en el límite Git (.git).
    """
    elegida = ruta_explicita
    if elegida is None:
        argumentos = list(argv or [])
        if "--proyecto" in argumentos:
            idx = argumentos.index("--proyecto")
            if idx + 1 >= len(argumentos) or argumentos[idx + 1].startswith("-"):
                raise TareaError("falta la ruta: --proyecto <ruta>")
            elegida = argumentos[idx + 1]
        else:
            elegida = os.environ.get("ORACLE_PROYECTO") or None

    if elegida is not None:
        destino = Path(elegida).expanduser().resolve()
        if destino.is_file():
            raise TrackerNoEncontrado(f"{destino} es un archivo, se esperaba un directorio")
        if not permitir_crear and not (destino / "tareas").is_dir():
            raise TrackerNoEncontrado(f"el directorio {destino} no tiene `tareas/`")
        return destino

    actual = Path.cwd().resolve()
    recorrido = actual
    while True:
        if (recorrido / "tareas").is_dir():
            return recorrido
        if (recorrido / ".git").exists():
            # Límite Git alcanzado: si no tiene tareas/, no subir más
            break
        if recorrido.parent == recorrido:
            break
        recorrido = recorrido.parent

    if permitir_crear:
        return actual

    raise TrackerNoEncontrado(
        "no se encontró ningún tracker de tareas (`tareas/`). Usá `oracle tarea init` para crearlo."
    )


def parsear_tarea(texto: str, ruta: Path) -> Tarea:
    lineas = texto.splitlines()

    idx = 0
    while idx < len(lineas) and not lineas[idx].strip():
        idx += 1

    if idx >= len(lineas):
        raise TareaInvalida(f"{ruta}: el archivo está vacío")

    linea_titulo = lineas[idx].strip()
    if not linea_titulo.startswith("# "):
        raise TareaInvalida(
            f"{ruta}: el archivo debe comenzar con un título Markdown de nivel 1 (`# Título`)"
        )

    titulo = linea_titulo[2:].strip()
    idx += 1
    while idx < len(lineas) and not lineas[idx].strip():
        idx += 1

    campos: dict[str, str] = {}
    campos_vistos: set[str] = set()
    campos_adicionales: dict[str, str] = {}

    while idx < len(lineas):
        linea = lineas[idx]
        if not linea.strip():
            break
        m = LINEA_META_RE.match(linea)
        if not m:
            break

        clave_cruda = m.group(1).strip()
        valor = m.group(2).strip()
        clave_norm = clave_cruda.upper()

        if clave_norm in campos_vistos:
            raise TareaInvalida(f"{ruta}: campo duplicado en metadatos: «{clave_cruda}»")
        campos_vistos.add(clave_norm)
        campos[clave_norm] = valor

        if clave_norm not in ("ESTADO", "PRIORIDAD", "ETIQUETAS"):
            campos_adicionales[clave_cruda] = valor

        idx += 1

    if "ESTADO" not in campos:
        raise TareaInvalida(f"{ruta}: falta el campo obligatorio «ESTADO» en el bloque de metadatos")
    estado = campos["ESTADO"].upper()
    if estado not in ("ABIERTA", "CERRADA"):
        raise TareaInvalida(
            f"{ruta}: estado inválido «{campos['ESTADO']}», debe ser ABIERTA o CERRADA"
        )

    if "PRIORIDAD" not in campos:
        raise TareaInvalida(
            f"{ruta}: falta el campo obligatorio «PRIORIDAD» en el bloque de metadatos"
        )
    try:
        prioridad = int(campos["PRIORIDAD"])
    except ValueError:
        raise TareaInvalida(
            f"{ruta}: prioridad inválida «{campos['PRIORIDAD']}», debe ser un número entero"
        )

    etiquetas_raw = campos.get("ETIQUETAS", "")
    etiquetas = tuple(e.strip() for e in etiquetas_raw.split(",") if e.strip())

    cuerpo = "\n".join(lineas[idx:]).strip()
    id_tarea = ruta.parent.name

    return Tarea(
        id=id_tarea,
        titulo=titulo,
        estado=estado,
        prioridad=prioridad,
        etiquetas=etiquetas,
        campos_adicionales=campos_adicionales,
        cuerpo=cuerpo,
        ruta=ruta,
    )


def guardar_documento_atomico(ruta: Path, contenido: bytes) -> None:
    """Reemplaza el documento sólo después de preparar bytes y permisos originales.

    Un fallo de stat, escritura, sincronización o chmod se propaga antes de reemplazarlo.
    No serializa escritores concurrentes ni promete persistencia ante pérdida de energía.
    """
    modo = stat.S_IMODE(ruta.stat().st_mode)
    with tempfile.NamedTemporaryFile(dir=ruta.parent, delete=False) as temporal:
        destino_temporal = Path(temporal.name)
        try:
            temporal.write(contenido)
            temporal.flush()
            os.fsync(temporal.fileno())
            temporal.close()
            os.chmod(destino_temporal, modo)
            os.replace(destino_temporal, ruta)
        finally:
            temporal.close()
            destino_temporal.unlink(missing_ok=True)


def actualizar_estado_tarea(ruta_tarea: Path, nuevo_estado: str) -> bool:
    """Actualiza el estado de la tarea de forma atómica.

    Preserva exactamente los bytes del archivo fuera del valor ABIERTA/CERRADA
    (sangría, viñeta, espaciado, campos desconocidos, cuerpo, modo POSIX y CRLF/LF).
    Devuelve True si el estado cambió, False si ya tenía el nuevo estado (idempotente).
    """
    if nuevo_estado not in ("ABIERTA", "CERRADA"):
        raise TareaInvalida(f"estado objetivo inválido: {nuevo_estado}")

    try:
        raw_bytes = ruta_tarea.read_bytes()
    except OSError as e:
        raise TareaInvalida(f"{ruta_tarea}: no se pudo leer el archivo: {e}") from e

    try:
        texto = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise TareaInvalida(f"{ruta_tarea}: codificación UTF-8 inválida en TAREA.md: {e}") from e

    tarea = parsear_tarea(texto, ruta_tarea)
    if tarea.estado == nuevo_estado:
        return False

    # El parser ya probó que el primer campo ESTADO está en el bloque de metadatos.
    # Reutilizar su patrón evita un segundo parser que pueda discrepar sobre espacios o EOL.
    posicion = 0
    for linea in texto.splitlines(keepends=True):
        campo = LINEA_META_RE.match(linea)
        if campo and campo.group(1).upper() == "ESTADO":
            valor = campo.group(2)
            inicio = posicion + campo.start(2) + len(valor) - len(valor.lstrip())
            fin = posicion + campo.start(2) + len(valor.rstrip())
            contenido = (texto[:inicio] + nuevo_estado + texto[fin:]).encode("utf-8")
            guardar_documento_atomico(ruta_tarea, contenido)
            return True
        posicion += len(linea)
    raise TareaInvalida(f"{ruta_tarea}: no se encontró ESTADO después de validar los metadatos")


def crear_carpeta_tarea_atomica(
    raiz_tareas: Path,
    sufijo: str | None,
    fecha_utc: datetime.datetime | None = None,
) -> tuple[str, Path]:
    """Crea la carpeta de una nueva tarea de forma atómica y sin colisiones concurrentes."""
    ahora = fecha_utc or datetime.datetime.now(datetime.timezone.utc)
    base = ahora.strftime("%Y%m%d-%H%M%S")
    slug = _sanear_slug(sufijo) if sufijo else ""
    candidato_base = f"{base}-{slug}" if slug else base

    # Intento 0: carpeta directa
    candidato = candidato_base
    carpeta = raiz_tareas / candidato
    try:
        os.mkdir(carpeta)
        return candidato, carpeta
    except FileExistsError:
        pass

    # Reintentos con sufijo secuencial
    contador = 1
    while contador < 10000:
        candidato = f"{candidato_base}-{contador}"
        carpeta = raiz_tareas / candidato
        try:
            os.mkdir(carpeta)
            return candidato, carpeta
        except FileExistsError:
            contador += 1

    raise TareaError("no se pudo reservar una carpeta de tarea única tras múltiples intentos")


def resolver_id_o_prefijo(raiz_tareas: Path, id_o_prefijo: str) -> Path:
    if raiz_tareas.is_symlink():
        raise RutaInsegura(f"el directorio {raiz_tareas} es un enlace simbólico")

    validar_seguridad_id(id_o_prefijo)

    if not raiz_tareas.is_dir():
        raise TrackerNoEncontrado(f"directorio de tareas inexistente: {raiz_tareas}")

    directo = raiz_tareas / id_o_prefijo
    if directo.is_symlink() or directo.is_dir():
        asegurar_confinamiento(raiz_tareas, directo)
        if not ID_COMPLETO_RE.fullmatch(directo.name):
            raise TareaInvalida(f"nombre de carpeta de tarea inválido: {directo.name}")
        return directo

    candidatos: list[Path] = []
    for entrada in sorted(raiz_tareas.iterdir()):
        if entrada.name.startswith("."):
            continue
        if not ID_COMPLETO_RE.fullmatch(entrada.name):
            continue
        if entrada.name.startswith(id_o_prefijo):
            asegurar_confinamiento(raiz_tareas, entrada)
            candidatos.append(entrada)

    if not candidatos:
        raise TareaNoEncontrada(
            f"no se encontró ninguna tarea con id o prefijo «{id_o_prefijo}»"
        )
    if len(candidatos) > 1:
        nombres = sorted(c.name for c in candidatos)
        raise IdAmbiguo(
            f"el prefijo «{id_o_prefijo}» es ambiguo; coincide con: {', '.join(nombres)}"
        )

    return candidatos[0]


def leer_archivo_etiquetas(raiz_tareas: Path) -> tuple[dict[str, str], list[ProblemaEtiquetas]]:
    """Lee y valida el archivo opcional `tareas/etiquetas`.

    Devuelve una tupla (mapa_descripciones, problemas), donde mapa_descripciones
    asocia la etiqueta en minúsculas con su descripción textual (usando la última definición).
    Si hay enlaces simbólicos, errores de decodificación UTF-8, o redefiniciones,
    se devuelven en la lista estructurada `problemas`.
    """
    archivo = raiz_tareas / "etiquetas"
    if archivo.is_symlink():
        return {}, [
            ProblemaEtiquetas(
                categoria="symlink",
                mensaje="tareas/etiquetas es un enlace simbólico; no se permite",
            )
        ]

    if not archivo.is_file():
        return {}, []

    try:
        st = archivo.stat()
        if st.st_size > 2 * 1024 * 1024:
            return {}, [
                ProblemaEtiquetas(
                    categoria="fatal",
                    mensaje="tareas/etiquetas supera el límite de tamaño permitido (2 MiB)",
                )
            ]
        raw_bytes = archivo.read_bytes()
    except OSError as e:
        return {}, [
            ProblemaEtiquetas(
                categoria="fatal",
                mensaje=f"tareas/etiquetas: error al leer archivo: {e}",
            )
        ]

    try:
        texto = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        return {}, [
            ProblemaEtiquetas(
                categoria="fatal",
                mensaje=f"tareas/etiquetas: codificación UTF-8 inválida: {e}",
            )
        ]

    descripciones: dict[str, str] = {}
    problemas: list[ProblemaEtiquetas] = []
    vistas: set[str] = set()

    for num_linea, linea in enumerate(texto.splitlines(), start=1):
        linea_limpia = linea.strip()
        if not linea_limpia:
            continue

        m = re.match(r"^([^\s,]+)(?:[\s,]+(.*))?$", linea_limpia)
        if not m:
            continue
        etiqueta = m.group(1)
        descripcion = (m.group(2) or "").strip()
        clave = etiqueta.lower()

        if clave in vistas:
            problemas.append(
                ProblemaEtiquetas(
                    categoria="redefinicion",
                    mensaje=f"etiquetas:{num_linea}: etiqueta «{etiqueta}» redefinida",
                )
            )
        else:
            vistas.add(clave)

        descripciones[clave] = descripcion

    return descripciones, problemas


def auditar_tareas(raiz_tareas: Path) -> tuple[list[Tarea], list[str]]:
    """Audita `tareas/` y devuelve tareas válidas y lista de problemas detectados."""
    if raiz_tareas.is_symlink():
        return [], [f"el directorio de tareas es un enlace simbólico: {raiz_tareas}"]

    if not raiz_tareas.is_dir():
        return [], [f"directorio de tareas no existe: {raiz_tareas}"]

    tareas_validas: list[Tarea] = []
    problemas: list[str] = []

    for entrada in sorted(raiz_tareas.iterdir()):
        if entrada.name.startswith("."):
            continue

        if entrada.is_symlink():
            if entrada.name == "etiquetas":
                continue
            try:
                target = entrada.resolve(strict=True)
            except (FileNotFoundError, OSError, RuntimeError):
                problemas.append(f"enlace simbólico roto o inválido: {entrada.name}")
                continue
            try:
                target.relative_to(raiz_tareas.resolve())
            except (ValueError, OSError):
                problemas.append(f"enlace simbólico fuera de tareas/: {entrada.name}")
                continue

        if entrada.is_file():
            if entrada.name in ARCHIVOS_AUXILIARES_PERMITIDOS:
                continue
            problemas.append(f"archivo no reconocido en tareas/: {entrada.name}")
            continue

        if entrada.is_dir():
            if not ID_COMPLETO_RE.fullmatch(entrada.name):
                problemas.append(f"nombre de carpeta inválido: {entrada.name}")
                continue

            tarea_md = entrada / "TAREA.md"
            if not tarea_md.is_file():
                problemas.append(f"carpeta candidata sin TAREA.md: {entrada.name}")
                continue

            if tarea_md.is_symlink():
                try:
                    # is_file ya acreditó un destino existente en este recorrido estable.
                    target_md = tarea_md.resolve()
                    target_md.relative_to(raiz_tareas.resolve())
                except (FileNotFoundError, OSError, RuntimeError, ValueError):
                    problemas.append(
                        f"TAREA.md es un enlace simbólico que apunta fuera de tareas/ o está roto: {entrada.name}"
                    )
                    continue

            try:
                raw_bytes = tarea_md.read_bytes()
            except OSError as e:
                problemas.append(f"{tarea_md}: error al leer archivo: {e}")
                continue

            try:
                texto = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                problemas.append(f"{tarea_md}: codificación UTF-8 inválida en TAREA.md")
                continue

            try:
                tarea = parsear_tarea(texto, tarea_md)
                tareas_validas.append(tarea)
            except TareaInvalida as e:
                problemas.append(str(e))
            except Exception as e:
                problemas.append(f"{tarea_md}: error al leer tarea: {e}")

    return tareas_validas, problemas


def cmd_init(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea init",
        description="Inicializa el tracker de tareas en tareas/",
    )
    parser.add_argument(
        "ruta",
        nargs="?",
        default=None,
        help="Ruta del proyecto (por defecto: directorio actual)",
    )
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parser.add_argument(
        "--sin-readme",
        action="store_true",
        help="Inicializa el tracker sin crear README.md",
    )
    parsed = parser.parse_args(args)

    try:
        raiz = resolver_raiz_tracker(
            argv,
            permitir_crear=True,
            ruta_explicita=parsed.ruta or parsed.proyecto,
        )
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    if raiz_tareas.is_symlink():
        print(
            f"ERROR: el directorio de tareas {raiz_tareas} es un enlace simbólico; no se permite inicializarlo.",
            file=sys.stderr,
        )
        return 1

    try:
        raiz_tareas.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"ERROR: no se pudo crear el directorio {raiz_tareas}: {e}", file=sys.stderr)
        return 1

    if not parsed.sin_readme:
        readme = raiz_tareas / "README.md"
        if readme.is_symlink():
            print(
                f"ERROR: {readme} es un enlace simbólico; no se permite inicializar a través de enlaces.",
                file=sys.stderr,
            )
            return 1

        contenido_readme = (
            "# Tareas de Oracle\n\n"
            "Este directorio almacena tareas y contexto de trabajo en carpetas y Markdown.\n"
            "Cada subdirectorio representa una tarea con su archivo `TAREA.md` y adjuntos.\n"
        )
        # O_CREAT | O_EXCL rechaza cualquier entrada preexistente, también enlaces rotos.
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        modo = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
        try:
            fd = os.open(readme, flags, modo)
            with open(fd, "w", encoding="utf-8") as f:
                f.write(contenido_readme)
        except FileExistsError:
            pass
        except OSError as e:
            print(f"ERROR: no se pudo crear {readme}: {e}", file=sys.stderr)
            return 1

    print(f"Tracker de tareas inicializado en {raiz_tareas}")
    return 0


def cmd_nueva(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea nueva",
        description="Crea una nueva tarea con plantilla lista",
    )
    parser.add_argument("titulo", help="Título de la tarea")
    parser.add_argument(
        "--etiqueta",
        "-e",
        action="append",
        default=[],
        help="Etiqueta para la tarea (repetible o separada por comas)",
    )
    parser.add_argument(
        "--prioridad",
        type=int,
        default=50,
        help="Prioridad numérica entera (defecto: 50)",
    )
    parser.add_argument("--sufijo", default=None,
                        help="Sufijo del ID; sin él se deriva del título, hasta 16 caracteres")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    titulo = parsed.titulo.strip()
    if not titulo:
        print("ERROR: el título de la tarea no puede estar vacío", file=sys.stderr)
        return 1
    if parsed.titulo.splitlines() != [parsed.titulo]:
        print("ERROR: el título no puede contener saltos de línea", file=sys.stderr)
        return 1

    etiquetas: list[str] = []
    for item in parsed.etiqueta:
        if item and item.splitlines() != [item]:
            print("ERROR: las etiquetas no pueden contener saltos de línea", file=sys.stderr)
            return 1
        for e in item.split(","):
            if e.strip():
                etiquetas.append(e.strip())

    try:
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    if raiz_tareas.is_symlink():
        print(
            f"ERROR: el directorio de tareas {raiz_tareas} es un enlace simbólico; escrituras no permitidas.",
            file=sys.stderr,
        )
        return 1

    sufijo = parsed.sufijo if parsed.sufijo is not None else _sufijo_del_titulo(titulo)

    try:
        id_tarea, carpeta = crear_carpeta_tarea_atomica(raiz_tareas, sufijo)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    tarea_md = carpeta / "TAREA.md"
    etiquetas_str = ", ".join(etiquetas)
    contenido = (
        f"# {titulo}\n\n"
        f"- ESTADO: ABIERTA\n"
        f"- PRIORIDAD: {parsed.prioridad}\n"
        f"- ETIQUETAS: {etiquetas_str}\n\n"
    )
    try:
        tarea_md.write_text(contenido, encoding="utf-8")
    except OSError as e:
        print(f"ERROR: no se pudo escribir {tarea_md}: {e}", file=sys.stderr)
        return 1

    if parsed.json:
        print(json.dumps({"id": id_tarea, "ruta": str(tarea_md.resolve())}))
    else:
        print(f"Tarea creada: {id_tarea}")
        print(f"Ruta: {tarea_md.resolve()}")

    return 0


def cmd_listar(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea listar",
        description="Lista tareas del proyecto (alias: ls)",
    )
    parser.add_argument("consulta", nargs="*", default=[], help="Consulta TQL opcional")
    parser.add_argument("--cerradas", action="store_true", help="Muestra sólo tareas cerradas")
    parser.add_argument("--todas", action="store_true", help="Muestra abiertas y cerradas")
    parser.add_argument("--etiqueta", "-e", default=None, help="Filtra por etiqueta exacta")
    parser.add_argument(
        "--texto", "-t", default=None, help="Busca texto en título o descripción"
    )
    parser.add_argument(
        "--por-id",
        action="store_true",
        help="Ordena por ID descendente (más nuevas primero)",
    )
    parser.add_argument("--invertir", action="store_true", help="Invierte el orden de la lista")
    parser.add_argument(
        "--explicar",
        action="store_true",
        help="Muestra tokens y forma compilada sin listar ni requerir tracker",
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    texto_consulta = " ".join(parsed.consulta)
    try:
        consulta_tql = compilar(texto_consulta)
    except ConsultaInvalida as e:
        print(e, file=sys.stderr)
        return 2

    if parsed.explicar:
        print(consulta_tql.explicar())
        return 0

    if parsed.cerradas and parsed.todas:
        print(
            "ERROR: las opciones --cerradas y --todas son incompatibles",
            file=sys.stderr,
        )
        return 1

    try:
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    try:
        tareas_validas, problemas = auditar_tareas(raiz_tareas)
    except OSError as e:
        print(f"ERROR: no se pudo recorrer {raiz_tareas}: {e}", file=sys.stderr)
        return 1

    if problemas:
        print(
            f"ERROR: se detectaron {len(problemas)} registro(s) inválido(s) en {raiz_tareas}:",
            file=sys.stderr,
        )
        for p in problemas:
            print(f"  · {p}", file=sys.stderr)
        return 1

    estado_filtro = "CERRADA" if parsed.cerradas else None
    filtradas = filtrar_tareas(
        tareas_validas,
        estado=estado_filtro,
        etiqueta=parsed.etiqueta,
        texto=parsed.texto,
        consulta_tql=consulta_tql,
        por_id=parsed.por_id,
        invertir=parsed.invertir,
        todas=parsed.todas,
    )

    if parsed.json:
        datos = [t.a_dict() for t in filtradas]
        print(json.dumps(datos))
        return 0

    if not filtradas:
        print("No hay tareas que coincidan con la búsqueda.")
        return 0

    filas_datos: list[tuple[str, str, str, str, str]] = []
    for t in filtradas:
        etiq_str = f"[{', '.join(t.etiquetas)}]" if t.etiquetas else ""
        prio_str = f"P{t.prioridad}"
        filas_datos.append((t.id, t.estado, prio_str, etiq_str, t.titulo))

    anchos = [max(len(c) for c in columna) for columna in zip(*filas_datos)]
    for fila in filas_datos:
        # La columna de etiquetas desaparece si ninguna fila tiene; el título va sin relleno.
        celdas = [celda.ljust(ancho) for celda, ancho in zip(fila[:4], anchos) if ancho]
        print(" ".join(celdas + [fila[4]]).rstrip())

    return 0


def filtrar_tareas(
    tareas: list[Tarea],
    *,
    estado: str | None = None,
    etiqueta: str | None = None,
    texto: str | None = None,
    consulta_tql: Any = None,
    por_id: bool = False,
    invertir: bool = False,
    todas: bool = False,
) -> list[Tarea]:
    """Aplica filtros de estado, etiqueta, texto y TQL sobre una lista de tareas."""
    filtradas: list[Tarea] = []
    for t in tareas:
        if not todas:
            if estado is not None and t.estado != estado:
                continue
            if estado is None and t.estado != "ABIERTA":
                continue
        if etiqueta:
            etiq_buscada = etiqueta.strip().lower()
            if not any(e.lower() == etiq_buscada for e in t.etiquetas):
                continue
        if texto:
            txt_buscado = texto.strip().lower()
            if txt_buscado not in t.titulo.lower() and txt_buscado not in t.cuerpo.lower():
                continue
        if consulta_tql is not None and not consulta_tql.evaluar(t):
            continue
        filtradas.append(t)

    if por_id:
        filtradas.sort(key=lambda x: x.id, reverse=True)
    else:
        filtradas.sort(key=lambda x: (-x.prioridad, x.id))

    if invertir:
        filtradas.reverse()

    return filtradas


def leer_tarea(raiz_tareas: Path, id_o_prefijo: str) -> Tarea:
    """Resuelve y carga una tarea individual por ID o prefijo único."""
    carpeta = resolver_id_o_prefijo(raiz_tareas, id_o_prefijo)
    tarea_md = carpeta / "TAREA.md"
    if not tarea_md.is_file():
        raise TareaNoEncontrada(f"{carpeta.name} no contiene TAREA.md")

    asegurar_confinamiento_archivo(raiz_tareas, tarea_md)

    try:
        raw_bytes = tarea_md.read_bytes()
    except OSError as e:
        raise TareaError(f"no se pudo leer {tarea_md}: {e}") from e

    try:
        texto = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        raise TareaInvalida(
            f"{tarea_md}: codificación UTF-8 inválida en TAREA.md: {e}"
        ) from e

    return parsear_tarea(texto, tarea_md)


def cmd_ver(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea ver",
        description="Muestra detalles de una tarea o su ruta",
    )
    parser.add_argument("id", help="Identificador o prefijo inequívoco de la tarea")
    parser.add_argument("--ruta", action="store_true", help="Imprime sólo la ruta a TAREA.md")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    if parsed.ruta and parsed.json:
        print("ERROR: las opciones --ruta y --json son incompatibles", file=sys.stderr)
        return 1

    try:
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    try:
        tarea = leer_tarea(raiz_tareas, parsed.id)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if parsed.ruta:
        print(str(tarea.ruta.resolve()))
        return 0

    if parsed.json:
        print(json.dumps(tarea.a_dict()))
        return 0

    print(f"ID:        {tarea.id}")
    print(f"Título:    {tarea.titulo}")
    print(f"Estado:    {tarea.estado}")
    print(f"Prioridad: {tarea.prioridad}")
    print(f"Etiquetas: {', '.join(tarea.etiquetas) if tarea.etiquetas else '(ninguna)'}")
    print(f"Ruta:      {tarea.ruta.resolve()}")
    for k, v in tarea.campos_adicionales.items():
        print(f"{k}: {v}")
    print()
    if tarea.cuerpo:
        print(tarea.cuerpo)
    else:
        print("(sin descripción adicional)")

    return 0


def cmd_cerrar(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea cerrar",
        description="Marca una tarea como CERRADA de forma atómica",
    )
    parser.add_argument("id", help="Identificador o prefijo inequívoco de la tarea")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    try:
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    try:
        carpeta = resolver_id_o_prefijo(raiz_tareas, parsed.id)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    tarea_md = carpeta / "TAREA.md"
    if not tarea_md.is_file():
        print(f"ERROR: {carpeta.name} no contiene TAREA.md", file=sys.stderr)
        return 1

    try:
        asegurar_confinamiento_archivo(raiz_tareas, tarea_md)
    except RutaInsegura as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    try:
        cambio = actualizar_estado_tarea(tarea_md, "CERRADA")
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if cambio:
        print(f"Tarea cerrada: {carpeta.name}")
    else:
        print(f"Tarea ya estaba cerrada: {carpeta.name}")
    return 0


def cmd_reabrir(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea reabrir",
        description="Marca una tarea como ABIERTA de forma atómica",
    )
    parser.add_argument("id", help="Identificador o prefijo inequívoco de la tarea")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    try:
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    try:
        carpeta = resolver_id_o_prefijo(raiz_tareas, parsed.id)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    tarea_md = carpeta / "TAREA.md"
    if not tarea_md.is_file():
        print(f"ERROR: {carpeta.name} no contiene TAREA.md", file=sys.stderr)
        return 1

    try:
        asegurar_confinamiento_archivo(raiz_tareas, tarea_md)
    except RutaInsegura as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    try:
        cambio = actualizar_estado_tarea(tarea_md, "ABIERTA")
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if cambio:
        print(f"Tarea reabierta: {carpeta.name}")
    else:
        print(f"Tarea ya estaba abierta: {carpeta.name}")
    return 0


def cmd_revisar(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea revisar",
        description="Audita la integridad del directorio tareas/",
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    try:
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    try:
        tareas_validas, problemas = auditar_tareas(raiz_tareas)
    except OSError as e:
        print(f"ERROR: no se pudo recorrer {raiz_tareas}: {e}", file=sys.stderr)
        return 1

    _, problemas_etiq = leer_archivo_etiquetas(raiz_tareas)
    for pe in problemas_etiq:
        problemas.append(pe.mensaje)

    if parsed.json:
        resultado = {
            "ok": len(problemas) == 0,
            "tareas_validas": len(tareas_validas),
            "problemas": problemas,
        }
        print(json.dumps(resultado))
        return 0 if not problemas else 1

    if problemas:
        print(
            f"REVISIÓN FALLIDA — {len(problemas)} problema(s) en {raiz_tareas}:",
            file=sys.stderr,
        )
        for p in problemas:
            print(f"  · {p}", file=sys.stderr)
        return 1

    print(f"REVISIÓN OK: {len(tareas_validas)} tarea(s) válida(s) en {raiz_tareas}")
    return 0


def _aplicar_etiquetas_texto(
    texto: str,
    etiquetas_operacion: list[str],
    *,
    modo: str,
    id_tarea: str,
    ruta_tarea: Path,
) -> tuple[bool, str, dict[str, Any]]:
    """Calcula la modificación de etiquetas en el texto de un TAREA.md.

    Devuelve (modificado, nuevo_texto, info_cambio).
    """
    lineas_raw = texto.splitlines(keepends=True)
    eol_doc = "\r\n" if "\r\n" in texto else "\n"

    idx = 0
    while idx < len(lineas_raw) and not lineas_raw[idx].strip():
        idx += 1

    if idx >= len(lineas_raw) or not lineas_raw[idx].strip().startswith("# "):
        raise TareaInvalida(f"{ruta_tarea}: encabezado inválido (# Título requerido)")

    idx += 1
    while idx < len(lineas_raw) and not lineas_raw[idx].strip():
        idx += 1

    meta_inicio = idx
    meta_fin = idx
    linea_etiquetas_idx: int | None = None
    match_etiquetas: re.Match[str] | None = None

    while meta_fin < len(lineas_raw):
        m = LINEA_META_RE.match(lineas_raw[meta_fin])
        if not m:
            break
        if m.group(1).upper() == "ETIQUETAS":
            linea_etiquetas_idx = meta_fin
            match_etiquetas = m
        meta_fin += 1

    if match_etiquetas is not None:
        num_linea = linea_etiquetas_idx + 1
        valor_raw = match_etiquetas.group(2)
        etiquetas_actuales = [e.strip() for e in valor_raw.split(",") if e.strip()]
        linea_orig = lineas_raw[linea_etiquetas_idx]
        eol_linea = "\r\n" if linea_orig.endswith("\r\n") else ("\n" if linea_orig.endswith("\n") else "")
        prefijo = linea_orig[: match_etiquetas.start(2)]
    else:
        num_linea = meta_fin + 1
        etiquetas_actuales = []
        eol_linea = eol_doc
        prefijo = "- ETIQUETAS: "

    if modo == "agregar":
        nuevas_etiquetas = list(etiquetas_actuales)
        vistas_lower = {e.lower() for e in etiquetas_actuales}
        for item in etiquetas_operacion:
            if item.lower() not in vistas_lower:
                nuevas_etiquetas.append(item)
                vistas_lower.add(item.lower())
    elif modo == "quitar":
        quitar_lower = {e.lower() for e in etiquetas_operacion}
        nuevas_etiquetas = [e for e in etiquetas_actuales if e.lower() not in quitar_lower]
    else:
        raise ValueError(f"modo desconocido: {modo}")

    # Sin cambios no se reescribe; quitar sobre una tarea sin línea de etiquetas cae acá.
    if nuevas_etiquetas == etiquetas_actuales:
        return False, texto, {}

    nueva_linea = f"{prefijo}{', '.join(nuevas_etiquetas)}{eol_linea}"
    if linea_etiquetas_idx is not None:
        lineas_raw[linea_etiquetas_idx] = nueva_linea
    else:
        # meta_fin >= 1: el título existe. Una última línea sin EOL recibe el del documento.
        if not lineas_raw[meta_fin - 1].endswith(("\r\n", "\n")):
            lineas_raw[meta_fin - 1] += eol_doc
        lineas_raw.insert(meta_fin, nueva_linea)

    nuevo_texto = "".join(lineas_raw)
    antes_str = ", ".join(etiquetas_actuales)
    despues_str = ", ".join(nuevas_etiquetas)

    info = {
        "id": id_tarea,
        "ruta": str(ruta_tarea.resolve()),
        "linea": num_linea,
        "antes": antes_str,
        "despues": despues_str,
        "etiquetas_antes": list(etiquetas_actuales),
        "etiquetas_despues": list(nuevas_etiquetas),
    }
    return True, nuevo_texto, info


def _sanear_etiquetas_operacion(etiquetas_arg: list[str]) -> list[str]:
    resultado: list[str] = []
    for item in etiquetas_arg:
        if item and item.splitlines() != [item]:
            raise TareaError("las etiquetas no pueden contener saltos de línea")
        resultado.extend(e.strip() for e in item.split(",") if e.strip())
    if not resultado:
        raise TareaError("debe especificar al menos una etiqueta no vacía con --etiqueta")
    return resultado


def _aplicar_y_guardar_etiquetas(
    raiz_tareas: Path,
    carpetas: list[Path],
    etiquetas_op: list[str],
    *,
    modo: str,
    salida_json: bool,
) -> int:
    cambios: list[dict[str, Any]] = []
    escrituras: list[tuple[Path, bytes, dict[str, Any]]] = []

    for carpeta in carpetas:
        tarea_md = carpeta / "TAREA.md"
        try:
            asegurar_confinamiento_archivo(raiz_tareas, tarea_md)
            raw_bytes = tarea_md.read_bytes()
            texto = raw_bytes.decode("utf-8")
        except (TareaError, OSError, UnicodeDecodeError) as e:
            print(f"ERROR: no se pudo leer {tarea_md}: {e}", file=sys.stderr)
            return 1

        modificado, nuevo_texto, info = _aplicar_etiquetas_texto(
            texto,
            etiquetas_op,
            modo=modo,
            id_tarea=carpeta.name,
            ruta_tarea=tarea_md,
        )
        if modificado:
            nuevo_bytes = nuevo_texto.encode("utf-8")
            escrituras.append((tarea_md, nuevo_bytes, info))
            cambios.append(info)

    escritas: list[str] = []
    for ruta_md, contenido_bytes, _ in escrituras:
        try:
            guardar_documento_atomico(ruta_md, contenido_bytes)
            escritas.append(ruta_md.parent.name)
        except OSError as e:
            if escritas:
                ids_str = ", ".join(escritas)
                print(
                    f"ERROR: fallo al escribir {ruta_md}: {e}. "
                    f"Tareas escritas previamente: {ids_str}",
                    file=sys.stderr,
                )
            else:
                print(f"ERROR: fallo al escribir {ruta_md}: {e}", file=sys.stderr)
            return 1

    if salida_json:
        print(json.dumps(cambios))
        return 0

    for info in cambios:
        print(
            f"tareas/{info['id']}/TAREA.md:{info['linea']}: etiquetas: "
            f"{info['antes']} → {info['despues']}"
        )

    print(f"{len(cambios)} tarea(s) modificada(s)")
    return 0


def cmd_etiquetar(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea etiquetar",
        description="Agrega una o más etiquetas a tareas existentes",
    )
    parser.add_argument(
        "ids",
        nargs="*",
        default=[],
        help="Identificadores o prefijos inequívocos de tareas",
    )
    parser.add_argument(
        "--etiqueta",
        "-e",
        action="append",
        default=[],
        help="Etiqueta a agregar (repetible o separada por comas)",
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    if not parsed.ids:
        parser.error("exige al menos un identificador de tarea")
    if not parsed.etiqueta:
        parser.error("debe especificar al menos una etiqueta con --etiqueta")

    try:
        etiquetas_op = _sanear_etiquetas_operacion(parsed.etiqueta)
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    _, problemas = auditar_tareas(raiz_tareas)
    if problemas:
        print(
            f"ERROR: se detectaron {len(problemas)} registro(s) inválido(s) en {raiz_tareas}:",
            file=sys.stderr,
        )
        for p in problemas:
            print(f"  · {p}", file=sys.stderr)
        return 1

    carpetas: list[Path] = []
    for id_arg in parsed.ids:
        try:
            c = resolver_id_o_prefijo(raiz_tareas, id_arg)
            if c not in carpetas:
                carpetas.append(c)
        except TareaError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

    return _aplicar_y_guardar_etiquetas(
        raiz_tareas,
        carpetas,
        etiquetas_op,
        modo="agregar",
        salida_json=parsed.json,
    )


def cmd_desetiquetar(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea desetiquetar",
        description="Quita una o más etiquetas de tareas",
    )
    parser.add_argument(
        "ids",
        nargs="*",
        default=[],
        help="Identificadores o prefijos inequívocos de tareas",
    )
    parser.add_argument(
        "--etiqueta",
        "-e",
        action="append",
        default=[],
        help="Etiqueta a quitar (repetible o separada por comas)",
    )
    parser.add_argument(
        "--consulta",
        default=None,
        help="Expresión de consulta TQL para filtrar tareas (modo masivo)",
    )
    parser.add_argument(
        "--cerradas",
        action="store_true",
        help="Aplica a tareas cerradas (modo masivo)",
    )
    parser.add_argument(
        "--todas",
        action="store_true",
        help="Aplica a tareas abiertas y cerradas (modo masivo)",
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    if parsed.cerradas and parsed.todas:
        parser.error("las opciones --cerradas y --todas son incompatibles")
    if parsed.ids and (parsed.cerradas or parsed.todas):
        parser.error("no se pueden combinar identificadores explícitos con --cerradas o --todas")
    if parsed.ids and parsed.consulta:
        parser.error("no se pueden combinar identificadores explícitos con --consulta")
    if not parsed.etiqueta:
        parser.error("debe especificar al menos una etiqueta con --etiqueta")

    consulta_obj = None
    if parsed.consulta:
        try:
            consulta_obj = compilar(parsed.consulta)
        except ConsultaInvalida as e:
            print(str(e), file=sys.stderr)
            return 2

    try:
        etiquetas_op = _sanear_etiquetas_operacion(parsed.etiqueta)
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    tareas_validas, problemas = auditar_tareas(raiz_tareas)
    if problemas:
        print(
            f"ERROR: se detectaron {len(problemas)} registro(s) inválido(s) en {raiz_tareas}:",
            file=sys.stderr,
        )
        for p in problemas:
            print(f"  · {p}", file=sys.stderr)
        return 1

    carpetas: list[Path] = []
    if parsed.ids:
        for id_arg in parsed.ids:
            try:
                c = resolver_id_o_prefijo(raiz_tareas, id_arg)
                if c not in carpetas:
                    carpetas.append(c)
            except TareaError as e:
                print(f"ERROR: {e}", file=sys.stderr)
                return 1
    else:
        for t in tareas_validas:
            if not parsed.todas:
                if parsed.cerradas and t.estado != "CERRADA":
                    continue
                if not parsed.cerradas and t.estado != "ABIERTA":
                    continue
            if consulta_obj is not None and not consulta_obj.evaluar(t):
                continue
            carpetas.append(t.ruta.parent)

    return _aplicar_y_guardar_etiquetas(
        raiz_tareas,
        carpetas,
        etiquetas_op,
        modo="quitar",
        salida_json=parsed.json,
    )


def ayuda() -> None:
    print("""Oracle — metalenguaje de medidas: tracker de tareas.

Uso:
  oracle tarea init [ruta] [opciones]     Inicializa el tracker de tareas en tareas/
  oracle tarea nueva <titulo> [opciones]  Crea una nueva tarea con plantilla lista
  oracle tarea listar [consulta] [opc]    Lista tareas (alias: ls)
  oracle tarea ver <id> [--ruta] [--json] Muestra detalles de una tarea o su ruta
  oracle tarea cerrar <id>                Marca la tarea como CERRADA de forma atómica
  oracle tarea reabrir <id>               Marca la tarea como ABIERTA de forma atómica
  oracle tarea revisar [--json]           Audita la integridad del directorio tareas/
  oracle tarea anotar <id> [texto] [opc]  Agrega una nota, URL o marca temporal a una tarea
  oracle tarea adjuntar <id> <archivo>    Copia un adjunto al directorio de la tarea
  oracle tarea buscar <texto> [--json]    Busca texto en tareas y notas del tracker
  oracle tarea referencias [id] [--json]  Busca menciones del ID en tareas y código
  oracle tarea resumen [--json]           Muestra cantidades por estado y etiquetas
  oracle tarea seguimiento [opciones]     Diagnóstico de seguimiento y cobertura en Git
  oracle tarea hechos [opciones]          Emite hechos relacionales del tracker en JSON
  oracle tarea etiquetar <id>... [opc]    Agrega una o más etiquetas a tareas
  oracle tarea desetiquetar [id]... [opc] Quita una o más etiquetas de tareas
  oracle tarea grafo [--json]             Emite el grafo de referencias en DOT o JSON

Opciones de «init»:
  --sin-readme                           Inicializa el tracker sin crear README.md

Opciones de «nueva»:
  --etiqueta, -e <etiqueta>              Agrega una o más etiquetas (separadas por coma o repetidas)
  --prioridad <n>                        Prioridad numérica entera (por defecto: 50)
  --sufijo <slug>                        Sufijo del ID (sin él se deriva del título, ≤16)
  --json                                 Emite el ID y ruta en JSON

Opciones de «listar» / «ls»:
  --cerradas                             Muestra sólo tareas cerradas
  --todas                                Muestra abiertas y cerradas
  --etiqueta, -e <etiqueta>              Filtra por etiqueta exacta
  --texto, -t <palabra>                  Busca texto en título o descripción
  --por-id                               Ordena por ID descendente
  --invertir                             Invierte el orden del listado final
  --explicar                             Muestra la consulta TQL compilada y sale
  --json                                 Emite la lista de tareas en JSON

Opciones de «anotar»:
  --url <url>                            URL absoluta (http/https) de referencia
  --marca <posicion>                     Marca temporal o posición en el recurso (exige --url)
  --json                                 Emite la nota registrada en JSON

Opciones de «adjuntar»:
  --permitir-grande                      Permite copiar archivos mayores a 20 MiB
  --json                                 Emite la ruta del adjunto y documento en JSON

Opciones de «hechos»:
  --git                                  Comprueba estado frente al índice y HEAD de Git
  --json                                 Emite el resultado en JSON (siempre activo)

Opciones de «etiquetar»:
  --etiqueta, -e <etiqueta>              Etiqueta a agregar (repetible o separada por comas)
  --json                                 Emite la lista de cambios en JSON

Opciones de «desetiquetar»:
  --etiqueta, -e <etiqueta>              Etiqueta a quitar (repetible o separada por comas)
  --consulta <tql>                       Filtra tareas por consulta TQL en modo masivo
  --cerradas                             Aplica a tareas cerradas (modo masivo)
  --todas                                Aplica a abiertas y cerradas (modo masivo)
  --json                                 Emite la lista de cambios en JSON

Opciones de «grafo»:
  --json                                 Emite nodos y aristas en formato JSON

Opciones comunes:
  --proyecto <ruta>                      Apunta a la raíz de un proyecto explícito
  -h, --help                             Muestra esta ayuda
""")


def despachar(verbo: str, args: list[str], argv: list[str]) -> int:
    """Punto de entrada para el sustantivo `tarea` desde `tools/cli.py`."""
    if not verbo or verbo in ("-h", "--help", "help"):
        ayuda()
        return 0

    if verbo == "init":
        return cmd_init(argv, args)
    if verbo == "nueva":
        return cmd_nueva(argv, args)
    if verbo in ("listar", "ls"):
        return cmd_listar(argv, args)
    if verbo == "ver":
        return cmd_ver(argv, args)
    if verbo == "cerrar":
        return cmd_cerrar(argv, args)
    if verbo == "reabrir":
        return cmd_reabrir(argv, args)
    if verbo == "revisar":
        return cmd_revisar(argv, args)
    if verbo == "etiquetar":
        return cmd_etiquetar(argv, args)
    if verbo == "desetiquetar":
        return cmd_desetiquetar(argv, args)
    if verbo == "grafo":
        from tools import tareas_grafo
        return tareas_grafo.cmd_grafo(argv, args)
    if verbo in ("anotar", "adjuntar", "buscar", "referencias", "resumen"):
        from tools import tareas_contexto
        comandos = {
            "anotar": tareas_contexto.cmd_anotar,
            "adjuntar": tareas_contexto.cmd_adjuntar,
            "buscar": tareas_contexto.cmd_buscar,
            "referencias": tareas_contexto.cmd_referencias,
            "resumen": tareas_contexto.cmd_resumen,
        }
        try:
            return comandos[verbo](argv, args)
        except (TareaError, OSError) as e:
            # Incluye fallos al enumerar carpetas, anteriores a la lectura de cada archivo.
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
    if verbo == "seguimiento":
        from tools import tareas_git
        return tareas_git.cmd_seguimiento(argv, args)
    if verbo == "hechos":
        from tools import tareas_hechos
        return tareas_hechos.cmd_hechos(argv, args)

    print(f"verbo desconocido para «tarea»: {verbo}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    argv_lista = list(sys.argv[1:] if argv is None else argv)
    if not argv_lista or argv_lista[0] in ("-h", "--help", "help"):
        ayuda()
        return 0

    verbo = argv_lista[0]
    args = argv_lista[1:]
    return despachar(verbo, args, argv_lista)


_entrada_directa = {"__main__": main}.get(__name__)
if _entrada_directa:
    sys.exit(_entrada_directa())
