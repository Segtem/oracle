"""Resolución por sufijo y sugerencias compartidas por CLI y MCP."""
import io
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

from tools import cli, mcp, tareas


class TestSufijos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        self.tracker = self.raiz / 'tareas'
        self.tracker.mkdir()
        self.id = '20260919-140308-multimalla'
        self.crear(self.id)

    def crear(self, identificador):
        carpeta = self.tracker / identificador
        carpeta.mkdir()
        (carpeta / 'TAREA.md').write_text(
            '# Prueba\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n- ETIQUETAS: \n\n',
            encoding='utf-8')
        return carpeta

    def resolver(self, valor):
        return tareas.resolver_id_o_prefijo(self.tracker, valor)

    def ejecutar(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = cli.main(['--proyecto', str(self.raiz), 'tarea', *args])
        return rc, out.getvalue(), err.getvalue()

    def test_sufijo_unico_id_y_prefijo(self):
        for valor in ('multimalla', self.id, '20260919-140308'):
            with self.subTest(valor=valor):
                self.assertEqual(self.resolver(valor).name, self.id)

    def test_una_similitud_justo_en_el_umbral_se_sugiere(self):
        # «abcxy» contra el sufijo «abcde»: 3 de 5 letras en común, similitud exactamente 0,6.
        self.crear('20260101-000000-abcde')
        with self.assertRaises(tareas.TareaNoEncontrada) as ctx:
            self.resolver('abcxy')
        self.assertIn('20260101-000000-abcde', str(ctx.exception))

    def test_sufijo_completo_con_guiones_y_colision_numerica(self):
        otro = '20260919-140309-multi-malla-1'
        self.crear(otro)
        self.assertEqual(self.resolver('multi-malla-1').name, otro)
        for parcial in ('malla-1', 'multi-malla'):
            with self.assertRaises(tareas.TareaNoEncontrada):
                self.resolver(parcial)

    def test_ambiguo_enumera_ids_ordenados(self):
        otro = '20260920-140308-multimalla'
        self.crear(otro)
        with self.assertRaises(tareas.IdAmbiguo) as ctx:
            self.resolver('multimalla')
        self.assertIn(f'{self.id}, {otro}', str(ctx.exception))

    def test_id_completo_tiene_precedencia(self):
        self.crear('20260920-140308-' + self.id)
        self.assertEqual(self.resolver(self.id).name, self.id)

    def test_sugiere_typo_y_timestamp_erroneo(self):
        for valor in ('multimala', '20260919-140309-multimalla'):
            with self.subTest(valor=valor), self.assertRaises(tareas.TareaNoEncontrada) as ctx:
                self.resolver(valor)
            self.assertIn(f'¿quisiste decir {self.id}?', str(ctx.exception))

    def test_sugerencias_limitadas_y_deterministas(self):
        ids = [self.id] + [f'2026092{i}-140308-multimalla' for i in range(4)]
        for identificador in ids[1:]:
            self.crear(identificador)
        with self.assertRaises(tareas.TareaNoEncontrada) as ctx:
            self.resolver('multimala')
        self.assertIn('¿quisiste decir ' + ', '.join(sorted(ids)[:3]) + '?', str(ctx.exception))

    def test_sin_similitud_o_tracker_vacio(self):
        for valor in ('zzzzzz',):
            with self.assertRaises(tareas.TareaNoEncontrada) as ctx:
                self.resolver(valor)
            self.assertNotIn('quisiste', str(ctx.exception))
        vacio = self.raiz / 'vacio'
        vacio.mkdir()
        with self.assertRaises(tareas.TareaNoEncontrada):
            tareas.resolver_id_o_prefijo(vacio, 'multimalla')

    def test_confinamiento_y_validacion(self):
        for valor in ('../multimalla', '', '/multimalla'):
            with self.assertRaises(tareas.RutaInsegura):
                self.resolver(valor)
        enlace = self.tracker / '20260920-140308-externa'
        enlace.symlink_to(self.raiz, target_is_directory=True)
        with self.assertRaises(tareas.RutaInsegura):
            self.resolver('externa')
        with self.assertRaises(tareas.TareaNoEncontrada) as ctx:
            self.resolver('extern')
        self.assertNotIn(enlace.name, str(ctx.exception))

    def test_cli_ver_anotar_cerrar_reabrir(self):
        for args, estado in [(('ver', 'multimalla'), 'ABIERTA'),
                             (('anotar', 'multimalla', 'Avance comprobado'), 'ABIERTA'),
                             (('cerrar', 'multimalla'), 'CERRADA'),
                             (('reabrir', 'multimalla'), 'ABIERTA')]:
            with self.subTest(args=args):
                rc, _, err = self.ejecutar(*args)
                self.assertEqual(rc, 0, err)
                self.assertEqual(tareas.leer_tarea(self.tracker, self.id).estado, estado)
        self.assertIn('Avance comprobado', tareas.leer_tarea(self.tracker, self.id).cuerpo)

    def test_cli_error_no_muta(self):
        archivo = self.tracker / self.id / 'TAREA.md'
        antes = archivo.read_bytes()
        for accion in ('ver', 'anotar', 'cerrar', 'reabrir'):
            for valor in ('multimala', 'multimalla'):
                if valor == 'multimalla' and not (self.tracker / '20260920-140308-multimalla').exists():
                    self.crear('20260920-140308-multimalla')
                args = [accion, valor] + (['No escribir'] if accion == 'anotar' else [])
                rc, _, err = self.ejecutar(*args)
                self.assertEqual(rc, 1, err)
                self.assertIn('quisiste decir' if valor == 'multimala' else 'ambiguo', err)
                self.assertEqual(archivo.read_bytes(), antes)

    def test_mcp_hereda_resolucion_y_errores(self):
        proyecto = mcp.Proyecto(self.raiz)
        def ver(valor):
            return mcp.tareas_para_mcp(proyecto, {'accion': 'ver', 'id': valor})
        self.assertEqual(ver('multimalla')['resultado']['id'], self.id)
        with self.assertRaises(mcp.ErrorHerramienta) as ctx:
            ver('multimala')
        self.assertEqual(ctx.exception.codigo, 'TAREA_NO_ENCONTRADA')
        self.assertIn(f'¿quisiste decir {self.id}?', str(ctx.exception))
        otro = '20260920-140308-multimalla'
        self.crear(otro)
        with self.assertRaises(mcp.ErrorHerramienta) as ctx:
            ver('multimalla')
        self.assertEqual(ctx.exception.codigo, 'ID_AMBIGUO')
        self.assertIn(f'{self.id}, {otro}', str(ctx.exception))
