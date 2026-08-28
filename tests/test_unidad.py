"""Tests unitarios exhaustivos para nucleo/unidad.py (Nivel L−1)."""

from __future__ import annotations

import unittest
from typing import Callable

from nucleo.algebra import COMPARADORES, RegistroEscalares, escalar
from nucleo.medida import Medida
from nucleo.relacion import Campo, Relacion
from nucleo.unidad import (
    RELACIONES_DE_UNIDAD,
    UNIDAD_ADIMENSIONAL,
    UNIDAD_NO_DERIVABLE,
    UNIDAD_SIN_UNIDAD,
    _PROCESO_RELACIONES,
    _columnas_de_agrupar,
    _extraer_comparaciones_de_expr,
    _extraer_comparaciones_de_paso,
    como_hechos,
    comparaciones_de_medida,
    derivar_unidad_comparacion,
    derivar_unidad_nodo,
    extraer_alias_de_fuente,
    hechos_de_unidades,
)


class UnidadTests(unittest.TestCase):
    def setUp(self):
        self.rel_pieza = Relacion(
            nombre="pieza",
            campos=(
                Campo("id", "texto", "sin_unidad"),
                Campo("ox", "flotante", "cm"),
                Campo("yaw", "flotante", "grados"),
            ),
            alcance="sensor pieza",
        )
        self.rel_objetivo = Relacion(
            nombre="objetivo",
            campos=(
                Campo("id", "texto", "sin_unidad"),
                Campo("distancia", "flotante", "cm"),
            ),
            alcance="sensor objetivo",
        )
        self.relaciones = {
            "pieza": self.rel_pieza,
            "objetivo": self.rel_objetivo,
        }
        self.registro = RegistroEscalares()

        @escalar(
            "desvio",
            "cm",
            unidades_argumentos=("sin_unidad", "cm"),
            registro=self.registro,
        )
        def desvio(p, g):
            return 0.0

        @escalar("desvio_sin_unidades_de_argumentos", "cm", registro=self.registro)
        def desvio_sin_unidades_de_argumentos(p, g):
            return 0.0

        @escalar(
            "opcional_con_unidad",
            "cm",
            unidades_argumentos=("cm",),
            registro=self.registro,
        )
        def opcional_con_unidad(grilla=10.0):
            return grilla

        @escalar("opcional_sin_unidad", "cm", registro=self.registro)
        def opcional_sin_unidad(grilla=10.0):
            return grilla

        @escalar("sin_unidad_fn", "", registro=self.registro)
        def sin_unidad_fn(p):
            return 0.0

        @escalar("espacios_fn", "   ", registro=self.registro)
        def espacios_fn(p):
            return 0.0

        @escalar("aritmetica", registro=self.registro)
        def aritmetica(a, b):
            return 0.0

        @escalar("unaria", registro=self.registro)
        def unaria(a):
            return 0.0

        self.rel_lenguaje = frozenset({"medida", "campo_declarado", "caso"})

    def test_constantes(self):
        self.assertEqual(RELACIONES_DE_UNIDAD, frozenset({"cantidad_comparada"}))
        self.assertEqual(UNIDAD_ADIMENSIONAL, "adimensional")
        self.assertEqual(UNIDAD_NO_DERIVABLE, "sin_declarar")
        self.assertEqual(UNIDAD_SIN_UNIDAD, "sin_unidad")
        self.assertIn("mutante", _PROCESO_RELACIONES)
        self.assertIn("alcanzable", _PROCESO_RELACIONES)
        self.assertIn("modulo", _PROCESO_RELACIONES)

    def test_extraer_alias_de_fuente(self):
        self.assertEqual(extraer_alias_de_fuente(None), {})
        self.assertEqual(extraer_alias_de_fuente([]), {})
        self.assertEqual(extraer_alias_de_fuente("no es lista"), {})
        self.assertEqual(extraer_alias_de_fuente(123), {})
        self.assertEqual(extraer_alias_de_fuente(["de", "pieza", "p"]), {"p": "pieza"})
        self.assertEqual(
            extraer_alias_de_fuente([
                "unir",
                ["de", "pieza", "a"],
                ["de", "objetivo", "b"],
            ]),
            {"a": "pieza", "b": "objetivo"},
        )
        self.assertEqual(extraer_alias_de_fuente(["otro", "pieza", "p"]), {})
        self.assertEqual(extraer_alias_de_fuente(["de", "pieza"]), {})
        self.assertEqual(extraer_alias_de_fuente(["de", "pieza", "p", "extra"]), {})
        self.assertEqual(extraer_alias_de_fuente(["de", 123, "p"]), {})
        self.assertEqual(extraer_alias_de_fuente(["de", "pieza", 123]), {})
        self.assertEqual(extraer_alias_de_fuente(["unir", ["de", "pieza", "a"]]), {})
        self.assertEqual(extraer_alias_de_fuente(["unir", ["de", "pieza", "a"], ["de", "objetivo", "b"], "extra"]), {})

    def test_derivar_unidad_nodo_campo(self):
        alias_map = {"a": "pieza", "m": "medida", "proc": "mutante", 1: "pieza", "desc": "desconocida"}

        # Campo con magnitud
        self.assertEqual(
            derivar_unidad_nodo(["campo", "a", "ox"], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "cm",
        )
        self.assertEqual(
            derivar_unidad_nodo(["campo", "a", "yaw"], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "grados",
        )
        self.assertEqual(
            derivar_unidad_nodo(["campo", "a", "id"], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "sin_unidad",
        )

        # Relación del lenguaje
        self.assertEqual(
            derivar_unidad_nodo(["campo", "m", "alcance"], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "sin_unidad",
        )

        # Relación de proceso
        self.assertEqual(
            derivar_unidad_nodo(["campo", "proc", "estado"], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "sin_unidad",
        )

        # Alias ausente
        self.assertIsNone(
            derivar_unidad_nodo(["campo", "z", "ox"], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )

        # Relación no declarada
        self.assertIsNone(
            derivar_unidad_nodo(["campo", "desc", "ox"], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )

        # Campo inexistente
        self.assertIsNone(
            derivar_unidad_nodo(["campo", "a", "no_existe"], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )

        # Longitud incorrecta o tipos no string
        self.assertIsNone(derivar_unidad_nodo(["campo", "a"], alias_map, self.relaciones, self.registro, self.rel_lenguaje))
        self.assertIsNone(derivar_unidad_nodo(["campo", "a", "ox", "extra"], alias_map, self.relaciones, self.registro, self.rel_lenguaje))
        self.assertIsNone(derivar_unidad_nodo(["campo", 1, "ox"], alias_map, self.relaciones, self.registro, self.rel_lenguaje))
        self.assertIsNone(derivar_unidad_nodo(["campo", "a", 123], alias_map, self.relaciones, self.registro, self.rel_lenguaje))

    def test_derivar_unidad_nodo_col(self):
        alias_map = {"a": "pieza"}
        cols = {"total": "adimensional", "longitud": "cm"}

        self.assertEqual(
            derivar_unidad_nodo(["col", "total"], alias_map, self.relaciones, self.registro, self.rel_lenguaje, cols),
            "adimensional",
        )
        self.assertEqual(
            derivar_unidad_nodo(["col", "longitud"], alias_map, self.relaciones, self.registro, self.rel_lenguaje, cols),
            "cm",
        )
        self.assertIsNone(
            derivar_unidad_nodo(["col", "no_esta"], alias_map, self.relaciones, self.registro, self.rel_lenguaje, cols)
        )
        self.assertIsNone(
            derivar_unidad_nodo(["col", "total"], alias_map, self.relaciones, self.registro, self.rel_lenguaje, None)
        )
        self.assertIsNone(
            derivar_unidad_nodo(["col"], alias_map, self.relaciones, self.registro, self.rel_lenguaje, cols)
        )
        self.assertIsNone(
            derivar_unidad_nodo(["col", "total", "extra"], alias_map, self.relaciones, self.registro, self.rel_lenguaje, cols)
        )
        self.assertIsNone(
            derivar_unidad_nodo(["col", 123], alias_map, self.relaciones, self.registro, self.rel_lenguaje, cols)
        )

    def test_derivar_unidad_nodo_resumen(self):
        alias_map = {"a": "pieza"}
        self.assertEqual(
            derivar_unidad_nodo(["resumen", "contar", 1], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "adimensional",
        )
        self.assertEqual(
            derivar_unidad_nodo(["resumen", "max", ["campo", "a", "ox"]], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "cm",
        )
        self.assertIsNone(
            derivar_unidad_nodo(["resumen", "max", 10], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )
        self.assertIsNone(
            derivar_unidad_nodo(["resumen", "max"], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )
        self.assertIsNone(
            derivar_unidad_nodo(["resumen", "max", ["campo", "a", "ox"], "extra"], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )

    def test_derivar_unidad_nodo_escalar(self):
        alias_map = {"a": "pieza"}
        # Escalar con unidad declarada
        self.assertEqual(
            derivar_unidad_nodo(["desvio", ["hecho", "a"], 10], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "cm",
        )
        self.assertEqual(
            derivar_unidad_nodo(
                ["desvio", ["hecho", "a"], ["campo", "a", "ox"]],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            ),
            "cm",
        )
        self.assertIsNone(
            derivar_unidad_nodo(
                ["desvio", ["hecho", "a"], ["campo", "a", "yaw"]],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            )
        )
        self.assertIsNone(
            derivar_unidad_nodo(
                ["desvio", ["campo", "a", "ox"], 10],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            )
        )
        self.assertIsNone(
            derivar_unidad_nodo(
                ["desvio_sin_unidades_de_argumentos", ["hecho", "a"], 10],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            )
        )
        self.assertEqual(
            derivar_unidad_nodo(
                ["opcional_con_unidad"],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            ),
            "cm",
        )
        self.assertIsNone(
            derivar_unidad_nodo(
                ["opcional_sin_unidad"],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            )
        )
        # Escalar sin unidad explícita pero con propagación aritmética
        # 1. arg1 con unidad, arg2 literal
        self.assertEqual(
            derivar_unidad_nodo(["aritmetica", ["campo", "a", "ox"], 10.0], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "cm",
        )
        # 2. arg2 con unidad, arg1 literal
        self.assertEqual(
            derivar_unidad_nodo(["aritmetica", 10.0, ["campo", "a", "ox"]], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "cm",
        )
        # 3. ambos con misma unidad
        self.assertEqual(
            derivar_unidad_nodo(["aritmetica", ["campo", "a", "ox"], ["campo", "a", "ox"]], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "cm",
        )
        # 4. adimensional y sin_unidad
        self.assertEqual(
            derivar_unidad_nodo(["aritmetica", ["resumen", "contar", 1], ["campo", "a", "id"]], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "sin_unidad",
        )
        self.assertEqual(
            derivar_unidad_nodo(["aritmetica", ["campo", "a", "id"], ["resumen", "contar", 1]], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            "sin_unidad",
        )
        # 5. unidades incompatibles
        self.assertIsNone(
            derivar_unidad_nodo(["aritmetica", ["campo", "a", "ox"], ["campo", "a", "yaw"]], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )
        # 6. unaria (len < 3)
        self.assertIsNone(
            derivar_unidad_nodo(["unaria", ["campo", "a", "ox"]], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )
        # 7. no registrada
        self.assertIsNone(
            derivar_unidad_nodo(["desconocida", 1, 2], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )
        # 8. vacía o espacios
        self.assertIsNone(
            derivar_unidad_nodo(["sin_unidad_fn", 1], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )
        self.assertIsNone(
            derivar_unidad_nodo(["espacios_fn", 1], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )
        # 9. argumentos no derivables
        self.assertIsNone(
            derivar_unidad_nodo(["aritmetica", ["campo", "a", "no_existe"], ["campo", "a", "ox"]], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )
        self.assertIsNone(
            derivar_unidad_nodo(["aritmetica", ["campo", "a", "ox"], ["campo", "a", "no_existe"]], alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        )

    def test_derivar_unidad_nodo_invalidos(self):
        alias_map = {"a": "pieza"}
        self.assertIsNone(derivar_unidad_nodo(None, alias_map, self.relaciones, self.registro, self.rel_lenguaje))
        self.assertIsNone(derivar_unidad_nodo([], alias_map, self.relaciones, self.registro, self.rel_lenguaje))
        self.assertIsNone(derivar_unidad_nodo("texto", alias_map, self.relaciones, self.registro, self.rel_lenguaje))
        self.assertIsNone(derivar_unidad_nodo(123, alias_map, self.relaciones, self.registro, self.rel_lenguaje))
        self.assertIsNone(derivar_unidad_nodo([123, "a"], alias_map, self.relaciones, self.registro, self.rel_lenguaje))

    def test_derivar_unidad_comparacion(self):
        alias_map = {"a": "pieza", "b": "objetivo"}

        # Ambos literales
        self.assertEqual(
            derivar_unidad_comparacion(1, 2, alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            (False, "sin_declarar"),
        )

        # Izquierda literal, derecha válida
        self.assertEqual(
            derivar_unidad_comparacion(0.0, ["campo", "a", "ox"], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            (True, "cm"),
        )
        # Izquierda literal, derecha no derivable
        self.assertEqual(
            derivar_unidad_comparacion(0.0, ["campo", "a", "no_existe"], alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            (False, "sin_declarar"),
        )

        # Derecha literal, izquierda válida
        self.assertEqual(
            derivar_unidad_comparacion(["campo", "a", "yaw"], 90.0, alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            (True, "grados"),
        )
        # Derecha literal, izquierda no derivable
        self.assertEqual(
            derivar_unidad_comparacion(["campo", "a", "no_existe"], 90.0, alias_map, self.relaciones, self.registro, self.rel_lenguaje),
            (False, "sin_declarar"),
        )

        # Dos no-literales misma unidad
        self.assertEqual(
            derivar_unidad_comparacion(
                ["campo", "a", "ox"],
                ["campo", "b", "distancia"],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            ),
            (True, "cm"),
        )

        # Uno adimensional, otro con unidad
        self.assertEqual(
            derivar_unidad_comparacion(
                ["resumen", "contar", 1],
                ["campo", "a", "ox"],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            ),
            (True, "cm"),
        )
        self.assertEqual(
            derivar_unidad_comparacion(
                ["campo", "a", "ox"],
                ["resumen", "contar", 1],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            ),
            (True, "cm"),
        )

        # Adimensional y no derivable
        self.assertEqual(
            derivar_unidad_comparacion(
                ["resumen", "contar", 1],
                ["campo", "a", "no_existe"],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            ),
            (False, "sin_declarar"),
        )
        self.assertEqual(
            derivar_unidad_comparacion(
                ["campo", "a", "no_existe"],
                ["resumen", "contar", 1],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            ),
            (False, "sin_declarar"),
        )

        # Incompatibles
        self.assertEqual(
            derivar_unidad_comparacion(
                ["campo", "a", "ox"],
                ["campo", "a", "yaw"],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            ),
            (False, "sin_declarar"),
        )

        # Uno o ambos None
        self.assertEqual(
            derivar_unidad_comparacion(
                ["campo", "a", "ox"],
                ["campo", "a", "no_existe"],
                alias_map,
                self.relaciones,
                self.registro,
                self.rel_lenguaje,
            ),
            (False, "sin_declarar"),
        )

    def test_extraer_comparaciones_de_expr(self):
        self.assertEqual(_extraer_comparaciones_de_expr(None), [])
        self.assertEqual(_extraer_comparaciones_de_expr([]), [])
        self.assertEqual(_extraer_comparaciones_de_expr(123), [])

        for op in COMPARADORES:
            expr = [op, ["campo", "a", "ox"], 10.0]
            self.assertEqual(_extraer_comparaciones_de_expr(expr), [(["campo", "a", "ox"], 10.0)])

        # Longitud incorrecta
        self.assertEqual(_extraer_comparaciones_de_expr(["<=", 1]), [])
        self.assertEqual(_extraer_comparaciones_de_expr(["<=", 1, 2, 3]), [])

        # Expresión anidada
        expr_anidada = [
            "y",
            ["==", ["campo", "a", "id"], "x"],
            ["o", [">", ["campo", "a", "ox"], 0.0], ["<", ["campo", "a", "yaw"], 180.0]],
        ]
        self.assertEqual(
            _extraer_comparaciones_de_expr(expr_anidada),
            [
                (["campo", "a", "id"], "x"),
                (["campo", "a", "ox"], 0.0),
                (["campo", "a", "yaw"], 180.0),
            ],
        )

    def test_columnas_de_agrupar(self):
        alias_map = {"a": "pieza"}
        self.assertEqual(_columnas_de_agrupar(None, alias_map, self.relaciones, self.registro, self.rel_lenguaje), {})
        self.assertEqual(_columnas_de_agrupar([], alias_map, self.relaciones, self.registro, self.rel_lenguaje), {})
        self.assertEqual(_columnas_de_agrupar(["donde", 1], alias_map, self.relaciones, self.registro, self.rel_lenguaje), {})
        self.assertEqual(_columnas_de_agrupar(["agrupar", 1], alias_map, self.relaciones, self.registro, self.rel_lenguaje), {})
        self.assertEqual(_columnas_de_agrupar(["agrupar", 1, 2, 3], alias_map, self.relaciones, self.registro, self.rel_lenguaje), {})

        paso = [
            "agrupar",
            [
                ["clave_id", ["campo", "a", "id"]],
                ["clave_ox", ["campo", "a", "ox"]],
                ["clave_no_der", ["campo", "a", "no_existe"]],
                ["invalido"],
                123,
                [123, "a"],
                [456, "b", "c"],
            ],
            [
                ["cnt", "contar", 1],
                ["sum_bool", "suma", ["==", ["campo", "a", "id"], "1"]],
                ["sum_ox", "suma", ["campo", "a", "ox"]],
                ["max_ox", "max", ["campo", "a", "ox"]],
                ["max_no_der", "max", ["campo", "a", "no_existe"]],
                ["invalido_agg"],
                456,
                [789, "contar", 1],
                [999, "b", "c"],
            ],
        ]
        cols = _columnas_de_agrupar(paso, alias_map, self.relaciones, self.registro, self.rel_lenguaje)
        self.assertEqual(cols["clave_id"], "sin_unidad")
        self.assertEqual(cols["clave_ox"], "cm")
        self.assertEqual(cols["clave_no_der"], "sin_unidad")
        self.assertEqual(cols["cnt"], "adimensional")
        self.assertEqual(cols["sum_bool"], "adimensional")
        self.assertEqual(cols["sum_ox"], "cm")
        self.assertEqual(cols["max_ox"], "cm")
        self.assertEqual(cols["max_no_der"], "sin_unidad")
        self.assertNotIn(123, cols)
        self.assertNotIn(456, cols)
        self.assertNotIn(789, cols)
        self.assertNotIn(999, cols)

    def test_extraer_comparaciones_de_paso(self):
        self.assertEqual(_extraer_comparaciones_de_paso(None), [])
        self.assertEqual(_extraer_comparaciones_de_paso([]), [])
        self.assertEqual(_extraer_comparaciones_de_paso("otro"), [])
        self.assertEqual(_extraer_comparaciones_de_paso(["donde"]), [])
        self.assertEqual(_extraer_comparaciones_de_paso(["donde", 1, 2]), [])
        self.assertEqual(_extraer_comparaciones_de_paso(["agrupar", 1]), [])
        self.assertEqual(_extraer_comparaciones_de_paso(["agrupar", 1, 2, 3]), [])
        self.assertEqual(_extraer_comparaciones_de_paso(["otro", 1]), [])

        paso_donde = ["donde", ["==", ["campo", "a", "id"], "x"]]
        self.assertEqual(
            _extraer_comparaciones_de_paso(paso_donde),
            [(["campo", "a", "id"], "x")],
        )

        paso_agrupar = [
            "agrupar",
            [["k", ["==", ["campo", "a", "id"], "1"]], ["k_inv"], 123],
            [["cnt", "contar", 1], ["max_diff", "max", [">", ["campo", "a", "ox"], 5.0]], ["a_inv"], 456],
        ]
        self.assertEqual(
            _extraer_comparaciones_de_paso(paso_agrupar),
            [
                (["campo", "a", "id"], "1"),
                (["campo", "a", "ox"], 5.0),
            ],
        )

    def test_comparaciones_de_medida_y_hechos(self):
        m1 = Medida(
            id="test.m1",
            tuberia=[
                "desde",
                ["de", "pieza", "a"],
                ["donde", ["<=", ["campo", "a", "ox"], 10.0]],
                [],
                "paso_no_lista",
            ],
            resumen=["resumen", "contar", 1],
            op="<=",
            limite=0,
            porque="defensa",
            alcance="alcance",
        )
        m2 = Medida(
            id="test.m2",
            tuberia=["desde", ["de", "pieza", "a"]],
            resumen=["resumen", "max", ["campo", "a", "ox"]],
            op="<=",
            limite=100.0,
            porque="defensa",
            alcance="alcance",
        )
        m_invalida_tuberia = Medida(
            id="test.minv",
            tuberia=123,  # type: ignore
            resumen=["resumen", "contar", 1],
            op="<=",
            limite=0,
            porque="defensa",
            alcance="alcance",
        )

        # Mapping de relaciones
        h_map = hechos_de_unidades([m1, m2], self.relaciones, self.registro)
        self.assertEqual(len(h_map["cantidad_comparada"]), 3)
        self.assertEqual(h_map["cantidad_comparada"][0], {"medida": "test.m1", "unidad": "adimensional", "es_derivable": True})
        self.assertEqual(h_map["cantidad_comparada"][1], {"medida": "test.m1", "unidad": "cm", "es_derivable": True})
        self.assertEqual(h_map["cantidad_comparada"][2], {"medida": "test.m2", "unidad": "cm", "es_derivable": True})

        # Iterable de relaciones y objetos no Relacion ignorados
        h_iter = hechos_de_unidades([m1], [self.rel_pieza, "no relacion"], self.registro)
        self.assertEqual(len(h_iter["cantidad_comparada"]), 2)

        # Relaciones None y registro None
        h_none = hechos_de_unidades([m1], None, None)
        self.assertEqual(len(h_none["cantidad_comparada"]), 2)

        # Tuberia no lista
        h_inv = hechos_de_unidades([m_invalida_tuberia], self.relaciones, self.registro)
        self.assertEqual(len(h_inv["cantidad_comparada"]), 1)

        # como_hechos
        self.assertEqual(como_hechos([m1], self.relaciones, self.registro), h_iter)

        # Tipo no Medida
        with self.assertRaises(ValueError):
            hechos_de_unidades(["no es Medida"])  # type: ignore


if __name__ == "__main__":
    unittest.main()
