# Oracle

Trabajá en español.

## Protocolo de tareas y relevo

- Para retomar: `oracle tarea listar` muestra las abiertas por prioridad; `oracle tarea ver <id>` da el contexto.
- Desde este repo también se puede usar `python3 tools/cli.py tarea …`.
- La tarea es la fuente de verdad: qué se pidió, qué se hizo y cuál es el próximo paso.
- Registrá avances, evidencia y bloqueos con `oracle tarea anotar <id> "…"`.
- Todo pendiente nuevo va a una tarea: `oracle tarea nueva "<título>" --sufijo <corto>`.
- Al dejar el trabajo, actualizá una única sección `## Próximo paso` al final del cuerpo de `TAREA.md`.
- Escribí allí la acción concreta para continuar; reemplazá el paso anterior, no acumules secciones.
- Si hay un bloqueo, anotá su causa y qué falta para destrabarlo en esa misma tarea.
- Nunca dejes el relevo en un `.md` suelto ni dependas de recordar una conversación.
- Commits: `<ID>: resumen`; cierre: `<ID>: done`, con la tarea marcada CERRADA.
