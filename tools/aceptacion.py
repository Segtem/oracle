"""La prueba de aceptación del marco: **el corpus juzga al oráculo, no al revés.**

    python tools/aceptacion.py [--proyecto <ruta>] [--confiar-escalares]

Criterio 4 de la especificación, ejecutable:

  · todo caso de defecto que **declara** una medida tiene que ponerse en **ROJO** con esa medida;
  · todo caso `verde_correcto` tiene que salir **VERDE**. Son la otra polaridad, y no son relleno:
    sin ellos `quitar_filtro` sobrevive siempre, porque contar sin filtro sólo da verde con la
    relación vacía. Un corpus de puros defectos deja las medidas flojas;
  · los casos sin medida distinguen `abierto`, `resuelto` y `limite_humano`; sólo los abiertos son
    deuda del marco y su número tiene que bajar;
  · y al final corre el nivel L2: las medidas del catálogo servidas **como relación**, medidas por
    una medida. Sin mecanismo nuevo — es lo que vuelve esto un metalenguaje.

Sale != 0 si algún caso que debía ponerse rojo salió verde.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402  registra las escalares declaradas
from nucleo.caso import cargar_casos  # noqa: E402
from nucleo.marco import hechos_de_casos, hechos_de_sombra  # noqa: E402
from nucleo.medida import (cargar_catalogo, como_hechos, evaluar,
                           medidas_aplicables)  # noqa: E402
from nucleo.relacion import cargar_relaciones, hechos_de_relaciones  # noqa: E402
from nucleo.unidad import hechos_de_unidades  # noqa: E402
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables,  # noqa: E402
                             catalogos_a_cargar, configuracion,
                             confiar_escalares, escalares_del_proyecto,
                             macros_del_proyecto,
                             problemas_estructura, relaciones_del_proyecto)  # noqa: E402
from tools.sesion import resolver_cli  # noqa: E402

def casos(proy) -> list[dict]:
    return cargar_casos(proy.corpus)


def _ejecutar(proy) -> int:
    estructura = problemas_estructura(proy, ("catalogos", "corpus"))
    if estructura:
        print("PROYECTO INVÁLIDO — " + "; ".join(estructura))
        return 1
    catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
    todos = casos(proy)
    fallas: list[str] = []
    rojos = 0
    verdes = 0
    huecos: list[str] = []
    archivados = {"resuelto": [], "limite_humano": []}

    print(f"catálogo: {len(catalogo)} medidas · corpus: {len(todos)} casos\n")

    if not todos:
        print("ACEPTACIÓN NO APLICABLE — SIN CASOS: un corpus vacío no puede juzgar al oráculo")
        return 1

    for c in todos:
        mid = c.get("medida")
        if not mid:
            estado = c.get("estado_sin_medida", "abierto")
            if estado == "abierto":
                huecos.append(f"{c['id']} — {c.get('sin_medida_todavia', '')[:70]}")
            elif estado in archivados:
                archivados[estado].append(c["id"])
            continue
        if mid not in catalogo:
            fallas.append(f"{c['id']}: reclama la medida «{mid}» y no está en el catálogo")
            continue

        esperado_ok = c["etiqueta"] == "verde_correcto"
        v = catalogo[mid].evaluar(c["evidencia"])
        if v.ok != esperado_ok:
            pass          # lo dictamina `meta.el_caso_se_pone_como_debe`, no un `if` de acá
        elif esperado_ok:
            verdes += 1
            print(f"  verde {c['id']:<38} {mid}  (valor {v.valor})")
        else:
            rojos += 1
            print(f"  ROJO  {c['id']:<38} {mid}  (valor {v.valor})")

    print(f"\ndefectos que se pusieron rojos: {rojos} · verdes correctos: {verdes} · "
          f"huecos declarados: {len(huecos)}")
    for h in huecos:
        print(f"  hueco  {h}")
    for estado, ids in archivados.items():
        for cid in ids:
            print(f"  {estado:<14} {cid}")

    # ---- L2: el marco medido con sus propias medidas ----
    # Antes esto era una lista de `if`s en este archivo. El veredicto sobre el marco es un dato como
    # cualquier otro: acá sólo se producen los hechos y se imprime lo que las medidas dicen.
    print("\nnivel meta — el marco medido con sus propias medidas:")
    relaciones = relaciones_del_proyecto(proy)
    evidencia_meta = {"medida": como_hechos(catalogo.values()),
                      **hechos_de_casos(catalogo, todos),
                      **hechos_de_relaciones(relaciones.values()),
                      **hechos_de_unidades(catalogo.values(), relaciones)}
    metas = [m for mid, m in sorted(catalogo.items()) if mid.startswith("meta.")]
    informe_meta = evaluar(medidas_aplicables(metas, evidencia_meta), evidencia_meta)

    # La SOMBRA apaga la consecuencia de un rojo, no la medición. Una medida en sombra se evalúa
    # igual, se imprime igual y se cuenta igual; lo único que no hace es tumbar la corrida.
    #
    # Existe porque heredar un catálogo de políticas te pone en rojo, y con razón: sus medidas ven
    # cosas que las tuyas no veían. Pero si la primera experiencia de heredarlo es que el proyecto
    # entero deja de pasar, no se hereda una segunda vez. La sombra compra tiempo sin comprar
    # silencio: cada una declara desde cuándo y por qué, y `catalogos/meta/` tiene tres medidas que
    # las vigilan —que declaren, que no sobrevivan a su propio verde, y que no apunten a un id que
    # ya no existe—.
    en_sombra = {e.medida for e in configuracion(proy).sombra}
    ensombrecidas = []
    for v in informe_meta.veredictos:
        # La marca va en la línea del VEREDICTO, no al final del bloque: `v.linea()` trae también
        # los testigos, y pegada al final quedaba a cinco renglones del id que ensombrece — donde
        # nadie la asocia con la medida, que es lo mismo que no marcarla.
        veredicto, salto, resto = v.linea().partition("\n")
        if v.id in en_sombra:
            veredicto += "   [EN SOMBRA]"
        print(" ", veredicto + salto + resto)
        if v.ok:
            continue
        if v.id in en_sombra:
            ensombrecidas.append(v)
        else:
            fallas.append(f"{v.id}: el marco no cumple su propia regla")

    # La segunda vuelta: las medidas que juzgan la sombra misma. Van aparte porque necesitan los
    # veredictos de la primera —una sombra «ya en verde» no se puede saber antes de medir—.
    sombra_declarada = configuracion(proy).sombra
    if sombra_declarada:
        evidencia_sombra = {**evidencia_meta,
                            **hechos_de_sombra(sombra_declarada,
                                               {v.id: v.ok for v in informe_meta.veredictos},
                                               catalogo)}
        vigilan = [m for mid, m in sorted(catalogo.items()) if "sombra" in mid]
        informe_sombra = evaluar(medidas_aplicables(vigilan, evidencia_sombra), evidencia_sombra)
        print(f"\nEN SOMBRA — {len(sombra_declarada)} medida(s) que se miden y no hacen fallar:")
        for entrada in sombra_declarada:
            hecho = next(h for h in evidencia_sombra["sombra"] if h["medida"] == entrada.medida)
            antiguedad = f"hace {hecho['dias']} días" if hecho["dias"] >= 0 else "sin fecha"
            print(f"  · {entrada.medida}  ({antiguedad})")
            print(f"      porque: {entrada.porque or '(no declarado)'}")
        for v in informe_sombra.veredictos:
            print(" ", v.linea())
            if not v.ok:
                # Las medidas que vigilan la sombra NO se pueden poner en sombra: sería apagar el
                # único mecanismo que impide que apagar salga gratis.
                fallas.append(f"{v.id}: el marco no cumple su propia regla")

    if fallas:
        print(f"\nACEPTACIÓN ✗ — {len(fallas)} problema(s)")
        for f in fallas:
            print("  ·", f)
        return 1
    print(f"\nACEPTACIÓN ✓ — {rojos} defectos en rojo, {verdes} verdes correctos, "
          f"{len(huecos)} huecos declarados sin tapar")
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


# El mismo modismo que `cli.py` y `corpus.py`, y por el mismo motivo: con
# `if __name__ == "__main__"` el mutante que da vuelta el comparador hace que el módulo se ejecute
# al IMPORTARSE, y el arnés muere durante el descubrimiento con un `SystemExit`. Eso no es un
# mutante sobreviviente ni uno muerto: es una ronda inconclusa, que vale menos que las dos.
_entrada_directa = {"__main__": main}.get(__name__)
if _entrada_directa:
    sys.exit(_entrada_directa())
