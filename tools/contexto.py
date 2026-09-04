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
from tools.medida import inventario_de_relaciones  # noqa: E402
from nucleo.vocabulario import (OPERADORES, ORIGENES_DE_UMBRAL,  # noqa: E402
                                opciones)
from nucleo.proyecto import (EscalaresNoConfiables, catalogo_efectivo,  # noqa: E402
                             configuracion, escalares_del_proyecto, macros_del_proyecto)
from tools.sesion import resolver_cli  # noqa: E402


def _medidas(proy, *, confiar: bool = False) -> tuple[list, str]:
    """Las medidas del proyecto, y si no se pudieron cargar, POR QUÉ.

    Devolvía `[]` y se tragaba la excepción. Medido el 2026-09-04 sobre los dos consumidores
    conocidos: los dos tienen catálogo —41 y 9 medidas— y este contexto decía «LAS 0 MEDIDAS QUE YA
    EXISTEN». La causa es que un consumidor declara sus propias escalares y hay que registrarlas
    antes de cargar; sin eso el catálogo no resuelve un nombre y falla entero.

    Los dos defectos eran uno solo mal partido. El de fondo no es que no cargue: es que un texto
    escrito PARA UN AGENTE, que no tiene con qué dudar, afirmaba que el proyecto no tenía medidas.
    Un cero por falla es indistinguible de un cero real, y sobre esa base un agente escribe la
    primera medida de un catálogo que ya tiene cuarenta y una.

    Ahora falla abierto: dice qué pasó y qué hace falta. Un `--confiar-escalares` ausente no es un
    error del proyecto sino una autorización que nadie dio, y decirlo es la diferencia entre una
    respuesta inútil y una accionable.
    """
    # El `try` envuelve al `with` y no sólo a su cuerpo: `escalares_del_proyecto` levanta
    # `EscalaresNoConfiables` al ENTRAR, no adentro. Con el `try` por dentro, la excepción pasaba de
    # largo y el comando terminaba en una traza de Python — que es otra forma de no contestar.
    try:
        with escalares_del_proyecto(proy, confiar=confiar):
            # `catalogo_efectivo` y NO `catalogos_a_cargar`: el primero aplica el filtro de
            # ámbito de 0.5.0. Con el segundo, este texto le enumera a un consumidor medidas que
            # NO lo obligan —las que sólo obligan a Oracle— y lo invita a preocuparse por ellas.
            catalogo = catalogo_efectivo(proy, macros=macros_del_proyecto(proy))
    except EscalaresNoConfiables:
        return [], ("el catálogo usa escalares declaradas por el proyecto y nadie autorizó "
                    "ejecutarlas: repetí con `--confiar-escalares`")
    except Exception as e:
        return [], f"no se pudo cargar el catálogo — {type(e).__name__}: {e}"
    return sorted(catalogo.items()), ""


def _relaciones(proy) -> tuple[dict, dict]:
    try:
        return inventario_de_relaciones(proy)
    except Exception:
        return {}, {}


def texto(proy, *, compacto: bool = False, confiar_escalares: bool = False) -> str:
    campos, dondes = _relaciones(proy)
    catalogo, falla = _medidas(proy, confiar=confiar_escalares)
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

    # El encabezado NO puede decir un número cuando el número no se pudo averiguar: «LAS 0 MEDIDAS
    # QUE YA EXISTEN» es indistinguible de un catálogo vacío de verdad, y quien lee esto no tiene con
    # qué dudar. Cuando falla, el texto lo dice y no cuenta.
    if falla:
        partes.append("## LAS MEDIDAS QUE YA EXISTEN — NO SE PUDIERON LEER")
        partes.append("")
        partes.append(f"  ⚠ {falla}")
        partes.append("  No sigas como si el catálogo estuviera vacío: puede tener medidas que")
        partes.append("  todavía no ves, y escribir una repetida es el resultado esperable.")
    else:
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
