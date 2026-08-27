# Decisión 006 — el umbral declara de dónde sale su número, y la prosa deja de ser obligatoria

**Fecha:** 2026-08-27 · **Estado:** aprobado, en construcción
**Sube:** `VERSION_ALGEBRA` 0.3 → 0.4 (agrega, no cambia significado)

## Lo que se decide

El umbral gana una ranura de conjunto cerrado:

```
umbral <= 1.0 segun convencion                 ← la defensa en prosa ya NO es obligatoria
umbral <= 0   segun contrato porque "…"        ← quien tiene algo que decir lo sigue diciendo
```

```
medicion     el número salió de medir algo
contrato     lo fija un acuerdo: una especificación, un contrato operativo, una norma
convencion   es una costumbre del dominio, y se podría discutir
tanteo       se probó hasta que anduvo
```

Forma canónica: `["umbral", op, valor, porque, segun]`. `porque` conserva su posición y puede ser
`""`; `segun` es nuevo y al final.

## Por qué

Hoy `porque` es obligatorio y lo único que la máquina comprueba es **que no esté vacío**. La medida
que lo vigila lo confiesa: *«ve si la defensa del umbral está VACÍA. NO ve si la defensa es mala,
circular o mentirosa»*. Es una obligación cara —87 defensas y 17.369 caracteres en los tres
catálogos— que compra una comprobación de casi cero.

Y obligar a escribir un párrafo produce, previsiblemente, párrafos escritos por obligación.

`segun` invierte eso: lo obligatorio pasa a ser lo evaluable. Con la etiqueta puesta, Oracle puede
contestar una pregunta que hoy no puede ni formular — **«¿cuántos umbrales de este catálogo son puro
tanteo?»**—. Un catálogo con quince tanteos y ninguna medición dice algo cierto y grave sobre sí
mismo.

Es el mismo movimiento que `procedencia` sobre la evidencia, doce días antes: sacar de la prosa lo
que es un conjunto cerrado, dejar la prosa para lo que no lo es.

## Por qué la prosa NO se borra

Se midió antes de decidir. La etiqueta contesta **de dónde salió el número**; la prosa contesta **por
qué ése y no otro**. Son dos preguntas y la etiqueta responde una. Tres defensas reales, con lo que
la etiqueta deja afuera:

| medida | etiqueta | lo que se perdería |
|---|---|---|
| `snap.al_ras` | `convencion` | «evita rechazar ruido de bounds sin aceptar una junta visible» — el canje entre dos formas de fallar |
| `scatter.cobertura` | `contrato` | por qué 0 y no un margen: el 0,6 ya está en el filtro y dos copias no se mantienen iguales — más el puntero al caso `012` |
| `ml_deformer.malla_objetivo_fragmentada` | ninguna encaja | la derivación entera: una superficie partida no propaga la deformación a través de la junta |

La tercera no entra en las cuatro categorías: no es medición, ni contrato, ni convención, ni tanteo.
Es una derivación de cómo funciona el método. Si la prosa desapareciera, esa medida se quedaría sin
su única explicación.

Hay además un argumento incómodo: si el objetivo es que un humano audite lo que escribió un LLM, el
`porque` es literalmente **lo único que el humano puede juzgar y la máquina no**. Sacarlo del
lenguaje es sacarle al humano su parte.

## Por qué agrega en vez de reemplazar

La forma obvia era `["umbral", op, valor, segun, porque]`, cambiando el significado de la posición 3.
Eso sube la MAYOR, y ahí está el problema: **ninguno de los dos consumidores declara `algebra` en su
`oracle.json`**. La maquinaria de versiones existe, funciona y es opt-in, y nadie optó. Un cambio
mayor no les fallaría cerrado con «tu proyecto pide 0.3 y este núcleo implementa 1.0»: les daría un
error de parseo sin causa.

Agregando al final, ninguna medida existente se rompe. La presión para migrar no viene de un error,
viene de una medida en rojo — igual que con `procedencia`, que salió roja en 12 el primer día y se
cerró transcribiendo, no rompiendo.

## Lo que reemplaza a `meta.ningun_umbral_sin_defensa`

Esa medida exige prosa no vacía y deja de tener sentido. En su lugar, dos:

- **`meta.todo_umbral_declara_de_donde_sale`** — un umbral cuyo `segun` quedó `sin_declarar`.
  `sin_declarar` es una ausencia visible, no un default creíble.
- **`meta.todo_tanteo_explica_por_que`** — un `tanteo` sin prosa. La etiqueta ya dice todo lo que hay
  que decir de una `medicion`; de un `tanteo` no dice nada, y ahí la explicación sigue haciendo falta.

## Lo que NO se hace

- **No** se borra la prosa. Se vuelve opcional, que es distinto.
- **No** se pone un default en `segun`. Un default creíble se queda sin pensar; ya se aprendió.
- **No** se deja que una herramienta rellene `segun` sola. La etiqueta es un juicio sobre de dónde
  vino un número, y sólo lo sabe quien lo puso.
