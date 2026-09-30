# puente OpenSpec → Oracle: importar spec.md a requisitos y verificar como paso de /opsx:verify

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: oracle

### Nota (2026-09-30 15:34:04 UTC)

Por qué (2026-09-30): OpenSpec tiene 70.771 estrellas y ninguna herramienta de specs popular verifica de forma determinista si el código cumple la spec; Kiro prueba propiedades pero no valida sus propias propiedades (ni mutación ni puntos ciegos declarados). Un importador de ### Requirement a .requisito (con sin_medir pendiente) y un paso de verificación enchufable a /opsx:verify es la mayor vía de adopción y el camino más directo para destrabar pilotos-externos. Base: el experimento de tareas/20260928-210611-openspec/ (sensor, 32 medidas, requisitos de cli-validate).
