"""Flujo consumidor: aceptación actual + tracker → política de cierre.

No guarda informes reutilizables: sólo juzga la composición de esta ejecución.
Al copiar el ejemplo fuera del checkout, usar --oracle oracle.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

POLITICA = "seguimiento.toda_tarea_cerrada_cumple_medidas_de_cierre"


def leer_salida(resultado: subprocess.CompletedProcess, codigos: tuple[int, ...]) -> dict:
    if resultado.returncode not in codigos:
        raise ValueError(f"falló Oracle (código {resultado.returncode}): {resultado.stderr.strip()}")
    datos = json.loads(resultado.stdout)
    if not isinstance(datos, dict):
        raise ValueError("se esperaba un objeto JSON de Oracle")
    return datos


def convertir_aceptacion(resultado: subprocess.CompletedProcess) -> dict:
    """El ok global y las sombras nunca reemplazan el ok individual."""
    datos = leer_salida(resultado, (0, 1))
    if (type(datos.get("ok")) is not bool
            or not isinstance(datos.get("medidas"), list)
            or not isinstance(datos.get("no_aplicadas"), list)):
        raise ValueError("informe de juzgar inválido")
    filas = []
    vistos = set()
    for medida in datos["medidas"]:
        if (not isinstance(medida, dict) or not isinstance(medida.get("id"), str)
                or not medida["id"] or type(medida.get("ok")) is not bool):
            raise ValueError("veredicto individual inválido")
        if medida["id"] in vistos:
            raise ValueError("veredicto duplicado")
        vistos.add(medida["id"])
        filas.append({"medida": medida["id"], "ok": medida["ok"]})
    return {"aceptacion_medida": filas}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proyecto", required=True, help="catálogo del dominio")
    parser.add_argument("--con", required=True, help="evidencia actual del dominio")
    parser.add_argument("--tracker", required=True, help="proyecto con tareas/")
    parser.add_argument("--git", action="store_true", help="incluir diagnóstico Git del tracker")
    parser.add_argument("--politicas", default=str(Path(__file__).resolve().parent))
    parser.add_argument("--oracle", nargs="+", default=[
        sys.executable, "-B", str(Path(__file__).resolve().parents[2] / "tools/cli.py")])
    args = parser.parse_args(argv)

    def ejecutar(argumentos):
        return subprocess.run(args.oracle + argumentos, capture_output=True, text=True, check=False)

    try:
        aceptacion = convertir_aceptacion(ejecutar([
            "juzgar", "--proyecto", args.proyecto, "--con", args.con, "--json"]))
        tracker = leer_salida(ejecutar([
            "tarea", "hechos", "--proyecto", args.tracker,
            *(["--git"] if args.git else [])]), (0,))
        if (not {"tarea_seguimiento", "tarea_cierre_medida"} <= tracker.keys()
                or "aceptacion_medida" in tracker
                or any(not isinstance(filas, list) or any(not isinstance(fila, dict) for fila in filas)
                       for filas in tracker.values())):
            raise ValueError("hechos del tracker inválidos o incompatibles")
        # Archivo nuevo y privado por corrida: un error nunca recupera evidencia previa.
        with tempfile.TemporaryDirectory(prefix="oracle-cierre-") as temporal:
            ruta = Path(temporal) / "hechos.json"
            ruta.write_text(json.dumps({**tracker, **aceptacion}), encoding="utf-8")
            resultado = ejecutar([
                "juzgar", "--proyecto", args.politicas, "--con", str(ruta),
                "--medida", POLITICA, "--json"])
            leer_salida(resultado, (0, 1))
        print(resultado.stdout, end="")
        return resultado.returncode
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
