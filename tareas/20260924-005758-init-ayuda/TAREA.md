# oracle init --help crea un proyecto en una carpeta llamada --help en vez de mostrar la ayuda

- ESTADO: CERRADA
- PRIORIDAD: 65
- ETIQUETAS: oracle, cli, ergonomia


## Qué pasó

2026-09-23, al armar `~/Dev/commander` con Oracle 0.28.0 de PyPI: `oracle init --help` respondió
«Proyecto Oracle inicializado en …/--help» y creó `catalogos/`, `corpus/`, `diferencial/` y
`oracle.json` dentro de una carpeta `--help`. `oracle tarea nueva --help` sí muestra la ayuda: el
defecto es del parser de `init`, que toma cualquier argumento como ruta.

### Nota (2026-09-24 01:05:49 UTC)

Reproducción: el test nuevo de ayuda en posición de ruta falló en 24 variantes antes del cambio. Se corrigieron init, proyecto init, biblioteca nueva/verificar/listar, medida revisar/probar/expandir, caso nuevo y los atajos revisar/expandir/convertir mediante el despacho existente. init también rechaza opciones que empiezan con - y --proyecto sin valor válido. Verificación: 2430 tests en verde con python3 -m unittest discover -s tests; git diff --check limpio. No hay ids de tools/cli.py ni tests/test_cli.py en equivalentes.json.

## Próximo paso

Al integrar este worktree, revisar el diff y registrar el commit cuando `.git` permita escritura.
