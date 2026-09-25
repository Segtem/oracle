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

## Próximo paso

Esperar a que Codex termine la parte de `huecos-spec` que no necesitaba decisión; después,
implementar esto en una rama y medir los consumidores.
