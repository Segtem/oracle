"""Sólo para medir lo que queda detrás del primer hueco: pasa el nodo ambito detrás de alcance."""
import importlib.util, sys
_s = importlib.util.spec_from_file_location("codex08_real", __import__("pathlib").Path(__file__).with_name("evaluador.py"))
_m = importlib.util.module_from_spec(_s); sys.modules["codex08_real"] = _m; _s.loader.exec_module(_m)
ErrorDeAlgebra = _m.ErrorDeAlgebra
VERSION_ALGEBRA = _m.VERSION_ALGEBRA
def evaluar(medida, evidencia, escalares):
    if isinstance(medida, list):
        amb = [n for n in medida if isinstance(n, list) and n[:1] == ["ambito"]]
        resto = [n for n in medida if not (isinstance(n, list) and n[:1] == ["ambito"])]
        medida = resto + amb
    return _m.evaluar(medida, evidencia, escalares)
