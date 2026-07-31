"""Regresiones fail-closed de las herramientas de línea de comandos."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo.diferencial import Procedencia, crear_frescura
from nucleo.fixtures import cargar_fixtures, evidencias as evidencias_fixture
from nucleo.medida import Medida
from nucleo import algebra
from nucleo.proyecto import (EscalaresInvalidas, Proyecto, escalares_del_proyecto,
                             sin_bandera)
from tools.corpus import revisar_estado_sin_medida, revisar_evidencia
from tools.diferencial import comparar_dominio, validar_fixture


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
                    f"@escalar('{nombre}', 'unidad')\n"
                    f"def funcion(x={valor}): return x\n",
                    encoding="utf-8")
                with escalares_del_proyecto(Proyecto(proyecto), confiar=True):
                    fn = algebra.ESCALARES[nombre]
                    self.assertEqual(fn(), valor)
                    self.assertEqual((fn.aridad_min, fn.aridad_max), (0, 1))
                    self.assertEqual(fn.unidad, "unidad")
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
        r = subprocess.run(
            [sys.executable, str(RAIZ / "tools" / "mutar_codigo.py"),
             "--hechos", "--timeout", "0.001"],
            cwd=RAIZ, capture_output=True, text=True)

        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        datos = json.loads(r.stdout)
        self.assertEqual(datos["error_mutacion"][0]["tipo"], "LineaBaseFallida")
        self.assertIn("timeout", datos["error_mutacion"][0]["mensaje"])
        self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_la_mutacion_de_codigo_incluye_el_perfil_y_particiona_sin_escapar(self) -> None:
        from tools import mutar_codigo as cli

        disponibles = cli.objetivos_disponibles()
        self.assertIn("nucleo/algebra.py", disponibles)
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


if __name__ == "__main__":
    unittest.main()
