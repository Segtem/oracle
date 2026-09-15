"""Lenguaje de consultas de tareas (TQL en español) para Oracle.

Módulo puro de análisis léxico, sintáctico, tipado estático y evaluación
sobre tareas (`tools.tareas.Tarea`).
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

ID_COMPLETO_RE = re.compile(r"^[0-9]{8}-[0-9]{6}(?:-[a-z0-9_-]+)*$")
ENTERO_RE = re.compile(r"^[+-]?[0-9]+$")

# Sólo palabras: `<` y `>` redirigen en la shell, que es por lo que tatr tampoco los usa.
OPERADORES = {
    "menor": lambda a, b: a < b,
    "hasta": lambda a, b: a <= b,
    "mayor": lambda a, b: a > b,
    "desde": lambda a, b: a >= b,
    "igual": lambda a, b: a == b,
    "distinto": lambda a, b: a != b,
}

TIPO_BOOLEANO = "booleano"
TIPO_ENTERO = "entero"


class ConsultaInvalida(ValueError):
    """Error al analizar o compilar una consulta TQL."""

    def __init__(self, mensaje: str, columna: int, consulta: str = ""):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.columna = columna
        self.consulta = consulta

    def __str__(self) -> str:
        return f"{self.consulta}\n{' ' * self.columna}^\nERROR: {self.mensaje}"


@dataclass
class Token:
    texto: str
    columna: int  # Índice de carácter (0-indexed) en la consulta


def tokenizar(cadena: str) -> list[Token]:
    """Segmenta la consulta en tokens conservando la columna en caracteres."""
    tokens: list[Token] = []
    i = 0
    n = len(cadena)
    while i < n:
        c = cadena[i]
        if c.isspace():
            i += 1
            continue
        if c in "[]":
            tokens.append(Token(c, i))
            i += 1
            continue
        inicio = i
        while i < n and not cadena[i].isspace() and cadena[i] not in "[]":
            i += 1
        tokens.append(Token(cadena[inicio:i], inicio))
    return tokens


# ---- Nodos del AST ----

class Nodo(ABC):
    tipo: str
    columna: int

    @abstractmethod
    def evaluar(self, tarea: Any) -> Any:
        ...

    @abstractmethod
    def explicar(self) -> str:
        ...


@dataclass
class NodoCualquiera(Nodo):
    columna: int
    tipo: str = TIPO_BOOLEANO

    def evaluar(self, tarea: Any) -> bool:
        return True

    def explicar(self) -> str:
        return "cualquiera"


@dataclass
class NodoEtiquetada(Nodo):
    columna: int
    tipo: str = TIPO_BOOLEANO

    def evaluar(self, tarea: Any) -> bool:
        return len(tarea.etiquetas) > 0

    def explicar(self) -> str:
        return "etiquetada"


@dataclass
class NodoEtiqueta(Nodo):
    etiqueta: str
    columna: int
    tipo: str = TIPO_BOOLEANO

    def __post_init__(self):
        self._etiqueta_lower = self.etiqueta.lower()

    def evaluar(self, tarea: Any) -> bool:
        return any(e.lower() == self._etiqueta_lower for e in tarea.etiquetas)

    def explicar(self) -> str:
        return f":{self.etiqueta}"


@dataclass
class NodoId(Nodo):
    id_esperado: str
    columna: int
    tipo: str = TIPO_BOOLEANO

    def evaluar(self, tarea: Any) -> bool:
        return tarea.id == self.id_esperado

    def explicar(self) -> str:
        return f"id({self.id_esperado})"


@dataclass
class NodoPrioridad(Nodo):
    columna: int
    tipo: str = TIPO_ENTERO

    def evaluar(self, tarea: Any) -> int:
        return tarea.prioridad

    def explicar(self) -> str:
        return "prioridad"


@dataclass
class NodoEntero(Nodo):
    valor: int
    columna: int
    tipo: str = TIPO_ENTERO

    def evaluar(self, tarea: Any) -> int:
        return self.valor

    def explicar(self) -> str:
        return str(self.valor)


@dataclass
class NodoNo(Nodo):
    operando: Nodo
    columna: int
    tipo: str = TIPO_BOOLEANO

    def evaluar(self, tarea: Any) -> bool:
        return not self.operando.evaluar(tarea)

    def explicar(self) -> str:
        return f"(no {self.operando.explicar()})"


@dataclass
class NodoComparacion(Nodo):
    izq: Nodo
    operador: str
    der: Nodo
    columna: int
    tipo: str = TIPO_BOOLEANO

    def evaluar(self, tarea: Any) -> bool:
        return OPERADORES[self.operador](self.izq.evaluar(tarea), self.der.evaluar(tarea))

    def explicar(self) -> str:
        return f"({self.izq.explicar()} {self.operador} {self.der.explicar()})"


@dataclass
class NodoY(Nodo):
    izq: Nodo
    der: Nodo
    columna: int
    tipo: str = TIPO_BOOLEANO

    def evaluar(self, tarea: Any) -> bool:
        return self.izq.evaluar(tarea) and self.der.evaluar(tarea)

    def explicar(self) -> str:
        return f"({self.izq.explicar()} y {self.der.explicar()})"


@dataclass
class NodoO(Nodo):
    izq: Nodo
    der: Nodo
    columna: int
    tipo: str = TIPO_BOOLEANO

    def evaluar(self, tarea: Any) -> bool:
        return self.izq.evaluar(tarea) or self.der.evaluar(tarea)

    def explicar(self) -> str:
        return f"({self.izq.explicar()} o {self.der.explicar()})"


# ---- Parser y Verificador de Tipos ----

class _Parser:
    def __init__(self, texto: str, tokens: list[Token]):
        self.texto = texto
        self.tokens = tokens
        self.pos = 0

    def _actual(self) -> Token | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consumir(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parsear(self) -> Nodo:
        if not self.tokens:
            return NodoCualquiera(columna=0)
        raiz = self._parse_o()
        if self.pos < len(self.tokens):
            tok_sobrante = self.tokens[self.pos]
            raise ConsultaInvalida(
                f"token inesperado «{tok_sobrante.texto}»",
                columna=tok_sobrante.columna,
                consulta=self.texto,
            )
        if raiz.tipo != TIPO_BOOLEANO:
            raise ConsultaInvalida(
                f"tipo incorrecto: la consulta debe ser booleana (se esperaba booleano y llegó {raiz.tipo})",
                columna=raiz.columna,
                consulta=self.texto,
            )
        return raiz

    def _parse_o(self) -> Nodo:
        izq = self._parse_y()
        while True:
            tok = self._actual()
            if tok and tok.texto == "o":
                tok_op = self._consumir()
                if izq.tipo != TIPO_BOOLEANO:
                    raise ConsultaInvalida(
                        f"tipo incorrecto para «o»: se esperaba booleano y llegó {izq.tipo}",
                        columna=tok_op.columna,
                        consulta=self.texto,
                    )
                der = self._parse_y()
                if der.tipo != TIPO_BOOLEANO:
                    raise ConsultaInvalida(
                        f"tipo incorrecto para «o»: se esperaba booleano y llegó {der.tipo}",
                        columna=tok_op.columna,
                        consulta=self.texto,
                    )
                izq = NodoO(izq=izq, der=der, columna=tok_op.columna)
            else:
                break
        return izq

    def _parse_y(self) -> Nodo:
        izq = self._parse_comparacion()
        while True:
            tok = self._actual()
            if tok and tok.texto == "y":
                tok_op = self._consumir()
                if izq.tipo != TIPO_BOOLEANO:
                    raise ConsultaInvalida(
                        f"tipo incorrecto para «y»: se esperaba booleano y llegó {izq.tipo}",
                        columna=tok_op.columna,
                        consulta=self.texto,
                    )
                der = self._parse_comparacion()
                if der.tipo != TIPO_BOOLEANO:
                    raise ConsultaInvalida(
                        f"tipo incorrecto para «y»: se esperaba booleano y llegó {der.tipo}",
                        columna=tok_op.columna,
                        consulta=self.texto,
                    )
                izq = NodoY(izq=izq, der=der, columna=tok_op.columna)
            else:
                break
        return izq

    def _parse_comparacion(self) -> Nodo:
        izq = self._parse_primaria()
        while True:
            tok = self._actual()
            if tok and tok.texto in OPERADORES:
                tok_op = self._consumir()
                if izq.tipo != TIPO_ENTERO:
                    raise ConsultaInvalida(
                        f"tipo incorrecto para «{tok_op.texto}»: se esperaba entero y llegó {izq.tipo}",
                        columna=tok_op.columna,
                        consulta=self.texto,
                    )
                der = self._parse_primaria()
                if der.tipo != TIPO_ENTERO:
                    raise ConsultaInvalida(
                        f"tipo incorrecto para «{tok_op.texto}»: se esperaba entero y llegó {der.tipo}",
                        columna=tok_op.columna,
                        consulta=self.texto,
                    )
                izq = NodoComparacion(
                    izq=izq, operador=tok_op.texto, der=der, columna=tok_op.columna
                )
            else:
                break
        return izq

    def _parse_primaria(self) -> Nodo:
        tok = self._actual()
        if tok is None:
            raise ConsultaInvalida(
                "se esperaba una primaria al final de la consulta",
                columna=len(self.texto),
                consulta=self.texto,
            )

        if tok.texto == "no":
            tok_no = self._consumir()
            operando = self._parse_primaria()
            if operando.tipo != TIPO_BOOLEANO:
                raise ConsultaInvalida(
                    f"tipo incorrecto para «no»: se esperaba booleano y llegó {operando.tipo}",
                    columna=tok_no.columna,
                    consulta=self.texto,
                )
            return NodoNo(operando=operando, columna=tok_no.columna)

        if tok.texto == "[":
            tok_abre = self._consumir()
            nodo_interno = self._parse_o()
            tok_cierre = self._actual()
            if tok_cierre is None or tok_cierre.texto != "]":
                raise ConsultaInvalida(
                    "corchete '[' sin cerrar (falta ']')",
                    columna=tok_abre.columna,
                    consulta=self.texto,
                )
            self._consumir()
            return nodo_interno

        if tok.texto == "]":
            raise ConsultaInvalida(
                f"token inesperado «{tok.texto}»",
                columna=tok.columna,
                consulta=self.texto,
            )

        if tok.texto.startswith(":"):
            self._consumir()
            etiqueta = tok.texto[1:]
            if not etiqueta:
                raise ConsultaInvalida(
                    "etiqueta vacía después de ':'",
                    columna=tok.columna,
                    consulta=self.texto,
                )
            return NodoEtiqueta(etiqueta=etiqueta, columna=tok.columna)

        if tok.texto == "cualquiera":
            self._consumir()
            return NodoCualquiera(columna=tok.columna)

        if tok.texto == "etiquetada":
            self._consumir()
            return NodoEtiquetada(columna=tok.columna)

        if tok.texto == "prioridad":
            self._consumir()
            return NodoPrioridad(columna=tok.columna)

        if ENTERO_RE.fullmatch(tok.texto):
            self._consumir()
            return NodoEntero(valor=int(tok.texto), columna=tok.columna)

        if ID_COMPLETO_RE.fullmatch(tok.texto):
            self._consumir()
            return NodoId(id_esperado=tok.texto, columna=tok.columna)

        self._consumir()
        raise ConsultaInvalida(
            f"token inesperado «{tok.texto}»",
            columna=tok.columna,
            consulta=self.texto,
        )


@dataclass
class Consulta:
    texto: str
    tokens: list[Token]
    raiz: Nodo

    def evaluar(self, tarea: Any) -> bool:
        return self.raiz.evaluar(tarea)

    def explicar(self) -> str:
        lineas = ["TOKENS:"]
        if not self.tokens:
            lineas.append("  (vacío)")
        else:
            for t in self.tokens:
                lineas.append(f"  [{t.columna}] {t.texto}")
        lineas.append("COMPILADO:")
        lineas.append(f"  {self.raiz.explicar()}")
        return "\n".join(lineas)


def compilar(texto: str) -> Consulta:
    """Compila un texto de consulta TQL en un objeto Consulta listo para evaluar."""
    tokens = tokenizar(texto)
    parser = _Parser(texto, tokens)
    raiz = parser.parsear()
    return Consulta(texto=texto, tokens=tokens, raiz=raiz)
