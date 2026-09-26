"""Forma única de las tres superficies de autoría."""

from __future__ import annotations

from pathlib import Path

from nucleo import caso, relacion, sintaxis
from nucleo.forma import diferencia, sin_comentarios


LECTORES = {
    ".oracle": (sintaxis.leer, sintaxis.imprimir),
    ".caso": (caso.leer, caso.imprimir),
    ".relacion": (relacion.leer, relacion.imprimir),
}


def canonico(ruta: Path, texto: str, *, macros=None) -> str:
    lector, impresor = LECTORES[ruta.suffix]
    if ruta.suffix == ".oracle":
        return impresor(lector(texto, macros=macros), macros=macros)
    return impresor(lector(texto))


def con_comentarios(original: str, normalizado: str) -> str:
    """Conserva cada comentario antes de la misma línea de contenido ordinal.

    El impresor puede mover o fusionar cláusulas; en ese caso el comentario queda en
    su posición relativa dentro del archivo, y los comentarios finales siguen al final.
    """
    comentarios: dict[int, list[str]] = {}
    posicion = 0
    for linea in original.splitlines(keepends=True):
        if linea.lstrip().startswith("#"):
            comentarios.setdefault(posicion, []).append(linea.rstrip("\r\n") + "\n")
        elif linea.strip():
            posicion += 1
    salida = []
    posicion = 0
    for linea in normalizado.splitlines(keepends=True):
        salida.extend(comentarios.pop(posicion, []))
        salida.append(linea)
        if linea.strip():
            posicion += 1
    for pendientes in comentarios.values():
        salida.extend(pendientes)
    return "".join(salida)
