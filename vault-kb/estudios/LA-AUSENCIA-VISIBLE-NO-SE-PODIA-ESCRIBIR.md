# Oracle imprimía algo que no podía volver a leer

**Fecha:** 2026-09-07. **Estado:** arreglado, con la sintaxis en `0.3`.

Apareció migrando un consumidor y no buscándolo, que es como aparecen los que importan.

## Cómo se llegó

Jam tenía 33 de sus 41 medidas escritas contra la aridad anterior de las macros `ninguno`, `peor` y
`ninguno-par`, de antes de que ganaran `segun` y `ambito`. Cargaban y evaluaban bien —el cargador
completa los dos campos con `sin_declarar`—, pero no se podían imprimir, y desde 0.9.1 `oracle test`
las listaba en vez de morir con un traceback.

La migración parecía mecánica: escribir explícitamente los dos valores que el cargador ya infiere.
Y lo es — se hizo, y **las 79 formas canónicas quedaron idénticas**, con la huella de las 41 medidas
propias coincidiendo con la línea de base tomada antes de tocar nada. Aun así los 33 seguían
ilegibles, ahora por otro motivo:

```
imprimir(...)  emite   →   segun sin_declarar
leer(...)      rechaza →   «se esperaba segun en ['contrato','convencion','medicion','tanteo']»
```

## El defecto

**La ausencia visible se podía producir y no se podía escribir.**

En la forma `medida`, `segun` y `ambito` sin declarar se expresan OMITIENDO la cláusula: el impresor
no la escribe, el lector nunca la ve, y la ida y vuelta cierra. En una invocación de macro los
argumentos son **posicionales** y no hay cómo saltear uno, así que el impresor escribía
`sin_declarar` literal — y el lector lo rechazaba.

O sea que el lenguaje imprimía una forma que él mismo no aceptaba. `meta.sintaxis_ida_y_vuelta`
existe para atrapar exactamente eso, y no lo veía: el catálogo propio de Oracle **no tiene ninguna
medida** con `segun` o `ambito` sin declarar, así que la combinación nunca se ejercía.

Es la misma familia que el defecto de 0.9.1 —una herramienta que se cae en vez de informar— y llegó
por el mismo camino: un consumidor haciendo algo que el proyecto no hace consigo mismo.

## El arreglo, y lo que NO afloja

Cuatro líneas en `_leer_argumento_macro`: `sin_declarar` se acepta como valor de `segun` y `ambito`
**sólo en argumentos de macro**, que es donde no se puede omitir.

La pregunta que hubo que contestar antes de tocar nada era si esto afloja la validación. No:

- Un valor inventado sigue siendo un error. `segun cualquiera` y `ambito global` se siguen
  rechazando, y ahora el mensaje enumera las opciones **y** la ausencia.
- Las dos medidas que persiguen la ausencia la siguen contando igual. Sus propios `porque` lo dicen:
  «`sin_declarar` es la ausencia visible que dejan las formas viejas o incompletas, **no una etiqueta
  aceptable**». Persiguen el VALOR, así que hacerlo escribible no lo hace aceptable.
- Medido sobre el consumidor que lo destapó: sus tres sombras quedaron en los mismos **9 / 54 / 41**.
  Los 41 umbrales sin origen se siguen contando uno por uno.

Lo que cambia es que ahora la ausencia **se puede escribir donde no se puede omitir**. Nada más.

## Las versiones

`VERSION_SINTAXIS` **0.2 → 0.3**: el lector gana una forma que antes era un error de sintaxis, que
es el caso 1 de la regla. Es la primera vez que se mueve desde que ganó la cláusula `ambito`.

`VERSION_DISTRIBUCION` **0.9.1 → 0.9.2**, sólo el parche. Acá me equivoqué primero y `agy` me
corrigió: yo propuse `0.10.0` por costumbre de SemVer, y el criterio que este proyecto practica para
la menor de distribución es otro, escrito en los dos cortes anteriores — **si un consumidor puede
cambiar de color**. Acá no cambia ninguno, y está medido, no supuesto.

`VERSION_ALGEBRA` queda en `0.6`: la forma canónica ya admitía los dos valores; lo que cambió es
sólo el parser de la superficie.

## Sobre los agentes

**`codex` paró donde correspondía, y eso vale más que si hubiera seguido.** Migró los 33 archivos,
comprobó que la forma canónica no cambiaba, y al toparse con el rechazo del lector informó: «Oracle
rechaza `segun sin_declarar`; resolverlo requiere modificar Oracle, fuera del alcance autorizado».
No inventó un `segun` para que pasara. Después escribió los seis tests del arreglo y —sin que se le
pidiera— los verificó mutando en memoria seis veces para comprobar que discriminan.

**`agy` anticipó el defecto antes de que ocurriera.** Se le preguntó, entre otras cosas, «¿se te
ocurre alguna forma en que esta migración pueda salir mal SIN que ninguna de esas comprobaciones lo
note?», y contestó con las líneas exactas de `nucleo/sintaxis.py` donde el lector iba a rechazar lo
que el impresor emite. Después corrigió el número de versión que yo había propuesto mal.

Las dos veces el aporte fue el mismo: no hacer el trabajo más rápido, sino evitar que saliera mal.
