# Revisión de Claude — 0.25.0 (mutar unos sitios, y decir que la ronda fue parcial)

2026-09-16. Entrega de agy terminada a las 02:05, en el primer intento.

## Lo que se verificó, corriendo

Esto es lo que agy no podía hacer, y es donde estaba lo que faltaba:

- **Ronda parcial de verdad**, sobre `nucleo/version.py` (15 sitios): con `--lineas 43-56` mutó 3,
  anunció `*** RONDA PARCIAL DE MUTACIÓN` en la primera línea y `RESUMEN: RONDA PARCIAL (3 de 15
  sitios del objetivo)` al final; con `--sitio nucleo/version.py:51:8:retorno` mutó 1 de 15.
- **Ronda completa**: 15/15 y el mensaje de siempre. No cambió nada para quien no usa el filtro.
- **Filtro que no selecciona nada**: `--lineas 25-30` sobre un archivo cuyos sitios están en otras
  líneas sale «el filtro de sitios no seleccionó ningún sitio» con código 2. Falla cerrado, que era
  la mitad del encargo: una ronda vacía no puede decir «todos muertos».
- La medida `proceso.ronda_mutacion_concluyente` se pone en **rojo** ante una ronda parcial, que es
  lo que se pedía.
- Suite completa, aceptación ✓ (119 rojos / 84 verdes, con los dos casos nuevos), corpus 210,
  mutación de medidas 994/994, diferencial y sintaxis al día.
- **Los dos consumidores no se ven afectados**: ninguno emite `corrida_mutacion` —esa relación es
  evidencia de la mutación del propio Oracle, que en un consumidor se saltea—, así que el campo nuevo
  no les pide nada.

## Defecto, corregido por Claude

### R1. Una ronda parcial salía con código 0

El informe decía «PARCIAL» por todos lados y la medida se ponía roja, pero `mutar_codigo.py`
terminaba con **0**: el mismo código que una verificación completa. Quien mire sólo `$?` —un script,
el CI, alguien apurado— no podía distinguirlas, que es exactamente la confusión que declarar la ronda
parcial existe para evitar. Y contradecía el contrato escrito en el encabezado del propio archivo:
«2 si la ronda fue inconclusa».

Ahora una ronda parcial sin sobrevivientes sale **2**. Si además hay un sobreviviente gana el **1**:
es lo accionable, y la parcialidad se sigue leyendo en el informe. Las dos cosas tienen su test; el de
la entrega fijaba el 0 y se corrigió.

### R2. La identidad parcial no la fijaba nadie

La primera ronda de `perfiles/python/mutacion_codigo.py` dio 231 de 233: los dos vivos estaban en
cómo se guarda que la ronda fue parcial. `_identidad_ronda` tenía `parcial: bool = False` y ningún
llamador usaba el valor por omisión, así que moverlo a `True` no se notaba; y el `is not None` con que
`correr` lo calcula tampoco lo miraba ningún test. Lo segundo importa: si una ronda filtrada quedara
guardada como completa, reanudarla sin filtro la tomaría por la misma. `parcial` pasa a ser un
parámetro obligatorio —una identidad que no lo dice está diciendo que la ronda fue completa— y un
test lee el manifiesto de una ronda parcial y de una completa.

## Lo que se revisó y quedó como estaba

- **`total_sitios` se calcula antes de filtrar**, y los equivalentes se validan contra el inventario
  completo. Las dos son las decisiones correctas y no son obvias: con el denominador recortado, una
  ronda parcial podría publicar «3 de 3» y con los equivalentes filtrados, un equivalente declarado
  fuera del rango parecería vencido.
- **El filtro marca la ronda como parcial aunque seleccione todos los sitios.** Es conservador en la
  dirección correcta: declarar parcial algo completo pierde una verificación; al revés, la inventa.
- **`parcial` entra en la identidad de la ronda**, así que reanudar un manifiesto no mezcla una ronda
  parcial con una completa.
- Los 25 campos de `corrida_mutacion` quedaron declarados junto al emisor (`CAMPOS_DE_RELACIONES`),
  que es lo que 0.22.0 pide, y el test que los compara con las filas emitidas pasa.
