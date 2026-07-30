"""Muta las medidas y mide el resultado CON LAS MEDIDAS. El bucle se cierra acá.

    python tools/mutar.py            → informe
    python tools/mutar.py --hechos   → volcar la evidencia producida (JSON)

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
from nucleo.medida import cargar_catalogo, evaluar  # noqa: E402
from nucleo.mutacion import correr  # noqa: E402
from nucleo.proyecto import (catalogos_a_cargar, registrar_escalares, resolver,
                             sin_bandera)  # noqa: E402

PROY = resolver(sys.argv[1:])
registrar_escalares(PROY)


def casos(catalogo) -> list[dict]:
    """El corpus MÁS la prueba diferencial.

    Sin esto las medidas de geometría quedaban sin mutar: ningún caso del corpus las declara, y su
    fijación vive en el fixture diferencial. Un mutador que nadie ejercita es peor que no tenerlo,
    porque el informe diría «todos murieron» dejando cuatro medidas afuera.
    """
    salida = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((PROY.corpus).rglob("*.json"))]
    for f in sorted((PROY.diferencial).glob("*.json")):
        datos = json.loads(f.read_text(encoding="utf-8"))

        # Formato de dominio declarado: no hay expectativa por medida —eso reimplementaba las
        # medidas—, así que la línea base es el veredicto ACTUAL de cada una. Para mutar es lo
        # correcto: la pregunta no es «¿acierta?» sino «¿algún escenario nota que la cambiaron?».
        if "escenarios" in datos:
            for mid in datos["medidas"]:
                if mid not in catalogo:
                    continue
                for esc in datos["escenarios"]:
                    ok = catalogo[mid].evaluar(esc["evidencia"]).ok
                    salida.append({
                        "id": f"{f.stem}/{mid}[{esc['id']}]",
                        "etiqueta": "verde_correcto" if ok else "falso_verde",
                        "medida": mid,
                        "evidencia": esc["evidencia"],
                    })
            continue

        for mid, entradas in datos["grupos"].items():
            for i, e in enumerate(entradas):
                salida.append({
                    "id": f"{f.stem}/{mid}[{i}]",
                    "etiqueta": "verde_correcto" if e["esperado_ok"] else "falso_verde",
                    "medida": mid,
                    "evidencia": e["evidencia"],
                })
    return salida


def main() -> int:
    catalogo = cargar_catalogo(catalogos_a_cargar(PROY))
    evidencia = correr(catalogo, casos(catalogo))

    if "--hechos" in sin_bandera(sys.argv[1:]):
        print(json.dumps(evidencia, ensure_ascii=False, indent=2))
        return 0

    mutantes = evidencia["mutante"]
    vivos = [m for m in mutantes if not m["murio"]]
    print(f"mutantes de medida (medida × mutador): {len(mutantes)} · "
          f"murieron {len(mutantes) - len(vivos)} · sobrevivieron {len(vivos)}")
    print(f"detecciones evaluadas (mutante × caso): {len(evidencia['deteccion'])}\n")

    # El bucle: los hechos del sensor, juzgados por MEDIDAS. Antes acá había un `if vivos: return 1`
    # que dictaminaba en Python lo mismo que una medida del catálogo ya dice.
    listado = casos(catalogo)
    metas = {mid for mid in catalogo if mid.startswith("meta.")}
    evidencia.update(hechos_de_uso(catalogo, listado, evidencia["mutante"], evaluadas_aparte=metas))

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
        print("\nSe tapa agregando un caso que SÍ lo note, no cambiando la medida. Y si un mutante")
        print("no lo puede detectar ninguna polaridad, suele faltar el caso de la otra:")
        print("`quitar_filtro` sólo lo agarra un caso verde; `aflojar_umbral`, sólo uno rojo.")

    # el código de salida sale del VEREDICTO, no de un `if` propio
    return 0 if informe.ok else 1


if __name__ == "__main__":
    sys.exit(main())
