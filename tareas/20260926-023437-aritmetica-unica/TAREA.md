# a + 1 y mas(a, 1) son dos maneras de escribir lo mismo: el impresor tiene que usar sólo la infija

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 02:34:37 UTC)

2026-09-26, parte de una-sintaxis. Desde la sintaxis 0.7 el lector acepta + - * y los traduce a las escalares mas/menos/por, pero el impresor conserva las llamadas funcionales, así que la superficie tiene dos escrituras de la misma suma (quedan 5 usos de mas/menos/por en catálogos). Hacer que el impresor imprima + - * con los paréntesis mínimos por precedencia, convertir los 5 usos, y que la ida y vuelta siga dando el mismo árbol (la forma canónica no cambia: sigue siendo ["mas", a, b]). Las llamadas funcionales se siguen LEYENDO (compatibilidad) pero no se imprimen ni se enseñan.
