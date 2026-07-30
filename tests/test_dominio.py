"""Tests del dominio declarado — la pieza de «herramienta que crea herramientas».

Lo que importa: que se NIEGUE cuando el instrumento no discriminaría. Un generador de fixtures que
acepta cualquier cosa produce evidencia decorativa.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import FrozenInstanceError
import math
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.diferencial import (ESQUEMA_DIFERENCIAL, Procedencia, ProcedenciaInvalida,
                                _resolver_entrada, huella_archivos, ids_de_medidas, json_canonico,
                                revisar_frescura)
from nucleo.dominio import Dominio, DominioMalDeclarado, generar
from nucleo.medida import Medida

MEDIDA = Medida.de_datos(
    ["ninguno", "d.sin_fallas", "cosa", "c", ["==", ["campo", "c", "mal"], True],
     "una razón", "NO ve nada más"])
def procedencia_buena():
    """Se construye dentro de cada prueba: un mutante del contrato debe fallar como test, no import."""
    return Procedencia(
        raiz=RAIZ,
        emisor=("tests/test_dominio.py",),
        referencia=("tests/test_dominio.py",),
    )


def generar_prueba(dominio, medidas=(MEDIDA,)):
    return generar(dominio, medidas, procedencia=procedencia_buena())

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
    def test_la_declaracion_es_inmutable(self) -> None:
        dominio = dominio_bueno()
        with self.assertRaises(FrozenInstanceError):
            dominio.nombre = "otro"

    def test_un_dominio_sin_defectos_no_se_declara(self) -> None:
        with self.assertRaises(DominioMalDeclarado) as e:
            Dominio(nombre="d", montar=montar, hechos=hechos, referencia=referencia)
        self.assertIn("evidencia roja", str(e.exception))

    def test_un_nombre_con_punto_no_pasa(self) -> None:
        with self.assertRaises(DominioMalDeclarado):
            Dominio(nombre="a.b", montar=montar, hechos=hechos, referencia=referencia,
                    defectos=("x",))


class ProcedenciaTests(unittest.TestCase):
    def test_la_procedencia_es_inmutable_y_exige_listas_de_rutas_cerradas(self) -> None:
        p = Procedencia(RAIZ, ("tests/test_dominio.py",), ("tests/test_dominio.py",))
        with self.assertRaises(FrozenInstanceError):
            p.desde_proyecto = ".."

        invalidas = (
            {"emisor": (), "referencia": ("x",)},
            {"emisor": ["x"], "referencia": ("x",)},
            {"emisor": ("",), "referencia": ("x",)},
            {"emisor": (7,), "referencia": ("x",)},
        )
        for campos in invalidas:
            with self.subTest(campos=campos):
                with self.assertRaises(ProcedenciaInvalida):
                    Procedencia(RAIZ, **campos)

        for desde in (7, "otro", "/tmp"):
            with self.subTest(desde=desde):
                with self.assertRaises(ProcedenciaInvalida):
                    Procedencia(RAIZ, ("x",), ("x",), desde_proyecto=desde)

    def test_json_canonico_fija_unicode_orden_separadores_y_no_finitos(self) -> None:
        self.assertEqual(json_canonico({"b": 1, "a": "á"}), b'{"a":"\xc3\xa1","b":1}')
        for invalido in (math.nan, math.inf, {"x"}):
            with self.subTest(invalido=invalido):
                with self.assertRaises(ProcedenciaInvalida):
                    json_canonico(invalido)

    def test_las_rutas_firmadas_no_escapan_ni_aceptan_vacios_o_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as fuera:
            raiz = Path(td)
            (raiz / "vacio").mkdir()
            (Path(fuera) / "fuente.py").write_text("X = 1\n", encoding="utf-8")
            (raiz / "enlace.py").symlink_to(Path(fuera) / "fuente.py")

            for entrada in (".", "../fuera", str(Path(fuera) / "fuente.py"),
                            "no-existe.py", "vacio", "enlace.py"):
                with self.subTest(entrada=entrada):
                    with self.assertRaises((ProcedenciaInvalida, OSError)):
                        huella_archivos(raiz, (entrada,))
            with self.assertRaisesRegex(ProcedenciaInvalida, "raíz de procedencia inválida"):
                huella_archivos(raiz / "raiz-inexistente", ("x.py",))

            for entrada in (".", "../fuera", str(Path(fuera) / "fuente.py")):
                with self.subTest(mensaje=entrada):
                    with self.assertRaisesRegex(ProcedenciaInvalida, "no confinada"):
                        _resolver_entrada(raiz, entrada)
            with self.assertRaisesRegex(ProcedenciaInvalida, "ruta de procedencia inválida"):
                _resolver_entrada(raiz, "no-existe.py")

    def test_cada_resolucion_fisica_es_estricta(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "fuente.py").write_text("X = 1\n", encoding="utf-8")
            original = Path.resolve
            estrictas = []

            def observar(ruta, *args, **kwargs):
                estrictas.append(kwargs.get("strict", args[0] if args else False))
                return original(ruta, *args, **kwargs)

            with mock.patch.object(Path, "resolve", observar):
                huella_archivos(raiz, ("fuente.py",))
            self.assertGreaterEqual(len(estrictas), 4)
            self.assertTrue(all(valor is True for valor in estrictas))

    def test_ids_distingue_escenarios_y_grupos(self) -> None:
        self.assertEqual(ids_de_medidas({"escenarios": [], "medidas": ["d.a"]}), ["d.a"])
        self.assertEqual(ids_de_medidas({"grupos": {"d.b": [], "d.a": []}}), ["d.b", "d.a"])


class GenerarTests(unittest.TestCase):
    def test_produce_un_fixture_con_los_hechos_y_el_veredicto_de_la_referencia(self) -> None:
        fx = generar_prueba(dominio_bueno())
        self.assertEqual(fx["esquema"], ESQUEMA_DIFERENCIAL)
        self.assertEqual(fx["dominio"], "d")
        self.assertEqual(fx["medidas"], ["d.sin_fallas"])
        self.assertEqual(fx["origen"], "prueba")
        self.assertEqual([e["id"] for e in fx["escenarios"]],
                         ["sin-defecto", "una_mala"])
        self.assertEqual([e["defecto"] for e in fx["escenarios"]], ["", "una_mala"])
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
        self.assertIn("d.sin_fallas", str(e.exception))

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
        self.assertEqual([e["id"] for e in generar_prueba(d)["escenarios"]],
                         ["sin-defecto·0", "sin-defecto·1", "una_mala·0", "una_mala·1"])

    def test_se_niega_sin_medidas(self) -> None:
        with self.assertRaises(DominioMalDeclarado):
            generar_prueba(dominio_bueno(), ())

    def test_generar_dos_veces_sin_cambios_es_identico(self) -> None:
        self.assertEqual(generar_prueba(dominio_bueno()), generar_prueba(dominio_bueno()))

    def test_un_dominio_sin_descripcion_publica_un_origen_informativo(self) -> None:
        d = Dominio(nombre="d", montar=montar, hechos=hechos, referencia=referencia,
                    defectos=("una_mala",))
        self.assertEqual(generar_prueba(d)["origen"], "dominio «d» vs su referencia")

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

            faltantes = revisar_frescura(fixture, raiz, {})
            self.assertEqual(len(faltantes), 1)
            self.assertIn("faltan medidas", faltantes[0])
            self.assertIn(MEDIDA.id, faltantes[0])

            anterior = fixture["frescura"]["huellas"]["emisor"]
            (raiz / "emisor.py").write_text("VERSION = 2\n", encoding="utf-8")
            nueva = huella_archivos(raiz, ("emisor.py",))
            problemas = revisar_frescura(fixture, raiz, catalogo)
            self.assertTrue(any("emisor" in p for p in problemas))
            self.assertIn(f"{anterior[:12]}… → {nueva[:12]}…", "\n".join(problemas))
            (raiz / "emisor.py").write_text("VERSION = 1\n", encoding="utf-8")

            cambiada = Medida.de_datos(
                ["ninguno", "d.sin_fallas", "cosa", "c",
                 ["==", ["campo", "c", "mal"], False], "una razón", "NO ve nada más"])
            self.assertTrue(any("catalogo" in p for p in revisar_frescura(
                fixture, raiz, {cambiada.id: cambiada})))

            fixture["frescura"]["configuracion"]["repeticiones"] = 99
            self.assertTrue(any("configuracion" in p for p in
                                revisar_frescura(fixture, raiz, catalogo)))
