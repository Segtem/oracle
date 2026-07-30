"""Muta las medidas y mide el resultado CON LAS MEDIDAS. El bucle se cierra acá.

    python tools/mutar.py            → informe
    python tools/mutar.py --hechos   → volcar la evidencia producida (JSON)

El sensor produce hechos; el álgebra los juzga. Ninguna lógica de veredicto vive en el sensor, que es
lo que permite que la misma medida —`proceso.test_con_mutante_que_lo_mata`— sirva para los mutantes de
Jam y para los del propio oráculo.

Sale != 0 si algún mutante sobrevivió, porque un mutante que sobrevive es un aspecto de la medida que
el corpus no fija.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402
from nucleo.medida import cargar_catalogo  # noqa: E402
from nucleo.mutacion import correr  # noqa: E402


def casos() -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((RAIZ / "corpus").rglob("*.json"))]


def main() -> int:
    catalogo = cargar_catalogo(RAIZ / "catalogos")
    evidencia = correr(catalogo, casos())

    if "--hechos" in sys.argv:
        print(json.dumps(evidencia, ensure_ascii=False, indent=2))
        return 0

    mutantes = evidencia["mutante"]
    vivos = [m for m in mutantes if not m["murio"]]
    print(f"mutantes de medida (medida × mutador): {len(mutantes)} · "
          f"murieron {len(mutantes) - len(vivos)} · sobrevivieron {len(vivos)}")
    print(f"detecciones evaluadas (mutante × caso): {len(evidencia['deteccion'])}\n")

    # el bucle: los hechos del sensor, juzgados por la medida del catálogo
    v = catalogo["proceso.test_con_mutante_que_lo_mata"].evaluar(evidencia)
    print(f"juzgado por «{v.id}»:")
    print(f"  {'✗' if not v.ok else '✓'} valor {v.valor}  (umbral {v.umbral})")

    if vivos:
        print("\nlo que el corpus NO fija — ningún caso detecta estas mutaciones:")
        for m in vivos:
            print(f"  · mutar «{m['cambio']}» en {m['apunta_a']} pasa inadvertido")
        print("\nSe tapa agregando un caso que SÍ lo note, no cambiando la medida. Y si un mutante")
        print("no lo puede detectar ninguna polaridad, suele faltar el caso de la otra:")
        print("`quitar_filtro` sólo lo agarra un caso verde; `aflojar_umbral`, sólo uno rojo.")
        return 1

    print("\nTodos los mutantes murieron: el corpus fija las medidas que declara.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
