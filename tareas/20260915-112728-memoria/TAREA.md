# mutar_codigo no limita la memoria de los mutantes

- ESTADO: ABIERTA
- PRIORIDAD: 55
- ETIQUETAS: oracle, bug, mutacion


## Qué pasa

`tools/mutar_codigo.py` limita el tiempo (`--timeout`) y la salida (`--limite-salida-kb`) de cada
mutante, pero no su memoria. Medido el 2026-09-15 al mutar `tools/tareas_consulta.py` para 0.19.0: el
mutante `not in` → `in` de la línea 65 deja a `tokenizar` sin avanzar y agrega `Token("", i)` sin fin.
Hasta el timeout de 300 s se come la RAM de la máquina; el sistema mató la ronda dos veces, y con
ella procesos ajenos.

La ronda de 0.19.0 se corrió con `ulimit -v 4000000` desde afuera: el mutante muere con `MemoryError`,
que es un fallo de tests y cuenta como muerto.

## Qué se espera

- El arnés pone un tope de memoria a cada ejecución de tests de un mutante (p. ej.
  `resource.setrlimit(RLIMIT_AS)` en el hijo), configurable como el timeout.
- Un mutante que excede el tope es un mutante muerto, no una ronda inconclusa; un test lo fija.
- La baseline corre con el mismo tope, para que un tope demasiado bajo se vea antes de mutar.
- El job `mutacion-codigo` de CI usa el tope.
