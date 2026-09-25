"""La descripción publicada debe conservar los enlaces de su versión."""

import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from nucleo.version import VERSION_DISTRIBUCION


RAIZ = Path(__file__).resolve().parents[1]


class EnlacesDePyPI(unittest.TestCase):
    def test_el_wheel_conserva_los_enlaces_del_readme(self) -> None:
        original = (RAIZ / "README.md").read_bytes()
        with tempfile.TemporaryDirectory() as td:
            resultado = subprocess.run(
                [sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation",
                 "--wheel-dir", td, str(RAIZ)], capture_output=True, text=True)
            self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
            rueda, = Path(td).glob("oracle_metalenguaje-*.whl")
            with zipfile.ZipFile(rueda) as archivo:
                metadata, = (nombre for nombre in archivo.namelist()
                             if nombre.endswith(".dist-info/METADATA"))
                texto = archivo.read(metadata).decode("utf-8")
        self.assertEqual((RAIZ / "README.md").read_bytes(), original)
        self.assertIn(
            f"https://github.com/Segtem/oracle/blob/v{VERSION_DISTRIBUCION}/NOTAS-DE-RELEASE.md",
            texto)
        self.assertNotIn("github.com/Segtem/oracle/blob/main/", texto)
        self.assertNotIn("github.com/Segtem/oracle/tree/main/", texto)

    def test_los_enlaces_relativos_se_vuelven_absolutos(self) -> None:
        from tools.cifras import enlaces_del_tag

        texto = "[doc](docs/guia.md#parte) [dir](./ejemplo/) [local](#seccion)"
        esperado = ("[doc](https://github.com/Segtem/oracle/blob/v0.30.0/docs/guia.md#parte) "
                    "[dir](https://github.com/Segtem/oracle/tree/v0.30.0/ejemplo/) "
                    "[local](#seccion)")
        self.assertEqual(enlaces_del_tag(texto, "0.30.0"), esperado)

    def test_cifras_detecta_y_actualiza_enlaces_vencidos(self) -> None:
        from unittest import mock
        from tools import cifras

        with tempfile.TemporaryDirectory() as td:
            ruta = Path(td) / "README.md"
            ruta.write_text("[notas](https://github.com/Segtem/oracle/blob/main/NOTAS-DE-RELEASE.md)\n",
                            encoding="utf-8")
            with mock.patch.multiple(cifras, RAIZ=Path(td), BLOQUES={},
                                     DOCUMENTOS=("README.md",)), mock.patch.object(
                                         cifras, "custodiados_sin_versionar", return_value=[]):
                self.assertEqual(cifras.main([]), 1)
                self.assertEqual(cifras.main(["--actualizar"]), 0)
                self.assertEqual(cifras.main([]), 0)
            self.assertIn(f"blob/v{VERSION_DISTRIBUCION}/NOTAS-DE-RELEASE.md",
                          ruta.read_text(encoding="utf-8"))
