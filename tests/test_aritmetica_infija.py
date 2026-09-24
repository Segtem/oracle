"""La aritmética de superficie conserva los árboles de las escalares."""

import unittest

from nucleo.sintaxis import ErrorSintaxis, _leer_expr, imprimir, leer


class AritmeticaInfijaTests(unittest.TestCase):
    def test_precedencia_asociatividad_y_parentesis(self):
        casos = {
            "a + b * c": ["mas", ["col", "a"], ["por", ["col", "b"], ["col", "c"]]],
            "(a + b) * c": ["por", ["mas", ["col", "a"], ["col", "b"]], ["col", "c"]],
            "a - b + c": ["mas", ["menos", ["col", "a"], ["col", "b"]], ["col", "c"]],
            "a * b * c": ["por", ["por", ["col", "a"], ["col", "b"]], ["col", "c"]],
            "t2.turno == t1.turno + 1":
                ["==", ["campo", "t2", "turno"], ["mas", ["campo", "t1", "turno"], 1]],
            "no a + 1 == b y c":
                ["y", ["no", ["==", ["mas", ["col", "a"], 1], ["col", "b"]]],
                 ["col", "c"]],
        }
        for texto, esperado in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(_leer_expr(texto, 1, 1), esperado)

    def test_literales_negativos_y_resta(self):
        for texto, esperado in (
            ("-1", -1), ("-1.5e-2", -0.015),
            ("a - -1", ["menos", ["col", "a"], -1]),
            ("a + -1", ["mas", ["col", "a"], -1]),
            ("por(-2, 3)", ["por", -2, 3]),
        ):
            with self.subTest(texto=texto):
                self.assertEqual(_leer_expr(texto, 1, 1), esperado)
        for texto, esperado in (
            ("a-b", ["menos", ["col", "a"], ["col", "b"]]),
            ("turno-1", ["menos", ["col", "turno"], 1]),
            ("t1.turno-1", ["menos", ["campo", "t1", "turno"], 1]),
            ("a.x-a.y", ["menos", ["campo", "a", "x"], ["campo", "a", "y"]]),
        ):
            with self.subTest(texto=texto):
                self.assertEqual(_leer_expr(texto, 1, 1), esperado)

    def test_guion_en_nombre_de_campo_explica_la_resta(self):
        with self.assertRaises(ErrorSintaxis) as error:
            _leer_expr("a.-b", 1, 1)
        self.assertIn("guion", str(error.exception))
        self.assertIn("resta", str(error.exception))

    def test_ambas_formas_de_superficie_vuelven_al_mismo_arbol(self):
        prefijo = "medida demo.aritmetica:\n    de turno t\n    donde "
        sufijo = ('\n    resumen contar(1)\n'
                  '    umbral <= 0 segun convencion porque "regla"\n'
                  '    alcance "NO ve turnos ausentes"\n')
        infija = leer(prefijo + "t.turno + 1 == 2 * 3" + sufijo)
        funcional = leer(prefijo + "mas(t.turno, 1) == por(2, 3)" + sufijo)
        self.assertEqual(infija, funcional)
        impresa = imprimir(infija)
        self.assertEqual(leer(impresa), infija)
        self.assertIn("mas(t.turno, 1) == por(2, 3)", impresa)

    def test_operador_no_admitido_indica_la_alternativa(self):
        for operador in ("/", "%", "^"):
            with self.subTest(operador=operador), self.assertRaises(ErrorSintaxis) as error:
                _leer_expr(f"a {operador} b", 2, 4)
            self.assertEqual((error.exception.linea, error.exception.columna), (2, 6))
            self.assertIn(operador, str(error.exception))
            self.assertIn("escalar", str(error.exception))


if __name__ == "__main__":
    unittest.main()
