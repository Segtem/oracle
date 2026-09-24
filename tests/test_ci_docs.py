"""El CI debe mirar los documentos que forman parte de sus verificaciones."""

import json
import unittest
from fnmatch import fnmatchcase
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]


class TestFiltroDeCI(unittest.TestCase):
    def test_push_y_pull_request_no_ignoran_documentos_verificados(self):
        texto = (RAIZ / ".github/workflows/verificar.yml").read_text(encoding="utf-8")
        filtros = [json.loads(linea.split("paths-ignore:", 1)[1].strip())
                   for linea in texto.splitlines() if linea.strip().startswith("paths-ignore:")]
        self.assertEqual(len(filtros), 2)
        for ignorados in filtros:
            for archivo in ("README.md", ".gitignore", "docs/03-escribir-una-medida.md",
                            "docs/tutorial-practico.md", "docs/mcp-contrato.md",
                            "docs/decisiones/DECISION-001-EJEMPLO.md"):
                with self.subTest(archivo=archivo):
                    self.assertFalse(any(fnmatchcase(archivo, patron) for patron in ignorados))
            self.assertTrue(any(fnmatchcase("vault-kb/planes/PLAN.md", patron)
                                for patron in ignorados))
            self.assertTrue(any(fnmatchcase("tareas/123/TAREA.md", patron)
                                for patron in ignorados))


if __name__ == "__main__":
    unittest.main()
