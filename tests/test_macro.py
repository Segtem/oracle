"""Tests de las macros. Una macro que expande mal es peor que no tenerla: mueve el error a un lugar
donde nadie lo mira."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos  # noqa: F401
from nucleo.macro import MACROS, MacroMalUsada, es_macro, expandir
from nucleo.medida import Medida, cargar_catalogo

PRED = ["==", ["campo", "m", "murio"], False]


class ExpansionTests(unittest.TestCase):
    def test_ninguno_da_la_forma_de_contar_lo_que_ofende(self) -> None:
        d = expandir(["ninguno", "d.p", "mutante", "m", PRED, "razón", "NO ve nada"])
        self.assertEqual(d, ["medida", "d.p",
                             ["desde", ["de", "mutante", "m"], ["donde", PRED]],
                             ["resumen", "contar", 1],
                             ["umbral", "<=", 0, "razón"],
                             ["alcance", "NO ve nada"]])

    def test_ninguno_par_une_la_relacion_consigo_misma(self) -> None:
        d = expandir(["ninguno-par", "d.p", "doc", "a", "b", PRED, "razón", "NO ve nada"])
        self.assertEqual(d[2][1], ["unir", ["de", "doc", "a"], ["de", "doc", "b"]])

    def test_ninguno_par_con_el_mismo_alias_dos_veces_no_pasa(self) -> None:
        with self.assertRaises(MacroMalUsada) as e:
            expandir(["ninguno-par", "d.p", "doc", "a", "a", PRED, "r", "NO ve"])
        self.assertIn("distintos", str(e.exception))

    def test_peor_escribe_la_tolerancia_UNA_vez_y_la_pone_en_los_dos_lados(self) -> None:
        """Es el caso 012 del corpus, cerrado por construcción: la tolerancia estaba duplicada en el
        filtro y en el umbral, y nada las mantenía juntas."""
        expr = ["desvio_de_grilla", ["hecho", "a"], 100.0]
        d = expandir(["peor", "snap.x", "pieza", "a", expr, 1.0, "razón", "NO ve nada"])

        self.assertEqual(d[2][2], ["donde", [">", expr, 1.0]])   # el filtro
        self.assertEqual(d[3], ["resumen", "max", expr])          # la medición
        self.assertEqual(d[4][2], 1.0)                            # el umbral
        # y la expresión es LA MISMA en el filtro y en el resumen: no hay dos copias que divergir
        self.assertIs(d[2][2][1][1], d[3][2])

    def test_cada_macro_exige_su_cantidad_de_argumentos(self) -> None:
        for nombre in MACROS:
            with self.subTest(macro=nombre):
                with self.assertRaises(MacroMalUsada):
                    expandir([nombre, "d.p", "faltan", "cosas"])

    def test_lo_canonico_pasa_de_largo(self) -> None:
        canonica = ["medida", "d.p", ["desde", ["de", "m", "m"]], ["resumen", "contar", 1],
                    ["umbral", "<=", 0, "r"], ["alcance", "NO ve"]]
        self.assertFalse(es_macro(canonica))
        self.assertIs(expandir(canonica), canonica)

    def test_expandir_es_idempotente(self) -> None:
        una = expandir(["ninguno", "d.p", "mutante", "m", PRED, "razón", "NO ve nada"])
        self.assertEqual(expandir(una), una)


class ContratoConLaMedidaTests(unittest.TestCase):
    def test_una_macro_construye_una_medida_igual_que_la_canonica(self) -> None:
        macro = Medida.de_datos(["ninguno", "d.p", "mutante", "m", PRED, "razón", "NO ve nada"])
        canonica = Medida.de_datos(macro.a_datos())
        for campo in ("id", "tuberia", "resumen", "op", "limite", "porque", "alcance"):
            self.assertEqual(getattr(macro, campo), getattr(canonica, campo), campo)

    def test_a_datos_devuelve_SIEMPRE_la_canonica(self) -> None:
        m = Medida.de_datos(["ninguno", "d.p", "mutante", "m", PRED, "razón", "NO ve nada"])
        self.assertEqual(m.a_datos()[0], "medida")

    def test_a_fuente_devuelve_como_esta_escrita(self) -> None:
        m = Medida.de_datos(["ninguno", "d.p", "mutante", "m", PRED, "razón", "NO ve nada"])
        self.assertEqual(m.a_fuente()[0], "ninguno")
        c = Medida.de_datos(m.a_datos())
        self.assertEqual(c.a_fuente()[0], "medida")

    def test_una_macro_mal_usada_falla_al_LEERSE(self) -> None:
        with self.assertRaises(MacroMalUsada):
            Medida.de_datos(["peor", "d.p", "faltan"])


class CatalogoRealTests(unittest.TestCase):
    """El catálogo del repo: 26 de 27 medidas están escritas como macro."""

    def setUp(self) -> None:
        self.catalogo = cargar_catalogo(RAIZ / "catalogos")
        self.crudos = {json.loads(p.read_text(encoding="utf-8"))[1]:
                       json.loads(p.read_text(encoding="utf-8"))
                       for p in (RAIZ / "catalogos").rglob("*.json")}

    def test_todas_cargan_y_la_mayoria_son_macro(self) -> None:
        macros = sum(1 for d in self.crudos.values() if es_macro(d))
        self.assertGreaterEqual(macros, 24)
        self.assertEqual(len(self.catalogo), len(self.crudos))

    def test_la_expansion_de_cada_una_vuelve_a_construir_lo_mismo(self) -> None:
        """Idempotencia sobre el catálogo real: expandir y volver a leer no puede cambiar nada."""
        for mid, m in self.catalogo.items():
            with self.subTest(medida=mid):
                self.assertEqual(Medida.de_datos(m.a_datos()).a_datos(), m.a_datos())

    def test_ninguna_medida_escrita_como_macro_perdio_su_defensa_ni_su_alcance(self) -> None:
        for mid, m in self.catalogo.items():
            with self.subTest(medida=mid):
                self.assertTrue(m.porque.strip())
                self.assertIn("NO ", m.alcance)


if __name__ == "__main__":
    unittest.main()
