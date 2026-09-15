"""Revisión independiente de `oracle juzgar` (0.18.0).

Escrita por Claude contra `estudios/0.18.0-juzgar/ENCARGO-AGY.md`, antes de leer la implementación.
El catálogo es una copia de `ejemplo/seguimiento-tareas`; todo pasa por el CLI público.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parents[1]
CLI = RAIZ / "tools/cli.py"
EJEMPLO = RAIZ / "ejemplo/seguimiento-tareas"
REFERENCIAS = "seguimiento.referencias_locales_presentes"


def referencia(estado="presente", destino="captura.png"):
    return {"tarea_id": "t", "origen": "tareas/t/TAREA.md", "linea": 3,
            "destino_declarado": destino, "clase": "local", "estado": estado}


class JuzgarTemporal(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(prefix="oracle-juzgar-revision-")
        self.addCleanup(td.cleanup)
        self.temporal = Path(td.name)
        self.proyecto = self.temporal / "politicas"
        shutil.copytree(EJEMPLO, self.proyecto,
                        ignore=shutil.ignore_patterns("__pycache__", "evaluar.py"))
        self.env = {k: v for k, v in os.environ.items() if k != "ORACLE_PROYECTO"}
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"

    def evidencia(self, datos, nombre="hechos.json"):
        ruta = self.temporal / nombre
        if isinstance(datos, bytes):
            ruta.write_bytes(datos)
        else:
            ruta.write_text(datos if isinstance(datos, str) else json.dumps(datos), encoding="utf-8")
        return ruta

    def juzgar(self, *args, verbo=("juzgar",)):
        return subprocess.run([sys.executable, "-B", str(CLI), *verbo, *args],
                              env=self.env, capture_output=True, text=True, timeout=60,
                              cwd=self.temporal)

    def instantanea(self):
        return {str(p.relative_to(self.temporal)): p.read_bytes()
                for p in sorted(self.temporal.rglob("*")) if p.is_file()}

    def sin_traceback(self, p):
        self.assertNotIn("Traceback", p.stdout + p.stderr)


class VeredictoTests(JuzgarTemporal):
    def test_verde_sale_cero_y_enumera_lo_que_no_miro(self):
        con = self.evidencia({"referencia_seguimiento": [referencia()]})
        p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto), "--medida", REFERENCIAS)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn(REFERENCIAS, p.stdout)
        self.assertIn("SIN MIRAR", p.stdout)

    def test_rojo_sale_uno_con_testigo(self):
        con = self.evidencia({"referencia_seguimiento": [referencia("ausente", "falta-esto.png")]})
        p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto), "--medida", REFERENCIAS)
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("falta-esto.png", p.stdout)
        self.sin_traceback(p)

    def test_json_es_lo_unico_en_stdout(self):
        con = self.evidencia({"referencia_seguimiento": [referencia("ausente")]})
        p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto), "--medida", REFERENCIAS,
                        "--json")
        self.assertEqual(p.returncode, 1, p.stderr)
        datos = json.loads(p.stdout)
        self.assertIs(datos["ok"], False)
        self.assertEqual([m["id"] for m in datos["medidas"]], [REFERENCIAS])

    def test_nada_aplicable_nunca_es_verde(self):
        con = self.evidencia({"relacion_que_nadie_mide": [{"x": 1}]})
        p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("SIN MEDIDAS APLICABLES", (p.stdout + p.stderr).upper())
        self.assertIn("relacion_que_nadie_mide", p.stdout + p.stderr)
        self.sin_traceback(p)

    def test_alias_y_forma_canonica_dan_lo_mismo(self):
        con = self.evidencia({"referencia_seguimiento": [referencia("ausente")]})
        args = ("--con", str(con), "--proyecto", str(self.proyecto), "--medida", REFERENCIAS)
        corto, largo = self.juzgar(*args), self.juzgar(*args, verbo=("proyecto", "juzgar"))
        self.assertEqual((corto.returncode, corto.stdout), (largo.returncode, largo.stdout))

    def test_no_escribe_archivos(self):
        con = self.evidencia({"referencia_seguimiento": [referencia("ausente")]})
        antes = self.instantanea()
        self.juzgar("--con", str(con), "--proyecto", str(self.proyecto), "--json")
        self.juzgar("--help")
        self.assertEqual(self.instantanea(), antes)


class EntradaInvalidaTests(JuzgarTemporal):
    def test_formas_invalidas_de_evidencia_salen_dos(self):
        casos = {
            "no es objeto": json.dumps([referencia()]),
            "valor no lista": json.dumps({"referencia_seguimiento": referencia()}),
            "fila no objeto": json.dumps({"referencia_seguimiento": [1, 2]}),
            "json roto": '{"referencia_seguimiento": [',
            "utf8 invalido": b'{"referencia_seguimiento": [{"x": "\xff"}]}',
        }
        for nombre, contenido in casos.items():
            with self.subTest(nombre):
                con = self.evidencia(contenido, nombre=nombre.replace(" ", "-") + ".json")
                p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto))
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.sin_traceback(p)

    def test_archivo_ausente_nombra_la_ruta(self):
        ausente = self.temporal / "no-existe.json"
        p = self.juzgar("--con", str(ausente), "--proyecto", str(self.proyecto))
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("no-existe.json", p.stdout + p.stderr)
        self.sin_traceback(p)

    def test_sin_con_sale_dos(self):
        p = self.juzgar("--proyecto", str(self.proyecto))
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)

    def test_medida_inexistente_repetida_o_no_aplicable_sale_dos(self):
        con = self.evidencia({"referencia_seguimiento": [referencia()]})
        casos = {
            "inexistente": ["--medida", "seguimiento.no_existe"],
            "repetida": ["--medida", REFERENCIAS, "--medida", REFERENCIAS],
        }
        solo_lectura = self.evidencia({"lectura_seguimiento": [
            {"esquema": "oracle.tareas.hechos/v1", "completa": True, "git": "no_solicitado", "head": ""}
        ]}, nombre="lectura.json")
        for nombre, extra in casos.items():
            with self.subTest(nombre):
                p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto), *extra)
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.sin_traceback(p)
        with self.subTest("no aplicable"):
            p = self.juzgar("--con", str(solo_lectura), "--proyecto", str(self.proyecto),
                            "--medida", REFERENCIAS)
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertIn(REFERENCIAS, p.stdout + p.stderr)

    def test_escalares_sin_confianza_sale_dos_y_no_las_ejecuta(self):
        marca = self.temporal / "ejecutado"
        (self.proyecto / "escalares.py").write_text(
            f"from pathlib import Path\nPath({str(marca)!r}).write_text('si')\n", encoding="utf-8")
        con = self.evidencia({"referencia_seguimiento": [referencia()]})
        p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("--confiar-escalares", p.stdout + p.stderr)
        self.assertFalse(marca.exists())

    def test_proyecto_invalido_sale_dos(self):
        vacio = self.temporal / "sin-catalogos"
        vacio.mkdir()
        con = self.evidencia({"referencia_seguimiento": [referencia()]})
        p = self.juzgar("--con", str(con), "--proyecto", str(vacio))
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.sin_traceback(p)


class HechosDelTrackerTests(JuzgarTemporal):
    @unittest.skipUnless(shutil.which("git"), "requiere Git")
    def test_hechos_reales_del_tracker_verde_y_luego_rojo(self):
        repo = self.temporal / "repo"
        repo.mkdir()
        env = {k: v for k, v in self.env.items() if not k.startswith("GIT_")}
        corre = lambda *a: subprocess.run(a, cwd=repo, env=env, capture_output=True, text=True,
                                          timeout=60)
        self.assertEqual(corre(sys.executable, "-B", str(CLI), "tarea", "init",
                               "--proyecto", str(repo)).returncode, 0)
        creada = corre(sys.executable, "-B", str(CLI), "tarea", "nueva", "Con captura", "--json",
                       "--proyecto", str(repo))
        ident = json.loads(creada.stdout)["id"]
        documento = repo / "tareas" / ident / "TAREA.md"
        (documento.parent / "captura.png").write_bytes(b"png")
        documento.write_text(documento.read_text(encoding="utf-8") + "[captura](captura.png)\n",
                             encoding="utf-8")
        medida = ("--medida", REFERENCIAS, "--medida", "seguimiento.lectura_sin_omisiones")

        def juzgar_tracker():
            hechos = corre(sys.executable, "-B", str(CLI), "tarea", "hechos",
                           "--proyecto", str(repo))
            self.assertEqual(hechos.returncode, 0, hechos.stderr)
            con = self.evidencia(hechos.stdout, nombre="tracker.json")
            return self.juzgar("--con", str(con), "--proyecto", str(self.proyecto), *medida)

        verde = juzgar_tracker()
        self.assertEqual(verde.returncode, 0, verde.stdout + verde.stderr)
        documento.write_text(documento.read_text(encoding="utf-8") + "[rota](no-esta.png)\n",
                             encoding="utf-8")
        rojo = juzgar_tracker()
        self.assertEqual(rojo.returncode, 1, rojo.stdout + rojo.stderr)
        self.assertIn("no-esta.png", rojo.stdout)


if __name__ == "__main__":
    unittest.main()


class SombraTests(JuzgarTemporal):
    """Revisión: el mismo proyecto no puede dar dos veredictos. `oracle test` tolera una medida
    declarada en sombra; `oracle juzgar` tiene que evaluarla, mostrarla y no fallar por ella."""

    def test_medida_en_sombra_en_rojo_no_hace_fallar(self):
        config = json.loads((self.proyecto / "oracle.json").read_text(encoding="utf-8"))
        config["sombra"] = {REFERENCIAS: {"desde": "2026-09-15",
                                          "porque": "deuda construida para la revisión"}}
        (self.proyecto / "oracle.json").write_text(json.dumps(config), encoding="utf-8")
        con = self.evidencia({"referencia_seguimiento": [referencia("ausente", "en-sombra.png")]})
        p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto), "--medida", REFERENCIAS)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("SOMBRA", p.stdout.upper())
        self.assertIn("en-sombra.png", p.stdout)


class AmbitoTests(JuzgarTemporal):
    """Revisión de P0: una medida `del_origen` del catálogo base no juzga a un consumidor.
    `Motor.desde_proyecto` la carga (57 contra 37 medidas, medido el 2026-09-15); juzgar no."""

    def test_medida_del_origen_de_oracle_no_juzga_al_consumidor(self):
        config = json.loads((self.proyecto / "oracle.json").read_text(encoding="utf-8"))
        config["catalogo_base"] = True
        (self.proyecto / "oracle.json").write_text(json.dumps(config), encoding="utf-8")
        con = self.evidencia({"verbo_del_cli": [
            {"sustantivo": "proyecto", "verbo": "inventado", "nombrado_en_la_ayuda": False}]})
        p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto))
        self.assertNotIn("meta.todo_verbo_del_cli_esta_en_la_ayuda", p.stdout + p.stderr)
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("SIN MEDIDAS APLICABLES", (p.stdout + p.stderr).upper())


class TopeDeEvidenciaTests(JuzgarTemporal):
    """Sobrevivientes de la primera ronda: el tope de 50 MiB no tenía test en su borde."""

    def test_el_tope_declarado_es_50_mib(self):
        from tools import juzgar
        self.assertEqual(juzgar.LIMITE_TAMANO_EVIDENCIA, 50 * 1024 * 1024)

    def test_en_el_tope_se_lee_y_un_byte_mas_sale_dos(self):
        import contextlib
        import io
        from unittest import mock
        from tools import juzgar

        contenido = json.dumps({"referencia_seguimiento": [referencia()]}).encode("utf-8")
        con = self.evidencia(contenido)
        for tope, esperado in ((len(contenido), 0), (len(contenido) - 1, 2)):
            with self.subTest(tope=tope), \
                    mock.patch.object(juzgar, "LIMITE_TAMANO_EVIDENCIA", tope), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as errores:
                codigo = juzgar.cmd_juzgar(["--con", str(con), "--proyecto",
                                            str(self.proyecto), "--medida", REFERENCIAS])
                self.assertEqual(codigo, esperado, errores.getvalue())


class SobrevivientesDeJuzgarTests(JuzgarTemporal):
    """Sobrevivientes de la primera ronda sobre tools/juzgar.py con comportamiento observable."""

    def _con(self):
        return self.evidencia({"referencia_seguimiento": [referencia()]})

    def test_nombre_de_relacion_vacio_sale_dos(self):
        for nombre in ("", "   "):
            with self.subTest(nombre=nombre):
                con = self.evidencia({nombre: [referencia()]}, nombre="vacia.json")
                p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto))
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn("nombre de relación inválido", p.stderr)

    def test_errores_de_lectura_de_la_evidencia_salen_dos(self):
        import contextlib
        import io
        from unittest import mock
        from tools import juzgar

        con = self._con()
        for metodo in ("stat", "read_bytes"):
            original = getattr(Path, metodo)

            def falla(ruta, *a, _original=original, **k):
                if ruta.name == con.name:
                    raise OSError("disco ilegible")
                return _original(ruta, *a, **k)

            errores = io.StringIO()
            with self.subTest(metodo=metodo), mock.patch.object(Path, metodo, falla), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errores):
                codigo = juzgar.cmd_juzgar(["--con", str(con), "--proyecto",
                                            str(self.proyecto), "--medida", REFERENCIAS])
                self.assertEqual(codigo, 2, errores.getvalue())
                self.assertIn("disco ilegible", errores.getvalue())

    def test_cmd_juzgar_recibe_solo_banderas(self):
        import contextlib
        import io
        from tools import juzgar

        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
            codigo = juzgar.cmd_juzgar(["--con", str(self._con()), "--proyecto", str(self.proyecto),
                                        "--medida", REFERENCIAS])
        self.assertEqual(codigo, 0)
        self.assertIn(REFERENCIAS, salida.getvalue())

    def test_valor_de_bandera_al_final_ausente_o_seguido_de_otra_bandera(self):
        con = str(self._con())
        base = ("--proyecto", str(self.proyecto))
        self.assertEqual(self.juzgar(*base, "--medida", REFERENCIAS, "--con", con).returncode, 0)
        self.assertEqual(self.juzgar("--con", con, *base, "--medida", REFERENCIAS).returncode, 0)
        casos = {
            "con al final": ((*base, "--con"), "falta la ruta"),
            "medida al final": (("--con", con, *base, "--medida"), "falta el id"),
            "medida seguida de bandera": (("--con", con, *base, "--medida", "--json"), "falta el id"),
        }
        for nombre, (args, mensaje) in casos.items():
            with self.subTest(nombre):
                p = self.juzgar(*args)
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn(mensaje, p.stderr)
                self.sin_traceback(p)


class BanderasTests(JuzgarTemporal):
    """Segunda ronda de mutación: banderas sin valor y banderas encadenadas."""

    def test_json_seguido_de_otra_bandera(self):
        con = self.evidencia({"referencia_seguimiento": [referencia()]})
        p = self.juzgar("--json", "--medida", REFERENCIAS, "--con", str(con),
                        "--proyecto", str(self.proyecto))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIs(json.loads(p.stdout)["ok"], True)

    def test_proyecto_sin_valor_sale_dos(self):
        con = str(self.evidencia({"referencia_seguimiento": [referencia()]}))
        for args in (("--con", con, "--proyecto"), ("--con", con, "--proyecto", "--json")):
            with self.subTest(args=args):
                p = self.juzgar(*args)
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn("falta la ruta: `--proyecto", p.stderr)
                self.sin_traceback(p)

    def test_argumento_desconocido_se_nombra(self):
        con = str(self.evidencia({"referencia_seguimiento": [referencia()]}))
        p = self.juzgar("--desconocido", "--con", con, "--proyecto", str(self.proyecto))
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("argumento desconocido para `oracle juzgar`: --desconocido", p.stderr)

    @unittest.skipUnless(hasattr(os, "symlink"), "requiere enlaces simbólicos")
    def test_escalares_fuera_del_proyecto_salen_dos_aun_confiando(self):
        afuera = self.temporal / "escalares-de-afuera.py"
        afuera.write_text("x = 1\n", encoding="utf-8")
        (self.proyecto / "escalares.py").symlink_to(afuera)
        con = str(self.evidencia({"referencia_seguimiento": [referencia()]}))
        p = self.juzgar("--con", con, "--proyecto", str(self.proyecto), "--confiar-escalares",
                        "--medida", REFERENCIAS)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS", p.stderr)
        self.sin_traceback(p)

    def test_medida_en_sombra_en_verde_es_un_verde_comun(self):
        config = json.loads((self.proyecto / "oracle.json").read_text(encoding="utf-8"))
        config["sombra"] = {REFERENCIAS: {"desde": "2026-09-15", "porque": "deuda construida"}}
        (self.proyecto / "oracle.json").write_text(json.dumps(config), encoding="utf-8")
        con = self.evidencia({"referencia_seguimiento": [referencia()]})
        p = self.juzgar("--con", str(con), "--proyecto", str(self.proyecto), "--medida", REFERENCIAS)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("VEREDICTO: verde en 1 medidas. SIN MIRAR:", p.stdout)
        self.assertNotIn("por sombra", p.stdout)
        self.assertNotIn("perdonadas", p.stdout)
