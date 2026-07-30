"""Macros: medidas que escriben medidas.

De las 27 medidas del catálogo, **22 tenían exactamente la misma forma**:

    ["desde", ["de", R, x], ["donde", P]] · ["resumen","contar",1] · ["umbral","<=",0, …]

La regla del repositorio decía que las macros se habilitan «cuando aparezca la quinta medida con la
misma forma». Aparecieron veintidós. Sin macro, escribir la medida 28 es la misma ceremonia que la 1,
y cambiar esa forma alguna vez serían 22 archivos.

## Por qué esto no cuesta inspeccionabilidad

Una macro **expande a los mismos datos**, igual que en LISP: la expansión ocurre antes de construir la
medida, así que el evaluador, la mutación, el inventario y el nivel L2 siguen viendo formas canónicas
y no se enteran de que hubo macro. `tools/medida.py --expandir` muestra el resultado.

## `peor` cierra una deuda de diseño

El caso `012` del corpus anotaba que en el patrón «`donde tol` → `max` → `umbral tol`» la tolerancia
aparecía **dos veces** y nada las mantenía juntas. La macro la recibe **una sola vez** y genera las
dos. La deuda desaparece por construcción, que es mejor que comprobarla.

## Las macros son azúcar, no un embudo

La forma canónica sigue siendo válida y hay medidas que no pasan por macro (`colocacion.interpenetracion`
une DOS relaciones distintas y resume por `max`). Un sistema de macros que obliga a todo a pasar por él
se vuelve una camisa de fuerza: si la forma no encaja, se escribe canónica y listo.
"""

from __future__ import annotations


class MacroMalUsada(ValueError):
    """La invocación no tiene la forma que la macro necesita."""


def _pide(datos: list, n: int, nombre: str, firma: str) -> None:
    if len(datos) != n:
        raise MacroMalUsada(f"«{nombre}» va {firma} — recibió {len(datos)} elementos")


def ninguno(datos: list) -> list:
    """`["ninguno", id, relacion, alias, predicado, porque, alcance]`

    «Ninguna fila de `relacion` debe cumplir `predicado`». Es el 80% de las medidas: filtrás lo que
    ofende, contás, y cero es el único número aceptable.
    """
    _pide(datos, 7, "ninguno", "[id, relacion, alias, predicado, porque, alcance]")
    _, mid, relacion, alias, pred, porque, alcance = datos
    return ["medida", mid,
            ["desde", ["de", relacion, alias], ["donde", pred]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, porque],
            ["alcance", alcance]]


def ninguno_par(datos: list) -> list:
    """`["ninguno-par", id, relacion, aliasA, aliasB, predicado, porque, alcance]`

    Lo mismo sobre PARES de filas de la misma relación: homónimos, piezas que se clavan, las dos
    puntas de un relevo. Expande al producto de la relación consigo misma.
    """
    _pide(datos, 8, "ninguno-par", "[id, relacion, aliasA, aliasB, predicado, porque, alcance]")
    _, mid, relacion, a, b, pred, porque, alcance = datos
    if a == b:
        raise MacroMalUsada(f"{mid}: los dos alias de «ninguno-par» tienen que ser distintos")
    return ["medida", mid,
            ["desde", ["unir", ["de", relacion, a], ["de", relacion, b]], ["donde", pred]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, porque],
            ["alcance", alcance]]


def peor(datos: list) -> list:
    """`["peor", id, relacion, alias, expresion, tolerancia, porque, alcance]`

    «El peor caso de `expresion` no pasa de `tolerancia`». La tolerancia se escribe **una sola vez** y
    la macro genera con ella el filtro (que define los testigos) y el umbral (que trae la defensa).
    Ésa duplicación era el caso `012` del corpus.
    """
    _pide(datos, 8, "peor", "[id, relacion, alias, expresion, tolerancia, porque, alcance]")
    _, mid, relacion, alias, expr, tol, porque, alcance = datos
    return ["medida", mid,
            ["desde", ["de", relacion, alias], ["donde", [">", expr, tol]]],
            ["resumen", "max", expr],
            ["umbral", "<=", tol, porque],
            ["alcance", alcance]]


MACROS = {"ninguno": ninguno, "ninguno-par": ninguno_par, "peor": peor}


def es_macro(datos) -> bool:
    return isinstance(datos, list) and bool(datos) and datos[0] in MACROS


def expandir(datos: list) -> list:
    """Datos → forma canónica. Idempotente sobre lo que ya es canónico.

    Una sola pasada a propósito: una macro que expande a otra macro es una torre que nadie pidió, y
    hoy ninguna lo necesita. El día que haga falta, esto es un bucle de dos líneas — y ahí habrá que
    poner una guarda de recursión, como la de las funciones del Graph.
    """
    if not es_macro(datos):
        return datos
    expandida = MACROS[datos[0]](datos)
    if es_macro(expandida):
        raise MacroMalUsada(f"«{datos[0]}» expandió a otra macro; hoy no está soportado")
    return expandida
