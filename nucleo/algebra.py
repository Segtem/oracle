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

    def __init__(self, mensaje: object = "", *, ruta: tuple[int, ...] | str | None = None):
        super().__init__(mensaje)
        self._ruta = _normalizar_ruta(ruta)

    @property
    def ruta(self) -> str | None:
        if self._ruta is None:
            return None
        return _texto_ruta(self._ruta)

    @property
    def ruta_indices(self) -> tuple[int, ...] | None:
        return self._ruta

    def con_ruta_actual(self) -> "ErrorDeAlgebra":
        if self._ruta is None:
            self._ruta = ()
        return self

    def prefijar_ruta(self, prefijo: tuple[int, ...] | str | None) -> "ErrorDeAlgebra":
        indices = _normalizar_ruta(prefijo)
        if indices is None:
            return self
        self._ruta = indices if self._ruta is None else (*indices, *self._ruta)
        return self

    def descartar_ruta(self) -> "ErrorDeAlgebra":
        self._ruta = None
        return self

    def __str__(self) -> str:
        texto = super().__str__()
        if self._ruta is None:
            return texto
        ruta = _texto_ruta(self._ruta)
        return f"{texto} en `{ruta}`" if ruta else f"{texto} en la raíz"


def _normalizar_ruta(ruta: tuple[int, ...] | str | None) -> tuple[int, ...] | None:
    if ruta is None:
        return None
    if isinstance(ruta, str):
        if ruta == "":
            return ()
        partes: tuple[object, ...] = tuple(ruta.split("."))
    else:
        partes = tuple(ruta)
    salida = []
    for parte in partes:
        if isinstance(parte, bool):
            raise ValueError(f"ruta inválida: {ruta!r}")
        try:
            indice = int(parte)
        except (TypeError, ValueError) as e:
            raise ValueError(f"ruta inválida: {ruta!r}") from e
        if indice < 0:
            raise ValueError(f"ruta inválida: {ruta!r}")
        salida.append(indice)
    return tuple(salida)


def _texto_ruta(ruta: tuple[int, ...]) -> str:
    return ".".join(str(indice) for indice in ruta)


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


def escalar(
    nombre: str,
    unidad: str = "",
    *,
    unidades_argumentos: tuple[str, ...] = (),
    registro: RegistroEscalares | None = None,
):
    """Registra una función de dominio. Se DECLARA para que aparezca en el inventario: una función
    importada a mano no se puede contar ni discutir, igual que un umbral escondido en una firma."""
    if not isinstance(nombre, str) or NOMBRE_ESCALAR_RE.fullmatch(nombre) is None:
        raise ErrorDeAlgebra(
            "el nombre de una escalar usa minúsculas ASCII, dígitos y `_`, sin puntos")
    if not isinstance(unidad, str) or "\n" in unidad or "\r" in unidad:
        raise ErrorDeAlgebra("la unidad de una escalar debe ser texto de una línea")
    if not isinstance(unidades_argumentos, tuple):
        raise ErrorDeAlgebra("las unidades de los argumentos deben ser una tupla")
    if any(
        not isinstance(unidad_argumento, str)
        or not unidad_argumento.strip()
        or "\n" in unidad_argumento
        or "\r" in unidad_argumento
        for unidad_argumento in unidades_argumentos
    ):
        raise ErrorDeAlgebra(
            "cada unidad de argumento debe ser texto no vacío de una línea; "
            "usá `sin_unidad` cuando corresponda"
        )
    unidades_normalizadas = tuple(u.strip() for u in unidades_argumentos)

    def envolver(fn):
        destino = _registro(registro)
        if nombre in destino:
            raise ErrorDeAlgebra(f"la escalar «{nombre}» ya está registrada")
        aridad_min, aridad_max = _contrato_de_escalar(fn)
        if unidades_normalizadas and aridad_max is None:
            raise ErrorDeAlgebra(
                "una escalar variádica no puede declarar unidades posicionales"
            )
        if unidades_normalizadas and len(unidades_normalizadas) != aridad_max:
            raise ErrorDeAlgebra(
                f"la escalar declara {len(unidades_normalizadas)} unidad(es) para "
                f"{aridad_max} argumento(s) posicionales"
            )
        fn.nombre_escalar = nombre
        fn.unidad = unidad
        fn.unidades_argumentos = unidades_normalizadas
        fn.aridad_min = aridad_min
        fn.aridad_max = aridad_max
        fn.procedencia_escalar = _PROCEDENCIA_ACTIVA.get() or _PROCEDENCIA_ESCALAR
        destino[nombre] = fn
        return fn
    return envolver


# ---- traza de la evaluación (el evaluador como sensor de sí mismo) ----------------
#
# El álgebra no puede evaluarse a sí misma: recorrer un AST es recursión, y la recursión salió del
# álgebra a propósito (§8). Pero SÍ puede juzgarse ejecutándose, que es la doctrina de este proyecto
# aplicada al evaluador: el sensor produce hechos y el álgebra los mide.
#
# Con esto, las propiedades que valen sin importar la implementación —«`donde` nunca agrega filas»,
# «`unir` materializa exactamente el producto»— dejan de ser tests en Python y pasan a ser MEDIDAS:
# entran a la mutación, al corpus y al inventario de puntos ciegos como cualquier otra.
#
# Apagada por omisión y sin costo cuando lo está: una lectura de ContextVar por paso.

_TRAZA_ACTIVA: ContextVar[list | None] = ContextVar("oracle_traza", default=None)


@contextmanager
def trazar(destino: list | None = None):
    """Recolecta los hechos de la evaluación mientras dure el bloque.

    Es un contexto y no un global porque dos consumidores pueden medir a la vez sin pisarse, igual
    que el registro de escalares.
    """
    destino = [] if destino is None else destino
    token = _TRAZA_ACTIVA.set(destino)
    try:
        yield destino
    finally:
        _TRAZA_ACTIVA.reset(token)


def _anotar(clase: str, **campos) -> None:
    destino = _TRAZA_ACTIVA.get()
    if destino is None:
        return
    destino.append((clase, campos))


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
                 registro: Mapping[str, Callable[..., Any]] | None = None,
                 ruta: tuple[int, ...] | str | None = None):
    """Un literal es un literal; el acceso a datos es SIEMPRE explícito.

    Se eligió `["campo", alias, nombre]` en vez de la forma corta `"a.x"` (y en vez de dejar que un
    string suelto signifique un alias) porque si no, un valor de texto que coincida con un alias
    cambiaría de significado según el contexto. Es más verboso y no tiene casos raros.
    """
    escalares = _registro(registro)
    try:
        validar_expr(expr, limites, registro=escalares)
        return _evaluar_expr(expr, fila, escalares)
    except ErrorDeAlgebra as e:
        if ruta is None:
            e.descartar_ruta()
        else:
            e.con_ruta_actual().prefijar_ruta(ruta)
        raise


def _evaluar_hijo(expr: list, indice: int, fila: dict,
                  escalares: Mapping[str, Callable[..., Any]]):
    try:
        return _evaluar_expr(expr[indice], fila, escalares)
    except ErrorDeAlgebra as e:
        e.con_ruta_actual().prefijar_ruta((indice,))
        raise


def _evaluar_expr(expr, fila: dict, escalares: Mapping[str, Callable[..., Any]]):
    if not isinstance(expr, list):
        return expr                                   # número, bool, string, None

    cabeza, resto = expr[0], expr[1:]

    if cabeza == "campo":
        alias, nombre = resto
        if alias not in fila:
            raise ErrorDeAlgebra(f"el alias «{alias}» no existe en la fila", ruta=())
        return fila[alias].get(nombre)
    if cabeza == "hecho":
        (alias,) = resto
        if alias not in fila:
            raise ErrorDeAlgebra(f"el alias «{alias}» no existe en la fila", ruta=())
        return fila[alias]
    if cabeza == "col":
        (nombre,) = resto
        return fila.get(ALIAS_DERIVADO, {}).get(nombre)

    if cabeza in COMPARADORES:
        a = _evaluar_hijo(expr, 1, fila, escalares)
        b = _evaluar_hijo(expr, 2, fila, escalares)
        if a is None or b is None:
            # comparar contra un campo ausente es casi siempre un error de la medida, no un False
            raise ErrorDeAlgebra(f"«{cabeza}» sobre un valor ausente: {expr}", ruta=())
        try:
            return comparar(cabeza, a, b)
        except ErrorDeAlgebra as e:
            e.con_ruta_actual()
            raise
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
        valores = []
        for indice in range(1, len(expr)):
            valores.append(_evaluar_hijo(expr, indice, fila, escalares))
        # `declarados` sale del AST y `evaluados` de haber pasado por el bucle: si alguien vuelve a
        # cortocircuitar, los dos números dejan de coincidir y hay una medida que lo dice.
        _anotar("nodo", cabeza=cabeza, declarados=len(resto), evaluados=len(valores))
        return all(valores) if cabeza == "y" else any(valores)
    if cabeza == "no":
        return not _evaluar_hijo(expr, 1, fila, escalares)

    if cabeza in escalares:
        argumentos = [_evaluar_hijo(expr, indice, fila, escalares)
                      for indice in range(1, len(expr))]
        try:
            return escalares[cabeza](*argumentos)
        except ErrorDeAlgebra as e:
            e.con_ruta_actual()
            raise
        except Exception as e:
            # Una escalar que revienta con una excepción de Python cruda ATRAVESABA el álgebra. El
            # camino AISLADO ya la envolvía —«falló la escalar externa …»— y el que corre en proceso
            # no, así que el mismo defecto se veía como un error del dominio o como un `TypeError`
            # pelado según por dónde entrara. Un `TypeError` que sale del evaluador no le dice a
            # nadie si el álgebra rechazó algo o si algo explotó, y `mutar.py` no lo podía atajar:
            # terminaba la ronda en un traceback.
            #
            # Lo encontró una corrida sobre un catálogo ajeno: una medida le pasaba a una escalar un
            # campo que podía venir `null`, y como los lógicos ya no cortocircuitan —§3— la llamada
            # ocurre siempre. Que el dato sea malo es problema de quien escribió esa medida; que el
            # error saliera crudo era problema de acá.
            raise ErrorDeAlgebra(
                f"la escalar «{cabeza}» falló sobre {argumentos!r}: "
                f"{type(e).__name__}: {e}").con_ruta_actual() from e

    raise ErrorDeAlgebra(
        f"«{cabeza}» no es accesor, comparador, lógico ni escalar declarada", ruta=())


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


# ---- claves de unicidad -----------------------------------------------------------
#
# Una relación es una bolsa (§1): la multiplicidad es evidencia y Oracle no la deduce. Pero un
# dominio que SÍ conoce su identidad puede declararla como clave de unicidad, y entonces un duplicado
# deja de ser un hecho más para ser un defecto del sensor. La clave es un nodo opcional a la cabeza
# de la lista de hechos —`["clave", [<campo>, …]]`—; sin él, la relación es exactamente la bolsa de
# siempre y no cambia nada.

CLAVE = "clave"


def separar_clave(hechos: list) -> tuple[tuple[str, ...], list]:
    """Separa la declaración opcional de clave de las filas, validándola fail-closed.

    Devuelve `(clave, filas)`: `clave` es la tupla de campos declarados (vacía si la relación no
    declara nada) y `filas` son los hechos. Un nodo `clave` mal formado levanta, no se ignora: un
    contrato de identidad que se lee mal se leería como ausencia de contrato, y eso es exactamente
    el falso verde que la clave existe para cerrar.
    """
    if not hechos or not isinstance(hechos[0], list) or not hechos[0] or hechos[0][0] != CLAVE:
        return (), hechos
    nodo = hechos[0]
    if len(nodo) != 2 or not isinstance(nodo[1], list) or not nodo[1]:
        raise ErrorDeAlgebra(
            f"«{CLAVE}» va ['{CLAVE}', [<campo>, …]] con al menos un campo, no {nodo!r}")
    campos = nodo[1]
    if any(not isinstance(c, str) or not c.strip() for c in campos):
        raise ErrorDeAlgebra(
            f"la clave de unicidad lista campos de texto no vacíos, no {campos!r}")
    if len(set(campos)) != len(campos):
        raise ErrorDeAlgebra(f"la clave de unicidad repite un campo: {campos}")
    return tuple(campos), hechos[1:]


def validar_unicidad(relacion: str, clave: tuple[str, ...], filas: list) -> None:
    """Fail-closed: un duplicado bajo la clave declarada es un defecto del sensor, no un hecho más.

    El mensaje nombra la clave responsable y la fila que la viola, para que el sensor pueda corregir
    su producción sin adivinar qué relación ni qué campo. Un campo de la clave ausente también
    levanta: una identidad a medias no se puede comprobar, y un nulo implícito la dejaría sin
    comprobar en silencio.
    """
    vistos: dict = {}
    for i, hecho in enumerate(filas):
        ausentes = [campo for campo in clave if campo not in hecho]
        if ausentes:
            raise ErrorDeAlgebra(
                f"la relación «{relacion}» declara la clave ({', '.join(clave)}) y la fila {i} "
                f"no trae el campo {', '.join(ausentes)}")
        valores = tuple(hecho[campo] for campo in clave)
        try:
            hash(valores)
        except TypeError:
            raise ErrorDeAlgebra(
                f"la relación «{relacion}» declara la clave ({', '.join(clave)}) y la fila {i} "
                f"no la trae como escalar")
        if valores in vistos:
            raise ErrorDeAlgebra(
                f"la relación «{relacion}» declara la clave ({', '.join(clave)}) y la fila {i} "
                f"la repite: ya la traía la fila {vistos[valores]} — {hecho}")
        vistos[valores] = i


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
    clave, filas = separar_clave(hechos)
    if len(filas) > limites.filas_por_relacion:
        raise ErrorDeAlgebra(
            f"la relación «{relacion}» tiene {len(filas)} filas y supera el límite "
            f"de {limites.filas_por_relacion}")
    if not all(isinstance(hecho, dict) for hecho in filas):
        raise ErrorDeAlgebra(f"la relación «{relacion}» contiene una fila que no es un hecho")
    if clave:
        validar_unicidad(relacion, clave, filas)
    return [{alias: dict(hecho)} for hecho in filas]


def _unir(paso, evidencia: dict, limites: LimitesAlgebra,
          registro: Mapping[str, Callable[..., Any]], _lados: dict | None = None, *,
          ruta: tuple[int, ...] | None = None) -> list[dict]:
    """`["unir", izq, der]` → producto. Los alias de ambos lados conviven en la fila.

    `_lados` es la única concesión a la traza: deja los tamaños de cada lado para que quien llama
    anote el hecho **con lo que este operador realmente devolvió**. La primera versión anotaba acá
    adentro, leyendo `salida` antes del `return`, y así no medía nada: cualquier defecto entre esa
    línea y el punto de uso quedaba fuera. Un sensor que se lee a sí mismo no audita la frontera.
    """
    izq, der = paso[1], paso[2]
    for lado in (izq, der):
        if lado[0] not in FUENTES:
            raise ErrorDeAlgebra(f"«unir» toma fuentes, y recibió «{lado[0]}»")

    ruta_izq = (*ruta, 1) if ruta is not None else None
    ruta_der = (*ruta, 2) if ruta is not None else None
    filas_izq = aplicar(izq, [], evidencia, limites, registro=registro, ruta=ruta_izq)
    filas_der = aplicar(der, [], evidencia, limites, registro=registro, ruta=ruta_der)
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
    if _lados is not None:
        _lados["izquierda"], _lados["derecha"] = len(filas_izq), len(filas_der)
    return salida


def _agrupar(paso, filas: list[dict], limites: LimitesAlgebra,
             registro: Mapping[str, Callable[..., Any]], *,
             ruta: tuple[int, ...] | None = None) -> list[dict]:
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
    rutas_clave = [(*ruta, 1, posicion, 1) for posicion in range(len(claves))] if (
        ruta is not None) else [None] * len(claves)
    rutas_agregado = [(*ruta, 2, posicion, 2) for posicion in range(len(agregados))] if (
        ruta is not None) else [None] * len(agregados)
    grupos: dict[tuple, list[dict]] = {}
    for f in filas:
        valores_clave = []
        for ruta_expr, (_nombre, expr) in zip(rutas_clave, claves):
            valores_clave.append(evaluar_expr(
                expr, f, limites, registro=registro, ruta=ruta_expr))
        k = tuple(valores_clave)
        grupos.setdefault(k, []).append(f)

    salida = []
    for k, miembros in grupos.items():
        derivadas = {nombre: valor for (nombre, _expr), valor in zip(claves, k)}
        for ruta_expr, (nombre, agg, expr) in zip(rutas_agregado, agregados):
            if agg not in AGREGADOS:
                raise ErrorDeAlgebra(f"agregado desconocido: «{agg}»")
            derivadas[nombre] = (len(miembros) if agg == "contar" else
                                 _agregar(agg, [evaluar_expr(
                                     expr, m, limites, registro=registro, ruta=ruta_expr)
                                     for m in miembros]))
        salida.append({ALIAS_DERIVADO: derivadas})
    return salida


def aplicar(paso, filas: list[dict], evidencia: dict,
            limites: LimitesAlgebra | None = None, *,
            registro: Mapping[str, Callable[..., Any]] | None = None,
            ruta: tuple[int, ...] | None = None) -> list[dict]:
    limites = _limites(limites)
    escalares = _registro(registro)
    op = paso[0]
    if op == "de":
        relacion, alias = paso[1], paso[2]
        # La ruta se le pega al error del `de`, y NO estaba. `_unir` calculaba `ruta_izq` y
        # `ruta_der` con esmero y las pasaba acá, donde se descartaban: un error en cualquiera de
        # los dos lados de un `unir` salía SIN ruta, así que `fragmento_de_error` no podía señalar
        # nada sobre la superficie. El mapa de fuente tenía un agujero del tamaño de `unir`.
        #
        # Lo denunció la mutación de código: cuatro mutantes de `ruta_izq`/`ruta_der` sobrevivían
        # —incluido cambiar el índice 1 por el 2— porque el valor calculado no llegaba a ninguna
        # parte. Un mutante que no se puede matar porque su resultado no se usa no es equivalente:
        # es código que quería hacer algo y no lo hacía.
        try:
            return _de(evidencia, relacion, alias, limites)
        except ErrorDeAlgebra as e:
            raise e.prefijar_ruta(ruta) if ruta is not None else e
    if op == "unir":
        # El hecho se anota con lo que el operador DEVOLVIÓ, no con lo que creyó construir.
        lados: dict = {}
        filas_unidas = _unir(paso, evidencia, limites, escalares, lados, ruta=ruta)
        _anotar("producto", izquierda=lados["izquierda"], derecha=lados["derecha"],
                salida=len(filas_unidas))
        return filas_unidas
    if op == "donde":
        ruta_expr = (*ruta, 1) if ruta is not None else None
        return [f for f in filas if evaluar_expr(
            paso[1], f, limites, registro=escalares, ruta=ruta_expr)]
    if op == "agrupar":
        return _agrupar(paso, filas, limites, escalares, ruta=ruta)
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
    for t, paso in enumerate(tuberia[1:]):
        antes = len(filas)
        filas = aplicar(paso, filas, evidencia, limites, registro=escalares, ruta=(2, t + 1))
        _anotar("paso", t=t, operador=paso[0], filas_antes=antes, filas_despues=len(filas))
    return filas


def resumir(resumen, filas: list[dict], limites: LimitesAlgebra | None = None, *,
            registro: Mapping[str, Callable[..., Any]] | None = None,
            ruta: tuple[int, ...] | None = (3,)):
    """`["resumen", agg, expr]` → el escalar. `contar` no evalúa la expresión: cuenta filas."""
    limites = _limites(limites)
    escalares = _registro(registro)
    validar_resumen(resumen, limites, registro=escalares)
    _, agg, expr = resumen
    if agg == "contar":
        return len(filas)
    ruta_expr = (*ruta, 2) if ruta is not None else None
    return _agregar(agg, [evaluar_expr(
        expr, f, limites, registro=escalares, ruta=ruta_expr) for f in filas])
