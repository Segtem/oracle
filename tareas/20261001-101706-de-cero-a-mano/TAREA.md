# de-cero se puede hacer a mano: sin python -c ni banderas de git que sólo necesita el test

- ESTADO: ABIERTA
- PRIORIDAD: 81
- ETIQUETAS: 

### Nota (2026-10-01 10:17:06 UTC)

Medido el 2026-10-01: tres python3 -c (aflojar y devolver el umbral; sacar los tiros de la partida) y un git -c user.name=… -c user.email=… commit que sólo existen porque el test de la guía no tiene editor ni identidad de git. Qué: que cada paso sea algo que una persona hace con su editor y su terminal (un archivo entero para pegar en vez de un python -c; git init/add/commit simples, con la identidad la pone el corredor de la guía por variables de entorno), y que el test siga reproduciendo la guía entera. Encargado a Codex.
