"""Tests unitarios para las capacidades incorporadas a oracle-mcp en 0.27.0.

Cubre:
1. oracle_evaluar con sombras (con/sin cota, dentro/fuera de cota, en memoria, esquema v2).
2. oracle_juzgar (con/sin ids, medidas no aplicadas, id desconocido/no aplicable, estabilidad, ok).
3. oracle_tareas (tracker ausente, listar abierta/cerrada/etiqueta, ver id/ambiguo/inexistente, buscar, hechos).
4. Contrato normativo entero de 5 herramientas idéntico entre MCP-CONTRATO.md y tools/mcp.py.
"""

from __future__ import annotations

import io
import json
import re
import tempfile
import unittest
from pathlib import Path

from nucleo.version import VERSION_DISTRIBUCION
from tools import mcp


def _medida(mid: str, *, ambito: str = "universal", limite: int = 0,
            requiere: tuple[str, ...] = (), relacion: str = "item", segun: str = "contrato",
            porque: str = "ningún item malo") -> list:
    """Crea la estructura canónica de datos de una medida de prueba.

    La medida lee `relacion`: una medida se aplica por lo que LEE, no por lo que requiere. Sin
    `requiere`, la relación vacía es un verde; con `requiere`, es SIN EVIDENCIA.
    """
    return [
        "medida", mid,
        ["desde", ["de", relacion, "i"]],
        ["resumen", "contar", 1],
        ["umbral", "<=", limite, porque, segun],
        *([["requiere", *requiere]] if requiere else []),
        ["ambito", ambito],
        ["alcance", "NO ve propiedades distintas del conteo de items"],
    ]


def _proyecto_con_sombras(raiz: Path, medidas: list[list], sombra_dict: dict | None = None) -> Path:
    """Inicializa la estructura mínima de proyecto con medidas y configuración de sombra."""
    cat_dir = raiz / "catalogos" / "demo"
    cat_dir.mkdir(parents=True, exist_ok=True)
    for m in medidas:
        (cat_dir / f"{m[1]}.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")

    cfg: dict = {"esquema": "oracle.proyecto/v1", "catalogo_base": False}
    if sombra_dict is not None:
        cfg["sombra"] = sombra_dict
    (raiz / "oracle.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    return raiz


def _inicializar_tracker(raiz: Path) -> Path:
    """Crea la estructura de tareas de prueba dentro de raiz/tareas."""
    tareas_dir = raiz / "tareas"
    tareas_dir.mkdir(parents=True, exist_ok=True)

    t1 = tareas_dir / "20260901-100000-tarea-abierta"
    t1.mkdir()
    (t1 / "TAREA.md").write_text(
        "# Primera tarea abierta\n\n"
        "- ESTADO: ABIERTA\n"
        "- PRIORIDAD: 70\n"
        "- ETIQUETAS: bug, backend\n\n"
        "Detalle de la tarea de backend con texto para buscar.\n",
        encoding="utf-8",
    )

    t2 = tareas_dir / "20260901-110000-tarea-cerrada"
    t2.mkdir()
    (t2 / "TAREA.md").write_text(
        "# Segunda tarea cerrada\n\n"
        "- ESTADO: CERRADA\n"
        "- PRIORIDAD: 40\n"
        "- ETIQUETAS: doc\n\n"
        "Documentación técnica ya resuelta.\n",
        encoding="utf-8",
    )

    # Tarea con prefijo similar para probar ambigüedad
    t3 = tareas_dir / "20260901-120000-tarea-otra"
    t3.mkdir()
    (t3 / "TAREA.md").write_text(
        "# Tercera tarea abierta\n\n"
        "- ESTADO: ABIERTA\n"
        "- PRIORIDAD: 20\n"
        "- ETIQUETAS: frontend\n\n"
        "Vista de usuario.\n",
        encoding="utf-8",
    )

    return raiz


class ContratoNormativoTests(unittest.TestCase):
    """Verifica que el bloque JSON normativo de MCP-CONTRATO.md describe exactamente 5 herramientas."""

    def test_tools_list_publica_las_cinco_con_el_contrato_normativo_entero(self) -> None:
        contrato = (mcp.RAIZ / "docs" / "mcp-contrato.md").read_text(encoding="utf-8")
        from tools.mcp_contrato import regenerar
        self.assertEqual(contrato, regenerar(contrato), "Regenerar el contrato MCP")
        bloque = re.search(
            r"<!-- herramientas-json:inicio -->\n```json\n(.*?)\n```\n"
            r"<!-- herramientas-json:fin -->",
            contrato,
            re.DOTALL,
        )
        self.assertIsNotNone(bloque, "Falta el bloque de herramientas JSON en MCP-CONTRATO.md")
        esperadas = json.loads(bloque.group(1))

        self.assertEqual(len(esperadas), 5)
        self.assertEqual(len(mcp.HERRAMIENTAS), 5)
        self.assertEqual(
            [h["name"] for h in mcp.HERRAMIENTAS],
            [
                "oracle_catalogo_efectivo",
                "oracle_evaluar",
                "oracle_desafiar",
                "oracle_juzgar",
                "oracle_tareas",
            ],
        )
        self.assertEqual(mcp.HERRAMIENTAS, esperadas)


class EvaluarSombrasTests(unittest.TestCase):
    """Pruebas para oracle_evaluar con soporte de sombras (esquema oracle.mcp/evaluacion/v2)."""

    def test_medida_sin_sombra_devuelve_sombra_null_y_esquema_v2(self) -> None:
        m = _medida("demo.sin_sombra", limite=0)
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto_con_sombras(Path(td), [m])
            proy = mcp.Proyecto(raiz)
            res = mcp.evaluar_para_mcp(
                proy,
                {"medida": {"id": "demo.sin_sombra"}, "evidencia": {"item": []}},
            )
            self.assertEqual(res["esquema"], "oracle.mcp/evaluacion/v2")
            self.assertEqual(res["estado"], "verde")
            self.assertIsNone(res["sombra"])

    def test_medida_en_memoria_siempre_devuelve_sombra_null(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            # Incluso si oracle.json declara una sombra para ese id, en memoria nunca está en sombra
            sombra = {
                "demo.en_memoria": {
                    "desde": "2026-09-01",
                    "porque": "deuda",
                }
            }
            raiz = _proyecto_con_sombras(Path(td), [], sombra_dict=sombra)
            proy = mcp.Proyecto(raiz)
            m_datos = _medida("demo.en_memoria", limite=0)
            res = mcp.evaluar_para_mcp(
                proy,
                {
                    "medida": {"texto": json.dumps(m_datos), "formato": "json"},
                    "evidencia": {"item": [{"a": 1}]},
                },
            )
            self.assertEqual(res["esquema"], "oracle.mcp/evaluacion/v2")
            self.assertEqual(res["estado"], "rojo")
            self.assertIsNone(res["sombra"])

    def test_sombra_sin_cota_perdona_rojo(self) -> None:
        m = _medida("demo.sombra_sin_cota", limite=0)
        sombra = {
            "demo.sombra_sin_cota": {
                "desde": "2026-09-01",
                "porque": "deuda historica",
            }
        }
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto_con_sombras(Path(td), [m], sombra_dict=sombra)
            proy = mcp.Proyecto(raiz)
            res = mcp.evaluar_para_mcp(
                proy,
                {"medida": {"id": "demo.sombra_sin_cota"}, "evidencia": {"item": [{"x": 1}]}},
            )
            self.assertEqual(res["esquema"], "oracle.mcp/evaluacion/v2")
            self.assertEqual(res["estado"], "rojo")
            self.assertEqual(res["sombra"], {
                "desde": "2026-09-01",
                "porque": "deuda historica",
                "cota": None,
                "perdona": True,
            })

    def test_sombra_sin_cota_no_perdona_verde_y_si_sin_evidencia(self) -> None:
        """`perdona` es la misma pregunta que `ok` en `oracle juzgar`: sin cota, la sombra apaga
        también la consecuencia de un SIN EVIDENCIA. Un verde no tiene nada que perdonar."""
        m = _medida("demo.sombra_verde", limite=0)
        sombra = {
            "demo.sombra_verde": {
                "desde": "2026-09-01",
                "porque": "deuda",
            }
        }
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto_con_sombras(Path(td), [m], sombra_dict=sombra)
            proy = mcp.Proyecto(raiz)

            # 1. Caso verde: perdona debe ser False
            res_verde = mcp.evaluar_para_mcp(
                proy,
                {"medida": {"id": "demo.sombra_verde"}, "evidencia": {"item": []}},
            )
            self.assertEqual(res_verde["estado"], "verde")
            self.assertFalse(res_verde["sombra"]["perdona"])

            # 2. Caso sin_evidencia: sin cota, la sombra lo perdona como en juzgar
            (raiz / "catalogos" / "demo" / "demo.sombra_verde.json").write_text(json.dumps(
                _medida("demo.sombra_verde", limite=0, requiere=("item",))), encoding="utf-8")
            res_sin_ev = mcp.evaluar_para_mcp(
                proy,
                {"medida": {"id": "demo.sombra_verde"}, "evidencia": {"item": []}},
            )
            self.assertEqual(res_sin_ev["estado"], "sin_evidencia")
            self.assertTrue(res_sin_ev["sombra"]["perdona"])

    def test_sombra_con_cota_dentro_y_fuera_de_cota(self) -> None:
        m = _medida("demo.sombra_cota", limite=0)
        sombra = {
            "demo.sombra_cota": {
                "desde": "2026-09-01",
                "porque": "deuda acotada",
                "cota": 4,
            }
        }
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto_con_sombras(Path(td), [m], sombra_dict=sombra)
            proy = mcp.Proyecto(raiz)

            # Dentro de la cota: valor 4 <= 4 -> perdona True
            res_dentro = mcp.evaluar_para_mcp(
                proy,
                {
                    "medida": {"id": "demo.sombra_cota"},
                    "evidencia": {"item": [{"id": i} for i in range(4)]},
                },
            )
            self.assertEqual(res_dentro["estado"], "rojo")
            self.assertEqual(res_dentro["valor"], 4)
            self.assertEqual(res_dentro["sombra"], {
                "desde": "2026-09-01",
                "porque": "deuda acotada",
                "cota": 4,
                "perdona": True,
            })

            # Fuera de la cota: valor 5 > 4 -> perdona False
            res_fuera = mcp.evaluar_para_mcp(
                proy,
                {
                    "medida": {"id": "demo.sombra_cota"},
                    "evidencia": {"item": [{"id": i} for i in range(5)]},
                },
            )
            self.assertEqual(res_fuera["estado"], "rojo")
            self.assertEqual(res_fuera["valor"], 5)
            self.assertEqual(res_fuera["sombra"], {
                "desde": "2026-09-01",
                "porque": "deuda acotada",
                "cota": 4,
                "perdona": False,
            })


class JuzgarMcpTests(unittest.TestCase):
    """Pruebas para oracle_juzgar (esquema oracle.mcp/juzgar/v1)."""

    def test_juzgar_sin_ids_evalua_todas_las_aplicables_y_reporta_no_aplicadas(self) -> None:
        m_item = _medida("demo.item", limite=0, requiere=("item",))
        m_otra = _medida("demo.otra", limite=0, relacion="otra_relacion")
        sombra = {
            "demo.item": {
                "desde": "2026-09-01",
                "porque": "deuda",
                "cota": 2,
            }
        }
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto_con_sombras(Path(td), [m_item, m_otra], sombra_dict=sombra)
            proy = mcp.Proyecto(raiz)
            evidencia = {"item": [{"id": 1}]}

            res = mcp.juzgar_para_mcp(proy, {"evidencia": evidencia})

            self.assertEqual(res["esquema"], "oracle.mcp/juzgar/v1")
            self.assertEqual(res["oracle_version"], VERSION_DISTRIBUCION)
            self.assertTrue(res["ok"])  # 1 item está dentro de cota 2
            self.assertEqual(len(res["medidas"]), 1)
            med = res["medidas"][0]
            self.assertEqual(med["id"], "demo.item")
            self.assertEqual(med["estado"], "rojo")
            self.assertEqual(med["sombra"]["perdona"], True)
            self.assertEqual(med["sombra"]["cota"], 2)

            # m_otra debe figurar en no_aplicadas
            self.assertEqual(len(res["no_aplicadas"]), 1)
            self.assertEqual(res["no_aplicadas"][0]["id"], "demo.otra")
            self.assertEqual(res["no_aplicadas"][0]["faltan"], ["otra_relacion"])

    def test_juzgar_con_ids_evalua_solo_las_solicitadas(self) -> None:
        m1 = _medida("demo.uno", limite=0)
        m2 = _medida("demo.dos", limite=0)
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto_con_sombras(Path(td), [m1, m2])
            proy = mcp.Proyecto(raiz)
            evidencia = {"item": []}

            res = mcp.juzgar_para_mcp(proy, {"evidencia": evidencia, "ids": ["demo.uno"]})
            self.assertEqual(len(res["medidas"]), 1)
            self.assertEqual(res["medidas"][0]["id"], "demo.uno")
            self.assertEqual(res["no_aplicadas"], [])
            self.assertTrue(res["ok"])

    def test_juzgar_con_id_inexistente_falla_con_medida_desconocida(self) -> None:
        m1 = _medida("demo.uno", limite=0)
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto_con_sombras(Path(td), [m1])
            proy = mcp.Proyecto(raiz)

            with self.assertRaises(mcp.ErrorHerramienta) as ctx:
                mcp.juzgar_para_mcp(proy, {"evidencia": {"item": []}, "ids": ["demo.inexistente"]})
            self.assertEqual(ctx.exception.codigo, "MEDIDA_DESCONOCIDA")

    def test_juzgar_con_id_no_aplicable_falla_con_medida_no_aplicable(self) -> None:
        m_item = _medida("demo.item", limite=0, requiere=("item",))
        m_otra = _medida("demo.otra", limite=0, relacion="otra_relacion")
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto_con_sombras(Path(td), [m_item, m_otra])
            proy = mcp.Proyecto(raiz)

            with self.assertRaises(mcp.ErrorHerramienta) as ctx:
                mcp.juzgar_para_mcp(
                    proy,
                    {"evidencia": {"item": []}, "ids": ["demo.otra"]},
                )
            self.assertEqual(ctx.exception.codigo, "MEDIDA_NO_APLICABLE")

    def test_juzgar_sin_medidas_aplicables_devuelve_ok_false_y_advertencia(self) -> None:
        m_otra = _medida("demo.otra", limite=0, relacion="otra_relacion")
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto_con_sombras(Path(td), [m_otra])
            proy = mcp.Proyecto(raiz)

            res = mcp.juzgar_para_mcp(proy, {"evidencia": {"desconocida": []}})
            self.assertFalse(res["ok"])
            self.assertEqual(res["medidas"], [])
            self.assertTrue(any("ninguna medida" in adv for adv in res["advertencias"]))

    def test_juzgar_mediante_servidor_jsonrpc(self) -> None:
        m = _medida("demo.uno", limite=0)
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto_con_sombras(Path(td), [m])
            proy = mcp.Proyecto(raiz)
            salida = io.BytesIO()
            servidor = mcp.Servidor(proy, salida)
            servidor.estado = "inicializado"

            servidor.manejar({
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {
                    "name": "oracle_juzgar",
                    "arguments": {"evidencia": {"item": []}},
                },
            })

            salida.seek(0)
            linea = salida.readline().decode("utf-8")
            respuesta = json.loads(linea)
            self.assertEqual(respuesta["id"], 10)
            self.assertFalse(respuesta["result"]["isError"])
            resultado = respuesta["result"]["structuredContent"]
            self.assertEqual(resultado["esquema"], "oracle.mcp/juzgar/v1")
            self.assertTrue(resultado["ok"])


class TareasMcpTests(unittest.TestCase):
    """Pruebas para oracle_tareas (esquema oracle.mcp/tareas/v1)."""

    def test_tracker_ausente_falla_con_error_herramienta(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy = mcp.Proyecto(Path(td))
            with self.assertRaises(mcp.ErrorHerramienta) as ctx:
                mcp.tareas_para_mcp(proy, {"accion": "listar"})
            self.assertEqual(ctx.exception.codigo, "TRACKER_AUSENTE")

    def test_listar_tareas_por_omision_abiertas_cerradas_y_etiqueta(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = _inicializar_tracker(Path(td))
            proy = mcp.Proyecto(raiz)

            # Por omisión: abiertas (t1 y t3)
            res_abiertas = mcp.tareas_para_mcp(proy, {"accion": "listar"})
            self.assertEqual(res_abiertas["esquema"], "oracle.mcp/tareas/v1")
            self.assertEqual(res_abiertas["accion"], "listar")
            ids_abiertas = [t["id"] for t in res_abiertas["resultado"]]
            self.assertIn("20260901-100000-tarea-abierta", ids_abiertas)
            self.assertIn("20260901-120000-tarea-otra", ids_abiertas)
            self.assertNotIn("20260901-110000-tarea-cerrada", ids_abiertas)

            # Cerradas
            res_cerradas = mcp.tareas_para_mcp(proy, {"accion": "listar", "estado": "CERRADA"})
            ids_cerradas = [t["id"] for t in res_cerradas["resultado"]]
            self.assertEqual(ids_cerradas, ["20260901-110000-tarea-cerrada"])

            # Por etiqueta
            res_etiqueta = mcp.tareas_para_mcp(proy, {"accion": "listar", "etiqueta": "backend"})
            ids_etiqueta = [t["id"] for t in res_etiqueta["resultado"]]
            self.assertEqual(ids_etiqueta, ["20260901-100000-tarea-abierta"])

    def test_listar_omite_solo_cuerpo_y_ver_conserva_detalle_y_notas(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = _inicializar_tracker(Path(td))
            proy = mcp.Proyecto(raiz)
            ruta = raiz / "tareas" / "20260901-100000-tarea-abierta" / "TAREA.md"
            with ruta.open("a", encoding="utf-8") as archivo:
                archivo.write("\n### Nota (2026-09-23)\n\nTestigo y alcance completos.\n")
            for filtros in ({}, {"estado": "CERRADA"}, {"etiqueta": "backend"}):
                with self.subTest(filtros=filtros):
                    listado = mcp.tareas_para_mcp(proy, {"accion": "listar", **filtros})
                    self.assertTrue(listado["resultado"])
                    for resumen in listado["resultado"]:
                        detalle = mcp.tareas_para_mcp(
                            proy, {"accion": "ver", "id": resumen["id"]})["resultado"]
                        self.assertNotIn("cuerpo", resumen)
                        self.assertEqual(resumen, {k: v for k, v in detalle.items() if k != "cuerpo"})
            detalle = mcp.tareas_para_mcp(proy, {"accion": "ver", "id": "tarea-abierta"})
            self.assertIn("Detalle de la tarea de backend", detalle["resultado"]["cuerpo"])
            self.assertIn("Testigo y alcance completos.", detalle["resultado"]["cuerpo"])
            self.assertTrue(mcp.tareas_para_mcp(
                proy, {"accion": "buscar", "texto": "Testigo y alcance completos."}
            )["resultado"]["coincidencias"])

    def test_ver_tarea_existente_inexistente_y_ambigua(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = _inicializar_tracker(Path(td))
            proy = mcp.Proyecto(raiz)

            # Existente por id completo
            res = mcp.tareas_para_mcp(proy, {"accion": "ver", "id": "20260901-100000-tarea-abierta"})
            self.assertEqual(res["resultado"]["id"], "20260901-100000-tarea-abierta")
            self.assertEqual(res["resultado"]["estado"], "ABIERTA")
            self.assertEqual(res["resultado"]["prioridad"], 70)

            # Existente por prefijo inequívoco
            res_pref = mcp.tareas_para_mcp(proy, {"accion": "ver", "id": "20260901-100000"})
            self.assertEqual(res_pref["resultado"]["id"], "20260901-100000-tarea-abierta")

            # Inexistente
            with self.assertRaises(mcp.ErrorHerramienta) as ctx:
                mcp.tareas_para_mcp(proy, {"accion": "ver", "id": "no-existe"})
            self.assertEqual(ctx.exception.codigo, "TAREA_NO_ENCONTRADA")

            # Ambiguo
            with self.assertRaises(mcp.ErrorHerramienta) as ctx_amb:
                mcp.tareas_para_mcp(proy, {"accion": "ver", "id": "20260901"})
            self.assertEqual(ctx_amb.exception.codigo, "ID_AMBIGUO")

    def test_buscar_en_tracker(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = _inicializar_tracker(Path(td))
            proy = mcp.Proyecto(raiz)

            # Búsqueda válida
            res = mcp.tareas_para_mcp(proy, {"accion": "buscar", "texto": "backend"})
            coincidencias = res["resultado"]["coincidencias"]
            self.assertTrue(len(coincidencias) > 0)
            self.assertTrue(any("20260901-100000" in c["ruta"] for c in coincidencias))

            # Búsqueda con texto vacío falla
            with self.assertRaises(mcp.ErrorHerramienta) as ctx:
                mcp.tareas_para_mcp(proy, {"accion": "buscar", "texto": ""})
            self.assertEqual(ctx.exception.codigo, "ARGUMENTOS_INVALIDOS")

    def test_hechos_en_tracker(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = _inicializar_tracker(Path(td))
            proy = mcp.Proyecto(raiz)

            res = mcp.tareas_para_mcp(proy, {"accion": "hechos", "git": False})
            self.assertEqual(res["esquema"], "oracle.mcp/tareas/v1")
            self.assertEqual(res["accion"], "hechos")
            self.assertIsInstance(res["resultado"], dict)
            self.assertIn("tarea_seguimiento", res["resultado"])
            self.assertEqual(len(res["resultado"]["tarea_seguimiento"]), 3)

    def test_tareas_mediante_servidor_rpc(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = _inicializar_tracker(Path(td))
            proy = mcp.Proyecto(raiz)
            salida = io.BytesIO()
            servidor = mcp.Servidor(proy, salida)
            servidor.estado = "inicializado"

            servidor.manejar({
                "jsonrpc": "2.0",
                "id": 20,
                "method": "tools/call",
                "params": {
                    "name": "oracle_tareas",
                    "arguments": {"accion": "listar"},
                },
            })

            salida.seek(0)
            linea = salida.readline().decode("utf-8")
            respuesta = json.loads(linea)
            self.assertEqual(respuesta["id"], 20)
            self.assertFalse(respuesta["result"]["isError"])
            resultado = respuesta["result"]["structuredContent"]
            self.assertEqual(resultado["esquema"], "oracle.mcp/tareas/v1")
            self.assertEqual(resultado["accion"], "listar")


if __name__ == "__main__":
    unittest.main()
