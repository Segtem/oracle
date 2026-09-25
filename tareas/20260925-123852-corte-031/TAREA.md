# Corte 0.31.0

- ESTADO: ABIERTA
- PRIORIDAD: 90
- ETIQUETAS: oracle, release


Cortar 0.31.0 para que PyPI tenga lo que ya muestra la web publicada: el álgebra 1.0 (`algebra-10`:
testigos de la tubería completa, predicados booleanos estrictos, claves en toda la evidencia, sin
null, cabecera sola vacía, `unir` con tipos), las medidas sin casos en rojo (`medida-sin-casos`),
`verde-diseno` (sombra y sin evidencia, macros -requiere, `juzgar --parcial`), `nueva-con-casos`,
las fricciones de `auditoria-nuevo`, `huecos-spec`, `custodia` completa, `perfil-mutacion`,
`guias-cli`, `guias-ejecutables`, la web nueva (`web-diseno`, `de-cero-naval`) y el ejemplo de la
batalla naval. `VERSION_ALGEBRA` 1.0 es mayor: los consumidores siguen fijados en 0.30.0 hasta
migrar sus null (`algebra-10-null` en LyraGASP y Jam).

## Próximo paso

La mutación de lo tocado (18 módulos, lanzada el 2026-09-25), después notas, crónica, cifras al
final, build limpio, tag y release; Brian sube a PyPI.

### Nota (2026-09-25 13:00:54 UTC)

2026-09-25: la ronda encontró dos puntos flojos, arreglados en beea467 (null en corrida_mutacion → -1; unir indexado con claves bool cede al producto). En la rama corte-031 (worktree del scratchpad): --help de nueva/medida/caso, versión 0.31.0, crónica y notas. algebra.py y cli.py se re-mutan desde esa rama al terminar la ronda (tanda c031b); después, cifras, build, tag.
