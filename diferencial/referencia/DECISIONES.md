# Decisiones de implementacion

Estas decisiones cubren puntos donde `ESPECIFICACION.md` y las decisiones locales dejaban margen.

## Forma de los testigos

Seccion ambigua: "Los testigos no se declaran".

Decision: `testigos` devuelve copias de las filas internas que sobrevivieron al ultimo `donde`.
Antes de `agrupar`, una fila tiene la forma `{"alias": {campo: valor}}`. Despues de `agrupar`,
una fila tiene columnas derivadas, por ejemplo `{"modulo": "b", "reales": 0}`.

Si la tuberia no contiene ningun `donde`, `testigos` es la relacion final de `desde`.

## `agrupar` con uno o varios agregados

Seccion ambigua: tabla de operadores de la seccion 3 y ejemplo de ausencia en la seccion 8.

Decision: se aceptan dos formas para los agregados de `agrupar`:

```json
["agrupar", [["k", ["campo", "a", "id"]]], ["n", "contar", 1]]
```

y

```json
["agrupar", [["k", ["campo", "a", "id"]]], [["n", "contar", 1]]]
```

La segunda forma permite mas de un agregado, aunque los casos actuales usen uno.

## `agrupar` sobre cero filas

Seccion ambigua: agregados sobre cero filas y limite declarado en ausencia.

Decision: si `agrupar` recibe cero filas, produce cero grupos. Por lo tanto no emite una fila
artificial con agregados en `0`, aun si la lista de claves esta vacia. El agregado global sobre cero
filas queda cubierto por `resumen`.

## Ubicacion de `resumen`

Seccion ambigua: la tabla lista `resumen` como operador, pero la forma de medida lo separa de
`desde`.

Decision: en esta API, `resumen` se evalua solo en la seccion top-level `["resumen", agg, expr]` de
la medida. Dentro de `desde`, `resumen` falla porque ya no produce una relacion encadenable.

## Comparador `!=` con flotantes

Seccion ambigua: igualdad exacta de flotantes.

Decision: se prohibe exactamente `["==", a, b]` cuando ambos operandos evaluan a `float`, tal como
dice el contrato. `["!=", a, b]` queda permitido si los tipos son compatibles y los floats son
finitos.

## Logicos sin cortocircuito

Seccion ambigua: semantica de `y` y `o`.

Decision: `y` y `o` evaluan todos sus operandos antes de combinar el resultado. Asi un campo ausente
o un valor no finito no queda oculto por cortocircuito.

## Operadores que pueden ser pasos de `desde`

Seccion ambigua: relacion entre operadores y tuberia.

Decision: `de`, `unir` y `desde` son fuentes o subexpresiones de relacion. Los pasos que consumen la
relacion corriente son `donde` y `agrupar`. `resumen` queda fuera de la tuberia por la decision
anterior.

## Codificacion de `SIN EVIDENCIA`

Seccion ambigua: `requiere` dice que la evaluacion "devuelve SIN EVIDENCIA", pero la API publica
sigue siendo `{"id","valor","ok","testigos"}` y no agrega un campo de estado.

Decision: cuando falta evidencia requerida, `valor` es el texto `"SIN EVIDENCIA"`, `ok` es `False`
y `testigos` es la lista vacia. Asi el resultado no queda verde, y el consumidor puede distinguirlo
de un rojo del mundo mirando el valor.

## Relacion requerida ausente

Seccion ambigua: `requiere` habla de relaciones vacias, pero no explicita si una relacion ausente en
el mapa de evidencia es un error de algebra o ausencia de evidencia.

Decision: para `requiere`, una relacion ausente equivale a una relacion vacia y devuelve
`SIN EVIDENCIA`. Para `["de", relacion, alias]`, una relacion ausente sigue siendo error de algebra.

## Validacion de claves declaradas

Seccion ambigua: la clave declarada se valida antes de medir, pero no dice si alcanza con validar las
relaciones usadas por la medida.

Decision: se validan todas las claves declaradas en la evidencia recibida antes de medir, incluso si
la relacion no aparece en la tuberia. El nodo `["clave", campos]` no cuenta como hecho. Los campos de
clave deben ser textos no vacios, no repetidos, y una clave sin campos es invalida. La fila informada
en errores es el indice dentro de la lista JSON de la relacion, contando el nodo `clave` si existe.

## Limites con API fija

Seccion ambigua: la especificacion dice que `LimitesAlgebra` forma parte de la llamada, pero la tarea
fija la API publica como `evaluar(medida, evidencia, escalares=None)`.

Decision: el evaluador mantiene la firma publica y usa limites finitos internos: 100000 filas por
relacion, 1000000 filas materializadas por producto cartesiano y profundidad maxima de expresion 100.
Superarlos levanta `ErrorDeAlgebra`.

## `min`/`max` sobre booleanos

Seccion ambigua: los agregados `suma` y `promedio` aceptan booleanos como indicadores 0/1, pero
`min` y `max` solo piden escalares homogeneos y comparables.

Decision: los booleanos no se consideran ordenables para `min`/`max`. Si una medida necesita medir
booleanos como indicadores, debe usar `suma` o `promedio`.
