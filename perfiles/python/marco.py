"""Sensores optativos para árboles de módulos Python."""

from __future__ import annotations

import ast
from pathlib import Path

from nucleo.grafo import cierre


def hechos_de_modulos(raiz, paquetes, entradas) -> dict:
    """`modulo`, `importa` y `alcanzable` de un árbol de Python."""
    raiz = Path(raiz)
    modulos, importa = [], []
    for paquete in paquetes:
        for p in sorted((raiz / paquete).rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            nombre = ".".join(p.relative_to(raiz).with_suffix("").parts).removesuffix(".__init__")
            es_test = (p.name.startswith("test_") or p.name.endswith("_test.py")
                       or "tests" in p.parts)
            fuente = p.read_text(encoding="utf-8")
            arbol = ast.parse(fuente)
            modulos.append({"nombre": nombre, "es_test": es_test,
                            "lineas": len(fuente.splitlines()),
                            "es_paquete_vacio": p.name == "__init__.py" and not arbol.body})
            for n in ast.walk(arbol):
                objetivos = []
                if isinstance(n, ast.Import):
                    objetivos = [a.name for a in n.names]
                elif isinstance(n, ast.ImportFrom):
                    if n.level:
                        base = ".".join(nombre.split(".")[:-n.level] or [nombre.split(".")[0]])
                        objetivos = ([f"{base}.{n.module}"] if n.module
                                     else [f"{base}.{a.name}" for a in n.names])
                    elif n.module:
                        objetivos = [n.module]
                for objetivo in objetivos:
                    if objetivo.split(".")[0] in paquetes:
                        importa.append({"a": nombre, "b": objetivo, "es_test": es_test})

    conocidos = {m["nombre"] for m in modulos}
    aristas = [e for e in importa if e["b"] in conocidos]
    return {"modulo": modulos, "importa": aristas,
            "alcanzable": cierre(aristas, [e for e in entradas if e in conocidos])}
