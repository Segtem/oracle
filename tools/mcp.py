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

from nucleo.medida import Medida, MedidaMalDeclarada, relaciones_de_medida  # noqa: E402
from nucleo.proyecto import (EscalaresInvalidas, EscalaresNoConfiables,  # noqa: E402
                             ID_MEDIDA_RE, Proyecto, ProyectoInvalido,
                             catalogo_efectivo,
                             escalares_del_proyecto, macros_del_proyecto,
                             presentar_ruta, relaciones_del_proyecto)
from nucleo.sintaxis import ErrorSintaxis, fragmento_de_error, leer_con_mapa  # noqa: E402
from nucleo.version import (VERSION_DISTRIBUCION, VersionInvalida,  # noqa: E402
                            exigir_sintaxis_compatible)
from tools.medida import ejercicio_del_catalogo, relaciones_por_alias  # noqa: E402
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

HERRAMIENTA_EVALUAR = {
    "name": "oracle_evaluar",
    "title": "Evaluar una medida en memoria",
    "description": (
        "Evalúa una medida efectiva por id o un texto de medida sin guardarlo contra una "
        "evidencia JSON. Devuelve verde, rojo o sin_evidencia como estados distintos, además "
        "del valor, umbral, testigos y alcance. Use esta herramienta para entender conducta "
        "puntual; no prueba que la medida sea correcta."
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
        "required": ["medida", "evidencia"],
        "properties": {
            "medida": {
                "oneOf": [
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["id"],
                        "properties": {
                            "id": {
                                "type": "string",
                                "pattern": "^[a-z][a-z0-9_]*(?:\\.[a-z][a-z0-9_]*)+$",
                            },
                        },
                    },
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["texto", "formato"],
                        "properties": {
                            "texto": {"type": "string"},
                            "formato": {"enum": ["oracle", "json"]},
                        },
                    },
                ],
            },
            "evidencia": {"$ref": "#/$defs/evidencia"},
        },
        "$defs": {
            "evidencia": {
                "type": "object",
                "additionalProperties": {
                    "type": "array",
                    "items": {"type": "object"},
                },
            },
        },
    },
    "outputSchema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "esquema", "oracle_version", "proyecto", "entrada_sha256", "medida",
            "estado", "valor", "umbral", "testigos", "testigos_omitidos", "alcance",
            "alcance_derivado", "advertencias",
        ],
        "properties": {
            "esquema": {"const": "oracle.mcp/evaluacion/v1"},
            "oracle_version": {"type": "string"},
            "proyecto": {"type": "string"},
            "entrada_sha256": {
                "type": "string", "pattern": "^[0-9a-f]{64}$",
            },
            "medida": {"type": "string"},
            "estado": {"enum": ["verde", "rojo", "sin_evidencia"]},
            "valor": {"type": "number"},
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
            "testigos": {
                "type": "array", "items": {"type": "object"}, "maxItems": 5,
            },
            "testigos_omitidos": {"type": "integer", "minimum": 0},
            "alcance": {"type": "string"},
            "alcance_derivado": {"type": "array", "items": {"type": "string"}},
            "advertencias": {"type": "array", "items": {"type": "string"}},
        },
    },
}

# La declaración es la del contrato, palabra por palabra: `MCP-CONTRATO.md` es normativo y un
# test compara los dos. Divergir acá sería anunciar una herramienta que nadie documentó.
HERRAMIENTA_DESAFIAR = {
    "name": "oracle_desafiar",
    "title": "Desafiar una medida con corpus y mutación",
    "description": "Falsa en memoria una medida por id o texto. Combina, si se pide, sus casos del corpus y diferenciales del proyecto con casos efímeros, exige ambas polaridades y ejecuta mutación de medidas. Informa discordancias, mutantes sobrevivientes y rechazos del álgebra; nunca declara que la medida sea semánticamente correcta ni escribe evidencia.",
    "annotations": {
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    },
    "inputSchema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "medida"
        ],
        "properties": {
            "medida": {
                "oneOf": [
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "id"
                        ],
                        "properties": {
                            "id": {
                                "type": "string",
                                "pattern": "^[a-z][a-z0-9_]*(?:\\.[a-z][a-z0-9_]*)+$"
                            }
                        }
                    },
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "texto",
                            "formato"
                        ],
                        "properties": {
                            "texto": {
                                "type": "string"
                            },
                            "formato": {
                                "enum": [
                                    "oracle",
                                    "json"
                                ]
                            }
                        }
                    }
                ]
            },
            "usar_evidencia_del_proyecto": {
                "type": "boolean",
                "default": True,
                "description": "Incluye corpus y diferenciales que nombran el id de la medida."
            },
            "casos": {
                "type": "array",
                "default": [],
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "id",
                        "espera",
                        "evidencia"
                    ],
                    "properties": {
                        "id": {
                            "type": "string",
                            "minLength": 1
                        },
                        "espera": {
                            "enum": [
                                "verde",
                                "rojo"
                            ]
                        },
                        "evidencia": {
                            "$ref": "#/$defs/evidencia"
                        }
                    }
                }
            }
        },
        "$defs": {
            "evidencia": {
                "type": "object",
                "additionalProperties": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                }
            }
        }
    },
    "outputSchema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "esquema",
            "oracle_version",
            "proyecto",
            "entrada_sha256",
            "medida",
            "conclusion",
            "casos",
            "discordancias",
            "mutacion",
            "advertencias"
        ],
        "properties": {
            "esquema": {
                "const": "oracle.mcp/desafio/v1"
            },
            "oracle_version": {
                "type": "string"
            },
            "proyecto": {
                "type": "string"
            },
            "entrada_sha256": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$"
            },
            "medida": {
                "type": "string"
            },
            "conclusion": {
                "enum": [
                    "original_no_reproduce",
                    "faltan_polaridades",
                    "sin_mutantes",
                    "sobrevivientes",
                    "sin_sobrevivientes_con_rechazos",
                    "todos_detectados_por_conducta"
                ]
            },
            "casos": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "total",
                    "del_proyecto",
                    "efimeros",
                    "esperan_verde",
                    "esperan_rojo"
                ],
                "properties": {
                    "total": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "del_proyecto": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "efimeros": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "esperan_verde": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "esperan_rojo": {
                        "type": "integer",
                        "minimum": 0
                    }
                }
            },
            "discordancias": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "caso",
                        "esperado",
                        "obtenido"
                    ],
                    "properties": {
                        "caso": {
                            "type": "string"
                        },
                        "esperado": {
                            "enum": [
                                "verde",
                                "rojo"
                            ]
                        },
                        "obtenido": {
                            "enum": [
                                "verde",
                                "rojo",
                                "sin_evidencia",
                                "error"
                            ]
                        }
                    }
                }
            },
            "mutacion": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "generados",
                    "detectados_por_conducta",
                    "rechazados_por_el_algebra",
                    "no_detectados"
                ],
                "properties": {
                    "generados": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "detectados_por_conducta": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "rechazados_por_el_algebra": {
                        "type": "integer",
                        "minimum": 0
                    },
                    "no_detectados": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": [
                                "id",
                                "cambio",
                                "estado"
                            ],
                            "properties": {
                                "id": {
                                    "type": "string"
                                },
                                "cambio": {
                                    "type": "string"
                                },
                                "estado": {
                                    "enum": [
                                        "sobrevivio",
                                        "rechazado_por_el_algebra"
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            "advertencias": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            }
        }
    }
}

HERRAMIENTAS = [HERRAMIENTA_CATALOGO, HERRAMIENTA_EVALUAR, HERRAMIENTA_DESAFIAR]


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


def _validar_evaluacion(argumentos) -> tuple[dict, dict]:
    """Aplica la unión cerrada también en el servidor; el esquema del cliente no es autoridad."""
    if not isinstance(argumentos, dict):
        raise ErrorHerramienta(
            "ARGUMENTOS_INVALIDOS",
            f"$: {_json_compacto(argumentos)}; se esperaba un objeto con medida y evidencia.",
        )
    extras = sorted(set(argumentos) - {"medida", "evidencia"})
    if extras:
        extra = extras[0]
        raise ErrorHerramienta(
            "ARGUMENTOS_INVALIDOS",
            f"$.{extra}: {_json_compacto(argumentos[extra])}; se esperaba ninguna propiedad "
            "adicional.",
        )
    faltantes = [nombre for nombre in ("medida", "evidencia") if nombre not in argumentos]
    if faltantes:
        raise ErrorHerramienta(
            "ARGUMENTOS_INVALIDOS",
            f"$: falta {faltantes[0]}; se esperaban los campos medida y evidencia.",
        )

    especificacion = argumentos["medida"]
    if not isinstance(especificacion, dict):
        raise ErrorHerramienta(
            "ARGUMENTOS_INVALIDOS",
            f"$.medida: {_json_compacto(especificacion)}; se esperaba {{id}} o "
            "{texto, formato}.",
        )
    campos = set(especificacion)
    if campos == {"id"}:
        mid = especificacion["id"]
        if not isinstance(mid, str) or ID_MEDIDA_RE.fullmatch(mid) is None:
            raise ErrorHerramienta(
                "ARGUMENTOS_INVALIDOS",
                f"$.medida.id: {_json_compacto(mid)}; se esperaba un id dominio.nombre "
                "portable.",
            )
    elif campos == {"texto", "formato"}:
        texto = especificacion["texto"]
        formato = especificacion["formato"]
        if not isinstance(texto, str):
            raise ErrorHerramienta(
                "ARGUMENTOS_INVALIDOS",
                f"$.medida.texto: {_json_compacto(texto)}; se esperaba texto.",
            )
        if formato not in ("oracle", "json") or not isinstance(formato, str):
            raise ErrorHerramienta(
                "ARGUMENTOS_INVALIDOS",
                f"$.medida.formato: {_json_compacto(formato)}; se esperaba oracle o json.",
            )
    else:
        raise ErrorHerramienta(
            "ARGUMENTOS_INVALIDOS",
            f"$.medida: {_json_compacto(especificacion)}; se esperaba exactamente {{id}} o "
            "{texto, formato}; archivo no está admitido.",
        )

    evidencia = argumentos["evidencia"]
    if not isinstance(evidencia, dict):
        raise ErrorHerramienta(
            "ARGUMENTOS_INVALIDOS",
            f"$.evidencia: {_json_compacto(evidencia)}; se esperaba un objeto de relaciones.",
        )
    for relacion, filas in evidencia.items():
        if not isinstance(filas, list):
            raise ErrorHerramienta(
                "ARGUMENTOS_INVALIDOS",
                f"$.evidencia.{relacion}: {_json_compacto(filas)}; se esperaba una lista de "
                "filas objeto.",
            )
        for indice, fila in enumerate(filas):
            if not isinstance(fila, dict):
                raise ErrorHerramienta(
                    "ARGUMENTOS_INVALIDOS",
                    f"$.evidencia.{relacion}[{indice}]: {_json_compacto(fila)}; se esperaba "
                    "una fila objeto.",
                )
    return especificacion, evidencia


def _medida_en_memoria(especificacion: dict, macros) -> Medida:
    """Carga sólo bytes recibidos; ni el modo JSON ni el modo Oracle aceptan una ruta lateral."""
    texto = especificacion["texto"]
    formato = especificacion["formato"]
    try:
        if formato == "json":
            datos = json.loads(texto)
        else:
            lectura = leer_con_mapa(texto, macros=macros)
            exigir_sintaxis_compatible(lectura.version)
            datos = lectura.datos
        return Medida.de_datos(datos, macros=macros)
    except json.JSONDecodeError as e:
        raise ErrorHerramienta(
            "MEDIDA_INVALIDA", f"el texto JSON de la medida no se entiende: {e}.") from e
    except ErrorSintaxis as e:
        raise ErrorHerramienta(
            "MEDIDA_INVALIDA",
            f"el texto Oracle de la medida no se entiende: {fragmento_de_error(e, texto)}.",
        ) from e
    except (MedidaMalDeclarada, VersionInvalida) as e:
        raise ErrorHerramienta("MEDIDA_INVALIDA", f"la medida no carga: {e}.") from e


def _alcance_derivado_estricto(medida: Medida, declaradas: dict) -> list[str]:
    """Cruza campos sólo después de que el cargador estricto validó todas las declaraciones."""
    alias_de = relaciones_por_alias(medida.a_datos())
    leidos: set[tuple[str, str]] = set()

    def visitar(nodo) -> None:
        if not isinstance(nodo, list) or not nodo:
            return
        if nodo[0] == "campo" and len(nodo) == 3:
            leidos.add((alias_de.get(nodo[1], ""), nodo[2]))
        for hijo in nodo[1:]:
            visitar(hijo)

    visitar(medida.a_datos())
    lineas = []
    for _alias, relacion in sorted(alias_de.items()):
        declarada = declaradas.get(relacion)
        if declarada is None:
            lineas.append(f"    de `{relacion}` no se sabe: nadie declaró sus campos")
            continue
        nombres = {campo.nombre for campo in declarada.campos}
        sin_leer = [campo.nombre for campo in declarada.campos
                    if (relacion, campo.nombre) not in leidos]
        sin_declarar = sorted(campo for rel, campo in leidos
                              if rel == relacion and campo not in nombres)
        if sin_declarar:
            lineas.append(
                f"    ⚠ de `{relacion}` LEE campos que la relación no declara: "
                f"{', '.join(sin_declarar)}")
        if sin_leer:
            lineas.append(f"    de `{relacion}` NO lee: {', '.join(sin_leer)}")
        elif not sin_declarar:
            lineas.append(f"    de `{relacion}` lee todos los campos declarados")
    return lineas


def _entrada_sha256(medida: Medida, evidencia: dict) -> str:
    """Firma la expansión canónica y los datos, de modo que un id mutable nunca sea la entrada."""
    normalizada = {"medida": medida.a_datos(), "evidencia": evidencia}
    return hashlib.sha256(_json_compacto(normalizada).encode("utf-8")).hexdigest()


def _presentar_evaluacion(proy: Proyecto, medida: Medida, veredicto: dict,
                          evidencia: dict, declaradas: dict) -> dict:
    """Proyecta un Veredicto ya decidido; aquí no hay una segunda comparación con el umbral."""
    if veredicto["sin_evidencia"]:
        estado = "sin_evidencia"
    elif veredicto["ok"]:
        estado = "verde"
    else:
        estado = "rojo"

    advertencias = []
    if not declaradas:
        advertencias.append(
            "El proyecto no declara relaciones; alcance_derivado está vacío y no afirma que "
            "la medida mire todos los campos.")
    for relacion in relaciones_de_medida(medida):
        if relacion not in medida.requiere and not evidencia.get(relacion):
            advertencias.append(
                f"La medida consume «{relacion}», pero no la declara en requiere y esa relación "
                "vino vacía; se conserva el resultado del álgebra.")

    testigos = veredicto["testigos"][:5]
    return {
        "esquema": "oracle.mcp/evaluacion/v1",
        "oracle_version": VERSION_DISTRIBUCION,
        "proyecto": str(proy.raiz.resolve()),
        "entrada_sha256": _entrada_sha256(medida, evidencia),
        "medida": veredicto["id"],
        "estado": estado,
        "valor": veredicto["valor"],
        "umbral": {
            "operador": medida.op,
            "valor": medida.limite,
            "segun": medida.segun,
            "porque": veredicto["porque"],
        },
        "testigos": testigos,
        "testigos_omitidos": len(veredicto["testigos"]) - len(testigos),
        "alcance": veredicto["alcance"],
        "alcance_derivado": (
            _alcance_derivado_estricto(medida, declaradas) if declaradas else []),
        "advertencias": advertencias,
    }


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
        # `partition` y no `split(..., 1)`: con `maxsplit` el arnés genera un mutante `1 → 2` que
        # NINGÚN test puede distinguir —el primer segmento es el mismo para cualquier maxsplit
        # positivo, y acá se toma `[0]`—. Declararlo equivalente sería anotar un sitio que se puede
        # borrar; `partition` no lleva la constante, así que el mutante deja de existir. El `[0]` sí
        # queda medido: con un mensaje sin el separador, `[1]` devuelve vacío y el test lo nota.
        archivo = str(e).partition(" es código Python externo")[0]
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


def _rutas_de_evaluacion(proy: Proyecto, catalogo) -> list[Path]:
    """Enumera los bytes locales leídos por evaluar, sin sumar corpus que esta operación no usa."""
    entradas = set()
    if catalogo is not None:
        entradas.update(entrada.ruta.resolve() for entrada in catalogo.entradas.values())
    for nombre in ("oracle.json", "escalares.py"):
        ruta = proy.raiz / nombre
        if ruta.exists() or ruta.is_symlink():
            entradas.add(ruta.resolve())
    for nombre in ("macros", "relaciones"):
        entradas.update(
            ruta.resolve() for ruta in _rutas_de_directorio(proy.raiz / nombre))
    return sorted(entradas)


def _huella_evaluacion(proy: Proyecto, catalogo) -> str:
    """Firma rutas y bytes: una reescritura equivalente sigue siendo un cambio durante la llamada."""
    huella = hashlib.sha256()
    for ruta in _rutas_de_evaluacion(proy, catalogo):
        try:
            contenido = ruta.read_bytes()
        except OSError as e:
            raise OSError(f"no se pudo leer {ruta}: {e}") from e
        huella.update(str(ruta).encode("utf-8") + b"\0" + contenido + b"\0")
    return huella.hexdigest()


def _huella_final_evaluacion(proy: Proyecto, refrescar) -> str:
    """Hace comparable una rotura final con el estado válido que abrió la evaluación."""
    try:
        catalogo = refrescar()
        return _huella_evaluacion(proy, catalogo)
    except Exception as e:
        marca = {"error": type(e).__name__, "mensaje": str(e)}
        return hashlib.sha256(_json_compacto(marca).encode("utf-8")).hexdigest()


@contextmanager
def _evaluacion_estable(proy: Proyecto, catalogo, refrescar):
    """Rechaza el objeto entero si alguno de los bytes consultados cambió mientras se armaba."""
    inicial = _huella_evaluacion(proy, catalogo)
    try:
        yield
    except Exception:
        final = _huella_final_evaluacion(proy, refrescar)
        if inicial != final:
            raise ErrorHerramienta(
                "PROYECTO_CAMBIO_DURANTE_LA_CONSULTA",
                f"huella inicial {inicial} y final {final}; reintentá sobre un estado estable.",
            )
        raise
    final = _huella_final_evaluacion(proy, refrescar)
    if inicial != final:
        raise ErrorHerramienta(
            "PROYECTO_CAMBIO_DURANTE_LA_CONSULTA",
            f"huella inicial {inicial} y final {final}; reintentá sobre un estado estable.",
        )



def _casos_del_desafio(argumentos, mid: str, corpus) -> list[dict]:
    """Los casos que van a desafiar la medida, con su origen conservado.

    Un caso de la llamada es EFÍMERO y sólo puede declarar qué veredicto espera. No acepta
    `procedencia`: una llamada no puede convertir evidencia fabricada en evidencia observada, y
    permitirlo volvería esta herramienta una manera de blanquear un corpus.

    Un id repetido entre el corpus y la llamada se rechaza en vez de dejar ganar al último. Ganar
    en silencio es cómo una evidencia escrita para pasar reemplaza a la que estaba midiendo.
    """
    del_proyecto = argumentos.get("usar_evidencia_del_proyecto", True)
    if not isinstance(del_proyecto, bool):
        raise ErrorHerramienta(
            "ARGUMENTOS_INVALIDOS", "`usar_evidencia_del_proyecto` es booleano.")
    casos = []
    if del_proyecto:
        for caso in corpus:
            if caso.get("medida") != mid:
                continue
            casos.append({
                "id": caso.get("id", ""),
                "espera": "verde" if caso.get("etiqueta") == "verde_correcto" else "rojo",
                "evidencia": caso.get("evidencia", {}),
                "origen": "corpus",
            })
    del_corpus = {caso["id"] for caso in casos}
    vistos = set(del_corpus)
    for caso in argumentos.get("casos", []):
        if caso["id"] in vistos:
            # El mensaje dice DÓNDE está el otro. Decir siempre «ya existe en el corpus» manda a
            # buscar al lugar equivocado cuando el duplicado estaba dentro de la misma llamada.
            donde = ("ya existe en el corpus del proyecto" if caso["id"] in del_corpus
                     else "aparece dos veces en esta llamada")
            raise ErrorHerramienta(
                "CASO_REPETIDO",
                f"«{caso['id']}» {donde}; renombralo. No se eligió uno de los dos.")
        vistos.add(caso["id"])
        casos.append({**caso, "origen": "efimero"})
    return casos


def _desafiar(medida: Medida, casos: list[dict]) -> dict:
    """El lazo: reproducir, exigir las dos polaridades, mutar. En ese orden y sin seguir si falla.

    `nucleo.mutacion.correr` saltea en silencio un caso que no está en su estado esperado —«no fija
    nada»— y para una ronda del arnés eso alcanza. Acá no: si el original no reproduce lo que el
    caso espera, mutar mide otra cosa y el número saldría igual de convincente. Se corta y se dice
    cuál no reprodujo.

    `obtenido` distingue `sin_evidencia` de `rojo` por el mismo motivo que la evaluación: rojo
    afirma algo del mundo, sin evidencia afirma que no se pudo mirar. Colapsarlos acá le diría a un
    agente que su medida falló cuando lo que faltó fue la relación.
    """
    from nucleo.mutacion import mutantes

    def observar(m, evidencia):
        try:
            v = m.evaluar(evidencia).a_dict()
        except Exception as e:
            return "error", f"{type(e).__name__}: {e}"
        if v["sin_evidencia"]:
            return "sin_evidencia", None
        return ("verde" if v["ok"] else "rojo"), None

    discordancias = []
    for caso in casos:
        obtenido, _detalle = observar(medida, caso["evidencia"])
        if obtenido != caso["espera"]:
            discordancias.append({"caso": caso["id"], "esperado": caso["espera"],
                                  "obtenido": obtenido})
    if discordancias:
        return {"conclusion": "original_no_reproduce", "discordancias": discordancias,
                "casos": len(casos), "mutacion": None}

    polaridades = {caso["espera"] for caso in casos}
    if polaridades != {"verde", "rojo"}:
        return {"conclusion": "faltan_polaridades", "discordancias": [],
                "casos": len(casos), "mutacion": None}

    generados = mutantes(medida.a_datos())
    if not generados:
        # No es lo mismo que «todos detectados»: un denominador vacío no prueba nada, y llamarlo
        # verde sería el `019-ronda-sin-mutantes-declarada-verde` del corpus, un nivel más arriba.
        return {"conclusion": "sin_mutantes", "discordancias": [], "casos": len(casos),
                "mutacion": {"generados": 0, "detectados_por_conducta": 0,
                             "rechazados_por_el_algebra": 0, "no_detectados": []}}

    conducta = algebra = 0
    no_detectados = []
    for nombre, datos in generados:
        try:
            mutante = Medida.de_datos(datos)
        except Exception:
            algebra += 1
            continue
        detectado = rechazado = False
        for caso in casos:
            obtenido, _d = observar(mutante, caso["evidencia"])
            if obtenido == "error":
                rechazado = True
                continue
            if obtenido != caso["espera"]:
                detectado = True
                break
        if detectado:
            conducta += 1
        elif rechazado:
            algebra += 1
        else:
            no_detectados.append({"mutador": nombre})

    # La conclusión más fuerte NO se llama «correcta», «aprobada» ni «lista_para_guardar».
    # Significa exactamente: estos mutadores, escritos por estos autores, fueron discriminados por
    # estas evidencias. Un nombre más ambicioso convertiría un cálculo correcto en una conclusión
    # falsa al cruzar el transporte.
    if no_detectados:
        conclusion = "sobrevivientes"
    elif algebra:
        conclusion = "sin_sobrevivientes_con_rechazos"
    else:
        conclusion = "todos_detectados_por_conducta"
    return {
        "conclusion": conclusion,
        "discordancias": [],
        "casos": len(casos),
        "mutacion": {"generados": len(generados), "detectados_por_conducta": conducta,
                     "rechazados_por_el_algebra": algebra, "no_detectados": no_detectados},
    }


def desafiar_para_mcp(proy: Proyecto, argumentos, *, confiar_escalares: bool = False) -> dict:
    """El lazo candidato → dos polaridades → mutación, entero en memoria y sin tocar el disco."""
    if not isinstance(argumentos, dict) or "medida" not in argumentos:
        raise ErrorHerramienta("ARGUMENTOS_INVALIDOS", "`medida` es obligatoria.")
    especificacion = argumentos["medida"]
    if not isinstance(especificacion, dict):
        raise ErrorHerramienta("ARGUMENTOS_INVALIDOS", "`medida` es un objeto.")
    for caso in argumentos.get("casos", []):
        if not isinstance(caso, dict) or {"id", "espera", "evidencia"} - set(caso):
            raise ErrorHerramienta(
                "ARGUMENTOS_INVALIDOS", "cada caso lleva `id`, `espera` y `evidencia`.")
        if "procedencia" in caso:
            raise ErrorHerramienta(
                "PROCEDENCIA_NO_ADMITIDA",
                "un caso de la llamada no declara procedencia: una llamada no puede convertir "
                "evidencia fabricada en evidencia observada.")
        if caso["espera"] not in ("verde", "rojo"):
            raise ErrorHerramienta("ARGUMENTOS_INVALIDOS", "`espera` es «verde» o «rojo».")
    try:
        with escalares_del_proyecto(proy, confiar=confiar_escalares):
            macros = macros_del_proyecto(proy)
            catalogo = None
            if "id" in especificacion:
                try:
                    catalogo = catalogo_efectivo(proy, macros=macros)
                except ProyectoInvalido:
                    raise
                except Exception as e:
                    raise _error_catalogo(proy, e) from e
                mid = especificacion["id"]
                if mid not in catalogo:
                    raise _error_id_ausente(mid, proy, catalogo)
                medida = catalogo[mid]
            else:
                medida = _medida_en_memoria(especificacion, macros)
            corpus = []
            if argumentos.get("usar_evidencia_del_proyecto", True):
                from nucleo.caso import cargar_casos
                try:
                    corpus = cargar_casos(proy.corpus)
                except Exception as e:
                    # Fallo cerrado: un corpus ilegible NO se degrada a «no había casos». Un
                    # desafío sobre cero casos del proyecto daría «faltan_polaridades», que es una
                    # afirmación sobre la medida y no sobre el disco.
                    raise ErrorHerramienta(
                        "CORPUS_INVALIDO",
                        f"no se pudo leer el corpus: {e}. No se desafió con menos casos.") from e
            casos = _casos_del_desafio(argumentos, medida.id, corpus)
            advertencias = []
            if not any(caso["origen"] == "corpus" for caso in casos):
                advertencias.append(
                    "ningún caso salió del corpus del proyecto: lo que se desafió son evidencias "
                    "de esta llamada, y una evidencia escrita para la medida puede repetir su "
                    "error")
            resultado = _desafiar(medida, casos)
    except ErrorHerramienta:
        raise
    except EscalaresNoConfiables as e:
        archivo = str(e).partition(" es código Python externo")[0]
        raise ErrorHerramienta(
            "ESCALARES_NO_AUTORIZADAS",
            f"{archivo} es código externo; autorizalo en la configuración de arranque del "
            "servidor, no en esta llamada.") from e
    except EscalaresInvalidas as e:
        raise _error_catalogo(proy, e) from e
    except ProyectoInvalido as e:
        raise ErrorHerramienta("PROYECTO_INVALIDO", f"{proy.raiz.resolve()}: {e}.") from e
    return {
        "esquema": "oracle.mcp/desafio/v1",
        "oracle_version": VERSION_DISTRIBUCION,
        "proyecto": str(proy.raiz.resolve()),
        "entrada_sha256": hashlib.sha256(
            json.dumps(argumentos, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest(),
        "medida": medida.id,
        "advertencias": advertencias,
        **resultado,
    }

def evaluar_para_mcp(proy: Proyecto, argumentos, *, confiar_escalares: bool = False) -> dict:
    """Evalúa por valor y falla cerrado; no traduce una carga rota a verde ni a lista vacía."""
    especificacion, evidencia = _validar_evaluacion(argumentos)
    try:
        with escalares_del_proyecto(proy, confiar=confiar_escalares):
            macros = macros_del_proyecto(proy)
            catalogo = None
            if "id" in especificacion:
                try:
                    catalogo = catalogo_efectivo(proy, macros=macros)
                except ProyectoInvalido:
                    raise
                except Exception as e:
                    raise _error_catalogo(proy, e) from e
            try:
                declaradas = relaciones_del_proyecto(proy)
            except ProyectoInvalido:
                raise
            except Exception as e:
                raise ErrorHerramienta(
                    "RELACIONES_INVALIDAS",
                    f"no se pudo derivar el alcance: {e}. No se devolvió un alcance vacío.",
                ) from e

            def refrescar():
                macros_actuales = macros_del_proyecto(proy)
                relaciones_del_proyecto(proy)
                if catalogo is None:
                    return None
                return catalogo_efectivo(proy, macros=macros_actuales)

            with _evaluacion_estable(proy, catalogo, refrescar):
                if catalogo is None:
                    medida = _medida_en_memoria(especificacion, macros)
                else:
                    mid = especificacion["id"]
                    if mid not in catalogo:
                        raise _error_id_ausente(mid, proy, catalogo)
                    medida = catalogo[mid]
                try:
                    veredicto = medida.evaluar(evidencia).a_dict()
                except Exception as e:
                    raise ErrorHerramienta(
                        "EVALUACION_FALLIDA",
                        f"«{medida.id}» no se pudo evaluar: {type(e).__name__}: {e}.",
                    ) from e
                contenido = _presentar_evaluacion(
                    proy, medida, veredicto, evidencia, declaradas)
    except ErrorHerramienta:
        raise
    except EscalaresNoConfiables as e:
        archivo = str(e).partition(" es código Python externo")[0]
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
        raise ErrorHerramienta(
            "EVALUACION_FALLIDA",
            f"la evaluación falló cerrada: {type(e).__name__}: {e}.",
        ) from e
    return contenido


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

    def _resultado_herramienta(self, mensaje: dict, nombre: str, argumentos) -> None:
        try:
            if nombre == HERRAMIENTA_CATALOGO["name"]:
                contenido = catalogo_para_mcp(
                    self.proy, argumentos, confiar_escalares=self.confiar_escalares)
            elif nombre == HERRAMIENTA_DESAFIAR["name"]:
                contenido = desafiar_para_mcp(
                    self.proy, argumentos, confiar_escalares=self.confiar_escalares)
            else:
                contenido = evaluar_para_mcp(
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
            elif params["name"] not in {herramienta["name"] for herramienta in HERRAMIENTAS}:
                self._error(
                    mensaje, -32602,
                    f"tools/call inválido: herramienta desconocida: {params['name']}",
                )
            else:
                self._resultado_herramienta(
                    mensaje, params["name"], params.get("arguments", {}))
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
