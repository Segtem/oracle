"""Captura y consultas de contexto de trabajo para el tracker de tareas de Oracle (P2).

Proporciona operaciones de captura de notas, referencias URL, adjuntos locales,
búsqueda en texto de tareas, rastreo de menciones/referencias y resúmenes estadísticos.
Independiente del catálogo de medidas y sin dependencias externas.
"""
from __future__ import annotations

import argparse
import datetime
import json
import io
import os
import re
import stat
import sys
import urllib.parse
import unicodedata
from pathlib import Path
from typing import Any

from tools.tareas import (
    ID_COMPLETO_RE,
    ParserDeSubcomando,
    RutaInsegura,
    Tarea,
    TareaError,
    TareaInvalida,
    TareaNoEncontrada,
    TrackerNoEncontrado,
    asegurar_confinamiento,
    asegurar_confinamiento_archivo,
    auditar_tareas,
    guardar_documento_atomico,
    leer_archivo_etiquetas,
    parsear_tarea,
    resolver_id_o_prefijo,
    resolver_raiz_tracker,
)

# Límites de seguridad y capacidad
LIMITE_ADJUNTO_BYTES = 20 * 1024 * 1024   # 20 MiB por defecto
LIMITE_BUSQUEDA_BYTES = 2 * 1024 * 1024   # 2 MiB por archivo para búsqueda

# Directorios excluidos al buscar referencias en el proyecto
DIRECTORIOS_IGNORADOS_REFERENCIAS = frozenset({
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "build",
    "dist",
})

# Extensiones de texto admitidas para búsqueda literal
EXTENSIONES_TEXTO_ADMITIDAS = frozenset({
    ".md",
    ".txt",
    ".rst",
    ".oracle",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".csv",
    ".tsv",
    ".log",
    ".ini",
    ".cfg",
    ".conf",
    ".sh",
    ".bash",
    ".py",
    ".js",
    ".ts",
    ".html",
    ".htm",
    ".css",
    ".xml",
    ".sql",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".rs",
    ".go",
    ".java",
})

# Extensiones binarias o multimedia reconocidas que se omiten directamente
EXTENSIONES_BINARIAS_CONOCIDAS = frozenset({
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".webp",
    ".svg",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".rar",
    ".exe",
    ".bin",
    ".so",
    ".dll",
    ".dylib",
    ".pyc",
    ".pyo",
    ".pyd",
    ".class",
    ".mp3",
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".flv",
    ".wav",
    ".ogg",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
})


def validar_url_estricta(url: str) -> None:
    """Valida que la URL sea absoluta http/https y no contenga caracteres de control ni espacios.

    Conserva la cadena exactamente sin normalizar ni alterar parámetros de consulta (ej. ?t=...).
    """
    if not url or not isinstance(url, str):
        raise TareaError("la URL no puede estar vacía")

    if any(c.isspace() or unicodedata.category(c) == "Cc" for c in url):
        raise TareaError(f"la URL contiene espacios o caracteres de control: {url!r}")

    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname
        # Acceder a port valida también puertos no numéricos o fuera de rango.
        parsed.port
    except ValueError as e:
        raise TareaError(f"la URL no pudo interpretarse: {url!r}: {e}") from e

    if parsed.scheme.lower() not in ("http", "https"):
        raise TareaError(f"esquema no soportado en URL (sólo se admite http o https): {url!r}")

    if not host:
        raise TareaError(f"la URL debe ser absoluta y contener dominio o host: {url!r}")


def _escapar_enlace_markdown(nombre_archivo: str) -> tuple[str, str]:
    """Genera la etiqueta visible escapada y el destino URL relativo escapado para Markdown."""
    # Escapar barras invertidas antes que los corchetes para no romper el escape
    etiqueta = nombre_archivo.replace("\\", "\\\\").replace("[", r"\[").replace("]", r"\]")
    destino = urllib.parse.quote(nombre_archivo, safe=".-_~/")
    return etiqueta, destino


def leer_archivo_texto_si_aplica(
    ruta: Path,
) -> tuple[list[str] | None, str | None, bool]:
    """Inspecciona y lee un archivo de texto aplicando límites y extensiones admitidas.

    Retorna una tupla (lineas, motivo_omision, es_error_operacional):
    - (lineas, None, False): Archivo regular de texto válido leído y decodificado como UTF-8.
    - (None, motivo, False): Archivo omitido válidamente (binario, tamaño, symlink, extensión desconocida).
    - (None, mensaje_error, True): Error operacional (permisos, fallo de E/S) que debe fallar con código 1.
    """
    if ruta.is_symlink():
        return None, "enlace simbólico", False

    try:
        st = os.lstat(ruta)
    except OSError as e:
        return None, f"error al acceder a {ruta}: {e}", True

    if not stat.S_ISREG(st.st_mode):
        return None, "archivo especial (FIFO/dispositivo/socket)", False

    if st.st_size > LIMITE_BUSQUEDA_BYTES:
        mb = LIMITE_BUSQUEDA_BYTES // (1024 * 1024)
        return None, f"archivo supera el límite de {mb} MiB", False

    sufijo = ruta.suffix.lower()
    if sufijo in EXTENSIONES_BINARIAS_CONOCIDAS:
        return None, "archivo binario", False

    if sufijo and sufijo not in EXTENSIONES_TEXTO_ADMITIDAS:
        return None, f"extensión no admitida ({sufijo})", False

    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(ruta, flags)
        try:
            with open(fd, "rb") as f:
                raw = f.read(LIMITE_BUSQUEDA_BYTES + 1)
        except Exception:
            try:
                os.close(fd)
            except OSError:
                pass
            raise
    except OSError as e:
        return None, f"error operacional al leer {ruta}: {e}", True

    if len(raw) > LIMITE_BUSQUEDA_BYTES:
        mb = LIMITE_BUSQUEDA_BYTES // (1024 * 1024)
        return None, f"archivo supera el límite de {mb} MiB", False

    if b"\x00" in raw:
        return None, "archivo binario (contiene bytes nulos)", False

    try:
        texto = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, "codificación no UTF-8", False

    return texto.splitlines(), None, False


# ---------------------------------------------------------------------------
# 1. Comandos de captura y notas: `anotar` y `adjuntar`
# ---------------------------------------------------------------------------


def cmd_anotar(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea anotar",
        description="Agrega una nota, URL o marca temporal a una tarea existente",
    )
    parser.add_argument("id", help="Identificador o prefijo inequívoco de la tarea")
    parser.add_argument("texto", nargs="?", default=None, help="Texto explicativo de la nota")
    parser.add_argument("--url", default=None, help="URL absoluta de referencia (http/https)")
    parser.add_argument(
        "--marca",
        default=None,
        help="Posición o marca temporal del recurso (ej. 01:32); exige --url",
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    texto_nota = parsed.texto
    if texto_nota is not None and not texto_nota.strip():
        print("ERROR: el texto de la nota no puede estar vacío", file=sys.stderr)
        return 1

    if not texto_nota and not parsed.url:
        print(
            "ERROR: se requiere al menos un texto o una --url para registrar una nota",
            file=sys.stderr,
        )
        return 1

    if parsed.marca and not parsed.url:
        print(
            "ERROR: la opción --marca requiere especificar una --url asociada",
            file=sys.stderr,
        )
        return 1

    if parsed.url:
        try:
            validar_url_estricta(parsed.url)
        except TareaError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

    try:
        raiz = resolver_raiz_tracker(argv, ruta_explicita=parsed.proyecto)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    raiz_tareas = raiz / "tareas"
    try:
        carpeta = resolver_id_o_prefijo(raiz_tareas, parsed.id)
    except TareaError as e:
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
        raw_bytes = tarea_md.read_bytes()
    except OSError as e:
        print(f"ERROR: no se pudo leer {tarea_md}: {e}", file=sys.stderr)
        return 1

    try:
        texto_actual = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as e:
        print(f"ERROR: codificación UTF-8 inválida en {tarea_md}: {e}", file=sys.stderr)
        return 1

    try:
        parsear_tarea(texto_actual, tarea_md)
    except TareaInvalida as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    crlf = b"\r\n" in raw_bytes
    eol = "\r\n" if crlf else "\n"
    ahora_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Formatear la entrada de la nota preservando exactamente espacios e indentación
    lineas_nota: list[str] = []
    lineas_nota.append(f"### Nota ({ahora_utc})")
    lineas_nota.append("")
    if texto_nota:
        lineas_nota.append(texto_nota)
    if parsed.url:
        if parsed.marca:
            lineas_nota.append(f"- URL: {parsed.url} (marca: {parsed.marca})")
        else:
            lineas_nota.append(f"- URL: {parsed.url}")

    bloque_nota = eol.join(lineas_nota) + eol

    if texto_actual.endswith(eol * 2):
        texto_nuevo = texto_actual + bloque_nota
    elif texto_actual.endswith(eol):
        texto_nuevo = texto_actual + eol + bloque_nota
    else:
        texto_nuevo = texto_actual + (eol * 2) + bloque_nota

    try:
        guardar_documento_atomico(tarea_md, texto_nuevo.encode("utf-8"))
    except (OSError, TareaError) as e:
        print(f"ERROR: no se pudo actualizar {tarea_md}: {e}", file=sys.stderr)
        return 1

    if parsed.json:
        salida_json = {
            "id": carpeta.name,
            "documento": str(tarea_md.resolve()),
            "fecha": ahora_utc,
            "texto": texto_nota,
            "url": parsed.url,
            "marca": parsed.marca,
        }
        print(json.dumps(salida_json))
    else:
        print(f"Nota agregada a la tarea {carpeta.name}")
        print(f"Documento: {tarea_md.resolve()}")

    return 0


def cmd_adjuntar(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea adjuntar",
        description="Copia un adjunto al directorio de la tarea y lo vincula en TAREA.md",
    )
    parser.add_argument("id", help="Identificador o prefijo inequívoco de la tarea")
    parser.add_argument("archivo", help="Ruta al archivo regular de origen")
    parser.add_argument(
        "--permitir-grande",
        action="store_true",
        help="Permite adjuntar archivos mayores a 20 MiB",
    )
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    origen = Path(parsed.archivo).expanduser()
    try:
        st_origen = os.lstat(origen)
    except FileNotFoundError:
        print(f"ERROR: el archivo de origen no existe: {parsed.archivo}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"ERROR: no se pudo consultar el archivo de origen: {e}", file=sys.stderr)
        return 1

    if stat.S_ISLNK(st_origen.st_mode):
        print(
            f"ERROR: el archivo de origen no puede ser un enlace simbólico: {parsed.archivo}",
            file=sys.stderr,
        )
        return 1

    if not stat.S_ISREG(st_origen.st_mode):
        print(
            f"ERROR: el archivo de origen debe ser un archivo regular (no directorio ni dispositivo/FIFO): {parsed.archivo}",
            file=sys.stderr,
        )
        return 1

    tamano_origen = st_origen.st_size
    if tamano_origen > LIMITE_ADJUNTO_BYTES and not parsed.permitir_grande:
        print(
            f"ERROR: el archivo ({tamano_origen} bytes) supera el límite de 20 MiB; usá --permitir-grande para adjuntarlo",
            file=sys.stderr,
        )
        return 1

    nombre_archivo = origen.name
    if any(unicodedata.category(c) in ("Cc", "Zl", "Zp") for c in nombre_archivo):
        print(
            f"ERROR: el nombre de archivo contiene caracteres de control o saltos de línea: {nombre_archivo!r}",
            file=sys.stderr,
        )
        return 1

    if nombre_archivo.upper() == "TAREA.MD":
        print(
            "ERROR: no se puede adjuntar un archivo con el nombre reservado TAREA.md",
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
        carpeta = resolver_id_o_prefijo(raiz_tareas, parsed.id)
    except TareaError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    tarea_md = carpeta / "TAREA.md"
    if not tarea_md.is_file():
        print(f"ERROR: {carpeta.name} no contiene TAREA.md", file=sys.stderr)
        return 1

    try:
        asegurar_confinamiento(raiz_tareas, carpeta)
        asegurar_confinamiento_archivo(raiz_tareas, tarea_md)
    except RutaInsegura as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    destino = carpeta / nombre_archivo

    # Impedir colisión con archivos o enlaces preexistentes (incluidos enlaces rotos)
    if destino.exists() or destino.is_symlink():
        print(
            f"ERROR: el archivo de destino ya existe en la tarea: {destino.name}",
            file=sys.stderr,
        )
        return 1

    # Path.name no contiene separadores; la carpeta ya fue confinada arriba.
    # O_EXCL evita seguir o sobrescribir una entrada creada después de comprobar la colisión.
    # Copiar por bloques con creación exclusiva y límite acumulado
    destino_creado = False
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    modo = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
    try:
        fd_dest = os.open(destino, flags, modo)
        destino_creado = True
        acumulado = 0
        with open(fd_dest, "wb") as f_dst, open(origen, "rb") as f_src:
            while True:
                chunk = f_src.read(io.DEFAULT_BUFFER_SIZE)
                if not chunk:
                    break
                acumulado += len(chunk)
                if not parsed.permitir_grande and acumulado > LIMITE_ADJUNTO_BYTES:
                    raise TareaError(
                        f"el archivo superó el límite de 20 MiB durante la copia ({acumulado} bytes); usá --permitir-grande"
                    )
                f_dst.write(chunk)
            f_dst.flush()
            os.fsync(f_dst.fileno())
    except Exception as e:
        print(f"ERROR: no se pudo copiar el archivo al destino: {e}", file=sys.stderr)
        if destino_creado:
            try:
                destino.unlink(missing_ok=True)
            except OSError as error_limpieza:
                print(
                    f"ERROR: no se pudo revertir la copia {destino}: {error_limpieza}; "
                    "puede quedar un adjunto sin registrar",
                    file=sys.stderr,
                )
        return 1

    # Registrar el enlace en TAREA.md preservando documento y revirtiendo en caso de fallo
    try:
        raw_bytes = tarea_md.read_bytes()
        texto_actual = raw_bytes.decode("utf-8")
        parsear_tarea(texto_actual, tarea_md)

        crlf = b"\r\n" in raw_bytes
        eol = "\r\n" if crlf else "\n"

        etiqueta_vis, destino_url = _escapar_enlace_markdown(nombre_archivo)
        linea_adjunto = f"- Adjunto: [{etiqueta_vis}]({destino_url})"

        if texto_actual.endswith(eol * 2):
            texto_nuevo = texto_actual + linea_adjunto + eol
        elif texto_actual.endswith(eol):
            texto_nuevo = texto_actual + eol + linea_adjunto + eol
        else:
            texto_nuevo = texto_actual + (eol * 2) + linea_adjunto + eol

        guardar_documento_atomico(tarea_md, texto_nuevo.encode("utf-8"))
    except Exception as e:
        # Reversión limpia: eliminar sólo el archivo copiado en destino
        print(f"ERROR: no se pudo registrar el adjunto en {tarea_md}: {e}", file=sys.stderr)
        try:
            destino.unlink(missing_ok=True)
        except OSError as error_limpieza:
            print(
                f"ERROR: no se pudo revertir la copia {destino}: {error_limpieza}; "
                "puede quedar un adjunto sin registrar",
                file=sys.stderr,
            )
        return 1

    if parsed.json:
        salida_json = {
            "id": carpeta.name,
            "ruta": str(destino.resolve()),
            "documento": str(tarea_md.resolve()),
        }
        print(json.dumps(salida_json))
    else:
        print(f"Archivo adjuntado a la tarea {carpeta.name}")
        print(f"Ruta:      {destino.resolve()}")
        print(f"Documento: {tarea_md.resolve()}")

    return 0


# ---------------------------------------------------------------------------
# 2. Comandos de consulta: `buscar`, `referencias` y `resumen`
# ---------------------------------------------------------------------------


def buscar_en_tracker(raiz: Path, texto_buscado: str) -> dict[str, Any]:
    """Busca texto de forma literal e insensible a mayúsculas en tareas y notas del tracker.

    Retorna un diccionario con 'coincidencias' y 'omitidos'.
    """
    raiz_tareas = raiz / "tareas"
    coincidencias: list[dict[str, Any]] = []
    omitidos: list[dict[str, str]] = []
    termino_lower = texto_buscado.lower()

    # Recorrer archivos bajo tareas/ recursivamente (incluyendo subcarpetas de tareas)
    for entrada in sorted(raiz_tareas.iterdir()):
        if entrada.name.startswith("."):
            omitidos.append({"ruta": str(entrada.relative_to(raiz)), "motivo": "entrada oculta"})
            continue
        if entrada.is_symlink():
            omitidos.append({"ruta": str(entrada.relative_to(raiz)), "motivo": "enlace simbólico"})
            continue

        if entrada.is_file():
            try:
                ruta_rel = str(entrada.relative_to(raiz))
            except ValueError:
                ruta_rel = str(entrada)

            lineas, motivo, es_error = leer_archivo_texto_si_aplica(entrada)
            if es_error:
                raise TareaInvalida(motivo or "error al leer archivo de texto")
            if motivo is not None:
                omitidos.append({"ruta": ruta_rel, "motivo": motivo})
                continue

            assert lineas is not None
            for num_linea, linea in enumerate(lineas, start=1):
                if termino_lower in linea.lower():
                    coincidencias.append({
                        "ruta": ruta_rel,
                        "linea": num_linea,
                        "texto": linea,
                    })
            continue

        # La auditoría previa ya validó los nombres de todos los directorios visibles.
        if entrada.is_dir():
            error_walk: list[str] = []

            def on_walk_err(err: OSError):
                error_walk.append(f"error al recorrer {err.filename}: {err}")

            for dirpath_str, dirnames, filenames in os.walk(entrada, onerror=on_walk_err):
                dirpath = Path(dirpath_str)

                nuevos_dirnames = []
                for d in sorted(dirnames):
                    subdir = dirpath / d
                    if subdir.is_symlink():
                        try:
                            rel = str(subdir.relative_to(raiz))
                        except ValueError:
                            rel = str(subdir)
                        omitidos.append({"ruta": rel, "motivo": "enlace simbólico de directorio"})
                        continue
                    if (subdir / ".git").exists():
                        try:
                            rel = str(subdir.relative_to(raiz))
                        except ValueError:
                            rel = str(subdir)
                        omitidos.append({"ruta": rel, "motivo": "repositorio anidado"})
                        continue
                    nuevos_dirnames.append(d)
                dirnames[:] = nuevos_dirnames

                for fname in sorted(filenames):
                    if fname.startswith("."):
                        omitidos.append({"ruta": str((dirpath / fname).relative_to(raiz)),
                                         "motivo": "archivo oculto"})
                        continue
                    arch = dirpath / fname
                    try:
                        ruta_rel = str(arch.relative_to(raiz))
                    except ValueError:
                        ruta_rel = str(arch)

                    lineas, motivo, es_error = leer_archivo_texto_si_aplica(arch)
                    if es_error:
                        raise TareaInvalida(motivo or "error al leer archivo de texto")
                    if motivo is not None:
                        omitidos.append({"ruta": ruta_rel, "motivo": motivo})
                        continue

                    assert lineas is not None
                    for num_linea, linea in enumerate(lineas, start=1):
                        if termino_lower in linea.lower():
                            coincidencias.append({
                                "ruta": ruta_rel,
                                "linea": num_linea,
                                "texto": linea,
                            })

            if error_walk:
                raise TareaError(error_walk[0])

    coincidencias.sort(key=lambda x: (x["ruta"], x["linea"]))
    omitidos.sort(key=lambda x: x["ruta"])
    return {
        "coincidencias": coincidencias,
        "omitidos": omitidos,
    }


def cmd_buscar(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea buscar",
        description="Busca texto de forma literal e insensible a mayúsculas en tareas y notas",
    )
    parser.add_argument("texto", help="Texto literal a buscar")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    texto_buscado = parsed.texto
    if not texto_buscado:
        print("ERROR: el texto a buscar no puede estar vacío", file=sys.stderr)
        return 1

    try:
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

    try:
        resultado = buscar_en_tracker(raiz, texto_buscado)
    except (TareaError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    coincidencias = resultado["coincidencias"]
    omitidos = resultado["omitidos"]

    if parsed.json:
        print(json.dumps(resultado))
        return 0

    if not coincidencias:
        print(f"No se encontraron coincidencias para «{texto_buscado}».")
    else:
        for c in coincidencias:
            print(f"{c['ruta']}:{c['linea']}: {c['texto']}")

    if omitidos:
        print("\nArchivos omitidos:")
        for o in omitidos:
            print(f"  · {o['ruta']}: {o['motivo']}")

    return 0


def cmd_referencias(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea referencias",
        description="Busca menciones textuales del ID canónico en tareas, notas y código del proyecto",
    )
    parser.add_argument("id", nargs="?", default=None, help="Identificador o prefijo inequívoco de la tarea")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--proyecto", default=None, help="Ruta al proyecto")
    parsed = parser.parse_args(args)

    try:
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

    id_objetivo = parsed.id
    if id_objetivo is None:
        try:
            rel = Path.cwd().resolve().relative_to(raiz_tareas.resolve())
        except ValueError:
            rel = None
        if rel is not None and len(rel.parts) >= 1:
            candidato = rel.parts[0]
            if (raiz_tareas / candidato / "TAREA.md").exists() and ID_COMPLETO_RE.fullmatch(candidato):
                id_objetivo = candidato
        if id_objetivo is None:
            print(
                "ERROR: falta el ID de la tarea o debe ejecutarse dentro de la carpeta de una tarea",
                file=sys.stderr,
            )
            return 2

    try:
        carpeta = resolver_id_o_prefijo(raiz_tareas, id_objetivo)
    except TareaError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    id_canonica = carpeta.name
    # Delimitar el ID con límites de palabra/carácter para evitar que 'ID' coincida con 'ID-1' o 'copia-ID'
    patron_id = re.compile(rf"(?<![a-zA-Z0-9_-]){re.escape(id_canonica)}(?![a-zA-Z0-9_-])")

    coincidencias: list[dict[str, Any]] = []
    omitidos: list[dict[str, str]] = []
    error_walk: list[str] = []

    def on_walk_error(err: OSError):
        error_walk.append(f"error al recorrer {err.filename}: {err}")

    # Recorrer todo el árbol del proyecto excluyendo directorios ignorados y enlaces
    for dirpath_str, dirnames, filenames in os.walk(raiz, onerror=on_walk_error):
        dirpath = Path(dirpath_str)

        nuevos_dirnames = []
        for d in sorted(dirnames):
            if d in DIRECTORIOS_IGNORADOS_REFERENCIAS:
                continue
            subdir = dirpath / d
            if subdir.is_symlink():
                try:
                    rel = str(subdir.relative_to(raiz))
                except ValueError:
                    rel = str(subdir)
                omitidos.append({"ruta": rel, "motivo": "enlace simbólico de directorio"})
                continue
            if (subdir / ".git").exists():
                try:
                    rel = str(subdir.relative_to(raiz))
                except ValueError:
                    rel = str(subdir)
                omitidos.append({"ruta": rel, "motivo": "repositorio anidado"})
                continue
            nuevos_dirnames.append(d)
        dirnames[:] = nuevos_dirnames

        for fname in sorted(filenames):
            if fname.startswith("."):
                omitidos.append({"ruta": str((dirpath / fname).relative_to(raiz)),
                                 "motivo": "archivo oculto"})
                continue

            archivo = dirpath / fname
            try:
                ruta_rel = str(archivo.relative_to(raiz))
            except ValueError:
                ruta_rel = str(archivo)

            lineas, motivo, es_error = leer_archivo_texto_si_aplica(archivo)
            if es_error:
                print(f"ERROR: {motivo}", file=sys.stderr)
                return 1
            if motivo is not None:
                omitidos.append({"ruta": ruta_rel, "motivo": motivo})
                continue

            assert lineas is not None
            for num_linea, linea in enumerate(lineas, start=1):
                if patron_id.search(linea):
                    coincidencias.append({
                        "ruta": ruta_rel,
                        "linea": num_linea,
                        "texto": linea,
                    })

    if error_walk:
        for err_msg in error_walk:
            print(f"ERROR: {err_msg}", file=sys.stderr)
        return 1

    coincidencias.sort(key=lambda x: (x["ruta"], x["linea"]))
    omitidos.sort(key=lambda x: x["ruta"])

    if parsed.json:
        resultado = {
            "id": id_canonica,
            "tipo": "mencion_textual",
            "coincidencias": coincidencias,
            "omitidos": omitidos,
        }
        print(json.dumps(resultado))
        return 0

    if not coincidencias:
        print(f"No se encontraron referencias para «{id_canonica}».")
    else:
        print(f"Referencias encontradas para «{id_canonica}»:")
        for c in coincidencias:
            print(f"{c['ruta']}:{c['linea']}: {c['texto']}")

    if omitidos:
        print("\nArchivos omitidos:")
        for o in omitidos:
            print(f"  · {o['ruta']}: {o['motivo']}")

    return 0


def cmd_resumen(argv: list[str], args: list[str]) -> int:
    parser = ParserDeSubcomando(
        prog="oracle tarea resumen",
        description="Muestra cantidades agregadas por estado y etiquetas a partir de registros válidos",
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
    tareas_validas, problemas = auditar_tareas(raiz_tareas)

    if problemas:
        print(
            f"ERROR: se detectaron {len(problemas)} registro(s) inválido(s) en {raiz_tareas}:",
            file=sys.stderr,
        )
        for p in problemas:
            print(f"  · {p}", file=sys.stderr)
        return 1

    descripciones_map, problemas_etiq = leer_archivo_etiquetas(raiz_tareas)
    for p in problemas_etiq:
        if p.categoria == "fatal":
            print(f"ERROR: {p.mensaje}", file=sys.stderr)
            return 1
        # Redefinición o enlace simbólico: `revisar` falla; el resumen avisa y sigue.
        print(f"AVISO: {p.mensaje}", file=sys.stderr)

    total = len(tareas_validas)
    estados: dict[str, int] = {"ABIERTA": 0, "CERRADA": 0}
    etiquetas_map: dict[str, int] = {}

    for t in tareas_validas:
        estados[t.estado] += 1
        # Contar cada tarea una sola vez por etiqueta, conservando mayúsculas/minúsculas originales
        # parsear_tarea ya elimina espacios y etiquetas vacías antes de la auditoría.
        etiquetas_tarea = set(t.etiquetas)
        for etiq in etiquetas_tarea:
            etiquetas_map[etiq] = etiquetas_map.get(etiq, 0) + 1

    etiquetas_ordenadas = {k: etiquetas_map[k] for k in sorted(etiquetas_map.keys())}
    sin_etiquetas = sum(1 for t in tareas_validas if not t.etiquetas)

    if parsed.json:
        resultado = {
            "total": total,
            "estados": estados,
            "etiquetas": etiquetas_ordenadas,
            "descripciones": {
                etiq: descripciones_map.get(etiq.lower())
                for etiq in etiquetas_ordenadas
            },
            "sin_etiquetas": sin_etiquetas,
        }
        print(json.dumps(resultado))
        return 0

    print(f"Resumen del tracker de tareas ({raiz_tareas}):")
    print(f"  Total tareas: {total}")
    print(f"  Abiertas:     {estados['ABIERTA']}")
    print(f"  Cerradas:     {estados['CERRADA']}")
    print(f"  Sin etiquetas: {sin_etiquetas}")
    if etiquetas_ordenadas:
        print("  Etiquetas:")
        for etiq, cantidad in etiquetas_ordenadas.items():
            desc = descripciones_map.get(etiq.lower())
            if desc:
                print(f"    · {etiq}: {cantidad} — {desc}")
            else:
                print(f"    · {etiq}: {cantidad}")
    else:
        print("  Etiquetas:    (ninguna)")

    return 0
