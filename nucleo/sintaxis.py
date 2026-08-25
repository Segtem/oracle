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

COMPARADORES = ("==", "!=", "<=", ">=", "<", ">")
LOGICOS = {"y": 2, "o": 1}
PALABRAS_LITERAL = {"true": True, "false": False, "null": None}

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
NUMERO_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
IND = "    "
IND2 = IND * 2


@dataclass(frozen=True)
class ErrorSintaxis(ValueError):
    linea: int
    columna: int
    esperado: str
    encontrado: str = ""

    def __str__(self) -> str:
        visto = f"; llegó {self.encontrado}" if self.encontrado else ""
        return f"línea {self.linea}, columna {self.columna}: se esperaba {self.esperado}{visto}"


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

    def ubicacion(self, ruta: tuple[int, ...] | str) -> Ubicacion | None:
        return self.ubicaciones.get(_texto_ruta(_normalizar_ruta(ruta)))


@dataclass(frozen=True)
class _Nodo:
    valor: object
    linea: int
    columna: int
    hijos: tuple["_Nodo", ...] = ()


def _fallar(linea: int, columna: int, esperado: str, encontrado: object = "") -> None:
    raise ErrorSintaxis(linea, columna, esperado, repr(encontrado) if encontrado != "" else "")


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


def _literal_texto(texto: str, linea: int, columna: int) -> str:
    tokens = _tokenizar(texto, linea, columna)
    if tokens[0].tipo != "STRING":
        _fallar(tokens[0].linea, tokens[0].columna, "texto entre comillas", tokens[0].valor)
    if tokens[1].tipo != "EOF":
        _fallar(tokens[1].linea, tokens[1].columna, "fin de línea", tokens[1].valor)
    return str(tokens[0].valor)


def _leer_umbral(texto: str, linea: int, columna: int):
    tokens = _tokenizar(texto, linea, columna)
    if tokens[0].tipo != "OP" or tokens[0].valor not in COMPARADORES:
        _fallar(tokens[0].linea, tokens[0].columna, "comparador de umbral", tokens[0].valor)
    p = _Expr(tokens, 1, detener={"porque"})
    limite = p.expresion()
    porque = p._exigir("IDENT", "porque", "porque")
    texto_tok = p._exigir("STRING", "texto de defensa del umbral")
    fin = p.actual()
    if fin.tipo != "EOF":
        _fallar(fin.linea, fin.columna, "fin de línea", fin.valor)
    return tokens[0].valor, limite.valor, texto_tok.valor, porque.columna


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


def _leer_de(item: tuple[int, str], palabra: str = "de") -> list:
    resto, col = _exigir_prefijo(item, palabra + " ", 1)
    partes = resto.split()
    if len(partes) != 2:
        _fallar(item[0], col, f"{palabra} <relación> <alias>", resto)
    return ["de", partes[0], partes[1]]


def _leer_requiere(item: tuple[int, str]) -> list:
    resto, col = _exigir_prefijo(item, "requiere ", 1)
    partes = [p.strip() for p in resto.split(",")]
    if not partes or any(not p for p in partes):
        _fallar(item[0], col, "una o más relaciones requeridas", resto)
    return ["requiere", *partes]


def _macro_ninguno(clase: str, mid: str, cuerpo: list[tuple[int, str]], *,
                   ubicaciones: dict[str, Ubicacion] | None = None) -> list:
    esperado = 4
    if len(cuerpo) != esperado:
        linea = cuerpo[min(len(cuerpo), esperado - 1)][0] if cuerpo else 2
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


def _leer_medida(mid: str, cuerpo: list[tuple[int, str]], *,
                 ubicaciones: dict[str, Ubicacion] | None = None) -> list:
    if not cuerpo:
        _fallar(2, 1, "cuerpo de medida")
    fuentes = [_leer_de(cuerpo[0])]
    i = 1
    while i < len(cuerpo):
        n, linea = cuerpo[i]
        if not _indentada(linea, 1, n).startswith("unir "):
            break
        fuentes.append(_leer_de(cuerpo[i], "unir"))
        i += 1
    fuente = fuentes[0]
    for siguiente in fuentes[1:]:
        fuente = ["unir", fuente, siguiente]

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


def leer_con_mapa(texto: str) -> Lectura:
    """Lee superficie infija y devuelve datos junto con ruta -> línea/columna."""
    lineas = _lineas(texto)
    if not lineas:
        _fallar(1, 1, "encabezado de medida")
    n, encabezado = lineas[0]
    m = re.fullmatch(r"(medida|ninguno|ninguno-par|peor)\s+(\S+):", encabezado)
    if not m:
        _fallar(n, 1, "encabezado «medida|ninguno|ninguno-par|peor <id>:»", encabezado)
    clase, mid = m.groups()
    # `\S+` acepta cualquier cosa sin espacios, y eso dejaba a la superficie escribir ids que el
    # resto del proyecto rechaza: `tareas.vencida_sin_dueño` se leía sin quejarse pero
    # `--nuevo` se niega a crearlo. La gramática es una sola y vive en `ID_MEDIDA_RE`.
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
    return Lectura(datos, ubicaciones)


def leer(texto: str) -> list:
    """Lee superficie infija y devuelve el JSON de almacenamiento."""
    return leer_con_mapa(texto).datos


def ubicar_ruta(texto: str, ruta: tuple[int, ...] | str) -> Ubicacion | None:
    """Traduce una ruta JSON de la medida a línea y columna de la superficie."""
    return leer_con_mapa(texto).ubicacion(ruta)


def fragmento_de_error(error: Exception, texto: str) -> str:
    """Muestra el diagnóstico del álgebra con el fragmento de superficie señalado."""
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


def _expr(expr, padre: int = 0) -> str:
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
        return [f"{IND}de {fuente[1]} {fuente[2]}"]
    if fuente[0] != "unir":
        raise ValueError(f"fuente no imprimible: {fuente!r}")
    lineas = _lineas_fuente(fuente[1])
    derecha = fuente[2]
    if derecha[0] != "de":
        raise ValueError("la superficie sólo imprime `unir` encadenado con fuentes `de`")
    lineas.append(f"{IND}unir {derecha[1]} {derecha[2]}")
    return lineas


def _imprimir_pasos(tuberia: list) -> list[str]:
    salida = []
    for paso in tuberia[2:]:
        if paso[0] == "donde":
            salida.append(f"{IND}donde {_expr(paso[1])}")
        elif paso[0] == "agrupar":
            salida.append(f"{IND}agrupar:")
            for nombre, expr in paso[1]:
                salida.append(f"{IND2}clave {nombre} = {_expr(expr)}")
            for nombre, agregado, expr in paso[2]:
                salida.append(f"{IND2}agregado {nombre} = {agregado}({_expr(expr)})")
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
            f"ninguno {mid}:",
            f"{IND}de {rel} {alias}",
            f"{IND}donde {_expr(pred)}",
            f"{IND}umbral <= 0 porque {_json(porque)}",
            f"{IND}alcance {_json(alcance)}",
        ]
    elif clase == "ninguno-par":
        _c, mid, rel, alias_a, alias_b, pred, porque, alcance = datos
        lineas = [
            f"ninguno-par {mid}:",
            f"{IND}de {rel} {alias_a}, {alias_b}",
            f"{IND}donde {_expr(pred)}",
            f"{IND}umbral <= 0 porque {_json(porque)}",
            f"{IND}alcance {_json(alcance)}",
        ]
    elif clase == "peor":
        _c, mid, rel, alias, expr, tolerancia, porque, alcance = datos
        lineas = [
            f"peor {mid}:",
            f"{IND}de {rel} {alias}",
            f"{IND}expresion {_expr(expr)}",
            f"{IND}tolerancia {_expr(tolerancia)}",
            f"{IND}umbral <= {_expr(tolerancia)} porque {_json(porque)}",
            f"{IND}alcance {_json(alcance)}",
        ]
    elif clase == "medida":
        if len(datos) == 7:
            _c, mid, tuberia, resumen, umbral, requiere, alcance = datos
        elif len(datos) == 6:
            _c, mid, tuberia, resumen, umbral, alcance = datos
            requiere = None
        else:
            raise ValueError("una medida canónica tiene 6 o 7 elementos")
        lineas = [f"medida {mid}:", *_lineas_fuente(tuberia[1]), *_imprimir_pasos(tuberia)]
        lineas.append(f"{IND}resumen {resumen[1]}({_expr(resumen[2])})")
        lineas.append(f"{IND}umbral {umbral[1]} {_expr(umbral[2])} porque {_json(umbral[3])}")
        if requiere is not None:
            lineas.append(f"{IND}requiere {', '.join(requiere[1:])}")
        lineas.append(f"{IND}alcance {_json(alcance[1])}")
    else:
        raise ValueError(f"forma de medida no imprimible: {clase!r}")
    return "\n".join(lineas) + "\n"
