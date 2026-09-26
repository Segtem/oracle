"""Custodia la sintaxis que las interfaces públicas enseñan a escribir."""

import unittest
from pathlib import Path

from nucleo.algebra import ESCALARES
from nucleo.proyecto import Proyecto
from tools import contexto, manual, mcp

RAIZ = Path(__file__).resolve().parents[1]


class EnsenanzaUnaSintaxisTests(unittest.TestCase):
    def test_mcp_solo_recibe_medidas_en_superficie(self):
        for herramienta in mcp.HERRAMIENTAS:
            esquema = herramienta["inputSchema"]["properties"].get("medida")
            if esquema is not None:
                por_texto = next(rama for rama in esquema["oneOf"]
                                 if "texto" in rama["properties"])
                self.assertEqual(por_texto["properties"]["formato"], {"const": "oracle"})
        with self.assertRaises(mcp.ErrorHerramienta):
            mcp._validar_evaluacion({"medida": {"texto": '["medida"]', "formato": "json"},
                                    "evidencia": {}})

    def test_contexto_muestra_expresiones_de_superficie(self):
        texto = contexto.texto(Proyecto(RAIZ), compacto=True)
        seccion = texto.split("## CON QUÉ SE ESCRIBE", 1)[1].split("## LAS ", 1)[0]
        self.assertIn("p.x", seccion)
        self.assertIn("a + b", seccion)
        self.assertNotIn('["campo"', seccion)
        for nombre in ("mas/", "menos/", "por/"):
            self.assertNotIn(nombre, seccion)
        for nombre in ESCALARES:
            if nombre not in {"mas", "menos", "por"}:
                self.assertIn(nombre + "/", seccion)

    def test_documentos_y_manual_no_ofrecen_json_como_autoria(self):
        contrato = (RAIZ / "docs/mcp-contrato.md").read_text()
        readme = (RAIZ / "README.md").read_text()
        guia = (RAIZ / "docs/03-escribir-una-medida.md").read_text()
        self.assertNotRegex(contrato, r'"formato":\s*"oracle"\s*\|\s*"json"')
        self.assertNotRegex(readme, r'\(\.oracle y \.json\)|\(\.caso y \.json\)')
        self.assertNotRegex(guia, r'cargan[^\n]*\.json por igual|convertir <archivo\.oracle>')
        self.assertIn("fila {…}", manual.texto("casos"))
        self.assertIn("fila {…}", (RAIZ / "ESPECIFICACION.md").read_text())
        self.assertIn("formato de intercambio", guia)
        self.assertNotIn("traduce entre superficie y JSON", (RAIZ / "tools/cli.py").read_text())


if __name__ == "__main__":
    unittest.main()
