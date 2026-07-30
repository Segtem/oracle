"""Tests del modo simulación. Lo que más importa: que el contrato NO tenga conceptos de dominio y
que el determinismo se compruebe en vez de prometerse."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.simulacion import Corrida, SimuladorMalContratado, correr
from simuladores.cola import cola_simple
from simuladores.laberinto import agente_miope, resoluble

ESC = {"id": "e1"}


def _fijo(escenario, semilla, tope):
    return Corrida([{"t": 0, "actor": "a", "que": "x"}], pasos=1, razon="fin", resumen={"n": 1})


class ContratoTests(unittest.TestCase):
    def test_una_corrida_NO_tiene_campo_de_veredicto(self) -> None:
        """El contrato no puede traer «ganó»: si terminar así está bien lo dice una medida. La
        primera versión lo tenía y era un concepto de juego metido adentro del núcleo."""
        self.assertEqual(sorted(Corrida().__dataclass_fields__),
                         ["eventos", "pasos", "razon", "resumen"])

    def test_un_simulador_que_no_devuelve_Corrida_no_pasa(self) -> None:
        with self.assertRaises(SimuladorMalContratado):
            correr(lambda e, s, t: {"gano": True}, [ESC], [1])

    def test_un_evento_sin_t_o_sin_que_no_pasa(self) -> None:
        with self.assertRaises(SimuladorMalContratado):
            correr(lambda e, s, t: Corrida([{"actor": "a"}]), [ESC], [1])

    def test_la_traza_tiene_que_ser_L0_plana(self) -> None:
        with self.assertRaises(SimuladorMalContratado) as e:
            correr(lambda e, s, t: Corrida([{"t": 0, "que": "x", "lista": [1, 2]}]), [ESC], [1])
        self.assertIn("L0", str(e.exception))

    def test_el_resumen_tambien_tiene_que_ser_escalar(self) -> None:
        with self.assertRaises(SimuladorMalContratado):
            correr(lambda e, s, t: Corrida([], resumen={"x": {"anidado": 1}}), [ESC], [1])

    def test_el_resumen_de_dominio_se_copia_a_la_relacion_corrida(self) -> None:
        ev = correr(_fijo, [ESC], [1])
        self.assertEqual(ev["corrida"][0]["n"], 1)

    def test_produce_relaciones_y_no_veredictos(self) -> None:
        ev = correr(_fijo, [ESC], [1, 2])
        self.assertEqual(sorted(ev), ["corrida", "evento"])
        self.assertEqual(sorted(ev["corrida"][0]),
                         ["determinista", "escenario", "id", "n", "pasos", "razon", "semilla"])

    def test_sin_traza_no_emite_la_relacion_evento(self) -> None:
        self.assertEqual(sorted(correr(_fijo, [ESC], [1], con_traza=False)), ["corrida"])


class DeterminismoTests(unittest.TestCase):
    def test_el_runner_lo_COMPRUEBA_corriendo_dos_veces(self) -> None:
        llamadas = []

        def contando(escenario, semilla, tope):
            llamadas.append(semilla)
            return Corrida([{"t": 0, "actor": "a", "que": "x"}])

        correr(contando, [ESC], [7])
        self.assertEqual(llamadas, [7, 7])

    def test_un_simulador_que_ignora_la_semilla_sale_marcado(self) -> None:
        import itertools
        contador = itertools.count()

        def sin_semilla(escenario, semilla, tope):
            return Corrida([{"t": 0, "actor": "a", "que": f"azar:{next(contador)}"}])

        ev = correr(sin_semilla, [ESC], [1])
        self.assertFalse(ev["corrida"][0]["determinista"])

    def test_un_simulador_determinista_sale_marcado_como_tal(self) -> None:
        self.assertTrue(correr(_fijo, [ESC], [1])["corrida"][0]["determinista"])


class SimuladoresDeReferenciaTests(unittest.TestCase):
    def test_la_cola_es_determinista_y_reporta_sus_hechos(self) -> None:
        esc = {"id": "c", "servidores": 1, "capacidad": 4, "duracion": 30,
               "llega_cada": 2, "atiende_en": 3}
        for c in correr(cola_simple, [esc], [1, 2, 3], con_traza=False)["corrida"]:
            self.assertTrue(c["determinista"])
            self.assertIn(c["razon"], ("fin_de_ventana", "desborde"))
            self.assertGreaterEqual(c["cola_maxima"], 0)

    def test_una_cola_saturada_rechaza_y_una_holgada_no(self) -> None:
        sat = {"id": "s", "servidores": 1, "capacidad": 2, "duracion": 40,
               "llega_cada": 1, "atiende_en": 5}
        holg = {"id": "h", "servidores": 3, "capacidad": 8, "duracion": 40,
                "llega_cada": 3, "atiende_en": 2}
        razones = lambda e: {c["razon"] for c in                                  # noqa: E731
                            correr(cola_simple, [e], [1, 2, 3], con_traza=False)["corrida"]}
        self.assertEqual(razones(sat), {"desborde"})
        self.assertNotIn("desborde", razones(holg))

    def test_el_recorrido_no_alcanza_lo_que_el_BFS_declara_imposible(self) -> None:
        """La invariante de solidez: si no existe camino, nadie puede llegar. Al revés no vale, y
        justamente eso es lo que aporta la simulación."""
        tapiado = {"id": "t", "ancho": 5, "alto": 5, "muros": "3,4 4,3 3,3",
                   "inicio": "0,0", "meta": "4,4"}
        self.assertFalse(resoluble(tapiado))
        for c in correr(agente_miope, [tapiado], [1, 2, 3], tope=100, con_traza=False)["corrida"]:
            self.assertNotEqual(c["razon"], "meta")

    def test_existe_camino_y_el_presupuesto_igual_no_alcanza(self) -> None:
        """El desacuerdo que justifica esta mitad: un oráculo de propiedad daría verde."""
        duro = {"id": "d", "ancho": 9, "alto": 9,
                "muros": "5,5 8,3 5,8 6,5 0,5 5,7 8,5 3,3 5,2 2,3 0,7 6,7 6,4 2,1 2,4 4,4 1,3 "
                         "1,2 4,5 7,5 6,1",
                "inicio": "0,0", "meta": "8,8"}
        self.assertTrue(resoluble(duro))
        razones = {c["razon"] for c in
                   correr(agente_miope, [duro], [1, 2, 3], tope=40, con_traza=False)["corrida"]}
        self.assertEqual(razones, {"tope"})


if __name__ == "__main__":
    unittest.main()
