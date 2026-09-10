"""Aceptación y empaquetado de la CLI: integraciones conservadas al final de su perfil de mutación."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

from nucleo.proyecto import Proyecto
from tests import test_cli as _cli_tests
from tools import cli

RAIZ = Path(__file__).resolve().parents[1]


class AceptacionCliTests(_cli_tests.CliTestCase):
    # El escenario y los tests directos de init comparten los mismos datos.
    MEDIDA_INVERTIDA = _cli_tests.InitDejaLasGuardasPuestasTests.MEDIDA_INVERTIDA
    CASO = _cli_tests.InitDejaLasGuardasPuestasTests.CASO

    def test_rapido_saltea_mutacion_y_lo_informa_en_el_veredicto(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])

            # Creamos relación, medida y caso válidos
            (raiz / "relaciones").mkdir(exist_ok=True)
            (raiz / "relaciones" / "item.json").write_text(
                json.dumps([
                    "relacion", "item",
                    ["campos", ["campo", "mal", "booleano", "sin_unidad"]],
                    ["alcance", "sensor de items"]
                ]),
                encoding="utf-8",
            )
            proy = Proyecto(raiz)
            _, _ = self._callado(cli.cmd_nueva, proy, "demo.prueba")
            medida_path = raiz / "catalogos" / "demo" / "demo.prueba.oracle"
            medida_path.write_text(
                "ninguno demo.prueba:\n"
                "    de item x\n"
                "    donde x.mal == true\n"
                "    umbral <= 0 segun contrato porque \"ningun item puede estar mal\"\n"
                "    ambito universal\n"
                "    alcance \"NO ve otros items\"\n",
                encoding="utf-8",
            )
            _, _ = self._callado(cli.cmd_caso, proy, "demo/001-rojo")
            caso_path = raiz / "corpus" / "demo" / "001-rojo.caso"
            caso_path.write_text(
                "caso 001-rojo:\n"
                "    fecha: \"2026-08-26\"\n"
                "    origen:\n"
                "        repo: \"demo\"\n"
                "        commit: \"local\"\n"
                "        comando: \"python3 tools/mide.py\"\n"
                "    procedencia: observada\n"
                "    titulo: \"item defectuoso\"\n"
                "    etiqueta: falso_verde\n"
                "    sintoma:\n"
                "        item mal marcado\n"
                "    como_se_detecto: mutacion\n"
                "    medida: demo.prueba\n"
                "    evidencia:\n"
                "        item: mal\n"
                "            true\n"
                "    leccion:\n"
                "        activa la medida\n",
                encoding="utf-8",
            )

            # Con --rapido: saltea mutación y lo dice en el veredicto
            salida_rapido = io.StringIO()
            with redirect_stdout(salida_rapido):
                rc_rapido = cli.main(["test", "--proyecto", str(raiz), "--rapido"])
            self.assertEqual(rc_rapido, 0)
            self.assertIn("MUTACIÓN: salteada por --rapido", salida_rapido.getvalue())
            self.assertIn(
                "VEREDICTO: VERDE (se salteó: mutación de medidas (--rapido))",
                salida_rapido.getvalue())


    def test_una_medida_invertida_con_su_caso_sale_ROJA(self) -> None:
        """El escenario de auditoría: un modelo escribe una medida al revés y su caso.

        Es la prueba de que una persona puede confiar en el veredicto sin releer cada predicado.
        """
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d) / "nuevo"
            self._callado(cli.cmd_init, str(raiz), [])
            medida = raiz / "catalogos" / "tareas" / "tareas.vencida_sin_dueno.oracle"
            medida.parent.mkdir(parents=True, exist_ok=True)
            medida.write_text(self.MEDIDA_INVERTIDA, encoding="utf-8")
            caso = raiz / "corpus" / "tareas" / "001-vencida-sin-nadie.caso"
            caso.parent.mkdir(parents=True, exist_ok=True)
            caso.write_text(self.CASO, encoding="utf-8")

            codigo, salida = self._callado(cli.main, ["test", "--rapido", "--proyecto", str(raiz)])
            self.assertEqual(codigo, 1, salida)
            self.assertIn("meta.el_caso_se_pone_como_debe", salida)
            self.assertIn("ROJO", salida)


class EmpaquetadoCliTests(unittest.TestCase):
    def test_wheel_instalado_trae_datos_y_ejecuta_oracle_test(self) -> None:
        with tempfile.TemporaryDirectory(prefix="oracle-wheel-test-") as td:
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
            env = os.environ.copy()
            env.pop("ORACLE_PROYECTO", None)
            env.pop("PYTHONPATH", None)
            env["PYTHONDONTWRITEBYTECODE"] = "1"

            # `--no-build-isolation` evita que pip se baje el backend en cada corrida, y a cambio
            # exige que `setuptools` —el que declara `pyproject.toml`— esté en ESTE intérprete.
            # Desde 3.12 un venv ya no lo trae, así que faltar es lo esperable y hay que decirlo en
            # una línea: sin esto, pip lo reporta como cuarenta líneas de traceback terminadas en
            # `BackendUnavailable`, que es lo que tuvo el CI de este repositorio en rojo durante
            # cuatro cortes seguidos sin que nadie leyera hasta el final para ver qué faltaba.
            if importlib.util.find_spec("setuptools") is None:
                self.fail(
                    f"falta `setuptools` en {sys.executable}: es el build-backend que declara "
                    "`pyproject.toml` y este test construye la rueda sin aislamiento. Se instala "
                    'con `python -m pip install "setuptools>=68"`.')

            wheel = subprocess.run(
                [
                    sys.executable, "-m", "pip", "wheel", "--no-deps",
                    "--no-build-isolation", "--wheel-dir", str(ruedas), str(fuente),
                ],
                cwd=temporal, env=env, capture_output=True, text=True,
            )
            self.assertEqual(wheel.returncode, 0, wheel.stdout + wheel.stderr)
            encontradas = tuple(ruedas.glob("oracle_metalenguaje-*.whl"))
            self.assertEqual(len(encontradas), 1, str(encontradas))

            with zipfile.ZipFile(encontradas[0]) as paquete:
                nombres = set(paquete.namelist())
            esperados = {
                "oracle_metalenguaje/tools/cli.py",
                "oracle_metalenguaje/nucleo/aislamiento/escalares.py",
                "oracle_metalenguaje/nucleo/macros/ninguno.oracle",
                "oracle_metalenguaje/nucleo/macros/ninguno-par.oracle",
                "oracle_metalenguaje/nucleo/macros/ninguno-requiere.oracle",
                "oracle_metalenguaje/nucleo/macros/peor.oracle",
                "oracle_metalenguaje/catalogos/meta/meta.toda_medida_esta_fijada.oracle",
                "oracle_metalenguaje/perfiles/python/catalogos/proceso/"
                "proceso.arnes_con_bytecode_frio.oracle",
            }
            self.assertFalse(esperados - nombres)
            genericos = ("nucleo/", "catalogos/", "perfiles/", "tools/")
            self.assertFalse([nombre for nombre in nombres if nombre.startswith(genericos)])

            entorno = temporal / "entorno"
            venv.EnvBuilder(with_pip=True).create(entorno)
            python = entorno / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
            instalar = subprocess.run(
                [str(python), "-m", "pip", "install", "--no-deps", str(encontradas[0])],
                cwd=temporal, env=env, capture_output=True, text=True,
            )
            self.assertEqual(instalar.returncode, 0, instalar.stdout + instalar.stderr)

            binarios = entorno / ("Scripts" if sys.platform == "win32" else "bin")
            oracle = binarios / ("oracle.exe" if sys.platform == "win32" else "oracle")
            cwd_vacio = temporal / "cwd-vacio"
            cwd_vacio.mkdir()
            proyecto = temporal / "proyecto"

            init = subprocess.run(
                [str(oracle), "init", str(proyecto)],
                cwd=cwd_vacio, env=env, capture_output=True, text=True,
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            vacio = subprocess.run(
                [str(oracle), "test", "--proyecto", str(proyecto)],
                cwd=cwd_vacio, env=env, capture_output=True, text=True,
            )
            self.assertEqual(vacio.returncode, 0, vacio.stdout + vacio.stderr)
            self.assertIn("VEREDICTO: VERDE", vacio.stdout)
            self.assertIn("proyecto vacío", vacio.stdout)

            rels = proyecto / "relaciones"
            rels.mkdir()
            (rels / "item.json").write_text(
                json.dumps([
                    "relacion", "item",
                    ["campos",
                     ["campo", "id", "texto", "sin_unidad"],
                     ["campo", "mal", "booleano", "sin_unidad"]],
                    ["alcance", "sensor de items"]
                ]),
                encoding="utf-8",
            )
            dominio = proyecto / "catalogos" / "demo"
            dominio.mkdir()
            (dominio / "demo.instalado.oracle").write_text(
                "ninguno demo.instalado:\n"
                "    de item i\n"
                "    donde i.mal == true\n"
                "    umbral <= 0 segun contrato porque \"ningun item malo pasa\"\n"
                "    ambito universal\n"
                "    alcance \"NO ve campos distintos de mal\"\n",
                encoding="utf-8",
            )
            casos = proyecto / "corpus" / "demo"
            casos.mkdir()
            (casos / "001-rojo.caso").write_text(
                "caso 001-rojo:\n"
                "    fecha: \"2026-08-26\"\n"
                "    origen:\n"
                "        repo: \"temporal\"\n"
                "        commit: \"sin-commit\"\n"
                "        comando: \"python3 tools/mide.py\"\n"
                "    procedencia: observada\n"
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
            con_macro = subprocess.run(
                [str(oracle), "test", "--proyecto", str(proyecto), "--rapido"],
                cwd=cwd_vacio, env=env, capture_output=True, text=True,
            )
            self.assertEqual(con_macro.returncode, 0, con_macro.stdout + con_macro.stderr)
            self.assertIn("SINTAXIS OK", con_macro.stdout)
            self.assertIn("ACEPTACIÓN", con_macro.stdout)
            self.assertIn("VEREDICTO: VERDE", con_macro.stdout)

