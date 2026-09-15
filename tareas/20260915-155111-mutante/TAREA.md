# La relación mutante tiene dos esquemas y una medida universal no puede juzgar uno

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: oracle, metalenguaje, bug

La relación `mutante` la producen dos herramientas con campos distintos:

- mutación de **medidas** (`nucleo/mutacion.py`, `tools/mutar.py`): `detecciones_conductuales`,
  `rechazos_del_algebra`;
- mutación de **código** (`perfiles/python/mutacion_codigo.py`, `tools/mutar_codigo.py`): `id`,
  `apunta_a`, `cambio`, `murio`, `estado`, `tests_fallaron`, `error_arnes`…

`proceso.test_con_mutante_que_lo_mata` es `universal` y lee `m.detecciones_conductuales`: aplica por
relación a la evidencia de código y no la puede juzgar. Cada ronda de `mutar_codigo` lo imprime
(«1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no», visto el
2026-09-15 en las rondas de 0.19.0 y 0.20.0). El espejo está en LyraGASP:
`proceso.codigo_con_mutante_que_lo_mata` espera `m.estado`, que la evidencia de medidas no trae
(anotado en `RELEVO.md`, «Deudas vivas»).

Es un defecto del metalenguaje, no de una herramienta: una relación es un contrato y hoy un mismo
nombre significa dos cosas. A decidir y medir:

- dos relaciones con nombre propio (p. ej. `mutante_de_medida` / `mutante_de_codigo`) declaradas en
  `relaciones/`, o una sola con esquema común;
- que la aplicabilidad no dependa sólo del nombre de la relación: una medida cuyos campos no están
  hoy «no juzga» en silencio; ¿debería ser un error de declaración o un rojo?
- migración de los consumidores que ya escriben medidas sobre `mutante`.
