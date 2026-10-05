# Aceptar --con repetible y rechazar relaciones repetidas entre archivos de hechos

- ESTADO: ABIERTA
- PRIORIDAD: 30
- ETIQUETAS: factory, consumidor


## Objetivo

Lo pide Factory, por el piloto con agentes del 2026-10-05 (`~/Dev/factory`, tarea `20261004-121432-coordinar-dos`, `piloto-agentes-01/piloto.md`, fricción 1). Un candidato integrado tiene un sensor por frente, y `oracle juzgar` y `oracle cobertura` aceptan un solo `--con`.

- `--con` repetible en `juzgar` y en `cobertura`, combinando las relaciones.
- Error explícito si dos archivos aportan la misma relación: es un solapamiento de interfaz entre frentes que Git no ve (la medida de un frente cuenta filas del otro).
