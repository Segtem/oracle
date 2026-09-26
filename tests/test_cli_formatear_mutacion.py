"""Tests de mutación para formatear y despacho en tools/cli.py."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo.proyecto import Proyecto
from tools import cli


MEDIDA_CANONICA = (
    'medida demo.prueba:\n'
    '    de pieza p\n'
    '    resumen contar(1)\n'
    '    umbral <= 0 segun contrato porque "r"\n'
    '    alcance "a"\n'
)

MACRO_CANONICA = (
    'defmacro sin-fallas(id, relacion, alias, predicado, porque, segun, ambito, alcance):\n'
    '    ninguno $id:\n'
    '        de $relacion $alias\n'
    '        donde $predicado\n'
    '        umbral <= 0 segun $segun porque $porque\n'
    '        ambito $ambito\n'
    '        alcance $alcance\n'
)

MEDIDA_CON_MACRO = (
    'sin-fallas demo.todo_ok:\n'
    '    de item i\n'
    '    donde i.ok == false\n'
    '    umbral <= 0 segun contrato porque "un item falso invalida la entrega entera"\n'
    '    ambito universal\n'
    '    alcance "NO ve items que nadie declaró"\n'
)

CASO_CANONICO = (
    'caso 001-demo:\n'
    '    fecha: "2026-08-24"\n'
    '    origen:\n'
    '        repo: "Segtem/oracle"\n'
    '        commit: "c81a87c"\n'
    '    titulo: "demo"\n'
    '    etiqueta: falso_verde\n'
    '    sintoma:\n'
    '        sintoma\n'
    '    como_se_detecto: mutacion\n'
    '    medida: demo.prueba\n'
    '    evidencia:\n'
    '        paso: clave(t); t\n'
    '            0\n'
    '    leccion:\n'
    '        leccion\n'
)


class CliFormatearMutacionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        with redirect_stdout(io.StringIO()):
            cli.cmd_init(str(self.raiz), [])
        self.proy = Proyecto(self.raiz)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _crear_macro_y_medida(self) -> tuple[Path, Path]:
        d_macros = self.raiz / "macros"
        d_macros.mkdir(exist_ok=True)
        ruta_macro = d_macros / "sin-fallas.oracle"
        ruta_macro.write_text(MACRO_CANONICA, encoding="utf-8")

        d_cat = self.raiz / "catalogos" / "demo"
        d_cat.mkdir(parents=True, exist_ok=True)
        ruta_medida = d_cat / "demo.todo_ok.oracle"
        ruta_medida.write_text(MEDIDA_CON_MACRO, encoding="utf-8")
        return ruta_macro, ruta_medida

    def _crear_caso(self) -> Path:
        d_corpus = self.raiz / "corpus"
        d_corpus.mkdir(exist_ok=True)
        ruta_caso = d_corpus / "demo.caso"
        ruta_caso.write_text(CASO_CANONICO, encoding="utf-8")
        return ruta_caso

    # -------------------------------------------------------------------------
    # Grupo 1: Líneas 901-923 de tools/cli.py (_formatear_uno)
    # -------------------------------------------------------------------------

    def test_mutante_901_19_booleano_medida_con_macro_resuelve_macro(self) -> None:
        # Mata tools/cli.py:901:19:booleano (and ↔ or)
        # Si ruta.suffix == ".oracle" or any(...), cualquier medida ordinaria (.oracle)
        # se clasifica erróneamente como es_macro=True, dejando macros=None.
        # Al formatear una medida que usa macros del proyecto, falla la resolución.
        _, ruta_medida = self._crear_macro_y_medida()
        with redirect_stdout(io.StringIO()):
            ret = cli.cmd_formatear(self.proy, str(ruta_medida))
        self.assertEqual(ret, 0)

    def test_mutante_901_19_comparador_formatear_macro_no_invoca_macros_del_proyecto(self) -> None:
        # Mata tools/cli.py:901:19:comparador (Eq → NotEq)
        # Si ruta.suffix != ".oracle", la macro .oracle queda con es_macro=False e invocaría
        # macros_del_proyecto(proy).
        ruta_macro, _ = self._crear_macro_y_medida()
        with mock.patch("tools.cli.macros_del_proyecto", side_effect=ValueError("no invocar")):
            with redirect_stdout(io.StringIO()):
                ret = cli.cmd_formatear(self.proy, str(ruta_macro))
        self.assertEqual(ret, 0)

    def test_mutante_903_68_negacion_formatear_macro_no_invoca_macros_del_proyecto(self) -> None:
        # Mata tools/cli.py:903:68:negacion (se borra el `not`)
        # Al quitar el not, solo las líneas que empiezan con # pasan al filtro, dejando es_macro=False.
        ruta_macro, _ = self._crear_macro_y_medida()
        with mock.patch("tools.cli.macros_del_proyecto", side_effect=ValueError("no invocar")):
            with redirect_stdout(io.StringIO()):
                ret = cli.cmd_formatear(self.proy, str(ruta_macro))
        self.assertEqual(ret, 0)

    def test_mutante_904_46_booleano_formatear_caso_no_invoca_macros_del_proyecto(self) -> None:
        # Mata tools/cli.py:904:46:booleano (and ↔ or)
        # En ruta.suffix == ".oracle" or not es_macro, para un .caso es_macro es False,
        # haciendo que evalúe macros_del_proyecto(proy).
        ruta_caso = self._crear_caso()
        with mock.patch("tools.cli.macros_del_proyecto", side_effect=ValueError("no invocar")):
            with redirect_stdout(io.StringIO()):
                ret = cli.cmd_formatear(self.proy, str(ruta_caso))
        self.assertEqual(ret, 0)

    def test_mutante_904_46_comparador_medida_con_macro_recibe_macros(self) -> None:
        # Mata tools/cli.py:904:46:comparador (Eq → NotEq)
        # Si ruta.suffix != ".oracle", una medida .oracle no cargaría macros del proyecto.
        _, ruta_medida = self._crear_macro_y_medida()
        with redirect_stdout(io.StringIO()):
            ret = cli.cmd_formatear(self.proy, str(ruta_medida))
        self.assertEqual(ret, 0)

    def test_mutante_904_75_negacion_medida_con_macro_recibe_macros(self) -> None:
        # Mata tools/cli.py:904:75:negacion (se borra el `not`)
        # Si 'and es_macro', una medida ordinaria (es_macro=False) recibe macros=None.
        _, ruta_medida = self._crear_macro_y_medida()
        with redirect_stdout(io.StringIO()):
            ret = cli.cmd_formatear(self.proy, str(ruta_medida))
        self.assertEqual(ret, 0)

    def test_mutante_908_12_retorno_formatear_forma_unica_devuelve_cero(self) -> None:
        # Mata tools/cli.py:908:12:retorno (return <algo> → return None)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.cmd_formatear(self.proy, str(ruta_caso))
        self.assertIs(ret, 0)

    def test_mutante_908_19_constante_formatear_forma_unica_devuelve_cero(self) -> None:
        # Mata tools/cli.py:908:19:constante (0 → 1)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.cmd_formatear(self.proy, str(ruta_caso))
        self.assertEqual(ret, 0)

    def test_mutante_923_8_retorno_formatear_error_devuelve_uno(self) -> None:
        # Mata tools/cli.py:923:8:retorno (return <algo> → return None)
        ruta = self.raiz / "catalogos" / "demo.oracle"
        ruta.write_text("medida rota\n    invalida\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            ret = cli.cmd_formatear(self.proy, str(ruta))
        self.assertIs(ret, 1)

    def test_mutante_923_15_constante_formatear_error_devuelve_uno(self) -> None:
        # Mata tools/cli.py:923:15:constante (1 → 2)
        ruta = self.raiz / "catalogos" / "demo.oracle"
        ruta.write_text("medida rota\n    invalida\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            ret = cli.cmd_formatear(self.proy, str(ruta))
        self.assertEqual(ret, 1)

    # -------------------------------------------------------------------------
    # Grupo 2: Línea 995 de tools/cli.py (cmd_test)
    # -------------------------------------------------------------------------

    def test_mutante_995_15_constante_cmd_test_desformateado_devuelve_uno(self) -> None:
        # Mata tools/cli.py:995:15:constante (1 → 2)
        ruta = self.raiz / "catalogos" / "demo.oracle"
        ruta.write_text(MEDIDA_CANONICA.replace("medida demo.prueba", "medida   demo.prueba"), encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            ret = cli.cmd_test(self.proy, [])
        self.assertEqual(ret, 1)

    # -------------------------------------------------------------------------
    # Grupo 3: Líneas 1590-1598 de tools/cli.py (subcomando formatear en main)
    # -------------------------------------------------------------------------

    def test_mutante_1590_36_comparador_main_formatear_acepta_argumentos_distintos_de_rapido(self) -> None:
        # Mata tools/cli.py:1590:36:comparador (NotEq → Eq)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso)])
        self.assertEqual(ret, 0)

    def test_mutante_1591_11_booleano_main_formatear_rechaza_repetir_escribir_con_ruta(self) -> None:
        # Mata tools/cli.py:1591:11:booleano (and ↔ or)
        ruta_caso = self._crear_caso()
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = cli.main(["formatear", str(ruta_caso), "--escribir", "--escribir"])
        self.assertEqual(ret, 1)
        self.assertIn("uso: oracle formatear", buf.getvalue())

    def test_mutante_1591_11_comparador_main_formatear_uno_o_dos_argumentos_no_falla_uso(self) -> None:
        # Mata tools/cli.py:1591:11:comparador (NotIn → In)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso)])
        self.assertEqual(ret, 0)

    def test_mutante_1591_29_constante_main_formatear_un_argumento_valido(self) -> None:
        # Mata tools/cli.py:1591:29:constante (1 → 2)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso)])
        self.assertEqual(ret, 0)

    def test_mutante_1591_32_constante_main_formatear_dos_argumentos_con_escribir(self) -> None:
        # Mata tools/cli.py:1591:32:constante (2 → 3)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso), "--escribir"])
        self.assertEqual(ret, 0)

    def test_mutante_1591_42_booleano_main_formatear_argumento_posicional_no_es_rechazado_por_flag(self) -> None:
        # Mata tools/cli.py:1591:42:booleano (and ↔ or)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso)])
        self.assertEqual(ret, 0)

    def test_mutante_1591_65_comparador_main_formatear_acepta_flag_escribir(self) -> None:
        # Mata tools/cli.py:1591:65:comparador (NotEq → Eq)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso), "--escribir"])
        self.assertEqual(ret, 0)

    def test_mutante_1591_101_comparador_main_formatear_permite_un_escribir(self) -> None:
        # Mata tools/cli.py:1591:101:comparador (Gt → GtE)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso), "--escribir"])
        self.assertEqual(ret, 0)
    def test_mutante_1593_12_retorno_main_formatear_sin_argumentos_retorna_uno(self) -> None:
        # Mata tools/cli.py:1593:12:retorno (return <algo> → return None)
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear"])
        self.assertIs(ret, 1)

    def test_mutante_1593_19_constante_main_formatear_sin_argumentos_retorna_uno(self) -> None:
        # Mata tools/cli.py:1593:19:constante (1 → 2)
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear"])
        self.assertEqual(ret, 1)

    def test_mutante_1594_36_comparador_main_formatear_extrae_ruta_no_escribir(self) -> None:
        # Mata tools/cli.py:1594:36:comparador (NotEq → Eq)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso)])
        self.assertEqual(ret, 0)

    def test_mutante_1595_11_comparador_main_formatear_con_una_ruta_continua(self) -> None:
        # Mata tools/cli.py:1595:11:comparador (NotEq → Eq)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso)])
        self.assertEqual(ret, 0)

    def test_mutante_1595_25_constante_main_formatear_con_una_ruta_continua(self) -> None:
        # Mata tools/cli.py:1595:25:constante (1 → 2)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso)])
        self.assertEqual(ret, 0)

    def test_mutante_1597_12_retorno_main_formatear_solo_escribir_retorna_uno(self) -> None:
        # Mata tools/cli.py:1597:12:retorno (return <algo> → return None)
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", "--escribir"])
        self.assertIs(ret, 1)

    def test_mutante_1597_19_constante_main_formatear_solo_escribir_retorna_uno(self) -> None:
        # Mata tools/cli.py:1597:19:constante (1 → 2)
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", "--escribir"])
        self.assertEqual(ret, 1)

    def test_mutante_1598_8_retorno_main_formatear_retorna_codigo_de_cmd_formatear(self) -> None:
        # Mata tools/cli.py:1598:8:retorno (return <algo> → return None)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso)])
        self.assertIs(ret, 0)

    def test_mutante_1598_41_constante_main_formatear_usa_indice_cero_de_rutas(self) -> None:
        # Mata tools/cli.py:1598:41:constante (0 → 1)
        ruta_caso = self._crear_caso()
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_caso)])
        self.assertEqual(ret, 0)

    def test_mutante_1598_54_comparador_main_formatear_sin_escribir_no_modifica_archivo(self) -> None:
        # Mata tools/cli.py:1598:54:comparador (In → NotIn)
        ruta_medida = self.raiz / "catalogos" / "demo.oracle"
        texto_desformateado = "# comentario\n" + MEDIDA_CANONICA.replace("medida demo.prueba", "medida   demo.prueba")
        ruta_medida.write_text(texto_desformateado, encoding="utf-8")
        with redirect_stdout(io.StringIO()):
            ret = cli.main(["formatear", str(ruta_medida)])
        self.assertEqual(ret, 0)
        self.assertEqual(ruta_medida.read_text(encoding="utf-8"), texto_desformateado)
