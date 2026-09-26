"""La receta conserva capturas y exige las decisiones del autor."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from nucleo.caso import cargar_fuente_caso
from nucleo.medida import cargar
from tools.corpus import verificar

RAIZ = Path(__file__).resolve().parents[1]
CAPTURA = RAIZ / 'observaciones/2026-09-09-aceptacion'
RECETA = RAIZ / 'ejemplo/caso-observado/convertir.py'


class RecetaObservadosTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directorio = Path(self.tmp.name)
        self.meta = cargar_fuente_caso(
            CAPTURA / '494-la-cota-de-la-sombra-observada-por-el-recorrido.caso')
        self.meta.pop('evidencia')
        self.evidencia = json.loads((CAPTURA / 'evidencia.json').read_text())
        self.destino = self.directorio / (self.meta['id'] + '.caso')

    def ejecutar(self):
        captura = self.directorio / 'captura.json'
        metadatos = self.directorio / 'metadatos.json'
        captura.write_text(json.dumps(self.evidencia))
        metadatos.write_text(json.dumps(self.meta))
        return subprocess.run([sys.executable, str(RECETA), str(captura),
                               str(metadatos), str(self.destino)],
                              capture_output=True, text=True, cwd=RAIZ)

    def test_captura_real_verificada_con_herramientas_existentes(self):
        resultado = self.ejecutar()
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        caso = cargar_fuente_caso(self.destino)
        self.assertEqual(caso, dict(self.meta, evidencia=self.evidencia))
        corpus = self.directorio / 'corpus'
        corpus.mkdir()
        self.destino.rename(corpus / self.destino.name)
        self.assertEqual(verificar(corpus)[0], [])
        medida = cargar(RAIZ / 'catalogos/meta/meta.ninguna_sombra_supera_su_cota.oracle')
        veredicto = medida.evaluar(caso['evidencia'])
        self.assertEqual(veredicto.valor, 0)
        self.assertFalse(veredicto.sin_evidencia)
        self.assertTrue(veredicto.ok)
        self.assertEqual(self.meta, json.loads(
            (RAIZ / 'ejemplo/caso-observado/metadatos.json').read_text()))

    def test_preserva_vacias_duplicados_tipos_claves_y_mil_filas(self):
        self.evidencia = {'vacia': [], 'datos': [
            {'id': n, 'texto': 'línea\\n"', 'nulo': None, 'bool': True, 'real': 1.5}
            for n in range(1000)], 'duplicados': [{'x': 1}, {'x': 1}],
            'con_clave': [['clave', ['id']], {'id': 1}]}
        resultado = self.ejecutar()
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        caso = cargar_fuente_caso(self.destino)
        self.assertEqual(caso['evidencia'], self.evidencia)
        self.assertIs(type(caso['evidencia']['datos'][0]['bool']), bool)
        self.assertIs(type(caso['evidencia']['datos'][0]['id']), int)

    def test_no_infiere_decisiones_ni_acepta_evidencia_en_metadatos(self):
        originales = self.meta.copy()
        for campo in ('procedencia', 'origen', 'medida', 'etiqueta', 'fecha'):
            with self.subTest(campo=campo):
                self.meta = {k: v for k, v in originales.items() if k != campo}
                resultado = self.ejecutar()
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(campo, resultado.stderr)
                self.assertFalse(self.destino.exists())
        self.meta = dict(originales, evidencia={})
        resultado = self.ejecutar()
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn('evidencia', resultado.stderr)

    def test_origen_es_dato_y_no_sobrescribe(self):
        testigo = self.directorio / 'no-ejecutar'
        self.meta['origen']['comando'] = f'touch {testigo}'
        resultado = self.ejecutar()
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertFalse(testigo.exists())
        anterior = self.destino.read_bytes()
        self.evidencia['sombra'] = []
        self.assertNotEqual(self.ejecutar().returncode, 0)
        self.assertEqual(self.destino.read_bytes(), anterior)

    def test_rechaza_metadatos_y_evidencia_invalidos(self):
        originales = self.meta.copy()
        for campo, valor in [('procedencia', 'construida'), ('etiqueta', 'verde'),
                             ('origen', {}), ('medida', ''), ('id', '../escape')]:
            with self.subTest(campo=campo):
                self.meta = dict(originales, **{campo: valor})
                resultado = self.ejecutar()
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(campo, resultado.stderr)
                self.assertFalse(self.destino.exists())
        self.meta = originales
        self.evidencia = {'dato': [{'anidado': {'x': 1}}]}
        self.assertNotEqual(self.ejecutar().returncode, 0)
        self.assertFalse(self.destino.exists())
