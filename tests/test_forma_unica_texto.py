"""La forma del impresor es la única superficie guardable."""

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nucleo import caso, relacion, sintaxis as lector_medida
from nucleo.proyecto import Proyecto
from tools import cli, formato, sintaxis


MEDIDA = ('medida demo.prueba:\n'
          '    de pieza p\n'
          '    resumen contar(1)\n'
          '    umbral <= 0 segun contrato porque "r"\n'
          '    alcance "a"\n')
AGRUPADA = MEDIDA.replace('    resumen contar(1)\n',
                          '    agrupar:\n        clave c = p.id\n'
                          '        agregado a = contar(1)\n    resumen contar(1)\n')
CASO = ('caso 001-demo:\n    fecha: "2026-08-24"\n    origen:\n'
        '        repo: "Segtem/oracle"\n        commit: "c81a87c"\n'
        '    titulo: "demo"\n    etiqueta: falso_verde\n'
        '    sintoma:\n        sintoma\n    como_se_detecto: mutacion\n'
        '    medida: demo.prueba\n    evidencia:\n'
        '        paso: clave(t);\n            fila {"t": 0}\n'
        '    leccion:\n        leccion\n')
RELACION = ('relacion evento:\n    tipo: texto\n    variantes por tipo:\n'
            '        inicio:\n            hora: texto\n    alcance "ve eventos"\n')


class FormaUnicaTests(unittest.TestCase):
    def test_cada_variante_legible_falla_el_invariante_del_proyecto(self):
        variantes = [
            ('.oracle', MEDIDA, 'sintaxis 0.8\n' + MEDIDA),
            ('.oracle', MEDIDA, MEDIDA.replace('medida demo', 'medida   demo')),
            ('.oracle', MEDIDA.replace('contar(1)', 'contar(0.001)'),
             MEDIDA.replace('contar(1)', 'contar(1e-3)')),
            ('.oracle', AGRUPADA, AGRUPADA.replace(
                '        clave c = p.id\n        agregado a = contar(1)\n',
                '        agregado a = contar(1)\n        clave c = p.id\n')),
            ('.caso', CASO, CASO.replace(
                '        repo: "Segtem/oracle"\n        commit: "c81a87c"\n',
                '        commit: "c81a87c"\n        repo: "Segtem/oracle"\n')),
            ('.caso', CASO, CASO.replace('paso: clave(t);', 'paso: clave(t)')),
            ('.relacion', RELACION, RELACION.replace('        inicio:', '        "inicio":')),
        ]
        lectores = {'.oracle': lector_medida.leer, '.caso': caso.leer,
                    '.relacion': relacion.leer}
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            for ext, canon, variante in variantes:
                with self.subTest(variante=variante[:65]):
                    self.assertEqual(lectores[ext](canon), lectores[ext](variante))
                    subdir = {'.oracle': 'catalogos', '.caso': 'corpus',
                              '.relacion': 'relaciones'}[ext]
                    ruta = raiz / subdir / ('demo' + ext)
                    ruta.parent.mkdir(exist_ok=True)
                    ruta.write_text(variante, encoding='utf-8')
                    informe = sintaxis.verificar_catalogo(raiz)
                    self.assertEqual([f['ruta'] for f in informe['desformateados']],
                                     [f'{subdir}/demo{ext}'])
                    self.assertTrue(informe['desformateados'][0]['diff_forma'])
                    ruta.unlink()

    def test_formatear_conserva_comentarios_y_arbol(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            ruta = raiz / 'demo.oracle'
            original = '# explicación\n' + MEDIDA.replace('medida demo', 'medida   demo')
            ruta.write_text(original, encoding='utf-8')
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.cmd_formatear(Proyecto(raiz), str(ruta)), 0)
            self.assertEqual(ruta.read_text(), original)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.cmd_formatear(Proyecto(raiz), str(ruta), escribir=True), 0)
            self.assertEqual(ruta.read_text(), '# explicación\n' + MEDIDA)
            self.assertEqual(formato.canonico(ruta, ruta.read_text()), MEDIDA)

    def test_formatear_un_directorio_recorre_sus_fuentes_y_no_toca_diferencial(self):
        desordenada = ("medida d.m:\n    de a p\n    agrupar:\n        agregado n = contar(1)\n"
                       "        clave k = p.x\n    donde n > 1\n    resumen contar(1)\n"
                       "    umbral <= 0 segun contrato porque \"r\"\n    ambito universal\n"
                       "    alcance \"z\"\n")
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            with redirect_stdout(io.StringIO()):
                cli.main(["init", str(raiz)])
            for relativa in ("catalogos/d/d.m.oracle", "catalogos/d/sub/d.n.oracle",
                             "diferencial/no-tocar.oracle", ".oculto/tampoco.oracle",
                             "tareas/t1/catalogos/historia.oracle"):
                destino = raiz / relativa
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(desordenada.replace("d.m", "d." + destino.stem.split(".")[-1]),
                                   encoding="utf-8")
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = cli.cmd_formatear(Proyecto(raiz), str(raiz), escribir=True)
            self.assertEqual(codigo, 0, salida.getvalue())
            for relativa in ("catalogos/d/d.m.oracle", "catalogos/d/sub/d.n.oracle"):
                texto = (raiz / relativa).read_text(encoding="utf-8")
                self.assertLess(texto.index("clave k"), texto.index("agregado n"), relativa)
            for relativa in ("diferencial/no-tocar.oracle", ".oculto/tampoco.oracle",
                             "tareas/t1/catalogos/historia.oracle"):
                texto = (raiz / relativa).read_text(encoding="utf-8")
                self.assertLess(texto.index("agregado n"), texto.index("clave k"), relativa)
            self.assertIn("oracle formatear", salida.getvalue())

    def test_o_muestra_y_entre_parentesis_sin_cambiar_arbol(self):
        arbol = ['o', ['y', True, False], True]
        self.assertEqual(lector_medida._expr(arbol), '(true y false) o true')
        medida = MEDIDA.replace('    resumen contar(1)\n',
                                '    donde (true y false) o true\n    resumen contar(1)\n')
        self.assertEqual(lector_medida.leer(medida)[2][2][1], arbol)

    def test_oracle_esta_formateado(self):
        informe = sintaxis.verificar_catalogo(Path(__file__).resolve().parents[1])
        self.assertEqual(informe['ilegibles'], [])
        self.assertEqual(informe['desformateados'], [])

    def test_capa_sintaxis_del_cli_falla_aun_si_solo_hay_relaciones(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.cmd_init(str(raiz), []), 0)
            ruta = raiz / 'relaciones' / 'demo_unica.relacion'
            ruta.write_text(RELACION.replace('evento', 'demo_unica').replace(
                '        inicio:', '        "inicio":'), encoding='utf-8')
            resultado = subprocess.run(
                [sys.executable, 'tools/cli.py', 'test', '--rapido', '--proyecto', td],
                capture_output=True, text=True)
            self.assertNotEqual(resultado.returncode, 0)
            self.assertIn('SINTAXIS ✗ — 1 archivo(s) fuera de la forma única',
                          resultado.stdout)
            self.assertIn('formatear relaciones/demo_unica.relacion --escribir',
                          resultado.stdout)
