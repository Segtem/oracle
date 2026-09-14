"""Tests de cobertura de errores y códigos de retorno para el subsistema de tareas P1.

Cubre sobrevivientes de mutación en comandos P1 (tools/tareas.py líneas 470 en adelante):
- Exigencia de código exacto 1 ante raíz no válida en cmd_init, cmd_nueva, cmd_listar,
  cmd_ver, cmd_cerrar, cmd_reabrir y cmd_revisar.
- Rechazo estricto con código 1 ante directorios tareas/ o archivos README.md que sean enlaces simbólicos.
- Validación de título y etiquetas en cmd_nueva (título vacío, espacios, saltos de línea LF y CR).
- Errores de E/S en mkdir, open, read_bytes, write_text y fallo atómico de creación de carpetas.
- Errores en cmd_ver ante identificadores inexistentes, carpetas sin TAREA.md, symlinks que escapan,
  archivos no UTF-8 y documentos mal formados.
- Errores en cmd_cerrar y cmd_reabrir ante ID ausente, TAREA.md ausente, symlinks y fallos de actualización.
- Casos positivos clave: idempotencia de cmd_init ante README preexistente, filtrado de tareas
  cerradas con --cerradas y emisión exacta de ruta con cmd_ver --ruta.
- Despacho y punto de entrada main: banderas y verbos de ayuda (código 0), verbos desconocidos
  (código 1), delegación a seguimiento y hechos, traducción de TareaError y OSError en comandos P2,
  y comportamiento con sys.argv por defecto frente a argv explícito.
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from tools import tareas
from tools.tareas import (
    RutaInsegura,
    TareaError,
    TareaInvalida,
    TrackerNoEncontrado,
)


class ErroresBaseTestCase(unittest.TestCase):
    """Caso base con sandbox temporal aislado y capturador de flujos estándar."""

    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="oracle-p1-err-")
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name).resolve()
        (self.raiz / ".git").mkdir()

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
        estado: str = "ABIERTA",
        prioridad: int = 50,
        etiquetas: str = "test",
        sufijo: str = "prueba",
        cuerpo: str = "Cuerpo de prueba\n",
    ) -> tuple[str, Path]:
        raiz_tareas = self.raiz / "tareas"
        raiz_tareas.mkdir(parents=True, exist_ok=True)
        carpeta = raiz_tareas / f"20260913-100000-{sufijo}"
        carpeta.mkdir(parents=True, exist_ok=True)
        tarea_md = carpeta / "TAREA.md"
        contenido = (
            f"# {titulo}\n\n"
            f"- ESTADO: {estado}\n"
            f"- PRIORIDAD: {prioridad}\n"
            f"- ETIQUETAS: {etiquetas}\n\n"
            f"{cuerpo}"
        )
        tarea_md.write_text(contenido, encoding="utf-8")
        return carpeta.name, tarea_md


class TestErroresRaizYDirectorio(ErroresBaseTestCase):
    """Verifica que la resolución inválida de raíz y directorios no permitidos devuelva código exacto 1."""

    def test_cmd_init_raiz_invalida_retorna_1_exacto(self) -> None:
        """Evita que un fallo al resolver la raíz al inicializar devuelva código distinto de 1."""
        archivo_invalido = self.raiz / "archivo_falso"
        archivo_invalido.write_text("no soy un directorio")
        rc, out, err = self._callado(
            tareas.cmd_init,
            ["init", "--proyecto", str(archivo_invalido)],
            ["--proyecto", str(archivo_invalido)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)

    def test_cmd_init_directorio_tareas_enlace_simbolico_retorna_1_exacto(self) -> None:
        """Evita que inicializar sobre un directorio tareas/ que es enlace simbólico devuelva código distinto de 1."""
        otro_dir = self.raiz / "otro_destino"
        otro_dir.mkdir()
        (self.raiz / "tareas").symlink_to(otro_dir)
        rc, out, err = self._callado(
            tareas.cmd_init,
            ["init", "--proyecto", str(self.raiz)],
            ["--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("es un enlace simbólico; no se permite inicializarlo.", err)

    def test_cmd_init_readme_enlace_simbolico_retorna_1_exacto(self) -> None:
        """Evita que inicializar sobre un README.md que es enlace simbólico devuelva código distinto de 1."""
        (self.raiz / "tareas").mkdir()
        archivo_meta = self.raiz / "meta.md"
        archivo_meta.write_text("externo")
        (self.raiz / "tareas" / "README.md").symlink_to(archivo_meta)
        rc, out, err = self._callado(
            tareas.cmd_init,
            ["init", "--proyecto", str(self.raiz)],
            ["--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("es un enlace simbólico; no se permite inicializar a través de enlaces.", err)

    def test_cmd_nueva_raiz_invalida_retorna_1_exacto(self) -> None:
        """Evita que cmd_nueva ante raíz no resuelta devuelva código distinto de 1."""
        dir_sin_tracker = self.raiz / "vacio"
        dir_sin_tracker.mkdir()
        rc, out, err = self._callado(
            tareas.cmd_nueva,
            ["nueva", "--proyecto", str(dir_sin_tracker), "Nueva tarea"],
            ["--proyecto", str(dir_sin_tracker), "Nueva tarea"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)

    def test_cmd_nueva_directorio_tareas_enlace_simbolico_retorna_1_exacto(self) -> None:
        """Evita que cmd_nueva permita escribir cuando tareas/ es enlace simbólico o devuelva código distinto de 1."""
        otro_dir = self.raiz / "otro_destino"
        otro_dir.mkdir()
        (self.raiz / "tareas").symlink_to(otro_dir)
        rc, out, err = self._callado(
            tareas.cmd_nueva,
            ["nueva", "--proyecto", str(self.raiz), "Nueva tarea"],
            ["--proyecto", str(self.raiz), "Nueva tarea"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("es un enlace simbólico; escrituras no permitidas.", err)

    def test_cmd_listar_raiz_invalida_retorna_1_exacto(self) -> None:
        """Evita que cmd_listar ante raíz no resuelta devuelva código distinto de 1."""
        dir_sin_tracker = self.raiz / "vacio"
        dir_sin_tracker.mkdir()
        rc, out, err = self._callado(
            tareas.cmd_listar,
            ["listar", "--proyecto", str(dir_sin_tracker)],
            ["--proyecto", str(dir_sin_tracker)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)

    def test_cmd_ver_raiz_invalida_retorna_1_exacto(self) -> None:
        """Evita que cmd_ver ante raíz no resuelta devuelva código distinto de 1."""
        dir_sin_tracker = self.raiz / "vacio"
        dir_sin_tracker.mkdir()
        rc, out, err = self._callado(
            tareas.cmd_ver,
            ["ver", "20260913-100000-dummy", "--proyecto", str(dir_sin_tracker)],
            ["20260913-100000-dummy", "--proyecto", str(dir_sin_tracker)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)

    def test_cmd_cerrar_raiz_invalida_retorna_1_exacto(self) -> None:
        """Evita que cmd_cerrar ante raíz no resuelta devuelva código distinto de 1."""
        dir_sin_tracker = self.raiz / "vacio"
        dir_sin_tracker.mkdir()
        rc, out, err = self._callado(
            tareas.cmd_cerrar,
            ["cerrar", "20260913-100000-dummy", "--proyecto", str(dir_sin_tracker)],
            ["20260913-100000-dummy", "--proyecto", str(dir_sin_tracker)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)

    def test_cmd_reabrir_raiz_invalida_retorna_1_exacto(self) -> None:
        """Evita que cmd_reabrir ante raíz no resuelta devuelva código distinto de 1."""
        dir_sin_tracker = self.raiz / "vacio"
        dir_sin_tracker.mkdir()
        rc, out, err = self._callado(
            tareas.cmd_reabrir,
            ["reabrir", "20260913-100000-dummy", "--proyecto", str(dir_sin_tracker)],
            ["20260913-100000-dummy", "--proyecto", str(dir_sin_tracker)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)

    def test_cmd_revisar_raiz_invalida_retorna_1_exacto(self) -> None:
        """Evita que cmd_revisar ante raíz no resuelta devuelva código distinto de 1."""
        dir_sin_tracker = self.raiz / "vacio"
        dir_sin_tracker.mkdir()
        rc, out, err = self._callado(
            tareas.cmd_revisar,
            ["revisar", "--proyecto", str(dir_sin_tracker)],
            ["--proyecto", str(dir_sin_tracker)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)


class TestErroresEntradaNueva(ErroresBaseTestCase):
    """Verifica la validación de títulos y etiquetas en cmd_nueva."""

    def test_cmd_nueva_titulo_vacio_retorna_1_exacto(self) -> None:
        """Evita que un título vacío devuelva código distinto de 1."""
        rc, out, err = self._callado(
            tareas.cmd_nueva,
            ["nueva", "--proyecto", str(self.raiz), ""],
            ["--proyecto", str(self.raiz), ""],
        )
        self.assertEqual(rc, 1)
        self.assertIn("el título de la tarea no puede estar vacío", err)

    def test_cmd_nueva_titulo_solo_espacios_retorna_1_exacto(self) -> None:
        """Evita que un título compuesto exclusivamente por espacios devuelva código distinto de 1."""
        rc, out, err = self._callado(
            tareas.cmd_nueva,
            ["nueva", "--proyecto", str(self.raiz), "   \t  "],
            ["--proyecto", str(self.raiz), "   \t  "],
        )
        self.assertEqual(rc, 1)
        self.assertIn("el título de la tarea no puede estar vacío", err)

    def test_cmd_nueva_titulo_con_salto_de_linea_lf_retorna_1_exacto(self) -> None:
        """Evita que un título con salto de línea '\\n' sea aceptado o devuelva código distinto de 1."""
        rc, out, err = self._callado(
            tareas.cmd_nueva,
            ["nueva", "--proyecto", str(self.raiz), "Título con\nsalto"],
            ["--proyecto", str(self.raiz), "Título con\nsalto"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("el título no puede contener saltos de línea", err)

    def test_cmd_nueva_titulo_con_retorno_carro_cr_retorna_1_exacto(self) -> None:
        """Evita que un título con retorno de carro '\\r' sea aceptado o devuelva código distinto de 1."""
        rc, out, err = self._callado(
            tareas.cmd_nueva,
            ["nueva", "--proyecto", str(self.raiz), "Título con\rretorno"],
            ["--proyecto", str(self.raiz), "Título con\rretorno"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("el título no puede contener saltos de línea", err)

    def test_cmd_nueva_etiqueta_con_salto_de_linea_lf_retorna_1_exacto(self) -> None:
        """Evita que una etiqueta con '\\n' sea aceptada o devuelva código distinto de 1."""
        rc, out, err = self._callado(
            tareas.cmd_nueva,
            ["nueva", "--proyecto", str(self.raiz), "-e", "tag\ninvalida", "Título"],
            ["--proyecto", str(self.raiz), "-e", "tag\ninvalida", "Título"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("las etiquetas no pueden contener saltos de línea", err)

    def test_cmd_nueva_etiqueta_con_retorno_carro_cr_retorna_1_exacto(self) -> None:
        """Evita que una etiqueta con '\\r' sea aceptada o devuelva código distinto de 1."""
        rc, out, err = self._callado(
            tareas.cmd_nueva,
            ["nueva", "--proyecto", str(self.raiz), "-e", "tag\rinvalida", "Título"],
            ["--proyecto", str(self.raiz), "-e", "tag\rinvalida", "Título"],
        )
        self.assertEqual(rc, 1)
        self.assertIn("las etiquetas no pueden contener saltos de línea", err)


class TestErroresIOYArchivo(ErroresBaseTestCase):
    """Verifica el manejo de fallos de E/S y corrupción de archivos en subcomandos P1."""

    def test_cmd_init_error_mkdir_retorna_1_exacto(self) -> None:
        """Evita que fallos de E/S al crear tareas/ propaguen excepción o devuelvan código distinto de 1."""
        with mock.patch.object(Path, "mkdir", side_effect=OSError("Permiso denegado al crear directorio")):
            rc, out, err = self._callado(
                tareas.cmd_init,
                ["init", "--proyecto", str(self.raiz)],
                ["--proyecto", str(self.raiz)],
            )
        self.assertEqual(rc, 1)
        self.assertIn("no se pudo crear el directorio", err)

    def test_cmd_init_error_open_readme_retorna_1_exacto(self) -> None:
        """Evita que fallos de E/S al crear README.md devuelvan código distinto de 1."""
        with mock.patch("os.open", side_effect=OSError("Error al abrir README")):
            rc, out, err = self._callado(
                tareas.cmd_init,
                ["init", "--proyecto", str(self.raiz)],
                ["--proyecto", str(self.raiz)],
            )
        self.assertEqual(rc, 1)
        self.assertIn("no se pudo crear", err)

    def test_cmd_nueva_error_crear_carpeta_atomica_retorna_1_exacto(self) -> None:
        """Evita que fallos de E/S al crear la carpeta de la tarea devuelvan código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        with mock.patch("tools.tareas.crear_carpeta_tarea_atomica", side_effect=OSError("Fallo en creacion de carpeta")):
            rc, out, err = self._callado(
                tareas.cmd_nueva,
                ["nueva", "--proyecto", str(self.raiz), "Mi Tarea"],
                ["--proyecto", str(self.raiz), "Mi Tarea"],
            )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR: Fallo en creacion de carpeta", err)

    def test_cmd_nueva_error_write_text_retorna_1_exacto(self) -> None:
        """Evita que fallos de E/S al escribir TAREA.md devuelvan código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        with mock.patch.object(Path, "write_text", side_effect=OSError("Fallo en disco")):
            rc, out, err = self._callado(
                tareas.cmd_nueva,
                ["nueva", "--proyecto", str(self.raiz), "Mi Tarea"],
                ["--proyecto", str(self.raiz), "Mi Tarea"],
            )
        self.assertEqual(rc, 1)
        self.assertIn("no se pudo escribir", err)

    def test_cmd_ver_banderas_incompatibles_ruta_y_json_retorna_1_exacto(self) -> None:
        """Evita que combinar --ruta y --json en cmd_ver sea aceptado o devuelva código distinto de 1."""
        rc, out, err = self._callado(
            tareas.cmd_ver,
            ["ver", "id-tarea", "--ruta", "--json", "--proyecto", str(self.raiz)],
            ["id-tarea", "--ruta", "--json", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("las opciones --ruta y --json son incompatibles", err)

    def test_cmd_ver_id_inexistente_retorna_1_exacto(self) -> None:
        """Evita que cmd_ver ante un ID no encontrado devuelva código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        rc, out, err = self._callado(
            tareas.cmd_ver,
            ["ver", "20260913-000000-inexistente", "--proyecto", str(self.raiz)],
            ["20260913-000000-inexistente", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("no se encontró ninguna tarea", err)

    def test_cmd_ver_carpeta_sin_tarea_md_retorna_1_exacto(self) -> None:
        """Evita que cmd_ver ante carpeta sin TAREA.md devuelva código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        (self.raiz / "tareas" / "20260913-100000-sinmd").mkdir()
        rc, out, err = self._callado(
            tareas.cmd_ver,
            ["ver", "20260913-100000-sinmd", "--proyecto", str(self.raiz)],
            ["20260913-100000-sinmd", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("no contiene TAREA.md", err)

    def test_cmd_ver_tarea_md_enlace_que_escapa_retorna_1_exacto(self) -> None:
        """Evita que cmd_ver permita leer enlaces simbólicos que apuntan fuera de tareas/."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        carpeta = self.raiz / "tareas" / "20260913-100000-escape"
        carpeta.mkdir()
        externo = self.raiz / "externo.md"
        externo.write_text("# Externo\n- ESTADO: ABIERTA\n- PRIORIDAD: 1\n", encoding="utf-8")
        (carpeta / "TAREA.md").symlink_to(externo)
        rc, out, err = self._callado(
            tareas.cmd_ver,
            ["ver", "20260913-100000-escape", "--proyecto", str(self.raiz)],
            ["20260913-100000-escape", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)

    def test_cmd_ver_error_read_bytes_retorna_1_exacto(self) -> None:
        """Evita que un fallo de lectura de bytes en TAREA.md devuelva código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        id_t, _ = self._crear_tarea(sufijo="readerr")
        with mock.patch.object(Path, "read_bytes", side_effect=OSError("Error E/S")):
            rc, out, err = self._callado(
                tareas.cmd_ver,
                ["ver", id_t, "--proyecto", str(self.raiz)],
                [id_t, "--proyecto", str(self.raiz)],
            )
        self.assertEqual(rc, 1)
        self.assertIn("no se pudo leer", err)

    def test_cmd_ver_tarea_md_no_utf8_retorna_1_exacto(self) -> None:
        """Evita que TAREA.md con codificación no UTF-8 devuelva código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        carpeta = self.raiz / "tareas" / "20260913-100000-badutf"
        carpeta.mkdir()
        (carpeta / "TAREA.md").write_bytes(b"\xff\xfe\x00\x12")
        rc, out, err = self._callado(
            tareas.cmd_ver,
            ["ver", "20260913-100000-badutf", "--proyecto", str(self.raiz)],
            ["20260913-100000-badutf", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("codificación UTF-8 inválida en TAREA.md", err)

    def test_cmd_ver_tarea_invalida_retorna_1_exacto(self) -> None:
        """Evita que TAREA.md con metadatos inválidos o mal formados devuelva código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        carpeta = self.raiz / "tareas" / "20260913-100000-malformada"
        carpeta.mkdir()
        (carpeta / "TAREA.md").write_text("# Solo Titulo\n\nSin bloque de metadatos\n", encoding="utf-8")
        rc, out, err = self._callado(
            tareas.cmd_ver,
            ["ver", "20260913-100000-malformada", "--proyecto", str(self.raiz)],
            ["20260913-100000-malformada", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)


class TestErroresActualizarEstado(ErroresBaseTestCase):
    """Verifica el manejo de errores en cmd_cerrar y cmd_reabrir."""

    def test_cmd_cerrar_id_inexistente_retorna_1_exacto(self) -> None:
        """Evita que cmd_cerrar ante un ID inexistente devuelva código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        rc, out, err = self._callado(
            tareas.cmd_cerrar,
            ["cerrar", "20260913-000000-inexistente", "--proyecto", str(self.raiz)],
            ["20260913-000000-inexistente", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("no se encontró ninguna tarea", err)

    def test_cmd_cerrar_carpeta_sin_tarea_md_retorna_1_exacto(self) -> None:
        """Evita que cmd_cerrar ante una carpeta sin TAREA.md devuelva código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        (self.raiz / "tareas" / "20260913-100000-sinmd").mkdir()
        rc, out, err = self._callado(
            tareas.cmd_cerrar,
            ["cerrar", "20260913-100000-sinmd", "--proyecto", str(self.raiz)],
            ["20260913-100000-sinmd", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("no contiene TAREA.md", err)

    def test_cmd_cerrar_tarea_md_enlace_que_escapa_retorna_1_exacto(self) -> None:
        """Evita que cmd_cerrar permita modificar enlaces simbólicos que escapan de tareas/."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        carpeta = self.raiz / "tareas" / "20260913-100000-escape"
        carpeta.mkdir()
        externo = self.raiz / "externo.md"
        externo.write_text("# Ext\n- ESTADO: ABIERTA\n- PRIORIDAD: 10\n", encoding="utf-8")
        (carpeta / "TAREA.md").symlink_to(externo)
        rc, out, err = self._callado(
            tareas.cmd_cerrar,
            ["cerrar", "20260913-100000-escape", "--proyecto", str(self.raiz)],
            ["20260913-100000-escape", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)

    def test_cmd_cerrar_fallos_actualizar_estado_tarea_retorna_1_exacto(self) -> None:
        """Evita que errores de validación o E/S en actualizar_estado_tarea al cerrar devuelvan código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        id_t, _ = self._crear_tarea(sufijo="cerrarerr")
        with mock.patch("tools.tareas.actualizar_estado_tarea", side_effect=TareaInvalida("documento corrupto")):
            rc, out, err = self._callado(
                tareas.cmd_cerrar,
                ["cerrar", id_t, "--proyecto", str(self.raiz)],
                [id_t, "--proyecto", str(self.raiz)],
            )
        self.assertEqual(rc, 1)
        self.assertIn("documento corrupto", err)

        with mock.patch("tools.tareas.actualizar_estado_tarea", side_effect=OSError("fallo de escritura atomica")):
            rc, out, err = self._callado(
                tareas.cmd_cerrar,
                ["cerrar", id_t, "--proyecto", str(self.raiz)],
                [id_t, "--proyecto", str(self.raiz)],
            )
        self.assertEqual(rc, 1)
        self.assertIn("fallo de escritura atomica", err)

    def test_cmd_reabrir_id_inexistente_retorna_1_exacto(self) -> None:
        """Evita que cmd_reabrir ante un ID inexistente devuelva código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        rc, out, err = self._callado(
            tareas.cmd_reabrir,
            ["reabrir", "20260913-000000-inexistente", "--proyecto", str(self.raiz)],
            ["20260913-000000-inexistente", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("no se encontró ninguna tarea", err)

    def test_cmd_reabrir_carpeta_sin_tarea_md_retorna_1_exacto(self) -> None:
        """Evita que cmd_reabrir ante una carpeta sin TAREA.md devuelva código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        (self.raiz / "tareas" / "20260913-100000-sinmd").mkdir()
        rc, out, err = self._callado(
            tareas.cmd_reabrir,
            ["reabrir", "20260913-100000-sinmd", "--proyecto", str(self.raiz)],
            ["20260913-100000-sinmd", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("no contiene TAREA.md", err)

    def test_cmd_reabrir_tarea_md_enlace_que_escapa_retorna_1_exacto(self) -> None:
        """Evita que cmd_reabrir permita modificar enlaces simbólicos que escapan de tareas/."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        carpeta = self.raiz / "tareas" / "20260913-100000-escape"
        carpeta.mkdir()
        externo = self.raiz / "externo.md"
        externo.write_text("# Ext\n- ESTADO: CERRADA\n- PRIORIDAD: 10\n", encoding="utf-8")
        (carpeta / "TAREA.md").symlink_to(externo)
        rc, out, err = self._callado(
            tareas.cmd_reabrir,
            ["reabrir", "20260913-100000-escape", "--proyecto", str(self.raiz)],
            ["20260913-100000-escape", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("ERROR:", err)

    def test_cmd_reabrir_fallos_actualizar_estado_tarea_retorna_1_exacto(self) -> None:
        """Evita que errores de validación o E/S en actualizar_estado_tarea al reabrir devuelvan código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        id_t, _ = self._crear_tarea(sufijo="reabrirerr", estado="CERRADA")
        with mock.patch("tools.tareas.actualizar_estado_tarea", side_effect=TareaInvalida("formato corrupto")):
            rc, out, err = self._callado(
                tareas.cmd_reabrir,
                ["reabrir", id_t, "--proyecto", str(self.raiz)],
                [id_t, "--proyecto", str(self.raiz)],
            )
        self.assertEqual(rc, 1)
        self.assertIn("formato corrupto", err)

        with mock.patch("tools.tareas.actualizar_estado_tarea", side_effect=OSError("fallo de E/S")):
            rc, out, err = self._callado(
                tareas.cmd_reabrir,
                ["reabrir", id_t, "--proyecto", str(self.raiz)],
                [id_t, "--proyecto", str(self.raiz)],
            )
        self.assertEqual(rc, 1)
        self.assertIn("fallo de E/S", err)


class TestCasosPositivosComandos(ErroresBaseTestCase):
    """Verifica flujos positivos clave para descartar mutantes booleanos y de constantes en retornos exitosos."""

    def test_cmd_init_idempotente_segunda_vez_devuelve_0_exacto(self) -> None:
        """Evita que reinicializar un tracker existente falle cuando README.md ya existe."""
        rc1, out1, err1 = self._callado(
            tareas.cmd_init,
            ["init", "--proyecto", str(self.raiz)],
            ["--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc1, 0, err1)
        self.assertIn("Tracker de tareas inicializado", out1)

        # Segunda invocación idempotente
        rc2, out2, err2 = self._callado(
            tareas.cmd_init,
            ["init", "--proyecto", str(self.raiz)],
            ["--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc2, 0, err2)
        self.assertIn("Tracker de tareas inicializado", out2)

    def test_cmd_listar_filtro_cerradas_positivo_devuelve_0_exacto(self) -> None:
        """Evita que el listado con --cerradas omita filtrar abiertas o devuelva código distinto de 0."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        id_abierta, _ = self._crear_tarea(titulo="Tarea Abierta", estado="ABIERTA", sufijo="abierta")
        id_cerrada, _ = self._crear_tarea(titulo="Tarea Cerrada", estado="CERRADA", sufijo="cerrada")

        # Modo humano
        rc, out, err = self._callado(
            tareas.cmd_listar,
            ["listar", "--cerradas", "--proyecto", str(self.raiz)],
            ["--cerradas", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 0, err)
        self.assertIn(id_cerrada, out)
        self.assertNotIn(id_abierta, out)

        # Modo JSON
        rc_json, out_json, err_json = self._callado(
            tareas.cmd_listar,
            ["listar", "--cerradas", "--json", "--proyecto", str(self.raiz)],
            ["--cerradas", "--json", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc_json, 0, err_json)
        datos = json.loads(out_json)
        self.assertEqual(len(datos), 1)
        self.assertEqual(datos[0]["id"], id_cerrada)
        self.assertEqual(datos[0]["estado"], "CERRADA")

    def test_cmd_ver_opcion_ruta_devuelve_0_exacto(self) -> None:
        """Evita que la opción --ruta en cmd_ver devuelva código distinto de 0 o emita líneas espurias."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        id_t, ruta_t = self._crear_tarea(titulo="Ver Ruta", sufijo="verruta")
        rc, out, err = self._callado(
            tareas.cmd_ver,
            ["ver", id_t, "--ruta", "--proyecto", str(self.raiz)],
            [id_t, "--ruta", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 0, err)
        self.assertEqual(out.strip(), str(ruta_t.resolve()))


class TestErroresRevisar(ErroresBaseTestCase):
    """Verifica los códigos de salida y salidas estructuradas de cmd_revisar."""

    def test_cmd_revisar_fallos_modo_humano_retorna_1_exacto(self) -> None:
        """Evita que una auditoría con problemas en formato humano devuelva código distinto de 1."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        (self.raiz / "tareas" / "archivo_no_permitido.txt").write_text("invalido")
        rc, out, err = self._callado(
            tareas.cmd_revisar,
            ["revisar", "--proyecto", str(self.raiz)],
            ["--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        self.assertIn("REVISIÓN FALLIDA", err)

    def test_cmd_revisar_fallos_modo_json_retorna_1_exacto(self) -> None:
        """Evita que una auditoría con problemas en formato JSON devuelva 0 o emita ok=true."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        (self.raiz / "tareas" / "archivo_no_permitido.txt").write_text("invalido")
        rc, out, err = self._callado(
            tareas.cmd_revisar,
            ["revisar", "--json", "--proyecto", str(self.raiz)],
            ["--json", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 1)
        datos = json.loads(out)
        self.assertFalse(datos["ok"])
        self.assertGreater(len(datos["problemas"]), 0)

    def test_cmd_revisar_sin_problemas_humano_y_json_retornan_0_exacto(self) -> None:
        """Evita que una auditoría sin problemas falle o devuelva código distinto de 0."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        self._crear_tarea(titulo="Valida", sufijo="valida")

        # Humano
        rc, out, err = self._callado(
            tareas.cmd_revisar,
            ["revisar", "--proyecto", str(self.raiz)],
            ["--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 0, err)
        self.assertIn("REVISIÓN OK", out)

        # JSON
        rc_json, out_json, err_json = self._callado(
            tareas.cmd_revisar,
            ["revisar", "--json", "--proyecto", str(self.raiz)],
            ["--json", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc_json, 0, err_json)
        datos = json.loads(out_json)
        self.assertTrue(datos["ok"])
        self.assertEqual(len(datos["problemas"]), 0)
        self.assertEqual(datos["tareas_validas"], 1)


class TestDespachoYMain(ErroresBaseTestCase):
    """Verifica el despacho central, delegación, traducción de errores y punto de entrada main."""

    def test_despachar_ayuda_vacia_y_flags_devuelven_0_exacto(self) -> None:
        """Evita que pedir ayuda en despachar devuelva un código distinto de 0."""
        for flag in ("", "-h", "--help", "help"):
            rc, out, err = self._callado(tareas.despachar, flag, [], [flag] if flag else [])
            self.assertEqual(rc, 0)
            self.assertIn("Oracle — metalenguaje de medidas: tracker de tareas.", out)

    def test_despachar_verbo_desconocido_devuelve_1_exacto(self) -> None:
        """Evita que un verbo desconocido devuelva un código distinto de 1."""
        rc, out, err = self._callado(tareas.despachar, "inexistente", [], ["inexistente"])
        self.assertEqual(rc, 1)
        self.assertIn("verbo desconocido para «tarea»: inexistente", err)

    def test_despachar_comandos_p2_captura_y_traduce_tarea_error_a_1_exacto(self) -> None:
        """Evita que excepciones TareaError en comandos P2 escapen sin traducción o devuelvan código distinto de 1."""
        verbos_p2 = ("anotar", "adjuntar", "buscar", "referencias", "resumen")
        for verbo in verbos_p2:
            with mock.patch(f"tools.tareas_contexto.cmd_{verbo}", side_effect=TareaError(f"error tarea en {verbo}")):
                rc, out, err = self._callado(
                    tareas.despachar,
                    verbo,
                    ["--proyecto", str(self.raiz)],
                    [verbo, "--proyecto", str(self.raiz)],
                )
                self.assertEqual(rc, 1, f"Fallo en verbo {verbo}")
                self.assertIn(f"ERROR: error tarea en {verbo}", err)

    def test_despachar_comandos_p2_captura_y_traduce_oserror_a_1_exacto(self) -> None:
        """Evita que excepciones OSError en comandos P2 escapen sin traducción o devuelvan código distinto de 1."""
        verbos_p2 = ("anotar", "adjuntar", "buscar", "referencias", "resumen")
        for verbo in verbos_p2:
            with mock.patch(f"tools.tareas_contexto.cmd_{verbo}", side_effect=OSError(f"error io en {verbo}")):
                rc, out, err = self._callado(
                    tareas.despachar,
                    verbo,
                    ["--proyecto", str(self.raiz)],
                    [verbo, "--proyecto", str(self.raiz)],
                )
                self.assertEqual(rc, 1, f"Fallo en verbo {verbo}")
                self.assertIn(f"ERROR: error io en {verbo}", err)

    def test_despachar_seguimiento_y_hechos_delega_correctamente(self) -> None:
        """Evita que despachar altere los argumentos o código de salida al delegar a seguimiento y hechos."""
        with mock.patch("tools.tareas_git.cmd_seguimiento", return_value=42) as m_seg:
            rc, out, err = self._callado(
                tareas.despachar, "seguimiento", ["--proyecto", str(self.raiz)], ["seguimiento", "--proyecto", str(self.raiz)]
            )
            self.assertEqual(rc, 42)
            m_seg.assert_called_once_with(["seguimiento", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])

        with mock.patch("tools.tareas_hechos.cmd_hechos", return_value=43) as m_hech:
            rc, out, err = self._callado(
                tareas.despachar, "hechos", ["--proyecto", str(self.raiz)], ["hechos", "--proyecto", str(self.raiz)]
            )
            self.assertEqual(rc, 43)
            m_hech.assert_called_once_with(["hechos", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])

    def test_main_ayuda_vacio_y_flags_devuelven_0_exacto(self) -> None:
        """Evita que invocar main sin argumentos o con flags de ayuda devuelva código distinto de 0."""
        for inv in ([], ["-h"], ["--help"], ["help"]):
            rc, out, err = self._callado(tareas.main, inv)
            self.assertEqual(rc, 0)
            self.assertIn("Oracle — metalenguaje de medidas: tracker de tareas.", out)

    def test_main_con_sys_argv_por_defecto(self) -> None:
        """Evita que main con argv=None falle al consumir sys.argv[1:] o propague errores indebidos."""
        with mock.patch.object(sys, "argv", ["oracle-tarea"]):
            rc, out, err = self._callado(tareas.main)
            self.assertEqual(rc, 0)
            self.assertIn("Oracle — metalenguaje de medidas: tracker de tareas.", out)

        with mock.patch.object(sys, "argv", ["oracle-tarea", "-h"]):
            rc, out, err = self._callado(tareas.main)
            self.assertEqual(rc, 0)
            self.assertIn("Oracle — metalenguaje de medidas: tracker de tareas.", out)

        with mock.patch.object(sys, "argv", ["oracle-tarea", "init", "--proyecto", str(self.raiz)]):
            rc, out, err = self._callado(tareas.main)
            self.assertEqual(rc, 0, err)

        with mock.patch.object(sys, "argv", ["oracle-tarea", "verbo_inexistente"]):
            rc, out, err = self._callado(tareas.main)
            self.assertEqual(rc, 1)
            self.assertIn("verbo desconocido para «tarea»: verbo_inexistente", err)

    def test_main_con_argv_explicito_pasa_verbo_y_argumentos(self) -> None:
        """Evita que main con lista explícita altere el verbo o descarte argumentos hacia despachar."""
        self._callado(tareas.cmd_init, ["init", "--proyecto", str(self.raiz)], ["--proyecto", str(self.raiz)])
        id_t, ruta_t = self._crear_tarea(titulo="Main Tarea", sufijo="maintarea")
        rc, out, err = self._callado(
            tareas.main,
            ["ver", id_t, "--ruta", "--proyecto", str(self.raiz)],
        )
        self.assertEqual(rc, 0, err)
        self.assertEqual(out.strip(), str(ruta_t.resolve()))


if __name__ == "__main__":
    unittest.main()
