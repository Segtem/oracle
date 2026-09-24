# Faltan formas que un catálogo real ya necesita: contar distintos por grupo, una relación vacía en un caso, la división

- ESTADO: CERRADA
- PRIORIDAD: 76
- ETIQUETAS: oracle, metalenguaje, ergonomia


## Por qué

[la auditoría](../20260924-174258-auditoria/AUDITORIA.md) §2.4 y `20260923-120207-ergonomia/VERIFICACION.md`: contar distintos exige un doble `agrupar`
(2.1); `.caso` no puede escribir una relación vacía; no existe `/`, que es lo primero que un LLM
escribe para una proporción. La regla del proyecto es no agregar un operador hasta que una segunda
medida lo necesite.

## Qué hacer

1. **Medir primero**: en los catálogos de Oracle, Jam, LyraGASP y commander, cuántas medidas usan el
   doble `agrupar` para contar distintos, cuántos casos rodean la relación vacía y cuántas medidas
   calculan una proporción con un rodeo. Con archivo:línea.
2. Para cada forma con dos o más usos reales, una propuesta de azúcar de la superficie (como la
   aritmética de 0.30) y qué versión sube.

**Quién:** agy (la medición); Codex (la implementación).

## Avance

- Se completó la medición del punto 1 en [MEDICION.md](MEDICION.md), con citas `archivo:línea` sobre los catálogos de Oracle (base y ejemplos en worktree), Jam y LyraGASP (copiados en `consumidores/`). Se constató que `commander` no estaba copiado en `consumidores/` y no fue leído.
- Hallazgos de la medición:
  1. **Doble `agrupar` para contar distintos**: 0 medidas reales en producción (sólo 1 caso didáctico en `GUIA22.md:794-822`).
  2. **Casos que rodean la relación vacía**: 0 casos reales en producción (sólo 1 caso didáctico en `GUIA22.md:868-875`). La superficie `.caso` ya soporta relaciones vacías (`nucleo/caso.py:178-179`, `ejemplo/primer-valor/corpus/colocacion/006-sin-celdas.caso:14`).
  3. **Medidas con rodeo de proporción por falta de `/`**: 0 medidas en los catálogos examinados.
- Conclusión: ninguna de las formas cumple la regla del proyecto de $\ge 2$ usos reales para incorporar azúcar sintáctico o nuevos operadores en este corte.

## Revisión de Claude (2026-09-24)

Verificado: `ejemplo/primer-valor/corpus/colocacion/006-sin-celdas.caso` escribe `celda_ocupada:`
vacía, y en Oracle, Jam y LyraGASP ninguna medida encadena dos `agrupar` (las dos que aparecen con
«agrupar» dos veces lo tienen dentro de un texto). La relación vacía era una fricción ya falsada en
`ergonomia/VERIFICACION.md`, y la auditoría la repitió por error; está corregida allí.

## Próximo paso

Ninguno. Ninguna de las tres formas tiene dos usos reales. `/` queda para cuando una medida calcule
una proporción: hoy los sensores entregan la tasa ya normalizada.
