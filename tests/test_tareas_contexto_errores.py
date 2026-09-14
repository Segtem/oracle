"""P2 conserva datos y diagnósticos ante colisiones, E/S y nombres multilínea."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tools import cli, tareas_contexto


class ErroresContextoTests(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name).resolve()
        self.identidad = '20260913-020000-adjunto'
        self.carpeta = self.raiz / 'tareas' / self.identidad
        self.carpeta.mkdir(parents=True)
        self.documento = self.carpeta / 'TAREA.md'
        self.original = (b'# Adjunto\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n'
                         b'- ETIQUETAS: Bug, Bug, bug\n\nContenido original.\n')
        self.documento.write_bytes(self.original)
        self.origen = self.raiz / 'captura.txt'
        self.contenido = b'Captura construida\n'
        self.origen.write_bytes(self.contenido)
        self.destino = self.carpeta / self.origen.name

    def ejecutar(self, *args):
        salida, error = io.StringIO(), io.StringIO()
        with redirect_stdout(salida), redirect_stderr(error):
            codigo = cli.main(['tarea', *args, '--proyecto', str(self.raiz)])
        return codigo, salida.getvalue(), error.getvalue()

    def adjuntar_falla(self, origen=None):
        codigo, salida, error = self.ejecutar('adjuntar', self.identidad,
                                             str(origen or self.origen))
        self.assertEqual(codigo, 1, (salida, error))
        self.assertEqual(salida, '')
        self.assertIn('ERROR', error)
        self.assertNotIn('Traceback', error)
        self.assertEqual(self.documento.read_bytes(), self.original)
        self.assertEqual(self.origen.read_bytes(), self.contenido)
        return error

    def test_permiso_denegado_no_se_presenta_como_archivo_ausente(self):
        """Path.exists oculta OSError; la captura conserva el diagnóstico de acceso denegado."""
        with patch.object(Path, 'stat', side_effect=PermissionError('lectura denegada')):
            with patch.object(tareas_contexto.os, 'lstat', side_effect=PermissionError('lectura denegada')):
                with redirect_stdout(io.StringIO()) as salida, redirect_stderr(io.StringIO()) as error:
                    codigo = tareas_contexto.cmd_adjuntar([], ['20260913-050000-tarea', str(self.origen)])
        self.assertEqual(codigo, 1)
        self.assertEqual(salida.getvalue(), '')
        self.assertIn('lectura denegada', error.getvalue())
        self.assertNotIn('no existe', error.getvalue())
        self.assertEqual(self.origen.read_bytes(), self.contenido)

    def test_separadores_unicode_no_generan_enlaces_partidos(self):
        """Zl/Zp son saltos para los lectores internos aunque no pertenezcan a Cc."""
        for separador in ('\u2028', '\u2029'):
            with self.subTest(separador=repr(separador)):
                origen = self.raiz / f'captura{separador}partida.txt'
                origen.write_bytes(self.contenido)
                self.adjuntar_falla(origen)
                self.assertFalse((self.carpeta / origen.name).exists())
                self.assertEqual(origen.read_bytes(), self.contenido)

    def test_colision_posterior_a_comprobacion_conserva_archivo_competidor(self):
        """Si otro escritor gana O_EXCL, el rollback no borra su archivo."""
        abrir_real = os.open
        competidor = b'Contenido del otro escritor\n'
        def abrir(path, flags, *args, **kwargs):
            if Path(path) == self.destino:
                self.destino.write_bytes(competidor)
            return abrir_real(path, flags, *args, **kwargs)
        with patch.object(tareas_contexto.os, 'open', side_effect=abrir):
            self.adjuntar_falla()
        self.assertEqual(self.destino.read_bytes(), competidor)

    def test_fsync_de_copia_fallido_revierte_adjunto(self):
        """El adjunto no se confirma ni registra si falla su propia sincronización."""
        with patch.object(tareas_contexto.os, 'fsync', side_effect=OSError('copia no sincronizada')):
            error = self.adjuntar_falla()
        self.assertIn('copia no sincronizada', error)
        self.assertFalse(self.destino.exists())

    def test_lectura_regular_funciona_sin_flags_opcionales(self):
        """La ausencia de extensiones POSIX no debe abrir una nota en modo escritura."""
        with patch.dict(tareas_contexto.os.__dict__):
            tareas_contexto.os.__dict__.pop('O_NOFOLLOW', None)
            tareas_contexto.os.__dict__.pop('O_NONBLOCK', None)
            resultado = tareas_contexto.leer_archivo_texto_si_aplica(self.origen)
        self.assertEqual(resultado, (['Captura construida'], None, False))
        self.assertEqual(self.origen.read_bytes(), self.contenido)

    def test_lectura_no_solicita_mas_del_limite_y_un_byte_de_deteccion(self):
        """El lector tiene un presupuesto de E/S, incluso si el archivo crece sin límite."""
        solicitudes = []
        abrir_real = open
        class LecturaObservada:
            def __init__(self, *args, **kwargs):
                self.archivo = abrir_real(*args, **kwargs)
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return self.archivo.__exit__(*args)
            def read(self, cantidad=-1):
                solicitudes.append(cantidad)
                return self.archivo.read(cantidad)
        with patch('tools.tareas_contexto.open', LecturaObservada, create=True):
            resultado = tareas_contexto.leer_archivo_texto_si_aplica(self.origen)
        self.assertEqual(resultado, (['Captura construida'], None, False))
        self.assertTrue(solicitudes)
        self.assertTrue(all(0 <= n <= 2 * 1024 * 1024 + 1 for n in solicitudes), solicitudes)

    def test_adjunto_grande_informa_tamano_exacto_antes_de_copiar(self):
        """Los bytes exactos permiten decidir si autorizar el adjunto sin redondeos ocultos."""
        grande = self.raiz / 'grande.txt'
        tamano = 20 * 1024 * 1024 + 1
        with grande.open('wb') as archivo:
            archivo.truncate(tamano)
        error = self.adjuntar_falla(grande)
        self.assertIn(f'{tamano} bytes', error)
        self.assertIn('20 MiB', error)
        self.assertIn('--permitir-grande', error)
        self.assertFalse((self.carpeta / grande.name).exists())

    def test_adjunto_que_crece_informa_bytes_observados_durante_copia(self):
        """Si stat quedó viejo, el diagnóstico informa el acumulado que excedió el límite."""
        grande = self.raiz / 'crece.txt'
        tamano = 20 * 1024 * 1024 + 1
        with grande.open('wb') as archivo:
            archivo.truncate(tamano)
        lstat_real = os.lstat
        def consultar(path, *args, **kwargs):
            dato = lstat_real(path, *args, **kwargs)
            if Path(path) == grande:
                return SimpleNamespace(st_mode=dato.st_mode, st_size=1)
            return dato
        with patch.object(tareas_contexto.os, 'lstat', side_effect=consultar):
            error = self.adjuntar_falla(grande)
        self.assertIn(f'{tamano} bytes', error)
        self.assertIn('20 MiB', error)
        self.assertIn('--permitir-grande', error)
        self.assertFalse((self.carpeta / grande.name).exists())
        self.assertEqual(grande.stat().st_size, tamano)

    def bloquear_borrado(self):
        borrar_real = Path.unlink
        def borrar(path, *args, **kwargs):
            if path == self.destino:
                raise PermissionError('reversión denegada')
            return borrar_real(path, *args, **kwargs)
        return patch.object(Path, 'unlink', autospec=True, side_effect=borrar)

    def test_fallo_de_registro_y_reversion_preserva_ambos_diagnosticos(self):
        """El fallo secundario de limpieza no debe ocultar por qué no se registró la copia."""
        with self.bloquear_borrado(), patch.object(
            tareas_contexto, 'guardar_documento_atomico', side_effect=OSError('registro rechazado')
        ):
            error = self.adjuntar_falla()
        self.assertIn('registro rechazado', error)
        self.assertIn('reversión denegada', error)
        self.assertIn(str(self.destino), error)
        self.assertEqual(self.destino.read_bytes(), self.contenido)

    def test_fallo_de_copia_y_reversion_preserva_ambos_diagnosticos(self):
        """Si la copia falla y queda un residuo, el usuario recibe causa y ruta recuperable."""
        with self.bloquear_borrado(), patch.object(
            tareas_contexto.os, 'fsync', side_effect=OSError('copia no sincronizada')
        ):
            error = self.adjuntar_falla()
        self.assertIn('copia no sincronizada', error)
        self.assertIn('reversión denegada', error)
        self.assertIn(str(self.destino), error)
        self.assertEqual(self.destino.read_bytes(), self.contenido)

    def test_copia_ya_eliminada_no_genera_fallo_falso_de_limpieza(self):
        """Otro actor puede borrar la copia fallida antes del rollback: no queda residuo."""
        def fallar_copia(*args):
            self.destino.unlink()
            raise OSError('copia interrumpida')
        with patch.object(tareas_contexto.os, 'fsync', side_effect=fallar_copia):
            error = self.adjuntar_falla()
        self.assertIn('copia interrumpida', error)
        self.assertEqual(error.count('ERROR:'), 1, error)
        self.assertNotIn('sin registrar', error)
        self.assertFalse(self.destino.exists())

    def test_registro_fallido_con_copia_ya_eliminada_no_inventa_residuo(self):
        """No se informa una reversión fallida si la copia ya desapareció al fallar registro."""
        def fallar_registro(*args):
            self.destino.unlink()
            raise OSError('registro interrumpido')
        with patch.object(tareas_contexto, 'guardar_documento_atomico', side_effect=fallar_registro):
            error = self.adjuntar_falla()
        self.assertIn('registro interrumpido', error)
        self.assertEqual(error.count('ERROR:'), 1, error)
        self.assertNotIn('sin registrar', error)
        self.assertFalse(self.destino.exists())

    def test_busqueda_no_acepta_directorio_con_nombre_no_id(self):
        """La auditoría descarta estructuras inválidas antes de recorrer notas de tareas."""
        ajena = self.raiz / 'tareas' / 'otra-carpeta'
        ajena.mkdir()
        (ajena / 'nota.txt').write_text('dato que no debe ocultar el registro inválido')
        codigo, salida, error = self.ejecutar('buscar', 'dato', '--json')
        self.assertEqual(codigo, 1)
        self.assertEqual(salida, '')
        self.assertIn('otra-carpeta', error)
        self.assertIn('inválido', error)

    def test_resumen_deduplica_etiquetas_ya_limpias_sin_cambiar_identidad(self):
        """La simplificación conserva conteo por tarea y distingue Bug de bug."""
        codigo, salida, error = self.ejecutar('resumen', '--json')
        self.assertEqual(codigo, 0, error)
        self.assertEqual(json.loads(salida)['etiquetas'], {'Bug': 1, 'bug': 1})


if __name__ == '__main__':
    unittest.main()
