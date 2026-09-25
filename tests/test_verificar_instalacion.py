"""Contratos rápidos del verificador instalado; ningún test construye un wheel real."""

import io
import json
import os
import tarfile
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import importlib

vi = None
from nucleo.version import VERSION_DISTRIBUCION


class FuncionesDelVerificador(unittest.TestCase):
    def setUp(self):
        global vi
        vi = importlib.import_module("tools.verificar_instalacion")
        self.assertEqual(Path(vi.__file__).resolve(), Path.cwd() / "tools" / "verificar_instalacion.py")
        self.assertEqual(__import__("sys").path[0], str(Path.cwd()))

    def test_metadata_exige_version_y_tag_sin_enlaces_a_main(self):
        tag = f"https://github.com/Segtem/oracle/blob/v{VERSION_DISTRIBUCION}/"
        valida = f"Version: {VERSION_DISTRIBUCION}\n{tag}NOTAS-DE-RELEASE.md\n"
        vi._comprobar_enlaces(valida, "prueba")
        for mala in (valida.replace(VERSION_DISTRIBUCION, "0.0.0", 1),
                     valida.replace("NOTAS-DE-RELEASE.md", "otro.md"),
                     valida + "github.com/Segtem/oracle/blob/main/README.md",
                     valida + "github.com/Segtem/oracle/tree/main/docs"):
            with self.subTest(mala=mala), self.assertRaisesRegex(RuntimeError, "prueba"):
                vi._comprobar_enlaces(mala, "prueba")

    def test_entorno_quita_solo_contaminacion_y_evitar_bytecode(self):
        with mock.patch.dict(os.environ, {"ORACLE_PROYECTO": "sucio", "PYTHONPATH": "sucio",
                                          "VARIABLE_TESTIGO": "valor"}):
            env = vi._entorno_limpio()
        self.assertNotIn("ORACLE_PROYECTO", env)
        self.assertNotIn("PYTHONPATH", env)
        self.assertEqual(env["VARIABLE_TESTIGO"], "valor")
        self.assertEqual(env["PYTHONDONTWRITEBYTECODE"], "1")

    def test_correr_rechaza_cualquier_codigo_no_cero_y_conserva_salida(self):
        for codigo in (0, 1, 2, -9):
            respuesta = SimpleNamespace(returncode=codigo, stdout="salida", stderr="error")
            with self.subTest(codigo=codigo), mock.patch.object(vi.subprocess, "run", return_value=respuesta) as run:
                if codigo:
                    with self.assertRaisesRegex(RuntimeError, "salida.*"):
                        vi._correr(["prog", "arg"], cwd=Path("/tmp"), env={"A": "B"})
                else:
                    self.assertIs(vi._correr(["prog", "arg"], cwd=Path("/tmp"), env={"A": "B"}), respuesta)
                run.assert_called_once_with(["prog", "arg"], cwd=Path("/tmp"), env={"A": "B"},
                                            capture_output=True, text=True)

    def test_entry_points_salen_del_pyproject_declarado(self):
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "pyproject.toml").write_text('[project.scripts]\nzeta="a:b"\nalfa="a:c"\n')
            with mock.patch.object(vi, "RAIZ", raiz):
                self.assertEqual(vi._entry_points_declarados(), ["alfa", "zeta"])

    def test_lsp_envia_tres_mensajes_y_exige_capacidades(self):
        bueno = b"capabilities codeLensProvider completionProvider"
        def llamar(salida=bueno, codigo=0):
            with mock.patch.object(vi.subprocess, "run", return_value=SimpleNamespace(
                    returncode=codigo, stdout=salida, stderr=b"fallo")) as run:
                if codigo or salida != bueno:
                    with self.assertRaises(RuntimeError):
                        vi._hablarle_al_lsp(Path("oracle-lsp"), proyecto=Path("proyecto"),
                                            cwd=Path("cwd"), env={})
                else:
                    vi._hablarle_al_lsp(Path("oracle-lsp"), proyecto=Path("proyecto"),
                                       cwd=Path("cwd"), env={})
                args, kwargs = run.call_args
                self.assertEqual(args[0], ["oracle-lsp", "--proyecto", "proyecto"])
                self.assertEqual(kwargs["timeout"], 120)
                entrada = kwargs["input"]
                self.assertEqual(entrada.count(b"Content-Length:"), 3)
                self.assertIn(b'"method": "initialize"', entrada)
                self.assertIn(b'"method": "shutdown"', entrada)
                self.assertIn(b'"method": "exit"', entrada)
                self.assertIn(b'"id": 1', entrada)
                self.assertIn(b'"id": 2', entrada)
                self.assertEqual(kwargs["capture_output"], True)
        llamar()
        llamar(codigo=1)
        with mock.patch.object(vi.subprocess, "run", return_value=SimpleNamespace(
                returncode=0, stdout=b"sin capacidades" + b"x" * 800, stderr=b"")):
            with self.assertRaisesRegex(RuntimeError, "STDOUT:") as error:
                vi._hablarle_al_lsp(Path("oracle-lsp"), proyecto=Path("proyecto"), cwd=Path("cwd"), env={})
            self.assertLessEqual(len(str(error.exception).split("STDOUT:\n", 1)[1]), 600)
        for capacidad in (b"capabilities", b"codeLensProvider", b"completionProvider"):
            llamar(salida=bueno.replace(capacidad, b"ausente"))


class RondaSinConstruccion(unittest.TestCase):
    """El artefacto mínimo se crea en milisegundos y cada mutante lo usa una vez."""
    def setUp(self):
        global vi
        vi = importlib.import_module("tools.verificar_instalacion")
        self.assertEqual(Path(vi.__file__).resolve(), Path.cwd() / "tools" / "verificar_instalacion.py")
        self.assertEqual(__import__("sys").path[0], str(Path.cwd()))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        plantilla = self.raiz / "ejemplo" / "sensor-prosa"
        plantilla.mkdir(parents=True)
        (plantilla / "README.md").write_bytes(b"plantilla")
        (plantilla / "__init__.py").write_bytes(b"omitido")
        (plantilla / "__pycache__").mkdir()
        (plantilla / "__pycache__" / "x.pyc").write_bytes(b"omitido")
        self.llamadas = []
        self.respuestas = {}
        self.rechazo = SimpleNamespace(returncode=2, stdout="--proyecto", stderr="")
        self.entries = ["oracle", "oracle-lsp", "oracle-medida", "oracle-aceptacion"]
        self.extra_genericos = []

    def _copiar(self, _origen, destino, **_kwargs):
        Path(destino).mkdir()

    def _venv(self, entorno):
        (Path(entorno) / "bin").mkdir(parents=True)

    def _correr(self, args, *, cwd, env):
        args = list(map(str, args))
        self.llamadas.append((args, Path(cwd), dict(env)))
        if len(args) > 1 and args[1] == "init":
            (Path(args[2]) / "catalogos").mkdir(parents=True)
            (Path(args[2]) / "relaciones").mkdir()
            (Path(args[2]) / "corpus").mkdir()
        if "wheel" in args:
            ruedas = Path(args[args.index("--wheel-dir") + 1])
            with zipfile.ZipFile(ruedas / "oracle_metalenguaje-1.whl", "w") as wheel:
                wheel.writestr("oracle_metalenguaje-1.dist-info/METADATA", "Version: 1")
                wheel.writestr("oracle_metalenguaje/plantilla_sensor_prosa/README.md", b"plantilla")
                for generico in self.extra_genericos:
                    wheel.writestr(generico, b"x")
                for nombre in ("nucleo/algebra.py", "tools/cli.py",
                               "nucleo/aislamiento/escalares.py", "nucleo/macros/ninguno.oracle",
                               "nucleo/macros/ninguno-par.oracle", "nucleo/macros/ninguno-requiere.oracle",
                               "nucleo/macros/peor.oracle",
                               "catalogos/meta/meta.toda_medida_esta_fijada.oracle",
                               "perfiles/python/catalogos/proceso/proceso.arnes_con_bytecode_frio.oracle"):
                    wheel.writestr("oracle_metalenguaje/" + nombre, b"x")
        if "build_sdist" in " ".join(args):
            path = Path(cwd) / "distribuciones" / "oracle_metalenguaje-1.tar.gz"
            with tarfile.open(path, "w:gz") as tar:
                data = b"Version: 1"
                info = tarfile.TarInfo("oracle_metalenguaje-1/PKG-INFO")
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
                extra = tarfile.TarInfo("anidado/otro/PKG-INFO")
                extra.size = len(data)
                tar.addfile(extra, io.BytesIO(data))
                extra_dos = tarfile.TarInfo("anidado/tercero/PKG-INFO")
                extra_dos.size = len(data)
                tar.addfile(extra_dos, io.BytesIO(data))
        comando = tuple(args[1:])
        salida = self.respuestas.get(comando, "")
        if "--escalares" in args:
            salida = self.respuestas.get("inventario", "doble_instalado")
        elif args[-2:] == ["test", "--rapido"]:
            salida = "VEREDICTO: VERDE"
        elif "test" in args and "--rapido" in args:
            salida = self.respuestas.get("macro", "VEREDICTO: VERDE")
        elif "test" in args:
            salida = self.respuestas.get("vacio", "VEREDICTO: SIN MEDICIÓN · proyecto vacío")
        elif "manual" in args:
            salida = self.respuestas.get("html" if "--html" in args else "manual",
                "<!doctype html><dl>" if "--html" in args else
                "OPERADORES — SEGUN — VERBOS — oracle medida")
        if "motor_a" in " ".join(args):
            fuente = Path(cwd).parent
            self.assertEqual(json.loads((fuente / "perfiles-host" / "smoke_externo" / "catalogos" / "demo.instalado.json").read_text())[4][2], 10)
            self.assertTrue(json.loads((fuente / "proyecto-empaquetado" / "oracle.json").read_text())["catalogo_base"])
        return SimpleNamespace(returncode=0, stdout=salida, stderr="")

    def ejecutar(self):
        with mock.patch.object(vi, "RAIZ", self.raiz), \
             mock.patch.object(vi.shutil, "copytree", side_effect=self._copiar), \
             mock.patch.object(vi.venv.EnvBuilder, "__init__", return_value=None) as constructor, \
             mock.patch.object(vi.venv.EnvBuilder, "create", side_effect=self._venv), \
             mock.patch.object(vi, "_correr", side_effect=self._correr), \
             mock.patch.object(vi, "_comprobar_enlaces") as enlaces, \
             mock.patch.object(vi, "_entry_points_declarados", return_value=self.entries), \
             mock.patch.object(vi, "_recorrer_plantilla") as plantilla, \
             mock.patch.object(vi, "_recorrer_tareas") as tareas, \
             mock.patch.object(vi, "_hablarle_al_lsp") as lsp, \
             mock.patch.object(vi.subprocess, "run", return_value=self.rechazo) as run, \
             redirect_stdout(io.StringIO()) as stdout:
            resultado = vi.main()
        self.assertEqual(enlaces.call_count, 2)
        constructor.assert_called_once_with(with_pip=True)
        self.assertEqual(run.call_args.kwargs["capture_output"], True)
        self.assertEqual(run.call_args.kwargs["text"], True)
        plantilla.assert_called_once()
        tareas.assert_called_once()
        lsp.assert_called_once()
        return resultado, stdout.getvalue()

    def test_recorrido_completo_y_argumentos_criticos(self):
        codigo, salida = self.ejecutar()
        self.assertEqual(codigo, 0)
        self.assertIn("WHEEL OK", salida)
        comandos = [args for args, _cwd, _env in self.llamadas]
        self.assertTrue(any("--no-build-isolation" in a and "--no-deps" in a for a in comandos))
        self.assertTrue(any("--target" in a and "--no-deps" in a for a in comandos))
        self.assertTrue(any("from tools.referencias import VALOR" in " ".join(a) for a in comandos))
        self.assertTrue(any("motor_b" in " ".join(a) and "motor_empaquetado" in " ".join(a) for a in comandos))
        self.assertTrue(any("--help" in a for a in comandos))
        self.assertTrue(any(a[0].endswith("/bin/python") for a in comandos))
        self.assertTrue(all(a[0].find("/bin/") >= 0 for a in comandos if "--help" in a))
        self.assertTrue(any("--rapido" in a for a in comandos))
        self.assertTrue(any(env.get("PYTHONPATH", "").endswith("vendorizado")
                            for _args, _cwd, env in self.llamadas))

    def test_rechaza_diagnosticos_y_salidas_falsamente_verdes(self):
        casos = [({"inventario": "sin UDF"}, "UDF"),
                 ({"vacio": "VEREDICTO: VERDE"}, "recién inicializado"),
                 ({"vacio": "VEREDICTO: SIN MEDICIÓN"}, "recién inicializado"),
                 ({"vacio": "proyecto vacío"}, "recién inicializado"),
                 ({"macro": "VEREDICTO: ROJO"}, "macro estándar"),
                 ({"manual": "OPERADORES — SEGUN — VERBOS —"}, "VERBOS"),
                 ({"html": "<dl>"}, "página")]
        for respuestas, error in casos:
            with self.subTest(respuestas=respuestas):
                self.respuestas = respuestas
                with self.assertRaisesRegex(RuntimeError, error):
                    self.ejecutar()
        self.respuestas = {}
        for respuesta in (SimpleNamespace(returncode=0, stdout="--proyecto", stderr=""),
                          SimpleNamespace(returncode=2, stdout="sin proyecto", stderr=""),
                          SimpleNamespace(returncode=2, stdout="--proyecto", stderr="Traceback")):
            with self.subTest(respuesta=respuesta):
                self.rechazo = respuesta
                with self.assertRaisesRegex(RuntimeError, "sin corpus"):
                    self.ejecutar()

    def test_exige_dos_entry_points(self):
        self.entries = ["oracle"]
        with self.assertRaisesRegex(RuntimeError, "entry points"):
            self.ejecutar()

    def test_diagnostico_de_paquetes_genericos_se_acota_a_cinco(self):
        self.extra_genericos = [f"tools/intruso_{i}.py" for i in range(6)]
        with self.assertRaisesRegex(RuntimeError, "paquetes genéricos") as error:
            self.ejecutar()
        self.assertIn("intruso_4.py", str(error.exception))
        self.assertNotIn("intruso_5.py", str(error.exception))

    def test_dos_entry_points_son_suficientes(self):
        self.entries = ["oracle", "oracle-lsp"]
        self.ejecutar()


class TrackerInstalado(unittest.TestCase):
    def setUp(self):
        global vi
        vi = importlib.import_module("tools.verificar_instalacion")
        self.assertEqual(Path(vi.__file__).resolve(), Path.cwd() / "tools" / "verificar_instalacion.py")
        self.assertEqual(__import__("sys").path[0], str(Path.cwd()))

    def test_recorrido_tracker_con_cli_real_y_proyecto_aislado(self):
        import sys
        with tempfile.TemporaryDirectory() as td:
            temporal = Path(td)
            oracle = temporal / "oracle"
            oracle.write_text(f'#!/bin/sh\nexec {sys.executable} -B {vi.RAIZ / "tools" / "cli.py"} "$@"\n')
            oracle.chmod(0o755)
            env = vi._entorno_limpio()
            env["GIT_INDEX_FILE"] = str(temporal / "índice-inexistente")
            vi._recorrer_tareas(oracle, temporal=temporal, env=env)


class PlantillaInstalada(unittest.TestCase):
    def setUp(self):
        global vi
        vi = importlib.import_module("tools.verificar_instalacion")
        self.assertEqual(Path(vi.__file__).resolve(), Path.cwd() / "tools" / "verificar_instalacion.py")
        self.assertEqual(__import__("sys").path[0], str(Path.cwd()))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.temporal = Path(self.tmp.name)
        self.recursos = {"README.md": (b"Inicio\n```bash\n"
                        b"oracle plantilla sensor-prosa prosa\n"
                        b"cd prosa\npython sensor_prosa.py correr\n"
                        b"oracle test --rapido\n```\n"), "sensor_prosa.py": b"codigo"}
        self.salidas = []
        self.repetido = SimpleNamespace(returncode=1, stdout="", stderr="")

    def _correr(self, args, *, cwd, env):
        self.salidas.append((args, cwd))
        if "plantilla" in args:
            destino = self.temporal / "consumidor prosa á" / "prosa"
            destino.mkdir()
            for nombre, contenido in self.recursos.items():
                (destino / nombre).write_bytes(contenido)
            return SimpleNamespace(stdout="OPENROUTER_API_KEY sensor_prosa.py correr oracle juzgar")
        if "correr" in args:
            (cwd / "preparada").mkdir()
            (cwd / "hechos-construidos.json").write_text("{}")
        return SimpleNamespace(stdout="VEREDICTO: VERDE")

    def test_readme_ejecuta_comandos_y_rechaza_destino_ya_existente(self):
        with mock.patch.object(vi, "_correr", side_effect=self._correr), \
             mock.patch.object(vi.subprocess, "run", return_value=self.repetido) as run:
            vi._recorrer_plantilla(Path("oracle"), Path("python"), temporal=self.temporal,
                                  env={}, recursos=self.recursos)
        self.assertEqual(len(self.salidas), 3)
        self.assertEqual([a[0][0] for a in self.salidas], ["oracle", "python", "oracle"])
        self.assertEqual(run.call_args.kwargs["cwd"], self.temporal / "consumidor prosa á")
        self.assertEqual(run.call_args.kwargs["capture_output"], True)
        self.assertEqual(run.call_args.kwargs["text"], True)

    def test_exige_cada_artefacto_del_readme(self):
        for quitar in ("preparada", "hechos-construidos.json"):
            with self.subTest(quitar=quitar):
                self.setUp()
                original = self._correr
                def correr(args, *, cwd, env):
                    resultado = original(args, cwd=cwd, env=env)
                    if "correr" in args:
                        objetivo = cwd / quitar
                        if objetivo.is_dir():
                            objetivo.rmdir()
                        else:
                            objetivo.unlink()
                    return resultado
                with mock.patch.object(vi, "_correr", side_effect=correr), \
                     mock.patch.object(vi.subprocess, "run", return_value=self.repetido):
                    with self.assertRaisesRegex(RuntimeError, "artefactos"):
                        vi._recorrer_plantilla(Path("oracle"), Path("python"), temporal=self.temporal,
                                              env={}, recursos=self.recursos)

    def test_no_acepta_segunda_copia_exitosa(self):
        self.repetido = SimpleNamespace(returncode=0, stdout="", stderr="")
        with mock.patch.object(vi, "_correr", side_effect=self._correr), \
             mock.patch.object(vi.subprocess, "run", return_value=self.repetido):
            with self.assertRaisesRegex(RuntimeError, "destino existente"):
                vi._recorrer_plantilla(Path("oracle"), Path("python"), temporal=self.temporal,
                                      env={}, recursos=self.recursos)


class TrackerConRespuestasConstruidas(unittest.TestCase):
    def setUp(self):
        global vi
        vi = importlib.import_module("tools.verificar_instalacion")
        self.assertEqual(Path(vi.__file__).resolve(), Path.cwd() / "tools" / "verificar_instalacion.py")
        self.assertEqual(__import__("sys").path[0], str(Path.cwd()))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.temporal = Path(self.tmp.name)
        self.proyecto = self.temporal / "tareas consumidor á"
        self.ruta = self.proyecto / "tareas" / "20260101-000000-prueba" / "TAREA.md"
        self.original = None
        self.seguimiento = 0
        self.resumen = 0
        self.listar = 0
        self.nueva = 0
        self.resultado_juzgar = SimpleNamespace(returncode=1, stdout="ausente-p3.txt", stderr="")
        self.resultado_invalido = SimpleNamespace(returncode=2, stdout="", stderr="^ error")
        self.alterar = None

    def _respuesta(self, args, *, cwd, env):
        args = list(map(str, args))
        if args[0] == "git":
            return SimpleNamespace(stdout="", stderr="")
        accion = args[2] if len(args) > 2 and args[1] == "tarea" else args[1]
        salida = ""
        if accion == "init":
            (self.proyecto / "tareas").mkdir()
        elif accion == "nueva":
            self.nueva += 1
            identidad = "20260101-000000-prueba" if self.nueva == 1 else "20260101-000001-otra"
            ruta = self.proyecto / "tareas" / identidad / "TAREA.md"
            ruta.parent.mkdir()
            ruta.write_text("Estado: ABIERTA\nCita: ABIERTA\n")
            salida = json.dumps({"id": identidad})
        elif accion == "ls":
            salida = json.dumps([{"id": "20260101-000000-prueba"}])
        elif accion == "ver":
            salida = str(self.ruta)
        elif accion == "cerrar":
            self.original = self.ruta.read_bytes()
            self.ruta.write_bytes(self.original.replace(b"ABIERTA", b"CERRADA", 1))
        elif accion == "listar":
            self.listar += 1
            salida = json.dumps([] if self.listar == 1 else [{"id": "20260101-000000-prueba"}])
        elif accion == "reabrir":
            self.ruta.write_bytes(self.original)
        elif accion == "anotar":
            with self.ruta.open("a") as f:
                f.write("Hallazgo del recorrido instalado " + args[args.index("--url") + 1])
        elif accion == "adjuntar":
            origen = Path(args[4])
            destino = self.ruta.parent / origen.name
            destino.write_bytes(origen.read_bytes())
            salida = json.dumps({"ruta": str(destino)})
        elif accion == "buscar":
            salida = json.dumps({"coincidencias": [1]})
        elif accion == "referencias":
            salida = json.dumps({"coincidencias": [{"ruta": "src/detalle/solucion.py"}]})
        elif accion == "resumen":
            self.resumen += 1
            salida = json.dumps({"total": 1, "descripcion": "Descripción instalada á"})
        elif accion == "seguimiento":
            self.seguimiento += 1
            datos = [dict(en_indice=False, en_head=False, estado="local"),
                     dict(en_indice=True, en_head=False, estado="en_indice"),
                     dict(en_indice=True, en_head=True, estado="sin_cambios")]
            salida = json.dumps({"archivos": [datos[self.seguimiento - 1]]})
        elif accion == "hechos":
            salida = json.dumps({"tarea_seguimiento": [1], "lectura_seguimiento": [{"completa": True}]})
        elif accion == "etiquetar":
            self.antes_etiqueta = self.ruta.read_bytes()
            self.ruta.write_bytes(self.antes_etiqueta + b"instalado")
        elif accion == "desetiquetar":
            self.ruta.write_bytes(self.antes_etiqueta)
        elif accion == "grafo":
            salida = (json.dumps({"aristas": [{"origen": "20260101-000001-otra",
                                                 "destino": "20260101-000000-prueba"}]})
                      if "--json" in args else "digraph { a -> b }")
        respuesta = SimpleNamespace(stdout=salida, stderr="", returncode=0)
        if self.alterar is not None:
            respuesta = self.alterar(accion, respuesta, args)
        return respuesta

    def ejecutar(self):
        corridas = [self.resultado_juzgar, self.resultado_invalido]
        def run(*_a, **_kw):
            return corridas.pop(0)
        with mock.patch.object(vi, "_correr", side_effect=self._respuesta), \
             mock.patch.object(vi.subprocess, "run", side_effect=run), \
             mock.patch.object(vi.shutil, "which", return_value="git"):
            vi._recorrer_tareas(Path("oracle"), temporal=self.temporal, env={"GIT_INDEX_FILE": "sucio"})

    def test_recorrido_con_respuestas_minimas(self):
        self.ejecutar()
        self.assertEqual(self.seguimiento, 3)

    def test_rechaza_respuestas_parciales_aunque_la_otra_condicion_siga_verde(self):
        casos = [
            ("ls", lambda r: json.dumps([{"id": "otro"}]), "subcarpeta"),
            ("reabrir", lambda r: r, "texto o adjuntos"),
            ("anotar", lambda r: r, "contexto previo"),
            ("adjuntar", lambda r: r, "archivo de origen"),
            ("hechos", lambda r: json.dumps({"tarea_seguimiento": [1],
                                              "lectura_seguimiento": [{"completa": False}]}), "P1/P2"),
        ]
        for accion_objetivo, cambiar, error in casos:
            with self.subTest(accion=accion_objetivo):
                self.setUp()
                def alterar(accion, respuesta, args):
                    if accion == accion_objetivo:
                        if accion == "reabrir":
                            (self.ruta.parent / "captura.png").write_bytes(b"roto")
                        elif accion == "anotar":
                            self.ruta.write_bytes(b"nota " + args[args.index("--url") + 1].encode())
                        elif accion == "adjuntar":
                            copia = Path(json.loads(respuesta.stdout)["ruta"])
                            copia.write_bytes(b"roto")
                        else:
                            respuesta.stdout = cambiar(respuesta)
                    return respuesta
                self.alterar = alterar
                with self.assertRaisesRegex(RuntimeError, error):
                    self.ejecutar()

    def test_seguimiento_rechaza_cada_estado_parcial(self):
        casos = [
            (1, dict(en_indice=True, en_head=False, estado="local"), "archivos locales"),
            (2, dict(en_indice=False, en_head=False, estado="local"), "índice de HEAD"),
            (3, dict(en_indice=True, en_head=False, estado="sin_cambios"), "contenido confirmado"),
        ]
        for numero, dato, error in casos:
            with self.subTest(numero=numero, dato=dato):
                self.setUp()
                def alterar(accion, respuesta, _args):
                    if accion == "seguimiento" and self.seguimiento == numero:
                        respuesta.stdout = json.dumps({"archivos": [dato]})
                    return respuesta
                self.alterar = alterar
                with self.assertRaisesRegex(RuntimeError, error):
                    self.ejecutar()

    def test_rechazo_exige_codigo_y_testigo_y_consulta_invalida_exige_posicion(self):
        for respuesta in (SimpleNamespace(returncode=0, stdout="ausente-p3.txt", stderr=""),
                          SimpleNamespace(returncode=1, stdout="sin testigo", stderr="")):
            with self.subTest(respuesta=respuesta):
                self.setUp()
                self.resultado_juzgar = respuesta
                with self.assertRaisesRegex(RuntimeError, "enlace roto"):
                    self.ejecutar()
        for respuesta in (SimpleNamespace(returncode=0, stdout="", stderr="^"),
                          SimpleNamespace(returncode=2, stdout="", stderr="sin posición"),
                          SimpleNamespace(returncode=2, stdout="", stderr="^ Traceback")):
            with self.subTest(respuesta=respuesta):
                self.setUp()
                self.resultado_invalido = respuesta
                with self.assertRaisesRegex(RuntimeError, "tipo inválido"):
                    self.ejecutar()

    def test_juzgar_con_git_no_restringe_medidas_y_timeout_es_acotado(self):
        comandos = []
        original = self._respuesta
        def correr(args, *, cwd, env):
            comandos.append(list(args))
            return original(args, cwd=cwd, env=env)
        respuestas = [self.resultado_juzgar, self.resultado_invalido]
        tiempos = []
        def run(*_args, **kwargs):
            tiempos.append(kwargs["timeout"])
            return respuestas.pop(0)
        with mock.patch.object(vi, "_correr", side_effect=correr), \
             mock.patch.object(vi.subprocess, "run", side_effect=run), \
             mock.patch.object(vi.shutil, "which", return_value="git"):
            vi._recorrer_tareas(Path("oracle"), temporal=self.temporal, env={})
        juzgar = next(a for a in comandos if len(a) > 1 and a[1] == "juzgar")
        self.assertNotIn("--medida", juzgar)
        self.assertEqual(tiempos, [30, 30])
