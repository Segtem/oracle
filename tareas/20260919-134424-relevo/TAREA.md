# Retomar el trabajo tiene que ser leer una tarea, no recordar una conversación

- ESTADO: CERRADA
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

### Nota (2026-09-19 13:56:17 UTC)

Inventario de los tres relevos: RELEVO.md ya remitía al tracker (migración 20260915-155111-relevo). RELEVO-2026-09-10.md y PLAN-0.14-LO-QUE-FALTA.md confirman cerrados la custodia de metamórficas (242/242), el costo del CLI (509/509 en 452,61 s), la optimización del validador, los diagnósticos, el estudio de autenticidad y el plan de observación de Jam. El corte 0.15.0 fue autorizado y está en NOTAS-DE-RELEASE.md; no queda una propuesta de versión pendiente. Los 94 orígenes son deuda irrecuperable, no trabajo pendiente. La observación de consumidores (incluido el caso 018 de Jam y la procedencia de LyraGASP) corresponde al inventario ya abierto en 20260919-134424-tareas-jam y 20260919-134424-tareas-lyra. La accesibilidad tiene trabajo concreto en 20260919-135054-primer-valor y 20260919-135054-test-alcance; las direcciones generales no justifican inventar tareas. No apareció otro pendiente real sin tarea. No se tocaron repos consumidores.

### Nota (2026-09-19 13:56:18 UTC)

Creado AGENTS.md con protocolo de 13 líneas: fuente de verdad, notas, sección única Próximo paso que se reemplaza al final del cuerpo y commits con ID. No existe CLAUDE.md dentro del repo. Los tres relevos quedan en una línea; git grep confirmó referencias desde planes, tareas, estudios y ejemplos, por lo que se conservan sus rutas. La historia y evidencia de los cierres permanecen en Git y estudios. Los cambios ajenos encontrados al iniciar quedan fuera de este trabajo.

### Nota (2026-09-19 13:56:47 UTC)

Bloqueo de entorno: git add AGENTS.md RELEVO.md RELEVO-PARA-CODEX.md RELEVO-2026-09-10.md tareas/20260919-134424-relevo/TAREA.md falló con fatal: Unable to create .git/index.lock: Read-only file system. No se pudo crear ningún commit y no se hizo push. La verificación exacta tarea hechos --git > /tmp/h.json seguida de juzgar --proyecto ejemplo/seguimiento-tareas --con /tmp/h.json salió 1: archivos_confirmados_sin_cambios = 5, por esta tarea y cambios preexistentes en aura, naval-pm, primer-valor y test-alcance. Las otras medidas obligatorias pasan; los cuatro cierres históricos sin commit siguen en sombra dentro de su cota. No se agregan ni confirman cambios ajenos para ocultar ese rojo. tarea revisar: 48 tareas válidas. git diff --check: OK.

### Nota (2026-09-19 13:57:50 UTC)

Suite requerida completada: python3 -B -m unittest discover -s tests -t . -q salió 0, 2364 tests en 72,137 s, OK. La implementación documental está terminada; la tarea permanece ABIERTA por los commits imposibles en este entorno y el seguimiento Git pendiente. Sin push.

## Próximo paso

Retomar en un entorno con escritura habilitada en `.git`. Confirmar únicamente `AGENTS.md`,
los tres `RELEVO*.md` y esta tarea con el prefijo `20260919-134424-relevo:`.
Esperar a que los responsables confirmen los cambios ajenos de las tareas aura, naval-pm,
primer-valor y test-alcance; no incluirlos en este commit. Repetir
`python3 tools/cli.py tarea hechos --git > /tmp/h.json && python3 tools/cli.py juzgar --proyecto ejemplo/seguimiento-tareas --con /tmp/h.json`.
Cuando el seguimiento quede verde y la suite esté verificada, registrar el resultado,
marcar esta tarea CERRADA, reemplazar este paso por «Sin pendientes» y crear el commit
`20260919-134424-relevo: done`. Comprobar de nuevo el seguimiento tras el cierre. No hacer push.
