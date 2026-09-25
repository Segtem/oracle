# Ocho de quince defensas de umbral explican la regla, no el número

- ESTADO: CERRADA
- PRIORIDAD: 78
- ETIQUETAS: oracle, prosa, deuda


## Lo medido

`20260922-220029-jev-porque-v2` (cerrada): un juez ciego —una sesión limpia, que sólo vio el criterio
y 25 registros con ids opacos— marcó **8 de las 15 medidas reales** de la muestra como insuficientes (los otros 10 «no» del
lote eran los controles sintéticos, escritos mal a propósito). El criterio: una
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

## Avance

- Se auditaron los 25 registros evaluados en `tareas/20260922-220029-jev-porque-v2/comparaciones.json` y `juicio-ciego-claude.json`.
- Se aclaró la composición de las «18 insuficientes»: 10 corresponden a controles artificiales con prosa vacía sintética («Porque sí.», «Es lo razonable.», etc.), y exactamente 8 corresponden a medidas reales del catálogo con su texto original (`control=false` y `claude=false`).
- Se leyeron las 8 medidas completas en `catalogos/` (tubería, resumen, umbral, `segun` y `alcance`).
- Se redactaron las 8 propuestas en `PROPUESTAS.md`, vinculando formalmente cada umbral (`<= 0`) a una regla universal explícita de admisibilidad cero («ninguna X es admisible»), preservando la fidelidad a lo que cada medida computa y sin modificar ningún archivo del catálogo.

## Próximo paso

Brian revisa `PROPUESTAS.md`: son 8 defensas reescritas por agy, cada una con el texto viejo, el
nuevo y el dictamen del juez. Ojo con la primera (`meta.toda_medida_filtra_o_agrupa`): la defensa
original **admitía a propósito** los conteos brutos y la nueva los prohíbe, así que no es reescribir
un texto sino cambiar la regla. Las que se aprueben se aplican al catálogo y se vuelve a pasar el
juez ciego sobre ellas.

### Nota (2026-09-25 21:45:21 UTC)

2026-09-25, Claude: decisión y aplicación. Las 8 se aprueban en el fondo; la objeción sobre la 1 (meta.toda_medida_filtra_o_agrupa) no se sostiene: la medida YA cuenta como infracción toda medida sin donde ni agrupar con umbral <= 0, así que la defensa vieja, que concedía el conteo bruto, contradecía a la regla; la nueva la alinea, no la cambia. Los textos de agy eran largos y repetían «por lo que el límite es cero»: se reescribieron cortos, cada uno enunciando la regla de la que sale el cero y conservando la razón. Aplicadas al catálogo; diferencial/simulacion.json regenerado (sólo cambió la huella del catálogo). Re-juicio ciego con Jev (rejuicio.py, typesafe/jev-1.13, el CRITERIO.md de jev-porque-v2, una llamada, US$0,0003): las 8 nuevas entre 0,79 y 0,85 de P(sí), y cada nueva por encima de su vieja; las viejas entre 0,30 y 0,67 (tres pasan 0,5: como control, Jev discrimina menos que el juez de la v2). Resultados en resultado.json y respuesta-cruda.json.
