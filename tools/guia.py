#!/usr/bin/env python3
"""Reconstruye el ejemplo de docs/de-cero.md y comprueba sus salidas.

Con --escribir sustituye sólo los cuerpos de los bloques ``text salida``.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

RAIZ = Path(__file__).resolve().parents[1]
GUIA = RAIZ / "docs/de-cero.md"
CLI = RAIZ / "tools/cli.py"
FENCE = re.compile(r"^```([^\n]*)$")
ATRIBUTOS = re.compile(r"(archivo|incluir)=([^\s]+)")
TIEMPO = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:ms|s|segundos?)\b")


def bloques(lineas: list[str]):
    """Devuelve (inicio, fin, cabecera, cuerpo), con fin en el cierre del fence."""
    i = 0
    while i < len(lineas):
        m = FENCE.fullmatch(lineas[i].rstrip("\n"))
        if not m:
            i += 1
            continue
        j = i + 1
        while j < len(lineas) and lineas[j].strip() != "```":
            j += 1
        if j == len(lineas):
            raise ValueError(f"Bloque sin cierre en línea {i + 1}")
        yield i, j, m.group(1).split(), "".join(lineas[i + 1:j])
        i = j + 1


def dentro(base: Path, ruta: str) -> Path:
    destino = (base / ruta).resolve()
    if not destino.is_relative_to(base.resolve()) or destino == base.resolve():
        raise ValueError(f"Ruta fuera del proyecto: {ruta}")
    return destino


def normalizar(salida: str, temporal: Path) -> str:
    salida = salida.replace(str(temporal / "batalla-naval"), "batalla-naval")
    salida = salida.replace(str(temporal), ".")
    salida = TIEMPO.sub("<tiempo>", salida)
    return salida.rstrip("\n") + ("\n" if salida else "")


def correr(comando: str, cwd: Path, temporal: Path) -> tuple[str, Path]:
    argumentos = shlex.split(comando)
    if not argumentos:
        return "", cwd
    if argumentos[:3] == ["uv", "tool", "install"]:
        return "", cwd
    if argumentos[0] == "cd":
        if len(argumentos) != 2:
            raise ValueError(f"cd inválido: {comando}")
        destino = dentro(temporal, str((cwd / argumentos[1]).relative_to(temporal)))
        if not destino.is_dir():
            raise ValueError(f"No existe el directorio {argumentos[1]}")
        return "", destino
    if argumentos[0] == "oracle":
        argumentos = [sys.executable, str(CLI), *argumentos[1:]]
    elif argumentos[0] == "python3":
        argumentos[0] = sys.executable
    else:
        raise ValueError(f"Comando no contemplado: {comando}")
    entorno = os.environ.copy()
    entorno.pop("ORACLE_PROYECTO", None)
    entorno.pop("PYTHONPATH", None)
    p = subprocess.run(argumentos, cwd=cwd, env=entorno, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True, timeout=180)
    salida = normalizar(p.stdout, temporal)
    if p.returncode and not ("VEREDICTO: ROJO" in salida or
                             (" medidas en rojo" in salida and argumentos[2] == "juzgar")):
        raise RuntimeError(f"Falló `{comando}` (código {p.returncode}):\n{salida}")
    return salida, cwd


def verificar(escribir: bool = False, guia: Path = GUIA) -> None:
    lineas = guia.read_text(encoding="utf-8").splitlines(keepends=True)
    encontrados = list(bloques(lineas))
    cambios: list[tuple[int, int, str]] = []
    with tempfile.TemporaryDirectory(prefix="oracle-guia-") as tmp:
        temporal = Path(tmp)
        cwd = temporal
        for n, (inicio, fin, cabecera, cuerpo) in enumerate(encontrados):
            atributos = dict(ATRIBUTOS.findall(" ".join(cabecera)))
            if "archivo" in atributos or "incluir" in atributos:
                if set(atributos) != {"archivo", "incluir"}:
                    raise ValueError(f"Faltan atributos en línea {inicio + 1}")
                fuente = dentro(RAIZ, atributos["incluir"])
                destino = dentro(cwd, atributos["archivo"])
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(fuente.read_bytes())
            if cabecera != ["bash", "paso"]:
                continue
            salida = ""
            for comando in cuerpo.splitlines():
                if comando.strip() and not comando.lstrip().startswith("#"):
                    fragmento, cwd = correr(comando, cwd, temporal)
                    salida += fragmento
            if n + 1 >= len(encontrados) or encontrados[n + 1][2] != ["text", "salida"]:
                raise ValueError(f"Falta `text salida` después del paso en línea {inicio + 1}")
            si, sf, _, esperado = encontrados[n + 1]
            if salida != esperado:
                if not escribir:
                    raise AssertionError(f"Salida vieja en línea {si + 1}; ejecutá "
                                         "python3 tools/guia.py --escribir")
                cambios.append((si + 1, sf, salida))
    if escribir:
        for inicio, fin, salida in reversed(cambios):
            lineas[inicio:fin] = salida.splitlines(keepends=True)
        guia.write_text("".join(lineas), encoding="utf-8")
    print(f"Guía verificada: {sum(b[2] == ['bash', 'paso'] for b in encontrados)} pasos, "
          f"{len(cambios)} salidas actualizadas")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--escribir", action="store_true")
    args = parser.parse_args()
    try:
        verificar(args.escribir)
    except (AssertionError, RuntimeError, ValueError, OSError) as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
