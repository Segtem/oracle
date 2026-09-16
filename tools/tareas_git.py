"""Diagnóstico local de archivos del tracker frente al índice y HEAD de Git."""

from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys

from tools import tareas


def _git(raiz: Path, *argumentos: str) -> subprocess.CompletedProcess:
    # Una selección de repositorio heredada no debe sustituir el proyecto pedido.
    entorno = {k: v for k, v in os.environ.items()
               if not k.startswith("GIT_")}
    entorno.update(LC_ALL="C", GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    try:
        return subprocess.run(
            ["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
             "-c", "core.untrackedCache=false", "-C", str(raiz), *argumentos],
            env=entorno, capture_output=True, timeout=30,
        )
    except FileNotFoundError as e:
        raise tareas.TareaError("Git no está disponible para comprobar el seguimiento") from e
    except subprocess.TimeoutExpired as e:
        raise tareas.TareaError("Git excedió 30 segundos; seguimiento no comprobado") from e


def _salida_git(raiz: Path, *argumentos: str) -> bytes:
    resultado = _git(raiz, *argumentos)
    if resultado.returncode:
        raise tareas.TareaError(
            "no se pudo consultar Git: " + os.fsdecode(resultado.stderr).strip())
    return resultado.stdout


def _rutas_nul(salida: bytes) -> set[str]:
    return {os.fsdecode(ruta) for ruta in salida.split(b"\0") if ruta}


def _archivos_locales(raiz: Path) -> tuple[set[str], list[dict]]:
    archivos: set[str] = set()
    omitidos = []

    def error(exc):
        raise exc

    for directorio, carpetas, nombres in os.walk(raiz / "tareas", onerror=error):
        base = Path(directorio)
        for nombre in list(carpetas):
            ruta = base / nombre
            if nombre in (".git", ".hg", ".svn"):
                carpetas.remove(nombre)
                omitidos.append({"ruta": ruta.relative_to(raiz).as_posix(),
                                 "motivo": "metadatos de control de versiones"})
                continue
            # Un subrepositorio tiene su propia historia; no atribuirla al padre.
            if ruta.is_symlink() or (ruta / ".git").exists():
                carpetas.remove(nombre)
                relativo = ruta.relative_to(raiz).as_posix()
                archivos.add(relativo)
                omitidos.append({"ruta": relativo, "motivo": "directorio no recorrido"})
        for nombre in nombres:
            archivos.add((base / nombre).relative_to(raiz).as_posix())
    return archivos, sorted(omitidos, key=lambda x: x["ruta"])


SEPARADOR_COMMIT = "\x1f"


def commits(raiz: Path) -> list[dict] | None:
    """El sha y el asunto de cada commit alcanzable desde HEAD, o `None` sin repositorio.

    `None` y no una lista vacía: «no hay con qué mirar» es distinto de «no hay commits», y de la
    diferencia depende que una política no se ponga verde por ausencia de evidencia. Es la misma
    distinción que hace `seguimiento` con `repositorio: None`.

    Sólo el asunto: el cuerpo del mensaje puede traer cualquier cosa —incluso saltos de línea— y lo
    que la convención del tracker fija es la primera línea, `<ID>: resumen`.
    """
    resultado = _git(raiz, "rev-parse", "--show-toplevel")
    if resultado.returncode:
        if b"not a git repository" in resultado.stderr:
            return None
        raise tareas.TareaError("Git no pudo localizar el repositorio: "
                                + os.fsdecode(resultado.stderr).strip())
    salida = _git(raiz, "log", "--no-color", f"--format=%H{SEPARADOR_COMMIT}%s")
    if salida.returncode:
        # Un repositorio recién creado, sin un solo commit, no es un error: no tiene historia.
        if b"does not have any commits yet" in salida.stderr:
            return []
        raise tareas.TareaError(
            "no se pudo leer la historia: " + os.fsdecode(salida.stderr).strip())
    filas = []
    for linea in os.fsdecode(salida.stdout).splitlines():
        sha, _, asunto = linea.partition(SEPARADOR_COMMIT)
        if sha:
            filas.append({"sha": sha, "asunto": asunto})
    return filas


def seguimiento(raiz: Path) -> dict:
    """Observa sin hacer git add, commit, fetch ni modificar el índice."""
    tracker = raiz / "tareas"
    if tracker.is_symlink() or not tracker.is_dir():
        raise tareas.RutaInsegura("tareas/ debe ser un directorio local, no un enlace")
    locales, omitidos = _archivos_locales(raiz)
    resultado = _git(raiz, "rev-parse", "--show-toplevel")
    if resultado.returncode:
        if b"not a git repository" in resultado.stderr:
            return {"repositorio": None, "head": None, "archivos": [],
                    "sin_repositorio": sorted(locales), "omitidos": omitidos,
                    "diagnostico": "El proyecto no pertenece a un repositorio Git."}
        raise tareas.TareaError("Git no pudo localizar el repositorio: "
                                + os.fsdecode(resultado.stderr).strip())
    repo = Path(os.fsdecode(resultado.stdout.removesuffix(b"\n"))).resolve()
    try:
        relativo_proyecto = raiz.relative_to(repo).as_posix()
    except ValueError as e:
        raise tareas.TareaError(
            "la raíz del proyecto no pertenece al árbol de trabajo informado por Git") from e
    prefijo = "" if relativo_proyecto == "." else relativo_proyecto + "/"
    especificacion = ":(literal)" + prefijo + "tareas"

    def del_proyecto(rutas):
        # El pathspec acota la consulta; comprobar también las rutas recibidas.
        salida = set()
        for ruta in rutas:
            if not ruta.startswith(prefijo + "tareas/"):
                continue
            relativo = ruta[len(prefijo):]
            if ".." not in PurePosixPath(relativo).parts:
                salida.add(relativo)
        return salida

    indice = del_proyecto(_rutas_nul(_salida_git(
        repo, "ls-files", "--cached", "-z", "--", especificacion)))
    ignorados = del_proyecto(_rutas_nul(_salida_git(
        repo, "ls-files", "--others", "--ignored", "--exclude-standard", "-z",
        "--", especificacion)))
    head_resultado = _git(repo, "rev-parse", "--verify", "--quiet", "HEAD")
    if head_resultado.returncode not in (0, 1):
        raise tareas.TareaError("Git no pudo comprobar HEAD")
    head = head_resultado.stdout.decode("ascii").strip() if not head_resultado.returncode else None
    confirmados = del_proyecto(_rutas_nul(_salida_git(
        repo, "ls-tree", "-r", "--name-only", "-z", head, "--", especificacion))) if head else set()
    # -z evita interpretar comillas, saltos o escapes de nombres como estructura del informe.
    campos = _salida_git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all",
                         "--no-renames", "--", especificacion).split(b"\0")
    estados = {}
    for campo in campos:
        if not campo:
            continue
        ruta_repo = os.fsdecode(campo[3:])
        rutas = del_proyecto({ruta_repo})
        if rutas:
            estados.setdefault(rutas.pop(), []).append(campo[:2].decode("ascii"))
    archivos = []
    for ruta in sorted(locales | indice | confirmados):
        codigos = estados.get(ruta, [])
        # Una eliminación del índice puede coexistir con el mismo archivo como untracked.
        xy = next((c for c in codigos if c != "??"), "??" if codigos else "  ")
        ignorado = ruta in ignorados and ruta not in indice
        if ignorado:
            estado = "ignorado"
        elif ruta not in indice and ruta not in confirmados:
            estado = "sin_seguimiento"
        elif xy != "  ":
            estado = "con_cambios"
        else:
            estado = "sin_cambios"
        archivos.append({"ruta": ruta, "estado": estado, "en_indice": ruta in indice,
                         "en_head": ruta in confirmados, "existe": ruta in locales,
                         "ignorado": ignorado, "indice": xy[0], "trabajo": xy[1],
                         "codigos_git": codigos})
    return {"repositorio": str(repo), "head": head, "archivos": archivos,
            "sin_repositorio": [], "omitidos": omitidos}


def cmd_seguimiento(argv: list[str], args: list[str]) -> int:
    parser = tareas.ParserDeSubcomando(
        prog="oracle tarea seguimiento",
        description="Compara archivos del tracker con el índice y HEAD de Git, sin escribir")
    parser.add_argument("--proyecto", help="Raíz explícita del proyecto")
    parser.add_argument("--json", action="store_true", help="Diagnóstico como JSON")
    opciones = parser.parse_args(args)
    try:
        raiz = tareas.resolver_raiz_tracker(argv, ruta_explicita=opciones.proyecto)
        datos = seguimiento(raiz)
    except (tareas.TareaError, OSError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    if opciones.json:
        print(json.dumps(datos))
    elif datos["repositorio"] is None:
        print(datos["diagnostico"])
        for ruta in datos["sin_repositorio"]:
            print(f"  sin repositorio: {ruta}")
    else:
        print(f"Repositorio: {datos['repositorio']} · HEAD: {datos['head'] or 'sin commits'}")
        for archivo in datos["archivos"]:
            print(f"  {archivo['estado']}: {archivo['ruta']} "
                  f"(índice={archivo['en_indice']}, HEAD={archivo['en_head']}, "
                  f"XY={archivo['indice']}{archivo['trabajo']})")
        for omision in datos["omitidos"]:
            print(f"  omitido: {omision['ruta']} ({omision['motivo']})")
    return 0
