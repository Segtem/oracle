# Oracle — tutorial práctico: cómo se programa con Oracle

Guía complementaria a `ORACLE-PARA-NOTEBOOKLM.md`. Ese documento es el estudio integral (filosofía,
especificación completa, auditoría, historia). **Este es distinto a propósito**: es un tutorial —
aprender haciendo, de lo más simple a lo más compuesto, con ejemplos reales tomados del propio
repositorio y de un proyecto que ya lo usa en producción (Jam, un plugin de Unreal Engine). Si
`ORACLE-PARA-NOTEBOOKLM.md` responde «¿por qué existe Oracle?», este documento responde «¿cómo
escribo la primera medida, y la segunda, y la que necesita algo más complicado?».

- Generado: `2026-07-31`
- Todos los ejemplos de sintaxis fueron verificados contra el código fuente vigente de
  `Segtem/oracle` (rama `main`) y contra medidas reales en producción del proyecto Jam.

---

## 0. Oracle en una frase

Oracle es un **lenguaje de datos** (no una biblioteca de funciones) para escribir *medidas*: reglas
que toman hechos sobre lo que se construyó, calculan un número, lo comparan contra un umbral, y si el
umbral se viola, señalan exactamente qué filas lo violaron. Una medida se guarda como JSON — es datos,
no código — y por eso se puede inspeccionar, mutar, contar y medir con las mismas herramientas que
mide cualquier otra cosa.

Si nunca escribiste una medida, la meta de este documento es que después de leerlo puedas escribir la
tuya sin haber leído el evaluador.

---

## 1. El modelo mental: tres niveles, una sola representación

```
L0   evidencia   los HECHOS crudos: pieza(id, x, y, ex, ey) · mutante(id, apunta_a, murio)
L1   medidas     enunciados SOBRE L0: "ninguna pieza se clava en otra"
L2   medidas     enunciados SOBRE L1: "toda medida tiene al menos un mutante que la fija"
```

Lo importante: **L2 no necesita mecanismos nuevos**. Una medida (L1) es un dato, así que el catálogo
de medidas es una relación más (`medida(id, umbral_op, umbral_valor, porque, alcance, …)`), y se puede
medir con el mismo álgebra que mide piezas o eventos. Ese es el sentido de «metalenguaje»: no hay una
capa especial para «medir la medición».

```
                    ┌──────────────┐
   hechos  ───────► │   MEDIDA     │ ───────► veredicto (ok / no-ok, valor, testigos, alcance)
 (evidencia)         └──────────────┘
                    tubería → resumen → umbral
```

Una medida no produce "verdad": produce un **veredicto acotado** — un número, si pasó o no, las filas
que lo explican (testigos), y una declaración explícita de qué NO mira (alcance). Ningún veredicto se
presenta sin su alcance: por diseño, Oracle no permite escribir una medida que diga «todo bien» sin
decir también qué no miró.

---

## 2. Anatomía de una medida

Toda medida, en su forma completa (**canónica**), tiene esta forma — una lista de 6 elementos:

```json
["medida", "<id>",
  ["desde", <fuente>, <paso>, <paso>, "..."],
  ["resumen", "<agregado>", <expresion>],
  ["umbral", "<comparador>", <valor>, "<por qué ese número>"],
  ["alcance", "<qué NO ve esta medida>"]]
```

| Pieza | Qué es | Obligatorio |
|---|---|---|
| `id` | `dominio.nombre`, minúsculas ASCII, dígitos y `_` | sí |
| `desde …` | la tubería: de dónde salen los datos y qué filtros pasan | sí |
| `resumen` | cómo se colapsa la tubería a UN escalar — la medición en sí | sí |
| `umbral` | comparador + valor + **defensa en texto** de por qué ese valor | sí, con defensa no vacía |
| `alcance` | qué NO mira esta medida, en texto | sí, no puede estar vacío |

Dos reglas no son estilo, son validación dura: **una medida sin defensa del umbral no carga, y una
medida sin `alcance` no carga.** Fallan al leerse, no al usarse — antes de evaluar un solo hecho.

El ejemplo más simple posible del propio catálogo de Oracle:

```json
["medida", "proceso.test_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"], ["donde", ["==", ["campo", "m", "murio"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0,
    "un mutante que sobrevive es un test que no discrimina: pasa igual con el código roto"],
  ["alcance",
    "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los mutadores que nadie escribió"]]
```

Léelo en voz alta y ya sabés leer el 90% de las medidas que vas a encontrar: **«de la relación
`mutante`, alias `m`, quedate con los que tienen `murio == false`; contá cuántos quedaron; si son más
de 0, rojo — porque un mutante vivo es un test que no discrimina; y esto no ve los mutantes que nadie
llegó a escribir».**

Un detalle que sorprende la primera vez: **los testigos no se declaran aparte.** Los testigos —las
filas que se muestran cuando la medida da rojo, para que alguien pueda mirar el defecto— son
exactamente las filas que sobrevivieron al último `donde`. No hay una segunda función que las calcule,
porque escribir la misma condición dos veces es exactamente cómo se desincroniza (fue un defecto real
del proyecto — ver §7).

---

## 3. El álgebra: cinco operadores, y nada más

Toda la sintaxis sale de combinar **cinco operadores**. Cada uno toma filas (o hace de fuente) y
devuelve filas: esa clausura es lo que permite encadenarlos sin casos especiales.

| Operador | Forma | Qué hace |
|---|---|---|
| `de` | `["de", "<relacion>", "<alias>"]` | fuente: trae una relación y la etiqueta con un alias |
| `donde` | `["donde", <predicado>]` | filtra — **acá se definen los testigos** |
| `unir` | `["unir", <fuente_izq>, <fuente_der>]` | producto cartesiano de dos fuentes |
| `agrupar` | `["agrupar", [<claves>], [<agregados>]]` | agrupa filas y las resume a una fila por grupo |
| `resumen` | `["resumen", "<agregado>", <expresion>]` | colapsa TODA la tubería a un único escalar |

`resumen` no es un paso de la tubería: es lo último que se aplica, fuera de `desde`. Los primeros
cuatro sí van dentro de `["desde", …]`.

### 3.1 `de` — la fuente

```json
["de", "pieza", "a"]
```

Trae todos los hechos de la relación `pieza` y los etiqueta con el alias `a`. A partir de acá, cada
fila de la tubería tiene una clave `"a"` con el hecho completo.

### 3.2 `donde` — el filtro (y los testigos)

```json
["donde", [">", ["campo", "a", "volumen"], 0]]
```

Se queda sólo con las filas donde el predicado da `true`. **Es el único lugar donde se definen los
testigos**: lo que sobrevive acá es lo que se le muestra a un humano cuando la medida da rojo.

### 3.3 Acceso a los datos: siempre explícito

No hay azúcar corta tipo `"a.x"`. Tres accesores, y son los únicos que leen datos de una fila:

| Accesor | Forma | Devuelve |
|---|---|---|
| `campo` | `["campo", "<alias>", "<nombre>"]` | un campo de un hecho |
| `hecho` | `["hecho", "<alias>"]` | el hecho ENTERO (para pasarlo a una escalar) |
| `col` | `["col", "<nombre>"]` | una columna derivada por `agrupar` |

`["campo", "a", "volumen"]` — "en la fila actual, tomá el hecho con alias `a` y devolvé su campo
`volumen`". Comparar contra un campo que no existe **es un error**, no da `false`: así un nombre de
campo mal escrito no se disfraza de verde silencioso.

### 3.4 Comparadores y lógicos

```
==  !=  <  <=  >  >=       y   o   no
```

Reglas del álgebra que sorprenden si vienen de Python:

- **`bool` no es número.** `True == 1` da error acá, aunque en Python valga. Sólo `suma` y `promedio`
  tratan un booleano como indicador 0/1, y de forma explícita.
- **Igualdad exacta sobre flotantes está PROHIBIDA**, tanto en una expresión como en el umbral final.
  `["==", x, 3.0]` no carga. La razón: `0.1 + 0.2 != 0.3` en punto flotante, y una medida que compare
  así puede decir verde sin que nadie se entere. Usá una comparación de orden con tolerancia:
  `["<=", ["distancia", a, b], 0.5]`.
- **Los dos lados de una comparación tienen que ser del mismo tipo.** Comparar un número contra texto
  es error de álgebra, no `false`.
- `y` / `o` aceptan dos O MÁS operandos: `["y", p1, p2, p3]`.

### 3.5 `resumen` y los agregados

```json
["resumen", "contar", 1]
["resumen", "max", ["campo", "a", "volumen"]]
```

Cinco agregados: `contar`, `max`, `min`, `suma`, `promedio`. `contar` es especial: **no evalúa la
expresión**, sólo cuenta filas — por eso la convención es escribir `["resumen", "contar", 1]` (el `1`
es un relleno que nunca se mira). Sobre cero filas, cualquier agregado da `0`. `suma` y `promedio`
aceptan números o booleanos (0/1); `min` y `max` exigen valores del mismo tipo y comparables.

### 3.6 `unir` — comparar filas entre sí

```json
["desde",
  ["unir", ["de", "documento", "a"], ["de", "documento", "b"]],
  ["donde", ["y",
    ["==", ["campo", "a", "nombre"], ["campo", "b", "nombre"]],
    ["!=", ["campo", "a", "carpeta"], ["campo", "b", "carpeta"]]]]]
```

`unir` hace el producto cartesiano de dos fuentes: cada fila resultante tiene AMBOS alias
(`a` y `b`) disponibles. Es así como se comparan hechos entre sí — piezas que se tocan, documentos
homónimos, las dos puntas de un relevo. Acá: «dos documentos con el mismo nombre en carpetas
distintas» — el defecto real que motiva `vault.nombre_unico_en_el_vault` (un wikilink resuelve por
nombre, y dos homónimos lo dejan ambiguo).

Un `unir` consigo misma cuenta cada par dos veces (`(a,b)` y `(b,a)`) y también se empareja consigo
misma (`a==a`); normalmente hay que filtrar eso en el `donde` si el dominio lo requiere.

### 3.7 `agrupar` — cómo se expresa la AUSENCIA sin usar `null`

Este es el operador que más cuesta la primera vez, porque resuelve algo que en SQL pide un
`LEFT JOIN` con nulos — y acá **no hay nulos**. La pregunta es «¿qué módulos no tienen NINGÚN
importador real?» — una ausencia, no una presencia.

```json
["desde",
  ["unir", ["de", "modulo", "m"], ["de", "importa", "i"]],
  ["agrupar",
    [["modulo", ["campo", "m", "nombre"]]],
    [["reales", "suma",
      ["y", ["==", ["campo", "i", "b"], ["campo", "m", "nombre"]],
            ["==", ["campo", "i", "es_test"], false]]]]],
  ["donde", ["==", ["col", "reales"], 0]]]
```

El truco: se agrupa sobre el PRODUCTO sin filtrar primero, y se agrega con `suma` sobre un predicado
booleano. Como un booleano suma 0 o 1, un módulo sin ningún importador real da `reales = 0` — y el
grupo **sigue existiendo**, porque nunca se filtró antes de agrupar. Sin necesitar un concepto de nulo.

Forma general:

```json
["agrupar",
  [["<nombre_clave>", <expresion>], "..."],
  [["<nombre_agregado>", "<agregado>", <expresion>], "..."]]
```

Después de `agrupar`, las filas ya NO tienen los alias originales (`m`, `i` desaparecen: se
consumieron en el resumen). Se leen con `["col", "<nombre>"]`.

---

## 4. Las macros: la forma corta

**15 de las 18 medidas del catálogo de Oracle están escritas con una macro.** Una macro es azúcar
sintáctica que se expande a la forma canónica ANTES de construir la medida — el evaluador, la
mutación y el inventario nunca se enteran de que hubo una macro. `python tools/medida.py --expandir
<archivo>` te muestra la expansión.

| Macro | Forma | Para qué |
|---|---|---|
| `ninguno` | `["ninguno", id, relacion, alias, predicado, porque, alcance]` | ninguna fila debe cumplir el predicado — el 80% de los casos |
| `ninguno-par` | `["ninguno-par", id, relacion, aliasA, aliasB, predicado, porque, alcance]` | lo mismo, sobre PARES de la misma relación (envuelve un `unir` consigo misma) |
| `peor` | `["peor", id, relacion, alias, expresion, tolerancia, porque, alcance]` | el peor caso de una magnitud no puede pasar de una tolerancia |

### `ninguno` — el caso común

```json
["ninguno", "proceso.test_con_mutante_que_lo_mata",
  "mutante", "m",
  ["==", ["campo", "m", "murio"], false],
  "un mutante que sobrevive es un test que no discrimina",
  "cuenta mutantes DECLARADOS. NO ve los que nadie escribió"]
```

Expande EXACTO a la forma canónica de §2. `ninguno` cubre todo lo que se reduce a «filtrás lo que
ofende, contás, cero es el único número aceptable».

### `peor` — cuando el número importa, no la cuenta

```json
["peor", "snap.grilla",
  "pieza", "a",
  ["desvio_de_grilla", ["hecho", "a"], 100.0],
  1.0,
  "por debajo de 1 cm el desvío no se ve y no produce juntas visibles en una pieza de 4 m",
  "desvío del PIVOTE respecto de la grilla. NO ve si el pivote está donde debería dentro de la malla"]
```

Ejemplo real, en producción, del catálogo de geometría de Jam. Fijate el problema que resuelve
`peor`: escrita a mano, la tolerancia (`1.0`) aparecería DOS veces — una en el `donde` que filtra
(«¿superó 1 cm?») y otra en el `umbral` («¿el peor caso está por debajo de 1 cm?») — y nada garantiza
que sigan sincronizadas si alguien cambia una y no la otra. Ese fue un defecto real del proyecto (caso
`012` del corpus). `peor` recibe la tolerancia **una sola vez** y genera las dos apariciones desde ahí.

Expande a:

```json
["medida", "snap.grilla",
  ["desde", ["de", "pieza", "a"],
    ["donde", [">", ["desvio_de_grilla", ["hecho", "a"], 100.0], 1.0]]],
  ["resumen", "max", ["desvio_de_grilla", ["hecho", "a"], 100.0]],
  ["umbral", "<=", 1.0, "por debajo de 1 cm el desvío no se ve…"],
  ["alcance", "desvío del PIVOTE…"]]
```

### `ninguno-par`

```json
["ninguno-par", "tareas.misma_persona_sobrecargada_el_mismo_dia",
  "tarea", "a", "b",
  ["y",
    ["==", ["campo", "a", "dueño"], ["campo", "b", "dueño"]],
    ["==", ["campo", "a", "vence"], ["campo", "b", "vence"]],
    ["!=", ["campo", "a", "id"], ["campo", "b", "id"]]],
  "dos tareas del mismo día para la misma persona compiten por las mismas horas",
  "ve coincidencia de fecha y dueño. NO ve cuánto dura cada tarea ni si el día alcanza igual"]
```

(Ejemplo ilustrativo, con la misma forma que `vault.nombre_unico_en_el_vault` del catálogo real de
Jam.) El patrón general de `ninguno-par`: **igualar el campo que define el conflicto** (`dueño` +
`vence`) **y exigir que difieran en la identidad** (`id`) — si no, cada tarea se empareja consigo
misma y el predicado da siempre verdadero.

### Las macros no son un embudo

Si tu caso no encaja en ninguna de las tres, la forma canónica sigue siendo 100% válida. El ejemplo de
`colocacion.interpenetracion` en §5.3 usa `unir` sobre DOS relaciones distintas (`pieza` y `vecina`) y
no tiene macro que lo cubra — se escribe canónico y listo.

---

## 5. Seis ejemplos reales, de menor a mayor complejidad

Todos están en producción hoy: los tres primeros en el propio catálogo de Oracle, los otros tres en el
catálogo de geometría de Jam (un consumidor real e independiente).

### 5.1 Contar lo que ofende (el patrón más común)

Ya lo viste en §2 (`proceso.test_con_mutante_que_lo_mata`). Receta: filtrás lo malo con `donde`,
contás con `resumen contar`, umbral `<= 0`.

### 5.2 Medir una magnitud con una función de dominio (`peor` + escalar)

```json
["peor", "snap.yaw",
  "pieza", "a",
  ["desvio_de_paso", ["campo", "a", "yaw"], 90.0],
  0.5,
  "medio grado en una pieza de 4 m da ~3 cm en la punta: el límite donde una junta se abre a la vista",
  "sólo el YAW contra su paso. NO ve pitch ni roll, ni si la pieza mira al lado correcto"]
```

`desvio_de_paso` no es parte del álgebra: es una **función escalar** (UDF) que el proyecto Jam
declaró — ver §6. El álgebra no sabe nada de grados ni de grillas; sólo sabe llamar funciones
declaradas y comparar sus resultados.

### 5.3 Comparar filas entre sí con `unir` (forma canónica, sin macro)

```json
["medida", "colocacion.interpenetracion",
  ["desde",
    ["unir", ["de", "pieza", "a"], ["de", "vecina", "b"]],
    ["donde", ["y",
      ["no", ["es_fondo", ["hecho", "b"]]],
      [">", ["penetracion", ["hecho", "a"], ["hecho", "b"]], 0]]]],
  ["resumen", "max", ["penetracion", ["hecho", "a"], ["hecho", "b"]]],
  ["umbral", "<=", 0,
    "`penetracion` ya descuenta la tolerancia de contacto: tocarse da 0 y clavarse da >0"],
  ["alcance",
    "solape de AABB entre piezas de escala comparable. NO ve la malla real, oclusión visual, ni si la pieza quedó flotando"]]
```

Por qué NO es una macro: `unir` combina DOS relaciones distintas (`pieza` y `vecina`), no la misma
consigo misma. `ninguno-par` no encaja, así que se escribe la forma canónica.

Fijate también `es_fondo`: sin ese filtro, cualquier pieza chica "interpenetraría" el fondo de
escenografía (un SkySphere gigante) y la medida daría rojo siempre — un caso real de por qué el
`alcance` y el filtro tienen que decir la verdad completa sobre qué se está comparando.

### 5.4 `unir` sin `donde`, resumiendo con `min`

```json
["medida", "snap.comparte_cara",
  ["desde", ["unir", ["de", "pieza", "a"], ["de", "objetivo", "b"]]],
  ["resumen", "min", ["solape_lateral_minimo", ["hecho", "a"], ["hecho", "b"]]],
  ["umbral", ">", 1.0,
    "el solape lateral debe superar la tolerancia de 1 cm: tocar una arista o estar en diagonal no cuenta"],
  ["alcance",
    "solape de AABB en los dos ejes laterales. NO ve cuánto de la cara real de la malla coincide"]]
```

No todos los `desde` tienen `donde`: acá no hace falta filtrar, sólo unir y resumir directo con `min`.
Fijate también el umbral `>` en vez de `<=` — el comparador lo elige la medida, no está fijo a `<= 0`.

### 5.5 `agrupar` en un caso real: que la traza de una simulación no tenga huecos

```json
["medida", "simulacion.la_traza_no_tiene_huecos",
  ["desde", ["de", "evento", "e"],
    ["agrupar",
      [["corrida", ["campo", "e", "corrida"]]],
      [["registrados", "contar", 1], ["ultimo", "max", ["campo", "e", "t"]]]],
    ["donde", ["!=", ["col", "registrados"], ["mas", ["col", "ultimo"], 1]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0,
    "una traza con huecos describe otra corrida que la que ocurrió"],
  ["alcance",
    "compara cuántos eventos hay contra el instante final, asumiendo que arranca en 0 y avanza de a 1. NO ve trazas con eventos simultáneos"]]
```

`mas` es una escalar del núcleo (`+1`) — así se expresa aritmética sobre un campo ordinal
(`t`), porque una relación es una bolsa sin orden: «consecutivo» se vuelve aritmética sobre el campo,
no una propiedad implícita del almacenamiento.

### 5.6 L2: una medida sobre medidas

```json
["ninguno", "meta.toda_medida_esta_fijada",
  "medida_en_uso", "m",
  ["y",
    ["==", ["campo", "m", "debe_tener_mutantes"], true],
    ["o",
      ["==", ["campo", "m", "mutantes"], 0],
      ["!=", ["campo", "m", "mutantes_vivos"], 0]]],
  "una medida propia con cero mutantes pasa vacuamente igual que una cuyos mutantes sobreviven",
  "exige al menos un mutante y ninguno vivo sólo cuando corresponde. NO exige nada de medidas heredadas ni evaluadas aparte"]
```

Ninguna sintaxis nueva: `medida_en_uso` es una relación como cualquier otra (la produce
`nucleo/marco.py` a partir del catálogo real), y esta medida la mide con el mismo `ninguno` de
siempre. Así es como el marco se verifica con sus propias herramientas.

---

## 6. Funciones escalares (UDF): cuando el álgebra no alcanza

El álgebra no sabe geometría, ni de grillas, ni de nada de un dominio particular — a propósito. Lo que
sí sabe hacer es llamar funciones **declaradas**, con nombre, aridad y unidad, para que aparezcan en
el inventario y se puedan discutir igual que un umbral.

```python
from oracle_metalenguaje import escalar

@escalar("volumen", "cm3")
def volumen(p: dict) -> float:
    return p["ex"] * p["ey"] * p["ez"]

@escalar("desvio_de_grilla", "cm")
def desvio_de_grilla(p: dict, grilla: float) -> float:
    """El peor desvío del PIVOTE respecto de la grilla, sobre los tres ejes."""
    return max(abs(v - round(v / grilla) * grilla) for v in (p["lx"], p["ly"], p["lz"]))

@escalar("penetracion", "cm")
def penetracion(a: dict, b: dict, tol: float = 1.0) -> float:
    """Profundidad efectiva en cm después de descontar la tolerancia de contacto."""
    solapes = []
    for (ca, ea), (cb, eb) in zip(_ejes(a), _ejes(b)):
        solape = (ea + eb) - abs(ca - cb)
        if solape <= tol:
            return 0.0
        solapes.append(solape)
    return min(solapes) - tol
```

(Estos tres son reales, del `escalares.py` del dominio de geometría de Jam.)

Reglas:

- El decorador **registra** la función — no basta con importarla. Así aparece en
  `python tools/medida.py --escalares`, y se puede contar cuántas escalares tiene un proyecto.
- El nombre usa minúsculas ASCII, dígitos y `_`, **sin puntos** (para no confundirse con un id de
  medida).
- Una escalar recibe hechos completos con `["hecho", alias]` (como `penetracion(a, b)` arriba) o
  campos sueltos con `["campo", alias, nombre]` (como `desvio_de_paso(valor, paso)`).
- Es **código Python con los mismos permisos que el proceso**. Por eso ninguna herramienta la ejecuta
  salvo que se pase explícitamente `--confiar-escalares`. Sin esa bandera, `--relaciones`,
  `--escalares` (sólo el inventario base) y `--nueva` siguen siendo seguros — nunca importan el
  archivo del proyecto.

---

## 7. El corpus: cómo se escribe un caso

**La primera regla del repositorio: el caso del corpus se escribe ANTES que la medida.** Dos motivos,
no es prolijidad:

1. una medida escrita primero se escribe *para pasar*, no para atrapar el defecto real;
2. la herramienta puede decirte si tu medida está bien **formada**, pero no puede saber qué quisiste
   decir. Una condición invertida —que selecciona lo que está BIEN en vez de lo que ofende— pasa todas
   las comprobaciones automáticas igual. El caso del corpus es lo único que la detecta.

Un caso es un archivo JSON con esta forma (ejemplo real, un `falso_verde`):

```json
{
  "id": "001-verde-acumulativo",
  "titulo": "«489 tests OK» reportado cada turno: un número que sube y nunca significa más",
  "etiqueta": "falso_verde",
  "sintoma": "El agente cerró cada entrega con un conteo de tests en verde. El conteo crece monótonamente y no distingue haber cubierto algo nuevo de haber agregado tests a lo ya cubierto.",
  "como_se_detecto": "persona",
  "medida": "proceso.afirmacion_declara_alcance",
  "evidencia": {
    "afirmacion": [
      {"id": "a1", "texto": "459 tests OK", "comando": "unittest discover", "alcance": ""},
      {"id": "a3", "texto": "489 tests OK", "comando": "unittest discover", "alcance": ""}
    ]
  },
  "leccion": "Una afirmación de verde sin alcance declarado no es verificable: es una cifra.",
  "fecha": "2026-07-29"
}
```

Y uno **`verde_correcto`** — la otra polaridad, igual de necesaria:

```json
{
  "id": "102-verificacion-vigente",
  "titulo": "Después de recorrer el motor, los commits siguientes fueron sólo de documentación",
  "etiqueta": "verde_correcto",
  "sintoma": "Se volvió a correr la verificación con motor y a partir de ahí sólo cambiaron documentos. La verificación seguía siendo válida, y era cierto.",
  "como_se_detecto": "observacion",
  "medida": "proceso.verificacion_vigente",
  "evidencia": {
    "verificacion": [{"que": "motor", "commit": "80373ea", "camino": "editor headless"}],
    "cambio": [{"archivo": "RELEVO.md", "commiteado": true, "es_codigo_vivo": false}]
  },
  "leccion": "La regla mira QUÉ cambió y no CUÁNTO: así los commits de documentación no invalidan una verificación."
}
```

### Las etiquetas

| `etiqueta` | Significa |
|---|---|
| `falso_verde` | algo estaba mal y la medición dijo bien |
| `falso_rojo` | algo estaba bien y la medición dijo mal (pesa igual de grave: enseña a ignorar el verificador) |
| `verde_correcto` | algo estaba bien y la medición dijo bien — **la otra polaridad**, sin ella `quitar_filtro` sobrevive siempre |
| `deuda_de_diseño` | un defecto del propio lenguaje, no de una medida de dominio |
| `medida_correcta_conclusion_errada` | la medida dio el veredicto correcto pero alguien sacó la conclusión causal equivocada de ella |

### ¿Por qué necesito la otra polaridad (`verde_correcto`)?

Es el error más común al empezar. Con `contar` y umbral `<= 0`, una medida sin la evidencia positiva
**siempre puede pasar vaciando la relación** — quitarle el filtro a una medida sólo se nota si hay
filas que NO ofenden y que deberían seguir dando verde. Sin `verde_correcto`, el corpus tiene "sólo
defectos" y varias mutaciones (sobre todo `quitar_filtro`) sobreviven siempre. Es lo mismo que evaluar
un clasificador únicamente con ejemplos positivos.

### Casos sin medida: `abierto`, `resuelto`, `limite_humano`

Un caso puede no tener una medida todavía (`"medida": null`). Entonces declara `estado_sin_medida`:

- **`abierto`** — es deuda real: el marco todavía no puede atrapar ese defecto. Es la lista de lo que
  falta, y ese número tiene que bajar.
- **`resuelto`** — el defecto se resolvió, pero no con una medida puntual sino cambiando el lenguaje
  (ver el ejemplo de `004-testigos-duplicados` más abajo: se resolvió eliminando la posibilidad misma
  de declarar testigos aparte).
- **`limite_humano`** — no es automatizable: requiere juicio (por ejemplo, una atribución causal). Se
  documenta para no perderlo, y no cuenta como deuda pendiente.

```json
{
  "id": "004-testigos-duplicados",
  "titulo": "La medición y sus testigos recorrían los datos dos veces, con dos definiciones",
  "etiqueta": "deuda_de_diseño",
  "medida": null,
  "estado_sin_medida": "resuelto",
  "resuelto": "2026-07-29, por construcción: los testigos son las filas que sobrevivieron a la única tubería de la medida; ya no existe una segunda función donde repetir la condición.",
  "leccion": "Si el lenguaje obliga a escribir dos veces la misma condición, el lenguaje está mal."
}
```

---

## 8. Un proyecto de punta a punta

Armemos un proyecto mínimo desde cero: **un gestor de tareas donde ninguna tarea vencida puede
quedar sin persona asignada.**

### 8.1 La carpeta

```
mi-proyecto/
  oracle.json
  escalares.py
  catalogos/
    tareas/
      tareas.vencida_sin_dueño.json
  corpus/
    tareas/
      001-vencida-sin-nadie.json
      002-vencida-con-dueño.json
```

### 8.2 `oracle.json`

```json
{
  "esquema": "oracle.proyecto/v1",
  "perfiles": []
}
```

(Sin `catalogo_base: true` no se cargan las medidas universales de `proceso`/`meta`/`simulacion` —
sólo tu catálogo. Las activás si además vas a medir TU PROCESO de construcción con un LLM.)

### 8.3 La escalar (opcional en este ejemplo, para mostrar el patrón)

```python
# escalares.py
from oracle_metalenguaje import escalar

@escalar("dias_de_atraso", "dias")
def dias_de_atraso(tarea: dict) -> int:
    return max(0, tarea["dias_vencida"])
```

### 8.4 La medida

Con la macro `ninguno` — el caso más común:

```json
["ninguno", "tareas.vencida_sin_dueño",
  "tarea", "t",
  ["y",
    ["==", ["campo", "t", "vencida"], true],
    ["==", ["campo", "t", "asignada"], false]],
  "una tarea vencida sin dueño no la va a hacer nadie: el atraso queda invisible hasta que alguien la busca a mano",
  "ve sólo el par vencida+sin-dueño. NO ve si la persona asignada realmente puede resolverla, ni cuán vencida está"]
```

Guardala en `catalogos/tareas/tareas.vencida_sin_dueño.json`. (En un proyecto real, generás el
esqueleto con `python <oracle>/tools/medida.py --nueva tareas.vencida_sin_dueño --proyecto
mi-proyecto` y editás los `RELACION`/`CAMPO`/textos en mayúsculas que deja puestos.)

### 8.5 El corpus — las dos polaridades

```json
// corpus/tareas/001-vencida-sin-nadie.json
{
  "id": "001-vencida-sin-nadie",
  "titulo": "Una tarea vencida hace tres días y sin asignar",
  "etiqueta": "falso_verde",
  "sintoma": "El tablero mostraba todo en orden porque nadie miraba las tareas sin dueño.",
  "como_se_detecto": "persona",
  "medida": "tareas.vencida_sin_dueño",
  "evidencia": {
    "tarea": [{"id": "t1", "vencida": true, "asignada": false, "dias_vencida": 3}]
  },
  "leccion": "Una tarea vencida sin dueño no aparece en ningún filtro habitual del tablero.",
  "fecha": "2026-07-31"
}
```

```json
// corpus/tareas/002-vencida-con-dueño.json
{
  "id": "002-vencida-con-dueño",
  "titulo": "Vencida pero con alguien encima — no debe dar rojo",
  "etiqueta": "verde_correcto",
  "sintoma": "Una tarea vencida CON dueño asignado no es el defecto que esta medida busca.",
  "como_se_detecto": "observacion",
  "medida": "tareas.vencida_sin_dueño",
  "evidencia": {
    "tarea": [{"id": "t2", "vencida": true, "asignada": true, "dias_vencida": 1}]
  },
  "leccion": "Sin este caso, quitarle el filtro `asignada` a la medida no lo notaría nadie.",
  "fecha": "2026-07-31"
}
```

### 8.6 Correr todo

```bash
cd mi-proyecto
python <ruta-a-oracle>/tools/medida.py --proyecto . --relaciones     # ¿qué hechos hay?
python <ruta-a-oracle>/tools/aceptacion.py --proyecto .              # ¿el corpus se pone rojo/verde como debe?
python <ruta-a-oracle>/tools/mutar.py --proyecto .                   # ¿el corpus ALCANZA para fijar la medida?
```

`aceptacion.py` tiene que confirmar: el caso `001` se pone ROJO con `tareas.vencida_sin_dueño`, y el
`002` se pone VERDE. Si `mutar.py` encuentra un mutante que sobrevive (por ejemplo, sacarle el `y` y
dejar sólo `vencida == true`), es que falta un tercer caso que discrimine esa mutación específica —
una tarea vencida CON dueño, que ya tenemos, o una NO vencida sin dueño, que faltaría agregar.

O, desde Python, como biblioteca:

```python
from oracle_metalenguaje import Motor

motor = Motor.desde_proyecto("mi-proyecto")
informe = motor.evaluar({"tarea": [{"id": "t1", "vencida": True, "asignada": False}]})
print(informe.ok)     # False
print(informe.texto())
```

---

## 9. Los comandos: cuál usar y cuándo

| Comando | Para qué |
|---|---|
| `tools/medida.py --relaciones` | ver qué hechos existen HOY (derivado de evidencia real, no una lista a mano) |
| `tools/medida.py --escalares` | ver las funciones de dominio, operadores y agregados disponibles |
| `tools/medida.py --nueva <id>` | crear el esqueleto de una medida nueva |
| `tools/medida.py <archivo.json>` | validar UNA medida y correrla contra el corpus |
| `tools/medida.py --expandir <archivo>` | ver a qué forma canónica expande una macro |
| `tools/corpus.py [--resumen]` | el corpus está bien formado y ningún caso se cae en silencio |
| `tools/aceptacion.py` | **el corpus juzga al oráculo**: todo defecto se pone rojo, todo `verde_correcto` se pone verde |
| `tools/diferencial.py --proyecto <p>` | comparar contra una implementación de referencia independiente |
| `tools/mutar.py` | ¿el corpus ALCANZA para fijar cada medida? (muta las medidas, no el código) |
| `tools/mutar_codigo.py --objetivo <archivo.py>` | lo mismo pero mutando el CÓDIGO del núcleo/perfiles |
| `tools/estudio.py` | vuelca todo el repo a un Markdown autocontenido para NotebookLM (así se generó el otro documento) |
| `python -m unittest discover -s tests -t . -q` | la suite de tests, sin dependencias externas |

Todos aceptan `--proyecto <ruta>` (o `$ORACLE_PROYECTO`) y, si el proyecto declara `escalares.py`,
exigen `--confiar-escalares` para ejecutarlo. Sin esa bandera, las inspecciones (`--help`,
`--relaciones`, `--nueva`, `--escalares` sin UDF externas) son siempre seguras.

---

## 10. Errores frecuentes al escribir tu primera medida

| Lo que ves | Qué significa | Cómo se arregla |
|---|---|---|
| `el umbral <= 0 no trae defensa` | falta el texto de `porque` en `umbral` | agregá por qué ese número y no otro |
| `hay que declarar qué NO ve` | falta `alcance`, o está vacío | escribí honestamente el punto ciego |
| `«>» sobre un valor ausente` | un `campo` mal escrito o que no existe en la evidencia | `--relaciones` para ver los campos reales |
| `«==» sobre un flotante…` | comparaste igualdad exacta de dos flotantes | usá `<=`/`>=` con una tolerancia |
| medida que nunca se pone roja | la condición del `donde` probablemente está invertida | escribí el caso del corpus primero; si no se pone rojo, la medida mide al revés |
| medida que nunca se pone verde | falta un caso `verde_correcto`, o el filtro es demasiado amplio | agregá evidencia donde la medida DEBE dar verde |
| `el id «x» está dos veces` | dos archivos del catálogo declaran el mismo id | cambiale el nombre a uno de los dos |
| `la relación «x» no existe en la evidencia` | tu tubería pide una relación que la evidencia no trae | una relación vacía se declara `[]` explícitamente, nunca se omite |

Lo que la herramienta **no puede decirte**: si la condición dice lo que quisiste decir. Una medida que
selecciona lo que está BIEN en vez de lo que ofende pasa todas las validaciones automáticas — está
bien formada, discrimina, y mide exactamente al revés de lo que pensabas. Por eso el caso del corpus
va primero: es lo único que lee la intención.

---

## 11. Glosario rápido

| Término | Definición corta |
|---|---|
| **hecho** | un registro de campos escalares (sin objetos anidados) |
| **relación** | una bolsa nombrada de hechos del mismo tipo — el equivalente a una tabla |
| **evidencia** | el mapa completo `relación → lista de hechos` que se le pasa a una medida |
| **medida** | un dato (JSON) que describe cómo medir algo: tubería + resumen + umbral + alcance |
| **testigos** | las filas que sobrevivieron al último `donde` — se muestran cuando la medida da rojo |
| **umbral** | el límite contra el que se compara el valor medido, con su defensa en texto |
| **alcance** | lo que la medida explícitamente NO mira — obligatorio, no puede estar vacío |
| **escalar (UDF)** | una función de dominio declarada con `@escalar`, para lo que el álgebra no sabe hacer sola |
| **macro** | azúcar sintáctica (`ninguno`, `ninguno-par`, `peor`) que expande a la forma canónica |
| **corpus** | la colección de casos reales (defectos y aciertos) que fija que las medidas midan lo que dicen medir |
| **dominio** | el conjunto de medidas + escenario + implementación de referencia que verifica un proyecto externo (geometría, vault, etc.) |
| **fixture diferencial** | evidencia versionada + veredicto de una implementación independiente, para comparar contra Oracle |
| **L0 / L1 / L2** | evidencia / medidas sobre evidencia / medidas sobre medidas — la misma representación en los tres niveles |

---

## Para seguir

- El estudio integral completo (filosofía, especificación formal, auditoría, historia de decisiones):
  `ORACLE-PARA-NOTEBOOKLM.md`.
- La guía de referencia oficial para escribir una medida: `ESCRIBIR-UNA-MEDIDA.md`.
- La especificación formal del álgebra, con las preguntas abiertas y cómo se cerraron:
  `ESPECIFICACION.md`.
- Un consumidor real en producción, para ver medidas de un dominio completo (geometría, colocación de
  piezas, snapping): el catálogo de Jam, en `~/Dev/jam/medidas/catalogos/`.
