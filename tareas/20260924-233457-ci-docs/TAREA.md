# El CI no corre cuando sólo cambia docs/, y docs/ ya tiene archivos que oracle test lee

- ESTADO: CERRADA
- PRIORIDAD: 75
- ETIQUETAS: oracle, ci, flaqueza


## Por qué

`.github/workflows/verificar.yml` ignora `**.md` y `docs/**`. Tenía sentido cuando `docs/` era sólo
la web. Desde 0.30.0, `docs/` tiene archivos que `oracle test` y la suite leen:
`docs/03-escribir-una-medida.md` y `docs/tutorial-practico.md` (en `DOCUMENTOS_CON_SUPERFICIE`, que
verifica sus bloques `oracle`), `docs/mcp-contrato.md` (el contrato que compara `tests/test_mcp.py`) y
`docs/decisiones/` (el test de ids citados). Un commit que sólo toca `docs/` puede poner rojo
`oracle test` sin que corra el CI. Pasó al revés en la mudanza de `repo-limpio`: hubo que verificarla
a mano.

## Qué hacer

Que el CI corra cuando cambia cualquier archivo que algo verifica. Lo más chico: quitar `docs/**` y
`**.md` del ignore, y dejar ignorados sólo `vault-kb/**` y lo que de verdad nadie lee. Medir el costo
en minutos de Actions con la cuenta del propio comentario del workflow.

### Nota (2026-09-24 23:46:05 UTC)

Test nuevo: tests.test_ci_docs falló con el filtro anterior y pasó con el cambio. verificar.yml ignora vault-kb/** y tareas/**; tracker.yml cubre tareas/**. Costo estimado según el comentario del workflow: ~8 min de Actions por push de docs y ~68 min por pull request. Suite completa: 2441 tests OK; test --rapido: VERDE tras actualizar cifras. Sin ids de equivalentes afectados.

## Próximo paso

Integrar los cambios desde un entorno con escritura en `.git`.
