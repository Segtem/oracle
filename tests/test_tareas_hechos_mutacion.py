"""Fija gramática y datos omitidos por la primera ronda diagnóstica del extractor."""
import hashlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import tareas_hechos as h

ID = "20260912-140000-contrato"


class GramaticaHechosTests(unittest.TestCase):
    def test_backtick_escapado_no_oculta_un_enlace_roto(self):
        """Una apertura literal no inicia código; dentro del código una barra no anula el cierre."""
        casos = [
            (r"\`[visible](falta)`", ["falta"]),
            (r"\` [visible](falta) \`", ["falta"]),
            (r"\\`[oculto](falta)`", []),
            (r"`[oculto](falta)\` [visible](otro)", ["otro"]),
            (r"\``[oculto](falta)` [visible](otro)", ["otro"]),
            (r"\```[oculto](falta)`` [visible](otro)", ["otro"]),
        ]
        for texto, destinos in casos:
            with self.subTest(texto=texto):
                enlaces, omisiones = h._extraer_enlaces_linea(texto, h._encontrar_spans_codigo(texto))
                self.assertEqual([destino for _, _, destino in enlaces], destinos)
                self.assertEqual(omisiones, [])

    def test_paridad_de_escape_y_limites_de_codigo(self):
        """Dos barras restauran el enlace; un span incluye inicio y excluye fin."""
        for barras, esperado in [(0, False), (1, True), (2, False), (3, True), (4, False)]:
            texto = "\\" * barras + "["
            self.assertEqual(h._esta_escapado(texto, barras), esperado)
        self.assertEqual([h._esta_en_span(p, [(2, 5)]) for p in range(7)],
                         [False, False, True, True, True, False, False])

    def test_rachas_completas_y_terminacion(self):
        """Un cierre largo no aporta su sufijo; entradas incompletas terminan con resultado exacto."""
        casos = {"": [], "abc": [], "`x`": [(0, 3)], "a`x`b": [(1, 4)],
                 "``x```": [], "``x```y``": [(0, 9)], "`x": [],
                 "`a``b` [x](y)": [(0, 6)], "``x`` `y`": [(0, 5), (6, 9)]}
        # Aislar el parser hace fallar una regresión que no avanza, sin colgar la suite.
        codigo = "from tools.tareas_hechos import _encontrar_spans_codigo as f\n"
        codigo += "casos = " + repr(casos) + "\n"
        codigo += "for texto, esperado in casos.items():\n assert f(texto) == esperado, (texto, f(texto), esperado)\n"
        try:
            r = subprocess.run([sys.executable, "-B", "-c", codigo], capture_output=True,
                               timeout=3, cwd=Path(__file__).resolve().parents[1])
        except subprocess.TimeoutExpired:
            self.fail("el reconocimiento de código inline no terminó en tres segundos")
        self.assertEqual(r.returncode, 0, r.stderr.decode())

    def test_enlaces_con_posiciones_y_destinos_exactos(self):
        """Fija spans consumidos, destinos balanceados, imágenes y adyacencia sin perder caracteres."""
        casos = [
            ("[x](a)", [(0, 6, "a")]),
            ("![x](a)", [(0, 7, "a")]),
            ("![x](a)[y](b)", [(0, 7, "a"), (7, 13, "b")]),
            ("[x](a(b)c)", [(0, 10, "a(b)c")]),
            (r"[x](a\(b\)c)", [(0, 12, r"a\(b\)c")]),
            ('[x](  <a b> "titulo")', [(0, 21, "a b")]),
            (r'[x](<a\>b>)', [(0, 11, r'a\>b')]),
            ('[x](a "titulo")', [(0, 15, "a")]),
            ("[x]()", [(0, 5, "")]),
            (r"[a\]b](c)", [(0, 9, "c")]),
            (r"\\[x](a)", [(2, 8, "a")]),
            ("!", []), ("[x]", []), (r"\[x](a)", []),
            ("`[f](m)`[x](a)", [(8, 14, "a")]),
            ("[a`[]`b](c)", [(0, 11, "c")]),
            ("[a`x`](c)", [(0, 9, "c")]),
            ("`x`[a](b)", [(3, 9, "b")]),
            ("[a[b](c)", [(2, 8, "c")]),
        ]
        for texto, esperado in casos:
            with self.subTest(texto=texto):
                enlaces, omisiones = h._extraer_enlaces_linea(texto, h._encontrar_spans_codigo(texto))
                self.assertEqual(enlaces, esperado)
                self.assertEqual(omisiones, [])

    def test_etiquetas_vacias_anidadas_y_espaciado_impar(self):
        """El escaneo conserva el corchete inicial real, incluso tras texto entre corchetes."""
        casos = [("[](a)", [(0, 5, "a")]), ("![](a)", [(0, 6, "a")]),
                 ("[[x](a)", [(1, 7, "a")]),
                 ("[literal]![x](a)", [(9, 16, "a")]),
                 ("[x]( <a>)", [(0, 9, "a")])]
        for texto, esperado in casos:
            with self.subTest(texto=texto):
                self.assertEqual(h._extraer_enlaces_linea(texto, []), (esperado, []))

    def test_titulo_requiere_separador_y_cierre_tras_espacios(self):
        """No se acepta un título pegado al destino ni se pierde el cierre tras un espacio impar."""
        for texto, esperado in [(' "título" )', 11), (' "título"   )', 13),
                                (' "título"', None), (' "título" ', None),
                                ('"título")', None)]:
            with self.subTest(texto=texto):
                self.assertEqual(h._cerrar_enlace_despues_destino(texto, 0), esperado)
        self.assertEqual(h._extraer_enlaces_linea('[x](<a>"título")', []),
                         ([], ["sintaxis de enlace incompleta o multilínea no admitida"]))

    def test_sintaxis_incompleta_y_referencias_escapadas(self):
        """La omisión conserva la etiqueta real y los literales no producen falsos avisos."""
        incompleta = "sintaxis de enlace incompleta o multilínea no admitida"
        for texto in ["[", "[x", "[x](", "[x](<a", "[x](<a>", "[x](a\\"]:
            with self.subTest(texto=texto):
                self.assertEqual(h._extraer_enlaces_linea(texto, []), ([], [incompleta]))
        for texto in [r"\[texto][clave]", "`[texto][clave]`"]:
            self.assertEqual(h._extraer_enlaces_linea(texto, h._encontrar_spans_codigo(texto)), ([], []))
        self.assertEqual(h._extraer_enlaces_linea("[texto][clave]", []),
                         ([], ["enlace por referencia no resuelto: [texto][clave]"]))


class DatosHechosTests(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory(prefix="oracle-hechos-contrato-")
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        self.carpeta = self.raiz / "tareas" / ID
        self.carpeta.mkdir(parents=True)
        self.documento = self.carpeta / "TAREA.md"
        self.documento.write_text("# Contrato\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n\n")

    def referencia(self, destino, origen=None):
        return h._clasificar_referencia(self.raiz, origen or f"tareas/{ID}/TAREA.md", 7, destino)

    def test_identidad_de_referencia_y_rutas_locales(self):
        """La identidad distingue auxiliares de tareas y las rutas no atraviesan archivos ni ausencias."""
        (self.carpeta / "archivo").write_text("x")
        (self.carpeta / "a(b).txt").write_text("x")
        casos = [("./archivo", "presente"), ("././archivo", "presente"),
                 ("archivo/hijo", "ausente"), ("falta/../archivo", "ausente"),
                 ("falta/hijo", "ausente"), (r"a\(b\).txt?x#y", "presente"),
                 (str(self.carpeta / "archivo"), "presente"), ("../../../", "fuera_del_proyecto")]
        for destino, estado in casos:
            with self.subTest(destino=destino):
                ref, omision = self.referencia(destino)
                self.assertEqual(ref, {"tarea_id": ID, "origen": f"tareas/{ID}/TAREA.md",
                    "linea": 7, "destino_declarado": destino, "clase": "local", "estado": estado})
                self.assertIsNone(omision)
        for origen, identidad in [("tareas/README.md", ""), ("README.md", ""),
                                   (f"otros/{ID}/nota.md", ""), (f"tareas/{ID}/sub/nota.md", ID)]:
            ref, _ = self.referencia("#ancla", origen)
            self.assertEqual(ref["tarea_id"], identidad)

    def test_host_codificado_no_consulta_disco(self):
        """El percent encoding no permite tratar un host UNC como una ruta local."""
        with patch.object(h, "_lstat_seguro", side_effect=AssertionError("no consultar red")):
            ref, omision = self.referencia("%2F%2Fservidor/recurso")
        self.assertEqual((ref["clase"], ref["estado"]), ("no_admitida", "no_comprobado"))
        self.assertEqual(omision, {"ruta": f"tareas/{ID}/TAREA.md", "linea": 7,
            "motivo": "URL con host no admitida: %2F%2Fservidor/recurso"})

    def test_inventario_y_omisiones_exactas(self):
        """Especiales, repositorios y enlaces dejan motivos de archivo completo y no se recorren."""
        (self.raiz / "tareas" / "README.md").write_text("aux")
        (self.carpeta / "sub").mkdir()
        (self.carpeta / "sub" / "TAREA.md").write_text("adj")
        (self.carpeta / "vacio").write_bytes(b"")
        os.mkfifo(self.carpeta / "fifo")
        (self.carpeta / "puente").symlink_to("vacio")
        (self.carpeta / ".hg").mkdir()
        (self.carpeta / ".hg" / "oculto").write_text("no")
        (self.carpeta / "repo" / ".git").mkdir(parents=True)
        (self.carpeta / "repo" / "oculto").write_text("no")
        datos = h.extraer_hechos(self.raiz)
        archivos = {a["ruta"]: a for a in datos["archivo_seguimiento"]}
        for nombre, clase, tipo, tamano in [("TAREA.md", "documento", "regular", self.documento.stat().st_size),
                ("sub/TAREA.md", "adjunto", "regular", 3), ("vacio", "adjunto", "regular", 0),
                ("fifo", "adjunto", "especial", 0), ("puente", "adjunto", "enlace", 5)]:
            ruta = f"tareas/{ID}/{nombre}"
            self.assertEqual(archivos[ruta], {"tarea_id": ID, "ruta": ruta, "clase": clase,
                "tipo": tipo, "tamano_bytes": tamano, "existe": True, "git_comprobado": False,
                "en_indice": False, "en_head": False, "ignorado": False, "indice": "", "trabajo": ""})
        self.assertEqual(len(archivos), 6)
        self.assertEqual(archivos["tareas/README.md"]["tarea_id"], "")
        self.assertEqual(archivos["tareas/README.md"]["clase"], "auxiliar")
        self.assertEqual(datos["omision_seguimiento"], [
            {"ruta": f"tareas/{ID}/{nombre}", "linea": 0, "motivo": motivo}
            for nombre, motivo in [(".hg", "metadatos de control de versiones"),
                ("fifo", "archivo especial en el tracker (FIFO/dispositivo/socket)"),
                ("puente", "enlace simbólico en el tracker"), ("repo", "repositorio anidado")]])

    def test_markdown_invalido_y_frontera_exacta(self):
        """Dos MiB se leen; el byte adicional, NUL y UTF-8 inválido dejan omisiones exactas."""
        limite = 2 * 1024 * 1024
        for nombre, contenido in [("limite.md", b"x" * limite), ("grande.md", b"x" * (limite + 1)),
                                   ("nulo.md", b"\x00"), ("codificacion.md", b"\xff")]:
            (self.carpeta / nombre).write_bytes(contenido)
        datos = h.extraer_hechos(self.raiz)
        self.assertEqual(datos["omision_seguimiento"], [
            {"ruta": f"tareas/{ID}/{nombre}", "linea": 0, "motivo": motivo}
            for nombre, motivo in [("codificacion.md", "archivo Markdown con codificación inválida (no UTF-8)"),
                ("grande.md", "archivo Markdown supera el límite de 2 MiB"),
                ("nulo.md", "archivo Markdown contiene bytes nulos")]])
        base = self.documento.read_bytes()
        self.documento.write_bytes(base + b"x" * (limite - len(base)))
        tarea = h.extraer_hechos(self.raiz)["tarea_seguimiento"][0]
        self.assertEqual(tarea["sha256_documento"], hashlib.sha256(self.documento.read_bytes()).hexdigest())

    def test_cercas_de_distinto_caracter_y_tamano(self):
        """Una cerca corta o de otro carácter no cierra; el primer enlace tras cierre sí aparece."""
        nota = self.carpeta / "cercas.md"
        nota.write_text("````python\n```\n[x](oculto1)\n~~~~\n[x](oculto2)\n````\n[x](visible1)\n"
                        "~~~\n[x](oculto3)\n~~~~\n[x](visible2)\n")
        refs = h.extraer_hechos(self.raiz)["referencia_seguimiento"]
        self.assertEqual([(r["linea"], r["destino_declarado"]) for r in refs], [(7, "visible1"), (11, "visible2")])

    def test_autolink_dentro_de_url_y_enlace_no_se_duplica(self):
        """Las posiciones cubiertas evitan doble fila pero conservan apariciones independientes."""
        (self.carpeta / "urls.md").write_text("- URL: <https://a.test>\n[x](<https://b.test>) <https://c.test>\n")
        refs = h.extraer_hechos(self.raiz)["referencia_seguimiento"]
        self.assertEqual([(r["linea"], r["destino_declarado"]) for r in refs],
                         [(1, "https://a.test"), (2, "https://b.test"), (2, "https://c.test")])

    def test_git_borrados_clasificacion_y_filas_presentes(self):
        """La unión Git incluye borrados sin duplicar presentes ni inventar ausencias para lo existente."""
        ruta = f"tareas/{ID}/TAREA.md"
        filas = []
        for nombre, existe in [(ruta, True), ("tareas/README.md", False),
             (f"tareas/{ID}/borrado.txt", False), ("tareas/20260912-140001/TAREA.md", False),
             (f"tareas/{ID}/sub/TAREA.md", False), (f"tareas/{ID}/no_inventariado", True)]:
            filas.append({"ruta": nombre, "existe": existe, "en_indice": False,
                          "en_head": True, "ignorado": True, "indice": "D", "trabajo": "M"})
        with patch("tools.tareas_git.seguimiento", return_value={"repositorio": str(self.raiz), "head": "abc", "archivos": filas}):
            datos = h.extraer_hechos(self.raiz, con_git=True)
        self.assertEqual(datos["lectura_seguimiento"], [{"esquema": "oracle.tareas.hechos/v1", "git": "comprobado", "head": "abc", "completa": True}])
        archivos = {a["ruta"]: a for a in datos["archivo_seguimiento"]}
        self.assertEqual(len(archivos), 5)
        for nombre, identidad, clase in [("tareas/README.md", "", "auxiliar"),
                (f"tareas/{ID}/borrado.txt", ID, "adjunto"),
                ("tareas/20260912-140001/TAREA.md", "20260912-140001", "documento"),
                (f"tareas/{ID}/sub/TAREA.md", ID, "adjunto")]:
            self.assertEqual(archivos[nombre], {"tarea_id": identidad, "ruta": nombre, "clase": clase,
                "tipo": "ausente", "tamano_bytes": 0, "existe": False, "git_comprobado": True,
                "en_indice": False, "en_head": True, "ignorado": True, "indice": "D", "trabajo": "M"})
        self.assertTrue(archivos[ruta]["existe"])
        self.assertEqual(archivos[ruta]["tipo"], "regular")

    def test_git_sin_fila_para_archivo_recien_creado(self):
        """Una creación entre inventarios queda observada en disco, sin fingir inclusión en índice o HEAD."""
        with patch("tools.tareas_git.seguimiento", return_value={"repositorio": str(self.raiz), "head": None, "archivos": []}):
            archivo = h.extraer_hechos(self.raiz, con_git=True)["archivo_seguimiento"][0]
        self.assertEqual({k: archivo[k] for k in ["git_comprobado", "en_indice", "en_head", "ignorado", "indice", "trabajo"]},
                         {"git_comprobado": True, "en_indice": False, "en_head": False, "ignorado": False, "indice": "", "trabajo": ""})

    def test_lecturas_acotadas_y_crecimiento_tras_stat(self):
        """Cada lectura pide sólo 2 MiB más el centinela y detecta crecimiento posterior al stat."""
        limite = 2 * 1024 * 1024
        original_open = open
        adjunto = self.carpeta / "crece.md"
        adjunto.write_bytes(b"x")
        for objetivo, debe_abortar in [(self.documento, True), (adjunto, False)]:
            llamadas = []
            class LecturaQueCrece(io.BytesIO):
                def read(interno, cantidad=-1):
                    llamadas.append(cantidad)
                    self.assertEqual(cantidad, limite + 1, "el presupuesto incluye un único byte centinela")
                    return super().read(cantidad)
            def abrir(ruta, modo):
                if Path(ruta) == objetivo:
                    return LecturaQueCrece(b"x" * (limite + 1))
                return original_open(ruta, modo)
            with self.subTest(archivo=objetivo.name), patch.object(h, "open", abrir, create=True):
                if debe_abortar:
                    with self.assertRaisesRegex(h.TareaError, "documento central .* supera el límite de 2 MiB"):
                        h.extraer_hechos(self.raiz)
                else:
                    datos = h.extraer_hechos(self.raiz)
                    self.assertEqual(datos["omision_seguimiento"], [{"ruta": f"tareas/{ID}/crece.md",
                        "linea": 0, "motivo": "archivo Markdown supera el límite de 2 MiB"}])
                self.assertEqual(llamadas, [limite + 1])

    def test_frontera_exacta_despues_de_stat_y_presupuesto_central(self):
        """La lectura de exactamente 2 MiB sigue siendo válida aunque el archivo crezca tras el stat."""
        limite = 2 * 1024 * 1024
        original_open = open
        contenido = b"x" * limite
        llamadas = []
        class LecturaEnLimite(io.BytesIO):
            def read(interno, cantidad=-1):
                llamadas.append(cantidad)
                self.assertEqual(cantidad, limite + 1)
                return super().read(cantidad)
        def abrir(ruta, modo):
            if Path(ruta) == self.documento:
                return LecturaEnLimite(contenido)
            return original_open(ruta, modo)
        with patch.object(h, "open", abrir, create=True):
            datos = h.extraer_hechos(self.raiz)
        self.assertEqual(datos["omision_seguimiento"], [])
        self.assertEqual(datos["tarea_seguimiento"][0]["sha256_documento"], hashlib.sha256(contenido).hexdigest())
        self.assertEqual(llamadas, [limite + 1, limite + 1])

    def test_auxiliares_y_ocultos_no_son_documentos_centrales(self):
        """Un TAREA.md bajo carpeta oculta se inventaría como archivo, sin prechequeo de tarea central."""
        oculto = self.raiz / "tareas" / ".oculto"
        oculto.mkdir()
        (oculto / "TAREA.md").write_bytes(b"x" * (2 * 1024 * 1024 + 1))
        (self.raiz / "tareas" / "README.md").write_text("auxiliar")
        datos = h.extraer_hechos(self.raiz)
        self.assertEqual(datos["omision_seguimiento"], [{"ruta": "tareas/.oculto/TAREA.md", "linea": 0,
                         "motivo": "archivo Markdown supera el límite de 2 MiB"}])
        self.assertEqual(len(datos["tarea_seguimiento"]), 1)

    def test_error_de_listado_y_de_lectura_no_se_ocultan(self):
        """Permisos y errores de E/S deben cortar la extracción en vez de generar evidencia parcial."""
        with patch.object(Path, "iterdir", side_effect=PermissionError("denegado")):
            with self.assertRaisesRegex(h.TareaError, "error operacional al listar"):
                h.extraer_hechos(self.raiz)
        with patch.object(h, "open", side_effect=OSError("E/S"), create=True):
            with self.assertRaisesRegex(h.TareaError, "error operacional al leer"):
                h.extraer_hechos(self.raiz)
        original_open = open
        adjunto = self.carpeta / "denegado.md"
        adjunto.write_text("x")
        def abrir(ruta, modo):
            if Path(ruta) == adjunto:
                raise PermissionError("denegado")
            return original_open(ruta, modo)
        with patch.object(h, "open", abrir, create=True):
            with self.assertRaisesRegex(h.TareaError, "error operacional al leer tareas/.*/denegado.md"):
                h.extraer_hechos(self.raiz)

    def test_walk_propaga_error_en_vez_de_inventario_parcial(self):
        """Un fallo de scandir no puede dejar completa=true omitiendo una carpeta inaccesible."""
        def caminar(raiz, *, onerror):
            onerror(PermissionError("carpeta inaccesible"))
            return iter(())
        with patch.object(h.os, "walk", caminar):
            with self.assertRaisesRegex(h.TareaError, "error operacional al recorrer"):
                h.extraer_hechos(self.raiz)

    def test_prechequeo_ausencia_y_archivos_no_directorio(self):
        """Una entrada desaparecida o regular no se interpreta como carpeta de tarea."""
        (self.raiz / "tareas" / "suelto").write_text("no es una carpeta")
        original_lstat = h._lstat_seguro
        def examinar(ruta):
            if ruta == self.carpeta:
                return None
            return original_lstat(ruta)
        with patch.object(h, "_lstat_seguro", examinar):
            self.assertIsNone(h._prechequear_documentos_centrales(self.raiz, self.raiz / "tareas"))
        self.documento.unlink()
        self.assertIsNone(h._prechequear_documentos_centrales(self.raiz, self.raiz / "tareas"))

    def test_referencias_a_origen_bajo_enlace_no_atraviesan_puente(self):
        """También se verifica el directorio origen, aunque un llamador aporte una ruta simbólica."""
        puente = self.raiz / "tareas" / "puente"
        puente.symlink_to(self.carpeta, target_is_directory=True)
        for destino in ["../TAREA.md", "TAREA.md"]:
            ref, omision = self.referencia(destino, "tareas/puente/nota.md")
            self.assertEqual(ref["estado"], "no_comprobado")
            self.assertEqual(omision, {"ruta": "tareas/puente/nota.md", "linea": 7,
                         "motivo": "enlace simbólico en la ruta de referencia: tareas/puente"})

    def test_origen_inexistente_o_archivo_no_puede_contener_hijos(self):
        """Un padre ausente o regular no admite navegación con puntos ni nombres de hijos."""
        for padre in ["falta", "TAREA.md"]:
            for destino in ["../otro", "otro"]:
                ref, omision = self.referencia(destino, f"tareas/{ID}/{padre}/nota.md")
                self.assertEqual(ref["estado"], "ausente")
                self.assertIsNone(omision)

    def test_omisiones_sintacticas_con_lineas_exactas(self):
        """La política de lectura necesita motivos y líneas fieles, incluso con etiqueta distinta de clave."""
        nota = self.carpeta / "gramatica.md"
        nota.write_text("[clave]: archivo\n[etiqueta][clave]\n[x](mailto:a@b)\n"
                        "- URL: ftp://servidor\n[x](//host/recurso)\n[x](\n")
        datos = h.extraer_hechos(self.raiz)
        ruta = f"tareas/{ID}/gramatica.md"
        self.assertEqual(datos["omision_seguimiento"], [
            {"ruta": ruta, "linea": linea, "motivo": motivo}
            for linea, motivo in [
                (1, "definición de enlace por referencia no resuelta: [clave]: ..."),
                (2, "enlace por referencia no resuelto: [etiqueta][clave]"),
                (3, "esquema no admitido en referencia: mailto:a@b"),
                (4, "esquema no admitido en referencia: ftp://servidor"),
                (5, "URL de red o protocolo no admitida: //host/recurso"),
                (6, "sintaxis de enlace incompleta o multilínea no admitida")]])
        self.assertEqual([(r["linea"], r["clase"], r["estado"]) for r in datos["referencia_seguimiento"]],
                         [(3, "no_admitida", "no_comprobado"), (4, "no_admitida", "no_comprobado"),
                          (5, "no_admitida", "no_comprobado")])

    def test_cmd_json_utf8_valido_y_codigo_de_error(self):
        """El despacho emite UTF-8 válido con escapes de nombres Unix, y no emite hechos ante error."""
        from contextlib import redirect_stdout, redirect_stderr
        import json
        nombre = os.fsdecode(b"nombre-\xff")
        (self.carpeta / nombre).write_bytes(b"x")
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = h.cmd_hechos([], ["--proyecto", str(self.raiz)])
        self.assertEqual(rc, 0)
        self.assertEqual(err.getvalue(), "")
        datos = json.loads(out.getvalue().encode("utf-8"))
        self.assertIn(f"tareas/{ID}/{nombre}", [a["ruta"] for a in datos["archivo_seguimiento"]])
        out, err = io.StringIO(), io.StringIO()
        with patch.object(h, "extraer_hechos", side_effect=h.TareaError("defecto construido")), \
                redirect_stdout(out), redirect_stderr(err):
            rc = h.cmd_hechos([], ["--proyecto", str(self.raiz), "--json"])
        self.assertEqual(rc, 1)
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), "ERROR: defecto construido\n")

    def test_nul_codificado_se_omite_sin_consultar_el_destino(self):
        """%00 es sintaxis visible válida en UTF-8, pero nunca debe llegar como NUL a lstat."""
        with patch.object(h, "_lstat_seguro", side_effect=AssertionError("no consultar el destino NUL")):
            ref, omision = self.referencia("carpeta/%00nombre")
        self.assertEqual(ref, {"tarea_id": ID, "origen": f"tareas/{ID}/TAREA.md", "linea": 7,
            "destino_declarado": "carpeta/%00nombre", "clase": "no_admitida", "estado": "no_comprobado"})
        self.assertEqual(omision, {"ruta": f"tareas/{ID}/TAREA.md", "linea": 7,
                                 "motivo": "carácter NUL en referencia"})
        (self.carpeta / "nul.md").write_text("[x](%00)\n")
        datos = h.extraer_hechos(self.raiz)
        self.assertFalse(datos["lectura_seguimiento"][0]["completa"])
        self.assertEqual(datos["omision_seguimiento"], [{"ruta": f"tareas/{ID}/nul.md", "linea": 1,
                                                       "motivo": "carácter NUL en referencia"}])

    def test_enlace_de_adjunto_no_reinterpreta_barras_percent_encoded(self):
        """Un nombre con barra antes de paréntesis conserva esa barra al consumir el enlace que produce P2."""
        from tools.tareas_contexto import _escapar_enlace_markdown
        nombres = [r"barra\(1).txt", r"barra\)1.txt", "literal(1).txt"]
        lineas = []
        destinos = []
        for nombre in nombres:
            (self.carpeta / nombre).write_text("adjunto real de la prueba")
            etiqueta, destino = _escapar_enlace_markdown(nombre)
            destinos.append(destino)
            lineas.append(f"[{etiqueta}]({destino})")
        (self.carpeta / "adjuntos.md").write_text("\n".join(lineas))
        datos = h.extraer_hechos(self.raiz)
        self.assertEqual([(r["destino_declarado"], r["estado"]) for r in datos["referencia_seguimiento"]],
                         [(d, "presente") for d in destinos])
        self.assertEqual(datos["omision_seguimiento"], [])

    def test_sufijo_de_directorio_no_acepta_archivo_regular(self):
        """La existencia de archivo no prueba archivo/ ni archivo/.; también se conserva en ruta absoluta."""
        (self.carpeta / "archivo").write_text("regular")
        (self.carpeta / "directorio").mkdir()
        for nombre, esperado in [("archivo", "ausente"), ("directorio", "presente")]:
            for base in [nombre, str(self.carpeta / nombre)]:
                for sufijo in ["/", "/.", "/./", "/./."]:
                    with self.subTest(destino=base + sufijo):
                        ref, omision = self.referencia(base + sufijo)
                        self.assertEqual(ref["estado"], esperado)
                        self.assertIsNone(omision)
        ref, omision = self.referencia("archivo/./../directorio")
        self.assertEqual(ref["estado"], "ausente")
        self.assertIsNone(omision)

    def test_sufijos_sobre_symlink_no_borran_la_omision(self):
        """Exigir directorio no permite atravesar el symlink ni ocultarlo detrás de puntos."""
        (self.carpeta / "destino").mkdir()
        (self.carpeta / "puente").symlink_to("destino", target_is_directory=True)
        for base in ["puente", str(self.carpeta / "puente")]:
            for sufijo in ["/", "/.", "/../TAREA.md", "/./../TAREA.md"]:
                with self.subTest(destino=base + sufijo):
                    ref, omision = self.referencia(base + sufijo)
                    self.assertEqual(ref["estado"], "no_comprobado")
                    self.assertEqual(omision, {"ruta": f"tareas/{ID}/TAREA.md", "linea": 7,
                        "motivo": f"enlace simbólico en la ruta de referencia: tareas/{ID}/puente"})

    def test_titulos_consumidos_no_aportan_enlaces_ni_definiciones(self):
        """Paréntesis, enlaces y autolinks escritos dentro del título no son referencias del documento."""
        textos = [
            '[x](<a> "título ) [z](b) <https://falso.test> [uno][dos]")',
            '[x](a "título ( [z](b)")',
            "[x](a 'título ) [z](b)')",
            r'[x](a "título \" ) [z](b)")',
            '[x](<a> "")',
            '[x](a "título"  )',
        ]
        for texto in textos:
            with self.subTest(texto=texto):
                self.assertEqual(h._extraer_enlaces_linea(texto, h._encontrar_spans_codigo(texto)),
                                 ([(0, len(texto), "a")], []))
        (self.carpeta / "titulos.md").write_text("\n".join(textos) + '\n[x](a "título )") [real](c)\n')
        datos = h.extraer_hechos(self.raiz)
        self.assertEqual([(r["linea"], r["destino_declarado"]) for r in datos["referencia_seguimiento"]],
                         [(i, "a") for i in range(1, 8)] + [(7, "c")])
        self.assertEqual(datos["omision_seguimiento"], [])

    def test_titulo_incompleto_omite_resto_de_linea_sin_exponer_su_contenido(self):
        """Un título sin cierre fiable deja omisión; sus aparentes enlaces o autolinks no son evidencia."""
        casos = ['[x](a "sin cierre ) [falso](b) <https://falso.test>',
                 '[x](<a> "sin cierre ) [falso](b) [uno][dos]',
                 '[x](a "cerrado" sobrante [falso](b))',
                 '[x](<a> título no admitido [falso](b))',
                 '[x](a (título no admitido [falso](b)))']
        (self.carpeta / "incompletos.md").write_text("\n".join(casos) + "\n[real](c)\n")
        datos = h.extraer_hechos(self.raiz)
        self.assertEqual([(r["linea"], r["destino_declarado"]) for r in datos["referencia_seguimiento"]], [(6, "c")])
        self.assertEqual(datos["omision_seguimiento"], [{"ruta": f"tareas/{ID}/incompletos.md", "linea": i,
            "motivo": "sintaxis de enlace incompleta o multilínea no admitida"} for i in range(1, 6)])

    def test_extraccion_sin_git_no_invoca_el_sensor(self):
        """El argumento omitido no habilita el proceso Git ni siquiera en un proyecto sin repositorio."""
        with patch("tools.tareas_git.seguimiento", side_effect=AssertionError("Git no solicitado")):
            datos = h.extraer_hechos(self.raiz)
        self.assertEqual(datos["lectura_seguimiento"], [{"esquema": "oracle.tareas.hechos/v1",
            "completa": True, "git": "no_solicitado", "head": ""}])

    def test_url_con_angulos_parciales_conserva_declaracion(self):
        """La envoltura de autolink se retira sólo cuando ambos ángulos pertenecen al token completo."""
        (self.carpeta / "declaradas.md").write_text("- URL: <https://a.test\n- URL: https://b.test>\n")
        referencias = h.extraer_hechos(self.raiz)["referencia_seguimiento"]
        self.assertEqual([r["destino_declarado"] for r in referencias],
                         ["<https://a.test", "https://b.test>"])


def load_tests(loader, tests, pattern):
    """Adelanta gramática barata sin perder pruebas recibidas ni futuras clases del módulo."""
    def aplanar(suite):
        for prueba in suite:
            if isinstance(prueba, unittest.TestSuite):
                yield from aplanar(prueba)
            else:
                yield prueba
    pruebas = list(aplanar(tests))
    pruebas.sort(key=lambda prueba: not isinstance(prueba, GramaticaHechosTests))
    return unittest.TestSuite(pruebas)
