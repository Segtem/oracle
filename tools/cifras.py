"""Genera y comprueba las cifras técnicas publicadas en el README de Oracle."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


def cifras() -> str:
    suite = unittest.defaultTestLoader.discover(
        str(RAIZ / "tests"), top_level_dir=str(RAIZ))
    cantidad_tests = suite.countTestCases()

    from nucleo.medida import cargar_catalogo
    from nucleo.mutacion import correr as mutar_medidas
    from nucleo.proyecto import catalogos_a_cargar
    from perfiles.python.mutacion_codigo import sitios_de
    from tools import mutar as cli_medidas
    from tools.mutar_codigo import objetivos_disponibles

    catalogo = cargar_catalogo(catalogos_a_cargar(cli_medidas.PROY))
    evidencia = mutar_medidas(catalogo, cli_medidas.casos(catalogo))
    mutantes_medida = evidencia["mutante"]
    muertos_medida = sum(fila["murio"] for fila in mutantes_medida)

    por_objetivo = {
        nombre: len(sitios_de(ruta, RAIZ))
        for nombre, ruta in objetivos_disponibles().items()
    }
    motor_python = por_objetivo["perfiles/python/mutacion_codigo.py"]
    total_codigo = sum(por_objetivo.values())
    resto_codigo = total_codigo - motor_python
    return (
        f"{cantidad_tests} tests · {muertos_medida}/{len(mutantes_medida)} mutantes de medida · "
        f"**{total_codigo} sitios de mutación de código** "
        f"({resto_codigo} + {motor_python} del motor Python)."
    )


def actualizar(contenido: str, bloque: str) -> str:
    inicio = "<!-- cifras:inicio -->"
    fin = "<!-- cifras:fin -->"
    antes, separador, resto = contenido.partition(inicio)
    if not separador:
        raise ValueError(f"falta {inicio} en README.md")
    _viejo, separador, despues = resto.partition(fin)
    if not separador:
        raise ValueError(f"falta {fin} en README.md")
    return f"{antes}{inicio}\n{bloque}\n{fin}{despues}"


def main() -> int:
    ruta = RAIZ / "README.md"
    previo = ruta.read_text(encoding="utf-8")
    esperado = actualizar(previo, cifras())
    if "--actualizar" in sys.argv[1:]:
        ruta.write_text(esperado, encoding="utf-8")
        print("README.md actualizado")
        return 0
    if previo != esperado:
        print("README.md tiene cifras vencidas; ejecutá `python tools/cifras.py --actualizar`")
        return 1
    print("CIFRAS OK — " + cifras())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
