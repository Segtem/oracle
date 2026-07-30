"""Regresiones fail-closed de las herramientas de línea de comandos."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo.proyecto import sin_bandera
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

    def test_argumentos_sin_bandera_solo_quita_el_par_proyecto(self) -> None:
        self.assertEqual(
            sin_bandera(["--hechos", "--timeout", "0.001"]),
            ["--hechos", "--timeout", "0.001"])
        self.assertEqual(
            sin_bandera(["--proyecto", "/tmp/proyecto", "--hechos"]),
            ["--hechos"])

    def test_mutacion_con_baseline_timeout_emite_error_json_y_falla(self) -> None:
        r = subprocess.run(
            [sys.executable, str(RAIZ / "tools" / "mutar_codigo.py"),
             "--hechos", "--timeout", "0.001"],
            cwd=RAIZ, capture_output=True, text=True)

        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        datos = json.loads(r.stdout)
        self.assertEqual(datos["error_mutacion"][0]["tipo"], "LineaBaseFallida")
        self.assertIn("timeout", datos["error_mutacion"][0]["mensaje"])
        self.assertNotIn("Traceback", r.stdout + r.stderr)

    def _salida_mutacion_simulada(self, *, mutantes: int, errores: int, timeouts: int,
                                  equivalentes: list[dict] | None = None) -> int:
        from tools import mutar_codigo as cli

        evidencia = {
            "mutante": [],
            "mutante_equivalente": equivalentes or [],
            "corrida_mutacion": [{
                "id": "simulada",
                "mutantes": mutantes,
                "baseline_verde": True,
                "bytecode_frio": True,
                "tests_fallaron": 0,
                "errores_arnes": errores,
                "timeouts": timeouts,
            }],
        }
        with (mock.patch.object(cli, "correr", return_value=evidencia),
              mock.patch.object(cli.sys, "argv", ["mutar_codigo.py", "--hechos"]),
              redirect_stdout(io.StringIO())):
            return cli.main()

    def test_un_equivalente_inconcluso_no_puede_hacer_salir_cero(self) -> None:
        equivalente = [{
            "id": "m.py:1:8:constante", "estado": "timeout", "tests_fallaron": False,
            "error_arnes": False, "timeout": True,
        }]
        self.assertEqual(
            self._salida_mutacion_simulada(
                mutantes=1, errores=0, timeouts=1, equivalentes=equivalente),
            2)

    def test_una_ronda_sin_mutantes_es_inconclusa(self) -> None:
        self.assertEqual(
            self._salida_mutacion_simulada(mutantes=0, errores=0, timeouts=0),
            2)

    def test_equivalentes_json_rechaza_duplicados_razones_vacias_y_formato_roto(self) -> None:
        from tools import mutar_codigo as cli

        invalidos = (
            [{"id": "m:1", "razon": "una"}, {"id": "m:1", "razon": "otra"}],
            [{"id": "m:1", "razon": "  "}],
            {"id": "m:1", "razon": "no es una lista"},
        )
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "equivalentes.json"
            for datos in invalidos:
                with self.subTest(datos=datos):
                    ruta.write_text(json.dumps(datos), encoding="utf-8")
                    with self.assertRaises(cli.EquivalenteInvalido):
                        cli.cargar_equivalentes(ruta)

            ruta.write_text("{roto", encoding="utf-8")
            with self.assertRaises(cli.EquivalenteInvalido):
                cli.cargar_equivalentes(ruta)

            ruta.write_text(
                json.dumps([{"id": "m:1", "razon": "revisión individual"}]),
                encoding="utf-8")
            self.assertEqual(cli.cargar_equivalentes(ruta), {"m:1": "revisión individual"})


class RunnerMutacionTests(unittest.TestCase):
    def _correr(self, fuente: str | None):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            tests = raiz / "tests"
            tests.mkdir()
            (tests / "__init__.py").write_text("", encoding="utf-8")
            if fuente is not None:
                (tests / "test_ejemplo.py").write_text(fuente, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "ejecutar_suite_mutacion.py"),
                 "--inicio", "tests", "--tope", "."],
                cwd=raiz, capture_output=True, text=True)

    def test_un_fallo_o_excepcion_dentro_de_un_test_discrimina(self) -> None:
        fallo = self._correr(
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_falla(self): self.assertEqual(1, 2)\n")
        excepcion = self._correr(
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_error(self): raise RuntimeError('roto')\n")

        self.assertEqual(fallo.returncode, 1, fallo.stdout + fallo.stderr)
        self.assertEqual(excepcion.returncode, 1, excepcion.stdout + excepcion.stderr)

    def test_se_detiene_en_el_primer_fallo(self) -> None:
        r = self._correr(
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_a_falla(self): self.fail('discrimina')\n"
            "    def test_b_no_debe_correr(self): print('SEGUNDO_TEST_EJECUTADO')\n")

        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("SEGUNDO_TEST_EJECUTADO", r.stdout + r.stderr)

    def test_cero_tests_es_error_del_arnes(self) -> None:
        r = self._correr(None)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("cero tests", r.stdout + r.stderr)

    def test_system_exit_durante_descubrimiento_es_error_del_arnes(self) -> None:
        r = self._correr("raise SystemExit(1)\n")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("SystemExit", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
