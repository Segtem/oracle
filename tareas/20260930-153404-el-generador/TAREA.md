# el generador busca y encoge evidencia en vez de aplicar reglas fijas

- ESTADO: CERRADA
- PRIORIDAD: 60
- ETIQUETAS: oracle

### Nota (2026-09-30 15:34:04 UTC)

Por qué: el generador de casos es heurístico por forma de medida y no cubre auto-joins, agrupar ni disyunciones anidadas. Property-based testing (y Kiro con fast-check) busca contraejemplos y los encoge al mínimo. Buscar evidencia que mate a cada mutante vivo y encogerla daría casos mínimos para formas que hoy no se pueden generar. Ballí (arXiv 2607.13707) respalda que la evidencia de defecto se fabrique por perturbación determinista, no por un modelo.

### Nota (2026-09-30 20:46:27 UTC)

Hecho: buscar_candidatos en nucleo/generador.py (semillas de las reglas y del corpus de la medida; vecinos deterministas a uno y dos cambios; criterio de correr; encogido recursivo). oracle caso generar la usa; «no posible» sólo si ni reglas ni búsqueda encuentran. Experimento con corpus vacío (experimento/README.md): OpenSpec 80,8→93,7 %, LyraGASP 76,6→88,9 %, Jam 76,6→78,6 %, Oracle 68,0→83,9 %; medidas no posibles 28→0. Mutación de las líneas nuevas 67/67 (un timeout del bucle de encogido se resolvió reescribiéndolo sin bandera). Suite 2247 OK; oracle test VERDE. Límite: la evidencia no respeta los tipos del .relacion.
