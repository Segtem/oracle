# oracle test --todo: la línea base supera el timeout de 60 segundos

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

### Nota (2026-09-22 22:14:33 UTC)

Detectado al preparar jev-porque-v2. python3 tools/cli.py test --todo terminó con código 1: LineaBaseFallida por timeout 60 s. Los 2401 unitarios pasaron en 82,645 s; la línea base aislada alcanzó 1235 tests en 59,460 s antes de SIGTERM. Evidencia íntegra: tareas/20260922-220029-jev-porque-v2/verificacion/oracle-test-todo.log. tools/cli.py invoca mutar_codigo.argumentos([]), cuyo timeout por defecto es 60 s. No se cambió código ni se reintentó una ronda larga. El árbol tenía cambios previos de otra tarea, preservados.

## Próximo paso

Revisar el presupuesto de tiempo de la línea base completa en `oracle test --todo`
y su propagación al arnés; distinguir el timeout de base del timeout por mutante.
Reproducir con tiempo suficiente sin debilitar el criterio de muerte, agregar la
prueba pertinente y correr las verificaciones. No declarar verde la mutación con
una línea base interrumpida. Evidencia inicial en
`tareas/20260922-220029-jev-porque-v2/verificacion/oracle-test-todo.log`.

### Nota (2026-09-23 00:48:05 UTC)

En curso: confirmado que oracle test --todo usa el mismo timeout de 60 s para base y mutantes. Medición aislada iniciada con techo diagnóstico de 600 s, bytecode frío y límite de memoria original; evidencia en verificacion/medicion-base.log. Implementada opción independiente timeout_base/--timeout-base con herencia del timeout anterior si se omite; pendiente fijar presupuesto de --todo después de medir y validar suite completa. Sin commits.
