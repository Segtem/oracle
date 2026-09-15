"""Revisión independiente de las consultas de tareas (0.19.0).

Escrita por Claude contra `estudios/0.19.0-tql/ENCARGO-AGY.md`, antes de leer la implementación.
Todo pasa por el CLI público y trackers temporales con IDs fijos.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parents[1]
CLI = RAIZ / "tools/cli.py"

A = "20260915-100000-a"   # P90 [bug, ui]
B = "20260915-100001-b"   # P50 [bug]
C = "20260915-100002-c"   # P50 sin etiquetas
D = "20260915-100003-d"   # P10 [Scope] cerrada
ABIERTAS_POR_PRIORIDAD = [A, B, C]


class TrackerTemporal(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(prefix="oracle-consulta-revision-")
        self.addCleanup(td.cleanup)
        self.temporal = Path(td.name)
        self.raiz = self.temporal / "proyecto"
        (self.raiz / "tareas").mkdir(parents=True)
        self.env = {k: v for k, v in os.environ.items() if k != "ORACLE_PROYECTO"}
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"
        for ident, prioridad, etiquetas, estado in ((A, 90, "bug, ui", "ABIERTA"),
                                                    (B, 50, "bug", "ABIERTA"),
                                                    (C, 50, "", "ABIERTA"),
                                                    (D, 10, "Scope", "CERRADA")):
            carpeta = self.raiz / "tareas" / ident
            carpeta.mkdir()
            (carpeta / "TAREA.md").write_text(
                f"# Tarea {ident[-1]}\n\n- ESTADO: {estado}\n- PRIORIDAD: {prioridad}\n"
                f"- ETIQUETAS: {etiquetas}\n\n", encoding="utf-8")

    def cli(self, *args, cwd=None, proyecto=True):
        extra = ("--proyecto", str(self.raiz)) if proyecto else ()
        return subprocess.run([sys.executable, "-B", str(CLI), "tarea", *args, *extra],
                              env=self.env, capture_output=True, text=True, timeout=60,
                              cwd=cwd or self.temporal)

    def ids(self, *args):
        p = self.cli("listar", *args, "--json")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return [t["id"] for t in json.loads(p.stdout)]

    def instantanea(self):
        return {str(p.relative_to(self.temporal)): p.read_bytes()
                for p in sorted(self.temporal.rglob("*")) if p.is_file()}


class LenguajeTests(TrackerTemporal):
    def test_sin_consulta_es_cualquiera(self):
        self.assertEqual(self.ids(), ABIERTAS_POR_PRIORIDAD)
        self.assertEqual(self.ids("cualquiera"), ABIERTAS_POR_PRIORIDAD)

    def test_etiqueta_no_y_o(self):
        self.assertEqual(self.ids(":bug"), [A, B])
        self.assertEqual(self.ids(":bug", "y", "no", ":ui"), [B])
        self.assertEqual(self.ids(":ui", "o", "no", "etiquetada"), [A, C])

    def test_etiquetas_sin_distinguir_mayusculas(self):
        self.assertEqual(self.ids(":BUG"), [A, B])
        self.assertEqual(self.ids(":scope", "--todas"), [D])

    def test_y_liga_antes_que_o_y_no_se_aplica_a_una_primaria(self):
        # :ui o :bug y no etiquetada  ==  :ui o (:bug y no etiquetada)  ==  A
        self.assertEqual(self.ids(":ui", "o", ":bug", "y", "no", "etiquetada"), [A])
        self.assertEqual(self.ids("[", ":ui", "o", ":bug", "]", "y", "no", "etiquetada"), [])
        self.assertEqual(self.ids("no", ":ui", "y", ":bug"), [B])

    def test_comparadores_en_el_borde(self):
        casos = {"menor": [], "hasta": [B, C], "mayor": [A], "desde": [A, B, C],
                 "igual": [B, C], "distinto": [A]}
        for comparador, esperado in casos.items():
            with self.subTest(comparador):
                self.assertEqual(self.ids("prioridad", comparador, "50"), esperado)

    def test_enteros_negativos_y_comparaciones_con_la_prioridad_a_la_derecha(self):
        self.assertEqual(self.ids("prioridad", "mayor", "-1"), ABIERTAS_POR_PRIORIDAD)
        self.assertEqual(self.ids("60", "menor", "prioridad"), [A])

    def test_id_exacto_y_no_prefijo(self):
        self.assertEqual(self.ids(B), [B])
        # `20260915-100001` también es un ID válido (sin sufijo): no coincide con ninguna tarea.
        self.assertEqual(self.ids("20260915-100001"), [])

    def test_la_consulta_se_suma_a_las_banderas(self):
        self.assertEqual(self.ids(":bug", "--etiqueta", "ui"), [A])
        self.assertEqual(self.ids("cualquiera", "--cerradas"), [D])


class ErroresTests(TrackerTemporal):
    def test_consultas_invalidas_salen_dos_con_posicion(self):
        casos = {
            "primaria esperada": (":bug y",),
            "token inesperado": (":bug", "inventado"),
            "corchete sin cerrar": ("[", ":bug"),
            "etiqueta vacia": (":",),
            "tipo: comparar booleano": (":bug", "menor", "3"),
            "tipo: resultado entero": ("prioridad",),
            "tipo: y con entero": ("prioridad", "y", ":bug"),
        }
        for nombre, consulta in casos.items():
            with self.subTest(nombre):
                p = self.cli("listar", *consulta)
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn("^", p.stderr)
                self.assertNotIn("Traceback", p.stderr)
                self.assertEqual(p.stdout.strip(), "")

    def test_la_columna_cuenta_caracteres_y_no_bytes(self):
        p = self.cli("listar", ":ñandú", "inventado")
        self.assertEqual(p.returncode, 2, p.stderr)
        lineas = p.stderr.splitlines()
        i = next(n for n, l in enumerate(lineas) if ":ñandú inventado" in l)
        self.assertEqual(lineas[i + 1].index("^"), lineas[i].index("inventado"))

    def test_el_error_de_tipo_no_espera_a_leer_tareas(self):
        vacio = self.temporal / "sin-tracker"
        vacio.mkdir()
        p = subprocess.run([sys.executable, "-B", str(CLI), "tarea", "listar", "prioridad",
                            "--proyecto", str(vacio)],
                           env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn("^", p.stderr)


class ExplicarYOrdenTests(TrackerTemporal):
    def test_explicar_no_lista_ni_exige_tracker(self):
        vacio = self.temporal / "sin-tracker"
        vacio.mkdir()
        p = subprocess.run([sys.executable, "-B", str(CLI), "tarea", "listar", ":bug", "y", "no",
                            ":ui", "--explicar", "--proyecto", str(vacio)],
                           env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("bug", p.stdout)
        self.assertNotIn(A, p.stdout)
        otra = subprocess.run([sys.executable, "-B", str(CLI), "tarea", "listar", ":bug", "y", "no",
                               ":ui", "--explicar", "--proyecto", str(vacio)],
                              env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual(otra.stdout, p.stdout)

    def test_orden_por_id_invertir_y_los_dos(self):
        self.assertEqual(self.ids("--por-id"), [C, B, A])
        self.assertEqual(self.ids("--invertir"), [C, B, A])
        self.assertEqual(self.ids("--por-id", "--invertir"), [A, B, C])


class DesetiquetarConsultaTests(TrackerTemporal):
    def etiquetas(self, ident):
        texto = (self.raiz / "tareas" / ident / "TAREA.md").read_text(encoding="utf-8")
        return next(l for l in texto.splitlines() if l.startswith("- ETIQUETAS:"))

    def test_quita_solo_en_las_que_cumplen_y_respeta_el_estado(self):
        p = self.cli("desetiquetar", "--etiqueta", "bug", "--consulta", ":bug y no :ui")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.etiquetas(A), "- ETIQUETAS: bug, ui")
        self.assertEqual(self.etiquetas(B).rstrip(), "- ETIQUETAS:")
        p = self.cli("desetiquetar", "--etiqueta", "scope", "--consulta", ":scope")
        self.assertEqual(self.etiquetas(D), "- ETIQUETAS: Scope")
        self.cli("desetiquetar", "--etiqueta", "scope", "--consulta", ":scope", "--todas")
        self.assertEqual(self.etiquetas(D).rstrip(), "- ETIQUETAS:")

    def test_con_ids_o_invalida_sale_dos_sin_escribir(self):
        antes = self.instantanea()
        for args in (("--etiqueta", "bug", "--consulta", ":bug", A),
                     ("--etiqueta", "bug", "--consulta", ":bug y")):
            with self.subTest(args=args):
                p = self.cli("desetiquetar", *args)
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertNotIn("Traceback", p.stderr)
        self.assertEqual(self.instantanea(), antes)


class ReferenciasEInitTests(TrackerTemporal):
    def test_referencias_sin_id_desde_la_tarea_o_un_subdirectorio(self):
        (self.raiz / "codigo.py").write_text(f"# ver {B}\n", encoding="utf-8")
        carpeta = self.raiz / "tareas" / B
        sub = carpeta / "notas"
        sub.mkdir()
        for cwd in (carpeta, sub):
            with self.subTest(cwd=cwd.name):
                p = self.cli("referencias", cwd=cwd, proyecto=False)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                self.assertIn("codigo.py", p.stdout)

    def test_referencias_sin_id_fuera_de_una_tarea_sale_dos(self):
        p = self.cli("referencias", cwd=self.raiz, proyecto=False)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stderr)

    def test_init_sin_readme(self):
        nuevo = self.temporal / "nuevo"
        nuevo.mkdir()
        p = subprocess.run([sys.executable, "-B", str(CLI), "tarea", "init", "--sin-readme",
                            "--proyecto", str(nuevo)],
                           env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue((nuevo / "tareas").is_dir())
        self.assertFalse((nuevo / "tareas" / "README.md").exists())
        r = subprocess.run([sys.executable, "-B", str(CLI), "tarea", "revisar", "--proyecto", str(nuevo)],
                           env=self.env, capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()


class RevisionDeLaEntregaTests(TrackerTemporal):
    """Revisión de la entrega de agy: lo que el encargo no pedía y lo que tiene que coincidir."""

    def test_los_simbolos_no_son_comparadores(self):
        for simbolo in ("<", "<=", ">", ">=", "==", "=", "!="):
            with self.subTest(simbolo=simbolo):
                p = self.cli("listar", "prioridad", simbolo, "50")
                self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
                self.assertIn("^", p.stderr)

    def test_el_id_de_la_consulta_es_el_del_tracker(self):
        from tools import tareas, tareas_consulta
        self.assertEqual(tareas_consulta.ID_COMPLETO_RE.pattern, tareas.ID_COMPLETO_RE.pattern)

    def test_desetiquetar_muestra_la_posicion_como_listar(self):
        p = self.cli("desetiquetar", "--etiqueta", "bug", "--consulta", ":bug y")
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertIn(":bug y\n", p.stderr)
        self.assertIn("^", p.stderr)
