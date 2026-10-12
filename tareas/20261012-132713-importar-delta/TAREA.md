# El importador de OpenSpec entiende las secciones del delta (ADDED, MODIFIED, REMOVED)

- ESTADO: ABIERTA
- PRIORIDAD: 30
- ETIQUETAS: openspec, importar


## Objetivo

`oracle requisito importar` lee los `### Requirement:` de una spec de OpenSpec sin mirar en qué sección del delta están. Un requisito bajo `## REMOVED Requirements` (que sólo trae su título) se importa como uno nuevo, con el título como texto y sin cuerpo, y queda «sin medida todavía» aunque lo que se pide es retirarlo.

Pasó en Oracle Factory, cambio `20261012-131420-clue-dependencia` (2026-10-12), la primera spec con REMOVED. Factory lo resolvió de su lado: después de importar, borra los requisitos de la sección REMOVED. Cuando el importador entienda las secciones, ese filtro puede salir.

## Notas

- REMOVED: no importar (o reportarlo aparte como «a retirar»).
- MODIFIED: importar como hoy, con el texto nuevo.
- RENAMED: OpenSpec lo define; Factory lo rechaza.
