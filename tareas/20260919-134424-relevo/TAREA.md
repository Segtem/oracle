# Retomar el trabajo tiene que ser leer una tarea, no recordar una conversación

- ESTADO: ABIERTA
- PRIORIDAD: 90
- ETIQUETAS: oracle, proceso, relevo


## Por qué

Brian (2026-09-19): «me desmoraliza tener que andar pensando en qué charla estábamos trabajando para
continuar; quiero algo más directo y simple, como decirle al modelo *leé la tarea y continuemos*».
Hoy el estado vive repartido entre la memoria de Claude, la de Codex, `RELEVO.md`,
`RELEVO-PARA-CODEX.md`, `PLAN-*.md` y otros `.md` sueltos. Eso termina siendo desastroso: nadie sabe
cuál está vigente. Ahora hay un tracker (`oracle tarea`) y **se usa sí o sí**.

## Qué hacer (Codex)

1. **El protocolo, en un solo lugar y corto.** En `AGENTS.md` de Oracle (crealo si no existe; es el
   archivo que leen Codex y agy) y en el `CLAUDE.md` del repo si existe, una sección de ≤ 15 líneas:
   - para retomar: `oracle tarea listar` (abiertas por prioridad) y `oracle tarea ver <id>`;
   - la tarea es la fuente de verdad: qué se pidió, qué se hizo (notas con `oracle tarea anotar`) y
     **cuál es el próximo paso**;
   - al dejar el trabajo, anotar en la tarea el próximo paso concreto; nunca en un `.md` suelto;
   - commits `<ID>: resumen`, cierre `<ID>: done`.
2. **Una forma fija para el próximo paso.** Una sección `## Próximo paso` al final del cuerpo de la
   tarea, que se actualiza (no se acumula). Si hace falta que `oracle tarea ver` la destaque, eso es
   otra tarea de Oracle, no se hace acá.
3. **Vaciar los relevos sueltos de Oracle.** Leé `RELEVO.md`, `RELEVO-PARA-CODEX.md` y
   `RELEVO-2026-09-10.md`. Todo lo que sea trabajo pendiente y no tenga tarea abierta, pasa a una
   tarea (`oracle tarea nueva … --sufijo <corto>`). Después esos archivos quedan con una sola línea
   que diga que el relevo ahora es el tracker, o se borran si nada los enlaza (`git grep`).
4. Verificá: `python3 tools/cli.py tarea hechos --git > /tmp/h.json && python3 tools/cli.py juzgar
   --proyecto ejemplo/seguimiento-tareas --con /tmp/h.json` tiene que quedar verde, y la suite
   (`python3 -B -m unittest discover -s tests -t . -q`) también.

Commits en Oracle con `20260919-134424-relevo: …` y el cierre `20260919-134424-relevo: done`.
**No hagas push.** No toques LyraGASP ni Jam: tienen sus propias tareas
(`20260919-134424-tareas-lyra`, `20260919-134424-tareas-jam`).

## Próximo paso

Codex lee esta tarea y la hace.
