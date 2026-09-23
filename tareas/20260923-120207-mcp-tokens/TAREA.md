# El MCP gasta tokens que el agente paga antes de hacer nada

- ESTADO: CERRADA
- PRIORIDAD: 76
- ETIQUETAS: oracle, mcp, tokens


## Lo medido (2026-09-23, sobre el propio repositorio)

- `tools/list`: **12.385 bytes, ~3.100 tokens**. Lo paga cada agente al conectarse, en cada sesión,
  antes de la primera pregunta. Son las descripciones y los esquemas de entrada y salida de las cinco
  herramientas.
- `oracle_catalogo_efectivo` sin argumentos (el índice «compacto»): **14.033 bytes, ~3.500 tokens**.
- `tools/mcp.py` es el archivo más grande del proyecto: **85 KB**, más que `nucleo/sintaxis.py`.

Brian (2026-09-23): «investigar cómo mejorar el MCP y bajar tokens».

## Qué hacer

1. **Medir antes de tocar**: tokens de `tools/list` y de una respuesta típica de cada herramienta
   (con un tokenizador real si está disponible; si no, bytes y la regla ~4 bytes/token, declarada).
   Qué parte es descripción, qué parte esquema, qué parte repetición entre herramientas.
2. **Buscar el desperdicio**, por ejemplo: `outputSchema` enteros que el agente no necesita para
   llamar; textos largos en `description` que explican el porqué del diseño (eso va en el contrato,
   no en cada conexión); campos que se repiten en cada respuesta (`oracle_version`, `proyecto`,
   `entrada_sha256`); testigos y alcances que se podrían pedir con un argumento; JSON con sangría.
3. **Proponer, con la cifra de cada cambio**, cuánto baja y qué se pierde. Ojo con lo que NO se
   puede recortar: la regla del contrato es que las respuestas sean falsables (premisas a la vista,
   alcance, testigos concretos). Bajar tokens escondiendo el alcance sería volver al verde a secas.
4. Implementar lo que se apruebe, con el contrato regenerado desde el código (ver el diseño en
   [`repo-limpio`](../20260923-113951-repo-limpio/TAREA.md)) y los tests del MCP en verde.

### Nota (2026-09-23 12:15:26 UTC)

2026-09-23: Codex midió y se quedó sin cuota antes de proponer (vuelve 13:11). Lo medido, verificado por Claude sobre medicion/resultados.json: (1) outputSchema es el 55 % de tools/list (6.741 de 12.366 bytes); (2) cada respuesta lleva el mismo JSON dos veces —content[0].text es exactamente structuredContent serializado—, así que pesa x2,03 a x2,23 lo necesario; (3) oracle_tareas listar devuelve 40 KB porque trae el cuerpo de cada tarea. Matiz antes de recortar: la especificación de MCP RECOMIENDA el texto duplicado por compatibilidad, y outputSchema es opcional; lo que se paga no son los bytes del cable sino lo que cada cliente (Claude Code, Codex, agy) le pasa al modelo. Primero medir eso en al menos dos clientes; la ganancia segura, sin depender del cliente, es listar sin cuerpos. Sin tokenizador instalado: la regla es bytes/4, declarada.

### Nota (2026-09-23 17:30:14 UTC)

Implementadas las reducciones independientes del cliente: listar sin cuerpo (ver y buscar conservan el contenido) y descripciones breves con límites explícitos. Se conservan outputSchema, ambas copias, metadatos, huellas, alcances y testigos. Contrato regenerable desde HERRAMIENTAS con python3 -m tools.mcp_contrato; 147 tests MCP verdes. Ahorro comparable a captura original: 34.732 bytes por payload de listar y 718 bytes netos en tools/list. Evidencia y verificador en verificacion/ y verificar_ahorro.py. Suite completa en curso; sin commits.

## Propuestas y decisión (2026-09-23)

Fuente: `medicion/resultados.json` y sus candidatos, sin sobrescribir la captura.
Todas las cifras son bytes UTF-8 de JSON compacto y estimaciones bytes/4: **no son
un conteo de tokens reales ni facturación del modelo**. Los ahorros de distintas
representaciones no se suman. Reducir contenido no requiere adaptación del cliente;
cuánto de ese contenido cobra cada anfitrión sigue sin haberse medido.

### Sin dependencia del cliente

| Propuesta | Antes → después (bytes) | Ahorro bytes / tokens estimados | Decisión y pérdida |
|---|---:|---:|---|
| `oracle_tareas listar` sin cuerpos | 39.966 → 5.234 por payload | 34.732 / 8.683 (86,9 %) | Implementada. Lista todos los metadatos y conserva filtros y orden; cuerpo y notas completos mediante `ver`, texto localizable mediante `buscar`. No cambia los veredictos. |
| Descripciones breves, candidato original | 12.376 → 11.499 en tools/list | 877 / 219,25 | Implementada con ajustes: explicita cuerpo completo, selección por ids, evidencia JSON y corpus opcional. Sólo quita explicación redundante; garantías de lectura siguen en annotations y contrato. |
| Descripciones finales + precisión del esquema de tareas | 12.376 → 11.658 en tools/list | **718 / 179,5** | Ahorro neto real de la implementación; el esquema conserva su estructura y aclara listar/ver. |
| Compactar JSON | Ya compacto | 0 / 0 | No hay trabajo: `_json_compacto` y `_enviar` ya usan separadores compactos. |

### Dependientes del cliente: pendientes, no implementadas

| Propuesta | Antes → después (bytes) | Ahorro bytes / tokens estimados | Dependencia / pérdida |
|---|---:|---:|---|
| Quitar outputSchema | 12.376 → 5.635 en tools/list | 6.741 / 1.685,25 | Falta medir si cada cliente lo expone al modelo; pierde contrato de salida para validadores. |
| Quitar outputSchema + descripciones del candidato | 12.376 → 4.758 | 7.618 / 1.904,5 | Combinación original, no ahorro adicional; misma dependencia. |
| Una copia: catálogo | 14.142 → 7.471 en result | 6.671 / 1.667,75 | El candidato medido quita structuredContent y conserva texto. Quitar texto en su lugar tiene otra cifra y afecta a clientes que lo necesitan. |
| Una copia: evaluar | 2.442 → 1.273 | 1.169 / 292,25 | Misma dependencia de presentación y compatibilidad. |
| Una copia: desafiar | 1.116 → 595 | 521 / 130,25 | Ídem. |
| Una copia: juzgar | 5.586 → 2.883 | 2.703 / 675,75 | Ídem. |
| Una copia: tareas ver | 5.105 → 2.609 | 2.496 / 624 | Ídem. |
| Una copia: tareas listar original | 80.953 → 40.966 | 39.987 / 9.996,75 | Ídem; no sumar a listar sin cuerpos. |
| Agrupar catálogo por origen y fijación | 6.650 → 3.032 por payload | 3.618 / 904,5 | No pierde esos valores, pero reemplaza `medidas` por `grupos`: rompe el esquema v1 y requiere migración de consumidores. Se conserva el contrato actual. |

Para la variante explícita **quitar el texto duplicado**, conservando structuredContent y
`content: []`, cálculo adicional sobre la misma captura (bytes de result):

| Respuesta | Antes → después | Ahorro bytes / tokens estimados |
|---|---:|---:|
| catálogo | 14142 → 6701 | 7441 / 1860.25 |
| evaluar | 2442 → 1199 | 1243 / 310.75 |
| desafiar | 1116 → 551 | 565 / 141.25 |
| juzgar | 5586 → 2733 | 2853 / 713.25 |
| tareas ver | 5105 → 2526 | 2579 / 644.75 |
| tareas listar | 80953 → 40017 | 40936 / 10234 |

También queda pendiente de compatibilidad y exposición real al modelo; no se implementó.

La nota previa advierte que MCP recomienda el texto por compatibilidad. No se ha
verificado la exposición al modelo en Claude Code, Codex ni agy; ninguna cifra de
transporte demuestra por sí sola ahorro de contexto. No se retira ninguna copia.

### Recortes rechazados por perder trazabilidad o falsabilidad

| Propuesta | Ahorro por payload, bytes / tokens estimados | Motivo |
|---|---:|---|
| Quitar oracle_version y proyecto | 140 / 35 en cada una de las seis respuestas medidas | Pierde versión y proyecto al leer una respuesta aislada. |
| Quitar entrada_sha256 | 84 / 21 en evaluar, desafiar y juzgar; 0 en catálogo y tareas | Pierde identidad de la entrada; la huella del catálogo es otro campo y se conserva. |
| Quitar alcance, alcance_derivado y testigos de evaluar | 529 / 132,25 | Esconde las premisas y la evidencia concreta. Prohibido por el pedido. |
| Lo mismo en juzgar | 1.234 / 308,5 | Ídem. |

## Implementación y evidencia

- `tools/mcp.py`: sólo descripciones y proyección sin cuerpo en listar; no se tocan los evaluadores.
- `tools/mcp_contrato.py`: genera el bloque JSON de `estudios/MCP-CONTRATO.md` desde HERRAMIENTAS;
  `--check` y el test normativo exigen que esté regenerado. La mudanza a docs sigue en repo-limpio.
- `tests/test_mcp_027.py`: verifica metadatos íntegros, filtros, cuerpo y notas en ver y búsqueda
  del texto omitido del listado. La suite existente cubre orden, errores, contrato y falsabilidad.
- `verificar_ahorro.py` reproduce las llamadas y deja `verificacion/ahorro.json` sin alterar
  medicion/. Compara la captura fija y también el tracker actual, cuyo cuerpo crece con estas notas.
  Evaluar/desafiar/juzgar conservan sus payloads; catálogo sólo difiere en huella_proyecto de la
  captura anterior (dependiente del estado de los archivos), no en las medidas ni su procedencia.
- MCP: 147 tests verdes en `verificacion/mcp.log`. Suite completa: **2.415 tests OK** en 84,360 s, `verificacion/suite.log`.
- No se hicieron commits. La tarea permanece ABIERTA por las propuestas que requieren clientes.

### Nota (2026-09-23 17:33:04 UTC)

Verificación final: suite completa 2415 tests OK en 84,360 s (verificacion/suite.log), MCP 147 OK, contrato --check y diff --check verdes. La primera corrida completa capturó descripciones durante una edición y tuvo dos comparaciones fallidas; se conserva suite-durante-edicion.log y la repetición estable pasó. oracle test detectó cifras README vencidas; se regeneraron (2415 tests, 7905 sitios) y se está repitiendo. Sin commits.

### Nota (2026-09-23 17:34:29 UTC)

Cierre de esta intervención, sin commits: 2415 tests de suite completa OK, 147 tests MCP OK, contrato regenerado y --check OK, cifras README regeneradas y --check OK. oracle test repetido terminó exit 0 / VERDE (verificacion/oracle-test.log); mutación de medidas 1010/1010, alcance corpus guardado y omisión de mutación de código explícitos. Propuestas separadas y cuantificadas en el cuerpo; sólo listar sin cuerpos y descripciones breves implementadas. Pendiente: medir al menos dos clientes para las variantes del esquema y la duplicación; tarea ABIERTA.

## Qué recibe el modelo en cada cliente (2026-09-23)

La sonda `clientes/sonda_mcp.py` pone una marca aleatoria distinta en la descripción (D), en el
`outputSchema` (S), en el bloque de texto (T) y en `structuredContent` (E), y ofrece una segunda
herramienta con `content: []`. `clientes/correr.sh` le pide a cada cliente que copie las marcas que
vio; `marcas-*.json` es lo emitido y `respuesta-*.txt` lo visto.

| Cliente | D | S | T | E | con `content: []` |
|---|---|---|---|---|---|
| Claude Code 2.1.281 | sí | **no** | **no** | sí | ve E |
| Codex 0.155.1 | sí | **no** | sí | sí | ve E |
| agy (Gemini 3.8 Flash) | sí | **no** | sí | **no** | no ve nada |

Lo que decide:

- **`outputSchema` no llega al modelo en ninguno.** Quitarlo no ahorra contexto, sólo transporte, y
  se perdería el contrato que valida los clientes. Se conserva.
- **Las dos copias hacen falta.** Claude Code descarta el texto cuando hay `structuredContent`;
  agy descarta `structuredContent`. Quitar cualquiera de las dos deja ciego a un cliente. Sólo Codex
  paga las dos, y el texto ya es JSON compacto (`separators=(",", ":")`): no queda recorte sin pérdida.
- **Agrupar catálogo** rompe el contrato v1 por 904 tokens; ya estaba descartado.

Lo que sí ahorraba (listar sin cuerpos, −87 %, y descripciones breves) está en `main` desde
b7f89cd. Las cifras valen para estas versiones de cliente; si una cambia, `clientes/correr.sh
<claude|codex>` repite la medición (agy necesita `agy mcp add` antes y `--sandbox
--dangerously-skip-permissions`, porque el modo sin interacción rechaza la herramienta).

## Próximo paso

Ninguno: la tarea queda cerrada con lo medido.
