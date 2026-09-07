"""La custodia del generador debe fallar ante una entrega contradictoria o ausente."""

import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from nucleo import generador
from tools import sondear_generador as sonda


class SondaDelGenerador(unittest.TestCase):
    def ejecutar(self, args=()):
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = sonda.main(list(args))
        return codigo, salida.getvalue()

    def test_las_sondas_fijan_los_bordes_publicados(self):
        medidas = sonda.sondas()
        self.assertEqual([(m.op, m.limite, m.resumen[1], debe) for m, debe in medidas], [
            ("<=", 5, "contar", True), ("<", 5, "contar", True),
            ("<=", 5.5, "contar", True), ("<=", 10, "max", False),
            ("<=", 90, "max", True),
        ])
        self.assertEqual(medidas[-1][0].id, "meta.ninguna_sombra_envejece_sin_revisarse")

    def test_el_generador_actual_cumple_las_17_comprobaciones(self):
        codigo, texto = self.ejecutar()
        self.assertEqual(codigo, 0)
        self.assertIn("17 comprobaciones", texto)
        self.assertIn("✓ meta.el_caso_se_pone_como_debe", texto)

    def test_los_hechos_son_datos_y_conservan_ambas_polaridades(self):
        codigo, texto = self.ejecutar(("--hechos",))
        filas = json.loads(texto)["caso"]
        self.assertEqual(codigo, 0)
        self.assertEqual(len(filas), 17)
        self.assertEqual({f["esperado_ok"] for f in filas}, {False, True})
        self.assertTrue(all(f["esperado_ok"] == f["dio_ok"] for f in filas))
        self.assertTrue(all(type(f["dio_ok"]) is bool for f in filas))

    def test_el_generador_anterior_da_cinco_discordancias(self):
        # La heurística anterior sigue existiendo, pero ya no se publica sin comprobarla.
        with patch.object(sonda, "fabricar_candidatos", generador._proponer_candidatos):
            codigo, texto = self.ejecutar(("--hechos",))
        discordantes = [f for f in json.loads(texto)["caso"] if f["esperado_ok"] != f["dio_ok"]]
        self.assertEqual(codigo, 1)
        self.assertEqual(len(discordantes), 5)
        self.assertIn("sonda-gen-001-conteo-inclusivo", [f["id"] for f in discordantes])

    def test_negarse_a_todo_no_es_cumplir_el_contrato(self):
        with patch.object(sonda, "fabricar_candidatos", side_effect=generador.GeneracionNoPosible("no")):
            codigo, texto = self.ejecutar(("--hechos",))
        filas = json.loads(texto)["caso"]
        self.assertEqual(codigo, 1)
        self.assertEqual(sum(f["esperado_ok"] != f["dio_ok"] for f in filas), 4)

    def test_una_lista_vacia_no_se_confunde_con_un_rechazo_explicito(self):
        with patch.object(sonda, "fabricar_candidatos", return_value=[]):
            codigo, texto = self.ejecutar(("--hechos",))
        filas = json.loads(texto)["caso"]
        self.assertEqual(codigo, 1)
        entrega = next(f for f in filas if f["id"] == "sonda.magnitud_insuficiente:entrega")
        self.assertFalse(entrega["esperado_ok"])
        self.assertTrue(entrega["dio_ok"])

    def test_entregar_solo_rojos_tampoco_alcanza(self):
        def solo_rojos(medida):
            return [c for c in generador.fabricar_candidatos(medida) if c["etiqueta"] == "falso_verde"]

        with patch.object(sonda, "fabricar_candidatos", solo_rojos):
            codigo, texto = self.ejecutar(("--hechos",))
        faltantes = [f for f in json.loads(texto)["caso"] if f["id"].endswith(":ambas_polaridades")]
        self.assertEqual(codigo, 1)
        self.assertTrue(all(not f["dio_ok"] for f in faltantes))

    def test_un_error_inesperado_no_se_convierte_en_negativa_valida(self):
        with patch.object(sonda, "fabricar_candidatos", side_effect=RuntimeError("defecto")):
            with self.assertRaisesRegex(RuntimeError, "defecto"):
                self.ejecutar()

    def test_sin_sondas_no_se_publica_un_verde_vacio(self):
        with patch.object(sonda, "sondas", return_value=[]):
            codigo, texto = self.ejecutar()
        self.assertEqual(codigo, 1)
        self.assertIn("GENERADOR NO COMPROBADO", texto)

    def test_la_entrada_real_lee_la_primera_opcion(self):
        salida = io.StringIO()
        with patch("sys.argv", ["sondear_generador.py", "--hechos"]), redirect_stdout(salida):
            codigo = sonda.main()
        self.assertEqual(codigo, 0)
        self.assertEqual(len(json.loads(salida.getvalue())["caso"]), 17)

    def test_evalua_filas_independientes_del_predicado_que_usa_la_heuristica(self):
        def entregar(medida):
            if medida.id == "sonda.magnitud_insuficiente":
                raise generador.GeneracionNoPosible("La sonda requiere negativa explícita")
            if medida.id == sonda.MID_SOMBRAS:
                return generador.fabricar_candidatos(medida)
            n = 5 if medida.id == "sonda.conteo_estricto" else 6
            return [
                {"id": medida.id + ":rojo", "etiqueta": "falso_verde",
                 "evidencia": {"dato": [{"valor": 1} for _ in range(n)]}},
                {"id": medida.id + ":verde", "etiqueta": "verde_correcto",
                 "evidencia": {"dato": [{"valor": 0}]}},
            ]

        # Un desplazamiento del filtro de > 0 a > 1 no puede esconderse detrás de un generador
        # que desplaza también sus filas. Acá el dato ofensivo es uno, fijado independientemente.
        with patch.object(sonda, "fabricar_candidatos", entregar):
            codigo, texto = self.ejecutar()
        self.assertEqual(codigo, 0, texto)
