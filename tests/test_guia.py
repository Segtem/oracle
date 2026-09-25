"""Los recorridos se pueden reproducir desde una carpeta vacía."""

import unittest

from tools import guia


class GuiaTests(unittest.TestCase):
    def test_bloques_y_salidas_reales(self):
        for ruta in guia.GUIAS:
            with self.subTest(guia=ruta.name):
                guia.verificar(guia=ruta)
