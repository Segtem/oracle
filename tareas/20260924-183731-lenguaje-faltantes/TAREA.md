# Faltan formas que un catálogo real ya necesita: contar distintos por grupo, una relación vacía en un caso, la división

- ESTADO: ABIERTA
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

## Próximo paso

La medición del punto 1.
