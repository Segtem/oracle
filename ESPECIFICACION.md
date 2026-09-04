# Especificación del álgebra

Versión `0.5`, declarada de forma **legible por máquina** en `nucleo/version.py`
(`VERSION_ALGEBRA`). Esta prosa la cita, no la define: la define el dato, y la regla de qué cambio
sube qué parte del número está en §0. **Escrita para ser rota**: el criterio de si sirve está al
final, y es comprobable.

> **Qué cambió respecto de `0.1`, y por qué.** La implementación encontró dos cosas.
> **(a)** El acceso a datos pasó a ser **explícito** (`["campo", alias, nombre]`, `["hecho", alias]`)
> en vez de la forma corta `["penetracion", "a", "b"]` que publicaba la 0.1: si un string suelto
> significara «alias», un dato de texto que coincida con un alias cambiaría de sentido según el
> contexto. Es más verboso y no tiene casos raros.
> **(b)** Los operadores se incorporan sólo cuando los piden medidas reales. `con` y la unión
> izquierda se retiraron de la especificación activa al no alcanzar dos usuarios — ver §3.
> **(c)** La 0.3 resuelve la contradicción entre “conjunto” y la multiplicidad real: una relación es
> una **bolsa sin orden semántico**. La decisión completa está en
> [`DECISION-001-RELACIONES-COMO-BOLSAS.md`](DECISION-001-RELACIONES-COMO-BOLSAS.md).
> **(d)** La 0.4 hace explícito de dónde sale cada umbral con el campo `segun`: medición,
> contrato, convención o tanteo.
> **(e)** La 0.5 permite que una escalar declare la unidad de cada argumento; una declaración vieja
> sigue cargando, pero su unidad no se considera derivable hasta completar ese dato.

Regla de diseño que gobierna todo el documento: **no se agrega un operador hasta que una segunda
medida lo necesite.** Es lo único que evita que esto se vuelva el proyecto que reemplaza al proyecto.

---

## 0. La versión del lenguaje

La versión es un dato, no una frase. Vive en `nucleo/version.py` como `VERSION_ALGEBRA`, con la
forma `MAYOR.MENOR` (dos enteros). Sin una regla que diga qué cambio sube qué parte, el número es
decorativo; con ella, la incompatibilidad se detecta en vez de descubrirse.

**`MENOR` sube** cuando el álgebra **gana** algo sin cambiar el significado de lo que ya valía: un
nodo opcional nuevo (`requiere`), un operador nuevo (`agrupar`, `unir`), un agregado nuevo, una
escalar declarada nueva, una relación de traza nueva. Quien no usa lo nuevo queda exactamente igual;
quien *implementa el álgebra completo* —una referencia independiente— quedó incompleto y tiene que
volver a verificarse. De `0.2` a `0.3` subió la menor (entraron `agrupar`, `requiere` y `clave`);
de `0.3` a `0.4` volvió a subir porque el umbral ganó `segun`.
De `0.4` a `0.5` subió porque `@escalar` ganó `unidades_argumentos`.

**`MAYOR` sube** cuando cambia el **significado o el contrato** de algo que ya existía: la semántica
de un operador (qué hace `min`/`max` con booleanos), la forma canónica de una medida, una validación
que hacía cargar lo que ahora se rechaza, o quitar/renombrar un operador. Eso rompe a todo
consumidor, use o no la parte cambiada. De `0.3` a `1.0`, y la menor vuelve a `0`.

**Cómo se comprueba.** El núcleo publica lo que implementa. Un proyecto puede declarar en
`oracle.json` la versión que necesita (`"algebra": "0.5"`); si no es compatible, la carga falla
cerrado con un mensaje que dice cuál hay y cuál se pidió, y quien no la declara sigue funcionando.
La compatibilidad es la del párrafo anterior: misma `MAYOR` y `MENOR` al menos tan nueva como la
pedida. Una implementación de referencia, en cambio, declara contra qué versión se escribió y el
arnés del diferencial la compara con la del núcleo antes de emitir un fixture: la referencia se fija
a una versión **exacta**, porque un agregado puede no romper a un consumidor y sí a un evaluador que
no conoce el nodo nuevo.

### La superficie tiene su propia versión

La superficie infija declara la suya, `VERSION_SINTAXIS`, con la misma forma `MAYOR.MENOR` y la
misma maquinaria (`parsear`, `compatible`, `VersionInvalida`). La regla aplica a las medidas
(`.oracle`) y a los casos del corpus (`.caso`): la superficie es cómo se escribe y el JSON es cómo
se guarda, cargándose ambos por igual. La distinción que importa es entre el **lector** y el
**impresor**, y no envejecen igual: un archivo `.oracle` o `.caso` viejo se **lee**; el
impresor no lo toca. Por eso **una sola versión alcanza**, y alcanza porque la comparación es
asimétrica —el archivo declara contra qué se escribió y el núcleo declara qué implementa—:

- un archivo viejo leído por un núcleo nuevo es compatible si la mayor coincide y la menor del
  núcleo es al menos la declarada;
- un archivo nuevo —que usa una palabra nueva— leído por un núcleo viejo falla cerrado, porque el
  núcleo declara una menor anterior a la que el archivo pide.

No hacen falta dos números: la ida y vuelta lector↔impresor es un invariante interno que
`sintaxis.py --verificar` comprueba, y el impresor sólo cambia en dos casos —o el lector aprende una
forma nueva (MENOR), o deja de aceptar una que ya se publicaba (MAYOR)—.

**`MENOR` sube** cuando el lector **gana** una forma sin cambiar el significado de lo que ya valía:
una palabra nueva que antes era un error de sintaxis, un separador nuevo. Un archivo escrito contra
la menor anterior se sigue leyendo idéntico.

**`MAYOR` sube** cuando el lector **cambia** lo que ya aceptaba: una forma que hoy se lee pasa a
significar otra cosa, o pasa a ser un error de lectura. Eso rompe a todo archivo que la use.

Casos concretos:

1. **Agregar una palabra nueva que antes era un error de sintaxis** → **MENOR**. Quien no la usa no
   se entera; un archivo viejo sigue cargando.
2. **Cambiar cómo se imprime algo sin cambiar qué se acepta al leer** → **no sube nada**. El archivo
   viejo se lee igual porque el lector no cambió, y el que el impresor reescribe lo sigue leyendo un
   lector viejo porque la forma impresa ya era aceptada. (Si el cambio de impresión mete una forma
   que el lector tiene que aprender, es el caso 1, MENOR; si hace que una forma ya publicada deje de
   leerse, es MAYOR.)
3. **Que una forma que hoy se acepta pase a ser un error** → **MAYOR**. Un archivo que la use deja
   de cargar.

Un `.oracle` puede declarar contra qué versión se escribió, con una primera línea
`sintaxis MAYOR.MENOR`. Es opcional —los archivos de hoy no la declaran y siguen cargando— y es
parte de la superficie, no un comentario pegado arriba. Declarar una versión incompatible falla
cerrado al cargar, con un mensaje que dice las dos versiones. `oracle.json` puede pedir una versión
de sintaxis (`"sintaxis": "0.1"`) con la misma regla que pide la del álgebra.

---

## 1. Hechos y relaciones (L0)

Un **hecho** es un registro de campos escalares. Una **relación** es una bolsa nombrada de hechos del
mismo tipo. La evidencia es un mapa de relaciones:

```json
{
  "pieza":   [{"id": "Muro_A", "x": 100, "y": 100, "ex": 200, "ey": 25}],
  "mutante": [{"id": "firma_por_id", "apunta_a": "funcion._orden_visual",
               "detecciones_conductuales": 0, "rechazos_del_algebra": 0}]
}
```

Nada más. Sin objetos, sin punteros, sin nulos implícitos. El **sensor** que produce la evidencia es
específico de cada dominio y vive con el productor, no acá.

La multiplicidad cuenta y el orden de almacenamiento no. Dos apariciones idénticas son dos hechos:
`contar` devuelve 2, `suma` usa ambas y un producto conserva ambas. Oracle no deduplica porque no
puede inventar una identidad genérica.

Un dominio que SÍ conoce su identidad puede **declarar una clave de unicidad** para una relación,
poniendo a la cabeza de su lista de hechos un nodo `["clave", [<campo>, …]]`:

```json
{
  "pieza": [["clave", ["id"]],
             {"id": "Muro_A", "x": 100}, {"id": "Muro_B", "x": 300}]
}
```

La clave es **opcional** y se valida **antes de medir**, fail-closed: si dos hechos repiten la clave
declarada, la evaluación levanta un error que nombra la clave responsable y la fila que la viola — no
un veredicto verde, no un error genérico. Un campo de la clave ausente en un hecho también es error:
una identidad a medias no se puede comprobar, y un nulo implícito la dejaría sin comprobar en
silencio. Sin el nodo, la relación es exactamente la bolsa de siempre, y la multiplicidad intencional
sigue siendo expresable sin declarar nada.

### 1.1 Las relaciones que el lenguaje emite

Casi toda la evidencia la produce un sensor del dominio. Pero hay relaciones que **produce el
propio marco**, sobre sí mismo: son las que hacen posible L2 —medidas sobre medidas— y las que
permiten que un veredicto sobre el catálogo sea un dato y no un `if` escondido en `tools/`.

Se distinguen porque `catalogos/meta/` las consume y ningún proyecto las declara. La lista es
derivable —`relaciones_del_lenguaje_declaradas()` la calcula leyendo los emisores— y hay una
medida, `meta.toda_relacion_del_lenguaje_esta_en_la_referencia`, que exige que cada una aparezca
acá. Esta sección no puede envejecer en silencio.

| relación | qué describe | quién la emite |
|---|---|---|
| `medida` | cada medida del catálogo, reificada: su comparador, umbral, `segun`, `alcance` | `nucleo/medida.py` |
| `termino` · `fuente` · `paso_de_medida` · `nodo` | las piezas de una medida vistas como árbol: sus términos, de dónde saca filas, cada paso de la tubería y cada nodo lógico | `nucleo/medida.py` |
| `dependencia_de_medida` | cada relación de la que una medida depende y por qué vía (`fuente` o `requiere`); une las dos para que una política sobre dependencias se escriba una vez | `nucleo/medida.py` |
| `requiere` | qué relaciones declara necesitar una medida para concluir | `nucleo/medida.py` |
| `caso` | cada caso del corpus: su polaridad, su `procedencia`, si su medida existe, y —desde `DECISION-009`— si es propio o de una biblioteca | `nucleo/marco.py` |
| `medida_en_uso` | cuántos casos evalúan cada medida y cuántos mutantes le sobreviven | `nucleo/marco.py` |
| `sombra` | qué medidas heredadas se miden pero todavía no obligan, desde cuándo, por qué y hace cuántos días | `nucleo/marco.py` |
| `relacion_documentada` | si cada relación del lenguaje está nombrada en esta especificación | `nucleo/marco.py` |
| `verbo_del_cli` | cada verbo que el comando acepta y si la ayuda lo nombra | `nucleo/marco.py` |
| `opcion_del_vocabulario` | cada opción de un vocabulario cerrado, con cuántas palabras la explican y si el manual la muestra | `nucleo/marco.py` |
| `mutador_excluido` | cada exclusión de mutador declarada, con su premisa, si algún autor ofrece el mutador y si el registro del arnés lo tiene | `nucleo/marco.py` |
| `relacion_declarada` · `campo_declarado` · `ambito_de_relacion` | las relaciones que un proyecto declara, sus campos con unidad y dónde obliga cada relación | `nucleo/relacion.py` |
| `cantidad_comparada` | cada comparación de una medida y si su unidad se puede derivar (L−1) | `nucleo/unidad.py` |
| `referente_declarado` · `referente_comparado` | la identidad y la frescura de aquello que se midió (L−2) | `nucleo/referente.py` |
| `equivalencia` | dos formas que deberían dar lo mismo, para las propiedades metamórficas | `tools/metamorficas.py` |
| `paso` · `producto` · `ancestro` | lo que una evaluación trazada produjo: cada paso, el tamaño del producto de un `unir`, y la ascendencia de un nodo | `nucleo/algebra.py` |
| `campo_diagnostico` | cada valor de texto del diagnóstico local y si contiene algo del dominio | `nucleo/diagnostico.py` |

**Ninguna de estas relaciones se declara en `relaciones/`.** Un proyecto que definiera una con el
mismo nombre estaría pisando una del lenguaje, y por eso los nombres se reservan.

### 1.2 Los vocabularios cerrados, y el manual que sale de ellos

Cinco campos del lenguaje admiten un conjunto cerrado de valores: los seis operadores de una
tubería, el `segun` de un umbral, y la `etiqueta`, la `procedencia` y el `como_se_detecto` de un
caso. Es la parte que más se equivoca quien recién llega, porque los nombres se parecen entre sí.

Cada opción **declara su significado junto a su nombre** —`nucleo/vocabulario.py` y
`nucleo/caso.py`—, y de esa única fuente salen las dos cosas que importan:

- el error que ve quien escribe un valor inválido, en el momento exacto en que se equivoca, con
  las opciones y qué es cada una;
- `oracle manual`, que no es un documento aparte sino una **vista** de esas declaraciones. La
  misma salida en `--html` es la página del sitio, y en `--man` son páginas de manual: tres vistas
  de una sola fuente, ninguna escrita a mano.

Un manual generado no puede quedar viejo, salvo por una grieta: que aparezca un vocabulario y nadie
lo anote en el registro que dice qué mostrar. Eso lo mide
`meta.todo_vocabulario_cerrado_esta_en_el_manual`; que ninguna opción quede sin explicar lo mide
`meta.toda_opcion_del_vocabulario_declara_su_sentido`.

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

**La forma canónica admite un nodo opcional `requiere`, y va antes de `alcance`:**

```json
["medida", "<id>", <tubería>, <resumen>, <umbral>,
  ["requiere", "<relación>", …],
  ["alcance", "<qué NO ve>"]]
```

Es el espejo de `alcance`: uno declara qué NO ve la medida, el otro **qué NECESITA ver para
concluir**. Si alguna de las relaciones listadas viene vacía, la evaluación no mide: devuelve
`SIN EVIDENCIA`, que no es verde y tampoco es un rojo del mundo. Existe porque el álgebra no puede
expresarlo —un agregado sobre cero filas da `0` y un umbral `<= 0` lo lee como éxito— y la ausencia
total salía verde justo cuando el mundo estaba peor; el caso completo está en §8.

En la terminología de Shi, Zhang y Cui, *A Programming Paradigm for Spatiotemporal
Composability*, §3.2, `requiere` es un **coefecto**: una especificación de dependencias que se
contrasta contra el contexto disponible antes de ejecutar. Oracle toma sólo esa mitad declarativa.
No toma la reactividad del paper —clasificar cada cambio del contexto para activar y desactivar
componentes— porque la evidencia no cambia durante una evaluación; si falta una relación, se corta
fail-closed con `SIN EVIDENCIA`.

Una medida sin el nodo se comporta exactamente como antes y su forma canónica **no cambia**: son seis
elementos, no siete. Un evaluador tiene que aceptar las dos longitudes.

Una medida real, del catálogo que ya corre — sin `unir`, que todavía no tiene usuario:

```json
["medida", "proceso.test_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"],
    ["donde", ["y", ["==", ["campo", "m", "detecciones_conductuales"], 0],
                    ["==", ["campo", "m", "rechazos_del_algebra"], 0]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina…"],
  ["alcance", "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los que nadie escribió…"]]
```

Listas anidadas, serializable a JSON. De eso salen cuatro cosas que si no serían mecanismos aparte:

1. el **corpus** puede guardar medidas, no sólo evidencia;
2. el **inventario** de umbrales y de puntos ciegos es una consulta sobre las medidas;
3. la **mutación** es una transformación de datos, no un `sed` sobre archivos;
4. las **macros** (una medida que escribe medidas) no necesitan permiso del diseñador del lenguaje.

La mutación de medidas cubre un denominador explícito: umbral y filtros completos; cada fuente que
puede sustituirse por otra relación nombrada en la misma medida; comparadores, lógicos y booleanos de
expresiones; un agregado alternativo por sitio; y referencias de campo sustituibles dentro del mismo
alias o espacio derivado. Los ids incluyen la ruta JSON del sitio. No muta nombres de UDF, aridades,
defensas ni alcances: las dos primeras fallan al cargar, y las dos últimas fallan al cargar **y**
además quedan reificadas como medidas de L2 (§4).

**Los testigos no se declaran.** Son las filas que sobrevivieron al último `donde`. Declararlos
aparte obliga a recorrer los datos dos veces y a mantener dos definiciones de lo mismo sincronizadas
a mano — el error concreto que motivó esta especificación (ver
[`004-testigos-duplicados`](corpus/proceso/)).

## 3. Los operadores

Cinco. Cuatro toman relaciones y devuelven una relación: **eso es la clausura**, y es lo que permite
encadenarlos en cualquier orden sin un solo caso especial. `resumen` es el que la rompe a propósito,
porque colapsa a un escalar: por eso va último y una sola vez, y por eso **la clausura es sobre
filas, no sobre medidas**.

Conviene decirlo fuerte, porque la versión corta de esta frase engañaba: una medida termina en un
escalar y un umbral, y ahí se acaba. **Ninguna medida puede consumir los testigos ni el veredicto de
otra**, y eso no es una limitación pendiente sino una decisión tomada y registrada en
[`DECISION-002`](DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md). Las preguntas que esa decisión deja
afuera —«¿qué medidas comparten testigos?»— se responden en L2, midiendo el catálogo como relación.

| Operador | Forma | Qué hace |
|---|---|---|
| `de` | `["de", relación, alias]` | fuente |
| `donde` | `["donde", pred]` | filtra — **define los testigos** |
| `unir` | `["unir", izq, der]` | producto cartesiano |
| `agrupar` | `["agrupar", [claves], [nombre, agg, expr]]` | agrupa y agrega |
| `resumen` | `["resumen", agg, expr]` | colapsa a un escalar — **la medición** |

Agregados: `max`, `min`, `suma`, `promedio`, `contar`. `contar` **no evalúa la expresión**: cuenta
filas. Los agregados sobre cero filas dan `0`. `suma` y `promedio` aceptan números finitos y
booleanos como indicadores 0/1; `min` y `max` exigen escalares homogéneos y comparables. Un valor no
finito o una mezcla incompatible es error de álgebra, no un veredicto.

`desde` no es un operador: es la tubería que los encadena (`["desde", fuente, paso, paso, …]`).

### Lenguaje activo: cinco operadores

La regla *no se agrega un operador hasta que una segunda medida lo necesite* aplica también a
**publicarlos**: un operador sin usuario es un operador sin verificar. Corren `de`, `donde`,
`resumen`, `unir` y `agrupar`.

| Operador | Estado |
|---|---|
| `unir` | ✅ entró con el catálogo de geometría: «pares de piezas que se clavan» es un producto |
| `agrupar` | ✅ entró con la AUSENCIA — ver §8 |

`con` y la unión izquierda no son promesas pendientes ni sintaxis aceptada: no tienen dos usuarios
reales y por eso una declaración que los use falla al cargar. Si aparecen esos usuarios, vuelven con
sus casos, semántica y mutantes; no como ramas dormidas.

Un grupo **no es un hecho**: es un resumen. Las filas que salen de `agrupar` no llevan alias —los
hechos se consumieron— sino columnas derivadas, que se leen con `["col", nombre]`. Ese accesor existía
desde el principio y recién acá encontró su usuario.

### Acceso a los datos

Explícito siempre: `["campo", alias, nombre]` para un campo, `["hecho", alias]` para el hecho entero,
`["col", nombre]` para una columna derivada. Todo lo demás en posición de expresión es un **literal**.

Comparar contra un campo ausente **levanta un error**, no devuelve `False`: en una medida eso es casi
siempre un nombre mal escrito, y un `False` silencioso lo convertiría en un verde.

### Funciones escalares

Los predicados de dominio (`penetracion`, `distancia`, `desvio_de_grilla`) entran como **funciones
escalares declaradas**, con nombre, aridad, unidad de retorno y unidad de cada argumento. Es el
mecanismo de UDF de SQL, y es el escape
hatch honesto: evita inventar un lenguaje que sepa geometría.

Se **declaran**, no se importan sueltas: así aparecen en el inventario y se pueden contar y discutir
igual que los umbrales.

El contrato declarativo incluye un nombre con gramática cerrada, aridad mínima y máxima (o
variádica), unidad de retorno, `unidades_argumentos` y procedencia. `sin_unidad` se escribe de forma
explícita para un hecho entero o un texto; omitir la tupla conserva compatibilidad de carga pero deja
la cantidad como `sin_declarar` en L−1. Una UDF externa sigue siendo **código Python con los mismos permisos
que Oracle**: sólo se activa con `--confiar-escalares`, durante una operación, y el registro anterior
se restaura al terminar o fallar. `--help`, `--relaciones`, `--nueva` y `--escalares` sin esa bandera
son modos de inspección: pueden mostrar archivos o el inventario base, pero no importan código del
proyecto.

## 4. Los tres niveles con un solo mecanismo

Como una medida es un hecho, `medida` es una relación más y las medidas sobre medidas son medidas
normales:

```json
["medida", "meta.todo_tanteo_explica_por_que",
  ["desde", ["de", "medida", "m"],
    ["donde", ["y", ["==", ["campo", "m", "segun"], "tanteo"], ["==", ["campo", "m", "porque"], ""]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "si un número es tanteo, decir por qué todavía importa", "contrato"],
  ["alcance", "ve sólo tanteos sin explicación. NO juzga si la explicación alcanza"]]
```

Ese `alcance` es el ejemplo de por qué el campo es obligatorio: la medida es útil y es
superficialísima, y decirlo evita que se lea como más de lo que es.

Tres reglas que antes eran `raise` de `nucleo/medida.py` quedaron reificadas así, como medidas del
catálogo base: `meta.todo_umbral_declara_de_donde_sale`, `meta.ninguna_medida_sin_alcance` y
`meta.ningun_umbral_flotante_de_igualdad`. Las dos primeras conservan el `raise` de carga además de
la medida — son contratos fail-closed, y la medida las vuelve inspeccionables y discutibles —; la
tercera sólo vive en la medida y en `algebra.comparar`, porque un umbral `== 3.14` está bien formado
y su rechazo es un juicio, no un contrato. La distinción completa está en `INFORME.md`.

## 5. Modo simulación — ✅ IMPLEMENTADO

La segunda fuente de evidencia. En vez de consultar hechos estáticos, se corre el sistema y se
observan los hechos que emergen:

```
evento(corrida, t, actor, que, …)
corrida(id, escenario, semilla, pasos, razon, determinista)
```

**No es otro sistema.** Una traza es una relación, y las mismas operaciones la miden sin cambio
alguno. La simulación es un *productor de hechos*, no un segundo oráculo.

Dos reglas del contrato, y las dos salieron de equivocarse primero:

- **ningún campo de veredicto.** La primera versión tenía `gano: bool`, que es un concepto de un
  dominio metido adentro del núcleo. Una corrida termina por una `razon`; si esa razón es aceptable lo
  decide una medida. Lo mismo con «quedó gente en la cola»: es un hecho del resumen, no una razón.
- **el determinismo se comprueba.** Cada corrida se ejecuta dos veces con la misma semilla y
  `determinista` es un hecho. Una corrida irreproducible no puede ser material de corpus.

Importa porque es la mitad más resistente a Goodhart: un umbral se afloja cambiando un número; lo que
emerge de correr el sistema, no. Y produce el desacuerdo que la primera mitad no puede ver: **«existe»
y «se llega» no son lo mismo.**

## 6. Fixtures diferenciales

El esquema vigente es `oracle.diferencial/v1`. Todo fixture declara su versión y una sección
`frescura` con cuatro huellas SHA-256: emisor, fuentes de referencia, catálogo canónico de las
medidas usadas y configuración del dominio. Las rutas son relativas a la raíz del proyecto o a su
padre inmediato; no se aceptan rutas absolutas ni ancestros arbitrarios. Si una huella actual no
coincide, el fixture está **vencido** y no se evalúa.

En el formato `escenarios`, `referencia_ok` conserva únicamente la respuesta global de la
implementación independiente. `oracle_al_generar.global_ok` y
`oracle_al_generar.por_medida` guardan la fotografía de Oracle al emitirlo. La primera comprueba el
acuerdo independiente del conjunto; la segunda detecta cambios individuales, incluso si dos errores
se compensan y el `AND` global permanece igual. Una fotografía individual no se presenta como una
referencia independiente.

La serialización es JSON canónico con orden estable, sin `NaN`; toda aleatoriedad deriva su semilla
de SHA-256 y cualquier repositorio temporal fija las fechas que intervienen en sus identificadores.
Regenerar dos veces con las mismas entradas debe producir exactamente los mismos bytes.

## 7. Criterio de aceptación de esta especificación

Comprobable, y si falla el diseño está mal:

1. una medida sobre **piezas** y una medida sobre **nodos de un grafo** usan los mismos operadores,
   sin adaptador;
2. una medida **sobre medidas** no introduce ninguna construcción nueva;
3. el corpus guarda los tres niveles con el mismo formato (en superficie `.caso` para autoría o `.json` para almacenamiento);
4. **todo caso del corpus que declara una medida se pone en rojo** con esa medida. El que quede verde
   señala lenguaje faltante o medida mal escrita, y hay que decir cuál. Los casos con
   estado `abierto` **siguen verdes a propósito**: son el hueco declarado, no una falla del
   evaluador. Los casos `resuelto` y `limite_humano` conservan memoria, pero no cuentan como deuda.

**Condición de parada:** si los casos del corpus no se ponen rojos con este juego chico de
operadores, se para y se rediseña — no se agregan operadores hasta que entren.

## 8. Preguntas abiertas

Escritas porque una especificación que finge no tener huecos es peor que una con huecos marcados.

**Las cuatro originales están cerradas**, y sólo una de ellas amplió el álgebra: la ausencia trajo
`agrupar`. El orden resultó ser un campo del hecho, la recursión salió del álgebra hacia el sensor, y
la igualdad de flotantes se resolvió prohibiéndola. Que tres de cuatro se cierren sin agregar
operadores es la única prueba de que el juego chico alcanzaba.

- **Ausencia.** ✅ **RESUELTA, y sin nulos.** «Módulo sin ningún importador REAL» parecía pedir un
  anti-join, y un `LEFT JOIN` habría metido el concepto de nulo —la peor verruga de SQL—. La solución
  no necesitó operador nuevo más allá de `agrupar`: se agrupa sobre el producto **sin filtrar** y se
  agrega con `suma` sobre un predicado. Los booleanos suman 0 y 1, así que **un grupo donde nada casó
  da cero y sigue existiendo**:

  ```json
  ["unir", ["de","modulo","m"], ["de","importa","i"]],
  ["agrupar", [["modulo", ["campo","m","nombre"]]],
              [["reales","suma", ["y", ["==", ["campo","i","b"], ["campo","m","nombre"]],
                                       ["==", ["campo","i","es_test"], false]]]]],
  ["donde", ["==", ["col","reales"], 0]]
  ```

  Quedaba un límite, y era peor de lo que la palabra «límite» sugiere: si la relación del lado
  derecho está **vacía**, no hay pares, no hay grupos, el agregado sobre cero filas da `0` y un
  umbral `<= 0` lo lee como éxito. La medida **se ponía más verde cuanto peor estaba el mundo** —con
  un importador señalaba los módulos muertos; con ninguno, verde—. Declararlo en el `alcance` lo
  volvía visible sin cerrarlo, y esta sección lo llamaba RESUELTO tres líneas después de admitirlo
  (ver [`043-ausencia-total-sale-verde`](corpus/proceso/)).

  **Cerrado con `requiere`, y no con un operador.** No era expresable con los cinco: sin join no hay
  correlación, y `DECISION-002` prohíbe que una medida consuma la salida de otra. `["requiere",
  <relación>, …]` es un nodo opcional de la medida y el espejo exacto de `alcance` —uno declara qué
  NO ve, el otro qué NECESITA ver—; el evaluador comprueba la precondición **antes** de medir y
  emite `SIN EVIDENCIA`, que no es verde ni un rojo del mundo. El álgebra queda intacta.

  El caso general que esto expone: **un agregado sobre cero filas es indistinguible de un agregado
  que dio cero**, y sólo la medida sabe cuál de las dos cosas es.
- **Recursión.** ✅ **RESUELTA, y fuera del álgebra.** «Alcanzable desde» no se expresa con los
  operadores, y es la pared que hizo falta `WITH RECURSIVE` en SQL. Un operador `cierre` habría sido
  recursión en un lenguaje que se mantiene chico a propósito, con **un solo usuario**. La salida es
  más fiel a la doctrina: **la alcanzabilidad es un HECHO**, y producir hechos es trabajo del sensor.

  ```
  alcanzable(desde, hasta, saltos)
  ```

  El álgebra la mide como cualquier otra relación, sin saber nada de grafos. `nucleo/grafo.py` pone el
  BFS para que ningún sensor tenga que reimplementarlo — que era el otro riesgo, acumular la misma
  función en cada dominio. No es una evasión: es la misma línea que separa el sensor del juez en todo
  lo demás.
- **Igualdad de flotantes.** ✅ **RESUELTA negándose — y la prohibición ahora es L2.** El `raise`
  de carga que prohibía `==` sobre flotante en el umbral final se retiró: una medida con `== 0.3`
  está bien formada y se carga. El juicio de que es una mala idea vive en dos lugares: `algebra.comparar`
  sigue fallando cerrado al EVALUAR (la medida no puede producir un verde), y la política
  `meta.ningun_umbral_flotante_de_igualdad` la vuelve inspeccionable en L2, con su `porque`, su
  `alcance`, casos de corpus en las dos polaridades y la mutación probándola.

  La igualdad exacta sólo tiene sentido sobre cosas que se **cuentan** o se **nombran** —enteros,
  booleanos, textos—, y ahí sigue permitida. Sobre cosas que se **miden** hace falta una tolerancia,
  que es justamente lo que el lenguaje pide para todo umbral:

  ```json
  ["<=", ["cerca", a, b], tolerancia]
  ```

  Las comparaciones de ORDEN sobre flotantes siguen permitidas: una tolerancia *es* una comparación
  de orden.
- **Orden.** ✅ **RESUELTO: es un campo del hecho.** No puede ser una propiedad de la relación, porque
  L0 dice que una relación es una **bolsa sin orden semántico**. Entonces «consecutivos» es aritmética
  sobre el campo ordinal, y para eso alcanzó con declarar las escalares `mas` y `menos`.

  Ejemplo real: «la traza no tiene huecos» se expresa agrupando por corrida y comparando la cuenta de
  eventos contra el último instante — `["!=", ["col","registrados"], ["mas", ["col","ultimo"], 1]]`.
  Sin operador nuevo.

## 9. Presupuesto de evaluación

Una medida puede recibir evidencia hostil o simplemente demasiado grande. `LimitesAlgebra` forma
parte de la llamada de evaluación y acota tres amplificaciones: filas por relación, filas que puede
materializar un producto cartesiano y profundidad de una expresión. Los valores por defecto son
finitos; un consumidor puede elegir otros sin alterar un global compartido. Superar un límite es
`ErrorDeAlgebra`, nunca un veredicto verde ni una evaluación parcial.

Estos techos no son umbrales de una medida: protegen al evaluador y por eso no deciden nada sobre el
mundo medido.

## 10. Lo que esta versión deliberadamente no tiene

Sintaxis propia con parser (la forma de dato alcanza), transporte por red (cero consumidores remotos)
y optimizador. Los límites impiden una expansión no acotada; no vuelven eficiente una consulta grande.
