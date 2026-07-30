"""Mutación de CÓDIGO — la otra mitad del sensor, y la que atrapó 3 de los casos del corpus.

`mutacion.py` muta medidas, que son datos. Esto muta el árbol sintáctico de archivos `.py` reales,
que es más caro y más incómodo, y hace falta igual: los tests que no discriminan sólo se ven
rompiendo el código que dicen cubrir.

## Los mutantes se GENERAN, no se declaran

Es la decisión de diseño del módulo. Si el autor elige qué romper, elige —sin querer— lo que sus
tests ya atrapan, que es el sesgo del que todo este repositorio intenta salir. Un recorrido del AST
no tiene opinión: propone todo lo que puede proponer, y los sobrevivientes son la lista honesta de lo
que nadie está fijando.

Cinco operadores, deliberadamente pocos:

  · `comparador`  <  ↔  <=   ·  >  ↔  >=   ·  ==  ↔  !=   ·  is ↔ is not   ·  in ↔ not in
  · `booleano`    and ↔ or
  · `negacion`    se borra un `not`
  · `constante`   n → n+1  ·  True ↔ False
  · `retorno`     `return <algo>` → `return None`

## El caché

Cada corrida limpia `__pycache__` ANTES de correr los tests. No es prolijidad: `max` y `min` ocupan
lo mismo y CPython invalida el `.pyc` por (mtime, tamaño), así que mutar y restaurar dentro del mismo
segundo deja al intérprete corriendo el bytecode mutado sobre el código ya restaurado. Es el caso
`006` del corpus, y con él los resultados de una ronda entera fueron basura.

## Mutantes equivalentes

Algunos mutantes no cambian el comportamiento y no se pueden matar (un `<` que sólo compara enteros
donde el borde es imposible, un mensaje de error). Se pueden declarar en `equivalentes.json`, pero
**con una razón escrita**, igual que un umbral lleva su defensa. Un equivalente sin razón es una
excusa, y el número de equivalentes declarados es una métrica que hay que mirar.
"""

from __future__ import annotations

import ast
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

CAMBIOS_COMPARADOR = {
    ast.Lt: ast.LtE, ast.LtE: ast.Lt,
    ast.Gt: ast.GtE, ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
    ast.Is: ast.IsNot, ast.IsNot: ast.Is,
    ast.In: ast.NotIn, ast.NotIn: ast.In,
}


@dataclass(frozen=True)
class Sitio:
    """Un lugar mutable del archivo. El `id` tiene que ser estable entre corridas."""

    archivo: str
    linea: int
    columna: int
    operador: str
    descripcion: str

    @property
    def id(self) -> str:
        return f"{self.archivo}:{self.linea}:{self.columna}:{self.operador}"


class _Recolector(ast.NodeVisitor):
    def __init__(self, archivo: str):
        self.archivo = archivo
        self.sitios: list[Sitio] = []

    def _añadir(self, nodo, operador, descripcion):
        self.sitios.append(Sitio(self.archivo, getattr(nodo, "lineno", 0),
                                 getattr(nodo, "col_offset", 0), operador, descripcion))

    def visit_Compare(self, nodo):
        for op in nodo.ops:
            if type(op) in CAMBIOS_COMPARADOR:
                self._añadir(nodo, "comparador",
                             f"{type(op).__name__} → {CAMBIOS_COMPARADOR[type(op)].__name__}")
                break
        self.generic_visit(nodo)

    def visit_BoolOp(self, nodo):
        self._añadir(nodo, "booleano", "and ↔ or")
        self.generic_visit(nodo)

    def visit_UnaryOp(self, nodo):
        if isinstance(nodo.op, ast.Not):
            self._añadir(nodo, "negacion", "se borra el `not`")
        self.generic_visit(nodo)

    def visit_Constant(self, nodo):
        if isinstance(nodo.value, bool):
            self._añadir(nodo, "constante", f"{nodo.value} → {not nodo.value}")
        elif isinstance(nodo.value, (int, float)):
            self._añadir(nodo, "constante", f"{nodo.value} → {nodo.value + 1}")

    def visit_Return(self, nodo):
        if nodo.value is not None and not (
                isinstance(nodo.value, ast.Constant) and nodo.value.value is None):
            self._añadir(nodo, "retorno", "return <algo> → return None")
        self.generic_visit(nodo)


class _Aplicador(ast.NodeTransformer):
    """Aplica UN solo sitio. Un mutante = un cambio, o no se sabe cuál mató al test."""

    def __init__(self, objetivo: Sitio):
        self.objetivo = objetivo
        self.aplicado = False

    def _es(self, nodo, operador) -> bool:
        return (not self.aplicado
                and getattr(nodo, "lineno", -1) == self.objetivo.linea
                and getattr(nodo, "col_offset", -1) == self.objetivo.columna
                and operador == self.objetivo.operador)

    def visit_Compare(self, nodo):
        self.generic_visit(nodo)
        if self._es(nodo, "comparador"):
            for i, op in enumerate(nodo.ops):
                if type(op) in CAMBIOS_COMPARADOR:
                    nodo.ops[i] = CAMBIOS_COMPARADOR[type(op)]()
                    self.aplicado = True
                    break
        return nodo

    def visit_BoolOp(self, nodo):
        self.generic_visit(nodo)
        if self._es(nodo, "booleano"):
            nodo.op = ast.Or() if isinstance(nodo.op, ast.And) else ast.And()
            self.aplicado = True
        return nodo

    def visit_UnaryOp(self, nodo):
        self.generic_visit(nodo)
        if isinstance(nodo.op, ast.Not) and self._es(nodo, "negacion"):
            self.aplicado = True
            return nodo.operand
        return nodo

    def visit_Constant(self, nodo):
        if self._es(nodo, "constante"):
            if isinstance(nodo.value, bool):
                nodo = ast.Constant(value=not nodo.value)
            elif isinstance(nodo.value, (int, float)):
                nodo = ast.Constant(value=nodo.value + 1)
            self.aplicado = True
        return nodo

    def visit_Return(self, nodo):
        self.generic_visit(nodo)
        if self._es(nodo, "retorno"):
            nodo.value = ast.Constant(value=None)
            self.aplicado = True
        return nodo


def sitios_de(ruta: Path, raiz: Path) -> list[Sitio]:
    rel = str(ruta.relative_to(raiz))
    r = _Recolector(rel)
    r.visit(ast.parse(ruta.read_text(encoding="utf-8")))
    return r.sitios


def mutar_fuente(fuente: str, sitio: Sitio) -> str | None:
    arbol = ast.parse(fuente)
    ap = _Aplicador(sitio)
    nuevo = ap.visit(arbol)
    if not ap.aplicado:
        return None
    ast.fix_missing_locations(nuevo)
    return ast.unparse(nuevo)


def limpiar_cache(raiz: Path) -> int:
    """Borra todo `__pycache__` bajo `raiz`. Sin esto la ronda entera puede ser basura (caso 006)."""
    n = 0
    for d in raiz.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)
        n += 1
    return n


def correr_tests(comando: list[str], raiz: Path) -> bool:
    """True si los tests pasan. Se corre SIEMPRE con el caché ya limpio."""
    r = subprocess.run(comando, cwd=str(raiz), capture_output=True, text=True)
    return r.returncode == 0


def correr(raiz: Path, objetivos: list[Path], comando: list[str],
           equivalentes: dict[str, str] | None = None, al_terminar_uno=None) -> dict:
    """Genera y prueba todos los mutantes. Devuelve EVIDENCIA, no un informe.

    Restaura siempre el archivo original, incluso si el subproceso revienta: el `finally` es lo único
    que separa esta herramienta de un destructor de repositorios.
    """
    equivalentes = equivalentes or {}
    filas: list[dict] = []

    for ruta in objetivos:
        original = ruta.read_text(encoding="utf-8")
        for sitio in sitios_de(ruta, raiz):
            mutado = mutar_fuente(original, sitio)
            if mutado is None:
                continue
            try:
                ruta.write_text(mutado, encoding="utf-8")
                limpiar_cache(raiz)
                murio = not correr_tests(comando, raiz)
            finally:
                ruta.write_text(original, encoding="utf-8")
                limpiar_cache(raiz)

            filas.append({
                "id": sitio.id,
                "apunta_a": sitio.archivo,
                "cambio": f"{sitio.operador}: {sitio.descripcion}",
                "murio": murio,
                "equivalente_declarado": sitio.id in equivalentes,
                "razon_equivalente": equivalentes.get(sitio.id, ""),
            })
            if al_terminar_uno:
                al_terminar_uno(filas[-1])

    reales = [f for f in filas if not f["equivalente_declarado"]]
    return {
        "mutante": reales,
        "mutante_equivalente": [f for f in filas if f["equivalente_declarado"]],
        "corrida_mutacion": [{
            "id": "mutacion_de_codigo",
            "mutantes": len(reales),
            "bytecode_frio": True,       # se limpia antes de CADA corrida de tests
            "resultado_confiable": True,
        }],
    }
