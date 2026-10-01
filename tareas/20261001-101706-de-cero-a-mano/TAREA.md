# de-cero se puede hacer a mano: sin python -c ni banderas de git que sólo necesita el test

- ESTADO: CERRADA
- PRIORIDAD: 81
- ETIQUETAS: 

### Nota (2026-10-01 10:17:06 UTC)

Medido el 2026-10-01: tres python3 -c (aflojar y devolver el umbral; sacar los tiros de la partida) y un git -c user.name=… -c user.email=… commit que sólo existen porque el test de la guía no tiene editor ni identidad de git. Qué: que cada paso sea algo que una persona hace con su editor y su terminal (un archivo entero para pegar en vez de un python -c; git init/add/commit simples, con la identidad la pone el corredor de la guía por variables de entorno), y que el test siga reproduciendo la guía entera. Encargado a Codex.

### Nota (2026-10-01 10:28:10 UTC)

Reemplacé los tres python3 -c de docs/de-cero.md por archivos enteros: sin-tiros.json incluido desde el ejemplo y variantes completa/aflojada de la medida; dejé git init, git add . y git commit -m base. tools/guia.py fija identidad por entorno y restringe los comandos Git a esos tres. La guía se reconstruyó sin salidas viejas; la suite completa pasó (2250 tests).

### Nota (2026-10-01 10:33:24 UTC)

Verificación final: python3 tools/guia.py --escribir (0 salidas actualizadas), python3 tools/sitio.py --escribir (sin páginas pendientes), python3 -m unittest discover -s tests (2250 tests, OK), python3 tools/oracle.py test (VEREDICTO: VERDE; mutación de código salteada). No se hizo commit.

## Próximo paso

Revisar el diff de esta tarea para su eventual versionado; no queda implementación pendiente.
