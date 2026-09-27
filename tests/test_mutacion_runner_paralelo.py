"""Tests para el runner paralelo de mutación de código y selección de tests.

Cubre y mata los sobrevivientes identificados en SOBREVIVIENTES-RUNNER.txt:
- perfiles/python/mutacion_codigo.py: _comando_para_tests_seleccionados
- perfiles/python/mutacion_codigo.py: _correr_en_raiz
- perfiles/python/mutacion_codigo.py: correr (paralelismo, cobertura y selección)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import perfiles.python.mutacion_codigo as mc
from perfiles.python.mutacion_codigo import (
    _comando_para_tests_seleccionados,
    _correr_en_raiz,
    correr,
    sitios_de,
    EquivalenteInvalido,
    LineaBaseFallida,
)


class ComandoParaTestsSeleccionadosTests(unittest.TestCase):
    def test_611_comparador_lt_a_lte(self) -> None:
        """Línea 611: if idx + 1 < len(comando) (Lt -> LtE)."""
        cmd = [sys.executable, "tools/ejecutar_suite_mutacion.py", "--inicio"]
        res = _comando_para_tests_seleccionados(cmd, Path("/tmp"), ["test_1"])
        self.assertIsNotNone(res)
        self.assertNotIn("--inicio", res)

    def test_611_constante_1_a_2(self) -> None:
        """Línea 611: if idx + 1 < len(comando) (1 -> 2)."""
        cmd = [sys.executable, "tools/ejecutar_suite_mutacion.py", "--inicio", "tests"]
        res = _comando_para_tests_seleccionados(cmd, Path("/tmp"), ["test_1"])
        self.assertIsNotNone(res)
        self.assertIn("--inicio", res)
        self.assertEqual(res[res.index("--inicio") + 1], "tests")

    def test_603_comparador_in_a_notin(self) -> None:
        """Línea 603: if 'ejecutar_suite_mutacion.py' in str(arg) (In -> NotIn)."""
        cmd = [sys.executable, "tools/ejecutar_suite_mutacion.py"]
        res = _comando_para_tests_seleccionados(cmd, Path("/tmp"), ["test_1"])
        self.assertIsNotNone(res)
        self.assertEqual(res[1], "tools/ejecutar_suite_mutacion.py")

    def test_612_constante_1_a_2(self) -> None:
        """Línea 612: inicio_args = ['--inicio', comando[idx + 1]] (1 -> 2)."""
        cmd = [sys.executable, "tools/ejecutar_suite_mutacion.py", "--inicio", "tests", "otro"]
        res = _comando_para_tests_seleccionados(cmd, Path("/tmp"), ["test_1"])
        self.assertIsNotNone(res)
        self.assertEqual(res[res.index("--inicio") + 1], "tests")

    def test_613_constante_0_a_1(self) -> None:
        """Línea 613: cmd = [comando[0], runner, ...] (0 -> 1)."""
        cmd = [sys.executable, "tools/ejecutar_suite_mutacion.py"]
        res = _comando_para_tests_seleccionados(cmd, Path("/tmp"), ["test_1"])
        self.assertIsNotNone(res)
        self.assertEqual(res[0], sys.executable)


class CorrerEnRaizTests(unittest.TestCase):
    SIEMPRE_PASA = [sys.executable, "-c", "raise SystemExit(0)"]

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temp_dir.name)
        self.obj = self.raiz / "m.py"
        self.obj.write_text("def f(x):\n    return x > 0\n", encoding="utf-8")
        self.sitios = sitios_de(self.obj, self.raiz)
        # Sitios generados: retorno (línea 2), comparador (línea 2), constante (línea 2)
        self.sitio_constante = next(s for s in self.sitios if s.operador == "constante")
        self.sitio_retorno = next(s for s in self.sitios if s.operador == "retorno")
        self.sitio_comparador = next(s for s in self.sitios if s.operador == "comparador")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_941_negacion_se_borra_not(self) -> None:
        """Línea 941: if not isinstance(razon, str) or not razon.strip()."""
        # Con razón válida no vacía, no debe levantar EquivalenteInvalido.
        # El mutante sin 'not' evalúa True con isinstance(razon, str) y falla.
        ev = _correr_en_raiz(
            self.raiz, [self.obj], self.SIEMPRE_PASA,
            equivalentes={self.sitio_constante.id: "razon valida no vacia"},
        )
        self.assertEqual(len(ev["mutante_equivalente"]), 1)

    def test_956_comparador_in_a_notin(self) -> None:
        """Línea 956: lambda s: s.id in filtro_sitios (In -> NotIn)."""
        ev = _correr_en_raiz(
            self.raiz, [self.obj], self.SIEMPRE_PASA,
            filtro_sitios={self.sitio_constante.id},
        )
        self.assertEqual([m["id"] for m in ev["mutante"]], [self.sitio_constante.id])

    def test_959_comparador_eq_a_noteq(self) -> None:
        """Línea 959: if sum(...) == 0 (Eq -> NotEq)."""
        ev = _correr_en_raiz(
            self.raiz, [self.obj], self.SIEMPRE_PASA,
            filtro_sitios={self.sitio_constante.id},
        )
        self.assertEqual(len(ev["mutante"]), 1)

    def test_959_constante_0_a_1(self) -> None:
        """Línea 959: if sum(...) == 0 (0 -> 1)."""
        ev = _correr_en_raiz(
            self.raiz, [self.obj], self.SIEMPRE_PASA,
            filtro_sitios={self.sitio_constante.id},
        )
        self.assertEqual(len(ev["mutante"]), 1)

    def test_962_comparador_in_a_notin(self) -> None:
        """Línea 962: any('ejecutar_suite_mutacion.py' in str(arg) for arg in comando) (In -> NotIn)."""
        runner = self.raiz / "ejecutar_suite_mutacion.py"
        runner.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--solo-prioridad' in sys.argv:\n"
            "    sys.exit(1)\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        runner.chmod(0o755)
        mapa = {"m.py": {"2": ["test_1"]}}
        ev = _correr_en_raiz(self.raiz, [self.obj], [str(runner)], mapa_cobertura=mapa)
        self.assertTrue(all(m["tests_fallaron"] for m in ev["mutante"]))

    def test_975_constante_0_a_1(self) -> None:
        """Línea 975: ejecutados_ahora = 0 (0 -> 1)."""
        ev = _correr_en_raiz(
            self.raiz, [self.obj], self.SIEMPRE_PASA,
            filtro_sitios={self.sitio_constante.id},
        )
        # 1 línea base + 1 mutante ejecutado = 2
        self.assertEqual(ev["corrida_mutacion"][0]["rondas_ejecutadas"], 2)

    def test_990_booleano_and_a_or(self) -> None:
        """Línea 990: tests_del_sitio = get(str(linea)) or get(linea) (and <-> or)."""
        mapa = {"m.py": {"2": ["test_sel"]}}
        cmd_sel = lambda tests, raiz: [
            sys.executable, "-c", "import sys; sys.exit(1 if 'test_sel' in sys.argv else 0)"
        ] + tests
        ev = _correr_en_raiz(
            self.raiz, [self.obj], self.SIEMPRE_PASA,
            mapa_cobertura=mapa, comando_seleccion=cmd_sel,
        )
        self.assertTrue(ev["mutante"][0]["tests_fallaron"])

    def test_1029_comparador_in_a_notin(self) -> None:
        """Línea 1029: 'equivalente_declarado': sitio.id in equivalentes (In -> NotIn)."""
        ev = _correr_en_raiz(
            self.raiz, [self.obj], self.SIEMPRE_PASA,
            equivalentes={self.sitio_constante.id: "razon valida"},
        )
        self.assertEqual([m["id"] for m in ev["mutante_equivalente"]], [self.sitio_constante.id])

    def test_1036_booleano_and_a_or(self) -> None:
        """Línea 1036: if (resultado.error_arnes or resultado.timeout) and primer_inconcluso is None."""
        ev = _correr_en_raiz(self.raiz, [self.obj], self.SIEMPRE_PASA)
        self.assertEqual(ev["corrida_mutacion"][0]["primer_inconcluso_id"], "")

    def test_1051_negacion_se_borra_not(self) -> None:
        """Línea 1051: reales = [f for f in publicadas if not f['equivalente_declarado']]."""
        ev = _correr_en_raiz(
            self.raiz, [self.obj], self.SIEMPRE_PASA,
            equivalentes={self.sitio_constante.id: "razon valida"},
        )
        ids_reales = [m["id"] for m in ev["mutante"]]
        self.assertNotIn(self.sitio_constante.id, ids_reales)
        self.assertEqual(len(ids_reales), 2)

    def test_1066_constante_false_a_true(self) -> None:
        """Línea 1066: salida_truncada = False cuando no hay fallos (False -> True)."""
        ev = _correr_en_raiz(self.raiz, [self.obj], self.SIEMPRE_PASA)
        self.assertFalse(ev["corrida_mutacion"][0]["primer_fallo_salida_truncada"])

    def test_1080_constante_false_a_true(self) -> None:
        """Línea 1080: inconcluso_truncado = False cuando no hay inconclusos (False -> True)."""
        ev = _correr_en_raiz(self.raiz, [self.obj], self.SIEMPRE_PASA)
        self.assertFalse(ev["corrida_mutacion"][0]["primer_inconcluso_salida_truncada"])

    def test_1095_constante_1_a_2(self) -> None:
        """Línea 1095: 'rondas_cache_verificadas': 1 + ejecutados_ahora (1 -> 2)."""
        ev = _correr_en_raiz(
            self.raiz, [self.obj], self.SIEMPRE_PASA,
            filtro_sitios={self.sitio_constante.id},
        )
        self.assertEqual(ev["corrida_mutacion"][0]["rondas_cache_verificadas"], 2)

    def test_1094_constante_1_a_2(self) -> None:
        """Línea 1094: 'rondas_ejecutadas': 1 + ejecutados_ahora (1 -> 2)."""
        ev = _correr_en_raiz(
            self.raiz, [self.obj], self.SIEMPRE_PASA,
            filtro_sitios={self.sitio_constante.id},
        )
        self.assertEqual(ev["corrida_mutacion"][0]["rondas_ejecutadas"], 2)


class CorrerParaleloYSeleccionTests(unittest.TestCase):
    SIEMPRE_PASA = [sys.executable, "-c", "raise SystemExit(0)"]

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.raiz = Path(self.temp_dir.name)
        self.obj = self.raiz / "m.py"
        self.obj.write_text("def f(x):\n    return x > 0\n", encoding="utf-8")
        self.sitios = sitios_de(self.obj, self.raiz)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_1128_booleano_and_a_or(self) -> None:
        """Línea 1128: if isinstance(paralelo, bool) or not isinstance(paralelo, int) or paralelo < 1."""
        with self.assertRaises(ValueError) as ctx:
            correr(self.raiz, [self.obj], self.SIEMPRE_PASA, paralelo=True)
        self.assertIn("paralelo tiene que ser un entero positivo", str(ctx.exception))

    def test_1200_constante_1_a_2(self) -> None:
        """Línea 1200: n_trabajadores = min(paralelo, len(pendientes)) if pendientes else 1 (1 -> 2)."""
        mani = self.raiz / "manifiesto.json"
        correr(self.raiz, [self.obj], self.SIEMPRE_PASA, manifiesto=mani)
        with mock.patch("perfiles.python.mutacion_codigo._copiar_proyecto", wraps=mc._copiar_proyecto) as mock_cp:
            ev = correr(
                self.raiz, [self.obj], self.SIEMPRE_PASA,
                manifiesto=mani, reanudar=True, paralelo=1,
            )
            self.assertEqual(mock_cp.call_count, 1)

    def test_1221_comparador_is_a_isnot(self) -> None:
        """Línea 1221: if mapa_cobertura is None and es_suite_mutacion (Is -> IsNot)."""
        tools = self.raiz / "tools"
        tools.mkdir()
        runner = tools / "ejecutar_suite_mutacion.py"
        runner.write_text(
            "import sys, json\n"
            "from pathlib import Path\n"
            "if '--guardar-cobertura' not in sys.argv:\n"
            "    sys.exit(99)\n"
            "idx = sys.argv.index('--guardar-cobertura')\n"
            "Path(sys.argv[idx + 1]).write_text('{}', encoding='utf-8')\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        cmd = [sys.executable, str(runner)]
        ev = correr(self.raiz, [self.obj], cmd, paralelo=1, mapa_cobertura=None)
        self.assertTrue(ev["corrida_mutacion"][0]["baseline_verde"])

    def test_1236_booleano_and_a_or_tiempo(self) -> None:
        """Línea 1236: if mapa_cobertura is None and ruta_cobertura.exists() (and <-> or).

        Test rápido que falla inmediatamente si el mutante sobreescribe el mapa del caller.
        """
        tools = self.raiz / "tools"
        tools.mkdir()
        runner = tools / "ejecutar_suite_mutacion.py"
        runner.write_text(
            "import sys, json\n"
            "from pathlib import Path\n"
            "base_dir = Path.cwd().parent.parent\n"
            "ruta_cobertura = base_dir / 'cobertura.json'\n"
            "if '--solo-prioridad' in sys.argv:\n"
            "    if 'test_caller' in sys.argv:\n"
            "        sys.exit(1)\n"
            "    sys.exit(0)\n"
            "else:\n"
            "    ruta_cobertura.write_text(json.dumps({'m.py': {'2': ['test_disco']}}), encoding='utf-8')\n"
            "    sys.exit(0)\n",
            encoding="utf-8",
        )
        mapa = {"m.py": {"2": ["test_caller"]}}
        cmd = [sys.executable, str(runner)]
        ev = correr(self.raiz, [self.obj], cmd, paralelo=1, mapa_cobertura=mapa)
        self.assertTrue(ev["mutante"][0]["murio"])

    def test_1236_comparador_is_a_isnot_tiempo(self) -> None:
        """Línea 1236: if mapa_cobertura is None and ruta_cobertura.exists() (Is -> IsNot).

        Test rápido que falla inmediatamente si el mutante no carga la cobertura de disco.
        """
        tools = self.raiz / "tools"
        tools.mkdir()
        runner = tools / "ejecutar_suite_mutacion.py"
        runner.write_text(
            "import sys, json\n"
            "from pathlib import Path\n"
            "if '--guardar-cobertura' in sys.argv:\n"
            "    idx = sys.argv.index('--guardar-cobertura')\n"
            "    Path(sys.argv[idx + 1]).write_text(json.dumps({'m.py': {'2': ['test_disco']}}), encoding='utf-8')\n"
            "    sys.exit(0)\n"
            "if '--solo-prioridad' in sys.argv and 'test_disco' in sys.argv:\n"
            "    sys.exit(1)\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        cmd = [sys.executable, str(runner)]
        ev = correr(self.raiz, [self.obj], cmd, paralelo=1, mapa_cobertura=None)
        self.assertTrue(ev["mutante"][0]["murio"])

    def test_1272_booleano_and_a_or(self) -> None:
        """Línea 1272: tests_del_sitio = get(str(linea)) or get(linea) (and <-> or)."""
        tools = self.raiz / "tools"
        tools.mkdir()
        runner = tools / "ejecutar_suite_mutacion.py"
        runner.write_text(
            "import sys\n"
            "if '--solo-prioridad' in sys.argv and 'test_cadena' in sys.argv:\n"
            "    sys.exit(1)\n"
            "sys.exit(0)\n",
            encoding="utf-8",
        )
        mapa = {"m.py": {"2": ["test_cadena"]}}
        cmd = [sys.executable, str(runner)]
        ev = correr(self.raiz, [self.obj], cmd, paralelo=1, mapa_cobertura=mapa)
        self.assertTrue(ev["mutante"][0]["murio"])


if __name__ == "__main__":
    unittest.main()
