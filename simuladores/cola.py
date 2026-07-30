"""Simulador de referencia: **una cola y unos servidores**. El caso canónico de GPSS.

Está acá para dejar claro que el modo simulación no es una cosa de juegos. Entidades que llegan,
esperan, las atiende alguien y se van: eso describe una caja de supermercado, una cola de tareas, un
pipeline de build, o los turnos de dos agentes trabajando un repositorio. Ninguno «gana».

El escenario, plano como manda L0:

    {"id": "…", "servidores": 2, "capacidad": 5, "duracion": 40,
     "llega_cada": 2, "atiende_en": 3}

Termina por una de tres razones, y **ninguna de las tres es un veredicto**: si desbordarse está mal
lo dice una medida, no este archivo.

    "fin_de_ventana"  se agotó el tiempo simulado sin rechazar a nadie
    "desborde"        llegó alguien y la cola estaba llena: se lo rechazó

Si al final quedó gente en el sistema es un HECHO del resumen (`quedaron`), no una razón: que eso
esté mal lo decide una medida.
"""

from __future__ import annotations

import random

from nucleo.simulacion import Corrida


def cola_simple(escenario: dict, semilla: int, tope: int) -> Corrida:
    """Determinista dado (escenario, semilla): la semilla sólo mueve la variación de los tiempos."""
    r = random.Random(semilla)
    servidores = int(escenario.get("servidores", 1))
    capacidad = int(escenario.get("capacidad", 5))
    duracion = min(int(escenario.get("duracion", 40)), tope)
    llega_cada = max(1, int(escenario.get("llega_cada", 2)))
    atiende_en = max(1, int(escenario.get("atiende_en", 3)))

    eventos: list[dict] = []
    cola: list[int] = []                 # instante de llegada de cada uno que espera
    ocupados: list[int] = []             # instante en que se libera cada servidor
    cola_maxima = atendidos = rechazados = 0
    esperas: list[int] = []
    razon = "fin_de_ventana"

    for t in range(duracion + 1):
        ocupados = [fin for fin in ocupados if fin > t]

        # ¿llega alguien? la semilla desplaza el ritmo sin romper el determinismo
        if t % llega_cada == r.randrange(llega_cada):
            if len(cola) >= capacidad:
                rechazados += 1
                eventos.append({"t": t, "actor": "cola", "que": "rechaza", "largo": len(cola)})
                razon = "desborde"
                break
            cola.append(t)
            eventos.append({"t": t, "actor": "entidad", "que": "llega", "largo": len(cola)})

        while cola and len(ocupados) < servidores:
            llegada = cola.pop(0)
            esperas.append(t - llegada)
            ocupados.append(t + atiende_en)
            atendidos += 1
            eventos.append({"t": t, "actor": "servidor", "que": "atiende", "espera": t - llegada})

        cola_maxima = max(cola_maxima, len(cola))
    else:
        # Terminó la ventana entera sin desbordar. «vacia» sólo si además drenó: quedarse a mitad
        # con gente esperando NO es lo mismo que haber atendido todo, y confundirlos haría que la
        # medida de desborde diera verde en un sistema que nunca se puso al día.
        eventos.append({"t": duracion, "actor": "cola", "que": "fin_de_ventana",
                        "largo": len(cola)})

    return Corrida(
        eventos=eventos,
        pasos=eventos[-1]["t"] if eventos else 0,
        razon=razon,
        resumen={"cola_maxima": cola_maxima, "atendidos": atendidos, "rechazados": rechazados,
                 "quedaron": len(cola) + len(ocupados),
                 "espera_maxima": max(esperas) if esperas else 0,
                 "espera_promedio": round(sum(esperas) / len(esperas), 2) if esperas else 0.0},
    )
