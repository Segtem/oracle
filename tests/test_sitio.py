"""Las páginas de documentación del sitio se generan desde los `.md` y no pueden quedar atrás."""

import unittest

from tools import sitio


class LasPaginasDelSitioEstanAlDiaTests(unittest.TestCase):
    def test_cada_pagina_publicada_es_exactamente_la_generada(self) -> None:
        for p in sitio.PAGINAS:
            with self.subTest(pagina=p.salida):
                publicada = (sitio.DOCS / p.salida).read_text(encoding="utf-8")
                self.assertEqual(publicada, sitio.pagina(p),
                                 f"docs/{p.salida} quedó atrás: regenerala con "
                                 "`python tools/sitio.py --escribir`")


class ElConvertidorTests(unittest.TestCase):
    def convertir(self, md: str) -> str:
        c = sitio.Convertidor(sitio.DOCS / "x.md", sitio.DOCS / "x.html")
        return c.bloques(md.splitlines())

    def test_un_enlace_a_otro_md_del_sitio_va_a_su_pagina(self) -> None:
        self.assertIn('href="02-de-cero-a-un-rojo.html#instalar"',
                      self.convertir("[a](02-de-cero-a-un-rojo.md#instalar)"))

    def test_un_enlace_a_un_archivo_del_repo_va_a_github(self) -> None:
        self.assertIn(f'href="{sitio.REPO}/blob/main/tools/cli.py"', self.convertir("[a](../tools/cli.py)"))

    def test_una_lista_anidada_queda_anidada(self) -> None:
        self.assertIn("<li>dos\n<ul><li>dos.a</li></ul></li>", self.convertir("- uno\n- dos\n  - dos.a"))

    def test_el_codigo_se_escapa_y_no_se_interpreta(self) -> None:
        salida = self.convertir("```\n<b>**no**</b>\n```")
        self.assertIn("&lt;b&gt;**no**&lt;/b&gt;", salida)

    def test_una_tabla_se_convierte_en_tabla(self) -> None:
        salida = self.convertir("| a | b |\n|---|---|\n| 1 | 2 |")
        self.assertIn("<th>a</th>", salida)
        self.assertIn("<td>2</td>", salida)
