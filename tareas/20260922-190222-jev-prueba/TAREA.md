# Probar Jev como sensor de Oracle: hechos sobre la prosa que ninguna medida puede juzgar

- ESTADO: ABIERTA
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

## Próximo paso

Brian: una clave de OpenRouter (y decir el tope de gasto). Con eso, Codex arma el lote, corre las
recetas y mide.

### Nota (2026-09-22 19:59:39 UTC)

2026-09-22: bloqueo levantado. La clave de OpenRouter vive en ~/.config/openrouter/key (permisos 600), la exporta ~/.config/fish/config.fish como OPENROUTER_API_KEY, y tiene tope de 5 USD mensuales (usado 0). Los agentes la leen del archivo, nunca de un archivo del proyecto, y ningún comando debe imprimir la cabecera de autorización. Ojo: había una clave vieja guardada como variable universal de fish que daba 401; se borra con set -Ue OPENROUTER_API_KEY.
