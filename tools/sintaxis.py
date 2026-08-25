"""CLI para la superficie infija de autoría.

    python tools/sintaxis.py --imprimir catalogos/meta/meta.donde_compone.json
    python tools/sintaxis.py --leer medida.oracle
    python tools/sintaxis.py --verificar
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.sintaxis import (  # noqa: E402,F401
    ErrorSintaxis,
    Lectura,
    Ubicacion,
    fragmento_de_error,
    imprimir,
    leer,
    leer_con_mapa,
    ubicar_ruta,
)
from nucleo.medida import cargar_fuente_medida, rutas_de_catalogo  # noqa: E402


def _rutas_catalogo(raiz: Path = RAIZ) -> list[Path]:
    return rutas_de_catalogo(
        raiz / "catalogos",
        *sorted((raiz / "perfiles").glob("*/catalogos")),
    )


def _rutas_macros(raiz: Path = RAIZ) -> list[Path]:
    """La biblioteca estándar de macros. Una macro es la otra mitad del lenguaje: si la superficie
    cubre las medidas y no las macros, es la sintaxis de la mitad del lenguaje."""
    from nucleo.macro import EXTENSIONES_DE_MACRO

    return sorted(p for p in (raiz / "nucleo" / "macros").iterdir()
                  if p.suffix in EXTENSIONES_DE_MACRO and p.is_file())


def _puntuacion(texto: str) -> int:
    return sum(1 for c in texto if unicodedata.category(c).startswith("P"))


def _fila_verificacion(ruta: Path, raiz: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8")
    datos = leer(texto) if ruta.suffix == ".oracle" else json.loads(texto)
    superficie = imprimir(datos)
    releida = leer(superficie)
    reimpresa = imprimir(releida)
    json_compacto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    return {
        "ruta": str(ruta.relative_to(raiz)),
        "json_igual": releida == datos,
        "texto_igual": reimpresa == superficie,
        "caracteres_json": len(json_compacto),
        "caracteres_superficie": len(superficie),
        "puntuacion_json": _puntuacion(json_compacto),
        "puntuacion_superficie": _puntuacion(superficie),
    }


def verificar_catalogo(raiz: Path = RAIZ) -> dict:
    filas_medidas = [_fila_verificacion(r, raiz) for r in _rutas_catalogo(raiz)]
    filas_macros = [_fila_verificacion(r, raiz) for r in _rutas_macros(raiz)]
    filas = filas_medidas + filas_macros
    total = {
        "medidas": len(filas_medidas),
        "macros": len(filas_macros),
        "json_igual": all(f["json_igual"] for f in filas),
        "texto_igual": all(f["texto_igual"] for f in filas),
        "caracteres_json": sum(f["caracteres_json"] for f in filas),
        "caracteres_superficie": sum(f["caracteres_superficie"] for f in filas),
        "puntuacion_json": sum(f["puntuacion_json"] for f in filas),
        "puntuacion_superficie": sum(f["puntuacion_superficie"] for f in filas),
        "filas": filas,
    }
    return total


# Los documentos que enseñan la superficie llevan bloques cercados. Sólo ```oracle promete ser una
# medida completa y verificable; las otras dos etiquetas declaran por qué un bloque NO se ejecuta, y
# esa declaración es el punto. `ORACLE-TUTORIAL-PRACTICO.md` afirma en su encabezado que todos sus
# ejemplos fueron verificados contra el código vigente, y hasta hoy esa afirmación no la ejercitaba
# nada: la sostenía la palabra de quien escribió el documento, que es exactamente la clase de
# afirmación que este repositorio no acepta en ningún otro lado.
DOCUMENTOS_CON_SUPERFICIE = ("ESCRIBIR-UNA-MEDIDA.md", "ORACLE-TUTORIAL-PRACTICO.md")
BLOQUE_RE = re.compile(r"```(oracle|oracle-gramatica|oracle-fragmento)\n(.*?)```", re.S)


def verificar_documentos(raiz: Path = RAIZ) -> dict:
    """Cada bloque ```oracle de los documentos tiene que leer y volver idéntico."""
    fallas, ejecutables, declarados = [], 0, 0
    for nombre in DOCUMENTOS_CON_SUPERFICIE:
        ruta = raiz / nombre
        if not ruta.exists():
            # Un documento declarado que no está es un ERROR, no un salto: si faltara en silencio,
            # sacar un documento de la verificación sería tan barato como renombrarlo.
            fallas.append(f"{nombre}: declarado pero no está en el árbol")
            continue
        texto = ruta.read_text(encoding="utf-8")
        for m in BLOQUE_RE.finditer(texto):
            etiqueta, bloque = m.group(1), m.group(2)
            linea = texto[:m.start()].count("\n") + 1
            if etiqueta != "oracle":
                declarados += 1
                continue
            ejecutables += 1
            try:
                datos = leer(bloque)
            except ErrorSintaxis as e:
                fallas.append(f"{nombre}:{linea}: no lee — {e}")
                continue
            if imprimir(datos) != bloque:
                fallas.append(f"{nombre}:{linea}: lee pero no es la forma canónica que imprime la "
                              "herramienta")
    return {"ejecutables": ejecutables, "declarados": declarados, "fallas": fallas}


def _porcentaje(num: int, den: int) -> str:
    return f"{(100 * num / den):.1f}%".replace(".", ",") if den else "0,0%"


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--imprimir":
        if len(argv) != 2:
            print("uso: python tools/sintaxis.py --imprimir <medida.json|medida.oracle>")
            return 1
        print(imprimir(cargar_fuente_medida(Path(argv[1]))), end="")
        return 0
    if argv[0] == "--leer":
        if len(argv) != 2:
            print("uso: python tools/sintaxis.py --leer <medida.oracle>")
            return 1
        try:
            datos = leer(Path(argv[1]).read_text(encoding="utf-8"))
        except ErrorSintaxis as e:
            print(f"✗ {e}")
            return 1
        print(json.dumps(datos, ensure_ascii=False, separators=(",", ":")))
        return 0
    if argv[0] == "--verificar":
        informe = verificar_catalogo()
        docs = verificar_documentos()
        ok = (informe["json_igual"] and informe["texto_igual"] and informe["medidas"] > 0
              and informe["macros"] > 0 and not docs["fallas"] and docs["ejecutables"] > 0)
        print(f"medidas convertidas: {informe['medidas']}")
        print(f"macros convertidas: {informe['macros']}")
        print(f"ida JSON: {'OK' if informe['json_igual'] else 'FALLA'}")
        print(f"vuelta texto: {'OK' if informe['texto_igual'] else 'FALLA'}")
        print(f"caracteres: JSON {informe['caracteres_json']} · superficie "
              f"{informe['caracteres_superficie']}")
        print(f"puntuación: JSON {informe['puntuacion_json']} "
              f"({_porcentaje(informe['puntuacion_json'], informe['caracteres_json'])}) · "
              f"superficie {informe['puntuacion_superficie']} "
              f"({_porcentaje(informe['puntuacion_superficie'], informe['caracteres_superficie'])})")
        print(f"bloques de documentación: {docs['ejecutables']} verificados · "
              f"{docs['declarados']} declarados como gramática o fragmento")
        for falla in docs["fallas"]:
            print(f"  ✗ {falla}")
        return 0 if ok else 1
    print(f"opción desconocida: {argv[0]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
