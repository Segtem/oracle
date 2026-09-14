"""Límites que no pueden desaparecer sin perder el rechazo o la integridad del tracker."""

import datetime
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools import tareas


class LimitesDeTareasTests(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory(prefix="oracle-limites-")
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        self.tracker = self.raiz / "tareas"
        self.tracker.mkdir()
        self.documento = self.tracker / "20260913-050000-limite" / "TAREA.md"

    def test_parser_no_exige_linea_vacia_tras_titulo(self):
        """Saltar dos líneas después del título perdía ESTADO en el documento mínimo válido."""
        tarea = tareas.parsear_tarea("# x\n- ESTADO: ABIERTA\n- PRIORIDAD: 0", self.documento)
        self.assertEqual((tarea.titulo, tarea.estado, tarea.prioridad), ("x", "ABIERTA", 0))

    def test_init_crea_los_padres_del_proyecto_pedido(self):
        """Una ruta explícita nueva puede tener varios padres ausentes y debe quedar utilizable."""
        proyecto = self.raiz / "nuevo" / "proyecto"
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            codigo = tareas.cmd_init([], ["--proyecto", str(proyecto)])
        self.assertEqual(codigo, 0)
        self.assertTrue((proyecto / "tareas" / "README.md").is_file())
        self.assertIn(str(proyecto / "tareas"), salida.getvalue())

    def test_ver_json_devuelve_exito_explicito_y_el_documento_leido(self):
        """Emitir JSON correcto no basta si el código de salida declara fallo o no devuelve un entero."""
        self.documento.parent.mkdir()
        self.documento.write_text("# x\n- ESTADO: ABIERTA\n- PRIORIDAD: 0")
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            codigo = tareas.cmd_ver([], [self.documento.parent.name, "--json", "--proyecto", str(self.raiz)])
        self.assertEqual(codigo, 0)
        datos = json.loads(salida.getvalue())
        self.assertEqual((datos["id"], datos["titulo"], datos["ruta"]),
                         (self.documento.parent.name, "x", str(self.documento)))

    def test_parser_vacio_es_error_de_dominio_sin_indexerror(self):
        """Un documento vacío o sólo con saltos de línea debe rechazarse como TareaInvalida."""
        for texto in ("", "\n", " \n\t\n"):
            with self.subTest(texto=texto), self.assertRaises(tareas.TareaInvalida):
                tareas.parsear_tarea(texto, self.documento)

    def test_confinamiento_rechaza_destinos_internos_inexistentes(self):
        """Estar dentro del tracker no basta: un destino roto no acredita un archivo utilizable."""
        for funcion in (tareas.asegurar_confinamiento, tareas.asegurar_confinamiento_archivo):
            for ruta in (self.documento, self.tracker / "roto"):
                with self.subTest(funcion=funcion.__name__, ruta=ruta):
                    with self.assertRaises(tareas.RutaInsegura):
                        funcion(self.tracker, ruta)

    def test_enlace_roto_directo_se_diagnostica_como_ruta_insegura(self):
        """Un enlace roto con ID parcial no debe ocultarse como una tarea simplemente inexistente."""
        (self.tracker / "roto").symlink_to(self.raiz / "ausente")
        with self.assertRaises(tareas.RutaInsegura):
            tareas.resolver_id_o_prefijo(self.tracker, "roto")

    def test_auditoria_de_tracker_ausente_y_simbolico_devuelve_problemas(self):
        """Los llamadores necesitan la pareja tareas/problemas incluso cuando no pueden recorrer."""
        enlace = self.raiz / "enlace"
        enlace.symlink_to(self.tracker, target_is_directory=True)
        for ruta, motivo in ((self.raiz / "ausente", "no existe"), (enlace, "simbólico")):
            with self.subTest(ruta=ruta):
                validas, problemas = tareas.auditar_tareas(ruta)
                self.assertEqual(validas, [])
                self.assertEqual(len(problemas), 1)
                self.assertIn(motivo, problemas[0])

    def test_auditoria_no_oculta_enlace_roto_dentro_del_tracker(self):
        """Resolver sin existencia convertiría un enlace roto interno en una entrada ignorada."""
        (self.tracker / "20260913-050000-roto").symlink_to(self.tracker / "ausente")
        validas, problemas = tareas.auditar_tareas(self.tracker)
        self.assertEqual(validas, [])
        self.assertEqual(len(problemas), 1)
        self.assertIn("roto o inválido", problemas[0])

    def test_colisiones_agotadas_tienen_un_presupuesto_finito(self):
        """Una carpeta ocupada por cada reintento no permite superar 10.000 reservas ni esperar sin fin."""
        fecha = datetime.datetime(2026, 9, 13, 5, tzinfo=datetime.timezone.utc)
        with mock.patch.object(tareas.os, "mkdir", side_effect=FileExistsError) as reservar:
            with self.assertRaises(tareas.TareaError):
                tareas.crear_carpeta_tarea_atomica(self.tracker, "x", fecha)
        self.assertEqual(reservar.call_count, 10000)
        self.assertEqual(reservar.call_args.args[0].name, "20260913-050000-x-9999")

    def test_error_al_enumerar_no_filtra_excepcion_desde_los_comandos(self):
        """Listar, revisar y resolver un prefijo no pueden presentar una lectura fallida como éxito."""
        for funcion, args in ((tareas.cmd_listar, []), (tareas.cmd_revisar, []),
                              (tareas.cmd_ver, ["20260913"]),
                              (tareas.cmd_cerrar, ["20260913"]),
                              (tareas.cmd_reabrir, ["20260913"])):
            with self.subTest(funcion=funcion.__name__):
                with mock.patch.object(Path, "iterdir", side_effect=PermissionError("listado denegado")):
                    with contextlib.redirect_stdout(io.StringIO()) as salida:
                        with contextlib.redirect_stderr(io.StringIO()) as error:
                            codigo = funcion([], [*args, "--proyecto", str(self.raiz)])
                self.assertEqual(codigo, 1)
                self.assertEqual(salida.getvalue(), "")
                self.assertIn("listado denegado", error.getvalue())

    def test_separadores_unicode_no_crean_documentos_invalidos(self):
        """Los separadores de splitlines también rompen título/metadatos, aunque no sean CR/LF."""
        for separador in ("\n", "\r", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029"):
            for args in (["antes" + separador + "después"], ["Título", "--etiqueta", "antes" + separador + "después"]):
                with self.subTest(separador=repr(separador), args=args):
                    with contextlib.redirect_stdout(io.StringIO()) as salida:
                        with contextlib.redirect_stderr(io.StringIO()) as error:
                            codigo = tareas.cmd_nueva([], [*args, "--proyecto", str(self.raiz)])
                    self.assertEqual(codigo, 1)
                    self.assertEqual(salida.getvalue(), "")
                    self.assertIn("saltos de línea", error.getvalue())
                    self.assertEqual(list(self.tracker.iterdir()), [])

    def test_etiqueta_vacia_se_omite_sin_invalidar_la_tarea(self):
        """El rechazo de saltos no cambia el permiso de omitir etiquetas vacías."""
        with contextlib.redirect_stdout(io.StringIO()) as salida:
            codigo = tareas.cmd_nueva([], ["Sin etiquetas", "--etiqueta", "", "--json", "--proyecto", str(self.raiz)])
        self.assertEqual(codigo, 0)
        documento = Path(json.loads(salida.getvalue())["ruta"])
        self.assertEqual(tareas.parsear_tarea(documento.read_text(), documento).etiquetas, ())
