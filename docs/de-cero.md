# Tu primer juego con un LLM, y cómo saber si está bien

Esta guía es para alguien que recién empieza a programar y programa con un modelo de lenguaje: le
pedís el código, lo probás y seguís. Vamos a hacer una batalla naval que corre en el navegador y, sobre
todo, vamos a responder una pregunta que el juego solo no puede contestar: **¿cumple las reglas?**

No hace falta saber programar. Hace falta paciencia para leer lo que el modelo te devuelve y ganas de
preguntar «¿cómo sé que esto está bien?».

> **Estado de esta guía.** El recorrido y las explicaciones están escritos. Las salidas de terminal
> marcadas como *pendiente* se completan con corridas reales cuando el ejemplo `ejemplo/batalla-naval/`
> quede verde en el repositorio (tarea `de-cero-naval`). Ninguna salida de esta guía se escribe a mano.

## Lo que vas a construir

Un juego de batalla naval en un tablero de 10 por 10. Cada jugador tiene cinco barcos: un portaaviones
de 5 casillas, un acorazado de 4, un crucero de 3, un submarino de 3 y un destructor de 2. En total, 17
casillas por flota. Se dispara por turnos y gana quien hunde toda la flota del otro.

Y al lado del juego, un **catálogo de reglas** escritas en Oracle que miran cada partida y dicen si se
respetaron, con la prueba en la mano cuando no.

## HTML, CSS y JavaScript, lo justo

Un juego en el navegador son tres archivos que se reparten el trabajo:

| Archivo | Qué hace | En la batalla naval |
|---|---|---|
| `index.html` | la estructura: qué hay en la pantalla | los dos tableros, los botones, el panel de la partida |
| `css/…` | el aspecto: colores, tamaños, posiciones | el agua, los barcos, las explosiones |
| `js/…` | el comportamiento: qué pasa cuando hacés algo | colocar barcos, disparar, decidir quién gana |

Para esta guía no hace falta leer el CSS. Del JavaScript nos importa un archivo: el que **cuenta lo
que pasó** en la partida. Lo vemos más abajo.

## Pedirle el juego a un modelo

Un pedido que funciona bien es concreto sobre las reglas y sobre la forma:

```text
Haceme una batalla naval en HTML5, CSS y JavaScript, sin librerías.
Tablero de 10x10. Flota: portaaviones 5, acorazado 4, crucero 3, submarino 3, destructor 2.
Contra la computadora, por turnos alternados. Gana quien hunde las 17 casillas del otro.
Separá el código en index.html, css/estilos.css y js/ (motor, interfaz).
```

Cuando te devuelva el código, abrí `index.html` en el navegador y jugá una partida. Si anda, **todavía
no sabés si está bien**. Sabés que anda. Son cosas distintas, y el resto de la guía es sobre esa
diferencia.

## El problema: un juego que anda no es un juego correcto

Mirá estas preguntas. Ninguna se contesta jugando una vez:

- ¿Puede quedar un barco con una casilla fuera del tablero?
- ¿Pueden dos barcos del mismo jugador ocupar la misma casilla?
- ¿Alternan de verdad los turnos, o a veces tira dos veces el mismo?
- Cuando el juego dice «¡impacto!», ¿había un barco en esa casilla?
- ¿El ganador hundió las 17 casillas, o el juego terminó antes?

Si le pedís al mismo modelo que escriba el juego y también los tests, los tests van a confirmar lo que
el modelo ya creía. Por eso las reglas van **aparte**, en un lenguaje hecho para eso, y miran lo que el
juego hizo, no lo que el juego cree que hizo.

> Esto pasó de verdad. Un agente construyó una batalla naval «con Oracle» y `oracle test` dio verde.
> El catálogo estaba vacío: el verde validaba la sintaxis de un archivo, no el juego. Está contado en
> [Por qué Oracle](por-que.html). Desde entonces, un proyecto sin medidas sale *sin medición*, no verde.

## Que el juego cuente lo que pasó

La idea central: **el juego no se juzga a sí mismo, cuenta lo que pasó.** Mientras se juega, un archivo
anota cada hecho en filas planas, sin opinar. En el ejemplo ese archivo es `js/trace.js`, y anota tres
cosas:

| Relación | Una fila por… | Campos |
|---|---|---|
| `celda_barco` | cada casilla ocupada por un barco | `id`, `jugador`, `barco_id`, `segmento_idx`, `fila`, `columna` |
| `tiro` | cada disparo | `turno`, `tirador`, `receptor`, `fila`, `columna`, `es_impacto`, `hundio_barco`, `barco_hundido` |
| `partida` | el final de la partida | `estado`, `ganador`, `perdedor`, `turno_final`, `total_tiros`, `impactos_ganador`, `impactos_perdedor` |

Al terminar, el juego descarga esas filas como un archivo JSON. Así se ve el primer tiro de una partida real (`partida_real.json` del ejemplo):

```json
{
  "tiro": [
    {"turno": 0, "tirador": "jugador", "receptor": "cpu", "fila": 2, "columna": 3, "es_impacto": false, "hundio_barco": false, "barco_hundido": "ninguno"}
  ]
}
```

Si trabajás con un modelo, **pedile esto explícitamente**: «agregá un registro que anote cada casilla
de barco, cada tiro y el resultado final, y que lo descargue como JSON». Es lo que después vas a
juzgar.

## Instalar Oracle y crear el proyecto

Oracle se instala con `uv` (o `pip` dentro de un entorno virtual). Necesita Python 3.11 o posterior.

```bash
uv tool install oracle-metalenguaje
oracle init reglas-naval
cd reglas-naval
oracle test
```

Un proyecto recién creado sale **sin medición**: todavía no hay ninguna regla, y Oracle no lo disfraza
de verde.

## La primera regla: ningún barco fuera del tablero

Las reglas de Oracle se llaman **medidas**. Esta es la primera, tal como está en el ejemplo:

```oracle
ninguno naval.barcos_dentro_del_tablero:
    de celda_barco c
    donde c.fila < 0 o c.fila > 9 o c.columna < 0 o c.columna > 9
    umbral <= 0 segun contrato porque "todas las celdas ocupadas por barcos deben ubicarse dentro de la cuadrícula de 10x10"
    ambito universal
    alcance "revisa los límites de cada celda de barco reportada. No verifica solapamientos ni continuidad."
```

Línea por línea:

- `ninguno` dice qué clase de regla es: **no tiene que haber ninguna** fila que ofenda.
- `de celda_barco c` elige las filas a mirar: las casillas de barco, y a cada una la llama `c`.
- `donde …` dice cuáles ofenden: las que tienen una fila o columna fuera de 0 a 9.
- `umbral <= 0` es cuántas se toleran: cero. `segun contrato` dice de dónde sale ese cero: de las
  reglas del juego, no de una intuición. `porque` lo defiende en palabras.
- `ambito universal` dice que la regla vale para cualquier partida.
- `alcance` dice **lo que la regla no mira**. Es obligatorio. Un verde que no dice qué dejó sin mirar
  se lee como «está todo bien», y eso es justo lo que queremos evitar.

## Probar la regla antes de confiar en ella

Una regla nueva puede estar mal escrita y dar verde siempre. Por eso, **antes** de usarla, se prueba
con dos ejemplos que vos armás: uno donde tiene que ponerse **roja** (un barco en la fila 10) y otro
donde tiene que quedar **verde** (todos dentro). Esos ejemplos se llaman **casos** y viven en el
**corpus**.

*Salida pendiente: el caso rojo y el caso verde del ejemplo, y lo que dice `oracle test` sobre ellos.*

## Por qué dos casos no alcanzan: la mutación

Oracle no se conforma con que tus casos pasen. Debilita cada regla a propósito: afloja el umbral de 0
a 1, invierte una comparación, le quita el filtro. A cada versión debilitada la llama **mutante**. Si
algún caso nota la diferencia, el mutante muere. Si ninguno la nota, esa parte de la regla no la está
cuidando nadie.

Esto no es teoría. El juego del ejemplo llegó con **11 reglas y 2 casos**. Medido el 2026-09-25, su
`oracle test` salió **rojo por mutación**: la mayoría de los mutantes sobrevivían, porque dos casos no
alcanzan para fijar once reglas. Un verde con dos casos habría sido otra vez el verde que no mide nada.

La cuenta es simple: cada regla necesita al menos un caso que la ponga roja cerca del borde y uno
verde, para que aflojarla o dejarla sin filtro se note.

*Salida pendiente: el `oracle test` del ejemplo con sus casos completos, en verde.*

## Más reglas, cada una con su idea

Con la primera entendida, el resto son variaciones. Cada una enseña una pieza del lenguaje.

**Turnos que alternan.** Compara cada tiro con el siguiente. Se lee como lo pensarías:

```oracle
medida naval.alternancia_turnos:
    de tiro t1
    unir tiro t2
    donde t2.turno == t1.turno + 1 y t1.tirador == t2.tirador
    resumen contar(1)
    umbral <= 0 segun contrato porque "los turnos deben alternar estrictamente entre ambos jugadores en turnos consecutivos"
    ambito universal
    alcance "compara el tirador del turno k con el tirador del turno k+1. No valida la ausencia de saltos si falta un turno completo."
```

`unir` junta cada tiro con cada otro tiro, y el `donde` se queda con los pares donde el mismo jugador
tiró en dos turnos seguidos. `t1.turno + 1` se escribe así, como en cualquier lenguaje.

**Barcos que no se pisan.** Mismo recurso, sobre las casillas de barco: dos casillas distintas del mismo
jugador en la misma coordenada son una ofensa. Está en `naval.barcos_sin_solapamiento`.

**La flota completa.** `naval.flota_reglamentaria` usa `agrupar` para contar las casillas de cada
jugador y exige exactamente 17. Además dice `requiere celda_barco`: si el juego no mandó ninguna
casilla, la regla no sale verde, sale **sin evidencia**. Cero barcos no es una flota correcta, es un
registro roto.

**Un impacto que era verdad.** `naval.veracidad_impacto_positivo` usa `sin`: busca los tiros marcados
como impacto **sin** ninguna casilla de barco del rival en ese lugar.

```oracle
medida naval.veracidad_impacto_positivo:
    de tiro t
    sin celda_barco c donde c.jugador == t.receptor y c.fila == t.fila y c.columna == t.columna
    donde t.es_impacto == true
    resumen contar(1)
    umbral <= 0 segun contrato porque "un disparo no puede declararse impacto si en esa casilla no había un segmento de barco rival"
    ambito universal
    alcance "detecta disparos registrados como impacto que no corresponden a ninguna celda ocupada por la flota del receptor. No verifica si el barco ya estaba completamente hundido."
```

El ejemplo completo tiene once reglas: límites, solapamiento, flota, tiros dentro del tablero, tiros
sin repetir, turnos que alternan, turnos sin huecos, impactos verdaderos (a favor y en contra), ganador
legítimo y que nadie dispare después del final.

## Juzgar una partida de verdad

Las reglas ya están probadas. Ahora se juzga una partida real: jugás, el juego descarga el JSON y se lo
pasás a Oracle.

```bash
oracle juzgar --con hechos_partida.json
```

*Salida pendiente: `oracle juzgar` sobre `partida_real.json` del ejemplo.*

Dos cosas del resultado son las que más importan:

- **`SIN MIRAR`** junta los `alcance` de las reglas que se aplicaron: lo que el verde no garantiza.
- **`NO SE APLICARON`** lista las reglas cuya relación no vino en el archivo. Si el juego se olvidó de
  anotar los tiros, las reglas de tiros no te dan un verde de regalo: aparecen acá.

Si una regla sale roja, el veredicto trae **testigos**: las filas exactas que ofendieron. Con eso le
volvés a hablar al modelo: «el tiro del turno 14 se marcó como impacto y no había barco en esa
casilla; corregilo».

## Qué le falta a este juego

El juego del ejemplo anda y sus reglas miran lo principal, pero no todo. Lo que ninguna de sus reglas
mira hoy, y serían buenas siguientes reglas:

- que cada barco sea una línea recta y continua (hoy se cuentan casillas, no la forma);
- que un barco hundido tenga todas sus casillas impactadas;
- que la computadora no sepa dónde están tus barcos antes de dispararles.

Cada una empieza igual: ¿qué hecho necesita que el juego anote?, ¿qué fila ofendería?, ¿qué caso rojo
y qué caso verde la fijan?

## Si trabajás con un modelo, cinco consejos

1. **Pedile que el juego cuente lo que pasa**, en filas planas. Sin eso no hay nada que juzgar.
2. **No le pidas las reglas y el código en la misma pasada.** Escribí o revisá vos las reglas.
3. **Probá cada regla con un caso rojo y uno verde** antes de creerle.
4. **Leé el `alcance`** de cada regla: es lo que el verde no te promete.
5. **Cuando algo sale rojo, pasale al modelo los testigos**, no una descripción vaga.

Después de esto, [La primera medida real](13-primer-valor.html) muestra el mismo recorrido con menos
explicación, y [Escribir una medida](03-escribir-una-medida.html) es la referencia del lenguaje.
