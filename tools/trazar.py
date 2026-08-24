"""El evaluador como sensor de sí mismo: corre el corpus bajo traza y mide lo que el álgebra hizo.

    python tools/trazar.py            → informe
    python tools/trazar.py --hechos   → evidencia JSON

Oracle no puede evaluarse a sí mismo —recorrer un AST es recursión, y la recursión salió del álgebra
a propósito (`ESPECIFICACION.md` §8)— pero sí puede **juzgarse ejecutándose**. Es la doctrina del
proyecto aplicada al evaluador: el sensor produce hechos, el álgebra los mide, y acá el sensor es el
evaluador.

Lo que cambia con esto no es qué se verifica, sino DÓNDE vive la regla. «`donde` nunca agrega filas»
como test en Python es una afirmación que nadie muta y que no aparece en ningún inventario. Como
medida entra a la mutación, al corpus, al inventario de umbrales y al de puntos ciegos, igual que
cualquier otra — y sale del núcleo, que es la única dirección en la que la proporción mejora sin
sastrearla.

El punto ciego que esto tendría si se dejara solo: las medidas las evaluaría el mismo evaluador que
vigilan, y un defecto podría taparse a sí mismo. Por eso cada propiedad se juzga DOS veces —con
`nucleo/` y con `diferencial/referencia/evaluador.py`, escrito por otro autor que nunca vio el
núcleo— y un desacuerdo entre las dos hace fallar la corrida. No es una garantía absoluta: si las dos
implementaciones comparten el mismo malentendido, las dos callan igual. Es lo que un diferencial
puede dar.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402
import importlib.util  # noqa: E402
from nucleo.algebra import ESCALARES, trazar  # noqa: E402
from nucleo.medida import cargar_catalogo, evaluar, medidas_aplicables  # noqa: E402
from nucleo.proyecto import (Proyecto, catalogos_a_cargar,  # noqa: E402
                             macros_del_proyecto)

# Las medidas que vigilan al evaluador. Se nombran para poder EXCLUIRLAS de la corrida trazada: si se
# midieran a sí mismas, la traza crecería con cada paso que da la propia vigilancia y el resultado
# hablaría del vigilante y no de lo vigilado.
VIGILANTES = frozenset({
    "meta.donde_nunca_agrega_filas",
    "meta.agrupar_no_agranda_la_relacion",
    "meta.unir_materializa_el_producto",
    "meta.los_logicos_evaluan_todos_sus_operandos",
})


REFERENCIA = RAIZ / "diferencial" / "referencia" / "evaluador.py"


def cargar_referencia():
    """La implementación independiente. Su procedencia está en `diferencial/referencia/`."""
    spec = importlib.util.spec_from_file_location("referencia_trazar", REFERENCIA)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def contrastar(medidas, evidencia: dict) -> list[str]:
    """Evalúa cada propiedad con las DOS implementaciones y devuelve los desacuerdos.

    Un desacuerdo no dice cuál de las dos tiene razón. Dice que la especificación no alcanzó, que es
    justamente lo que un diferencial existe para encontrar.
    """
    referencia = cargar_referencia()
    escalares = dict(ESCALARES)
    desacuerdos = []
    for medida in medidas:
        try:
            propio = medida.evaluar(evidencia).ok
        except Exception as e:            # noqa: BLE001
            propio = f"{type(e).__name__}"
        try:
            ajeno = referencia.evaluar(medida.a_datos(), evidencia, escalares)["ok"]
        except Exception as e:            # noqa: BLE001
            ajeno = f"{type(e).__name__}"
        if propio != ajeno:
            desacuerdos.append(f"{medida.id}: nucleo={propio!r} vs referencia={ajeno!r}")
    return desacuerdos


def casos(proy: Proyecto) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in sorted(proy.corpus.rglob("*.json"))]


def hechos(catalogo: dict, listado: list[dict]) -> dict:
    """Evalúa cada caso del corpus con su medida, bajo traza, y devuelve lo que el álgebra hizo.

    Un caso que rompe no se descarta en silencio: no aporta hechos, y eso es correcto —lo que se
    está midiendo es la evaluación que ocurrió, no la que se pretendía—, pero se cuenta aparte para
    que el denominador de la corrida sea visible.
    """
    crudos: list[tuple[str, dict]] = []
    evaluados = fallidos = 0
    for caso in listado:
        mid = caso.get("medida")
        evidencia = caso.get("evidencia")
        if not mid or mid not in catalogo or evidencia is None or mid in VIGILANTES:
            continue
        try:
            with trazar(crudos):
                catalogo[mid].evaluar(evidencia)
            evaluados += 1
        except Exception:      # noqa: BLE001  una medida que no evalúa no produce traza, y ya está
            fallidos += 1

    salida: dict[str, list[dict]] = {"paso": [], "nodo": [], "producto": []}
    for clase, campos in crudos:
        salida[clase].append(dict(campos))
    return salida, evaluados, fallidos


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    proy = Proyecto(RAIZ)
    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    evidencia, evaluados, fallidos = hechos(catalogo, casos(proy))

    if "--hechos" in argv:
        print(json.dumps(evidencia, ensure_ascii=False, indent=2))
        return 0

    print(f"evaluaciones trazadas: {evaluados}" + (f" · {fallidos} no evaluaron" if fallidos else ""))
    print(f"hechos: {len(evidencia['paso'])} pasos · {len(evidencia['nodo'])} nodos lógicos · "
          f"{len(evidencia['producto'])} productos\n")

    juezas = medidas_aplicables(catalogo.values(), evidencia)
    if not juezas:
        print("sin medidas aplicables a la traza")
        return 1
    informe = evaluar(juezas, evidencia)
    print("el álgebra, juzgada por medidas escritas en el álgebra:")
    for v in informe.veredictos:
        print(" ", v.linea())

    # La segunda mano. Sin esto, el evaluador se estaría examinando solo.
    desacuerdos = contrastar(juezas, evidencia)
    print()
    if desacuerdos:
        print("DESACUERDO con la implementación de referencia — la especificación no alcanza:")
        for d in desacuerdos:
            print(f"  · {d}")
        return 1
    print(f"contrastado con la implementación independiente: {len(juezas)} propiedades, "
          "0 desacuerdos")

    print()
    for v in informe.veredictos:
        print(f"  · {v.id}: {v.alcance}")
    return 0 if informe.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
