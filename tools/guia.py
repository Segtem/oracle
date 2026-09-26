#!/usr/bin/env python3
"""Reconstruye los recorridos de las guías y comprueba sus salidas.

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
import shutil

RAIZ = Path(__file__).resolve().parents[1]
GUIAS = tuple(RAIZ / "docs" / nombre for nombre in (
    "de-cero.md", "como-funciona.md", "02-de-cero-a-un-rojo.md", "05-por-que-la-mutacion.md",
    "07-conectar-a-un-proyecto-propio.md", "13-primer-valor.md", "recetas.md"))
GUIA = GUIAS[0]
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
    salida = salida.replace(str(RAIZ), "…/oracle")
    salida = salida.replace(str(temporal / "batalla-naval"), "batalla-naval")
    salida = salida.replace(str(temporal), ".")
    salida = TIEMPO.sub("<tiempo>", salida)
    return salida.rstrip("\n") + ("\n" if salida else "")


def correr(comando: str, cwd: Path, temporal: Path, falla: bool = False) -> tuple[str, Path]:
    comando = comando.replace("\\\n", "")
    # La guía 07 pasa al CLI la salida del sensor sin invocar un shell general.
    sustitucion = re.search(r'"\$\((python3 [^()]+)\)"', comando)
    if sustitucion:
        salida_sensor, _ = correr(sustitucion.group(1), cwd, temporal)
        comando = comando[:sustitucion.start()] + shlex.quote(salida_sensor.rstrip("\n")) + comando[sustitucion.end():]
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
    if argumentos[0] == "rm" and argumentos[1:2] == ["-f"] and len(argumentos) == 3:
        dentro(cwd, argumentos[2]).unlink(missing_ok=True)
        return "", cwd
    if argumentos[0] == "oracle":
        argumentos = [sys.executable, str(CLI), *argumentos[1:]]
    elif argumentos[0] == "python3":
        argumentos[0] = sys.executable
        if len(argumentos) > 1 and not argumentos[1].startswith("-"):
            dentro(cwd, argumentos[1])
    else:
        raise ValueError(f"Comando no contemplado: {comando}")
    entorno = os.environ.copy()
    entorno.pop("ORACLE_PROYECTO", None)
    entorno.pop("PYTHONPATH", None)
    p = subprocess.run(argumentos, cwd=cwd, env=entorno, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True, timeout=180)
    salida = normalizar(p.stdout, temporal)
    # Un paso `bash paso falla` muestra un error a propósito: tiene que fallar, y si no falla la
    # guía está mostrando algo que Oracle ya no hace.
    if falla:
        if not p.returncode:
            raise RuntimeError(f"Se esperaba que fallara `{comando}` y terminó bien:\n{salida}")
        return salida, cwd
    if p.returncode and not (len(argumentos) > 2 and argumentos[2] == "revisar" or
                             "VEREDICTO: ROJO" in salida or "CATÁLOGO INVÁLIDO" in salida or
                             ((" medidas en rojo" in salida or " medidas propias sin aplicar" in salida)
                              and len(argumentos) > 2 and argumentos[2] == "juzgar")):
        raise RuntimeError(f"Falló `{comando}` (código {p.returncode}):\n{salida}")
    return salida, cwd


def reemplazar_salidas(lineas: list[str], cambios: list[tuple[int, int, str]]) -> list[str]:
    """Devuelve una copia con los cuerpos de salida nuevos, conservando el resto del documento."""
    resultado = lineas.copy()
    for inicio, fin, salida in reversed(cambios):
        resultado[inicio:fin] = salida.splitlines(keepends=True)
    return resultado


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
                if fuente.is_dir():
                    shutil.copytree(fuente, destino, dirs_exist_ok=True)
                else:
                    destino.write_bytes(fuente.read_bytes())
            if cabecera not in (["bash", "paso"], ["bash", "paso", "falla"]):
                continue
            falla = cabecera[2:] == ["falla"]
            salida = ""
            comandos = []
            for linea in cuerpo.splitlines():
                if linea.startswith(" ") and comandos:
                    comandos[-1] += "\n" + linea
                elif linea.endswith("\\") and comandos:
                    comandos[-1] += "\n" + linea
                else:
                    comandos.append(linea)
            for comando in comandos:
                if comando.strip() and not comando.lstrip().startswith("#"):
                    fragmento, cwd = correr(comando, cwd, temporal, falla)
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
        guia.write_text("".join(reemplazar_salidas(lineas, cambios)), encoding="utf-8")
    print(f"{guia.relative_to(RAIZ)}: {sum(b[2][:2] == ['bash', 'paso'] for b in encontrados)} pasos, "
          f"{len(cambios)} salidas actualizadas")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--escribir", action="store_true")
    parser.add_argument("guias", nargs="*", help="rutas de guías; sin argumentos ejecuta todas")
    args = parser.parse_args()
    try:
        for guia in (args.guias or GUIAS):
            verificar(args.escribir, Path(guia).resolve())
    except (AssertionError, RuntimeError, ValueError, OSError) as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
