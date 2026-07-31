"""Frontera común entre errores de proyecto y los códigos de salida de los entry points."""

from __future__ import annotations

import sys

from nucleo.proyecto import ProyectoInvalido, resolver


def resolver_cli(argv: list[str]):
    try:
        return resolver(argv)
    except ProyectoInvalido as e:
        print(f"PROYECTO INVÁLIDO — {e}", file=sys.stderr)
        return None
