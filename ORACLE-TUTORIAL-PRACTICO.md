# Oracle — tutorial práctico: cómo se programa con Oracle

Guía complementaria a `ORACLE-PARA-NOTEBOOKLM.md`. Ese documento es el estudio integral (filosofía,
especificación completa, auditoría, historia). **Este es distinto a propósito**: es un tutorial —
aprender haciendo, de lo más simple a lo más compuesto, con ejemplos reales tomados del propio
repositorio y de un proyecto que ya lo usa en producción (Jam, un plugin de Unreal Engine). Si
`ORACLE-PARA-NOTEBOOKLM.md` responde «¿por qué existe Oracle?», este documento responde «¿cómo
escribo la primera medida, y la segunda, y la que necesita algo más complicado?».

- Generado: `2026-08-24`
- Todos los ejemplos de sintaxis fueron verificados contra el código fuente vigente de
  `Segtem/oracle` (rama `main`) y contra medidas reales en producción del proyecto Jam.

---

## 0. Oracle en una frase

**La superficie es cómo se escribe; el JSON es cómo se guarda.**

Oracle es un **lenguaje de datos** (no una biblioteca de funciones) para escribir *medidas*: reglas
que toman hechos sobre lo que se construyó, calculan un número, lo comparan contra un umbral, y si el
umbral se viola, señalan exactamente qué filas lo violaron. Las medidas y los casos se escriben en
una superficie legible y se guardan como JSON —son datos, no código— y por eso se pueden
inspeccionar, mutar, contar y medir con las mismas herramientas que mide cualquier otra cosa.

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

Toda medida, en su forma completa (**canónica**), se escribe así en la superficie infija:

```oracle-gramatica
medida <id>:
    de <relacion> <alias>
    [unir <relacion2> <alias2>]
    [donde <predicado>]
    [agrupar:
        clave <nombre> = <expresion>
        agregado <nombre> = <agregado>(<expresion>)]
    resumen <agregado>(<expresion>)
    umbral <comparador> <valor> porque "<por qué ese número>"
    [requiere <relaciones>]
    alcance "<qué NO ve esta medida>"
```

| Pieza | Qué es | Obligatorio |
|---|---|---|
| `id` | `dominio.nombre`, minúsculas ASCII, dígitos y `_` | sí |
| `de …` | la fuente: de dónde salen los datos y qué alias reciben | sí |
| `unir …` | producto cartesiano con otra fuente | opcional |
| `donde …` | el filtro de lo que ofende — **acá se definen los testigos** | opcional |
| `agrupar:` | agrupa filas por claves y calcula agregados intermedios | opcional |
| `resumen` | cómo se colapsa la tubería a UN escalar — la medición en sí | sí |
| `umbral` | comparador + valor + **defensa en texto** (`porque`) de por qué ese valor | sí, con defensa no vacía |
| `requiere` | declara qué relaciones de evidencia son indispensables | opcional (obligatorio en medidas de ausencia) |
| `alcance` | qué NO mira esta medida, en texto | sí, no puede estar vacío |

Tres reglas no son estilo, son validación dura:
1. **Una medida sin defensa del umbral no carga, y una medida sin `alcance` no carga.** Fallan al leerse, no al usarse — antes de evaluar un solo hecho.
2. **Un umbral de igualdad (`==`) está prohibido.** La regla universal `meta.ningun_umbral_de_igualdad` exige umbrales de orden (`<=`, `>=`, `<`, `>`).
3. **Si una medida declara `requiere <relacion>`, la relación no puede faltar ni venir vacía.** Si no hay evidencia requerida, la evaluación devuelve `SIN EVIDENCIA` y no un verde espurio.

### El almacenamiento: por qué JSON

La superficie infija es la forma legible para escribir y revisar. En el disco (dentro de `catalogos/`), la medida se guarda como una lista JSON homoicónica que representa su AST directamente:

```json
["medida", "<id>",
  ["desde", ["de", "<relacion>", "<alias>"],
            ["donde", <predicado>]],
  ["resumen", "<agregado>", <expresion>],
  ["umbral", "<comparador>", <valor>, "<por qué ese número>"],
  ["requiere", "<relacion>"],
  ["alcance", "<qué NO ve esta medida>"]]
```

Para traducir entre la superficie infija y el archivo JSON tenés la herramienta `tools/sintaxis.py`:

```bash
python tools/sintaxis.py --imprimir catalogos/proceso/proceso.verificacion_vigente.json  # JSON -> superficie
oracle nueva dominio.regla        # crea el andamio ya en superficie infija
python tools/sintaxis.py --leer medida.oracle       # superficie -> JSON, si lo necesitás
```

El ejemplo más simple posible del propio catálogo de Oracle:

```oracle
medida proceso.test_con_mutante_que_lo_mata:
    de mutante m
    donde m.detecciones_conductuales == 0 y m.rechazos_del_algebra == 0
    resumen contar(1)
    umbral <= 0 segun contrato porque "un mutante que sobrevive es un test que no discrimina: pasa igual con el código roto"
    alcance "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los mutadores que nadie escribió"
```

Léelo en voz alta y ya sabés leer el 90% de las medidas que vas a encontrar: **«de la relación
`mutante`, alias `m`, quedate con los que sobrevivieron (`detecciones == 0` y `rechazos == 0`); contá cuántos quedaron; si son más
de 0, rojo — porque un mutante vivo es un test que no discrimina; y esto no ve los mutantes que nadie
llegó a escribir».**

Un detalle que sorprende la primera vez: **los testigos no se declaran aparte.** Los testigos —las
filas que se muestran cuando la medida da rojo, para que alguien pueda mirar el defecto— son
exactamente las filas que sobrevivieron al último `donde`. No hay una segunda función que las calcule,
porque escribir la misma condición dos veces es exactamente cómo se desincroniza (fue un defecto real
del proyecto — ver §7).

Tampoco hay composición de medidas (`DECISION-002`): una medida no puede invocar el resultado de otra medida. Cada medida juzga hechos directos del dominio.

---

## 3. El álgebra: cinco operadores, y nada más

Toda la sintaxis sale de combinar **cinco operadores**. Cada uno toma filas (o hace de fuente) y
devuelve filas: esa clausura es lo que permite encadenarlos sin casos especiales.

| Operador | Superficie | Qué hace |
|---|---|---|
| `de` | `de <relacion> <alias>` | fuente: trae una relación y la etiqueta con un alias |
| `donde` | `donde <predicado>` | filtra — **acá se definen los testigos** |
| `unir` | `unir <relacion> <alias>` | producto cartesiano con otra fuente |
| `agrupar` | `agrupar:\n    clave ...\n    agregado ...` | agrupa filas y las resume a una fila por grupo |
| `resumen` | `resumen <agregado>(<expresion>)` | colapsa TODA la tubería a un único escalar |

`resumen` no es un paso de la tubería: es lo último que se aplica para obtener el escalar de juicio.

### 3.1 `de` — la fuente

```oracle-fragmento
de pieza a
```

Trae todos los hechos de la relación `pieza` y los etiqueta con el alias `a`. A partir de acá, cada
fila de la tubería tiene acceso a los campos del hecho `a`.

### 3.2 `donde` — el filtro (y los testigos)

```oracle-fragmento
donde a.volumen > 0
```

Se queda sólo con las filas donde el predicado da `true`. **Es el único lugar donde se definen los
testigos**: lo que sobrevive acá es lo que se le muestra a un humano cuando la medida da rojo.

### 3.3 Acceso a los datos: siempre explícito

Tres accesores leen datos de una fila:

| Accesor | Superficie | En AST (JSON) | Devuelve |
|---|---|---|---|
| Campo | `a.volumen` | `["campo", "a", "volumen"]` | un campo de un hecho con alias `a` |
| Hecho | `hecho(a)` | `["hecho", "a"]` | el hecho ENTERO (para pasarlo a una escalar) |
| Columna | `col(reales)` o `reales` | `["col", "reales"]` | una columna o agregado derivado por `agrupar` |

`a.volumen` — "en la fila actual, tomá el hecho con alias `a` y devolvé su campo `volumen`". Comparar
contra un campo que no existe **es un error**, no da `false`: así un nombre de campo mal escrito no se
disfraza de verde silencioso.

### 3.4 Comparadores y lógicos

```
==  !=  <  <=  >  >=       y   o   no
```

Reglas del álgebra que sorprenden si vienen de Python:

- **`bool` no es número.** `true == 1` da error acá, aunque en Python valga. Sólo `suma` y `promedio`
  tratan un booleano como indicador 0/1, y de forma explícita.
- **Igualdad exacta sobre flotantes está PROHIBIDA**, tanto en una expresión como en el umbral final.
  `x == 3.0` no carga. La razón: `0.1 + 0.2 != 0.3` en punto flotante, y una medida que compare
  así puede decir verde sin que nadie se entere. Usá una comparación de orden con tolerancia:
  `distancia(hecho(a), hecho(b)) <= 0.5`.
- **Los dos lados de una comparación tienen que ser del mismo tipo.** Comparar un número contra texto
  es error de álgebra, no `false`.
- `y` / `o` se encadenan de forma infija: `a.x == 1 y a.y == 2 y a.z == 3`.

### 3.5 `resumen` y los agregados

```oracle-fragmento
resumen contar(1)
resumen max(a.volumen)
```

Cinco agregados: `contar`, `max`, `min`, `suma`, `promedio`. `contar` es especial: **no evalúa la
expresión**, sólo cuenta filas — por eso la convención es escribir `resumen contar(1)` (el `1`
es un relleno que nunca se mira). Sobre cero filas, cualquier agregado da `0`. `suma` y `promedio`
aceptan números o booleanos (0/1); `min` y `max` exigen valores del mismo tipo y comparables.

### 3.6 `unir` — comparar filas entre sí

```oracle-fragmento
de documento a
unir documento b
donde a.nombre == b.nombre y a.carpeta != b.carpeta
```

`unir` hace el producto cartesiano: cada fila resultante tiene AMBOS alias (`a` y `b`) disponibles.
Es así como se comparan hechos entre sí — piezas que se tocan, documentos homónimos, las dos puntas de
un relevo. Acá: «dos documentos con el mismo nombre en carpetas distintas» — el defecto real que motiva
`vault.nombre_unico_en_el_vault` (un wikilink resuelve por nombre, y dos homónimos lo dejan ambiguo).

Un `unir` sobre la misma relación cuenta cada par dos veces (`(a,b)` y `(b,a)`) y también empareja cada
fila consigo misma (`a == b`); normalmente hay que filtrar eso en el `donde` (por ejemplo exigiendo
`a.carpeta != b.carpeta` o `a.id != b.id`).

### 3.7 `agrupar` — cómo se expresa la AUSENCIA sin usar `null`

Este es el operador que más cuesta la primera vez, porque resuelve algo que en SQL pide un
`LEFT JOIN` con nulos — y acá **no hay nulos**. La pregunta es «¿qué módulos no tienen NINGÚN
importador real?» — una ausencia, no una presencia.

```oracle-fragmento
de modulo m
unir importa i
agrupar:
    clave modulo = m.nombre
    agregado reales = suma(i.b == m.nombre y i.es_test == false)
donde reales == 0
```

El truco: se agrupa sobre el PRODUCTO sin filtrar primero, y se agrega con `suma` sobre un predicado
booleano. Como un booleano suma 0 o 1, un módulo sin ningún importador real da `reales = 0` — y el
grupo **sigue existiendo**, porque nunca se filtró antes de agrupar. Sin necesitar un concepto de nulo.

Forma general:

```oracle-gramatica
agrupar:
    clave <nombre_clave> = <expresion>
    agregado <nombre_agregado> = <agregado>(<expresion>)
```

Después de `agrupar`, las filas ya NO tienen los alias originales (`m`, `i` desaparecen: se
consumieron en el resumen). Las claves y agregados derivados se leen directamente por su nombre o con
`col(nombre)`.

---

## 4. Las macros: la forma corta

**La mayoría de las medidas del catálogo de Oracle están escritas con una macro.** Una macro es azúcar
sintáctica que se expande a la forma canónica ANTES de construir la medida — el evaluador, la
mutación y el inventario nunca se enteran de que hubo una macro. `oracle expandir <archivo>` te muestra
la expansión.

| Macro | Superficie | Para qué |
|---|---|---|
| `ninguno` | `ninguno <id>:\n    relacion <rel>\n    alias <alias>\n    predicado <pred>\n    porque "..."\n    alcance "..."` | ninguna fila debe cumplir el predicado — el 80% de los casos |
| `ninguno-par` | `ninguno-par <id>:\n    relacion <rel>\n    aliasA <a1>\n    aliasB <a2>\n    predicado <pred>\n    porque "..."\n    alcance "..."` | lo mismo, sobre PARES de la misma relación |
| `peor` | `peor <id>:\n    relacion <rel>\n    alias <alias>\n    expresion <expr>\n    tolerancia <tol>\n    porque "..."\n    alcance "..."` | el peor caso de una magnitud no puede pasar de una tolerancia |

### `ninguno` — el caso común

```oracle
ninguno proceso.test_con_mutante_que_lo_mata:
    relacion mutante
    alias m
    predicado m.detecciones_conductuales == 0 y m.rechazos_del_algebra == 0
    porque "un mutante que sobrevive es un test que no discrimina"
    alcance "cuenta mutantes DECLARADOS. NO ve los que nadie escribió"
```

Expande EXACTO a la forma canónica de §2. `ninguno` cubre todo lo que se reduce a «filtrás lo que
ofende, contás, cero es el único número aceptable».

### `peor` — cuando el número importa, no la cuenta

```oracle
peor snap.grilla:
    relacion pieza
    alias a
    expresion desvio_de_grilla(hecho(a), 100.0)
    tolerancia 1.0
    porque "por debajo de 1 cm el desvío no se ve y no produce juntas visibles en una pieza de 4 m"
    alcance "desvío del PIVOTE respecto de la grilla. NO ve si el pivote está donde debería dentro de la malla"
```

Ejemplo real, en producción, del catálogo de geometría de Jam. Fijate el problema que resuelve
`peor`: escrita a mano, la tolerancia (`1.0`) aparecería DOS veces — una en el `donde` que filtra
(«¿superó 1 cm?») y otra en el `umbral` («¿el peor caso está por debajo de 1 cm?») — y nada garantiza
que sigan sincronizadas si alguien cambia una y no la otra. Ese fue un defecto real del proyecto (caso
`012` del corpus). `peor` recibe la tolerancia **una sola vez** y genera las dos apariciones desde ahí.

Expande a:

```oracle
medida snap.grilla:
    de pieza a
    donde desvio_de_grilla(hecho(a), 100.0) > 1.0
    resumen max(desvio_de_grilla(hecho(a), 100.0))
    umbral <= 1.0 porque "por debajo de 1 cm el desvío no se ve y no produce juntas visibles en una pieza de 4 m"
    alcance "desvío del PIVOTE respecto de la grilla. NO ve si el pivote está donde debería dentro de la malla"
```

### `ninguno-par`

```oracle
ninguno-par tareas.misma_persona_sobrecargada_el_mismo_dia:
    relacion tarea
    aliasA a
    aliasB b
    predicado a.dueno == b.dueno y a.vence == b.vence y a.id != b.id
    porque "dos tareas del mismo día para la misma persona compiten por las mismas horas"
    alcance "ve coincidencia de fecha y dueño. NO ve cuánto dura cada tarea ni si el día alcanza igual"
```

(Ejemplo ilustrativo, con la misma forma que `vault.nombre_unico_en_el_vault` del catálogo real de
Jam.) El patrón general de `ninguno-par`: **igualar el campo que define el conflicto** (`dueno` +
`vence`) **y exigir que difieran en la identidad** (`id`) — si no, cada tarea se empareja consigo
misma y el predicado da siempre verdadero.

### Las macros no son un embudo

Si tu caso no encaja en ninguna macro, la forma canónica sigue siendo 100% válida. El ejemplo de
`colocacion.interpenetracion` en §5.3 usa `unir` sobre DOS relaciones distintas (`pieza` y `vecina`) y
no tiene macro que lo cubra — se escribe canónico y listo.

---

## 5. Seis ejemplos reales, de menor a mayor complejidad

Todos están en producción hoy: los tres primeros en el propio catálogo de Oracle, los otros tres en el
catálogo de geometría de Jam (un consumidor real e independiente).

### 5.1 Contar lo que ofende (el patrón más común)

Ya lo viste en §2 (`proceso.test_con_mutante_que_lo_mata`). Receta: filtrás lo malo con `donde`,
contás con `resumen contar(1)`, umbral `<= 0`.

### 5.2 Medir una magnitud con una función de dominio (`peor` + escalar)

```oracle
peor snap.yaw:
    relacion pieza
    alias a
    expresion desvio_de_paso(a.yaw, 90.0)
    tolerancia 0.5
    porque "medio grado en una pieza de 4 m da ~3 cm en la punta: el límite donde una junta se abre a la vista"
    alcance "sólo el YAW contra su paso. NO ve pitch ni roll, ni si la pieza mira al lado correcto"
```

`desvio_de_paso` no es parte del álgebra: es una **función escalar** (UDF) que el proyecto Jam
declaró — ver §6. El álgebra no sabe nada de grados ni de grillas; sólo sabe llamar funciones
declaradas y comparar sus resultados.

### 5.3 Comparar filas entre sí con `unir` (forma canónica, sin macro)

```oracle
medida colocacion.interpenetracion:
    de pieza a
    unir vecina b
    donde no es_fondo(hecho(b)) y penetracion(hecho(a), hecho(b)) > 0
    resumen max(penetracion(hecho(a), hecho(b)))
    umbral <= 0 segun contrato porque "`penetracion` ya descuenta la tolerancia de contacto: tocarse da 0 y clavarse da >0"
    alcance "solape de AABB entre piezas de escala comparable. NO ve la malla real, oclusión visual, ni si la pieza quedó flotando"
```

Por qué NO es una macro: `unir` combina DOS relaciones distintas (`pieza` y `vecina`), no la misma
consigo misma. `ninguno-par` no encaja, así que se escribe la forma canónica.

Fijate también `es_fondo`: sin ese filtro, cualquier pieza chica "interpenetraría" el fondo de
escenografía (un SkySphere gigante) y la medida daría rojo siempre — un caso real de por qué el
`alcance` y el filtro tienen que decir la verdad completa sobre qué se está comparando.

### 5.4 `unir` sin `donde`, resumiendo con `min`

```oracle
medida snap.comparte_cara:
    de pieza a
    unir objetivo b
    resumen min(solape_lateral_minimo(hecho(a), hecho(b)))
    umbral > 1.0 segun convencion porque "el solape lateral debe superar la tolerancia de 1 cm: tocar una arista o estar en diagonal no cuenta"
    alcance "solape de AABB en los dos ejes laterales. NO ve cuánto de la cara real de la malla coincide"
```

No todos los `desde` tienen `donde`: acá no hace falta filtrar, sólo unir y resumir directo con `min`.
Fijate también el umbral `>` en vez de `<=` — el comparador lo elige la medida, no está fijo a `<= 0`.

### 5.5 `agrupar` en un caso real: que la traza de una simulación no tenga huecos

```oracle
medida simulacion.la_traza_no_tiene_huecos:
    de evento e
    agrupar:
        clave corrida = e.corrida
        agregado registrados = contar(1)
        agregado ultimo = max(e.t)
    donde registrados != mas(ultimo, 1)
    resumen contar(1)
    umbral <= 0 segun convencion porque "una traza con huecos describe otra corrida que la que ocurrió: si faltan pasos, cualquier cosa que se mida sobre ella habla de lo que se registró y no de lo que pasó"
    requiere evento
    alcance "compara cuántos eventos hay contra el instante final, asumiendo que el tiempo arranca en cero y avanza de a uno. NO ve trazas donde varios eventos comparten instante, ni sabe si el que falta es importante. Si evento viene vacío la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—."
```

`mas` es una escalar del núcleo (`+1`) — así se expresa aritmética sobre un campo ordinal
(`t`), porque una relación es una bolsa sin orden: «consecutivo» se vuelve aritmética sobre el campo,
no una propiedad implícita del almacenamiento.

### 5.6 L2: una medida sobre medidas

```oracle
ninguno meta.toda_medida_esta_fijada:
    relacion medida_en_uso
    alias m
    predicado m.debe_tener_mutantes == true y (m.mutantes == 0 o m.mutantes_vivos != 0)
    porque "una medida propia con cero mutantes pasa vacuamente igual que una cuyos mutantes sobreviven: en ambos casos el catálogo la contiene pero la mutación no demuestra que esté fijada"
    alcance "exige al menos un mutante y ninguno vivo sólo cuando `debe_tener_mutantes` es verdadero. NO vuelve a exigirlos a medidas heredadas —responde su corpus de origen— ni a las evaluadas aparte, y NO ve los mutadores que nadie escribió. Si medida_en_uso viene vacía no hay medidas sin fijar y verde es correcto; además contiene una fila por medida cargada por construcción"
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

@escalar("volumen", "cm3", unidades_argumentos=("sin_unidad",))
def volumen(p: dict) -> float:
    return p["ex"] * p["ey"] * p["ez"]

@escalar("desvio_de_grilla", "cm", unidades_argumentos=("sin_unidad", "cm"))
def desvio_de_grilla(p: dict, grilla: float) -> float:
    """El peor desvío del PIVOTE respecto de la grilla, sobre los tres ejes."""
    return max(abs(v - round(v / grilla) * grilla) for v in (p["lx"], p["ly"], p["lz"]))

@escalar("penetracion", "cm", unidades_argumentos=("sin_unidad", "sin_unidad", "cm"))
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
  `oracle escalares`, y se puede contar cuántas escalares tiene un proyecto.
- El nombre usa minúsculas ASCII, dígitos y `_`, **sin puntos** (para no confundirse con un id de
  medida).
- En la superficie infija, una escalar recibe hechos completos con `hecho(alias)` (como `penetracion(hecho(a), hecho(b))` arriba) o
  campos sueltos con `alias.nombre` (como `desvio_de_paso(a.yaw, 90.0)`).
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

Toda la regla de las medidas aplica acá: **la superficie (`.caso`) es cómo se escribe; el JSON es
cómo se guarda** — y el corpus carga ambos formatos por igual, sin paso de traducción.

Un caso en superficie tiene esta forma (ejemplo real, un `falso_verde`):

```caso
caso 001-verde-acumulativo:
    fecha: "2026-07-29"
    origen:
        repo: "Brianholl/jam"
        commit: "todos"
    procedencia: observada
    titulo: "«489 tests OK» reportado cada turno: un número que sube y nunca significa más"
    etiqueta: falso_verde
    sintoma:
        El agente cerró cada entrega con un conteo de tests en verde. El conteo crece monótonamente y no distingue haber cubierto algo nuevo de haber agregado tests a lo ya cubierto. Se lee como «está bien» y sólo dice «no se rompió lo de antes».
    como_se_detecto: persona
    medida: proceso.afirmacion_declara_alcance
    evidencia:
        afirmacion: id, texto, comando, alcance
            "a1", "459 tests OK", "unittest discover", ""
            "a2", "477 tests OK", "unittest discover", ""
            "a3", "489 tests OK", "unittest discover", ""
    leccion:
        Una afirmación de verde sin alcance declarado no es una afirmación verificable: es una cifra. El alcance es lo que la vuelve discutible.
```

Y uno **`verde_correcto`** — la otra polaridad, igual de necesaria:

```caso
caso 102-verificacion-vigente:
    fecha: "2026-07-29"
    origen:
        repo: "Brianholl/jam"
        commit: "sesión 2026-07-29"
    procedencia: observada
    titulo: "Después de recorrer el motor, los commits siguientes fueron sólo de documentación"
    etiqueta: verde_correcto
    sintoma:
        Se volvió a correr la verificación con motor y a partir de ahí sólo cambiaron documentos. `relevo.py` declaró la verificación vigente, y era cierto.
    como_se_detecto: observacion
    medida: proceso.verificacion_vigente
    evidencia:
        verificacion: que, commit, camino
            "motor", "80373ea", "editor headless"
        cambio: archivo, commiteado, es_codigo_vivo
            "RELEVO.md", true, false
            "Vault-kb/README.md", true, false
    leccion:
        La regla mira QUÉ cambió y no CUÁNTO: por eso los commits de documentación no invalidan una verificación, y eso es lo que la hace usable en vez de molesta.
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

Un caso puede no tener una medida todavía (`"medida": null` o `medida: null`). Entonces declara `estado_sin_medida`:

- **`abierto`** — es deuda real: el marco todavía no puede atrapar ese defecto. Es la lista de lo que
  falta, y ese número tiene que bajar.
- **`resuelto`** — el defecto se resolvió, pero no con una medida puntual sino cambiando el lenguaje
  (ver el ejemplo de `004-testigos-duplicados` más abajo: se resolvió eliminando la posibilidad misma
  de declarar testigos aparte).
- **`limite_humano`** — no es automatizable: requiere juicio (por ejemplo, una atribución causal). Se
  documenta para no perderlo, y no cuenta como deuda pendiente.

```caso
caso 004-testigos-duplicados:
    fecha: "2026-07-29"
    origen:
        repo: "Brianholl/jam"
        commit: "535d476"
    procedencia: observada
    titulo: "La medición y sus testigos recorrían los datos dos veces, con dos definiciones"
    etiqueta: deuda_de_diseño
    sintoma:
        `INTERPENETRACION` declaraba `mide=penetracion_maxima` y `testigos=piezas_clavadas`: dos funciones que recorren lo mismo con la misma condición escrita dos veces. Nada garantiza que no se separen.
    como_se_detecto: persona
    medida: null
    estado_sin_medida: resuelto
    resuelto:
        2026-07-29, por construcción: los testigos son las filas que sobrevivieron a la única tubería de la medida; ya no existe una segunda función donde repetir la condición.
    evidencia:
        declaracion: medida, mide, testigos, condicion_repetida
            "colocacion.interpenetracion", "penetracion_maxima", "piezas_clavadas", true
    leccion:
        Si el lenguaje obliga a escribir dos veces la misma condición, el lenguaje está mal. Los testigos no son un cálculo aparte: son el filtro.
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
      tareas.vencida_sin_dueno.oracle
  corpus/
    tareas/
      001-vencida-sin-nadie.caso
      002-vencida-con-dueno.caso
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

@escalar("dias_de_atraso", "dias", unidades_argumentos=("sin_unidad",))
def dias_de_atraso(tarea: dict) -> int:
    return max(0, tarea["dias_vencida"])
```

### 8.4 La medida

La escribís en la superficie infija (con la macro `ninguno` — el caso más común):

```oracle
ninguno tareas.vencida_sin_dueno:
    relacion tarea
    alias t
    predicado t.vencida == true y t.asignada == false
    porque "una tarea vencida sin dueño no la va a hacer nadie: el atraso queda invisible hasta que alguien la busca a mano"
    alcance "ve sólo el par vencida+sin-dueño. NO ve si la persona asignada realmente puede resolverla, ni cuán vencida está"
```

Y la guardás tal cual: el catálogo carga `.oracle` igual que `.json`, así que no hay paso de
traducción.

```bash
mv tareas.vencida_sin_dueno.oracle catalogos/tareas/
```

### 8.5 El corpus — las dos polaridades

```caso
caso 001-vencida-sin-nadie:
    fecha: "2026-07-31"
    origen:
        repo: "mi-proyecto"
        commit: "ejemplo"
    procedencia: construida
    titulo: "Una tarea vencida hace tres días y sin asignar"
    etiqueta: falso_verde
    sintoma:
        El tablero mostraba todo en orden porque nadie miraba las tareas sin dueño.
    como_se_detecto: persona
    medida: tareas.vencida_sin_dueno
    evidencia:
        tarea: id, vencida, asignada, dias_vencida
            "t1", true, false, 3
    leccion:
        Una tarea vencida sin dueño no aparece en ningún filtro habitual del tablero.
```

```caso
caso 002-vencida-con-dueno:
    fecha: "2026-07-31"
    origen:
        repo: "mi-proyecto"
        commit: "ejemplo"
    procedencia: construida
    titulo: "Vencida pero con alguien encima — no debe dar rojo"
    etiqueta: verde_correcto
    sintoma:
        Una tarea vencida CON dueño asignado no es el defecto que esta medida busca.
    como_se_detecto: observacion
    medida: tareas.vencida_sin_dueno
    evidencia:
        tarea: id, vencida, asignada, dias_vencida
            "t2", true, true, 1
    leccion:
        Sin este caso, quitarle el filtro `asignada` a la medida no lo notaría nadie.
```

*(El id del caso y del archivo usan `dueno` en ASCII: los identificadores son nombres de archivo y
por diseño rechazan caracteres no ASCII para evitar divergencias entre normalizaciones NFC/NFD).*

### 8.6 El contexto del proyecto y correr todo

Antes de verificar, podés ver todo lo que tu proyecto expone con un solo comando:

```bash
cd mi-proyecto
oracle contexto           # relaciones, campos, escalares, operadores y medidas disponibles
oracle contexto --compacto # la misma información en ~1.600 tokens (ideal para editores y LLMs)
oracle test               # secuencia completa: corpus, sintaxis, aceptación y mutación
```

**Por qué `oracle contexto` complementa este tutorial en vez de acortarlo:** este tutorial enseña a
pensar una medida —los tres niveles, la clausura del álgebra, las macros, el rol de los testigos y
las polaridades del corpus—. `oracle contexto` no explica nada de eso: da la fotografía viva y
concreta del proyecto en el que estás trabajando. En vez de alternar entre `oracle relaciones`,
`oracle escalares` y listados de catálogo, tenés el inventario activo en una sola salida.

`oracle test` tiene que confirmar: el caso `001` se pone ROJO con `tareas.vencida_sin_dueno`, y el
`002` se pone VERDE. Si la mutación encuentra un mutante que sobrevive (por ejemplo, sacarle el `y` y
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
| `oracle init [ruta]` | inicializa un proyecto con `catalogos/`, `corpus/`, `diferencial/` y `oracle.json` |
| `oracle caso nuevo <grupo/id>` | crea el andamio de un caso nuevo, ya en superficie (`.caso`) |
| `oracle caso listar` | lista los casos del corpus, su etiqueta y qué medida reclaman |
| `oracle caso generar <medida>` | fabrica evidencia discriminante para fijar mutaciones a partir de sobrevivientes |
| `oracle nueva <dominio.nombre>` | crea el andamio de una medida, ya en superficie infija (`.oracle`) |
| `oracle revisar <archivo>` | valida una medida suelta contra la evidencia |
| `oracle medida probar <arch> --con <filas>` | corre una medida contra filas escritas a mano (`--vigilar` para re-probar al guardar) |
| `oracle expandir <archivo>` | muestra la forma canónica a la que expande una macro |
| `oracle contexto [--compacto]` | reúne relaciones, campos, escalares, operadores y medidas de TU proyecto (~1.600 tokens con `--compacto`) |
| `oracle test [--rapido\|--todo]` | secuencia completa: corpus, sintaxis, aceptación, diferencial y mutación |
| `oracle relaciones` | ver qué hechos y campos existen HOY (derivados de evidencia real) |
| `oracle escalares` | ver las funciones de dominio, operadores y agregados disponibles |
| `oracle manual [tema]` | la referencia del lenguaje armada de sus fuentes (`--html` para el sitio, `--man` para páginas de manual; tema `medidas` para las 54 universales y sus alcances) |
| `oracle biblioteca instaladas` | qué bibliotecas de políticas hay instaladas y cuáles usa este proyecto |
| `oracle biblioteca verificar <ruta>` | certifica una biblioteca antes de confiar en ella |
| `oracle biblioteca listar <ruta>` | muestra umbrales, orígenes (`segun`) y alcances de una biblioteca |
| `oracle diagnostico` | qué versión de Oracle corre y desde dónde, sin publicar nada del dominio |
| `tools/sintaxis.py --verificar` | comprueba ida y vuelta entre JSON y superficie en todo el catálogo, macros, corpus y bloques de documentación |
| `python -m unittest discover -s tests -t . -q` | la suite de tests, sin dependencias externas |

Todos aceptan `--proyecto <ruta>` (o `$ORACLE_PROYECTO`) y, si el proyecto declara `escalares.py`,
exigen `--confiar-escalares` para ejecutarlo. Sin esa bandera, las inspecciones (`--help`,
`--relaciones`, `--nueva`, `--escalares` sin UDF externas, `contexto`) son siempre seguras.

### Heredar un catálogo sin quedar en rojo el primer día

Cuando un proyecto adopta un catálogo que no escribió —el catálogo base de Oracle, o una biblioteca
de políticas— suele salir rojo en cosas reales que nadie va a arreglar hoy. Apagar la medida sería
volver al verde que no significa nada, así que hay una tercera opción: **la sombra**. Se declara en
`oracle.json` y la medida se evalúa, se informa con la marca `[EN SOMBRA]`, y **no tumba la
corrida**:

```json
{
  "sombra": {
    "meta.toda_medida_filtra_o_agrupa": {
      "desde": "2026-09-01",
      "porque": "tres medidas heredadas sin filtro; se arreglan de a una"
    }
  }
}
```

Los dos campos son obligatorios y hay medidas que los vigilan: una sombra sin fecha no se puede
envejecer, una sin motivo no se puede discutir, y una sobre una medida que ya da verde no tiene
nada que perdonar. La sombra además **envejece**:

- `meta.ninguna_sombra_envejece_sin_revisarse`: si la sombra supera los **90 días**, la medida se
  pone roja.
- `meta.toda_sombra_declara_una_fecha_real`: si la fecha no se puede parsear o está en el futuro,
  falla.
- `meta.ninguna_sombra_ya_en_verde`: prohíbe mantener en sombra medidas que ya dan verde.
- `meta.ninguna_sombra_sobre_una_medida_que_no_existe`: prohíbe sombras huérfanas.

**Ninguna de esas medidas se puede poner en sombra a sí misma**, que es lo que impide que la
sombra se coma su propio control.

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
| **superficie infija** | la forma humana y legible en que se escriben las medidas (`.oracle`) y los casos (`.caso`) |
| **hecho** | un registro de campos escalares (sin objetos anidados) |
| **relación** | una bolsa nombrada de hechos del mismo tipo — el equivalente a una tabla |
| **evidencia** | el mapa completo `relación → lista de hechos` que se le pasa a una medida |
| **medida** | un dato que describe cómo medir algo: tubería + resumen + umbral + alcance |
| **testigos** | las filas que sobrevivieron al último `donde` — se muestran cuando la medida da rojo |
| **umbral** | el límite contra el que se compara el valor medido, con su defensa en texto (`porque`) |
| **requiere** | declaración explícita de relaciones necesarias para no emitir veredictos vacíos |
| **alcance** | lo que la medida explícitamente NO mira — obligatorio, no puede estar vacío |
| **escalar (UDF)** | una función de dominio declarada con `@escalar`, para lo que el álgebra no sabe hacer sola |
| **macro** | azúcar sintáctica (`ninguno`, `ninguno-requiere`, `ninguno-par`, `peor`) que expande a la forma canónica |
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
- Dos consumidores reales en producción consumiendo desde PyPI: el catálogo de Jam (plugin de Unreal
  Engine: geometría, colocación de piezas, snapping) en `~/Dev/jam/medidas/catalogos/` y el de
  LyraGASP (juego en Unreal Engine: deformers, recarga, assets) en `~/Dev/games/unreal/LyraGASP/medidas/catalogos/`.
- Las lecciones de migración desde subtree al paquete de PyPI: `docs/migracion/de-subtree-a-pypi.md`.
