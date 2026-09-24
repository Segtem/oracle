# oracle test --todo: la línea base supera el timeout de 60 segundos

- ESTADO: CERRADA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-09-22 22:14:33 UTC)

Detectado al preparar jev-porque-v2. python3 tools/cli.py test --todo terminó con código 1: LineaBaseFallida por timeout 60 s. Los 2401 unitarios pasaron en 82,645 s; la línea base aislada alcanzó 1235 tests en 59,460 s antes de SIGTERM. Evidencia íntegra: tareas/20260922-220029-jev-porque-v2/verificacion/oracle-test-todo.log. tools/cli.py invoca mutar_codigo.argumentos([]), cuyo timeout por defecto es 60 s. No se cambió código ni se reintentó una ronda larga. El árbol tenía cambios previos de otra tarea, preservados.

### Nota (2026-09-23 00:48:05 UTC)

En curso: confirmado que oracle test --todo usa el mismo timeout de 60 s para base y mutantes. Medición aislada iniciada con techo diagnóstico de 600 s, bytecode frío y límite de memoria original; evidencia en verificacion/medicion-base.log. Implementada opción independiente timeout_base/--timeout-base con herencia del timeout anterior si se omite; pendiente fijar presupuesto de --todo después de medir y validar suite completa. Sin commits.

### Nota (2026-09-24 00:54:29 UTC)

Resuelto: el árbol ya traía timeout_base/--timeout-base independiente. La línea base aislada con bytecode frío y límite de memoria original pasó 2401 tests en 163,716 s (verificacion/medicion-base.log); oracle test --todo ahora le asigna 240 s a la base y conserva 60 s por mutante. Test de regresión agregado: falló antes (None != 240.0) y pasó después; los tests del arnés confirman que timeout de mutante no cuenta como muerte. Suite completa: 2428 tests OK en 86,821 s (verificacion/suite-completa.log). python3 tools/cifras.py --actualizar: README actualizado. No se corrió ronda completa de mutación de código ni se hicieron commits.

## Próximo paso

No queda trabajo pendiente en esta tarea.
