"""Evidencia de tareas y políticas optativas verificadas sobre archivos construidos."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from nucleo.caso import cargar_casos
from nucleo.medida import cargar_catalogo
from nucleo.mutacion import correr
from nucleo.relacion import cargar_relaciones


RAIZ = Path(__file__).resolve().parents[1]
CLI = RAIZ / "tools" / "cli.py"
EJEMPLO = RAIZ / "ejemplo" / "seguimiento-tareas"
ID = "20260912-140000-investigacion"


class PoliticasSeguimientoTests(unittest.TestCase):
    def test_corpus_ejercita_ambas_polaridades_de_cada_politica(self):
        """Cada política optativa tiene defectos que rechaza y estados correctos que acepta."""
        catalogo = cargar_catalogo([EJEMPLO / "catalogos"])
        casos = cargar_casos(EJEMPLO / "corpus")
        self.assertEqual(len(catalogo), 3)
        for mid, medida in catalogo.items():
            propios = [c for c in casos if c["medida"] == mid]
            self.assertEqual({c["etiqueta"] == "verde_correcto" for c in propios}, {True, False})
            for caso in propios:
                with self.subTest(caso=caso["id"]):
                    self.assertEqual(medida.evaluar(caso["evidencia"]).ok,
                                     caso["etiqueta"] == "verde_correcto")

    def test_mutacion_no_deja_politicas_sin_fijar(self):
        """Cambiar filtros, precondiciones o umbrales de las políticas debe ser observable."""
        catalogo = cargar_catalogo([EJEMPLO / "catalogos"])
        datos = correr(catalogo, cargar_casos(EJEMPLO / "corpus"))
        self.assertTrue(datos["mutante"])
        self.assertEqual({m["apunta_a"] for m in datos["mutante"]}, set(catalogo))
        self.assertEqual([m["id"] for m in datos["mutante"]
                          if not m["detecciones_conductuales"] and not m["rechazos_del_algebra"]], [])


class EvidenciaTareasRevisionTests(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory(prefix="oracle-p3-revision-")
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        self.proyecto = self.raiz / "proyecto ñ"
        self.carpeta = self.proyecto / "tareas" / ID
        self.carpeta.mkdir(parents=True)
        self.documento = self.carpeta / "TAREA.md"
        self.documento.write_text("# Investigación\n\n- ESTADO: CERRADA\n- PRIORIDAD: 80\n\n")
        self.entorno = {k: v for k, v in os.environ.items()
                        if k != "ORACLE_PROYECTO" and not k.startswith("GIT_")}

    def ejecutar(self, *args, timeout=10):
        return subprocess.run([sys.executable, "-B", str(CLI), "tarea", "hechos", *args,
                               "--proyecto", str(self.proyecto)],
                              cwd=self.raiz, env=self.entorno, capture_output=True, timeout=timeout)

    def hechos(self, *args):
        r = self.ejecutar(*args)
        self.assertEqual(r.returncode, 0, r.stderr.decode())
        return json.loads(r.stdout)

    def agregar(self, texto):
        with self.documento.open("a") as archivo:
            archivo.write(texto)

    def test_evidencia_determinista_declarada_y_observada(self):
        """Una lectura repetida conserva bytes y no presenta CERRADA como trabajo verificado."""
        primero = self.ejecutar()
        segundo = self.ejecutar()
        self.assertEqual(primero.returncode, 0, primero.stderr)
        self.assertEqual(primero.stdout, segundo.stdout)
        self.assertNotIn(str(self.raiz).encode(), primero.stdout)
        datos = json.loads(primero.stdout)
        tarea = datos["tarea_seguimiento"][0]
        self.assertEqual(tarea["estado_declarado"], "CERRADA")
        self.assertEqual(tarea["sha256_documento"], hashlib.sha256(self.documento.read_bytes()).hexdigest())
        self.assertEqual(datos["lectura_seguimiento"][0]["git"], "no_solicitado")
        self.assertFalse(datos["archivo_seguimiento"][0]["git_comprobado"])
        relaciones = cargar_relaciones([EJEMPLO / "relaciones"])
        self.assertEqual(set(datos), set(relaciones))
        tipos = {"texto": str, "entero": int, "booleano": bool}
        for nombre, relacion in relaciones.items():
            for fila in datos[nombre]:
                self.assertEqual(set(fila), {c.nombre for c in relacion.campos})
                for campo in relacion.campos:
                    self.assertIs(type(fila[campo.nombre]), tipos[campo.tipo])

    def test_enlaces_de_p2_y_defecto_local_producen_testigos(self):
        """El enlace escapado de adjuntar se resuelve y una referencia ausente queda como defecto."""
        captura = self.carpeta / "captura ñ (1)#.png"
        captura.write_bytes(b"imagen construida\x00\xff")
        self.agregar("[captura](captura%20%C3%B1%20%281%29%23.png)\n"
                     "[falta](ausente.txt)\n- URL: https://youtu.be/ejemplo?t=92 (marca: 01:32)\n")
        datos = self.hechos()
        refs = {f["destino_declarado"]: f for f in datos["referencia_seguimiento"]}
        self.assertEqual(refs["captura%20%C3%B1%20%281%29%23.png"]["estado"], "presente")
        self.assertEqual(refs["ausente.txt"]["estado"], "ausente")
        self.assertEqual(refs["https://youtu.be/ejemplo?t=92"]["estado"], "no_comprobado")
        politica = cargar_catalogo([EJEMPLO / "catalogos"])["seguimiento.referencias_locales_presentes"]
        self.assertFalse(politica.evaluar(datos).ok)
        (self.carpeta / "ausente.txt").write_text("ahora existe")
        self.assertTrue(politica.evaluar(self.hechos()).ok)

    def test_enlaces_de_codigo_no_son_referencias_del_documento(self):
        """Ejemplos en código no inventan referencias rotas de la tarea."""
        self.agregar("`[inline](ausente.txt)`\n```md\n[falso](ausente.md)\n```\n"
                     "[real](#contexto)\n")
        refs = self.hechos()["referencia_seguimiento"]
        self.assertEqual([f["destino_declarado"] for f in refs], ["#contexto"])

    def test_escapes_y_enlaces_simbolicos_no_se_declaran_presentes(self):
        """La existencia fuera del proyecto o detrás de un symlink no prueba una referencia local."""
        externo = self.raiz / "externo.txt"
        externo.write_text("externo")
        (self.carpeta / "enlace.txt").symlink_to(externo)
        self.agregar("[fuera](../../../externo.txt)\n[link](enlace.txt)\n"
                     "[codificado](%2e%2e/%2e%2e/%2e%2e/externo.txt)\n")
        datos = self.hechos()
        refs = {f["destino_declarado"]: f["estado"] for f in datos["referencia_seguimiento"]}
        self.assertEqual(refs["../../../externo.txt"], "fuera_del_proyecto")
        self.assertEqual(refs["enlace.txt"], "no_comprobado")
        self.assertEqual(refs["%2e%2e/%2e%2e/%2e%2e/externo.txt"], "fuera_del_proyecto")
        self.assertFalse(datos["lectura_seguimiento"][0]["completa"])

    def test_sintaxis_omitida_impide_afirmar_lectura_completa(self):
        """Enlaces Markdown por referencia no soportados dejan una omisión medible."""
        self.agregar("[referencia][clave]\n\n[clave]: ausente.txt\n")
        datos = self.hechos()
        self.assertTrue(datos["omision_seguimiento"])
        politica = cargar_catalogo([EJEMPLO / "catalogos"])["seguimiento.lectura_sin_omisiones"]
        self.assertFalse(politica.evaluar(datos).ok)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requiere FIFO POSIX")
    def test_inventario_no_lee_adjuntos_especiales(self):
        """Un FIFO junto al Markdown se inventaría sin bloquear la extracción."""
        os.mkfifo(self.carpeta / "entrada.md")
        datos = self.hechos()
        fila = next(f for f in datos["archivo_seguimiento"] if f["ruta"].endswith("entrada.md"))
        self.assertEqual(fila["tipo"], "especial")
        self.assertFalse(datos["lectura_seguimiento"][0]["completa"])

    def test_markdown_grande_se_declara_omitido(self):
        """La evidencia informa el límite de lectura en vez de afirmar inspección completa."""
        nota = self.carpeta / "grande.md"
        with nota.open("wb") as archivo:
            archivo.truncate(2 * 1024 * 1024 + 1)
        datos = self.hechos()
        self.assertTrue(any(o["ruta"].endswith("grande.md") for o in datos["omision_seguimiento"]))
        self.assertFalse(datos["lectura_seguimiento"][0]["completa"])

    def test_registro_roto_no_emite_json_parcial(self):
        """Un error del documento central invalida la lectura en lugar de perder la tarea."""
        self.documento.write_bytes(b"\xff")
        r = self.ejecutar()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, b"")
        self.assertNotIn(b"Traceback", r.stderr)

    @unittest.skipUnless(shutil.which("git"), "requiere Git")
    def test_git_optativo_y_politica_de_confirmacion(self):
        """Una política de Git falla sin comprobación y sólo pasa tras confirmar el contenido."""
        def git(*args):
            r = subprocess.run(["git", "-C", str(self.proyecto), *args], env=self.entorno,
                               capture_output=True, timeout=10)
            self.assertEqual(r.returncode, 0, r.stderr)
        medida = cargar_catalogo([EJEMPLO / "catalogos"])["seguimiento.archivos_confirmados_sin_cambios"]
        self.assertFalse(medida.evaluar(self.hechos()).ok)
        self.assertEqual(self.hechos("--git")["lectura_seguimiento"][0]["git"], "sin_repositorio")
        git("init", "-q")
        git("add", "--", "tareas")
        self.assertFalse(medida.evaluar(self.hechos("--git")).ok)
        git("-c", "user.name=Prueba", "-c", "user.email=prueba@example.invalid",
            "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "Ejemplo")
        self.assertTrue(medida.evaluar(self.hechos("--git")).ok)

    def test_ayuda_no_requiere_tracker_ni_escribe(self):
        """Consultar el contrato no inicia ni modifica tareas."""
        antes = self.documento.read_bytes()
        r = self.ejecutar("--help")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(self.documento.read_bytes(), antes)

    def test_parentesis_escapados_y_titulo_no_alteran_destino(self):
        """La ruta declarada conserva escapes y un título opcional no se vuelve parte del nombre."""
        (self.carpeta / "nota(uno).md").write_text("contexto")
        self.agregar('[nota](nota\\(uno\\).md "título")\n')
        referencia = self.hechos()["referencia_seguimiento"][0]
        self.assertEqual(referencia["destino_declarado"], r"nota\(uno\).md")
        self.assertEqual(referencia["estado"], "presente")

    def test_cada_aparicion_se_conserva_sin_duplicar_autolink_interno(self):
        """Dos enlaces en una línea son dos declaraciones; un destino entre ángulos es una sola."""
        self.agregar('[uno](https://ejemplo.invalid/a) [dos](https://ejemplo.invalid/a)\n'
                     '[tres](<https://ejemplo.invalid/b>)\n')
        refs = self.hechos()["referencia_seguimiento"]
        self.assertEqual(sum(r["destino_declarado"] == "https://ejemplo.invalid/a" for r in refs), 2)
        self.assertEqual(sum(r["destino_declarado"] == "https://ejemplo.invalid/b" for r in refs), 1)

    def test_enlace_multilinea_deja_omision_si_no_se_resuelve(self):
        """Un enlace válido escrito en dos líneas no desaparece detrás de completa=true."""
        self.agregar('[nota](\nausente.txt)\n')
        datos = self.hechos()
        self.assertTrue(datos["referencia_seguimiento"] or datos["omision_seguimiento"])
        if not datos["referencia_seguimiento"]:
            self.assertFalse(datos["lectura_seguimiento"][0]["completa"])

    def test_parent_dotdot_no_oculta_un_componente_simbolico(self):
        """Normalizar .. antes de inspeccionar componentes puede borrar un symlink de la ruta."""
        externo = self.raiz / "externo" / "sub"
        externo.mkdir(parents=True)
        (self.carpeta / "puente").symlink_to(externo, target_is_directory=True)
        (self.carpeta / "parece-local.txt").write_text("local")
        self.agregar('[salida](puente/../parece-local.txt)\n')
        datos = self.hechos()
        referencia = datos["referencia_seguimiento"][0]
        self.assertNotEqual(referencia["estado"], "presente")
        self.assertTrue(any(a["ruta"].endswith("/puente") and a["tipo"] == "enlace"
                            for a in datos["archivo_seguimiento"]))

    def test_falso_cierre_de_cerca_no_expone_codigo_como_enlace(self):
        """Una cerca de cierre con texto extra no termina el bloque de código."""
        self.agregar('```md\n```no-es-cierre\n[falso](ausente.txt)\n```\n')
        self.assertEqual(self.hechos()["referencia_seguimiento"], [])

    def test_esquema_http_no_depende_de_mayusculas(self):
        """Una URL aceptada por anotar conserva su categoría remota al extraer hechos."""
        self.agregar('- URL: HTTPS://ejemplo.invalid/video?t=12 (marca: 00:12)\n')
        referencia = self.hechos()["referencia_seguimiento"][0]
        self.assertEqual(referencia["clase"], "remota")

    @unittest.skipUnless(os.name == "posix" and os.geteuid() != 0, "requiere permisos POSIX sin root")
    def test_permiso_denegado_no_se_confunde_con_referencia_ausente(self):
        """No poder comprobar un destino es un fallo de lectura, no evidencia de ausencia."""
        privado = self.proyecto / "privado"
        privado.mkdir()
        (privado / "nota.txt").write_text("existe")
        self.agregar('[privado](../../privado/nota.txt)\n')
        privado.chmod(0)
        try:
            r = self.ejecutar()
        finally:
            privado.chmod(0o700)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, b"")
        self.assertNotIn(b"Traceback", r.stderr)

    def test_central_grande_falla_antes_de_emitir_una_tarea_parcial(self):
        """El documento central también respeta el límite de lectura declarado."""
        with self.documento.open("ab") as documento:
            documento.write(b"x" * (2 * 1024 * 1024))
        r = self.ejecutar()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, b"")
        self.assertNotIn(b"Traceback", r.stderr)

    def test_central_simbolico_interno_no_se_lee_como_documento_propio(self):
        """La política de no seguir enlaces también alcanza al archivo central de una tarea."""
        copia = self.carpeta / "copia.md"
        self.documento.rename(copia)
        self.documento.symlink_to(copia)
        r = self.ejecutar()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, b"")

    def test_literales_escapados_no_se_convierten_en_referencias(self):
        """Escapar el corchete de apertura permite escribir ejemplos literales sin enlace."""
        self.agregar(r"\[literal](ausente.txt)" + "\n")
        self.assertEqual(self.hechos()["referencia_seguimiento"], [])

    def test_ruta_absoluta_tampoco_elimina_un_symlink_antes_de_comprobarlo(self):
        """La comprobación por componentes también se aplica a destinos absolutos declarados."""
        afuera = self.raiz / "afuera" / "sub"
        afuera.mkdir(parents=True)
        (self.carpeta / "puente").symlink_to(afuera, target_is_directory=True)
        (self.carpeta / "local.txt").write_text("local")
        destino = str(self.carpeta / "puente") + "/../local.txt"
        self.agregar(f"[absoluto](<{destino}>)\n")
        self.assertNotEqual(self.hechos()["referencia_seguimiento"][0]["estado"], "presente")

    def test_carpeta_central_simbolica_no_salta_la_validacion(self):
        """Una carpeta de tarea simbólica no permite leer un central que evitó el prechequeo."""
        alias = self.proyecto / "tareas" / "20260912-150000-alias"
        alias.symlink_to(self.carpeta, target_is_directory=True)
        r = self.ejecutar()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, b"")
