# Tu primer juego con un LLM, y cómo saber si está bien

Esta guía es para alguien que recién empieza a programar y programa con un modelo de lenguaje. Vas a
armar, **copiando y pegando**, una batalla naval que corre en el navegador. Y vas a aprender a contestar
la pregunta que el juego solo no puede contestar: **¿cumple las reglas?**

Cada paso tiene la misma forma: una **pregunta** para que la pienses vos, la **respuesta** plegada
(abrila cuando quieras), el **bloque para copiar**, y **lo que tenés que ver**. Si ves otra cosa, el paso
te dice qué hacer.

> Un test del repositorio arma el juego pegando los bloques de esta guía en orden, desde una carpeta
> vacía, y corre `oracle test` después de cada paso. Las salidas que ves acá salen de esa corrida: si un
> bloque cambia, el test lo nota.

## Paso 1 · Preparar la carpeta

Oracle se instala una sola vez. Necesitás Python 3.11 o posterior y `uv`.

```bash paso
uv tool install oracle-metalenguaje
oracle init batalla-naval
cd batalla-naval
oracle test
```

```text salida
Proyecto Oracle inicializado en batalla-naval:
  · catalogos/
  · corpus/
  · diferencial/
  · relaciones/
  · oracle.json

Próximos pasos:
  1. Creá un caso:     oracle caso <grupo/id>
  2. Creá una medida:  oracle nueva <dominio.nombre>
  3. Verificá todo:    oracle test
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS: sin casos guardados para verificar
SINTAXIS: salteado (sin medidas ni casos todavía)
ACEPTACIÓN: salteado (sin medidas ni casos todavía)
DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)
MUTACIÓN: salteada (sin medidas todavía)

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

PRODUCTO: sin nueva medición; no se ejecutó el producto.
VEREDICTO: SIN MEDICIÓN (advertencia: proyecto vacío: 0 medidas propias, 0 casos, 0 fixtures diferenciales)
```

**Si ves otra cosa.** Si dice `oracle: command not found`, cerrá y abrí la terminal: `uv` agrega
`oracle` al `PATH` pero la terminal abierta no se entera.

<details>
<summary>¿Por qué dice «sin medición» y no «verde»?</summary>

Porque todavía no hay ninguna regla. Un verde sin reglas diría «está todo bien» sin haber mirado nada.
Oracle prefiere decir lo que pasó: no midió.

</details>

Una cosa más antes de seguir. `oracle init` deja activado el **catálogo base**: las reglas de Oracle
sobre tus reglas. Son exigentes (piden unidades declaradas y evidencia observada de partidas reales) y
las vamos a encender al final. Por ahora, apagalo:

```json archivo=oracle.json incluir=ejemplo/batalla-naval/oracle.json
```

## Paso 2 · El tablero

Un juego en el navegador son tres cosas: **HTML** (qué hay en la pantalla), **CSS** (cómo se ve) y
**JavaScript** (qué pasa cuando hacés algo). Empezamos por las dos primeras.

<details>
<summary>Ver el archivo index.html</summary>

```html archivo=index.html incluir=ejemplo/batalla-naval/index.html
```

</details>

<details>
<summary>Ver el archivo css/style.css</summary>

```css archivo=css/style.css incluir=ejemplo/batalla-naval/css/style.css
```

</details>

Abrí `index.html` en el navegador (doble clic, o arrastralo a una pestaña). Vas a ver la cabecera y los
paneles, **sin tableros todavía**: los tableros los dibuja el JavaScript.

## Paso 3 · El juego

Estos cuatro archivos son el juego: el sonido, el registro de lo que pasa, el motor con las reglas y
la interfaz que dibuja los tableros.

<details>
<summary>Ver los cuatro archivos de JavaScript</summary>

```javascript archivo=js/audio.js incluir=ejemplo/batalla-naval/js/audio.js
```

```javascript archivo=js/trace.js incluir=ejemplo/batalla-naval/js/trace.js
```

```javascript archivo=js/engine.js incluir=ejemplo/batalla-naval/js/engine.js
```

```javascript archivo=js/ui.js incluir=ejemplo/batalla-naval/js/ui.js
```

</details>

Recargá la página. Ahora se juega: colocá tus barcos (o usá el despliegue automático) y disparale a
la computadora.

**Si ves otra cosa.** Si la página queda en blanco, abrí la consola del navegador (F12, pestaña
Consola). Casi siempre es un archivo guardado con otro nombre o en otra carpeta: tienen que quedar
`js/audio.js`, `js/trace.js`, `js/engine.js` y `js/ui.js`.

<p class="pregunta">**Pensalo.** El juego anda. ¿Eso quiere decir que cumple las reglas?</p>

<details>
<summary>Ver la respuesta</summary>

No. Quiere decir que anda. Jugando una vez no sabés si un barco puede quedar fuera del tablero, si dos
barcos se pueden pisar, si los turnos alternan siempre o si un «¡impacto!» tenía un barco abajo. Y si
le pedís al mismo modelo que escribió el juego que también escriba los tests, los tests van a confirmar
lo que el modelo ya creía.

</details>

## Paso 4 · Que el juego cuente lo que pasó

<p class="pregunta">**Pensalo.** Para juzgar un disparo después de la partida, ¿qué tendría que haber anotado el juego?</p>

<details>
<summary>Ver la respuesta</summary>

El turno, quién tiró, a quién, en qué casilla, y si el juego lo dio por impacto. Para juzgar si ese
impacto era verdad, también dónde estaba cada barco. Y para juzgar el final, quién ganó y con cuántos
impactos.

</details>

Esa es la idea central de Oracle: **el juego no se juzga a sí mismo, cuenta lo que pasó.** El archivo
`js/trace.js`, que ya pegaste, anota tres cosas en filas planas, sin opinar:

| Relación | Una fila por… | Campos |
|---|---|---|
| `celda_barco` | cada casilla ocupada por un barco | `id`, `jugador`, `barco_id`, `segmento_idx`, `fila`, `columna` |
| `tiro` | cada disparo | `turno`, `tirador`, `receptor`, `fila`, `columna`, `es_impacto`, `hundio_barco`, `barco_hundido` |
| `partida` | el final | `estado`, `ganador`, `perdedor`, `turno_final`, `total_tiros`, `impactos_ganador`, `impactos_perdedor` |

Al terminar una partida, el panel de auditoría del juego descarga esas filas como `hechos_partida.json`.
Así se ve el primer tiro de una partida real:

```json
{"turno": 0, "tirador": "jugador", "receptor": "cpu", "fila": 2, "columna": 3, "es_impacto": false, "hundio_barco": false, "barco_hundido": "ninguno"}
```

**Si trabajás con un modelo**, pedíselo así: «agregá un registro que anote cada casilla de barco, cada
tiro y el resultado final en filas planas, y que lo descargue como JSON». Y **desconfiá** si en vez de
anotar lo que pasó, el registro anota conclusiones («partida válida: sí»): eso ya es opinión.

## Paso 5 · La primera regla, empezando por el caso rojo

La regla más simple: **ningún barco fuera del tablero de 10 por 10.**

<p class="pregunta">**Pensalo.** Antes de escribir la regla: ¿qué partida tendría que ponerla roja?</p>

<details>
<summary>Ver la respuesta</summary>

Una con un barco en una casilla que no existe: por ejemplo, en la fila 10 (las filas van de 0 a 9).
Escribir primero ese ejemplo te obliga a decir qué es un defecto antes de escribir cómo buscarlo.

</details>

En Oracle ese ejemplo se llama **caso**. Guardalo en `corpus/naval/`:

```oracle archivo=corpus/naval/005-barco-fila-desbordada.caso incluir=ejemplo/batalla-naval/corpus/naval/005-barco-fila-desbordada.caso
```

```bash paso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 1 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 0 medidas · 0 macros · 1 casos

catálogo: 0 medidas · corpus: 1 casos


defectos que se pusieron rojos: 0 · verdes correctos: 0 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✗ — 1 problema(s)
  · 005-barco-fila-desbordada: reclama la medida «naval.barcos_dentro_del_tablero» y no está en el catálogo

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

MUTACIÓN: salteada (sin medidas todavía)

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: ROJO (falló: aceptación)
```

Rojo, y está bien: el caso reclama una regla que todavía no existe. Ahora sí, la regla. En Oracle se
llama **medida**:

```oracle archivo=catalogos/naval/naval.barcos_dentro_del_tablero.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.barcos_dentro_del_tablero.oracle
```

Línea por línea: `ninguno` dice que **no tiene que haber ninguna** fila que ofenda; `de celda_barco c`
elige qué mirar; `donde` dice cuáles ofenden; `umbral <= 0` cuántas se toleran, `segun contrato` de
dónde sale ese cero y `porque` lo defiende; `alcance` dice **qué no mira**.

<p class="pregunta">**Pensalo.** ¿Qué no está mirando esta regla?</p>

<details>
<summary>Ver la respuesta</summary>

Lo dice su `alcance`: no mira si dos barcos se pisan ni si un barco es una línea continua. Un verde de
esta regla no promete eso. Por eso el `alcance` es obligatorio: un verde que no dice qué dejó sin
mirar se lee como «está todo bien».

</details>

```bash paso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 1 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 1 casos

catálogo: 1 medidas · corpus: 1 casos

  ROJO  005-barco-fila-desbordada              naval.barcos_dentro_del_tablero  (valor 1)

defectos que se pusieron rojos: 1 · verdes correctos: 0 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 1 defectos en rojo, 0 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 18 · murieron 10 · sobrevivieron 8
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 10 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 18

sin políticas meta activas — se informa sólo el resultado operativo

lo que el corpus NO fija — ningún caso detecta estas mutaciones:
  · mutar «quitar_filtro» en naval.barcos_dentro_del_tablero pasa inadvertido
  · mutar «alejar_limite_de_defecto» en naval.barcos_dentro_del_tablero pasa inadvertido
  · mutar «expresion:comparador@2.2.1.1:<→>=» en naval.barcos_dentro_del_tablero pasa inadvertido
  · mutar «expresion:comparador@2.2.1.3:<→>=» en naval.barcos_dentro_del_tablero pasa inadvertido
  · mutar «expresion:comparador@2.2.1.4:>→<=» en naval.barcos_dentro_del_tablero pasa inadvertido
  · mutar «campo:2.2.1.1.1.2:fila→columna» en naval.barcos_dentro_del_tablero pasa inadvertido
  · mutar «campo:2.2.1.3.1.2:columna→fila» en naval.barcos_dentro_del_tablero pasa inadvertido
  · mutar «campo:2.2.1.4.1.2:columna→fila» en naval.barcos_dentro_del_tablero pasa inadvertido

Se tapa agregando un caso que SÍ lo note o declarando una equivalencia individual
demostrable; nunca debilitando el mutador. La polaridad y el borde también importan:
`quitar_filtro` suele pedir un verde; `aflojar_umbral`, un rojo junto al límite.

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: ROJO (falló: mutación)
```

## Paso 6 · Un caso rojo no alcanza: la mutación

Todavía rojo, pero por otra razón: **sobreviven mutantes**. Oracle debilita tu regla a propósito
(afloja el umbral, invierte una comparación, le quita el filtro) y se fija si tus casos lo notan. A cada
versión debilitada la llama **mutante**.

<p class="pregunta">**Pensalo.** Si Oracle le quita el `donde` a la regla, pasa a contar todas las casillas. Tu único caso sigue saliendo rojo. ¿Qué caso haría falta para que se note?</p>

<details>
<summary>Ver la respuesta</summary>

Uno **verde**: una partida con todos los barcos dentro, que la regla sin filtro pondría roja. Y conviene
que esté en el borde (fila 9), para que también se note si alguien corre el límite.

</details>

```oracle archivo=corpus/naval/006-barco-en-borde.caso incluir=ejemplo/batalla-naval/corpus/naval/006-barco-en-borde.caso
```

```bash paso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 2 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 2 casos

catálogo: 1 medidas · corpus: 2 casos

  ROJO  005-barco-fila-desbordada              naval.barcos_dentro_del_tablero  (valor 1)
  verde 006-barco-en-borde                     naval.barcos_dentro_del_tablero  (valor 0)

defectos que se pusieron rojos: 1 · verdes correctos: 1 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 1 defectos en rojo, 1 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 18 · murieron 14 · sobrevivieron 4
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 14 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 36

sin políticas meta activas — se informa sólo el resultado operativo

lo que el corpus NO fija — ningún caso detecta estas mutaciones:
  · mutar «alejar_limite_de_defecto» en naval.barcos_dentro_del_tablero pasa inadvertido
  · mutar «campo:2.2.1.1.1.2:fila→columna» en naval.barcos_dentro_del_tablero pasa inadvertido
  · mutar «campo:2.2.1.3.1.2:columna→fila» en naval.barcos_dentro_del_tablero pasa inadvertido
  · mutar «campo:2.2.1.4.1.2:columna→fila» en naval.barcos_dentro_del_tablero pasa inadvertido

Se tapa agregando un caso que SÍ lo note o declarando una equivalencia individual
demostrable; nunca debilitando el mutador. La polaridad y el borde también importan:
`quitar_filtro` suele pedir un verde; `aflojar_umbral`, un rojo junto al límite.

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: ROJO (falló: mutación)
```

Quedan mutantes vivos. La regla tiene cuatro formas de ofender (fila menor que 0, fila mayor que 9,
columna menor que 0, columna mayor que 9) y tu caso rojo sólo prueba una. Los otros tres casos rojos:

```oracle archivo=corpus/naval/026-barco-columna-desbordada.caso incluir=ejemplo/batalla-naval/corpus/naval/026-barco-columna-desbordada.caso
```

```oracle archivo=corpus/naval/027-barco-fila-negativa.caso incluir=ejemplo/batalla-naval/corpus/naval/027-barco-fila-negativa.caso
```

```oracle archivo=corpus/naval/028-barco-columna-negativa.caso incluir=ejemplo/batalla-naval/corpus/naval/028-barco-columna-negativa.caso
```

```bash paso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 5 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 5 casos

catálogo: 1 medidas · corpus: 5 casos

  ROJO  005-barco-fila-desbordada              naval.barcos_dentro_del_tablero  (valor 1)
  verde 006-barco-en-borde                     naval.barcos_dentro_del_tablero  (valor 0)
  ROJO  026-barco-columna-desbordada           naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  027-barco-fila-negativa                naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  028-barco-columna-negativa             naval.barcos_dentro_del_tablero  (valor 1)

defectos que se pusieron rojos: 4 · verdes correctos: 1 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 4 defectos en rojo, 1 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 18 · murieron 18 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 18 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 90

sin políticas meta activas — se informa sólo el resultado operativo

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: VERDE (todas las verificaciones aplicables en regla)
```

**Verde, y ahora el verde significa algo**: cada forma de debilitar la regla la nota algún caso.

## Paso 7 · Diez reglas más, y la trampa de los pocos casos

El juego tiene más reglas. Pegá las diez que faltan de una vez, cada una con su idea:

<details>
<summary>Ver las diez medidas</summary>

```oracle archivo=catalogos/naval/naval.tiros_dentro_del_tablero.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.tiros_dentro_del_tablero.oracle
```

```oracle archivo=catalogos/naval/naval.barcos_sin_solapamiento.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.barcos_sin_solapamiento.oracle
```

```oracle archivo=catalogos/naval/naval.flota_reglamentaria.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.flota_reglamentaria.oracle
```

```oracle archivo=catalogos/naval/naval.alternancia_turnos.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.alternancia_turnos.oracle
```

```oracle archivo=catalogos/naval/naval.turnos_sin_huecos.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.turnos_sin_huecos.oracle
```

```oracle archivo=catalogos/naval/naval.tiros_sin_repeticion.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.tiros_sin_repeticion.oracle
```

```oracle archivo=catalogos/naval/naval.veracidad_impacto_positivo.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.veracidad_impacto_positivo.oracle
```

```oracle archivo=catalogos/naval/naval.veracidad_impacto_negativo.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.veracidad_impacto_negativo.oracle
```

```oracle archivo=catalogos/naval/naval.ganador_legitimo.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.ganador_legitimo.oracle
```

```oracle archivo=catalogos/naval/naval.fin_de_juego_sin_tiros_posteriores.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.fin_de_juego_sin_tiros_posteriores.oracle
```

</details>

Tres para mirar con calma, porque cada una enseña algo del lenguaje:

- `naval.alternancia_turnos` compara cada tiro con el siguiente usando `unir`, y se escribe como lo
  pensás: `t2.turno == t1.turno + 1`.
- `naval.flota_reglamentaria` usa `agrupar` para contar las casillas de cada jugador y dice `requiere
  celda_barco`: si el juego no mandó ningún barco, la regla no sale verde, sale **sin evidencia**. Cero
  barcos no es una flota correcta, es un registro roto.
- `naval.veracidad_impacto_positivo` usa `sin`: busca los tiros marcados como impacto **sin** ningún
  barco del rival en esa casilla.

Con el juego original venían sólo dos casos, los dos de la regla de tiros:

```oracle archivo=corpus/naval/001-tiro-fuera-de-tablero.caso incluir=ejemplo/batalla-naval/corpus/naval/001-tiro-fuera-de-tablero.caso
```

```oracle archivo=corpus/naval/002-tiro-valido.caso incluir=ejemplo/batalla-naval/corpus/naval/002-tiro-valido.caso
```

<p class="pregunta">**Pensalo.** Once reglas y siete casos, casi todos de dos reglas. ¿Qué tendría que decir `oracle test`?</p>

<details>
<summary>Ver la respuesta</summary>

Que la mayoría de las reglas no las prueba nadie. Una regla sin casos que puedan romperla es
decoración: puede estar mal escrita y dar verde siempre, y nunca te vas a enterar.

</details>

```bash paso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 7 casos · esquema, evidencia L0 y trazabilidad en regla

MEDIDAS SIN CASOS ✗ — 9 medida(s) propias sin ejercitar:
  · naval.alternancia_turnos: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.barcos_sin_solapamiento: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.fin_de_juego_sin_tiros_posteriores: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.flota_reglamentaria: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.ganador_legitimo: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.tiros_sin_repeticion: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.turnos_sin_huecos: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.veracidad_impacto_negativo: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.veracidad_impacto_positivo: escribí un caso rojo y uno verde que ejerzan esta medida

SINTAXIS OK · 11 medidas · 0 macros · 7 casos

catálogo: 11 medidas · corpus: 7 casos

  ROJO  001-tiro-fuera-de-tablero              naval.tiros_dentro_del_tablero  (valor 1)
  verde 002-tiro-valido                        naval.tiros_dentro_del_tablero  (valor 0)
  ROJO  005-barco-fila-desbordada              naval.barcos_dentro_del_tablero  (valor 1)
  verde 006-barco-en-borde                     naval.barcos_dentro_del_tablero  (valor 0)
  ROJO  026-barco-columna-desbordada           naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  027-barco-fila-negativa                naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  028-barco-columna-negativa             naval.barcos_dentro_del_tablero  (valor 1)

defectos que se pusieron rojos: 5 · verdes correctos: 2 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 5 defectos en rojo, 2 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 36 · murieron 32 · sobrevivieron 4
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 32 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 126

medidas que no se pudieron mutar por falta de casos:
  · naval.alternancia_turnos: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.barcos_sin_solapamiento: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.fin_de_juego_sin_tiros_posteriores: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.flota_reglamentaria: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.ganador_legitimo: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.tiros_sin_repeticion: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.turnos_sin_huecos: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.veracidad_impacto_negativo: escribí un caso rojo y uno verde que ejerzan esta medida
  · naval.veracidad_impacto_positivo: escribí un caso rojo y uno verde que ejerzan esta medida
sin políticas meta activas — se informa sólo el resultado operativo

lo que el corpus NO fija — ningún caso detecta estas mutaciones:
  · mutar «alejar_limite_de_defecto» en naval.tiros_dentro_del_tablero pasa inadvertido
  · mutar «campo:2.2.1.1.1.2:fila→columna» en naval.tiros_dentro_del_tablero pasa inadvertido
  · mutar «campo:2.2.1.3.1.2:columna→fila» en naval.tiros_dentro_del_tablero pasa inadvertido
  · mutar «campo:2.2.1.4.1.2:columna→fila» en naval.tiros_dentro_del_tablero pasa inadvertido

Se tapa agregando un caso que SÍ lo note o declarando una equivalencia individual
demostrable; nunca debilitando el mutador. La polaridad y el borde también importan:
`quitar_filtro` suele pedir un verde; `aflojar_umbral`, un rojo junto al límite.

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: ROJO (falló: medidas sin casos, mutación)
```

Los casos que faltan: para cada regla, al menos uno que la ponga roja cerca del borde y uno verde.

<details>
<summary>Ver los casos que faltan</summary>

```oracle archivo=corpus/naval/023-columna-desbordada.caso incluir=ejemplo/batalla-naval/corpus/naval/023-columna-desbordada.caso
```

```oracle archivo=corpus/naval/024-fila-negativa.caso incluir=ejemplo/batalla-naval/corpus/naval/024-fila-negativa.caso
```

```oracle archivo=corpus/naval/025-columna-negativa.caso incluir=ejemplo/batalla-naval/corpus/naval/025-columna-negativa.caso
```

```oracle archivo=corpus/naval/007-barcos-superpuestos.caso incluir=ejemplo/batalla-naval/corpus/naval/007-barcos-superpuestos.caso
```

```oracle archivo=corpus/naval/008-barcos-separados.caso incluir=ejemplo/batalla-naval/corpus/naval/008-barcos-separados.caso
```

```oracle archivo=corpus/naval/011-flota-de-dieciseis.caso incluir=ejemplo/batalla-naval/corpus/naval/011-flota-de-dieciseis.caso
```

```oracle archivo=corpus/naval/012-flota-de-diecisiete.caso incluir=ejemplo/batalla-naval/corpus/naval/012-flota-de-diecisiete.caso
```

```oracle archivo=corpus/naval/029-flota-sin-celdas.caso incluir=ejemplo/batalla-naval/corpus/naval/029-flota-sin-celdas.caso
```

```oracle archivo=corpus/naval/003-mismo-tirador-seguido.caso incluir=ejemplo/batalla-naval/corpus/naval/003-mismo-tirador-seguido.caso
```

```oracle archivo=corpus/naval/004-tiradores-alternos.caso incluir=ejemplo/batalla-naval/corpus/naval/004-tiradores-alternos.caso
```

```oracle archivo=corpus/naval/017-turno-saltado.caso incluir=ejemplo/batalla-naval/corpus/naval/017-turno-saltado.caso
```

```oracle archivo=corpus/naval/018-turnos-contiguos.caso incluir=ejemplo/batalla-naval/corpus/naval/018-turnos-contiguos.caso
```

```oracle archivo=corpus/naval/030-sin-tiros-registrados.caso incluir=ejemplo/batalla-naval/corpus/naval/030-sin-tiros-registrados.caso
```

```oracle archivo=corpus/naval/015-tiro-repetido.caso incluir=ejemplo/batalla-naval/corpus/naval/015-tiro-repetido.caso
```

```oracle archivo=corpus/naval/016-tiros-distintos.caso incluir=ejemplo/batalla-naval/corpus/naval/016-tiros-distintos.caso
```

```oracle archivo=corpus/naval/031-distinta-fila-igual-turno-ajeno.caso incluir=ejemplo/batalla-naval/corpus/naval/031-distinta-fila-igual-turno-ajeno.caso
```

```oracle archivo=corpus/naval/033-fila-confundida-con-turno.caso incluir=ejemplo/batalla-naval/corpus/naval/033-fila-confundida-con-turno.caso
```

```oracle archivo=corpus/naval/021-impacto-fantasma.caso incluir=ejemplo/batalla-naval/corpus/naval/021-impacto-fantasma.caso
```

```oracle archivo=corpus/naval/022-impacto-real.caso incluir=ejemplo/batalla-naval/corpus/naval/022-impacto-real.caso
```

```oracle archivo=corpus/naval/032-agua-declarada-agua.caso incluir=ejemplo/batalla-naval/corpus/naval/032-agua-declarada-agua.caso
```

```oracle archivo=corpus/naval/019-barco-reportado-como-agua.caso incluir=ejemplo/batalla-naval/corpus/naval/019-barco-reportado-como-agua.caso
```

```oracle archivo=corpus/naval/020-agua-reportada-como-agua.caso incluir=ejemplo/batalla-naval/corpus/naval/020-agua-reportada-como-agua.caso
```

```oracle archivo=corpus/naval/013-ganador-con-dieciseis-impactos.caso incluir=ejemplo/batalla-naval/corpus/naval/013-ganador-con-dieciseis-impactos.caso
```

```oracle archivo=corpus/naval/014-ganador-con-diecisiete-impactos.caso incluir=ejemplo/batalla-naval/corpus/naval/014-ganador-con-diecisiete-impactos.caso
```

```oracle archivo=corpus/naval/009-tiro-despues-del-final.caso incluir=ejemplo/batalla-naval/corpus/naval/009-tiro-despues-del-final.caso
```

```oracle archivo=corpus/naval/010-tiro-en-turno-final.caso incluir=ejemplo/batalla-naval/corpus/naval/010-tiro-en-turno-final.caso
```

</details>

```bash paso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 33 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 11 medidas · 0 macros · 33 casos

catálogo: 11 medidas · corpus: 33 casos

  ROJO  001-tiro-fuera-de-tablero              naval.tiros_dentro_del_tablero  (valor 1)
  verde 002-tiro-valido                        naval.tiros_dentro_del_tablero  (valor 0)
  ROJO  003-mismo-tirador-seguido              naval.alternancia_turnos  (valor 1)
  verde 004-tiradores-alternos                 naval.alternancia_turnos  (valor 0)
  ROJO  005-barco-fila-desbordada              naval.barcos_dentro_del_tablero  (valor 1)
  verde 006-barco-en-borde                     naval.barcos_dentro_del_tablero  (valor 0)
  ROJO  007-barcos-superpuestos                naval.barcos_sin_solapamiento  (valor 1)
  verde 008-barcos-separados                   naval.barcos_sin_solapamiento  (valor 0)
  ROJO  009-tiro-despues-del-final             naval.fin_de_juego_sin_tiros_posteriores  (valor 1)
  verde 010-tiro-en-turno-final                naval.fin_de_juego_sin_tiros_posteriores  (valor 0)
  ROJO  011-flota-de-dieciseis                 naval.flota_reglamentaria  (valor 1)
  verde 012-flota-de-diecisiete                naval.flota_reglamentaria  (valor 0)
  ROJO  013-ganador-con-dieciseis-impactos     naval.ganador_legitimo  (valor 1)
  verde 014-ganador-con-diecisiete-impactos    naval.ganador_legitimo  (valor 0)
  ROJO  015-tiro-repetido                      naval.tiros_sin_repeticion  (valor 1)
  verde 016-tiros-distintos                    naval.tiros_sin_repeticion  (valor 0)
  ROJO  017-turno-saltado                      naval.turnos_sin_huecos  (valor 1)
  verde 018-turnos-contiguos                   naval.turnos_sin_huecos  (valor 0)
  ROJO  019-barco-reportado-como-agua          naval.veracidad_impacto_negativo  (valor 1)
  verde 020-agua-reportada-como-agua           naval.veracidad_impacto_negativo  (valor 0)
  ROJO  021-impacto-fantasma                   naval.veracidad_impacto_positivo  (valor 1)
  verde 022-impacto-real                       naval.veracidad_impacto_positivo  (valor 0)
  ROJO  023-columna-desbordada                 naval.tiros_dentro_del_tablero  (valor 1)
  ROJO  024-fila-negativa                      naval.tiros_dentro_del_tablero  (valor 1)
  ROJO  025-columna-negativa                   naval.tiros_dentro_del_tablero  (valor 1)
  ROJO  026-barco-columna-desbordada           naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  027-barco-fila-negativa                naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  028-barco-columna-negativa             naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  029-flota-sin-celdas                   naval.flota_reglamentaria  (SIN EVIDENCIA: «celda_barco» vacía)
  ROJO  030-sin-tiros-registrados              naval.turnos_sin_huecos  (SIN EVIDENCIA: «tiro» vacía)
  verde 031-distinta-fila-igual-turno-ajeno    naval.tiros_sin_repeticion  (valor 0)
  verde 032-agua-declarada-agua                naval.veracidad_impacto_positivo  (valor 0)
  verde 033-fila-confundida-con-turno          naval.tiros_sin_repeticion  (valor 0)

defectos que se pusieron rojos: 19 · verdes correctos: 14 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 19 defectos en rojo, 14 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 209 · murieron 209 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 158 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 51 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 634

sin políticas meta activas — se informa sólo el resultado operativo

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: VERDE (todas las verificaciones aplicables en regla)
```

Once reglas, cada una con casos que la pueden romper, y ningún mutante vivo.

## Paso 8 · Juzgar una partida de verdad

Las reglas ya están probadas. Ahora se juzga una partida real: jugá una partida entera, abrí el panel
de auditoría y descargá `hechos_partida.json` en la carpeta del proyecto. (Si todavía no jugaste, podés
[bajar la partida del ejemplo](https://github.com/Segtem/oracle/raw/main/ejemplo/batalla-naval/partida_real.json)
y guardarla con ese nombre.)

<details>
<summary>Ver la partida del ejemplo (hechos_partida.json)</summary>

```json archivo=hechos_partida.json incluir=ejemplo/batalla-naval/partida_real.json
```

</details>

```bash paso
oracle juzgar --con hechos_partida.json
```

```text salida
✓ naval.alternancia_turnos                            0 (<= 0)
✓ naval.barcos_dentro_del_tablero                     0 (<= 0)
✓ naval.barcos_sin_solapamiento                       0 (<= 0)
✓ naval.fin_de_juego_sin_tiros_posteriores            0 (<= 0)
✓ naval.flota_reglamentaria                           0 (<= 0)
✓ naval.ganador_legitimo                              0 (<= 0)
✓ naval.tiros_dentro_del_tablero                      0 (<= 0)
✓ naval.tiros_sin_repeticion                          0 (<= 0)
✓ naval.turnos_sin_huecos                             0 (<= 0)
✓ naval.veracidad_impacto_negativo                    0 (<= 0)
✓ naval.veracidad_impacto_positivo                    0 (<= 0)

VEREDICTO: verde en 11 medidas. SIN MIRAR:
  · naval.alternancia_turnos: compara el tirador del turno k con el tirador del turno k+1. No valida la ausencia de saltos si falta un turno completo.
  · naval.barcos_dentro_del_tablero: revisa los límites de cada celda de barco reportada. No verifica solapamientos ni continuidad.
  · naval.barcos_sin_solapamiento: detecta pares de celdas distintas del mismo jugador con id1 < id2 que colisionan en la misma coordenada. No comprueba barcos de jugadores opuestos.
  · naval.fin_de_juego_sin_tiros_posteriores: compara el turno de cada tiro contra el turno final registrado en el estado de la partida. No valida si la partida debió terminar antes.
  · naval.flota_reglamentaria: agrupa las casillas de barco por jugador y exige exactamente 17 casillas por flota. No comprueba la orientación lineal de los barcos.
  · naval.ganador_legitimo: comprueba que los impactos acumulados por el ganador sean exactamente 17. No valida si los tiros fueron asignados al tirador correcto.
  · naval.tiros_dentro_del_tablero: comprueba que las coordenadas de cada disparo estén en el rango [0, 9]. No comprueba si el casillero ya fue disparado previamente ni la validez del turno.
  · naval.tiros_sin_repeticion: detecta disparos repetidos del mismo jugador a la misma celda con diferente número de turno. No evalúa si el tiro fue agua o impacto.
  · naval.turnos_sin_huecos: compara la cantidad total de tiros registrados contra el turno máximo reportado más uno. No valida la alternancia de tiradores.
  · naval.veracidad_impacto_negativo: cruza cada disparo contra las celdas de la flota rival y detecta impactos omitidos registrados falsamente como agua. No verifica la secuencia de turnos.
  · naval.veracidad_impacto_positivo: detecta disparos registrados como impacto que no corresponden a ninguna celda ocupada por la flota del receptor. No verifica si el barco ya estaba completamente hundido.
```

<p class="pregunta">**Pensalo.** Todo verde. ¿Quiere decir que el juego está bien?</p>

<details>
<summary>Ver la respuesta</summary>

Quiere decir que esas once reglas se cumplieron en esta partida. La lista `SIN MIRAR` dice lo que
ninguna regla garantiza, por ejemplo que cada barco sea una línea recta. Esa lista no es letra chica:
es la mitad de la respuesta.

</details>

<p class="pregunta">**Pensalo.** ¿Y si el juego se olvidara de anotar los tiros?</p>

<details>
<summary>Ver la respuesta</summary>

Las reglas de tiros no tendrían nada que mirar. Un sistema descuidado las daría por buenas; Oracle las
lista aparte, en `NO SE APLICARON`, y falla la corrida completa. Si ejecutás sólo una parte del
catálogo a propósito, `--parcial` permite esa omisión. Probalo:

</details>

```bash paso
python3 -c "import json; d = json.load(open('hechos_partida.json')); json.dump({'celda_barco': d['celda_barco'], 'partida': d['partida']}, open('sin-tiros.json', 'w'))"
oracle juzgar --con sin-tiros.json
```

```text salida
✓ naval.barcos_dentro_del_tablero                     0 (<= 0)
✓ naval.barcos_sin_solapamiento                       0 (<= 0)
✓ naval.flota_reglamentaria                           0 (<= 0)
✓ naval.ganador_legitimo                              0 (<= 0)

NO SE APLICARON (7) — su relación no vino en la evidencia:
  · naval.alternancia_turnos: falta tiro
  · naval.fin_de_juego_sin_tiros_posteriores: falta tiro
  · naval.tiros_dentro_del_tablero: falta tiro
  · naval.tiros_sin_repeticion: falta tiro
  · naval.turnos_sin_huecos: falta tiro
  · naval.veracidad_impacto_negativo: falta tiro
  · naval.veracidad_impacto_positivo: falta tiro

VEREDICTO: 7 medidas propias sin aplicar (usá --parcial para una corrida deliberadamente parcial)
```

Si una regla sale roja, el veredicto trae **testigos**: las filas exactas que ofendieron. Con eso le
volvés a hablar al modelo con precisión: «el tiro del turno 14 se marcó como impacto y no había barco
en esa casilla; corregilo».

## Paso 9 · Qué le falta a este juego

Once reglas miran lo principal, no todo. Ninguna mira hoy:

- que cada barco sea una línea recta y continua (se cuentan casillas, no la forma);
- que un barco hundido tenga todas sus casillas impactadas;
- que la computadora no sepa dónde están tus barcos antes de dispararles.

<p class="pregunta">**Pensalo.** Elegí una. ¿Qué hecho tendría que anotar el juego, qué fila ofendería y qué caso rojo la fijaría?</p>

<details>
<summary>Ver una respuesta, para la de la línea recta</summary>

Con `celda_barco` alcanza: las casillas de un mismo `barco_id` tienen que compartir la fila (y tener
columnas consecutivas) o compartir la columna (y tener filas consecutivas). Una fila ofende si su barco
tiene casillas en dos filas y dos columnas distintas a la vez. El caso rojo: un destructor con una
casilla en (2,3) y otra en (3,4), en diagonal.

</details>

Y el catálogo base que apagaste en el paso 1: encendelo (`"catalogo_base": true`) y corré `oracle
test`. Te va a pedir lo que falta para que estas reglas valgan fuera de esta guía: declarar las unidades
de los campos y sostener cada regla con partidas **observadas**, no sólo con casos construidos.

## Si trabajás con un modelo

1. **Pedile que el juego cuente lo que pasa**, en filas planas, sin conclusiones.
2. **No le pidas las reglas y el código en la misma pasada.** Escribí o revisá vos las reglas.
3. **Pedile primero el caso rojo**, después la regla. Si te da la regla sin caso, desconfiá.
4. **Leé el `alcance`** de cada regla: es lo que el verde no te promete.
5. **Cuando algo sale rojo, pasale los testigos**, no una descripción vaga.
6. **Si te dice «ya está todo verificado», preguntale qué mutantes sobrevivieron** y qué dice `SIN MIRAR`.

Después de esto, [La primera medida real](13-primer-valor.html) muestra el mismo recorrido con menos
explicación, y [Escribir una medida](03-escribir-una-medida.html) es la referencia del lenguaje.
