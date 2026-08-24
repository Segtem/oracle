import math
import unittest

from evaluador import ErrorDeAlgebra, evaluar


class EvaluadorTests(unittest.TestCase):
    def test_contar_preserva_multiplicidad_y_no_evalua_expr(self):
        medida = [
            "medida",
            "mutantes.sobrevivientes",
            [
                "desde",
                ["de", "mutante", "m"],
                ["donde", ["==", ["campo", "m", "murio"], False]],
            ],
            ["resumen", "contar", ["campo", "m", "campo_inexistente"]],
            ["umbral", "<=", 0, "no debe sobrevivir ningun mutante"],
            ["alcance", "cuenta mutantes declarados"],
        ]
        evidencia = {
            "mutante": [
                {"id": "a", "murio": False},
                {"id": "b", "murio": True},
                {"id": "a", "murio": False},
            ]
        }

        resultado = evaluar(medida, evidencia)

        self.assertEqual(resultado["id"], "mutantes.sobrevivientes")
        self.assertEqual(resultado["valor"], 2)
        self.assertFalse(resultado["ok"])
        self.assertEqual(
            resultado["testigos"],
            [
                {"m": {"id": "a", "murio": False}},
                {"m": {"id": "a", "murio": False}},
            ],
        )

    def test_campo_ausente_en_comparacion_es_error(self):
        medida = [
            "medida",
            "campo.ausente",
            ["desde", ["de", "pieza", "p"], ["donde", [">", ["campo", "p", "x"], 0]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "x debe existir"],
            ["alcance", "prueba de campo ausente"],
        ]

        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, {"pieza": [{"id": "sin_x"}]})

    def test_agrupar_y_sumar_booleanos_para_ausencia(self):
        medida = [
            "medida",
            "modulo.sin_importador_real",
            [
                "desde",
                ["unir", ["de", "modulo", "m"], ["de", "importa", "i"]],
                [
                    "agrupar",
                    [["modulo", ["campo", "m", "nombre"]]],
                    [
                        [
                            "reales",
                            "suma",
                            [
                                "y",
                                ["==", ["campo", "i", "b"], ["campo", "m", "nombre"]],
                                ["==", ["campo", "i", "es_test"], False],
                            ],
                        ]
                    ],
                ],
                ["donde", ["==", ["col", "reales"], 0]],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 1, "solo un modulo queda sin importador real"],
            ["alcance", "usa producto sin filtrar y agrupacion"],
        ]
        evidencia = {
            "modulo": [{"nombre": "a"}, {"nombre": "b"}],
            "importa": [
                {"b": "a", "es_test": False},
                {"b": "a", "es_test": True},
            ],
        }

        resultado = evaluar(medida, evidencia)

        self.assertEqual(resultado["valor"], 1)
        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["testigos"], [{"modulo": "b", "reales": 0}])

    def test_funcion_escalar_con_hechos_y_unir(self):
        def distinto(a, b):
            return a["id"] != b["id"]

        medida = [
            "medida",
            "pares.distintos",
            [
                "desde",
                ["unir", ["de", "pieza", "a"], ["de", "pieza", "b"]],
                ["donde", ["distinto", ["hecho", "a"], ["hecho", "b"]]],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 2, "dos pares ordenados distintos"],
            ["alcance", "producto cartesiano conserva multiplicidad"],
        ]

        resultado = evaluar(
            medida,
            {"pieza": [{"id": "p1"}, {"id": "p2"}]},
            {"distinto": distinto},
        )

        self.assertEqual(resultado["valor"], 2)
        self.assertTrue(resultado["ok"])

    def test_igualdad_exacta_entre_floats_falla_en_expresion_y_umbral(self):
        medida_expr = [
            "medida",
            "float.expr",
            ["desde", ["de", "muestra", "m"], ["donde", ["==", ["campo", "m", "x"], 1.0]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "sin igualdad exacta"],
            ["alcance", "prueba floats"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_expr, {"muestra": [{"x": 1.0}]})

        medida_umbral = [
            "medida",
            "float.umbral",
            ["desde", ["de", "muestra", "m"]],
            ["resumen", "suma", ["campo", "m", "x"]],
            ["umbral", "==", 1.0, "sin igualdad exacta"],
            ["alcance", "prueba floats"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_umbral, {"muestra": [{"x": 1.0}]})

    def test_no_finito_y_operador_desconocido_fallan(self):
        medida_nan = [
            "medida",
            "nan",
            ["desde", ["de", "muestra", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "nan invalido"],
            ["alcance", "prueba no finitos"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_nan, {"muestra": [{"x": math.nan}]})

        medida_con = [
            "medida",
            "con.prohibido",
            ["desde", ["con", ["de", "a", "a"], ["de", "b", "b"]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "con no existe"],
            ["alcance", "operador prohibido"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_con, {"a": [], "b": []})

    def test_agregados_sobre_cero_filas_devuelven_cero(self):
        for agregado in ["max", "min", "suma", "promedio", "contar"]:
            with self.subTest(agregado=agregado):
                medida = [
                    "medida",
                    f"cero.{agregado}",
                    ["desde", ["de", "muestra", "m"]],
                    ["resumen", agregado, ["campo", "m", "x"]],
                    ["umbral", "==", 0, "cero filas"],
                    ["alcance", "agregados vacios"],
                ]

                resultado = evaluar(medida, {"muestra": []})

                self.assertEqual(resultado["valor"], 0)
                self.assertTrue(resultado["ok"])
                self.assertEqual(resultado["testigos"], [])


if __name__ == "__main__":
    unittest.main()
