"""Tests de mutación y comportamiento fino para el subsistema de tareas P1.

Cubre casos de borde y sobrevivientes del diagnóstico de mutación en:
- Resolución de raíz (flags explícitos, variables de entorno, permisos de creación)
- Parseo de TAREA.md (espacios iniciales, longitudes mínimas, campos adicionales, etiquetas)
- Preservación atómica de contenido, orden de metadatos y saltos CRLF
- Generación determinista y desambiguación secuencial de carpetas de tareas (-1, -2)
- Resolución de identificadores directos y prefijos inequívocos
- Validación estricta de seguridad en identificadores y confinamiento
- Códigos de salida del CLI (código 2 ante errores de argumentos, código 1 ante errores de dominio)
- Filtros, combinaciones y salidas humanas y JSON en listar, ver, cerrar, reabrir y revisar
"""
from __future__ import annotations

import datetime
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from tools import cli, tareas


class MutacionBaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporal = tempfile.TemporaryDirectory(prefix="oracle-p1-mut-")
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


class TestMutacionResolucionRaiz(MutacionBaseTestCase):
    """Pruebas para resolver_raiz_tracker sobre flags, variables de entorno y precedencia."""

    def test_resolver_raiz_con_ruta_explicita_permitir_crear_en_directorio_sin_tareas(self) -> None:
        """Evita que resolver_raiz_tracker rechace una ruta explícita al inicializar cuando tareas/ aún no existe."""
        destino = self.raiz / "nuevo_proyecto"
        destino.mkdir()
        # Con permitir_crear=True debe aceptar el directorio sin tareas/
        res = tareas.resolver_raiz_tracker(ruta_explicita=destino, permitir_crear=True)
        self.assertEqual(res, destino.resolve())

        # Con permitir_crear=False debe fallar informando que no tiene tareas/
        with self.assertRaises(tareas.TrackerNoEncontrado):
            tareas.resolver_raiz_tracker(ruta_explicita=destino, permitir_crear=False)

    def test_resolver_raiz_con_argv_proyecto_sin_valor_al_final(self) -> None:
        """Evita IndexError o comportamiento errático si --proyecto se pasa como último argumento en argv."""
        with self.assertRaises(tareas.TareaError) as ctx:
            tareas.resolver_raiz_tracker(["--proyecto"])
        self.assertIn("falta la ruta: --proyecto <ruta>", str(ctx.exception))

    def test_resolver_raiz_con_argv_proyecto_seguido_de_otra_bandera(self) -> None:
        """Evita que una bandera subsiguiente se tome erróneamente como ruta del proyecto."""
        with self.assertRaises(tareas.TareaError) as ctx:
            tareas.resolver_raiz_tracker(["--proyecto", "--otra-bandera"])
        self.assertIn("falta la ruta: --proyecto <ruta>", str(ctx.exception))

    def test_resolver_raiz_con_variable_entorno_permitir_crear_y_sin_tareas(self) -> None:
        """Evita que $ORACLE_PROYECTO falle al inicializar si tareas/ aún no existe y permitir_crear=True."""
        destino = self.raiz / "env_proyecto"
        destino.mkdir()
        old_env = os.environ.get("ORACLE_PROYECTO")
        os.environ["ORACLE_PROYECTO"] = str(destino)
        try:
            res = tareas.resolver_raiz_tracker(permitir_crear=True)
            self.assertEqual(res, destino.resolve())
            with self.assertRaises(tareas.TrackerNoEncontrado):
                tareas.resolver_raiz_tracker(permitir_crear=False)
        finally:
            if old_env is not None:
                os.environ["ORACLE_PROYECTO"] = old_env
            else:
                os.environ.pop("ORACLE_PROYECTO", None)

    def test_resolver_raiz_con_variable_entorno_apunta_a_archivo(self) -> None:
        """Evita que un archivo ordinario configurado en $ORACLE_PROYECTO se acepte como raíz de proyecto."""
        archivo = self.raiz / "un_archivo.txt"
        archivo.write_text("contenido", encoding="utf-8")
        old_env = os.environ.get("ORACLE_PROYECTO")
        os.environ["ORACLE_PROYECTO"] = str(archivo)
        try:
            with self.assertRaises(tareas.TrackerNoEncontrado):
                tareas.resolver_raiz_tracker(permitir_crear=True)
        finally:
            if old_env is not None:
                os.environ["ORACLE_PROYECTO"] = old_env
            else:
                os.environ.pop("ORACLE_PROYECTO", None)


class TestMutacionParseoTarea(MutacionBaseTestCase):
    """Pruebas de límites de sintaxis y metadatos en parsear_tarea."""

    def test_parsear_tarea_lineas_en_blanco_al_inicio(self) -> None:
        """Evita que líneas en blanco iniciales antes del título H1 causen rechazo indebido del documento."""
        texto = "\n\n  \n# Tarea con espacio inicial\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 40\n\nCuerpo.\n"
        ruta = self.raiz / "tareas" / "20260913-110000-demo" / "TAREA.md"
        t = tareas.parsear_tarea(texto, ruta)
        self.assertEqual(t.titulo, "Tarea con espacio inicial")
        self.assertEqual(t.prioridad, 40)
        self.assertEqual(t.cuerpo, "Cuerpo.")

    def test_parsear_tarea_titulo_un_solo_caracter_valido_y_rechazo_espacio_vacio(self) -> None:
        """Evita que títulos válidos de 1 carácter sean rechazados o que '# ' sin título sea admitido."""
        ruta = self.raiz / "tareas" / "20260913-110000-demo" / "TAREA.md"
        # 1 carácter válido tras '# '
        t1 = tareas.parsear_tarea("# X\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n", ruta)
        self.assertEqual(t1.titulo, "X")

        # Almohadilla seguida de espacios vacíos debe fallar
        with self.assertRaises(tareas.TareaInvalida):
            tareas.parsear_tarea("#   \n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n", ruta)

        # Almohadilla sin espacio separador debe fallar
        with self.assertRaises(tareas.TareaInvalida):
            tareas.parsear_tarea("#TituloSinEspacio\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n", ruta)

    def test_parsear_tarea_campos_adicionales_se_guardan_y_estandar_se_excluyen(self) -> None:
        """Evita que metadatos personalizados se omitan o que campos estándar se dupliquen en adicionales."""
        texto = (
            "# Defecto sensor\n\n"
            "- ESTADO: ABIERTA\n"
            "- PRIORIDAD: 90\n"
            "- ETIQUETAS: core, red\n"
            "- ASIGNADO: dev1\n"
            "- MODULO: sensor_arnes\n\n"
            "Descripción técnica.\n"
        )
        ruta = self.raiz / "tareas" / "20260913-110000-demo" / "TAREA.md"
        t = tareas.parsear_tarea(texto, ruta)
        self.assertEqual(t.campos_adicionales, {"ASIGNADO": "dev1", "MODULO": "sensor_arnes"})
        self.assertNotIn("ESTADO", t.campos_adicionales)
        self.assertNotIn("PRIORIDAD", t.campos_adicionales)
        self.assertNotIn("ETIQUETAS", t.campos_adicionales)
        self.assertEqual(t.etiquetas, ("core", "red"))

    def test_parsear_tarea_etiquetas_espacios_y_elementos_vacios(self) -> None:
        """Evita que comas repetidas o espacios residuales contaminen la tupla de etiquetas de la tarea."""
        texto = (
            "# Tarea limpia\n\n"
            "- ESTADO: ABIERTA\n"
            "- PRIORIDAD: 50\n"
            "- ETIQUETAS: bug, , sensor ,  , urgente\n"
        )
        ruta = self.raiz / "tareas" / "20260913-110000-demo" / "TAREA.md"
        t = tareas.parsear_tarea(texto, ruta)
        self.assertEqual(t.etiquetas, ("bug", "sensor", "urgente"))


class TestMutacionActualizacionAtomaYCrlf(MutacionBaseTestCase):
    """Pruebas de preservación atómica de bytes, CRLF y retorno booleano estricto."""

    def test_actualizar_estado_idempotente_retorna_false_estricto(self) -> None:
        """Evita que actualizar_estado_tarea retorne None o valores ambiguos ante un estado ya fijado."""
        carpeta = self.raiz / "tareas" / "20260913-110000-demo"
        carpeta.mkdir(parents=True)
        tarea_md = carpeta / "TAREA.md"
        tarea_md.write_text("# Tarea\n\n- ESTADO: CERRADA\n- PRIORIDAD: 50\n", encoding="utf-8")

        cambio = tareas.actualizar_estado_tarea(tarea_md, "CERRADA")
        self.assertIs(cambio, False)

    def test_actualizar_estado_preserva_crlf_orden_metadata_y_espaciado(self) -> None:
        """Evita que la actualización de estado corrompa saltos CRLF o trastoque metadatos previos a ESTADO."""
        carpeta = self.raiz / "tareas" / "20260913-110000-demo"
        carpeta.mkdir(parents=True)
        tarea_md = carpeta / "TAREA.md"

        contenido_original = (
            b"\r\n"
            b"# Titulo Tarea\r\n"
            b"\r\n"
            b"- PRIORIDAD: 100\r\n"
            b"- ASIGNADO: juan\r\n"
            b"- ESTADO: ABIERTA\r\n"
            b"- ETIQUETAS: arnes\r\n"
            b"\r\n"
            b"Cuerpo con texto\r\n"
            b"```python\r\n"
            b"- ESTADO: ABIERTA\r\n"
            b"```\r\n"
        )
        tarea_md.write_bytes(contenido_original)

        cambio = tareas.actualizar_estado_tarea(tarea_md, "CERRADA")
        self.assertIs(cambio, True)

        contenido_despues = tarea_md.read_bytes()
        self.assertIn(b"\r\n", contenido_despues)
        esperado = contenido_original.replace(b"- ESTADO: ABIERTA\r\n", b"- ESTADO: CERRADA\r\n", 1)
        self.assertEqual(contenido_despues, esperado)


class TestMutacionCreacionYColisiones(MutacionBaseTestCase):
    """Pruebas de creación de carpetas de tareas y desambiguación determinista sin generar_id_tarea."""

    def test_crear_carpeta_atomica_desambiguador_secuencial_exacto(self) -> None:
        """Evita que colisiones temporales salten números o comiencen desambiguadores en 2 en vez de 1."""
        raiz_tareas = self.raiz / "tareas"
        raiz_tareas.mkdir(parents=True)
        fecha_fija = datetime.datetime(2026, 9, 13, 10, 0, 0, tzinfo=datetime.timezone.utc)

        # Primer intento: nombre base
        id0, c0 = tareas.crear_carpeta_tarea_atomica(raiz_tareas, "sinc", fecha_utc=fecha_fija)
        self.assertEqual(id0, "20260913-100000-sinc")
        self.assertTrue(c0.is_dir())

        # Primera colisión: debe agregar -1 exactamente
        id1, c1 = tareas.crear_carpeta_tarea_atomica(raiz_tareas, "sinc", fecha_utc=fecha_fija)
        self.assertEqual(id1, "20260913-100000-sinc-1")
        self.assertTrue(c1.is_dir())

        # Segunda colisión: debe avanzar a -2 exactamente
        id2, c2 = tareas.crear_carpeta_tarea_atomica(raiz_tareas, "sinc", fecha_utc=fecha_fija)
        self.assertEqual(id2, "20260913-100000-sinc-2")
        self.assertTrue(c2.is_dir())

    def test_sanear_slug_translitera_acentos_sin_insertar_guiones_espurios(self) -> None:
        """Evita que el filtrado de combining characters se desactive rompiendo palabras con acentos."""
        slug_esp = tareas._sanear_slug("Desincronización de eventos")
        self.assertEqual(slug_esp, "desincronizacion-de-eventos")

        slug_enie = tareas._sanear_slug("Año y Señal")
        self.assertEqual(slug_enie, "ano-y-senal")


class TestMutacionResolucionIdYConfinamiento(MutacionBaseTestCase):
    """Pruebas de resolución inequívoca de prefijos y confinamiento sin depender del retorno Path."""

    def test_resolver_id_carpeta_directa_y_prefijo_inequivoco(self) -> None:
        """Evita que resolver_id_o_prefijo falle en la ruta directa o confunda un prefijo único con ambiguo."""
        raiz_tareas = self.raiz / "tareas"
        carpeta = raiz_tareas / "20260913-100000-tarea-base"
        carpeta.mkdir(parents=True)

        # Ruta directa por ID completo
        res_directa = tareas.resolver_id_o_prefijo(raiz_tareas, "20260913-100000-tarea-base")
        self.assertEqual(res_directa.resolve(), carpeta.resolve())

        # Resolución por prefijo único
        res_prefijo = tareas.resolver_id_o_prefijo(raiz_tareas, "20260913-100000")
        self.assertEqual(res_prefijo.resolve(), carpeta.resolve())

    def test_validar_seguridad_id_rechaza_casos_inseguros(self) -> None:
        """Evita que identificadores vacíos, no texto o con caracteres de escape eludan la validación."""
        with self.assertRaises(tareas.RutaInsegura):
            tareas.validar_seguridad_id("")
        with self.assertRaises(tareas.RutaInsegura):
            tareas.validar_seguridad_id(None)  # type: ignore
        with self.assertRaises(tareas.RutaInsegura):
            tareas.validar_seguridad_id("tarea/sub")
        with self.assertRaises(tareas.RutaInsegura):
            tareas.validar_seguridad_id("tarea\\sub")
        with self.assertRaises(tareas.RutaInsegura):
            tareas.validar_seguridad_id("..")
        with self.assertRaises(tareas.RutaInsegura):
            tareas.validar_seguridad_id("tarea\x00nulo")

    def test_asegurar_confinamiento_acepta_rutas_seguras_y_rechaza_escapes(self) -> None:
        """Evita que asegurar_confinamiento tolere escapes fuera de tareas/ o rechace rutas válidas."""
        raiz_tareas = self.raiz / "tareas"
        raiz_tareas.mkdir(parents=True)
        c = raiz_tareas / "20260913-100000-demo"
        c.mkdir()
        tarea_md = c / "TAREA.md"
        tarea_md.write_text("# Demo\n", encoding="utf-8")

        # Rutas válidas dentro de tareas/ no deben lanzar excepción
        tareas.asegurar_confinamiento(raiz_tareas, c)
        tareas.asegurar_confinamiento_archivo(raiz_tareas, tarea_md)

        # Rutas que escapan de tareas/ deben fallar con RutaInsegura
        fuera = self.raiz / "otro_archivo.txt"
        fuera.write_text("afuera", encoding="utf-8")
        with self.assertRaises(tareas.RutaInsegura):
            tareas.asegurar_confinamiento(raiz_tareas, fuera)
        with self.assertRaises(tareas.RutaInsegura):
            tareas.asegurar_confinamiento_archivo(raiz_tareas, fuera)


class TestMutacionCliComandosYCodigos(MutacionBaseTestCase):
    """Pruebas directas de CLI para códigos de salida (2 y 1), filtros y salidas humanas."""

    def test_parser_subcomando_opcion_invalida_sale_con_codigo_2_exacto(self) -> None:
        """Evita que errores de sintaxis o banderas desconocidas devuelvan un código distinto a 2."""
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "listar", "--bandera-inexistente"]
        )
        self.assertEqual(rc, 2)
        self.assertIn("ERROR:", err)

    def test_cmd_nueva_prioridad_por_defecto_50_y_sufijo_custom(self) -> None:
        """Evita que la prioridad por defecto difiera de 50 o que --sufijo sea ignorado si el título existe."""
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        rc, out, err = self._callado(
            cli.main,
            [
                "--proyecto", str(self.raiz), "tarea", "nueva",
                "Mi Titulo Largo", "--sufijo", "mi-slug-personal"
            ]
        )
        self.assertEqual(rc, 0, err)
        carpetas = [d for d in (self.raiz / "tareas").iterdir() if d.is_dir()]
        self.assertEqual(len(carpetas), 1)
        self.assertTrue(carpetas[0].name.endswith("-mi-slug-personal"))
        tarea_md = carpetas[0] / "TAREA.md"
        texto = tarea_md.read_text(encoding="utf-8")
        self.assertIn("- PRIORIDAD: 50", texto)

    def test_cmd_nueva_recorte_de_slug_largo(self) -> None:
        """El ID entero es el prefijo de cada commit de esa tarea: eran 40 caracteres, y por un
        sufijo de 41 hubo que rehacer dos commits de 0.18.0. Ahora son 16 como mucho."""
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        titulo_largo = "a" * 80
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "nueva", titulo_largo]
        )
        self.assertEqual(rc, 0, err)
        carpetas = [d for d in (self.raiz / "tareas").iterdir() if d.is_dir()]
        slug = carpetas[0].name.split("-", 2)[2]
        self.assertEqual(len(slug), 16)

    def test_cmd_nueva_corta_el_sufijo_en_una_palabra_entera(self) -> None:
        """Media palabra se lee peor que una palabra menos, y el listado está para leerse de un
        vistazo. Si el corte cae justo en el guion, la última palabra ya está entera."""
        from tools.tareas import _sufijo_del_titulo

        self.assertEqual(_sufijo_del_titulo("juzgar evidencia real desde el CLI 0.18"),
                         "juzgar-evidencia")
        self.assertEqual(_sufijo_del_titulo("medición de sombras vencidas"), "medicion-de")
        self.assertEqual(_sufijo_del_titulo("corte"), "corte")
        self.assertEqual(_sufijo_del_titulo("supercalifragilisticoespialidoso"),
                         "supercalifragili")

    def test_cmd_nueva_con_sufijo_vacio_no_pone_ninguno(self) -> None:
        """`--sufijo ""` es una elección, no una ausencia: el ID queda sólo con fecha y hora."""
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "nueva", "un título cualquiera",
             "--sufijo", ""]
        )
        self.assertEqual(rc, 0, err)
        carpetas = [d for d in (self.raiz / "tareas").iterdir() if d.is_dir()]
        self.assertRegex(carpetas[0].name, r"^[0-9]{8}-[0-9]{6}$")

    def test_cmd_listar_incompatibilidad_cerradas_y_todas_devuelve_codigo_1(self) -> None:
        """Evita que combinar --cerradas y --todas se procese exitosamente o devuelva código distinto a 1."""
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        rc, out, err = self._callado(
            cli.main,
            ["--proyecto", str(self.raiz), "tarea", "listar", "--cerradas", "--todas"]
        )
        self.assertEqual(rc, 1)
        self.assertIn("incompatibles", err)

    def test_cmd_listar_por_defecto_solo_abiertas_y_filtros_etiqueta_texto(self) -> None:
        """Evita que el listado por defecto muestre cerradas o que los filtros de etiqueta y texto fallen."""
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        raiz_tareas = self.raiz / "tareas"

        # Tarea 1: Abierta, etiqueta "bug", texto en cuerpo "fuga de memoria"
        c1 = raiz_tareas / "20260913-100001-t1"
        c1.mkdir(parents=True)
        (c1 / "TAREA.md").write_text("# Tarea 1\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 80\n- ETIQUETAS: bug\n\nContiene fuga de memoria.\n", encoding="utf-8")

        # Tarea 2: Cerrada, etiqueta "bug", texto en cuerpo "otra cosa"
        c2 = raiz_tareas / "20260913-100002-t2"
        c2.mkdir(parents=True)
        (c2 / "TAREA.md").write_text("# Tarea 2\n\n- ESTADO: CERRADA\n- PRIORIDAD: 50\n- ETIQUETAS: bug\n\nSin relacion.\n", encoding="utf-8")

        # Tarea 3: Abierta, etiqueta "sensor", texto en cuerpo "fuga detectada"
        c3 = raiz_tareas / "20260913-100003-t3"
        c3.mkdir(parents=True)
        (c3 / "TAREA.md").write_text("# Tarea 3\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 20\n- ETIQUETAS: sensor\n\nFuga detectada en sensor.\n", encoding="utf-8")

        # 1. Por defecto: sólo abiertas (T1 y T3 presentes, T2 ausente)
        rc_def, out_def, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "listar", "--json"])
        self.assertEqual(rc_def, 0)
        ids_def = [t["id"] for t in json.loads(out_def)]
        self.assertEqual(ids_def, ["20260913-100001-t1", "20260913-100003-t3"])

        # 2. Filtro etiqueta exacto (case-insensitive)
        rc_etiq, out_etiq, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "listar", "--etiqueta", "BUG", "--todas", "--json"])
        self.assertEqual(rc_etiq, 0)
        ids_etiq = [t["id"] for t in json.loads(out_etiq)]
        self.assertEqual(ids_etiq, ["20260913-100001-t1", "20260913-100002-t2"])

        # 3. Filtro texto buscando en cuerpo cuando no figura en el título
        rc_txt, out_txt, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "listar", "--texto", "fuga", "--json"])
        self.assertEqual(rc_txt, 0)
        ids_txt = [t["id"] for t in json.loads(out_txt)]
        self.assertEqual(ids_txt, ["20260913-100001-t1", "20260913-100003-t3"])

        # 4. Sin coincidencias devuelve mensaje de aviso y código 0
        rc_cero, out_cero, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "listar", "--texto", "termino_inexistente"])
        self.assertEqual(rc_cero, 0)
        self.assertIn("No hay tareas que coincidan con la búsqueda.", out_cero)

    def test_cmd_ver_ruta_y_formato_humano(self) -> None:
        """Evita que cmd_ver confunda --ruta y --json o emita etiquetas erróneas en formato humano."""
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        carpeta = self.raiz / "tareas" / "20260913-100000-demo"
        carpeta.mkdir(parents=True)
        tarea_md = carpeta / "TAREA.md"
        tarea_md.write_text("# Sola\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n", encoding="utf-8")

        # Incompatibilidad --ruta y --json
        rc_inc, _, err_inc = self._callado(
            cli.main, ["--proyecto", str(self.raiz), "tarea", "ver", "20260913-100000", "--ruta", "--json"]
        )
        self.assertEqual(rc_inc, 1)
        self.assertIn("incompatibles", err_inc)

        # --ruta sola imprime solo el path a TAREA.md
        rc_ruta, out_ruta, _ = self._callado(
            cli.main, ["--proyecto", str(self.raiz), "tarea", "ver", "20260913-100000", "--ruta"]
        )
        self.assertEqual(rc_ruta, 0)
        self.assertEqual(out_ruta.strip(), str(tarea_md.resolve()))

        # Formato humano sin etiquetas y sin cuerpo
        rc_hum, out_hum, _ = self._callado(
            cli.main, ["--proyecto", str(self.raiz), "tarea", "ver", "20260913-100000"]
        )
        self.assertEqual(rc_hum, 0)
        self.assertIn("Etiquetas: (ninguna)", out_hum)
        self.assertIn("(sin descripción adicional)", out_hum)

    def test_cmd_cerrar_y_reabrir_mensajes_cambio_e_idempotencia(self) -> None:
        """Evita que cerrar o reabrir reporten mensajes invertidos o fallen ante estados ya fijados."""
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        carpeta = self.raiz / "tareas" / "20260913-100000-demo"
        carpeta.mkdir(parents=True)
        (carpeta / "TAREA.md").write_text("# Demo\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n", encoding="utf-8")

        # Cerrar abierta
        rc1, out1, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "cerrar", "20260913-100000"])
        self.assertEqual(rc1, 0)
        self.assertIn("Tarea cerrada: 20260913-100000-demo", out1)

        # Cerrar ya cerrada (idempotente)
        rc2, out2, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "cerrar", "20260913-100000"])
        self.assertEqual(rc2, 0)
        self.assertIn("Tarea ya estaba cerrada: 20260913-100000-demo", out2)

        # Reabrir cerrada
        rc3, out3, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "reabrir", "20260913-100000"])
        self.assertEqual(rc3, 0)
        self.assertIn("Tarea reabierta: 20260913-100000-demo", out3)

        # Reabrir ya abierta (idempotente)
        rc4, out4, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "reabrir", "20260913-100000"])
        self.assertEqual(rc4, 0)
        self.assertIn("Tarea ya estaba abierta: 20260913-100000-demo", out4)

    def test_cmd_revisar_json_y_humano_exito_y_fallo(self) -> None:
        """Evita que cmd_revisar omita el código 1 ante problemas o emita estructura JSON incorrecta."""
        self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "init"])
        raiz_tareas = self.raiz / "tareas"

        # Tarea válida
        c_ok = raiz_tareas / "20260913-100000-ok"
        c_ok.mkdir(parents=True)
        (c_ok / "TAREA.md").write_text("# Ok\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n", encoding="utf-8")

        # Archivos auxiliares permitidos README y .gitignore no deben considerarse problemas
        (raiz_tareas / "README").write_text("info", encoding="utf-8")
        (raiz_tareas / ".gitignore").write_text("*.tmp\n", encoding="utf-8")

        # Revisión OK en JSON
        rc_jok, out_jok, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "revisar", "--json"])
        self.assertEqual(rc_jok, 0)
        data_jok = json.loads(out_jok)
        self.assertTrue(data_jok["ok"])
        self.assertEqual(data_jok["tareas_validas"], 1)
        self.assertEqual(data_jok["problemas"], [])

        # Introducir problema: archivo suelto no permitido
        (raiz_tareas / "invalido.txt").write_text("suelto", encoding="utf-8")

        # Revisión con fallo en JSON
        rc_jerr, out_jerr, _ = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "revisar", "--json"])
        self.assertEqual(rc_jerr, 1)
        data_jerr = json.loads(out_jerr)
        self.assertFalse(data_jerr["ok"])
        self.assertEqual(len(data_jerr["problemas"]), 1)

        # Revisión con fallo en modo humano
        rc_herr, _, err_herr = self._callado(cli.main, ["--proyecto", str(self.raiz), "tarea", "revisar"])
        self.assertEqual(rc_herr, 1)
        self.assertIn("REVISIÓN FALLIDA", err_herr)
