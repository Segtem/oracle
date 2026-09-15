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

## Medido (2026-09-15)

- El choque está **dentro del catálogo de Oracle**, no sólo entre herramientas: dos medidas
  `universal` sobre la misma relación con campos incompatibles.
  - `proceso.test_con_mutante_que_lo_mata`: `m.detecciones_conductuales`, `m.rechazos_del_algebra`
    (mutación de medidas). Casos: `corpus/proceso/002, 003, 005, 013, 014, 018, 058, 059, 101`.
  - `proceso.codigo_con_mutante_que_lo_mata`: `m.estado`, `m.equivalente_declarado` (mutación de
    código). Casos: `corpus/proceso/025, 026, 027, 109, 110`.
- `mutante` **no está declarada** en `relaciones/` (sólo `corrida`, `evento`, `pieza`), aunque el
  lenguaje ya tiene la forma `relacion` con `campos` (nombre, tipo, unidad).
- `medidas_aplicables` (`nucleo/medida.py`) decide sólo por nombre de relación. `tools/mutar.py` y
  `tools/mutar_codigo.py` atajan el `ErrorDeAlgebra` y lo listan como «NO pudieron juzgar»: es el
  parche de este defecto, comentado como tal en `mutar_codigo.py`.

## Decisión del dueño y lo que costaría (2026-09-15)

El dueño eligió **una relación común** `mutante` con un campo `tipo`, y la regla general de campos
declarados como tarea aparte (`20260915-155654-campos`). Probado por ejecución sobre las medidas
compiladas (`dataclasses.replace` de la tubería):

1. Con `mutante` mezclada (una fila de medida, una de código), las dos medidas actuales levantan
   `«==» sobre un valor ausente`: el lenguaje no cortocircuita `y`/`o` a propósito
   (`meta.los_logicos_evaluan_todos_sus_operandos`), así que `m.tipo == "medida" y …` tampoco sirve.
2. **Dos `donde` encadenados funcionan sin tocar el álgebra**: `donde m.tipo == "medida"` y después el
   `donde` original. Cada medida cuenta 1 sobre la mezcla, sin error.
3. **`requiere` deja de proteger**: la medida de código con `requiere mutante`, sobre una `mutante` que
   sólo trae filas de medida, da **verde (0)** en vez de SIN EVIDENCIA. `requiere` mira que la
   relación tenga filas, no que queden filas después del filtro. Con `mutante` vacía sí da SIN
   EVIDENCIA. Es un falso verde nuevo que la relación común abriría en cada ronda de `tools/mutar.py`.
4. `relaciones/*.json` no admite campos presentes sólo en algunas filas: cada `campo` son cuatro
   elementos y «no hay defaults silenciosos» (`nucleo/relacion.py`).

La relación común pide entonces dos extensiones del lenguaje (campos por `tipo` en la declaración y
un `requiere` sobre las filas filtradas); dos relaciones no piden ninguna. Consultado de nuevo con el
dueño con estos datos.

**Decisión (2026-09-15, con los datos de arriba): relación común extendiendo el lenguaje.** Entran en
esta tarea:

- `relaciones/` puede declarar campos presentes sólo para un valor de un campo discriminante
  (`tipo`), y `mutante` se declara así;
- `requiere` protege las filas que quedan después del filtro, no sólo la relación entera: una medida
  de código sobre una ronda sólo de medidas sale SIN EVIDENCIA, no verde;
- las dos medidas de `proceso` filtran por `tipo` y los productores emiten `tipo`. El aviso «NO
  pudieron juzgar» de `mutar.py` y `mutar_codigo.py` **se conserva** (corregido el mismo día): protege
  contra cualquier medida con campos ausentes, que es la tarea `20260915-155654-campos`.

**Medido antes del plan:** las 20 medidas con `requiere` que existen (16 de Oracle, 4 de Jam) filtran
con `donde` la relación requerida, y en todas el `donde` selecciona violaciones. Un `requiere` «sobre
las filas filtradas» las pasaría de verde a SIN EVIDENCIA; por eso el plan lo diseña como `requiere`
**con condición** propia (`requiere mutante m donde m.tipo == "codigo"`), aditivo. Plan:
[`PLAN-0.21.0-MUTANTE.md`](../../PLAN-0.21.0-MUTANTE.md).

Flujo: plan, encargo a agy, revisión, mutación y corte.
