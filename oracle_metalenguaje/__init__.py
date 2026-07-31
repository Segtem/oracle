"""API pública y estable de Oracle como biblioteca incrustable."""

from ._compat import cargar_interno

cargar_interno("nucleo", __name__)
cargar_interno("catalogos", __name__)
cargar_interno("perfiles", __name__)
cargar_interno("tools", __name__)

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
