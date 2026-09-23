# Qué le falta al lenguaje para que escribir medidas sea cómodo

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, metalenguaje, ergonomia


## La pregunta

Brian (2026-09-23): «ver qué le falta al metalenguaje para que sea más cómodo para trabajar».

No se responde con gustos: se responde con evidencia de uso real. Hay mucha:

- **Los catálogos que ya existen**: Oracle (62 medidas), Jam (83), LyraGASP (66), los ejemplos. ¿Qué
  patrones se repiten a mano en muchas medidas? ¿Qué se escribe largo que podría ser una macro o una
  forma de la superficie? ¿Qué medidas tuvieron que torcer el álgebra para decir algo simple?
- **Los agentes que escribieron Oracle desde afuera**: la batalla naval de agy
  (`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280`), la guía de la batalla naval
  (`~/TestOracleEjemplo/GUIA22.md`), el postmortem (`estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md`):
  dónde se trabaron, qué errores de carga vieron, qué mensaje no entendieron.
- **Lo que ya se tuvo que agregar por necesidad**: `sin` (0.26), `requiere` con condición, el doble
  `agrupar` para contar distintos que apareció en la guía. Cada uno fue una fricción antes de ser
  una forma del lenguaje.
- **Los mensajes de error**: los que salen con traceback, los que no dicen qué hacer.

## Qué hacer

1. Un inventario de fricciones con **evidencia citada** (archivo y línea, o comando y salida), sin
   inventar ninguna.
2. Agruparlas y, para cada grupo, la forma más chica que la resolvería: una macro, un azúcar de la
   superficie, un mensaje mejor, un verbo, o nada. Recordar la regla del proyecto: **no se agrega un
   operador hasta que una segunda medida lo necesite**, y cada forma nueva tiene que decir qué cambia
   en `VERSION_ALGEBRA` o `VERSION_SINTAXIS`.
3. Ordenarlas por cuánto duele y cuánto cuesta, y proponer las tres primeras como tareas.

## Próximo paso

El inventario del punto 1, con sus citas.
