"""Contrasta una implementación independiente del álgebra con la referencia del diferencial.

    python3 estudios/0.26.0-codex/contrastar.py <candidato/evaluador.py> [--json]

Compara, medida por medida, el veredicto entero —`ok`, valor y si levantó— de las dos
implementaciones, sobre dos fuentes: los mundos de `tools/generar_diferencial.py` con sus cinco
medidas, y cada caso del corpus de Oracle con la medida que declara. No decide quién tiene razón:
lista dónde se dividen, que es lo que después hay que clasificar a mano —especificación que no
decide, núcleo contra todas, o defecto de una implementación— como en
`diferencial/referencia/PROCEDENCIA.md`.

Sale 0 si coinciden en todo, 1 si hay desacuerdos y 2 si el candidato no se puede usar.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path = [str(RAIZ), *sys.path]

import catalogos.escalares  # noqa: F401,E402  registra las UDF declaradas
from nucleo.algebra import ESCALARES  # noqa: E402
from nucleo.caso import cargar_casos  # noqa: E402
from nucleo.medida import Medida, cargar_catalogo  # noqa: E402
from nucleo.proyecto import Proyecto, catalogos_a_cargar, macros_del_proyecto  # noqa: E402
from tools import generar_diferencial as gen  # noqa: E402


def cargar_modulo(ruta: Path, nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def veredicto(modulo, medida, evidencia) -> dict:
    """El mismo registro que guarda el diferencial. Una excepción que NO es `ErrorDeAlgebra` se
    anota aparte: el contrato dice que ninguna otra puede escaparse, y eso es un defecto clase 3."""
    try:
        return gen._de_la_referencia(modulo, medida, evidencia, dict(ESCALARES))
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "escapa": type(e).__name__}


def fuentes(catalogo: dict):
    """(origen, medida, evidencia) de los mundos del diferencial y de cada caso del corpus."""
    medidas = ([catalogo[mid] for mid in gen.MEDIDAS_DEL_CATALOGO]
               + [Medida.de_datos(d) for d in gen.MEDIDAS_DEL_EMISOR])
    for nombre, evidencia in gen.MUNDOS:
        for medida in medidas:
            yield f"mundo:{nombre}", medida, evidencia
    for caso in cargar_casos(RAIZ / "corpus"):
        medida = catalogo.get(caso.get("medida"))
        if medida is not None and isinstance(caso.get("evidencia"), dict):
            yield f"caso:{caso['id']}", medida, caso["evidencia"]


def contrastar(candidato, referencia, catalogo) -> tuple[int, list[dict]]:
    total, desacuerdos = 0, []
    for origen, medida, evidencia in fuentes(catalogo):
        total += 1
        suyo = veredicto(candidato, medida, evidencia)
        nuestro = veredicto(referencia, medida, evidencia)
        if suyo != nuestro:
            desacuerdos.append({"origen": origen, "medida": medida.id,
                                "candidato": suyo, "referencia": nuestro})
    return total, desacuerdos


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0 if argv else 2
    ruta = Path(argv[0]).resolve()
    if not ruta.is_file():
        print(f"no existe {ruta}")
        return 2
    candidato = cargar_modulo(ruta, "candidato_independiente")
    referencia = cargar_modulo(gen.REFERENCIA, "referencia_diferencial")
    for nombre in ("evaluar", "ErrorDeAlgebra", "VERSION_ALGEBRA"):
        if not hasattr(candidato, nombre):
            print(f"el candidato no cumple el contrato: le falta `{nombre}`")
            return 2
    if candidato.VERSION_ALGEBRA != referencia.VERSION_ALGEBRA:
        print(f"el candidato declara el álgebra {candidato.VERSION_ALGEBRA} y la referencia "
              f"{referencia.VERSION_ALGEBRA}: no se comparan versiones distintas")
        return 2

    proy = Proyecto(RAIZ)
    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    total, desacuerdos = contrastar(candidato, referencia, catalogo)

    if "--json" in argv:
        print(json.dumps({"comparaciones": total, "desacuerdos": desacuerdos},
                         ensure_ascii=False, indent=2))
        return 1 if desacuerdos else 0

    print(f"{total} comparaciones · {len(desacuerdos)} desacuerdos")
    for medida, n in Counter(d["medida"] for d in desacuerdos).most_common():
        print(f"  {n:>4}  {medida}")
    for d in desacuerdos[:30]:
        print(f"\n  {d['origen']} · {d['medida']}\n"
              f"      candidato:  {d['candidato']}\n      referencia: {d['referencia']}")
    return 1 if desacuerdos else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
