"""Qué clase de mutante deja vivo el generador de reglas fijas, por tipo de cambio."""
import sys, json
from collections import Counter
from pathlib import Path
from nucleo.generador import GeneracionNoPosible, fabricar_candidatos
from nucleo.mutacion import correr, mutantes
from nucleo.proyecto import ORIGEN_PROYECTO, Proyecto, catalogo_efectivo, escalares_del_proyecto, macros_del_proyecto

tipos, formas = Counter(), Counter()
for ruta, confiar in ((sys.argv[i], True) for i in range(1, len(sys.argv))):
    proy = Proyecto(Path(ruta))
    with escalares_del_proyecto(proy, confiar=confiar):
        cat = catalogo_efectivo(proy, macros=macros_del_proyecto(proy))
        for mid, e in cat.entradas.items():
            if not (e.origen == ORIGEN_PROYECTO or proy.es_el_propio_oracle):
                continue
            m = cat[mid]
            nombres = {n for n, _ in mutantes(m.a_datos())}
            try:
                cands = fabricar_candidatos(m)
            except GeneracionNoPosible as err:
                formas[str(err)[:90]] += 1
                continue
            buenos = []
            for c in cands:
                try:
                    v = m.evaluar(c["evidencia"])
                except Exception:
                    continue
                if c.get("espera") == "sin_evidencia" and v.sin_evidencia or v.ok == (c["etiqueta"] == "verde_correcto") and c.get("espera") != "sin_evidencia":
                    buenos.append(c)
            muertos = {d["cambio"] for d in correr({mid: m}, buenos)["mutante"] if d["detecciones_conductuales"] or d["rechazos_del_algebra"]}
            for n in nombres - muertos:
                tipos[n.split("·")[0].split(":")[0].split("(")[0][:40]] += 1
print("sobrevivientes por tipo:")
for t, n in tipos.most_common(25):
    print(f"  {n:4d}  {t}")
print("no posible:")
for f, n in formas.most_common():
    print(f"  {n:4d}  {f}")
