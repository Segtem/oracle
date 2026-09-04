"""`oracle contexto` es una vista, no un documento: todo lo que dice sale de otra fuente."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from nucleo.proyecto import Proyecto  # noqa: E402
from nucleo.vocabulario import OPERADORES, ORIGENES_DE_UMBRAL  # noqa: E402
from tools import contexto  # noqa: E402


def _proyecto_vacio(td: str) -> Proyecto:
    raiz = Path(td)
    (raiz / "catalogos").mkdir()
    (raiz / "corpus").mkdir()
    (raiz / "oracle.json").write_text(
        json.dumps({"esquema": "oracle.proyecto/v1"}), encoding="utf-8")
    return Proyecto(raiz)


class ContieneLoQueHaceFaltaTests(unittest.TestCase):

    def setUp(self) -> None:
        self.propio = contexto.texto(Proyecto(RAIZ))

    def test_dice_lo_que_toda_medida_declara(self) -> None:
        """Es lo único que no se puede deducir mirando el proyecto: hay que saberlo de antemano."""
        for exigido in ("umbral", "segun", "alcance", "porque"):
            self.assertIn(exigido, self.propio)

    def test_los_origenes_del_umbral_salen_del_vocabulario(self) -> None:
        """No copiados: si mañana entra un quinto origen, aparece acá solo."""
        for origen in ORIGENES_DE_UMBRAL:
            self.assertIn(origen, self.propio)

    def test_los_operadores_salen_del_vocabulario(self) -> None:
        for operador in OPERADORES:
            self.assertIn(operador, self.propio)

    def test_las_relaciones_salen_de_la_evidencia_real(self) -> None:
        """Del mismo inventario que usa `oracle relaciones`, no de una lista escrita al lado."""
        from tools.medida import inventario_de_relaciones

        campos, _ = inventario_de_relaciones(Proyecto(RAIZ))
        self.assertTrue(campos, "el proyecto propio tiene que tener evidencia")
        for relacion in list(campos)[:5]:
            self.assertIn(relacion, self.propio)

    def test_nombra_las_medidas_que_ya_existen(self) -> None:
        """Para no proponer una que ya está. Sin esto, el que escribe no tiene cómo saberlo."""
        self.assertIn("meta.toda_medida_esta_fijada", self.propio)

    def test_dice_que_el_caso_va_antes_que_la_medida(self) -> None:
        """Es el error que ninguna validación automática atrapa: una medida escrita primero hace
        que el caso la describa en vez de probarla."""
        self.assertIn("CASO", self.propio)
        self.assertIn("antes", self.propio)


class ElCompactoDiceLoMismoConMenosTests(unittest.TestCase):

    def setUp(self) -> None:
        proy = Proyecto(RAIZ)
        self.normal = contexto.texto(proy)
        self.compacto = contexto.texto(proy, compacto=True)

    def test_ahorra_de_verdad(self) -> None:
        """El destinatario probable es un agente con una ventana de contexto. Si ahorrara poco, la
        bandera sería una complicación sin motivo."""
        self.assertLess(len(self.compacto) * 2, len(self.normal))

    def test_no_pierde_ninguna_relacion(self) -> None:
        """Apretar no es recortar: lo que se va son renglones en blanco y prosa, no información."""
        from tools.medida import inventario_de_relaciones

        campos, _ = inventario_de_relaciones(Proyecto(RAIZ))
        for relacion in campos:
            self.assertIn(relacion, self.compacto)

    def test_no_pierde_ninguna_medida(self) -> None:
        catalogo, falla = contexto._medidas(Proyecto(RAIZ))
        self.assertEqual(falla, "")
        for mid, _ in catalogo:
            self.assertIn(mid, self.compacto)

    def test_no_deja_renglones_vacios(self) -> None:
        self.assertNotIn("\n\n", self.compacto)


class UnProyectoSinNadaNoRompeTests(unittest.TestCase):
    """Un proyecto recién inicializado es el caso donde MÁS falta este comando, y es justo donde
    no hay evidencia ni medidas de las que derivar nada."""

    def test_sin_evidencia_lo_dice_en_vez_de_fallar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            salida = contexto.texto(_proyecto_vacio(td))
        self.assertIn("ninguna", salida)
        self.assertIn("umbral", salida)

    def test_sin_medidas_tambien(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            salida = contexto.texto(_proyecto_vacio(td))
        self.assertIn("0 MEDIDAS", salida.upper())


if __name__ == "__main__":
    unittest.main()


class ElContextoNoMienteCuandoNoPuedeLeerTests(unittest.TestCase):
    """Un cero por falla es indistinguible de un cero real, y quien lee esto no tiene con qué dudar.

    Medido el 2026-09-04: los dos consumidores conocidos tienen catálogo —41 y 9 medidas— y este
    texto decía «LAS 0 MEDIDAS QUE YA EXISTEN», porque un `except Exception: return []` se tragaba
    el fallo de cargar las escalares del proyecto. Sobre esa base, un agente escribe la primera
    medida de un catálogo que ya tiene cuarenta y una.
    """

    def _proyecto_con_escalares(self, td: str):
        raiz = Path(td)
        (raiz / "catalogos").mkdir()
        (raiz / "escalares.py").write_text(
            "# código del proyecto: ejecutarlo necesita autorización\n", encoding="utf-8")
        return Proyecto(raiz)

    def test_sin_autorizacion_dice_que_falta_y_no_cuenta_cero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy = self._proyecto_con_escalares(td)
            catalogo, falla = contexto._medidas(proy, confiar=False)

            self.assertEqual(catalogo, [])
            self.assertIn("--confiar-escalares", falla)

    def test_el_texto_no_afirma_un_numero_que_no_pudo_averiguar(self) -> None:
        """Lo que se lee es la afirmación, no el valor de retorno: es lo único que ve un agente."""
        with tempfile.TemporaryDirectory() as td:
            salida = contexto.texto(self._proyecto_con_escalares(td))

        self.assertIn("NO SE PUDIERON LEER", salida)
        self.assertNotIn("LAS 0 MEDIDAS QUE YA EXISTEN", salida)

    def test_un_catalogo_vacio_de_verdad_si_dice_cero(self) -> None:
        """El otro lado: sin escalares que autorizar, cero es cero y hay que decirlo."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            catalogo, falla = contexto._medidas(Proyecto(raiz))

            self.assertEqual(falla, "")
            self.assertEqual(catalogo, [])
            self.assertIn("LAS 0 MEDIDAS QUE YA EXISTEN", contexto.texto(Proyecto(raiz)))
