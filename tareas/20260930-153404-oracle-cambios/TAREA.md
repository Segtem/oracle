# oracle cambios también mira los sensores: escalares, relaciones y el código que emite los hechos

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle

### Nota (2026-09-30 15:34:04 UTC)

Por qué: SpecBench (arXiv 2605.21384), EvilGenie (2511.21654) y el Reward Hacking Benchmark (2605.02964) documentan agentes que, en vez de mejorar la solución, cambian lo que se mide: editan el verificador, reescriben scripts de puntaje, cambian configuración. oracle cambios hoy sólo mira el catálogo, el corpus y la sombra; un agente puede aflojar igual cambiando escalares.py, una .relacion o el sensor para que deje de emitir el hecho que ofende.

### Nota (2026-09-30 17:15:24 UTC)

Hecho: oracle cambios avisa escalar cambiada (por AST, función por función; si cambia el código común, todas) y relación cambiada, con las medidas que las usan; vigila los `sensores` que declara oracle.json (rutas relativas al proyecto, pueden salir a ../tools) y dejar de vigilar una ruta es error. Probado contra la historia de LyraGASP: nombra es_cuerpo_entero y su medida. Mutación de tools/cambios.py 87/87. Falta: declarar sensores en LyraGASP y Jam tras el release.

### Nota (2026-09-30 18:28:45 UTC)

Sensores declarados en LyraGASP (ce36032) y Jam (9fda890) con 0.37.0.
