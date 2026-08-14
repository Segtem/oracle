# Decisión 002 — las medidas no componen

**Estado:** rechazada la composición el 2026-08-03.

## Contexto

El álgebra cierra sobre **filas**: `de`, `donde`, `unir` y `agrupar` toman filas y devuelven filas, y
`resumen` las colapsa en un escalar. Esa clausura es lo que permite escribir tres dominios que no se
parecen en nada con los mismos operadores y sin un solo adaptador.

Pero **no cierra sobre medidas**. Una medida termina en un escalar y un umbral, y ahí se acaba: no hay
forma de que una medida consuma los testigos o el veredicto de otra. Eso deja preguntas naturales sin
escribir —«¿qué medidas comparten testigos?», «¿qué medida se pone roja siempre que esta otra se pone
roja?»— y obliga a que el nivel L2 se apoye en hechos que produce Python (`nucleo/marco.py`) en vez de
en el álgebra.

Una auditoría del 2026-08-03 lo señaló como el hueco de diseño más visible del proyecto: el álgebra
tiene clausura sobre la evidencia pero no sobre lo que enuncia sobre ella.

## Decisión

**La composición de medidas no entra al lenguaje.** Una medida no puede tomar como fuente el
resultado, los testigos ni el veredicto de otra medida.

## Por qué se rechaza, y no es por costo

No es una decisión de implementación diferida: el mecanismo sería barato. Se rechaza porque **es el
modo de falla que Oracle existe para evitar**.

Componer medidas permite que las medidas **se cubran entre sí**. Una medida que consume los testigos
de otra hereda su punto ciego sin declararlo, y el `alcance` —que es obligatorio justamente para que
un verde no se pueda leer como «todo bien»— deja de ser comprobable a mano: habría que recorrer la
cadena entera para saber qué no se miró. El README lo dice de la única forma que importa:

> Un conjunto de medidas puede ser internamente impecable y colectivamente ciego, y ninguna cantidad
> de reflexión lo detecta desde adentro.

La composición hace ese estado **más fácil de alcanzar y más difícil de ver**. Un conjunto de medidas
que se apoyan unas en otras produce mucho verde con poca evidencia independiente, que es exactamente
la forma que toma Goodhart cuando el que escribe la herramienta escribe también su verificador.

Hay además una razón de procedimiento, y en este repositorio pesa: **nada entra al lenguaje hasta que
una medida real lo necesite**. Hoy ninguna de las 18 medidas universales lo necesita. `con` y la unión
izquierda se retiraron por no alcanzar ese disparador, y la composición no está ni cerca de
alcanzarlo.

## Consecuencias

- El álgebra sigue cerrando sobre filas y no sobre medidas. Es una limitación **declarada**, no una
  ausencia por olvido — que es la única diferencia que importa entre las dos cosas.
- El nivel L2 sigue necesitando que alguien reifique el catálogo como hechos. Hoy eso lo hace
  `nucleo/marco.py` en Python, y ese acoplamiento es el problema que ataca el ítem (b) del
  [plan](PLAN-LENGUAJE.md) — **reificación mecánica, no composición**. Son dos caminos distintos para
  el mismo síntoma, y se elige el que no permite que las medidas se cubran entre sí.
- Una pregunta que hoy sólo se contestaría componiendo se contesta produciendo un **hecho nuevo** con
  un sensor, y midiéndolo con el álgebra que ya existe. Es más trabajo y deja la evidencia a la vista,
  que es el intercambio buscado.

## Qué evidencia revierte esta decisión

**Dos medidas reales, en un proyecto consumidor, que no se puedan expresar sin composición**, y cuya
ausencia quede registrada como hueco declarado en el corpus de ese proyecto.

Dos, no una: es el mismo disparador que aplicaron `con` y la unión izquierda, y que no alcanzaron.
Jam es el primer candidato con derecho a producir ese caso, porque es el primer consumidor que no se
diseñó junto con Oracle.

Si alguna vez entra, tiene que entrar con una regla que hoy no existe: **una medida compuesta debe
declarar el alcance acumulado de su cadena**, no sólo el propio. Sin eso, el `alcance` deja de
significar lo que significa hoy.
