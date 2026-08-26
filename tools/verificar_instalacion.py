#!/usr/bin/env python3
"""Construye el wheel y prueba la API pública desde un entorno y cwd aislados."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]


def _entorno_limpio() -> dict[str, str]:
    env = os.environ.copy()
    env.pop("ORACLE_PROYECTO", None)
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _correr(argumentos, *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    resultado = subprocess.run(
        argumentos,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        comando = " ".join(str(a) for a in argumentos)
        raise RuntimeError(
            f"falló {comando} en {cwd}\nSTDOUT:\n{resultado.stdout}\nSTDERR:\n{resultado.stderr}"
        )
    return resultado


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="oracle-wheel-") as td:
        env = _entorno_limpio()
        temporal = Path(td)
        fuente = temporal / "fuente"
        shutil.copytree(
            RAIZ,
            fuente,
            ignore=shutil.ignore_patterns(
                ".git", "build", "dist", "*.egg-info", "__pycache__", "*.pyc"),
        )
        ruedas = temporal / "ruedas"
        ruedas.mkdir()
        _correr([
            sys.executable, "-m", "pip", "wheel", "--no-deps",
            "--no-build-isolation", "--wheel-dir", str(ruedas), str(fuente),
        ], cwd=temporal, env=env)
        encontradas = tuple(ruedas.glob("oracle_metalenguaje-*.whl"))
        if len(encontradas) != 1:
            raise RuntimeError(f"se esperaba un wheel de Oracle, no {encontradas}")
        with zipfile.ZipFile(encontradas[0]) as wheel:
            nombres = set(wheel.namelist())
        genericos = ("nucleo/", "catalogos/", "perfiles/", "tools/")
        filtrados = sorted(nombre for nombre in nombres if nombre.startswith(genericos))
        if filtrados:
            raise RuntimeError(f"el wheel todavía instala paquetes genéricos: {filtrados[:5]}")
        esperados = {
            "oracle_metalenguaje/nucleo/algebra.py",
            "oracle_metalenguaje/tools/cli.py",
            "oracle_metalenguaje/nucleo/aislamiento/escalares.py",
            "oracle_metalenguaje/nucleo/macros/ninguno.oracle",
            "oracle_metalenguaje/nucleo/macros/ninguno-par.oracle",
            "oracle_metalenguaje/nucleo/macros/peor.oracle",
            "oracle_metalenguaje/catalogos/meta/meta.toda_medida_esta_fijada.oracle",
            "oracle_metalenguaje/perfiles/python/catalogos/proceso/"
            "proceso.arnes_con_bytecode_frio.oracle",
        }
        faltantes = sorted(esperados - nombres)
        if faltantes:
            raise RuntimeError("el wheel no contiene datos requeridos: " + ", ".join(faltantes))

        entorno = temporal / "entorno"
        venv.EnvBuilder(with_pip=True).create(entorno)
        python = entorno / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        _correr([
            str(python), "-m", "pip", "install", "--no-deps", str(encontradas[0]),
        ], cwd=temporal, env=env)
        _correr([
            str(python), "-I", "-c",
            ("import importlib.util\n"
             "for nombre in ('nucleo', 'catalogos', 'perfiles', 'tools'):\n"
             "    assert importlib.util.find_spec(nombre) is None, nombre\n"),
        ], cwd=temporal, env=env)

        proyecto = temporal / "proyecto"
        (proyecto / "catalogos").mkdir(parents=True)
        raiz_perfiles = temporal / "perfiles-host"
        catalogo = raiz_perfiles / "smoke_externo" / "catalogos"
        catalogo.mkdir(parents=True)
        medida = [
            "medida", "demo.instalado",
            ["desde", ["de", "item", "i"]],
            ["resumen", "max", ["doble_instalado", ["campo", "i", "valor"]]],
            ["umbral", "<=", 10, "el smoke test fija un resultado observable"],
            ["alcance", "NO comprueba dominios externos"],
        ]
        (catalogo / "demo.instalado.json").write_text(
            json.dumps(medida), encoding="utf-8")
        (proyecto / "oracle.json").write_text(json.dumps({
            "esquema": "oracle.proyecto/v1",
            "perfiles": ["smoke_externo"],
        }), encoding="utf-8")
        (proyecto / "escalares.py").write_text(
            "from oracle_metalenguaje import escalar\n\n"
            "@escalar('doble_instalado')\n"
            "def doble(valor):\n"
            "    return valor * 2\n",
            encoding="utf-8",
        )
        proyecto_b = temporal / "proyecto-b"
        (proyecto_b / "catalogos").mkdir(parents=True)
        (proyecto_b / "oracle.json").write_text(
            (proyecto / "oracle.json").read_text(encoding="utf-8"), encoding="utf-8")
        (proyecto_b / "escalares.py").write_text(
            "from oracle_metalenguaje import escalar\n\n"
            "@escalar('doble_instalado')\n"
            "def triple(valor):\n"
            "    return valor * 3\n",
            encoding="utf-8",
        )
        proyecto_empaquetado = temporal / "proyecto-empaquetado"
        (proyecto_empaquetado / "catalogos").mkdir(parents=True)
        (proyecto_empaquetado / "oracle.json").write_text(json.dumps({
            "esquema": "oracle.proyecto/v1",
            "perfiles": ["python"],
            "catalogo_base": True,
        }), encoding="utf-8")
        vacio = temporal / "cwd-vacio"
        vacio.mkdir()
        programa = (
            "from oracle_metalenguaje import Motor\n"
            f"motor_a = Motor.desde_proyecto({str(proyecto)!r}, confiar_escalares=True, "
            f"raices_perfiles=({str(raiz_perfiles)!r},))\n"
            f"motor_b = Motor.desde_proyecto({str(proyecto_b)!r}, confiar_escalares=True, "
            f"raices_perfiles=({str(raiz_perfiles)!r},))\n"
            f"motor_empaquetado = Motor.desde_proyecto({str(proyecto_empaquetado)!r})\n"
            "informe_a = motor_a.evaluar({'item': [{'valor': 4}]})\n"
            "informe_b = motor_b.evaluar({'item': [{'valor': 4}]})\n"
            "assert informe_a.ok and informe_a.veredictos[0].valor == 8\n"
            "assert not informe_b.ok and informe_b.veredictos[0].valor == 12\n"
            "assert {medida.id for medida in motor_a.medidas} == {'demo.instalado'}\n"
            "assert {'doble_instalado', 'mas'} <= set(motor_a.escalares)\n"
            "ids = {medida.id for medida in motor_empaquetado.medidas}\n"
            "assert {'meta.toda_medida_esta_fijada', 'proceso.arnes_con_bytecode_frio'} <= ids\n"
        )
        _correr([str(python), "-I", "-c", programa], cwd=vacio, env=env)

        binarios = entorno / ("Scripts" if sys.platform == "win32" else "bin")
        entry_points = (
            "oracle",
            "oracle-aceptacion", "oracle-corpus", "oracle-diferencial", "oracle-estudio",
            "oracle-medida", "oracle-mutar", "oracle-mutar-codigo",
        )
        for nombre in entry_points:
            _correr([str(binarios / nombre), "--help"], cwd=vacio, env=env)
        inventario = _correr([
            str(binarios / "oracle-medida"), "--proyecto", str(proyecto),
            "--confiar-escalares", "--escalares",
        ], cwd=vacio, env=env)
        if "doble_instalado" not in inventario.stdout:
            raise RuntimeError("oracle-medida no cargó la UDF del proyecto externo")
        sin_proyecto = subprocess.run(
            [str(binarios / "oracle-aceptacion")], cwd=vacio,
            env=env, capture_output=True, text=True)
        diagnostico = sin_proyecto.stdout + sin_proyecto.stderr
        if (sin_proyecto.returncode == 0 or "--proyecto" not in diagnostico
                or "Traceback" in diagnostico):
            raise RuntimeError(
                "una instalación sin corpus debe exigir --proyecto: " + diagnostico)

        oracle = binarios / "oracle"
        proyecto_cli = temporal / "proyecto-cli"
        _correr([str(oracle), "init", str(proyecto_cli)], cwd=vacio, env=env)
        vacio_cli = _correr(
            [str(oracle), "test", "--proyecto", str(proyecto_cli)], cwd=vacio, env=env)
        if "VEREDICTO: VERDE" not in vacio_cli.stdout or "proyecto vacío" not in vacio_cli.stdout:
            raise RuntimeError("oracle test no aceptó un proyecto recién inicializado")
        dominio = proyecto_cli / "catalogos" / "demo"
        dominio.mkdir()
        (dominio / "demo.instalado.oracle").write_text(
            "ninguno demo.instalado:\n"
            "    de item i\n"
            "    donde i.mal == true\n"
            "    umbral <= 0 porque \"ningun item malo pasa\"\n"
            "    alcance \"NO ve campos distintos de mal\"\n",
            encoding="utf-8",
        )
        casos = proyecto_cli / "corpus" / "demo"
        casos.mkdir()
        (casos / "001-rojo.caso").write_text(
            "caso 001-rojo:\n"
            "    fecha: \"2026-08-26\"\n"
            "    origen:\n"
            "        repo: \"temporal\"\n"
            "        commit: \"sin-commit\"\n"
            "    titulo: \"item malo detectado\"\n"
            "    etiqueta: falso_verde\n"
            "    sintoma:\n"
            "        Un item malo tiene que poner roja la medida instalada.\n"
            "    como_se_detecto: mutacion\n"
            "    medida: demo.instalado\n"
            "    evidencia:\n"
            "        item: id, mal\n"
            "            \"a\", true\n"
            "    leccion:\n"
            "        La macro estándar tiene que estar empaquetada.\n",
            encoding="utf-8",
        )
        con_macro = _correr(
            [str(oracle), "test", "--proyecto", str(proyecto_cli), "--rapido"],
            cwd=vacio, env=env)
        if "VEREDICTO: VERDE" not in con_macro.stdout:
            raise RuntimeError("oracle test no pudo cargar la macro estándar empaquetada")

    print(
        "WHEEL OK · namespace, datos, 8 entry points, oracle test y dos motores aislados "
        "fuera del checkout"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
