"""Regresiones fail-closed del comando unificado `oracle`."""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from nucleo.proyecto import Proyecto
from tools import cli

RAIZ = Path(__file__).resolve().parents[1]


class OracleCliTests(unittest.TestCase):
    @staticmethod
    def _callado(fn, *args, **kw):
        """Corre una función del CLI sin dejar su salida en la de la suite.

        Los tests capturaban `cli.main` pero llamaban `cmd_init`, `cmd_nueva` y `cmd_caso` DIRECTO,
        así que la ayuda del comando terminaba mezclada con el resumen de la corrida:
        `python -m unittest -q | tail -3` mostraba «Creá una medida» en vez de «OK». Un test que
        ensucia la salida hace ilegible justo lo que uno mira cuando algo falla.
        """
        salida = io.StringIO()
        with redirect_stdout(salida):
            resultado = fn(*args, **kw)
        return resultado, salida.getvalue()

    def _cmd_test_oracle_simulado(self, *extras: str, unitarios: int = 0,
                                  mutacion_codigo: int = 0):
        from tools import cifras, metamorficas, mutar_codigo, trazar

        def correr_unitarios(proy):
            print("UNITARIOS OK" if unitarios == 0 else "UNITARIOS ✗")
            return unitarios

        def correr_mutacion_codigo(proy, args):
            print("MUTACIÓN DE CÓDIGO OK" if mutacion_codigo == 0 else "MUTACIÓN DE CÓDIGO ✗")
            return mutacion_codigo

        salida = io.StringIO()
        with (mock.patch.object(cli, "_ejecutar_unitarios", side_effect=correr_unitarios) as m_unit,
              mock.patch.object(cli, "cargar_catalogo", return_value={"meta.medida": object()}),
              mock.patch.object(cli, "rutas_de_corpus",
                                return_value=[RAIZ / "corpus" / "meta" / "001.caso"]),
              mock.patch.object(cli.corpus, "verificar", return_value=([], [{"id": "001"}])),
              mock.patch.object(cli.sintaxis, "verificar_catalogo",
                                return_value={"json_igual": True, "texto_igual": True,
                                              "medidas": 1, "macros": 0, "casos": 1}),
              mock.patch.object(cli.sintaxis, "verificar_documentos", return_value={"fallas": []}),
              mock.patch.object(cli.aceptacion, "_ejecutar", return_value=0),
              mock.patch.object(cli.diferencial, "_ejecutar", return_value=0),
              mock.patch.object(trazar, "main", return_value=0),
              mock.patch.object(metamorficas, "main", return_value=0),
              mock.patch.object(cifras, "main", return_value=0),
              mock.patch.object(cli.mutar, "_ejecutar", return_value=0) as m_mutar,
              mock.patch.object(mutar_codigo, "_ejecutar",
                                side_effect=correr_mutacion_codigo) as m_mutar_codigo,
              redirect_stdout(salida)):
            rc = cli.main(["test", "--proyecto", str(RAIZ), *extras])
        return rc, salida.getvalue(), m_unit, m_mutar, m_mutar_codigo


    def test_ayuda_y_sin_argumentos_devuelven_cero(self) -> None:
        salida_help = io.StringIO()
        with redirect_stdout(salida_help):
            rc_help = cli.main(["--help"])
        self.assertEqual(rc_help, 0)
        self.assertIn("oracle init", salida_help.getvalue())
        self.assertIn("oracle test", salida_help.getvalue())

        salida_vacia = io.StringIO()
        with redirect_stdout(salida_vacia):
            rc_vacia = cli.main([])
        self.assertEqual(rc_vacia, 0)
        self.assertEqual(salida_help.getvalue(), salida_vacia.getvalue())

    def test_init_crea_estructura_valida_y_test_la_acepta(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            destino = Path(td) / "nuevo-proyecto"
            salida_init = io.StringIO()
            with redirect_stdout(salida_init):
                rc_init = cli.main(["init", str(destino)])
            self.assertEqual(rc_init, 0)
            self.assertTrue((destino / "catalogos").is_dir())
            self.assertTrue((destino / "corpus").is_dir())
            self.assertTrue((destino / "diferencial").is_dir())
            self.assertTrue((destino / "oracle.json").is_file())

            # oracle test sobre el proyecto recién inicializado debe ser verde
            salida_test = io.StringIO()
            with redirect_stdout(salida_test):
                rc_test = cli.main(["test", "--proyecto", str(destino)])
            self.assertEqual(rc_test, 0)
            self.assertIn("VEREDICTO: VERDE", salida_test.getvalue())
            self.assertIn("proyecto vacío", salida_test.getvalue())

    def test_test_distingue_no_aplica_de_falla(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])

            # 1. Sin fixtures diferenciales -> no aplica (salteado)
            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main(["test", "--proyecto", str(raiz)])
            self.assertEqual(rc, 0)
            self.assertIn("DIFERENCIAL: salteado", salida.getvalue())

            # 2. Con fixture malformado -> falla
            (raiz / "diferencial" / "roto.json").write_text("{}", encoding="utf-8")
            salida_falla = io.StringIO()
            with redirect_stdout(salida_falla):
                rc_falla = cli.main(["test", "--proyecto", str(raiz)])
            self.assertEqual(rc_falla, 1)
            self.assertIn("DIFERENCIAL ✗", salida_falla.getvalue())
            self.assertIn("VEREDICTO: ROJO", salida_falla.getvalue())

    def test_rapido_saltea_mutacion_y_lo_informa_en_el_veredicto(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])

            # Creamos una medida y un caso válidos
            proy = Proyecto(raiz)
            _, _ = self._callado(cli.cmd_nueva, proy, "demo.prueba")
            medida_path = raiz / "catalogos" / "demo" / "demo.prueba.oracle"
            medida_path.write_text(
                "ninguno demo.prueba:\n"
                "    de item x\n"
                "    donde x.mal == true\n"
                "    umbral <= 0 porque \"ningun item puede estar mal\"\n"
                "    alcance \"NO ve otros items\"\n",
                encoding="utf-8",
            )
            _, _ = self._callado(cli.cmd_caso, proy, "demo/001-rojo")
            caso_path = raiz / "corpus" / "demo" / "001-rojo.caso"
            caso_path.write_text(
                "caso 001-rojo:\n"
                "    fecha: \"2026-08-26\"\n"
                "    origen:\n"
                "        repo: \"demo\"\n"
                "        commit: \"local\"\n"
                "    titulo: \"item defectuoso\"\n"
                "    etiqueta: falso_verde\n"
                "    sintoma:\n"
                "        item mal marcado\n"
                "    como_se_detecto: mutacion\n"
                "    medida: demo.prueba\n"
                "    evidencia:\n"
                "        item: mal\n"
                "            true\n"
                "    leccion:\n"
                "        activa la medida\n",
                encoding="utf-8",
            )

            # Con --rapido: saltea mutación y lo dice en el veredicto
            salida_rapido = io.StringIO()
            with redirect_stdout(salida_rapido):
                rc_rapido = cli.main(["test", "--proyecto", str(raiz), "--rapido"])
            self.assertEqual(rc_rapido, 0)
            self.assertIn("MUTACIÓN: salteada por --rapido", salida_rapido.getvalue())
            self.assertIn(
                "VEREDICTO: VERDE (se salteó: mutación de medidas (--rapido))",
                salida_rapido.getvalue())

    def test_test_por_omision_en_oracle_corre_unitarios_y_nombra_codigo_salteado(self) -> None:
        rc, salida, m_unit, m_mutar, m_mutar_codigo = self._cmd_test_oracle_simulado()

        self.assertEqual(rc, 0)
        m_unit.assert_called_once()
        m_mutar.assert_called_once()
        m_mutar_codigo.assert_not_called()
        self.assertIn("MUTACIÓN DE CÓDIGO: salteada", salida)
        self.assertIn("oracle test --todo", salida)
        self.assertIn(
            "VEREDICTO: VERDE (se salteó: mutación de código (corré `oracle test --todo`))",
            salida)

    def test_test_todo_en_oracle_corre_mutacion_de_codigo_y_no_declara_omisiones(self) -> None:
        rc, salida, m_unit, m_mutar, m_mutar_codigo = self._cmd_test_oracle_simulado("--todo")

        self.assertEqual(rc, 0)
        m_unit.assert_called_once()
        m_mutar.assert_called_once()
        m_mutar_codigo.assert_called_once()
        self.assertNotIn("se salteó", salida)
        self.assertIn("VEREDICTO: VERDE (todo: todas las verificaciones en regla", salida)

    def test_rapido_en_oracle_nombra_todo_lo_salteado(self) -> None:
        rc, salida, m_unit, m_mutar, m_mutar_codigo = self._cmd_test_oracle_simulado("--rapido")

        self.assertEqual(rc, 0)
        m_unit.assert_not_called()
        m_mutar.assert_not_called()
        m_mutar_codigo.assert_not_called()
        self.assertIn("UNITARIOS: salteados por --rapido", salida)
        self.assertIn("MUTACIÓN: salteada por --rapido", salida)
        self.assertIn("MUTACIÓN DE CÓDIGO: salteada por --rapido", salida)
        self.assertIn("tests unitarios (--rapido)", salida)
        self.assertIn("mutación de medidas (--rapido)", salida)
        self.assertIn("mutación de código (corré `oracle test --todo`)", salida)

    def test_un_fallo_de_unitarios_pone_rojo_el_veredicto(self) -> None:
        rc, salida, m_unit, _, _ = self._cmd_test_oracle_simulado(unitarios=1)

        self.assertEqual(rc, 1)
        m_unit.assert_called_once()
        self.assertIn("UNITARIOS ✗", salida)
        self.assertIn("VEREDICTO: ROJO (falló: unitarios)", salida)

    def test_medida_sin_casos_falla_en_test(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])
            proy = Proyecto(raiz)
            _, _ = self._callado(cli.cmd_nueva, proy, "demo.sola")
            (raiz / "catalogos" / "demo" / "demo.sola.oracle").write_text(
                "ninguno demo.sola:\n"
                "    de item x\n"
                "    donde x.mal == true\n"
                "    umbral <= 0 porque \"defensa\"\n"
                "    alcance \"alcance\"\n",
                encoding="utf-8",
            )
            salida = io.StringIO()
            with redirect_stdout(salida):
                rc = cli.main(["test", "--proyecto", str(raiz), "--rapido"])
            self.assertEqual(rc, 1)
            self.assertIn("ACEPTACIÓN ✗", salida.getvalue())
            self.assertIn("VEREDICTO: ROJO", salida.getvalue())

    def test_nueva_y_caso_validan_identificadores(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])
            proy = Proyecto(raiz)

            # Identificadores inválidos
            for mid_invalido in ("medida_sin_punto", "MAYUS.nombre", "123.456", "../escape"):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.cmd_nueva(proy, mid_invalido)
                self.assertEqual(rc, 1)

            for cid_invalido in ("sin_grupo", "grupo/sin_numero", "grupo/MAYUS", "grupo/../escape"):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    rc = cli.cmd_caso(proy, cid_invalido)
                self.assertEqual(rc, 1)

    def test_escalares_externas_exigen_confianza_en_test_y_revisar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            _, _ = self._callado(cli.cmd_init, str(raiz), [])
            (raiz / "escalares.py").write_text(
                "from nucleo.algebra import escalar\n"
                "@escalar('es_malo')\n"
                "def es_malo(fila): return fila['mal']\n",
                encoding="utf-8",
            )
            (raiz / "catalogos" / "demo").mkdir(parents=True, exist_ok=True)
            medida_path = raiz / "catalogos" / "demo" / "demo.udf.oracle"
            medida_path.write_text(
                "ninguno demo.udf:\n"
                "    de item x\n"
                "    donde es_malo(x) == true\n"
                "    umbral <= 0 porque \"defensa\"\n"
                "    alcance \"alcance\"\n",
                encoding="utf-8",
            )
            salida_sin = io.StringIO()
            with redirect_stdout(salida_sin):
                rc_sin = cli.main(["test", "--proyecto", str(raiz)])
            self.assertEqual(rc_sin, 1)
            self.assertIn("--confiar-escalares", salida_sin.getvalue())

            salida_con = io.StringIO()
            with redirect_stdout(salida_con):
                rc_con = cli.main([
                    "test", "--proyecto", str(raiz), "--confiar-escalares", "--rapido",
                ])
            self.assertEqual(rc_con, 1)
            self.assertIn("ACEPTACIÓN ✗", salida_con.getvalue())
            self.assertNotIn("CATÁLOGO INVÁLIDO", salida_con.getvalue())

            salida_rev_sin = io.StringIO()
            with redirect_stdout(salida_rev_sin):
                rc_rev_sin = cli.main(["revisar", str(medida_path), "--proyecto", str(raiz)])
            self.assertEqual(rc_rev_sin, 1)
            self.assertIn("--confiar-escalares", salida_rev_sin.getvalue())

    def test_ejecucion_como_subproceso(self) -> None:
        r = subprocess.run(
            [sys.executable, str(RAIZ / "tools" / "cli.py"), "--help"],
            cwd=RAIZ, capture_output=True, text=True,
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("oracle init", r.stdout)

    def test_wheel_instalado_trae_datos_y_ejecuta_oracle_test(self) -> None:
        with tempfile.TemporaryDirectory(prefix="oracle-wheel-test-") as td:
            temporal = Path(td)
            fuente = temporal / "fuente"
            shutil.copytree(
                RAIZ,
                fuente,
                ignore=shutil.ignore_patterns(
                    ".git", "build", "dist", "*.egg-info", "__pycache__", "*.pyc"),
            )
            ruedas = temporal / "ruedas"
            ruedas.mkdir()
            env = os.environ.copy()
            env.pop("ORACLE_PROYECTO", None)
            env.pop("PYTHONPATH", None)
            env["PYTHONDONTWRITEBYTECODE"] = "1"

            wheel = subprocess.run(
                [
                    sys.executable, "-m", "pip", "wheel", "--no-deps",
                    "--no-build-isolation", "--wheel-dir", str(ruedas), str(fuente),
                ],
                cwd=temporal, env=env, capture_output=True, text=True,
            )
            self.assertEqual(wheel.returncode, 0, wheel.stdout + wheel.stderr)
            encontradas = tuple(ruedas.glob("oracle_metalenguaje-*.whl"))
            self.assertEqual(len(encontradas), 1, str(encontradas))

            with zipfile.ZipFile(encontradas[0]) as paquete:
                nombres = set(paquete.namelist())
            esperados = {
                "oracle_metalenguaje/tools/cli.py",
                "oracle_metalenguaje/nucleo/aislamiento/escalares.py",
                "oracle_metalenguaje/nucleo/macros/ninguno.oracle",
                "oracle_metalenguaje/nucleo/macros/ninguno-par.oracle",
                "oracle_metalenguaje/nucleo/macros/peor.oracle",
                "oracle_metalenguaje/catalogos/meta/meta.toda_medida_esta_fijada.oracle",
                "oracle_metalenguaje/perfiles/python/catalogos/proceso/"
                "proceso.arnes_con_bytecode_frio.oracle",
            }
            self.assertFalse(esperados - nombres)
            genericos = ("nucleo/", "catalogos/", "perfiles/", "tools/")
            self.assertFalse([nombre for nombre in nombres if nombre.startswith(genericos)])

            entorno = temporal / "entorno"
            venv.EnvBuilder(with_pip=True).create(entorno)
            python = entorno / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
            instalar = subprocess.run(
                [str(python), "-m", "pip", "install", "--no-deps", str(encontradas[0])],
                cwd=temporal, env=env, capture_output=True, text=True,
            )
            self.assertEqual(instalar.returncode, 0, instalar.stdout + instalar.stderr)

            binarios = entorno / ("Scripts" if sys.platform == "win32" else "bin")
            oracle = binarios / ("oracle.exe" if sys.platform == "win32" else "oracle")
            cwd_vacio = temporal / "cwd-vacio"
            cwd_vacio.mkdir()
            proyecto = temporal / "proyecto"

            init = subprocess.run(
                [str(oracle), "init", str(proyecto)],
                cwd=cwd_vacio, env=env, capture_output=True, text=True,
            )
            self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
            vacio = subprocess.run(
                [str(oracle), "test", "--proyecto", str(proyecto)],
                cwd=cwd_vacio, env=env, capture_output=True, text=True,
            )
            self.assertEqual(vacio.returncode, 0, vacio.stdout + vacio.stderr)
            self.assertIn("VEREDICTO: VERDE", vacio.stdout)
            self.assertIn("proyecto vacío", vacio.stdout)

            dominio = proyecto / "catalogos" / "demo"
            dominio.mkdir()
            (dominio / "demo.instalado.oracle").write_text(
                "ninguno demo.instalado:\n"
                "    de item i\n"
                "    donde i.mal == true\n"
                "    umbral <= 0 porque \"ningun item malo pasa\"\n"
                "    alcance \"NO ve campos distintos de mal\"\n",
                encoding="utf-8",
            )
            casos = proyecto / "corpus" / "demo"
            casos.mkdir()
            (casos / "001-rojo.caso").write_text(
                "caso 001-rojo:\n"
                "    fecha: \"2026-08-26\"\n"
                "    origen:\n"
                "        repo: \"temporal\"\n"
                "        commit: \"sin-commit\"\n"
                "    titulo: \"item malo detectado\"\n"
                "    etiqueta: falso_verde\n"
                "    sintoma:\n"
                "        Un item malo tiene que poner roja la medida instalada.\n"
                "    como_se_detecto: mutacion\n"
                "    medida: demo.instalado\n"
                "    evidencia:\n"
                "        item: id, mal\n"
                "            \"a\", true\n"
                "    leccion:\n"
                "        La macro estándar tiene que estar empaquetada.\n",
                encoding="utf-8",
            )
            con_macro = subprocess.run(
                [str(oracle), "test", "--proyecto", str(proyecto), "--rapido"],
                cwd=cwd_vacio, env=env, capture_output=True, text=True,
            )
            self.assertEqual(con_macro.returncode, 0, con_macro.stdout + con_macro.stderr)
            self.assertIn("SINTAXIS OK", con_macro.stdout)
            self.assertIn("ACEPTACIÓN", con_macro.stdout)
            self.assertIn("VEREDICTO: VERDE", con_macro.stdout)


class InitDejaLasGuardasPuestasTests(OracleCliTests):
    """Lo más importante que escribe `init` es `catalogo_base`, y faltaba.

    Sin él un proyecto carga SÓLO sus propias medidas y se queda sin las universales: nadie comprueba
    que un umbral traiga defensa, que una medida declare `alcance`, que toda medida esté fijada por
    un caso, ni que un caso se ponga como su etiqueta declara.

    El escenario que lo destapó está fijado abajo, y es el que importa para que una persona pueda
    AUDITAR lo que escribió un modelo: una medida con el predicado invertido —selecciona lo que está
    bien en vez de lo que ofende— más un caso que la declara `falso_verde`. Sin guardas eso daba
    «ACEPTACIÓN ✓ · VEREDICTO: VERDE».
    """

    MEDIDA_INVERTIDA = (
        "ninguno tareas.vencida_sin_dueno:\n"
        "    de tarea t\n"
        "    donde t.vencida == true y t.asignada == true\n"
        '    umbral <= 0 porque "una tarea vencida sin dueño no la va a hacer nadie"\n'
        '    alcance "ve el par vencida+sin-dueño y nada más"\n')

    CASO = (
        "caso 001-vencida-sin-nadie:\n"
        '    fecha: "2026-08-26"\n'
        "    origen:\n"
        '        repo: "yo/tablero"\n'
        '        commit: "x"\n'
        '    titulo: "Una tarea vencida sin dueño pasó desapercibida"\n'
        "    etiqueta: falso_verde\n"
        "    sintoma:\n"
        "        El tablero no mostraba las tareas sin asignar.\n"
        "    como_se_detecto: persona\n"
        "    medida: tareas.vencida_sin_dueno\n"
        "    evidencia:\n"
        "        tarea: id, vencida, asignada\n"
        '            "t-1", true, false\n'
        '            "t-2", false, true\n'
        "    leccion:\n"
        "        Una tarea sin dueño no la ve nadie.\n")

    def test_init_declara_el_catalogo_base(self) -> None:
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d) / "nuevo"
            self._callado(cli.cmd_init, str(raiz), [])
            datos = json.loads((raiz / "oracle.json").read_text(encoding="utf-8"))
            self.assertIs(datos.get("catalogo_base"), True,
                          "sin `catalogo_base` el proyecto nace sin ninguna medida universal")

    def test_un_proyecto_recien_creado_ve_las_medidas_universales(self) -> None:
        """No alcanza con que la bandera esté escrita: tiene que traer medidas de verdad."""
        import tempfile
        from nucleo.medida import cargar_catalogo
        from nucleo.proyecto import Proyecto, catalogos_a_cargar, macros_del_proyecto
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d) / "nuevo"
            self._callado(cli.cmd_init, str(raiz), [])
            proy = Proyecto(raiz)
            catalogo = cargar_catalogo(catalogos_a_cargar(proy), macros=macros_del_proyecto(proy))
            self.assertIn("meta.el_caso_se_pone_como_debe", catalogo)
            self.assertIn("meta.ningun_umbral_sin_defensa", catalogo)

    def test_una_medida_invertida_con_su_caso_sale_ROJA(self) -> None:
        """El escenario de auditoría: un modelo escribe una medida al revés y su caso.

        Es la prueba de que una persona puede confiar en el veredicto sin releer cada predicado.
        """
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d) / "nuevo"
            self._callado(cli.cmd_init, str(raiz), [])
            medida = raiz / "catalogos" / "tareas" / "tareas.vencida_sin_dueno.oracle"
            medida.parent.mkdir(parents=True, exist_ok=True)
            medida.write_text(self.MEDIDA_INVERTIDA, encoding="utf-8")
            caso = raiz / "corpus" / "tareas" / "001-vencida-sin-nadie.caso"
            caso.parent.mkdir(parents=True, exist_ok=True)
            caso.write_text(self.CASO, encoding="utf-8")

            codigo, salida = self._callado(cli.main, ["test", "--rapido", "--proyecto", str(raiz)])
            self.assertEqual(codigo, 1, salida)
            self.assertIn("meta.el_caso_se_pone_como_debe", salida)
            self.assertIn("ROJO", salida)


if __name__ == "__main__":
    unittest.main()
