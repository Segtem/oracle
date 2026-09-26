# Los catálogos, casos y relaciones de Oracle y de sus ejemplos tienen que estar todos en superficie

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 02:34:37 UTC)

2026-09-26, parte de una-sintaxis, después de convertir-lote y relaciones-superficie. Hoy en Oracle quedan en JSON: 1 medida de catalogos/, 2 casos de corpus/ y las 12 relaciones de relaciones/, más lo que haya en ejemplo/*. Convertirlos con oracle convertir --a-superficie; lo que no sea convertible se informa y se decide uno por uno. Los fixtures de diferencial/ NO se convierten: son datos generados, no escritura. oracle test VERDE y las guías sin salidas viejas.

### Nota (2026-09-26 03:31:18 UTC)

2026-09-26, Claude: hecho con oracle convertir --a-superficie --escribir sobre catalogos (1), corpus (2), perfiles/python (1) y ejemplo/ (25); relaciones/ ya lo había hecho relaciones-superficie. Quedan fuera a propósito: vault-kb/estudios y tareas/ (historia; algunos ni cargan con el lenguaje de hoy) y build/ (ignorado). Los tests que exigían que el catálogo y el corpus reales tuvieran JSON «para ejercitar los dos lectores» ahora exigen que estén todo en superficie, y ejercitan el lector JSON con un archivo temporal generado desde una medida y un caso reales. Suite 2589 OK, guías sin salidas viejas, test --rapido VERDE.
