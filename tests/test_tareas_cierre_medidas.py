"""Criterios de cierre declarativos, independientes del catálogo y del motor."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools import cli, tareas


class CierreMedidasTests(unittest.TestCase):
    def documento(self, campo=""):
        return "# Cierre\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n" + campo + "\nCuerpo\n"

    def parsear(self, campo=""):
        return tareas.parsear_tarea(self.documento(campo), Path("tareas/ejemplo/TAREA.md"))

    def test_opcional_vacio_y_json(self):
        for campo in ("", "- CIERRA CON: \n"):
            with self.subTest(campo=campo):
                tarea = self.parsear(campo)
                self.assertEqual(tarea.cierra_con, ())
                self.assertEqual(tarea.a_dict()["cierra_con"], [])

    def test_sanea_espacios_y_repeticiones_sin_cambiar_identidad(self):
        tarea = self.parsear("* cierra con:  dedos.flexion_digital , recarga.slot_2, dedos.flexion_digital\n- EXTRA: dato\n")
        self.assertEqual(tarea.cierra_con, ("dedos.flexion_digital", "recarga.slot_2"))
        self.assertEqual(tarea.a_dict()["cierra_con"], list(tarea.cierra_con))
        self.assertEqual(tarea.campos_adicionales, {"EXTRA": "dato"})

    def test_identificadores_invalidos_no_se_descartan_silenciosamente(self):
        for valor in ("simple", "Dedos.flexion", "dedos.flexión", "a..b", "a.b/otro",
                      "a.b,", ",a.b", "a.b,,c.d", "a.b c.d", "a.2b", "../a.b"):
            with self.subTest(valor=valor), self.assertRaisesRegex(tareas.TareaInvalida, "CIERRA CON"):
                self.parsear(f"- CIERRA CON: {valor}\n")

    def test_rechaza_campo_duplicado(self):
        with self.assertRaisesRegex(tareas.TareaInvalida, "duplicado"):
            self.parsear("- CIERRA CON: a.b\n- cierra con: c.d\n")

    def test_cuerpo_no_declara_medidas(self):
        tarea = self.parsear("\n- CIERRA CON: esto no es un identificador\n")
        self.assertEqual(tarea.cierra_con, ())
        self.assertIn("- CIERRA CON:", tarea.cuerpo)

    def test_cierre_antes_de_estado_no_interrumpe_metadatos(self):
        tarea = tareas.parsear_tarea("# Cierre\n\n- CIERRA CON: a.b\n- ESTADO: ABIERTA\n- PRIORIDAD: 1\n", Path("TAREA.md"))
        self.assertEqual(tarea.cierra_con, ("a.b",))
        self.assertEqual(tarea.prioridad, 1)

    def test_modificaciones_atomicas_preservan_criterio_y_bytes(self):
        for eol in ("\n", "\r\n"):
            with self.subTest(eol=eol), tempfile.TemporaryDirectory() as temporal:
                raiz = Path(temporal)
                carpeta = raiz / "tareas" / "20260921-010000-cierre"
                carpeta.mkdir(parents=True)
                ruta = carpeta / "TAREA.md"
                original = self.documento("  * cierra con: a.b,  c.d  \n- ETIQUETAS: uno\n").replace("\n", eol).encode()
                ruta.write_bytes(original)
                ruta.chmod(0o640)
                with mock.patch.object(tareas.os, "replace", side_effect=OSError("fallo construido")):
                    with self.assertRaises(OSError):
                        tareas.actualizar_estado_tarea(ruta, "CERRADA")
                self.assertEqual(ruta.read_bytes(), original)
                tareas.actualizar_estado_tarea(ruta, "CERRADA")
                esperado = original.replace(b"ABIERTA", b"CERRADA")
                self.assertEqual(ruta.read_bytes(), esperado)
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    codigo = cli.main(["tarea", "etiquetar", carpeta.name, "--etiqueta", "dos", "--proyecto", str(raiz)])
                self.assertEqual(codigo, 0)
                esperado = esperado.replace(b"ETIQUETAS: uno", b"ETIQUETAS: uno, dos")
                self.assertEqual(ruta.read_bytes(), esperado)
                self.assertEqual(ruta.stat().st_mode & 0o777, 0o640)
                self.assertEqual(tareas.parsear_tarea(ruta.read_text(), ruta).cierra_con, ("a.b", "c.d"))
                self.assertEqual(list(carpeta.iterdir()), [ruta])
