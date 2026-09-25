"""El juego incluido conserva su corpus y su partida de referencia."""

import subprocess
import sys
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
