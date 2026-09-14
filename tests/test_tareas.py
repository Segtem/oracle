"""Tests de conducta para el subsistema de tareas (P0 y P1).

Cada test documenta explícitamente el fallo que evita en su docstring.
"""
from __future__ import annotations

import datetime
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools import cli, tareas


class TareasTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.raiz = Path(self.td.name).resolve()
        # Simular repositorio git
        (self.raiz / ".git").mkdir()

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


class TestDescubrimientoYContrato(TareasTestCase):
    """Pruebas de descubrimiento de raíz, límites Git y contrato mínimo (P0)."""

    def test_init_crea_directorio_tareas_y_readme(self) -> None:
        """Evita que un proyecto intente operar sin el andamio inicial o que una reinicialización
        destruya el README existente."""
        rc, out, err = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        self.assertEqual(rc, 0, err)
        self.assertTrue((self.raiz / "tareas").is_dir())
        readme = self.raiz / "tareas" / "README.md"
        self.assertTrue(readme.is_file())
        contenido_previo = readme.read_text(encoding="utf-8")

        # Idempotencia: correr init nuevamente no rompe ni borra
        rc2, _, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        self.assertEqual(rc2, 0)
        self.assertEqual(readme.read_text(encoding="utf-8"), contenido_previo)

    def test_init_no_requiere_catalogos_ni_oracle_json(self) -> None:
        """Evita acoplar el tracker al catálogo de medidas, permitiendo usar tareas en proyectos
        que no declaran medidas ni configuran Oracle."""
        # self.raiz no tiene catalogos/ ni oracle.json
        self.assertFalse((self.raiz / "catalogos").exists())
        self.assertFalse((self.raiz / "oracle.json").exists())
        rc, out, err = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        self.assertEqual(rc, 0, err)
        self.assertIn("inicializado", out)

    def test_descubrimiento_desde_subcarpeta_encuentra_la_raiz(self) -> None:
        """Evita obligar al usuario a situarse en la raíz del repositorio para usar el tracker."""
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        sub = self.raiz / "src" / "modulo" / "componente"
        sub.mkdir(parents=True)
        old_cwd = os.getcwd()
        try:
            os.chdir(sub)
            raiz_hallada = tareas.resolver_raiz_tracker()
            self.assertEqual(raiz_hallada, self.raiz)
        finally:
            os.chdir(old_cwd)

    def test_descubrimiento_se_detiene_en_limite_git_y_no_salta_a_otro_repo(self) -> None:
        """Evita que un repositorio anidado (como un submódulo o checkout secundario) contamine
        el tracker del repositorio padre."""
        # Repositorio padre con tareas/
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])

        # Subdirectorio que es a su vez un repositorio git independiente sin tareas/
        sub_repo = self.raiz / "dependencia_submodulo"
        sub_repo.mkdir()
        (sub_repo / ".git").mkdir()

        sub_dir = sub_repo / "src"
        sub_dir.mkdir()

        old_cwd = os.getcwd()
        try:
            os.chdir(sub_dir)
            with self.assertRaises(tareas.TrackerNoEncontrado):
                tareas.resolver_raiz_tracker()
        finally:
            os.chdir(old_cwd)

    def test_precedencia_proyecto_sobre_entorno_y_busqueda(self) -> None:
        """Evita que variables de entorno desactualizadas o la carpeta de trabajo alteren
        la ruta indicada explícitamente con --proyecto."""
        otro_dir = self.raiz / "otro"
        otro_dir.mkdir()
        (otro_dir / "tareas").mkdir()

        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])

        # ORACLE_PROYECTO apunta a self.raiz, pero --proyecto pide otro_dir
        os.environ["ORACLE_PROYECTO"] = str(self.raiz)
        try:
            res = tareas.resolver_raiz_tracker(["--proyecto", str(otro_dir)])
            self.assertEqual(res, otro_dir.resolve())
        finally:
            os.environ.pop("ORACLE_PROYECTO", None)


class TestCreacionYColisiones(TareasTestCase):
    """Pruebas de creación de tareas e identidad estable (P0 y P1)."""

    def setUp(self) -> None:
        super().setUp()
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])

    def test_nueva_crea_estructura_y_archivo_con_formato(self) -> None:
        """Evita generar tareas con metadatos incompletos, permisos incorrectos o campos faltantes."""
        rc, out, err = self._callado(
            cli.main,
            [
                "--proyecto",
                str(self.raiz),
                "tarea",
                "nueva",
                "Defecto en sensor",
                "--etiqueta",
                "bug,urgente",
                "--prioridad",
                "80",
            ],
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("Tarea creada:", out)

        carpetas = [d for d in (self.raiz / "tareas").iterdir() if d.is_dir()]
        self.assertEqual(len(carpetas), 1)
        tarea_md = carpetas[0] / "TAREA.md"
        self.assertTrue(tarea_md.is_file())

        texto = tarea_md.read_text(encoding="utf-8")
        self.assertIn("# Defecto en sensor", texto)
        self.assertIn("- ESTADO: ABIERTA", texto)
        self.assertIn("- PRIORIDAD: 80", texto)
        self.assertIn("- ETIQUETAS: bug, urgente", texto)

    def test_colision_de_ids_en_el_mismo_segundo_resuelve_con_sufijo_secuencial(self) -> None:
        """Evita la sobrescritura silenciosa de tareas o bloqueos cuando se crean múltiples tareas
        en el mismo segundo con idéntico prefijo temporal."""
        raiz_tareas = self.raiz / "tareas"
        fecha_fija = datetime.datetime(2026, 9, 11, 18, 0, 0, tzinfo=datetime.timezone.utc)

        id1, _ = tareas.crear_carpeta_tarea_atomica(raiz_tareas, "sensor", fecha_utc=fecha_fija)

        id2, _ = tareas.crear_carpeta_tarea_atomica(raiz_tareas, "sensor", fecha_utc=fecha_fija)

        id3, _ = tareas.crear_carpeta_tarea_atomica(raiz_tareas, "sensor", fecha_utc=fecha_fija)

        self.assertEqual(id1, "20260911-180000-sensor")
        self.assertEqual(id2, "20260911-180000-sensor-1")
        self.assertEqual(id3, "20260911-180000-sensor-2")

    def test_nueva_salida_json_contiene_id_y_ruta(self) -> None:
        """Evita que scripts y herramientas no puedan integrar la creación de tareas programáticamente."""
        rc, out, err = self._callado(
            cli.main,
            [
                "--proyecto",
                str(self.raiz),
                "tarea",
                "nueva",
                "Automatizada",
                "--json",
            ],
        )
        self.assertEqual(rc, 0, err)
        datos = json.loads(out)
        self.assertIn("id", datos)
        self.assertIn("ruta", datos)
        self.assertTrue(Path(datos["ruta"]).is_file())


class TestMetadatosYPreservacion(TareasTestCase):
    """Pruebas de validación estricta y preservación del cuerpo al modificar estado."""

    def setUp(self) -> None:
        super().setUp()
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])

    def test_preservacion_del_cuerpo_y_campos_desconocidos_al_cerrar_y_reabrir(self) -> None:
        """Evita que cambiar el estado destruya notas manuales, imágenes adjuntas o campos
        personalizados en TAREA.md."""
        carpeta = self.raiz / "tareas" / "20260911-180000-investigar"
        carpeta.mkdir()
        tarea_md = carpeta / "TAREA.md"

        contenido_inicial = (
            "# Investigar sensor de prueba\n\n"
            "- ESTADO: ABIERTA\n"
            "- PRIORIDAD: 70\n"
            "- ETIQUETAS: sensor, test\n"
            "- ASIGNADO: brian\n"
            "- MODULO: nucleo/sensor\n\n"
            "## Descripción detallada\n\n"
            "Apuntes del autor con listas:\n"
            "- Punto 1\n"
            "- Punto 2 con `- ESTADO: ABIERTA` dentro de una nota\n\n"
            "```python\n"
            "# Código que no debe tocarse\n"
            "def test():\n"
            "    return '- ESTADO: ABIERTA'\n"
            "```\n"
        )
        tarea_md.write_text(contenido_inicial, encoding="utf-8")

        # Cerrar tarea
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "cerrar", "20260911-180000-investigar"],
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("Tarea cerrada", out)

        texto_cerrado = tarea_md.read_text(encoding="utf-8")
        self.assertIn("- ESTADO: CERRADA", texto_cerrado)
        self.assertIn("- ASIGNADO: brian", texto_cerrado)
        self.assertIn("- MODULO: nucleo/sensor", texto_cerrado)
        self.assertIn("Punto 2 con `- ESTADO: ABIERTA` dentro de una nota", texto_cerrado)
        self.assertIn("def test():", texto_cerrado)

        # Reabrir tarea
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "reabrir", "20260911-180000-investigar"],
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("Tarea reabierta", out)

        texto_reabierto = tarea_md.read_text(encoding="utf-8")
        self.assertIn("- ESTADO: ABIERTA", texto_reabierto)
        self.assertIn("- ASIGNADO: brian", texto_reabierto)
        self.assertIn("Punto 2 con `- ESTADO: ABIERTA` dentro de una nota", texto_reabierto)

    def test_idempotencia_al_cerrar_o_reabrir(self) -> None:
        """Evita que reintentar cerrar una tarea ya cerrada o reabrir una ya abierta falle con error."""
        carpeta = self.raiz / "tareas" / "20260911-180000-idemp"
        carpeta.mkdir()
        (carpeta / "TAREA.md").write_text(
            "# Idempotente\n\n- ESTADO: CERRADA\n- PRIORIDAD: 50\n- ETIQUETAS: \n",
            encoding="utf-8",
        )
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "cerrar", "20260911-180000-idemp"],
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("ya estaba cerrada", out)

    def test_metadatos_duplicados_se_rechazan(self) -> None:
        """Evita la ambigüedad generada por campos repetidos en el bloque de metadatos."""
        carpeta = self.raiz / "tareas" / "20260911-180000-duplicado"
        carpeta.mkdir()
        (carpeta / "TAREA.md").write_text(
            "# Duplicado\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n- ESTADO: CERRADA\n",
            encoding="utf-8",
        )
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "revisar"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("campo duplicado en metadatos", err)

    def test_estado_invalido_se_rechaza(self) -> None:
        """Evita que estados arbitrarios (e.g. 'EN_PROGRESO') invaliden los listados y la historia."""
        carpeta = self.raiz / "tareas" / "20260911-180000-invalido"
        carpeta.mkdir()
        (carpeta / "TAREA.md").write_text(
            "# Estado raro\n\n- ESTADO: PENDIENTE\n- PRIORIDAD: 50\n",
            encoding="utf-8",
        )
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "revisar"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("estado inválido", err)

    def test_prioridad_no_entera_se_rechaza(self) -> None:
        """Evita caídas por excepción al ordenar tareas cuando la prioridad contiene texto en vez de número."""
        carpeta = self.raiz / "tareas" / "20260911-180000-prio-mala"
        carpeta.mkdir()
        (carpeta / "TAREA.md").write_text(
            "# Prio mala\n\n- ESTADO: ABIERTA\n- PRIORIDAD: alta\n",
            encoding="utf-8",
        )
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "revisar"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("prioridad inválida", err)


class TestSeguridadYConfinamiento(TareasTestCase):
    """Pruebas de contención de rutas y prevención de path traversal (P0 y P1)."""

    def setUp(self) -> None:
        super().setUp()
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])

    def test_id_con_caracteres_de_escape_se_rechaza(self) -> None:
        """Evita ataques de navegación por directorios con `..` o barras en el ID de tarea."""
        for intento in ("../otro", "foo/bar", "..", "\\escape", "foo\x00bar"):
            with self.subTest(intento=intento):
                rc, _, err = self._callado(
                    cli.main,
                    ["--proyecto", str(self.raiz), "tarea", "ver", intento],
                )
                self.assertEqual(rc, 1)
                self.assertIn("ERROR:", err)

    def test_symlink_hacia_afuera_de_tareas_se_rechaza(self) -> None:
        """Evita acceder a directorios ajenos al tracker siguiendo enlaces simbólicos."""
        externo = self.raiz.parent / "externo_secreto"
        externo.mkdir(exist_ok=True)
        (externo / "TAREA.md").write_text(
            "# Secreto\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 10\n",
            encoding="utf-8",
        )
        symlink = self.raiz / "tareas" / "link_externo"
        symlink.symlink_to(externo, target_is_directory=True)

        rc, _, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "ver", "link_externo"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("escapa del directorio de tareas", err)


class TestListarVerYRevisar(TareasTestCase):
    """Pruebas de consultas, filtros, desambiguación y revisión de integridad."""

    def setUp(self) -> None:
        super().setUp()
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])

    def test_desambiguacion_de_prefijos_en_ver(self) -> None:
        """Evita consultar o modificar una tarea errónea cuando un prefijo corto coincide con varias."""
        _, out1, _ = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "nueva", "Sensor A", "--sufijo", "sen-a", "--json"],
        )
        _, out2, _ = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "nueva", "Sensor B", "--sufijo", "sen-b", "--json"],
        )
        id1 = json.loads(out1)["id"]
        id2 = json.loads(out2)["id"]

        # Prefijo ambiguo compartido (marca temporal inicial YYYYMMDD)
        prefijo_ambiguo = id1[:8]
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "ver", prefijo_ambiguo],
        )
        self.assertNotEqual(rc, 0)
        self.assertIn("es ambiguo", err)

        # Prefijo unívoco
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "ver", id1],
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("Sensor A", out)

    def test_ver_con_bandera_ruta_imprime_solo_ruta_absoluta(self) -> None:
        """Evita romper la integración con editores ($EDITOR $(oracle tarea ver ID --ruta))."""
        _, out_nueva, _ = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "nueva", "Edicion", "--sufijo", "edicion", "--json"],
        )
        id_creado = json.loads(out_nueva)["id"]
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "ver", id_creado, "--ruta"],
        )
        self.assertEqual(rc, 0, err)
        ruta_salida = Path(out.strip())
        self.assertTrue(ruta_salida.is_file())
        self.assertEqual(ruta_salida.name, "TAREA.md")

    def test_listar_ordena_por_prioridad_descendente_y_desempata_por_id(self) -> None:
        """Evita listados desordenados donde las tareas urgentes queden ocultas al final."""
        raiz_tareas = self.raiz / "tareas"
        fecha_a = datetime.datetime(2026, 9, 11, 10, 0, 0, tzinfo=datetime.timezone.utc)
        fecha_b = datetime.datetime(2026, 9, 11, 11, 0, 0, tzinfo=datetime.timezone.utc)
        fecha_c = datetime.datetime(2026, 9, 11, 12, 0, 0, tzinfo=datetime.timezone.utc)

        id1, _ = tareas.crear_carpeta_tarea_atomica(raiz_tareas, "media-1", fecha_utc=fecha_a)
        (raiz_tareas / id1 / "TAREA.md").write_text(
            "# Media 1\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n- ETIQUETAS:\n", encoding="utf-8"
        )

        id2, _ = tareas.crear_carpeta_tarea_atomica(raiz_tareas, "alta", fecha_utc=fecha_b)
        (raiz_tareas / id2 / "TAREA.md").write_text(
            "# Alta\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 100\n- ETIQUETAS:\n", encoding="utf-8"
        )

        id3, _ = tareas.crear_carpeta_tarea_atomica(raiz_tareas, "media-2", fecha_utc=fecha_c)
        (raiz_tareas / id3 / "TAREA.md").write_text(
            "# Media 2\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n- ETIQUETAS:\n", encoding="utf-8"
        )

        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "listar", "--json"],
        )
        self.assertEqual(rc, 0, err)
        items = json.loads(out)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["id"], id2)  # Prioridad 100
        self.assertEqual(items[1]["id"], id1)  # Prioridad 50 (id más chico)
        self.assertEqual(items[2]["id"], id3)  # Prioridad 50 (id más grande)

    def test_listar_vacio_es_exito_pero_datos_invalidos_salen_con_error(self) -> None:
        """Evita disfrazar errores de lectura o corrupción de datos bajo la apariencia de una lista vacía."""
        # 1. Consulta sin coincidencias -> salida 0
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "listar", "--etiqueta", "inexistente"],
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("No hay tareas", out)

        # 2. Carpeta de tarea rota en tareas/
        rota = self.raiz / "tareas" / "20260911-180000-rota"
        rota.mkdir()
        # Sin TAREA.md
        rc2, out2, err2 = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "listar"],
        )
        self.assertEqual(rc2, 1)
        self.assertIn("sin TAREA.md", err2)

    def test_revisar_audita_integridad_completa_y_tolera_readme(self) -> None:
        """Evita falsas alarmas con README.md o .gitignore en tareas/ pero atrapa carpetas mal formadas."""
        # Un tracker limpio pasa revisión
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "revisar"],
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("REVISIÓN OK", out)

        # Carpeta mal formada
        (self.raiz / "tareas" / "carpeta_sin_tarea").mkdir()
        rc2, out2, err2 = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "revisar"],
        )
        self.assertEqual(rc2, 1)
        self.assertIn("REVISIÓN FALLIDA", err2)

    def test_alias_ls_es_equivalente_a_listar(self) -> None:
        """Evita divergencias entre el comando canónico 'listar' y el alias habitual 'ls'."""
        self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "nueva", "Para LS", "--sufijo", "pls"],
        )
        rc1, out1, _ = self._callado(
            cli.main, ["--proyecto", str(self.raiz), "tarea", "listar"]
        )
        rc2, out2, _ = self._callado(
            cli.main, ["--proyecto", str(self.raiz), "tarea", "ls"]
        )
        self.assertEqual(rc1, 0)
        self.assertEqual(rc2, 0)
        self.assertEqual(out1, out2)


if __name__ == "__main__":
    unittest.main()
