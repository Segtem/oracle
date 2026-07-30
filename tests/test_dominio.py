"""Tests del dominio declarado — la pieza de «herramienta que crea herramientas».

Lo que importa: que se NIEGUE cuando el instrumento no discriminaría. Un generador de fixtures que
acepta cualquier cosa produce evidencia decorativa.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.diferencial import ESQUEMA_DIFERENCIAL, Procedencia, revisar_frescura
from nucleo.dominio import Dominio, DominioMalDeclarado, generar
from nucleo.medida import Medida

MEDIDA = Medida.de_datos(
    ["ninguno", "d.sin_fallas", "cosa", "c", ["==", ["campo", "c", "mal"], True],
     "una razón", "NO ve nada más"])
PROCEDENCIA = Procedencia(
    raiz=RAIZ,
    emisor=("tests/test_dominio.py",),
    referencia=("tests/test_dominio.py",),
)


def generar_prueba(dominio, medidas=(MEDIDA,)):
    return generar(dominio, medidas, procedencia=PROCEDENCIA)

# el «mundo»: una lista de cosas, alguna marcada como mal
def montar(defecto, i=0):
    return [{"id": "a", "mal": defecto == "una_mala"}]

def hechos(ctx):
    return {"cosa": ctx}

def referencia(ctx):
    return not any(c["mal"] for c in ctx)      # implementación independiente, trivial

def dominio_bueno():
    """Construir dentro del test evita que un mutante del contrato rompa el discovery del arnés."""
    return Dominio(nombre="d", montar=montar, hechos=hechos, referencia=referencia,
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
        fx = generar_prueba(dominio_bueno())
        self.assertEqual(fx["esquema"], ESQUEMA_DIFERENCIAL)
        self.assertEqual(fx["dominio"], "d")
        self.assertEqual(fx["medidas"], ["d.sin_fallas"])
        self.assertEqual([e["referencia_ok"] for e in fx["escenarios"]], [True, False])
        self.assertEqual(sorted(fx["escenarios"][0]),
                         ["defecto", "evidencia", "id", "oracle_al_generar", "referencia_ok"])
        self.assertEqual(
            fx["escenarios"][0]["oracle_al_generar"],
            {"global_ok": True, "por_medida": {"d.sin_fallas": True}})
        self.assertEqual(sorted(fx["frescura"]["huellas"]),
                         ["catalogo", "configuracion", "emisor", "referencia"])

    def test_NO_guarda_expectativa_por_medida(self) -> None:
        """Eso reimplementaba las medidas en Python: dos definiciones de lo mismo."""
        for esc in generar_prueba(dominio_bueno())["escenarios"]:
            self.assertNotIn("esperado_ok", esc)
            self.assertNotIn("espera", esc)

    def test_se_niega_si_el_sensor_y_la_referencia_no_coinciden(self) -> None:
        mentirosa = Dominio(nombre="d", montar=montar, hechos=hechos,
                            referencia=lambda ctx: True,      # dice ok siempre
                            defectos=("una_mala",))
        with self.assertRaises(DominioMalDeclarado) as e:
            generar_prueba(mentirosa)
        self.assertIn("no coinciden", str(e.exception))

    def test_se_niega_si_a_una_medida_le_falta_una_polaridad(self) -> None:
        sin_rojo = Dominio(nombre="d", montar=lambda d, i=0: [{"id": "a", "mal": False}],
                           hechos=hechos, referencia=referencia, defectos=("no_hace_nada",))
        with self.assertRaises(DominioMalDeclarado) as e:
            generar_prueba(sin_rojo)
        self.assertIn("polaridades", str(e.exception))

    def test_la_repeticion_llega_como_segundo_argumento(self) -> None:
        vistos = []

        def montar_contando(defecto, i):
            vistos.append((defecto, i))
            return [{"id": "a", "mal": defecto == "una_mala"}]

        d = Dominio(nombre="d", montar=montar_contando, hechos=hechos, referencia=referencia,
                    defectos=("una_mala",), repeticiones=2)
        generar_prueba(d)
        self.assertEqual(vistos, [(None, 0), (None, 1), ("una_mala", 0), ("una_mala", 1)])

    def test_se_niega_sin_medidas(self) -> None:
        with self.assertRaises(DominioMalDeclarado):
            generar_prueba(dominio_bueno(), ())

    def test_generar_dos_veces_sin_cambios_es_identico(self) -> None:
        self.assertEqual(generar_prueba(dominio_bueno()), generar_prueba(dominio_bueno()))

    def test_cambiar_emisor_catalogo_o_configuracion_vence_el_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "emisor.py").write_text("VERSION = 1\n", encoding="utf-8")
            (raiz / "referencia.py").write_text("VERSION = 1\n", encoding="utf-8")
            procedencia = Procedencia(
                raiz=raiz, emisor=("emisor.py",), referencia=("referencia.py",))
            fixture = generar(dominio_bueno(), [MEDIDA], procedencia=procedencia)
            catalogo = {MEDIDA.id: MEDIDA}
            self.assertEqual(revisar_frescura(fixture, raiz, catalogo), [])

            (raiz / "emisor.py").write_text("VERSION = 2\n", encoding="utf-8")
            self.assertTrue(any("emisor" in p for p in
                                revisar_frescura(fixture, raiz, catalogo)))
            (raiz / "emisor.py").write_text("VERSION = 1\n", encoding="utf-8")

            cambiada = Medida.de_datos(
                ["ninguno", "d.sin_fallas", "cosa", "c",
                 ["==", ["campo", "c", "mal"], False], "una razón", "NO ve nada más"])
            self.assertTrue(any("catalogo" in p for p in revisar_frescura(
                fixture, raiz, {cambiada.id: cambiada})))

            fixture["frescura"]["configuracion"]["repeticiones"] = 99
            self.assertTrue(any("configuracion" in p for p in
                                revisar_frescura(fixture, raiz, catalogo)))
