# Cómo funciona Oracle

Esta página cuenta qué hace Oracle, en qué orden y qué contesta en cada caso. No hay ninguna salida
inventada: un test del repositorio arma el proyecto de esta página desde una carpeta vacía, corre
cada comando y compara lo que sale con lo que ves acá. Si Oracle cambia y la página no, el test se
pone rojo.

El proyecto es chico a propósito: una sola regla de la batalla naval —**ningún barco fuera del
tablero de 10×10**— para mirar de cerca cada pieza. La guía [Tu primer juego con un
LLM](de-cero.md) arma el juego completo; esta página explica la máquina.

```bash paso
oracle --version
```

```text salida
oracle 0.31.1
  álgebra:  1.0   (qué SIGNIFICA una medida)
  sintaxis: 0.8   (cómo se ESCRIBE)
  corriendo desde: …/oracle
```

Tres versiones, y son tres cosas distintas. El **álgebra** versiona lo que una medida significa: si
sube la mayor, una medida que ya tenías puede dar otro resultado. La **sintaxis** versiona cómo se
escribe un `.oracle` o un `.caso`. La **distribución** es el paquete que instalás, y cambia también
cuando se arregla una herramienta sin tocar el lenguaje.

## Las tres piezas

Todo en Oracle es uno de estos tres archivos:

| pieza | archivo | qué es |
|---|---|---|
| **evidencia** | un `.json` | lo que pasó, en filas planas. La escribe un **sensor** de tu proyecto, no Oracle |
| **medida** | un `.oracle` en `catalogos/` | una regla: qué filas cuentan como infracción y cuántas se toleran |
| **caso** | un `.caso` en `corpus/` | una evidencia guardada y lo que la medida **tiene** que decir sobre ella |

Y dos verbos:

- `oracle juzgar --con hechos.json` cruza tus medidas con una evidencia nueva y da un veredicto.
- `oracle test` cruza tus medidas con los casos guardados, y además **ataca a las medidas** para ver
  si los casos las sostienen.

Oracle no corre tu juego, no abre la red y no llama a ningún modelo. Juzga lo que el sensor le
entrega, y cada veredicto dice qué no miró.

## El proyecto

```bash paso
oracle init .
```

```text salida
Proyecto Oracle inicializado en .:
  · catalogos/
  · corpus/
  · diferencial/
  · relaciones/
  · oracle.json

Próximos pasos:
  1. Creá un caso:     oracle caso <grupo/id>
  2. Creá una medida:  oracle nueva <dominio.nombre>
  3. Verificá todo:    oracle test
```

`init` crea `catalogos/`, `corpus/`, `diferencial/`, `relaciones/` y `oracle.json`. Para esta página
apagamos el catálogo base: así lo único que se mide son nuestras reglas y cada salida es corta. En
un proyecto real conviene dejarlo prendido, porque trae las **políticas** que vigilan tu catálogo
(que toda medida declare qué no ve, de dónde sale cada umbral, etc.).

```json archivo=oracle.json incluir=ejemplo/como-funciona/oracle.json
```

## Una medida, línea por línea

```oracle archivo=catalogos/flota/flota.casillas_dentro_del_tablero.oracle incluir=ejemplo/como-funciona/catalogos/flota/flota.casillas_dentro_del_tablero.oracle
```

| línea | qué dice | qué pasa si falta |
|---|---|---|
| `ninguno-requiere flota.casillas_dentro_del_tablero:` | la **forma** de la regla y su id. `ninguno` = «no tiene que haber ninguna infracción»; `-requiere` = «y tiene que haber algo que mirar» | el id es obligatorio: `dominio.nombre`, en ASCII |
| `de casilla c` | de qué **relación** de la evidencia salen las filas, y con qué alias se nombran | sin fuente no hay medida |
| `donde …` | qué fila cuenta como **infracción**. Tiene que dar `true` o `false`: un número o un texto es error | sin filtro, toda casilla sería una infracción |
| `umbral <= 0 segun contrato porque "…"` | cuántas infracciones se toleran, **de dónde salió ese número** (`contrato`, `medicion`, `convencion` o `tanteo`) y por qué | es obligatorio: una regla sin umbral no decide nada |
| `requiere casilla` | la relación que **tiene** que traer filas. Si viene vacía, el veredicto es SIN EVIDENCIA | con `ninguno` a secas, cero filas son cero infracciones: verde |
| `ambito universal` | dónde obliga la regla: `universal` (siempre) o `del_origen` (sólo en el proyecto que la escribió) | se asume `sin_declarar` |
| `alcance "…"` | qué **no** ve la medida. Oracle lo repite al final de cada verde | es obligatorio: un verde sin alcance promete de más |

Una macro como `ninguno-requiere` es sólo una forma corta. Oracle la expande a la forma canónica, que
es un dato JSON: así se guarda, se compara y se muta.

<details>
<summary>Ver la forma canónica de esta medida</summary>

```bash paso
oracle medida expandir catalogos/flota/flota.casillas_dentro_del_tablero.oracle
```

```text salida
[
 "medida",
 "flota.casillas_dentro_del_tablero",
 [
  "desde",
  [
   "de",
   "casilla",
   "c"
  ],
  [
   "donde",
   [
    "o",
    [
     "<",
     [
      "campo",
      "c",
      "fila"
     ],
     0
    ],
    [
     ">",
     [
      "campo",
      "c",
      "fila"
     ],
     9
    ],
    [
     "<",
     [
      "campo",
      "c",
      "columna"
     ],
     0
    ],
    [
     ">",
     [
      "campo",
      "c",
      "columna"
     ],
     9
    ]
   ]
  ]
 ],
 [
  "resumen",
  "contar",
  1
 ],
 [
  "umbral",
  "<=",
  0,
  "el tablero es de 10x10: filas y columnas van de 0 a 9",
  "contrato"
 ],
 [
  "requiere",
  "casilla"
 ],
 [
  "ambito",
  "universal"
 ],
 [
  "alcance",
  "mira cada casilla ocupada que el juego anotó. NO ve si los barcos se tocan ni si la flota está completa"
 ]
]
```

`ninguno` se vuelve una **tubería** (`desde`: de dónde salen las filas y cómo se filtran), un
**resumen** (`contar` las filas que quedaron) y un **umbral** (`<= 0`). Toda medida tiene esa forma.

</details>

## Qué pasa cuando juzgás

`oracle juzgar` hace siempre lo mismo, en este orden:

1. **Carga el catálogo.** Cada medida se valida al leerla: vocabularios cerrados, `alcance`
   obligatorio, macros completas. Una medida mal escrita no se evalúa a medias: la corrida no empieza.
2. **Lee la evidencia.** Un objeto JSON: cada clave es una relación y su valor, una lista de filas.
3. **Valida la evidencia entera, antes de medir nada.** Un `null` se rechaza, y las claves de
   unicidad se comprueban en **todas** las relaciones, también en las que ninguna medida usa.
4. **Mide cada regla.** Si una relación de `requiere` viene vacía, esa medida sale SIN EVIDENCIA y no
   se mide. Si no, corre la tubería: las filas que sobreviven son los **testigos**, el resumen las
   cuenta y el umbral decide.
5. **Aplica las sombras.** Una medida en sombra se mide igual, pero su rojo no hace fallar la corrida
   mientras no supere su cota. Un SIN EVIDENCIA no se perdona nunca.
6. **Da el veredicto y un código de salida**: `0` si todo pasó; `1` si hubo un rojo, un SIN EVIDENCIA
   o una medida propia que no se pudo aplicar; `2` si no se pudo juzgar (evidencia inválida, error
   del álgebra, uso incorrecto).

Veámoslo con cinco evidencias.

```json archivo=evidencia/en-regla.json incluir=ejemplo/como-funciona/evidencia/en-regla.json
```

```json archivo=evidencia/fuera.json incluir=ejemplo/como-funciona/evidencia/fuera.json
```

```json archivo=evidencia/vacia.json incluir=ejemplo/como-funciona/evidencia/vacia.json
```

```json archivo=evidencia/con-null.json incluir=ejemplo/como-funciona/evidencia/con-null.json
```

```json archivo=evidencia/repetida.json incluir=ejemplo/como-funciona/evidencia/repetida.json
```

### Verde: y lo que no miró

```bash paso
oracle juzgar --con evidencia/en-regla.json
```

```text salida
✓ flota.casillas_dentro_del_tablero                   0 (<= 0)

VEREDICTO: verde en 1 medidas. SIN MIRAR:
  · flota.casillas_dentro_del_tablero: mira cada casilla ocupada que el juego anotó. NO ve si los barcos se tocan ni si la flota está completa
```

`0 (<= 0)`: cero infracciones contra un umbral de cero. Un verde **nunca** termina ahí: siempre
enumera lo que no se miró, que es el `alcance` de cada medida.

### Rojo: con el testigo exacto

```bash paso falla
oracle juzgar --con evidencia/fuera.json
```

```text salida
✗ flota.casillas_dentro_del_tablero                   1 (<= 0)
      → c={'barco': 'b1', 'fila': 10, 'columna': 4}

VEREDICTO: 1 de 1 medidas en rojo
```

El **testigo** es la fila que hizo fallar la regla, tal como vino en la evidencia. La casilla de la
fila 9 no aparece: está dentro del tablero. Con el testigo sabés qué corregir sin adivinar.

### Sin evidencia: no es verde ni rojo

```bash paso falla
oracle juzgar --con evidencia/vacia.json
```

```text salida
⊘ flota.casillas_dentro_del_tablero            SIN EVIDENCIA («casilla» vacía; no se midió)

VEREDICTO: 1 de 1 sin evidencia (no se midieron)
```

La partida no anotó ninguna casilla. Eso no prueba que los barcos estén bien: prueba que el sensor
no miró. Oracle no lo cuenta como verde, y tampoco como un rojo del juego: lo nombra aparte, y
la corrida falla igual.

<p class="pregunta">**Pensalo.** ¿Y si la regla no tuviera `requiere`?</p>

<details>
<summary>Probalo</summary>

La misma regla con `ninguno` a secas:

```oracle archivo=catalogos/flota/flota.casillas_dentro_sin_requiere.oracle incluir=ejemplo/como-funciona/floja/flota.casillas_dentro_sin_requiere.oracle
```

```bash paso falla
oracle juzgar --con evidencia/vacia.json
```

```text salida
⊘ flota.casillas_dentro_del_tablero            SIN EVIDENCIA («casilla» vacía; no se midió)
✓ flota.casillas_dentro_sin_requiere                  0 (<= 0)

VEREDICTO: 1 de 2 sin evidencia (no se midieron)
```

Sobre la misma evidencia vacía, la versión sin `requiere` dice **verde**: cero filas, cero
infracciones. Es la trampa más común de un catálogo, y por eso existe `-requiere`: **si la relación
es el universo que se evalúa, usá la variante `-requiere`**. Más abajo, `oracle test` va a atrapar
esta medida floja por su cuenta.

</details>

### Evidencia inválida: no se juzga

```bash paso falla
oracle juzgar --con evidencia/con-null.json
```

```text salida
ERROR AL EVALUAR — «flota.casillas_dentro_del_tablero»: la relación «casilla» trae null explícito en la fila 0, campo «fila»
ERROR AL EVALUAR — «flota.casillas_dentro_sin_requiere»: la relación «casilla» trae null explícito en la fila 0, campo «fila»
```

Un `null` no dice si la casilla estaba bien o mal: cada comparación lo interpretaría a su manera.
Oracle lo rechaza antes de medir. Si tu sensor no pudo decidir un dato, que lo diga con un campo
aparte (`fila_decidible: false`), no con un hueco.

Una relación puede declarar su **clave de unicidad** poniendo `["clave", [campos…]]` como primera
fila. Oracle la comprueba en toda la evidencia antes de medir:

```bash paso falla
oracle juzgar --con evidencia/repetida.json
```

```text salida
ERROR AL EVALUAR — «flota.casillas_dentro_del_tablero»: la relación «casilla» declara la clave (barco, fila, columna) y la fila 1 la repite: ya la traía la fila 0 — {'barco': 'b1', 'fila': 3, 'columna': 4}
ERROR AL EVALUAR — «flota.casillas_dentro_sin_requiere»: la relación «casilla» declara la clave (barco, fila, columna) y la fila 1 la repite: ya la traía la fila 0 — {'barco': 'b1', 'fila': 3, 'columna': 4}
```

Sin la cabecera, dos filas iguales son dos hechos: Oracle no deduplica, porque no puede inventar una
identidad que tu dominio no declaró.

## Qué comprueba `oracle test`

`juzgar` mira una partida. `test` mira **tus reglas**: ¿se ponen rojas cuando deben y verdes cuando
deben? ¿Y se nota si alguien las rompe?

```bash paso falla
oracle test --rapido
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 0 casos · esquema, evidencia L0 y trazabilidad en regla

MEDIDAS SIN CASOS ✗ — 2 medida(s) propias sin ejercitar:
  · flota.casillas_dentro_del_tablero: escribí un caso rojo y uno verde que ejerzan esta medida
  · flota.casillas_dentro_sin_requiere: escribí un caso rojo y uno verde que ejerzan esta medida

SINTAXIS OK · 2 medidas · 0 macros · 0 casos · 0 relaciones

ACEPTACIÓN ✗ — sin casos en el corpus: un catálogo con medidas no puede verificarse sin casos

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

MUTACIÓN: salteada por --rapido

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
OMISIONES: mutación de medidas (--rapido)
VEREDICTO: ROJO (falló: medidas sin casos, aceptación)
```

Dos medidas y ningún caso: nada respalda a esas reglas. Un caso es una evidencia guardada con su
**etiqueta**, que dice qué tiene que contestar la medida:

| etiqueta | la medida tiene que dar |
|---|---|
| `falso_verde` | rojo: la evidencia trae un defecto que la regla no puede dejar pasar |
| `verde_correcto` | verde: todo en regla, y la regla lo reconoce |

Para esta regla hacen falta seis: un rojo por cada una de las cuatro condiciones del `donde`, un
verde en los cuatro bordes y una partida sin casillas. Y uno más, contra la medida floja.

<details>
<summary>Ver los siete casos</summary>

```oracle archivo=corpus/flota/001-fila-desbordada.caso incluir=ejemplo/como-funciona/corpus/flota/001-fila-desbordada.caso
```

```oracle archivo=corpus/flota/002-fila-negativa.caso incluir=ejemplo/como-funciona/corpus/flota/002-fila-negativa.caso
```

```oracle archivo=corpus/flota/003-columna-desbordada.caso incluir=ejemplo/como-funciona/corpus/flota/003-columna-desbordada.caso
```

```oracle archivo=corpus/flota/004-columna-negativa.caso incluir=ejemplo/como-funciona/corpus/flota/004-columna-negativa.caso
```

```oracle archivo=corpus/flota/005-las-cuatro-esquinas.caso incluir=ejemplo/como-funciona/corpus/flota/005-las-cuatro-esquinas.caso
```

```oracle archivo=corpus/flota/006-partida-sin-casillas.caso incluir=ejemplo/como-funciona/corpus/flota/006-partida-sin-casillas.caso
```

```oracle archivo=corpus/flota/007-sin-requiere-sin-casillas.caso incluir=ejemplo/como-funciona/floja/007-sin-requiere-sin-casillas.caso
```

</details>

```bash paso falla
oracle test --rapido
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 7 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 2 medidas · 0 macros · 7 casos · 0 relaciones

catálogo: 2 medidas · corpus: 7 casos

  ROJO  001-fila-desbordada                    flota.casillas_dentro_del_tablero  (valor 1)
  ROJO  002-fila-negativa                      flota.casillas_dentro_del_tablero  (valor 1)
  ROJO  003-columna-desbordada                 flota.casillas_dentro_del_tablero  (valor 1)
  ROJO  004-columna-negativa                   flota.casillas_dentro_del_tablero  (valor 1)
  verde 005-las-cuatro-esquinas                flota.casillas_dentro_del_tablero  (valor 0)
  SIN EVIDENCIA 006-partida-sin-casillas      flota.casillas_dentro_del_tablero  («casilla» vacía)
  FALLA 007-sin-requiere-sin-casillas          flota.casillas_dentro_sin_requiere  (valor 0; salió verde, se esperaba ROJO medido)

defectos que se pusieron rojos: 4 · verdes correctos: 1 · sin evidencia esperada: 1 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✗ — 1 problema(s)
  · 007-sin-requiere-sin-casillas: se esperaba ROJO medido con flota.casillas_dentro_sin_requiere

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

MUTACIÓN: salteada por --rapido

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
OMISIONES: mutación de medidas (--rapido)
VEREDICTO: ROJO (falló: aceptación)
```

El caso 007 dice que una partida sin casillas es un defecto, y la medida sin `requiere` la deja pasar
en verde. `oracle test` no la perdona: la nombra, dice qué esperaba y se pone rojo. La salida es
borrar la medida floja, porque la otra ya dice lo mismo, y bien:

```bash paso
rm -f catalogos/flota/flota.casillas_dentro_sin_requiere.oracle
rm -f corpus/flota/007-sin-requiere-sin-casillas.caso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 6 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 6 casos · 0 relaciones

catálogo: 1 medidas · corpus: 6 casos

  ROJO  001-fila-desbordada                    flota.casillas_dentro_del_tablero  (valor 1)
  ROJO  002-fila-negativa                      flota.casillas_dentro_del_tablero  (valor 1)
  ROJO  003-columna-desbordada                 flota.casillas_dentro_del_tablero  (valor 1)
  ROJO  004-columna-negativa                   flota.casillas_dentro_del_tablero  (valor 1)
  verde 005-las-cuatro-esquinas                flota.casillas_dentro_del_tablero  (valor 0)
  SIN EVIDENCIA 006-partida-sin-casillas      flota.casillas_dentro_del_tablero  («casilla» vacía)

defectos que se pusieron rojos: 4 · verdes correctos: 1 · sin evidencia esperada: 1 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 4 defectos en rojo, 1 sin evidencia esperada, 1 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 20 · murieron 20 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 20 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 120

sin políticas meta activas — se informa sólo el resultado operativo

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: VERDE (todas las verificaciones aplicables en regla)
```

### Las capas, en orden

`oracle test` corre estas capas una detrás de otra. Con `--rapido` saltea la mutación; con `--todo`
agrega la mutación de código, que sólo existe dentro del propio Oracle.

| capa | qué comprueba | se pone roja si… |
|---|---|---|
| **estructura** | que existan `catalogos/`, `corpus/` y `diferencial/` | falta alguna |
| **andamio** | los casos que creó `oracle nueva` | alguno sigue sin evidencia real |
| **catálogo** | que cada medida se pueda leer | una medida está mal escrita |
| **corpus** | el esquema de cada caso y su evidencia | un caso está mal formado |
| **medidas sin casos** | que cada medida propia tenga al menos un caso, también con `--rapido` | una medida no tiene ninguno |
| **sintaxis** | que cada medida y cada caso se impriman y se vuelvan a leer iguales | la ida y vuelta cambia algo |
| **aceptación** | que cada caso salga como pide su etiqueta; y, con el catálogo base, las políticas que vigilan tu catálogo | un caso sale al revés |
| **diferencial** | los fixtures de `diferencial/`: veredictos guardados contra una implementación independiente | un veredicto cambió |
| **mutación de medidas** | ataca cada medida con cada mutador (afloja el umbral, quita un filtro, invierte una comparación…) y exige que algún caso lo note | sobrevive un mutante |

El veredicto final es uno de tres: **VERDE**, **ROJO** (y qué capas fallaron) o **SIN MEDICIÓN**
(no hay medidas ni casos: no hay nada que decir, y no es verde). Un VERDE con capas salteadas lo
dice en el mismo renglón: `VERDE (se salteó: mutación de medidas (--rapido))`.

### Por qué la mutación

Un caso rojo no alcanza. El mutador `alejar_limite_de_defecto` cambia `c.fila < 0` por
`c.fila < -1`: la regla sigue pareciendo razonable, pero ya no ve la fila -1. De los siete casos,
**sólo el 002** lo nota, porque es el único con una casilla en la fila -1; sin él, ese mutante
sobreviviría y `oracle test` se pondría rojo. La mutación prueba que tus casos **sostienen** cada
parte de tu regla, no sólo que la ejercitan. Lo cuenta en detalle [Por qué la mutación](05-por-que-la-mutacion.md).

## Lo que Oracle no hace

- **No corre tu producto.** Juzga lo que el sensor exportó. Un verde dice que la regla se cumple
  sobre esos hechos, dentro de su `alcance`; no dice que el juego esté bien en todo lo demás.
- **No llama a la red ni a ningún modelo.** El núcleo es determinista: la misma evidencia da el
  mismo veredicto.
- **No confía en tu código sin permiso.** Si tu proyecto trae funciones propias en `escalares.py`,
  Oracle las ejecuta sólo con `--confiar-escalares`, y en un proceso aislado que no puede leer ni
  escribir fuera del proyecto, abrir la red ni lanzar procesos.
- **No compone medidas.** Una medida termina en un número y un umbral. Ninguna puede leer el
  veredicto de otra: las preguntas sobre el catálogo se contestan midiendo el catálogo, en el nivel
  meta.

La referencia completa del lenguaje está en la [especificación](../ESPECIFICACION.md) y en el
[manual](manual.html), que se genera de las mismas declaraciones que usa Oracle.
