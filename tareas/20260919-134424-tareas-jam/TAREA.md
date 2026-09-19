# Jam organiza su trabajo pendiente en su propio tracker

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: jam, proceso, tracker


## Por qué

Brian (2026-09-19): «debemos organizar las tareas de LyraGASP y Jam usando oracle tatr y que queden
en el repo; no podemos depender de la memoria de Claude o de Codex, ni de README.md o *.md dando
vueltas por ahí». Ver [`20260919-134424-relevo`](../20260919-134424-relevo/TAREA.md) para el
protocolo.

## Qué hacer (Codex), en `/home/workstation/Dev/jam`

1. `oracle tarea init` en la raíz de Jam (la herramienta global `oracle` está en 0.27.0).
2. **Inventario del trabajo pendiente**, leyendo lo que hoy lo guarda: `RELEVO.md`, `AGENTS.md`,
   `docs/`, roadmaps, TODOs en `.md`, notas de estudio, y `git log` reciente. Por cada trabajo
   pendiente real, una tarea: `oracle tarea nueva "<título que diga el problema>" --prioridad <n>
   --etiqueta <…> --sufijo <corto>`, con un cuerpo que diga qué se sabe, dónde está la evidencia y
   `## Próximo paso`. No inventes trabajo: si algo es dudoso, una sola tarea «revisar X» con la cita.
3. **El arranque**: en el archivo de instrucciones del repo (`AGENTS.md` / `CLAUDE.md`), una sección
   corta que diga que el trabajo se retoma con `oracle tarea listar` y `oracle tarea ver <id>`, y
   que un relevo se deja anotando la tarea, no escribiendo otro `.md`.
4. Verificá con `oracle tarea revisar` y `oracle tarea hechos --git` que el tracker quede sano.

Jam tiene `tools/relevo.py`, `RELEVO.md` y `AGENTS.md` (un solo archivo para los dos agentes). El vault (`Vault-kb/`) es documentación, no trabajo pendiente: no lo migres, sólo enlazá desde una tarea si hace falta.

Commits en Jam, cada uno empezando con el ID de la tarea de Jam que corresponda (la primera:
«<id>: el tracker del proyecto»). **No hagas push.** Al terminar, anotá en ESTA tarea de Oracle
(`cd /home/workstation/Dev/oracle && python3 tools/cli.py tarea anotar 20260919-134424-tareas-jam
"…"`) cuántas tareas quedaron, las cinco más prioritarias y qué no pudiste decidir, y commiteá esa
nota en Oracle como `20260919-134424-tareas-jam: inventario`. No la cierres: la cierra Claude después
de revisar.

## Próximo paso

Codex lee esta tarea y la hace.
