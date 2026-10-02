# Tu primer juego con un LLM, y cómo saber si está bien

Esta guía es para alguien que recién empieza a programar y programa con un modelo de lenguaje. Un
**modelo de lenguaje** (o **LLM**, por sus siglas en inglés) es una inteligencia artificial generativa,
como ChatGPT, Claude o Gemini, que puede escribir código a partir de tus pedidos en lenguaje cotidiano.
Vas a armar, **copiando y pegando** código en archivos de texto simples en tu computadora, una batalla
naval que corre en el navegador web (como Chrome, Firefox o Edge). «Corre en el navegador» significa que no
necesitás instalar programas raros para jugar: funciona directamente como una página web en tu máquina al
hacerle doble clic. Y vas a aprender a contestar la pregunta que el juego solo no puede contestar:
**¿cumple las reglas de verdad?**

Para vigilar las reglas creamos **Oracle**: un programa independiente que examina lo que pasó en el juego
sin juzgarse a sí mismo. A las partidas de prueba (tanto las limpias como las que cometen trampas para ver si
el sistema las nota) las llamamos **casos**. Y a las versiones de tus reglas alteradas a propósito con trampas
para probar si tus defensas son sólidas las llamamos **mutantes**.

La guía es una travesía de **nueve misiones**. Cada una tiene la misma forma: una **pregunta** para
que la pienses vos, la **respuesta** plegada (abrila cuando quieras), el **bloque para copiar**, y **lo
que tenés que ver**. Si ves otra cosa, el paso te dice qué hacer.

En el sitio, además, se juega: antes de cada salida **predecís** qué va a decir Oracle, en la misión 5
**rompés la regla** en un tablero, y en la 6 **cazás los mutantes** de tu regla eligiendo casos. Cada
cosa suma experiencia y algunas dan logros; la bitácora, abajo a la derecha, lleva la cuenta. Todo queda
en tu navegador: no se manda a ningún lado.

> El test de esta guía reconstruye los archivos en una carpeta temporal vacía y comprueba los comandos de
> Oracle y sus salidas. No instala las herramientas ni prueba los clics en tu navegador. Los tiempos de
> ejecución y algunos mensajes de instalación o de Git pueden variar en tu computadora.

## Antes de empezar

Antes de arrancar con la primera misión, necesitás tener lista tu computadora. No hace falta que sepas nada
previo: acá tenés el paso a paso para preparar las herramientas.

### Qué es una terminal y cómo se abre

Una **terminal** (también llamada consola o línea de comandos) es una ventana donde le das órdenes directas
a la computadora escribiendo texto con el teclado, en vez de hacer clics con el ratón. Cada línea de texto
que escribís es un **comando**; cuando presionás la tecla **Enter**, la computadora ejecuta esa orden y te
muestra el resultado en la pantalla.

Cómo abrirla según tu sistema operativo:

- **En Windows:** presioná la tecla Windows, escribí `Terminal` (o `PowerShell`) y presioná Enter. *Tip:* en
  la terminal de Windows, si querés pegar texto y `Ctrl + V` no responde, hacé clic derecho adentro de la
  ventana negra para pegar.
- **En macOS:** presioná las teclas `Cmd + Barra espaciadora`, escribí `Terminal` y presioná Enter.
- **En Linux:** presioná `Ctrl + Alt + T` o buscá `Terminal` en tu menú de aplicaciones.

Cómo moverte entre carpetas desde la terminal:

- Al abrir la terminal, estás parado en tu carpeta personal de usuario (por ejemplo `C:\Users\TuNombre` en
  Windows o `/home/tunombre` en Linux).
- Para saber en qué carpeta estás en cualquier momento, escribí `pwd` y presioná Enter (en Windows PowerShell
  también funciona `pwd`).
- Para entrar a una carpeta escribí `cd nombre-carpeta` (`cd` significa *change directory*, cambiar directorio)
  y presioná Enter.
- Para salir de la carpeta actual y retroceder a la carpeta anterior, escribí `cd ..` y presioná Enter.

### Qué instalar y cómo

Necesitás tener instalados estos cuatro programas gratuitos:

1. **Python (versión 3.11 o posterior):** es el lenguaje en el que está programado Oracle. Descargalo gratis
   desde [python.org](https://www.python.org/downloads/).
   - *Paso crítico en Windows:* al iniciar el instalador, antes de tocar cualquier botón, marcá la casilla que
     dice **«Add python.exe to PATH»** abajo de todo. Si no la marcás, tu terminal no va a reconocer los comandos
     de Python.
2. **`uv`:** es una herramienta moderna y ultrarrápida para instalar y ejecutar aplicaciones de Python. Para
   instalarlo, abrí tu terminal y ejecutá el comando que corresponda a tu sistema:
   - En macOS y Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - En Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - Si preferís ver la guía oficial, consultá [docs.astral.sh/uv](https://docs.astral.sh/uv).
3. **Git:** es un programa que guarda versiones de los archivos de tu proyecto para poder comparar cambios
   y volver a una versión anterior. Ese historial queda en tu computadora.
   Descargalo e instalalo desde [git-scm.com](https://git-scm.com/downloads) manteniendo todas las opciones
   recomendadas por defecto.
4. **Un editor de texto para código:** para crear y guardar los archivos del juego necesitás un editor de texto
   plano. **Nunca uses Microsoft Word ni WordPad**: agregan formatos invisibles y comillas tipográficas que
   rompen el código de programación. Te recomendamos descargar gratis [Visual Studio Code](https://code.visualstudio.com/).
   Si no querés instalar un editor nuevo, podés usar el **Bloc de Notas** de Windows (o TextEdit en Mac configurado
   en texto plano).

### Cómo comprobar que quedó todo instalado

Abrí una ventana nueva de la terminal (para que tome las instalaciones recientes) y escribí estos tres comandos,
presionando Enter después de cada uno:

- `python --version` (o `python3 --version` en Mac y Linux): tiene que responderte con `Python 3.11` o un número mayor.
- `uv --version`: tiene que mostrar la versión instalada de `uv`.
- `git --version`: tiene que mostrar la versión instalada de `git`.

Si alguno te dice «comando no encontrado» (*command not found*), cerrá la terminal y volvé a abrirla. Si sigue sin
reconocerlo, reinstalá ese programa asegurándote de marcar la opción de agregarlo al PATH del sistema.

### Cómo crear carpetas, archivos y guardarlos con el nombre exacto

- **Cómo se leen las rutas con barras:** cuando veas nombres como `css/style.css` o `corpus/naval/005-barco.caso`,
  la barra inclinada `/` significa que el archivo va **adentro de una subcarpeta**. Por ejemplo, para `css/style.css`,
  primero creás la carpeta `css` y adentro guardás el archivo `style.css`.
- **Cómo crear carpetas:** podés crearlas haciendo clic derecho en tu explorador de archivos («Nueva carpeta») o
  desde la terminal escribiendo `mkdir nombre-carpeta` y presionando Enter.
- **Extensiones de archivo y nombres exactos:** cada archivo de código termina en un punto y su tipo (`.html`,
  `.css`, `.js`, `.json`, `.caso`, `.oracle`, `.requisito`). El nombre tiene que ser exactamente el indicado en
  la guía, con mayúsculas y minúsculas respetadas.
- *Cuidado en Windows con las extensiones ocultas:* por defecto, Windows oculta las extensiones. En el Explorador
  de archivos andá a la pestaña *Ver* (o *Ver* -> *Mostrar*) y marcá la casilla **«Extensiones de nombre de archivo»**.
  Si usás el Bloc de Notas para guardar un archivo, en la ventana de «Guardar como» seleccioná en el menú *Tipo:*
  **«Todos los archivos (*.*)»** antes de guardar. Si dejás «Documentos de texto (*.txt)», Windows le va a agregar
  `.txt` al final (por ejemplo `index.html.txt`) y el juego no va a andar.

### Cómo se leen los bloques de esta guía

En cada misión vas a ver estos tipos de bloques:

- **Bloque rotulado `bash`:** son comandos para la terminal. Copiás el texto del recuadro, lo
  pegás adentro de tu terminal y presionás Enter. Si el bloque tiene varias líneas, podés pegarlas juntas o escribirlas
  de a una.
- **Bloque rotulado con una ruta, como `css/style.css`:** indica código que tenés que guardar. Abrís tu editor de
  texto, copiás todo el contenido del bloque, lo pegás y lo guardás con el nombre y la ruta que figuran en el encabezado.
- **Bloque «lo que tenés que ver»:** muestra la salida esperada de la terminal; no lo copies como comando.
- **Bloque «así tiene que quedar tu carpeta»:** muestra dónde va cada archivo. Comparalo con tus carpetas;
  las líneas y ramificaciones son un dibujo, no texto para pegar en un archivo.
- **«Si ves otra cosa»:** si en tu pantalla aparece un mensaje de error o algo distinto a la salida esperada, este
  apartado te explica qué pasó y cómo destrabarlo.

## Paso 1 · Preparar la carpeta

<!-- juego {"tipo": "mision", "n": 1, "objetivo": "Instalar Oracle, crear el proyecto y ver tu primer SIN MEDICIÓN.", "xp": 50, "logro": "enrolado", "sprite": "ancla"} -->

Oracle se instala una sola vez. Con Python 3.11+ y `uv` ya instalados en tu computadora (como comprobamos
en «Antes de empezar»), abrí tu terminal y ejecutá este bloque de comandos. Podés copiarlos y pegarlos juntos,
o escribir cada línea presionando Enter:
- `uv tool install oracle-metalenguaje` descarga e instala la herramienta Oracle en tu sistema.
- `oracle init batalla-naval` crea una carpeta nueva llamada `batalla-naval` en el lugar donde esté parada tu terminal (en tu carpeta de usuario).
- `cd batalla-naval` te mete adentro de esa carpeta (`cd` significa *change directory*, cambiar directorio) para que todos los comandos siguientes se ejecuten allí.
- `oracle test` corre una primera revisión del proyecto recién nacido.

```bash paso
uv tool install oracle-metalenguaje
oracle init batalla-naval
cd batalla-naval
oracle test
```


<!-- juego {"tipo": "predecir", "id": "p1", "pregunta": "Recién creado: sin reglas y sin casos. ¿Qué dice `oracle test`?", "opciones": ["VERDE", "ROJO", "SIN MEDICIÓN"], "correcta": "SIN MEDICIÓN", "explica": "Sin reglas no hay nada que medir, y Oracle no llama verde a lo que no midió."} -->

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

```text arbol
batalla-naval/
├── catalogos/
├── corpus/
├── diferencial/
├── relaciones/
└── oracle.json
```

**Lo que tenés que ver.** En la terminal vas a ver varias líneas técnicas que terminan en `VEREDICTO: SIN MEDICIÓN`.
No te asustes por las líneas que dicen «salteado» ni por la «advertencia: proyecto vacío»: como el proyecto recién
empieza y todavía no tiene ninguna regla, es exactamente lo que tiene que pasar.
Antes pueden aparecer mensajes de instalación de `uv`. En «Proyecto Oracle inicializado», tu terminal
muestra la ruta completa de tu carpeta; acá la abreviamos como `batalla-naval`.

**Si ves otra cosa.** Si dice `oracle: command not found` (orden no encontrada), ejecutá
`uv tool update-shell` para agregar la carpeta de herramientas al `PATH` (la lista de carpetas donde el sistema
busca programas ejecutables). Cerrá la terminal y abrí una nueva. Si todavía no se creó `batalla-naval`,
volvé a ejecutar `oracle init batalla-naval`; después ejecutá `cd batalla-naval` y `oracle test`.
Si la carpeta ya existe, entrá con `cd batalla-naval` y ejecutá `oracle test` sin repetir la creación.

<details>
<summary>¿Por qué dice «sin medición» y no «verde»?</summary>

Porque todavía no hay ninguna regla. Un verde sin reglas diría «está todo bien» sin haber mirado nada.
Oracle prefiere decir lo que pasó: no midió.

</details>

Una cosa más antes de seguir. Un **catálogo** es la carpeta donde se organizan todas las reglas de tu proyecto.
Al crearlo, `oracle init` deja activado el **catálogo base**: una colección de reglas internas de Oracle sobre tus
propias reglas. Son muy exigentes (piden unidades declaradas y evidencia observada de partidas reales) y las vamos a
encender al final de la guía. Por ahora, las apagamos para avanzar paso a paso.

Para apagarlas vamos a modificar `oracle.json`. Un archivo **JSON** es un formato de texto estándar que guarda datos
organizados entre llaves `{}` con nombres y valores legibles. (En proyectos avanzados, si una regla falla pero no la
podés arreglar ya, también podés declararla en **sombra** en este archivo: una excepción temporal con fecha límite que
avisa del problema sin voltear la corrida completa; por ahora sólo apagamos el catálogo base cambiando su valor a `false`).

Buscá el archivo `oracle.json` adentro de la carpeta `batalla-naval`, abrilo con tu editor de texto (o Bloc de Notas),
reemplazá todo su contenido por este bloque tal cual y guardalo:

```json archivo=oracle.json incluir=ejemplo/batalla-naval/oracle.json
```


## Paso 2 · El tablero

<!-- juego {"tipo": "mision", "n": 2, "objetivo": "Ver la cabecera y los paneles del juego en el navegador.", "xp": 30, "sprite": "barco"} -->

Un juego en el navegador se compone de tres cosas: **HTML** (la estructura y el contenido que hay en la pantalla),
**CSS** (los colores, tamaños y cómo se ve) y **JavaScript** (qué pasa cuando hacés clic o interactuás). Empezamos
creando los dos primeros archivos en tu carpeta `batalla-naval`.

Abrí el desplegable que sigue, copiá todo el código, pegalo en un archivo nuevo en tu editor y guardalo en la
carpeta principal `batalla-naval` con el nombre exacto `index.html` (si usás el Bloc de Notas, acordate de poner en
Tipo: «Todos los archivos (*.*)» para que no termine guardado como `index.html.txt`):

<details>
<summary>Ver el archivo index.html</summary>

```html archivo=index.html incluir=ejemplo/batalla-naval/index.html
```


</details>

Ahora creá los estilos visuales. Adentro de la carpeta `batalla-naval`, creá una subcarpeta llamada `css`. Después
abrí el siguiente desplegable, copiá el código y guardalo adentro de esa carpeta `css` con el nombre `style.css`
(la ruta completa te tiene que quedar `css/style.css`):

<details>
<summary>Ver el archivo css/style.css</summary>

```css archivo=css/style.css incluir=ejemplo/batalla-naval/css/style.css
```


</details>

Abrí tu explorador de archivos, andá a tu carpeta `batalla-naval` y hacé doble clic sobre `index.html` para abrirlo
en tu navegador web (también podés arrastrarlo a una pestaña de Chrome, Firefox o Edge, o escribir en tu terminal
`start index.html` en Windows, `open index.html` en Mac o `xdg-open index.html` en Linux).

**Lo que tenés que ver.** Vas a ver la cabecera con el título del juego y los paneles oscuros vacíos, **sin tableros
todavía**: los tableros y las cuadrículas los dibuja el código de JavaScript que agregamos en el próximo paso. Es normal
que todavía no se pueda jugar.

**Si ves otra cosa.** Si el navegador te muestra el código fuente escrito en texto plano en vez de la página diseñada,
revisá que el archivo se llame `index.html` y no `index.html.txt`. Si al hacerle doble clic no se abre tu navegador,
hacé clic derecho en `index.html`, elegí «Abrir con» y seleccioná tu navegador web habitual.

## Paso 3 · El juego

<!-- juego {"tipo": "mision", "n": 3, "objetivo": "Jugar una partida entera contra la computadora.", "xp": 40, "sprite": "barco"} -->

Adentro de la carpeta `batalla-naval`, creá una carpeta nueva llamada `js`. Ahí adentro vas a guardar los cuatro
archivos de JavaScript que le dan vida al juego: el sonido (`audio.js`), el registro de lo que pasa (`trace.js`), el
motor con las reglas de la batalla (`engine.js`) y la interfaz visual que dibuja los tableros (`ui.js`).

Abrí el desplegable que sigue. Vas a encontrar cuatro bloques de código separados: copiá el contenido de cada bloque
y guardalo en su propio archivo adentro de la subcarpeta `js/` respetando el nombre exacto de cada cabecera
(`js/audio.js`, `js/trace.js`, `js/engine.js` y `js/ui.js`):

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

```text arbol
batalla-naval/
├── catalogos/
├── corpus/
├── css/
│   └── style.css
├── diferencial/
├── js/
│   ├── audio.js
│   ├── engine.js
│   ├── trace.js
│   └── ui.js
├── relaciones/
├── index.html
└── oracle.json
```
Volvé a la pestaña de tu navegador donde abriste `index.html` y recargá la página (presionando la tecla **F5** o
haciendo clic en el botón de la flechita circular). Ahora sí se juega: vas a ver aparecer dos tableros cuadriculados
con letras y números listos para la batalla. Colocá tus barcos (o usá el botón de despliegue automático) y hacé clic
en las casillas del tablero rival para dispararle a la computadora.

**Si ves otra cosa.** Si la página queda en blanco o los tableros no aparecen, hacé clic derecho en cualquier lugar
vacío de la página, elegí **«Inspeccionar»** y hacé clic en la pestaña **«Consola»** (en la mayoría de los teclados
también podés abrirla con la tecla **F12**). Si ves mensajes en letras rojas que avisan que falta un archivo (*404 Not
Found*), revisá tu explorador de carpetas: adentro de `batalla-naval/js` tienen que quedar exactamente los cuatro
archivos con sus nombres bien guardados: `audio.js`, `trace.js`, `engine.js` y `ui.js`.

<p class="pregunta">**Pensalo.** El juego anda. ¿Eso quiere decir que cumple las reglas?</p>

<details>
<summary>Ver la respuesta</summary>

No. Quiere decir que anda. Jugando una vez no sabés si un barco puede quedar fuera del tablero, si dos
barcos se pueden pisar, si los turnos alternan siempre o si un «¡impacto!» tenía un barco abajo. En programación,
los **tests** son programas automáticos diseñados para verificar si otra aplicación anda bien o tiene fallas. Y si
le pedís al mismo modelo que escribió el juego que también escriba los tests, los tests van a confirmar
lo que el modelo ya creía.

</details>

## Paso 4 · Que el juego cuente lo que pasó

<!-- juego {"tipo": "mision", "n": 4, "objetivo": "Entender qué anota el juego: hechos, no opiniones.", "xp": 60, "sprite": "hoja"} -->

<p class="pregunta">**Pensalo.** Para juzgar un disparo después de la partida, ¿qué tendría que haber anotado el juego?</p>

<details>
<summary>Ver la respuesta</summary>

El turno, quién tiró, a quién, en qué casilla, y si el juego lo dio por impacto. Para juzgar si ese
impacto era verdad, también dónde estaba cada barco. Y para juzgar el final, quién ganó y con cuántos
impactos.

</details>

Esa es la idea central de Oracle: **el juego no se juzga a sí mismo, cuenta lo que pasó.** El archivo
`js/trace.js`, que ya guardaste, no opina sobre quién tiene razón: anota los acontecimientos en **filas planas**
(listas simples de datos directos, como los renglones de una planilla de cálculo sin texto decorativo).
En la base de hechos, cada tabla de eventos se llama **relación**, y cada columna o dato puntual dentro de la fila se
llama **campo**:

| Relación | Una fila por… | Campos |
|---|---|---|
| `celda_barco` | cada casilla ocupada por un barco | `id`, `jugador`, `barco_id`, `segmento_idx`, `fila`, `columna` |
| `tiro` | cada disparo | `turno`, `tirador`, `receptor`, `fila`, `columna`, `es_impacto`, `hundio_barco`, `barco_hundido` |
| `partida` | el final | `estado`, `ganador`, `perdedor`, `turno_final`, `total_tiros`, `impactos_ganador`, `impactos_perdedor` |

Durante la partida o al terminarla, mirá abajo a la derecha en la pantalla del juego: vas a ver un botón que dice
**«⚖ Auditoría & Traza Oracle»**. Al hacerle clic se abre un panel lateral con un botón para descargar esas filas
como un archivo llamado `hechos_partida.json`.

El siguiente recuadro es únicamente una muestra para que veas qué aspecto tiene por dentro un renglón de ese archivo
de registro en formato JSON (no hace falta que lo copies en ningún lado):

```json
{"turno": 0, "tirador": "jugador", "receptor": "cpu", "fila": 2, "columna": 3, "es_impacto": false, "hundio_barco": false, "barco_hundido": "ninguno"}
```


**Si trabajás con un modelo de inteligencia artificial** (como ChatGPT o Claude), pedíselo con esta indicación textual:
«agregá un registro que anote cada casilla de barco, cada tiro y el resultado final en filas planas, y que lo descargue
como JSON». Y **desconfiá** si en vez de anotar los hechos puros, el registro anota conclusiones («partida válida: sí»):
eso ya es opinión del juego sobre sí mismo, no un hecho objetivo.

<!-- juego {"tipo": "elegir", "id": "hecho", "titulo": "Hecho u opinión", "xp": 30, "logro": "cronista", "pregunta": "El modelo te propone tres filas para el registro. ¿Cuál es un hecho que Oracle puede juzgar?", "opciones": [{"texto": "{\"partida_valida\": true}", "codigo": true, "ok": false, "porque": "Es una conclusión: el juego se juzga a sí mismo. Si está mal, esta fila también."}, {"texto": "{\"turno\": 7, \"tirador\": \"cpu\", \"fila\": 4, \"columna\": 2, \"es_impacto\": true}", "codigo": true, "ok": true, "porque": "Es un hecho: qué pasó y dónde. Una regla puede cruzarlo con dónde estaban los barcos y decir si el impacto era verdad."}, {"texto": "{\"reglas_cumplidas\": 11}", "codigo": true, "ok": false, "porque": "Es un resultado, no un hecho: ¿qué reglas, medidas cómo? Oracle necesita lo que pasó para contarlo él."}]} -->

## Paso 5 · La primera regla, empezando por el caso rojo

<!-- juego {"tipo": "mision", "n": 5, "objetivo": "Escribir el caso rojo, después la regla, y romperla en el tablero.", "xp": 100, "logro": "primer_rojo", "sprite": "bandera"} -->

La regla más simple: **ningún barco fuera del tablero de 10 por 10.**

<p class="pregunta">**Pensalo.** Antes de escribir la regla: ¿qué partida tendría que ponerla roja?</p>

<details>
<summary>Ver la respuesta</summary>

Una con un barco en una casilla que no existe: por ejemplo, en la fila 10 (las filas van de 0 a 9).
Escribir primero ese ejemplo te obliga a decir qué es un defecto antes de escribir cómo buscarlo.

</details>

En Oracle, una partida de prueba armada para comprobar si las reglas detectan defectos se llama **caso**. La colección
de casos se guarda en una carpeta llamada **corpus** (del latín: cuerpo o conjunto de documentos de prueba). Guardalo
en `corpus/naval/`. Como `oracle init` todavía no creó esa carpeta ni `catalogos/naval/` (donde van a ir las reglas),
crealas ahora: en tu explorador de archivos, abrí `corpus` y creá adentro una carpeta `naval`; después abrí
`catalogos` y creá allí otra carpeta `naval`. También podés ejecutar `mkdir corpus/naval` y luego
`mkdir catalogos/naval` en la terminal; las dos carpetas padre ya existen.

Adentro de `corpus/naval/`, creá un archivo nuevo, pegá el contenido de este bloque y guardalo con el nombre exacto
`005-barco-fila-desbordada.caso` (en el Bloc de Notas seleccioná Tipo: «Todos los archivos (*.*)» para que no le sume
`.txt` al final):

```oracle archivo=corpus/naval/005-barco-fila-desbordada.caso incluir=ejemplo/batalla-naval/corpus/naval/005-barco-fila-desbordada.caso
```


Volvé a la ventana de la terminal (comprobando que sigas adentro de la carpeta `batalla-naval`), escribí `oracle test` y presioná Enter:

```bash paso
oracle test
```


<!-- juego {"tipo": "predecir", "id": "p2", "pregunta": "Hay un caso que reclama una regla que todavía no escribiste. ¿Qué dice `oracle test`?", "opciones": ["VERDE", "ROJO", "SIN MEDICIÓN"], "correcta": "ROJO", "explica": "El caso nombra una medida que el catálogo no tiene, y la aceptación falla."} -->

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 1 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 0 medidas · 0 macros · 1 casos · 0 relaciones

catálogo: 0 medidas · corpus: 1 casos


defectos que se pusieron rojos: 0 · verdes correctos: 0 · sin evidencia esperada: 0 · huecos declarados: 0

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


**Lo que tenés que ver.** Tenés que ver que la terminal muestra una cruz y dice `VEREDICTO: ROJO (falló: aceptación)`.
No te asustes: es exactamente lo que buscamos. El caso reclama una regla llamada `naval.barcos_dentro_del_tablero` que
todavía no escribimos. En Oracle, cuando una prueba detecta un problema o falta una regla requerida, el veredicto es rojo.

**Si ves otra cosa.** Si la terminal te arroja un error de sintaxis o dice que no encuentra el archivo, revisá que esté
guardado adentro de `corpus/naval/` con el nombre exacto `005-barco-fila-desbordada.caso` sin ninguna extensión `.txt` agregada.

Rojo, y está bien: el caso reclama una regla que todavía no existe. Ahora sí, la regla. En Oracle, a cada regla formal
obligatoria la llamamos **medida**, porque mide con precisión matemática un aspecto de los hechos. Adentro de la
carpeta `catalogos/naval/`, creá un archivo nuevo, pegá este bloque y guardalo con el nombre exacto
`naval.barcos_dentro_del_tablero.oracle`:

```oracle archivo=catalogos/naval/naval.barcos_dentro_del_tablero.oracle incluir=ejemplo/batalla-naval/catalogos/naval/naval.barcos_dentro_del_tablero.oracle
```


Línea por línea: `ninguno` dice que **no tiene que haber ninguna** fila que ofenda; `de celda_barco c` elige qué tabla
mirar; `donde` dice cuáles son las casillas que ofenden; `umbral <= 0` fija el **umbral** (el límite máximo de faltas
toleradas, en este caso cero infracciones permitidas); `segun contrato` y `porque` fundamentan el motivo de esa
exigencia; y `alcance` declara abiertamente **qué cosas no mira** esta regla.

Oracle no acepta variantes de estilo ni discusiones estéticas: cada regla se escribe de **una sola manera oficial**,
la que escribe su impresor automático. Si la escribe un modelo, `oracle formatear` la pone en esa forma única antes de
medir nada. Para que el programa acomode los espacios y sangrías de tus archivos, escribí en la terminal:

```bash paso
oracle formatear . --escribir
```


```text salida
catalogos/naval/naval.barcos_dentro_del_tablero.oracle: ya tiene forma única
corpus/naval/005-barco-fila-desbordada.caso: ya tiene forma única
```

```text arbol
batalla-naval/
├── catalogos/
│   └── naval/
│       └── naval.barcos_dentro_del_tablero.oracle
├── corpus/
│   └── naval/
│       └── 005-barco-fila-desbordada.caso
├── css/
│   └── style.css
├── diferencial/
├── js/
│   ├── audio.js
│   ├── engine.js
│   ├── trace.js
│   └── ui.js
├── relaciones/
├── index.html
└── oracle.json
```

El punto `.` le indica que formatee los archivos de la carpeta actual, y `--escribir` guarda los cambios directamente.

<!-- juego {"tipo": "elegir", "id": "forma", "titulo": "Una sola forma de escribir", "xp": 30, "pregunta": "El modelo te devuelve la regla con la línea del `donde` escrita de tres maneras. ¿Cuál carga Oracle?", "opciones": [{"texto": "donde c.fila<0 o c.fila>9 o c.columna<0 o c.columna>9", "codigo": true, "ok": false, "porque": "Se lee igual, pero no es el texto que escribe el impresor: sin espacios alrededor del `<` queda fuera de la forma única y no carga. `oracle formatear` lo arregla."}, {"texto": "donde c.fila < 0 o c.fila > 9 o c.columna < 0 o c.columna > 9", "codigo": true, "ok": true, "porque": "Es exactamente lo que escribe el impresor. En Oracle cada regla se escribe de una sola manera, como el código Go con gofmt."}, {"texto": "donde c.fila < 0  o c.fila > 9 o c.columna < 0 o c.columna > 9", "codigo": true, "ok": false, "porque": "Hay dos espacios antes de la primera `o`. Un espacio de más no es estilo: es otro texto, y Oracle lo rechaza con el diff y el comando que lo corrige."}]} -->

<p class="pregunta">**Pensalo.** ¿Qué no está mirando esta regla?</p>

<details>
<summary>Ver la respuesta</summary>

Lo dice su `alcance`: no mira si dos barcos se pisan ni si un barco es una línea continua. Un verde de
esta regla no promete eso. Por eso el `alcance` es obligatorio: un verde que no dice qué dejó sin
mirar se lee como «está todo bien».

</details>

<!-- juego {"tipo": "tablero", "id": "t5", "proyecto": "ejemplo/batalla-naval", "medida": "naval.barcos_dentro_del_tablero", "titulo": "Rompé la regla", "xp": 60, "logro": "cartografo", "inicial": [[9, 4], [10, 4]], "consigna": "Así queda el caso 005: un barco que asoma por la fila 10. Tocá casillas para mover la flota, también en el borde que no existe, y mirá qué filas se vuelven testigos. Reto: poné la regla roja con cada una de sus cuatro condiciones."} -->

Ahora que ya tenés el caso y la regla, volvé a ejecutar las pruebas en la terminal:

```bash paso
oracle test
```


<!-- juego {"tipo": "predecir", "id": "p3", "pregunta": "Ya está la regla y el caso rojo sale rojo. ¿Ahora sí verde?", "opciones": ["VERDE", "ROJO"], "correcta": "ROJO", "explica": "El caso anda, pero sobreviven mutantes: versiones debilitadas de la regla que tu único caso no nota."} -->

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 1 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 1 casos · 0 relaciones

catálogo: 1 medidas · corpus: 1 casos

  ROJO  005-barco-fila-desbordada              naval.barcos_dentro_del_tablero  (valor 1)

defectos que se pusieron rojos: 1 · verdes correctos: 0 · sin evidencia esperada: 0 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 1 defectos en rojo, 0 sin evidencia esperada, 0 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 18 · murieron 10 · sobrevivieron 8
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 10 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
  respaldo real: 0 de 10 muertos los mata al menos un caso observado; 10 sólo los sostiene evidencia construida, generada, sin procedencia o diferencial
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


**Lo que tenés que ver.** Tenés que ver que el resultado sigue siendo `VEREDICTO: ROJO`, pero ahora por `falló: mutación`.
¡Vas muy bien! Esto te avisa que la regla está cargada y el caso rojo fue detectado, pero Oracle te advierte que la regla
todavía es tan fácil de engañar que no pasa los controles de robustez.

## Paso 6 · Un caso rojo no alcanza: la mutación

<!-- juego {"tipo": "mision", "n": 6, "objetivo": "Que ningún mutante de la regla del tablero sobreviva.", "xp": 120, "sprite": "mutante"} -->

Todavía rojo, pero por otra razón: **sobreviven mutantes**. Para comprobar si tus casos de prueba son de verdad
rigurosos, Oracle le hace trampitas a tu regla a propósito: le afloja el **umbral** (acepta faltas que no debería),
invierte los signos de comparación (cambia un `<` por un `>=`) o le quita los filtros `donde`. A cada una de esas
versiones adulteradas la llama **mutante**, y se fija si tus casos de prueba son capaces de detectar la trampa.

<p class="pregunta">**Pensalo.** Si Oracle le quita el `donde` a la regla, pasa a contar todas las casillas. Tu único caso sigue saliendo rojo. ¿Qué caso haría falta para que se note?</p>

<details>
<summary>Ver la respuesta</summary>

Uno **verde**: una partida con todos los barcos dentro, que la regla sin filtro pondría roja. Y conviene
que esté en el borde (fila 9), para que también se note si alguien corre el límite.

</details>

<!-- juego {"tipo": "cazamutantes", "id": "c6", "proyecto": "ejemplo/batalla-naval", "medida": "naval.barcos_dentro_del_tablero", "titulo": "Cacería de mutantes", "xp": 80, "logro": "cazamutantes", "activos": ["005-barco-fila-desbordada"], "consigna": "Estos son los mutantes reales que Oracle genera para tu regla. Empezás con el caso 005. Sumá casos hasta que no quede ninguno vivo: ¿cuántos hacen falta, y cuál mata a cada uno?"} -->

Creá un archivo nuevo adentro de `corpus/naval/`, pegá este bloque y guardalo con el nombre exacto `006-barco-en-borde.caso`:

```oracle archivo=corpus/naval/006-barco-en-borde.caso incluir=ejemplo/batalla-naval/corpus/naval/006-barco-en-borde.caso
```


Volvé a correr las pruebas en la terminal:

```bash paso
oracle test
```


<!-- juego {"tipo": "predecir", "id": "p4", "pregunta": "Agregaste el caso verde del borde. ¿Verde?", "opciones": ["VERDE", "ROJO"], "correcta": "ROJO", "explica": "Murieron más mutantes, pero todavía viven los que tocan las otras tres condiciones del donde."} -->

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 2 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 2 casos · 0 relaciones

catálogo: 1 medidas · corpus: 2 casos

  ROJO  005-barco-fila-desbordada              naval.barcos_dentro_del_tablero  (valor 1)
  verde 006-barco-en-borde                     naval.barcos_dentro_del_tablero  (valor 0)

defectos que se pusieron rojos: 1 · verdes correctos: 1 · sin evidencia esperada: 0 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 1 defectos en rojo, 0 sin evidencia esperada, 1 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 18 · murieron 14 · sobrevivieron 4
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 14 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
  respaldo real: 0 de 14 muertos los mata al menos un caso observado; 14 sólo los sostiene evidencia construida, generada, sin procedencia o diferencial
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


**Lo que tenés que ver.** Murieron 14 mutantes y ahora sobreviven sólo 4. El reporte te avisa qué trampas no fueron
descubiertas todavía: para tapar esos huecos vas a necesitar agregar tanto partidas válidas (casos verdes) como partidas
con errores justo en los bordes del tablero (casos rojos).

Quedan mutantes vivos porque la regla vigila cuatro condiciones (fila menor que 0, fila mayor que 9, columna menor que 0,
columna mayor que 9) y tu caso rojo sólo probaba una de ellas. Creá tres archivos separados adentro de `corpus/naval/`:
guardá el primer bloque como `026-barco-columna-desbordada.caso`, el segundo como `027-barco-fila-negativa.caso` y el
tercero como `028-barco-columna-negativa.caso`:

```oracle archivo=corpus/naval/026-barco-columna-desbordada.caso incluir=ejemplo/batalla-naval/corpus/naval/026-barco-columna-desbordada.caso
```


```oracle archivo=corpus/naval/027-barco-fila-negativa.caso incluir=ejemplo/batalla-naval/corpus/naval/027-barco-fila-negativa.caso
```


```oracle archivo=corpus/naval/028-barco-columna-negativa.caso incluir=ejemplo/batalla-naval/corpus/naval/028-barco-columna-negativa.caso
```


Ahora corré de nuevo `oracle test` en la terminal:

```bash paso
oracle test
```


<!-- juego {"tipo": "predecir", "id": "p5", "pregunta": "Un caso rojo por cada condición. ¿Y ahora?", "opciones": ["VERDE", "ROJO"], "correcta": "VERDE", "explica": "Cada forma de debilitar la regla la nota algún caso."} -->

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 5 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 5 casos · 0 relaciones

catálogo: 1 medidas · corpus: 5 casos

  ROJO  005-barco-fila-desbordada              naval.barcos_dentro_del_tablero  (valor 1)
  verde 006-barco-en-borde                     naval.barcos_dentro_del_tablero  (valor 0)
  ROJO  026-barco-columna-desbordada           naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  027-barco-fila-negativa                naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  028-barco-columna-negativa             naval.barcos_dentro_del_tablero  (valor 1)

defectos que se pusieron rojos: 4 · verdes correctos: 1 · sin evidencia esperada: 0 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 4 defectos en rojo, 0 sin evidencia esperada, 1 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 18 · murieron 18 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 18 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
  respaldo real: 0 de 18 muertos los mata al menos un caso observado; 18 sólo los sostiene evidencia construida, generada, sin procedencia o diferencial
detecciones evaluadas (mutante × caso): 90

sin políticas meta activas — se informa sólo el resultado operativo

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: VERDE (todas las verificaciones aplicables en regla)
```


**Lo que tenés que ver.** Tenés que ver que la última línea de la terminal dice `VEREDICTO: VERDE (todas las verificaciones aplicables en regla)`.
**Verde, y ahora el verde significa algo**: tus cinco casos atraparon todas las trampas posibles, murieron los 18 mutantes
y la regla del tablero quedó completamente asegurada.

**Si ves otra cosa.** Si todavía dice `VEREDICTO: ROJO`, leé las líneas de la terminal: te van a indicar qué mutante
sigue vivo o qué caso no se ejecutó. Revisá que los nombres de los tres archivos nuevos en `corpus/naval/` coincidan letra
por letra.

## Paso 7 · Diez reglas más, y la trampa de los pocos casos

<!-- juego {"tipo": "mision", "n": 7, "objetivo": "Once reglas, cada una con casos que la puedan romper.", "xp": 150, "logro": "flota", "sprite": "barco"} -->

El juego tiene más reglas para ser una batalla naval completa. Adentro de la carpeta `catalogos/naval/`, vas a crear diez
archivos de texto por separado. Abrí el desplegable que sigue, copiá el contenido de cada bloque y guardalo con el nombre
exacto que figura en el encabezado de cada uno (`catalogos/naval/...`):

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

Tres reglas para mirar con calma, porque cada una enseña una palabra clave de consulta del lenguaje:

- `naval.alternancia_turnos` usa `unir` para cruzar cada tiro con el tiro siguiente y comprueba que los números de turno sean correlativos: `t2.turno == t1.turno + 1` (en programación, el doble igual `==` significa 'es igual a').
- `naval.flota_reglamentaria` usa `agrupar` para contar cuántas casillas de barco tiene cada jugador y exige `requiere celda_barco`: si el juego no envió ningún barco en el registro, la regla no sale verde, sale **sin evidencia**. Cero barcos no es una flota correcta, es un registro roto.
- `naval.veracidad_impacto_positivo` usa `sin` para detectar contradicciones: busca los disparos reportados como acierto **sin** ningún barco rival en esa misma casilla.

Con el juego original venían sólo dos casos de prueba para la regla de disparos. Creá dos archivos nuevos en `corpus/naval/`: guardá el primer bloque como `001-tiro-fuera-de-tablero.caso` y el segundo como `002-tiro-valido.caso`:

```oracle archivo=corpus/naval/001-tiro-fuera-de-tablero.caso incluir=ejemplo/batalla-naval/corpus/naval/001-tiro-fuera-de-tablero.caso
```


```oracle archivo=corpus/naval/002-tiro-valido.caso incluir=ejemplo/batalla-naval/corpus/naval/002-tiro-valido.caso
```

```text arbol
batalla-naval/
├── catalogos/
│   └── naval/
│       ├── naval.alternancia_turnos.oracle
│       ├── naval.barcos_dentro_del_tablero.oracle
│       ├── naval.barcos_sin_solapamiento.oracle
│       ├── naval.fin_de_juego_sin_tiros_posteriores.oracle
│       ├── naval.flota_reglamentaria.oracle
│       ├── naval.ganador_legitimo.oracle
│       ├── naval.tiros_dentro_del_tablero.oracle
│       ├── naval.tiros_sin_repeticion.oracle
│       ├── naval.turnos_sin_huecos.oracle
│       ├── naval.veracidad_impacto_negativo.oracle
│       └── naval.veracidad_impacto_positivo.oracle
├── corpus/
│   └── naval/
│       ├── 001-tiro-fuera-de-tablero.caso
│       ├── 002-tiro-valido.caso
│       ├── 005-barco-fila-desbordada.caso
│       ├── 006-barco-en-borde.caso
│       ├── 026-barco-columna-desbordada.caso
│       ├── 027-barco-fila-negativa.caso
│       └── 028-barco-columna-negativa.caso
├── css/
│   └── style.css
├── diferencial/
├── js/
│   ├── audio.js
│   ├── engine.js
│   ├── trace.js
│   └── ui.js
├── relaciones/
├── index.html
└── oracle.json
```

<p class="pregunta">**Pensalo.** Once reglas y siete casos, casi todos de dos reglas. ¿Qué tendría que decir `oracle test`?</p>

<details>
<summary>Ver la respuesta</summary>

Que la mayoría de las reglas no las prueba nadie. Una regla sin casos que puedan romperla es
decoración: puede estar mal escrita y dar verde siempre, y nunca te vas a enterar.

</details>

Volvé a ejecutar las pruebas en la terminal:

```bash paso
oracle test
```


<!-- juego {"tipo": "predecir", "id": "p6", "pregunta": "Once reglas y siete casos. ¿Qué dice `oracle test`?", "opciones": ["VERDE", "ROJO", "SIN MEDICIÓN"], "correcta": "ROJO", "explica": "Nueve reglas no tienen ni un caso: MEDIDAS SIN CASOS, y la mutación tampoco cierra."} -->

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

SINTAXIS OK · 11 medidas · 0 macros · 7 casos · 0 relaciones

catálogo: 11 medidas · corpus: 7 casos

  ROJO  001-tiro-fuera-de-tablero              naval.tiros_dentro_del_tablero  (valor 1)
  verde 002-tiro-valido                        naval.tiros_dentro_del_tablero  (valor 0)
  ROJO  005-barco-fila-desbordada              naval.barcos_dentro_del_tablero  (valor 1)
  verde 006-barco-en-borde                     naval.barcos_dentro_del_tablero  (valor 0)
  ROJO  026-barco-columna-desbordada           naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  027-barco-fila-negativa                naval.barcos_dentro_del_tablero  (valor 1)
  ROJO  028-barco-columna-negativa             naval.barcos_dentro_del_tablero  (valor 1)

defectos que se pusieron rojos: 5 · verdes correctos: 2 · sin evidencia esperada: 0 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 5 defectos en rojo, 0 sin evidencia esperada, 2 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 36 · murieron 32 · sobrevivieron 4
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 32 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
  respaldo real: 0 de 32 muertos los mata al menos un caso observado; 32 sólo los sostiene evidencia construida, generada, sin procedencia o diferencial
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


**Lo que tenés que ver.** La terminal te muestra `MEDIDAS SIN CASOS`: te lista nueve medidas que no tienen pruebas y
frena el avance. Es una protección esencial: una regla sin pruebas no te da ninguna garantía.

Para blindar las once reglas necesitamos 26 casos más en `corpus/naval/`: para cada regla, al menos uno que la ponga
roja cerca del borde y uno verde. Abrí el desplegable que sigue y creá adentro de `corpus/naval/` cada uno de estos
26 archivos con el nombre exacto de su encabezado:

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

Volvé a correr las pruebas en la terminal:

```bash paso
oracle test
```


<!-- juego {"tipo": "predecir", "id": "p7", "pregunta": "Con todos los casos que faltan. ¿Verde?", "opciones": ["VERDE", "ROJO"], "correcta": "VERDE", "explica": "Once reglas y ningún mutante vivo."} -->

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 33 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 11 medidas · 0 macros · 33 casos · 0 relaciones

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
  SIN EVIDENCIA 029-flota-sin-celdas          naval.flota_reglamentaria  («celda_barco» vacía)
  SIN EVIDENCIA 030-sin-tiros-registrados     naval.turnos_sin_huecos  («tiro» vacía)
  verde 031-distinta-fila-igual-turno-ajeno    naval.tiros_sin_repeticion  (valor 0)
  verde 032-agua-declarada-agua                naval.veracidad_impacto_positivo  (valor 0)
  verde 033-fila-confundida-con-turno          naval.tiros_sin_repeticion  (valor 0)

defectos que se pusieron rojos: 17 · verdes correctos: 14 · sin evidencia esperada: 2 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 17 defectos en rojo, 2 sin evidencia esperada, 14 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 209 · murieron 209 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 158 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 51 rechazados por el álgebra sin evaluar
  respaldo real: 0 de 209 muertos los mata al menos un caso observado; 209 sólo los sostiene evidencia construida, generada, sin procedencia o diferencial
detecciones evaluadas (mutante × caso): 634

sin políticas meta activas — se informa sólo el resultado operativo

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: VERDE (todas las verificaciones aplicables en regla)
```


**Lo que tenés que ver.** Fijate al final de la pantalla que aparezca `VEREDICTO: VERDE (todas las verificaciones aplicables en regla)`:
eso te confirma que las once reglas y los 33 casos de prueba se ejecutaron impecablemente, y que ningún mutante quedó vivo.

**Si ves otra cosa.** Si la salida muestra `MEDIDAS SIN CASOS` o termina en `ROJO`, leé atentamente los renglones que
tienen un punto `·`: te van a marcar cuál es la medida o caso que falta o si hubo un error de tipeo en algún nombre de archivo.

## Paso 8 · Juzgar una partida de verdad

<!-- juego {"tipo": "mision", "n": 8, "objetivo": "Juzgar una partida real y leer lo que quedó sin mirar.", "xp": 120, "logro": "juez", "sprite": "ojo"} -->

Las reglas ya están probadas en el laboratorio de casos. Ahora vamos a juzgar una partida real jugada por vos:
abrí `index.html` en tu navegador, jugá una partida entera contra la computadora, abrí el panel de auditoría (abajo
a la derecha) y hacé clic en el botón para descargar `hechos_partida.json`.

El navegador web va a guardar el archivo en tu carpeta de **Descargas**. Andá a tu carpeta de Descargas, hacé clic
derecho sobre `hechos_partida.json`, elegí «Cortar», andá a tu carpeta del proyecto `batalla-naval` y poné «Pegar»
(el archivo tiene que quedar en la carpeta principal de `batalla-naval`, al lado de `oracle.json`, que es donde lo
busca el comando).

(Si todavía no jugaste o querés probar con una partida real ya lista, podés
[bajar la partida del ejemplo](https://github.com/Segtem/oracle/raw/main/ejemplo/batalla-naval/partida_real.json).
Como se descarga con el nombre `partida_real.json`, andá a Descargas, hacé clic derecho sobre el archivo, elegí
«Cambiar nombre», escribí exactamente `hechos_partida.json` y luego pegalo en tu carpeta `batalla-naval`).

Si preferís crearlo a mano en vez de descargarlo, abrí el desplegable de abajo. Es un archivo muy extenso (más de
1500 líneas) porque contiene el registro detallado de cada tiro y posición de una partida completa:

<details>
<summary>Ver la partida del ejemplo (hechos_partida.json)</summary>

```json archivo=hechos_partida.json incluir=ejemplo/batalla-naval/partida_real.json
```


</details>

En la terminal, escribí `oracle juzgar --con hechos_partida.json` y presioná Enter. El parámetro `--con` le indica
a Oracle qué archivo de hechos debe evaluar contra las once medidas del catálogo:

```bash paso
oracle juzgar --con hechos_partida.json
```


<!-- juego {"tipo": "predecir", "id": "p8", "pregunta": "Juzgás una partida jugada de verdad. ¿Qué dice?", "opciones": ["VERDE", "ROJO"], "correcta": "VERDE", "explica": "Las once reglas se cumplieron en esta partida. Mirá la lista SIN MIRAR: es la otra mitad de la respuesta."} -->

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


**Lo que tenés que ver.** Vas a ver que las once reglas tienen un tilde `✓` y dice `VEREDICTO: verde en 11 medidas`.
Abajo aparece una lista titulada `SIN MIRAR:`: **no te asustes, no son errores**. Oracle es totalmente honesto y
transparente: te avisa qué cosas comprobó y te declara abiertamente cuáles detalles del juego quedaron fuera de su
vigilancia (por ejemplo, que los barcos tengan forma recta). Esa lista no es letra chica: es la otra mitad del veredicto.

**Si ves otra cosa.** Si la terminal te dice que no encuentra el archivo `hechos_partida.json`, revisá que esté adentro
de la carpeta principal `batalla-naval` (no adentro de `corpus` ni de `js`) y que no tenga una extensión oculta como
`.json.txt`.

<p class="pregunta">**Pensalo.** Todo verde. ¿Quiere decir que el juego está bien?</p>

<details>
<summary>Ver la respuesta</summary>

Quiere decir que esas once reglas se cumplieron en esta partida. La lista `SIN MIRAR` dice lo que
ninguna regla garantiza, por ejemplo que cada barco sea una línea recta. Esa lista no es letra chica:
es la mitad de la respuesta.

</details>

Las reglas tienen nombres técnicos, pero conviene escribir también las promesas generales que querés hacer sobre el
juego. En desarrollo de software, un **requisito** es una promesa formal sobre el comportamiento que debe tener el
sistema. En Oracle, cada archivo con extensión `.requisito` dice qué prometés, qué medidas técnicas lo comprueban y
qué parte sigue sin medir.

Primero, creá una carpeta llamada `requisitos` adentro de `batalla-naval` (en la terminal podés escribir `mkdir requisitos`
o crearla desde tu explorador de archivos). Después abrí el desplegable de abajo y creá adentro de esa carpeta estos seis
archivos con extensión `.requisito`: cinco agrupan las once medidas y el sexto deja visible una deuda técnica:

<details>
<summary>Ver las promesas del juego</summary>

```oracle archivo=requisitos/naval.flota.requisito incluir=ejemplo/batalla-naval/requisitos/naval.flota.requisito
```


```oracle archivo=requisitos/naval.disparos.requisito incluir=ejemplo/batalla-naval/requisitos/naval.disparos.requisito
```


```oracle archivo=requisitos/naval.turnos.requisito incluir=ejemplo/batalla-naval/requisitos/naval.turnos.requisito
```


```oracle archivo=requisitos/naval.impactos.requisito incluir=ejemplo/batalla-naval/requisitos/naval.impactos.requisito
```


```oracle archivo=requisitos/naval.final.requisito incluir=ejemplo/batalla-naval/requisitos/naval.final.requisito
```


```oracle archivo=requisitos/naval.barcos_rectos.requisito incluir=ejemplo/batalla-naval/requisitos/naval.barcos_rectos.requisito
```


</details>

<p class="pregunta">**Pensalo.** ¿Tener una medida para una promesa quiere decir que se cumplió en esta partida?</p>

<details>
<summary>Ver la respuesta</summary>

Todavía no. `oracle cobertura` muestra qué promesas tienen medidas; con `--con` juzga los hechos de
esta partida y dice cuáles se cumplieron. Una promesa puede quedar sólo en parte medida.

</details>

En Oracle, la **cobertura** muestra cuántas de tus promesas o requisitos están respaldados por reglas y cuáles se cumplieron efectivamente en tu partida. Ejecutá estos dos comandos en la terminal:

```bash paso
oracle cobertura
oracle cobertura --con hechos_partida.json
```


```text salida
· naval.barcos_rectos   SIN MEDIR: todavía no hay una medida para comprobar la forma de cada barco
✓ naval.disparos   naval.tiros_dentro_del_tablero, naval.tiros_sin_repeticion
✓ naval.final   naval.fin_de_juego_sin_tiros_posteriores, naval.ganador_legitimo
◐ naval.flota   naval.barcos_dentro_del_tablero, naval.barcos_sin_solapamiento, naval.flota_reglamentaria · SIN MEDIR: la forma recta y continua de cada barco
✓ naval.impactos   naval.veracidad_impacto_negativo, naval.veracidad_impacto_positivo
✓ naval.turnos   naval.alternancia_turnos, naval.turnos_sin_huecos

6 requisitos: 4 medidos · 1 en parte · 1 sin medir · 0 con medidas inexistentes
· naval.barcos_rectos   sin medir · SIN MEDIR: todavía no hay una medida para comprobar la forma de cada barco
✓ naval.disparos   cumple · naval.tiros_dentro_del_tablero cumple, naval.tiros_sin_repeticion cumple
✓ naval.final   cumple · naval.fin_de_juego_sin_tiros_posteriores cumple, naval.ganador_legitimo cumple
◐ naval.flota   cumple · naval.barcos_dentro_del_tablero cumple, naval.barcos_sin_solapamiento cumple, naval.flota_reglamentaria cumple · SIN MEDIR: la forma recta y continua de cada barco
✓ naval.impactos   cumple · naval.veracidad_impacto_negativo cumple, naval.veracidad_impacto_positivo cumple
✓ naval.turnos   cumple · naval.alternancia_turnos cumple, naval.turnos_sin_huecos cumple

6 requisitos: 5 se cumplen (1 sólo en lo medido) · 0 no se cumplen · 0 sin juicio · 1 sin medir · 0 con medidas inexistentes
```


**Lo que tenés que ver.** La terminal te muestra el estado de tus promesas con tres símbolos claros:
- El tilde `✓` indica un requisito completamente vigilado que se cumplió en esta partida.
- El círculo medio lleno `◐` significa que se cumple sólo en parte (la flota tiene 17 casillas, pero todavía no sabemos si los barcos son rectos).
- El punto `·` señala un requisito que está `sin medir`, sin ninguna regla que lo controle. Oracle no lo disfraza de verde.

Si más adelante tus promesas vienen de una especificación formal de requisitos (como OpenSpec), vas a poder usar `oracle requisito importar` para crear esos archivos automáticamente. Acá los escribimos a mano para que veas qué significa cada línea.

<p class="pregunta">**Pensalo.** ¿Y si el juego se olvidara de anotar los tiros?</p>

<details>
<summary>Ver la respuesta</summary>

Las reglas de tiros no tendrían nada que mirar. Un sistema descuidado las daría por buenas; Oracle las
lista aparte, en `NO SE APLICARON`, y falla la corrida completa. Si ejecutás sólo una parte del
catálogo a propósito, `--parcial` permite esa omisión. Probalo:

</details>

Guardá este archivo como `sin-tiros.json`: contiene la misma partida, con `celda_barco` y
`partida`, pero sin la relación `tiro`.

```json archivo=sin-tiros.json incluir=ejemplo/batalla-naval/sin-tiros.json
```

```bash paso
oracle juzgar --con sin-tiros.json
```


<!-- juego {"tipo": "predecir", "id": "p9", "pregunta": "El archivo no trae la relación `tiro`. ¿Qué pasa?", "opciones": ["VERDE", "ROJO", "NO SE APLICARON"], "correcta": "NO SE APLICARON", "explica": "Siete reglas no tenían qué mirar. Oracle no las da por buenas: las lista aparte y falla la corrida."} -->

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


**Lo que tenés que ver.** Tenés que ver que Oracle se niega a dar un aprobado a ciegas. Siete reglas no tenían qué
mirar porque faltaban los datos de los disparos, y aparecen listadas bajo `NO SE APLICARON`. Como faltaba información
esencial, la corrida falla. (Si alguna vez querés evaluar deliberadamente una corrida parcial sin que falle, podés
agregarle la opción `--parcial` al comando).

Si una regla sale roja en una partida, el veredicto trae los **testigos**: son las filas exactas de datos que cometieron
la infracción (mostrándote en qué turno o coordenada ocurrió la trampa). Con esa evidencia puntual le volvés a hablar
al modelo de lenguaje con total precisión: «el tiro del turno 14 se marcó como impacto y no había barco en esa casilla;
corregilo».

## Paso 9 · Qué le falta a este juego

<!-- juego {"tipo": "mision", "n": 9, "objetivo": "Diseñar, en tu cabeza, la regla que le falta al juego.", "xp": 100, "logro": "disenador", "sprite": "hoja"} -->

Antes de agregar otra regla, guardá esta versión en **Git**. Git es un sistema de control de versiones que saca fotos
del estado de tus archivos: a cada punto de control guardado lo llama **commit**. El comando `oracle cambios` compara
las reglas actuales con ese punto guardado en Git para vigilar que nadie haya aflojado una exigencia por error.

Vamos a aflojar a propósito el límite de una regla: permitir un disparo repetido a la misma casilla (pasando el umbral
de `<= 0` a `<= 1`), sin cambiar la frase `porque` que defiende el límite original.

<p class="pregunta">**Pensalo.** Si los casos siguen pasando, ¿cómo te enterás de que alguien aflojó esa promesa?</p>

<details>
<summary>Ver la respuesta</summary>

Git guarda el antes; `oracle cambios` revisa el después. Un límite más permisivo con el mismo
`porque` es un error aunque el resto del catálogo siga igual.

</details>

Copiá y pegá estas líneas en la terminal para inicializar Git (`git init`), registrar los archivos (`git add .`)
y guardar el commit base (`git commit -m base`). Después vas a cambiar la regla con tu editor:

```bash paso
git init
git add .
git commit -m base
```


```text salida
```

Git confirma la creación del repositorio y el commit; la rama y el hash varían según tu máquina.
Si Git pide nombre y correo, configurá `git config user.name "Tu nombre"` y
`git config user.email "tu@correo"`, y repetí el commit.

Editá `catalogos/naval/naval.tiros_sin_repeticion.oracle`: reemplazá el archivo entero por este bloque, que permite un tiro repetido.

```oracle archivo=catalogos/naval/naval.tiros_sin_repeticion.oracle incluir=docs/archivos-guia/naval.tiros_sin_repeticion_aflojada.oracle
```

En Git, **HEAD** es el nombre que recibe tu último commit guardado (la versión de referencia de tu proyecto). Ahora
ejecutá `oracle cambios` para comparar las reglas modificadas contra HEAD:

```bash paso falla
oracle cambios
```


```text salida
cambios desde HEAD:
✗ umbral aflojado sin nueva defensa  naval.tiros_sin_repeticion  <= 0 → <= 1  (el `porque` no cambió)

1 errores · 0 avisos
```


**Lo que tenés que ver.** Oracle señala `naval.tiros_sin_repeticion` y el paso de `<= 0` a `<= 1`: detecta que aflojaste
el umbral de la regla pero el texto explicativo `porque` sigue defendiendo que no haya disparos repetidos.

**Si ves otra cosa.** Si la terminal dice `git: command not found`, asegurate de haber instalado Git como indicamos en
«Antes de empezar» y de reiniciar la terminal para que reconozca el comando.

Para devolver el umbral a cero, podés abrir `catalogos/naval/naval.tiros_sin_repeticion.oracle` en tu editor y volver a
escribir `umbral <= 0 segun contrato`, o ejecutar este bloque en la terminal:

```oracle archivo=catalogos/naval/naval.tiros_sin_repeticion.oracle incluir=docs/archivos-guia/naval.tiros_sin_repeticion_restaurada.oracle
```

```bash paso
oracle cambios
```


```text salida
cambios desde HEAD:
  nada se aflojó

0 errores · 0 avisos
```


**Lo que tenés que ver.** Al correrlo, tenés que ver que dice `cambios desde HEAD: nada se aflojó` y `0 errores`.

El ejemplo también incluye una explicación y un **script** (un programa que se ejecuta de corrido para hacer pruebas
automáticas) para probar infracciones deliberadas. Copialos para tener la carpeta completa adentro de `batalla-naval`:
un archivo de texto explicativo en formato Markdown (`README.md`) y el script de Python (`verificar_oraculo.py`).
El recorrido de arriba no necesita ejecutar ese script.

<details>
<summary>Ver los archivos complementarios</summary>

```markdown archivo=README.md incluir=ejemplo/batalla-naval/README.md
```


```python archivo=verificar_oraculo.py incluir=ejemplo/batalla-naval/verificar_oraculo.py
```


</details>

```text arbol
batalla-naval/
├── catalogos/
│   └── naval/
│       ├── naval.alternancia_turnos.oracle
│       ├── naval.barcos_dentro_del_tablero.oracle
│       ├── naval.barcos_sin_solapamiento.oracle
│       ├── naval.fin_de_juego_sin_tiros_posteriores.oracle
│       ├── naval.flota_reglamentaria.oracle
│       ├── naval.ganador_legitimo.oracle
│       ├── naval.tiros_dentro_del_tablero.oracle
│       ├── naval.tiros_sin_repeticion.oracle
│       ├── naval.turnos_sin_huecos.oracle
│       ├── naval.veracidad_impacto_negativo.oracle
│       └── naval.veracidad_impacto_positivo.oracle
├── corpus/
│   └── naval/
│       ├── 001-tiro-fuera-de-tablero.caso
│       ├── 002-tiro-valido.caso
│       ├── 003-mismo-tirador-seguido.caso
│       ├── 004-tiradores-alternos.caso
│       ├── 005-barco-fila-desbordada.caso
│       ├── 006-barco-en-borde.caso
│       ├── 007-barcos-superpuestos.caso
│       ├── 008-barcos-separados.caso
│       ├── 009-tiro-despues-del-final.caso
│       ├── 010-tiro-en-turno-final.caso
│       ├── 011-flota-de-dieciseis.caso
│       ├── 012-flota-de-diecisiete.caso
│       ├── 013-ganador-con-dieciseis-impactos.caso
│       ├── 014-ganador-con-diecisiete-impactos.caso
│       ├── 015-tiro-repetido.caso
│       ├── 016-tiros-distintos.caso
│       ├── 017-turno-saltado.caso
│       ├── 018-turnos-contiguos.caso
│       ├── 019-barco-reportado-como-agua.caso
│       ├── 020-agua-reportada-como-agua.caso
│       ├── 021-impacto-fantasma.caso
│       ├── 022-impacto-real.caso
│       ├── 023-columna-desbordada.caso
│       ├── 024-fila-negativa.caso
│       ├── 025-columna-negativa.caso
│       ├── 026-barco-columna-desbordada.caso
│       ├── 027-barco-fila-negativa.caso
│       ├── 028-barco-columna-negativa.caso
│       ├── 029-flota-sin-celdas.caso
│       ├── 030-sin-tiros-registrados.caso
│       ├── 031-distinta-fila-igual-turno-ajeno.caso
│       ├── 032-agua-declarada-agua.caso
│       └── 033-fila-confundida-con-turno.caso
├── css/
│   └── style.css
├── diferencial/
├── js/
│   ├── audio.js
│   ├── engine.js
│   ├── trace.js
│   └── ui.js
├── relaciones/
├── requisitos/
│   ├── naval.barcos_rectos.requisito
│   ├── naval.disparos.requisito
│   ├── naval.final.requisito
│   ├── naval.flota.requisito
│   ├── naval.impactos.requisito
│   └── naval.turnos.requisito
├── README.md
├── hechos_partida.json
├── index.html
├── oracle.json
├── sin-tiros.json
└── verificar_oraculo.py
```
Para volver a abrir el juego cuando quieras, podés hacerle doble clic a `index.html` desde tu explorador de carpetas
(o escribir `start index.html` en Windows, `open index.html` en Mac o `xdg-open index.html` en Linux).

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

Y el catálogo base que apagaste en el paso 1: volvé a abrir el archivo `oracle.json` en tu editor de texto, cambiá
`"catalogo_base": false` por `"catalogo_base": true`, guardalo y corré `oracle test` en la terminal. Te va a pedir lo
que falta para que estas reglas valgan fuera de esta guía: declarar las unidades de los campos y sostener cada regla
con partidas **observadas** (jugadas por personas reales), no sólo con casos construidos.

## Si trabajás con un modelo de inteligencia artificial

1. **Pedile que el juego cuente lo que pasa**, en filas planas y formato JSON, sin opiniones ni conclusiones propias.
2. **No le pidas las reglas y el código en la misma pasada.** Escribí o revisá vos las reglas de forma independiente.
3. **Pedile primero el caso rojo**, y recién después la regla. Si te da una regla sin caso que la pruebe, desconfiá.
4. **Leé el `alcance`** de cada regla: es lo que el veredicto verde no te promete.
5. **Cuando algo salga rojo, pasale los testigos exactos** (los turnos o casillas que ofendieron), no una descripción vaga.
6. **Si te dice «ya está todo verificado», preguntale qué mutantes sobrevivieron** y qué dice la lista `SIN MIRAR`.

Después de esto, podés consultar la documentación en el sitio web de Oracle: [La primera medida real](13-primer-valor.md)
muestra el mismo recorrido con menos explicación, y [Escribir una medida](03-escribir-una-medida.md) es la referencia
completa del lenguaje.

<!-- juego {"tipo": "cierre"} -->
