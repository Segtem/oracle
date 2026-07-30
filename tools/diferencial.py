"""La prueba diferencial: el álgebra contra una implementación independiente.

    python tools/diferencial.py

`diferencial/geometria.json` lo produce Jam corriendo sus oráculos de colocación y snap escritos a
mano — código que no comparte una línea con este álgebra. Acá se re-juzga la misma evidencia con las
medidas del catálogo y se comparan los veredictos, uno por uno.

Es la única forma de saber si las medidas de geometría dicen lo que creen decir: nadie de este lado
las escribió mirando la otra implementación, y el archivo es datos, no una dependencia.

Sale != 0 ante cualquier desacuerdo.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos  # noqa: F401,E402  registra las escalares de todos los dominios
from nucleo.medida import cargar_catalogo  # noqa: E402


def main() -> int:
    fixtures = sorted((RAIZ / "diferencial").glob("*.json"))
    if not fixtures:
        print("no hay fixtures en diferencial/ — los genera `tools/emitir_diferencial.py` en Jam")
        return 1

    catalogo = cargar_catalogo(RAIZ / "catalogos")
    fallas: list[str] = []
    total = 0

    for f in fixtures:
        datos = json.loads(f.read_text(encoding="utf-8"))
        print(f"{f.name} · {datos['mundos']} mundos · origen: {datos['origen']}\n")
        for mid, casos in sorted(datos["grupos"].items()):
            if mid not in catalogo:
                fallas.append(f"{mid}: el fixture la reclama y no está en el catálogo")
                continue
            medida = catalogo[mid]
            desacuerdos = []
            for i, caso in enumerate(casos):
                v = medida.evaluar(caso["evidencia"])
                total += 1
                if v.ok != caso["esperado_ok"]:
                    desacuerdos.append((i, v.valor, caso["esperado_ok"]))
            verdes = sum(1 for c in casos if c["esperado_ok"])
            marca = "✓" if not desacuerdos else "✗"
            print(f"  {marca} {mid:<32} {len(casos):>4} casos "
                  f"({verdes} verdes / {len(casos) - verdes} rojos) · "
                  f"{len(desacuerdos)} desacuerdos")
            for i, valor, esperado in desacuerdos[:5]:
                fallas.append(f"{mid}[{i}]: el álgebra dio {valor} "
                              f"y la otra implementación esperaba ok={esperado}")

    if fallas:
        print(f"\nDIFERENCIAL ✗ — {len(fallas)} desacuerdo(s)")
        for x in fallas[:20]:
            print("  ·", x)
        return 1
    print(f"\nDIFERENCIAL ✓ — {total} veredictos coinciden con la implementación independiente")
    return 0


if __name__ == "__main__":
    sys.exit(main())
