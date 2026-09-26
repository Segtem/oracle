# Contrato MCP de Oracle: consultar, evaluar y falsar sin escribir

**Fecha:** 2026-09-04
**Estado:** diseño; no especifica una implementación ya existente

## Decisión

El servidor expone **cinco herramientas** y es de sólo lectura respecto del proyecto:
`oracle_catalogo_efectivo`, `oracle_evaluar`, `oracle_desafiar`, `oracle_juzgar` y `oracle_tareas`.
Las cinco reciben un proyecto fijado al arrancar el proceso; ninguna acepta una ruta de proyecto por
llamada y ninguna crea, modifica ni borra archivos.

Cinco herramientas responden a cinco preguntas distintas del agente sin mezclar costos ni autoridades:

1. **¿Qué me obliga y por qué?** (`oracle_catalogo_efectivo`) Es una consulta sobre el proyecto y su
   jurisdicción.
2. **¿Qué hace esta medida con esta evidencia?** (`oracle_evaluar`) Es una ejecución puntual que
   conserva valor, umbral, testigos, ausencia de evidencia y estado de sombra (con cota y perdón).
3. **¿Qué parte del candidato todavía no está fijada?** (`oracle_desafiar`) Es un experimento de
   falsación sobre varias evidencias y los mutantes de la medida.
4. **¿Esta evidencia cumple el catálogo efectivo entero?** (`oracle_juzgar`) Es un juicio completo
   contra el proyecto, que respeta sombras, cotas y medidas no aplicadas.
5. **¿Cuál es el estado del tracker local?** (`oracle_tareas`) Es una lectura del seguimiento de
   tareas (`tareas/`) para agentes sin acceso a shell, sin permitir escrituras que romperían la
   correspondencia con Git.

Esta decisión contradice la inclinación de `vault-kb/planes/PLAN-0.6.0-MCP.md` hacia `oracle_proponer`. La compuerta
«trae un rojo y un verde» es valiosa como experimento, pero no autoriza a llamar buena a la medida:
las dos evidencias pueden haber sido fabricadas para repetir exactamente su error. Guardar después de
esa compuerta agrega una escritura riesgosa, duplica una capacidad que el agente ya tiene mediante su
editor y convierte evidencia insuficiente en una apariencia de aprobación. `oracle_desafiar` conserva
la parte nueva —evaluar ambas polaridades y mutar sin persistir— sin hacer esa promesa.

El plan también describe `oracle_contexto` como respuesta correcta a «qué medidas aplican a este
proyecto». Hoy no lo es. `tools/contexto.py::_medidas` llama a `catalogos_a_cargar`, mientras
`nucleo/proyecto.py::catalogo_efectivo` agrega el filtro de `ambito` introducido en 0.5.0. La
herramienta nueva tiene que llamar a esta última función; no debe copiar su criterio ni arreglar la
respuesta después de cargar.

## Autoridad y modelo de ejecución

La configuración del anfitrión arranca el proceso como `oracle-mcp --proyecto <ruta>`. La resolución
es la de `nucleo.proyecto`, pero ocurre una sola vez, antes de aceptar mensajes. La raíz física queda
fijada durante toda la vida del proceso y se muestra en cada respuesta. No existe un parámetro
`proyecto`, `ruta`, `archivo` ni URI en las herramientas. Así, una instrucción dentro de un archivo
medido no puede convencer al agente de ampliar la autoridad del servidor a otro árbol.

Las escalares externas merecen el mismo corte. Por omisión no se ejecuta `escalares.py`. El usuario
puede autorizarlo al configurar el servidor con `--confiar-escalares`; una llamada MCP no puede
concederse esa confianza a sí misma. Cuando una operación necesita una escalar no autorizada, falla
con `ESCALARES_NO_AUTORIZADAS`, no carga un catálogo parcial y no devuelve una lista vacía.

Las cinco herramientas llevan las anotaciones `readOnlyHint: true`, `destructiveHint: false`,
`idempotentHint: true` y `openWorldHint: false`. Son pistas para el anfitrión, no controles de
seguridad; el control real es que el despachador no tenga ningún camino de escritura y que la raíz
no sea parte de los argumentos.

Cada respuesta exitosa incluye:

- `oracle_version`, para distinguir un binario instalado y viejo del checkout que el agente cree
  estar usando;
- `proyecto`, la raíz canónica que efectivamente se leyó;
- una huella SHA-256 del conjunto ordenado de entradas leídas o de los argumentos normalizados.

En el catálogo, `huella_proyecto` cubre identidad y bytes de configuración, macros, fuentes de
medidas, corpus y diferenciales que participaron del resultado. En evaluación y desafío,
`entrada_sha256` cubre la forma canónica ya expandida de la medida y la evidencia normalizada; usar
sólo el id sería insuficiente porque el mismo id puede cambiar de contenido entre dos llamadas.

La huella no demuestra que la semántica sea correcta. Sirve para una afirmación más chica y
comprobable: dos respuestas que dicen provenir del mismo estado deben traer la misma huella. El
servidor calcula el conjunto de archivos y la huella antes y después de la operación; si cambiaron,
rechaza con `PROYECTO_CAMBIO_DURANTE_LA_CONSULTA` y pide reintentar. Nunca mezcla silenciosamente dos
estados del árbol.

## Superficie normativa

El siguiente arreglo es el contenido normativo de `tools/list`, sin el envoltorio JSON-RPC. Los
esquemas cierran propiedades con `additionalProperties: false`: un error de nombre no se ignora.
Los campos opcionales de una medida sólo aparecen en modo detalle; el servidor valida como
poscondición que `detalle: true` implique que todos estén presentes.

El bloque siguiente se genera desde `tools.mcp.HERRAMIENTAS` con
`python3 -m tools.mcp_contrato` (verificar con `--check`).

<!-- herramientas-json:inicio -->
```json
[
  {
    "name": "oracle_catalogo_efectivo",
    "title": "Catálogo efectivo de Oracle",
    "description": "Consulta medidas efectivas del proyecto fijado. Sin ids: índice; con ids: detalle. No evalúa evidencia.",
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
    "description": "Evalúa una medida efectiva por id o texto sin guardar contra evidencia JSON. Distingue verde, rojo y sin_evidencia; incluye umbral, testigos y alcance. No demuestra corrección de la medida.",
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
        "sombra",
        "testigos",
        "testigos_omitidos",
        "alcance",
        "alcance_derivado",
        "advertencias"
      ],
      "properties": {
        "esquema": {
          "const": "oracle.mcp/evaluacion/v2"
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
        "sombra": {
          "oneOf": [
            {
              "type": "null"
            },
            {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "desde",
                "porque",
                "cota",
                "perdona"
              ],
              "properties": {
                "desde": {
                  "type": "string"
                },
                "porque": {
                  "type": "string"
                },
                "cota": {
                  "type": [
                    "integer",
                    "null"
                  ]
                },
                "perdona": {
                  "type": "boolean"
                }
              }
            }
          ]
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
    "description": "Desafía por id o texto con corpus y diferenciales opcionales y casos efímeros. Exige ambas polaridades y muta; informa discordancias, sobrevivientes y rechazos. No demuestra corrección semántica.",
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
                  "rojo",
                  "sin_evidencia"
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
  },
  {
    "name": "oracle_juzgar",
    "title": "Juzgar evidencia contra el catálogo efectivo",
    "description": "Juzga evidencia contra el catálogo efectivo (ids selecciona un subconjunto). Informa no aplicadas, sombras y cotas. ok exige medidas satisfechas y sombras dentro de cota; no ejecuta escalares no autorizadas.",
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
        "evidencia"
      ],
      "properties": {
        "evidencia": {
          "$ref": "#/$defs/evidencia"
        },
        "ids": {
          "type": "array",
          "minItems": 1,
          "uniqueItems": true,
          "items": {
            "type": "string",
            "pattern": "^[a-z][a-z0-9_]*(?:\\.[a-z][a-z0-9_]*)+$"
          },
          "description": "Ids efectivos a evaluar. Omitir para evaluar todas las aplicables del catálogo."
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
        "ok",
        "medidas",
        "no_aplicadas",
        "no_juzgaron",
        "advertencias"
      ],
      "properties": {
        "esquema": {
          "const": "oracle.mcp/juzgar/v1"
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
        "ok": {
          "type": "boolean"
        },
        "medidas": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "id",
              "estado",
              "valor",
              "umbral",
              "sombra",
              "testigos",
              "testigos_omitidos",
              "alcance"
            ],
            "properties": {
              "id": {
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
              "sombra": {
                "oneOf": [
                  {
                    "type": "null"
                  },
                  {
                    "type": "object",
                    "additionalProperties": false,
                    "required": [
                      "desde",
                      "porque",
                      "cota",
                      "perdona"
                    ],
                    "properties": {
                      "desde": {
                        "type": "string"
                      },
                      "porque": {
                        "type": "string"
                      },
                      "cota": {
                        "type": [
                          "integer",
                          "null"
                        ]
                      },
                      "perdona": {
                        "type": "boolean"
                      }
                    }
                  }
                ]
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
              }
            }
          }
        },
        "no_aplicadas": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "id",
              "faltan"
            ],
            "properties": {
              "id": {
                "type": "string"
              },
              "faltan": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          }
        },
        "no_juzgaron": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "required": [
              "id",
              "motivo"
            ],
            "properties": {
              "id": {
                "type": "string"
              },
              "motivo": {
                "type": "string"
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
  },
  {
    "name": "oracle_tareas",
    "title": "Consultar el tracker de tareas del proyecto",
    "description": "Lee tareas/: listar sin cuerpos; ver por id o sufijo/prefijo con cuerpo completo; buscar texto o extraer hechos. Sin tracker: TRACKER_AUSENTE.",
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
        "accion"
      ],
      "properties": {
        "accion": {
          "enum": [
            "listar",
            "ver",
            "buscar",
            "hechos"
          ],
          "description": "Acción de consulta a ejecutar en el tracker."
        },
        "estado": {
          "enum": [
            "ABIERTA",
            "CERRADA"
          ],
          "description": "Filtro de estado para la acción listar."
        },
        "etiqueta": {
          "type": "string",
          "description": "Filtro por etiqueta exacta para la acción listar."
        },
        "id": {
          "type": "string",
          "description": "Identificador canónico o prefijo inequívoco de la tarea para la acción ver."
        },
        "texto": {
          "type": "string",
          "description": "Texto literal a buscar en tareas y notas para la acción buscar."
        },
        "git": {
          "type": "boolean",
          "default": false,
          "description": "Si es true, incluye diagnóstico de Git al extraer hechos."
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
        "accion",
        "resultado"
      ],
      "properties": {
        "esquema": {
          "const": "oracle.mcp/tareas/v1"
        },
        "oracle_version": {
          "type": "string"
        },
        "proyecto": {
          "type": "string"
        },
        "accion": {
          "enum": [
            "listar",
            "ver",
            "buscar",
            "hechos"
          ]
        },
        "resultado": {
          "type": [
            "array",
            "object"
          ],
          "description": "Resultado de la acción: lista de tareas sin cuerpo para listar, objeto de tarea con cuerpo completo para ver, objeto con coincidencias y omitidos para buscar, u objeto de hechos relacionales para hechos."
        }
      }
    }
  }
]
```
<!-- herramientas-json:fin -->

### `oracle_catalogo_efectivo`

Sin `ids`, devuelve una fila compacta por cada medida del `Catalogo` producido por
`catalogo_efectivo`: id, origen lógico y estado de fijación. `total` es el
tamaño del catálogo efectivo entero, no el largo de la selección devuelta. Con `ids`, conserva ese
`total`, pone `detalle: true` y agrega a cada fila `relaciones`, `ambito`, `requiere`, umbral
completo, alcance, archivo fuente y huella del archivo. `origen` se codifica sin estructura
repetida: `catalogo_base:oracle`, `perfil:<id>`, `biblioteca:<id>` o `proyecto`.
Una lista `ids` vacía se rechaza en vez de crear un tercer modo implícito. Las medidas siempre se
ordenan por id, incluso si el pedido llegó en otro orden. `fuente` usa `presentar_ruta`: relativa al
proyecto cuando pertenece a él y absoluta cuando vive en una distribución instalada.

Pedir detalle de un id que está instalado pero queda afuera por `ambito` no debe responder «no
existe». Debe rechazarlo así:

> `MEDIDA_NO_EFECTIVA — «perfil.regla» existe en una fuente seleccionada pero su ambito
> «del_origen» no obliga a «/ruta/proyecto».`

Si el id no aparece en ninguna fuente seleccionada, el mensaje cambia la afirmación:

> `MEDIDA_DESCONOCIDA — «perfil.regla» no aparece en las fuentes seleccionadas por este
> proyecto. Consultá oracle_catalogo_efectivo sin ids para ver los efectivos.`

La distinción importa para un agente: «no existe» lo invita a crear un duplicado; «no tiene
jurisdicción acá» le enseña que el archivo ya tiene dueño y alcance.

`fijacion` tampoco se infiere contando casos en el adaptador. Sale de
`ejercicio_del_catalogo`, que deja juzgar a `meta.toda_medida_esta_ejercitada`. Sus cuatro valores
significan:

- `evidencia`: el corpus o un diferencial la ejercita;
- `arnes`: la evalúa un arnés sobre relaciones del lenguaje;
- `heredada`: responde el corpus de quien publicó la política, no este consumidor;
- `sin_fijar`: la medida jueza la encontró sin ejercicio.

Si no aparece la medida jueza o no se puede reunir toda la evidencia que ella sabe mirar, la
consulta falla con `EVIDENCIA_INCOMPLETA`; no inventa un quinto estado ni entrega una mezcla de
fijaciones comprobadas y desconocidas.

La capacidad nueva no es «listar medidas en JSON». Es exponer, con procedencia conservada, la
selección de jurisdicción que hoy sólo existe como función de núcleo. `oracle medida listar` y
`oracle contexto` cargan fuentes; no contestan esa selección.

### `oracle_evaluar`

`medida` es una unión cerrada. `{"id": ...}` sólo admite una medida del catálogo efectivo;
`{"texto": ..., "formato": "oracle"|"json"}` carga una medida enteramente en memoria. No se
admite `archivo`: aceptar una ruta haría de esta herramienta otra ortografía de `oracle medida
probar` y abriría lecturas fuera de la raíz.

`evidencia` usa la representación JSON ya consumida por `Medida.evaluar`: cada clave es una relación
y cada valor, una lista de filas objeto. El servidor pasa el resultado de `Veredicto.a_dict` a una
única función de presentación; no vuelve a decidir el umbral en el adaptador.

La respuesta tiene tres estados, no un booleano:

- `verde` cuando `ok` es verdadero;
- `rojo` cuando `ok` es falso y `sin_evidencia` está vacío;
- `sin_evidencia` cuando falta una relación declarada en `requiere`.

Una traducción que trate `sin_evidencia` como rojo sería plausible y falsa: rojo afirma algo del
mundo; sin evidencia afirma que no se pudo mirar. El esquema evita el booleano tentador y el corpus
del servidor debe fijar las tres ramas.

El resultado gana la clave obligatoria `sombra` (esquema `oracle.mcp/evaluacion/v2`): `null` si la
medida no está en sombra en el `oracle.json` del proyecto o si fue evaluada en memoria (`formato`);
si está en sombra, `{"desde": str, "porque": str, "cota": int | null, "perdona": bool}`.
`perdona` es verdadero sólo si la medida dio rojo y la sombra lo perdona: sin cota, siempre; con
cota, sólo si el valor es un número y no la supera (la misma regla que `Informe.supera_su_cota` en
`nucleo/medida.py`). `estado` no cambia (`verde`, `rojo` o `sin_evidencia`): la sombra no altera la
medición sino su consecuencia.

Se devuelven a lo sumo cinco testigos, el mismo corte que ya usa `tools/medida.py::probar`, y
`testigos_omitidos` dice cuántos quedaron afuera. Una respuesta sin testigos nunca se interpreta
como ausencia de evidencia: esa afirmación vive exclusivamente en `estado`. Si falta una relación
que la medida consume pero no declara en `requiere`, la evaluación conserva la semántica actual del
álgebra y agrega una advertencia; no inventa una precondición.

`alcance_derivado` se calcula sólo después de cargar correctamente las relaciones declaradas. Si el
proyecto no declara ninguna, vuelve vacío y `advertencias` lo dice. Si las declaraciones existen
pero son inválidas, la herramienta falla; no hereda el `except Exception: return []` de la vista
actual ni hace pasar «no pude derivar» por «no hay puntos ciegos derivados».

La capacidad nueva es que tanto la medida como la evidencia pueden llegar por valor y que el
resultado es estructurado. El CLI exige que la medida ya exista como archivo y devuelve texto. Esto
permite explorar sin ensuciar el árbol y sin parsear una salida pensada para personas.

### `oracle_desafiar`

Esta herramienta acepta la misma unión de medida. Si `usar_evidencia_del_proyecto` se omite, vale
verdadero: reúne los casos del corpus y los diferenciales cuyo `medida` coincide con el id del
candidato. Los `casos` de la llamada se agregan en memoria y se marcan como efímeros. No aceptan
`procedencia`, porque una llamada no puede convertir evidencia fabricada en evidencia observada.
Ids repetidos entre ambas fuentes se rechazan con `CASO_REPETIDO`; nunca gana el último en silencio.

El orden es parte del contrato:

1. carga y normaliza la medida;
2. reúne casos y conserva su origen;
3. evalúa el original contra cada expectativa;
4. si alguna no se reproduce, devuelve `original_no_reproduce` y no muta;
5. si no hay al menos un caso que espere verde y otro que espere rojo medido o
   `sin_evidencia`, devuelve
   `faltan_polaridades` y no muta;
6. genera los mutantes de la forma canónica y los ejecuta contra todos los casos;
7. separa cambio conductual, rechazo del álgebra y supervivencia.

`discordancias` es vacío cuando el original reproduce todo. Una excepción durante un caso se
registra como `obtenido: "error"`; no se transforma en rojo. `mutacion.generados` es el denominador
antes de correr casos. `detectados_por_conducta` cuenta mutantes para los que algún caso invirtió el
veredicto, cambió el valor o cambió testigos. Un mutante que sólo levantó una excepción va en
`rechazado_por_el_algebra`: no se publica como capacidad conductual del corpus.

La conclusión más fuerte se llama `todos_detectados_por_conducta`, no `correcta`, `aprobada` ni
`lista_para_guardar`. Incluso esa conclusión significa solamente «estos mutadores, escritos por
estos autores, fueron discriminados por estas evidencias». Si no sobrevivió ninguno pero hubo
rechazos, la conclusión separada `sin_sobrevivientes_con_rechazos` impide inflar el resultado.

La capacidad nueva es ejecutar el lazo candidato efímero → dos polaridades → mutación sin que la
medida ni los casos existan en disco. Ni `oracle medida revisar`, ni `oracle medida probar`, ni
`oracle caso generar` hacen esa composición en memoria.

### `oracle_juzgar`

Lo mismo que `oracle juzgar --con`, sobre una evidencia JSON pasada por valor.

Acepta `{"evidencia": {...}, "ids": [...]}` donde `ids` es opcional y no admite duplicados. Falla
con `ARGUMENTOS_INVALIDOS` si faltan argumentos obligatorios o si `ids` contiene nombres malformados
o repetidos.

Aplica el catálogo **efectivo** del proyecto fijado al arranque, respetando el ámbito de cada
medida y las sombras y cotas declaradas en `oracle.json`. Cuando `ids` se omite, evalúa todas las
medidas aplicables y adjunta `no_aplicadas` con las medidas del catálogo propio cuyas relaciones
faltaron en la evidencia. Si ninguna medida aplica, devuelve `ok: false` con una advertencia
explicativa; nunca devuelve un verde vacío.

Si se indica `ids` y alguna de las medidas pedidas no existe en el catálogo o no aplica a la
evidencia provista, la herramienta falla cerrado con error de dominio (`MEDIDA_DESCONOCIDA`,
`MEDIDA_NO_EFECTIVA` o `MEDIDA_NO_APLICABLE`), de modo análogo a `oracle_evaluar`.

La salida (esquema `oracle.mcp/juzgar/v1`) incluye: `esquema`, `oracle_version`, `proyecto`,
`entrada_sha256`, `ok`, `medidas` (con `estado`, `valor`, `umbral`, `sombra`, `testigos`,
`testigos_omitidos` y `alcance`), `no_aplicadas`, `no_juzgaron` y `advertencias`. Conserva la misma
protección de concurrencia que `oracle_evaluar` (`_evaluacion_estable`): si el proyecto cambia
durante el juicio, rechaza con `PROYECTO_CAMBIO_DURANTE_LA_CONSULTA`.

### `oracle_tareas`

Permite que un agente sin acceso a shell consulte el tracker de tareas (`tareas/`) del proyecto.

Es estrictamente de **sólo lectura** (`readOnlyHint: true`, `destructiveHint: false`,
`idempotentHint: true`, `openWorldHint: false`). No expone acciones de escritura (`nueva`,
`anotar`, `cerrar`, `etiquetar`): una tarea creada o cerrada sin su commit correspondiente deja el
tracker en rojo, y el commit no se realiza por MCP.

Acepta cuatro acciones mediante el parámetro obligatorio `accion`:

- `listar`: enumera tareas sin `cuerpo`, conservando todos sus metadatos. Admite filtro opcional por `estado` (`"ABIERTA"` o `"CERRADA"`, por
  omisión abiertas) y por `etiqueta`.
- `ver`: requiere `id` (identificador canónico o prefijo inequívoco). Devuelve el detalle de la
  tarea con su `cuerpo` completo (incluidas las notas) o falla con `TAREA_NO_ENCONTRADA` o `ID_AMBIGUO`.
- `buscar`: requiere `texto`. Busca de forma literal e insensible a mayúsculas en tareas y notas
  del tracker, devolviendo `coincidencias` y `omitidos`.
- `hechos`: extrae los hechos relacionales del tracker (esquema de evidencia relacional para `oracle
  juzgar`), con soporte opcional de inspección de Git (`git: true`).

Si el proyecto no tiene directorio `tareas/`, la herramienta falla con `TRACKER_AUSENTE`, nunca con
una lista o resultado vacío. Si el tracker contiene registros inválidos o symlinks no permitidos,
falla con `TRACKER_INVALIDO`.

La salida (esquema `oracle.mcp/tareas/v1`) incluye `esquema`, `oracle_version`, `proyecto`, `accion`
y `resultado` (con la información del `--json` del verbo CLI equivalente, salvo `listar`,
que omite `cuerpo`; `ver` conserva el contenido completo).

## Rechazos y forma de los errores

Hay que separar errores del protocolo y errores de ejecución de una herramienta. JSON ilegible usa
`-32700`; un pedido que no es JSON-RPC válido usa `-32600`; un método MCP desconocido usa `-32601`;
una herramienta desconocida o un sobre `tools/call` mal formado usa `-32602`. Son respuestas
JSON-RPC con `error`, porque el despachador no pudo iniciar una herramienta. Los mensajes son,
respectivamente, `JSON inválido: <detalle>`, `pedido JSON-RPC inválido: <detalle>`, `método no
soportado: <metodo>` y `tools/call inválido: <detalle>`; para un nombre desconocido, el último
detalle es `herramienta desconocida: <nombre>`.

Todo error que el agente puede corregir dentro de una herramienta vuelve como resultado MCP con
`isError: true` y un único bloque de texto. Su primera línea tiene forma estable
`CODIGO — mensaje`; las siguientes dicen el campo y la corrección. No lleva `structuredContent`,
porque los esquemas publicados describen respuestas exitosas y una respuesta de error no debe
fingir que los cumple.

Los códigos de dominio cerrados son:

| Código | Qué rechaza | Plantilla exacta del mensaje |
|---|---|---|
| `ARGUMENTOS_INVALIDOS` | propiedades de más, unión con dos fuentes de medida, tipos o ids inválidos | `ARGUMENTOS_INVALIDOS — <ruta JSON>: <valor recibido>; se esperaba <forma>.` |
| `PROYECTO_INVALIDO` | estructura, configuración, confinamiento o symlink inválido | `PROYECTO_INVALIDO — <raíz>: <motivo de nucleo.proyecto>.` |
| `CATALOGO_INVALIDO` | una fuente seleccionada no carga, hay ids duplicados o versiones incompatibles | `CATALOGO_INVALIDO — <fuente>: <motivo de carga>. No se devolvió un catálogo parcial.` |
| `MEDIDA_DESCONOCIDA` | el id no aparece en fuentes seleccionadas | `MEDIDA_DESCONOCIDA — «<id>» no aparece en las fuentes seleccionadas; consultá oracle_catalogo_efectivo sin ids.` |
| `MEDIDA_NO_EFECTIVA` | el id existe pero su ámbito no obliga aquí | `MEDIDA_NO_EFECTIVA — «<id>» existe en <origen>, pero su ambito «<ambito>» no obliga a «<proyecto>».` |
| `MEDIDA_NO_APLICABLE` | el id pedido en `oracle_juzgar` no aplica a las relaciones de la evidencia | `MEDIDA_NO_APLICABLE — «<id>» requiere las relaciones <relaciones>, no presentes en la evidencia.` |
| `MEDIDA_INVALIDA` | el texto no parsea o no satisface `Medida.de_datos` | `MEDIDA_INVALIDA — <id o texto>: <motivo> en <línea y columna o ruta canónica>.` |
| `EVIDENCIA_INVALIDA` | una relación no es una lista de objetos o una fila no es evaluable | `EVIDENCIA_INVALIDA — $.evidencia.<relación>[<índice>]: <motivo>.` |
| `EVIDENCIA_INCOMPLETA` | falta la medida jueza, un fixture está vencido o no se pudo reunir todo lo que exige un juicio de fijación | `EVIDENCIA_INCOMPLETA — no se pudo juzgar la fijación: <motivo>. No se devolvieron fijaciones parciales.` |
| `CASO_REPETIDO` | dos casos tienen el mismo id | `CASO_REPETIDO — «<id>» aparece en <origen 1> y <origen 2>; ninguno tiene precedencia.` |
| `ESCALARES_NO_AUTORIZADAS` | haría falta ejecutar `escalares.py` no confiado | `ESCALARES_NO_AUTORIZADAS — <archivo> es código externo; autorizalo en la configuración de arranque del servidor, no en esta llamada.` |
| `TRACKER_AUSENTE` | el proyecto no tiene directorio `tareas/` | `TRACKER_AUSENTE — el proyecto no tiene tracker de tareas: falta <ruta tareas>.` |
| `TRACKER_INVALIDO` | el directorio `tareas/` contiene registros inválidos, documentos centrales corruptos o enlaces simbólicos | `TRACKER_INVALIDO — se detectaron <N> registro(s) inválido(s) en <ruta tareas>:` |
| `TAREA_NO_ENCONTRADA` | el id o prefijo pedido en `oracle_tareas ver` no existe | `TAREA_NO_ENCONTRADA — no se encontró ninguna tarea con prefijo «<id>».` |
| `ID_AMBIGUO` | el prefijo pedido en `oracle_tareas ver` coincide con más de una tarea | `ID_AMBIGUO — el prefijo «<prefijo>» coincide con <N> tareas: <ids>.` |
| `LIMITE_DE_ALGEBRA` | se excede un presupuesto de `LimitesAlgebra` | `LIMITE_DE_ALGEBRA — <nombre>: se observó <valor> y el límite activo es <límite>.` |
| `PROYECTO_CAMBIO_DURANTE_LA_CONSULTA` | el conjunto o contenido de entradas cambió durante la operación | `PROYECTO_CAMBIO_DURANTE_LA_CONSULTA — huella inicial <sha> y final <sha>; reintentá sobre un estado estable.` |
| `EVALUACION_FALLO` | excepción no clasificable de una medida o escalar | `EVALUACION_FALLO — <tipo de excepción>: <mensaje>. No se produjo un veredicto.` |

Una consulta vacía no es un error si el proyecto es válido: un catálogo efectivo de cero medidas
responde `total: 0`. En cambio, una excepción al cargar nunca se convierte en cero. Esta regla elimina
el patrón `except Exception: return []` de `tools/contexto.py`: para una interfaz que alimenta a un
agente, «no pude mirar» y «miré y no hay» deben viajar por canales distintos.

Los presupuestos de evaluación no se inventan en MCP. Son los ya definidos por
`LimitesAlgebra`: filas por relación, producto cartesiano, profundidad de expresión y expansiones de
macros. El adaptador no ofrece argumentos para aumentarlos. El límite de presentación de cinco
testigos también precede a MCP. Para cancelación, el lector de stdio sigue atendiendo mensajes
mientras el trabajo corre en un trabajador; al recibir `notifications/cancelled` marca el trabajo,
deja de emitir su respuesta y corta entre casos o mutantes. Nunca imprime una respuesta tardía para
un id cancelado.

## Por qué no se exponen los verbos del CLI

El comentario de la propuesta previa habla de 22 verbos, pero la fuente actual no contiene ese
número. `VERBOS` declara 17 verbos canónicos de dominio y ocho temas bajo `manual`, 25 entradas si
se cuentan esos temas como verbos. Los alias `--verbo` y `caso nueva` tampoco son capacidades. Esta
es la medición reproducible:

```text
$ python - <<'PY'
from tools.cli import VERBOS
for k, v in VERBOS.items(): print(k, len(v), ', '.join(v))
print('total_canónicos=', sum(map(len, VERBOS.values())))
print('sin_temas_manual=', sum(len(v) for k,v in VERBOS.items() if k != 'manual'))
PY
medida 5 nueva, revisar, probar, listar, expandir
caso 3 nuevo, listar, generar
proyecto 5 init, test, relaciones, escalares, contexto
biblioteca 4 nueva, instaladas, verificar, listar
manual 8 operadores, segun, etiqueta, procedencia, como_se_detecto, relaciones, verbos, medidas
total_canónicos= 25
sin_temas_manual= 17
```

La exclusión se decide por capacidad, no por cantidad:

| Superficie del CLI | Por qué no es una herramienta MCP |
|---|---|
| `medida nueva`, `caso nuevo`, `proyecto init`, `biblioteca nueva` | Crean plantillas o árboles. El agente ya sabe editar archivos y el MCP no sabe más que él al hacerlo. |
| `medida revisar`, `medida probar` | Sus partes nuevas quedan subsumidas por entrada enteramente en memoria y salida estructurada de `oracle_evaluar` y `oracle_desafiar`; envolver el archivo y el texto de consola no alcanza. |
| `medida listar` | Lista fuentes cargadas, no el catálogo efectivo por ámbito. La herramienta se justifica sólo por corregir esa pregunta mediante `catalogo_efectivo`. |
| `medida expandir`, `convertir` | Son transformaciones de representación que el CLI ya hace de modo determinista. No agregan observación ni falsación. |
| `caso listar` | Es un listado de archivos ya accesibles. El desafío usa esos casos sin obligar al agente a parsear la vista. |
| `caso generar` | Propone evidencia a partir de sobrevivientes y puede escribirla; `oracle_desafiar` devuelve el sobreviviente crudo. Inventar el caso sigue requiriendo juicio, no otra envoltura. |
| `proyecto test` | Es una orquestación larga disponible por consola. Ocultarla detrás de una llamada síncrona empeora progreso, cancelación y alcance sin crear una comprobación nueva. |
| `proyecto relaciones`, `proyecto escalares`, `proyecto contexto` | Ya son vistas compactas y el agente puede pedirlas por CLI. MCP no las vuelve nuevas por serializarlas. Las relaciones consumidas que hacen falta para entender jurisdicción sí viajan en el índice efectivo. |
| `biblioteca instaladas`, `biblioteca verificar`, `biblioteca listar` | Son administración e inspección del entorno de paquetes, no una pregunta sobre la medición actual. Además aceptar una ruta de biblioteca ampliaría la autoridad fijada al arrancar. |
| `manual` y sus ocho temas | Son referencia derivada y estable. Meterla como herramienta cobraría descripciones en cada turno para devolver texto que ya se puede leer sin ejecución. |
| `diagnostico`, ayuda y versión | Son soporte de la instalación. La versión necesaria ya acompaña cada resultado; el resto no participa de decidir ni medir. |
| `tarea nueva`, `tarea anotar`, `tarea cerrar`, `tarea etiquetar`, `tarea adjuntar` | Son operaciones de escritura del tracker. Modificar o cerrar una tarea sin su commit correspondiente deja el tracker en rojo, y el commit pertenece al control de versiones fuera de MCP. La consulta de sólo lectura se expone en `oracle_tareas`. |

No se expone `oracle_proponer`. Su ausencia es deliberada, no una fase pendiente de esta superficie.
Si en otra versión se quisiera escritura, tendría que responder una capacidad nueva propia —por
ejemplo, una transacción revisable que no pueda sobrescribir— y no entrar por simetría con el CLI.

## Transporte

`tools/lsp.py` es el precedente correcto en cuatro decisiones: JSON-RPC escrito con la biblioteca
estándar, un despachador explícito, respuestas compactas y stdout reservado al protocolo. No se debe
copiar su enmarcado. LSP usa cabeceras `Content-Length`; el transporte stdio de MCP 2026-07-28 usa un
objeto JSON-RPC UTF-8 por línea, sin saltos de línea literales. `json.dumps` escapa los saltos dentro
de cadenas y cada escritura termina con un solo `\n`. Logs, trazas y excepciones van a stderr; una
sola línea humana en stdout corrompe el canal.

El servidor no necesita un SDK MCP ni un validador JSON Schema en producción. `json`, `sys`,
`hashlib` y los mecanismos de concurrencia de la biblioteca estándar alcanzan para el transporte;
los argumentos se validan con funciones explícitas contra estos tres esquemas cerrados. Un
validador independiente sí conviene en los tests para comprobar que esas funciones y los esquemas
publicados no divergieron. El `jsonschema` del comando de medición de este documento se instala en
un entorno aislado y no se propone como dependencia del paquete.

El servidor debe ser de dos eras porque en la fecha de este diseño conviven clientes anteriores y
posteriores al cambio de ciclo de vida:

- para MCP 2026-07-28 implementa `server/discover`, valida en cada pedido los metadatos de versión
  y capacidades, y no conserva una sesión implícita;
- para MCP 2025-11-25 implementa `initialize`, `notifications/initialized`, `ping`, `shutdown` y
  `exit` con el estado de sesión correspondiente;
- en ambas eras implementa `tools/list`, `tools/call` y `notifications/cancelled`, con la misma
  superficie y semántica de Oracle.

No anuncia recursos, prompts, muestreo, raíces ni cambios dinámicos de herramientas. El resultado de
`tools/list` es siempre el arreglo anterior, en ese orden, por lo que se puede cachear y favorece la
caché del prompt. En respuestas exitosas, `structuredContent` contiene el objeto que satisface
`outputSchema` y `content` contiene su serialización JSON compacta para clientes que no consumen
contenido estructurado. `isError` es falso. Esta duplicación en el cable se mide abajo: el anfitrión
debería entregar al modelo una sola de las dos representaciones, no ambas.

En la era moderna, todo resultado completo —incluidos los errores de ejecución— agrega
`resultType: "complete"`; `tools/list` también lo agrega. En la era heredada se usa la forma de
2025-11-25, que no tiene ese campo. El objeto de dominio dentro de `structuredContent` es idéntico:
la compatibilidad del transporte no crea dos contratos de Oracle.

El servidor atiende llamadas concurrentes sin estado semántico compartido: cada una reconstruye su
lectura desde la raíz fijada. Los registros temporales de macros y escalares viven dentro del trabajo
y se restauran aun ante error o cancelación. No hay handles, caché cuya invalidez cambie una respuesta
ni una llamada que dependa de haber invocado otra antes.

Fuentes normativas del transporte consultadas para este diseño:

- [MCP 2026-07-28: stdio](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio),
  que fija la delimitación por nueva línea y el uso exclusivo de stdout;
- [MCP 2026-07-28: herramientas](https://modelcontextprotocol.io/specification/2026-07-28/server/tools),
  que fija esquemas de entrada/salida, contenido estructurado y anotaciones;
- [MCP 2026-07-28: versiones y compatibilidad](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning),
  que distingue pedidos modernos con metadatos de la inicialización heredada.

## Costo de contexto

Hay dos costos diferentes. `tools/list` se paga al exponer la superficie, aunque no se llame nada;
una respuesta se paga sólo cuando el agente usa una herramienta. Para no confundir palabras con
tokens, todas las cifras siguientes usan `o200k_base` y el contenido UTF-8 exacto. No se afirma que
todo anfitrión use ese tokenizador.

La vista existente da una referencia medida del problema que se quiere mejorar:

```text
$ uv run --isolated --with tiktoken python - <<'PY'
import tiktoken
from pathlib import Path
from nucleo.proyecto import Proyecto
from tools.contexto import texto
enc=tiktoken.get_encoding('o200k_base')
p=Proyecto(Path.cwd())
for compacto in (False, True):
    s=texto(p, compacto=compacto)
    print(('normal' if not compacto else 'compacto'), len(enc.encode(s)), 'tokens o200k_base')
PY
normal 5605 tokens o200k_base
compacto 2104 tokens o200k_base
```

La superficie normativa cuesta 200 tokens en sus tres descripciones solas y 1.940 con nombres,
anotaciones y esquemas completos. Esto último es el costo relevante si el anfitrión inyecta la
definición entera, y explica por qué agregar herramientas «por comodidad» no es gratis.

Para las respuestas se usó el proyecto Oracle de esta fecha, no objetos inventados: el índice de
sus 57 medidas efectivas; el detalle de `meta.agrupar_no_agranda_la_relacion`; su caso rojo
`051-agrupar-invento-un-grupo`; y su desafío con ese caso y el verde
`052-agrupar-colapsa-como-debe`. El script arma los objetos según los esquemas anteriores, los
valida con JSON Schema 2020-12 y mide tanto el objeto de dominio como el resultado moderno que lo
duplica en `content` y `structuredContent`:

```text
$ uv run --isolated --with tiktoken --with jsonschema python - <<'PY'
import hashlib,json,re,tiktoken
from pathlib import Path
import catalogos
from jsonschema import Draft202012Validator
from nucleo.caso import cargar_casos
from nucleo.medida import relaciones_de_medida
from nucleo.mutacion import correr
from nucleo.proyecto import Proyecto,catalogo_efectivo,macros_del_proyecto
from nucleo.version import VERSION_DISTRIBUCION
from tools.medida import alcance_derivado,ejercicio_del_catalogo
H=lambda x:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
E=lambda v:'sin_evidencia' if v.sin_evidencia else ('verde' if v.ok else 'rojo')
doc=Path('docs/mcp-contrato.md').read_text(); defs=json.loads(re.search(r'<!-- herramientas-json:inicio -->\n```json\n(.*?)\n```\n<!-- herramientas-json:fin -->',doc,re.S).group(1))
p=Proyecto(Path.cwd()); cat=catalogo_efectivo(p); ej=ejercicio_del_catalogo(p,cat,macros_del_proyecto(p)); assert ej.hubo_jueza and ej.completa; hp=hashlib.sha256()
archivos={x.ruta.resolve() for x in cat.entradas.values()}|{x.resolve() for d in ('corpus','diferencial','macros') for x in (p.raiz/d).rglob('*') if x.is_file()}|({(p.raiz/'oracle.json').resolve()} if (p.raiz/'oracle.json').is_file() else set())
for ruta in sorted(archivos): hp.update(str(ruta).encode()+b'\0'+ruta.read_bytes()+b'\0')
ms=[]
for mid in sorted(cat):
 x=cat.entradas[mid]; o='proyecto' if x.origen.clase=='proyecto' else f'{x.origen.clase}:{x.origen.identificador}'
 f=('heredada' if mid in ej.heredadas else 'evidencia' if ej.casos_por_medida.get(mid,0) else 'arnes' if mid in ej.aparte else 'sin_fijar')
 assert f!='sin_fijar' or mid in ej.sin_ejercitar
 ms.append({'id':mid,'origen':o,'fijacion':f})
base={'esquema':'oracle.mcp/catalogo-efectivo/v1','oracle_version':VERSION_DISTRIBUCION,'proyecto':str(p.raiz.resolve()),'huella_proyecto':hp.hexdigest(),'total':len(cat)}
rc={**base,'detalle':False,'medidas':ms}; elegido='meta.agrupar_no_agranda_la_relacion'; m=cat[elegido]; ent=cat.entradas[elegido]; mi=next(x for x in ms if x['id']==elegido)
rmd={**base,'detalle':True,'medidas':[{**mi,'relaciones':list(relaciones_de_medida(m)),'ambito':m.ambito,'requiere':list(m.requiere),'umbral':{'operador':m.op,'valor':m.limite,'segun':m.segun,'porque':m.porque},'alcance':m.alcance,'fuente':ent.ruta.relative_to(p.raiz).as_posix(),'fuente_sha256':hashlib.sha256(ent.ruta.read_bytes()).hexdigest()}]}
cs=[x for x in cargar_casos(p.corpus) if x['id'] in {'051-agrupar-invento-un-grupo','052-agrupar-colapsa-como-debe'}]; cr=next(x for x in cs if x['id']=='051-agrupar-invento-un-grupo'); v=m.evaluar(cr['evidencia'])
reval={'esquema':'oracle.mcp/evaluacion/v1','oracle_version':VERSION_DISTRIBUCION,'proyecto':str(p.raiz.resolve()),'entrada_sha256':H({'medida':m.a_datos(),'evidencia':cr['evidencia']}),'medida':m.id,'estado':E(v),'valor':v.valor,'umbral':{'operador':m.op,'valor':m.limite,'segun':m.segun,'porque':m.porque},'testigos':[dict(x) for x in v.testigos[:5]],'testigos_omitidos':max(0,len(v.testigos)-5),'alcance':m.alcance,'alcance_derivado':alcance_derivado(p,m),'advertencias':[]}
facts=correr({m.id:m},cs)['mutante']; no=[]; det=rej=0
for f in facts:
 if f['detecciones_conductuales']: det+=1
 elif f['rechazos_del_algebra']: rej+=1; no.append({'id':f['id'],'cambio':f['cambio'],'estado':'rechazado_por_el_algebra'})
 else: no.append({'id':f['id'],'cambio':f['cambio'],'estado':'sobrevivio'})
disc=[]
for c in cs:
 esp=c.get('espera') or ('verde' if c['etiqueta']=='verde_correcto' else 'rojo'); obt=E(m.evaluar(c['evidencia']))
 if esp!=obt: disc.append({'caso':c['id'],'esperado':esp,'obtenido':obt})
con=('original_no_reproduce' if disc else 'faltan_polaridades' if len({x['etiqueta']=='verde_correcto' for x in cs})<2 else 'sin_mutantes' if not facts else 'sobrevivientes' if any(x['estado']=='sobrevivio' for x in no) else 'sin_sobrevivientes_con_rechazos' if rej else 'todos_detectados_por_conducta')
rd={'esquema':'oracle.mcp/desafio/v1','oracle_version':VERSION_DISTRIBUCION,'proyecto':str(p.raiz.resolve()),'entrada_sha256':H({'medida':m.a_datos(),'casos':cs}),'medida':m.id,'conclusion':con,'casos':{'total':len(cs),'del_proyecto':len(cs),'efimeros':0,'esperan_verde':sum(x['etiqueta']=='verde_correcto' for x in cs),'esperan_rojo':sum(x['etiqueta']!='verde_correcto' for x in cs)},'discordancias':disc,'mutacion':{'generados':len(facts),'detectados_por_conducta':det,'rechazados_por_el_algebra':rej,'no_detectados':no},'advertencias':['La mutación no demuestra corrección semántica.']}
enc=tiktoken.get_encoding('o200k_base'); dumps=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':')); tok=lambda x:len(enc.encode(dumps(x)))
print('descripciones=',len(enc.encode('\n'.join(x['description'] for x in defs))),'tokens o200k_base'); print('definiciones_tools_list=',tok(defs),'tokens o200k_base')
for name,payload,schema in [('catalogo_indice',rc,defs[0]['outputSchema']),('catalogo_detalle_un_id',rmd,defs[0]['outputSchema']),('evaluacion_roja',reval,defs[1]['outputSchema']),('desafio_dos_polaridades',rd,defs[2]['outputSchema'])]:
 Draft202012Validator(schema).validate(payload); result={'resultType':'complete','content':[{'type':'text','text':dumps(payload)}],'structuredContent':payload,'isError':False}
 print(name,'campos_validos=si','payload=',tok(payload),'tokens','resultado_moderno_duplicado=',tok(result),'tokens','bytes=',len(dumps(payload).encode()))
print('catalogo_total=',rc['total'],'detalle_id=',elegido,'caso_evaluado=',cr['id'],'estado=',reval['estado'],'desafio_conclusion=',rd['conclusion'],'mutantes=',len(facts))
PY
Installed 1 package in 2ms
descripciones= 200 tokens o200k_base
definiciones_tools_list= 1940 tokens o200k_base
catalogo_indice campos_validos=si payload= 1897 tokens resultado_moderno_duplicado= 3933 tokens bytes= 6062
catalogo_detalle_un_id campos_validos=si payload= 369 tokens resultado_moderno_duplicado= 769 tokens bytes= 1237
evaluacion_roja campos_validos=si payload= 331 tokens resultado_moderno_duplicado= 692 tokens bytes= 1151
desafio_dos_polaridades campos_validos=si payload= 481 tokens resultado_moderno_duplicado= 998 tokens bytes= 1266
catalogo_total= 57 detalle_id= meta.agrupar_no_agranda_la_relacion caso_evaluado= 051-agrupar-invento-un-grupo estado= rojo desafio_conclusion= sin_sobrevivientes_con_rechazos mutantes= 16
```

La respuesta típica barata queda entre 331 y 481 tokens de contenido estructurado en estos casos.
El índice completo cuesta 1.897 porque enumera las 57 medidas; el detalle selectivo de una vuelve a
369. El peor costo observado no lo causa Oracle sino la compatibilidad que duplica el mismo JSON:
si el anfitrión entrega ambas copias al modelo, casi duplica todos esos valores. Por eso el contrato
mantiene el índice compacto y exige que el anfitrión prefiera `structuredContent` cuando lo soporte.
Estas son mediciones de los casos nombrados, no cotas universales: más medidas, prosa más larga o
más sobrevivientes producen respuestas mayores.

## Una respuesta plausible y equivocada

Un `outputSchema` sólo detecta una mentira de forma: falta un campo, sobra otro o cambia un tipo. No
detecta una lista bien formada del catálogo equivocado. Tampoco lo hace una huella calculada por el
mismo servidor que produjo la respuesta. Por eso el contrato usa cuatro defensas distintas y no
presenta ninguna como suficiente:

1. **Una sola autoridad semántica por afirmación.** La jurisdicción sale de
   `catalogo_efectivo`; el estado puntual sale de `Veredicto`; el ejercicio sale de la medida meta;
   la mutación sale de `nucleo.mutacion.correr`. El adaptador proyecta datos, no reescribe reglas.
2. **Fallo cerrado.** Catálogo, corpus o diferenciales ilegibles producen `isError`; nunca una lista
   vacía, un verde o una ronda sin sobrevivientes.
3. **Datos que permiten reconciliar.** Se devuelve valor junto con umbral, testigos junto con su
   truncamiento, denominador de mutantes junto con sus tres destinos, origen junto con id y huellas
   junto con versión. Un consumidor mecánico puede rechazar cuentas que no cierran antes de que las
   lea el agente.
4. **Un oráculo externo al camino productivo.** Un corpus de conversaciones JSON-RPC completas fija
   los bytes y la semántica observada; la mutación del módulo demuestra que esos casos fallan cuando
   el adaptador altera una afirmación.

La cuarta es la que descubre una respuesta coherente pero incorrecta. Repetir la llamada sólo
detecta no determinismo; no detecta un error determinista. El agente en producción no puede
adivinarlo. Si una mutación que reemplaza `catalogo_efectivo` por `catalogos_a_cargar`, cambia
`sin_evidencia` por `rojo`, cuenta un rechazo del álgebra como detección conductual o traga una
excepción sigue dejando verde el corpus MCP, el servidor no está verificado.

Las respuestas tampoco deben usar lenguaje que exceda sus datos. `oracle_evaluar` dice lo que
ocurrió con una evidencia; `oracle_desafiar`, qué mutaciones discriminó un conjunto. Ninguna dice que
el mundo está bien, que la procedencia es observada o que el candidato debe guardarse. Reducir la
fuerza de la afirmación no arregla un cálculo equivocado, pero evita que un cálculo correcto se vuelva
una conclusión falsa al cruzar el transporte.

## Verificación del servidor

La prueba debe entrar por stdin y observar stdout, stderr, código de salida y sistema de archivos.
Llamar directamente a las funciones del adaptador no fija el contrato de transporte. El corpus
mínimo contiene conversaciones completas para:

- descubrimiento moderno y negociación de una versión no soportada;
- inicialización heredada, orden válido, apagado y salida;
- `tools/list` exacto, estable y conforme a sus propios esquemas;
- JSON truncado, mensaje no objeto, método desconocido, herramienta desconocida y argumentos con
  propiedad extra;
- proyecto efectivo construido con catálogo base, perfil, biblioteca y catálogo propio, incluyendo
  una medida `universal`, una `del_origen` ajena excluida y una `del_origen` propia incluida;
- detalle de id desconocido frente a id existente pero no efectivo;
- evaluación verde, roja y sin evidencia, con testigos por debajo y por encima del corte de
  presentación;
- candidato en texto que no toca disco y forma canónica equivalente que devuelve la misma
  evaluación;
- original que no reproduce un caso, corpus de una sola polaridad, mutante sobreviviente, mutante
  detectado por conducta y mutante rechazado por el álgebra;
- catálogo roto, diferencial vencido, escalar no autorizada y cambio concurrente de una entrada;
- cancelación durante una ronda y ausencia posterior de respuesta para ese id;
- stdout compuesto exclusivamente por objetos JSON-RPC de una línea y proyecto byte a byte
  idéntico antes y después de cada herramienta.

No basta cobertura de ramas. La ronda de mutación del módulo MCP tiene que matar, al menos, cambios
de despacho, nombre de campo, esquema, estado, origen, selector de catálogo, clasificación de
mutantes, canal stdout/stderr y supresión de errores. Los tests específicos del protocolo deben ir
primero al mutar ese objetivo: son los que pueden matar barato y con un diagnóstico que nombre el
contrato roto.

### La afirmación que custodia y nadie más comprueba

El futuro módulo MCP sólo merece entrar en `HERRAMIENTAS_CUSTODIAS` si custodia esta afirmación:

> **Todo `tools/call` aceptado proyecta por stdout, sin ampliar la raíz ni escribirla, exactamente
> la distinción semántica que devolvió el núcleo: catálogo cargado frente a efectivo, verde frente a
> rojo frente a sin evidencia, y mutante detectado frente a rechazado frente a sobreviviente.**

`nucleo/proyecto.py`, `nucleo/medida.py` y `nucleo/mutacion.py` comprueban cada distinción antes del
transporte. `tools/lsp.py` comprueba otro protocolo. Ninguno comprueba que el adaptador MCP preserve
esas distinciones en los bytes que recibe un agente ni que una llamada declarada de lectura deje el
árbol intacto. Ésa es la custodia propia. Si los tests del servidor sólo vuelven a probar el núcleo,
el archivo no entra en la lista aunque tenga cobertura alta.

## Condiciones de aceptación del diseño

El servidor está listo para implementarse cuando pueda demostrarse, con el corpus anterior, que:

- publica exactamente tres herramientas y las tres justifican una capacidad que el CLI no tiene;
- una llamada no puede elegir otra raíz, autorizar código externo ni persistir un borrador;
- el índice usa `catalogo_efectivo` y conserva el origen lógico de cada entrada;
- ninguna falla de carga se disfraza de vacío, verde o mutación concluyente;
- la evaluación conserva los tres estados y el desafío conserva las tres clases de mutante;
- cada respuesta exitosa satisface su `outputSchema` y cada error corregible llega al agente como
  `isError: true` con un mensaje accionable;
- el mismo contrato funciona en las dos eras declaradas, con una línea JSON-RPC por mensaje;
- el proyecto queda idéntico antes y después de todas las conversaciones;
- la mutación del módulo no deja sobrevivir cambios a la afirmación que custodia.

Hasta que esas condiciones tengan corpus y resultado de mutación, «MCP» describe un transporte
posible, no una herramienta confiable para un agente.
