"""Las páginas de documentación del sitio se generan desde los `.md` y no pueden quedar atrás."""

import html
import re
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

    def test_los_archivos_incluidos_se_pueden_copiar_sin_perder_texto(self) -> None:
        texto = (sitio.DOCS / "de-cero.md").read_text(encoding="utf-8")
        archivos = re.findall(r"^```\w+ archivo=(\S+) incluir=(\S+)$", texto, re.M)
        self.assertGreater(len(archivos), 50)
        for destino, fuente in archivos:
            with self.subTest(archivo=destino, fuente=fuente):
                bloque = self.convertir(f"```oracle archivo={destino} incluir={fuente}\n```\n")
                codigo = re.search(r"<code>(.*?)</code>", bloque, re.S).group(1)
                copiado = html.unescape(re.sub(r"</?span\b[^>]*>", "", codigo))
                self.assertEqual(copiado, (sitio.RAIZ / fuente).read_text(encoding="utf-8"))

    def test_toda_clave_de_un_caso_y_de_una_medida_se_colorea(self) -> None:
        # Hasta el 2026-10-01 la gramática pintaba `origen` y `titulo` pero no `fecha` ni
        # `procedencia`: en un mismo caso, la mitad de las claves salía sin color.
        for clave in ("fecha", "repo", "commit", "procedencia", "etiqueta", "como_se_detecto", "medida",
                      "espera", "ambito", "sin", "origen", "titulo"):
            with self.subTest(clave=clave):
                self.assertIn(f'<span class="tok-keyword">    {clave}</span>', sitio.colorear_oracle(f"    {clave}: x"))

    def test_un_arbol_se_rotula_y_no_se_ofrece_para_copiar(self) -> None:
        html = self.convertir("```text arbol\nbatalla-naval/\n└── oracle.json\n```")
        self.assertIn('<pre class="arbol" data-lenguaje="así tiene que quedar tu carpeta">', html)
        self.assertIn("└── oracle.json", html)
        self.assertNotIn('class="salida"', html)
        self.assertIn('.prosa pre:not(.salida):not(.arbol)', (sitio.RAIZ / "docs/de-cero.html").read_text(encoding="utf-8"))

    def test_medida_coloreada_con_la_gramatica_del_editor(self) -> None:
        entrada = 'medida naval.prueba:\n    donde t.fila < 2 y t.columna == "<x>" # nota'
        esperado = ('<span class="tok-storage">medida</span> '
                    '<span class="tok-entity">naval.prueba</span>:\n'
                    '<span class="tok-keyword">    donde</span> '
                    '<span class="tok-variable">t</span>.<span class="tok-property">fila</span> '
                    '<span class="tok-operator">&lt;</span> <span class="tok-number">2</span> '
                    '<span class="tok-keyword">y</span> '
                    '<span class="tok-variable">t</span>.<span class="tok-property">columna</span> '
                    '<span class="tok-operator">==</span> '
                    '<span class="tok-string">&quot;&lt;x&gt;&quot;</span> '
                    '<span class="tok-comment"># nota</span>')
        self.assertEqual(sitio.colorear_oracle(entrada), esperado)

    def test_una_tabla_se_convierte_en_tabla(self) -> None:
        salida = self.convertir("| a | b |\n|---|---|\n| 1 | 2 |")
        self.assertIn("<th>a</th>", salida)
        self.assertIn("<td>2</td>", salida)


class ElIndiceDeLasNotasLlegaASuVersionTests(unittest.TestCase):
    def test_cada_ancla_del_indice_existe_en_la_pagina(self):
        import re
        pagina = sitio.pagina(next(p for p in sitio.PAGINAS if p.salida == "notas.html"))
        texto = (sitio.RAIZ / "NOTAS-DE-RELEASE.md").read_text(encoding="utf-8")
        indice = texto.split("<!-- notas_indice:inicio -->")[1].split("<!-- notas_indice:fin -->")[0]
        anclas = re.findall(r"\]\(#([^)]+)\)", indice)
        self.assertGreater(len(anclas), 10)
        ids = set(re.findall(r'id="([^"]+)"', pagina))
        for ancla in anclas:
            with self.subTest(ancla=ancla):
                self.assertIn(ancla, ids)
