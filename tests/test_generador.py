"""Pruebas para el generador automático de evidencia y casos."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import catalogos.escalares  # noqa: F401
from nucleo.algebra import ESCALARES
from nucleo.caso import leer as leer_caso, imprimir as imprimir_caso
from nucleo.generador import (
    extraer_accesos_campo,
    extraer_fuentes,
    fabricar_candidatos,
    fabricar_filas,
    generar_caso,
    resolver_predicado,
)
from nucleo.medida import Medida
from nucleo.proyecto import Proyecto, escalares_del_proyecto
from tools.corpus import revisar_evidencia


class TestGeneradorAST(unittest.TestCase):
    def test_extraer_fuentes_simple_y_compuesta(self):
        f_simple = ["de", "documento", "d"]
        self.assertEqual(extraer_fuentes(f_simple), [("documento", "d")])

        f_join = ["unir", ["de", "pieza", "a"], ["de", "objetivo", "b"]]
        self.assertEqual(extraer_fuentes(f_join), [("pieza", "a"), ("objetivo", "b")])

        f_triple = ["unir", ["de", "a", "x"], ["unir", ["de", "b", "y"], ["de", "c", "z"]]]
        self.assertEqual(extraer_fuentes(f_triple), [("a", "x"), ("b", "y"), ("c", "z")])

    def test_extraer_accesos_campo(self):
        tuberia = [
            "desde",
            ["de", "doc", "d"],
            ["donde", ["==", ["campo", "d", "carpeta_conocida"], False]],
            ["donde", ["!=", ["campo", "d", "area"], ["campo", "d", "carpeta"]]],
        ]
        resumen = ["resumen", "contar", 1]
        campos = extraer_accesos_campo(tuberia, resumen)
        self.assertEqual(campos, {"d": {"carpeta_conocida", "area", "carpeta"}})

    def test_resolver_predicado_comparadores(self):
        # == literal
        res_true = resolver_predicado(["==", ["campo", "d", "ok"], False], True)
        self.assertEqual(res_true, {"d": {"ok": False}})
        res_false = resolver_predicado(["==", ["campo", "d", "ok"], False], False)
        self.assertEqual(res_false, {"d": {"ok": True}})

        # != literal
        res_true_ne = resolver_predicado(["!=", ["campo", "d", "estado"], "activo"], True)
        self.assertEqual(res_true_ne, {"d": {"estado": ""}})
        res_false_ne = resolver_predicado(["!=", ["campo", "d", "estado"], "activo"], False)
        self.assertEqual(res_false_ne, {"d": {"estado": "activo"}})

        # < literal
        res_lt_true = resolver_predicado(["<", ["campo", "s", "fraccion"], 0.6], True)
        self.assertLess(res_lt_true["s"]["fraccion"], 0.6)
        res_lt_false = resolver_predicado(["<", ["campo", "s", "fraccion"], 0.6], False)
        self.assertGreaterEqual(res_lt_false["s"]["fraccion"], 0.6)

    def test_resolver_predicado_mismo_alias(self):
        # != entre campos del mismo alias
        pred = ["!=", ["campo", "d", "area"], ["campo", "d", "carpeta"]]
        res_true = resolver_predicado(pred, True)
        self.assertIn("area", res_true["d"])
        self.assertIn("carpeta", res_true["d"])
        self.assertNotEqual(res_true["d"]["area"], res_true["d"]["carpeta"])

        res_false = resolver_predicado(pred, False)
        self.assertEqual(res_false["d"]["area"], res_false["d"]["carpeta"])

    def test_resolver_predicado_logicos(self):
        pred_y = [
            "y",
            ["==", ["campo", "a", "x"], 1],
            ["==", ["campo", "a", "y"], 2],
        ]
        res_y_true = resolver_predicado(pred_y, True)
        self.assertEqual(res_y_true["a"]["x"], 1)
        self.assertEqual(res_y_true["a"]["y"], 2)

        pred_no = ["no", ["==", ["campo", "a", "activo"], True]]
        res_no_true = resolver_predicado(pred_no, True)
        self.assertEqual(res_no_true["a"]["activo"], False)


class TestFabricacionCasos(unittest.TestCase):
    def test_fabricar_candidatos_medida_simple(self):
        m = Medida.de_datos([
            "medida",
            "test.carpeta_conocida",
            ["desde", ["de", "documento", "d"], ["donde", ["==", ["campo", "d", "carpeta_conocida"], False]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "todas las carpetas deben ser conocidas"],
            ["alcance", "valida carpetas. NO ve documentos sueltos"],
        ])
        candidatos = fabricar_candidatos(m)
        self.assertGreaterEqual(len(candidatos), 2)
        cand_rojo = [c for c in candidatos if c["etiqueta"] == "falso_verde"][0]
        cand_verde = [c for c in candidatos if c["etiqueta"] == "verde_correcto"][0]

        # Veredicto de rojo debe ser False (ok == False)
        v_rojo = m.evaluar(cand_rojo["evidencia"])
        self.assertFalse(v_rojo.ok)

        # Veredicto de verde debe ser True (ok == True)
        v_verde = m.evaluar(cand_verde["evidencia"])
        self.assertTrue(v_verde.ok)

        # La evidencia debe cumplir L0 y ser válida
        self.assertEqual(revisar_evidencia("test-rojo", cand_rojo["evidencia"]), [])
        self.assertEqual(revisar_evidencia("test-verde", cand_verde["evidencia"]), [])

    def test_imprimir_y_leer_caso_generado(self):
        m = Medida.de_datos([
            "medida",
            "test.ejemplo",
            ["desde", ["de", "cosa", "c"], ["donde", ["==", ["campo", "c", "activo"], False]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "defensa del umbral"],
            ["alcance", "alcance de prueba"],
        ])
        candidatos = fabricar_candidatos(m)
        c = candidatos[0]
        caso_dict = {
            "id": c["id"],
            "fecha": "2026-08-26",
            "origen": {"repo": "oracle", "commit": "generado-por-oracle"},
            "titulo": c["titulo"],
            "etiqueta": c["etiqueta"],
            "sintoma": "Evidencia generada para prueba.",
            "como_se_detecto": "mutacion",
            "medida": m.id,
            "evidencia": c["evidencia"],
            "leccion": "Lección de prueba.",
        }
        texto = imprimir_caso(caso_dict)
        recuperado = leer_caso(texto)
        self.assertEqual(recuperado["id"], caso_dict["id"])
        self.assertEqual(recuperado["medida"], caso_dict["medida"])
        self.assertEqual(recuperado["etiqueta"], caso_dict["etiqueta"])


class TestGenerarComando(unittest.TestCase):
    def test_generar_en_medida_ya_fijada_es_ruido(self):
        proy = Proyecto(Path("."))
        rc, res = generar_caso(proy, "meta.sintaxis_cubre_algebra", imprimir_solo=True)
        self.assertEqual(rc, 0)
        self.assertEqual(res["vivos_antes"], 0)
        self.assertEqual(res["casos"], [])


if __name__ == "__main__":
    unittest.main()
