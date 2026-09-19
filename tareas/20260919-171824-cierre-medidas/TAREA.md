# Una tarea no puede declarar con qué medidas se cierra, así que cerrarla no se comprueba

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: oracle, tracker, metalenguaje


## Qué pasó

2026-09-19, en LyraGASP: Codex explicó bien que el tracker (`tareas/`) es la cola de trabajo y que
`medidas/` son los contratos, y que una tarea como «dedos deformados» sólo se cierra cuando su
hallazgo tiene una medida que pasa la aceptación. Es la regla del `CLAUDE.md` de LyraGASP («todo
hallazgo que se pueda medir se escribe como medida antes de darlo por cerrado»). Pero hoy ese
vínculo es **prosa**: nada impide cerrar la tarea con la medida inexistente o en rojo.

## Qué hacer

1. Una forma de declarar, en la tarea, las medidas que la cierran (por ejemplo una línea
   `- CIERRA CON: recarga.montage_en_slot_cuerpo_entero, dedos.flexion_digital`), leída por el
   parser del tracker y emitida por `oracle tarea hechos` como relación (`tarea_cierre_medida`:
   tarea, medida).
2. Una política en `ejemplo/seguimiento-tareas` (y para copiar en los consumidores): **ninguna tarea
   cerrada cuyo criterio de cierre nombre una medida que no existe en el catálogo o que no está
   verde en la última aceptación**. Decidir de dónde sale el «está verde»: el tracker no evalúa
   medidas, así que la evidencia tiene que venir de juntar `tarea hechos` con los hechos de la
   aceptación del proyecto, y eso se diseña antes de escribirlo.
3. Una tarea sin `CIERRA CON` sigue siendo válida: no todo trabajo es medible (documentación,
   decisiones). La política sólo mira las que lo declaran.

## Próximo paso

Diseñar cómo se juntan los hechos del tracker con los de la aceptación (punto 2), en un plan corto
dentro de esta tarea, antes de tocar el parser.
