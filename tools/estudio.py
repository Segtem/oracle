"""Vuelca todo el repositorio a Markdown plano y autocontenido, para subirlo y estudiarlo.

    python tools/estudio.py [--proyecto <ruta>] [--destino estudio] [--confiar-escalares]
    python tools/estudio.py --archivo ORACLE-PARA-NOTEBOOKLM.md

Pensado para NotebookLM y parientes: ingieren **documentos planos**, no repositorios. Así que acá no
hay enlaces relativos, ni wikilinks, ni referencias a archivos que el lector no tiene. Cada documento
se explica solo.

Tres cosas que no son «copiar y pegar», y son la razón de que esto sea un generador y no una carpeta
mantenida a mano:

  1. **el catálogo y el corpus son datos**, y crudos se leen mal. Acá salen como prosa y tablas, con
     la medida expandida a su forma canónica al lado de cómo está escrita.
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
from nucleo.caso import cargar_casos, rutas_de_corpus  # noqa: E402
from nucleo.medida import (Medida, cargar_catalogo, cargar_fuente_medida, como_hechos,  # noqa: E402
                           rutas_de_catalogo)
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables, catalogos_a_cargar,
                             confiar_escalares, escalares_del_proyecto,
                             macros_del_proyecto, problemas_estructura)  # noqa: E402
from tools.sesion import resolver_cli  # noqa: E402


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


def catalogo_en_prosa(catalogos_dirs, macros=None) -> str:
    cat = cargar_catalogo(catalogos_dirs, macros=macros)
    hechos = {h["id"]: h for h in como_hechos(cat.values())}
    fuentes = {}
    for p in rutas_de_catalogo(catalogos_dirs):
        crudo = cargar_fuente_medida(p)
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


def corpus_en_prosa(raiz_corpus: Path) -> str:
    casos = cargar_casos(raiz_corpus)
    et = Counter(c["etiqueta"] for c in casos)
    det = Counter(c["como_se_detecto"] for c in casos)
    proc = Counter(c.get("procedencia", "sin_declarar") for c in casos)

    out = ["# El corpus: los casos donde la medición dijo bien y no estaba bien", "",
           "Son datos, no anécdotas: cada caso trae su evidencia en forma de relaciones, así que se",
           "puede volver a juzgar. El corpus es el **criterio de aceptación** del resto: cuando hay",
           "medidas, cada caso de defecto tiene que ponerse rojo y cada caso correcto, verde.", "",
           "## Los números", "",
           "| Etiqueta | Cuántos |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in et.most_common()]
    out += ["", "| Cómo se detectó | Cuántos |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in det.most_common()]
    out += ["", "| Procedencia | Cuántos |", "|---|---|"]
    out += [f"| {k} | {v} |" for k, v in proc.most_common()]
    out += ["",
            "**Cada caso registra cómo se detectó.** Una suite verde y una mutación, una persona o",
            "un accidente son señales distintas; mezclarlas borraría justo la evidencia que el",
            "corpus intenta conservar.", ""]

    for c in casos:
        out += [f"## {c['id']}", "", f"**{c['titulo']}**", "",
                f"- etiqueta: `{c['etiqueta']}` · se detectó por: `{c['como_se_detecto']}`",
                f"- procedencia: `{c.get('procedencia', 'sin_declarar')}`",
                f"- medida que lo atrapa: `{c['medida'] or 'ninguna todavía'}`",
                f"- de dónde salió: {c['origen'].get('repo', '?')} · {c['origen'].get('commit', '?')}",
                "", f"**Qué pasó.** {c['sintoma']}", "", f"**Qué se aprendió.** {c['leccion']}", ""]
        if c.get("sin_medida_todavia"):
            out += [f"**Por qué no hay medida todavía.** {c['sin_medida_todavia']}", ""]
        if c.get("resuelto"):
            out += [f"**Resuelto.** {c['resuelto']}", ""]
        if c.get("limite_humano"):
            out += [f"**Límite humano.** {c['limite_humano']}", ""]
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


def numeros(catalogos_dirs, raiz_corpus: Path, macros=None) -> str:
    cat = cargar_catalogo(catalogos_dirs, macros=macros)
    hechos = como_hechos(cat.values())
    lineas_nucleo = sum(len(p.read_text(encoding="utf-8").splitlines())
                        for p in (RAIZ / "nucleo").glob("*.py"))
    lineas_catalogo = sum(len(p.read_text(encoding="utf-8").splitlines())
                          for p in rutas_de_catalogo(catalogos_dirs))
    negativas = sum(p.read_text(encoding="utf-8").count("raise ")
                    for p in (RAIZ / "nucleo").glob("*.py"))
    casos = rutas_de_corpus(raiz_corpus)
    return "\n".join([
        "# Los números, y qué dicen", "",
        "| Qué | Cuánto | Qué dice |", "|---|---|---|",
        f"| líneas del núcleo | {lineas_nucleo} | el lenguaje |",
        f"| líneas de medidas escritas en él | {lineas_catalogo} | lo escrito en el lenguaje |",
        f"| proporción | {lineas_nucleo / max(lineas_catalogo, 1):.0f} a 1 | la apuesta: que el "
        "segundo crezca y el primero no |",
        f"| (contando sólo el catálogo base) | {lineas_nucleo / max(sum(len(x.read_text(encoding='utf-8').splitlines()) for x in rutas_de_catalogo(RAIZ / 'catalogos')), 1):.0f} a 1 | "
        "sin ningún proyecto que lo use |",
        f"| negativas en el núcleo (`raise`) | {negativas} | su naturaleza es rechazar, no medir |",
        f"| medidas | {len(cat)} | de las cuales "
        f"{sum(1 for h in hechos if h['es_meta_por_lo_que_mide'])} miden el lenguaje mismo |",
        f"| casos de corpus | {len(casos)} | fallas reales, con su evidencia |",
        # Acá decía «cerca de la mitad corrigen una afirmación propia». Era un juicio del autor sin
        # ningún respaldo mecánico, replicado desde el README. Se retiró de los dos lados: el conteo
        # de commits es un hecho, la interpretación no lo era.
        f"| commits | {len(_git('log', '--format=%H').splitlines())} | el historial completo |",
        "",
        # Acá decía «si en seis meses la proporción no se movió, el lenguaje no valió la pena».
        # Se retiró el 2026-08-24 junto con la puerta de abandono: era una afirmación de producto
        # en un proyecto EXPERIMENTAL, y tratar una cifra de costo como veredicto fue lo que llevó
        # a las auditorías a medirlo con una vara que el proyecto no había ganado todavía.
        "**Estado: EXPERIMENTAL**, y el destino declarado es un metalenguaje. No hay fecha de corte",
        "ni condición de cierre. La proporción de arriba es una cifra sobre el COSTO, no un",
        "veredicto: es la única que no se puede sastrear escribiendo más medidas, y eso la hace",
        "útil para mirar, no para dictaminar.", ""])


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


def _documentos(proy) -> dict[str, str]:
    dirs = catalogos_a_cargar(proy)
    macros = macros_del_proyecto(proy)
    docs = {
        "00-esencia.md": esencia(),
        "01-el-algebra.md": algebra(),
        "02-escribir-una-medida.md": como_escribir(),
        "03-el-catalogo.md": catalogo_en_prosa(dirs, macros),
        "04-el-corpus.md": corpus_en_prosa(proy.corpus),
        "05-el-nucleo.md": modulos(
            "nucleo", "El núcleo, módulo por módulo",
            "Los docstrings enteros: ahí vive el razonamiento y las decisiones descartadas, que es lo "
            "que no se puede reconstruir leyendo el código."),
        "06-las-herramientas.md": modulos(
            "tools", "Las herramientas",
            "Cada una existe por un motivo que está escrito en su encabezado. Varias nacieron de un "
            "defecto concreto del corpus."),
        "07-el-diario.md": diario(),
        "08-los-numeros.md": numeros(dirs, proy.corpus, macros),
    }
    docs["README.md"] = indice(docs)
    return docs


def _bajar_titulos(texto: str) -> str:
    """Anida un Markdown sin tocar comentarios o ejemplos dentro de bloques de código."""
    salida = []
    en_bloque = False
    for linea in texto.splitlines():
        if linea.lstrip().startswith("```"):
            en_bloque = not en_bloque
        if not en_bloque and linea.startswith("#"):
            linea = "#" + linea
        salida.append(linea)
    return "\n".join(salida)


def documento_unico(docs: dict[str, str], *, extras=None) -> str:
    """Compone el paquete de estudio en una única fuente autocontenida para NotebookLM."""
    if extras is None:
        # Se declaran acá, y un archivo declarado que no está es un ERROR y no un salto: si faltara
        # en silencio, sacar un documento del paquete de estudio sería tan barato como borrarlo.
        # `AUDITORIA-2026-07-30.md` salió de esta lista el 2026-08-24 porque el archivo se movió
        # fuera del repositorio, a `~/Dev/auditorias/oracle/`, y dejó la referencia colgando.
        # `COMPROMISOS.json` salió el mismo día: la puerta de abandono se retiró entera al declarar
        # el proyecto EXPERIMENTAL, y un experimento no se gobierna con plazos.
        declarados = (
            ("09-decision-relaciones-como-bolsas.md", "DECISION-001-RELACIONES-COMO-BOLSAS.md"),
            ("10-decision-sin-composicion.md", "DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md"),
            ("11-decision-sin-parametros-opcionales.md",
             "DECISION-003-SIN-PARAMETROS-OPCIONALES-EN-DEFMACRO.md"),
            ("12-plan-de-correccion.md", "PLAN-CORRECCION.md"),
        )
        faltan = [origen for _n, origen in declarados if not (RAIZ / origen).exists()]
        if faltan:
            raise FileNotFoundError(
                f"el paquete de estudio declara documentos que no están: {faltan}")
        extras = tuple(
            (nombre, (RAIZ / origen).read_text(encoding="utf-8"))
            for nombre, origen in declarados)
    partes = [
        (nombre, texto) for nombre, texto in sorted(docs.items())
        if nombre != "README.md"
    ]
    partes.extend(extras)
    fecha = subprocess.run(
        ["date", "+%Y-%m-%d"], capture_output=True, text=True).stdout.strip()
    commit = _git("rev-parse", "--short=12", "HEAD").strip() or "desconocido"
    salida = [
        "# Oracle — documento integral para NotebookLM",
        "",
        "Fuente única de estudio del metalenguaje Oracle: propósito, semántica, autoría, catálogo,",
        "corpus, arquitectura, herramientas, historia, decisiones, auditoría y plan de corrección.",
        "",
        f"- Generado: `{fecha}`",
        f"- Revisión de código base: `{commit}`",
        f"- Partes incluidas: `{len(partes)}`",
        "",
        "> Nota de lectura: la auditoría y el plan conservan cifras y hallazgos históricos para",
        "> explicar cómo evolucionó Oracle. Cuando una cifra histórica difiera del estado actual,",
        "> prevalecen «Los números» y «Estado» de las primeras partes, generados desde el checkout",
        "> vigente.",
        "",
        "## Orden sugerido",
        "",
        "Leé primero la esencia, el álgebra y los números. Después recorré el catálogo y el corpus;",
        "son la teoría puesta a prueba. El diario, la auditoría y el plan explican las alternativas",
        "descartadas, los defectos encontrados y las fronteras que todavía no puede cerrar el código.",
    ]
    for nombre, texto in partes:
        salida.extend((
            "",
            "---",
            "",
            f"<!-- fuente: {nombre} -->",
            "",
            _bajar_titulos(texto.rstrip()),
        ))
    return "\n".join(salida).rstrip() + "\n"


def _ejecutar(proy, destino: Path) -> int:
    docs = _documentos(proy)
    destino.mkdir(parents=True, exist_ok=True)

    for nombre, texto in docs.items():
        (destino / nombre).write_text(texto.rstrip() + "\n", encoding="utf-8")

    total = sum(len(t.splitlines()) for t in docs.values())
    print(f"{len(docs)} documentos · {total} líneas · {destino}")
    for nombre in sorted(docs):
        print(f"  {nombre:<28} {len(docs[nombre].splitlines()):>5} líneas")
    return 0


def _ejecutar_archivo(proy, destino: Path) -> int:
    if destino.suffix.lower() != ".md":
        print("--archivo debe terminar en .md")
        return 1
    texto = documento_unico(_documentos(proy))
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    print(f"DOCUMENTO INTEGRAL · {len(texto.splitlines())} líneas · {destino}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    proy = resolver_cli(argv)
    if proy is None:
        return 1
    estructura = problemas_estructura(proy, ("catalogos", "corpus"))
    if estructura:
        print("PROYECTO INVÁLIDO — " + "; ".join(estructura))
        return 1
    if "--destino" in argv and "--archivo" in argv:
        print("usá --destino para el paquete o --archivo para un solo Markdown, no ambos")
        return 1
    if "--archivo" in argv:
        i = argv.index("--archivo")
        if i + 1 >= len(argv):
            print("--archivo necesita una ruta .md")
            return 1
        indicado = Path(argv[i + 1]).expanduser()
        archivo = indicado if indicado.is_absolute() else proy.raiz / indicado
    elif "--destino" in argv:
        i = argv.index("--destino")
        if i + 1 >= len(argv):
            print("--destino necesita una ruta")
            return 1
        indicado = Path(argv[i + 1]).expanduser()
        destino = indicado if indicado.is_absolute() else proy.raiz / indicado
    else:
        destino = proy.raiz / "estudio"
    try:
        with escalares_del_proyecto(proy, confiar=confiar_escalares(argv)):
            if "--archivo" in argv:
                return _ejecutar_archivo(proy, archivo)
            return _ejecutar(proy, destino)
    except (EscalaresNoConfiables, EscalaresInvalidas) as e:
        print(f"ESCALARES EXTERNAS NO EJECUTADAS — {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
