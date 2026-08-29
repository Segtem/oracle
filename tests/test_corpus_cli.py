"""Contrato observable del verificador y la CLI de corpus."""

from __future__ import annotations

import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo.proyecto import Proyecto, ProyectoInvalido
from tools import corpus


def _datos_caso(cid: str, *, medida: str | None = "meta.mide", **cambios) -> dict:
    datos = {
        "id": cid,
        "fecha": "2026-08-28",
        "origen": {"repo": "Segtem/oracle", "commit": "prueba"},
        "procedencia": "observada",
        "titulo": "Caso de prueba",
        "etiqueta": "verde_correcto",
        "sintoma": "síntoma",
        "como_se_detecto": "observacion",
        "medida": medida,
        "evidencia": {"hecho": [{"id": "a", "ok": True}]},
        "leccion": "lección",
    }
    datos.update(cambios)
    return datos


def _proyecto(raiz: Path) -> Proyecto:
    (raiz / "catalogos").mkdir(exist_ok=True)
    (raiz / "corpus").mkdir(exist_ok=True)
    return Proyecto(raiz)


def _escribir_caso(proy: Proyecto, grupo: str, datos: dict) -> Path:
    destino = proy.corpus / grupo / f"{datos['id']}.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return destino


class RutaYCasoNuevoTests(unittest.TestCase):
    def test_la_ruta_nueva_exige_grupo_id_y_alfabeto_del_contrato(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            proy = _proyecto(Path(d))
            invalidas = (
                "sin-grupo",
                "meta/dos/001-caso",
                "Meta/001-caso",
                "meta/no-numero",
            )
            for ubicacion in invalidas:
                with self.subTest(ubicacion=ubicacion), self.assertRaises(ProyectoInvalido):
                    corpus.ruta_de_caso_nuevo(proy, ubicacion)
            self.assertEqual(
                corpus.ruta_de_caso_nuevo(proy, "meta/999-caso"),
                proy.corpus / "meta" / "999-caso.caso",
            )

    def test_nuevo_deriva_metadatos_crea_en_grupo_existente_y_no_pisa(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            proy = _proyecto(Path(d))
            (proy.corpus / "meta").mkdir()
            salida = io.StringIO()
            with mock.patch.object(
                corpus,
                "_del_repositorio",
                return_value=("2026-08-28", "Segtem/oracle", "abc1234"),
            ), redirect_stdout(salida):
                self.assertEqual(corpus.nuevo(proy, "meta/999-caso"), 0)
            texto = salida.getvalue()
            self.assertIn("creado: corpus/meta/999-caso.caso", texto)
            self.assertIn("fecha, repo, commit", texto)
            self.assertIn("etiqueta:", texto)
            self.assertIn("procedencia:", texto)
            self.assertIn("como_se_detecto:", texto)
            escrito = (proy.corpus / "meta" / "999-caso.caso").read_text(encoding="utf-8")
            self.assertIn('repo: "Segtem/oracle"', escrito)
            self.assertIn('commit: "abc1234"', escrito)

            salida = io.StringIO()
            with redirect_stdout(salida):
                self.assertEqual(corpus.nuevo(proy, "meta/999-caso"), 1)
            self.assertIn("ya existe: corpus/meta/999-caso.caso", salida.getvalue())


class GitDelRepositorioTests(unittest.TestCase):
    def test_git_usa_raiz_captura_texto_timeout_y_codigo_cero(self) -> None:
        resultado = subprocess.CompletedProcess([], 0, stdout=" abc1234\n", stderr="")
        with mock.patch("subprocess.run", return_value=resultado) as run:
            self.assertEqual(corpus._git_del_repositorio(Path("/tmp/proyecto"), "rev-parse"), "abc1234")
        run.assert_called_once_with(
            ["git", "-C", "/tmp/proyecto", "rev-parse"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        for respuesta in (
            subprocess.CompletedProcess([], 1, stdout="no usar", stderr="falla"),
            OSError("git ausente"),
            subprocess.TimeoutExpired(["git"], 5),
        ):
            with self.subTest(respuesta=type(respuesta).__name__):
                efecto = respuesta if isinstance(respuesta, BaseException) else None
                with mock.patch("subprocess.run", side_effect=efecto, return_value=None if efecto else respuesta):
                    self.assertEqual(corpus._git_del_repositorio(Path("/tmp/p"), "x"), "")

    def test_metadatos_normalizan_remoto_y_dejan_marcadores_si_git_falla(self) -> None:
        respuestas = (
            subprocess.CompletedProcess([], 0, stdout="abc1234\n", stderr=""),
            subprocess.CompletedProcess(
                [], 0, stdout="https://host/grupo/subgrupo/oracle.git\n", stderr=""
            ),
        )
        with mock.patch("subprocess.run", side_effect=respuestas):
            fecha, repo, commit = corpus._del_repositorio(Path("/tmp/p"))
        self.assertRegex(fecha, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual((repo, commit), ("subgrupo/oracle", "abc1234"))

        with mock.patch("subprocess.run", side_effect=OSError("sin git")):
            _fecha, repo, commit = corpus._del_repositorio(Path("/tmp/p"))
        self.assertEqual((repo, commit), ("REPO", "COMMIT"))


class GenerarCasoTests(unittest.TestCase):
    def test_generar_propaga_codigo_flags_y_directorio(self) -> None:
        proy = Proyecto(Path("/tmp/proyecto"))
        with mock.patch("nucleo.generador.generar_caso", return_value=(7, object())) as generar:
            rc = corpus.generar(
                proy,
                "dominio.medida",
                ["--confiar-escalares", "--imprimir", "--directorio", "salida"],
            )
        self.assertEqual(rc, 7)
        generar.assert_called_once_with(
            proy,
            "dominio.medida",
            directorio_destino=Path("salida"),
            confiar=True,
            imprimir_solo=True,
        )

    def test_directorio_sin_valor_no_inventa_un_destino(self) -> None:
        proy = Proyecto(Path("/tmp/proyecto"))
        with mock.patch("nucleo.generador.generar_caso", return_value=(0, object())) as generar:
            self.assertEqual(corpus.generar(proy, "dominio.medida", ["--directorio"]), 0)
        self.assertIsNone(generar.call_args.kwargs["directorio_destino"])


class VerificarYResumenTests(unittest.TestCase):
    def test_verificar_rechaza_procedencia_inventada_en_json(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            proy = _proyecto(Path(d))
            _escribir_caso(
                proy,
                "meta",
                _datos_caso("001-procedencia", procedencia="telepatica"),
            )
            fallas, cargados = corpus.verificar(proy.corpus)
        self.assertEqual(len(cargados), 1)
        self.assertEqual(len(fallas), 1)
        self.assertIn("procedencia", fallas[0])
        self.assertIn("telepatica", fallas[0])

    def test_resumen_separa_cada_estado_sin_medida(self) -> None:
        cargados = [
            _datos_caso(
                "001-abierto",
                medida=None,
                estado_sin_medida="abierto",
                sin_medida_todavia="falta",
            ),
            _datos_caso(
                "002-resuelto",
                medida=None,
                estado_sin_medida="resuelto",
                resuelto="cerrado",
            ),
            _datos_caso(
                "003-limite",
                medida=None,
                estado_sin_medida="limite_humano",
                limite_humano="juicio",
            ),
        ]
        salida = io.StringIO()
        with redirect_stdout(salida):
            corpus.resumen(cargados)
        texto = salida.getvalue()
        self.assertIn("huecos abiertos (1):\n  · 001-abierto", texto)
        self.assertIn("casos resueltos conservados como memoria (1):\n  · 002-resuelto", texto)
        self.assertIn("límites humanos no automatizables (1):\n  · 003-limite", texto)


class ListarCorpusTests(unittest.TestCase):
    def test_listar_rechaza_estructura_y_caso_ilegible(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            proy = Proyecto(Path(d))
            salida = io.StringIO()
            with redirect_stdout(salida):
                self.assertEqual(corpus.listar(proy), 1)
            self.assertIn("PROYECTO INVÁLIDO", salida.getvalue())

            proy = _proyecto(Path(d))
            roto = proy.corpus / "meta" / "001-roto.json"
            roto.parent.mkdir()
            roto.write_text("{", encoding="utf-8")
            salida = io.StringIO()
            with redirect_stdout(salida):
                self.assertEqual(corpus.listar(proy), 1)
            self.assertIn("✗", salida.getvalue())
            self.assertIn("JSON inválido", salida.getvalue())

    def test_listar_distingue_vacio_unico_y_huecos_con_anchos_estables(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            proy = _proyecto(Path(d))
            salida = io.StringIO()
            with redirect_stdout(salida):
                self.assertEqual(corpus.listar(proy), 0)
            self.assertIn("CORPUS: 0 casos", salida.getvalue())

            medido = _datos_caso("001-medido")
            _escribir_caso(proy, "g", medido)
            salida = io.StringIO()
            with redirect_stdout(salida):
                self.assertEqual(corpus.listar(proy), 0)
            texto = salida.getvalue()
            self.assertIn("CORPUS (1 caso · todos con medida):", texto)
            rel = "g/001-medido"
            linea = f"  {rel}  verde_correcto  meta.mide"
            self.assertIn(linea, texto.splitlines())

            hueco = _datos_caso(
                "002-hueco",
                medida=None,
                estado_sin_medida="abierto",
                sin_medida_todavia="falta",
            )
            _escribir_caso(proy, "g", hueco)
            salida = io.StringIO()
            with redirect_stdout(salida):
                self.assertEqual(corpus.listar(proy), 0)
            texto = salida.getvalue()
            self.assertIn("CORPUS (2 casos · 1 con medida · 1 hueco declarado):", texto)
            self.assertIn("⚠ hueco declarado (abierto)", texto)


class MainCorpusTests(unittest.TestCase):
    def _llamar(self, argv, *, proy=None):
        salida = io.StringIO()
        parches = [] if proy is None else [mock.patch.object(corpus, "resolver_cli", return_value=proy)]
        with parches[0] if parches else mock.patch.object(corpus, "resolver_cli", wraps=corpus.resolver_cli):
            with redirect_stdout(salida):
                rc = corpus.main(argv)
        return rc, salida.getvalue()

    def test_help_funciona_con_cualquiera_de_sus_dos_formas(self) -> None:
        for bandera in ("-h", "--help"):
            with self.subTest(bandera=bandera):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    self.assertEqual(corpus.main([bandera]), 0)
                self.assertIn("Verificador del corpus", salida.getvalue())

        salida = io.StringIO()
        with mock.patch.object(corpus.sys, "argv", ["corpus.py", "--help"]), redirect_stdout(salida):
            self.assertEqual(corpus.main(None), 0)
        self.assertIn("Verificador del corpus", salida.getvalue())

    def test_proyecto_ausente_o_invalido_falla(self) -> None:
        with mock.patch.object(corpus, "resolver_cli", return_value=None):
            self.assertEqual(corpus.main([]), 1)
        with tempfile.TemporaryDirectory() as d:
            proy = Proyecto(Path(d))
            rc, salida = self._llamar([], proy=proy)
        self.assertEqual(rc, 1)
        self.assertIn("PROYECTO INVÁLIDO", salida)

    def test_despachos_propagan_codigo_y_validan_aridad(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            proy = _proyecto(Path(d))
            with mock.patch.object(corpus, "resolver_cli", return_value=proy), mock.patch.object(
                corpus, "problemas_estructura", return_value=[]
            ), mock.patch.object(corpus, "listar", return_value=7) as listar:
                self.assertEqual(corpus.main(["listar"]), 7)
                listar.assert_called_once_with(proy)

            for forma in ("generar", "--generar"):
                with self.subTest(forma=forma), mock.patch.object(
                    corpus, "resolver_cli", return_value=proy
                ), mock.patch.object(corpus, "problemas_estructura", return_value=[]), mock.patch.object(
                    corpus, "generar", return_value=7
                ) as generar:
                    self.assertEqual(corpus.main([forma, "meta.mide"]), 7)
                    generar.assert_called_once_with(proy, "meta.mide", [forma, "meta.mide"])
            for argv in (["generar"], ["generar", "a", "b"]):
                rc, salida = self._llamar(argv, proy=proy)
                self.assertEqual(rc, 1)
                self.assertIn("--generar <dominio.medida>", salida)

            with mock.patch.object(corpus, "resolver_cli", return_value=proy), mock.patch.object(
                corpus, "problemas_estructura", return_value=[]
            ), mock.patch.object(corpus, "nuevo", return_value=7) as nuevo:
                self.assertEqual(corpus.main(["--nuevo", "meta/999-caso"]), 7)
                nuevo.assert_called_once_with(proy, "meta/999-caso")
            for argv in (["--nuevo"], ["--nuevo", "a", "b"]):
                rc, salida = self._llamar(argv, proy=proy)
                self.assertEqual(rc, 1)
                self.assertIn("--nuevo <grupo/NNN-descripcion>", salida)

    def test_verificacion_imprime_fallas_y_resumen_solo_si_se_pide(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            proy = _proyecto(Path(d))
            parches = (
                mock.patch.object(corpus, "resolver_cli", return_value=proy),
                mock.patch.object(corpus, "problemas_estructura", return_value=[]),
            )
            with parches[0], parches[1], mock.patch.object(
                corpus, "verificar", return_value=(["uno", "dos"], [])
            ):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    self.assertEqual(corpus.main([]), 1)
                self.assertIn("CORPUS: 2 problema(s)", salida.getvalue())
                self.assertIn("· uno", salida.getvalue())
                self.assertIn("· dos", salida.getvalue())

            cargados = [_datos_caso("001-ok")]
            for argv, llamadas in (([], 0), (["--resumen"], 1)):
                with mock.patch.object(corpus, "resolver_cli", return_value=proy), mock.patch.object(
                    corpus, "problemas_estructura", return_value=[]
                ), mock.patch.object(corpus, "verificar", return_value=([], cargados)), mock.patch.object(
                    corpus, "resumen"
                ) as resumen:
                    salida = io.StringIO()
                    with redirect_stdout(salida):
                        self.assertEqual(corpus.main(argv), 0)
                    self.assertEqual(resumen.call_count, llamadas)
                    self.assertIn("CORPUS OK · 1 casos", salida.getvalue())
