#!/usr/bin/env python3
"""Censo estático y ejecución instrumentada, sin modificar el checkout original."""
import argparse
import ast
import collections
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
# Los catálogos de los consumidores, en sus repos. Se leen, no se escriben.
HOME = Path.home() / "Dev"
PROYECTOS = {
    "Oracle": ROOT,
    "Ejemplo: primer-valor": ROOT / "ejemplo/primer-valor",
    "Ejemplo: sensor-prosa": ROOT / "ejemplo/sensor-prosa",
    "Ejemplo: seguimiento-tareas": ROOT / "ejemplo/seguimiento-tareas",
    "Jam": HOME / "jam" / "medidas",
    "LyraGASP": HOME / "games" / "unreal" / "LyraGASP" / "medidas",
}
BIBLIOTECA = ROOT / "ejemplo/biblioteca-segtem/oracle_bibliotecas/oracle_biblioteca_segtem_meta_calidad"


def linea(ruta, op, ordinal):
    texto = ruta.read_text(encoding="utf-8")
    patron = re.compile(r'\b' + re.escape(op) + r'\b' if ruta.suffix == '.oracle'
                        else r'"' + re.escape(op) + r'"')
    halladas = [i for i, s in enumerate(texto.splitlines(), 1) if patron.search(s)]
    return halladas[min(ordinal, len(halladas) - 1)] if halladas else 1


def predicados(m):
    for paso in m.tuberia:
        if paso[0] == "donde":
            yield "donde", paso[1]
        elif paso[0] == "sin":
            yield "sin", paso[2]
    for entrada in m.requiere:
        if isinstance(entrada, list):
            yield "requiere", entrada[3]


def retornos_bool(raiz):
    archivo = raiz / "escalares.py"
    if not archivo.exists():
        return set()
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    return {n.name for n in arbol.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and (isinstance(n.returns, ast.Name) and n.returns.id == "bool"
                 or isinstance(n.returns, ast.Constant) and n.returns.value == "bool")}


def sospechas(expr, bools):
    """Nodos usados como condición; operandos de comparación no son predicados."""
    if type(expr) is bool:
        return []
    if not isinstance(expr, list):
        return [expr]
    op = expr[0]
    if op in ("==", "!=", "<", ">", "<=", ">="):
        return []
    if op in ("y", "o", "no"):
        return [n for hijo in expr[1:] for n in sospechas(hijo, bools)]
    if op in bools:
        return []
    return [expr]


def estatico():
    from nucleo.proyecto import (Proyecto, catalogo_efectivo, macros_del_proyecto,
                                 escalares_del_proyecto)
    resultado = {k: {"medidas": 0, "predicados": 0, "medidas_propias": 0,
                      "predicados_propios": 0, "sospechosos": []}
                 for k in PROYECTOS}
    mapa = collections.defaultdict(list)
    for nombre, raiz in PROYECTOS.items():
        bools = retornos_bool(raiz)
        proy = Proyecto(raiz)
        with escalares_del_proyecto(proy, confiar=True):
            catalogo = catalogo_efectivo(proy, macros=macros_del_proyecto(proy))
        for mid, medida in catalogo.items():
            entrada = catalogo.entradas[mid]
            ruta = entrada.ruta
            # Los catálogos heredados se cuentan en el proyecto donde se ejecutan.
            resultado[nombre]["medidas"] += 1
            propia = ruta.is_relative_to(raiz / "catalogos")
            resultado[nombre]["medidas_propias"] += int(propia)
            orden = collections.Counter()
            for op, expr in predicados(medida):
                nlinea = linea(ruta, op, orden[op]); orden[op] += 1
                clave = json.dumps(expr, ensure_ascii=False, sort_keys=True)
                lugar = f"{ruta}:{nlinea}"
                mapa[clave].append((nombre, mid, op, lugar))
                resultado[nombre]["predicados"] += 1
                resultado[nombre]["predicados_propios"] += int(propia)
                # En los lógicos, un hijo no booleano también es sospechoso: la
                # comprobación estática de requiere usa la misma regla recursiva.
                nodos = sospechas(expr, bools)
                if nodos:
                    lugar_sospecha = lugar
                    if ruta.suffix == ".json" and len(nodos) == 1 and isinstance(nodos[0], list):
                        n = nodos[0]
                        if n[0] in ("campo", "col") and isinstance(n[-1], str):
                            contenido = ruta.read_text(encoding="utf-8").splitlines()
                            matches = [i for i, s in enumerate(contenido, 1)
                                       if f'"{n[-1]}"' in s]
                            if len(matches) == 1:
                                lugar_sospecha = f"{ruta}:{matches[0]}"
                    resultado[nombre]["sospechosos"].append(
                        {"medida": mid, "operador": op, "lugar": lugar_sospecha,
                         "nodos": nodos})
                    for nodo in nodos:
                        if isinstance(nodo, list) and nodo[0] in ("campo", "hecho", "col"):
                            # El acceso puede ser operando de «no». Se registra
                            # aparte del valor booleano del predicado completo.
                            k = json.dumps(nodo, ensure_ascii=False, sort_keys=True)
                            mapa[k].append((nombre, mid, "operando-no", lugar_sospecha))
    from nucleo.medida import cargar
    nombre = "Ejemplo: biblioteca-segtem"
    resultado[nombre] = {"medidas": 0, "predicados": 0, "medidas_propias": 0,
                         "predicados_propios": 0, "sospechosos": []}
    for ruta in sorted((BIBLIOTECA / "catalogos").rglob("*.oracle")):
        medida = cargar(ruta)
        resultado[nombre]["medidas"] += 1
        resultado[nombre]["medidas_propias"] += 1
        orden = collections.Counter()
        for op, expr in predicados(medida):
            lugar = f"{ruta}:{linea(ruta, op, orden[op])}"
            orden[op] += 1
            clave = json.dumps(expr, ensure_ascii=False, sort_keys=True)
            mapa[clave].append((nombre, medida.id, op, lugar))
            resultado[nombre]["predicados"] += 1
            resultado[nombre]["predicados_propios"] += 1
            nodos = sospechas(expr, set())
            if nodos:
                resultado[nombre]["sospechosos"].append(
                    {"medida": medida.id, "operador": op, "lugar": lugar,
                     "nodos": nodos})
    return resultado, mapa


def instrumentar(copia):
    a = copia / "nucleo/algebra.py"
    s = a.read_text()
    punto = 'def _exigir_de_en_sin(fuente) -> None:'
    ayuda = '''def _medir_predicado(valor, expr, operador):
    if type(valor) is not bool:
        import json, os
        with open(os.environ["ORACLE_MEDICION_LOG"], "a", encoding="utf-8") as salida:
            salida.write(json.dumps({"proyecto": os.environ.get("ORACLE_MEDICION_PROYECTO"),
                                     "operador": operador, "expr": expr,
                                     "tipo": type(valor).__name__, "valor": repr(valor)},
                                    ensure_ascii=False, sort_keys=True) + "\\n")
    return valor


'''
    assert s.count(punto) == 1
    s = s.replace(punto, ayuda + punto)
    viejo = 'if evaluar_expr(condicion, fila_combinada, limites, registro=registro, ruta=ruta_cond):'
    nuevo = 'if _medir_predicado(evaluar_expr(condicion, fila_combinada, limites, registro=registro, ruta=ruta_cond), condicion, "sin"):'
    assert s.count(viejo) == 1
    s = s.replace(viejo, nuevo)
    viejo = 'return not _evaluar_hijo(expr, 1, fila, escalares)'
    nuevo = 'return not _medir_predicado(_evaluar_hijo(expr, 1, fila, escalares), expr[1], "operando-no")'
    assert s.count(viejo) == 1
    s = s.replace(viejo, nuevo)
    viejo = 'if evaluar_expr(\n            paso[1], f, limites, registro=escalares, ruta=ruta_expr)]'
    nuevo = 'if _medir_predicado(evaluar_expr(\n            paso[1], f, limites, registro=escalares, ruta=ruta_expr), paso[1], "donde")]'
    assert s.count(viejo) == 1
    a.write_text(s.replace(viejo, nuevo))

    m = copia / "nucleo/medida.py"
    s = m.read_text()
    viejo = 'valor = evaluar_expr(condicion, {alias: fila}, limites, registro=registro)\n    if type(valor) is not bool:'
    nuevo = ('valor = evaluar_expr(condicion, {alias: fila}, limites, registro=registro)\n'
             '    from .algebra import _medir_predicado\n'
             '    _medir_predicado(valor, condicion, "requiere")\n'
             '    if type(valor) is not bool:')
    assert s.count(viejo) == 1
    m.write_text(s.replace(viejo, nuevo))


def dinamico(mapa, rapido=False):
    with tempfile.TemporaryDirectory(prefix="oracle-pbool-") as temporal:
        copia = Path(temporal) / "oracle"
        shutil.copytree(ROOT, copia, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__"))
        instrumentar(copia)
        log = Path(temporal) / "predicados.jsonl"
        env = dict(os.environ, ORACLE_MEDICION_LOG=str(log), PYTHONPATH=str(copia))
        corridas = []
        for nombre, raiz in PROYECTOS.items():
            env["ORACLE_MEDICION_PROYECTO"] = nombre
            proyecto = copia / raiz.relative_to(ROOT) if raiz.is_relative_to(ROOT) else raiz
            cmd = [sys.executable, str(copia / "tools/cli.py"), "test", "--rapido",
                   "--confiar-escalares",
                   "--proyecto", str(proyecto)]
            p = subprocess.run(cmd, cwd=copia, env=env, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               timeout=600)
            corridas.append({"proyecto": nombre, "retorno": p.returncode,
                             "aceptacion": [s.strip() for s in p.stdout.splitlines()
                                            if "ACEPTACIÓN " in s],
                             "ultima_salida": p.stdout[-2500:]})
        cmd = [sys.executable, str(copia / "tools/cli.py"), "biblioteca", "verificar",
               str(copia / BIBLIOTECA.relative_to(ROOT))]
        env["ORACLE_MEDICION_PROYECTO"] = "Ejemplo: biblioteca-segtem"
        p = subprocess.run(cmd, cwd=copia, env=env, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=600)
        corridas.append({"proyecto": "Ejemplo: biblioteca-segtem", "retorno": p.returncode,
                         "ultima_salida": p.stdout[-2500:]})
        observados = collections.defaultdict(lambda: {"veces": 0, "valores": set()})
        eventos = 0
        sin_mapa = []
        if log.exists():
            for s in log.read_text().splitlines():
                eventos += 1
                dato = json.loads(s)
                clave = json.dumps(dato["expr"], ensure_ascii=False, sort_keys=True)
                encontrados = 0
                for nombre, mid, op, lugar in mapa.get(clave, []):
                    if op != dato["operador"] or nombre != dato["proyecto"]:
                        continue
                    encontrados += 1
                    k = (nombre, mid, op, lugar)
                    observados[k]["veces"] += 1
                    observados[k]["valores"].add((dato["tipo"], dato["valor"]))
                if not encontrados:
                    sin_mapa.append(dato)
        filas = [{"proyecto": n, "medida": mid, "operador": op, "lugar": lugar,
                  "veces": v["veces"], "valores": sorted(v["valores"])}
                 for (n, mid, op, lugar), v in sorted(observados.items())]
        return corridas, filas, {"eventos": eventos, "sin_mapa": sin_mapa}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-estatico", action="store_true")
    args = ap.parse_args()
    datos, mapa = estatico()
    salida = {"estatico": datos}
    if not args.solo_estatico:
        salida["corridas"], salida["observados"], salida["diagnostico"] = dinamico(mapa)
    print(json.dumps(salida, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
