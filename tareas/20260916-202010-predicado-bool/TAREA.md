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

### Nota (2026-09-24 18:37:31 UTC)

2026-09-24, auditoría (§2.1 y §4.1): es el único falso verde conocido del álgebra y la primera recomendación. Plan: Codex mide cuántas medidas de Oracle, Jam, LyraGASP y commander dependen de que un predicado no booleano pase por verdad de Python, con archivo:línea y el valor que tomaría. Después Brian decide exigir bool, que sube el álgebra a 1.0.

### Nota (2026-09-24 18:45:18 UTC)

Medición completada en MEDICION.md y medir.py, sin modificar nucleo/ ni el lenguaje. Censo: Oracle catalogos/ 59 medidas y 64 predicados; ejemplo/ 11 y 13; Jam 41 y 42; LyraGASP 28 y 28. Una sospecha estática: LyraGASP personaje.ancla_requerida_ausente.json:38, campo a.presente bajo no. Instrumentación en copia: 0 resultados completos no bool en donde/sin/requiere durante corpus y aceptación; 10 valores None en ese operando de no, sin cambio de color por exigir bool al predicado completo. Aceptación pasó en todos; código final 1 de Oracle por cifras README y de Jam/Lyra por procedencia diferencial ausente en estos checkouts. Sin commits. Próximo paso: Brian decide semántica de bool y versionado.

## Próximo paso

Brian revisa `MEDICION.md` y decide si exigir `bool` al resultado completo de `donde` y `sin`, y si el alcance también incluye operandos lógicos como el `None` observado en LyraGASP; después define el versionado correspondiente antes de implementar.

### Nota (2026-09-24 18:53:07 UTC)

2026-09-24, revisión de Claude: la medición se reproduce con las rutas reales de Jam y LyraGASP (medir.py ya no depende de copias). Resultado para decidir: exigir bool al resultado de donde, sin y requiere no cambia el color de ninguna de las 139 medidas propias. Pero hay un caso adentro de un predicado: en LyraGASP personaje.ancla_requerida_ausente hace no(a.presente) con a.presente = None diez veces en su corpus, y no None da verdadero por verdad de Python, que es el mismo falso verde un nivel más adentro. Propuesta para álgebra 1.0: exigir bool también a los operandos de y, o y no; y en LyraGASP, que el sensor emita presente como bool (o la medida lo compare explícito) antes de subir a 1.0.

### Nota (2026-09-25 02:17:57 UTC)

2026-09-24, Brian: se exige bool en donde, sin, requiere y en los operandos de y/o/no; álgebra 1.0. Se implementa en la tarea algebra-10, junto con otras tres decisiones de huecos-spec.
