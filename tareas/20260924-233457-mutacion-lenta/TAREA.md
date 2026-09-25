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

## Avance

Se completó el análisis de los puntos 1 y 2 en `tareas/20260924-233457-mutacion-lenta/ANALISIS.md` sin modificar código ni ejecutar comandos de shell:
- Se constató que `failfast=True` ya opera en `tools/ejecutar_suite_mutacion.py:26`. Los mutantes muertos por módulos prioritarios no pagan la suite descubierta; la suite completa (~86-90 s) la sufren los mutantes vivos/equivalentes y los que escapan a las prioridades declaradas.
- En `nucleo/sintaxis.py` (~6,1 s/mutante), el costo se explica porque `tests/test_sintaxis.py` tiene 3163 líneas y se evalúa secuencialmente hasta hallar el test que falla, más la sobrecarga fija por mutante (subproceso frío, escrituras atómicas con `fsync` y múltiples barridos `os.walk` de caché).
- En `tools/cli.py`, `PRIORIDADES` antepone cuatro módulos ajenos (`test_reportar`, `test_vigilar`, `test_biblioteca`, `test_tareas`) antes de `test_cli`.
- Al agregar tests para mutantes vivos, el arnés invalida el manifiesto (`perfiles/python/mutacion_codigo.py:756-757`), forzando a reejecutar los 595 mutantes completos (>1 h) para release.
- Se documentaron cuatro propuestas graduales que preservan intacto el criterio de muerte.

## Próximo paso

Medir UN mutante de `tools/cli.py` por partes —arranque del subproceso, import de los tests, cada
módulo prioritario, limpieza de caches— y recién con ese desglose proponer. La medición A/B refutó
que el orden de las prioridades sea la causa ([medicion/ab-tiempos.txt](medicion/ab-tiempos.txt)).
La propuesta 4 (conservar muertos al agregar tests) sigue siendo decisión de Brian.
