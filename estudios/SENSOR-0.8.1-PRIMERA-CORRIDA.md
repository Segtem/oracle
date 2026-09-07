# Primer recorrido real: dataset de LyraGASP

**Revisión:** 2026-09-07. **Estado:** experimento mínimo conservado; sin corte de versión.
Responde a las tres decisiones de `PLAN-0.8.1-SENSOR.md`. No agrega una capacidad al lenguaje ni
declara listo un sistema general de captura o autenticación de evidencia.

## La premisa revisada

No faltaba todo sensor: LyraGASP ya tiene adaptadores de recarga, malla y dataset, con una parte
pura y otra que lee el dominio. Algunos casos narran lecturas reales de Unreal, pero el censo
encontraba **26 casos sin `procedencia` explícita**, no 26 declarados sintéticos. No se
reclasificaron: una narración histórica no permite certificar ahora cómo se obtuvieron sus filas.

Se eligió el sensor del dataset externo, que consulta archivos reales sin abrir Unreal. Es una
observación de presencia de archivos, no de calidad del dataset ni de los assets del editor.
El sensor sigue viviendo en el consumidor, no se copió al núcleo.

## Corrida y resultado

En LyraGASP se ejecutó el adaptador existente:

```bash
python3 -B tools/mide_ml_deformer_dataset.py --salida /tmp/oracle-081-corrida-3tj70kqk/evidencia.json
```

La corrida registrada ocurrió el **2026-09-07 a las 00:42:45 UTC** (2026-09-06, 21:42:45 en Salta).
La carpeta de observación usa la fecha local; el caso y el registro usan UTC. No se actualiza esa
fecha por volver a aceptar el caso hoy.

| Lectura real | Resultado | Medida |
| --- | --- | --- |
| Clips declarados en el manifiesto | 37/37 | `ml_deformer.manifiesto_ausente_o_incompleto`: verde, 0 |
| FBX presentes | 37/37 | `ml_deformer.entrada_fbx_faltante`: verde, 0 |
| Ground truth presentes | 0/37 | `ml_deformer.ground_truth_faltante`: rojo, 37 |

La salida 0 del sensor significa que pudo emitir evidencia, no que el dataset esté bien. Oracle
juzga después. No se crearon FBX/ABC, no se abrió Unreal ni se alteraron assets. La ausencia de
37 ground truth queda registrada, no resuelta como trabajo de autoría.

## Artefactos conservados en el consumidor

Con autorización se agregaron exclusivamente cinco archivos nuevos en LyraGASP:

- `medidas/corpus/ml_deformer/017-ground-truth-ausente-en-corrida-del-dataset.json`;
- `medidas/observaciones/2026-09-06-dataset/evidencia.json`;
- `medidas/observaciones/2026-09-06-dataset/registro.json`;
- `medidas/observaciones/2026-09-06-dataset/registrar_corrida.py`;
- `medidas/observaciones/2026-09-06-dataset/README.md`.

El caso declara `procedencia: observada`: sus relaciones son exactamente el mapa emitido por el
adaptador, incorporado automáticamente, sin transcribir ni minimizar filas. Síntoma, etiqueta y
lección son el juicio explícito del experimento; la etiqueta no se calcula a partir del color.
La captura exige reproducir los 37 ausentes y rechaza una selección vacía o lecturas distintas.
Una corrida distinta se revisa, no se fuerza para que pase.

El registro conserva comando, salida, intérprete, fechas, commit y estado sucio del consumidor.
Las huellas pertinentes identifican qué fuentes se usaron sin fingir que el commit contiene todo
el árbol. El registrador reproduce esta lectura concreta desde esta máquina; no es un capturador
general ni se afirma haber fijado todo su código mediante mutación.

## Qué comprueban las huellas

Se compararon **seis referentes** antes y después: adaptador, sensor puro, inventario, manifiesto,
medida de ground truth y listado de rutas con su presencia. También se verificaron las huellas del
JSON y del registrador, y la igualdad de las relaciones del caso y de la salida. La comprobación
posterior encontró cero referentes cambiados.

La sexta huella NO afirma haber leído bytes de los FBX/ABC: identifica rutas y booleanos
`es_archivo`. Coincide con el alcance de las medidas, que sólo juzgan presencia. No demuestra que
el contenido, la topología o la sincronización no cambiaron.

L−2 se ejerció con `Referente`, `hechos_de_frescura` y la medida existente de referente vencido.
Dos controles **construidos**, separados de la observación, comprueban su límite:

- una huella distinta entre declaración leída y actual da **rojo, valor 1**;
- dos declaraciones con la misma huella falsa dan **verde, valor 0**.

**L−2 no autentica una ejecución.** Permite comparar declaraciones contra algo que se vuelve a
leer; una declaración autoconsistente puede mentir. Dos lecturas iguales tampoco prueban ausencia
de cambios intermedios. El caso es histórico: aceptar el corpus no vuelve a medir el dataset ni
certifica frescura presente. No se agregó un booleano «auténtico» para disfrazar este límite.

## Sombras y verificación

Lyra pasa corpus y aceptación con **27 casos: 13 rojos esperados y 14 verdes correctos**. El nuevo
caso es el único con `procedencia: observada` explícita; los otros 26 siguen sin declarar. Las
medidas sostenidas sólo por evidencia no observada bajan **de 9 a 8**. La sombra sigue activa,
junto con 16 comparaciones sin unidad derivable y 9 umbrales sin origen.

Jam mantiene **23 casos**, 20 rojos esperados y 3 verdes correctos. Sus tres sombras permanecen
en **9** medidas sin observación, **54** comparaciones sin unidad derivable y **41** umbrales sin
origen. Observar archivos en Lyra no observa geometría de Jam ni decide unidades o umbrales.

Pasan los **cuatro tests** existentes del sensor y adaptador de dataset. La medida de ground truth
cierra **9/9 mutantes por conducta**, cero rechazos del álgebra, usando sus tres casos. El nuevo
detecta seis de los nueve: no sustituye los bordes sintéticos ni aporta una muerte antes ausente.
Aporta la observación real que esa medida no tenía explícitamente registrada.

Oracle mantiene **184 casos** y su única medida meta roja con valor **2**, con la línea literal
de CI intacta. No se cambió su código ni se repitió la suite completa en este avance documental;
la última corrida del corte 0.8.0 sigue siendo 1295 tests. Versiones 0.8.0 / 0.6 / 0.2 conservadas;
sin cambios al servidor MCP, archivos existentes del consumidor, commits, push o publicación.

## Límite de este avance

Hay un recorrido real nuevo y respuestas verificadas a las tres preguntas del plan. No hay aún un
camino general de captura y revalidación incorporado a la herramienta cotidiana del consumidor:
el registrador conservado es específico. Tampoco se corrieron sensores que necesitan el editor,
se resolvieron los 37 ground truth o se autenticó procedencia por medios independientes. El siguiente
paso propuesto es convertir captura/revalidación en un camino reutilizable del consumidor y fijarlo
con pruebas, conservando estos límites antes de otro corte.
