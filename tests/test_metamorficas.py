"""Custodia de las sondas: perder una comparación no puede parecer una equivalencia."""

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from nucleo.medida import Medida
from nucleo.proyecto import Proyecto
from tools import metamorficas as sonda


class Comparaciones(unittest.TestCase):
    def test_compara_color_valor_y_bolsa_por_separado(self):
        """Coincidir en color no permite perder valor, identidad ni multiplicidad de testigos."""
        base = SimpleNamespace(ok=False, valor=2, testigos=[{'c': {'x': 1}}, {'c': {'x': 2}}])
        variantes = (
            (base, (True, True, True)),
            (SimpleNamespace(ok=True, valor=2, testigos=base.testigos), (False, True, True)),
            (SimpleNamespace(ok=False, valor=3, testigos=base.testigos), (True, False, True)),
            (SimpleNamespace(ok=False, valor=2, testigos=[{'c': {'x': 2}}, {'c': {'x': 1}}]), (True, True, True)),
            (SimpleNamespace(ok=False, valor=2, testigos=[{'c': {'x': 1}}, {'c': {'x': 1}}]), (True, True, False)),
        )
        for otro, esperado in variantes:
            with self.subTest(esperado=esperado, otro=otro):
                a, b = mock.Mock(), mock.Mock()
                a.evaluar.return_value, b.evaluar.return_value = base, otro
                resultado = sonda._comparar(a, b, {'entrada': []})
                self.assertEqual(resultado, dict(evaluo=True, error='',
                    mismo_veredicto=esperado[0], mismo_valor=esperado[1], mismos_testigos=esperado[2]))
                a.evaluar.assert_called_once_with({'entrada': []})
                b.evaluar.assert_called_once_with({'entrada': []})
                a.evaluar.side_effect = [base, otro]
                with mock.patch.object(sonda, 'forzar_plan_unir') as plan:
                    self.assertEqual(sonda._comparar_planes(a, {'entrada': []}), resultado)
                self.assertEqual(plan.call_args_list, [mock.call(False), mock.call(True)])

    def test_un_error_en_cualquiera_de_los_caminos_no_es_coincidencia(self):
        """Un evaluador que no llegó a concluir debe dejar los tres acuerdos en falso."""
        for posicion in (0, 1):
            a, b = mock.Mock(), mock.Mock()
            base = SimpleNamespace(ok=True, valor=0, testigos=[])
            a.evaluar.return_value = b.evaluar.return_value = base
            (a, b)[posicion].evaluar.side_effect = ValueError('falló la lectura')
            esperado = dict(evaluo=False, error='ValueError', mismo_veredicto=False,
                            mismo_valor=False, mismos_testigos=False)
            self.assertEqual(sonda._comparar(a, b, {}), esperado)
            a.evaluar.side_effect = [ValueError('falló')] if posicion == 0 else [base, ValueError('falló')]
            self.assertEqual(sonda._comparar_planes(a, {}), esperado)


class Transformaciones(unittest.TestCase):
    @staticmethod
    def _medida(pasos=(), fuente=None):
        return Medida.de_datos(['medida', 'prueba.sonda',
            ['desde', fuente or ['de', 'cosa', 'c'], *pasos],
            ['resumen', 'contar', 1], ['umbral', '<=', 0, '', 'contrato'],
            ['ambito', 'universal'], ['alcance', 'Sólo la evidencia de esta prueba']])

    def test_los_filtros_conservan_los_pasos_vecinos_y_la_seleccion(self):
        """Partir una conjunción o juntar dos filtros no debe borrar el filtro vecino."""
        p = ['>', ['campo', 'c', 'n'], 1]
        q = ['<', ['campo', 'c', 'm'], 30]
        r = ['!=', ['campo', 'c', 'n'], 3]
        for pasos in (
            [['donde', ['y', p, q]], ['donde', r]],
            [['donde', r], ['donde', p], ['donde', q]],
            [['donde', ['o', p, q]]],
            [['donde', True]],
        ):
            medida = self._medida(pasos)
            casos = [dict(id='caso-real', medida=medida.id, evidencia=sonda.EV_SONDA)]
            with mock.patch.object(sonda, '_comparar', wraps=sonda._comparar) as comparar:
                filas = sonda._donde_compone({medida.id: medida}, casos)
            esperadas = 3 if len(pasos) > 1 else 1
            self.assertEqual(len(filas), esperadas)
            for fila in filas:
                self.assertTrue(fila['evaluo'])
                self.assertTrue(fila['mismo_valor'])
                self.assertTrue(fila['mismos_testigos'])
            for llamada in comparar.call_args_list[1:]:
                original, transformada, evidencia = llamada.args
                self.assertIs(original, medida)
                self.assertEqual(original.evaluar(evidencia).valor, transformada.evaluar(evidencia).valor)
                self.assertNotEqual(original.tuberia, transformada.tuberia)
                self.assertEqual(transformada.tuberia[0], 'desde')

    def test_el_catalogo_sin_caso_aplicable_no_inventa_observaciones(self):
        """Un caso sin medida conocida o sin evidencia no sostiene una equivalencia del catálogo."""
        medida = self._medida()
        casos = [dict(id='sin-medida'), dict(id='nula', medida=None),
                 dict(id='desconocida', medida='otra.medida', evidencia={}),
                 dict(id='sin-evidencia', medida=medida.id)]
        for funcion, construidas in ((sonda._donde_compone, 1), (sonda._unir_conmuta, 1),
            (sonda._agrupar_sin_claves, 5), (sonda._el_plan_indexado_da_lo_mismo_que_el_producto, 0)):
            self.assertEqual(len(funcion({medida.id: medida}, casos)), construidas)
        self.assertEqual(sonda._macro_equivale_a_su_expansion({medida.id: medida}, casos, {}), [])

    def test_el_producto_y_el_plan_indexado_comparan_solo_medidas_con_union(self):
        """Una unión real debe emitirse una vez; una fuente simple no prueba el índice."""
        for fuente, cantidad in ((['de', 'cosa', 'c'], 0),
            (['unir', ['de', 'cosa', 'c'], ['de', 'otra', 'o']], 1)):
            medida = self._medida(fuente=fuente)
            casos = [dict(id='caso-real', medida=medida.id, evidencia=sonda.EV_SONDA)]
            for funcion, adicionales in ((sonda._unir_conmuta, 1),
                (sonda._el_plan_indexado_da_lo_mismo_que_el_producto, 0)):
                filas = funcion({medida.id: medida}, casos)
                self.assertEqual(len(filas), cantidad + adicionales)
                for fila in filas:
                    self.assertTrue(fila['evaluo'])
                    self.assertTrue(fila['mismo_valor'])
                    self.assertTrue(fila['mismos_testigos'])
                if cantidad:
                    self.assertEqual(filas[-1]['origen'], 'catalogo')
                    self.assertEqual(filas[-1]['caso'], 'caso-real')

    def test_agrupar_no_se_aplica_dos_veces_y_ejerce_los_cinco_agregados(self):
        """Reagrupar una medida ya agrupada da una columna ajena y falsea el contraste."""
        for pasos, esperadas in (([], 6),
            ([['agrupar', [], [['n', 'contar', 1]]]], 5)):
            medida = self._medida(pasos)
            filas = sonda._agrupar_sin_claves({medida.id: medida},
                [dict(id='caso-real', medida=medida.id, evidencia=sonda.EV_SONDA)])
            self.assertEqual(len(filas), esperadas)
            self.assertEqual({f['caso'] for f in filas[:5]}, {'contar', 'suma', 'max', 'min', 'promedio'})
            for fila in filas:
                self.assertTrue(fila['evaluo'])
                self.assertTrue(fila['mismo_valor'])


class Superficie(unittest.TestCase):
    def test_un_error_de_impresion_o_lectura_deja_una_fila_roja(self):
        """Un archivo o una candidata que no vuelve debe contarse: omitirlo fabrica verde."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            ruta = raiz / 'ejemplo.json'
            ruta.write_text('{}', encoding='utf-8')
            for funcion, modulo, generador in (
                (sonda._sintaxis_ida_y_vuelta, sonda.sintaxis, None),
                (sonda._sintaxis_casos_ida_y_vuelta, sonda.sintaxis_caso, None),
                (sonda._sintaxis_cubre_algebra, sonda.sintaxis, '_generar_candidatas'),
                (sonda._sintaxis_casos_cubre_casos, sonda.sintaxis_caso, '_generar_casos_candidatos')):
                for operacion in ('imprimir', 'leer'):
                    with self.subTest(funcion=funcion.__name__, operacion=operacion), ExitStack() as pila:
                        pila.enter_context(mock.patch.object(sonda.sintaxis, '_rutas_catalogo', return_value=[ruta]))
                        pila.enter_context(mock.patch.object(sonda.sintaxis, '_rutas_corpus', return_value=[ruta]))
                        pila.enter_context(mock.patch.object(sonda, 'cargar_fuente_medida', return_value=Transformaciones._medida().a_datos()))
                        pila.enter_context(mock.patch.object(sonda, 'cargar_fuente_caso', return_value=sonda._caso_generado('001-ejemplo', {'cosa': []})))
                        if generador:
                            candidato = Transformaciones._medida().a_datos() if generador == '_generar_candidatas' else sonda._caso_generado('001-ejemplo', {'cosa': []})
                            pila.enter_context(mock.patch.object(sonda, generador, return_value=[candidato]))
                        pila.enter_context(mock.patch.object(modulo, operacion, side_effect=ValueError('esquina perdida')))
                        filas = funcion() if generador else funcion(Proyecto(raiz))
                        self.assertEqual(len(filas), 1)
                        self.assertEqual({k: filas[0][k] for k in ('evaluo', 'error', 'mismo_veredicto', 'mismo_valor', 'mismos_testigos')},
                            dict(evaluo=False, error='ValueError: esquina perdida', mismo_veredicto=False, mismo_valor=False, mismos_testigos=False))

    def test_las_esquinas_que_cerraron_la_decision_se_siguen_generando(self):
        """La igualdad de ida y vuelta es vacua si se borran los grupos vacíos o los campos con espacios."""
        medidas = sonda._generar_candidatas()
        grupos = [m[2][2] for m in medidas if m[1].startswith('meta_gen.grp_')]
        self.assertEqual({(len(g[1]), len(g[2])) for g in grupos},
                         {(c, a) for c in (0, 1, 2) for a in (0, 1, 2)})
        self.assertEqual(len(grupos), 24)
        self.assertEqual(len({m[1] for m in medidas}), len(medidas))
        for datos in medidas:
            Medida.de_datos(datos)
        casos = sonda._generar_casos_candidatos()
        self.assertEqual(len({c['id'] for c in casos}), len(casos))
        campos = {campo for c in casos for filas in c['evidencia'].values()
                  for fila in filas if isinstance(fila, dict) for campo in fila}
        self.assertTrue({'campo con espacio', 'campo,con,coma', 'campo\tcon\ttab'} <= campos)
        self.assertEqual({len(c['evidencia']) for c in casos}, {1, 2, 3})
        for fila in sonda._sintaxis_cubre_algebra() + sonda._sintaxis_casos_cubre_casos():
            self.assertEqual((fila['evaluo'], fila['error'], fila['mismo_veredicto'],
                              fila['mismo_valor'], fila['mismos_testigos']), (True, '', True, True, True))


class ContratoDeSondasPublicadas(unittest.TestCase):
    def test_las_sondas_publicadas_conservan_identidad_tipos_y_contenido(self):
        """Cambiar una sonda bajo el mismo id rompe la reproducción de una observación anterior.

        La referencia se capturó del árbol publicado 0.14.0, antes del arreglo, y es legible como
        datos. No se regenera al correr: además de cubrir la gramática, fijamos qué se compara.
        La comparación JSON distingue `true` de `1`, que la igualdad de Python confunde.
        """
        ruta = Path(__file__).parent / 'datos/sondas_sintaxis_0_14_0.json'
        esperado = json.loads(ruta.read_text(encoding='utf-8'))
        actuales = dict(medidas=sonda._generar_candidatas(), casos=sonda._generar_casos_candidatos())
        self.assertEqual(json.dumps(actuales, sort_keys=True, ensure_ascii=False),
                         json.dumps(esperado, sort_keys=True, ensure_ascii=False))

    def test_las_sondas_de_filtros_tienen_filas_en_cada_frontera(self):
        """Mover los valores de la evidencia o los límites puede dejar sin probar un filtro estricto."""
        with mock.patch.object(sonda, '_comparar', wraps=sonda._comparar) as comparar:
            sonda._donde_compone({}, [])
        dos, una, evidencia = comparar.call_args.args
        self.assertEqual(dos.evaluar(evidencia).valor, 2)
        self.assertEqual(dos.a_datos()[3], ['resumen', 'contar', 1])
        self.assertEqual(dos.a_datos()[4][1:3], ['<=', 0])
        self.assertEqual(dos.tuberia[2:], [['donde', ['>', ['campo', 'c', 'n'], 1]],
                                        ['donde', ['<', ['campo', 'c', 'm'], 30]]])
        self.assertEqual(evidencia['cosa'],
                         [{'n': 1, 'm': 10}, {'n': 2, 'm': 20}, {'n': 3, 'm': 10}, {'n': 4, 'm': 30}])
        with mock.patch.object(sonda, '_comparar', wraps=sonda._comparar) as comparar:
            sonda._unir_conmuta({}, [])
        a, b, evidencia = comparar.call_args.args
        self.assertEqual(a.a_datos()[3], ['resumen', 'contar', 1])
        self.assertEqual(a.evaluar(evidencia).valor, 4)

    def test_una_macro_real_se_compara_y_una_canonica_no_se_inventa_como_macro(self):
        """Sin una invocación real, el camino que expande macros podría desaparecer sin alarma."""
        macros = sonda.macros_del_proyecto(Proyecto(sonda.RAIZ))
        medida = Medida.de_datos(['ninguno', 'prueba.macro', 'cosa', 'c',
            ['>', ['campo', 'c', 'n'], 1], '', 'contrato', 'universal', 'Sólo esta prueba'], macros=macros)
        canonica = Medida.de_datos(medida.a_datos())
        for m, cantidad in ((medida, 1), (canonica, 0)):
            filas = sonda._macro_equivale_a_su_expansion({m.id: m},
                [dict(id='001-real', medida=m.id, evidencia=sonda.EV_SONDA)], macros)
            self.assertEqual(len(filas), cantidad)
            if filas:
                self.assertEqual(filas[0], dict(propiedad='una_macro_equivale_a_su_expansion',
                    caso='001-real', origen='catalogo', evaluo=True, error='',
                    mismo_veredicto=True, mismo_valor=True, mismos_testigos=True))


class RecorridoYSalida(unittest.TestCase):
    def test_la_ayuda_devuelve_cero_tambien_al_llamarla_como_funcion(self):
        """SystemExit(None) sale cero: probar sólo el proceso no fija el contrato de main."""
        for argumentos in (["--help"], ["-h"]):
            with redirect_stdout(io.StringIO()) as salida:
                self.assertEqual(sonda.main(argumentos), 0)
            self.assertIn("--hechos", salida.getvalue())

    def test_el_recorrido_incluye_las_nueve_propiedades_y_el_proyecto_elegido(self):
        """Omitir un sensor del recorrido dejaría su jueza sin ninguna fila que rechazar."""
        nombres = ('_donde_compone', '_unir_conmuta',
            '_el_plan_indexado_da_lo_mismo_que_el_producto', '_agrupar_sin_claves',
            '_macro_equivale_a_su_expansion', '_sintaxis_ida_y_vuelta', '_sintaxis_cubre_algebra',
            '_sintaxis_casos_ida_y_vuelta', '_sintaxis_casos_cubre_casos')
        for proy in (None, Proyecto(Path('/tmp/proyecto-elegido'))):
            with ExitStack() as pila:
                sensores = {n: pila.enter_context(mock.patch.object(sonda, n, return_value=[{'sensor': n}])) for n in nombres}
                resultado = sonda.hechos({}, [], {}, proy)
                self.assertEqual(resultado, {'equivalencia': [{'sensor': n} for n in nombres]})
                raiz = proy.raiz if proy is not None else Path(__file__).resolve().parents[1]
                for n in ('_sintaxis_ida_y_vuelta', '_sintaxis_casos_ida_y_vuelta'):
                    self.assertEqual(sensores[n].call_args.args[0].raiz, raiz)

    def test_el_recorrido_real_no_confunde_exito_con_comparacion_omitida(self):
        """La integración fija los campos de éxito de las dos superficies sobre archivos reales."""
        proy = Proyecto(Path(__file__).resolve().parents[1])
        for funcion in (sonda._sintaxis_ida_y_vuelta, sonda._sintaxis_casos_ida_y_vuelta):
            filas = funcion(proy)
            self.assertGreater(len(filas), 0)
            for fila in filas:
                self.assertEqual((fila['evaluo'], fila['error'], fila['mismo_veredicto'],
                    fila['mismo_valor'], fila['mismos_testigos']), (True, '', True, True, True))

    def test_la_salida_conserva_conteos_y_codigos_de_exito_rojo_y_ausencia(self):
        """Una corrida sin pares, sin juezas o con rojo no puede devolver éxito por el reporte."""
        filas = [dict(propiedad='ejemplo con eñe', origen=o) for o in ('construido', 'catalogo', 'catalogo')]
        for vacia, juezas, ok, codigo in ((False, [object()], True, 0),
            (False, [object()], False, 1), (True, [object()], True, 1), (False, [], True, 1)):
            with ExitStack() as pila:
                pila.enter_context(mock.patch.object(sonda, 'macros_del_proyecto', return_value={}))
                pila.enter_context(mock.patch.object(sonda, 'cargar_catalogo', return_value={}))
                pila.enter_context(mock.patch.object(sonda, 'cargar_casos', return_value=[]))
                pila.enter_context(mock.patch.object(sonda, 'hechos', return_value={'equivalencia': [] if vacia else filas}))
                pila.enter_context(mock.patch.object(sonda, 'medidas_aplicables', return_value=juezas))
                veredicto = SimpleNamespace(linea=lambda: 'veredicto de ejemplo')
                evaluar = pila.enter_context(mock.patch.object(sonda, 'evaluar', return_value=SimpleNamespace(ok=ok, veredictos=[veredicto])))
                salida = pila.enter_context(redirect_stdout(io.StringIO()))
                self.assertEqual(sonda.main([]), codigo)
                texto = salida.getvalue()
                if vacia:
                    self.assertIn('SIN EQUIVALENCIAS', texto)
                    evaluar.assert_not_called()
                else:
                    self.assertIn('equivalencias comprobadas: 3', texto)
                    self.assertIn('(1 construidas, 2 del catálogo)', texto)
                    if juezas:
                        self.assertIn('veredicto de ejemplo', texto)
                    else:
                        self.assertIn('sin medidas aplicables', texto)
                        evaluar.assert_not_called()
                if not vacia:
                    salida.seek(0); salida.truncate()
                    with mock.patch.object(sys, 'argv', ['metamorficas.py', '--hechos']):
                        self.assertEqual(sonda.main(), 0)
                    self.assertEqual(salida.getvalue(), json.dumps({'equivalencia': filas}, ensure_ascii=False, indent=2) + '\n')

    def test_la_entrada_directa_y_la_importacion_no_dependen_del_anfitrion(self):
        """Importar con argumentos ajenos no ejecuta main; el script sí interpreta sus opciones."""
        raiz = Path(__file__).resolve().parents[1]
        for argumentos, codigo, esperado in ((['--help'], 0, '--hechos'),
            (['--hehcos'], 2, 'argumentos no reconocidos'),
            (['--hechos', 'sobrante'], 2, 'argumentos no reconocidos')):
            r = subprocess.run([sys.executable, '-B', str(raiz / 'tools/metamorficas.py'), *argumentos],
                               cwd=raiz, capture_output=True, text=True)
            self.assertEqual(r.returncode, codigo, r.stdout+r.stderr)
            self.assertIn(esperado, r.stdout+r.stderr)
        r = subprocess.run([sys.executable, '-B', '-c',
            "import sys; sys.argv = ['anfitrion', '--desconocido']; from tools import metamorficas; print('IMPORTACION OK')"],
            cwd=raiz, capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, 'IMPORTACION OK\n', ''))


if __name__ == '__main__':
    unittest.main()
