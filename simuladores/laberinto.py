"""Simulador de referencia: un agente MIOPE caminando una grilla.

Existe para que el modo simulación tenga un consumidor real y chico, y para mostrar la diferencia que
justifica toda esta mitad:

  · `resoluble()` es un BFS — información perfecta, memoria infinita. Contesta **«¿existe camino?»**
  · `agente_miope()` ve sólo sus cuatro vecinos y recuerda dónde estuvo. Contesta **«¿lo encuentra
    alguien que no lo sabe todo, con un presupuesto finito?»**

Eso es un laberinto acá, y es una topología cualquiera en otro lado: un grafo de dependencias que se
puede resolver en teoría y no encuentra el que lo recorre, una configuración alcanzable que nadie
alcanza. El dominio no importa; la diferencia entre «existe» y «se llega» sí.

Los mundos donde los dos difieren son los interesantes: técnicamente ganables, prácticamente no. Un
oráculo de propiedad no puede verlos.

El agente es determinista dado (mundo, semilla): la semilla sólo desempata entre movimientos que le
parecen igual de buenos. Sin eso, ninguna corrida podría entrar al corpus.

Formato del mundo — plano, como manda L0:

    {"id": "…", "ancho": 5, "alto": 5, "muros": "1,1 1,2 2,1", "inicio": "0,0", "meta": "4,4"}
"""

from __future__ import annotations

import random
from collections import deque

from nucleo.simulacion import Corrida

DIRS = (("N", 0, -1), ("S", 0, 1), ("E", 1, 0), ("O", -1, 0))


def _celdas(texto: str) -> set[tuple[int, int]]:
    if not texto:
        return set()
    return {tuple(int(v) for v in par.split(",")) for par in texto.split(" ") if par}


def _punto(texto: str) -> tuple[int, int]:
    x, y = texto.split(",")
    return int(x), int(y)


def _libre(mundo: dict, muros, p) -> bool:
    x, y = p
    return 0 <= x < mundo["ancho"] and 0 <= y < mundo["alto"] and p not in muros


def resoluble(mundo: dict) -> bool:
    """BFS: ¿existe algún camino? Información perfecta — es un oráculo de PROPIEDAD, no de juego."""
    muros = _celdas(mundo.get("muros", ""))
    inicio, meta = _punto(mundo["inicio"]), _punto(mundo["meta"])
    vistos, cola = {inicio}, deque([inicio])
    while cola:
        p = cola.popleft()
        if p == meta:
            return True
        for _, dx, dy in DIRS:
            q = (p[0] + dx, p[1] + dy)
            if q not in vistos and _libre(mundo, muros, q):
                vistos.add(q)
                cola.append(q)
    return False


def agente_miope(mundo: dict, semilla: int, tope: int) -> Corrida:
    """Ve sus cuatro vecinos, recuerda dónde estuvo, y va hacia la meta sin planificar.

    Es a propósito peor que el BFS: **así es como se juega de verdad**. Si prefiere acercarse a la
    meta y todos los vecinos que se acercan ya los visitó, retrocede; si no le queda ninguno, se
    declara atascado. La semilla sólo desempata entre opciones igual de buenas.
    """
    r = random.Random(semilla)
    muros = _celdas(mundo.get("muros", ""))
    meta = _punto(mundo["meta"])
    p = _punto(mundo["inicio"])
    visitados = {p}
    eventos = [{"t": 0, "actor": "agente", "que": "inicio", "donde": f"{p[0]},{p[1]}"}]

    for t in range(1, tope + 1):
        if p == meta:
            return Corrida(eventos, pasos=t - 1, razon="meta",
                           resumen={"visitados": len(visitados)})

        vecinos = [(n, (p[0] + dx, p[1] + dy)) for n, dx, dy in DIRS]
        posibles = [(n, q) for n, q in vecinos if _libre(mundo, muros, q)]
        nuevos = [(n, q) for n, q in posibles if q not in visitados]
        candidatos = nuevos or posibles
        if not candidatos:
            eventos.append({"t": t, "actor": "agente", "que": "atascado",
                            "donde": f"{p[0]},{p[1]}"})
            return Corrida(eventos, pasos=t - 1, razon="atascado",
                           resumen={"visitados": len(visitados)})

        dist = lambda q: abs(q[0] - meta[0]) + abs(q[1] - meta[1])   # noqa: E731
        mejor = min(dist(q) for _, q in candidatos)
        empatados = sorted((n, q) for n, q in candidatos if dist(q) == mejor)
        nombre, p = empatados[r.randrange(len(empatados))]

        visitados.add(p)
        eventos.append({"t": t, "actor": "agente", "que": f"mueve:{nombre}",
                        "donde": f"{p[0]},{p[1]}"})

    eventos.append({"t": tope, "actor": "agente", "que": "tope", "donde": f"{p[0]},{p[1]}"})
    return Corrida(eventos, pasos=tope, razon="tope",
                   resumen={"visitados": len(visitados)})
