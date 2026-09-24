# Roadmap 0.21.0 — una relación `mutante` con variantes, y un `requiere` con condición

Fecha: 2026-09-15. Base: distribución 0.20.0, álgebra 0.6, sintaxis 0.4.
Tarea: [`20260915-155111-mutante`](../../tareas/20260915-155111-mutante/TAREA.md). Implementa agy; revisa,
mide y corta Claude. La regla general («una medida sólo lee campos declarados») es otra tarea:
[`20260915-155654-campos`](../../tareas/20260915-155654-campos/TAREA.md).

## El problema, medido

La relación `mutante` la producen dos herramientas con campos incompatibles, y el catálogo de Oracle
tiene **dos medidas universales** sobre ella:

| medida | lee | la produce | casos |
|---|---|---|---|
| `proceso.test_con_mutante_que_lo_mata` | `detecciones_conductuales`, `rechazos_del_algebra` | `nucleo/mutacion.py` (medidas) | 002 003 005 013 014 018 058 059 101 |
| `proceso.codigo_con_mutante_que_lo_mata` | `estado`, `equivalente_declarado` | `perfiles/python/mutacion_codigo.py` (código) | 025 026 027 109 110 |

`mutante` no está declarada en `relaciones/`. `medidas_aplicables` elige por nombre de relación, y
el lenguaje, a propósito, **no cortocircuita** `y`/`o` y **levanta** al comparar un campo ausente
(`meta.los_logicos_evaluan_todos_sus_operandos`). Probado por ejecución el 2026-09-15:

1. Con `mutante` mezclada, las dos medidas levantan `«==» sobre un valor ausente`.
2. Dos `donde` encadenados —primero `m.tipo == "medida"`, después el filtro original— funcionan hoy
   sin tocar el álgebra.
3. La medida de código con `requiere mutante`, sobre una `mutante` sólo de filas de medida, da
   **verde (0)**: `requiere` mira que la relación tenga filas, no que haya filas de su tipo. Una
   relación común sin más abriría ese falso verde en cada ronda de `tools/mutar.py`, y el espejo en
   cada ronda de código.
4. `relaciones/*.json` no puede declarar campos presentes sólo en algunas filas.

## Decisión del dueño

Una relación común `mutante` con `tipo`, **extendiendo el lenguaje** para que la declaración y
`requiere` alcancen.

### Por qué el `requiere` es con condición y no «sobre las filas filtradas»

Leído al pie de la letra, «`requiere` mira las filas después del `donde`» rompe el lenguaje. Medido
sobre los catálogos reales: **las 20 medidas con `requiere` que existen filtran con `donde`** la
relación que requieren (16 de Oracle, 4 de Jam; LyraGASP no usa `requiere`), y en todas el `donde`
selecciona las **violaciones**. Cero filas filtradas es su caso verde: con esa lectura, las 20
pasarían de verde a SIN EVIDENCIA.

Lo que la medida de código necesita es otra cosa: que existan filas de su **tipo**, con una condición
propia, separada del filtro de violaciones. Eso es aditivo: ninguna medida existente cambia.

## Diseño

### 1. `requiere` con condición

Forma canónica — cada elemento de `requiere` es un nombre (como hoy) o una entrada con condición:

```json
["requiere", "pieza", ["filas", "mutante", "m", ["==", ["campo", "m", "tipo"], "codigo"]]]
```

- Semántica: `SIN EVIDENCIA` si la relación viene vacía **o** si ninguna fila cumple la condición.
  La condición se evalúa con el álgebra del `donde`: un campo ausente **levanta** (no es `False`).
- Validación al cargar: alias válido, condición booleana bien formada, relación no repetida entre
  entradas; los mismos límites del álgebra que un `donde`.
- `sin_evidencia` del veredicto nombra la relación con su condición: `mutante con m.tipo == "codigo"`, que la línea imprime como `«mutante con m.tipo == "codigo"» vacía`.
- Superficie `.oracle`: una línea `requiere` por entrada con condición, además de la de nombres; varias
  líneas se juntan en un solo nodo, en orden. El impresor emite la forma inversa.

  ```
  requiere pieza
  requiere mutante m donde m.tipo == "codigo"
  ```

- Hechos: `requiere` y `dependencia_de_medida` suman `con_condicion` (booleano), sin quitar columnas.
- Una medida sin condición conserva exactamente su forma canónica actual.

### 2. Relaciones con variantes

```json
["relacion", "mutante",
  ["campos", ["campo", "id", "texto", "sin_unidad"], ["campo", "apunta_a", "texto", "sin_unidad"],
             ["campo", "cambio", "texto", "sin_unidad"], ["campo", "tipo", "texto", "sin_unidad"]],
  ["variantes", "tipo",
    ["variante", "medida", ["campo", "detecciones_conductuales", "entero", "sin_unidad"], …],
    ["variante", "codigo", ["campo", "estado", "texto", "sin_unidad"], …]],
  ["alcance", "…"]]
```

- `variantes` es opcional: una relación sin él conserva su forma de cuatro elementos.
- El discriminante es un campo **común** de tipo `texto`; los valores de variante son únicos y no
  vacíos; cada variante declara al menos un campo; un campo de variante no repite uno común; el mismo
  nombre en dos variantes exige el mismo tipo y la misma unidad.
- Hechos: `campo_declarado` suma `variante` (`""` para los comunes); `relacion_declarada` suma
  `variantes` (cantidad). Sin quitar columnas.
- `nucleo/unidad.py` y los puntos ciegos de `tools/medida.py` encuentran los campos de variante.

### 3. `mutante` y sus dos medidas

- `relaciones/mutante.json` declara la relación con las dos variantes y sus campos reales (los de
  `nucleo/mutacion.py` y los `requeridos` de `perfiles/python/mutacion_codigo.py`).
- Los productores emiten `tipo`: `"medida"` y `"codigo"`; el manifiesto de mutación de código lo
  valida (un manifiesto anterior sin `tipo` se rechaza como inválido, igual que hoy uno vencido).
- Las dos medidas filtran primero por `tipo` y requieren filas de su tipo:

  ```
  medida proceso.codigo_con_mutante_que_lo_mata:
      de mutante m
      donde m.tipo == "codigo"
      donde m.estado == "pasaron" y m.equivalente_declarado == false
      resumen contar(1)
      umbral <= 0 segun contrato porque "…"
      requiere mutante m donde m.tipo == "codigo"
      ambito universal
      alcance "…"
  ```

- El aviso «NO pudieron juzgar» de `tools/mutar.py` y `tools/mutar_codigo.py` **se conserva**: después
  de este corte el catálogo de Oracle no lo dispara, pero protege contra cualquier medida con campos
  ausentes, que es la tarea `campos`.

## Entregas y dueños

| quién | qué |
|---|---|
| agy | `nucleo/medida.py` (`requiere` con condición), `nucleo/sintaxis.py` (lector e impresor), `nucleo/relacion.py` (variantes y hechos), `nucleo/unidad.py`, `tools/medida.py`, productores (`nucleo/mutacion.py`, `perfiles/python/mutacion_codigo.py`), `relaciones/mutante.json`, las dos medidas de `catalogos/proceso/`, tests de todo eso, `AVANCE`/`INFORME` |
| Claude | tests de revisión escritos antes de leer la entrega; corpus (columna `tipo` en los casos existentes y los dos falsos verdes nuevos, observados por ejecución el 2026-09-15); `ESPECIFICACION.md` (§ requiere, § relaciones, §0), versiones, NOTAS, README, manual; la referencia del diferencial (abajo); mutación y corte |

## La referencia del diferencial

`diferencial/referencia/evaluador.py` es una implementación del álgebra escrita por **otro autor que
nunca vio `nucleo/`** (Codex, 2026-08-24; `PROCEDENCIA.md`), fijada a la versión **exacta**:
`comprobar_version_referencia` rechaza emitir fixtures si el núcleo implementa otra. Subir a 0.7 sin
actualizarla deja el diferencial bloqueado; actualizarla mirando `nucleo/` la vuelve decorativa.

Mismo procedimiento que b250e6c: primero `ESPECIFICACION.md` queda completa con el `requiere` con
condición; después se delega a Codex, en un directorio aislado, con **sólo** la especificación, las
decisiones y la referencia actual, sin decirle qué cambió en el núcleo. Se registra en `PROCEDENCIA.md`
y `DECISIONES.md`, se regeneran los fixtures, y un desacuerdo se clasifica como en `PROCEDENCIA.md`
(la especificación no decide / el núcleo contra todas / defecto de la referencia). Ni agy ni Claude
pueden escribirla: los dos leyeron el núcleo.

## Versiones

- `VERSION_ALGEBRA` 0.6 → **0.7**: `requiere` gana entradas con condición y la declaración de relaciones
  gana `variantes`; lo que ya valía significa lo mismo (MENOR, §0).
- `VERSION_SINTAXIS` 0.4 → **0.5**: el lector gana `requiere <relación> <alias> donde <condición>`.
- `VERSION_DISTRIBUCION` 0.20.0 → **0.21.0**. Un proyecto que declara `"algebra": "0.6"` sigue cargando.

## Fuera de alcance

- La regla general de campos declarados y qué hacer con un campo ausente: tarea `campos`.
- Declarar en `relaciones/` las demás relaciones de proceso.
- Una macro nueva: las dos medidas se escriben en forma plana.

## Criterios de salida del corte

Suite completa verde; aceptación del corpus con los dos falsos verdes nuevos en rojo con la medida
de antes y detectados con la nueva; ninguna ronda de `mutar` ni `mutar_codigo` sobre el catálogo de
Oracle imprime «NO pudieron juzgar»; referencia independiente re-derivada contra 0.7 y diferencial regenerado; mutación de los módulos
tocados sin sobrevivientes o con equivalentes defendidos; `verificar_instalacion` y cifras; LyraGASP
y Jam medidos con la versión nueva sin cambio de veredicto.
