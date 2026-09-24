# Un predicado que no es booleano pasa por verdadero en el núcleo y es error en la referencia

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, metalenguaje, diferencial


Encontrado el 2026-09-16 al sondear la referencia re-derivada contra 0.8
(`vault-kb/estudios/0.26.0-antijunta/referencia/`). `["donde", ["campo", "x", "k"]]` con `k` numérico: el
núcleo lo evalúa por verdad de Python (un 2 pasa, un 0 no), la referencia levanta
`ErrorDeAlgebra` porque decidió que un predicado tiene que dar `bool` (`DECISIONES.md`, sección de
`requiere` con condición). Es anterior a 0.8 y `sin` lo hereda igual.

La especificación (§2, §3) dice «expresión booleana» y no dice qué pasa con otra cosa. La
coerción silenciosa es la forma de falso verde que el lenguaje persigue: un campo numérico usado
por error como predicado filtra sin avisar. A decidir: exigir `bool` en `donde`, `sin` y
`requiere` (validación estática donde se pueda, y en la evaluación), con la sección de la
especificación que lo diga. Puede cambiar colores → MENOR.

### Nota (2026-09-16 20:34:27 UTC)

2026-09-16: no se implementa sin decisión del dueño: exigir bool cambia la semántica de donde, que ya existía, y por §0 eso sube la MAYOR del álgebra (1.0). Antes de decidir conviene medir cuántas medidas de Oracle, LyraGASP y Jam usan un predicado no booleano.
