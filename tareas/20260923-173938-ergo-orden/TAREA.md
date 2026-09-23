# Propuesta: explicar la ubicación de requiere en errores de sintaxis

- ESTADO: CERRADA
- PRIORIDAD: 60
- ETIQUETAS: ergonomia, propuesta

## Alcance propuesto

Derivada de [ergonomia](../20260923-120207-ergonomia/VERIFICACION.md), entrada 3.1, grupo 3. Es una propuesta: no se implementó en la auditoría.

Colocar requiere antes de resumen o umbral falla con «se esperaba línea resumen/umbral», sin explicar dónde mover la cláusula. El mismo archivo carga al ponerla después de umbral y antes de ambito.

La solución mínima propuesta es un diagnóstico contextual con la posición permitida y el fragmento afectado. Se conserva el orden gramatical y el AST. No aceptar cláusulas en cualquier orden ni reordenar pasos de tubería.

## Aceptación propuesta

- Los dos errores reproducidos explican dónde mover requiere.
- La forma válida conserva AST y evaluación; se mantienen ubicación de línea/columna y códigos de fallo.
- VERSION_ALGEBRA 0.8 y VERSION_SINTAXIS 0.6 no cambian: mejora de mensaje, no gramática nueva.

### Nota (2026-09-23 17:43:54 UTC)

Propuesta derivada de ergonomia 3.1: dos posiciones rechazadas y control válido reproducidos. Sólo se escribió alcance y aceptación; sin implementación ni commits.

### Nota (2026-09-23 20:02:22 UTC)

Inicio autorizado: implementar sólo el diagnóstico contextual para requiere antes de resumen/umbral, sin cambiar gramática, AST ni versiones. Se agregarán regresiones y controles de evaluación, ubicación y código CLI; se comprobará rojo antes del cambio y suite completa después. Sin commits por instrucción del usuario.

### Nota (2026-09-23 20:03:33 UTC)

Regresiones verificadas antes del cambio: tests.test_requiere_orden ejecutó 4 tests, con 4 fallos de subtests exclusivamente por faltar la indicación en las dos posiciones (lector y CLI); controles de AST/evaluación y otro prefijo en verde. Cambio mínimo en _exigir_prefijo: añade una línea contextual sólo al encontrar requiere donde se esperaba resumen o umbral. Después del cambio: 169 tests de orden, requiere y sintaxis OK. Suite completa python3 tools/cli.py test --todo en ejecución.

### Nota (2026-09-23 20:05:39 UTC)

Primera verificación test --todo: rojo por referencias posicionales desplazadas en equivalentes.json (causaron 5 fallos y 4 errores en 2419 tests) y cifras README vencidas. Se reapuntaron únicamente los dos sitios intactos de _expr (+3 líneas) y se regeneró README con tools/cifras.py --actualizar. Se repite la suite estándar completa con python3 tools/cli.py test; la mutación exhaustiva de código es una ronda adicional separada.

### Nota (2026-09-23 20:07:24 UTC)

Implementación terminada. python3 tools/cli.py test: exit 0, 2419 tests OK (83.037 s), corpus/sintaxis/aceptación/diferencial/metamórficas/cifras en verde y 1010/1010 mutantes de medida muertos. La suite estándar omite mutación exhaustiva de código; no se afirma que test --todo esté verde. Evidencia en verificacion/regresiones-sin-cambio.log (4 subtests rojos por mensaje faltante), verificacion/primera-suite.log (fallos de referencias y cifras ya corregidos) y verificacion/suite.log (verde final). Cambio productivo: 3 líneas netas en nucleo/sintaxis.py; tests/test_requiere_orden.py cubre dos posiciones, CLI exit 1, fragmento, línea/columna, AST y evaluación verde/roja/sin evidencia, versiones 0.8/0.6 y prefijo ajeno. README regenerado y dos referencias equivalentes reapuntadas sin cambiar sus razones. git diff --check limpio; sin commits.

## Próximo paso

Ninguno dentro del alcance: diagnóstico mínimo implementado y suite estándar completa en verde. Tarea CERRADA; cambios sin commit por instrucción del usuario. La mutación exhaustiva de código no está certificada por esta verificación.
