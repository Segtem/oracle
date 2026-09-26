"""El resultado ausente es una expectativa distinta de un rojo medido."""
import unittest

from nucleo import caso
from tools.aceptacion import _resultado_esperado


class SinEvidenciaEsperadaTests(unittest.TestCase):
    def test_declara_ausencia_y_la_conserva_en_ida_y_vuelta(self):
        datos = {"id": "001-ausente", "fecha": "2026-09-25", "origen": {"repo": "p"},
                 "titulo": "t", "etiqueta": "falso_verde", "espera": "sin_evidencia",
                 "sintoma": "s", "como_se_detecto": "persona", "medida": "d.m",
                 "evidencia": {"item": []}, "leccion": "l"}
        texto = caso.imprimir(datos)
        self.assertIn("etiqueta: falso_verde\n    espera: sin_evidencia\n", texto)
        self.assertEqual(caso.leer(texto), datos)
        self.assertEqual(_resultado_esperado(datos, ok=False, sin_evidencia="item"), None)

    def test_ausencia_declarada_rechaza_rojo_medido_y_verde(self):
        datos = {"etiqueta": "falso_verde", "espera": "sin_evidencia"}
        self.assertIsNotNone(_resultado_esperado(datos, ok=False, sin_evidencia=""))
        self.assertIsNotNone(_resultado_esperado(datos, ok=True, sin_evidencia=""))

    def test_defecto_sin_campo_rechaza_ausencia_con_mensaje(self):
        error = _resultado_esperado({"etiqueta": "falso_verde"}, ok=False,
                                    sin_evidencia="item")
        self.assertIn("salió SIN EVIDENCIA; si es lo que el caso prueba, declaralo con espera: sin_evidencia", error)

    def test_campo_invalido_o_verde_correcto_se_rechaza(self):
        datos = {"id": "001-ausente", "fecha": "2026-09-25", "origen": {"repo": "p"},
                 "titulo": "t", "etiqueta": "falso_verde", "espera": "rojo",
                 "sintoma": "s", "como_se_detecto": "persona", "medida": "d.m",
                 "evidencia": {"item": []}, "leccion": "l"}
        with self.assertRaisesRegex(caso.CasoMalDeclarado, "espera"):
            caso.imprimir(datos)
        datos["espera"] = "sin_evidencia"
        datos["etiqueta"] = "verde_correcto"
        with self.assertRaisesRegex(caso.CasoMalDeclarado, "verde_correcto"):
            caso.imprimir(datos)
