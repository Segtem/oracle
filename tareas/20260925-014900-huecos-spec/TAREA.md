# La especificación puede tener más preguntas sin contestar que las tres que encontró el tercer autor

- ESTADO: ABIERTA
- PRIORIDAD: 78
- ETIQUETAS: oracle, especificacion, flaqueza


## Por qué

El tercer autor (tarea `codex`, 2026-09-24) implementó el álgebra 0.8 sólo con `ESPECIFICACION.md` y
encontró tres preguntas que el texto no contestaba: dónde va `ambito`, la aridad de `y`/`o` y
`min`/`max` sobre booleanos. Las encontró por los desacuerdos del diferencial, o sea, sólo en lo que
los mundos y el corpus ejercitan. Lo que ninguno ejercita puede tener más huecos.

## Qué hacer

Leer `ESPECIFICACION.md` como alguien que va a implementarla sin ver el núcleo y listar cada
pregunta que el texto no contesta. Para cada una: el párrafo que la deja abierta, qué hace
`nucleo/` (archivo:línea) y si la referencia (`diferencial/referencia/evaluador.py`) hace lo mismo.
Las que el núcleo y la referencia resuelven igual se escriben en la especificación con lo que ya
hacen; las que resuelven distinto son defectos; las que ninguno resuelve son decisiones de Brian.
Descartar lo que no se pueda sostener con cita.

## Próximo paso

La lectura y la lista.
