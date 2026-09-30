# las medidas se validan contra defectos reales, no sólo con mutación

- ESTADO: ABIERTA
- PRIORIDAD: 84
- ETIQUETAS: oracle

### Nota (2026-09-30 15:34:04 UTC)

Por qué: Zhao, Zhou y Cohen (ISSTA 2026, arXiv 2607.22880) muestran que el puntaje de mutación de suites generadas por modelos correlaciona con la efectividad en regresión pero deja de ser confiable cuando el código ya tiene bugs. Oracle usa la mutación como criterio de medida fijada. Los casos procedencia: observada son defectos reales, pero no se cuentan aparte. Experimento: por medida, cuántos defectos reales observados atrapa, junto a su mutación; en Oracle, LyraGASP y Jam.

### Nota (2026-09-30 15:46:56 UTC)

Experimento 1 (2026-09-30, procedencia.py): la mutación de medidas corrida por grupo de procedencia (observada, construida o generada, corpus sin declarar, fixtures diferenciales). Los tres proyectos publican mutación 100 %, pero la parte que ningún defecto real respalda (mutantes muertos que no mata ningún caso observado) es: Oracle 282 de 1026 (27,5 %; las 59 medidas tienen algún defecto real), LyraGASP 384 de 487 (78,9 %; 11 de 29 medidas con defecto real), Jam 458 de 458 (100 %; 0 de 42 medidas: su corpus no tiene ni un caso observado y la fijación sale del diferencial, 4298 casos, y de 40 casos construidos o sin procedencia). Es el efecto de Zhao et al. (ISSTA 2026) medido en Oracle: la cifra de mutación dice que el corpus distingue la medida de sus variantes, no que atrape defectos reales. Resultados en resultados/*.json. Próximo: que oracle test lo diga junto a la mutación.
