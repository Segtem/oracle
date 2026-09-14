"""Revisión independiente del tramo 0.17.0: lo que faltaba de tatr.

Escrita por Claude contra `estudios/0.17.0-tatr/ENCARGO-AGY.md`, antes de leer la implementación.
Todo pasa por el CLI público y proyectos temporales con IDs fijos.
"""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

RAIZ = Path(__file__).resolve().parents[1]
CLI = RAIZ / "tools/cli.py"

CORTA = "20260914-100000-a"
LARGA = "20260914-100001-investigar-un-defecto-del-sensor-de-procesos"
SENSOR = "20260914-100002-sensor"
SENSOR_2 = "20260914-100003-sensor-2"


class TrackerTemporal(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(prefix="oracle-tatr-revision-")
        self.addCleanup(td.cleanup)
        self.raiz = Path(td.name) / "proyecto"
        (self.raiz / "tareas").mkdir(parents=True)
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith("GIT_") and k != "ORACLE_PROYECTO"}
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"

    def tarea(self, ident, titulo, *, estado="ABIERTA", prioridad=50, etiquetas="",
              extra="", cuerpo="", fin="\n"):
        carpeta = self.raiz / "tareas" / ident
        carpeta.mkdir()
        lineas = [f"# {titulo}", "", f"- ESTADO: {estado}", f"- PRIORIDAD: {prioridad}"]
        if etiquetas is not None:
            lineas.append(f"- ETIQUETAS: {etiquetas}")
        if extra:
            lineas.append(extra)
        lineas += ["", cuerpo] if cuerpo else [""]
        ruta = carpeta / "TAREA.md"
        ruta.write_bytes((fin.join(lineas) + fin).encode("utf-8"))
        return ruta

    def cli(self, verbo, *args):
        return subprocess.run([sys.executable, "-B", str(CLI), "tarea", verbo, *args,
                               "--proyecto", str(self.raiz)],
                              env=self.env, capture_output=True, text=True, timeout=30)

    def ok(self, verbo, *args):
        p = self.cli(verbo, *args)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        return p

    def instantanea(self):
        return {str(p.relative_to(self.raiz)): (p.read_bytes() if p.is_file() else None)
                for p in sorted(self.raiz.rglob("*"))}


class ListarAlineadoTests(TrackerTemporal):
    def test_ids_largos_y_cortos_comparten_columnas_sin_espacios_finales(self):
        self.tarea(CORTA, "Corta", etiquetas="x")
        self.tarea(LARGA, "Larga", etiquetas="bug, sensor, procesos")
        filas = [l for l in self.ok("listar").stdout.splitlines() if l.strip()]
        self.assertEqual(len(filas), 2)
        for fila in filas:
            self.assertEqual(fila, fila.rstrip(), "espacio final en la fila")
        columnas = [fila.index("ABIERTA") for fila in filas]
        self.assertEqual(columnas[0], columnas[1], filas)
        titulos = [fila.rindex("Corta" if "Corta" in fila else "Larga") for fila in filas]
        self.assertEqual(titulos[0], titulos[1], filas)


class ArchivoEtiquetasTests(TrackerTemporal):
    def setUp(self):
        super().setUp()
        self.tarea(CORTA, "Con bug", etiquetas="bug, UI")
        self.tarea(LARGA, "Sin etiquetas", etiquetas="")

    def test_revisar_acepta_el_archivo_como_auxiliar(self):
        (self.raiz / "tareas/etiquetas").write_text(
            "bug, algo que falla\n\n   \nui    interfaz de usuario\nvacia\n", encoding="utf-8")
        self.ok("revisar")

    def test_resumen_muestra_descripciones_y_tareas_sin_etiquetas(self):
        (self.raiz / "tareas/etiquetas").write_text(
            "bug, algo que falla\nui    interfaz de usuario\n", encoding="utf-8")
        texto = self.ok("resumen").stdout
        self.assertIn("algo que falla", texto)
        self.assertIn("interfaz de usuario", texto)  # UI en la tarea, ui en el archivo
        datos = json.loads(self.ok("resumen", "--json").stdout)
        self.assertEqual(datos["sin_etiquetas"], 1)
        volcado = json.dumps(datos, ensure_ascii=False)
        self.assertIn("algo que falla", volcado)
        self.assertNotIn(", algo que falla", volcado)

    def test_redefinicion_falla_revisar_con_linea_y_no_resumen(self):
        (self.raiz / "tareas/etiquetas").write_text(
            "bug primera\nbug segunda\n", encoding="utf-8")
        p = self.cli("revisar")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertRegex(p.stdout + p.stderr, r"etiquetas:2")
        r = self.ok("resumen")
        self.assertIn("segunda", r.stdout)
        self.assertNotIn("primera", r.stdout)
        self.assertTrue(r.stderr.strip(), "la redefinición debe avisar por stderr")

    def test_utf8_invalido_es_diagnostico_sin_traceback(self):
        (self.raiz / "tareas/etiquetas").write_bytes(b"bug \xff\xfe\n")
        p = self.cli("revisar")
        self.assertEqual(p.returncode, 1)
        self.assertNotIn("Traceback", p.stderr)
        self.assertIn("etiquetas", p.stdout + p.stderr)

    @unittest.skipUnless(hasattr(os, "symlink"), "requiere enlaces simbólicos")
    def test_enlace_simbolico_no_se_sigue(self):
        afuera = self.raiz.parent / "secreto"
        afuera.write_text("bug SECRETO-DE-AFUERA\n", encoding="utf-8")
        (self.raiz / "tareas/etiquetas").symlink_to(afuera)
        self.assertNotIn("SECRETO-DE-AFUERA", self.cli("resumen").stdout)
        self.assertEqual(self.cli("revisar").returncode, 1)

    def test_hechos_lo_inventaria_como_auxiliar(self):
        (self.raiz / "tareas/etiquetas").write_text("bug algo\n", encoding="utf-8")
        hechos = json.loads(self.ok("hechos").stdout)
        filas = [f for f in hechos["archivo_seguimiento"] if f["ruta"] == "tareas/etiquetas"]
        self.assertEqual(len(filas), 1, hechos["archivo_seguimiento"])
        self.assertEqual(filas[0]["clase"], "auxiliar")
        self.assertEqual(filas[0]["tarea_id"], "")


class EtiquetarTests(TrackerTemporal):
    def test_preserva_crlf_campos_desconocidos_y_cuerpo(self):
        ruta = self.tarea(CORTA, "Crlf", etiquetas="bug", extra="- DUEÑO: brian",
                          cuerpo="Texto\r\n- ETIQUETAS: no-es-metadato", fin="\r\n")
        antes = ruta.read_bytes()
        p = self.ok("etiquetar", CORTA, "--etiqueta", "ui,Sensor")
        despues = ruta.read_bytes()
        self.assertEqual(despues, antes.replace(b"- ETIQUETAS: bug\r\n",
                                                b"- ETIQUETAS: bug, ui, Sensor\r\n"))
        self.assertRegex(p.stdout, rf"tareas/{CORTA}/TAREA\.md:5:")

    def test_inserta_la_linea_ausente_al_final_del_bloque(self):
        ruta = self.tarea(CORTA, "Sin línea", etiquetas=None, extra="- OTRO: x", cuerpo="Cuerpo")
        self.ok("etiquetar", CORTA, "--etiqueta", "bug")
        lineas = ruta.read_text(encoding="utf-8").splitlines()
        self.assertEqual(lineas[2:7], ["- ESTADO: ABIERTA", "- PRIORIDAD: 50", "- OTRO: x",
                                       "- ETIQUETAS: bug", ""])
        self.assertEqual(lineas[-1], "Cuerpo")

    def test_idempotente_e_insensible_a_mayusculas_no_reescribe(self):
        ruta = self.tarea(CORTA, "Ya etiquetada", etiquetas="Bug")
        os.utime(ruta, (1_000_000_000, 1_000_000_000))
        antes = ruta.read_bytes()
        p = self.ok("etiquetar", CORTA, "--etiqueta", "bug")
        self.assertEqual(ruta.read_bytes(), antes)
        self.assertEqual(ruta.stat().st_mtime, 1_000_000_000)
        self.assertIn("0 tarea", p.stdout)

    def test_prefijo_inequivoco(self):
        ruta = self.tarea(LARGA, "Larga", etiquetas="")
        self.ok("etiquetar", "20260914-100001-investigar", "--etiqueta", "bug")
        self.assertIn("- ETIQUETAS: bug", ruta.read_text(encoding="utf-8"))

    def test_etiquetar_sin_ids_o_sin_etiqueta_falla(self):
        self.tarea(CORTA, "A", etiquetas="")
        antes = self.instantanea()
        self.assertNotEqual(self.cli("etiquetar", "--etiqueta", "bug").returncode, 0)
        self.assertNotEqual(self.cli("etiquetar", CORTA).returncode, 0)
        self.assertEqual(self.instantanea(), antes)

    def test_registro_roto_no_escribe_ninguna_tarea(self):
        self.tarea(CORTA, "Sana", etiquetas="")
        rota = self.raiz / "tareas/20260914-100009-rota"
        rota.mkdir()
        (rota / "TAREA.md").write_text("# Rota\n\n- ESTADO: QUIZAS\n- PRIORIDAD: 1\n")
        antes = self.instantanea()
        p = self.cli("etiquetar", CORTA, "--etiqueta", "bug")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertEqual(self.instantanea(), antes)


class DesetiquetarTests(TrackerTemporal):
    def setUp(self):
        super().setUp()
        self.abierta = self.tarea(CORTA, "Abierta", etiquetas="vieja, bug")
        self.cerrada = self.tarea(LARGA, "Cerrada", estado="CERRADA", etiquetas="Vieja")

    def test_masivo_toca_solo_abiertas_por_defecto(self):
        self.ok("desetiquetar", "--etiqueta", "vieja")
        self.assertIn("- ETIQUETAS: bug\n", self.abierta.read_text(encoding="utf-8"))
        self.assertIn("- ETIQUETAS: Vieja\n", self.cerrada.read_text(encoding="utf-8"))

    def test_masivo_con_todas_incluye_cerradas_y_la_ultima_queda_como_nueva(self):
        self.ok("desetiquetar", "--etiqueta", "vieja", "--todas")
        self.assertIn("- ETIQUETAS: bug\n", self.abierta.read_text(encoding="utf-8"))
        lineas = self.cerrada.read_text(encoding="utf-8").splitlines()
        self.assertEqual([l for l in lineas if "ETIQUETAS" in l], ["- ETIQUETAS: "])

    def test_ids_explicitos_con_filtro_de_estado_es_error_sin_escrituras(self):
        antes = self.instantanea()
        p = self.cli("desetiquetar", CORTA, "--etiqueta", "vieja", "--todas")
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("Traceback", p.stderr)
        self.assertEqual(self.instantanea(), antes)

    def test_ids_explicitos_ignoran_estado(self):
        self.ok("desetiquetar", LARGA, "--etiqueta", "vieja")
        self.assertNotIn("Vieja", self.cerrada.read_text(encoding="utf-8"))
        self.assertIn("vieja", self.abierta.read_text(encoding="utf-8"))


class GrafoTests(TrackerTemporal):
    def test_borde_de_token_autoarista_duplicados_y_cerradas(self):
        self.tarea(SENSOR, 'Título con "comillas" y \\barra', cuerpo=(
            f"Me menciono: {SENSOR}. Depende de {SENSOR_2} y de {SENSOR_2} otra vez."))
        self.tarea(SENSOR_2, "Sensor dos", estado="CERRADA", cuerpo=f"Ver {CORTA}")
        self.tarea(CORTA, "Aislada no", cuerpo=f"Prefijo {SENSOR}-2x no cuenta")
        self.tarea(LARGA, "Aislada")
        datos = json.loads(self.ok("grafo", "--json").stdout)
        aristas = [(a["origen"], a["destino"]) for a in datos["aristas"]]
        self.assertEqual(aristas, sorted([(SENSOR, SENSOR_2), (SENSOR_2, CORTA)]))
        ids = [n["id"] for n in datos["nodos"]]
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(set(ids), {SENSOR, SENSOR_2, CORTA})
        self.assertEqual({n["id"]: n["estado"] for n in datos["nodos"]}[SENSOR_2], "CERRADA")

    def test_dot_escapa_y_es_determinista_sin_escribir_archivos(self):
        self.tarea(SENSOR, 'Con "comillas" y \\barra', cuerpo=f"Ver {SENSOR_2}")
        self.tarea(SENSOR_2, "Dos")
        antes = self.instantanea()
        uno, dos = self.ok("grafo").stdout, self.ok("grafo").stdout
        self.assertEqual(uno, dos)
        self.assertEqual(self.instantanea(), antes)
        self.assertTrue(uno.lstrip().startswith("digraph"), uno)
        self.assertIn(f'"{SENSOR}" -> "{SENSOR_2}"', uno)
        self.assertIn('\\"comillas\\"', uno)
        self.assertIn("\\\\barra", uno)
        if shutil.which("dot"):
            p = subprocess.run(["dot", "-Tsvg"], input=uno, capture_output=True, text=True,
                               timeout=30)
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_sin_aristas_es_grafo_vacio_valido(self):
        self.tarea(CORTA, "Sola")
        self.assertRegex(self.ok("grafo").stdout.strip(), r"^digraph[^{]*\{\s*\}$")
        self.assertEqual(json.loads(self.ok("grafo", "--json").stdout),
                         {"nodos": [], "aristas": []})

    def test_registro_roto_sale_uno(self):
        self.tarea(CORTA, "Sana")
        rota = self.raiz / "tareas/20260914-100009-rota"
        rota.mkdir()
        p = self.cli("grafo")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stderr)


class AyudaTests(TrackerTemporal):
    def test_ayuda_de_verbos_nuevos_no_escribe(self):
        antes = self.instantanea()
        for verbo in ("etiquetar", "desetiquetar", "grafo"):
            self.ok(verbo, "--help")
        general = subprocess.run([sys.executable, "-B", str(CLI), "tarea", "--help"],
                                 env=self.env, capture_output=True, text=True, timeout=30)
        for verbo in ("etiquetar", "desetiquetar", "grafo"):
            self.assertRegex(general.stdout, rf"\b{verbo}\b")
        self.assertEqual(self.instantanea(), antes)


if __name__ == "__main__":
    unittest.main()


class GrafoErroresOperacionalesTests(TrackerTemporal):
    """Sobrevivientes de la primera ronda: tareas_grafo.py:32 y :56 no tenían código fijado."""

    def test_sin_tracker_sale_exactamente_uno(self):
        sin_tracker = self.raiz.parent / "vacio"
        sin_tracker.mkdir()
        p = subprocess.run([sys.executable, "-B", str(CLI), "tarea", "grafo",
                            "--proyecto", str(sin_tracker)],
                           env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stderr)

    def test_lectura_fallida_tras_la_auditoria_sale_exactamente_uno(self):
        import contextlib
        import io
        from unittest import mock
        from tools import tareas_grafo

        self.tarea(CORTA, "Legible")
        salida, errores = io.StringIO(), io.StringIO()
        with mock.patch.object(Path, "read_text", side_effect=OSError("disco ausente")), \
                contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = tareas_grafo.cmd_grafo([], ["--proyecto", str(self.raiz)])
        self.assertEqual(codigo, 1)
        self.assertIn("disco ausente", errores.getvalue())
        self.assertEqual(salida.getvalue(), "")


class SobrevivientesTareasTests(TrackerTemporal):
    """Sobrevivientes de la primera ronda sobre tools/tareas.py con comportamiento observable."""

    def test_listar_formato_exacto_con_y_sin_etiquetas(self):
        self.tarea(CORTA, "A", prioridad=50, etiquetas="x")
        self.tarea(LARGA, "B", estado="CERRADA", prioridad=5, etiquetas="")
        ancho = len(LARGA)
        self.assertEqual(self.ok("listar", "--todas").stdout.splitlines(), [
            f"{CORTA:<{ancho}} ABIERTA P50 [x] A",
            f"{LARGA} CERRADA P5      B",
        ])
        self.assertEqual(self.ok("listar", "--cerradas").stdout.splitlines(),
                         [f"{LARGA} CERRADA P5 B"])

    def test_limite_de_dos_mib_en_el_borde(self):
        self.tarea(CORTA, "A")
        archivo = self.raiz / "tareas/etiquetas"
        # 2048 etiquetas distintas de 1024 bytes cada línea: justo 2 MiB, sin redefiniciones.
        contenido = b"".join(b"t%04d " % i + b"x" * 1017 + b"\n" for i in range(2048))
        archivo.write_bytes(contenido)
        self.assertEqual(archivo.stat().st_size, 2 * 1024 * 1024)
        self.ok("revisar")
        archivo.write_bytes(contenido + b"y")
        p = self.cli("revisar")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        self.assertIn("2 MiB", p.stdout + p.stderr)

    def test_error_de_lectura_del_archivo_de_etiquetas(self):
        import contextlib
        import io
        from unittest import mock
        from tools import tareas

        self.tarea(CORTA, "A")
        (self.raiz / "tareas/etiquetas").write_text("bug algo\n", encoding="utf-8")
        leer = Path.read_bytes

        def falla_en_etiquetas(ruta):
            if ruta.name == "etiquetas":
                raise OSError("sector ilegible")
            return leer(ruta)

        salida = io.StringIO()
        with mock.patch.object(Path, "read_bytes", falla_en_etiquetas), \
                contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            codigo = tareas.cmd_revisar([], ["--proyecto", str(self.raiz)])
        self.assertEqual(codigo, 1)
        self.assertIn("sector ilegible", salida.getvalue())

    def test_insercion_usa_el_fin_de_linea_del_documento(self):
        crlf = self.tarea(CORTA, "Crlf", etiquetas=None, cuerpo="Cuerpo", fin="\r\n")
        lf = self.tarea(LARGA, "Lf", etiquetas=None, cuerpo="Cuerpo")
        self.ok("etiquetar", CORTA, LARGA, "--etiqueta", "bug")
        self.assertIn(b"- PRIORIDAD: 50\r\n- ETIQUETAS: bug\r\n\r\n", crlf.read_bytes())
        self.assertIn(b"- PRIORIDAD: 50\n- ETIQUETAS: bug\n\n", lf.read_bytes())
        self.assertNotIn(b"\r", lf.read_bytes())

    def test_documento_en_blanco_es_tarea_invalida(self):
        from tools import tareas

        for texto in ("", "\n  \n\t\n"):
            with self.assertRaises(tareas.TareaInvalida):
                tareas._aplicar_etiquetas_texto(texto, ["bug"], modo="agregar", id_tarea=CORTA,
                                                ruta_tarea=self.raiz / "TAREA.md")

    def test_linea_en_blanco_antes_del_titulo(self):
        ruta = self.raiz / "tareas" / CORTA / "TAREA.md"
        ruta.parent.mkdir()
        ruta.write_bytes(b"\n# T\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n")
        self.ok("etiquetar", CORTA, "--etiqueta", "bug")
        self.assertEqual(ruta.read_bytes(),
                         b"\n# T\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n- ETIQUETAS: bug\n")

    def test_etiquetas_como_primer_metadato(self):
        for sep in (b"", b"\n"):
            with self.subTest(linea_en_blanco=bool(sep)):
                ruta = self.raiz / "tareas" / CORTA / "TAREA.md"
                ruta.parent.mkdir(exist_ok=True)
                resto = b"- ESTADO: ABIERTA\n- PRIORIDAD: 50\n"
                ruta.write_bytes(b"# T\n" + sep + b"- ETIQUETAS: a\n" + resto)
                p = self.ok("etiquetar", CORTA, "--etiqueta", "b")
                self.assertEqual(ruta.read_bytes(), b"# T\n" + sep + b"- ETIQUETAS: a, b\n" + resto)
                self.assertIn(f"TAREA.md:{2 + len(sep)}:", p.stdout)

    def test_insercion_informa_la_linea_insertada(self):
        self.tarea(CORTA, "T", etiquetas=None)
        self.assertIn("TAREA.md:5:", self.ok("etiquetar", CORTA, "--etiqueta", "bug").stdout)

    def test_titulo_sin_metadatos_ni_fin_de_linea(self):
        from tools import tareas

        modificado, texto, _ = tareas._aplicar_etiquetas_texto(
            "# T", ["bug"], modo="agregar", id_tarea=CORTA, ruta_tarea=self.raiz / "TAREA.md")
        self.assertTrue(modificado)
        self.assertEqual(texto, "# T\n- ETIQUETAS: bug\n")

    def test_salto_de_linea_en_la_etiqueta_se_rechaza_sin_escribir(self):
        self.tarea(CORTA, "T", etiquetas="a")
        for mala in ("bug\n", "bug\r", "a,b\nc"):
            with self.subTest(etiqueta=mala):
                antes = self.instantanea()
                p = self.cli("etiquetar", CORTA, "--etiqueta", mala)
                self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
                self.assertIn("saltos de línea", p.stderr)
                self.assertEqual(self.instantanea(), antes)

    def test_rechazo_al_releer_la_tarea_sale_exactamente_uno(self):
        import contextlib
        import io
        from unittest import mock
        from tools import tareas

        ruta = self.tarea(CORTA, "T", etiquetas="a")
        antes = ruta.read_bytes()
        errores = io.StringIO()
        with mock.patch.object(tareas, "asegurar_confinamiento_archivo",
                               side_effect=tareas.RutaInsegura("fuera del tracker")), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errores):
            codigo = tareas.cmd_etiquetar([], [CORTA, "--etiqueta", "b", "--proyecto", str(self.raiz)])
        self.assertEqual(codigo, 1)
        self.assertIn("fuera del tracker", errores.getvalue())
        self.assertEqual(ruta.read_bytes(), antes)

    def test_json_sale_exactamente_cero(self):
        import contextlib
        import io
        from tools import tareas

        self.tarea(CORTA, "T", etiquetas="a")
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = tareas.cmd_etiquetar([], [CORTA, "--etiqueta", "b", "--json",
                                               "--proyecto", str(self.raiz)])
        self.assertEqual(codigo, 0)
        self.assertEqual([c["despues"] for c in json.loads(salida.getvalue())], ["a, b"])

    def test_fallo_de_escritura_a_mitad_informa_las_escritas_y_sale_uno(self):
        import contextlib
        import io
        from unittest import mock
        from tools import tareas

        self.tarea(CORTA, "Primera", etiquetas="a")
        segunda = self.tarea(LARGA, "Segunda", etiquetas="a")
        antes = segunda.read_bytes()
        real = tareas.guardar_documento_atomico

        def falla_la_segunda(ruta, contenido):
            if ruta.parent.name == LARGA:
                raise OSError("disco lleno")
            real(ruta, contenido)

        errores = io.StringIO()
        with mock.patch.object(tareas, "guardar_documento_atomico", falla_la_segunda), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errores):
            codigo = tareas.cmd_etiquetar([], [CORTA, LARGA, "--etiqueta", "b",
                                               "--proyecto", str(self.raiz)])
        self.assertEqual(codigo, 1)
        self.assertIn("disco lleno", errores.getvalue())
        self.assertIn(f"Tareas escritas previamente: {CORTA}", errores.getvalue())
        self.assertEqual(segunda.read_bytes(), antes)

    def test_errores_de_entrada_salen_exactamente_uno(self):
        self.tarea(CORTA, "T", etiquetas="a")
        sin_tracker = self.raiz.parent / "sin-tracker"
        sin_tracker.mkdir()
        casos = {
            "etiquetar id inexistente": ["etiquetar", "20991231-000000-nada", "--etiqueta", "b"],
            "desetiquetar id inexistente": ["desetiquetar", "20991231-000000-nada", "--etiqueta", "a"],
            "desetiquetar etiqueta con salto": ["desetiquetar", CORTA, "--etiqueta", "a\n"],
        }
        for nombre, argumentos in casos.items():
            with self.subTest(nombre):
                antes = self.instantanea()
                p = self.cli(*argumentos)
                self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
                self.assertNotIn("Traceback", p.stderr)
                self.assertEqual(self.instantanea(), antes)
        for verbo in ("etiquetar", "desetiquetar"):
            with self.subTest(f"{verbo} sin tracker"):
                p = subprocess.run([sys.executable, "-B", str(CLI), "tarea", verbo, CORTA,
                                    "--etiqueta", "a", "--proyecto", str(sin_tracker)],
                                   env=self.env, capture_output=True, text=True, timeout=30)
                self.assertEqual(p.returncode, 1, p.stdout + p.stderr)

    def test_desetiquetar_con_registro_roto_sale_uno_sin_escribir(self):
        self.tarea(CORTA, "Sana", etiquetas="vieja")
        (self.raiz / "tareas/20260914-100009-rota").mkdir()
        antes = self.instantanea()
        p = self.cli("desetiquetar", "--etiqueta", "vieja")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertEqual(self.instantanea(), antes)

    def test_desetiquetar_cerradas_no_toca_abiertas(self):
        abierta = self.tarea(CORTA, "Abierta", etiquetas="vieja")
        cerrada = self.tarea(LARGA, "Cerrada", estado="CERRADA", etiquetas="vieja")
        self.ok("desetiquetar", "--etiqueta", "vieja", "--cerradas")
        self.assertIn("- ETIQUETAS: vieja\n", abierta.read_text(encoding="utf-8"))
        self.assertIn("- ETIQUETAS: \n", cerrada.read_text(encoding="utf-8"))
