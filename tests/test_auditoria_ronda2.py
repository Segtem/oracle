"""La salida MCP exige que todas las medidas propias hayan recibido relaciones."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nucleo.proyecto import Proyecto
from tools import cli, mcp


class McpNoAplicadasTests(unittest.TestCase):
    def test_mcp_no_aprueba_si_una_medida_propia_quedo_sin_aplicar(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            (raiz / "oracle.json").write_text(json.dumps({
                "esquema": "oracle.proyecto/v1", "catalogo_base": False, "perfiles": [],
            }))
            for nombre, relacion in (("uno", "item"), ("dos", "otro")):
                (raiz / "catalogos" / f"{nombre}.oracle").write_text(
                    f"medida demo.{nombre}:\n"
                    f"    de {relacion} i\n"
                    '    resumen contar(1)\n'
                    '    umbral >= 0 segun contrato porque "conteo"\n'
                    '    ambito universal\n'
                    '    alcance "conteo"\n')
            evidencia = {"item": [{"id": 1}]}
            ruta_evidencia = raiz / "e.json"
            ruta_evidencia.write_text(json.dumps(evidencia))
            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main(["juzgar", "--proyecto", str(raiz), "--con",
                               str(ruta_evidencia), "--json"])
            self.assertEqual(rc, 1)
            self.assertIs(json.loads(salida.getvalue())["ok"], False)

            resultado = mcp.juzgar_para_mcp(Proyecto(raiz), {"evidencia": evidencia})
            self.assertEqual(resultado["no_aplicadas"], [
                {"id": "demo.dos", "faltan": ["otro"]}])
            self.assertIs(resultado["ok"], False)


if __name__ == "__main__":
    unittest.main()
