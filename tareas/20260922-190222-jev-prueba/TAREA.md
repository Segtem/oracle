# Probar Jev como sensor de Oracle: hechos sobre la prosa que ninguna medida puede juzgar

- ESTADO: CERRADA
- PRIORIDAD: 65
- ETIQUETAS: oracle, investigacion, sensores, jev


## De dónde sale

Brian (2026-09-22) señaló `https://openrouter.ai/labs/jev`. Existe y es de verdad: **Jev Lab**,
recetas que corren en vivo contra Jev de TypeSafe AI por OpenRouter, cada una con su código y su
resultado. Corrige lo que quedó sin confirmar en
[`20260922-185116-jev`](../20260922-185116-jev/TAREA.md): Jev **sí** está en OpenRouter, como
laboratorio y no en el listado de modelos (por eso no aparecía al consultar la API de modelos).

Lo que la página muestra, con sus propias cifras:

| receta | qué hace | cifra publicada |
|---|---|---|
| `jev/triage` | cinco preguntas de sí o no sobre 95 mensajes | 475 respuestas en 1,2 s · US$ 0,0014 |
| `jev/overseer` | cuatro comprobaciones sobre 24 llamadas a herramientas; lo riesgoso frena | 96 respuestas en 0,5 s · US$ 0,0004 |
| `jev/extract` | extrae campos eligiendo entre candidatos del texto, así no puede inventar | 12 campos en 0,6 s · US$ 0,0002 |
| `jev/compile` | Claude reescribe un pedido en prosa como preguntas de Jev | 380 respuestas en 2 s |
| `jev/feed` | una regla escrita en palabras filtra publicaciones | 40 en 0,5 s · US$ 0,0003 |

El modelo aparece como `jev-1.13`.

## La hipótesis a probar

Oracle tiene un hueco declarado desde siempre: **la máquina no puede juzgar si la prosa dice la
verdad**. `alcance` es obligatorio y se comprueba que no esté vacío; `porque` defiende un umbral y
nadie comprueba que defienda algo. Jev responde preguntas de sí o no, en lote, por milésimos de
dólar. Entonces: **Jev como sensor que emite hechos sobre la prosa, y Oracle juzgándolos como a
cualquier otro hecho.**

Ojo con la trampa: un sensor probabilístico no es un juez. Si esto entra alguna vez, la medida que
lo use tiene que declarar en su `alcance` que sus filas las produjo un modelo y con qué margen.

## La prueba, chica y falsable

1. **Sobre el catálogo del propio Oracle** (62 medidas, prosa real y pública): armar el lote de
   preguntas de sí o no por medida, por ejemplo «¿el `alcance` nombra algo concreto que la medida no
   mira?», «¿el `porque` explica por qué ESE número y no otro?», «¿el `alcance` es una promesa vacía
   del tipo “no ve todo lo demás”?».
2. **Correrlo** con `jev/triage` o `jev/compile` por OpenRouter; anotar costo, latencia y el JSON
   crudo. Hace falta una clave de OpenRouter: **es lo que hoy bloquea la tarea** (la pone Brian).
3. **Contrastar contra un juicio humano**: Brian (o Claude) responde a mano las mismas preguntas
   sobre una muestra al azar de 15 medidas, **sin ver** las respuestas de Jev. Medir el acuerdo.
4. **Cerrar el ciclo**: emitir esas respuestas como una relación (`afirmacion_prosa`: medida,
   pregunta, respuesta, probabilidad) y escribir UNA medida que las juzgue, con su corpus de las dos
   polaridades. Correr `oracle juzgar`.
5. **Escribir `estudios/JEV-COMO-SENSOR.md`** con lo medido: acuerdo, costo, latencia, y en qué se
   equivocó el modelo. Si el acuerdo es malo, ese también es el resultado y se dice.

## Qué decide la prueba

Si el acuerdo con el juicio humano es alto y barato, Oracle gana una clase de sensor que hoy no
tiene, y hay que discutir dónde entra sin romper la doctrina (una medida juzga hechos; los hechos
pueden venir de un modelo si se declara). Si es bajo, queda escrito que esa prosa no se puede
delegar, que es un resultado igual de útil.

## El juicio a ciegas ya está hecho (2026-09-22)

Claude respondió las tres preguntas sobre 15 medidas al azar (semilla 20260922) **antes** de que
existiera ninguna respuesta de Jev: `juicio-ciego-claude.json` y `muestra-jev.json`, acá al lado.

Y al hacerlo apareció un problema de diseño: **las 15 dan el mismo patrón** (sí, sí, no). La prosa
del catálogo de Oracle es pareja, así que un modelo que conteste siempre «sí, sí, no» tendría 100 %
de acuerdo sin leer nada. Un experimento sin las dos polaridades no prueba nada —es la misma regla
que Oracle le exige a cualquier medida—.

**Entonces el lote lleva controles rojos**, mezclados y sin marcar: 10 variantes deliberadamente
malas, hechas a partir de medidas reales, con el `alcance` reemplazado por una promesa vacía
(«no ve nada más», «no cubre otros casos») o el `porque` por una no-defensa («porque sí», «es lo
razonable»).
Sus respuestas esperadas son las opuestas, y quedan anotadas junto al lote antes de correrlo.

Lo que se mide entonces: acuerdo sobre las 15 reales, **y** cuántos de los 10 controles atrapa. Un
modelo que no atrape los controles no sirve para esto, por más que coincida en las reales.


### Nota (2026-09-22 19:59:39 UTC)

2026-09-22: bloqueo levantado. La clave de OpenRouter vive en ~/.config/openrouter/key (permisos 600), la exporta ~/.config/fish/config.fish como OPENROUTER_API_KEY, y tiene tope de 5 USD mensuales (usado 0). Los agentes la leen del archivo, nunca de un archivo del proyecto, y ningún comando debe imprimir la cabecera de autorización. Ojo: había una clave vieja guardada como variable universal de fish que daba 401; se borra con set -Ue OPENROUTER_API_KEY.

### Nota (2026-09-22 20:00:48 UTC)

2026-09-22: juicio a ciegas de Claude guardado (sha256 dc84bda7d7be8c00) antes de correr nada; el lote tiene que llevar 10 controles rojos con prosa deliberadamente vacía, mezclados y sin marcar.

### Nota (2026-09-22 20:08:00 UTC)

Experimento completo. Lote fijado de 62 medidas + 10 controles mixtos; 216 respuestas en 6 corridas Jev, guardadas antes de abrir el juicio ciego (hash dc84bda7d7be8c00 confirmado). Costo real por corrida: US$ 0.000151872, 0.000164136, 0.000140910, 0.000142968, 0.000137130, 0.000140028; total US$ 0.000877044, latencia secuencial 9.539 s. Acuerdo Claude 31/45 (68.9%): alcance 15/15 y 15/15; porque 1/15. Controles 10/10 completos (30/30 respuestas). No respalda adopción automática de P2. Relación afirmacion_prosa y medida aislada en proyecto-sensor; corpus 3 rojos/1 verde y aceptación OK; juzgar lote ROJO esperado con 81 señales. Evidencia, scripts, solicitudes, respuestas crudas, costos y análisis en esta carpeta; estudio en estudios/JEV-COMO-SENSOR.md. Sin commits ni credenciales en artefactos.

## Próximo paso

Experimento terminado; tarea CERRADA. Para revisar la decisión, leer `ANALISIS.md` y los desacuerdos en `comparaciones.json`: no adoptar la guarda automática de `porque` con este resultado. No quedan corridas ni implementación pendientes en esta tarea.

### Nota (2026-09-22 20:09:58 UTC)

2026-09-22, revisión de Claude: acepto el informe y agrego lo que a mí me toca. El desacuerdo de P2 no es sólo del modelo: mi juicio a ciegas fue generoso. Para los umbrales contractuales de cero, esos 'porque' defienden la REGLA («ninguna ausencia es aceptable»), no el número; yo los di por buenos y Jev pidió que el texto defienda el número. La pregunta estaba mal formulada para ese caso, y su probabilidad lo mostró: las 14 discrepancias caen entre 0,12 y 0,47, es decir que el modelo nunca afirmó 'no' con confianza, dudó. Conclusiones que me llevo: (1) para 'alcance' la señal es fuerte —15/15 en ambas preguntas y 10/10 controles— y es candidata a sensor si algún día se quiere; (2) para 'porque' no se automatiza, y antes de volver a intentarlo hay que arreglar la pregunta y mandar también la tubería de la medida, no sólo la prosa; (3) el experimento costó 0,088 centavos, así que el costo nunca va a ser el impedimento.
