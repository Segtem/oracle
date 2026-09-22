# Un patrón para que un proyecto use un modelo como sensor de su prosa, sin que Oracle dependa de él

- ESTADO: ABIERTA
- PRIORIDAD: 72
- ETIQUETAS: oracle, sensores, metalenguaje, jev


## La decisión de diseño, primero

Oracle **no** va a llamar a un modelo ni a depender de una clave: hoy corre sin red y su veredicto es
reproducible, y eso es lo que lo hace creíble. Lo que puede llevar es el **patrón** para que un
proyecto lo haga por su cuenta, igual que los sensores de Unreal: el sensor vive afuera, Oracle
juzga lo que el sensor emite.

Sale de `20260922-190222-jev-prueba`: sobre `alcance`, un modelo barato acertó 15/15 y atrapó 10 de
10 controles de prosa vacía, por menos de un décimo de centavo. Hoy Oracle sólo comprueba que
`alcance` no esté **vacío**; que diga algo concreto no lo comprueba nadie.

## Qué hacer

1. **La relación declarada** `afirmacion_prosa` en `relaciones/`: `medida`, `pregunta`, `respuesta`
   (booleano), `probabilidad` (flotante, `sin_unidad`), `modelo`, `fecha`. Con su `alcance` diciendo
   qué NO ve: que la respuesta la produjo un modelo y no una persona.
2. **Una medida de ejemplo** —en `ejemplo/`, no en el catálogo que obliga a todos— que la juzgue:
   por ejemplo, ninguna medida con una afirmación adversa de alta probabilidad sobre su `alcance`.
   Con su corpus de las dos polaridades. En su `alcance`, sin vueltas: **estas filas las produjo un
   modelo probabilístico; el umbral de probabilidad es una decisión, no un hecho**.
3. **El sensor, afuera y opcional**: un script de ejemplo (`ejemplo/…/sensor_prosa.py`) que arme el
   lote desde un catálogo y llame a un modelo por HTTP, con la clave en el entorno. Que funcione con
   Jev por OpenRouter y que el proveedor sea un parámetro, no una dependencia. Reusar lo que ya
   escribió Codex en `tareas/20260922-190222-jev-prueba/`.
4. **Documentarlo** en `docs/` como lo que es: una forma de convertir prosa en hechos, con sus
   límites, y la advertencia de que un sensor probabilístico no es un juez.
5. **No tocar el catálogo que obliga**: ningún proyecto debería ponerse rojo por esto sin haberlo
   elegido.

## Cuándo entra

Cuando `jev-porque-v2` cierre, para que el patrón nazca sabiendo qué parte de la prosa se puede
delegar y cuál no. Corte candidato: 0.30.0.

## Próximo paso

Esperar a `20260922-...-jev-porque-v2`; mientras tanto, escribir la relación y el alcance de la
medida de ejemplo, que no dependen del resultado.
