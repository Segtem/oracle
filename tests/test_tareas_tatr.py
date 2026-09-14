"""Tests exhaustivos del tramo 0.17.0: lo que faltaba de tatr.

Cubre especificación de alineación dinámica en listar, catálogo tareas/etiquetas,
etiquetar, desetiquetar, grafo de referencias y ayuda e integración CLI.
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools import cli, tareas, tareas_contexto, tareas_grafo


ID_A = "20260914-110000-a"
ID_B = "20260914-110001-investigar-un-defecto-complejo-del-sensor-de-procesos"
ID_SENSOR = "20260914-110002-sensor"
ID_SENSOR_2 = "20260914-110003-sensor-2"


class BaseTatrTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory(prefix="oracle-tatr-agy-")
        self.addCleanup(self.td.cleanup)
        self.raiz = Path(self.td.name).resolve()
        self.raiz_tareas = self.raiz / "tareas"
        self.raiz_tareas.mkdir(parents=True)
        # Git boundary para resolución ascendente confinada
        (self.raiz / ".git").mkdir()

    def crear_tarea(
        self,
        ident: str,
        titulo: str,
        *,
        estado: str = "ABIERTA",
        prioridad: int = 50,
        etiquetas: str | list[str] | None = "",
        extra: str = "",
        cuerpo: str = "",
        fin_linea: str = "\n",
    ) -> Path:
        carpeta = self.raiz_tareas / ident
        carpeta.mkdir(parents=True, exist_ok=True)
        lineas = [
            f"# {titulo}",
            "",
            f"- ESTADO: {estado}",
            f"- PRIORIDAD: {prioridad}",
        ]
        if etiquetas is not None:
            if isinstance(etiquetas, list):
                etiq_str = ", ".join(etiquetas)
            else:
                etiq_str = etiquetas
            lineas.append(f"- ETIQUETAS: {etiq_str}")
        if extra:
            lineas.append(extra)
        lineas.append("")
        if cuerpo:
            lineas.append(cuerpo)
            lineas.append("")
        contenido = fin_linea.join(lineas)
        ruta = carpeta / "TAREA.md"
        ruta.write_bytes(contenido.encode("utf-8"))
        return ruta

    def ejecutar_cli(self, *args: str) -> tuple[int, str, str]:
        """Ejecuta cli.main capturando stdout, stderr y SystemExit."""
        out = io.StringIO()
        err = io.StringIO()
        cmd = ["--proyecto", str(self.raiz), "tarea", *args]
        with redirect_stdout(out), redirect_stderr(err):
            try:
                rc = cli.main(cmd)
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else (1 if e.code else 0)
        return rc, out.getvalue(), err.getvalue()

    def instantanea_archivos(self) -> dict[str, bytes | None]:
        """Captura estado y contenido de todos los archivos bajo la raíz."""
        res: dict[str, bytes | None] = {}
        for p in sorted(self.raiz.rglob("*")):
            if p.is_file():
                try:
                    res[str(p.relative_to(self.raiz))] = p.read_bytes()
                except OSError:
                    res[str(p.relative_to(self.raiz))] = None
            else:
                res[str(p.relative_to(self.raiz))] = None
        return res


class TestAlineacionDinamicaListar(BaseTatrTestCase):
    """Pruebas de la alineación dinámica de columnas en `oracle tarea listar`."""

    def test_alineacion_dinamica_con_ids_largos_cortos_y_sin_trailing_whitespace(self) -> None:
        self.crear_tarea(ID_A, "Tarea Corta", prioridad=90, etiquetas="alfa")
        self.crear_tarea(
            ID_B,
            "Tarea Larga con Titulo Extenso",
            prioridad=50,
            etiquetas="bug, hardware, urgente, sensor",
        )
        rc, out, err = self.ejecutar_cli("listar")
        self.assertEqual(rc, 0, err)
        filas = [linea for linea in out.splitlines() if linea.strip()]
        # Al menos cabecera y 2 filas
        self.assertGreaterEqual(len(filas), 2)

        # Ninguna fila debe contener espacios al final
        for fila in filas:
            self.assertEqual(fila, fila.rstrip(), f"Fila contiene espacios finales: {fila!r}")

        # Las columnas ESTADO y PRIO deben alinearse en la misma posición horizontal
        idx_estado_corta = next(f.index("ABIERTA") for f in filas if ID_A in f)
        idx_estado_larga = next(f.index("ABIERTA") for f in filas if ID_B in f)
        self.assertEqual(idx_estado_corta, idx_estado_larga, "Columna ESTADO desalineada")

        idx_titulo_corta = next(f.index("Tarea Corta") for f in filas if ID_A in f)
        idx_titulo_larga = next(f.index("Tarea Larga") for f in filas if ID_B in f)
        self.assertEqual(idx_titulo_corta, idx_titulo_larga, "Columna TÍTULO desalineada")

    def test_alineacion_con_tareas_sin_etiquetas(self) -> None:
        self.crear_tarea(ID_A, "Con Etiquetas", etiquetas="tag1, tag2")
        self.crear_tarea(ID_B, "Sin Etiquetas", etiquetas="")
        rc, out, err = self.ejecutar_cli("listar")
        self.assertEqual(rc, 0, err)
        filas = [linea for linea in out.splitlines() if linea.strip()]
        for fila in filas:
            self.assertEqual(fila, fila.rstrip(), "Espacio redundante al final")


class TestCatalogoEtiquetas(BaseTatrTestCase):
    """Pruebas del archivo auxiliar `tareas/etiquetas`."""

    def test_formato_valido_comas_espacios_y_descripcion_vacia(self) -> None:
        (self.raiz_tareas / "etiquetas").write_text(
            "bug Defectos y anomalías en arnés\n"
            "sensor,   Telemetría y reloj monotónico\n"
            "vacia\n"
            "\n"
            "gui, , Interfaz de usuario\n",
            encoding="utf-8",
        )
        self.crear_tarea(ID_A, "Tarea sensor", etiquetas="sensor, bug")
        self.crear_tarea(ID_B, "Tarea vacia", etiquetas="vacia")

        # revisar acepta el archivo como auxiliar y valida ok
        rc_rev, out_rev, err_rev = self.ejecutar_cli("revisar")
        self.assertEqual(rc_rev, 0, out_rev + err_rev)

        # resumen muestra las descripciones
        rc_res, out_res, err_res = self.ejecutar_cli("resumen")
        self.assertEqual(rc_res, 0, err_res)
        self.assertIn("Telemetría y reloj monotónico", out_res)
        self.assertIn("Defectos y anomalías en arnés", out_res)

        # resumen --json incluye mapa de descripciones
        rc_json, out_json, _ = self.ejecutar_cli("resumen", "--json")
        self.assertEqual(rc_json, 0)
        datos = json.loads(out_json)
        self.assertIn("descripciones", datos)
        self.assertEqual(datos["descripciones"]["sensor"], "Telemetría y reloj monotónico")
        self.assertEqual(datos["descripciones"]["bug"], "Defectos y anomalías en arnés")
        self.assertEqual(datos["descripciones"]["vacia"], "")

    def test_etiqueta_con_numeral_no_es_comentario(self) -> None:
        (self.raiz_tareas / "etiquetas").write_text(
            "#algo Etiqueta que comienza con numeral\n",
            encoding="utf-8",
        )
        self.crear_tarea(ID_A, "Tarea con numeral", etiquetas="#algo")
        rc_rev, out_rev, err_rev = self.ejecutar_cli("revisar")
        self.assertEqual(rc_rev, 0, out_rev + err_rev)

        rc_res, out_res, err_res = self.ejecutar_cli("resumen")
        self.assertEqual(rc_res, 0, err_res)
        self.assertIn("Etiqueta que comienza con numeral", out_res)

        rc_json, out_json, _ = self.ejecutar_cli("resumen", "--json")
        self.assertEqual(rc_json, 0)
        datos = json.loads(out_json)
        self.assertEqual(datos["descripciones"]["#algo"], "Etiqueta que comienza con numeral")

    def test_redefinicion_falla_revisar_con_linea_y_avisa_en_resumen(self) -> None:
        (self.raiz_tareas / "etiquetas").write_text(
            "bug Primera definicion\n"
            "docs Documentacion\n"
            "bug Segunda definicion que prevalece\n",
            encoding="utf-8",
        )
        self.crear_tarea(ID_A, "Tarea bug", etiquetas="bug")

        # revisar debe fallar con código 1 e indicar línea y etiqueta
        rc_rev, out_rev, err_rev = self.ejecutar_cli("revisar")
        self.assertEqual(rc_rev, 1)
        self.assertRegex(out_rev + err_rev, r"etiquetas:3")
        self.assertIn("redefinida", out_rev + err_rev)

        # resumen debe devolver 0, advertir en stderr y usar la última definición
        rc_res, out_res, err_res = self.ejecutar_cli("resumen")
        self.assertEqual(rc_res, 0, err_res)
        self.assertTrue(err_res.strip(), "Debe advertir redefinición en stderr")
        self.assertIn("Segunda definicion que prevalece", out_res)
        self.assertNotIn("Primera definicion", out_res)

    def test_redefinicion_en_etiquetas_no_rompe_otras_operaciones(self) -> None:
        (self.raiz_tareas / "etiquetas").write_text(
            "bug Primera definicion\n"
            "bug Segunda definicion\n",
            encoding="utf-8",
        )
        self.crear_tarea(ID_A, "Tarea A", etiquetas="bug", cuerpo=f"Menciona a {ID_B}")
        self.crear_tarea(ID_B, "Tarea B", etiquetas="")

        # Las operaciones de lectura y mutación no deben fallar por la redefinición en etiquetas
        rc_ls, _, _ = self.ejecutar_cli("listar")
        self.assertEqual(rc_ls, 0)

        rc_gr, _, _ = self.ejecutar_cli("grafo")
        self.assertEqual(rc_gr, 0)

        rc_hech, _, _ = self.ejecutar_cli("hechos")
        self.assertEqual(rc_hech, 0)

        rc_busc, _, _ = self.ejecutar_cli("buscar", "Menciona")
        self.assertEqual(rc_busc, 0)

        rc_ref, _, _ = self.ejecutar_cli("referencias", ID_B)
        self.assertEqual(rc_ref, 0)

        rc_etiq, _, _ = self.ejecutar_cli("etiquetar", ID_B, "--etiqueta", "nueva")
        self.assertEqual(rc_etiq, 0)

        rc_deset, _, _ = self.ejecutar_cli("desetiquetar", ID_B, "--etiqueta", "nueva")
        self.assertEqual(rc_deset, 0)

        # Solo revisar debe fallar con código 1
        rc_rev, _, _ = self.ejecutar_cli("revisar")
        self.assertEqual(rc_rev, 1)

    def test_utf8_invalido_falla_revisar_y_resumen_sin_traceback(self) -> None:
        (self.raiz_tareas / "etiquetas").write_bytes(b"bug \xff\xfe bytes no utf8\n")
        self.crear_tarea(ID_A, "Tarea simple")

        rc_rev, out_rev, err_rev = self.ejecutar_cli("revisar")
        self.assertEqual(rc_rev, 1)
        self.assertNotIn("Traceback", err_rev)
        self.assertIn("etiquetas", out_rev + err_rev)

        rc_res, out_res, err_res = self.ejecutar_cli("resumen")
        self.assertEqual(rc_res, 1)
        self.assertNotIn("Traceback", err_res)
        self.assertIn("etiquetas", out_res + err_res)

        # listar y grafo no deben fallar por el archivo etiquetas corrupto
        rc_ls, _, _ = self.ejecutar_cli("listar")
        self.assertEqual(rc_ls, 0)

        rc_gr, _, _ = self.ejecutar_cli("grafo")
        self.assertEqual(rc_gr, 0)

    @unittest.skipUnless(hasattr(os, "symlink"), "Requiere soporte de enlaces simbólicos")
    def test_symlink_falla_revisar_y_es_ignorado_en_resumen(self) -> None:
        archivo_afuera = self.raiz.parent / "etiquetas-externas.txt"
        archivo_afuera.write_text("bug CLAVE_SECRETA_EXTERNA\n", encoding="utf-8")
        (self.raiz_tareas / "etiquetas").symlink_to(archivo_afuera)
        self.crear_tarea(ID_A, "Tarea con bug", etiquetas="bug")

        # revisar falla con código 1
        rc_rev, _, _ = self.ejecutar_cli("revisar")
        self.assertEqual(rc_rev, 1)

        # resumen no sigue el symlink, emite aviso por stderr y sale 0
        rc_res, out_res, err_res = self.ejecutar_cli("resumen")
        self.assertEqual(rc_res, 0)
        self.assertIn("enlace simbólico", err_res)
        self.assertNotIn("CLAVE_SECRETA_EXTERNA", out_res)

        # listar y grafo no fallan por el symlink
        rc_ls, _, _ = self.ejecutar_cli("listar")
        self.assertEqual(rc_ls, 0)

        rc_gr, _, _ = self.ejecutar_cli("grafo")
        self.assertEqual(rc_gr, 0)

    def test_clasificacion_como_auxiliar_en_hechos(self) -> None:
        (self.raiz_tareas / "etiquetas").write_text("bug defecto\n", encoding="utf-8")
        self.crear_tarea(ID_A, "Tarea inicial")
        rc, out, err = self.ejecutar_cli("hechos")
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        items = [f for f in datos["archivo_seguimiento"] if f["ruta"] == "tareas/etiquetas"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["clase"], "auxiliar")
        self.assertEqual(items[0]["tarea_id"], "")


class TestResumenMetricas(BaseTatrTestCase):
    """Pruebas del reporte de resumen con catálogo de etiquetas y conteo sin_etiquetas."""

    def test_resumen_sin_etiquetas_y_descripciones(self) -> None:
        (self.raiz_tareas / "etiquetas").write_text(
            "alfa Primera letra\nbeta Segunda letra\n", encoding="utf-8"
        )
        self.crear_tarea(ID_A, "Con alfa y beta", etiquetas="alfa, beta")
        self.crear_tarea(ID_B, "Sin etiquetas", etiquetas="")
        self.crear_tarea(ID_SENSOR, "Solo alfa", etiquetas="alfa")

        rc, out, err = self.ejecutar_cli("resumen")
        self.assertEqual(rc, 0, err)
        self.assertIn("Sin etiquetas: 1", out)
        self.assertIn("alfa: 2 — Primera letra", out)
        self.assertIn("beta: 1 — Segunda letra", out)

        rc_json, out_json, _ = self.ejecutar_cli("resumen", "--json")
        self.assertEqual(rc_json, 0)
        datos = json.loads(out_json)
        self.assertEqual(datos["sin_etiquetas"], 1)
        self.assertEqual(datos["total"], 3)
        self.assertEqual(datos["etiquetas"]["alfa"], 2)
        self.assertEqual(datos["etiquetas"]["beta"], 1)
        self.assertEqual(datos["descripciones"]["alfa"], "Primera letra")
        self.assertEqual(datos["descripciones"]["beta"], "Segunda letra")


class TestEtiquetarYDesetiquetar(BaseTatrTestCase):
    """Pruebas de los comandos `etiquetar` y `desetiquetar`."""

    def test_etiquetar_por_id_y_prefijo(self) -> None:
        ruta_a = self.crear_tarea(ID_A, "Tarea A", etiquetas="")
        ruta_b = self.crear_tarea(ID_B, "Tarea B", etiquetas="existente")

        # Etiquetar A por ID canónico
        rc1, out1, err1 = self.ejecutar_cli("etiquetar", ID_A, "--etiqueta", "nueva")
        self.assertEqual(rc1, 0, out1 + err1)
        self.assertIn("- ETIQUETAS: nueva", ruta_a.read_text(encoding="utf-8"))

        # Etiquetar B por prefijo inequívoco
        prefijo_b = "20260914-110001-investigar"
        rc2, out2, err2 = self.ejecutar_cli("etiquetar", prefijo_b, "--etiqueta", "urgente")
        self.assertEqual(rc2, 0, out2 + err2)
        self.assertIn("- ETIQUETAS: existente, urgente", ruta_b.read_text(encoding="utf-8"))

    def test_etiquetar_multiples_etiquetas_en_una_invocacion(self) -> None:
        ruta = self.crear_tarea(ID_A, "Tarea Multiple", etiquetas="base")
        rc, out, err = self.ejecutar_cli(
            "etiquetar", ID_A, "--etiqueta", "uno, dos", "--etiqueta", "tres"
        )
        self.assertEqual(rc, 0, out + err)
        contenido = ruta.read_text(encoding="utf-8")
        self.assertIn("- ETIQUETAS: base, uno, dos, tres", contenido)

    def test_etiquetar_preserva_crlf_campos_desconocidos_y_cuerpo(self) -> None:
        ruta = self.crear_tarea(
            ID_A,
            "CRLF Preservado",
            etiquetas="inicial",
            extra="- DUENO: brian\r\n- IMPACTO: alto",
            cuerpo="Cuerpo con bloque:\r\n```\r\n- ETIQUETAS: no-es-meta\r\n```",
            fin_linea="\r\n",
        )
        antes = ruta.read_bytes()
        self.assertIn(b"\r\n", antes)

        rc, out, err = self.ejecutar_cli("etiquetar", ID_A, "--etiqueta", "extra")
        self.assertEqual(rc, 0, out + err)
        despues = ruta.read_bytes()

        self.assertEqual(
            despues,
            antes.replace(b"- ETIQUETAS: inicial\r\n", b"- ETIQUETAS: inicial, extra\r\n"),
        )
        self.assertRegex(out, rf"tareas/{ID_A}/TAREA\.md:5:")

    def test_etiquetar_inserta_linea_si_no_existia(self) -> None:
        ruta = self.crear_tarea(ID_A, "Sin etiquetas", etiquetas=None, extra="- ORIGEN: manual")
        rc, out, err = self.ejecutar_cli("etiquetar", ID_A, "--etiqueta", "creada")
        self.assertEqual(rc, 0, out + err)
        lineas = ruta.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lineas[2:6],
            ["- ESTADO: ABIERTA", "- PRIORIDAD: 50", "- ORIGEN: manual", "- ETIQUETAS: creada"],
        )

    def test_etiquetar_tarea_sin_salto_de_linea_final_no_corrompe(self) -> None:
        carpeta = self.raiz_tareas / ID_A
        carpeta.mkdir()
        ruta = carpeta / "TAREA.md"
        ruta.write_bytes(b"# Sin EOL\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50")

        rc, out, err = self.ejecutar_cli("etiquetar", ID_A, "--etiqueta", "bug")
        self.assertEqual(rc, 0, out + err)
        contenido = ruta.read_text(encoding="utf-8")
        self.assertNotIn("- PRIORIDAD: 50- ETIQUETAS:", contenido)
        self.assertIn("- PRIORIDAD: 50\n- ETIQUETAS: bug", contenido)

        # La tarea modificada debe pasar la auditoría sin errores de metadatos
        rc_rev, out_rev, err_rev = self.ejecutar_cli("revisar")
        self.assertEqual(rc_rev, 0, out_rev + err_rev)

    def test_modificar_etiquetas_sin_eol_final_no_agrega_eol(self) -> None:
        carpeta = self.raiz_tareas / ID_A
        carpeta.mkdir()
        ruta = carpeta / "TAREA.md"
        original = b"# Sin EOL\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n- ETIQUETAS: bug"
        ruta.write_bytes(original)

        # Modificar agregando una etiqueta no debe agregar salto de línea final
        rc1, out1, err1 = self.ejecutar_cli("etiquetar", ID_A, "--etiqueta", "extra")
        self.assertEqual(rc1, 0, out1 + err1)
        modificado = ruta.read_bytes()
        self.assertFalse(modificado.endswith(b"\n"))
        self.assertEqual(
            modificado,
            b"# Sin EOL\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n- ETIQUETAS: bug, extra",
        )

        # Desetiquetar quitando la etiqueta extra debe retornar exactamente al original byte a byte
        rc2, out2, err2 = self.ejecutar_cli("desetiquetar", ID_A, "--etiqueta", "extra")
        self.assertEqual(rc2, 0, out2 + err2)
        self.assertEqual(ruta.read_bytes(), original)

    def test_etiquetar_idempotencia_no_reescribe_disco(self) -> None:
        ruta = self.crear_tarea(ID_A, "Ya tiene etiqueta", etiquetas="Bug")
        os.utime(ruta, (1_100_000_000, 1_100_000_000))
        antes = ruta.read_bytes()

        rc, out, err = self.ejecutar_cli("etiquetar", ID_A, "--etiqueta", "bug")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(ruta.read_bytes(), antes)
        self.assertEqual(ruta.stat().st_mtime, 1_100_000_000)
        self.assertIn("0 tarea(s) modificada(s)", out)

    def test_etiquetar_con_registro_roto_aborta_sin_tocar_ninguna(self) -> None:
        ruta_sana = self.crear_tarea(ID_A, "Sana", etiquetas="ok")
        # Crear carpeta con tarea rota
        carpeta_rota = self.raiz_tareas / "20260914-110099-rota"
        carpeta_rota.mkdir()
        (carpeta_rota / "TAREA.md").write_text("# Rota\n- ESTADO: INVENTADO\n", encoding="utf-8")

        antes = self.instantanea_archivos()
        rc, out, err = self.ejecutar_cli("etiquetar", ID_A, "--etiqueta", "nueva")
        self.assertEqual(rc, 1)
        self.assertEqual(self.instantanea_archivos(), antes)

    def test_desetiquetar_por_id_y_prefijo(self) -> None:
        ruta_a = self.crear_tarea(ID_A, "Tarea A", etiquetas="vieja, mantener")
        ruta_b = self.crear_tarea(ID_B, "Tarea B", etiquetas="vieja, otra")

        rc1, _, _ = self.ejecutar_cli("desetiquetar", ID_A, "--etiqueta", "vieja")
        self.assertEqual(rc1, 0)
        lineas_a = ruta_a.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            next(l for l in lineas_a if l.startswith("- ETIQUETAS:")),
            "- ETIQUETAS: mantener",
        )

        prefijo_b = "20260914-110001-investigar"
        rc2, _, _ = self.ejecutar_cli("desetiquetar", prefijo_b, "--etiqueta", "vieja")
        self.assertEqual(rc2, 0)
        lineas_b = ruta_b.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            next(l for l in lineas_b if l.startswith("- ETIQUETAS:")),
            "- ETIQUETAS: otra",
        )

    def test_desetiquetar_masivo_afecta_solo_abiertas_por_defecto(self) -> None:
        ruta_abierta = self.crear_tarea(ID_A, "Abierta", estado="ABIERTA", etiquetas="vieja, test")
        ruta_cerrada = self.crear_tarea(ID_B, "Cerrada", estado="CERRADA", etiquetas="vieja, prod")

        rc, out, err = self.ejecutar_cli("desetiquetar", "--etiqueta", "vieja")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("- ETIQUETAS: test", ruta_abierta.read_text(encoding="utf-8"))
        self.assertIn("- ETIQUETAS: vieja, prod", ruta_cerrada.read_text(encoding="utf-8"))

    def test_desetiquetar_masivo_con_todas_y_ultima_etiqueta_queda_como_nueva(self) -> None:
        ruta_abierta = self.crear_tarea(ID_A, "Abierta", estado="ABIERTA", etiquetas="vieja")
        ruta_cerrada = self.crear_tarea(ID_B, "Cerrada", estado="CERRADA", etiquetas="vieja")

        rc, out, err = self.ejecutar_cli("desetiquetar", "--etiqueta", "vieja", "--todas")
        self.assertEqual(rc, 0, out + err)

        # Ambas tareas se quedan sin etiquetas; el campo debe conservarse como "- ETIQUETAS: "
        for ruta in (ruta_abierta, ruta_cerrada):
            lineas = ruta.read_text(encoding="utf-8").splitlines()
            linea_etiq = [l for l in lineas if "ETIQUETAS" in l]
            self.assertEqual(linea_etiq, ["- ETIQUETAS: "])

    def test_desetiquetar_ids_con_banderas_de_estado_da_error_2(self) -> None:
        self.crear_tarea(ID_A, "Tarea A", etiquetas="vieja")
        antes = self.instantanea_archivos()

        rc, out, err = self.ejecutar_cli("desetiquetar", ID_A, "--etiqueta", "vieja", "--cerradas")
        self.assertEqual(rc, 2)
        self.assertNotIn("Traceback", err)
        self.assertEqual(self.instantanea_archivos(), antes)

        rc2, _, _ = self.ejecutar_cli("desetiquetar", ID_A, "--etiqueta", "vieja", "--todas")
        self.assertEqual(rc2, 2)

    def test_desetiquetar_id_explicito_admite_tarea_cerrada(self) -> None:
        ruta_cerrada = self.crear_tarea(ID_B, "Cerrada", estado="CERRADA", etiquetas="revisar")
        rc, out, err = self.ejecutar_cli("desetiquetar", ID_B, "--etiqueta", "revisar")
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("revisar", ruta_cerrada.read_text(encoding="utf-8"))


class TestGrafo(BaseTatrTestCase):
    """Pruebas del comando `oracle tarea grafo`."""

    def test_grafo_referencias_validas_y_frontera_de_tokens(self) -> None:
        self.crear_tarea(
            ID_SENSOR,
            'Sensor con "comillas" y \\barra',
            cuerpo=(
                f"Referencia propia {ID_SENSOR} no es arista. "
                f"Referencia a {ID_SENSOR_2} y otra vez {ID_SENSOR_2} se deduplica. "
                f"Prefijo {ID_SENSOR_2}-sufijo no cuenta como {ID_SENSOR_2}."
            ),
        )
        self.crear_tarea(
            ID_SENSOR_2,
            "Sensor dos",
            estado="CERRADA",
            cuerpo=f"Dependencia cerrada hacia {ID_A}.",
        )
        self.crear_tarea(ID_A, "Tarea A", cuerpo="Sin referencias salientes.")
        self.crear_tarea(ID_B, "Tarea aislada", cuerpo="No menciona nada ni la mencionan.")

        rc, out, err = self.ejecutar_cli("grafo", "--json")
        self.assertEqual(rc, 0, out + err)
        datos = json.loads(out)

        aristas = [(a["origen"], a["destino"]) for a in datos["aristas"]]
        self.assertEqual(
            aristas,
            sorted([(ID_SENSOR, ID_SENSOR_2), (ID_SENSOR_2, ID_A)]),
        )

        nodos_ids = [n["id"] for n in datos["nodos"]]
        self.assertEqual(nodos_ids, sorted(nodos_ids))
        # Nodos participantes no incluyen a ID_B porque está aislada
        self.assertEqual(set(nodos_ids), {ID_SENSOR, ID_SENSOR_2, ID_A})
        self.assertNotIn(ID_B, nodos_ids)

        estados = {n["id"]: n["estado"] for n in datos["nodos"]}
        self.assertEqual(estados[ID_SENSOR_2], "CERRADA")

    def test_grafo_dot_escapado_y_determinismo(self) -> None:
        self.crear_tarea(
            ID_SENSOR,
            'Tarea "comillas" y \\barra',
            cuerpo=f"Ver {ID_A}",
        )
        self.crear_tarea(ID_A, "Destino")

        rc1, out1, _ = self.ejecutar_cli("grafo")
        rc2, out2, _ = self.ejecutar_cli("grafo")
        self.assertEqual(rc1, 0)
        self.assertEqual(out1, out2, "La salida DOT debe ser determinista")
        self.assertTrue(out1.strip().startswith("digraph tareas {"))
        self.assertIn(f'"{ID_SENSOR}" -> "{ID_A}";', out1)
        self.assertIn('\\"comillas\\"', out1)
        self.assertIn("\\\\barra", out1)

    def test_grafo_vacio_cuando_no_hay_aristas(self) -> None:
        self.crear_tarea(ID_A, "Tarea sin enlaces")
        self.crear_tarea(ID_B, "Otra tarea sin enlaces")

        rc_dot, out_dot, _ = self.ejecutar_cli("grafo")
        self.assertEqual(rc_dot, 0)
        self.assertRegex(out_dot.strip(), r"^digraph[^{]*\{\s*\}$")

        rc_json, out_json, _ = self.ejecutar_cli("grafo", "--json")
        self.assertEqual(rc_json, 0)
        self.assertEqual(json.loads(out_json), {"nodos": [], "aristas": []})

    def test_grafo_falla_con_codigo_1_ante_tarea_rota(self) -> None:
        self.crear_tarea(ID_A, "Tarea Sana")
        carpeta_rota = self.raiz_tareas / "20260914-110099-rota"
        carpeta_rota.mkdir()
        (carpeta_rota / "TAREA.md").write_text("# Rota\n- ESTADO: DESCONOCIDO\n", encoding="utf-8")

        rc, out, err = self.ejecutar_cli("grafo")
        self.assertEqual(rc, 1)
        self.assertNotIn("Traceback", err)


class TestCliIntegracionYAyudas(BaseTatrTestCase):
    """Pruebas de invocación general y de ayuda de los nuevos comandos."""

    def test_ayudas_de_verbos_nuevos_sin_tocar_disco(self) -> None:
        antes = self.instantanea_archivos()
        for verbo in ("etiquetar", "desetiquetar", "grafo"):
            rc, out, err = self.ejecutar_cli(verbo, "--help")
            self.assertEqual(rc, 0, f"Error en ayuda de {verbo}: {err}")
            self.assertIn(f"oracle tarea {verbo}", out)

        # Ayuda general de tarea menciona los tres nuevos verbos
        rc_gen, out_gen, _ = self.ejecutar_cli("--help")
        self.assertEqual(rc_gen, 0)
        for verbo in ("etiquetar", "desetiquetar", "grafo"):
            self.assertIn(verbo, out_gen)

        self.assertEqual(self.instantanea_archivos(), antes)


if __name__ == "__main__":
    unittest.main()
