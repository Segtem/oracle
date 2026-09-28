"""Emite requisito_medido_por y los ids del catálogo de este proyecto, tal como los ve Oracle.

    PYTHONPATH=<raíz de Oracle> python3 hechos_requisitos.py
"""

import json
from pathlib import Path

from nucleo.proyecto import Proyecto, catalogo_efectivo, macros_del_proyecto
from nucleo.requisito import cargar_requisitos, hechos_de_requisitos

RAIZ = Path(__file__).resolve().parent
proy = Proyecto(RAIZ)
hechos = hechos_de_requisitos(cargar_requisitos(RAIZ / "requisitos").values())
catalogo = catalogo_efectivo(proy, macros=macros_del_proyecto(proy))
print(json.dumps({"requisito_medido_por": hechos["requisito_medido_por"],
                  "medida": [{"id": mid} for mid in sorted(catalogo)]}, ensure_ascii=False, indent=2))
