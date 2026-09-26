# El paquete todavía enseña u ofrece la segunda forma: MCP, oracle contexto, oracle convertir, README, docs/03 y la plantilla sensor-prosa

- ESTADO: CERRADA
- PRIORIDAD: 85
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 04:10:07 UTC)

2026-09-26, origen: AUDITORIA.md de una-sintaxis (prioridades 1, 3 y 5). DECISIONES: (1) MCP: las herramientas que reciben una medida aceptan sólo superficie (se quita formato json del esquema y de docs/mcp-contrato.md); es la interfaz de los agentes y es donde más importa. (2) oracle contexto: la sección «CON QUÉ SE ESCRIBE» muestra la superficie (p.x, a + b, las escalares del proyecto), no accesores en JSON ni mas/menos/por. (3) oracle convertir sólo convierte HACIA la superficie; ver la forma canónica es oracle medida expandir. (4) README y docs/03: quitar que el catálogo y el corpus aceptan .json como forma de escribir; decir que Oracle lee JSON como formato de intercambio. (5) ejemplo/sensor-prosa/README.md manda a leer un .json que no existe: corregir. (6) Documentar en el manual y en la especificación cuándo un .caso usa el escape fila {…} (filas heterogéneas o campos no imprimibles como tabla): es la única forma de escribir esa evidencia, no una segunda. (7) Un test que falle si contexto, el esquema MCP, el manual o la documentación enseñan una forma de escritura JSON para medidas, casos o relaciones (la meta mira archivos; esto mira lo que el paquete enseña).

### Nota (2026-09-26 04:21:19 UTC)

Implementado: MCP acepta solo formato oracle para medidas en memoria; contexto muestra accesores y aritmética de superficie; convertir solo va de medida JSON a superficie; README, guía, contrato MCP, manual, especificación y sensor-prosa corregidos; prueba editorial agregada. Verificación: suite completa 2594 tests OK; guia --escribir 0 salidas actualizadas; sitio --escribir regeneró 3 páginas; test --rapido VERDE y salteó mutación. Sin ejecutar mutación separada ni hacer commits. Tarea permanece ABIERTA.

## Próximo paso

Claude: correr la mutación pendiente y revisar sus resultados; después decidir el cierre de la tarea.

### Nota (2026-09-26 04:24:33 UTC)

2026-09-26, Claude: revisada y unida. La mutación de los módulos tocados va en la ronda del corte.
