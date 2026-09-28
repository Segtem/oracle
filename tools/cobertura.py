"""`oracle cobertura`: qué promesas del proyecto mide alguna medida y cuáles no.

Lee `requisitos/*.requisito` y el catálogo efectivo. No evalúa nada: dice qué está cubierto, qué
declara por qué no se mide y qué nombra una medida que no existe. Esto último es un error (sale con
1), porque un requisito que apunta a la nada se lee como cubierto y no lo está.
"""

from __future__ import annotations

from nucleo.proyecto import ORIGEN_PROYECTO, catalogo_efectivo, macros_del_proyecto
from nucleo.requisito import RequisitoMalDeclarado, cargar_requisitos


def main(proy) -> int:
    try:
        requisitos = cargar_requisitos(proy.raiz / "requisitos")
    except RequisitoMalDeclarado as e:
        print(f"✗ {e}")
        return 1
    if not requisitos:
        print("sin requisitos: el proyecto no tiene requisitos/*.requisito")
        return 0
    catalogo = catalogo_efectivo(proy, macros=macros_del_proyecto(proy))
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
