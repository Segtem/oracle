# Un agente no encuentra una tarea que existe porque adivina el prefijo de su id

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: oracle, tracker, agentes


## Qué pasó

2026-09-19, en LyraGASP: Codex dijo que la tarea `multimalla` «no existe». Existe:
`20260919-140308-multimalla`. Codex la buscó como `tareas/20260919-140309-multimalla` porque el
resto de la tanda tenía ese prefijo: las 27 tareas se crearon en dos segundos distintos (7 con
`140308`, 20 con `140309`). El `sed` falló y la conclusión fue «no existe».

El tracker no ayuda: `oracle tarea ver multimalla` responde «no se encontró ninguna tarea con id o
prefijo «multimalla»». `resolver_id_o_prefijo` (`tools/tareas.py`) sólo resuelve por id completo o
por prefijo, y el prefijo es la parte que nadie recuerda: la marca de tiempo. La parte que un humano o
un agente sí recuerda es el **sufijo**.

## Qué hacer

1. `oracle tarea ver|anotar|cerrar|reabrir <x>` resuelven también por sufijo exacto (`multimalla`)
   cuando es único; si hay varios, `IdAmbiguo` con la lista.
2. Si no hay coincidencia, el error sugiere las más parecidas («¿quisiste decir
   20260919-140308-multimalla?»), en vez de un «no se encontró» que un agente lee como «no existe».
3. El MCP (`oracle_tareas` acción `ver`) usa el mismo resolvedor, así que lo hereda.
4. En el protocolo de `AGENTS.md`: referirse a una tarea por su id completo o por su sufijo, nunca
   reconstruir un id a mano ni buscarla con un glob.

### Nota (2026-09-21 20:32:14 UTC)

Implementado el resolvedor compartido por CLI y MCP: sufijo completo exacto y único, IdAmbiguo con IDs ordenados, sugerencias de hasta tres IDs similares (comparación con ID y sufijo, umbral 0.6), conservando precedencia del ID completo y prefijos. Actualizados AGENTS.md, ayuda del CLI y docs/12-tareas.md. Agregados 11 tests en tests/test_tareas_sufijo.py para resolvedor, seguridad, CLI ver/anotar/cerrar/reabrir, ausencia de mutaciones ante errores y MCP. Los 11 tests pasan; suite completa en ejecución. Verificación manual: tarea ver buscar-sufijo --ruta devuelve esta tarea. Sin commits.

### Nota (2026-09-21 20:32:50 UTC)

Validación final: python3 -B -m unittest discover -s tests -t . -q terminó con código 0: Ran 2375 tests in 74.810s, OK. git diff --check sin errores. Implementación y tests completos; no se hicieron commits por instrucción del usuario. El cierre con commit queda para Claude.

## Próximo paso

Claude: revisar los cambios validados (2375 tests OK), marcar la tarea CERRADA y crear el
commit `20260919-171824-buscar-sufijo: done`. No quedan cambios de implementación pendientes.
