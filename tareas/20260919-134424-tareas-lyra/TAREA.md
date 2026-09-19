# LyraGASP organiza su trabajo pendiente en su propio tracker

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: lyragasp, proceso, tracker


## Por qué

Brian (2026-09-19): «debemos organizar las tareas de LyraGASP y Jam usando oracle tatr y que queden
en el repo; no podemos depender de la memoria de Claude o de Codex, ni de README.md o *.md dando
vueltas por ahí». Ver [`20260919-134424-relevo`](../20260919-134424-relevo/TAREA.md) para el
protocolo.

## Qué hacer (Codex), en `/home/workstation/Dev/games/unreal/LyraGASP`

1. `oracle tarea init` en la raíz de LyraGASP (la herramienta global `oracle` está en 0.27.0).
2. **Inventario del trabajo pendiente**, leyendo lo que hoy lo guarda: `RELEVO.md`, `AGENTS.md`,
   `docs/`, roadmaps, TODOs en `.md`, notas de estudio, y `git log` reciente. Por cada trabajo
   pendiente real, una tarea: `oracle tarea nueva "<título que diga el problema>" --prioridad <n>
   --etiqueta <…> --sufijo <corto>`, con un cuerpo que diga qué se sabe, dónde está la evidencia y
   `## Próximo paso`. No inventes trabajo: si algo es dudoso, una sola tarea «revisar X» con la cita.
3. **El arranque**: en el archivo de instrucciones del repo (`AGENTS.md` / `CLAUDE.md`), una sección
   corta que diga que el trabajo se retoma con `oracle tarea listar` y `oracle tarea ver <id>`, y
   que un relevo se deja anotando la tarea, no escribiendo otro `.md`.
4. Verificá con `oracle tarea revisar` y `oracle tarea hechos --git` que el tracker quede sano.

⚠ LyraGASP tiene trabajo de Brian SIN COMMITEAR (uassets, C++, `RELEVO.md`, `investigaciones/`, un caso del corpus nuevo). **No lo toques, no lo agregues a ningún commit**: `git add` sólo de `tareas/` y del archivo de instrucciones que edites. Si `RELEVO.md` está modificado sin commitear, leelo pero no lo edites; anotá en esta tarea lo que habría que cambiar.

Commits en LyraGASP, cada uno empezando con el ID de la tarea de LyraGASP que corresponda (la primera:
«<id>: el tracker del proyecto»). **No hagas push.** Al terminar, anotá en ESTA tarea de Oracle
(`cd /home/workstation/Dev/oracle && python3 tools/cli.py tarea anotar 20260919-134424-tareas-lyra
"…"`) cuántas tareas quedaron, las cinco más prioritarias y qué no pudiste decidir, y commiteá esa
nota en Oracle como `20260919-134424-tareas-lyra: inventario`. No la cierres: la cierra Claude después
de revisar.

## Próximo paso

Codex lee esta tarea y la hace.
