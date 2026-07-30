"""Muta las medidas y mide el resultado CON LAS MEDIDAS. El bucle se cierra acá.

    python tools/mutar.py [--confiar-escalares]          → informe
    python tools/mutar.py --hechos [--confiar-escalares] → evidencia JSON

El sensor produce hechos; el álgebra los juzga. Ninguna lógica de veredicto vive en el sensor, que es
lo que permite que la misma medida —`proceso.test_con_mutante_que_lo_mata`— sirva para los mutantes de
Jam y para los del propio oráculo.

Sale != 0 si algún mutante sobrevivió, porque un mutante que sobrevive es un aspecto de la medida que
el corpus no fija.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402
from nucleo.marco import hechos_de_uso  # noqa: E402
from nucleo.fixtures import cargar_fixtures, casos_para_mutacion  # noqa: E402
from nucleo.medida import cargar_catalogo, evaluar  # noqa: E402
from nucleo.mutacion import correr  # noqa: E402
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables, RAIZ_ORACLE,
                             catalogos_a_cargar, catalogos_base_a_cargar, confiar_escalares,
                             escalares_del_proyecto, problemas_estructura, resolver,
                             sin_banderas_comunes)  # noqa: E402

PROY = resolver(sys.argv[1:])


def casos(catalogo) -> list[dict]:
    """El corpus MÁS la prueba diferencial.

    Sin esto las medidas de geometría quedaban sin mutar: ningún caso del corpus las declara, y su
    fijación vive en el fixture diferencial. Un mutador que nadie ejercita es peor que no tenerlo,
    porque el informe diría «todos murieron» dejando cuatro medidas afuera.
    """
    salida = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((PROY.corpus).rglob("*.json"))]
    fixtures, fallas = cargar_fixtures(
        sorted(PROY.diferencial.glob("*.json")), raiz=PROY.raiz, catalogo=catalogo)
    if fallas:
        raise ValueError("fixtures diferenciales inválidos o vencidos:\n  · " + "\n  · ".join(fallas))
    for fixture in fixtures:
        salida.extend(casos_para_mutacion(fixture, catalogo))
    return salida


def _ejecutar(args: list[str]) -> int:
    estructura = problemas_estructura(PROY, ("catalogos", "corpus", "diferencial"))
    if estructura:
        print("PROYECTO INVÁLIDO — " + "; ".join(estructura))
        return 1
    catalogo = cargar_catalogo(catalogos_a_cargar(PROY))
    try:
        listado = casos(catalogo)
    except ValueError as e:
        print(f"MUTACIÓN NO CONFIABLE — {e}")
        return 1
    evidencia = correr(catalogo, listado)

    if "--hechos" in args:
        print(json.dumps(evidencia, ensure_ascii=False, indent=2))
        return 0

    mutantes = evidencia["mutante"]
    vivos = [m for m in mutantes if not m["murio"]]
    print(f"mutantes de medida (medida × mutador): {len(mutantes)} · "
          f"murieron {len(mutantes) - len(vivos)} · sobrevivieron {len(vivos)}")
    print(f"detecciones evaluadas (mutante × caso): {len(evidencia['deteccion'])}\n")

    # El bucle: los hechos del sensor, juzgados por MEDIDAS. Antes acá había un `if vivos: return 1`
    # que dictaminaba en Python lo mismo que una medida del catálogo ya dice.
    metas = {mid for mid in catalogo if mid.startswith("meta.")}
    base = cargar_catalogo(catalogos_base_a_cargar(PROY)) if not PROY.es_el_propio_oracle else {}
    evidencia.update(hechos_de_uso(catalogo, listado, evidencia["mutante"],
                                   evaluadas_aparte=metas, heredadas=set(base)))

    juezas = [catalogo[mid] for mid in ("proceso.test_con_mutante_que_lo_mata",
                                        "meta.toda_medida_esta_ejercitada",
                                        "meta.toda_medida_esta_fijada") if mid in catalogo]
    informe = evaluar(juezas, evidencia)
    print("juzgado por las medidas del catálogo:")
    for v in informe.veredictos:
        print(" ", v.linea())

    if vivos:
        print("\nlo que el corpus NO fija — ningún caso detecta estas mutaciones:")
        for m in vivos:
            print(f"  · mutar «{m['cambio']}» en {m['apunta_a']} pasa inadvertido")
        print("\nSe tapa agregando un caso que SÍ lo note o declarando una equivalencia individual")
        print("demostrable; nunca debilitando el mutador. La polaridad y el borde también importan:")
        print("`quitar_filtro` suele pedir un verde; `aflojar_umbral`, un rojo junto al límite.")

    # el código de salida sale del VEREDICTO, no de un `if` propio
    return 0 if informe.ok else 1


def main() -> int:
    argv = sys.argv[1:]
    args = sin_banderas_comunes(argv)
    if not args or "-h" in args or "--help" in args:
        if "-h" in args or "--help" in args:
            print(__doc__)
            return 0
    try:
        with escalares_del_proyecto(PROY, confiar=confiar_escalares(argv)):
            return _ejecutar(args)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
