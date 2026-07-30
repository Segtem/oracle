"""Tests del sensor de mutación. Un sensor sin tests es evidencia sin garantía."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogos.escalares  # noqa: F401
from nucleo import mutacion
from nucleo.medida import Medida

BASE = ["medida", "d.prueba",
        ["desde", ["de", "cosa", "c"], ["donde", ["==", ["campo", "c", "mal"], True]]],
        ["resumen", "contar", 1],
        ["umbral", "<=", 0, "una razón"],
        ["alcance", "NO ve nada más"]]

# una fila que ofende y otra que no: es lo que permite que el filtro se pueda fijar
EV_ROJO = {"cosa": [{"id": "x", "mal": True}, {"id": "y", "mal": False}]}
EV_VERDE = {"cosa": [{"id": "y", "mal": False}, {"id": "z", "mal": False}]}

CASO_ROJO = {"id": "c-rojo", "etiqueta": "falso_verde", "medida": "d.prueba", "evidencia": EV_ROJO}
CASO_VERDE = {"id": "c-verde", "etiqueta": "verde_correcto", "medida": "d.prueba",
              "evidencia": EV_VERDE}


class MutadoresTests(unittest.TestCase):
    def test_todo_mutante_sigue_siendo_una_medida_valida(self) -> None:
        for nombre, datos in mutacion.mutantes(BASE):
            with self.subTest(mutador=nombre):
                Medida.de_datos(datos)   # no debe levantar

    def test_no_toca_la_medida_original(self) -> None:
        antes = str(BASE)
        mutacion.mutantes(BASE)
        self.assertEqual(str(BASE), antes)

    def test_aflojar_umbral_lo_vuelve_imposible_de_violar(self) -> None:
        d = mutacion.aflojar_umbral(BASE)
        self.assertEqual(d[4][2], mutacion.GRANDE)
        self.assertTrue(Medida.de_datos(d).evaluar(EV_ROJO).ok)

    def test_aflojar_umbral_no_aplica_a_igualdad(self) -> None:
        d = [*BASE[:4], ["umbral", "==", 0, "x"], BASE[5]]
        self.assertIsNone(mutacion.aflojar_umbral(d))

    def test_invertir_comparador(self) -> None:
        self.assertEqual(mutacion.invertir_comparador(BASE)[4][1], ">")

    def test_quitar_filtro_cuenta_la_relacion_entera(self) -> None:
        d = mutacion.quitar_filtro(BASE)
        self.assertEqual(Medida.de_datos(d).evaluar(EV_VERDE).valor, 2)

    def test_quitar_y_negar_filtro_no_aplican_sin_donde(self) -> None:
        d = [*BASE[:2], ["desde", ["de", "cosa", "c"]], *BASE[3:]]
        self.assertIsNone(mutacion.quitar_filtro(d))
        self.assertIsNone(mutacion.negar_filtro(d))

    def test_negar_filtro_invierte_el_predicado(self) -> None:
        d = mutacion.negar_filtro(BASE)
        self.assertEqual(Medida.de_datos(d).evaluar(EV_ROJO).valor, 1)   # la fila «y»


class CorrerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalogo = {"d.prueba": Medida.de_datos(BASE)}

    def test_produce_hechos_y_no_veredictos(self) -> None:
        ev = mutacion.correr(self.catalogo, [CASO_ROJO, CASO_VERDE])
        self.assertEqual(sorted(ev), ["corrida_mutacion", "deteccion", "mutante"])
        for fila in ev["mutante"]:
            self.assertEqual(sorted(fila),
                             ["apunta_a", "cambio", "casos_que_lo_detectan", "id", "murio"])

    def test_un_mutante_muere_si_ALGUN_caso_lo_detecta(self) -> None:
        ev = mutacion.correr(self.catalogo, [CASO_ROJO, CASO_VERDE])
        quitar = next(m for m in ev["mutante"] if m["cambio"] == "quitar_filtro")
        self.assertTrue(quitar["murio"])
        self.assertEqual(quitar["casos_que_lo_detectan"], 2)

    def test_quitar_el_filtro_se_detecta_por_los_TESTIGOS_no_por_el_veredicto(self) -> None:
        """En el caso rojo, contar sin filtro sigue dando >0: el veredicto no se mueve. Lo que
        cambia es QUIÉNES son los testigos, y el informe también es contrato."""
        ev = mutacion.correr(self.catalogo, [CASO_ROJO])
        d = next(x for x in ev["deteccion"] if x["mutante"].endswith("quitar_filtro"))
        self.assertTrue(d["invirtio"])
        self.assertEqual(d["como"], "cambio_los_testigos")

    def test_aflojar_el_umbral_se_detecta_por_el_VEREDICTO(self) -> None:
        ev = mutacion.correr(self.catalogo, [CASO_ROJO])
        d = next(x for x in ev["deteccion"] if x["mutante"].endswith("aflojar_umbral"))
        self.assertEqual(d["como"], "invirtio_el_veredicto")

    def test_aflojar_umbral_sigue_necesitando_un_caso_ROJO(self) -> None:
        """Aflojar un umbral no mueve un verde ni le cambia los testigos: hace falta un caso ROJO.
        Es al revés de lo que yo suponía cuando agregué los casos verdes."""
        solo_verde = mutacion.correr(self.catalogo, [CASO_VERDE])
        self.assertFalse(next(m for m in solo_verde["mutante"]
                              if m["cambio"] == "aflojar_umbral")["murio"])
        solo_rojo = mutacion.correr(self.catalogo, [CASO_ROJO])
        self.assertTrue(next(m for m in solo_rojo["mutante"]
                             if m["cambio"] == "aflojar_umbral")["murio"])

    def test_un_caso_que_no_esta_en_su_estado_esperado_se_saltea(self) -> None:
        # etiquetado verde pero su evidencia da rojo: no fija nada y no debe contaminar
        mentiroso = {**CASO_ROJO, "etiqueta": "verde_correcto", "id": "c-mal"}
        self.assertEqual(mutacion.correr(self.catalogo, [mentiroso])["deteccion"], [])

    def test_una_medida_que_no_esta_en_el_catalogo_se_ignora(self) -> None:
        ajeno = {**CASO_ROJO, "medida": "d.fantasma"}
        self.assertEqual(mutacion.correr(self.catalogo, [ajeno])["mutante"], [])

    def test_el_bytecode_frio_es_por_construccion(self) -> None:
        # no se toca ningún archivo: no hay .pyc que pueda quedar viejo
        ev = mutacion.correr(self.catalogo, [CASO_ROJO])
        self.assertTrue(ev["corrida_mutacion"][0]["bytecode_frio"])

    def test_un_mutante_que_revienta_cuenta_como_muerto_y_no_como_hallazgo(self) -> None:
        malo = [*BASE[:2],
                ["desde", ["de", "cosa", "c"], ["donde", ["==", ["campo", "c", "no_existe"], True]]],
                *BASE[3:]]
        catalogo = {"d.prueba": Medida.de_datos(BASE)}
        original = mutacion.MUTADORES["negar_filtro"]
        try:
            mutacion.MUTADORES["negar_filtro"] = lambda d: malo
            ev = mutacion.correr(catalogo, [CASO_ROJO])
            d = next(x for x in ev["deteccion"] if x["mutante"].endswith("negar_filtro"))
            self.assertTrue(d["invirtio"])
            self.assertTrue(d["como"].startswith("error:"))
        finally:
            mutacion.MUTADORES["negar_filtro"] = original


if __name__ == "__main__":
    unittest.main()
