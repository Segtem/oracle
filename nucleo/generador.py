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
    """Devuelve la lista de (relacion, alias) del árbol de fuentes: `de` o `unir` (algebra.FUENTES)."""
    if fuente[0] == "unir":
        return extraer_fuentes(fuente[1]) + extraer_fuentes(fuente[2])
    return [(fuente[1], fuente[2])]


def extraer_accesos_campo(tuberia: list, resumen: list) -> dict[str, set[str]]:
    """Devuelve los campos accedidos por alias."""
    campos: dict[str, set[str]] = {}
    for _rel, alias in extraer_fuentes(tuberia[1]):
        campos[alias] = set()

    def _buscar(expr: Any) -> None:
        # El árbol trae listas vacías (una medida sin agregados, por ejemplo).
        if not isinstance(expr, list) or not expr:
            return
        if expr[0] == "campo" and expr[1] in campos:
            campos[expr[1]].add(expr[2])
        for sub in expr[1:]:
            _buscar(sub)

    for paso in tuberia[2:]:
        _buscar(paso)
    _buscar(resumen)
    return campos


def _alt_val(val: Any) -> Any:
    """Un valor distinto de `val` y del mismo tipo; cuál, no importa."""
    if isinstance(val, (bool, int, float)):
        return type(val)(not val)
    if isinstance(val, str):
        return "algo" if val == "" else ""
    return "otro"


_OPUESTO = {"<": ">=", "<=": ">", ">": "<=", ">=": "<", "==": "!=", "!=": "=="}
_ESPEJO = {"<": ">", "<=": ">=", ">": "<", ">=": "<=", "==": "==", "!=": "!="}
# Dos campos comparados entre sí: textos que cumplen el comparador en orden lexicográfico.
_PARES_DE_CAMPOS = {"==": ("mismo_valor", "mismo_valor"), "!=": ("valor_a", "valor_b"),
                    "<": ("01-A", "02-B"), "<=": ("01-A", "02-B"),
                    ">": ("02-B", "01-A"), ">=": ("02-B", "01-A")}


def _menor(val):
    return math.nextafter(val, -math.inf) if isinstance(val, float) else val - 1


def _mayor(val):
    return math.nextafter(val, math.inf) if isinstance(val, float) else val + 1


def _valor_que_cumple(op: str, val: Any) -> Any:
    """Un valor `v` con `v op val` cierto; None si `val` no es un número que se pueda ordenar."""
    if op == "==":
        return val
    if op == "!=":
        return _alt_val(val)
    if isinstance(val, bool) or not isinstance(val, (int, float)):
        return None
    if op in ("<=", ">="):
        return val
    return _menor(val) if op == "<" else _mayor(val)


def resolver_predicado(expr: Any, objetivo: bool) -> dict[str, dict[str, Any]]:
    """Dada una expresión de predicado, devuelve asignaciones de campos {alias: {campo: valor}}

    que hacen que la expresión evalúe a `objetivo` (True o False).
    """
    if not isinstance(expr, list):
        return {}

    cabeza = expr[0]

    # 1. Negación
    if cabeza == "no":
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

    # 4. Comparaciones: se resuelve el comparador que tiene que cumplirse (el mismo si `objetivo`, el
    # opuesto si no) y se fabrica un valor que lo cumpla. La propiedad la fija el test: el valor
    # devuelto hace que la comparación dé `objetivo`.
    if cabeza in COMPARADORES:
        izq, der = expr[1], expr[2]
        op = cabeza if objetivo else _OPUESTO[cabeza]
        es_campo = lambda nodo: isinstance(nodo, list) and nodo[0] == "campo"  # noqa: E731

        if es_campo(izq) and es_campo(der):
            v1, v2 = _PARES_DE_CAMPOS[op]
            res: dict[str, dict[str, Any]] = {}
            res.setdefault(izq[1], {})[izq[2]] = v1
            res.setdefault(der[1], {})[der[2]] = v2
            return res
        if es_campo(der) and not isinstance(izq, list):
            return resolver_predicado([_ESPEJO[cabeza], der, izq], objetivo)
        if es_campo(izq) and not isinstance(der, list):
            v = _valor_que_cumple(op, der)
            return {} if v is None else {izq[1]: {izq[2]: v}}
        # cerca(campo, blanco) op tolerancia: la distancia es |campo - blanco|.
        if op not in ("==", "!=") and isinstance(izq, list) and izq[0] == "cerca" and es_campo(izq[1]):
            blanco = izq[2]
            v = blanco if op in ("<", "<=") else _mayor(blanco + der)
            return {izq[1][1]: {izq[1][2]: v}}

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
        # El sufijo distingue filas, pero no puede tocar un valor que el `donde` fijó: un `id` que
        # tiene que casar con el campo de otra relación dejaba de casar y el join no producía nada.
        if "id" in fila and isinstance(fila["id"], str) and "id" not in valores_alias:
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
        elif len(fuentes) == 2:  # una relación unida consigo misma
            (rel, _), _ = fuentes
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

    # Toda relación que la medida lee tiene que estar en la evidencia, aunque sea vacía: el álgebra
    # no evalúa una relación ausente. Pasaba con un `sin` en las ramas de join y de disyunción.
    for candidato in candidatos:
        for rel in relaciones_de_medida(medida):
            candidato["evidencia"].setdefault(rel, [])

    return candidatos


# ── Búsqueda: evidencia que separa a la medida de un mutante, encogida al mínimo ────────────────
#
# Las reglas de `_proponer_candidatos` derivan la evidencia de la forma de la medida y no cubren
# todas las formas: un campo cambiado por otro sobrevive si las filas fabricadas tienen el mismo
# valor en los dos, y una escalar que espera un tipo del dominio falla con un `0.0` inventado. La
# búsqueda no deduce: parte de la evidencia que ya hay (la que proponen las reglas y la del corpus
# de la medida), la perturba de a un cambio por vez y se queda con la primera en la que la medida
# y el mutante dan veredictos distintos. Después la encoge, como el *shrinking* de las pruebas
# basadas en propiedades: saca filas y simplifica valores mientras la discrepancia siga. Todo es
# determinista —el mismo catálogo da los mismos casos— y nada llama a un modelo.

PRESUPUESTO_BUSQUEDA = 3000     # evaluaciones por mutante; alcanza para dos cambios sobre semillas chicas


def _literales(expr: Any, salida: list) -> list:
    """Los números, textos y booleanos que aparecen escritos en la medida, en orden y sin repetir."""
    if isinstance(expr, list):
        # La cabeza es el operador; `campo` y `de` sólo nombran relaciones, alias y campos.
        if expr and expr[0] not in ("campo", "de"):
            for sub in expr[1:] if isinstance(expr[0], str) else expr:
                _literales(sub, salida)
    elif isinstance(expr, (bool, int, float, str)) and expr not in salida:
        salida.append(expr)
    return salida


def _alternativas(valor: Any, fila: dict, literales: list) -> list:
    """Valores de prueba para un campo: los de la medida, los de la misma fila y los vecinos."""
    if isinstance(valor, bool):
        propios = [not valor]
    elif isinstance(valor, (int, float)):
        propios = [valor + 1, valor - 1, 0, -valor, valor * 2 + 1]
    elif isinstance(valor, str):
        propios = ["", f"{valor}-otro"]
    else:
        return []
    del_mismo_tipo = [v for v in [*literales, *fila.values()]
                      if type(v) is type(valor) or (isinstance(v, (int, float)) and isinstance(valor, (int, float))
                                                    and not isinstance(v, bool) and not isinstance(valor, bool))]
    salida = []
    for v in [*del_mismo_tipo, *propios]:
        if v != valor and v not in salida:
            salida.append(v)
    return salida


def _vecinos(evidencia: dict, literales: list):
    """Cada evidencia a un cambio de distancia, en un orden fijo."""
    for rel in sorted(evidencia):
        filas = evidencia[rel]
        for i, fila in enumerate(filas):
            for campo in sorted(fila):
                for v in _alternativas(fila[campo], fila, literales):
                    nueva = {**evidencia, rel: [*filas[:i], {**fila, campo: v}, *filas[i + 1:]]}
                    yield nueva
            yield {**evidencia, rel: [*filas, dict(fila)]}
            yield {**evidencia, rel: [*filas[:i], *filas[i + 1:]]}


def _veredicto(medida: Medida, evidencia: dict):
    try:
        return medida.evaluar(evidencia)
    except Exception:            # noqa: BLE001  una evidencia que no evalúa no separa nada
        return None


def _separa(original: Medida, mutante: Medida, evidencia: dict) -> bool | None:
    """El `ok` de la original si ella y el mutante discrepan en esta evidencia; None si no."""
    base = _veredicto(original, evidencia)
    if base is None or base.sin_evidencia:
        return None
    otro = _veredicto(mutante, evidencia)
    if otro is None or otro.ok == base.ok:
        return None
    return base.ok


def _simplificaciones(evidencia: dict):
    """Cada evidencia con una fila menos, y después cada una con un valor llevado a 0, "" o false."""
    for rel in sorted(evidencia):
        for i in range(len(evidencia[rel]) - 1, -1, -1):
            yield {**evidencia, rel: evidencia[rel][:i] + evidencia[rel][i + 1:]}
    for rel in sorted(evidencia):
        for i, fila in enumerate(evidencia[rel]):
            for campo in sorted(fila):
                valor = fila[campo]
                simple = (False if isinstance(valor, bool) else 0 if isinstance(valor, (int, float))
                          else "" if isinstance(valor, str) else valor)
                if simple != valor:
                    yield {**evidencia, rel: [*evidencia[rel][:i], {**fila, campo: simple}, *evidencia[rel][i + 1:]]}


def _encoger(original: Medida, mutante: Medida, evidencia: dict, ok: bool) -> dict:
    """Saca filas y simplifica valores mientras la medida y el mutante sigan discrepando igual.
    Cada paso aceptado achica la evidencia y vuelve a empezar, así que termina."""
    for menor in _simplificaciones(evidencia):
        if _separa(original, mutante, menor) is ok:
            return _encoger(original, mutante, menor, ok)
    return evidencia


def _buscar(original: Medida, mutante: Medida, semillas: list[dict], literales: list,
            presupuesto: int) -> tuple[dict, bool] | None:
    """Anchura primero desde las semillas, hasta dos cambios: la primera evidencia que separa."""
    gastado = 0
    frontera = []
    for semilla in semillas:
        ok = _separa(original, mutante, semilla)
        if ok is not None:
            return semilla, ok
        frontera.append(semilla)
    for _profundidad in range(2):
        siguiente = []
        for ev in frontera:
            for vecina in _vecinos(ev, literales):
                gastado += 1
                if gastado > presupuesto:
                    return None
                ok = _separa(original, mutante, vecina)
                if ok is not None:
                    return vecina, ok
                siguiente.append(vecina)
        frontera = siguiente
    return None


def buscar_candidatos(medida: Medida, casos_existentes: list[dict[str, Any]], *,
                      presupuesto: int = PRESUPUESTO_BUSQUEDA) -> list[dict[str, Any]]:
    """Los candidatos de las reglas que respetan su polaridad, más uno buscado por mutante que ni
    el corpus ni esos candidatos matan. Cada buscado lleva la etiqueta que la medida original le da."""
    mid = medida.id
    dominio = mid.split(".")[0]
    nombre_medida = mid.split(".", 1)[1].replace("_", "-")
    try:
        reglas = fabricar_candidatos(medida)
    except GeneracionNoPosible:
        reglas = []
    leidas = relaciones_de_medida(medida)

    def completa(evidencia: dict) -> dict:
        return {rel: [dict(f) for f in evidencia.get(rel, []) if isinstance(f, dict)] for rel in leidas}

    semillas = [completa(c["evidencia"]) for c in _proponer_candidatos(medida)]
    semillas += [completa(c["evidencia"]) for c in casos_existentes if c.get("medida") == mid]
    muertos = {d["cambio"] for d in correr({mid: medida}, [*casos_existentes, *reglas])["mutante"]
               if d["detecciones_conductuales"] or d["rechazos_del_algebra"]}
    literales = _literales([medida.tuberia, medida.resumen, medida.limite], [])
    buscados = []
    for nombre, datos in mutantes(medida.a_datos()):
        if nombre in muertos:
            continue
        try:
            mutante = Medida.de_datos(datos)
        except Exception:        # noqa: BLE001  un mutante que no construye ya lo mata el álgebra
            continue
        if any(_separa(medida, mutante, b["evidencia"]) is not None for b in buscados):
            continue             # un caso ya buscado lo separa: `evaluar_utilidad` lo cuenta ahí
        hallado = _buscar(medida, mutante, semillas, literales, presupuesto)
        if hallado is None:
            continue
        evidencia, ok = hallado
        buscados.append({
            "id": f"{dominio}-gen-2{len(buscados):02d}-{nombre_medida}-buscado",
            "etiqueta": "verde_correcto" if ok else "falso_verde",
            "medida": mid,
            "evidencia": _encoger(medida, mutante, evidencia, ok),
            "titulo": f"Evidencia buscada y encogida que separa a {mid} de su mutante {nombre}",
        })
        muertos.add(nombre)
    return [*reglas, *buscados]


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
        if d["detecciones_conductuales"] or d["rechazos_del_algebra"]
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
            if d["detecciones_conductuales"] or d["rechazos_del_algebra"]
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

        candidatos = buscar_candidatos(medida, casos_existentes)
        if not candidatos:
            # Ni las reglas ni la búsqueda dieron evidencia: el motivo lo dicen las reglas.
            try:
                fabricar_candidatos(medida)
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
