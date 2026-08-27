"""Tests de la superficie infija de autoría."""

from __future__ import annotations

import json
import pathlib
import unittest
from pathlib import Path

from nucleo import caso as sintaxis_caso
from nucleo import sintaxis as sintaxis_nucleo
from nucleo.caso import CasoMalDeclarado
from nucleo.medida import rutas_de_catalogo
from nucleo.macro import EXTENSIONES_DE_MACRO
from nucleo.medida import cargar_fuente_medida, ruta_de_medida
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
        del_corpus = len(sintaxis_caso.rutas_de_corpus(RAIZ / "corpus"))
        self.assertEqual(informe["casos"], del_corpus)
        self.assertGreater(del_corpus, 0)
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
        # Por el LECTOR común, no por `json.loads`: la medida está guardada en la superficie y el
        # test habla de la superficie, no del formato en que quedó el archivo.
        datos = cargar_fuente_medida(ruta_de_medida("meta.donde_compone", RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        superficie = sintaxis.imprimir(datos)

        self.assertTrue(superficie.startswith("ninguno meta.donde_compone:"))
        self.assertEqual(sintaxis.leer(superficie), datos)

    def test_una_medida_canonica_preserva_requiere_y_agrupar(self) -> None:
        datos = cargar_fuente_medida(
            ruta_de_medida("proceso.modulo_con_consumidor", RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
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
        jueza = cargar_fuente_medida(
            ruta_de_medida("meta.sintaxis_ida_y_vuelta", RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        from nucleo.proyecto import macros_del_proyecto
        m = Medida.de_datos(jueza, macros=macros_del_proyecto(Proyecto(RAIZ)))
        self.assertTrue(m.evaluar({"equivalencia": filas}).ok)

    def test_la_metamorfica_de_sintaxis_cubre_algebra(self) -> None:
        from nucleo.medida import Medida
        from nucleo.proyecto import Proyecto, macros_del_proyecto
        from tools import metamorficas

        filas = metamorficas._sintaxis_cubre_algebra()
        self.assertGreater(len(filas), 0)
        self.assertTrue(all(f["mismo_veredicto"] and f["mismo_valor"] for f in filas))
        jueza = cargar_fuente_medida(
            ruta_de_medida("meta.sintaxis_cubre_algebra", RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        m = Medida.de_datos(jueza, macros=macros_del_proyecto(Proyecto(RAIZ)))
        self.assertTrue(m.evaluar({"equivalencia": filas}).ok)


class MutacionDeSintaxisTests(unittest.TestCase):
    def _texto(self, lineas: list[str]) -> str:
        return "\n".join(lineas) + "\n"

    def _fragmento_esperado(self, texto: str, linea: int, columna: int,
                            mensaje: str) -> str:
        lineas = texto.splitlines()
        fuente = lineas[linea - 1] if linea <= len(lineas) else ""
        numero = f"{linea:>4}"
        marca = " " * max(columna - 1, 0) + "^"
        return f"{mensaje}\n{numero} | {fuente}\n{' ' * len(numero)} | {marca}"

    def assertErrorDeSintaxis(self, texto: str, linea: int, columna: int,
                              mensaje: str) -> None:
        with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
            sintaxis.leer(texto)
        self.assertEqual(
            sintaxis.fragmento_de_error(cm.exception, texto),
            self._fragmento_esperado(texto, linea, columna, mensaje),
        )

    def assertErrorDirecto(self, funcion, linea: int, columna: int, mensaje: str) -> None:
        with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
            funcion()
        self.assertEqual(str(cm.exception), mensaje)
        self.assertEqual((cm.exception.linea, cm.exception.columna), (linea, columna))

    def assertUbicaciones(self, texto: str, esperadas: dict[str, tuple[int, int]]) -> None:
        lectura = sintaxis.leer_con_mapa(texto)
        for ruta, ubicacion in esperadas.items():
            with self.subTest(ruta=ruta):
                self.assertEqual(lectura.ubicacion(ruta), sintaxis.Ubicacion(*ubicacion))

    def test_los_objetos_de_lectura_son_inmutables_sin_congelar_la_excepcion(self) -> None:
        from dataclasses import FrozenInstanceError, dataclass

        objetos = (
            (sintaxis.ErrorSintaxis(1, 2, "x"), "linea", 9),
            (sintaxis_nucleo.Token("IDENT", "x", 1, 2), "tipo", "NUMBER"),
            (sintaxis.Ubicacion(1, 2), "columna", 9),
            (sintaxis.Lectura([], {}), "version", "0.1"),
            (sintaxis_nucleo._Nodo("x", 1, 2), "valor", "y"),
        )
        for objeto, atributo, valor in objetos:
            with self.subTest(objeto=type(objeto).__name__, atributo=atributo):
                with self.assertRaises(FrozenInstanceError):
                    setattr(objeto, atributo, valor)

        self.assertEqual(
            str(sintaxis.ErrorSintaxis(2, 3, "expresión")),
            "línea 2, columna 3: se esperaba expresión",
        )
        self.assertEqual(
            str(sintaxis.ErrorSintaxis(2, 3, "mensaje literal", literal=True)),
            "línea 2, columna 3: mensaje literal",
        )
        self.assertEqual(
            str(sintaxis.ErrorSintaxis(2, 3, "expresión", "x")),
            "línea 2, columna 3: se esperaba expresión; llegó x",
        )

        with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
            sintaxis_nucleo._fallar(4, 5, "fin")
        self.assertEqual(str(cm.exception), "línea 4, columna 5: se esperaba fin")

        @dataclass(frozen=True)
        class ErrorDePrueba(ValueError):
            valor: int

        self.assertIs(
            sintaxis_nucleo._permitir_atributos_de_excepcion(ErrorDePrueba),
            ErrorDePrueba,
        )
        error = ErrorDePrueba(1)
        error.__traceback__ = None
        error.__cause__ = None
        error.__context__ = None
        error.__suppress_context__ = True
        error.__notes__ = ["nota"]
        self.assertEqual(error.__notes__, ["nota"])
        with self.assertRaises(FrozenInstanceError):
            error.valor = 2

    def test_rutas_tokens_y_parser_de_expresiones_fijan_bordes(self) -> None:
        self.assertEqual(sintaxis_nucleo._normalizar_ruta(""), ())
        self.assertEqual(sintaxis_nucleo._normalizar_ruta("0.2"), (0, 2))
        self.assertEqual(sintaxis_nucleo._normalizar_ruta((0, "2")), (0, 2))
        self.assertEqual(sintaxis_nucleo._texto_ruta((0, 2, 3)), "0.2.3")
        for ruta in ((True,), "1.-1", "a", (-1,)):
            with self.subTest(ruta=ruta):
                with self.assertRaises(ValueError):
                    sintaxis_nucleo._normalizar_ruta(ruta)

        tokens = sintaxis_nucleo._tokenizar("a<=b a<b", 7, 3)
        self.assertEqual(
            [(t.tipo, t.valor, t.linea, t.columna) for t in tokens],
            [
                ("IDENT", "a", 7, 3),
                ("OP", "<=", 7, 4),
                ("IDENT", "b", 7, 6),
                ("IDENT", "a", 7, 8),
                ("OP", "<", 7, 9),
                ("IDENT", "b", 7, 10),
                ("EOF", "", 7, 11),
            ],
        )

        fin = sintaxis_nucleo._Expr(
            sintaxis_nucleo._tokenizar("porque", 1, 1), detener={"porque"})
        self.assertIs(fin._fin(), True)
        no_fin = sintaxis_nucleo._Expr(
            sintaxis_nucleo._tokenizar("x", 1, 1), detener={"porque"})
        self.assertIs(no_fin._fin(), False)
        self.assertIsNone(no_fin._tomar("NUMBER"))
        self.assertEqual(no_fin.i, 0)
        self.assertIsNone(no_fin._tomar("IDENT", "otro"))
        self.assertEqual(no_fin.i, 0)
        self.assertEqual(no_fin._tomar("IDENT", "x").valor, "x")
        self.assertEqual(no_fin.i, 1)

        self.assertEqual(sintaxis_nucleo._leer_expr("hecho(alias)", 8, 9),
                         ["hecho", "alias"])
        self.assertEqual(sintaxis_nucleo._leer_expr("col(nombre)", 8, 9),
                         ["col", "nombre"])
        for expr, mensaje in (
            ("hecho(1)", "línea 8, columna 9: se esperaba hecho(alias)"),
            ("hecho(a, b)", "línea 8, columna 9: se esperaba hecho(alias)"),
            ("col(1)", "línea 8, columna 9: se esperaba col(nombre)"),
            ("col(a, b)", "línea 8, columna 9: se esperaba col(nombre)"),
        ):
            with self.subTest(expr=expr):
                self.assertErrorDirecto(lambda expr=expr: sintaxis_nucleo._leer_expr(expr, 8, 9),
                                        8, 9, mensaje)

    def test_helpers_textuales_fallan_cerrado_con_posicion_exacta(self) -> None:
        self.assertEqual(sintaxis_nucleo._literal_texto("$razon", 3, 7), ["$", "razon"])
        self.assertEqual(
            sintaxis_nucleo._leer_umbral('<= 0 porque $porque', 2, 5),
            ("<=", 0, ["$", "porque"], 10),
        )
        self.assertEqual(
            sintaxis_nucleo._lineas(" \n# comentario\nmedida d.x:  \n"),
            [(3, "medida d.x:")],
        )
        self.assertEqual(sintaxis_nucleo._indentada("    donde x", 1, 3), "donde x")
        self.assertEqual(
            sintaxis_nucleo._exigir_prefijo((3, "    donde x"), "donde ", 1),
            ("x", 11),
        )
        self.assertEqual(
            sintaxis_nucleo._contenido((4, '    alcance "x"'), "alcance ", 1),
            ('"x"', 4, 13),
        )
        self.assertEqual(sintaxis_nucleo._leer_nombre("$rel", 1, 8), ["$", "rel"])
        self.assertEqual(
            sintaxis_nucleo._leer_de((6, "    de $rel $alias")),
            ["de", ["$", "rel"], ["$", "alias"]],
        )
        self.assertEqual(
            sintaxis_nucleo._leer_de((6, "    unir rel r"), "unir"),
            ["de", "rel", "r"],
        )
        self.assertEqual(
            sintaxis_nucleo._leer_requiere((7, "    requiere $rel, otra")),
            ["requiere", ["$", "rel"], "otra"],
        )
        self.assertEqual(
            sintaxis_nucleo._huecos_en_linea('guarda x "a\\n" $hueco'),
            [("hueco", 16)],
        )
        ubicaciones: dict[str, sintaxis.Ubicacion] = {}
        self.assertEqual(
            sintaxis_nucleo._leer_resumen(
                (8, "    resumen contar(1)"), ubicaciones=ubicaciones),
            ["resumen", "contar", 1],
        )
        self.assertEqual(ubicaciones["3"], sintaxis.Ubicacion(8, 13))
        self.assertEqual(ubicaciones["3.0"], sintaxis.Ubicacion(8, 13))
        self.assertEqual(ubicaciones["3.1"], sintaxis.Ubicacion(8, 13))
        self.assertEqual(ubicaciones["3.2"], sintaxis.Ubicacion(8, 20))

        casos = (
            (lambda: sintaxis_nucleo._literal_texto("1", 4, 5), 4, 5,
             "línea 4, columna 5: se esperaba texto entre comillas; llegó 1"),
            (lambda: sintaxis_nucleo._literal_texto('"x" 1', 4, 5), 4, 9,
             "línea 4, columna 9: se esperaba fin de línea; llegó 1"),
            (lambda: sintaxis_nucleo._leer_umbral('0 porque "x"', 2, 5), 2, 5,
             "línea 2, columna 5: se esperaba comparador de umbral; llegó 0"),
            (lambda: sintaxis_nucleo._leer_umbral("<= 0 porque 1", 2, 5), 2, 17,
             "línea 2, columna 17: se esperaba texto de defensa del umbral; llegó 1"),
            (lambda: sintaxis_nucleo._leer_umbral('"<= 0" porque "x"', 2, 5), 2, 5,
             "línea 2, columna 5: se esperaba comparador de umbral; llegó '<= 0'"),
            (lambda: sintaxis_nucleo._indentada("sin indentación", 1, 5), 5, 1,
             "línea 5, columna 1: se esperaba indentación de 4 espacios; llegó 's'"),
            (lambda: sintaxis_nucleo._indentada("     de rel r", 1, 6), 6, 6,
             "línea 6, columna 6: se esperaba indentación de 4 espacios; llegó '     d'"),
            (lambda: sintaxis_nucleo._exigir_prefijo((3, "    umbral x"), "donde ", 1), 3, 5,
             "línea 3, columna 5: se esperaba línea «donde»; llegó 'umbral x'"),
            (lambda: sintaxis_nucleo._leer_nombre("$", 3, 7), 3, 7,
             "línea 3, columna 7: se esperaba nombre de parámetro después de «$»; llegó '$'"),
            (lambda: sintaxis_nucleo._leer_nombre("$1x", 3, 7), 3, 7,
             "línea 3, columna 7: se esperaba nombre de parámetro después de «$»; llegó '$1x'"),
            (lambda: sintaxis_nucleo._leer_de((6, "    de rel")), 6, 8,
             "línea 6, columna 8: se esperaba de <relación> <alias>; llegó 'rel'"),
            (lambda: sintaxis_nucleo._leer_de((6, "    de $ alias")), 6, 8,
             "línea 6, columna 8: se esperaba nombre de parámetro después de «$»; llegó '$'"),
            (lambda: sintaxis_nucleo._leer_de((6, "    de rel $")), 6, 12,
             "línea 6, columna 12: se esperaba nombre de parámetro después de «$»; llegó '$'"),
            (lambda: sintaxis_nucleo._leer_requiere((7, "    requiere rel, ")), 7, 14,
             "línea 7, columna 14: se esperaba una o más relaciones requeridas; llegó 'rel, '"),
            (lambda: sintaxis_nucleo._leer_requiere((7, "    requiere $")), 7, 14,
             "línea 7, columna 14: se esperaba nombre de parámetro después de «$»; llegó '$'"),
            (lambda: sintaxis_nucleo._leer_umbral('123 <= 0 porque "x"', 2, 5), 2, 5,
             "línea 2, columna 5: se esperaba comparador de umbral; llegó 123"),
            (lambda: sintaxis_nucleo._macro_ninguno("ninguno", "d.m", [
                (10, "    de pieza p"), (11, "    donde p.x == 1"),
                (12, '    umbral <= 0 porque "defensa valida y suficiente"'),
                (13, '    alcance "nada"'), (14, "    sobra")]), 14, 1,
             "línea 14, columna 1: la macro ninguno lleva exactamente 4 líneas de cuerpo "
             "(de, donde, umbral, alcance) y llegaron 5"),
            (lambda: sintaxis_nucleo._macro_ninguno("ninguno", "d.m", [
                (10, "    de pieza p"), (11, "    donde p.x == 1"),
                (12, '    umbral <= 0 porque "defensa valida y suficiente"')]), 13, 1,
             "línea 13, columna 1: a la macro ninguno le falta `alcance`. Su cuerpo son estas "
             "4 líneas, en este orden: de, donde, umbral, alcance"),
            (lambda: sintaxis_nucleo._macro_ninguno_par("d.m", [
                (10, "    de pieza a, b"), (11, "    donde a.x == b.x")]), 10, 1,
             "línea 10, columna 1: se esperaba 4 líneas de cuerpo para ninguno-par"),
            (lambda: sintaxis_nucleo._macro_peor("d.m", [
                (20, "    de pieza p"), (21, "    expresion p.x")]), 20, 1,
             "línea 20, columna 1: se esperaba 5 líneas de cuerpo para peor"),
            (lambda: sintaxis_nucleo._leer_plantilla([
                (1, "    medida $123:"), (2, "        de pieza p")]), 1, 12,
             "línea 1, columna 12: se esperaba nombre de parámetro después de «$»; llegó '$123'"),
        )
        for funcion, linea, columna, mensaje in casos:
            with self.subTest(mensaje=mensaje):
                self.assertErrorDirecto(funcion, linea, columna, mensaje)

    def test_ubicaciones_de_superficie_quedan_fijadas(self) -> None:
        medida = self._texto([
            "medida d.completa:",
            "    de rel r",
            "    unir otra o",
            "    donde r.x == true",
            "    donde o.y > 2",
            "    agrupar:",
            "        clave k = r.x",
            "        agregado total = contar(o.y)",
            "    resumen max(total)",
            '    umbral <= 0 porque "razón"',
            "    requiere rel, otra",
            '    alcance "NO ve más"',
        ])
        self.assertUbicaciones(medida, {
            "": (1, 1),
            "0": (1, 1),
            "1": (1, 8),
            "2.2": (4, 5),
            "2.2.0": (4, 5),
            "2.2.1": (4, 15),
            "2.2.1.1.2": (4, 13),
            "2.2.1.2": (4, 18),
            "2.3": (5, 5),
            "2.3.1.1.2": (5, 13),
            "2.4": (6, 5),
            "2.4.0": (6, 5),
            "2.4.1.0": (7, 15),
            "2.4.1.0.1": (7, 19),
            "2.4.2.0": (8, 18),
            "2.4.2.0.0": (8, 18),
            "2.4.2.0.1": (8, 26),
            "2.4.2.0.2.2": (8, 35),
            "2.4.1.0.0": (7, 15),
            "3": (9, 13),
            "3.0": (9, 13),
            "3.1": (9, 13),
            "3.2": (9, 17),
            "3.2.1": (9, 17),
        })
        self.assertEqual(sintaxis.leer_con_mapa(medida).ubicacion((2, 4, 2, 0, 2, 2)),
                         sintaxis.Ubicacion(8, 35))

        self.assertUbicaciones(self._texto([
            "ninguno d.n:",
            "    de rel r",
            "    donde r.x == true",
            '    umbral <= 0 porque "razón"',
            '    alcance "NO ve"',
        ]), {
            "1": (1, 9),
            "4": (3, 15),
            "4.1.2": (3, 13),
            "4.2": (3, 18),
        })
        self.assertUbicaciones(self._texto([
            "ninguno-par d.n:",
            "    de rel a, b",
            "    donde a.x == b.x",
            '    umbral <= 0 porque "razón"',
            '    alcance "NO ve"',
        ]), {
            "1": (1, 13),
            "5": (3, 15),
            "5.1.2": (3, 13),
            "5.2.2": (3, 20),
        })
        self.assertUbicaciones(self._texto([
            "peor d.p:",
            "    de rel r",
            "    expresion r.x",
            "    tolerancia 2",
            '    umbral <= 2 porque "razón"',
            '    alcance "NO ve"',
        ]), {
            "1": (1, 6),
            "4": (3, 15),
            "4.2": (3, 17),
            "5": (4, 16),
        })

    def test_errores_de_medidas_y_macros_fijan_fragmentos(self) -> None:
        casos = [
            # El mensaje NOMBRA la línea que falta. «se esperaba 4 líneas» es cierto y no dice
            # cuál de las cuatro se olvidó.
            ("ninguno sin cuerpo", "ninguno d.n:\n", 2, 1,
             "línea 2, columna 1: a la macro ninguno le falta `de`, `donde`, `umbral`, "
             "`alcance`. Su cuerpo son estas 4 líneas, en este orden: de, donde, umbral, alcance"),
            ("ninguno incompleto", self._texto(["ninguno d.n:", "    de rel r"]), 3, 1,
             "línea 3, columna 1: a la macro ninguno le falta `donde`, `umbral`, `alcance`. "
             "Su cuerpo son estas 4 líneas, en este orden: de, donde, umbral, alcance"),
            ("ninguno largo", self._texto([
                "ninguno d.n:", "    de rel r", "    donde r.x == true",
                '    umbral <= 0 porque "razón"', '    alcance "NO ve"', "    sobra"]), 6, 1,
             "línea 6, columna 1: la macro ninguno lleva exactamente 4 líneas de cuerpo "
             "(de, donde, umbral, alcance) y llegaron 5"),
            ("ninguno umbral", self._texto([
                "ninguno d.n:", "    de rel r", "    donde r.x == true",
                '    umbral < 0 porque "razón"', '    alcance "NO ve"']), 4, 16,
             "línea 4, columna 16: la macro ninguno cuenta lo que ofende, así que su umbral es "
             "siempre «<= 0» y llegó «< 0»"),
            ("ninguno-par sin cuerpo", "ninguno-par d.n:\n", 2, 1,
             "línea 2, columna 1: se esperaba 4 líneas de cuerpo para ninguno-par"),
            ("ninguno-par de", self._texto([
                "ninguno-par d.n:", "    de rel a b", "    donde a.x == b.x",
                '    umbral <= 0 porque "razón"', '    alcance "NO ve"']), 2, 8,
             "línea 2, columna 8: se esperaba de <relación> <aliasA>, <aliasB>; "
             "llegó 'rel a b'"),
            ("ninguno-par umbral operador", self._texto([
                "ninguno-par d.n:", "    de rel a, b", "    donde a.x == b.x",
                '    umbral < 0 porque "razón"', '    alcance "NO ve"']), 4, 16,
             "línea 4, columna 16: se esperaba la macro ninguno-par con umbral <= 0"),
            ("ninguno-par umbral limite", self._texto([
                "ninguno-par d.n:", "    de rel a, b", "    donde a.x == b.x",
                '    umbral <= 1 porque "razón"', '    alcance "NO ve"']), 4, 17,
             "línea 4, columna 17: se esperaba la macro ninguno-par con umbral <= 0"),
            ("peor sin cuerpo", "peor d.p:\n", 2, 1,
             "línea 2, columna 1: se esperaba 5 líneas de cuerpo para peor"),
            ("peor umbral operador", self._texto([
                "peor d.p:", "    de rel r", "    expresion r.x", "    tolerancia 2",
                '    umbral < 2 porque "razón"', '    alcance "NO ve"']), 5, 16,
             "línea 5, columna 16: se esperaba la macro peor con umbral <= tolerancia"),
            ("peor umbral", self._texto([
                "peor d.p:", "    de rel r", "    expresion r.x", "    tolerancia 2",
                '    umbral <= 3 porque "razón"', '    alcance "NO ve"']), 5, 17,
             "línea 5, columna 17: se esperaba la macro peor con umbral <= tolerancia"),
            ("medida vacía", "medida d.vacia:\n", 2, 1,
             "línea 2, columna 1: se esperaba cuerpo de medida"),
            ("falta resumen", self._texto(["medida d.r:", "    de rel r"]), 3, 1,
             "línea 3, columna 1: se esperaba resumen"),
            ("falta resumen tras unir", self._texto([
                "medida d.r:", "    de rel r", "    unir otra o"]), 4, 1,
             "línea 4, columna 1: se esperaba resumen"),
            ("falta umbral", self._texto([
                "medida d.r:", "    de rel r", "    resumen contar(1)"]), 4, 1,
             "línea 4, columna 1: se esperaba umbral"),
            ("falta alcance", self._texto([
                "medida d.r:", "    de rel r", "    resumen contar(1)",
                '    umbral <= 0 porque "razón"']), 5, 1,
             "línea 5, columna 1: se esperaba alcance"),
            ("extra final", self._texto([
                "medida d.r:", "    de rel r", "    resumen contar(1)",
                '    umbral <= 0 porque "razón"', '    alcance "NO ve"', "    sobra"]), 6, 5,
             "línea 6, columna 5: se esperaba fin de medida; llegó 'sobra'"),
            ("agrupar sin agregado", self._texto([
                "medida d.r:", "    de rel r", "    agrupar:", "        clave k = r.x",
                "    resumen contar(1)", '    umbral <= 0 porque "razón"',
                '    alcance "NO ve"']), 3, 5,
             "línea 3, columna 5: se esperaba al menos un agregado"),
            ("agrupar hijo malo", self._texto([
                "medida d.r:", "    de rel r", "    agrupar:", "        raro k = r.x",
                "        agregado total = contar(1)", "    resumen contar(1)",
                '    umbral <= 0 porque "razón"', '    alcance "NO ve"']), 4, 9,
             "línea 4, columna 9: se esperaba clave o agregado; llegó 'raro k = r.x'"),
            ("agrupar hasta eof", self._texto([
                "medida d.r:", "    de rel r", "    agrupar:",
                "        agregado total = contar(1)"]), 5, 1,
             "línea 5, columna 1: se esperaba resumen"),
            ("agregado sin separador", self._texto([
                "medida d.r:", "    de rel r", "    agrupar:",
                "        agregado total contar(1)", "    resumen contar(1)",
                '    umbral <= 0 porque "razón"', '    alcance "NO ve"']), 4, 18,
             "línea 4, columna 18: se esperaba agregado <nombre> = agregado(expr); "
             "llegó 'total contar(1)'"),
            ("agregado sin nombre", self._texto([
                "medida d.r:", "    de rel r", "    agrupar:",
                "        agregado  = contar(1)", "    resumen contar(1)",
                '    umbral <= 0 porque "razón"', '    alcance "NO ve"']), 4, 18,
             "línea 4, columna 18: se esperaba agregado <nombre> = agregado(expr); "
             "llegó ' = contar(1)'"),
            ("agregado malo", self._texto([
                "medida d.r:", "    de rel r", "    agrupar:",
                "        agregado total = 1", "    resumen contar(1)",
                '    umbral <= 0 porque "razón"', '    alcance "NO ve"']), 4, 26,
             "línea 4, columna 26: se esperaba llamada de agregado; llegó '1'"),
            ("clave sin separador", self._texto([
                "medida d.r:", "    de rel r", "    agrupar:",
                "        clave k r.x", "        agregado total = contar(1)",
                "    resumen contar(1)", '    umbral <= 0 porque "razón"',
                '    alcance "NO ve"']), 4, 15,
             "línea 4, columna 15: se esperaba clave <nombre> = expresión; llegó 'k r.x'"),
            ("clave sin nombre", self._texto([
                "medida d.r:", "    de rel r", "    agrupar:",
                "        clave  = r.x", "        agregado total = contar(1)",
                "    resumen contar(1)", '    umbral <= 0 porque "razón"',
                '    alcance "NO ve"']), 4, 15,
             "línea 4, columna 15: se esperaba clave <nombre> = expresión; llegó ' = r.x'"),
            ("resumen malo", self._texto([
                "medida d.r:", "    de rel r", "    resumen 1",
                '    umbral <= 0 porque "razón"', '    alcance "NO ve"']), 3, 13,
             "línea 3, columna 13: se esperaba resumen agregado(expr); llegó '1'"),
            ("requiere mal indentado", self._texto([
                "medida d.r:", "    de rel r", "    resumen contar(1)",
                '    umbral <= 0 porque "razón"', "     requiere rel",
                '    alcance "NO ve"']), 5, 6,
             "línea 5, columna 6: se esperaba indentación de 4 espacios; llegó '     r'"),
        ]
        for nombre, texto, linea, columna, mensaje in casos:
            with self.subTest(nombre=nombre):
                self.assertErrorDeSintaxis(texto, linea, columna, mensaje)

    def test_defmacro_cubre_plantillas_guardas_y_huecos(self) -> None:
        variantes = {
            "ninguno": self._texto([
                "defmacro todos(id, rel, alias, pred, porque, alcance):",
                "    ninguno $id:",
                "        de $rel $alias",
                "        donde $pred",
                "        umbral <= 0 porque $porque",
                "        alcance $alcance",
            ]),
            "ninguno-par": self._texto([
                "defmacro pares(id, rel, a, b, pred, porque, alcance):",
                "    ninguno-par $id:",
                "        de $rel $a, $b",
                "        donde $pred",
                "        umbral <= 0 porque $porque",
                "        alcance $alcance",
            ]),
            "peor": self._texto([
                "defmacro peor-propia(id, rel, alias, expr, tol, porque, alcance):",
                "    peor $id:",
                "        de $rel $alias",
                "        expresion $expr",
                "        tolerancia $tol",
                "        umbral <= $tol porque $porque",
                "        alcance $alcance",
            ]),
        }
        for clase, texto in variantes.items():
            with self.subTest(clase=clase):
                datos = sintaxis.leer(texto)
                self.assertEqual(datos[4][0], clase)
                self.assertEqual(sintaxis.leer(sintaxis.imprimir(datos)), datos)

        macro = variantes["ninguno"]
        lectura = sintaxis.leer_con_mapa(macro)
        self.assertEqual(lectura.ubicacion(""), sintaxis.Ubicacion(1, 1))
        self.assertEqual(lectura.ubicacion("0"), sintaxis.Ubicacion(1, 1))
        self.assertEqual(lectura.ubicacion("1"), sintaxis.Ubicacion(1, 10))

        linea = 'guarda $id != "$no \\" $tampoco" y $otro'
        self.assertEqual(
            sintaxis_nucleo._huecos_en_linea(linea),
            [("id", linea.index("$id") + 1), ("otro", linea.index("$otro") + 1)],
        )
        empieza_con_hueco = "$id y $otro"
        self.assertEqual(
            sintaxis_nucleo._huecos_en_linea(empieza_con_hueco),
            [("id", 1), ("otro", empieza_con_hueco.index("$otro") + 1)],
        )
        cierre_saltado = '"" $visible'
        self.assertEqual(
            sintaxis_nucleo._huecos_en_linea(cierre_saltado),
            [("visible", cierre_saltado.index("$visible") + 1)],
        )
        escape = '"\\\\$no" $si'
        self.assertEqual(
            sintaxis_nucleo._huecos_en_linea(escape),
            [("si", escape.index("$si") + 1)],
        )

        casos = [
            ("sin cuerpo", "defmacro m(id):\n", 2, 1,
             "línea 2, columna 1: se esperaba plantilla de la macro"),
            ("sin plantilla", self._texto([
                "defmacro m(id):", '    guarda $id != 1 "x"']), 3, 1,
             "línea 3, columna 1: se esperaba plantilla de la macro"),
            # La columna es la del TOKEN que ofende —el `"msg"` donde iba la expresión—, no la de
            # la palabra `guarda`. Señalar la palabra clave manda a mirar lo que está bien.
            ("guarda sin expresion", self._texto(["defmacro m(id):", '    guarda "msg"']), 2, 12,
             "línea 2, columna 12: se esperaba expresión de la guarda; llegó '\"msg\"'"),
            ("plantilla mala", self._texto(["defmacro m(id):", "    nada $id:"]), 2, 5,
             "línea 2, columna 5: se esperaba plantilla "
             "«medida|ninguno|ninguno-par|ninguno-unir|peor <id>:»; llegó 'nada $id:'"),
            ("plantilla con id hueco invalido", self._texto([
                "defmacro m(id):", "    medida $:"]), 2, 12,
             "línea 2, columna 12: se esperaba nombre de parámetro después de «$»; llegó '$'"),
            ("hueco no declarado", self._texto([
                "defmacro propia(id):", "    medida $id:", "        de rel r",
                "        donde r.x == $inventado", "        resumen contar(1)",
                '        umbral <= 0 porque "razón"', '        alcance "NO ve"']), 4, 22,
             "línea 4, columna 22: «$inventado» no es un parámetro de la macro; "
             "llegó 'donde r.x == $inventado'"),
            ("parametro sin usar", self._texto([
                "defmacro propia(id, sobra):", "    medida $id:", "        de rel r",
                "        resumen contar(1)", '        umbral <= 0 porque "razón"',
                '        alcance "NO ve"']), 1, 21,
             "línea 1, columna 21: la macro declara el parámetro «sobra» y la plantilla "
             "nunca lo usa; llegó 'defmacro propia(id, sobra):'"),
        ]
        for nombre, texto, linea, columna, mensaje in casos:
            with self.subTest(nombre=nombre):
                self.assertErrorDeSintaxis(texto, linea, columna, mensaje)

    def test_encabezados_version_y_fragmentos_fallan_cerrado(self) -> None:
        cuerpo = self._texto([
            "ninguno d.n:",
            "    de rel r",
            "    donde r.x == true",
            '    umbral <= 0 porque "razón"',
            '    alcance "NO ve"',
        ])
        lectura = sintaxis.leer_con_mapa("# comentario\nsintaxis 0.1\n" + cuerpo)
        self.assertEqual(lectura.version, "0.1")
        self.assertEqual(lectura.ubicacion(""), sintaxis.Ubicacion(3, 1))
        self.assertEqual(lectura.ubicacion("1"), sintaxis.Ubicacion(3, 9))

        casos = [
            ("vacio", "", 1, 1,
             "línea 1, columna 1: se esperaba encabezado de medida"),
            ("version sola", "sintaxis 0.1\n", 2, 1,
             "línea 2, columna 1: se esperaba encabezado de medida"),
            ("version mala", "sintaxis 0\n" + cuerpo, 1, 10,
             "línea 1, columna 10: versión «'0'» inválida: se espera MAYOR.MENOR con "
             "enteros no negativos"),
            ("defmacro sin parametros", "defmacro m():\n", 1, 1,
             "línea 1, columna 1: se esperaba parámetros de la macro; llegó 'defmacro m():'"),
            ("defmacro parametro malo", "defmacro m(1x):\n", 1, 12,
             "línea 1, columna 12: se esperaba nombre de parámetro, no «1x»; "
             "llegó 'defmacro m(1x):'"),
            ("defmacro parametro repetido", "defmacro m(x, x):\n", 1, 1,
             "línea 1, columna 1: se esperaba parámetros sin repetir; llegó 'defmacro m(x, x):'"),
            ("id malo", cuerpo.replace("ninguno d.n:", "ninguno d:"), 1, 9,
             "línea 1, columna 9: se esperaba id «dominio.nombre», sólo con minúsculas "
             "ASCII, dígitos y `_`; llegó 'd'"),
            ("encabezado malo", "nada\n", 1, 1,
             "línea 1, columna 1: se esperaba encabezado «medida|ninguno|ninguno-par|"
             "ninguno-unir|peor "
             "<id>:»; llegó 'nada'"),
        ]
        for nombre, texto, linea, columna, mensaje in casos:
            with self.subTest(nombre=nombre):
                self.assertErrorDeSintaxis(texto, linea, columna, mensaje)

        self.assertEqual(sintaxis.fragmento_de_error(ValueError("sin posición"), cuerpo),
                         "sin posición")

        class SoloLinea(Exception):
            linea = 1

        class SoloColumna(Exception):
            columna = 1

        self.assertEqual(sintaxis.fragmento_de_error(SoloLinea("sin columna"), cuerpo),
                         "sin columna")
        self.assertEqual(sintaxis.fragmento_de_error(SoloColumna("sin línea"), cuerpo),
                         "sin línea")

        class ErrorConRuta(Exception):
            ruta = "99.99"

        self.assertEqual(
            sintaxis.fragmento_de_error(ErrorConRuta("ruta rota"), cuerpo),
            "ruta rota\n(no se encontró la ruta 99.99)",
        )

    def test_impresion_fija_precedencia_y_formas_invalidas(self) -> None:
        self.assertTrue(sintaxis_nucleo._es_hueco(["$", "param"]))
        self.assertFalse(sintaxis_nucleo._es_hueco(["param", "$"]))
        self.assertEqual(sintaxis_nucleo._nombre(["$", "param"]), "$param")
        self.assertEqual(sintaxis_nucleo._nombre("rel"), "rel")
        self.assertEqual(sintaxis_nucleo._texto_o_hueco(["$", "param"]), "$param")
        self.assertEqual(sintaxis_nucleo._texto_o_hueco("razon"), '"razon"')
        self.assertEqual(sintaxis_nucleo._expr(["$", "param"]), "$param")
        self.assertEqual(
            sintaxis_nucleo._expr(["no", ["no", ["col", "x"]]]),
            "no no x",
        )
        self.assertEqual(
            sintaxis_nucleo._expr(["no", ["y", True, False]]),
            "no (true y false)",
        )
        self.assertEqual(
            sintaxis_nucleo._expr(["no", ["o", True, False]]),
            "no (true o false)",
        )
        self.assertEqual(
            sintaxis_nucleo._expr(["y", ["o", True, False], True]),
            "(true o false) y true",
        )
        self.assertEqual(
            sintaxis_nucleo._expr(["o", ["y", True, False], True]),
            "true y false o true",
        )
        self.assertEqual(
            sintaxis_nucleo._expr(["no", ["contar", 1]]),
            "no contar(1)",
        )
        self.assertEqual(
            sintaxis_nucleo._expr(["==", ["contar", 1], 1]),
            "contar(1) == 1",
        )
        self.assertEqual(
            sintaxis_nucleo._expr(["y", ["==", ["col", "x"], 1], ["==", ["col", "y"], 2]]),
            "x == 1 y y == 2",
        )
        self.assertEqual(
            sintaxis_nucleo._expr(["==", ["y", True, False], True]),
            "(true y false) == true",
        )
        self.assertEqual(
            sintaxis_nucleo._expr(["no", ["==", ["col", "x"], 1]]),
            "no (x == 1)",
        )
        self.assertEqual(
            sintaxis_nucleo._expr(["y", ["y", True, False], True]),
            "true y false y true",
        )
        datos = ["medida", "d.impresa",
                 ["desde", ["unir", ["de", "rel", "r"], ["de", "otra", "o"]],
                  ["donde", ["==", ["y", True, False], True]],
                  ["agrupar", [["k", ["campo", "r", "x"]]],
                   [["total", "contar", ["campo", "o", "y"]]]]],
                 ["resumen", "max", ["col", "total"]],
                 ["umbral", "<=", ["no", ["==", ["col", "total"], 1]], "razón"],
                 ["requiere", "rel", "otra"],
                 ["alcance", "NO ve"]]
        texto = sintaxis.imprimir(datos)
        self.assertIn("    unir otra o\n", texto)
        self.assertIn("    donde (true y false) == true\n", texto)
        self.assertIn("        clave k = r.x\n", texto)
        self.assertIn("        agregado total = contar(o.y)\n", texto)
        self.assertIn("    requiere rel, otra\n", texto)
        self.assertEqual(sintaxis.leer(texto), datos)

        for invalido in ([], "x"):
            with self.subTest(invalido=invalido):
                with self.assertRaises(ValueError):
                    sintaxis.imprimir(invalido)
        with self.assertRaises(ValueError):
            sintaxis_nucleo._lineas_fuente(["otro"])
        with self.assertRaises(ValueError):
            sintaxis_nucleo._lineas_fuente(["unir", ["de", "rel", "r"], ["otra"]])
        with self.assertRaises(ValueError):
            sintaxis_nucleo._imprimir_pasos(["desde", ["de", "rel", "r"], ["raro"]])


class SintaxisDeCasosTests(unittest.TestCase):
    def _caso_base(self, evidencia=None) -> dict:
        return {
            "id": "999-caso-de-prueba",
            "fecha": "2026-08-25",
            "origen": {"repo": "test", "commit": "local"},
            "titulo": "Caso de prueba",
            "etiqueta": "verde_correcto",
            "sintoma": "Prosa con `backticks`, comillas \"dobles\" y coma, sin escapar.",
            "como_se_detecto": "observacion",
            "medida": "demo.mide",
            "evidencia": evidencia or {"hecho": [{"id": "a", "ok": True}]},
            "leccion": "La prosa vuelve igual.",
        }

    def _superficie_base(self, evidencia=None) -> str:
        return sintaxis_caso.imprimir(self._caso_base(evidencia))

    def _texto(self, lineas: list[str]) -> str:
        return "\n".join(lineas) + "\n"

    def _fragmento_esperado(self, texto: str, linea: int, columna: int,
                            mensaje: str) -> str:
        lineas = texto.splitlines()
        fuente = lineas[linea - 1] if linea <= len(lineas) else ""
        numero = f"{linea:>4}"
        marca = " " * max(columna - 1, 0) + "^"
        return f"{mensaje}\n{numero} | {fuente}\n{' ' * len(numero)} | {marca}"

    def assertErrorDeCaso(self, texto: str, linea: int, columna: int,
                          mensaje: str) -> None:
        with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
            sintaxis_caso.leer(texto)
        self.assertEqual(
            sintaxis.fragmento_de_error(cm.exception, texto),
            self._fragmento_esperado(texto, linea, columna, mensaje),
        )

    def test_los_errores_de_caso_fijan_linea_columna_y_encontrado(self) -> None:
        base = self._superficie_base()

        def con(reemplazos=(), borrar=()):
            lineas = base.splitlines()
            for numero in sorted(borrar, reverse=True):
                del lineas[numero - 1]
            for numero, contenido in reemplazos:
                lineas[numero - 1] = contenido
            return self._texto(lineas)

        def insertando(*inserciones):
            lineas = base.splitlines()
            for numero, contenido in inserciones:
                lineas.insert(numero - 1, contenido)
            return self._texto(lineas)

        escape = self._superficie_base({"hecho": [{"id": "a"}]})
        escape_lineas = escape.splitlines()
        escape_lineas[12] = "        hecho:"
        escape_lineas[13] = "            fila nope"
        fila_json_rota = self._texto(escape_lineas)
        escape_lineas = escape.splitlines()
        escape_lineas[12] = "        hecho:"
        escape_lineas[13] = '            "a"'
        fila_sin_encabezado = self._texto(escape_lineas)

        casos = [
            ("entrada vacía", "", 1, 1,
             "línea 1, columna 1: se esperaba encabezado «caso <id>:»"),
            ("sólo encabezado", "caso 999-roto:\n", 2, 1,
             "línea 2, columna 1: se esperaba línea «fecha:»"),
            ("indentación extra", con([(2, '     fecha: "2026-08-25"')]), 2, 6,
             "línea 2, columna 6: se esperaba indentación de 4 espacios; llegó '     f'"),
            ("fecha sin espacio", con([(2, '    fecha:"2026-08-25"')]), 2, 11,
             "línea 2, columna 11: se esperaba espacio o fin tras ':'; llegó "
             "'\"2026-08-25\"'"),
            ("fecha sin valor", con([(2, "    fecha:")]), 2, 11,
             "línea 2, columna 11: se esperaba texto entre comillas"),
            ("fecha no JSON", con([(2, "    fecha: nope")]), 2, 12,
             "línea 2, columna 12: se esperaba texto entre comillas; llegó 'nope'"),
            ("fecha sin comillas", con([(2, "    fecha: 2026-08-26")]), 2, 16,
             "línea 2, columna 16: se esperaba texto entre comillas; llegó '-08-26'"),
            ("falta titulo", con(borrar=(6,)), 6, 5,
             "línea 6, columna 5: se esperaba línea «titulo:»; llegó "
             "'etiqueta: verde_correcto'"),
            ("etiqueta inventada", con([(7, "    etiqueta: rojo_feo")]), 7, 15,
             "línea 7, columna 15: se esperaba etiqueta en ['deuda_de_diseño', "
             "'falso_rojo', 'falso_verde', 'medida_correcta_conclusion_errada', "
             "'verde_correcto']; llegó 'rojo_feo'"),
            ("bloque sin prosa", con(borrar=(9,)), 9, 1,
             "línea 9, columna 1: se esperaba prosa para «sintoma»"),
            ("como_se_detecto inventado", con([(10, "    como_se_detecto: inventado")]), 10, 22,
             "línea 10, columna 22: se esperaba como_se_detecto en ['accidente', "
             "'herramienta_ajena', 'mutacion', 'observacion', 'persona']; llegó 'inventado'"),
            ("origen hasta EOF",
             'caso 999-roto:\n    fecha: "2026-08-25"\n    origen:\n'
             '        repo: "test"\n',
             5, 1, "línea 5, columna 1: se esperaba línea «titulo:»"),
            ("origen sin dos puntos", con([(4, "        repo")]), 4, 9,
             "línea 4, columna 9: se esperaba campo de origen «nombre: valor»; llegó "
             "'repo'"),
            ("origen sin espacio", con([(4, '        repo:"test"')]), 4, 14,
             "línea 4, columna 14: se esperaba espacio tras ':'; llegó 'repo:\"test\"'"),
            ("origen repetido", insertando((6, '        repo: "otro"')), 6, 9,
             "línea 6, columna 9: se esperaba campo de origen sin repetir, no «repo»; "
             "llegó 'repo: \"otro\"'"),
            ("origen valor no JSON", con([(4, "        repo: nope")]), 4, 15,
             "línea 4, columna 15: se esperaba texto entre comillas; llegó 'nope'"),
            ("origen vacío", con(borrar=(4, 5)), 4, 1,
             "línea 4, columna 1: se esperaba origen con al menos un campo"),
            ("clave sin punto y coma", con([(13, "        hecho: clave(id) id, ok")]),
             13, 24, "línea 13, columna 24: se esperaba ';' antes de campos; llegó "
             "'id, ok'"),
            ("clave sin coma", con([(13, "        hecho: clave(id ok); id, ok")]),
             13, 25, "línea 13, columna 25: se esperaba ',' entre campos de clave; llegó 'ok'"),
            ("campos sin coma", con([(13, "        hecho: id ok")]), 13, 19,
             "línea 13, columna 19: se esperaba ',' entre campos; llegó 'ok'"),
            ("campos sin coma tras clave", con([(13, "        hecho: clave(id, ok); id ok")]), 13, 34,
             "línea 13, columna 34: se esperaba ',' entre campos; llegó 'ok'"),
            ("relación sobreindentada", con([(13, "            hecho: id, ok")]), 13, 9,
             "línea 13, columna 9: se esperaba relación; llegó 'hecho: id, ok'"),
            ("relación sin dos puntos", con([(13, "        hecho")]), 13, 9,
             "línea 13, columna 9: se esperaba relación «nombre: campos»; llegó 'hecho'"),
            ("relación repetida",
             insertando((15, "        hecho: id, ok"), (16, '            "b", false')),
             15, 9, "línea 15, columna 9: se esperaba relación sin repetir, no «hecho»; "
             "llegó 'hecho: id, ok'"),
            ("campos repetidos", con([(13, "        hecho: id, id")]), 13, 15,
             "línea 13, columna 15: se esperaba campos sin repetir; llegó 'id, id'"),
            ("escape con campos",
             con([(14, '            fila {"id": "a", "ok": true}')]), 14, 13,
             "línea 14, columna 13: se esperaba fila de tabla, no escape JSON, porque "
             "hay campos; llegó 'fila {\"id\": \"a\", \"ok\": true}'"),
            ("fila escape JSON roto", fila_json_rota, 14, 18,
             "línea 14, columna 18: se esperaba texto entre comillas; llegó 'nope'"),
            ("fila de tabla sin encabezado", fila_sin_encabezado, 14, 13,
             "línea 14, columna 13: se esperaba «fila { ... }» o relación nueva; llegó "
             "'\"a\"'"),
            ("fila sin coma", con([(14, '            "a" true')]), 14, 17,
             "línea 14, columna 17: se esperaba ',' entre valores de fila; llegó 'true'"),
            ("fila sólo tab", con([(14, "            \t")]), 14, 13,
             "línea 14, columna 13: se esperaba valores de fila; llegó '\\t'"),
            ("cantidad de valores", con([(14, '            "a"')]), 14, 13,
             "línea 14, columna 13: la relación «hecho» declara 2 campos (id, ok) y "
             "esta fila trae 1; llegó '\"a\"'"),
            ("más valores que campos", con([(14, '            "a", true, 9')]), 14, 13,
             "línea 14, columna 13: la relación «hecho» declara 2 campos (id, ok) y "
             "esta fila trae 3; llegó '\"a\", true, 9'"),
            ("relación de un campo con fila de dos valores",
             con([(13, "        hecho: id"), (14, '            "a", true')]), 14, 13,
             "línea 14, columna 13: la relación «hecho» declara 1 campo (id) y "
             "esta fila trae 2; llegó '\"a\", true'"),
            ("relación con campos sin filas", con(borrar=(14,)), 13, 15,
             "línea 13, columna 15: se esperaba filas para una relación con encabezado "
             "de campos; llegó 'hecho: id, ok'"),
            ("evidencia vacía", con(borrar=(13, 14)), 13, 1,
             "línea 13, columna 1: se esperaba al menos una relación de evidencia"),
            ("falta lección hasta EOF", con(borrar=(15, 16)), 15, 1,
             "línea 15, columna 1: se esperaba línea «leccion:»"),
            ("encabezado roto", "caso:\n", 1, 1,
             "línea 1, columna 1: se esperaba encabezado «caso <id>:»; llegó 'caso:'"),
            ("id inválido", con([(1, "caso 999_Caso:")]), 1, 6,
             "línea 1, columna 6: se esperaba id «NNN-descripcion», sólo con minúsculas "
             "ASCII, dígitos y `-`; llegó '999_Caso'"),
            ("extra final", base + "    sobra: x\n", 17, 5,
             "línea 17, columna 5: se esperaba fin de caso; llegó 'sobra: x'"),
        ]
        for nombre, texto, linea, columna, mensaje in casos:
            with self.subTest(nombre=nombre):
                self.assertErrorDeCaso(texto, linea, columna, mensaje)

    def test_los_bordes_validos_de_casos_tambien_quedan_fijados(self) -> None:
        con_comentario = "# comentario\n" + self._superficie_base()
        self.assertEqual(sintaxis_caso.leer(con_comentario)["id"], "999-caso-de-prueba")

        sin_espacio_tras_coma = self._superficie_base().replace('"a", true', '"a",true')
        self.assertEqual(
            sintaxis_caso.leer(sin_espacio_tras_coma)["evidencia"]["hecho"],
            [{"id": "a", "ok": True}],
        )

        sin_espacio_tras_punto_y_coma = self._superficie_base().replace(
            "        hecho: id, ok\n"
            '            "a", true\n',
            "        hecho: clave(id);ok\n"
            "            true\n",
        )
        self.assertEqual(
            sintaxis_caso.leer(sin_espacio_tras_punto_y_coma)["evidencia"]["hecho"],
            [["clave", ["id"]], {"ok": True}],
        )

    def test_el_impresor_de_casos_falla_cerrado_en_ids_y_claves_invalidas(self) -> None:
        for cid in (123, "999_Caso"):
            with self.subTest(cid=cid):
                datos = self._caso_base()
                datos["id"] = cid
                with self.assertRaises(ValueError):
                    sintaxis_caso.imprimir(datos)

        datos = self._caso_base({"pieza": [["clave", "id"], {"id": "a"}]})
        with self.assertRaises(ValueError):
            sintaxis_caso.imprimir(datos)

    def test_el_impresor_no_ascii_y_campos_no_tabulares_van_por_escape(self) -> None:
        texto = sintaxis_caso.imprimir(
            self._caso_base({"rel": [{"a,b": "ñ", "ok": True}]}))

        self.assertIn('\n        rel:\n', texto)
        self.assertIn('            fila {"a,b": "ñ", "ok": true}\n', texto)
        self.assertEqual(sintaxis_caso.leer(texto)["evidencia"]["rel"],
                         [{"a,b": "ñ", "ok": True}])

    def test_rutas_de_corpus_distingue_ausencia_y_raiz_no_fisica(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            self.assertEqual(sintaxis_caso.rutas_de_corpus(raiz / "ausente"), [])
            archivo = raiz / "corpus"
            archivo.write_text("", encoding="utf-8")
            with self.assertRaises(CasoMalDeclarado):
                sintaxis_caso.rutas_de_corpus(archivo)

    def test_todo_el_corpus_vuelve_exacto_en_la_superficie_de_casos(self) -> None:
        rutas = sintaxis_caso.rutas_de_corpus(RAIZ / "corpus")
        self.assertGreater(len(rutas), 0)
        for ruta in rutas:
            with self.subTest(caso=ruta.relative_to(RAIZ)):
                datos = sintaxis_caso.cargar_fuente_caso(ruta)
                superficie = sintaxis_caso.imprimir(datos)
                releido = sintaxis_caso.leer(superficie)
                self.assertEqual(releido, datos)
                self.assertEqual(sintaxis_caso.imprimir(releido), superficie)

    def test_procedencia_de_caso_es_opcional_y_vuelve_exacta(self) -> None:
        datos = self._caso_base()
        texto_sin = sintaxis_caso.imprimir(datos)
        self.assertNotIn("procedencia:", texto_sin)
        self.assertNotIn("procedencia", sintaxis_caso.leer(texto_sin))

        datos["procedencia"] = "observada"
        texto_con = sintaxis_caso.imprimir(datos)

        self.assertIn(
            '        commit: "local"\n    procedencia: observada\n    titulo: "Caso de prueba"',
            texto_con,
        )
        self.assertEqual(sintaxis_caso.leer(texto_con), datos)

    def test_procedencia_de_caso_es_conjunto_cerrado(self) -> None:
        lineas = self._superficie_base().splitlines()
        lineas.insert(5, "    procedencia: inventada")
        texto = self._texto(lineas)

        self.assertErrorDeCaso(
            texto, 6, 18,
            "línea 6, columna 18: se esperaba procedencia en ['construida', "
            "'generada', 'observada']; llegó 'inventada'",
        )

    def test_el_corpus_real_ejercita_los_dos_lectores(self) -> None:
        rutas = sintaxis_caso.rutas_de_corpus(RAIZ / "corpus")
        self.assertEqual({r.suffix for r in rutas}, {".caso", ".json"})
        self.assertEqual(sum(1 for r in rutas if r.suffix == ".json"), 2)
        self.assertEqual(sum(1 for r in rutas if r.suffix == ".caso"), len(rutas) - 2)

    def test_la_metamorfica_de_casos_juzga_todo_el_corpus(self) -> None:
        from nucleo.medida import Medida
        from nucleo.proyecto import Proyecto, macros_del_proyecto
        from tools import metamorficas

        filas = metamorficas._sintaxis_casos_ida_y_vuelta(Proyecto(RAIZ))
        self.assertEqual(len(filas), len(sintaxis_caso.rutas_de_corpus(RAIZ / "corpus")))
        self.assertTrue(all(f["mismo_veredicto"] and f["mismo_valor"] for f in filas))
        jueza = cargar_fuente_medida(
            ruta_de_medida("meta.sintaxis_casos_ida_y_vuelta", RAIZ / "catalogos",
                           *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        m = Medida.de_datos(jueza, macros=macros_del_proyecto(Proyecto(RAIZ)))
        self.assertTrue(m.evaluar({"equivalencia": filas}).ok)

    def test_la_metamorfica_de_casos_cubre_la_forma_del_caso(self) -> None:
        from nucleo.medida import Medida
        from nucleo.proyecto import Proyecto, macros_del_proyecto
        from tools import metamorficas

        candidatos = metamorficas._generar_casos_candidatos()
        self.assertGreaterEqual(len(candidatos), 5)
        self.assertTrue(any("vacia" in c["evidencia"] and c["evidencia"]["vacia"] == []
                            for c in candidatos))
        self.assertTrue(any(len(c["evidencia"]) == 3 for c in candidatos))
        self.assertTrue(any(c["medida"] is None and c["estado_sin_medida"] == "abierto"
                            for c in candidatos))
        self.assertTrue(any(any(isinstance(f, list) and f[0] == "clave"
                                for filas in c["evidencia"].values() for f in filas)
                            for c in candidatos))
        filas = metamorficas._sintaxis_casos_cubre_casos()
        self.assertEqual(len(filas), len(candidatos))
        self.assertTrue(all(f["mismo_veredicto"] and f["mismo_valor"] for f in filas))
        jueza = cargar_fuente_medida(
            ruta_de_medida("meta.sintaxis_casos_cubre_casos", RAIZ / "catalogos",
                           *sorted((RAIZ / "perfiles").glob("*/catalogos"))))
        m = Medida.de_datos(jueza, macros=macros_del_proyecto(Proyecto(RAIZ)))
        self.assertTrue(m.evaluar({"equivalencia": filas}).ok)

    def test_una_relacion_heterogenea_usa_la_salida_de_escape(self) -> None:
        datos = self._caso_base({"rel": [{"a": 1}, {"b": "dos", "c": False}]})
        superficie = sintaxis_caso.imprimir(datos)

        self.assertIn("\n        rel:\n", superficie)
        self.assertIn('            fila {"a": 1}\n', superficie)
        self.assertIn('            fila {"b": "dos", "c": false}\n', superficie)
        self.assertEqual(sintaxis_caso.leer(superficie), datos)

    def test_una_relacion_presente_y_vacia_no_es_una_relacion_ausente(self) -> None:
        datos = self._caso_base({"presente": []})
        releido = sintaxis_caso.leer(sintaxis_caso.imprimir(datos))

        self.assertIn("presente", releido["evidencia"])
        self.assertEqual(releido["evidencia"]["presente"], [])
        self.assertNotIn("ausente", releido["evidencia"])

    def test_una_relacion_vacia_puede_conservar_clave_declarada(self) -> None:
        datos = self._caso_base({"pieza": [["clave", ["id"]]]})
        releido = sintaxis_caso.leer(sintaxis_caso.imprimir(datos))

        self.assertEqual(releido["evidencia"]["pieza"], [["clave", ["id"]]])

    def test_el_mismo_id_en_json_y_caso_es_error(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "corpus").mkdir()
            datos = self._caso_base()
            (raiz / "corpus" / "uno.json").write_text(
                json.dumps(datos, ensure_ascii=False), encoding="utf-8")
            (raiz / "corpus" / "dos.caso").write_text(
                sintaxis_caso.imprimir(datos), encoding="utf-8")

            with self.assertRaises(CasoMalDeclarado) as cm:
                sintaxis_caso.cargar_casos(raiz / "corpus")

        mensaje = str(cm.exception)
        self.assertIn("999-caso-de-prueba", mensaje)
        self.assertIn("uno.json", mensaje)
        self.assertIn("dos.caso", mensaje)

    def test_un_caso_mal_formado_denuncia_archivo_linea_columna_y_fragmento(self) -> None:
        import tempfile
        texto = "\n".join([
            "caso 999-roto:",
            '    fecha: "2026-08-25"',
            "    origen:",
            '        repo: "test"',
            '        commit: "local"',
            '    titulo: "Roto"',
            "    etiqueta: verde_correcto",
            "    sintoma:",
            "        falla",
            "    como_se_detecto: observacion",
            "    medida: demo.mide",
            "    evidencia:",
            "        hecho: id, ok",
            '            "a" true',
            "    leccion:",
            "        falla",
        ]) + "\n"
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "roto.caso"
            ruta.write_text(texto, encoding="utf-8")
            with self.assertRaises(CasoMalDeclarado) as cm:
                sintaxis_caso.cargar_fuente_caso(ruta)

        mensaje = str(cm.exception)
        self.assertIn("roto.caso", mensaje)
        self.assertIn("línea 14, columna", mensaje)
        self.assertIn("  14 |", mensaje)
        self.assertIn("^", mensaje)

    def test_las_herramientas_no_vuelven_a_rglob_json_sobre_corpus(self) -> None:
        revisadas = (
            RAIZ / "tools" / "aceptacion.py",
            RAIZ / "tools" / "cifras.py",
            RAIZ / "tools" / "corpus.py",
            RAIZ / "tools" / "estudio.py",
            RAIZ / "tools" / "medida.py",
            RAIZ / "tools" / "metamorficas.py",
            RAIZ / "tools" / "mutar.py",
            RAIZ / "tools" / "trazar.py",
        )
        for ruta in revisadas:
            with self.subTest(ruta=ruta.name):
                codigo = ruta.read_text(encoding="utf-8")
                self.assertNotIn('rglob("*.json")', codigo)
                self.assertNotIn('glob("*/*.json")', codigo)


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


class GramaticaDelIdDeCasoTests(unittest.TestCase):
    def _texto(self, cid: str) -> str:
        datos = {
            "id": "999-caso-valido",
            "fecha": "2026-08-25",
            "origen": {"repo": "test", "commit": "local"},
            "titulo": "Caso valido",
            "etiqueta": "verde_correcto",
            "sintoma": "Prueba",
            "como_se_detecto": "observacion",
            "medida": "demo.mide",
            "evidencia": {"hecho": [{"id": "a"}]},
            "leccion": "Prueba",
        }
        datos["id"] = cid
        return sintaxis_caso.imprimir(datos)

    def test_la_superficie_acepta_un_id_de_caso_de_la_gramatica(self) -> None:
        self.assertEqual(sintaxis_caso.leer(self._texto("999-caso-valido"))["id"],
                         "999-caso-valido")

    def test_la_superficie_rechaza_un_id_de_caso_fuera_de_la_gramatica(self) -> None:
        cuerpo = self._texto("999-caso-valido").replace("999-caso-valido", "999-caso-con-dueno")
        for malo in ("999-caso-con-dueño", "999_Caso", "999-", "abc-caso", "999--doble"):
            with self.subTest(malo=malo):
                texto = cuerpo.replace("999-caso-con-dueno", malo)
                with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
                    sintaxis_caso.leer(texto)
                self.assertIn("minúsculas ASCII", str(cm.exception))

    def test_la_gramatica_no_describe_a_UN_catalogo_sino_al_lenguaje(self) -> None:
        """Casi entra una gramática derivada de un solo corpus, y rechazaba a un consumidor.

        La primera versión exigía `^[0-9]{3}-…` —tres dígitos y a otra cosa— porque así se llaman
        los casos de ESTE repositorio. Un consumidor real numera por dominio
        (`scatter-004-coberturas-distintas`, `physics-tanda-001-…`) y 9 de sus casos dejaban de
        cargar. Derivar la gramática de un catálogo propio es la misma trampa que medir la
        superficie contra las medidas que uno mismo escribió: describe al autor, no al lenguaje.
        """
        for ajeno in ("scatter-004-coberturas-distintas",
                      "physics-tanda-001-interpenetracion-en-el-borde",
                      "geometria-010-comparte-cara-de-sobra-es-verde",
                      "99-serie-corta"):
            with self.subTest(ajeno=ajeno):
                self.assertEqual(sintaxis_caso.leer(self._texto(ajeno))["id"], ajeno)

    def test_el_json_no_puede_contrabandear_un_id_de_caso_invalido(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "999-caso-con-dueno.json"
            ruta.write_text(json.dumps({"id": "999-caso-con-dueño"}, ensure_ascii=False),
                            encoding="utf-8")
            with self.assertRaises(CasoMalDeclarado) as cm:
                sintaxis_caso.cargar_fuente_caso(ruta)
        self.assertIn("minúsculas ASCII", str(cm.exception))

    def test_la_gramatica_vive_junto_a_la_de_medida(self) -> None:
        from nucleo.proyecto import ID_CASO_RE, ID_MEDIDA_RE
        self.assertIsNotNone(ID_MEDIDA_RE.fullmatch("dominio.nombre"))
        self.assertIsNotNone(ID_CASO_RE.fullmatch("999-caso-valido"))
        self.assertIsNone(ID_CASO_RE.fullmatch("999-caso-con-dueño"))


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


class CasoNuevoNaceEnLaSuperficieTests(unittest.TestCase):
    def test_la_plantilla_de_caso_no_trae_una_etiqueta_puesta(self) -> None:
        """La plantilla de MEDIDA parsea entera; ésta no puede, y es a propósito.

        `etiqueta`, `procedencia` y `como_se_detecto` son conjuntos cerrados. Los dos marcadores
        quedan fuera del conjunto por definición, y `procedencia` queda como comentario para no
        inventar un valor. Se podría poner un valor plausible —`falso_verde`, `observada`,
        `mutacion`— y la plantilla parsearía, pero esos campos no son decorativos: la etiqueta decide
        la polaridad del caso, `procedencia` decide si la evidencia fija mundo o ejemplo fabricado, y
        `como_se_detecto` alimenta una cifra que el README publica. **Un default creíble se queda sin
        pensar**, que es peor que un error.

        El marcador sólo es aceptable porque el error enseña qué poner y el andamio lo lista al
        crear el archivo. Eso es lo que fijan los dos tests de abajo.
        """
        from tools.corpus import PLANTILLA

        texto = PLANTILLA.format(cid="999-caso-nuevo")
        self.assertIn("ETIQUETA", texto)
        self.assertIn("# procedencia:", texto)
        self.assertNotIn("    procedencia: observada", texto)
        self.assertIn("COMO_SE_DETECTO", texto)
        with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
            sintaxis_caso.leer(texto)
        self.assertIn("etiqueta en [", str(cm.exception))

    def test_el_error_del_marcador_enumera_los_valores_validos(self) -> None:
        from nucleo.caso import DETECCIONES, ETIQUETAS, PROCEDENCIAS
        from tools.corpus import PLANTILLA

        texto = PLANTILLA.format(cid="999-caso-nuevo")
        with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
            sintaxis_caso.leer(texto)
        for valor in ETIQUETAS:
            self.assertIn(valor, str(cm.exception))
        for valor in PROCEDENCIAS:
            self.assertIn(valor, texto)
        con_etiqueta = texto.replace("etiqueta: ETIQUETA", "etiqueta: falso_verde")
        with self.assertRaises(sintaxis.ErrorSintaxis) as cm2:
            sintaxis_caso.leer(con_etiqueta)
        for valor in DETECCIONES:
            self.assertIn(valor, str(cm2.exception))

    def test_el_andamio_lista_los_conjuntos_cerrados_al_crear_el_caso(self) -> None:
        """El momento de decidirlos es al crear el archivo, no dos comandos después."""
        import io
        import tempfile
        from contextlib import redirect_stdout
        from nucleo.caso import DETECCIONES, ETIQUETAS, PROCEDENCIAS
        from nucleo.proyecto import Proyecto
        from tools import corpus

        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            for sub in ("catalogos", "corpus", "diferencial"):
                (raiz / sub).mkdir()
            (raiz / "oracle.json").write_text(
                '{"esquema":"oracle.proyecto/v1","perfiles":[]}', encoding="utf-8")
            salida = io.StringIO()
            with redirect_stdout(salida):
                corpus.nuevo(Proyecto(raiz), "tareas/001-prueba")
            texto = salida.getvalue()
            for valor in (*ETIQUETAS, *DETECCIONES, *PROCEDENCIAS):
                self.assertIn(valor, texto)

    def test_el_andamio_crea_un_caso_en_superficie(self) -> None:
        import io
        import tempfile
        from contextlib import redirect_stdout
        from nucleo.proyecto import Proyecto
        from tools import corpus

        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "catalogos").mkdir()
            (raiz / "corpus").mkdir()
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = corpus.main(["--proyecto", str(raiz), "--nuevo", "meta/999-caso-nuevo"])
            destino = raiz / "corpus" / "meta" / "999-caso-nuevo.caso"

            self.assertEqual(codigo, 0, salida.getvalue())
            self.assertTrue(destino.exists())
            self.assertEqual(corpus.ruta_de_caso_nuevo(Proyecto(raiz), "meta/999-caso-nuevo"),
                             destino)
            # NO se comprueba que cargue: la plantilla trae los dos marcadores de conjunto cerrado
            # sin llenar, a propósito (ver `test_la_plantilla_de_caso_no_trae_una_etiqueta_puesta`).
            escrito = destino.read_text(encoding="utf-8")
            self.assertTrue(escrito.startswith("caso 999-caso-nuevo:"))
            self.assertIn("evidencia:", escrito)


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


class DefmacroSurfaceTests(unittest.TestCase):
    """La superficie cubre la otra mitad del lenguaje: las macros, no sólo las medidas."""

    def test_las_macros_del_nucleo_vuelven_exactas(self) -> None:
        informe = sintaxis.verificar_catalogo(RAIZ)
        del_macros = len([p for p in (RAIZ / "nucleo" / "macros").iterdir()
                          if p.suffix in EXTENSIONES_DE_MACRO and p.is_file()])
        self.assertEqual(informe["macros"], del_macros)
        self.assertTrue(informe["json_igual"])
        self.assertTrue(informe["texto_igual"])

    def test_cada_macro_del_nucleo_se_lee_igual_al_archivo(self) -> None:
        for ruta in sorted(p for p in (RAIZ / "nucleo" / "macros").iterdir()
                           if p.suffix in EXTENSIONES_DE_MACRO and p.is_file()):
            with self.subTest(macro=ruta.stem):
                texto = ruta.read_text(encoding="utf-8")
                datos = (sintaxis.leer(texto) if ruta.suffix == ".oracle"
                         else json.loads(texto))
                superficie = sintaxis.imprimir(datos)
                self.assertTrue(superficie.startswith(f"defmacro {ruta.stem}("))
                self.assertEqual(sintaxis.leer(superficie), datos)
                self.assertEqual(sintaxis.imprimir(sintaxis.leer(superficie)), superficie)

    def test_una_macro_con_huecos_se_imprime_como_defmacro(self) -> None:
        datos = ["defmacro", "todos-cumplen",
                 ["id", "relacion", "alias", "predicado", "porque", "alcance"],
                 [],
                 ["medida", ["$", "id"],
                  ["desde", ["de", ["$", "relacion"], ["$", "alias"]],
                   ["donde", ["no", ["$", "predicado"]]]],
                  ["resumen", "contar", 1],
                  ["umbral", "<=", 0, ["$", "porque"]],
                  ["alcance", ["$", "alcance"]]]]
        superficie = sintaxis.imprimir(datos)

        self.assertTrue(superficie.startswith(
            "defmacro todos-cumplen(id, relacion, alias, predicado, porque, alcance):"))
        self.assertIn("\n    medida $id:\n", superficie)
        self.assertIn("\n        de $relacion $alias\n", superficie)
        self.assertIn("\n        donde no $predicado\n", superficie)
        self.assertIn("\n        umbral <= 0 porque $porque\n", superficie)
        self.assertIn("\n        alcance $alcance\n", superficie)
        self.assertEqual(sintaxis.leer(superficie), datos)

    def test_una_macro_con_guarda_vuelve_exacta(self) -> None:
        datos = ["defmacro", "propia",
                 ["id", "otro"],
                 [["guarda", ["!=", ["$", "id"], ["$", "otro"]], "distintos"]],
                 ["medida", ["$", "id"],
                  ["desde", ["de", "rel", ["$", "otro"]]],
                  ["resumen", "contar", 1],
                  ["umbral", "<=", 0, ["$", "id"]],
                  ["alcance", ["$", "otro"]]]]
        superficie = sintaxis.imprimir(datos)

        self.assertIn("\n    guarda $id != $otro \"distintos\"\n", superficie)
        self.assertEqual(sintaxis.leer(superficie), datos)

    def test_la_aridad_de_defmacro_es_cinco(self) -> None:
        for datos in (["defmacro", "p", ["id"], []],
                      ["defmacro", "p", ["id"], [], ["medida"], "de+"],
                      ["no-defmacro", "p", ["id"], [], ["medida"]]):
            with self.subTest(datos=datos):
                with self.assertRaises(ValueError):
                    sintaxis.imprimir(datos)

    def test_una_guarda_mal_formada_trae_linea_y_columna(self) -> None:
        texto = "\n".join([
            "defmacro mala(id):",
            "    guarda $id != 1",
            "    medida $id:",
            "        de rel r",
            "        donde r.x == true",
            "        resumen contar(1)",
            "        umbral <= 0 porque \"razón\"",
            "        alcance \"NO ve\"",
        ])

        with self.assertRaises(sintaxis.ErrorSintaxis) as e:
            sintaxis.leer(texto)
        self.assertEqual(e.exception.linea, 2)
        self.assertIn("mensaje de la guarda", str(e.exception))

    def test_un_parametro_que_la_plantilla_nunca_usa_no_carga(self) -> None:
        texto = "\n".join([
            "defmacro propia(id, sobra):",
            "    medida $id:",
            "        de rel r",
            "        donde r.x == true",
            "        resumen contar(1)",
            "        umbral <= 0 porque \"razón\"",
            "        alcance \"NO ve\"",
        ])

        with self.assertRaises(sintaxis.ErrorSintaxis) as e:
            sintaxis.leer(texto)
        self.assertEqual(e.exception.linea, 1)
        self.assertIn("nunca lo usa", str(e.exception))

    def test_un_hueco_de_parametro_no_declarado_no_carga(self) -> None:
        texto = "\n".join([
            "defmacro propia(id):",
            "    medida $id:",
            "        de rel r",
            "        donde r.x == $inventado",
            "        resumen contar(1)",
            "        umbral <= 0 porque \"razón\"",
            "        alcance \"NO ve\"",
        ])

        with self.assertRaises(sintaxis.ErrorSintaxis) as e:
            sintaxis.leer(texto)
        self.assertEqual(e.exception.linea, 4)
        self.assertIn("no es un parámetro", str(e.exception))

    def test_un_hueco_dentro_de_una_cadena_no_cuenta_como_hueco(self) -> None:
        """Un `$x` adentro del mensaje de una guarda es texto, no un hueco: no se lo exige como
        parámetro ni se lo cuenta como usado."""
        texto = "\n".join([
            "defmacro propia(id):",
            "    guarda $id != 1 \"usá $otro si querés\"",
            "    medida $id:",
            "        de rel r",
            "        donde r.x == true",
            "        resumen contar(1)",
            "        umbral <= 0 porque \"razón\"",
            "        alcance \"NO ve\"",
        ])
        datos = sintaxis.leer(texto)
        self.assertEqual(datos[2], ["id"])
        self.assertEqual(datos[3][0][2], "usá $otro si querés")


class MacrosEnLaSuperficieTests(unittest.TestCase):
    """La biblioteca estándar del lenguaje también se guarda en la superficie."""

    def test_la_biblioteca_estandar_esta_escrita_en_la_superficie(self) -> None:
        from nucleo.macro import macros_base
        base = pathlib.Path(RAIZ / "nucleo" / "macros")
        self.assertTrue(any(p.suffix == ".oracle" for p in base.iterdir()))
        self.assertEqual(sorted(macros_base()), [
            "ninguno", "ninguno-par", "ninguno-unir", "peor"])

    def test_el_mismo_nombre_en_los_dos_formatos_es_un_error(self) -> None:
        """No gana ninguno: un ganador silencioso es una divergencia esperando."""
        import tempfile
        from nucleo.macro import MacroMalDeclarada, cargar_macros
        cuerpo = (RAIZ / "nucleo" / "macros" / "ninguno.oracle").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as d:
            raiz = pathlib.Path(d)
            (raiz / "ninguno.oracle").write_text(cuerpo, encoding="utf-8")
            (raiz / "ninguno.json").write_text(
                json.dumps(sintaxis.leer(cuerpo), ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(MacroMalDeclarada):
                cargar_macros(raiz)

    def test_el_numerador_no_pierde_las_macros_al_cambiarles_el_formato(self) -> None:
        """Bajar la proporción renombrando archivos es sastreo con otra ropa.

        Cuando las tres macros base pasaron a `.oracle`, el `glob("*.json")` a mano de `cifras.py`
        las dejó caer del numerador sin una queja. El inventario de formatos es UNO.
        """
        from nucleo.macro import EXTENSIONES_DE_MACRO
        from tools import cifras
        contadas = [p for p in cifras._lenguaje() if p.parent.name == "macros"]
        en_disco = [p for p in (RAIZ / "nucleo" / "macros").iterdir()
                    if p.suffix in EXTENSIONES_DE_MACRO and p.is_file()]
        self.assertEqual(len(contadas), len(en_disco))
        self.assertGreater(len(contadas), 0)


class ElCatalogoRealEjercitaLosDosLectoresTests(unittest.TestCase):
    """Un lector que sólo ejercitan los tests es un lector a medio probar.

    El catálogo universal está escrito en la superficie —es la forma en que se autoriza a escribir
    y tiene que ser la forma en que está escrito lo que se publica— pero DOS medidas se dejan a
    propósito en `.json`. Si todas migraran, el camino `.json` de `cargar_catalogo` dejaría de
    correrse en el catálogo real y sólo lo tocarían los temporales de esta suite; el día que se
    rompiera, se enteraría un consumidor —Jam y LyraGASP guardan sus medidas en `.json`— y no acá.
    """

    def _rutas(self):
        from nucleo.medida import rutas_de_catalogo
        return rutas_de_catalogo(RAIZ / "catalogos",
                                 *sorted((RAIZ / "perfiles").glob("*/catalogos")))

    def test_el_catalogo_publica_medidas_en_los_dos_formatos(self) -> None:
        sufijos = {r.suffix for r in self._rutas()}
        self.assertEqual(sufijos, {".oracle", ".json"})

    def test_la_superficie_es_la_forma_dominante_y_no_una_excepcion(self) -> None:
        """Si quedara una sola en superficie, la afirmación «el catálogo está escrito en el
        lenguaje» sería falsa y nada la contradiría."""
        rutas = self._rutas()
        en_superficie = [r for r in rutas if r.suffix == ".oracle"]
        self.assertGreater(len(en_superficie), len(rutas) // 2)

    def test_las_dos_que_quedan_en_json_cargan_por_el_mismo_camino(self) -> None:
        from nucleo.medida import cargar_fuente_medida
        for ruta in (r for r in self._rutas() if r.suffix == ".json"):
            with self.subTest(medida=ruta.stem):
                self.assertEqual(cargar_fuente_medida(ruta)[1], ruta.stem)


class VersionDeLaSuperficieTests(unittest.TestCase):
    """La superficie declara contra qué sintaxis se escribió, y cargarla es fail-closed.

    Es el hueco que el álgebra ya cerró, abierto un nivel más arriba: un `.oracle` es un formato
    GUARDADO, y hasta hoy nada le decía a nadie si un archivo escrito ayer sigue significando lo
    mismo. La regla de qué sube cada parte del número está en `ESPECIFICACION.md` §0.
    """

    CUERPO = (
        'ninguno d.prueba:\n'
        '    de pieza p\n'
        '    donde p.x == true\n'
        '    umbral <= 0 porque "razón"\n'
        '    alcance "NO ve otros campos"\n'
    )

    def test_sin_declarar_no_hay_version(self) -> None:
        self.assertIsNone(sintaxis.leer_con_mapa(self.CUERPO).version)

    def test_el_lector_devuelve_la_version_declarada(self) -> None:
        lectura = sintaxis.leer_con_mapa("sintaxis 0.1\n" + self.CUERPO)
        self.assertEqual(lectura.version, "0.1")
        self.assertEqual(lectura.datos, sintaxis.leer(self.CUERPO))

    def test_la_version_es_superficie_no_un_comentario_pegado_arriba(self) -> None:
        comentado = sintaxis.leer_con_mapa("# sintaxis 0.1\n" + self.CUERPO)
        self.assertIsNone(comentado.version)
        declarado = sintaxis.leer_con_mapa("sintaxis 0.1\n" + self.CUERPO)
        self.assertEqual(declarado.version, "0.1")

    def test_una_version_mal_formada_falla_cerrado(self) -> None:
        for mala in ("basura", "0", "0.3.1", "a.b", "01.2", "-1.0"):
            with self.subTest(mala=mala):
                with self.assertRaises(sintaxis.ErrorSintaxis) as e:
                    sintaxis.leer(f"sintaxis {mala}\n" + self.CUERPO)
                self.assertIn("MAYOR.MENOR", str(e.exception))

    def _cargar(self, declarada):
        import tempfile
        from nucleo.medida import cargar
        prefijo = f"sintaxis {declarada}\n" if declarada is not None else ""
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "d.prueba.oracle"
            ruta.write_text(prefijo + self.CUERPO, encoding="utf-8")
            return cargar(ruta)

    def test_sin_declarar_la_misma_y_una_menor_vieja_cargan(self) -> None:
        self.assertEqual(self._cargar(None).id, "d.prueba")
        self.assertEqual(self._cargar("0.1").id, "d.prueba")
        self.assertEqual(self._cargar("0.0").id, "d.prueba")

    def test_una_menor_futura_y_una_mayor_no_cargan_diciendo_las_dos(self) -> None:
        import tempfile
        from nucleo.medida import MedidaMalDeclarada, cargar
        for declarada in ("0.2", "1.0"):
            with self.subTest(declarada=declarada), tempfile.TemporaryDirectory() as d:
                ruta = Path(d) / "d.prueba.oracle"
                ruta.write_text(f"sintaxis {declarada}\n" + self.CUERPO, encoding="utf-8")
                with self.assertRaises(MedidaMalDeclarada) as ctx:
                    cargar(ruta)
                self.assertIn(declarada, str(ctx.exception))
                self.assertIn("0.1", str(ctx.exception))

    def test_ningun_archivo_existente_tuvo_que_declarar_version(self) -> None:
        """Poner versión a la superficie no puede obligar a tocar un archivo ya escrito.

        Contado, no escrito: la versión anterior de este test fijaba «34» a mano y se cayó con la
        primera medida nueva —por el conteo, no por lo que dice medir—. Es el mismo error que tenía
        `--verificar` con su `== 29`, y en este repositorio ya tiene nombre.
        """
        from nucleo.macro import cargar_macros

        en_superficie = [r for r in sintaxis._rutas_catalogo(RAIZ) if r.suffix == ".oracle"]
        self.assertTrue(en_superficie)
        sin_declarar = 0
        for ruta in en_superficie + sintaxis._rutas_macros(RAIZ):
            texto = ruta.read_text(encoding="utf-8")
            if not texto.startswith("sintaxis "):
                sin_declarar += 1
                cargar_fuente_medida(ruta) if ruta in en_superficie else None
        self.assertEqual(sin_declarar, len(en_superficie) + len(sintaxis._rutas_macros(RAIZ)),
                         "algún archivo del árbol quedó obligado a declarar versión")
        self.assertEqual(len(cargar_macros(RAIZ / "nucleo" / "macros")),
                         len(sintaxis._rutas_macros(RAIZ)))

    def test_el_verificador_sigue_en_verde_sobre_todo_lo_que_hay(self) -> None:
        informe = sintaxis.verificar_catalogo(RAIZ)
        docs = sintaxis.verificar_documentos(RAIZ)
        self.assertEqual(informe["medidas"], len(sintaxis._rutas_catalogo(RAIZ)))
        self.assertEqual(informe["macros"], len(sintaxis._rutas_macros(RAIZ)))
        self.assertEqual(informe["casos"], len(sintaxis_caso.rutas_de_corpus(RAIZ / "corpus")))
        self.assertGreater(docs["ejecutables"], 0)
        self.assertTrue(informe["json_igual"])
        self.assertTrue(informe["texto_igual"])
        self.assertEqual(docs["fallas"], [])


class NingunaEntradaEsFailOpenTests(unittest.TestCase):
    """Todas las puertas juzgan la versión, no sólo las que cargan un catálogo.

    `leer()` es puro y no juzga —es la decisión correcta y está defendida en su docstring—, pero
    `tools/sintaxis.py --leer` también carga un archivo, y traducía en silencio, con exit 0, una
    superficie escrita contra una sintaxis que este núcleo no implementa. Una salida fail-open al
    lado de dos fail-closed es peor que no tener ninguna: enseña a confiar.
    """

    FUTURO = ('sintaxis 9.0\n'
              'ninguno tareas.mide:\n'
              '    de tarea t\n'
              '    donde t.vencida == true\n'
              '    umbral <= 0 porque "una tarea vencida sin dueño no la hace nadie"\n'
              '    alcance "ve el par vencida+sin-dueño y nada más"\n')

    def _archivo(self, d, nombre="m.oracle"):
        ruta = pathlib.Path(d) / nombre
        ruta.write_text(self.FUTURO, encoding="utf-8")
        return ruta

    def test_el_cli_leer_rechaza_una_sintaxis_que_este_nucleo_no_implementa(self) -> None:
        import io
        import tempfile
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = sintaxis.main(["--leer", str(self._archivo(d))])
            self.assertEqual(codigo, 1)
            self.assertIn("9.0", salida.getvalue())
            self.assertNotIn('"ninguno"', salida.getvalue())

    def test_las_tres_puertas_coinciden(self) -> None:
        """El catálogo, las macros y el CLI dan el mismo veredicto sobre el mismo archivo."""
        import io
        import tempfile
        from contextlib import redirect_stdout

        from nucleo.macro import MacroMalDeclarada, cargar_macros
        from nucleo.medida import MedidaMalDeclarada, cargar_fuente_medida
        with tempfile.TemporaryDirectory() as d:
            ruta = self._archivo(d)
            with self.assertRaises(MedidaMalDeclarada):
                cargar_fuente_medida(ruta)
            with self.assertRaises(MacroMalDeclarada):
                cargar_macros(pathlib.Path(d))
            with redirect_stdout(io.StringIO()):
                self.assertEqual(sintaxis.main(["--leer", str(ruta)]), 1)


class LosBloquesDeCasoDeLaDocumentacionTambienSeVerificanTests(unittest.TestCase):
    """Cuando entró la superficie de casos, sus ejemplos quedaron fuera del verificador.

    `verificar_documentos` miraba dos documentos y una sola superficie. Los ejemplos de `.caso`
    aparecieron en cuatro documentos y ninguno pasaba por el lector: volvían a ser una afirmación
    sostenida por la palabra de quien la escribió, que es lo que este mecanismo vino a terminar.
    """

    def test_se_verifican_las_dos_superficies(self) -> None:
        import re
        de_caso = 0
        for nombre in sintaxis.DOCUMENTOS_CON_SUPERFICIE:
            texto = (RAIZ / nombre).read_text(encoding="utf-8")
            de_caso += sum(1 for m in sintaxis.BLOQUE_RE.finditer(texto)
                           if m.group(1) == "caso" and not m.group(2))
        self.assertGreater(de_caso, 0, "ningún documento muestra un caso ejecutable")
        self.assertEqual(sintaxis.verificar_documentos(RAIZ)["fallas"], [])

    def test_un_bloque_de_caso_roto_se_denuncia(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            for nombre in sintaxis.DOCUMENTOS_CON_SUPERFICIE:
                (raiz / nombre).write_text("```caso\ncaso 999-roto:\n    fecha\n```\n",
                                           encoding="utf-8")
            fallas = sintaxis.verificar_documentos(raiz)["fallas"]
            self.assertEqual(len(fallas), len(sintaxis.DOCUMENTOS_CON_SUPERFICIE))
            self.assertIn("no lee", fallas[0])


class ElErrorDelLenguajeSeManipulaComoUnErrorTests(unittest.TestCase):
    """`ErrorSintaxis` es un `dataclass(frozen=True)`, y eso congelaba de más.

    Un dataclass congelado reemplaza `__setattr__` por uno que rechaza TODO, incluidos los dunder
    que el intérprete y las herramientas de traza escriben sobre cualquier excepción. CPython los
    escribe por la API de C al levantar —por eso un `raise` simple andaba— pero cualquier código
    Python que re-lance o encadene el error se estrellaba con `FrozenInstanceError`.

    Lo encontró la mutación de código, no una persona: **51 de 193 mutantes** de `nucleo/caso.py` no
    salieron ni muertos ni vivos, salieron `error_arnes` con
    `FrozenInstanceError: cannot assign to field '__traceback__'`. Un error del arnés no es una
    muerte —caso `017` del corpus—, así que esos 51 no medían nada y la ronda quedaba inconclusa.
    """

    def test_se_le_puede_escribir_la_maquinaria_de_excepciones(self) -> None:
        for atributo in ("__traceback__", "__cause__", "__context__"):
            with self.subTest(atributo=atributo):
                e = sintaxis.ErrorSintaxis(1, 1, "x")
                setattr(e, atributo, None)
                self.assertIsNone(getattr(e, atributo))

    def test_los_campos_del_error_siguen_congelados(self) -> None:
        """La inmutabilidad que se quiere es la de línea, columna y qué se esperaba."""
        import dataclasses
        e = sintaxis.ErrorSintaxis(1, 1, "x")
        for campo in ("linea", "columna", "esperado"):
            with self.subTest(campo=campo):
                with self.assertRaises(dataclasses.FrozenInstanceError):
                    setattr(e, campo, 99)

    def test_se_puede_encadenar_y_relanzar_desde_python(self) -> None:
        """El camino exacto que el arnés rompía: atrapar, encadenar y volver a levantar."""
        import traceback
        try:
            try:
                raise sintaxis.ErrorSintaxis(3, 7, "adentro")
            except sintaxis.ErrorSintaxis as interno:
                raise sintaxis.ErrorSintaxis(1, 1, "afuera") from interno
        except sintaxis.ErrorSintaxis as e:
            texto = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            self.assertIn("adentro", texto)
            self.assertIn("afuera", texto)


class UnErrorDentroDeUnUnirDiceDondeTests(unittest.TestCase):
    """El mapa de fuente tenía un agujero del tamaño de `unir`.

    `_unir` calculaba `ruta_izq` y `ruta_der` con esmero y se las pasaba a `aplicar`, donde el brazo
    del `de` las descartaba. Resultado: un error en cualquiera de los lados de un `unir` salía SIN
    ruta, y `fragmento_de_error` no podía señalar nada.

    Lo denunció la mutación de código, no una persona: cuatro mutantes sobre `ruta_izq`/`ruta_der`
    —incluido cambiar el índice `1` por el `2`— sobrevivían porque el valor calculado no llegaba a
    ninguna parte. Un mutante que no se puede matar porque su resultado no se usa no es equivalente:
    es código que quería hacer algo y no lo hacía.
    """

    @staticmethod
    def _texto(*relaciones):
        lineas = ["    de %s r0" % relaciones[0]]
        lineas += ["    unir %s r%d" % (rel, i) for i, rel in enumerate(relaciones[1:], 1)]
        return ("medida d.mide:\n" + "\n".join(lineas) + "\n"
                "    donde r0.k == 1\n"
                "    resumen contar(1)\n"
                '    umbral <= 0 porque "una defensa suficientemente larga para el validador"\n'
                '    alcance "no ve nada mas que esto"\n')

    def _falla(self, texto):
        import catalogos  # noqa: F401
        from nucleo.algebra import ErrorDeAlgebra
        from nucleo.medida import Medida
        with self.assertRaises(ErrorDeAlgebra) as cm:
            Medida.de_datos(sintaxis.leer(texto)).evaluar(
                {"pieza": [{"k": 1}], "objetivo": [{"k": 1}]})
        return cm.exception

    def test_cada_fuente_del_unir_tiene_su_propia_ruta(self) -> None:
        """Si las tres coincidieran, cambiar el índice 1 por el 2 sería indistinguible."""
        rutas = {}
        for posicion, relaciones in enumerate((
                ("ausente", "objetivo", "pieza"),
                ("pieza", "ausente", "objetivo"),
                ("pieza", "objetivo", "ausente"))):
            rutas[posicion] = self._falla(self._texto(*relaciones)).ruta
        self.assertEqual(len(set(rutas.values())), 3, "rutas repetidas: %s" % rutas)
        self.assertIsNotNone(rutas[0])

    def test_la_ruta_se_traduce_a_la_linea_y_la_columna_de_la_fuente(self) -> None:
        """De punta a punta: del error del álgebra al caret sobre la superficie."""
        for posicion, relaciones in enumerate((
                ("ausente", "objetivo"),
                ("pieza", "ausente"),
                ("ausente", "objetivo", "pieza"),
                ("pieza", "ausente", "objetivo"),
                ("pieza", "objetivo", "ausente"))):
            with self.subTest(posicion=posicion, relaciones=relaciones):
                texto = self._texto(*relaciones)
                fragmento = sintaxis.fragmento_de_error(self._falla(texto), texto)
                self.assertNotIn("no se encontró la ruta", fragmento)
                senalada = [l for l in fragmento.splitlines() if "|" in l][0]
                self.assertIn("ausente", senalada)
                caret = [l for l in fragmento.splitlines() if "^" in l][0]
                self.assertGreater(caret.index("^"), senalada.index("|") + 2)


class LosSeisTropiezosDeCasosFijanMensajeYPosicionTests(unittest.TestCase):
    """Los seis tropiezos de quien escribe su primer caso del corpus.

    El mensaje tiene que contener lo que hay que hacer, no sólo lo que se esperaba — y la posición
    tiene que seguir siendo exacta. Un mensaje amable que señala la línea equivocada es peor que uno
    seco que acierta.
    """

    def _caso_base(self) -> str:
        return (
            "caso 001-prueba:\n"
            '    fecha: "2026-08-26"\n'
            "    origen:\n"
            '        repo: "test"\n'
            '        commit: "local"\n'
            '    titulo: "T"\n'
            "    etiqueta: verde_correcto\n"
            "    sintoma:\n"
            "        S\n"
            "    como_se_detecto: observacion\n"
            "    medida: demo.mide\n"
            "    evidencia:\n"
            "        tarea: id, vencida\n"
            '            "t-1", true\n'
            "    leccion:\n"
            "        L\n"
        )

    def _falla(self, texto: str) -> sintaxis.ErrorSintaxis:
        with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
            sintaxis_caso.leer(texto)
        return cm.exception

    def test_tropiezo_1_olvida_el_origen(self) -> None:
        texto = (
            "caso 001-prueba:\n"
            '    fecha: "2026-08-26"\n'
            '    titulo: "T"\n'
            "    etiqueta: verde_correcto\n"
            "    sintoma:\n"
            "        S\n"
            "    como_se_detecto: observacion\n"
            "    medida: demo.mide\n"
            "    evidencia:\n"
            "        tarea: id, vencida\n"
            '            "t-1", true\n'
            "    leccion:\n"
            "        L\n"
        )
        e = self._falla(texto)
        self.assertEqual(e.linea, 3)
        self.assertEqual(e.columna, 5)
        self.assertEqual(str(e), "línea 3, columna 5: se esperaba línea «origen:»; llegó 'titulo: \"T\"'")
        fragmento = sintaxis.fragmento_de_error(e, texto)
        self.assertIn("se esperaba línea «origen:»", fragmento)
        self.assertIn("   3 |     titulo: \"T\"", fragmento)

    def test_tropiezo_2_etiqueta_inventada(self) -> None:
        texto = self._caso_base().replace("etiqueta: verde_correcto", "etiqueta: rojo_feo")
        e = self._falla(texto)
        self.assertEqual(e.linea, 7)
        self.assertEqual(e.columna, 15)
        self.assertIn("etiqueta en", str(e))
        self.assertIn("rojo_feo", str(e))
        fragmento = sintaxis.fragmento_de_error(e, texto)
        self.assertIn("   7 |     etiqueta: rojo_feo", fragmento)
        self.assertIn("     |               ^", fragmento)

    def test_tropiezo_2b_como_se_detecto_inventado(self) -> None:
        texto = self._caso_base().replace("como_se_detecto: observacion", "como_se_detecto: inventado")
        e = self._falla(texto)
        self.assertEqual(e.linea, 10)
        self.assertEqual(e.columna, 22)
        self.assertIn("como_se_detecto en", str(e))
        self.assertIn("inventado", str(e))
        fragmento = sintaxis.fragmento_de_error(e, texto)
        self.assertIn("  10 |     como_se_detecto: inventado", fragmento)
        self.assertIn("     |                      ^", fragmento)

    def test_tropiezo_3_fila_con_menos_columnas(self) -> None:
        texto = self._caso_base().replace('"t-1", true', '"t-1"')
        e = self._falla(texto)
        self.assertEqual(e.linea, 14)
        self.assertEqual(e.columna, 13)
        self.assertEqual(
            str(e),
            "línea 14, columna 13: la relación «tarea» declara 2 campos (id, vencida) y esta fila trae 1; llegó '\"t-1\"'",
        )
        fragmento = sintaxis.fragmento_de_error(e, texto)
        self.assertIn("  14 |             \"t-1\"", fragmento)
        self.assertIn("     |             ^", fragmento)

    def test_tropiezo_4_fila_con_mas_columnas(self) -> None:
        texto = self._caso_base().replace('"t-1", true', '"t-1", true, 9')
        e = self._falla(texto)
        self.assertEqual(e.linea, 14)
        self.assertEqual(e.columna, 13)
        self.assertEqual(
            str(e),
            "línea 14, columna 13: la relación «tarea» declara 2 campos (id, vencida) y esta fila trae 3; llegó '\"t-1\", true, 9'",
        )
        fragmento = sintaxis.fragmento_de_error(e, texto)
        self.assertIn("  14 |             \"t-1\", true, 9", fragmento)
        self.assertIn("     |             ^", fragmento)

    def test_tropiezo_5_olvida_las_comillas(self) -> None:
        texto = self._caso_base().replace('fecha: "2026-08-26"', "fecha: 2026-08-26")
        e = self._falla(texto)
        self.assertEqual(e.linea, 2)
        self.assertEqual(e.columna, 16)
        self.assertEqual(
            str(e),
            "línea 2, columna 16: se esperaba texto entre comillas; llegó '-08-26'",
        )
        fragmento = sintaxis.fragmento_de_error(e, texto)
        self.assertIn("   2 |     fecha: 2026-08-26", fragmento)
        self.assertIn("     |                ^", fragmento)

    def test_tropiezo_6_campos_sin_coma(self) -> None:
        texto = self._caso_base().replace("tarea: id, vencida", "tarea: id vencida")
        e = self._falla(texto)
        self.assertEqual(e.linea, 13)
        self.assertEqual(e.columna, 19)
        self.assertEqual(
            str(e),
            "línea 13, columna 19: se esperaba ',' entre campos; llegó 'vencida'",
        )
        fragmento = sintaxis.fragmento_de_error(e, texto)
        self.assertIn("  13 |         tarea: id vencida", fragmento)
        self.assertIn("     |                   ^", fragmento)


class ElErrorDiceQueHacerNoSoloQueEsperabaTests(unittest.TestCase):
    """Un error que nombra la gramática es correcto y deja a la persona donde estaba.

    Caminando el recorrido de alguien que escribe su primera medida, cuatro de diez tropiezos
    terminaban en un mensaje cierto e inútil. «se esperaba expresión; llegó \'=\'» no le enseña a
    nadie que la comparación se escribe `==`.

    Criterio: el mensaje contiene **lo que hay que hacer**, no sólo lo que se esperaba. Y la posición
    sigue siendo exacta — un mensaje amable que señala la línea equivocada es peor que uno seco que
    acierta.
    """

    CUERPO = ('ninguno tareas.vencida:\n'
              '    de tarea t\n'
              '    donde t.vencida == true\n'
              '    umbral <= 0 porque "una tarea vencida sin dueño no la va a hacer nadie"\n'
              '    alcance "ve el par vencida+sin-dueño y nada más"\n')

    def _error(self, texto):
        with self.assertRaises(sintaxis.ErrorSintaxis) as cm:
            sintaxis.leer(texto)
        return cm.exception

    def test_un_igual_solo_ensena_el_doble_igual(self) -> None:
        e = self._error(self.CUERPO.replace("t.vencida ==", "t.vencida ="))
        self.assertIn("«==»", str(e))
        self.assertEqual((e.linea, e.columna), (3, 21))

    def test_un_acento_en_un_nombre_explica_la_gramatica(self) -> None:
        """Y aclara que la prosa SÍ los lleva: si no, el mensaje asusta de más y alguien
        termina escribiendo el `porque` sin tildes."""
        e = self._error(self.CUERPO.replace("t.vencida", "t.vencída"))
        self.assertIn("minúsculas ASCII", str(e))
        self.assertIn("porque", str(e))
        self.assertEqual((e.linea, e.columna), (3, 17))

    def test_la_linea_que_falta_se_nombra(self) -> None:
        for palabra, quitar in (
                ("alcance", '    alcance "ve el par vencida+sin-dueño y nada más"\n'),
                ("donde", "    donde t.vencida == true\n")):
            with self.subTest(falta=palabra):
                e = self._error(self.CUERPO.replace(quitar, ""))
                self.assertIn(f"`{palabra}`", str(e))
                self.assertIn("de, donde, umbral, alcance", str(e))

    def test_un_cuerpo_de_mas_no_se_confunde_con_uno_de_menos(self) -> None:
        e = self._error(self.CUERPO + "    sobra\n")
        self.assertIn("y llegaron 5", str(e))
        self.assertNotIn("le falta", str(e))

    def test_el_umbral_de_igualdad_dice_por_que_esta_prohibido(self) -> None:
        e = self._error(self.CUERPO.replace("umbral <= 0", "umbral == 0"))
        self.assertIn("meta.ningun_umbral_de_igualdad", str(e))

    def test_pero_un_umbral_distinto_de_cero_no_habla_de_igualdad(self) -> None:
        """Sumar la prohibición a un `<= 1` mezcla dos problemas y confunde."""
        e = self._error(self.CUERPO.replace("umbral <= 0", "umbral <= 1"))
        self.assertIn("«<= 1»", str(e))
        self.assertNotIn("meta.ningun_umbral_de_igualdad", str(e))

    def test_el_cuerpo_vacio_senala_donde_iria_la_primera_linea(self) -> None:
        """No una línea que no existe: la 2, que es donde empieza el cuerpo."""
        e = self._error("ninguno d.n:\n")
        self.assertEqual((e.linea, e.columna), (2, 1))


class ConvertirTraduceEnLasTresDireccionesTests(unittest.TestCase):
    """El último paso de autoría que seguía exigiendo el checkout de Oracle.

    Existía sólo como `python tools/sintaxis.py --imprimir|--leer`, y por eso la documentación tenía
    que dejarlo escrito así: no se documenta un comando que no existe. Ahora es `oracle convertir`,
    con un solo verbo porque la dirección la dice la extensión.
    """

    def _correr(self, ruta):
        import io
        from contextlib import redirect_stdout
        from tools import cli
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = cli.main(["convertir", str(ruta), "--proyecto", str(RAIZ)])
        return codigo, salida.getvalue()

    def test_una_medida_en_superficie_sale_como_json(self) -> None:
        import json as _json
        from nucleo.medida import ruta_de_medida
        ruta = ruta_de_medida("meta.donde_compone", RAIZ / "catalogos",
                              *sorted((RAIZ / "perfiles").glob("*/catalogos")))
        codigo, salida = self._correr(ruta)
        self.assertEqual(codigo, 0)
        self.assertEqual(_json.loads(salida)[1], "meta.donde_compone")

    def test_una_medida_en_json_sale_como_superficie(self) -> None:
        from nucleo.medida import rutas_de_catalogo
        jsons = [r for r in rutas_de_catalogo(RAIZ / "catalogos") if r.suffix == ".json"]
        self.assertTrue(jsons, "el catálogo dejó de tener medidas en JSON")
        codigo, salida = self._correr(jsons[0])
        self.assertEqual(codigo, 0)
        self.assertEqual(sintaxis.leer(salida)[1], jsons[0].stem)

    def test_una_extension_desconocida_no_adivina(self) -> None:
        codigo, salida = self._correr(RAIZ / "README.md")
        self.assertEqual(codigo, 1)
        self.assertIn(".oracle", salida)

    def test_un_archivo_roto_señala_donde(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "roto.oracle"
            ruta.write_text("ninguno d.m:\n    de a\n", encoding="utf-8")
            codigo, salida = self._correr(ruta)
            self.assertEqual(codigo, 1)
            self.assertIn("^", salida)


if __name__ == "__main__":
    unittest.main()
