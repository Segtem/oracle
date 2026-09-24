"""Las citas normativas y la raíz documental tienen destinos verificables."""

import re
import unittest
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
REGISTRO = RAIZ / "docs" / "decisiones"
FUENTES = ("nucleo", "tools", "tests", "docs", "vault-kb", "diferencial",
           "ejemplo", "observaciones", "catalogos", "relaciones", "perfiles", "mutadores")
EXTENSIONES = {".py", ".md", ".html", ".json", ".sh", ".cjs", ".toml"}


class TestDocumentosRepo(unittest.TestCase):
    def test_cada_decision_citada_existe(self) -> None:
        decisiones = list(REGISTRO.glob("DECISION-*.md"))
        ids = [re.match(r"DECISION-(\d{3})-", p.name)[1] for p in decisiones]
        self.assertEqual(len(ids), len(set(ids)), "hay ids de decisión duplicados")
        existentes = set(ids)
        fuentes = [p for carpeta in FUENTES for p in (RAIZ / carpeta).rglob("*")
                   if p.is_file() and p.suffix in EXTENSIONES]
        fuentes += [RAIZ / nombre for nombre in ("README.md", "ESPECIFICACION.md",
                    "NOTAS-DE-RELEASE.md", "AGENTS.md", "pyproject.toml")]
        faltantes = []
        for p in fuentes:
            try:
                texto = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for numero in set(re.findall(r"\bDECISION-(\d{3})\b", texto)):
                if numero not in existentes:
                    faltantes.append(f"{p.relative_to(RAIZ)}: DECISION-{numero}")
        self.assertEqual(faltantes, [])

    def test_no_hay_documentos_sueltos_nuevos_en_la_raiz(self) -> None:
        permitidos = {"AGENTS.md", "ESPECIFICACION.md", "NOTAS-DE-RELEASE.md", "README.md"}
        encontrados = {p.name for p in RAIZ.glob("*.md")}
        self.assertEqual(encontrados - permitidos, set())


if __name__ == "__main__":
    unittest.main()
