#!/usr/bin/env python3
"""Genera las páginas de documentación del sitio desde los `.md` del repositorio.

    python tools/sitio.py --escribir    # regenera docs/*.html desde los .md
    python tools/sitio.py               # falla si alguna página quedó vieja

Una sola fuente por documento: el `.md` es el original y la página es su vista. Antes el sitio
enlazaba los `.md` crudos de GitHub, que se leen como texto plano; duplicarlos a mano en HTML sería
garantizar que se desincronicen. Por eso las páginas se generan y un test (`tests/test_sitio.py`)
falla si alguna quedó atrás, igual que `docs/manual.html` con `oracle manual --html`.

Convierte un subconjunto de Markdown —el que usan estos documentos: títulos, párrafos, listas
anidadas, tablas, bloques de código, citas, enlaces, énfasis— con la biblioteca estándar, porque
Oracle no tiene dependencias y el sitio no va a ser la primera.
"""

from __future__ import annotations

import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"
REPO = "https://github.com/Segtem/oracle"


@dataclass(frozen=True)
class Pagina:
    origen: str   # ruta del .md relativa a la raíz
    salida: str   # ruta del .html relativa a docs/
    grupo: str    # sección del menú lateral
    titulo: str   # cómo se nombra en el menú


PAGINAS = (
    Pagina("docs/README.md", "documentacion.html", "Empezar", "El camino"),
    Pagina("docs/02-de-cero-a-un-rojo.md", "02-de-cero-a-un-rojo.html", "Empezar", "De cero a un rojo"),
    Pagina("docs/03-escribir-una-medida.md", "03-escribir-una-medida.html", "Empezar", "Escribir una medida"),
    Pagina("docs/13-primer-valor.md", "13-primer-valor.html", "Empezar", "La primera medida real"),
    Pagina("docs/05-por-que-la-mutacion.md", "05-por-que-la-mutacion.html", "Entender", "Por qué la mutación"),
    Pagina("docs/07-conectar-a-un-proyecto-propio.md", "07-conectar-a-un-proyecto-propio.html", "Entender", "Conectar un proyecto"),
    Pagina("docs/tutorial-practico.md", "tutorial-practico.html", "Entender", "Tutorial práctico"),
    Pagina("docs/12-tareas.md", "12-tareas.html", "Herramientas", "El tracker de tareas"),
    Pagina("docs/14-sensor-prosa.md", "14-sensor-prosa.html", "Herramientas", "Un modelo como sensor"),
    Pagina("docs/mcp-contrato.md", "mcp-contrato.html", "Herramientas", "El servidor MCP"),
    Pagina("docs/mutacion-memoria.md", "mutacion-memoria.html", "Herramientas", "Memoria de la mutación"),
    Pagina("docs/reportar.md", "reportar.html", "Herramientas", "Reportar un límite"),
    Pagina("ESPECIFICACION.md", "especificacion.html", "Referencia", "Especificación"),
    Pagina("docs/decisiones/README.md", "decisiones/index.html", "Referencia", "Decisiones"),
    Pagina("NOTAS-DE-RELEASE.md", "notas.html", "Referencia", "Notas de release"),
    *(Pagina(f"docs/decisiones/{p.name}", f"decisiones/{p.stem}.html", "Decisiones",
             p.stem.replace("DECISION-", "").split("-", 1)[0])
      for p in sorted((DOCS / "decisiones").glob("DECISION-*.md"))),
)

_POR_ORIGEN = {(RAIZ / p.origen).resolve(): p for p in PAGINAS}


# ------------------------------------------------------------------------------ en línea

def slug(texto: str) -> str:
    """El ancla que GitHub le da a un título, para que los enlaces `#…` sigan valiendo."""
    t = re.sub(r"<[^>]+>", "", texto).strip().lower()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def _destino(dest: str, origen: Path, salida: Path) -> str:
    if re.match(r"^[a-z][a-z0-9+.-]*:", dest) or dest.startswith("#"):
        return dest
    ruta, _, ancla = dest.partition("#")
    if not ruta:
        return dest
    objetivo = (origen.parent / ruta).resolve()
    ancla = f"#{ancla}" if ancla else ""
    if objetivo in _POR_ORIGEN:
        destino = DOCS / _POR_ORIGEN[objetivo].salida
        return _relativa(destino, salida) + ancla
    try:
        relativa = objetivo.relative_to(RAIZ).as_posix()
    except ValueError:
        return dest
    tipo = "tree" if ruta.endswith("/") or objetivo.is_dir() else "blob"
    return f"{REPO}/{tipo}/main/{relativa}{ancla}"


def _relativa(destino: Path, desde: Path) -> str:
    partes_d, partes_o = destino.parts, desde.parent.parts
    comun = 0
    while comun < min(len(partes_d), len(partes_o)) and partes_d[comun] == partes_o[comun]:
        comun += 1
    return "/".join([".."] * (len(partes_o) - comun) + list(partes_d[comun:]))


def en_linea(texto: str, origen: Path, salida: Path) -> str:
    guardados: list[str] = []

    def guardar(fragmento: str) -> str:
        guardados.append(fragmento)
        return f"\x00{len(guardados) - 1}\x00"

    texto = re.sub(r"(`+)(.+?)\1",
                   lambda m: guardar(f"<code>{html.escape(m.group(2).strip())}</code>"), texto)
    texto = html.escape(texto, quote=False)

    def enlace(m: re.Match) -> str:
        imagen, etiqueta, dest = m.group(1), m.group(2), html.unescape(m.group(3))
        href = html.escape(_destino(dest, origen, salida))
        if imagen:
            return f'<span class="imagen-faltante">[imagen: {etiqueta}]</span>'
        externo = ' rel="noopener"' if href.startswith("http") else ""
        return f'<a href="{href}"{externo}>{etiqueta}</a>'

    texto = re.sub(r"(!?)\[([^\]]+)\]\(([^)\s]+)\)", enlace, texto)
    texto = re.sub(r"&lt;(https?://[^&\s]+)&gt;", r'<a href="\1" rel="noopener">\1</a>', texto)
    texto = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texto)
    texto = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", texto)
    texto = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", texto)
    return re.sub(r"\x00(\d+)\x00", lambda m: guardados[int(m.group(1))], texto)


# ------------------------------------------------------------------------------ código

_CLAVES_ORACLE = ("medida", "ninguno", "ninguno-requiere", "caso", "de", "donde", "sin", "unir",
                  "agrupar", "resumen", "umbral", "segun", "porque", "alcance", "ambito",
                  "requiere", "etiqueta", "evidencia", "defmacro", "sombra", "y", "o", "no")


def codigo(texto: str, lenguaje: str) -> str:
    cuerpo = html.escape(texto)
    if lenguaje in ("oracle", "caso"):
        cuerpo = re.sub(r"(&quot;.*?&quot;)", r'<span class="c-txt">\1</span>', cuerpo)
        patron = r"(?<![\w.-])(" + "|".join(map(re.escape, _CLAVES_ORACLE)) + r")(?![\w-])"
        partes = re.split(r'(<span class="c-txt">.*?</span>)', cuerpo)
        cuerpo = "".join(p if p.startswith("<span") else
                         re.sub(patron, r'<span class="c-kw">\1</span>', p) for p in partes)
    etiqueta = f' data-lenguaje="{html.escape(lenguaje)}"' if lenguaje else ""
    return f"<pre{etiqueta}><code>{cuerpo}</code></pre>"


# ------------------------------------------------------------------------------ bloques

_ITEM = re.compile(r"^( *)([-*+]|\d+[.)]) +(.*)$")
_FENCE = re.compile(r"^ *(`{3,}|~{3,})\s*([\w+-]*)")


def _es_separador_tabla(linea: str) -> bool:
    return bool(re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$", linea))


def _celdas(linea: str) -> list[str]:
    linea = linea.strip()
    if linea.startswith("|"):
        linea = linea[1:]
    if linea.endswith("|") and not linea.endswith("\\|"):
        linea = linea[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", linea)]


class Convertidor:
    def __init__(self, origen: Path, salida: Path):
        self.origen, self.salida = origen, salida
        self.indice: list[tuple[int, str, str]] = []
        self._ids: dict[str, int] = {}

    def linea(self, texto: str) -> str:
        return en_linea(texto, self.origen, self.salida)

    def _id(self, texto: str) -> str:
        base = slug(texto) or "seccion"
        n = self._ids.get(base, 0)
        self._ids[base] = n + 1
        return base if n == 0 else f"{base}-{n}"

    def bloques(self, lineas: list[str]) -> str:
        salida: list[str] = []
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            if not linea.strip():
                i += 1
                continue
            m = _FENCE.match(linea)
            if m:
                cerca = m.group(1)
                j = i + 1
                while j < len(lineas) and not lineas[j].strip().startswith(cerca):
                    j += 1
                sangria = len(linea) - len(linea.lstrip())
                cuerpo = "\n".join(l[sangria:] if l[:sangria].strip() == "" else l
                                   for l in lineas[i + 1:j])
                salida.append(codigo(cuerpo, m.group(2)))
                i = j + 1
                continue
            m = re.match(r"^(#{1,6}) +(.*?)\s*#*\s*$", linea)
            if m:
                nivel = len(m.group(1))
                contenido = self.linea(m.group(2))
                ident = self._id(contenido)
                if nivel in (2, 3):
                    self.indice.append((nivel, ident, re.sub(r"<[^>]+>", "", contenido)))
                salida.append(f'<h{nivel} id="{ident}">{contenido}'
                              f'<a class="ancla" href="#{ident}" aria-label="Enlace a esta sección">#</a>'
                              f'</h{nivel}>')
                i += 1
                continue
            if re.match(r"^ {0,3}([-*_])( *\1){2,}\s*$", linea):
                salida.append("<hr>")
                i += 1
                continue
            if "|" in linea and i + 1 < len(lineas) and _es_separador_tabla(lineas[i + 1]):
                encabezado = _celdas(linea)
                j = i + 2
                filas = []
                while j < len(lineas) and "|" in lineas[j] and lineas[j].strip():
                    filas.append(_celdas(lineas[j]))
                    j += 1
                cab = "".join(f"<th>{self.linea(c)}</th>" for c in encabezado)
                cuerpo = "".join("<tr>" + "".join(f"<td>{self.linea(c)}</td>" for c in f) + "</tr>"
                                 for f in filas)
                cab_html = f"<thead><tr>{cab}</tr></thead>" if any(encabezado) else ""
                salida.append(f'<div class="tabla"><table>{cab_html}<tbody>{cuerpo}</tbody></table></div>')
                i = j
                continue
            if linea.lstrip().startswith(">"):
                j = i
                citado = []
                while j < len(lineas) and lineas[j].lstrip().startswith(">"):
                    citado.append(re.sub(r"^\s*> ?", "", lineas[j]))
                    j += 1
                salida.append(f"<blockquote>{self.bloques(citado)}</blockquote>")
                i = j
                continue
            m = _ITEM.match(linea)
            if m:
                i = self._lista(lineas, i, salida)
                continue
            j = i
            parrafo = []
            while (j < len(lineas) and lineas[j].strip() and not _FENCE.match(lineas[j])
                   and not re.match(r"^#{1,6} ", lineas[j]) and not lineas[j].lstrip().startswith(">")
                   and not (j > i and _ITEM.match(lineas[j]))
                   and not ("|" in lineas[j] and j + 1 < len(lineas) and _es_separador_tabla(lineas[j + 1]))):
                parrafo.append(lineas[j].strip())
                j += 1
            salida.append(f"<p>{self.linea(' '.join(parrafo))}</p>")
            i = j
        return "\n".join(salida)

    def _lista(self, lineas: list[str], i: int, salida: list[str]) -> int:
        primero = _ITEM.match(lineas[i])
        base = len(primero.group(1))
        ordenada = primero.group(2)[0].isdigit()
        items: list[tuple[int, list[str]]] = []  # (sangría del contenido, líneas)
        suelta = False
        while i < len(lineas):
            linea = lineas[i]
            m = _ITEM.match(linea)
            if m and len(m.group(1)) == base and m.group(2)[0].isdigit() == ordenada:
                sangria = len(m.group(1)) + len(m.group(2)) + 1
                items.append((sangria, [" " * sangria + m.group(3)]))
            elif not linea.strip():
                siguiente = next((l for l in lineas[i + 1:] if l.strip()), "")
                indent = len(siguiente) - len(siguiente.lstrip())
                otro = _ITEM.match(siguiente)
                if not siguiente or (indent <= base and not (otro and len(otro.group(1)) == base)):
                    break
                suelta = suelta or (indent > base and not otro)
                items[-1][1].append("")
            elif len(linea) - len(linea.lstrip()) > base or not (
                    _ITEM.match(linea) or _FENCE.match(linea)
                    or linea.lstrip().startswith(("#", ">", "|"))):
                items[-1][1].append(linea)
            else:
                break
            i += 1
        partes = []
        for sangria, item in items:
            contenido = [l[sangria:] if l[:sangria].strip() == "" else l.lstrip() for l in item]
            cuerpo = self.bloques(contenido)
            if not suelta and cuerpo.startswith("<p>") and cuerpo.count("<p>") == 1:
                cuerpo = cuerpo.replace("<p>", "", 1).replace("</p>", "", 1)
            partes.append(f"<li>{cuerpo}</li>")
        etiqueta = "ol" if ordenada else "ul"
        salida.append(f"<{etiqueta}>{''.join(partes)}</{etiqueta}>")
        return i


# ------------------------------------------------------------------------------ página

def _titulo(texto: str) -> str:
    m = re.search(r"^# +(.+)$", texto, re.MULTILINE)
    return re.sub(r"[`*]", "", m.group(1)).strip() if m else "Oracle"


def _menu(actual: Pagina, salida: Path) -> str:
    grupos: dict[str, list[Pagina]] = {}
    for p in PAGINAS:
        if p.grupo != "Decisiones":
            grupos.setdefault(p.grupo, []).append(p)
    out = []
    for grupo, paginas in grupos.items():
        enlaces = "".join(
            f'<li><a href="{_relativa(DOCS / p.salida, salida)}"'
            f'{" aria-current=page" if p is actual else ""}>{html.escape(p.titulo)}</a></li>'
            for p in paginas)
        out.append(f'<p class="menu-grupo">{html.escape(grupo)}</p><ul>{enlaces}</ul>')
    return "".join(out)


def pagina(p: Pagina) -> str:
    origen = RAIZ / p.origen
    salida = DOCS / p.salida
    texto = origen.read_text(encoding="utf-8")
    conv = Convertidor(origen, salida)
    cuerpo = conv.bloques(texto.splitlines())
    titulo = _titulo(texto)
    raiz = _relativa(DOCS / "index.html", salida).removesuffix("index.html") or "./"
    indice = "".join(
        f'<li class="n{nivel}"><a href="#{ident}">{html.escape(t)}</a></li>'
        for nivel, ident, t in conv.indice)
    en_github = f"{REPO}/blob/main/{p.origen}"
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(titulo)} — Oracle</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=JetBrains+Mono:wght@400;600&family=Silkscreen&display=swap">
<link rel="stylesheet" href="{raiz}assets/sitio.css">
<link rel="icon" href="{raiz}assets/emblema.svg" type="image/svg+xml">
</head>
<body class="doc">
<a class="saltar" href="#contenido">Saltar al contenido</a>
<header class="barra">
  <a class="marca" href="{raiz}"><img src="{raiz}assets/emblema.svg" alt="" width="28" height="28"> oracle</a>
  <nav aria-label="Principal">
    <a href="{raiz}por-que.html">Por qué</a>
    <a href="{raiz}documentacion.html">Documentación</a>
    <a href="{raiz}manual.html">Manual</a>
    <a href="{REPO}" rel="noopener">GitHub</a>
  </nav>
</header>
<div class="doc-rejilla">
  <details class="menu" open>
    <summary>Documentación</summary>
    <nav aria-label="Documentación">{_menu(p, salida)}</nav>
  </details>
  <main id="contenido" class="prosa">
{cuerpo}
    <p class="fuente">Esta página se genera desde <a href="{en_github}" rel="noopener">{html.escape(p.origen)}</a>.</p>
  </main>
  <aside class="en-esta-pagina" aria-label="En esta página">
    {"<p class='menu-grupo'>En esta página</p><ul>" + indice + "</ul>" if indice else ""}
  </aside>
</div>
<script>if (matchMedia("(max-width: 760px)").matches) document.querySelector(".menu").removeAttribute("open");</script>
</body>
</html>
"""


def main(argv: list[str]) -> int:
    escribir = "--escribir" in argv
    vencidas = []
    for p in PAGINAS:
        destino = DOCS / p.salida
        nuevo = pagina(p)
        actual = destino.read_text(encoding="utf-8") if destino.exists() else None
        if actual == nuevo:
            continue
        if escribir:
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(nuevo, encoding="utf-8")
            print(f"escrita {destino.relative_to(RAIZ)}")
        else:
            vencidas.append(p.salida)
    if vencidas:
        print("páginas del sitio vencidas: " + ", ".join(vencidas)
              + "\nregeneralas con `python tools/sitio.py --escribir`")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
