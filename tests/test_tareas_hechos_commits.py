"""Los commits como hechos del tracker: `commit_seguimiento` y lo que cada tarea recibe de ellos.

La convención de Oracle desde 0.18.0 es que cada commit de una tarea empiece con su ID y que el que
la cierra sea `<ID>: done`. Hasta acá eso era prosa: nada lo medía. Estos tests fijan lo que el
tracker EMITE; quién juzga si está bien son las medidas de `ejemplo/seguimiento-tareas/`, escritas en
el lenguaje.
"""

from __future__ import annotations

import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools import cli, tareas_git
from tools.tareas_hechos import _commit_del_tracker


def _git(raiz: Path, *orden: str) -> None:
    subprocess.run(["git", "-C", str(raiz), "-c", "user.email=t@t", "-c", "user.name=t", *orden],
                   capture_output=True, check=True)


class LecturaDelAsuntoTests(unittest.TestCase):
    """El asunto es lo único que la convención fija, y acá no se juzga: se declara qué dice."""

    ESTADOS = {"20260916-010101-uno": "CERRADA", "20260916-020202-dos": "ABIERTA"}

    def _fila(self, asunto: str) -> dict:
        return _commit_del_tracker({"sha": "abc123", "asunto": asunto}, self.ESTADOS)

    def test_un_commit_que_nombra_una_tarea_que_existe(self) -> None:
        fila = self._fila("20260916-020202-dos: arregla el sensor")
        self.assertEqual(
            fila,
            {"sha": "abc123", "asunto": "20260916-020202-dos: arregla el sensor",
             "nombra_tarea": True, "tarea_nombrada": "20260916-020202-dos", "tarea_existe": True,
             "estado_de_la_tarea": "ABIERTA", "es_cierre": False})

    def test_un_commit_que_nombra_una_tarea_que_no_existe(self) -> None:
        fila = self._fila("20260916-030303-fantasma: done")
        self.assertTrue(fila["nombra_tarea"])
        self.assertFalse(fila["tarea_existe"])
        self.assertEqual(fila["estado_de_la_tarea"], "")
        self.assertTrue(fila["es_cierre"])

    def test_un_commit_que_no_nombra_ninguna_tarea(self) -> None:
        fila = self._fila("arregla un typo del README")
        self.assertFalse(fila["nombra_tarea"])
        self.assertEqual(fila["tarea_nombrada"], "")
        self.assertFalse(fila["tarea_existe"])
        self.assertFalse(fila["es_cierre"])

    def test_el_cierre_es_done_y_nada_mas(self) -> None:
        """Estricto a propósito: un asunto que sigue con otra cosa —una firma pegada, por ejemplo—
        no es el commit de cierre que la convención pide, y que la medida lo vea es el punto."""
        self.assertTrue(self._fila("20260916-010101-uno: done")["es_cierre"])
        self.assertTrue(self._fila("20260916-010101-uno:done")["es_cierre"])
        self.assertFalse(
            self._fila("20260916-010101-uno: done Co-Authored-By: alguien")["es_cierre"])
        self.assertFalse(self._fila("20260916-010101-uno: done y algo más")["es_cierre"])
        self.assertFalse(self._fila("20260916-010101-uno: casi done")["es_cierre"])

    def test_un_id_sin_sufijo_tambien_es_un_id(self) -> None:
        fila = self._fila("20260916-040404: empieza")
        self.assertTrue(fila["nombra_tarea"])
        self.assertEqual(fila["tarea_nombrada"], "20260916-040404")

    def test_lo_que_se_parece_a_un_id_y_no_lo_es(self) -> None:
        for asunto in ("2026-09-16: arregla", "20260916-0101: arregla",
                       "20260916-010101 sin dos puntos", "x20260916-010101-uno: arregla"):
            with self.subTest(asunto):
                self.assertFalse(self._fila(asunto)["nombra_tarea"])


class CommitsDelRepositorioTests(unittest.TestCase):
    def test_sin_repositorio_devuelve_None_y_no_una_lista_vacia(self) -> None:
        """«No hay con qué mirar» es distinto de «no hay commits», y de esa diferencia depende que
        una política no se ponga verde por ausencia de evidencia."""
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(tareas_git.commits(Path(d)))

    def test_un_repositorio_sin_un_solo_commit_no_es_un_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            _git(raiz, "init", "-q")
            self.assertEqual(tareas_git.commits(raiz), [])

    def test_el_sha_y_el_asunto_de_cada_commit_del_mas_nuevo_al_mas_viejo(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            _git(raiz, "init", "-q")
            for texto in ("uno", "dos"):
                (raiz / f"{texto}.txt").write_text(texto, encoding="utf-8")
                _git(raiz, "add", "-A")
                _git(raiz, "commit", "-qm", f"20260916-010101-x: {texto}")
            filas = tareas_git.commits(raiz)
        self.assertEqual([f["asunto"] for f in filas],
                         ["20260916-010101-x: dos", "20260916-010101-x: uno"])
        self.assertEqual({len(f["sha"]) for f in filas}, {40})

    def test_un_asunto_con_el_separador_adentro_no_parte_la_fila(self) -> None:
        """El separador es \\x1f, que no aparece en un mensaje escrito por una persona; el test está
        para que se note si algún día se cambia por algo que sí."""
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            _git(raiz, "init", "-q")
            (raiz / "a.txt").write_text("a", encoding="utf-8")
            _git(raiz, "add", "-A")
            _git(raiz, "commit", "-qm", "20260916-010101-x: con : dos puntos y más")
            filas = tareas_git.commits(raiz)
        self.assertEqual(filas[0]["asunto"], "20260916-010101-x: con : dos puntos y más")


class HechosConCommitsTests(unittest.TestCase):
    """De punta a punta: `oracle tarea hechos --git` sobre un tracker de verdad."""

    def _callado(self, *argumentos: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                rc = cli.main(list(argumentos))
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else (1 if e.code else 0)
        return rc, out.getvalue()

    def _proyecto(self, raiz: Path) -> str:
        self._callado("--proyecto", str(raiz), "tarea", "init")
        rc, salida = self._callado("--proyecto", str(raiz), "tarea", "nueva", "una tarea",
                                   "--sufijo", "una", "--json")
        self.assertEqual(rc, 0)
        return json.loads(salida)["id"]

    def test_los_commits_llegan_y_cada_tarea_cuenta_los_suyos(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d).resolve()
            _git(raiz, "init", "-q")
            tarea = self._proyecto(raiz)
            _git(raiz, "add", "-A")
            _git(raiz, "commit", "-qm", f"{tarea}: nueva tarea")
            (raiz / "otro.txt").write_text("x", encoding="utf-8")
            _git(raiz, "add", "-A")
            _git(raiz, "commit", "-qm", "un commit que no nombra ninguna tarea")
            (raiz / "otro.txt").write_text("y", encoding="utf-8")
            _git(raiz, "add", "-A")
            _git(raiz, "commit", "-qm", "20260101-000000-inventada: done")

            rc, salida = self._callado("--proyecto", str(raiz), "tarea", "hechos", "--git")
            self.assertEqual(rc, 0)
            datos = json.loads(salida)

        commits = datos["commit_seguimiento"]
        self.assertEqual(len(commits), 3)
        self.assertEqual([c["nombra_tarea"] for c in commits], [True, False, True])
        inventada = commits[0]
        self.assertEqual(inventada["tarea_nombrada"], "20260101-000000-inventada")
        self.assertFalse(inventada["tarea_existe"])
        self.assertTrue(inventada["es_cierre"])

        suya, = [t for t in datos["tarea_seguimiento"] if t["id"] == tarea]
        # Desde 0.26.0 el cruce tarea-commit lo hace la medida con `sin`: el emisor ya no cuenta.
        self.assertNotIn("commits_que_la_nombran", suya)
        self.assertNotIn("commits_de_cierre", suya)

    def test_sin_git_la_relacion_viene_vacia(self) -> None:
        """Sin `--git` no se le pregunta a la historia, y lo que no se miró no se inventa."""
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d).resolve()
            tarea = self._proyecto(raiz)
            rc, salida = self._callado("--proyecto", str(raiz), "tarea", "hechos")
            self.assertEqual(rc, 0)
            datos = json.loads(salida)
        self.assertEqual(datos["commit_seguimiento"], [])
        suya, = [t for t in datos["tarea_seguimiento"] if t["id"] == tarea]
        self.assertNotIn("commits_de_cierre", suya)

    def test_dos_corridas_sobre_la_misma_historia_emiten_lo_mismo(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d).resolve()
            _git(raiz, "init", "-q")
            tarea = self._proyecto(raiz)
            _git(raiz, "add", "-A")
            _git(raiz, "commit", "-qm", f"{tarea}: done")
            _, una = self._callado("--proyecto", str(raiz), "tarea", "hechos", "--git")
            _, otra = self._callado("--proyecto", str(raiz), "tarea", "hechos", "--git")
        self.assertEqual(una, otra)


if __name__ == "__main__":
    unittest.main()
