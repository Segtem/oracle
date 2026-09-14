"""El seguimiento distingue archivos locales, índice y contenido confirmado."""

import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from tools import tareas_git


@unittest.skipUnless(shutil.which("git"), "requiere Git")
class SeguimientoGitTests(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory(prefix="oracle-git-tareas-")
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        self.proyecto = self.raiz / "proyecto [ñ]"
        self.carpeta = self.proyecto / "tareas" / "20260912-100000-ejemplo"
        self.carpeta.mkdir(parents=True)
        self.documento = self.carpeta / "TAREA.md"
        self.documento.write_text("# Ejemplo\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n")
        self.git("init", "-q")

    def git(self, *args):
        resultado = subprocess.run(
            ["git", "-C", str(self.raiz), *args], capture_output=True, timeout=15,
            env={k: v for k, v in os.environ.items() if not k.startswith("GIT_")})
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        return resultado.stdout

    def confirmar(self):
        self.git("-c", "user.name=Prueba", "-c", "user.email=prueba@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "Ejemplo construido")

    def filas(self):
        return {a["ruta"]: a for a in tareas_git.seguimiento(self.proyecto)["archivos"]}

    def fila(self, ruta=None):
        return self.filas()[(ruta or self.documento).relative_to(self.proyecto).as_posix()]

    def test_local_indice_y_commit_son_tres_observaciones_distintas(self):
        """Un archivo recién creado o añadido no se presenta como contenido confirmado."""
        primero = self.fila()
        self.assertEqual(primero["estado"], "sin_seguimiento")
        self.assertFalse(primero["en_indice"])
        self.assertFalse(primero["en_head"])
        self.git("add", "--", str(self.documento))
        agregado = self.fila()
        self.assertTrue(agregado["en_indice"])
        self.assertFalse(agregado["en_head"])
        self.assertEqual(agregado["indice"], "A")
        self.confirmar()
        confirmado = self.fila()
        self.assertTrue(confirmado["en_head"])
        self.assertEqual(confirmado["estado"], "sin_cambios")
        self.documento.write_text(self.documento.read_text() + "\nNota posterior\n")
        modificado = self.fila()
        self.assertTrue(modificado["en_head"])
        self.assertEqual(modificado["trabajo"], "M")
        self.assertEqual(modificado["estado"], "con_cambios")

    def test_archivos_ignorados_no_desaparecen_del_diagnostico(self):
        """Un directorio ignorado completo sigue mostrando sus adjuntos individuales."""
        self.proyecto.joinpath(".gitignore").write_text("*.png\nprivado/\n")
        captura = self.carpeta / "captura ñ (1).png"
        captura.write_bytes(b"imagen construida")
        oculto = self.carpeta / "privado" / "nota.txt"
        oculto.parent.mkdir()
        oculto.write_text("oculto")
        for ruta in (captura, oculto):
            self.assertTrue(self.fila(ruta)["ignorado"])
            self.assertEqual(self.fila(ruta)["estado"], "ignorado")
        self.git("add", "-f", "--", str(captura))
        self.assertFalse(self.fila(captura)["ignorado"])
        self.assertTrue(self.fila(captura)["en_indice"])

    def test_borrados_locales_y_del_indice_conservan_su_rastro(self):
        """Un archivo borrado todavía presente en HEAD no desaparece del informe."""
        self.git("add", "--", str(self.documento))
        self.confirmar()
        self.documento.unlink()
        borrado = self.fila()
        self.assertFalse(borrado["existe"])
        self.assertTrue(borrado["en_indice"])
        self.assertEqual(borrado["trabajo"], "D")
        self.git("add", "-u")
        borrado = self.fila()
        self.assertFalse(borrado["en_indice"])
        self.assertTrue(borrado["en_head"])
        self.assertEqual(borrado["indice"], "D")

    def test_nombres_con_saltos_y_unicode_no_rompen_el_formato(self):
        """La salida NUL de Git conserva nombres que no caben en un parser por líneas."""
        archivo = self.carpeta / "captura\nñ.txt"
        archivo.write_text("nota")
        self.git("add", "--", str(archivo))
        self.assertTrue(self.fila(archivo)["en_indice"])
        self.assertEqual(self.fila(archivo)["indice"], "A")

    def test_retirar_del_indice_no_oculta_el_borrado_pendiente(self):
        """Un archivo conservado en disco puede ser a la vez borrado del índice y untracked."""
        self.git("add", "--", str(self.documento))
        self.confirmar()
        self.git("rm", "--cached", "--", str(self.documento))
        fila = self.fila()
        self.assertFalse(fila["en_indice"])
        self.assertTrue(fila["en_head"])
        self.assertTrue(fila["existe"])
        self.assertEqual(fila["indice"], "D")
        self.assertEqual(set(fila["codigos_git"]), {"D ", "??"})

    def test_consulta_no_modifica_indice_ni_archivos(self):
        """Consultar cobertura no hace git add ni refresca el índice en disco."""
        self.git("add", "--", str(self.documento))
        indice = self.raiz / ".git" / "index"
        contenido = indice.read_bytes()
        fecha = indice.stat().st_mtime_ns
        original = self.documento.read_bytes()
        self.filas()
        self.assertEqual(indice.read_bytes(), contenido)
        self.assertEqual(indice.stat().st_mtime_ns, fecha)
        self.assertEqual(self.documento.read_bytes(), original)

    def test_git_dir_heredado_no_redirige_el_proyecto(self):
        """El diagnóstico observa el proyecto pedido aunque la shell seleccione otro Git."""
        with mock.patch.dict(os.environ, {"GIT_DIR": "/ruta/que/no/existe"}):
            self.assertEqual(self.fila()["estado"], "sin_seguimiento")

    def test_raiz_simbolica_se_rechaza_y_adjuntos_externos_no_se_recorren(self):
        """Los enlaces del tracker no permiten leer contenido de carpetas externas."""
        enlace = self.carpeta / "externo"
        enlace.symlink_to(self.raiz, target_is_directory=True)
        datos = tareas_git.seguimiento(self.proyecto)
        self.assertTrue(any(x["ruta"].endswith("externo") for x in datos["omitidos"]))
        self.assertFalse(any("externo/" in x["ruta"] for x in datos["archivos"]))
        otro = self.raiz / "otro"
        otro.mkdir()
        (otro / "tareas").symlink_to(self.proyecto / "tareas", target_is_directory=True)
        with self.assertRaises(ValueError):
            tareas_git.seguimiento(otro)

    def test_sin_repositorio_se_informa_sin_afirmar_seguimiento(self):
        """Una carpeta independiente es utilizable pero no tiene historia comprobada."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "tareas").mkdir()
            (raiz / "tareas" / "README.md").write_text("guía")
            datos = tareas_git.seguimiento(raiz)
            self.assertIsNone(datos["repositorio"])
            self.assertEqual(datos["sin_repositorio"], ["tareas/README.md"])
            self.assertEqual(datos["archivos"], [])

    def test_ayuda_y_argumentos_invalidos_no_ejecutan_git(self):
        """La ayuda y errores de sintaxis se resuelven antes de consultar el proyecto."""
        for args, esperado in ((["--help"], 0), (["--inventada"], 2)):
            with self.subTest(args=args), mock.patch.object(tareas_git, "_git") as llamada:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as e:
                        tareas_git.cmd_seguimiento(args, args)
                self.assertEqual(e.exception.code, esperado)
                llamada.assert_not_called()

    def test_error_git_no_se_disfraza_de_archivos_sin_seguimiento(self):
        """Un fallo de Git devuelve error operacional y no un diagnóstico vacío exitoso."""
        args = ["--proyecto", str(self.proyecto), "--json"]
        with mock.patch.object(tareas_git, "_git", side_effect=FileNotFoundError("git")):
            with contextlib.redirect_stderr(io.StringIO()) as salida:
                rc = tareas_git.cmd_seguimiento(args, args)
        self.assertEqual(rc, 1)
        self.assertIn("ERROR", salida.getvalue())
