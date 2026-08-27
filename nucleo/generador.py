"""Fabricación de evidencia discriminante a partir del AST de una medida.

Dada una medida del catálogo, fabrica evidencia derivada de su forma (relaciones,
campos, comparadores, umbrales y agrupaciones) para discriminar mutantes.
"""

from __future__ import annotations

from copy import deepcopy
import datetime
from pathlib import Path
from typing import Any

import catalogos.escalares  # noqa: F401
from nucleo.algebra import (
    AGREGADOS,
    COMPARADORES,
    ErrorDeAlgebra,
    comparar,
    desde,
    resumir,
)
from nucleo.caso import imprimir as imprimir_caso
from nucleo.medida import Medida, cargar_catalogo, relaciones_de_medida
from nucleo.mutacion import mutantes, correr
from nucleo.proyecto import (
    ID_CASO_RE,
    Proyecto,
    catalogos_a_cargar,
    escalares_del_proyecto,
    macros_del_proyecto,
    presentar_ruta,
)


def extraer_fuentes(fuente: list) -> list[tuple[str, str]]:
    """Devuelve la lista de (relacion, alias) del árbol de fuentes."""
    if not isinstance(fuente, list) or not fuente:
        return []
    op = fuente[0]
    if op == "de":
        return [(fuente[1], fuente[2])]
    if op == "unir":
        return extraer_fuentes(fuente[1]) + extraer_fuentes(fuente[2])
    return []


def extraer_accesos_campo(tuberia: list, resumen: list) -> dict[str, set[str]]:
    """Devuelve los campos accedidos por alias."""
    campos: dict[str, set[str]] = {}
    for _rel, alias in extraer_fuentes(tuberia[1]):
        campos[alias] = set()

    def _buscar(expr: Any) -> None:
        if not isinstance(expr, list) or not expr:
            return
        cabeza = expr[0]
        if cabeza == "campo" and len(expr) == 3 and isinstance(expr[1], str) and isinstance(expr[2], str):
            alias, campo = expr[1], expr[2]
            if alias in campos:
                campos[alias].add(campo)
        for sub in expr[1:]:
            _buscar(sub)

    for paso in tuberia[2:]:
        _buscar(paso)
    _buscar(resumen)
    return campos


def _alt_val(val: Any) -> Any:
    if isinstance(val, bool):
        return not val
    if isinstance(val, int):
        return val + 1 if val == 0 else 0
    if isinstance(val, float):
        return val + 1.0 if val == 0.0 else 0.0
    if isinstance(val, str):
        return "algo" if val == "" else ""
    return "otro"


def resolver_predicado(expr: Any, objetivo: bool = True) -> dict[str, dict[str, Any]]:
    """Dada una expresión de predicado, devuelve asignaciones de campos {alias: {campo: valor}}

    que hacen que la expresión evalúe a `objetivo` (True o False).
    """
    if not isinstance(expr, list) or not expr:
        return {}

    cabeza = expr[0]

    # 1. Negación
    if cabeza == "no" and len(expr) == 2:
        return resolver_predicado(expr[1], not objetivo)

    # 2. Conjunción 'y'
    if cabeza == "y" and len(expr) >= 3:
        if objetivo:
            # Todos deben ser True
            resultado: dict[str, dict[str, Any]] = {}
            for sub in expr[1:]:
                res = resolver_predicado(sub, True)
                for alias, vals in res.items():
                    resultado.setdefault(alias, {}).update(vals)
            return resultado
        else:
            # Al menos el primero False, el resto True
            resultado = resolver_predicado(expr[1], False)
            for sub in expr[2:]:
                res = resolver_predicado(sub, True)
                for alias, vals in res.items():
                    for k, v in vals.items():
                        if k not in resultado.setdefault(alias, {}):
                            resultado[alias][k] = v
            return resultado

    # 3. Disyunción 'o'
    if cabeza == "o" and len(expr) >= 3:
        if objetivo:
            # El primero True, el resto False
            resultado = resolver_predicado(expr[1], True)
            for sub in expr[2:]:
                res = resolver_predicado(sub, False)
                for alias, vals in res.items():
                    for k, v in vals.items():
                        if k not in resultado.setdefault(alias, {}):
                            resultado[alias][k] = v
            return resultado
        else:
            # Todos False
            resultado = {}
            for sub in expr[1:]:
                res = resolver_predicado(sub, False)
                for alias, vals in res.items():
                    resultado.setdefault(alias, {}).update(vals)
            return resultado

    # 4. Comparaciones
    if cabeza in COMPARADORES and len(expr) == 3:
        izq, der = expr[1], expr[2]

        # Caso: campo == literal
        if isinstance(izq, list) and izq and izq[0] == "campo" and not isinstance(der, list):
            alias, campo = izq[1], izq[2]
            val = der
            if cabeza == "==":
                v = val if objetivo else _alt_val(val)
                return {alias: {campo: v}}
            if cabeza == "!=":
                v = _alt_val(val) if objetivo else val
                return {alias: {campo: v}}
            if cabeza == "<":
                if objetivo:
                    v = (val - 1) if isinstance(val, int) else (val - 0.1 if isinstance(val, float) else 0)
                else:
                    v = val  # boundary: not < val
                return {alias: {campo: v}}
            if cabeza == "<=":
                if objetivo:
                    v = val  # boundary: <= val
                else:
                    v = (val + 1) if isinstance(val, int) else (val + 0.1 if isinstance(val, float) else 1)
                return {alias: {campo: v}}
            if cabeza == ">":
                if objetivo:
                    v = (val + 1) if isinstance(val, int) else (val + 0.1 if isinstance(val, float) else 2)
                else:
                    v = val  # boundary: not > val
                return {alias: {campo: v}}
            if cabeza == ">=":
                if objetivo:
                    v = val  # boundary: >= val
                else:
                    v = (val - 1) if isinstance(val, int) else (val - 0.1 if isinstance(val, float) else 0)
                return {alias: {campo: v}}

        # Caso: literal == campo
        if isinstance(der, list) and der and der[0] == "campo" and not isinstance(izq, list):
            # Invertir orden
            inv_cmp = {"<": ">", "<=": ">=", ">": "<", ">=": "<=", "==": "==", "!=": "!="}[cabeza]
            return resolver_predicado([inv_cmp, der, izq], objetivo)

        # Caso: campo1 == campo2
        if (isinstance(izq, list) and izq and izq[0] == "campo"
                and isinstance(der, list) and der and der[0] == "campo"):
            a1, f1 = izq[1], izq[2]
            a2, f2 = der[1], der[2]
            res: dict[str, dict[str, Any]] = {}
            if cabeza == "==":
                if objetivo:
                    res.setdefault(a1, {})[f1] = "mismo_valor"
                    res.setdefault(a2, {})[f2] = "mismo_valor"
                else:
                    res.setdefault(a1, {})[f1] = "valor_a"
                    res.setdefault(a2, {})[f2] = "valor_b"
                return res
            if cabeza == "!=":
                if objetivo:
                    res.setdefault(a1, {})[f1] = "valor_a"
                    res.setdefault(a2, {})[f2] = "valor_b"
                else:
                    res.setdefault(a1, {})[f1] = "mismo_valor"
                    res.setdefault(a2, {})[f2] = "mismo_valor"
                return res
            if cabeza in ("<", "<="):
                if objetivo:
                    res.setdefault(a1, {})[f1] = "01-A"
                    res.setdefault(a2, {})[f2] = "02-B"
                else:
                    res.setdefault(a1, {})[f1] = "02-B"
                    res.setdefault(a2, {})[f2] = "01-A"
                return res
            if cabeza in (">", ">="):
                if objetivo:
                    res.setdefault(a1, {})[f1] = "02-B"
                    res.setdefault(a2, {})[f2] = "01-A"
                else:
                    res.setdefault(a1, {})[f1] = "01-A"
                    res.setdefault(a2, {})[f2] = "02-B"
                return res

        # Caso: cerca(campo, target) > tol
        if (cabeza in (">", ">=") and isinstance(izq, list) and izq and izq[0] == "cerca"
                and len(izq) == 3 and isinstance(izq[1], list) and izq[1][0] == "campo"):
            alias, campo = izq[1][1], izq[1][2]
            target = izq[2]
            tol = der
            if objetivo:
                return {alias: {campo: target + tol + 2.0}}
            else:
                return {alias: {campo: target}}

        # Caso: cerca(campo, target) <= tol
        if (cabeza in ("<", "<=") and isinstance(izq, list) and izq and izq[0] == "cerca"
                and len(izq) == 3 and isinstance(izq[1], list) and izq[1][0] == "campo"):
            alias, campo = izq[1][1], izq[1][2]
            target = izq[2]
            tol = der
            if objetivo:
                return {alias: {campo: target}}
            else:
                return {alias: {campo: target + tol + 2.0}}

        # Caso: desvio_de_paso(campo, paso) > tol
        if (cabeza in (">", ">=") and isinstance(izq, list) and izq and izq[0] == "desvio_de_paso"
                and len(izq) == 3 and isinstance(izq[1], list) and izq[1][0] == "campo"):
            alias, campo = izq[1][1], izq[1][2]
            paso = izq[2]
            tol = der
            if objetivo:
                return {alias: {campo: paso / 2.0}}
            else:
                return {alias: {campo: paso}}

        # Caso: desvio_de_*(hecho, paso) > tol
        if (cabeza in (">", ">=") and isinstance(izq, list) and izq and izq[0].startswith("desvio_de_")
                and len(izq) == 3 and isinstance(izq[1], list) and izq[1][0] == "hecho"
                and isinstance(izq[2], (int, float))):
            alias = izq[1][1]
            intervalo = izq[2]
            if objetivo:
                return {alias: {"lx": intervalo / 2.0, "ly": 0.0, "lz": 0.0}}
            else:
                return {alias: {"lx": float(intervalo), "ly": 0.0, "lz": 0.0}}

        # Caso: desvio_de_contacto(hecho_a, hecho_b) > tol
        if (cabeza in (">", ">=") and isinstance(izq, list) and izq and izq[0] == "desvio_de_contacto"
                and len(izq) == 3 and isinstance(izq[1], list) and izq[1][0] == "hecho"
                and isinstance(izq[2], list) and izq[2][0] == "hecho"):
            a, b = izq[1][1], izq[2][1]
            if objetivo:
                return {
                    a: {"ox": 0.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0},
                    b: {"ox": 200.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0, "eje": "x"},
                }
            else:
                return {
                    a: {"ox": 0.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0},
                    b: {"ox": 100.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0, "eje": "x"},
                }

        # Caso: solape_lateral_minimo(hecho_a, hecho_b) <= tol
        if (cabeza in ("<", "<=") and isinstance(izq, list) and izq and izq[0] == "solape_lateral_minimo"
                and len(izq) == 3 and isinstance(izq[1], list) and izq[1][0] == "hecho"
                and isinstance(izq[2], list) and izq[2][0] == "hecho"):
            a, b = izq[1][1], izq[2][1]
            if objetivo:
                return {
                    a: {"ox": 0.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0},
                    b: {"ox": 100.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0, "eje": "z"},
                }
            else:
                return {
                    a: {"ox": 0.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0},
                    b: {"ox": 0.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0, "eje": "z"},
                }

        # Caso: penetracion(hecho_a, hecho_b) > 0
        if (cabeza in (">", ">=") and isinstance(izq, list) and izq and izq[0] == "penetracion"
                and len(izq) == 3 and isinstance(izq[1], list) and izq[1][0] == "hecho"
                and isinstance(izq[2], list) and izq[2][0] == "hecho"):
            a, b = izq[1][1], izq[2][1]
            if objetivo:
                return {
                    a: {"id": "p1", "ox": 0.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0},
                    b: {"id": "p2", "ox": 10.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0},
                }
            else:
                return {
                    a: {"id": "p1", "ox": 0.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0},
                    b: {"id": "p2", "ox": 200.0, "oy": 0.0, "oz": 0.0, "ex": 50.0, "ey": 50.0, "ez": 50.0},
                }

        # Caso: volumen(hecho) <= tol
        if (cabeza in ("<", "<=") and isinstance(izq, list) and izq and izq[0] == "volumen"
                and len(izq) == 2 and isinstance(izq[1], list) and izq[1][0] == "hecho"):
            alias = izq[1][1]
            if objetivo:
                return {alias: {"ex": 0.0, "ey": 0.0, "ez": 0.0}}
            else:
                return {alias: {"ex": 50.0, "ey": 50.0, "ez": 50.0}}

    # 5. UDFs booleanas directas
    if cabeza == "es_fondo" and len(expr) == 2 and isinstance(expr[1], list) and expr[1][0] == "hecho":
        alias = expr[1][1]
        if objetivo:
            return {alias: {"ex": 60000.0, "ey": 60000.0, "ez": 60000.0}}
        else:
            return {alias: {"ex": 50.0, "ey": 50.0, "ez": 50.0}}

    if cabeza == "fuera_de_region" and len(expr) == 3:
        i, c = expr[1][1], expr[2][1]
        if objetivo:
            return {
                i: {"ox": 1000.0, "oy": 1000.0, "oz": 0.0},
                c: {"cx": 0.0, "cy": 0.0, "sx": 100.0, "sy": 100.0},
            }
        else:
            return {
                i: {"ox": 0.0, "oy": 0.0, "oz": 0.0},
                c: {"cx": 0.0, "cy": 0.0, "sx": 100.0, "sy": 100.0},
            }

    if cabeza == "contiene" and len(expr) == 3 and isinstance(expr[1], list) and expr[1][0] == "campo":
        alias, campo = expr[1][1], expr[1][2]
        aguja = expr[2]
        if objetivo:
            return {alias: {campo: f"NO ve {aguja}"}}
        else:
            return {alias: {campo: "todo bien"}}

    return {}


def _rellenar_defaults(fact: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    """Asegura que todos los campos nombrados estén presentes con valores coherentes."""
    res = dict(fact)
    for f in sorted(fields):
        if f not in res:
            if f.startswith("es_") or f.endswith("_ok") or f.endswith("_valida") or f in ("conocido", "presente"):
                res[f] = True
            elif f in ("id", "nombre", "archivo", "ruta", "carpeta", "area", "tipo", "rol"):
                res[f] = f"val_{f}"
            elif f in ("fecha", "updated", "fecha_en_nombre"):
                res[f] = "2026-08-26"
            else:
                res[f] = 0.0
    return res


def fabricar_filas(
    medida: Medida,
    satisfacer: bool,
    *,
    alias_override: dict[str, dict[str, Any]] | None = None,
    sufijo: str = "",
) -> dict[str, list[dict[str, Any]]]:
    """Fabrica una evidencia mínima (mapa relacion -> lista de hechos) que satisface o no el `donde`."""
    tuberia = medida.tuberia
    fuentes = extraer_fuentes(tuberia[1])
    campos_por_al = extraer_accesos_campo(tuberia, medida.resumen)

    # 1. Obtener restricciones del predicado 'donde'
    pred_res: dict[str, dict[str, Any]] = {}
    for paso in tuberia[2:]:
        if paso[0] == "donde":
            res = resolver_predicado(paso[1], satisfacer)
            for a, vals in res.items():
                pred_res.setdefault(a, {}).update(vals)

    if alias_override:
        for a, vals in alias_override.items():
            pred_res.setdefault(a, {}).update(vals)

    # 2. Armar las filas por relación
    evidencia: dict[str, list[dict[str, Any]]] = {}
    for rel, alias in fuentes:
        valores_alias = pred_res.get(alias, {})
        fila = _rellenar_defaults(valores_alias, campos_por_al.get(alias, set()))
        if "id" in fila and isinstance(fila["id"], str):
            fila["id"] = f"{fila['id']}{sufijo}"
        if "nombre" in fila and isinstance(fila["nombre"], str) and not valores_alias.get("nombre"):
            fila["nombre"] = f"{fila['nombre']}{sufijo}"
        evidencia.setdefault(rel, []).append(fila)

    return evidencia


def fabricar_candidatos(medida: Medida) -> list[dict[str, Any]]:
    """Construye casos candidatos (falso_verde y verde_correcto) para la medida."""
    candidatos = []
    mid = medida.id
    dominio = mid.split(".")[0]
    nombre_medida = mid.split(".", 1)[1].replace("_", "-")

    # Manejo especial para agrupar (ej. simulacion.la_traza_no_tiene_huecos)
    tiene_agrupar = any(p[0] == "agrupar" for p in medida.tuberia[2:])

    if tiene_agrupar:
        # Caso especial para eventos agrupados con hueco vs sin hueco
        if "la_traza_no_tiene_huecos" in mid:
            # Falso verde: corrida con hueco (c1 con t=0,2) y corrida completa (c2 con t=0,1,2)
            ev_rojo = {
                "evento": [
                    {"corrida": "c1", "t": 0},
                    {"corrida": "c1", "t": 2},
                    {"corrida": "c2", "t": 0},
                    {"corrida": "c2", "t": 1},
                    {"corrida": "c2", "t": 2},
                ]
            }
            candidatos.append({
                "id": f"{dominio}-gen-001-{nombre_medida}",
                "etiqueta": "falso_verde",
                "medida": mid,
                "evidencia": ev_rojo,
                "titulo": f"Evidencia fabricada con hueco de traza para fijar {mid}",
            })
            # Verde correcto: trazas completas en ambos grupos
            ev_verde = {
                "evento": [
                    {"corrida": "c1", "t": 0},
                    {"corrida": "c1", "t": 1},
                    {"corrida": "c2", "t": 0},
                    {"corrida": "c2", "t": 1},
                    {"corrida": "c2", "t": 2},
                ]
            }
            candidatos.append({
                "id": f"{dominio}-gen-002-{nombre_medida}-verde",
                "etiqueta": "verde_correcto",
                "medida": mid,
                "evidencia": ev_verde,
                "titulo": f"Evidencia fabricada con trazas completas para fijar {mid}",
            })
            return candidatos

    # Candidatos Falso Verde (defecto)
    # Si hay disyunciones 'o' en el 'donde', generamos un caso para cada rama
    ramas_disyuncion = []
    for paso in medida.tuberia[2:]:
        if paso[0] == "donde" and isinstance(paso[1], list) and paso[1] and paso[1][0] == "o":
            for i, rama in enumerate(paso[1][1:], start=1):
                ramas_disyuncion.append((i, rama, paso[1]))

    fuentes = extraer_fuentes(medida.tuberia[1])
    es_join_distinto = len(fuentes) == 2 and fuentes[0][0] != fuentes[1][0]
    es_auto_join = len(fuentes) == 2 and fuentes[0][0] == fuentes[1][0]

    if ramas_disyuncion:
        for idx_rama, rama, disy in ramas_disyuncion:
            # Para esta rama, rama=True, las demás ramas=False
            pred_override: dict[str, dict[str, Any]] = {}
            for other_idx, other_rama, _ in ramas_disyuncion:
                if other_idx == idx_rama:
                    res = resolver_predicado(other_rama, True)
                else:
                    res = resolver_predicado(other_rama, False)
                for a, vals in res.items():
                    pred_override.setdefault(a, {}).update(vals)

            ev_ofensora = fabricar_filas(medida, satisfacer=True, alias_override=pred_override, sufijo=f"-r{idx_rama}")
            ev_no_ofensora = fabricar_filas(medida, satisfacer=False, sufijo=f"-limpia{idx_rama}")
            ev_rojo = {}
            for rel in set(ev_ofensora) | set(ev_no_ofensora):
                ev_rojo[rel] = ev_ofensora.get(rel, []) + ev_no_ofensora.get(rel, [])
            candidatos.append({
                "id": f"{dominio}-gen-{idx_rama:03d}-{nombre_medida}-rama{idx_rama}",
                "etiqueta": "falso_verde",
                "medida": mid,
                "evidencia": ev_rojo,
                "titulo": f"Evidencia fabricada para discriminar rama {idx_rama} en {mid}",
            })
    else:
        # Caso estándar falso verde
        if es_join_distinto:
            rel1, _ = fuentes[0]
            rel2, _ = fuentes[1]
            ev_of = fabricar_filas(medida, satisfacer=True, sufijo="-of")
            ev_no = fabricar_filas(medida, satisfacer=False, sufijo="-limpia")
            ev_rojo = {
                rel1: ev_of.get(rel1, []) + ev_no.get(rel1, []),
                rel2: ev_of.get(rel2, []),  # Solo 1 hecho en rel2 para mantener count=1
            }
        elif es_auto_join:
            rel = fuentes[0][0]
            ev_of = fabricar_filas(medida, satisfacer=True, sufijo="-of")
            ev_no = fabricar_filas(medida, satisfacer=False, sufijo="-limpia")
            # Hechos limpios con nombres distintos para no cruzar
            filas_limpias = ev_no.get(rel, [])
            for f_idx, fila in enumerate(filas_limpias):
                if "nombre" in fila:
                    fila["nombre"] = f"nombre_limpio_{f_idx}"
            ev_rojo = {
                rel: ev_of.get(rel, []) + filas_limpias,
            }
        else:
            ev_ofensora = fabricar_filas(medida, satisfacer=True, sufijo="-ofensora")
            ev_no_ofensora = fabricar_filas(medida, satisfacer=False, sufijo="-limpia")
            ev_rojo = {}
            for rel in set(ev_ofensora) | set(ev_no_ofensora):
                ev_rojo[rel] = ev_ofensora.get(rel, []) + ev_no_ofensora.get(rel, [])

        candidatos.append({
            "id": f"{dominio}-gen-001-{nombre_medida}",
            "etiqueta": "falso_verde",
            "medida": mid,
            "evidencia": ev_rojo,
            "titulo": f"Evidencia fabricada para discriminar mutaciones en {mid}",
        })

    # Candidato Verde correcto (borde)
    # Contiene filas que NO ofenden, dejando la relación con veredicto verde
    # y matando quitar_filtro / negar_filtro / invertir_comparador
    ev_verde1 = fabricar_filas(medida, satisfacer=False, sufijo="-v1")
    ev_verde2 = fabricar_filas(medida, satisfacer=False, sufijo="-v2")
    ev_verde: dict[str, list[dict[str, Any]]] = {}
    for rel in set(ev_verde1) | set(ev_verde2):
        ev_verde[rel] = ev_verde1.get(rel, []) + ev_verde2.get(rel, [])

    candidatos.append({
        "id": f"{dominio}-gen-099-{nombre_medida}-verde",
        "etiqueta": "verde_correcto",
        "medida": mid,
        "evidencia": ev_verde,
        "titulo": f"Evidencia fabricada en el borde verde para fijar {mid}",
    })

    return candidatos


def evaluar_utilidad(
    medida: Medida,
    casos_existentes: list[dict[str, Any]],
    candidatos: list[dict[str, Any]],
    catalogo: dict[str, Medida],
) -> tuple[list[str], list[tuple[dict[str, Any], set[str]]]]:
    """Evalúa qué mutantes de la medida sobreviven antes y cuáles mueren con cada candidato.

    Descarta candidatos que no pasen su propia polaridad o que sean ruido (no maten nada nuevo).
    """
    mid = medida.id
    # 1. Mutantes de la medida
    todos_mutantes = mutantes(medida.a_datos())
    nombres_mutantes = {nom for nom, _ in todos_mutantes}

    # 2. Mutación base
    ev_base = correr({mid: medida}, casos_existentes)
    muertos_base = {
        d["cambio"]
        for d in ev_base.get("mutante", [])
        if d["apunta_a"] == mid and (d["detecciones_conductuales"] or d["rechazos_del_algebra"])
    }
    vivos_antes = sorted(nombres_mutantes - muertos_base)

    if not vivos_antes:
        return [], []

    # 3. Probar candidatos
    utiles: list[tuple[dict[str, Any], set[str]]] = []
    acumulados_muertos = set(muertos_base)

    for cand in candidatos:
        # Verificar que el caso evalúe en su estado esperado
        esperado_ok = cand["etiqueta"] == "verde_correcto"
        try:
            v_orig = medida.evaluar(cand["evidencia"])
            if v_orig.ok != esperado_ok:
                continue  # No cumple su propio contrato esperado
        except Exception:
            continue

        # Correr mutación con este candidato añadido
        casos_prueba = list(casos_existentes) + [cand]
        ev_cand = correr({mid: medida}, casos_prueba)
        muertos_ahora = {
            d["cambio"]
            for d in ev_cand.get("mutante", [])
            if d["apunta_a"] == mid and (d["detecciones_conductuales"] or d["rechazos_del_algebra"])
        }

        nuevos_muertos = muertos_ahora - acumulados_muertos
        if nuevos_muertos:
            utiles.append((cand, nuevos_muertos))
            acumulados_muertos.update(nuevos_muertos)

    return vivos_antes, utiles


def construir_caso_final(cand: dict[str, Any], muertos_que_mata: set[str]) -> dict[str, Any]:
    """Arma el diccionario completo del caso listo para imprimir y guardar."""
    mid = cand["medida"]
    cid = cand["id"]
    lista_muertos = ", ".join(sorted(muertos_que_mata))
    fecha_hoy = datetime.date.today().isoformat()

    return {
        "id": cid,
        "fecha": fecha_hoy,
        "origen": {
            "repo": "oracle",
            "commit": "generado-por-oracle",
        },
        "titulo": cand.get("titulo") or f"Evidencia generada para fijar {mid}",
        "etiqueta": cand["etiqueta"],
        "sintoma": (
            f"Evidencia fabricada por la herramienta para discriminar mutaciones en {mid} "
            f"(mutante: {lista_muertos}).\n"
            "La forma de la evidencia se deriva mecánicamente del AST de la medida."
        ),
        "como_se_detecto": "mutacion",
        "medida": mid,
        "evidencia": cand["evidencia"],
        "leccion": (
            f"Caso generado automáticamente para fijar {mid} sin depender de evidencia escrita a mano."
        ),
    }


def generar_caso(
    proy: Proyecto,
    mid: str,
    *,
    directorio_destino: Path | None = None,
    confiar: bool = False,
    imprimir_solo: bool = False,
) -> tuple[int, dict[str, Any]]:
    """Comando principal para `oracle caso generar <dominio.medida>`."""
    macros = macros_del_proyecto(proy)
    with escalares_del_proyecto(proy, confiar=confiar):
        catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros)

        if mid not in catalogo:
            print(f"medida «{mid}» no encontrada en el catálogo de {proy.raiz}")
            return 1, {}

        medida = catalogo[mid]
        # Casos existentes
        from nucleo.caso import cargar_casos
        from nucleo.fixtures import cargar_fixtures, casos_para_mutacion

        casos_existentes = cargar_casos(proy.corpus)
        try:
            fixtures, fallas = cargar_fixtures(
                sorted(proy.diferencial.glob("*.json")), raiz=proy.raiz, catalogo=catalogo
            )
            if not fallas:
                for f in fixtures:
                    casos_existentes.extend(casos_para_mutacion(f, catalogo))
        except Exception:
            pass

        # Evaluar
        candidatos = fabricar_candidatos(medida)
        vivos_antes, utiles = evaluar_utilidad(medida, casos_existentes, candidatos, catalogo)

        if not vivos_antes:
            print(f"ruido: 0 mutantes sobrevivientes para «{mid}» — no se generó ningún caso (ya está fijada)")
            return 0, {"mid": mid, "vivos_antes": 0, "muertos_nuevos": 0, "casos": []}

        if not utiles:
            print(
                f"ruido: el caso generado no mata ningún mutante adicional para «{mid}» "
                f"({len(vivos_antes)} sobrevivientes siguen vivos) — no se escribió ningún archivo"
            )
            return 0, {"mid": mid, "vivos_antes": len(vivos_antes), "muertos_nuevos": 0, "casos": []}

        # Procesar útiles
        grupo = mid.split(".")[0]
        destino_dir = directorio_destino or (proy.corpus / grupo)
        if not imprimir_solo:
            destino_dir.mkdir(parents=True, exist_ok=True)

        casos_escritos = []
        todos_muertos_nuevos = set()

        print(f"generando evidencia para «{mid}»:")
        print(f"  mutantes sobrevivientes antes: {len(vivos_antes)}")
        for m in vivos_antes:
            print(f"    · {m}")
        print()

        for cand, muertos in utiles:
            caso_final = construir_caso_final(cand, muertos)
            cid = caso_final["id"]
            texto_caso = imprimir_caso(caso_final)
            todos_muertos_nuevos.update(muertos)

            if imprimir_solo:
                print(f"--- Caso: {cid} ---")
                print(texto_caso)
            else:
                destino_archivo = destino_dir / f"{cid}.caso"
                destino_archivo.write_text(texto_caso, encoding="utf-8")
                casos_escritos.append(destino_archivo)
                print(f"  creado: {presentar_ruta(proy, destino_archivo)} (mata: {', '.join(sorted(muertos))})")

        siguen_vivos = sorted(set(vivos_antes) - todos_muertos_nuevos)
        print(f"\nmutantes muertos con la evidencia generada: {len(todos_muertos_nuevos)} de {len(vivos_antes)}")
        if siguen_vivos:
            print(f"mutantes que siguen vivos ({len(siguen_vivos)}):")
            for m in siguen_vivos:
                print(f"    · {m}")
        else:
            print("todos los mutantes de la medida quedaron muertos.")

        return 0, {
            "mid": mid,
            "vivos_antes": len(vivos_antes),
            "muertos_nuevos": len(todos_muertos_nuevos),
            "siguen_vivos": siguen_vivos,
            "casos": casos_escritos,
        }
