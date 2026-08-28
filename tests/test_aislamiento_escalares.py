"""Contrato interno del sandbox de escalares externas.

Estas pruebas no intentan cerrar la fuga declarada de metadatos. Fijan la logica que decide que
eventos bloquea el audit hook, como clasifica escrituras y como termina el proceso trabajador.
"""

from __future__ import annotations

import contextlib
import io
import json
import math
import os
import selectors
import signal
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from nucleo import algebra


RAIZ = Path(__file__).resolve().parents[1]
modulo = None


def cargar_modulo():
    global modulo
    if modulo is None:
        try:
            from nucleo.aislamiento import escalares as escalares_modulo
        except SystemExit as e:
            raise AssertionError("importar el sandbox no debe ejecutar su main") from e
        modulo = escalares_modulo
    return modulo


class CanalFalso:
    def __init__(self, *, falla_al_escribir: BaseException | None = None) -> None:
        self.falla_al_escribir = falla_al_escribir
        self.escrito = ""
        self.flushes = 0
        self.cerrado = False

    def write(self, texto: str) -> int:
        if self.falla_al_escribir is not None:
            raise self.falla_al_escribir
        self.escrito += texto
        return len(texto)

    def flush(self) -> None:
        self.flushes += 1

    def close(self) -> None:
        self.cerrado = True


class StdoutFalso:
    def __init__(self, linea: str) -> None:
        self.linea = linea
        self.cerrado = False

    def readline(self) -> str:
        return self.linea

    def close(self) -> None:
        self.cerrado = True


class SelectorFalso:
    def __init__(self, eventos: list[object]) -> None:
        self.eventos = eventos
        self.timeout = None
        self.registrados: list[tuple[object, int]] = []
        self.cerrado = False

    def register(self, canal, evento) -> None:
        self.registrados.append((canal, evento))

    def select(self, timeout):
        self.timeout = timeout
        return self.eventos

    def close(self) -> None:
        self.cerrado = True


class ProcFalso:
    pid = 43210

    def __init__(self, *, poll=None, stdin=None, stdout=None, espera_timeout=False) -> None:
        self._poll = poll
        self.stdin = CanalFalso() if stdin is None else stdin
        self.stdout = CanalFalso() if stdout is None else stdout
        self.espera_timeout = espera_timeout
        self.waits: list[float] = []
        self.terminado = False
        self.matado = False

    def poll(self):
        return self._poll

    def wait(self, timeout=None):
        self.waits.append(timeout)
        if self.espera_timeout and len(self.waits) == 1:
            raise subprocess.TimeoutExpired(["trabajador"], timeout)
        return -signal.SIGKILL if self.matado else 0

    def terminate(self) -> None:
        self.terminado = True

    def kill(self) -> None:
        self.matado = True


class FinalizadorFalso:
    def __init__(self) -> None:
        self.detachado = False

    def detach(self) -> None:
        self.detachado = True


def proceso_vivo(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def terminar_subproceso(proc: subprocess.Popen) -> None:
    try:
        if proc.poll() is None:
            if os.name == "posix":
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
            with contextlib.suppress(subprocess.TimeoutExpired):
                proc.wait(timeout=5)
    finally:
        for canal in (proc.stdin, proc.stdout, proc.stderr):
            if canal is not None:
                with contextlib.suppress(OSError):
                    canal.close()


class AislamientoTestCase(unittest.TestCase):
    def setUp(self) -> None:
        cargar_modulo()


class HelpersTests(AislamientoTestCase):
    def test_00_timeout_y_raiz_oracle_son_el_contrato_publicado(self) -> None:
        self.assertEqual(modulo.RAIZ_ORACLE, RAIZ)
        self.assertEqual(modulo.TIEMPO_MAXIMO_SEGUNDOS, 10)

    def test_01_escalar_declarada_es_inmutable(self) -> None:
        declarada = modulo.EscalarDeclarada("n", "u", ("cm",), 0, 1, "p")

        with self.assertRaises(AttributeError):
            declarada.nombre = "otra"

    def test_02_dentro_de_devuelve_booleanos_exactos_y_falla_cerrado(self) -> None:
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as afuera:
            raiz = Path(td).resolve()
            interior = raiz / "archivo.txt"
            exterior = Path(afuera) / "archivo.txt"
            interior.write_text("x", encoding="utf-8")
            exterior.write_text("x", encoding="utf-8")

            self.assertIs(modulo._dentro_de(interior, raiz), True)
            self.assertIs(modulo._dentro_de(exterior, raiz), False)
            with mock.patch.object(
                    modulo.Path, "resolve", side_effect=OSError("sin permiso")):
                self.assertIs(modulo._dentro_de(interior, raiz), False)

    def test_03_escritura_reconoce_modos_y_banderas_sin_aceptar_extranos(self) -> None:
        for modo in ("w", "a", "x", "r+", "w+b"):
            with self.subTest(modo=modo):
                self.assertIs(modulo._escritura(modo, None), True)
        for modo in ("r", "rb", ""):
            with self.subTest(modo=modo):
                self.assertIs(modulo._escritura(modo, None), False)
        for bandera in (os.O_WRONLY, os.O_RDWR, os.O_CREAT, os.O_TRUNC, os.O_APPEND,
                        os.O_WRONLY | os.O_CREAT):
            with self.subTest(bandera=bandera):
                self.assertIs(modulo._escritura(None, bandera), True)
        self.assertIs(modulo._escritura(None, 0), False)
        self.assertIs(modulo._escritura(object(), None), False)

    def test_04_ruta_rechaza_descriptores_y_acepta_pathlike_no_enteros(self) -> None:
        class EnteroConRuta(int):
            def __fspath__(self):
                return "no_debe_usarse"

        class Ruta:
            def __fspath__(self):
                return "adentro.txt"

        self.assertIsNone(modulo._ruta(3))
        self.assertIsNone(modulo._ruta(None))
        self.assertIsNone(modulo._ruta(EnteroConRuta(1)))
        self.assertEqual(modulo._ruta("adentro.txt"), Path("adentro.txt"))
        self.assertEqual(modulo._ruta(Ruta()), Path("adentro.txt"))

    def test_05_enviar_emite_json_finito_con_unicode_sin_escape(self) -> None:
        salida = io.StringIO()

        with mock.patch.object(modulo.sys, "__stdout__", salida):
            modulo._enviar({"ok": True, "resultado": "senial ñ"})

        self.assertEqual(salida.getvalue(), '{"ok": true, "resultado": "senial ñ"}\n')
        with mock.patch.object(modulo.sys, "__stdout__", io.StringIO()):
            with self.assertRaises(ValueError):
                modulo._enviar({"ok": True, "resultado": math.nan})

    def test_06_respuesta_error_conserva_tipo_y_mensaje(self) -> None:
        self.assertEqual(
            modulo._respuesta_error(PermissionError("bloqueado")),
            {"ok": False, "tipo": "PermissionError", "mensaje": "bloqueado"},
        )

    def test_07_metadata_exige_el_decorador_y_devuelve_campos_exactos(self) -> None:
        def cruda():
            return None

        with self.assertRaisesRegex(RuntimeError, "@escalar"):
            modulo._metadata(cruda)

        registro = algebra.RegistroEscalares()
        with algebra.usar_registro(registro, procedencia="proyecto:/tmp/demo"):
            @algebra.escalar(
                "fijada",
                "unidad",
                unidades_argumentos=("sin_unidad", "unidad"),
            )
            def fijada(a, b=1):
                return a + b

        self.assertEqual(modulo._metadata(fijada), {
            "nombre": "fijada",
            "unidad": "unidad",
            "unidades_argumentos": ("sin_unidad", "unidad"),
            "aridad_min": 1,
            "aridad_max": 2,
            "procedencia": "proyecto:/tmp/demo",
        })

    def test_08_cargar_en_trabajador_exige_spec_y_loader_de_importlib(self) -> None:
        import importlib.util

        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            archivo = raiz / "escalares.py"
            archivo.write_text("", encoding="utf-8")

            with mock.patch.object(importlib.util, "spec_from_file_location", return_value=None):
                with self.assertRaisesRegex(RuntimeError, "preparar la carga"):
                    modulo._cargar_en_trabajador(raiz, archivo)

            spec_sin_loader = mock.Mock()
            spec_sin_loader.loader = None
            with mock.patch.object(
                    importlib.util, "spec_from_file_location", return_value=spec_sin_loader):
                with self.assertRaisesRegex(RuntimeError, "preparar la carga"):
                    modulo._cargar_en_trabajador(raiz, archivo)


class CierreProcesoTests(AislamientoTestCase):
    def test_10_cerrar_proceso_ignora_none_y_cierra_canales_de_un_proceso_terminado(self) -> None:
        modulo._cerrar_proceso(None)
        proc = ProcFalso(poll=0)

        with mock.patch.object(modulo.os, "killpg") as killpg:
            modulo._cerrar_proceso(proc)

        killpg.assert_not_called()
        self.assertEqual(proc.waits, [])
        self.assertTrue(proc.stdin.cerrado)
        self.assertTrue(proc.stdout.cerrado)

    def test_11_cerrar_proceso_posix_escala_de_sigterm_a_sigkill(self) -> None:
        proc = ProcFalso(poll=None, espera_timeout=True)

        with mock.patch.object(modulo.os, "killpg") as killpg:
            modulo._cerrar_proceso(proc)

        self.assertEqual(
            [llamada.args for llamada in killpg.call_args_list],
            [(proc.pid, signal.SIGTERM), (proc.pid, signal.SIGKILL)],
        )
        self.assertEqual(proc.waits, [1, 1])
        self.assertTrue(proc.stdin.cerrado)
        self.assertTrue(proc.stdout.cerrado)

    def test_12_cerrar_proceso_no_posix_usa_terminate_y_luego_kill(self) -> None:
        proc = ProcFalso(poll=None, espera_timeout=True)

        with mock.patch.object(modulo.os, "name", "nt"):
            modulo._cerrar_proceso(proc)

        self.assertTrue(proc.terminado)
        self.assertTrue(proc.matado)
        self.assertEqual(proc.waits, [1, 1])


class TrabajadorObjetoTests(AislamientoTestCase):
    def _trabajador(self) -> modulo.TrabajadorEscalares:
        return modulo.TrabajadorEscalares(Path("/tmp/proyecto"), Path("/tmp/proyecto/escalares.py"))

    def test_20_iniciar_configura_proceso_minimo_selector_y_metadata(self) -> None:
        stdout = CanalFalso()
        proc = ProcFalso(stdout=stdout)
        selector = SelectorFalso([])
        respuesta = {"ok": True, "escalares": [{
            "nombre": "demo", "unidad": "u", "unidades_argumentos": ["cm", "cm"], "aridad_min": 1,
            "aridad_max": 2, "procedencia": "proyecto:/tmp/proyecto",
        }]}

        with (mock.patch.object(modulo.subprocess, "Popen", return_value=proc) as popen,
              mock.patch.object(modulo.selectors, "DefaultSelector", return_value=selector),
              mock.patch.object(modulo.weakref, "finalize", return_value=FinalizadorFalso()),
              mock.patch.object(
                  modulo.TrabajadorEscalares, "_leer", return_value=respuesta)):
            declaradas = self._trabajador().iniciar()

        kwargs = popen.call_args.kwargs
        self.assertEqual(kwargs["cwd"], modulo.RAIZ_ORACLE)
        self.assertIs(kwargs["text"], True)
        self.assertEqual(kwargs["env"], {
            "PYTHONPATH": str(modulo.RAIZ_ORACLE),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONIOENCODING": "utf-8",
            "LC_ALL": "C.UTF-8",
            "LANG": "C.UTF-8",
        })
        self.assertIs(kwargs["start_new_session"], True)
        self.assertEqual(selector.registrados, [(stdout, selectors.EVENT_READ)])
        self.assertEqual(
            declaradas,
            (modulo.EscalarDeclarada(
                "demo", "u", ("cm", "cm"), 1, 2, "proyecto:/tmp/proyecto"
            ),),
        )

    def test_21_iniciar_falla_cerrado_si_no_hay_stdout_o_la_carga_responde_error(self) -> None:
        proc_sin_stdout = ProcFalso(stdout=None)
        proc_sin_stdout.stdout = None

        with (mock.patch.object(modulo.subprocess, "Popen", return_value=proc_sin_stdout),
              mock.patch.object(modulo.TrabajadorEscalares, "cerrar") as cerrar):
            with self.assertRaisesRegex(modulo.ErrorEscalarAislada, "canal"):
                self._trabajador().iniciar()
            cerrar.assert_called_once()

        proc = ProcFalso(stdout=CanalFalso())
        selector = SelectorFalso([])
        with (mock.patch.object(modulo.subprocess, "Popen", return_value=proc),
              mock.patch.object(modulo.selectors, "DefaultSelector", return_value=selector),
              mock.patch.object(modulo.weakref, "finalize", return_value=FinalizadorFalso()),
              mock.patch.object(
                  modulo.TrabajadorEscalares, "_leer",
                  return_value={"ok": False, "tipo": "CargaRota", "mensaje": "boom"}),
              mock.patch.object(modulo.TrabajadorEscalares, "cerrar") as cerrar):
            with self.assertRaisesRegex(modulo.ErrorEscalarAislada, "CargaRota: boom"):
                self._trabajador().iniciar()
            cerrar.assert_called_once()

    def test_22_llamar_valida_estado_argumentos_json_canal_y_respuesta(self) -> None:
        trabajador = self._trabajador()
        stdin = CanalFalso()
        trabajador._proc = ProcFalso(poll=None, stdin=stdin)

        with mock.patch.object(trabajador, "_leer", return_value={"ok": True, "resultado": "si"}):
            self.assertEqual(trabajador.llamar("eco", ("ñ", 2)), "si")

        self.assertNotIn("\\u00f1", stdin.escrito)
        self.assertEqual(
            json.loads(stdin.escrito),
            {"op": "llamar", "nombre": "eco", "argumentos": ["ñ", 2]},
        )
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "JSON finito"):
            trabajador.llamar("eco", (math.nan,))

        proc_sin_stdin = ProcFalso(poll=None)
        proc_sin_stdin.stdin = None
        for proc in (None, proc_sin_stdin, ProcFalso(poll=3)):
            otro = self._trabajador()
            otro._proc = proc
            with self.subTest(proc=proc), self.assertRaisesRegex(
                    algebra.ErrorDeAlgebra, "activo"):
                otro.llamar("eco", ())

        roto = self._trabajador()
        roto._proc = ProcFalso(poll=None, stdin=CanalFalso(
            falla_al_escribir=BrokenPipeError()))
        with self.assertRaisesRegex(algebra.ErrorDeAlgebra, "canal"):
            roto.llamar("eco", ())

        con_error = self._trabajador()
        con_error._proc = ProcFalso(poll=None)
        with mock.patch.object(
                con_error, "_leer",
                return_value={"ok": False, "tipo": "ValueError", "mensaje": "boom"}):
            with self.assertRaisesRegex(
                    algebra.ErrorDeAlgebra,
                    "externa .eco.: ValueError: boom"):
                con_error.llamar("eco", ())

    def test_23_cerrar_envia_orden_cierra_recursos_y_es_idempotente(self) -> None:
        trabajador = self._trabajador()
        proc = ProcFalso(poll=None)
        selector = SelectorFalso([])
        finalizador = FinalizadorFalso()
        trabajador._proc = proc
        trabajador._selector = selector
        trabajador._finalizador = finalizador
        modulo._TRABAJADORES.add(trabajador)

        with mock.patch.object(modulo, "_cerrar_proceso") as cerrar_proc:
            trabajador.cerrar()
            trabajador.cerrar()

        cerrar_proc.assert_called_once_with(proc)
        self.assertEqual(json.loads(proc.stdin.escrito), {"op": "cerrar"})
        self.assertEqual(proc.stdin.flushes, 1)
        self.assertTrue(selector.cerrado)
        self.assertIsNone(trabajador._selector)
        self.assertTrue(proc.stdin.cerrado)
        self.assertTrue(proc.stdout.cerrado)
        self.assertTrue(finalizador.detachado)
        self.assertIsNone(trabajador._proc)
        self.assertNotIn(trabajador, modulo._TRABAJADORES)

    def test_24_cerrar_no_escribe_orden_si_el_proceso_ya_no_esta_activo(self) -> None:
        trabajador = self._trabajador()
        proc = ProcFalso(poll=0)
        trabajador._proc = proc

        with mock.patch.object(modulo, "_cerrar_proceso") as cerrar_proc:
            trabajador.cerrar()

        cerrar_proc.assert_called_once_with(proc)
        self.assertEqual(proc.stdin.escrito, "")

    def test_25_leer_distingue_timeout_fin_de_canal_json_invalido_y_no_objeto(self) -> None:
        trabajador = self._trabajador()
        trabajador._proc = ProcFalso(stdout=StdoutFalso('{"ok": true, "valor": 1}\n'))
        selector = SelectorFalso([object()])
        trabajador._selector = selector
        self.assertEqual(trabajador._leer(), {"ok": True, "valor": 1})
        self.assertEqual(selector.timeout, 10)

        casos = (
            ([], '{"ok": true}\n', None, "respond"),
            ([object()], "", 7, "sin respuesta"),
            ([object()], "{roto\n", None, "datos"),
            ([object()], "[1]\n", None, "objeto JSON"),
        )
        for eventos, linea, codigo, mensaje in casos:
            otro = self._trabajador()
            otro._proc = ProcFalso(poll=codigo, stdout=StdoutFalso(linea))
            otro._selector = SelectorFalso(eventos)
            with self.subTest(mensaje=mensaje), mock.patch.object(otro, "cerrar") as cerrar:
                with self.assertRaisesRegex(modulo.ErrorEscalarAislada, mensaje):
                    otro._leer()
                cerrar.assert_called_once()

        proc_sin_stdout = ProcFalso()
        proc_sin_stdout.stdout = None
        for proc, selector in (
                (None, SelectorFalso([object()])),
                (proc_sin_stdout, SelectorFalso([object()])),
                (ProcFalso(stdout=StdoutFalso("{}\n")), None),
        ):
            otro = self._trabajador()
            otro._proc = proc
            otro._selector = selector
            with self.subTest(proc=proc, selector=selector), self.assertRaisesRegex(
                    modulo.ErrorEscalarAislada, "canal de lectura"):
                otro._leer()

    def test_26_registrar_escalares_instala_proxies_y_rechaza_repetidas(self) -> None:
        declarada = modulo.EscalarDeclarada(
            "externa", "u", ("sin_unidad", "cm"), 1, 2, "proyecto:/tmp/p"
        )
        trabajador = mock.Mock()
        trabajador.iniciar.return_value = (declarada,)
        registro = algebra.RegistroEscalares()

        with mock.patch.object(modulo, "TrabajadorEscalares", return_value=trabajador):
            devuelto = modulo.registrar_escalares_aisladas(
                Path("/tmp/p"), Path("/tmp/p/escalares.py"), registro)

        self.assertIs(devuelto, trabajador)
        proxy = registro["externa"]
        self.assertEqual(proxy.__name__, "externa")
        self.assertEqual(proxy.nombre_escalar, "externa")
        self.assertEqual(proxy.unidad, "u")
        self.assertEqual(proxy.unidades_argumentos, ("sin_unidad", "cm"))
        self.assertEqual((proxy.aridad_min, proxy.aridad_max), (1, 2))
        self.assertEqual(proxy.procedencia_escalar, "proyecto:/tmp/p")
        trabajador.llamar.return_value = 9
        self.assertEqual(proxy(4), 9)
        trabajador.llamar.assert_called_once_with("externa", (4,))

        repetido = mock.Mock()
        repetido.iniciar.return_value = (declarada,)
        with mock.patch.object(modulo, "TrabajadorEscalares", return_value=repetido):
            with self.assertRaisesRegex(modulo.ErrorEscalarAislada, "registros"):
                modulo.registrar_escalares_aisladas(
                    Path("/tmp/p"), Path("/tmp/p/escalares.py"),
                    algebra.RegistroEscalares({"externa": lambda: None}))
        repetido.cerrar.assert_called_once()


class SubprocesoTests(AislamientoTestCase):
    def _proyecto(self, raiz: Path, fuente: str) -> Path:
        (raiz / "catalogos").mkdir()
        archivo = raiz / "escalares.py"
        archivo.write_text(textwrap.dedent(fuente), encoding="utf-8")
        return archivo

    def _lanzar_trabajador(self, raiz: Path, archivo: Path) -> subprocess.Popen:
        entorno = os.environ.copy()
        entorno["PYTHONPATH"] = str(RAIZ)
        proc = subprocess.Popen(
            [sys.executable, "-B", "-m", "nucleo.aislamiento.escalares",
             "--trabajador", str(raiz), str(archivo)],
            cwd=RAIZ,
            env=entorno,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            start_new_session=(os.name == "posix"),
        )
        self.addCleanup(terminar_subproceso, proc)
        return proc

    def _leer_json(self, proc: subprocess.Popen, *, timeout: float = 5) -> dict:
        self.assertIsNotNone(proc.stdout)
        selector = selectors.DefaultSelector()
        try:
            selector.register(proc.stdout, selectors.EVENT_READ)
            eventos = selector.select(timeout)
        finally:
            selector.close()
        if not eventos:
            self.fail("el trabajador no emitio respuesta")
        linea = proc.stdout.readline()
        if not linea:
            stderr = proc.stderr.read() if proc.stderr is not None else ""
            self.fail(f"el trabajador termino sin JSON: {stderr}")
        return json.loads(linea)

    def _enviar(self, proc: subprocess.Popen, pedido) -> dict:
        self.assertIsNotNone(proc.stdin)
        proc.stdin.write(json.dumps(pedido, ensure_ascii=False, allow_nan=False) + "\n")
        proc.stdin.flush()
        return self._leer_json(proc)

    def test_30_worker_real_es_lider_de_grupo_y_cerrar_lo_deja_muerto(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            archivo = self._proyecto(raiz, """
                from nucleo.algebra import escalar

                @escalar("eco")
                def eco(valor=1):
                    return valor
            """)
            trabajador = modulo.TrabajadorEscalares(raiz.resolve(), archivo.resolve())
            self.addCleanup(trabajador.cerrar)
            declaradas = trabajador.iniciar()
            proc = trabajador._proc
            self.assertIsNotNone(proc)
            pid = proc.pid
            if os.name == "posix":
                self.assertEqual(os.getpgid(pid), pid)

            self.assertEqual([d.nombre for d in declaradas], ["eco"])
            self.assertEqual(trabajador.llamar("eco", (4,)), 4)
            trabajador.cerrar()
            self.assertFalse(proceso_vivo(pid))
            trabajador.cerrar()

    def test_31_worker_responde_llamadas_errores_no_json_no_finito_y_mensajes_rotos(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            archivo = self._proyecto(raiz, """
                from nucleo.algebra import escalar

                @escalar("eco")
                def eco(valor):
                    return valor + 1

                @escalar("revienta")
                def revienta():
                    raise ValueError("boom")

                @escalar("no_json")
                def no_json():
                    return {1, 2}

                @escalar("no_finito")
                def no_finito():
                    return float("nan")
            """)
            proc = self._lanzar_trabajador(raiz.resolve(), archivo.resolve())
            inicio = self._leer_json(proc)
            self.assertTrue(inicio["ok"])
            self.assertEqual(
                [e["nombre"] for e in inicio["escalares"]],
                ["eco", "revienta", "no_json", "no_finito"],
            )

            self.assertEqual(
                self._enviar(proc, {"op": "llamar", "nombre": "eco", "argumentos": [2]}),
                {"ok": True, "resultado": 3},
            )
            self.assertEqual(
                self._enviar(proc, {"op": "desconocida"})["tipo"],
                "ValueError",
            )
            self.assertEqual(
                self._enviar(proc, {"op": "llamar", "nombre": "ausente"})["tipo"],
                "KeyError",
            )
            self.assertEqual(
                self._enviar(proc, {"op": "llamar", "nombre": "revienta"})["tipo"],
                "ValueError",
            )
            self.assertEqual(
                self._enviar(proc, {"op": "llamar", "nombre": "no_json"})["tipo"],
                "TypeError",
            )
            self.assertEqual(
                self._enviar(proc, {"op": "llamar", "nombre": "no_finito"})["tipo"],
                "ValueError",
            )
            self.assertEqual(
                self._enviar(proc, {"op": "llamar", "nombre": "eco", "argumentos": [9]}),
                {"ok": True, "resultado": 10},
            )

            self.assertIsNotNone(proc.stdin)
            proc.stdin.write("{roto\n")
            proc.stdin.flush()
            self.assertEqual(self._leer_json(proc)["tipo"], "JSONDecodeError")
            proc.stdin.write(json.dumps({"op": "cerrar"}) + "\n")
            proc.stdin.flush()
            self.assertEqual(proc.wait(timeout=5), 0)

    def test_32_worker_informa_error_de_carga_y_uso_invalido(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            archivo = self._proyecto(raiz, "def rota(:\n")
            proc = self._lanzar_trabajador(raiz.resolve(), archivo.resolve())
            respuesta = self._leer_json(proc)
            self.assertFalse(respuesta["ok"])
            self.assertEqual(respuesta["tipo"], "SyntaxError")
            self.assertEqual(proc.wait(timeout=5), 1)

        invalido = subprocess.run(
            [sys.executable, "-B", "-m", "nucleo.aislamiento.escalares", "--trabajador"],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(invalido.returncode, 2)
        self.assertEqual(
            json.loads(invalido.stdout),
            {"ok": False, "tipo": "UsoInvalido", "mensaje": "faltan raíz y archivo"},
        )
        self.assertEqual(invalido.stderr, "")

        ayuda = subprocess.run(
            [sys.executable, "-B", "-m", "nucleo.aislamiento.escalares"],
            cwd=RAIZ,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(ayuda.returncode, 2)
        self.assertEqual(ayuda.stdout, "")
        self.assertIn("--trabajador <raiz> <archivo>", ayuda.stderr)

    def test_33_auditoria_decide_evento_y_polaridad_sin_instalarse_en_la_suite(self) -> None:
        codigo = r'''
import json
import os
import sys
from pathlib import Path

from nucleo.aislamiento.escalares import RAIZ_ORACLE, _instalar_auditoria

raiz = Path(sys.argv[1]).resolve()
afuera = Path(sys.argv[2]).resolve()
interno = raiz / "interno.txt"
externo = afuera / "externo.txt"
repo = RAIZ_ORACLE / "README.md"
_instalar_auditoria(raiz)

def probar(evento, *args):
    try:
        sys.audit(evento, *args)
    except BaseException as e:
        return type(e).__name__
    return "ok"

resultados = {
    "open_solo_ruta_dentro": probar("open", str(interno)),
    "open_lectura_dentro": probar("open", str(interno), "r", 0),
    "open_lectura_fuera": probar("open", str(externo), "r", 0),
    "open_escritura_dentro": probar("open", str(interno), "w", os.O_WRONLY),
    "open_repo_dos_args_escritura": probar("open", str(repo), "w"),
    "open_repo_banderas_escritura": probar("open", str(repo), "r", os.O_WRONLY),
    "listdir_dentro": probar("os.listdir", str(raiz)),
    "listdir_fuera": probar("os.listdir", str(afuera)),
    "scandir_dentro": probar("os.scandir", str(raiz)),
    "scandir_fuera": probar("os.scandir", str(afuera)),
    "chdir_dentro": probar("os.chdir", str(raiz)),
    "chdir_fuera": probar("os.chdir", str(afuera)),
    "rename_dentro_dos_rutas": probar("os.rename", str(raiz / "a"), str(raiz / "b")),
    "rename_dentro_ignora_dir_fd": probar("os.rename", str(raiz / "a"), str(raiz / "b"), str(afuera)),
    "rename_fuera_origen": probar("os.rename", str(afuera / "a"), str(raiz / "b")),
    "rename_fuera_destino": probar("os.rename", str(raiz / "a"), str(afuera / "b")),
    "copyfile_fuera": probar("shutil.copyfile", str(raiz / "a"), str(afuera / "b")),
    "mkdir_fuera": probar("os.mkdir", str(afuera / "nuevo")),
    "unlink_fuera": probar("os.unlink", str(afuera / "externo.txt")),
    "metadatos_fuera_declarados": probar("os.stat", str(externo)),
    "subprocess_bloqueado": probar("subprocess.Popen", "cmd"),
    "socket_bloqueado": probar("socket.__new__", "socket"),
    "import_ctypes": probar("import", "ctypes"),
    "import_math": probar("import", "math"),
}
sys.__stdout__.write(json.dumps(resultados, ensure_ascii=False, sort_keys=True))
'''
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as afuera:
            raiz = Path(td)
            exterior = Path(afuera)
            (raiz / "interno.txt").write_text("adentro", encoding="utf-8")
            (exterior / "externo.txt").write_text("afuera", encoding="utf-8")
            r = subprocess.run(
                [sys.executable, "-B", "-c", codigo, str(raiz), str(exterior)],
                cwd=RAIZ,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10,
            )

        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        resultados = json.loads(r.stdout)
        for nombre in (
                "open_solo_ruta_dentro", "open_lectura_dentro", "open_escritura_dentro",
                "listdir_dentro", "scandir_dentro", "chdir_dentro",
                "rename_dentro_dos_rutas", "rename_dentro_ignora_dir_fd",
                "metadatos_fuera_declarados", "import_math"):
            with self.subTest(nombre=nombre):
                self.assertEqual(resultados[nombre], "ok")
        for nombre in (
                "open_lectura_fuera", "open_repo_dos_args_escritura",
                "open_repo_banderas_escritura", "listdir_fuera", "scandir_fuera",
                "chdir_fuera", "rename_fuera_origen", "rename_fuera_destino",
                "copyfile_fuera", "mkdir_fuera", "unlink_fuera",
                "subprocess_bloqueado", "socket_bloqueado", "import_ctypes"):
            with self.subTest(nombre=nombre):
                self.assertEqual(resultados[nombre], "PermissionError")

    def test_34_ejecutar_trabajador_devuelve_enteros_y_prevalida_json_finito(self) -> None:
        codigo = r'''
import io
import json
import sys
from pathlib import Path

from nucleo.aislamiento import escalares as modulo

raiz = Path(sys.argv[1]).resolve()
archivo = Path(sys.argv[2]).resolve()
modo = sys.argv[3]
real_dumps = json.dumps
captura = io.StringIO()
stdout_real = sys.__stdout__
observados = []

if modo == "cerrar":
    sys.stdin = io.StringIO(real_dumps({"op": "cerrar"}) + "\n")
elif modo == "eof":
    sys.stdin = io.StringIO("")
elif modo == "unicode":
    def dumps_espiado(datos, *args, **kwargs):
        if datos == "ñ":
            observados.append(dict(kwargs))
        return real_dumps(datos, *args, **kwargs)

    modulo.json.dumps = dumps_espiado
    sys.stdin = io.StringIO(real_dumps(
        {"op": "llamar", "nombre": "unicode", "argumentos": []},
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n" + real_dumps({"op": "cerrar"}) + "\n")
else:
    raise AssertionError(modo)

sys.__stdout__ = captura
retorno = modulo._ejecutar_trabajador([str(raiz), str(archivo)])
sys.__stdout__ = stdout_real
stdout_real.write(real_dumps({
    "retorno": retorno,
    "observados": observados,
    "salida": captura.getvalue().splitlines(),
}, ensure_ascii=False, sort_keys=True))
'''
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            archivo = self._proyecto(raiz, """
                from nucleo.algebra import escalar

                @escalar("unicode")
                def unicode():
                    return "ñ"
            """)
            resultados = {}
            for modo in ("cerrar", "eof", "unicode"):
                r = subprocess.run(
                    [sys.executable, "-B", "-c", codigo, str(raiz), str(archivo), modo],
                    cwd=RAIZ,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=10,
                )
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                resultados[modo] = json.loads(r.stdout)

        self.assertEqual(resultados["cerrar"]["retorno"], 0)
        self.assertEqual(resultados["eof"]["retorno"], 0)
        self.assertEqual(resultados["unicode"]["retorno"], 0)
        self.assertEqual(
            resultados["unicode"]["observados"],
            [{"ensure_ascii": False, "allow_nan": False}],
        )
        self.assertEqual(len(resultados["cerrar"]["salida"]), 1)
        self.assertEqual(len(resultados["eof"]["salida"]), 1)
        self.assertEqual(json.loads(resultados["unicode"]["salida"][1]),
                         {"ok": True, "resultado": "ñ"})

    def test_90_cerrar_proceso_real_mata_grupo_que_ignora_sigterm(self) -> None:
        if os.name != "posix":
            self.skipTest("la escalada por grupo aplica a POSIX")
        codigo = (
            "import signal, sys, time\n"
            "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
            "print('listo', flush=True)\n"
            "while True: time.sleep(1)\n"
        )
        proc = subprocess.Popen(
            [sys.executable, "-B", "-c", codigo],
            cwd=RAIZ,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            start_new_session=True,
        )
        try:
            self.assertEqual(proc.stdout.readline().strip(), "listo")
            modulo._cerrar_proceso(proc)
            self.assertIsNotNone(proc.poll())
            self.assertFalse(proceso_vivo(proc.pid))
        finally:
            terminar_subproceso(proc)


if __name__ == "__main__":
    unittest.main()
