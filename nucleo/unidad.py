"""Derivación de la unidad de lo que una medida compara (L−1).

Para cada medida del catálogo, deriva la unidad de cada cantidad comparada:
- `["campo", alias, campo]`: la unidad declarada en la relación para ese campo (o `sin_unidad` para relaciones del lenguaje/proceso).
- `["col", nombre]`: la unidad de la clave o agregado producida en `agrupar`.
- Una escalar registrada: su `unidad` de retorno si fue declarada, o propagada para operadores aritméticos universales.
- `contar`: `adimensional` (conteo).
- Literales: heredan la unidad del otro operando en la comparación.
- Cualquier otra cosa: `no derivable` (`es_derivable: False`).

Emite la relación del lenguaje `cantidad_comparada(medida, unidad, es_derivable)`.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping

from .algebra import COMPARADORES, _registro
from .medida import Medida, relaciones_del_lenguaje_declaradas
from .relacion import Relacion

RELACIONES_DE_UNIDAD = frozenset({"cantidad_comparada"})

UNIDAD_ADIMENSIONAL = "adimensional"
UNIDAD_NO_DERIVABLE = "sin_declarar"
UNIDAD_SIN_UNIDAD = "sin_unidad"

_PROCESO_RELACIONES = frozenset({
    "afirmacion",
    "alcanzable",
    "archivo",
    "cambio",
    "corrida_mutacion",
    "hallazgo",
    "hecho_historia",
    "importa",
    "modulo",
    "mutante",
    "paquete",
    "veredicto",
})


def extraer_alias_de_fuente(fuente: Any) -> dict[str, str]:
    """Extrae el mapeo alias -> nombre_relacion desde la fuente de una tubería."""
    if not isinstance(fuente, list) or not fuente:
        return {}
    cabeza = fuente[0]
    if cabeza == "de" and len(fuente) == 3 and isinstance(fuente[1], str) and isinstance(fuente[2], str):
        return {fuente[2]: fuente[1]}
    if cabeza == "unir" and len(fuente) == 3:
        salida = extraer_alias_de_fuente(fuente[1])
        salida.update(extraer_alias_de_fuente(fuente[2]))
        return salida
    return {}


def derivar_unidad_nodo(
    nodo: Any,
    alias_relaciones: Mapping[str, str],
    relaciones: Mapping[str, Relacion],
    registro: Mapping[str, Callable[..., Any]],
    relaciones_lenguaje: frozenset[str],
    columnas: Mapping[str, str] | None = None,
) -> str | None:
    """Deriva la unidad intrínseca de un nodo o expresión. Devuelve None si no es derivable o es literal."""
    if not isinstance(nodo, list) or not nodo:
        return None

    cols = columnas or {}
    cabeza = nodo[0]

    if cabeza == "campo" and len(nodo) == 3 and isinstance(nodo[1], str) and isinstance(nodo[2], str):
        alias, campo_nombre = nodo[1], nodo[2]
        rel_nombre = alias_relaciones.get(alias)
        if rel_nombre is None:
            return None
        if rel_nombre in relaciones_lenguaje or rel_nombre in _PROCESO_RELACIONES:
            return UNIDAD_SIN_UNIDAD
        if rel_nombre in relaciones:
            for c in relaciones[rel_nombre].campos:
                if c.nombre == campo_nombre:
                    return c.unidad
        return None

    if cabeza == "col" and len(nodo) == 2 and isinstance(nodo[1], str):
        return cols.get(nodo[1])

    if cabeza == "resumen" and len(nodo) == 3:
        if nodo[1] == "contar":
            return UNIDAD_ADIMENSIONAL
        return derivar_unidad_nodo(nodo[2], alias_relaciones, relaciones, registro, relaciones_lenguaje, cols)

    if isinstance(cabeza, str) and cabeza in registro:
        fn = registro[cabeza]
        u = getattr(fn, "unidad", "")
        if isinstance(u, str) and u.strip():
            unidades_argumentos = getattr(fn, "unidades_argumentos", ())
            argumentos = nodo[1:]
            if not isinstance(unidades_argumentos, tuple):
                return None
            if len(unidades_argumentos) != getattr(fn, "aridad_max", None):
                return None
            for esperado, argumento in zip(unidades_argumentos, argumentos):
                if not isinstance(argumento, list):
                    continue
                if (
                    len(argumento) == 2
                    and argumento[0] == "hecho"
                    and isinstance(argumento[1], str)
                ):
                    observado = UNIDAD_SIN_UNIDAD
                else:
                    observado = derivar_unidad_nodo(
                        argumento,
                        alias_relaciones,
                        relaciones,
                        registro,
                        relaciones_lenguaje,
                        cols,
                    )
                if observado != esperado:
                    return None
            return u.strip()
        if len(nodo) >= 3:
            u1 = derivar_unidad_nodo(nodo[1], alias_relaciones, relaciones, registro, relaciones_lenguaje, cols)
            u2 = derivar_unidad_nodo(nodo[2], alias_relaciones, relaciones, registro, relaciones_lenguaje, cols)
            if u1 is not None and not isinstance(nodo[2], list):
                return u1
            if u2 is not None and not isinstance(nodo[1], list):
                return u2
            if u1 and u2 and u1 == u2:
                return u1
            if {u1, u2} == {UNIDAD_ADIMENSIONAL, UNIDAD_SIN_UNIDAD}:
                return UNIDAD_SIN_UNIDAD
        return None

    return None


def derivar_unidad_comparacion(
    izq: Any,
    der: Any,
    alias_relaciones: Mapping[str, str],
    relaciones: Mapping[str, Relacion],
    registro: Mapping[str, Callable[..., Any]],
    relaciones_lenguaje: frozenset[str],
    columnas: Mapping[str, str] | None = None,
) -> tuple[bool, str]:
    """Deriva la unidad de una comparación entre dos operandos."""
    izq_lit = not isinstance(izq, list)
    der_lit = not isinstance(der, list)

    if izq_lit and der_lit:
        return False, UNIDAD_NO_DERIVABLE

    if izq_lit:
        u = derivar_unidad_nodo(der, alias_relaciones, relaciones, registro, relaciones_lenguaje, columnas)
        if u is not None:
            return True, u
        return False, UNIDAD_NO_DERIVABLE

    if der_lit:
        u = derivar_unidad_nodo(izq, alias_relaciones, relaciones, registro, relaciones_lenguaje, columnas)
        if u is not None:
            return True, u
        return False, UNIDAD_NO_DERIVABLE

    u_izq = derivar_unidad_nodo(izq, alias_relaciones, relaciones, registro, relaciones_lenguaje, columnas)
    u_der = derivar_unidad_nodo(der, alias_relaciones, relaciones, registro, relaciones_lenguaje, columnas)

    if u_izq and u_der:
        if u_izq == u_der:
            return True, u_izq
        if u_izq == UNIDAD_ADIMENSIONAL:
            return True, u_der
        if u_der == UNIDAD_ADIMENSIONAL:
            return True, u_izq

    return False, UNIDAD_NO_DERIVABLE


def _extraer_comparaciones_de_expr(expr: Any) -> list[tuple[Any, Any]]:
    """Busca recursivamente comparaciones [op, izq, der] en una expresión."""
    if not isinstance(expr, list) or not expr:
        return []

    cabeza = expr[0]
    comparaciones: list[tuple[Any, Any]] = []

    if isinstance(cabeza, str) and cabeza in COMPARADORES and len(expr) == 3:
        izq, der = expr[1], expr[2]
        comparaciones.append((izq, der))
        comparaciones.extend(_extraer_comparaciones_de_expr(izq))
        comparaciones.extend(_extraer_comparaciones_de_expr(der))
    else:
        for hijo in expr[1:]:
            comparaciones.extend(_extraer_comparaciones_de_expr(hijo))

    return comparaciones


def _columnas_de_agrupar(
    paso: Any,
    alias_relaciones: Mapping[str, str],
    relaciones: Mapping[str, Relacion],
    registro: Mapping[str, Callable[..., Any]],
    relaciones_lenguaje: frozenset[str],
) -> dict[str, str]:
    cols: dict[str, str] = {}
    if not isinstance(paso, list) or len(paso) != 3 or paso[0] != "agrupar":
        return cols
    claves, agregados = paso[1], paso[2]
    if isinstance(claves, list):
        for item in claves:
            if isinstance(item, list) and len(item) == 2 and isinstance(item[0], str):
                u = derivar_unidad_nodo(item[1], alias_relaciones, relaciones, registro, relaciones_lenguaje)
                cols[item[0]] = u or UNIDAD_SIN_UNIDAD
    if isinstance(agregados, list):
        for item in agregados:
            if isinstance(item, list) and len(item) == 3 and isinstance(item[0], str):
                nom, agg, expr = item[0], item[1], item[2]
                if agg == "contar":
                    cols[nom] = UNIDAD_ADIMENSIONAL
                elif agg == "suma":
                    u = derivar_unidad_nodo(expr, alias_relaciones, relaciones, registro, relaciones_lenguaje)
                    cols[nom] = u if u is not None else UNIDAD_ADIMENSIONAL
                else:
                    u = derivar_unidad_nodo(expr, alias_relaciones, relaciones, registro, relaciones_lenguaje)
                    cols[nom] = u or UNIDAD_SIN_UNIDAD
    return cols


def _extraer_comparaciones_de_paso(paso: Any) -> list[tuple[Any, Any]]:
    if not isinstance(paso, list) or not paso:
        return []
    op = paso[0]
    if op == "donde" and len(paso) == 2:
        return _extraer_comparaciones_de_expr(paso[1])
    if op == "agrupar" and len(paso) == 3:
        claves, agregados = paso[1], paso[2]
        comparaciones = []
        if isinstance(claves, list):
            for item in claves:
                if isinstance(item, list) and len(item) == 2:
                    comparaciones.extend(_extraer_comparaciones_de_expr(item[1]))
        if isinstance(agregados, list):
            for item in agregados:
                if isinstance(item, list) and len(item) == 3:
                    comparaciones.extend(_extraer_comparaciones_de_expr(item[2]))
        return comparaciones
    return []


def comparaciones_de_medida(
    medida: Medida,
    relaciones: Mapping[str, Relacion],
    registro: Mapping[str, Callable[..., Any]],
    relaciones_lenguaje: frozenset[str],
) -> list[dict]:
    """Genera los hechos de cantidad_comparada para una sola medida."""
    fuente = medida.tuberia[1] if isinstance(medida.tuberia, list) and len(medida.tuberia) >= 2 else None
    alias_map = extraer_alias_de_fuente(fuente)
    columnas: dict[str, str] = {}
    filas: list[dict] = []

    # Registrar columnas si hay un paso de agrupar
    if isinstance(medida.tuberia, list):
        for paso in medida.tuberia[2:]:
            columnas.update(_columnas_de_agrupar(paso, alias_map, relaciones, registro, relaciones_lenguaje))

    # 1. Comparación del umbral final (resumen vs límite)
    es_der, unidad = derivar_unidad_comparacion(
        medida.resumen, medida.limite, alias_map, relaciones, registro, relaciones_lenguaje, columnas
    )
    filas.append({
        "medida": medida.id,
        "unidad": unidad,
        "es_derivable": es_der,
    })

    # 2. Comparaciones en los pasos de la tubería
    if isinstance(medida.tuberia, list):
        for paso in medida.tuberia[2:]:
            for izq, der in _extraer_comparaciones_de_paso(paso):
                es_der_paso, unidad_paso = derivar_unidad_comparacion(
                    izq, der, alias_map, relaciones, registro, relaciones_lenguaje, columnas
                )
                filas.append({
                    "medida": medida.id,
                    "unidad": unidad_paso,
                    "es_derivable": es_der_paso,
                })

    return filas


def hechos_de_unidades(
    medidas: Iterable[Medida],
    relaciones: Mapping[str, Relacion] | Iterable[Relacion] | None = None,
    registro: Mapping[str, Callable[..., Any]] | None = None,
) -> dict[str, list[dict]]:
    """Calcula los hechos de la relación `cantidad_comparada` para un conjunto de medidas."""
    if isinstance(relaciones, Mapping):
        rel_map = dict(relaciones)
    elif isinstance(relaciones, Iterable):
        rel_map = {r.nombre: r for r in relaciones if isinstance(r, Relacion)}
    else:
        rel_map = {}

    reg = _registro(registro)
    rel_lenguaje = relaciones_del_lenguaje_declaradas()
    filas: list[dict] = []

    for m in medidas:
        if not isinstance(m, Medida):
            raise ValueError(f"se esperaba `Medida`, no {type(m).__name__}")
        filas.extend(comparaciones_de_medida(m, rel_map, reg, rel_lenguaje))

    return {"cantidad_comparada": filas}


def como_hechos(
    medidas: Iterable[Medida],
    relaciones: Mapping[str, Relacion] | Iterable[Relacion] | None = None,
    registro: Mapping[str, Callable[..., Any]] | None = None,
) -> dict[str, list[dict]]:
    return hechos_de_unidades(medidas, relaciones=relaciones, registro=registro)
