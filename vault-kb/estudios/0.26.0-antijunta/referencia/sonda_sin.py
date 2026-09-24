# Sondas de los bordes de `sin` contra el núcleo y la referencia. Desde la raíz: PYTHONPATH=. python3 vault-kb/estudios/0.26.0-antijunta/referencia/sonda_sin.py
import sys
sys.path.insert(0, "diferencial/referencia")
import evaluador as ref
from nucleo.medida import Medida

def m(tub):
    return ["medida", "d.x", tub, ["resumen", "contar", 1], ["umbral", "<=", 0, "r"],
            ["ambito", "del_origen"], ["alcance", "a"]]

def nucleo(datos, ev):
    try:
        v = Medida.de_datos(datos).evaluar(ev)
        return ("ok", v.valor)
    except Exception as e:
        return ("ERR", type(e).__name__)

def referencia(datos, ev):
    try:
        return ("ok", ref.evaluar(datos, ev, {})["valor"])
    except ref.ErrorDeAlgebra:
        return ("ERR", "ErrorDeAlgebra")
    except Exception as e:
        return ("ERR!", type(e).__name__)

EV = {"a": [{"k": 1}, {"k": 2}], "b": [{"k": 1}], "c": [{"k": 1}]}
SONDAS = {
    "fuente unir": m(["desde", ["de", "a", "x"], ["sin", ["unir", ["de", "b", "y"], ["de", "c", "z"]], ["==", ["campo", "y", "k"], ["campo", "x", "k"]]]]),
    "cond no booleana (número)": m(["desde", ["de", "a", "x"], ["sin", ["de", "b", "y"], ["campo", "y", "k"]]]),
    "alias repetido": m(["desde", ["de", "a", "x"], ["sin", ["de", "b", "x"], True]]),
    "alias repetido, izquierda vacía": m(["desde", ["de", "a", "x"], ["donde", False], ["sin", ["de", "b", "x"], True]]),
    "sin como fuente": m(["desde", ["sin", ["de", "b", "y"], True]]),
    "sin con 2 elementos": m(["desde", ["de", "a", "x"], ["sin", ["de", "b", "y"]]]),
    "alias de sin leído después": m(["desde", ["de", "a", "x"], ["sin", ["de", "b", "y"], False], ["donde", ["==", ["campo", "y", "k"], 1]]]),
    "cond literal true": m(["desde", ["de", "a", "x"], ["sin", ["de", "b", "y"], True]]),
    "alias igual a col de agrupar": m(["desde", ["de", "a", "x"], ["agrupar", [["y", ["campo", "x", "k"]]], []], ["sin", ["de", "b", "y"], True]]),
}
for n, d in SONDAS.items():
    a, b = nucleo(d, EV), referencia(d, EV)
    print(("  " if a == b else "≠ ") + f"{n}: núcleo {a} · referencia {b}")
print("--- donde")
for n, d in {"donde número": m(["desde", ["de", "a", "x"], ["donde", ["campo", "x", "k"]]]),
             "unir alias repetido izquierda vacía": m(["desde", ["unir", ["de", "a", "x"], ["de", "b", "x"]]])}.items():
    a, b = nucleo(d, EV), referencia(d, EV)
    print(("  " if a == b else "≠ ") + f"{n}: núcleo {a} · referencia {b}")
