"""La versión del álgebra y de la superficie que implementa este núcleo, legible por máquina.

`ESPECIFICACION.md` decía «Versión 0.3» en prosa y el núcleo no la conocía: cada extensión del
lenguaje apagaba un pedazo del diferencial en silencio, porque la implementación de referencia
estaba escrita contra una versión anterior y nadie lo comprobaba. Este módulo es el lugar único
donde los datos viven. De acá los leen los consumidores:

- `nucleo/proyecto.py`, para saber si un proyecto pide una versión compatible con la que hay;
- `tools/generar_diferencial.py`, para saber si la referencia se escribió contra esta versión;
- `nucleo/medida.py` y `nucleo/macro.py`, para comprobar que un `.oracle` guardado no declare una
  sintaxis que este núcleo ya no lee igual.

La regla sobre qué cambio sube qué parte de cada número está en `ESPECIFICACION.md` §0. Acá sólo
vive la maquinaria de comparar y de fallar cerrado: un `None` o un `False` silencioso es la forma en
que un defecto se disfraza de verde.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Tres versiones, y son tres cosas distintas a propósito: unificarlas mentiría. El álgebra versiona
# lo que una medida SIGNIFICA; la sintaxis versiona cómo se ESCRIBE (un `.oracle` se lee, y el
# impresor no lo toca, así que no envejecen juntas); y la distribución versiona el paquete que se
# instala, que cambia cada vez que se arregla una herramienta sin tocar el lenguaje.
VERSION_DISTRIBUCION = "0.1.0"

VERSION_ALGEBRA = "0.3"

# La superficie infija declara su versión por separado: no envejece igual que el álgebra, porque un
# archivo `.oracle` se LEE y el impresor no lo toca. La regla de qué sube cada parte está en
# `ESPECIFICACION.md` §0; acá sólo vive el dato y la misma maquinaria que el álgebra.
VERSION_SINTAXIS = "0.1"

_VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


class VersionInvalida(ValueError):
    """Una versión ilegible o incompatible con la que este núcleo implementa."""


@dataclass(frozen=True)
class Version:
    """`MAYOR.MENOR`: dos enteros no negativos. La semántica está en ESPECIFICACION.md §0."""

    mayor: int
    menor: int

    def __str__(self) -> str:
        return f"{self.mayor}.{self.menor}"


def parsear(texto) -> Version:
    """Convierte un texto en una versión o falla cerrado con la causa."""
    if not isinstance(texto, str):
        raise VersionInvalida(f"la versión debe ser un texto, no {type(texto).__name__}")
    m = _VERSION_RE.fullmatch(texto)
    if m is None:
        raise VersionInvalida(
            f"versión «{texto!r}» inválida: se espera MAYOR.MENOR con enteros no negativos")
    return Version(int(m.group(1)), int(m.group(2)))


def del_nucleo() -> Version:
    """La versión del álgebra que este núcleo implementa, ya parseada."""
    return parsear(VERSION_ALGEBRA)


def del_nucleo_sintaxis() -> Version:
    """La versión de la superficie que este núcleo implementa, ya parseada."""
    return parsear(VERSION_SINTAXIS)


def exigir_sintaxis_compatible(declarada: str | None) -> None:
    """Fail-closed: si una superficie declara contra qué sintaxis se escribió, tiene que ser
    compatible con la que implementa este núcleo. No declarar nada sigue cargando."""
    if declarada is None:
        return
    necesitada = parsear(declarada)
    disponible = del_nucleo_sintaxis()
    if not compatible(necesitada, disponible):
        raise VersionInvalida(
            f"la superficie declara la sintaxis {necesitada} y este núcleo implementa "
            f"{disponible}; un archivo que declara una versión incompatible no carga")


def compatible(necesitada: Version, disponible: Version) -> bool:
    """Un consumidor funciona si el núcleo es de la MISMA mayor y de menor igual o posterior.

    La menor sube al AGREGAR (nadie que no use lo nuevo se rompe); la mayor sube al CAMBIAR el
    significado de lo existente (rompe a todos). Por eso basta con exigir la misma mayor y una menor
    al menos tan nueva como la pedida.
    """
    return necesitada.mayor == disponible.mayor and necesitada.menor <= disponible.menor
