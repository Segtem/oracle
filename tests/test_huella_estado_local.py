"""La huella de un directorio de procedencia no depende del estado local de las herramientas."""

import tempfile
import unittest
from pathlib import Path

from nucleo.diferencial import huella_archivos


class EstadoLocalTests(unittest.TestCase):
    def test_ocultos_y_pycache_no_cambian_la_huella_de_un_directorio(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "vault").mkdir()
            (raiz / "vault" / "nota.md").write_text("contenido", encoding="utf-8")
            antes = huella_archivos(raiz, ["vault"])
            for ruta in (".obsidian/workspace.json", ".DS_Store", "sub/.oculto", "__pycache__/x.pyc"):
                destino = raiz / "vault" / ruta
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text("estado local", encoding="utf-8")
                with self.subTest(ruta=ruta):
                    self.assertEqual(huella_archivos(raiz, ["vault"]), antes)
            (raiz / "vault" / "otra.md").write_text("contenido", encoding="utf-8")
            self.assertNotEqual(huella_archivos(raiz, ["vault"]), antes)

    def test_un_oculto_nombrado_como_fuente_se_cuenta(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / ".config").write_text("uno", encoding="utf-8")
            antes = huella_archivos(raiz, [".config"])
            (raiz / ".config").write_text("dos", encoding="utf-8")
            self.assertNotEqual(huella_archivos(raiz, [".config"]), antes)


if __name__ == "__main__":
    unittest.main()
