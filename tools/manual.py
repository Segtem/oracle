"""`oracle manual` — la referencia del lenguaje, armada de lo que el lenguaje ya declara.

No es un documento. Es una vista: cada sección se lee de la fuente que ya existe —los vocabularios
cerrados de `nucleo/vocabulario.py` y `nucleo/caso.py`, las relaciones que emite `nucleo/marco.py`,
los verbos de `tools/cli.py`, el catálogo base— y por eso no puede quedar vieja sin que alguna de
esas fuentes cambie. Un manual escrito a mano envejece en silencio; éste no tiene dónde envejecer.

Lo que sí puede pasar es que aparezca un vocabulario nuevo y nadie lo agregue acá. Eso lo mide
`meta.todo_vocabulario_cerrado_esta_en_el_manual`, que es la razón por la que este archivo entra al
perfil de mutación: custodia una afirmación —«el manual está completo»— que nadie más comprueba.
"""

from __future__ import annotations

import argparse
import html as _html
import sys
from pathlib import Path

# La misma forma que `tools/cli.py`. La versión con guarda —`if RAIZ not in sys.path:
# sys.path.insert(0, RAIZ)`— dejaba dos mutantes que ningún test podía matar: en un test `RAIZ`
# SIEMPRE está en el camino, así que ni la guarda ni el índice se pueden distinguir de su
# contrario. La posición no es un detalle: cada consumidor de Oracle tiene su propio `catalogos/`,
# y si el suyo va primero, sombrea el del lenguaje.
RAIZ = str(Path(__file__).resolve().parent.parent)
sys.path = [RAIZ, *sys.path]

from nucleo.caso import DETECCIONES, ETIQUETAS, PROCEDENCIAS          # noqa: E402
from nucleo.vocabulario import (OPERADORES, ORIGENES_DE_UMBRAL,        # noqa: E402
                                RELACIONES_EXPLICADAS)


class TemaDesconocido(KeyError):
    """Se pidió un tema que el manual no tiene."""


# Cada vocabulario cerrado del lenguaje, con el campo donde se escribe y su registro.
VOCABULARIOS: dict[str, tuple[str, dict[str, str]]] = {
    "operadores": ("los seis operadores de una tubería", OPERADORES),
    "segun": ("de dónde salió el número de un umbral (campo `segun`)", ORIGENES_DE_UMBRAL),
    "etiqueta": ("qué enseña un caso del corpus (campo `etiqueta`)", ETIQUETAS),
    "procedencia": ("de dónde salió la evidencia de un caso (campo `procedencia`)", PROCEDENCIAS),
    "como_se_detecto": ("quién encontró el defecto (campo `como_se_detecto`)", DETECCIONES),
    "relaciones": ("las relaciones que el lenguaje emite sobre sí mismo", RELACIONES_EXPLICADAS),
}


def _lista(vocabulario: dict[str, str]) -> list[tuple[str, str]]:
    return sorted(vocabulario.items())


def temas() -> tuple[str, ...]:
    """Los temas que el manual sabe mostrar, en el orden en que conviene leerlos."""
    return tuple(VOCABULARIOS) + ("verbos",)


def _verbos() -> dict[str, tuple[str, ...]]:
    # Adentro de la función a propósito: `tools.cli` importa este módulo para el subcomando, y a
    # nivel de módulo el ciclo rompe el arranque del CLI.
    from tools.cli import VERBOS
    return {sustantivo: tuple(sorted(vs)) for sustantivo, vs in sorted(VERBOS.items())}


def entradas(tema: str) -> list[tuple[str, str]]:
    """Las entradas de un tema: pares (nombre, qué significa)."""
    if tema in VOCABULARIOS:
        return _lista(VOCABULARIOS[tema][1])
    if tema == "verbos":
        return [(f"oracle {sustantivo}", " · ".join(vs))
                for sustantivo, vs in _verbos().items()]
    raise TemaDesconocido(tema)


def titulo(tema: str) -> str:
    if tema in VOCABULARIOS:
        return VOCABULARIOS[tema][0]
    if tema == "verbos":
        return "los verbos del CLI, por sustantivo"
    raise TemaDesconocido(tema)


def _envolver(texto: str, ancho: int, sangria: str) -> list[str]:
    lineas, actual = [], ""
    for palabra in texto.split():
        if actual and len(actual) + 1 + len(palabra) > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f"{actual} {palabra}".strip()
    if actual:
        lineas.append(actual)
    return [lineas[0]] + [sangria + l for l in lineas[1:]]


def seccion(tema: str, ancho: int = 96) -> str:
    """Una sección del manual, en texto para la terminal."""
    partes = [f"{tema.upper()} — {titulo(tema)}", ""]
    nombres = entradas(tema)
    columna = max(len(nombre) for nombre, _ in nombres) + 2
    for nombre, sentido in nombres:
        sangria = " " * (columna + 2)
        envuelto = _envolver(sentido, ancho - columna - 2, sangria)
        partes.append(f"  {nombre.ljust(columna)}{envuelto[0]}")
        partes.extend(envuelto[1:])
    return "\n".join(partes)


def texto(tema: str | None = None, ancho: int = 96) -> str:
    """El manual entero, o un tema."""
    if tema is not None:
        return seccion(tema, ancho)
    bloques = [seccion(t, ancho) for t in temas()]
    return "\n\n".join(bloques)


def html() -> str:
    """El mismo manual, para el sitio. Sale de las mismas entradas: no hay una segunda copia."""
    partes = ['<div class="manual">']
    for tema in temas():
        # El rótulo va en su propia columna, como las secciones de la portada: sin eso el texto se
        # amontona en el tercio izquierdo y media pantalla queda en blanco.
        partes.append(f'<section class="tema" id="manual-{_html.escape(tema)}">')
        partes.append(f'<div class="rotulo"><h2>{_html.escape(tema)}</h2>'
                      f'<p>{_html.escape(titulo(tema))}</p></div>')
        partes.append("<dl>")
        for nombre, sentido in entradas(tema):
            partes.append(f"<dt>{_html.escape(nombre)}</dt>"
                          f"<dd>{_html.escape(sentido)}</dd>")
        partes.append("</dl>")
        partes.append("</section>")
    partes.append("</div>")
    return "\n".join(partes)


ESTILO = """
  :root { --tinta: oklch(0.16 0 0); --papel: oklch(0.96 0.004 95);
          --acento: oklch(0.58 0.20 45); --regla: 3px; --mg: 44px;
          --mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
          --negra: 'Archivo Black', 'Archivo', system-ui, sans-serif; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--papel); color: var(--tinta); font-size: 17px;
         line-height: 1.5; font-family: 'Archivo', system-ui, -apple-system, sans-serif; }
  a { color: inherit; text-underline-offset: 3px; }
  a:hover { color: var(--acento); }
  .barra { display: flex; align-items: center; justify-content: space-between; gap: 16px;
           padding: 16px var(--mg); background: var(--tinta); color: var(--papel);
           font-family: var(--mono); font-size: 12px; letter-spacing: 0.06em;
           text-transform: uppercase; flex-wrap: wrap; }
  .barra a { text-decoration: none; }
  .barra nav { display: flex; gap: 26px; flex-wrap: wrap; }
  .encabezado { padding: 48px var(--mg) 30px; }
  .encabezado h1 { font-family: var(--negra); font-size: clamp(40px, 8vw, 78px); margin: 0 0 20px;
                   line-height: 0.92; letter-spacing: -0.035em; text-transform: uppercase; }
  .encabezado p { max-width: 62ch; font-size: 19px; margin: 0; text-wrap: pretty; }
  .indice { display: flex; flex-wrap: wrap; gap: 10px; padding: 0 var(--mg) 34px; }
  .indice a { font-family: var(--mono); font-size: 13px; text-decoration: none;
              padding: 7px 14px; box-shadow: inset 0 0 0 2px var(--tinta); }
  .indice a:hover { background: var(--tinta); color: var(--papel); }
  .tema { display: grid; grid-template-columns: 19rem minmax(0, 1fr);
          border-top: var(--regla) solid var(--tinta); }
  .rotulo { padding: 26px var(--mg); border-right: var(--regla) solid var(--tinta);
            position: sticky; top: 0; align-self: start; }
  .rotulo h2 { font-family: var(--negra); font-size: clamp(24px, 2.6vw, 32px);
               margin: 0 0 10px; line-height: 1.02; text-transform: uppercase;
               letter-spacing: -0.02em; }
  .rotulo p { margin: 0; font-family: var(--mono); font-size: 12px; line-height: 1.55;
              color: oklch(0.45 0.01 95); }
  /* Sin hueco entre columnas: con `column-gap` la línea de cada fila se parte en dos trazos y
     parece un borde roto. El aire lo pone el padding del término, que sí se puede subrayar. */
  .manual dl { margin: 0; padding: 26px var(--mg); display: grid;
               grid-template-columns: minmax(10rem, 14rem) minmax(0, 1fr); gap: 0; }
  .manual dt { font-family: var(--mono); font-weight: 700;
               padding: 10px 30px 10px 0; }
  .manual dd { margin: 0; padding: 10px 0; max-width: 92ch; text-wrap: pretty; }
  .manual dt:not(:first-of-type), .manual dt:not(:first-of-type) + dd {
    border-top: 1px solid oklch(0.16 0 0 / 0.14); }
  .pie { border-top: var(--regla) solid var(--tinta); padding: 26px var(--mg);
         font-family: var(--mono); font-size: 13px; }
  @media (max-width: 1000px) {
    .tema { grid-template-columns: 1fr; }
    .rotulo { position: static; border-right: 0;
              border-bottom: var(--regla) solid var(--tinta); padding-bottom: 18px; }
    .manual dl { padding-top: 18px; }
  }
  @media (max-width: 760px) {
    :root { --mg: 20px; }
    .manual dl { grid-template-columns: 1fr; gap: 0; }
    .manual dd { padding-top: 4px; padding-bottom: 16px; border-top: 0; }
    .manual dt:not(:first-of-type) { padding-top: 12px; }
  }
"""


def pagina() -> str:
    """La página del sitio, con el mismo cuerpo que imprime la terminal.

    `docs/manual.html` es exactamente la salida de `oracle manual --html`, y un test lo compara:
    la página del sitio no puede quedar atrasada respecto del lenguaje sin que la corrida lo diga.
    """
    indice = "\n".join(
        f'  <a href="#manual-{_html.escape(t)}">{_html.escape(t)}</a>' for t in temas())
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Manual — Oracle</title>
<meta name="description" content="La referencia del lenguaje Oracle: los operadores de una tubería, los vocabularios cerrados de una medida y de un caso, las relaciones que el lenguaje emite sobre sí mismo y los verbos del comando.">
<link rel="canonical" href="https://segtem.github.io/oracle/manual.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Archivo+Black&family=JetBrains+Mono:wght@400;500;700&display=swap">
<style>{ESTILO}</style>
</head>
<body>

<header class="barra">
  <div><strong>oracle</strong> · manual</div>
  <nav>
    <a href="./">inicio</a>
    <a href="https://github.com/Segtem/oracle/blob/main/docs/README.md">documentación</a>
    <a href="https://github.com/Segtem/oracle">github</a>
  </nav>
</header>

<div class="encabezado">
  <h1>Manual</h1>
  <p>Esta página no se escribió: se generó. Cada entrada sale de la declaración que el lenguaje
  ya tiene —los vocabularios cerrados, las relaciones que emite sobre sí mismo, los verbos del
  comando—, así que no hay dónde quede vieja. Lo mismo se lee en la terminal con
  <code>oracle manual</code>.</p>
</div>

<div class="indice">
{indice}
</div>

{html()}

<footer class="pie">
  Generado con <code>oracle manual --html</code> · <a href="https://github.com/Segtem/oracle">Segtem/oracle</a>
</footer>

</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="La referencia del lenguaje, armada de sus fuentes.")
    p.add_argument("tema", nargs="?", help=f"uno de: {', '.join(temas())}")
    p.add_argument("--html", action="store_true", help="emitir HTML para el sitio")
    args = p.parse_args(argv)

    if args.tema is not None and args.tema not in temas():
        print(f"tema desconocido: {args.tema!r}\nlos temas son: {', '.join(temas())}",
              file=sys.stderr)
        return 2
    print(pagina() if args.html else texto(args.tema))
    return 0


# El mismo modismo que `cli.py` y `corpus.py`. Con `is not None`, el mutante `IsNot → Is` hace que
# el módulo se ejecute a sí mismo al importarlo y llame a `None()`: no muere, rompe el arnés, y un
# error de arnés no es una muerte. Con la verdad del valor, el mutante no existe.
_entrada_directa = {"__main__": main}.get(__name__)
if _entrada_directa:
    sys.exit(_entrada_directa())
