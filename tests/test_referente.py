"""Contratos para la declaración y reificación de referentes (Nivel L−2)."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from nucleo.referente import (Referente, ReferenteMalDeclarado, como_hechos,
                              hechos_de_referentes)


class ReferenteTests(unittest.TestCase):
    def _datos(self):
        return ["referente", "Content/Props/silla.uasset", "sha256:abc", "2026-08-27T09:14:00"]

    def test_la_declaracion_es_inmutable_y_vuelve_a_su_json_canonico(self) -> None:
        referente = Referente.de_datos(self._datos())
        self.assertEqual(referente.que, "Content/Props/silla.uasset")
        self.assertEqual(referente.huella, "sha256:abc")
        self.assertEqual(referente.cuando, "2026-08-27T09:14:00")
        self.assertEqual(referente.a_datos(), self._datos())
        with self.assertRaises(FrozenInstanceError):
            referente.que = "otro"  # type: ignore

    def test_rechaza_formas_y_tipos_mal_declarados(self) -> None:
        invalidas = (
            "no es lista",
            ["referente"],
            ["otro", "x", "h", "t"],
            ["referente", "x", "h"],
            ["referente", "x", "h", "t", "sobra"],
            ["referente", "", "h", "t"],
            ["referente", "   ", "h", "t"],
            ["referente", "x", 1, "t"],
            ["referente", "x", "h", None],
            ["referente", "x", "h", "   "],
        )
        for datos in invalidas:
            with self.subTest(datos=datos), self.assertRaises(ReferenteMalDeclarado):
                Referente.de_datos(datos)

    def test_una_huella_vacía_se_reifica_como_falta_de_huella(self) -> None:
        referente = Referente("asset", "", "ahora")
        hechos = hechos_de_referentes([referente])
        self.assertEqual(hechos, {"referente_declarado": [{
            "que": "asset", "huella": "", "cuando": "ahora", "tiene_huella": False,
        }]})

    def test_la_reificacion_conserva_el_conjunto_y_rechaza_entradas_ajenas(self) -> None:
        referentes = [Referente("a", "h-a", "t-a"), Referente("b", "h-b", "t-b")]
        hechos = hechos_de_referentes(referentes)
        self.assertEqual([fila["que"] for fila in hechos["referente_declarado"]], ["a", "b"])
        self.assertEqual(como_hechos(referentes), hechos)

        for invalido in (None, ["no es Referente"]):
            with self.subTest(invalido=invalido), self.assertRaises(ReferenteMalDeclarado):
                hechos_de_referentes(invalido)


if __name__ == "__main__":
    unittest.main()
