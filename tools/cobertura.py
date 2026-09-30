"""`oracle cobertura`: qué promesas del proyecto mide alguna medida y cuáles no.

Lee `requisitos/*.requisito` y el catálogo efectivo. No evalúa nada: dice qué está cubierto, qué
declara por qué no se mide y qué nombra una medida que no existe. Esto último es un error (sale con
1), porque un requisito que apunta a la nada se lee como cubierto y no lo está.

Con `--con <hechos.json>` además juzga esa evidencia —igual que `oracle juzgar`, con sombras y
cotas— y dice de cada requisito si **se cumple** hoy, no sólo si tiene medida: una medida roja o en
sombra deja el requisito sin cumplir, y una que no tuvo evidencia lo deja sin juicio. Es la pregunta
«¿el código cumple la spec?», contestada con su `sin_medir` al lado. Sale con 1 si algún requisito
tiene un rojo que la sombra no perdona.
"""

from __future__ import annotations

from nucleo.algebra import ErrorDeAlgebra
from nucleo.medida import MedidaMalDeclarada
from nucleo.proyecto import (ORIGEN_PROYECTO, ProyectoInvalido, EscalaresInvalidas, EscalaresNoConfiables,
                             catalogo_efectivo, escalares_del_proyecto, macros_del_proyecto)
from nucleo.requisito import RequisitoMalDeclarado, cargar_requisitos


MARCAS_JUICIO = {"cumple": "✓", "no_cumple": "✗", "sin_juicio": "?"}


def estado_de_medida(mid: str, informe) -> str:
    """cumple · falla · falla en sombra · sin evidencia · no juzgó · no aplicada."""
    if mid in dict(informe.no_juzgaron):
        return "no juzgó"
    veredicto = next((v for v in informe.veredictos if v.id == mid), None)
    if veredicto is None:
        return "no aplicada"
    if veredicto.sin_evidencia:
        return "sin evidencia"
    if veredicto.ok:
        return "cumple"
    return "falla en sombra" if informe.perdona(veredicto) else "falla"


def juicio(estados: list[str]) -> str:
    if any(e.startswith("falla") for e in estados):
        return "no_cumple"
    return "cumple" if all(e == "cumple" for e in estados) else "sin_juicio"


def main(proy, *, confiar: bool = False, con: str | None = None) -> int:
    try:
        requisitos = cargar_requisitos(proy.raiz / "requisitos")
    except RequisitoMalDeclarado as e:
        print(f"✗ {e}")
        return 1
    if not requisitos:
        print("sin requisitos: el proyecto no tiene requisitos/*.requisito")
        return 0
    # Las medidas de un proyecto pueden usar sus escalares: sin registrarlas, el catálogo no carga.
    evidencia = None
    if con is not None:
        from tools.juzgar import _leer_evidencia
        evidencia, error = _leer_evidencia(con)
        if error:
            print(f"✗ {error}")
            return 1
    try:
        with escalares_del_proyecto(proy, confiar=confiar):
            catalogo = catalogo_efectivo(proy, macros=macros_del_proyecto(proy))
            if evidencia is not None:
                from tools.juzgar import juzgar_evidencia
                informe = juzgar_evidencia(proy, evidencia)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        return 1
    except (ProyectoInvalido, MedidaMalDeclarada, ErrorDeAlgebra, KeyError) as e:
        print(f"✗ no se pudo juzgar la evidencia: {e}")
        return 1
    if evidencia is not None:
        return _con_juicio(requisitos, catalogo, informe)
    cuenta = {"total": 0, "parcial": 0, "ninguna": 0}
    inexistentes = 0
    usadas: set[str] = set()
    for r in requisitos.values():
        usadas.update(r.medido_por)
        faltan = [m for m in r.medido_por if m not in catalogo]
        if faltan:
            inexistentes += 1
            print(f"✗ {r.id}   nombra medidas que no existen: {', '.join(faltan)}")
            continue
        cuenta[r.cobertura] += 1
        marca = {"total": "✓", "parcial": "◐", "ninguna": "·"}[r.cobertura]
        partes = [", ".join(r.medido_por)] if r.medido_por else []
        if r.sin_medir:
            partes.append(f"SIN MEDIR: {r.sin_medir}")
        print(f"{marca} {r.id}   {' · '.join(partes)}")
    print(f"\n{len(requisitos)} requisitos: {cuenta['total']} medidos · {cuenta['parcial']} en parte"
          f" · {cuenta['ninguna']} sin medir · {inexistentes} con medidas inexistentes")
    propias = sorted(mid for mid, e in catalogo.entradas.items() if e.origen == ORIGEN_PROYECTO)
    huerfanas = [mid for mid in propias if mid not in usadas]
    if huerfanas:
        print(f"{len(huerfanas)} de {len(propias)} medidas propias no cubren ningún requisito:")
        for mid in huerfanas:
            print(f"  · {mid}")
    return 1 if inexistentes else 0


def _con_juicio(requisitos, catalogo, informe) -> int:
    cuenta = {"cumple": 0, "no_cumple": 0, "sin_juicio": 0, "sin_medir": 0}
    inexistentes = parciales = rojos = 0
    ids_rojos = {v.id for v in informe.rojos}
    for r in requisitos.values():
        faltan = [m for m in r.medido_por if m not in catalogo]
        if faltan:
            inexistentes += 1
            print(f"✗ {r.id}   nombra medidas que no existen: {', '.join(faltan)}")
            continue
        sin_medir = f" · SIN MEDIR: {r.sin_medir}" if r.sin_medir else ""
        if not r.medido_por:
            cuenta["sin_medir"] += 1
            print(f"· {r.id}   sin medir{sin_medir}")
            continue
        estados = [estado_de_medida(m, informe) for m in r.medido_por]
        j = juicio(estados)
        cuenta[j] += 1
        rojos += any(m in ids_rojos for m in r.medido_por)
        marca = MARCAS_JUICIO[j]
        if j == "cumple" and r.sin_medir:
            marca, parciales = "◐", parciales + 1
        detalle = ", ".join(f"{m} {e}" for m, e in zip(r.medido_por, estados))
        print(f"{marca} {r.id}   {j.replace('_', ' ')} · {detalle}{sin_medir}")
    print(f"\n{len(requisitos)} requisitos: {cuenta['cumple']} se cumplen ({parciales} sólo en lo medido)"
          f" · {cuenta['no_cumple']} no se cumplen · {cuenta['sin_juicio']} sin juicio"
          f" · {cuenta['sin_medir']} sin medir · {inexistentes} con medidas inexistentes")
    for mid, motivo in informe.no_juzgaron:
        print(f"✗ {mid} no juzgó: {motivo}")
    return 1 if inexistentes or rojos or informe.no_juzgaron else 0
