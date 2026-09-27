"""Regresiones de las fronteras públicas ante relaciones duplicadas."""
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from nucleo.proyecto import Proyecto, ProyectoInvalido, relaciones_del_proyecto



def _medida(mid: str) -> list:
    """Una medida mínima (antes venía de tests/test_mcp.py, que se fue con oracle-mcp)."""
    return ["medida", mid, ["desde", ["de", "item", "i"]], ["resumen", "contar", 1],
            ["umbral", "<=", 0, "ningún item ofensivo", "contrato"],
            ["ambito", "universal"], ["alcance", "NO ve propiedades distintas de la presencia del item"]]


def _proyecto(raiz: Path, *medidas: list) -> Path:
    catalogos = raiz / "catalogos" / "demo"
    catalogos.mkdir(parents=True)
    for datos in medidas:
        (catalogos / f"{datos[1]}.json").write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return raiz

RAIZ = Path(__file__).resolve().parents[1]


class RelacionDuplicadaTests(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = _proyecto(Path(self.temporal.name), _medida('demo.uno'))
        (self.raiz / 'oracle.json').write_text('{"esquema": "oracle.proyecto/v1", "catalogo_base": true}', encoding='utf-8')
        for nombre in ('corpus', 'diferencial', 'relaciones'):
            (self.raiz / nombre).mkdir()
        shutil.copy(RAIZ / 'relaciones/pieza.relacion', self.raiz / 'relaciones/pieza.relacion')
        (self.raiz / 'hechos.json').write_text('{"item": []}', encoding='utf-8')

    def comprobar_diagnostico(self, texto):
        self.assertIn('pieza', texto)
        self.assertIn(str(RAIZ / 'relaciones/pieza.relacion'), texto)
        self.assertIn(str(self.raiz / 'relaciones/pieza.relacion'), texto)
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

    def test_duplicado_local_no_se_atribuye_a_oracle(self):
        (self.raiz / 'oracle.json').unlink()
        shutil.copy(self.raiz / 'relaciones/pieza.relacion', self.raiz / 'relaciones/otra.relacion')
        with self.assertRaisesRegex(ProyectoInvalido, 'está dos veces') as error:
            relaciones_del_proyecto(Proyecto(self.raiz))
        self.assertNotIn('ya existe en Oracle', str(error.exception))

    def test_base_no_seleccionada_permite_relacion_propia(self):
        (self.raiz / 'oracle.json').unlink()
        declaradas = relaciones_del_proyecto(Proyecto(self.raiz))
        self.assertEqual(set(declaradas), {'pieza'})

    def test_declaracion_malformada_se_informa_como_proyecto_invalido(self):
        (self.raiz / 'relaciones/pieza.relacion').write_text('{', encoding='utf-8')
        with self.assertRaisesRegex(ProyectoInvalido, 'relacion <nombre>'):
            relaciones_del_proyecto(Proyecto(self.raiz))
