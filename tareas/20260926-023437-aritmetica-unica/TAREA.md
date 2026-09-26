# a + 1 y mas(a, 1) son dos maneras de escribir lo mismo: el impresor tiene que usar sólo la infija

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 02:34:37 UTC)

2026-09-26, parte de una-sintaxis. Desde la sintaxis 0.7 el lector acepta + - * y los traduce a las escalares mas/menos/por, pero el impresor conserva las llamadas funcionales, así que la superficie tiene dos escrituras de la misma suma (quedan 5 usos de mas/menos/por en catálogos). Hacer que el impresor imprima + - * con los paréntesis mínimos por precedencia, convertir los 5 usos, y que la ida y vuelta siga dando el mismo árbol (la forma canónica no cambia: sigue siendo ["mas", a, b]). Las llamadas funcionales se siguen LEYENDO (compatibilidad) pero no se imprimen ni se enseñan.

### Nota (2026-09-26 03:21:37 UTC)

Impresor aritmético: mas/menos/por binarios salen como +, - y * con paréntesis según precedencia y asociación; el lector funcional sigue aceptado y la forma canónica no cambia. Convertí las dos llamadas funcionales aún presentes en catálogos activos y la del tutorial; el manual y el error de operadores no muestran mas/menos/por como escritura. Agregué pruebas de árboles anidados e ida y vuelta. Quité de equivalentes.json el sitio prec = 4 → 5: con la nueva precedencia aritmética ya no es equivalente. Ejecuté suite completa: 2589 pruebas, OK; python3 tools/guia.py: OK, 0 salidas actualizadas; python3 tools/sitio.py --escribir: regeneró tutorial-practico.html; python3 tools/cifras.py --actualizar: actualizó README.md; python3 tools/cli.py test --rapido: VERDE. No ejecuté mutación por el límite del sandbox. Sin commits; tarea abierta.

## Próximo paso

Claude: correr la mutación fuera de este sandbox sobre los cambios de aritmetica-unica, revisar los sobrevivientes y registrar el resultado en esta tarea. Mantenerla abierta y sin commits hasta esa revisión.
