"""La versión del álgebra que implementa este núcleo, legible por máquina.

`ESPECIFICACION.md` decía «Versión 0.3» en prosa y el núcleo no la conocía: cada extensión del
lenguaje apagaba un pedazo del diferencial en silencio, porque la implementación de referencia
estaba escrita contra una versión anterior y nadie lo comprobaba. Este módulo es el lugar único
donde el dato vive. De acá lo leen dos consumidores:

- `nucleo/proyecto.py`, para saber si un proyecto pide una versión compatible con la que hay;
- `tools/generar_diferencial.py`, para saber si la referencia se escribió contra esta versión.

La regla sobre qué cambio sube qué parte del número está en `ESPECIFICACION.md` §0. Acá sólo vive la
maquinaria de comparar y de fallar cerrado: un `None` o un `False` silencioso es la forma en que un
defecto se disfraza de verde.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

VERSION_ALGEBRA = "0.3"

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
    """La versión que este núcleo implementa, ya parseada."""
    return parsear(VERSION_ALGEBRA)


def compatible(necesitada: Version, disponible: Version) -> bool:
    """Un consumidor funciona si el núcleo es de la MISMA mayor y de menor igual o posterior.

    La menor sube al AGREGAR (nadie que no use lo nuevo se rompe); la mayor sube al CAMBIAR el
    significado de lo existente (rompe a todos). Por eso basta con exigir la misma mayor y una menor
    al menos tan nueva como la pedida.
    """
    return necesitada.mayor == disponible.mayor and necesitada.menor <= disponible.menor
