"""La prueba diferencial: el álgebra contra una implementación independiente.

    python tools/diferencial.py [--proyecto <ruta>] [--confiar-escalares]

Re-juzga la evidencia versionada con las medidas actuales, comprueba primero su procedencia y compara
por separado el acuerdo global con la referencia y la estabilidad de cada veredicto de Oracle.
Sale != 0 ante un fixture inválido, vencido o cualquier desacuerdo.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos  # noqa: F401,E402
from nucleo.fixtures import (cargar_fixtures, revisar_frescura,
                             validar_fixture)  # noqa: F401,E402
from nucleo.medida import cargar_catalogo, evaluar  # noqa: E402
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables, catalogos_a_cargar,
                             confiar_escalares, escalares_del_proyecto,
                             macros_del_proyecto,
                             problemas_estructura)  # noqa: E402
from tools.sesion import resolver_cli  # noqa: E402

def comparar_dominio(datos: dict, catalogo: dict, nombre: str = "fixture") -> dict:
    """Compara por separado la referencia global y la fotografía individual de Oracle."""
    faltan = [mid for mid in datos["medidas"] if mid not in catalogo]
    resultado = {
        "globales": len(datos["escenarios"]),
        "individuales": len(datos["escenarios"]) * len(datos["medidas"]),
        "desacuerdos_globales": [],
        "cambios_individuales": [],
        "fallas": [],
    }
    if faltan:
        resultado["fallas"].append(
            f"{nombre}: el fixture reclama medidas que no están: {faltan}")
        return resultado

    medidas = [catalogo[mid] for mid in datos["medidas"]]
    for escenario in datos["escenarios"]:
        try:
            informe = evaluar(medidas, escenario["evidencia"])
        except Exception as e:  # noqa: BLE001
            resultado["fallas"].append(
                f"{nombre}[{escenario['id']}]: error al evaluar: {type(e).__name__}: {e}")
            continue
        if informe.ok != escenario["referencia_ok"]:
            resultado["desacuerdos_globales"].append(escenario["id"])
        anteriores = escenario["oracle_al_generar"]["por_medida"]
        for veredicto in informe.veredictos:
            if veredicto.ok != anteriores[veredicto.id]:
                resultado["cambios_individuales"].append(
                    (escenario["id"], veredicto.id, anteriores[veredicto.id], veredicto.ok))
    return resultado


def _ejecutar(proy) -> int:
    estructura = problemas_estructura(proy, ("catalogos", "diferencial"))
    if estructura:
        print("PROYECTO INVÁLIDO — " + "; ".join(estructura))
        return 1
    rutas = sorted(proy.diferencial.glob("*.json"))
    if not rutas:
        print("no hay fixtures en diferencial/ — los genera el emisor del proyecto")
        return 1

    fixtures, fallas = cargar_fixtures(rutas)
    if fallas:
        print(f"DIFERENCIAL ✗ — {len(fallas)} problema(s) de fixture")
        for falla in fallas[:20]:
            print("  ·", falla)
        return 1

    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    total_global = total_individual = 0
    for fixture in fixtures:
        f, datos = fixture.ruta, fixture.datos
        print(f"{f.name} · {datos['mundos']} mundos · origen: {datos['origen']}\n")
        problemas_frescura = revisar_frescura(datos, proy.raiz, catalogo)
        if problemas_frescura:
            fallas += [f"{f.name}: {p}" for p in problemas_frescura]
            print(f"  ✗ fixture vencido · {len(problemas_frescura)} cambio(s) de procedencia\n")
            continue

        if "escenarios" in datos:
            fallas_antes = len(fallas)
            comparacion = comparar_dominio(datos, catalogo, f.name)
            total_global += comparacion["globales"]
            total_individual += comparacion["individuales"]
            fallas += comparacion["fallas"]
            malos = comparacion["desacuerdos_globales"]
            cambios = comparacion["cambios_individuales"]
            marca_global = "✓" if not malos and len(fallas) == fallas_antes else "✗"
            marca_individual = "✓" if not cambios and len(fallas) == fallas_antes else "✗"
            verdes = sum(1 for e in datos["escenarios"] if e["referencia_ok"])
            print(f"  {marca_global} acuerdo global: {len(datos['escenarios'])} escenarios "
                  f"({verdes} verdes / {len(datos['escenarios']) - verdes} rojos) · "
                  f"{len(malos)} desacuerdos")
            print(f"  {marca_individual} estabilidad individual: {len(datos['medidas'])} medidas × "
                  f"{len(datos['escenarios'])} escenarios · {len(cambios)} cambios")
            for eid in malos[:5]:
                fallas.append(f"{f.name}[{eid}]: las medidas y la referencia no coinciden")
            for eid, mid, antes, ahora in cambios[:5]:
                fallas.append(f"{f.name}[{eid}].{mid}: veredicto individual cambió {antes} → {ahora}")
            print()
            continue

        for mid, casos in sorted(datos["grupos"].items()):
            if mid not in catalogo:
                fallas.append(f"{mid}: el fixture la reclama y no está en el catálogo")
                continue
            fallas_antes, desacuerdos = len(fallas), []
            for i, caso in enumerate(casos):
                total_individual += 1
                try:
                    veredicto = catalogo[mid].evaluar(caso["evidencia"])
                except Exception as e:  # noqa: BLE001
                    fallas.append(f"{f.name}[{mid}][{i}]: error al evaluar: {type(e).__name__}: {e}")
                    continue
                if veredicto.ok != caso["esperado_ok"]:
                    desacuerdos.append((i, veredicto.valor, caso["esperado_ok"]))
            verdes = sum(1 for c in casos if c["esperado_ok"])
            marca = "✓" if not desacuerdos and len(fallas) == fallas_antes else "✗"
            print(f"  {marca} {mid:<32} {len(casos):>4} casos "
                  f"({verdes} verdes / {len(casos) - verdes} rojos) · "
                  f"{len(desacuerdos)} desacuerdos")
            for i, valor, esperado in desacuerdos[:5]:
                fallas.append(f"{mid}[{i}]: el álgebra dio {valor} y la referencia esperaba ok={esperado}")

    if fallas:
        print(f"\nDIFERENCIAL ✗ — {len(fallas)} desacuerdo(s)")
        for falla in fallas[:20]:
            print("  ·", falla)
        return 1
    partes = []
    if total_global:
        partes.append(f"{total_global} acuerdos globales con referencias independientes")
    if total_individual:
        partes.append(f"{total_individual} veredictos individuales estables")
    print("\nDIFERENCIAL ✓ — " + " · ".join(partes))
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    proy = resolver_cli(argv)
    if proy is None:
        return 1
    try:
        with escalares_del_proyecto(proy, confiar=confiar_escalares(argv)):
            return _ejecutar(proy)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
