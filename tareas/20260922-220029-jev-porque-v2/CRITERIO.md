# Criterio fijado para la segunda corrida

Fecha: 2026-09-22. Fijado antes del nuevo juicio de Claude y de cualquier llamada a Jev.
Se evalúa lo que dice `porque` en relación con la tubería, el resumen y el umbral.
No se completa la defensa con conocimientos externos ni con la etiqueta `segun`.
La pregunta evalúa si hay una justificación textual, no si su afirmación es verdadera.

## P1 — origen del valor (`porque_origen`)

¿La defensa permite derivar el valor del umbral, mediante una regla explícita,
una fuente o un cálculo, en lugar de limitarse a decir por qué la regla importa?

Sí: vincula lo que se cuenta o resume con el límite. Para un conteo de infracciones
con umbral cero, una exigencia explícita de universalidad o de ninguna excepción
justifica cero aunque no escriba el numeral. No basta describir un perjuicio.
No: sólo expresa importancia, conveniencia, un perjuicio o una decisión circular.
`segun: contrato` por sí solo no convierte una defensa en sí.

Ejemplos sí (inventados, ajenos al lote):

- Conteo de entregas sin firma, <= 0: «Todas las entregas deben estar firmadas;
  ninguna entrega sin firma es admisible». La regla universal deriva cero.
- Máximo de días de retención, <= 30: «El contrato fija un máximo de 30 días de
  retención». Identifica una fuente del valor, aunque no explique su elección.

Ejemplos no:

- Conteo de entregas sin firma, <= 0: «Las firmas ayudan a resolver disputas».
  Explica importancia, no cuántas ausencias se permiten.
- Máximo de días de retención, <= 30: «Treinta días es lo razonable».
  Repite el valor sin fuente, regla ni cálculo.

## P2 — elección entre valores vecinos (`porque_vecino`)

Para este umbral distinto de cero, ¿la defensa explica por qué se eligió ese
valor y no uno vecino, mediante una restricción o un criterio de elección?

Sólo se pregunta si el límite numérico es distinto de cero. Para cero se registra
`no_aplica`; no se convierte en no ni se envía como pregunta binaria al modelo.
Sí: aporta un criterio que distingue ese corte de otro cercano; no necesita
nombrar literalmente los dos vecinos. No: sólo repite un valor o una autoridad,
o justifica la importancia de tener algún límite.

Ejemplos sí:

- Máximo de días de retención, <= 30: «Las reclamaciones se reciben hasta el día
  30 inclusive: borrar antes pierde respaldo y conservar después no tiene uso
  permitido; elegimos el último día necesario».
- Conteo de conexiones simultáneas, <= 8: «Cada conexión reserva 1 GiB y hay
  8 GiB disponibles; nueve exceden memoria y siete desperdician una plaza».

Ejemplos no:

- Máximo de días de retención, <= 30: «El contrato fija 30 días».
  Da procedencia (P1 sí), pero no el criterio que eligió ese valor (P2 no).
- Conteo de conexiones simultáneas, <= 8: «Hay que evitar la saturación».
  No distingue ocho de siete ni de nueve.

## Contexto y registro

La tubería canónica `desde` define la fuente y los pasos de selección; `resumen`
define el agregado que se compara con `umbral`. `campo` accede a una columna,
`lit` a un literal. Leer esas formas junto con la prosa, sin ejecutar ni corregirla.
Cada respuesta de Claude llevará sí/no (booleano), una justificación breve y una
cita de `porque` (puede ser vacía si falta defensa). En P2 no aplicable, usar null.
No deducir una respuesta de otra: P1 sí no obliga a P2 sí.

Las preguntas de alcance no se repiten: esta segunda prueba aísla las dos preguntas
nuevas de `porque`. Los controles conservan ambos textos degradados de la primera
corrida, aunque ahora sólo se juzga `porque`.
