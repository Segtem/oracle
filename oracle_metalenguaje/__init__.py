"""API pública y estable de Oracle como biblioteca incrustable."""

from ._compat import cargar_interno

# `tools` NO se registra acá, y es a propósito: es el nombre de paquete más común que hay en un
# repositorio, y hacerlo desde la fachada le borraba el suyo a cualquier consumidor que importara
# esta biblioteca. Lo registra `tools/__init__.py`, que se carga sólo cuando corre un entry point
# de Oracle. Los otros tres los necesita el núcleo para sus propios imports absolutos.
cargar_interno("nucleo", __name__)
cargar_interno("catalogos", __name__)
cargar_interno("perfiles", __name__)

from nucleo.algebra import ErrorDeAlgebra, LimitesAlgebra, RegistroEscalares, escalar
from nucleo.medida import Informe, Medida, Veredicto
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables,
                             ProyectoInvalido)

from .motor import ErrorDeMotor, Motor, SinMedidasAplicables, registro_base

__all__ = (
    "ErrorDeAlgebra",
    "ErrorDeMotor",
    "EscalaresInvalidas",
    "EscalaresNoConfiables",
    "Informe",
    "LimitesAlgebra",
    "Medida",
    "Motor",
    "ProyectoInvalido",
    "RegistroEscalares",
    "SinMedidasAplicables",
    "Veredicto",
    "escalar",
    "registro_base",
)
