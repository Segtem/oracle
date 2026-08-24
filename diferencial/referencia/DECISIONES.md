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
