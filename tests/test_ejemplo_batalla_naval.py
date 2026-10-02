"""El juego incluido conserva su corpus y su partida de referencia."""

import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


RAIZ = Path(__file__).resolve().parents[1]
EJEMPLO = RAIZ / "ejemplo" / "batalla-naval"


class BatallaNavalTests(unittest.TestCase):
    def test_oracle_test_del_ejemplo_es_verde(self):
        corrida = subprocess.run(
            [sys.executable, str(RAIZ / "tools" / "cli.py"), "test",
             "--proyecto", str(EJEMPLO)],
            cwd=RAIZ, capture_output=True, text=True,
        )
        self.assertEqual(corrida.returncode, 0, corrida.stdout + corrida.stderr)
        self.assertIn("VEREDICTO: VERDE", corrida.stdout)
        self.assertIn("sobrevivieron 0", corrida.stdout)

    def test_verificador_juzga_la_partida_guardada(self):
        corrida = subprocess.run(
            [sys.executable, str(EJEMPLO / "verificar_oraculo.py")],
            cwd=RAIZ, capture_output=True, text=True,
        )
        self.assertEqual(corrida.returncode, 0, corrida.stdout + corrida.stderr)
        self.assertIn("Leída de partida_real.json", corrida.stdout)
        self.assertIn("VEREDICTO: verde en 11 medidas", corrida.stdout)

    def test_verificador_acepta_el_nombre_de_partida_de_la_guia(self):
        with tempfile.TemporaryDirectory() as tmp:
            proyecto = Path(tmp) / "batalla-naval"
            shutil.copytree(EJEMPLO, proyecto, ignore=shutil.ignore_patterns("__pycache__"))
            (proyecto / "partida_real.json").rename(proyecto / "hechos_partida.json")
            spec = importlib.util.spec_from_file_location("verificador_naval", proyecto / "verificar_oraculo.py")
            verificador = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(verificador)
            salida = io.StringIO()
            with patch.object(verificador, "CLI", RAIZ / "tools/cli.py"), contextlib.redirect_stdout(salida):
                verificador.main()
            self.assertIn("Leída de hechos_partida.json", salida.getvalue())
            self.assertIn("VEREDICTO: verde en 11 medidas", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
