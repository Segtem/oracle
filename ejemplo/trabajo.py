"""Ejemplo mínimo: **un trabajo que consume un presupuesto**. No es un dominio, es un banco de pruebas.

Existe por una sola razón: las medidas neutrales de simulación necesitan evidencia para quedar
fijadas, y esa evidencia tiene que salir de correr algo. Es deliberadamente abstracto —no hay
jugadores, ni colas, ni piezas— porque cualquier cosa más concreta volvería a meter un dominio
particular en la herramienta.

    escenario = {"id": "…", "trabajo": 20, "rinde": 3, "presupuesto": 10}

Termina por «completado» o por «tope», y ninguna de las dos es un veredicto.
"""

from __future__ import annotations

import random

from nucleo.simulacion import Corrida


def trabajo_con_presupuesto(escenario: dict, semilla: int, tope: int) -> Corrida:
    """Determinista dado (escenario, semilla): la semilla sólo mueve cuánto rinde cada paso."""
    r = random.Random(semilla)
    falta = int(escenario.get("trabajo", 10))
    rinde = max(1, int(escenario.get("rinde", 2)))
    presupuesto = min(int(escenario.get("presupuesto", 10)), tope)

    eventos = [{"t": 0, "actor": "trabajo", "que": "empieza", "falta": falta}]
    for t in range(1, presupuesto + 1):
        hecho = r.randint(1, rinde)
        falta -= hecho
        eventos.append({"t": t, "actor": "trabajo", "que": "avanza", "falta": max(0, falta)})
        if falta <= 0:
            return Corrida(eventos, pasos=t, razon="completado", resumen={"sobro": presupuesto - t})
    eventos.append({"t": presupuesto, "actor": "trabajo", "que": "tope", "falta": falta})
    return Corrida(eventos, pasos=presupuesto, razon="tope", resumen={"falto": falta})


def sin_usar_la_semilla(escenario: dict, semilla: int, tope: int) -> Corrida:
    """Roto a propósito: ignora la semilla. Sirve para OBSERVAR el no-determinismo en vez de
    inventarlo, que es lo que fija `simulacion.corrida_reproducible`."""
    return Corrida([{"t": 0, "actor": "x", "que": f"azar:{random.randrange(10**6)}"}],
                   pasos=1, razon="completado")


def con_la_traza_agujereada(escenario: dict, semilla: int, tope: int) -> Corrida:
    """Roto a propósito: no registra un paso. La traza queda con un hueco y sigue pareciendo sana —
    sirve para fijar la medida de orden con una observación en vez de con evidencia inventada."""
    entera = trabajo_con_presupuesto(escenario, semilla, tope)
    return Corrida([e for e in entera.eventos if e["t"] != 1],
                   pasos=entera.pasos, razon=entera.razon, resumen=entera.resumen)
