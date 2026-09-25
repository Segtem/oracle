"""El verde del corpus no es una nueva medición del producto."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from nucleo.proyecto import Proyecto
from tools import cli


class TestAlcanceTests(unittest.TestCase):
    def test_todo_declara_los_modulos_fuera_de_la_mutacion(self):
        from tools import mutar_codigo

        salida = io.StringIO()
        with redirect_stdout(salida):
            cli._alcance_test(todo=True, propio_oracle=True)
        informe = mutar_codigo.alcance_del_perfil()
        texto = salida.getvalue()
        for directorio in ("nucleo", "tools"):
            fuera = informe[directorio]["fuera"]
            self.assertIn(f"{directorio}/: {len(fuera)} de {informe[directorio]['total']}", texto)
            for ruta, razon in fuera.items():
                self.assertIn(ruta, texto)
                self.assertIn(razon, texto)
        self.assertIn("tools/mcp_contrato.py", texto)
        self.assertIn("tools/__init__.py", texto)

    def test_el_perfil_de_mutacion_solo_se_informa_con_todo_y_en_oracle(self):
        # El perfil es del propio Oracle: un consumidor no tiene esos módulos, y sin --todo no se
        # mutó nada.
        for todo, propio in ((True, False), (False, True), (False, False)):
            with self.subTest(todo=todo, propio=propio):
                salida = io.StringIO()
                with redirect_stdout(salida):
                    cli._alcance_test(todo=todo, propio_oracle=propio)
                self.assertNotIn("MUTACIÓN DE CÓDIGO", salida.getvalue())

    def test_perfil_exige_razon_para_cada_modulo_fuera(self):
        from tools import mutar_codigo

        informe = mutar_codigo.alcance_del_perfil()
        for directorio in ("nucleo", "tools"):
            encontrados = {p.relative_to(mutar_codigo.RAIZ).as_posix()
                           for p in (mutar_codigo.RAIZ / directorio).rglob("*.py")}
            self.assertEqual(encontrados, informe[directorio]["dentro"] |
                             set(informe[directorio]["fuera"]))
            self.assertTrue(all(informe[directorio]["fuera"].values()))

    def ejecutar(self, *args):
        salida = io.StringIO()
        with redirect_stdout(salida):
            rc = cli.main(list(args))
        return rc, salida.getvalue()

    def comprobar_alcance(self, salida):
        resumen = salida[salida.rindex("ALCANCE:"):]
        self.assertIn("medidas contra casos guardados del corpus", resumen)
        self.assertIn("sin nueva medición", resumen)
        self.assertIn("no reejecuta los comandos de origen ni el producto", resumen)
        self.assertIn("mutación de medidas (--rapido)", resumen)

    def crear_caso(self, raiz, medida):
        caso = raiz / "corpus" / "001-juego.caso"
        caso.write_text(f'''caso 001-juego:
    fecha: "2026-09-19"
    origen:
        repo: "juego"
        commit: "local"
        comando: "node -c game.js"
    procedencia: observada
    titulo: "Archivo del juego con sintaxis válida"
    etiqueta: verde_correcto
    sintoma:
        El archivo parsea.
    como_se_detecto: herramienta_ajena
    medida: {medida}
    evidencia:
        archivo: ruta, sintaxis_valida
            "game.js", true
    leccion:
        Este caso guarda el resultado del parser en ese momento.
''', encoding="utf-8")
        return caso

    def test_vacio_advierte_sin_cambiar_codigo_ci(self):
        for nivel in ([], ["--rapido"], ["--todo"]):
            with self.subTest(nivel=nivel), tempfile.TemporaryDirectory() as td:
                self.ejecutar("init", td)
                rc, salida = self.ejecutar("test", "--proyecto", td, *nivel)
                self.assertEqual(rc, 0, salida)
                self.assertIn("VEREDICTO: SIN MEDICIÓN (advertencia: proyecto vacío", salida)
                self.assertNotIn("VEREDICTO: VERDE", salida)
                self.assertNotIn("CORPUS OK", salida)
                self.assertIn("CORPUS: sin casos guardados", salida)

    def test_corpus_propio_y_heredado_no_reejecutan_el_producto(self):
        for propia in (False, True):
            with self.subTest(propia=propia), tempfile.TemporaryDirectory() as td:
                raiz = Path(td)
                self.ejecutar("init", td)
                mid = "proceso.sintaxis_valida_tras_edicion_masiva"
                if propia:
                    mid = "juego.sintaxis"
                    (raiz / "catalogos" / "juego.oracle").write_text('''ninguno juego.sintaxis:
    de archivo a
    donde a.sintaxis_valida == false
    umbral <= 0 segun contrato porque "el archivo debe parsear"
    ambito universal
    alcance "NO ve errores de comportamiento"
''', encoding="utf-8")
                caso = self.crear_caso(raiz, mid)
                guardado = caso.read_bytes()
                juego = raiz / "game.js"
                juego.write_text("const flota = [];\n", encoding="utf-8")
                rc, salida = self.ejecutar("test", "--proyecto", td, "--rapido")
                self.assertEqual(rc, 0, salida)
                self.assertIn("VEREDICTO: VERDE", salida)
                self.comprobar_alcance(salida)
                juego.write_text("function { JavaScript destruido", encoding="utf-8")
                rc_roto, salida_roto = self.ejecutar("test", "--proyecto", td, "--rapido")
                self.assertEqual((rc_roto, salida_roto), (rc, salida))
                self.assertEqual(caso.read_bytes(), guardado)

                # Cambiar la evidencia sí invalida la polaridad declarada del caso.
                caso.write_text(caso.read_text().replace('"game.js", true', '"game.js", false'))
                rc, salida = self.ejecutar("test", "--proyecto", td, "--rapido")
                self.assertEqual(rc, 1, salida)
                self.assertIn("VEREDICTO: ROJO", salida)
                self.assertIn("aceptación", salida)
                self.comprobar_alcance(salida)

                caso.write_text("caso roto: no es un caso válido", encoding="utf-8")
                rc, salida = self.ejecutar("test", "--proyecto", td, "--rapido")
                self.assertEqual(rc, 1, salida)
                self.assertIn("VEREDICTO: ROJO", salida)
                self.assertIn("falló: corpus", salida)
                self.comprobar_alcance(salida)

                # La ruta completa también debe llegar al veredicto, sin traceback.
                rc, salida = self.ejecutar("test", "--proyecto", td)
                self.assertEqual(rc, 1, salida)
                self.assertIn("VEREDICTO: ROJO", salida)
                self.assertIn("MUTACIÓN NO CONFIABLE", salida)

    def test_estructura_invalida_no_es_sin_medicion(self):
        with tempfile.TemporaryDirectory() as td:
            captura = io.StringIO()
            with redirect_stdout(captura):
                rc = cli.cmd_test(Proyecto(Path(td)), ["--rapido"])
            salida = captura.getvalue()
            self.assertEqual(rc, 1, salida)
            self.assertIn("VEREDICTO: ROJO (estructura de proyecto inválida)", salida)
            self.assertNotIn("VEREDICTO: SIN MEDICIÓN", salida)
