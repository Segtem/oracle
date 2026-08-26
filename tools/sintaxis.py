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
from nucleo import caso as sintaxis_caso  # noqa: E402
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

    dir_macros = raiz / "nucleo" / "macros" if (raiz / "nucleo" / "macros").is_dir() else raiz / "macros"
    if not dir_macros.is_dir():
        return []
    return sorted(p for p in dir_macros.iterdir()
                  if p.suffix in EXTENSIONES_DE_MACRO and p.is_file())


def _rutas_corpus(raiz: Path = RAIZ) -> list[Path]:
    return sintaxis_caso.rutas_de_corpus(raiz / "corpus")


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


def _fila_verificacion_caso(ruta: Path, raiz: Path) -> dict:
    datos = sintaxis_caso.cargar_fuente_caso(ruta)
    superficie = sintaxis_caso.imprimir(datos)
    releida = sintaxis_caso.leer(superficie)
    reimpresa = sintaxis_caso.imprimir(releida)
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
    filas_casos = [_fila_verificacion_caso(r, raiz) for r in _rutas_corpus(raiz)]
    filas = filas_medidas + filas_macros + filas_casos
    total = {
        "medidas": len(filas_medidas),
        "macros": len(filas_macros),
        "casos": len(filas_casos),
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
# Los cuatro documentos que muestran superficie. Eran dos: al entrar la superficie de CASOS, los
# ejemplos nuevos aparecieron también en el README y en la especificación, y ahí nadie los miraba.
DOCUMENTOS_CON_SUPERFICIE = ("ESCRIBIR-UNA-MEDIDA.md", "ORACLE-TUTORIAL-PRACTICO.md",
                             "README.md", "ESPECIFICACION.md")
# Dos superficies, dos lectores. `oracle` es una medida y `caso` es un caso del corpus; las
# etiquetas con sufijo declaran por qué un bloque NO se ejecuta, y esa declaración es el punto.
BLOQUE_RE = re.compile(
    r"```(oracle|caso)(-gramatica|-fragmento)?\n(.*?)```", re.S)


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
            superficie, sufijo, bloque = m.group(1), m.group(2), m.group(3)
            linea = texto[:m.start()].count("\n") + 1
            if sufijo:
                declarados += 1
                continue
            ejecutables += 1
            leer_, imprimir_ = ((leer, imprimir) if superficie == "oracle"
                                else (sintaxis_caso.leer, sintaxis_caso.imprimir))
            try:
                datos = leer_(bloque)
            except (ErrorSintaxis, sintaxis_caso.CasoMalDeclarado) as e:
                fallas.append(f"{nombre}:{linea}: no lee — {e}")
                continue
            if imprimir_(datos) != bloque:
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
        # El LECTOR es puro a propósito y no juzga la versión declarada; eso es trabajo del que
        # carga. Pero esta rama del CLI también carga: sin la comprobación, `--leer` traducía en
        # silencio —y con exit 0— un archivo escrito contra una sintaxis que este núcleo no
        # implementa, mientras `cargar_fuente_medida` y `cargar_macros` lo rechazaban. Una salida
        # fail-open al lado de dos fail-closed es peor que no tener ninguna: enseña a confiar.
        from nucleo.version import VersionInvalida, exigir_sintaxis_compatible

        texto = Path(argv[1]).read_text(encoding="utf-8")
        try:
            lectura = leer_con_mapa(texto)
            exigir_sintaxis_compatible(lectura.version)
        except (ErrorSintaxis, VersionInvalida) as e:
            print(f"✗ {fragmento_de_error(e, texto)}")
            return 1
        datos = lectura.datos
        print(json.dumps(datos, ensure_ascii=False, separators=(",", ":")))
        return 0
    if argv[0] == "--verificar":
        informe = verificar_catalogo()
        docs = verificar_documentos()
        ok = (informe["json_igual"] and informe["texto_igual"] and informe["medidas"] > 0
              and informe["macros"] > 0 and informe["casos"] > 0 and not docs["fallas"]
              and docs["ejecutables"] > 0)
        print(f"medidas convertidas: {informe['medidas']}")
        print(f"macros convertidas: {informe['macros']}")
        print(f"casos convertidos: {informe['casos']}")
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
