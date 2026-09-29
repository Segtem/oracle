from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nucleo.proyecto import Proyecto
from tools import cli
from tools.escenario import comentario, de_spec, leer

SPEC = """# cap Specification

## Requirements
### Requirement: Foo
The system SHALL foo.

#### Scenario: Primero
- **GIVEN** una spec
- **AND** un cambio
- **WHEN** se valida
  - con `--strict`
- **THEN** sale con 1
- **AND** avisa

#### Scenario: Con código
- **WHEN** hay viñetas
- **THEN** avisa con una plantilla:
```
#### Scenario: Falso
- **WHEN** esto no cuenta
```

### Requirement: Bar
"""


class LeerTests(unittest.TestCase):
    def test_vinetas_de_openspec(self) -> None:
        self.assertEqual(leer(de_spec(self._spec(), "Primero")), {
            "dado": ["una spec", "un cambio"],
            "cuando": ["se valida con `--strict`"],
            "entonces": ["sale con 1", "avisa"]})

    def test_una_linea_y_castellano(self) -> None:
        self.assertEqual(leer("WHEN corro validate THEN sale con 1"),
                         {"dado": [], "cuando": ["corro validate"], "entonces": ["sale con 1"]})
        self.assertEqual(leer("CUANDO: se valida y falla\nENTONCES sale con 1\nY lista las banderas"),
                         {"dado": [], "cuando": ["se valida y falla"],
                          "entonces": ["sale con 1", "lista las banderas"]})

    def test_una_clave_pegada_a_otra_palabra_no_es_clave(self) -> None:
        self.assertEqual(leer("WHEN bullets that start with WHEN/THEN/AND are found THEN warn")["cuando"],
                         ["bullets that start with WHEN/THEN/AND are found"])

    def test_rechaza(self) -> None:
        for texto in ("THEN sale con 1", "WHEN algo", "AND algo WHEN x THEN y", "sin claves", "WHEN THEN y"):
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                leer(texto)

    def _spec(self) -> Path:
        ruta = Path(tempfile.mkdtemp()) / "spec.md"
        self.addCleanup(lambda: __import__("shutil").rmtree(ruta.parent))
        ruta.write_text(SPEC, encoding="utf-8")
        return ruta

    def test_de_spec_se_detiene_y_saltea_el_codigo(self) -> None:
        texto = de_spec(self._spec(), "Con código")
        self.assertIn("avisa con una plantilla", texto)
        self.assertNotIn("Falso", texto)
        self.assertNotIn("Requirement: Bar", texto)
        with self.assertRaisesRegex(ValueError, "no tiene un «#### Scenario: Falso»"):
            de_spec(self._spec(), "Falso")
        with self.assertRaisesRegex(ValueError, "no tiene un «#### Scenario: Nada»"):
            de_spec(self._spec(), "Nada")

    def test_comentario(self) -> None:
        self.assertEqual(comentario(leer("GIVEN a WHEN b THEN c AND d"), "Escenario «x»"),
                         "# Escenario «x»\n#   DADO a\n#   CUANDO b\n#   ENTONCES c\n#   ENTONCES d\n"
                         "# Lo que ofende: que pase lo de CUANDO y no lo de ENTONCES.\n")


class NuevaDesdeEscenarioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raiz = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(self.raiz))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(cli.cmd_init(str(self.raiz), []), 0)
        (self.raiz / "spec.md").write_text(SPEC, encoding="utf-8")
        (self.raiz / "requisitos").mkdir()
        (self.raiz / "requisitos" / "cap.foo.requisito").write_text(
            'requisito cap.foo:\n    texto "Foo"\n    sin_medir "todavía nada"\n', encoding="utf-8")

    def _nueva(self, *opciones: str) -> tuple[int, str]:
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = cli.cmd_nueva(Proyecto(self.raiz), "cap.primero", list(opciones))
        return codigo, salida.getvalue()

    def _archivos(self) -> list[str]:
        return sorted(p.relative_to(self.raiz).as_posix() for p in self.raiz.rglob("*") if p.is_file())

    def test_desde_una_spec_y_con_requisito(self) -> None:
        codigo, texto = self._nueva("--escenario-de", str(self.raiz / "spec.md"), "Primero",
                                    "--requisito", "cap.foo")
        self.assertEqual(codigo, 0, texto)
        medida = (self.raiz / "catalogos/cap/cap.primero.oracle").read_text(encoding="utf-8")
        self.assertTrue(medida.startswith(f"# Escenario «Primero» de {self.raiz / 'spec.md'}\n#   DADO una spec\n"))
        self.assertIn("\nninguno cap.primero:\n", medida)
        rojo = (self.raiz / "corpus/cap/001-primero-rojo.caso").read_text(encoding="utf-8")
        verde = (self.raiz / "corpus/cap/002-primero-verde.caso").read_text(encoding="utf-8")
        self.assertIn('titulo: "«Primero» — no se cumple"', rojo)
        self.assertIn("Pasa lo del escenario: se valida con `--strict`. Y NO se cumple: sale con 1; avisa.", rojo)
        self.assertIn('titulo: "«Primero» — se cumple"', verde)
        self.assertIn("Y se cumple: sale con 1; avisa.", verde)
        self.assertEqual((self.raiz / "requisitos/cap.foo.requisito").read_text(encoding="utf-8"),
                         'requisito cap.foo:\n    texto "Foo"\n    medido_por cap.primero\n    sin_medir "todavía nada"\n')
        self.assertIn("requisito: cap.foo ahora dice medido_por cap.primero", texto)

    def test_escenario_en_linea_sin_titulo(self) -> None:
        codigo, _ = self._nueva("--escenario", "WHEN corro THEN sale con 1")
        self.assertEqual(codigo, 0)
        medida = (self.raiz / "catalogos/cap/cap.primero.oracle").read_text(encoding="utf-8")
        self.assertTrue(medida.startswith("# Escenario\n#   CUANDO corro\n"))
        rojo = (self.raiz / "corpus/cap/001-primero-rojo.caso").read_text(encoding="utf-8")
        self.assertIn('titulo: "TITULO"', rojo)

    def test_un_error_no_deja_nada_escrito(self) -> None:
        antes = self._archivos()
        for opciones, esperado in (
                (("--requisito", "cap.no_existe"), "cap.no_existe.requisito"),
                (("--escenario", "sin claves"), "✗ escenario: "),
                (("--escenario-de", str(self.raiz / "spec.md"), "Nada"), "✗ escenario: "),
                (("--escenario-de", str(self.raiz / "no.md"), "Primero"), "✗ escenario: "),
                (("--escenario", "WHEN a THEN b", "--escenario-de", "spec.md", "Primero"), "uso: oracle medida nueva"),
                (("--escenario",), "uso: oracle medida nueva"),
                (("--otra", "x"), "uso: oracle medida nueva"),
                (("--requisito", "cap.foo", "--requisito", "cap.foo"), "uso: oracle medida nueva")):
            with self.subTest(opciones=opciones):
                codigo, texto = self._nueva(*opciones)
                self.assertEqual(codigo, 1)
                self.assertIn(esperado, texto)
                self.assertEqual(self._archivos(), antes)

    def test_por_la_cli(self) -> None:
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = cli.main(["medida", "nueva", "cap.primero", "--escenario", "WHEN a THEN b",
                               "--proyecto", str(self.raiz)])
        self.assertEqual(codigo, 0, salida.getvalue())
        self.assertTrue((self.raiz / "catalogos/cap/cap.primero.oracle").is_file())


if __name__ == "__main__":
    unittest.main()
