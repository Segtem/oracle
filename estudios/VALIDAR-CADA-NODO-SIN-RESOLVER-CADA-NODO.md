# Validar cada nodo sin resolver cada nodo

**2026-09-10 · continuación de rendimiento**

El validador sigue recorriendo cada expresión en cada fila. La optimización resuelve el presupuesto
y el registro una vez al entrar a `validar_expr`, y la recursión usa esas mismas referencias.
No se cachea la validez de la expresión ni se elimina una validación de forma o profundidad.

## Medición antes de editar

El perfil de `ModoSombra.test_una_sombra_sin_fecha_lo_dice` tenía 2.341.040 visitas recursivas a
`validar_expr` en 405.161 llamadas de entrada. Resolver límites y comprobar que el registro era un
mapa se repetía en cada una. El tiempo del perfil incluye la sobrecarga de cProfile; no se usa como
medida del ahorro.

Se contrastaron el código anterior y el candidato, alternados en el mismo proceso, ejecutando la
misma prueba de integración y exigiendo que pasara. Para aislar el cambio se sustituyeron únicamente
las funciones de validación; no se modificó el catálogo ni el escenario de sombras.

| Orden | Variante | Segundos |
|---|---|---:|
| 1 | anterior | 1,6880 |
| 2 | candidata | 1,3256 |
| 3 | candidata | 1,3444 |
| 4 | anterior | 1,5963 |
| 5 | anterior | 1,5813 |
| 6 | candidata | 1,3340 |

Medianas: **1,5963 → 1,3340 s**, una reducción del **16,4 %** en ese escenario. Son tres muestras
por variante en esta máquina, no una garantía sobre cualquier expresión ni una medición de CI.
Las expresiones pequeñas añaden una llamada al auxiliar; las compuestas evitan resolver el contexto
en cada hijo. No se extrapola ese porcentaje a todos los consumidores.

## Premisa y límite

`LimitesAlgebra` es una dataclass inmutable. El registro se resuelve una vez por llamada y conserva
su identidad: no se copia ni se congelan sus funciones. La recursión anterior ya pasaba ese registro
explícitamente a los hijos. Por eso no necesita repetir la resolución del registro activo ni la
comprobación del tipo de presupuesto en cada nodo.

**No se supone que la expresión o el registro sean inmutables entre filas.** Las expresiones son
listas y el registro es un mapa modificable. Una escalar puede cambiar la siguiente expresión o
reemplazar una función por otra con distinta aridad. Adelantar toda la validación fuera del bucle
de filas necesitaría una garantía adicional que el sistema no impone.

El test nuevo construye precisamente esos cambios y verifica que la segunda fila falle antes de
otra llamada, con mensaje y ubicación correctos. Cubre filtro, clave de agrupación, agregado y
resumen. Es una regresión construida para fijar esa frontera; no se añadió como evidencia observada
al corpus ni se afirma que el defecto existiera antes de esta optimización.

## Contraste de mutantes

Se aplicaron a una copia **38 mutantes** del tramo refactorizado: los 38 produjeron un fallo de
pruebas, con el original en verde. Una variante manual adicional que omitía la validación por fila
también falló. Las comprobaciones de profundidad y las expresiones inválidas siguen siendo
conducta observable; no se sustituyeron por tests que sólo cuentan llamadas internas.

## Rondas completas y costo del perfil

La primera ronda completa del álgebra dio **390/390 en 383,70 s**, sin sobrevivientes, timeouts,
errores de arnés ni equivalentes declarados. Los mutantes que cambian las rutas de error de `unir`
tardaban mucho más: sus tests estaban en sintaxis, fuera del perfil prioritario.

Se agregó `tests.test_sintaxis` después de álgebra, núcleo y motor. La primera línea base del perfil
ampliado se detuvo porque el test que fija el comando seguía exigiendo los tres módulos anteriores.
Se actualizó su lista explícita con el cuarto módulo, conservando la igualdad exacta y el resto
de sus comprobaciones. Esa línea base fallida no produjo mutantes ni cuenta como ronda completa.

Con el perfil final, la ronda entera volvió a dar **390/390 en 140,83 s**: **63,3 % menos tiempo**,
sin perder mutantes ni cambiar la suite. Cero sobrevivientes, timeouts, errores de arnés y
equivalentes en ambas rondas completas. La segunda cambia únicamente el perfil y el test de su
comando: el código del álgebra es el mismo.

Las salidas conservan el diagnóstico previo sobre la medida de mutación de medidas que no aplica
a estas filas de mutación de código. No se ocultó ni se completaron campos ficticios para callarlo;
las tres medidas aplicables al protocolo de código están verdes.

## Reproducción y evidencia conservada

- [Tiempos del contraste inicial](2026-09-10-validacion/tiempos-iniciales.json).
- [Aplicaciones manuales](2026-09-10-validacion/contrastes-manuales.json), con código y fallo de cada variante.
- [Ronda con el perfil anterior](2026-09-10-validacion/ronda-perfil-anterior.json) y
  [ronda final](2026-09-10-validacion/ronda-final.json), con fuentes y dependencias identificadas por huella.
- [Reproducción independiente del contraste](2026-09-10-validacion/reproduccion.json): medianas
  **1,6152 → 1,3538 s**, mejora de **16,2 %**.

`python3 -B estudios/contrastar_validacion.py` reproduce el contraste alternado con las dos fuentes
conservadas en `2026-09-10-validacion/algebra-antes.txt` y `algebra-despues.txt`. Sustituye sólo las
funciones de validación; el resto del evaluador y la prueba son los del árbol desde el que se
invoca. Por eso una ejecución futura mide esas implementaciones sobre ese árbol futuro, no cambia
retroactivamente las cifras guardadas acá.

## Verificación del árbol final

Se ejecutó completa y en orden la lista del relevo, seguida por la aceptación de Jam con este
árbol. Las once ejecuciones salieron 0. [Comandos y duraciones](2026-09-10-validacion/verificacion/resultados.json):
**1536 tests en 41,69 s**, corpus de 203 casos, aceptación 115/81, mutación de medidas 959/959,
cifras actualizadas, manual HTML regenerado, WHEEL OK, ambas sondas, traza y Jam 28/3.
La suite anterior había tardado 43,51 s; ese par de corridas no reemplaza el contraste alternado ni
permite afirmar un 16 % de mejora en la suite entera. No se ejecutó CI remoto.

[Jam y sus referentes](2026-09-10-validacion/jam-tras-validacion.json) muestra una consecuencia
esperable del cambio de implementación: la observación anterior conserva la misma evidencia,
pero la revalidación informa el cambio de huella de `../oracle/nucleo/algebra.py`.
No se corrigió aquella observación para ponerla verde. Se capturó otra en un destino nuevo y su
revalidación dio sin cambios, valor 0 y autenticidad no comprobada. Ninguna se promovió al corpus.

No se cambiaron versiones, medidas, umbrales, cotas, procedencias antiguas ni LyraGASP. El núcleo
conserva su significado; la propuesta de corte del relevo sigue dependiendo de los cambios de
códigos de salida del CLI hechos antes de esta optimización, no de esta refactorización.
