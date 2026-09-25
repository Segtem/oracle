"""Tests de comportamiento para captura y consultas de contexto de trabajo (P2).

Cubre los comandos `anotar`, `adjuntar`, `buscar`, `referencias` y `resumen` a través
del CLI público sobre proyectos temporales, verificando preservación, confinamiento,
límites, manejo de Unicode/espacios y códigos de salida sin efectos residuales.
"""
from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools import cli, tareas, tareas_contexto


class TareasContextoTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.raiz = Path(self.td.name).resolve()
        (self.raiz / ".git").mkdir()
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


class TestAnotar(TareasContextoTestCase):
    """Pruebas del comando `oracle tarea anotar`."""

    def test_anotar_agrega_texto_y_preserva_cuerpo_y_permisos(self) -> None:
        """Evita perder notas previas, alterar el cuerpo o degradar permisos del archivo."""
        id_tarea, ruta_md = self._crear_tarea("Verificar sensor", sufijo="sensor")
        ruta_md.chmod(0o640)

        rc, out, err = self._callado(
            cli.main,
            [
                "--proyecto",
                str(self.raiz),
                "tarea",
                "anotar",
                id_tarea,
                "Se detectó un jitter de 4 ms en la prueba de estrés.",
            ],
        )
        self.assertEqual(rc, 0, err)
        contenido = ruta_md.read_text(encoding="utf-8")
        self.assertIn("### Nota (", contenido)
        self.assertIn("Se detectó un jitter de 4 ms", contenido)
        self.assertIn("# Verificar sensor", contenido)
        if os.name != "nt":
            self.assertEqual(ruta_md.stat().st_mode & 0o777, 0o640)

    def test_anotar_preserva_sangria_y_espacios_significativos(self) -> None:
        """Evita aplicar strip al texto de la nota perdiendo indentación o espaciado deliberado."""
        id_tarea, ruta_md = self._crear_tarea("Nota sangrada", sufijo="sangria")
        texto_con_sangria = "    def snippet():\n        return 42"

        rc, out, err = self._callado(
            cli.main,
            [
                "--proyecto",
                str(self.raiz),
                "tarea",
                "anotar",
                id_tarea,
                texto_con_sangria,
            ],
        )
        self.assertEqual(rc, 0, err)
        contenido = ruta_md.read_text(encoding="utf-8")
        self.assertIn(texto_con_sangria, contenido)

    def test_anotar_con_url_y_marca_exactas(self) -> None:
        """Evita corromper parámetros query (?t=...) o perder la marca temporal en recursos."""
        id_tarea, ruta_md = self._crear_tarea("Investigar video", sufijo="video")
        url_original = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s"
        marca = "01:32"

        rc, out, err = self._callado(
            cli.main,
            [
                "--proyecto",
                str(self.raiz),
                "tarea",
                "anotar",
                id_tarea,
                "Momento exacto de la explicación",
                "--url",
                url_original,
                "--marca",
                marca,
                "--json",
            ],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        self.assertEqual(datos["url"], url_original)
        self.assertEqual(datos["marca"], marca)

        contenido = ruta_md.read_text(encoding="utf-8")
        self.assertIn(f"- URL: {url_original} (marca: {marca})", contenido)

    def test_anotar_rechaza_sin_texto_ni_url(self) -> None:
        """Evita crear notas vacías sin información útil."""
        id_tarea, ruta_md = self._crear_tarea("Tarea vacia", sufijo="vacia")
        antes = ruta_md.read_text(encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "anotar", id_tarea],
        )
        self.assertEqual(rc, 1)
        self.assertIn("se requiere al menos un texto o una --url", err)
        self.assertEqual(ruta_md.read_text(encoding="utf-8"), antes)

    def test_anotar_marca_sin_url_se_rechaza(self) -> None:
        """Evita registrar marcas temporales huérfanas sin una URL asociada."""
        id_tarea, _ = self._crear_tarea("Tarea marca", sufijo="marca")

        rc, out, err = self._callado(
            cli.main,
            [
                "--proyecto",
                str(self.raiz),
                "tarea",
                "anotar",
                id_tarea,
                "Texto sin url",
                "--marca",
                "10:20",
            ],
        )
        self.assertEqual(rc, 1)
        self.assertIn("requiere especificar una --url asociada", err)

    def test_anotar_url_invalida_o_con_espacios_se_rechaza(self) -> None:
        """Evita inyectar esquemas no soportados o URLs mal formadas."""
        id_tarea, _ = self._crear_tarea("Tarea url", sufijo="url")

        for url_invalida in (
            "ftp://servidor.com/recurso",
            "http://sitio .com/espacio",
            "https://sitio.com/linea\ncontrol",
            "solo-texto",
        ):
            with self.subTest(url=url_invalida):
                rc, _, err = self._callado(
                    cli.main,
                    [
                        "--proyecto",
                        str(self.raiz),
                        "tarea",
                        "anotar",
                        id_tarea,
                        "--url",
                        url_invalida,
                    ],
                )
                self.assertEqual(rc, 1)


class TestAdjuntar(TareasContextoTestCase):
    """Pruebas del comando `oracle tarea adjuntar`."""

    def test_adjuntar_copia_exacta_y_preserva_original(self) -> None:
        """Evita mover, alterar o eliminar el archivo de origen durante el adjuntado."""
        id_tarea, ruta_md = self._crear_tarea("Tarea adjunto", sufijo="adj")
        origen = self.raiz / "captura.log"
        contenido_bin = b"Log de prueba con bytes exactos \x00\x01\x02"
        origen.write_bytes(contenido_bin)

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "adjuntar", id_tarea, str(origen), "--json"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        destino = Path(datos["ruta"])

        # El original debe permanecer intacto
        self.assertTrue(origen.exists())
        self.assertEqual(origen.read_bytes(), contenido_bin)

        # El destino debe tener los mismos bytes
        self.assertTrue(destino.exists())
        self.assertEqual(destino.read_bytes(), contenido_bin)

        # TAREA.md debe registrar el enlace
        contenido_md = ruta_md.read_text(encoding="utf-8")
        self.assertIn("- Adjunto: [captura.log](captura.log)", contenido_md)

    def test_adjuntar_con_espacios_y_caracteres_unicode(self) -> None:
        """Evita corromper nombres con espacios, caracteres Unicode y símbolos especiales en Markdown."""
        id_tarea, ruta_md = self._crear_tarea("Tarea unicode", sufijo="uni")
        nombre_complejo = "captura (análisis) #1 [versión final].log"
        origen = self.raiz / nombre_complejo
        origen.write_text("contenido de prueba", encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "adjuntar", id_tarea, str(origen)],
        )
        self.assertEqual(rc, 0, err)

        carpeta_tarea = ruta_md.parent
        destino = carpeta_tarea / nombre_complejo
        self.assertTrue(destino.exists())

        # El enlace debe estar escapado adecuadamente en la URL y en la etiqueta Markdown
        contenido_md = ruta_md.read_text(encoding="utf-8")
        self.assertIn("captura%20%28an%C3%A1lisis%29%20%231%20%5Bversi%C3%B3n%20final%5D.log", contenido_md)
        self.assertIn(r"\[versión final\]", contenido_md)

    def test_adjuntar_escapa_barras_invertidas_antes_que_corchetes(self) -> None:
        """Evita que el escape de corchetes se corrompa si el nombre contiene barras invertidas."""
        id_tarea, ruta_md = self._crear_tarea("Tarea escape barras", sufijo="barras")
        nombre_con_barra = "nota\\[test\\].txt"
        origen = self.raiz / nombre_con_barra
        origen.write_text("texto con barras", encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "adjuntar", id_tarea, str(origen)],
        )
        self.assertEqual(rc, 0, err)
        contenido_md = ruta_md.read_text(encoding="utf-8")
        # La barra literal necesita dos escapes y el corchete requiere su propio escape.
        self.assertIn(r"nota\\\[test\\\]", contenido_md)

    def test_adjuntar_rechaza_nombre_con_saltos_de_linea(self) -> None:
        """Evita inyectar líneas en TAREA.md mediante nombres de archivo partidos con \n."""
        id_tarea, _ = self._crear_tarea("Tarea salto", sufijo="salto")
        origen = self.raiz / "valido.txt"
        origen.write_text("prueba", encoding="utf-8")

        # Intentar pasar nombre con salto de línea vía argumento
        rc, _, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "adjuntar", id_tarea, "archivo\npartido.txt"],
        )
        self.assertEqual(rc, 1)

    def test_adjuntar_rechaza_enlace_simbolico_de_origen(self) -> None:
        """Evita adjuntar mediante symlinks que puedan inducir lecturas o copias inseguras."""
        id_tarea, _ = self._crear_tarea("Tarea symlink", sufijo="sym")
        real = self.raiz / "real.txt"
        real.write_text("datos reales", encoding="utf-8")
        enlace = self.raiz / "link.txt"
        enlace.symlink_to(real)

        rc, _, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "adjuntar", id_tarea, str(enlace)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("no puede ser un enlace simbólico", err)

    def test_adjuntar_rechaza_colision_con_archivo_existente(self) -> None:
        """Evita sobrescribir adjuntos preexistentes con el mismo nombre."""
        id_tarea, ruta_md = self._crear_tarea("Tarea colision", sufijo="col")
        archivo_previo = ruta_md.parent / "datos.csv"
        archivo_previo.write_text("primera version", encoding="utf-8")

        nuevo = self.raiz / "datos.csv"
        nuevo.write_text("segunda version", encoding="utf-8")

        rc, _, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "adjuntar", id_tarea, str(nuevo)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ya existe en la tarea", err)
        self.assertEqual(archivo_previo.read_text(encoding="utf-8"), "primera version")

    def test_adjuntar_rechaza_nombre_tarea_md(self) -> None:
        """Evita destruir o reemplazar el archivo central TAREA.md mediante un adjunto."""
        id_tarea, _ = self._crear_tarea("Tarea central", sufijo="cen")
        falso_tarea = self.raiz / "TAREA.md"
        falso_tarea.write_text("# Intento de sobreescritura", encoding="utf-8")

        rc, _, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "adjuntar", id_tarea, str(falso_tarea)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("nombre reservado TAREA.md", err)

    def test_adjuntar_limite_20mib_sin_bandera_y_permite_con_ella(self) -> None:
        """Evita saturar el repositorio con archivos grandes sin confirmación explícita."""
        id_tarea, ruta_md = self._crear_tarea("Tarea tamano", sufijo="tam")
        grande = self.raiz / "archivo_grande.bin"
        with open(grande, "wb") as f:
            f.seek(21 * 1024 * 1024 - 1)
            f.write(b"\x00")

        rc, _, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "adjuntar", id_tarea, str(grande)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("supera el límite de 20 MiB", err)

        rc_ok, _, err_ok = self._callado(
            cli.main,
            [
                "--proyecto",
                str(self.raiz),
                "tarea",
                "adjuntar",
                id_tarea,
                str(grande),
                "--permitir-grande",
            ],
        )
        self.assertEqual(rc_ok, 0, err_ok)
        destino = ruta_md.parent / "archivo_grande.bin"
        self.assertTrue(destino.exists())


class TestBuscar(TareasContextoTestCase):
    """Pruebas del comando `oracle tarea buscar`."""

    def test_buscar_encuentra_coincidencias_en_subcarpetas_de_la_tarea(self) -> None:
        """Evita restringir la búsqueda a un solo nivel de adjuntos dentro de la tarea."""
        id1, ruta1 = self._crear_tarea("Tarea con arbol", sufijo="arbol")
        sub = ruta1.parent / "evidencia" / "logs"
        sub.mkdir(parents=True)
        (sub / "arnes.txt").write_text("Fallo por timeout en arnés", encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "buscar", "timeout", "--json"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        rutas = [c["ruta"] for c in datos["coincidencias"]]
        self.assertTrue(any("arnes.txt" in r for r in rutas))

    def test_buscar_omite_fifo_sin_bloquearse(self) -> None:
        """Evita bloquear el proceso ante archivos especiales o tuberías nombradas (FIFOs)."""
        if not hasattr(os, "mkfifo"):
            self.skipTest("mkfifo no soportado en esta plataforma")

        id1, ruta1 = self._crear_tarea("Tarea con fifo", sufijo="fifo")
        fifo = ruta1.parent / "pipe.txt"
        try:
            os.mkfifo(fifo)
        except OSError:
            self.skipTest("No se pudo crear FIFO en este sistema de archivos")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "buscar", "algo", "--json"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        self.assertTrue(any("pipe.txt" in o["ruta"] and "especial" in o["motivo"] for o in datos["omitidos"]))

    def test_buscar_omite_binarios_con_diagnostico_en_json(self) -> None:
        """Evita leer o intentar parsear archivos binarios como texto."""
        id1, ruta1 = self._crear_tarea("Tarea con imagen", sufijo="img")
        binario = ruta1.parent / "captura.png"
        binario.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "buscar", "algo", "--json"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        omitidos = datos["omitidos"]
        self.assertTrue(any("captura.png" in o["ruta"] and "binario" in o["motivo"] for o in omitidos))

    def test_buscar_humano_muestra_omitidos_con_cero_coincidencias(self) -> None:
        """Evita esconder omisiones o alcance parcial en la salida de consola cuando no hay resultados."""
        id1, ruta1 = self._crear_tarea("Tarea con omision", sufijo="omi")
        (ruta1.parent / "foto.jpg").write_bytes(b"\xff\xd8\xff\xe0")

        rc, out, _ = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "buscar", "inexistente"],
        )
        self.assertEqual(rc, 0)
        self.assertIn("No se encontraron coincidencias", out)
        self.assertIn("Archivos omitidos:", out)
        self.assertIn("foto.jpg", out)

    def test_buscar_falla_si_hay_registros_invalidos(self) -> None:
        """Evita disfrazar carpetas corruptas como si fueran búsquedas vacías exitosas."""
        carpeta_invalida = self.raiz / "tareas" / "carpeta_con_nombre_invalido"
        carpeta_invalida.mkdir()

        rc, _, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "buscar", "cualquiera"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("registro(s) inválido(s)", err)


class TestReferencias(TareasContextoTestCase):
    """Pruebas del comando `oracle tarea referencias`."""

    def test_referencias_encuentra_menciones_en_codigo_del_proyecto(self) -> None:
        """Evita que el rastreo de contexto pierda referencias válidas en el código fuente."""
        id_tarea, _ = self._crear_tarea("Bug de sincronizacion", sufijo="sinc")

        codigo_dir = self.raiz / "src"
        codigo_dir.mkdir(parents=True, exist_ok=True)
        archivo_py = codigo_dir / "sensor.py"
        archivo_py.write_text(
            f"# Solución implementada para la tarea {id_tarea}\ndef resolver(): pass\n",
            encoding="utf-8",
        )

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "referencias", id_tarea, "--json"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        self.assertEqual(datos["id"], id_tarea)
        self.assertEqual(datos["tipo"], "mencion_textual")

        coincidencias = datos["coincidencias"]
        self.assertTrue(any("sensor.py" in c["ruta"] and id_tarea in c["texto"] for c in coincidencias))

    def test_referencias_falla_si_hay_registros_invalidos(self) -> None:
        """Evita devolver éxito en referencias si el tracker contiene registros corruptos."""
        id_tarea, _ = self._crear_tarea("Tarea ok", sufijo="ok")
        carpeta_rota = self.raiz / "tareas" / "20260912-100000-rota"
        carpeta_rota.mkdir()
        (carpeta_rota / "TAREA.md").write_text("invalido", encoding="utf-8")

        rc, _, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "referencias", id_tarea],
        )
        self.assertEqual(rc, 1)
        self.assertIn("registro(s) inválido(s)", err)

    def test_referencias_no_confunde_id_con_sufijos(self) -> None:
        """Evita atribuir menciones de tareas derivadas (ej. ID-1) a la tarea base."""
        id_base, _ = self._crear_tarea("Tarea base", sufijo="base")
        id_derivada = f"{id_base}-1"

        archivo = self.raiz / "referencias.md"
        archivo.write_text(f"Mención de {id_derivada} solamente", encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "referencias", id_base, "--json"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        self.assertFalse(any("referencias.md" in c["ruta"] for c in datos["coincidencias"]))

    def test_referencias_ignora_directorios_excluidos(self) -> None:
        """Evita recorrer .git, node_modules o entornos virtuales."""
        id_tarea, _ = self._crear_tarea("Tarea ignorar", sufijo="ign")

        git_log = self.raiz / ".git" / "dummy.log"
        git_log.write_text(f"Commit para {id_tarea}", encoding="utf-8")

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "referencias", id_tarea, "--json"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        self.assertFalse(any(".git" in c["ruta"] for c in datos["coincidencias"]))


class TestResumen(TareasContextoTestCase):
    """Pruebas del comando `oracle tarea resumen`."""

    def test_resumen_calcula_totales_estados_y_conserva_mayusculas_de_etiquetas(self) -> None:
        """Evita convertir etiquetas a minúsculas o perder su identidad exacta."""
        id1, _ = self._crear_tarea("Tarea 1", etiquetas=["Bug", "Urgente", "Bug"])
        id2, _ = self._crear_tarea("Tarea 2", etiquetas=["bug", "Docs"])
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "cerrar", id2])

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "resumen", "--json"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        self.assertEqual(datos["total"], 2)
        self.assertEqual(datos["estados"]["ABIERTA"], 1)
        self.assertEqual(datos["estados"]["CERRADA"], 1)

        # Conserva el casing original: 'Bug' y 'bug' no se colapsan a minúsculas
        self.assertEqual(datos["etiquetas"]["Bug"], 1)
        self.assertEqual(datos["etiquetas"]["bug"], 1)
        self.assertEqual(datos["etiquetas"]["Docs"], 1)
        self.assertEqual(datos["etiquetas"]["Urgente"], 1)

    def test_resumen_vacio_devuelve_cero(self) -> None:
        """Evita fallos cuando el tracker está recién inicializado y sin tareas."""
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "resumen", "--json"],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        self.assertEqual(datos["total"], 0)
        self.assertEqual(datos["estados"]["ABIERTA"], 0)
        self.assertEqual(datos["estados"]["CERRADA"], 0)
        self.assertEqual(datos["etiquetas"], {})

    def test_resumen_falla_si_hay_registros_invalidos(self) -> None:
        """Evita emitir estadísticas engañosas cuando hay registros rotos en tareas/."""
        invalida = self.raiz / "tareas" / "20260912-110000-rota"
        invalida.mkdir()
        (invalida / "TAREA.md").write_text("Archivo invalido sin metadatos", encoding="utf-8")

        rc, _, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "resumen"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("registro(s) inválido(s)", err)


class TestComportamientoGlobalP2(TareasContextoTestCase):
    """Pruebas de ayuda sin escrituras y rechazo de opciones desconocidas en verbos P2."""

    def test_ayudas_de_cada_verbo_no_escriben(self) -> None:
        """Evita que consultar --help en cualquiera de los nuevos verbos cree carpetas o archivos."""
        raiz_vacia = Path(tempfile.mkdtemp()).resolve()
        try:
            for verbo in ("anotar", "adjuntar", "buscar", "referencias", "resumen"):
                with self.subTest(verbo=verbo):
                    rc, out, _ = self._callado(cli.main, ["tarea", verbo, "--help"])
                    self.assertEqual(rc, 0)
                    self.assertIn(f"oracle tarea {verbo}", out)
                    self.assertFalse((raiz_vacia / "tareas").exists())
        finally:
            shutil.rmtree(raiz_vacia, ignore_errors=True)

    def test_opciones_desconocidas_devuelven_codigo_2(self) -> None:
        """Evita ignorar banderas inválidas aportando los argumentos posicionales requeridos."""
        id_tarea, _ = self._crear_tarea("Tarea opciones", sufijo="opc")
        archivo_dummy = self.raiz / "adj.txt"
        archivo_dummy.write_text("prueba", encoding="utf-8")

        casos = [
            ("anotar", [id_tarea, "texto"]),
            ("adjuntar", [id_tarea, str(archivo_dummy)]),
            ("buscar", ["termino"]),
            ("referencias", [id_tarea]),
            ("resumen", []),
        ]

        for verbo, posicionales in casos:
            with self.subTest(verbo=verbo):
                rc, _, err = self._callado(
                    cli.main,
                    ["--proyecto", str(self.raiz), "tarea", verbo, *posicionales, "--opcion-inventada"],
                )
                self.assertEqual(rc, 2)
                self.assertIn("argumentos no reconocidos", err.lower())
