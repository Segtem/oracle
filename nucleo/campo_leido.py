"""Relación del lenguaje `campo_leido` (L2).

Para cada medida del catálogo, emite una fila por cada lectura `["campo", alias, nombre]`
en su forma canónica:
- `medida`: id de la medida
- `relacion`: relación resuelta para el alias (fuentes y requiere condicional), o "" si no resuelve
- `campo`: nombre del campo leído
- `origen`: "declarada" (proyecto), "lenguaje" (núcleo) o "sin_declarar"
- `existe`: si el campo pertenece a la relación; False para "sin_declarar"
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from .medida import Medida
from .relacion import Relacion, campos_de_relaciones_declarados
from .unidad import extraer_alias_de_fuente

RELACIONES_DE_CAMPO_LEIDO = frozenset({"campo_leido"})
AMBITOS_DE_RELACIONES = {"campo_leido": "universal"}
CAMPOS_DE_RELACIONES = {
    "campo_leido": ("medida", "relacion", "campo", "origen", "existe"),
}


def extraer_alias_de_medida(medida: Medida) -> dict[str, str]:
    """Extrae los alias declarados en las fuentes, pasos «sin» y entradas condicionales de requiere."""
    # `Medida.de_datos` ya validó la forma: la tubería trae su fuente, y cada entrada de `requiere` es un
    # nombre o `["filas", relación, alias, condición]`.
    alias_map = extraer_alias_de_fuente(medida.tuberia[1])
    if isinstance(medida.tuberia, list):
        for paso in medida.tuberia[2:]:
            if isinstance(paso, list) and len(paso) >= 3 and paso[0] == "sin":
                alias_map.update(extraer_alias_de_fuente(paso[1]))
    for entrada in medida.requiere:
        if not isinstance(entrada, str):
            alias_map[entrada[2]] = entrada[1]
    return alias_map


def _extraer_lecturas_de_arbol(nodo: Any):
    """Recorre el árbol canónico de la medida buscando ['campo', alias, nombre]."""
    if not isinstance(nodo, list) or not nodo:
        return
    if len(nodo) == 3 and nodo[0] == "campo":  # el álgebra ya validó que alias y nombre son nombres
        yield nodo[1], nodo[2]
        return
    for hijo in nodo:
        yield from _extraer_lecturas_de_arbol(hijo)


def hechos_de_campos_leidos(
    medidas: Iterable[Medida],
    relaciones: Mapping[str, Relacion] | Iterable[Relacion] | None = None,
    raiz: Path | None = None,
) -> dict[str, list[dict]]:
    """Genera los hechos de `campo_leido` para un conjunto de medidas."""
    if isinstance(relaciones, Mapping):
        rel_map = dict(relaciones)
    elif isinstance(relaciones, Iterable):
        rel_map = {r.nombre: r for r in relaciones if isinstance(r, Relacion)}
    else:
        rel_map = {}

    campos_lenguaje = campos_de_relaciones_declarados(raiz=raiz)
    filas: list[dict] = []

    for m in medidas:
        if not isinstance(m, Medida):
            raise ValueError(f"se esperaba `Medida`, no {type(m).__name__}")
        alias_map = extraer_alias_de_medida(m)
        for alias, campo_nombre in _extraer_lecturas_de_arbol(m.a_datos()):
            rel_nombre = alias_map.get(alias)
            if rel_nombre is None:
                relacion = ""
                origen = "sin_declarar"
                existe = False
            elif rel_nombre in rel_map:
                relacion = rel_nombre
                origen = "declarada"
                rel_obj = rel_map[rel_nombre]
                nombres_conocidos = {c.nombre for c in rel_obj.todos_los_campos}
                existe = (campo_nombre in nombres_conocidos)
            elif rel_nombre in campos_lenguaje:
                relacion = rel_nombre
                origen = "lenguaje"
                existe = (campo_nombre in campos_lenguaje[rel_nombre])
            else:
                relacion = rel_nombre
                origen = "sin_declarar"
                existe = False

            filas.append({
                "medida": m.id,
                "relacion": relacion,
                "campo": campo_nombre,
                "origen": origen,
                "existe": existe,
            })

    return {"campo_leido": filas}

