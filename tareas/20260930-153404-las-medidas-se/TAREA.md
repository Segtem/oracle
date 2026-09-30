# las medidas se validan contra defectos reales, no sólo con mutación

- ESTADO: ABIERTA
- PRIORIDAD: 84
- ETIQUETAS: oracle

### Nota (2026-09-30 15:34:04 UTC)

Por qué: Zhao, Zhou y Cohen (ISSTA 2026, arXiv 2607.22880) muestran que el puntaje de mutación de suites generadas por modelos correlaciona con la efectividad en regresión pero deja de ser confiable cuando el código ya tiene bugs. Oracle usa la mutación como criterio de medida fijada. Los casos procedencia: observada son defectos reales, pero no se cuentan aparte. Experimento: por medida, cuántos defectos reales observados atrapa, junto a su mutación; en Oracle, LyraGASP y Jam.
