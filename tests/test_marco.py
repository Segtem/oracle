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
from nucleo.medida import cargar, ruta_de_medida  # noqa: E402


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
    return cargar(ruta_de_medida("meta.toda_medida_esta_fijada", RAIZ / "catalogos", *sorted((RAIZ / "perfiles").glob("*/catalogos"))))


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

    def test_procedencia_ausente_se_expone_como_sin_declarar(self) -> None:
        catalogo = {"dominio.existe": _MedidaFalsa(True)}
        casos = [
            {"id": "declarado", "medida": "dominio.existe", "etiqueta": "verde_correcto",
             "procedencia": "observada", "evidencia": {}},
            {"id": "ausente", "medida": "dominio.existe", "etiqueta": "verde_correcto",
             "evidencia": {}},
        ]
        filas = {f["id"]: f for f in hechos_de_casos(catalogo, casos)["caso"]}

        self.assertEqual(filas["declarado"]["procedencia"], "observada")
        self.assertEqual(filas["ausente"]["procedencia"], "sin_declarar")

    def test_reifica_si_el_caso_es_heredado_y_que_biblioteca_lo_trajo(self) -> None:
        casos = [
            {"id": "propio", "etiqueta": "verde_correcto", "evidencia": {},
             "es_heredado": False, "biblioteca": ""},
            {"id": "ajeno", "etiqueta": "verde_correcto", "evidencia": {},
             "es_heredado": True, "biblioteca": "tercero.calidad"},
        ]
        filas = {f["id"]: f for f in hechos_de_casos({}, casos)["caso"]}

        self.assertFalse(filas["propio"]["es_heredado"])
        self.assertEqual(filas["propio"]["biblioteca"], "")
        self.assertTrue(filas["ajeno"]["es_heredado"])
        self.assertEqual(filas["ajeno"]["biblioteca"], "tercero.calidad")

    def test_un_caso_sin_origen_reificado_es_propio_por_compatibilidad(self) -> None:
        fila, = hechos_de_casos(
            {}, [{"id": "legado", "etiqueta": "verde_correcto", "evidencia": {}}]
        )["caso"]
        self.assertFalse(fila["es_heredado"])
        self.assertEqual(fila["biblioteca"], "")

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


class AlcanceDeCasosHeredadosTests(unittest.TestCase):
    def _medida(self, mid: str):
        return cargar(ruta_de_medida(mid, RAIZ / "catalogos"))

    def test_la_fijacion_mira_solo_casos_propios_y_lo_declara(self) -> None:
        medida = self._medida("meta.la_medida_no_se_fija_solo_con_evidencia_fabricada")
        evidencia = {"caso": [
            {"medida": "propia.regla", "tiene_medida": True,
             "procedencia": "observada", "es_heredado": False},
            {"medida": "ajena.regla", "tiene_medida": True,
             "procedencia": "construida", "es_heredado": True},
        ]}
        self.assertTrue(medida.evaluar(evidencia).ok)
        self.assertIn("sólo casos propios", medida.alcance)
        self.assertIn("es_heredado == false", medida.alcance)

    def test_la_explicacion_del_hueco_mira_solo_lo_propio_y_lo_declara(self) -> None:
        medida = self._medida("meta.el_hueco_declarado_explica_por_que")
        comun = {"tiene_medida": False, "es_hueco_abierto": True}
        evidencia = {"caso": [
            {**comun, "explica_el_hueco": True, "es_heredado": False},
            {**comun, "explica_el_hueco": False, "es_heredado": True},
        ]}
        self.assertTrue(medida.evaluar(evidencia).ok)
        self.assertIn("sólo casos propios", medida.alcance)
        self.assertIn("es_heredado == false", medida.alcance)

        evidencia["caso"][0]["explica_el_hueco"] = False
        self.assertFalse(medida.evaluar(evidencia).ok)

    def test_un_caso_heredado_con_medida_ausente_se_mira_y_el_alcance_dice_todo(self) -> None:
        medida = self._medida("meta.el_caso_reclama_una_medida_que_existe")
        evidencia = {"caso": [
            {"tiene_medida": True, "medida_existe": False, "es_heredado": True},
        ]}
        self.assertFalse(medida.evaluar(evidencia).ok)
        self.assertIn("todos los casos, propios y heredados", medida.alcance)

    def test_un_caso_heredado_que_difiere_se_mira_y_el_alcance_dice_todo(self) -> None:
        medida = self._medida("meta.el_caso_se_pone_como_debe")
        evidencia = {"caso": [
            {"esperado_ok": True, "dio_ok": False, "es_heredado": True},
        ]}
        self.assertFalse(medida.evaluar(evidencia).ok)
        self.assertIn("todos los casos, propios y heredados", medida.alcance)


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


class HechosDeSombra(unittest.TestCase):
    """La sombra apaga la CONSECUENCIA de un rojo, no la medición.

    Estos hechos existen para que apagar no salga gratis: son lo que le da a
    `catalogos/meta/` con qué juzgar la sombra misma.
    """

    def _entrada(self, mid, desde="", porque=""):
        from nucleo.proyecto import EnSombra
        return EnSombra(mid, desde, porque)

    def _fila(self, entradas, ok=None, catalogo=None, hoy=None):
        from datetime import date
        from nucleo.marco import hechos_de_sombra
        return hechos_de_sombra(entradas, ok or {}, catalogo or {},
                                hoy or date(2026, 9, 1))["sombra"]

    def test_cuenta_los_dias_desde_la_fecha_declarada(self) -> None:
        """«Lo tengo en sombra hace ocho meses» tiene que ser un número, no una sensación."""
        fila, = self._fila([self._entrada("m.a", "2026-01-01", "x")])
        self.assertEqual(fila["dias"], 243)
        self.assertTrue(fila["declara_desde"])
        self.assertTrue(fila["declara_porque"])

    def test_una_fecha_ausente_o_ilegible_da_menos_uno_y_no_revienta(self) -> None:
        """-1 no es un nulo disfrazado: el álgebra levanta error al comparar contra un ausente,
        y de la falta se ocupa otra medida mirando `declara_desde`."""
        for desde in ("", "ayer", "2026-13-45"):
            with self.subTest(desde=desde):
                fila, = self._fila([self._entrada("m.a", desde, "x")])
                self.assertEqual(fila["dias"], -1)
                self.assertFalse(fila["declara_desde"] and desde == "")

    def test_una_sombra_en_blanco_no_declara_nada(self) -> None:
        fila, = self._fila([self._entrada("m.a")])
        self.assertFalse(fila["declara_desde"])
        self.assertFalse(fila["declara_porque"])

    def test_un_motivo_de_puros_espacios_no_cuenta_como_declarado(self) -> None:
        fila, = self._fila([self._entrada("m.a", "2026-01-01", "   ")])
        self.assertFalse(fila["declara_porque"])

    def test_dio_ok_marca_la_sombra_que_ya_no_hace_falta(self) -> None:
        filas = self._fila([self._entrada("m.verde"), self._entrada("m.roja")],
                           ok={"m.verde": True, "m.roja": False})
        self.assertEqual({f["medida"]: f["dio_ok"] for f in filas},
                         {"m.verde": True, "m.roja": False})

    def test_una_medida_que_no_corrio_no_se_declara_en_verde(self) -> None:
        """No se puede afirmar que esté en verde algo que no se evaluó."""
        fila, = self._fila([self._entrada("m.a")], ok={})
        self.assertFalse(fila["dio_ok"])

    def test_existe_compara_contra_el_catalogo_cargado(self) -> None:
        filas = self._fila([self._entrada("m.hay"), self._entrada("m.no")],
                           catalogo={"m.hay": object()})
        self.assertEqual({f["medida"]: f["existe"] for f in filas},
                         {"m.hay": True, "m.no": False})

    def test_sin_sombras_la_relacion_viene_vacia(self) -> None:
        self.assertEqual(self._fila([]), [])


class HechosDeDocumentacion(unittest.TestCase):
    """La documentación es la única parte del proyecto SIN arnés, y por eso envejece sola.

    Al 2026-09-01, diez de diecinueve relaciones del lenguaje —incluidas TODAS las de L−1 y L−2—
    no estaban nombradas en la especificación, y nada lo había señalado nunca. Se encontró porque
    alguien preguntó, no porque algo se pusiera rojo.
    """

    def _filas(self, relaciones, referencia):
        from nucleo.marco import hechos_de_documentacion
        return hechos_de_documentacion(relaciones, referencia).get("relacion_documentada", [])

    def test_marca_la_que_la_referencia_no_nombra(self) -> None:
        filas = self._filas({"esta", "no_esta"}, "acá se habla de `esta` y nada más")
        self.assertEqual({f["relacion"]: f["nombrada_en_la_referencia"] for f in filas},
                         {"esta": True, "no_esta": False})

    def test_sin_referencia_no_se_emite_ni_la_relacion(self) -> None:
        """Un consumidor no tiene —ni tiene por qué tener— la especificación de Oracle: el paquete
        instalado ni la incluye. Documentar el lenguaje es de quien lo publica.

        Se devuelve el mapa VACÍO, no la relación vacía: `medidas_aplicables` elige juezas por las
        relaciones presentes, así que sin la clave la medida ni se evalúa. Con la clave vacía
        saldría SIN EVIDENCIA, que la aceptación cuenta como falla — un rojo igual."""
        from nucleo.marco import hechos_de_documentacion
        for vacia in ("", "   ", "\n\t "):
            with self.subTest(referencia=repr(vacia)):
                self.assertEqual(hechos_de_documentacion({"a", "b"}, vacia), {})

    def test_sale_ordenado_para_que_dos_corridas_se_lean_igual(self) -> None:
        filas = self._filas({"zeta", "alfa", "media"}, "una referencia con texto")
        self.assertEqual([f["relacion"] for f in filas], ["alfa", "media", "zeta"])

    def test_sin_relaciones_la_relacion_viene_vacia(self) -> None:
        """Distinto de no tener referencia: acá la referencia existe y no hay nada que documentar."""
        from nucleo.marco import hechos_de_documentacion
        self.assertEqual(hechos_de_documentacion(set(), "cualquier cosa"),
                         {"relacion_documentada": []})

