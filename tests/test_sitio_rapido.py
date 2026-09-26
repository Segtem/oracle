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
        juego = self.convertir('<!-- juego {"tipo":"tablero","proyecto":"ejemplo/batalla-naval",'
                               '"medida":"naval.barcos_dentro_del_tablero"} -->')
        datos = json.loads(html.unescape(juego.split('data-juego="')[1].split('"')[0]))
        self.assertEqual(datos["donde"], tablero["donde"])
        with self.assertRaisesRegex(ValueError, "tipo de juego desconocido"):
            sitio.juego('{"tipo":"inventado"}')

    def test_cazamutantes_publica_matriz_real(self):
        datos = sitio._cazamutantes("ejemplo/batalla-naval", "naval.barcos_dentro_del_tablero")
        self.assertEqual(len(datos["casos"]), 5)
        self.assertEqual(len(datos["mutantes"]), 18)
        aflojar = next(m for m in datos["mutantes"] if m["id"] == "aflojar_umbral")
        self.assertEqual(aflojar["cambia"], ["umbral <= 1"])
        self.assertEqual(aflojar["quita"], ["umbral <= 0"])
        self.assertIn("005-barco-fila-desbordada", aflojar["muere_con"])
        self.assertEqual(datos["casos"][0]["id"], "005-barco-fila-desbordada")


if __name__ == "__main__":
    unittest.main()
