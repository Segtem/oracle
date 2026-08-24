"""Propiedades metamórficas: dos caminos que tienen que dar lo mismo.

    python tools/metamorficas.py            → informe
    python tools/metamorficas.py --hechos   → evidencia JSON

Una propiedad metamórfica no dice cuál es el resultado correcto: dice que **dos formas distintas de
escribir la misma medida tienen que coincidir**. Por eso atrapa defectos que nadie imaginó — no hace
falta saber la respuesta, sólo que los dos caminos lleguen al mismo lugar.

`PLAN-LENGUAJE.md` §(e.1) enumeró cinco. Una ya vive como medida sobre la traza
(`meta.donde_nunca_agrega_filas`); las demás son equivalencias, y una equivalencia no se lee de una
traza: hay que **correr las dos formas y comparar**. Eso es lo que hace este sensor.

## Por qué algunas formas se construyen acá y no salen del catálogo

Medido el 2026-08-24 sobre las medidas publicadas: **cero** usan dos `donde`, **cero** usan
`agrupar` sin claves, dos usan `unir` y la mayoría están escritas por macro. Así que dos de las
propiedades no tienen ningún material real contra el cual comprobarse.

Comprobarlas sólo donde el catálogo casualmente las ejercita sería medir la coincidencia, no la
propiedad: el día que alguien escriba la primera medida con dos `donde`, la propiedad tendría que
haber estado vigente desde antes. Así que el sensor **construye** las formas que el catálogo no
tiene, y cada hecho declara su `origen` —`catalogo` o `construido`— para que la medida que lo juzga
no pueda confundir una cosa con la otra.

El sensor produce HECHOS y no juzga: si una equivalencia que falla es aceptable lo dice una medida.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402
from nucleo.medida import Medida, cargar_catalogo, evaluar, medidas_aplicables  # noqa: E402
from nucleo.mutacion import _huella  # noqa: E402
from nucleo.proyecto import (Proyecto, catalogos_a_cargar,  # noqa: E402
                             macros_del_proyecto)
from tools import sintaxis  # noqa: E402

UMBRAL = ["umbral", "<=", 0, "sonda de equivalencia: el umbral no se juzga, se comparan dos formas"]
ALCANCE = ["alcance", "sonda construida para comprobar una equivalencia. NO mide ningún mundo"]
# Evidencia de las sondas construidas. Tiene filas que pasan cada filtro y filas que no, porque una
# equivalencia comprobada sólo sobre filas que nadie descarta no ejercita el filtro.
EV_SONDA = {
    "cosa": [{"n": 1, "m": 10}, {"n": 2, "m": 20}, {"n": 3, "m": 10}, {"n": 4, "m": 30}],
    "otra": [{"k": "a"}, {"k": "b"}],
}


def _comparar(a: Medida, b: Medida, evidencia: dict) -> dict:
    """Evalúa las dos formas y devuelve en qué coinciden. Los tres campos son contrato.

    El veredicto no alcanza: dos formas pueden caer del mismo lado del umbral con valores distintos,
    y el valor explica CUÁNTO. Los testigos tampoco son decorativos — son lo que una persona lee para
    actuar. Es la misma lección que la mutación de medidas aprendió y por eso se reusa su huella.
    """
    try:
        va, vb = a.evaluar(evidencia), b.evaluar(evidencia)
    except Exception as e:                 # noqa: BLE001
        return {"evaluo": False, "error": type(e).__name__,
                "mismo_veredicto": False, "mismo_valor": False, "mismos_testigos": False}
    return {
        "evaluo": True,
        "error": "",
        "mismo_veredicto": va.ok == vb.ok,
        "mismo_valor": va.valor == vb.valor,
        # El orden de una bolsa no es semántico; quiénes son, sí.
        "mismos_testigos": _huella(va.testigos) == _huella(vb.testigos),
    }


def _sonda(tuberia, resumen) -> Medida:
    return Medida.de_datos(["medida", "sonda.x", tuberia, resumen, UMBRAL, ALCANCE])


def _donde_compone() -> list[dict]:
    """`donde P` seguido de `donde Q` ≡ `donde ["y", P, Q]`."""
    P = [">", ["campo", "c", "n"], 1]
    Q = ["<", ["campo", "c", "m"], 30]
    resumen = ["resumen", "contar", 1]
    dos = _sonda(["desde", ["de", "cosa", "c"], ["donde", P], ["donde", Q]], resumen)
    una = _sonda(["desde", ["de", "cosa", "c"], ["donde", ["y", P, Q]]], resumen)
    return [{"propiedad": "donde_compone", "caso": "dos-filtros-vs-conjuncion",
             "origen": "construido", **_comparar(dos, una, EV_SONDA)}]


def _unir_conmuta(catalogo: dict, casos: list[dict]) -> list[dict]:
    """`unir A B` ≡ `unir B A`. Las filas llevan los dos alias, así que el producto conmuta salvo el
    orden de las filas — y el orden de una bolsa no es parte del contrato."""
    filas = []
    izq, der = ["de", "cosa", "c"], ["de", "otra", "o"]
    resumen = ["resumen", "contar", 1]
    pred = ["==", ["campo", "o", "k"], "a"]
    a = _sonda(["desde", ["unir", izq, der], ["donde", pred]], resumen)
    b = _sonda(["desde", ["unir", der, izq], ["donde", pred]], resumen)
    filas.append({"propiedad": "unir_conmuta", "caso": "sonda-cosa-otra",
                  "origen": "construido", **_comparar(a, b, EV_SONDA)})

    # Y sobre las medidas reales que usan `unir`, con la evidencia real de su caso de corpus.
    for caso in casos:
        mid = caso.get("medida")
        if not mid or mid not in catalogo or "evidencia" not in caso:
            continue
        datos = catalogo[mid].a_datos()
        fuente = datos[2][1]
        if not (isinstance(fuente, list) and fuente and fuente[0] == "unir"):
            continue
        volteada = json.loads(json.dumps(datos))
        volteada[2][1] = ["unir", fuente[2], fuente[1]]
        filas.append({"propiedad": "unir_conmuta", "caso": caso["id"], "origen": "catalogo",
                      **_comparar(catalogo[mid], Medida.de_datos(volteada), caso["evidencia"])})
    return filas


def _agrupar_sin_claves() -> list[dict]:
    """`agrupar` sin claves seguido de leer la columna ≡ el resumen global directo.

    Sin claves hay un solo grupo, así que agregar por grupo y agregar sobre todo tienen que dar el
    mismo número. Si no coinciden, `agrupar` está inventando o perdiendo filas al colapsar.
    """
    filas = []
    for agg in ("contar", "suma", "max", "min", "promedio"):
        expr = 1 if agg == "contar" else ["campo", "c", "n"]
        agrupada = _sonda(
            ["desde", ["de", "cosa", "c"], ["agrupar", [], [["t", agg, expr]]]],
            ["resumen", "max", ["col", "t"]])
        directa = _sonda(["desde", ["de", "cosa", "c"]], ["resumen", agg, expr])
        filas.append({"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": agg,
                      "origen": "construido", **_comparar(agrupada, directa, EV_SONDA)})
    return filas


def _macro_equivale_a_su_expansion(catalogo: dict, casos: list[dict], macros) -> list[dict]:
    """Toda medida por macro ≡ su expansión canónica.

    Es la única de las cuatro con material de sobra —diecinueve de veintidós medidas pasan por una
    macro— y la que más importa: si una macro expandiera distinto de lo que su autor cree, todo el
    catálogo escrito con ella mediría otra cosa, en silencio.
    """
    filas = []
    for caso in casos:
        mid = caso.get("medida")
        if not mid or mid not in catalogo or "evidencia" not in caso:
            continue
        m = catalogo[mid]
        if not m.fuente:                   # se escribió canónica: no hay dos formas que comparar
            continue
        canonica = Medida.de_datos(m.a_datos(), macros=macros)
        filas.append({"propiedad": "una_macro_equivale_a_su_expansion", "caso": caso["id"],
                      "origen": "catalogo", **_comparar(m, canonica, caso["evidencia"])})
    return filas


def _sintaxis_ida_y_vuelta(proy: Proyecto) -> list[dict]:
    filas = []
    for ruta in sintaxis._rutas_catalogo(proy.raiz):
        caso = str(ruta.relative_to(proy.raiz))
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
            superficie = sintaxis.imprimir(datos)
            releida = sintaxis.leer(superficie)
            reimpresa = sintaxis.imprimir(releida)
        except Exception as e:             # noqa: BLE001
            filas.append({"propiedad": "sintaxis_ida_y_vuelta", "caso": caso,
                          "origen": "catalogo", "evaluo": False,
                          "error": f"{type(e).__name__}: {e}",
                          "mismo_veredicto": False, "mismo_valor": False,
                          "mismos_testigos": False})
            continue
        filas.append({"propiedad": "sintaxis_ida_y_vuelta", "caso": caso,
                      "origen": "catalogo", "evaluo": True, "error": "",
                      # Reusa los nombres genéricos para que las otras medidas sobre `equivalencia`
                      # puedan evaluar todos sus operandos sin tropezar con campos ausentes.
                      "mismo_veredicto": releida == datos,
                      "mismo_valor": reimpresa == superficie,
                      "mismos_testigos": True})
    return filas


def hechos(catalogo: dict, casos: list[dict], macros, proy: Proyecto | None = None) -> dict:
    proy = proy or Proyecto(RAIZ)
    return {"equivalencia": [
        *_donde_compone(),
        *_unir_conmuta(catalogo, casos),
        *_agrupar_sin_claves(),
        *_macro_equivale_a_su_expansion(catalogo, casos, macros),
        *_sintaxis_ida_y_vuelta(proy),
    ]}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    proy = Proyecto(RAIZ)
    macros = macros_del_proyecto(proy)
    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros)
    casos = [json.loads(p.read_text(encoding="utf-8"))
             for p in sorted(proy.corpus.rglob("*.json"))]
    evidencia = hechos(catalogo, casos, macros, proy)

    if "--hechos" in argv:
        print(json.dumps(evidencia, ensure_ascii=False, indent=2))
        return 0

    filas = evidencia["equivalencia"]
    por_propiedad: dict[str, list] = {}
    for f in filas:
        por_propiedad.setdefault(f["propiedad"], []).append(f)
    print(f"equivalencias comprobadas: {len(filas)}")
    for nombre, grupo in sorted(por_propiedad.items()):
        construidas = sum(1 for f in grupo if f["origen"] == "construido")
        print(f"  {nombre:<44} {len(grupo):>3} "
              f"({construidas} construidas, {len(grupo) - construidas} del catálogo)")
    print()

    # Mismo fail-closed que `tools/trazar.py`: las juezas son medidas «ninguno», así que sin
    # equivalencias que comparar salen verdes. Una corrida que no comparó nada no es un lenguaje
    # consistente — es un lenguaje que no se comparó.
    if not filas:
        print("SIN EQUIVALENCIAS — no se comparó ni un par de formas.")
        return 1

    juezas = medidas_aplicables(catalogo.values(), evidencia)
    if not juezas:
        print("sin medidas aplicables a las equivalencias")
        return 1
    informe = evaluar(juezas, evidencia)
    print("juzgado por las medidas aplicables:")
    for v in informe.veredictos:
        print(" ", v.linea())
    return 0 if informe.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
