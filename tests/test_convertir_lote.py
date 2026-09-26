"""Migración de un proyecto mixto sin pérdida de árboles canónicos."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo import caso, sintaxis
from tools import cli


RAIZ = Path(__file__).resolve().parents[1]


class ConvertirLoteTests(unittest.TestCase):
    def _proyecto(self, raiz: Path):
        for nombre in ("catalogos/demo", "corpus/demo", "relaciones", "diferencial"):
            (raiz / nombre).mkdir(parents=True)
        medida = sintaxis.leer((RAIZ / "catalogos/proceso/proceso.verificador_sin_falsos_rojos.oracle")
                               .read_text(encoding="utf-8"))
        caso_datos = caso.leer((RAIZ / "corpus/meta/477-medida-universal-depende-por-requiere-de-relacion-del-origen.caso")
                               .read_text(encoding="utf-8"))
        fuentes = {
            "medida": raiz / "catalogos/demo/medida.json",
            "caso": raiz / "corpus/demo/caso.json",
            "relacion": raiz / "relaciones/item.json",
        }
        for nombre, datos in (("medida", medida), ("caso", caso_datos),
                              ("relacion", ["relacion", "item", []])):
            fuentes[nombre].write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
        (raiz / "catalogos/demo/ya.oracle").write_text("existente\n", encoding="utf-8")
        (raiz / "diferencial/fixture.json").write_text("{}", encoding="utf-8")
        return fuentes

    def _correr(self, raiz: Path, *opciones):
        salida = io.StringIO()
        with redirect_stdout(salida):
            codigo = cli.main(["convertir", str(raiz), "--a-superficie", *opciones,
                               "--proyecto", str(raiz)])
        return codigo, salida.getvalue()

    def test_vista_previa_y_escritura_de_proyecto_mixto(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            fuentes = self._proyecto(raiz)
            originales = {nombre: json.loads(ruta.read_text(encoding="utf-8"))
                         for nombre, ruta in fuentes.items()}
            codigo, salida = self._correr(raiz)
            self.assertEqual(codigo, 1)
            self.assertIn("2 convertibles; 1 no convertibles", salida)
            self.assertIn(".relacion todavía no tiene conversor", salida)
            self.assertTrue(all(ruta.exists() for ruta in fuentes.values()))
            self.assertFalse(fuentes["medida"].with_suffix(".oracle").exists())

            codigo, salida = self._correr(raiz, "--escribir")
            self.assertEqual(codigo, 1)
            self.assertIn("2 convertidos; 1 no convertibles", salida)
            self.assertEqual(sintaxis.leer(fuentes["medida"].with_suffix(".oracle").read_text()),
                             originales["medida"])
            self.assertEqual(caso.leer(fuentes["caso"].with_suffix(".caso").read_text()),
                             originales["caso"])
            self.assertFalse(fuentes["medida"].exists())
            self.assertFalse(fuentes["caso"].exists())
            self.assertTrue(fuentes["relacion"].exists())
            self.assertTrue((raiz / "diferencial/fixture.json").exists())

    def test_falla_individual_no_pisa_origen_ni_destino(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            fuentes = self._proyecto(raiz)
            destino = fuentes["medida"].with_suffix(".oracle")
            destino.write_text("conservar\n", encoding="utf-8")
            fuentes["caso"].write_text('{"campo_extra": true}', encoding="utf-8")
            originales = {nombre: ruta.read_bytes() for nombre, ruta in fuentes.items()}
            codigo, salida = self._correr(raiz, "--escribir")
            self.assertEqual(codigo, 1)
            self.assertIn("ya existe el destino", salida)
            self.assertIn("no sabe escribir", salida)
            self.assertEqual(destino.read_text(encoding="utf-8"), "conservar\n")
            for nombre, ruta in fuentes.items():
                self.assertEqual(ruta.read_bytes(), originales[nombre])

    def test_igualdad_exacta_es_obligatoria(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            fuentes = self._proyecto(raiz)
            original = fuentes["medida"].read_bytes()
            with mock.patch("tools.cli._superficie", return_value=("texto", ["otro"])):
                codigo, salida = self._correr(raiz, "--escribir")
            self.assertEqual(codigo, 1)
            self.assertIn("ida y vuelta cambió", salida)
            self.assertEqual(fuentes["medida"].read_bytes(), original)
            self.assertFalse(fuentes["medida"].with_suffix(".oracle").exists())

    def test_igualdad_distingue_tipos_json(self):
        self.assertFalse(cli._mismo_arbol({"dato": [True]}, {"dato": [1]}))
        self.assertFalse(cli._mismo_arbol([1.0], [1]))
        self.assertTrue(cli._mismo_arbol({"a": 1, "b": [False]},
                                                     {"b": [False], "a": 1}))

    def test_banderas_no_permiten_escritura_ambigua(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            self._proyecto(raiz)
            for args, esperado in ((["--escribir"], "requiere --a-superficie"),
                                   (["--desconocida"], "opción desconocida"),
                                   (["--a-superficie", "otra"], "una sola ruta")):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    codigo = cli.main(["convertir", str(raiz), *args,
                                       "--proyecto", str(raiz)])
                self.assertEqual(codigo, 1)
                self.assertIn(esperado, salida.getvalue())
