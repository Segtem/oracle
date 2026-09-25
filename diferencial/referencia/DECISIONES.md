# Decisiones de implementacion

Estas decisiones cubren puntos donde `ESPECIFICACION.md` y las decisiones locales dejaban margen.

## Forma de los testigos

Seccion ambigua: "Los testigos no se declaran".

Decision: `testigos` devuelve copias de las filas internas que sobrevivieron al ultimo `donde`.
Antes de `agrupar`, una fila tiene la forma `{"alias": {campo: valor}}`. Despues de `agrupar`,
una fila tiene columnas derivadas, por ejemplo `{"modulo": "b", "reales": 0}`.

Si la tuberia no contiene ningun `donde`, `testigos` es la relacion final de `desde`.

## `agrupar` con uno o varios agregados

La seccion 3 exige una lista de agregados, como el ejemplo de ausencia de la seccion 8:

```json
["agrupar", [["k", ["campo", "a", "id"]]], [["n", "contar", 1]]]
```

La forma con un agregado individual sin lista exterior es invalida.

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

Decision: `==` y `!=` levantan error cuando cualquiera de los operandos es flotante.

## Logicos sin cortocircuito

Seccion ambigua: semantica de `y` y `o`.

Decision: `y` y `o` evaluan todos sus operandos antes de combinar el resultado. Asi un campo ausente
o un valor no finito no queda oculto por cortocircuito.

## Operadores que pueden ser pasos de `desde`

Seccion ambigua: relacion entre operadores y tuberia.

Decision: `de` y `unir` son fuentes; cada lado de `unir` admite solo estas dos formas.
`desde` encabeza la tuberia, y `donde`, `agrupar` y `sin` son pasos. `resumen` queda fuera de la tuberia.

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
en errores se cuenta desde cero entre los hechos, sin contar el nodo `clave`.

## Limites con API fija

Seccion ambigua: la especificacion dice que `LimitesAlgebra` forma parte de la llamada, pero la tarea
fija la API publica como `evaluar(medida, evidencia, escalares=None)`.

Decision: el evaluador mantiene la firma publica y usa limites finitos internos: 100000 filas por
relacion, 1000000 filas por producto cartesiano, profundidad maxima de expresion 64 y 16 expansiones
maximas. Los campos se llaman `filas_por_relacion`, `producto_cartesiano`,
`profundidad_expresion` y `expansiones_maximas`, como en el nucleo.
Superarlos levanta `ErrorDeAlgebra`.

## `min`/`max` sobre booleanos

Seccion ambigua: los agregados `suma` y `promedio` aceptan booleanos como indicadores 0/1, pero
`min` y `max` solo piden escalares homogeneos y comparables.

Decision: los booleanos no se consideran ordenables para `min`/`max`. Si una medida necesita medir
booleanos como indicadores, debe usar `suma` o `promedio`.

## Version del algebra vigente (0.8)

Seccion ambigua: §0 ("La version del lenguaje").

Decision: la primera linea de §0 fija explicitamente las versiones vigentes: "Versiones vigentes: algebra 0.8, sintaxis 0.6, distribucion 0.25.2". En §3 y §8 se documenta la incorporacion de la anti-junta `sin` como nuevo operador de tuberia en 0.8. Por lo tanto, la version vigente del algebra es `"0.8"`, y `VERSION_ALGEBRA` se define en `"0.8"`.

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

## Paso de tuberia `sin` y no expresion de relacion aislada

Seccion ambigua: §3 ("Los operadores", tabla y subseccion "Lenguaje activo: seis operadores").

Decision: `sin` se especifica como "un paso de la tuberia, como `donde`". Por ende, solo es valido como paso subsiguiente dentro de `desde` (`["desde", fuente, ..., ["sin", ...], ...]`). Si `sin` aparece como la fuente inicial de `desde` (`desde[1]`) o en cualquier posicion donde se evalua una expresion de relacion (como operando de `unir` o subexpresion evaluada por `_evaluar_relacion`), levanta `ErrorDeAlgebra` (al igual que `donde` y `agrupar`).

## Forma estricta de la fuente en `sin`

Seccion ambigua: §3 (tabla "Forma": `["sin", ["de", relacion, alias], cond]`).

Decision: el segundo elemento de `sin` debe ser estrictamente un nodo de fuente simple `["de", relacion, alias]` con nombres de relacion y alias de tipo texto no vacios. No se admiten relaciones anonimas, sub-tuberias `desde` ni productos `unir` directamente dentro de `sin`. Cualquier variacion estructural levanta `ErrorDeAlgebra`.

## Verificacion de relacion ausente en `sin` con precedencia sobre filas vacias

Seccion ambigua: §3 ("Relacion ausente de la evidencia: el mismo error que de, aunque no llegue ninguna fila. Una anti-junta sobre algo que no se trajo no puede dar verde por omision").

Decision: se valida la existencia de la relacion requerida por `sin` en el diccionario de evidencia antes de comprobar si la lista de filas entrantes a `sin` esta vacia. Aunque la tuberia no haya producido filas entrantes (`filas == []`), si la relacion nombrada en `sin` no esta presente en `evidencia`, se levanta inmediatamente `ErrorDeAlgebra(f"relacion ausente: {relacion}")`.

## Deteccion de colision de alias en `sin` con relacion derecha vacia

Seccion ambigua: §3 ("Alias repetido: si el alias nuevo ya esta en la fila que llega, es error de algebra").

Decision: para toda fila entrante que llega a `sin`, si el `alias` nuevo introducido por `sin` coincide con algun alias ya presente en la fila o con una columna derivada existente, se levanta `ErrorDeAlgebra`. Esta comprobacion se realiza independientemente de si la relacion derecha en evidencia tiene hechos o esta vacia (`[]`).

## Evaluacion de la condicion de `sin` sin cortocircuito y con tipo booleano estricto

Seccion ambigua: §3 ("Sin cortocircuito: cond se evalua contra todas las filas de la relacion antes de decidir. Si una evaluacion es error, la medida es error, aunque otra fila ya hubiera correspondido: el orden de la bolsa no puede cambiar el veredicto").

Decision: para cada fila entrante, la condicion `cond` se evalua contra todos y cada uno de los hechos de la relacion derecha en su totalidad. No se interrumpe la iteracion al hallar el primer hecho que cumpla la condicion (`cumple == True`). Si la evaluacion sobre algun hecho falla con `ErrorDeAlgebra` (por ejemplo, campo ausente o funcion escalar fallida) o produce un valor que no es de tipo `bool`, se levanta `ErrorDeAlgebra` de inmediato. Solo si todos los hechos se evaluaron exitosamente sin error y ninguno de ellos cumplio la condicion (`not alguna_cumple`), la fila entrante pasa a la salida.

## Testigos y el operador `sin`

Seccion ambigua: §2 ("Los testigos no se declaran. Son las filas que sobrevivieron al ultimo donde"), §3 (tabla donde solo `donde` dice "define los testigos", mientras `sin` dice "anti-junta: deja las filas que ninguna fila de la relacion cumple").

Decision: `sin` no actualiza por si mismo la variable de testigos de la tuberia (`ultimos_testigos`). Si la tuberia contiene al menos un paso `donde`, `testigos` devuelve exactamente las copias de las filas que sobrevivieron al ultimo `donde`. Si la tuberia no contiene ningun paso `donde`, aplica la decision general preexistente ("Si la tuberia no contiene ningun donde, testigos es la relacion final de desde"), devolviendo las filas resultantes de `desde` tras ser filtradas por `sin`.

## Acceso a columnas derivadas tras `agrupar` en la condicion de `sin`

Seccion ambigua: §3 ("Despues de agrupar: vale igual; la condicion lee las columnas con ['col', nombre]").

Decision: cuando `sin` se ubica tras un paso `agrupar`, la fila entrante contiene columnas derivadas. Dentro de la condicion de `sin`, se accede a esas columnas mediante `["col", nombre]` y a los campos del hecho derecho mediante `["campo", alias, nombre]` o `["hecho", alias]`. Cualquier intento de usar `["campo", col, ...]` sobre una columna derivada levanta `ErrorDeAlgebra(f"{alias} no es un hecho")`, y usar `["col", alias]` levanta `ErrorDeAlgebra(f"{nombre} no es una columna derivada")`.

## Presupuesto de producto cartesiano en `sin`

Seccion ambigua: §3 ("Presupuesto: |filas que llegan| × |relacion| evaluaciones, contra el mismo limite de producto cartesiano que unir (§9)").

Decision: antes de iterar sobre los hechos de la relacion derecha, se verifica si `len(filas) * len(evidencia[relacion]) > limites.producto_cartesiano`. Si el producto excede dicho limite, se levanta `ErrorDeAlgebra("sin supera el limite de filas materializadas")`.

## Aislamiento del alias nuevo de `sin`

Seccion ambigua: §3 ("La salida conserva la fila tal como llego: el alias nuevo existe solo dentro de la condicion y un paso posterior no puede leerlo").

Decision: al pasar una fila que sobrevivio al filtro de `sin`, se copia la fila original entrante sin agregarle el alias del hecho derecho. Cualquier paso posterior en la tuberia que intente referenciar el alias de `sin` levantara `ErrorDeAlgebra("alias ausente: ...")`. Asimismo, dos pasos `sin` sucesivos en la misma tuberia pueden reutilizar el mismo nombre de alias sin considerarse colision.
