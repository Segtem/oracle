"""Contrato fail-closed y proyecciones de los fixtures diferenciales."""

from __future__ import annotations

import copy
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace

from nucleo.diferencial import ALGORITMO_HUELLA, ESQUEMA_DIFERENCIAL
from nucleo.fixtures import (Fixture, _id_escenario_valido, _validar_comunes,
                             _validar_dominio, _validar_evidencia, _validar_grupos,
                             casos_para_mutacion, validar_fixture)


def _evidencia(ok=True):
    return {"hecho": [{"id": "h", "ok": ok}]}


def _frescura():
    return {
        "algoritmo": ALGORITMO_HUELLA,
        "raiz_fuentes": ".",
        "fuentes": {"emisor": ["tools/emisor.py"], "referencia": ["referencia.py"]},
        "configuracion": {"repeticiones": 1},
        "huellas": {nombre: "a" * 64 for nombre in
                     ("emisor", "referencia", "catalogo", "configuracion")},
    }


def _dominio():
    return {
        "esquema": ESQUEMA_DIFERENCIAL,
        "origen": "referencia independiente",
        "medidas": ["prueba.mide"],
        "mundos": 2,
        "escenarios": [
            {"id": "verde", "evidencia": _evidencia(True), "referencia_ok": True,
             "oracle_al_generar": {
                 "global_ok": True, "por_medida": {"prueba.mide": True}}},
            {"id": "rojo", "evidencia": _evidencia(False), "referencia_ok": False,
             "oracle_al_generar": {
                 "global_ok": False, "por_medida": {"prueba.mide": False}}},
        ],
        "frescura": _frescura(),
    }


def _grupos():
    return {
        "esquema": ESQUEMA_DIFERENCIAL,
        "origen": "referencia independiente",
        "mundos": 2,
        "grupos": {"prueba.mide": [
            {"evidencia": _evidencia(True), "esperado_ok": True},
            {"evidencia": _evidencia(False), "esperado_ok": False},
        ]},
        "frescura": _frescura(),
    }


class FixturesTests(unittest.TestCase):
    def test_fixture_es_inmutable(self) -> None:
        fixture = Fixture(Path("demo.json"), _dominio())
        with self.assertRaises(FrozenInstanceError):
            fixture.ruta = Path("otro.json")

    def test_id_de_escenario_exige_texto_no_vacio_y_sin_espacios(self) -> None:
        self.assertTrue(_id_escenario_valido("caso-01"))
        for invalido in (1, "", "con espacio", "\ttabulado"):
            with self.subTest(invalido=invalido):
                self.assertFalse(_id_escenario_valido(invalido))

    def test_evidencia_rechaza_cada_nivel_mal_tipado(self) -> None:
        invalidas = (
            ["no es mapa"],
            {},
            {1: []},
            {"": []},
            {"hecho": ()},
            {"hecho": [1]},
            {"hecho": [{1: "valor"}]},
            {"hecho": [{"campo": ["no", "es", "escalar"]}]},
        )
        for evidencia in invalidas:
            with self.subTest(evidencia=evidencia):
                self.assertTrue(_validar_evidencia(evidencia, "caso"))
        self.assertEqual(_validar_evidencia({"hecho": []}, "caso"), [])

    def test_envelope_comun_rechaza_tipos_bordes_y_rutas_no_confinadas(self) -> None:
        base = _grupos()
        cambios = []
        for campo, valor in (("origen", 1), ("origen", " "),
                             ("mundos", True), ("mundos", 0), ("mundos", None)):
            datos = copy.deepcopy(base)
            datos[campo] = valor
            cambios.append(datos)
        sin_mundos = copy.deepcopy(base)
        del sin_mundos["mundos"]
        cambios.append(sin_mundos)

        for fuentes in (
                {"emisor": ("emisor.py",), "referencia": ["referencia.py"]},
                {"emisor": [1], "referencia": ["referencia.py"]},
                {"emisor": ["/tmp/afuera.py"], "referencia": ["referencia.py"]},
                {"emisor": ["../afuera.py"], "referencia": ["referencia.py"]}):
            datos = copy.deepcopy(base)
            datos["frescura"]["fuentes"] = fuentes
            cambios.append(datos)

        huellas_lista = copy.deepcopy(base)
        huellas_lista["frescura"]["huellas"] = [
            "emisor", "referencia", "catalogo", "configuracion"]
        cambios.append(huellas_lista)
        huella_no_textual = copy.deepcopy(base)
        huella_no_textual["frescura"]["huellas"]["emisor"] = 1
        cambios.append(huella_no_textual)

        for datos in cambios:
            with self.subTest(datos=datos):
                self.assertTrue(_validar_comunes(datos, "demo.json"))

        uno = copy.deepcopy(base)
        uno["mundos"] = 1
        self.assertFalse(any("mundos" in falla for falla in _validar_comunes(uno, "demo.json")))

    def test_dominio_rechaza_colecciones_y_fotos_inconsistentes(self) -> None:
        invalidos = []
        for campo, valor in (("medidas", ("prueba.mide",)),
                             ("medidas", ["ID.Invalido"]),
                             ("medidas", ["prueba.mide", "prueba.mide"]),
                             ("escenarios", tuple(_dominio()["escenarios"]))):
            datos = _dominio()
            datos[campo] = valor
            invalidos.append(datos)

        no_global = _dominio()
        no_global["escenarios"][0]["oracle_al_generar"]["global_ok"] = False
        no_referencia = _dominio()
        no_referencia["escenarios"][0]["referencia_ok"] = False

        for datos in invalidos:
            with self.subTest(datos=datos):
                self.assertTrue(_validar_dominio(datos, "demo.json"))
        self.assertTrue(any("AND" in falla for falla in
                            _validar_dominio(no_global, "demo.json")))
        self.assertTrue(any("referencia" in falla for falla in
                            _validar_dominio(no_referencia, "demo.json")))
        self.assertEqual(_validar_dominio(_dominio(), "demo.json"), [])

    def test_grupos_rechaza_casos_no_listados_y_conserva_el_borde_de_mundos(self) -> None:
        base = _grupos()
        casos = base["grupos"]["prueba.mide"]
        invalidos = []
        for valor in (tuple(casos), []):
            datos = copy.deepcopy(base)
            datos["grupos"]["prueba.mide"] = valor
            invalidos.append(datos)
        for datos in invalidos:
            with self.subTest(datos=datos):
                self.assertTrue(_validar_grupos(datos, "demo.json"))
        self.assertEqual(_validar_grupos(base, "demo.json"), [])

    def test_envelope_invalido_no_se_interpreta_como_un_formato_de_dominio(self) -> None:
        self.assertEqual(
            validar_fixture([], "demo.json"),
            ["demo.json: la raíz del fixture debe ser un objeto JSON"])

        datos = _dominio()
        datos["esquema"] = "oracle.diferencial/v0"
        del datos["escenarios"]
        fallas = validar_fixture(datos, "demo.json")
        self.assertEqual(len(fallas), 1)
        self.assertIn("esquema", fallas[0])

    def test_casos_de_dominio_saltan_solo_medidas_ausentes_del_catalogo(self) -> None:
        fixture = Fixture(Path("demo.json"), _dominio())
        medida = SimpleNamespace(
            evaluar=lambda evidencia: SimpleNamespace(ok=evidencia["hecho"][0]["ok"]))

        casos = list(casos_para_mutacion(fixture, {"prueba.mide": medida}))
        self.assertEqual(len(casos), 2)
        self.assertEqual([caso["etiqueta"] for caso in casos],
                         ["verde_correcto", "falso_verde"])
        self.assertEqual(list(casos_para_mutacion(fixture, {})), [])


if __name__ == "__main__":
    unittest.main()
