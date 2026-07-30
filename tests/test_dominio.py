"""Tests del dominio declarado — la pieza de «herramienta que crea herramientas».

Lo que importa: que se NIEGUE cuando el instrumento no discriminaría. Un generador de fixtures que
acepta cualquier cosa produce evidencia decorativa.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.dominio import Dominio, DominioMalDeclarado, generar
from nucleo.medida import Medida

MEDIDA = Medida.de_datos(
    ["ninguno", "d.sin_fallas", "cosa", "c", ["==", ["campo", "c", "mal"], True],
     "una razón", "NO ve nada más"])

# el «mundo»: una lista de cosas, alguna marcada como mal
def montar(defecto):
    return [{"id": "a", "mal": defecto == "una_mala"}]

def hechos(ctx):
    return {"cosa": ctx}

def referencia(ctx):
    return not any(c["mal"] for c in ctx)      # implementación independiente, trivial

BUENO = Dominio(nombre="d", montar=montar, hechos=hechos, referencia=referencia,
                defectos=("una_mala",), descripcion="prueba")


class DeclaracionTests(unittest.TestCase):
    def test_un_dominio_sin_defectos_no_se_declara(self) -> None:
        with self.assertRaises(DominioMalDeclarado) as e:
            Dominio(nombre="d", montar=montar, hechos=hechos, referencia=referencia)
        self.assertIn("evidencia roja", str(e.exception))

    def test_un_nombre_con_punto_no_pasa(self) -> None:
        with self.assertRaises(DominioMalDeclarado):
            Dominio(nombre="a.b", montar=montar, hechos=hechos, referencia=referencia,
                    defectos=("x",))


class GenerarTests(unittest.TestCase):
    def test_produce_un_fixture_con_los_hechos_y_el_veredicto_de_la_referencia(self) -> None:
        fx = generar(BUENO, [MEDIDA])
        self.assertEqual(fx["dominio"], "d")
        self.assertEqual(fx["medidas"], ["d.sin_fallas"])
        self.assertEqual([e["referencia_ok"] for e in fx["escenarios"]], [True, False])
        self.assertEqual(sorted(fx["escenarios"][0]),
                         ["defecto", "evidencia", "id", "referencia_ok"])

    def test_NO_guarda_expectativa_por_medida(self) -> None:
        """Eso reimplementaba las medidas en Python: dos definiciones de lo mismo."""
        for esc in generar(BUENO, [MEDIDA])["escenarios"]:
            self.assertNotIn("esperado_ok", esc)
            self.assertNotIn("espera", esc)

    def test_se_niega_si_el_sensor_y_la_referencia_no_coinciden(self) -> None:
        mentirosa = Dominio(nombre="d", montar=montar, hechos=hechos,
                            referencia=lambda ctx: True,      # dice ok siempre
                            defectos=("una_mala",))
        with self.assertRaises(DominioMalDeclarado) as e:
            generar(mentirosa, [MEDIDA])
        self.assertIn("no coinciden", str(e.exception))

    def test_se_niega_si_a_una_medida_le_falta_una_polaridad(self) -> None:
        sin_rojo = Dominio(nombre="d", montar=lambda d: [{"id": "a", "mal": False}],
                           hechos=hechos, referencia=referencia, defectos=("no_hace_nada",))
        with self.assertRaises(DominioMalDeclarado) as e:
            generar(sin_rojo, [MEDIDA])
        self.assertIn("polaridades", str(e.exception))

    def test_se_niega_sin_medidas(self) -> None:
        with self.assertRaises(DominioMalDeclarado):
            generar(BUENO, [])
