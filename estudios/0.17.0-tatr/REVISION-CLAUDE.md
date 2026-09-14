# Revisión de Claude — entrega de agy, 0.17.0

2026-09-14. Revisión del código, la documentación y el informe de agy contra
[ENCARGO-AGY.md](ENCARGO-AGY.md). Mismas reglas: sólo lectura y edición, sin shell, tests, red
ni commits; la misma propiedad de archivos. Claude ejecuta todo.

## Lo que se verificó y pasa

- Suite completa: 1898 tests, 1 falla ajena a agy (`docs/manual.html` desactualizado, es de Claude).
- `tests/test_tareas_tatr.py` (agy) y `tests/test_tareas_tatr_revision.py` (Claude): en verde.
- Los 316 tests previos del tracker y los de CLI, herramientas y MCP: en verde.
- `tools/verificar_instalacion.py`, con el recorrido nuevo de etiquetar, etiquetas y grafo: `WHEEL OK`.

## Defectos reproducidos — corregir

Cada uno con su reproducción. Todos necesitan un test de regresión en `tests/test_tareas_tatr.py`.

### R1. `etiquetar` corrompe una tarea sin salto de línea final (grave)

```
printf '# Sin EOL\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50' > tareas/<id>/TAREA.md
oracle tarea etiquetar <id> --etiqueta bug      # sale 0: «1 tarea(s) modificada(s)»
# queda: "- PRIORIDAD: 50- ETIQUETAS: bug"  →  revisar: prioridad inválida
```

`_aplicar_etiquetas_texto` inserta la línea nueva después de una línea que no termina en EOL.
Si la línea anterior no tiene EOL, agregárselo (el EOL del documento) antes de insertar.
Al modificar una línea `- ETIQUETAS:` existente que no termina en EOL (última línea del archivo),
no agregarle uno: hoy `etiquetar` + `desetiquetar` sobre ese archivo agrega un `\n` final y el
resultado ya no es byte a byte el original.

### R2. Los problemas de `tareas/etiquetas` rompen lecturas que no lo usan

Con `bug uno` y `bug dos` en `tareas/etiquetas`: `listar`, `grafo`, `hechos`, `buscar` y
`etiquetar` salen 1. Con `tareas/etiquetas` como enlace simbólico, `listar` sale 1. El encargo
pide que sólo `revisar` falle y que las demás lecturas sigan.

La causa es que `auditar_tareas` suma los problemas del archivo de etiquetas, y `cmd_resumen` los
vuelve a quitar comparando el texto de los mensajes, que es frágil. Corregir así:

- `auditar_tareas` sólo reconoce `etiquetas` como auxiliar; **no lo lee** ni suma sus problemas.
- `cmd_revisar` llama a `leer_archivo_etiquetas` y suma sus problemas (redefinición con
  `etiquetas:<línea>`, enlace simbólico, UTF-8, tamaño, E/S) ⇒ 1.
- `cmd_resumen` llama a `leer_archivo_etiquetas`: redefinición ⇒ aviso por stderr y última
  definición; enlace simbólico ⇒ aviso por stderr y sin descripciones; en los dos casos sale 0.
  UTF-8 inválido, tamaño o E/S ⇒ 1 con la ruta. Eliminar el filtro por texto de mensajes;
  distinguir los casos por datos (por ejemplo, un tipo o una categoría en el problema).
- `listar`, `ver`, `grafo`, `hechos`, `buscar`, `referencias`, `seguimiento`, `etiquetar` y
  `desetiquetar` no leen el archivo y no cambian su código por él.

### R3. Comentarios con `#` en `tareas/etiquetas`

No estaban en el encargo y tatr no los tiene: una etiqueta `#algo` quedaría sin poder describirse.
Quitar el tratamiento de `#`; cada línea no vacía es una definición.

## Simplificaciones pedidas

### S1. `etiquetar` y `desetiquetar` duplican unas 150 líneas

Parseo y validación de `--etiqueta`, resolución de la raíz, auditoría, resolución de IDs, lectura,
escritura con informe de parciales y salida son idénticos. Extraer un camino común y dejar en
cada comando sólo el parser, la selección de tareas y el modo. Menos código duplicado es también
menos sitios de mutación que custodiar dos veces.

### S2. `grafo` compara cada tarea con cada ID

Hoy son n² búsquedas con un patrón por ID. Hay una forma lineal equivalente: un solo patrón que
extrae tokens candidatos, `(?<![A-Za-z0-9_-])[0-9]{8}-[0-9]{6}[A-Za-z0-9_-]*`, y la pertenencia al
conjunto de IDs válidos. Como el token se extiende con la misma clase de caracteres que define el
borde, `…-sensor` dentro de `…-sensor-2` produce el token `…-sensor-2` y no coincide, igual que hoy.

## Documentación: afirmaciones que no son ciertas

- «Diferencias con tatr», punto 4: `listar` **no tiene** `--estado`. Los filtros son `--cerradas`,
  `--todas`, `--etiqueta` y `--texto`.
- Punto 2 sugiere que tatr usa YAML, frontmatter o cabeceras binarias: tatr usa exactamente la
  misma forma `- CLAVE: VALOR`. La diferencia real es de nombres (`TASK.md`/`STATUS`/`PRIORITY`/
  `TAGS`/`OPEN`/`CLOSED` frente a los de Oracle), y por eso los formatos no se leen entre sí.
- Punto 3 afirma que los bytes nulos fallan con código 1. No hay tratamiento de NUL: UTF-8 los admite.
  Quitar la afirmación o limitarla a lo que el código hace.
- «Alineación dinámica» menciona cabeceras `ID`, `ESTADO`, `PRIO`, `ETIQ`: `listar` no imprime
  cabecera. El informe dice lo mismo en 3.1.
- Enlace simbólico en `resumen`: documentar el comportamiento corregido en R2.
- Agregar a «Diferencias con tatr»: tatr separa etiquetas por comas **y espacios**; Oracle sólo por
  comas, así que `hola mundo` es una sola etiqueta en `TAREA.md` y no se puede describir en
  `tareas/etiquetas`, donde el primer espacio separa etiqueta y descripción.
- Pedido del encargo: la sección debe ser breve y exacta. Hoy es larga y promocional
  («rigurosidad», «auditoría formal»). Una línea por diferencia, sin adjetivos.

## Al terminar

Actualizar `INFORME-AGY.md` con una sección «Correcciones tras la revisión» que diga qué cambió en
cada punto (R1–R3, S1–S2, documentación) y qué tests se agregaron. No afirmar que pasan.
