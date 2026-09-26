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
        with self.assertRaisesRegex(AssertionError, r"Salida vieja en línea 7; ejecutá\b"):
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
        with self.assertRaisesRegex(ValueError, r"Falta `text salida` después del paso en línea 4\b"):
            guia.verificar(guia=self.guia)
        with self.assertRaisesRegex(ValueError, r"Bloque sin cierre en línea 1\b"):
            list(guia.bloques(["```bash paso\n", "python3 saludar.py\n"]))

    def test_cd_a_un_directorio_que_no_existe_lo_nombra(self):
        with tempfile.TemporaryDirectory() as td:
            temporal = Path(td)
            with self.assertRaises(ValueError) as error:
                guia.correr("cd no-existe", temporal, temporal)
        self.assertIn("No existe el directorio no-existe", str(error.exception))

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

    def test_guia_predeterminada(self):
        self.assertEqual(guia.GUIA, guia.GUIAS[0])

    def test_correr_comando_vacio_y_rm(self):
        salida, cwd = guia.correr("   ", self.raiz, self.raiz)
        self.assertEqual(salida, "")
        self.assertEqual(cwd, self.raiz)
        salida, cwd = guia.correr("rm -f no_existe.txt", self.raiz, self.raiz)
        self.assertEqual(salida, "")
        self.assertEqual(cwd, self.raiz)

    @patch.object(guia.subprocess, "run")
    def test_correr_python_sin_argumentos_y_timeout(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""
        guia.correr("python3", self.raiz, self.raiz)
        self.assertEqual(mock_run.call_args.kwargs.get("timeout"), 180)

    def test_correr_python_valida_ruta_dentro(self):
        with self.assertRaisesRegex(ValueError, "Ruta fuera del proyecto"):
            guia.correr("python3 ../fuera.py", self.raiz, self.raiz)

    @patch.object(guia.subprocess, "run")
    def test_correr_fallas_admitidas_en_guia(self, mock_run):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "fallo\n"
        salida, _ = guia.correr("oracle revisar", self.raiz, self.raiz)
        self.assertIn("fallo", salida)
        mock_run.return_value.stdout = "1 medidas en rojo\n"
        salida, _ = guia.correr("oracle juzgar", self.raiz, self.raiz)
        self.assertIn("medidas en rojo", salida)
        with self.assertRaisesRegex(RuntimeError, "Falló"):
            guia.correr("oracle", self.raiz, self.raiz)

    def test_verificar_atributos_bloque_y_directorios(self):
        self.guia.write_text("```python archivo=saludar.py\nx\n```\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, r"Faltan atributos en línea 1\b"):
            guia.verificar(guia=self.guia)
        (self.raiz / "paquete").mkdir()
        (self.raiz / "paquete" / "mod.py").write_text("print(1)\n", encoding="utf-8")
        self.guia.write_text(
            "```python archivo=sub/dir/mod.py incluir=paquete/mod.py\nx\n```\n"
            "```python archivo=sub/copia incluir=paquete\nx\n```\n"
            "```python archivo=sub/copia incluir=paquete\nx\n```\n"
            "```bash paso\npython3 sub/dir/mod.py\n```\n"
            "```text salida\n1\n```\n", encoding="utf-8")
        guia.verificar(guia=self.guia)

    def test_comandos_multilinea_y_comentarios(self):
        # 1. Comentario con comando inexistente que fallaría si se ejecutara
        self.guia.write_text(
            "```python archivo=saludar.py incluir=saludar.py\nx\n```\n"
            "```bash paso\n"
            "# \"$(python3 inexistente_que_fallaria.py)\"\n"
            "python3 saludar.py\n"
            "```\n"
            "```text salida\nhola\n```\n", encoding="utf-8")
        guia.verificar(guia=self.guia)

        # 2. Paso con continuación sin sangría que termina en barra invertida
        (self.raiz / "eco.py").write_text(
            "import sys\nprint(' '.join(sys.argv[1:]))\n", encoding="utf-8")
        self.guia.write_text(
            "```python archivo=eco.py incluir=eco.py\nx\n```\n"
            "```bash paso\n"
            "python3 eco.py \\\n"
            "--otra_linea \\\n"
            "  --final\n"
            "```\n"
            "```text salida\n--otra_linea --final\n```\n", encoding="utf-8")
        guia.verificar(guia=self.guia)

    def test_salida_conteo_pasos_en_stdout(self):
        import io
        from contextlib import redirect_stdout
        (self.raiz / "fallar.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
        self.guia.write_text(
            "```python archivo=saludar.py incluir=saludar.py\nx\n```\n"
            "```python archivo=fallar.py incluir=fallar.py\nx\n```\n"
            "```bash paso\npython3 saludar.py\n```\n"
            "```text salida\nhola\n```\n"
            "```bash paso falla\npython3 fallar.py\n```\n"
            "```text salida\n<tiempo>\n```\n", encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf):
            guia.verificar(escribir=True, guia=self.guia)
        self.assertIn("2 pasos, ", buf.getvalue())

    def test_main_ejecuta_guias_indicadas_y_codigos_retorno(self):
        import sys
        with patch.object(sys, "argv", ["guia.py", str(self.guia)]), \
             patch.object(guia, "verificar") as mock_ver:
            codigo = guia.main()
            self.assertEqual(codigo, 0)
            self.assertEqual(mock_ver.call_count, 1)

        with patch.object(sys, "argv", ["guia.py", str(self.guia)]), \
             patch.object(guia, "verificar", side_effect=ValueError("error")):
            codigo = guia.main()
            self.assertEqual(codigo, 1)


if __name__ == "__main__":
    unittest.main()
