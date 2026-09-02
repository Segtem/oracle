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
                             casos_para_mutacion, referentes_de_fixture, validar_fixture)
from nucleo.referente import Referente, hechos_de_referentes


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


class ReferentesDeFixtureTests(unittest.TestCase):
    """L−2 deja de existir sólo en el lenguaje: el fixture declara lo que leyó, con su huella."""

    def test_una_declaracion_por_huella_con_lo_que_el_emisor_leyo(self) -> None:
        referentes = referentes_de_fixture(
            {"frescura": {"huellas": {"emisor": "aa" * 32, "catalogo": "bb" * 32}}})
        self.assertEqual(referentes,
                         [Referente("catalogo", "bb" * 32, "al generar"),
                          Referente("emisor", "aa" * 32, "al generar")])

    def test_van_ordenadas_y_no_en_el_orden_del_json(self) -> None:
        """Un orden que depende de cómo quedó escrito el archivo hace que la evidencia de un caso
        cambie sin que cambie nada de lo que se mide."""
        referentes = referentes_de_fixture(
            {"frescura": {"huellas": {"zeta": "1" * 8, "alfa": "2" * 8, "mu": "3" * 8}}})
        self.assertEqual([r.que for r in referentes], ["alfa", "mu", "zeta"])

    def test_el_cuando_dice_al_generar_y_no_ahora(self) -> None:
        """Lo que el fixture declara es lo que el emisor vio CUANDO lo generó. Decir «ahora» sería
        afirmar que sigue siendo cierto, que es justo lo que esta declaración no puede saber."""
        referentes = referentes_de_fixture({"frescura": {"huellas": {"x": "c" * 32}}})
        self.assertEqual(referentes[0].cuando, "al generar")

    def test_una_huella_vacia_llega_como_vacia_y_no_se_inventa(self) -> None:
        """El punto entero de `tiene_huella` es que la ausencia sea observable. Rellenarla acá con
        cualquier cosa dejaría a la medida sin nada que encontrar."""
        filas = hechos_de_referentes(
            referentes_de_fixture({"frescura": {"huellas": {"x": ""}}}))["referente_declarado"]
        self.assertEqual(filas[0]["tiene_huella"], False)

    def test_una_huella_que_no_es_texto_tampoco_se_inventa(self) -> None:
        filas = hechos_de_referentes(
            referentes_de_fixture({"frescura": {"huellas": {"x": None}}}))["referente_declarado"]
        self.assertEqual(filas[0]["huella"], "")
        self.assertEqual(filas[0]["tiene_huella"], False)

    def test_un_fixture_sin_frescura_no_declara_nada(self) -> None:
        """Devolver una lista vacía y no romper: hay fixtures sin bloque de frescura, y que no
        declaren referentes es distinto de declararlos mal."""
        self.assertEqual(referentes_de_fixture({}), [])
        self.assertEqual(referentes_de_fixture({"frescura": "no es un mapa"}), [])
        self.assertEqual(referentes_de_fixture({"frescura": {}}), [])
        self.assertEqual(referentes_de_fixture({"frescura": {"huellas": []}}), [])

    def test_el_fixture_real_del_repo_declara_sus_cuatro_fuentes(self) -> None:
        """Sobre el archivo de verdad: si mañana el fixture deja de declarar una fuente, el caso
        observado que fija esta medida queda hablando de un mundo que ya no existe."""
        import json

        raiz = Path(__file__).resolve().parents[1]
        datos = json.loads((raiz / "diferencial" / "simulacion.json").read_text(encoding="utf-8"))
        referentes = referentes_de_fixture(datos)
        self.assertEqual([r.que for r in referentes],
                         ["catalogo", "configuracion", "emisor", "referencia"])
        for r in referentes:
            self.assertEqual(len(r.huella), 64, r.que)


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

    def test_fila_malformada_con_clave_no_intenta_validar_unicidad(self) -> None:
        fallas = _validar_evidencia({"hecho": [["clave", ["id"]], 1]}, "caso")
        self.assertEqual(fallas, ["caso: hecho[0] no es una fila"])

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
