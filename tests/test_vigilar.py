"""Contrato pequeño y prioritario del bucle vivo de `oracle medida probar`."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo.proyecto import Proyecto
from tools import cli, medida


class _SalidaDiferida(io.StringIO):
    def __init__(self) -> None:
        super().__init__()
        self.visible = ""

    def flush(self) -> None:
        self.visible = self.getvalue()
        super().flush()


def _proyecto(raiz: Path) -> tuple[Proyecto, Path]:
    for nombre in ("catalogos", "corpus", "diferencial"):
        (raiz / nombre).mkdir()
    (raiz / "oracle.json").write_text(json.dumps({
        "esquema": "oracle.proyecto/v1",
        "catalogo_base": True,
        "perfiles": [],
    }), encoding="utf-8")
    ruta = raiz / "catalogos" / "demo" / "demo.alto.oracle"
    ruta.parent.mkdir()
    ruta.write_text(
        "ninguno demo.alto:\n"
        "    de pieza p\n"
        "    donde p.alto > 400.0\n"
        '    umbral <= 0 segun contrato porque "cuatro metros es el techo"\n'
        '    alcance "mira el alto declarado. NO mira la malla"\n',
        encoding="utf-8",
    )
    return Proyecto(raiz), ruta


class VigilarTests(unittest.TestCase):
    def test_firma_detecta_reemplazo_y_archivo_ausente(self) -> None:
        estado = mock.Mock(st_mtime_ns=11, st_size=22, st_ino=33)
        ruta = mock.Mock()
        ruta.stat.return_value = estado
        self.assertEqual(medida._firma_de_archivo(ruta), (11, 22, 33))

        ruta.stat.return_value = mock.Mock(st_mtime_ns=12, st_size=22, st_ino=33)
        self.assertNotEqual(medida._firma_de_archivo(ruta), (11, 22, 33))

        ruta.stat.side_effect = FileNotFoundError("guardado atómico")
        self.assertIsNone(medida._firma_de_archivo(ruta))

    def test_reevalua_al_guardar_y_sobrevive_a_un_reemplazo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            firmas = [(1, 10, 100), None, (2, 11, 101)]
            salida = _SalidaDiferida()
            vueltas = 0
            evaluaciones = 0

            def evaluar(_proy, _ruta, _texto) -> int:
                nonlocal evaluaciones
                if evaluaciones == 0:
                    self.assertIn("VIGILANDO", salida.visible)
                rc = (1, 0)[evaluaciones]
                evaluaciones += 1
                return rc

            def dormir(_intervalo: float) -> None:
                nonlocal vueltas
                vueltas += 1
                if vueltas == 2:
                    self.assertIn("esperando que vuelva a aparecer", salida.visible)
                if vueltas == 3:
                    raise KeyboardInterrupt

            with (mock.patch.object(medida, "_firma_de_archivo", side_effect=firmas),
                  mock.patch.object(medida, "probar", side_effect=evaluar) as probar,
                  mock.patch.object(medida.time, "sleep", side_effect=dormir) as esperar,
                  redirect_stdout(salida)):
                rc = medida.vigilar(
                    proy, ruta, 'pieza: id, alto\n    "columna", 450.0')

        self.assertEqual(rc, 0)
        self.assertEqual(probar.call_count, 2)
        self.assertEqual(esperar.call_args_list, [mock.call(0.25)] * 3)
        self.assertIn("VIGILANDO", salida.getvalue())
        self.assertIn("esperando que vuelva a aparecer", salida.getvalue())
        self.assertIn("Vigilancia terminada", salida.getvalue())

    def test_un_error_real_de_parseo_no_mata_la_vigilancia(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            valido = ruta.read_text(encoding="utf-8")
            ruta.write_text("ninguno demo.alto:\n    de", encoding="utf-8")
            vueltas = 0

            def guardar_y_terminar(_intervalo: float) -> None:
                nonlocal vueltas
                vueltas += 1
                if vueltas == 1:
                    ruta.write_text(valido, encoding="utf-8")
                else:
                    raise KeyboardInterrupt

            salida = io.StringIO()
            with (mock.patch.object(medida.time, "sleep", side_effect=guardar_y_terminar),
                  redirect_stdout(salida)):
                rc = medida.vigilar(
                    proy, ruta, 'pieza: id, alto\n    "columna", 450.0')

        self.assertEqual(rc, 0)
        self.assertIn("✗", salida.getvalue())
        self.assertIn("ROJO", salida.getvalue())
        self.assertIn("Vigilancia terminada", salida.getvalue())

    def test_cli_despacha_vigilar_y_valida_el_valor_de_con(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            evidencia = 'pieza: id, alto\n    "columna", 450.0'
            argv_vigilar = [
                "medida", "probar", str(ruta), "--con", evidencia, "--vigilar",
                "--proyecto", str(proy.raiz)]
            with mock.patch.object(medida, "vigilar", return_value=7) as vigilar:
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.main(argv_vigilar)
            self.assertEqual(rc, 7)
            vigilar.assert_called_once_with(proy, ruta, evidencia)

            argv_una = [
                "medida", "probar", str(ruta), "--proyecto", str(proy.raiz),
                "--con", evidencia]
            with mock.patch.object(cli, "cmd_probar", return_value=5) as probar:
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.main(argv_una)
            self.assertEqual(rc, 5)
            probar.assert_called_once_with(
                proy, str(ruta), evidencia, argv=argv_una, vigilar=False)

            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main([
                    "medida", "probar", str(ruta), "--proyecto", str(proy.raiz), "--con"])
            self.assertEqual(rc, 1)
            self.assertIn("falta la evidencia", salida.getvalue())

            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main([
                    "medida", "probar", str(ruta), "--con", "--vigilar",
                    "--proyecto", str(proy.raiz)])
            self.assertEqual(rc, 1)
            self.assertIn("falta la evidencia", salida.getvalue())

    def test_wrapper_elige_una_sola_modalidad_y_propaga_el_codigo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            with (mock.patch.object(medida, "probar", return_value=3) as una,
                  mock.patch.object(medida, "vigilar", return_value=4) as viva):
                self.assertEqual(cli.cmd_probar(proy, str(ruta), "filas"), 3)
                self.assertEqual(cli.cmd_probar(
                    proy, str(ruta), "filas", vigilar=True), 4)
            una.assert_called_once_with(proy, ruta, "filas")
            viva.assert_called_once_with(proy, ruta, "filas")

    def test_wrapper_respeta_confianza_de_escalares_y_falla_cerrado(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            contexto = mock.MagicMock()
            contexto.__enter__.return_value = None
            contexto.__exit__.return_value = False
            with (mock.patch.object(cli, "escalares_del_proyecto", return_value=contexto) as abrir,
                  mock.patch.object(cli, "confiar_escalares", return_value=True),
                  mock.patch.object(medida, "probar", return_value=0)):
                self.assertEqual(cli.cmd_probar(
                    proy, str(ruta), "filas", argv=["--confiar-escalares"]), 0)
            abrir.assert_called_once_with(proy, confiar=True)

            contexto.__enter__.side_effect = cli.EscalaresNoConfiables("falta confianza")
            salida = io.StringIO()
            with (mock.patch.object(cli, "escalares_del_proyecto", return_value=contexto),
                  redirect_stdout(salida)):
                self.assertEqual(cli.cmd_probar(proy, str(ruta), "filas"), 1)
            self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS", salida.getvalue())
