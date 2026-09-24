"""Regenera sólo el bloque de herramientas del contrato MCP desde el código."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.mcp import HERRAMIENTAS, RAIZ  # noqa: E402


def regenerar(documento: str) -> str:
    inicio = "<!-- herramientas-json:inicio -->"
    fin = "<!-- herramientas-json:fin -->"
    antes, bloque = documento.split(inicio, 1)
    _, despues = bloque.split(fin, 1)
    declaracion = json.dumps(HERRAMIENTAS, ensure_ascii=False, indent=2)
    return f"{antes}{inicio}\n```json\n{declaracion}\n```\n{fin}{despues}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    ruta = RAIZ / "estudios" / "MCP-CONTRATO.md"
    original = ruta.read_text(encoding="utf-8")
    generado = regenerar(original)
    if args.check:
        if original != generado:
            print("Contrato desactualizado: ejecutar python3 -m tools.mcp_contrato")
            return 1
    else:
        ruta.write_text(generado, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
