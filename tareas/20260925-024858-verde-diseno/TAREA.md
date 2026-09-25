# Cuatro preguntas de diseño sobre verdes que podrían no medir: sombra y sin evidencia, macros sin requiere, agregados vacíos y medidas no aplicadas

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: oracle, diseno, flaqueza


## Qué hacer

`auditoria-verde` (HALLAZGOS.md 3, 4, 5 y 6) deja cuatro preguntas que no son defectos comprobados sino
decisiones: (3) una sombra perdona también un `SIN EVIDENCIA`; (4) las macros base `ninguno`, `peor` y
`ninguno-par` no emiten `requiere`; (5) los agregados sobre cero filas dan 0 (lo dice la
especificación); (6) las medidas propias que no se aplicaron se listan pero no invalidan el
veredicto. Para cada una: qué pasa hoy (con archivo:línea y, si se puede, el caso del corpus que lo
muestra), qué alternativas hay, qué rompería cada una en Oracle, Jam y LyraGASP, y una recomendación
alineada con el «fail-closed» del proyecto. Brian decide. En `ANALISIS.md`.

## Próximo paso

El análisis.
