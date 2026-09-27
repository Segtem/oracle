"""Puente temporal entre el layout del checkout y el namespace único del wheel."""

from __future__ import annotations

import importlib
import importlib.util
import sys


class _MismoModulo:
    """`oracle_metalenguaje.nucleo.X` y `nucleo.X` son el MISMO módulo, en cualquier orden.

    Por dentro, Oracle importa `nucleo.X` (absoluto). Si un consumidor importaba después
    `oracle_metalenguaje.nucleo.X`, Python lo cargaba otra vez con otro nombre: dos copias de cada
    clase, y un `isinstance` que fallaba sin explicación. Este buscador manda el nombre largo al
    corto, sólo cuando el corto es de verdad el paquete de Oracle.
    """

    def __init__(self, paquete: str, nombre: str):
        self.prefijo = f"{paquete}.{nombre}."
        self.nombre = nombre
        self.namespaced = f"{paquete}.{nombre}"

    def find_spec(self, fullname, path=None, target=None):
        if not fullname.startswith(self.prefijo):
            return None
        if sys.modules.get(self.nombre) is not sys.modules.get(self.namespaced):
            return None
        corto = self.nombre + fullname[len(self.namespaced):]
        return importlib.util.spec_from_loader(fullname, _Alias(corto))


class _Alias:
    def __init__(self, corto: str):
        self.corto = corto

    def create_module(self, spec):
        return importlib.import_module(self.corto)

    def exec_module(self, module):
        """El módulo ya se ejecutó con su nombre corto."""


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
    if destino == namespaced and not any(isinstance(b, _MismoModulo) and b.namespaced == namespaced
                                         for b in sys.meta_path):
        sys.meta_path.insert(0, _MismoModulo(paquete, nombre))
    prefijo = modulo.__name__ + "."
    for cargado, hijo in tuple(sys.modules.items()):
        if cargado.startswith(prefijo):
            sys.modules.setdefault(nombre + cargado[len(modulo.__name__):], hijo)
    return modulo
