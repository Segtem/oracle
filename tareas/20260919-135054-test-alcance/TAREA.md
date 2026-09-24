# Distinguir en oracle test la validación del corpus y la ausencia de medición del producto

- ESTADO: CERRADA
- PRIORIDAD: 75
- ETIQUETAS: oracle, ux

## Problema y evidencia

Derivada de 20260919-134424-naval-pm; ver [postmortem](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md) y [reproducciones](../../vault-kb/postmortems/naval-pm/oracle-resultados.txt).
Con Oracle 0.27.0, un catálogo propio vacío y un caso sobre una medida heredada de sintaxis reciben verde con `test --rapido`, aun destruyendo game.js en una copia temporal. El caso guarda booleanos; el comando valida ese corpus, no reejecuta el juego. Sin casos ni medidas propias, cmd_test emite explícitamente VERDE de proyecto vacío. Son dos escenarios diferentes.

## Resultado buscado

Que el resumen final permita reconocer qué se validó, qué se omitió y qué no se midió. No inferir cobertura del producto de la cantidad de medidas propias ni rechazar proyectos legítimos que sólo usan medidas heredadas.

## Alcance y aceptación

- Definir y documentar el estado del proyecto vacío (propuesta: advertencia/“sin medición”), separado de error de estructura y de corpus válido. Decidir explícitamente compatibilidad y códigos de salida para CI antes de cambiarlos.
- Mostrar en el veredicto de test que se verificaron medidas contra casos guardados; no que se volvió a ejecutar el comando de origen o el producto. Mantener visibles las omisiones de --rapido.
- Reproducir vacío, un caso con medida heredada, medidas propias con corpus válido y corpus inválido. Incluir el control donde cambia game.js y el caso no cambia: el resultado del corpus puede conservarse, su alcance debe quedar claro.
- Mantener la semántica de juzgar y su ausencia de medidas aplicables; no mezclarla con aceptación del corpus ni exigir sensores por una heurística de nombres de dominio.

### Nota (2026-09-21 20:33:38 UTC)

Contrato decidido antes de implementar: conservar exit 0 para proyecto vacío y verificaciones aprobadas, exit 1 para estructura o verificaciones fallidas. Cambiar el vacío de VERDE a advertencia SIN MEDICIÓN; explicitar en el resumen la evaluación de medidas contra casos guardados, sin reejecución de origen/producto, y conservar omisiones de --rapido también en rojo. No cambiar juzgar ni inferir cobertura por medidas propias.

### Nota (2026-09-21 20:37:06 UTC)

Implementado: proyecto vacío informa SIN MEDICIÓN sin CORPUS OK y conserva exit 0; resumen final aclara verificación contra casos guardados y ausencia de nueva medición del producto; omisiones de --rapido visibles también en rojo. README y guía de inicio documentan contrato y compatibilidad textual. Regresiones cubren vacío en tres niveles, corpus propio y heredado, game.js destruido con evidencia intacta (misma salida), polaridad inválida, caso malformado y estructura inválida. El caso malformado reveló una excepción sin capturar en aceptación: ahora llega al resumen ROJO/exit 1; ruta completa de mutación verificada. Pruebas focalizadas: 3 tests OK (9,292 s). Suite completa final en ejecución. Sin cambios a juzgar y sin commits.

### Nota (2026-09-21 20:38:31 UTC)

Validación final: python3 -B -m unittest discover -s tests -t . -q completó 2378 tests en 83,173 s, OK (exit 0). git diff --check sin errores. Implementación y documentación completas; queda revisión y commit por Claude, según instrucción del usuario. Se preservaron los cambios preexistentes de otras tareas; no se hicieron commits.

## Próximo paso

Claude: revisar los cambios de esta tarea en tools/cli.py, tests/test_test_alcance.py, tests/test_cli.py, tests/test_cli_integracion.py, README.md y docs/02-de-cero-a-un-rojo.md; hacer el commit con el ID 20260919-135054-test-alcance y cerrar la tarea. Implementación completa, sin bloqueos técnicos: suite final de 2378 tests OK. No incluir los cambios preexistentes de otras tareas. Codex no hizo commits por instrucción del usuario.
