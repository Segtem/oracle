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
   `## Próximo paso

Claude revisa el inventario de Jam: `oracle tarea listar` y `oracle tarea ver <id>` desde
`/home/workstation/Dev/jam`. Los commits son c40fc74 y f2ba91f; quedaron 57 tareas abiertas
y la implantación cerrada. Revisar especialmente las propuestas históricas marcadas «revisar»
y los gestos sin confirmación de Brian. La vigencia del editor tiene su propia tarea.
Confirmar esta nota en Oracle con `20260919-134424-tareas-jam: inventario` si aún no figura
en el historial; incluir sólo esta tarea, sin cambios ajenos. No hacer push.
Claude decide el cierre de esta tarea después de revisar; Codex la deja ABIERTA.
