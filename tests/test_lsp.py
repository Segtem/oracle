"""Contrato del servidor LSP de diagnósticos."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from nucleo.proyecto import Proyecto
from tools import lsp


MEDIDA = """\
ninguno demo.alto:
    de pieza p
    donde p.alto > 400
    umbral <= 0 segun contrato porque "cuatro metros"
    alcance "no mira la malla"
"""

CASO = """\
caso 001-alto:
    fecha: "2026-08-31"
    origen:
        repo: "prueba/oracle"
        commit: "abc"
    procedencia: construida
    titulo: "Fija alto"
    etiqueta: verde_correcto
    sintoma:
        fija la medida
    como_se_detecto: observacion
    medida: demo.alto
    evidencia:
        pieza: id, alto
            "a", 401
    leccion:
        el alto importa
"""


def _proyecto(raiz: Path) -> tuple[Proyecto, Path]:
    (raiz / "catalogos" / "demo").mkdir(parents=True)
    (raiz / "corpus" / "demo").mkdir(parents=True)
    ruta = raiz / "catalogos" / "demo" / "demo.alto.oracle"
    ruta.write_text(MEDIDA, encoding="utf-8")
    return Proyecto(raiz), ruta


def _marco(mensaje: dict) -> bytes:
    cuerpo = json.dumps(mensaje, ensure_ascii=False).encode("utf-8")
    return f"Content-Length: {len(cuerpo)}\r\n\r\n".encode("ascii") + cuerpo


def _mensajes(datos: bytes) -> list[dict]:
    entrada = io.BytesIO(datos)
    salida = []
    while mensaje := lsp._leer_mensaje(entrada):
        salida.append(mensaje)
    return salida


class DiagnosticosTests(unittest.TestCase):
    def test_diagnostico_por_omision_empieza_en_cero(self) -> None:
        diagnostico = lsp._diagnostico("mal", 1)
        self.assertEqual(diagnostico["severity"], 1)
        self.assertEqual(diagnostico["range"], {
            "start": {"line": 0, "character": 0},
            "end": {"line": 0, "character": 1},
        })

    def test_error_sintactico_convierte_linea_y_columna_a_base_cero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            diagnosticos = lsp.diagnosticar(
                proy, ruta, MEDIDA.replace("donde p.alto", "donde p.@alto"))

        self.assertEqual(len(diagnosticos), 1)
        diagnostico = diagnosticos[0]
        self.assertEqual(diagnostico["severity"], 1)
        self.assertEqual(diagnostico["range"], {
            "start": {"line": 2, "character": 12},
            "end": {"line": 2, "character": 13},
        })
        self.assertIn("se esperaba", diagnostico["message"])

    def test_medida_mal_declarada_es_error_y_usa_la_ruta_del_nucleo(self) -> None:
        texto = MEDIDA.replace("ninguno demo.alto:", "medida demo.alto:").replace(
            "    resumen contar(1)\n", "")
        texto = texto.replace(
            "    umbral", "    resumen desconocido(p.alto)\n    umbral")
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            diagnostico, = lsp.diagnosticar(proy, ruta, texto)

        self.assertEqual(diagnostico["severity"], 1)
        # ErrorDeAlgebra no trae ruta para el nombre de un agregado desconocido.
        self.assertEqual(diagnostico["range"]["start"], {"line": 0, "character": 0})
        self.assertIn("desconocido", diagnostico["message"])

    def test_caso_mal_escrito_es_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, _ruta = _proyecto(Path(td))
            ruta = proy.corpus / "demo" / "001-alto.caso"
            diagnostico, = lsp.diagnosticar(
                proy, ruta, CASO.replace("etiqueta: verde_correcto", "etiqueta: inventada"))

        self.assertEqual(diagnostico["severity"], 1)
        self.assertEqual(diagnostico["range"]["start"]["line"], 7)
        self.assertIn("etiqueta en", diagnostico["message"])

    def test_medida_sin_caso_publica_aviso_sobre_el_id(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            diagnostico, = lsp.diagnosticar(proy, ruta, MEDIDA)

        self.assertEqual(diagnostico["severity"], 2)
        self.assertEqual(diagnostico["range"]["start"], {"line": 0, "character": 8})
        self.assertEqual(
            diagnostico["message"], "SIN FIJAR — ninguna evidencia la pone a prueba")

    def test_un_caso_que_la_nombra_quita_sin_fijar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            (proy.corpus / "demo" / "001-alto.caso").write_text(CASO, encoding="utf-8")
            self.assertEqual(lsp.diagnosticar(proy, ruta, MEDIDA), [])

    def test_caso_valido_y_extension_ajena_no_producen_diagnosticos(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, _ruta = _proyecto(Path(td))
            self.assertEqual(
                lsp.diagnosticar(proy, proy.corpus / "demo" / "001-alto.caso", CASO), [])
            self.assertEqual(lsp.diagnosticar(proy, proy.raiz / "nota.txt", "mal"), [])

    def test_error_al_cargar_macros_del_proyecto_falla_en_el_inicio(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            (proy.raiz / "macros").mkdir()
            (proy.raiz / "macros" / "rota.oracle").write_text("esto no es una macro\n")
            diagnostico, = lsp.diagnosticar(proy, ruta, MEDIDA)

        self.assertEqual(diagnostico["severity"], 1)
        self.assertEqual(diagnostico["range"]["start"], {"line": 0, "character": 0})
        self.assertIn("rota.oracle", diagnostico["message"])

    def test_una_medida_del_lenguaje_evaluada_aparte_no_se_marca(self) -> None:
        texto = MEDIDA.replace("de pieza p", "de medida p").replace(
            "p.alto > 400", "p.es_meta == false")
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            self.assertEqual(lsp.diagnosticar(proy, ruta, texto), [])

    def test_archivo_fuera_del_catalogo_no_se_declara_sin_fijar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, _ruta = _proyecto(Path(td))
            self.assertEqual(lsp.diagnosticar(proy, proy.raiz / "borrador.oracle", MEDIDA), [])


class ProtocoloTests(unittest.TestCase):
    def test_initialize_declara_solo_sincronizacion_y_diagnosticos_push(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            entrada = b"".join((
                _marco({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}),
                _marco({"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": {
                    "textDocument": {"uri": ruta.as_uri(), "version": 3, "text": MEDIDA}}}),
                _marco({"jsonrpc": "2.0", "id": 2, "method": "shutdown"}),
                _marco({"jsonrpc": "2.0", "method": "exit"}),
            ))
            salida = io.BytesIO()
            self.assertEqual(lsp.servir(proy, io.BytesIO(entrada), salida), 0)

        respuestas = _mensajes(salida.getvalue())
        self.assertEqual(respuestas[0], {
            "jsonrpc": "2.0", "id": 1,
            "result": {"capabilities": {
                "textDocumentSync": {"openClose": True, "change": 1}}},
        })
        publicacion = respuestas[1]
        self.assertEqual(publicacion["method"], "textDocument/publishDiagnostics")
        self.assertEqual(publicacion["params"]["uri"], ruta.as_uri())
        self.assertEqual(publicacion["params"]["version"], 3)
        self.assertEqual(publicacion["params"]["diagnostics"][0]["severity"], 2)
        self.assertEqual(respuestas[2], {"jsonrpc": "2.0", "id": 2, "result": None})

    def test_did_change_exige_texto_completo_y_did_close_limpia(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            salida = io.BytesIO()
            servidor = lsp.Servidor(proy, salida)
            servidor.manejar({
                "method": "textDocument/didChange",
                "params": {"textDocument": {"uri": ruta.as_uri(), "version": 4},
                           "contentChanges": [{"text": "mal"}]},
            })
            servidor.manejar({
                "method": "textDocument/didClose",
                "params": {"textDocument": {"uri": ruta.as_uri()}},
            })

        publicaciones = _mensajes(salida.getvalue())
        self.assertEqual(publicaciones[0]["params"]["version"], 4)
        self.assertEqual(publicaciones[0]["params"]["diagnostics"][0]["severity"], 1)
        self.assertEqual(publicaciones[1]["params"], {
            "uri": ruta.as_uri(), "diagnostics": []})

        with self.assertRaisesRegex(ValueError, "texto completo"):
            servidor.manejar({
                "method": "textDocument/didChange",
                "params": {"textDocument": {"uri": ruta.as_uri()},
                           "contentChanges": [{"range": {}, "text": MEDIDA}]},
            })

    def test_longitud_cuenta_bytes_utf8_y_rechaza_mensajes_truncados(self) -> None:
        salida = io.BytesIO()
        lsp._enviar(salida, {"mensaje": "línea"})
        self.assertEqual(_mensajes(salida.getvalue()), [{"mensaje": "línea"}])

        with self.assertRaisesRegex(EOFError, "cuerpo"):
            lsp._leer_mensaje(io.BytesIO(b"Content-Length: 4\r\n\r\n{}"))

    def test_request_desconocido_recibe_method_not_found_y_exit_sin_shutdown_falla(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, _ruta = _proyecto(Path(td))
            salida = io.BytesIO()
            servidor = lsp.Servidor(proy, salida)
            self.assertTrue(servidor.manejar({"id": 9, "method": "textDocument/hover"}))
            self.assertEqual(_mensajes(salida.getvalue())[0]["error"]["code"], -32601)
            self.assertIs(servidor.manejar({"method": "exit"}), False)

            entrada = io.BytesIO(_marco({"method": "exit"}))
            self.assertEqual(lsp.servir(proy, entrada, io.BytesIO()), 1)

    def test_uri_no_file_falla_cerrado(self) -> None:
        for uri in ("https:/medida.oracle", "file://remoto/medida.oracle"):
            with self.subTest(uri=uri), self.assertRaisesRegex(ValueError, "URI de archivo"):
                lsp._ruta_de_uri(uri)

    def test_entrypoint_corre_desde_el_proyecto_sin_depender_de_pythonpath(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, _ruta = _proyecto(Path(td))
            entrada = b"".join((
                _marco({"id": 1, "method": "initialize"}),
                _marco({"method": "textDocument/didOpen", "params": {"textDocument": {
                    "uri": (proy.catalogos / "demo" / "demo.alto.oracle").as_uri(),
                    "text": MEDIDA}}}),
                _marco({"id": 2, "method": "shutdown"}),
                _marco({"method": "exit"}),
            ))
            resultado = subprocess.run(
                [sys.executable, str(lsp.RAIZ / "tools" / "lsp.py"),
                 "--proyecto", str(proy.raiz)],
                input=entrada, capture_output=True, cwd=proy.raiz.parent,
            )

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        mensajes = _mensajes(resultado.stdout)
        self.assertEqual([m.get("id") for m in mensajes], [1, None, 2])
        self.assertEqual(mensajes[1]["params"]["diagnostics"][0]["severity"], 2)

    def test_main_propaga_argumentos_y_falla_si_no_resuelve_proyecto(self) -> None:
        with mock.patch.object(lsp, "resolver_cli", return_value=None) as resolver:
            self.assertEqual(lsp.main([]), 1)
        resolver.assert_called_once_with([])


if __name__ == "__main__":
    unittest.main()
