# Relevo

El trabajo de Oracle se lleva en su propio tracker, no en este archivo. Para tomar el turno:

```bash
oracle tarea listar                      # lo abierto, por prioridad
oracle tarea listar ":metalenguaje y prioridad desde 70"
oracle tarea ver <id>                    # el detalle de una
```

Cada cambio nace como tarea (`oracle tarea nueva <título> --sufijo <corto>`), cada commit de ese
trabajo empieza con su ID (`<ID>: resumen`) y el que la cierra es `<ID>: done`. La guía del tracker
está en [`docs/12-tareas.md`](docs/12-tareas.md).

Dónde está lo demás:

- **en qué versiones está el lenguaje**: `ESPECIFICACION.md` §0, primera línea;
- **qué cambió en cada corte**: `NOTAS-DE-RELEASE.md`;
- **por qué se decidió lo que se decidió**: los `DECISION-*.md` y los `PLAN-*.md` de la raíz;
- **cómo se verificó un corte**: `estudios/<versión>-<tarea>/`.

Este archivo era un relevo fechado, escrito a mano antes de que existiera el tracker: describía el
corte 0.8.1 del 2026-09-08 y sus deudas vivas: todas están hoy como tareas. Se conserva como
[`estudios/RELEVO-2026-09-08.md`](estudios/RELEVO-2026-09-08.md), porque lo que aprendió esa sesión
sigue valiendo aunque las cifras hayan envejecido.
