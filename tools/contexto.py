"""`oracle contexto` — todo lo que hace falta para escribir una medida, en un solo lugar.

Quien va a escribir una medida —una persona o un agente— necesita saber cuatro cosas: qué relaciones
existen y con qué campos, qué funciones puede usar, qué tiene que declarar sí o sí, y qué medidas ya
están para no repetirlas. Hoy eso se averigua corriendo tres comandos y leyendo dos documentos, y el
que no sabe que existen no los corre.

No es un documento nuevo: es una VISTA, igual que el manual. Las relaciones salen del inventario que
usa `oracle relaciones`, las escalares del registro real, los vocabularios de `nucleo/vocabulario.py`
y las medidas del catálogo cargado. Si algo cambia, cambia acá solo.

`--compacto` existe porque el destinatario más probable es un agente con una ventana de contexto: la
misma información sin los renglones en blanco, sin las prosas largas y sin lo que se puede deducir.
No es un formato distinto — es la misma vista, apretada.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path = [str(RAIZ), *sys.path]

from nucleo.algebra import AGREGADOS, COMPARADORES, ESCALARES  # noqa: E402
from nucleo.medida import cargar_catalogo  # noqa: E402
from tools.medida import inventario_de_relaciones  # noqa: E402
from nucleo.vocabulario import (OPERADORES, ORIGENES_DE_UMBRAL,  # noqa: E402
                                opciones)
from nucleo.proyecto import (catalogos_a_cargar,  # noqa: E402
                             configuracion, macros_del_proyecto)
from tools.sesion import resolver_cli  # noqa: E402


def _medidas(proy) -> list:
    try:
        catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    except Exception:
        return []
    return sorted(catalogo.items())


def _relaciones(proy) -> tuple[dict, dict]:
    try:
        return inventario_de_relaciones(proy)
    except Exception:
        return {}, {}


def texto(proy, *, compacto: bool = False) -> str:
    campos, dondes = _relaciones(proy)
    catalogo = _medidas(proy)
    cfg = configuracion(proy)
    partes: list[str] = []
    sep = "" if compacto else "\n"

    partes.append(f"# CONTEXTO PARA ESCRIBIR UNA MEDIDA · {proy.raiz.name}")
    partes.append("")
    if cfg.sombra:
        partes.append(f"sombra: {len(cfg.sombra)} medida(s) se miden y NO tumban la corrida")
    partes.append(f"perfiles: {', '.join(cfg.perfiles) or 'ninguno'}"
                  f" · catálogo base: {'sí' if cfg.catalogo_base else 'no'}")
    partes.append("")

    partes.append("## LO QUE TODA MEDIDA DECLARA, SIN EXCEPCIÓN")
    partes.append("")
    partes.append("  umbral <comparador> <número> segun <origen> porque \"<por qué ESE número>\"")
    partes.append("  alcance \"<qué NO ve esta medida>\"")
    partes.append("")
    partes.append("El `alcance` no es prosa de relleno: una medida sin punto ciego declarado se lee")
    partes.append("como si viera todo, y ninguna ve todo. Los orígenes del umbral son cerrados:")
    partes.append(opciones(ORIGENES_DE_UMBRAL) if not compacto
                  else "  " + " · ".join(sorted(ORIGENES_DE_UMBRAL)))
    partes.append("")

    partes.append("## RELACIONES QUE HAY HOY, CON SUS CAMPOS")
    partes.append("")
    if not campos:
        partes.append("  (ninguna: sin evidencia no hay nada que medir todavía)")
    for rel in sorted(campos):
        cs = sorted(campos[rel].items())
        if compacto:
            partes.append(f"  {rel}: " + ", ".join(f"{c}:{'/'.join(sorted(t))}" for c, t in cs))
        else:
            partes.append(f"  {rel}")
            for campo, tipos in cs:
                partes.append(f"      {campo:<28} {'/'.join(sorted(tipos))}")
            partes.append(f"      · aparece en: {', '.join(sorted(dondes[rel])[:3])}")
            partes.append("")
    partes.append("Un hecho nuevo se agrega desde su SENSOR, no acá.")
    partes.append("")

    partes.append("## CON QUÉ SE ESCRIBE")
    partes.append("")
    partes.append(f"  operadores:  {' · '.join(sorted(OPERADORES))}")
    partes.append(f"  comparadores: {' '.join(COMPARADORES)}")
    partes.append(f"  lógicos:      y  o  no")
    partes.append(f"  agregados:    {' '.join(sorted(AGREGADOS))}")
    partes.append('  accesores:    ["campo", alias, nombre] · ["hecho", alias] · ["col", nombre]')
    partes.append("")
    if ESCALARES:
        partes.append("  escalares:")
        for nombre in sorted(ESCALARES):
            fn = ESCALARES[nombre]
            maximo = getattr(fn, "aridad_max", "?")
            aridad = (f"{fn.aridad_min}+" if maximo is None else
                      str(fn.aridad_min) if fn.aridad_min == maximo
                      else f"{fn.aridad_min}..{maximo}")
            if compacto:
                partes.append(f"    {nombre}/{aridad}")
            else:
                doc = (fn.__doc__ or "").strip().split("\n")[0]
                partes.append(f"    {nombre}/{aridad}")
                if doc:
                    partes.append(f"        {doc}")
    partes.append("")

    partes.append(f"## LAS {len(catalogo)} MEDIDAS QUE YA EXISTEN")
    partes.append("")
    if not catalogo:
        partes.append("  (ninguna todavía)")
    for mid, m in catalogo:
        if compacto:
            partes.append(f"  {mid}")
        else:
            alcance = (getattr(m, "alcance", "") or "").strip().split(".")[0]
            partes.append(f"  {mid}")
            if alcance:
                partes.append(f"      NO ve: {alcance}")
    partes.append("")
    partes.append("## EL ORDEN QUE IMPORTA")
    partes.append("")
    partes.append("Escribí el CASO del corpus antes que la medida. Si la medida se escribe primero,")
    partes.append("el caso termina diciendo lo que la medida ya hace, y entonces no la prueba: la")
    partes.append("describe. Una medida que selecciona lo que está BIEN en vez de lo que ofende pasa")
    partes.append("todas las validaciones automáticas y mide exactamente al revés.")
    return "\n".join(partes if not compacto else [l for l in partes if l.strip()]) + sep


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    p = argparse.ArgumentParser(
        description="Todo lo que hace falta para escribir una medida en este proyecto.")
    p.add_argument("--compacto", action="store_true",
                   help="la misma vista, sin lo que se puede deducir (para un agente)")
    args, _ = p.parse_known_args([a for a in argv if a != "--confiar-escalares"])
    proy = resolver_cli(argv)
    if proy is None:
        return 2
    print(texto(proy, compacto=args.compacto))
    return 0


_entrada_directa = {"__main__": main}.get(__name__)
if _entrada_directa:
    sys.exit(_entrada_directa())
