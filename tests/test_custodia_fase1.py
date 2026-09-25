"""Contratos de los tres arneses incorporados al perfil de custodia."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


class MutacionDeMedidas(unittest.TestCase):
    def test_casos_incluye_el_corpus_y_cada_fixture_diferencial(self):
        from tools import mutar

        proy = SimpleNamespace(corpus=Path("corpus"), diferencial=Path("diferencial"),
                               raiz=Path("."))
        corpus = [{"medida": "del.corpus"}]
        fixture = object()
        diferencial = [{"medida": "del.diferencial"}]
        with mock.patch.object(mutar, "cargar_casos", return_value=corpus), \
             mock.patch.object(mutar, "cargar_fixtures", return_value=([fixture], [])), \
             mock.patch.object(mutar, "casos_para_mutacion", return_value=diferencial) as convertir:
            self.assertEqual(mutar.casos(proy, {}), [{"medida": "del.corpus"}, *diferencial])
            convertir.assert_called_once_with(fixture, {})

    def test_un_fixture_invalido_impide_mutar_medidas(self):
        from tools import mutar

        proy = SimpleNamespace(corpus=Path("corpus"), diferencial=Path("diferencial"),
                               raiz=Path("."))
        with mock.patch.object(mutar, "cargar_casos", return_value=[]), \
             mock.patch.object(mutar, "cargar_fixtures", return_value=([], ["fixture vencido"])):
            with self.assertRaisesRegex(ValueError, "fixture vencido"):
                mutar.casos(proy, {})

    def test_politicas_rechazan_rojos_y_medidas_que_no_pudieron_juzgar(self):
        from tools import mutar

        verde = SimpleNamespace(ok=True, sin_evidencia=False)
        rojo = SimpleNamespace(ok=False, sin_evidencia=False)
        ausente = SimpleNamespace(ok=False, sin_evidencia=True)
        informe = lambda veredictos, no_juzgaron=(): SimpleNamespace(
            veredictos=veredictos, no_juzgaron=no_juzgaron)
        self.assertTrue(mutar._politicas_ok(informe([verde, ausente])))
        self.assertFalse(mutar._politicas_ok(informe([verde, rojo])))
        self.assertFalse(mutar._politicas_ok(informe([verde], [("meta.x", "campo ausente")])))

    def test_mutante_vivo_hace_fallar_la_corrida_aunque_la_politica_sea_verde(self):
        from tools import mutar

        proy = SimpleNamespace(es_el_propio_oracle=True)
        catalogo = {}
        informe = SimpleNamespace(veredictos=[], no_juzgaron=[])
        vivo = {"detecciones_conductuales": [], "rechazos_del_algebra": [],
                "cambio": "umbral", "apunta_a": "m.x"}
        muerto = {**vivo, "detecciones_conductuales": ["c1"]}
        with mock.patch.multiple(mutar, problemas_estructura=lambda *_: [],
                                 catalogos_a_cargar=lambda *_: [],
                                 macros_del_proyecto=lambda *_: [],
                                 cargar_catalogo=lambda *_a, **_k: catalogo,
                                 casos=lambda *_: [],
                                 correr=lambda *_: {"mutante": [vivo, muerto], "deteccion": []},
                                 cobertura_de_mutadores=lambda: {"hay_ajenos": True,
                                    "total": 2, "propios": 1, "ajenos": 1},
                                 evaluadas_en_otro_arnes=lambda *_: set(),
                                 hechos_de_uso=lambda *_a, **_k: {},
                                 medidas_aplicables=lambda *_: [],
                                 evaluar_conjunto=lambda *_: informe):
            with redirect_stdout(io.StringIO()) as salida:
                self.assertEqual(mutar._ejecutar(proy, []), 1)
        self.assertIn("sobrevivieron 1", salida.getvalue())


class TrazaDelAlgebra(unittest.TestCase):
    def test_un_caso_que_falla_se_cuenta_y_no_inventa_traza(self):
        from tools import trazar

        medida = SimpleNamespace(evaluar=mock.Mock(side_effect=ValueError("roto")))
        datos, evaluados, fallidos = trazar.hechos(
            {"m.x": medida}, [{"medida": "m.x", "evidencia": {"r": []}}])
        self.assertEqual((evaluados, fallidos), (0, 1))
        self.assertEqual(datos, {"paso": [], "nodo": [], "producto": []})

    def test_traza_vacia_y_ausencia_de_juezas_fallan_cerrado(self):
        from tools import trazar

        proy = SimpleNamespace()
        base = {"paso": [{"t": 1}], "nodo": [{"cabeza": "x"}],
                "producto": [{"izquierda": 1}]}
        common = dict(Proyecto=lambda *_: proy, catalogos_a_cargar=lambda *_: [],
                      macros_del_proyecto=lambda *_: [], cargar_catalogo=lambda *_a, **_k: {},
                      casos=lambda *_: [], medidas_aplicables=lambda *_: [])
        with mock.patch.multiple(trazar, **common), \
             mock.patch.object(trazar, "hechos", return_value=({**base, "paso": []}, 0, 0)):
            with redirect_stdout(io.StringIO()) as salida:
                self.assertEqual(trazar.main([]), 1)
            self.assertIn("TRAZA VACÍA", salida.getvalue())
        with mock.patch.multiple(trazar, **common), \
             mock.patch.object(trazar, "hechos", return_value=(base, 1, 0)):
            with redirect_stdout(io.StringIO()) as salida:
                self.assertEqual(trazar.main([]), 1)
            self.assertIn("sin medidas aplicables", salida.getvalue())

    def test_un_desacuerdo_con_la_referencia_hace_fallar(self):
        from tools import trazar

        proy = SimpleNamespace()
        base = {"paso": [{}], "nodo": [{}], "producto": [{}]}
        juez = SimpleNamespace(id="meta.x")
        veredicto = SimpleNamespace(id="meta.x", alcance="vigila", linea=lambda: "verde")
        informe = SimpleNamespace(veredictos=[veredicto], ok=True)
        with mock.patch.multiple(trazar, Proyecto=lambda *_: proy,
                                 catalogos_a_cargar=lambda *_: [],
                                 macros_del_proyecto=lambda *_: [],
                                 cargar_catalogo=lambda *_a, **_k: {}, casos=lambda *_: [],
                                 hechos=lambda *_: (base, 1, 0),
                                 medidas_aplicables=lambda *_: [juez],
                                 evaluar=lambda *_: informe,
                                 contrastar=lambda *_: ["meta.x discrepa"]):
            with redirect_stdout(io.StringIO()) as salida:
                self.assertEqual(trazar.main([]), 1)
            self.assertIn("DESACUERDO", salida.getvalue())


class EmisorDiferencial(unittest.TestCase):
    def test_no_escribe_un_fixture_invalido(self):
        from tools import generar_diferencial as gen

        with tempfile.TemporaryDirectory() as td:
            ruta = Path(td) / "fixture.json"
            with mock.patch.multiple(gen, SALIDA=ruta, Proyecto=lambda *_: object(),
                                     catalogos_a_cargar=lambda *_: [],
                                     macros_del_proyecto=lambda *_: [],
                                     cargar_catalogo=lambda *_a, **_k: {},
                                     construir=lambda *_: {"dato": 1},
                                     validar_fixture=lambda *_: ["inválido"]):
                with redirect_stdout(io.StringIO()) as salida:
                    self.assertEqual(gen.main(["--escribir"]), 1)
                self.assertFalse(ruta.exists())
                self.assertIn("FIXTURE INVÁLIDO", salida.getvalue())

    def test_verificar_detecta_fixture_ausente_y_vencido(self):
        from tools import generar_diferencial as gen

        with tempfile.TemporaryDirectory() as td:
            ruta = Path(td) / "fixture.json"
            with mock.patch.multiple(gen, RAIZ=Path(td), SALIDA=ruta, Proyecto=lambda *_: object(),
                                     catalogos_a_cargar=lambda *_: [],
                                     macros_del_proyecto=lambda *_: [],
                                     cargar_catalogo=lambda *_a, **_k: {},
                                     construir=lambda *_: {"dato": 1},
                                     validar_fixture=lambda *_: []):
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(gen.main([]), 1)
                ruta.write_text("vencido", encoding="utf-8")
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(gen.main([]), 1)
                self.assertEqual(json.loads(gen.serializar({"dato": 1})), {"dato": 1})


if __name__ == "__main__":
    unittest.main()
