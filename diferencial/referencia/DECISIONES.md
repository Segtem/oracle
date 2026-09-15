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

## Version del algebra vigente

Seccion ambigua: §0 ("La version del lenguaje").

Decision: en §0 se detallan cortes historicos donde `VERSION_ALGEBRA` quedaba en `0.6`, pero la regla
explicita de incremento de version senala que subio de `0.6` a `0.7` porque una entrada de `requiere`
puede llevar condicion y la declaracion de una relacion gano `variantes` (§1.3, §2). Por ende, la version
vigente del algebra es `"0.7"`, y `VERSION_ALGEBRA` se define en `"0.7"`.

## Evaluacion de condiciones en `requiere` sin cortocircuito entre filas

Seccion ambigua: §2 ("Una medida es un dato", subseccion "Una entrada de requiere puede llevar condicion").

Decision: al evaluar `["filas", relacion, alias, condicion]`, la condicion se evalua sobre todas las filas
existentes de la relacion. No se realiza cortocircuito tras hallar la primera fila que cumple la condicion.
Si alguna fila presenta un campo ausente, alias invalido, tipo no booleano o error de funcion escalar, se
levanta `ErrorDeAlgebra` inmediatamente. Esto garantiza que el orden de almacenamiento de los hechos en la
bolsa no altere el resultado (respetando DECISION-001) y mantiene la doctrina fail-closed sin cortocircuito
registrada para los operadores logicos.

## Precedencia de errores de algebra en `requiere` frente a relaciones vacias

Seccion ambigua: §2 ("Una medida es un dato") y decision "Codificacion de SIN EVIDENCIA".

Decision: si una relacion presente en la evidencia contiene filas pero la condicion de `filas` falla con
`ErrorDeAlgebra` (por ejemplo, por referenciar un campo ausente en una fila presente), ese error se levanta
inmediatamente y no queda encubierto ni silenciado si otra relacion requerida viene vacia o ausente. La
ausencia de evidencia devuelve `"SIN EVIDENCIA"` unicamente cuando los datos provistos en la evidencia no
contienen errores de algebra al evaluar las condiciones sobre sus hechos.

## Expresiones permitidas y contexto en la condicion de `requiere`

Seccion ambigua: §2 ("Una medida es un dato", "La condicion es una expresion booleana con las reglas de un donde: solo usa su alias...").

Decision: la condicion se evalua con el evaluador general de expresiones (`_evaluar_expr`) bajo un contexto
donde solo existe el alias declarado (`{alias: hecho}`). Se permiten operadores de comparacion, logicos (`y`,
`o`, `no`), literales, funciones escalares registradas en `escalares`, y accesores `["campo", alias, nombre]` y
`["hecho", alias]`. Cualquier uso de `col` o de un alias no declarado levanta `ErrorDeAlgebra`. La condicion
debe evaluar estrictamente a un booleano (`True` o `False`); cualquier otro tipo levanta `ErrorDeAlgebra`.

## Unicidad estatica de relaciones en `requiere`

Seccion ambigua: §2 ("Una relacion no puede aparecer dos veces en requiere, con condicion o sin ella").

Decision: la unicidad de las relaciones listadas en `requiere` se valida de forma estatica durante el parseo
de la medida (`_parsear_requiere`). No se admite que un mismo nombre de relacion aparezca mas de una vez, ya
sea como nombre simple `str` o en entradas con condicion `["filas", rel, ...]`. Detectar un duplicado levanta
`ErrorDeAlgebra` inmediatamente, con independencia de la evidencia provista.

