"""Tests del mutador de CÓDIGO. Existe porque su primera corrida delató que no los tenía: de 88
mutantes vivos, 57 eran de este módulo.

La propiedad que más importa acá no es la corrección de los operadores: es que **el archivo original
se restaure siempre**. Esta herramienta escribe sobre fuentes reales.
"""

from __future__ import annotations

import subprocess
import signal
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo import mutacion_codigo as mc

FUENTE = '''\
def f(x, y):
    if x < 3 and not y:
        return True
    return x == 0
'''

SIEMPRE_PASA = [sys.executable, "-c", "raise SystemExit(0)"]
SIEMPRE_FALLA = [sys.executable, "-c", "raise SystemExit(1)"]
SIEMPRE_ERROR_ARNES = [sys.executable, "-c", "raise SystemExit(2)"]
SIEMPRE_DUERME = [sys.executable, "-c", "import time; print('antes', flush=True); time.sleep(30)"]
PASA_SOLO_CON_ORIGINAL = [
    sys.executable,
    "-c",
    ("from pathlib import Path; "
     f"raise SystemExit(Path('m.py').read_text(encoding='utf-8') != {FUENTE!r})"),
]
DUERME_SOLO_CON_MUTANTE = [
    sys.executable,
    "-c",
    ("from pathlib import Path; import time; "
     "actual = Path('m.py').read_text(encoding='utf-8'); "
     f"time.sleep(30) if actual != {FUENTE!r} else None"),
]
ERROR_SOLO_CON_MUTANTE = [
    sys.executable,
    "-c",
    ("from pathlib import Path; "
     f"raise SystemExit(2 if Path('m.py').read_text(encoding='utf-8') != {FUENTE!r} else 0)"),
]
FALLA_CON_DIAGNOSTICO_SOLO_CON_MUTANTE = [
    sys.executable,
    "-c",
    ("from pathlib import Path; import sys; "
     f"mutado = Path('m.py').read_text(encoding='utf-8') != {FUENTE!r}; "
     "print('salida del mutante') if mutado else None; "
     "print('error del mutante', file=sys.stderr) if mutado else None; "
     "raise SystemExit(1 if mutado else 0)"),
]
CACHE_SOLO_CON_MUTANTE = [
    sys.executable,
    "-c",
    ("from pathlib import Path; "
     f"mutado = Path('m.py').read_text(encoding='utf-8') != {FUENTE!r}; "
     "Path('__pycache__').mkdir(exist_ok=True) if mutado else None; "
     "raise SystemExit(1 if mutado else 0)"),
]


class SitiosTests(unittest.TestCase):
    def _sitios(self, fuente=FUENTE):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.py"
            p.write_text(fuente, encoding="utf-8")
            return mc.sitios_de(p, Path(d))

    def test_encuentra_los_cinco_tipos_de_sitio(self) -> None:
        ops = {s.operador for s in self._sitios()}
        self.assertEqual(ops, {"comparador", "booleano", "negacion", "constante", "retorno"})

    def test_el_id_es_estable_y_dice_donde(self) -> None:
        s = next(x for x in self._sitios() if x.operador == "booleano")
        self.assertEqual(s.id, f"{s.archivo}:{s.linea}:{s.columna}:booleano")
        self.assertEqual(s.linea, 2)

    def test_no_propone_mutar_un_return_que_ya_es_None(self) -> None:
        self.assertEqual([s for s in self._sitios("def f():\n    return None\n")
                          if s.operador == "retorno"], [])

    def test_las_constantes_de_TEXTO_no_se_mutan(self) -> None:
        # mutar textos genera ruido sin señal: un mensaje de error distinto no es un defecto.
        # El `return` sí es mutable —eso es otra cosa— así que hay que mirar sólo `constante`.
        sitios = self._sitios('def f():\n    return "hola"\n')
        self.assertEqual([s for s in sitios if s.operador == "constante"], [])
        self.assertEqual([s.operador for s in sitios], ["retorno"])


class MutarFuenteTests(unittest.TestCase):
    def _uno(self, operador: str) -> str:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.py"
            p.write_text(FUENTE, encoding="utf-8")
            sitio = next(s for s in mc.sitios_de(p, Path(d)) if s.operador == operador)
        return mc.mutar_fuente(FUENTE, sitio)

    def test_comparador(self) -> None:
        self.assertIn("x <= 3", self._uno("comparador"))

    def test_booleano(self) -> None:
        self.assertIn(" or ", self._uno("booleano"))

    def test_negacion_borra_el_not(self) -> None:
        salida = self._uno("negacion")
        self.assertNotIn("not y", salida)
        self.assertIn("and y", salida)

    def test_constante(self) -> None:
        self.assertTrue(any(x in self._uno("constante") for x in ("4", "False", "1")))

    def test_retorno(self) -> None:
        self.assertIn("return None", self._uno("retorno"))

    def test_un_mutante_cambia_UNA_sola_cosa(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.py"
            p.write_text(FUENTE, encoding="utf-8")
            sitios = mc.sitios_de(p, Path(d))
        for s in sitios:
            with self.subTest(sitio=s.id):
                salida = mc.mutar_fuente(FUENTE, s)
                # una sola diferencia respecto del original re-serializado
                import ast
                base = ast.unparse(ast.parse(FUENTE)).split("\n")
                mut = salida.split("\n")
                distintas = sum(1 for a, b in zip(base, mut) if a != b)
                self.assertEqual(distintas, 1)

    def test_un_sitio_que_no_matchea_devuelve_None(self) -> None:
        fantasma = mc.Sitio("m.py", 999, 0, "comparador", "x")
        self.assertIsNone(mc.mutar_fuente(FUENTE, fantasma))


class CorrerTests(unittest.TestCase):
    def _entorno(self, d: str):
        raiz = Path(d)
        objetivo = raiz / "m.py"
        objetivo.write_text(FUENTE, encoding="utf-8")
        return raiz, objetivo

    def test_restaura_el_archivo_EXACTAMENTE(self) -> None:
        """La propiedad crítica: esta herramienta escribe sobre fuentes reales."""
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            mc.correr(raiz, [objetivo], PASA_SOLO_CON_ORIGINAL)
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)

    def test_restaura_incluso_si_los_tests_pasan_siempre(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            mc.correr(raiz, [objetivo], SIEMPRE_PASA)
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)

    def test_si_los_tests_nunca_fallan_TODOS_los_mutantes_sobreviven(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            ev = mc.correr(raiz, [objetivo], SIEMPRE_PASA)
            self.assertTrue(ev["mutante"])
            self.assertTrue(all(not m["murio"] for m in ev["mutante"]))

    def test_si_la_linea_base_falla_aborta_sin_tocar_la_fuente(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            producidos = []
            with self.assertRaises(mc.LineaBaseFallida):
                mc.correr(raiz, [objetivo], SIEMPRE_FALLA,
                          al_terminar_uno=producidos.append)
            self.assertEqual(producidos, [])
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)

    def test_rechaza_un_objetivo_symlink_antes_de_escribir_fuera_de_la_raiz(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as ajeno:
            raiz = Path(d)
            exterior = Path(ajeno) / "exterior.py"
            exterior.write_text(FUENTE, encoding="utf-8")
            enlace = raiz / "m.py"
            enlace.symlink_to(exterior)

            with self.assertRaises(mc.ObjetivoInvalido):
                mc.correr(raiz, [enlace], SIEMPRE_PASA)

            self.assertEqual(exterior.read_text(encoding="utf-8"), FUENTE)

    def test_produce_hechos_con_la_forma_que_espera_la_medida(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            ev = mc.correr(raiz, [objetivo], PASA_SOLO_CON_ORIGINAL)
        self.assertEqual(sorted(ev), ["corrida_mutacion", "mutante", "mutante_equivalente"])
        self.assertEqual(sorted(ev["mutante"][0]),
                         ["apunta_a", "cambio", "codigo_salida", "equivalente_declarado",
                          "error_arnes", "estado", "id", "murio", "razon_equivalente",
                          "tests_fallaron", "timeout"])
        corrida = ev["corrida_mutacion"][0]
        self.assertTrue(corrida["baseline_verde"])
        self.assertTrue(corrida["bytecode_frio"])
        self.assertNotIn("resultado_confiable", corrida)
        self.assertNotIn("cache_reapariciones", corrida)

    def test_un_fallo_de_tests_es_la_UNICA_muerte_valida(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            ev = mc.correr(raiz, [objetivo], PASA_SOLO_CON_ORIGINAL)

        for fila in ev["mutante"]:
            self.assertTrue(fila["tests_fallaron"])
            self.assertFalse(fila["error_arnes"])
            self.assertFalse(fila["timeout"])
            self.assertTrue(fila["murio"])
            self.assertEqual(fila["estado"], "tests_fallaron")

    def test_un_error_del_arnes_no_mata_el_mutante_ni_da_confianza(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            ev = mc.correr(raiz, [objetivo], ERROR_SOLO_CON_MUTANTE)

        for fila in ev["mutante"]:
            self.assertFalse(fila["tests_fallaron"])
            self.assertTrue(fila["error_arnes"])
            self.assertFalse(fila["timeout"])
            self.assertFalse(fila["murio"])
        corrida = ev["corrida_mutacion"][0]
        self.assertGreater(corrida["errores_arnes"], 0)
        self.assertEqual(corrida["primer_inconcluso_estado"], "error_arnes")
        self.assertTrue(corrida["primer_inconcluso_id"])

    def test_un_timeout_por_mutante_es_inconcluso_y_restaura_la_fuente(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)

            def resultado_segun_fuente(*_args, **_kwargs):
                if objetivo.read_text(encoding="utf-8") == FUENTE:
                    return mc.ResultadoTests(mc.EstadoTests.PASARON, 0)
                return mc.ResultadoTests(
                    mc.EstadoTests.TIMEOUT, None, stdout="antes del timeout")

            # El timeout real del subproceso se prueba en `test_ejecutar_tests_distingue...`.
            # Acá se prueba, sin depender de que otro intérprete arranque en menos de 50 ms, cómo
            # `correr` propaga ese estado para cada mutante y restaura la fuente.
            with mock.patch.object(mc, "ejecutar_tests", side_effect=resultado_segun_fuente):
                ev = mc.correr(raiz, [objetivo], DUERME_SOLO_CON_MUTANTE,
                               timeout_por_ejecucion=0.05)

            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)
        for fila in ev["mutante"]:
            self.assertFalse(fila["tests_fallaron"])
            self.assertFalse(fila["error_arnes"])
            self.assertTrue(fila["timeout"])
            self.assertFalse(fila["murio"])
        self.assertGreater(ev["corrida_mutacion"][0]["timeouts"], 0)
        self.assertEqual(ev["corrida_mutacion"][0]["primer_inconcluso_estado"], "timeout")

    def test_conserva_stdout_y_stderr_del_primer_fallo(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            corrida = mc.correr(
                raiz, [objetivo], FALLA_CON_DIAGNOSTICO_SOLO_CON_MUTANTE
            )["corrida_mutacion"][0]

        self.assertEqual(corrida["primer_fallo_estado"], "tests_fallaron")
        self.assertIn("salida del mutante", corrida["primer_fallo_salida"])
        self.assertIn("error del mutante", corrida["primer_fallo_salida"])

    def test_un_equivalente_declarado_sale_de_los_mutantes_y_lleva_su_razon(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            todos = mc.correr(raiz, [objetivo], SIEMPRE_PASA)["mutante"]
            elegido = todos[0]["id"]
            ev = mc.correr(raiz, [objetivo], SIEMPRE_PASA, {elegido: "porque sí, con razón escrita"})

        self.assertNotIn(elegido, [m["id"] for m in ev["mutante"]])
        eq = next(m for m in ev["mutante_equivalente"] if m["id"] == elegido)
        self.assertEqual(eq["razon_equivalente"], "porque sí, con razón escrita")

    def test_un_equivalente_inconcluso_permanece_en_los_contadores(self) -> None:
        fuente = "valor = True\n"
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            objetivo = raiz / "m.py"
            objetivo.write_text(fuente, encoding="utf-8")
            sitio = mc.sitios_de(objetivo, raiz)[0]

            def resultado_segun_fuente(*_args, **_kwargs):
                if objetivo.read_text(encoding="utf-8") == fuente:
                    return mc.ResultadoTests(mc.EstadoTests.PASARON, 0)
                return mc.ResultadoTests(mc.EstadoTests.TIMEOUT, None)

            with mock.patch.object(mc, "ejecutar_tests", side_effect=resultado_segun_fuente):
                ev = mc.correr(
                    raiz, [objetivo], SIEMPRE_PASA,
                    {sitio.id: "equivalencia revisada pero ejecución inconclusa"})

        self.assertEqual(ev["mutante"], [])
        self.assertTrue(ev["mutante_equivalente"][0]["timeout"])
        self.assertEqual(ev["corrida_mutacion"][0]["timeouts"], 1)

    def test_un_equivalente_sin_razon_se_rechaza_antes_de_mutar(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            sitio = mc.sitios_de(objetivo, raiz)[0]
            with self.assertRaises(mc.EquivalenteInvalido):
                mc.correr(raiz, [objetivo], SIEMPRE_PASA, {sitio.id: "  "})
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)

    def test_un_equivalente_vencido_se_rechaza_antes_de_mutar(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            with self.assertRaises(mc.EquivalenteInvalido):
                mc.correr(raiz, [objetivo], SIEMPRE_PASA,
                          {"m.py:999:0:retorno": "existió en otra versión"})
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)

    def test_si_MATAN_el_proceso_el_archivo_igual_se_restaura(self) -> None:
        """El `finally` no alcanza: `timeout` manda SIGTERM y Python termina sin ejecutarlo. Pasó de
        verdad —una corrida cortada dejó `mutacion_codigo.py` mutado en el árbol— y el daño lo salvó
        git, no la herramienta. Se prueba lanzando un subproceso y matándolo a mitad."""
        import os
        import signal as sig
        import time
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            guion = raiz / "correr.py"
            guion.write_text(
                "import sys, time\n"
                f"sys.path.insert(0, {str(RAIZ)!r})\n"
                "from nucleo import mutacion_codigo as mc\n"
                f"mc.correr({str(raiz)!r} and __import__('pathlib').Path({str(raiz)!r}), "
                f"[__import__('pathlib').Path({str(objetivo)!r})], "
                f"{DUERME_SOLO_CON_MUTANTE!r})\n",
                encoding="utf-8")
            proc = subprocess.Popen([sys.executable, str(guion)])
            limite = time.monotonic() + 10
            while objetivo.read_text(encoding="utf-8") == FUENTE and time.monotonic() < limite:
                if proc.poll() is not None:
                    self.fail("el subproceso terminó antes de escribir el primer mutante")
                time.sleep(0.01)
            self.assertNotEqual(objetivo.read_text(encoding="utf-8"), FUENTE,
                                "el subproceso no llegó a escribir el primer mutante")
            os.kill(proc.pid, sig.SIGTERM)
            proc.wait(timeout=15)

            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE,
                             "el archivo quedó mutado después de matar el proceso")

    def test_limpiar_cache_borra_los_pycache(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sub" / "__pycache__").mkdir(parents=True)
            self.assertEqual(mc.limpiar_cache(Path(d)), 1)
            self.assertFalse((Path(d) / "sub" / "__pycache__").exists())

    def test_limpiar_cache_desenlaza_un_symlink_sin_borrar_su_destino(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            destino = raiz / "cache_ajeno"
            destino.mkdir()
            enlace = raiz / "sub" / "__pycache__"
            enlace.parent.mkdir()
            enlace.symlink_to(destino, target_is_directory=True)

            self.assertEqual(mc.limpiar_cache(raiz), 1)
            self.assertFalse(enlace.exists())
            self.assertFalse(enlace.is_symlink())
            self.assertTrue(destino.exists())

    def test_limpiar_cache_tambien_desenlaza_un_symlink_roto(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            enlace = raiz / "sub" / "__pycache__"
            enlace.parent.mkdir()
            enlace.symlink_to(raiz / "destino-que-no-existe", target_is_directory=True)

            self.assertTrue(enlace.is_symlink())
            self.assertFalse(enlace.exists())
            self.assertEqual(mc.limpiar_cache(raiz), 1)
            self.assertFalse(enlace.is_symlink())

    def test_limpiar_cache_no_declara_exito_si_el_borrado_falla(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            cache = Path(d) / "__pycache__"
            cache.mkdir()
            with mock.patch.object(mc.shutil, "rmtree", side_effect=OSError("sin permiso")):
                with self.assertRaises(mc.CacheNoLimpio):
                    mc.limpiar_cache(Path(d))

    def test_limpiar_cache_no_confia_en_un_enumerador_que_devuelve_otra_cosa(self) -> None:
        """Defensa en profundidad: este módulo se muta a sí mismo. Si el `== '__pycache__'` del
        enumerador cambia a `!=`, el punto de borrado no puede obedecer esa lista corrompida."""
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            victima = raiz / "codigo"
            victima.mkdir()
            (victima / "importante.py").write_text("valor = 1\n", encoding="utf-8")
            with mock.patch.object(mc, "_caches_bajo", return_value=[victima]):
                with self.assertRaises(mc.CacheNoLimpio):
                    mc.limpiar_cache(raiz)

            self.assertTrue((victima / "importante.py").exists())

    def test_limpiar_cache_no_borra_un_cache_fuera_de_la_raiz(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as ajeno:
            raiz = Path(d)
            victima = Path(ajeno) / "__pycache__"
            victima.mkdir()
            (victima / "importante.pyc").write_bytes(b"no borrar")
            with mock.patch.object(mc, "_caches_bajo", return_value=[victima]):
                with self.assertRaises(mc.CacheNoLimpio):
                    mc.limpiar_cache(raiz)

            self.assertTrue((victima / "importante.pyc").exists())

    def test_un_cache_que_reaparece_durante_tests_invalida_la_ronda(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            with self.assertRaises(mc.CacheNoLimpio) as atrapado:
                mc.correr(raiz, [objetivo], CACHE_SOLO_CON_MUTANTE)

            self.assertIn("después de ejecutar", str(atrapado.exception))
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)
            self.assertFalse((raiz / "__pycache__").exists())

    def test_un_cache_que_reaparece_en_la_linea_base_tampoco_se_oculta(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            comando = [sys.executable, "-c",
                       "from pathlib import Path; Path('__pycache__').mkdir(); raise SystemExit(0)"]
            with self.assertRaises(mc.CacheNoLimpio) as atrapado:
                mc.correr(raiz, [objetivo], comando)

            self.assertIn("línea base", str(atrapado.exception))
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)

    def test_un_import_normal_usa_cache_aislado_y_no_crea_pycache_local(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "modulo.py").write_text("valor = 1\n", encoding="utf-8")
            ev = mc.correr(raiz, [], [sys.executable, "-c", "import modulo"])

            self.assertTrue(ev["corrida_mutacion"][0]["bytecode_frio"])
            self.assertFalse((raiz / "__pycache__").exists())

    def test_un_cache_creado_por_callback_antes_del_cierre_invalida_la_ronda(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            creado = False

            def reaparecer(_fila):
                nonlocal creado
                if not creado:
                    (raiz / "__pycache__").mkdir()
                    creado = True

            with self.assertRaises(mc.CacheNoLimpio):
                mc.correr(raiz, [objetivo], SIEMPRE_PASA, al_terminar_uno=reaparecer)
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)

    def test_correr_tests_lee_el_codigo_de_salida(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(mc.correr_tests(SIEMPRE_PASA, Path(d)))
            self.assertFalse(mc.correr_tests(SIEMPRE_FALLA, Path(d)))

    def test_ejecutar_tests_distingue_fallo_error_y_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            fallo = mc.ejecutar_tests(SIEMPRE_FALLA, raiz, timeout=1)
            error = mc.ejecutar_tests(SIEMPRE_ERROR_ARNES, raiz, timeout=1)
            timeout = mc.ejecutar_tests(SIEMPRE_DUERME, raiz, timeout=0.05)
            expirado = subprocess.TimeoutExpired(
                SIEMPRE_DUERME, 1, output=b"antes", stderr=b"detalle")
            with mock.patch.object(mc.subprocess, "run", side_effect=expirado):
                timeout_con_salida = mc.ejecutar_tests(SIEMPRE_DUERME, raiz, timeout=1)

        self.assertEqual(fallo.estado.value, "tests_fallaron")
        self.assertEqual(error.estado.value, "error_arnes")
        self.assertEqual(timeout.estado.value, "timeout")
        self.assertIn("antes", timeout_con_salida.salida)
        self.assertIn("detalle", timeout_con_salida.salida)

    def test_un_codigo_de_fallo_de_tests_no_puede_ser_una_senal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                mc.ejecutar_tests(
                    SIEMPRE_PASA, Path(d), timeout=1,
                    codigos_fallo_tests={-signal.SIGKILL})

    def test_un_ejecutable_inexistente_es_error_del_arnes_no_excepcion(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = mc.ejecutar_tests([str(Path(d) / "no-existe")], Path(d), timeout=1)

        self.assertEqual(r.estado.value, "error_arnes")
        self.assertIsNone(r.codigo_salida)
        self.assertTrue(r.salida)

    def test_timeout_de_linea_base_aborta_con_diagnostico_y_sin_mutar(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            resultado = mc.ResultadoTests(
                mc.EstadoTests.TIMEOUT, None, stdout="antes del timeout")
            with mock.patch.object(mc, "ejecutar_tests", return_value=resultado):
                with self.assertRaises(mc.LineaBaseFallida) as atrapado:
                    mc.correr(raiz, [objetivo], SIEMPRE_DUERME,
                              timeout_por_ejecucion=0.05)

            self.assertEqual(atrapado.exception.resultado.estado.value, "timeout")
            self.assertIn("antes", atrapado.exception.resultado.salida)
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)


if __name__ == "__main__":
    unittest.main()
