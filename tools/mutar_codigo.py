"""Muta el CÓDIGO del núcleo y mide el resultado con las medidas del catálogo.

    python tools/mutar_codigo.py                 → informe
    python tools/mutar_codigo.py --hechos        → volcar la evidencia (JSON)

Toca archivos reales, así que cada mutante se restaura en un `finally` y el caché se limpia antes de
cada corrida de tests. Si el proceso se interrumpe a la fuerza, comprobá `git status` antes de seguir.

Sale != 0 si algún mutante sobrevivió sin estar declarado equivalente: un mutante vivo es código que
ningún test fija.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos  # noqa: F401,E402
from nucleo.medida import cargar_catalogo  # noqa: E402
from nucleo.mutacion_codigo import correr  # noqa: E402
from nucleo.proyecto import (catalogos_a_cargar, registrar_escalares, resolver,
                             sin_bandera)  # noqa: E402

PROY = resolver(sys.argv[1:])
registrar_escalares(PROY)

TESTS = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", ".", "-q"]
EQUIVALENTES = RAIZ / "equivalentes.json"


def main() -> int:
    objetivos = sorted((RAIZ / "nucleo").glob("*.py"))
    equivalentes = {}
    if EQUIVALENTES.exists():
        equivalentes = {e["id"]: e["razon"]
                        for e in json.loads(EQUIVALENTES.read_text(encoding="utf-8"))}

    silencioso = "--hechos" in sin_bandera(sys.argv[1:])
    hechos_previos = []

    def progreso(fila):
        hechos_previos.append(fila)
        if not silencioso:
            marca = "·" if fila["murio"] else "VIVO"
            print(f"  {marca:>4}  {fila['id']:<52} {fila['cambio']}", flush=True)

    if not silencioso:
        print(f"objetivos: {', '.join(p.name for p in objetivos)}\n")

    evidencia = correr(RAIZ, objetivos, TESTS, equivalentes, al_terminar_uno=progreso)

    if silencioso:
        print(json.dumps(evidencia, ensure_ascii=False, indent=2))
        return 0

    vivos = [m for m in evidencia["mutante"] if not m["murio"]]
    eq = evidencia["mutante_equivalente"]
    print(f"\nmutantes: {len(evidencia['mutante'])} · murieron "
          f"{len(evidencia['mutante']) - len(vivos)} · sobrevivieron {len(vivos)} · "
          f"equivalentes declarados: {len(eq)}")

    catalogo = cargar_catalogo(catalogos_a_cargar(PROY))
    for mid in ("proceso.test_con_mutante_que_lo_mata", "proceso.arnes_con_bytecode_frio"):
        v = catalogo[mid].evaluar(evidencia)
        print(f"  {'✓' if v.ok else '✗'} {mid:<44} valor {v.valor} ({v.umbral})")

    if vivos:
        print("\nCÓDIGO QUE NINGÚN TEST FIJA:")
        for m in vivos:
            print(f"  · {m['id']}\n      {m['cambio']}")
        print("\nCada uno es un test que falta, o un mutante equivalente que hay que DECLARAR en")
        print("equivalentes.json con su razón escrita. Declararlo sin razón es una excusa.")
        return 1

    print("\nTodos los mutantes murieron: los tests fijan el código del núcleo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
