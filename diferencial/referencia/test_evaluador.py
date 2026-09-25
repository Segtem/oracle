import math
import unittest

from evaluador import VERSION_ALGEBRA, ErrorDeAlgebra, LimitesAlgebra, evaluar


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

    def test_min_max_aceptan_booleanos_homogeneos(self):
        evidencia = {"muestra": [{"x": True}, {"x": False}, {"x": True}]}
        for agregado, esperado in (("min", False), ("max", True)):
            with self.subTest(agregado=agregado):
                medida = [
                    "medida", f"booleanos.{agregado}",
                    ["desde", ["de", "muestra", "m"]],
                    ["resumen", agregado, ["campo", "m", "x"]],
                    ["umbral", "==", esperado, "orden booleano"],
                    ["alcance", "booleanos homogeneos"],
                ]
                resultado = evaluar(medida, evidencia)
                self.assertIs(resultado["valor"], esperado)
                self.assertTrue(resultado["ok"])

    def test_version_algebra_es_0_8(self):
        self.assertEqual(VERSION_ALGEBRA, "1.0")

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

    def test_sin_basico_filtra_filas_que_cumplen(self):
        medida = [
            "medida",
            "test.sin.basico",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "pieza_id"], ["campo", "p", "id"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 1, "solo una pieza queda sin bloqueo"],
            ["alcance", "prueba basica de sin"],
        ]
        evidencia = {
            "pieza": [
                {"id": "p1", "nombre": "Muro"},
                {"id": "p2", "nombre": "Puerta"},
            ],
            "bloqueo": [
                {"pieza_id": "p1"},
            ],
        }
        resultado = evaluar(medida, evidencia)
        self.assertEqual(resultado["valor"], 1)
        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["testigos"], [{"p": {"id": "p2", "nombre": "Puerta"}}])

    def test_sin_relacion_vacia_deja_pasar_todas_las_filas(self):
        medida = [
            "medida",
            "test.sin.relacion_vacia",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "pieza_id"], ["campo", "p", "id"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 2, "pasan todas si no hay bloqueos"],
            ["alcance", "sin con relacion vacia"],
        ]
        evidencia = {
            "pieza": [{"id": "p1"}, {"id": "p2"}],
            "bloqueo": [],
        }
        resultado = evaluar(medida, evidencia)
        self.assertEqual(resultado["valor"], 2)
        self.assertTrue(resultado["ok"])
        self.assertEqual(len(resultado["testigos"]), 2)

    def test_sin_relacion_ausente_levanta_error(self):
        medida = [
            "medida",
            "test.sin.relacion_ausente",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "pieza_id"], ["campo", "p", "id"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "sin con relacion ausente"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, {"pieza": [{"id": "p1"}]})

    def test_sin_relacion_ausente_con_filas_entrantes_vacias_levanta_error(self):
        medida = [
            "medida",
            "test.sin.relacion_ausente_vacia",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "pieza_id"], ["campo", "p", "id"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "sin con relacion ausente aunque no haya filas entrantes"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, {"pieza": []})

    def test_sin_sin_cortocircuito_evalua_todas_las_filas(self):
        medida = [
            "medida",
            "test.sin.sin_cortocircuito",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "pieza_id"], ["campo", "p", "id"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "sin cortocircuito entre filas de la relacion derecha"],
        ]
        evidencia_1 = {
            "pieza": [{"id": "p1"}],
            "bloqueo": [
                {"pieza_id": "p1"},
                {"sin_campo": 123},
            ],
        }
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, evidencia_1)

        evidencia_2 = {
            "pieza": [{"id": "p1"}],
            "bloqueo": [
                {"sin_campo": 123},
                {"pieza_id": "p1"},
            ],
        }
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, evidencia_2)

    def test_sin_alias_duplicado_con_fila_entrante_levanta_error(self):
        medida = [
            "medida",
            "test.sin.alias_duplicado",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "p"],
                    ["==", ["campo", "p", "id"], 1],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "alias duplicado en sin"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, {"pieza": [{"id": "p1"}], "bloqueo": [{"id": 1}]})

    def test_sin_alias_duplicado_con_relacion_vacia_levanta_error(self):
        medida = [
            "medida",
            "test.sin.alias_duplicado_vacia",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "p"],
                    ["==", ["campo", "p", "id"], 1],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "alias duplicado en sin incluso si la relacion derecha esta vacia"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, {"pieza": [{"id": "p1"}], "bloqueo": []})

    def test_sin_alias_nuevo_no_escapa_a_pasos_posteriores(self):
        medida = [
            "medida",
            "test.sin.aislamiento_alias",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "pieza_id"], ["campo", "p", "id"]],
                ],
                ["donde", ["==", ["campo", "b", "pieza_id"], "p2"]],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "alias de sin no debe ser visible despues de sin"],
        ]
        evidencia = {
            "pieza": [{"id": "p2"}],
            "bloqueo": [],
        }
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, evidencia)

    def test_sin_despues_de_agrupar_con_col(self):
        medida = [
            "medida",
            "test.sin.despues_de_agrupar",
            [
                "desde",
                ["de", "modulo", "m"],
                ["agrupar", [["nombre", ["campo", "m", "nombre"]]], []],
                [
                    "sin",
                    ["de", "excluidos", "e"],
                    ["==", ["col", "nombre"], ["campo", "e", "nombre"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 1, "un solo modulo no excluido"],
            ["alcance", "sin despues de agrupar usando col"],
        ]
        evidencia = {
            "modulo": [
                {"nombre": "a"},
                {"nombre": "b"},
                {"nombre": "a"},
            ],
            "excluidos": [
                {"nombre": "a"},
            ],
        }
        resultado = evaluar(medida, evidencia)
        self.assertEqual(resultado["valor"], 1)
        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["testigos"], [{"nombre": "b"}])

    def test_sin_despues_de_agrupar_alias_colisiona_con_columna(self):
        medida = [
            "medida",
            "test.sin.colision_columna",
            [
                "desde",
                ["de", "modulo", "m"],
                ["agrupar", [["nombre", ["campo", "m", "nombre"]]], []],
                [
                    "sin",
                    ["de", "excluidos", "nombre"],
                    ["==", ["col", "nombre"], 1],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "alias colisiona con columna derivada"],
        ]
        evidencia = {
            "modulo": [{"nombre": "a"}],
            "excluidos": [{"nombre": "a"}],
        }
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, evidencia)

    def test_sin_supera_limite_filas_materializadas(self):
        medida = [
            "medida",
            "test.sin.limite_presupuesto",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "id"], ["campo", "p", "id"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "supera limite de presupuesto materializado"],
        ]
        evidencia = {
            "pieza": [{"id": i} for i in range(10_000)],
            "bloqueo": [{"id": i} for i in range(101)],
        }
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, evidencia)

    def test_sin_condicion_no_booleana_levanta_error(self):
        medida = [
            "medida",
            "test.sin.no_booleana",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["campo", "b", "id"],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "condicion de sin no booleana"],
        ]
        evidencia = {
            "pieza": [{"id": "p1"}],
            "bloqueo": [{"id": "b1"}],
        }
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, evidencia)

    def test_sin_como_operador_fuente_o_relacion_invalido(self):
        medida_fuente = [
            "medida",
            "test.sin.fuente",
            [
                "desde",
                ["sin", ["de", "bloqueo", "b"], True],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "sin como fuente inicial de desde"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_fuente, {"bloqueo": [{"id": 1}]})

        medida_unir = [
            "medida",
            "test.sin.en_unir",
            [
                "desde",
                ["unir", ["de", "pieza", "p"], ["sin", ["de", "bloqueo", "b"], True]],
            ],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "cero"],
            ["alcance", "sin dentro de unir"],
        ]
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida_unir, {"pieza": [{"id": 1}], "bloqueo": [{"id": 1}]})

    def test_sin_sintaxis_invalida_levanta_error(self):
        casos_sin_invalidos = [
            ["sin"],
            ["sin", ["de", "bloqueo", "b"]],
            ["sin", "bloqueo", True],
            ["sin", ["de", "", "b"], True],
            ["sin", ["de", "bloqueo", ""], True],
            ["sin", ["de", 123, "b"], True],
            ["sin", ["de", "bloqueo", 123], True],
            ["sin", ["de", "bloqueo", "b", "extra"], True],
            ["sin", ["de", "bloqueo", "b"], True, "extra"],
            ["sin", ["otro", "bloqueo", "b"], True],
        ]
        for paso_sin in casos_sin_invalidos:
            with self.subTest(paso_sin=paso_sin):
                medida = [
                    "medida",
                    "invalida.sin",
                    ["desde", ["de", "pieza", "p"], paso_sin],
                    ["resumen", "contar", 1],
                    ["umbral", "==", 1, "uno"],
                    ["alcance", "sintaxis invalida de sin"],
                ]
                with self.assertRaises(ErrorDeAlgebra):
                    evaluar(medida, {"pieza": [{"id": "p1"}], "bloqueo": [{"id": "b1"}]})

    def test_sin_con_funcion_escalar_y_hecho_entero(self):
        def coincide_prefijo(hecho_a, hecho_b):
            return hecho_a["id"][0] == hecho_b["id"][0]

        medida = [
            "medida",
            "test.sin.escalar_hecho",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["coincide_prefijo", ["hecho", "p"], ["hecho", "b"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 1, "solo una pieza no tiene bloqueo con mismo prefijo"],
            ["alcance", "sin con funcion escalar y hechos enteros"],
        ]
        evidencia = {
            "pieza": [
                {"id": "A1"},
                {"id": "B1"},
            ],
            "bloqueo": [
                {"id": "A9"},
            ],
        }
        resultado = evaluar(medida, evidencia, {"coincide_prefijo": coincide_prefijo})
        self.assertEqual(resultado["valor"], 1)
        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["testigos"], [{"p": {"id": "B1"}}])

    def test_sin_testigos_sin_donde_reflejan_filas_salientes_de_sin(self):
        medida = [
            "medida",
            "test.sin.testigos_sin_donde",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "id"], ["campo", "p", "id"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 1, "uno"],
            ["alcance", "testigos cuando no hay donde en tuberia con sin"],
        ]
        evidencia = {
            "pieza": [{"id": "p1"}, {"id": "p2"}],
            "bloqueo": [{"id": "p1"}],
        }
        resultado = evaluar(medida, evidencia)
        self.assertEqual(resultado["testigos"], [{"p": {"id": "p2"}}])

    def test_sin_testigos_con_donde_anterior(self):
        medida = [
            "medida",
            "test.sin.testigos_donde_anterior",
            [
                "desde",
                ["de", "pieza", "p"],
                ["donde", [">", ["campo", "p", "x"], 0]],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "id"], ["campo", "p", "id"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 1, "uno"],
            ["alcance", "testigos con donde antes de sin"],
        ]
        evidencia = {
            "pieza": [
                {"id": "p1", "x": 10},
                {"id": "p2", "x": 20},
                {"id": "p3", "x": -5},
            ],
            "bloqueo": [{"id": "p1"}],
        }
        resultado = evaluar(medida, evidencia)
        self.assertEqual(resultado["valor"], 1)
        self.assertEqual(
            resultado["testigos"],
            [{"p": {"id": "p2", "x": 20}}],
        )

    def test_sin_testigos_con_donde_posterior(self):
        medida = [
            "medida",
            "test.sin.testigos_donde_posterior",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "id"], ["campo", "p", "id"]],
                ],
                ["donde", [">", ["campo", "p", "x"], 0]],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 1, "uno"],
            ["alcance", "testigos con donde despues de sin"],
        ]
        evidencia = {
            "pieza": [
                {"id": "p1", "x": 10},
                {"id": "p2", "x": 20},
                {"id": "p3", "x": -5},
            ],
            "bloqueo": [{"id": "p1"}],
        }
        resultado = evaluar(medida, evidencia)
        self.assertEqual(resultado["valor"], 1)
        self.assertEqual(
            resultado["testigos"],
            [{"p": {"id": "p2", "x": 20}}],
        )

    def test_sin_preserva_multiplicidad_bolsa(self):
        medida = [
            "medida",
            "test.sin.multiplicidad",
            [
                "desde",
                ["de", "pieza", "p"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "id"], "x"],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 3, "tres"],
            ["alcance", "multiplicidad de hechos"],
        ]
        evidencia = {
            "pieza": [
                {"id": "p1"},
                {"id": "p1"},
                {"id": "p2"},
            ],
            "bloqueo": [{"id": "y"}, {"id": "z"}],
        }
        resultado = evaluar(medida, evidencia)
        self.assertEqual(resultado["valor"], 3)
        self.assertEqual(len(resultado["testigos"]), 3)

    def test_sin_multiple_en_cadena(self):
        medida = [
            "medida",
            "test.sin.encadenado",
            [
                "desde",
                ["de", "tarea", "t"],
                [
                    "sin",
                    ["de", "bloqueo", "b"],
                    ["==", ["campo", "b", "t_id"], ["campo", "t", "id"]],
                ],
                [
                    "sin",
                    ["de", "asignada", "a"],
                    ["==", ["campo", "a", "t_id"], ["campo", "t", "id"]],
                ],
            ],
            ["resumen", "contar", 1],
            ["umbral", "==", 1, "solo una tarea no bloqueada y no asignada"],
            ["alcance", "dos sin encadenados en una misma tuberia"],
        ]
        evidencia = {
            "tarea": [
                {"id": "t1"},
                {"id": "t2"},
                {"id": "t3"},
            ],
            "bloqueo": [
                {"t_id": "t1"},
            ],
            "asignada": [
                {"t_id": "t2"},
            ],
        }
        resultado = evaluar(medida, evidencia)
        self.assertEqual(resultado["valor"], 1)
        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["testigos"], [{"t": {"id": "t3"}}])


class ConcordanciaConNucleoTests(unittest.TestCase):
    def medida(self, fuente=None, umbral=None):
        return [
            "medida", "concordancia",
            ["desde", fuente or ["de", "pieza", "p"]],
            ["resumen", "contar", 1],
            umbral or ["umbral", "==", 1, "una pieza"],
            ["alcance", "contrato del álgebra"],
        ]

    def test_desigualdad_con_cualquier_flotante_levanta(self):
        for izquierda, derecha in ((1.0, 2.0), (1, 1.0), (1.0, 1)):
            with self.subTest(izquierda=izquierda, derecha=derecha):
                medida = self.medida(umbral=["umbral", "!=", derecha, "desigualdad"])
                medida[3] = ["resumen", "max", ["campo", "p", "x"]]
                with self.assertRaises(ErrorDeAlgebra):
                    evaluar(medida, {"pieza": [{"x": izquierda}]})

    def test_agrupar_exige_lista_de_agregados(self):
        medida = self.medida()
        medida[2].append(["agrupar", [], ["total", "contar", 1]])
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, {"pieza": [{"id": 1}]})
        medida[2][-1][2] = [["total", "contar", 1]]
        self.assertEqual(evaluar(medida, {"pieza": [{"id": 1}]})["valor"], 1)

    def test_clave_numera_hechos_desde_cero(self):
        medida = self.medida()
        for hechos, fragmento in (
            ([{"id": 1}, {"id": 1}], "fila 1; primera fila 0"),
            ([{"id": 1}, {"otro": 2}], "fila 1: id"),
        ):
            with self.subTest(hechos=hechos):
                with self.assertRaises(ErrorDeAlgebra) as error:
                    evaluar(medida, {"pieza": [["clave", ["id"]], *hechos]})
                self.assertIn(fragmento, str(error.exception))

    def test_unir_rechaza_subtuberia_desde(self):
        medida = self.medida(["unir", ["desde", ["de", "pieza", "p"]],
                              ["de", "pieza", "q"]])
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(medida, {"pieza": [{"id": 1}]})

    def test_segun_tiene_vocabulario_cerrado(self):
        evidencia = {"pieza": [{"id": 1}]}
        for origen in ("inventado", [], None):
            with self.subTest(origen=origen):
                with self.assertRaises(ErrorDeAlgebra):
                    evaluar(self.medida(umbral=["umbral", "==", 1, "uno", origen]), evidencia)
        for origen in ("medicion", "contrato", "convencion", "tanteo", "sin_declarar"):
            with self.subTest(origen=origen):
                self.assertTrue(evaluar(
                    self.medida(umbral=["umbral", "==", 1, "uno", origen]), evidencia
                )["ok"])

    def test_limites_tienen_nombres_y_valores_del_nucleo(self):
        self.assertEqual(LimitesAlgebra(), LimitesAlgebra(
            filas_por_relacion=100_000, producto_cartesiano=1_000_000,
            profundidad_expresion=64, expansiones_maximas=16,
        ))


if __name__ == "__main__":
    unittest.main()
