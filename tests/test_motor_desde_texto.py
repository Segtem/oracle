"""Pruebas de Motor.desde_texto y exigencia de la forma única."""

import unittest

from nucleo.algebra import ErrorDeAlgebra, LimitesAlgebra, RegistroEscalares
from nucleo.macro import RegistroMacros, macros_base
from nucleo.sintaxis import imprimir


def setUpModule() -> None:
    global ErrorDeMotor, Motor
    from oracle_metalenguaje import ErrorDeMotor, Motor


MEDIDA_CANONICA = (
    "medida demo.valor:\n"
    "    de item i\n"
    "    resumen max(i.valor)\n"
    '    umbral <= 10 porque "el límite es parte del ejemplo verificable"\n'
    '    alcance "NO comprueba propiedades ajenas a valor"\n'
)

ARBOL_MEDIDA = [
    "medida", "demo.valor",
    ["desde", ["de", "item", "i"]],
    ["resumen", "max", ["campo", "i", "valor"]],
    ["umbral", "<=", 10, "el límite es parte del ejemplo verificable"],
    ["alcance", "NO comprueba propiedades ajenas a valor"],
]


class MotorDesdeTextoTests(unittest.TestCase):
    def test_carga_medida_canonica(self):
        motor = Motor.desde_texto([MEDIDA_CANONICA])
        self.assertEqual([m.id for m in motor.medidas], ["demo.valor"])
        self.assertIn("mas", motor.escalares)
        self.assertEqual(motor.limites, LimitesAlgebra())
        self.assertIsNone(motor.proyecto)

    def test_rechaza_doble_espacio(self):
        variante = MEDIDA_CANONICA.replace("medida demo.valor:", "medida  demo.valor:")
        with self.assertRaises(ErrorDeMotor) as ctx:
            Motor.desde_texto([variante])
        self.assertIn("fuera de la forma única", str(ctx.exception))
        self.assertIn("--- actual", str(ctx.exception))
        self.assertIn("+++ impresor", str(ctx.exception))

    def test_rechaza_crlf(self):
        variante = MEDIDA_CANONICA.replace("\n", "\r\n")
        with self.assertRaises(ErrorDeMotor) as ctx:
            Motor.desde_texto([variante])
        self.assertIn("fuera de la forma única", str(ctx.exception))
        self.assertIn("CRLF (\\r\\n)", str(ctx.exception))

    def test_rechaza_sin_salto_final(self):
        variante = MEDIDA_CANONICA.rstrip("\n")
        with self.assertRaises(ErrorDeMotor) as ctx:
            Motor.desde_texto([variante])
        self.assertIn("fuera de la forma única", str(ctx.exception))
        self.assertIn("sin salto final", str(ctx.exception))

    def test_rechaza_mas_a_b(self):
        texto_mas = (
            "medida demo.aritmetica:\n"
            "    de item i\n"
            "    donde mas(i.valor, 1) == 2\n"
            "    resumen contar(1)\n"
            '    umbral <= 0 porque "regla"\n'
            '    alcance "NO comprueba propiedades ajenas a valor"\n'
        )
        with self.assertRaises(ErrorDeMotor) as ctx:
            Motor.desde_texto([texto_mas])
        self.assertIn("escribí a + b", str(ctx.exception))

    def test_acepta_lineas_comentario(self):
        texto_con_comentarios = (
            "# Comentario de encabezado\n"
            "medida demo.valor:\n"
            "    # Comentario interno de paso\n"
            "    de item i\n"
            "    resumen max(i.valor)\n"
            '    umbral <= 10 porque "el límite es parte del ejemplo verificable"\n'
            '    alcance "NO comprueba propiedades ajenas a valor"\n'
            "# Comentario al pie\n"
        )
        motor = Motor.desde_texto([texto_con_comentarios])
        self.assertEqual([m.id for m in motor.medidas], ["demo.valor"])

    def test_la_medida_cargada_evalua_igual_que_desde_datos_con_el_mismo_arbol(self):
        motor_datos = Motor.desde_datos([ARBOL_MEDIDA])
        motor_texto = Motor.desde_texto([MEDIDA_CANONICA])
        self.assertEqual(imprimir(ARBOL_MEDIDA), MEDIDA_CANONICA)

        for evidencia in (
            {"item": [{"valor": 5}]},
            {"item": [{"valor": 10}]},
            {"item": [{"valor": 15}]},
        ):
            inf_datos = motor_datos.evaluar(evidencia)
            inf_texto = motor_texto.evaluar(evidencia)
            self.assertEqual(inf_datos.ok, inf_texto.ok)
            self.assertEqual(len(inf_datos.veredictos), len(inf_texto.veredictos))
            self.assertEqual(inf_datos.veredictos[0].valor, inf_texto.veredictos[0].valor)
            self.assertEqual(inf_datos.a_json(), inf_texto.a_json())

    def test_carga_medida_con_macro_estandar(self):
        texto_macro = (
            "ninguno demo.vacio:\n"
            "    de item i\n"
            "    donde i.valor > 10\n"
            '    umbral <= 0 segun contrato porque "sin items mayores a 10"\n'
            "    ambito universal\n"
            '    alcance "cuenta items mayores a 10"\n'
        )
        motor = Motor.desde_texto([texto_macro])
        self.assertEqual([m.id for m in motor.medidas], ["demo.vacio"])
        informe = motor.evaluar({"item": [{"valor": 5}]})
        self.assertTrue(informe.ok)

    def test_carga_defmacro_dinamica_y_medida_que_la_usa(self):
        macro_texto = (
            "defmacro mi_ninguno(id, relacion, alias, alcance):\n"
            "    medida $id:\n"
            "        de $relacion $alias\n"
            "        resumen contar(1)\n"
            '        umbral <= 0 porque "ninguno"\n'
            "        alcance $alcance\n"
        )
        medida_texto = (
            "mi_ninguno demo.custom:\n"
            "    de item i\n"
            '    alcance "solo item"\n'
        )
        motor = Motor.desde_texto([macro_texto, medida_texto])
        self.assertEqual([m.id for m in motor.medidas], ["demo.custom"])
        informe = motor.evaluar({"item": []})
        self.assertTrue(informe.ok)

    def test_la_macro_se_declara_antes_aunque_venga_despues_y_con_un_comentario_arriba(self):
        # Mutación: sin ordenar las macros primero, o sin saltear las líneas # al reconocer un
        # defmacro, la medida se leía antes que su macro y no cargaba.
        macro_texto = (
            "# una macro propia\n"
            "defmacro mi_ninguno(id, relacion, alias, alcance):\n"
            "    medida $id:\n"
            "        de $relacion $alias\n"
            "        resumen contar(1)\n"
            '        umbral <= 0 porque "ninguno"\n'
            "        alcance $alcance\n"
        )
        medida_texto = "mi_ninguno demo.custom:\n    de item i\n    alcance \"solo item\"\n"
        motor = Motor.desde_texto([medida_texto, macro_texto])
        self.assertEqual([m.id for m in motor.medidas], ["demo.custom"])

    def test_validaciones_de_entrada(self):
        with self.assertRaisesRegex(ErrorDeMotor, "iterable de cadenas"):
            Motor.desde_texto(MEDIDA_CANONICA)
        with self.assertRaisesRegex(ErrorDeMotor, "debe ser una cadena"):
            Motor.desde_texto([123])
        with self.assertRaisesRegex(ErrorDeMotor, "RegistroMacros"):
            Motor.desde_texto([MEDIDA_CANONICA], macros=object())
        with self.assertRaisesRegex(ErrorDeMotor, "repetidos"):
            Motor.desde_texto([MEDIDA_CANONICA, MEDIDA_CANONICA])
        with self.assertRaisesRegex(ErrorDeMotor, "RegistroEscalares"):
            Motor.desde_texto([MEDIDA_CANONICA], registro={})
        with self.assertRaisesRegex(ErrorDeAlgebra, "LimitesAlgebra"):
            Motor.desde_texto([MEDIDA_CANONICA], limites=object())
