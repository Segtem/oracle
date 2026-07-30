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


def _es_flotante(v) -> bool:
    """Un `bool` es `int` en Python, y un entero se compara exacto sin problema."""
    return isinstance(v, float) and not isinstance(v, bool)
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
        # La última pregunta abierta de la especificación, resuelta NEGÁNDOSE. `["==", x, 0]` sobre
        # centímetros es una falsedad esperando: 0.30000000000000004 no es 0.3, y la medida diría
        # verde sin que nadie se enterara. La igualdad exacta sólo tiene sentido sobre cosas que se
        # cuentan o se nombran; sobre cosas que se MIDEN hace falta una tolerancia, y declararla es
        # justamente lo que este lenguaje pide para todo umbral.
        if cabeza in ("==", "!=") and (_es_flotante(a) or _es_flotante(b)):
            raise ErrorDeAlgebra(
                f"«{cabeza}» sobre un flotante ({a!r}, {b!r}): la igualdad exacta entre cantidades "
                f"medidas es una falsedad silenciosa. Usá una tolerancia: "
                f'["<=", ["cerca", a, b], tol] o un umbral con «<=»')
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
}

FUENTES = ("de", "unir")


def _de(evidencia: dict, relacion: str, alias: str) -> list[dict]:
    return [{alias: dict(hecho)} for hecho in evidencia.get(relacion, [])]


def _unir(paso, evidencia: dict) -> list[dict]:
    """`["unir", izq, der, modo?]` → producto. Los alias de los dos lados conviven en la fila.

    Se implementó al llegar su disparador: «pares de piezas que se clavan» es un producto, y ninguna
    medida de proceso lo necesitaba. `modo` sigue sin usuario: `"izquierda"` traería el concepto de
    NULO, que es la peor verruga de SQL, y no hace falta para nada de lo que existe.
    """
    izq, der = paso[1], paso[2]
    modo = paso[3] if len(paso) > 3 else "todos"
    if modo != "todos":
        raise OperadorNoImplementado(
            f"«unir» en modo «{modo}» todavía no tiene usuario. Se implementa cuando aparezca una "
            "medida de AUSENCIA (p. ej. módulos sin ningún importador), y con ella hay que decidir "
            "cómo se representa un valor que falta — ver «ausencia» en la especificación")
    for lado in (izq, der):
        if lado[0] not in FUENTES:
            raise ErrorDeAlgebra(f"«unir» toma fuentes, y recibió «{lado[0]}»")

    filas_izq = aplicar(izq, [], evidencia)
    filas_der = aplicar(der, [], evidencia)
    salida = []
    for a in filas_izq:
        for b in filas_der:
            comunes = set(a) & set(b)
            if comunes:
                raise ErrorDeAlgebra(f"«unir» con alias repetido: {sorted(comunes)}")
            salida.append({**a, **b})
    return salida


def _agrupar(paso, filas: list[dict]) -> list[dict]:
    """`["agrupar", [[nombre, expr]…], [[nombre, agg, expr]…]]` → una fila por grupo.

    Un grupo NO es un hecho: es un resumen. Así que las filas que salen no llevan alias —los hechos
    se consumieron— sino columnas derivadas, que se leen con `["col", nombre]`. Ese accesor existía
    desde el principio y recién acá encuentra su usuario.

    **Con esto se expresa la AUSENCIA**, que era una de las preguntas abiertas de la especificación.
    El truco no es un `LEFT JOIN` con nulos —la peor verruga de SQL— sino agrupar sobre el producto
    SIN filtrar y agregar con `suma` sobre un predicado: los booleanos suman 0 y 1, así que un grupo
    donde nada casó da cero y sigue existiendo. Sin nulos y sin operador nuevo.
    """
    claves, agregados = paso[1], paso[2]
    grupos: dict[tuple, list[dict]] = {}
    for f in filas:
        k = tuple(evaluar_expr(expr, f) for _nombre, expr in claves)
        grupos.setdefault(k, []).append(f)

    salida = []
    for k, miembros in grupos.items():
        derivadas = {nombre: valor for (nombre, _expr), valor in zip(claves, k)}
        for nombre, agg, expr in agregados:
            if agg not in AGREGADOS:
                raise ErrorDeAlgebra(f"agregado desconocido: «{agg}»")
            valores = [evaluar_expr(expr, m) for m in miembros]
            derivadas[nombre] = len(miembros) if agg == "contar" else AGREGADOS[agg](valores)
        salida.append({ALIAS_DERIVADO: derivadas})
    return salida


def aplicar(paso, filas: list[dict], evidencia: dict) -> list[dict]:
    op = paso[0]
    if op == "de":
        relacion, alias = paso[1], paso[2]
        return _de(evidencia, relacion, alias)
    if op == "unir":
        return _unir(paso, evidencia)
    if op == "donde":
        return [f for f in filas if evaluar_expr(paso[1], f)]
    if op == "agrupar":
        return _agrupar(paso, filas)
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
        if i == 0 and paso[0] not in FUENTES:
            raise ErrorDeAlgebra(f"el primer paso tiene que ser una fuente {FUENTES}")
        filas = aplicar(paso, filas, evidencia)
    return filas


def resumir(resumen, filas: list[dict]):
    """`["resumen", agg, expr]` → el escalar. `contar` no evalúa la expresión: cuenta filas."""
    _, agg, expr = resumen
    if agg not in AGREGADOS:
        raise ErrorDeAlgebra(f"agregado desconocido: «{agg}» (hay {sorted(AGREGADOS)})")
    if agg == "contar":
        return len(filas)
    return AGREGADOS[agg]([evaluar_expr(expr, f) for f in filas])
