"""CLI para la superficie infija de autoría.

    python tools/sintaxis.py --imprimir catalogos/meta/meta.donde_compone.json
    python tools/sintaxis.py --leer medida.oracle
    python tools/sintaxis.py --verificar
"""

from __future__ import annotations

import json
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


def _puntuacion(texto: str) -> int:
    return sum(1 for c in texto if unicodedata.category(c).startswith("P"))


def verificar_catalogo(raiz: Path = RAIZ) -> dict:
    filas = []
    for ruta in _rutas_catalogo(raiz):
        datos = cargar_fuente_medida(ruta)
        superficie = imprimir(datos)
        releida = leer(superficie)
        reimpresa = imprimir(releida)
        json_compacto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
        filas.append({
            "ruta": str(ruta.relative_to(raiz)),
            "json_igual": releida == datos,
            "texto_igual": reimpresa == superficie,
            "caracteres_json": len(json_compacto),
            "caracteres_superficie": len(superficie),
            "puntuacion_json": _puntuacion(json_compacto),
            "puntuacion_superficie": _puntuacion(superficie),
        })
    total = {
        "medidas": len(filas),
        "json_igual": all(f["json_igual"] for f in filas),
        "texto_igual": all(f["texto_igual"] for f in filas),
        "caracteres_json": sum(f["caracteres_json"] for f in filas),
        "caracteres_superficie": sum(f["caracteres_superficie"] for f in filas),
        "puntuacion_json": sum(f["puntuacion_json"] for f in filas),
        "puntuacion_superficie": sum(f["puntuacion_superficie"] for f in filas),
        "filas": filas,
    }
    return total


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
        ok = informe["json_igual"] and informe["texto_igual"] and informe["medidas"] > 0
        print(f"medidas convertidas: {informe['medidas']}")
        print(f"ida JSON: {'OK' if informe['json_igual'] else 'FALLA'}")
        print(f"vuelta texto: {'OK' if informe['texto_igual'] else 'FALLA'}")
        print(f"caracteres: JSON {informe['caracteres_json']} · superficie "
              f"{informe['caracteres_superficie']}")
        print(f"puntuación: JSON {informe['puntuacion_json']} "
              f"({_porcentaje(informe['puntuacion_json'], informe['caracteres_json'])}) · "
              f"superficie {informe['puntuacion_superficie']} "
              f"({_porcentaje(informe['puntuacion_superficie'], informe['caracteres_superficie'])})")
        return 0 if ok else 1
    print(f"opción desconocida: {argv[0]}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
