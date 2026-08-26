"""Verificador del corpus — la primera regla del repositorio, y se aplica a sí mismo.

    python tools/corpus.py            → verifica (sale != 0 si algo está mal)
    python tools/corpus.py --resumen  → verifica y además cuenta qué mecanismo atrapa qué
    python tools/corpus.py --nuevo meta/999-caso-nuevo
                                      → crea un caso nuevo en superficie

Comprueba lo que se degrada solo:

  1. **el esquema** de cada caso, y que el `id` sea el nombre del archivo;
  2. **la forma de la evidencia**: un mapa de relación → filas de campos ESCALARES. Es el contrato
     L0 de la especificación, y si se afloja acá se afloja en todo el resto;
  3. **que ningún caso se caiga en silencio**: un caso sin medida declara si sigue abierto, quedó
     resuelto por construcción o documenta un límite humano no automatizable.

La 3 es la que importa. Los casos incómodos —los que el marco todavía no puede medir— son
justamente los que no hay que perder: son la lista de lo que falta.
"""

from __future__ import annotations

import sys
import re
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from nucleo.algebra import ErrorDeAlgebra, separar_clave  # noqa: E402
from nucleo.caso import (DETECCIONES, ETIQUETAS, CasoMalDeclarado,
                         cargar_fuente_caso, rutas_de_corpus)  # noqa: E402
from nucleo.proyecto import (ID_CASO_RE, ProyectoInvalido, presentar_ruta,
                             problemas_estructura, sin_bandera)  # noqa: E402
from tools.sesion import resolver_cli  # noqa: E402

OBLIGATORIOS = ("id", "fecha", "origen", "titulo", "etiqueta", "sintoma",
                "como_se_detecto", "medida", "evidencia", "leccion")
GRUPO_CASO_RE = re.compile(r"^[a-z][a-z0-9_-]*$")

PLANTILLA = """\
caso {cid}:
    fecha: "FECHA"
    origen:
        repo: "REPO"
        commit: "COMMIT"
    titulo: "TITULO"
    etiqueta: falso_verde
    sintoma:
        SINTOMA
    como_se_detecto: mutacion
    medida: DOMINIO.MEDIDA
    evidencia:
        RELACION: CAMPO
            "VALOR"
    leccion:
        LECCION
"""

ESCALARES = (str, int, float, bool, type(None))
ESTADOS_SIN_MEDIDA = {"abierto", "resuelto", "limite_humano"}


def casos(raiz: Path) -> list[Path]:
    return rutas_de_corpus(raiz)


def ruta_de_caso_nuevo(proy, ubicacion: str) -> Path:
    if not isinstance(ubicacion, str) or "/" not in ubicacion:
        raise ProyectoInvalido("el caso nuevo debe indicarse como `grupo/NNN-descripcion`")
    partes = ubicacion.split("/")
    if len(partes) != 2:
        raise ProyectoInvalido("el caso nuevo debe indicarse como `grupo/NNN-descripcion`")
    grupo, cid = partes
    if GRUPO_CASO_RE.fullmatch(grupo) is None:
        raise ProyectoInvalido("el grupo del corpus debe usar minúsculas ASCII, dígitos, `_` y `-`")
    if ID_CASO_RE.fullmatch(cid) is None:
        raise ProyectoInvalido(
            "el id de caso debe ser `NNN-descripcion`, sólo con minúsculas ASCII, dígitos y `-`")
    corpus = proy.corpus.resolve()
    destino = proy.corpus / grupo / f"{cid}.caso"
    try:
        destino.resolve().relative_to(corpus)
    except (OSError, ValueError) as e:
        raise ProyectoInvalido(f"el destino de {ubicacion!r} escapa de `corpus/`") from e
    return destino


def nuevo(proy, ubicacion: str) -> int:
    try:
        destino = ruta_de_caso_nuevo(proy, ubicacion)
    except ProyectoInvalido as e:
        print(f"id inválido: {e}")
        return 1
    if destino.exists():
        print(f"ya existe: {presentar_ruta(proy, destino)}")
        return 1
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(PLANTILLA.format(cid=destino.stem), encoding="utf-8")
    print(f"creado: {presentar_ruta(proy, destino)}\n")
    print("Reemplazá los marcadores en MAYÚSCULAS. Después:")
    print(f"  oracle test")
    return 0


def revisar_evidencia(nombre: str, evidencia) -> list[str]:
    """L0: relación → filas planas. Sin objetos anidados, sin listas dentro de un campo.

    Una relación puede encabezarse con `["clave", [<campo>, …]]`, la declaración opcional de
    unicidad. Se valida con la misma función que usa el álgebra —no con una copia de la regla acá—
    porque dos lecturas del mismo contrato terminan divergiendo, que es el caso `012` del corpus.
    Sin esto, un caso que declarara una clave era rechazado como «no es un hecho» y el mecanismo no
    se podía fijar con casos, que es como este proyecto fija todo lo demás.
    """
    fallas = []
    if not isinstance(evidencia, dict) or not evidencia:
        return [f"{nombre}: `evidencia` tiene que ser un mapa de relación → filas, y no estar vacío"]
    for relacion, filas in evidencia.items():
        if not isinstance(filas, list):
            fallas.append(f"{nombre}: la relación «{relacion}» no es una lista de filas")
            continue
        try:
            _clave, filas = separar_clave(filas)
        except ErrorDeAlgebra as e:
            fallas.append(f"{nombre}: la relación «{relacion}» declara mal su clave: {e}")
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


def revisar_estado_sin_medida(nombre: str, caso: dict) -> list[str]:
    if caso.get("medida"):
        return []
    estado = caso.get("estado_sin_medida")
    if estado not in ESTADOS_SIN_MEDIDA:
        return [f"{nombre}: `medida` es nula y `estado_sin_medida` no está en "
                f"{sorted(ESTADOS_SIN_MEDIDA)}"]
    campo = {"abierto": "sin_medida_todavia", "resuelto": "resuelto",
             "limite_humano": "limite_humano"}[estado]
    if not str(caso.get(campo, "")).strip():
        return [f"{nombre}: estado {estado!r} necesita `{campo}` no vacío"]
    return []


def verificar(raiz: Path) -> tuple[list[str], list[dict]]:
    fallas: list[str] = []
    cargados: list[dict] = []
    vistos: dict[str, Path] = {}

    for p in casos(raiz):
        try:
            c = cargar_fuente_caso(p)
        except CasoMalDeclarado as e:
            fallas.append(str(e))
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

        fallas += revisar_estado_sin_medida(p.name, c)

        fallas += revisar_evidencia(p.name, c["evidencia"])
        cargados.append(c)

    return fallas, cargados


def resumen(cargados: list[dict]) -> None:
    print(f"\ncasos: {len(cargados)}")
    for titulo, clave in (("por etiqueta", "etiqueta"), ("por cómo se detectó", "como_se_detecto")):
        print(f"\n{titulo}:")
        for k, n in Counter(c[clave] for c in cargados).most_common():
            print(f"  {n:2}  {k}")
    for estado, titulo in (("abierto", "huecos abiertos"),
                           ("resuelto", "casos resueltos conservados como memoria"),
                           ("limite_humano", "límites humanos no automatizables")):
        ids = [c["id"] for c in cargados if c.get("estado_sin_medida") == estado]
        print(f"\n{titulo} ({len(ids)}):")
        for cid in ids:
            print("  ·", cid)
    print("\nmedidas que el corpus reclama:")
    for k, n in Counter(c["medida"] for c in cargados if c["medida"]).most_common():
        print(f"  {n:2}  {k}")


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = sin_bandera(argv)
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    proy = resolver_cli(argv)
    if proy is None:
        return 1
    estructura = problemas_estructura(proy, ("corpus",))
    if estructura:
        print("PROYECTO INVÁLIDO — " + "; ".join(estructura))
        return 1
    if args and args[0] == "--nuevo":
        if len(args) != 2:
            print("uso: python tools/corpus.py --nuevo <grupo/NNN-descripcion>")
            return 1
        return nuevo(proy, args[1])
    fallas, cargados = verificar(proy.corpus)
    if fallas:
        print(f"CORPUS: {len(fallas)} problema(s)")
        for f in fallas:
            print("  ·", f)
        return 1
    print(f"CORPUS OK · {len(cargados)} casos · esquema, evidencia L0 y trazabilidad en regla")
    if "--resumen" in args:
        resumen(cargados)
    return 0


if __name__ == "__main__":
    sys.exit(main())
