"""El álgebra: relaciones, expresiones y los operadores. Sin dependencias.

Una **fila de trabajo** es un mapa `alias → hecho`, más las columnas derivadas bajo la clave
reservada `_`. Toda operación toma filas y devuelve filas: eso es la clausura.

**Sólo están implementados tres de los seis operadores** —`de`, `donde`, `resumen`— porque son los
únicos que piden las medidas que existen hoy. La regla de la especificación es *no se agrega un
operador hasta que una segunda medida lo necesite*, y aplica también a implementarlos: un operador
sin usuario es un operador sin verificar. Los otros tres levantan un error que dice cuál es su
disparador, así que el día que hagan falta no hay que adivinar por qué faltan.
"""

from __future__ import annotations

from typing import Any, Callable

ALIAS_DERIVADO = "_"


class ErrorDeAlgebra(ValueError):
    """La expresión o el operador no cumplen el contrato."""


class OperadorNoImplementado(NotImplementedError):
    """Declarado en la especificación, sin usuario todavía."""


# ---- funciones escalares (el mecanismo de UDF) ------------------------------------

ESCALARES: dict[str, Callable[..., Any]] = {}


def escalar(nombre: str, unidad: str = ""):
    """Registra una función de dominio. Se DECLARA para que aparezca en el inventario: una función
    importada a mano no se puede contar ni discutir, igual que un umbral escondido en una firma."""
    def envolver(fn):
        if nombre in ESCALARES:
            raise ErrorDeAlgebra(f"la escalar «{nombre}» ya está registrada")
        fn.unidad = unidad
        ESCALARES[nombre] = fn
        return fn
    return envolver


# ---- expresiones ------------------------------------------------------------------

def _cmp(op):
    return {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
    }[op]


COMPARADORES = ("==", "!=", "<", "<=", ">", ">=")
LOGICOS = ("y", "o", "no")
ACCESORES = ("campo", "hecho", "col")


def evaluar_expr(expr, fila: dict):
    """Un literal es un literal; el acceso a datos es SIEMPRE explícito.

    Se eligió `["campo", alias, nombre]` en vez de la forma corta `"a.x"` (y en vez de dejar que un
    string suelto signifique un alias) porque si no, un valor de texto que coincida con un alias
    cambiaría de significado según el contexto. Es más verboso y no tiene casos raros.
    """
    if not isinstance(expr, list):
        return expr                                   # número, bool, string, None

    if not expr:
        raise ErrorDeAlgebra("expresión vacía")
    cabeza, resto = expr[0], expr[1:]

    if cabeza == "campo":
        alias, nombre = resto
        if alias not in fila:
            raise ErrorDeAlgebra(f"el alias «{alias}» no existe en la fila")
        return fila[alias].get(nombre)
    if cabeza == "hecho":
        (alias,) = resto
        if alias not in fila:
            raise ErrorDeAlgebra(f"el alias «{alias}» no existe en la fila")
        return fila[alias]
    if cabeza == "col":
        (nombre,) = resto
        return fila.get(ALIAS_DERIVADO, {}).get(nombre)

    if cabeza in COMPARADORES:
        a, b = (evaluar_expr(x, fila) for x in resto)
        if a is None or b is None:
            # comparar contra un campo ausente es casi siempre un error de la medida, no un False
            raise ErrorDeAlgebra(f"«{cabeza}» sobre un valor ausente: {expr}")
        return _cmp(cabeza)(a, b)
    if cabeza == "y":
        return all(evaluar_expr(x, fila) for x in resto)
    if cabeza == "o":
        return any(evaluar_expr(x, fila) for x in resto)
    if cabeza == "no":
        (x,) = resto
        return not evaluar_expr(x, fila)

    if cabeza in ESCALARES:
        return ESCALARES[cabeza](*(evaluar_expr(x, fila) for x in resto))

    raise ErrorDeAlgebra(f"«{cabeza}» no es accesor, comparador, lógico ni escalar declarada")


# ---- agregados --------------------------------------------------------------------

AGREGADOS: dict[str, Callable[[list], Any]] = {
    "contar": len,
    "max": lambda xs: max(xs) if xs else 0,
    "min": lambda xs: min(xs) if xs else 0,
    "suma": sum,
    "promedio": lambda xs: (sum(xs) / len(xs)) if xs else 0,
}


# ---- operadores -------------------------------------------------------------------

DISPARADORES = {
    "con": "una medida que necesite una columna derivada reusada en más de un paso",
    "unir": "el catálogo de geometría: «pares de piezas que se clavan» es un producto",
    "agrupar": "contar por grupo — p. ej. importadores por módulo (ver «ausencia» en la espec.)",
}


def _de(evidencia: dict, relacion: str, alias: str) -> list[dict]:
    return [{alias: dict(hecho)} for hecho in evidencia.get(relacion, [])]


def aplicar(paso, filas: list[dict], evidencia: dict) -> list[dict]:
    op = paso[0]
    if op == "de":
        relacion, alias = paso[1], paso[2]
        return _de(evidencia, relacion, alias)
    if op == "donde":
        return [f for f in filas if evaluar_expr(paso[1], f)]
    if op in DISPARADORES:
        raise OperadorNoImplementado(
            f"«{op}» está declarado en la especificación y todavía no tiene usuario. "
            f"Se implementa cuando aparezca: {DISPARADORES[op]}")
    raise ErrorDeAlgebra(f"operador desconocido: «{op}»")


def desde(tuberia, evidencia: dict) -> list[dict]:
    """`["desde", fuente, paso, paso, …]` → las filas que sobrevivieron. **Son los testigos.**"""
    if tuberia[0] != "desde":
        raise ErrorDeAlgebra("una tubería empieza con «desde»")
    filas: list[dict] = []
    for i, paso in enumerate(tuberia[1:]):
        filas = aplicar(paso, filas, evidencia)
        if i == 0 and paso[0] != "de" and paso[0] not in DISPARADORES:
            raise ErrorDeAlgebra("el primer paso tiene que ser una fuente («de»)")
    return filas


def resumir(resumen, filas: list[dict]):
    """`["resumen", agg, expr]` → el escalar. `contar` no evalúa la expresión: cuenta filas."""
    _, agg, expr = resumen
    if agg not in AGREGADOS:
        raise ErrorDeAlgebra(f"agregado desconocido: «{agg}» (hay {sorted(AGREGADOS)})")
    if agg == "contar":
        return len(filas)
    return AGREGADOS[agg]([evaluar_expr(expr, f) for f in filas])
