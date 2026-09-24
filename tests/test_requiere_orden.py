"""El orden de requiere se explica sin ampliar la gramática."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nucleo.medida import Medida
from nucleo.sintaxis import ErrorSintaxis, fragmento_de_error, leer
from nucleo.version import VERSION_ALGEBRA, VERSION_SINTAXIS
from tools import sintaxis


class RequiereOrdenTests(unittest.TestCase):
    def _texto(self, posicion):
        lineas = [
            'medida d.orden:',
            '    de dato d',
            '    donde d.x > 0',
            '    resumen contar(1)',
            '    umbral <= 0 porque "no hay positivos"',
            '    ambito universal',
            '    alcance "NO ve otros datos"',
        ]
        lineas.insert(posicion, '    requiere dato')
        return '\n'.join(lineas) + '\n'

    def test_requiere_antes_de_resumen_o_umbral_explica_donde_moverlo(self):
        for posicion, esperado in ((3, 'resumen'), (4, 'umbral')):
            with self.subTest(esperado=esperado):
                texto = self._texto(posicion)
                with self.assertRaises(ErrorSintaxis) as capturado:
                    leer(texto)
                error = capturado.exception
                self.assertEqual((error.linea, error.columna), (posicion + 1, 5))
                self.assertEqual(error.encontrado, "'requiere dato'")
                self.assertIn(f'se esperaba línea «{esperado}»', str(error))
                self.assertIn('«requiere» va después de «umbral» y antes de «ambito» o «alcance»', str(error))
                fragmento = fragmento_de_error(error, texto)
                self.assertIn('    requiere dato', fragmento)
                self.assertIn('^', fragmento)

    def test_cli_conserva_codigo_de_fallo_y_muestra_la_indicacion(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / 'orden.oracle'
            for posicion in (3, 4):
                with self.subTest(posicion=posicion):
                    ruta.write_text(self._texto(posicion), encoding='utf-8')
                    salida = io.StringIO()
                    with redirect_stdout(salida):
                        codigo = sintaxis.main(['--leer', str(ruta)])
                    self.assertEqual(codigo, 1)
                    self.assertIn(f'línea {posicion + 1}, columna 5', salida.getvalue())
                    self.assertIn('requiere dato', salida.getvalue())
                    self.assertIn('«requiere» va después de «umbral» y antes de «ambito» o «alcance»', salida.getvalue())

    def test_orden_valido_conserva_ast_y_evaluacion(self):
        esperado = [
            'medida', 'd.orden',
            ['desde', ['de', 'dato', 'd'], ['donde', ['>', ['campo', 'd', 'x'], 0]]],
            ['resumen', 'contar', 1],
            ['umbral', '<=', 0, 'no hay positivos'],
            ['requiere', 'dato'], ['ambito', 'universal'],
            ['alcance', 'NO ve otros datos'],
        ]
        datos = leer(self._texto(5))
        self.assertEqual(datos, esperado)
        medida = Medida.de_datos(datos)
        for hechos, valor, ok, sin_evidencia in (
            ({'dato': [{'x': 0}]}, 0, True, ''),
            ({'dato': [{'x': 1}]}, 1, False, ''),
            ({}, 0, False, 'dato'),
        ):
            with self.subTest(hechos=hechos):
                resultado = medida.evaluar(hechos)
                self.assertEqual((resultado.valor, resultado.ok, resultado.sin_evidencia),
                                 (valor, ok, sin_evidencia))
        self.assertEqual((VERSION_ALGEBRA, VERSION_SINTAXIS), ('0.8', '0.7'))

    def test_otro_prefijo_incorrecto_conserva_el_diagnostico(self):
        texto = self._texto(3).replace('requiere dato', 'requierex dato')
        with self.assertRaises(ErrorSintaxis) as capturado:
            leer(texto)
        self.assertEqual(str(capturado.exception),
                         "línea 4, columna 5: se esperaba línea «resumen»; llegó 'requierex dato'")
