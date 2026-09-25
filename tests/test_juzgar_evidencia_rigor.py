"""Lo que `oracle juzgar` acepta y cómo resume lo que falla, contra la especificación."""

import json
import tempfile
import unittest
from pathlib import Path

from nucleo import medida as m
from tools import juzgar


class ClaveEnLaEvidencia(unittest.TestCase):
    def _leer(self, datos):
        with tempfile.TemporaryDirectory() as td:
            ruta = Path(td) / "hechos.json"
            ruta.write_text(json.dumps(datos), encoding="utf-8")
            return juzgar._leer_evidencia(str(ruta))

    def test_la_cabecera_clave_llega_al_nucleo(self):
        # ESPECIFICACION §1: un nodo ["clave", [...]] a la cabeza declara la unicidad.
        datos = {"a": [["clave", ["id"]], {"id": 1}]}
        self.assertEqual(self._leer(datos), (datos, None))

    def test_una_lista_que_no_es_la_cabecera_sigue_rechazada(self):
        for filas in ([{"id": 1}, ["clave", ["id"]]], [["otra", ["id"]]], [[1, 2]]):
            with self.subTest(filas=filas):
                datos, error = self._leer({"a": filas})
                self.assertIsNone(datos)
                self.assertIn("debe ser un objeto", error)


class ResumenDeLoQueFalla(unittest.TestCase):
    def test_sin_evidencia_no_se_cuenta_como_rojo(self):
        rojo = m.Veredicto("d.rojo", 1, False, "<= 0", "razón", "alcance", ())
        vacio = m.Veredicto("d.vacio", 0, False, "<= 0", "razón", "alcance", (), sin_evidencia="a")
        verde = m.Veredicto("d.verde", 0, True, "<= 0", "razón", "alcance", ())
        self.assertEqual(m.partes_de_lo_que_falla((rojo, vacio), 3),
                         ["1 de 3 medidas en rojo", "1 de 3 sin evidencia (no se midieron)"])
        self.assertEqual(m.partes_de_lo_que_falla((vacio,), 2),
                         ["1 de 2 sin evidencia (no se midieron)"])
        self.assertIn("VEREDICTO: 1 de 2 sin evidencia (no se midieron)",
                      m.Informe((vacio, verde)).texto())


if __name__ == "__main__":
    unittest.main()
