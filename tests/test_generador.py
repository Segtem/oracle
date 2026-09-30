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

    def test_donde_las_reglas_no_pueden_la_busqueda_escribe_casos_con_su_polaridad(self):
        # Hasta 0.37.0 esto era «generación no posible»: la regla no sabe superar un `max`. La
        # búsqueda sube el valor de a un paso hasta que la medida y el mutante discrepan.
        medida = self.medida(10, agregado="max")
        with self.assertRaisesRegex(GeneracionNoPosible, "umbral <= 10"):
            fabricar_candidatos(medida)
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            (raiz / "catalogos" / "prueba.json").write_text(json.dumps(medida.a_datos()), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                codigo, resultado = generar_caso(Proyecto(raiz), "prueba.umbral")
            self.assertEqual(codigo, 0)
            self.assertTrue(resultado["casos"])
            from nucleo.caso import cargar_fuente_caso
            for ruta in resultado["casos"]:
                caso = cargar_fuente_caso(ruta)
                self.assertEqual(caso["procedencia"], "generada")
                self.assertEqual(medida.evaluar(caso["evidencia"]).ok, caso["etiqueta"] == "verde_correcto")

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
        self.assertEqual(cand["evidencia"], {"corrida": [], "problema": []})
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


class TestPiezasPuras(unittest.TestCase):
    def test_alt_val_da_otro_valor_del_mismo_tipo(self) -> None:
        from nucleo.generador import _alt_val
        for val in (True, False, 0, 7, -3, 0.0, 2.5, "", "x"):
            with self.subTest(val=val):
                otro = _alt_val(val)
                self.assertIs(type(otro), type(val))
                self.assertNotEqual(otro, val)
        self.assertEqual(_alt_val(None), "otro")

    def test_un_predicado_que_no_es_expresion_no_asigna_nada(self) -> None:
        self.assertEqual(resolver_predicado(True, True), {})
        self.assertEqual(resolver_predicado("x", False), {})

    def test_accesos_de_campo_por_alias(self) -> None:
        tuberia = ["desde", ["unir", ["de", "a", "x"], ["de", "b", "y"]],
                   ["donde", ["y", ["==", ["campo", "x", "f"], 1], ["==", ["campo", "z", "g"], 2]]],
                   ["agrupar", [], []]]
        self.assertEqual(extraer_accesos_campo(tuberia, ["resumen", "suma", ["campo", "y", "h"]]),
                         {"x": {"f"}, "y": {"h"}})

    def test_cada_comparador_resuelve_hacia_su_objetivo(self) -> None:
        import operator
        ops = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge,
               "==": operator.eq, "!=": operator.ne}
        for op, fn in ops.items():
            for val in (0, 5, -2, 0.0, 2.5, 1e300):
                for objetivo in (True, False):
                    with self.subTest(op=op, val=val, objetivo=objetivo):
                        v = resolver_predicado([op, ["campo", "a", "f"], val], objetivo)["a"]["f"]
                        self.assertIs(fn(v, val), objetivo)
                        self.assertIs(type(v), type(val))
                        # literal a la izquierda: `val op campo`
                        w = resolver_predicado([op, val, ["campo", "a", "f"]], objetivo)["a"]["f"]
                        self.assertIs(fn(val, w), objetivo)
                        # dos campos
                        par = resolver_predicado([op, ["campo", "a", "f"], ["campo", "b", "g"]], objetivo)
                        self.assertIs(fn(par["a"]["f"], par["b"]["g"]), objetivo)
                        # cerca(campo, blanco) op tolerancia
                        if op not in ("==", "!="):
                            c = resolver_predicado([op, ["cerca", ["campo", "a", "f"], val], 3], objetivo)
                            self.assertIs(fn(abs(c["a"]["f"] - val), 3), objetivo)

    def test_lo_que_no_se_sabe_ordenar_no_se_inventa(self) -> None:
        for val in ("texto", True, None):
            for op in ("<", "<=", ">", ">="):
                with self.subTest(op=op, val=val):
                    self.assertEqual(resolver_predicado([op, ["campo", "a", "f"], val], True), {})
        self.assertEqual(resolver_predicado(["==", ["campo", "a", "f"], "x"], True), {"a": {"f": "x"}})
        self.assertEqual(resolver_predicado(["<", ["mas", 1, 2], 5], True), {})
        self.assertEqual(resolver_predicado(["==", 1, 1], True), {})
        self.assertEqual(resolver_predicado(["contiene", ["campo", "a", "m"], "X"], True), {"a": {"m": "NO ve X"}})
        self.assertNotIn("X", resolver_predicado(["contiene", ["campo", "a", "m"], "X"], False)["a"]["m"])
        self.assertEqual(resolver_predicado(["==", ["cerca", ["campo", "a", "f"], 1], 3], True), {})

    def test_rellenar_defaults_por_nombre(self) -> None:
        from nucleo.generador import _rellenar_defaults
        campos = {"es_x", "y_ok", "z_valida", "conocido", "presente", "id", "rol", "fecha", "updated",
                  "fecha_en_nombre", "peso", "fijo"}
        self.assertEqual(_rellenar_defaults({"fijo": 7}, campos), {
            "es_x": True, "y_ok": True, "z_valida": True, "conocido": True, "presente": True,
            "id": "val_id", "rol": "val_rol", "fecha": "2026-08-26", "updated": "2026-08-26",
            "fecha_en_nombre": "2026-08-26", "peso": 0.0, "fijo": 7})


def _medida_de(texto: str) -> Medida:
    from nucleo.forma import datos_en_forma_unica
    return Medida.de_datos(datos_en_forma_unica(texto, "prueba"))


def _muertos(medida: Medida, casos: list) -> set[str]:
    from nucleo.mutacion import correr
    return {d["cambio"] for d in correr({medida.id: medida}, casos)["mutante"]
            if d["detecciones_conductuales"] or d["rechazos_del_algebra"]}


class TestRamasDeCandidatos(unittest.TestCase):
    """Las ramas de `_proponer_candidatos`: disyunción, join entre relaciones y auto-join."""

    def test_una_rama_por_disyuncion(self) -> None:
        medida = _medida_de(
            "medida prueba.dos.ramas:\n    de item x\n    donde x.a == 1 o x.b == 2\n    resumen contar(1)\n"
            "    umbral <= 0 segun contrato porque \"cero\"\n    ambito universal\n    alcance \"prueba\"\n")
        candidatos = fabricar_candidatos(medida)
        ids = [c["id"] for c in candidatos]
        self.assertEqual(ids[:2], ["prueba-gen-001-dos.ramas-rama1", "prueba-gen-002-dos.ramas-rama2"])
        for c in candidatos:
            self.assertEqual(medida.evaluar(c["evidencia"]).ok, c["etiqueta"] == "verde_correcto")
        # La rama 1 ofende sólo por `a` y la 2 sólo por `b`: cada una mata el mutante que la borra.
        ramas = {c["id"][-5:]: [f for f in c["evidencia"]["item"] if f["a"] == 1 or f["b"] == 2]
                 for c in candidatos[:2]}
        self.assertEqual([(f["a"] == 1, f["b"] == 2) for f in ramas["rama1"]], [(True, False)])
        self.assertEqual([(f["a"] == 1, f["b"] == 2) for f in ramas["rama2"]], [(False, True)])
        muertos = _muertos(medida, candidatos)
        self.assertIn("expresion:logico@2.2.1:o→y", muertos)
        self.assertIn("conservar_una_rama_de_disyuncion", muertos)

    def test_join_entre_relaciones_distintas(self) -> None:
        medida = _medida_de(
            "medida prueba.join:\n    de pedido p\n    unir cliente c\n"
            "    donde p.cliente == c.id y c.activo == false\n    resumen contar(1)\n"
            "    umbral <= 0 segun contrato porque \"cero\"\n    ambito universal\n    alcance \"prueba\"\n")
        candidatos = fabricar_candidatos(medida)
        rojo = candidatos[0]
        self.assertEqual(medida.evaluar(rojo["evidencia"]).valor, 1)
        self.assertEqual(rojo["evidencia"]["cliente"][0]["id"], rojo["evidencia"]["pedido"][0]["cliente"])
        self.assertEqual(len(rojo["evidencia"]["pedido"]), 2)   # la ofensora y la limpia
        self.assertEqual(len(rojo["evidencia"]["cliente"]), 1)  # sólo la ofensora
        for c in candidatos:
            self.assertEqual(medida.evaluar(c["evidencia"]).ok, c["etiqueta"] == "verde_correcto")
        self.assertIn("quitar_filtro", _muertos(medida, candidatos))

    def test_un_join_con_sin_trae_la_relacion_negada(self) -> None:
        medida = _medida_de(
            "medida prueba.vivo:\n    de corrida c\n    unir en_disco e\n"
            "    donde e.fixture == c.fixture y e.archivado == false\n"
            "    sin item i donde i.caso == c.caso y i.id == e.id\n    resumen contar(1)\n"
            "    umbral <= 0 segun contrato porque \"cero\"\n    requiere en_disco\n"
            "    ambito universal\n    alcance \"prueba\"\n")
        candidatos = fabricar_candidatos(medida)
        for c in candidatos:
            with self.subTest(candidato=c["id"]):
                self.assertEqual(set(c["evidencia"]), {"corrida", "en_disco", "item"})
                v = medida.evaluar(c["evidencia"])
                if c.get("espera"):
                    self.assertTrue(v.sin_evidencia)
                else:
                    self.assertEqual(v.ok, c["etiqueta"] == "verde_correcto")
        self.assertIn("quitar_antijunta", _muertos(medida, [c for c in candidatos if not c.get("espera")]))

    def test_auto_join_renombra_las_filas_limpias(self) -> None:
        medida = _medida_de(
            "medida prueba.duplicado:\n    de archivo a\n    unir archivo b\n"
            "    donde a.nombre == b.nombre y a.id != b.id\n    resumen contar(1)\n"
            "    umbral <= 0 segun contrato porque \"cero\"\n    ambito universal\n    alcance \"prueba\"\n")
        from nucleo.generador import _proponer_candidatos
        rojo = _proponer_candidatos(medida)[0]
        nombres = [f["nombre"] for f in rojo["evidencia"]["archivo"]]
        self.assertIn("nombre_limpio_0", nombres)
        self.assertEqual(medida.evaluar(rojo["evidencia"]).valor, 2)  # la ofensora, cruzada en los dos órdenes

    def test_un_nombre_fijado_por_el_donde_no_lleva_sufijo(self) -> None:
        medida = _medida_de(
            "medida prueba.nombres:\n    de item x\n    donde x.nombre == \"fijo\" y x.tipo == \"t\"\n"
            "    resumen contar(1)\n    umbral <= 0 segun contrato porque \"cero\"\n"
            "    ambito universal\n    alcance \"prueba\"\n")
        self.assertEqual(fabricar_filas(medida, satisfacer=True, sufijo="-s")["item"][0]["nombre"], "fijo")
        suelta = _medida_de(
            "medida prueba.suelta:\n    de item x\n    donde x.tipo == \"t\" y x.nombre != \"\"\n"
            "    resumen contar(1)\n    umbral <= 0 segun contrato porque \"cero\"\n"
            "    ambito universal\n    alcance \"prueba\"\n")
        fila = fabricar_filas(suelta, satisfacer=False, sufijo="-s")["item"][0]
        self.assertEqual(fila["nombre"], "algo")

    def test_el_titulo_por_omision(self) -> None:
        from nucleo.generador import construir_caso_final
        cand = {"id": "p-gen-001-x", "medida": "p.x", "etiqueta": "falso_verde", "evidencia": {"t": []}}
        self.assertEqual(construir_caso_final(cand, set())["titulo"], "Evidencia generada para fijar p.x")
        self.assertEqual(construir_caso_final({**cand, "titulo": "propio"}, set())["titulo"], "propio")


class TestGenerarCasoEnUnProyecto(unittest.TestCase):
    MEDIDA = ("medida prueba.x:\n    de item i\n    donde i.malo == true\n    resumen contar(1)\n"
              "    umbral <= 0 segun contrato porque \"cero\"\n    ambito universal\n    alcance \"prueba\"\n")

    def setUp(self) -> None:
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.raiz))
        (self.raiz / "oracle.json").write_text(
            '{"esquema": "oracle.proyecto/v1", "catalogo_base": false, "perfiles": []}\n', encoding="utf-8")
        (self.raiz / "catalogos" / "prueba").mkdir(parents=True)
        (self.raiz / "corpus" / "prueba").mkdir(parents=True)
        (self.raiz / "diferencial").mkdir()
        (self.raiz / "catalogos" / "prueba" / "prueba.x.oracle").write_text(self.MEDIDA, encoding="utf-8")

    def _generar(self, mid="prueba.x", **kw):
        with redirect_stdout(io.StringIO()) as salida:
            codigo, res = generar_caso(Proyecto(self.raiz), mid, **kw)
        return codigo, res, salida.getvalue()

    def test_una_medida_que_no_existe(self) -> None:
        codigo, res, texto = self._generar("prueba.no_existe")
        self.assertEqual((codigo, res), (1, {}))
        self.assertIn("medida «prueba.no_existe» no encontrada", texto)

    def test_escribe_en_el_grupo_y_despues_es_ruido(self) -> None:
        codigo, res, _ = self._generar()
        self.assertEqual(codigo, 0)
        self.assertTrue(res["casos"])
        self.assertTrue(all(r.parent == self.raiz / "corpus" / "prueba" for r in res["casos"]))
        self.assertEqual(res["siguen_vivos"], [])
        self.assertEqual(res["muertos_nuevos"], res["vivos_antes"])
        codigo, res, texto = self._generar()
        self.assertEqual((codigo, res), (0, {"mid": "prueba.x", "vivos_antes": 0, "muertos_nuevos": 0, "casos": []}))
        self.assertIn("ya está fijada", texto)

    def test_candidatos_que_no_matan_nada_no_se_escriben(self) -> None:
        from unittest import mock
        with mock.patch("nucleo.generador.evaluar_utilidad", return_value=(["quitar_filtro"], [])), \
                mock.patch("nucleo.generador.fabricar_candidatos", return_value=[]):
            codigo, res, texto = self._generar()
        self.assertEqual((codigo, res), (0, {"mid": "prueba.x", "vivos_antes": 1, "muertos_nuevos": 0, "casos": []}))
        self.assertIn("no mata ningún mutante adicional", texto)

    def test_la_generacion_imposible_dice_por_que(self) -> None:
        from unittest import mock
        with mock.patch("nucleo.generador.fabricar_candidatos", side_effect=GeneracionNoPosible("motivo")), \
                mock.patch("nucleo.generador._buscar", return_value=None):
            codigo, res, _ = self._generar()
        self.assertEqual(codigo, 1)
        self.assertEqual({k: v for k, v in res.items() if k != "vivos_antes"},
                         {"mid": "prueba.x", "muertos_nuevos": 0, "casos": [], "error": "motivo"})

    def test_los_fixtures_del_diferencial_cuentan_solo_si_cargan_bien(self) -> None:
        from unittest import mock
        from nucleo.forma import datos_en_forma_unica
        medida = Medida.de_datos(datos_en_forma_unica(self.MEDIDA, "prueba"))
        casos = [c for c in fabricar_candidatos(medida) if "espera" not in c]
        for fallas, fijada in (([], True), (["roto"], False)):
            with self.subTest(fallas=fallas), \
                    mock.patch("nucleo.fixtures.cargar_fixtures", return_value=(["f"], fallas)), \
                    mock.patch("nucleo.fixtures.casos_para_mutacion", return_value=casos):
                codigo, res, _ = self._generar(imprimir_solo=True)
            self.assertEqual(res["vivos_antes"] == 0, fijada, res)

    def test_sin_confianza_no_corre_las_escalares_del_proyecto(self) -> None:
        from nucleo.proyecto import EscalaresNoConfiables
        (self.raiz / "escalares.py").write_text("x = 1\n", encoding="utf-8")
        with self.assertRaises(EscalaresNoConfiables):
            self._generar()



if __name__ == "__main__":
    unittest.main()


class BusquedaTests(unittest.TestCase):
    """La búsqueda parte de evidencia que ya hay, la perturba y la encoge. Todo determinista."""

    medida = staticmethod(TestUmbralDeclarado.medida)

    def _mutante(self, medida, prefijo):
        from nucleo.mutacion import mutantes
        return next(Medida.de_datos(d) for n, d in mutantes(medida.a_datos()) if n.startswith(prefijo))

    def test_literales_sin_operadores_ni_nombres(self):
        from nucleo.generador import _literales
        arbol = ["desde", ["de", "paso", "p"],
                 ["donde", ["y", ["==", ["campo", "p", "op"], "agrupar"], [">", ["campo", "p", "a"], 3]]]]
        self.assertEqual(_literales([arbol, 3, True], []), ["agrupar", 3, True])

    def test_alternativas_por_tipo(self):
        from nucleo.generador import _alternativas
        self.assertEqual(_alternativas(True, {"b": True}, ["t", 4]), [False])
        self.assertEqual(_alternativas(2, {"a": 2, "b": 7, "c": "t", "d": True}, [4, 2.5, "t", True]),
                         [4, 2.5, 7, 3, 1, 0, -2, 5])
        self.assertEqual(_alternativas("a", {"x": "a", "y": "b", "n": 1}, ["c", 1]), ["c", "b", "", "a-otro"])
        self.assertEqual(_alternativas(None, {}, [1]), [])
        self.assertEqual(_alternativas(0.5, {}, [True, False]), [1.5, -0.5, 0, 2.0])   # -0.5 una sola vez

    def test_vecinos_cambian_un_campo_duplican_y_quitan(self):
        from nucleo.generador import _vecinos
        vecinos = list(_vecinos({"dato": [{"v": True}]}, []))
        self.assertEqual(vecinos, [{"dato": [{"v": False}]}, {"dato": [{"v": True}, {"v": True}]}, {"dato": []}])

    def test_separa_encuentra_encoge_y_es_determinista(self):
        from nucleo.generador import _buscar, _encoger, _separa, buscar_candidatos
        medida = self.medida(10, agregado="max")
        mutante = self._mutante(medida, "aflojar_umbral")
        semilla = {"dato": [{"valor": 1}, {"valor": 3}]}
        self.assertIsNone(_separa(medida, mutante, semilla))                 # los dos verdes
        self.assertIsNone(_buscar(medida, mutante, [semilla], [10], presupuesto=0))
        evidencia, ok = _buscar(medida, mutante, [semilla], [10], presupuesto=500)
        self.assertIs(ok, False)
        self.assertIs(_separa(medida, mutante, evidencia), False)
        chica = _encoger(medida, mutante, {"dato": [*evidencia["dato"], {"valor": 2}]}, ok)
        self.assertEqual(len(chica["dato"]), 1)
        self.assertIs(_separa(medida, mutante, chica), False)
        self.assertEqual(buscar_candidatos(medida, []), buscar_candidatos(medida, []))

    def test_separa_ignora_lo_que_no_evalua_o_no_tiene_evidencia(self):
        from nucleo.generador import _separa
        medida = self.medida(10, agregado="max", requiere=("dato",))
        mutante = self._mutante(medida, "aflojar_umbral")
        self.assertIsNone(_separa(medida, mutante, {"dato": []}))            # sin evidencia
        self.assertIsNone(_separa(medida, mutante, {"otra": [{"x": 1}]}))    # no evalúa
        self.assertIs(_separa(medida, mutante, {"dato": [{"valor": 11}]}), False)

    def test_encoger_simplifica_valores_y_conserva_el_veredicto(self):
        from nucleo.generador import _encoger
        medida = Medida.de_datos([
            "medida", "prueba.texto",
            ["desde", ["de", "dato", "x"], ["donde", ["==", ["campo", "x", "activo"], True]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "Contrato construido"],
            ["alcance", "Prueba construida"],
        ])
        mutante = self._mutante(medida, "aflojar_umbral")
        ev = {"dato": [{"activo": True, "nombre": "x", "peso": 3, "otro": False}]}
        self.assertEqual(_encoger(medida, mutante, ev, False),
                         {"dato": [{"activo": True, "nombre": "", "peso": 0, "otro": False}]})

    def test_la_busqueda_mata_lo_que_las_reglas_no_y_sin_repetir(self):
        from nucleo.generador import buscar_candidatos, evaluar_utilidad
        from nucleo.mutacion import correr, mutantes
        medida = self.medida(10, agregado="max")
        candidatos = buscar_candidatos(medida, [])
        buscados = [c for c in candidatos if c["id"].endswith("-buscado")]
        self.assertTrue(buscados)
        self.assertEqual([c["id"] for c in buscados],
                         [f"prueba-gen-2{i:02d}-umbral-buscado" for i in range(len(buscados))])
        for c in buscados:
            self.assertEqual(medida.evaluar(c["evidencia"]).ok, c["etiqueta"] == "verde_correcto")
        _, utiles = evaluar_utilidad(medida, [], candidatos, {medida.id: medida})
        self.assertEqual(len(utiles), len(buscados))                       # ninguno es ruido
        muertos = {d["cambio"] for d in correr({medida.id: medida}, candidatos)["mutante"]
                   if d["detecciones_conductuales"] or d["rechazos_del_algebra"]}
        self.assertGreater(len(muertos), 0)
        self.assertLessEqual(len(muertos), len(list(mutantes(medida.a_datos()))))

    def test_el_corpus_de_la_medida_es_semilla_y_sus_muertos_no_se_buscan(self):
        from nucleo.generador import buscar_candidatos
        medida = self.medida(10, agregado="max")
        todos = buscar_candidatos(medida, [])
        corpus = [{**c, "medida": medida.id} for c in todos]
        self.assertEqual([c for c in buscar_candidatos(medida, corpus) if c["id"].endswith("-buscado")], [])
