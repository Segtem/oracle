"""Vuelca todo el repositorio a Markdown plano y autocontenido, para subirlo y estudiarlo.

    python tools/estudio.py [--proyecto <ruta>] [--destino estudio]

Pensado para NotebookLM y parientes: ingieren **documentos planos**, no repositorios. Así que acá no
hay enlaces relativos, ni wikilinks, ni referencias a archivos que el lector no tiene. Cada documento
se explica solo.

Tres cosas que no son «copiar y pegar», y son la razón de que esto sea un generador y no una carpeta
mantenida a mano:

  1. **el catálogo y el corpus son JSON**, y crudos se leen mal. Acá salen como prosa y tablas, con la
     medida expandida a su forma canónica al lado de cómo está escrita.
  2. **los mensajes de commit tienen buena parte del «por qué»** — las correcciones, los mutantes que
     sobrevivieron, lo que se descubrió a mitad de camino. Si sólo se suben los documentos, se pierde
     justo lo que más sirve para entender por qué las cosas son como son.
  3. **los docstrings del núcleo tienen el razonamiento**, no el código. Van enteros.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos  # noqa: F401,E402
from nucleo.medida import Medida, cargar_catalogo, como_hechos  # noqa: E402
from nucleo.proyecto import resolver  # noqa: E402


def _git(*args) -> str:
    r = subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def _compacto(m: list) -> str:
    """Un elemento por línea arriba, las expresiones anidadas en una línea. `indent=1` explota los
    arreglos y vuelve ilegible justo lo que hay que leer."""
    return "[\n" + ",\n".join("  " + json.dumps(x, ensure_ascii=False) for x in m) + "\n]"


def _docstring(ruta: Path) -> str:
    try:
        return ast.get_docstring(ast.parse(ruta.read_text(encoding="utf-8"))) or ""
    except SyntaxError:
        return ""


# ---------------------------------------------------------------- documentos

def esencia() -> str:
    """El README, tal cual: ya es autocontenido y no tiene enlaces que se rompan al sacarlo."""
    texto = (RAIZ / "README.md").read_text(encoding="utf-8")
    # los enlaces a archivos del repo no significan nada fuera de él
    import re
    texto = re.sub(r"\[([^\]]+)\]\((?!http)[^)]+\)", r"\1", texto)
    return "# oracle — qué es y por qué\n\n" + texto.split("\n", 1)[1]


def algebra() -> str:
    return (RAIZ / "ESPECIFICACION.md").read_text(encoding="utf-8")


def como_escribir() -> str:
    import re
    t = (RAIZ / "ESCRIBIR-UNA-MEDIDA.md").read_text(encoding="utf-8")
    return re.sub(r"\[([^\]]+)\]\((?!http)[^)]+\)", r"\1", t)


def catalogo_en_prosa(catalogos_dirs) -> str:
    cat = cargar_catalogo(catalogos_dirs)
    hechos = {h["id"]: h for h in como_hechos(cat.values())}
    fuentes = {}
    for d in catalogos_dirs:
        for p in Path(d).rglob("*.json"):
            crudo = json.loads(p.read_text(encoding="utf-8"))
            fuentes[crudo[1]] = crudo

    out = ["# El catálogo de medidas", "",
           "Cada medida es un **archivo de datos**, no código. Se muestran las dos formas: cómo está",
           "escrita (a veces con una macro) y en qué se expande. Y los dos campos que este lenguaje",
           "exige y ningún otro verificador pide: **la defensa del umbral** y **el punto ciego**.", ""]

    por_dominio: dict[str, list] = {}
    for mid, m in sorted(cat.items()):
        por_dominio.setdefault(mid.split(".")[0], []).append((mid, m))

    for dominio, medidas in sorted(por_dominio.items()):
        h0 = hechos[medidas[0][0]]
        que = "el LENGUAJE mismo" if h0["es_meta_por_lo_que_mide"] else "el mundo"
        out += [f"## Dominio `{dominio}` — mide {que}", ""]
        for mid, m in medidas:
            h = hechos[mid]
            out += [f"### {mid}", "",
                    f"- **mide sobre** la relación `{h['relacion']}`",
                    f"- **umbral**: `{m.op} {m.limite}`",
                    f"- **por qué ese número**: {m.porque}",
                    f"- **qué NO ve**: {m.alcance}", "",
                    "Como está escrita:", "", "```json",
                    _compacto(fuentes.get(mid, m.a_datos())), "```", ""]
            if fuentes.get(mid, [""])[0] != "medida":
                out += ["En qué se expande:", "", "```json",
                        _compacto(m.a_datos()), "```", ""]
    return "\n".join(out)


def corpus_en_prosa() -> str:
    casos = [json.loads(p.read_text(encoding="utf-8"))
             for p in sorted((RAIZ / "corpus").rglob("*.json"))]
    et = Counter(c["etiqueta"] for c in casos)
    det = Counter(c["como_se_detecto"] for c in casos)

    out = ["# El corpus: los casos donde la medición dijo bien y no estaba bien", "",
           "Son datos, no anécdotas: cada caso trae su evidencia en forma de relaciones, así que se",
           "puede volver a juzgar. El corpus es el **criterio de aceptación** del resto: cuando hay",
           "medidas, cada caso de defecto tiene que ponerse rojo y cada caso correcto, verde.", "",
           "## Los números", "",
           "| Etiqueta | Cuántos |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in et.most_common()]
    out += ["", "| Cómo se detectó | Cuántos |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in det.most_common()]
    out += ["",
            "**Ninguno lo atrapó un verificador propio en el momento en que ocurrió.** Ésa es la",
            "medición que justifica el repositorio entero.", ""]

    for c in casos:
        out += [f"## {c['id']}", "", f"**{c['titulo']}**", "",
                f"- etiqueta: `{c['etiqueta']}` · se detectó por: `{c['como_se_detecto']}`",
                f"- medida que lo atrapa: `{c['medida'] or 'ninguna todavía'}`",
                f"- de dónde salió: {c['origen'].get('repo', '?')} · {c['origen'].get('commit', '?')}",
                "", f"**Qué pasó.** {c['sintoma']}", "", f"**Qué se aprendió.** {c['leccion']}", ""]
        if c.get("sin_medida_todavia"):
            out += [f"**Por qué no hay medida todavía.** {c['sin_medida_todavia']}", ""]
        if c.get("resuelto"):
            out += [f"**Resuelto.** {c['resuelto']}", ""]
        ev = "\n".join(f'  "{rel}": ' + json.dumps(filas, ensure_ascii=False)[:1200]
                       for rel, filas in c["evidencia"].items())
        out += ["La evidencia, como relaciones:", "", "```json", "{", ev, "}", "```", ""]
    return "\n".join(out)


def modulos(carpeta: str, titulo: str, intro: str) -> str:
    out = [f"# {titulo}", "", intro, ""]
    for p in sorted((RAIZ / carpeta).glob("*.py")):
        if p.name == "__init__.py":
            continue
        doc = _docstring(p)
        if not doc:
            continue
        out += [f"## `{carpeta}/{p.name}`", "",
                f"*{len(p.read_text(encoding='utf-8').splitlines())} líneas*", "", doc, ""]
    return "\n".join(out)


def diario() -> str:
    out = ["# El diario: por qué las cosas son como son", "",
           "Los mensajes de commit, del más viejo al más nuevo. Acá vive buena parte del",
           "razonamiento —y casi todas las correcciones—: qué se intentó, qué salió mal, qué mutante",
           "sobrevivió, qué afirmación hubo que retirar. Leído en orden, es la historia de un autor",
           "equivocándose y siendo atrapado por lo que estaba construyendo.", ""]
    crudo = _git("log", "--reverse", "--format=%H%x1f%ad%x1f%s%x1f%b%x1e", "--date=short")
    for entrada in crudo.split("\x1e"):
        if not entrada.strip():
            continue
        sha, fecha, titulo, cuerpo = (entrada.strip().split("\x1f") + ["", "", "", ""])[:4]
        out += [f"## {fecha} — {titulo}", "", f"*commit {sha[:7]}*", "", cuerpo.strip(), ""]
    return "\n".join(out)


def numeros(catalogos_dirs) -> str:
    cat = cargar_catalogo(catalogos_dirs)
    hechos = como_hechos(cat.values())
    lineas_nucleo = sum(len(p.read_text(encoding="utf-8").splitlines())
                        for p in (RAIZ / "nucleo").glob("*.py"))
    lineas_catalogo = sum(len(p.read_text(encoding="utf-8").splitlines())
                          for d in catalogos_dirs for p in Path(d).rglob("*.json"))
    negativas = sum(p.read_text(encoding="utf-8").count("raise ")
                    for p in (RAIZ / "nucleo").glob("*.py"))
    casos = list((RAIZ / "corpus").rglob("*.json"))
    return "\n".join([
        "# Los números, y qué dicen", "",
        "| Qué | Cuánto | Qué dice |", "|---|---|---|",
        f"| líneas del núcleo | {lineas_nucleo} | el lenguaje |",
        f"| líneas de medidas escritas en él | {lineas_catalogo} | lo escrito en el lenguaje |",
        f"| proporción | {lineas_nucleo / max(lineas_catalogo, 1):.0f} a 1 | la apuesta: que el "
        "segundo crezca y el primero no |",
        f"| (contando sólo el catálogo base) | {lineas_nucleo / max(sum(len(x.read_text(encoding='utf-8').splitlines()) for x in (RAIZ / 'catalogos').rglob('*.json')), 1):.0f} a 1 | "
        "sin ningún proyecto que lo use |",
        f"| negativas en el núcleo (`raise`) | {negativas} | su naturaleza es rechazar, no medir |",
        f"| medidas | {len(cat)} | de las cuales "
        f"{sum(1 for h in hechos if h['es_meta_por_lo_que_mide'])} miden el lenguaje mismo |",
        f"| casos de corpus | {len(casos)} | fallas reales, con su evidencia |",
        f"| commits | {len(_git('log', '--format=%H').splitlines())} | cerca de la mitad corrigen "
        "una afirmación propia |",
        "",
        "Si en seis meses la proporción no se movió, el lenguaje no valió la pena. Es la única",
        "métrica del proyecto que no se puede sastrear escribiendo más medidas.", ""])


def indice(archivos) -> str:
    return "\n".join([
        "# oracle — paquete de estudio", "",
        "Documentos planos y autocontenidos, generados por `tools/estudio.py`. Sin enlaces relativos",
        "ni referencias a archivos que no estén acá: cada uno se lee solo.", "",
        "| Documento | De qué trata |", "|---|---|",
        "| `00-esencia.md` | qué es, su naturaleza, y el norte |",
        "| `01-el-algebra.md` | la especificación: hechos, medidas como dato, operadores, clausura |",
        "| `02-escribir-una-medida.md` | cómo se escribe una, y qué NO puede decirte la herramienta |",
        "| `03-el-catalogo.md` | cada medida, con su defensa y su punto ciego, en las dos formas |",
        "| `04-el-corpus.md` | cada caso donde la medición dijo bien y no estaba bien |",
        "| `05-el-nucleo.md` | el razonamiento de cada módulo (los docstrings, enteros) |",
        "| `06-las-herramientas.md` | qué hace cada instrumento y por qué existe |",
        "| `07-el-diario.md` | los mensajes de commit: dónde vive el «por qué» |",
        "| `08-los-numeros.md` | lo medido, y qué dice cada número |",
        "",
        "## Por dónde empezar", "",
        "`00` y `08` dan el marco en diez minutos. `04` es lo más concreto: son fallas reales.",
        "`07` es el más largo y el más revelador — leído en orden muestra el proceso, no el",
        "resultado.", "",
        f"*Generado el {subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True).stdout.strip()}"
        f" · {len(archivos)} documentos.*", ""])


def main() -> int:
    argv = sys.argv[1:]
    destino = RAIZ / (argv[argv.index("--destino") + 1] if "--destino" in argv else "estudio")
    proy = resolver(argv)
    dirs = [RAIZ / "catalogos"]
    if not proy.es_el_propio_oracle:
        dirs.append(proy.catalogos)

    destino.mkdir(parents=True, exist_ok=True)
    docs = {
        "00-esencia.md": esencia(),
        "01-el-algebra.md": algebra(),
        "02-escribir-una-medida.md": como_escribir(),
        "03-el-catalogo.md": catalogo_en_prosa(dirs),
        "04-el-corpus.md": corpus_en_prosa(),
        "05-el-nucleo.md": modulos(
            "nucleo", "El núcleo, módulo por módulo",
            "Los docstrings enteros: ahí vive el razonamiento y las decisiones descartadas, que es lo "
            "que no se puede reconstruir leyendo el código."),
        "06-las-herramientas.md": modulos(
            "tools", "Las herramientas",
            "Cada una existe por un motivo que está escrito en su encabezado. Varias nacieron de un "
            "defecto concreto del corpus."),
        "07-el-diario.md": diario(),
        "08-los-numeros.md": numeros(dirs),
    }
    docs["README.md"] = indice(docs)

    for nombre, texto in docs.items():
        (destino / nombre).write_text(texto.rstrip() + "\n", encoding="utf-8")

    total = sum(len(t.splitlines()) for t in docs.values())
    print(f"{len(docs)} documentos · {total} líneas · {destino}")
    for nombre in sorted(docs):
        print(f"  {nombre:<28} {len(docs[nombre].splitlines()):>5} líneas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
