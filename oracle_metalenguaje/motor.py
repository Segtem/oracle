"""Fachada estable para incrustar Oracle sin depender de sus herramientas CLI."""

from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from pathlib import Path

import importlib

from nucleo.algebra import (ESCALARES, ErrorDeAlgebra, LimitesAlgebra,
                            RegistroEscalares, limites_predeterminados,
                            validar_resumen, validar_tuberia)
from nucleo.medida import (Informe, Medida, cargar_catalogo, evaluar,
                           medidas_aplicables)
from nucleo.proyecto import (Proyecto, ProyectoInvalido, catalogos_a_cargar,
                             escalares_del_proyecto, macros_del_proyecto,
                             problemas_estructura)


class ErrorDeMotor(ValueError):
    """La configuración del motor no permite producir un veredicto válido."""


class SinMedidasAplicables(ErrorDeMotor):
    """La evidencia no satisface las relaciones de entrada de ninguna medida."""


_REGISTRO_BASE: RegistroEscalares | None = None


def registro_base() -> RegistroEscalares:
    """Copia independiente de las escalares universales, capturadas al primer uso.

    Antes esto era `import catalogos` más un dict, los dos a nivel de módulo. Como
    `tests/test_motor.py` importa el paquete al tope, el decorador `@escalar` corría durante el
    **descubrimiento** de la suite: once mutantes de `escalar()`, `_registro()` y
    `_contrato_de_escalar()` rompían la importación y el arnés los reportaba como «error» en vez de
    «muerte». Eran los últimos que quedaban sin veredicto.

    El filtro por `__module__` hace que el orden no importe: se capturan las del catálogo base y
    ninguna otra, aunque el consumidor ya haya declarado las suyas en el registro global.
    """
    global _REGISTRO_BASE
    if _REGISTRO_BASE is None:
        importlib.import_module("catalogos")   # declara las escalares universales
        _REGISTRO_BASE = RegistroEscalares({
            nombre: fn for nombre, fn in ESCALARES.items()
            if getattr(fn, "__module__", "").endswith("catalogos.escalares")
        })
    return _REGISTRO_BASE.copiar()


def _limites_propios(limites: LimitesAlgebra | None) -> LimitesAlgebra:
    if limites is None:
        # Se llama, no se importa: importar el valor al tope volvería a construirlo durante el
        # import de este módulo, que es justo lo que se sacó de `nucleo.algebra`.
        return limites_predeterminados()
    if not isinstance(limites, LimitesAlgebra):
        raise ErrorDeAlgebra("`limites` debe ser una instancia de LimitesAlgebra")
    return limites


def _registro_propio(registro: RegistroEscalares | None) -> RegistroEscalares:
    if registro is None:
        return registro_base()
    if not isinstance(registro, RegistroEscalares):
        raise ErrorDeMotor("`registro` debe ser una instancia de RegistroEscalares")
    return registro.copiar()


class Motor:
    """Evaluador reusable con catálogo, UDF y límites propiedad de una instancia."""

    __slots__ = ("_medidas", "_registro", "limites", "proyecto")

    _medidas: tuple[Medida, ...]
    _registro: RegistroEscalares
    limites: LimitesAlgebra
    proyecto: Path | None

    def __new__(cls, *args, **kwargs):
        raise ErrorDeMotor("usá Motor.desde_datos, desde_medidas o desde_proyecto")

    def __setattr__(self, nombre, valor):
        raise AttributeError("Motor es inmutable; construí otra instancia")

    @classmethod
    def _crear(cls, medidas: Iterable[Medida], registro: RegistroEscalares,
               limites: LimitesAlgebra, proyecto: Path | None = None) -> "Motor":
        recibidas = tuple(medidas)
        if any(not isinstance(medida, Medida) for medida in recibidas):
            raise ErrorDeMotor("todas las medidas deben ser instancias de Medida")
        declaradas = tuple(deepcopy(medida) for medida in recibidas)
        ids = [medida.id for medida in declaradas]
        repetidos = sorted({mid for mid in ids if ids.count(mid) > 1})
        if repetidos:
            raise ErrorDeMotor(f"ids de medida repetidos: {repetidos}")
        for medida in declaradas:
            validar_tuberia(medida.tuberia, limites, registro=registro)
            validar_resumen(medida.resumen, limites, registro=registro)

        motor = object.__new__(cls)
        object.__setattr__(motor, "_medidas", declaradas)
        object.__setattr__(motor, "_registro", registro)
        object.__setattr__(motor, "limites", limites)
        object.__setattr__(motor, "proyecto", proyecto)
        return motor

    @classmethod
    def desde_medidas(cls, medidas: Iterable[Medida], *,
                      registro: RegistroEscalares | None = None,
                      limites: LimitesAlgebra | None = None) -> "Motor":
        """Construye un motor desde objetos ya declarados, sin tocar el filesystem."""
        return cls._crear(
            medidas,
            _registro_propio(registro),
            _limites_propios(limites),
        )

    @classmethod
    def desde_datos(cls, medidas: Iterable[list], *,
                    registro: RegistroEscalares | None = None,
                    limites: LimitesAlgebra | None = None) -> "Motor":
        """Construye desde las formas JSON del lenguaje mantenidas en memoria."""
        registro_propio = _registro_propio(registro)
        limites_propios = _limites_propios(limites)
        declaradas = tuple(
            Medida.de_datos(datos, registro=registro_propio, limites=limites_propios)
            for datos in medidas
        )
        return cls._crear(declaradas, registro_propio, limites_propios)

    @classmethod
    def desde_proyecto(cls, ruta, *, confiar_escalares: bool = False,
                       limites: LimitesAlgebra | None = None,
                       raices_perfiles=()) -> "Motor":
        """Carga un proyecto explícito; nunca consulta argv, cwd ni variables de entorno."""
        if not isinstance(confiar_escalares, bool):
            raise ErrorDeMotor("`confiar_escalares` debe ser booleano")
        raiz = Path(ruta).expanduser().resolve()
        proy = Proyecto(raiz)
        fallas = problemas_estructura(proy, ("catalogos",))
        if fallas:
            raise ProyectoInvalido(f"{raiz} no parece un proyecto: {'; '.join(fallas)}")

        registro = registro_base()
        limites_propios = _limites_propios(limites)
        macros = macros_del_proyecto(proy)
        with escalares_del_proyecto(
                proy, confiar=confiar_escalares, registro=registro):
            catalogo = cargar_catalogo(
                catalogos_a_cargar(proy, raices_perfiles=raices_perfiles),
                registro=registro,
                limites=limites_propios,
                macros=macros,
            )
        return cls._crear(
            catalogo.values(), registro, limites_propios, proyecto=raiz)

    @property
    def medidas(self) -> tuple[Medida, ...]:
        return deepcopy(self._medidas)

    @property
    def escalares(self) -> tuple[str, ...]:
        """Inventario inmutable; las funciones concretas quedan encapsuladas."""
        return tuple(sorted(self._registro))

    def evaluar(self, evidencia: dict) -> Informe:
        aplicables = medidas_aplicables(self._medidas, evidencia)
        if not aplicables:
            raise SinMedidasAplicables(
                "ninguna medida es aplicable a las relaciones declaradas en la evidencia")
        return evaluar(
            aplicables,
            evidencia,
            self.limites,
            registro=self._registro,
        )
