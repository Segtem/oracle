"""Lector único y fail-closed de fixtures diferenciales versionados.

Los consumidores no deben conocer la forma física del fixture. Este módulo valida las dos formas
de ``oracle.diferencial/v1`` y las proyecta como evidencias o casos asociados a una medida. Así
``medida --relaciones``, la revisión, el diferencial y la mutación leen exactamente el mismo dato.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator

from nucleo.diferencial import (ALGORITMO_HUELLA, ESQUEMA_DIFERENCIAL, HUELLA_RE,
                                revisar_frescura)
from nucleo.proyecto import ID_MEDIDA_RE


ESCALARES_L0 = (str, int, float, bool, type(None))


@dataclass(frozen=True)
class Fixture:
    ruta: Path
    datos: dict


def id_medida_valido(valor: Any) -> bool:
    """Gramática portable de ids; excluye rutas, espacios y nombres ambiguos."""
    return isinstance(valor, str) and ID_MEDIDA_RE.fullmatch(valor) is not None


def _id_escenario_valido(valor: Any) -> bool:
    return isinstance(valor, str) and bool(valor) and not any(c.isspace() for c in valor)


def _validar_evidencia(evidencia: Any, contexto: str) -> list[str]:
    if not isinstance(evidencia, dict) or not evidencia:
        return [f"{contexto}: `evidencia` debe ser un mapa no vacío de relación → filas"]

    fallas = []
    for relacion, filas in evidencia.items():
        if not isinstance(relacion, str) or not relacion.strip():
            fallas.append(f"{contexto}: nombre de relación inválido: {relacion!r}")
            continue
        if not isinstance(filas, list):
            fallas.append(f"{contexto}: la relación «{relacion}» debe ser una lista de filas")
            continue
        for i, fila in enumerate(filas):
            if not isinstance(fila, dict):
                fallas.append(f"{contexto}: {relacion}[{i}] no es una fila")
                continue
            for campo, valor in fila.items():
                if not isinstance(campo, str) or not campo:
                    fallas.append(f"{contexto}: {relacion}[{i}] tiene un campo inválido")
                if not isinstance(valor, ESCALARES_L0):
                    fallas.append(
                        f"{contexto}: {relacion}[{i}].{campo} no es escalar "
                        f"({type(valor).__name__})")
    return fallas


def _validar_comunes(datos: Any, nombre: str) -> list[str]:
    if not isinstance(datos, dict):
        return [f"{nombre}: la raíz del fixture debe ser un objeto JSON"]

    fallas = []
    if datos.get("esquema") != ESQUEMA_DIFERENCIAL:
        fallas.append(
            f"{nombre}: esquema ausente o desconocido; se requiere {ESQUEMA_DIFERENCIAL!r}")
    if not isinstance(datos.get("origen"), str) or not datos.get("origen", "").strip():
        fallas.append(f"{nombre}: falta `origen` no vacío")
    if type(datos.get("mundos")) is not int or datos.get("mundos") <= 0:
        fallas.append(f"{nombre}: `mundos` debe ser un entero positivo")
    frescura = datos.get("frescura")
    if not isinstance(frescura, dict):
        fallas.append(f"{nombre}: falta `frescura` versionada")
        return fallas
    if frescura.get("algoritmo") != ALGORITMO_HUELLA:
        fallas.append(f"{nombre}: `frescura.algoritmo` debe ser {ALGORITMO_HUELLA!r}")
    if frescura.get("raiz_fuentes") not in (".", ".."):
        fallas.append(f"{nombre}: `frescura.raiz_fuentes` sólo admite '.' o '..'")
    fuentes = frescura.get("fuentes")
    if not isinstance(fuentes, dict):
        fallas.append(f"{nombre}: `frescura.fuentes` debe ser un mapa")
    else:
        for clase in ("emisor", "referencia"):
            rutas = fuentes.get(clase)
            if not isinstance(rutas, list) or not rutas or any(
                    not isinstance(r, str) or not r.strip() or Path(r).is_absolute()
                    or ".." in Path(r).parts for r in (rutas or [])):
                fallas.append(
                    f"{nombre}: `frescura.fuentes.{clase}` requiere rutas relativas válidas")
    if not isinstance(frescura.get("configuracion"), dict):
        fallas.append(f"{nombre}: `frescura.configuracion` debe ser un mapa")
    huellas = frescura.get("huellas")
    requeridas = {"emisor", "referencia", "catalogo", "configuracion"}
    if not isinstance(huellas, dict) or set(huellas) != requeridas:
        fallas.append(f"{nombre}: `frescura.huellas` debe contener {sorted(requeridas)}")
    elif any(not isinstance(h, str) or not HUELLA_RE.fullmatch(h) for h in huellas.values()):
        fallas.append(f"{nombre}: cada huella debe ser SHA-256 hexadecimal")
    return fallas


def _validar_dominio(datos: dict, nombre: str) -> list[str]:
    fallas = []
    medidas, escenarios = datos.get("medidas"), datos.get("escenarios")
    if not isinstance(medidas, list) or not medidas:
        fallas.append(f"{nombre}: el formato Dominio requiere `medidas` no vacías")
    elif any(not id_medida_valido(m) for m in medidas) or len(set(medidas)) != len(medidas):
        fallas.append(f"{nombre}: `medidas` debe contener ids válidos y únicos")

    if not isinstance(escenarios, list) or not escenarios:
        fallas.append(f"{nombre}: el formato Dominio requiere `escenarios` no vacíos")
        return fallas
    if type(datos.get("mundos")) is int and datos["mundos"] != len(escenarios):
        fallas.append(
            f"{nombre}: `mundos` dice {datos['mundos']} pero hay {len(escenarios)} escenarios")

    ids, polaridades = set(), set()
    individuales = {mid: set() for mid in medidas} if isinstance(medidas, list) else {}
    for i, escenario in enumerate(escenarios):
        contexto = f"{nombre}: escenario[{i}]"
        if not isinstance(escenario, dict):
            fallas.append(f"{contexto} debe ser un objeto")
            continue
        eid = escenario.get("id")
        if not _id_escenario_valido(eid):
            fallas.append(f"{contexto}: `id` debe ser un texto no vacío y sin espacios")
        elif eid in ids:
            fallas.append(f"{contexto}: id duplicado «{eid}»")
        else:
            ids.add(eid)
        if type(escenario.get("referencia_ok")) is not bool:
            fallas.append(f"{contexto}: `referencia_ok` debe ser booleano")
        else:
            polaridades.add(escenario["referencia_ok"])
        guardado = escenario.get("oracle_al_generar")
        if not isinstance(guardado, dict):
            fallas.append(f"{contexto}: falta `oracle_al_generar`")
        else:
            global_ok, por_medida = guardado.get("global_ok"), guardado.get("por_medida")
            if type(global_ok) is not bool:
                fallas.append(f"{contexto}: `oracle_al_generar.global_ok` debe ser booleano")
            if not isinstance(por_medida, dict) or set(por_medida) != set(medidas or []):
                fallas.append(
                    f"{contexto}: `oracle_al_generar.por_medida` debe cubrir exactamente `medidas`")
            elif any(type(ok) is not bool for ok in por_medida.values()):
                fallas.append(f"{contexto}: los veredictos individuales deben ser booleanos")
            else:
                for mid, ok in por_medida.items():
                    if mid in individuales:
                        individuales[mid].add(ok)
                if type(global_ok) is bool and global_ok != all(por_medida.values()):
                    fallas.append(f"{contexto}: `global_ok` no es el AND de `por_medida`")
                if (type(global_ok) is bool and type(escenario.get("referencia_ok")) is bool
                        and global_ok != escenario["referencia_ok"]):
                    fallas.append(f"{contexto}: Oracle y la referencia ya discrepaban al generar")
        fallas += _validar_evidencia(escenario.get("evidencia"), contexto)
    if polaridades != {False, True}:
        fallas.append(f"{nombre}: los escenarios deben contener ambas polaridades globales")
    flojas = [mid for mid, vistos in individuales.items() if vistos != {False, True}]
    if flojas:
        fallas.append(f"{nombre}: faltan ambas polaridades individuales para {flojas}")
    return fallas


def _validar_grupos(datos: dict, nombre: str) -> list[str]:
    grupos = datos.get("grupos")
    if not isinstance(grupos, dict) or not grupos:
        return [f"{nombre}: el formato `grupos` requiere grupos no vacíos"]
    fallas, mundos = [], datos.get("mundos")
    for mid, casos in grupos.items():
        contexto = f"{nombre}: grupo {mid!r}"
        if not id_medida_valido(mid):
            fallas.append(f"{nombre}: id de medida de grupo inválido: {mid!r}")
        if not isinstance(casos, list) or not casos:
            fallas.append(f"{contexto} requiere casos no vacíos")
            continue
        if type(mundos) is int and mundos != len(casos):
            fallas.append(f"{contexto}: `mundos` dice {mundos} pero el grupo tiene {len(casos)} casos")
        polaridades = set()
        for i, caso in enumerate(casos):
            caso_ctx = f"{contexto}[{i}]"
            if not isinstance(caso, dict):
                fallas.append(f"{caso_ctx} debe ser un objeto")
                continue
            if type(caso.get("esperado_ok")) is not bool:
                fallas.append(f"{caso_ctx}: `esperado_ok` debe ser booleano")
            else:
                polaridades.add(caso["esperado_ok"])
            fallas += _validar_evidencia(caso.get("evidencia"), caso_ctx)
        if polaridades != {False, True}:
            fallas.append(f"{contexto} debe contener ambas polaridades (verde y rojo)")
    return fallas


def validar_fixture(datos: Any, nombre: str = "fixture") -> list[str]:
    """Contrato fail-closed para las dos formas de ``oracle.diferencial/v1``."""
    fallas = _validar_comunes(datos, nombre)
    if not isinstance(datos, dict):
        return fallas
    if datos.get("esquema") != ESQUEMA_DIFERENCIAL or not isinstance(datos.get("frescura"), dict):
        return fallas
    tiene_escenarios, tiene_grupos = "escenarios" in datos, "grupos" in datos
    if tiene_escenarios and tiene_grupos:
        fallas.append(f"{nombre}: mezcla los formatos `escenarios` y `grupos`")
    elif tiene_escenarios:
        fallas += _validar_dominio(datos, nombre)
    elif tiene_grupos:
        fallas += _validar_grupos(datos, nombre)
    else:
        fallas.append(f"{nombre}: formato desconocido; falta `escenarios` o `grupos`")
    return fallas


def cargar_fixtures(rutas: Iterable[Path], *, raiz: Path | None = None,
                    catalogo: dict | None = None) -> tuple[list[Fixture], list[str]]:
    """Carga y valida; con raíz y catálogo también exige procedencia todavía fresca."""
    if (raiz is None) != (catalogo is None):
        raise ValueError("`raiz` y `catalogo` se pasan juntos para comprobar frescura")
    cargados, fallas = [], []
    for ruta in rutas:
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as e:
            fallas.append(f"{ruta.name}: JSON ilegible — {e}")
            continue
        problemas = validar_fixture(datos, ruta.name)
        if not problemas and raiz is not None:
            problemas = [f"{ruta.name}: {p}" for p in revisar_frescura(datos, raiz, catalogo)]
        if problemas:
            fallas += problemas
        else:
            cargados.append(Fixture(ruta, datos))
    return cargados, fallas


def evidencias(fixture: Fixture) -> Iterator[tuple[str, dict]]:
    """Evidencias únicas con un origen legible, sin obligar al consumidor a conocer el formato."""
    datos = fixture.datos
    if "escenarios" in datos:
        for escenario in datos["escenarios"]:
            yield f"{fixture.ruta.stem}/{escenario['id']}", escenario["evidencia"]
    else:
        for mid, casos in datos["grupos"].items():
            for i, caso in enumerate(casos):
                yield f"{fixture.ruta.stem}/{mid}[{i}]", caso["evidencia"]


def casos_para_mutacion(fixture: Fixture, catalogo: dict) -> Iterator[dict]:
    """Proyecta cualquiera de las dos formas al contrato corpus-like del mutador."""
    datos = fixture.datos
    if "escenarios" in datos:
        for mid in datos["medidas"]:
            if mid not in catalogo:
                continue
            for escenario in datos["escenarios"]:
                ok = catalogo[mid].evaluar(escenario["evidencia"]).ok
                yield {"id": f"{fixture.ruta.stem}/{mid}[{escenario['id']}]",
                       "etiqueta": "verde_correcto" if ok else "falso_verde",
                       "medida": mid, "evidencia": escenario["evidencia"]}
    else:
        for mid, entradas in datos["grupos"].items():
            for i, entrada in enumerate(entradas):
                yield {"id": f"{fixture.ruta.stem}/{mid}[{i}]",
                       "etiqueta": "verde_correcto" if entrada["esperado_ok"] else "falso_verde",
                       "medida": mid, "evidencia": entrada["evidencia"]}
