#!/usr/bin/env python3
"""Construye o verifica un espejo del catálogo Jam con `segun` declarado.

Jam es sólo lectura. El resultado vive junto a este estudio y se puede copiar al consumidor cuando
su dueño decida adoptarlo.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


RAIZ_ESTUDIO = Path(__file__).resolve().parent
ORIGENES = {"medicion", "contrato", "convencion", "tanteo"}


def _clasificacion() -> dict[str, str]:
    datos = json.loads((RAIZ_ESTUDIO / "clasificacion.json").read_text(encoding="utf-8"))
    invalidos = {mid: origen for mid, origen in datos.items() if origen not in ORIGENES}
    if invalidos:
        raise ValueError(f"orígenes inválidos: {invalidos}")
    return datos


def _migrar(datos: list, origen: str) -> list:
    salida = json.loads(json.dumps(datos, ensure_ascii=False))
    if salida[0] == "medida":
        umbral = salida[4]
        if not isinstance(umbral, list) or len(umbral) != 4 or umbral[0] != "umbral":
            raise ValueError(f"umbral canónico inesperado: {umbral!r}")
        umbral.append(origen)
        return salida
    if salida[0] not in {"ninguno", "ninguno-par", "ninguno-requiere", "peor"}:
        raise ValueError(f"forma de medida inesperada: {salida[0]!r}")
    salida.insert(-1, origen)
    return salida


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("jam", type=Path, help="raíz del repo Jam, que se abre sólo para lectura")
    parser.add_argument("--verificar", action="store_true", help="comparar sin escribir")
    args = parser.parse_args()

    catalogos = args.jam.resolve() / "medidas" / "catalogos"
    clasificacion = _clasificacion()
    fuentes = sorted(catalogos.rglob("*.json"))
    por_id: dict[str, tuple[Path, list]] = {}
    for fuente in fuentes:
        datos = json.loads(fuente.read_text(encoding="utf-8"))
        mid = datos[1]
        if mid in por_id:
            raise ValueError(f"id repetido en Jam: {mid}")
        por_id[mid] = (fuente, datos)

    faltan = sorted(set(por_id) - set(clasificacion))
    sobran = sorted(set(clasificacion) - set(por_id))
    if faltan or sobran:
        raise ValueError(f"clasificación desfasada; faltan={faltan}, sobran={sobran}")

    destino_raiz = RAIZ_ESTUDIO / "catalogos"
    for mid, (fuente, datos) in por_id.items():
        destino = destino_raiz / fuente.relative_to(catalogos)
        texto = json.dumps(_migrar(datos, clasificacion[mid]), ensure_ascii=False, indent=2) + "\n"
        if args.verificar:
            if not destino.exists() or destino.read_text(encoding="utf-8") != texto:
                raise ValueError(f"espejo desactualizado: {destino.relative_to(RAIZ_ESTUDIO)}")
        else:
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(texto, encoding="utf-8")

    conteos = Counter(clasificacion.values())
    print(
        f"medidas={len(por_id)} · contrato={conteos['contrato']} · "
        f"convencion={conteos['convencion']} · medicion={conteos['medicion']} · "
        f"tanteo={conteos['tanteo']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
