# Juzgar evidencia real desde el CLI (0.18.0)

- ESTADO: CERRADA
- PRIORIDAD: 80
- ETIQUETAS: oracle, release

Oracle gana `oracle juzgar`: juzgar evidencia real —un JSON de hechos— con el catálogo efectivo de
un proyecto, en vez de un adaptador por consumidor. El tracker deja de ser un vecino: CI juzga el
`tareas/` del propio Oracle con las políticas de seguimiento.

- Plan: [PLAN-0.18.0-JUZGAR.md](../../vault-kb/planes/PLAN-0.18.0-JUZGAR.md)
- Encargo a agy: [ENCARGO-AGY.md](../../vault-kb/estudios/0.18.0-juzgar/ENCARGO-AGY.md)
- Revisión: [REVISION-CLAUDE.md](../../vault-kb/estudios/0.18.0-juzgar/REVISION-CLAUDE.md)

Convención desde esta tarea, como en tatr: cada commit de este trabajo empieza con
`20260915-010206-juzgar: `, y el que la cierra es `20260915-010206-juzgar: done` y pasa el estado a CERRADA.

Encontrado en el camino: la primera corrida manual del job de mutación de CI dejó 4 sobrevivientes
en `nucleo/mutacion.py`, deuda anterior a 0.17.0; se cierran con tests en `tests/test_mutacion.py`.

### Nota (2026-09-15 02:36:52 UTC)

Cerrada con el corte 0.18.0: oracle juzgar publicado, CI juzga el tareas/ de Oracle. Mutación juzgar.py 112/112, cli.py 536/536. Ver estudios/0.18.0-juzgar/CIERRE.md.
