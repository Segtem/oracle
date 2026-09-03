"""El manual es una vista de las declaraciones, y eso es lo que se fija acá."""

from __future__ import annotations

import io
import sys
import unittest
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from tools import manual  # noqa: E402


class TemasTests(unittest.TestCase):

    def test_estan_todos_los_vocabularios_y_los_verbos(self) -> None:
        self.assertEqual(set(manual.temas()), set(manual.VOCABULARIOS) | {"verbos"})

    def test_los_vocabularios_van_antes_que_los_verbos(self) -> None:
        """El orden es el de lectura: primero lo que hay que entender para escribir una medida,
        y al final el listado de comandos, que se consulta y no se lee."""
        self.assertEqual(manual.temas()[-1], "verbos")

    def test_no_hay_temas_repetidos(self) -> None:
        self.assertEqual(len(manual.temas()), len(set(manual.temas())))


class EntradasTests(unittest.TestCase):

    def test_un_vocabulario_entrega_sus_opciones_ordenadas(self) -> None:
        pares = manual.entradas("segun")
        self.assertEqual([n for n, _ in pares], ["contrato", "convencion", "medicion", "tanteo"])
        for _, sentido in pares:
            self.assertTrue(sentido)

    def test_cada_opcion_viaja_con_su_sentido_y_no_con_su_nombre(self) -> None:
        for nombre, (_, vocabulario) in manual.VOCABULARIOS.items():
            with self.subTest(tema=nombre):
                self.assertEqual(dict(manual.entradas(nombre)), vocabulario)

    def test_los_verbos_se_agrupan_por_sustantivo(self) -> None:
        pares = dict(manual.entradas("verbos"))
        self.assertIn("oracle medida", pares)
        self.assertIn("listar", pares["oracle medida"])
        self.assertIn("·", pares["oracle medida"])

    def test_un_tema_que_no_existe_no_devuelve_vacio_sino_que_falla(self) -> None:
        """Devolver una lista vacía imprimiría una sección con título y sin nada: el lector
        concluiría que el tema existe y está vacío, que es peor que no encontrarlo."""
        with self.assertRaises(manual.TemaDesconocido):
            manual.entradas("mengano")
        with self.assertRaises(manual.TemaDesconocido):
            manual.titulo("mengano")


class TituloTests(unittest.TestCase):

    def test_cada_tema_tiene_titulo_propio(self) -> None:
        titulos = [manual.titulo(t) for t in manual.temas()]
        self.assertEqual(len(titulos), len(set(titulos)))
        for t in titulos:
            self.assertTrue(t.strip())


@contextmanager
def _vocabulario(opciones: dict[str, str], tema: str = "segun"):
    """Reemplaza un vocabulario por uno chico, para poder fijar el render exacto.

    Contra los vocabularios de verdad no se puede: cambian, y un test que copie su prosa se rompe
    cada vez que alguien mejora una explicación. Lo que hay que fijar es la ARITMÉTICA del render.
    """
    original = manual.VOCABULARIOS[tema]
    manual.VOCABULARIOS[tema] = ("prueba", opciones)
    try:
        yield
    finally:
        manual.VOCABULARIOS[tema] = original


class EnvolverTests(unittest.TestCase):

    def test_ninguna_linea_pasa_el_ancho(self) -> None:
        largo = "palabra " * 40
        for linea in manual._envolver(largo.strip(), 30, " " * 4):
            self.assertLessEqual(len(linea), 34)

    def test_la_primera_linea_no_lleva_sangria_y_las_demas_si(self) -> None:
        """La primera va pegada al nombre; las de abajo cuelgan de la misma columna. Sin eso el
        texto continúa bajo el nombre y no se distingue dónde empieza la entrada siguiente."""
        lineas = manual._envolver("uno dos tres cuatro cinco seis", 12, "    ")
        self.assertFalse(lineas[0].startswith(" "))
        for l in lineas[1:]:
            self.assertTrue(l.startswith("    "))

    def test_una_palabra_mas_larga_que_el_ancho_no_se_pierde(self) -> None:
        lineas = manual._envolver("corta supercalifragilisticoespialidoso", 8, "  ")
        self.assertIn("supercalifragilisticoespialidoso", " ".join(lineas))

    def test_la_primera_palabra_va_sola_aunque_no_entre(self) -> None:
        """Una palabra que sola ya pasa el ancho no puede empujar una línea VACÍA delante suyo.
        El `actual and …` es lo que lo evita: sin él, la primera vuelta corta antes de tener nada
        que cortar."""
        self.assertEqual(manual._envolver("supercalifragilistico corta", 8, "  "),
                         ["supercalifragilistico", "  corta"])

    def test_lo_que_entra_justo_no_se_parte(self) -> None:
        """El caso del borde: dos palabras que con el espacio suman EXACTAMENTE el ancho. Entran.
        Fija tres cosas a la vez —que la comparación sea estricta, que el espacio cuente uno solo,
        y que el ancho sea el que se pidió—, y ninguna se puede ver sin caer justo en el límite."""
        self.assertEqual(manual._envolver("ab cd", 5, "  "), ["ab cd"])
        self.assertEqual(manual._envolver("ab cde", 5, "  "), ["ab", "  cde"])


class SeccionTests(unittest.TestCase):

    def test_lleva_el_tema_en_mayusculas_y_su_titulo(self) -> None:
        s = manual.seccion("segun")
        self.assertTrue(s.startswith("SEGUN — de dónde"))

    def test_aparecen_todas_las_opciones_con_su_sentido(self) -> None:
        s = manual.seccion("etiqueta")
        for nombre, sentido in manual.entradas("etiqueta"):
            self.assertIn(nombre, s)
            self.assertIn(sentido.split()[0], s)

    def test_los_nombres_quedan_alineados_en_una_columna(self) -> None:
        """Un vocabulario se busca con la vista. Si cada sentido empieza en una columna distinta,
        hay que leer renglón por renglón."""
        cuerpo = [l for l in manual.seccion("etiqueta").splitlines()[2:] if l.strip()]
        arranques = {len(l) - len(l.lstrip()) for l in cuerpo}
        self.assertEqual(len(arranques), 2, "hay más de una sangría de nombre y una de sentido")


class ElRenderFijaSuAritmeticaTests(unittest.TestCase):
    """Los nombres se alinean en una columna y el texto cuelga de ella. Es todo aritmética, y cada
    número de esa aritmética es un mutante que sin un render exacto nadie distingue."""

    def test_la_columna_y_la_sangria_salen_del_nombre_mas_largo(self) -> None:
        with _vocabulario({"a": "uno", "bbbb": "dos"}):
            self.assertEqual(
                manual.seccion("segun"),
                "SEGUN — prueba\n"
                "\n"
                "  a     uno\n"
                "  bbbb  dos")

    def test_lo_que_sigue_cuelga_de_la_misma_columna_que_el_texto(self) -> None:
        with _vocabulario({"a": "uno dos tres cuatro"}):
            self.assertEqual(
                manual.seccion("segun", 14),
                "SEGUN — prueba\n"
                "\n"
                "  a  uno dos\n"
                "     tres\n"
                "     cuatro")

    def test_no_se_pierde_ninguna_linea_de_las_que_siguen(self) -> None:
        with _vocabulario({"a": "uno dos tres cuatro cinco seis siete"}):
            cuerpo = manual.seccion("segun", 14).splitlines()[2:]
            self.assertEqual(len(cuerpo), 6)
            self.assertIn("siete", cuerpo[-1])

    def test_el_ancho_por_defecto_es_noventa_y_seis(self) -> None:
        """No se afirma leyendo la firma: se afirma mostrando que a 97 el texto se acomoda
        distinto. Un valor por defecto que nadie puede distinguir del de al lado no está fijado."""
        justo = " ".join(["abcdefghij"] * 8 + ["xyz"])
        with _vocabulario({"aa": justo}):
            self.assertEqual(manual.seccion("segun"), manual.seccion("segun", 96))
            self.assertNotEqual(manual.seccion("segun"), manual.seccion("segun", 97))
            self.assertEqual(manual.texto("segun"), manual.texto("segun", 96))
            self.assertNotEqual(manual.texto("segun"), manual.texto("segun", 97))


class TextoTests(unittest.TestCase):

    def test_sin_tema_trae_todas_las_secciones(self) -> None:
        completo = manual.texto()
        for tema in manual.temas():
            self.assertIn(f"{tema.upper()} — ", completo)

    def test_con_tema_trae_solo_esa(self) -> None:
        uno = manual.texto("segun")
        self.assertIn("SEGUN — ", uno)
        self.assertNotIn("ETIQUETA — ", uno)


class HtmlTests(unittest.TestCase):

    def test_hay_una_entrada_por_opcion(self) -> None:
        salida = manual.html()
        esperadas = sum(len(manual.entradas(t)) for t in manual.temas())
        self.assertEqual(salida.count("<dt>"), esperadas)
        self.assertEqual(salida.count("<dd>"), esperadas)

    def test_cada_tema_tiene_ancla_propia(self) -> None:
        salida = manual.html()
        for tema in manual.temas():
            self.assertIn(f'id="manual-{tema}"', salida)

    def test_escapa_lo_que_podria_cerrar_una_etiqueta(self) -> None:
        """El sitio se publica; una prosa con `<` rompería la página en silencio."""
        vocabulario = {"x": "a < b & c"}
        original = manual.VOCABULARIOS.get("segun")
        manual.VOCABULARIOS["segun"] = ("prueba", vocabulario)
        try:
            salida = manual.html()
        finally:
            manual.VOCABULARIOS["segun"] = original
        self.assertIn("a &lt; b &amp; c", salida)
        self.assertNotIn("a < b & c", salida)


class PaginaTests(unittest.TestCase):

    def test_es_un_documento_entero_y_no_un_fragmento(self) -> None:
        pagina = manual.pagina()
        self.assertTrue(pagina.startswith("<!doctype html>"))
        self.assertIn("<title>Manual — Oracle</title>", pagina)
        self.assertIn("</html>", pagina)

    def test_lleva_adentro_el_mismo_cuerpo_que_la_terminal(self) -> None:
        """Si la página se armara aparte, sería una segunda copia del manual — que es exactamente
        lo que el manual existe para no tener."""
        self.assertIn(manual.html(), manual.pagina())

    def test_el_indice_lleva_a_todas_las_secciones(self) -> None:
        pagina = manual.pagina()
        for tema in manual.temas():
            self.assertIn(f'<a href="#manual-{tema}">', pagina)
            self.assertIn(f'id="manual-{tema}"', pagina)


class LaPaginaPublicadaNoSeDespegaTests(unittest.TestCase):
    """`docs/manual.html` se publica en el sitio y se genera con `oracle manual --html`.

    Sin esto, la página del sitio puede quedar mostrando un vocabulario que ya no existe y nadie se
    entera: nada la lee, y el que la lee no tiene con qué comparar. Se regenera con:

        python tools/cli.py manual --html > docs/manual.html
    """

    def test_el_archivo_publicado_es_exactamente_la_salida_del_comando(self) -> None:
        publicada = (RAIZ / "docs" / "manual.html").read_text(encoding="utf-8")
        self.assertEqual(publicada.rstrip("\n"), manual.pagina().rstrip("\n"),
                         "docs/manual.html quedó atrás: regeneralo con "
                         "`python tools/cli.py manual --html > docs/manual.html`")


class RoffTests(unittest.TestCase):
    """Cada uno de estos escapes se puso porque groff rompía algo EN SILENCIO."""

    def test_la_barra_invertida_deja_de_ser_una_directiva(self) -> None:
        self.assertEqual(manual._roff("uno \\ dos"), "uno \\e dos")

    def test_una_linea_que_empieza_con_punto_no_se_lee_como_macro(self) -> None:
        """La prosa de una medida puede empezar con «.» sin que nadie lo piense, y entonces groff
        se come el renglón entero."""
        self.assertEqual(manual._roff(".TH falso"), "\\&.TH falso")
        self.assertEqual(manual._roff("'apostrofo"), "\\&'apostrofo")
        self.assertEqual(manual._roff("no. empieza"), "no. empieza")

    def test_el_guion_largo_no_sale_duplicado(self) -> None:
        """Medido: «uno — dos» crudo se renderiza «uno —— dos»."""
        self.assertEqual(manual._roff("uno — dos"), "uno \\[em] dos")
        self.assertNotIn("—", manual.man("segun"))

    def test_las_comillas_invertidas_pasan_a_negrita(self) -> None:
        """Crudas salen como comilla simple IZQUIERDA de los dos lados: ‘segun‘."""
        self.assertEqual(manual._roff("el campo `segun` manda"),
                         "el campo \\fBsegun\\fR manda")
        self.assertNotIn("`", manual.man())

    def test_dos_pares_de_comillas_en_la_misma_prosa(self) -> None:
        """Con UN par no se puede distinguir un recorrido de a dos de uno de a tres: los dos toman
        el mismo elemento. Hacía falta una prosa con dos pares, que es además el caso real — una
        explicación que nombra dos campos."""
        self.assertEqual(
            manual._roff("entre `uno` y `dos` hay texto"),
            "entre \\fBuno\\fR y \\fBdos\\fR hay texto")

    def test_tres_pares_no_pierden_el_ultimo(self) -> None:
        """El tramo de texto que sigue al último código es el que se cae si el recorrido de los
        restos avanza de más."""
        self.assertEqual(
            manual._roff("`a` x `b` y `c` z"),
            "\\fBa\\fR x \\fBb\\fR y \\fBc\\fR z")

    def test_una_comilla_invertida_suelta_se_deja_como_esta(self) -> None:
        """Sin par no hay código que resaltar, y abrir una negrita que nunca cierra se lleva
        puesto todo lo que sigue en la página."""
        self.assertEqual(manual._roff("suelta ` sola"), "suelta ` sola")


class PaginasDeManualTests(unittest.TestCase):

    def test_la_pagina_de_un_tema_declara_su_seccion_y_su_nombre(self) -> None:
        pagina = manual.man("segun")
        self.assertTrue(pagina.startswith(".TH ORACLE-SEGUN 7 "))
        self.assertIn(".SH NOMBRE", pagina)
        self.assertIn("oracle-segun \\- ", pagina)
        self.assertIn(".SH SEGUN", pagina)

    def test_el_nombre_no_se_repite_a_los_dos_lados_del_guion(self) -> None:
        """`whatis` y `apropos` indexan esa línea y sólo esa: «oracle-segun - segun — …» gasta la
        mitad del renglón repitiendo lo que está a la izquierda."""
        linea = [l for l in manual.man("segun").splitlines() if l.startswith("oracle-segun")][0]
        descripcion = linea.split("\\- ", 1)[1]
        self.assertFalse(descripcion.startswith("segun"), linea)
        self.assertEqual(descripcion, manual._roff(manual.titulo("segun")))

    def test_sin_tema_estan_todos_los_temas(self) -> None:
        pagina = manual.man()
        self.assertTrue(pagina.startswith(".TH ORACLE-MANUAL 7 "))
        for tema in manual.temas():
            self.assertIn(f".SH {tema.upper()}", pagina)

    def test_cada_opcion_es_un_termino_con_su_definicion(self) -> None:
        pagina = manual.man("etiqueta")
        entradas = manual.entradas("etiqueta")
        self.assertEqual(pagina.count(".TP"), len(entradas))
        for nombre, _ in entradas:
            self.assertIn(f".B {nombre}", pagina)

    def test_la_pagina_del_comando_sale_de_los_verbos_del_despacho(self) -> None:
        """No se copian: si mañana entra un verbo, aparece acá solo."""
        from tools.cli import VERBOS

        pagina = manual.man_del_comando()
        self.assertTrue(pagina.startswith(".TH ORACLE 1 "))
        for sustantivo, verbos in VERBOS.items():
            self.assertIn(f".B oracle {sustantivo}", pagina)
            for verbo in verbos:
                self.assertIn(verbo, pagina)

    def test_estan_la_del_comando_la_general_y_una_por_tema(self) -> None:
        paginas = manual.paginas_man()
        self.assertEqual(set(paginas),
                         {"man1/oracle.1", "man7/oracle-manual.7"}
                         | {f"man7/oracle-{t}.7" for t in manual.temas()})

    def test_se_instalan_en_la_estructura_que_man_espera(self) -> None:
        """`man` busca por sección: una página suelta en la raíz del MANPATH no la encuentra."""
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            destino = Path(td)
            escritas = manual.instalar_man(destino)
            self.assertEqual(len(escritas), len(manual.paginas_man()))
            self.assertTrue((destino / "man1" / "oracle.1").is_file())
            self.assertTrue((destino / "man7" / "oracle-segun.7").is_file())
            self.assertEqual((destino / "man7" / "oracle-segun.7").read_text(encoding="utf-8"),
                             manual.man("segun"))
            for ruta in escritas:
                self.assertTrue(ruta.is_file(), ruta)

    def test_crea_los_directorios_que_falten_por_el_camino(self) -> None:
        """`man1/` y `man7/` cuelgan del destino, y el destino puede no existir todavía: nadie crea
        `~/.local/share/man` a mano antes de instalar. El test anterior usaba un temporal que YA
        existía, así que no distinguía crear la rama entera de crear un solo nivel."""
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            destino = Path(td) / "sin" / "crear" / "todavia"
            self.assertFalse(destino.exists())
            escritas = manual.instalar_man(destino)
            self.assertTrue((destino / "man7" / "oracle-segun.7").is_file())
            self.assertEqual(len(escritas), len(manual.paginas_man()))

    def test_instalar_dos_veces_no_falla(self) -> None:
        """Se reinstala en cada actualización del paquete; un `mkdir` sin `exist_ok` rompería
        justo la segunda vez, que es la que nadie prueba."""
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            manual.instalar_man(Path(td))
            manual.instalar_man(Path(td))


class MainTests(unittest.TestCase):

    def _correr(self, argv):
        salida, err = io.StringIO(), io.StringIO()
        with redirect_stdout(salida), redirect_stderr(err):
            codigo = manual.main(argv)
        return codigo, salida.getvalue(), err.getvalue()

    def test_sin_argumentos_imprime_el_manual_entero(self) -> None:
        codigo, salida, _ = self._correr([])
        self.assertEqual(codigo, 0)
        self.assertIn("OPERADORES — ", salida)
        self.assertIn("VERBOS — ", salida)

    def test_con_tema_imprime_solo_ese(self) -> None:
        codigo, salida, _ = self._correr(["segun"])
        self.assertEqual(codigo, 0)
        self.assertIn("SEGUN — ", salida)
        self.assertNotIn("OPERADORES — ", salida)

    def test_un_tema_desconocido_falla_y_dice_cuales_hay(self) -> None:
        codigo, salida, err = self._correr(["mengano"])
        self.assertEqual(codigo, 2)
        self.assertEqual(salida, "")
        self.assertIn("mengano", err)
        for tema in manual.temas():
            self.assertIn(tema, err)

    def test_html_emite_html_y_no_texto(self) -> None:
        codigo, salida, _ = self._correr(["--html"])
        self.assertEqual(codigo, 0)
        self.assertIn("<dl>", salida)
        self.assertNotIn("OPERADORES — ", salida)


if __name__ == "__main__":
    unittest.main()
