"""Registra todas las escalares declaradas. Importar `catalogos` alcanza.

Vive acá para que ninguna herramienta tenga que acordarse de importar cada dominio: una escalar sin
registrar hace fallar la medida que la usa, y ese error se ve tarde y confunde.
"""

from . import escalares  # noqa: F401
from .geometria import escalares as _geometria  # noqa: F401
