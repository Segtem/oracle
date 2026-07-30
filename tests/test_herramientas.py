"""Regresiones fail-closed de las herramientas de línea de comandos."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.corpus import revisar_evidencia
from tools.diferencial import validar_fixture


RAIZ = Path(__file__).resolve().parents[1]


def _evidencia(valor=True):
    return {"hecho": [{"id": "h", "ok": valor}]}


def _dominio(**cambios):
    datos = {
        "origen": "referencia independiente",
        "dominio": "prueba",
        "medidas": ["prueba.mide"],
        "mundos": 2,
        "escenarios": [
            {"id": "verde", "evidencia": _evidencia(True), "referencia_ok": True},
            {"id": "rojo", "evidencia": _evidencia(False), "referencia_ok": False},
        ],
    }
    datos.update(cambios)
    return datos


class CorpusL0Tests(unittest.TestCase):
    def test_una_relacion_presente_puede_tener_cero_filas(self) -> None:
        self.assertEqual(revisar_evidencia("caso", {"relacion": []}), [])

    def test_el_mapa_de_evidencia_no_puede_estar_vacio(self) -> None:
        self.assertTrue(revisar_evidencia("caso", {}))


class ContratoDiferencialTests(unittest.TestCase):
    def test_un_fixture_de_dominio_completo_es_valido(self) -> None:
        self.assertEqual(validar_fixture(_dominio()), [])

    def test_una_relacion_vacia_tambien_es_L0_valida_en_un_fixture(self) -> None:
        datos = _dominio()
        for escenario in datos["escenarios"]:
            escenario["evidencia"] = {"hecho": []}
        self.assertEqual(validar_fixture(datos), [])

    def test_dominio_exige_contenido_consistencia_y_dos_polaridades(self) -> None:
        invalidos = (
            _dominio(medidas=[]),
            _dominio(escenarios=[], mundos=0),
            _dominio(mundos=99),
            _dominio(escenarios=[
                {"id": "a", "evidencia": _evidencia(), "referencia_ok": True},
                {"id": "b", "evidencia": _evidencia(), "referencia_ok": True},
            ]),
            _dominio(escenarios=[
                {"id": "", "evidencia": {}, "referencia_ok": "sí"},
                {"id": "b", "evidencia": _evidencia(), "referencia_ok": False},
            ]),
        )
        for datos in invalidos:
            with self.subTest(datos=datos):
                self.assertTrue(validar_fixture(datos))

    def test_formato_grupos_exige_grupos_casos_y_campos_basicos(self) -> None:
        valido = {
            "origen": "referencia independiente",
            "mundos": 2,
            "grupos": {
                "prueba.mide": [
                    {"evidencia": _evidencia(True), "esperado_ok": True},
                    {"evidencia": _evidencia(False), "esperado_ok": False},
                ],
            },
        }
        self.assertEqual(validar_fixture(valido), [])

        for datos in (
            {**valido, "grupos": {}},
            {**valido, "grupos": {"prueba.mide": []}},
            {**valido, "grupos": {"prueba.mide": [{"evidencia": _evidencia()}]}},
            {**valido, "mundos": 3},
            {**valido, "grupos": {"id con espacios": valido["grupos"]["prueba.mide"]}},
            {**valido, "grupos": {"prueba.mide": [
                {"evidencia": _evidencia(), "esperado_ok": True},
                {"evidencia": _evidencia(), "esperado_ok": True},
            ]}},
        ):
            with self.subTest(datos=datos):
                self.assertTrue(validar_fixture(datos))

    def test_en_grupos_mundos_es_el_largo_de_cada_grupo_no_la_suma(self) -> None:
        casos = [
            {"evidencia": _evidencia(True), "esperado_ok": True},
            {"evidencia": _evidencia(False), "esperado_ok": False},
        ]
        historico = {
            "origen": "fixture histórico",
            "mundos": 2,
            "grupos": {"a.mide": casos, "b.mide": list(casos)},
        }
        self.assertEqual(validar_fixture(historico), [])


class HerramientasCLITests(unittest.TestCase):
    def _proyecto(self, raiz: Path) -> None:
        (raiz / "catalogos").mkdir()

    def test_aceptacion_sin_casos_es_no_aplicable_y_falla(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proyecto = Path(td)
            self._proyecto(proyecto)
            r = subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "aceptacion.py"),
                 "--proyecto", str(proyecto)],
                cwd=RAIZ, capture_output=True, text=True)

        salida = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("SIN CASOS", salida)
        self.assertNotIn("ACEPTACIÓN ✓", salida)

    def test_fixture_malformado_falla_sin_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proyecto = Path(td)
            self._proyecto(proyecto)
            diferencial = proyecto / "diferencial"
            diferencial.mkdir()
            (diferencial / "roto.json").write_text(json.dumps({}), encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "diferencial.py"),
                 "--proyecto", str(proyecto)],
                cwd=RAIZ, capture_output=True, text=True)

        salida = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("DIFERENCIAL ✗", salida)
        self.assertNotIn("Traceback", salida)


if __name__ == "__main__":
    unittest.main()
