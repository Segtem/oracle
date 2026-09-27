"""Pruebas unitarias para el rastreador y protocolo de cobertura en ejecutar_suite_mutacion."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import ejecutar_suite_mutacion as runner
from tools.ejecutar_suite_mutacion import (
    _RastreadorCobertura,
    _correr_suite,
    main,
)


class RastreadorCoberturaInicializacionTests(unittest.TestCase):
    def test_descubrimiento_por_omision_filtra_directorios_excluidos(self):
        with tempfile.TemporaryDirectory() as d:
            tope = Path(d).resolve()
            (tope / "modulo.py").write_text("x = 1\n", encoding="utf-8")
            sub = tope / "sub"
            sub.mkdir()
            (sub / "otro.py").write_text("y = 2\n", encoding="utf-8")
            tests_dir = tope / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_algo.py").write_text("pass\n", encoding="utf-8")
            git_dir = tope / ".git"
            git_dir.mkdir()
            (git_dir / "config.py").write_text("pass\n", encoding="utf-8")
            cache_dir = tope / "__pycache__"
            cache_dir.mkdir()
            (cache_dir / "cache.py").write_text("pass\n", encoding="utf-8")

            rastreador = _RastreadorCobertura([], tope)
            seguidos = set(rastreador.archivos_seguidos.values())
            self.assertIn("modulo.py", seguidos)
            self.assertIn("sub/otro.py", seguidos)
            self.assertNotIn("tests/test_algo.py", seguidos)
            self.assertNotIn(".git/config.py", seguidos)
            self.assertNotIn("__pycache__/cache.py", seguidos)

    def test_deteccion_monitoring_requiere_coverage_id(self):
        fake_monitoring = SimpleNamespace(**{k: getattr(sys.monitoring, k) for k in dir(sys.monitoring) if k != "COVERAGE_ID"})
        with patch.object(sys, "monitoring", fake_monitoring):
            rastreador = _RastreadorCobertura([], Path("."))
            self.assertFalse(rastreador.usando_monitoring)
            self.assertIsNone(rastreador.tool_id)


class RastreadorCoberturaMonitoringTests(unittest.TestCase):
    def test_line_cb_monitoring_filtro_y_registro(self):
        cb = None

        def capturar_callback(tool_id, event, callback):
            nonlocal cb
            cb = callback

        with tempfile.TemporaryDirectory() as d:
            tope = Path(d).resolve()
            archivo_seguido = tope / "seguido.py"
            archivo_seguido.write_text("x = 1\n", encoding="utf-8")
            rastreador = _RastreadorCobertura([str(archivo_seguido)], tope)

            with patch.object(sys.monitoring, "register_callback", side_effect=capturar_callback):
                rastreador.activar()
            try:
                self.assertIsNotNone(cb)
                code_seguido = compile("x = 1", str(archivo_seguido), "exec")
                code_ajeno = compile("y = 2", "/ruta/ajena.py", "exec")

                # Sin test fijado: no debe registrar nada y debe retornar DISABLE
                ret_sin_test = cb(code_seguido, 10)
                self.assertEqual(ret_sin_test, sys.monitoring.DISABLE)
                self.assertEqual(rastreador.mapa, {})

                # Con test fijado pero archivo ajeno: no debe registrar nada y debe retornar DISABLE
                rastreador.fijar_test("test_caso")
                ret_ajeno = cb(code_ajeno, 20)
                self.assertEqual(ret_ajeno, sys.monitoring.DISABLE)
                self.assertEqual(rastreador.mapa, {})
                self.assertNotIn(None, rastreador.mapa)

                # Con test fijado y archivo seguido: debe registrar en mapa y retornar DISABLE
                ret_seguido = cb(code_seguido, 30)
                self.assertEqual(ret_seguido, sys.monitoring.DISABLE)
                self.assertIn("seguido.py", rastreador.mapa)
                self.assertIn(30, rastreador.mapa["seguido.py"])
                self.assertEqual(rastreador.mapa["seguido.py"][30], {"test_caso"})
            finally:
                rastreador.desactivar()

    def test_desactivar_monitoring_apaga_eventos_con_cero(self):
        rastreador = _RastreadorCobertura([], Path("."))
        if not rastreador.usando_monitoring:
            self.skipTest("Requiere sys.monitoring")
        llamadas_eventos = []
        orig_set_events = sys.monitoring.set_events

        def registrar_eventos(tid, ev):
            llamadas_eventos.append((tid, ev))
            return orig_set_events(tid, ev)

        with patch.object(sys.monitoring, "set_events", side_effect=registrar_eventos):
            rastreador.activar()
            rastreador.desactivar()

        self.assertIn((rastreador.tool_id, 0), llamadas_eventos)
        self.assertNotIn((rastreador.tool_id, 1), llamadas_eventos)


class RastreadorCoberturaFallbackTraceTests(unittest.TestCase):
    def test_fallback_sys_settrace(self):
        trace_fn = None

        def fake_settrace(fn):
            nonlocal trace_fn
            trace_fn = fn

        with tempfile.TemporaryDirectory() as d:
            tope = Path(d).resolve()
            archivo_seguido = tope / "seguido.py"
            archivo_seguido.write_text("x = 1\n", encoding="utf-8")
            rastreador = _RastreadorCobertura([str(archivo_seguido)], tope)
            rastreador.usando_monitoring = False

            with patch.object(sys, "settrace", side_effect=fake_settrace), \
                 patch.object(sys, "gettrace", return_value="prev_trace"):
                rastreador.activar()
            try:
                self.assertIsNotNone(trace_fn)
                frame_seguido = SimpleNamespace(f_code=SimpleNamespace(co_filename=str(archivo_seguido)), f_lineno=42)
                frame_ajeno = SimpleNamespace(f_code=SimpleNamespace(co_filename="/ruta/ajena.py"), f_lineno=10)

                # trace_fn debe retornar la propia función trace
                ret = trace_fn(frame_seguido, "line", None)
                self.assertIs(ret, trace_fn)

                # Sin test fijado: no debe registrar nada
                self.assertEqual(rastreador.mapa, {})

                # Con test fijado:
                rastreador.fijar_test("test_fallback")

                # Evento distinto de 'line' (ej: 'call'): no registra
                trace_fn(frame_seguido, "call", None)
                self.assertEqual(rastreador.mapa, {})

                # Frame ajeno: no lanza KeyError ni registra nada
                trace_fn(frame_ajeno, "line", None)
                self.assertEqual(rastreador.mapa, {})
                self.assertNotIn(None, rastreador.mapa)

                # Frame seguido y evento 'line': registra línea y test
                trace_fn(frame_seguido, "line", None)
                self.assertIn("seguido.py", rastreador.mapa)
                self.assertIn(42, rastreador.mapa["seguido.py"])
                self.assertEqual(rastreador.mapa["seguido.py"][42], {"test_fallback"})
            finally:
                with patch.object(sys, "settrace") as mock_settrace:
                    rastreador.desactivar()
                    mock_settrace.assert_called_with("prev_trace")


class RastreadorCoberturaOperacionesTests(unittest.TestCase):
    def test_fijar_test_asigna_indice_cero(self):
        rastreador = _RastreadorCobertura([], Path("."))
        rastreador.fijar_test("test_id_123")
        self.assertEqual(rastreador.test_actual[0], "test_id_123")
        self.assertEqual(len(rastreador.test_actual), 1)
        rastreador.fijar_test(None)
        self.assertIsNone(rastreador.test_actual[0])

    def test_serializar_retorna_diccionario_ordenado(self):
        rastreador = _RastreadorCobertura([], Path("."))
        rastreador.mapa = {
            "b.py": {10: {"t2", "t1"}},
            "a.py": {5: {"t3"}},
        }
        esperado = {
            "a.py": {"5": ["t3"]},
            "b.py": {"10": ["t1", "t2"]},
        }
        resultado = rastreador.serializar()
        self.assertEqual(resultado, esperado)
        self.assertIsNotNone(resultado)

    def test_guardar_crea_directorios_padres_recursivamente(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "nivel1" / "nivel2" / "mapa.json"
            rastreador = _RastreadorCobertura([], Path("."))
            rastreador.mapa = {"mod.py": {1: {"t1"}}}
            rastreador.guardar(ruta)
            self.assertTrue(ruta.is_file())

    def test_guardar_acepta_directorio_existente(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "mapa.json"
            rastreador = _RastreadorCobertura([], Path("."))
            rastreador.guardar(ruta)
            rastreador.guardar(ruta)
            self.assertTrue(ruta.is_file())

    def test_guardar_formato_indentacion(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "mapa.json"
            rastreador = _RastreadorCobertura([], Path("."))
            rastreador.mapa = {"mod.py": {1: {"t1"}}}
            rastreador.guardar(ruta)
            contenido = ruta.read_text(encoding="utf-8")
            self.assertEqual(contenido, '{\n "mod.py": {\n  "1": [\n   "t1"\n  ]\n }\n}\n')

    def test_guardar_preserva_caracteres_no_ascii(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "mapa.json"
            rastreador = _RastreadorCobertura([], Path("."))
            rastreador.mapa = {"módulo.py": {1: {"test_año"}}}
            rastreador.guardar(ruta)
            contenido = ruta.read_text(encoding="utf-8")
            self.assertIn('"módulo.py"', contenido)
            self.assertIn('"test_año"', contenido)
            self.assertNotIn("\\u00f3", contenido)
            self.assertNotIn("\\u00f1", contenido)


class CoberturaSuiteRunnerTests(unittest.TestCase):
    def test_correr_suite_con_rastreador_retorna_resultado_con_verbosidad_1(self):
        class CasoTestigo(unittest.TestCase):
            def test_dummy(self):
                pass

        suite = unittest.TestSuite([CasoTestigo("test_dummy")])
        rastreador = _RastreadorCobertura([], Path("."))
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            resultado = _correr_suite(suite, rastreador)

        self.assertIsNotNone(resultado)
        self.assertIsInstance(resultado, unittest.TestResult)
        self.assertTrue(resultado.wasSuccessful())
        self.assertEqual(resultado.testsRun, 1)
        self.assertFalse(resultado.showAll)
        self.assertTrue(resultado.dots)
        salida = buf.getvalue()
        self.assertNotIn("test_dummy (", salida)
        self.assertIn("Ran 1 test", salida)

    def test_cobertura_result_fija_y_limpia_test_actual(self):
        rastreador = _RastreadorCobertura([], Path("."))
        test_activo_durante_ejecucion = None

        class CasoObservador(unittest.TestCase):
            def test_inspeccionar(self):
                nonlocal test_activo_durante_ejecucion
                test_activo_durante_ejecucion = rastreador.test_actual[0]

        suite = unittest.TestSuite([CasoObservador("test_inspeccionar")])
        with contextlib.redirect_stderr(io.StringIO()):
            _correr_suite(suite, rastreador)

        self.assertIsNotNone(test_activo_durante_ejecucion)
        self.assertIn("test_inspeccionar", test_activo_durante_ejecucion)
        self.assertIsNone(rastreador.test_actual[0])

    def test_main_guardar_cobertura_sin_rastreador_por_error_inicial(self):
        with patch.object(runner, "_RastreadorCobertura", side_effect=RuntimeError("fallo previsto")):
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                codigo = main(["--guardar-cobertura", "salida.json"])
            self.assertEqual(codigo, 2)
            self.assertIn("fallo previsto", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
