"""Pruebas de conservación y cegamiento; no evalúan semántica ni llaman a una API."""
import json
import unittest
from preparar import D, ANTERIOR, construir


class PaqueteCiego(unittest.TestCase):
    def setUp(self):
        self.datos = construir()
        self.lote = self.datos['lote.json']
        self.clave = self.datos['clave-operador.json']
        self.ciego = self.datos['ciego/registros.json']

    def test_conserva_controles_y_muestra(self):
        self.assertEqual(len(self.lote), 72)
        self.assertEqual(sum(r['control'] for r in self.clave), 10)
        muestra = json.loads((ANTERIOR / 'muestra-jev.json').read_text())
        self.assertEqual({r['medida'] for r in self.clave if r['muestra']}, set(muestra))
        viejos = {r['id']: r for r in json.loads((ANTERIOR / 'lote.json').read_text())['records']}
        for r, clave in zip(self.lote, self.clave):
            for campo in ('alcance', 'porque', 'umbral', 'segun'):
                self.assertEqual(r[campo], viejos[clave['anterior']][campo])

    def test_ciego_sin_etiquetas_y_con_tuberia(self):
        self.assertEqual(len(self.ciego), 25)
        self.assertEqual(len({r['id'] for r in self.ciego}), 25)
        permitidos = {'id', 'alcance', 'porque', 'umbral', 'segun', 'tuberia',
                      'resumen', 'limite', 'aplica_vecino'}
        for r in self.ciego:
            self.assertEqual(set(r), permitidos)
            self.assertEqual(r['tuberia'][0], 'desde')
            self.assertEqual(r['resumen'][0], 'resumen')

    def test_no_aplica_no_se_convierte_en_no(self):
        reales = {r['id'] for r in self.clave if r['muestra']}
        self.assertTrue(all(not r['aplica_vecino'] for r in self.ciego if r['id'] in reales))
        self.assertEqual(sum(r['aplica_vecino'] for r in self.lote), 1)
        for r in self.clave:
            if r['control']:
                self.assertIsNone(r['esperado']['porque_vecino'])
        for r in self.datos['ciego/plantilla.json']:
            self.assertIsNone(r['porque_origen'])
            self.assertIsNone(r['porque_vecino'])

    def test_artefactos_coinciden_con_preparacion(self):
        for nombre, contenido in self.datos.items():
            self.assertEqual(json.loads((D / nombre).read_text()), contenido)


if __name__ == '__main__':
    unittest.main()
