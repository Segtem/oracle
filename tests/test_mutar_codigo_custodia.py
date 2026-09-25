"""Contratos del orquestador sin lanzar una ronda recursiva."""

import contextlib
import io
import importlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

mc = None


class CustodiaMutarCodigo(unittest.TestCase):
    def setUp(self):
        global mc
        mc = importlib.import_module("tools.mutar_codigo")

    def test_objetivos_y_prioridades(self):
        disponibles = mc.objetivos_disponibles()
        for nombre in ("tools/mutar_codigo.py", "tools/ejecutar_suite_mutacion.py"):
            self.assertIn(nombre, disponibles)
        self.assertEqual(mc.resolver_objetivos(["tools/mutar_codigo.py"]),
                         [disponibles["tools/mutar_codigo.py"]])
        with self.assertRaises(ValueError):
            mc.resolver_objetivos(["tools/ausente.py"])
        with self.assertRaises(ValueError):
            mc.resolver_objetivos(["tools/mutar_codigo.py"] * 2)
        self.assertEqual(mc.comando_de_tests([disponibles["tools/mutar_codigo.py"]], priorizar=False), mc.TESTS)
        comando = mc.comando_de_tests([disponibles["tools/mutar_codigo.py"]], priorizar=True)
        self.assertEqual(comando.count("--prioridad"), 4)
        self.assertIn("--solo-prioridad", comando)
        self.assertIn("tests.test_mutar_codigo_custodia", comando)
        instalacion = mc.comando_de_tests(
            [disponibles["tools/verificar_instalacion.py"]], priorizar=True)
        self.assertIn("--solo-prioridad", instalacion)
        self.assertIn("tests.test_verificar_instalacion", instalacion)

    def test_rango_lineas(self):
        self.assertEqual(mc.parsear_rango_lineas("1-3"), (1, 3))
        self.assertEqual(mc.parsear_rango_lineas("4"), (4, 4))
        for valor in ("0", "3-1", "1-2-3", "x"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                mc.parsear_rango_lineas(valor)

    def test_esquema_equivalentes(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "equivalentes.json"
            for datos in ({}, [{"id": "a:1:0:retorno", "razon": "x"}] * 2,
                          [{"id": "a:1:0:retorno", "razon": ""}]):
                ruta.write_text(json.dumps(datos), encoding="utf-8")
                with self.subTest(datos=datos), self.assertRaises(mc.EquivalenteInvalido):
                    mc.leer_declaraciones_equivalentes(ruta)
            ruta.write_text(json.dumps([{"id": "a:1:0:retorno", "razon": "misma conducta"}]), encoding="utf-8")
            self.assertEqual(len(mc.leer_declaraciones_equivalentes(ruta)), 1)

    def test_equivalentes_del_alcance_rechaza_vencidos_y_recorta(self):
        a = mc.RAIZ / "tools" / "mutar_codigo.py"
        b = mc.RAIZ / "tools" / "ejecutar_suite_mutacion.py"
        with patch.object(mc, "objetivos_disponibles", return_value={"tools/mutar_codigo.py": a, "tools/ejecutar_suite_mutacion.py": b}), patch.object(mc, "sitios_de", side_effect=lambda ruta, raiz: [type("Sitio", (), {"id": f"tools/{ruta.name}:1:0:retorno"})()]):
            self.assertEqual(mc.equivalentes_del_alcance({"tools/mutar_codigo.py:1:0:retorno": "a", "tools/ejecutar_suite_mutacion.py:1:0:retorno": "b"}, [a]), {"tools/mutar_codigo.py:1:0:retorno": "a"})
            with self.assertRaises(mc.EquivalenteInvalido):
                mc.equivalentes_del_alcance({"tools/ausente.py:1:0:retorno": "x"}, [a])

    def test_veredicto_de_ronda_programada(self):
        objetivo = mc.RAIZ / "tools" / "mutar_codigo.py"
        def evidencia(estado, *, parcial=False, timeout=0, error=0):
            return {"corrida_mutacion": [{"baseline_verde": True, "bytecode_frio": True,
                     "mutantes": 1, "errores_arnes": error, "timeouts": timeout,
                     "parcial": parcial, "primer_inconcluso_id": None}],
                    "mutante": [{"id": "x", "estado": estado,
                                 "tests_fallaron": estado == "tests_fallaron", "cambio": "x"}],
                    "mutante_equivalente": []}
        for estado, parcial, timeout, error, esperado in (
            ("tests_fallaron", False, 0, 0, 0),
            ("pasaron", False, 0, 0, 1),
            ("tests_fallaron", True, 0, 0, 2),
            ("tests_fallaron", False, 1, 0, 2),
            ("tests_fallaron", False, 0, 1, 2),
        ):
            args = mc.argumentos((["--objetivo", "tools/mutar_codigo.py"] if parcial else
                                  ["--hechos", "--objetivo", "tools/mutar_codigo.py"]))
            with self.subTest(estado=estado, parcial=parcial, timeout=timeout, error=error), \
                 patch.object(mc, "resolver_objetivos", return_value=[objetivo]), \
                 patch.object(mc, "cargar_equivalentes", return_value={}), \
                 patch.object(mc, "equivalentes_del_alcance", return_value={}), \
                 patch.object(mc, "dependencias_de_ronda", return_value=[]), \
                 patch.object(mc, "correr", return_value=evidencia(estado, parcial=parcial, timeout=timeout, error=error)), \
                 patch.object(mc, "cargar_catalogo", return_value={}), \
                 patch.object(mc, "catalogos_a_cargar", return_value=[]), \
                 patch.object(mc, "macros_del_proyecto", return_value=[]), \
                 patch.object(mc, "medidas_aplicables", return_value=[]), \
                 patch.object(mc, "evaluar_conjunto", return_value=type("Informe", (), {"veredictos": [], "no_juzgaron": []})()), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(mc._ejecutar(None, args), esperado)

    def test_main_sin_proyecto(self):
        with patch.object(mc, "resolver_cli", return_value=None):
            self.assertEqual(mc.main([]), 2)


if __name__ == "__main__":
    unittest.main()


class ReubicacionProgramada(unittest.TestCase):
    def setUp(self):
        global mc
        mc = importlib.import_module("tools.mutar_codigo")

    def caso(self, entrada, fuente="x = 1\ny = 2\nx = 1\n", ids=()):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        raiz = Path(temporal.name)
        (raiz / "mod.py").write_text(fuente, encoding="utf-8")
        ruta = raiz / "equivalentes.json"
        ruta.write_text(json.dumps([entrada]), encoding="utf-8")
        destino = raiz / "salida.json"
        sitios = [type("Sitio", (), {"id": mid})() for mid in ids]
        with patch.object(mc, "sitios_de", return_value=sitios), \
             contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            codigo = mc.reapuntar_equivalentes(ruta, raiz, destino=destino)
        datos = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else None
        return codigo, datos

    def test_puebla_metadatos_de_primera_y_ultima_linea(self):
        for linea in (1, 3):
            mid = f"mod.py:{linea}:0:constante"
            codigo, datos = self.caso({"id": mid, "razon": "misma conducta"}, ids=[mid])
            self.assertEqual(codigo, 0)
            self.assertEqual(datos[0]["linea_texto"], "x = 1")
            self.assertEqual(datos[0]["ordinal"], 1 if linea == 1 else 2)

    def test_reubica_por_texto_y_ordinal(self):
        viejo, nuevo = "mod.py:9:0:constante", "mod.py:3:0:constante"
        codigo, datos = self.caso({"id": viejo, "linea_texto": "x = 1",
                                   "ordinal": 2, "razon": "misma conducta"}, ids=[nuevo])
        self.assertEqual(codigo, 0)
        self.assertEqual(datos[0]["id"], nuevo)

    def test_rechaza_entradas_no_resueltas(self):
        casos = [
            ({"id": "mod.py:9:0:constante", "razon": "x"}, (), "x = 1\n"),
            ({"id": "mod.py:9:0:constante", "linea_texto": "ausente", "ordinal": 1, "razon": "x"}, (), "x = 1\n"),
            ({"id": "mod.py:9:0:constante", "linea_texto": "x = 1", "ordinal": 3, "razon": "x"}, (), "x = 1\n"),
            ({"id": "mod.py:9:0:constante", "linea_texto": "x = 1", "ordinal": 1, "razon": "x"}, (), "x = 1\n"),
            ({"id": "otro.py:1:0:constante", "razon": "x"}, (), "x = 1\n"),
            ({"id": "mod.py:x:0:constante", "razon": "x"}, (), "x = 1\n"),
            ({"id": "mod.py:1:0", "razon": "x"}, (), "x = 1\n"),
        ]
        for entrada, ids, fuente in casos:
            with self.subTest(entrada=entrada):
                codigo, _ = self.caso(entrada, fuente=fuente, ids=ids)
                self.assertEqual(codigo, 1)

    def test_id_vigente_con_metadatos_no_reescribe(self):
        mid = "mod.py:1:0:constante"
        entrada = {"id": mid, "linea_texto": "x = 1", "ordinal": 1,
                   "razon": "misma conducta"}
        codigo, datos = self.caso(entrada, ids=[mid])
        self.assertEqual(codigo, 0)
        self.assertIsNone(datos)

    def test_esquema_declaraciones_rechaza_cada_campo_invalido(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "equivalentes.json"
            entradas = [42, {}, {"id": 1, "razon": "x"},
                        {"id": "a", "razon": 1}, {"id": "a", "razon": "x", "linea_texto": ""},
                        {"id": "a", "razon": "x", "ordinal": True},
                        {"id": "a", "razon": "x", "ordinal": 0}]
            for entrada in entradas:
                ruta.write_text(json.dumps([entrada]), encoding="utf-8")
                with self.subTest(entrada=entrada), self.assertRaises(mc.EquivalenteInvalido):
                    mc.leer_declaraciones_equivalentes(ruta)
            ruta.write_text("no es json", encoding="utf-8")
            with self.assertRaises(mc.EquivalenteInvalido):
                mc.leer_declaraciones_equivalentes(ruta)


class RamasDelOrquestador(unittest.TestCase):
    def setUp(self):
        global mc
        mc = importlib.import_module("tools.mutar_codigo")

    def test_dependencias_de_ronda_filtra_y_ordena(self):
        with tempfile.TemporaryDirectory() as d, patch.object(mc, "RAIZ", Path(d)):
            raiz = Path(d)
            (raiz / "nucleo").mkdir()
            (raiz / "nucleo" / "a.py").write_text("x = 1")
            (raiz / "nucleo" / "a.pyc").write_text("bytecode")
            (raiz / "nucleo" / "__pycache__").mkdir()
            (raiz / "nucleo" / "__pycache__" / "b.py").write_text("x = 2")
            dependencias = mc.dependencias_de_ronda()
            self.assertIn(raiz / "nucleo" / "a.py", dependencias)
            self.assertIn(raiz / "tools" / "ejecutar_suite_mutacion.py", dependencias)
            self.assertNotIn(raiz / "nucleo" / "a.pyc", dependencias)
            self.assertNotIn(raiz / "nucleo" / "__pycache__" / "b.py", dependencias)
            self.assertEqual(dependencias, sorted(set(dependencias)))

    def test_comando_mixto_no_restringe_descubrimiento(self):
        objetivos = [mc.RAIZ / "tools" / "mutar_codigo.py", mc.RAIZ / "nucleo" / "algebra.py"]
        comando = mc.comando_de_tests(objetivos, priorizar=True)
        self.assertNotIn("--solo-prioridad", comando)
        self.assertIn("tests.test_mutar_codigo_custodia", comando)
        self.assertIn("tests.test_algebra", comando)

    def test_argumentos_predeterminados_y_limites(self):
        args = mc.argumentos([])
        self.assertEqual(args.timeout, 60.0)
        self.assertEqual(args.limite_salida_kb, 1024)
        self.assertEqual(mc.parsear_rango_lineas("1"), (1, 1))
        with self.assertRaises(ValueError):
            mc.parsear_rango_lineas("1-0")

    def test_cargar_equivalentes_y_reapuntar_faltante_o_invalido(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            ruta = raiz / "equivalentes.json"
            self.assertEqual(mc.cargar_equivalentes(ruta), {})
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(mc.reapuntar_equivalentes(ruta, raiz), 1)
            ruta.write_text("{", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(mc.reapuntar_equivalentes(ruta, raiz), 1)
            ruta.write_text(json.dumps([{"id": "a:1:0:retorno", "razon": "x"}]))
            self.assertEqual(mc.cargar_equivalentes(ruta), {"a:1:0:retorno": "x"})

    def _ejecutar_programado(self, args, evidencia=None, error=None):
        objetivo = mc.RAIZ / "tools" / "mutar_codigo.py"
        capturado = {}
        def correr_falso(*_args, **kwargs):
            capturado.update(kwargs)
            if error is not None:
                raise error
            return evidencia
        with patch.object(mc, "resolver_objetivos", return_value=[objetivo]), \
             patch.object(mc, "cargar_equivalentes", return_value={}), \
             patch.object(mc, "equivalentes_del_alcance", return_value={}), \
             patch.object(mc, "dependencias_de_ronda", return_value=[]), \
             patch.object(mc, "correr", side_effect=correr_falso), \
             patch.object(mc, "cargar_catalogo", return_value={}), \
             patch.object(mc, "catalogos_a_cargar", return_value=[]), \
             patch.object(mc, "macros_del_proyecto", return_value=[]), \
             patch.object(mc, "medidas_aplicables", return_value=[]), \
             patch.object(mc, "evaluar_conjunto", return_value=type("Informe", (), {"veredictos": [], "no_juzgaron": []})()), \
             contextlib.redirect_stdout(salida := io.StringIO()), contextlib.redirect_stderr(error_salida := io.StringIO()):
            codigo = mc._ejecutar(None, args)
        self.ultima_salida = salida.getvalue()
        self.ultimo_error = error_salida.getvalue()
        return codigo, capturado

    def evidencia(self, *, estado="tests_fallaron", parcial=False, timeout=0, error=0):
        return {"corrida_mutacion": [{"baseline_verde": True, "bytecode_frio": True,
                "mutantes": 1, "errores_arnes": error, "timeouts": timeout,
                "parcial": parcial, "primer_inconcluso_id": None}],
                "mutante": [{"id": "x", "estado": estado, "tests_fallaron": estado == "tests_fallaron",
                             "cambio": "x"}], "mutante_equivalente": []}

    def test_filtros_de_sitio_y_rango_llegan_a_correr(self):
        args = mc.argumentos(["--hechos", "--objetivo", "tools/mutar_codigo.py",
                              "--lineas", "2-4", "--sitio", "m.py:9:0:+"])
        codigo, kwargs = self._ejecutar_programado(args, self.evidencia())
        self.assertEqual(codigo, 0)
        filtro = kwargs["filtro_sitios"]
        for mid, linea, esperado in (("m.py:9:0:+", 9, True), ("otro", 2, True),
                                      ("otro", 4, True), ("otro", 1, False),
                                      ("otro", 5, False)):
            self.assertEqual(filtro(type("Sitio", (), {"id": mid, "linea": linea})()), esperado)
        args = mc.argumentos(["--hechos", "--objetivo", "tools/mutar_codigo.py"])
        _, kwargs = self._ejecutar_programado(args, self.evidencia())
        self.assertIsNone(kwargs["filtro_sitios"])

    def test_rechaza_sitio_y_memoria_invalidos(self):
        for argumentos in (["--sitio", "x"], ["--limite-memoria-mb", "-1"]):
            args = mc.argumentos(["--hechos", "--objetivo", "tools/mutar_codigo.py", *argumentos])
            codigo, kwargs = self._ejecutar_programado(args)
            self.assertEqual(codigo, 2)
            self.assertEqual(kwargs, {})
        args = mc.argumentos(["--hechos", "--objetivo", "tools/mutar_codigo.py", "--limite-memoria-mb", "0"])
        codigo, kwargs = self._ejecutar_programado(args, self.evidencia())
        self.assertEqual(codigo, 0)
        self.assertIsNone(kwargs["limite_memoria"])

    def test_error_de_correr_sale_dos(self):
        args = mc.argumentos(["--hechos", "--objetivo", "tools/mutar_codigo.py"])
        codigo, _ = self._ejecutar_programado(args, error=ValueError("previsto"))
        self.assertEqual(codigo, 2)

    def test_veredictos_silenciosos_y_humanos(self):
        for hechos in (True, False):
            args = mc.argumentos((["--hechos"] if hechos else []) + ["--objetivo", "tools/mutar_codigo.py"])
            for evidencia, esperado in ((self.evidencia(), 0),
                                        (self.evidencia(estado="pasaron"), 1),
                                        (self.evidencia(timeout=1), 2),
                                        (self.evidencia(error=1), 2)):
                codigo, _ = self._ejecutar_programado(args, evidencia)
                self.assertEqual(codigo, esperado)
            if not hechos:
                codigo, _ = self._ejecutar_programado(args, self.evidencia(parcial=True))
                self.assertEqual(codigo, 2)

    def test_main_reapunta_y_propaga_resultado(self):
        with patch.object(mc, "reapuntar_equivalentes", return_value=1) as reapuntar:
            self.assertEqual(mc.main(["--reapuntar-equivalentes"]), 1)
            reapuntar.assert_called_once()
        with patch.object(mc, "resolver_cli", return_value=object()), \
             patch.object(mc, "escalares_del_proyecto", return_value=contextlib.nullcontext()), \
             patch.object(mc, "_ejecutar", return_value=7):
            self.assertEqual(mc.main([]), 7)

    def test_comando_solo_prioridad_con_ambos_arneses(self):
        objetivos = [mc.RAIZ / "tools" / "mutar_codigo.py",
                     mc.RAIZ / "tools" / "ejecutar_suite_mutacion.py"]
        self.assertIn("--solo-prioridad", mc.comando_de_tests(objetivos, priorizar=True))

    def test_reubicacion_con_un_metadato_o_linea_fuera_de_rango(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "mod.py").write_text("x = 1\n", encoding="utf-8")
            ruta = raiz / "equivalentes.json"
            for entrada, ids, esperado in (
                ({"id": "mod.py:1:0:constante", "linea_texto": "x = 1", "razon": "x"},
                 ["mod.py:1:0:constante"], 0),
                ({"id": "mod.py:1:0:constante", "ordinal": 1, "razon": "x"},
                 ["mod.py:1:0:constante"], 0),
                ({"id": "mod.py:9:0:constante", "razon": "x"},
                 ["mod.py:9:0:constante"], 1),
            ):
                ruta.write_text(json.dumps([entrada]), encoding="utf-8")
                sitios = [type("Sitio", (), {"id": mid})() for mid in ids]
                with self.subTest(entrada=entrada), patch.object(mc, "sitios_de", return_value=sitios), \
                     contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(mc.reapuntar_equivalentes(ruta, raiz, destino=raiz / "salida.json"), esperado)

    def test_reubicacion_json_legible_y_unicode(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "mod.py").write_text("x = 1\n", encoding="utf-8")
            ruta = raiz / "equivalentes.json"
            destino = raiz / "salida.json"
            mid = "mod.py:1:0:constante"
            ruta.write_text(json.dumps([{"id": mid, "razon": "razón válida"}]))
            sitio = type("Sitio", (), {"id": mid})()
            with patch.object(mc, "sitios_de", return_value=[sitio]), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(mc.reapuntar_equivalentes(ruta, raiz, destino=destino), 0)
            texto = destino.read_text(encoding="utf-8")
            self.assertIn('\n  "id"', texto)
            self.assertIn("razón válida", texto)

    def test_progreso_humano_y_silencioso(self):
        def correr_con_progreso(*_a, **kwargs):
            kwargs["al_terminar_uno"]({"id": "x", "cambio": "c", "tests_fallaron": True,
                                        "timeout": False, "error_arnes": False})
            return self.evidencia()
        # La salida humana debe incluir una marca por mutante; la JSON debe ser sólo evidencia.
        for hechos in (False, True):
            args = mc.argumentos((["--hechos"] if hechos else []) + ["--objetivo", "tools/mutar_codigo.py"])
            objetivo = mc.RAIZ / "tools" / "mutar_codigo.py"
            with patch.object(mc, "resolver_objetivos", return_value=[objetivo]), \
                 patch.object(mc, "cargar_equivalentes", return_value={}), \
                 patch.object(mc, "equivalentes_del_alcance", return_value={}), \
                 patch.object(mc, "dependencias_de_ronda", return_value=[]), \
                 patch.object(mc, "correr", side_effect=correr_con_progreso), \
                 patch.object(mc, "cargar_catalogo", return_value={}), \
                 patch.object(mc, "catalogos_a_cargar", return_value=[]), \
                 patch.object(mc, "macros_del_proyecto", return_value=[]), \
                 patch.object(mc, "medidas_aplicables", return_value=[]), \
                 patch.object(mc, "evaluar_conjunto", return_value=type("Informe", (), {"veredictos": [], "no_juzgaron": []})()), \
                 contextlib.redirect_stdout(salida := io.StringIO()):
                self.assertEqual(mc._ejecutar(None, args), 0)
            self.assertEqual("  ·" in salida.getvalue(), not hechos)

    def test_un_mib_y_un_kib_conservan_la_conversion(self):
        args = mc.argumentos(["--hechos", "--objetivo", "tools/mutar_codigo.py",
                              "--limite-memoria-mb", "1", "--limite-salida-kb", "1"])
        codigo, kwargs = self._ejecutar_programado(args, self.evidencia())
        self.assertEqual(codigo, 0)
        self.assertEqual(kwargs["limite_memoria"], 1024 * 1024)
        self.assertEqual(kwargs["limite_salida"], 1024)

    def test_linea_base_fallida_conserva_campos_y_limite(self):
        from perfiles.python.mutacion_codigo import EstadoTests, ResultadoTests
        args = mc.argumentos(["--hechos", "--objetivo", "tools/mutar_codigo.py"])
        resultado = ResultadoTests(EstadoTests.TESTS_FALLARON, 1, stdout="á" + "x" * 16384)
        codigo, _ = self._ejecutar_programado(args, error=mc.LineaBaseFallida(resultado))
        self.assertEqual(codigo, 2)
        error = json.loads(self.ultima_salida)["error_mutacion"][0]
        self.assertIs(error["baseline_verde"], False)
        self.assertIs(error["tests_fallaron"], True)
        self.assertEqual(error["codigo_salida"], 1)
        self.assertEqual(len(error["salida"]), 16384)
        self.assertIs(error["salida_truncada"], True)
        self.assertIn("á", self.ultima_salida)

    def test_cero_mutantes_es_inconcluso_y_json_unicode(self):
        args = mc.argumentos(["--hechos", "--objetivo", "tools/mutar_codigo.py"])
        evidencia = self.evidencia()
        evidencia["corrida_mutacion"][0]["mutantes"] = 0
        codigo, _ = self._ejecutar_programado(args, evidencia)
        self.assertEqual(codigo, 2)
        evidencia["corrida_mutacion"][0]["mutantes"] = 1
        evidencia["mutante"][0]["cambio"] = "razón"
        codigo, _ = self._ejecutar_programado(args, evidencia)
        self.assertEqual(codigo, 0)
        self.assertIn("razón", self.ultima_salida)

    def test_main_toma_argv_desde_indice_uno_y_atrapa_escalares(self):
        with patch.object(mc.sys, "argv", ["script", "--reapuntar-equivalentes"]), \
             patch.object(mc, "reapuntar_equivalentes", return_value=0) as reapuntar:
            self.assertEqual(mc.main(), 0)
            reapuntar.assert_called_once()
        with patch.object(mc, "resolver_cli", return_value=object()), \
             patch.object(mc, "escalares_del_proyecto", side_effect=mc.EscalaresInvalidas("previsto")), \
             contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(mc.main([]), 2)

    def test_raiz_tiene_precedencia_al_importar(self):
        import os
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as d:
            codigo = ("import runpy, sys; "
                      "sys.path.insert(0, 'centinela'); "
                      f"runpy.run_path({str(mc.RAIZ / 'tools' / 'mutar_codigo.py')!r}, run_name='custodia'); "
                      f"assert sys.path[0] == {str(mc.RAIZ)!r}")
            salida = subprocess.run([sys.executable, "-c", codigo], cwd=d,
                                    env={**os.environ, "PYTHONPATH": str(mc.RAIZ)},
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(salida.returncode, 0, salida.stderr)

    def test_salida_json_indenta_dos_espacios(self):
        args = mc.argumentos(["--hechos", "--objetivo", "tools/mutar_codigo.py"])
        codigo, _ = self._ejecutar_programado(args, self.evidencia())
        self.assertEqual(codigo, 0)
        self.assertIn('\n  "mutante"', self.ultima_salida)
        codigo, _ = self._ejecutar_programado(args, error=ValueError("previsto"))
        self.assertEqual(codigo, 2)
        self.assertIn('\n  "error_mutacion"', self.ultima_salida)

    def test_limite_diagnostico_exactamente_16384_no_trunca(self):
        from perfiles.python.mutacion_codigo import EstadoTests, ResultadoTests
        args = mc.argumentos(["--hechos", "--objetivo", "tools/mutar_codigo.py"])
        resultado = ResultadoTests(EstadoTests.TESTS_FALLARON, 1, stdout="x" * 16384)
        codigo, _ = self._ejecutar_programado(args, error=mc.LineaBaseFallida(resultado))
        self.assertEqual(codigo, 2)
        detalle = json.loads(self.ultima_salida)["error_mutacion"][0]
        self.assertIs(detalle["salida_truncada"], False)

    def test_progreso_vuelca_cada_fila_sin_buffer(self):
        objetivo = mc.RAIZ / "tools" / "mutar_codigo.py"
        def correr_falso(*_args, **kwargs):
            kwargs["al_terminar_uno"]({"id": "x", "cambio": "x", "tests_fallaron": True,
                                        "timeout": False, "error_arnes": False})
            return self.evidencia()
        args = mc.argumentos(["--objetivo", "tools/mutar_codigo.py"])
        with patch.object(mc, "resolver_objetivos", return_value=[objetivo]), \
             patch.object(mc, "cargar_equivalentes", return_value={}), \
             patch.object(mc, "equivalentes_del_alcance", return_value={}), \
             patch.object(mc, "dependencias_de_ronda", return_value=[]), \
             patch.object(mc, "correr", side_effect=correr_falso), \
             patch.object(mc, "cargar_catalogo", return_value={}), \
             patch.object(mc, "catalogos_a_cargar", return_value=[]), \
             patch.object(mc, "macros_del_proyecto", return_value=[]), \
             patch.object(mc, "medidas_aplicables", return_value=[]), \
             patch.object(mc, "evaluar_conjunto", return_value=type("Informe", (), {"veredictos": [], "no_juzgaron": []})()), \
             patch("builtins.print", wraps=print) as imprimir, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(mc._ejecutar(None, args), 0)
        self.assertTrue(any(llamada.kwargs.get("flush") is True for llamada in imprimir.call_args_list))
