"""Contrato del runner de simulación.

El simulador aporta hechos de dominio; los campos que identifican y certifican la corrida pertenecen
al runner. Una colisión no puede resolverse por orden de diccionarios porque permitiría falsificar,
entre otras cosas, el determinismo que el runner acaba de comprobar.
"""

from __future__ import annotations

import itertools
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.simulacion import Corrida, SimuladorMalContratado, correr


ESCENARIO = {"id": "e1"}


def _fijo(escenario, semilla, tope):
    return Corrida([{"t": 0, "actor": "a", "que": "empieza"}],
                   pasos=1, razon="fin", resumen={"cantidad": 3})


class ContratoDeCorridaTests(unittest.TestCase):
    def test_un_simulador_devuelve_Corrida(self) -> None:
        with self.assertRaises(SimuladorMalContratado):
            correr(lambda e, s, t: {"pasos": 0}, [ESCENARIO], [1])

    def test_pasos_es_entero_no_negativo_y_no_bool(self) -> None:
        for invalido in (True, -1, 1.5, "1", None):
            with self.subTest(pasos=invalido):
                with self.assertRaises(SimuladorMalContratado):
                    correr(lambda e, s, t, x=invalido: Corrida(pasos=x), [ESCENARIO], [1])

        self.assertEqual(correr(lambda e, s, t: Corrida(pasos=0), [ESCENARIO], [1])
                         ["corrida"][0]["pasos"], 0)

    def test_razon_es_texto(self) -> None:
        for invalida in (None, 1, False, []):
            with self.subTest(razon=invalida):
                with self.assertRaises(SimuladorMalContratado):
                    correr(lambda e, s, t, x=invalida: Corrida(razon=x), [ESCENARIO], [1])

    def test_evento_tiene_t_y_que_y_es_L0(self) -> None:
        for eventos in ([{"que": "x"}], [{"t": 0}], [{"t": 0, "que": "x", "lista": [1]}]):
            with self.subTest(eventos=eventos):
                with self.assertRaises(SimuladorMalContratado):
                    correr(lambda e, s, t, xs=eventos: Corrida(xs), [ESCENARIO], [1])

        with self.assertRaises(SimuladorMalContratado):
            correr(lambda e, s, t: Corrida(eventos=({"t": 0, "que": "x"},)),
                   [ESCENARIO], [1])

    def test_resumen_es_un_mapa_L0(self) -> None:
        for resumen in ([1], {"anidado": {"x": 1}}):
            with self.subTest(resumen=resumen):
                with self.assertRaises(SimuladorMalContratado):
                    correr(lambda e, s, t, x=resumen: Corrida(resumen=x), [ESCENARIO], [1])


class CamposCertificadosTests(unittest.TestCase):
    def test_resumen_no_puede_reemplazar_campos_de_corrida(self) -> None:
        valores = {
            "id": "forjada", "escenario": "otro", "semilla": 99, "pasos": 0,
            "razon": "completado", "determinista": True,
        }
        for campo, valor in valores.items():
            with self.subTest(campo=campo):
                with self.assertRaisesRegex(SimuladorMalContratado, "certificados"):
                    correr(lambda e, s, t, k=campo, v=valor: Corrida(
                        [{"t": 0, "que": "x"}], pasos=1, razon="tope", resumen={k: v}),
                        [ESCENARIO], [1])

    def test_regresion_un_simulador_no_puede_falsificar_determinismo(self) -> None:
        contador = itertools.count()

        def tramposo(escenario, semilla, tope):
            return Corrida([{"t": 0, "que": f"azar:{next(contador)}"}],
                           resumen={"determinista": True})

        with self.assertRaisesRegex(SimuladorMalContratado, "determinista"):
            correr(tramposo, [ESCENARIO], [1])

    def test_evento_no_puede_elegir_a_que_corrida_pertenece(self) -> None:
        def tramposo(escenario, semilla, tope):
            return Corrida([{"corrida": "otra·s9", "t": 0, "que": "x"}])

        with self.assertRaisesRegex(SimuladorMalContratado, "certificados"):
            correr(tramposo, [ESCENARIO], [1])

    def test_runner_asigna_ids_coherentes_a_corrida_y_eventos(self) -> None:
        evidencia = correr(_fijo, [ESCENARIO], [7])
        self.assertEqual(evidencia["corrida"][0]["id"], "e1·s7")
        self.assertEqual(evidencia["corrida"][0]["escenario"], "e1")
        self.assertEqual(evidencia["corrida"][0]["semilla"], 7)
        self.assertEqual({e["corrida"] for e in evidencia["evento"]}, {"e1·s7"})

    def test_ids_de_corrida_repetidos_se_rechazan(self) -> None:
        with self.assertRaisesRegex(SimuladorMalContratado, "repetido"):
            correr(_fijo, [{"id": "e1"}, {"id": "e1"}], [7])
        with self.assertRaisesRegex(SimuladorMalContratado, "repetido"):
            correr(_fijo, [ESCENARIO], [7, 7])


class EntradasDelRunnerTests(unittest.TestCase):
    def test_id_de_escenario_es_escalar_y_no_vacio(self) -> None:
        for invalido in ("", "   ", True, None, [], {}):
            with self.subTest(id=invalido):
                with self.assertRaises(SimuladorMalContratado):
                    correr(_fijo, [{"id": invalido}], [1])

    def test_escenario_sin_id_conserva_el_fallback_historico(self) -> None:
        self.assertEqual(correr(_fijo, [{}], [1])["corrida"][0]["id"], "?·s1")

    def test_semilla_es_entero_no_bool(self) -> None:
        for invalida in (True, 1.5, "1", None):
            with self.subTest(semilla=invalida):
                with self.assertRaises(SimuladorMalContratado):
                    correr(_fijo, [ESCENARIO], [invalida])

    def test_tope_es_entero_no_negativo_y_no_bool(self) -> None:
        for invalido in (True, -1, 1.5, "1", None):
            with self.subTest(tope=invalido):
                with self.assertRaises(SimuladorMalContratado):
                    correr(_fijo, [ESCENARIO], [1], tope=invalido)

        evidencia = correr(lambda e, s, t: Corrida(pasos=0), [ESCENARIO], [1], tope=0)
        self.assertEqual(evidencia["corrida"][0]["pasos"], 0)

    def test_el_tope_por_defecto_es_parte_del_contrato(self) -> None:
        recibidos = []

        def observa_tope(escenario, semilla, tope):
            recibidos.append(tope)
            return Corrida()

        evidencia = correr(observa_tope, [ESCENARIO], [1])
        self.assertEqual(recibidos, [500, 500])
        self.assertEqual(evidencia["corrida"][0]["pasos"], 0)

    def test_determinismo_se_comprueba_con_dos_ejecuciones(self) -> None:
        llamadas = []

        def contando(escenario, semilla, tope):
            llamadas.append((escenario["id"], semilla, tope))
            return Corrida([{"t": 0, "que": "x"}])

        evidencia = correr(contando, [ESCENARIO], [5], tope=8)
        self.assertEqual(llamadas, [("e1", 5, 8), ("e1", 5, 8)])
        self.assertTrue(evidencia["corrida"][0]["determinista"])

    def test_una_diferencia_real_en_la_traza_marca_no_determinismo(self) -> None:
        contador = itertools.count()

        def variable(escenario, semilla, tope):
            return Corrida([{"t": 0, "que": f"evento-{next(contador)}"}],
                           pasos=1, razon="fin")

        evidencia = correr(variable, [ESCENARIO], [1])
        self.assertFalse(evidencia["corrida"][0]["determinista"])

    def test_sin_traza_no_publica_la_relacion_evento(self) -> None:
        evidencia = correr(_fijo, [ESCENARIO], [1], con_traza=False)
        self.assertNotIn("evento", evidencia)


if __name__ == "__main__":
    unittest.main()
