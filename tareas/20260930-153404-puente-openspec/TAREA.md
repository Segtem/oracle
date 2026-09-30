# puente OpenSpec → Oracle: importar spec.md a requisitos y verificar como paso de /opsx:verify

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: oracle

### Nota (2026-09-30 15:34:04 UTC)

Por qué (2026-09-30): OpenSpec tiene 70.771 estrellas y ninguna herramienta de specs popular verifica de forma determinista si el código cumple la spec; Kiro prueba propiedades pero no valida sus propias propiedades (ni mutación ni puntos ciegos declarados). Un importador de ### Requirement a .requisito (con sin_medir pendiente) y un paso de verificación enchufable a /opsx:verify es la mayor vía de adopción y el camino más directo para destrabar pilotos-externos. Base: el experimento de tareas/20260928-210611-openspec/ (sensor, 32 medidas, requisitos de cli-validate).

### Nota (2026-09-30 20:00:24 UTC)

Hecho: oracle requisito importar <spec.md | openspec/specs> [--dominio d] [--escribir] (tools/openspec.py): cada ### Requirement es un .requisito sin medir con texto SHALL, fuente spec.md#Nombre y sin_medir que nombra los escenarios pendientes; lo existente no se toca. Sobre OpenSpec real (clon del 2026-09-30): cli-validate 12 requisitos/31 escenarios como en el experimento; las 36 specs, 251 requisitos, todos cargan; reimportar no cambia nada. Paso de /opsx:verify documentado en docs/openspec.md: operations.apply.guidance de openspec/config.yaml llega a lo que verify lee, pero como consejo; la garantía es oracle cambios + oracle cobertura --con en hook o CI. Mutación: openspec.py 43/43, líneas nuevas de cli.py 25/25; en la matriz de CI. Suite 2239 OK; oracle test VERDE.
