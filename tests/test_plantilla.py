"""La entrega no ejecuta el sensor ni pisa contenido del consumidor."""
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import cli, plantilla


class Plantilla(unittest.TestCase):
    def ejecutar(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return cli.main(['plantilla', *map(str, args)])

    def test_copia_completa_sin_resolver_proyecto_ni_ejecutar_sensor(self):
        with tempfile.TemporaryDirectory() as td, patch.object(cli, 'resolver', side_effect=AssertionError):
            destino = Path(td) / 'prosa á'
            self.assertEqual(self.ejecutar('sensor-prosa', destino), 0)
            esperados = dict(plantilla.archivos(plantilla.fuente()))
            self.assertEqual({p.relative_to(destino): p.read_bytes()
                              for p in destino.rglob('*') if p.is_file()}, esperados)
            self.assertFalse((destino / 'corrida').exists())

    def test_rechaza_directorio_archivo_y_enlace_incluso_roto(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            directorio = raiz / 'directorio'
            directorio.mkdir()
            archivo = raiz / 'archivo'
            archivo.write_bytes(b'contenido propio')
            enlace = raiz / 'enlace'
            enlace.symlink_to(directorio, target_is_directory=True)
            roto = raiz / 'roto'
            roto.symlink_to(raiz / 'ausente')
            for destino in (directorio, archivo, enlace, roto):
                with self.subTest(destino=destino):
                    self.assertEqual(self.ejecutar('sensor-prosa', destino), 1)
            self.assertEqual(list(directorio.iterdir()), [])
            self.assertEqual(archivo.read_bytes(), b'contenido propio')
            self.assertTrue(enlace.is_symlink())
            self.assertTrue(roto.is_symlink())

    def test_argumentos_invalidos_no_crean_destino(self):
        with tempfile.TemporaryDirectory() as td:
            destino = Path(td) / 'prosa'
            self.assertEqual(self.ejecutar('desconocida', destino), 1)
            for args in [('sensor-prosa',),
                         ('sensor-prosa', destino, 'extra')]:
                with self.subTest(args=args), self.assertRaises(SystemExit) as error:
                    self.ejecutar(*args)
                self.assertEqual(error.exception.code, 2)
            self.assertFalse(destino.exists())
