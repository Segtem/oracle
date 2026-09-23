# Dieciocho de veinticinco defensas de umbral explican la regla, no el número

- ESTADO: ABIERTA
- PRIORIDAD: 78
- ETIQUETAS: oracle, prosa, deuda


## Lo medido

`20260922-220029-jev-porque-v2` (cerrada): un juez ciego —una sesión limpia, que sólo vio el criterio
y 25 registros con ids opacos— marcó **18 de 25 defensas como insuficientes**. El criterio: una
defensa sirve si permite derivar el valor del umbral (una regla universal, una fuente o un cálculo);
no sirve si sólo dice por qué la regla importa. Jev coincidió 15/15 con ese juez.

Ejemplos del propio catálogo, con lo que les falta:

- «un falso rojo enseña a ignorar el verificador» — dice el perjuicio; no dice por qué **cero**.
- «una medida que ningún caso evalúa es decoración» — está a un paso de la exigencia universal, pero
  no la enuncia.
- «comprobar que los N siguen parseando es una línea» — argumenta el costo, no el límite.

No es un problema del catálogo ajeno: **es deuda de Oracle sobre sí mismo**, y estaba invisible
porque ninguna medida puede leer prosa.

## Qué hacer

1. **Reescribir las defensas insuficientes**, una por una, agregando lo que falta: la regla universal
   de la que se sigue el cero («ninguna X es admisible»), la fuente del número, o el cálculo. Sin
   inventar: si no se puede defender el número, el que hay que revisar es el umbral, no el texto.
2. **Volver a pasar el juez** (el ciego y, si se quiere, Jev) sobre las reescritas, y anotar cuántas
   pasan. Es la manera de saber si el arreglo arregló algo.
3. **Decidir si esto se vuelve una medida** o queda como revisión periódica. Ojo: una medida que
   exija «defensa derivable» necesitaría un sensor de prosa, y eso es
   [`sensor-prosa`](../20260922-220029-sensor-prosa/TAREA.md). Mientras no exista, esto es trabajo a
   mano y está bien que lo sea.

## Próximo paso

Listar las 18 con su id real (está en `tareas/20260922-220029-jev-porque-v2/comparaciones.json`), y
redactar las propuestas para revisión de Brian.
