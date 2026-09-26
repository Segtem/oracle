"""Comprobación compartida de la forma de autoría, sin depender de los cargadores."""

import difflib
from pathlib import Path


def leer_texto(ruta: Path) -> str:
    # Path.read_text convierte CRLF a LF y ocultaría una grafía distinta.
    with ruta.open("r", encoding="utf-8", newline="") as archivo:
        return archivo.read()


def sin_comentarios(texto: str) -> str:
    return "".join(linea for linea in texto.splitlines(keepends=True)
                   if not linea.lstrip().startswith("#"))


def diferencia(texto: str, impreso: str, *, max_lineas: int = 8) -> list[str]:
    actual = sin_comentarios(texto)
    lineas = list(difflib.unified_diff(actual.splitlines(), impreso.splitlines(),
                                      fromfile="actual", tofile="impresor", lineterm=""))
    if not lineas and actual != impreso:
        if "\r\n" in actual:
            lineas = ["@@ fines de línea @@", "- CRLF (\\r\\n)", "+ LF (\\n)"]
        else:
            lineas = ["@@ salto de línea final @@", "- sin salto final", "+ con salto final"]
    return lineas[:max_lineas] + (["…"] if len(lineas) > max_lineas else [])


def error_forma(ruta: Path | str, texto: str, impreso: str) -> str | None:
    if sin_comentarios(texto) == impreso:
        return None
    diff = "\n".join(diferencia(texto, impreso))
    return (f"{ruta}: fuera de la forma única\n{diff}\n"
            f"oracle formatear {ruta} --escribir")
