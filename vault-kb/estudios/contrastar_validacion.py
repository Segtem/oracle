"""Contraste reproducible de las dos implementaciones de validación conservadas en el estudio.

Alterna tres muestras por variante sobre una integración real de sombras. Mide tiempo; no impone
un umbral de rendimiento a la suite. El resto del evaluador y el test son los del árbol actual.
"""

import ast
import io
import json
import statistics
import sys
import time
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path = [str(RAIZ), *sys.path]

from nucleo import algebra  # noqa: E402
from tests.test_sombras_integracion import ModoSombra  # noqa: E402


def contrastar() -> dict:
    """Sustituye sólo las funciones de validación y exige que ambas variantes pasen la prueba."""
    carpeta = RAIZ / "estudios" / "2026-09-10-validacion"
    fuentes = {nombre: (carpeta / f"algebra-{nombre}.txt").read_text(encoding="utf-8")
               for nombre in ("antes", "despues")}
    resultados = []
    for nombre in ("antes", "despues", "despues", "antes", "antes", "despues"):
        funciones = [nodo for nodo in ast.parse(fuentes[nombre]).body
                     if isinstance(nodo, ast.FunctionDef)
                     and nodo.name in ("validar_expr", "_validar_expr")]
        exec(compile(ast.Module(body=funciones, type_ignores=[]),
                     f"<validación {nombre}>", "exec"), algebra.__dict__)
        suite = unittest.TestSuite([ModoSombra("test_una_sombra_sin_fecha_lo_dice")])
        inicio = time.perf_counter()
        resultado = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        segundos = time.perf_counter() - inicio
        if not resultado.wasSuccessful():
            raise AssertionError((nombre, resultado.errors, resultado.failures))
        resultados.append({"variante": nombre, "segundos": segundos})
    medianas = {nombre: statistics.median(fila["segundos"] for fila in resultados
                                        if fila["variante"] == nombre)
                for nombre in fuentes}
    return {"muestras": resultados, "medianas": medianas,
            "reduccion_porcentual": 100 * (1 - medianas["despues"] / medianas["antes"])}


if __name__ == "__main__":
    print(json.dumps(contrastar(), ensure_ascii=False, indent=2))
