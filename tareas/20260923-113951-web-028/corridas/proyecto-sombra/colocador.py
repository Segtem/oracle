"""Lógica mínima de colocación de buques para Batalla Naval.

Este script representa el producto bajo análisis: coloca buques en un tablero
de 10x10 y extrae los hechos observables (nivel L0) en formato JSON para que
Oracle pueda juzgarlos de forma independiente.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class CeldaOcupada:
    barco: str
    fila: int
    columna: int


def colocar_buque(
    barco: str,
    fila: int,
    columna: int,
    longitud: int,
    orientacion: str,
    permitir_desborde: bool = False,
) -> list[CeldaOcupada]:
    """Coloca un buque de cierta longitud a partir de (fila, columna).

    orientacion: 'H' (horizontal) o 'V' (vertical).
    Si permitir_desborde es True, omite la validación interna simulando un bug.
    """
    celdas: list[CeldaOcupada] = []
    for i in range(longitud):
        r = fila + (i if orientacion == "V" else 0)
        c = columna + (i if orientacion == "H" else 0)
        if not permitir_desborde:
            if not (0 <= r < 10 and 0 <= c < 10):
                raise ValueError(
                    f"Colocación inválida: {barco} excede el tablero en ({r}, {c})"
                )
        celdas.append(CeldaOcupada(barco=barco, fila=r, columna=c))
    return celdas


def generar_despliegue(con_defecto: bool = False) -> dict[str, list[dict]]:
    """Genera una disposición de buques y retorna los hechos en formato Oracle."""
    flota: list[CeldaOcupada] = []

    # Buque 1: Fragata (3 celdas), posición (1, 2) Horizontal
    flota.extend(colocar_buque("fragata", 1, 2, 3, "H"))

    # Buque 2: Destructor (2 celdas)
    if con_defecto:
        # DEFECTO: colocado en fila 9 Vertical, ocupando celdas (9, 5) y (10, 5).
        # La celda (10, 5) queda fuera de la cuadrícula de 10x10 (índices 0 a 9).
        flota.extend(colocar_buque("destructor", 9, 5, 2, "V", permitir_desborde=True))
    else:
        # CORREGIDO: colocado en fila 8 Vertical, ocupando celdas (8, 5) y (9, 5).
        flota.extend(colocar_buque("destructor", 8, 5, 2, "V", permitir_desborde=False))

    return {
        "celda_ocupada": [asdict(c) for c in flota]
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Colocador de buques con exportación de hechos para Oracle."
    )
    parser.add_argument(
        "--defecto",
        action="store_true",
        help="Simular defecto de colocación con desborde del tablero.",
    )
    parser.add_argument(
        "--exportar",
        type=str,
        metavar="RUTA",
        help="Ruta donde escribir el archivo JSON de hechos.",
    )
    args = parser.parse_args(argv)

    hechos = generar_despliegue(con_defecto=args.defecto)
    salida = json.dumps(hechos, indent=2, ensure_ascii=False)

    if args.exportar:
        with open(args.exportar, "w", encoding="utf-8") as f:
            f.write(salida + "\n")
        print(f"Hechos exportados a {args.exportar}")
    else:
        print(salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
