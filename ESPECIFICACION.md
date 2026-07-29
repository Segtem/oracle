# Especificación del álgebra

Versión `0.2`. **Escrita para ser rota**: el criterio de si sirve está al final, y es comprobable.

> **Qué cambió respecto de `0.1`, y por qué.** La implementación encontró dos cosas.
> **(a)** El acceso a datos pasó a ser **explícito** (`["campo", alias, nombre]`, `["hecho", alias]`)
> en vez de la forma corta `["penetracion", "a", "b"]` que publicaba la 0.1: si un string suelto
> significara «alias», un dato de texto que coincida con un alias cambiaría de sentido según el
> contexto. Es más verboso y no tiene casos raros.
> **(b)** Sólo **tres de los seis operadores están implementados**, porque son los únicos que piden
> las medidas que existen. Es la regla de este documento aplicada a sí mismo — ver §3.

Regla de diseño que gobierna todo el documento: **no se agrega un operador hasta que una segunda
medida lo necesite.** Es lo único que evita que esto se vuelva el proyecto que reemplaza al proyecto.

---

## 1. Hechos y relaciones (L0)

Un **hecho** es un registro de campos escalares. Una **relación** es un conjunto nombrado de hechos
del mismo tipo. La evidencia es un mapa de relaciones:

```json
{
  "pieza":   [{"id": "Muro_A", "x": 100, "y": 100, "ex": 200, "ey": 25}],
  "mutante": [{"id": "firma_por_id", "apunta_a": "funcion._orden_visual", "murio": false}]
}
```

Nada más. Sin objetos, sin punteros, sin nulos implícitos. El **sensor** que produce la evidencia es
específico de cada dominio y vive con el productor, no acá.

## 2. Una medida es un dato

```json
["medida", "colocacion.interpenetracion",
  ["desde",
    ["unir", ["de", "pieza", "a"], ["de", "pieza", "b"]],
    ["donde", [">", ["penetracion", ["hecho", "a"], ["hecho", "b"]], 0]]],
  ["resumen", "max", ["penetracion", ["hecho", "a"], ["hecho", "b"]]],
  ["umbral", "<=", 0, "penetracion() ya descuenta la tolerancia de contacto"],
  ["alcance", "solape de AABB. NO ve la malla real, ni oclusión, ni si quedó flotando"]]
```

Una medida real, del catálogo que ya corre — sin `unir`, que todavía no tiene usuario:

```json
["medida", "proceso.test_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"], ["donde", ["==", ["campo", "m", "murio"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina…"],
  ["alcance", "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los que nadie escribió…"]]
```

Listas anidadas, serializable a JSON. De eso salen cuatro cosas que si no serían mecanismos aparte:

1. el **corpus** puede guardar medidas, no sólo evidencia;
2. el **inventario** de umbrales y de puntos ciegos es una consulta sobre las medidas;
3. la **mutación** es una transformación de datos, no un `sed` sobre archivos;
4. las **macros** (una medida que escribe medidas) no necesitan permiso del diseñador del lenguaje.

**Los testigos no se declaran.** Son las filas que sobrevivieron al último `donde`. Declararlos
aparte obliga a recorrer los datos dos veces y a mantener dos definiciones de lo mismo sincronizadas
a mano — el error concreto que motivó esta especificación (ver
[`004-testigos-duplicados`](corpus/proceso/)).

## 3. Los operadores

Seis. Cada uno toma relaciones y devuelve una relación: **eso es la clausura**, y es lo que permite
que una medida consuma la salida de otra sin ningún caso especial.

| Operador | Forma | Qué hace |
|---|---|---|
| `de` | `["de", relación, alias]` | fuente |
| `donde` | `["donde", pred]` | filtra — **define los testigos** |
| `con` | `["con", nombre, expr]` | agrega una columna derivada |
| `unir` | `["unir", izq, der, modo?]` | producto; `modo` = `"todos"` (default) o `"izquierda"` |
| `agrupar` | `["agrupar", [claves], [nombre, agg, expr]]` | agrupa y agrega |
| `resumen` | `["resumen", agg, expr]` | colapsa a un escalar — **la medición** |

Agregados: `max`, `min`, `suma`, `promedio`, `contar`. `contar` **no evalúa la expresión**: cuenta
filas. Los agregados sobre cero filas dan `0`.

`desde` no es un operador: es la tubería que los encadena (`["desde", fuente, paso, paso, …]`).

### Implementados: tres de seis

La regla *no se agrega un operador hasta que una segunda medida lo necesite* aplica también a
**implementarlos**: un operador sin usuario es un operador sin verificar. Hoy corren `de`, `donde` y
`resumen`, que es todo lo que piden las ocho medidas del catálogo. Los otros tres levantan un error
que dice su disparador, así que cuando hagan falta no hay que adivinar por qué faltan:

| Operador | Se implementa cuando aparezca… |
|---|---|
| `unir` | el catálogo de geometría: «pares de piezas que se clavan» es un producto |
| `agrupar` | contar por grupo — importadores por módulo, y con eso la «ausencia» de §7 |
| `con` | una medida que reuse una columna derivada en más de un paso |

### Acceso a los datos

Explícito siempre: `["campo", alias, nombre]` para un campo, `["hecho", alias]` para el hecho entero,
`["col", nombre]` para una columna derivada. Todo lo demás en posición de expresión es un **literal**.

Comparar contra un campo ausente **levanta un error**, no devuelve `False`: en una medida eso es casi
siempre un nombre mal escrito, y un `False` silencioso lo convertiría en un verde.

### Funciones escalares

Los predicados de dominio (`penetracion`, `distancia`, `desvio_de_grilla`) entran como **funciones
escalares declaradas**, con nombre, aridad y unidad. Es el mecanismo de UDF de SQL, y es el escape
hatch honesto: evita inventar un lenguaje que sepa geometría.

Se **declaran**, no se importan sueltas: así aparecen en el inventario y se pueden contar y discutir
igual que los umbrales.

## 4. Los tres niveles con un solo mecanismo

Como una medida es un hecho, `medida` es una relación más y las medidas sobre medidas son medidas
normales:

```json
["medida", "meta.umbral_sin_defensa",
  ["desde", ["de", "medida", "m"], ["donde", ["==", ["campo", "m", "porque"], ""]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un número que nadie puede discutir es una métrica esperando a volverse objetivo"],
  ["alcance", "ve si la defensa está VACÍA. NO ve si la defensa es mala, circular o mentirosa"]]
```

Ese `alcance` es el ejemplo de por qué el campo es obligatorio: la medida es útil y es
superficialísima, y decirlo evita que se lea como más de lo que es.

## 5. Modo simulación

La segunda fuente de evidencia. En vez de consultar hechos estáticos, se corre el sistema y se
observan los hechos que emergen:

```
evento(t, actor, qué, dónde)
```

**No es otro sistema.** Una traza es una relación, y las mismas seis operaciones la miden. La
simulación es un *productor de hechos*, no un segundo oráculo.

Importa porque es la mitad más resistente a Goodhart: se puede sastrear un umbral, es mucho más
difícil sastrear un jugador simulado.

## 6. Criterio de aceptación de esta especificación

Comprobable, y si falla el diseño está mal:

1. una medida sobre **piezas** y una medida sobre **nodos de un grafo** usan los mismos operadores,
   sin adaptador;
2. una medida **sobre medidas** no introduce ninguna construcción nueva;
3. el corpus guarda los tres niveles con el mismo formato;
4. **todo caso del corpus que declara una medida se pone en rojo** con esa medida. El que quede verde
   señala lenguaje faltante o medida mal escrita, y hay que decir cuál. Los casos con
   `sin_medida_todavia` **siguen verdes a propósito**: son el hueco declarado, no una falla del
   evaluador — y el número de casos sin medida es una métrica del marco, que tiene que bajar.

**Condición de parada:** si los casos del corpus no se ponen rojos con este juego chico de
operadores, se para y se rediseña — no se agregan operadores hasta que entren.

## 7. Preguntas abiertas

Escritas porque una especificación que finge no tener huecos es peor que una con huecos marcados.

- **Ausencia.** «Módulo sin ningún importador» es un anti-join. Hoy se expresa con
  `unir … "izquierda"` más un test de falta, pero eso mete el concepto de **nulo**, que es la peor
  verruga de SQL. Alternativa: `agrupar` + `contar == 0`, que evita el nulo a costa de ser más
  verboso. **Sin resolver.**
- **Recursión.** «Alcanzable desde» (el cierre de imports, la conectividad de un grafo) no se expresa
  con estos seis operadores. Es la misma pared que hizo falta `WITH RECURSIVE` en SQL. Candidatos: un
  operador `cierre`, o una función escalar que reciba la relación. **Diferido hasta que dos medidas lo
  pidan.**
- **Igualdad de flotantes.** `["==", x, 0]` sobre medidas en cm es una trampa. Probablemente todo
  umbral necesite una tolerancia explícita, lo que cambia la forma de `umbral`.
- **Orden.** `resumen max` no necesita orden, pero «piezas consecutivas a lo largo de una curva» sí.
  ¿El orden es un campo del hecho, o una propiedad de la relación?

## 8. Lo que esta versión deliberadamente no tiene

Sintaxis propia con parser (la forma de dato alcanza), macros (se habilitan cuando aparezca la quinta
medida con la misma forma), transporte por red (cero consumidores remotos), y optimizador (los
volúmenes son chicos; el día que no lo sean, ser declarativo es justo lo que permite agregarlo).
