"""El álgebra: relaciones, expresiones y los operadores. Sin dependencias.

Una **fila de trabajo** es un mapa `alias → hecho`, más las columnas derivadas bajo la clave
reservada `_`. Toda operación toma filas y devuelve filas: eso es la clausura.

El lenguaje activo tiene cinco operadores: `de`, `donde`, `resumen`, `unir` y `agrupar`.
"""

from __future__ import annotations

import inspect
import math
import re
from collections.abc import Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Callable

ALIAS_DERIVADO = "_"


class ErrorDeAlgebra(ValueError):
    """La expresión o el operador no cumplen el contrato."""


@dataclass(frozen=True)
class LimitesAlgebra:
    """Presupuesto explícito para evaluar datos y expresiones no confiables.

    Los límites son parte de cada evaluación, no variables globales: dos consumidores pueden elegir
    presupuestos distintos en el mismo proceso sin afectarse entre sí.
    """

    filas_por_relacion: int = 100_000
    producto_cartesiano: int = 1_000_000
    profundidad_expresion: int = 64
    # Cuántas veces puede una macro expandir a otra antes de declararse bucle. Dieciséis porque una
    # torre legítima tiene dos o tres pisos —una macro de proyecto sobre `ninguno`— y pasar de eso es
    # casi seguro recursión, no diseño. El número es alto a propósito: su trabajo es cortar un cuelgue,
    # no disciplinar el estilo de nadie.
    expansiones_maximas: int = 16

    def __post_init__(self) -> None:
        for nombre, valor in (
                ("filas_por_relacion", self.filas_por_relacion),
                ("producto_cartesiano", self.producto_cartesiano),
                ("profundidad_expresion", self.profundidad_expresion),
                ("expansiones_maximas", self.expansiones_maximas)):
            if not isinstance(valor, int) or isinstance(valor, bool) or valor < 1:
                raise ErrorDeAlgebra(
                    f"el límite {nombre} debe ser un entero positivo (no bool), no {valor!r}")


_PREDETERMINADOS: LimitesAlgebra | None = None


def limites_predeterminados() -> LimitesAlgebra:
    """El presupuesto por omisión, construido al primer uso y memorizado.

    Antes era `LIMITES_PREDETERMINADOS = LimitesAlgebra()` a nivel de módulo, y eso volvía inmedible
    a `__post_init__`: un mutante que rompiera la validación hacía fallar el **import** de
    `nucleo.algebra` —del que cuelga toda la suite— así que el arnés reportaba «error» y no «muerte».
    Un mutante sin veredicto es un hueco, y un hueco que además contamina la ronda entera de
    inconcluso es peor que cualquiera de las dos respuestas.

    Se pierde el autochequeo al importar; no se pierde nada más, porque los defaults ya están fijados
    por `test_00_los_limites_predeterminados_son_parte_del_contrato`. El objeto es inmutable y
    compartido, igual que antes.
    """
    global _PREDETERMINADOS
    if _PREDETERMINADOS is None:
        _PREDETERMINADOS = LimitesAlgebra()
    return _PREDETERMINADOS


def _limites(limites: LimitesAlgebra | None) -> LimitesAlgebra:
    if limites is None:
        return limites_predeterminados()
    if not isinstance(limites, LimitesAlgebra):
        raise ErrorDeAlgebra("`limites` debe ser una instancia de LimitesAlgebra")
    return limites


# ---- funciones escalares (el mecanismo de UDF) ------------------------------------

class RegistroEscalares(dict[str, Callable[..., Any]]):
    """Registro copiable que un consumidor puede poseer sin compartir estado global."""

    def copiar(self) -> "RegistroEscalares":
        return RegistroEscalares(self)


ESCALARES = RegistroEscalares()
NOMBRE_ESCALAR_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_PROCEDENCIA_ESCALAR = "oracle"
_REGISTRO_ACTIVO: ContextVar[RegistroEscalares | None] = ContextVar(
    "oracle_registro_escalares", default=None)
_PROCEDENCIA_ACTIVA: ContextVar[str | None] = ContextVar(
    "oracle_procedencia_escalar", default=None)


def _registro(registro: Mapping[str, Callable[..., Any]] | None = None):
    if registro is not None:
        if not isinstance(registro, Mapping):
            raise ErrorDeAlgebra("`registro` debe ser un mapa de funciones escalares")
        return registro
    activo = _REGISTRO_ACTIVO.get()
    return ESCALARES if activo is None else activo


@contextmanager
def usar_registro(registro: RegistroEscalares, *, procedencia: str | None = None):
    """Dirige declaraciones con ``@escalar`` a un registro propiedad del consumidor."""
    if not isinstance(registro, RegistroEscalares):
        raise ErrorDeAlgebra("el registro activo debe ser RegistroEscalares")
    token_registro = _REGISTRO_ACTIVO.set(registro)
    token_procedencia = _PROCEDENCIA_ACTIVA.set(procedencia)
    try:
        yield registro
    finally:
        _PROCEDENCIA_ACTIVA.reset(token_procedencia)
        _REGISTRO_ACTIVO.reset(token_registro)


def _contrato_de_escalar(fn) -> tuple[int, int | None]:
    try:
        parametros = inspect.signature(fn).parameters.values()
    except (TypeError, ValueError) as e:
        raise ErrorDeAlgebra("una escalar debe publicar una firma inspeccionable") from e
    minimo = maximo = 0
    variadica = False
    for parametro in parametros:
        if parametro.kind in (parametro.POSITIONAL_ONLY, parametro.POSITIONAL_OR_KEYWORD):
            maximo += 1
            if parametro.default is parametro.empty:
                minimo += 1
        elif parametro.kind is parametro.VAR_POSITIONAL:
            variadica = True
        elif parametro.kind is parametro.KEYWORD_ONLY and parametro.default is parametro.empty:
            raise ErrorDeAlgebra(
                f"la escalar tiene un argumento sólo-keyword obligatorio: {parametro.name}")
    return minimo, None if variadica else maximo


def escalar(nombre: str, unidad: str = "", *, registro: RegistroEscalares | None = None):
    """Registra una función de dominio. Se DECLARA para que aparezca en el inventario: una función
    importada a mano no se puede contar ni discutir, igual que un umbral escondido en una firma."""
    if not isinstance(nombre, str) or NOMBRE_ESCALAR_RE.fullmatch(nombre) is None:
        raise ErrorDeAlgebra(
            "el nombre de una escalar usa minúsculas ASCII, dígitos y `_`, sin puntos")
    if not isinstance(unidad, str) or "\n" in unidad or "\r" in unidad:
        raise ErrorDeAlgebra("la unidad de una escalar debe ser texto de una línea")

    def envolver(fn):
        destino = _registro(registro)
        if nombre in destino:
            raise ErrorDeAlgebra(f"la escalar «{nombre}» ya está registrada")
        aridad_min, aridad_max = _contrato_de_escalar(fn)
        fn.nombre_escalar = nombre
        fn.unidad = unidad
        fn.aridad_min = aridad_min
        fn.aridad_max = aridad_max
        fn.procedencia_escalar = _PROCEDENCIA_ACTIVA.get() or _PROCEDENCIA_ESCALAR
        destino[nombre] = fn
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


def _familia_escalar(valor) -> str:
    """Familia usada para impedir comparaciones que Python acepta de manera accidental.

    `bool` queda separado de los números aunque sea una subclase de `int`. Sólo `suma` y
    `promedio` lo interpretan explícitamente como indicador 0/1.
    """
    if isinstance(valor, bool):
        return "booleano"
    if isinstance(valor, (int, float)):
        return "numero"
    if isinstance(valor, str):
        return "texto"
    if valor is None:
        return "ausente"
    return type(valor).__name__


def validar_finito(valor, que: str = "el número") -> None:
    if _es_flotante(valor) and not math.isfinite(valor):
        raise ErrorDeAlgebra(f"{que} tiene que ser finito, no {valor!r}")


def comparar(op: str, a, b):
    """Compara escalares bajo el contrato del DSL, incluido el umbral final."""
    if op not in COMPARADORES:
        raise ErrorDeAlgebra(f"comparador desconocido: «{op}»")
    if a is None or b is None:
        raise ErrorDeAlgebra(f"«{op}» sobre un valor ausente: {a!r}, {b!r}")

    validar_finito(a, "el operando izquierdo")
    validar_finito(b, "el operando derecho")
    familia_a, familia_b = _familia_escalar(a), _familia_escalar(b)
    if familia_a not in {"numero", "booleano", "texto"} or familia_b not in {
            "numero", "booleano", "texto"}:
        raise ErrorDeAlgebra(
            f"«{op}» sólo compara escalares, no {familia_a} y {familia_b}")
    if familia_a != familia_b:
        raise ErrorDeAlgebra(
            f"«{op}» recibió tipos incompatibles: {familia_a} y {familia_b}")
    if op in ("==", "!=") and (_es_flotante(a) or _es_flotante(b)):
        raise ErrorDeAlgebra(
            f"«{op}» sobre un flotante ({a!r}, {b!r}): la igualdad exacta entre cantidades "
            "medidas es una falsedad silenciosa. Usá una comparación de orden con tolerancia")
    try:
        return _cmp(op)(a, b)
    except TypeError as e:
        raise ErrorDeAlgebra(
            f"«{op}» no puede comparar {type(a).__name__} con {type(b).__name__}") from e


LOGICOS = ("y", "o", "no")
ACCESORES = ("campo", "hecho", "col")
LITERALES_ESCALARES = (str, int, float, bool, type(None))


def _validar_nombre(valor, que: str) -> None:
    if not isinstance(valor, str) or not valor.strip():
        raise ErrorDeAlgebra(f"{que} tiene que ser texto no vacío, no {valor!r}")


def validar_expr(expr, limites: LimitesAlgebra | None = None, *,
                 registro: Mapping[str, Callable[..., Any]] | None = None,
                 _profundidad: int = 0) -> None:
    """Valida recursivamente la forma de una expresión, sin evaluarla.

    Los literales son los escalares que JSON puede representar. Las listas son siempre llamadas del
    DSL: accesor, comparador, lógico o escalar registrada.
    """
    limites = _limites(limites)
    escalares = _registro(registro)
    if _profundidad > limites.profundidad_expresion:
        raise ErrorDeAlgebra(
            "la expresión supera la profundidad máxima declarada "
            f"({limites.profundidad_expresion})")
    if not isinstance(expr, list):
        if not isinstance(expr, LITERALES_ESCALARES):
            raise ErrorDeAlgebra(
                f"un literal tiene que ser escalar, no {type(expr).__name__}")
        return
    if not expr:
        raise ErrorDeAlgebra("expresión vacía")

    cabeza, argumentos = expr[0], expr[1:]
    _validar_nombre(cabeza, "la cabeza de una expresión")

    if cabeza == "campo":
        if len(expr) != 3:
            raise ErrorDeAlgebra("«campo» va ['campo', alias, nombre]")
        _validar_nombre(expr[1], "el alias de «campo»")
        _validar_nombre(expr[2], "el nombre de «campo»")
        return
    if cabeza == "hecho":
        if len(expr) != 2:
            raise ErrorDeAlgebra("«hecho» va ['hecho', alias]")
        _validar_nombre(expr[1], "el alias de «hecho»")
        return
    if cabeza == "col":
        if len(expr) != 2:
            raise ErrorDeAlgebra("«col» va ['col', nombre]")
        _validar_nombre(expr[1], "el nombre de «col»")
        return

    if cabeza in COMPARADORES:
        if len(expr) != 3:
            raise ErrorDeAlgebra(f"«{cabeza}» necesita exactamente dos operandos")
    elif cabeza in ("y", "o"):
        if len(expr) < 3:
            raise ErrorDeAlgebra(f"«{cabeza}» necesita al menos dos operandos")
    elif cabeza == "no":
        if len(expr) != 2:
            raise ErrorDeAlgebra("«no» necesita exactamente un operando")
    elif cabeza in escalares:
        fn = escalares[cabeza]
        minimo, maximo = fn.aridad_min, fn.aridad_max
        if len(argumentos) < minimo or (maximo is not None and len(argumentos) > maximo):
            rango = f"{minimo} o más" if maximo is None else (
                str(minimo) if minimo == maximo else f"entre {minimo} y {maximo}")
            raise ErrorDeAlgebra(
                f"la escalar «{cabeza}» acepta {rango} argumento(s), no {len(argumentos)}")
    else:
        raise ErrorDeAlgebra(
            f"«{cabeza}» no es accesor, comparador, lógico ni escalar declarada")

    for argumento in argumentos:
        validar_expr(
            argumento, limites, registro=escalares, _profundidad=_profundidad + 1)


def evaluar_expr(expr, fila: dict, limites: LimitesAlgebra | None = None, *,
                 registro: Mapping[str, Callable[..., Any]] | None = None):
    """Un literal es un literal; el acceso a datos es SIEMPRE explícito.

    Se eligió `["campo", alias, nombre]` en vez de la forma corta `"a.x"` (y en vez de dejar que un
    string suelto signifique un alias) porque si no, un valor de texto que coincida con un alias
    cambiaría de significado según el contexto. Es más verboso y no tiene casos raros.
    """
    escalares = _registro(registro)
    validar_expr(expr, limites, registro=escalares)
    return _evaluar_expr(expr, fila, escalares)


def _evaluar_expr(expr, fila: dict, escalares: Mapping[str, Callable[..., Any]]):
    if not isinstance(expr, list):
        return expr                                   # número, bool, string, None

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
        a, b = (_evaluar_expr(x, fila, escalares) for x in resto)
        if a is None or b is None:
            # comparar contra un campo ausente es casi siempre un error de la medida, no un False
            raise ErrorDeAlgebra(f"«{cabeza}» sobre un valor ausente: {expr}")
        return comparar(cabeza, a, b)
    if cabeza in ("y", "o"):
        # SIN cortocircuito, y es deliberado. `all`/`any` sobre un generador dejan de evaluar apenas
        # el resultado está decidido, y eso tapaba exactamente el error que el `raise` de arriba
        # existe para levantar: `["y", <falso>, ["==", ["campo","a","typo"], 1]]` no llegaba nunca a
        # mirar el campo inexistente y devolvía un `False` silencioso — el verde que §3 de la
        # especificación prohíbe. Peor todavía, dependía de los datos: la misma medida rota
        # levantaba el error con una evidencia y lo escondía con otra.
        #
        # Se paga evaluando de más en predicados grandes. El presupuesto de §9 ya acota esa
        # amplificación, y una medida que se apoya en el cortocircuito para no romperse está rota.
        valores = [_evaluar_expr(x, fila, escalares) for x in resto]
        return all(valores) if cabeza == "y" else any(valores)
    if cabeza == "no":
        (x,) = resto
        return not _evaluar_expr(x, fila, escalares)

    if cabeza in escalares:
        return escalares[cabeza](*(_evaluar_expr(x, fila, escalares) for x in resto))

    raise ErrorDeAlgebra(f"«{cabeza}» no es accesor, comparador, lógico ni escalar declarada")


# ---- agregados --------------------------------------------------------------------

AGREGADOS: dict[str, Callable[[list], Any]] = {
    "contar": len,
    "max": max,
    "min": min,
    "suma": sum,
    "promedio": lambda xs: sum(xs) / len(xs),
}


def _agregar(agregado: str, valores: list):
    """Agrega valores comprobando dominio, compatibilidad y finitud antes y después."""
    if not valores:
        return 0

    for valor in valores:
        validar_finito(valor, f"un valor de «{agregado}»")

    familias = {_familia_escalar(valor) for valor in valores}
    if agregado in ("suma", "promedio"):
        if not familias <= {"numero", "booleano"}:
            raise ErrorDeAlgebra(
                f"«{agregado}» sólo acepta números o indicadores booleanos, no {sorted(familias)}")
    elif len(familias) != 1:
        raise ErrorDeAlgebra(
            f"«{agregado}» recibió tipos incompatibles: {sorted(familias)}")
    elif next(iter(familias)) not in {"numero", "booleano", "texto"}:
        raise ErrorDeAlgebra(
            f"«{agregado}» sólo acepta escalares comparables, no {sorted(familias)}")

    try:
        resultado = AGREGADOS[agregado](valores)
    except (TypeError, ValueError, OverflowError) as e:
        raise ErrorDeAlgebra(f"«{agregado}» no puede agregar esos valores: {e}") from e
    validar_finito(resultado, f"el resultado de «{agregado}»")
    return resultado


# ---- operadores -------------------------------------------------------------------

FUENTES = ("de", "unir")


def _de(evidencia: dict, relacion: str, alias: str, limites: LimitesAlgebra) -> list[dict]:
    if relacion not in evidencia:
        raise ErrorDeAlgebra(
            f"la relación «{relacion}» no existe en la evidencia; "
            "una relación vacía se declara explícitamente como []")
    hechos = evidencia[relacion]
    if not isinstance(hechos, list):
        raise ErrorDeAlgebra(
            f"la relación «{relacion}» debe ser una lista de hechos, no {type(hechos).__name__}")
    if len(hechos) > limites.filas_por_relacion:
        raise ErrorDeAlgebra(
            f"la relación «{relacion}» tiene {len(hechos)} filas y supera el límite "
            f"de {limites.filas_por_relacion}")
    if not all(isinstance(hecho, dict) for hecho in hechos):
        raise ErrorDeAlgebra(f"la relación «{relacion}» contiene una fila que no es un hecho")
    return [{alias: dict(hecho)} for hecho in hechos]


def _unir(paso, evidencia: dict, limites: LimitesAlgebra,
          registro: Mapping[str, Callable[..., Any]]) -> list[dict]:
    """`["unir", izq, der]` → producto. Los alias de ambos lados conviven en la fila."""
    izq, der = paso[1], paso[2]
    for lado in (izq, der):
        if lado[0] not in FUENTES:
            raise ErrorDeAlgebra(f"«unir» toma fuentes, y recibió «{lado[0]}»")

    filas_izq = aplicar(izq, [], evidencia, limites, registro=registro)
    filas_der = aplicar(der, [], evidencia, limites, registro=registro)
    tamano = len(filas_izq) * len(filas_der)
    if tamano > limites.producto_cartesiano:
        raise ErrorDeAlgebra(
            f"el producto cartesiano produciría {tamano} filas y supera el límite "
            f"de {limites.producto_cartesiano}")
    salida = []
    for a in filas_izq:
        for b in filas_der:
            comunes = set(a) & set(b)
            if comunes:
                raise ErrorDeAlgebra(f"«unir» con alias repetido: {sorted(comunes)}")
            salida.append({**a, **b})
    return salida


def _agrupar(paso, filas: list[dict], limites: LimitesAlgebra,
             registro: Mapping[str, Callable[..., Any]]) -> list[dict]:
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
        k = tuple(evaluar_expr(expr, f, limites, registro=registro)
                  for _nombre, expr in claves)
        grupos.setdefault(k, []).append(f)

    salida = []
    for k, miembros in grupos.items():
        derivadas = {nombre: valor for (nombre, _expr), valor in zip(claves, k)}
        for nombre, agg, expr in agregados:
            if agg not in AGREGADOS:
                raise ErrorDeAlgebra(f"agregado desconocido: «{agg}»")
            derivadas[nombre] = (len(miembros) if agg == "contar" else
                                 _agregar(agg, [evaluar_expr(
                                     expr, m, limites, registro=registro) for m in miembros]))
        salida.append({ALIAS_DERIVADO: derivadas})
    return salida


def aplicar(paso, filas: list[dict], evidencia: dict,
            limites: LimitesAlgebra | None = None, *,
            registro: Mapping[str, Callable[..., Any]] | None = None) -> list[dict]:
    limites = _limites(limites)
    escalares = _registro(registro)
    op = paso[0]
    if op == "de":
        relacion, alias = paso[1], paso[2]
        return _de(evidencia, relacion, alias, limites)
    if op == "unir":
        return _unir(paso, evidencia, limites, escalares)
    if op == "donde":
        return [f for f in filas if evaluar_expr(
            paso[1], f, limites, registro=escalares)]
    if op == "agrupar":
        return _agrupar(paso, filas, limites, escalares)
    raise ErrorDeAlgebra(f"operador desconocido: «{op}»")


def _validar_fuente(fuente, limites: LimitesAlgebra | None = None) -> None:
    if not isinstance(fuente, list) or not fuente:
        raise ErrorDeAlgebra("una fuente tiene que ser una lista no vacía")

    op = fuente[0]
    _validar_nombre(op, "el operador de una fuente")
    if op == "de":
        if len(fuente) != 3:
            raise ErrorDeAlgebra("«de» va ['de', relacion, alias]")
        _validar_nombre(fuente[1], "el nombre de la relación")
        _validar_nombre(fuente[2], "el alias de «de»")
        return
    if op == "unir":
        if len(fuente) != 3:
            raise ErrorDeAlgebra("«unir» va ['unir', fuente_izq, fuente_der]")
        _validar_fuente(fuente[1], limites)
        _validar_fuente(fuente[2], limites)
        return
    raise ErrorDeAlgebra(f"fuente desconocida: «{op}» (hay {FUENTES})")


def _validar_paso(paso, limites: LimitesAlgebra | None = None, *,
                  registro: Mapping[str, Callable[..., Any]] | None = None) -> None:
    if not isinstance(paso, list) or not paso:
        raise ErrorDeAlgebra("cada paso de una tubería tiene que ser una lista no vacía")

    op = paso[0]
    _validar_nombre(op, "el operador de un paso")
    if op == "donde":
        if len(paso) != 2:
            raise ErrorDeAlgebra("«donde» va ['donde', predicado]")
        validar_expr(paso[1], limites, registro=registro)
        return
    if op == "agrupar":
        if len(paso) != 3:
            raise ErrorDeAlgebra("«agrupar» va ['agrupar', claves, agregados]")
        claves, agregados = paso[1], paso[2]
        if not isinstance(claves, list) or not all(
                isinstance(clave, list) and len(clave) == 2 for clave in claves):
            raise ErrorDeAlgebra(
                "las claves de «agrupar» van [[nombre, expresion], ...]")
        if not isinstance(agregados, list) or not all(
                isinstance(agg, list) and len(agg) == 3 for agg in agregados):
            raise ErrorDeAlgebra(
                "los agregados de «agrupar» van [[nombre, agregado, expresion], ...]")
        for nombre, expr in claves:
            _validar_nombre(nombre, "el nombre de una clave de «agrupar»")
            validar_expr(expr, limites, registro=registro)
        for nombre, agg, expr in agregados:
            _validar_nombre(nombre, "el nombre de un agregado de «agrupar»")
            _validar_nombre(agg, "el operador agregado de «agrupar»")
            if agg not in AGREGADOS:
                raise ErrorDeAlgebra(
                    f"agregado desconocido: {agg!r} (hay {sorted(AGREGADOS)})")
            validar_expr(expr, limites, registro=registro)
        return
    if op in FUENTES:
        raise ErrorDeAlgebra(f"«{op}» es una fuente y sólo puede ser el primer paso")
    raise ErrorDeAlgebra(f"operador desconocido: «{op}»")


def validar_tuberia(tuberia, limites: LimitesAlgebra | None = None, *,
                    registro: Mapping[str, Callable[..., Any]] | None = None) -> None:
    """Valida recursivamente la estructura declarada, sin mirar evidencia ni calcular valores."""
    if not isinstance(tuberia, list) or not tuberia or tuberia[0] != "desde":
        raise ErrorDeAlgebra("una tubería empieza con «desde»")
    if len(tuberia) < 2:
        raise ErrorDeAlgebra("una tubería «desde» necesita una fuente")
    _validar_fuente(tuberia[1], limites)
    for paso in tuberia[2:]:
        _validar_paso(paso, limites, registro=registro)


def validar_resumen(resumen, limites: LimitesAlgebra | None = None, *,
                    registro: Mapping[str, Callable[..., Any]] | None = None) -> None:
    """Valida la forma `['resumen', agregado, expresion]`."""
    if not isinstance(resumen, list) or len(resumen) != 3 or resumen[0] != "resumen":
        raise ErrorDeAlgebra("un resumen va ['resumen', agregado, expresion]")
    _validar_nombre(resumen[1], "el operador de un resumen")
    if resumen[1] not in AGREGADOS:
        raise ErrorDeAlgebra(
            f"agregado desconocido: «{resumen[1]}» (hay {sorted(AGREGADOS)})")
    validar_expr(resumen[2], limites, registro=registro)


def desde(tuberia, evidencia: dict, limites: LimitesAlgebra | None = None, *,
          registro: Mapping[str, Callable[..., Any]] | None = None) -> list[dict]:
    """`["desde", fuente, paso, paso, …]` → las filas que sobrevivieron. **Son los testigos.**"""
    limites = _limites(limites)
    escalares = _registro(registro)
    validar_tuberia(tuberia, limites, registro=escalares)
    filas: list[dict] = []
    for paso in tuberia[1:]:
        filas = aplicar(paso, filas, evidencia, limites, registro=escalares)
    return filas


def resumir(resumen, filas: list[dict], limites: LimitesAlgebra | None = None, *,
            registro: Mapping[str, Callable[..., Any]] | None = None):
    """`["resumen", agg, expr]` → el escalar. `contar` no evalúa la expresión: cuenta filas."""
    limites = _limites(limites)
    escalares = _registro(registro)
    validar_resumen(resumen, limites, registro=escalares)
    _, agg, expr = resumen
    if agg == "contar":
        return len(filas)
    return _agregar(agg, [evaluar_expr(
        expr, f, limites, registro=escalares) for f in filas])
