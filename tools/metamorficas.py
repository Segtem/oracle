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
from nucleo import caso as sintaxis_caso  # noqa: E402
from nucleo.caso import cargar_casos, cargar_fuente_caso  # noqa: E402
from nucleo.medida import (Medida, cargar_catalogo, cargar_fuente_medida, evaluar,  # noqa: E402
                           medidas_aplicables)
from nucleo.mutacion import _huella  # noqa: E402
from nucleo.proyecto import (Proyecto, catalogos_a_cargar,  # noqa: E402
                             macros_del_proyecto)
from tools import sintaxis  # noqa: E402

RELACIONES_DEL_LENGUAJE = frozenset({"equivalencia"})

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


def _donde_compone(catalogo: dict, casos: list[dict]) -> list[dict]:
    """`donde P` seguido de `donde Q` ≡ `donde ["y", P, Q]`."""
    filas = []
    P = [">", ["campo", "c", "n"], 1]
    Q = ["<", ["campo", "c", "m"], 30]
    resumen = ["resumen", "contar", 1]
    dos = _sonda(["desde", ["de", "cosa", "c"], ["donde", P], ["donde", Q]], resumen)
    una = _sonda(["desde", ["de", "cosa", "c"], ["donde", ["y", P, Q]]], resumen)
    filas.append({"propiedad": "donde_compone", "caso": "dos-filtros-vs-conjuncion",
                  "origen": "construido", **_comparar(dos, una, EV_SONDA)})

    # Y sobre las medidas reales con dos `donde` o con `donde` de `y`, con la evidencia real de sus casos.
    for caso in casos:
        mid = caso.get("medida")
        if not mid or mid not in catalogo or "evidencia" not in caso:
            continue
        datos = catalogo[mid].a_datos()
        tuberia = datos[2]
        pasos = tuberia[1:]

        # Caso A: donde con "y" -> partir en varios donde
        for i, paso in enumerate(pasos):
            if paso[0] == "donde":
                cond = paso[1]
                if isinstance(cond, list) and cond and cond[0] == "y" and len(cond) > 2:
                    partida = json.loads(json.dumps(datos))
                    nuevos = [["donde", p] for p in cond[1:]]
                    partida[2] = [tuberia[0]] + pasos[:i] + nuevos + pasos[i+1:]
                    filas.append({"propiedad": "donde_compone", "caso": caso["id"], "origen": "catalogo",
                                  **_comparar(catalogo[mid], Medida.de_datos(partida), caso["evidencia"])})

        # Caso B: dos donde encadenados -> unir en un donde con "y"
        for i in range(len(pasos) - 1):
            if pasos[i][0] == "donde" and pasos[i+1][0] == "donde":
                unida = json.loads(json.dumps(datos))
                nueva_cond = ["y", pasos[i][1], pasos[i+1][1]]
                unida[2] = [tuberia[0]] + pasos[:i] + [["donde", nueva_cond]] + pasos[i+2:]
                filas.append({"propiedad": "donde_compone", "caso": caso["id"], "origen": "catalogo",
                              **_comparar(catalogo[mid], Medida.de_datos(unida), caso["evidencia"])})
    return filas


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


def _agrupar_sin_claves(catalogo: dict, casos: list[dict]) -> list[dict]:
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

    # Y sobre las medidas reales sin `agrupar`, con la evidencia real de su caso de corpus.
    for caso in casos:
        mid = caso.get("medida")
        if not mid or mid not in catalogo or "evidencia" not in caso:
            continue
        datos = catalogo[mid].a_datos()
        tuberia = datos[2]
        pasos = tuberia[1:]
        if any(isinstance(p, list) and p and p[0] == "agrupar" for p in pasos):
            continue
        resumen = datos[3]
        agg, expr = resumen[1], resumen[2]
        agrupada_datos = json.loads(json.dumps(datos))
        col_name = "t"
        agrupada_datos[2].append(["agrupar", [], [[col_name, agg, expr]]])
        agrupada_datos[3] = ["resumen", "max", ["col", col_name]]
        filas.append({"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": caso["id"],
                      "origen": "catalogo",
                      **_comparar(catalogo[mid], Medida.de_datos(agrupada_datos), caso["evidencia"])})
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
            datos = cargar_fuente_medida(ruta)
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


def _generar_candidatas() -> list[list]:
    """Generador sistemático y determinista derivado de la gramática del álgebra."""
    fuentes = [
        ("de", ["de", "cosa", "c"]),
        ("unir1", ["unir", ["de", "cosa", "c"], ["de", "otra", "o"]]),
        ("unir2", ["unir", ["unir", ["de", "cosa", "c"], ["de", "otra", "o"]], ["de", "tercera", "t"]]),
        ("unir3", ["unir", ["unir", ["unir", ["de", "cosa", "c"], ["de", "otra", "o"]], ["de", "tercera", "t"]], ["de", "cuarta", "cu"]]),
    ]

    acc_campo = ["campo", "c", "n"]
    acc_hecho = ["hecho", "c"]
    acc_col = ["col", "col1"]

    cmp_map = {
        "eq": "==", "neq": "!=", "lt": "<", "lte": "<=", "gt": ">", "gte": ">="
    }
    cmps = []
    for cmp_name, op in cmp_map.items():
        cmps.append((f"cmp_{cmp_name}_int", [op, acc_campo, 1]))

    cmps.append(("cmp_eq_true", ["==", acc_campo, True]))
    cmps.append(("cmp_eq_false", ["==", acc_campo, False]))
    cmps.append(("cmp_eq_null", ["==", acc_campo, None]))
    cmps.append(("cmp_lt_float", ["<", acc_campo, 3.14]))
    cmps.append(("cmp_gte_str", [">=", acc_campo, "alfa"]))
    cmps.append(("cmp_campo_campo", ["==", acc_campo, ["campo", "c", "m"]]))
    cmps.append(("cmp_hecho", ["!=", acc_hecho, 0]))
    cmps.append(("cmp_col", [">", acc_col, 5]))

    p1 = ["==", acc_campo, 1]
    p2 = ["<", ["campo", "c", "m"], 10]
    p3 = ["==", ["campo", "c", "activo"], True]
    p4 = ["==", ["campo", "c", "texto"], None]

    logicas = [
        ("y2", ["y", p1, p2]),
        ("y3", ["y", p1, p2, p3]),
        ("o2", ["o", p1, p2]),
        ("o3", ["o", p1, p2, p4]),
        ("no", ["no", p1]),
        ("no_y", ["no", ["y", p1, p2]]),
        ("no_o", ["no", ["o", p1, p2]]),
        ("y_de_o", ["y", ["o", p1, p2], ["o", p3, p4]]),
        ("o_de_y", ["o", ["y", p1, p2], ["y", p3, p4]]),
        ("no_anidado", ["no", ["no", p1]]),
        ("profunda_4", ["no", ["o", ["y", ["no", p1], p2], ["y", p3, ["no", p4]]]]),
        ("profunda_5", ["y", ["no", ["o", ["y", p1, p2], p3]], ["o", ["no", p4], ["==", acc_col, 0]]]),
    ]

    todas_exprs = cmps + logicas

    claves_opts = [
        ("c0", []),
        ("c1", [["k1", acc_campo]]),
        ("c2", [["k1", acc_campo], ["k2", ["campo", "c", "m"]]]),
    ]

    aggs_opts = [
        ("a1_contar", [["a1", "contar", 1]]),
        ("a1_suma", [["a1", "suma", acc_campo]]),
        ("a1_max", [["a1", "max", acc_campo]]),
        ("a1_min", [["a1", "min", acc_campo]]),
        ("a1_prom", [["a1", "promedio", acc_campo]]),
        ("a2_contar_suma", [["a1", "contar", 1], ["a2", "suma", ["campo", "c", "m"]]]),
        ("a2_max_min", [["a1", "max", acc_campo], ["a2", "min", ["campo", "c", "m"]]]),
    ]

    resumen_opts = [
        ("res_contar", ["resumen", "contar", 1]),
        ("res_suma", ["resumen", "suma", acc_campo]),
        ("res_max", ["resumen", "max", acc_campo]),
        ("res_min", ["resumen", "min", acc_campo]),
        ("res_prom", ["resumen", "promedio", acc_campo]),
        ("res_col", ["resumen", "max", acc_col]),
    ]

    umbral_opts = [
        ("umb_lte_0", ["umbral", "<=", 0, "defensa <= 0"]),
        ("umb_eq_true", ["umbral", "==", True, "defensa == true"]),
        ("umb_neq_false", ["umbral", "!=", False, "defensa != false"]),
        ("umb_gt_float", ["umbral", ">", 3.14, "defensa > 3.14"]),
        ("umb_lt_neg", ["umbral", "<", -5, "defensa < -5"]),
        ("umb_gte_str", ["umbral", ">=", "alfa", "defensa >= alfa"]),
    ]

    req_opts = [
        ("req0", None),
        ("req1", ["requiere", "cosa"]),
        ("req2", ["requiere", "cosa", "otra"]),
    ]

    medidas = []

    # 1. Fuentes combinadas con requiere y umbrales
    for f_id, fuente in fuentes:
        for r_id, req in req_opts:
            for u_id, umb in umbral_opts[:2]:
                mid = f"meta_gen.f_{f_id}_{r_id}_{u_id}"
                m = ["medida", mid, ["desde", fuente], ["resumen", "contar", 1], umb]
                if req:
                    m.append(req)
                m.append(["alcance", "sonda generada"])
                medidas.append(m)

    # 2. Expresiones completas en donde
    for expr_id, expr in todas_exprs:
        mid = f"meta_gen.expr_{expr_id}"
        m = ["medida", mid, ["desde", ["de", "cosa", "c"], ["donde", expr]],
             ["resumen", "contar", 1], ["umbral", "<=", 0, "defensa"], ["alcance", "sonda generada"]]
        medidas.append(m)

    # 3. Agrupar: claves x agregados
    for c_id, claves in claves_opts:
        for a_id, aggs in aggs_opts:
            mid = f"meta_gen.grp_{c_id}_{a_id}"
            res = ["resumen", "max", ["col", "a1"]]
            m = ["medida", mid, ["desde", ["de", "cosa", "c"], ["agrupar", claves, aggs]],
                 res, ["umbral", "<=", 0, "defensa"], ["alcance", "sonda generada"]]
            medidas.append(m)

    # 4. Tuberías multi-paso
    medidas.append(["medida", "meta_gen.paso_dd",
                    ["desde", ["de", "cosa", "c"], ["donde", p1], ["donde", p2]],
                    ["resumen", "contar", 1], ["umbral", "<=", 0, "defensa"], ["alcance", "sonda generada"]])
    medidas.append(["medida", "meta_gen.paso_dg",
                    ["desde", ["de", "cosa", "c"], ["donde", p1], ["agrupar", [["k1", acc_campo]], [["a1", "contar", 1]]]],
                    ["resumen", "max", ["col", "a1"]], ["umbral", "<=", 0, "defensa"], ["alcance", "sonda generada"]])
    medidas.append(["medida", "meta_gen.paso_gd",
                    ["desde", ["de", "cosa", "c"], ["agrupar", [["k1", acc_campo]], [["a1", "contar", 1]]], ["donde", [">", ["col", "a1"], 0]]],
                    ["resumen", "max", ["col", "a1"]], ["umbral", "<=", 0, "defensa"], ["alcance", "sonda generada"]])
    medidas.append(["medida", "meta_gen.paso_dgd",
                    ["desde", ["de", "cosa", "c"], ["donde", p1], ["agrupar", [["k1", acc_campo]], [["a1", "contar", 1]]], ["donde", [">", ["col", "a1"], 0]]],
                    ["resumen", "max", ["col", "a1"]], ["umbral", "<=", 0, "defensa"], ["alcance", "sonda generada"]])
    medidas.append(["medida", "meta_gen.paso_g22_d",
                    ["desde", ["de", "cosa", "c"], ["agrupar", [["k1", acc_campo], ["k2", ["campo", "c", "m"]]], [["a1", "contar", 1], ["a2", "suma", ["campo", "c", "m"]]]], ["donde", ["==", ["col", "k1"], 1]]],
                    ["resumen", "max", ["col", "a2"]], ["umbral", "<=", 0, "defensa"], ["alcance", "sonda generada"]])

    # 5. Operadores de resumen (los 5)
    for res_id, res in resumen_opts:
        mid = f"meta_gen.{res_id}"
        medidas.append(["medida", mid, ["desde", ["de", "cosa", "c"]], res,
                        ["umbral", "<=", 0, "defensa"], ["alcance", "sonda generada"]])

    # 6. Operadores de umbral (los 6 con distintos tipos)
    for umb_id, umb in umbral_opts:
        mid = f"meta_gen.{umb_id}"
        medidas.append(["medida", mid, ["desde", ["de", "cosa", "c"]],
                        ["resumen", "contar", 1], umb, ["alcance", "sonda generada"]])

    # 7. Requiere (0, 1, 2)
    for req_id, req in req_opts:
        mid = f"meta_gen.{req_id}"
        m = ["medida", mid, ["desde", ["de", "cosa", "c"]], ["resumen", "contar", 1],
             ["umbral", "<=", 0, "defensa"]]
        if req:
            m.append(req)
        m.append(["alcance", "sonda generada"])
        medidas.append(m)

    # 8. Combinaciones cruzadas de fuentes con agrupar y expresiones
    for f_id, fuente in fuentes[1:]:
        mid = f"meta_gen.unir_agrupar_{f_id}"
        m = ["medida", mid, ["desde", fuente, ["donde", p1], ["agrupar", [["k1", acc_campo]], [["a1", "contar", 1]]]],
             ["resumen", "max", ["col", "a1"]], ["umbral", "<=", 0, "defensa"], ["alcance", "sonda generada"]]
        medidas.append(m)

    return medidas


def _sintaxis_cubre_algebra() -> list[dict]:
    """Toda medida generada a partir de la gramática que el álgebra acepta, la superficie la
    imprime, la relee y da exactamente lo mismo."""
    candidatas = _generar_candidatas()
    filas = []
    for datos_candidata in candidatas:
        try:
            m = Medida.de_datos(datos_candidata)
        except Exception:                  # noqa: BLE001
            # Si el álgebra la rechaza, no es una medida válida: no entra a la propiedad.
            continue
        datos = m.a_datos()
        try:
            superficie = sintaxis.imprimir(datos)
            releida = sintaxis.leer(superficie)
            reimpresa = sintaxis.imprimir(releida)
        except Exception as e:             # noqa: BLE001
            filas.append({"propiedad": "sintaxis_cubre_algebra", "caso": m.id,
                          "origen": "construido", "evaluo": False,
                          "error": f"{type(e).__name__}: {e}",
                          "mismo_veredicto": False, "mismo_valor": False,
                          "mismos_testigos": False})
            continue
        filas.append({"propiedad": "sintaxis_cubre_algebra", "caso": m.id,
                      "origen": "construido", "evaluo": True, "error": "",
                      "mismo_veredicto": releida == datos,
                      "mismo_valor": reimpresa == superficie,
                      "mismos_testigos": True})
    return filas


def _sintaxis_casos_ida_y_vuelta(proy: Proyecto) -> list[dict]:
    """Cada caso publicado en el corpus debe sobrevivir la misma ida y vuelta que las medidas."""
    filas = []
    for ruta in sintaxis._rutas_corpus(proy.raiz):
        caso = str(ruta.relative_to(proy.raiz))
        try:
            datos = cargar_fuente_caso(ruta)
            superficie = sintaxis_caso.imprimir(datos)
            releida = sintaxis_caso.leer(superficie)
            reimpresa = sintaxis_caso.imprimir(releida)
        except Exception as e:             # noqa: BLE001
            filas.append({"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": caso,
                          "origen": "corpus", "evaluo": False,
                          "error": f"{type(e).__name__}: {e}",
                          "mismo_veredicto": False, "mismo_valor": False,
                          "mismos_testigos": False})
            continue
        filas.append({"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": caso,
                      "origen": "corpus", "evaluo": True, "error": "",
                      "mismo_veredicto": releida == datos,
                      "mismo_valor": reimpresa == superficie,
                      "mismos_testigos": True})
    return filas


def _relaciones_de_caso_generadas() -> tuple[tuple[str, list], ...]:
    """Componentes derivados de la forma L0 de un caso: relación → lista de filas planas."""
    fila_con_tipos = {
        "id": "a",
        "texto": "texto con `backticks`, comillas \"dobles\" y la palabra null",
        "entero": 7,
        "float": 2.5,
        "verdadero": True,
        "falso": False,
        "nulo": None,
        "literal_null": "null",
    }
    return (
        ("homogenea", [fila_con_tipos, {**fila_con_tipos, "id": "b", "entero": 8}]),
        ("vacia", []),
        ("heterogenea", [
            ["clave", ["id"]],
            {"id": "a", "solo_a": 1},
            {"id": "b", "solo_b": "dos", "nulo": None},
        ]),
    )


def _caso_generado(cid: str, evidencia: dict, *, medida: str | None = "meta.sonda") -> dict:
    datos = {
        "id": cid,
        "fecha": "2026-08-25",
        "origen": {"repo": "generador de metamorficas", "commit": "construido"},
        "titulo": f"Caso generado {cid}",
        "etiqueta": "verde_correcto",
        "sintoma": "Prosa con `backticks`, comillas \"dobles\".\nY un segundo renglón.",
        "como_se_detecto": "observacion",
        "medida": medida,
        "evidencia": evidencia,
        "leccion": "La superficie de casos conserva prosa, null, relaciones vacías y filas.",
    }
    if medida is None:
        datos["estado_sin_medida"] = "abierto"
        datos["sin_medida_todavia"] = (
            "El caso generado fija que `medida: null` vuelva como nulo y no como texto.")
    return datos


def _generar_casos_candidatos() -> list[dict]:
    """Generador determinista de la forma de un caso, no un catálogo manual de ejemplos."""
    relaciones = _relaciones_de_caso_generadas()
    candidatas = []

    # Una relación opcional ausente se representa por no emitir su nombre en el mapa de evidencia.
    candidatas.append(_caso_generado(
        "900-generado-relacion-ausente",
        {"presente": relaciones[0][1]},
    ))
    for cantidad in (1, 2, 3):
        candidatas.append(_caso_generado(
            f"90{cantidad}-generado-{cantidad}-relaciones",
            {nombre: filas for nombre, filas in relaciones[:cantidad]},
        ))
    candidatas.append(_caso_generado(
        "904-generado-sin-medida",
        {nombre: filas for nombre, filas in relaciones},
        medida=None,
    ))
    return candidatas


def _sintaxis_casos_cubre_casos() -> list[dict]:
    """Todo caso válido generado desde su forma de datos debe imprimirse y releerse sin pérdida."""
    filas = []
    for datos in _generar_casos_candidatos():
        try:
            superficie = sintaxis_caso.imprimir(datos)
            releida = sintaxis_caso.leer(superficie)
            reimpresa = sintaxis_caso.imprimir(releida)
        except Exception as e:             # noqa: BLE001
            filas.append({"propiedad": "sintaxis_casos_cubre_casos", "caso": datos.get("id", "?"),
                          "origen": "construido", "evaluo": False,
                          "error": f"{type(e).__name__}: {e}",
                          "mismo_veredicto": False, "mismo_valor": False,
                          "mismos_testigos": False})
            continue
        filas.append({"propiedad": "sintaxis_casos_cubre_casos", "caso": datos["id"],
                      "origen": "construido", "evaluo": True, "error": "",
                      "mismo_veredicto": releida == datos,
                      "mismo_valor": reimpresa == superficie,
                      "mismos_testigos": True})
    return filas


def hechos(catalogo: dict, casos: list[dict], macros, proy: Proyecto | None = None) -> dict:
    proy = proy or Proyecto(RAIZ)
    return {"equivalencia": [
        *_donde_compone(catalogo, casos),
        *_unir_conmuta(catalogo, casos),
        *_agrupar_sin_claves(catalogo, casos),
        *_macro_equivale_a_su_expansion(catalogo, casos, macros),
        *_sintaxis_ida_y_vuelta(proy),
        *_sintaxis_cubre_algebra(),
        *_sintaxis_casos_ida_y_vuelta(proy),
        *_sintaxis_casos_cubre_casos(),
    ]}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    proy = Proyecto(RAIZ)
    macros = macros_del_proyecto(proy)
    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros)
    casos = cargar_casos(proy.corpus)
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
