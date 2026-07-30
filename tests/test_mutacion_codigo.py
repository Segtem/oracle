"""Tests del mutador de CÓDIGO. Existe porque su primera corrida delató que no los tenía: de 88
mutantes vivos, 57 eran de este módulo.

La propiedad que más importa acá no es la corrección de los operadores: es que **el archivo original
se restaure siempre**. Esta herramienta escribe sobre fuentes reales.
"""

from __future__ import annotations

import subprocess
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

    def test_produce_hechos_con_la_forma_que_espera_la_medida(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            ev = mc.correr(raiz, [objetivo], PASA_SOLO_CON_ORIGINAL)
        self.assertEqual(sorted(ev), ["corrida_mutacion", "mutante", "mutante_equivalente"])
        self.assertEqual(sorted(ev["mutante"][0]),
                         ["apunta_a", "cambio", "equivalente_declarado", "id", "murio",
                          "razon_equivalente"])
        corrida = ev["corrida_mutacion"][0]
        self.assertTrue(corrida["baseline_verde"])
        self.assertTrue(corrida["bytecode_frio"])
        self.assertEqual(corrida["resultado_confiable"],
                         corrida["baseline_verde"] and corrida["bytecode_frio"])

    def test_un_equivalente_declarado_sale_de_los_mutantes_y_lleva_su_razon(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz, objetivo = self._entorno(d)
            todos = mc.correr(raiz, [objetivo], SIEMPRE_PASA)["mutante"]
            elegido = todos[0]["id"]
            ev = mc.correr(raiz, [objetivo], SIEMPRE_PASA, {elegido: "porque sí, con razón escrita"})

        self.assertNotIn(elegido, [m["id"] for m in ev["mutante"]])
        eq = next(m for m in ev["mutante_equivalente"] if m["id"] == elegido)
        self.assertEqual(eq["razon_equivalente"], "porque sí, con razón escrita")

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
            time.sleep(2.5)                       # que llegue a mutar el primer sitio
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

    def test_correr_tests_lee_el_codigo_de_salida(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(mc.correr_tests(SIEMPRE_PASA, Path(d)))
            self.assertFalse(mc.correr_tests(SIEMPRE_FALLA, Path(d)))


if __name__ == "__main__":
    unittest.main()
