"""Muta las medidas y mide el resultado CON LAS MEDIDAS. El bucle se cierra acá.

    python tools/mutar.py [--confiar-escalares]          → informe
    python tools/mutar.py --hechos [--confiar-escalares] → evidencia JSON

El sensor produce hechos y las políticas aplicables del catálogo pueden juzgarlos. Un proyecto
neutral no necesita importar esas políticas para obtener el resultado operativo de la mutación.

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
from nucleo.medida import cargar_catalogo, evaluar, medidas_aplicables  # noqa: E402
from nucleo.mutacion import correr  # noqa: E402
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables, RAIZ_ORACLE,
                             catalogos_a_cargar, catalogos_base_a_cargar, confiar_escalares,
                             escalares_del_proyecto, macros_del_proyecto,
                             problemas_estructura,
                             sin_banderas_comunes)  # noqa: E402
from tools.sesion import resolver_cli  # noqa: E402

def casos(proy, catalogo) -> list[dict]:
    """El corpus MÁS la prueba diferencial.

    Las medidas fijadas por un diferencial pueden no aparecer en el corpus. Un mutador que omite esos
    escenarios es peor que no tenerlo, porque publicaría «todos murieron» dejando medidas afuera.
    """
    salida = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted(proy.corpus.rglob("*.json"))]
    fixtures, fallas = cargar_fixtures(
        sorted(proy.diferencial.glob("*.json")), raiz=proy.raiz, catalogo=catalogo)
    if fallas:
        raise ValueError("fixtures diferenciales inválidos o vencidos:\n  · " + "\n  · ".join(fallas))
    for fixture in fixtures:
        salida.extend(casos_para_mutacion(fixture, catalogo))
    return salida


def _ejecutar(proy, args: list[str]) -> int:
    estructura = problemas_estructura(proy, ("catalogos", "corpus", "diferencial"))
    if estructura:
        print("PROYECTO INVÁLIDO — " + "; ".join(estructura))
        return 1
    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    try:
        listado = casos(proy, catalogo)
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
    base = (cargar_catalogo(catalogos_base_a_cargar(proy), macros=macros_del_proyecto(proy))
            if not proy.es_el_propio_oracle else {})
    evidencia.update(hechos_de_uso(catalogo, listado, evidencia["mutante"],
                                   evaluadas_aparte=metas, heredadas=set(base)))

    juezas = medidas_aplicables(catalogo.values(), evidencia)
    informe = evaluar(juezas, evidencia)
    if informe.veredictos:
        print("juzgado por las medidas del catálogo:")
        for v in informe.veredictos:
            print(" ", v.linea())
    else:
        print("sin políticas meta activas — se informa sólo el resultado operativo")

    if vivos:
        print("\nlo que el corpus NO fija — ningún caso detecta estas mutaciones:")
        for m in vivos:
            print(f"  · mutar «{m['cambio']}» en {m['apunta_a']} pasa inadvertido")
        print("\nSe tapa agregando un caso que SÍ lo note o declarando una equivalencia individual")
        print("demostrable; nunca debilitando el mutador. La polaridad y el borde también importan:")
        print("`quitar_filtro` suele pedir un verde; `aflojar_umbral`, un rojo junto al límite.")

    # Que sobreviva un mutante es el contrato operativo de esta herramienta, no una política de
    # dominio. Las medidas meta, cuando el host las activa, pueden imponer condiciones adicionales.
    politicas_ok = informe.ok if informe.veredictos else True
    return 0 if not vivos and politicas_ok else 1


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = sin_banderas_comunes(argv)
    if not args or "-h" in args or "--help" in args:
        if "-h" in args or "--help" in args:
            print(__doc__)
            return 0
    proy = resolver_cli(argv)
    if proy is None:
        return 1
    try:
        with escalares_del_proyecto(proy, confiar=confiar_escalares(argv)):
            return _ejecutar(proy, args)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
