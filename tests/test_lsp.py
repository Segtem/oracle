"""Contrato del servidor LSP de diagnósticos y completado."""

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
from tools.sesion import resolver_cli


MEDIDA = """\
ninguno demo.alto:
    de pieza p
    donde p.alto > 400
    umbral <= 0 segun contrato porque "cuatro metros"
    ambito universal
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
    (raiz / "relaciones").mkdir()
    (raiz / "relaciones" / "pieza.json").write_text(json.dumps([
        "relacion", "pieza", ["campos",
            ["campo", "id", "texto", "sin_unidad"],
            ["campo", "alto", "flotante", "cm"],
            ["campo", "yaw", "flotante", "grados"]],
        ["alcance", "NO lee la malla"],
    ]), encoding="utf-8")
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


def _posicion(texto: str, aguja: str) -> dict:
    indice = texto.index(aguja) + len(aguja)
    antes = texto[:indice]
    linea = antes.count("\n")
    prefijo = antes.rsplit("\n", 1)[-1]
    return {"line": linea, "character": len(prefijo.encode("utf-16-le")) // 2}


class DiagnosticosTests(unittest.TestCase):
    def test_diagnostico_por_omision_empieza_en_cero(self) -> None:
        diagnostico = lsp._diagnostico("ninguno demo.x:", "mal", 1)
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
        self.assertIn("se esperaba una etiqueta declarada", diagnostico["message"])
        # El diagnóstico del editor lleva el significado: es donde más sirve, porque
        # se lee sin salir del archivo que se está escribiendo.
        self.assertIn("falso_verde: la medida pasó y no debía", diagnostico["message"])

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


class CompletadoTests(unittest.TestCase):
    def test_conjuntos_cerrados_salen_del_nucleo(self) -> None:
        from nucleo.caso import DETECCIONES, ETIQUETAS, PROCEDENCIAS
        from nucleo.medida import ORIGENES_DE_UMBRAL

        contextos = (
            ("etiqueta: ", ETIQUETAS),
            ("procedencia: con", PROCEDENCIAS),
            ("como_se_detecto: ", DETECCIONES),
        )
        with tempfile.TemporaryDirectory() as td:
            proy, _ruta = _proyecto(Path(td))
            for linea, esperados in contextos:
                with self.subTest(linea=linea):
                    items = lsp.completar(
                        proy, proy.corpus / "demo" / "nuevo.caso", linea,
                        _posicion(linea, linea))
                    self.assertEqual([item["label"] for item in items], sorted(esperados))

            linea = "    umbral <= 0 segun con"
            items = lsp.completar(
                proy, proy.catalogos / "demo" / "nuevo.oracle", linea,
                _posicion(linea, linea))
            self.assertEqual(
                [item["label"] for item in items], sorted(ORIGENES_DE_UMBRAL))

    def test_relaciones_documentan_alcance_y_campos_muestran_tipo_y_unidad(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            linea_de = "    de pie"
            self.assertEqual(lsp.completar(
                proy, ruta, linea_de, _posicion(linea_de, linea_de)), [{
                    "label": "pieza", "documentation": "NO lee la malla"}])

            incompleta = MEDIDA.replace("donde p.alto > 400", "donde p.")
            items = lsp.completar(proy, ruta, incompleta, _posicion(incompleta, "p."))

        self.assertEqual(items, [
            {"label": "id", "detail": "texto · sin_unidad"},
            {"label": "alto", "detail": "flotante · cm"},
            {"label": "yaw", "detail": "flotante · grados"},
        ])

    def test_alias_de_unir_resuelve_su_propia_relacion(self) -> None:
        texto = """\
medida demo.alto:
    de pieza p
    unir evento e
    donde e.
    resumen contar(1)
    umbral <= 0 segun contrato porque "cuatro metros"
    alcance "no mira la malla"
"""
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            (proy.raiz / "relaciones" / "evento.json").write_text(json.dumps([
                "relacion", "evento", ["campos",
                    ["campo", "t", "entero", "pasos"]],
                ["alcance", "NO ve eventos omitidos"],
            ]), encoding="utf-8")
            items = lsp.completar(proy, ruta, texto, _posicion(texto, "e."))

        self.assertEqual(items, [{"label": "t", "detail": "entero · pasos"}])

    def test_caso_ofrece_ids_del_catalogo_cargado(self) -> None:
        texto = "    medida: demo."
        with tempfile.TemporaryDirectory() as td:
            proy, _ruta = _proyecto(Path(td))
            items = lsp.completar(
                proy, proy.corpus / "demo" / "nuevo.caso", texto,
                _posicion(texto, texto))
        self.assertEqual(items, [{"label": "demo.alto"}])

    def test_no_completa_prosa_ni_inventa_un_umbral(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            porque = MEDIDA.replace('porque "cuatro metros"', 'porque "p.')
            alcance = MEDIDA.replace('alcance "no mira la malla"', 'alcance "p.')
            self.assertEqual(lsp.completar(
                proy, ruta, porque, _posicion(porque, 'porque "p.')), [])
            self.assertEqual(lsp.completar(
                proy, ruta, alcance, _posicion(alcance, 'alcance "p.')), [])
            umbral = "    umbral <= "
            self.assertEqual(lsp.completar(
                proy, ruta, umbral, _posicion(umbral, umbral)), [])

    def test_contextos_ajenos_e_incompletos_devuelven_lista_vacia(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            caso = proy.corpus / "demo" / "nuevo.caso"
            self.assertEqual(lsp.completar(
                proy, caso, "    titulo: ", {"line": 0, "character": 12}), [])
            self.assertEqual(lsp.completar(
                proy, proy.raiz / "nota.txt", "    de ",
                {"line": 0, "character": 7}), [])
            rota = MEDIDA.replace("donde p.alto > 400", "donde p.").replace(
                "    umbral", "    linea inválida\n    umbral")
            self.assertEqual(lsp.completar(
                proy, ruta, rota, _posicion(rota, "p.")), [])

    def test_errores_de_declaraciones_y_relacion_no_declarada_no_completan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            caso = proy.corpus / "demo" / "nuevo.caso"
            ruta.write_text("medida rota", encoding="utf-8")
            self.assertEqual(lsp.completar(
                proy, caso, "    medida: ", {"line": 0, "character": 12}), [])

        sin_declarar = MEDIDA.replace("de pieza p", "de fantasma p").replace(
            "donde p.alto > 400", "donde p.")
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            self.assertEqual(lsp.completar(
                proy, ruta, sin_declarar, _posicion(sin_declarar, "p.")), [])

        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            (proy.raiz / "relaciones" / "pieza.json").write_text("mal", encoding="utf-8")
            self.assertEqual(lsp.completar(
                proy, ruta, "    de ", {"line": 0, "character": 7}), [])
            incompleta = MEDIDA.replace("donde p.alto > 400", "donde p.")
            self.assertEqual(lsp.completar(
                proy, ruta, incompleta, _posicion(incompleta, "p.")), [])

    def test_posicion_lsp_cuenta_utf16(self) -> None:
        prefijo, indice = lsp._contexto("😀 etiqueta: ", {"line": 0, "character": 13})
        self.assertEqual(prefijo, "😀 etiqueta: ")
        self.assertEqual(indice, 12)

        prefijo, indice = lsp._contexto("\uffffx", {"line": 0, "character": 1})
        self.assertEqual((prefijo, indice), ("\uffff", 1))
        prefijo, indice = lsp._contexto("\U00010000x", {"line": 0, "character": 2})
        self.assertEqual((prefijo, indice), ("\U00010000", 1))


class ProtocoloTests(unittest.TestCase):
    def test_initialize_declara_sincronizacion_diagnosticos_completado_y_lens(self) -> None:
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
                "textDocumentSync": {"openClose": True, "change": 1},
                "completionProvider": {"triggerCharacters": ["."]},
                "codeLensProvider": {"resolveProvider": False}}},
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

    def test_completion_usa_el_texto_abierto_actualizado_y_cerrar_lo_descarta(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            salida = io.BytesIO()
            servidor = lsp.Servidor(proy, salida)
            servidor.manejar({
                "method": "textDocument/didOpen", "params": {"textDocument": {
                    "uri": ruta.as_uri(), "text": "    de ", "version": 1}}})
            servidor.manejar({
                "method": "textDocument/didChange", "params": {
                    "textDocument": {"uri": ruta.as_uri(), "version": 2},
                    "contentChanges": [{"text": "    de pie"}]}})
            servidor.manejar({
                "id": 7, "method": "textDocument/completion", "params": {
                    "textDocument": {"uri": ruta.as_uri()},
                    "position": {"line": 0, "character": 10}}})
            servidor.manejar({
                "method": "textDocument/didClose",
                "params": {"textDocument": {"uri": ruta.as_uri()}}})
            servidor.manejar({
                "id": 8, "method": "textDocument/completion", "params": {
                    "textDocument": {"uri": ruta.as_uri()},
                    "position": {"line": 0, "character": 10}}})

        mensajes = _mensajes(salida.getvalue())
        respuestas = {mensaje["id"]: mensaje["result"] for mensaje in mensajes if "id" in mensaje}
        self.assertEqual(respuestas[7], [{
            "label": "pieza", "documentation": "NO lee la malla"}])
        self.assertEqual(respuestas[8], [])

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

    def test_code_lens_viaja_por_el_protocolo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            uri = ruta.as_uri()
            entrada = b"".join((
                _marco({"id": 1, "method": "initialize", "params": {}}),
                _marco({"method": "textDocument/didOpen", "params": {"textDocument": {
                    "uri": uri, "text": MEDIDA}}}),
                _marco({"id": 2, "method": "textDocument/codeLens",
                        "params": {"textDocument": {"uri": uri}}}),
                _marco({"id": 3, "method": "textDocument/codeLens",
                        "params": {"textDocument": {"uri": "file:///no/abierto.oracle"}}}),
                _marco({"id": 4, "method": "shutdown"}),
                _marco({"method": "exit"}),
            ))
            salida = io.BytesIO()
            self.assertEqual(lsp.servir(proy, io.BytesIO(entrada), salida), 0)

        por_id = {m.get("id"): m for m in _mensajes(salida.getvalue()) if "id" in m}
        self.assertIn("codeLensProvider", por_id[1]["result"]["capabilities"])
        self.assertIn("SIN FIJAR", por_id[2]["result"][0]["command"]["title"])
        # Un documento que el servidor no tiene abierto no se lee del disco a escondidas.
        self.assertEqual(por_id[3]["result"], [])

    def test_main_propaga_argumentos_y_falla_si_no_resuelve_proyecto(self) -> None:
        with mock.patch.object(lsp, "resolver_cli", return_value=None) as resolver:
            self.assertEqual(lsp.main([]), 1)
        resolver.assert_called_once_with([])


class RangoConAncho(unittest.TestCase):
    """Un rango de ancho cero es legal y no se ve. Acá se exige que nunca salga uno.

    El editor recorta la posición contra el fin de la línea, así que un error que
    señala «acá faltaba algo» al final de una línea produce un rango vacío: se
    cuenta en la lista de problemas y en la regla lateral, y en el texto no se
    dibuja nada. Se midió en VS Code sobre `umbral <= 0` —15 caracteres, error en
    la columna 16— y el subrayado no aparecía.
    """

    def test_una_columna_dentro_de_la_linea_marca_ese_caracter(self) -> None:
        rango = lsp._rango("de pieza p\ndonde p.oz > 4\n", 2, 7)
        self.assertEqual(rango, {"start": {"line": 1, "character": 6},
                                 "end": {"line": 1, "character": 7}})

    def test_una_columna_pasada_del_fin_marca_la_linea_sin_sangria(self) -> None:
        texto = 'ninguno aula.rota:\n    umbral <= 0\n'
        rango = lsp._rango(texto, 2, 16)
        self.assertEqual(rango, {"start": {"line": 1, "character": 4},
                                 "end": {"line": 1, "character": 15}})

    def test_sobre_una_linea_en_blanco_sube_a_la_ultima_con_contenido(self) -> None:
        texto = "ninguno demo.x:\n    de pieza p\n\n\n"
        rango = lsp._rango(texto, 4, 1)
        self.assertEqual(rango, {"start": {"line": 1, "character": 4},
                                 "end": {"line": 1, "character": 14}})

    def test_una_linea_mas_alla_del_final_no_revienta(self) -> None:
        rango = lsp._rango("de pieza p\n", 99, 99)
        self.assertEqual(rango["start"]["line"], 0)
        self.assertGreater(rango["end"]["character"], rango["start"]["character"])

    def test_un_archivo_vacio_da_un_rango_de_ancho_uno(self) -> None:
        rango = lsp._rango("", 1, 1)
        self.assertEqual(rango, {"start": {"line": 0, "character": 0},
                                 "end": {"line": 0, "character": 1}})

    def test_ningun_diagnostico_del_servidor_sale_con_ancho_cero(self) -> None:
        rotas = [
            'ninguno aula.rota:\n    de pieza p\n    donde p.oz > 400.0\n'
            '    umbral <= 0\n    alcance "no ve la malla"\n',
            "ninguno\n",
            'ninguno demo.x:\n    de pieza p\n    umbral <= 0 segun contrato\n',
        ]
        with tempfile.TemporaryDirectory() as tmp:
            proy, _r = _proyecto(Path(tmp))
            for i, texto in enumerate(rotas):
                ruta = proy.catalogos / "demo" / f"rota{i}.oracle"
                with self.subTest(medida=i):
                    diagnosticos = lsp.diagnosticar(proy, ruta, texto)
                    self.assertTrue(diagnosticos, "esta medida tenía que fallar")
                    for d in diagnosticos:
                        inicio, fin = d["range"]["start"], d["range"]["end"]
                        self.assertGreater(
                            (fin["line"], fin["character"]),
                            (inicio["line"], inicio["character"]),
                            f"rango vacío: {d}")


class SinFijarLoDecideLaMedida(unittest.TestCase):
    """El aviso «SIN FIJAR» es el veredicto de `meta.toda_medida_esta_ejercitada`, no un cálculo
    propio del servidor.

    Antes acá había un `any(caso["medida"] == mid for caso in casos)` que decía en Python lo mismo
    que esa medida dice en Oracle. Las dos coincidían, hasta que dejaran de hacerlo: la medida
    cuenta los casos que aportan los fixtures diferenciales —`tools/mutar.py` los suma al listado,
    y su docstring avisa que «las medidas fijadas por un diferencial pueden no aparecer en el
    corpus»— y aquella línea no los miraba. Una medida así salía amarilla en el editor y verde en
    la aceptación, sin que nada señalara la contradicción.
    """

    def _con_diferencial(self, raiz: Path, mid: str) -> None:
        """Escribe un fixture diferencial FRESCO que fija `mid`, sin ningún caso en el corpus."""
        from nucleo import fixtures as fx
        from nucleo.medida import cargar as cargar_medida
        from nucleo.proyecto import macros_del_proyecto

        proy = Proyecto(raiz)
        medida = cargar_medida(raiz / "catalogos" / "demo" / "demo.alto.oracle",
                               macros=macros_del_proyecto(proy))
        (raiz / "diferencial").mkdir(exist_ok=True)
        (raiz / "emisor.py").write_text("# el generador\n", encoding="utf-8")
        (raiz / "referencia.py").write_text("# la reimplementación\n", encoding="utf-8")
        configuracion = {"dominio": "demo"}
        datos = {
            "esquema": fx.ESQUEMA_DIFERENCIAL,
            "origen": "escrito a mano para esta prueba",
            "mundos": 2,
            "frescura": {
                "algoritmo": fx.ALGORITMO_HUELLA,
                "raiz_fuentes": ".",
                "configuracion": configuracion,
                "fuentes": {"emisor": ["emisor.py"], "referencia": ["referencia.py"]},
                "huellas": {
                    "catalogo": fx.huella_catalogo([medida]),
                    "configuracion": fx.huella_datos(configuracion),
                    "emisor": fx.huella_archivos(raiz, ["emisor.py"]),
                    "referencia": fx.huella_archivos(raiz, ["referencia.py"]),
                },
            },
            "grupos": {mid: [
                {"esperado_ok": True,
                 "evidencia": {"pieza": [{"id": "p1", "alto": 10.0, "yaw": 0.0}]}},
                {"esperado_ok": False,
                 "evidencia": {"pieza": [{"id": "p2", "alto": 900.0, "yaw": 0.0}]}},
            ]},
        }
        ruta = raiz / "diferencial" / "demo.json"
        ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(fx.validar_fixture(datos, "demo.json"), [],
                         "el fixture de la prueba tiene que ser válido")

    def test_sin_corpus_ni_diferencial_avisa(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            diag = lsp.diagnosticar(proy, ruta, MEDIDA)
            self.assertEqual([d["message"][:9] for d in diag], ["SIN FIJAR"])
            self.assertEqual(diag[0]["severity"], 2)

    def test_una_medida_que_fija_solo_un_diferencial_no_sale_sin_fijar(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            proy, ruta = _proyecto(raiz)
            self.assertTrue(lsp.diagnosticar(proy, ruta, MEDIDA), "control: sin fixture, avisa")
            self._con_diferencial(raiz, "demo.alto")
            self.assertEqual(lsp.diagnosticar(Proyecto(raiz), ruta, MEDIDA), [])

    def test_si_el_diferencial_esta_vencido_el_aviso_dice_que_no_lo_pudo_leer(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            proy, ruta = _proyecto(raiz)
            self._con_diferencial(raiz, "demo.alto")
            (raiz / "referencia.py").write_text("# otra cosa\n", encoding="utf-8")
            diag = lsp.diagnosticar(Proyecto(raiz), ruta, MEDIDA)
            self.assertEqual(len(diag), 1)
            self.assertIn("no se pudieron leer los diferenciales", diag[0]["message"].lower())

    def test_sin_la_medida_jueza_no_se_inventa_un_veredicto(self) -> None:
        """Sin jueza no hay aviso. El servidor no tiene una segunda definición de guardia."""
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            with mock.patch.object(lsp, "esta_ejercitada", return_value=(None, True)):
                self.assertEqual(lsp.diagnosticar(proy, ruta, MEDIDA), [])


class LenteSobreLaMedida(unittest.TestCase):
    """La línea que el editor dibuja arriba de la medida.

    Es la misma vista que `tools/medida.py --listar`, armada con `texto_de_fijacion`: el editor no
    tiene una segunda opinión sobre cuándo una medida está ejercitada.
    """

    def test_dice_fijacion_polaridad_y_umbral(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            (proy.corpus / "demo" / "001.caso").write_text(CASO, encoding="utf-8")
            lente, = lsp.lentes(proy, ruta, MEDIDA)
            self.assertEqual(lente["command"]["title"],
                             "1 caso · 1 verde · 0 rojos · umbral <= 0 segun contrato")

    def test_se_ancla_en_la_linea_del_id_y_en_la_columna_cero(self) -> None:
        """El rango entero, no sólo la línea.

        La columna no la mira ninguno de los dos editores —dibujan el lens sobre la línea y
        listo—, así que un cambio ahí no rompe nada visible y por eso ningún test lo notaba. Pero
        el rango es parte de lo que sale por el protocolo, y un tercer cliente sí podría usarlo:
        el contrato se fija acá en vez de declararlo inobservable.
        """
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            lente, = lsp.lentes(proy, ruta, "# un comentario\n\n" + MEDIDA)
            self.assertEqual(lente["range"], {"start": {"line": 2, "character": 0},
                                              "end": {"line": 2, "character": 0}})

    def test_una_medida_sin_evidencia_avisa_en_el_lens(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            lente, = lsp.lentes(proy, ruta, MEDIDA)
            self.assertIn("SIN FIJAR", lente["command"]["title"])

    def _con_casos(self, proy, *etiquetas) -> None:
        """Escribe un caso por etiqueta, con id propio, todos sobre `demo.alto`."""
        for i, etiqueta in enumerate(etiquetas):
            texto = (CASO.replace("etiqueta: verde_correcto", f"etiqueta: {etiqueta}")
                         .replace("caso 001-alto:", f"caso 00{i + 1}-alto:"))
            (proy.corpus / "demo" / f"00{i + 1}.caso").write_text(texto, encoding="utf-8")

    def test_singular_y_plural_en_las_dos_polaridades(self) -> None:
        """El plural se decide por cada conteo por separado. Con un solo caso de cada lado no se
        distingue una regla correcta de `siempre singular`, así que se prueban las cuatro esquinas."""
        esperado = {
            ("verde_correcto",): "1 caso · 1 verde · 0 rojos",
            ("verde_correcto", "verde_correcto"): "2 casos · 2 verdes · 0 rojos",
            ("falso_verde",): "1 caso · 0 verdes · 1 rojo",
            ("verde_correcto", "falso_verde", "falso_rojo"): "3 casos · 1 verde · 2 rojos",
        }
        for etiquetas, prefijo in esperado.items():
            with self.subTest(etiquetas=etiquetas), tempfile.TemporaryDirectory() as td:
                proy, ruta = _proyecto(Path(td))
                self._con_casos(proy, *etiquetas)
                lente, = lsp.lentes(proy, ruta, MEDIDA)
                self.assertEqual(lente["command"]["title"],
                                 f"{prefijo} · umbral <= 0 segun contrato")

    def test_sin_ningun_caso_no_dibuja_polaridad(self) -> None:
        """Cero y cero no se escriben: «0 verdes · 0 rojos» ocupa lugar y no dice nada que
        «SIN FIJAR» no haya dicho ya."""
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            lente, = lsp.lentes(proy, ruta, MEDIDA)
            self.assertNotIn("verde", lente["command"]["title"])
            self.assertNotIn("rojo", lente["command"]["title"])

    def test_una_medida_ilegible_no_dibuja_nada(self) -> None:
        """El archivo roto ya tiene su diagnóstico; un lens a medias sería ruido encima."""
        with tempfile.TemporaryDirectory() as td:
            proy, ruta = _proyecto(Path(td))
            self.assertEqual(lsp.lentes(proy, ruta, "ninguno\n"), [])

    def test_un_caso_no_lleva_lens(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            proy, _ruta = _proyecto(Path(td))
            caso = proy.corpus / "demo" / "001.caso"
            caso.write_text(CASO, encoding="utf-8")
            self.assertEqual(lsp.lentes(proy, caso, CASO), [])

    def test_oracle_no_se_declara_heredero_de_si_mismo(self) -> None:
        """Cuando Oracle se mide, su catálogo ES el base. Sin restar las propias, todas sus
        medidas salían «responde Oracle» y el lens no decía nada útil sobre ninguna."""
        proy = resolver_cli([])
        ruta = proy.catalogos / "meta" / "meta.donde_compone.oracle"
        lente, = lsp.lentes(proy, ruta, ruta.read_text(encoding="utf-8"))
        self.assertNotIn("responde Oracle", lente["command"]["title"])
        self.assertIn("umbral", lente["command"]["title"])


if __name__ == "__main__":
    unittest.main()
