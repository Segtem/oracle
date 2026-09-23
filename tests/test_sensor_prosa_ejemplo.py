"""Contrato del sensor opcional: transporte simulado, nunca red ni clave real."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

RUTA = Path(__file__).resolve().parents[1] / 'ejemplo/sensor-prosa'
spec = importlib.util.spec_from_file_location('sensor_prosa_ejemplo', RUTA / 'sensor_prosa.py')
sensor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sensor)


class SensorProsa(unittest.TestCase):
    def respuesta(self, pedido, p=.5):
        return {'model': 'prueba/version-fija', 'answers': {
            q: {'type': 'noul', 'noul': p} for q in pedido['questions']}}

    def test_polaridades_del_corpus_sin_politicas_meta(self):
        from nucleo.medida import cargar_catalogo, evaluar_conjunto
        catalogo = cargar_catalogo(RUTA / 'catalogos')
        for archivo in sorted((RUTA / 'corpus/prosa').glob('*.json')):
            caso = json.loads(archivo.read_text())
            with self.subTest(caso=caso['id']):
                informe = evaluar_conjunto([catalogo[caso['medida']]], caso['evidencia'])
                self.assertEqual(informe.veredictos[0].ok, caso['etiqueta'] == 'verde_correcto')

    def test_catalogo_oracle_incluye_escalares_distribuidas(self):
        raiz = RUTA.parents[1]
        registros = sensor.construir([raiz / 'catalogos', raiz / 'perfiles/python/catalogos'])
        self.assertTrue(any(r['medida'] == 'meta.unir_materializa_el_producto' for r in registros))
        self.assertEqual(len({r['id'] for r in registros}), len(registros))

    def test_preparar_no_lee_clave_ni_llama_y_conserva_contexto(self):
        with tempfile.TemporaryDirectory() as d, patch.object(sensor, 'enviar') as enviar:
            salida = Path(d) / 'preparado'
            with patch.dict(sensor.os.environ, {}, clear=True):
                self.assertEqual(sensor.main(['preparar', '--catalogo', str(RUTA / 'catalogos'),
                                             '--salida', str(salida)]), 0)
            pedido = json.loads((salida / 'solicitud-001.json').read_text())
            self.assertIn('tuberia', pedido['state']['records'][0])
            self.assertIn('porque', pedido['state']['records'][0])
            self.assertEqual(len(pedido['questions']), 2)
            enviar.assert_not_called()
            self.assertFalse((salida / 'hechos.json').exists())

    def test_correr_publica_y_exige_revision_incluso_en_bordes(self):
        for p in (.4, .5, .6):
            with self.subTest(p=p), tempfile.TemporaryDirectory() as d:
                salida = Path(d) / 'corrida'
                with patch.dict(sensor.os.environ, {'CLAVE_PRUEBA': 'secreto-local'}), \
                     patch.object(sensor, 'enviar', side_effect=lambda url, key, req: self.respuesta(req, p)) as enviar:
                    rc = sensor.main(['correr', '--catalogo', str(RUTA / 'catalogos'),
                                      '--salida', str(salida), '--clave-entorno', 'CLAVE_PRUEBA',
                                      '--proveedor', 'https://proveedor.invalid/decisions'])
                self.assertEqual(rc, 2)
                self.assertEqual(enviar.call_args.args[0], 'https://proveedor.invalid/decisions')
                filas = json.loads((salida / 'hechos.json').read_text())['afirmacion_prosa']
                self.assertEqual(len(json.loads((salida / 'revision-humana.json').read_text())), 2)
                self.assertEqual(filas[0]['respuesta'], p >= .5)
                self.assertEqual(filas[0]['modelo'], 'prueba/version-fija')
                self.assertNotIn('secreto-local', ''.join(f.read_text() for f in salida.iterdir()))

    def test_respuesta_invalida_no_se_convierte_en_hechos(self):
        pedido = sensor.solicitud([{'id': 'r1', 'medida': 'una.medida'}], 'prueba')
        for p in (True, float('nan'), float('inf'), -.1, 1.1, '0.5', None):
            with self.subTest(p=p), self.assertRaises(ValueError):
                sensor.convertir(self.respuesta(pedido, p), pedido, 'fecha', .5, (.4, .6))
        with self.assertRaises(ValueError):
            sensor.convertir([], pedido, 'fecha', .5, (.4, .6))
        data = self.respuesta(pedido)
        data['answers'].pop(next(iter(data['answers'])))
        with self.assertRaises(ValueError):
            sensor.convertir(data, pedido, 'fecha', .5, (.4, .6))

    def test_lote_parcial_no_publica_evidencia_ni_reintenta(self):
        registros = [{'id': f'r{i}', 'medida': f'una.medida{i}'} for i in range(13)]
        with tempfile.TemporaryDirectory() as d, \
             patch.object(sensor, 'construir', return_value=registros), \
             patch.dict(sensor.os.environ, {'OPENROUTER_API_KEY': 'prueba'}):
            salida = Path(d) / 'parcial'
            def contestar(url, key, req):
                if req['state']['records'][0]['id'] == 'r12':
                    raise ValueError('Falla simulada')
                return self.respuesta(req, .9)
            with patch.object(sensor, 'enviar', side_effect=contestar) as enviar:
                self.assertEqual(sensor.main(['correr', '--catalogo', 'ignorado', '--salida', str(salida)]), 1)
                self.assertEqual(enviar.call_count, 2)
            self.assertTrue((salida / 'respuesta-001.json').exists())
            self.assertFalse((salida / 'hechos.json').exists())

    def test_transporte_conserva_contrato_del_experimento(self):
        from unittest.mock import MagicMock
        pedido = sensor.solicitud([{'id': 'r1', 'medida': 'una.medida'}], 'typesafe/jev-1.13')
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value.read.return_value = json.dumps(self.respuesta(pedido)).encode()
        with patch.object(sensor.urllib.request, 'build_opener', return_value=opener):
            sensor.enviar('https://proveedor.invalid/decisions', 'clave-prueba', pedido)
        req = opener.open.call_args.args[0]
        self.assertEqual(req.get_header('Authorization'), 'Bearer clave-prueba')
        self.assertEqual(json.loads(req.data), pedido)
        self.assertEqual(opener.open.call_args.kwargs['timeout'], 60)


if __name__ == '__main__':
    unittest.main()
