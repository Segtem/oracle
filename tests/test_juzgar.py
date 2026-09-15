"""Pruebas para `oracle juzgar` y `oracle proyecto juzgar` (0.18.0)."""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from nucleo.algebra import ErrorDeAlgebra
from nucleo.medida import MedidaMalDeclarada
from tools import cli
from tools import juzgar

RAIZ = Path(__file__).resolve().parents[1]
CLI = RAIZ / "tools/cli.py"
EJEMPLO_SEGUIMIENTO = RAIZ / "ejemplo/seguimiento-tareas"
POLITICA_REFERENCIAS = "seguimiento.referencias_locales_presentes"
POLITICA_LECTURA = "seguimiento.lectura_sin_omisiones"
POLITICA_ARCHIVOS = "seguimiento.archivos_confirmados_sin_cambios"


def _fila_referencia(estado: str = "presente", destino: str = "captura.png") -> dict:
    return {
        "tarea_id": "20260915-100000-tarea",
        "origen": "tareas/20260915-100000-tarea/TAREA.md",
        "linea": 5,
        "destino_declarado": destino,
        "clase": "local",
        "estado": estado,
    }


class BaseJuzgarTest(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory(prefix="oracle-test-juzgar-")
        self.temporal = Path(self._td.name).resolve()
        self.proyecto = self.temporal / "proyecto-politicas"
        shutil.copytree(
            EJEMPLO_SEGUIMIENTO,
            self.proyecto,
            ignore=shutil.ignore_patterns("__pycache__", "evaluar.py"),
        )
        self.env = {k: v for k, v in os.environ.items() if k != "ORACLE_PROYECTO"}
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"

    def tearDown(self) -> None:
        self._td.cleanup()

    def escribir_evidencia(self, contenido, nombre: str = "hechos.json") -> Path:
        ruta = self.temporal / nombre
        if isinstance(contenido, bytes):
            ruta.write_bytes(contenido)
        elif isinstance(contenido, str):
            ruta.write_text(contenido, encoding="utf-8")
        else:
            ruta.write_text(json.dumps(contenido, ensure_ascii=False), encoding="utf-8")
        return ruta

    def correr_cli(self, *args: str) -> tuple[int, str, str]:
        """Ejecuta el CLI en proceso capturando stdout y stderr."""
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                rc = cli.main(list(args))
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 1
        return rc, stdout.getvalue(), stderr.getvalue()

    def correr_subproceso(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(CLI), *args],
            cwd=self.temporal,
            env=self.env,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def instantanea_archivos(self) -> dict[str, bytes]:
        return {
            str(p.relative_to(self.temporal)): p.read_bytes()
            for p in sorted(self.temporal.rglob("*"))
            if p.is_file()
        }


class TestVeredictosYSalidas(BaseJuzgarTest):
    """Verifica veredictos 0 (verde) y 1 (rojo), y formatos texto y JSON."""

    def test_verde_con_alcance_enumerado_retorna_cero(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS,
        )
        self.assertEqual(rc, 0, out + err)
        self.assertIn("✓ seguimiento.referencias_locales_presentes", out)
        self.assertIn("VEREDICTO: verde en 1 medidas. SIN MIRAR:", out)
        self.assertNotIn("Traceback", out + err)

    def test_rojo_con_testigo_retorna_uno(self) -> None:
        con = self.escribir_evidencia({
            "referencia_seguimiento": [_fila_referencia("ausente", "diagrama-ausente.png")],
        })
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS,
        )
        self.assertEqual(rc, 1, out + err)
        self.assertIn("✗ seguimiento.referencias_locales_presentes", out)
        self.assertIn("diagrama-ausente.png", out)
        self.assertIn("VEREDICTO: 1 de 1 medidas en rojo", out)
        self.assertNotIn("Traceback", out + err)

    def test_json_parseable_y_sin_ruido_en_stdout(self) -> None:
        con = self.escribir_evidencia({
            "referencia_seguimiento": [_fila_referencia("ausente", "rota.png")],
        })
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS, "--json",
        )
        self.assertEqual(rc, 1, err)
        datos = json.loads(out)
        self.assertIs(datos["ok"], False)
        self.assertEqual(len(datos["medidas"]), 1)
        self.assertEqual(datos["medidas"][0]["id"], POLITICA_REFERENCIAS)
        self.assertFalse(datos["medidas"][0]["ok"])
        self.assertTrue(len(datos["medidas"][0]["testigos"]) >= 1)

    def test_paridad_alias_juzgar_y_proyecto_juzgar(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        rc1, out1, err1 = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS,
        )
        rc2, out2, err2 = self.correr_cli(
            "proyecto", "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS,
        )
        self.assertEqual(rc1, rc2)
        self.assertEqual(out1, out2)
        self.assertEqual(err1, err2)

    def test_evaluacion_sin_medida_aplica_todas_las_pertinentes(self) -> None:
        con = self.escribir_evidencia({
            "referencia_seguimiento": [_fila_referencia()],
            "lectura_seguimiento": [{
                "esquema": "oracle.tareas.hechos/v1",
                "completa": True,
                "git": "no_solicitado",
                "head": "",
            }],
        })
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
        )
        self.assertEqual(rc, 0, out + err)
        self.assertIn(POLITICA_REFERENCIAS, out)
        self.assertIn(POLITICA_LECTURA, out)


class TestEntradaInvalida(BaseJuzgarTest):
    """Verifica rechazo con código 2 ante formas inválidas de evidencia y parámetros."""

    def test_sin_con_retorna_dos(self) -> None:
        rc, out, err = self.correr_cli("juzgar", "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("falta la evidencia", err)
        self.assertNotIn("Traceback", out + err)

    def test_con_sin_ruta_retorna_dos(self) -> None:
        rc, out, err = self.correr_cli("juzgar", "--con")
        self.assertEqual(rc, 2)
        self.assertIn("falta la ruta", err)

        rc2, out2, err2 = self.correr_cli("juzgar", "--con", "--json")
        self.assertEqual(rc2, 2)
        self.assertIn("falta la ruta", err2)

    def test_con_repetido_retorna_dos(self) -> None:
        con1 = self.escribir_evidencia({"x": []}, "a.json")
        con2 = self.escribir_evidencia({"x": []}, "b.json")
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con1), "--con", str(con2), "--proyecto", str(self.proyecto)
        )
        self.assertEqual(rc, 2)
        self.assertIn("repetida", err)

    def test_archivo_ausente_retorna_dos_y_nombra_ruta(self) -> None:
        ausente = self.temporal / "inexistente.json"
        rc, out, err = self.correr_cli("juzgar", "--con", str(ausente), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("inexistente.json", err)
        self.assertNotIn("Traceback", out + err)

    def test_ruta_directorio_retorna_dos(self) -> None:
        directorio = self.temporal / "carpeta"
        directorio.mkdir()
        rc, out, err = self.correr_cli("juzgar", "--con", str(directorio), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("directorio", err)
        self.assertNotIn("Traceback", out + err)

    def test_evidencia_no_objeto_retorna_dos(self) -> None:
        con = self.escribir_evidencia([_fila_referencia()])
        rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("objeto JSON", err)
        self.assertNotIn("Traceback", out + err)

    def test_evidencia_valor_no_lista_retorna_dos(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": _fila_referencia()})
        rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("lista de filas", err)
        self.assertNotIn("Traceback", out + err)

    def test_evidencia_fila_no_objeto_retorna_dos(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": [1, 2, 3]})
        rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("debe ser un objeto", err)
        self.assertNotIn("Traceback", out + err)

    def test_evidencia_json_malformado_retorna_dos(self) -> None:
        con = self.escribir_evidencia('{"referencia_seguimiento": [')
        rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("JSON inválido", err)
        self.assertNotIn("Traceback", out + err)

    def test_evidencia_utf8_invalido_retorna_dos(self) -> None:
        con = self.escribir_evidencia(b'{"referencia_seguimiento": [{"x": "\xff\xfe"}]}')
        rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("UTF-8", err)
        self.assertNotIn("Traceback", out + err)

    def test_evidencia_supera_tope_50mib_retorna_dos(self) -> None:
        ruta_grande = self.temporal / "gigante.json"
        with open(ruta_grande, "wb") as f:
            f.seek(juzgar.LIMITE_TAMANO_EVIDENCIA + 10)
            f.write(b"}")
        rc, out, err = self.correr_cli("juzgar", "--con", str(ruta_grande), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("50 MiB", err)
        self.assertNotIn("Traceback", out + err)

    def test_argumento_desconocido_retorna_dos(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto), "--inventada")
        self.assertEqual(rc, 2)
        self.assertIn("desconocido", err)


class TestAplicabilidadYRestricciones(BaseJuzgarTest):
    """Verifica reglas de aplicabilidad y uso de la bandera `--medida`."""

    def test_sin_medidas_aplicables_retorna_uno_y_menciona_relaciones(self) -> None:
        con = self.escribir_evidencia({"relacion_huerfana": [{"clave": "valor"}]})
        rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 1)
        self.assertIn("SIN MEDIDAS APLICABLES", (out + err).upper())
        self.assertIn("relacion_huerfana", out + err)
        self.assertNotIn("Traceback", out + err)

    def test_medida_inexistente_retorna_dos_y_la_nombra(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", "seguimiento.fantasma",
        )
        self.assertEqual(rc, 2)
        self.assertIn("seguimiento.fantasma", err)
        self.assertNotIn("Traceback", out + err)

    def test_medida_duplicada_retorna_dos(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS, "--medida", POLITICA_REFERENCIAS,
        )
        self.assertEqual(rc, 2)
        self.assertIn("repetido", err)
        self.assertIn(POLITICA_REFERENCIAS, err)

    def test_medida_no_aplicable_a_evidencia_retorna_dos_y_la_nombra(self) -> None:
        con = self.escribir_evidencia({"otra_relacion": [{"x": 1}]})
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS,
        )
        self.assertEqual(rc, 2)
        self.assertIn("NO APLICABLE", err)
        self.assertIn(POLITICA_REFERENCIAS, err)


class TestEscalaresYProyecto(BaseJuzgarTest):
    """Verifica reglas de seguridad de escalares y validación de estructura de proyectos."""

    def test_escalares_sin_confianza_retorna_dos_y_no_las_ejecuta(self) -> None:
        testigo = self.temporal / "marca-ejecutada.txt"
        (self.proyecto / "escalares.py").write_text(
            f"from pathlib import Path\nPath({str(testigo)!r}).write_text('peligro')\n",
            encoding="utf-8",
        )
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("ESCALARES EXTERNAS NO EJECUTADAS", err)
        self.assertIn("--confiar-escalares", err)
        self.assertFalse(testigo.exists(), "No debe ejecutar escalares.py sin --confiar-escalares")

    def test_escalares_con_confianza_autoriza_ejecucion(self) -> None:
        (self.proyecto / "escalares.py").write_text(
            "# Archivo de escalares confiado\n", encoding="utf-8"
        )
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--confiar-escalares", "--medida", POLITICA_REFERENCIAS,
        )
        self.assertEqual(rc, 0, out + err)

    def test_proyecto_sin_catalogos_retorna_dos(self) -> None:
        vacio = self.temporal / "sin-catalogos"
        vacio.mkdir()
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(vacio))
        self.assertEqual(rc, 2)
        self.assertIn("PROYECTO INVÁLIDO", err)
        self.assertNotIn("Traceback", out + err)

    def test_proyecto_oracle_json_invalido_retorna_dos(self) -> None:
        (self.proyecto / "oracle.json").write_text("{json_invalido", encoding="utf-8")
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(rc, 2)
        self.assertIn("PROYECTO INVÁLIDO", err)


class TestAyudasYNoMutacion(BaseJuzgarTest):
    """Verifica ayudas de comandos y ausencia de efectos colaterales en disco."""

    def test_ayuda_no_escribe_archivos(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        antes = self.instantanea_archivos()
        rc1, out1, _ = self.correr_cli("juzgar", "--help")
        self.assertEqual(rc1, 0)
        self.assertIn("oracle juzgar", out1)

        rc2, out2, _ = self.correr_cli("proyecto", "juzgar", "--help")
        self.assertEqual(rc2, 0)
        self.assertIn("oracle proyecto juzgar", out2)

        rc3, _, _ = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto), "--json"
        )
        self.assertEqual(rc3, 0)
        self.assertEqual(self.instantanea_archivos(), antes)

    def test_ayudas_generales_documentan_juzgar(self) -> None:
        rc_gen, out_gen, _ = self.correr_cli("--help")
        self.assertEqual(rc_gen, 0)
        self.assertIn("oracle juzgar", out_gen)
        self.assertIn("juzgar", out_gen)

        rc_proy, out_proy, _ = self.correr_cli("proyecto", "--help")
        self.assertEqual(rc_proy, 0)
        self.assertIn("oracle proyecto juzgar", out_proy)


class TestIntegracionTracker(BaseJuzgarTest):
    """Recorrido de integración: juzgar hechos reales emitidos por `oracle tarea hechos`."""

    @unittest.skipUnless(shutil.which("git"), "Requiere git instalado")
    def test_hechos_reales_del_tracker_verde_y_luego_rojo(self) -> None:
        repo = self.temporal / "repo-tracker"
        repo.mkdir()
        env = {k: v for k, v in self.env.items() if not k.startswith("GIT_")}

        def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, "-B", str(CLI), *args],
                cwd=repo,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )

        # 1. Inicializar tracker y crear tarea
        self.assertEqual(run_cli("tarea", "init", "--proyecto", str(repo)).returncode, 0)
        creada = run_cli("tarea", "nueva", "Tarea con captura", "--json", "--proyecto", str(repo))
        self.assertEqual(creada.returncode, 0, creada.stderr)
        tarea_id = json.loads(creada.stdout)["id"]

        # 2. Agregar adjunto y referencia local
        carpeta_tarea = repo / "tareas" / tarea_id
        (carpeta_tarea / "grafico.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        doc_tarea = carpeta_tarea / "TAREA.md"
        doc_tarea.write_text(
            doc_tarea.read_text(encoding="utf-8") + "\nVer [grafico](grafico.png)\n",
            encoding="utf-8",
        )

        # 3. Emitir hechos del tracker
        hechos_p = run_cli("tarea", "hechos", "--proyecto", str(repo))
        self.assertEqual(hechos_p.returncode, 0, hechos_p.stderr)
        ruta_hechos = self.escribir_evidencia(hechos_p.stdout, "tracker-hechos.json")

        # 4. Juzgar con las políticas de seguimiento: debe ser VERDE (código 0)
        juzgar_p = self.correr_subproceso(
            "juzgar", "--con", str(ruta_hechos), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS, "--medida", POLITICA_LECTURA,
        )
        self.assertEqual(juzgar_p.returncode, 0, juzgar_p.stdout + juzgar_p.stderr)
        self.assertIn("SIN MIRAR", juzgar_p.stdout)

        # 5. Construir defecto: enlace roto a archivo inexistente
        doc_tarea.write_text(
            doc_tarea.read_text(encoding="utf-8") + "\n[roto](archivo-inexistente.png)\n",
            encoding="utf-8",
        )
        hechos_roto_p = run_cli("tarea", "hechos", "--proyecto", str(repo))
        self.assertEqual(hechos_roto_p.returncode, 0, hechos_roto_p.stderr)
        ruta_hechos_roto = self.escribir_evidencia(hechos_roto_p.stdout, "tracker-roto.json")

        # 6. Juzgar nuevamente: debe ser ROJO (código 1) con el testigo visible
        juzgar_roto_p = self.correr_subproceso(
            "juzgar", "--con", str(ruta_hechos_roto), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS,
        )
        self.assertEqual(juzgar_roto_p.returncode, 1, juzgar_roto_p.stdout + juzgar_roto_p.stderr)
        self.assertIn("archivo-inexistente.png", juzgar_roto_p.stdout)


class TestRevisionCorrecciones(BaseJuzgarTest):
    """Pruebas de regresión específicas para las correcciones R1 a R5 de 0.18.0."""

    def test_r1_medida_en_sombra_en_rojo_sale_cero_con_marca_y_testigo(self) -> None:
        config = json.loads((self.proyecto / "oracle.json").read_text(encoding="utf-8"))
        config["sombra"] = {
            POLITICA_REFERENCIAS: {
                "desde": "2026-09-15",
                "porque": "deuda construida para la revisión",
            }
        }
        (self.proyecto / "oracle.json").write_text(json.dumps(config), encoding="utf-8")
        con = self.escribir_evidencia({
            "referencia_seguimiento": [_fila_referencia("ausente", "en-sombra.png")]
        })
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS,
        )
        self.assertEqual(rc, 0, f"stdout: {out}\nstderr: {err}")
        self.assertIn("[EN SOMBRA]", out)
        self.assertIn("2026-09-15", out)
        self.assertIn("deuda construida para la revisión", out)
        self.assertIn("en-sombra.png", out)
        self.assertIn("SIN MIRAR", out)

    def test_r1_todas_aplicables_en_sombra_en_rojo_dice_verde_por_sombra(self) -> None:
        config = json.loads((self.proyecto / "oracle.json").read_text(encoding="utf-8"))
        config["sombra"] = {
            POLITICA_REFERENCIAS: {
                "desde": "2026-09-15",
                "porque": "en transición",
            }
        }
        (self.proyecto / "oracle.json").write_text(json.dumps(config), encoding="utf-8")
        con = self.escribir_evidencia({
            "referencia_seguimiento": [_fila_referencia("ausente", "rota.png")]
        })
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS,
        )
        self.assertEqual(rc, 0)
        self.assertIn("verde por sombra", out)
        self.assertNotIn("VEREDICTO: verde en 1 medidas.", out)

    def test_r1_json_agrega_campo_en_sombra_sin_remover_ni_renombrar(self) -> None:
        config = json.loads((self.proyecto / "oracle.json").read_text(encoding="utf-8"))
        config["sombra"] = {
            POLITICA_REFERENCIAS: {
                "desde": "2026-09-15",
                "porque": "auditoría en curso",
            }
        }
        (self.proyecto / "oracle.json").write_text(json.dumps(config), encoding="utf-8")
        con = self.escribir_evidencia({
            "referencia_seguimiento": [_fila_referencia("ausente", "rota.png")]
        })
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS, "--json",
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        self.assertIs(datos["ok"], True)
        self.assertEqual(len(datos["medidas"]), 1)
        m = datos["medidas"][0]
        self.assertEqual(m["id"], POLITICA_REFERENCIAS)
        self.assertIs(m["ok"], False)
        self.assertIs(m["en_sombra"], True)
        # Claves originales intactas
        for clave in ("id", "valor", "ok", "umbral", "porque", "alcance", "sin_evidencia", "testigos"):
            self.assertIn(clave, m)

    def test_r1_rojo_fuera_de_sombra_con_rojo_en_sombra_sale_uno(self) -> None:
        config = json.loads((self.proyecto / "oracle.json").read_text(encoding="utf-8"))
        config["sombra"] = {
            POLITICA_REFERENCIAS: {"desde": "2026-09-15", "porque": "sombra"}
        }
        (self.proyecto / "oracle.json").write_text(json.dumps(config), encoding="utf-8")
        con = self.escribir_evidencia({
            "referencia_seguimiento": [_fila_referencia("ausente", "rota.png")],
            "lectura_seguimiento": [
                {"esquema": "oracle.tareas.hechos/v1", "completa": False,
                 "git": "no_solicitado", "head": ""}
            ],
        })
        rc, out, err = self.correr_cli(
            "juzgar", "--con", str(con), "--proyecto", str(self.proyecto),
            "--medida", POLITICA_REFERENCIAS, "--medida", POLITICA_LECTURA,
        )
        self.assertEqual(rc, 1)
        self.assertIn("1 de 2 medidas en rojo", out)

    def test_r2_despacho_unico_cli(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        rc1, out1, _ = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
        rc2, out2, _ = self.correr_cli("proyecto", "juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
        self.assertEqual(rc1, rc2)
        self.assertEqual(out1, out2)

    def test_r3_alias_y_verbos_aceptados_revertidos(self) -> None:
        self.assertNotIn(("oracle", "juzgar"), cli.ALIAS)
        self.assertIn("juzgar", cli.verbos_aceptados("proyecto"))
        with self.assertRaises(KeyError):
            cli.verbos_aceptados("sustantivo_inexistente")

    def test_r4_excepciones_acotadas_a_entrada_y_catalogo(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        with patch("tools.juzgar.evaluar_conjunto", side_effect=ErrorDeAlgebra("error de algebra")):
            rc, out, err = self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))
            self.assertEqual(rc, 2)
            self.assertIn("ERROR AL EVALUAR", err)

        with patch("tools.juzgar.evaluar_conjunto", side_effect=RuntimeError("bug inesperado del motor")):
            with self.assertRaises(RuntimeError):
                self.correr_cli("juzgar", "--con", str(con), "--proyecto", str(self.proyecto))

    def test_r5_tokens_sueltos_rechazados_con_codigo_dos(self) -> None:
        con = self.escribir_evidencia({"referencia_seguimiento": [_fila_referencia()]})
        casos = [
            ("juzgar", "--con", str(con), "--proyecto", str(self.proyecto), "proyecto"),
            ("juzgar", "--con", str(con), "--proyecto", str(self.proyecto), "juzgar"),
            ("proyecto", "juzgar", "--con", str(con), "--proyecto", str(self.proyecto), "extra"),
        ]
        for cmd in casos:
            with self.subTest(cmd=cmd):
                rc, out, err = self.correr_cli(*cmd)
                self.assertEqual(rc, 2)
                self.assertIn("argumento desconocido", err)


if __name__ == "__main__":
    unittest.main()
