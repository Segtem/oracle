"""Regresiones encontradas al usar el tracker y medir su diagnóstico Git."""

import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tools import tareas, tareas_git

RAIZ = Path(tareas.__file__).resolve().parents[1]
CLI = RAIZ / "tools/cli.py"
EJEMPLO = RAIZ / "ejemplo/seguimiento-tareas/evaluar.py"


class ConsumidorDesdeCheckoutTests(unittest.TestCase):
    def test_ejemplo_carga_desde_checkout_y_muestra_testigo(self):
        """El wheel pasaba, pero la instrucción PYTHONPATH del ejemplo no podía importar."""
        with tempfile.TemporaryDirectory() as td:
            evidencia = Path(td) / "hechos.json"
            env = dict(os.environ, PYTHONPATH=str(RAIZ), PYTHONDONTWRITEBYTECODE="1")
            for estado, esperado in (("presente", 0), ("ausente", 1)):
                evidencia.write_text(json.dumps({"referencia_seguimiento": [{
                    "tarea_id": "ejemplo", "origen": "tareas/ejemplo/TAREA.md", "linea": 8,
                    "destino_declarado": "captura-pendiente.png", "clase": "local",
                    "estado": estado}]}))
                p = subprocess.run([sys.executable, "-B", str(EJEMPLO), "--con", str(evidencia),
                                    "--politica", "referencias_locales_presentes"],
                                   cwd=td, env=env, capture_output=True, text=True, timeout=15)
                self.assertEqual(p.returncode, esperado, p.stderr)
                self.assertNotIn("Traceback", p.stderr)
                if esperado:
                    self.assertIn("captura-pendiente.png", p.stdout)


@unittest.skipUnless(shutil.which("git"), "requiere Git")
class RevisionGitP4Tests(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(prefix="oracle-p4-revision-")
        self.addCleanup(td.cleanup)
        self.temporal = Path(td.name)
        self.raiz = self.temporal / "proyecto"
        self.carpeta = self.raiz / "tareas/20260912-150000-prueba"
        self.carpeta.mkdir(parents=True)
        (self.carpeta / "TAREA.md").write_text(
            "# Prueba\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n\n")
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith("GIT_") and k != "ORACLE_PROYECTO"}
        self.git("init", "-q")

    def git(self, *args):
        p = subprocess.run(["git", "-C", str(self.raiz), *args], env=self.env,
                           capture_output=True, timeout=15)
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout

    def cli(self, verbo, *args):
        return subprocess.run([sys.executable, "-B", str(CLI), "tarea", verbo,
                               "--proyecto", str(self.raiz), *args], env=self.env,
                              capture_output=True, timeout=15)

    def test_git_con_arbol_externo_falla_sin_traceback(self):
        """Una configuración core.worktree externa no debe filtrar ValueError desde hechos."""
        otro = self.temporal / "arbol real"
        otro.mkdir()
        self.git("config", "core.worktree", str(otro))
        for verbo, opciones in (("seguimiento", ("--json",)), ("hechos", ("--git",))):
            with self.subTest(verbo=verbo):
                p = self.cli(verbo, *opciones)
                self.assertEqual(p.returncode, 1)
                self.assertEqual(p.stdout, b"")
                self.assertIn(b"ERROR:", p.stderr)
                self.assertNotIn(b"Traceback", p.stderr)

    def test_nombre_del_repositorio_con_salto_final_se_preserva(self):
        """rstrip borraba caracteres del nombre además del terminador de rev-parse."""
        nuevo = self.temporal / "proyecto\n"
        self.raiz.rename(nuevo)
        self.raiz = nuevo
        for verbo, opciones in (("seguimiento", ("--json",)), ("hechos", ("--git",))):
            with self.subTest(verbo=verbo):
                p = self.cli(verbo, *opciones)
                self.assertEqual(p.returncode, 0, p.stderr)
                datos = json.loads(p.stdout)
                if verbo == "seguimiento":
                    self.assertEqual(datos["repositorio"], str(nuevo))
                else:
                    self.assertEqual(datos["lectura_seguimiento"][0]["git"], "comprobado")

    def test_json_es_utf8_aunque_un_nombre_local_no_lo_sea(self):
        """ensure_ascii protege nombres Unix con bytes inválidos: JSON debe seguir decodificando."""
        nombre = os.fsencode(self.carpeta) + b"/captura_\xff.bin"
        with open(nombre, "wb") as archivo:
            archivo.write(b"adjunto construido")
        for verbo, opciones, relacion in (("seguimiento", ("--json",), "archivos"),
                                          ("hechos", (), "archivo_seguimiento")):
            with self.subTest(verbo=verbo):
                p = self.cli(verbo, *opciones)
                self.assertEqual(p.returncode, 0, p.stderr)
                datos = json.loads(p.stdout.decode("utf-8"))
                self.assertTrue(any(os.fsencode(a["ruta"]).endswith(b"captura_\xff.bin")
                                    for a in datos[relacion]))

    def test_directorio_simbolico_sin_git_tambien_se_omite(self):
        """Exigir simultáneamente symlink y subrepo permitía recorrer un enlace ordinario."""
        externo = self.temporal / "sin git"
        externo.mkdir()
        (externo / "privado.txt").write_text("fuera del tracker")
        enlace = self.carpeta / "enlace"
        enlace.symlink_to(externo, target_is_directory=True)
        datos = tareas_git.seguimiento(self.raiz)
        ruta = enlace.relative_to(self.raiz).as_posix()
        self.assertIn(ruta, {a["ruta"] for a in datos["omitidos"]})
        self.assertFalse(any(a["ruta"].startswith(ruta + "/") for a in datos["archivos"]))

    def test_retiro_del_indice_sigue_siendo_un_cambio_pendiente(self):
        """Conservar el archivo en disco después de git rm --cached no lo vuelve nuevo sin historia."""
        self.git("add", "tareas")
        self.git("-c", "user.name=Prueba", "-c", "user.email=prueba@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "Ejemplo construido")
        self.git("rm", "--cached", "-r", "tareas")
        datos = tareas_git.seguimiento(self.raiz)
        self.assertEqual({a["estado"] for a in datos["archivos"]}, {"con_cambios"})

    def test_salida_humana_distingue_sin_commits_de_head_real(self):
        """El JSON estaba fijado, pero la salida humana podía perder HEAD o imprimir None."""
        p = self.cli("seguimiento")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn(b"HEAD: sin commits", p.stdout)
        self.git("add", "tareas")
        self.git("-c", "user.name=Prueba", "-c", "user.email=prueba@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "Ejemplo construido")
        head = self.git("rev-parse", "HEAD").strip()
        p = self.cli("seguimiento")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn(b"HEAD: " + head, p.stdout)
        self.assertNotIn(b"sin commits", p.stdout)

    def test_salida_humana_sin_repositorio_y_codigo_del_despacho(self):
        """El despacho devuelve éxito explícito y enumera archivos aunque no haya Git."""
        raiz = self.temporal / "sin repo"
        (raiz / "tareas").mkdir(parents=True)
        (raiz / "tareas/README.md").write_text("Prueba construida")
        args = ["--proyecto", str(raiz)]
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            codigo = tareas_git.cmd_seguimiento(args, args)
        self.assertEqual(codigo, 0)
        self.assertIn("no pertenece a un repositorio Git", salida.getvalue())
        self.assertIn("sin repositorio: tareas/README.md", salida.getvalue())


class LimiteGitP4Tests(unittest.TestCase):
    def test_git_tiene_limite_de_30_segundos_y_traduce_timeout(self):
        """La ronda dejó pasar 30→31 aunque el contrato anuncia un máximo de 30 segundos."""
        with mock.patch.object(tareas_git.subprocess, "run",
                               side_effect=subprocess.TimeoutExpired("git", 30)) as ejecutar:
            with self.assertRaisesRegex(tareas.TareaError, "30 segundos"):
                tareas_git._git(Path("/tmp"), "status")
        self.assertEqual(ejecutar.call_args.kwargs["timeout"], 30)

    def test_git_ausente_da_error_de_dominio(self):
        """La ausencia del ejecutable se traduce en la frontera que realmente lanza FileNotFoundError."""
        with mock.patch.object(tareas_git.subprocess, "run", side_effect=FileNotFoundError("git")):
            with self.assertRaisesRegex(tareas.TareaError, "Git no está disponible"):
                tareas_git._git(Path("/tmp"), "status")
