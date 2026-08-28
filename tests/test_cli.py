"""Regresiones fail-closed del comando unificado `oracle`."""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo.proyecto import Proyecto
from tools import cli

RAIZ = Path(__file__).resolve().parents[1]


class CliTestCase(unittest.TestCase):
    """Ayudas compartidas; no hereda casos concretos entre grupos de pruebas."""

    @staticmethod
    def _callado(fn, *args, **kw):
        """Corre una función del CLI sin dejar su salida en la de la suite.

        Los tests capturaban `cli.main` pero llamaban `cmd_init`, `cmd_nueva` y `cmd_caso` DIRECTO,
        así que la ayuda del comando terminaba mezclada con el resumen de la corrida:
        `python -m unittest -q | tail -3` mostraba «Creá una medida» en vez de «OK». Un test que
        ensucia la salida hace ilegible justo lo que uno mira cuando algo falla.
        """
        salida = io.StringIO()
        with redirect_stdout(salida):
            resultado = fn(*args, **kw)
        return resultado, salida.getvalue()


class OracleCliTests(CliTestCase):
    def _cmd_test_oracle_simulado(self, *extras: str, unitarios: int = 0,
                                  mutacion_codigo: int = 0, catalogo: bool = True,
                                  casos: bool = True, json_igual: bool = True,
                                  texto_igual: bool = True, fallas_docs=()):
        from tools import cifras, metamorficas, mutar_codigo, trazar

        def correr_unitarios(proy):
            print("UNITARIOS OK" if unitarios == 0 else "UNITARIOS ✗")
            return unitarios

        def correr_mutacion_codigo(proy, args):
            print("MUTACIÓN DE CÓDIGO OK" if mutacion_codigo == 0 else "MUTACIÓN DE CÓDIGO ✗")
            return mutacion_codigo

        salida = io.StringIO()
        with (mock.patch.object(cli, "_ejecutar_unitarios", side_effect=correr_unitarios) as m_unit,
              mock.patch.object(cli, "cargar_catalogo", return_value=(
                  {"meta.medida": object()} if catalogo else {})),
              mock.patch.object(cli, "rutas_de_corpus",
                                return_value=(
                                    [RAIZ / "corpus" / "meta" / "001.caso"] if casos else [])),
              mock.patch.object(cli.corpus, "verificar", return_value=(
                  [], [{"id": "001"}] if casos else [])),
              mock.patch.object(cli.sintaxis, "verificar_catalogo",
                                return_value={"json_igual": json_igual,
                                              "texto_igual": texto_igual,
                                              "medidas": 1, "macros": 0, "casos": 1}),
              mock.patch.object(cli.sintaxis, "verificar_documentos",
                                return_value={"fallas": list(fallas_docs)}),
              mock.patch.object(cli.aceptacion, "_ejecutar", return_value=0),
              mock.patch.object(cli.diferencial, "_ejecutar", return_value=0),
              mock.patch.object(trazar, "main", return_value=0),
              mock.patch.object(metamorficas, "main", return_value=0),
              mock.patch.object(cifras, "main", return_value=0),
              mock.patch.object(cli.mutar, "_ejecutar", return_value=0) as m_mutar,
              mock.patch.object(mutar_codigo, "_ejecutar",
                                side_effect=correr_mutacion_codigo) as m_mutar_codigo,
              redirect_stdout(salida)):
            rc = cli.main(["test", "--proyecto", str(RAIZ), *extras])
        return rc, salida.getvalue(), m_unit, m_mutar, m_mutar_codigo


    def test_ayuda_y_sin_argumentos_devuelven_cero(self) -> None:
        salida_help = io.StringIO()
        with redirect_stdout(salida_help):
            rc_help = cli.main(["--help"])
        self.assertEqual(rc_help, 0)
        self.assertIn("oracle init", salida_help.getvalue())
        self.assertIn("oracle test", salida_help.getvalue())

        salida_vacia = io.StringIO()
        with redirect_stdout(salida_vacia):
            rc_vacia = cli.main([])
        self.assertEqual(rc_vacia, 0)
        self.assertEqual(salida_help.getvalue(), salida_vacia.getvalue())

    def test_init_crea_estructura_valida_y_test_la_acepta(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            destino = Path(td) / "nuevo-proyecto"
            salida_init = io.StringIO()
            with redirect_stdout(salida_init):
                rc_init = cli.main(["init", str(destino)])
            self.assertEqual(rc_init, 0)
            self.assertTrue((destino / "catalogos").is_dir())
            self.assertTrue((destino / "corpus").is_dir())
            self.assertTrue((destino / "diferencial").is_dir())
            self.assertTrue((destino / "oracle.json").is_file())

            # oracle test sobre el proyecto recién inicializado debe ser verde
            salida_test = io.StringIO()
            with redirect_stdout(salida_test):
                rc_test = cli.main(["test", "--proyecto", str(destino)])
            self.assertEqual(rc_test, 0)
            self.assertIn("VEREDICTO: VERDE", salida_test.getvalue())
            self.assertIn("proyecto vacío", salida_test.getvalue())

    def test_init_acepta_proyecto_es_idempotente_y_escribe_json_legible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            destino = Path(td) / "por-bandera"

            rc_primero, _ = self._callado(
                cli.main, ["init", "--proyecto", str(destino)])
            rc_segundo, _ = self._callado(
                cli.main, ["init", "--proyecto", str(destino)])

            self.assertEqual(rc_primero, 0)
            self.assertEqual(rc_segundo, 0)
            esperado = json.dumps({
                "esquema": cli.ESQUEMA_PROYECTO,
                "catalogo_base": True,
                "perfiles": [],
            }, indent=2) + "\n"
            self.assertEqual((destino / "oracle.json").read_text(encoding="utf-8"), esperado)

    def test_init_falla_cerrado_si_proyecto_no_tiene_ruta(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            rc, _ = self._callado(cli.main, ["init", "--proyecto"])

        self.assertEqual(rc, 1)
        self.assertIn("--proyecto necesita una ruta", stderr.getvalue())

    def test_init_propaga_error_de_escritura_como_uno(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stderr = io.StringIO()
            with (mock.patch.object(Path, "mkdir", side_effect=PermissionError("solo lectura")),
                  redirect_stderr(stderr)):
                rc = cli.cmd_init(str(Path(td) / "sin-permiso"), [])

        self.assertEqual(rc, 1)
        self.assertIn("No se pudo inicializar", stderr.getvalue())

    def test_wrappers_de_archivo_resuelven_relativos_y_propagan_resultado(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.cmd_init, str(raiz), [])
            proy = Proyecto(raiz)
            relativa = Path("catalogos/demo/demo.prueba.oracle")
            archivo = raiz / relativa
            archivo.parent.mkdir(parents=True)
            archivo.write_text("contenido observado", encoding="utf-8")

            with mock.patch.object(cli.medida, "revisar", return_value=1) as revisar:
                self.assertEqual(cli.cmd_revisar(proy, str(relativa), []), 1)
                revisar.assert_called_once_with(proy, archivo)
            with mock.patch.object(cli.medida, "probar", return_value=1) as probar:
                self.assertEqual(cli.cmd_probar(proy, str(relativa), "item: id"), 1)
                probar.assert_called_once_with(proy, archivo, "item: id")
            with mock.patch.object(cli.medida, "expandir_archivo", return_value=1) as expandir:
                self.assertEqual(cli.cmd_expandir(proy, str(relativa)), 1)
                self.assertEqual(expandir.call_args.args[0], archivo)

    def test_wrappers_de_archivo_ausente_devuelven_uno(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy = Proyecto(Path(td))
            for comando, args in (
                (cli.cmd_revisar, (proy, "ausente.oracle", [])),
                (cli.cmd_probar, (proy, "ausente.oracle", "item: id")),
                (cli.cmd_expandir, (proy, "ausente.oracle")),
            ):
                rc, salida = self._callado(comando, *args)
                self.assertEqual(rc, 1)
                self.assertIn("no existe", salida)

            rc_convertir, salida_convertir = self._callado(
                cli.cmd_convertir, proy, "ausente.oracle")
            self.assertEqual(rc_convertir, 1)
            self.assertIn("no existe", salida_convertir)

    def test_convertir_resuelve_relativo_y_conserva_unicode(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.cmd_init, str(raiz), [])
            relativa = Path("catalogos/demo/demo.acento.oracle")
            fuente = raiz / relativa
            fuente.parent.mkdir(parents=True)
            fuente.write_text(
                "ninguno demo.acento:\n"
                "    de item i\n"
                "    donde i.mal == true\n"
                "    umbral <= 0 segun contrato porque \"ningún ítem puede estar mal\"\n"
                "    alcance \"sólo ve el campo mal\"\n",
                encoding="utf-8")

            rc, salida = self._callado(cli.cmd_convertir, Proyecto(raiz), str(relativa))

        self.assertEqual(rc, 0)
        self.assertIn("ningún ítem", salida)
        self.assertNotIn("\\u00", salida)

    def test_convertir_caso_es_json_legible_y_extension_ausente_nombra_archivo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.cmd_init, str(raiz), [])
            caso = raiz / "caso.caso"
            caso.write_text(
                "caso 001-acento:\n"
                "    fecha: \"2026-08-28\"\n"
                "    origen:\n"
                "        repo: \"demo\"\n"
                "        commit: \"local\"\n"
                "    procedencia: observada\n"
                "    titulo: \"Ítem inválido\"\n"
                "    etiqueta: falso_verde\n"
                "    sintoma:\n"
                "        Pasó un ítem inválido.\n"
                "    como_se_detecto: persona\n"
                "    medida: demo.acento\n"
                "    evidencia:\n"
                "        item: mal\n"
                "            true\n"
                "    leccion:\n"
                "        Debe ponerse rojo.\n",
                encoding="utf-8")
            rc_caso, salida_caso = self._callado(
                cli.cmd_convertir, Proyecto(raiz), str(caso))

            desconocido = raiz / "misterioso"
            desconocido.write_text("", encoding="utf-8")
            rc_desconocido, salida_desconocida = self._callado(
                cli.cmd_convertir, Proyecto(raiz), str(desconocido))

        self.assertEqual(rc_caso, 0)
        self.assertTrue(salida_caso.startswith("{\n  \"id\""), salida_caso)
        self.assertIn("Ítem inválido", salida_caso)
        self.assertNotIn("\\u00", salida_caso)
        self.assertEqual(rc_desconocido, 1)
        self.assertIn("misterioso", salida_desconocida)

    def test_ejecutar_unitarios_conserva_opciones_salida_y_codigo(self) -> None:
        resultado = subprocess.CompletedProcess(
            args=cli.COMANDO_UNITARIOS, returncode=1,
            stdout="SALIDA UNITARIA\n", stderr="ERROR UNITARIO\n")
        with mock.patch.object(cli.subprocess, "run", return_value=resultado) as ejecutar:
            rc, salida = self._callado(cli._ejecutar_unitarios, Proyecto(RAIZ))

        self.assertEqual(rc, 1)
        self.assertIn("SALIDA UNITARIA", salida)
        self.assertIn("ERROR UNITARIO", salida)
        self.assertIn("UNITARIOS ✗", salida)
        ejecutar.assert_called_once_with(
            cli.COMANDO_UNITARIOS, cwd=RAIZ, capture_output=True, text=True)

    def test_test_rechaza_niveles_incompatibles_y_estructura_invalida(self) -> None:
        rc_niveles, salida_niveles = self._callado(
            cli.cmd_test, Proyecto(RAIZ), ["--rapido", "--todo"])
        with tempfile.TemporaryDirectory() as td:
            rc_estructura, salida_estructura = self._callado(
                cli.cmd_test, Proyecto(Path(td)), ["--rapido"])

        self.assertEqual(rc_niveles, 1)
        self.assertIn("nivel de verificación inválido", salida_niveles)
        self.assertEqual(rc_estructura, 1)
        self.assertIn("estructura de proyecto inválida", salida_estructura)

    def test_test_distingue_escalar_no_confiada_invalida_y_catalogo_invalido(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.cmd_init, str(raiz), [])
            (raiz / "escalares.py").write_text("esto no es python\n", encoding="utf-8")
            proy = Proyecto(raiz)

            rc_sin, salida_sin = self._callado(cli.cmd_test, proy, ["--rapido"])
            rc_con, salida_con = self._callado(
                cli.cmd_test, proy, ["--rapido", "--confiar-escalares"])
            (raiz / "escalares.py").unlink()
            with mock.patch.object(cli, "cargar_catalogo", side_effect=ValueError("roto")):
                rc_catalogo, salida_catalogo = self._callado(
                    cli.cmd_test, proy, ["--rapido"])

        self.assertEqual(rc_sin, 1)
        self.assertIn("escalares.py no confiado", salida_sin)
        self.assertNotIn("no pudo cargarse", salida_sin)
        self.assertEqual(rc_con, 1)
        self.assertIn("escalares.py no pudo cargarse", salida_con)
        self.assertEqual(rc_catalogo, 1)
        self.assertIn("catálogo no pudo cargarse", salida_catalogo)

    def test_caso_generar_propaga_el_resultado(self) -> None:
        proy = Proyecto(RAIZ)
        with mock.patch.object(cli.corpus, "generar", return_value=1) as generar:
            rc = cli.cmd_caso_generar(proy, "demo.medida", ["--una-bandera"])

        self.assertEqual(rc, 1)
        generar.assert_called_once_with(proy, "demo.medida", ["--una-bandera"])

    def test_escalares_externas_se_omiten_sin_confianza_y_propagan_resultado(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.cmd_init, str(raiz), [])
            (raiz / "escalares.py").write_text("raise RuntimeError('no ejecutar')\n",
                                                encoding="utf-8")
            proy = Proyecto(raiz)
            with mock.patch.object(cli.medida, "escalares", return_value=1) as escalares:
                rc = cli.cmd_escalares(proy, [])

        self.assertEqual(rc, 1)
        escalares.assert_called_once_with(proy, externas_omitidas=True)

    def test_escalares_sin_archivo_entran_al_contexto_y_propagan_resultado(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.cmd_init, str(raiz), [])
            proy = Proyecto(raiz)
            with mock.patch.object(cli.medida, "escalares", return_value=1) as escalares:
                rc = cli.cmd_escalares(proy, [])

        self.assertEqual(rc, 1)
        escalares.assert_called_once_with(proy)

    def test_escalares_invalidas_con_confianza_devuelven_uno(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.cmd_init, str(raiz), [])
            (raiz / "escalares.py").write_text("esto no es python\n", encoding="utf-8")
            rc, salida = self._callado(
                cli.cmd_escalares, Proyecto(raiz), ["--confiar-escalares"])

        self.assertEqual(rc, 1)
        self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS", salida)

    def test_test_distingue_no_aplica_de_falla(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])

            # 1. Sin fixtures diferenciales -> no aplica (salteado)
            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main(["test", "--proyecto", str(raiz)])
            self.assertEqual(rc, 0)
            self.assertIn("DIFERENCIAL: salteado", salida.getvalue())

            # 2. Con fixture malformado -> falla
            (raiz / "diferencial" / "roto.json").write_text("{}", encoding="utf-8")
            salida_falla = io.StringIO()
            with redirect_stdout(salida_falla):
                rc_falla = cli.main(["test", "--proyecto", str(raiz)])
            self.assertEqual(rc_falla, 1)
            self.assertIn("DIFERENCIAL ✗", salida_falla.getvalue())
            self.assertIn("VEREDICTO: ROJO", salida_falla.getvalue())

    def test_rapido_saltea_mutacion_y_lo_informa_en_el_veredicto(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])

            # Creamos una medida y un caso válidos
            proy = Proyecto(raiz)
            _, _ = self._callado(cli.cmd_nueva, proy, "demo.prueba")
            medida_path = raiz / "catalogos" / "demo" / "demo.prueba.oracle"
            medida_path.write_text(
                "ninguno demo.prueba:\n"
                "    de item x\n"
                "    donde x.mal == true\n"
                "    umbral <= 0 segun contrato porque \"ningun item puede estar mal\"\n"
                "    alcance \"NO ve otros items\"\n",
                encoding="utf-8",
            )
            _, _ = self._callado(cli.cmd_caso, proy, "demo/001-rojo")
            caso_path = raiz / "corpus" / "demo" / "001-rojo.caso"
            caso_path.write_text(
                "caso 001-rojo:\n"
                "    fecha: \"2026-08-26\"\n"
                "    origen:\n"
                "        repo: \"demo\"\n"
                "        commit: \"local\"\n"
                "    procedencia: observada\n"
                "    titulo: \"item defectuoso\"\n"
                "    etiqueta: falso_verde\n"
                "    sintoma:\n"
                "        item mal marcado\n"
                "    como_se_detecto: mutacion\n"
                "    medida: demo.prueba\n"
                "    evidencia:\n"
                "        item: mal\n"
                "            true\n"
                "    leccion:\n"
                "        activa la medida\n",
                encoding="utf-8",
            )

            # Con --rapido: saltea mutación y lo dice en el veredicto
            salida_rapido = io.StringIO()
            with redirect_stdout(salida_rapido):
                rc_rapido = cli.main(["test", "--proyecto", str(raiz), "--rapido"])
            self.assertEqual(rc_rapido, 0)
            self.assertIn("MUTACIÓN: salteada por --rapido", salida_rapido.getvalue())
            self.assertIn(
                "VEREDICTO: VERDE (se salteó: mutación de medidas (--rapido))",
                salida_rapido.getvalue())

    def test_test_por_omision_en_oracle_corre_unitarios_y_nombra_codigo_salteado(self) -> None:
        rc, salida, m_unit, m_mutar, m_mutar_codigo = self._cmd_test_oracle_simulado()

        self.assertEqual(rc, 0)
        m_unit.assert_called_once()
        m_mutar.assert_called_once()
        m_mutar_codigo.assert_not_called()
        self.assertIn("MUTACIÓN DE CÓDIGO: salteada", salida)
        self.assertIn("oracle test --todo", salida)
        self.assertIn(
            "VEREDICTO: VERDE (se salteó: mutación de código (corré `oracle test --todo`))",
            salida)

    def test_test_todo_en_oracle_corre_mutacion_de_codigo_y_no_declara_omisiones(self) -> None:
        rc, salida, m_unit, m_mutar, m_mutar_codigo = self._cmd_test_oracle_simulado("--todo")

        self.assertEqual(rc, 0)
        m_unit.assert_called_once()
        m_mutar.assert_called_once()
        m_mutar_codigo.assert_called_once()
        self.assertNotIn("se salteó", salida)
        self.assertIn("VEREDICTO: VERDE (todo: todas las verificaciones en regla", salida)

    def test_rapido_en_oracle_nombra_todo_lo_salteado(self) -> None:
        rc, salida, m_unit, m_mutar, m_mutar_codigo = self._cmd_test_oracle_simulado("--rapido")

        self.assertEqual(rc, 0)
        m_unit.assert_not_called()
        m_mutar.assert_not_called()
        m_mutar_codigo.assert_not_called()
        self.assertIn("UNITARIOS: salteados por --rapido", salida)
        self.assertIn("MUTACIÓN: salteada por --rapido", salida)
        self.assertIn("MUTACIÓN DE CÓDIGO: salteada por --rapido", salida)
        self.assertIn("tests unitarios (--rapido)", salida)
        self.assertIn("mutación de medidas (--rapido)", salida)
        self.assertIn("mutación de código (corré `oracle test --todo`)", salida)

    def test_un_fallo_de_unitarios_pone_rojo_el_veredicto(self) -> None:
        rc, salida, m_unit, _, _ = self._cmd_test_oracle_simulado(unitarios=1)

        self.assertEqual(rc, 1)
        m_unit.assert_called_once()
        self.assertIn("UNITARIOS ✗", salida)
        self.assertIn("VEREDICTO: ROJO (falló: unitarios)", salida)

    def test_sintaxis_exige_que_ambas_direcciones_sean_iguales(self) -> None:
        for json_igual, texto_igual in ((False, True), (True, False)):
            with self.subTest(json_igual=json_igual, texto_igual=texto_igual):
                rc, salida, *_ = self._cmd_test_oracle_simulado(
                    "--rapido", json_igual=json_igual, texto_igual=texto_igual)
                self.assertEqual(rc, 1)
                self.assertIn("SINTAXIS ✗", salida)
                self.assertIn("VEREDICTO: ROJO", salida)

    def test_falla_de_documentacion_no_se_tapa_con_sintaxis_ok(self) -> None:
        rc, salida, *_ = self._cmd_test_oracle_simulado(
            "--rapido", fallas_docs=("bloque vencido",))

        self.assertEqual(rc, 1)
        self.assertIn("SINTAXIS ✗ — 1 falla(s) en documentación", salida)
        self.assertNotIn("SINTAXIS OK", salida)

    def test_catalogo_sin_casos_falla_y_ausencia_total_salte_acceptacion(self) -> None:
        rc_catalogo, salida_catalogo, *_ = self._cmd_test_oracle_simulado(
            "--rapido", casos=False)
        rc_vacio, salida_vacia, *_ = self._cmd_test_oracle_simulado(
            "--rapido", catalogo=False, casos=False)

        self.assertEqual(rc_catalogo, 1)
        self.assertIn("ACEPTACIÓN ✗ — sin casos", salida_catalogo)
        self.assertEqual(rc_vacio, 0)
        self.assertIn("SINTAXIS: salteado", salida_vacia)
        self.assertIn("ACEPTACIÓN: salteado", salida_vacia)

    def test_medida_sin_casos_falla_en_test(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])
            proy = Proyecto(raiz)
            _, _ = self._callado(cli.cmd_nueva, proy, "demo.sola")
            (raiz / "catalogos" / "demo" / "demo.sola.oracle").write_text(
                "ninguno demo.sola:\n"
                "    de item x\n"
                "    donde x.mal == true\n"
                "    umbral <= 0 segun contrato porque \"defensa\"\n"
                "    alcance \"alcance\"\n",
                encoding="utf-8",
            )
            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main(["test", "--proyecto", str(raiz), "--rapido"])
            self.assertEqual(rc, 1)
            self.assertIn("ACEPTACIÓN ✗", salida.getvalue())
            self.assertIn("VEREDICTO: ROJO", salida.getvalue())

    def test_nueva_y_caso_validan_identificadores(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])
            proy = Proyecto(raiz)

            # Identificadores inválidos
            for mid_invalido in ("medida_sin_punto", "MAYUS.nombre", "123.456", "../escape"):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.cmd_nueva(proy, mid_invalido)
                self.assertEqual(rc, 1)

            for cid_invalido in ("sin_grupo", "grupo/sin_numero", "grupo/MAYUS", "grupo/../escape"):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.cmd_caso(proy, cid_invalido)
                self.assertEqual(rc, 1)

    def test_escalares_externas_exigen_confianza_en_test_y_revisar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])
            (raiz / "escalares.py").write_text(
                "from nucleo.algebra import escalar\n"
                "@escalar('es_malo')\n"
                "def es_malo(fila): return fila['mal']\n",
                encoding="utf-8",
            )
            (raiz / "catalogos" / "demo").mkdir(parents=True, exist_ok=True)
            medida_path = raiz / "catalogos" / "demo" / "demo.udf.oracle"
            medida_path.write_text(
                "ninguno demo.udf:\n"
                "    de item x\n"
                "    donde es_malo(x) == true\n"
                "    umbral <= 0 segun contrato porque \"defensa\"\n"
                "    alcance \"alcance\"\n",
                encoding="utf-8",
            )
            salida_sin = io.StringIO()
            with redirect_stdout(salida_sin):
                rc_sin = cli.main(["test", "--proyecto", str(raiz)])
            self.assertEqual(rc_sin, 1)
            self.assertIn("--confiar-escalares", salida_sin.getvalue())

            salida_con = io.StringIO()
            with redirect_stdout(salida_con):
                rc_con = cli.main([
                    "test", "--proyecto", str(raiz), "--confiar-escalares", "--rapido",
                ])
            self.assertEqual(rc_con, 1)
            self.assertIn("ACEPTACIÓN ✗", salida_con.getvalue())
            self.assertNotIn("CATÁLOGO INVÁLIDO", salida_con.getvalue())

            salida_rev_sin = io.StringIO()
            with redirect_stdout(salida_rev_sin):
                rc_rev_sin = cli.main(["revisar", str(medida_path), "--proyecto", str(raiz)])
            self.assertEqual(rc_rev_sin, 1)
            self.assertIn("--confiar-escalares", salida_rev_sin.getvalue())

    def test_ejecucion_como_subproceso(self) -> None:
        r = subprocess.run(
            [sys.executable, str(RAIZ / "tools" / "cli.py"), "--help"],
            cwd=RAIZ, capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("oracle init", r.stdout)

    def test_wheel_instalado_trae_datos_y_ejecuta_oracle_test(self) -> None:
        with tempfile.TemporaryDirectory(prefix="oracle-wheel-test-") as td:
            temporal = Path(td)
            fuente = temporal / "fuente"
            shutil.copytree(
                RAIZ,
                fuente,
                ignore=shutil.ignore_patterns(
                    ".git", "build", "dist", "*.egg-info", "__pycache__", "*.pyc"),
            )
            ruedas = temporal / "ruedas"
            ruedas.mkdir()
            env = os.environ.copy()
            env.pop("ORACLE_PROYECTO", None)
            env.pop("PYTHONPATH", None)
            env["PYTHONDONTWRITEBYTECODE"] = "1"

            wheel = subprocess.run(
                [
                    sys.executable, "-m", "pip", "wheel", "--no-deps",
                    "--no-build-isolation", "--wheel-dir", str(ruedas), str(fuente),
                ],
                cwd=temporal, env=env, capture_output=True, text=True,
            )
            self.assertEqual(wheel.returncode, 0, wheel.stdout + wheel.stderr)
            encontradas = tuple(ruedas.glob("oracle_metalenguaje-*.whl"))
            self.assertEqual(len(encontradas), 1, str(encontradas))

            with zipfile.ZipFile(encontradas[0]) as paquete:
                nombres = set(paquete.namelist())
            esperados = {
                "oracle_metalenguaje/tools/cli.py",
                "oracle_metalenguaje/nucleo/aislamiento/escalares.py",
                "oracle_metalenguaje/nucleo/macros/ninguno.oracle",
                "oracle_metalenguaje/nucleo/macros/ninguno-par.oracle",
                "oracle_metalenguaje/nucleo/macros/ninguno-requiere.oracle",
                "oracle_metalenguaje/nucleo/macros/peor.oracle",
                "oracle_metalenguaje/catalogos/meta/meta.toda_medida_esta_fijada.oracle",
                "oracle_metalenguaje/perfiles/python/catalogos/proceso/"
                "proceso.arnes_con_bytecode_frio.oracle",
            }
            self.assertFalse(esperados - nombres)
            genericos = ("nucleo/", "catalogos/", "perfiles/", "tools/")
            self.assertFalse([nombre for nombre in nombres if nombre.startswith(genericos)])

            entorno = temporal / "entorno"
            venv.EnvBuilder(with_pip=True).create(entorno)
            python = entorno / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
            instalar = subprocess.run(
                [str(python), "-m", "pip", "install", "--no-deps", str(encontradas[0])],
                cwd=temporal, env=env, capture_output=True, text=True,
            )
            self.assertEqual(instalar.returncode, 0, instalar.stdout + instalar.stderr)

            binarios = entorno / ("Scripts" if sys.platform == "win32" else "bin")
            oracle = binarios / ("oracle.exe" if sys.platform == "win32" else "oracle")
            cwd_vacio = temporal / "cwd-vacio"
            cwd_vacio.mkdir()
            proyecto = temporal / "proyecto"

            init = subprocess.run(
                [str(oracle), "init", str(proyecto)],
                cwd=cwd_vacio, env=env, capture_output=True, text=True,
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            vacio = subprocess.run(
                [str(oracle), "test", "--proyecto", str(proyecto)],
                cwd=cwd_vacio, env=env, capture_output=True, text=True,
            )
            self.assertEqual(vacio.returncode, 0, vacio.stdout + vacio.stderr)
            self.assertIn("VEREDICTO: VERDE", vacio.stdout)
            self.assertIn("proyecto vacío", vacio.stdout)

            dominio = proyecto / "catalogos" / "demo"
            dominio.mkdir()
            (dominio / "demo.instalado.oracle").write_text(
                "ninguno demo.instalado:\n"
                "    de item i\n"
                "    donde i.mal == true\n"
                "    umbral <= 0 segun contrato porque \"ningun item malo pasa\"\n"
                "    alcance \"NO ve campos distintos de mal\"\n",
                encoding="utf-8",
            )
            casos = proyecto / "corpus" / "demo"
            casos.mkdir()
            (casos / "001-rojo.caso").write_text(
                "caso 001-rojo:\n"
                "    fecha: \"2026-08-26\"\n"
                "    origen:\n"
                "        repo: \"temporal\"\n"
                "        commit: \"sin-commit\"\n"
                "    procedencia: observada\n"
                "    titulo: \"item malo detectado\"\n"
                "    etiqueta: falso_verde\n"
                "    sintoma:\n"
                "        Un item malo tiene que poner roja la medida instalada.\n"
                "    como_se_detecto: mutacion\n"
                "    medida: demo.instalado\n"
                "    evidencia:\n"
                "        item: id, mal\n"
                "            \"a\", true\n"
                "    leccion:\n"
                "        La macro estándar tiene que estar empaquetada.\n",
                encoding="utf-8",
            )
            con_macro = subprocess.run(
                [str(oracle), "test", "--proyecto", str(proyecto), "--rapido"],
                cwd=cwd_vacio, env=env, capture_output=True, text=True,
            )
            self.assertEqual(con_macro.returncode, 0, con_macro.stdout + con_macro.stderr)
            self.assertIn("SINTAXIS OK", con_macro.stdout)
            self.assertIn("ACEPTACIÓN", con_macro.stdout)
            self.assertIn("VEREDICTO: VERDE", con_macro.stdout)


class InitDejaLasGuardasPuestasTests(CliTestCase):
    """Lo más importante que escribe `init` es `catalogo_base`, y faltaba.

    Sin él un proyecto carga SÓLO sus propias medidas y se queda sin las universales: nadie comprueba
    que un umbral traiga defensa, que una medida declare `alcance`, que toda medida esté fijada por
    un caso, ni que un caso se ponga como su etiqueta declara.

    El escenario que lo destapó está fijado abajo, y es el que importa para que una persona pueda
    AUDITAR lo que escribió un modelo: una medida con el predicado invertido —selecciona lo que está
    bien en vez de lo que ofende— más un caso que la declara `falso_verde`. Sin guardas eso daba
    «ACEPTACIÓN ✓ · VEREDICTO: VERDE».
    """

    MEDIDA_INVERTIDA = (
        "ninguno tareas.vencida_sin_dueno:\n"
        "    de tarea t\n"
        "    donde t.vencida == true y t.asignada == true\n"
        '    umbral <= 0 segun contrato porque "una tarea vencida sin dueño no la va a hacer nadie"\n'
        '    alcance "ve el par vencida+sin-dueño y nada más"\n')

    CASO = (
        "caso 001-vencida-sin-nadie:\n"
        '    fecha: "2026-08-26"\n'
        "    origen:\n"
        '        repo: "yo/tablero"\n'
        '        commit: "x"\n'
        "    procedencia: observada\n"
        '    titulo: "Una tarea vencida sin dueño pasó desapercibida"\n'
        "    etiqueta: falso_verde\n"
        "    sintoma:\n"
        "        El tablero no mostraba las tareas sin asignar.\n"
        "    como_se_detecto: persona\n"
        "    medida: tareas.vencida_sin_dueno\n"
        "    evidencia:\n"
        "        tarea: id, vencida, asignada\n"
        '            "t-1", true, false\n'
        '            "t-2", false, true\n'
        "    leccion:\n"
        "        Una tarea sin dueño no la ve nadie.\n")

    def test_init_declara_el_catalogo_base(self) -> None:
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d) / "nuevo"
            self._callado(cli.cmd_init, str(raiz), [])
            datos = json.loads((raiz / "oracle.json").read_text(encoding="utf-8"))
            self.assertIs(datos.get("catalogo_base"), True,
                          "sin `catalogo_base` el proyecto nace sin ninguna medida universal")

    def test_un_proyecto_recien_creado_ve_las_medidas_universales(self) -> None:
        """No alcanza con que la bandera esté escrita: tiene que traer medidas de verdad."""
        import tempfile
        from nucleo.medida import cargar_catalogo
        from nucleo.proyecto import Proyecto, catalogos_a_cargar, macros_del_proyecto
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d) / "nuevo"
            self._callado(cli.cmd_init, str(raiz), [])
            proy = Proyecto(raiz)
            catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
            self.assertIn("meta.el_caso_se_pone_como_debe", catalogo)
            self.assertIn("meta.todo_umbral_declara_de_donde_sale", catalogo)

    def test_una_medida_invertida_con_su_caso_sale_ROJA(self) -> None:
        """El escenario de auditoría: un modelo escribe una medida al revés y su caso.

        Es la prueba de que una persona puede confiar en el veredicto sin releer cada predicado.
        """
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d) / "nuevo"
            self._callado(cli.cmd_init, str(raiz), [])
            medida = raiz / "catalogos" / "tareas" / "tareas.vencida_sin_dueno.oracle"
            medida.parent.mkdir(parents=True, exist_ok=True)
            medida.write_text(self.MEDIDA_INVERTIDA, encoding="utf-8")
            caso = raiz / "corpus" / "tareas" / "001-vencida-sin-nadie.caso"
            caso.parent.mkdir(parents=True, exist_ok=True)
            caso.write_text(self.CASO, encoding="utf-8")

            codigo, salida = self._callado(cli.main, ["test", "--rapido", "--proyecto", str(raiz)])
            self.assertEqual(codigo, 1, salida)
            self.assertIn("meta.el_caso_se_pone_como_debe", salida)
            self.assertIn("ROJO", salida)


class NounVerbCliTests(CliTestCase):
    def test_ayudas_de_sustantivos_devuelven_cero(self) -> None:
        for sust, verbos in (
            ("medida", ("nueva", "revisar", "listar", "expandir")),
            ("caso", ("nuevo", "listar")),
            ("proyecto", ("init", "test", "relaciones", "escalares")),
        ):
            rc, salida = self._callado(cli.main, [sust])
            self.assertEqual(rc, 0)
            self.assertIn(f"oracle {sust}", salida)
            for v in verbos:
                self.assertIn(v, salida)

            # También con --help
            rc_h, salida_h = self._callado(cli.main, [sust, "--help"])
            self.assertEqual(rc_h, 0)
            self.assertEqual(salida, salida_h)

    def test_verbos_desconocidos_fallan_y_muestran_disponibles(self) -> None:
        for sust, verbo_invalido, esperados in (
            ("medida", "borrar", ("nueva", "revisar", "listar", "expandir")),
            ("caso", "borrar", ("nuevo", "listar")),
            ("proyecto", "borrar", ("init", "test", "relaciones", "escalares")),
        ):
            rc, salida = self._callado(cli.main, [sust, verbo_invalido])
            self.assertEqual(rc, 1)
            self.assertIn(f"verbo desconocido para «{sust}»: {verbo_invalido}", salida)
            for v in esperados:
                self.assertIn(v, salida)

        # Subcomando desconocido plano
        rc_des, salida_des = self._callado(cli.main, ["desconocido"])
        self.assertEqual(rc_des, 1)
        self.assertIn("subcomando desconocido: desconocido", salida_des)

    def test_version_dice_las_tres_y_de_donde_sale(self) -> None:
        """Un binario que no sabe decir qué es se confunde con un CLI roto: pasó, y costó tiempo."""
        for bandera in ("--version", "-V", "version"):
            rc, salida = self._callado(cli.main, [bandera])
            self.assertEqual(rc, 0, bandera)
            self.assertIn("oracle 0.1.0", salida)
            self.assertIn("álgebra:", salida)
            self.assertIn("sintaxis:", salida)
            self.assertIn("corriendo desde:", salida)

    def test_la_version_del_paquete_es_la_del_nucleo(self) -> None:
        """`pyproject.toml` la lee de `nucleo/version.py`; si alguien la duplica, esto lo dice."""
        texto = (RAIZ / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('dynamic = ["version"]', texto)
        self.assertIn("nucleo.version.VERSION_DISTRIBUCION", texto)
        self.assertNotIn('\nversion = "', texto)

    def _proyecto_con_una_medida(self, raiz):
        self._callado(cli.main, ["proyecto", "init", str(raiz)])
        m = raiz / "catalogos" / "juego" / "juego.pieza_muy_alta.oracle"
        m.parent.mkdir(parents=True, exist_ok=True)
        m.write_text(
            "ninguno juego.pieza_muy_alta:\n"
            "    de pieza p\n"
            "    donde p.alto > 400.0\n"
            '    umbral <= 0 segun contrato porque "cuatro metros es el techo del set"\n'
            '    alcance "mira el alto declarado. NO mira la malla"\n',
            encoding="utf-8")
        return m

    def test_probar_corre_una_medida_sin_pasar_por_el_corpus(self) -> None:
        """El corte entre explorar y registrar: ver el veredicto sin redactar un caso de 11 campos."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            m = self._proyecto_con_una_medida(raiz)
            rc, salida = self._callado(cli.main, [
                "medida", "probar", str(m), "--con",
                'pieza: id, alto\n    "silla", 90.0\n    "columna", 450.0',
                "--proyecto", str(raiz)])
            self.assertEqual(rc, 0)
            self.assertIn("ROJO", salida)
            # Los testigos son las filas que ofenden, y se muestran: ahí está la lección.
            self.assertIn("columna", salida)
            self.assertNotIn("silla", salida.split("testigos")[1])
            self.assertIn("alcance:", salida)

    def test_probar_ubica_el_error_en_lo_que_escribio_quien_prueba(self) -> None:
        """La evidencia se envuelve en un caso sintético; la posición tiene que descontarlo.

        Sin descontar, quien escribe dos líneas recibe «línea 14»: una posición correcta respecto de
        un archivo que nunca vio. Un error que apunta a un lugar inexistente es peor que ninguno.
        """
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            m = self._proyecto_con_una_medida(raiz)
            rc, salida = self._callado(cli.main, [
                "medida", "probar", str(m), "--con", 'pieza: id, alto\n    "silla"',
                "--proyecto", str(raiz)])
            self.assertEqual(rc, 1)
            self.assertIn("línea 2", salida)
            self.assertNotIn("línea 14", salida)

    def test_probar_sin_evidencia_ensena_la_forma(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            m = self._proyecto_con_una_medida(raiz)
            rc, salida = self._callado(cli.main, ["medida", "probar", str(m),
                                                  "--proyecto", str(raiz)])
            self.assertEqual(rc, 1)
            self.assertIn("igual que en un caso del corpus", salida)

    def test_caso_nuevo_deriva_fecha_y_origen_del_repositorio(self) -> None:
        """Un dato que la máquina sabe no se le pide a una persona: 62 de 112 casos decían prosa."""
        import subprocess
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            subprocess.run(["git", "init", "-q", str(raiz)], check=True)
            subprocess.run(["git", "-C", str(raiz), "remote", "add", "origin",
                            "git@github.com:Alumno/taller.git"], check=True)
            (raiz / "a.txt").write_text("x", encoding="utf-8")
            subprocess.run(["git", "-C", str(raiz), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(raiz), "-c", "user.email=a@b", "-c", "user.name=a",
                            "commit", "-qm", "inicial"], check=True)
            self._callado(cli.main, ["proyecto", "init", str(raiz)])
            rc, salida = self._callado(cli.main, ["caso", "nuevo", "juego/001-prueba",
                                                  "--proyecto", str(raiz)])
            self.assertEqual(rc, 0)
            escrito = (raiz / "corpus" / "juego" / "001-prueba.caso").read_text(encoding="utf-8")
            self.assertIn('repo: "Alumno/taller"', escrito)
            self.assertNotIn('"COMMIT"', escrito)
            self.assertNotIn('"FECHA"', escrito)
            # Los dos juicios NO se derivan: procedencia y etiqueta las decide quien escribe.
            self.assertIn("# procedencia:", escrito)
            self.assertIn("etiqueta: ETIQUETA", escrito)

    def test_caso_nuevo_sin_git_falla_abierto(self) -> None:
        """Sin repositorio se dejan los marcadores. Negarse a crear el caso sería confundir dos
        cosas: el caso registra un hecho, no un commit."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.main, ["proyecto", "init", str(raiz)])
            rc, _salida = self._callado(cli.main, ["caso", "nuevo", "juego/001-prueba",
                                                   "--proyecto", str(raiz)])
            self.assertEqual(rc, 0)
            escrito = (raiz / "corpus" / "juego" / "001-prueba.caso").read_text(encoding="utf-8")
            self.assertIn('repo: "REPO"', escrito)
            self.assertNotIn('"FECHA"', escrito)   # la fecha sí se sabe siempre

    def test_alcance_derivado_dice_lo_que_la_medida_no_lee(self) -> None:
        """La mitad del `alcance` que se calcula: qué campos declarados no toca la medida.

        No se compara contra el `alcance` escrito —sería juzgar prosa contra estructura— sino que se
        muestra al lado, para que quien escribe decida si alguno debería mirarse.
        """
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            m = self._proyecto_con_una_medida(raiz)
            rel = raiz / "relaciones" / "pieza.json"
            rel.parent.mkdir(parents=True, exist_ok=True)
            rel.write_text(json.dumps([
                "relacion", "pieza",
                ["campos", ["campo", "id", "texto", "sin_unidad"],
                 ["campo", "alto", "flotante", "cm"],
                 ["campo", "yaw", "flotante", "grados"]],
                ["alcance", "lee el AABB declarado. NO lee la malla"]],
                ensure_ascii=False), encoding="utf-8")
            _rc, salida = self._callado(cli.main, [
                "medida", "probar", str(m), "--con", 'pieza: id, alto\n    "columna", 450.0',
                "--proyecto", str(raiz)])
            self.assertIn("de `pieza` NO lee: id, yaw", salida)
            self.assertNotIn("NO lee: id, alto", salida)

    def test_alcance_derivado_avisa_de_un_campo_leido_sin_declarar(self) -> None:
        """Pesa más que uno declarado y sin leer: o falta la declaración, o la medida lee humo."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            m = self._proyecto_con_una_medida(raiz)
            rel = raiz / "relaciones" / "pieza.json"
            rel.parent.mkdir(parents=True, exist_ok=True)
            rel.write_text(json.dumps([
                "relacion", "pieza",
                ["campos", ["campo", "id", "texto", "sin_unidad"]],
                ["alcance", "lee el id declarado"]], ensure_ascii=False), encoding="utf-8")
            _rc, salida = self._callado(cli.main, [
                "medida", "probar", str(m), "--con", 'pieza: id, alto\n    "columna", 450.0',
                "--proyecto", str(raiz)])
            self.assertIn("LEE campos que la relación no declara: alto", salida)

    def test_sin_relaciones_declaradas_no_se_inventa_un_alcance(self) -> None:
        """Que no haya declaraciones no significa que la medida lo vea todo: significa que nadie
        declaró qué hay para ver. La diferencia es la misma que entre adimensional y no derivable."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            m = self._proyecto_con_una_medida(raiz)
            _rc, salida = self._callado(cli.main, [
                "medida", "probar", str(m), "--con", 'pieza: id, alto\n    "columna", 450.0',
                "--proyecto", str(raiz)])
            self.assertNotIn("NO lee:", salida)
            self.assertNotIn("lee todos los campos", salida)

    def test_medida_listar_en_propio_oracle(self) -> None:
        rc, salida = self._callado(cli.main, ["medida", "listar", "--proyecto", str(RAIZ)])
        self.assertEqual(rc, 0)
        self.assertIn("CATÁLOGO (38 medidas", salida)
        # Las del perfil `python` no viven en `catalogos/`: se heredan, y se ven.
        self.assertIn("MEDIDAS HEREDADAS", salida)
        self.assertIn("proceso.modulo_alcanzable", salida)
        self.assertIn("meta.agrupar_no_agranda_la_relacion", salida)
        self.assertIn("umbral:", salida)
        self.assertIn("fijación:", salida)
        self.assertIn("alcance:", salida)
        self.assertIn("meta.el_caso_reclama_una_medida_que_existe", salida)
        # Las medidas L2 —las que juzgan al catálogo mismo— NO se marcan SIN FIJAR aunque ningún
        # caso las nombre: las ejercita el arnés. Marcarlas era un falso rojo en la herramienta que
        # existe para auditar, y encima incluía a `meta.toda_medida_esta_fijada`, que pasa en verde.
        self.assertIn("la ejercita el arnés sobre el catálogo", salida)
        self.assertNotIn("⚠ SIN FIJAR", salida)

    def test_medida_listar_marca_la_que_de_verdad_no_tiene_evidencia(self) -> None:
        """Y el aviso tiene que seguir apareciendo cuando corresponde, o no sirve de nada."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.main, ["proyecto", "init", str(raiz)])
            medida = raiz / "catalogos" / "x" / "x.nadie_la_prueba.oracle"
            medida.parent.mkdir(parents=True, exist_ok=True)
            medida.write_text(
                "ninguno x.nadie_la_prueba:\n"
                "    de pieza p\n"
                "    donde p.rota == true\n"
                '    umbral <= 0 segun contrato porque "una pieza rota en la escena se ve"\n'
                '    alcance "mira la bandera declarada. NO ve la malla real"\n',
                encoding="utf-8")
            _rc, salida = self._callado(cli.main, ["medida", "listar", "--proyecto", str(raiz)])
            self.assertIn("x.nadie_la_prueba", salida)
            self.assertIn("⚠ SIN FIJAR", salida)

    def test_medida_listar_en_proyecto_vacio_y_con_medidas(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.main, ["proyecto", "init", str(raiz)])

            # Vacío
            rc_vacio, salida_vacio = self._callado(cli.main, ["medida", "listar", "--proyecto", str(raiz)])
            self.assertEqual(rc_vacio, 0)
            self.assertIn("0 medidas", salida_vacio)

            # Con una medida sin caso
            self._callado(cli.main, ["medida", "nueva", "demo.prueba", "--proyecto", str(raiz)])
            (raiz / "catalogos" / "demo" / "demo.prueba.oracle").write_text(
                "ninguno demo.prueba:\n"
                "    de item x\n"
                "    donde x.mal == true\n"
                "    umbral <= 0 segun contrato porque \"defensa\"\n"
                "    alcance \"NO ve otros items\"\n",
                encoding="utf-8",
            )
            rc_sin_caso, salida_sin_caso = self._callado(cli.main, ["medida", "listar", "--proyecto", str(raiz)])
            self.assertEqual(rc_sin_caso, 0)
            self.assertIn("demo.prueba", salida_sin_caso)
            self.assertIn("0 casos  ⚠ SIN FIJAR", salida_sin_caso)
            self.assertIn("NO ve otros items", salida_sin_caso)
            self.assertIn("1 sin fijar", salida_sin_caso)

            # Con un caso que la fija
            self._callado(cli.main, ["caso", "nuevo", "demo/001-rojo", "--proyecto", str(raiz)])
            (raiz / "corpus" / "demo" / "001-rojo.caso").write_text(
                "caso 001-rojo:\n"
                "    fecha: \"2026-08-26\"\n"
                "    origen:\n"
                "        repo: \"demo\"\n"
                "        commit: \"local\"\n"
                "    procedencia: observada\n"
                "    titulo: \"item defectuoso\"\n"
                "    etiqueta: falso_verde\n"
                "    sintoma:\n"
                "        item mal marcado\n"
                "    como_se_detecto: mutacion\n"
                "    medida: demo.prueba\n"
                "    evidencia:\n"
                "        item: mal\n"
                "            true\n"
                "    leccion:\n"
                "        activa la medida\n",
                encoding="utf-8",
            )
            rc_con_caso, salida_con_caso = self._callado(cli.main, ["medida", "listar", "--proyecto", str(raiz)])
            self.assertEqual(rc_con_caso, 0)
            self.assertIn("demo.prueba", salida_con_caso)
            self.assertIn("1 caso", salida_con_caso)
            self.assertIn("todas fijadas", salida_con_caso)

    def test_caso_listar_en_propio_oracle_y_proyecto_vacio(self) -> None:
        rc, salida = self._callado(cli.main, ["caso", "listar", "--proyecto", str(RAIZ)])
        self.assertEqual(rc, 0)
        # El conteo se deriva del corpus real: fijarlo a mano hace que agregar un caso —que es la
        # actividad normal del repo— rompa un test que no tiene nada que ver con lo que cambió.
        cuantos = sum(1 for p in (RAIZ / "corpus").rglob("*") if p.suffix in (".caso", ".json"))
        self.assertIn(f"CORPUS ({cuantos} casos", salida)
        self.assertIn("huecos declarados", salida)
        self.assertIn("proceso/004-testigos-duplicados", salida)
        self.assertIn("⚠ hueco declarado (resuelto)", salida)

        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.main, ["proyecto", "init", str(raiz)])

            # Vacío
            rc_vacio, salida_vacio = self._callado(cli.main, ["caso", "listar", "--proyecto", str(raiz)])
            self.assertEqual(rc_vacio, 0)
            self.assertIn("0 casos", salida_vacio)

            # Con un caso válido
            self._callado(cli.main, ["caso", "nuevo", "demo/001-rojo", "--proyecto", str(raiz)])
            (raiz / "corpus" / "demo" / "001-rojo.caso").write_text(
                "caso 001-rojo:\n"
                "    fecha: \"2026-08-26\"\n"
                "    origen:\n"
                "        repo: \"demo\"\n"
                "        commit: \"local\"\n"
                "    procedencia: observada\n"
                "    titulo: \"item defectuoso\"\n"
                "    etiqueta: falso_verde\n"
                "    sintoma:\n"
                "        item mal marcado\n"
                "    como_se_detecto: mutacion\n"
                "    medida: demo.prueba\n"
                "    evidencia:\n"
                "        item: mal\n"
                "            true\n"
                "    leccion:\n"
                "        activa la medida\n",
                encoding="utf-8",
            )
            rc_uno, salida_uno = self._callado(cli.main, ["caso", "listar", "--proyecto", str(raiz)])
            self.assertEqual(rc_uno, 0)
            self.assertIn("demo/001-rojo", salida_uno)

    def test_formas_canonicas_y_atajos_equivalen(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            # init canónico
            rc_init, _ = self._callado(cli.main, ["proyecto", "init", str(raiz)])
            self.assertEqual(rc_init, 0)

            # proyecto test canónico sobre proyecto vacío
            rc_test, _ = self._callado(cli.main, ["proyecto", "test", "--proyecto", str(raiz)])
            self.assertEqual(rc_test, 0)

            # proyecto relaciones canónico
            rc_rel, salida_rel = self._callado(cli.main, ["proyecto", "relaciones", "--proyecto", str(raiz)])
            self.assertEqual(rc_rel, 0)
            self.assertIn("RELACIONES", salida_rel)

            # proyecto escalares canónico
            rc_esc, salida_esc = self._callado(cli.main, ["proyecto", "escalares", "--proyecto", str(raiz)])
            self.assertEqual(rc_esc, 0)
            self.assertIn("FUNCIONES ESCALARES", salida_esc)

            # medida nueva canónica
            rc_mn, _ = self._callado(cli.main, ["medida", "nueva", "demo.canon", "--proyecto", str(raiz)])
            self.assertEqual(rc_mn, 0)
            self.assertTrue((raiz / "catalogos" / "demo" / "demo.canon.oracle").is_file())

            # caso nuevo canónico
            rc_cn, _ = self._callado(cli.main, ["caso", "nuevo", "demo/002-otro", "--proyecto", str(raiz)])
            self.assertEqual(rc_cn, 0)
            self.assertTrue((raiz / "corpus" / "demo" / "002-otro.caso").is_file())

            # caso atajo con barra
            rc_ca, _ = self._callado(cli.main, ["caso", "demo/003-atajo", "--proyecto", str(raiz)])
            self.assertEqual(rc_ca, 0)
            self.assertTrue((raiz / "corpus" / "demo" / "003-atajo.caso").is_file())

    def test_convertir_usa_macros_oracle_del_proyecto_en_ambas_direcciones(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.main, ["proyecto", "init", str(raiz)])
            (raiz / "macros").mkdir()
            (raiz / "macros" / "sin-fallas.oracle").write_text(
                "\n".join([
                    "defmacro sin-fallas(id, relacion, alias, predicado, porque, alcance):",
                    "    ninguno $id:",
                    "        relacion $relacion",
                    "        alias $alias",
                    "        predicado $predicado",
                    "        porque $porque",
                    "        alcance $alcance",
                    "",
                ]), encoding="utf-8")
            catalogo = raiz / "catalogos" / "demo"
            catalogo.mkdir(parents=True)

            fuente = catalogo / "demo.todo_ok.oracle"
            fuente.write_text(
                "\n".join([
                    "sin-fallas demo.todo_ok:",
                    "    relacion item",
                    "    alias i",
                    "    predicado i.ok == false",
                    "    porque \"un item falso invalida la entrega entera\"",
                    "    alcance \"NO ve items que nadie declaró\"",
                    "",
                ]), encoding="utf-8")

            rc_oracle, salida_oracle = self._callado(
                cli.main, ["convertir", str(fuente), "--proyecto", str(raiz)])
            self.assertEqual(rc_oracle, 0)
            self.assertEqual(json.loads(salida_oracle), [
                "sin-fallas", "demo.todo_ok", "item", "i",
                ["==", ["campo", "i", "ok"], False],
                "un item falso invalida la entrega entera",
                "NO ve items que nadie declaró",
            ])

            canonica = catalogo / "demo.todo_ok.json"
            canonica.write_text(json.dumps(json.loads(salida_oracle)), encoding="utf-8")
            rc_json, salida_json = self._callado(
                cli.main, ["convertir", str(canonica), "--proyecto", str(raiz)])
            self.assertEqual(rc_json, 0)
            self.assertTrue(salida_json.startswith("sin-fallas demo.todo_ok:\n"))
            self.assertIn("    relacion item\n", salida_json)

    def test_faltan_argumentos_en_verbos_devuelve_uno(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.main, ["proyecto", "init", str(raiz)])

            for args, mensaje in (
                (["medida", "nueva", "--proyecto", str(raiz)], "falta el id: oracle medida nueva"),
                (["medida", "revisar", "--proyecto", str(raiz)], "falta el archivo: oracle medida revisar"),
                (["medida", "probar", "--proyecto", str(raiz)], "falta el archivo: oracle medida probar"),
                (["medida", "expandir", "--proyecto", str(raiz)], "falta el archivo: oracle medida expandir"),
                (["caso", "nuevo", "--proyecto", str(raiz)], "falta la ubicación: oracle caso nuevo"),
                (["caso", "generar", "--proyecto", str(raiz)], "falta la medida: oracle caso generar"),
                (["convertir", "--proyecto", str(raiz)], "falta el archivo: oracle convertir"),
                (["nueva", "--proyecto", str(raiz)], "falta el id: oracle nueva"),
                (["--caso", "--proyecto", str(raiz)], "falta la ubicación: oracle caso"),
                (["--nuevo", "--proyecto", str(raiz)], "falta la ubicación: oracle caso"),
                (["revisar", "--proyecto", str(raiz)], "falta el archivo: oracle revisar"),
                (["expandir", "--proyecto", str(raiz)], "falta el archivo: oracle expandir"),
            ):
                rc, salida = self._callado(cli.main, args)
                self.assertEqual(rc, 1)
                self.assertIn(mensaje, salida)

    def test_despachos_canonicos_y_atajos_propagan_resultado_y_argumento(self) -> None:
        proyecto = str(RAIZ)
        casos = (
            (["medida", "revisar", "marca.oracle"], "cmd_revisar", "marca.oracle"),
            (["medida", "expandir", "marca.oracle"], "cmd_expandir", "marca.oracle"),
            (["caso", "generar", "demo.marca"], "cmd_caso_generar", "demo.marca"),
            (["nueva", "demo.marca"], "cmd_nueva", "demo.marca"),
            (["--caso", "demo/001-marca"], "cmd_caso", "demo/001-marca"),
            (["relaciones"], "cmd_relaciones", None),
            (["escalares"], "cmd_escalares", None),
            (["expandir", "marca.oracle"], "cmd_expandir", "marca.oracle"),
        )
        for argv, nombre, argumento in casos:
            with self.subTest(argv=argv), mock.patch.object(cli, nombre, return_value=1) as comando:
                rc, _ = self._callado(cli.main, [*argv, "--proyecto", proyecto])
                self.assertEqual(rc, 1)
                comando.assert_called_once()
                if argumento is not None:
                    self.assertEqual(comando.call_args.args[1], argumento)

    def test_archivo_directo_relativo_al_proyecto_se_despacha_a_revisar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            self._callado(cli.cmd_init, str(raiz), [])
            relativa = Path("catalogos/demo/demo.directa.oracle")
            archivo = raiz / relativa
            archivo.parent.mkdir(parents=True)
            archivo.write_text("contenido", encoding="utf-8")
            with mock.patch.object(cli, "cmd_revisar", return_value=1) as revisar:
                rc, _ = self._callado(
                    cli.main, [str(relativa), "--proyecto", str(raiz)])

        self.assertEqual(rc, 1)
        revisar.assert_called_once()
        self.assertEqual(revisar.call_args.args[1], str(relativa))

    def test_proyecto_invalido_devuelve_uno(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                rc, _ = self._callado(
                    cli.main, ["medida", "listar", "--proyecto", str(Path(td) / "ausente")])

        self.assertEqual(rc, 1)
        self.assertIn("PROYECTO INVÁLIDO", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
