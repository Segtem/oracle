"""Suites testigo programadas para el protocolo del runner bajo prueba."""

import subprocess
import sys
import tempfile
import unittest
import contextlib
import io
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

RUTA_RUNNER = Path(__file__).resolve().parents[1] / "tools" / "ejecutar_suite_mutacion.py"


class ProtocoloRunner(unittest.TestCase):
    def ejecutar(self, archivos, *argumentos):
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            tests = raiz / "tests"
            tests.mkdir()
            (tests / "__init__.py").write_text("", encoding="utf-8")
            for nombre, fuente in archivos.items():
                (tests / nombre).write_text(fuente, encoding="utf-8")
            salida = subprocess.run(
                [sys.executable, str(RUTA_RUNNER), "--tope", str(raiz),
                 "--inicio", str(tests), *argumentos], cwd=raiz,
                text=True, capture_output=True, timeout=10)
            return salida, raiz

    def test_exito(self):
        salida, _ = self.ejecutar({"test_exito.py": "import unittest\nclass Caso(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n"})
        self.assertEqual(salida.returncode, 0, salida.stderr)
        self.assertIn("Ran 1 test", salida.stderr)
        self.assertNotIn("test_ok (", salida.stderr)

    def test_solo_prioridad(self):
        salida, _ = self.ejecutar({"test_exito.py": "import unittest\nclass Caso(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n"},
                                 "--prioridad", "tests.test_exito", "--solo-prioridad")
        self.assertEqual(salida.returncode, 0, salida.stderr)
        self.assertEqual(salida.stderr.count("Ran 1 test"), 1)
        vacia, _ = self.ejecutar({}, "--solo-prioridad")
        self.assertEqual(vacia.returncode, 2, vacia.stderr)

    def test_fallo_y_excepcion(self):
        for cuerpo in ("self.assertEqual(1, 2)", "raise RuntimeError('previsto')"):
            with self.subTest(cuerpo=cuerpo):
                salida, _ = self.ejecutar({"test_fallo.py":
                    f"import unittest\nclass Caso(unittest.TestCase):\n def test_falla(self): {cuerpo}\n"})
                self.assertEqual(salida.returncode, 1, salida.stderr)

    def test_exito_inesperado(self):
        salida, _ = self.ejecutar({"test_exito.py":
            "import unittest\nclass Caso(unittest.TestCase):\n @unittest.expectedFailure\n def test_ok(self): self.assertTrue(True)\n"})
        self.assertEqual(salida.returncode, 1, salida.stderr)

    def test_prioridad_fallida_detiene_descubrimiento(self):
        with tempfile.TemporaryDirectory() as d:
            # El test general deja una marca fuera de la suite efímera.
            marca = Path(d) / "marca"
            fuente = f"import unittest\nfrom pathlib import Path\nclass Caso(unittest.TestCase):\n def test_general(self): Path({str(marca)!r}).write_text('ejecutado')\n"
            salida, _ = self.ejecutar({
                "test_prioritario.py": "import unittest\nclass Caso(unittest.TestCase):\n def test_falla(self): self.fail('previsto')\n",
                "test_general.py": fuente}, "--prioridad", "tests.test_prioritario")
            self.assertEqual(salida.returncode, 1, salida.stderr)
            self.assertFalse(marca.exists())

    def test_prioridad_exitosa_continua_y_no_duplica(self):
        salida, _ = self.ejecutar({
            "test_prioritario.py": "import unittest\nclass Caso(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n",
            "test_general.py": "import unittest\nclass Caso(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n"},
            "--prioridad", "tests.test_prioritario")
        self.assertEqual(salida.returncode, 0, salida.stderr)
        self.assertEqual(salida.stderr.count("Ran 1 test"), 2, salida.stderr)

    def test_failfast(self):
        salida, _ = self.ejecutar({"test_fallos.py":
            "import unittest\nclass Caso(unittest.TestCase):\n def test_a(self): self.fail('primero')\n def test_b(self): self.fail('segundo')\n"})
        self.assertEqual(salida.returncode, 1, salida.stderr)
        self.assertIn("Ran 1 test", salida.stderr)
        self.assertNotIn("segundo", salida.stderr)

    def test_error_prioritario(self):
        salida, _ = self.ejecutar({}, "--prioridad", "tests.inexistente")
        self.assertEqual(salida.returncode, 2, salida.stderr)

    def test_sintaxis_invalida(self):
        salida, _ = self.ejecutar({"test_roto.py": "def !\n"})
        self.assertEqual(salida.returncode, 2, salida.stderr)

    def test_cero_tests(self):
        salida, _ = self.ejecutar({})
        self.assertEqual(salida.returncode, 2, salida.stderr)

    def test_system_exit_en_descubrimiento(self):
        salida, _ = self.ejecutar({"test_salida.py": "raise SystemExit(0)\n"})
        self.assertEqual(salida.returncode, 2, salida.stderr)

    def test_excepcion_en_descubrimiento(self):
        salida, _ = self.ejecutar({"test_roto.py": "raise RuntimeError('importación')\n"})
        self.assertEqual(salida.returncode, 2, salida.stderr)

    def test_filtro_de_prioritarios(self):
        from tools import ejecutar_suite_mutacion as runner

        class Caso(unittest.TestCase):
            def runTest(self):
                pass

        prioritario = Caso()
        general = Caso()
        with patch.object(prioritario, "id", return_value="tests.prioridad.Caso.runTest"), \
             patch.object(general, "id", return_value="tests.general.Caso.runTest"):
            suite = unittest.TestSuite([unittest.TestSuite([prioritario]), general])
            filtrada = runner._sin_modulos(suite, ["tests.prioridad"])
            self.assertEqual([caso.id() for caso in filtrada], ["tests.general.Caso.runTest"])
            self.assertEqual(len(list(runner._sin_modulos(suite, []))), 2)

    def test_excepciones_del_descubridor(self):
        from tools import ejecutar_suite_mutacion as runner
        for error in (SystemExit(0), RuntimeError("previsto")):
            with self.subTest(error=error), patch.object(runner.unittest.TestLoader, "discover", side_effect=error):
                self.assertEqual(runner.main(["--inicio", "tests"]), 2)

    def test_main_retorna_entero_en_exito_y_prioridad(self):
        from tools import ejecutar_suite_mutacion as runner
        suite = unittest.TestSuite([unittest.FunctionTestCase(lambda: None)])
        with patch.object(runner.unittest.TestLoader, "loadTestsFromName", return_value=suite):
            self.assertEqual(runner.main(["--prioridad", "tests.falsa", "--solo-prioridad"]), 0)
        with patch.object(runner.unittest.TestLoader, "discover", return_value=unittest.TestSuite([
                unittest.FunctionTestCase(lambda: None)])):
            self.assertEqual(runner.main([]), 0)

    def test_tope_se_inserta_primero(self):
        from tools import ejecutar_suite_mutacion as runner
        with tempfile.TemporaryDirectory() as d, patch.object(runner.sys, "path", ["ruta-previa"]), \
             patch.object(runner.unittest.TestLoader, "loadTestsFromName", return_value=unittest.TestSuite([
                 unittest.FunctionTestCase(lambda: None)])):
            self.assertEqual(runner.main(["--tope", d, "--prioridad", "tests.falsa",
                                          "--solo-prioridad"]), 0)
            self.assertEqual(runner.sys.path[0], str(Path(d).resolve()))

    def test_errores_del_loader_prioritario_y_diagnostico_primero(self):
        from tools import ejecutar_suite_mutacion as runner
        cargador = SimpleNamespace(errors=["primer error", "segundo error"],
                                   loadTestsFromName=lambda nombre: unittest.TestSuite([
                                       unittest.FunctionTestCase(lambda: None)]))
        salida = io.StringIO()
        with patch.object(runner.unittest, "TestLoader", return_value=cargador), \
             contextlib.redirect_stderr(salida):
            self.assertEqual(runner.main(["--prioridad", "tests.falsa", "--solo-prioridad"]), 2)
        self.assertIn("primer error", salida.getvalue())
        self.assertNotIn("segundo error", salida.getvalue())

    def test_errores_del_loader_en_descubrimiento(self):
        from tools import ejecutar_suite_mutacion as runner
        cargador = SimpleNamespace(errors=["primer error", "segundo error"],
                                   discover=lambda **_kw: unittest.TestSuite([
                                       unittest.FunctionTestCase(lambda: None)]))
        salida = io.StringIO()
        with patch.object(runner.unittest, "TestLoader", return_value=cargador), \
             contextlib.redirect_stderr(salida):
            self.assertEqual(runner.main([]), 2)
        self.assertIn("primer error", salida.getvalue())
        self.assertNotIn("segundo error", salida.getvalue())

    def test_fallo_de_importacion_sin_errors_del_loader(self):
        from tools import ejecutar_suite_mutacion as runner
        fallido = unittest.loader._FailedTest("test_roto", ImportError("previsto"))
        resultado = SimpleNamespace(testsRun=1, errors=[(fallido, "previsto")],
                                    failures=[], unexpectedSuccesses=[])
        with patch.object(runner.unittest.TestLoader, "discover", return_value=unittest.TestSuite()), \
             patch.object(runner, "_correr_suite", return_value=resultado):
            self.assertEqual(runner.main([]), 2)

    def test_resultado_no_exitoso_sin_fallos_reportados(self):
        from tools import ejecutar_suite_mutacion as runner
        resultado = SimpleNamespace(testsRun=1, errors=[], failures=[],
                                    unexpectedSuccesses=[], wasSuccessful=lambda: False)
        with patch.object(runner.unittest.TestLoader, "discover", return_value=unittest.TestSuite()), \
             patch.object(runner, "_correr_suite", return_value=resultado):
            self.assertEqual(runner.main([]), 2)


if __name__ == "__main__":
    unittest.main()
