# la mutación cuenta como muerto un mutante cuyos tests fallaron por falta de disco

- ESTADO: ABIERTA
- PRIORIDAD: 90
- ETIQUETAS: oracle

### Nota (2026-09-29 12:31:33 UTC)

Medido el 2026-09-29 con nucleo/generador.py: con /tmp (tmpfs de 16 GB) llenándose, una ronda completa dio 91 vivos de 683 y otra parcial 0 de 94; con el disco sano, la misma ronda da 380 de 645 y la parcial 8 de 93. Un test que falla por ENOSPC sale con código 1, que el protocolo lee como TESTS_FALLARON: muerte falsa. La ronda terminó con OSError [Errno 28] recién cuando el propio arnés no pudo escribir. Pone en duda las cifras de mutación del corte 0.35.0 (1400 sin sobrevivientes), corridas la noche anterior sin control del espacio: hay que volver a medirlas.
