# Postmortem: batalla naval de agy con y sin Oracle

Tarea: **20260919-134424-naval-pm**. Investigación: 2026-09-19. Estado: evidencia de producto analizada; reconstrucción de sesión bloqueada por falta de logs. La tarea queda abierta para revisión de Claude.

## Hallazgo

La versión sin Oracle contiene más interfaz y opciones de interacción. La versión con Oracle **no midió reglas de batalla naval**: guardó un caso sobre sintaxis de archivos, sin sensor del juego ni medidas propias. Con el checkout actual, su `oracle test --rapido` da verde aunque se destruya el JavaScript; el test completo da rojo por mutación. Son resultados sobre el corpus, no certificación del producto.

Esto sostiene dos mejoras: hacer explícito qué validó el comando y ofrecer una entrada corta que conecte una regla del producto con evidencia real. **No sostiene que Oracle haya consumido el 60 % de la atención ni causado por sí solo la diferencia de producto.** No se recuperó la conversación original. El postmortem examina condiciones y mensajes del sistema, sin atribuir culpas o intenciones a agy.

## Fuentes, método y límites

Fuentes primarias locales:

- `/home/workstation/Dev/lab/batalla_naval_test/`: las dos carpetas y `el_porque_de_agy.md`. Inventario completo con SHA-256 en [inventario.json](naval-pm/inventario.json).
- `batalla_naval_con_oracle/tareas/20260918-190831-juego-batalla/TAREA.md`: alcance y nota histórica; `oracle.json` y `corpus/juego/001-flota-completa.caso`: integración efectiva.
- [README de Oracle](../README.md), especialmente instalación, tracker y `juzgar`; `/home/workstation/TestOracleEjemplo/GUIA22.md`, secciones 1–14. Son las copias disponibles hoy, no prueba de qué leyó agy.
- [Implementación de test](../tools/cli.py), `cmd_test`, y [medida heredada](../catalogos/proceso/proceso.sintaxis_valida_tras_edicion_masiva.oracle).

Reproducción con Node **v24.21.0**, Oracle **0.27.0**, álgebra **0.8**, sintaxis **0.6**, checkout `63a47a1cdb0d03dfe6a44288556064af8e06492d`. No se conoce la versión instalada por agy. La guía se declara comprobada con 0.25.2 el 2026-09-16. **Las salidas actuales no se presentan como logs de 2026-09-18.**

No se escribió en el laboratorio. [reproducir_oracle.py](naval-pm/reproducir_oracle.py) usa una copia temporal. [probar_juegos.cjs](naval-pm/probar_juegos.cjs) lee los scripts y expone sus cierres sólo en memoria: simula DOM y audio, conserva la lógica de colocación/disparos y controla la cola de temporizadores. No es una prueba visual, de audio real, accesibilidad ni compatibilidad de navegadores. Los conteos de funciones son textuales, no complejidad ni calidad.

Reejecución desde Oracle:

```bash
python3 estudios/naval-pm/reproducir_oracle.py
node estudios/naval-pm/probar_juegos.cjs
```

Ambos aceptan como argumento la ruta raíz del laboratorio. Resultados conservados: [Oracle](naval-pm/oracle-resultados.txt) y [juegos](naval-pm/juegos-resultados.txt). `node --check` terminó con código 0 para los tres archivos JS originales; eso no valida HTML, CSS ni jugabilidad.

## Qué se construyó, medido

Bytes exactos, sin comprimir; líneas incluidas las vacías:

| Archivo | Con Oracle: bytes / líneas | Sin Oracle: bytes / líneas |
|---|---:|---:|
| `index.html` | 5.471 / 151 | 10.115 / 235 |
| `styles.css` / `style.css` | 13.032 / 691 | 20.993 / 1.027 |
| `game.js` | 27.858 / 826 | 39.513 / 1.025 |
| `audio.js` | integrado en game.js | 9.186 / 308 |
| README del juego | no hay | 3.848 / 89 |
| Total ejecutable HTML/CSS/JS | **46.361 / 1.668** | **79.807 / 2.595** |
| Archivos del juego, incluido README | 3 / 46.361 bytes | 5 / 83.655 bytes |
| Archivos adicionales Oracle | 4 / 2.497 bytes | 0 |
| Total de archivos regulares | **7 / 48.858 bytes** | **5 / 83.655 bytes** |

Con Oracle: 23 declaraciones `function nombre(...)`. Sin Oracle: 41, más 13 métodos en la clase de audio (incluyen constructor y auxiliares); no se cuentan callbacks flecha o IIFE anónimas como funciones nombradas. El juego sin Oracle tiene **1,72 veces** los bytes ejecutables, o 1,80 si se suma sólo su README. “Casi el doble de código” es una aproximación dependiente del denominador; “el doble de completo” no es una medida definida.

| Capacidad, identificada en código | Con Oracle | Sin Oracle |
|---|---|---|
| Tableros y flota | 10×10, 5/4/3/3/2 | igual |
| Colocación | clic, botón/R, aleatoria, vaciar flota | además arrastrar/soltar, recoger un barco y clic derecho |
| Previsualización válida/inválida | sí (`handlePlayerCellHover`) | sí (`handlePlayerCellMouseEnter`) |
| Audio procedural | 6 tipos en `playSound`: fire/hit/miss/sunk/victory/defeat | módulo separado; 8 efectos incluyendo sonar y clic; `playNoiseBurst` es auxiliar |
| Radar | presentación CSS | animación Canvas en `initRadarAnimation` |
| Estado de buques | vivo/hundido | además indicadores por segmento dañado |
| IA | damero y cola de vecinos | damero, cola y deducción de orientación |
| Estadísticas y final | disparos, aciertos, precisión, hundidos, victoria/derrota | también, con paneles de ayuda y HUD más detallado |
| Medición Oracle de reglas del juego | **ninguna** | ninguna |

El conjunto de requisitos conservado en la tarea de agy se implementa en gran parte como producto. Su compromiso de “Modelado de medidas y reglas de verificación en catálogos” no se materializa. No hay prompt original para comprobar que ambas corridas tuvieron exactamente el mismo alcance o presupuesto.

### Reglas comprobadas y límites de corrección

En ambos scripts, el arnés verificó:

- 100 despliegues aleatorios con semilla determinista, cada uno con cinco buques de longitudes 5/4/3/3/2 y 17 celdas ocupadas; rechazos en borde horizontal/vertical y ante superposición.
- Adyacencia permitida. La separación de una celda es una variante, no un incumplimiento demostrado del encargo conservado.
- Disparo bloqueado fuera del turno del jugador; repetición sobre un impacto no suma otro disparo; un único impacto no hunde al portaaviones.
- Hundimiento de los cinco barcos con 17 impactos distintos y transición a victoria; una corrida de IA por versión llega a derrota del jugador sin repetir casillas.

Por lectura, las dos variantes ceden turno también al acertar; el enemigo permanece oculto salvo impactos/agua/hundidos. No se impone la variante de repetir turno tras acierto. Los ensayos no son prueba exhaustiva de IA ni de todas las partidas. Ambos colocadores tienen un tope de intentos (500/1.000 por barco) sin garantía posterior de éxito: no fallaron en las 100 muestras.

Dos defectos reproducidos ponen límite a “completo”:

1. **Sin Oracle**, `initGame` llama cada vez a `setupEventListeners`. Tras dos inicializaciones, el botón de rotación tiene dos manejadores: un clic hace H→V→H. También se vuelve a iniciar el radar por lectura del código; el arnés no mide su costo gráfico.
2. **Con Oracle**, `initGame` no cancela el `setTimeout(enemyTurn, ...)` pendiente, y `enemyTurn` sólo comprueba `PHASE`, no `currentTurn`. Un callback de la partida anterior dispara durante el turno del jugador en una nueva partida ya iniciada. Se reprodujo con temporizadores controlados, no con latencias humanas.

No se corrigieron esos juegos ni se abrieron tareas de implementación en Oracle para código del laboratorio: son evidencia de que el verde conservado no cubría comportamiento y de que más UX no implica ausencia de fallos.

## Qué verificó Oracle y qué decía su verde

`catalogos/` y `diferencial/` están vacíos, pero **el proyecto no está vacío**: hay un caso y `catalogo_base: true`. En la reproducción carga **39 medidas heredadas efectivas**. Confundir ausencia de medidas propias con ausencia de cualquier medida escondería el mecanismo real.

El caso `001-flota-completa` lleva un nombre naval pero su título es “Archivos del juego Batalla Naval con sintaxis válida”. Declara `archivo(ruta, sintaxis_valida)` con tres filas `true`, y referencia `proceso.sintaxis_valida_tras_edicion_masiva`. La medida cuenta filas cuyo booleano es `false` y exige valor ≤ 0. Con tres `true`, obtiene 0. **No carga game.js ni ejecuta el comando de origen.** `SINTAXIS OK` dentro de `oracle test` se refiere a la representación de archivos Oracle, no al parser JavaScript o HTML.

La procedencia dice `observada`, repo `batalla-naval-html5`, commit `a1b2c3d`, comando `node -c game.js`. No hay historial Git del juego ni salida adjunta que permitan verificar ese commit. Su aspecto de ejemplo no prueba que sea inventado. Aun si ese comando se ejecutó, sólo justifica parseo de JS, no los booleanos de HTML y CSS. La trazabilidad aprobada es estructural; no autenticación del origen ni reejecución de la observación.

| Experimento actual, siempre en copia | Resultado |
|---|---|
| Caso y código conservados, `test --rapido` | exit 0; verde; mutación omitida explícitamente |
| Caso y código conservados, `test` | exit 1; rojo por mutación: 9 mutantes, 5 muertos, **4 sobrevivientes** |
| Destruir sintaxis de game.js, conservar caso, `test --rapido` | exit 0, mismo verde |
| Cambiar la fila game.js a `false`, manteniendo etiqueta verde_correcto | exit 1; falla `meta.el_caso_se_pone_como_debe` |
| Quitar también el único caso (0 propias, 0 casos, 0 fixtures) | exit 0; `VEREDICTO: VERDE (proyecto vacío: 0 medidas, 0 casos)` |

El primer verde exacto es `VEREDICTO: VERDE (se salteó: mutación de medidas (--rapido))`. El test completo deja vivos `aflojar_umbral`, `aflojar_cota_superior`, `vaciar_tuberia_si_cero_aprueba` y `agregado:3.1:contar→suma(0)`. Por tanto la explicación de agy no puede usarse como evidencia de “todas las pruebas formales” o mutación aprobada. No conocemos la salida histórica literal.

El comportamiento sobre un caso guardado es coherente con un verificador de medidas: prueba qué hace la medida con esas filas. El problema es **leer ese resultado como prueba del estado actual del juego**. Un catálogo lleno tampoco resolvería por sí solo la ausencia de un sensor y evidencia pertinente.

## Secuencia histórica: qué sabemos y qué falta

Se inspeccionaron los nombres de logs en `~/.gemini/antigravity-cli/log/`, búsquedas recursivas de nombres de sesiones y búsquedas de contenido (también binario, `rg -a`) en `~/.gemini` por batalla naval y el ID del caso. No hubo coincidencias. El índice SQLite `conversation_summaries.db`, abierto con `mode=ro&immutable=1`, tampoco contiene una candidata naval: la sesión con modificación UTC del 18 encontrada se titula “Instalación de Unity CLI”. Un índice de resúmenes no reemplaza un transcript. No se copian aquí conversaciones ajenas.

Los logs disponibles saltan de archivos fechados 17 a 19 de septiembre. La explicación señala rutas `/c/holamundo/batalla_naval` y `/taller/batalla-naval`; el README del segundo juego conserva `/home/administradortt/taller/batalla-naval`. **Es una pista para recuperar otra máquina/cuenta**, no prueba del lugar o momento de ejecución. Los mtimes de las copias del laboratorio no son duración de trabajo.

| Paso atribuido por agy | Corroboración disponible | Comando, errores y costo histórico |
|---|---|---|
| Instalar con `uv tool install` | sólo su explicación | no verificables; versión desconocida |
| `oracle init` | estructura y oracle.json compatibles | invocación exacta y tiempo desconocidos |
| `oracle tarea init/nueva`, redactar tarea | tarea `20260918-190831-juego-batalla` | ID compatible con 19:08:31 UTC; no prueba del inicio de sesión |
| Construir juego | tres archivos de producto | orden de ediciones, turnos y reintentos desconocidos |
| Redactar caso | archivo conservado, fecha 2026-09-18 | no se conoce su primera versión |
| `node -c game.js` | declarado en origen del caso | ejecución y salida histórica no conservadas |
| `oracle test --rapido`, corregir esquemas | explicación y nota dicen verde | no hay comandos fallidos ni mensajes para reconstruir depuración |
| `oracle tarea anotar` | nota fechada **19:12:02 UTC** | texto afirma implementación y caso verde |
| Segunda versión, sin Oracle | cinco archivos y explicación | sin cronología verificable |

Entre la hora codificada en el ID de tarea y la nota hay **3 min 31 s**. Es un intervalo entre dos marcas documentales, no duración del desarrollo ni tiempo dedicado a Oracle. No existe denominador de turnos o llamadas para calcular porcentajes. La secuencia de arriba sigue el relato, no un orden reconstruido desde logs.

Contraste con `el_porque_de_agy.md`:

- **~46 KB y ~83 KB:** aproximadamente reproducibles contando el README sólo del segundo lado.
- **Mayor riqueza de UX:** sostenida por funciones específicas; audio y preview de colisiones ya existían con Oracle. Ocho efectos identificables en el módulo sin Oracle si se incluye clic, no siete.
- **60 % de atención/llamadas y 100 % de capacidad en producto:** no verificables; atención no es directamente observable aun teniendo logs. Habría que contar llamadas clasificadas y aclarar las mixtas.
- **Trazabilidad excelente/pruebas formales integradas:** no sostenidas como garantía del juego; hay un caso estático de sintaxis y ausencia de medidas de dominio.
- **Oracle obliga a todo ese ritual y explica causalmente la diferencia:** hipótesis plausible de fricción, no resultado de un experimento controlado. Faltan prompts, orden confirmado, tokens, modelo efectivo, límites y transcript de ambas corridas.

## Por qué pudo ocurrir: condiciones del sistema

**El éxito elegido quedó desconectado del objetivo.** La propia tarea de agy habla de “metodología y validación” y enumera init, tracker y test. En el artefacto final, esos rastros existen mientras falta la medición naval prometida. Es evidencia de una integración centrada en proceso; no de que agy recibiera una obligación específica en el prompt original.

**El README permite una lectura demasiado amplia del arranque.** En instalación dice “un proyecto nuevo ya tiene quién lo juzgue” y ofrece `init → nueva → test`. Ese recorrido no muestra todavía extracción de hechos del producto y `juzgar`. La distinción existe más abajo: `juzgar --con hechos.json` y salida sin medidas aplicables. El tracker se documenta por separado y sus políticas se dicen optativas; no hay base para concluir que Oracle exige crear tareas para medir un juego.

**La guía no prescribe el ritual atribuido.** Tiene juego, relaciones, medidas navales, casos y sensor; no una secuencia obligatoria de `tarea init/nueva/anotar`. En secciones 8, 10, 12 y 14 insiste en evidencia observada, límites del verde y diferencia entre probar medidas y juzgar el juego. Incluso dice cuándo basta un `assert`. Eso contradice la idea de que enseñe deliberadamente a certificar producto con un caso de sintaxis. Pero sus **1.171 líneas** y el recorrido de cuatro medidas/19 casos son un tutorial amplio: no una entrada mínima para quien quiere construir primero. El cierre del ciclo observado recién tiene sección propia después del primer veredicto y de mutación. No sabemos si agy la leyó.

**Hay dos problemas distintos de presentación.** El proyecto realmente vacío recibe VERDE explícito por decisión de `cmd_test` para no comenzar en rojo; el proyecto naval recibe verde con un caso y medidas heredadas. Convertir sólo “catalogos vacío” en rojo no arregla el segundo y rechazaría usos legítimos de medidas heredadas. Recomendación: estado visible “sin medición” para el vacío, resumen del alcance validado para el no vacío, y política explícita para CI. No declarar que no se midió nada cuando sí se comprobó un corpus, ni que se midió producto por contar medidas propias.

La causa inmediata demostrable es la **ausencia del vínculo regla naval → sensor → evidencia → medida aplicada**. La fricción de aprendizaje y la prominencia del verde son contribuyentes plausibles. Atribuir una pérdida cuantitativa de productividad a Oracle requiere recuperar ambas sesiones y un diseño comparativo; este caso solo no permite esa causalidad.

## Tareas derivadas y próximo paso

Se crearon únicamente dos tareas respaldadas por las reproducciones:

1. [20260919-135054-test-alcance](../tareas/20260919-135054-test-alcance/TAREA.md): distinguir corpus validado, omisiones y ausencia de medición; cubrir vacío y catálogo heredado sin imponer medidas propias.
2. [20260919-135054-primer-valor](../tareas/20260919-135054-primer-valor/TAREA.md): camino corto a una medida observable del producto, con tracker opcional, procedencia reproducible y diferencia entre `test` y `juzgar`.

No se proponen cambios generales de lenguaje, prohibir Oracle para juegos ni enforcement de commits supuestamente falsos a partir de un solo identificador no verificable. Los fallos de los juegos sirven como ejemplos posibles para el recorrido, sin modificar el laboratorio.

**Próximo paso de esta investigación:** Claude revisa el informe y las dos tareas; recuperar/exportar las sesiones originales del 18 desde la máquina/cuenta de origen para completar la cronología pendiente. Con los logs: listar llamadas y errores, clasificar instalación/documentación/tracker/medición/producto/mixtas, publicar conteos y ventanas de tiempo sin confundirlas con atención. Hasta entonces, el punto 2 histórico queda explícitamente bloqueado y la tarea abierta.
