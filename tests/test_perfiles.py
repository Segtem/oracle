"""Los supuestos de lenguaje se activan por proyecto y no contaminan el catálogo universal."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401,E402
from nucleo.medida import cargar_catalogo  # noqa: E402
from nucleo.proyecto import (Proyecto, ProyectoInvalido, catalogos_a_cargar,
                             catalogos_base_a_cargar)  # noqa: E402
from perfiles.python.marco import hechos_de_modulos  # noqa: E402


class PerfilesDeProyectoTests(unittest.TestCase):
    def _proyecto(self, raiz: Path, perfiles=None) -> Proyecto:
        (raiz / "catalogos").mkdir()
        if perfiles is not None:
            (raiz / "oracle.json").write_text(json.dumps({
                "esquema": "oracle.proyecto/v1", "perfiles": perfiles,
            }), encoding="utf-8")
        return Proyecto(raiz)

    def test_un_proyecto_sin_declaracion_recibe_solo_el_catalogo_universal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            proy = self._proyecto(Path(d))
            catalogo = cargar_catalogo(catalogos_a_cargar(proy))
            self.assertNotIn("proceso.arnes_con_bytecode_frio", catalogo)
            self.assertNotIn("proceso.modulo_alcanzable", catalogo)

    def test_el_perfil_python_se_carga_solo_si_el_proyecto_lo_declara(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            proy = self._proyecto(Path(d), ["python"])
            catalogo = cargar_catalogo(catalogos_a_cargar(proy))
            self.assertIn("proceso.arnes_con_bytecode_frio", catalogo)
            self.assertIn("proceso.modulo_alcanzable", catalogo)
            self.assertEqual(len(catalogos_base_a_cargar(proy)), 2)

    def test_un_perfil_desconocido_falla_cerrado(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            proy = self._proyecto(Path(d), ["lenguaje-inventado"])
            with self.assertRaisesRegex(ProyectoInvalido, "desconocidos"):
                catalogos_a_cargar(proy)

    def test_el_sensor_ast_tambien_se_importa_desde_el_perfil(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            paquete = raiz / "paquete"
            paquete.mkdir()
            (paquete / "__init__.py").write_text("from . import usado\n", encoding="utf-8")
            (paquete / "usado.py").write_text("X = 1\n", encoding="utf-8")
            hechos = hechos_de_modulos(raiz, ["paquete"], ["paquete"])
            self.assertEqual(hechos["importa"], [
                {"a": "paquete", "b": "paquete.usado", "es_test": False},
            ])
            self.assertEqual(hechos["alcanzable"], [
                {"desde": "paquete", "hasta": "paquete", "saltos": 0},
                {"desde": "paquete", "hasta": "paquete.usado", "saltos": 1},
            ])


if __name__ == "__main__":
    unittest.main()
