"""Superficie infija de autoría para medidas.

El lector devuelve la misma forma de almacenamiento que recibió el impresor, incluidas las
invocaciones de macro que ya viven en el catálogo.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .proyecto import ID_MEDIDA_RE
from .version import VersionInvalida, parsear

COMPARADORES = ("==", "!=", "<=", ">=", "<", ">")
LOGICOS = {"y": 2, "o": 1}
PALABRAS_LITERAL = {"true": True, "false": False, "null": None}
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
DEFMACRO_RE = re.compile(r"defmacro\s+([^\s(]+)\s*\(([^)]*)\)\s*:")
NUMERO_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
IND = "    "
IND2 = IND * 2

# Un archivo `.oracle` puede declarar, como PRIMERA línea, contra qué versión de la superficie se
# escribió: `sintaxis MAYOR.MENOR`. Es parte de la superficie —se lee y se valida— y no un comentario
# pegado arriba; por eso vive en la gramática y no en el filtro de `#`. Es OPCIONAL: quien no la
# declara sigue cargando, y los 34 archivos de hoy no la declaran.
VERSION_LINE_RE = re.compile(r"^sintaxis\s+(\S+)$")


# Los atributos que el intérprete y las herramientas de traza escriben sobre CUALQUIER excepción.
# Un `dataclass(frozen=True)` reemplaza `__setattr__` por uno que rechaza todo, y eso alcanza a
# éstos: `e.__traceback__ = tb` levanta `FrozenInstanceError`. CPython los escribe por la API de C
# al levantar la excepción —por eso un `raise` simple anda— pero cualquier código Python que
# re-lance, encadene o COPIE el error se estrella.
#
# La mutación de código lo descubrió: 51 de 193 mutantes de `nucleo/caso.py` no salieron ni muertos
# ni vivos, salieron **error de arnés**, con `FrozenInstanceError: cannot assign to field
# '__traceback__'` durante el descubrimiento de tests. Un error del arnés no es una muerte —caso
# `017` del corpus—, así que la ronda entera quedaba inconclusa y esos 51 mutantes no medían nada.
#
# La inmutabilidad que se quiere es la de los CAMPOS del error —línea, columna, qué se esperaba—,
# no la de la maquinaria de excepciones de Python.
_ATRIBUTOS_DE_EXCEPCION = ("__traceback__", "__cause__", "__context__", "__suppress_context__",
                           "__notes__")


@dataclass(frozen=True)
class ErrorSintaxis(ValueError):
    linea: int
    columna: int
    esperado: str
    encontrado: str = ""
    # No todo error de sintaxis es «se esperaba X». Un parámetro que la plantilla nunca usa no es
    # algo que faltó en una posición: es una afirmación sobre la macro entera. Forzar la plantilla
    # producía «se esperaba parámetro «sobra» que la plantilla nunca usa», que se lee al revés de
    # lo que pasó. Un error que hay que descifrar es un error que no sirve.
    literal: bool = False

    def __str__(self) -> str:
        visto = f"; llegó {self.encontrado}" if self.encontrado else ""
        cabeza = self.esperado if self.literal else f"se esperaba {self.esperado}"
        return f"línea {self.linea}, columna {self.columna}: {cabeza}{visto}"


def _permitir_atributos_de_excepcion(clase):
    """Deja pasar los dunder de excepción por el `__setattr__` congelado del dataclass.

    Se aplica DESPUÉS de la clase porque `dataclass(frozen=True)` se niega a que se declare un
    `__setattr__` propio adentro (`TypeError: Cannot overwrite attribute __setattr__`).
    """
    congelado = clase.__setattr__

    def asignar(self, nombre, valor):
        if nombre in _ATRIBUTOS_DE_EXCEPCION:
            object.__setattr__(self, nombre, valor)
            return
        congelado(self, nombre, valor)

    clase.__setattr__ = asignar
    return clase


_permitir_atributos_de_excepcion(ErrorSintaxis)


@dataclass(frozen=True)
class Token:
    tipo: str
    valor: object
    linea: int
    columna: int


@dataclass(frozen=True)
class Ubicacion:
    linea: int
    columna: int


@dataclass(frozen=True)
class Lectura:
    datos: list
    ubicaciones: dict[str, Ubicacion]
    version: str | None = None

    def ubicacion(self, ruta: tuple[int, ...] | str) -> Ubicacion | None:
        return self.ubicaciones.get(_texto_ruta(_normalizar_ruta(ruta)))


@dataclass(frozen=True)
class _Nodo:
    valor: object
    linea: int
    columna: int
    hijos: tuple["_Nodo", ...] = ()


def _fallar(linea: int, columna: int, esperado: str, encontrado: object = "", *,
            literal: bool = False) -> None:
    raise ErrorSintaxis(linea, columna, esperado,
                        repr(encontrado) if encontrado != "" else "", literal)


def _normalizar_ruta(ruta: tuple[int, ...] | str) -> tuple[int, ...]:
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


def _hoja(valor: object, token: Token) -> _Nodo:
    return _Nodo(valor, token.linea, token.columna)


def _lista(cabeza: str, token: Token, hijos: list[_Nodo]) -> _Nodo:
    cabeza_nodo = _Nodo(cabeza, token.linea, token.columna)
    return _Nodo([cabeza, *(h.valor for h in hijos)], token.linea, token.columna,
                 (cabeza_nodo, *hijos))


def _volcar_mapa(nodo: _Nodo, ruta: tuple[int, ...],
                 ubicaciones: dict[str, Ubicacion]) -> None:
    ubicaciones[_texto_ruta(ruta)] = Ubicacion(nodo.linea, nodo.columna)
    for indice, hijo in enumerate(nodo.hijos):
        _volcar_mapa(hijo, (*ruta, indice), ubicaciones)


def _registrar(ubicaciones: dict[str, Ubicacion] | None, ruta: tuple[int, ...],
               linea: int, columna: int) -> None:
    if ubicaciones is not None:
        ubicaciones[_texto_ruta(ruta)] = Ubicacion(linea, columna)


def _registrar_nodo(ubicaciones: dict[str, Ubicacion] | None, ruta: tuple[int, ...],
                    nodo: _Nodo) -> None:
    if ubicaciones is not None:
        _volcar_mapa(nodo, ruta, ubicaciones)


def _tokenizar(texto: str, linea: int, columna_base: int) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    while i < len(texto):
        c = texto[i]
        col = columna_base + i
        if c.isspace():
            i += 1
            continue
        if c == '"':
            try:
                valor, fin = json.JSONDecoder().raw_decode(texto[i:])
            except json.JSONDecodeError as e:
                _fallar(linea, col + e.pos, "texto JSON válido", texto[i:])
            if not isinstance(valor, str):
                _fallar(linea, col, "texto JSON", valor)
            tokens.append(Token("STRING", valor, linea, col))
            i += fin
            continue
        if texto.startswith(("==", "!=", "<=", ">="), i):
            tokens.append(Token("OP", texto[i:i + 2], linea, col))
            i += 2
            continue
        if c in "<>":
            tokens.append(Token("OP", c, linea, col))
            i += 1
            continue
        if c in "(),.":
            tokens.append(Token(c, c, linea, col))
            i += 1
            continue
        if c == "$":
            m = IDENT_RE.match(texto, i + 1)
            if not m:
                _fallar(linea, col, "nombre de parámetro después de «$»", c)
            tokens.append(Token("HUECO", m.group(0), linea, col))
            i = m.end()
            continue
        m = NUMERO_RE.match(texto, i)
        if m:
            crudo = m.group(0)
            valor = float(crudo) if any(x in crudo for x in ".eE") else int(crudo)
            tokens.append(Token("NUMBER", valor, linea, col))
            i = m.end()
            continue
        m = IDENT_RE.match(texto, i)
        if m:
            tokens.append(Token("IDENT", m.group(0), linea, col))
            i = m.end()
            continue
        _fallar(linea, col, "expresión", c)
    tokens.append(Token("EOF", "", linea, columna_base + len(texto)))
    return tokens


class _Expr:
    def __init__(self, tokens: list[Token], indice: int = 0, detener: set[str] | None = None):
        self.tokens = tokens
        self.i = indice
        self.detener = detener or set()

    def actual(self) -> Token:
        return self.tokens[self.i]

    def _fin(self) -> bool:
        t = self.actual()
        return t.tipo == "EOF" or (t.tipo == "IDENT" and t.valor in self.detener)

    def _tomar(self, tipo: str, valor: object | None = None) -> Token | None:
        t = self.actual()
        if t.tipo == tipo and (valor is None or t.valor == valor):
            self.i += 1
            return t
        return None

    def _exigir(self, tipo: str, esperado: str, valor: object | None = None) -> Token:
        t = self._tomar(tipo, valor)
        if t is None:
            a = self.actual()
            _fallar(a.linea, a.columna, esperado, a.valor)
        return t

    def expresion(self) -> _Nodo:
        if self._fin():
            t = self.actual()
            _fallar(t.linea, t.columna, "expresión", t.valor)
        return self._o()

    def _o(self) -> _Nodo:
        partes = [self._y()]
        operador = None
        while self.actual().tipo == "IDENT" and self.actual().valor == "o":
            if operador is None:
                operador = self.actual()
            self.i += 1
            partes.append(self._y())
        return partes[0] if len(partes) == 1 else _lista("o", operador, partes)

    def _y(self) -> _Nodo:
        partes = [self._no()]
        operador = None
        while self.actual().tipo == "IDENT" and self.actual().valor == "y":
            if operador is None:
                operador = self.actual()
            self.i += 1
            partes.append(self._no())
        return partes[0] if len(partes) == 1 else _lista("y", operador, partes)

    def _no(self) -> _Nodo:
        if self.actual().tipo == "IDENT" and self.actual().valor == "no":
            token = self.actual()
            self.i += 1
            return _lista("no", token, [self._no()])
        return self._comparacion()

    def _comparacion(self) -> _Nodo:
        izq = self._primario()
        if self.actual().tipo != "OP":
            return izq
        token = self.actual()
        op = str(token.valor)
        self.i += 1
        der = self._primario()
        if self.actual().tipo == "OP":
            t = self.actual()
            _fallar(t.linea, t.columna, "un solo comparador por expresión", t.valor)
        return _lista(op, token, [izq, der])

    def _primario(self) -> _Nodo:
        t = self.actual()
        if t.tipo == "NUMBER":
            self.i += 1
            return _hoja(t.valor, t)
        if t.tipo == "STRING":
            self.i += 1
            return _hoja(t.valor, t)
        if t.tipo == "HUECO":
            self.i += 1
            return _Nodo(["$", t.valor], t.linea, t.columna,
                         (_Nodo("$", t.linea, t.columna),
                          _Nodo(t.valor, t.linea, t.columna)))
        if t.tipo == "IDENT":
            nombre = t.valor
            self.i += 1
            if nombre in PALABRAS_LITERAL:
                return _hoja(PALABRAS_LITERAL[nombre], t)
            if self._tomar(".", "."):
                campo = self._exigir("IDENT", "nombre de campo")
                return _Nodo(
                    ["campo", nombre, campo.valor], t.linea, t.columna,
                    (_Nodo("campo", t.linea, t.columna),
                     _Nodo(nombre, t.linea, t.columna),
                     _Nodo(campo.valor, campo.linea, campo.columna)))
            if self._tomar("(", "("):
                args = []
                if not self._tomar(")", ")"):
                    while True:
                        args.append(self.expresion())
                        if self._tomar(")", ")"):
                            break
                        self._exigir(",", "',' o ')'")
                if nombre == "hecho":
                    if (len(args) != 1 or not isinstance(args[0].valor, list)
                            or args[0].valor[0] != "col"):
                        _fallar(t.linea, t.columna, "hecho(alias)")
                    return _Nodo(
                        ["hecho", args[0].valor[1]], t.linea, t.columna,
                        (_Nodo("hecho", t.linea, t.columna), args[0].hijos[1]))
                if nombre == "col":
                    if (len(args) != 1 or not isinstance(args[0].valor, list)
                            or args[0].valor[0] != "col"):
                        _fallar(t.linea, t.columna, "col(nombre)")
                    return _Nodo(
                        ["col", args[0].valor[1]], t.linea, t.columna,
                        (_Nodo("col", t.linea, t.columna), args[0].hijos[1]))
                return _lista(str(nombre), t, args)
            return _Nodo(["col", nombre], t.linea, t.columna,
                         (_Nodo("col", t.linea, t.columna),
                          _Nodo(nombre, t.linea, t.columna)))
        if self._tomar("(", "("):
            expr = self.expresion()
            self._exigir(")", "')'")
            return expr
        _fallar(t.linea, t.columna, "expresión", t.valor)


def _leer_expr_nodo(texto: str, linea: int, columna: int) -> _Nodo:
    p = _Expr(_tokenizar(texto, linea, columna))
    expr = p.expresion()
    t = p.actual()
    if t.tipo != "EOF":
        _fallar(t.linea, t.columna, "fin de expresión", t.valor)
    return expr


def _leer_expr(texto: str, linea: int, columna: int):
    return _leer_expr_nodo(texto, linea, columna).valor


def _leer_expr_en(texto: str, linea: int, columna: int,
                  ubicaciones: dict[str, Ubicacion] | None,
                  ruta: tuple[int, ...]):
    nodo = _leer_expr_nodo(texto, linea, columna)
    _registrar_nodo(ubicaciones, ruta, nodo)
    return nodo.valor


def _literal_texto(texto: str, linea: int, columna: int):
    """Lee un texto JSON o un hueco: `"x"` queda `"x"`, `$x` queda `["$", "x"]`."""
    tokens = _tokenizar(texto, linea, columna)
    if tokens[0].tipo == "STRING":
        valor = tokens[0].valor
    elif tokens[0].tipo == "HUECO":
        valor = ["$", tokens[0].valor]
    else:
        _fallar(tokens[0].linea, tokens[0].columna, "texto entre comillas", tokens[0].valor)
    if tokens[1].tipo != "EOF":
        _fallar(tokens[1].linea, tokens[1].columna, "fin de línea", tokens[1].valor)
    return valor


def _leer_umbral(texto: str, linea: int, columna: int):
    tokens = _tokenizar(texto, linea, columna)
    if tokens[0].tipo != "OP" or tokens[0].valor not in COMPARADORES:
        _fallar(tokens[0].linea, tokens[0].columna, "comparador de umbral", tokens[0].valor)
    p = _Expr(tokens, 1, detener={"porque"})
    limite = p.expresion()
    porque = p._exigir("IDENT", "porque", "porque")
    t = p.actual()
    if t.tipo == "STRING":
        defensa = t.valor
        p.i += 1
    elif t.tipo == "HUECO":
        defensa = ["$", t.valor]
        p.i += 1
    else:
        _fallar(t.linea, t.columna, "texto de defensa del umbral", t.valor)
    fin = p.actual()
    if fin.tipo != "EOF":
        _fallar(fin.linea, fin.columna, "fin de línea", fin.valor)
    return tokens[0].valor, limite.valor, defensa, porque.columna


def _lineas(texto: str) -> list[tuple[int, str]]:
    salida = []
    for n, linea in enumerate(texto.splitlines(), start=1):
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        salida.append((n, linea.rstrip()))
    return salida


def _indentada(linea: str, nivel: int, n: int) -> str:
    esperado = IND * nivel
    if not linea.startswith(esperado) or linea.startswith(esperado + " "):
        col = len(linea) - len(linea.lstrip()) + 1
        _fallar(n, col, f"indentación de {len(esperado)} espacios", linea[:col])
    return linea[len(esperado):]


def _exigir_prefijo(item: tuple[int, str], prefijo: str, nivel: int) -> tuple[str, int]:
    n, linea = item
    cuerpo = _indentada(linea, nivel, n)
    if not cuerpo.startswith(prefijo):
        _fallar(n, len(linea) - len(cuerpo) + 1, f"línea «{prefijo.strip()}»", cuerpo)
    return cuerpo[len(prefijo):], len(linea) - len(cuerpo) + len(prefijo) + 1


def _contenido(item: tuple[int, str], prefijo: str, nivel: int) -> tuple[str, int, int]:
    texto, col = _exigir_prefijo(item, prefijo, nivel)
    return texto, item[0], col


def _leer_nombre(texto: str, linea: int, columna: int):
    """Lee un nombre o un hueco: `rel` queda `"rel"`, `$rel` queda `["$", "rel"]`."""
    if not texto.startswith("$"):
        return texto
    nombre = texto[1:]
    if not nombre or IDENT_RE.fullmatch(nombre) is None:
        _fallar(linea, columna, "nombre de parámetro después de «$»", texto)
    return ["$", nombre]


def _leer_de(item: tuple[int, str], palabra: str = "de", *, con_columna: bool = False):
    resto, col = _exigir_prefijo(item, palabra + " ", 1)
    partes = resto.split()
    if len(partes) != 2:
        _fallar(item[0], col, f"{palabra} <relación> <alias>", resto)
    datos = ["de", _leer_nombre(partes[0], item[0], col),
             _leer_nombre(partes[1], item[0], col + len(partes[0]) + 1)]
    return (datos, col) if con_columna else datos


def _leer_requiere(item: tuple[int, str]) -> list:
    resto, col = _exigir_prefijo(item, "requiere ", 1)
    partes = [p.strip() for p in resto.split(",")]
    if not partes or any(not p for p in partes):
        _fallar(item[0], col, "una o más relaciones requeridas", resto)
    return ["requiere", *(_leer_nombre(p, item[0], col) for p in partes)]


def _macro_ninguno(clase: str, mid: str, cuerpo: list[tuple[int, str]], *,
                   ubicaciones: dict[str, Ubicacion] | None = None) -> list:
    esperado = 4
    if len(cuerpo) != esperado:
        linea = cuerpo[min(len(cuerpo) - 1, esperado - 1)][0] if cuerpo else 2
        _fallar(linea, 1, f"{esperado} líneas de cuerpo para {clase}")
    fuente = _leer_de(cuerpo[0])
    pred_txt, col_pred = _exigir_prefijo(cuerpo[1], "donde ", 1)
    op, limite, porque, col_umbral = _leer_umbral(*_contenido(cuerpo[2], "umbral ", 1))
    if op != "<=" or limite != 0:
        _fallar(cuerpo[2][0], col_umbral, "la macro ninguno con umbral <= 0")
    alcance = _literal_texto(*_contenido(cuerpo[3], "alcance ", 1))
    return [clase, mid, fuente[1], fuente[2],
            _leer_expr_en(pred_txt, cuerpo[1][0], col_pred, ubicaciones, (4,)),
            porque, alcance]


def _macro_ninguno_par(mid: str, cuerpo: list[tuple[int, str]], *,
                       ubicaciones: dict[str, Ubicacion] | None = None) -> list:
    if len(cuerpo) != 4:
        linea = cuerpo[0][0] if cuerpo else 2
        _fallar(linea, 1, "4 líneas de cuerpo para ninguno-par")
    resto, col = _exigir_prefijo(cuerpo[0], "de ", 1)
    m = re.fullmatch(r"(\S+)\s+(\S+)\s*,\s*(\S+)", resto)
    if not m:
        _fallar(cuerpo[0][0], col, "de <relación> <aliasA>, <aliasB>", resto)
    pred_txt, col_pred = _exigir_prefijo(cuerpo[1], "donde ", 1)
    op, limite, porque, col_umbral = _leer_umbral(*_contenido(cuerpo[2], "umbral ", 1))
    if op != "<=" or limite != 0:
        _fallar(cuerpo[2][0], col_umbral, "la macro ninguno-par con umbral <= 0")
    alcance = _literal_texto(*_contenido(cuerpo[3], "alcance ", 1))
    rel, alias_a, alias_b = m.groups()
    return ["ninguno-par", mid, rel, alias_a, alias_b,
            _leer_expr_en(pred_txt, cuerpo[1][0], col_pred, ubicaciones, (5,)),
            porque, alcance]


def _macro_peor(mid: str, cuerpo: list[tuple[int, str]], *,
                ubicaciones: dict[str, Ubicacion] | None = None) -> list:
    if len(cuerpo) != 5:
        linea = cuerpo[0][0] if cuerpo else 2
        _fallar(linea, 1, "5 líneas de cuerpo para peor")
    fuente = _leer_de(cuerpo[0])
    expr_txt, col_expr = _exigir_prefijo(cuerpo[1], "expresion ", 1)
    tol_txt, col_tol = _exigir_prefijo(cuerpo[2], "tolerancia ", 1)
    op, limite, porque, col_umbral = _leer_umbral(*_contenido(cuerpo[3], "umbral ", 1))
    tolerancia = _leer_expr_en(tol_txt, cuerpo[2][0], col_tol, ubicaciones, (5,))
    if op != "<=" or limite != tolerancia:
        _fallar(cuerpo[3][0], col_umbral, "la macro peor con umbral <= tolerancia")
    alcance = _literal_texto(*_contenido(cuerpo[4], "alcance ", 1))
    return ["peor", mid, fuente[1], fuente[2],
            _leer_expr_en(expr_txt, cuerpo[1][0], col_expr, ubicaciones, (4,)),
            tolerancia, porque, alcance]


def _leer_agregado(item: tuple[int, str], *,
                   ubicaciones: dict[str, Ubicacion] | None = None,
                   ruta: tuple[int, ...] = ()) -> list:
    resto, col = _exigir_prefijo(item, "agregado ", 2)
    nombre, sep, expr_txt = resto.partition(" = ")
    if not sep or not nombre.strip():
        _fallar(item[0], col, "agregado <nombre> = agregado(expr)", resto)
    nodo = _leer_expr_nodo(expr_txt, item[0], col + len(nombre) + len(sep))
    expr = nodo.valor
    if not isinstance(expr, list) or len(expr) != 2:
        _fallar(item[0], col + len(nombre) + len(sep), "llamada de agregado", expr_txt)
    if ubicaciones is not None:
        _registrar(ubicaciones, ruta, item[0], col)
        _registrar(ubicaciones, (*ruta, 0), item[0], col)
        _registrar_nodo(ubicaciones, (*ruta, 1), nodo.hijos[0])
        _registrar_nodo(ubicaciones, (*ruta, 2), nodo.hijos[1])
    return [nombre.strip(), expr[0], expr[1]]


def _leer_clave(item: tuple[int, str], *,
                ubicaciones: dict[str, Ubicacion] | None = None,
                ruta: tuple[int, ...] = ()) -> list:
    resto, col = _exigir_prefijo(item, "clave ", 2)
    nombre, sep, expr_txt = resto.partition(" = ")
    if not sep or not nombre.strip():
        _fallar(item[0], col, "clave <nombre> = expresión", resto)
    if ubicaciones is not None:
        _registrar(ubicaciones, ruta, item[0], col)
        _registrar(ubicaciones, (*ruta, 0), item[0], col)
    return [nombre.strip(), _leer_expr_en(
        expr_txt, item[0], col + len(nombre) + len(sep), ubicaciones, (*ruta, 1))]


def _leer_resumen(item: tuple[int, str], *,
                  ubicaciones: dict[str, Ubicacion] | None = None,
                  ruta: tuple[int, ...] = (3,)) -> list:
    resto, col = _exigir_prefijo(item, "resumen ", 1)
    nodo = _leer_expr_nodo(resto, item[0], col)
    expr = nodo.valor
    if not isinstance(expr, list) or len(expr) != 2:
        _fallar(item[0], col, "resumen agregado(expr)", resto)
    if ubicaciones is not None:
        _registrar(ubicaciones, ruta, item[0], col)
        _registrar(ubicaciones, (*ruta, 0), item[0], col)
        _registrar_nodo(ubicaciones, (*ruta, 1), nodo.hijos[0])
        _registrar_nodo(ubicaciones, (*ruta, 2), nodo.hijos[1])
    return ["resumen", expr[0], expr[1]]


def _rutas_de_fuentes(ubicaciones, fuentes) -> None:
    """Ubica cada fuente en la ruta que el álgebra le va a dar.

    `unir` es izquierdo-asociativo: `[unir [unir A B] C]`. Visto desde la tubería, `C` cuelga de `2`,
    `B` de `1.2`, `A` de `1.1`, y así hacia adentro. Se recorre al revés —de la última a la primera—
    porque la última es la que queda más cerca de la raíz.
    """
    if ubicaciones is None:
        return
    # `2` es la tubería dentro de la medida y `1` es la fuente dentro de `desde`: toda fuente cuelga
    # de `2.1`. De ahí para adentro manda la asociatividad izquierda del `unir`.
    ruta: tuple[int, ...] = (2, 1)
    for indice in range(len(fuentes) - 1, 0, -1):
        _, col, item = fuentes[indice]
        _registrar(ubicaciones, (*ruta, 2), item[0], col)
        ruta = (*ruta, 1)
    _, col, item = fuentes[0]
    _registrar(ubicaciones, ruta, item[0], col)


def _leer_medida(mid: str, cuerpo: list[tuple[int, str]], *,
                 ubicaciones: dict[str, Ubicacion] | None = None) -> list:
    if not cuerpo:
        _fallar(2, 1, "cuerpo de medida")
    fuentes = [(*_leer_de(cuerpo[0], con_columna=True), cuerpo[0])]
    i = 1
    while i < len(cuerpo):
        n, linea = cuerpo[i]
        if not _indentada(linea, 1, n).startswith("unir "):
            break
        fuentes.append((*_leer_de(cuerpo[i], "unir", con_columna=True), cuerpo[i]))
        i += 1

    # Las FUENTES también van al mapa. Sin esto, un error del álgebra dentro de un `unir` traía su
    # ruta —`2.1.2`, el lado derecho— y `ubicar_ruta` no encontraba nada, así que el fragmento decía
    # «no se encontró la ruta» en vez de señalar la línea. Media promesa cumplida es peor que
    # ninguna: el error sabía dónde estaba y el mapa no sabía traducirlo.
    #
    # El `unir` es izquierdo-asociativo, así que la ruta de cada fuente se arma de afuera hacia
    # adentro: con tres fuentes, la primera queda en `1.1`, la segunda en `1.2` y la tercera en `2`,
    # todo colgando de la ruta de la tubería.
    fuente = fuentes[0][0]
    for datos_siguiente, _col, _item in fuentes[1:]:
        fuente = ["unir", fuente, datos_siguiente]
    _rutas_de_fuentes(ubicaciones, fuentes)

    pasos = []
    while i < len(cuerpo):
        n, linea = cuerpo[i]
        actual = _indentada(linea, 1, n)
        if actual.startswith("donde "):
            expr_txt, col = _exigir_prefijo(cuerpo[i], "donde ", 1)
            ruta_paso = (2, len(pasos) + 2)
            _registrar(ubicaciones, ruta_paso, n, len(IND) + 1)
            _registrar(ubicaciones, (*ruta_paso, 0), n, len(IND) + 1)
            pasos.append(["donde", _leer_expr_en(
                expr_txt, n, col, ubicaciones, (*ruta_paso, 1))])
            i += 1
            continue
        if actual == "agrupar:":
            ruta_paso = (2, len(pasos) + 2)
            _registrar(ubicaciones, ruta_paso, n, len(IND) + 1)
            _registrar(ubicaciones, (*ruta_paso, 0), n, len(IND) + 1)
            i += 1
            claves = []
            agregados = []
            while i < len(cuerpo):
                n2, linea2 = cuerpo[i]
                if not linea2.startswith(IND2):
                    break
                interno = _indentada(linea2, 2, n2)
                if interno.startswith("clave "):
                    claves.append(_leer_clave(
                        cuerpo[i], ubicaciones=ubicaciones,
                        ruta=(*ruta_paso, 1, len(claves))))
                elif interno.startswith("agregado "):
                    agregados.append(_leer_agregado(
                        cuerpo[i], ubicaciones=ubicaciones,
                        ruta=(*ruta_paso, 2, len(agregados))))
                else:
                    _fallar(n2, len(IND2) + 1, "clave o agregado", interno)
                i += 1
            if not agregados:
                _fallar(n, len(IND) + 1, "al menos un agregado")
            pasos.append(["agrupar", claves, agregados])
            continue
        break

    if i >= len(cuerpo):
        _fallar(cuerpo[-1][0] + 1, 1, "resumen")
    resumen = _leer_resumen(cuerpo[i], ubicaciones=ubicaciones, ruta=(3,))
    i += 1
    if i >= len(cuerpo):
        _fallar(cuerpo[-1][0] + 1, 1, "umbral")
    op, limite, porque, _col = _leer_umbral(*_contenido(cuerpo[i], "umbral ", 1))
    i += 1
    requiere = None
    if i < len(cuerpo) and _indentada(cuerpo[i][1], 1, cuerpo[i][0]).startswith("requiere "):
        requiere = _leer_requiere(cuerpo[i])
        i += 1
    if i >= len(cuerpo):
        _fallar(cuerpo[-1][0] + 1, 1, "alcance")
    alcance = _literal_texto(*_contenido(cuerpo[i], "alcance ", 1))
    i += 1
    if i != len(cuerpo):
        n, linea = cuerpo[i]
        _fallar(n, len(linea) - len(linea.lstrip()) + 1, "fin de medida", linea.strip())

    base = ["medida", mid, ["desde", fuente, *pasos], resumen, ["umbral", op, limite, porque]]
    if requiere is not None:
        base.append(requiere)
    base.append(["alcance", alcance])
    return base


def _leer_guarda(item: tuple[int, str]) -> list:
    """Lee `guarda <expresión> "<mensaje>"`. El mensaje es la última cadena de la línea."""
    n, linea = item
    resto, col = _exigir_prefijo(item, "guarda ", 1)
    tokens = _tokenizar(resto, n, col)
    mensaje_idx = None
    for idx in range(len(tokens) - 1, -1, -1):
        if tokens[idx].tipo == "STRING":
            mensaje_idx = idx
            break
    if mensaje_idx is None:
        _fallar(n, col, "mensaje de la guarda entre comillas", resto)
    mensaje = tokens[mensaje_idx].valor
    expr_texto = resto[:tokens[mensaje_idx].columna - col]
    if not expr_texto.strip():
        _fallar(n, col, "expresión de la guarda", resto)
    return ["guarda", _leer_expr(expr_texto, n, col), mensaje]


def _leer_plantilla(bloque: list[tuple[int, str]]) -> list:
    """Lee la plantilla de una macro: una medida (o macro) con huecos, un nivel más adentro."""
    n0, linea0 = bloque[0]
    cuerpo0 = _indentada(linea0, 1, n0)
    m = re.fullmatch(r"(medida|ninguno|ninguno-par|peor)\s+(\S+):", cuerpo0)
    if not m:
        _fallar(n0, len(linea0) - len(cuerpo0) + 1,
                "plantilla «medida|ninguno|ninguno-par|peor <id>:»", cuerpo0)
    clase, mid_txt = m.groups()
    col_mid = len(linea0) - len(cuerpo0) + len(clase) + 2
    mid = _leer_nombre(mid_txt, n0, col_mid)
    cuerpo = [(n, linea[len(IND):]) for n, linea in bloque[1:]]
    if clase == "medida":
        return _leer_medida(mid, cuerpo)
    if clase == "ninguno":
        return _macro_ninguno(clase, mid, cuerpo)
    if clase == "ninguno-par":
        return _macro_ninguno_par(mid, cuerpo)
    return _macro_peor(mid, cuerpo)


def _huecos_en_linea(linea: str) -> list[tuple[str, int]]:
    """Devuelve (nombre, columna) de cada `$x` fuera de cadenas JSON."""
    huecos: list[tuple[str, int]] = []
    en_cadena = False
    i = 0
    while i < len(linea):
        c = linea[i]
        if en_cadena:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                en_cadena = False
            i += 1
            continue
        if c == '"':
            en_cadena = True
            i += 1
            continue
        if c == "$":
            m = IDENT_RE.match(linea, i + 1)
            if m:
                huecos.append((m.group(0), i + 1))
                i = m.end()
                continue
        i += 1
    return huecos


def _leer_defmacro(nombre: str, parametros: list[str], lineas: list[tuple[int, str]],
                   n: int) -> list:
    cuerpo = lineas[1:]
    i = 0
    guardas = []
    while i < len(cuerpo):
        n2, linea2 = cuerpo[i]
        if _indentada(linea2, 1, n2).startswith("guarda "):
            guardas.append(_leer_guarda(cuerpo[i]))
            i += 1
        else:
            break
    if i >= len(cuerpo):
        _fallar(cuerpo[-1][0] + 1 if cuerpo else n + 1, 1, "plantilla de la macro")
    plantilla = _leer_plantilla(cuerpo[i:])

    usados: set[str] = set()
    # Los huecos se cuentan desde el texto fuente, no desde el JSON: `$x` dentro de una cadena
    # de mensaje no es un hueco. `_huecos_en_linea` se salta las cadenas JSON.
    declarados = set(parametros)
    for _n2, _linea2 in cuerpo:
        for hueco, _col in _huecos_en_linea(_linea2):
            usados.add(hueco)
    desconocidos = sorted(usados - declarados)
    if desconocidos:
        for _n2, _linea2 in cuerpo:
            for hueco, col in _huecos_en_linea(_linea2):
                if hueco == desconocidos[0]:
                    _fallar(_n2, col, f"«${hueco}» no es un parámetro de la macro",
                            _linea2.strip(), literal=True)
    sin_usar = sorted(declarados - usados)
    if sin_usar:
        encabezado = lineas[0][1]
        m_param = re.search(rf"\b{re.escape(sin_usar[0])}\b", encabezado)
        _fallar(n, m_param.start() + 1,
                f"la macro declara el parámetro «{sin_usar[0]}» y la plantilla nunca lo usa",
                encabezado, literal=True)

    return ["defmacro", nombre, parametros, guardas, plantilla]


def leer_con_mapa(texto: str) -> Lectura:
    """Lee superficie infija y devuelve datos junto con ruta -> línea/columna.

    Una primera línea opcional `sintaxis MAYOR.MENOR` declara contra qué versión de la superficie se
    escribió el archivo. La versión se valida con el MISMO parser que el álgebra y se devuelve aparte
    —no es parte de la medida—; comprobar si es compatible con la de este núcleo es trabajo del que
    carga, no del lector, que es una función pura.
    """
    lineas = _lineas(texto)
    if not lineas:
        _fallar(1, 1, "encabezado de medida")
    version = None
    n, encabezado = lineas[0]
    m_ver = VERSION_LINE_RE.fullmatch(encabezado)
    if m_ver:
        version_txt = m_ver.group(1)
        try:
            parsear(version_txt)
        except VersionInvalida as e:
            _fallar(n, encabezado.find(version_txt) + 1, str(e), literal=True)
        version = version_txt
        lineas = lineas[1:]
        if not lineas:
            _fallar(n + 1, 1, "encabezado de medida")
        n, encabezado = lineas[0]
    m_def = DEFMACRO_RE.fullmatch(encabezado)
    if m_def:
        nombre, params_txt = m_def.groups()
        parametros = [p.strip() for p in params_txt.split(",") if p.strip()]
        if not parametros:
            _fallar(n, 1, "parámetros de la macro", encabezado)
        for p in parametros:
            if IDENT_RE.fullmatch(p) is None:
                _fallar(n, encabezado.find(p) + 1, f"nombre de parámetro, no «{p}»", encabezado)
        if len(set(parametros)) != len(parametros):
            _fallar(n, 1, "parámetros sin repetir", encabezado)
        datos = _leer_defmacro(nombre, parametros, lineas, n)
        ubicaciones: dict[str, Ubicacion] = {
            "": Ubicacion(n, 1),
            "0": Ubicacion(n, 1),
            "1": Ubicacion(n, encabezado.find(nombre) + 1),
        }
        return Lectura(datos, ubicaciones, version)
    m = re.fullmatch(r"(medida|ninguno|ninguno-par|peor)\s+(\S+):", encabezado)
    if not m:
        _fallar(n, 1, "encabezado «medida|ninguno|ninguno-par|peor <id>:»", encabezado)
    clase, mid = m.groups()
    # `\S+` acepta cualquier cosa sin espacios, y eso dejaba a la superficie escribir ids que el
    # resto del proyecto rechaza: `tareas.vencida_sin_dueño` se leía sin quejarse pero `--nueva` se
    # niega a crearlo. La gramática es una sola y vive en `ID_MEDIDA_RE`.
    if ID_MEDIDA_RE.fullmatch(mid) is None:
        _fallar(n, encabezado.find(mid) + 1,
                "id «dominio.nombre», sólo con minúsculas ASCII, dígitos y `_`", mid)
    ubicaciones: dict[str, Ubicacion] = {
        "": Ubicacion(n, 1),
        "0": Ubicacion(n, 1),
        "1": Ubicacion(n, encabezado.find(mid) + 1),
    }
    cuerpo = lineas[1:]
    if clase == "medida":
        datos = _leer_medida(mid, cuerpo, ubicaciones=ubicaciones)
    elif clase == "ninguno":
        datos = _macro_ninguno(clase, mid, cuerpo, ubicaciones=ubicaciones)
    elif clase == "ninguno-par":
        datos = _macro_ninguno_par(mid, cuerpo, ubicaciones=ubicaciones)
    else:
        datos = _macro_peor(mid, cuerpo, ubicaciones=ubicaciones)
    return Lectura(datos, ubicaciones, version)


def leer(texto: str) -> list:
    """Lee superficie infija y devuelve el JSON de almacenamiento."""
    return leer_con_mapa(texto).datos


def ubicar_ruta(texto: str, ruta: tuple[int, ...] | str) -> Ubicacion | None:
    """Traduce una ruta JSON de la medida a línea y columna de la superficie."""
    return leer_con_mapa(texto).ubicacion(ruta)


def fragmento_de_error(error: Exception, texto: str) -> str:
    """Muestra el diagnóstico con el fragmento de superficie señalado.

    Dos clases de error llegan acá y las dos tienen que salir señaladas: un `ErrorDeAlgebra`, que
    dice qué NODO ofende y hay que traducir su ruta a línea y columna, y un `ErrorSintaxis`, que ya
    trae la posición porque falló antes de haber AST que rutear.
    """
    ruta = getattr(error, "ruta", None)
    if ruta is None:
        linea = getattr(error, "linea", None)
        columna = getattr(error, "columna", None)
        if not isinstance(linea, int) or not isinstance(columna, int):
            return str(error)
        ubicacion = Ubicacion(linea, columna)
    else:
        ubicacion = ubicar_ruta(texto, ruta)
        if ubicacion is None:
            return f"{error}\n(no se encontró la ruta {ruta})"
    return _fragmento_en(texto, ubicacion, str(error))


def _fragmento_en(texto: str, ubicacion: Ubicacion, mensaje: str) -> str:
    lineas = texto.splitlines()
    fuente = lineas[ubicacion.linea - 1] if ubicacion.linea <= len(lineas) else ""
    numero = f"{ubicacion.linea:>4}"
    marca = " " * max(ubicacion.columna - 1, 0) + "^"
    return f"{mensaje}\n{numero} | {fuente}\n{' ' * len(numero)} | {marca}"


def _json(valor) -> str:
    return json.dumps(valor, ensure_ascii=False)


def _es_hueco(nodo) -> bool:
    """`["$", "x"]` es un hueco de plantilla, no una llamada a una función `$`."""
    return isinstance(nodo, list) and len(nodo) == 2 and nodo[0] == "$"


def _nombre(nodo) -> str:
    """Rinde un nombre o un hueco: `"rel"` queda `rel`, `["$", "rel"]` queda `$rel`."""
    return f"${nodo[1]}" if _es_hueco(nodo) else str(nodo)


def _texto_o_hueco(nodo) -> str:
    """Rinde un texto JSON o un hueco: `"razón"` queda `"razón"`, `["$", "x"]` queda `$x`."""
    return f"${nodo[1]}" if _es_hueco(nodo) else _json(nodo)


def _expr(expr, padre: int = 0) -> str:
    if _es_hueco(expr):
        return f"${expr[1]}"
    if not isinstance(expr, list):
        return _json(expr)
    if not expr:
        raise ValueError("expresión vacía")
    cabeza = expr[0]
    if cabeza == "campo":
        return f"{expr[1]}.{expr[2]}"
    if cabeza == "col":
        return expr[1]
    if cabeza == "hecho":
        return f"hecho({expr[1]})"
    if cabeza in COMPARADORES:
        prec = 3
        texto = f"{_expr(expr[1], prec)} {cabeza} {_expr(expr[2], prec)}"
    elif cabeza in ("y", "o"):
        prec = LOGICOS[cabeza]
        texto = f" {cabeza} ".join(_expr(e, prec) for e in expr[1:])
    elif cabeza == "no":
        prec = 4
        texto = f"no {_expr(expr[1], prec)}"
    else:
        prec = 5
        texto = f"{cabeza}({', '.join(_expr(e) for e in expr[1:])})"
    return f"({texto})" if prec < padre else texto


def _lineas_fuente(fuente) -> list[str]:
    if fuente[0] == "de":
        return [f"{IND}de {_nombre(fuente[1])} {_nombre(fuente[2])}"]
    if fuente[0] != "unir":
        raise ValueError(f"fuente no imprimible: {fuente!r}")
    lineas = _lineas_fuente(fuente[1])
    derecha = fuente[2]
    if derecha[0] != "de":
        raise ValueError("la superficie sólo imprime `unir` encadenado con fuentes `de`")
    lineas.append(f"{IND}unir {_nombre(derecha[1])} {_nombre(derecha[2])}")
    return lineas


def _imprimir_pasos(tuberia: list) -> list[str]:
    salida = []
    for paso in tuberia[2:]:
        if paso[0] == "donde":
            salida.append(f"{IND}donde {_expr(paso[1])}")
        elif paso[0] == "agrupar":
            salida.append(f"{IND}agrupar:")
            for nombre, expr in paso[1]:
                salida.append(f"{IND2}clave {_nombre(nombre)} = {_expr(expr)}")
            for nombre, agregado, expr in paso[2]:
                salida.append(f"{IND2}agregado {_nombre(nombre)} = {_nombre(agregado)}({_expr(expr)})")
        else:
            raise ValueError(f"paso no imprimible: {paso!r}")
    return salida


def imprimir(datos: list) -> str:
    """Devuelve la superficie canónica para una medida almacenada como JSON."""
    if not isinstance(datos, list) or not datos:
        raise ValueError("una medida tiene que ser una lista JSON")
    clase = datos[0]
    if clase == "ninguno":
        _c, mid, rel, alias, pred, porque, alcance = datos
        lineas = [
            f"ninguno {_nombre(mid)}:",
            f"{IND}de {_nombre(rel)} {_nombre(alias)}",
            f"{IND}donde {_expr(pred)}",
            f"{IND}umbral <= 0 porque {_texto_o_hueco(porque)}",
            f"{IND}alcance {_texto_o_hueco(alcance)}",
        ]
    elif clase == "ninguno-par":
        _c, mid, rel, alias_a, alias_b, pred, porque, alcance = datos
        lineas = [
            f"ninguno-par {_nombre(mid)}:",
            f"{IND}de {_nombre(rel)} {_nombre(alias_a)}, {_nombre(alias_b)}",
            f"{IND}donde {_expr(pred)}",
            f"{IND}umbral <= 0 porque {_texto_o_hueco(porque)}",
            f"{IND}alcance {_texto_o_hueco(alcance)}",
        ]
    elif clase == "peor":
        _c, mid, rel, alias, expr, tolerancia, porque, alcance = datos
        lineas = [
            f"peor {_nombre(mid)}:",
            f"{IND}de {_nombre(rel)} {_nombre(alias)}",
            f"{IND}expresion {_expr(expr)}",
            f"{IND}tolerancia {_expr(tolerancia)}",
            f"{IND}umbral <= {_expr(tolerancia)} porque {_texto_o_hueco(porque)}",
            f"{IND}alcance {_texto_o_hueco(alcance)}",
        ]
    elif clase == "defmacro":
        if len(datos) != 5:
            raise ValueError(
                "una macro es ['defmacro', nombre, parametros, guardas, plantilla]")
        _c, nombre, parametros, guardas, plantilla = datos
        lineas = [f"defmacro {nombre}({', '.join(parametros)}):"]
        for guarda in guardas:
            lineas.append(f"{IND}guarda {_expr(guarda[1])} {_json(guarda[2])}")
        for sublinea in imprimir(plantilla).rstrip("\n").split("\n"):
            lineas.append(f"{IND}{sublinea}")
    elif clase == "medida":
        if len(datos) == 7:
            _c, mid, tuberia, resumen, umbral, requiere, alcance = datos
        elif len(datos) == 6:
            _c, mid, tuberia, resumen, umbral, alcance = datos
            requiere = None
        else:
            raise ValueError("una medida canónica tiene 6 o 7 elementos")
        lineas = [f"medida {_nombre(mid)}:", *_lineas_fuente(tuberia[1]), *_imprimir_pasos(tuberia)]
        lineas.append(f"{IND}resumen {_nombre(resumen[1])}({_expr(resumen[2])})")
        lineas.append(f"{IND}umbral {umbral[1]} {_expr(umbral[2])} porque {_texto_o_hueco(umbral[3])}")
        if requiere is not None:
            lineas.append(f"{IND}requiere {', '.join(_nombre(r) for r in requiere[1:])}")
        lineas.append(f"{IND}alcance {_texto_o_hueco(alcance[1])}")
    else:
        raise ValueError(f"forma de medida no imprimible: {clase!r}")
    return "\n".join(lineas) + "\n"
