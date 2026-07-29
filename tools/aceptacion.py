"""La prueba de aceptación del marco: **el corpus juzga al oráculo, no al revés.**

    python tools/aceptacion.py

Criterio 4 de la especificación, ejecutable:

  · todo caso que **declara** una medida tiene que ponerse en **ROJO** con esa medida. Si sale verde,
    la medida está mal escrita o falta lenguaje — y hay que decir cuál;
  · los casos con `sin_medida_todavia` **quedan verdes a propósito**: son el hueco declarado. Su
    número es una métrica del marco y tiene que bajar;
  · y al final corre el nivel L2: las medidas del catálogo servidas **como relación**, medidas por
    una medida. Sin mecanismo nuevo — es lo que vuelve esto un metalenguaje.

Sale != 0 si algún caso que debía ponerse rojo salió verde.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402  registra las escalares declaradas
from nucleo.medida import cargar_catalogo, como_hechos  # noqa: E402


def casos() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((RAIZ / "corpus").rglob("*.json"))]


def main() -> int:
    catalogo = cargar_catalogo(RAIZ / "catalogos")
    todos = casos()
    fallas: list[str] = []
    rojos = 0
    huecos: list[str] = []

    print(f"catálogo: {len(catalogo)} medidas · corpus: {len(todos)} casos\n")

    for c in todos:
        mid = c.get("medida")
        if not mid:
            huecos.append(f"{c['id']} — {c.get('sin_medida_todavia', '')[:70]}")
            continue
        if mid not in catalogo:
            fallas.append(f"{c['id']}: reclama la medida «{mid}» y no está en el catálogo")
            continue

        v = catalogo[mid].evaluar(c["evidencia"])
        if v.ok:
            fallas.append(f"{c['id']}: la medida «{mid}» salió VERDE y el caso es un defecto real "
                          f"(valor {v.valor}, umbral {v.umbral}) — medida mal escrita o falta lenguaje")
        else:
            rojos += 1
            print(f"  ROJO  {c['id']:<38} {mid}  (valor {v.valor})")

    print(f"\ncasos que se pusieron rojos: {rojos} · huecos declarados: {len(huecos)}")
    for h in huecos:
        print(f"  hueco  {h}")

    # ---- L2: medir las medidas con el mismo álgebra ----
    print("\nnivel L2 — el catálogo servido como relación:")
    evidencia_meta = {"medida": como_hechos(catalogo.values())}
    for mid, m in sorted(catalogo.items()):
        if not mid.startswith("meta.") or m.tuberia[1][1] != "medida":
            continue
        v = m.evaluar(evidencia_meta)
        print(" ", v.linea())
        if not v.ok:
            fallas.append(f"{mid}: el catálogo no cumple su propia regla meta")

    if fallas:
        print(f"\nACEPTACIÓN ✗ — {len(fallas)} problema(s)")
        for f in fallas:
            print("  ·", f)
        return 1
    print(f"\nACEPTACIÓN ✓ — los {rojos} casos con medida se ponen en rojo; "
          f"{len(huecos)} huecos declarados sin tapar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
