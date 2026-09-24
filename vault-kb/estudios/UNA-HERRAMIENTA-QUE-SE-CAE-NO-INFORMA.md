# Una herramienta que se cae no informa nada

**Fecha:** 2026-09-07. **Estado:** arreglado, sin corte.

`oracle test --proyecto <consumidor>` moría con un traceback:

```
ValueError: la macro ninguno lleva 8 argumento(s) y recibió 6
```

Apareció al subirle el pin a Jam, y lo primero que hubo que establecer es **si lo traía la versión
nueva**. No: se reproduce idéntico instalando 0.5.0 —la que Jam tenía fijada—, 0.8.1 y 0.9.0 en
venvs limpios. Venía pasando desde al menos cuatro versiones, sobre el comando que el propio
`AGENTS.md` de Jam manda correr.

## Lo que se perdía

La causa es del consumidor: 33 de las 41 medidas de Jam están escritas contra una aridad anterior
de `ninguno`, `peor` y `ninguno-par`, de antes de que ganaran `ambito`. **Cargan y evalúan bien** —
por eso corpus, aceptación, mutación y diferencial pasan—; lo que no puede es imprimirlas.

Pero el defecto que importa no es ése. Es que la **primera** excepción se llevaba puesta la corrida
entera: no se informaba ni una de las 33, y las cuatro etapas siguientes —aceptación, diferencial,
mutación, veredicto— no se ejecutaban. Un consumidor con un archivo roto no recibía un informe con
un problema: no recibía informe.

## El arreglo, y la distinción que exige

`_fila_verificacion` y `_fila_verificacion_caso` atrapan la excepción y devuelven una fila que lo
declara, con dos campos nuevos: `imprimio` y `error`. `verificar_catalogo` los junta en `ilegibles`,
y `cmd_test` los informa **primero**, con nombre y motivo, recortando a diez y diciendo cuántos
faltan.

Lo que no se podía hacer es confundir las dos fallas. «No coincidió la ida y vuelta» y «no se pudo
imprimir» son cosas distintas: la primera dice que la superficie pierde información, la segunda que
no hubo superficie que comparar. Decirlas con la misma frase manda a buscar el defecto al lugar
equivocado. Es la misma distinción que el núcleo ya hace con `Veredicto.sin_evidencia` —«un rojo
dice que el mundo está mal, y esto dice que no hay con qué mirar»— y la que la relación
`equivalencia` ya modela con su campo `error`, que las cuatro medidas `meta.sintaxis_*` miran
aparte de los booleanos.

## Una discrepancia que vale la pena dejar escrita

`agy` argumentó que, cuando `imprimio` es falso, `json_igual` y `texto_igual` deberían quedar en
**`true`** y no en `false`, siguiendo a `nucleo/marco.py`, que iguala `dio` a `esperado` cuando no
hay nada que comparar para que la medida de coincidencia no juzgue una fila que no le toca.

El argumento es bueno y no se siguió. La diferencia está en de qué lado cae cada elección:

- `esperado_ok` y `dio_ok` son un **par que se compara consigo mismo**. Ningún valor fijo es más
  seguro que otro, así que igualarlos es la única salida neutral.
- `json_igual` es un **booleano suelto** con un lado seguro y uno peligroso. Y `Veredicto` ya
  decidió cuál: «`ok` sigue en False porque lo único inaceptable es que salga verde».

Con `false`, si alguien borra el informe de ilegibles la corrida igual sale roja por el camino
viejo. Con `true` sale **verde** y nadie se entera. Fail-closed contra fail-open, y el proyecto ya
eligió ese lado en todos los demás.

## Lo que NO se hizo, y por qué

**No se agregó una medida al catálogo.** Fue la otra pregunta a `agy`, y su respuesta convence:
sería universal, se pondría roja en Jam, y **Jam no puede arreglarla** — sus medidas son ASTs
válidos que el cargador acepta; quien no puede imprimirlas es el impresor de Oracle. `DECISION-012`
lo dice: «un rojo sobre el que el receptor no puede actuar enseña a ignorar la herramienta». La
etapa de sintaxis de `cmd_test` es un arnés, como el paso de corpus, y ahí es donde corresponde
informarlo.

**No se arreglaron las 33 medidas de Jam.** Es trabajo del otro repositorio y son 33 archivos.

**No se cambió el código de salida:** sigue distinto de cero, que es lo que corresponde. Lo que no
se pudo verificar no se da por bueno, y el precedente aplicable es `SIN EVIDENCIA` —que la
aceptación cuenta como falla— y no el de las sombras, que exigen una declaración deliberada con
fecha y motivo en `oracle.json`. El arnés nunca decide solo que algo pase a sombra.

## Sobre los agentes

`codex` **se bloqueó dos veces** por el filtro de su proveedor —`This content was flagged for
possible cybersecurity risk`—, las dos con encuadres que pedían encontrar cómo hacer fallar una
herramienta propia. La segunda vez tras 31.9k tokens de trabajo ya hecho, al llegar a permisos y
enlaces simbólicos. Re-despachado en positivo —«escribí los tests que faltan»— entregó **10 tests
que pasan**, cubriendo lo pedido más un `KeyError` del impresor de casos que encontró él. Se
adoptaron cambiándoles la ruta absoluta por la del árbol.

La lección para la próxima: a `codex` hay que pedirle **lo que tiene que construir**, no lo que
tiene que romper. Es el mismo trabajo y pasa el filtro.

`agy` entregó las cuatro respuestas con el texto que evaluaba citado, acertó en dos decisiones,
falló en una con un argumento que valía la pena responder, y no inventó nada para tener algo que
entregar.
