"""Revisión independiente de captura, consultas y seguimiento por el CLI público."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import quote


CLI = Path(__file__).resolve().parents[1] / "tools" / "cli.py"
ID = "20260912-120000-investigacion"


class RevisionContextoTests(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory(prefix="oracle-p2-revision-")
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        self.proyecto = self.raiz / "consumidor ñ"
        self.carpeta = self.proyecto / "tareas" / ID
        self.carpeta.mkdir(parents=True)
        self.documento = self.carpeta / "TAREA.md"
        self.original = b"# Investigar\r\n\r\n- ESTADO: ABIERTA\r\n- PRIORIDAD: 50\r\n\r\nCuerpo libre\r\n"
        self.documento.write_bytes(self.original)
        self.documento.chmod(0o640)
        self.env = {k: v for k, v in os.environ.items()
                    if k != "ORACLE_PROYECTO" and not k.startswith("GIT_")}

    def ejecutar(self, *args, timeout=10):
        return subprocess.run([sys.executable, "-B", str(CLI), "tarea", *args,
                               "--proyecto", str(self.proyecto)],
                              env=self.env, cwd=self.raiz, capture_output=True,
                              text=True, timeout=timeout)

    def exito(self, *args):
        r = self.ejecutar(*args, "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_nota_con_url_marca_y_sangria_preserva_texto_y_documento(self):
        """Capturar una cita conserva su sangría y URL exacta sin alterar bytes anteriores."""
        nota = "  cita con sangría\n    segunda línea  "
        url = "https://www.youtube.com/watch?v=ejemplo&t=92s#fragmento"
        self.exito("anotar", ID, nota, "--url", url, "--marca", "01:32")
        contenido = self.documento.read_bytes()
        self.assertTrue(contenido.startswith(self.original))
        self.assertIn(nota.encode(), contenido)
        self.assertIn(url.encode(), contenido)
        self.assertIn(b"01:32", contenido)
        self.assertEqual(self.documento.stat().st_mode & 0o777, 0o640)

    def test_urls_invalidas_no_dejan_cambios(self):
        """URLs no absolutas, con controles o esquemas ajenos no se registran como referencias."""
        for url in ("file:///tmp/a", "https://", "https://ejemplo.invalid/\nroto", "../nota.md",
                    "https://:80", "https://usuario@", "https://ejemplo.invalid:puerto"):
            with self.subTest(url=url):
                r = self.ejecutar("anotar", ID, "--url", url)
                self.assertNotEqual(r.returncode, 0)
                self.assertNotIn("Traceback", r.stderr)
                self.assertEqual(self.documento.read_bytes(), self.original)

    def test_adjuntar_escapa_nombre_y_preserva_origen_y_cuerpo(self):
        """Un nombre con espacios, Unicode, corchetes y numeral produce un enlace utilizable."""
        origen = self.raiz / "captura ñ [detalle](1)#.png"
        origen.write_bytes(b"captura construida\x00\xff")
        datos = self.exito("adjuntar", ID, str(origen))
        destino = self.carpeta / origen.name
        self.assertEqual(Path(datos["ruta"]), destino)
        self.assertEqual(origen.read_bytes(), destino.read_bytes())
        self.assertTrue(self.documento.read_bytes().startswith(self.original))
        self.assertIn(quote(origen.name, safe="").encode(), self.documento.read_bytes())
        self.assertEqual(self.documento.stat().st_mode & 0o777, 0o640)

    def test_colision_con_enlace_roto_no_toca_destino_externo(self):
        """Adjuntar no sigue ni reemplaza un enlace existente con el nombre elegido."""
        origen = self.raiz / "captura.png"
        origen.write_bytes(b"imagen")
        externo = self.raiz / "no-crear.png"
        destino = self.carpeta / origen.name
        destino.symlink_to(externo)
        r = self.ejecutar("adjuntar", ID, str(origen))
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(destino.is_symlink())
        self.assertFalse(externo.exists())
        self.assertEqual(self.documento.read_bytes(), self.original)

    def test_documento_roto_revierte_la_copia_del_adjunto(self):
        """El fallo al registrar un adjunto no deja una copia huérfana ni pierde el original."""
        self.documento.write_bytes(b"no es una tarea\xff")
        origen = self.raiz / "nota.txt"
        origen.write_text("contexto")
        r = self.ejecutar("adjuntar", ID, str(origen))
        self.assertEqual(r.returncode, 1)
        self.assertFalse((self.carpeta / origen.name).exists())
        self.assertEqual(origen.read_text(), "contexto")
        self.assertEqual(self.documento.read_bytes(), b"no es una tarea\xff")

    def test_limite_de_adjuntos_requiere_eleccion_explicita(self):
        """Un video grande no se copia accidentalmente al tracker."""
        origen = self.raiz / "video.mp4"
        with origen.open("wb") as f:
            f.truncate(20 * 1024 * 1024 + 1)
        r = self.ejecutar("adjuntar", ID, str(origen))
        self.assertEqual(r.returncode, 1)
        self.assertFalse((self.carpeta / origen.name).exists())
        self.exito("adjuntar", ID, str(origen), "--permitir-grande")
        self.assertEqual((self.carpeta / origen.name).stat().st_size, origen.stat().st_size)

    def test_busqueda_encuentra_nota_y_declara_omisiones(self):
        """La consulta distingue sin coincidencias de archivos que no examinó."""
        (self.carpeta / "nota.md").write_text("Antes\nHallazgo ÚNICO\n")
        (self.carpeta / "captura.png").write_bytes(b"Hallazgo")
        (self.carpeta / "enlace.txt").symlink_to(self.raiz / "ausente")
        datos = self.exito("buscar", "hallazgo")
        self.assertTrue(any(c["linea"] == 2 and c["ruta"].endswith("nota.md")
                            for c in datos["coincidencias"]))
        omitidos = {c["ruta"] for c in datos["omitidos"]}
        self.assertIn(f"tareas/{ID}/captura.png", omitidos)
        self.assertIn(f"tareas/{ID}/enlace.txt", omitidos)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requiere FIFO POSIX")
    def test_busqueda_no_abre_fifos_ni_dispositivos(self):
        """Un archivo especial junto a una tarea no puede bloquear una consulta de texto."""
        os.mkfifo(self.carpeta / "entrada.txt")
        r = self.ejecutar("buscar", "dato", "--json", timeout=3)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(any(c["ruta"].endswith("entrada.txt")
                            for c in json.loads(r.stdout)["omitidos"]))

    def test_referencias_no_incluyen_sufijos_ni_repos_anidados(self):
        """Una mención del ID exacto no se confunde con otra tarea ni otro repositorio."""
        (self.proyecto / "codigo.py").write_text(f"# {ID}\n# {ID}-otra\n")
        ajeno = self.proyecto / "otro-repo"
        (ajeno / ".git").mkdir(parents=True)
        (ajeno / "ajeno.py").write_text(ID)
        datos = self.exito("referencias", ID)
        self.assertEqual(datos["tipo"], "mencion_textual")
        referencias = datos["coincidencias"]
        self.assertTrue(any(c["ruta"] == "codigo.py" and c["linea"] == 1 for c in referencias))
        self.assertFalse(any(c["ruta"] == "codigo.py" and c["linea"] == 2 for c in referencias))
        self.assertFalse(any("ajeno.py" in c["ruta"] for c in referencias))

    def test_consultas_no_ocultan_documentos_de_tarea_rotos(self):
        """Buscar y resumir no dan éxito parcial si el registro central es inválido."""
        self.documento.write_bytes(b"registro corrupto\xff")
        for args in (("buscar", "cuerpo"), ("resumen",), ("referencias", ID)):
            with self.subTest(args=args):
                r = self.ejecutar(*args, "--json")
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertNotIn("Traceback", r.stderr)

    def test_seguimiento_publico_funciona_sin_catalogo(self):
        """El despacho de seguimiento no necesita interpretar el oracle.json del consumidor."""
        (self.proyecto / "oracle.json").write_text("inválido")
        datos = self.exito("seguimiento")
        self.assertIsNone(datos["repositorio"])
        self.assertIn(f"tareas/{ID}/TAREA.md", datos["sin_repositorio"])

    def test_busqueda_recupera_notas_en_subcarpetas(self):
        """Agrupar notas dentro de la tarea no las vuelve invisibles para buscar."""
        notas = self.carpeta / "kb" / "fuentes"
        notas.mkdir(parents=True)
        (notas / "hallazgo.oracle").write_text("Hallazgo profundo\n")
        datos = self.exito("buscar", "profundo")
        self.assertTrue(any(c["ruta"].endswith("kb/fuentes/hallazgo.oracle")
                            for c in datos["coincidencias"]))

    def test_salida_humana_informa_archivos_no_examinados(self):
        """Sin JSON también se informa que una imagen fue omitida de la búsqueda."""
        (self.carpeta / "captura.png").write_bytes(b"imagen")
        r = self.ejecutar("buscar", "palabra ausente")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("captura.png", r.stdout + r.stderr)

    def test_resumen_conserva_la_identidad_de_etiquetas(self):
        """Resumen y listar deben reconocer las mismas etiquetas sin mezclar mayúsculas."""
        self.documento.write_text("# Investigación\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 1\n"
                                 "- ETIQUETAS: Bug, bug, Bug\n\nNota\n")
        datos = self.exito("resumen")
        self.assertEqual(datos["etiquetas"], {"Bug": 1, "bug": 1})

    @unittest.skipUnless(os.name == "posix" and os.geteuid() != 0, "requiere permisos POSIX sin root")
    def test_fallo_de_lectura_no_se_disfraza_de_omision_exitosa(self):
        """Un permiso denegado al leer contexto invalida la consulta con la ruta afectada."""
        nota = self.carpeta / "nota.txt"
        nota.write_text("dato")
        nota.chmod(0)
        try:
            r = self.ejecutar("buscar", "dato")
        finally:
            nota.chmod(0o600)
        self.assertEqual(r.returncode, 1)
        self.assertIn("nota.txt", r.stderr)
        self.assertNotIn("Traceback", r.stderr)

    @unittest.skipUnless(os.name == "posix" and os.geteuid() != 0, "requiere permisos POSIX sin root")
    def test_error_al_enumerar_tracker_tiene_diagnostico_sin_traceback(self):
        """Un tracker sin permiso de lectura falla limpiamente también antes de abrir tareas."""
        tracker = self.proyecto / "tareas"
        tracker.chmod(0o100)
        try:
            for args in (("buscar", "dato"), ("referencias", ID), ("resumen",)):
                with self.subTest(args=args):
                    r = self.ejecutar(*args)
                    self.assertEqual(r.returncode, 1)
                    self.assertNotIn("Traceback", r.stderr)
                    self.assertIn("ERROR", r.stderr)
        finally:
            tracker.chmod(0o700)
