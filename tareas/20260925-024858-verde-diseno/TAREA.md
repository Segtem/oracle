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

## Avance

Se completó el análisis exhaustivo en `ANALISIS.md` de las cuatro decisiones de diseño derivadas de `auditoria-verde` (`tareas/20260925-023140-auditoria-verde/HALLAZGOS.md:72-166`):
1. Sombra y `SIN EVIDENCIA` (`nucleo/medida.py:479-495, 705-707`, `tools/juzgar.py:348`, `corpus/proceso/043-ausencia-total-sale-verde.caso:1-21`). Alternativas, impacto en Jam y LyraGASP, y recomendación fail-closed de no perdonar nunca `sin_evidencia` por sombra.
2. Macros base sin `requiere` (`nucleo/macros/ninguno.oracle:4-12`, `peor.oracle:4-12`, `ninguno-par.oracle:4-14` frente a `ninguno-requiere.oracle:4-13`). Alternativas, preservación del caso de uso de relaciones de infracciones donde `[]` es éxito, e impacto de versionado.
3. Agregados sobre cero filas dando 0 (`nucleo/algebra.py:580-593`, `ESPECIFICACION.md:802-803`, `diferencial/referencia/DECISIONES.md:25-32`). Demostración de por qué levantar error en `max([])` destruiría el funcionamiento de la macro `peor` ante cero transgresiones, y recomendación de preservar la especificación delegando la guarda en `requiere`.
4. Medidas no aplicadas en `juzgar` (`tools/juzgar.py:159-170, 348`, `nucleo/medida.py:710-714`, `tareas/20260916-201124-juzgar-omite/TAREA.md:8-17`). Alternativas, impacto en arquitecturas de CI particionadas en Jam y LyraGASP, y recomendación fail-closed de fallar por defecto en corridas totales exigiendo `--parcial` para ejecuciones modulares.

## Próximo paso

Revisión y decisión por parte de Brian sobre las alternativas recomendadas en `ANALISIS.md`.
