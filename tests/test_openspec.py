"""`oracle requisito importar`: las promesas de una spec de OpenSpec como requisitos sin medir."""

from __future__ import annotations

import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nucleo.requisito import RequisitoMalDeclarado, cargar_requisitos
from tools.openspec import requisitos_de_spec

SPEC = """# CLI Validate

## Purpose
Validar. Esto no es un requisito.

## Requirements

### Requirement: Paths in every issue
All issues SHALL include the file path.
- It SHALL also name the line.

#### Scenario: Zod validation error
- **WHEN** a schema fails
- **THEN** the issue names the file

```markdown
### Requirement: Ejemplo dentro de un bloque
#### Scenario: Tampoco cuenta
```

#### Scenario: Missing section
- **WHEN** a section is missing
- **THEN** the issue names it

### Requirement: Sin escenarios
El texto.

### Requirement: Ñandú 2
Otro.

## Why
Esto tampoco.
"""


class LeerSpecTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.spec = self.dir / "spec.md"
        self.spec.write_text(SPEC, encoding="utf-8")

    def test_requisitos_texto_fuente_y_escenarios(self) -> None:
        r1, r2, r3 = requisitos_de_spec(self.spec, "cli_validate")
        self.assertEqual(r1.id, "cli_validate.paths_in_every_issue")
        self.assertEqual(r1.texto, "All issues SHALL include the file path. It SHALL also name the line.")
        self.assertEqual(r1.fuente, f"{self.spec}#Paths in every issue")
        self.assertEqual(r1.medido_por, ())
        self.assertEqual(r1.sin_medir, "sin medida todavía; escenarios: «Zod validation error», «Missing section»")
        self.assertEqual((r2.id, r2.texto, r2.sin_medir), ("cli_validate.sin_escenarios", "El texto.", "sin medida todavía"))
        self.assertEqual(r3.id, "cli_validate.nandu_2")

    def test_el_nombre_es_el_texto_si_no_hay_parrafo_y_un_digito_inicial_se_prefija(self) -> None:
        self.spec.write_text("### Requirement: 3 pasos\n#### Scenario: s\n", encoding="utf-8")
        (r,) = requisitos_de_spec(self.spec, "d")
        self.assertEqual((r.id, r.texto), ("d.r_3_pasos", "3 pasos"))

    def test_ids_repetidos_o_invalidos(self) -> None:
        self.spec.write_text("### Requirement: A b\n### Requirement: a-b\n", encoding="utf-8")
        with self.assertRaisesRegex(RequisitoMalDeclarado, "mismo id d.a_b"):
            requisitos_de_spec(self.spec, "d")
        self.spec.write_text("### Requirement: ¿?\n", encoding="utf-8")
        with self.assertRaisesRegex(RequisitoMalDeclarado, "no da un id válido"):
            requisitos_de_spec(self.spec, "d")


class ImportarTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir)
        self.raiz = self.dir / "proyecto"
        for d in ("catalogos", "corpus", "diferencial"):
            (self.raiz / d).mkdir(parents=True)
        (self.raiz / "oracle.json").write_text(
            '{"esquema": "oracle.proyecto/v1", "catalogo_base": false, "perfiles": []}\n', encoding="utf-8")
        self.specs = self.dir / "openspec" / "specs"
        (self.specs / "cli-validate").mkdir(parents=True)
        (self.specs / "cli-validate" / "spec.md").write_text(SPEC, encoding="utf-8")

    def _cli(self, *args: str) -> tuple[int, str]:
        from tools import cli
        with redirect_stdout(io.StringIO()) as salida:
            codigo = cli.main(["requisito", *args, "--proyecto", str(self.raiz)])
        return codigo, salida.getvalue()

    def test_sin_escribir_no_toca_nada_y_con_escribir_carga(self) -> None:
        codigo, texto = self._cli("importar", str(self.specs))
        self.assertEqual(codigo, 0)
        self.assertIn("+ cli_validate.paths_in_every_issue   sin medida todavía; escenarios:", texto)
        self.assertIn("3 requisitos nuevos; repetí con --escribir", texto)
        self.assertFalse((self.raiz / "requisitos").exists())
        codigo, texto = self._cli("importar", str(self.specs), "--escribir")
        self.assertEqual(codigo, 0)
        self.assertIn("3 requisitos escritos en", texto)
        self.assertEqual(sorted(cargar_requisitos(self.raiz / "requisitos")),
                         ["cli_validate.nandu_2", "cli_validate.paths_in_every_issue", "cli_validate.sin_escenarios"])

    def test_lo_que_ya_existe_no_se_toca(self) -> None:
        self._cli("importar", str(self.specs), "--escribir")
        ruta = self.raiz / "requisitos" / "cli_validate.sin_escenarios.requisito"
        propio = ruta.read_text(encoding="utf-8").replace("sin medida todavía", "lo decidí yo")
        ruta.write_text(propio, encoding="utf-8")
        codigo, texto = self._cli("importar", str(self.specs / "cli-validate" / "spec.md"), "--escribir")
        self.assertEqual(codigo, 0)
        self.assertIn("= cli_validate.sin_escenarios   ya existe; no se toca", texto)
        self.assertIn("0 requisitos escritos", texto)
        self.assertEqual(ruta.read_text(encoding="utf-8"), propio)

    def test_dominio_propio(self) -> None:
        codigo, texto = self._cli("importar", str(self.specs), "--dominio", "validar")
        self.assertEqual(codigo, 0)
        self.assertIn("+ validar.paths_in_every_issue", texto)
        codigo, texto = self._cli("importar", str(self.specs), "--dominio", "Mal-Dominio")
        self.assertEqual(codigo, 1)
        self.assertIn("✗ dominio inválido", texto)

    def test_errores(self) -> None:
        for args, esperado in (
                (("importar", str(self.dir / "no-existe")), "✗ no existe"),
                (("importar", str(self.dir)), "no tiene ninguna <capacidad>/spec.md"),
                (("importar",), "uso: oracle requisito importar"),
                (("importar", str(self.specs), "--dominio"), "uso: oracle requisito importar"),
                ((), "uso: oracle requisito importar"),
                (("borrar", "x"), "borrar")):
            with self.subTest(args=args):
                codigo, texto = self._cli(*args)
                self.assertEqual(codigo, 1)
                self.assertIn(esperado, texto)
        (self.specs / "cli-validate" / "spec.md").write_text("### Requirement: A\n### Requirement: a\n",
                                                            encoding="utf-8")
        codigo, texto = self._cli("importar", str(self.specs))
        self.assertEqual(codigo, 1)
        self.assertIn("✗ ", texto)
        self.assertIn("mismo id", texto)

    def test_un_requisito_existente_mal_escrito_se_dice(self) -> None:
        (self.raiz / "requisitos").mkdir()
        (self.raiz / "requisitos" / "x.malo.requisito").write_text("basura\n", encoding="utf-8")
        codigo, texto = self._cli("importar", str(self.specs))
        self.assertEqual(codigo, 1)
        self.assertTrue(texto.startswith("✗ "), texto)


if __name__ == "__main__":
    unittest.main()
