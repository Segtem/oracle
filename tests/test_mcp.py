"""Contrato por bytes del servidor MCP y de su primera herramienta de sólo lectura."""

from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
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


def _medida(mid: str, *, ambito: str = "universal", limite: int = 0,
            requiere: tuple[str, ...] = ()) -> list:
    """Una medida mínima cuya fijación puede juzgar la medida meta real de Oracle."""
    datos = [
        "medida", mid,
        ["desde", ["de", "item", "i"]],
        ["resumen", "contar", 1],
        ["umbral", "<=", limite, "ningún item ofensivo", "contrato"],
    ]
    if requiere:
        datos.append(["requiere", *requiere])
    return [
        *datos,
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


def _pedido_evaluar(indice: int, argumentos) -> dict:
    """Nombra la segunda herramienta sin ocultar el sobre que cada conversación transmite."""
    return {
        "jsonrpc": "2.0", "id": indice, "method": "tools/call",
        "params": {"name": "oracle_evaluar", "arguments": argumentos},
    }


def _resultado_exitoso(indice: int, contenido: dict) -> dict:
    """Construye el sobre esperado sin reutilizar el serializador del servidor bajo prueba."""
    texto = json.dumps(
        contenido, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "jsonrpc": "2.0", "id": indice,
        "result": {
            "content": [{"type": "text", "text": texto}],
            "structuredContent": contenido,
            "isError": False,
        },
    }


def _resultado_error(indice: int, texto: str) -> dict:
    """Fija que una falla de dominio no finja structuredContent ni escape como error JSON-RPC."""
    return {
        "jsonrpc": "2.0", "id": indice,
        "result": {
            "content": [{"type": "text", "text": texto}],
            "isError": True,
        },
    }


def _sha_entrada(medida: list, evidencia: dict) -> str:
    """Calcula la huella desde el contrato JSON, independiente del helper productivo."""
    forma = json.dumps(
        {"medida": medida, "evidencia": evidencia},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(forma).hexdigest()


def _sha_archivos(*rutas: Path) -> str:
    """Reproduce la huella publicada desde bytes, sin llamar al código que debe vigilarla."""
    huella = hashlib.sha256()
    for ruta in sorted(rutas):
        huella.update(str(ruta.resolve()).encode("utf-8") + b"\0"
                      + ruta.read_bytes() + b"\0")
    return huella.hexdigest()


class AConversacionCompletaTests(unittest.TestCase):
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
        self.assertEqual(respuestas[1]["result"]["tools"], mcp.HERRAMIENTAS)
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

    def test_tools_list_publica_evaluar_con_el_contrato_normativo_entero(self) -> None:
        """Comparar sólo el nombre dejaría divergir la unión cerrada y los tres estados sin ruido."""
        contrato = (mcp.RAIZ / "estudios" / "MCP-CONTRATO.md").read_text(encoding="utf-8")
        bloque = re.search(
            r"<!-- herramientas-json:inicio -->\n```json\n(.*?)\n```\n"
            r"<!-- herramientas-json:fin -->",
            contrato,
            re.DOTALL,
        )
        self.assertEqual(bloque is not None, True)
        esperadas = json.loads(bloque.group(1))[:2]
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            pedido = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
            resultado = _ejecutar(raiz, _conversacion(pedido))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(
            _desenmarcar(resultado.stdout)[1],
            {"jsonrpc": "2.0", "id": 2,
             "result": {"tools": esperadas}},
        )


class EvaluarTests(unittest.TestCase):
    """La segunda herramienta conserva el juicio del núcleo y sólo lo vuelve transportable."""

    def _contenido(self, raiz: Path, medida: list, evidencia: dict, *, estado: str,
                   valor: int, testigos: list, omitidos: int,
                   derivado: list[str] | None = None,
                   advertencias: list[str] | None = None) -> dict:
        """Explicita cada campo para que una omisión no se esconda detrás de defaults del test."""
        return {
            "esquema": "oracle.mcp/evaluacion/v1",
            "oracle_version": VERSION_DISTRIBUCION,
            "proyecto": str(raiz.resolve()),
            "entrada_sha256": _sha_entrada(medida, evidencia),
            "medida": medida[1],
            "estado": estado,
            "valor": valor,
            "umbral": {
                "operador": medida[4][1],
                "valor": medida[4][2],
                "segun": medida[4][4],
                "porque": medida[4][3],
            },
            "testigos": testigos,
            "testigos_omitidos": omitidos,
            "alcance": medida[-1][1],
            "alcance_derivado": [] if derivado is None else derivado,
            "advertencias": [] if advertencias is None else advertencias,
        }

    def test_verde_rojo_y_sin_evidencia_son_tres_respuestas_enteras_distintas(self) -> None:
        """Sin_evidencia afirma que no se pudo mirar; convertirlo en rojo inventaría un mundo."""
        sin_requiere = _medida("demo.tres_estados")
        con_requiere = _medida("demo.requiere", requiere=("item",))
        filas = [{"id": str(i)} for i in range(7)]
        vacia = {"item": []}
        roja = {"item": filas}
        ausente = {}
        sin_declaraciones = (
            "El proyecto no declara relaciones; alcance_derivado está vacío y no afirma que "
            "la medida mire todos los campos.")
        falta_no_declarada = (
            "La medida consume «item», pero no la declara en requiere y esa relación vino "
            "vacía; se conserva el resultado del álgebra.")
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), sin_requiere, con_requiere)
            pedidos = (
                _pedido_evaluar(2, {"medida": {"id": sin_requiere[1]}, "evidencia": vacia}),
                _pedido_evaluar(3, {"medida": {"id": sin_requiere[1]}, "evidencia": roja}),
                _pedido_evaluar(4, {"medida": {"id": con_requiere[1]},
                                    "evidencia": ausente}),
            )
            resultado = _ejecutar(raiz, _conversacion(*pedidos))
            esperadas = [
                _resultado_exitoso(2, self._contenido(
                    raiz, sin_requiere, vacia, estado="verde", valor=0, testigos=[],
                    omitidos=0, advertencias=[sin_declaraciones, falta_no_declarada])),
                _resultado_exitoso(3, self._contenido(
                    raiz, sin_requiere, roja, estado="rojo", valor=7,
                    testigos=[{"i": fila} for fila in filas[:5]], omitidos=2,
                    advertencias=[sin_declaraciones])),
                _resultado_exitoso(4, self._contenido(
                    raiz, con_requiere, ausente, estado="sin_evidencia", valor=0,
                    testigos=[], omitidos=0, advertencias=[sin_declaraciones])),
            ]

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(_desenmarcar(resultado.stdout)[1:4], esperadas)

    def test_texto_json_se_evalua_en_memoria_y_deriva_el_alcance_declarado(self) -> None:
        """El modo por valor debe funcionar sin crear un archivo y sin ocultar campos no leídos."""
        medida = _medida("demo.efimera")
        evidencia = {"item": [{"id": "a", "nombre": "A"}]}
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td))
            relaciones = raiz / "relaciones"
            relaciones.mkdir()
            (relaciones / "item.json").write_text(json.dumps([
                "relacion", "item",
                ["campos", ["campo", "id", "texto", "sin_unidad"],
                 ["campo", "nombre", "texto", "sin_unidad"]],
                ["alcance", "NO ve el origen del item"],
            ]), encoding="utf-8")
            pedido = _pedido_evaluar(2, {
                "medida": {"texto": json.dumps(medida), "formato": "json"},
                "evidencia": evidencia,
            })
            resultado = _ejecutar(raiz, _conversacion(pedido))
            contenido = self._contenido(
                raiz, medida, evidencia, estado="rojo", valor=1,
                testigos=[{"i": evidencia["item"][0]}], omitidos=0,
                derivado=["    de `item` NO lee: id, nombre"],
            )

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(_desenmarcar(resultado.stdout)[1], _resultado_exitoso(2, contenido))

    def test_texto_oracle_se_expande_antes_de_firmar_y_conserva_testigos(self) -> None:
        """Firmar el texto superficial haría distintas dos medidas con la misma forma canónica."""
        texto = """\
ninguno demo.oracle:
    de item i
    donde i.ofensivo == true
    umbral <= 0 segun contrato porque "ninguno ofensivo"
    ambito universal
    alcance "NO ve campos distintos de ofensivo"
"""
        medida = [
            "medida", "demo.oracle",
            ["desde", ["de", "item", "i"],
             ["donde", ["==", ["campo", "i", "ofensivo"], True]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "ninguno ofensivo", "contrato"],
            ["ambito", "universal"],
            ["alcance", "NO ve campos distintos de ofensivo"],
        ]
        evidencia = {"item": [
            {"id": "a", "ofensivo": False}, {"id": "b", "ofensivo": True},
        ]}
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td))
            relaciones = raiz / "relaciones"
            relaciones.mkdir()
            (relaciones / "item.json").write_text(json.dumps([
                "relacion", "item",
                ["campos", ["campo", "id", "texto", "sin_unidad"],
                 ["campo", "ofensivo", "booleano", "sin_unidad"]],
                ["alcance", "NO ve por qué es ofensivo"],
            ]), encoding="utf-8")
            resultado = _ejecutar(raiz, _conversacion(_pedido_evaluar(2, {
                "medida": {"texto": texto, "formato": "oracle"},
                "evidencia": evidencia,
            })))
            contenido = self._contenido(
                raiz, medida, evidencia, estado="rojo", valor=1,
                testigos=[{"i": evidencia["item"][1]}], omitidos=0,
                derivado=["    de `item` NO lee: id"],
            )

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(_desenmarcar(resultado.stdout)[1], _resultado_exitoso(2, contenido))

    def test_archivo_y_formas_hibridas_no_abren_una_tercera_alternativa(self) -> None:
        """Aceptar una ruta o media rama de la unión ampliaría autoridad y escondería errores."""
        especificaciones = (
            {"archivo": "../afuera.json"},
            {"id": "demo.uno", "texto": "[]", "formato": "json"},
            {"texto": "[]", "formato": "yaml"},
            {"texto": 7, "formato": "json"},
            {"id": "sin_dominio"},
        )
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            pedidos = tuple(_pedido_evaluar(i, {
                "medida": especificacion, "evidencia": {},
            }) for i, especificacion in enumerate(especificaciones, start=2))
            resultado = _ejecutar(raiz, _conversacion(*pedidos))
        textos = (
            'ARGUMENTOS_INVALIDOS — $.medida: {"archivo":"../afuera.json"}; se esperaba '
            'exactamente {id} o {texto, formato}; archivo no está admitido.',
            'ARGUMENTOS_INVALIDOS — $.medida: {"formato":"json","id":"demo.uno",'
            '"texto":"[]"}; se esperaba exactamente {id} o {texto, formato}; archivo no está '
            'admitido.',
            'ARGUMENTOS_INVALIDOS — $.medida.formato: "yaml"; se esperaba oracle o json.',
            'ARGUMENTOS_INVALIDOS — $.medida.texto: 7; se esperaba texto.',
            'ARGUMENTOS_INVALIDOS — $.medida.id: "sin_dominio"; se esperaba un id '
            'dominio.nombre portable.',
        )

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(
            _desenmarcar(resultado.stdout)[1:6],
            [_resultado_error(i, texto) for i, texto in enumerate(textos, start=2)],
        )

    def test_evidencia_y_raiz_de_argumentos_se_validan_sin_resumen_opaco(self) -> None:
        """Cada nivel inválido nombra el dato exacto; nunca se transforma en evidencia vacía."""
        argumentos = (
            [],
            {"medida": {"id": "demo.uno"}},
            {"medida": {"id": "demo.uno"}, "evidencia": [], "extra": 1},
            {"medida": {"id": "demo.uno"}, "evidencia": []},
            {"medida": {"id": "demo.uno"}, "evidencia": {"item": {}}},
            {"medida": {"id": "demo.uno"}, "evidencia": {"item": [7]}},
        )
        textos = (
            "ARGUMENTOS_INVALIDOS — $: []; se esperaba un objeto con medida y evidencia.",
            "ARGUMENTOS_INVALIDOS — $: falta evidencia; se esperaban los campos medida y "
            "evidencia.",
            "ARGUMENTOS_INVALIDOS — $.extra: 1; se esperaba ninguna propiedad adicional.",
            "ARGUMENTOS_INVALIDOS — $.evidencia: []; se esperaba un objeto de relaciones.",
            "ARGUMENTOS_INVALIDOS — $.evidencia.item: {}; se esperaba una lista de filas objeto.",
            "ARGUMENTOS_INVALIDOS — $.evidencia.item[0]: 7; se esperaba una fila objeto.",
        )
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            pedidos = tuple(_pedido_evaluar(i, valor)
                            for i, valor in enumerate(argumentos, start=2))
            resultado = _ejecutar(raiz, _conversacion(*pedidos))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(
            _desenmarcar(resultado.stdout)[1:7],
            [_resultado_error(i, texto) for i, texto in enumerate(textos, start=2)],
        )

    def test_relaciones_invalidas_fallan_en_lugar_de_simular_cero_declaraciones(self) -> None:
        """No pude derivar y no hay puntos ciegos son afirmaciones incompatibles sobre el árbol."""
        medida = _medida("demo.uno")
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), medida)
            relaciones = raiz / "relaciones"
            relaciones.mkdir()
            (relaciones / "item.json").write_text(json.dumps([
                "relacion", "item", ["campos"], ["alcance", "incompleta"],
            ]), encoding="utf-8")
            resultado = _ejecutar(raiz, _conversacion(_pedido_evaluar(2, {
                "medida": {"id": medida[1]}, "evidencia": {"item": []},
            })))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(
            _desenmarcar(resultado.stdout)[1],
            _resultado_error(
                2, "RELACIONES_INVALIDAS — no se pudo derivar el alcance: item: la relación "
                "debe declarar al menos un campo. No se devolvió un alcance vacío."),
        )

    def test_id_desconocido_y_textos_rotos_fallan_sin_resultado_estructurado(self) -> None:
        """Una entrada que no cargó no puede adquirir valor cero, estado ni apariencia de juicio."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            pedidos = (
                _pedido_evaluar(2, {"medida": {"id": "demo.ausente"}, "evidencia": {}}),
                _pedido_evaluar(3, {"medida": {"texto": "{", "formato": "json"},
                                    "evidencia": {}}),
                _pedido_evaluar(4, {"medida": {"texto": "", "formato": "oracle"},
                                    "evidencia": {}}),
            )
            resultado = _ejecutar(raiz, _conversacion(*pedidos))
        textos = (
            "MEDIDA_DESCONOCIDA — «demo.ausente» no aparece en las fuentes seleccionadas; "
            "consultá oracle_catalogo_efectivo sin ids.",
            "MEDIDA_INVALIDA — el texto JSON de la medida no se entiende: Expecting property "
            "name enclosed in double quotes: line 1 column 2 (char 1).",
            "MEDIDA_INVALIDA — el texto Oracle de la medida no se entiende: línea 1, columna 1: "
            "se esperaba encabezado de medida\n   1 | \n     | ^.",
        )

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(
            _desenmarcar(resultado.stdout)[1:4],
            [_resultado_error(i, texto) for i, texto in enumerate(textos, start=2)],
        )

    def test_error_del_algebra_no_se_traduce_a_rojo(self) -> None:
        """Una excepción significa que no hubo veredicto; rojo afirmaría que sí se pudo juzgar."""
        medida = [
            "medida", "demo.falla",
            ["desde", ["de", "item", "i"],
             ["donde", ["==", ["campo", "i", "ausente"], True]]],
            ["resumen", "contar", 1],
            ["umbral", "<=", 0, "ningún ausente", "contrato"],
            ["ambito", "universal"],
            ["alcance", "NO ve campos distintos de ausente"],
        ]
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td))
            resultado = _ejecutar(raiz, _conversacion(_pedido_evaluar(2, {
                "medida": {"texto": json.dumps(medida), "formato": "json"},
                "evidencia": {"item": [{"id": "a"}]},
            })))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(
            _desenmarcar(resultado.stdout)[1],
            _resultado_error(
                2, "EVALUACION_FALLIDA — «demo.falla» no se pudo evaluar: ErrorDeAlgebra: "
                "«==» sobre un valor ausente: ['==', ['campo', 'i', 'ausente'], True] en "
                "`2.2.1`."),
        )

    def test_escalares_externas_sólo_se_autorizan_al_arrancar(self) -> None:
        """Un argumento de herramienta nunca puede concederse permiso para ejecutar Python ajeno."""
        medida = _medida("demo.efimera")
        argumentos = {
            "medida": {"texto": json.dumps(medida), "formato": "json"},
            "evidencia": {"item": []},
        }
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td))
            escalares = raiz / "escalares.py"
            escalares.write_text("# código externo, aunque esté vacío\n", encoding="utf-8")
            sin_permiso = _ejecutar(
                raiz, _conversacion(_pedido_evaluar(2, argumentos)))
            con_permiso = _ejecutar(
                raiz, _conversacion(_pedido_evaluar(2, argumentos)), "--confiar-escalares")
            advertencias = [
                "El proyecto no declara relaciones; alcance_derivado está vacío y no afirma que "
                "la medida mire todos los campos.",
                "La medida consume «item», pero no la declara en requiere y esa relación vino "
                "vacía; se conserva el resultado del álgebra.",
            ]
            contenido = self._contenido(
                raiz, medida, argumentos["evidencia"], estado="verde", valor=0,
                testigos=[], omitidos=0, advertencias=advertencias)

        self.assertEqual(sin_permiso.returncode, 0, sin_permiso.stderr.decode())
        self.assertEqual(con_permiso.returncode, 0, con_permiso.stderr.decode())
        self.assertEqual(
            _desenmarcar(sin_permiso.stdout)[1],
            _resultado_error(
                2, f"ESCALARES_NO_AUTORIZADAS — {escalares} es código externo; autorizalo en "
                "la configuración de arranque del servidor, no en esta llamada."),
        )
        self.assertEqual(
            _desenmarcar(con_permiso.stdout)[1], _resultado_exitoso(2, contenido))

    def test_cambio_de_archivos_invalida_el_resultado_aun_si_ambos_estados_cargan(self) -> None:
        """Un resultado mezclado no pertenece ni al estado inicial ni al final del proyecto."""
        medida = _medida("demo.uno")
        relacion_inicial = [
            "relacion", "item",
            ["campos", ["campo", "id", "texto", "sin_unidad"]],
            ["alcance", "NO ve el origen"],
        ]
        relacion_final = [
            "relacion", "item",
            ["campos", ["campo", "id", "texto", "sin_unidad"],
             ["campo", "nombre", "texto", "sin_unidad"]],
            ["alcance", "NO ve el origen"],
        ]
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), medida)
            relaciones = raiz / "relaciones"
            relaciones.mkdir()
            archivo_relacion = relaciones / "item.json"
            archivo_relacion.write_text(json.dumps(relacion_inicial), encoding="utf-8")
            archivo_medida = raiz / "catalogos" / "demo" / "demo.uno.json"
            inicial = _sha_archivos(archivo_medida, archivo_relacion)
            presentar_real = mcp._presentar_evaluacion

            def cambiar(*args, **kwargs):
                contenido = presentar_real(*args, **kwargs)
                archivo_relacion.write_text(json.dumps(relacion_final), encoding="utf-8")
                return contenido

            entrada = _conversacion(_pedido_evaluar(2, {
                "medida": {"id": medida[1]}, "evidencia": {"item": []},
            }))
            salida = io.BytesIO()
            with mock.patch.object(mcp, "_presentar_evaluacion", side_effect=cambiar):
                codigo = mcp.servir(mcp.Proyecto(raiz), io.BytesIO(entrada), salida)
            final = _sha_archivos(archivo_medida, archivo_relacion)

        self.assertEqual(codigo, 0)
        self.assertEqual(_desenmarcar(salida.getvalue())[1], _resultado_error(
            2, "PROYECTO_CAMBIO_DURANTE_LA_CONSULTA — "
            f"huella inicial {inicial} y final {final}; reintentá sobre un estado estable.",
        ))

    def test_rotura_durante_una_falla_también_gana_sobre_el_error_parcial(self) -> None:
        """Si el segundo estado ya no carga, devolver el primer error ocultaría la carrera real."""
        medida = _medida("demo.uno")
        relacion = [
            "relacion", "item",
            ["campos", ["campo", "id", "texto", "sin_unidad"]],
            ["alcance", "NO ve el origen"],
        ]
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), medida)
            relaciones = raiz / "relaciones"
            relaciones.mkdir()
            archivo_relacion = relaciones / "item.json"
            archivo_relacion.write_text(json.dumps(relacion), encoding="utf-8")
            archivo_medida = raiz / "catalogos" / "demo" / "demo.uno.json"
            inicial = _sha_archivos(archivo_medida, archivo_relacion)

            def romper(*_args, **_kwargs):
                archivo_relacion.write_text(json.dumps([
                    "relacion", "item", ["campos"], ["alcance", "rota"],
                ]), encoding="utf-8")
                raise RuntimeError("resultado parcial deliberado")

            entrada = _conversacion(_pedido_evaluar(2, {
                "medida": {"id": medida[1]}, "evidencia": {"item": []},
            }))
            salida = io.BytesIO()
            with mock.patch.object(mcp, "_presentar_evaluacion", side_effect=romper):
                codigo = mcp.servir(mcp.Proyecto(raiz), io.BytesIO(entrada), salida)
            marca = {
                "error": "RelacionMalDeclarada",
                "mensaje": "item: la relación debe declarar al menos un campo",
            }
            final = hashlib.sha256(json.dumps(
                marca, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")).hexdigest()

        self.assertEqual(codigo, 0)
        self.assertEqual(_desenmarcar(salida.getvalue())[1], _resultado_error(
            2, "PROYECTO_CAMBIO_DURANTE_LA_CONSULTA — "
            f"huella inicial {inicial} y final {final}; reintentá sobre un estado estable.",
        ))


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

    def test_ids_rechaza_por_separado_tipo_y_formato_invalidos(self) -> None:
        """Una disyunción rota no debe aceptar justo la mitad inválida de cada alternativa."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            pedidos = tuple({
                "jsonrpc": "2.0", "id": indice, "method": "tools/call",
                "params": {
                    "name": "oracle_catalogo_efectivo", "arguments": {"ids": [mid]},
                },
            } for indice, mid in ((2, 7), (3, "sin_dominio")))
            resultado = _ejecutar(raiz, _conversacion(*pedidos))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        respuestas = _desenmarcar(resultado.stdout)
        self.assertEqual(
            [respuesta["result"]["content"][0]["text"] for respuesta in respuestas[1:3]],
            [
                "ARGUMENTOS_INVALIDOS — $.ids[0]: 7; se esperaba un id dominio.nombre portable.",
                "ARGUMENTOS_INVALIDOS — $.ids[0]: \"sin_dominio\"; se esperaba un id "
                "dominio.nombre portable.",
            ],
        )

    def test_cada_clase_de_fijacion_conserva_su_nombre_completo(self) -> None:
        """Perder un retorno confundiría evidencia, arnés y herencia con una fijación ausente."""
        ejercicios = (
            SimpleNamespace(
                heredadas={"demo.uno"}, casos_por_medida={}, aparte=set(),
                sin_ejercitar=set()),
            SimpleNamespace(
                heredadas=set(), casos_por_medida={"demo.uno": 1}, aparte=set(),
                sin_ejercitar=set()),
            SimpleNamespace(
                heredadas=set(), casos_por_medida={}, aparte={"demo.uno"},
                sin_ejercitar=set()),
        )
        self.assertEqual(
            [mcp._fijacion("demo.uno", ejercicio) for ejercicio in ejercicios],
            ["heredada", "evidencia", "arnes"],
        )

    def test_falta_de_autorizacion_rige_tambien_en_la_llamada_directa(self) -> None:
        """El valor predeterminado no puede conceder permiso fuera del arranque del servidor."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            (raiz / "escalares.py").write_text("# código externo\n", encoding="utf-8")
            with self.assertRaises(mcp.ErrorHerramienta) as atrapado:
                mcp.catalogo_para_mcp(mcp.Proyecto(raiz), {})

        self.assertEqual(atrapado.exception.codigo, "ESCALARES_NO_AUTORIZADAS")

    def test_mensaje_de_escalar_sin_separador_no_pierde_su_texto(self) -> None:
        """Extraer el campo equivocado borraría el único diagnóstico que puede leer el agente."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            error = mcp.EscalaresNoConfiables("mensaje entero sin el separador esperado")
            with mock.patch.object(mcp, "escalares_del_proyecto", side_effect=error):
                with self.assertRaises(mcp.ErrorHerramienta) as atrapado:
                    mcp.catalogo_para_mcp(mcp.Proyecto(raiz), {})

        self.assertEqual(
            str(atrapado.exception),
            "ESCALARES_NO_AUTORIZADAS — mensaje entero sin el separador esperado es código "
            "externo; autorizalo en la configuración de arranque del servidor, no en esta llamada.",
        )


class HuellaYConfinamientoTests(unittest.TestCase):
    """La huella sólo representa archivos físicos confinados y fallas reproducibles."""

    def test_directorios_opcionales_rechazan_enlaces_rotos_y_archivos(self) -> None:
        """Omitir una mitad de la guarda convertiría una entrada inválida en evidencia ausente."""
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            roto = base / "roto"
            roto.symlink_to(base / "no-existe", target_is_directory=True)
            archivo = base / "archivo"
            archivo.write_text("dato", encoding="utf-8")
            for ruta, mensaje in (
                    (roto, "`roto/` debe ser un directorio físico"),
                    (archivo, "`archivo/` debe ser un directorio físico")):
                with self.subTest(ruta=ruta.name):
                    with self.assertRaises(mcp.ProyectoInvalido) as atrapado:
                        mcp._rutas_de_directorio(ruta)
                    self.assertEqual(str(atrapado.exception), mensaje)

    def test_un_enlace_dentro_de_evidencia_nunca_se_acepta_como_archivo(self) -> None:
        """Un enlace interno no debe adquirir autoridad de lectura por apuntar dentro de la raíz."""
        with tempfile.TemporaryDirectory() as td:
            directorio = Path(td) / "corpus"
            directorio.mkdir()
            destino = directorio / "real.caso"
            destino.write_text("dato", encoding="utf-8")
            (directorio / "enlace.caso").symlink_to(destino)
            with self.assertRaises(mcp.ProyectoInvalido) as atrapado:
                mcp._rutas_de_directorio(directorio)

        self.assertEqual(
            str(atrapado.exception),
            f"{directorio / 'enlace.caso'} debe ser un archivo físico, no un symlink",
        )

    def test_enlaces_rotos_de_configuracion_y_escalares_entran_en_la_huella(self) -> None:
        """Ignorarlos haría que crear su destino no cambiara la identidad consultada."""
        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            catalogo = SimpleNamespace(entradas={})
            for nombre in ("oracle.json", "escalares.py"):
                with self.subTest(nombre=nombre):
                    enlace = raiz / nombre
                    destino = raiz / f"{nombre}.ausente"
                    enlace.symlink_to(destino)
                    self.assertEqual(
                        mcp._entradas_de_huella(mcp.Proyecto(raiz), catalogo),
                        [destino.resolve()],
                    )
                    enlace.unlink()

    def test_una_falla_al_refrescar_tiene_una_huella_determinista(self) -> None:
        """Sin marca completa, dos roturas distintas podrían parecer el mismo estado final."""
        with tempfile.TemporaryDirectory() as td:
            proy = mcp.Proyecto(Path(td))

            def fallar():
                raise RuntimeError("rotura deliberada")

            marca = {"error": "RuntimeError", "mensaje": "rotura deliberada"}
            esperada = hashlib.sha256(
                mcp._json_compacto(marca).encode("utf-8")).hexdigest()
            obtenida = mcp._huella_final(proy, SimpleNamespace(), fallar)

        self.assertEqual(obtenida, esperada)


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

    def test_pedido_mal_formado_es_solicitud_invalida_y_no_corta_la_sesion(self) -> None:
        """Un sobre inválido es -32600 y el cliente debe poder corregirlo en la misma sesión."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            entrada = _linea({
                "jsonrpc": "1.0", "id": 20, "method": "ping",
            }) + _conversacion()
            resultado = _ejecutar(raiz, entrada)

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        respuestas = _desenmarcar(resultado.stdout)
        self.assertEqual(respuestas[0], {
            "jsonrpc": "2.0", "id": 20,
            "error": {
                "code": -32600,
                "message": "pedido JSON-RPC inválido: se esperaba un objeto con jsonrpc '2.0' "
                           "y method.",
            },
        })
        self.assertEqual(respuestas[-1], {"jsonrpc": "2.0", "id": 99, "result": None})

    def test_inicializacion_repetida_es_solicitud_invalida_y_no_reinicia_el_estado(self) -> None:
        """Reiniciar una sesión activa ocultaría un error de orden bajo una segunda bienvenida."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            repetido = {
                "jsonrpc": "2.0", "id": 2, "method": "initialize", "params": {},
            }
            resultado = _ejecutar(raiz, _conversacion(repetido))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        respuestas = _desenmarcar(resultado.stdout)
        self.assertEqual(respuestas[1], {
            "jsonrpc": "2.0", "id": 2,
            "error": {
                "code": -32600,
                "message": "pedido JSON-RPC inválido: initialize fuera de orden.",
            },
        })
        self.assertEqual(respuestas[-1], {"jsonrpc": "2.0", "id": 99, "result": None})

    def test_notificacion_de_inicio_con_id_no_habilita_herramientas(self) -> None:
        """Confundir pedido con notificación adelantaría el estado antes del aviso legítimo."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            mensajes = (
                {
                    "jsonrpc": "2.0", "id": 1, "method": "initialize",
                    "params": {},
                },
                {
                    "jsonrpc": "2.0", "id": 2,
                    "method": "notifications/initialized",
                },
                {"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}},
                {"jsonrpc": "2.0", "id": 99, "method": "shutdown"},
                {"jsonrpc": "2.0", "method": "exit"},
            )
            resultado = _ejecutar(raiz, b"".join(_linea(mensaje) for mensaje in mensajes))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        respuestas = _desenmarcar(resultado.stdout)
        self.assertEqual(respuestas[1], {
            "jsonrpc": "2.0", "id": 3,
            "error": {"code": -32601, "message": "método no soportado: tools/list"},
        })

    def test_ping_devuelve_el_resultado_entero_despues_de_inicializar(self) -> None:
        """Una comparación invertida convertiría el mecanismo de vida en método inexistente."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            pedido = {"jsonrpc": "2.0", "id": 2, "method": "ping"}
            resultado = _ejecutar(raiz, _conversacion(pedido))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(
            _desenmarcar(resultado.stdout)[1],
            {"jsonrpc": "2.0", "id": 2, "result": {}},
        )

    def test_cada_error_de_parametros_conserva_el_codigo_de_parametros_invalidos(self) -> None:
        """Método válido con forma inválida es -32602, nunca método inexistente ni otro código."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            pedidos = (
                {
                    "jsonrpc": "2.0", "id": 2, "method": "tools/list",
                    "params": {"inesperado": 1},
                },
                {
                    "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                    "params": {
                        "name": "oracle_catalogo_efectivo", "arguments": {},
                        "inesperado": 1,
                    },
                },
            )
            resultado = _ejecutar(raiz, _conversacion(*pedidos))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        respuestas = _desenmarcar(resultado.stdout)
        self.assertEqual(
            [respuesta["error"] for respuesta in respuestas[1:3]],
            [
                {"code": -32602,
                 "message": "tools/list inválido: parámetros inesperados."},
                {"code": -32602,
                 "message": "tools/call inválido: se esperaba name y arguments."},
            ],
        )

    def test_notificacion_desconocida_no_se_confunde_con_exit(self) -> None:
        """Una notificación extensible no debe terminar el servidor antes del apagado acordado."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            desconocida = {"jsonrpc": "2.0", "method": "notificacion/desconocida"}
            resultado = _ejecutar(raiz, _conversacion(desconocida))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(_desenmarcar(resultado.stdout)[-1], {
            "jsonrpc": "2.0", "id": 99, "result": None,
        })

    def test_exit_con_id_es_pedido_desconocido_y_la_sesion_continua(self) -> None:
        """Quitar la negación haría que un pedido mal formado apagara unilateralmente la sesión."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            pedido = {"jsonrpc": "2.0", "id": 2, "method": "exit"}
            resultado = _ejecutar(raiz, _conversacion(pedido))

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        respuestas = _desenmarcar(resultado.stdout)
        self.assertEqual(respuestas[1], {
            "jsonrpc": "2.0", "id": 2,
            "error": {"code": -32601, "message": "método no soportado: exit"},
        })
        self.assertEqual(respuestas[-1], {"jsonrpc": "2.0", "id": 99, "result": None})

    def test_manejar_salida_devuelve_false_exacto(self) -> None:
        """El bucle distingue la orden de salida por este valor, que no admite un retorno ausente."""
        with tempfile.TemporaryDirectory() as td:
            servidor = mcp.Servidor(mcp.Proyecto(Path(td)), io.BytesIO())
            servidor.estado = "inicializado"
            resultado = servidor.manejar({"jsonrpc": "2.0", "method": "exit"})

        self.assertEqual(servidor.confiar_escalares, False)
        self.assertEqual(resultado, False)


class TerminacionDelTransporteTests(unittest.TestCase):
    """Cada cierre tiene un código de proceso completo que el anfitrión puede interpretar."""

    def test_transporte_truncado_sale_uno_y_explica_el_error_por_stderr(self) -> None:
        """Un flujo de bytes incompleto no puede parecer un cierre limpio ni un fallo de herramienta."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            resultado = _ejecutar(raiz, b"{}")

        self.assertEqual(resultado.returncode, 1)
        self.assertEqual(resultado.stdout, b"")
        self.assertEqual(
            resultado.stderr.decode("utf-8"),
            "TRANSPORTE MCP INVÁLIDO — mensaje MCP truncado: falta el delimitador '\\n'\n",
        )

    def test_fin_de_entrada_antes_del_apagado_sale_uno(self) -> None:
        """Desaparecer sin shutdown es una sesión abortada aunque no haya bytes mal formados."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            resultado = _ejecutar(raiz, b"")

        self.assertEqual(resultado.returncode, 1)
        self.assertEqual(resultado.stdout, b"")
        self.assertEqual(resultado.stderr, b"")

    def test_fin_de_entrada_despues_del_apagado_sale_cero(self) -> None:
        """Tras aceptar shutdown, cerrar stdin es una terminación limpia aunque no llegue exit."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            entrada = b"".join(_linea(mensaje) for mensaje in (
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 99, "method": "shutdown"},
            ))
            resultado = _ejecutar(raiz, entrada)

        self.assertEqual(resultado.returncode, 0, resultado.stderr.decode())
        self.assertEqual(_desenmarcar(resultado.stdout)[-1], {
            "jsonrpc": "2.0", "id": 99, "result": None,
        })

    def test_salida_antes_del_apagado_sale_uno(self) -> None:
        """Una notificación exit prematura no debe certificar el cierre que nunca se acordó."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            entrada = b"".join(_linea(mensaje) for mensaje in (
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "method": "exit"},
            ))
            resultado = _ejecutar(raiz, entrada)

        self.assertEqual(resultado.returncode, 1)
        self.assertEqual(_desenmarcar(resultado.stdout), [{
            "jsonrpc": "2.0", "id": 1,
            "result": {
                "protocolVersion": "2025-11-25",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "oracle-mcp", "version": "0.5.0"},
            },
        }])

    def test_servir_sin_permiso_predeterminado_devuelve_error_de_herramienta(self) -> None:
        """La entrada por bytes tampoco puede elevar confianza por omitir una bandera opcional."""
        with tempfile.TemporaryDirectory() as td:
            raiz = _proyecto(Path(td), _medida("demo.uno"))
            (raiz / "escalares.py").write_text("# código externo\n", encoding="utf-8")
            entrada = _conversacion({
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "oracle_catalogo_efectivo", "arguments": {}},
            })
            salida = io.BytesIO()
            codigo = mcp.servir(mcp.Proyecto(raiz), io.BytesIO(entrada), salida)

        self.assertEqual(codigo, 0)
        self.assertEqual(
            _desenmarcar(salida.getvalue())[1]["result"]["isError"],
            True,
        )


class VersionYEntradaTests(unittest.TestCase):
    """La instalación debe exponer el servidor con la distribución publicada vigente."""

    def test_version_y_entry_point_tienen_una_sola_fuente(self) -> None:
        """Duplicar la versión en el adaptador permitiría que el checkout y el binario discrepen."""
        pyproject = (mcp.RAIZ / "pyproject.toml").read_text(encoding="utf-8")
        self.assertEqual(VERSION_DISTRIBUCION, "0.5.0")
        self.assertEqual(
            'oracle-mcp = "oracle_metalenguaje.tools.mcp:main"' in pyproject, True)

    def test_proyecto_inexistente_hace_fallar_el_punto_de_entrada(self) -> None:
        """Un destino que no existe no puede abrir un servidor sobre un proyecto implícito."""
        with tempfile.TemporaryDirectory() as td:
            inexistente = Path(td) / "no-existe"
            resultado = subprocess.run(
                [sys.executable, str(mcp.RAIZ / "tools" / "mcp.py"),
                 "--proyecto", str(inexistente)],
                input=b"",
                capture_output=True,
                cwd=Path(td),
                check=False,
            )

        self.assertEqual(resultado.returncode, 1)
        self.assertEqual(resultado.stdout, b"")
        self.assertEqual(
            resultado.stderr.decode("utf-8"),
            f"PROYECTO INVÁLIDO — {inexistente} no parece un proyecto: le falta `catalogos/`\n",
        )


if __name__ == "__main__":
    unittest.main()


class LosCuatroQueLaMutacionDejoVivosTests(unittest.TestCase):
    """Cada uno con la entrada que lo separa de su mutante, no con una que sólo lo ejecuta.

    Los cuatro sobrevivieron a la primera ronda con las dos herramientas adentro. Ninguno es
    cosmético: dos deciden qué le dice el servidor a un agente sobre los campos que su medida lee,
    uno decide qué bytes se declaran leídos, y el cuarto es el valor por omisión de la autorización
    para ejecutar código del proyecto.
    """

    def _relacion(self, nombre: str, *campos: str):
        return SimpleNamespace(
            nombre=nombre,
            campos=tuple(SimpleNamespace(nombre=c) for c in campos))

    def _medida(self, texto: str):
        from nucleo.macro import macros_base
        from nucleo.sintaxis import leer_con_mapa

        lectura = leer_con_mapa(texto, macros=macros_base())
        return mcp.Medida.de_datos(lectura.datos, macros=macros_base())

    def test_un_campo_no_declarado_se_atribuye_a_SU_relacion_y_no_a_otra(self) -> None:
        """El `rel == relacion` empareja lectura y declaración. Con `!=` el aviso saldría bajo la
        relación equivocada: le diría a un agente que arregle una declaración que está sana.
        """
        medida = self._medida(
            "medida d.dos:\n"
            "    de alfa a\n"
            "    unir beta b\n"
            "    donde a.propio == true y b.ajeno == true\n"
            "    resumen contar(1)\n"
            "    umbral <= 0 segun contrato porque \"x\"\n"
            "    ambito universal\n"
            "    alcance \"NO ve nada\"\n")
        declaradas = {"alfa": self._relacion("alfa", "propio"),
                      "beta": self._relacion("beta")}

        lineas = mcp._alcance_derivado_estricto(medida, declaradas)

        self.assertEqual(
            lineas,
            ["    de `alfa` lee todos los campos declarados",
             "    ⚠ de `beta` LEE campos que la relación no declara: ajeno"])

    def test_leer_un_campo_no_declarado_no_se_informa_como_leer_todo(self) -> None:
        """El `not` del `elif`. Sin él, una relación que declara CERO campos y de la que la medida
        lee uno cerraría con «lee todos los campos declarados» — literalmente cierto y engañoso:
        un agente leería que está en orden justo donde acaba de aparecer el aviso.
        """
        medida = self._medida(
            "ninguno d.una:\n"
            "    de sola s\n"
            "    donde s.invisible == true\n"
            "    umbral <= 0 segun contrato porque \"x\"\n"
            "    ambito universal\n"
            "    alcance \"NO ve nada\"\n")

        lineas = mcp._alcance_derivado_estricto(medida, {"sola": self._relacion("sola")})

        self.assertEqual(
            lineas,
            ["    ⚠ de `sola` LEE campos que la relación no declara: invisible"])

    def test_un_enlace_roto_cuenta_como_byte_leido(self) -> None:
        """`exists()` da falso en un symlink colgado, así que sólo `is_symlink()` lo ve. Con `and`
        el enlace roto desaparece del inventario y la huella del proyecto no cambiaría al
        repararlo: dos estados distintos del disco darían la misma respuesta.
        """
        import os

        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            os.symlink(raiz / "no-esta", raiz / "escalares.py")
            proy = SimpleNamespace(raiz=raiz)

            rutas = mcp._rutas_de_evaluacion(proy, None)
            # `resolve()` de un enlace colgado da su DESTINO, así que se compara contra él: lo que
            # el mutante cambia no es el nombre sino si la entrada existe o no.
            esperado = [(raiz / "no-esta").resolve()]

        self.assertEqual(sorted(rutas), esperado)

    def test_sin_autorizacion_explicita_no_se_ejecutan_las_escalares(self) -> None:
        """El valor por omisión de `confiar_escalares`. Si fuera `True`, quien llamara sin decir
        nada estaría ejecutando código del proyecto sin haberlo autorizado — y la autorización es
        justamente lo que se decide al arrancar el servidor y no por llamada.
        """
        import inspect

        firma = inspect.signature(mcp.evaluar_para_mcp)
        self.assertEqual(firma.parameters["confiar_escalares"].default, False)

        with tempfile.TemporaryDirectory() as td:
            raiz = Path(td)
            (raiz / "catalogos").mkdir()
            (raiz / "escalares.py").write_text("# código del proyecto\n", encoding="utf-8")
            proy = mcp.Proyecto(raiz)
            with self.assertRaises(mcp.ErrorHerramienta) as capturado:
                mcp.evaluar_para_mcp(proy, {"medida": {"id": "d.x"}, "evidencia": {}})

        self.assertEqual(capturado.exception.codigo, "ESCALARES_NO_AUTORIZADAS")
