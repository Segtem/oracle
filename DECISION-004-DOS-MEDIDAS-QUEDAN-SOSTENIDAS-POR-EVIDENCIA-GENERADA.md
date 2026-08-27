# Decisión 004 — dos medidas quedan sostenidas por evidencia generada, y se deja dicho

**Fecha:** 2026-08-26 · **Estado:** vigente · **Consecuencia:** `tools/aceptacion.py` sale con
código 1 mientras esto siga así.

## El hecho

`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` señala las medidas cuyos casos son **todos**
no observados. Al escribirla salió roja en 12. Diez se cerraron transcribiendo evidencia que ya
existía —un catálogo real que no tenía filtro, corridas reales del marco sobre sí mismo—. Dos no:

- `meta.sintaxis_cubre_algebra`
- `meta.sintaxis_casos_cubre_casos`

## Por qué éstas no se pueden cerrar

Las dos existen **para ir más allá del catálogo**. Su hermana `meta.sintaxis_ida_y_vuelta` comprueba
que las medidas escritas sobrevivan la ida y vuelta por la superficie, y se fija con 38 filas del
catálogo real: ésa está observada y no aparece en el rojo. Estas dos comprueban lo que la escrita a
mano **no** alcanza: que la superficie cubra formas del álgebra que nadie escribió todavía —`unir`
encadenado, `agrupar` multiclave, predicados anidados—, generadas desde la gramática.

Su sujeto es la medida generada. Una evidencia observada para ellas sería una contradicción: si la
forma estuviera en el catálogo, la cubriría `meta.sintaxis_ida_y_vuelta` y estas dos no harían falta.

## Lo que NO se hizo, y por qué

Se consideró y se descartó agregarle a la medida una condición que las excluyera —un campo de
excepción, una lista de medidas eximidas, un `donde` que las nombre—. Cualquiera de las tres es la
misma cosa: una puerta para que una medida deje de señalar sin que el hecho señalado cambie. El
proyecto existe para no tener esa puerta. Un rojo verdadero es el producto.

También se consideró aflojar el umbral a `<= 2`. Es peor: convierte una afirmación falsable en un
presupuesto, y el día que aparezca una tercera medida sostenida sólo por evidencia fabricada —una
que sí sea un descuido— entraría bajo el techo sin que nadie se entere.

## Cómo se cierra, si alguna vez se cierra

No transcribiendo nada: cambiando el mundo. Si algún día la generación por gramática deja de ser la
única forma de llegar a esas formas del álgebra —porque alguien escribe medidas reales que las usen,
en este catálogo o en el de un consumidor—, esas medidas pasan a tener evidencia observada y la
señal se apaga sola. Hasta entonces el 2 se lee, no se tapa.

## El costo asumido

`oracle test` y `tools/aceptacion.py` salen en rojo. Alguien que llegue nuevo al repo lo ve y tiene
que leer esto para saber que no es una regresión. Es un costo real y se paga a propósito: la
alternativa era un verde que no significa nada, que es el defecto que este repo cataloga 66 veces.
