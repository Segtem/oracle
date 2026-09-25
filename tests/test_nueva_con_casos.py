"""Una medida nueva nace con ambos casos pendientes y no puede dar verde."""

import tempfile
import unittest
from pathlib import Path

from nucleo.proyecto import Proyecto
from tools import cli


class NuevaConCasosTests(unittest.TestCase):
    def test_nueva_crea_rojo_y_verde_marcados_y_test_los_denuncia(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self.assertEqual(cli.cmd_init(str(raiz), []), 0)
            self.assertEqual(cli.cmd_nueva(Proyecto(raiz), "demo.prueba"), 0)
            rojo = raiz / "corpus/demo/001-prueba-rojo.caso"
            verde = raiz / "corpus/demo/002-prueba-verde.caso"
            for ruta, etiqueta in ((rojo, "falso_verde"), (verde, "verde_correcto")):
                self.assertTrue(ruta.is_file(), ruta)
                contenido = ruta.read_text(encoding="utf-8")
                self.assertIn("ANDAMIO", contenido)
                self.assertIn("evidencia:", contenido)
                self.assertIn(f"etiqueta: {etiqueta}", contenido)
                self.assertIn("medida: demo.prueba", contenido)
            (raiz / "catalogos/demo/demo.prueba.oracle").write_text(
                "ninguno demo.prueba:\n"
                "    de item x\n"
                "    donde x.mal == true\n"
                "    umbral <= 0 segun contrato porque \"defensa\"\n"
                "    ambito universal\n"
                "    alcance \"otros items\"\n", encoding="utf-8")
            from contextlib import redirect_stdout
            from io import StringIO
            salida = StringIO()
            with redirect_stdout(salida):
                rc = cli.cmd_test(Proyecto(raiz), ["--rapido"])
            self.assertEqual(rc, 1)
            self.assertIn("ANDAMIO", salida.getvalue())
            self.assertIn("001-prueba-rojo.caso", salida.getvalue())
            self.assertIn("002-prueba-verde.caso", salida.getvalue())
            self.assertIn("VEREDICTO: ROJO", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
