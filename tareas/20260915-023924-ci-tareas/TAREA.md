# CI no corre cuando sólo cambia tareas/

- ESTADO: CERRADA
- PRIORIDAD: 65
- ETIQUETAS: oracle, ci, bug

`verificar.yml` ignora `**.md` en `push` y `pull_request`, y todo el tracker es Markdown
(`tareas/*/TAREA.md`). El paso que agregó 0.18.0 —juzgar el `tareas/` de Oracle con las políticas
de seguimiento— no corre cuando cambia sólo el tracker: pasó con el push de `20260915-023750-tql`,
que no disparó ninguna corrida. Un enlace roto en una tarea recién se vería con el próximo push de
código.

Además `concurrency` con `cancel-in-progress: true` es por rama: un push a `main` cancela la corrida
manual de mutación en curso, que tarda horas.

A decidir: excluir `tareas/**` del filtro (comprobar primero cómo combina GitHub `paths-ignore` con
un patrón `!`), o un workflow chico propio del tracker que no cancele la mutación. Medir con un push
que sólo toque `tareas/`.
