# Un hueco declarado sigue siendo un hueco

**2026-09-08 · corte 0.11.1**

## El hallazgo

El censo de 0.11.0 corrió por primera vez sobre los tres proyectos y dijo, de LyraGASP:

```
sintaxis   139/140 archivos se imprimen
```

Un archivo. `animacion.clip_de_linea_base_ausente_del_lote.json`, con el error
`se esperaba al menos un agregado`.

La medida agrupa por clip **sin agregados**, para contar ausencias del lote y no curvas. El álgebra
la acepta, la evalúa y la venía evaluando desde siempre —LyraGASP estaba verde con ella cargada—.
Lo que no se podía era volver a **escribirla**: el impresor emitía

```
    agrupar:
        clave clip = c.clip
```

y el lector lo rechazaba.

## Es el defecto de 0.9.2 otra vez

0.9.2 corrigió que el impresor escribiera `segun sin_declarar` en una invocación de macro y el
lector no lo aceptara. Éste es el mismo defecto en otra cláusula: **la superficie es más angosta
que el álgebra, y el impresor cruza esa frontera.**

La restricción era además asimétrica, y la asimetría no la sostenía nada. Las cuatro esquinas de
`agrupar`, medidas contra el álgebra:

| | el álgebra | la superficie (antes) |
|---|---|---|
| 0 claves, 0 agregados | válido, da 1 fila | **rechazado** |
| claves, 0 agregados | válido, deduplica | **rechazado** |
| 0 claves, agregados | válido | aceptado |
| claves, agregados | válido | aceptado |

Cero **claves** se aceptó siempre. Cero agregados, nunca.

## Lo que hace a este caso distinto: el hueco estaba escrito

`meta.sintaxis_cubre_algebra` es la medida que existe exactamente para esto — comprueba que toda
medida que el álgebra acepta dé la vuelta por la superficie sin perder nada. Y su `alcance` decía,
palabra por palabra:

> «agrupar con 0 a 2 claves y 1 a 2 agregados […] **NO cubre agrupar con 0 agregados (la sintaxis
> exige al menos un agregado en el bloque agrupar:)**»

El `alcance` hizo su trabajo. Cuando el consumidor pisó el defecto, el proyecto ya tenía escrito por
qué su propia sonda no lo había visto: nadie tuvo que reconstruirlo. Eso es exactamente para lo que
la cláusula existe, y funcionó.

**Pero decir dónde no se mira no es lo mismo que mirar.** Un hueco declarado y no cerrado es una
apuesta a que nadie pase por ahí, y la apuesta se paga entera cuando alguien pasa. Acá se pagó con
un archivo ilegible que estuvo semanas en un consumidor sin que nada lo señalara — hasta que una
herramienta nueva, escrita para otra cosa, lo contó.

La asimetría, además, estaba a la vista en el código del generador y nadie la leyó así:

```python
claves_opts = [("c0", []), ("c1", …), ("c2", …)]   # cero claves, desde siempre
aggs_opts   = [("a1_contar", …), …]                # cero agregados, nunca
```

## Se cierra en el generador, no en el alcance

`aggs_opts` gana `("a0", [])`. El resumen de la sonda pasa a contar grupos cuando no hay agregados
—sin `a1` no hay columna que resumir—. Y el `alcance` pierde la frase, porque ya no es cierta.

La comprobación de que esto sirve para algo no es que la sonda pase: es que **encuentre el defecto**.
Restaurado el lector viejo en una copia del árbol, la sonda extendida devuelve tres rojos:

```
✗ meta.sintaxis_cubre_algebra   3 (<= 0)
   meta_gen.grp_c0_a0 · meta_gen.grp_c1_a0 · meta_gen.grp_c2_a0
   ErrorSintaxis: línea 3, columna 5: se esperaba al menos un agregado
```

El mismo error, palabra por palabra, que el que pisó el consumidor.

## Lo que se llevó puesto de paso

`meta.sintaxis_cubre_algebra` era una de las dos medidas de DECISION-004 — las que quedaban
sostenidas **sólo por evidencia fabricada**, con la consecuencia declarada de que `aceptacion.py`
sale con código 1 mientras siga así.

Sale de la lista, y por el mismo camino que la tercera se había cerrado el 2026-09-01: no
transcribiendo evidencia, sino **cambiando el mundo**. La corrida contra el lector viejo es una
observación real de una falla real, no una construcción; los casos `488` y `489` la transcriben con
su `origen` y su comando. El rojo baja de 2 a 1.

Vale notar el orden, porque no fue el previsto: la deuda no se cerró porque alguien se sentara a
cerrarla. Se cerró porque un defecto abrió la puerta para observar algo que hasta entonces no
ocurría.

## La regla que queda

**Cuando el impresor puede escribir una forma, el lector tiene que poder leerla.** Y si la sonda que
comprueba eso no genera la forma, el hueco se cierra en el generador — no en el `alcance`.

El `alcance` es para lo que todavía no se puede mirar. No para lo que no se quiso.
