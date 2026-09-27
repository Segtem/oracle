"""`oracle_metalenguaje.nucleo.X` y `nucleo.X` tienen que ser el MISMO módulo en el wheel.

Hasta 0.33.0, un consumidor que importaba `oracle_metalenguaje.nucleo.X` después de que Oracle
arrancara (y Oracle arranca importando `nucleo.X`) recibía una segunda copia: otras clases, y un
`isinstance` que fallaba sin explicación. Lo destapó oracle-mcp al salir del repositorio.

El test arma un paquete con la forma del wheel instalado —`<paquete>/nucleo/`, con la fachada que
llama a `cargar_interno`— y lo importa en los dos órdenes, cada uno en su propio proceso.
"""
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

PRUEBA = textwrap.dedent("""
    import importlib, sys
    import falso
    orden = sys.argv[1:]
    nombres = {"externo": "falso.nucleo.hijo", "interno": "nucleo.hijo"}
    a, b = (importlib.import_module(nombres[o]) for o in orden)
    print(a is b, a.Clase is b.Clase)
""")


class MismoModuloTests(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        paquete = self.raiz / "falso"
        (paquete / "nucleo").mkdir(parents=True)
        shutil.copy(RAIZ / "oracle_metalenguaje/_compat.py", paquete / "_compat.py")
        (paquete / "__init__.py").write_text(
            "from ._compat import cargar_interno\ncargar_interno('nucleo', __name__)\n"
            "import nucleo.otro  # como la fachada real, que ya usa el núcleo al arrancar\n")
        (paquete / "nucleo/__init__.py").write_text("")
        (paquete / "nucleo/otro.py").write_text("")
        (paquete / "nucleo/hijo.py").write_text("class Clase:\n    pass\n")

    def importar(self, *orden):
        salida = subprocess.run([sys.executable, "-B", "-c", PRUEBA, *orden], cwd=self.raiz,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(salida.returncode, 0, salida.stderr)
        return salida.stdout.split()

    def test_el_nombre_largo_despues_del_corto_da_el_mismo_modulo(self):
        self.assertEqual(self.importar("interno", "externo"), ["True", "True"])

    def test_el_nombre_largo_antes_del_corto_da_el_mismo_modulo(self):
        self.assertEqual(self.importar("externo", "interno"), ["True", "True"])

    def test_un_nombre_corto_ajeno_no_se_toca(self):
        # Si `nucleo` en sys.modules no es el de Oracle, el buscador se hace a un lado.
        from unittest import mock
        import types
        from oracle_metalenguaje._compat import _MismoModulo
        buscador = _MismoModulo("falso", "nucleo")
        with mock.patch.dict(sys.modules, {"nucleo": types.ModuleType("nucleo"),
                                           "falso.nucleo": types.ModuleType("falso.nucleo")}):
            self.assertIsNone(buscador.find_spec("falso.nucleo.hijo"))
        self.assertIsNone(buscador.find_spec("otro.nucleo.hijo"))


if __name__ == "__main__":
    unittest.main()
