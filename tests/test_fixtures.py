"""Contrato fail-closed y proyecciones de los fixtures diferenciales."""

from __future__ import annotations

import copy
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace

from nucleo.diferencial import ALGORITMO_HUELLA, ESQUEMA_DIFERENCIAL
from nucleo.fixtures import (SIN_EVIDENCIA_EN_FIXTURE, Fixture, _id_escenario_valido,
                             _validar_comunes, _validar_dominio, _validar_evidencia,
                             _validar_grupos, casos_para_mutacion, mismo_veredicto, ok_guardado,
                             referentes_de_fixture, registro_de_veredicto, valor_comparable,
                             validar_fixture)
from nucleo.medida import Medida
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


class VeredictoGuardadoTests(unittest.TestCase):
    """La forma larga de un veredicto: además del `ok`, con qué valor salió y si levantó."""

    def _con(self, guardado_verde, guardado_rojo):
        datos = _dominio()
        datos["escenarios"][0]["oracle_al_generar"]["por_medida"]["prueba.mide"] = guardado_verde
        datos["escenarios"][1]["oracle_al_generar"]["por_medida"]["prueba.mide"] = guardado_rojo
        return _validar_dominio(datos, "demo.json")

    def test_las_dos_formas_valen_y_conviven(self) -> None:
        """La corta es la que emitieron los fixtures hasta 0.23.0 y la que siguen emitiendo los
        consumidores: exigirles la larga los invalidaría a todos de golpe."""
        self.assertEqual(self._con(True, False), [])
        self.assertEqual(self._con({"ok": True, "valor": 0}, {"ok": False, "valor": 2}), [])
        self.assertEqual(self._con(True, {"ok": False, "levanta": True}), [])
        self.assertEqual(
            self._con({"ok": True, "valor": 0}, {"ok": False, "valor": SIN_EVIDENCIA_EN_FIXTURE}),
            [])

    def test_cada_forma_incoherente_se_rechaza(self) -> None:
        casos = {
            "no es booleano ni mapa": ("verde", "booleano o un mapa"),
            "ok que no es booleano": ({"ok": "si"}, "`ok` debe ser booleano"),
            "levanta en verde": ({"ok": True, "levanta": True}, "`levanta` con `ok`"),
            "levanta con valor": ({"ok": False, "levanta": True, "valor": 1},
                                  "`levanta` no lleva `valor`"),
            "levanta que no es booleano": ({"ok": False, "levanta": "si"},
                                           "`levanta` debe ser booleano"),
            "valor que no es número": ({"ok": False, "valor": "dos"}, "`valor` debe ser"),
            "valor booleano": ({"ok": False, "valor": True}, "`valor` debe ser"),
            "sin evidencia en verde": ({"ok": True, "valor": SIN_EVIDENCIA_EN_FIXTURE},
                                       "nunca sale en verde"),
            "campo de más": ({"ok": False, "valor": 1, "testigos": []}, "campos desconocidos"),
        }
        for nombre, (guardado, esperado) in casos.items():
            with self.subTest(nombre):
                fallas = self._con(True, guardado)
                self.assertTrue(any(esperado in falla for falla in fallas), fallas)

    def test_un_veredicto_ilegible_no_tapa_el_resto_de_las_comprobaciones(self) -> None:
        """La evidencia del escenario se sigue validando: un veredicto mal escrito no puede
        comprarse el resto del contrato."""
        datos = _dominio()
        datos["escenarios"][1]["oracle_al_generar"]["por_medida"]["prueba.mide"] = {"ok": "no"}
        datos["escenarios"][1]["evidencia"] = {"hecho": [{"id": "h", "ok": {"anidado": 1}}]}
        fallas = _validar_dominio(datos, "demo.json")
        self.assertTrue(any("`ok` debe ser booleano" in f for f in fallas))
        self.assertTrue(any("no es escalar" in f for f in fallas))

    def test_ok_guardado_lee_las_dos_formas(self) -> None:
        self.assertIs(ok_guardado(True), True)
        self.assertIs(ok_guardado({"ok": False, "levanta": True}), False)
        self.assertIsNone(ok_guardado({"ok": "si"}))
        self.assertIsNone(ok_guardado("verde"))

    def test_mismo_veredicto_no_le_reclama_a_un_fixture_viejo_lo_que_no_declaro(self) -> None:
        self.assertTrue(mismo_veredicto(False, {"ok": False, "valor": 3}))
        self.assertTrue(mismo_veredicto(False, {"ok": False, "levanta": True}))
        self.assertFalse(mismo_veredicto(True, {"ok": False, "valor": 3}))

    def test_mismo_veredicto_ve_lo_que_el_ok_no_distingue(self) -> None:
        """Un rojo que pasa a SIN EVIDENCIA, o a un error, es un cambio de veredicto aunque el
        booleano no se mueva: es justo lo que la forma corta no podía decir."""
        rojo = {"ok": False, "valor": 3}
        self.assertFalse(mismo_veredicto(rojo, {"ok": False, "valor": SIN_EVIDENCIA_EN_FIXTURE}))
        self.assertFalse(mismo_veredicto(rojo, {"ok": False, "levanta": True}))
        self.assertFalse(mismo_veredicto(rojo, {"ok": False, "valor": 4}))
        self.assertTrue(mismo_veredicto(rojo, {"ok": False, "valor": 3}))
        # `assertIs` y no `assertFalse`: devolver None también es falso, y ahí el mutante vive.
        self.assertIs(mismo_veredicto("verde", {"ok": True, "valor": 0}), False)


class RegistroDeVeredictoTests(unittest.TestCase):
    """Lo que el emisor escribe y el verificador recalcula, que es una sola función a propósito."""

    @staticmethod
    def _medida(requiere=None):
        datos = ["medida", "d.mide",
                 ["desde", ["de", "m", "x"], ["donde", ["==", ["campo", "x", "estado"], "vivo"]]],
                 ["resumen", "contar", 1],
                 ["umbral", "<=", 0, "razón"]]
        if requiere:
            datos.append(requiere)
        datos.append(["alcance", "NO ve"])
        return Medida.de_datos(datos)

    def test_verde_y_rojo_guardan_el_valor(self) -> None:
        medida = self._medida()
        self.assertEqual(registro_de_veredicto(medida, {"m": [{"estado": "muerto"}]}),
                         {"ok": True, "valor": 0})
        self.assertEqual(registro_de_veredicto(medida, {"m": [{"estado": "vivo"}]}),
                         {"ok": False, "valor": 1})

    def test_sin_evidencia_no_se_confunde_con_un_rojo(self) -> None:
        medida = self._medida(["requiere", ["filas", "m", "y", ["==", ["campo", "y", "tipo"], "codigo"]]])
        self.assertEqual(registro_de_veredicto(medida, {"m": [{"estado": "vivo", "tipo": "medida"}]}),
                         {"ok": False, "valor": SIN_EVIDENCIA_EN_FIXTURE})

    def test_una_evaluacion_que_levanta_queda_anotada_sin_su_mensaje(self) -> None:
        """El mensaje no entra: dos implementaciones independientes redactan distinto, y compararlo
        volvería contrato a la redacción."""
        medida = self._medida()
        self.assertEqual(registro_de_veredicto(medida, {"m": [{"otra_cosa": 1}]}),
                         {"ok": False, "levanta": True})

    def test_un_entero_flotante_y_uno_entero_son_el_mismo_numero(self) -> None:
        self.assertEqual(valor_comparable(3.0), 3)
        self.assertEqual(valor_comparable(3.5), 3.5)
        self.assertEqual(valor_comparable(SIN_EVIDENCIA_EN_FIXTURE), SIN_EVIDENCIA_EN_FIXTURE)


class MedidasDeclaradasTests(unittest.TestCase):
    """Un fixture puede traer escritas las medidas que no están en ningún catálogo."""

    def _con(self, declaradas):
        datos = _dominio()
        datos["medidas_declaradas"] = declaradas
        return _validar_dominio(datos, "demo.json")

    CANONICA = ["medida", "prueba.mide", ["desde", ["de", "hecho", "h"]],
                ["resumen", "contar", 1], ["umbral", "<=", 0, "razón"], ["alcance", "NO ve"]]

    def test_una_declaracion_bien_formada_vale(self) -> None:
        self.assertEqual(self._con({"prueba.mide": self.CANONICA}), [])

    def test_ningun_fixture_esta_obligado_a_declarar(self) -> None:
        self.assertEqual(_validar_dominio(_dominio(), "demo.json"), [])

    def test_cada_forma_invalida_se_rechaza(self) -> None:
        casos = {
            "mapa vacío": {},
            "no es un mapa": [self.CANONICA],
            "id que no está en medidas": {"otra.medida": [*self.CANONICA[:1], "otra.medida",
                                                          *self.CANONICA[2:]]},
            "no es la forma canónica": {"prueba.mide": {"id": "prueba.mide"}},
            "id que no coincide": {"prueba.mide": [*self.CANONICA[:1], "otra.medida",
                                                   *self.CANONICA[2:]]},
            "canónica corta": {"prueba.mide": ["medida", "prueba.mide"]},
        }
        for nombre, declaradas in casos.items():
            with self.subTest(nombre):
                self.assertTrue(self._con(declaradas))


class ElFixtureRealEjercitaElAlgebraTests(unittest.TestCase):
    """Sobre el archivo versionado: el agujero que cerró la tarea del diferencial era que ninguna
    de sus medidas usaba lo que el álgebra 0.7 agregó, así que la referencia nunca pasaba por ahí."""

    @classmethod
    def setUpClass(cls) -> None:
        import json

        raiz = Path(__file__).resolve().parents[1]
        cls.datos = json.loads(
            (raiz / "diferencial" / "simulacion.json").read_text(encoding="utf-8"))

    def test_alguna_medida_pide_filas_con_condicion(self) -> None:
        requieren = [canonica for canonica in self.datos.get("medidas_declaradas", {}).values()
                     for nodo in canonica
                     if isinstance(nodo, list) and nodo and nodo[0] == "requiere"
                     for entrada in nodo[1:]
                     if isinstance(entrada, list) and entrada[0] == "filas"]
        self.assertTrue(requieren, "ninguna medida del fixture usa `requiere` con condición")

    def test_hay_escenarios_con_sin_evidencia_y_con_error(self) -> None:
        registros = [r for e in self.datos["escenarios"]
                     for r in e["oracle_al_generar"]["por_medida"].values()]
        self.assertTrue(any(isinstance(r, dict) and r.get("valor") == SIN_EVIDENCIA_EN_FIXTURE
                            for r in registros))
        self.assertTrue(any(isinstance(r, dict) and r.get("levanta") for r in registros))

    def test_una_relacion_con_variantes_mezcla_sus_dos_formas(self) -> None:
        """La variante `medida` de `mutante` no trae `estado`, y la de `codigo` sí: es el mundo que
        distingue evaluar todas las filas de cortar en la primera que cumple."""
        mezclados = [e["id"] for e in self.datos["escenarios"]
                     if len({fila.get("tipo") for fila in e["evidencia"].get("mutante", [])}) > 1]
        self.assertTrue(mezclados)


if __name__ == "__main__":
    unittest.main()
