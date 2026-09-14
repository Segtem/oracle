"""Una preparación fallida no reemplaza documentos ni deja adjuntos sin registrar."""

import contextlib
import io
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock

from tools import cli, tareas


class EscriturasAtomicasTests(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory(prefix="oracle-escritura-")
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        self.identidad = "20260913-010000-escritura"
        self.carpeta = self.raiz / "tareas" / self.identidad
        self.carpeta.mkdir(parents=True)
        self.documento = self.carpeta / "TAREA.md"
        self.original = ("# Investigación ñ\r\n\r\n- ESTADO: ABIERTA\r\n"
                         "- PRIORIDAD: 40\r\n\r\nTexto original.\r\n").encode()
        self.documento.write_bytes(self.original)
        self.documento.chmod(0o640)

    def intacto(self):
        self.assertEqual(self.documento.read_bytes(), self.original)
        self.assertEqual(stat.S_IMODE(self.documento.stat().st_mode), 0o640)
        self.assertEqual(list(self.carpeta.iterdir()), [self.documento])

    def test_fallos_antes_del_reemplazo_conservan_original_y_limpian_temporal(self):
        """Antes se ignoraba el fallo de chmod y se confirmaba una copia con modo 0600."""
        for operacion in ("chmod", "fsync", "replace"):
            with self.subTest(operacion=operacion):
                with mock.patch.object(tareas.os, operacion, side_effect=OSError("fallo construido")):
                    with self.assertRaisesRegex(OSError, "fallo construido"):
                        tareas.guardar_documento_atomico(self.documento, b"contenido nuevo")
                self.intacto()

    def test_stat_fallido_no_recurre_a_permisos_predeterminados(self):
        """Un fallo al conocer los permisos no autoriza reemplazar el documento con 0644."""
        with mock.patch.object(Path, "stat", side_effect=OSError("stat construido")):
            with self.assertRaisesRegex(OSError, "stat construido"):
                tareas.guardar_documento_atomico(self.documento, b"contenido nuevo")
        self.intacto()

    def test_los_tres_comandos_rechazan_fallo_de_permisos_sin_dejar_cambios(self):
        """Cerrar, anotar y adjuntar comparten el rechazo; adjuntar revierte además su copia."""
        origen = self.raiz / "registro.txt"
        origen.write_bytes(b"registro construido")
        for verbo, argumentos in (("cerrar", []), ("anotar", ["Nota nueva"]),
                                 ("adjuntar", [str(origen)])):
            with self.subTest(verbo=verbo), contextlib.redirect_stdout(io.StringIO()) as salida:
                with contextlib.redirect_stderr(io.StringIO()) as error:
                    with mock.patch.object(tareas.os, "chmod", side_effect=OSError("chmod construido")):
                        codigo = cli.main(["tarea", verbo, self.identidad, *argumentos,
                                           "--proyecto", str(self.raiz)])
                self.assertEqual(codigo, 1, salida.getvalue())
                self.assertIn("chmod construido", error.getvalue())
            self.intacto()
        self.assertEqual(origen.read_bytes(), b"registro construido")

    @unittest.skipUnless(os.name == "posix", "modo POSIX")
    def test_actualizacion_preserva_modo_posix_y_bytes_ajenos_al_estado(self):
        """El modo incluye bits especiales; en UTF-8/CRLF sólo cambia el valor del estado."""
        self.documento.chmod(0o1640)
        self.assertTrue(tareas.actualizar_estado_tarea(self.documento, "CERRADA"))
        self.assertEqual(self.documento.read_bytes(), self.original.replace(b"ABIERTA", b"CERRADA"))
        self.assertEqual(stat.S_IMODE(self.documento.stat().st_mode), 0o1640)
        self.assertFalse(tareas.actualizar_estado_tarea(self.documento, "CERRADA"))
