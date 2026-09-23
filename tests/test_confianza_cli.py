"""Regresiones de confianza explícita y de la receta local copiable."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parents[1]


class ConfianzaCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="oracle confianza ")
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        for nombre in ("catalogos", "corpus", "diferencial"):
            (self.raiz / nombre).mkdir()
        (self.raiz / "oracle.json").write_text('{"esquema": "oracle.proyecto/v1", "catalogo_base": false}')
        (self.raiz / "catalogos/demo.oracle").write_text('''medida demo.prueba:
    de dato a
    donde a.x > 0
    resumen contar(1)
    umbral <= 0 segun contrato porque "prueba"
    ambito universal
    alcance "no ve otros datos"
''')
        (self.raiz / "hechos con espacios.json").write_text('{"dato": [{"x": 0}]}')
        (self.raiz / "escalares.py").write_text('# Sin funciones externas.\n')
        for cid, x, etiqueta in (("001-verde", 0, "verde_correcto"), ("002-rojo", 1, "falso_verde")):
            (self.raiz / "corpus" / f"{cid}.json").write_text(json.dumps({
                "id": cid, "fecha": "2026-09-23",
                "origen": {"repo": "prueba", "commit": "local"},
                "procedencia": "construida", "titulo": cid, "etiqueta": etiqueta,
                "sintoma": "Valores positivos son defectos.", "como_se_detecto": "persona",
                "medida": "demo.prueba", "evidencia": {"dato": [{"x": x}]},
                "leccion": "Distinguir cero de un valor positivo.",
            }))

    def correr(self, args, **kwargs):
        return subprocess.run(args, cwd="/tmp", capture_output=True, text=True,
                              timeout=30, **kwargs)

    def cli(self, *args):
        return self.correr([sys.executable, str(RAIZ / "tools/cli.py"),
                           *args, "--proyecto", str(self.raiz)])

    def wrapper(self):
        texto = (RAIZ / "README.md").read_text()
        inicio = texto.index('```sh\n#!/bin/sh\n') + len('```sh\n')
        receta = texto[inicio:texto.index('```', inicio)]
        destino = self.raiz / "oracle-local"
        destino.write_text(receta)
        destino.chmod(0o755)
        return destino

    def test_generar_sin_confianza_no_ejecuta_ni_escribe_y_explica(self):
        marca = self.raiz / "ejecutado"
        (self.raiz / "escalares.py").write_text(
            f'from pathlib import Path\nPath({str(marca)!r}).touch()\n')
        antes = set(self.raiz.rglob('*'))
        for extras in ([], ["--imprimir"], ["--directorio", str(self.raiz / "salida")]):
            with self.subTest(extras=extras):
                r = self.cli("caso", "generar", "demo.prueba", *extras)
                self.assertEqual(r.returncode, 1)
                self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS", r.stdout)
                self.assertIn("código Python externo", r.stdout)
                self.assertIn("--confiar-escalares", r.stdout)
                self.assertEqual(r.stderr, "")
                self.assertEqual(set(self.raiz.rglob('*')), antes)
                self.assertFalse(marca.exists())

    def test_wrapper_conserva_argumentos_y_codigo(self):
        wrapper = self.wrapper()
        binario = self.raiz / "bin"
        binario.mkdir()
        oracle = binario / "oracle"
        oracle.write_text(f'#!{sys.executable}\nimport json, sys\n'
                          'print(json.dumps(sys.argv[1:]))\nsys.exit(37)\n')
        oracle.chmod(0o755)
        args = ["caso", "generar", "demo.prueba", "", "ruta con espacios", "*.json"]
        r = self.correr([str(wrapper), *args], env={**os.environ, "PATH": str(binario) + os.pathsep + os.environ["PATH"]})
        self.assertEqual(r.returncode, 37)
        self.assertEqual(json.loads(r.stdout), args + ["--proyecto", str(self.raiz), "--confiar-escalares"])

    def test_wrapper_permite_los_cinco_comandos_como_invocacion_explicita(self):
        wrapper = self.wrapper()
        binario = self.raiz / "bin"
        binario.mkdir()
        oracle = binario / "oracle"
        import shlex
        oracle.write_text('#!/bin/sh\nexec ' + shlex.join([sys.executable, str(RAIZ / "tools/cli.py")]) + ' "$@"\n')
        oracle.chmod(0o755)
        for args, sin_confianza in (
            (["test", "--rapido"], 1),
            (["juzgar", "--con", str(self.raiz / "hechos con espacios.json")], 2),
            (["revisar", "catalogos/demo.oracle"], 1),
            (["medida", "listar"], 1),
            (["caso", "generar", "demo.prueba", "--imprimir"], 1),
        ):
            with self.subTest(args=args):
                rechazado = self.cli(*args)
                self.assertEqual(rechazado.returncode, sin_confianza)
                self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS", rechazado.stdout + rechazado.stderr)
                directo = self.cli(*args, "--confiar-escalares")
                self.assertEqual(directo.returncode, 0, directo.stdout + directo.stderr)
                local = self.correr([str(wrapper), *args], env={**os.environ, "PATH": str(binario) + os.pathsep + os.environ["PATH"]})
                self.assertEqual((local.returncode, local.stdout, local.stderr),
                                 (directo.returncode, directo.stdout, directo.stderr))
                self.assertNotIn("ESCALARES EXTERNAS NO EJECUTADAS", local.stdout)
                self.assertNotIn("Traceback", local.stderr)
