# Roadmap 0.26.0 — el álgebra puede decir «ninguna fila de otra relación corresponde»

Fecha: 2026-09-16. Base: distribución 0.25.1, álgebra 0.7, sintaxis 0.5.
Tarea: [`20260916-151553-antijunta`](../../tareas/20260916-151553-antijunta/TAREA.md). Implementa agy; revisa,
mide y corta Claude. La referencia del diferencial la re-deriva agy aislado, y el 19/09 Codex escribe
la suya de cero contra 0.8 (`20260915-201030-codex`).

## El problema, medido

El álgebra tiene `unir` (producto) y `donde` (filtro), y con eso sabe decir «hay una fila de B que
corresponde a esta de A». Lo que no sabe decir es lo contrario: **ninguna** fila de B corresponde. Es
la anti-junta, y le falta.

Cinco medidas la necesitaban y la resolvieron igual, con un conteo que calcula un sensor en Python
para que la medida compare contra cero:

| campo contado por el sensor | medida |
|---|---|
| `commits_de_cierre` | `seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre` |
| `mutantes` | `meta.toda_medida_esta_fijada` |
| `casos_que_la_evaluan` | `meta.toda_medida_esta_ejercitada` |
| `detecciones_conductuales`, `rechazos_del_algebra` | `proceso.test_con_mutante_que_lo_mata` |

Cada conteo es lógica fuera del lenguaje: el diferencial no lo contrasta, la mutación de medidas no lo
toca y el catálogo no puede decir qué cuenta. La última vez se vio en `20260915-010452-commits`, donde
la regla «toda tarea cerrada tiene su commit de cierre» no se pudo escribir.

## Diseño

### 1. Un paso de tubería: `sin`

Forma canónica, un paso más como `donde` y `agrupar`:

```json
["sin", ["de", "<relación>", "<alias>"], <condición>]
```

Superficie:

```
ninguno seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre:
    de tarea_seguimiento t
    donde t.estado_declarado == "CERRADA"
    sin commit_seguimiento c donde c.tarea_nombrada == t.id y c.es_cierre == true
    ...
```

Deja pasar cada fila de la tubería para la que **ninguna** fila de la relación cumple la condición. La
condición ve la fila actual —sus alias y sus columnas— y el alias nuevo; el alias nuevo **no** queda en
la salida.

### 2. Semántica en los bordes

- **Relación vacía** (`[]`): no hay con qué corresponder, así que todas las filas pasan.
- **Relación ausente** de la evidencia: el mismo error que `de` —«una relación vacía se declara
  explícitamente como []»—. Una anti-junta sobre algo que no se trajo no puede dar verde por
  omisión, y ésta es exactamente la forma de verde vacío que el lenguaje persigue.
- **Sin cortocircuito**: la condición se evalúa contra **todas** las filas de la derecha antes de
  decidir, como `requiere` desde 0.21.0. Si alguna evaluación levanta, la evaluación levanta, aunque
  otra fila ya hubiera correspondido: el orden de la bolsa no puede cambiar el veredicto.
- **Alias repetido**: el alias nuevo no puede ser uno de la fila actual; es un error de validación.
- **Presupuesto**: `|izquierda| × |derecha|` evaluaciones, contra `producto_cartesiano`, igual que
  `unir`.
- **Después de `agrupar`**: vale igual; la condición ve las columnas con `col`.

### 3. Versiones

- `VERSION_ALGEBRA` 0.7 → **0.8**: un nodo nuevo; todo lo que valía significa lo mismo.
- `VERSION_SINTAXIS` 0.5 → **0.6**: una cláusula nueva, `sin … donde …`.
- `VERSION_DISTRIBUCION` → **0.26.0**.

### 4. Lo que tiene que acompañarlo

- `nucleo/vocabulario.py`: `sin` en `OPERADORES` con su explicación
  (`meta.todo_operador_del_manual_lo_reconoce_el_algebra` lo exige).
- La traza: `sin` nunca agrega filas; una medida de traza como las de `donde` y `agrupar` lo vuelve
  falsable (`meta.sin_nunca_agrega_filas`).
- Los mutadores de medidas: al menos uno que quite el paso `sin` o invierta su efecto, para que la
  mutación de medidas vea las que lo usan.
- **La prueba de valor**: reescribir `seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre` con
  `sin` y **borrar** `commits_de_cierre` y `commits_que_la_nombran` del emisor del tracker. Si la
  medida reescrita da lo mismo sobre la historia real (4, con su sombra), la anti-junta reemplazó
  lógica del sensor, que es lo que se buscaba. Las otras cuatro medidas quedan como tarea aparte:
  sus conteos viven en el marco y en el perfil, y moverlos es otro trabajo.
- **La referencia del diferencial** a 0.8, re-derivada por agy aislado como en 0.21.0: sin ella,
  `comprobar_version_referencia` hace fallar el diferencial en cuanto el núcleo diga 0.8.
- **Mundos del diferencial** con `sin`: derecha vacía, ausente, una que corresponde, ninguna que
  corresponde, una fila que levanta detrás de una que corresponde.
- Corpus: las dos polaridades de cada medida nueva o reescrita.

## Entregas y dueños

| quién | qué |
|---|---|
| agy (conversación del núcleo) | `nucleo/algebra.py`, `nucleo/sintaxis.py`, `nucleo/vocabulario.py`, la traza y su medida, el mutador, la reescritura de la medida del tracker y el emisor, tests de todo, `AVANCE`/`INFORME` |
| agy aislado (proyecto nuevo) | `diferencial/referencia/` a 0.8, sin ver `nucleo/` |
| Claude | tests de revisión antes de leer la entrega, corpus, `ESPECIFICACION.md` §2 y §0, mundos del diferencial, versiones, notas, mutación y corte |

## Fuera de alcance

- Las otras cuatro medidas con conteos del sensor (tarea aparte).
- Una semi-junta (`con` / «existe») explícita: hoy se escribe con `unir` + `donde`.
- Subconsultas dentro de expresiones.

## Criterios de salida del corte

Suite completa verde; aceptación ✓; la medida del tracker reescrita da 4 sobre la historia real, igual
que con el conteo; diferencial ✓ con la referencia 0.8 y los mundos nuevos; mutación de los módulos
tocados sin sobrevivientes o con equivalentes defendidos; `verificar_instalacion`, cifras y sintaxis.
