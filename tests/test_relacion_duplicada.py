"""Regresiones de las fronteras públicas ante relaciones duplicadas."""
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import mcp
from tests.test_mcp import _conversacion, _desenmarcar, _medida, _pedido_evaluar, _proyecto

RAIZ = Path(__file__).resolve().parents[1]


class RelacionDuplicadaTests(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = _proyecto(Path(self.temporal.name), _medida('demo.uno'))
        (self.raiz / 'oracle.json').write_text('{"esquema": "oracle.proyecto/v1", "catalogo_base": true}', encoding='utf-8')
        for nombre in ('corpus', 'diferencial', 'relaciones'):
            (self.raiz / nombre).mkdir()
        shutil.copy(RAIZ / 'relaciones/pieza.json', self.raiz / 'relaciones/pieza.json')
        (self.raiz / 'hechos.json').write_text('{"item": []}', encoding='utf-8')

    def comprobar_diagnostico(self, texto):
        self.assertIn('pieza', texto)
        self.assertIn(str(RAIZ / 'relaciones/pieza.json'), texto)
        self.assertIn(str(self.raiz / 'relaciones/pieza.json'), texto)
        self.assertIn('ya existe en Oracle', texto)
        self.assertIn('renombr', texto)
        self.assertNotIn('Traceback', texto)

    def correr(self, *args):
        resultado = subprocess.run(
            [sys.executable, str(RAIZ / 'tools/cli.py'), *args,
             '--proyecto', str(self.raiz)], capture_output=True, text=True, timeout=60)
        self.assertEqual(resultado.returncode, 2, resultado.stdout + resultado.stderr)
        self.assertIn('PROYECTO INVÁLIDO —', resultado.stderr)
        self.comprobar_diagnostico(resultado.stderr)

    def test_test(self):
        self.correr('test', '--rapido')

    def test_juzgar(self):
        self.correr('juzgar', '--con', str(self.raiz / 'hechos.json'))

    def test_revisar(self):
        self.correr('medida', 'revisar', 'catalogos/demo/demo.uno.json')

    def test_mcp(self):
        entrada = _conversacion(_pedido_evaluar(2, {
            'medida': {'id': 'demo.uno'}, 'evidencia': {'item': []}}))
        salida = io.BytesIO()
        codigo = mcp.servir(mcp.Proyecto(self.raiz), io.BytesIO(entrada), salida)
        self.assertEqual(codigo, 0)  # El error pertenece a la llamada, no al transporte.
        resultado = _desenmarcar(salida.getvalue())[1]['result']
        self.assertTrue(resultado['isError'])
        texto = resultado['content'][0]['text']
        self.assertIn('PROYECTO_INVALIDO —', texto)
        self.comprobar_diagnostico(texto)

    def test_duplicado_local_no_se_atribuye_a_oracle(self):
        (self.raiz / 'oracle.json').unlink()
        shutil.copy(self.raiz / 'relaciones/pieza.json', self.raiz / 'relaciones/otra.json')
        with self.assertRaisesRegex(mcp.ProyectoInvalido, 'está dos veces') as error:
            mcp.relaciones_del_proyecto(mcp.Proyecto(self.raiz))
        self.assertNotIn('ya existe en Oracle', str(error.exception))

    def test_base_no_seleccionada_permite_relacion_propia(self):
        (self.raiz / 'oracle.json').unlink()
        declaradas = mcp.relaciones_del_proyecto(mcp.Proyecto(self.raiz))
        self.assertEqual(set(declaradas), {'pieza'})

    def test_declaracion_malformada_se_informa_como_proyecto_invalido(self):
        (self.raiz / 'relaciones/pieza.json').write_text('{', encoding='utf-8')
        with self.assertRaisesRegex(mcp.ProyectoInvalido, 'JSON inválido'):
            mcp.relaciones_del_proyecto(mcp.Proyecto(self.raiz))
