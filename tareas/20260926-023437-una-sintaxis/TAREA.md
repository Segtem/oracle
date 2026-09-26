# Una sola sintaxis para escribir Oracle: la superficie; el JSON canónico queda como formato interno

- ESTADO: ABIERTA
- PRIORIDAD: 90
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 02:34:37 UTC)

2026-09-26, DECISIÓN de Brian: una sola sintaxis. Hoy conviven cuatro maneras de escribir: la superficie (.oracle/.caso: Oracle, 58 medidas y 210 casos), el JSON canónico, el JSON con macros escrito a mano (Jam 41 medidas y 35 casos; LyraGASP 29 y 194) y, en expresiones, a + 1 junto a mas(a, 1) (5 usos). Las relaciones sólo existen en JSON. Un LLM aprende de ejemplos y ve dos idiomas. Qué queda: la SUPERFICIE es la única forma de escribir medidas, casos y relaciones; el JSON canónico sigue siendo el formato interno y de intercambio (es lo que muta la mutación, lo que mide L2 y lo que guarda el diferencial) y Oracle lo sigue leyendo, pero nadie lo escribe a mano. Subtareas: convertir-lote, relaciones-superficie, aritmetica-unica, oracle-a-superficie, meta-una-sintaxis, docs-una-sintaxis; y en los consumidores, una-sintaxis en Jam y en LyraGASP. Terminado cuando: los tres repos no tienen medidas, casos ni relaciones en JSON escrito a mano; la documentación sólo enseña la superficie (el JSON aparece únicamente donde se explica la forma canónica); y una medida meta lo vigila. Sale con sintaxis 0.8 (junto con espera: sin_evidencia) y una menor de distribución.
