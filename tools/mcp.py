"""Servidor MCP de sólo lectura para consultar qué medidas obligan a un proyecto.

El proyecto y la autorización para ejecutar sus escalares se fijan al arrancar. Eso evita que
una instrucción recibida por MCP pueda ampliar la raíz o concederse permiso para ejecutar código.
El transporte se escribe a mano porque el servidor necesita una frontera pequeña y auditable:
JSON-RPC UTF-8 compacto sobre stdio, un mensaje por línea y sin cabeceras. A diferencia de LSP,
el transporte stdio de MCP no usa enmarcado ``Content-Length``. ``stdout`` queda reservado en
exclusiva al protocolo; cualquier traza o mensaje humano debe ir a ``stderr``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path = [str(RAIZ), *sys.path]

from nucleo.medida import relaciones_de_medida  # noqa: E402
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables,  # noqa: E402
                             ID_MEDIDA_RE, Proyecto, ProyectoInvalido,
                             catalogo_efectivo,
                             escalares_del_proyecto, macros_del_proyecto,
                             presentar_ruta)
from nucleo.version import VERSION_DISTRIBUCION  # noqa: E402
from tools.medida import ejercicio_del_catalogo  # noqa: E402
from tools.sesion import resolver_cli  # noqa: E402


PROTOCOLO = "2025-11-25"
NOMBRE_SERVIDOR = "oracle-mcp"

HERRAMIENTA_CATALOGO = {
    "name": "oracle_catalogo_efectivo",
    "title": "Catálogo efectivo de Oracle",
    "description": (
        "Consulta las medidas que obligan al proyecto fijado al arrancar el servidor. Sin ids "
        "devuelve un índice compacto; con ids devuelve el detalle de esas medidas. Usa "
        "catalogo_efectivo: no confunde todo lo instalado con lo que tiene jurisdicción aquí. "
        "No evalúa evidencia ni escribe archivos."
    ),
    "annotations": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
    "inputSchema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "ids": {
                "type": "array",
                "minItems": 1,
                "uniqueItems": True,
                "items": {
                    "type": "string",
                    "pattern": "^[a-z][a-z0-9_]*(?:\\.[a-z][a-z0-9_]*)+$",
                },
                "description": "Ids efectivos cuyo detalle se pide. Omitir para listar todos.",
            }
        },
    },
    "outputSchema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "esquema", "oracle_version", "proyecto", "huella_proyecto", "detalle",
            "total", "medidas",
        ],
        "properties": {
            "esquema": {"const": "oracle.mcp/catalogo-efectivo/v1"},
            "oracle_version": {"type": "string"},
            "proyecto": {"type": "string"},
            "huella_proyecto": {
                "type": "string", "pattern": "^[0-9a-f]{64}$",
            },
            "detalle": {"type": "boolean"},
            "total": {"type": "integer", "minimum": 0},
            "medidas": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["id", "origen", "fijacion"],
                    "properties": {
                        "id": {"type": "string"},
                        "origen": {"type": "string"},
                        "relaciones": {
                            "type": "array", "items": {"type": "string"},
                            "uniqueItems": True,
                        },
                        "fijacion": {
                            "enum": ["evidencia", "arnes", "heredada", "sin_fijar"],
                        },
                        "ambito": {
                            "enum": ["universal", "del_origen", "sin_declarar"],
                        },
                        "requiere": {
                            "type": "array", "items": {"type": "string"},
                            "uniqueItems": True,
                        },
                        "umbral": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["operador", "valor", "segun", "porque"],
                            "properties": {
                                "operador": {"type": "string"},
                                "valor": {"type": ["string", "number", "boolean"]},
                                "segun": {"type": "string"},
                                "porque": {"type": "string"},
                            },
                        },
                        "alcance": {"type": "string"},
                        "fuente": {"type": "string"},
                        "fuente_sha256": {
                            "type": "string", "pattern": "^[0-9a-f]{64}$",
                        },
                    },
                },
            },
        },
    },
}

HERRAMIENTAS = [HERRAMIENTA_CATALOGO]


@dataclass
class ErrorHerramienta(Exception):
    """Error corregible por quien llama, separado de los errores del sobre JSON-RPC."""

    codigo: str
    mensaje: str

    def __str__(self) -> str:
        return f"{self.codigo} — {self.mensaje}"


def _json_compacto(valor) -> str:
    return json.dumps(valor, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _leer_mensaje(entrada):
    """Lee una línea JSON-RPC; un EOF sin el ``\n`` final es transporte truncado."""
    linea = entrada.readline()
    if not linea:
        return None
    if not linea.endswith(b"\n"):
        raise EOFError("mensaje MCP truncado: falta el delimitador '\\n'")
    cuerpo = linea[:-1]
    if cuerpo.endswith(b"\r"):
        raise ValueError("delimitador MCP inválido: se esperaba '\\n', no '\\r\\n'")
    return json.loads(cuerpo.decode("utf-8"))


def _enviar(salida, mensaje: dict) -> None:
    """Escribe un JSON compacto y un solo delimitador; los saltos internos quedan escapados."""
    cuerpo = json.dumps(mensaje, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    salida.write(cuerpo + b"\n")
    salida.flush()


def _origen_texto(origen) -> str:
    return (origen.clase if origen.clase == "proyecto"
            else f"{origen.clase}:{origen.identificador}")


def _rutas_de_directorio(directorio: Path) -> list[Path]:
    """Enumera datos opcionales sin permitir que un symlink amplíe la raíz consultada."""
    if not directorio.exists() and not directorio.is_symlink():
        return []
    if directorio.is_symlink() or not directorio.is_dir():
        raise ProyectoInvalido(f"`{directorio.name}/` debe ser un directorio físico")
    raiz = directorio.resolve()
    rutas = []
    for ruta in directorio.rglob("*"):
        if ruta.is_dir():
            continue
        if ruta.is_symlink() or not ruta.is_file():
            raise ProyectoInvalido(f"{ruta} debe ser un archivo físico, no un symlink")
        try:
            ruta.resolve().relative_to(raiz)
        except (OSError, ValueError) as e:
            raise ProyectoInvalido(f"{ruta} no está confinado en {raiz}") from e
        rutas.append(ruta)
    return sorted(rutas)


def _entradas_de_huella(proy: Proyecto, catalogo) -> list[Path]:
    """Reúne exactamente las fuentes efectivas y la evidencia que sostuvo sus fijaciones."""
    entradas = {entrada.ruta.resolve() for entrada in catalogo.entradas.values()}
    oracle_json = proy.raiz / "oracle.json"
    if oracle_json.exists() or oracle_json.is_symlink():
        entradas.add(oracle_json.resolve())
    for nombre in ("corpus", "diferencial", "macros"):
        entradas.update(ruta.resolve() for ruta in _rutas_de_directorio(proy.raiz / nombre))

    escalares = proy.raiz / "escalares.py"
    if escalares.exists() or escalares.is_symlink():
        entradas.add(escalares.resolve())
    return sorted(entradas)


def _huella_proyecto(proy: Proyecto, catalogo) -> str:
    """Firma ruta absoluta y bytes con el algoritmo reproducible publicado en el contrato."""
    huella = hashlib.sha256()
    for ruta in _entradas_de_huella(proy, catalogo):
        try:
            contenido = ruta.read_bytes()
        except OSError as e:
            raise OSError(f"no se pudo leer {ruta}: {e}") from e
        huella.update(str(ruta).encode("utf-8") + b"\0" + contenido + b"\0")
    return huella.hexdigest()


def _huella_final(proy: Proyecto, catalogo, refrescar) -> str:
    """Vuelve comparable una desaparición o rotura ocurrida después de la primera lectura."""
    try:
        catalogo = refrescar()
        return _huella_proyecto(proy, catalogo)
    except Exception as e:
        marca = {"error": type(e).__name__, "mensaje": str(e)}
        return hashlib.sha256(_json_compacto(marca).encode("utf-8")).hexdigest()


@contextmanager
def _estado_estable(proy: Proyecto, catalogo, refrescar):
    """Comprueba la huella también cuando la operación falla por el cambio que está detectando."""
    inicial = _huella_proyecto(proy, catalogo)
    try:
        yield inicial
    except Exception:
        final = _huella_final(proy, catalogo, refrescar)
        if inicial != final:
            raise ErrorHerramienta(
                "PROYECTO_CAMBIO_DURANTE_LA_CONSULTA",
                f"huella inicial {inicial} y final {final}; reintentá sobre un estado estable.",
            )
        raise
    final = _huella_final(proy, catalogo, refrescar)
    if inicial != final:
        raise ErrorHerramienta(
            "PROYECTO_CAMBIO_DURANTE_LA_CONSULTA",
            f"huella inicial {inicial} y final {final}; reintentá sobre un estado estable.",
        )


def _validar_argumentos(argumentos) -> tuple[str, ...] | None:
    """Valida el esquema cerrado sin sumar una dependencia que pueda divergir del servidor."""
    if not isinstance(argumentos, dict):
        raise ErrorHerramienta(
            "ARGUMENTOS_INVALIDOS",
            f"$: {_json_compacto(argumentos)}; se esperaba un objeto con el campo opcional ids.",
        )
    extras = sorted(set(argumentos) - {"ids"})
    if extras:
        raise ErrorHerramienta(
            "ARGUMENTOS_INVALIDOS",
            f"$.{extras[0]}: {_json_compacto(argumentos[extras[0]])}; se esperaba ninguna "
            "propiedad adicional.",
        )
    if "ids" not in argumentos:
        return None
    ids = argumentos["ids"]
    if not isinstance(ids, list) or not ids:
        raise ErrorHerramienta(
            "ARGUMENTOS_INVALIDOS",
            f"$.ids: {_json_compacto(ids)}; se esperaba una lista no vacía de ids únicos.",
        )
    vistos = set()
    for indice, mid in enumerate(ids):
        if not isinstance(mid, str) or ID_MEDIDA_RE.fullmatch(mid) is None:
            raise ErrorHerramienta(
                "ARGUMENTOS_INVALIDOS",
                f"$.ids[{indice}]: {_json_compacto(mid)}; se esperaba un id dominio.nombre "
                "portable.",
            )
        if mid in vistos:
            raise ErrorHerramienta(
                "ARGUMENTOS_INVALIDOS",
                f"$.ids[{indice}]: {_json_compacto(mid)}; se esperaba un id no repetido.",
            )
        vistos.add(mid)
    return tuple(ids)


def _fijacion(mid: str, ejercicio) -> str:
    """Proyecta el juicio compartido; no vuelve a definir cuándo una medida está ejercitada."""
    if mid in ejercicio.heredadas:
        return "heredada"
    if ejercicio.casos_por_medida.get(mid, 0):
        return "evidencia"
    if mid in ejercicio.aparte:
        return "arnes"
    if mid in ejercicio.sin_ejercitar:
        return "sin_fijar"
    raise ErrorHerramienta(
        "EVIDENCIA_INCOMPLETA",
        f"no se pudo juzgar la fijación de «{mid}». No se devolvieron fijaciones parciales.",
    )


def _fila_compacta(mid: str, catalogo, ejercicio) -> dict:
    entrada = catalogo.entradas[mid]
    return {
        "id": mid,
        "origen": _origen_texto(entrada.origen),
        "fijacion": _fijacion(mid, ejercicio),
    }


def _fila_detallada(proy: Proyecto, mid: str, catalogo, ejercicio) -> dict:
    medida = catalogo[mid]
    entrada = catalogo.entradas[mid]
    return {
        **_fila_compacta(mid, catalogo, ejercicio),
        "relaciones": list(relaciones_de_medida(medida)),
        "ambito": medida.ambito,
        "requiere": list(medida.requiere),
        "umbral": {
            "operador": medida.op,
            "valor": medida.limite,
            "segun": medida.segun,
            "porque": medida.porque,
        },
        "alcance": medida.alcance,
        "fuente": presentar_ruta(proy, entrada.ruta),
        "fuente_sha256": hashlib.sha256(entrada.ruta.read_bytes()).hexdigest(),
    }


def _error_id_ausente(mid: str, proy: Proyecto, catalogo) -> ErrorHerramienta:
    entrada = catalogo.entradas_seleccionadas.get(mid)
    if entrada is None:
        return ErrorHerramienta(
            "MEDIDA_DESCONOCIDA",
            f"«{mid}» no aparece en las fuentes seleccionadas; consultá "
            "oracle_catalogo_efectivo sin ids.",
        )
    return ErrorHerramienta(
        "MEDIDA_NO_EFECTIVA",
        f"«{mid}» existe en {_origen_texto(entrada.origen)}, pero su ambito "
        f"«{entrada.medida.ambito}» no obliga a «{proy.raiz.resolve()}».",
    )


def _error_catalogo(proy: Proyecto, error: Exception) -> ErrorHerramienta:
    """Conserva la fuente concreta del núcleo y presenta como relativa la que es del proyecto."""
    motivo = str(error)
    prefijo = str(proy.raiz.resolve()) + "/"
    motivo = motivo.replace(prefijo, "")
    return ErrorHerramienta(
        "CATALOGO_INVALIDO", f"{motivo}. No se devolvió un catálogo parcial.")


def catalogo_para_mcp(proy: Proyecto, argumentos, *, confiar_escalares: bool = False) -> dict:
    """Construye una respuesta completa o un error explícito; nunca convierte una falla en cero."""
    ids = _validar_argumentos(argumentos)
    try:
        # El try incluye la ENTRADA al context manager: la falta de autorización levanta ahí, no
        # dentro del cuerpo, y de otro modo escaparía como una traza que corrompe el protocolo.
        with escalares_del_proyecto(proy, confiar=confiar_escalares):
            try:
                macros = macros_del_proyecto(proy)
                # Esta es la autoridad de la selección publicada. El núcleo conserva también qué
                # descartó para explicar la jurisdicción sin abrir un segundo camino de carga acá.
                catalogo = catalogo_efectivo(proy, macros=macros)
            except ProyectoInvalido:
                raise
            except Exception as e:
                raise _error_catalogo(proy, e) from e

            def refrescar():
                return catalogo_efectivo(proy, macros=macros_del_proyecto(proy))

            with _estado_estable(proy, catalogo, refrescar) as huella_inicial:
                try:
                    ejercicio = ejercicio_del_catalogo(proy, catalogo, macros)
                except Exception as e:
                    raise ErrorHerramienta(
                        "EVIDENCIA_INCOMPLETA",
                        f"no se pudo juzgar la fijación: {e}. "
                        "No se devolvieron fijaciones parciales.",
                    ) from e
                if not ejercicio.hubo_jueza:
                    raise ErrorHerramienta(
                        "EVIDENCIA_INCOMPLETA",
                        "no se pudo juzgar la fijación: falta la medida jueza "
                        "meta.toda_medida_esta_ejercitada. "
                        "No se devolvieron fijaciones parciales.",
                    )
                if not ejercicio.completa:
                    raise ErrorHerramienta(
                        "EVIDENCIA_INCOMPLETA",
                        "no se pudo juzgar la fijación: el catálogo o un diferencial no se pudo "
                        "reunir por completo. No se devolvieron fijaciones parciales.",
                    )

                seleccion = sorted(catalogo) if ids is None else sorted(ids)
                ausente = next((mid for mid in seleccion if mid not in catalogo), None)
                if ausente is not None:
                    raise _error_id_ausente(ausente, proy, catalogo)

                medidas = [
                    (_fila_compacta(mid, catalogo, ejercicio) if ids is None
                     else _fila_detallada(proy, mid, catalogo, ejercicio))
                    for mid in seleccion
                ]
    except ErrorHerramienta:
        raise
    except EscalaresNoConfiables as e:
        archivo = str(e).split(" es código Python externo", 1)[0]
        raise ErrorHerramienta(
            "ESCALARES_NO_AUTORIZADAS",
            f"{archivo} es código externo; autorizalo en la configuración de arranque del "
            "servidor, no en esta llamada.",
        ) from e
    except EscalaresInvalidas as e:
        raise _error_catalogo(proy, e) from e
    except ProyectoInvalido as e:
        raise ErrorHerramienta(
            "PROYECTO_INVALIDO", f"{proy.raiz.resolve()}: {e}.",
        ) from e
    except Exception as e:
        raise _error_catalogo(proy, e) from e

    return {
        "esquema": "oracle.mcp/catalogo-efectivo/v1",
        "oracle_version": VERSION_DISTRIBUCION,
        "proyecto": str(proy.raiz.resolve()),
        "huella_proyecto": huella_inicial,
        "detalle": ids is not None,
        "total": len(catalogo),
        "medidas": medidas,
    }


class Servidor:
    """Despachador explícito: una sesión no puede inventar métodos ni herramientas."""

    def __init__(self, proy: Proyecto, salida, *, confiar_escalares: bool = False) -> None:
        self.proy = Proyecto(proy.raiz.resolve())
        self.salida = salida
        self.confiar_escalares = confiar_escalares
        self.estado = "nuevo"

    def _respuesta(self, mensaje: dict, resultado) -> None:
        _enviar(self.salida, {
            "jsonrpc": "2.0", "id": mensaje["id"], "result": resultado,
        })

    def _error(self, mensaje: dict, codigo: int, texto: str) -> None:
        mid = mensaje.get("id") if isinstance(mensaje, dict) else None
        _enviar(self.salida, {
            "jsonrpc": "2.0", "id": mid,
            "error": {"code": codigo, "message": texto},
        })

    def _resultado_herramienta(self, mensaje: dict, argumentos) -> None:
        try:
            contenido = catalogo_para_mcp(
                self.proy, argumentos, confiar_escalares=self.confiar_escalares)
        except ErrorHerramienta as e:
            self._respuesta(mensaje, {
                "content": [{"type": "text", "text": str(e)}],
                "isError": True,
            })
            return
        self._respuesta(mensaje, {
            "content": [{"type": "text", "text": _json_compacto(contenido)}],
            "structuredContent": contenido,
            "isError": False,
        })

    def manejar(self, mensaje) -> bool:
        if not isinstance(mensaje, dict) or mensaje.get("jsonrpc") != "2.0" or not isinstance(
                mensaje.get("method"), str):
            self._error(
                mensaje if isinstance(mensaje, dict) else {}, -32600,
                "pedido JSON-RPC inválido: se esperaba un objeto con jsonrpc '2.0' y method.",
            )
            return True
        metodo = mensaje["method"]
        es_pedido = "id" in mensaje

        if metodo == "initialize":
            if not es_pedido or self.estado != "nuevo" or not isinstance(
                    mensaje.get("params", {}), dict):
                if es_pedido:
                    self._error(
                        mensaje, -32600,
                        "pedido JSON-RPC inválido: initialize fuera de orden.")
                return True
            self.estado = "inicializando"
            self._respuesta(mensaje, {
                "protocolVersion": PROTOCOLO,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": NOMBRE_SERVIDOR, "version": VERSION_DISTRIBUCION},
            })
        elif metodo == "notifications/initialized":
            if not es_pedido and self.estado == "inicializando":
                self.estado = "inicializado"
        elif metodo == "ping" and es_pedido and self.estado == "inicializado":
            self._respuesta(mensaje, {})
        elif metodo == "tools/list" and es_pedido and self.estado == "inicializado":
            params = mensaje.get("params", {})
            if not isinstance(params, dict) or set(params) - {"cursor"}:
                self._error(mensaje, -32602, "tools/list inválido: parámetros inesperados.")
            else:
                self._respuesta(mensaje, {"tools": HERRAMIENTAS})
        elif metodo == "tools/call" and es_pedido and self.estado == "inicializado":
            params = mensaje.get("params")
            if (not isinstance(params, dict) or set(params) - {"name", "arguments"}
                    or not isinstance(params.get("name"), str)):
                self._error(mensaje, -32602, "tools/call inválido: se esperaba name y arguments.")
            elif params["name"] != HERRAMIENTA_CATALOGO["name"]:
                self._error(
                    mensaje, -32602,
                    f"tools/call inválido: herramienta desconocida: {params['name']}",
                )
            else:
                self._resultado_herramienta(mensaje, params.get("arguments", {}))
        elif metodo == "shutdown" and es_pedido and self.estado in {
                "inicializando", "inicializado"}:
            self.estado = "apagado"
            self._respuesta(mensaje, None)
        elif metodo == "exit" and not es_pedido:
            return False
        elif es_pedido:
            self._error(mensaje, -32601, f"método no soportado: {metodo}")
        return True


def servir(proy: Proyecto, entrada, salida, *, confiar_escalares: bool = False) -> int:
    servidor = Servidor(proy, salida, confiar_escalares=confiar_escalares)
    while True:
        try:
            mensaje = _leer_mensaje(entrada)
        except json.JSONDecodeError as e:
            _enviar(salida, {
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": f"JSON inválido: {e}"},
            })
            continue
        except (EOFError, UnicodeError, ValueError) as e:
            print(f"TRANSPORTE MCP INVÁLIDO — {e}", file=sys.stderr)
            return 1
        if mensaje is None:
            return 0 if servidor.estado == "apagado" else 1
        if not servidor.manejar(mensaje):
            return 0 if servidor.estado == "apagado" else 1


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        description="Servidor MCP de sólo lectura para un proyecto Oracle.")
    parser.add_argument("--proyecto", help="raíz fijada durante toda la vida del servidor")
    parser.add_argument(
        "--confiar-escalares", action="store_true",
        help="autoriza ejecutar escalares.py del proyecto al consultar",
    )
    args = parser.parse_args(argv)
    argumentos_proyecto = (["--proyecto", args.proyecto] if args.proyecto is not None else [])
    proy = resolver_cli(argumentos_proyecto)
    if proy is None:
        return 1
    return servir(
        proy, sys.stdin.buffer, sys.stdout.buffer,
        confiar_escalares=args.confiar_escalares,
    )


for _punto_de_entrada in {"__main__": (main,)}.get(__name__, ()):
    sys.exit(_punto_de_entrada())
