"""Regresiones fail-closed de las herramientas de línea de comandos."""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo.diferencial import Procedencia, crear_frescura
from nucleo.fixtures import cargar_fixtures, evidencias as evidencias_fixture
from nucleo.macro import EXTENSIONES_DE_MACRO
from nucleo.medida import Medida
from nucleo import algebra
from nucleo.proyecto import (ConfiguracionProyecto, EscalaresInvalidas, Proyecto, ProyectoInvalido,
                             configuracion, escalares_del_proyecto, sin_bandera)

def setUpModule() -> None:
    """Importa las herramientas DENTRO de la suite, no al descubrirla.

    Cada `tools/*.py` hace `import catalogos` al tope —correcto para un CLI, que necesita las
    escalares registradas apenas arranca— pero traerlas al importar este archivo metía `@escalar` en
    el **descubrimiento**: un mutante en `escalar()` o `_registro()` rompía la importación y el arnés
    lo daba por «error» en vez de «muerte».
    """
    global revisar_estado_sin_medida, revisar_evidencia, comparar_dominio, validar_fixture
    from tools.corpus import revisar_estado_sin_medida, revisar_evidencia  # noqa: F811
    from tools.diferencial import comparar_dominio, validar_fixture  # noqa: F811


RAIZ = Path(__file__).resolve().parents[1]


def _evidencia(valor=True):
    return {"hecho": [{"id": "h", "ok": valor}]}


def _frescura():
    return {
        "algoritmo": "sha256",
        "raiz_fuentes": ".",
        "fuentes": {"emisor": ["tools/emisor.py"], "referencia": ["ref.py"]},
        "configuracion": {"repeticiones": 1},
        "huellas": {k: "a" * 64 for k in
                     ("emisor", "referencia", "catalogo", "configuracion")},
    }


def _dominio(**cambios):
    datos = {
        "esquema": "oracle.diferencial/v1",
        "origen": "referencia independiente",
        "dominio": "prueba",
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
    datos.update(cambios)
    return datos


class CorpusL0Tests(unittest.TestCase):
    def test_una_relacion_presente_puede_tener_cero_filas(self) -> None:
        self.assertEqual(revisar_evidencia("caso", {"relacion": []}), [])

    def test_el_mapa_de_evidencia_no_puede_estar_vacio(self) -> None:
        self.assertTrue(revisar_evidencia("caso", {}))

    def test_un_caso_sin_medida_distingue_deuda_memoria_y_limite_humano(self) -> None:
        validos = (
            {"medida": None, "estado_sin_medida": "abierto",
             "sin_medida_todavia": "falta una capacidad"},
            {"medida": None, "estado_sin_medida": "resuelto",
             "resuelto": "se eliminó la duplicación"},
            {"medida": None, "estado_sin_medida": "limite_humano",
             "limite_humano": "requiere juicio causal"},
        )
        for caso in validos:
            self.assertEqual(revisar_estado_sin_medida("caso", caso), [])

        for caso in ({"medida": None},
                     {"medida": None, "estado_sin_medida": "resuelto"},
                     {"medida": None, "estado_sin_medida": "inventado", "resuelto": "x"}):
            self.assertTrue(revisar_estado_sin_medida("caso", caso))


class ClaveEnElCorpus(unittest.TestCase):
    """El validador L0 del corpus y el del álgebra leen el MISMO contrato.

    Escritos por separado divergen —es el caso `012`— y acá la divergencia tenía una consecuencia
    concreta: un caso que declaraba una clave era rechazado como «no es un hecho», así que el
    mecanismo no se podía fijar con casos. En este proyecto todo lo demás se fija con casos.
    """

    def test_una_relacion_puede_declarar_su_clave(self) -> None:
        self.assertEqual(
            revisar_evidencia("caso", {"pieza": [["clave", ["id"]], {"id": "a"}]}), [])

    def test_una_clave_mal_declarada_se_denuncia_como_clave(self) -> None:
        for malo in ([], [1], ["id", "id"], ["  "]):
            with self.subTest(malo=malo):
                fallas = revisar_evidencia("caso", {"pieza": [["clave", malo], {"id": "a"}]})
                self.assertTrue(fallas)
                self.assertIn("clave", fallas[0])

    def test_una_fila_que_no_es_hecho_sigue_denunciandose_como_fila(self) -> None:
        """El nodo `clave` sólo vale a la cabeza: en otra posición es una fila mal formada."""
        fallas = revisar_evidencia("caso", {"pieza": [{"id": "a"}, ["clave", ["id"]]]})
        self.assertTrue(fallas)
        self.assertIn("no es un hecho", fallas[0])

    def test_el_validador_del_corpus_no_reimplementa_la_regla(self) -> None:
        """Si el corpus tuviera su propia copia, este test se cae al cambiar una sola de las dos."""
        from nucleo import algebra, caso
        from tools import corpus as cli

        self.assertIs(cli.separar_clave, algebra.separar_clave)
        self.assertIs(cli.ETIQUETAS, caso.ETIQUETAS)
        self.assertIs(cli.DETECCIONES, caso.DETECCIONES)


class ContratoDiferencialTests(unittest.TestCase):
    def test_un_fixture_de_dominio_completo_es_valido(self) -> None:
        self.assertEqual(validar_fixture(_dominio()), [])

    def test_una_relacion_vacia_tambien_es_L0_valida_en_un_fixture(self) -> None:
        datos = _dominio()
        for escenario in datos["escenarios"]:
            escenario["evidencia"] = {"hecho": []}
        self.assertEqual(validar_fixture(datos), [])

    def test_dominio_exige_contenido_consistencia_y_dos_polaridades(self) -> None:
        invalidos = (
            _dominio(medidas=[]),
            _dominio(escenarios=[], mundos=0),
            _dominio(mundos=99),
            _dominio(escenarios=[
                {**_dominio()["escenarios"][0], "id": "a"},
                {**_dominio()["escenarios"][0], "id": "b"},
            ]),
            _dominio(escenarios=[
                {"id": "", "evidencia": {}, "referencia_ok": "sí",
                 "oracle_al_generar": {}},
                {**_dominio()["escenarios"][1], "id": "b"},
            ]),
        )
        for datos in invalidos:
            with self.subTest(datos=datos):
                self.assertTrue(validar_fixture(datos))

    def test_formato_grupos_exige_grupos_casos_y_campos_basicos(self) -> None:
        valido = {
            "esquema": "oracle.diferencial/v1",
            "origen": "referencia independiente",
            "mundos": 2,
            "frescura": _frescura(),
            "grupos": {
                "prueba.mide": [
                    {"evidencia": _evidencia(True), "esperado_ok": True},
                    {"evidencia": _evidencia(False), "esperado_ok": False},
                ],
            },
        }
        self.assertEqual(validar_fixture(valido), [])

        for datos in (
            {**valido, "grupos": {}},
            {**valido, "grupos": {"prueba.mide": []}},
            {**valido, "grupos": {"prueba.mide": [{"evidencia": _evidencia()}]}},
            {**valido, "mundos": 3},
            {**valido, "grupos": {"id con espacios": valido["grupos"]["prueba.mide"]}},
            {**valido, "grupos": {"prueba.mide": [
                {"evidencia": _evidencia(), "esperado_ok": True},
                {"evidencia": _evidencia(), "esperado_ok": True},
            ]}},
        ):
            with self.subTest(datos=datos):
                self.assertTrue(validar_fixture(datos))

    def test_en_grupos_mundos_es_el_largo_de_cada_grupo_no_la_suma(self) -> None:
        casos = [
            {"evidencia": _evidencia(True), "esperado_ok": True},
            {"evidencia": _evidencia(False), "esperado_ok": False},
        ]
        historico = {
            "esquema": "oracle.diferencial/v1",
            "origen": "fixture histórico",
            "mundos": 2,
            "frescura": _frescura(),
            "grupos": {"a.mide": casos, "b.mide": list(casos)},
        }
        self.assertEqual(validar_fixture(historico), [])

    def test_el_lector_comun_normaliza_grupos_y_escenarios(self) -> None:
        grupos = {
            "esquema": "oracle.diferencial/v1", "origen": "histórico", "mundos": 2,
            "frescura": _frescura(), "grupos": {"prueba.mide": [
                {"evidencia": _evidencia(True), "esperado_ok": True},
                {"evidencia": _evidencia(False), "esperado_ok": False},
            ]}}
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            rutas = [raiz / "dominio.json", raiz / "grupos.json"]
            rutas[0].write_text(json.dumps(_dominio()), encoding="utf-8")
            rutas[1].write_text(json.dumps(grupos), encoding="utf-8")
            fixtures, fallas = cargar_fixtures(rutas)

        self.assertEqual(fallas, [])
        self.assertEqual([len(list(evidencias_fixture(f))) for f in fixtures], [2, 2])

    def test_rechaza_fixture_sin_version_huellas_o_foto_individual(self) -> None:
        sin_version = _dominio()
        del sin_version["esquema"]
        sin_huellas = _dominio()
        sin_huellas["frescura"]["huellas"] = {}
        sin_individual = _dominio()
        del sin_individual["escenarios"][0]["oracle_al_generar"]
        for datos in (sin_version, sin_huellas, sin_individual):
            with self.subTest(datos=datos):
                self.assertTrue(validar_fixture(datos))

    def test_una_permutacion_individual_no_se_oculta_detras_del_AND_global(self) -> None:
        from nucleo.medida import Medida

        def medida(mid, campo):
            return Medida.de_datos(
                ["ninguno", mid, "hecho", "h", ["==", ["campo", "h", campo], True],
                 "razón", "NO ve el otro campo"])

        original = {"m.a": medida("m.a", "a"), "m.b": medida("m.b", "b")}
        escenarios = []
        for eid, a, b in (("solo-a", True, False), ("solo-b", False, True),
                          ("ninguno", False, False)):
            evidencia = {"hecho": [{"a": a, "b": b}]}
            por_medida = {mid: m.evaluar(evidencia).ok for mid, m in original.items()}
            escenarios.append({
                "id": eid, "evidencia": evidencia, "referencia_ok": all(por_medida.values()),
                "oracle_al_generar": {
                    "global_ok": all(por_medida.values()), "por_medida": por_medida},
            })
        datos = {"medidas": ["m.a", "m.b"], "escenarios": escenarios}
        permutado = {"m.a": medida("m.a", "b"), "m.b": medida("m.b", "a")}

        comparacion = comparar_dominio(datos, permutado)
        self.assertEqual(comparacion["desacuerdos_globales"], [])
        self.assertEqual(len(comparacion["cambios_individuales"]), 4)


class HerramientasCLITests(unittest.TestCase):
    def test_documento_integral_anida_titulos_sin_alterar_bloques_de_codigo(self) -> None:
        from tools import estudio

        texto = estudio.documento_unico({
            "README.md": "índice descartado",
            "00-prueba.md": "# Título\n\n## Sección\n\n```bash\n# comentario\n```\n",
        }, extras=())

        self.assertIn("## Título", texto)
        self.assertIn("### Sección", texto)
        self.assertIn("```bash\n# comentario\n```", texto)
        self.assertNotIn("índice descartado", texto)

    def test_importar_herramientas_no_interpreta_argv_del_host(self) -> None:
        programa = """
import sys
sys.argv = ['proceso-anfitrion', '--proyecto', '/ruta/que/no/existe']
from tools import aceptacion, cifras, corpus, diferencial, estudio, medida, mutar, mutar_codigo
for modulo in (aceptacion, corpus, diferencial, estudio, medida, mutar):
    assert modulo.main(['--help']) == 0, modulo.__name__
print('IMPORTS OK')
"""
        resultado = subprocess.run(
            [sys.executable, "-c", programa], cwd=RAIZ, capture_output=True, text=True)

        self.assertEqual(resultado.returncode, 0, resultado.stdout + resultado.stderr)
        self.assertIn("IMPORTS OK", resultado.stdout)

    def test_oracle_sin_fixtures_diferenciales_no_se_declara_verde(self) -> None:
        from tools import diferencial as cli

        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            (raiz / "diferencial").mkdir()
            salida = io.StringIO()
            with redirect_stdout(salida):
                codigo = cli._ejecutar(Proyecto(raiz))

        self.assertEqual(codigo, 1)
        self.assertIn("no hay fixtures", salida.getvalue())
        self.assertNotIn("DIFERENCIAL ✓", salida.getvalue())

    def _proyecto(self, raiz: Path) -> None:
        (raiz / "catalogos").mkdir()

    def _proyecto_externo_completo(self, raiz: Path) -> Path:
        for nombre in ("catalogos", "corpus", "diferencial"):
            (raiz / nombre).mkdir()
        (raiz / "emisor.py").write_text("VERSION = 1\n", encoding="utf-8")
        (raiz / "referencia.py").write_text("VERSION = 1\n", encoding="utf-8")
        (raiz / "escalares.py").write_text(
            "from nucleo.algebra import escalar\n"
            "@escalar('es_malo_demo')\n"
            "def es_malo_demo(fila): return fila['mal']\n",
            encoding="utf-8")
        with escalares_del_proyecto(Proyecto(raiz), confiar=True):
            medida = Medida.de_datos([
                "ninguno", "demo.sin_malos", "item", "x",
                ["es_malo_demo", ["hecho", "x"]],
                "cualquier item malo invalida el conjunto",
                "NO ve propiedades distintas de `mal`",
            ])
        dominio = raiz / "catalogos" / "demo"
        dominio.mkdir()
        ruta_medida = dominio / "demo.sin_malos.json"
        ruta_medida.write_text(json.dumps(medida.a_datos()), encoding="utf-8")

        comunes = {
            "fecha": "2026-07-30", "origen": {"repo": "temporal", "commit": "ninguno"},
            "procedencia": "observada",
            "titulo": "caso temporal", "sintoma": "prueba", "como_se_detecto": "observacion",
            "medida": medida.id, "leccion": "prueba de integración",
        }
        casos = (
            {**comunes, "id": "001-rojo", "etiqueta": "falso_verde",
             "evidencia": {"item": [{"id": "a", "mal": True}]}},
            {**comunes, "id": "002-verde", "etiqueta": "verde_correcto",
             "evidencia": {"item": [{"id": "a", "mal": False}]}},
        )
        for caso in casos:
            (raiz / "corpus" / f"{caso['id']}.json").write_text(
                json.dumps(caso), encoding="utf-8")

        escenarios = []
        with escalares_del_proyecto(Proyecto(raiz), confiar=True):
            for caso in casos:
                ok = medida.evaluar(caso["evidencia"]).ok
                escenarios.append({
                    "id": caso["id"], "evidencia": caso["evidencia"], "referencia_ok": ok,
                    "oracle_al_generar": {"global_ok": ok, "por_medida": {medida.id: ok}},
                })
        procedencia = Procedencia(
            raiz=raiz, emisor=("emisor.py",), referencia=("referencia.py",))
        fixture = {
            "esquema": "oracle.diferencial/v1", "origen": "referencia temporal",
            "dominio": "demo", "medidas": [medida.id], "mundos": 2,
            "escenarios": escenarios,
            "frescura": crear_frescura(procedencia, [medida], {"repeticiones": 1}),
        }
        (raiz / "diferencial" / "demo.json").write_text(
            json.dumps(fixture), encoding="utf-8")
        return ruta_medida

    def test_aceptacion_sin_casos_es_no_aplicable_y_falla(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proyecto = Path(td)
            self._proyecto(proyecto)
            (proyecto / "corpus").mkdir()
            r = subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "aceptacion.py"),
                 "--proyecto", str(proyecto)],
                cwd=RAIZ, capture_output=True, text=True)

        salida = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("SIN CASOS", salida)
        self.assertNotIn("ACEPTACIÓN ✓", salida)

    def test_fixture_malformado_falla_sin_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proyecto = Path(td)
            self._proyecto(proyecto)
            diferencial = proyecto / "diferencial"
            diferencial.mkdir()
            (diferencial / "roto.json").write_text(json.dumps({}), encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "diferencial.py"),
                 "--proyecto", str(proyecto)],
                cwd=RAIZ, capture_output=True, text=True)

        salida = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("DIFERENCIAL ✗", salida)
        self.assertNotIn("Traceback", salida)

    def test_nueva_rechaza_ids_de_ruta_y_symlinks_fuera_del_catalogo(self) -> None:
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as afuera:
            proyecto = Path(td)
            self._proyecto(proyecto)
            (proyecto / "catalogos" / "escape").symlink_to(Path(afuera), target_is_directory=True)
            comandos = ("../fuera", "/tmp/fuera", "escape.medida")
            resultados = [subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "medida.py"), "--nueva", mid,
                 "--proyecto", str(proyecto)],
                cwd=RAIZ, capture_output=True, text=True) for mid in comandos]

            self.assertTrue(all(r.returncode != 0 for r in resultados))
            self.assertFalse((Path(afuera) / "escape.medida.json").exists())
            self.assertFalse((proyecto / "fuera.json").exists())

    def test_cada_herramienta_exige_la_estructura_que_consume(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proyecto = Path(td)
            self._proyecto(proyecto)
            r = subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "medida.py"), "--relaciones",
                 "--proyecto", str(proyecto)], cwd=RAIZ, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("falta `corpus/`", r.stdout)
        self.assertIn("falta `diferencial/`", r.stdout)

    def test_estudio_no_ejecuta_escalares_externas_sin_confirmacion(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proyecto = Path(td)
            self._proyecto(proyecto)
            (proyecto / "corpus").mkdir()
            dominio = proyecto / "catalogos" / "demo"
            dominio.mkdir()
            (dominio / "demo.udf.json").write_text(json.dumps([
                "ninguno", "demo.udf", "item", "x",
                ["es_malo_temporal", ["hecho", "x"]], "razón", "NO ve otros campos",
            ]), encoding="utf-8")
            marca = proyecto / "ejecutado"
            (proyecto / "escalares.py").write_text(
                "from pathlib import Path\n"
                "from nucleo.algebra import escalar\n"
                f"Path({str(marca)!r}).write_text('sí')\n"
                "@escalar('es_malo_temporal')\n"
                "def es_malo_temporal(fila): return fila['mal']\n",
                encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "estudio.py"),
                 "--proyecto", str(proyecto)], cwd=RAIZ, capture_output=True, text=True)
            se_ejecuto = marca.exists()
            confiado = subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "estudio.py"),
                 "--proyecto", str(proyecto), "--confiar-escalares"],
                cwd=RAIZ, capture_output=True, text=True)
            se_ejecuto_con_confianza = marca.exists()

        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--confiar-escalares", r.stdout)
        self.assertFalse(se_ejecuto)
        self.assertEqual(confiado.returncode, 0, confiado.stdout + confiado.stderr)
        self.assertTrue(se_ejecuto_con_confianza)

    def test_ayuda_e_inventarios_no_ejecutan_python_externo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proyecto = Path(td)
            for nombre in ("catalogos", "corpus", "diferencial"):
                (proyecto / nombre).mkdir()
            marca = proyecto / "ejecutado"
            (proyecto / "escalares.py").write_text(
                f"from pathlib import Path\nPath({str(marca)!r}).write_text('sí')\n",
                encoding="utf-8")
            herramientas = ("aceptacion.py", "diferencial.py", "medida.py", "mutar.py",
                            "mutar_codigo.py", "estudio.py")
            ayudas = [subprocess.run(
                [sys.executable, str(RAIZ / "tools" / herramienta), "--help",
                 "--proyecto", str(proyecto)], cwd=RAIZ, capture_output=True, text=True)
                for herramienta in herramientas]
            inventarios = [subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "medida.py"), opcion,
                 "--proyecto", str(proyecto)], cwd=RAIZ, capture_output=True, text=True)
                for opcion in ("--relaciones", "--escalares")]
            sin_confianza = subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "aceptacion.py"),
                 "--proyecto", str(proyecto)], cwd=RAIZ, capture_output=True, text=True)
            se_ejecuto = marca.exists()

        self.assertTrue(all(r.returncode == 0 for r in ayudas),
                        "\n".join(r.stdout + r.stderr for r in ayudas))
        self.assertTrue(all(r.returncode == 0 for r in inventarios))
        self.assertIn("no se ejecutó", inventarios[1].stdout)
        self.assertNotEqual(sin_confianza.returncode, 0)
        self.assertIn("--confiar-escalares", sin_confianza.stdout)
        self.assertFalse(se_ejecuto)

    def test_el_registro_de_escalares_esta_aislado_por_proyecto(self) -> None:
        nombre = "udf_aislada_temporal"
        self.assertNotIn(nombre, algebra.ESCALARES)
        for valor in (1, 2):
            with tempfile.TemporaryDirectory() as td:
                proyecto = Path(td)
                (proyecto / "catalogos").mkdir()
                (proyecto / "escalares.py").write_text(
                    "from nucleo.algebra import escalar\n"
                    f"@escalar('{nombre}', 'unidad', unidades_argumentos=('cm',))\n"
                    f"def funcion(x={valor}): return x\n",
                    encoding="utf-8")
                with escalares_del_proyecto(Proyecto(proyecto), confiar=True):
                    fn = algebra.ESCALARES[nombre]
                    self.assertEqual(fn(), valor)
                    self.assertEqual((fn.aridad_min, fn.aridad_max), (0, 1))
                    self.assertEqual(fn.unidad, "unidad")
                    self.assertEqual(fn.unidades_argumentos, ("cm",))
                    self.assertEqual(fn.procedencia_escalar, f"proyecto:{proyecto.resolve()}")
                self.assertNotIn(nombre, algebra.ESCALARES)

    def test_escalares_symlink_no_recibe_autoridad_de_ejecucion(self) -> None:
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as afuera:
            proyecto, exterior = Path(td), Path(afuera)
            (proyecto / "catalogos").mkdir()
            marca = exterior / "ejecutado"
            fuente = exterior / "escalares.py"
            fuente.write_text(
                f"from pathlib import Path\nPath({str(marca)!r}).write_text('sí')\n",
                encoding="utf-8")
            (proyecto / "escalares.py").symlink_to(fuente)
            with self.assertRaises(EscalaresInvalidas):
                with escalares_del_proyecto(Proyecto(proyecto), confiar=True):
                    pass
            se_ejecuto = marca.exists()
        self.assertFalse(se_ejecuto)

    def test_una_udf_no_puede_evitar_el_contrato_de_declaracion(self) -> None:
        nombre = "udf_sin_decorador_temporal"
        with tempfile.TemporaryDirectory() as td:
            proyecto = Path(td)
            (proyecto / "catalogos").mkdir()
            (proyecto / "escalares.py").write_text(
                "from nucleo.algebra import ESCALARES\n"
                f"ESCALARES['{nombre}'] = lambda x: x\n",
                encoding="utf-8")
            with self.assertRaises(EscalaresInvalidas):
                with escalares_del_proyecto(Proyecto(proyecto), confiar=True):
                    pass
        self.assertNotIn(nombre, algebra.ESCALARES)

    def test_flujo_completo_de_un_proyecto_externo_temporal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proyecto = Path(td)
            medida = self._proyecto_externo_completo(proyecto)
            comandos = (
                (["tools/corpus.py"], "CORPUS OK", False),
                (["tools/medida.py", "--relaciones"], "item", False),
                (["tools/medida.py", str(medida)], "discrimina", True),
                (["tools/aceptacion.py"], "ACEPTACIÓN ✓", True),
                (["tools/diferencial.py"], "DIFERENCIAL ✓", True),
                (["tools/mutar.py"], "sobrevivieron 0", True),
                (["tools/estudio.py", "--destino", "salida-estudio"], "10 documentos", True),
            )
            resultados = []
            for argumentos, esperado, confiar in comandos:
                r = subprocess.run(
                    [sys.executable, str(RAIZ / argumentos[0]), *argumentos[1:],
                     "--proyecto", str(proyecto),
                     *(["--confiar-escalares"] if confiar else [])],
                    cwd=RAIZ, capture_output=True, text=True)
                resultados.append((argumentos[0], esperado, r))

            corpus_estudio = (proyecto / "salida-estudio" / "04-el-corpus.md").read_text(
                encoding="utf-8")

        for comando, esperado, r in resultados:
            with self.subTest(comando=comando):
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertIn(esperado, r.stdout)
        self.assertIn("001-rojo", corpus_estudio)

    def test_mutacion_tambien_rechaza_un_fixture_vencido(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proyecto = Path(td)
            self._proyecto_externo_completo(proyecto)
            (proyecto / "emisor.py").write_text("VERSION = 2\n", encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "mutar.py"),
                 "--proyecto", str(proyecto), "--confiar-escalares"],
                cwd=RAIZ, capture_output=True, text=True)

        self.assertNotEqual(r.returncode, 0)
        self.assertIn("fixture vencido", r.stdout)

    def test_argumentos_sin_bandera_solo_quita_el_par_proyecto(self) -> None:
        self.assertEqual(
            sin_bandera(["--hechos", "--timeout", "0.001"]),
            ["--hechos", "--timeout", "0.001"])
        self.assertEqual(
            sin_bandera(["--proyecto", "/tmp/proyecto", "--hechos"]),
            ["--hechos"])

    def test_mutacion_con_baseline_timeout_emite_error_json_y_falla(self) -> None:
        """Corre sobre una RAÍZ PROPIA, no sobre la del repositorio.

        El bloqueo de `mutar_codigo.py` es por raíz, así que este test fallaba —con
        `RondaEnCurso` en vez de `LineaBaseFallida`— cada vez que alguien tenía una ronda de verdad
        andando en el mismo árbol. Es la tercera vez en el día que un test rompe por depender del
        entorno de alrededor en vez de armarse el suyo, y la lección ya está escrita en los otros
        dos: un test que necesita el entorno de su autor no es un test, es una coincidencia.
        """
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td) / "proyecto"
            shutil.copytree(RAIZ, raiz, ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "build", "*.egg-info", "estudio"))
            r = subprocess.run(
                [sys.executable, str(raiz / "tools" / "mutar_codigo.py"),
                 "--hechos", "--timeout", "0.001"],
                cwd=raiz, capture_output=True, text=True)

            self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
            datos = json.loads(r.stdout)
            self.assertEqual(datos["error_mutacion"][0]["tipo"], "LineaBaseFallida")
            self.assertIn("timeout", datos["error_mutacion"][0]["mensaje"])
            self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_la_mutacion_de_codigo_incluye_el_perfil_y_particiona_sin_escapar(self) -> None:
        from tools import mutar_codigo as cli

        disponibles = cli.objetivos_disponibles()
        self.assertIn("nucleo/algebra.py", disponibles)
        self.assertIn("nucleo/aislamiento/escalares.py", disponibles)
        self.assertIn("oracle_metalenguaje/motor.py", disponibles)
        self.assertIn("perfiles/python/mutacion_codigo.py", disponibles)
        elegidos = cli.resolver_objetivos(["nucleo/algebra.py"])
        self.assertEqual(elegidos, [RAIZ / "nucleo" / "algebra.py"])
        comando = cli.comando_de_tests(elegidos, priorizar=True)
        self.assertEqual(comando[len(cli.TESTS):], [
            "--prioridad", "tests.test_algebra",
            "--prioridad", "tests.test_nucleo",
            "--prioridad", "tests.test_motor",
        ])
        dependencias = {p.relative_to(RAIZ).as_posix() for p in cli.dependencias_de_ronda()}
        self.assertIn("tests/test_nucleo.py", dependencias)
        self.assertIn("oracle_metalenguaje/motor.py", dependencias)
        self.assertIn("tools/ejecutar_suite_mutacion.py", dependencias)

        for invalido in ("../afuera.py", "/tmp/afuera.py", "nucleo/no_existe.py"):
            with self.subTest(invalido=invalido):
                with self.assertRaises(ValueError):
                    cli.resolver_objetivos([invalido])
        with self.assertRaises(ValueError):
            cli.resolver_objetivos(["nucleo/algebra.py", "nucleo/algebra.py"])

    def _salida_mutacion_simulada(self, *, mutantes: int, errores: int, timeouts: int,
                                  equivalentes: list[dict] | None = None) -> int:
        from tools import mutar_codigo as cli

        evidencia = {
            "mutante": [],
            "mutante_equivalente": equivalentes or [],
            "corrida_mutacion": [{
                "id": "simulada",
                "mutantes": mutantes,
                "baseline_verde": True,
                "bytecode_frio": True,
                "tests_fallaron": 0,
                "errores_arnes": errores,
                "timeouts": timeouts,
            }],
        }
        with (mock.patch.object(cli, "correr", return_value=evidencia),
              mock.patch.object(cli.sys, "argv", ["mutar_codigo.py", "--hechos"]),
              redirect_stdout(io.StringIO())):
            return cli.main()

    def test_un_equivalente_inconcluso_no_puede_hacer_salir_cero(self) -> None:
        equivalente = [{
            "id": "m.py:1:8:constante", "estado": "timeout", "tests_fallaron": False,
            "error_arnes": False, "timeout": True,
        }]
        self.assertEqual(
            self._salida_mutacion_simulada(
                mutantes=1, errores=0, timeouts=1, equivalentes=equivalente),
            2)

    def test_una_ronda_sin_mutantes_es_inconclusa(self) -> None:
        self.assertEqual(
            self._salida_mutacion_simulada(mutantes=0, errores=0, timeouts=0),
            2)

    def test_equivalentes_json_rechaza_duplicados_razones_vacias_y_formato_roto(self) -> None:
        from tools import mutar_codigo as cli

        invalidos = (
            [{"id": "m:1", "razon": "una"}, {"id": "m:1", "razon": "otra"}],
            [{"id": "m:1", "razon": "  "}],
            {"id": "m:1", "razon": "no es una lista"},
        )
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "equivalentes.json"
            for datos in invalidos:
                with self.subTest(datos=datos):
                    ruta.write_text(json.dumps(datos), encoding="utf-8")
                    with self.assertRaises(cli.EquivalenteInvalido):
                        cli.cargar_equivalentes(ruta)

            ruta.write_text("{roto", encoding="utf-8")
            with self.assertRaises(cli.EquivalenteInvalido):
                cli.cargar_equivalentes(ruta)

            ruta.write_text(
                json.dumps([{"id": "m:1", "razon": "revisión individual"}]),
                encoding="utf-8")
            self.assertEqual(cli.cargar_equivalentes(ruta), {"m:1": "revisión individual"})


class RunnerMutacionTests(unittest.TestCase):
    def _correr(self, fuente: str | None, *extras: str):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            tests = raiz / "tests"
            tests.mkdir()
            (tests / "__init__.py").write_text("", encoding="utf-8")
            if fuente is not None:
                (tests / "test_ejemplo.py").write_text(fuente, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(RAIZ / "tools" / "ejecutar_suite_mutacion.py"),
                 "--inicio", "tests", "--tope", ".", *extras],
                cwd=raiz, capture_output=True, text=True)

    def test_un_fallo_o_excepcion_dentro_de_un_test_discrimina(self) -> None:
        fallo = self._correr(
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_falla(self): self.assertEqual(1, 2)\n")
        excepcion = self._correr(
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_error(self): raise RuntimeError('roto')\n")

        self.assertEqual(fallo.returncode, 1, fallo.stdout + fallo.stderr)
        self.assertEqual(excepcion.returncode, 1, excepcion.stdout + excepcion.stderr)

    def test_se_detiene_en_el_primer_fallo(self) -> None:
        r = self._correr(
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_a_falla(self): self.fail('discrimina')\n"
            "    def test_b_no_debe_correr(self): print('SEGUNDO_TEST_EJECUTADO')\n")

        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertNotIn("SEGUNDO_TEST_EJECUTADO", r.stdout + r.stderr)

    def test_una_prioridad_discrimina_antes_de_descubrir_el_resto(self) -> None:
        r = self._correr(
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_falla(self): self.fail('prioridad')\n",
            "--prioridad", "tests.test_ejemplo")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)

    def test_una_prioridad_inexistente_es_error_del_arnes(self) -> None:
        r = self._correr(
            "import unittest\nclass T(unittest.TestCase):\n    def test_ok(self): pass\n",
            "--prioridad", "tests.no_existe")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("carga prioritaria", r.stdout + r.stderr)

    def test_cero_tests_es_error_del_arnes(self) -> None:
        r = self._correr(None)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("cero tests", r.stdout + r.stderr)

    def test_system_exit_durante_descubrimiento_es_error_del_arnes(self) -> None:
        r = self._correr("raise SystemExit(1)\n")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("SystemExit", r.stdout + r.stderr)


class CifrasDelReadme(unittest.TestCase):
    """Un número tipeado a mano en la prosa es una afirmación que nadie ejercita.

    El corte anterior publicaba «2202 líneas» y «trece a uno» cuando ya iban 2654 y 16,2 — y la
    proporción es el criterio de falsación declarado del proyecto. Estas regresiones fijan que cada
    cifra salga de un bloque generado y que borrar la marca no sea la salida barata.
    """

    def test_los_equivalentes_se_recortan_al_alcance_pero_se_validan_contra_todo(self) -> None:
        """Un `equivalentes.json` es del proyecto; la ronda puede ser de un archivo. Sin recortar,
        el CI —un objetivo por job— fallaba todos los jobs salvo el del archivo declarado. Sin
        validar contra el inventario completo, una declaración vencida no la miraría nadie."""
        from tools.mutar_codigo import (EQUIVALENTES, RAIZ as RAIZ_MC, cargar_equivalentes,
                                        equivalentes_del_alcance)

        declarados = cargar_equivalentes(EQUIVALENTES)
        self.assertTrue(declarados, "el test necesita al menos un equivalente declarado")
        propio = next(iter(declarados))
        archivo = propio.rsplit(":", 3)[0]

        dentro = equivalentes_del_alcance(declarados, [RAIZ_MC / archivo])
        fuera = equivalentes_del_alcance(declarados, [RAIZ_MC / "nucleo/grafo.py"])
        self.assertIn(propio, dentro)
        self.assertEqual(fuera, {})

    def test_un_equivalente_que_no_apunta_a_ningun_sitio_se_denuncia(self) -> None:
        from tools.mutar_codigo import EquivalenteInvalido, RAIZ as RAIZ_MC, equivalentes_del_alcance

        with self.assertRaisesRegex(EquivalenteInvalido, "no apuntan a ningún sitio"):
            equivalentes_del_alcance(
                {"nucleo/grafo.py:9999:0:constante": "el código que la justificaba ya no existe"},
                [RAIZ_MC / "nucleo/grafo.py"])

    def test_todo_objetivo_de_mutacion_declara_sus_tests_prioritarios(self) -> None:
        """`comando_de_tests` indexa `PRIORIDADES` directo, así que un objetivo sin entrada revienta
        con `KeyError` recién al correr su job del CI. Pasó al sumar `tools/cifras.py`: quedó en la
        matriz y fuera del mapa, y el job habría fallado por una causa que no tenía nada que ver con
        los mutantes."""
        from tools.mutar_codigo import PRIORIDADES, objetivos_disponibles

        faltantes = sorted(set(objetivos_disponibles()) - set(PRIORIDADES))
        self.assertEqual(faltantes, [], "objetivos sin tests prioritarios declarados")

    def test_una_marca_de_apertura_ausente_falla_cerrado(self) -> None:
        from tools import cifras as cli

        with self.assertRaises(ValueError):
            cli.actualizar("sin marcas\n<!-- x:fin -->", "x", "algo")

    def test_una_marca_de_cierre_ausente_falla_cerrado(self) -> None:
        from tools import cifras as cli

        with self.assertRaises(ValueError):
            cli.actualizar("<!-- x:inicio -->\nsin cierre", "x", "algo")

    def test_todo_bloque_declarado_tiene_su_marca_en_el_readme(self) -> None:
        from tools import cifras as cli

        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        for nombre in cli.BLOQUES:
            self.assertIn(f"<!-- {nombre}:inicio -->", readme, nombre)
            self.assertIn(f"<!-- {nombre}:fin -->", readme, nombre)

    def test_la_proporcion_publicada_es_la_que_sale_de_los_archivos(self) -> None:
        """Recalcula el cociente por otra vía: si la fórmula se afloja, esto se cae."""
        from tools import cifras as cli

        # `rglob`, igual que el numerador: un módulo dentro de un subpaquete de `nucleo/` es
        # lenguaje lo mismo que uno suelto, y contarlo sólo si está en la raíz convertía «mover el
        # archivo una carpeta más adentro» en una manera de sacar código del criterio de falsación.
        lineas_lenguaje = sum(
            len(p.read_text(encoding="utf-8").splitlines())
            for p in list((RAIZ / "nucleo").rglob("*.py"))
                   + [x for x in (RAIZ / "nucleo" / "macros").iterdir()
                      if x.suffix in EXTENSIONES_DE_MACRO and x.is_file()]
            if p.name != "__init__.py" and "__pycache__" not in p.parts)
        lineas_medidas = sum(
            len(p.read_text(encoding="utf-8").splitlines())
            for p in cli._medidas_universales())

        esperado = f"{lineas_lenguaje / lineas_medidas:.1f}".replace(".", ",")
        self.assertIn(f"**{esperado} a 1**", cli.escala())
        self.assertIn(f"**{lineas_lenguaje} líneas", cli.escala())

    def test_un_subpaquete_de_nucleo_cuenta_como_lenguaje(self) -> None:
        """Mover un módulo a `nucleo/<subpaquete>/` no puede sacarlo del criterio de falsación.

        Pasó de verdad: 411 líneas del aislamiento de UDF quedaban fuera del numerador y fuera de
        la mutación de código por vivir una carpeta más adentro. El numerador ya contaba
        `nucleo/macros/*.json` por el mismo motivo — sólo faltaba que valiera para los `.py`."""
        from tools import cifras as cli

        contadas = {p.relative_to(RAIZ).as_posix() for p in cli._fuentes_del_nucleo()}
        en_subpaquetes = {
            p.relative_to(RAIZ).as_posix() for p in (RAIZ / "nucleo").rglob("*.py")
            if p.parent != RAIZ / "nucleo" and p.name != "__init__.py"
            and "__pycache__" not in p.parts}
        self.assertTrue(en_subpaquetes, "no hay subpaquetes: el test dejó de ejercitar algo")
        self.assertLessEqual(en_subpaquetes, contadas)

    def _aislado(self, td, contenido, bloque="hola"):
        """`main()` sobre un README temporal y un bloque trivial.

        Se aísla porque lo que hay que ejercitar es su CONTROL DE FLUJO —qué devuelve cuando el
        archivo está al día, cuando venció y cuando se pide actualizar—, no las cifras reales. Sin
        esto, los `return` y las comparaciones de `main()` no los fija nada: la ronda de mutación
        dejó vivos catorce mutantes ahí adentro.
        """
        from tools import cifras as cli

        ruta = Path(td) / "README.md"
        ruta.write_text(contenido, encoding="utf-8")
        return cli, mock.patch.multiple(
            cli, RAIZ=Path(td), BLOQUES={"prueba": lambda: bloque},
            DOCUMENTOS=("README.md",))

    def test_main_devuelve_cero_cuando_el_readme_esta_al_dia(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cli, parche = self._aislado(
                td, "<!-- prueba:inicio -->\nhola\n<!-- prueba:fin -->\n")
            with parche, redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main([]), 0)

    def test_main_devuelve_uno_cuando_una_cifra_vencio(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cli, parche = self._aislado(
                td, "<!-- prueba:inicio -->\nvencido\n<!-- prueba:fin -->\n")
            salida = io.StringIO()
            with parche, redirect_stdout(salida):
                self.assertEqual(cli.main([]), 1)
            self.assertIn("vencidas", salida.getvalue())

    def test_main_con_actualizar_reescribe_el_archivo_y_devuelve_cero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cli, parche = self._aislado(
                td, "<!-- prueba:inicio -->\nvencido\n<!-- prueba:fin -->\n")
            with parche, redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["--actualizar"]), 0)
                self.assertEqual(cli.main([]), 0)
            texto = (Path(td) / "README.md").read_text(encoding="utf-8")
        self.assertIn("hola", texto)
        self.assertNotIn("vencido", texto)

    def test_main_sin_argv_explicito_lee_los_del_proceso(self) -> None:
        """`main(None)` tiene que mirar `sys.argv[1:]`, no la lista entera ni ignorarla."""
        with tempfile.TemporaryDirectory() as td:
            cli, parche = self._aislado(
                td, "<!-- prueba:inicio -->\nvencido\n<!-- prueba:fin -->\n")
            with parche, mock.patch.object(
                    sys, "argv", ["cifras.py", "--actualizar"]), redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(), 0)
            self.assertIn("hola", (Path(td) / "README.md").read_text(encoding="utf-8"))

    def test_main_custodia_todos_los_documentos_declarados(self) -> None:
        """La deriva revivía en los derivados porque el CI vigilaba sólo el README."""
        from tools import cifras as cli

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "README.md").write_text(
                "<!-- prueba:inicio -->\nhola\n<!-- prueba:fin -->\n", encoding="utf-8")
            derivado = Path(td) / "derivado.md"
            derivado.write_text(
                "<!-- prueba:inicio -->\nvencido\n<!-- prueba:fin -->\n", encoding="utf-8")
            parche = mock.patch.multiple(
                cli, RAIZ=Path(td), BLOQUES={"prueba": lambda: "hola"},
                DOCUMENTOS=("README.md", "derivado.md"))
            salida = io.StringIO()
            with parche, redirect_stdout(salida):
                # el README está al día y aun así falla: el derivado también es contrato
                self.assertEqual(cli.main([]), 1)
                self.assertEqual(cli.main(["--actualizar"]), 0)
                self.assertEqual(cli.main([]), 0)
            self.assertIn("derivado.md", salida.getvalue())
            self.assertIn("hola", derivado.read_text(encoding="utf-8"))

    def test_un_documento_declarado_que_no_existe_es_un_error(self) -> None:
        """Borrar el archivo no puede ser la manera de librarse de la medición."""
        from tools import cifras as cli

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "README.md").write_text(
                "<!-- prueba:inicio -->\nhola\n<!-- prueba:fin -->\n", encoding="utf-8")
            parche = mock.patch.multiple(
                cli, RAIZ=Path(td), BLOQUES={"prueba": lambda: "hola"},
                DOCUMENTOS=("README.md", "borrado.md"))
            with parche, redirect_stdout(io.StringIO()):
                with self.assertRaises(FileNotFoundError):
                    cli.main([])

    def test_un_documento_sin_la_marca_no_inventa_el_bloque(self) -> None:
        """No todo documento publica todas las cifras; el que no la marca, no la lleva."""
        from tools import cifras as cli

        with tempfile.TemporaryDirectory() as td:
            cli_, parche = self._aislado(td, "sin ninguna marca\n")
            with parche, redirect_stdout(io.StringIO()):
                self.assertEqual(cli_.main([]), 0)

    def test_todo_documento_custodiado_existe(self) -> None:
        """Lo único que se puede afirmar sin git, y por eso es lo único que afirma este test.

        La comprobación fuerte —que git los siga— vive en `tools/cifras.py`, que corre en el árbol
        real. Estuvo acá y no funcionaba: el arnés de `mutar_codigo.py` copia el proyecto SIN `.git`
        y el test leía ese error de entorno como una falla, dejando la línea base roja y la ronda
        INCONCLUSA. Es el caso `017` del corpus: un error del arnés no es una muerte.
        """
        from tools import cifras as cli

        self.assertTrue(cli.DOCUMENTOS)
        for nombre in cli.DOCUMENTOS:
            with self.subTest(nombre=nombre):
                self.assertTrue((RAIZ / nombre).exists())

    def test_la_herramienta_denuncia_un_documento_que_git_no_sigue(self) -> None:
        """Que la comprobación se haya mudado no la vuelve opcional: acá se ejercita.

        HERMÉTICO: arma su propio repositorio en un temporal en vez de preguntarle al de alrededor.
        Dos intentos anteriores dependían del árbol ambiente y los dos rompieron la línea base de
        `mutar_codigo.py`, que corre sobre una copia SIN `.git`. Un test que necesita el entorno de
        su autor no es un test, es una coincidencia.
        """
        import subprocess
        import tempfile

        from tools import cifras as cli

        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            (raiz / "seguido.md").write_text("x\n", encoding="utf-8")
            (raiz / "generado.md").write_text("y\n", encoding="utf-8")
            for orden in (["init", "-q"], ["add", "seguido.md"]):
                subprocess.run(["git", *orden], cwd=raiz, check=True,
                               capture_output=True, text=True)
            fuera = cli.custodiados_sin_versionar(
                raiz, ("seguido.md", "generado.md"))
            self.assertEqual(fuera, ["generado.md"])

        with tempfile.TemporaryDirectory() as d:
            # Sin repositorio no afirma nada, que es distinto de afirmar que está todo bien: el
            # `main` de la herramienta corre igual y la comprobación fuerte queda para el árbol real.
            self.assertEqual(
                cli.custodiados_sin_versionar(Path(d), ("cualquiera.md",)), [])

    def test_render_aplica_el_bloque_y_devuelve_el_contenido(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cli, parche = self._aislado(td, "")
            with parche:
                salida = cli.render("antes\n<!-- prueba:inicio -->\nx\n<!-- prueba:fin -->\ndespués")
        self.assertIn("antes", salida)
        self.assertIn("hola", salida)
        self.assertIn("después", salida)

    def test_actualizar_conserva_lo_que_rodea_al_bloque(self) -> None:
        from tools import cifras as cli

        salida = cli.actualizar(
            "A\n<!-- x:inicio -->\nviejo\n<!-- x:fin -->\nB", "x", "nuevo")
        self.assertEqual(salida, "A\n<!-- x:inicio -->\nnuevo\n<!-- x:fin -->\nB")

    def test_las_negativas_se_cuentan_una_por_sentencia_raise(self) -> None:
        from tools import cifras as cli

        with tempfile.TemporaryDirectory() as td:
            fuente = Path(td) / "m.py"
            fuente.write_text(
                "def f():\n"
                "    raise ValueError('una')\n"
                "    raise KeyError('dos')\n"
                "# raise en comentario no cuenta\n"
                "x = 'raise dentro de un texto tampoco'\n",
                encoding="utf-8")
            self.assertEqual(cli._negativas([fuente]), 2)

    def test_cada_bloque_produce_texto_no_vacio(self) -> None:
        """Un generador que devuelve `None` deja el bloque vacío y el README diría nada."""
        from tools import cifras as cli

        # `cifras` entra igual que los demás: descubrir la suite y mutar las medidas cuesta 0,1 s.
        # Excluirlo dejaba su `return` sin fijar, y el mutante que lo volvía `None` sobrevivió.
        for nombre, generar in cli.BLOQUES.items():
            with self.subTest(bloque=nombre):
                texto = generar()
                self.assertIsInstance(texto, str)
                self.assertTrue(texto.strip())

    def test_la_cuenta_de_macros_distingue_la_forma_canonica(self) -> None:
        """`por_macro` cuenta las formas que NO son `medida`. Si la comparación se invierte, el
        número pasa a ser el de las canónicas y nadie se entera."""
        from tools import cifras as cli
        from nucleo.medida import cargar_fuente_medida

        canonicas = sum(
            1 for p in cli._medidas_universales()
            if cargar_fuente_medida(p)[0] == "medida")
        total = len(cli._medidas_universales())
        self.assertIn(f"{total - canonicas} de las {total} pasan por una macro", cli.escala())
        self.assertNotEqual(canonicas, total - canonicas, "el test no discrimina si hay empate")

    def test_mover_lenguaje_de_python_a_datos_no_mejora_la_proporcion(self) -> None:
        """La biblioteca estándar de macros dejó de ser Python y pasó a `nucleo/macros/`. Si el
        numerador contara sólo `.py`, ese movimiento habría «mejorado» la proporción sin que el
        lenguaje encogiera nada — el sastreo exacto contra el que esta medición existe.

        Y no se fija por nombre de archivo: cuando las tres macros pasaron de `.json` a `.oracle`,
        una lista de nombres a mano habría hecho fallar el test por el renombre en vez de por lo
        que dice medir. Se fija que TODAS las de la biblioteca estén contadas, en el formato que
        sea, que es la afirmación que importa.
        """
        from tools import cifras as cli

        contadas = {p.name for p in cli._lenguaje()}
        self.assertIn("macro.py", contadas)
        en_disco = {p.name for p in (RAIZ / "nucleo" / "macros").iterdir()
                    if p.suffix in EXTENSIONES_DE_MACRO and p.is_file()}
        self.assertTrue(en_disco)
        self.assertTrue(en_disco <= contadas)

    def test_el_reparto_del_corpus_suma_todos_los_casos(self) -> None:
        from nucleo.caso import rutas_de_corpus
        from tools import cifras as cli

        casos = len(rutas_de_corpus(RAIZ / "corpus"))
        self.assertIn(f"**{casos} casos**", cli.corpus())

    def test_las_dos_secciones_no_pueden_contradecirse_en_las_negativas(self) -> None:
        """`negativas` y `escala` salen de la misma función: el conteo aparece dos veces, medido
        una. Es la lección del caso 012 aplicada a la prosa."""
        from tools import cifras as cli

        negativas = cli._negativas(cli._fuentes_del_nucleo())
        self.assertIn(f"**{negativas} negativas", cli.negativas())
        self.assertIn(f"**{negativas} negativas", cli.escala())

class ContrasteDeLaTraza(unittest.TestCase):
    """Las propiedades del álgebra las juzgan DOS implementaciones, no una.

    Sin esto el evaluador se examinaría solo: un defecto en `donde` podría tapar la medida que
    vigila `donde`. La segunda mano es `diferencial/referencia/evaluador.py`, escrito por otro autor
    que nunca vio `nucleo/`.
    """

    def _juezas_y_evidencia(self):
        from nucleo.medida import cargar_catalogo, medidas_aplicables
        from nucleo.proyecto import catalogos_a_cargar, macros_del_proyecto
        from tools import trazar as cli

        proy = Proyecto(RAIZ)
        catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
        evidencia, _evaluados, _fallidos = cli.hechos(catalogo, cli.casos(proy))
        return cli, medidas_aplicables(catalogo.values(), evidencia), evidencia

    def test_las_dos_implementaciones_coinciden_sobre_la_traza_real(self) -> None:
        cli, juezas, evidencia = self._juezas_y_evidencia()
        self.assertTrue(juezas, "ninguna propiedad se activó con la traza")
        self.assertEqual(cli.contrastar(juezas, evidencia), [])

    def test_un_desacuerdo_se_denuncia_y_no_se_traga(self) -> None:
        """Una comprobación que no puede fallar no comprueba nada."""
        cli, juezas, evidencia = self._juezas_y_evidencia()

        class Discrepante:
            @staticmethod
            def evaluar(medida, _evidencia, _escalares=None):
                return {"ok": False, "valor": 0, "testigos": []}   # nucleo las da verdes

        with mock.patch.object(cli, "cargar_referencia", lambda: Discrepante):
            desacuerdos = cli.contrastar(juezas, evidencia)
            self.assertEqual(len(desacuerdos), len(juezas))
            self.assertIn("nucleo=True vs referencia=False", desacuerdos[0])
            with redirect_stdout(io.StringIO()) as salida:
                self.assertEqual(cli.main([]), 1)
            self.assertIn("DESACUERDO", salida.getvalue())

    def test_una_referencia_que_revienta_cuenta_como_desacuerdo(self) -> None:
        """No se puede aprobar por incomparecencia: si la referencia no evalúa, eso es el hallazgo."""
        cli, juezas, evidencia = self._juezas_y_evidencia()

        class Rota:
            @staticmethod
            def evaluar(*_a, **_k):
                raise RuntimeError("no evalúa")

        with mock.patch.object(cli, "cargar_referencia", lambda: Rota):
            desacuerdos = cli.contrastar(juezas, evidencia)
        self.assertEqual(len(desacuerdos), len(juezas))
        self.assertIn("RuntimeError", desacuerdos[0])


class VersionDelAlgebra(unittest.TestCase):
    """El número del lenguaje es un dato legible por máquina, y su lectura falla cerrada.

    La especificación lo declaraba «en prosa» y el núcleo no lo conocía: una extensión apagaba en
    silencio un pedazo del diferencial. Estos tests fijan que la versión vive en un solo lugar y que
    compararla nunca produce un `False` callado.
    """

    def test_el_nucleo_declara_una_version_legible_y_estable(self) -> None:
        from nucleo.version import VERSION_ALGEBRA, del_nucleo

        self.assertEqual(str(del_nucleo()), VERSION_ALGEBRA)
        self.assertEqual(str(del_nucleo()), "0.5")

    def test_la_superficie_declara_su_propia_version_legible_y_estable(self) -> None:
        from nucleo.version import VERSION_SINTAXIS, del_nucleo_sintaxis

        self.assertEqual(str(del_nucleo_sintaxis()), VERSION_SINTAXIS)
        self.assertEqual(str(del_nucleo_sintaxis()), "0.1")

    def test_parsear_acepta_mayor_menor_y_rechaza_lo_demas(self) -> None:
        from nucleo.version import Version, VersionInvalida, parsear

        self.assertEqual(parsear("0.3"), Version(0, 3))
        self.assertEqual(parsear("10.20"), Version(10, 20))
        for malo in (3, None, ["0.3"], "", "3", "0", "0.3.1", "a.b", "0.3-beta",
                      "01.2", "-1.0", "0."):
            with self.subTest(malo=malo):
                with self.assertRaises(VersionInvalida):
                    parsear(malo)

    def test_version_es_inmutable(self) -> None:
        from dataclasses import FrozenInstanceError
        from nucleo.version import Version

        v = Version(1, 2)
        with self.assertRaises(FrozenInstanceError):
            v.mayor = 3
        with self.assertRaises(FrozenInstanceError):
            v.menor = 4

    def test_compatible_exige_la_misma_mayor_y_menor_al_menos_pedida(self) -> None:
        from nucleo.version import compatible, parsear

        self.assertTrue(compatible(parsear("0.3"), parsear("0.3")))
        self.assertTrue(compatible(parsear("0.2"), parsear("0.3")))
        self.assertTrue(compatible(parsear("0.3"), parsear("0.4")))
        self.assertFalse(compatible(parsear("0.4"), parsear("0.3")))
        self.assertFalse(compatible(parsear("1.0"), parsear("0.9")))
        self.assertFalse(compatible(parsear("0.9"), parsear("1.0")))



class VersionDelProyecto(unittest.TestCase):
    """Un consumidor declara qué versión necesita; si no coincide, falla con un mensaje útil.

    Quien no declara versión sigue funcionando: no se rompe a un proyecto que ya existía.
    """

    def _raiz(self, base: str) -> Path:
        raiz = Path(base)
        (raiz / "catalogos").mkdir()
        return raiz

    def _configurar(self, raiz: Path, datos) -> None:
        (raiz / "oracle.json").write_text(json.dumps(datos), encoding="utf-8")

    def test_sin_oracle_json_o_sin_algebra_el_proyecto_sigue_andando(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            self.assertEqual(configuracion(Proyecto(raiz)), ConfiguracionProyecto())

        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            self._configurar(raiz, {"esquema": "oracle.proyecto/v1", "perfiles": []})
            self.assertEqual(configuracion(Proyecto(raiz)).perfiles, ())

    def test_una_version_compatible_carga_sin_queja(self) -> None:
        for declarada in ("0.2", "0.3", "0.4", "0.5"):
            with self.subTest(declarada=declarada), tempfile.TemporaryDirectory() as td:
                raiz = self._raiz(td)
                self._configurar(raiz, {"esquema": "oracle.proyecto/v1",
                                        "algebra": declarada, "perfiles": []})
                self.assertEqual(configuracion(Proyecto(raiz)).perfiles, ())

    def test_una_version_incompatible_falla_diciendo_cual_hay_y_cual_se_pidio(self) -> None:
        for declarada in ("0.6", "1.0", "9.9"):
            with self.subTest(declarada=declarada), tempfile.TemporaryDirectory() as td:
                raiz = self._raiz(td)
                self._configurar(raiz, {"esquema": "oracle.proyecto/v1",
                                        "algebra": declarada, "perfiles": []})
                with self.assertRaises(ProyectoInvalido) as ctx:
                    configuracion(Proyecto(raiz))
                self.assertIn(declarada, str(ctx.exception))
                self.assertIn("0.5", str(ctx.exception))

    def test_una_version_mal_declarada_falla_cerrado(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            self._configurar(raiz, {"esquema": "oracle.proyecto/v1",
                                    "algebra": "no-es-version", "perfiles": []})
            with self.assertRaises(ProyectoInvalido):
                configuracion(Proyecto(raiz))

    def test_el_oracle_de_si_mismo_declara_una_version_compatible(self) -> None:
        # El `oracle.json` del propio proyecto carga sin queja: su declaración no es ajena al núcleo.
        self.assertEqual(configuracion(Proyecto(RAIZ)).catalogo_base, True)

    def test_una_sintaxis_compatible_carga_sin_queja(self) -> None:
        for declarada in ("0.0", "0.1"):
            with self.subTest(declarada=declarada), tempfile.TemporaryDirectory() as td:
                raiz = self._raiz(td)
                self._configurar(raiz, {"esquema": "oracle.proyecto/v1",
                                        "sintaxis": declarada, "perfiles": []})
                self.assertEqual(configuracion(Proyecto(raiz)).perfiles, ())

    def test_una_sintaxis_incompatible_falla_diciendo_cual_hay_y_cual_se_pidio(self) -> None:
        for declarada in ("0.2", "1.0", "9.9"):
            with self.subTest(declarada=declarada), tempfile.TemporaryDirectory() as td:
                raiz = self._raiz(td)
                self._configurar(raiz, {"esquema": "oracle.proyecto/v1",
                                        "sintaxis": declarada, "perfiles": []})
                with self.assertRaises(ProyectoInvalido) as ctx:
                    configuracion(Proyecto(raiz))
                self.assertIn(declarada, str(ctx.exception))
                self.assertIn("0.1", str(ctx.exception))

    def test_una_sintaxis_mal_declarada_falla_cerrado(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = self._raiz(td)
            self._configurar(raiz, {"esquema": "oracle.proyecto/v1",
                                    "sintaxis": "no-es-version", "perfiles": []})
            with self.assertRaises(ProyectoInvalido):
                configuracion(Proyecto(raiz))


class VersionDeLaReferencia(unittest.TestCase):
    """La implementación de referencia declara contra qué versión se escribió, y el arnés la compara.

    Es el caso que motivó todo: agregar `requiere` y `clave` invalidó en silencio a un evaluador
    anterior, y el contraste seguía publicando «0 desacuerdos» porque los fixtures no lo ejercitaban.
    """

    def test_la_referencia_versionada_coincide_con_el_nucleo(self) -> None:
        from types import SimpleNamespace

        from nucleo.diferencial import comprobar_version_referencia
        from tools import generar_diferencial as gen

        referencia = gen.cargar_referencia()
        self.assertEqual(comprobar_version_referencia(referencia), [])

    def test_una_referencia_desfasada_o_muda_se_denuncia(self) -> None:
        from types import SimpleNamespace

        from nucleo.diferencial import comprobar_version_referencia

        for declarada in (None, "0.2", "1.0", "no-version"):
            with self.subTest(declarada=declarada):
                problemas = comprobar_version_referencia(
                    SimpleNamespace(VERSION_ALGEBRA=declarada))
                self.assertTrue(problemas)

    def test_el_arnes_del_diferencial_aborta_ante_una_referencia_desfasada(self) -> None:
        from nucleo.medida import cargar_catalogo
        from nucleo.proyecto import catalogos_a_cargar, macros_del_proyecto
        from tools import generar_diferencial as gen

        proy = Proyecto(RAIZ)
        catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))

        class ReferenciaVieja:
            VERSION_ALGEBRA = "0.2"

        with mock.patch.object(gen, "cargar_referencia", lambda: ReferenciaVieja):
            with self.assertRaises(SystemExit) as ctx:
                gen.construir(catalogo)
        self.assertIn("0.2", str(ctx.exception))
        self.assertIn("0.5", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
