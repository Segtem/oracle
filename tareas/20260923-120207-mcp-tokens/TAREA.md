# El MCP gasta tokens que el agente paga antes de hacer nada

- ESTADO: ABIERTA
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

## Próximo paso

La medición del punto 1 y la lista de propuestas con su cifra, para revisión antes de implementar.

### Nota (2026-09-23 12:15:26 UTC)

2026-09-23: Codex midió y se quedó sin cuota antes de proponer (vuelve 13:11). Lo medido, verificado por Claude sobre medicion/resultados.json: (1) outputSchema es el 55 % de tools/list (6.741 de 12.366 bytes); (2) cada respuesta lleva el mismo JSON dos veces —content[0].text es exactamente structuredContent serializado—, así que pesa x2,03 a x2,23 lo necesario; (3) oracle_tareas listar devuelve 40 KB porque trae el cuerpo de cada tarea. Matiz antes de recortar: la especificación de MCP RECOMIENDA el texto duplicado por compatibilidad, y outputSchema es opcional; lo que se paga no son los bytes del cable sino lo que cada cliente (Claude Code, Codex, agy) le pasa al modelo. Primero medir eso en al menos dos clientes; la ganancia segura, sin depender del cliente, es listar sin cuerpos. Sin tokenizador instalado: la regla es bytes/4, declarada.
