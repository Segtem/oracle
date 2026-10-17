# Aceptar --con repetible y rechazar relaciones repetidas entre archivos de hechos

- ESTADO: CERRADA
- PRIORIDAD: 30
- ETIQUETAS: factory, consumidor


## Objetivo

Lo pide Factory, por el piloto con agentes del 2026-10-05 (`~/Dev/factory`, tarea `20261004-121432-coordinar-dos`, `piloto-agentes-01/piloto.md`, fricción 1). Un candidato integrado tiene un sensor por frente, y `oracle juzgar` y `oracle cobertura` aceptan un solo `--con`.

- `--con` repetible en `juzgar` y en `cobertura`, combinando las relaciones.
- Error explícito si dos archivos aportan la misma relación: es un solapamiento de interfaz entre frentes que Git no ve (la medida de un frente cuenta filas del otro).

### Nota (2026-10-16 21:25:13 UTC)

Hecho en 96f6a26: _leer_evidencias combina los archivos de --con (juzgar y cobertura); dos archivos con la misma relación, o el mismo archivo dos veces (también como sub/../a.json), salen con 2 (juzgar) o 1 (cobertura) nombrando la relación y los dos archivos. Pruebas en tests/test_juzgar_varios.py; test_con_repetido pasa a exigir el error por relación repetida. Suite 2263 OK; mutación --bajo de juzgar, cobertura y cli: 22 de 22 muertos. Falta: release 0.39.0 y que Factory lo use (tarea hechos-varios de Factory).

### Nota (2026-10-17 11:34:01 UTC)

Publicado en 0.39.0 (tag v0.39.0, PyPI 2026-10-17) y usado por Oracle Factory desde el cambio 20261017-023151-hechos-varios (merge 8cbf0df en Segtem/oracle-factory).
