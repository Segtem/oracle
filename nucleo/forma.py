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


def datos_en_forma_unica(texto: str, nombre, *, macros=None, error=ValueError) -> list:
    """Lee superficie `.oracle` y exige la forma única. `error` es la excepción de quien llama.

    Es la única puerta de texto a árbol: la usan los cargadores de medidas y de macros y
    `Motor.desde_texto`, así que una grafía que no carga en un lado no carga en ninguno.
    """
    from .sintaxis import ErrorSintaxis, fragmento_de_error, imprimir, leer_con_mapa
    from .version import VersionInvalida, exigir_sintaxis_compatible
    try:
        lectura = leer_con_mapa(texto, macros=macros)
    except ErrorSintaxis as e:
        raise error(f"{nombre}: {fragmento_de_error(e, texto)}") from e
    try:
        exigir_sintaxis_compatible(lectura.version)
    except VersionInvalida as e:
        raise error(f"{nombre}: {e}") from e
    fuera = error_forma(nombre, texto, imprimir(lectura.datos, macros=macros))
    if fuera:
        raise error(fuera)
    return lectura.datos
