"""Contrato de la guía con dos pasos aislados, sin ejecutar sus recorridos largos."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import guia


class GuiaMinimaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        self.parche_raiz = patch.object(guia, "RAIZ", self.raiz)
        self.parche_raiz.start()
        self.addCleanup(self.parche_raiz.stop)
        self.guia = self.raiz / "dos-pasos.md"
        (self.raiz / "saludar.py").write_text("print('hola')\n", encoding="utf-8")
        self.guia.write_text(
            "```python archivo=saludar.py incluir=saludar.py\nignored\n```\n"
            "```bash paso\npython3 saludar.py\n```\n"
            "```text salida\nhola\n```\n"
            "```bash paso\npython3 saludar.py\n```\n"
            "```text salida\nhola\n```\n", encoding="utf-8")

    def test_dos_pasos_reales_y_salida_vieja(self):
        guia.verificar(guia=self.guia)
        self.guia.write_text(self.guia.read_text().replace("hola\n```", "adiós\n```", 1))
        with self.assertRaisesRegex(AssertionError, "Salida vieja"):
            guia.verificar(guia=self.guia)

    def test_escribir_sustituye_solo_salidas_y_ambas(self):
        original = self.guia.read_text()
        self.guia.write_text(original.replace("```text salida\nhola", "```text salida\nvieja"))
        guia.verificar(escribir=True, guia=self.guia)
        self.assertEqual(self.guia.read_text(), original)

    def test_reemplazo_puro_de_dos_bloques(self):
        lineas = ["inicio\n", "vieja a\n", "medio\n", "vieja b\n", "fin\n"]
        nueva = guia.reemplazar_salidas(lineas, [(1, 2, "a\n"), (3, 4, "b\n")])
        self.assertEqual(nueva, ["inicio\n", "a\n", "medio\n", "b\n", "fin\n"])
        self.assertEqual(lineas, ["inicio\n", "vieja a\n", "medio\n", "vieja b\n", "fin\n"])

    def test_paso_sin_salida_y_fence_abierto_fallan(self):
        self.guia.write_text("```python archivo=saludar.py incluir=saludar.py\nignored\n```\n"
                              "```bash paso\npython3 saludar.py\n```\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Falta `text salida`"):
            guia.verificar(guia=self.guia)
        with self.assertRaisesRegex(ValueError, "Bloque sin cierre"):
            list(guia.bloques(["```bash paso\n", "python3 saludar.py\n"]))

    def test_rutas_fuera_del_proyecto_se_rechazan(self):
        for ruta in ("..", "../escape", "."):
            with self.subTest(ruta=ruta), self.assertRaisesRegex(ValueError, "Ruta fuera"):
                guia.dentro(self.raiz, ruta)

    def test_normalizacion_preserva_texto_y_oculta_rutas_y_tiempos(self):
        temporal = self.raiz / "temporal"
        salida = guia.normalizar(f"{self.raiz}/archivo {temporal}/batalla-naval 1.2 s\n", temporal)
        self.assertEqual(salida, "…/oracle/archivo …/oracle/temporal/batalla-naval <tiempo>\n")

    def test_paso_que_debe_fallar_y_comando_no_admitido(self):
        (self.raiz / "fallar.py").write_text("raise SystemExit(3)\n", encoding="utf-8")
        guia.correr("python3 fallar.py", self.raiz, self.raiz, falla=True)
        with self.assertRaisesRegex(RuntimeError, "Falló"):
            guia.correr("python3 fallar.py", self.raiz, self.raiz)
        with self.assertRaisesRegex(RuntimeError, "Se esperaba que fallara"):
            guia.correr("python3 saludar.py", self.raiz, self.raiz, falla=True)
        with self.assertRaisesRegex(ValueError, "Comando no contemplado"):
            guia.correr("echo hola", self.raiz, self.raiz)


if __name__ == "__main__":
    unittest.main()
