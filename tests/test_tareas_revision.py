"""Regresiones observadas al revisar el tracker desde su interfaz pública."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor


CLI = Path(__file__).resolve().parents[1] / "tools" / "cli.py"
CONTENIDO = "# Tarea\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n\nCuerpo\n"


class RevisionTareas(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory(prefix="oracle-revision-tareas-")
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.entorno = dict(os.environ)
        self.entorno.pop("ORACLE_PROYECTO", None)
        self.entorno["PYTHONDONTWRITEBYTECODE"] = "1"

    def ejecutar(self, *args, cwd=None):
        return subprocess.run(
            [sys.executable, "-B", str(CLI), "tarea", *args],
            cwd=cwd or self.raiz, env=self.entorno, capture_output=True,
            text=True, timeout=20,
        )

    def inicializar(self):
        resultado = self.ejecutar("init")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)

    def tarea(self, nombre="20260911-210000-prueba", contenido=CONTENIDO):
        ruta = self.raiz / "tareas" / nombre / "TAREA.md"
        ruta.parent.mkdir(parents=True)
        ruta.write_bytes(contenido.encode("utf-8"))
        return ruta

    def test_ayuda_de_cada_verbo_no_escribe(self):
        """Pedir ayuda a init creaba un tracker en el directorio actual."""
        for verbo in ("init", "nueva", "listar", "ls", "ver", "cerrar", "reabrir", "revisar"):
            with self.subTest(verbo=verbo):
                resultado = self.ejecutar(verbo, "--help")
                self.assertEqual(resultado.returncode, 0, resultado.stderr)
                self.assertIn("oracle tarea", resultado.stdout)
                self.assertEqual(list(self.raiz.iterdir()), [])

    def test_opciones_desconocidas_no_se_ignoran(self):
        """Listar --inventada devolvía éxito como si hubiese aplicado un filtro."""
        self.inicializar()
        ruta = self.tarea()
        for args in (("init",), ("nueva", "Nombre"), ("listar",),
                     ("ver", ruta.parent.name), ("cerrar", ruta.parent.name),
                     ("reabrir", ruta.parent.name), ("revisar",)):
            with self.subTest(args=args):
                antes = {p.relative_to(self.raiz): p.read_bytes()
                         for p in self.raiz.rglob("*") if p.is_file()}
                resultado = self.ejecutar(*args, "--inventada")
                self.assertNotEqual(resultado.returncode, 0)
                despues = {p.relative_to(self.raiz): p.read_bytes()
                           for p in self.raiz.rglob("*") if p.is_file()}
                self.assertEqual(antes, despues)

    def test_opcion_antes_del_titulo_no_cambia_el_titulo(self):
        """El valor bug de --etiqueta se tomaba por título de la tarea."""
        self.inicializar()
        resultado = self.ejecutar("nueva", "--etiqueta", "bug", "Título real", "--json")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        tarea = json.loads(self.ejecutar("ver", json.loads(resultado.stdout)["id"], "--json").stdout)
        self.assertEqual(tarea["titulo"], "Título real")
        self.assertEqual(tarea["etiquetas"], ["bug"])

    def test_titulo_y_etiqueta_iguales_no_pierden_argumentos(self):
        """Eliminar argumentos por igualdad borraba el valor de --etiqueta."""
        self.inicializar()
        resultado = self.ejecutar("nueva", "bug", "--etiqueta", "bug", "--json")
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        tarea = json.loads(self.ejecutar("ver", json.loads(resultado.stdout)["id"], "--json").stdout)
        self.assertEqual(tarea["titulo"], "bug")
        self.assertEqual(tarea["etiquetas"], ["bug"])

    def test_no_crea_documentos_invalidos_desde_titulo_o_etiqueta(self):
        """Un salto de línea inyectaba cabeceras y nueva devolvía éxito con datos rotos."""
        self.inicializar()
        for args in (("Nombre\n\n- ESTADO: CERRADA",),
                     ("Nombre", "--etiqueta", "bug\n- ESTADO: CERRADA")):
            with self.subTest(args=args):
                resultado = self.ejecutar("nueva", *args)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertEqual(list((self.raiz / "tareas").glob("*/TAREA.md")), [])

    def test_cambio_de_estado_preserva_bytes_ajenos_al_valor(self):
        """Cerrar convertía el cuerpo CRLF a LF y normalizaba la línea de estado."""
        texto = ("# Prueba á\r\n\r\n  * ESTADO : ABIERTA  \r\n- PRIORIDAD: 50\r\n"
                 "- ASIGNADO: Brian\r\n\r\n```\r\n- ESTADO: ABIERTA\r\n```\r\n\r\n")
        ruta = self.tarea(contenido=texto)
        original = ruta.read_bytes()
        resultado = self.ejecutar("cerrar", ruta.parent.name)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(ruta.read_bytes(), original.replace(b"ABIERTA", b"CERRADA", 1))
        self.assertEqual(self.ejecutar("reabrir", ruta.parent.name).returncode, 0)
        self.assertEqual(ruta.read_bytes(), original)

    def test_archivo_simbolico_externo_no_se_lee_ni_modifica(self):
        """Ver y revisar seguían TAREA.md fuera del tracker aunque su carpeta fuese interna."""
        externo = self.raiz / "externo.md"
        externo.write_text(CONTENIDO + "MARCADOR_EXTERNO", encoding="utf-8")
        carpeta = self.raiz / "tareas" / "20260911-210000-enlace"
        carpeta.mkdir(parents=True)
        ruta = carpeta / "TAREA.md"
        ruta.symlink_to(externo)
        for args in (("ver", carpeta.name), ("listar",), ("revisar",),
                     ("cerrar", carpeta.name), ("reabrir", carpeta.name)):
            with self.subTest(args=args):
                resultado = self.ejecutar(*args)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertNotIn("MARCADOR_EXTERNO", resultado.stdout)
                self.assertTrue(ruta.is_symlink())
                self.assertEqual(externo.read_text(), CONTENIDO + "MARCADOR_EXTERNO")

    def test_carpeta_simbolica_externa_no_se_audita_como_valida(self):
        """La auditoría no aplicaba el confinamiento que sí tenía ver por ID."""
        externo = self.raiz / "externa"
        externo.mkdir()
        (externo / "TAREA.md").write_text(CONTENIDO)
        (self.raiz / "tareas").mkdir()
        (self.raiz / "tareas" / "20260911-210000-enlace").symlink_to(externo, target_is_directory=True)
        for verbo in ("listar", "revisar"):
            with self.subTest(verbo=verbo):
                self.assertNotEqual(self.ejecutar(verbo).returncode, 0)

    def test_raiz_simbolica_no_redirige_escrituras(self):
        """Resolver tareas/ antes de comprobarlo permitía inicializar fuera del proyecto."""
        externo = self.raiz / "externa"
        externo.mkdir()
        (self.raiz / "tareas").symlink_to(externo, target_is_directory=True)
        for args in (("init",), ("nueva", "Prueba")):
            with self.subTest(args=args):
                self.assertNotEqual(self.ejecutar(*args).returncode, 0)
                self.assertEqual(list(externo.iterdir()), [])

    def test_links_rotos_y_ciclicos_tienen_diagnostico(self):
        """Un enlace roto desaparecía del censo sin figurar como registro inválido."""
        (self.raiz / "tareas").mkdir()
        enlace = self.raiz / "tareas" / "20260911-210000-roto"
        enlace.symlink_to(self.raiz / "ausente")
        for verbo in ("listar", "revisar"):
            with self.subTest(verbo=verbo):
                resultado = self.ejecutar(verbo)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertIn(enlace.name, resultado.stdout + resultado.stderr)
                self.assertNotIn("Traceback", resultado.stderr)

    def test_nombre_de_carpeta_invalido_no_desaparece_ni_pasa(self):
        """Una carpeta ajena al contrato de identidad se aceptaba como tarea válida."""
        self.tarea(nombre="nombre-invalido")
        resultado = self.ejecutar("revisar")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("nombre-invalido", resultado.stdout + resultado.stderr)

    def test_utf8_invalido_falla_sin_traceback(self):
        """Cerrar no traducía errores de codificación a diagnóstico del tracker."""
        ruta = self.tarea()
        ruta.write_bytes(b"\xff\xfe")
        for verbo in ("ver", "cerrar", "reabrir"):
            with self.subTest(verbo=verbo):
                resultado = self.ejecutar(verbo, ruta.parent.name)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertNotIn("Traceback", resultado.stderr)
                self.assertIn("TAREA.md", resultado.stderr)
                self.assertEqual(ruta.read_bytes(), b"\xff\xfe")

    def test_creaciones_concurrentes_no_pierden_tareas(self):
        """Comprobar exists antes de mkdir no reserva el ID frente a otro proceso."""
        self.inicializar()
        with ThreadPoolExecutor(max_workers=8) as ejecutor:
            resultados = list(ejecutor.map(lambda _: self.ejecutar("nueva", "Simultánea", "--json"), range(8)))
        for resultado in resultados:
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
        ids = [json.loads(resultado.stdout)["id"] for resultado in resultados]
        self.assertEqual(len(set(ids)), 8)
        listado = self.ejecutar("listar", "--json")
        self.assertEqual(listado.returncode, 0, listado.stderr)
        self.assertEqual({t["id"] for t in json.loads(listado.stdout)}, set(ids))

    def test_init_no_escribe_por_readme_simbolico(self):
        """Init seguía un README simbólico roto y creaba un archivo fuera del tracker."""
        (self.raiz / "tareas").mkdir()
        externo = self.raiz / "afuera.md"
        readme = self.raiz / "tareas" / "README.md"
        readme.symlink_to(externo)
        resultado = self.ejecutar("init")
        self.assertNotEqual(resultado.returncode, 0)
        self.assertFalse(externo.exists())
        self.assertTrue(readme.is_symlink())

    def test_ver_rechaza_la_misma_identidad_que_revisar(self):
        """Ver aceptaba por coincidencia directa un ID que revisar consideraba inválido."""
        ruta = self.tarea(nombre="nombre-invalido")
        for verbo in ("ver", "cerrar", "reabrir"):
            with self.subTest(verbo=verbo):
                resultado = self.ejecutar(verbo, ruta.parent.name)
                self.assertNotEqual(resultado.returncode, 0)
                self.assertEqual(ruta.read_text(), CONTENIDO)

    def test_estado_normalizado_tambien_se_puede_actualizar(self):
        """La lectura aceptaba estado en minúsculas y cerrar no encontraba su valor."""
        ruta = self.tarea(contenido=CONTENIDO.replace("ABIERTA", "abierta"))
        self.assertEqual(self.ejecutar("ver", ruta.parent.name).returncode, 0)
        resultado = self.ejecutar("cerrar", ruta.parent.name)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(ruta.read_text(), CONTENIDO.replace("ABIERTA", "CERRADA"))

    def test_init_con_archivo_como_raiz_no_da_traceback(self):
        """Un destino que era archivo provocaba una excepción sin traducir en init."""
        archivo = self.raiz / "archivo"
        archivo.write_text("preservar")
        resultado = self.ejecutar("init", str(archivo))
        self.assertNotEqual(resultado.returncode, 0)
        self.assertNotIn("Traceback", resultado.stderr)
        self.assertEqual(archivo.read_text(), "preservar")

    @unittest.skipIf(os.name == "nt", "permisos POSIX")
    def test_cerrar_conserva_los_permisos_del_documento(self):
        """El temporal de reemplazo convertía un documento compartido 0640 a 0600."""
        ruta = self.tarea()
        ruta.chmod(0o640)
        resultado = self.ejecutar("cerrar", ruta.parent.name)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(ruta.stat().st_mode & 0o777, 0o640)

    @unittest.skipUnless(shutil.which("git"), "requiere Git para comprobar sus reglas reales")
    def test_gitignore_del_proyecto_no_oculta_las_tareas(self):
        """La regla histórica TAREA.md ocultaba todos los registros del nuevo tracker."""
        (self.raiz / ".gitignore").write_bytes((CLI.parents[1] / ".gitignore").read_bytes())
        subprocess.run(["git", "init", "-q"], cwd=self.raiz, check=True, capture_output=True)
        resultado = subprocess.run(
            ["git", "check-ignore", "--no-index", "tareas/20260911-220000-prueba/TAREA.md"],
            cwd=self.raiz, capture_output=True, text=True,
        )
        self.assertEqual(resultado.returncode, 1, resultado.stdout + resultado.stderr)
