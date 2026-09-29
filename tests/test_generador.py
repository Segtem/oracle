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


class TestMedidaConSin(unittest.TestCase):
    """Tarea caso-generar-no: una medida con `sin` necesita parejas en la relación negada."""

    TEXTO = (
        "medida prueba.avisa:\n"
        "    de corrida c\n"
        "    donde c.fixture == \"sin_clave\" y c.modo == \"normal\"\n"
        "    sin problema p donde p.caso == c.caso y p.nivel == \"WARNING\" y contiene(p.mensaje, \"SHALL\") "
        "y contiene(p.mensaje, \"MUST\")\n"
        "    resumen contar(1)\n"
        "    umbral <= 0 segun contrato porque \"cero\"\n"
        "    requiere corrida\n"
        "    ambito universal\n"
        "    alcance \"prueba\"\n"
    )

    def setUp(self) -> None:
        from nucleo.forma import datos_en_forma_unica
        self.medida = Medida.de_datos(datos_en_forma_unica(self.TEXTO, "prueba"))

    def test_cada_candidato_respeta_su_polaridad(self) -> None:
        candidatos = fabricar_candidatos(self.medida)
        etiquetas = {c["id"].rsplit("-", 1)[-1]: c for c in candidatos}
        self.assertIn("salvada", etiquetas)
        for c in candidatos:
            with self.subTest(candidato=c["id"]):
                v = self.medida.evaluar(c["evidencia"])
                if c.get("espera") == "sin_evidencia":
                    self.assertTrue(v.sin_evidencia)
                else:
                    self.assertEqual(v.ok, c["etiqueta"] == "verde_correcto")
                    self.assertEqual(revisar_evidencia(c["id"], c["evidencia"]), [])

    def test_la_pareja_copia_la_clave_real_y_junta_los_contiene(self) -> None:
        from nucleo.generador import salvar_con_parejas
        filas = fabricar_filas(self.medida, satisfacer=True)
        salvada = salvar_con_parejas(self.medida, filas)
        corrida, pareja = salvada["corrida"][0], salvada["problema"][0]
        self.assertEqual(pareja["caso"], corrida["caso"])
        self.assertIsInstance(corrida["caso"], str)
        self.assertEqual(pareja["nivel"], "WARNING")
        self.assertIn("SHALL", pareja["mensaje"])
        self.assertIn("MUST", pareja["mensaje"])
        self.assertNotIn("problema", filas, "salvar no toca la evidencia que recibe")

    def test_las_claves_son_unicas_entre_filas(self) -> None:
        a = fabricar_filas(self.medida, satisfacer=True)["corrida"][0]["caso"]
        b = fabricar_filas(self.medida, satisfacer=False)["corrida"][0]["caso"]
        self.assertNotEqual(a, b)

    def test_los_candidatos_matan_quitar_sin_filtro_y_requiere(self) -> None:
        from nucleo.mutacion import correr, mutantes
        candidatos = fabricar_candidatos(self.medida)
        informe = correr({self.medida.id: self.medida}, candidatos)
        muertos = {d["cambio"] for d in informe["mutante"]
                   if d["detecciones_conductuales"] or d["rechazos_del_algebra"]}
        for nombre in ("quitar_antijunta", "quitar_filtro", "quitar_requiere",
                       "quitar_requisitos_de_evidencia", "expresion:logico@2.2.1:y→o"):
            with self.subTest(mutante=nombre):
                self.assertIn(nombre, {n for n, _ in mutantes(self.medida.a_datos())})
                self.assertIn(nombre, muertos)

    def test_el_caso_sin_evidencia_lleva_su_espera(self) -> None:
        from nucleo.generador import construir_caso_final
        cand = next(c for c in fabricar_candidatos(self.medida) if c.get("espera"))
        self.assertEqual(cand["evidencia"], {"corrida": []})
        caso = construir_caso_final(cand, {"quitar_requiere"})
        self.assertEqual(caso["espera"], "sin_evidencia")
        self.assertNotIn("vacia", caso)
        self.assertEqual(leer_caso(imprimir_caso(caso))["espera"], "sin_evidencia")

    def test_un_requiere_que_no_protege_no_se_disfraza(self) -> None:
        from dataclasses import replace
        from unittest import mock
        original = Medida.evaluar

        def sin_proteccion(m, evidencia):
            v = original(m, evidencia)
            return replace(v, sin_evidencia=None) if v.sin_evidencia else v

        with mock.patch.object(Medida, "evaluar", sin_proteccion):
            with self.assertRaisesRegex(GeneracionNoPosible, "con «corrida» vacía la medida concluyó igual"):
                fabricar_candidatos(self.medida)


class TestFormasDelSin(unittest.TestCase):
    def test_igualdades_solo_con_la_fila_de_afuera(self) -> None:
        from nucleo.generador import _igualdades_con
        cond = ["y", ["==", ["campo", "p", "caso"], ["campo", "c", "caso"]],
                ["y", ["==", ["campo", "c", "id"], ["campo", "p", "item"]],
                 ["==", ["campo", "p", "a"], ["campo", "p", "b"]]],
                ["==", ["campo", "p", "nivel"], "ERROR"],
                ["==", "ERROR", ["campo", "p", "nivel"]],
                ["==", ["campo", "p", "codigo"], 1],
                ["!=", ["campo", "p", "x"], ["campo", "c", "x"]]]
        self.assertEqual(sorted(_igualdades_con(cond, "p")), [("caso", "c", "caso"), ("item", "c", "id")])
        self.assertEqual(sorted(_igualdades_con(cond, "c")), [("caso", "p", "caso"), ("id", "p", "item")])
        self.assertEqual(list(_igualdades_con("literal", "p")), [])

    def test_contiene_solo_literales_del_alias(self) -> None:
        from nucleo.generador import _campos_de, _contiene_de
        cond = ["y", ["contiene", ["campo", "p", "m"], "A"],
                ["y", ["contiene", ["campo", "p", "m"], "B"], ["contiene", ["campo", "c", "m"], "C"]],
                ["contiene", ["campo", "p", "n"], ["campo", "c", "k"]]]
        self.assertEqual(_contiene_de(cond, "p"), {"m": ["A", "B"]})
        self.assertEqual(_contiene_de(["contiene", ["campo", "p", "m"], "A"], "p"), {"m": ["A"]})
        self.assertEqual(_contiene_de("x", "p"), {})
        self.assertEqual(_campos_de(cond, "p"), {"m", "n"})
        self.assertEqual(_campos_de(cond, "c"), {"m", "k"})
        self.assertEqual(_campos_de(["campo", "c", "k"], "p"), set())

    def test_un_requiere_solo_condicional_no_fabrica_el_caso_vacio(self) -> None:
        from nucleo.forma import datos_en_forma_unica
        texto = TestMedidaConSin.TEXTO.replace(
            "    requiere corrida\n", "    requiere corrida c donde c.modo == \"normal\"\n")
        medida = Medida.de_datos(datos_en_forma_unica(texto, "prueba"))
        self.assertFalse(any(c.get("espera") for c in fabricar_candidatos(medida)))

    def test_la_utilidad_acepta_el_caso_vacio_solo_si_no_concluye(self) -> None:
        from nucleo.generador import evaluar_utilidad
        from nucleo.forma import datos_en_forma_unica
        medida = Medida.de_datos(datos_en_forma_unica(TestMedidaConSin.TEXTO, "prueba"))
        vacio = next(c for c in fabricar_candidatos(medida) if c.get("espera"))
        _, utiles = evaluar_utilidad(medida, [], [vacio], {medida.id: medida})
        self.assertEqual([c["id"] for c, _ in utiles], [vacio["id"]])
        self.assertIn("quitar_requiere", utiles[0][1])
        concluye = {**vacio, "evidencia": {"corrida": [{"fixture": "x", "modo": "x", "caso": "k"}],
                                           "problema": []}}
        self.assertEqual(evaluar_utilidad(medida, [], [concluye], {medida.id: medida})[1], [])

    def test_un_sin_como_primer_paso(self) -> None:
        from nucleo.forma import datos_en_forma_unica
        texto = TestMedidaConSin.TEXTO.replace(
            "    donde c.fixture == \"sin_clave\" y c.modo == \"normal\"\n", "")
        medida = Medida.de_datos(datos_en_forma_unica(texto, "prueba"))
        candidatos = fabricar_candidatos(medida)
        self.assertIn("salvada", {c["id"].rsplit("-", 1)[-1] for c in candidatos})
        verdes = [c for c in candidatos if c["etiqueta"] == "verde_correcto"]
        self.assertTrue(verdes)
        for c in verdes:
            self.assertIn("problema", c["evidencia"])
            self.assertTrue(medida.evaluar(c["evidencia"]).ok)

    def test_la_pareja_cumple_un_literal_que_va_primero(self) -> None:
        from nucleo.forma import datos_en_forma_unica
        from nucleo.generador import salvar_con_parejas
        texto = TestMedidaConSin.TEXTO.replace(
            "sin problema p donde p.caso == c.caso y p.nivel == \"WARNING\"",
            "sin problema p donde p.nivel == \"WARNING\" y p.caso == c.caso")
        medida = Medida.de_datos(datos_en_forma_unica(texto, "prueba"))
        pareja = salvar_con_parejas(medida, fabricar_filas(medida, satisfacer=True))["problema"][0]
        self.assertEqual(pareja["nivel"], "WARNING")

