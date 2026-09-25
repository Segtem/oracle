"""El recorrido de cero se puede reproducir desde una carpeta vacía."""

import unittest

from tools import guia


class GuiaTests(unittest.TestCase):
    def test_bloques_y_salidas_reales(self):
        guia.verificar()
