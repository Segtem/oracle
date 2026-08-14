"""Tests del mutador de CÓDIGO. Existe porque su primera corrida delató que no los tenía: de 88
mutantes vivos, 57 eran de este módulo.

La propiedad que más importa acá no es la corrección de los operadores: es que **el árbol original
no se escriba nunca**. Cada mutante vive en una copia temporal.
"""

from __future__ import annotations

import io
import json
import subprocess
import signal
import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from perfiles.python import mutacion_codigo as mc

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

    def test_sitio_y_resultado_son_inmutables_y_publican_defaults_exactos(self) -> None:
        sitio = mc.Sitio("m.py", 1, 2, "constante", "1 → 2")
        resultado = mc.ResultadoTests(mc.EstadoTests.PASARON, 0)
        self.assertEqual((resultado.stdout_truncado, resultado.stderr_truncado), (False, False))
        for objeto, campo in ((sitio, "linea"), (resultado, "codigo_salida")):
            with self.subTest(tipo=type(objeto).__name__), self.assertRaises(FrozenInstanceError):
                setattr(objeto, campo, 99)

    def test_las_descripciones_de_constantes_dicen_el_cambio_generado(self) -> None:
        sitios = self._sitios("bandera = True\nnumero = 7\n")
        self.assertEqual(
            [sitio.descripcion for sitio in sitios if sitio.operador == "constante"],
            ["True → False", "7 → 8"],
        )

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
            corrida = ev["corrida_mutacion"][0]
            self.assertEqual(corrida["primer_fallo_id"], "")
            self.assertEqual(corrida["primer_fallo_estado"], "")
            self.assertIsNone(corrida["primer_fallo_codigo_salida"])
            self.assertEqual(corrida["primer_fallo_salida"], "")
            self.assertIs(corrida["primer_fallo_salida_truncada"], False)
            self.assertEqual(corrida["primer_inconcluso_id"], "")
            self.assertEqual(corrida["primer_inconcluso_estado"], "")
            self.assertIsNone(corrida["primer_inconcluso_codigo_salida"])
            self.assertEqual(corrida["primer_inconcluso_salida"], "")
            self.assertIs(corrida["primer_inconcluso_salida_truncada"], False)

    def test_primer_fallo_e_inconcluso_son_los_primeros_reales(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            sitios = mc.sitios_de(objetivo, raiz)
            resultados = [
                mc.ResultadoTests(mc.EstadoTests.PASARON, 0),       # línea base
                mc.ResultadoTests(mc.EstadoTests.PASARON, 0),       # primer mutante
                mc.ResultadoTests(mc.EstadoTests.TESTS_FALLARON, 1),
                mc.ResultadoTests(mc.EstadoTests.ERROR_ARNES, 2),
            ] + [mc.ResultadoTests(mc.EstadoTests.PASARON, 0)] * (len(sitios) - 3)
            with mock.patch.object(mc, "ejecutar_tests", side_effect=resultados):
                corrida = mc._correr_en_raiz(
                    raiz, [objetivo], SIEMPRE_PASA)["corrida_mutacion"][0]
        self.assertEqual(corrida["primer_fallo_id"], sitios[1].id)
        self.assertEqual(corrida["primer_fallo_estado"], "tests_fallaron")
        self.assertEqual(corrida["primer_inconcluso_id"], sitios[2].id)
        self.assertEqual(corrida["primer_inconcluso_estado"], "error_arnes")

    def test_si_la_linea_base_falla_aborta_sin_tocar_la_fuente(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            producidos = []
            with self.assertRaises(mc.LineaBaseFallida):
                mc.correr(raiz, [objetivo], SIEMPRE_FALLA,
                          al_terminar_uno=producidos.append)
            self.assertEqual(producidos, [])
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)

    def test_una_linea_base_sin_salida_conserva_un_diagnostico_explicito(self) -> None:
        resultado = mc.ResultadoTests(mc.EstadoTests.ERROR_ARNES, 2)
        error = mc.LineaBaseFallida(resultado)
        self.assertIn("(sin salida diagnóstica)", str(error))

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
        self.assertEqual(corrida["rondas_ejecutadas"], len(ev["mutante"]) + 1)
        self.assertEqual(corrida["rondas_cache_verificadas"], len(ev["mutante"]) + 1)
        self.assertEqual(corrida["mutantes_reutilizados"], 0)

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

            def resultado_segun_fuente(_comando, raiz_copia, **_kwargs):
                if (raiz_copia / "m.py").read_text(encoding="utf-8") == FUENTE:
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

            def resultado_segun_fuente(_comando, raiz_copia, **_kwargs):
                if (raiz_copia / "m.py").read_text(encoding="utf-8") == fuente:
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

    def test_equivalentes_invalidos_se_rechazan_antes_de_copiar(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            sitio = mc.sitios_de(objetivo, raiz)[0]
            for equivalentes in ({sitio.id: "  "}, {"vencido": "razón"}):
                with self.subTest(equivalentes=equivalentes), mock.patch.object(
                        mc, "_copiar_proyecto") as copiar:
                    with self.assertRaises(mc.EquivalenteInvalido):
                        mc.correr(raiz, [objetivo], SIEMPRE_PASA, equivalentes)
                    copiar.assert_not_called()

    def test_la_validacion_interna_rechaza_equivalentes_y_limites_invalidos(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            sitio = mc.sitios_de(objetivo, raiz)[0]
            for equivalentes in ({sitio.id: "  "}, {"vencido": "razón"}):
                with self.subTest(equivalentes=equivalentes), self.assertRaises(
                        mc.EquivalenteInvalido):
                    mc._correr_en_raiz(
                        raiz, [objetivo], SIEMPRE_PASA, equivalentes=equivalentes)
            for limite in (True, 0, -1, 1.5):
                with self.subTest(limite=limite), self.assertRaises(ValueError):
                    mc._correr_en_raiz(
                        raiz, [objetivo], SIEMPRE_PASA, limite_diagnostico=limite)

    def test_linea_base_tolera_y_limpia_cache_preexistente(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "__pycache__").mkdir()
            evidencia = mc._correr_en_raiz(raiz, [], SIEMPRE_PASA)
            self.assertTrue(evidencia["corrida_mutacion"][0]["baseline_verde"])
            self.assertFalse((raiz / "__pycache__").exists())

    def test_SIGTERM_no_toca_el_original_y_termina_el_subproceso(self) -> None:
        """La ronda muta una copia: el original no cambia ni durante ni después de SIGTERM."""
        import os
        import signal as sig
        import time
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as externo:
            raiz, objetivo = self._entorno(d)
            marca = Path(externo) / "mutante-iniciado"
            comando = [
                sys.executable, "-c",
                ("from pathlib import Path; import os,time; "
                 f"mutado = Path('m.py').read_text(encoding='utf-8') != {FUENTE!r}; "
                 f"Path({str(marca)!r}).write_text(str(os.getpid())) if mutado else None; "
                 "time.sleep(30) if mutado else None"),
            ]
            guion = raiz / "correr.py"
            guion.write_text(
                "import sys\n"
                f"sys.path.insert(0, {str(RAIZ)!r})\n"
                "from perfiles.python import mutacion_codigo as mc\n"
                f"mc.correr({str(raiz)!r} and __import__('pathlib').Path({str(raiz)!r}), "
                f"[__import__('pathlib').Path({str(objetivo)!r})], "
                f"{comando!r})\n",
                encoding="utf-8")
            proc = subprocess.Popen([sys.executable, str(guion)])
            limite = time.monotonic() + 10
            while not marca.exists() and time.monotonic() < limite:
                if proc.poll() is not None:
                    self.fail("la ronda terminó antes de ejecutar el primer mutante")
                time.sleep(0.01)
            self.assertTrue(marca.exists(), "la ronda no llegó al primer mutante")
            hijo = int(marca.read_text(encoding="utf-8"))
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)
            os.kill(proc.pid, sig.SIGTERM)
            proc.wait(timeout=15)

            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE,
                             "SIGTERM alteró la fuente original")
            with self.assertRaises(ProcessLookupError):
                os.kill(hijo, 0)

    def test_dos_rondas_no_pueden_tomar_el_mismo_bloqueo(self) -> None:
        import os
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            with mc._bloqueo_de_ronda(raiz):
                with self.assertRaises(mc.RondaEnCurso) as atrapado:
                    with mc._bloqueo_de_ronda(raiz):
                        pass
                self.assertIn(f"pid {os.getpid()}", str(atrapado.exception))

    def test_senales_de_ronda_publican_salida_convencional_y_se_restauran(self) -> None:
        anterior = signal.getsignal(signal.SIGTERM)
        with mock.patch.object(mc, "_terminar_activos") as terminar:
            with mc._senales_de_ronda():
                handler = signal.getsignal(signal.SIGTERM)
                with self.assertRaises(SystemExit) as salida:
                    handler(signal.SIGTERM, None)
                self.assertEqual(
                    salida.exception.code,
                    mc.DESPLAZAMIENTO_SALIDA_POR_SENAL + signal.SIGTERM)
                terminar.assert_called_once_with()
        self.assertIs(signal.getsignal(signal.SIGTERM), anterior)

    def test_copiar_proyecto_preserva_enlaces_y_excluye_metadatos(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            raiz = base / "origen"
            destino = base / "copia"
            raiz.mkdir()
            (raiz / "dato.txt").write_text("dato", encoding="utf-8")
            (raiz / "enlace").symlink_to("dato.txt")
            (raiz / ".git").mkdir()
            (raiz / ".git" / "config").write_text("secreto", encoding="utf-8")
            (raiz / "__pycache__").mkdir()
            (raiz / "__pycache__" / "m.pyc").write_bytes(b"cache")
            mc._copiar_proyecto(raiz, destino)
            self.assertTrue((destino / "enlace").is_symlink())
            self.assertEqual((destino / "enlace").readlink(), Path("dato.txt"))
            self.assertFalse((destino / ".git").exists())
            self.assertFalse((destino / "__pycache__").exists())

    def test_comando_en_copia_solo_reescribe_rutas_absolutas_internas(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as e:
            raiz = Path(d).resolve()
            copia = raiz.parent / "copia-aislada"
            interno = raiz / "sub" / "a.py"
            externo = Path(e).resolve() / "b.py"
            comando = ["python", str(interno), "relativo.py", str(externo)]
            self.assertEqual(
                mc._comando_en_copia(comando, raiz, copia),
                ["python", str(copia / "sub" / "a.py"), "relativo.py", str(externo)])

    def test_validar_objetivos_rechaza_raiz_y_objetivos_no_fisicos(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as e:
            raiz = Path(d)
            exterior = Path(e) / "m.py"
            exterior.write_text(FUENTE, encoding="utf-8")
            directorio = raiz / "directorio.py"
            directorio.mkdir()
            for objetivos in ([raiz / "ausente.py"], [directorio], [exterior]):
                with self.subTest(objetivos=objetivos), self.assertRaises(mc.ObjetivoInvalido):
                    mc._validar_objetivos(raiz, objetivos)
            archivo_raiz = raiz / "archivo"
            archivo_raiz.write_text("x", encoding="utf-8")
            with self.assertRaises(mc.ObjetivoInvalido):
                mc._validar_objetivos(archivo_raiz, [])

    def test_un_fallo_de_escritura_en_la_copia_no_toca_el_original(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            with mock.patch.object(mc.os, "replace", side_effect=OSError("disco roto")):
                with self.assertRaises(OSError):
                    mc.correr(raiz, [objetivo], SIEMPRE_PASA)
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)

    def test_la_copia_temporal_se_elimina_al_terminar(self) -> None:
        antes = {p for p in Path(tempfile.gettempdir()).glob("oracle-mutacion-*") if p.is_dir()}
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            ev = mc.correr(raiz, [objetivo], SIEMPRE_PASA)
        despues = {p for p in Path(tempfile.gettempdir()).glob("oracle-mutacion-*") if p.is_dir()}
        self.assertEqual(despues, antes)
        self.assertTrue(ev["corrida_mutacion"][0]["aislada"])
        self.assertTrue(ev["corrida_mutacion"][0]["fuentes_originales_intactas"])

    def test_detecta_por_separado_original_modificado_o_eliminado(self) -> None:
        class AlterarOriginal:
            def __init__(self, objetivo: Path, eliminar: bool):
                self.objetivo = objetivo
                self.eliminar = eliminar
                self.hecho = False

            def __call__(self, _fila):
                if self.hecho:
                    return
                if self.eliminar:
                    self.objetivo.unlink()
                else:
                    self.objetivo.write_text("cambio externo\n", encoding="utf-8")
                self.hecho = True

        for eliminar in (False, True):
            with self.subTest(eliminar=eliminar), tempfile.TemporaryDirectory() as d:
                raiz, objetivo = self._entorno(d)
                with self.assertRaises(mc.AislamientoRoto):
                    mc.correr(
                        raiz, [objetivo], SIEMPRE_PASA,
                        al_terminar_uno=AlterarOriginal(objetivo, eliminar))

    def test_una_ronda_interrumpida_reanuda_desde_un_manifiesto_verificado(self) -> None:
        class Interrumpida(RuntimeError):
            pass

        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            manifiesto = raiz / "progreso.json"
            vistos = 0

            def cortar(_fila):
                nonlocal vistos
                vistos += 1
                raise Interrumpida("corte simulado")

            with self.assertRaises(Interrumpida):
                mc.correr(
                    raiz, [objetivo], SIEMPRE_PASA, al_terminar_uno=cortar,
                    manifiesto=manifiesto)
            guardado = json.loads(manifiesto.read_text(encoding="utf-8"))
            self.assertEqual(guardado["estado"], "en_curso")
            self.assertEqual(len(guardado["completados"]), 1)

            evidencia = mc.correr(
                raiz, [objetivo], SIEMPRE_PASA,
                manifiesto=manifiesto, reanudar=True)
            final = json.loads(manifiesto.read_text(encoding="utf-8"))

        self.assertEqual(final["estado"], "completa")
        self.assertEqual(evidencia["corrida_mutacion"][0]["mutantes_reutilizados"], 1)
        self.assertEqual(len(final["completados"]), len(evidencia["mutante"]))

    def test_reanudar_rechaza_fuentes_cambiadas_o_manifiesto_corrupto(self) -> None:
        class Interrumpida(RuntimeError):
            pass

        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            dependencia = raiz / "test_contrato.py"
            dependencia.write_text("VERSION = 1\n", encoding="utf-8")
            manifiesto = raiz / "progreso.json"
            with self.assertRaises(Interrumpida):
                mc.correr(
                    raiz, [objetivo], SIEMPRE_PASA,
                    al_terminar_uno=lambda _fila: (_ for _ in ()).throw(Interrumpida()),
                    manifiesto=manifiesto, dependencias=[dependencia])
            original_manifiesto = manifiesto.read_text(encoding="utf-8")
            objetivo.write_text(FUENTE + "\n# cambio\n", encoding="utf-8")
            with self.assertRaises(mc.ManifiestoInvalido):
                mc.correr(
                    raiz, [objetivo], SIEMPRE_PASA,
                    manifiesto=manifiesto, reanudar=True, dependencias=[dependencia])

            objetivo.write_text(FUENTE, encoding="utf-8")
            dependencia.write_text("VERSION = 2\n", encoding="utf-8")
            with self.assertRaises(mc.ManifiestoInvalido):
                mc.correr(
                    raiz, [objetivo], SIEMPRE_PASA,
                    manifiesto=manifiesto, reanudar=True, dependencias=[dependencia])

            dependencia.write_text("VERSION = 1\n", encoding="utf-8")
            datos = json.loads(original_manifiesto)
            datos["completados"][0]["murio"] = not datos["completados"][0]["murio"]
            manifiesto.write_text(json.dumps(datos), encoding="utf-8")
            with self.assertRaises(mc.ManifiestoInvalido):
                mc.correr(
                    raiz, [objetivo], SIEMPRE_PASA,
                    manifiesto=manifiesto, reanudar=True, dependencias=[dependencia])

    def test_cargar_reanudacion_rechaza_cada_clase_de_corrupcion(self) -> None:
        sitio = mc.Sitio("m.py", 1, 0, "retorno", "return <algo> → return None")
        identidad = {"equivalentes": {}}
        fila = {
            "id": sitio.id,
            "apunta_a": sitio.archivo,
            "cambio": f"{sitio.operador}: {sitio.descripcion}",
            "murio": False,
            "estado": mc.EstadoTests.PASARON.value,
            "tests_fallaron": False,
            "error_arnes": False,
            "timeout": False,
            "codigo_salida": 0,
            "equivalente_declarado": False,
            "razon_equivalente": "",
        }

        def manifiesto(filas=None):
            filas = [dict(fila)] if filas is None else filas
            return {
                "esquema": mc.ESQUEMA_MANIFIESTO,
                "identidad": identidad,
                "huella": mc._huella_json(identidad),
                "completados": filas,
                "huella_completados": mc._huella_json(filas),
            }

        def con_fila(**cambios):
            alterada = dict(fila)
            alterada.update(cambios)
            return manifiesto([alterada])

        casos = {
            "raiz_no_objeto": [],
            "esquema": {**manifiesto(), "esquema": "desconocido"},
            "identidad": {**manifiesto(), "identidad": {"equivalentes": {"x": "y"}}},
            "huella_identidad": {**manifiesto(), "huella": "0"},
            "filas_no_lista": {**manifiesto(), "completados": {}},
            "huella_filas": {**manifiesto(), "huella_completados": "0"},
            "fila_no_objeto": manifiesto(["fila"]),
            "id_duplicado": manifiesto([dict(fila), dict(fila)]),
            "id_vencido": con_fila(id="m.py:9:0:retorno"),
            "campo_faltante": manifiesto([{k: v for k, v in fila.items() if k != "cambio"}]),
            "archivo": con_fila(apunta_a="otro.py"),
            "cambio": con_fila(cambio="constante: otro"),
            "estado": con_fila(estado="inventado"),
            "murio_no_bool": con_fila(murio=1, tests_fallaron=1),
            "muerte_incoherente": con_fila(murio=True),
            "equivalente_incoherente": con_fila(equivalente_declarado=True),
            "razon_incoherente": con_fila(razon_equivalente="inventada"),
        }
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "estado.json"
            valido = manifiesto()
            ruta.write_text(json.dumps(valido), encoding="utf-8")
            datos, filas = mc._cargar_reanudacion(ruta, identidad, {sitio.id: sitio})
            self.assertEqual(datos, valido)
            self.assertEqual(filas, [fila])
            for nombre, datos_corruptos in casos.items():
                ruta.write_text(json.dumps(datos_corruptos), encoding="utf-8")
                with self.subTest(nombre=nombre), self.assertRaises(mc.ManifiestoInvalido):
                    mc._cargar_reanudacion(ruta, identidad, {sitio.id: sitio})

    def test_limpiar_cache_borra_los_pycache(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sub" / "__pycache__").mkdir(parents=True)
            self.assertEqual(mc.limpiar_cache(Path(d)), 1)
            self.assertFalse((Path(d) / "sub" / "__pycache__").exists())

    def test_el_recorrido_de_cache_es_fisico_podado_y_profundo_primero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "__pycache__").mkdir()
            (raiz / "sub" / "__pycache__").mkdir(parents=True)
            encontrados = mc._caches_bajo(raiz)
            self.assertEqual(
                encontrados,
                [raiz / "sub" / "__pycache__", raiz / "__pycache__"])

        with mock.patch.object(mc.os, "walk", return_value=[]) as walk:
            mc._caches_bajo(Path("raiz"))
        self.assertEqual(walk.call_args.args, (Path("raiz"),))
        self.assertIs(walk.call_args.kwargs["topdown"], True)
        self.assertIs(walk.call_args.kwargs["followlinks"], False)
        self.assertTrue(callable(walk.call_args.kwargs["onerror"]))

    def test_resolver_existente_falla_cerrado_y_la_muestra_esta_acotada(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            with self.assertRaises(FileNotFoundError):
                mc._resolver_existente(raiz / "ausente")
            rutas = [raiz / str(i) for i in range(5)]
            self.assertEqual(mc._muestra_rutas(rutas), ", ".join(map(str, rutas[:3])))
            self.assertEqual(mc._muestra_rutas(rutas, raiz), "0, 1, 2")

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
                mc._correr_en_raiz(
                    raiz, [objetivo], SIEMPRE_PASA, al_terminar_uno=reaparecer)
            self.assertEqual(objetivo.read_text(encoding="utf-8"), FUENTE)

    def test_correr_tests_lee_el_codigo_de_salida(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(mc.correr_tests(SIEMPRE_PASA, Path(d)))
            self.assertFalse(mc.correr_tests(SIEMPRE_FALLA, Path(d)))

    def test_la_politica_operativa_predeterminada_es_unica_y_explicita(self) -> None:
        self.assertEqual(mc.TIMEOUT_PREDETERMINADO, 60.0)
        self.assertEqual(mc.CODIGOS_FALLO_PREDETERMINADOS, frozenset({1}))
        self.assertEqual(mc.LIMITE_DIAGNOSTICO_PREDETERMINADO, 16_384)
        self.assertEqual(mc.LIMITE_SALIDA_PREDETERMINADO, 1_048_576)
        self.assertEqual(mc.MAX_RUTAS_DIAGNOSTICO, 3)
        self.assertEqual(mc.ESPERA_TERMINACION_SUAVE, 1.0)
        self.assertEqual(mc.ESPERA_TERMINACION_FORZADA, 2.0)
        self.assertEqual(mc.LONGITUD_IDENTIFICADOR_BLOQUEO, 24)
        self.assertEqual(mc.DESPLAZAMIENTO_SALIDA_POR_SENAL, 128)
        self.assertEqual(mc.SENAL_SONDEO_GRUPO, 0)

    def test_ejecutar_tests_rechaza_presupuestos_y_codigos_ambiguos(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            for timeout in (True, 0, -1, float("inf"), "1"):
                with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                    mc.ejecutar_tests(SIEMPRE_PASA, raiz, timeout=timeout)
            for codigos in ({0}, {True}, {1.5}):
                with self.subTest(codigos=codigos), self.assertRaises(ValueError):
                    mc.ejecutar_tests(
                        SIEMPRE_PASA, raiz, timeout=1, codigos_fallo_tests=codigos)
            for limite in (True, 0, -1, 1.5):
                with self.subTest(limite=limite), self.assertRaises(ValueError):
                    mc.ejecutar_tests(
                        SIEMPRE_PASA, raiz, timeout=1, limite_salida=limite)

            vacio = mc.ejecutar_tests([], raiz, timeout=1)
            self.assertEqual(vacio.estado, mc.EstadoTests.ERROR_ARNES)
            self.assertIsNone(vacio.codigo_salida)
            self.assertIn("vacío", vacio.stderr)

    def test_el_limite_de_captura_es_inclusivo(self) -> None:
        for limite, esperado in ((3, False), (2, True)):
            salida, estado = [], {}
            mc._leer_acotado(io.BytesIO(b"abc"), limite, salida, estado)
            with self.subTest(limite=limite):
                self.assertEqual(b"".join(salida), b"abc"[:limite])
                self.assertIs(estado["truncado"], esperado)

        class CanalPorBloques:
            def __init__(self):
                self.bloques = iter((b"a", b"b", b""))
                self.cerrado = False

            def read(self, _cantidad):
                return next(self.bloques)

            def close(self):
                self.cerrado = True

        canal = CanalPorBloques()
        salida, estado = [], {}
        mc._leer_acotado(canal, 1, salida, estado)
        self.assertEqual(salida, [b"a"])
        self.assertIs(estado["truncado"], True)
        self.assertTrue(canal.cerrado)

    def test_los_limites_minimos_validos_se_aceptan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            resultado = mc.ejecutar_tests(
                [sys.executable, "-c", "print('x', end='')"],
                raiz, timeout=1, limite_salida=1)
            self.assertTrue(resultado.pasaron)
            self.assertEqual(resultado.stdout, "x")
            evidencia = mc._correr_en_raiz(
                raiz, [], SIEMPRE_PASA, limite_diagnostico=1)
            self.assertTrue(evidencia["corrida_mutacion"][0]["baseline_verde"])

    def test_una_ronda_mutante_rechaza_cache_preexistente_por_defecto(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "__pycache__").mkdir()
            with self.assertRaises(mc.CacheNoLimpio):
                mc._ejecutar_ronda(
                    SIEMPRE_PASA, raiz, timeout=1,
                    codigos_fallo_tests={1}, etapa="mutante")
            self.assertFalse((raiz / "__pycache__").exists())

    def test_el_diagnostico_conserva_limites_y_marcas_de_captura(self) -> None:
        limpio = mc.ResultadoTests(mc.EstadoTests.TESTS_FALLARON, 1, stdout="abc")
        self.assertEqual(mc._diagnostico(limpio, 3), ("abc", False))
        self.assertEqual(mc._diagnostico(limpio, 2), ("ab\n… salida truncada …", True))
        for stdout_truncado, stderr_truncado in ((True, False), (False, True)):
            resultado = mc.ResultadoTests(
                mc.EstadoTests.TESTS_FALLARON, 1, stdout="abc",
                stdout_truncado=stdout_truncado, stderr_truncado=stderr_truncado)
            diagnostico, truncado = mc._diagnostico(resultado, 3)
            self.assertTrue(truncado)
            self.assertEqual(diagnostico, "abc\n… salida acotada durante la ejecución …")
        self.assertEqual(
            mc._diagnostico(mc.ResultadoTests(mc.EstadoTests.ERROR_ARNES, 2), 99),
            ("(sin salida diagnóstica)", False))

    def test_json_canonico_huella_y_manifiesto_son_deterministas(self) -> None:
        datos = {"b": 1, "a": "ñ"}
        canonico = '{"a":"ñ","b":1}'
        self.assertEqual(mc._json_canonico(datos), canonico)
        self.assertEqual(mc._huella_json(datos), mc._huella_json({"a": "ñ", "b": 1}))
        self.assertNotEqual(mc._huella_json(datos), mc._huella_json({"a": "ñ", "b": 2}))
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "uno" / "dos" / "estado.json"
            mc._escribir_manifiesto(ruta, datos)
            self.assertEqual(ruta.read_text(encoding="utf-8"), canonico + "\n")

    def test_00_los_tests_corren_en_su_propia_sesion_para_poder_matar_el_grupo(self) -> None:
        """`start_new_session=True` es lo que vuelve al hijo líder de su grupo, y sin eso los
        `os.killpg` de `_terminar_proceso` no alcanzan a los nietos: un mutante que lo apaga deja
        procesos huérfanos y la ronda entera se va a **timeout**.

        Se afirma sobre la llamada, no sobre el comportamiento, justamente por eso: comprobarlo de
        verdad exigiría colgar el arnés, y un timeout no mata a nadie — el mutante sobreviviría
        inconcluso. Acá el fallo es inmediato y del test.
        """
        with mock.patch.object(mc.subprocess, "Popen") as popen:
            # Streams REALES: los lectores corren en hilos hasta EOF, y un `Mock` no llega nunca —
            # el `join()` colgaría el test en vez de fallarlo.
            popen.return_value.stdout = io.BytesIO(b"")
            popen.return_value.stderr = io.BytesIO(b"")
            popen.return_value.wait.return_value = 0
            with tempfile.TemporaryDirectory() as d:
                mc.ejecutar_tests(["true"], Path(d), timeout=5)

        self.assertTrue(popen.called)
        self.assertIs(popen.call_args.kwargs.get("start_new_session"), True)

    def test_terminar_proceso_aplica_escalado_y_esperas_explicitas(self) -> None:
        proceso = mock.Mock(pid=123)
        proceso.wait.side_effect = [
            subprocess.TimeoutExpired("arnes", mc.ESPERA_TERMINACION_SUAVE),
            None,
        ]
        with mock.patch.object(mc.os, "killpg") as killpg:
            mc._terminar_proceso(proceso)
        self.assertEqual(
            killpg.call_args_list,
            [mock.call(123, signal.SIGTERM), mock.call(123, mc.SENAL_SONDEO_GRUPO),
             mock.call(123, signal.SIGKILL)])
        self.assertEqual(
            proceso.wait.call_args_list,
            [mock.call(timeout=mc.ESPERA_TERMINACION_SUAVE),
             mock.call(timeout=mc.ESPERA_TERMINACION_FORZADA)])

    def test_ejecutar_tests_distingue_fallo_error_y_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            fallo = mc.ejecutar_tests(SIEMPRE_FALLA, raiz, timeout=1)
            error = mc.ejecutar_tests(SIEMPRE_ERROR_ARNES, raiz, timeout=1)
            timeout = mc.ejecutar_tests(SIEMPRE_DUERME, raiz, timeout=0.05)
            duerme_con_diagnostico = [
                sys.executable, "-c",
                "import sys,time; print('antes',flush=True); "
                "print('detalle',file=sys.stderr,flush=True); time.sleep(30)",
            ]
            timeout_con_salida = mc.ejecutar_tests(
                duerme_con_diagnostico, raiz, timeout=0.05)

        self.assertEqual(fallo.estado.value, "tests_fallaron")
        self.assertEqual(error.estado.value, "error_arnes")
        self.assertEqual(timeout.estado.value, "timeout")
        self.assertIn("antes", timeout_con_salida.salida)
        self.assertIn("detalle", timeout_con_salida.salida)

    def test_la_salida_del_subproceso_esta_acotada_mientras_se_drena(self) -> None:
        comando = [
            sys.executable, "-c",
            "import sys; print('x' * 10000); print('y' * 10000, file=sys.stderr)",
        ]
        with tempfile.TemporaryDirectory() as d:
            resultado = mc.ejecutar_tests(
                comando, Path(d), timeout=1, limite_salida=128)
        self.assertTrue(resultado.pasaron)
        self.assertLessEqual(len(resultado.stdout.encode()), 128)
        self.assertLessEqual(len(resultado.stderr.encode()), 128)
        self.assertTrue(resultado.stdout_truncado)
        self.assertTrue(resultado.stderr_truncado)

    def test_timeout_mata_tambien_un_nieto_que_ignora_SIGTERM(self) -> None:
        import os
        import time
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            pid = raiz / "nieto.pid"
            hijo = (
                "import os,signal,time; from pathlib import Path; "
                "signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                f"Path({str(pid)!r}).write_text(str(os.getpid())); time.sleep(30)"
            )
            comando = [
                sys.executable, "-c",
                f"import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',{hijo!r}]); "
                "time.sleep(30)",
            ]
            # 0.2s alcanzaba en una máquina de desarrollo pero no en un runner de CI
            # compartido: hay que arrancar DOS intérpretes anidados antes de que el nieto
            # escriba su pid, y bajo carga esa carrera se perdía antes de spawnear nada.
            resultado = mc.ejecutar_tests(comando, raiz, timeout=1.5)
            self.assertTrue(pid.exists())
            nieto = int(pid.read_text(encoding="utf-8"))
            limite = time.monotonic() + 2
            while time.monotonic() < limite:
                try:
                    os.kill(nieto, 0)
                except ProcessLookupError:
                    break
                time.sleep(0.02)
            else:
                self.fail("el nieto del arnés quedó vivo después del timeout")
        self.assertTrue(resultado.timeout)

    def test_importar_el_modulo_no_reemplaza_handlers_de_senal(self) -> None:
        codigo = (
            "import signal,sys; "
            "antes={s:signal.getsignal(s) for s in (signal.SIGTERM,signal.SIGINT,signal.SIGHUP)}; "
            f"sys.path.insert(0,{str(RAIZ)!r}); import perfiles.python.mutacion_codigo; "
            "despues={s:signal.getsignal(s) for s in antes}; "
            "raise SystemExit(0 if antes == despues else 1)"
        )
        resultado = subprocess.run([sys.executable, "-c", codigo])
        self.assertEqual(resultado.returncode, 0)

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
