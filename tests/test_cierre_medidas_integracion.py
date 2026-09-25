"""Contrato de hechos y flujo consumidor de aceptación actual para cierres."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tools import cli, tareas_hechos

RAIZ = Path(__file__).resolve().parents[1]
EJEMPLO = RAIZ / "ejemplo/seguimiento-tareas"
SPEC = importlib.util.spec_from_file_location("flujo_cierre", EJEMPLO / "cierre_medidas.py")
flujo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(flujo)
DOMINIO = "seguimiento.referencias_locales_presentes"


def resultado(datos, codigo=0):
    return subprocess.CompletedProcess([], codigo, json.dumps(datos), "")


class CierreIntegracionTests(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.addCleanup(self.td.cleanup)
        self.raiz = Path(self.td.name)
        self.proyecto = self.raiz / "dominio"
        shutil.copytree(EJEMPLO, self.proyecto)
        self.documento = self.proyecto / "tareas/20260922-010000-cierre/TAREA.md"
        self.documento.parent.mkdir(parents=True)
        self.escribir_tarea()
        self.evidencia = self.raiz / "dominio.json"
        self.evidencia.write_text(json.dumps({"referencia_seguimiento": []}))

    def escribir_tarea(self, estado="CERRADA", criterios=DOMINIO):
        self.documento.write_text(f"# Cierre\n\n- ESTADO: {estado}\n- PRIORIDAD: 50\n"
                                 f"- CIERRA CON: {criterios}\n\nCuerpo\n")

    def llamar(self, argumentos):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = cli.main(argumentos)
        return rc, out.getvalue(), err.getvalue()

    def test_hechos_siempre_presentes_deterministas_y_saneados(self):
        self.escribir_tarea(criterios="z.b, a.b, z.b")
        otra = self.documento.parent.parent / "20260922-020000-otra/TAREA.md"
        otra.parent.mkdir()
        otra.write_text("# Otra\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 1\n- CIERRA CON: a.b\n")
        args = ["tarea", "hechos", "--proyecto", str(self.proyecto)]
        rc, out, err = self.llamar(args)
        self.assertEqual(rc, 0, err)
        self.assertEqual(out, self.llamar(args)[1])
        self.assertEqual(json.loads(out)["tarea_cierre_medida"], [
            {"tarea_id": self.documento.parent.name, "medida": "z.b"},
            {"tarea_id": self.documento.parent.name, "medida": "a.b"},
            {"tarea_id": otra.parent.name, "medida": "a.b"},
        ])
        otra.unlink()
        otra.parent.rmdir()
        self.escribir_tarea(criterios="")
        self.assertEqual(tareas_hechos.extraer_hechos(self.proyecto)["tarea_cierre_medida"], [])
        self.documento.unlink()
        self.documento.parent.rmdir()
        self.assertEqual(tareas_hechos.extraer_hechos(self.proyecto)["tarea_cierre_medida"], [])

    def test_relacion_ausente_no_aplica_vacia_rechaza(self):
        hechos = tareas_hechos.extraer_hechos(self.proyecto)
        ruta = self.raiz / "tracker.json"
        for presente in (False, True):
            with self.subTest(presente=presente):
                if presente:
                    hechos["aceptacion_medida"] = []
                ruta.write_text(json.dumps(hechos))
                rc, out, err = self.llamar(["juzgar", "--proyecto", str(EJEMPLO),
                                           "--con", str(ruta), "--json"])
                self.assertIn(rc, (0, 1), err)
                datos = json.loads(out)
                if presente:
                    medida = next(m for m in datos["medidas"] if m["id"] == flujo.POLITICA)
                    self.assertIs(medida["ok"], False)
                else:
                    self.assertIn({"id": flujo.POLITICA, "faltan": ["aceptacion_medida"]}, datos["no_aplicadas"])
                    self.assertNotIn(flujo.POLITICA, [m["id"] for m in datos["medidas"]])

    def ejecutar_flujo(self):
        return subprocess.run([sys.executable, "-B", str(EJEMPLO / "cierre_medidas.py"),
                               "--proyecto", str(self.proyecto), "--con", str(self.evidencia),
                               "--tracker", str(self.proyecto)], capture_output=True, text=True)

    def test_flujo_real_verde_rojo_sombra_no_evaluada_inexistente(self):
        for caso in ("verde", "rojo", "sombra", "no_evaluada", "inexistente", "abierta", "sin_criterios"):
            with self.subTest(caso=caso):
                self.escribir_tarea(estado="ABIERTA" if caso == "abierta" else "CERRADA",
                                    criterios="" if caso == "sin_criterios" else
                                    "dominio.inexistente" if caso == "inexistente" else DOMINIO)
                datos = {"referencia_seguimiento": []}
                if caso in ("rojo", "sombra", "abierta"):
                    datos["referencia_seguimiento"] = [{"clase": "local", "estado": "ausente"}]
                if caso == "no_evaluada":
                    datos = {"lectura_seguimiento": [{"completa": True}]}
                self.evidencia.write_text(json.dumps(datos))
                config = {"esquema": "oracle.proyecto/v1", "algebra": "1.0", "catalogo_base": False, "perfiles": []}
                if caso == "sombra":
                    config["sombra"] = {DOMINIO: {"desde": "2026-09-22", "porque": "deuda construida"}}
                (self.proyecto / "oracle.json").write_text(json.dumps(config))
                p = self.ejecutar_flujo()
                esperado = caso in ("verde", "abierta", "sin_criterios")
                self.assertEqual(p.returncode, 0 if esperado else 1, p.stderr)
                medida, = json.loads(p.stdout)["medidas"]
                self.assertEqual(medida["id"], flujo.POLITICA)
                self.assertIs(medida["ok"], esperado)
                if caso == "sombra":
                    rc, out, err = self.llamar(["juzgar", "--proyecto", str(self.proyecto),
                                               "--con", str(self.evidencia), "--json"])
                    self.assertEqual(rc, 0, err)
                    self.assertIs(json.loads(out)["medidas"][0]["ok"], False)

    def test_error_tras_verde_no_reutiliza_resultado(self):
        self.assertEqual(self.ejecutar_flujo().returncode, 0)
        self.evidencia.write_text("JSON roto")
        p = self.ejecutar_flujo()
        self.assertEqual(p.returncode, 2)
        self.assertEqual(p.stdout, "")
        self.assertIn("ERROR", p.stderr)


class ConversionAceptacionTests(unittest.TestCase):
    def test_conserva_ok_individual_omite_no_aplicadas(self):
        datos = {"ok": True, "medidas": [{"id": "d.a", "ok": False, "en_sombra": True}],
                 "no_aplicadas": [{"id": "d.b", "faltan": ["r"]}]}
        self.assertEqual(flujo.convertir_aceptacion(resultado(datos)),
                         {"aceptacion_medida": [{"medida": "d.a", "ok": False}]})
        datos["medidas"] = []
        self.assertEqual(flujo.convertir_aceptacion(resultado(datos, 1)), {"aceptacion_medida": []})

    def test_rechaza_errores_y_veredictos_malformados(self):
        valido = {"ok": True, "medidas": [], "no_aplicadas": []}
        for rc in (-9, 2, 127):
            with self.subTest(rc=rc), self.assertRaises(ValueError):
                flujo.convertir_aceptacion(resultado(valido, rc))
        for datos in ([], {}, {**valido, "medidas": None},
                      {**valido, "medidas": [{"id": "d.a", "ok": "false"}]},
                      {**valido, "medidas": [{"id": "d.a", "ok": 1}]},
                      {**valido, "medidas": [{"ok": True}]},
                      {**valido, "medidas": [{"id": "d.a", "ok": True}] * 2}):
            with self.subTest(datos=datos), self.assertRaises(ValueError):
                flujo.convertir_aceptacion(resultado(datos))
        with self.assertRaises(ValueError):
            flujo.convertir_aceptacion(subprocess.CompletedProcess([], 0, "no json", ""))

    def test_error_aborta_sin_publicar_ni_llamar_politica(self):
        aceptacion = resultado({"ok": True, "medidas": [], "no_aplicadas": []})
        for respuestas in ([resultado({}, 2)], [aceptacion, resultado({}, 1)],
                           [aceptacion, resultado({})], [OSError("sin ejecutable")]):
            with self.subTest(respuestas=respuestas), mock.patch.object(
                    flujo.subprocess, "run", side_effect=respuestas) as run:
                out, err = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc = flujo.main(["--proyecto", "/dominio", "--con", "/evidencia", "--tracker", "/tracker"])
                self.assertEqual(rc, 2)
                self.assertEqual(out.getvalue(), "")
                self.assertIn("ERROR", err.getvalue())
                self.assertEqual(run.call_count, len(respuestas))
