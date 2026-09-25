"""Los recorridos se pueden reproducir desde una carpeta vacía."""

import unittest

from tools import guia


class GuiaTests(unittest.TestCase):
    def test_bloques_y_salidas_reales(self):
        for ruta in guia.GUIAS:
            with self.subTest(guia=ruta.name):
                guia.verificar(guia=ruta)


class JuegoDeLaGuiaTests(unittest.TestCase):
    """Lo que el juego da por correcto tiene que ser lo que Oracle contesta."""

    @staticmethod
    def _categoria(salida: str) -> str:
        veredicto = [l for l in salida.splitlines() if l.startswith("VEREDICTO:")][-1]
        if veredicto.startswith(("VEREDICTO: VERDE", "VEREDICTO: verde")):
            return "VERDE"
        if "SIN MEDICIÓN" in veredicto:
            return "SIN MEDICIÓN"
        if "sin aplicar" in veredicto and "en rojo" not in veredicto:
            return "NO SE APLICARON"
        return "ROJO"

    def test_cada_prediccion_es_el_veredicto_de_su_salida(self):
        import json
        import re
        texto = (guia.RAIZ / "docs" / "de-cero.md").read_text(encoding="utf-8")
        patron = re.compile(r"<!-- juego (\{[^\n]*\}) -->\n\n```text salida\n(.*?)\n```", re.S)
        encontradas = patron.findall(texto)
        predicciones = [d for d in (json.loads(j) for j in re.findall(r"<!-- juego (\{.*\}) -->", texto))
                        if d["tipo"] == "predecir"]
        self.assertEqual(len(encontradas), len(predicciones), "toda predicción va justo antes de su salida")
        self.assertEqual(len({d["id"] for d in predicciones}), len(predicciones))
        for crudo, salida in encontradas:
            d = json.loads(crudo)
            with self.subTest(prediccion=d["id"]):
                self.assertIn(d["correcta"], d["opciones"])
                self.assertEqual(d["correcta"], self._categoria(salida))

    def test_cada_pregunta_cerrada_tiene_una_sola_respuesta(self):
        import json
        import re
        texto = (guia.RAIZ / "docs" / "de-cero.md").read_text(encoding="utf-8")
        for d in (json.loads(j) for j in re.findall(r"<!-- juego (\{.*\}) -->", texto)):
            if d["tipo"] == "elegir":
                with self.subTest(pregunta=d["id"]):
                    self.assertEqual(sum(o["ok"] for o in d["opciones"]), 1)
