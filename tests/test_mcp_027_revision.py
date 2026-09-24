"""Tests de revisión del MCP de 0.27.0, escritos por Claude ANTES de leer la entrega de agy.

Fijan el encargo (`vault-kb/estudios/0.27.0-mcp/ENCARGO-AGY.md`) desde el protocolo: `tools/list` y
`tools/call`, sin nombres internos. Corren sobre una copia de `ejemplo/seguimiento-tareas`, que tiene
tracker propio no, pero sí políticas y una sombra con cota; el tracker se arma en el temporal.
"""

from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tests.test_mcp import _conversacion, _desenmarcar
from tools import cli, mcp

RAIZ = Path(__file__).resolve().parents[1]
CIERRES = "seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre"
REFERENCIAS = "seguimiento.referencias_locales_presentes"
LECTURA = "seguimiento.lectura_sin_omisiones"
SOLO_LECTURA = {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True,
                "openWorldHint": False}


def _referencia(estado: str) -> dict:
    return {"tarea_id": "20260915-100000-tarea", "origen": "tareas/20260915-100000-tarea/TAREA.md",
            "linea": 5, "destino_declarado": "x.png", "clase": "local", "estado": estado}


def _tarea(id_: str, estado: str) -> dict:
    return {"id": id_, "estado_declarado": estado, "titulo": "t", "prioridad_declarada": 50,
            "ruta": f"tareas/{id_}/TAREA.md", "sha256_documento": "0" * 64}


def _commit(tarea: str, cierre: bool) -> dict:
    return {"sha": "a" * 40, "asunto": f"{tarea}: {'done' if cierre else 'algo'}",
            "nombra_tarea": True, "tarea_nombrada": tarea, "tarea_existe": True,
            "estado_de_la_tarea": "CERRADA", "es_cierre": cierre}


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.raiz = Path(self._td.name) / "proyecto"
        shutil.copytree(RAIZ / "ejemplo" / "seguimiento-tareas", self.raiz,
                        ignore=shutil.ignore_patterns("__pycache__"))

    def tearDown(self) -> None:
        self._td.cleanup()

    def llamar(self, nombre: str, argumentos: dict) -> dict:
        pedido = {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                  "params": {"name": nombre, "arguments": argumentos}}
        salida = io.BytesIO()
        mcp.servir(mcp.Proyecto(self.raiz), io.BytesIO(_conversacion(pedido)), salida)
        return _desenmarcar(salida.getvalue())[1]["result"]

    def ok(self, nombre: str, argumentos: dict) -> dict:
        r = self.llamar(nombre, argumentos)
        self.assertIs(r["isError"], False, r)
        return r["structuredContent"]

    def sombra(self, mid: str, cota: int | None) -> None:
        ruta = self.raiz / "oracle.json"
        config = json.loads(ruta.read_text(encoding="utf-8"))
        entrada = {"desde": "2026-09-16", "porque": "deuda"}
        if cota is not None:
            entrada["cota"] = cota
        config["sombra"] = {mid: entrada}
        ruta.write_text(json.dumps(config), encoding="utf-8")


class ListaTests(Base):
    def test_cinco_herramientas_todas_de_solo_lectura(self) -> None:
        salida = io.BytesIO()
        mcp.servir(mcp.Proyecto(self.raiz), io.BytesIO(_conversacion(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})), salida)
        herramientas = _desenmarcar(salida.getvalue())[1]["result"]["tools"]
        self.assertEqual(sorted(h["name"] for h in herramientas),
                         ["oracle_catalogo_efectivo", "oracle_desafiar", "oracle_evaluar",
                          "oracle_juzgar", "oracle_tareas"])
        for h in herramientas:
            self.assertEqual(h["annotations"], SOLO_LECTURA, h["name"])


class EvaluarConSombraTests(Base):
    EVIDENCIA = {"tarea_seguimiento": [_tarea("t1", "CERRADA"), _tarea("t2", "CERRADA")],
                 "commit_seguimiento": [_commit("t1", False)]}

    def evaluar(self) -> dict:
        return self.ok("oracle_evaluar", {"medida": {"id": CIERRES}, "evidencia": self.EVIDENCIA})

    def test_sin_sombra_es_null_y_el_esquema_es_v2(self) -> None:
        self.sombra(REFERENCIAS, None)
        r = self.evaluar()
        self.assertEqual(r["esquema"], "oracle.mcp/evaluacion/v2")
        self.assertIsNone(r["sombra"])
        self.assertEqual(r["estado"], "rojo")

    def test_dentro_de_la_cota_perdona(self) -> None:
        self.sombra(CIERRES, 2)
        r = self.evaluar()
        self.assertEqual(r["estado"], "rojo")
        self.assertEqual(r["sombra"], {"desde": "2026-09-16", "porque": "deuda", "cota": 2,
                                       "perdona": True})

    def test_por_encima_de_la_cota_no_perdona(self) -> None:
        self.sombra(CIERRES, 1)
        self.assertIs(self.evaluar()["sombra"]["perdona"], False)

    def test_sin_cota_perdona_y_cota_es_null(self) -> None:
        self.sombra(CIERRES, None)
        s = self.evaluar()["sombra"]
        self.assertIsNone(s["cota"])
        self.assertIs(s["perdona"], True)

    def test_un_verde_en_sombra_no_se_perdona_porque_no_hay_nada_que_perdonar(self) -> None:
        self.sombra(CIERRES, 5)
        r = self.ok("oracle_evaluar", {"medida": {"id": CIERRES}, "evidencia": {
            "tarea_seguimiento": [_tarea("t1", "CERRADA")],
            "commit_seguimiento": [_commit("t1", True)]}})
        self.assertEqual(r["estado"], "verde")
        self.assertIs(r["sombra"]["perdona"], False)

    def test_por_texto_nunca_esta_en_sombra(self) -> None:
        self.sombra(CIERRES, 5)
        texto = (self.raiz / "catalogos" / f"{CIERRES}.oracle").read_text(encoding="utf-8")
        r = self.ok("oracle_evaluar", {"medida": {"texto": texto, "formato": "oracle"},
                                       "evidencia": self.EVIDENCIA})
        self.assertIsNone(r["sombra"])


class JuzgarTests(Base):
    def test_juzga_el_catalogo_y_nombra_las_no_aplicadas(self) -> None:
        r = self.ok("oracle_juzgar", {"evidencia": {"referencia_seguimiento": [_referencia("presente")]}})
        self.assertEqual(r["esquema"], "oracle.mcp/juzgar/v1")
        self.assertIs(r["ok"], True)
        self.assertEqual([m["id"] for m in r["medidas"]], [REFERENCIAS])
        faltan = {f["id"]: f["faltan"] for f in r["no_aplicadas"]}
        self.assertEqual(faltan[LECTURA], ["lectura_seguimiento"])
        self.assertFalse(any(i.startswith("meta.") for i in faltan))
        self.assertEqual(r["no_juzgaron"], [])

    def test_un_rojo_hace_ok_falso(self) -> None:
        r = self.ok("oracle_juzgar", {"evidencia": {"referencia_seguimiento": [_referencia("ausente")]}})
        self.assertIs(r["ok"], False)
        self.assertEqual(r["medidas"][0]["estado"], "rojo")

    def test_la_sombra_con_cota_decide_ok(self) -> None:
        ev = {"referencia_seguimiento": [_referencia("ausente"), _referencia("ausente")]}
        self.sombra(REFERENCIAS, 2)
        r = self.ok("oracle_juzgar", {"evidencia": ev})
        self.assertIs(r["ok"], True)
        self.assertIs(r["medidas"][0]["sombra"]["perdona"], True)
        self.sombra(REFERENCIAS, 1)
        r = self.ok("oracle_juzgar", {"evidencia": ev})
        self.assertIs(r["ok"], False)
        self.assertIs(r["medidas"][0]["sombra"]["perdona"], False)

    def test_ids_restringe(self) -> None:
        r = self.ok("oracle_juzgar", {"evidencia": {
            "referencia_seguimiento": [_referencia("presente")],
            "lectura_seguimiento": [{"esquema": "oracle.tareas.hechos/v1", "completa": True,
                                     "git": "no_solicitado", "head": ""}]},
            "ids": [LECTURA]})
        self.assertEqual([m["id"] for m in r["medidas"]], [LECTURA])

    def test_sin_medidas_aplicables_no_es_un_verde(self) -> None:
        r = self.llamar("oracle_juzgar", {"evidencia": {"nada": [{"x": 1}]}})
        if not r["isError"]:
            self.assertIs(r["structuredContent"]["ok"], False)
            self.assertTrue(r["structuredContent"]["advertencias"])

    def test_un_id_que_no_existe_es_error(self) -> None:
        r = self.llamar("oracle_juzgar", {"evidencia": {"referencia_seguimiento": []},
                                          "ids": ["seguimiento.no_existe"]})
        self.assertIs(r["isError"], True)

    def test_ids_repetidos_es_error(self) -> None:
        r = self.llamar("oracle_juzgar", {"evidencia": {"referencia_seguimiento": []},
                                          "ids": [REFERENCIAS, REFERENCIAS]})
        self.assertIs(r["isError"], True)


class BordesDeLaMutacionTests(Base):
    """Lo que la mutación de 0.27.0 dejó vivo en `tools/mcp.py`: cada test mata uno o más."""

    def texto_de_error(self, nombre: str, argumentos) -> str:
        r = self.llamar(nombre, argumentos)
        self.assertIs(r["isError"], True, r)
        return r["content"][0]["text"]

    def test_una_propiedad_de_mas_se_nombra(self) -> None:
        self.assertIn("$.zzz", self.texto_de_error("oracle_juzgar", {"evidencia": {}, "zzz": 1}))
        self.assertIn("$.zzz", self.texto_de_error("oracle_tareas", {"accion": "listar", "zzz": 1}))

    def test_un_id_que_no_es_texto_es_argumento_invalido(self) -> None:
        self.assertTrue(self.texto_de_error("oracle_juzgar", {"evidencia": {}, "ids": [123]})
                        .startswith("ARGUMENTOS_INVALIDOS"))

    def test_git_que_no_es_booleano_es_argumento_invalido(self) -> None:
        (self.raiz / "tareas").mkdir()
        self.assertTrue(self.texto_de_error("oracle_tareas", {"accion": "hechos", "git": "si"})
                        .startswith("ARGUMENTOS_INVALIDOS"))

    def test_hechos_sin_git_no_le_pregunta_a_la_historia(self) -> None:
        (self.raiz / "tareas").mkdir()
        r = self.ok("oracle_tareas", {"accion": "hechos"})
        self.assertEqual(r["resultado"]["lectura_seguimiento"][0]["git"], "no_solicitado")

    def test_juzgar_sin_autorizacion_no_ejecuta_escalares(self) -> None:
        """Por omisión, la función tampoco confía: la autorización es del arranque."""
        (self.raiz / "escalares.py").write_text("# código externo\n", encoding="utf-8")
        with self.assertRaises(mcp.ErrorHerramienta) as ctx:
            mcp.juzgar_para_mcp(mcp.Proyecto(self.raiz), {"evidencia": {}})
        self.assertTrue(str(ctx.exception).startswith(
            f"ESCALARES_NO_AUTORIZADAS — {self.raiz / 'escalares.py'} es código externo"),
            str(ctx.exception))

    def test_los_testigos_se_cortan_en_cinco(self) -> None:
        r = self.ok("oracle_juzgar", {"evidencia": {"referencia_seguimiento": [
            _referencia("ausente") for _ in range(7)]}})
        m = r["medidas"][0]
        self.assertEqual((len(m["testigos"]), m["testigos_omitidos"]), (5, 2))

    def test_un_juicio_normal_no_trae_advertencias(self) -> None:
        r = self.ok("oracle_juzgar", {"evidencia": {"referencia_seguimiento": [_referencia("presente")]}})
        self.assertEqual(r["advertencias"], [])

    def test_la_huella_es_la_de_los_argumentos_canonicos(self) -> None:
        import hashlib
        argumentos = {"ids": [REFERENCIAS],
                      "evidencia": {"referencia_seguimiento": [dict(_referencia("presente"), nota="ñandú")]}}
        esperada = hashlib.sha256(json.dumps(argumentos, sort_keys=True, ensure_ascii=False)
                                  .encode("utf-8")).hexdigest()
        self.assertEqual(self.ok("oracle_juzgar", argumentos)["entrada_sha256"], esperada)


class TareasTests(Base):
    def setUp(self) -> None:
        super().setUp()
        with io.StringIO() as _, self._silencio():
            cli.main(["--proyecto", str(self.raiz), "tarea", "init"])
            cli.main(["--proyecto", str(self.raiz), "tarea", "nueva", "Una tarea abierta",
                      "--sufijo", "abierta", "--etiqueta", "rojo"])
            cli.main(["--proyecto", str(self.raiz), "tarea", "nueva", "Otra que se cierra",
                      "--sufijo", "cerrada"])
        self.cerrada = next(p.name for p in (self.raiz / "tareas").iterdir()
                            if p.name.endswith("-cerrada"))
        with self._silencio():
            cli.main(["--proyecto", str(self.raiz), "tarea", "cerrar", self.cerrada])

    @staticmethod
    def _silencio():
        from contextlib import redirect_stdout
        return redirect_stdout(io.StringIO())

    def test_listar_filtra_por_estado(self) -> None:
        r = self.ok("oracle_tareas", {"accion": "listar", "estado": "CERRADA"})
        self.assertEqual(r["esquema"], "oracle.mcp/tareas/v1")
        self.assertEqual(r["accion"], "listar")
        self.assertIn(self.cerrada, json.dumps(r["resultado"]))
        self.assertNotIn("-abierta", json.dumps(r["resultado"]))

    def test_listar_ordena_por_prioridad_y_sin_filtro_trae_las_abiertas(self) -> None:
        with self._silencio():
            cli.main(["--proyecto", str(self.raiz), "tarea", "nueva", "Menor",
                      "--sufijo", "menor", "--prioridad", "10"])
        # La nueva tiene el id más alto y la prioridad más baja: por id o invertido, iría primero.
        ids = [t["id"] for t in self.ok("oracle_tareas", {"accion": "listar"})["resultado"]]
        self.assertEqual([i.rsplit("-", 1)[1] for i in ids], ["abierta", "menor"])

    def test_ver_con_prefijo(self) -> None:
        r = self.ok("oracle_tareas", {"accion": "ver", "id": self.cerrada})
        self.assertIn("Otra que se cierra", json.dumps(r["resultado"], ensure_ascii=False))

    def test_ver_sin_id_es_error(self) -> None:
        self.assertIs(self.llamar("oracle_tareas", {"accion": "ver"})["isError"], True)

    def test_buscar(self) -> None:
        r = self.ok("oracle_tareas", {"accion": "buscar", "texto": "abierta"})
        self.assertIn("-abierta", json.dumps(r["resultado"]))

    def test_hechos_trae_las_relaciones_del_tracker(self) -> None:
        r = self.ok("oracle_tareas", {"accion": "hechos"})
        self.assertIn("tarea_seguimiento", r["resultado"])
        self.assertEqual(len(r["resultado"]["tarea_seguimiento"]), 2)

    def test_no_hay_acciones_que_escriban(self) -> None:
        antes = sorted(p.name for p in (self.raiz / "tareas").iterdir())
        for accion in ("nueva", "cerrar", "anotar", "reabrir", "etiquetar"):
            self.assertIs(self.llamar("oracle_tareas", {"accion": accion, "id": self.cerrada})
                          ["isError"], True, accion)
        self.assertEqual(sorted(p.name for p in (self.raiz / "tareas").iterdir()), antes)

    def test_sin_tracker_es_error_y_no_lista_vacia(self) -> None:
        shutil.rmtree(self.raiz / "tareas")
        r = self.llamar("oracle_tareas", {"accion": "listar"})
        self.assertIs(r["isError"], True)
        self.assertIn("TRACKER_AUSENTE", r["content"][0]["text"])


if __name__ == "__main__":
    unittest.main()
