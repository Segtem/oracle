#!/usr/bin/env python3
"""Mide qué cantidades de un catálogo consumidor puede derivar L−1 con estas relaciones."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path


RAIZ_ORACLE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_ORACLE))

import catalogos.escalares  # noqa: E402,F401  registra escalares base
from nucleo.medida import cargar_catalogo  # noqa: E402
from nucleo.proyecto import Proyecto, escalares_del_proyecto, macros_del_proyecto  # noqa: E402
from nucleo.relacion import cargar_relaciones  # noqa: E402
from nucleo.unidad import hechos_de_unidades  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("jam", type=Path, help="raíz del repo Jam que contiene medidas/")
    args = parser.parse_args()

    proyecto = Proyecto(args.jam.resolve() / "medidas")
    relaciones = cargar_relaciones(Path(__file__).resolve().parent)
    with escalares_del_proyecto(proyecto, confiar=True):
        catalogo = cargar_catalogo(
            proyecto.catalogos,
            macros=macros_del_proyecto(proyecto),
        )
        filas = hechos_de_unidades(
            catalogo.values(), relaciones=relaciones
        )["cantidad_comparada"]

    derivables = [fila for fila in filas if fila["es_derivable"]]
    pendientes = [fila for fila in filas if not fila["es_derivable"]]
    print(
        f"total={len(filas)} derivables={len(derivables)} "
        f"no_derivables={len(pendientes)}"
    )
    for medida, cantidad in sorted(
        Counter(fila["medida"] for fila in pendientes).items(),
        key=lambda par: (-par[1], par[0]),
    ):
        print(f"{cantidad:2d} {medida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
