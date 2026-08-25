"""Tests de la superficie infija de autoría."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from nucleo.medida import rutas_de_catalogo
from tools import sintaxis

RAIZ = Path(__file__).resolve().parents[1]


class SintaxisInfijaTests(unittest.TestCase):
    def test_todas_las_medidas_del_catalogo_vuelven_exactas(self) -> None:
        informe = sintaxis.verificar_catalogo(RAIZ)
        # Contado, no escrito: un 29 a mano vence con cada medida nueva y el test empieza a
        # medir cuántas hay en vez de que todas vuelvan exactas, que es lo que dice medir.
        del_catalogo = len(rutas_de_catalogo(
            RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        self.assertEqual(informe["medidas"], del_catalogo)
        self.assertGreater(del_catalogo, 0)
        self.assertTrue(informe["json_igual"])
        self.assertTrue(informe["texto_igual"])
        self.assertLess(informe["puntuacion_superficie"], informe["puntuacion_json"])
        self.assertTrue(any(p.suffix == ".oracle" for p in sintaxis._rutas_catalogo(RAIZ)))

    def test_los_inventarios_de_catalogo_no_vuelven_a_rglob_json_a_mano(self) -> None:
        def bloque(ruta: Path, inicio: str, fin: str) -> str:
            texto = ruta.read_text(encoding="utf-8")
            return texto.split(inicio, 1)[1].split(fin, 1)[0]

        revisados = (
            (RAIZ / "nucleo" / "medida.py", "def rutas_de_catalogo", "def cargar_fuente_medida"),
            (RAIZ / "tools" / "sintaxis.py", "def _rutas_catalogo", "def _puntuacion"),
            (RAIZ / "tools" / "cifras.py", "def _medidas_universales", "def _lineas"),
            (RAIZ / "tools" / "estudio.py", "def catalogo_en_prosa", "def corpus_en_prosa"),
            (RAIZ / "tools" / "estudio.py", "def numeros", "    casos = "),
        )
        for ruta, inicio, fin in revisados:
            with self.subTest(ruta=ruta.name, inicio=inicio):
                codigo = bloque(ruta, inicio, fin)
                self.assertNotIn('rglob("*.json")', codigo)
                self.assertNotIn('glob("*/*.json")', codigo)

    def test_una_macro_se_relee_como_macro_y_no_como_expansion(self) -> None:
        ruta = RAIZ / "catalogos/meta/meta.donde_compone.json"
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        superficie = sintaxis.imprimir(datos)

        self.assertTrue(superficie.startswith("ninguno meta.donde_compone:"))
        self.assertEqual(sintaxis.leer(superficie), datos)

    def test_una_medida_canonica_preserva_requiere_y_agrupar(self) -> None:
        ruta = RAIZ / "perfiles/python/catalogos/proceso/proceso.modulo_con_consumidor.json"
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        releida = sintaxis.leer(sintaxis.imprimir(datos))

        self.assertEqual(releida, datos)
        self.assertEqual(releida[5], ["requiere", "importa"])
        self.assertEqual(releida[2][2][0], "agrupar")

    def test_imprimir_leer_es_idempotente_sobre_la_superficie_generada(self) -> None:
        datos = ["ninguno", "d.prueba", "pieza", "p",
                 ["y", ["==", ["campo", "p", "mal"], True],
                  [">", ["campo", "p", "n"], 2]],
                 "una razón", "NO ve otros campos"]
        texto = sintaxis.imprimir(datos)

        self.assertEqual(sintaxis.imprimir(sintaxis.leer(texto)), texto)

    def test_un_error_de_expresion_trae_posicion_y_esperado(self) -> None:
        texto = "\n".join([
            "ninguno d.rota:",
            "    de pieza p",
            "    donde p.mal ==",
            "    umbral <= 0 porque \"razón\"",
            "    alcance \"NO ve\"",
        ])

        with self.assertRaises(sintaxis.ErrorSintaxis) as e:
            sintaxis.leer(texto)
        self.assertEqual(e.exception.linea, 3)
        self.assertIn("se esperaba expresión", str(e.exception))

    def test_una_ruta_de_error_se_traduce_a_linea_columna_y_fragmento(self) -> None:
        from nucleo import algebra

        texto = "\n".join([
            "medida d.rota:",
            "    de pieza p",
            "    donde p.x > 0 y p.typo == 2",
            "    resumen contar(1)",
            "    umbral <= 0 porque \"razón\"",
            "    alcance \"NO ve otros campos\"",
        ])
        lectura = sintaxis.leer_con_mapa(texto)

        with self.assertRaises(algebra.ErrorDeAlgebra) as e:
            algebra.desde(lectura.datos[2], {"pieza": [{"x": 1}]})

        self.assertEqual(e.exception.ruta, "2.2.1.2")
        ubicacion = lectura.ubicacion(e.exception.ruta)
        self.assertEqual((ubicacion.linea, ubicacion.columna), (3, 28))

        fragmento = sintaxis.fragmento_de_error(e.exception, texto)
        self.assertIn("en `2.2.1.2`", fragmento)
        self.assertIn("   3 |     donde p.x > 0 y p.typo == 2", fragmento)
        self.assertTrue(fragmento.endswith("^"))

    def test_la_metamorfica_de_sintaxis_juzga_todo_el_catalogo(self) -> None:
        from nucleo.medida import Medida
        from nucleo.proyecto import Proyecto
        from tools import metamorficas

        filas = metamorficas._sintaxis_ida_y_vuelta(Proyecto(RAIZ))
        del_catalogo = len(rutas_de_catalogo(
            RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        self.assertEqual(len(filas), del_catalogo)
        self.assertTrue(all(f["mismo_veredicto"] and f["mismo_valor"] for f in filas))
        # La jueza se busca en el CATÁLOGO, no en el código de la herramienta: estuvo un rato
        # declarada adentro de `metamorficas.py` —consecuencia de una restricción de la tarea que
        # la escribió— y una medida que vive en Python no entra a la mutación ni al inventario de
        # puntos ciegos, que es justo lo que este proyecto le exige a todas las demás.
        import json
        jueza = json.loads(
            (RAIZ / "catalogos/meta/meta.sintaxis_ida_y_vuelta.json").read_text(encoding="utf-8"))
        from nucleo.proyecto import macros_del_proyecto
        m = Medida.de_datos(jueza, macros=macros_del_proyecto(Proyecto(RAIZ)))
        self.assertTrue(m.evaluar({"equivalencia": filas}).ok)


class GramaticaDelIdTests(unittest.TestCase):
    """Un id es un nombre de archivo, y la gramática es UNA SOLA.

    Antes había dos: `ID_MEDIDA_RE` gobernaba la creación (`--nueva`) y la superficie aceptaba
    `\\S+`, cualquier cosa sin espacios. Así `tareas.vencida_sin_dueño` se leía sin una queja pero
    la herramienta se negaba a crearlo, y el catálogo podía guardar ids que el proyecto no sabe
    escribir. La razón del ASCII —dos nombres idénticos en pantalla con bytes distintos, NFC contra
    NFD— está escrita al lado de `ID_MEDIDA_RE`.
    """

    CUERPO = ('\n    de tarea t'
              '\n    donde t.vencida == true'
              '\n    umbral <= 0 porque "una tarea vencida sin dueño no la hace nadie"'
              '\n    alcance "ve el par vencida+sin-dueño. NO ve si quien la tiene puede resolverla"\n')

    def test_la_superficie_acepta_un_id_de_la_gramatica(self) -> None:
        datos = sintaxis.leer("ninguno tareas.vencida_sin_dueno:" + self.CUERPO)
        self.assertEqual(datos[1], "tareas.vencida_sin_dueno")

    def test_la_superficie_rechaza_un_id_fuera_de_la_gramatica(self) -> None:
        for malo in ("tareas.vencida_sin_dueño", "Tareas.mide", "sin_punto", "tareas..mide",
                     "tareas.mide-guion", "1tareas.mide"):
            with self.subTest(malo=malo):
                with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
                    sintaxis.leer(f"ninguno {malo}:" + self.CUERPO)
                self.assertIn("minúsculas ASCII", str(cm.exception))

    def test_el_almacenamiento_no_puede_contrabandear_un_id_que_la_superficie_rechaza(self) -> None:
        """Si sólo lo comprobara la superficie, escribir el JSON a mano saltearía la gramática."""
        from nucleo.medida import Medida, MedidaMalDeclarada
        datos = ["medida", "tareas.vencida_sin_dueño",
                 ["desde", ["de", "tarea", "t"], ["donde", ["==", ["campo", "t", "v"], True]]],
                 ["resumen", "contar", 1],
                 ["umbral", "<=", 0, "una tarea vencida sin dueño no la hace nadie"],
                 ["alcance", "ve el par vencida+sin-dueño"]]
        with self.assertRaises(MedidaMalDeclarada) as cm:
            Medida.de_datos(datos)
        self.assertIn("minúsculas ASCII", str(cm.exception))

    def test_dos_ids_que_se_dibujan_iguales_son_ids_distintos(self) -> None:
        """El peligro concreto que cierra la gramática, demostrado y no afirmado."""
        import unicodedata
        nfc, nfd = "dueño", unicodedata.normalize("NFD", "dueño")
        self.assertNotEqual(nfc, nfd)
        self.assertNotEqual(nfc.encode("utf-8"), nfd.encode("utf-8"))
        from nucleo.proyecto import ID_MEDIDA_RE
        for forma in (nfc, nfd):
            self.assertIsNone(ID_MEDIDA_RE.fullmatch(f"tareas.vencida_sin_{forma}"))


class MedidaNuevaNaceEnLaSuperficieTests(unittest.TestCase):
    def test_el_destino_de_una_medida_nueva_es_la_superficie(self) -> None:
        """El formato en el que se autoriza a alguien a escribir es el primer mensaje del lenguaje."""
        import tempfile
        from nucleo.proyecto import EXTENSION_DE_AUTORIA, Proyecto, ruta_de_medida_nueva
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "catalogos").mkdir()
            destino = ruta_de_medida_nueva(Proyecto(raiz), "tareas.mide")
            self.assertEqual(destino.suffix, EXTENSION_DE_AUTORIA)

    def test_la_plantilla_que_se_entrega_se_lee_y_carga(self) -> None:
        """Una plantilla que no parsea manda a la primera persona que la usa contra la pared."""
        from nucleo.medida import Medida
        from tools.medida import PLANTILLA
        datos = sintaxis.leer(PLANTILLA.format(mid="tareas.mide"))
        self.assertEqual(Medida.de_datos(datos).id, "tareas.mide")


class DocumentacionVerificadaTests(unittest.TestCase):
    """El tutorial afirma que sus ejemplos están verificados contra el código vigente.

    Hasta hoy esa afirmación la sostenía la palabra de quien escribió el documento. Un ejemplo que
    no compila es una afirmación no ejercitada, que es justo lo que el repositorio no acepta en
    ningún otro lado.
    """

    def test_todo_bloque_oracle_de_la_documentacion_lee_y_vuelve_canonico(self) -> None:
        informe = sintaxis.verificar_documentos(RAIZ)
        self.assertEqual(informe["fallas"], [])
        self.assertGreater(informe["ejecutables"], 0)

    def test_un_documento_declarado_que_no_esta_es_un_error(self) -> None:
        """Si faltara en silencio, sacar un documento de la verificación sería renombrarlo."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            informe = sintaxis.verificar_documentos(Path(d))
            self.assertEqual(len(informe["fallas"]), len(sintaxis.DOCUMENTOS_CON_SUPERFICIE))

    def test_un_bloque_roto_se_denuncia_con_documento_y_linea(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            for nombre in sintaxis.DOCUMENTOS_CON_SUPERFICIE:
                (raiz / nombre).write_text("texto\n\n```oracle\nmedida x:\n    de\n```\n",
                                           encoding="utf-8")
            informe = sintaxis.verificar_documentos(raiz)
            self.assertEqual(len(informe["fallas"]), len(sintaxis.DOCUMENTOS_CON_SUPERFICIE))
            self.assertIn(":3:", informe["fallas"][0])

    def test_un_bloque_que_lee_pero_no_es_canonico_tambien_falla(self) -> None:
        """Parsear no alcanza: el documento tiene que mostrar lo que la herramienta imprime."""
        import tempfile
        # `t.vencida==true` sin espacios alrededor del comparador: lee perfecto, pero el impresor
        # pone los espacios. Un documento así enseña una forma que la herramienta no produce.
        cuerpo = ("ninguno tareas.mide:\n"
                  "    de tarea t\n"
                  "    donde t.vencida==true\n"
                  '    umbral <= 0 porque "una tarea vencida sin dueño no la hace nadie"\n'
                  '    alcance "ve el par vencida+sin-dueño"\n')
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            for nombre in sintaxis.DOCUMENTOS_CON_SUPERFICIE:
                (raiz / nombre).write_text(f"```oracle\n{cuerpo}```\n", encoding="utf-8")
            fallas = sintaxis.verificar_documentos(raiz)["fallas"]
            self.assertTrue(fallas)
            self.assertIn("canónica", fallas[0])


if __name__ == "__main__":
    unittest.main()
