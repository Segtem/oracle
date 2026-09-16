# 0.19.0 declaró un equivalente que la regla del proyecto manda borrar

- ESTADO: CERRADA
- PRIORIDAD: 45
- ETIQUETAS: oracle, mutacion

En el corte 0.19.0 se declaró en `equivalentes.json` `tools/tareas_consulta.py:240:42:constante`
(`NodoCualquiera(columna=0)` de la consulta vacía: nada lee esa columna). `RELEVO.md` («Lo que aprendí»)
dice: **un equivalente genuino se borra, no se declara** — anotarlo acepta para siempre un mutante que
nadie puede matar; sacar el constructo lo elimina. Además el id es posicional y se vence con cualquier
edición de arriba.

A hacer: quitar la constante (p. ej. que la columna de `NodoCualquiera` no se pase o se derive), borrar
la entrada de `equivalentes.json` y confirmar con una ronda de `tools/tareas_consulta.py`.
