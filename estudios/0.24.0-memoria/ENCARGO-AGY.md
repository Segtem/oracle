# Encargo 0.24.0 — el arnés le pone tope de memoria a cada mutante

2026-09-16. Tarea [`20260915-112728-memoria`](../../tareas/20260915-112728-memoria/TAREA.md).
Revisa, mide y corta Claude.

## El problema, medido

`tools/mutar_codigo.py` limita el tiempo (`--timeout`) y la salida (`--limite-salida-kb`) de cada
mutante, pero no su memoria. Medido el 2026-09-15 mutando `tools/tareas_consulta.py`: el mutante
`not in` → `in` de la línea 65 deja a `tokenizar` sin avanzar y agrega `Token("", i)` sin fin; hasta
el timeout de 300 s se come la RAM de la máquina y el sistema mató la ronda dos veces, arrastrando
procesos ajenos. Desde entonces cada ronda se corre con `ulimit -v 4000000` puesto a mano desde
afuera, y eso no está en ninguna parte del arnés: quien lo olvide tumba su máquina.

Un mutante que se queda sin memoria muere con `MemoryError`, que es un fallo de tests y **cuenta como
mutante muerto**. No es un timeout ni un error de arnés: la ronda sigue siendo concluyente.

## Leer antes

- `perfiles/python/mutacion_codigo.py`: `ejecutar_tests` (el `Popen` que corre los tests de cada
  mutante, con su timeout, su lectura de salida limitada y `_terminar_proceso`), `_ejecutar_ronda`,
  la función que corre la línea base y la que arma la evidencia de la ronda (el diccionario con
  `limite_salida`, `codigos_fallo_tests`, etc.).
- `tools/mutar_codigo.py`: el `argparse` (`--timeout`, `--limite-salida-kb`) y dónde se pasan esos
  valores; `PRIORIDADES`; cómo se clasifican muerto / vivo / timeout / error de arnés.
- `relaciones/corrida_mutacion.json` y el `CAMPOS_DE_RELACIONES` del emisor de esa relación: desde
  0.22.0 los campos que emite una relación están declarados al lado del emisor y un test los compara
  con las filas emitidas. Si agregás un campo a esa relación, actualizá las dos declaraciones.
- `tests/test_mutacion_codigo.py`: cómo se prueba hoy el arnés sin correr una ronda entera.
- `ESPECIFICACION.md` §5 (mutación), sólo para no contradecirla.

## Qué hay que entregar

1. **Tope de memoria por ejecución.** `ejecutar_tests` acepta un límite de memoria (en bytes,
   `None` = sin tope) y lo aplica **en el hijo**, con `resource.setrlimit(RLIMIT_AS, …)`; el proceso
   padre no cambia su propio límite. Cuidá de no romper lo que ya hace el `Popen`: grupo de procesos
   propio, terminación del grupo y lectura limitada de salida siguen funcionando igual.
2. **Se propaga por toda la cadena**, incluida la corrida de la **línea base**: un tope demasiado
   bajo tiene que verse antes de mutar, no a mitad de la ronda.
3. **Un mutante que excede el tope está muerto.** Que quede claro en el código por qué: el proceso
   sale distinto de cero, que es exactamente lo que el arnés llama «los tests lo detectaron». No es
   timeout ni error de arnés.
4. **`--limite-memoria-mb` en `tools/mutar_codigo.py`**, con el mismo aire que `--timeout`: valor por
   omisión **4000** (los 4 GB que se venían poniendo a mano), `0` para desactivarlo, y validación de
   entrada como la que ya tienen los otros límites.
5. **La evidencia de la ronda lo declara**, junto a `limite_salida`. Si eso agrega un campo a
   `corrida_mutacion`, actualizá su declaración y el `CAMPOS_DE_RELACIONES` del emisor.
6. **Tests nuevos en `tests/test_mutacion_codigo.py`**: que el tope llega al hijo y lo limita de
   verdad (un comando que intente reservar mucha memoria muere con el tope puesto y sobrevive sin
   él); que un mutante que excede cuenta como muerto y no como timeout ni error de arnés; que la
   línea base usa el mismo tope; que `0` desactiva; que un valor inválido se rechaza. Que no
   dependan de la RAM de la máquina que los corra: un tope chico y un proceso que pide más.

## Propiedad

**Agy:** `perfiles/python/mutacion_codigo.py`, `tools/mutar_codigo.py`,
`tests/test_mutacion_codigo.py`, `relaciones/corrida_mutacion.json` y el `CAMPOS_DE_RELACIONES` de su
emisor si hace falta, y en `estudios/0.24.0-memoria/` los archivos `AVANCE-AGY.md` (primero, con tu
plan de archivos) e `INFORME-AGY.md` (al final, con lo hecho, las decisiones y las dudas).

**Claude:** `.github/`, `ESPECIFICACION.md`, `NOTAS-DE-RELEASE.md`, `README.md`, `nucleo/version.py`,
`docs/`, el corpus, y **todo test existente**. Si un test existente contradice el encargo, no lo
edites: anotalo en el informe con su nombre y por qué.

## Reglas

Sólo herramientas de lectura y edición: **NO shell, NO tests, NO subagentes, NO red, NO commits.**
En el informe no afirmes verificaciones que no corriste — no vas a poder correr ninguna, y está bien:
las corre Claude. Decilo así.
