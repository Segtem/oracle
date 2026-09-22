# Dos relaciones con el mismo nombre hacen caer oracle test con un traceback

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, errores, relaciones


## Qué pasó

2026-09-22, en Jam: agy declaró `medidas/relaciones/pieza.json`, y Oracle ya distribuye una relación
`pieza` (idéntica campo por campo). `oracle test --proyecto medidas` terminó con un traceback de
Python: `nucleo.relacion.RelacionMalDeclarada: la relación «pieza» está dos veces: …/site-packages/
oracle_metalenguaje/relaciones/pieza.json y …/jam/medidas/relaciones/pieza.json`.

El mensaje es claro, pero sale como traceback en vez de como un error del proyecto con salida 2, y
no dice qué hacer. Un agente lo lee como un crash de Oracle.

## Qué hacer

1. `oracle test` (y `juzgar`, `revisar`, el MCP) atrapan `RelacionMalDeclarada` al cargar relaciones
   y la informan como `PROYECTO INVÁLIDO — …` con salida 2, sin traceback.
2. Cuando el choque es con una relación que distribuye Oracle, el mensaje dice que ya existe y que el
   proyecto la usa tal cual (o la renombra), en vez de sólo «está dos veces».
3. Un test por cada verbo.

## Próximo paso

Buscar dónde se cargan las relaciones del proyecto junto con las de Oracle y quién deja escapar la
excepción; escribir los tests primero.
