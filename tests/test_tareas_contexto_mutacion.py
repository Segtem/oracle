"""Contratos P2 observables en proceso: límites, diagnósticos y captura de contexto."""
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tools import cli, tareas_contexto
from tools.tareas import TareaError


class ContextoMutacionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name).resolve()
        (self.raiz / '.git').mkdir()
        self.assertEqual(self.ejecutar('init')[0], 0)
        rc, out, err = self.ejecutar('nueva', 'Contexto verificable', '--sufijo', 'contexto', '--json')
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        self.id = datos['id']
        self.documento = Path(datos['ruta'])
        self.carpeta = self.documento.parent
        self.origen = self.raiz / 'captura.txt'
        self.origen.write_bytes(b'captura original\n')

    def ejecutar(self, *args, raiz=None):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = cli.main(['--proyecto', str(raiz or self.raiz), 'tarea', *args])
        return rc, out.getvalue(), err.getvalue()

    def exito(self, *args):
        rc, out, err = self.ejecutar(*args, '--json')
        self.assertEqual(rc, 0, err)
        self.assertEqual(err, '')
        return json.loads(out)

    def fallo(self, *args, raiz=None):
        rc, out, err = self.ejecutar(*args, raiz=raiz)
        self.assertEqual(rc, 1, (out, err))
        self.assertEqual(out, '')
        self.assertIn('ERROR', err)
        self.assertNotIn('Traceback', err)
        return err

    def test_lector_admite_exactamente_dos_mib_y_omite_el_byte_siguiente(self):
        """El borde documentado admite 2 MiB, pero no un archivo apenas mayor."""
        ruta = self.carpeta / 'limite.txt'
        limite = 2 * 1024 * 1024
        ruta.write_bytes(b'a' * limite)
        self.assertEqual(tareas_contexto.leer_archivo_texto_si_aplica(ruta), (['a' * limite], None, False))
        ruta.write_bytes(b'a' * (limite + 1))
        lineas, motivo, error = tareas_contexto.leer_archivo_texto_si_aplica(ruta)
        self.assertIsNone(lineas)
        self.assertIn('2 MiB', motivo)
        self.assertFalse(error)

    def test_lector_omite_crecimiento_posterior_a_stat(self):
        """Un archivo que crece tras consultar su tamaño no se lee como texto completo."""
        ruta = self.carpeta / 'crece.txt'
        ruta.write_bytes(b'a' * (2 * 1024 * 1024 + 1))
        real_lstat = os.lstat
        def tamaño_anterior(path, *args, **kwargs):
            dato = real_lstat(path, *args, **kwargs)
            if Path(path) == ruta:
                return SimpleNamespace(st_mode=dato.st_mode, st_size=10)
            return dato
        with patch.object(tareas_contexto.os, 'lstat', side_effect=tamaño_anterior):
            lineas, motivo, error = tareas_contexto.leer_archivo_texto_si_aplica(ruta)
        self.assertIsNone(lineas)
        self.assertIn('2 MiB', motivo)
        self.assertFalse(error)

    def test_lector_distingue_omisiones_de_error_operacional(self):
        """Binarios, codificación y extensión ajenas son omisiones; la ausencia es error."""
        for nombre, contenido, diagnostico in (
            ('bytes.txt', b'a\x00b', 'binario'),
            ('latin.txt', b'\xff', 'UTF-8'),
            ('formato.desconocido', b'texto', 'extensión'),
            ('imagen.PNG', b'texto', 'binario'),
        ):
            with self.subTest(nombre=nombre):
                ruta = self.carpeta / nombre
                ruta.write_bytes(contenido)
                lineas, motivo, error = tareas_contexto.leer_archivo_texto_si_aplica(ruta)
                self.assertIsNone(lineas)
                self.assertIn(diagnostico, motivo)
                self.assertIs(error, False)
        lineas, motivo, error = tareas_contexto.leer_archivo_texto_si_aplica(self.carpeta / 'ausente.txt')
        self.assertIsNone(lineas)
        self.assertIn('ausente.txt', motivo)
        self.assertIs(error, True)

    def test_lector_no_exige_extension_y_conserva_lineas_vacias(self):
        """Una nota sin extensión sigue siendo texto UTF-8 y mantiene su numeración."""
        ruta = self.carpeta / 'NOTAS'
        ruta.write_bytes('uno\r\n\r\ndos ñ\n'.encode())
        self.assertEqual(tareas_contexto.leer_archivo_texto_si_aplica(ruta), (['uno', '', 'dos ñ'], None, False))

    def test_lector_reporta_fallo_de_apertura_como_error(self):
        """Un permiso denegado no debe convertirse en omisión exitosa ni traceback."""
        with patch.object(tareas_contexto.os, 'open', side_effect=PermissionError('lectura denegada')):
            lineas, motivo, error = tareas_contexto.leer_archivo_texto_si_aplica(self.origen)
        self.assertIsNone(lineas)
        self.assertIn('lectura denegada', motivo)
        self.assertIs(error, True)

    def test_url_rechaza_del_controles_y_tipos_ajenos(self):
        """La validación excluye controles y valores ajenos sin normalizar URLs válidas."""
        for url in (None, 123, '', 'https://host/a\x7fb', 'https://host/a\x1fb'):
            with self.subTest(url=url), self.assertRaises(TareaError):
                tareas_contexto.validar_url_estricta(url)
        self.assertIsNone(tareas_contexto.validar_url_estricta('HTTPS://host:443/a?x=1&y=2#ñ'))

    def test_anotar_solo_url_conserva_datos_y_fecha_utc(self):
        """Una URL sola es una nota útil y devuelve el ID, documento y fecha de captura."""
        url = 'HTTPS://host/a?t=92&x=ñ#seccion'
        datos = self.exito('anotar', self.id, '--url', url)
        self.assertEqual(datos['id'], self.id)
        self.assertEqual(Path(datos['documento']), self.documento)
        self.assertIsNone(datos['texto'])
        self.assertIsNone(datos['marca'])
        self.assertEqual(datos['url'], url)
        self.assertRegex(datos['fecha'], r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC$')
        self.assertIn(f'- URL: {url}\n', self.documento.read_text())

    def test_nota_blanca_no_modifica_documento(self):
        """Una cadena explícita de espacios no se registra como nota vacía."""
        antes = self.documento.read_bytes()
        self.fallo('anotar', self.id, ' \t\n ')
        self.assertEqual(self.documento.read_bytes(), antes)

    def test_capturas_preservan_crlf_y_separan_bloque_previo(self):
        """Notas y adjuntos preservan bytes anteriores y el estilo CRLF, con cualquier final."""
        base = self.documento.read_bytes().replace(b'\n', b'\r\n').rstrip(b'\r\n')
        for verbo in ('anotar', 'adjuntar'):
            for saltos in (0, 1, 2):
                with self.subTest(verbo=verbo, saltos=saltos):
                    antes = base + b'\r\n' * saltos
                    self.documento.write_bytes(antes)
                    if verbo == 'anotar':
                        datos = self.exito(verbo, self.id, 'nota posterior')
                    else:
                        fuente = self.raiz / f'adjunto-{saltos}.txt'
                        fuente.write_bytes(b'dato')
                        datos = self.exito(verbo, self.id, str(fuente))
                        self.assertEqual(datos['id'], self.id)
                    despues = self.documento.read_bytes()
                    self.assertTrue(despues.startswith(antes))
                    self.assertNotIn(b'\n', despues.replace(b'\r\n', b''))
                    marcador = b'### Nota (' if verbo == 'anotar' else b'- Adjunto:'
                    self.assertIn(base + b'\r\n\r\n' + marcador, despues)

    def test_captura_documento_ausente_invalido_o_no_utf8_falla(self):
        """La captura exige un registro legible y válido; no deja un adjunto huérfano."""
        for contenido in (None, b'\xff', b'# Sin metadatos\n'):
            for verbo in ('anotar', 'adjuntar'):
                with self.subTest(contenido=contenido, verbo=verbo):
                    if contenido is None:
                        self.documento.unlink(missing_ok=True)
                    else:
                        self.documento.write_bytes(contenido)
                    args = [verbo, self.id, 'nota' if verbo == 'anotar' else str(self.origen)]
                    self.fallo(*args)
                    self.assertFalse((self.carpeta / self.origen.name).exists())
                    if contenido is not None:
                        self.assertEqual(self.documento.read_bytes(), contenido)

    def test_anotar_fallo_lectura_no_modifica_documento(self):
        """Una lectura fallida del registro no emite confirmación de nota guardada."""
        antes = self.documento.read_bytes()
        with patch.object(Path, 'read_bytes', side_effect=PermissionError('documento denegado')):
            self.assertIn('documento denegado', self.fallo('anotar', self.id, 'nota'))
        self.assertEqual(self.documento.read_bytes(), antes)

    def test_capturas_no_siguen_documento_simbolico(self):
        """La nota central enlazada no permite escribir en otro documento del proyecto."""
        original = self.documento.read_bytes()
        exterior = self.raiz / 'documento-externo.md'
        exterior.write_bytes(original)
        self.documento.unlink()
        self.documento.symlink_to(exterior)
        for args in (('anotar', self.id, 'nota'), ('adjuntar', self.id, str(self.origen))):
            with self.subTest(args=args):
                self.fallo(*args)
                self.assertEqual(exterior.read_bytes(), original)
                self.assertFalse((self.carpeta / self.origen.name).exists())

    def test_verbos_reportan_tracker_ausente_y_no_lo_crean(self):
        """Los verbos P2 requieren inicialización explícita y conservan el código operacional 1."""
        vacio = self.raiz / 'otro'
        vacio.mkdir()
        for args in (('anotar', self.id, 'nota'), ('adjuntar', self.id, str(self.origen)),
                     ('buscar', 'dato'), ('referencias', self.id), ('resumen',)):
            with self.subTest(args=args):
                self.fallo(*args, raiz=vacio)
                self.assertEqual(list(vacio.iterdir()), [])

    def test_verbos_con_id_reportan_id_ausente(self):
        """Un ID inexistente no se confunde con una operación exitosa sin resultado."""
        for args in (('anotar', '19990101-000000-ausente', 'nota'),
                     ('adjuntar', '19990101-000000-ausente', str(self.origen)),
                     ('referencias', '19990101-000000-ausente')):
            with self.subTest(args=args):
                self.fallo(*args)

    def test_adjuntar_rechaza_origen_ausente_directorio_y_control_del(self):
        """La fuente debe ser regular y su nombre no debe introducir controles en Markdown."""
        control = self.raiz / 'control\x7f.txt'
        control.write_bytes(b'x')
        for ruta in (self.raiz / 'ausente.txt', self.raiz, control):
            with self.subTest(ruta=ruta):
                self.fallo('adjuntar', self.id, str(ruta))

    def test_adjuntar_limite_exacto_veinte_mib(self):
        """El tamaño máximo por defecto está incluido, incluso durante la copia acumulada."""
        self.origen.write_bytes(b'x' * (20 * 1024 * 1024))
        datos = self.exito('adjuntar', self.id, str(self.origen))
        self.assertEqual(Path(datos['ruta']).stat().st_size, 20 * 1024 * 1024)
        self.assertEqual(Path(datos['documento']), self.documento)

    def test_adjuntar_rechaza_crecimiento_durante_la_copia(self):
        """El límite se controla también al copiar cuando el tamaño anunciado quedó viejo."""
        self.origen.write_bytes(b'x' * (20 * 1024 * 1024 + 1))
        antes = self.documento.read_bytes()
        real_lstat = os.lstat
        def tamaño_anterior(path, *args, **kwargs):
            dato = real_lstat(path, *args, **kwargs)
            if Path(path) == self.origen:
                return SimpleNamespace(st_mode=dato.st_mode, st_size=1)
            return dato
        with patch.object(tareas_contexto.os, 'lstat', side_effect=tamaño_anterior):
            err = self.fallo('adjuntar', self.id, str(self.origen))
        self.assertIn('20 MiB', err)
        self.assertIn('--permitir-grande', err)
        self.assertFalse((self.carpeta / self.origen.name).exists())
        self.assertEqual(self.documento.read_bytes(), antes)
        self.assertEqual(self.origen.stat().st_size, 20 * 1024 * 1024 + 1)

    def test_adjuntar_error_al_consultar_origen_es_operacional(self):
        """Una consulta de metadatos fallida se informa sin generar ningún adjunto."""
        real_lstat = os.lstat
        def consultar(path, *args, **kwargs):
            if Path(path) == self.origen:
                raise PermissionError('metadatos denegados')
            return real_lstat(path, *args, **kwargs)
        with patch.object(tareas_contexto.os, 'lstat', side_effect=consultar):
            self.assertIn('metadatos denegados', self.fallo('adjuntar', self.id, str(self.origen)))
        self.assertFalse((self.carpeta / self.origen.name).exists())

    def test_busqueda_archivo_raiz_es_literal_sin_distincion_de_caja(self):
        """Las notas del tracker fuera de tareas conservan ruta, texto y números de línea."""
        ruta = self.raiz / 'tareas' / 'README'
        ruta.write_text('sin coincidencia\nA+B? hallazgo\na+b? segunda\nab irrelevante\n')
        datos = self.exito('buscar', 'a+b?')
        self.assertEqual(datos['coincidencias'], [
            {'ruta': 'tareas/README', 'linea': 2, 'texto': 'A+B? hallazgo'},
            {'ruta': 'tareas/README', 'linea': 3, 'texto': 'a+b? segunda'},
        ])

    def test_busqueda_vacia_falla(self):
        """Un término vacío no equivale a encontrar todas las líneas del tracker."""
        self.fallo('buscar', '')

    def test_busqueda_publica_declara_omisiones_tanto_en_raiz_como_en_tarea(self):
        """La búsqueda distingue ausencia de coincidencias de archivos no examinados."""
        grande = self.raiz / 'tareas' / 'README'
        grande.write_bytes(b'x' * (2 * 1024 * 1024 + 1))
        desconocido = self.carpeta / 'nota.otroformato'
        desconocido.write_text('dato buscado')
        datos = self.exito('buscar', 'dato buscado')
        self.assertEqual(datos['coincidencias'], [])
        omitidos = {o['ruta']: o['motivo'] for o in datos['omitidos']}
        self.assertIn('2 MiB', omitidos[str(grande.relative_to(self.raiz))])
        self.assertIn('extensión', omitidos[str(desconocido.relative_to(self.raiz))])

    def test_consultas_no_ocultan_errores_de_lectura(self):
        """Fallar al leer una nota raíz o anidada invalida la consulta, también referencias."""
        leer = tareas_contexto.leer_archivo_texto_si_aplica
        for ruta, args in ((self.raiz / 'tareas' / 'README', ('buscar', 'dato')),
                           (self.carpeta / 'anidada.txt', ('buscar', 'dato')),
                           (self.raiz / 'codigo.py', ('referencias', self.id))):
            ruta.write_text('dato')
            def lectura(path):
                if path == ruta:
                    return None, f'lectura denegada: {ruta.name}', True
                return leer(path)
            with self.subTest(ruta=ruta), patch.object(tareas_contexto, 'leer_archivo_texto_si_aplica', side_effect=lectura):
                self.assertIn(ruta.name, self.fallo(*args))

    def test_consultas_no_ocultan_fallo_de_recorrido(self):
        """Un recorrido incompleto por E/S debe fallar aunque no haya coincidencias."""
        def recorrido(path, **kwargs):
            kwargs['onerror'](PermissionError(13, 'recorrido denegado', str(path)))
            return iter(())
        for args in (('buscar', 'dato'), ('referencias', self.id)):
            with self.subTest(args=args), patch.object(tareas_contexto.os, 'walk', side_effect=recorrido):
                self.assertIn('recorrido denegado', self.fallo(*args))

    def test_consultas_humanas_muestran_hallazgos_y_omisiones(self):
        """La salida humana incluye contexto utilizable y reconoce lo que no examinó."""
        nota = self.carpeta / 'nota.txt'
        nota.write_text(f'primera\nDato asociado ({self.id})\n')
        (self.carpeta / 'oculto.bin').write_bytes(b'\x00')
        rel = nota.relative_to(self.raiz)
        for args in (('buscar', 'DATO ASOCIADO'), ('referencias', self.id)):
            with self.subTest(args=args):
                rc, out, err = self.ejecutar(*args)
                self.assertEqual(rc, 0, err)
                self.assertIn(f'{rel}:2: Dato asociado ({self.id})', out)
                self.assertIn('oculto.bin', out)
                self.assertIn('binario', out)

    def test_referencias_sin_menciones_y_resumen_sin_etiquetas_son_exitos(self):
        """Los resultados vacíos tienen diagnóstico humano y código cero."""
        rc, out, err = self.ejecutar('referencias', self.id)
        self.assertEqual(rc, 0, err)
        self.assertIn('No se encontraron referencias', out)
        self.assertIn(self.id, out)
        rc, out, err = self.ejecutar('resumen')
        self.assertEqual(rc, 0, err)
        self.assertIn('Total tareas: 1', out)
        self.assertRegex(out, r'Abiertas:\s+1')
        self.assertRegex(out, r'Cerradas:\s+0')
        self.assertIn('(ninguna)', out)

    def test_resumen_humano_cuenta_estados_y_etiquetas_sin_duplicados(self):
        """El resumen humano comunica los mismos totales que el JSON, sin duplicar etiquetas."""
        self.documento.write_text('# Contexto\n\n- ESTADO: CERRADA\n- PRIORIDAD: 50\n- ETIQUETAS: Bug, Bug, bug\n\n')
        rc, out, err = self.ejecutar('resumen')
        self.assertEqual(rc, 0, err)
        self.assertRegex(out, r'Abiertas:\s+0')
        self.assertRegex(out, r'Cerradas:\s+1')
        self.assertIn('Bug: 1', out)
        self.assertIn('bug: 1', out)

    def test_capturas_humanas_informan_id_y_rutas(self):
        """Las confirmaciones humanas permiten localizar el documento y la copia creados."""
        for args in (('anotar', self.id, 'nota'), ('adjuntar', self.id, str(self.origen))):
            with self.subTest(args=args):
                rc, out, err = self.ejecutar(*args)
                self.assertEqual(rc, 0, err)
                self.assertIn(self.id, out)
                self.assertIn(str(self.documento), out)
                if args[0] == 'adjuntar':
                    self.assertIn(str(self.carpeta / self.origen.name), out)


if __name__ == '__main__':
    unittest.main()
