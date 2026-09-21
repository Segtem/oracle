"""Ejecuta el recorrido documentado sobre una copia limpia del producto."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


RAIZ = Path(__file__).resolve().parents[1]


class PrimerValorTests(unittest.TestCase):
    def test_catalogo_y_corridas_reales(self):
        with tempfile.TemporaryDirectory(prefix="oracle-primer-valor-") as td:
            cwd = Path(td)
            proyecto = cwd / "ejemplo" / "primer-valor"
            shutil.copytree(RAIZ / "ejemplo" / "primer-valor", proyecto)
            env = os.environ.copy()
            env.pop("ORACLE_PROYECTO", None)
            env.pop("PYTHONPATH", None)

            def ejecutar(args, codigo=0):
                resultado = subprocess.run(
                    [sys.executable, *map(str, args)], cwd=cwd, env=env,
                    capture_output=True, text=True, timeout=60,
                )
                self.assertEqual(resultado.returncode, codigo,
                                 resultado.stdout + resultado.stderr)
                return resultado.stdout

            cli = RAIZ / "tools" / "cli.py"
            salida = ejecutar([cli, "test", "--proyecto", proyecto])
            self.assertIn("VEREDICTO: VERDE", salida)
            self.assertIn("sobrevivieron 0", salida)
            hechos = cwd / "hechos.json"
            producto = proyecto / "colocador.py"
            ejecutar([producto, "--defecto", "--exportar", hechos])
            defecto = json.loads(hechos.read_text())
            self.assertEqual(len(defecto["celda_ocupada"]), 5)
            self.assertIn({"barco": "destructor", "fila": 10, "columna": 5},
                          defecto["celda_ocupada"])
            juzgar = [cli, "juzgar", "--proyecto", proyecto, "--con", hechos]
            salida = ejecutar(juzgar, 1)
            self.assertIn("'fila': 10", salida)
            self.assertIn("1 de 1 medidas en rojo", salida)
            # Volver a juzgar evidencia guardada conserva el defecto.
            ejecutar(juzgar, 1)
            ejecutar([producto, "--exportar", hechos])
            corregido = json.loads(hechos.read_text())
            self.assertNotEqual(defecto, corregido)
            self.assertEqual(len(corregido["celda_ocupada"]), 5)
            self.assertTrue(all(0 <= c["fila"] < 10 and 0 <= c["columna"] < 10
                                for c in corregido["celda_ocupada"]))
            salida = ejecutar(juzgar)
            self.assertIn("verde en 1 medidas. SIN MIRAR:", salida)
            self.assertIn("NO ve si los buques tienen la longitud declarada", salida)
