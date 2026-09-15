# Una medida se declara aplicable por el nombre de la relación aunque lea campos que la evidencia no trae

- ESTADO: ABIERTA
- PRIORIDAD: 78
- ETIQUETAS: oracle, metalenguaje

Salió de `20260915-155111-mutante` (el dueño decidió tratarla aparte, 2026-09-15).

`medidas_aplicables` (`nucleo/medida.py`) elige juezas por relación presente, no por campos. Una
medida que lee un campo que la evidencia no trae se declara aplicable y revienta dentro del `donde`
con `ErrorDeAlgebra` («sobre un valor ausente»); las herramientas lo atajan como «NO pudieron
juzgar», que es no juzgar en silencio con un aviso impreso.

El lenguaje ya tiene cómo declarar una relación con sus campos (`relaciones/*.json`: `relacion`,
`campos`, tipo y unidad) y medidas meta sobre esas declaraciones (`campo_declarado`,
`meta.ningun_campo_sin_unidad_declarada`).

A decidir y medir:

- una medida meta: toda medida lee sólo campos declarados de su relación (con relaciones de
  proceso sin declarar hoy, ¿rojo, sombra o `del_origen` hasta declararlas?);
- qué pasa en evaluación cuando falta un campo: error de declaración antes de evaluar, rojo, o
  SIN EVIDENCIA; hoy es un traceback atajado por cada herramienta por separado.
