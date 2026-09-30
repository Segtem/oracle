"""¿Cuánto de la fijación de las medidas la sostienen defectos reales y cuánto evidencia inventada?

Corre la mutación de medidas de un proyecto tres veces —con todos los casos, sólo con los construidos
o generados, sólo con los observados— y compara qué mutantes mata cada grupo. Un mutante que sólo
matan los casos inventados es fijación que ningún defecto real respalda.

    PYTHONPATH=<raíz de Oracle> python3 procedencia.py --proyecto <ruta> [--confiar-escalares] [--json salida.json]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

from nucleo.medida import cargar_catalogo
from nucleo.mutacion import correr
from nucleo.proyecto import Proyecto, catalogos_a_cargar, escalares_del_proyecto, macros_del_proyecto
from tools.mutar import casos as casos_del_proyecto

FABRICADA = {"construida", "generada"}


def grupo(caso: dict) -> str:
    if "/" in caso["id"]:
        return "diferencial"   # `fixture/medida[escenario]`: un fixture diferencial, no el corpus
    procedencia = caso.get("procedencia")
    if procedencia == "observada":
        return "observada"
    if procedencia in FABRICADA:
        return "fabricada"
    return "sin_declarar"      # un caso del corpus que no dice de dónde salió su evidencia


def muertos(catalogo, casos) -> tuple[set, set]:
    """(muertos por conducta, muertos por conducta o por rechazo del álgebra)."""
    filas = correr(catalogo, casos)["mutante"]
    conducta = {f["id"] for f in filas if f["detecciones_conductuales"]}
    cualquiera = {f["id"] for f in filas if f["detecciones_conductuales"] or f["rechazos_del_algebra"]}
    return conducta, cualquiera


def medir(proy: Proyecto, confiar: bool) -> dict:
    with escalares_del_proyecto(proy, confiar=confiar):
        catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
        todos = casos_del_proyecto(proy, catalogo)
        grupos = ("observada", "fabricada", "sin_declarar", "diferencial")
        por_grupo = {g: [c for c in todos if grupo(c) == g] for g in grupos}
        universo = {f["id"] for f in correr(catalogo, todos)["mutante"]}
        conducta_total, total = muertos(catalogo, todos)
        resultado = {g: muertos(catalogo, cs) for g, cs in por_grupo.items()}

    obs = resultado["observada"][1]
    medidas = {m.split("·")[0] for m in universo}
    con_real = {c["medida"] for c in por_grupo["observada"] if c.get("medida") in catalogo} & medidas
    return {
        "proyecto": str(proy.raiz),
        "casos": {g: len(cs) for g, cs in por_grupo.items()},
        "mutantes": len(universo),
        "muertos_con_todo": len(total),
        "muertos_por_conducta_con_todo": len(conducta_total),
        "muertos_por_grupo": {g: len(resultado[g][1]) for g in grupos},
        # Lo que la mutación da por fijado sin que ningún defecto real lo respalde.
        "muertos_sin_respaldo_de_un_defecto_real": len(total - obs),
        "proporcion_sin_respaldo_real": round(len(total - obs) / len(total), 3) if total else None,
        "medidas": len(medidas),
        "medidas_con_algun_defecto_real": len(con_real),
        "medidas_fijadas_solo_con_inventada": sorted(medidas - con_real),
        "etiquetas_observadas": dict(Counter(c.get("etiqueta") for c in por_grupo["observada"])),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--proyecto", required=True)
    ap.add_argument("--confiar-escalares", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    r = medir(Proyecto(__import__("pathlib").Path(a.proyecto)), a.confiar_escalares)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)
    salida = {k: v for k, v in r.items() if k != "medidas_fijadas_solo_con_inventada"}
    salida["medidas_fijadas_solo_con_inventada"] = len(r["medidas_fijadas_solo_con_inventada"])
    print(json.dumps(salida, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
