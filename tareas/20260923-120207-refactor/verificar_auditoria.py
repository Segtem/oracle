"""Auditoría previa por AST; --despues importa el MCP y verifica su declaración real."""

import argparse
import ast
import copy
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SHA256_DECLARACIONES = "ba56e283a38179e3fdcfe9391bd3096fb96e33f6149edfdcdf8d8442db0ddbac"


def arbol(ruta):
    return ast.parse((RAIZ / ruta).read_text(encoding="utf-8"))


def nodo(arbol_, tipo, linea):
    return next(n for n in ast.walk(arbol_) if isinstance(n, tipo) and n.lineno == linea)


def firma(n):
    return ast.dump(n, include_attributes=False)


def iguales(nodos):
    assert len({firma(n) for n in nodos}) == 1


def cuerpo(funcion):
    instrucciones = funcion.body
    if isinstance(instrucciones[0], ast.Expr) and isinstance(instrucciones[0].value, ast.Constant):
        instrucciones = instrucciones[1:]
    return ast.Module(body=instrucciones, type_ignores=[])


def funcion(arbol_, nombre):
    return next(n for n in arbol_.body if isinstance(n, ast.FunctionDef) and n.name == nombre)


def serializar(valor):
    return json.dumps(valor, ensure_ascii=False, separators=(",", ":")).encode()


def verificar_despues():
    sys.path.insert(0, str(RAIZ))
    from tools import mcp

    huella = hashlib.sha256(serializar(mcp.HERRAMIENTAS)).hexdigest()
    if huella != SHA256_DECLARACIONES:
        raise AssertionError(f"JSON MCP distinto: SHA256 {huella}; esperado {SHA256_DECLARACIONES}")
    print("OK: bytes JSON MCP conservados; SHA256", huella)

    # Ningún diccionario o lista puede compartirse entre declaraciones ni con
    # las plantillas: cambiar una herramienta no debe alterar otra ni su fuente.
    vistos = set()

    def independientes(valor):
        if isinstance(valor, (dict, list)):
            if id(valor) in vistos:
                raise AssertionError("Las declaraciones comparten una estructura mutable")
            vistos.add(id(valor))
            for hijo in (valor.values() if isinstance(valor, dict) else valor):
                independientes(hijo)

    for valor in [*mcp.HERRAMIENTAS, mcp._ESQUEMA_MEDIDA, mcp._ANOTACIONES,
                  mcp._ESQUEMA_UMBRAL, mcp._DEFS_EVIDENCIA, mcp._ESQUEMA_SOMBRA]:
        independientes(valor)
    print("OK: estructuras mutables independientes, incluidas las plantillas")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--despues", action="store_true",
                        help="verifica el contrato y las copias tras el refactor")
    if parser.parse_args().despues:
        verificar_despues()
        return
    mcp = arbol("tools/mcp.py")
    # Líneas físicas inclusivas. Cada constante conserva el bloque más corto;
    # se agregan una referencia por sitio y dos líneas separadoras por constante.
    grupos = [
        ("M1 medida", [150, 261]),
        ("M2 annotations", [51, 139, 248, 513, 664]),
        ("M3 umbral", [112, 204, 588]),
        ("M4 defs evidencia", [176, 331, 536]),
        ("M5 sombra", [215, 599]),
    ]
    reemplazos = {}
    ahorro = 0
    for nombre, lineas in grupos:
        nodos = [nodo(mcp, ast.Dict, linea) for linea in lineas]
        iguales(nodos)
        largos = [n.end_lineno - n.lineno + 1 for n in nodos]
        neto = sum(largos) - min(largos) - len(nodos) - 2
        ahorro += neto
        for n in nodos:
            reemplazos[n.lineno] = nodos[0]
        print(f"{nombre}: AST idénticos; bloques {largos}; ahorro neto {neto}")

    # Expande copias independientes de una única definición en memoria. Verifica
    # los bytes completos, incluido el orden de claves, sin cambiar el contrato.
    class Compartir(ast.NodeTransformer):
        def visit_Dict(self, n):
            if n.lineno in reemplazos:
                return copy.deepcopy(reemplazos[n.lineno])
            return self.generic_visit(n)

    originales = [n for n in mcp.body if isinstance(n, ast.Assign)
                  and isinstance(n.targets[0], ast.Name)
                  and n.targets[0].id.startswith("HERRAMIENTA_")]
    antes = [ast.literal_eval(n.value) for n in originales]
    despues = [ast.literal_eval(Compartir().visit(copy.deepcopy(n.value))) for n in originales]
    assert serializar(antes) == serializar(despues)
    print(f"M1–M5: bytes JSON idénticos; ahorro conjunto {ahorro - 1} (incluye import deepcopy)")
    print("SHA256 declaración:", hashlib.sha256(serializar(antes)).hexdigest())

    handlers = [nodo(mcp, ast.ExceptHandler, linea) for linea in [1236, 1515, 1589, 1748]]
    iguales(handlers)
    assert [h.end_lineno - h.lineno + 1 for h in handlers] == [12, 6, 7, 7]
    print("M6: cuatro handlers idénticos; 32 líneas → 21; ahorro 11")

    cargas = [nodo(mcp, ast.Try, linea) for linea in [1481, 1545, 1682]]
    iguales(cargas)
    assert all(n.end_lineno - n.lineno + 1 == 6 for n in cargas)
    print("M7: tres cargas idénticas; 18 líneas → 12; ahorro 6")

    caso, vocabulario, sintaxis = map(arbol, ["nucleo/caso.py", "nucleo/vocabulario.py", "nucleo/sintaxis.py"])
    iguales([cuerpo(funcion(a, "opciones")) for a in [caso, vocabulario]])
    print("N1: opciones tiene el mismo cuerpo sin globals propios; 9 líneas → import de 1; ahorro 8")

    for nombre in ["_indentada", "_fallar"]:
        iguales([funcion(a, nombre) for a in [caso, sintaxis]])
    def constante(a, nombre):
        return next(ast.literal_eval(n.value) for n in a.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == nombre for t in n.targets))
    assert constante(caso, "IND") == constante(sintaxis, "IND") == "    "
    # Caso usa la misma clase de error de sintaxis, no una excepción homónima.
    assert any(isinstance(n, ast.ImportFrom) and n.module == "sintaxis"
               and any(a.name == "ErrorSintaxis" for a in n.names) for n in caso.body)
    print("N2: _indentada y _fallar idénticas, mismo IND y ErrorSintaxis; 10 → import de 1; ahorro 9")
    print("OK: nueve hallazgos comprobados; ninguna fuente de nucleo/ o tools/ escrita")


if __name__ == "__main__":
    main()
