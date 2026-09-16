"""Tests de comportamiento para evidencia relacional del tracker propio (P3).

Cubre el comando `oracle tarea hechos [--git] [--json]` a través del CLI público
sobre proyectos temporales, verificando el contrato relacional, determinismo
byte por byte, inventario seguro de archivos, extracción y clasificación de
referencias Markdown, registro de omisiones y códigos de salida.
"""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools import cli, tareas, tareas_hechos


class TareasHechosTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.raiz = Path(self.td.name).resolve()
        # Inicializar el tracker de tareas en el proyecto temporal
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])

    def tearDown(self) -> None:
        self.td.cleanup()

    def _callado(self, funcion, *args, **kwargs) -> tuple[int, str, str]:
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                rc = funcion(*args, **kwargs)
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else (1 if e.code else 0)
        return rc, out.getvalue(), err.getvalue()

    def _crear_tarea(
        self,
        titulo: str = "Tarea de prueba",
        etiquetas: list[str] | None = None,
        prioridad: int = 50,
        sufijo: str | None = None,
    ) -> tuple[str, Path]:
        cmd = ["--proyecto", str(self.raiz), "tarea", "nueva", titulo, "--json"]
        if etiquetas:
            for e in etiquetas:
                cmd.extend(["--etiqueta", e])
        if prioridad != 50:
            cmd.extend(["--prioridad", str(prioridad)])
        if sufijo:
            cmd.extend(["--sufijo", sufijo])

        rc, out, err = self._callado(cli.main, cmd)
        self.assertEqual(rc, 0, f"Fallo al crear tarea: {err}")
        datos = json.loads(out)
        return datos["id"], Path(datos["ruta"])


class TestHechosEsquemaYDeterminismo(TareasHechosTestCase):
    """Pruebas de conformidad de esquema JSON y determinismo byte por byte."""

    def test_hechos_esquema_y_seis_claves_siempre_presentes(self) -> None:
        """Las seis relaciones están siempre, incluso vacías: una relación que aparece sólo cuando
        tiene filas obliga a cada política a preguntarse si falta o si está vacía."""
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        claves_esperadas = {
            "archivo_seguimiento",
            "commit_seguimiento",
            "lectura_seguimiento",
            "omision_seguimiento",
            "referencia_seguimiento",
            "tarea_seguimiento",
        }
        self.assertEqual(set(datos.keys()), claves_esperadas)

        self.assertEqual(len(datos["lectura_seguimiento"]), 1)
        lectura = datos["lectura_seguimiento"][0]
        self.assertEqual(lectura["esquema"], "oracle.tareas.hechos/v1")
        self.assertIsInstance(lectura["completa"], bool)
        self.assertEqual(lectura["git"], "no_solicitado")
        self.assertEqual(lectura["head"], "")

    def test_hechos_determinismo_byte_por_byte(self) -> None:
        """Dos corridas sobre el mismo árbol estable deben emitir el mismo JSON byte por byte."""
        self._crear_tarea("Tarea primera", etiquetas=["alfa", "beta"], sufijo="primera")
        self._crear_tarea("Tarea segunda", etiquetas=["gamma"], prioridad=80, sufijo="segunda")

        rc1, out1, err1 = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc1, 0, err1)

        rc2, out2, err2 = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc2, 0, err2)

        self.assertEqual(out1, out2)


class TestHechosTareasYArchivos(TareasHechosTestCase):
    """Pruebas de extracción de datos declarados e inventario de archivos."""

    def test_hechos_datos_declarados_tarea(self) -> None:
        """Verifica metadatos declarados y hash SHA-256 del documento TAREA.md."""
        id_tarea, ruta_md = self._crear_tarea(
            "Investigar sensor",
            etiquetas=["bug", "sensor"],
            prioridad=75,
            sufijo="sensor",
        )

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos", "--json"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        tareas_lista = datos["tarea_seguimiento"]
        self.assertEqual(len(tareas_lista), 1)
        t = tareas_lista[0]
        self.assertEqual(t["id"], id_tarea)
        self.assertEqual(t["titulo"], "Investigar sensor")
        self.assertEqual(t["estado_declarado"], "ABIERTA")
        self.assertEqual(t["prioridad_declarada"], 75)
        self.assertTrue(t["ruta"].endswith("TAREA.md"))
        self.assertEqual(len(t["sha256_documento"]), 64)

    def test_hechos_inventario_archivos_y_auxiliares(self) -> None:
        """Verifica clasificación de documento, adjunto y auxiliares documentados."""
        id_tarea, ruta_md = self._crear_tarea("Tarea con adjuntos", sufijo="adj")
        carpeta_tarea = ruta_md.parent

        adjunto = carpeta_tarea / "datos.csv"
        adjunto.write_text("a,b,c\n1,2,3\n", encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        archivos = {a["ruta"]: a for a in datos["archivo_seguimiento"]}

        self.assertIn("tareas/README.md", archivos)
        aux = archivos["tareas/README.md"]
        self.assertEqual(aux["clase"], "auxiliar")
        self.assertEqual(aux["tarea_id"], "")
        self.assertEqual(aux["tipo"], "regular")
        self.assertTrue(aux["existe"])

        rel_md = ruta_md.relative_to(self.raiz).as_posix()
        self.assertIn(rel_md, archivos)
        doc = archivos[rel_md]
        self.assertEqual(doc["clase"], "documento")
        self.assertEqual(doc["tarea_id"], id_tarea)
        self.assertEqual(doc["tipo"], "regular")

        rel_adj = adjunto.relative_to(self.raiz).as_posix()
        self.assertIn(rel_adj, archivos)
        adj = archivos[rel_adj]
        self.assertEqual(adj["clase"], "adjunto")
        self.assertEqual(adj["tarea_id"], id_tarea)
        self.assertEqual(adj["tipo"], "regular")

    def test_hechos_no_lee_binarios_ni_se_bloquea_en_fifo(self) -> None:
        """Comprueba que adjuntos binarios sólo inventarían stat y FIFOs causan omisión sin bloqueo."""
        id_tarea, ruta_md = self._crear_tarea("Tarea con binario", sufijo="binario")
        carpeta_tarea = ruta_md.parent

        binario = carpeta_tarea / "imagen.png"
        binario.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + b"\x00" * 100)

        tiene_fifo = False
        fifo_path = carpeta_tarea / "canal.pipe"
        if hasattr(os, "mkfifo"):
            try:
                os.mkfifo(fifo_path)
                tiene_fifo = True
            except OSError:
                pass

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        archivos = {a["ruta"]: a for a in datos["archivo_seguimiento"]}
        rel_bin = binario.relative_to(self.raiz).as_posix()
        self.assertIn(rel_bin, archivos)
        self.assertEqual(archivos[rel_bin]["clase"], "adjunto")
        self.assertEqual(archivos[rel_bin]["tipo"], "regular")
        self.assertEqual(archivos[rel_bin]["tamano_bytes"], len(binario.read_bytes()))

        if tiene_fifo:
            rel_fifo = fifo_path.relative_to(self.raiz).as_posix()
            self.assertIn(rel_fifo, archivos)
            self.assertEqual(archivos[rel_fifo]["tipo"], "especial")
            omisiones = [o for o in datos["omision_seguimiento"] if o["ruta"] == rel_fifo]
            self.assertTrue(len(omisiones) > 0)
            self.assertFalse(datos["lectura_seguimiento"][0]["completa"])


class TestHechosReferenciasMarkdown(TareasHechosTestCase):
    """Pruebas de extracción y clasificación de referencias cruzadas."""

    def test_hechos_referencias_locales_presentes_y_rotas(self) -> None:
        """Distingue referencias locales presentes de rotas/ausentes en disco."""
        id_tarea, ruta_md = self._crear_tarea("Tarea con enlaces", sufijo="links")
        carpeta_tarea = ruta_md.parent

        archivo_presente = carpeta_tarea / "existente.txt"
        archivo_presente.write_text("contenido existente", encoding="utf-8")

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += (
            "\n\n## Referencias\n"
            "- Ver [adjunto](existente.txt)\n"
            "- Ver [perdido](no_existe.txt)\n"
        )
        ruta_md.write_text(contenido, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        refs = {r["destino_declarado"]: r for r in datos["referencia_seguimiento"]}
        self.assertIn("existente.txt", refs)
        self.assertEqual(refs["existente.txt"]["clase"], "local")
        self.assertEqual(refs["existente.txt"]["estado"], "presente")

        self.assertIn("no_existe.txt", refs)
        self.assertEqual(refs["no_existe.txt"]["clase"], "local")
        self.assertEqual(refs["no_existe.txt"]["estado"], "ausente")

    def test_hechos_multiples_apariciones_en_misma_linea(self) -> None:
        """Conserva una fila por cada aparición aunque compartan el mismo destino en la misma línea."""
        id_tarea, ruta_md = self._crear_tarea("Tarea doble link", sufijo="doble")
        carpeta_tarea = ruta_md.parent

        doc = carpeta_tarea / "archivo.txt"
        doc.write_text("ok", encoding="utf-8")

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += "\n- Ver [primero](archivo.txt) y [segundo](archivo.txt)\n"
        ruta_md.write_text(contenido, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        coincidencias = [
            r for r in datos["referencia_seguimiento"] if r["destino_declarado"] == "archivo.txt"
        ]
        self.assertEqual(len(coincidencias), 2)

    def test_hechos_esquemas_mayusculas_y_autolinks(self) -> None:
        """Clasifica URLs http/https como remotas sin importar mayúsculas y preserva texto original."""
        id_tarea, ruta_md = self._crear_tarea("Tarea con URLs", sufijo="urls")

        self._callado(
            cli.main,
            [
                "--proyecto",
                str(self.raiz),
                "tarea",
                "anotar",
                id_tarea,
                "Nota técnica",
                "--url",
                "HTTPS://YOUTUBE.COM/WATCH?V=EJEMPLO&T=42S",
            ],
        )

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += (
            "\n- Enlace web: [sitio](HTTP://EXAMPLE.COM/GUIA)\n"
            "- Salto interno: [sección](#arquitectura)\n"
            "- Autolink mayúsculas: <HTTPS://EXAMPLE.ORG/API>\n"
        )
        ruta_md.write_text(contenido, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        refs = {r["destino_declarado"]: r for r in datos["referencia_seguimiento"]}

        self.assertIn("HTTPS://YOUTUBE.COM/WATCH?V=EJEMPLO&T=42S", refs)
        self.assertEqual(refs["HTTPS://YOUTUBE.COM/WATCH?V=EJEMPLO&T=42S"]["clase"], "remota")
        self.assertEqual(refs["HTTPS://YOUTUBE.COM/WATCH?V=EJEMPLO&T=42S"]["estado"], "no_comprobado")

        self.assertIn("HTTP://EXAMPLE.COM/GUIA", refs)
        self.assertEqual(refs["HTTP://EXAMPLE.COM/GUIA"]["clase"], "remota")

        self.assertIn("HTTPS://EXAMPLE.ORG/API", refs)
        self.assertEqual(refs["HTTPS://EXAMPLE.ORG/API"]["clase"], "remota")

        self.assertIn("#arquitectura", refs)
        self.assertEqual(refs["#arquitectura"]["clase"], "ancla")

    def test_hechos_sintaxis_multilinea_o_incompleta_genera_omision(self) -> None:
        """Sintaxis de enlace partida en múltiples líneas no se pierde silenciosamente sino que genera omisión."""
        id_tarea, ruta_md = self._crear_tarea("Tarea multilinea", sufijo="multilinea")

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += "\n- [nota](\nausente.txt)\n"
        ruta_md.write_text(contenido, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        omisiones = datos["omision_seguimiento"]
        self.assertTrue(any("sintaxis de enlace incompleta" in o["motivo"] for o in omisiones))
        self.assertFalse(datos["lectura_seguimiento"][0]["completa"])

    def test_hechos_corchetes_escapados_no_son_enlaces(self) -> None:
        """Los corchetes precedidos por barra invertida son literales y no deben extraerse como enlaces."""
        id_tarea, ruta_md = self._crear_tarea("Tarea corchetes escapados", sufijo="esc")

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += "\n- Texto con \\[literal](no_es_link.txt)\n"
        ruta_md.write_text(contenido, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        destinos = [r["destino_declarado"] for r in datos["referencia_seguimiento"]]
        self.assertNotIn("no_es_link.txt", destinos)

    def test_hechos_cerca_de_codigo_con_texto_no_cierra_bloque(self) -> None:
        """Una línea con ```texto dentro de un bloque cercado no actúa como cierre."""
        id_tarea, ruta_md = self._crear_tarea("Tarea cerca", sufijo="cerca")

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += (
            "\n```python\n"
            "```no-es-cierre\n"
            "[falso](no_debe_salir.txt)\n"
            "```\n"
        )
        ruta_md.write_text(contenido, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        destinos = [r["destino_declarado"] for r in datos["referencia_seguimiento"]]
        self.assertNotIn("no_debe_salir.txt", destinos)

    def test_hechos_referencia_puente_symlink_con_puntos_causa_omision(self) -> None:
        """La ruta puente/../parece-local.txt con puente simbólico no se normaliza a presente."""
        id_tarea, ruta_md = self._crear_tarea("Tarea puente", sufijo="puente")
        carpeta_tarea = ruta_md.parent

        (carpeta_tarea / "parece-local.txt").write_text("hola", encoding="utf-8")

        # Crear puente simbólico a directorio
        destino_dir = self.raiz / "otro_dir"
        destino_dir.mkdir()
        puente_sym = carpeta_tarea / "puente"
        try:
            puente_sym.symlink_to(destino_dir)
        except OSError:
            self.skipTest("El sistema de archivos no admite enlaces simbólicos")

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += "\n- [trampa](puente/../parece-local.txt)\n"
        ruta_md.write_text(contenido, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        refs = {r["destino_declarado"]: r for r in datos["referencia_seguimiento"]}
        self.assertIn("puente/../parece-local.txt", refs)
        self.assertEqual(refs["puente/../parece-local.txt"]["estado"], "no_comprobado")

        omisiones = [o for o in datos["omision_seguimiento"] if "puente" in o["motivo"]]
        self.assertTrue(len(omisiones) > 0)
        self.assertFalse(datos["lectura_seguimiento"][0]["completa"])

    def test_hechos_componente_archivo_con_puntos_es_ausente(self) -> None:
        """Navegar a través de un archivo regular como si fuera directorio da ausente."""
        id_tarea, ruta_md = self._crear_tarea("Tarea archivo punto punto", sufijo="archpp")
        carpeta_tarea = ruta_md.parent

        (carpeta_tarea / "archivo.txt").write_text("texto", encoding="utf-8")
        (carpeta_tarea / "otro.txt").write_text("texto2", encoding="utf-8")

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += "\n- [invalido](archivo.txt/../otro.txt)\n"
        ruta_md.write_text(contenido, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        refs = {r["destino_declarado"]: r for r in datos["referencia_seguimiento"]}
        self.assertIn("archivo.txt/../otro.txt", refs)
        self.assertEqual(refs["archivo.txt/../otro.txt"]["estado"], "ausente")

    def test_hechos_referencias_escape_fuera_del_proyecto(self) -> None:
        """Referencias que intentan escapar de la raíz se marcan como fuera_del_proyecto sin leerlas."""
        id_tarea, ruta_md = self._crear_tarea("Tarea con escape", sufijo="escape")

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += (
            "\n- Escape relativo: [passwd](../../../../../../etc/passwd)\n"
            "- Escape absoluto: [root](/etc/shadow)\n"
        )
        ruta_md.write_text(contenido, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        refs = {r["destino_declarado"]: r for r in datos["referencia_seguimiento"]}
        self.assertIn("../../../../../../etc/passwd", refs)
        self.assertEqual(refs["../../../../../../etc/passwd"]["clase"], "local")
        self.assertEqual(refs["../../../../../../etc/passwd"]["estado"], "fuera_del_proyecto")

        self.assertIn("/etc/shadow", refs)
        self.assertEqual(refs["/etc/shadow"]["clase"], "local")
        self.assertEqual(refs["/etc/shadow"]["estado"], "fuera_del_proyecto")

    def test_hechos_nombres_unicode_espacios_y_percent_encoding(self) -> None:
        """Conserva destino_declarado exacto con percent encoding y resuelve presencia de archivos Unicode."""
        id_tarea, ruta_md = self._crear_tarea("Tarea Unicode", sufijo="unicode")

        origen_adjunto = self.raiz / "prueba cámara [1].png"
        origen_adjunto.write_bytes(b"datos de prueba")

        rc, out, err = self._callado(
            cli.main,
            [
                "--proyecto",
                str(self.raiz),
                "tarea",
                "adjuntar",
                id_tarea,
                str(origen_adjunto),
            ],
        )
        self.assertEqual(rc, 0, err)

        rc_h, out_h, err_h = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc_h, 0, err_h)
        datos = json.loads(out_h)

        refs = datos["referencia_seguimiento"]
        self.assertTrue(len(refs) > 0)
        ref_adj = refs[0]
        self.assertIn("%20", ref_adj["destino_declarado"])
        self.assertEqual(ref_adj["clase"], "local")
        self.assertEqual(ref_adj["estado"], "presente")

    def test_hechos_omisiones_sintaxis_no_soportada_y_esquemas_invalidos(self) -> None:
        """Registra omisión explícita ante enlaces por referencia [texto][clave], definiciones reales y esquemas ajenos."""
        id_tarea, ruta_md = self._crear_tarea("Tarea no soportada", sufijo="nosop")

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += (
            "\n[clave1]: destino.txt\n"
            "[clave2]:destino2.txt\n"
            "- Enlace no resuelto: [mi texto][clave1]\n"
            "- Esquema no admitido: [correo](mailto:dev@example.com)\n"
            "- Esquema de red: [red](//servidor/recurso)\n"
        )
        ruta_md.write_text(contenido, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        omisiones = datos["omision_seguimiento"]
        motivos = [o["motivo"] for o in omisiones]

        self.assertTrue(any("enlace por referencia no resuelto" in m for m in motivos))
        self.assertTrue(any("definición de enlace por referencia no resuelta: [clave1]" in m for m in motivos))
        self.assertTrue(any("definición de enlace por referencia no resuelta: [clave2]" in m for m in motivos))
        self.assertTrue(any("esquema no admitido" in m for m in motivos))
        self.assertTrue(any("no admitida" in m for m in motivos))

        self.assertFalse(datos["lectura_seguimiento"][0]["completa"])


class TestHechosLimitesYErrores(TareasHechosTestCase):
    """Pruebas de límites de tamaño, integridad de metadatos y opciones del CLI."""

    def test_hechos_permiso_denegado_falla_con_codigo_1(self) -> None:
        """Un archivo o directorio con permiso denegado falla con código 1 sin convertirse en falsa ausencia."""
        if os.name == "nt" or os.geteuid() == 0:
            self.skipTest("No aplicable en Windows o usuario root")

        id_tarea, ruta_md = self._crear_tarea("Tarea permisos", sufijo="perm")
        carpeta_tarea = ruta_md.parent

        privado = carpeta_tarea / "privado"
        privado.mkdir()
        (privado / "secreto.txt").write_text("shh", encoding="utf-8")

        contenido = ruta_md.read_text(encoding="utf-8")
        contenido += "\n- [secreto](privado/secreto.txt)\n"
        ruta_md.write_text(contenido, encoding="utf-8")

        privado.chmod(0o000)
        try:
            rc, out, err = self._callado(
                cli.main,
                ["--proyecto", str(self.raiz), "tarea", "hechos"],
            )
            self.assertEqual(rc, 1)
            self.assertIn("ERROR:", err)
        finally:
            privado.chmod(0o755)

    def test_hechos_tarea_md_central_grande_o_simbolico_falla_codigo_1(self) -> None:
        """Un documento TAREA.md central mayor a 2 MiB o simbólico falla con código 1 en prechequeo."""
        id_tarea, ruta_md = self._crear_tarea("Tarea enorme", sufijo="enorme")

        # 1. TAREA.md que supera 2 MiB falla con código 1
        contenido_enorme = "# Tarea\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n\n" + ("A" * (2 * 1024 * 1024 + 50))
        ruta_md.write_text(contenido_enorme, encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("supera el límite de 2 MiB", err)

        # 2. TAREA.md como enlace simbólico falla con código 1
        ruta_md.unlink()
        destino_md = self.raiz / "otro_md.txt"
        destino_md.write_text("# Tarea\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n", encoding="utf-8")
        try:
            ruta_md.symlink_to(destino_md)
        except OSError:
            self.skipTest("El sistema de archivos no admite enlaces simbólicos")

        rc_sym, out_sym, err_sym = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc_sym, 1)
        self.assertIn("no puede ser un enlace simbólico", err_sym)

    def test_hechos_archivo_markdown_adjunto_grande_se_omite(self) -> None:
        """Archivos Markdown adjuntos mayores a 2 MiB se omiten con completa=False sin abortar el proceso."""
        id_tarea, ruta_md = self._crear_tarea("Tarea con adj grande", sufijo="adjgrande")
        carpeta_tarea = ruta_md.parent

        doc_grande = carpeta_tarea / "adjunto_enorme.md"
        doc_grande.write_bytes(b"# Titulo\n" + b"A" * (2 * 1024 * 1024 + 100))

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        rel_doc = doc_grande.relative_to(self.raiz).as_posix()
        omisiones = [o for o in datos["omision_seguimiento"] if o["ruta"] == rel_doc]
        self.assertTrue(len(omisiones) > 0)
        self.assertIn("supera el límite de 2 MiB", omisiones[0]["motivo"])
        self.assertFalse(datos["lectura_seguimiento"][0]["completa"])

    def test_hechos_metadata_corrupta_falla_con_codigo_1(self) -> None:
        """La existencia de tareas corruptas aborta con código 1 sin emitir JSON parcial."""
        id_tarea, ruta_md = self._crear_tarea("Tarea a corromper", sufijo="corrupta")

        ruta_md.write_text(
            "# Tarea rota\n\n- ESTADO: DESCONOCIDO_ROTO\n- PRIORIDAD: 50\n\nCuerpo\n",
            encoding="utf-8",
        )

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)
        self.assertNotIn("lectura_seguimiento", out)

    def test_hechos_ayuda_no_escribe_en_disco(self) -> None:
        """La opción --help devuelve código 0 y no crea tareas/ ni escribe en disco."""
        td_vacio = tempfile.TemporaryDirectory()
        try:
            ruta_vacia = Path(td_vacio.name).resolve()
            rc, out, err = self._callado(
                cli.main,
                ["--proyecto", str(ruta_vacia), "tarea", "hechos", "--help"],
            )
            self.assertEqual(rc, 0)
            self.assertIn("oracle tarea hechos", out)
            self.assertFalse((ruta_vacia / "tareas").exists())
        finally:
            td_vacio.cleanup()

    def test_hechos_opcion_desconocida_devuelve_codigo_2(self) -> None:
        """Banderas u opciones no reconocidas devuelven código 2 de argparse."""
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos", "--opcion-inexistente"],
        )
        self.assertEqual(rc, 2)


class TestHechosIntegracionGit(TareasHechosTestCase):
    """Pruebas de la bandera opcional --git en proyectos con y sin repositorio."""

    def test_hechos_git_sin_repositorio(self) -> None:
        """Si se pasa --git en un directorio sin repositorio Git, reporta sin_repositorio."""
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos", "--git"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        lectura = datos["lectura_seguimiento"][0]
        self.assertEqual(lectura["git"], "sin_repositorio")
        self.assertEqual(lectura["head"], "")

        for a in datos["archivo_seguimiento"]:
            self.assertFalse(a["git_comprobado"])

    def test_hechos_git_con_repositorio_y_commits(self) -> None:
        """Si se pasa --git en un repo con commits, audita HEAD e índice de Git."""
        try:
            subprocess.run(
                ["git", "init", "-q"],
                cwd=self.raiz,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=self.raiz,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=self.raiz,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.skipTest("Git no disponible para inicializar repositorio temporal")

        self._crear_tarea("Tarea en Git", sufijo="git")

        try:
            subprocess.run(["git", "add", "."], cwd=self.raiz, check=True)
            subprocess.run(["git", "commit", "-m", "commit inicial", "-q"], cwd=self.raiz, check=True)
        except subprocess.CalledProcessError:
            self.skipTest("Fallo al comitear en repositorio temporal")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "hechos", "--git"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)

        lectura = datos["lectura_seguimiento"][0]
        self.assertEqual(lectura["git"], "comprobado")
        self.assertTrue(len(lectura["head"]) >= 7)

        archivos = {a["ruta"]: a for a in datos["archivo_seguimiento"]}
        readme = archivos.get("tareas/README.md")
        self.assertIsNotNone(readme)
        self.assertTrue(readme["git_comprobado"])
        self.assertTrue(readme["en_head"])
        self.assertTrue(readme["en_indice"])
