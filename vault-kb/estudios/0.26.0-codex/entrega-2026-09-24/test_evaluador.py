import unittest

from evaluador import ErrorDeAlgebra, VERSION_ALGEBRA, evaluar


def medida(fuente, pasos=(), resumen=None, umbral=None, extra=()):
    return ["medida", "prueba", ["desde", fuente, *pasos],
            resumen or ["resumen", "contar", 1],
            umbral or ["umbral", "<=", 0, "contrato", "contrato"],
            *extra, ["alcance", "sólo mira esta evidencia"]]


class EvaluadorTests(unittest.TestCase):
    def test_version_y_bolsa(self):
        self.assertEqual(VERSION_ALGEBRA, "0.8")
        m = medida(["de", "pieza", "p"])
        resultado = evaluar(m, {"pieza": [{"id": 1}, {"id": 1}]})
        self.assertEqual(resultado["valor"], 2)
        self.assertFalse(resultado["ok"])
        self.assertEqual(resultado["testigos"], [{"p": {"id": 1}}] * 2)

    def test_clave_duplicada_y_ausente(self):
        m = medida(["de", "r", "a"])
        for filas in ([['clave', ['id']], {'id': 1}, {'id': 1}],
                      [['clave', ['id']], {'id': 1}, {'otro': 2}]):
            with self.assertRaises(ErrorDeAlgebra):
                evaluar(m, {"r": filas})

    def test_requiere_condicional_evaluacion_completa(self):
        m = medida(["de", "r", "r"], extra=(["requiere", ["filas", "s", "s", ["==", ["campo", "s", "tipo"], "a"]]],))
        self.assertEqual(evaluar(m, {"r": [], "s": [{"tipo": "b"}]})["valor"], "SIN EVIDENCIA")
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(m, {"r": [], "s": [{"tipo": "a"}, {}]})

    def test_sin_bolsa_y_sin_cortocircuito(self):
        paso = ["sin", ["de", "s", "s"], ["==", ["campo", "r", "id"], ["campo", "s", "id"]]]
        m = medida(["de", "r", "r"], [paso])
        resultado = evaluar(m, {"r": [{"id": 1}, {"id": 2}], "s": [{"id": 1}]})
        self.assertEqual(resultado["valor"], 1)
        self.assertEqual(resultado["testigos"], [{"r": {"id": 2}}])
        self.assertEqual(evaluar(m, {"r": [{"id": 1}], "s": []})["valor"], 1)
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(m, {"r": [{"id": 1}], "s": [{"id": 1}, {}]})
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(m, {"r": []})

    def test_sin_alias_repetido_aun_sin_filas(self):
        m = medida(["de", "r", "r"], [["sin", ["de", "s", "r"], True]])
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(m, {"r": [], "s": []})

    def test_agrupar_suma_indicadores_y_columnas(self):
        m = medida(["de", "r", "r"], [
            ["agrupar", [["tipo", ["campo", "r", "tipo"]]],
             [["activos", "suma", ["campo", "r", "activo"]]]],
            ["donde", [">", ["col", "activos"], 0]]],
            ["resumen", "contar", 1])
        resultado = evaluar(m, {"r": [{"tipo": "a", "activo": True},
                                      {"tipo": "a", "activo": False},
                                      {"tipo": "b", "activo": False}]})
        self.assertEqual(resultado["valor"], 1)
        self.assertEqual(resultado["testigos"], [{"tipo": "a", "activos": 1.0}])

    def test_agrupar_cero_agregados_deduplica(self):
        m = medida(["de", "r", "r"], [["agrupar", [["x", ["campo", "r", "x"]]], []]])
        self.assertEqual(evaluar(m, {"r": [{"x": 1}, {"x": 1}]})["valor"], 1)

    def test_producto_y_escalar(self):
        m = medida(["unir", ["de", "a", "x"], ["de", "b", "y"]],
                   [["donde", [">", ["doble", ["campo", "x", "n"]], ["campo", "y", "n"]]]])
        self.assertEqual(evaluar(m, {"a": [{"n": 2}], "b": [{"n": 1}, {"n": 5}]},
                                 {"doble": lambda n: n * 2})["valor"], 1)

    def test_error_unico_y_flotante(self):
        m = medida(["de", "r", "r"], umbral=["umbral", "==", 0.0, "", "contrato"])
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(m, {"r": []})
        m[4][3] = "razón"
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(m, {"r": []})
        m = medida(["de", "r", "r"], [["donde", ["==", ["campo", "r", "x"], 1.0]]])
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(m, {"r": [{"x": 1.0}]})
        m = medida(["de", "r", "r"], [["donde", ["mal", ["campo", "r", "x"]]]])
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(m, {"r": [{"x": 1.0}]}, {"mal": lambda x: 1 / 0})

    def test_logica_evalua_ambos_lados_y_ambito(self):
        m = medida(["de", "r", "r"],
                   [["donde", ["o", True, ["==", ["campo", "r", "ausente"], 1]]]])
        m.append(["ambito", "universal"])
        with self.assertRaises(ErrorDeAlgebra):
            evaluar(m, {"r": [{}]})


if __name__ == "__main__":
    unittest.main()
