# oracle init --help crea un proyecto en una carpeta llamada --help en vez de mostrar la ayuda

- ESTADO: ABIERTA
- PRIORIDAD: 65
- ETIQUETAS: oracle, cli, ergonomia


## Qué pasó

2026-09-23, al armar `~/Dev/commander` con Oracle 0.28.0 de PyPI: `oracle init --help` respondió
«Proyecto Oracle inicializado en …/--help» y creó `catalogos/`, `corpus/`, `diferencial/` y
`oracle.json` dentro de una carpeta `--help`. `oracle tarea nueva --help` sí muestra la ayuda: el
defecto es del parser de `init`, que toma cualquier argumento como ruta.

## Próximo paso

Que `init` use argparse como los demás verbos (o rechace una ruta que empiece con `-`), con un test
que falle hoy. Revisar si otros verbos con ruta posicional tienen el mismo defecto.
