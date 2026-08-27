"""Superficie infija de autoría para medidas.

El lector devuelve la misma forma de almacenamiento que recibió el impresor, incluidas las
invocaciones de macro que ya viven en el catálogo.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .proyecto import ID_MEDIDA_RE
from .version import VersionInvalida, parsear

COMPARADORES = ("==", "!=", "<=", ">=", "<", ">")
LOGICOS = {"y": 2, "o": 1}
PALABRAS_LITERAL = {"true": True, "false": False, "null": None}
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
DEFMACRO_RE = re.compile(r"defmacro\s+([^\s(]+)\s*\(([^)]*)\)\s*:")
ENCABEZADO_RE = re.compile(r"([^\s]+)\s+(\S+):")
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
        # Un error de tokenizador es lo primero que ve alguien que se equivoca, y «se esperaba
        # expresión; llegó '='» no le dice qué hacer. Los dos tropiezos que aparecen apenas
        # alguien escribe su primera medida tienen nombre y arreglo, así que se dicen.
        if c == "=" and texto[i:i + 2] != "==":
            _fallar(linea, col,
                    "la comparación se escribe «==», no «=»; «=» sola no es un operador del lenguaje",
                    literal=True)
        if unicodedata.category(c).startswith("L"):
            _fallar(linea, col,
                    f"«{c}» no puede ir en un nombre: relaciones, alias y campos usan minúsculas "
                    "ASCII, dígitos y `_`. La prosa de `porque` y `alcance` sí lleva acentos y eñes",
                    literal=True)
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
        _fallar(linea, tokens[0].columna, "texto entre comillas", tokens[0].valor)
    if tokens[1].tipo != "EOF":
        _fallar(linea, tokens[1].columna, "fin de línea", tokens[1].valor)
    return valor


def _leer_umbral(texto: str, linea: int, columna: int):
    tokens = _tokenizar(texto, linea, columna)
    if tokens[0].tipo != "OP":
        _fallar(linea, tokens[0].columna, "comparador de umbral", tokens[0].valor)
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


def _falta_o_sobra(cuerpo: list[tuple[int, str]], palabras: tuple[str, ...], clase: str) -> None:
    """Dice QUÉ línea falta, no sólo cuántas.

    «se esperaba 4 líneas de cuerpo para esta macro» es cierto y no sirve: quien escribió tres no sabe
    cuál de las cuatro se olvidó. Las macros tienen cuerpo fijo y en orden, así que la línea que
    falta se puede nombrar — y nombrarla es la diferencia entre releer la documentación y arreglarlo.
    """
    presentes = [_indentada(linea, 1, n).split(" ", 1)[0].rstrip(":") for n, linea in cuerpo]
    faltan = [p for p in palabras if p not in presentes]
    # Dónde señalar: la línea donde IRÍA la que falta. Con cuerpo, la siguiente a la última escrita;
    # sin cuerpo, la primera del cuerpo —la 2—, no una línea que no existe.
    ultima = cuerpo[-1][0] + 1 if cuerpo else 2
    if faltan:
        cuales = ", ".join(f"`{x}`" for x in faltan)
        _fallar(ultima, 1,
                f"a la macro {clase} le falta {cuales}. Su cuerpo son estas {len(palabras)} líneas, "
                f"en este orden: {', '.join(palabras)}", literal=True)
    _fallar(cuerpo[-1][0] if cuerpo else 2, 1,
            f"la macro {clase} lleva exactamente {len(palabras)} líneas de cuerpo "
            f"({', '.join(palabras)}) y llegaron {len(cuerpo)}", literal=True)


def _registro_macros(macros):
    if macros is None:
        from .macro import macros_base

        return macros_base()
    from .macro import MacroMalDeclarada, RegistroMacros

    if not isinstance(macros, RegistroMacros):
        raise MacroMalDeclarada("`macros` debe ser una instancia de RegistroMacros")
    return macros


def _linea_tiene_hueco_de(linea: str, parametros: set[str]) -> bool:
    return any(hueco in parametros for hueco, _col in _huecos_en_linea(linea))


def _palabra_de_linea(linea: str) -> str:
    return _indentada(linea, 1, 1).split(" ", 1)[0].rstrip(":")


def _sustituir_huecos(nodo, valores: dict):
    if _es_hueco(nodo):
        return valores.get(nodo[1], nodo)
    if not isinstance(nodo, list):
        return nodo
    return [_sustituir_huecos(hijo, valores) for hijo in nodo]


def _ubicacion_mas_cercana(ubicaciones: dict[str, Ubicacion] | None,
                           ruta: tuple[int, ...]) -> Ubicacion:
    if ubicaciones is None:
        return Ubicacion(1, 1)
    actual = ruta
    while True:
        ubicacion = ubicaciones.get(_texto_ruta(actual))
        if ubicacion is not None:
            return ubicacion
        if not actual:
            return Ubicacion(1, 1)
        actual = actual[:-1]


def _fallar_macro_en_ruta(nombre: str, ubicaciones: dict[str, Ubicacion] | None,
                          ruta: tuple[int, ...], esperado: str, encontrado) -> None:
    ubicacion = _ubicacion_mas_cercana(ubicaciones, ruta)
    _fallar(ubicacion.linea, ubicacion.columna,
            f"la macro {nombre} no coincide con su plantilla declarada: {esperado}",
            encontrado, literal=True)


def _copiar_ubicaciones_hueco(origen: dict[str, Ubicacion],
                              ruta_origen: tuple[int, ...],
                              destino: dict[str, Ubicacion] | None,
                              ruta_destino: tuple[int, ...]) -> None:
    if destino is None:
        return
    prefijo = _texto_ruta(ruta_origen)
    for texto_ruta, ubicacion in origen.items():
        if texto_ruta == prefijo:
            sufijo = ()
        elif prefijo and texto_ruta.startswith(prefijo + "."):
            sufijo = _normalizar_ruta(texto_ruta[len(prefijo) + 1:])
        elif not prefijo:
            sufijo = _normalizar_ruta(texto_ruta)
        else:
            continue
        destino[_texto_ruta((*ruta_destino, *sufijo))] = ubicacion


def _unificar_plantilla(patron, valor, nombre: str, capturas: dict,
                        ubicaciones_origen: dict[str, Ubicacion],
                        ubicaciones_salida: dict[str, Ubicacion] | None,
                        indices: dict[str, int], ruta: tuple[int, ...] = ()) -> None:
    if _es_hueco(patron):
        parametro = patron[1]
        if parametro in capturas:
            if capturas[parametro] != valor:
                _fallar_macro_en_ruta(
                    nombre, ubicaciones_origen, ruta,
                    f"«${parametro}» aparece más de una vez y las apariciones no coinciden",
                    valor)
            return
        capturas[parametro] = valor
        if parametro in indices:
            _copiar_ubicaciones_hueco(
                ubicaciones_origen, ruta, ubicaciones_salida, (indices[parametro],))
        return
    if isinstance(patron, list):
        if not isinstance(valor, list) or len(valor) != len(patron):
            _fallar_macro_en_ruta(nombre, ubicaciones_origen, ruta, f"se esperaba {patron!r}", valor)
        for indice, hijo in enumerate(patron):
            _unificar_plantilla(hijo, valor[indice], nombre, capturas, ubicaciones_origen,
                                ubicaciones_salida, indices, (*ruta, indice))
        return
    if patron != valor:
        _fallar_macro_en_ruta(nombre, ubicaciones_origen, ruta, f"se esperaba {patron!r}", valor)


def _agregar_tipo_parametro(tipos: dict[str, str], parametro: str, tipo: str) -> None:
    if tipo not in {"nombre", "expr", "texto"}:
        raise ValueError(
            f"el parámetro «{parametro}» ocupa un bloque {tipo} que la superficie no serializa")
    anterior = tipos.get(parametro)
    if anterior is not None and anterior != tipo:
        raise ValueError(
            f"el parámetro «{parametro}» aparece como {anterior} y como {tipo}")
    tipos[parametro] = tipo


def _tipos_en_plantilla(nodo, macros, tipos: dict[str, str], contexto: str,
                        visitadas: frozenset[str]) -> None:
    if _es_hueco(nodo):
        _agregar_tipo_parametro(tipos, nodo[1], contexto)
        return
    if not isinstance(nodo, list) or not nodo:
        return
    cabeza = nodo[0]
    if cabeza == "medida":
        if len(nodo) >= 2:
            _tipos_en_plantilla(nodo[1], macros, tipos, "nombre", visitadas)
        if len(nodo) >= 3:
            _tipos_en_plantilla(nodo[2], macros, tipos, "fuente", visitadas)
        if len(nodo) >= 4:
            _tipos_en_plantilla(nodo[3], macros, tipos, "resumen", visitadas)
        if len(nodo) >= 5:
            _tipos_en_plantilla(nodo[4], macros, tipos, "umbral", visitadas)
        for extra in nodo[5:]:
            _tipos_en_plantilla(extra, macros, tipos, "medida", visitadas)
        return
    if cabeza == "desde":
        for hijo in nodo[1:]:
            _tipos_en_plantilla(hijo, macros, tipos, "fuente", visitadas)
        return
    if cabeza == "de":
        for hijo in nodo[1:3]:
            _tipos_en_plantilla(hijo, macros, tipos, "nombre", visitadas)
        return
    if cabeza == "unir":
        for hijo in nodo[1:3]:
            _tipos_en_plantilla(hijo, macros, tipos, "fuente", visitadas)
        return
    if cabeza == "donde":
        if len(nodo) >= 2:
            _tipos_en_plantilla(nodo[1], macros, tipos, "expr", visitadas)
        return
    if cabeza == "agrupar":
        for clave in nodo[1] if len(nodo) > 1 and isinstance(nodo[1], list) else []:
            if isinstance(clave, list) and len(clave) >= 2:
                _tipos_en_plantilla(clave[0], macros, tipos, "nombre", visitadas)
                _tipos_en_plantilla(clave[1], macros, tipos, "expr", visitadas)
        for agregado in nodo[2] if len(nodo) > 2 and isinstance(nodo[2], list) else []:
            if isinstance(agregado, list) and len(agregado) >= 3:
                _tipos_en_plantilla(agregado[0], macros, tipos, "nombre", visitadas)
                _tipos_en_plantilla(agregado[1], macros, tipos, "nombre", visitadas)
                _tipos_en_plantilla(agregado[2], macros, tipos, "expr", visitadas)
        return
    if cabeza == "resumen":
        if len(nodo) >= 2:
            _tipos_en_plantilla(nodo[1], macros, tipos, "nombre", visitadas)
        if len(nodo) >= 3:
            _tipos_en_plantilla(nodo[2], macros, tipos, "expr", visitadas)
        return
    if cabeza == "umbral":
        if len(nodo) >= 3:
            _tipos_en_plantilla(nodo[2], macros, tipos, "expr", visitadas)
        if len(nodo) >= 4:
            _tipos_en_plantilla(nodo[3], macros, tipos, "texto", visitadas)
        return
    if cabeza == "requiere":
        for hijo in nodo[1:]:
            _tipos_en_plantilla(hijo, macros, tipos, "nombre", visitadas)
        return
    if cabeza == "alcance":
        if len(nodo) >= 2:
            _tipos_en_plantilla(nodo[1], macros, tipos, "texto", visitadas)
        return
    if isinstance(cabeza, str):
        registro = _registro_macros(macros)
        if cabeza in registro:
            if cabeza in visitadas:
                raise ValueError(f"macro recursiva no imprimible: {cabeza}")
            if len(nodo) - 1 != len(registro[cabeza].parametros):
                raise ValueError(
                    f"la plantilla invoca {cabeza} con {len(nodo) - 1} argumento(s), "
                    f"pero declara {len(registro[cabeza].parametros)}")
            propios = _tipos_de_parametros(registro[cabeza], registro, visitadas | {cabeza})
            for parametro, argumento in zip(registro[cabeza].parametros, nodo[1:]):
                _tipos_en_plantilla(argumento, macros, tipos, propios[parametro], visitadas)
            return
    for hijo in nodo[1:]:
        _tipos_en_plantilla(hijo, macros, tipos, "expr", visitadas)


def _tipos_de_parametros(macro, macros, visitadas: frozenset[str] = frozenset()) -> dict[str, str]:
    tipos: dict[str, str] = {}
    _tipos_en_plantilla(macro.plantilla, macros, tipos, "expr", visitadas)
    for expresion, _mensaje in macro.guardas:
        guardados: dict[str, str] = {}
        _tipos_en_plantilla(expresion, macros, guardados, "expr", visitadas)
        for parametro, tipo in guardados.items():
            if parametro not in tipos:
                tipos[parametro] = tipo
    faltan = [parametro for parametro in macro.parametros if parametro not in tipos]
    if faltan:
        raise ValueError(
            f"la macro {macro.nombre} no deja inferir cómo escribir «{faltan[0]}»")
    return tipos


def _leer_argumento_macro(item: tuple[int, str], parametro: str, tipo: str, *,
                          ubicaciones: dict[str, Ubicacion] | None,
                          ruta: tuple[int, ...]):
    resto, col = _exigir_prefijo(item, parametro + " ", 1)
    if tipo == "nombre":
        valor = resto.strip()
        if valor != resto or len(valor.split()) != 1:
            _fallar(item[0], col, f"{parametro} <nombre>", resto)
        _registrar(ubicaciones, ruta, item[0], col)
        return _leer_nombre(valor, item[0], col)
    if tipo == "texto":
        _registrar(ubicaciones, ruta, item[0], col)
        return _literal_texto(resto, item[0], col)
    return _leer_expr_en(resto, item[0], col, ubicaciones, ruta)


def _usa_forma_de_argumentos(cuerpo: list[tuple[int, str]], parametros: tuple[str, ...]) -> bool:
    esperados = parametros[1:]
    if not esperados or not cuerpo:
        return True
    primera = _indentada(cuerpo[0][1], 1, cuerpo[0][0]).split(" ", 1)[0]
    return primera == esperados[0]


def _leer_macro_por_argumentos(macro, mid, cuerpo: list[tuple[int, str]], *,
                               macros, ubicaciones: dict[str, Ubicacion] | None = None,
                               linea_encabezado: int = 1) -> list:
    parametros = macro.parametros
    esperados = parametros[1:]
    if len(cuerpo) != len(esperados):
        _falta_o_sobra(cuerpo, tuple(esperados), macro.nombre)
    try:
        tipos = _tipos_de_parametros(macro, macros, frozenset({macro.nombre}))
    except ValueError as e:
        _fallar(linea_encabezado, 1, str(e), literal=True)
    valores = {parametros[0]: mid}
    for indice, (parametro, item) in enumerate(zip(esperados, cuerpo), start=2):
        valores[parametro] = _leer_argumento_macro(
            item, parametro, tipos[parametro], ubicaciones=ubicaciones, ruta=(indice,))
    return [macro.nombre, *(valores[parametro] for parametro in parametros)]


def _leer_macro_por_plantilla(macro, mid, cuerpo: list[tuple[int, str]], *,
                              macros, ubicaciones: dict[str, Ubicacion] | None = None,
                              linea_encabezado: int = 1) -> list:
    parametros = macro.parametros
    if not parametros:
        _fallar(linea_encabezado, 1,
                f"la macro {macro.nombre} no declara parámetros de superficie", literal=True)
    visitadas = frozenset({macro.nombre})
    try:
        patron = _lineas_de_datos(macro.plantilla, macros, visitadas)
        patron_con_id = _lineas_de_datos(
            _sustituir_huecos(macro.plantilla, {parametros[0]: mid}), macros, visitadas)
    except ValueError as e:
        _fallar(linea_encabezado, 1, str(e), literal=True)

    parametros_del_cuerpo = set(parametros[1:])
    variables = {
        indice
        for indice, linea in enumerate(patron[1:], start=1)
        if _linea_tiene_hueco_de(linea, parametros_del_cuerpo)
    }
    esperadas = tuple(_palabra_de_linea(patron[indice]) for indice in sorted(variables))
    if len(cuerpo) != len(variables):
        _falta_o_sobra(cuerpo, esperadas, macro.nombre)

    reconstruidas = [(linea_encabezado, patron_con_id[0])]
    siguiente = 0
    for indice, linea in enumerate(patron_con_id[1:], start=1):
        if indice in variables:
            reconstruidas.append(cuerpo[siguiente])
            siguiente += 1
        else:
            numero = cuerpo[siguiente][0] if siguiente < len(cuerpo) else (
                cuerpo[-1][0] + 1 if cuerpo else linea_encabezado + 1)
            reconstruidas.append((numero, linea))

    ubicaciones_instancia: dict[str, Ubicacion] = {}
    instancia = _leer_bloque_forma(
        reconstruidas, macros=macros, ubicaciones=ubicaciones_instancia,
        permitir_huecos=True, validar_id=False)
    capturas = {parametros[0]: mid}
    indices = {parametro: indice + 1 for indice, parametro in enumerate(parametros)}
    _unificar_plantilla(
        macro.plantilla, instancia, macro.nombre, capturas, ubicaciones_instancia,
        ubicaciones, indices)
    sin_leer = [parametro for parametro in parametros if parametro not in capturas]
    if sin_leer:
        _fallar(linea_encabezado, 1,
                f"la macro {macro.nombre} no deja leer el parámetro «{sin_leer[0]}» "
                "desde su plantilla", literal=True)
    return [macro.nombre, *(capturas[parametro] for parametro in parametros)]


def _leer_macro_declarada(macro, mid, cuerpo: list[tuple[int, str]], *,
                          macros, ubicaciones: dict[str, Ubicacion] | None = None,
                          linea_encabezado: int = 1) -> list:
    if _usa_forma_de_argumentos(cuerpo, macro.parametros):
        return _leer_macro_por_argumentos(
            macro, mid, cuerpo, macros=macros, ubicaciones=ubicaciones,
            linea_encabezado=linea_encabezado)
    return _leer_macro_por_plantilla(
        macro, mid, cuerpo, macros=macros, ubicaciones=ubicaciones,
        linea_encabezado=linea_encabezado)


def _leer_bloque_forma(lineas: list[tuple[int, str]], *, macros=None,
                       ubicaciones: dict[str, Ubicacion] | None = None,
                       permitir_huecos: bool = False,
                       validar_id: bool = True) -> list:
    n, encabezado = lineas[0]
    m = ENCABEZADO_RE.fullmatch(encabezado)
    if not m:
        _fallar(n, 1, "encabezado «medida|macro declarada <id>:»", encabezado)
    clase, mid_txt = m.groups()
    col_mid = encabezado.find(mid_txt) + 1
    mid = _leer_nombre(mid_txt, n, col_mid) if permitir_huecos else mid_txt
    if clase != "medida":
        registro = _registro_macros(macros)
        if clase not in registro:
            _fallar(n, 1, "encabezado «medida|macro declarada <id>:»", encabezado)
    if validar_id and (not isinstance(mid, str) or ID_MEDIDA_RE.fullmatch(mid) is None):
        _fallar(n, col_mid,
                "id «dominio.nombre», sólo con minúsculas ASCII, dígitos y `_`", mid)
    cuerpo = lineas[1:]
    if clase == "medida":
        return _leer_medida(mid, cuerpo, ubicaciones=ubicaciones)
    return _leer_macro_declarada(
        registro[clase], mid, cuerpo, macros=registro, ubicaciones=ubicaciones,
        linea_encabezado=n)


def _leer_llamada_agregado(texto: str, linea: int, columna: int, esperado: str) -> _Nodo:
    tokens = _tokenizar(texto, linea, columna)
    cabeza = tokens[0]
    if cabeza.tipo == "IDENT":
        cabeza_nodo = _Nodo(cabeza.valor, cabeza.linea, cabeza.columna)
    elif cabeza.tipo == "HUECO":
        cabeza_nodo = _Nodo(
            ["$", cabeza.valor], cabeza.linea, cabeza.columna,
            (_Nodo("$", cabeza.linea, cabeza.columna),
             _Nodo(cabeza.valor, cabeza.linea, cabeza.columna)))
    else:
        _fallar(linea, cabeza.columna, esperado, texto)

    p = _Expr(tokens, 1)
    p._exigir("(", "'('")
    argumento = p.expresion()
    p._exigir(")", "')'")
    fin = p.actual()
    if fin.tipo != "EOF":
        _fallar(fin.linea, fin.columna, "fin de expresión", fin.valor)
    return _Nodo([cabeza_nodo.valor, argumento.valor], cabeza.linea, cabeza.columna,
                 (cabeza_nodo, argumento))


def _leer_agregado(item: tuple[int, str], *,
                   ubicaciones: dict[str, Ubicacion] | None = None,
                   ruta: tuple[int, ...] = ()) -> list:
    resto, col = _exigir_prefijo(item, "agregado ", 2)
    nombre, sep, expr_txt = resto.partition(" = ")
    nombre_limpio = nombre.strip()
    if not sep or not nombre_limpio or nombre_limpio != nombre or len(nombre_limpio.split()) != 1:
        _fallar(item[0], col, "agregado <nombre> = agregado(expr)", resto)
    nodo = _leer_llamada_agregado(
        expr_txt, item[0], col + len(nombre) + len(sep), "llamada de agregado")
    expr = nodo.valor
    if ubicaciones is not None:
        _registrar(ubicaciones, ruta, item[0], col)
        _registrar(ubicaciones, (*ruta, 0), item[0], col)
        _registrar_nodo(ubicaciones, (*ruta, 1), nodo.hijos[0])
        _registrar_nodo(ubicaciones, (*ruta, 2), nodo.hijos[1])
    return [_leer_nombre(nombre_limpio, item[0], col), expr[0], expr[1]]


def _leer_clave(item: tuple[int, str], *,
                ubicaciones: dict[str, Ubicacion] | None = None,
                ruta: tuple[int, ...] = ()) -> list:
    resto, col = _exigir_prefijo(item, "clave ", 2)
    nombre, sep, expr_txt = resto.partition(" = ")
    nombre_limpio = nombre.strip()
    if not sep or not nombre_limpio or nombre_limpio != nombre or len(nombre_limpio.split()) != 1:
        _fallar(item[0], col, "clave <nombre> = expresión", resto)
    if ubicaciones is not None:
        _registrar(ubicaciones, ruta, item[0], col)
        _registrar(ubicaciones, (*ruta, 0), item[0], col)
    return [_leer_nombre(nombre_limpio, item[0], col), _leer_expr_en(
        expr_txt, item[0], col + len(nombre) + len(sep), ubicaciones, (*ruta, 1))]


def _leer_resumen(item: tuple[int, str], *,
                  ubicaciones: dict[str, Ubicacion] | None = None,
                  ruta: tuple[int, ...] = (3,)) -> list:
    resto, col = _exigir_prefijo(item, "resumen ", 1)
    nodo = _leer_llamada_agregado(resto, item[0], col, "resumen agregado(expr)")
    expr = nodo.valor
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
    _registrar(ubicaciones, (4,), cuerpo[i][0], len(IND) + 1)
    _registrar(ubicaciones, (4, 0), cuerpo[i][0], len(IND) + 1)
    op, limite, porque, _col = _leer_umbral(*_contenido(cuerpo[i], "umbral ", 1))
    i += 1
    requiere = None
    if i < len(cuerpo) and _indentada(cuerpo[i][1], 1, cuerpo[i][0]).startswith("requiere "):
        _registrar(ubicaciones, (5,), cuerpo[i][0], len(IND) + 1)
        _registrar(ubicaciones, (5, 0), cuerpo[i][0], len(IND) + 1)
        requiere = _leer_requiere(cuerpo[i])
        i += 1
    if i >= len(cuerpo):
        _fallar(cuerpo[-1][0] + 1, 1, "alcance")
    ruta_alcance = (6,) if requiere is not None else (5,)
    _registrar(ubicaciones, ruta_alcance, cuerpo[i][0], len(IND) + 1)
    _registrar(ubicaciones, (*ruta_alcance, 0), cuerpo[i][0], len(IND) + 1)
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
    for idx, tok in reversed(list(enumerate(tokens))):
        if tok.tipo == "STRING":
            mensaje_idx = idx
            break
    if mensaje_idx is None:
        _fallar(n, col, "mensaje de la guarda entre comillas", resto)
    mensaje = tokens[mensaje_idx].valor
    expr_texto = resto[:tokens[mensaje_idx].columna - col]
    if not expr_texto.strip():
        _fallar(n, col, "expresión de la guarda", resto)
    return ["guarda", _leer_expr(expr_texto, n, col), mensaje]


def _leer_plantilla(bloque: list[tuple[int, str]], *, macros=None) -> list:
    """Lee la plantilla de una macro: una medida (o macro) con huecos, un nivel más adentro."""
    n0, linea0 = bloque[0]
    cuerpo0 = _indentada(linea0, 1, n0)
    m = ENCABEZADO_RE.fullmatch(cuerpo0)
    if not m:
        _fallar(n0, len(linea0) - len(cuerpo0) + 1,
                "plantilla «medida|macro declarada <id>:»", cuerpo0)
    lineas = [(n0, cuerpo0), *((n, linea[len(IND):]) for n, linea in bloque[1:])]
    try:
        return _leer_bloque_forma(lineas, macros=macros, permitir_huecos=True, validar_id=False)
    except ErrorSintaxis as e:
        esperado = e.esperado
        if esperado.startswith("encabezado «"):
            esperado = "plantilla " + esperado[len("encabezado "):]
        raise ErrorSintaxis(e.linea, e.columna + len(IND), esperado, e.encontrado, e.literal) from e


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
                   n: int, *, macros=None) -> list:
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
    plantilla = _leer_plantilla(cuerpo[i:], macros=macros)

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


def leer_con_mapa(texto: str, *, macros=None) -> Lectura:
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
        datos = _leer_defmacro(nombre, parametros, lineas, n, macros=macros)
        ubicaciones: dict[str, Ubicacion] = {
            "": Ubicacion(n, 1),
            "0": Ubicacion(n, 1),
            "1": Ubicacion(n, encabezado.find(nombre) + 1),
        }
        return Lectura(datos, ubicaciones, version)
    ubicaciones: dict[str, Ubicacion] = {
        "": Ubicacion(n, 1),
        "0": Ubicacion(n, 1),
    }
    m = ENCABEZADO_RE.fullmatch(encabezado)
    if m:
        ubicaciones["1"] = Ubicacion(n, encabezado.find(m.group(2)) + 1)
    datos = _leer_bloque_forma(lineas, macros=macros, ubicaciones=ubicaciones)
    return Lectura(datos, ubicaciones, version)


def leer(texto: str, *, macros=None) -> list:
    """Lee superficie infija y devuelve el JSON de almacenamiento."""
    return leer_con_mapa(texto, macros=macros).datos


def ubicar_ruta(texto: str, ruta: tuple[int, ...] | str, *, macros=None) -> Ubicacion | None:
    """Traduce una ruta JSON de la medida a línea y columna de la superficie."""
    return leer_con_mapa(texto, macros=macros).ubicacion(ruta)


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
        return f"{cabeza}({', '.join(_expr(e) for e in expr[1:])})"
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


def _lineas_medida(datos: list) -> list[str]:
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
    return lineas


def _lineas_defmacro(datos: list, macros, visitadas: frozenset[str]) -> list[str]:
    if len(datos) != 5:
        raise ValueError(
            "una macro es ['defmacro', nombre, parametros, guardas, plantilla]")
    _c, nombre, parametros, guardas, plantilla = datos
    lineas = [f"defmacro {nombre}({', '.join(parametros)}):"]
    for guarda in guardas:
        lineas.append(f"{IND}guarda {_expr(guarda[1])} {_json(guarda[2])}")
    for sublinea in _lineas_de_datos(plantilla, macros, visitadas):
        lineas.append(f"{IND}{sublinea}")
    return lineas


def _lineas_macro_declarada(datos: list, macros, visitadas: frozenset[str]) -> list[str]:
    clase = datos[0]
    registro = _registro_macros(macros)
    if clase not in registro:
        raise ValueError(f"forma de medida no imprimible: {clase!r}")
    if clase in visitadas:
        cadena = " -> ".join((*visitadas, clase))
        raise ValueError(f"macro recursiva no imprimible: {cadena}")
    macro = registro[clase]
    esperados = len(macro.parametros)
    if len(datos) - 1 != esperados:
        raise ValueError(
            f"la macro {clase} lleva {esperados} argumento(s) y recibió {len(datos) - 1}")

    try:
        tipos = _tipos_de_parametros(macro, registro, visitadas | frozenset({clase}))
    except ValueError as e:
        raise ValueError(str(e)) from e
    lineas = [f"{clase} {_nombre(datos[1])}:"]
    for parametro, valor in zip(macro.parametros[1:], datos[2:]):
        tipo = tipos[parametro]
        if tipo == "nombre":
            superficie = _nombre(valor)
        elif tipo == "texto":
            superficie = _texto_o_hueco(valor)
        else:
            superficie = _expr(valor)
        lineas.append(f"{IND}{parametro} {superficie}")
    return lineas


def _lineas_de_datos(datos: list, macros=None,
                     visitadas: frozenset[str] = frozenset()) -> list[str]:
    """Devuelve líneas de superficie sin salto final."""
    if not isinstance(datos, list) or not datos:
        raise ValueError("una medida tiene que ser una lista JSON")
    clase = datos[0]
    if clase == "defmacro":
        return _lineas_defmacro(datos, macros, visitadas)
    if clase == "medida":
        return _lineas_medida(datos)
    return _lineas_macro_declarada(datos, macros, visitadas)


def imprimir(datos: list, *, macros=None) -> str:
    """Devuelve la superficie canónica para una medida almacenada como JSON."""
    return "\n".join(_lineas_de_datos(datos, macros)) + "\n"
