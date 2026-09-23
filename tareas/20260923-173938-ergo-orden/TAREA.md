# Propuesta: explicar la ubicación de requiere en errores de sintaxis

- ESTADO: ABIERTA
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

## Próximo paso

Revisar esta propuesta junto con la auditoría y acordar el texto del diagnóstico antes de implementar sólo esa mejora.
