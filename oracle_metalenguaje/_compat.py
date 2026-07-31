"""Puente temporal entre el layout del checkout y el namespace único del wheel."""

from __future__ import annotations

import importlib
import importlib.util
import sys


def cargar_interno(nombre: str, paquete: str):
    namespaced = f"{paquete}.{nombre}"
    destino = namespaced if importlib.util.find_spec(namespaced) is not None else nombre
    try:
        modulo = importlib.import_module(destino)
    except ModuleNotFoundError as e:
        if destino != namespaced or e.name != namespaced:
            raise
        modulo = importlib.import_module(nombre)
    sys.modules.setdefault(nombre, modulo)
    prefijo = modulo.__name__ + "."
    for cargado, hijo in tuple(sys.modules.items()):
        if cargado.startswith(prefijo):
            sys.modules.setdefault(nombre + cargado[len(modulo.__name__):], hijo)
    return modulo
