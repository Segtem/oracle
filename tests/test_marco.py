"""Política explícita de uso y fijación de las medidas."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402  registra las escalares del catálogo base
from nucleo.marco import hechos_de_casos, hechos_de_uso  # noqa: E402
from nucleo.medida import cargar  # noqa: E402


MID = "dominio.ordinaria"
CATALOGO = {MID: object()}
FIJADA = cargar(RAIZ / "catalogos" / "meta" / "meta.toda_medida_esta_fijada.json")


class _MedidaFalsa:
    """Stub mínimo: sólo lo que `hechos_de_casos` le pide a una medida real."""

    def __init__(self, ok: bool) -> None:
        self._ok = ok

    def evaluar(self, evidencia: dict) -> SimpleNamespace:
        return SimpleNamespace(ok=self._ok)


class HechosDeCasosTests(unittest.TestCase):
    def test_esperado_ok_compara_la_etiqueta_no_el_resultado(self) -> None:
        """Cuando la medida SÍ existe, `esperado_ok` tiene que salir de la etiqueta del caso —
        no del resultado de la medida, que es independiente y viene fijo en `True` acá."""
        catalogo = {"dominio.existe": _MedidaFalsa(True)}
        casos = [
            {"id": "coincide", "medida": "dominio.existe", "etiqueta": "verde_correcto",
             "evidencia": {}},
            {"id": "no_coincide", "medida": "dominio.existe", "etiqueta": "falso_verde",
             "evidencia": {}},
        ]
        filas = {f["id"]: f for f in hechos_de_casos(catalogo, casos)["caso"]}

        self.assertTrue(filas["coincide"]["esperado_ok"])
        self.assertTrue(filas["coincide"]["dio_ok"])
        self.assertFalse(filas["no_coincide"]["esperado_ok"])
        self.assertTrue(filas["no_coincide"]["dio_ok"])

    def test_distingue_sin_medida_id_desconocido_y_estado_del_hueco(self) -> None:
        casos = [
            {"id": "abierto", "medida": None, "etiqueta": "falso_verde",
             "estado_sin_medida": "abierto", "sin_medida_todavia": "falta una regla"},
            {"id": "desconocido", "medida": "dominio.no_existe",
             "etiqueta": "falso_verde"},
            {"id": "resuelto", "medida": None, "etiqueta": "deuda_de_diseño",
             "estado_sin_medida": "resuelto", "resuelto": "cerrado"},
        ]
        filas = {f["id"]: f for f in hechos_de_casos({}, casos)["caso"]}

        self.assertEqual(filas["abierto"]["medida"], "")
        self.assertFalse(filas["abierto"]["tiene_medida"])
        self.assertFalse(filas["abierto"]["medida_existe"])
        self.assertTrue(filas["abierto"]["es_hueco_abierto"])
        self.assertTrue(filas["abierto"]["explica_el_hueco"])

        self.assertTrue(filas["desconocido"]["tiene_medida"])
        self.assertFalse(filas["desconocido"]["medida_existe"])
        self.assertFalse(filas["desconocido"]["es_hueco_abierto"])
        self.assertFalse(filas["resuelto"]["es_hueco_abierto"])


class TodaMedidaEstaFijadaTests(unittest.TestCase):
    def _evaluar(self, mutantes=(), **politica):
        evidencia = hechos_de_uso(CATALOGO, [], list(mutantes), **politica)
        return evidencia["medida_en_uso"][0], FIJADA.evaluar(evidencia)

    def test_una_medida_ordinaria_con_CERO_mutantes_no_pasa_vacuamente(self) -> None:
        uso, veredicto = self._evaluar()
        self.assertFalse(uso["es_heredada"])
        self.assertEqual(uso["casos_que_la_evaluan"], 0)
        self.assertTrue(uso["debe_tener_mutantes"])
        self.assertFalse(veredicto.ok)

    def test_un_caso_que_reclama_la_medida_la_cuenta_exactamente_una_vez(self) -> None:
        evidencia = hechos_de_uso(CATALOGO, [{"medida": MID}], [])
        self.assertEqual(evidencia["medida_en_uso"][0]["casos_que_la_evaluan"], 1)

    def test_una_medida_con_un_mutante_vivo_no_esta_fijada(self) -> None:
        uso, veredicto = self._evaluar([{"apunta_a": MID, "murio": False}])
        self.assertEqual((uso["mutantes"], uso["mutantes_vivos"]), (1, 1))
        self.assertFalse(veredicto.ok)

    def test_una_medida_con_todos_sus_mutantes_muertos_esta_fijada(self) -> None:
        uso, veredicto = self._evaluar([
            {"apunta_a": MID, "murio": True},
            {"apunta_a": MID, "murio": True},
        ])
        self.assertEqual((uso["mutantes"], uso["mutantes_vivos"]), (2, 0))
        self.assertTrue(veredicto.ok)

    def test_una_medida_heredada_declara_que_no_debe_mutarse_en_esta_ronda(self) -> None:
        uso, veredicto = self._evaluar(heredadas={MID})
        self.assertTrue(uso["es_heredada"])
        self.assertFalse(uso["debe_tener_mutantes"])
        self.assertTrue(veredicto.ok)

    def test_una_medida_evaluada_aparte_declara_que_no_debe_mutarse(self) -> None:
        uso, veredicto = self._evaluar(evaluadas_aparte={MID})
        self.assertEqual(uso["casos_que_la_evaluan"], 1)
        self.assertFalse(uso["debe_tener_mutantes"])
        self.assertTrue(veredicto.ok)

    def test_un_mutante_sin_resultado_booleano_no_puede_contar_como_muerto(self) -> None:
        for mutante in ({"apunta_a": MID}, {"apunta_a": MID, "murio": "si"},
                        {"apunta_a": "otra.medida", "murio": True}, None):
            with self.subTest(mutante=mutante):
                with self.assertRaises(ValueError):
                    hechos_de_uso(CATALOGO, [], [mutante])


if __name__ == "__main__":
    unittest.main()
