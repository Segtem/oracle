# Fixtures de aceptación del servidor MCP de Oracle: conversaciones JSON-RPC para `oracle_catalogo_efectivo`, `oracle_evaluar` y `oracle_desafiar`

**Fecha:** 2026-09-05  
**Estado:** fixtures de aceptación ejecutables y verificados contra el servidor implementado en `tools/mcp.py`  
**Autoridad normativa:** [`estudios/MCP-CONTRATO.md`](MCP-CONTRATO.md), [`PLAN-0.6.0-MCP.md`](../PLAN-0.6.0-MCP.md) y [`estudios/MCP-FALLAS.md`](MCP-FALLAS.md)

---

## 1. Naturaleza y propósito de estos fixtures

Este documento constituye la **especificación ejecutable** de las tres herramientas normativas del servidor MCP de Oracle (`oracle_catalogo_efectivo`, `oracle_evaluar` y `oracle_desafiar`), consolidada y comprobada contra el servidor en ejecución `tools/mcp.py`.

El objetivo es eliminar toda ambigüedad en el cable. Cada fixture documenta los bytes exactos transmitidos por stdin, la respuesta devuelta por stdout y la justificación técnica, semántica y epistémica que fundamenta por qué esa respuesta es la única admisible.

### Principios rectores del transporte y la semántica

1. **Transporte stdio sin estado acumulativo (MCP 2026-07-28 y MCP 2025-11-25):**  
   Cada mensaje JSON-RPC viaja en UTF-8 en una única línea delimitada estrictamente por `\n`, sin cabeceras HTTP ni `Content-Length` (a diferencia de LSP). La salida estándar (`stdout`) está consagrada exclusivamente al tráfico JSON-RPC; cualquier traza, depuración o log humano debe dirigirse a `stderr`.
2. **Sólo lectura con raíz física inmutable:**  
   El proceso se inicia fijando la autoridad del servidor: `oracle-mcp --proyecto <ruta>`. Ninguna herramienta acepta rutas ni URIs por llamada, impidiendo que una inyección en datos medidos desplace la autoridad a otro directorio.
3. **Fallo cerrado y respuestas falsables:**  
   Como demostró el estudio de fallas [`estudios/MCP-FALLAS.md`](MCP-FALLAS.md), un agente de IA no tiene herramientas cognitivas para sospechar de una respuesta estructurada que no emite error. Si un catálogo no puede leerse, el servidor **debe emitir un error explícito (`isError: true`)** y **jamás** una lista vacía o un `total: 0`.
4. **Distinción dual en el cable:**  
   En respuestas exitosas, `structuredContent` contiene el objeto tipado según `outputSchema`, mientras que `content` transporta un bloque de texto con su serialización JSON compacta para clientes que no procesan contenido estructurado nativo. En respuestas de error (`isError: true`), **no se emite `structuredContent`**, para no simular conformidad con el esquema de éxito, y `content[0].text` comienza de forma obligatoria con la plantilla `CODIGO — mensaje`.

---

## 2. Conversación 1: El Handshake del Servidor (`initialize`, `tools/list`, `tools/call`)

Esta conversación documenta el ciclo de arranque bajo la era MCP con sesión (2025-11-25) y su correspondencia con la era moderna (2026-07-28).

### 2.1. Inicialización (`initialize`)

#### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"agente-test","version":"1.0.0"}}}
```

*(En el cable: una única línea UTF-8 terminada en `\n`, 147 bytes).*

#### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-11-25","capabilities":{"tools":{}},"serverInfo":{"name":"oracle-mcp","version":"0.5.0"}}}
```

*(En el cable: una única línea UTF-8 terminada en `\n`, 135 bytes).*

#### Notificación obligatoria del cliente (`notifications/initialized`):

```json
{"jsonrpc":"2.0","method":"notifications/initialized"}
```

*(El servidor procesa la notificación y no emite respuesta JSON-RPC por ser una notificación).*

#### POR QUÉ esa respuesta y no otra:

- **Identidad del servidor (`serverInfo`):** Se identifica unívocamente como `"name": "oracle-mcp"`. La versión reportada es `"0.5.0"` (el valor exacto de `nucleo.version.VERSION_DISTRIBUCION`), permitiendo al anfitrión auditar la correspondencia entre el ejecutable invocado y el árbol de código del cliente.
- **Capacidades anunciadas (`capabilities`):** Anuncia **únicamente** `{"tools": {}}`.
  - **No anuncia `resources`:** Oracle no expone archivos directos ni abstrae el sistema de archivos; los archivos ya son leídos por el editor del anfitrión.
  - **No anuncia `prompts`:** Oracle no es una biblioteca de plantillas para modelos.
  - **No anuncia `sampling`:** El servidor no requiere solicitarle al anfitrión que complete prompts con LLMs adicionales.
  - **No anuncia `roots`:** La raíz física quedó sellada al momento del arranque con `--proyecto`.
  - **No anuncia `listChanged: true` en `tools`:** La superficie de herramientas de Oracle es fija y normativa. No aparecen ni desaparecen herramientas dinámicamente según el estado del proyecto. Esto habilita el almacenamiento en caché de prompts por parte del cliente LLM, abaratando drásticamente el consumo de tokens en cada llamada.

---

### 2.2. Listado de herramientas (`tools/list`)

#### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

#### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "oracle_catalogo_efectivo",
        "title": "Catálogo efectivo de Oracle",
        "description": "Consulta las medidas que obligan al proyecto fijado al arrancar el servidor. Sin ids devuelve un índice compacto; con ids devuelve el detalle de esas medidas. Usa catalogo_efectivo: no confunde todo lo instalado con lo que tiene jurisdicción aquí. No evalúa evidencia ni escribe archivos.",
        "annotations": {
          "readOnlyHint": true,
          "destructiveHint": false,
          "idempotentHint": true,
          "openWorldHint": false
        },
        "inputSchema": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "ids": {
              "type": "array",
              "minItems": 1,
              "uniqueItems": true,
              "items": {
                "type": "string",
                "pattern": "^[a-z][a-z0-9_]*(?:\\.[a-z][a-z0-9_]*)+$"
              },
              "description": "Ids efectivos cuyo detalle se pide. Omitir para listar todos."
            }
          }
        },
        "outputSchema": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "esquema",
            "oracle_version",
            "proyecto",
            "huella_proyecto",
            "detalle",
            "total",
            "medidas"
          ],
          "properties": {
            "esquema": {
              "const": "oracle.mcp/catalogo-efectivo/v1"
            },
            "oracle_version": {
              "type": "string"
            },
            "proyecto": {
              "type": "string"
            },
            "huella_proyecto": {
              "type": "string",
              "pattern": "^[0-9a-f]{64}$"
            },
            "detalle": {
              "type": "boolean"
            },
            "total": {
              "type": "integer",
              "minimum": 0
            },
            "medidas": {
              "type": "array",
              "items": {
                "type": "object",
                "additionalProperties": false,
                "required": [
                  "id",
                  "origen",
                  "fijacion"
                ],
                "properties": {
                  "id": {
                    "type": "string"
                  },
                  "origen": {
                    "type": "string"
                  },
                  "relaciones": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    },
                    "uniqueItems": true
                  },
                  "fijacion": {
                    "enum": [
                      "evidencia",
                      "arnes",
                      "heredada",
                      "sin_fijar"
                    ]
                  },
                  "ambito": {
                    "enum": [
                      "universal",
                      "del_origen",
                      "sin_declarar"
                    ]
                  },
                  "requiere": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    },
                    "uniqueItems": true
                  },
                  "umbral": {
                    "type": "object",
                    "additionalProperties": false,
                    "required": [
                      "operador",
                      "valor",
                      "segun",
                      "porque"
                    ],
                    "properties": {
                      "operador": {
                        "type": "string"
                      },
                      "valor": {
                        "type": [
                          "string",
                          "number",
                          "boolean"
                        ]
                      },
                      "segun": {
                        "type": "string"
                      },
                      "porque": {
                        "type": "string"
                      }
                    }
                  },
                  "alcance": {
                    "type": "string"
                  },
                  "fuente": {
                    "type": "string"
                  },
                  "fuente_sha256": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{64}$"
                  }
                }
              }
            }
          }
        }
      },
      {
        "name": "oracle_evaluar",
        "title": "Evaluar una medida en memoria",
        "description": "Evalúa una medida efectiva por id o un texto de medida sin guardarlo contra una evidencia JSON. Devuelve verde, rojo o sin_evidencia como estados distintos, además del valor, umbral, testigos y alcance. Use esta herramienta para entender conducta puntual; no prueba que la medida sea correcta.",
        "annotations": {
          "readOnlyHint": true,
          "destructiveHint": false,
          "idempotentHint": true,
          "openWorldHint": false
        },
        "inputSchema": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "medida",
            "evidencia"
          ],
          "properties": {
            "medida": {
              "oneOf": [
                {
                  "type": "object",
                  "additionalProperties": false,
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
                  "additionalProperties": false,
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
            "evidencia": {
              "$ref": "#/$defs/evidencia"
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
          "additionalProperties": false,
          "required": [
            "esquema",
            "oracle_version",
            "proyecto",
            "entrada_sha256",
            "medida",
            "estado",
            "valor",
            "umbral",
            "testigos",
            "testigos_omitidos",
            "alcance",
            "alcance_derivado",
            "advertencias"
          ],
          "properties": {
            "esquema": {
              "const": "oracle.mcp/evaluacion/v1"
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
            "estado": {
              "enum": [
                "verde",
                "rojo",
                "sin_evidencia"
              ]
            },
            "valor": {
              "type": "number"
            },
            "umbral": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "operador",
                "valor",
                "segun",
                "porque"
              ],
              "properties": {
                "operador": {
                  "type": "string"
                },
                "valor": {
                  "type": [
                    "string",
                    "number",
                    "boolean"
                  ]
                },
                "segun": {
                  "type": "string"
                },
                "porque": {
                  "type": "string"
                }
              }
            },
            "testigos": {
              "type": "array",
              "items": {
                "type": "object"
              },
              "maxItems": 5
            },
            "testigos_omitidos": {
              "type": "integer",
              "minimum": 0
            },
            "alcance": {
              "type": "string"
            },
            "alcance_derivado": {
              "type": "array",
              "items": {
                "type": "string"
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
      },
      {
        "name": "oracle_desafiar",
        "title": "Desafiar una medida con corpus y mutación",
        "description": "Falsa en memoria una medida por id o texto. Combina, si se pide, sus casos del corpus y diferenciales del proyecto con casos efímeros, exige ambas polaridades y ejecuta mutación de medidas. Informa discordancias, mutantes sobrevivientes y rechazos del álgebra; nunca declara que la medida sea semánticamente correcta ni escribe evidencia.",
        "annotations": {
          "readOnlyHint": true,
          "destructiveHint": false,
          "idempotentHint": true,
          "openWorldHint": false
        },
        "inputSchema": {
          "type": "object",
          "additionalProperties": false,
          "required": [
            "medida"
          ],
          "properties": {
            "medida": {
              "oneOf": [
                {
                  "type": "object",
                  "additionalProperties": false,
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
                  "additionalProperties": false,
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
              "default": true,
              "description": "Incluye corpus y diferenciales que nombran el id de la medida."
            },
            "casos": {
              "type": "array",
              "default": [],
              "items": {
                "type": "object",
                "additionalProperties": false,
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
          "additionalProperties": false,
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
              "additionalProperties": false,
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
                "additionalProperties": false,
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
              "additionalProperties": false,
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
                    "additionalProperties": false,
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
    ]
  }
}
```

*(En clientes de la era MCP 2026-07-28, el objeto `result` incluye `"resultType": "complete"`).*

#### POR QUÉ esa respuesta y no otra:

- **Tres herramientas y no veintidós:** No duplica los verbos de consola (`oracle medida nueva`, `oracle caso nuevo`, etc.). Las tres herramientas cubren las tres preguntas esenciales que un agente necesita responder:
  1. *¿Qué me obliga y por qué?* (`oracle_catalogo_efectivo`)
  2. *¿Qué hace esta medida con esta evidencia?* (`oracle_evaluar`)
  3. *¿Qué parte del candidato no está fijada?* (`oracle_desafiar`)
- **Anotaciones estrictas:** Todas declaran `readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true` y `openWorldHint: false`. Son operaciones cerradas al mundo fijado, deterministas y sin efectos secundarios en el sistema de archivos.
- **Esquemas sellados (`additionalProperties: false`):** Todo error en el nombre de un campo de argumentos es detectado y rechazado de inmediato por el validador estricto, impidiendo que argumentos mal escritos sean ignorados silenciosamente.

---

## 3. Conversación 2: El Catálogo Efectivo Sin `ids` (Índice Compacto)

**Contexto de ejecución:**  
El servidor corre fijado sobre el repositorio propio de Oracle:  
`oracle-mcp --proyecto /home/workstation/Dev/oracle`

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"oracle_catalogo_efectivo","arguments":{}}}
```

*(En el cable: una sola línea UTF-8 terminada en `\n`, 92 bytes).*

### Qué tiene que volver por stdout (Servidor → Cliente):

El resultado debe contener `structuredContent` y `content` sincronizados con los datos medidos del proyecto vivo:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"detalle\":false,\"esquema\":\"oracle.mcp/catalogo-efectivo/v1\",\"huella_proyecto\":\"fd300ddbef099a9c10e1e0a17c3a41624625894c6f327420c4197586a8d7f388\",\"medidas\":[{\"fijacion\":\"evidencia\",\"id\":\"meta.agrupar_no_agranda_la_relacion\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.agrupar_sin_claves_es_el_resumen_global\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.donde_compone\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.donde_nunca_agrega_filas\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"arnes\",\"id\":\"meta.el_caso_reclama_una_medida_que_existe\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"arnes\",\"id\":\"meta.el_caso_se_pone_como_debe\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.el_diagnostico_no_publica_el_dominio\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"arnes\",\"id\":\"meta.el_hueco_declarado_explica_por_que\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"arnes\",\"id\":\"meta.el_nivel_no_se_confunde_con_el_dominio\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.la_medida_no_se_fija_solo_con_evidencia_fabricada\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.los_logicos_evaluan_todos_sus_operandos\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ningun_campo_sin_unidad_declarada\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ningun_flotante_comparado_por_igualdad_en_un_filtro\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ningun_umbral_de_igualdad\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ningun_umbral_flotante_de_igualdad\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ninguna_evidencia_declara_un_referente_sin_huella\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ninguna_evidencia_se_juzga_con_referente_vencido\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ninguna_exclusion_de_mutador_se_aplica_globalmente\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ninguna_medida_sin_alcance\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ninguna_sombra_envejece_sin_revisarse\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ninguna_sombra_sobre_una_medida_que_no_existe\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.ninguna_sombra_ya_en_verde\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.sintaxis_casos_cubre_casos\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.sintaxis_casos_ida_y_vuelta\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.sintaxis_cubre_algebra\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.sintaxis_ida_y_vuelta\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.toda_cantidad_comparada_tiene_unidad_derivable\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.toda_medida_de_ausencia_declara_requiere\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.toda_medida_declara_su_ambito\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"arnes\",\"id\":\"meta.toda_medida_esta_ejercitada\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"arnes\",\"id\":\"meta.toda_medida_esta_fijada\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.toda_medida_filtra_o_agrupa\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.toda_opcion_del_vocabulario_declara_su_sentido\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.toda_relacion_del_lenguaje_esta_en_la_referencia\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.toda_sombra_declara_desde_y_porque\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.toda_sombra_declara_una_fecha_real\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.todo_tanteo_explica_por_que\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.todo_umbral_declara_de_donde_sale\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.todo_verbo_del_cli_esta_en_la_ayuda\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.todo_vocabulario_cerrado_esta_en_el_manual\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.una_macro_equivale_a_su_expansion\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.unir_conmuta\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"meta.unir_materializa_el_producto\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"proceso.afirmacion_declara_alcance\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"heredada\",\"id\":\"proceso.arnes_con_bytecode_frio\",\"origen\":\"perfil:python\"},{\"fijacion\":\"evidencia\",\"id\":\"proceso.codigo_con_mutante_que_lo_mata\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"heredada\",\"id\":\"proceso.modulo_alcanzable\",\"origen\":\"perfil:python\"},{\"fijacion\":\"heredada\",\"id\":\"proceso.modulo_con_consumidor\",\"origen\":\"perfil:python\"},{\"fijacion\":\"evidencia\",\"id\":\"proceso.ronda_mutacion_concluyente\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"proceso.sintaxis_valida_tras_edicion_masiva\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"proceso.test_con_mutante_que_lo_mata\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"proceso.verificacion_vigente\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"proceso.verificador_sin_falsos_rojos\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"simulacion.corrida_reproducible\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"simulacion.la_traza_no_tiene_huecos\",\"origen\":\"catalogo_base:oracle\"},{\"fijacion\":\"evidencia\",\"id\":\"simulacion.no_se_agoto_el_presupuesto\",\"origen\":\"catalogo_base:oracle\"}],\"oracle_version\":\"0.5.0\",\"proyecto\":\"/home/workstation/Dev/oracle\",\"total\":57}"
      }
    ],
    "structuredContent": {
      "esquema": "oracle.mcp/catalogo-efectivo/v1",
      "oracle_version": "0.5.0",
      "proyecto": "/home/workstation/Dev/oracle",
      "huella_proyecto": "fd300ddbef099a9c10e1e0a17c3a41624625894c6f327420c4197586a8d7f388",
      "detalle": false,
      "total": 57,
      "medidas": [
        {"id": "meta.agrupar_no_agranda_la_relacion", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.agrupar_sin_claves_es_el_resumen_global", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.donde_compone", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.donde_nunca_agrega_filas", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.el_caso_reclama_una_medida_que_existe", "origen": "catalogo_base:oracle", "fijacion": "arnes"},
        {"id": "meta.el_caso_se_pone_como_debe", "origen": "catalogo_base:oracle", "fijacion": "arnes"},
        {"id": "meta.el_diagnostico_no_publica_el_dominio", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.el_hueco_declarado_explica_por_que", "origen": "catalogo_base:oracle", "fijacion": "arnes"},
        {"id": "meta.el_nivel_no_se_confunde_con_el_dominio", "origen": "catalogo_base:oracle", "fijacion": "arnes"},
        {"id": "meta.la_medida_no_se_fija_solo_con_evidencia_fabricada", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.los_logicos_evaluan_todos_sus_operandos", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ningun_campo_sin_unidad_declarada", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ningun_flotante_comparado_por_igualdad_en_un_filtro", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ningun_umbral_de_igualdad", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ningun_umbral_flotante_de_igualdad", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ninguna_evidencia_declara_un_referente_sin_huella", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ninguna_evidencia_se_juzga_con_referente_vencido", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ninguna_exclusion_de_mutador_se_aplica_globalmente", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ninguna_medida_sin_alcance", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ninguna_sombra_envejece_sin_revisarse", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ninguna_sombra_sobre_una_medida_que_no_existe", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.ninguna_sombra_ya_en_verde", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.sintaxis_casos_cubre_casos", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.sintaxis_casos_ida_y_vuelta", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.sintaxis_cubre_algebra", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.sintaxis_ida_y_vuelta", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.toda_cantidad_comparada_tiene_unidad_derivable", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.toda_medida_de_ausencia_declara_requiere", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.toda_medida_declara_su_ambito", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.toda_medida_esta_ejercitada", "origen": "catalogo_base:oracle", "fijacion": "arnes"},
        {"id": "meta.toda_medida_esta_fijada", "origen": "catalogo_base:oracle", "fijacion": "arnes"},
        {"id": "meta.toda_medida_filtra_o_agrupa", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.toda_opcion_del_vocabulario_declara_su_sentido", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.toda_relacion_del_lenguaje_esta_en_la_referencia", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.toda_sombra_declara_desde_y_porque", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.toda_sombra_declara_una_fecha_real", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.todo_tanteo_explica_por_que", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.todo_umbral_declara_de_donde_sale", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.todo_verbo_del_cli_esta_en_la_ayuda", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.todo_vocabulario_cerrado_esta_en_el_manual", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.una_macro_equivale_a_su_expansion", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.unir_conmuta", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "meta.unir_materializa_el_producto", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "proceso.afirmacion_declara_alcance", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "proceso.arnes_con_bytecode_frio", "origen": "perfil:python", "fijacion": "heredada"},
        {"id": "proceso.codigo_con_mutante_que_lo_mata", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "proceso.modulo_alcanzable", "origen": "perfil:python", "fijacion": "heredada"},
        {"id": "proceso.modulo_con_consumidor", "origen": "perfil:python", "fijacion": "heredada"},
        {"id": "proceso.ronda_mutacion_concluyente", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "proceso.sintaxis_valida_tras_edicion_masiva", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "proceso.test_con_mutante_que_lo_mata", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "proceso.verificacion_vigente", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "proceso.verificador_sin_falsos_rojos", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "simulacion.corrida_reproducible", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "simulacion.la_traza_no_tiene_huecos", "origen": "catalogo_base:oracle", "fijacion": "evidencia"},
        {"id": "simulacion.no_se_agoto_el_presupuesto", "origen": "catalogo_base:oracle", "fijacion": "evidencia"}
      ]
    },
    "isError": false
  }
}
```

#### POR QUÉ esa respuesta y no otra:

1. **Fila compacta (`id`, `origen`, `fijacion`):** En este modo, `detalle` es estrictamente `false`. Omitir el umbral completo, el alcance, las relaciones y las fuentes ahorra miles de tokens: la respuesta pesa 1.897 tokens frente a los más de 12.000 que costaría el catálogo entero en detalle.
2. **`total: 57` es el catálogo efectivo ENTERO:** Representa la cardinalidad de la jurisdicción completa que obliga a este proyecto. No es el largo de una página ni una muestra.
3. **Procedencia fiel de `origen`:**
   - `catalogo_base:oracle` para las 54 medidas empaquetadas en `catalogos/`.
   - `perfil:python` para las 3 medidas del perfil Python (`proceso.arnes_con_bytecode_frio`, `proceso.modulo_alcanzable`, `proceso.modulo_con_consumidor`).
4. **`fijacion` proviene del juicio de la medida jueza:** No se calcula contando archivos de corpus en el adaptador. Proviene de `ejercicio_del_catalogo()`, que consulta directamente la meta-medida `meta.toda_medida_esta_ejercitada`:
   - `evidencia` (48 medidas): cuenta con casos de prueba en `corpus/` o en diferenciales del proyecto.
   - `arnes` (6 medidas): evaluada formalmente por el arnés sobre las relaciones del lenguaje (ej. `meta.el_caso_se_pone_como_debe`).
   - `heredada` (3 medidas): las del perfil Python, fijadas por el publicador del perfil y no por este repositorio consumidor.
   - `sin_fijar` (0 en Oracle): no hay medidas desatendidas.
5. **Huella criptográfica de proyecto (`huella_proyecto`):**  
   Calculada sobre el conjunto determinista ordenado de los 247 archivos participantes (fuentes de medidas, macros, corpus, diferenciales y `oracle.json`). Permite que el cliente audite si el servidor leyó el estado exacto del disco.

---

## 4. Conversación 3: El Catálogo Efectivo Con `ids` (Detalle de Medidas)

**Contexto de ejecución:**  
El servidor corre fijado sobre el repositorio propio de Oracle:  
`oracle-mcp --proyecto /home/workstation/Dev/oracle`

### Qué se manda por stdin (Cliente → Servidor):

El cliente solicita el detalle de dos medidas específicas (nótese que las pide desordenadas: primero la de `perfil:python` y luego la de `catalogo_base:oracle`):

```json
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"oracle_catalogo_efectivo","arguments":{"ids":["proceso.modulo_con_consumidor","meta.agrupar_no_agranda_la_relacion"]}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"detalle\":true,\"esquema\":\"oracle.mcp/catalogo-efectivo/v1\",\"huella_proyecto\":\"fd300ddbef099a9c10e1e0a17c3a41624625894c6f327420c4197586a8d7f388\",\"medidas\":[{\"alcance\":\"compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción\",\"ambito\":\"del_origen\",\"fijacion\":\"evidencia\",\"fuente\":\"catalogos/meta/meta.agrupar_no_agranda_la_relacion.oracle\",\"fuente_sha256\":\"0c91fac5ec96d77c79f3733c35c54817b22729345ee94fdef2305ff957d9194f\",\"id\":\"meta.agrupar_no_agranda_la_relacion\",\"origen\":\"catalogo_base:oracle\",\"relaciones\":[\"paso\"],\"requiere\":[],\"umbral\":{\"operador\":\"<=\",\"porque\":\"agrupar colapsa: una fila por grupo, y los grupos no pueden ser más que las filas que los originaron. Si sale agrandando, está inventando grupos que ninguna fila sostiene, y un agregado sobre un grupo inventado es un número sin evidencia detrás\",\"segun\":\"contrato\",\"valor\":0}},{\"alcance\":\"cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama\",\"ambito\":\"universal\",\"fijacion\":\"heredada\",\"fuente\":\"perfiles/python/catalogos/proceso/proceso.modulo_con_consumidor.oracle\",\"fuente_sha256\":\"94a102eb56393fa2674b066fa65854c98ab321bc046686b4120b745e0e05525e\",\"id\":\"proceso.modulo_con_consumidor\",\"origen\":\"perfil:python\",\"relaciones\":[\"modulo\",\"importa\"],\"requiere\":[\"importa\"],\"umbral\":{\"operador\":\"<=\",\"porque\":\"un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite\",\"segun\":\"contrato\",\"valor\":0}}],\"oracle_version\":\"0.5.0\",\"proyecto\":\"/home/workstation/Dev/oracle\",\"total\":57}"
      }
    ],
    "structuredContent": {
      "esquema": "oracle.mcp/catalogo-efectivo/v1",
      "oracle_version": "0.5.0",
      "proyecto": "/home/workstation/Dev/oracle",
      "huella_proyecto": "fd300ddbef099a9c10e1e0a17c3a41624625894c6f327420c4197586a8d7f388",
      "detalle": true,
      "total": 57,
      "medidas": [
        {
          "id": "meta.agrupar_no_agranda_la_relacion",
          "origen": "catalogo_base:oracle",
          "relaciones": [
            "paso"
          ],
          "fijacion": "evidencia",
          "ambito": "del_origen",
          "requiere": [],
          "umbral": {
            "operador": "<=",
            "valor": 0,
            "segun": "contrato",
            "porque": "agrupar colapsa: una fila por grupo, y los grupos no pueden ser más que las filas que los originaron. Si sale agrandando, está inventando grupos que ninguna fila sostiene, y un agregado sobre un grupo inventado es un número sin evidencia detrás"
          },
          "alcance": "compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción",
          "fuente": "catalogos/meta/meta.agrupar_no_agranda_la_relacion.oracle",
          "fuente_sha256": "0c91fac5ec96d77c79f3733c35c54817b22729345ee94fdef2305ff957d9194f"
        },
        {
          "id": "proceso.modulo_con_consumidor",
          "origen": "perfil:python",
          "relaciones": [
            "modulo",
            "importa"
          ],
          "fijacion": "heredada",
          "ambito": "universal",
          "requiere": [
            "importa"
          ],
          "umbral": {
            "operador": "<=",
            "valor": 0,
            "segun": "contrato",
            "porque": "un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite"
          },
          "alcance": "cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama",
          "fuente": "perfiles/python/catalogos/proceso/proceso.modulo_con_consumidor.oracle",
          "fuente_sha256": "94a102eb56393fa2674b066fa65854c98ab321bc046686b4120b745e0e05525e"
        }
      ]
    },
    "isError": false
  }
}
```

#### POR QUÉ esa respuesta y no otra:

1. **`total: 57` permanece inalterado:** Aunque la consulta devuelva sólo 2 medidas en el arreglo `medidas`, `total` sigue siendo 57. Informar `total: 2` sería un error gravísimo: le haría creer al agente que el catálogo entero del proyecto consta de 2 medidas. `total` es el tamaño del catálogo efectivo global; la longitud del arreglo `medidas` es el subconjunto solicitado.
2. **`detalle: true` activa la presencia de todos los campos enriquecidos:**  
   - `relaciones`: el conjunto de relaciones consumidas por la medida (permite al agente saber qué evidencia necesita preparar si desea evaluarla).
   - `ambito`: jurisdicción declarada (`del_origen` vs `universal`).
   - `requiere`: relaciones declaradas como precondición obligatoria. En `proceso.modulo_con_consumidor` es `["importa"]`, lo que significa que si `importa` está vacía la medida sale `sin_evidencia` en lugar de emitir un falso verde por vaciedad.
   - `umbral`: cuádrupla desglosada (`operador`, `valor`, `segun`, `porque`). Falsabilidad total: el agente sabe si el valor se basa en `contrato`, `convencion`, `tanteo` o `hecho`, y conoce la justificación humana de la cota.
   - `alcance`: el punto ciego declarado de la regla.
   - `fuente`: presentada con `presentar_ruta` (relativa a la raíz del proyecto para preservar portabilidad).
   - `fuente_sha256`: huella criptográfica del archivo en disco al momento de la consulta. Permite detectar si el archivo fue modificado concurrentemente.
3. **Ordenamiento determinista:** A pesar de que el cliente pidió `["proceso.modulo_con_consumidor", "meta.agrupar_no_agranda_la_relacion"]`, la respuesta devuelve primero `meta.agrupar_no_agranda_la_relacion`. La respuesta está ordenada canónicamente por `id`.

---

## 5. Conversación 4: Rechazo de Lista de `ids` Vacía (`ids: []`)

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"oracle_catalogo_efectivo","arguments":{"ids":[]}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "ARGUMENTOS_INVALIDOS — $.ids: []; se esperaba arreglo con al menos 1 elemento."
      }
    ],
    "isError": true
  }
}
```

#### POR QUÉ esa respuesta y no otra:

1. **No crea un tercer modo:** El contrato define exactamente dos modos:
   - Modo índice compacto: se omite el argumento `ids`.
   - Modo detalle selectivo: se entrega `ids` con uno o más identificadores.
   Si `ids: []` fuera aceptado devolviendo una lista vacía de medidas, crearía un modo absurdo ("dame el detalle de nada") que no aporta ninguna información útil. Si devolviera el detalle de todas, violaría el principio de costo de contexto.
2. **Violación estricta de esquema (`minItems: 1`):** El esquema normativo de entrada declara explícitamente `"minItems": 1`. Enviar `[]` es una violación contractual.
3. **`isError: true` y ausencia de `structuredContent`:** Los errores de ejecución de herramientas viajan con `isError: true`. No llevan `structuredContent` porque el esquema publicado describe respuestas exitosas (`oracle.mcp/catalogo-efectivo/v1`), y emitir un JSON parcial fingiría un éxito inexistente.
4. **Plantilla exacta:** La primera línea sigue la regla `ARGUMENTOS_INVALIDOS — <ruta JSON>: <valor recibido>; se esperaba <forma>.`

---

## 6. Conversación 5: Los Dos Rechazos que Importan (`MEDIDA_NO_EFECTIVA` vs `MEDIDA_DESCONOCIDA`)

### 6.1. La diferencia conceptual fundamental

Un agente de IA opera con un sesgo ontológico muy peligroso: **si una herramienta le dice «la regla X no existe», el agente deduce que la regla falta en el mundo y asume que su trabajo es programarla.**

Por eso Oracle prohíbe unificar los rechazos en un genérico "no existe" o "404":

- **`MEDIDA_NO_EFECTIVA` — Existe en una fuente seleccionada, pero su ámbito no obliga acá:**  
  La medida fue escrita, está instalada físicamente, compila, y está catalogada en alguna de las fuentes que este proyecto activó (por ejemplo, en el catálogo base de Oracle). Sin embargo, su cláusula `ambito` es `del_origen`, y el repositorio donde corre el servidor es un proyecto consumidor ajeno (como Jam o un microservicio).  
  *Significado para el agente:* **La regla tiene autor, tiene dueño y tiene propósito, pero no tiene jurisdicción sobre vos.** Si fallara, el consumidor no tendría ningún remedio disponible en su propio repositorio para corregirla (el defecto era del autor del catálogo, no del código del consumidor). Responder «no existe» invitaría al agente a programar un duplicado local innecesario.
- **`MEDIDA_DESCONOCIDA` — No aparece en ninguna fuente seleccionada:**  
  El identificador no figura en ninguna de las fuentes cargadas (`catalogo_base`, perfiles activados, bibliotecas instaladas ni catálogo propio).  
  *Significado para el agente:* O bien hubo un error tipográfico en el id, o bien el agente está asumiendo una política de un perfil o biblioteca que no ha sido declarada en `oracle.json`. El mensaje le indica consultar el catálogo efectivo sin `ids` para conocer el universo real de reglas disponibles.

---

### 6.2. Fixture 5.1: `MEDIDA_NO_EFECTIVA`

**Contexto de ejecución:**  
El servidor corre fijado sobre el repositorio de un proyecto consumidor (por ejemplo Jam, o un proyecto de prueba que configuró `"catalogo_base": true` en su `oracle.json`):  
`oracle-mcp --proyecto /home/workstation/Dev/jam`

El agente intenta consultar el detalle de una de las 5 medidas reales que dejaron de obligar a Jam en la versión 0.5.0 ([`NOTAS-DE-RELEASE.md`](../NOTAS-DE-RELEASE.md)): `meta.todo_vocabulario_cerrado_esta_en_el_manual`.

#### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"oracle_catalogo_efectivo","arguments":{"ids":["meta.todo_vocabulario_cerrado_esta_en_el_manual"]}}}
```

#### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "MEDIDA_NO_EFECTIVA — «meta.todo_vocabulario_cerrado_esta_en_el_manual» existe en catalogo_base:oracle, pero su ambito «del_origen» no obliga a «/home/workstation/Dev/jam»."
      }
    ],
    "isError": true
  }
}
```

#### POR QUÉ esa respuesta y no otra:

1. **La medida sí existe en las fuentes:** El cargador de fuentes (`catalogos_a_cargar`) leyó `catalogos/meta/meta.todo_vocabulario_cerrado_esta_en_el_manual.oracle` desde el catálogo base de Oracle (`catalogo_base:oracle`).
2. **Pero el ámbito la excluye:** Su ámbito es `del_origen`. Como el proyecto evaluado es `/home/workstation/Dev/jam` y no el repositorio de Oracle (`proy.es_el_propio_oracle == False`), la función `catalogo_efectivo` descarta la medida: no tiene jurisdicción aquí.
3. **Mensaje estructurado y pedagógico:**
   - Cita el id exacto (`«meta.todo_vocabulario_cerrado_esta_en_el_manual»`).
   - Identifica el origen lógico donde reside (`catalogo_base:oracle`).
   - Enuncia la causa jurídica (`su ambito «del_origen» no obliga`).
   - Nombra la raíz del proyecto consultado (`/home/workstation/Dev/jam`).
   El agente comprende de inmediato que la regla no debe ser duplicada.

---

### 6.3. Fixture 5.2: `MEDIDA_DESCONOCIDA`

**Contexto de ejecución:**  
Cualquier proyecto (por ejemplo `/home/workstation/Dev/oracle` o `/home/workstation/Dev/jam`). El agente consulta un identificador inexistente o inventado.

#### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"oracle_catalogo_efectivo","arguments":{"ids":["meta.regla_inventada_que_no_existe"]}}}
```

#### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "MEDIDA_DESCONOCIDA — «meta.regla_inventada_que_no_existe» no aparece en las fuentes seleccionadas; consultá oracle_catalogo_efectivo sin ids."
      }
    ],
    "isError": true
  }
}
```

#### POR QUÉ esa respuesta y no otra:

1. **Ausencia total en fuentes:** El id no figura en `catalogos_a_cargar`. No es que haya quedado fuera por una regla de jurisdicción (`ambito`): simplemente no existe en ningún catálogo activado.
2. **Instrucción accionable:** El mensaje le indica al agente cómo recuperarse de su error: ejecutar `oracle_catalogo_efectivo` sin `ids` para recibir el listado compacto de las medidas efectivas reales que sí puede consultar.

---

## 7. Conversación 6: El Fallo Cerrado (Catálogo Ilegible)

**Contexto de ejecución:**  
Un proyecto donde algún archivo de catálogo (`catalogos/medida_invalida.oracle`) tiene un error sintáctico (por ejemplo, indentación incorrecta o falta de una palabra clave obligatoria):

```oracle
ninguno proyecto.regla_rota:
  de relacion r
  umbral <= 0 segun contrato porque "falla sintaxis"
```

El servidor fue iniciado apuntando a ese proyecto:  
`oracle-mcp --proyecto /home/workstation/Dev/proyecto_roto`

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"oracle_catalogo_efectivo","arguments":{}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "CATALOGO_INVALIDO — catalogos/medida_invalida.oracle: línea 2, columna 3: se esperaba indentación de 4 espacios; llegó '  d'. No se devolvió un catálogo parcial."
      }
    ],
    "isError": true
  }
}
```

### POR QUÉ este es el fixture más importante de todos:

Este fixture es la **frontera crítica** que impide reintroducir el defecto histórico de `tools/contexto.py`.

Hasta el commit `20a2ded`, `tools/contexto.py` implementaba:

```python
try:
    catalogo = cargar_catalogo(...)
except Exception:
    return []
```

El resultado observado fue devastador: los dos proyectos consumidores conocidos de Oracle (que contaban con 41 y 9 medidas reales en sus catálogos) recibían en consola:

```text
## LAS 0 MEDIDAS QUE YA EXISTEN
  (ninguna todavía)
```

Un agente de IA ante ese texto no tenía con qué dudar: asumía que el proyecto era nuevo y procedía a reescribir desde cero medidas existentes, duplicando código y perdiendo todo el trabajo acumulado.

**La regla inviolable del MCP:**
- **«No pude mirar» y «miré y no hay nada» son afirmaciones completamente distintas y jamás deben viajar por el mismo canal.**
- Si un catálogo está roto, el servidor **falla ruidosamente con `isError: true` y código `CATALOGO_INVALIDO`**.
- **Nunca devuelve `medidas: []` ni `total: 0`.** Un catálogo con 0 medidas es un proyecto válido sin archivos de políticas; un catálogo roto es una condición de falla de infraestructura.
- **No devuelve catálogos parciales:** Devolver las medidas que sí compilaron y ocultar la rota generaría una falsa sensación de cumplimiento, permitiendo que mutantes e infracciones pasen desapercibidos. Por eso el mensaje afirma explícitamente: `No se devolvió un catálogo parcial.`

---

## 8. Conversación 7: Proyecto con Escalares No Autorizadas

**Contexto de ejecución:**  
Un proyecto consumidor dispone de funciones escalares propias definidas en un archivo `escalares.py` en la raíz de su repositorio. Sin embargo, el servidor MCP fue iniciado por el usuario o anfitrión **sin** el modificador de confianza:  
`oracle-mcp --proyecto /home/workstation/Dev/proyecto_consumidor`  
*(Se omitió `--confiar-escalares`).*

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"oracle_catalogo_efectivo","arguments":{}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 9,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "ESCALARES_NO_AUTORIZADAS — /home/workstation/Dev/proyecto_consumidor/escalares.py es código externo; autorizalo en la configuración de arranque del servidor, no en esta llamada."
      }
    ],
    "isError": true
  }
}
```

### POR QUÉ esa respuesta y no otra:

1. **Frontera de seguridad de código arbitrario:** El archivo `escalares.py` contiene código ejecutable en Python. Cargar el catálogo implica ejecutar o registrar esas funciones. Si una llamada MCP pudiera auto-concederse confianza (por ejemplo, mediante un argumento opcional `confiar: true`), cualquier prompt malicioso o entrada contaminada podría vulnerar la seguridad del anfitrión.
2. **Autoridad restringida al arranque:** La autorización de ejecutar código externo es una prerrogativa exclusiva del usuario humano al configurar el proceso servidor (`--confiar-escalares`). La herramienta MCP se niega a recibir esa delegación en tiempo de ejecución.
3. **Fallo cerrado sin omisión:** Si el catálogo no puede cargarse sin sus escalares, el servidor **no devuelve una lista vacía ni carga un catálogo mutilado**. Levanta la excepción interna `EscalaresNoConfiables` de `nucleo.proyecto.escalares_del_proyecto` y el despachador MCP la transforma en el rechazo `ESCALARES_NO_AUTORIZADAS`.
4. **Mensaje claro:** Indica la ruta física absoluta del archivo que requiere autorización y aclara que el permiso debe concederse en el arranque del servidor y no en la llamada.

---

## 9. Conversación 8: `oracle_evaluar` en Verde (Evaluación Favorable sin Testigos)

**Contexto de ejecución:**  
El servidor corre fijado sobre el repositorio propio de Oracle:  
`oracle-mcp --proyecto /home/workstation/Dev/oracle`

El cliente evalúa puntualmente la medida efectiva `proceso.modulo_con_consumidor` pasando por valor una evidencia donde el módulo `"nucleo.medida"` tiene un importador real y comprobado que no es test.

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"oracle_evaluar","arguments":{"medida":{"id":"proceso.modulo_con_consumidor"},"evidencia":{"modulo":[{"nombre":"nucleo.medida"}],"importa":[{"b":"nucleo.medida","es_test":false}]}}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 10,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"advertencias\":[],\"alcance\":\"cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama\",\"alcance_derivado\":[\"    de `importa` no se sabe: nadie declaró sus campos\",\"    de `modulo` no se sabe: nadie declaró sus campos\"],\"entrada_sha256\":\"ab0a1aef8c73170e25036b40539eb7aae18325d54a0a55914d6c0c17d8f16495\",\"esquema\":\"oracle.mcp/evaluacion/v1\",\"estado\":\"verde\",\"medida\":\"proceso.modulo_con_consumidor\",\"oracle_version\":\"0.5.0\",\"proyecto\":\"/home/workstation/Dev/oracle\",\"testigos\":[],\"testigos_omitidos\":0,\"umbral\":{\"operador\":\"<=\",\"porque\":\"un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite\",\"segun\":\"contrato\",\"valor\":0},\"valor\":0}"
      }
    ],
    "structuredContent": {
      "esquema": "oracle.mcp/evaluacion/v1",
      "oracle_version": "0.5.0",
      "proyecto": "/home/workstation/Dev/oracle",
      "entrada_sha256": "ab0a1aef8c73170e25036b40539eb7aae18325d54a0a55914d6c0c17d8f16495",
      "medida": "proceso.modulo_con_consumidor",
      "estado": "verde",
      "valor": 0,
      "umbral": {
        "operador": "<=",
        "valor": 0,
        "segun": "contrato",
        "porque": "un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite"
      },
      "testigos": [],
      "testigos_omitidos": 0,
      "alcance": "cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama",
      "alcance_derivado": [
        "    de `importa` no se sabe: nadie declaró sus campos",
        "    de `modulo` no se sabe: nadie declaró sus campos"
      ],
      "advertencias": []
    },
    "isError": false
  }
}
```

### POR QUÉ esa respuesta y no otra:

1. **Evaluación puntual sin efectos secundarios:** La herramienta evalúa en memoria el estado de los datos aportados por valor contra la regla identificada. No escribe archivos de evidencia ni muta el estado del repositorio.
2. **Conformidad con el umbral (`estado: "verde"`):** La regla suma los importadores donde `i.b == m.nombre y i.es_test == false`. Para `"nucleo.medida"` encuentra 1 importador real. El filtro `donde importadores_reales == 0` descarta la fila por no ser infractora. El conteo final de módulos infractores es `0`, que satisface la cuádrupla de umbral `<= 0`. Por tanto, `ok` es verdadero y el servidor proyecta el veredicto unívocamente a `"estado": "verde"`.
3. **Ausencia limpia de testigos:** Al cumplirse el umbral, no existen registros infractores que publicar: `testigos` es `[]` y `testigos_omitidos` es `0`.
4. **Huella criptográfica de entrada (`entrada_sha256`):** Se calcula sobre la forma canónica de la medida combinada con la evidencia serializada (`_entrada_sha256`). Esto garantiza trazabilidad determinista: si la evidencia o la definición de la medida cambian, la huella varía inmediatamente.
5. **Declaración honesta de alcances (`alcance` y `alcance_derivado`):** El servidor entrega el punto ciego declarado por el autor en `alcance`, e inspecciona las declaraciones del proyecto para advertir en `alcance_derivado` que nadie declaró formalmente los campos de `importa` y `modulo`. Nunca finge una cobertura de campos que no ha sido auditada.

---

## 10. Conversación 9: `oracle_evaluar` en Rojo con Testigos (Acotación de Muestra)

**Contexto de ejecución:**  
El servidor corre fijado sobre el repositorio propio de Oracle:  
`oracle-mcp --proyecto /home/workstation/Dev/oracle`

El cliente evalúa `proceso.modulo_con_consumidor` contra una evidencia donde se presentan 7 módulos (`m1` a `m7`), pero la relación `importa` sólo registra un importador para un módulo ajeno (`"otro"`). Por ende, los 7 módulos carecen por completo de consumidores reales.

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"oracle_evaluar","arguments":{"medida":{"id":"proceso.modulo_con_consumidor"},"evidencia":{"modulo":[{"nombre":"m1"},{"nombre":"m2"},{"nombre":"m3"},{"nombre":"m4"},{"nombre":"m5"},{"nombre":"m6"},{"nombre":"m7"}],"importa":[{"b":"otro","es_test":false}]}}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 11,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"advertencias\":[],\"alcance\":\"cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama\",\"alcance_derivado\":[\"    de `importa` no se sabe: nadie declaró sus campos\",\"    de `modulo` no se sabe: nadie declaró sus campos\"],\"entrada_sha256\":\"f7175db977a15bb81fae02e9092a3c64fa372973b052aa067997a99639133601\",\"esquema\":\"oracle.mcp/evaluacion/v1\",\"estado\":\"rojo\",\"medida\":\"proceso.modulo_con_consumidor\",\"oracle_version\":\"0.5.0\",\"proyecto\":\"/home/workstation/Dev/oracle\",\"testigos\":[{\"_\":{\"importadores_reales\":0,\"modulo\":\"m1\"}},{\"_\":{\"importadores_reales\":0,\"modulo\":\"m2\"}},{\"_\":{\"importadores_reales\":0,\"modulo\":\"m3\"}},{\"_\":{\"importadores_reales\":0,\"modulo\":\"m4\"}},{\"_\":{\"importadores_reales\":0,\"modulo\":\"m5\"}}],\"testigos_omitidos\":2,\"umbral\":{\"operador\":\"<=\",\"porque\":\"un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite\",\"segun\":\"contrato\",\"valor\":0},\"valor\":7}"
      }
    ],
    "structuredContent": {
      "esquema": "oracle.mcp/evaluacion/v1",
      "oracle_version": "0.5.0",
      "proyecto": "/home/workstation/Dev/oracle",
      "entrada_sha256": "f7175db977a15bb81fae02e9092a3c64fa372973b052aa067997a99639133601",
      "medida": "proceso.modulo_con_consumidor",
      "estado": "rojo",
      "valor": 7,
      "umbral": {
        "operador": "<=",
        "valor": 0,
        "segun": "contrato",
        "porque": "un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite"
      },
      "testigos": [
        {
          "_": {
            "importadores_reales": 0,
            "modulo": "m1"
          }
        },
        {
          "_": {
            "importadores_reales": 0,
            "modulo": "m2"
          }
        },
        {
          "_": {
            "importadores_reales": 0,
            "modulo": "m3"
          }
        },
        {
          "_": {
            "importadores_reales": 0,
            "modulo": "m4"
          }
        },
        {
          "_": {
            "importadores_reales": 0,
            "modulo": "m5"
          }
        }
      ],
      "testigos_omitidos": 2,
      "alcance": "cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama",
      "alcance_derivado": [
        "    de `importa` no se sabe: nadie declaró sus campos",
        "    de `modulo` no se sabe: nadie declaró sus campos"
      ],
      "advertencias": []
    },
    "isError": false
  }
}
```

### POR QUÉ esa respuesta y no otra:

1. **Afirmación fáctica del defecto (`estado: "rojo"`):** El estado `rojo` afirma categóricamente que la evidencia examinada contradice el umbral de la regla. En este caso, el valor observado es `7`, que excede el límite máximo tolerable `<= 0`.
2. **Acotación normativa de testigos (`maxItems: 5`):** Por especificación de contrato, el servidor limita el arreglo `testigos` a un máximo de 5 elementos. Un agente de IA que recibe miles de testigos en un resultado satura su ventana de contexto y diluye su capacidad de razonamiento. Cinco testigos alcanzan holgadamente para comprender la forma concreta y material del defecto.
3. **Conteo honesto de omisiones (`testigos_omitidos: 2`):** El servidor no oculta que la muestra fue truncada. Al reportar `testigos_omitidos: 2` y `valor: 7`, el modelo comprende de inmediato que existen 7 transgresiones en total y que se le exhiben las primeras 5.
4. **Estructura transparente del testigo:** Cada testigo en la lista expone exactamente los campos agrupados y calculados (`{"modulo": "m1", "importadores_reales": 0}`), brindando evidencia comprobable e irrefutable de la infracción.
5. **No es un error de transporte (`isError: false`):** Que una medida resulte `rojo` no constituye una falla del servidor MCP. La operación se ejecutó limpiamente y la respuesta viaja como resultado estructurado normal, con `isError: false`.

---

## 11. Conversación 10: `oracle_evaluar` en `sin_evidencia` (Falta de Relación Obligatoria por `requiere`)

**Contexto de ejecución:**  
El servidor corre fijado sobre el repositorio propio de Oracle:  
`oracle-mcp --proyecto /home/workstation/Dev/oracle`

El cliente evalúa `proceso.modulo_con_consumidor`. La medida declara expresamente `requiere importa`. Sin embargo, el cliente proporciona la relación `modulo` pero omite totalmente la relación `importa` en su objeto de evidencia.

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"oracle_evaluar","arguments":{"medida":{"id":"proceso.modulo_con_consumidor"},"evidencia":{"modulo":[{"nombre":"nucleo.medida"}]}}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 12,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"advertencias\":[],\"alcance\":\"cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama\",\"alcance_derivado\":[\"    de `importa` no se sabe: nadie declaró sus campos\",\"    de `modulo` no se sabe: nadie declaró sus campos\"],\"entrada_sha256\":\"27db1082a343e4efc1aa00d4118eec74afbc0bc3f5e749504d23c46e257fbad4\",\"esquema\":\"oracle.mcp/evaluacion/v1\",\"estado\":\"sin_evidencia\",\"medida\":\"proceso.modulo_con_consumidor\",\"oracle_version\":\"0.5.0\",\"proyecto\":\"/home/workstation/Dev/oracle\",\"testigos\":[],\"testigos_omitidos\":0,\"umbral\":{\"operador\":\"<=\",\"porque\":\"un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite\",\"segun\":\"contrato\",\"valor\":0},\"valor\":0}"
      }
    ],
    "structuredContent": {
      "esquema": "oracle.mcp/evaluacion/v1",
      "oracle_version": "0.5.0",
      "proyecto": "/home/workstation/Dev/oracle",
      "entrada_sha256": "27db1082a343e4efc1aa00d4118eec74afbc0bc3f5e749504d23c46e257fbad4",
      "medida": "proceso.modulo_con_consumidor",
      "estado": "sin_evidencia",
      "valor": 0,
      "umbral": {
        "operador": "<=",
        "valor": 0,
        "segun": "contrato",
        "porque": "un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite"
      },
      "testigos": [],
      "testigos_omitidos": 0,
      "alcance": "cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama",
      "alcance_derivado": [
        "    de `importa` no se sabe: nadie declaró sus campos",
        "    de `modulo` no se sabe: nadie declaró sus campos"
      ],
      "advertencias": []
    },
    "isError": false
  }
}
```

### POR QUÉ este es el fixture más crítico de `oracle_evaluar`:

1. **La distinción ontológica fundamental entre «no pude mirar» y «miré y falló»:**  
   Colapsar `sin_evidencia` en `rojo` o en `verde` es el defecto histórico que ya costó un arreglo real en `tools/contexto.py`.
   - Si el servidor respondiera `rojo`, le estaría afirmando al agente que los módulos de su software están huérfanos y violan la política arquitectónica, cuando en realidad lo que ocurrió fue un déficit de instrumentación: nadie extrajo la tabla de dependencias (`importa`). El agente intentaría "remediar" código que no estaba roto.
   - Si el servidor respondiera `verde` (como sucedería por defecto en un álgebra laxa donde una relación vacía produce 0 filas y 0 <= 0), crearía un **falso verde por vaciedad**: un proyecto sin evidencias pasaría como inmaculado.
2. **La semántica estricta de la cláusula `requiere`:**  
   `proceso.modulo_con_consumidor` declara formalmente `requiere importa`. Esta cláusula instruye al álgebra de que la presencia de datos en `importa` es una precondición obligatoria para emitir juicio. Al omitirse `importa` (o venir como lista vacía), el álgebra emite `sin_evidencia: true`.
3. **El estado ternario en el esquema (`verde`, `rojo`, `sin_evidencia`):**  
   El servidor no simula un booleano `ok: false`. Entrega explícitamente `"estado": "sin_evidencia"` en `structuredContent`.
4. **Respuesta exitosa de herramienta:** Al igual que en los casos anteriores, no viaja con `isError: true`. La herramienta funcionó a la perfección y determinó que las precondiciones de evidencia no fueron satisfechas.

---

## 12. Conversación 11: Rechazo de `archivo` en `oracle_evaluar` (Confinamiento de Raíz)

**Contexto de ejecución:**  
Un cliente intenta evaluar una medida indicando una ruta de archivo en el sistema de archivos (`"archivo": "catalogos/meta/meta.agrupar_no_agranda_la_relacion.oracle"` o intentando escapar con `"../fuera.oracle"` o `"/etc/passwd"`).

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":13,"method":"tools/call","params":{"name":"oracle_evaluar","arguments":{"medida":{"archivo":"catalogos/meta/meta.agrupar_no_agranda_la_relacion.oracle"},"evidencia":{}}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 13,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "ARGUMENTOS_INVALIDOS — $.medida: {\"archivo\":\"catalogos/meta/meta.agrupar_no_agranda_la_relacion.oracle\"}; se esperaba exactamente {id} o {texto, formato}; archivo no está admitido."
      }
    ],
    "isError": true
  }
}
```

### POR QUÉ esa respuesta y no otra:

1. **Invariante de confinamiento estricto:** La raíz del proyecto queda fijada al arrancar el servidor (`--proyecto <ruta>`). Si la herramienta aceptara una clave `archivo` con rutas relativas o absolutas, un prompt inyectado en datos medidos o un modelo descontrolado podría inducir lecturas fuera del repositorio (`../../etc/shadow`), vulnerando el principio de aislamiento del servidor MCP.
2. **Unión cerrada sin atajos:** El esquema normativo de entrada para `medida` define una unión cerrada estricta:
   - Modo id de catálogo: `{"id": "dominio.nombre"}`
   - Modo memoria en tránsito: `{"texto": "...", "formato": "oracle"|"json"}`
   El validador de `tools/mcp.py` rechaza categóricamente cualquier otra propiedad con `isError: true`.
3. **No duplicar los verbos de consola:** Para evaluar archivos ya guardados en disco existe el CLI (`oracle medida probar`). La herramienta MCP existe para permitir la evaluación efímera y estructurada en memoria sin tocar el disco.
4. **Mensaje normativo de error:** El mensaje indica la ruta exacta del argumento inválido (`$.medida`), exhibe el valor recibido y enuncia con precisión la forma esperada: `se esperaba exactamente {id} o {texto, formato}; archivo no está admitido.`

---

## 13. Conversación 12: `oracle_desafiar` con Dos Polaridades (`todos_detectados_por_conducta`)

**Contexto de ejecución:**  
El servidor corre fijado sobre el repositorio propio de Oracle:  
`oracle-mcp --proyecto /home/workstation/Dev/oracle`

El cliente desafía la medida efectiva `meta.ningun_umbral_de_igualdad`. La medida cuenta en el repositorio con 3 casos en su corpus (`corpus/meta/067-umbral-de-igualdad.json`, `068-umbral-de-orden.caso` y `071-catalogos-reales-sin-umbral-de-igualdad.caso`), los cuales satisfacen ambas polaridades (2 verdes y 1 rojo).

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":14,"method":"tools/call","params":{"name":"oracle_desafiar","arguments":{"medida":{"id":"meta.ningun_umbral_de_igualdad"}}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 14,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"advertencias\":[],\"casos\":3,\"conclusion\":\"todos_detectados_por_conducta\",\"discordancias\":[],\"entrada_sha256\":\"430e7c76faeee3cfadaab002e4b2b638968fe5a5dd295a00024df6ce800e48b0\",\"esquema\":\"oracle.mcp/desafio/v1\",\"medida\":\"meta.ningun_umbral_de_igualdad\",\"mutacion\":{\"detectados_por_conducta\":8,\"generados\":8,\"no_detectados\":[],\"rechazados_por_el_algebra\":0},\"oracle_version\":\"0.5.0\",\"proyecto\":\"/home/workstation/Dev/oracle\"}"
      }
    ],
    "structuredContent": {
      "esquema": "oracle.mcp/desafio/v1",
      "oracle_version": "0.5.0",
      "proyecto": "/home/workstation/Dev/oracle",
      "entrada_sha256": "430e7c76faeee3cfadaab002e4b2b638968fe5a5dd295a00024df6ce800e48b0",
      "medida": "meta.ningun_umbral_de_igualdad",
      "advertencias": [],
      "conclusion": "todos_detectados_por_conducta",
      "discordancias": [],
      "casos": 3,
      "mutacion": {
        "generados": 8,
        "detectados_por_conducta": 8,
        "rechazados_por_el_algebra": 0,
        "no_detectados": []
      }
    },
    "isError": false
  }
}
```

### POR QUÉ esa respuesta y no otra:

1. **El ciclo completo de falsación en memoria:**  
   El servidor:
   1. Carga y compila la medida `meta.ningun_umbral_de_igualdad`.
   2. Reúne los casos del corpus del proyecto cuyo campo `medida` coincide con su identificador (3 casos).
   3. Evalúa la regla original contra cada uno de los 3 casos: todos reproducen su expectativa (`discordancias: []`).
   4. Constata la existencia de ambas polaridades: hay al menos un caso que espera `verde` y al menos un caso que espera `rojo`.
   5. Genera los 8 mutantes sintácticos a partir de la representación canónica de la regla.
   6. Ejecuta los 8 mutantes contra los 3 casos y comprueba que para cada uno de los 8 mutantes existe al menos un caso de prueba que altera su conducta (cambiando veredicto o valor).
2. **Conclusión falsable, no elogio vacío:**  
   La conclusión es `todos_detectados_por_conducta` y **jamás** «correcta», «aprobada» ni «lista_para_guardar». El servidor se abstiene de emitir afirmaciones metafísicas sobre la "corrección" de una regla: reporta estrictamente el hecho empírico de que estos 8 mutadores fueron discriminados por estos 3 casos de prueba.
3. **Desglose transparente del álgebra de mutación:**  
   El objeto `mutacion` separa minuciosamente:
   - `generados: 8`: denominador total de mutantes producidos.
   - `detectados_por_conducta: 8`: mutantes neutralizados por cambio conductual.
   - `rechazados_por_el_algebra: 0`: mutantes que levantaron excepciones en el motor (ninguno en este caso).
   - `no_detectados: []`: mutantes sobrevivientes que ningún caso logró distinguir.
4. **Sin persistencia lateral:** Toda la mutación y evaluación ocurre estrictamente en memoria; no se crean ni modifican archivos en `corpus/` ni en `catalogos/`.

---

## 14. Conversación 13: `oracle_desafiar` con Falta de Polaridad (`faltan_polaridades` y Sin Mutación)

**Contexto de ejecución:**  
El cliente desafía `meta.ningun_umbral_de_igualdad` desconectando el corpus del repositorio (`usar_evidencia_del_proyecto: false`) y aportando un único caso efímero que sólo espera `verde`.

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":15,"method":"tools/call","params":{"name":"oracle_desafiar","arguments":{"medida":{"id":"meta.ningun_umbral_de_igualdad"},"usar_evidencia_del_proyecto":false,"casos":[{"id":"caso_solo_verde","espera":"verde","evidencia":{"medida":[{"comparador":"<="}]}}]}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 15,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"advertencias\":[\"ningún caso salió del corpus del proyecto: lo que se desafió son evidencias de esta llamada, y una evidencia escrita para la medida puede repetir su error\"],\"casos\":1,\"conclusion\":\"faltan_polaridades\",\"discordancias\":[],\"entrada_sha256\":\"e636989c63d75f9e226b2ea6b9d3815ef88986fc27067ba1afa5e527ec6576ed\",\"esquema\":\"oracle.mcp/desafio/v1\",\"medida\":\"meta.ningun_umbral_de_igualdad\",\"mutacion\":null,\"oracle_version\":\"0.5.0\",\"proyecto\":\"/home/workstation/Dev/oracle\"}"
      }
    ],
    "structuredContent": {
      "esquema": "oracle.mcp/desafio/v1",
      "oracle_version": "0.5.0",
      "proyecto": "/home/workstation/Dev/oracle",
      "entrada_sha256": "e636989c63d75f9e226b2ea6b9d3815ef88986fc27067ba1afa5e527ec6576ed",
      "medida": "meta.ningun_umbral_de_igualdad",
      "advertencias": [
        "ningún caso salió del corpus del proyecto: lo que se desafió son evidencias de esta llamada, y una evidencia escrita para la medida puede repetir su error"
      ],
      "conclusion": "faltan_polaridades",
      "discordancias": [],
      "casos": 1,
      "mutacion": null
    },
    "isError": false
  }
}
```

### POR QUÉ esa respuesta y no otra:

1. **La exigencia metodológica de las dos polaridades:**  
   Una prueba con una sola polaridad no es un arnés de falsación: una regla que evalúe siempre `true` pasaría indemne cualquier suite compuesta exclusivamente por casos que esperan `verde`. Para que una medida demuestre capacidad de discriminación, el agente debe obligatoriamente presentar al menos una evidencia donde deba pasar (`verde`) y al menos una evidencia donde deba ofender (`rojo`).
2. **Corte inmediato sin mutar (`mutacion: null`):**  
   Correr mutación sobre una suite desprovista de polaridad negativa produciría mutantes que parecen morir pero que no prueban nada, generando un costo computacional injustificado y métricas engañosas. El servidor aborta el lazo antes de generar mutantes, asignando estrictamente `mutacion: null`.
3. **Advertencia de evidencia fabricada:**  
   Dado que ningún caso provino del corpus histórico del proyecto (`usar_evidencia_del_proyecto: false`), el campo `advertencias` alerta con honestidad: `ningún caso salió del corpus del proyecto: lo que se desafió son evidencias de esta llamada, y una evidencia escrita para la medida puede repetir su error`.

---

## 15. Conversación 14: `oracle_desafiar` cuando el Original no Reproduce (`original_no_reproduce` y Sin Mutación)

**Contexto de ejecución:**  
El cliente desafía `meta.ningun_umbral_de_igualdad` enviando un caso efímero cuya expectativa de veredicto contradice lo que la medida original realmente calcula: el caso declara `espera: "rojo"`, pero la evidencia suministrada contiene una medida con comparador `"<="`, la cual evalúa legalmente a `0 <= 0` (`verde`).

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":16,"method":"tools/call","params":{"name":"oracle_desafiar","arguments":{"medida":{"id":"meta.ningun_umbral_de_igualdad"},"usar_evidencia_del_proyecto":false,"casos":[{"id":"caso_discordante","espera":"rojo","evidencia":{"medida":[{"comparador":"<="}]}}]}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 16,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"advertencias\":[\"ningún caso salió del corpus del proyecto: lo que se desafió son evidencias de esta llamada, y una evidencia escrita para la medida puede repetir su error\"],\"casos\":1,\"conclusion\":\"original_no_reproduce\",\"discordancias\":[{\"caso\":\"caso_discordante\",\"esperado\":\"rojo\",\"obtenido\":\"verde\"}],\"entrada_sha256\":\"3410260f300d165732a7692c2089eb587e394a1e275d5a4a99593e2534d34916\",\"esquema\":\"oracle.mcp/desafio/v1\",\"medida\":\"meta.ningun_umbral_de_igualdad\",\"mutacion\":null,\"oracle_version\":\"0.5.0\",\"proyecto\":\"/home/workstation/Dev/oracle\"}"
      }
    ],
    "structuredContent": {
      "esquema": "oracle.mcp/desafio/v1",
      "oracle_version": "0.5.0",
      "proyecto": "/home/workstation/Dev/oracle",
      "entrada_sha256": "3410260f300d165732a7692c2089eb587e394a1e275d5a4a99593e2534d34916",
      "medida": "meta.ningun_umbral_de_igualdad",
      "advertencias": [
        "ningún caso salió del corpus del proyecto: lo que se desafió son evidencias de esta llamada, y una evidencia escrita para la medida puede repetir su error"
      ],
      "conclusion": "original_no_reproduce",
      "discordancias": [
        {
          "caso": "caso_discordante",
          "esperado": "rojo",
          "obtenido": "verde"
        }
      ],
      "casos": 1,
      "mutacion": null
    },
    "isError": false
  }
}
```

### POR QUÉ cortar acá y no seguir (el peligro del número convincente):

1. **La divergencia entre el arnés interno y el servidor MCP:**  
   En el arnés de regresión masiva del núcleo (`nucleo.mutacion.correr`), un caso que no está en su estado esperado se descarta en silencio («no fija nada») para permitir que la suite global continúe. Sin embargo, en la interfaz MCP con un agente interactivo, **continuar sería devastador**.
2. **Mutar sobre una base desalineada mide otra cosa:**  
   Si el servidor procediera a mutar ignorando el caso desalineado o evaluando mutantes contra una premisa falsa, el reporte final arrojaría estadísticas de mutación numéricamente perfectas (porcentajes de detección, mutantes eliminados). El agente de IA vería esos números matemáticamente pulcros y asumiría que su regla fue validada, cuando en realidad la prueba jamás llegó a medir lo que el autor pretendía. El número saldría igual de convincente, pero midiendo una ficción.
3. **Identificación exacta de la discordancia:**  
   El servidor corta de inmediato el lazo y expone el objeto desalineado en `discordancias`:
   - `caso: "caso_discordante"`: el identificador exacto del caso fallido.
   - `esperado: "rojo"`: la expectativa declarada.
   - `obtenido: "verde"`: el veredicto real del original.
   El agente sabe al instante qué caso debe corregir.
4. **Sin mutación espuria (`mutacion: null`):** La mutación no se ejecuta ni genera datos engañosos.

---

## 16. Conversación 15: Rechazo de Procedencia Observada en Casos Efímeros (`PROCEDENCIA_NO_ADMITIDA`)

**Contexto de ejecución:**  
Un cliente desafía `meta.ningun_umbral_de_igualdad` enviando en la llamada un caso efímero que incluye la propiedad `"procedencia": "observada"`.

### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":17,"method":"tools/call","params":{"name":"oracle_desafiar","arguments":{"medida":{"id":"meta.ningun_umbral_de_igualdad"},"casos":[{"id":"caso_falso_observado","espera":"verde","evidencia":{"medida":[{"comparador":"<="}]},"procedencia":"observada"}]}}}
```

### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 17,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "PROCEDENCIA_NO_ADMITIDA — un caso de la llamada no declara procedencia: una llamada no puede convertir evidencia fabricada en evidencia observada."
      }
    ],
    "isError": true
  }
}
```

### POR QUÉ esto no es una restricción de forma sino de fondo:

1. **La frontera epistémica entre observación y fabricación:**  
   En la ontología de Oracle, la etiqueta `procedencia: observada` tiene un estatus jurídico privilegiado: certifica que una evidencia fue capturada directamente de un incidente real en un sistema en producción o en una ejecución trazada del arnés, respaldada por un commit en git. Esa procedencia es lo que sostiene la legitimidad del corpus frente a la tentación de inventar casos ad hoc para que una regla pase.
2. **Prohibición de blanqueo de evidencia:**  
   Cualquier evidencia transmitida dentro del payload de una llamada JSON-RPC efímera es, por definición física y ontológica, evidencia sintética o fabricada en ese instante por quien llama. Si el servidor aceptara que el cliente estampe `"procedencia": "observada"` en su mensaje JSON, la herramienta MCP se convertiría en un mecanismo para blanquear evidencia fabricada, dotándola de una categoría probatoria que jamás ganó en el mundo físico.
3. **Fallo cerrado con `isError: true`:**  
   El validador de argumentos en `tools/mcp.py` bloquea la llamada con el código cerrado `PROCEDENCIA_NO_ADMITIDA`. La procedencia observada no se negocia por cable: sólo puede provenir de archivos residentes en el corpus del repositorio versionado.

---

## 17. Conversación 16: `CASO_REPETIDO` en sus Dos Variantes (Corpus vs Misma Llamada)

El servidor MCP detecta duplicaciones de identificadores de casos y emite mensajes diferenciados según la procedencia del conflicto, orientando al agente de forma unívoca hacia el sitio exacto del error.

### 17.1. Variante 1: El ID choca con un caso existente en el corpus del proyecto

**Contexto de ejecución:**  
El cliente intenta evaluar un caso efímero con id `"067-umbral-de-igualdad"`. Dicho caso ya reside físicamente en `corpus/meta/067-umbral-de-igualdad.json`.

#### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":18,"method":"tools/call","params":{"name":"oracle_desafiar","arguments":{"medida":{"id":"meta.ningun_umbral_de_igualdad"},"casos":[{"id":"067-umbral-de-igualdad","espera":"rojo","evidencia":{"medida":[{"comparador":"=="}]}}]}}}
```

#### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 18,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "CASO_REPETIDO — «067-umbral-de-igualdad» ya existe en el corpus del proyecto; renombralo. No se eligió uno de los dos."
      }
    ],
    "isError": true
  }
}
```

---

### 17.2. Variante 2: El ID aparece repetido dentro de la misma llamada

**Contexto de ejecución:**  
El cliente envía dos casos efímeros con el mismo identificador `"caso_duplicado"` en el arreglo `casos`.

#### Qué se manda por stdin (Cliente → Servidor):

```json
{"jsonrpc":"2.0","id":19,"method":"tools/call","params":{"name":"oracle_desafiar","arguments":{"medida":{"id":"meta.ningun_umbral_de_igualdad"},"casos":[{"id":"caso_duplicado","espera":"verde","evidencia":{"medida":[{"comparador":"<="}]}},{"id":"caso_duplicado","espera":"rojo","evidencia":{"medida":[{"comparador":"=="}]}}]}}}
```

#### Qué tiene que volver por stdout (Servidor → Cliente):

```json
{
  "jsonrpc": "2.0",
  "id": 19,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "CASO_REPETIDO — «caso_duplicado» aparece dos veces en esta llamada; renombralo. No se eligió uno de los dos."
      }
    ],
    "isError": true
  }
}
```

### POR QUÉ esa respuesta y por qué la distinción del mensaje es crítica:

1. **Orientación diagnóstica correcta para el agente:**  
   Un mensaje genérico que dijera simplemente «el caso ya existe en el proyecto» confundiría fatalmente al modelo cuando el error está dentro de su propio payload JSON: el agente iría a buscar archivos en el disco, intentaría leer `corpus/` o supondría que alguien editó el árbol local. Al declarar con total precisión `aparece dos veces en esta llamada`, el mensaje instruye al agente a corregir sus argumentos inmediatos. Análogamente, cuando el conflicto es con el disco, `ya existe en el corpus del proyecto` le indica que debe elegir un nuevo identificador para no enmascarar la prueba histórica.
2. **Prohibición absoluta del principio «el último gana» (*last-write-wins*):**  
   Permitir que un caso repetido prevalezca en silencio sobre otro anterior es la forma más común en que una prueba escrita ad hoc neutraliza inadvertidamente a la prueba que estaba detectando el defecto. El servidor rechaza la ambigüedad con un fallo simétrico explícito: `No se eligió uno de los dos`.
3. **Integridad referencial determinista:** La suite de casos de un desafío debe componer un conjunto unívoco y libre de colisiones.

---

## 18. Matriz de Reconciliación de Aceptación

Esta tabla consolida las expectativas que la suite de tests de `tools/mcp.py` debe comprobar de manera estricta para las tres herramientas del servidor:

| Caso de prueba / Conversación | Herramienta | Entrada / Argumentos | Salida esperada / Código | Estado MCP | `structuredContent` | Aserción crítica de falsabilidad |
|---|---|---|---|---|---|---|
| **Handshake: initialize** | Sistema | `initialize` con protocolo `2025-11-25` | `serverInfo.name == "oracle-mcp"`, `version == "0.5.0"`, `capabilities == {"tools": {}}` | Éxito | No | Solo anuncia herramientas; no anuncia resources, prompts ni sampling. |
| **Handshake: tools/list** | Sistema | `tools/list` sin parámetros | Arreglo de 3 herramientas fijas con anotaciones | Éxito | No | Lista inmutable de 3 herramientas; esquemas con `additionalProperties: false`. |
| **Índice compacto** | `oracle_catalogo_efectivo` | `{}` | `total == 57`, `detalle == false`, 57 medidas ordenadas | `isError: false` | Sí | `total` es el catálogo entero; filas sólo con `id`, `origen`, `fijacion`. |
| **Detalle selectivo** | `oracle_catalogo_efectivo` | `ids: ["..."]` | `total == 57`, `detalle == true`, medidas pedidas | `isError: false` | Sí | `total` no cambia; todos los campos de auditoría presentes y ordenados. |
| **Lista vacía rechazada** | `oracle_catalogo_efectivo` | `ids: []` | `ARGUMENTOS_INVALIDOS` | `isError: true` | No | Rechazo estricto de esquema; no crea tercer modo. |
| **Medida no efectiva** | `oracle_catalogo_efectivo` | Id ajeno `del_origen` en un consumidor | `MEDIDA_NO_EFECTIVA` | `isError: true` | No | Distingue presencia sin jurisdicción; evita duplicados locales innecesarios. |
| **Medida desconocida** | `oracle_catalogo_efectivo` | Id inexistente en toda fuente | `MEDIDA_DESCONOCIDA` | `isError: true` | No | Distingue id ausente; aconseja consultar sin ids. |
| **Catálogo roto** | `oracle_catalogo_efectivo` | Sintaxis inválida en archivo `.oracle` | `CATALOGO_INVALIDO` | `isError: true` | No | Fallo cerrado: **nunca** devuelve `medidas: []` ni `total: 0`. |
| **Escalares sin autorizar** | `oracle_catalogo_efectivo` | Proyecto con `escalares.py` sin confianza | `ESCALARES_NO_AUTORIZADAS` | `isError: true` | No | Bloqueo de seguridad: la llamada no puede auto-confiarse. |
| **Evaluar: verde** | `oracle_evaluar` | Medida y evidencia conforme | `estado == "verde"`, `valor == 0`, `testigos == []` | `isError: false` | Sí | Evaluación puntual favorable; valor satisface el umbral sin testigos. |
| **Evaluar: rojo con testigos** | `oracle_evaluar` | Evidencia con 7 transgresores | `estado == "rojo"`, `valor == 7`, `testigos` (5 items), `testigos_omitidos == 2` | `isError: false` | Sí | Afirma defecto observado; trunca a 5 testigos con reporte honesto de omitidos. |
| **Evaluar: sin evidencia** | `oracle_evaluar` | Medida con `requiere` y evidencia sin la relación | `estado == "sin_evidencia"`, `valor == 0` | `isError: false` | Sí | Distingue «no pude mirar» de «miré y falló»; no emite falso verde ni falso rojo. |
| **Evaluar: rechazo de archivo** | `oracle_evaluar` | `medida.archivo: "..."` | `ARGUMENTOS_INVALIDOS` | `isError: true` | No | Seguridad: prohíbe rutas y confina lecturas estrictamente a la memoria o catálogo. |
| **Desafiar: dos polaridades** | `oracle_desafiar` | Medida con corpus verde y rojo | `conclusion == "todos_detectados_por_conducta"`, mutación completa | `isError: false` | Sí | Lazo de mutación exitoso; no emite afirmaciones no comprobadas sobre corrección. |
| **Desafiar: falta polaridad** | `oracle_desafiar` | Suite con sólo casos verdes | `conclusion == "faltan_polaridades"`, `mutacion == null` | `isError: false` | Sí | Aborta de inmediato sin mutar; exige ambas polaridades antes de gastar cómputo. |
| **Desafiar: original no reproduce** | `oracle_desafiar` | Caso efímero discordante con el original | `conclusion == "original_no_reproduce"`, `mutacion == null` | `isError: false` | Sí | Corta sin mutar; impide publicar números convincentes sobre bases desalineadas. |
| **Desafiar: procedencia prohibida** | `oracle_desafiar` | `procedencia: "observada"` en caso de la llamada | `PROCEDENCIA_NO_ADMITIDA` | `isError: true` | No | Integridad epistémica: una llamada efímera no puede blanquear evidencia fabricada. |
| **Desafiar: caso repetido (corpus)** | `oracle_desafiar` | ID que colisiona con archivo de `corpus/` | `CASO_REPETIDO` señalando el corpus del proyecto | `isError: true` | No | Manda a buscar al disco; prohíbe que el caso efímero opaque al del proyecto. |
| **Desafiar: caso repetido (llamada)** | `oracle_desafiar` | ID duplicado en el arreglo `casos` | `CASO_REPETIDO` señalando la misma llamada | `isError: true` | No | Manda a buscar en el payload; rechaza la prevalencia implícita del último. |

