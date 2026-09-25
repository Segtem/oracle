# Un caso de defecto se da por cumplido con SIN EVIDENCIA: que pueda declarar que espera sin_evidencia, distinto de un rojo medido

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, metalenguaje, sintaxis

### Nota (2026-09-25 21:59:50 UTC)

2026-09-25, origen: auditoria-verde ronda 2 (Codex), RONDA2.md fila 2. Hoy un caso falso_verde pasa la aceptación si la medida sale ROJO medido o SIN EVIDENCIA: los dos son «no ok». Los casos 029/030 de la batalla naval y 006 de primer-valor lo usan a propósito para fijar el requiere. El riesgo: un caso rojo que sale SIN EVIDENCIA no fija el donde; hoy lo cubre la mutación (los mutantes del filtro sobreviven), no la aceptación. Propuesta: un campo opcional en el caso (p. ej. «espera: sin_evidencia») que la aceptación compare exacto: un caso que lo declara tiene que salir SIN EVIDENCIA, y uno que no lo declara tiene que salir ROJO medido. Es cambio de sintaxis de .caso (sube VERSION_SINTAXIS) y de esquema; decidir antes de implementar si el campo es obligatorio para los casos que prueban requiere.
