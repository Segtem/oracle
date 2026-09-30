# sonda del generador por forma: auto-join, agrupar y disyunción anidada

- ESTADO: ABIERTA
- PRIORIDAD: 62
- ETIQUETAS: 

### Nota (2026-09-30 21:53:05 UTC)

Por qué: la propuesta 5 prometía cubrir auto-joins, agrupar y disyunciones anidadas; en 0.38.0 se midió el total (no posibles 28→0) pero no esas formas por separado. Qué: una sonda (como tools/sondear_generador.py) con medidas construidas de esas tres formas, que diga cuántos mutantes fija reglas sola y reglas+búsqueda en cada una. Si alguna queda corta, es el dato para la mejora siguiente.
