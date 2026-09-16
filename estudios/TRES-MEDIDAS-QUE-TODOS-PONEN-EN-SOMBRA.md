# Tres medidas que los dos consumidores ponen en sombra

2026-09-16. Tarea [`20260915-155111-exigentes`](../tareas/20260915-155111-exigentes/TAREA.md).

Desde el 2026-09-01, LyraGASP y Jam declaran en sombra **exactamente las mismas tres medidas
universales** de Oracle. Que el 100 % de los consumidores conocidos tape lo mismo es una señal sobre
el catálogo antes que sobre los consumidores, y por eso la tarea existía.

## Lo primero que se midió: la deuda creció

| medida | LyraGASP 09-01 | LyraGASP 09-16 | Jam 09-01 | Jam 09-16 |
|---|--:|--:|--:|--:|
| `meta.toda_cantidad_comparada_tiene_unidad_derivable` | 16 | **60** | 54 | 54 |
| `meta.todo_umbral_declara_de_donde_sale` | 9 | **26** | 41 | 41 |
| `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` | 9 | **17** | 9 | **16** |

Ninguna de las seis sombras tenía `cota`, que es el mecanismo que el propio proyecto tiene para esto
desde 0.11.0. En quince días, cuatro de las seis crecieron —una casi cuatro veces— sin que nada
fallara, mientras las tres explicaciones seguían diciendo los números de septiembre 1.

**Hecho el 2026-09-16:** las seis sombras tienen cota con el valor medido ese día, en los dos
consumidores. `meta.ninguna_sombra_supera_su_cota` y `meta.ninguna_cota_mas_alta_que_su_deuda` dan
cero en los dos. Si la deuda sube, la corrida se pone roja.

## Una por una

### `meta.todo_umbral_declara_de_donde_sale` — la exigencia es correcta y la herramienta existe

`oracle medida nueva` escribe el andamio con `segun SEGUN` y la lista de valores posibles en un
comentario: una medida escrita con el andamio no puede olvidarse. La deuda crece porque los
consumidores escriben medidas **en JSON canónico**, donde omitir `segun` es legal desde 0.9.2 —la
ausencia se expresa omitiendo la cláusula—.

No hay nada que aflojar en la medida: decir de dónde salió un número es barato y el que no lo dice no
se puede auditar. Lo que falta es que el camino del JSON no sea más fácil que el correcto.

### `meta.toda_cantidad_comparada_tiene_unidad_derivable` — falta una herramienta, y es la del medio

Para que una comparación tenga unidad derivable, la relación tiene que estar **declarada** con la
unidad de cada campo. Ninguno de los dos consumidores declara una sola relación: no tienen carpeta
`relaciones/`. Con eso, la medida no puede dar otra cosa que el total de sus comparaciones, y crece
sola con cada medida nueva.

Oracle ya sabe lo que haría falta: `oracle relaciones` lista las relaciones **observadas** en la
evidencia con sus campos. Lo que no existe es el paso de ahí a `relaciones/*.json`, que hoy se
escribe a mano, relación por relación, y que es exactamente lo que las dos explicaciones de sombra
dan como razón («se hace por relación, no de golpe»).

Queda como tarea [`20260916-035758-declarar`](../tareas/20260916-041500-declarar/TAREA.md): que
`oracle relaciones` pueda escribir el esqueleto de las relaciones observadas, con sus campos y la
unidad sin declarar, para que el trabajo del consumidor sea **revisar y completar** en vez de
transcribir.

### `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` — la herramienta existe y el trabajo es suyo

`oracle observar` (0.8.1) conserva una corrida real como caso con `procedencia: observada`. Lo que
falta en los dos consumidores es correr los sensores contra el mundo real —en los dos casos, con el
editor de Unreal abierto—, y eso es trabajo de ellos, no una exigencia mal puesta. Es también la
medida que más justifica su rojo: un catálogo fijado sólo con evidencia que alguien escribió a mano
puede estar ajustado a sus propios ejemplos.

## Lo que NO se hizo, y por qué

- **No se aflojó ninguna de las tres.** Ninguna resultó ser una exigencia equivocada: dos tienen
  herramienta y la tercera muestra que falta una.
- **No se pasaron a `del_origen`.** Las tres hablan de cómo está escrito el catálogo del proyecto
  evaluado, no de la instalación de Oracle: un consumidor puede arreglarlas, que es la prueba de que
  obligarlo tiene sentido.
- **No se les puso cota en Oracle.** La cota es del proyecto que tiene la deuda, no de la medida.
