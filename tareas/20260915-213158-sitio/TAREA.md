# El sitio publicado quedó en 0.8 y no muestra el task tracker

- ESTADO: CERRADA
- PRIORIDAD: 58
- ETIQUETAS: oracle, docs, sitio

Medido el 2026-09-15 sobre https://segtem.github.io/oracle/ (GitHub Pages desde `docs/`), con 0.21.0
publicada:

- La portada (`docs/index.html`) muestra `oracle 0.8.0` y «131 casos»; su último cambio es el corte 0.8.1
  (2026-09-07). Hoy la distribución es 0.21.0, el álgebra 0.7 y el corpus tiene más de 200 casos.
- Sobre el tracker, el sitio sólo tiene una línea generada en `manual.html`, la lista de verbos del CLI
  (`oracle tarea adjuntar · anotar · buscar · cerrar · desetiquetar …`): no dice qué es el tracker, ni la
  forma tatr, ni el lenguaje de consultas (entrado en 0.16.0–0.19.0). La portada no lo nombra. La guía `docs/12-tareas.md` sólo está enlazada desde `docs/README.md` y el README, en
  GitHub; en el sitio se sirve como Markdown crudo (`/12-tareas.md` responde 200 sin convertir) y
  `/12-tareas.html` da 404.
- Las cifras de la portada están escritas a mano: es la deriva que `tools/cifras.py` cerró en el README
  («un número escrito a mano en la prosa es una afirmación sin medida»), y en el sitio sigue abierta.

A hacer: una sección o página del tracker en el sitio (qué es, la forma tatr, el lenguaje de consultas,
enlace a la guía convertida o a GitHub); versión y cifras de la portada generadas o comprobadas por la
misma vía que el README, con un test que falle si envejecen; revisar que las demás páginas no citen
versiones viejas.
