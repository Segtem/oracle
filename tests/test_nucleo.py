"""Tests del núcleo. `unittest` puro: el repo no tiene dependencias, ni de desarrollo.

(El oráculo viejo de Jam tenía 13 archivos de test escritos para pytest y sin pytest instalado: 0
tests corriendo durante 8 días. No se repite.)
"""

from __future__ import annotations

import json
import importlib
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo import algebra
from nucleo.algebra import ErrorDeAlgebra, LimitesAlgebra, desde, evaluar_expr, resumir
from nucleo.medida import (ClasificacionMeta, Informe, Medida, clasificacion_meta_base,
                           MedidaMalDeclarada, cargar, cargar_catalogo, como_hechos, evaluar,
                           inventario, puntos_ciegos)

EV = {"pieza": [{"id": "a", "x": 0}, {"id": "b", "x": 7}]}


def setUpModule() -> None:
    """Registra las escalares del catálogo base DENTRO de la suite, no al importar el módulo.

    Como `import catalogos.escalares` al tope, el decorador `@escalar` corría durante el
    descubrimiento: un mutante en `escalar()`, `_registro()` o `_contrato_de_escalar()` rompía la
    importación del archivo de test y el arnés lo reportaba como «error» en vez de «muerte». Once
    mutantes de `nucleo/algebra.py` quedaban sin veredicto por esto. Acá el fallo es del test.
    """
    importlib.import_module("catalogos.escalares")


def _medida(pred=None, porque="una razón", alcance="NO ve nada más", umbral=("<=", 0)):
    return ["medida", "d.prueba",
            ["desde", ["de", "pieza", "p"], ["donde", pred or [">", ["campo", "p", "x"], 3]]],
            ["resumen", "contar", 1],
            ["umbral", umbral[0], umbral[1], porque],
            ["alcance", alcance]]


class AlgebraTests(unittest.TestCase):
    def test_los_limites_de_recursos_son_explicitos_y_configurables(self) -> None:
        with self.assertRaisesRegex(ErrorDeAlgebra, "supera el límite de 2"):
            desde(["desde", ["de", "pieza", "p"]],
                  {"pieza": [{"id": 1}, {"id": 2}, {"id": 3}]},
                  LimitesAlgebra(filas_por_relacion=2))

        producto = ["desde", ["unir", ["de", "a", "a"], ["de", "b", "b"]]]
        with self.assertRaisesRegex(ErrorDeAlgebra, "producto cartesiano.*4.*límite de 3"):
            desde(producto, {"a": [{}, {}], "b": [{}, {}]},
                  LimitesAlgebra(producto_cartesiano=3))
        self.assertEqual(len(desde(producto, {"a": [{}, {}], "b": [{}, {}]},
                                   LimitesAlgebra(producto_cartesiano=4))), 4)

        profunda = ["no", ["no", ["no", True]]]
        with self.assertRaisesRegex(ErrorDeAlgebra, "profundidad máxima"):
            evaluar_expr(profunda, {}, LimitesAlgebra(profundidad_expresion=2))
        self.assertFalse(evaluar_expr(profunda, {}, LimitesAlgebra(profundidad_expresion=3)))

    def test_un_limite_invalido_no_se_convierte_en_sin_limite(self) -> None:
        for invalido in (0, -1, True, 1.5):
            with self.subTest(invalido=invalido):
                with self.assertRaises(ErrorDeAlgebra):
                    LimitesAlgebra(filas_por_relacion=invalido)

    def test_un_literal_se_evalua_a_si_mismo(self) -> None:
        for lit in (3, "hola", True, None, 2.5):
            self.assertEqual(evaluar_expr(lit, {}), lit)

    def test_los_accesores_son_explicitos(self) -> None:
        fila = {"p": {"id": "a", "x": 9}, "_": {"doble": 18}}
        self.assertEqual(evaluar_expr(["campo", "p", "x"], fila), 9)
        self.assertEqual(evaluar_expr(["hecho", "p"], fila), {"id": "a", "x": 9})
        self.assertEqual(evaluar_expr(["col", "doble"], fila), 18)

    def test_un_string_nunca_se_confunde_con_un_alias(self) -> None:
        # si un string suelto significara «alias», un dato de texto cambiaría de sentido
        self.assertEqual(evaluar_expr("p", {"p": {"x": 1}}), "p")

    def test_comparar_contra_un_campo_ausente_es_error_y_no_False(self) -> None:
        with self.assertRaises(ErrorDeAlgebra) as e:
            evaluar_expr([">", ["campo", "p", "no_existe"], 0], {"p": {"x": 1}})
        self.assertIn("ausente", str(e.exception))

    def test_comparar_objetos_no_escalares_es_error(self) -> None:
        with self.assertRaisesRegex(ErrorDeAlgebra, "sólo compara escalares"):
            evaluar_expr(["==", ["hecho", "p"], ["hecho", "p"]], {"p": {"x": 1}})

    def test_la_igualdad_EXACTA_sobre_flotantes_esta_prohibida(self) -> None:
        """La última pregunta abierta de la especificación, resuelta negándose: 0.1+0.2 no es 0.3, y
        una medida que compare así diría verde sin que nadie se enterara."""
        for expr in ([" ==".strip(), 0.3, ["mas", 0.1, 0.2]], ["!=", 1.0, 1]):
            with self.subTest(expr=expr):
                with self.assertRaises(ErrorDeAlgebra) as e:
                    evaluar_expr(expr, {})
                self.assertIn("falsedad silenciosa", str(e.exception))

    def test_pero_los_enteros_y_booleanos_se_comparan_exacto(self) -> None:
        self.assertTrue(evaluar_expr(["==", 3, 3], {}))
        self.assertTrue(evaluar_expr(["==", True, True], {}))
        self.assertFalse(evaluar_expr(["!=", 0, 0], {}))

    def test_y_el_orden_sobre_flotantes_sigue_permitido(self) -> None:
        # una tolerancia es justamente una comparación de orden: eso está bien
        self.assertTrue(evaluar_expr(["<=", 0.5, 1.0], {}))
        self.assertTrue(evaluar_expr([">", 2.5, 1.0], {}))

    def test_cerca_reemplaza_la_igualdad_con_una_tolerancia_a_la_vista(self) -> None:
        self.assertTrue(evaluar_expr(["<=", ["cerca", ["mas", 0.1, 0.2], 0.3], 1e-9], {}))
        self.assertFalse(evaluar_expr(["<=", ["cerca", 1.0, 2.0], 0.1], {}))

    def test_un_alias_inexistente_no_pasa_en_silencio(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            evaluar_expr(["campo", "q", "x"], {"p": {"x": 1}})

    def test_una_cabeza_desconocida_es_error(self) -> None:
        # ojo: `penetracion` YA es una escalar declarada (dominio geometría). Hace falta un nombre
        # que de verdad no exista, o el test deja de comprobar lo que dice.
        with self.assertRaises(ErrorDeAlgebra) as e:
            evaluar_expr(["esta_escalar_no_existe", 1, 2], {})
        self.assertIn("escalar declarada", str(e.exception))

    def test_una_expresion_mal_formada_da_ErrorDeAlgebra_y_no_ValueError(self) -> None:
        invalidas = (["campo", "p"], ["hecho", "p", "extra"], ["col"],
                     ["==", 1], ["!=", 1, 2, 3], ["no", True, False],
                     ["y", True], ["o"], [], {"no": "escalar"})
        for expr in invalidas:
            with self.subTest(expr=expr):
                with self.assertRaises(ErrorDeAlgebra):
                    evaluar_expr(expr, {"p": {"x": 1}})

    def test_la_escalar_declarada_se_llama(self) -> None:
        self.assertTrue(evaluar_expr(["contiene", "NO ve la malla", "NO "], {}))
        self.assertFalse(evaluar_expr(["contiene", "ve la malla", "NO "], {}))

    def test_declarar_dos_veces_la_misma_escalar_es_error(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            algebra.escalar("contiene")(lambda *a: None)

    def test_donde_filtra_y_lo_que_queda_son_los_testigos(self) -> None:
        filas = desde(["desde", ["de", "pieza", "p"], ["donde", [">", ["campo", "p", "x"], 3]]], EV)
        self.assertEqual([f["p"]["id"] for f in filas], ["b"])

    def test_una_relacion_ausente_es_error_y_no_un_verde_vacio(self) -> None:
        with self.assertRaisesRegex(ErrorDeAlgebra, "no existe"):
            desde(["desde", ["de", "fantasma", "f"]], EV)

    def test_una_relacion_presente_y_vacia_da_cero_filas(self) -> None:
        self.assertEqual(desde(["desde", ["de", "vacia", "v"]], {"vacia": []}), [])

    def test_una_relacion_es_BOLSA_y_conserva_hechos_repetidos(self) -> None:
        hecho = {"id": "repetido", "x": 2}
        filas = desde(["desde", ["de", "pieza", "p"]], {"pieza": [hecho, hecho]})
        self.assertEqual(resumir(["resumen", "contar", 1], filas), 2)

    def test_agrupar_conserva_la_multiplicidad_de_la_bolsa(self) -> None:
        ev = {"pieza": [{"grupo": "a", "x": 2}, {"grupo": "a", "x": 2}]}
        filas = desde(
            ["desde", ["de", "pieza", "p"],
             ["agrupar", [["grupo", ["campo", "p", "grupo"]]],
              [["total", "suma", ["campo", "p", "x"]]]]], ev)
        self.assertEqual(filas, [{"_": {"grupo": "a", "total": 4}}])

    def test_una_tuberia_sin_fuente_se_rechaza(self) -> None:
        with self.assertRaisesRegex(ErrorDeAlgebra, "necesita una fuente"):
            desde(["desde"], EV)

    def test_la_tuberia_tiene_que_empezar_con_una_fuente(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            desde(["desde", ["donde", True]], EV)

    def test_un_operador_sin_usuarios_no_forma_parte_del_lenguaje_activo(self) -> None:
        with self.assertRaisesRegex(ErrorDeAlgebra, "operador desconocido"):
            desde(["desde", ["de", "pieza", "p"], ["con", "x", 1]], EV)

    def test_unir_hace_el_producto_y_conviven_los_alias(self) -> None:
        filas = desde(["desde", ["unir", ["de", "pieza", "a"], ["de", "pieza", "b"]]], EV)
        self.assertEqual(len(filas), 4)
        self.assertEqual(sorted(filas[0]), ["a", "b"])

    def test_unir_con_alias_repetido_no_pasa_en_silencio(self) -> None:
        with self.assertRaises(ErrorDeAlgebra) as e:
            desde(["desde", ["unir", ["de", "pieza", "a"], ["de", "pieza", "a"]]], EV)
        self.assertIn("alias repetido", str(e.exception))

    def test_unir_no_publica_un_modo_izquierda_sin_usuarios(self) -> None:
        with self.assertRaisesRegex(ErrorDeAlgebra, "unir.*fuente_izq"):
            desde(["desde", ["unir", ["de", "pieza", "a"], ["de", "pieza", "b"], "izquierda"]], EV)

    def test_unir_solo_acepta_fuentes(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            desde(["desde", ["unir", ["donde", True], ["de", "pieza", "b"]]], EV)

    def test_agrupar_devuelve_UNA_fila_por_grupo_con_columnas_derivadas(self) -> None:
        ev = {"cosa": [{"g": "a", "n": 1}, {"g": "a", "n": 2}, {"g": "b", "n": 5}]}
        filas = desde(["desde", ["de", "cosa", "c"],
                       ["agrupar", [["grupo", ["campo", "c", "g"]]],
                                   [["cuantos", "contar", 1], ["total", "suma", ["campo", "c", "n"]]]]],
                      ev)
        # un grupo NO es un hecho: no lleva alias, lleva columnas derivadas
        self.assertEqual(
            sorted((f["_"]["grupo"], f["_"]["cuantos"], f["_"]["total"]) for f in filas),
            [("a", 2, 3), ("b", 1, 5)])
        self.assertNotIn("c", filas[0])

    def test_agrupar_expresa_la_AUSENCIA_sin_nulos(self) -> None:
        """Era una de las preguntas abiertas de la especificación. El truco no es un LEFT JOIN con
        nulos: es agrupar sobre el producto SIN filtrar y sumar un predicado — los booleanos suman
        0 y 1, así que un grupo donde nada casó da cero y sigue existiendo."""
        ev = {"modulo": [{"nombre": "usado"}, {"nombre": "solo_por_test"}, {"nombre": "huerfano"}],
              "importa": [{"a": "x", "b": "usado", "es_test": False},
                          {"a": "t", "b": "solo_por_test", "es_test": True}]}
        filas = desde(["desde",
                       ["unir", ["de", "modulo", "m"], ["de", "importa", "i"]],
                       ["agrupar", [["modulo", ["campo", "m", "nombre"]]],
                                   [["reales", "suma",
                                     ["y", ["==", ["campo", "i", "b"], ["campo", "m", "nombre"]],
                                           ["==", ["campo", "i", "es_test"], False]]]]],
                       ["donde", ["==", ["col", "reales"], 0]]], ev)
        self.assertEqual(sorted(f["_"]["modulo"] for f in filas), ["huerfano", "solo_por_test"])

    def test_agrupar_con_un_agregado_desconocido_es_error(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            desde(["desde", ["de", "pieza", "p"],
                   ["agrupar", [["k", ["campo", "p", "id"]]], [["x", "moda", 1]]]], EV)

    def test_contar_no_evalua_la_expresion(self) -> None:
        filas = desde(["desde", ["de", "pieza", "p"]], EV)
        self.assertEqual(resumir(["resumen", "contar", ["campo", "p", "no_existe"]], filas), 2)

    def test_los_agregados_sobre_cero_filas_dan_cero(self) -> None:
        for agg in ("max", "min", "suma", "promedio"):
            self.assertEqual(resumir(["resumen", agg, ["campo", "p", "x"]], []), 0)

    def test_los_agregados_rechazan_no_finitos_y_tipos_incompatibles(self) -> None:
        for agg, valores in (
                ("suma", [float("inf")]),
                ("promedio", [float("nan")]),
                ("max", [1, "dos"]),
                ("min", [None])):
            with self.subTest(agregado=agg, valores=valores):
                filas = [{"p": {"x": valor}} for valor in valores]
                with self.assertRaises(ErrorDeAlgebra):
                    resumir(["resumen", agg, ["campo", "p", "x"]], filas)

    def test_un_agregado_rechaza_un_resultado_no_finito(self) -> None:
        filas = [{"p": {"x": 1e308}}, {"p": {"x": 1e308}}]
        with self.assertRaisesRegex(ErrorDeAlgebra, "finito"):
            resumir(["resumen", "suma", ["campo", "p", "x"]], filas)

    def test_suma_y_promedio_aceptan_booleanos_como_indicadores(self) -> None:
        filas = [{"p": {"x": True}}, {"p": {"x": False}}, {"p": {"x": True}}]
        self.assertEqual(resumir(["resumen", "suma", ["campo", "p", "x"]], filas), 2)
        self.assertAlmostEqual(
            resumir(["resumen", "promedio", ["campo", "p", "x"]], filas), 2 / 3)

    def test_max_sobre_filas_reales(self) -> None:
        filas = desde(["desde", ["de", "pieza", "p"]], EV)
        self.assertEqual(resumir(["resumen", "max", ["campo", "p", "x"]], filas), 7)

    def test_TODOS_los_comparadores_hacen_lo_que_dicen(self) -> None:
        """La mutación de código delató que sólo `<=` y `>` se ejercitaban: los otros cuatro estaban
        escritos y sin verificar. Cambiar `!=` por `==` en el álgebra no rompía ningún test."""
        casos = [("==", 2, 2, True), ("==", 2, 3, False),
                 ("!=", 2, 3, True), ("!=", 2, 2, False),
                 ("<", 1, 2, True), ("<", 2, 2, False),
                 ("<=", 2, 2, True), ("<=", 3, 2, False),
                 (">", 3, 2, True), (">", 2, 2, False),
                 (">=", 2, 2, True), (">=", 1, 2, False)]
        for op, a, b, esperado in casos:
            with self.subTest(op=op, a=a, b=b):
                self.assertEqual(evaluar_expr([op, a, b], {}), esperado)

    def test_y_o_no_hacen_lo_que_dicen(self) -> None:
        self.assertTrue(evaluar_expr(["y", True, True], {}))
        self.assertFalse(evaluar_expr(["y", True, False], {}))
        self.assertTrue(evaluar_expr(["o", False, True], {}))
        self.assertFalse(evaluar_expr(["o", False, False], {}))
        self.assertTrue(evaluar_expr(["no", False], {}))
        self.assertFalse(evaluar_expr(["no", True], {}))

    def test_el_decorador_escalar_devuelve_la_funcion_y_le_pone_la_unidad(self) -> None:
        @algebra.escalar("d_prueba_unidad", "cm")
        def _f(x):
            return x * 2

        try:
            self.assertEqual(_f(3), 6)                    # devuelve la función, no None
            self.assertEqual(_f.unidad, "cm")
            self.assertEqual((_f.aridad_min, _f.aridad_max), (1, 1))
            self.assertEqual(_f.nombre_escalar, "d_prueba_unidad")
            self.assertEqual(_f.procedencia_escalar, "oracle")
            self.assertIs(algebra.ESCALARES["d_prueba_unidad"], _f)
        finally:
            del algebra.ESCALARES["d_prueba_unidad"]

    def test_una_escalar_declara_nombre_unidad_y_firma_verificables(self) -> None:
        for nombre in ("Mayuscula", "con.punto", "con-guion", ""):
            with self.subTest(nombre=nombre), self.assertRaises(ErrorDeAlgebra):
                algebra.escalar(nombre)
        with self.assertRaises(ErrorDeAlgebra):
            algebra.escalar("unidad_rota", "cm\ninyectado")
        with self.assertRaises(ErrorDeAlgebra):
            @algebra.escalar("d_solo_keyword")
            def _solo_keyword(*, obligatorio):
                return obligatorio

    def test_promedio_sobre_filas_reales(self) -> None:
        filas = desde(["desde", ["de", "pieza", "p"]], EV)
        self.assertEqual(resumir(["resumen", "promedio", ["campo", "p", "x"]], filas), 3.5)
        self.assertEqual(resumir(["resumen", "suma", ["campo", "p", "x"]], filas), 7)
        self.assertEqual(resumir(["resumen", "min", ["campo", "p", "x"]], filas), 0)

    def test_un_agregado_desconocido_es_error(self) -> None:
        with self.assertRaises(ErrorDeAlgebra):
            resumir(["resumen", "moda", 1], [])


class MedidaTests(unittest.TestCase):
    def test_la_estructura_invalida_falla_al_CARGAR_y_no_al_evaluar(self) -> None:
        tuberias_invalidas = [
            [],
            7,
            ["desde"],
            ["desde", 7],
            ["desde", ["de", "pieza"]],
            ["desde", ["fantasma", "pieza", "p"]],
            ["desde", ["unir", 7, ["de", "pieza", "b"]]],
            ["desde", ["unir", ["de", "pieza", "a"],
                        ["de", "pieza", "b"], "modo-inventado"]],
            ["desde", ["de", "pieza", "p"], 7],
            ["desde", ["de", "pieza", "p"], ["donde"]],
            ["desde", ["de", "pieza", "p"], ["de", "pieza", "q"]],
            ["desde", ["unir", ["de", "pieza", "a"]]],
            ["desde", ["de", "pieza", "p"], ["con", "doble"]],
            ["desde", ["de", "pieza", "p"], ["agrupar", [], [["n", "contar"]]]],
            ["desde", ["de", "pieza", "p"],
             ["agrupar", 7, [["n", "contar", 1]]]],
            ["desde", ["de", "pieza", "p"],
             ["agrupar", [["nombre_sin_expresion"]], [["n", "contar", 1]]]],
            ["desde", ["de", "pieza", "p"], ["operador_nuevo", 1]],
        ]
        for tuberia in tuberias_invalidas:
            with self.subTest(tuberia=tuberia):
                datos = _medida()
                datos[2] = tuberia
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos(datos)

    def test_una_expresion_invalida_falla_al_CARGAR(self) -> None:
        expresiones_invalidas = (
            ["campo", "p"],
            ["campo", 7, "x"],
            ["hecho", "p", "extra"],
            ["col"],
            ["==", ["campo", "p", "x"]],
            ["no", True, False],
            ["y", True],
            ["escalar_que_no_existe", 1],
            ["contiene", "un solo argumento"],
            {"un": "objeto no es literal escalar"},
        )
        for expr in expresiones_invalidas:
            with self.subTest(expr=expr):
                datos = _medida(pred=expr)
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos(datos)

    def test_expresiones_de_resumen_y_agrupar_se_validan_al_CARGAR(self) -> None:
        medidas_invalidas = []

        resumen = _medida()
        resumen[3] = ["resumen", "max", ["campo", "p"]]
        medidas_invalidas.append(resumen)

        agrupar = _medida()
        agrupar[2].insert(2, ["agrupar", [["k", ["campo", "p"]]],
                              [["n", "contar", 1]]])
        medidas_invalidas.append(agrupar)

        agregado_sin_operador = _medida()
        agregado_sin_operador[2].insert(2, ["agrupar", [], [["n", [], 1]]])
        medidas_invalidas.append(agregado_sin_operador)

        for datos in medidas_invalidas:
            with self.subTest(datos=datos):
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos(datos)

    def test_fuente_exige_nombres_y_alias_de_texto(self) -> None:
        for fuente in (["de", 7, "p"], ["de", "pieza", None], ["de", "", "p"]):
            with self.subTest(fuente=fuente):
                datos = _medida()
                datos[2][1] = fuente
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos(datos)

    def test_el_id_exige_texto_no_vacio_y_sin_espacios(self) -> None:
        for mid in (7, None, "", "   ", "dominio con espacios"):
            with self.subTest(mid=mid):
                datos = _medida()
                datos[1] = mid
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos(datos)

    def test_una_escalar_registrada_respeta_argumentos_requeridos_opcionales_y_variadicos(self) -> None:
        @algebra.escalar("d_escalar_opcional")
        def opcional(a, b=1):
            return a + b

        @algebra.escalar("d_escalar_variadica")
        def variadica(*xs):
            return sum(xs)

        try:
            for expr in (["d_escalar_opcional", 1], ["d_escalar_opcional", 1, 2],
                         ["d_escalar_variadica"], ["d_escalar_variadica", 1, 2, 3]):
                Medida.de_datos(_medida(pred=[">", expr, 0]))
            for expr in (["d_escalar_opcional"], ["d_escalar_opcional", 1, 2, 3]):
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos(_medida(pred=[">", expr, 0]))
        finally:
            del algebra.ESCALARES["d_escalar_opcional"]
            del algebra.ESCALARES["d_escalar_variadica"]

    def test_umbral_defensa_y_alcance_exigen_tipos_basicos_al_CARGAR(self) -> None:
        invalidas = []
        for limite in ([], {}, None):
            datos = _medida()
            datos[4][2] = limite
            invalidas.append(datos)
        for porque in (7, [], None):
            invalidas.append(_medida(porque=porque))
        for alcance in (7, [], None):
            invalidas.append(_medida(alcance=alcance))

        for datos in invalidas:
            with self.subTest(datos=datos):
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos(datos)

    def test_la_forma_del_umbral_se_valida_al_CARGAR(self) -> None:
        for umbral in (None, [], ["umbral", "<=", 0],
                       ["otra-cosa", "<=", 0, "razon"]):
            with self.subTest(umbral=umbral):
                datos = _medida()
                datos[4] = umbral
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos(datos)

    def test_un_resumen_invalido_falla_al_CARGAR(self) -> None:
        for resumen in ([], ["resumen", "contar"], ["otra_cosa", "contar", 1],
                        ["resumen", "moda", 1], ["resumen", [], 1]):
            with self.subTest(resumen=resumen):
                datos = _medida()
                datos[3] = resumen
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos(datos)

    def test_con_esta_retirado_de_la_declaracion_activa(self) -> None:
        datos = _medida()
        datos[2].insert(2, ["con", "doble", ["campo", "p", "x"]])
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(datos)

    def test_un_umbral_sin_defensa_no_se_carga(self) -> None:
        with self.assertRaises(MedidaMalDeclarada) as e:
            Medida.de_datos(_medida(porque="   "))
        self.assertIn("defensa", str(e.exception))

    def test_una_medida_sin_alcance_no_se_carga(self) -> None:
        with self.assertRaises(MedidaMalDeclarada) as e:
            Medida.de_datos(_medida(alcance="  "))
        self.assertIn("alcance", str(e.exception))

    def test_un_operador_de_umbral_inventado_no_se_carga(self) -> None:
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(_medida(umbral=("≈", 0)))

    def test_un_umbral_rechaza_numeros_no_finitos_al_CARGAR(self) -> None:
        for limite in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(limite=limite):
                with self.assertRaisesRegex(MedidaMalDeclarada, "finito"):
                    Medida.de_datos(_medida(umbral=("<=", limite)))

    def test_la_igualdad_exacta_de_umbral_sobre_flotante_es_politica_no_contrato(self) -> None:
        """La regla dejó de ser un `raise` de carga: es una POLÍTICA reificada en L2.

        El umbral `== 0.3` está bien formado y se carga; el juicio de que es una mala idea vive en
        `algebra.comparar` (que sigue fallando cerrado al EVALUAR) y en
        `meta.ningun_umbral_flotante_de_igualdad` (que lo vuelve inspeccionable). Quitar el `raise`
        de carga no abre un hueco: la medida no puede producir un verde.
        """
        m = Medida.de_datos(_medida(umbral=("==", 0.3)))
        with self.assertRaisesRegex(ErrorDeAlgebra, "igualdad exacta"):
            m.evaluar(EV)

        datos = _medida(umbral=("==", 4))
        datos[3] = ["resumen", "promedio", ["campo", "p", "x"]]
        with self.assertRaisesRegex(ErrorDeAlgebra, "igualdad exacta"):
            Medida.de_datos(datos).evaluar({"pieza": [{"x": 4.0}]})

    def test_el_umbral_rechaza_tipos_incompatibles(self) -> None:
        with self.assertRaisesRegex(ErrorDeAlgebra, "incompatibles"):
            Medida.de_datos(_medida(umbral=("<=", "cero"))).evaluar(EV)

    def test_falla_al_LEERSE_y_no_al_usarse(self) -> None:
        # la diferencia importa: una medida mal declarada no debe poder existir a medias
        with self.assertRaises(MedidaMalDeclarada):
            Medida.de_datos(["medida", "x", [], []])

    def test_los_testigos_son_las_filas_que_sobrevivieron(self) -> None:
        v = Medida.de_datos(_medida()).evaluar(EV)
        self.assertEqual(v.valor, 1)
        self.assertFalse(v.ok)
        self.assertEqual([t["p"]["id"] for t in v.testigos], ["b"])

    def test_el_veredicto_tiene_la_misma_forma_para_cualquier_dominio(self) -> None:
        v = Medida.de_datos(_medida()).evaluar(EV)
        self.assertEqual(sorted(v.a_dict()),
                         ["alcance", "id", "ok", "porque", "sin_evidencia", "testigos",
                          "umbral", "valor"])

    def test_ida_y_vuelta_a_datos(self) -> None:
        d = _medida()
        self.assertEqual(Medida.de_datos(d).a_datos(), d)

    def test_una_medida_sin_requiere_no_cambia_de_forma_canonica(self) -> None:
        """`requiere` es opcional y no puede correr las rutas de mutación de lo que ya existía."""
        m = Medida.de_datos(_medida())
        self.assertEqual(m.requiere, ())
        self.assertEqual(len(m.a_datos()), 6)
        self.assertEqual(m.a_datos()[5][0], "alcance")

    def test_una_relacion_requerida_y_vacia_no_puede_dar_verde(self) -> None:
        """El falso verde de la ausencia: cuanto PEOR el mundo, más verde salía la medida.

        Con `unir`, un lado vacío no produce pares; sin pares no hay grupos; el agregado sobre cero
        filas da 0 y un umbral `<= 0` lo lee como verde. La medida más fuerte —«un módulo que no
        importa nadie»— se ponía verde justo cuando nadie importaba a nadie.
        """
        d = _medida()
        con_requiere = [*d[:5], ["requiere", "pieza"], d[5]]
        m = Medida.de_datos(con_requiere)
        self.assertEqual(m.requiere, ("pieza",))
        self.assertEqual(m.a_datos(), con_requiere)      # round-trip exacto

        for vacia in ({"pieza": []}, {}):
            with self.subTest(evidencia=vacia):
                v = m.evaluar(vacia)
                self.assertFalse(v.ok)                    # lo único inaceptable es el verde
                self.assertEqual(v.sin_evidencia, "pieza")
                self.assertEqual(v.testigos, ())
                self.assertIn("SIN EVIDENCIA", v.linea())

        # y con evidencia sí mide, sin quedar pegada en «sin evidencia»
        v = m.evaluar(EV)
        self.assertEqual(v.sin_evidencia, "")
        self.assertEqual(v.valor, 1)

    def test_requiere_mal_declarado_no_carga(self) -> None:
        d = _medida()
        for malo in (["requiere", ""], ["requiere", "a", "a"], ["requiere", 1], ["otra", "a"], "x"):
            with self.subTest(requiere=malo):
                with self.assertRaises(MedidaMalDeclarada):
                    Medida.de_datos([*d[:5], malo, d[5]])

    def test_un_informe_verde_enumera_lo_que_no_miro_y_nunca_dice_todo_verde(self) -> None:
        m = Medida.de_datos(_medida(pred=[">", ["campo", "p", "x"], 1000]))
        texto = evaluar([m], EV).texto()
        self.assertIn("SIN MIRAR", texto)
        self.assertIn("NO ve nada más", texto)
        self.assertNotIn("TODO VERDE", texto)

    def test_un_informe_sin_medidas_no_es_verde(self) -> None:
        informe = evaluar([], EV)
        self.assertFalse(informe.ok)
        self.assertIn("SIN MEDIDAS", informe.texto())
        self.assertNotIn("verde", informe.texto().lower())
        self.assertFalse(json.loads(informe.a_json())["ok"])

    def test_un_informe_rojo_no_promete_alcance(self) -> None:
        texto = evaluar([Medida.de_datos(_medida())], EV).texto()
        self.assertIn("en rojo", texto)
        self.assertNotIn("SIN MIRAR", texto)

    def test_la_linea_del_veredicto_dice_marca_valor_umbral_y_testigos(self) -> None:
        """El informe es contrato: los testigos son lo que una persona lee para actuar. La mutación
        de código delató que el formateo no lo verificaba nadie."""
        v = Medida.de_datos(_medida()).evaluar(EV)
        linea = v.linea()
        self.assertTrue(linea.startswith("✗"))
        self.assertIn("d.prueba", linea)
        self.assertIn("<= 0", linea)
        self.assertIn("p=b", linea)          # el testigo, identificado

    def test_un_veredicto_verde_no_lista_testigos(self) -> None:
        v = Medida.de_datos(_medida(pred=[">", ["campo", "p", "x"], 1000])).evaluar(EV)
        self.assertTrue(v.linea().startswith("✓"))
        self.assertNotIn("→", v.linea())

    def test_con_muchos_testigos_muestra_tres_y_cuenta_el_resto(self) -> None:
        muchos = {"pieza": [{"id": f"n{i}", "x": 9} for i in range(7)]}
        v = Medida.de_datos(_medida()).evaluar(muchos)
        linea = v.linea()
        self.assertEqual(linea.count("p=n"), 3)
        self.assertIn("+4", linea)

    def test_con_exactamente_tres_testigos_no_dice_mas(self) -> None:
        tres = {"pieza": [{"id": f"n{i}", "x": 9} for i in range(3)]}
        self.assertNotIn("+", Medida.de_datos(_medida()).evaluar(tres).linea().split("→")[1])

    def test_el_testigo_se_identifica_por_id_nombre_archivo_o_ruta(self) -> None:
        from nucleo.medida import _resumir_fila
        self.assertEqual(_resumir_fila({"a": {"id": "x"}}), "a=x")
        self.assertEqual(_resumir_fila({"a": {"nombre": "y"}}), "a=y")
        self.assertEqual(_resumir_fila({"a": {"ruta": "z.py"}}), "a=z.py")
        self.assertIn("otro", _resumir_fila({"a": {"otro": 1}}))

    def test_el_inventario_saca_los_umbrales_con_su_defensa(self) -> None:
        filas = inventario([Medida.de_datos(_medida())])
        self.assertEqual(filas[0]["umbral"], "<= 0")
        self.assertEqual(filas[0]["porque"], "una razón")

    def test_puntos_ciegos_lista_los_alcances(self) -> None:
        self.assertEqual(puntos_ciegos([Medida.de_datos(_medida())])[0]["alcance"],
                         "NO ve nada más")


class CatalogoRealTests(unittest.TestCase):
    """El catálogo del repo, cargado por el camino real."""

    def setUp(self) -> None:
        self.catalogo = cargar_catalogo(RAIZ / "catalogos")

    def test_todas_las_medidas_del_repo_cargan(self) -> None:
        self.assertGreaterEqual(len(self.catalogo), 8)

    def test_las_politicas_reificadas_se_cargan_y_juzgan(self) -> None:
        self.assertIn("meta.ningun_umbral_flotante_de_igualdad", self.catalogo)
        self.assertIn("meta.ningun_umbral_sin_defensa", self.catalogo)
        self.assertIn("meta.ninguna_medida_sin_alcance", self.catalogo)

        flotante = self.catalogo["meta.ningun_umbral_flotante_de_igualdad"]
        ofensa = {"medida": [{"id": "d.x", "umbral_es_flotante": True, "comparador": "=="}]}
        self.assertFalse(flotante.evaluar(ofensa).ok)
        sano = {"medida": [{"id": "d.x", "umbral_es_flotante": True, "comparador": "<="}]}
        self.assertTrue(flotante.evaluar(sano).ok)

        defensa = self.catalogo["meta.ningun_umbral_sin_defensa"]
        self.assertFalse(defensa.evaluar({"medida": [{"id": "d.x", "porque": ""}]}).ok)

        alcance = self.catalogo["meta.ninguna_medida_sin_alcance"]
        self.assertFalse(alcance.evaluar({"medida": [{"id": "d.x", "alcance": ""}]}).ok)

    def test_ninguna_medida_del_repo_tiene_umbral_sin_defensa(self) -> None:
        for f in inventario(self.catalogo.values()):
            self.assertTrue(f["porque"].strip(), f["id"])

    def test_como_hechos_sirve_el_catalogo_como_relacion_L2(self) -> None:
        hechos = como_hechos(self.catalogo.values())
        self.assertEqual(len(hechos), len(self.catalogo))
        self.assertEqual(sorted(hechos[0]),
                         ["agregado", "alcance", "comparador", "declara_requiere", "dominio",
                          "es_meta_por_el_nombre", "es_meta_por_lo_que_mide", "id", "pasos",
                          "porque", "relacion", "umbral", "umbral_es_flotante",
                          "umbral_op", "umbral_valor"])
        self.assertEqual(sorted(hechos.por_relacion),
                         ["fuente", "medida", "paso_de_medida", "requiere", "termino"])
        self.assertTrue(hechos.por_relacion["termino"])

    def test_los_dos_ejes_se_derivan_y_no_se_convienen(self) -> None:
        """El dominio sale del nombre; el NIVEL sale de sobre qué se mide. Que sean dos campos
        distintos es lo que permite comprobar que la convención se cumple."""
        hechos = {h["id"]: h for h in como_hechos(self.catalogo.values())}
        meta = hechos["meta.el_caso_se_pone_como_debe"]
        self.assertTrue(meta["es_meta_por_el_nombre"])
        self.assertTrue(meta["es_meta_por_lo_que_mide"])
        self.assertEqual(meta["relacion"], "caso")

        delMundo = hechos["proceso.verificador_sin_falsos_rojos"]
        self.assertFalse(delMundo["es_meta_por_el_nombre"])
        self.assertFalse(delMundo["es_meta_por_lo_que_mide"])
        self.assertEqual(delMundo["dominio"], "proceso")

    def test_el_alcance_no_impone_una_formula_textual_ni_un_idioma(self) -> None:
        medida = Medida.de_datos(_medida(alcance="Blind spots are documented elsewhere"))
        self.assertEqual(medida.alcance, "Blind spots are documented elsewhere")
        self.assertNotIn("meta.alcance_dice_que_no_ve", self.catalogo)

    def test_un_perfil_puede_extender_la_clasificacion_meta(self) -> None:
        medida = Medida.de_datos([
            "medida", "revision.regla", ["desde", ["de", "revision", "r"]],
            ["resumen", "contar", 1], ["umbral", "<=", 0, "una razón"],
            ["alcance", "a blind spot"],
        ])
        base = como_hechos([medida])[0]
        self.assertFalse(base["es_meta_por_el_nombre"])
        self.assertFalse(base["es_meta_por_lo_que_mide"])

        ampliada = clasificacion_meta_base().con(
            relaciones={"revision"}, prefijos=("revision.",))
        perfil = como_hechos([medida], ampliada)[0]
        self.assertTrue(perfil["es_meta_por_el_nombre"])
        self.assertTrue(perfil["es_meta_por_lo_que_mide"])

        with self.assertRaises(MedidaMalDeclarada):
            ClasificacionMeta({"revision"})

    def test_un_id_repetido_en_el_catalogo_no_pasa(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            for n in ("a.json", "b.json"):
                (Path(d) / n).write_text(json.dumps(_medida()), encoding="utf-8")
            with self.assertRaises(MedidaMalDeclarada):
                cargar_catalogo(Path(d))

    def test_catalogo_carga_oracle_sin_json(self) -> None:
        import tempfile
        from nucleo.sintaxis import imprimir

        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "d.prueba.oracle"
            ruta.write_text(imprimir(_medida()), encoding="utf-8")

            catalogo = cargar_catalogo(Path(d))

        self.assertEqual(set(catalogo), {"d.prueba"})

    def test_un_id_repetido_entre_json_y_oracle_nombra_los_dos_archivos(self) -> None:
        import tempfile
        from nucleo.sintaxis import imprimir

        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "a.json").write_text(json.dumps(_medida()), encoding="utf-8")
            (raiz / "b.oracle").write_text(imprimir(_medida()), encoding="utf-8")

            with self.assertRaises(MedidaMalDeclarada) as e:
                cargar_catalogo(raiz)

        mensaje = str(e.exception)
        self.assertIn("a.json", mensaje)
        self.assertIn("b.oracle", mensaje)

    def test_oracle_mal_formado_informa_archivo_linea_y_columna(self) -> None:
        import tempfile

        texto = "\n".join([
            "medida d.rota:",
            "    de pieza p",
            "    donde p.x ==",
            "    resumen contar(1)",
            "    umbral <= 0 porque \"razón\"",
            "    alcance \"NO ve nada más\"",
        ])
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "rota.oracle"
            ruta.write_text(texto, encoding="utf-8")

            with self.assertRaises(MedidaMalDeclarada) as e:
                cargar(ruta)

        mensaje = str(e.exception)
        self.assertIn("rota.oracle", mensaje)
        self.assertIn("línea 3", mensaje)
        self.assertIn("columna", mensaje)
        self.assertIn("^", mensaje)

    def test_oracle_vacio_no_es_catalogo_de_cero_medidas(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "vacia.oracle"
            ruta.write_text("  \n\t\n", encoding="utf-8")

            with self.assertRaises(MedidaMalDeclarada):
                cargar_catalogo(Path(d))

    def test_catalogo_rechaza_medidas_symlink(self) -> None:
        import tempfile
        from nucleo.sintaxis import imprimir

        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as afuera:
            real = Path(afuera) / "real.oracle"
            real.write_text(imprimir(_medida()), encoding="utf-8")
            (Path(d) / "enlace.oracle").symlink_to(real)

            with self.assertRaisesRegex(MedidaMalDeclarada, "symlink"):
                cargar_catalogo(Path(d))


class ClaveDeUnicidadEnMedidaTests(unittest.TestCase):
    """La clave de unicidad declarada por la relación, vista desde quien la mide.

    Es el criterio de éxito de la tarea: un duplicado bajo una clave declarada falla ANTES de medir
    nombrando la clave y la fila; sin clave, cero cambios de conducta; y la multiplicidad
    intencional sigue siendo expresable.
    """

    def _medida_contar(self, relacion="pieza"):
        return Medida.de_datos([
            "medida", "d.clave", ["desde", ["de", relacion, "p"]],
            ["resumen", "contar", 1], ["umbral", "<=", 0, "una razón"],
            ["alcance", "NO ve nada más"]])

    def test_un_duplicado_bajo_una_clave_declarada_falla_antes_de_medir(self) -> None:
        evidencia = {"pieza": [["clave", ["id"]], {"id": "a", "x": 9}, {"id": "a", "x": 9}]}
        with self.assertRaises(ErrorDeAlgebra) as error:
            self._medida_contar().evaluar(evidencia)
        mensaje = str(error.exception)
        self.assertIn("clave (id)", mensaje)
        self.assertIn("fila 1", mensaje)
        self.assertIn("fila 0", mensaje)

    def test_sin_clave_la_medida_cuenta_la_bolsa_como_siempre(self) -> None:
        hecho = {"id": "repetido", "x": 2}
        v = self._medida_contar().evaluar({"pieza": [hecho, hecho]})
        self.assertEqual(v.valor, 2)      # la multiplicidad sigue siendo evidencia

    def test_con_clave_y_sin_duplicado_la_medida_sale_como_la_evidencia_dicta(self) -> None:
        v = self._medida_contar().evaluar(
            {"pieza": [["clave", ["id"]], {"id": "a", "x": 9}, {"id": "b", "x": 9}]})
        self.assertEqual(v.valor, 2)

    def test_la_multiplicidad_intencional_se_expresa_no_declarando_clave(self) -> None:
        # dos observaciones del mismo id pueden ser dos eventos reales distintos: no declarar clave
        # conserva la semántica de bolsa sin obligar a fingir una identidad que el dominio no tiene
        v = self._medida_contar().evaluar(
            {"pieza": [{"id": "mismo", "t": 1}, {"id": "mismo", "t": 2}]})
        self.assertEqual(v.valor, 2)

    def test_el_lector_de_fixtures_rechaza_el_duplicado_nombrando_la_clave(self) -> None:
        from nucleo.fixtures import _validar_evidencia
        fallas = _validar_evidencia(
            {"pieza": [["clave", ["id"]], {"id": "x"}, {"id": "x"}]}, "demo")
        self.assertEqual(len(fallas), 1)
        self.assertIn("clave (id)", fallas[0])
        self.assertIn("fila 1", fallas[0])

    def test_el_lector_de_fixtures_acepta_una_clave_sin_duplicado(self) -> None:
        from nucleo.fixtures import _validar_evidencia
        self.assertEqual(_validar_evidencia(
            {"pieza": [["clave", ["id"]], {"id": "x"}, {"id": "y"}]}, "demo"), [])

    def test_el_lector_de_fixtures_rechaza_una_clave_mal_declarada(self) -> None:
        from nucleo.fixtures import _validar_evidencia
        fallas = _validar_evidencia({"pieza": [["clave", []], {"id": "x"}]}, "demo")
        self.assertTrue(any("clave" in f for f in fallas))


if __name__ == "__main__":
    unittest.main()
