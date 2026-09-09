"""Censa varios proyectos a la vez y conserva el estado con su fecha.

    python tools/censar.py --proyecto . --proyecto ../otro-proyecto/medidas
    python tools/censar.py --proyecto . --hechos
    python tools/censar.py --proyecto . --html censo.html

Hasta hoy, contestar «cómo está todo» era correr seis comandos en tres repositorios y armar la
tabla a mano. Esto lo hace de una y deja el resultado escrito.

## Por qué «censo» y no «relevo»

En este ecosistema «relevo» ya significa otra cosa: el traspaso de turno entre sesiones, con su
`RELEVO.md` y, en un consumidor, sus medidas `relevo.*`. Son homónimos sin relación operativa, y
`oracle relevar` haría pensar que sirve para cerrar el turno. Un censo es un empadronamiento
sincrónico de una población —acá, los proyectos— que cuenta sin juzgar.

## Hechos, no veredicto

Acá se producen los hechos; el juicio queda en `catalogos/meta/`, igual que en `nucleo/marco.py`.
El censo emite la relación `proyecto_censado` y **no calcula ningún puntaje**. La razón no
es estética: este proyecto ya vio a una cifra publicada convertirse en objetivo —la proporción de
falsación, que desde el 2026-08-24 es una cifra de costo y no un criterio— y un tablero con un
número de «salud» es la forma más rápida de repetirlo.

**La regla, en una línea:** ni cocientes, ni porcentajes, ni semáforos, ni booleanos de conformidad.
Todo denominador viaja como un hecho independiente, y ningún hecho agrega ni compensa entre dos
proyectos: la deuda de uno no se tapa con el volumen del otro.

## No compara contra el censo anterior, a propósito

La información valiosa suele ser el CAMBIO, pero calcularlo acá sería un error. «El anterior» es una
heurística frágil —¿el archivo más reciente en disco? ¿el commit padre?— y con dos agentes que se
turnan un repositorio puede ser de otra rama o de un árbol sucio. Y si la comparación se equivoca,
el número malo queda grabado dentro del censo de hoy, que es un registro histórico y no se corrige.
El precedente está en `corpus/proceso/007-relevo-verde-arbol-sucio`: una regla comparó contra HEAD
mientras los cambios estaban sin commitear, el diff salió vacío y la verificación se declaró vigente.

Una comparación necesita sus dos puntas declaradas por quien la pide, no adivinadas acá.

## Todo número viene con su denominador

`915 mutantes muertos` no dice nada sin `de 915, con 29 mutadores`. Esa regla no es una precaución:
el 2026-09-07 se descubrió que el paquete publicado medía con **5 de 29** mutadores y devolvía «0
sobrevivientes» sobre un espacio 5,8 veces más chico. El número era cierto y engañaba.

## Lo que NO sale

Hereda el contrato de `nucleo/diagnostico.py`: no salen filas de evidencia, ni `porque`, ni
`alcance`, ni nombres de archivo del dominio. De cada proyecto salen **conteos** y los ids de las
medidas que el propio Oracle publica —las `meta.*` de las sombras—, nunca los del dominio. Un censo se puede
compartir con quien ya tiene acceso a los proyectos; una evidencia no.
"""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path = [str(RAIZ), *sys.path]

import catalogos  # noqa: F401,E402  registra las escalares del catálogo base
from nucleo.caso import PROCEDENCIAS, cargar_casos  # noqa: E402
from nucleo.marco import hechos_de_sombra  # noqa: E402
from nucleo.mutacion import cobertura_de_mutadores  # noqa: E402
from nucleo.proyecto import (Proyecto, catalogo_efectivo, configuracion,  # noqa: E402
                             escalares_del_proyecto, macros_del_proyecto)
from nucleo.version import VERSION_ALGEBRA, VERSION_DISTRIBUCION, VERSION_SINTAXIS  # noqa: E402
from tools import sintaxis as tsintaxis  # noqa: E402

RELACION = "proyecto_censado"

# El nombre con el que se identifica un proyecto en el censo. Es el de su directorio, no su
# ruta: la ruta es de una máquina, y un censo que trae rutas absolutas no se puede comparar
# con el de otra ni compartir sin pensarlo dos veces.
def _nombre(raiz: Path) -> str:
    raiz = raiz.resolve()
    return raiz.parent.name if raiz.name == "medidas" else raiz.name


def _git(raiz: Path, *args: str) -> str:
    try:
        salida = subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True)
    except OSError:
        return ""
    return salida.stdout.strip() if salida.returncode == 0 else ""


def censar_uno(raiz: Path, *, confiar: bool = False) -> dict:
    """Los hechos de UN proyecto. Cada conteo con lo que hace falta para leerlo.

    `confiar` viene en False y hay que pedirlo: ejecutar el `escalares.py` de un proyecto ajeno es
    correr código de otro, y el CLI lo exige con una bandera explícita. Que la biblioteca lo hiciera
    sola por omisión era la puerta de atrás de esa misma decisión.
    """
    proy = Proyecto(raiz)
    with escalares_del_proyecto(proy, confiar=confiar):
        catalogo = catalogo_efectivo(proy, macros=macros_del_proyecto(proy))
    casos = cargar_casos(proy.corpus)
    conf = configuracion(proy)

    # El REPARTO POR ORIGEN, que es un hecho, en vez de un «propias / heredadas» que sería una
    # clasificación inventada acá. El primer intento partía por el prefijo del id y daba que Oracle
    # tenía «0 medidas propias»: las suyas se llaman `meta.*` y viven en el catálogo base, que para
    # Oracle ES el suyo y para un consumidor es heredado. La misma medida cambia de lado según quién
    # pregunte, así que el censo no elige: dice de dónde vino cada una y que lea quien lee.
    por_origen = Counter(e.origen.clase for e in getattr(catalogo, "entradas", {}).values())
    procedencias = [c.get("procedencia", "sin_declarar") for c in casos]
    conocidas = set(PROCEDENCIAS) | {"sin_declarar"}
    if set(procedencias) - conocidas:
        raise ValueError(
            f"procedencias que el censo no sabe contar: {sorted(set(procedencias) - conocidas)}. "
            "Agregarlas acá, o el total dejaría de cerrar sin que nadie lo note")
    # Las sombras se leen del proyecto, no de una corrida: son una declaración, y su antigüedad es
    # el dato que envejece. `dias` sale de la misma función que usa la aceptación.
    sombras = hechos_de_sombra(conf.sombra, {}, catalogo)["sombra"]
    informe_sintaxis = tsintaxis.verificar_catalogo(raiz)
    cobertura = cobertura_de_mutadores()

    return {
        "proyecto": _nombre(raiz),
        "commit": (_git(raiz, "rev-parse", "--short", "HEAD") or "sin_git"),
        "arbol_sucio": bool(_git(raiz, "status", "--short")),
        "medidas": len(catalogo),
        "medidas_del_proyecto": por_origen.get("proyecto", 0),
        "medidas_del_catalogo_base": por_origen.get("catalogo_base", 0),
        "medidas_de_perfiles": por_origen.get("perfil", 0),
        "medidas_de_bibliotecas": por_origen.get("biblioteca", 0),
        "casos": len(casos),
        "casos_observados": procedencias.count("observada"),
        "casos_construidos": procedencias.count("construida"),
        # `generada` estuvo AUSENTE en el primer intento y el test lo encontró: los conteos daban
        # 183 sobre 189 casos, y seis quedaban invisibles. Es el problema del denominador cometido
        # adentro del censo que existe para evitarlo. Las cuatro procedencias salen del vocabulario,
        # no de una lista escrita acá, así que una quinta no puede volver a caerse en silencio.
        "casos_generados": procedencias.count("generada"),
        "casos_sin_procedencia": procedencias.count("sin_declarar"),
        "sombras": len(sombras),
        "sombra_mas_vieja_dias": max((s["dias"] for s in sombras), default=0),
        "archivos_verificados": (informe_sintaxis["medidas"] + informe_sintaxis["macros"]
                                 + informe_sintaxis["casos"]),
        "archivos_ilegibles": len(informe_sintaxis["ilegibles"]),
        # Los ilegibles también traen json_igual=False, pero no llegaron a compararse.
        "archivos_no_identicos": sum(1 for f in informe_sintaxis["filas"]
                                     if f["imprimio"] and not f["json_igual"]),
        # El denominador viaja con el número, siempre. Ver el docstring del módulo.
        "mutadores_disponibles": cobertura["total"],
        "mutadores_de_otro_autor": cobertura["ajenos"],
        "oracle_distribucion": VERSION_DISTRIBUCION,
        "oracle_algebra": VERSION_ALGEBRA,
        "oracle_sintaxis": VERSION_SINTAXIS,
    }


def _fila_ilegible(raiz: Path, motivo: str) -> dict:
    """La fila de un proyecto que no se pudo leer. Dice quién es, y por qué no se pudo.

    Sin conteos: un proyecto ilegible no tiene «0 medidas», tiene medidas que nadie contó, y la
    diferencia es todo el punto de esta herramienta. Ver `LosConteosQueFaltanNoSeInventan`.
    """
    return {
        "proyecto": _nombre(raiz),
        "commit": (_git(raiz, "rev-parse", "--short", "HEAD") or "sin_git"),
        "arbol_sucio": bool(_git(raiz, "status", "--short")),
        "no_se_pudo_censar": motivo,
    }


def censar(raices: list[Path], *, confiar: bool = False) -> dict:
    """Los hechos de VARIOS proyectos. Uno ilegible no se lleva puestos a los demás.

    `censar_uno` levanta la excepción —es la primitiva de a uno, y quien la llama decide—; acá no,
    porque un censo de tres proyectos que muere en el primero no informa de los otros dos, que se
    podían leer perfectamente. Es la misma lección que 0.9.1 le enseñó a `sintaxis.py`: una
    herramienta que se cae no informa. El motivo viaja en la fila y se imprime en las dos vistas.
    """
    filas = []
    for r in raices:
        raiz = Path(r)
        try:
            filas.append(censar_uno(raiz, confiar=confiar))
        except Exception as caido:  # noqa: BLE001 — cualquier motivo es un hecho del censo
            filas.append(_fila_ilegible(raiz, f"{type(caido).__name__}: {caido}"))
    return {RELACION: filas}


def _cuando() -> str:
    return datetime.now(timezone.utc).isoformat()


def _reparto_medidas(f: dict) -> str:
    """De dónde vienen las medidas. Una sola función para las dos vistas: si cada una armara su
    frase, la página y la terminal podrían decir cosas distintas del mismo hecho."""
    partes = [(f["medidas_del_proyecto"], "del proyecto"),
              (f["medidas_del_catalogo_base"], "del catálogo base"),
              (f["medidas_de_perfiles"], "de perfiles"),
              (f["medidas_de_bibliotecas"], "de bibliotecas")]
    return " · ".join(f"{n} {q}" for n, q in partes if n)


def _con_reparto(f: dict) -> str:
    """El reparto con su separador, o nada. Un proyecto vacío no tiene de dónde repartir, y
    concatenar un « · » a secas dejaba un separador colgando que no separa nada."""
    reparto = _reparto_medidas(f)
    return f" · {reparto}" if reparto else ""


def imprimir(hechos: dict, cuando: str) -> str:
    filas = hechos[RELACION]
    lineas = [f"CENSO — {len(filas)} proyecto(s) · {cuando}", ""]
    for f in filas:
        sucio = " · árbol sucio" if f["arbol_sucio"] else ""
        lineas.append(f"{f['proyecto']}  ({f['commit']}{sucio})")
        if "no_se_pudo_censar" in f:
            lineas.append(f"    NO SE PUDO CENSAR — {f['no_se_pudo_censar']}")
            lineas.append("")
            continue
        lineas.append(f"    medidas    {f['medidas']}"
                      + _con_reparto(f))
        lineas.append(f"    corpus     {f['casos']} casos "
                      f"· {f['casos_observados']} observados"
                      f" · {f['casos_construidos']} construidos"
                      f" · {f['casos_generados']} generados"
                      f" · {f['casos_sin_procedencia']} sin declarar")
        # Poder imprimir no asegura conservar el JSON: las dos fallas se cuentan aparte.
        lineas.append(f"    sintaxis   {f['archivos_verificados'] - f['archivos_ilegibles']}"
                      f"/{f['archivos_verificados']} archivos se imprimen"
                      f" · {f['archivos_no_identicos']} se imprimen y no vuelven idénticos")
        if f["sombras"]:
            lineas.append(f"    sombras    {f['sombras']} declaradas "
                          f"· la más vieja hace {f['sombra_mas_vieja_dias']} días")
        else:
            lineas.append("    sombras    ninguna declarada")
        lineas.append(f"    medido con oracle {f['oracle_distribucion']} "
                      f"y {f['mutadores_disponibles']} mutadores "
                      f"({f['mutadores_de_otro_autor']} de otro autor)")
        lineas.append("")
    lineas.append("Esto es un censo, no un puntaje: son hechos con su fecha y su "
                  "procedencia.")
    lineas.append("El juicio lo dan las medidas, y cada proyecto lo corre con `oracle test`.")
    return "\n".join(lineas)


_ESTILO = """
:root { color-scheme: light dark; --tinta:#1a1a1a; --papel:#fbfbfa; --tenue:#6a6a6a;
        --linea:#e0dedb; --marca:#8a6d3b; }
@media (prefers-color-scheme: dark) {
  :root { --tinta:#e8e6e3; --papel:#161615; --tenue:#9a9a95; --linea:#33322f; --marca:#c8a86b; } }
body { margin:0; background:var(--papel); color:var(--tinta);
       font:15px/1.55 ui-serif, Georgia, "Times New Roman", serif; }
main { max-width:52rem; margin:0 auto; padding:3rem 1.5rem 5rem; }
h1 { font-size:1.6rem; font-weight:600; margin:0 0 .2rem; letter-spacing:-.01em; }
.fecha { color:var(--tenue); font-size:.85rem; margin:0 0 2.5rem;
         font-family:ui-monospace, SFMono-Regular, Menlo, monospace; }
section { border-top:1px solid var(--linea); padding:1.4rem 0; }
h2 { font-size:1.1rem; font-weight:600; margin:0 0 .1rem; }
.commit { color:var(--tenue); font-size:.8rem; font-weight:400;
          font-family:ui-monospace, SFMono-Regular, Menlo, monospace; }
dl { display:grid; grid-template-columns:9rem 1fr; gap:.35rem 1rem; margin:1rem 0 0; }
dt { color:var(--tenue); font-size:.85rem; }
dd { margin:0; }
.n { font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-weight:600; }
.aviso { color:var(--marca); }
footer { border-top:1px solid var(--linea); margin-top:2rem; padding-top:1.2rem;
         color:var(--tenue); font-size:.85rem; }
"""


def _dd(etiqueta: str, contenido: str) -> str:
    return f"<dt>{etiqueta}</dt><dd>{contenido}</dd>"


def a_html(hechos: dict, cuando: str) -> str:
    """La misma información que el CLI, sin un solo número que el CLI no diga.

    Dos vistas de los mismos hechos y ninguna con algo de más: si la página mostrara un dato que la
    terminal no, habría dos verdades que mantener sincronizadas a mano.
    """
    e = html.escape
    # El archivo se escribe en UTF-8 y hay que decirlo: sin `charset`, un navegador que lo abre
    # desde el disco adivina la codificación, y «días», «más vieja» y «árbol sucio» —las palabras
    # que este censo usa para lo que importa— son las primeras en salir rotas.
    partes = ['<!doctype html>', '<html lang="es">', '<meta charset="utf-8">',
              '<meta name="viewport" content="width=device-width, initial-scale=1">',
              f"<title>Censo — {e(cuando[:10])}</title>", f"<style>{_ESTILO}</style>",
              "<main>", "<h1>Censo</h1>",
              f"<p class=fecha>{e(cuando)}</p>"]
    for f in hechos[RELACION]:
        sucio = " · árbol sucio" if f["arbol_sucio"] else ""
        partes.append("<section>")
        partes.append(f"<h2>{e(f['proyecto'])} "
                      f"<span class=commit>{e(f['commit'])}{e(sucio)}</span></h2>")
        if "no_se_pudo_censar" in f:
            partes.append(f"<p class=aviso>No se pudo censar — "
                          f"{e(f['no_se_pudo_censar'])}</p></section>")
            continue
        partes.append("<dl>")
        partes.append(_dd("medidas", f"<span class=n>{f['medidas']}</span>"
                                     + e(_con_reparto(f))))
        partes.append(_dd("corpus", f"<span class=n>{f['casos']}</span> casos · "
                                    f"{f['casos_observados']} observados · "
                                    f"{f['casos_construidos']} construidos · "
                                    f"{f['casos_generados']} generados · "
                                    f"{f['casos_sin_procedencia']} sin declarar"))
        legibles = f["archivos_verificados"] - f["archivos_ilegibles"]
        clase = " class=aviso" if f["archivos_ilegibles"] or f["archivos_no_identicos"] else ""
        partes.append(_dd("sintaxis", f"<span{clase}><span class=n>{legibles}</span>"
                                      f"/{f['archivos_verificados']} archivos se imprimen"
                                      f" · {f['archivos_no_identicos']} se imprimen y no vuelven"
                                      " idénticos</span>"))
        if f["sombras"]:
            partes.append(_dd("sombras", f"<span class=n>{f['sombras']}</span> declaradas · "
                                         f"la más vieja hace {f['sombra_mas_vieja_dias']} días"))
        else:
            partes.append(_dd("sombras", "ninguna declarada"))
        partes.append(_dd("medido con", f"oracle {e(f['oracle_distribucion'])} y "
                                        f"{f['mutadores_disponibles']} mutadores "
                                        f"({f['mutadores_de_otro_autor']} de otro autor)"))
        partes.append("</dl></section>")
    partes.append("<footer><p>Esto es un censo, no un puntaje: son hechos con su fecha y su "
                  "procedencia. El juicio lo dan las medidas, y cada proyecto lo corre con "
                  "<code>oracle test</code>.</p></footer>")
    partes.append("</main>")
    return "\n".join(partes) + "\n"


def argumentos(argv: list[str]):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--proyecto", action="append", metavar="RUTA", required=True,
                   help="raíz de un proyecto Oracle; repetible")
    p.add_argument("--hechos", action="store_true", help="emitir sólo la relación, en JSON")
    p.add_argument("--html", metavar="RUTA", help="además, escribir la página en esta ruta")
    p.add_argument("--confiar-escalares", action="store_true",
                   help="ejecutar el escalares.py de cada proyecto")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = argumentos(sys.argv[1:] if argv is None else argv)
    cuando = _cuando()
    hechos = censar([Path(r) for r in args.proyecto], confiar=args.confiar_escalares)
    if args.html:
        Path(args.html).write_text(a_html(hechos, cuando), encoding="utf-8")
    if args.hechos:
        print(json.dumps(hechos, ensure_ascii=False))
    else:
        print(imprimir(hechos, cuando))
        if args.html:
            print(f"\npágina escrita en {args.html}")
    return 0


_entrada_directa = {"__main__": main}.get(__name__)
if _entrada_directa:
    raise SystemExit(_entrada_directa())
