"""Regresiones fail-closed del comando unificado `oracle`."""

from __future__ import annotations

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
from tools import cli

RAIZ = Path(__file__).resolve().parents[1]


class OracleCliTests(unittest.TestCase):
    @staticmethod
    def _callado(fn, *args, **kw):
        """Corre una función del CLI sin dejar su salida en la de la suite.

        Los tests capturaban `cli.main` pero llamaban `cmd_init`, `cmd_nueva` y `cmd_caso` DIRECTO,
        así que la ayuda del comando terminaba mezclada con el resumen de la corrida:
        `python -m unittest -q | tail -3` mostraba «Creá una medida» en vez de «OK». Un test que
        ensucia la salida hace ilegible justo lo que uno mira cuando algo falla.
        """
        salida = io.StringIO()
        with redirect_stdout(salida):
            resultado = fn(*args, **kw)
        return resultado, salida.getvalue()


    def test_ayuda_y_sin_argumentos_devuelven_cero(self) -> None:
        salida_help = io.StringIO()
        with redirect_stdout(salida_help):
            rc_help = cli.main(["--help"])
        self.assertEqual(rc_help, 0)
        self.assertIn("oracle init", salida_help.getvalue())
        self.assertIn("oracle test", salida_help.getvalue())

        salida_vacia = io.StringIO()
        with redirect_stdout(salida_vacia):
            rc_vacia = cli.main([])
        self.assertEqual(rc_vacia, 0)
        self.assertEqual(salida_help.getvalue(), salida_vacia.getvalue())

    def test_init_crea_estructura_valida_y_test_la_acepta(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            destino = Path(td) / "nuevo-proyecto"
            salida_init = io.StringIO()
            with redirect_stdout(salida_init):
                rc_init = cli.main(["init", str(destino)])
            self.assertEqual(rc_init, 0)
            self.assertTrue((destino / "catalogos").is_dir())
            self.assertTrue((destino / "corpus").is_dir())
            self.assertTrue((destino / "diferencial").is_dir())
            self.assertTrue((destino / "oracle.json").is_file())

            # oracle test sobre el proyecto recién inicializado debe ser verde
            salida_test = io.StringIO()
            with redirect_stdout(salida_test):
                rc_test = cli.main(["test", "--proyecto", str(destino)])
            self.assertEqual(rc_test, 0)
            self.assertIn("VEREDICTO: VERDE", salida_test.getvalue())
            self.assertIn("proyecto vacío", salida_test.getvalue())

    def test_test_distingue_no_aplica_de_falla(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])

            # 1. Sin fixtures diferenciales -> no aplica (salteado)
            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main(["test", "--proyecto", str(raiz)])
            self.assertEqual(rc, 0)
            self.assertIn("DIFERENCIAL: salteado", salida.getvalue())

            # 2. Con fixture malformado -> falla
            (raiz / "diferencial" / "roto.json").write_text("{}", encoding="utf-8")
            salida_falla = io.StringIO()
            with redirect_stdout(salida_falla):
                rc_falla = cli.main(["test", "--proyecto", str(raiz)])
            self.assertEqual(rc_falla, 1)
            self.assertIn("DIFERENCIAL ✗", salida_falla.getvalue())
            self.assertIn("VEREDICTO: ROJO", salida_falla.getvalue())

    def test_rapido_saltea_mutacion_y_lo_informa_en_el_veredicto(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])

            # Creamos una medida y un caso válidos
            proy = Proyecto(raiz)
            _, _ = self._callado(cli.cmd_nueva, proy, "demo.prueba")
            medida_path = raiz / "catalogos" / "demo" / "demo.prueba.oracle"
            medida_path.write_text(
                "ninguno demo.prueba:\n"
                "    de item x\n"
                "    donde x.mal == true\n"
                "    umbral <= 0 porque \"ningun item puede estar mal\"\n"
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
            self.assertIn("VEREDICTO: VERDE (rápido: se salteó la mutación)", salida_rapido.getvalue())

    def test_medida_sin_casos_falla_en_test(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])
            proy = Proyecto(raiz)
            _, _ = self._callado(cli.cmd_nueva, proy, "demo.sola")
            (raiz / "catalogos" / "demo" / "demo.sola.oracle").write_text(
                "ninguno demo.sola:\n"
                "    de item x\n"
                "    donde x.mal == true\n"
                "    umbral <= 0 porque \"defensa\"\n"
                "    alcance \"alcance\"\n",
                encoding="utf-8",
            )
            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main(["test", "--proyecto", str(raiz), "--rapido"])
            self.assertEqual(rc, 1)
            self.assertIn("ACEPTACIÓN ✗", salida.getvalue())
            self.assertIn("VEREDICTO: ROJO", salida.getvalue())

    def test_nueva_y_caso_validan_identificadores(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])
            proy = Proyecto(raiz)

            # Identificadores inválidos
            for mid_invalido in ("medida_sin_punto", "MAYUS.nombre", "123.456", "../escape"):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.cmd_nueva(proy, mid_invalido)
                self.assertEqual(rc, 1)

            for cid_invalido in ("sin_grupo", "grupo/sin_numero", "grupo/MAYUS", "grupo/../escape"):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.cmd_caso(proy, cid_invalido)
                self.assertEqual(rc, 1)

    def test_escalares_externas_exigen_confianza_en_test_y_revisar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])
            (raiz / "escalares.py").write_text(
                "from nucleo.algebra import escalar\n"
                "@escalar('es_malo')\n"
                "def es_malo(fila): return fila['mal']\n",
                encoding="utf-8",
            )
            (raiz / "catalogos" / "demo").mkdir(parents=True, exist_ok=True)
            medida_path = raiz / "catalogos" / "demo" / "demo.udf.oracle"
            medida_path.write_text(
                "ninguno demo.udf:\n"
                "    de item x\n"
                "    donde es_malo(x) == true\n"
                "    umbral <= 0 porque \"defensa\"\n"
                "    alcance \"alcance\"\n",
                encoding="utf-8",
            )
            salida_sin = io.StringIO()
            with redirect_stdout(salida_sin):
                rc_sin = cli.main(["test", "--proyecto", str(raiz)])
            self.assertEqual(rc_sin, 1)
            self.assertIn("--confiar-escalares", salida_sin.getvalue())

            salida_con = io.StringIO()
            with redirect_stdout(salida_con):
                rc_con = cli.main([
                    "test", "--proyecto", str(raiz), "--confiar-escalares", "--rapido",
                ])
            self.assertEqual(rc_con, 1)
            self.assertIn("ACEPTACIÓN ✗", salida_con.getvalue())
            self.assertNotIn("CATÁLOGO INVÁLIDO", salida_con.getvalue())

            salida_rev_sin = io.StringIO()
            with redirect_stdout(salida_rev_sin):
                rc_rev_sin = cli.main(["revisar", str(medida_path), "--proyecto", str(raiz)])
            self.assertEqual(rc_rev_sin, 1)
            self.assertIn("--confiar-escalares", salida_rev_sin.getvalue())

    def test_ejecucion_como_subproceso(self) -> None:
        r = subprocess.run(
            [sys.executable, str(RAIZ / "tools" / "cli.py"), "--help"],
            cwd=RAIZ, capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("oracle init", r.stdout)

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

            dominio = proyecto / "catalogos" / "demo"
            dominio.mkdir()
            (dominio / "demo.instalado.oracle").write_text(
                "ninguno demo.instalado:\n"
                "    de item i\n"
                "    donde i.mal == true\n"
                "    umbral <= 0 porque \"ningun item malo pasa\"\n"
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


if __name__ == "__main__":
    unittest.main()
