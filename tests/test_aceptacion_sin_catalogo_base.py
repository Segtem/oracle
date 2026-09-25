"""Un caso que no se pone como declara tumba la aceptación también sin catálogo base.

Hasta 0.31.0 el juicio de cada caso lo daba sólo `meta.el_caso_se_pone_como_debe`, que vive en el
catálogo base. Con `"catalogo_base": false` —el proyecto de la guía de la batalla naval— el caso se
descartaba sin aviso y `oracle test` salía VERDE.
"""

import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nucleo.proyecto import Proyecto
from tools import cli

NAVAL = Path(__file__).resolve().parents[1] / "ejemplo" / "batalla-naval"


class CasoMalEtiquetado(unittest.TestCase):
    def test_cada_polaridad_invertida_pone_rojo(self):
        for archivo, de, a in (("005-barco-fila-desbordada.caso", "falso_verde", "verde_correcto"),
                               ("006-barco-en-borde.caso", "verde_correcto", "falso_verde")):
            with self.subTest(caso=archivo), tempfile.TemporaryDirectory() as td:
                raiz = Path(td) / "naval"
                shutil.copytree(NAVAL, raiz)
                caso = raiz / "corpus" / "naval" / archivo
                texto = caso.read_text(encoding="utf-8")
                self.assertIn(f"etiqueta: {de}", texto)
                caso.write_text(texto.replace(f"etiqueta: {de}", f"etiqueta: {a}"), encoding="utf-8")
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.cmd_test(Proyecto(raiz), ["--rapido"])
                self.assertEqual(rc, 1, salida.getvalue())
                self.assertIn(f"FALLA {archivo[:-5]}", salida.getvalue())
                self.assertIn("VEREDICTO: ROJO (falló: aceptación)", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
