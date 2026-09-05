"""Contrato por bytes del servidor MCP y de su primera herramienta de sólo lectura."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from nucleo.version import VERSION_DISTRIBUCION
from tools import mcp


def _linea(mensaje) -> bytes:
    """Produce exactamente la línea compacta UTF-8 que escribiría un cliente MCP."""
    cuerpo = json.dumps(mensaje, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return cuerpo + b"\n"


def _desenmarcar(datos: bytes) -> list[dict]:
    """Lee la salida sin reutilizar el parser productivo: ambos no pueden compartir el defecto."""
    if datos and not datos.endswith(b"\n"):
        raise AssertionError("respuesta truncada: falta el delimitador final")
    cuerpos = datos.split(b"\n")[:-1]
    if any(b"\r" in cuerpo for cuerpo in cuerpos):
        raise AssertionError("el transporte MCP no admite delimitadores CRLF")
    return [json.loads(cuerpo.decode("utf-8")) for cuerpo in cuerpos]


def _medida(mid: str, *, ambito: str = "universal", limite: int = 0) -> list:
    """Una medida mínima cuya fijación puede juzgar la medida meta real de Oracle."""
    return [
        "medida", mid,
        ["desde", ["de", "item", "i"]],
        ["resumen", "contar", 1],
        ["umbral", "<=", limite, "ningún item ofensivo", "contrato"],
        ["ambito", ambito],
        ["alcance", "NO ve propiedades distintas de la presencia del item"],
    ]


def _proyecto(raiz: Path, *medidas: list) -> Path:
    """Crea sólo los datos que la herramienta dice necesitar; no depende del checkout como raíz."""
    catalogos = raiz / "catalogos" / "demo"
    catalogos.mkdir(parents=True)
    for datos in medidas:
        (catalogos / f"{datos[1]}.json").write_text(
            json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    return raiz


def _conversacion(*pedidos: dict) -> bytes:
    """Envuelve pedidos de herramienta en el ciclo de vida heredado completo."""
    mensajes = [
        {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": mcp.PROTOCOLO,
                "capabilities": {},
                "clientInfo": {"name": "prueba", "version": "1"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        *pedidos,
        {"jsonrpc": "2.0", "id": 99, "method": "shutdown"},
        {"jsonrpc": "2.0", "method": "exit"},
    ]
    return b"".join(_linea(mensaje) for mensaje in mensajes)


def _ejecutar(proyecto: Path, entrada: bytes, *argumentos: str) -> subprocess.CompletedProcess:
    """Habla con el entry point real para fijar stdin, stdout, stderr y el código de salida."""
    return subprocess.run(
        [sys.executable, str(mcp.RAIZ / "tools" / "mcp.py"),
         "--proyecto", str(proyecto), *argumentos],
        input=entrada,
        capture_output=True,
        cwd=proyecto.parent,
        check=False,
    )


class ConversacionCompletaTests(unittest.TestCase):
    """El adaptador sólo está probado si la semántica correcta sobrevive al transporte real."""

    def test_handshake_lista_llamada_y_apagado_viajan_por_stdin_y_stdout(self) -> None:
        """Una llamada directa no descubriría framing incorrecto ni texto humano en stdout."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            entrada = _conversacion(
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                {
                    "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                    "params": {"name": "oracle_catalogo_efectivo", "arguments": {}},
                },
            )
            resultado = _ejecutar(raiz, entrada)

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(resultado.stderr, b"")
        self.assertEqual(resultado.stdout.startswith(b"{"), True)
        self.assertEqual(resultado.stdout.count(b"\n"), 4)
        respuestas = _desenmarcar(resultado.stdout)
        self.assertEqual([respuesta["id"] for respuesta in respuestas], [1, 2, 3, 99])
        self.assertEqual(respuestas[0], {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "protocolVersion": "2025-11-25",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "oracle-mcp", "version": "0.5.0"},
            },
        })
        self.assertEqual(respuestas[1]["result"]["tools"], [mcp.HERRAMIENTA_CATALOGO])
        llamada = respuestas[2]["result"]
        self.assertEqual(llamada["isError"], False)
        self.assertEqual(json.loads(llamada["content"][0]["text"]),
                         llamada["structuredContent"])
        self.assertEqual(llamada["structuredContent"]["medidas"], [{
            "id": "demo.uno", "origen": "proyecto", "fijacion": "sin_fijar",
        }])
        self.assertEqual(respuestas[3], {"jsonrpc": "2.0", "id": 99, "result": None})

    def test_respuesta_utf8_es_una_sola_linea_compacta(self) -> None:
        """Los saltos de los datos se escapan y sólo el delimitador aparece como byte LF."""
        salida = bytearray()

        class Salida:
            def write(self, datos):
                salida.extend(datos)

            def flush(self):
                return None

        mensaje = {"mensaje": "ámbito\nsegunda línea"}
        mcp._enviar(Salida(), mensaje)
        self.assertEqual(bytes(salida).count(b"\n"), 1)
        self.assertEqual(bytes(salida).endswith(b"\n"), True)
        self.assertEqual(b"\\n" in salida, True)
        self.assertEqual(json.loads(bytes(salida[:-1]).decode("utf-8")), mensaje)


class CatalogoEfectivoTests(unittest.TestCase):
    """La herramienta publica jurisdicción y procedencia, no sólo archivos instalados."""

    def test_detalle_es_ordenado_y_totaliza_el_catalogo_entero(self) -> None:
        """El orden pedido no debe alterar la salida ni convertir total en tamaño de selección."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(
                Path(td), _medida("demo.zeta", limite=2), _medida("demo.alfa", limite=1))
            pedido = {
                "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {
                    "name": "oracle_catalogo_efectivo",
                    "arguments": {"ids": ["demo.zeta", "demo.alfa"]},
                },
            }
            resultado = _ejecutar(raiz, _conversacion(pedido))
            huella_alfa = hashlib.sha256(
                (raiz / "catalogos/demo/demo.alfa.json").read_bytes()).hexdigest()

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        contenido = _desenmarcar(resultado.stdout)[1]["result"]["structuredContent"]
        self.assertEqual(contenido["detalle"], True)
        self.assertEqual(contenido["total"], 2)
        self.assertEqual([fila["id"] for fila in contenido["medidas"]],
                         ["demo.alfa", "demo.zeta"])
        self.assertEqual(set(contenido["medidas"][0]), {
            "id", "origen", "fijacion", "relaciones", "ambito", "requiere", "umbral",
            "alcance", "fuente", "fuente_sha256",
        })
        self.assertEqual(contenido["medidas"][0]["fuente"],
                         "catalogos/demo/demo.alfa.json")
        self.assertEqual(
            contenido["medidas"][0]["fuente_sha256"],
            huella_alfa,
        )

    def test_distingue_medida_sin_jurisdiccion_de_medida_desconocida(self) -> None:
        """Llamar inexistente a la primera invitaría al agente a duplicar una política con dueño."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td))
            (raiz / "oracle.json").write_text(json.dumps({
                "esquema": "oracle.proyecto/v1", "catalogo_base": True,
            }), encoding="utf-8")
            pedidos = tuple({
                "jsonrpc": "2.0", "id": indice, "method": "tools/call",
                "params": {
                    "name": "oracle_catalogo_efectivo", "arguments": {"ids": [mid]},
                },
            } for indice, mid in (
                (2, "meta.agrupar_no_agranda_la_relacion"),
                (3, "demo.no_existe"),
            ))
            resultado = _ejecutar(raiz, _conversacion(*pedidos))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        respuestas = _desenmarcar(resultado.stdout)
        errores = [respuesta["result"] for respuesta in respuestas[1:3]]
        self.assertEqual([error["isError"] for error in errores], [True, True])
        self.assertEqual(
            errores[0]["content"][0]["text"].split(" — ", 1)[0],
            "MEDIDA_NO_EFECTIVA",
        )
        self.assertEqual(
            errores[1]["content"][0]["text"].split(" — ", 1)[0],
            "MEDIDA_DESCONOCIDA",
        )
        self.assertEqual("structuredContent" in errores[0], False)
        self.assertEqual("structuredContent" in errores[1], False)

    def test_catalogo_ilegible_es_error_y_no_indice_vacio(self) -> None:
        """Fallo cerrado evita confundir una lectura rota con un proyecto sin reglas."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td))
            (raiz / "catalogos/demo/rota.json").write_text("{", encoding="utf-8")
            pedido = {
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "oracle_catalogo_efectivo", "arguments": {}},
            }
            resultado = _ejecutar(raiz, _conversacion(pedido))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        error = _desenmarcar(resultado.stdout)[1]["result"]
        self.assertEqual(error["isError"], True)
        self.assertEqual(error["content"][0]["text"].startswith("CATALOGO_INVALIDO — "), True)
        self.assertEqual("structuredContent" in error, False)

    def test_corpus_y_diferencial_ilegibles_no_producen_fijaciones_parciales(self) -> None:
        """La fila no puede parecer fiable si la jueza no alcanzó a reunir toda su evidencia."""
        for clase, ruta_relativa in (
                ("corpus", "corpus/demo/roto.json"),
                ("diferencial", "diferencial/roto.json")):
            with self.subTest(clase=clase), tempfile.TemporaryDirectory() as td:
                raiz = _proyecto(Path(td), _medida("demo.uno"))
                rota = raiz / ruta_relativa
                rota.parent.mkdir(parents=True)
                rota.write_text("{", encoding="utf-8")
                pedido = {
                    "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                    "params": {"name": "oracle_catalogo_efectivo", "arguments": {}},
                }
                resultado = _ejecutar(raiz, _conversacion(pedido))

            self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
            error = _desenmarcar(resultado.stdout)[1]["result"]
            self.assertEqual(error["isError"], True)
            self.assertEqual(
                error["content"][0]["text"].startswith("EVIDENCIA_INCOMPLETA — "), True)
            self.assertEqual("structuredContent" in error, False)

    def test_un_archivo_que_cambia_durante_la_consulta_invalida_toda_la_respuesta(self) -> None:
        """Una respuesta no debe mezclar el catálogo anterior con evidencia del estado siguiente."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            archivo = raiz / "catalogos/demo/demo.uno.json"
            ejercicio_real = mcp.ejercicio_del_catalogo

            def cambiar_despues_de_juzgar(*args, **kwargs):
                ejercicio = ejercicio_real(*args, **kwargs)
                archivo.write_text(
                    json.dumps(_medida("demo.uno", limite=7)), encoding="utf-8")
                return ejercicio

            with mock.patch.object(
                    mcp, "ejercicio_del_catalogo", side_effect=cambiar_despues_de_juzgar):
                with self.assertRaises(mcp.ErrorHerramienta) as atrapado:
                    mcp.catalogo_para_mcp(mcp.Proyecto(raiz), {})

        self.assertEqual(atrapado.exception.codigo,
                         "PROYECTO_CAMBIO_DURANTE_LA_CONSULTA")

    def test_escalar_se_autoriza_al_arrancar_y_no_en_los_argumentos(self) -> None:
        """La llamada no puede concederse permiso para ejecutar el código que está por consultar."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            (raiz / "escalares.py").write_text(
                "# no declara nada, pero sigue siendo código externo\n", encoding="utf-8")
            pedido = {
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "oracle_catalogo_efectivo", "arguments": {}},
            }
            sin_permiso = _ejecutar(raiz, _conversacion(pedido))
            con_permiso = _ejecutar(
                raiz, _conversacion(pedido), "--confiar-escalares")

        self.assertEqual(sin_permiso.returncode, 0, sin_permiso.stderr.decode())
        self.assertEqual(con_permiso.returncode, 0, con_permiso.stderr.decode())
        error = _desenmarcar(sin_permiso.stdout)[1]["result"]
        exito = _desenmarcar(con_permiso.stdout)[1]["result"]
        self.assertEqual(error["isError"], True)
        self.assertEqual(
            error["content"][0]["text"].startswith("ESCALARES_NO_AUTORIZADAS — "), True)
        self.assertEqual(exito["isError"], False)
        self.assertEqual(exito["structuredContent"]["total"], 1)

    def test_ids_vacios_y_propiedades_extra_son_errores_de_herramienta(self) -> None:
        """El esquema cerrado evita un tercer modo implícito y errores de nombre ignorados."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            pedidos = tuple({
                "jsonrpc": "2.0", "id": indice, "method": "tools/call",
                "params": {"name": "oracle_catalogo_efectivo", "arguments": argumentos},
            } for indice, argumentos in (
                (2, {"ids": []}), (3, {"id": "demo.uno"}), (4, [])))
            resultado = _ejecutar(raiz, _conversacion(*pedidos))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        respuestas = _desenmarcar(resultado.stdout)
        textos = [respuesta["result"]["content"][0]["text"] for respuesta in respuestas[1:4]]
        self.assertEqual(
            [texto.split(" — ", 1)[0] for texto in textos],
            ["ARGUMENTOS_INVALIDOS", "ARGUMENTOS_INVALIDOS", "ARGUMENTOS_INVALIDOS"],
        )


class ErroresDeProtocoloTests(unittest.TestCase):
    """Los errores que impiden iniciar una herramienta pertenecen a JSON-RPC, no al dominio."""

    def test_json_roto_y_metodo_desconocido_llevan_codigos_json_rpc(self) -> None:
        """Separar ambos canales permite al cliente corregir transporte sin leer errores Oracle."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            entrada = (
                b"{\n"
                + _conversacion({
                    "jsonrpc": "2.0", "id": 2, "method": "inventado", "params": {},
                })
            )
            resultado = _ejecutar(raiz, entrada)

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        respuestas = _desenmarcar(resultado.stdout)
        self.assertEqual(respuestas[0]["error"]["code"], -32700)
        self.assertEqual(respuestas[2]["error"]["code"], -32601)
        self.assertEqual(respuestas[-1], {"jsonrpc": "2.0", "id": 99, "result": None})

    def test_herramienta_desconocida_es_invalid_params(self) -> None:
        """El despachador no debe convertir un nombre inventado en un error de dominio."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            pedido = {
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "oracle_inventar", "arguments": {}},
            }
            resultado = _ejecutar(raiz, _conversacion(pedido))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        error = _desenmarcar(resultado.stdout)[1]["error"]
        self.assertEqual(error["code"], -32602)
        self.assertEqual(error["message"],
                         "tools/call inválido: herramienta desconocida: oracle_inventar")


class VersionYEntradaTests(unittest.TestCase):
    """La instalación debe exponer el servidor con la distribución publicada vigente."""

    def test_version_y_entry_point_tienen_una_sola_fuente(self) -> None:
        """Duplicar la versión en el adaptador permitiría que el checkout y el binario discrepen."""
        pyproject = (mcp.RAIZ / "pyproject.toml").read_text(encoding="utf-8")
        self.assertEqual(VERSION_DISTRIBUCION, "0.5.0")
        self.assertEqual(
            'oracle-mcp = "oracle_metalenguaje.tools.mcp:main"' in pyproject, True)


if __name__ == "__main__":
    unittest.main()
