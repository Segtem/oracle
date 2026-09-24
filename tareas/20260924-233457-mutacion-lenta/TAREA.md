# La mutación de código tarda horas por módulo y cada corte espera dos horas

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: oracle, mutacion, flaqueza


## Por qué

En los cortes 0.29.0 y 0.30.0 la mutación de `nucleo/sintaxis.py` (1140 y 1177 mutantes) tardó unas
dos horas, y la de `tools/cli.py` (595) más de una hora. Cada corte espera eso, y una ronda
repetida (los 7 vivos de `cli.py`) suma otra hora. El feedback lento empuja a mutar menos, que es el
defecto que la mutación existe para evitar.

## Qué hacer

1. Medir dónde se va el tiempo: ¿cada mutante corre la suite completa (2440 tests, unos 86 s)? ¿cuánto
   es arranque de proceso, cuánto tests que no tocan el módulo mutado?
2. Proponer la forma más chica que lo baje sin debilitar el criterio de muerte. Por ejemplo: correr
   primero los tests que importan el módulo mutado y la suite entera sólo si ésos no lo matan, o
   cortar en el primer test que falla (`failfast`). Estimar con los logs de
   `tareas/*-corte-029/verificacion/` y `tareas/*-corte-030/verificacion/`.
3. Lo que cambie el criterio (qué cuenta como muerto) no se hace sin decisión de Brian.

## Próximo paso

El análisis de 1 y 2.
