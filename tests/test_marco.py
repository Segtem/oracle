"""Política explícita de uso y fijación de las medidas."""

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.marco import hechos_de_casos, hechos_de_uso  # noqa: E402
from nucleo.medida import cargar  # noqa: E402


MID = "dominio.ordinaria"
CATALOGO = {MID: object()}


def setUpModule() -> None:
    """Registra las escalares del catálogo base DENTRO de la suite, no al importar el módulo.

    Como `import catalogos.escalares` al tope, el decorador `@escalar` corría durante el
    descubrimiento: un mutante en `escalar()`, `_registro()` o `_contrato_de_escalar()` rompía la
    importación del archivo de test y el arnés lo reportaba como «error» en vez de «muerte». Once
    mutantes de `nucleo/algebra.py` quedaban sin veredicto por esto. Acá el fallo es del test.
    """
    importlib.import_module("catalogos.escalares")


def _fijada():
    """Se carga DENTRO del test, nunca al importar el módulo.

    Cuando esto era `FIJADA = cargar(...)` a nivel de módulo, leer una medida real —con su expansión
    de macros y su validación de álgebra— ocurría durante el **descubrimiento** de la suite. Un
    mutante que rompiera cualquier función de ese camino hacía fallar la importación del módulo de
    test, y el arnés lo reportaba como «error» en vez de «muerte».

    Lo grave no era perder esas muertes: era que el veredicto dependía de **cómo se particionara la
    ronda**. Mutando `nucleo/macro.py` sola daba 80/80; la misma mutación dentro de la ronda completa
    daba 63 errores de arnés, porque ahí `tests.test_marco` entraba en la carga prioritaria. Un
    resultado que cambia según cómo se corta la corrida no es una medición.
    """
    return cargar(RAIZ / "catalogos" / "meta" / "meta.toda_medida_esta_fijada.json")


class _MedidaFalsa:
    """Stub mínimo: sólo lo que `hechos_de_casos` le pide a una medida real."""

    def __init__(self, ok: bool) -> None:
        self._ok = ok

    def evaluar(self, evidencia: dict) -> SimpleNamespace:
        return SimpleNamespace(ok=self._ok)


class HechosDeCasosTests(unittest.TestCase):
    def test_esperado_ok_compara_la_etiqueta_no_el_resultado(self) -> None:
        """Cuando la medida SÍ existe, `esperado_ok` tiene que salir de la etiqueta del caso —
        no del resultado de la medida, que es independiente y viene fijo en `True` acá."""
        catalogo = {"dominio.existe": _MedidaFalsa(True)}
        casos = [
            {"id": "coincide", "medida": "dominio.existe", "etiqueta": "verde_correcto",
             "evidencia": {}},
            {"id": "no_coincide", "medida": "dominio.existe", "etiqueta": "falso_verde",
             "evidencia": {}},
        ]
        filas = {f["id"]: f for f in hechos_de_casos(catalogo, casos)["caso"]}

        self.assertTrue(filas["coincide"]["esperado_ok"])
        self.assertTrue(filas["coincide"]["dio_ok"])
        self.assertFalse(filas["no_coincide"]["esperado_ok"])
        self.assertTrue(filas["no_coincide"]["dio_ok"])

    def test_distingue_sin_medida_id_desconocido_y_estado_del_hueco(self) -> None:
        casos = [
            {"id": "abierto", "medida": None, "etiqueta": "falso_verde",
             "estado_sin_medida": "abierto", "sin_medida_todavia": "falta una regla"},
            {"id": "desconocido", "medida": "dominio.no_existe",
             "etiqueta": "falso_verde"},
            {"id": "resuelto", "medida": None, "etiqueta": "deuda_de_diseño",
             "estado_sin_medida": "resuelto", "resuelto": "cerrado"},
        ]
        filas = {f["id"]: f for f in hechos_de_casos({}, casos)["caso"]}

        self.assertEqual(filas["abierto"]["medida"], "")
        self.assertFalse(filas["abierto"]["tiene_medida"])
        self.assertFalse(filas["abierto"]["medida_existe"])
        self.assertTrue(filas["abierto"]["es_hueco_abierto"])
        self.assertTrue(filas["abierto"]["explica_el_hueco"])

        self.assertTrue(filas["desconocido"]["tiene_medida"])
        self.assertFalse(filas["desconocido"]["medida_existe"])
        self.assertFalse(filas["desconocido"]["es_hueco_abierto"])
        self.assertFalse(filas["resuelto"]["es_hueco_abierto"])


class TodaMedidaEstaFijadaTests(unittest.TestCase):
    def _evaluar(self, mutantes=(), casos=None, **politica):
        # Un caso por omisión: la obligación de tener mutantes nace de que ALGÚN caso declare la
        # medida, porque es ahí donde la mutación puede correr y significar algo.
        casos = [{"medida": MID}] if casos is None else casos
        evidencia = hechos_de_uso(CATALOGO, casos, list(mutantes), **politica)
        return evidencia["medida_en_uso"][0], _fijada().evaluar(evidencia)

    def test_una_medida_ordinaria_con_CERO_mutantes_no_pasa_vacuamente(self) -> None:
        uso, veredicto = self._evaluar()
        self.assertFalse(uso["es_heredada"])
        self.assertEqual(uso["casos_que_la_evaluan"], 1)
        self.assertTrue(uso["debe_tener_mutantes"])
        self.assertFalse(veredicto.ok)

    def test_sin_ningun_caso_la_obligacion_no_nace_y_de_eso_se_ocupa_otra_medida(self) -> None:
        """Antes la exención salía del prefijo `meta.` del id; ahora sale de una propiedad
        comprobable. Una medida que ningún caso declara no puede mutarse, así que exigirle mutantes
        sería un falso rojo — de que nadie la ejercite se ocupa `meta.toda_medida_esta_ejercitada`,
        y las dos preguntas quedan separadas en vez de resueltas por una convención de nombre."""
        uso, veredicto = self._evaluar(casos=[])
        self.assertEqual(uso["casos_que_la_evaluan"], 0)
        self.assertFalse(uso["debe_tener_mutantes"])
        self.assertTrue(veredicto.ok)

    def test_estar_evaluada_aparte_no_exime_de_tener_mutantes(self) -> None:
        """El agujero que cerró esto: las dos cosas iban juntas, así que una medida evaluada por
        otro arnés salía del denominador aunque tuviera casos de corpus para mutar."""
        uso, veredicto = self._evaluar(evaluadas_aparte={MID})
        self.assertEqual(uso["casos_que_la_evaluan"], 2)   # el caso más el crédito del otro arnés
        self.assertTrue(uso["debe_tener_mutantes"])
        self.assertFalse(veredicto.ok)

    def test_un_caso_que_reclama_la_medida_la_cuenta_exactamente_una_vez(self) -> None:
        evidencia = hechos_de_uso(CATALOGO, [{"medida": MID}], [])
        self.assertEqual(evidencia["medida_en_uso"][0]["casos_que_la_evaluan"], 1)

    def test_una_medida_con_un_mutante_vivo_no_esta_fijada(self) -> None:
        uso, veredicto = self._evaluar(
            [{"apunta_a": MID, "detecciones_conductuales": 0, "rechazos_del_algebra": 0}])
        self.assertEqual((uso["mutantes"], uso["mutantes_vivos"]), (1, 1))
        self.assertFalse(veredicto.ok)

    def test_una_medida_con_todos_sus_mutantes_muertos_esta_fijada(self) -> None:
        uso, veredicto = self._evaluar([
            {"apunta_a": MID, "detecciones_conductuales": 3, "rechazos_del_algebra": 0},
            # el rechazo del álgebra tampoco lo deja vivo: nadie lo notó es CERO de las dos formas
            {"apunta_a": MID, "detecciones_conductuales": 0, "rechazos_del_algebra": 1},
        ])
        self.assertEqual((uso["mutantes"], uso["mutantes_vivos"]), (2, 0))
        self.assertTrue(veredicto.ok)

    def test_una_medida_heredada_declara_que_no_debe_mutarse_en_esta_ronda(self) -> None:
        uso, veredicto = self._evaluar(heredadas={MID})
        self.assertTrue(uso["es_heredada"])
        self.assertFalse(uso["debe_tener_mutantes"])
        self.assertTrue(veredicto.ok)

    def test_evaluada_aparte_acredita_ejercicio_y_nada_mas(self) -> None:
        """Lo único que queda de la exención vieja: que otro arnés la evalúe la cuenta como
        ejercitada. Ya no la saca del denominador de mutación — para eso está el test de arriba."""
        uso, veredicto = self._evaluar(casos=[], evaluadas_aparte={MID})
        self.assertEqual(uso["casos_que_la_evaluan"], 1)   # el crédito, sin ningún caso propio
        self.assertFalse(uso["debe_tener_mutantes"])       # y sin casos no hay nada que mutar
        self.assertTrue(veredicto.ok)

    def test_un_mutante_sin_conteos_enteros_no_puede_contarse(self) -> None:
        sano = {"detecciones_conductuales": 1, "rechazos_del_algebra": 0}
        for mutante in ({"apunta_a": MID},
                        {"apunta_a": MID, **sano, "detecciones_conductuales": "si"},
                        {"apunta_a": MID, **sano, "rechazos_del_algebra": -1},
                        {"apunta_a": MID, "detecciones_conductuales": 1},
                        {"apunta_a": "otra.medida", **sano}, None):
            with self.subTest(mutante=mutante):
                with self.assertRaises(ValueError):
                    hechos_de_uso(CATALOGO, [], [mutante])


if __name__ == "__main__":
    unittest.main()
