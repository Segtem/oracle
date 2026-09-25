"""Regresiones de las decisiones semánticas del álgebra 1.0."""
import unittest
from dataclasses import replace
from nucleo.algebra import ErrorDeAlgebra, desde, forzar_plan_unir
from nucleo.medida import Medida


def medida(tuberia=None, requiere=None):
    return Medida.de_datos(["medida", "test.algebra10", tuberia or ["desde", ["de", "a", "a"]],
                            ["resumen", "contar", 1], ["umbral", "<=", 0, "ausencia"],
                            *([ ["requiere", requiere] ] if requiere else []),
                            ["alcance", "prueba"]])


class Algebra10(unittest.TestCase):
    def test_testigos_son_salida_completa(self):
        tuberia = ["desde", ["de", "a", "a"], ["donde", True],
                   ["agrupar", [], [["n", "contar", 1]]]]
        self.assertEqual(medida(tuberia).evaluar({"a": [{"id": 1}]}).testigos,
                         ({"_": {"n": 1}},))

    def test_predicados_exigen_bool(self):
        for valor in (1, "sí", None):
            for paso in (["donde", valor], ["sin", ["de", "b", "b"], valor],
                         ["donde", ["y", True, valor]], ["donde", ["o", False, valor]],
                         ["donde", ["no", valor]]):
                with self.subTest(valor=valor, paso=paso), self.assertRaises(ErrorDeAlgebra):
                    desde(["desde", ["de", "a", "a"], paso], {"a": [{"id": 1}], "b": [{"id": 1}]})

    def test_clave_ajena_se_valida_antes_de_requiere(self):
        with self.assertRaisesRegex(ErrorDeAlgebra, "clave"):
            medida(requiere="ausente").evaluar({"a": [], "otra": [["clave", ["id"]], {"id": 1}, {"id": 1}]})

    def test_null_ajeno_se_rechaza_al_cargar(self):
        with self.assertRaises(ErrorDeAlgebra):
            medida(requiere="ausente").evaluar({"a": [], "otra": [{"x": None}]})

    def test_cabecera_sin_hechos_es_sin_evidencia(self):
        v = medida(requiere="a").evaluar({"a": [["clave", ["id"]]]})
        self.assertFalse(v.ok)
        self.assertEqual(v.sin_evidencia, "a")

    def test_requiere_condicional_exige_bool(self):
        m = replace(medida(), requiere=(["filas", "a", "a", 1],))
        with self.assertRaisesRegex(ErrorDeAlgebra, "booleano"):
            m.evaluar({"a": [{"id": 1}]})

    def test_unir_indexado_rechaza_tipos_incompatibles(self):
        tuberia = ["desde", ["unir", ["de", "a", "a"], ["de", "b", "b"]],
                   ["donde", ["==", ["campo", "a", "id"], ["campo", "b", "id"]]]]
        evidencia = {"a": [{"id": 1}], "b": [{"id": "1"}]}
        for indexado in (False, True):
            with self.subTest(indexado=indexado), forzar_plan_unir(indexado), self.assertRaisesRegex(ErrorDeAlgebra, "tipos incompatibles"):
                desde(tuberia, evidencia)

    def test_unir_indexado_no_cambia_la_semantica_con_claves_no_indexables(self):
        tuberia = ["desde", ["unir", ["de", "a", "a"], ["de", "b", "b"]],
                   ["donde", ["==", ["campo", "a", "id"], ["campo", "b", "id"]]]]
        for clave in (True, 1.5, None, [1]):
            evidencia = {"a": [{"id": clave}, {"id": clave}], "b": [{"id": clave}]}
            resultados = []
            for indexado in (False, True):
                with forzar_plan_unir(indexado):
                    try:
                        resultados.append(desde(tuberia, evidencia))
                    except ErrorDeAlgebra as e:
                        resultados.append(str(e))
            with self.subTest(clave=clave):
                self.assertEqual(resultados[0], resultados[1])

    def test_unir_indexado_ubica_el_error_como_el_producto(self):
        tuberia = ["desde", ["unir", ["de", "a", "a"], ["de", "b", "b"]],
                   ["donde", ["==", ["campo", "a", "id"], ["campo", "b", "id"]]]]
        mensajes = []
        for indexado in (False, True):
            with forzar_plan_unir(indexado), self.assertRaises(ErrorDeAlgebra) as error:
                desde(tuberia, {"a": [{"id": 1}], "b": [{"id": "1"}]})
            mensajes.append(str(error.exception))
        self.assertEqual(mensajes[0], mensajes[1])
        self.assertIn("en `", mensajes[1])

