"""Revisión independiente de 0.22.0: campos de las relaciones, `campo_leido` y lo que no se pudo juzgar.

Escrita por Claude contra `estudios/0.22.0-campos/ENCARGO-AGY.md`, antes de leer la implementación.
Tarea `20260915-155654-campos`. Fija sólo lo que el encargo nombra: el lector de campos, `Informe`,
`_politicas_ok` de `mutar.py`, las declaraciones de `relaciones/` y la conducta de `aceptacion` y
`oracle juzgar` desde afuera.
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nucleo.medida import Informe, Veredicto, como_hechos, relaciones_del_lenguaje_declaradas

RAIZ = Path(__file__).resolve().parents[1]
CLI = RAIZ / "tools/cli.py"


class CamposDeRelacionesTests(unittest.TestCase):
    def test_toda_relacion_del_lenguaje_y_campo_leido_declaran_sus_campos(self):
        from nucleo.relacion import campos_de_relaciones_declarados
        campos = campos_de_relaciones_declarados()
        lenguaje = relaciones_del_lenguaje_declaradas()
        self.assertIn("campo_leido", lenguaje)
        self.assertEqual(set(campos), set(lenguaje))
        for relacion, nombres in campos.items():
            with self.subTest(relacion):
                self.assertTrue(nombres)
                self.assertEqual(len(nombres), len(set(nombres)))
        self.assertEqual(set(campos["campo_leido"]), {"medida", "relacion", "campo", "origen", "existe"})

    def test_las_filas_emitidas_traen_exactamente_los_campos_declarados(self):
        from nucleo.proyecto import Proyecto, catalogo_efectivo, relaciones_del_proyecto
        from nucleo.relacion import (ambitos_de_relaciones_declarados, campos_de_relaciones_declarados,
                                     hechos_de_relaciones)
        from nucleo.unidad import hechos_de_unidades
        from oracle_metalenguaje.motor import registro_base
        campos = campos_de_relaciones_declarados()
        proy = Proyecto(RAIZ)
        catalogo = catalogo_efectivo(proy, registro=registro_base())
        relaciones = relaciones_del_proyecto(proy)
        emitidas = {**como_hechos(catalogo.values()).por_relacion,
                    **hechos_de_relaciones(relaciones.values(), ambitos=ambitos_de_relaciones_declarados()),
                    **hechos_de_unidades(catalogo.values(), relaciones)}
        for relacion, filas in emitidas.items():
            with self.subTest(relacion):
                self.assertTrue(filas, "sin filas no se comprueba nada")
                for fila in filas:
                    self.assertEqual(set(fila), set(campos[relacion]))

    def test_las_relaciones_de_proceso_que_lee_el_catalogo_estan_declaradas(self):
        from nucleo.relacion import cargar_relaciones
        declaradas = cargar_relaciones(RAIZ / "relaciones")
        for relacion in ("corrida_mutacion", "archivo", "modulo", "alcanzable", "afirmacion", "hallazgo"):
            with self.subTest(relacion):
                self.assertIn(relacion, declaradas)


class NoJuzgaronTests(unittest.TestCase):
    VERDE = Veredicto("d.verde", 0, True, "<= 0", "razón", "alcance", ())

    def test_una_medida_que_no_juzgo_quita_el_verde_y_se_informa_aparte(self):
        informe = Informe((self.VERDE,), no_juzgaron=(("d.rota", "«==» sobre un valor ausente"),))
        self.assertIs(informe.ok, False)
        self.assertIn("d.rota", informe.texto())
        self.assertIn("valor ausente", informe.texto())
        datos = json.loads(informe.a_json())
        self.assertFalse(datos["ok"])
        self.assertEqual(datos["no_juzgaron"], [{"id": "d.rota", "motivo": "«==» sobre un valor ausente"}])

    def test_sin_ninguna_que_no_juzgo_nada_cambia(self):
        informe = Informe((self.VERDE,))
        self.assertTrue(informe.ok)
        self.assertEqual(json.loads(informe.a_json())["no_juzgaron"], [])
        self.assertNotIn("valor ausente", informe.texto())

    def test_mutar_cuenta_una_que_no_juzgo_como_politica_incumplida(self):
        from tools.mutar import _politicas_ok
        self.assertTrue(_politicas_ok(Informe((self.VERDE,))))
        self.assertFalse(_politicas_ok(Informe((self.VERDE,), no_juzgaron=(("d.rota", "motivo"),))))


class AceptacionTests(unittest.TestCase):
    """De punta a punta, en proceso, como `tests/test_sombras_integracion.py`."""

    def _proyecto(self, raiz: Path, campo_leido: str):
        from nucleo.proyecto import Proyecto
        (raiz / "catalogos" / "demo").mkdir(parents=True)
        (raiz / "corpus" / "demo").mkdir(parents=True)
        (raiz / "relaciones").mkdir()
        (raiz / "relaciones" / "item.json").write_text(json.dumps([
            "relacion", "item",
            ["campos", ["campo", "id", "texto", "sin_unidad"], ["campo", "mal", "booleano", "sin_unidad"]],
            ["alcance", "NO dice por qué un item está mal"],
        ]), encoding="utf-8")
        (raiz / "catalogos" / "demo" / "demo.items_malos.oracle").write_text(
            "ninguno demo.items_malos:\n"
            "    de item i\n"
            f"    donde i.{campo_leido} == true\n"
            "    umbral <= 0 segun contrato porque \"ningun item malo pasa\"\n"
            "    ambito universal\n"
            "    alcance \"NO ve campos distintos del que lee\"\n", encoding="utf-8")
        (raiz / "corpus" / "demo" / "001-item-malo.caso").write_text(
            "caso 001-item-malo:\n"
            "    fecha: \"2026-09-15\"\n"
            "    origen:\n"
            "        repo: \"prueba\"\n"
            "        commit: \"sin-commit\"\n"
            "    procedencia: construida\n"
            "    titulo: \"Un item malo la pone roja\"\n"
            "    etiqueta: falso_verde\n"
            "    sintoma:\n"
            "        Un item malo tiene que ponerla roja.\n"
            "    como_se_detecto: observacion\n"
            "    medida: demo.items_malos\n"
            "    evidencia:\n"
            "        item: id, mal\n"
            "            \"a\", true\n"
            "    leccion:\n"
            "        Sin este caso la medida nunca falla.\n", encoding="utf-8")
        (raiz / "oracle.json").write_text(json.dumps({"esquema": "oracle.proyecto/v1", "catalogo_base": True}),
                                          encoding="utf-8")
        return Proyecto(raiz)

    def _correr(self, proy):
        from tools import aceptacion
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = aceptacion._ejecutar(proy)
        return rc, salida.getvalue()

    def _linea(self, salida: str, mid: str) -> str:
        return next((l for l in salida.splitlines() if mid in l and ("✓" in l or "✗" in l)), "")

    def test_un_campo_que_no_existe_pone_roja_la_meta_y_no_revienta(self):
        with tempfile.TemporaryDirectory() as td:
            rc, salida = self._correr(self._proyecto(Path(td), "malo"))
        self.assertEqual(rc, 1)
        self.assertIn("✗", self._linea(salida, "meta.toda_medida_lee_campos_que_existen"), salida[-2000:])
        self.assertIn("demo.items_malos", salida)

    def test_un_campo_que_existe_deja_verde_la_meta(self):
        with tempfile.TemporaryDirectory() as td:
            _rc, salida = self._correr(self._proyecto(Path(td), "mal"))
        self.assertIn("✓", self._linea(salida, "meta.toda_medida_lee_campos_que_existen"), salida[-2000:])


class JuzgarTests(unittest.TestCase):
    def test_una_medida_que_no_puede_juzgar_sale_dos_sin_traceback_y_dice_cual(self):
        with tempfile.TemporaryDirectory(prefix="oracle-campos-revision-") as td:
            temporal = Path(td)
            proyecto = temporal / "politicas"
            (proyecto / "catalogos" / "demo").mkdir(parents=True)
            (proyecto / "oracle.json").write_text(json.dumps({"esquema": "oracle.proyecto/v1"}), encoding="utf-8")
            (proyecto / "catalogos" / "demo" / "demo.items_malos.oracle").write_text(
                "ninguno demo.items_malos:\n"
                "    de item i\n"
                "    donde i.mal == true\n"
                "    umbral <= 0 segun contrato porque \"ningun item malo pasa\"\n"
                "    ambito universal\n"
                "    alcance \"NO ve otra cosa\"\n", encoding="utf-8")
            evidencia = temporal / "hechos.json"
            evidencia.write_text(json.dumps({"item": [{"id": "a"}]}), encoding="utf-8")
            env = {k: v for k, v in os.environ.items() if k != "ORACLE_PROYECTO"}
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            p = subprocess.run([sys.executable, "-B", str(CLI), "juzgar", "--con", str(evidencia),
                                "--proyecto", str(proyecto)],
                               env=env, capture_output=True, text=True, timeout=60, cwd=temporal)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stdout + p.stderr)
        self.assertIn("demo.items_malos", p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
