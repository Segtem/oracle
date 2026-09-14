"""Ejemplo de consumidor: juzga hechos JSON con las políticas locales elegidas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from oracle_metalenguaje import Motor


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--con", dest="evidencia", required=True, type=Path,
                        help="Archivo JSON emitido por oracle tarea hechos")
    parser.add_argument("--politica", action="append", choices=(
        "referencias_locales_presentes", "archivos_confirmados_sin_cambios", "lectura_sin_omisiones"),
        help="Política a evaluar; repetible. Por defecto evalúa las tres del ejemplo.")
    args = parser.parse_args(argv)
    try:
        evidencia = json.loads(args.evidencia.read_text(encoding="utf-8"))
        if not isinstance(evidencia, dict) or not all(
                isinstance(filas, list) and all(isinstance(fila, dict) for fila in filas)
                for filas in evidencia.values()):
            raise ValueError("se esperaba un objeto relación → lista de filas")
        catalogo = {m.id: m for m in Motor.desde_proyecto(Path(__file__).parent).medidas}
        elegidas = {"seguimiento." + nombre for nombre in args.politica} if args.politica else set(catalogo)
        veredictos = [catalogo[mid].evaluar(evidencia) for mid in sorted(elegidas)]
    except (OSError, ValueError, TypeError) as e:
        print(f"ERROR: no se pudo evaluar la evidencia: {e}", file=sys.stderr)
        return 2
    for v in veredictos:
        print(v.linea())
        for testigo in v.testigos:
            print("  testigo: " + json.dumps(testigo, ensure_ascii=False, sort_keys=True))
    return 0 if all(v.ok for v in veredictos) else 1


if __name__ == "__main__":
    sys.exit(main())
