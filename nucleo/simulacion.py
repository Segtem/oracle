"""Modo simulación — la segunda fuente de evidencia, y la mitad GPSS del asunto.

Hasta acá el oráculo consulta **hechos estáticos**: piezas colocadas, documentos, mutantes. GPSS hace
otra cosa: **corre el sistema y reporta lo que pasó**. Eso da una clase de evidencia que la primera
mitad no puede producir.

## No es otro oráculo: es otro sensor

Una traza es una relación. Los mismos operadores la miden, no hace falta un álgebra nueva:

    evento(corrida, t, actor, que, …)                          lo que fue pasando
    corrida(id, escenario, semilla, pasos, razon, determinista)  cómo terminó

El simulador **no juzga**. Devuelve hechos, igual que cualquier sensor. Lo que decide si el resultado
está bien son medidas declaradas, con su umbral y su punto ciego, como todas las demás.

## Por qué esta mitad importa

Es la más difícil de sastrear. Un umbral se afloja cambiando un número; **lo que emerge de correr el
sistema, no**. Una propiedad estática se cumple o no; una simulación te dice qué pasó *de verdad* con
un presupuesto finito y sin información perfecta.

Y produce el desacuerdo que más enseña: **«es posible» y «pasa» no son lo mismo.** Un resolvedor con
información perfecta contesta la primera; un proceso con recursos limitados contesta la segunda. Los
escenarios donde difieren son los que hay que mirar, y ningún oráculo de propiedad puede verlos.

El dominio es indiferente: una cola con servidores, un recorrido sobre una topología, o los turnos de
dos agentes trabajando un repositorio. Ninguno «gana» — todos **terminan por una razón**.

## Determinismo: el runner lo comprueba, no lo promete

Una corrida no reproducible no puede ser material de corpus: mañana da otra cosa y el caso deja de
significar algo. Así que **cada corrida se ejecuta dos veces con la misma semilla** y si las trazas no
son idénticas, `determinista` sale `false` — un hecho más, que juzga una medida. No es una promesa del
docstring: es evidencia.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class Corrida:
    """Lo que devuelve un simulador. Hechos, no veredictos.

    **No hay campo `ganó`, y es a propósito.** Una corrida termina por una `razon`; si esa razón es
    aceptable lo decide una MEDIDA, no el sensor. La primera versión de este archivo tenía `gano:
    bool` y era un concepto de juego metido adentro del contrato — el mismo error que meter un `if`
    en un sensor. Un simulador de una cola de trabajo no «gana»; termina porque se vació, porque se
    desbordó, o porque se acabó el presupuesto de pasos.

    `resumen` lleva los hechos escalares propios del dominio (largo máximo de la cola, celdas
    visitadas, lo que sea): se copian tal cual a la relación `corrida`.
    """

    eventos: list[dict] = field(default_factory=list)
    pasos: int = 0
    razon: str = ""            # por qué terminó: «vacia», «tope», «atascado», «meta»…
    resumen: dict = field(default_factory=dict)


#  (escenario, semilla, tope_de_pasos) → Corrida
Simulador = Callable[[dict, int, int], Corrida]


class SimuladorMalContratado(ValueError):
    """El simulador no devolvió lo que el contrato pide."""


def _revisar(c) -> Corrida:
    if not isinstance(c, Corrida):
        raise SimuladorMalContratado(f"un simulador devuelve `Corrida`, no {type(c).__name__}")
    for k, v in c.resumen.items():
        if not isinstance(v, (str, int, float, bool, type(None))):
            raise SimuladorMalContratado(f"resumen.{k} no es escalar: `corrida` es una relación L0")
    for i, e in enumerate(c.eventos):
        if not isinstance(e, dict) or "t" not in e or "que" not in e:
            raise SimuladorMalContratado(f"evento[{i}] tiene que ser un hecho con `t` y `que`")
        for k, v in e.items():
            if not isinstance(v, (str, int, float, bool, type(None))):
                raise SimuladorMalContratado(
                    f"evento[{i}].{k} no es escalar: la traza es una relación L0")
    return c


def correr(simulador: Simulador, escenarios: list[dict], semillas: list[int],
           tope: int = 500, con_traza: bool = True) -> dict:
    """Corre el simulador sobre cada (escenario, semilla) y devuelve EVIDENCIA.

    Cada combinación se ejecuta **dos veces**: si las dos trazas no coinciden, la corrida se marca
    como no determinista y eso queda como hecho para que lo juzgue una medida.
    """
    corridas, eventos = [], []
    for escenario in escenarios:
        eid = escenario.get("id", "?")
        for semilla in semillas:
            a = _revisar(simulador(escenario, semilla, tope))
            b = _revisar(simulador(escenario, semilla, tope))
            determinista = (a.eventos == b.eventos and a.pasos == b.pasos
                            and a.razon == b.razon and a.resumen == b.resumen)

            cid = f"{eid}·s{semilla}"
            corridas.append({"id": cid, "escenario": eid, "semilla": semilla,
                             "pasos": int(a.pasos), "razon": a.razon,
                             "determinista": determinista, **a.resumen})
            if con_traza:
                for e in a.eventos:
                    eventos.append({"corrida": cid, **e})

    salida = {"corrida": corridas}
    if con_traza and eventos:
        salida["evento"] = eventos
    return salida
