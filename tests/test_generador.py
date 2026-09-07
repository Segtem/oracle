"""Pruebas para el generador automático de evidencia y casos."""

from __future__ import annotations

import tempfile
import unittest
import io
import json
from contextlib import redirect_stdout
from unittest.mock import patch
from pathlib import Path

import catalogos.escalares  # noqa: F401
from nucleo.algebra import ESCALARES, LimitesAlgebra
from nucleo.caso import leer as leer_caso, imprimir as imprimir_caso
from nucleo.generador import (
    extraer_accesos_campo,
    extraer_fuentes,
    fabricar_candidatos,
    GeneracionNoPosible,
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


class TestUmbralDeclarado(unittest.TestCase):
    @staticmethod
    def medida(limite=5, op="<=", agregado="contar", pasos=(), requiere=()):
        return Medida.de_datos([
            "medida", "prueba.umbral",
            ["desde", ["de", "dato", "x"],
             ["donde", [">", ["campo", "x", "valor"], 0]], *pasos],
            ["resumen", agregado, 1 if agregado == "contar" else ["campo", "x", "valor"]],
            ["umbral", op, limite, "Contrato construido para ejercer el umbral"],
            ["requiere", *requiere],
            ["alcance", "Prueba construida; no afirma nada sobre un dominio real"],
        ])

    def test_el_rojo_supera_el_limite_real_del_conteo(self):
        for op, limite, primer_rojo in (("<=", 0, 1), ("<=", 5, 6), ("<", 5, 5),
                                       ("<=", 5.5, 6), ("<", 5.5, 6)):
            with self.subTest(op=op, limite=limite):
                medida = self.medida(limite, op)
                candidatos = fabricar_candidatos(medida)
                for candidato in candidatos:
                    v = medida.evaluar(candidato["evidencia"])
                    self.assertEqual(v.ok, candidato["etiqueta"] == "verde_correcto")
                    self.assertEqual(revisar_evidencia(candidato["id"], candidato["evidencia"]), [])
                    if not v.ok:
                        self.assertEqual(v.valor, primer_rojo)

    def test_el_conteo_no_se_convierte_en_existencia(self):
        from nucleo.mutacion import mutantes
        medida = self.medida()
        rojo = fabricar_candidatos(medida)[0]
        mutado = next(datos for nombre, datos in mutantes(medida.a_datos())
                      if nombre == "convertir_conteo_en_existencia")
        self.assertFalse(medida.evaluar(rojo["evidencia"]).ok)
        self.assertTrue(Medida.de_datos(mutado).evaluar(rojo["evidencia"]).ok)

    def test_un_maximo_que_no_alcanza_no_se_disfraza_de_rojo(self):
        with self.assertRaisesRegex(GeneracionNoPosible, r"max y umbral <= 10.*valor 1"):
            fabricar_candidatos(self.medida(10, agregado="max"))

    def test_una_magnitud_que_si_discrimina_se_conserva(self):
        medida = self.medida(.5, agregado="max")
        candidatos = fabricar_candidatos(medida)
        self.assertEqual([medida.evaluar(c["evidencia"]).ok for c in candidatos], [False, True])

    def test_sin_evidencia_no_es_un_defecto_demostrado(self):
        with self.assertRaisesRegex(GeneracionNoPosible, "relación requerida otra"):
            fabricar_candidatos(self.medida(0, requiere=("otra",)))

    def test_el_presupuesto_se_comprueba_antes_de_multiplicar_filas(self):
        with self.assertRaisesRegex(GeneracionNoPosible, "presupuesto de 100000 filas"):
            fabricar_candidatos(self.medida(10**20))

    def test_se_admite_exactamente_el_presupuesto_de_filas(self):
        with patch("nucleo.generador.LimitesAlgebra",
                   return_value=LimitesAlgebra(filas_por_relacion=4)):
            rojo = fabricar_candidatos(self.medida(1))[0]
        self.assertEqual(len(rojo["evidencia"]["dato"]), 4)
        self.assertEqual(self.medida(1).evaluar(rojo["evidencia"]).valor, 2)

    def test_cero_filas_ofensoras_no_se_puede_amplificar(self):
        datos = self.medida().a_datos()
        datos[2].append(["donde", ["<", ["campo", "x", "valor"], 0]])
        with self.assertRaisesRegex(GeneracionNoPosible, "evidencia propuesta da valor 0"):
            fabricar_candidatos(Medida.de_datos(datos))

    def test_no_se_omite_el_primer_paso_al_descartar_agrupaciones(self):
        datos = self.medida(1).a_datos()
        datos[2] = ["desde", ["de", "dato", "x"],
                    ["agrupar", [], [["cantidad", "contar", 1]]],
                    ["donde", ["<=", ["col", "cantidad"], 2]]]
        # Repetir las filas haría desaparecer el grupo. La negativa debe describir la propuesta
        # original (un grupo), sin tratarla como si el conteo fuera lineal en las filas de entrada.
        with self.assertRaisesRegex(GeneracionNoPosible, "evidencia propuesta da valor 1"):
            fabricar_candidatos(Medida.de_datos(datos))

    def test_agrupar_no_se_extrapola_como_si_contara_filas(self):
        agrupar = ["agrupar", [], [["cantidad", "contar", 1]]]
        with self.assertRaisesRegex(GeneracionNoPosible, "no se pudo fabricar falso_verde"):
            fabricar_candidatos(self.medida(pasos=(agrupar,)))

    def test_un_error_de_evaluacion_explica_la_negativa(self):
        with self.assertRaisesRegex(GeneracionNoPosible, "no se pudo evaluar el candidato"):
            fabricar_candidatos(self.medida("cinco"))

    def test_tambien_se_comprueba_el_candidato_verde(self):
        with self.assertRaisesRegex(GeneracionNoPosible, "no se pudo fabricar verde_correcto"):
            fabricar_candidatos(self.medida(5, op=">="))

    def test_el_comando_rechaza_sin_escribir_y_explica_el_umbral(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            (raiz / "catalogos" / "prueba.json").write_text(
                json.dumps(self.medida(10, agregado="max").a_datos()), encoding="utf-8")
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo, resultado = generar_caso(Proyecto(raiz), "prueba.umbral")
            self.assertEqual(codigo, 1)
            self.assertEqual(resultado["casos"], [])
            self.assertIn("umbral <= 10", resultado["error"])
            self.assertIn("generación no posible", salida.getvalue())
            self.assertFalse((raiz / "corpus").exists())

    def test_el_comando_escribe_solo_casos_con_polaridad_correcta(self):
        medida = self.medida()
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            (raiz / "catalogos" / "prueba.json").write_text(
                json.dumps(medida.a_datos()), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                codigo, resultado = generar_caso(Proyecto(raiz), "prueba.umbral")
            self.assertEqual(codigo, 0)
            self.assertGreater(resultado["muertos_nuevos"], 0)
            self.assertTrue(resultado["casos"])
            for ruta in resultado["casos"]:
                caso = leer_caso(ruta.read_text())
                self.assertEqual(medida.evaluar(caso["evidencia"]).ok,
                                 caso["etiqueta"] == "verde_correcto")


if __name__ == "__main__":
    unittest.main()
