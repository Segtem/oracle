# el generador busca y encoge evidencia en vez de aplicar reglas fijas

- ESTADO: ABIERTA
- PRIORIDAD: 60
- ETIQUETAS: oracle

### Nota (2026-09-30 15:34:04 UTC)

Por qué: el generador de casos es heurístico por forma de medida y no cubre auto-joins, agrupar ni disyunciones anidadas. Property-based testing (y Kiro con fast-check) busca contraejemplos y los encoge al mínimo. Buscar evidencia que mate a cada mutante vivo y encogerla daría casos mínimos para formas que hoy no se pueden generar. Ballí (arXiv 2607.13707) respalda que la evidencia de defecto se fabrique por perturbación determinista, no por un modelo.
