import math
import unittest

from evaluador import VERSION_ALGEBRA, ErrorDeAlgebra, evaluar


class EvaluadorTests(unittest.TestCase):
    def test_acepta_requiere_y_ambito_en_orden_canonico(self):
        medida = [
            "medida",
            "con.ambito",
            ["desde", ["de", "muestra", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "==", 1, "hay una muestra"],
            ["requiere", "muestra"],
            ["ambito", "del_origen"],
            ["alcance", "prueba el formato completo"],
        ]

        resultado = evaluar(medida, {"muestra": [{"id": "m1"}]})

        self.assertEqual(resultado["valor"], 1)
        self.assertTrue(resultado["ok"])

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

    def test_version_algebra_es_0_7(self):
        self.assertEqual(VERSION_ALGEBRA, "0.7")

    def test_requiere_con_condicion_filas_satisfecho(self):
        medida = [
            "medida",
            "test.requiere.condicion",
            ["desde", ["de", "mutante", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "==", 2, "dos mutantes"],
            ["requiere", ["filas", "mutante", "m", ["==", ["campo", "m", "tipo"], "codigo"]]],
            ["alcance", "prueba requiere con condicion"],
        ]
        evidencia = {
            "mutante": [
                {"id": "m1", "tipo": "codigo"},
                {"id": "m2", "tipo": "medida"},
            ]
        }
        resultado = evaluar(medida, evidencia)
        self.assertEqual(resultado["valor"], 2)
        self.assertTrue(resultado["ok"])

    def test_requiere_con_condicion_sin_filas_que_cumplan_devuelve_sin_evidencia(self):
        medida = [
            "medida",
            "test.requiere.sin_evidencia",
            ["desde", ["de", "mutante", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "umbral que seria verde con 0"],
            ["requiere", ["filas", "mutante", "m", ["==", ["campo", "m", "tipo"], "codigo"]]],
            ["alcance", "prueba sin evidencia cuando ninguna fila cumple"],
        ]
        evidencia = {
            "mutante": [
                {"id": "m1", "tipo": "medida"},
                {"id": "m2", "tipo": "medida"},
            ]
        }
        resultado = evaluar(medida, evidencia)
        self.assertEqual(resultado["valor"], "SIN EVIDENCIA")
        self.assertFalse(resultado["ok"])
        self.assertEqual(resultado["testigos"], [])

    def test_requiere_con_condicion_relacion_vacia_o_ausente_devuelve_sin_evidencia(self):
        medida = [
            "medida",
            "test.requiere.vacia",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "umbral que seria verde con 0"],
            ["requiere", ["filas", "mutante", "m", ["==", ["campo", "m", "tipo"], "codigo"]]],
            ["alcance", "prueba sin evidencia con relacion vacia o ausente"],
        ]
        resultado_vacia = evaluar(medida, {"pieza": [{"id": "p1"}], "mutante": []})
        self.assertEqual(resultado_vacia["valor"], "SIN EVIDENCIA")
        self.assertFalse(resultado_vacia["ok"])
        self.assertEqual(resultado_vacia["testigos"], [])

        resultado_ausente = evaluar(medida, {"pieza": [{"id": "p1"}]})
        self.assertEqual(resultado_ausente["valor"], "SIN EVIDENCIA")
        self.assertFalse(resultado_ausente["ok"])
        self.assertEqual(resultado_ausente["testigos"], [])

    def test_requiere_con_condicion_y_variantes_medida_real(self):
        medida = [
            "medida",
            "proceso.test_con_mutante_que_lo_mata",
            [
                "desde",
                ["de", "mutante", "m"],
                ["donde", ["==", ["campo", "m", "tipo"], "medida"]],
                [
                    "donde",
                    [
                        "y",
                        ["==", ["campo", "m", "detecciones_conductuales"], 0],
                        ["==", ["campo", "m", "rechazos_del_algebra"], 0],
                    ],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina"],
            ["requiere", ["filas", "mutante", "m", ["==", ["campo", "m", "tipo"], "medida"]]],
            ["alcance", "cuenta mutantes declarados que sobrevivieron"],
        ]
        evidencia_sin_medida = {
            "mutante": [
                {"id": "c1", "tipo": "codigo", "estado": "vivo"},
            ]
        }
        res1 = evaluar(medida, evidencia_sin_medida)
        self.assertEqual(res1["valor"], "SIN EVIDENCIA")
        self.assertFalse(res1["ok"])

        evidencia_ok = {
            "mutante": [
                {
                    "id": "m1",
                    "tipo": "medida",
                    "detecciones_conductuales": 1,
                    "rechazos_del_algebra": 0,
                }
            ]
        }
        res2 = evaluar(medida, evidencia_ok)
        self.assertEqual(res2["valor"], 0)
        self.assertTrue(res2["ok"])

    def test_requiere_condicion_campo_ausente_levanta_error(self):
        medida = [
            "medida",
            "test.campo.ausente.requiere",
            ["desde", ["de", "mutante", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["requiere", ["filas", "mutante", "m", ["==", ["campo", "m", "campo_inexistente"], 1]]],
            ["alcance", "campo ausente en requiere"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, {"mutante": [{"id": "m1", "tipo": "medida"}]})

    def test_requiere_condicion_no_booleana_levanta_error(self):
        medida = [
            "medida",
            "test.no_booleana",
            ["desde", ["de", "mutante", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["requiere", ["filas", "mutante", "m", ["campo", "m", "id"]]],
            ["alcance", "condicion devuelve string en vez de booleano"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, {"mutante": [{"id": "m1"}]})

    def test_requiere_condicion_alias_o_col_invalido_levanta_error(self):
        medida_otro_alias = [
            "medida",
            "test.otro_alias",
            ["desde", ["de", "mutante", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["requiere", ["filas", "mutante", "m", ["==", ["campo", "otro", "id"], "m1"]]],
            ["alcance", "usa alias diferente al declarado"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_otro_alias, {"mutante": [{"id": "m1"}]})

        medida_col = [
            "medida",
            "test.col_invalido",
            ["desde", ["de", "mutante", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["requiere", ["filas", "mutante", "m", ["==", ["col", "c"], 1]]],
            ["alcance", "usa col en condicion de requiere"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_col, {"mutante": [{"id": "m1"}]})

    def test_requiere_relacion_duplicada_levanta_error(self):
        medida_simples = [
            "medida",
            "dup1",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["requiere", "pieza", "pieza"],
            ["alcance", "relacion duplicada simple"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_simples, {"pieza": [{"id": "p1"}]})

        medida_mixta = [
            "medida",
            "dup2",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["requiere", "pieza", ["filas", "pieza", "p", ["==", ["campo", "p", "id"], "p1"]]],
            ["alcance", "relacion duplicada mixta"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_mixta, {"pieza": [{"id": "p1"}]})

        medida_filas = [
            "medida",
            "dup3",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            [
                "requiere",
                ["filas", "pieza", "p1", ["==", ["campo", "p1", "id"], "a"]],
                ["filas", "pieza", "p2", ["==", ["campo", "p2", "id"], "b"]],
            ],
            ["alcance", "relacion duplicada con condicion"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_filas, {"pieza": [{"id": "p1"}]})

    def test_requiere_condicion_sin_cortocircuito_falla_en_cualquier_orden(self):
        medida = [
            "medida",
            "sin.cortocircuito",
            ["desde", ["de", "mutante", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["requiere", ["filas", "mutante", "m", ["==", ["campo", "m", "estado"], "vivo"]]],
            ["alcance", "prueba no cortocircuito entre filas"],
        ]
        evidencia_1 = {
            "mutante": [
                {"id": "m1", "estado": "vivo"},
                {"id": "m2"},
            ]
        }
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, evidencia_1)

        evidencia_2 = {
            "mutante": [
                {"id": "m2"},
                {"id": "m1", "estado": "vivo"},
            ]
        }
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, evidencia_2)

    def test_requiere_error_algebra_no_se_oculta_por_relacion_vacia(self):
        medida = [
            "medida",
            "error.no.oculto",
            ["desde", ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            [
                "requiere",
                "relacion_vacia",
                ["filas", "mutante", "m", ["==", ["campo", "m", "campo_ausente"], 1]],
            ],
            ["alcance", "error de algebra no queda silenciado por relacion vacia"],
        ]
        evidencia = {
            "pieza": [{"id": "p1"}],
            "relacion_vacia": [],
            "mutante": [{"id": "m1"}],
        }
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, evidencia)

    def test_requiere_condicion_con_funcion_escalar(self):
        def es_positivo(x):
            return x > 0

        medida = [
            "medida",
            "requiere.escalar",
            ["desde", ["de", "muestra", "m"]],
            ["resumen", "contar", 1],
            ["umbral", "==", 1, "uno"],
            ["requiere", ["filas", "muestra", "m", ["es_positivo", ["campo", "m", "valor"]]]],
            ["alcance", "condicion con funcion escalar"],
        ]
        resultado = evaluar(
            medida,
            {"muestra": [{"valor": 10}]},
            {"es_positivo": es_positivo},
        )
        self.assertEqual(resultado["valor"], 1)
        self.assertTrue(resultado["ok"])

    def test_requiere_sintaxis_invalida_levanta_error(self):
        casos_invalidos = [
            ["requiere"],
            ["requiere", ""],
            ["requiere", 123],
            ["requiere", ["invalido", "mutante", "m", True]],
            ["requiere", ["filas", "mutante", "m"]],
            ["requiere", ["filas", "", "m", True]],
            ["requiere", ["filas", "mutante", "", True]],
        ]
        for req in casos_invalidos:
            with self.subTest(req=req):
                medida = [
                    "medida",
                    "invalida",
                    ["desde", ["de", "muestra", "m"]],
                    ["resumen", "contar", 1],
                    ["umbral", "==", 1, "uno"],
                    req,
                    ["alcance", "sintaxis invalida"],
                ]
                with self.assertRaises(ErrorDeAlgebra):
                    evaluar(medida, {"muestra": [{"id": "m1"}]})


if __name__ == "__main__":
    unittest.main()
