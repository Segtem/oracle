# El álgebra 1.0: cuatro decisiones que cierran falsos verdes y cambian el significado

- ESTADO: ABIERTA
- PRIORIDAD: 92
- ETIQUETAS: oracle, metalenguaje, algebra, flaqueza


## Decisión (Brian, 2026-09-24)

De `huecos-spec` (HUECOS.md, sección 2) y `predicado-bool`, el lado más estricto, que es el que
cuadra con el «fail-closed» del proyecto:

1. **2.4 — testigos:** son las filas de salida de la tubería `desde` completa, las que suman al
   valor (como ya hace el núcleo). Se escribe en la especificación y la referencia se alinea.
2. **2.5 — predicados:** `donde`, `sin`, `requiere` y los operandos de `y`, `o` y `no` exigen `bool`.
   Un número, un texto o un `None` son error de álgebra, no verdad de Python. Cierra `predicado-bool`.
3. **2.6 — claves:** se validan las claves únicas de **toda** la evidencia recibida antes de medir,
   no sólo de las relaciones que la medida usa (como ya hace la referencia).
4. **2.9 — `null`:** un hecho con un campo `null` explícito se rechaza al cargar la evidencia (como ya
   hace la referencia). «Sin nulos implícitos» pasa a ser también sin nulos explícitos.

Cambia el significado de cosas que existían, así que por §0 sube la **mayor**:
`VERSION_ALGEBRA` 0.8 → **1.0**.

## Antes de publicar

- Medir Oracle, Jam, LyraGASP y commander con el núcleo nuevo. Ya se sabe de un caso: LyraGASP
  `personaje.ancla_requerida_ausente` aplica `no(a.presente)` con `a.presente = None` diez veces en su
  corpus (medición de `predicado-bool`). Con 2.5 y 2.9 eso es error: el sensor tiene que emitir
  `presente` como `bool`, o la medida tiene que compararlo explícito. Se arregla del lado del
  consumidor antes de subir.
- La referencia del diferencial se alinea en los cuatro puntos, con la ida y vuelta del contraste.

### Nota (2026-09-25 04:47:56 UTC)

Álgebra 1.0 implementada en núcleo, especificación y referencia; regresiones de testigos, bool (incluido requiere), claves globales, null, cabecera sola e igualdad indexada. Migrados oracle.json y ejemplos activos; fixture diferencial regenerado; equivalentes: 13 intactos. Verificación: unittest discover -s tests 2513 OK; referencia 48 OK; test --rapido VERDE; cifras actualizadas; tools/sitio.py no existe. Tercer autor 0.8: el contraste formal rechaza versiones distintas; comparación diagnóstica sobre 285 entradas conserva 63 desacuerdos históricos. Consumidores: Jam 31 casos OK pero diferencial ROJO en 10 entradas de physics por null explícito; commander sin medidas ni casos; LyraGASP no disponible como proyecto Oracle local. Sin commit por .git sólo lectura.

## Próximo paso

Corregir en Jam los `null` explícitos de los mundos `sin_suelo` (10 desacuerdos del diferencial), localizar el proyecto medible de LyraGASP y corregir `personaje.ancla_requerida_ausente` para que `presente` sea booleano; repetir las mediciones de ambos consumidores con el núcleo 1.0. Commander sólo ofreció un proyecto vacío. Dejar la entrega 0.8 del tercer autor como contraste histórico y cerrar esta tarea sólo cuando los consumidores estén verificados.

### Nota (2026-09-25 04:53:54 UTC)

2026-09-25, Claude: medido con el núcleo de esta rama. LyraGASP (medidas/): ROJO — 8 casos del corpus ya no se ponen como deben porque usan null a propósito para decir «no decidible» (ancla_personaje.presente, montage_recarga.has_root_motion, entre otros), y 9 mutantes de medida sobreviven. Jam: ROJO — 10 desacuerdos del diferencial por null explícitos en sus fixtures de física, y la mutación falla. Es lo esperado del punto 4 (sin null) y del 2 (bool estricto): los consumidores tienen que modelar el «no decidible» explícito antes de subir a 1.0. Tareas en sus trackers: LyraGASP y Jam, «algebra-10-null». El núcleo se une a main SIN publicar.
