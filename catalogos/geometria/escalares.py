"""Escalares del dominio GEOMETRÍA. El segundo dominio, y existe para probar que el álgebra es
general: si sirve para «un agente construyendo herramientas» y para «piezas en un nivel», que no se
parecen en nada, sirve.

Un hecho `pieza` es plano, como manda L0 — sin objetos ni anidamiento:

    pieza(id, ox, oy, oz, ex, ey, ez, lx, ly, lz, yaw)
          └ origen del AABB ┘ └ semi-extensión ┘ └ pivote ┘

Las cuentas son las mismas que hace el oráculo escrito a mano de Jam. La prueba diferencial
(`diferencial/`) comprueba que dan el MISMO veredicto sobre cientos de mundos generados por esa
implementación independiente; si divergen, esto está mal.
"""

from __future__ import annotations

from nucleo.algebra import escalar

TOL_CM = 1.0            # menos que esto = tocándose, no interpenetrando
MAX_VECINO_CM = 50000.0  # semi-extensión > 500 m = escenografía de fondo (envuelve el mapa)


def _ejes(p: dict):
    return ((p["ox"], p["ex"]), (p["oy"], p["ey"]), (p["oz"], p["ez"]))


@escalar("penetracion", "cm")
def penetracion(a: dict, b: dict, tol: float = TOL_CM) -> float:
    """Profundidad de interpenetración en cm; 0 si están separados (regla del eje separador).

    Devuelve 0 —no negativo— cuando hay un eje que los separa: «tocarse» no es «clavarse», y por eso
    el umbral de la medida puede ser `<= 0` sin tolerancias extra.
    """
    solapes = []
    for (ca, ea), (cb, eb) in zip(_ejes(a), _ejes(b)):
        solape = (ea + eb) - abs(ca - cb)
        if solape <= tol:
            return 0.0
        solapes.append(solape)
    return min(solapes)


@escalar("es_fondo")
def es_fondo(p: dict, max_cm: float = MAX_VECINO_CM) -> bool:
    """¿Es escenografía descomunal (SkySphere, atmósfera)? Sin este filtro cualquier pieza
    «interpenetra» el cielo y toda medida de colocación da rojo siempre."""
    return max(p["ex"], p["ey"], p["ez"]) > max_cm


@escalar("volumen", "cm3")
def volumen(p: dict) -> float:
    return p["ex"] * p["ey"] * p["ez"]


@escalar("desvio_de_grilla", "cm")
def desvio_de_grilla(p: dict, grilla: float) -> float:
    """El peor desvío del PIVOTE respecto de la grilla, sobre los tres ejes."""
    return max(abs(v - round(v / grilla) * grilla) for v in (p["lx"], p["ly"], p["lz"]))


@escalar("desvio_de_paso", "grados")
def desvio_de_paso(valor: float, paso: float) -> float:
    return abs(valor - round(valor / paso) * paso)
