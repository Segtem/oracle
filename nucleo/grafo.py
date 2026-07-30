"""Cierre transitivo — del lado del SENSOR, no del álgebra.

La especificación tenía abierta la recursión: «alcanzable desde» no se expresa con los operadores, y
es la misma pared que hizo falta `WITH RECURSIVE` en SQL.

## La decisión: no entra al álgebra

Agregar un operador `cierre` habría sido meter recursión en un lenguaje que se mantiene chico a
propósito, con **un solo usuario** — justo lo que la regla del repositorio prohíbe. Y hay una salida
que además es más fiel a la doctrina: **la alcanzabilidad es un HECHO**, y producir hechos es trabajo
del sensor.

    alcanzable(desde, hasta, saltos)

El álgebra la mide como cualquier otra relación, sin saber nada de grafos. El sensor la calcula, y
oracle pone el ayudante para que ningún sensor tenga que reimplementar un BFS — que era el otro riesgo,
el de acumular la misma función en cada dominio.

No es una evasión: es la misma línea que separa al sensor del juez en todo lo demás. El sensor mira el
mundo y no opina; el álgebra opina y no mira el mundo.
"""

from __future__ import annotations

from collections import deque


def cierre(aristas, semillas, desde: str = "a", hacia: str = "b") -> list[dict]:
    """`alcanzable(desde, hasta, saltos)` — a qué llega cada semilla, y en cuántos saltos.

    `aristas` son hechos con dos campos (por omisión `a` → `b`). Incluye la semilla misma con cero
    saltos: si no, «alcanzable desde X» excluiría a X y toda medida que cuente tendría que sumarle uno
    a mano.

    Un ciclo no cuelga: se visita cada nodo una vez.
    """
    vecinos: dict[str, list[str]] = {}
    for e in aristas:
        vecinos.setdefault(e[desde], []).append(e[hacia])

    salida: list[dict] = []
    for semilla in semillas:
        vistos = {semilla: 0}
        cola = deque([semilla])
        while cola:
            n = cola.popleft()
            for m in vecinos.get(n, ()):
                if m not in vistos:
                    vistos[m] = vistos[n] + 1
                    cola.append(m)
        salida += [{"desde": semilla, "hasta": n, "saltos": k} for n, k in sorted(vistos.items())]
    return salida
