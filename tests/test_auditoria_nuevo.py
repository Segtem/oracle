"""Regresiones del primer recorrido de quien instala Oracle."""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo.proyecto import ProyectoInvalido, resolver
from tools import cli, corpus, manual, tareas

RAIZ = Path(__file__).resolve().parents[1]


def correr(argv):
    salida, errores = io.StringIO(), io.StringIO()
    with redirect_stdout(salida), redirect_stderr(errores):
        try:
            codigo = cli.main(argv)
        except SystemExit as exc:
            codigo = exc.code
    return codigo, salida.getvalue(), errores.getvalue()


class RecorridoNuevo(unittest.TestCase):
    def test_ayuda_descubre_comandos(self):
        _, ayuda, _ = correr(["--help"])
        for palabra in ("manual", "contexto", "probar"):
            self.assertIn(palabra, ayuda)
        _, proyecto, _ = correr(["proyecto", "--help"])
        self.assertIn("contexto", proyecto)

    def test_test_help_no_ejecuta(self):
        with tempfile.TemporaryDirectory() as td:
            entorno = {k: v for k, v in os.environ.items() if k != "ORACLE_PROYECTO"}
            resultado = subprocess.run(
                [sys.executable, str(RAIZ / "tools/cli.py"), "test", "--help"],
                cwd=td, env=entorno, capture_output=True, text=True, timeout=5)
        self.assertEqual(resultado.returncode, 0)
        self.assertIn("oracle test", resultado.stdout)
        self.assertNotIn("UNITARIOS", resultado.stdout)

    def test_init_crea_relaciones_y_propone_caso_primero(self):
        with tempfile.TemporaryDirectory() as td:
            codigo, salida, _ = correr(["init", td])
            self.assertEqual(codigo, 0)
            self.assertTrue((Path(td) / "relaciones").is_dir())
            self.assertLess(salida.index("Creá un caso"), salida.index("Creá una medida"))

    def test_proyecto_ausente_orienta_a_init(self):
        with tempfile.TemporaryDirectory() as td:
            with (mock.patch("nucleo.proyecto.Path.cwd", return_value=Path(td)),
                  mock.patch("nucleo.proyecto.RAIZ_ORACLE", Path(td))):
                with self.assertRaises(ProyectoInvalido) as error:
                    resolver([])
            self.assertIn("oracle init", str(error.exception))

    def test_medida_nueva_nombra_todos_los_marcadores(self):
        with tempfile.TemporaryDirectory() as td:
            correr(["init", td])
            _, salida, _ = correr(["nueva", "demo.primera", "--proyecto", td])
            self.assertIn("SEGUN", salida)
            self.assertIn("AMBITO", salida)

    def test_manual_explica_ambito(self):
        self.assertEqual(set(dict(manual.entradas("ambito"))), {"universal", "del_origen"})

    def test_guia_usa_convertir(self):
        guia = (RAIZ / "docs/03-escribir-una-medida.md").read_text(encoding="utf-8")
        self.assertIn("oracle convertir <archivo", guia)
        self.assertNotIn("python tools/sintaxis.py", guia)

    def test_caso_pide_procedencia_y_explica_etiqueta(self):
        self.assertIn("    procedencia: PROCEDENCIA", corpus.PLANTILLA)
        with tempfile.TemporaryDirectory() as td:
            correr(["init", td])
            _, salida, _ = correr(["caso", "nuevo", "demo/001-prueba", "--proyecto", td])
            self.assertIn("oracle manual etiqueta", salida)

    def test_juzgar_sugiere_relaciones_del_catalogo(self):
        with tempfile.TemporaryDirectory() as td:
            correr(["init", td])
            evidencia = Path(td) / "evidencia.json"
            evidencia.write_text('{"inventada": [{"campo": 1}]}', encoding="utf-8")
            _, _, error = correr(["juzgar", "--proyecto", td, "--con", str(evidencia)])
            self.assertIn("Relaciones que espera el catálogo", error)
            self.assertIn("oracle contexto", error)

    def test_tarea_argumentos_en_espanol(self):
        error = io.StringIO()
        with redirect_stderr(error), self.assertRaises(SystemExit):
            tareas.main(["nueva"])
        self.assertIn("se requieren", error.getvalue())
