"""Tests para la mutación de código por niveles, paralelismo (-j N) y selección de tests."""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from perfiles.python.mutacion_codigo import correr, _comando_para_tests_seleccionados
import tools.mutar_codigo as mc


class GitReposTemporalesTests(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self._iniciar_repo()

    def _iniciar_repo(self):
        mc._git(self.raiz, "init")
        mc._git(self.raiz, "config", "user.name", "Test Oracle")
        mc._git(self.raiz, "config", "user.email", "test@oracle.local")
        mc._git(self.raiz, "config", "commit.gpgsign", "false")

    def test_ultimo_tag_sin_tags(self):
        (self.raiz / "archivo.py").write_text("x = 1\n", encoding="utf-8")
        mc._git(self.raiz, "add", "archivo.py")
        mc._git(self.raiz, "commit", "-m", "commit inicial")
        with self.assertRaises(ValueError) as ctx:
            mc.ultimo_tag(self.raiz)
        self.assertIn("tag", str(ctx.exception).lower())

    def test_ultimo_tag_con_tags(self):
        (self.raiz / "archivo.py").write_text("x = 1\n", encoding="utf-8")
        mc._git(self.raiz, "add", "archivo.py")
        mc._git(self.raiz, "commit", "-m", "commit inicial")
        mc._git(self.raiz, "tag", "v0.1.0")
        self.assertEqual(mc.ultimo_tag(self.raiz), "v0.1.0")

        (self.raiz / "archivo.py").write_text("x = 2\n", encoding="utf-8")
        mc._git(self.raiz, "commit", "-am", "segundo commit")
        mc._git(self.raiz, "tag", "v0.2.0")
        self.assertEqual(mc.ultimo_tag(self.raiz), "v0.2.0")

    def test_lineas_cambiadas_git(self):
        lineas = [f"val_{i} = {i}\n" for i in range(1, 11)]
        (self.raiz / "mod.py").write_text("".join(lineas), encoding="utf-8")
        mc._git(self.raiz, "add", "mod.py")
        mc._git(self.raiz, "commit", "-m", "version base")
        mc._git(self.raiz, "tag", "v1.0.0")

        # Modificación local (sin commitear) en líneas 3 y 7
        lineas[2] = "val_3 = 999\n"
        lineas[6] = "val_7 = 777\n"
        (self.raiz / "mod.py").write_text("".join(lineas), encoding="utf-8")

        cambios_head = mc.lineas_cambiadas_git(self.raiz, ref=None)
        self.assertEqual(cambios_head, {"mod.py": {3, 7}})

        cambios_tag = mc.lineas_cambiadas_git(self.raiz, ref="v1.0.0")
        self.assertEqual(cambios_tag, {"mod.py": {3, 7}})

        # Commitear y agregar nueva línea al final (línea 11)
        mc._git(self.raiz, "commit", "-am", "modificar 3 y 7")
        (self.raiz / "mod.py").write_text("".join(lineas) + "val_11 = 11\n", encoding="utf-8")

        cambios_head_despues = mc.lineas_cambiadas_git(self.raiz, ref=None)
        self.assertEqual(cambios_head_despues, {"mod.py": {11}})

        cambios_tag_despues = mc.lineas_cambiadas_git(self.raiz, ref="v1.0.0")
        self.assertEqual(cambios_tag_despues, {"mod.py": {3, 7, 11}})

    def test_modulos_cambiados_git(self):
        (self.raiz / "mod1.py").write_text("a = 1\n", encoding="utf-8")
        mc._git(self.raiz, "add", "mod1.py")
        mc._git(self.raiz, "commit", "-m", "tag base")
        mc._git(self.raiz, "tag", "v0.1.0")

        (self.raiz / "mod2.py").write_text("b = 2\n", encoding="utf-8")
        mc._git(self.raiz, "add", "mod2.py")
        mc._git(self.raiz, "commit", "-m", "agrega mod2")

        cambiados = mc.modulos_cambiados_git(self.raiz, "v0.1.0")
        self.assertEqual(cambiados, ["mod2.py"])


class OpcionesYNivelesValidacionTests(unittest.TestCase):
    def test_paralelo_invalido(self):
        args = mc.argumentos(["-j", "0"])
        with self.assertRaises(ValueError) as ctx:
            mc.validar_argumentos(args)
        self.assertIn("--paralelo", str(ctx.exception))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(mc._ejecutar(None, args), 2)

    def test_niveles_mutuamente_excluyentes(self):
        combinaciones = [
            ["--bajo", "--medio"],
            ["--alto", "--muy-alto"],
            ["--bajo", "--alto"],
            ["--medio", "--muy-alto"],
            ["--bajo", "--medio", "--alto", "--muy-alto"],
        ]
        for combo in combinaciones:
            with self.subTest(combo=combo):
                args = mc.argumentos(combo)
                with self.assertRaises(ValueError) as ctx:
                    mc.validar_argumentos(args)
                self.assertIn("mutuamente excluyentes", str(ctx.exception))
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(mc._ejecutar(None, args), 2)

    def test_niveles_con_lineas_o_sitio(self):
        casos = [
            ["--bajo", "--lineas", "1-5"],
            ["--medio", "--sitio", "nucleo/algebra.py:10:5:+"],
            ["--alto", "--lineas", "20"],
            ["--muy-alto", "--sitio", "nucleo/algebra.py:10:5:+"],
        ]
        for caso in casos:
            with self.subTest(caso=caso):
                args = mc.argumentos(caso)
                with self.assertRaises(ValueError) as ctx:
                    mc.validar_argumentos(args)
                self.assertIn("no se puede combinar", str(ctx.exception))
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(mc._ejecutar(None, args), 2)

    def test_niveles_alto_y_muy_alto_rechazan_objetivo(self):
        for nivel in ("--alto", "--muy-alto"):
            with self.subTest(nivel=nivel):
                args = mc.argumentos([nivel, "--objetivo", "nucleo/algebra.py"])
                with self.assertRaises(ValueError) as ctx:
                    mc.validar_argumentos(args)
                self.assertIn("no admite --objetivo", str(ctx.exception))
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(mc._ejecutar(None, args), 2)

    def test_nivel_alto_sin_modulos_cambiados(self):
        args = mc.argumentos(["--alto", "--hechos"])
        with patch.object(mc, "ultimo_tag", return_value="v1.0.0"), \
             patch.object(mc, "modulos_cambiados_git", return_value=["inexistente.txt"]), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            codigo = mc._ejecutar(None, args)
            self.assertEqual(codigo, 2)
            datos = json.loads(out.getvalue())
            self.assertIn("error_mutacion", datos)
            self.assertIn("ningún módulo del perfil cambió", datos["error_mutacion"][0]["mensaje"])


class ParalelismoTests(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)

        # Miniproyecto de juguete con archivo calculo.py y test_calculo.py
        codigo = (
            "def calcular(a, b):\n"
            "    x = a + b\n"
            "    y = a - b\n"
            "    z = a * b\n"
            "    return x > y\n"
        )
        (self.raiz / "calculo.py").write_text(codigo, encoding="utf-8")

        test_codigo = (
            "import unittest\n"
            "import calculo\n"
            "\n"
            "class TestCalculo(unittest.TestCase):\n"
            "    def test_op(self):\n"
            "        self.assertTrue(calculo.calcular(10, 5))\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        )
        (self.raiz / "test_calculo.py").write_text(test_codigo, encoding="utf-8")
        self.comando_tests = [sys.executable, "-B", "-m", "unittest", "test_calculo.py"]

    def test_paralelismo_consistencia_j_n_vs_j_1(self):
        # Correr con -j 1
        evidencia_1 = correr(
            self.raiz,
            [self.raiz / "calculo.py"],
            self.comando_tests,
            equivalentes={},
            paralelo=1,
            limite_memoria=None,
        )

        # Correr con -j 2 y -j 4
        for p in (2, 4):
            with self.subTest(paralelo=p):
                evidencia_p = correr(
                    self.raiz,
                    [self.raiz / "calculo.py"],
                    self.comando_tests,
                    equivalentes={},
                    paralelo=p,
                    limite_memoria=None,
                )

                # Comparar orden y estados de los mutantes
                mutantes_1 = evidencia_1["mutante"]
                mutantes_p = evidencia_p["mutante"]
                self.assertEqual(len(mutantes_1), len(mutantes_p))
                self.assertGreater(len(mutantes_1), 0)

                for m1, mp in zip(mutantes_1, mutantes_p):
                    self.assertEqual(m1["id"], mp["id"])
                    self.assertEqual(m1["estado"], mp["estado"])
                    self.assertEqual(m1["tests_fallaron"], mp["tests_fallaron"])

                # Comparar estadísticas globales de la corrida
                c1 = evidencia_1["corrida_mutacion"][0]
                cp = evidencia_p["corrida_mutacion"][0]
                self.assertEqual(c1["baseline_verde"], cp["baseline_verde"])
                self.assertEqual(c1["mutantes"], cp["mutantes"])
                self.assertEqual(c1["errores_arnes"], cp["errores_arnes"])
                self.assertEqual(c1["timeouts"], cp["timeouts"])


class SeleccionTests(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)

        codigo = (
            "def fn(a, b):\n"
            "    return a > b\n"
        )
        (self.raiz / "logica.py").write_text(codigo, encoding="utf-8")

    def test_comando_para_tests_seleccionados(self):
        cmd = [sys.executable, "tools/ejecutar_suite_mutacion.py"]
        copia = self.raiz
        tests = {"tests.test_a.TestA.test_1", "tests.test_b.TestB.test_2"}
        nuevo_cmd = _comando_para_tests_seleccionados(cmd, copia, tests)
        self.assertIsNotNone(nuevo_cmd)
        self.assertIn("--solo-prioridad", nuevo_cmd)
        self.assertIn("--prioridad", nuevo_cmd)
        self.assertIn("tests.test_a.TestA.test_1", nuevo_cmd)
        self.assertIn("tests.test_b.TestB.test_2", nuevo_cmd)

    def test_seleccion_nunca_declara_vivo_lo_que_suite_mata(self):
        """Demuestra que todo mutante que la suite entera mata es declarado muerto,

        incluso si los tests seleccionados fallan, pasan o están ausentes.
        """
        # Runner simulado estructurado como ejecutar_suite_mutacion.py
        tools_dir = self.raiz / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        runner_script = tools_dir / "ejecutar_suite_mutacion.py"

        # Comportamiento del runner simulado:
        # - Código original (línea base): sale 0.
        # - Mutante en fase de selección (--solo-prioridad):
        #     si alguna --prioridad contiene 'mata', sale 1; si no, sale 0.
        # - Mutante en suite completa (sin --solo-prioridad):
        #     siempre sale 1 (la suite completa lo mata).
        runner_script.write_text(
            "import sys\n"
            "from pathlib import Path\n"
            "argv = sys.argv[1:]\n"
            "contenido = Path('logica.py').read_text(encoding='utf-8')\n"
            "if 'return a > b' in contenido:\n"
            "    sys.exit(0)\n"
            "if '--solo-prioridad' in argv:\n"
            "    for i, arg in enumerate(argv):\n"
            "        if arg == '--prioridad' and i + 1 < len(argv):\n"
            "            if 'mata' in argv[i + 1]:\n"
            "                sys.exit(1)\n"
            "    sys.exit(0)\n"
            "sys.exit(1)\n",
            encoding="utf-8",
        )
        cmd = [sys.executable, str(runner_script)]

        # Caso A: Mapa con test que mata directamente en la selección
        mapa_a = {"logica.py": {"2": {"test_mata"}}}
        ev_a = correr(self.raiz, [self.raiz / "logica.py"], cmd, {}, mapa_cobertura=mapa_a)
        self.assertGreater(len(ev_a["mutante"]), 0)
        for m in ev_a["mutante"]:
            self.assertTrue(m["tests_fallaron"])
            self.assertEqual(m["estado"], "tests_fallaron")

        # Caso B: Mapa con test que pasa (no mata), pero la suite completa sí mata
        mapa_b = {"logica.py": {"2": {"test_pasa"}}}
        ev_b = correr(self.raiz, [self.raiz / "logica.py"], cmd, {}, mapa_cobertura=mapa_b)
        self.assertGreater(len(ev_b["mutante"]), 0)
        for m in ev_b["mutante"]:
            self.assertTrue(m["tests_fallaron"])
            self.assertEqual(m["estado"], "tests_fallaron")

        # Caso C: Mapa vacío para esa línea; la suite entera lo mata
        mapa_c = {"logica.py": {}}
        ev_c = correr(self.raiz, [self.raiz / "logica.py"], cmd, {}, mapa_cobertura=mapa_c)
        self.assertGreater(len(ev_c["mutante"]), 0)
        for m in ev_c["mutante"]:
            self.assertTrue(m["tests_fallaron"])
            self.assertEqual(m["estado"], "tests_fallaron")


if __name__ == "__main__":
    unittest.main()
