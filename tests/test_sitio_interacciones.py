"""El JavaScript publicado conserva el copiado y el menú entre anchos de pantalla."""
import shutil
import subprocess
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


class InteraccionesWebTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node no está instalado; pruebas JS omitidas")
    def test_interacciones_del_html_publicado(self):
        # V8 sin JIT evita reservar CodeRange fuera del límite de memoria del arnés.
        corrida = subprocess.run(
            ["node", "--jitless", "tests/js/sitio_interacciones.cjs"],
            cwd=RAIZ, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(corrida.returncode, 0, corrida.stdout + corrida.stderr)
