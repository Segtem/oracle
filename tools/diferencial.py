"""La prueba diferencial: el álgebra contra una implementación independiente.

    python tools/diferencial.py

`diferencial/geometria.json` lo produce Jam corriendo sus oráculos de colocación y snap escritos a
mano — código que no comparte una línea con este álgebra. Acá se re-juzga la misma evidencia con las
medidas del catálogo y se comparan los veredictos, uno por uno.

Es la única forma de saber si las medidas de geometría dicen lo que creen decir: nadie de este lado
las escribió mirando la otra implementación, y el archivo es datos, no una dependencia.

Sale != 0 ante cualquier desacuerdo.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos  # noqa: F401,E402  registra las escalares de todos los dominios
from nucleo.medida import cargar_catalogo, evaluar  # noqa: E402
from nucleo.proyecto import (catalogos_a_cargar, registrar_escalares, resolver,
                             sin_bandera)  # noqa: E402

PROY = resolver(sys.argv[1:])
registrar_escalares(PROY)


ESCALARES_L0 = (str, int, float, bool, type(None))


def _id_valido(valor: Any) -> bool:
    return isinstance(valor, str) and bool(valor) and not any(c.isspace() for c in valor)


def _validar_evidencia(evidencia: Any, contexto: str) -> list[str]:
    """Valida la forma L0 sin juzgar el contenido del dominio.

    Una relación presente puede tener cero filas: ausencia de hechos no es un fixture inválido. Lo
    que no puede faltar es el mapa de evidencia ni pueden colarse objetos anidados en sus filas.
    """
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
                        f"{contexto}: {relacion}[{i}].{campo} no es escalar ({type(valor).__name__})")
    return fallas


def _validar_comunes(datos: Any, nombre: str) -> list[str]:
    if not isinstance(datos, dict):
        return [f"{nombre}: la raíz del fixture debe ser un objeto JSON"]

    fallas = []
    if not isinstance(datos.get("origen"), str) or not datos.get("origen", "").strip():
        fallas.append(f"{nombre}: falta `origen` no vacío")
    if type(datos.get("mundos")) is not int or datos.get("mundos", 0) <= 0:
        fallas.append(f"{nombre}: `mundos` debe ser un entero positivo")
    return fallas


def _validar_dominio(datos: dict, nombre: str) -> list[str]:
    fallas = []
    medidas = datos.get("medidas")
    escenarios = datos.get("escenarios")

    if not isinstance(medidas, list) or not medidas:
        fallas.append(f"{nombre}: el formato Dominio requiere `medidas` no vacías")
    elif (any(not _id_valido(m) for m in medidas)
          or len(set(medidas)) != len(medidas)):
        fallas.append(f"{nombre}: `medidas` debe contener ids sin espacios y únicos")

    if not isinstance(escenarios, list) or not escenarios:
        fallas.append(f"{nombre}: el formato Dominio requiere `escenarios` no vacíos")
        return fallas

    if type(datos.get("mundos")) is int and datos["mundos"] != len(escenarios):
        fallas.append(
            f"{nombre}: `mundos` dice {datos['mundos']} pero hay {len(escenarios)} escenarios")

    ids = set()
    polaridades = set()
    for i, escenario in enumerate(escenarios):
        contexto = f"{nombre}: escenario[{i}]"
        if not isinstance(escenario, dict):
            fallas.append(f"{contexto} debe ser un objeto")
            continue
        eid = escenario.get("id")
        if not _id_valido(eid):
            fallas.append(f"{contexto}: `id` debe ser un texto no vacío y sin espacios")
        elif eid in ids:
            fallas.append(f"{contexto}: id duplicado «{eid}»")
        else:
            ids.add(eid)
        if type(escenario.get("referencia_ok")) is not bool:
            fallas.append(f"{contexto}: `referencia_ok` debe ser booleano")
        else:
            polaridades.add(escenario["referencia_ok"])
        fallas += _validar_evidencia(escenario.get("evidencia"), contexto)

    if polaridades != {False, True}:
        fallas.append(
            f"{nombre}: los escenarios deben contener ambas polaridades globales (verde y rojo)")
    return fallas


def _validar_grupos(datos: dict, nombre: str) -> list[str]:
    grupos = datos.get("grupos")
    if not isinstance(grupos, dict) or not grupos:
        return [f"{nombre}: el formato `grupos` requiere grupos no vacíos"]

    fallas = []
    mundos = datos.get("mundos")
    for mid, casos in grupos.items():
        contexto = f"{nombre}: grupo {mid!r}"
        if not _id_valido(mid):
            fallas.append(f"{nombre}: id de medida de grupo inválido: {mid!r}")
        if not isinstance(casos, list) or not casos:
            fallas.append(f"{contexto} requiere casos no vacíos")
            continue
        # En el formato histórico todos los grupos recorren los mismos mundos: `mundos` coincide con
        # el largo DE CADA GRUPO, no con la suma de casos de todos ellos.
        if type(mundos) is int and mundos != len(casos):
            fallas.append(
                f"{contexto}: `mundos` dice {mundos} pero el grupo tiene {len(casos)} casos")
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
    """Contrato fail-closed para los dos formatos históricos del diferencial."""
    fallas = _validar_comunes(datos, nombre)
    if not isinstance(datos, dict):
        return fallas
    tiene_escenarios = "escenarios" in datos
    tiene_grupos = "grupos" in datos
    if tiene_escenarios and tiene_grupos:
        fallas.append(f"{nombre}: mezcla los formatos `escenarios` y `grupos`")
    elif tiene_escenarios:
        fallas += _validar_dominio(datos, nombre)
    elif tiene_grupos:
        fallas += _validar_grupos(datos, nombre)
    else:
        fallas.append(f"{nombre}: formato desconocido; falta `escenarios` o `grupos`")
    return fallas


def _cargar_fixtures(rutas: list[Path]) -> tuple[list[tuple[Path, dict]], list[str]]:
    cargados = []
    fallas = []
    for ruta in rutas:
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as e:
            fallas.append(f"{ruta.name}: JSON ilegible — {e}")
            continue
        problemas = validar_fixture(datos, ruta.name)
        if problemas:
            fallas += problemas
        else:
            cargados.append((ruta, datos))
    return cargados, fallas


def main() -> int:
    fixtures = sorted((PROY.diferencial).glob("*.json"))
    if not fixtures:
        print("no hay fixtures en diferencial/ — los genera `tools/emitir_diferencial.py` en Jam")
        return 1

    cargados, fallas = _cargar_fixtures(fixtures)
    if fallas:
        print(f"DIFERENCIAL ✗ — {len(fallas)} problema(s) de fixture")
        for falla in fallas[:20]:
            print("  ·", falla)
        return 1

    catalogo = cargar_catalogo(catalogos_a_cargar(PROY))
    total = 0

    for f, datos in cargados:
        print(f"{f.name} · {datos['mundos']} mundos · origen: {datos['origen']}\n")

        # Formato de DOMINIO DECLARADO (`nucleo.dominio`): un veredicto global por escenario contra la
        # referencia. No hay expectativa por medida, porque eso reimplementaba las medidas en Python.
        if "escenarios" in datos:
            fallas_antes = len(fallas)
            medidas = [catalogo[m] for m in datos["medidas"] if m in catalogo]
            faltan = [m for m in datos["medidas"] if m not in catalogo]
            if faltan:
                fallas.append(f"{f.name}: el fixture reclama medidas que no están: {faltan}")
            malos = []
            for esc in datos["escenarios"]:
                total += 1
                try:
                    informe = evaluar(medidas, esc["evidencia"])
                except Exception as e:  # el fixture no puede convertir un error en un crash opaco
                    fallas.append(
                        f"{f.name}[{esc['id']}]: error al evaluar: {type(e).__name__}: {e}")
                    continue
                if informe.ok != esc["referencia_ok"]:
                    malos.append(esc["id"])
            marca = "✓" if not malos and len(fallas) == fallas_antes else "✗"
            verdes = sum(1 for e in datos["escenarios"] if e["referencia_ok"])
            print(f"  {marca} {len(medidas)} medidas × {len(datos['escenarios'])} escenarios "
                  f"({verdes} verdes / {len(datos['escenarios']) - verdes} rojos) · "
                  f"{len(malos)} desacuerdos")
            for mid in malos[:5]:
                fallas.append(f"{f.name}[{mid}]: las medidas y la referencia no coinciden")
            print()
            continue

        for mid, casos in sorted(datos["grupos"].items()):
            if mid not in catalogo:
                fallas.append(f"{mid}: el fixture la reclama y no está en el catálogo")
                continue
            fallas_antes = len(fallas)
            medida = catalogo[mid]
            desacuerdos = []
            for i, caso in enumerate(casos):
                total += 1
                try:
                    v = medida.evaluar(caso["evidencia"])
                except Exception as e:
                    fallas.append(
                        f"{f.name}[{mid}][{i}]: error al evaluar: {type(e).__name__}: {e}")
                    continue
                if v.ok != caso["esperado_ok"]:
                    desacuerdos.append((i, v.valor, caso["esperado_ok"]))
            verdes = sum(1 for c in casos if c["esperado_ok"])
            marca = "✓" if not desacuerdos and len(fallas) == fallas_antes else "✗"
            print(f"  {marca} {mid:<32} {len(casos):>4} casos "
                  f"({verdes} verdes / {len(casos) - verdes} rojos) · "
                  f"{len(desacuerdos)} desacuerdos")
            for i, valor, esperado in desacuerdos[:5]:
                fallas.append(f"{mid}[{i}]: el álgebra dio {valor} "
                              f"y la otra implementación esperaba ok={esperado}")

    if fallas:
        print(f"\nDIFERENCIAL ✗ — {len(fallas)} desacuerdo(s)")
        for x in fallas[:20]:
            print("  ·", x)
        return 1
    print(f"\nDIFERENCIAL ✓ — {total} veredictos coinciden con la implementación independiente")
    return 0


if __name__ == "__main__":
    sys.exit(main())
