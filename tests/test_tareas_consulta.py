"""Pruebas exhaustivas del motor de consultas TQL y su integración en el CLI de tareas (0.19.0).

Cubre:
1. Tokenización y columna de error precisa (caracteres Unicode).
2. Gramática, precedencia de operadores lógicos y comparadores, corchetes [...].
3. Chequeo estático de tipos en tiempo de compilación.
4. Evaluación del AST en memoria (etiquetas case-insensitive, prioridad, IDs, palabras clave).
5. Salida del método explicar().
6. Integración CLI:
   - listar <consulta> (filtro, estado, diagnósticos de error en stderr con código 2).
   - listar --explicar (sin requerir tracker, salida en stdout con código 0).
   - listar --por-id, --invertir y combinaciones.
   - desetiquetar --consulta (masivo, incompatibilidad con IDs explícitos, respeto a estados).
   - referencias sin ID desde directorio de tarea y subdirectorios, error código 2 fuera.
   - init --sin-readme y compatibilidad con revisar.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.tareas import Tarea
from tools.tareas_consulta import (
    Consulta,
    ConsultaInvalida,
    Nodo,
    NodoComparacion,
    NodoCualquiera,
    NodoEntero,
    NodoEtiqueta,
    NodoEtiquetada,
    NodoId,
    NodoNo,
    NodoO,
    NodoPrioridad,
    NodoY,
    Token,
    compilar,
    tokenizar,
)

RAIZ = Path(__file__).resolve().parents[1]
CLI = RAIZ / "tools/cli.py"


def crear_tarea_en_memoria(
    ident: str = "20260915-100000-a",
    prioridad: int = 50,
    etiquetas: tuple[str, ...] = ("bug",),
    estado: str = "ABIERTA",
    titulo: str = "Tarea de prueba",
) -> Tarea:
    return Tarea(
        id=ident,
        titulo=titulo,
        estado=estado,
        prioridad=prioridad,
        etiquetas=etiquetas,
        campos_adicionales={},
        cuerpo="Cuerpo de la tarea",
        ruta=Path(f"/tmp/mock/{ident}/TAREA.md"),
    )


class TestTokenizador(unittest.TestCase):
    """Pruebas unitarias de análisis léxico."""

    def test_tokens_basicos(self) -> None:
        toks = tokenizar(":bug y prioridad mayor 50")
        textos = [t.texto for t in toks]
        columnas = [t.columna for t in toks]
        self.assertEqual(textos, [":bug", "y", "prioridad", "mayor", "50"])
        self.assertEqual(columnas, [0, 5, 7, 17, 23])

    def test_corchetes_aislados_y_pegados(self) -> None:
        toks = tokenizar("[:bug y [:ui]]")
        textos = [t.texto for t in toks]
        self.assertEqual(textos, ["[", ":bug", "y", "[", ":ui", "]", "]"])

    def test_etiquetas_con_caracteres_unicode(self) -> None:
        toks = tokenizar(":ñandú :urgente_1")
        self.assertEqual([t.texto for t in toks], [":ñandú", ":urgente_1"])

    def test_enteros_con_signo(self) -> None:
        toks = tokenizar("+42 -10 0")
        self.assertEqual([t.texto for t in toks], ["+42", "-10", "0"])

    def test_identificador_de_tarea(self) -> None:
        toks = tokenizar("20260915-100000-sensor 20260915-100001")
        self.assertEqual(toks[0].texto, "20260915-100000-sensor")
        self.assertEqual(toks[1].texto, "20260915-100001")

    def test_comparadores_en_palabras_y_simbolos(self) -> None:
        for comp in ("menor", "hasta", "mayor", "desde", "igual", "distinto"):
            with self.subTest(comp=comp):
                toks = tokenizar(comp)
                self.assertEqual(toks[0].texto, comp)

    def test_columna_cuenta_caracteres_unicode(self) -> None:
        # 'ñ' es un carácter pero 2 bytes en UTF-8
        try:
            compilar(":ñandú inventado")
            self.fail("debía lanzar ConsultaInvalida")
        except ConsultaInvalida as e:
            lineas = str(e).splitlines()
            self.assertEqual(len(lineas), 3)
            # ':ñandú ' son 7 caracteres (0..6), 'inventado' inicia en columna 7
            self.assertEqual(lineas[1].index("^"), 7)
            self.assertIn("token inesperado «inventado»", lineas[2])

    def test_error_dos_puntos_vacio(self) -> None:
        with self.assertRaises(ConsultaInvalida) as ctx:
            compilar(":")
        self.assertIn("etiqueta vacía", str(ctx.exception))


class TestCompiladorYPrecedencia(unittest.TestCase):
    """Pruebas sintácticas y de precedencia de operadores."""

    def test_consulta_vacia_equivale_a_cualquiera(self) -> None:
        for vacia in ("", "   ", "\t\n"):
            c = compilar(vacia)
            self.assertIsInstance(c.raiz, NodoCualquiera)
            self.assertTrue(c.evaluar(crear_tarea_en_memoria()))

    def test_palabras_clave_primarias(self) -> None:
        c1 = compilar("cualquiera")
        self.assertIsInstance(c1.raiz, NodoCualquiera)
        c2 = compilar("etiquetada")
        self.assertIsInstance(c2.raiz, NodoEtiquetada)

    def test_precedencia_no_sobre_y_o(self) -> None:
        # 'no :a y :b' debe agruparse como '(no :a) y :b'
        c = compilar("no :a y :b")
        self.assertIsInstance(c.raiz, NodoY)
        self.assertIsInstance(c.raiz.izq, NodoNo)
        self.assertIsInstance(c.raiz.der, NodoEtiqueta)

    def test_precedencia_y_sobre_o(self) -> None:
        # ':a o :b y :c' debe agruparse como ':a o (:b y :c)'
        c = compilar(":a o :b y :c")
        self.assertIsInstance(c.raiz, NodoO)
        self.assertIsInstance(c.raiz.izq, NodoEtiqueta)
        self.assertIsInstance(c.raiz.der, NodoY)

    def test_asociatividad_por_izquierda(self) -> None:
        # ':a y :b y :c' -> '((:a y :b) y :c)'
        c = compilar(":a y :b y :c")
        self.assertIsInstance(c.raiz, NodoY)
        self.assertIsInstance(c.raiz.izq, NodoY)
        self.assertIsInstance(c.raiz.der, NodoEtiqueta)

    def test_corchetes_alteran_precedencia(self) -> None:
        # '[:a o :b] y :c' -> '(:a o :b) y :c'
        c = compilar("[:a o :b] y :c")
        self.assertIsInstance(c.raiz, NodoY)
        self.assertIsInstance(c.raiz.izq, NodoO)
        self.assertIsInstance(c.raiz.der, NodoEtiqueta)

    def test_doble_negacion(self) -> None:
        c = compilar("no no :bug")
        self.assertIsInstance(c.raiz, NodoNo)
        self.assertIsInstance(c.raiz.operando, NodoNo)

    def test_corchete_sin_cerrar(self) -> None:
        with self.assertRaises(ConsultaInvalida) as ctx:
            compilar("[:bug y :ui")
        self.assertIn("sin cerrar", str(ctx.exception))

    def test_corchete_de_cierre_inesperado(self) -> None:
        with self.assertRaises(ConsultaInvalida) as ctx:
            compilar(":bug]")
        self.assertIn("token inesperado «]»", str(ctx.exception))

    def test_operador_colgante_al_final(self) -> None:
        with self.assertRaises(ConsultaInvalida) as ctx:
            compilar(":bug y")
        self.assertIn("se esperaba una primaria", str(ctx.exception))


class TestChequeoDeTipos(unittest.TestCase):
    """Validación estática de tipos en tiempo de compilación."""

    def test_raiz_entera_es_invalida(self) -> None:
        for expr in ("50", "prioridad", "-10"):
            with self.subTest(expr=expr):
                with self.assertRaises(ConsultaInvalida) as ctx:
                    compilar(expr)
                self.assertIn("tipo incorrecto", str(ctx.exception))
                self.assertIn("booleana", str(ctx.exception))

    def test_operador_logico_con_entero(self) -> None:
        for expr in (":bug y 50", "prioridad o :ui", "no 10", "no prioridad"):
            with self.subTest(expr=expr):
                with self.assertRaises(ConsultaInvalida) as ctx:
                    compilar(expr)
                self.assertIn("tipo incorrecto", str(ctx.exception))
                self.assertIn("booleano", str(ctx.exception))

    def test_comparador_con_booleano(self) -> None:
        for expr in (":bug mayor 50", "10 menor :ui", ":a igual :b"):
            with self.subTest(expr=expr):
                with self.assertRaises(ConsultaInvalida) as ctx:
                    compilar(expr)
                self.assertIn("tipo incorrecto", str(ctx.exception))
                self.assertIn("entero", str(ctx.exception))


class TestEvaluacionEnMemoria(unittest.TestCase):
    """Evaluación semántica de ASTs sobre tareas."""

    def test_etiquetas_insensible_a_mayusculas(self) -> None:
        t = crear_tarea_en_memoria(etiquetas=("Bug", "UI"))
        self.assertTrue(compilar(":bug").evaluar(t))
        self.assertTrue(compilar(":BUG").evaluar(t))
        self.assertTrue(compilar(":ui").evaluar(t))
        self.assertFalse(compilar(":backend").evaluar(t))

    def test_etiquetada_y_cualquiera(self) -> None:
        con_etiquetas = crear_tarea_en_memoria(etiquetas=("doc",))
        sin_etiquetas = crear_tarea_en_memoria(etiquetas=())
        self.assertTrue(compilar("etiquetada").evaluar(con_etiquetas))
        self.assertFalse(compilar("etiquetada").evaluar(sin_etiquetas))
        self.assertTrue(compilar("cualquiera").evaluar(con_etiquetas))
        self.assertTrue(compilar("cualquiera").evaluar(sin_etiquetas))

    def test_comparacion_de_prioridad(self) -> None:
        t50 = crear_tarea_en_memoria(prioridad=50)
        self.assertTrue(compilar("prioridad mayor 40").evaluar(t50))
        self.assertTrue(compilar("prioridad desde 50").evaluar(t50))
        self.assertTrue(compilar("prioridad hasta 50").evaluar(t50))
        self.assertTrue(compilar("prioridad menor 100").evaluar(t50))
        self.assertTrue(compilar("prioridad igual 50").evaluar(t50))
        self.assertTrue(compilar("prioridad distinto 0").evaluar(t50))
        self.assertFalse(compilar("prioridad mayor 50").evaluar(t50))
        self.assertFalse(compilar("prioridad menor 50").evaluar(t50))

    def test_id_exacto(self) -> None:
        id_t = "20260915-120000-sensor"
        t = crear_tarea_en_memoria(ident=id_t)
        self.assertTrue(compilar(id_t).evaluar(t))
        self.assertFalse(compilar("20260915-120000-otro").evaluar(t))

    def test_explicar_emite_tokens_y_ast(self) -> None:
        c = compilar(":bug y prioridad mayor 50")
        expl = c.explicar()
        self.assertIn("TOKENS:", expl)
        self.assertIn("COMPILADO:", expl)
        self.assertIn(":bug", expl)
        self.assertIn("prioridad", expl)
        self.assertIn("mayor", expl)


class BaseCliTrackerTestCase(unittest.TestCase):
    """Arnés de integración para subprocesos sobre proyectos temporales."""

    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory(prefix="oracle-tql-tests-")
        self.addCleanup(self.td.cleanup)
        self.temporal = Path(self.td.name).resolve()
        self.raiz = self.temporal / "proyecto"
        (self.raiz / "tareas").mkdir(parents=True)
        self.env = {k: v for k, v in os.environ.items() if k != "ORACLE_PROYECTO"}
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"

        # Tareas de prueba con IDs deterministas:
        # T1: P90 [bug, urgente] (ABIERTA)
        # T2: P50 [bug] (ABIERTA)
        # T3: P50 sin etiquetas (ABIERTA)
        # T4: P10 [Scope] (CERRADA)
        self.t1 = "20260915-100001-t1"
        self.t2 = "20260915-100002-t2"
        self.t3 = "20260915-100003-t3"
        self.t4 = "20260915-100004-t4"

        for ident, prio, etiqs, est in [
            (self.t1, 90, "bug, urgente", "ABIERTA"),
            (self.t2, 50, "bug", "ABIERTA"),
            (self.t3, 50, "", "ABIERTA"),
            (self.t4, 10, "Scope", "CERRADA"),
        ]:
            carpeta = self.raiz / "tareas" / ident
            carpeta.mkdir(parents=True)
            contenido = (
                f"# Tarea {ident}\n\n"
                f"- ESTADO: {est}\n"
                f"- PRIORIDAD: {prio}\n"
                f"- ETIQUETAS: {etiqs}\n\n"
                f"Contenido de la tarea {ident}.\n"
            )
            (carpeta / "TAREA.md").write_text(contenido, encoding="utf-8")

    def run_cli(self, *args: str, cwd: Path | None = None, proyecto: bool = True) -> subprocess.CompletedProcess[str]:
        extra = ("--proyecto", str(self.raiz)) if proyecto else ()
        cmd = [sys.executable, "-B", str(CLI), "tarea", *args, *extra]
        return subprocess.run(
            cmd,
            env=self.env,
            capture_output=True,
            text=True,
            cwd=str(cwd or self.temporal),
            timeout=30,
        )

    def listar_ids(self, *args: str) -> list[str]:
        p = self.run_cli("listar", *args, "--json")
        self.assertEqual(p.returncode, 0, f"STDOUT: {p.stdout}\nSTDERR: {p.stderr}")
        data = json.loads(p.stdout)
        return [t["id"] for t in data]


class TestCliListarConsulta(BaseCliTrackerTestCase):
    """Pruebas del comando 'oracle tarea listar' con TQL y ordenamiento."""

    def test_listar_con_tql_filtra_abiertas(self) -> None:
        # Por defecto solo abiertas: t1 (P90) y t2 (P50) tienen 'bug'
        ids = self.listar_ids(":bug")
        self.assertEqual(ids, [self.t1, self.t2])

    def test_listar_con_tql_y_cerradas(self) -> None:
        # :scope coincide con 'Scope' (insensible a mayúsculas) en t4 cerrada
        ids = self.listar_ids(":scope", "--cerradas")
        self.assertEqual(ids, [self.t4])

    def test_listar_con_tql_y_todas(self) -> None:
        # palabra clave 'etiquetada' abarca t1, t2 y t4
        ids = self.listar_ids("etiquetada", "--todas")
        self.assertEqual(ids, [self.t1, self.t2, self.t4])

    def test_listar_negacion_y_prioridad(self) -> None:
        # no :urgente y prioridad desde 50 -> t2 y t3
        ids = self.listar_ids("no :urgente y prioridad desde 50")
        self.assertEqual(ids, [self.t2, self.t3])

    def test_listar_consulta_invalida_sale_codigo_2_sin_traceback(self) -> None:
        p = self.run_cli("listar", ":bug y")
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)
        self.assertIn("ERROR:", p.stderr)

    def test_listar_explicar_sale_0_sin_tracker(self) -> None:
        # Invocar --explicar en directorio vacío sin tracker
        vacio = self.temporal / "vacio"
        vacio.mkdir()
        p = self.run_cli("listar", ":bug y prioridad mayor 50", "--explicar", cwd=vacio, proyecto=False)
        self.assertEqual(p.returncode, 0, f"Error: {p.stderr}")
        self.assertIn("TOKENS:", p.stdout)
        self.assertIn("COMPILADO:", p.stdout)
        self.assertNotIn("20260915", p.stdout)

    def test_listar_orden_por_id_e_invertir(self) -> None:
        # Por defecto (prioridad desc, id asc): [t1, t2, t3]
        self.assertEqual(self.listar_ids(), [self.t1, self.t2, self.t3])

        # --por-id: ID descendente: [t3, t2, t1]
        self.assertEqual(self.listar_ids("--por-id"), [self.t3, self.t2, self.t1])

        # --invertir sobre defecto: [t3, t2, t1]
        self.assertEqual(self.listar_ids("--invertir"), [self.t3, self.t2, self.t1])

        # --por-id --invertir: ID ascendente: [t1, t2, t3]
        self.assertEqual(self.listar_ids("--por-id", "--invertir"), [self.t1, self.t2, self.t3])


class TestCliDesetiquetarConsulta(BaseCliTrackerTestCase):
    """Pruebas de 'oracle tarea desetiquetar --consulta'."""

    def obtener_etiquetas(self, ident: str) -> str:
        md = self.raiz / "tareas" / ident / "TAREA.md"
        for linea in md.read_text(encoding="utf-8").splitlines():
            if linea.startswith("- ETIQUETAS:"):
                return linea
        return ""

    def test_desetiquetar_por_consulta_respeta_condicion(self) -> None:
        # Quitar 'bug' solo en tareas que no tienen 'urgente' -> modifica t2, conserva t1
        p = self.run_cli("desetiquetar", "--etiqueta", "bug", "--consulta", ":bug y no :urgente")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.obtener_etiquetas(self.t1), "- ETIQUETAS: bug, urgente")
        self.assertEqual(self.obtener_etiquetas(self.t2).rstrip(), "- ETIQUETAS:")

    def test_desetiquetar_consulta_con_ids_sale_2(self) -> None:
        p = self.run_cli("desetiquetar", "--etiqueta", "bug", "--consulta", ":bug", self.t1)
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)

    def test_desetiquetar_consulta_invalida_no_escribe_y_sale_2(self) -> None:
        antes = {p: p.read_bytes() for p in self.raiz.rglob("*") if p.is_file()}
        p = self.run_cli("desetiquetar", "--etiqueta", "bug", "--consulta", ":bug o")
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)
        despues = {p: p.read_bytes() for p in self.raiz.rglob("*") if p.is_file()}
        self.assertEqual(antes, despues)


class TestCliReferenciasCwdEInit(BaseCliTrackerTestCase):
    """Pruebas de 'referencias' sin ID y 'init --sin-readme'."""

    def test_referencias_sin_id_desde_carpeta_de_tarea(self) -> None:
        # Crear mención de t1 en un archivo del proyecto
        (self.raiz / "modulo.py").write_text(f"# referencia a {self.t1}\n", encoding="utf-8")
        carpeta_t1 = self.raiz / "tareas" / self.t1
        sub_notas = carpeta_t1 / "notas"
        sub_notas.mkdir()

        # Desde la carpeta de la tarea
        p1 = self.run_cli("referencias", cwd=carpeta_t1, proyecto=False)
        self.assertEqual(p1.returncode, 0, p1.stdout + p1.stderr)
        self.assertIn("modulo.py", p1.stdout)

        # Desde un subdirectorio de la tarea
        p2 = self.run_cli("referencias", cwd=sub_notas, proyecto=False)
        self.assertEqual(p2.returncode, 0, p2.stdout + p2.stderr)
        self.assertIn("modulo.py", p2.stdout)

    def test_referencias_sin_id_fuera_de_tarea_sale_2(self) -> None:
        p = self.run_cli("referencias", cwd=self.raiz, proyecto=False)
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)
        self.assertIn("ERROR:", p.stderr)

    def test_init_sin_readme_y_auditoria(self) -> None:
        nuevo = self.temporal / "nuevo_repo"
        nuevo.mkdir()
        p_init = subprocess.run(
            [sys.executable, "-B", str(CLI), "tarea", "init", "--sin-readme", "--proyecto", str(nuevo)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(p_init.returncode, 0, p_init.stdout + p_init.stderr)
        self.assertTrue((nuevo / "tareas").is_dir())
        self.assertFalse((nuevo / "tareas" / "README.md").exists())

        # 'oracle tarea revisar' debe auditar con éxito (código 0)
        p_rev = subprocess.run(
            [sys.executable, "-B", str(CLI), "tarea", "revisar", "--proyecto", str(nuevo)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(p_rev.returncode, 0, p_rev.stdout + p_rev.stderr)


if __name__ == "__main__":
    unittest.main()
