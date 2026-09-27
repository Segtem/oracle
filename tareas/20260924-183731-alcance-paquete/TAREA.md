# El tracker y el MCP son subsistemas grandes dentro de un paquete que se presenta como un metalenguaje

- ESTADO: CERRADA
- PRIORIDAD: 55
- ETIQUETAS: oracle, arquitectura


## Por qué

[la auditoría](../20260924-174258-auditoria/AUDITORIA.md) §2.6: `tools/` tiene 16 415 líneas y `nucleo/` 10 848. El tracker (`tareas*.py`) y el MCP (1962
líneas) crecen más rápido que el lenguaje.

## Qué hacer

Decidir si el tracker es parte del producto o un consumidor que vive en el mismo repo, antes de que
la API pública lo fije. Hay que medir qué importa el tracker del núcleo y qué importa el núcleo del
tracker, y ver qué costaría separarlo en un paquete aparte con la misma versión.

**Quién:** agy (la medición de dependencias); Brian decide.

## Próximo paso

La medición.

### Nota (2026-09-27 12:41:14 UTC)

2026-09-27, MEDICIÓN (Claude): el tracker (tools/tareas*.py, 6 archivos, ~4240 líneas) NO importa nada de nucleo/; sólo se importa a sí mismo. El núcleo no importa el tracker: lo despachan tools/cli.py (oracle tarea) y tools/mcp.py. Ningún catálogo del núcleo mide tareas; sólo el ejemplo ejemplo/seguimiento-tareas juzga los hechos que emite oracle tarea hechos. El MCP (tools/mcp.py, ~2000 líneas) importa nucleo (medida, proyecto, sintaxis, version), tools.juzgar, tools.medida, tools.sesion y el tracker (tareas, tareas_contexto, tareas_hechos). El único proyecto ajeno conocido (AJENO, ver pilotos-externos) usa Motor y oracle test, ni tracker ni MCP. PROPUESTA (Brian decide): tracker a su repo y paquete propio, con el ejemplo de seguimiento como su proyecto Oracle y oracle tarea como alias por una o dos versiones; MCP como segunda distribución del mismo repo de Oracle (oracle-mcp, fijado ==), porque usa API interna, y sus herramientas de tareas se van con el tracker.

### Nota (2026-09-27 18:30:58 UTC)

2026-09-27, Claude: resuelta por separar-tracker-mcp. Brian decidió separar las dos piezas medidas acá: el tracker a Segtem/trackertast y el MCP a Segtem/oracle-mcp, publicados en PyPI. oracle-metalenguaje 0.34.0 queda en el metalenguaje (álgebra, superficie, Motor, test, juzgar, LSP, mutación) y bajó de 2761 a 2117 tests.
