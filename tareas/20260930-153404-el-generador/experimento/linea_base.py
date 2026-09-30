"""¿Cuánto fija el generador de reglas fijas partiendo de un corpus vacío?

Por medida: mutantes totales, cuántos mata la evidencia que fabrica `fabricar_candidatos` (sin
ningún caso previo), y si la forma no se puede generar. Con `--busqueda` usa además la búsqueda.

    PYTHONPATH=<oracle> python3 linea_base.py --proyecto <ruta> [--confiar-escalares] [--busqueda] [--json f]
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from nucleo.generador import GeneracionNoPosible, evaluar_utilidad, fabricar_candidatos
from nucleo.medida import cargar_catalogo
from nucleo.mutacion import mutantes
from nucleo.proyecto import (ORIGEN_PROYECTO, Proyecto, catalogo_efectivo, escalares_del_proyecto,
                             macros_del_proyecto)


def medir(proy: Proyecto, confiar: bool, busqueda: bool) -> dict:
    filas = []
    with escalares_del_proyecto(proy, confiar=confiar):
        catalogo = catalogo_efectivo(proy, macros=macros_del_proyecto(proy))
        propias = [mid for mid, e in catalogo.entradas.items()
                   if e.origen == ORIGEN_PROYECTO or proy.es_el_propio_oracle]
        for mid in sorted(propias):
            medida = catalogo[mid]
            total = len(mutantes(medida.a_datos()))
            fila = {"medida": mid, "mutantes": total, "no_posible": False, "muertos": 0}
            t0 = time.monotonic()
            try:
                if busqueda:
                    from nucleo.generador import buscar_candidatos
                    candidatos = buscar_candidatos(medida, [])
                else:
                    candidatos = fabricar_candidatos(medida)
                _, utiles = evaluar_utilidad(medida, [], candidatos, catalogo)
                fila["muertos"] = len(set().union(*(m for _, m in utiles))) if utiles else 0
                fila["casos"] = len(utiles)
            except GeneracionNoPosible:
                fila["no_posible"] = True
            fila["segundos"] = round(time.monotonic() - t0, 2)
            filas.append(fila)
    tot = sum(f["mutantes"] for f in filas)
    muertos = sum(f["muertos"] for f in filas)
    return {
        "proyecto": str(proy.raiz), "medidas": len(filas), "mutantes": tot, "muertos": muertos,
        "proporcion": round(muertos / tot, 3) if tot else None,
        "no_posible": sum(f["no_posible"] for f in filas),
        "medidas_enteras": sum(f["muertos"] == f["mutantes"] for f in filas),
        "segundos": round(sum(f["segundos"] for f in filas), 1),
        "filas": filas,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proyecto", required=True)
    ap.add_argument("--confiar-escalares", action="store_true")
    ap.add_argument("--busqueda", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args()
    r = medir(Proyecto(Path(a.proyecto)), a.confiar_escalares, a.busqueda)
    if a.json:
        Path(a.json).write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in r.items() if k != "filas"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
