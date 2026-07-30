"""Verificador del corpus — la primera regla del repositorio, y se aplica a sí mismo.

    python tools/corpus.py            → verifica (sale != 0 si algo está mal)
    python tools/corpus.py --resumen  → verifica y además cuenta qué mecanismo atrapa qué

Comprueba lo que se degrada solo:

  1. **el esquema** de cada caso, y que el `id` sea el nombre del archivo;
  2. **la forma de la evidencia**: un mapa de relación → filas de campos ESCALARES. Es el contrato
     L0 de la especificación, y si se afloja acá se afloja en todo el resto;
  3. **que ningún caso se caiga en silencio**: si un caso todavía no tiene medida que lo atrape,
     tiene que decir POR QUÉ en `sin_medida_todavia`. Un caso sin medida y sin explicación es un caso
     que alguien va a borrar.

La 3 es la que importa. Los casos incómodos —los que el marco todavía no puede medir— son
justamente los que no hay que perder: son la lista de lo que falta.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "corpus"

OBLIGATORIOS = ("id", "fecha", "origen", "titulo", "etiqueta", "sintoma",
                "como_se_detecto", "medida", "evidencia", "leccion")

ETIQUETAS = {
    "falso_verde",                        # dijo bien y estaba mal
    "falso_rojo",                         # dijo mal y estaba bien
    "deuda_de_diseño",                    # el lenguaje obliga a algo que se va a romper
    "medida_correcta_conclusion_errada",   # el número era cierto, la causa atribuida no
    # La OTRA polaridad: evidencia real donde la medida debe decir verde. Sin estos casos una
    # medida queda floja — `quitar_filtro` sobrevive siempre, porque contar sin filtro sólo da
    # verde con la relación vacía. Es lo mismo que evaluar un clasificador sólo con positivos.
    "verde_correcto",
}

# De dónde vino la detección. Sirve para saber qué mecanismo se paga solo y cuál es decorativo.
DETECCIONES = {
    "mutacion",           # se rompió el código a propósito
    "persona",            # alguien lo vio
    "accidente",          # apareció haciendo otra cosa
    "herramienta_ajena",  # lo detectó algo que no era nuestro verificador
    "observacion",        # no hubo defecto: se observó un verde correcto
}

ESCALARES = (str, int, float, bool, type(None))


def casos() -> list[Path]:
    return sorted(RAIZ.rglob("*.json"))


def revisar_evidencia(nombre: str, evidencia) -> list[str]:
    """L0: relación → filas planas. Sin objetos anidados, sin listas dentro de un campo."""
    fallas = []
    if not isinstance(evidencia, dict) or not evidencia:
        return [f"{nombre}: `evidencia` tiene que ser un mapa de relación → filas, y no estar vacío"]
    for relacion, filas in evidencia.items():
        if not isinstance(filas, list) or not filas:
            fallas.append(f"{nombre}: la relación «{relacion}» no es una lista de filas con contenido")
            continue
        for i, fila in enumerate(filas):
            if not isinstance(fila, dict):
                fallas.append(f"{nombre}: {relacion}[{i}] no es un hecho (un mapa de campos)")
                continue
            for campo, valor in fila.items():
                if not isinstance(valor, ESCALARES):
                    fallas.append(f"{nombre}: {relacion}[{i}].{campo} no es escalar "
                                  f"({type(valor).__name__}) — L0 no admite anidamiento")
    return fallas


def verificar() -> tuple[list[str], list[dict]]:
    fallas: list[str] = []
    cargados: list[dict] = []
    vistos: dict[str, Path] = {}

    for p in casos():
        try:
            c = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fallas.append(f"{p.name}: JSON inválido — {e}")
            continue

        faltan = [k for k in OBLIGATORIOS if k not in c]
        if faltan:
            fallas.append(f"{p.name}: le faltan los campos {faltan}")
            continue

        if c["id"] != p.stem:
            fallas.append(f"{p.name}: el `id` dice «{c['id']}» y el archivo se llama «{p.stem}»")
        if c["id"] in vistos:
            fallas.append(f"{p.name}: el id «{c['id']}» ya está en {vistos[c['id']].name}")
        vistos[c["id"]] = p

        if c["etiqueta"] not in ETIQUETAS:
            fallas.append(f"{p.name}: etiqueta «{c['etiqueta']}» no está en {sorted(ETIQUETAS)}")
        if c["como_se_detecto"] not in DETECCIONES:
            fallas.append(f"{p.name}: como_se_detecto «{c['como_se_detecto']}» "
                          f"no está en {sorted(DETECCIONES)}")

        # un caso sin medida es información valiosa, pero tiene que decir por qué
        if not c["medida"] and not str(c.get("sin_medida_todavia", "")).strip():
            fallas.append(f"{p.name}: `medida` es nula y no hay `sin_medida_todavia` que lo explique")

        fallas += revisar_evidencia(p.name, c["evidencia"])
        cargados.append(c)

    return fallas, cargados


def resumen(cargados: list[dict]) -> None:
    print(f"\ncasos: {len(cargados)}")
    for titulo, clave in (("por etiqueta", "etiqueta"), ("por cómo se detectó", "como_se_detecto")):
        print(f"\n{titulo}:")
        for k, n in Counter(c[clave] for c in cargados).most_common():
            print(f"  {n:2}  {k}")
    sin = [c["id"] for c in cargados if not c["medida"]]
    print(f"\nsin medida que los atrape ({len(sin)}) — la lista de lo que falta:")
    for s in sin:
        print("  ·", s)
    print("\nmedidas que el corpus reclama:")
    for k, n in Counter(c["medida"] for c in cargados if c["medida"]).most_common():
        print(f"  {n:2}  {k}")


def main() -> int:
    fallas, cargados = verificar()
    if fallas:
        print(f"CORPUS: {len(fallas)} problema(s)")
        for f in fallas:
            print("  ·", f)
        return 1
    print(f"CORPUS OK · {len(cargados)} casos · esquema, evidencia L0 y trazabilidad en regla")
    if "--resumen" in sys.argv:
        resumen(cargados)
    return 0


if __name__ == "__main__":
    sys.exit(main())
