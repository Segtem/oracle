"""Fabricación de evidencia discriminante a partir del AST de una medida.

Dada una medida del catálogo, fabrica evidencia derivada de su forma (relaciones,
campos, comparadores, umbrales y agrupaciones) para discriminar mutantes.
"""

from __future__ import annotations

from copy import deepcopy
import datetime
import itertools
import math
from pathlib import Path
from typing import Any

import catalogos.escalares  # noqa: F401
from nucleo.algebra import (
    AGREGADOS,
    COMPARADORES,
    ErrorDeAlgebra,
    LimitesAlgebra,
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

    # 5. UDFs booleanas directas. Sólo las escalares del propio Oracle: las de un consumidor no son
    # del núcleo (hasta el 2026-09-29 había siete, escritas por nombre y sin casos generados).
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
    claves_de_sin: dict[str, set[str]] = {}
    # El álgebra ya validó la forma: un `sin` es ["sin", ["de", rel, alias], condición].
    for paso in tuberia[2:]:
        if paso[0] == "sin":
            for _campo, otro, campo_otro in _igualdades_con(paso[2], paso[1][2]):
                claves_de_sin.setdefault(otro, set()).add(campo_otro)
    evidencia: dict[str, list[dict[str, Any]]] = {}
    for rel, alias in fuentes:
        valores_alias = pred_res.get(alias, {})
        fila = _rellenar_defaults(valores_alias, campos_por_al.get(alias, set()))
        if "id" in fila and isinstance(fila["id"], str):
            fila["id"] = f"{fila['id']}{sufijo}"
        if "nombre" in fila and isinstance(fila["nombre"], str) and not valores_alias.get("nombre"):
            fila["nombre"] = f"{fila['nombre']}{sufijo}"
        # Una clave con la que un `sin` busca pareja no puede quedar en su valor por defecto: la
        # compartirían la fila que ofende y la que no, y la pareja salvaría a las dos. Se vuelve
        # un texto único en TODA fila fabricada, para que las dos tengan el mismo tipo.
        for campo in claves_de_sin.get(alias, ()):
            if campo not in valores_alias:
                fila[campo] = f"{campo}-{next(_CLAVES)}"
        evidencia.setdefault(rel, []).append(fila)

    return evidencia


_CLAVES = itertools.count()


def _igualdades_con(expr: Any, alias: str):
    """(campo de `alias`, alias ajeno, campo ajeno) por cada `==` entre campos dentro de conjunciones.

    Un `==` entre dos campos del mismo alias no une nada con la fila de afuera y no se cuenta."""
    if not isinstance(expr, list):
        return
    if expr[0] == "y":
        for sub in expr[1:]:
            yield from _igualdades_con(sub, alias)
    elif expr[0] == "==" and all(isinstance(lado, list) and lado[0] == "campo" for lado in expr[1:]):
        lados = {expr[1][1]: expr[1][2], expr[2][1]: expr[2][2]}
        if alias in lados and len(lados) == 2:
            (otro, campo_otro), = ((a, c) for a, c in lados.items() if a != alias)
            yield lados[alias], otro, campo_otro


def _contiene_de(expr: Any, alias: str) -> dict[str, list[str]]:
    """Los literales que `contiene` exige a cada campo de `alias`, en conjunción."""
    salida: dict[str, list[str]] = {}
    if isinstance(expr, list) and expr[0] == "y":
        for sub in expr[1:]:
            for campo, literales in _contiene_de(sub, alias).items():
                salida.setdefault(campo, []).extend(literales)
    elif (isinstance(expr, list) and expr[0] == "contiene"
          and expr[1][:2] == ["campo", alias] and isinstance(expr[2], str)):
        salida[expr[1][2]] = [expr[2]]
    return salida


def _campos_de(expr: Any, alias: str) -> set[str]:
    if not isinstance(expr, list):
        return set()
    if expr[0] == "campo" and expr[1] == alias:
        return {expr[2]}
    return set().union(*(_campos_de(sub, alias) for sub in expr[1:]))


def salvar_con_parejas(medida: Medida, evidencia: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
    """Agrega, por cada paso `sin`, la fila que hace que la tupla de `evidencia` NO pase el `sin`.

    `evidencia` es la salida de UNA llamada a `fabricar_filas`: una fila por fuente. La pareja cumple
    la condición del `sin`: los literales salen de `resolver_predicado` y cada igualdad con un campo
    de la tupla copia el valor real de esa fila, no un marcador. Sin esto, un `sin` dejaba pasar
    todas las filas fabricadas y el verde no se podía fabricar (tarea caso-generar-no).
    """
    # ponytail: si el `sin` niega la misma relación que una fuente, la pareja también entra como
    # fila de esa fuente; el candidato lo comprueba `fabricar_candidatos` y, si no da, se rechaza.
    salida = {rel: [dict(fila) for fila in filas] for rel, filas in evidencia.items()}
    tupla = {alias: salida[rel][0] for rel, alias in extraer_fuentes(medida.tuberia[1]) if salida.get(rel)}
    for paso in medida.tuberia[2:]:
        if paso[0] != "sin":
            continue
        _, rel, alias = paso[1]
        pareja = _rellenar_defaults(resolver_predicado(paso[2], True).get(alias, {}), _campos_de(paso[2], alias))
        # `fabricar_filas` ya le dio a cada clave de un `sin` un valor propio en la tupla.
        for campo, otro, campo_otro in _igualdades_con(paso[2], alias):
            pareja[campo] = tupla[otro][campo_otro]
        for campo, literales in _contiene_de(paso[2], alias).items():
            pareja[campo] = " ".join(literales)
        salida.setdefault(rel, []).append(pareja)
    return salida


class GeneracionNoPosible(ValueError):
    """La evidencia propuesta no alcanza a demostrar la polaridad pedida."""


def fabricar_candidatos(medida: Medida) -> list[dict[str, Any]]:
    """Entrega candidatos con su polaridad comprobada, o explica por qué no puede fabricarlos.

    Repetir filas sólo escala un conteo sobre una fuente sin agrupación. No se extrapola a un
    máximo, una unión o grupos: si la heurística no produce el veredicto, se rechaza la propuesta.
    """
    candidatos = _proponer_candidatos(medida)
    for candidato in candidatos:
        esperado = candidato["etiqueta"] == "verde_correcto"
        evidencia = candidato["evidencia"]
        try:
            veredicto = medida.evaluar(evidencia)
            if (veredicto.ok != esperado and not esperado
                    and medida.resumen[1] == "contar"
                    and medida.tuberia[1][0] == "de"
                    and all(paso[0] == "donde" for paso in medida.tuberia[2:])
                    and medida.op in ("<", "<=")
                    and veredicto.valor > 0):
                necesarias = (math.floor(medida.limite) + 1 if medida.op == "<="
                              else math.ceil(medida.limite))
                repeticiones = (necesarias + veredicto.valor - 1) // veredicto.valor
                limite_filas = LimitesAlgebra().filas_por_relacion
                if any(len(filas) * repeticiones > limite_filas for filas in evidencia.values()):
                    raise GeneracionNoPosible(
                        f"{medida.id}: superar el umbral {medida.op} {medida.limite} "
                        f"excede el presupuesto de {limite_filas} filas por relación")
                evidencia = {rel: [deepcopy(fila) for _ in range(repeticiones) for fila in filas]
                             for rel, filas in evidencia.items()}
                candidato["evidencia"] = evidencia
                veredicto = medida.evaluar(evidencia)
        except ErrorDeAlgebra as error:
            raise GeneracionNoPosible(
                f"{medida.id}: no se pudo evaluar el candidato {candidato['id']}: {error}") from error
        if candidato.get("espera") == "sin_evidencia":
            if not veredicto.sin_evidencia:
                raise GeneracionNoPosible(
                    f"{medida.id}: con «{candidato['vacia']}» vacía la medida concluyó igual; "
                    "su `requiere` no la protege")
            continue
        if veredicto.sin_evidencia:
            raise GeneracionNoPosible(
                f"{medida.id}: el candidato carece de la relación requerida "
                f"{veredicto.sin_evidencia}; sin evidencia no demuestra un rojo")
        if veredicto.ok != esperado:
            raise GeneracionNoPosible(
                f"{medida.id}: no se pudo fabricar {candidato['etiqueta']} con "
                f"{medida.resumen[1]} y umbral {medida.op} {medida.limite}; "
                f"la evidencia propuesta da valor {veredicto.valor}, "
                f"verde={veredicto.ok}. Hace falta evidencia del dominio")
    return candidatos


def _proponer_candidatos(medida: Medida) -> list[dict[str, Any]]:
    """Propone evidencia heurística; todavía no afirma que respete la polaridad."""
    candidatos = []
    mid = medida.id
    dominio = mid.split(".")[0]
    nombre_medida = mid.split(".", 1)[1].replace("_", "-")

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
                rel2: ev_of.get(rel2, []),  # Propuesta mínima; fabricar_candidatos verifica el umbral.
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
            ev_no_ofensora = salvar_con_parejas(medida, fabricar_filas(medida, satisfacer=False, sufijo="-limpia"))
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
    ev_verde1 = salvar_con_parejas(medida, fabricar_filas(medida, satisfacer=False, sufijo="-v1"))
    ev_verde2 = salvar_con_parejas(medida, fabricar_filas(medida, satisfacer=False, sufijo="-v2"))
    ev_verde: dict[str, list[dict[str, Any]]] = {}
    for rel in set(ev_verde1) | set(ev_verde2):
        ev_verde[rel] = ev_verde1.get(rel, []) + ev_verde2.get(rel, [])

    requeridas = [r for r in medida.requiere if isinstance(r, str)]
    if requeridas:
        # La relación que la medida necesita, vacía: fija `requiere`, que ningún otro candidato
        # toca porque todos traen filas.
        candidatos.append({
            "id": f"{dominio}-gen-097-{nombre_medida}-sin-evidencia",
            "etiqueta": "falso_verde",
            "espera": "sin_evidencia",
            "vacia": requeridas[0],
            "medida": mid,
            "evidencia": {requeridas[0]: []},
            "titulo": f"Sin filas de {requeridas[0]}, {mid} no puede concluir",
        })

    if any(paso[0] == "sin" for paso in medida.tuberia[2:]):
        # La fila que ofendería, salvada por su pareja, y una limpia SIN pareja. Mata quitar el
        # `sin` (la salvada cuenta) y aflojar el `donde` (la limpia cuenta), que el verde de dos
        # filas limpias no distingue.
        salvada = salvar_con_parejas(medida, fabricar_filas(medida, satisfacer=True, sufijo="-salvada"))
        limpia = fabricar_filas(medida, satisfacer=False, sufijo="-sola")
        if not any(paso[0] == "donde" for paso in medida.tuberia[2:]):
            # Sin `donde` nada deja afuera a la limpia: sólo la salva su pareja.
            limpia = salvar_con_parejas(medida, limpia)
        candidatos.append({
            "id": f"{dominio}-gen-098-{nombre_medida}-salvada",
            "etiqueta": "verde_correcto",
            "medida": mid,
            "evidencia": {rel: salvada.get(rel, []) + limpia.get(rel, []) for rel in set(salvada) | set(limpia)},
            "titulo": f"Evidencia fabricada donde el `sin` salva la fila que ofendería en {mid}",
        })

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
            if cand.get("espera") == "sin_evidencia":
                if not v_orig.sin_evidencia:
                    continue
            elif v_orig.ok != esperado_ok:
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
        # El campo no es decorativo: es lo único que separa esta evidencia —que discrimina un
        # mutante y no dice nada del mundo— de la que se transcribió de algo que pasó. Sin él, un
        # corpus generado se cuenta igual que uno observado y el verde deja de significar.
        "procedencia": "generada",
        "titulo": cand.get("titulo") or f"Evidencia generada para fijar {mid}",
        "etiqueta": cand["etiqueta"],
        **({"espera": cand["espera"]} if "espera" in cand else {}),
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
        vivos_antes, _ = evaluar_utilidad(medida, casos_existentes, [], catalogo)

        if not vivos_antes:
            print(f"ruido: 0 mutantes sobrevivientes para «{mid}» — no se generó ningún caso (ya está fijada)")
            return 0, {"mid": mid, "vivos_antes": 0, "muertos_nuevos": 0, "casos": []}

        try:
            candidatos = fabricar_candidatos(medida)
        except GeneracionNoPosible as error:
            print(f"generación no posible: {error} — no se escribió ningún archivo")
            return 1, {"mid": mid, "vivos_antes": len(vivos_antes),
                       "muertos_nuevos": 0, "casos": [], "error": str(error)}
        vivos_antes, utiles = evaluar_utilidad(medida, casos_existentes, candidatos, catalogo)

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
