"""Afirmaciones directas del convertidor, enlaces y datos del juego publicado."""

import html
import json
import unittest
from pathlib import Path

from tools import sitio


class ConversionTests(unittest.TestCase):
    def convertir(self, texto):
        return sitio.Convertidor(sitio.DOCS / "x.md", sitio.DOCS / "x.html").bloques(texto.splitlines())

    def test_enlaces_internos_externos_y_archivos(self):
        origen, salida = sitio.DOCS / "x.md", sitio.DOCS / "x.html"
        self.assertEqual(sitio._destino("02-de-cero-a-un-rojo.md#instalar", origen, salida),
                         "02-de-cero-a-un-rojo.html#instalar")
        self.assertEqual(sitio._destino("../tools/cli.py", origen, salida),
                         f"{sitio.REPO}/blob/main/tools/cli.py")
        self.assertEqual(sitio._destino("https://example.org/a", origen, salida),
                         "https://example.org/a")
        self.assertEqual(sitio._destino("#parte", origen, salida), "#parte")
        self.assertIn('rel="noopener"', sitio.en_linea("[web](https://example.org)", origen, salida))

    def test_markdown_conserva_estructura_y_escapa_codigo(self):
        convertido = self.convertir(
            "## Hola mundo\n\n## Hola mundo\n\n**fuerte** y *énfasis*\n\n"
            "| a | b |\n|---|---|\n| 1 | 2 |\n\n"
            "- uno\n- dos\n  - hijo\n\n```oracle archivo=regla.oracle\nmedida x < y\n```")
        self.assertIn('id="hola-mundo"', convertido)
        self.assertIn('id="hola-mundo-1"', convertido)
        self.assertIn("<strong>fuerte</strong>", convertido)
        self.assertIn("<em>énfasis</em>", convertido)
        self.assertIn("<th>a</th>", convertido)
        self.assertIn("<td>2</td>", convertido)
        self.assertIn("<ul><li>hijo</li></ul>", convertido)
        self.assertIn("&lt;", convertido)
        self.assertIn('class="archivo"', convertido)

    def test_juego_inserta_datos_calculados(self):
        tablero = sitio._tablero("ejemplo/batalla-naval", "naval.barcos_dentro_del_tablero")
        self.assertEqual(tablero["relacion"], "celda_barco")
        self.assertEqual(tablero["alias"], "c")
        self.assertEqual(tablero["umbral"], ["<=", 0])
        self.assertEqual(tablero["donde"][0], "o")
        self.assertEqual(len(tablero["donde"]) - 1, 4)
        tablero_flota = sitio._tablero("ejemplo/batalla-naval", "naval.flota_reglamentaria")
        self.assertEqual(tablero_flota["requiere"], ["celda_barco"])
        juego = self.convertir('<!-- juego {"tipo":"tablero","proyecto":"ejemplo/batalla-naval",'
                               '"medida":"naval.barcos_dentro_del_tablero"} -->')
        datos = json.loads(html.unescape(juego.split('data-juego="')[1].split('"')[0]))
        self.assertEqual(datos["donde"], tablero["donde"])
        with self.assertRaisesRegex(ValueError, "tipo de juego desconocido"):
            sitio.juego('{"tipo":"inventado"}')
        from unittest.mock import patch
        with patch.object(sitio, "_medida") as mock_m:
            mock_m.return_value.a_datos.return_value = ["medida", "x", ["desde", ["de", "r", "a"]], ["resumen"], ["umbral"]]
            with self.assertRaisesRegex(ValueError, "el tablero necesita"):
                sitio._tablero("ejemplo/batalla-naval", "x")

    def test_cazamutantes_publica_matriz_real(self):
        datos = sitio._cazamutantes("ejemplo/batalla-naval", "naval.barcos_dentro_del_tablero")
        self.assertEqual(len(datos["casos"]), 5)
        self.assertEqual(len(datos["mutantes"]), 18)
        aflojar = next(m for m in datos["mutantes"] if m["id"] == "aflojar_umbral")
        self.assertEqual(aflojar["cambia"], ["umbral <= 1"])
        self.assertEqual(aflojar["quita"], ["umbral <= 0"])
        self.assertIn("005-barco-fila-desbordada", aflojar["muere_con"])
        self.assertEqual(datos["casos"][0]["id"], "005-barco-fila-desbordada")

    def test_pagina_inmutable(self):
        p = sitio.Pagina("a", "b", "c", "d")
        with self.assertRaises(Exception):
            p.origen = "otro"

    def test_decision_titulo_primer_token(self):
        decision = next(p for p in sitio.PAGINAS if p.grupo == "Decisiones")
        self.assertTrue(decision.titulo.isdigit())

    def test_destino_fuera_de_raiz_y_directorio(self):
        origen, salida = sitio.DOCS / "x.md", sitio.DOCS / "x.html"
        self.assertEqual(sitio._destino("/fuera/de/raiz", origen, salida), "/fuera/de/raiz")
        self.assertIn("/tree/main/catalogos", sitio._destino("../catalogos", origen, salida))

    def test_relativa_sin_partes_comunes(self):
        self.assertEqual(sitio._relativa(Path("a/b"), Path("c/d")), "../a/b")

    def test_imagen_en_linea(self):
        origen, salida = sitio.DOCS / "x.md", sitio.DOCS / "x.html"
        self.assertIn('<span class="imagen-faltante">[imagen: foto]</span>',
                      sitio.en_linea("![foto](foto.png)", origen, salida))

    def test_codigo_salida_por_defecto_falsa(self):
        html_code = sitio.codigo("print(1)", "python")
        self.assertNotIn('class="salida"', html_code)

    def test_celdas_con_barras_al_borde(self):
        self.assertEqual(sitio._celdas("|x|"), ["x"])

    def test_continuidad_bloques_despues_de_juego_pregunta_y_hr(self):
        md = (
            '<!-- juego {"tipo":"tablero","proyecto":"ejemplo/batalla-naval",'
            '"medida":"naval.barcos_dentro_del_tablero"} -->\n'
            "## Seccion A\n"
            '<p class="pregunta">¿Una pregunta?</p>\n'
            "## Seccion B\n"
            "---\n"
            "## Seccion C\n"
        )
        html_conv = self.convertir(md)
        self.assertIn('id="seccion-a"', html_conv)
        self.assertIn('id="seccion-b"', html_conv)
        self.assertIn('id="seccion-c"', html_conv)

    def test_pregunta_requiere_apertura_y_cierre(self):
        html_conv = self.convertir("texto con </p>")
        self.assertNotIn('class="pregunta"', html_conv)

    def test_fence_y_cita_al_final_del_documento(self):
        html_fence = self.convertir("```python\nx = 1")
        self.assertIn("<pre", html_fence)
        html_cita = self.convertir("> cita al final")
        self.assertIn("<blockquote>", html_cita)

    def test_tabla_al_final_y_despues_de_parrafo(self):
        html_tubo = self.convertir("linea con |")
        self.assertIn("<p>linea con |</p>", html_tubo)
        html_dos = self.convertir("| a | b |\n|---|---|")
        self.assertIn("<table>", html_dos)
        html_parr = self.convertir("parrafo\n| a | b |\n|---|---|")
        self.assertIn("<p>parrafo</p>", html_parr)
        self.assertIn("<table>", html_parr)

    def test_lista_con_linea_blanca_y_subitem_no_vuelve_suelta(self):
        html_conv = self.convertir("- uno\n\n  - hijo\n- dos")
        self.assertNotIn("<li><p>uno", html_conv)

    def test_main_sitio(self):
        import io
        import shutil
        from contextlib import redirect_stdout
        from unittest.mock import patch
        tmp_rel = sitio.RAIZ / "temporal_test_docs"
        tmp_rel.mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: shutil.rmtree(tmp_rel, ignore_errors=True))
        p = sitio.Pagina("test_tmp.md", "temporal_test_docs/sub/dir/test.html", "Grupo", "Titulo")
        (sitio.RAIZ / "test_tmp.md").write_text("# Test\n", encoding="utf-8")
        self.addCleanup(lambda: (sitio.RAIZ / "test_tmp.md").unlink(missing_ok=True))
        buf = io.StringIO()
        with redirect_stdout(buf):
            with patch.object(sitio, "PAGINAS", (p,)), \
                 patch.object(sitio, "DOCS", sitio.RAIZ):
                self.assertEqual(sitio.main([]), 1)
                self.assertEqual(sitio.main(["--escribir"]), 0)
                self.assertEqual(sitio.main([]), 0)
                # Segunda escritura con directorio ya existente (exige exist_ok=True)
                (sitio.RAIZ / "test_tmp.md").write_text("# Test 2\n", encoding="utf-8")
                self.assertEqual(sitio.main(["--escribir"]), 0)

    def test_entrada_directa_sitio(self):
        import runpy
        import sys
        from unittest.mock import patch

        class ArgvCaptura(list):
            captured_slice = None
            def __getitem__(self, item):
                if isinstance(item, slice):
                    ArgvCaptura.captured_slice = item
                return super().__getitem__(item)

        argv = ArgvCaptura(["tools/sitio.py"])
        with patch.object(sys, "argv", argv):
            with self.assertRaises(SystemExit) as ctx:
                runpy.run_path(str(sitio.RAIZ / "tools/sitio.py"), run_name="__main__")
            self.assertEqual(ctx.exception.code, 0)
            self.assertEqual(ArgvCaptura.captured_slice.start, 1)


if __name__ == "__main__":
    unittest.main()
