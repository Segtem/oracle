# la mutación cuenta como muerto un mutante cuyos tests fallaron por falta de disco

- ESTADO: CERRADA
- PRIORIDAD: 90
- ETIQUETAS: oracle

### Nota (2026-09-29 12:31:33 UTC)

Medido el 2026-09-29 con nucleo/generador.py: con /tmp (tmpfs de 16 GB) llenándose, una ronda completa dio 91 vivos de 683 y otra parcial 0 de 94; con el disco sano, la misma ronda da 380 de 645 y la parcial 8 de 93. Un test que falla por ENOSPC sale con código 1, que el protocolo lee como TESTS_FALLARON: muerte falsa. La ronda terminó con OSError [Errno 28] recién cuando el propio arnés no pudo escribir. Pone en duda las cifras de mutación del corte 0.35.0 (1400 sin sobrevivientes), corridas la noche anterior sin control del espacio: hay que volver a medirlas.

### Nota (2026-09-29 13:26:41 UTC)

Arreglado en 2f1553f: ejecutar_tests mide el espacio libre de la copia y del TMPDIR antes y después; por debajo de 256 MiB (ESPACIO_MINIMO), un fallo de tests es ERROR_ARNES y la ronda sale inconclusa. Mutación de las líneas nuevas 10/10. Remedición del corte 0.35.0 con el arreglo y el disco sano (11 GB libres todo el tiempo): requisito 70/70, cobertura 17/17, cambios 52/52 (+1 eq), escenario 20/20, formato 9/9, mutar 51/51 (+1 eq), aceptacion 89/89, medida 332/332, cli 760/760 (+1 eq). Las cifras publicadas se sostienen: 1400, ningún vivo. Las que no se sostenían eran las del generador (91 y 0 con el disco llenándose; 380 y 8 con el disco sano), que van en generador-los.
