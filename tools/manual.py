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
from datetime import date
from pathlib import Path

# La misma forma que `tools/cli.py`. La versión con guarda —`if RAIZ not in sys.path:
# sys.path.insert(0, RAIZ)`— dejaba dos mutantes que ningún test podía matar: en un test `RAIZ`
# SIEMPRE está en el camino, así que ni la guarda ni el índice se pueden distinguir de su
# contrario. La posición no es un detalle: cada consumidor de Oracle tiene su propio `catalogos/`,
# y si el suyo va primero, sombrea el del lenguaje.
RAIZ = str(Path(__file__).resolve().parent.parent)
RAIZ_PAQUETE = Path(RAIZ)
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


def catalogo_universal() -> dict:
    """Las medidas que Oracle trae y que declaran explícitamente ámbito ``universal``.

    Son parte del lenguaje igual que los vocabularios: viajan en el paquete y valen para cualquiera.
    Las de un proyecto no van acá —cambian con él, y para eso está `oracle contexto`—.

    Se carga adentro de la función y con `except`: el manual tiene que poder imprimirse aunque el
    catálogo no cargue. Un manual que revienta porque una medida está mal escrita es un manual que
    no se puede consultar justo cuando hace falta.
    """
    try:
        import catalogos.escalares  # noqa: F401  registra las escalares del catálogo base
        from nucleo.macro import macros_base
        from nucleo.medida import cargar_catalogo
        from nucleo.proyecto import (FuenteCatalogo, ORIGEN_CATALOGO_BASE,
                                     OrigenCatalogo)

        bases = [
            FuenteCatalogo(RAIZ_PAQUETE / "catalogos", ORIGEN_CATALOGO_BASE),
            FuenteCatalogo(RAIZ_PAQUETE / "perfiles" / "python" / "catalogos",
                            OrigenCatalogo("perfil", "python")),
        ]
        cargado = cargar_catalogo(
            [fuente for fuente in bases if fuente.directorio.is_dir()], macros=macros_base())
        return cargado.filtrar(lambda entrada: entrada.medida.ambito == "universal")
    except Exception:
        return {}


def _medidas_como_entradas() -> list[tuple[str, str]]:
    """Cada medida con lo que NO ve, que es lo que un lector necesita saber de una que no escribió.

    El `alcance` y no el `porque`: el `porque` justifica el número ante quien lo discute; el
    `alcance` dice qué NO cubre, que es lo único que evita confiar de más en un verde.
    """
    return [(mid, (getattr(m, "alcance", "") or "").strip())
            for mid, m in sorted(catalogo_universal().items())]


def _lista(vocabulario: dict[str, str]) -> list[tuple[str, str]]:
    return sorted(vocabulario.items())


def temas() -> tuple[str, ...]:
    """Los temas que el manual sabe mostrar, en el orden en que conviene leerlos."""
    return tuple(VOCABULARIOS) + ("verbos", "medidas")


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
    if tema == "medidas":
        return _medidas_como_entradas()
    raise TemaDesconocido(tema)


def titulo(tema: str) -> str:
    if tema in VOCABULARIOS:
        return VOCABULARIOS[tema][0]
    if tema == "verbos":
        return "los verbos del CLI, por sustantivo"
    if tema == "medidas":
        return "las medidas universales que Oracle trae, y qué NO ve cada una"
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
    if not nombres:
        partes.append("  (ninguna entrada declarada)")
        return "\n".join(partes)
    columna = max(len(nombre) for nombre, _ in nombres) + 2
    # Con nombres largos —los ids de medida pasan de cincuenta caracteres— la columna alineada se
    # come dos tercios del renglón y el texto queda en una tira de veinte. A partir de un tercio del
    # ancho conviene bajar la prosa a la línea siguiente: se pierde el barrido vertical de nombres,
    # que con ids largos ya no servía, y se gana el ancho que la explicación necesita.
    if columna > ancho // 3:
        sangria = " " * 6
        for nombre, sentido in nombres:
            partes.append(f"  {nombre}")
            partes.extend(sangria + l.lstrip() if i == 0 else l
                          for i, l in enumerate(_envolver(sentido, ancho - 6, sangria)))
            partes.append("")
        return "\n".join(partes).rstrip("\n")
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


# ---- la tercera vista: `man` ------------------------------------------------------
#
# La terminal, el sitio y `man` salen de las MISMAS entradas. Un manual escrito tres veces se
# desincroniza tres veces; éste no tiene dónde. `man` importa porque es donde alguien que instaló
# Oracle con un gestor de paquetes va a buscar primero, y porque funciona sin red.
#
# El roff se escribe a mano, sin biblioteca, por la misma razón que todo lo demás del proyecto: una
# dependencia para emitir doce macros no se paga sola.

VERSION_MANUAL_MAN = "1"


def _roff(texto: str) -> str:
    """Escapa un texto para roff, y traduce la puntuación que groff maltrata.

    Cuatro cosas rompen una página de manual, y las cuatro en silencio:

    · la barra invertida es el carácter de escape de roff, así que una sola convierte lo que sigue
      en una directiva;
    · una línea que EMPIEZA con punto o apóstrofo es una macro — la prosa de una medida puede
      empezar con «.» sin que nadie lo piense, y groff se la come entera;
    · un guion largo crudo sale DUPLICADO. Medido: «uno — dos» se renderiza «uno —— dos». La
      forma correcta es el escape `\\[em]`;
    · una comilla invertida se convierte en comilla simple IZQUIERDA, así que `segun` sale
      ‘segun‘, con las dos comillas para el mismo lado. Los pares de comillas invertidas son
      código en la prosa del proyecto, y en una página de manual eso se escribe en negrita.
    """
    salida = texto.replace("\\", "\\e")
    salida = salida.replace("—", "\\[em]")
    partes = salida.split("`")
    if len(partes) % 2 == 1:          # pares completos: 1 texto + n×(código + texto)
        salida = partes[0] + "".join(
            f"\\fB{codigo}\\fR{resto}" for codigo, resto in zip(partes[1::2], partes[2::2]))
    if salida[:1] in (".", "'"):
        salida = "\\&" + salida
    return salida


def man(tema: str | None = None) -> str:
    """La página de manual, entera o de un tema. En roff, para `man -l` o para instalar.

    Sin tema sale `oracle-manual(7)`, que es la sección de las convenciones y los formatos —no la
    de los comandos, que es la 1—: lo que se documenta acá es el LENGUAJE, no el ejecutable.
    """
    hoy = date.today().isoformat()
    nombre = "oracle-manual" if tema is None else f"oracle-{tema}"
    # El nombre ya está a la izquierda del guion; repetirlo a la derecha es ruido en la única
    # línea que `apropos` y `whatis` indexan.
    breve = "la referencia del lenguaje Oracle" if tema is None else titulo(tema)
    lineas = [
        f'.TH {nombre.upper()} 7 {hoy} "Oracle {VERSION_MANUAL_MAN}" "Metalenguaje de medidas"',
        ".SH NOMBRE",
        f"{_roff(nombre)} \\- {_roff(breve)}",
        ".SH DESCRIPCIÓN",
        _roff("Esta página no se escribió: se generó. Cada entrada sale de la declaración que el "
              "lenguaje ya tiene, así que no hay dónde quede vieja. La misma referencia se lee con "
              "«oracle manual» y en el sitio del proyecto."),
    ]
    for t in (temas() if tema is None else (tema,)):
        lineas.append(".SH " + _roff(t.upper()))
        lineas.append(_roff(titulo(t)))
        for opcion, sentido in entradas(t):
            lineas.append(".TP")
            lineas.append(f".B {_roff(opcion)}")
            lineas.append(_roff(sentido))
    lineas.append(".SH VER TAMBIÉN")
    lineas.append(_roff("oracle(1). El código y las decisiones: "
                        "https://github.com/Segtem/oracle"))
    return "\n".join(lineas) + "\n"


def man_del_comando() -> str:
    """`oracle(1)`: el ejecutable. Sale de `VERBOS`, que es de donde sale el despacho.

    Va en la sección 1 y no en la 7 porque documenta un comando. Los verbos NO se copian: los lee
    del mismo diccionario contra el que el CLI despacha, así que un verbo nuevo aparece acá solo —
    que es exactamente lo que `meta.todo_verbo_del_cli_esta_en_la_ayuda` pide para la ayuda.
    """
    lineas = [
        f'.TH ORACLE 1 {date.today().isoformat()} "Oracle {VERSION_MANUAL_MAN}" '
        f'"Metalenguaje de medidas"',
        ".SH NOMBRE",
        f"oracle \\- {_roff('escribir medidas falsables sobre lo que un proceso produjo')}",
        ".SH SINOPSIS",
        ".B oracle",
        ".I sustantivo verbo",
        "[" + _roff("argumentos") + "]",
        ".SH DESCRIPCIÓN",
        _roff("Oracle no juzga artefactos: evalúa medidas que alguien escribió, cada una con su "
              "umbral, de dónde salió ese número y qué NO mira. Los verbos van por sustantivo."),
        ".SH VERBOS",
    ]
    for sustantivo, verbos in _verbos().items():
        lineas.append(".TP")
        lineas.append(f".B oracle {_roff(sustantivo)}")
        lineas.append(_roff(" · ".join(verbos)))
    lineas.append(".SH VER TAMBIÉN")
    lineas.append(_roff("oracle-manual(7), y una página por tema: "
                        + ", ".join(f"oracle-{t}(7)" for t in temas())))
    return "\n".join(lineas) + "\n"


def paginas_man() -> dict[str, str]:
    """Todas las páginas: `oracle.1`, `oracle-manual.7` y una por tema.

    Una página por tema y no una sola gigante porque así funciona `man oracle-segun`, que es como
    se consulta una referencia: por el nombre que uno no se acuerda, no leyendo el índice.
    """
    paginas = {"man1/oracle.1": man_del_comando(),
               "man7/oracle-manual.7": man()}
    for tema in temas():
        paginas[f"man7/oracle-{tema}.7"] = man(tema)
    return paginas


def instalar_man(destino: Path) -> list[Path]:
    """Escribe las páginas bajo `destino`, con la estructura que `man` espera («man1/», «man7/»).

    Devuelve las rutas escritas. No toca el `MANPATH` ni corre `mandb`: eso es del sistema, y una
    herramienta que edita la configuración de otra sin que se lo pidan es la clase de cosa que este
    proyecto no hace.
    """
    escritas = []
    for relativa, contenido in sorted(paginas_man().items()):
        ruta = destino / relativa
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding="utf-8")
        escritas.append(ruta)
    return escritas


def _cortable(nombre: str) -> str:
    """El término, con una oportunidad de corte después de cada `_` y cada `.`.

    Un id de medida es una sola palabra para el navegador: el guión bajo no es punto de corte en
    CSS, a diferencia del guión medio. Sin esto el término desborda su columna y se dibuja encima
    de la definición. Medido el 2026-09-03: 56 de los 90 términos del manual desbordaban, y el peor
    —`meta.ninguna_exclusion_de_mutador_se_apoya_en_una_premisa_falsa`, 63 caracteres— pedía unos
    640 px en una columna de 194 px útiles.

    El corte va acá y no sólo en el CSS porque `overflow-wrap` parte donde llega, a mitad de
    palabra. Con `<wbr>` los cortes caen en el límite entre partes del nombre, que es donde una
    persona los leería. Queda igual `overflow-wrap` como red: el segmento más largo hoy mide 17
    caracteres y entran 19, pero eso vale para el catálogo de hoy, no para el de mañana.
    """
    return _html.escape(nombre).replace("_", "_<wbr>").replace(".", ".<wbr>")


def html() -> str:
    """El mismo manual, para el sitio. Sale de las mismas entradas: no hay una segunda copia."""
    partes = ['<div class="manual">']
    for tema in temas():
        # El rótulo va en su propia columna, como las secciones de la portada: sin eso el texto se
        # amontona en el tercio izquierdo y media pantalla queda en blanco.
        partes.append(f'<section class="tema" id="manual-{_html.escape(tema)}">')
        # El nombre del tema pasa por `_cortable` igual que los términos: `como_se_detecto` en
        # Archivo Black a 32px es más ancho que su columna, y sin corte se dibujaba encima de la
        # primera entrada de la columna de al lado. Es el mismo defecto que el del `dt`, en el
        # título de la sección, y sobrevivió al primer arreglo porque miré sólo los términos.
        partes.append(f'<div class="rotulo"><h2>{_cortable(tema)}</h2>'
                      f'<p>{_html.escape(titulo(tema))}</p></div>')
        partes.append("<dl>")
        for nombre, sentido in entradas(tema):
            partes.append(f"<dt>{_cortable(nombre)}</dt>"
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
               letter-spacing: -0.02em; overflow-wrap: break-word; }
  .rotulo p { margin: 0; font-family: var(--mono); font-size: 12px; line-height: 1.55;
              color: oklch(0.45 0.01 95); }
  /* Sin hueco entre columnas: con `column-gap` la línea de cada fila se parte en dos trazos y
     parece un borde roto. El aire lo pone el padding del término, que sí se puede subrayar. */
  .manual dl { margin: 0; padding: 26px var(--mg); display: grid;
               grid-template-columns: minmax(10rem, 14rem) minmax(0, 1fr); gap: 0; }
  .manual dt { font-family: var(--mono); font-weight: 700;
               padding: 10px 30px 10px 0; overflow-wrap: break-word; }
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
    p.add_argument("--man", action="store_true", help="emitir roff para `man`")
    p.add_argument("--instalar-man", metavar="DIR",
                   help="escribir las páginas bajo DIR/man1 y DIR/man7")
    args = p.parse_args(argv)

    if args.tema is not None and args.tema not in temas():
        print(f"tema desconocido: {args.tema!r}\nlos temas son: {', '.join(temas())}",
              file=sys.stderr)
        return 2
    if args.instalar_man:
        for ruta in instalar_man(Path(args.instalar_man)):
            print(ruta)
    elif args.man:
        print(man(args.tema), end="")
    else:
        print(pagina() if args.html else texto(args.tema))
    return 0


# El mismo modismo que `cli.py` y `corpus.py`. Con `is not None`, el mutante `IsNot → Is` hace que
# el módulo se ejecute a sí mismo al importarlo y llame a `None()`: no muere, rompe el arnés, y un
# error de arnés no es una muerte. Con la verdad del valor, el mutante no existe.
_entrada_directa = {"__main__": main}.get(__name__)
if _entrada_directa:
    sys.exit(_entrada_directa())
