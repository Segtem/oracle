"""Servidor LSP mínimo de Oracle: publica diagnósticos por stdio."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

RAIZ = Path(__file__).resolve().parents[1]
sys.path = [str(RAIZ), *sys.path]

from nucleo.caso import CasoMalDeclarado, cargar_casos, leer as leer_caso  # noqa: E402
from nucleo.medida import Medida, MedidaMalDeclarada  # noqa: E402
from nucleo.proyecto import Proyecto, macros_del_proyecto  # noqa: E402
from nucleo.sintaxis import ErrorSintaxis, leer_con_mapa  # noqa: E402
from nucleo.version import exigir_sintaxis_compatible  # noqa: E402
from tools.medida import _evaluadas_aparte  # noqa: E402
from tools.sesion import resolver_cli  # noqa: E402

ERROR = 1
AVISO = 2


def _rango(linea: int, columna: int) -> dict:
    inicio = {"line": linea - 1, "character": columna - 1}
    return {"start": inicio, "end": {"line": inicio["line"],
                                      "character": inicio["character"] + 1}}


def _diagnostico(mensaje: str, severidad: int, linea: int = 1, columna: int = 1) -> dict:
    return {
        "range": _rango(linea, columna),
        "severity": severidad,
        "source": "oracle",
        "message": mensaje,
    }


def diagnosticar(proy: Proyecto, ruta: Path, texto: str) -> list[dict]:
    try:
        if ruta.suffix == ".caso":
            leer_caso(texto)
            return []
        if ruta.suffix != ".oracle":
            return []
        macros = macros_del_proyecto(proy)
        lectura = leer_con_mapa(texto, macros=macros)
        exigir_sintaxis_compatible(lectura.version)
        medida = Medida.de_datos(lectura.datos, macros=macros)
        try:
            ruta.resolve().relative_to(proy.catalogos.resolve())
        except ValueError:
            pass
        else:
            casos = cargar_casos(proy.corpus) if proy.corpus.is_dir() else []
            aparte = _evaluadas_aparte(proy, {medida.id: medida})
            if (not any(caso.get("medida") == medida.id for caso in casos)
                    and medida.id not in aparte):
                ubicacion = lectura.ubicacion("1")
                return [_diagnostico(
                    "SIN FIJAR — ninguna evidencia la pone a prueba", AVISO,
                    ubicacion.linea, ubicacion.columna)]
        return []
    except ErrorSintaxis as e:
        return [_diagnostico(str(e), ERROR, e.linea, e.columna)]
    except (MedidaMalDeclarada, CasoMalDeclarado, ValueError) as e:
        return [_diagnostico(str(e), ERROR)]


def _ruta_de_uri(uri: str) -> Path:
    partes = urlsplit(uri)
    if partes.scheme != "file" or partes.netloc not in ("", "localhost"):
        raise ValueError(f"URI de archivo inválida: {uri!r}")
    return Path(unquote(partes.path))


def _leer_mensaje(entrada) -> dict | None:
    cabeceras = {}
    while True:
        linea = entrada.readline()
        if not linea:
            if cabeceras:
                raise EOFError("cabecera truncada")
            return None
        if linea in (b"\r\n", b"\n"):
            break
        nombre, separador, valor = linea.decode("ascii").partition(":")
        if not separador:
            raise ValueError("cabecera LSP sin ':'")
        cabeceras[nombre.lower()] = valor.strip()
    largo = int(cabeceras["content-length"])
    cuerpo = entrada.read(largo)
    if len(cuerpo) != largo:
        raise EOFError("cuerpo LSP truncado")
    mensaje = json.loads(cuerpo.decode("utf-8"))
    if not isinstance(mensaje, dict):
        raise ValueError("el mensaje LSP debe ser un objeto JSON")
    return mensaje


def _enviar(salida, mensaje: dict) -> None:
    cuerpo = json.dumps(mensaje, separators=(",", ":")).encode("utf-8")
    salida.write(f"Content-Length: {len(cuerpo)}\r\n\r\n".encode("ascii") + cuerpo)
    salida.flush()


class Servidor:
    def __init__(self, proy: Proyecto, salida) -> None:
        self.proy = proy
        self.salida = salida
        self.apagado = False

    def _respuesta(self, mensaje: dict, resultado) -> None:
        _enviar(self.salida, {"jsonrpc": "2.0", "id": mensaje["id"], "result": resultado})

    def _publicar(self, uri: str, texto: str | None, version=None) -> None:
        parametros = {"uri": uri, "diagnostics": (
            [] if texto is None else diagnosticar(self.proy, _ruta_de_uri(uri), texto))}
        if version is not None:
            parametros["version"] = version
        _enviar(self.salida, {
            "jsonrpc": "2.0", "method": "textDocument/publishDiagnostics",
            "params": parametros,
        })

    def manejar(self, mensaje: dict) -> bool:
        metodo = mensaje.get("method")
        if metodo == "initialize":
            self._respuesta(mensaje, {"capabilities": {
                "textDocumentSync": {"openClose": True, "change": 1},
            }})
        elif metodo == "shutdown":
            self.apagado = True
            self._respuesta(mensaje, None)
        elif metodo == "exit":
            return False
        elif metodo == "textDocument/didOpen":
            documento = mensaje["params"]["textDocument"]
            self._publicar(documento["uri"], documento["text"], documento.get("version"))
        elif metodo == "textDocument/didChange":
            params = mensaje["params"]
            cambios = params["contentChanges"]
            if len(cambios) != 1 or set(cambios[0]) != {"text"}:
                raise ValueError("didChange requiere un único cambio de texto completo")
            documento = params["textDocument"]
            self._publicar(documento["uri"], cambios[0]["text"], documento.get("version"))
        elif metodo == "textDocument/didClose":
            self._publicar(mensaje["params"]["textDocument"]["uri"], None)
        elif "id" in mensaje:
            _enviar(self.salida, {
                "jsonrpc": "2.0", "id": mensaje["id"],
                "error": {"code": -32601, "message": f"método no soportado: {metodo}"},
            })
        return True


def servir(proy: Proyecto, entrada, salida) -> int:
    servidor = Servidor(proy, salida)
    while True:
        mensaje = _leer_mensaje(entrada)
        if mensaje is None or not servidor.manejar(mensaje):
            return 0 if servidor.apagado else 1


def main(argv: list[str] | None = None) -> int:
    proy = resolver_cli(list(sys.argv[1:] if argv is None else argv))
    if proy is None:
        return 1
    return servir(proy, sys.stdin.buffer, sys.stdout.buffer)


for _punto_de_entrada in {"__main__": (main,)}.get(__name__, ()):
    sys.exit(_punto_de_entrada())
