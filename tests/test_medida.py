"""Contratos pequeños de medida, cargados sin importar el módulo durante descubrimiento.

Esto es intencional: si una mutación rompe la construcción de la clasificación base, la excepción
ocurre dentro de un test y demuestra discriminación; no se confunde con un runner roto.
"""

from __future__ import annotations

import importlib
import json
import unittest
from dataclasses import FrozenInstanceError
from types import SimpleNamespace


def modulo_medida():
    return importlib.import_module("nucleo.medida")


class ContratoMedidaTests(unittest.TestCase):
    def test_clasificacion_meta_valida_forma_y_contenido(self) -> None:
        m = modulo_medida()
        base = m.ClasificacionMeta()
        self.assertEqual(base.relaciones_del_lenguaje,
                         frozenset({"medida", "caso", "medida_en_uso"}))
        self.assertEqual(base.prefijos_meta, ("meta.",))

        invalidas = (
            {"relaciones_del_lenguaje": {"medida"}},
            {"relaciones_del_lenguaje": frozenset({1})},
            {"relaciones_del_lenguaje": frozenset({""})},
            {"prefijos_meta": ["meta."]},
            {"prefijos_meta": ()},
            {"prefijos_meta": (1,)},
            {"prefijos_meta": ("",)},
        )
        for kwargs in invalidas:
            with self.subTest(kwargs=kwargs), self.assertRaises(m.MedidaMalDeclarada):
                m.ClasificacionMeta(**kwargs)

    def test_los_cuatro_datos_publicos_son_inmutables(self) -> None:
        m = modulo_medida()
        objetos_y_campo = (
            (m.ClasificacionMeta(), "prefijos_meta"),
            (m.Veredicto("d.m", 0, True, "<= 0", "razón", "alcance", ()), "ok"),
            (m.Medida("d.m", [], [], "<=", 0, "razón", "alcance"), "limite"),
            (m.Informe(()), "veredictos"),
        )
        for objeto, campo in objetos_y_campo:
            with self.subTest(tipo=type(objeto).__name__), self.assertRaises(FrozenInstanceError):
                setattr(objeto, campo, None)

    def test_linea_roja_sin_testigos_no_inventa_una_flecha(self) -> None:
        m = modulo_medida()
        v = m.Veredicto("d.m", 1, False, "<= 0", "razón", "alcance", ())
        self.assertNotIn("→", v.linea())

    def test_exactamente_cuatro_testigos_muestra_tres_y_un_restante(self) -> None:
        m = modulo_medida()
        testigos = tuple({"x": {"id": str(i)}} for i in range(4))
        linea = m.Veredicto("d.m", 4, False, "<= 0", "razón", "alcance", testigos).linea()
        self.assertEqual(linea.count("x="), 3)
        self.assertIn("+1", linea)

    def test_json_del_informe_conserva_unicode_legible(self) -> None:
        m = modulo_medida()
        veredicto = m.Veredicto("dominio.señal", 0, True, "<= 0", "razón", "qué no ve", ())
        texto = m.Informe((veredicto,)).a_json()
        self.assertIn("señal", texto)
        self.assertNotIn("\\u00f1", texto)
        self.assertEqual(json.loads(texto)["medidas"][0]["id"], "dominio.señal")

    def test_relacion_vacia_directa_y_compuesta_se_derivan_sin_convenciones(self) -> None:
        m = modulo_medida()

        def medida(mid, tuberia):
            return SimpleNamespace(
                id=mid, tuberia=tuberia, op="<=", limite=0,
                porque="razón", alcance="qué no ve")

        casos = (
            (medida("d.vacia", ["desde"]), ""),
            (medida("d.directa", ["desde", ["de", "pieza", "p"]]), "pieza"),
            (medida("d.compuesta", [
                "desde",
                ["unir", ["de", "primera", "a"], ["de", "segunda", "b"], "producto"],
            ]), "primera"),
        )
        hechos = m.como_hechos([objeto for objeto, _esperada in casos])
        self.assertEqual([hecho["relacion"] for hecho in hechos],
                         [esperada for _objeto, esperada in casos])


if __name__ == "__main__":
    unittest.main()
