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

## Avance

- **Relación declarada (`relaciones/afirmacion_prosa.json`):**
  - Creada en formato canónico L−1 con los campos requeridos: `medida` (texto), `pregunta` (texto), `respuesta` (booleano), `probabilidad` (flotante), `modelo` (texto) y `fecha` (texto), todos `sin_unidad`.
  - Alcance explícito: declara que observa respuestas probabilísticas de un modelo (probabilidad = P(sí)) y que NO observa si la prosa es veraz ni valida el razonamiento: la respuesta la produjo un modelo probabilístico y no una persona.
- **Medida de ejemplo y su alcance (`ejemplo/catalogos/prosa/prosa.alcance_sin_afirmacion_adversa.oracle`):**
  - Creada en `ejemplo/` (con `ejemplo/oracle.json`), aislada del catálogo base para no obligar a ningún proyecto.
  - Juzga señales adversas de alta probabilidad sobre el alcance (`alcance_vacio` con P(sí) >= 0.8 o `alcance_concreto` con P(sí) <= 0.2).
  - Alcance exacto según la decisión de diseño: *«Estas filas las produjo un modelo probabilístico; el umbral de probabilidad es una decisión, no un hecho. NO juzga la verdad de la prosa ni el razonamiento del sensor, y no detecta preguntas o medidas omitidas de una relación entregada parcialmente.»*
- Estado de verificación: no se ejecutaron verificaciones en shell ni se realizaron commits en esta sesión, conforme a las restricciones operativas.

## Próximo paso

Aguardar la conclusión del experimento `jev-porque-v2` para determinar si el patrón abarca también la defensa del umbral (`porque`) o si se circunscribe a `alcance`. Con ese resultado, armar en `ejemplo/` el corpus con las dos polaridades, escribir el arnés desacoplado `sensor_prosa.py` y documentar el patrón en `docs/`.

### Nota (2026-09-22 22:16:08 UTC)

2026-09-22, revisión de Claude sobre la entrega de agy: la relación y el alcance están bien escritos, pero las dos ubicaciones estaban mal y una era seria. (1) afirmacion_prosa.json quedó en relaciones/, que son las relaciones que Oracle DISTRIBUYE a todos los proyectos: es lo mismo que hizo chocar a Jam con pieza. (2) ejemplo/oracle.json y ejemplo/catalogos/ convertían ejemplo/ —que es una carpeta de proyectos de ejemplo— en un proyecto. Todo se movió a ejemplo/sensor-prosa/, con catalogo_base en false. Además la medida se declaraba de ambito universal y pasó a del_origen: obliga a su proyecto, no a quien la herede. oracle test del ejemplo da ROJO sólo por falta de casos, que es el paso siguiente.
