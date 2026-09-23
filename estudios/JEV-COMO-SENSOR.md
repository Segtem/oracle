# Jev como sensor de prosa de Oracle

Fecha: 2026-09-22. [Artefactos y análisis reproducible](../tareas/20260922-190222-jev-prueba/ANALISIS.md).

Las rutas de artefactos que siguen son relativas a esa carpeta de tarea.

## Resultado y decisión

**No adoptar estas tres preguntas como una guarda automática de calidad.** Jev detectó los 10 controles
artificiales, con 30/30 respuestas esperadas, pero coincidió con Claude en sólo **31/45 respuestas
(68,9 %)** sobre las 15 medidas reales. Sólo 1/15 medidas tuvo el patrón completo acordado.
El problema se concentra en `porque`: 1/15 de acuerdo. Las dos preguntas de `alcance` dieron
15/15 cada una. Eso permite considerar `alcance` una señal prometedora en este lote, no un sensor
ya validado en general. No se añadió la medida al catálogo productivo.

La hipótesis de bajo costo queda respaldada: **US$ 0.000877044** en seis solicitudes,
0,0877044 centavos de dólar, muy por debajo del tope de US$ 5. La de acuerdo alto para toda la prosa
no queda respaldada. Es desacuerdo con un juez de referencia de IA, no una medición de verdad humana.

## Diseño fijado antes de llamar al modelo

Se congelaron las 62 medidas del catálogo propio y del perfil Python en `catalogo-congelado.json`.
El lote tiene 72 registros: 62 reales y 10 variantes de medidas reales elegidas con semilla
20260922. En cada variante se sustituyeron **ambos** campos: `alcance` por una frase genérica y
`porque` por una no-defensa. Por ejemplo «No ve nada más.» y «Porque sí.».
Se fijó para todas el patrón esperado no/no/sí en `clave-controles.json`, antes de la llamada.

Se mezclaron los registros con la misma semilla. Se enviaron sólo identificadores opacos, los dos
textos, el umbral y su origen `segun`; no se enviaron nombres de medidas, etiquetas de control,
respuestas esperadas ni el juicio de Claude. `lote.json`, `protocolo.json` y las seis
`solicitud-NN.json` conservan el diseño y el cuerpo exacto de cada petición.

Preguntas, en español, coincidentes semánticamente con las tres del juicio ciego:

1. ¿El alcance nombra algo concreto que la medida no mira?
2. ¿El porque explica por qué ESE número del umbral y no otro?
3. ¿El alcance es una promesa vacía del tipo «no ve todo lo demás»?

Se usó `noul`, con sí si P(sí) >= 0,5, fijado antes de correr. Se hicieron seis solicitudes
secuenciales de 12 registros × 3 preguntas: 216 respuestas, sin reintentos ni afinación posterior.
Se solicitó `typesafe/jev-1.13`; todas las respuestas identifican
`typesafe/jev-1.13-20260917`, proveedor TypeSafe.
La receta [triage de OpenRouter](https://openrouter.ai/labs/jev/triage) usa preguntas por registro
contra `/api/alpha/decisions`; se reprodujo ese mecanismo directamente, sin una llamada extra a
Claude para compilar las preguntas. La [ficha del modelo](https://openrouter.ai/typesafe/jev-1.13)
publica la tarifa; los costos de abajo provienen de `usage.cost`, no de estimarla.

**Orden del cegamiento:** las seis respuestas quedaron guardadas a las 20:04:16 UTC y se escribió
`respuestas-guardadas.json`; sólo después se abrió `juicio-ciego-claude.json`.
Su SHA-256 es `dc84bda7d7be8c0063f88e2363179187bc6042fbae16b26a2f6ceaa88f1df618`, coincidente con el prefijo registrado antes del experimento.
La tarea ya revelaba el patrón agregado sí/sí/no: por tanto el operador conocía ese resumen,
aunque no abrió ni usó el archivo individual para preparar el lote.

## Costos y latencia observados

| Corrida | Respuestas | Segundos de extremo a extremo | USD reales (`usage.cost`) |
|---|---:|---:|---:|
| 1 | 36 | 3.082 | 0.000151872 |
| 2 | 36 | 1.605 | 0.000164136 |
| 3 | 36 | 0.956 | 0.000140910 |
| 4 | 36 | 0.956 | 0.000142968 |
| 5 | 36 | 0.974 | 0.000137130 |
| 6 | 36 | 1.967 | 0.000140028 |

Total: 9.539 s de peticiones secuenciales; mediana por petición:
1.289 s. Incluye red, no es latencia pura de inferencia ni una prueba
bajo carga. `corridas.json` conserva fechas, HTTP 200, costo y hash de cada cuerpo crudo.
No hubo llamadas facturables adicionales. El costo es el informado por el proveedor en la respuesta,
no una conciliación separada de factura ni saldo global de la cuenta.

## Acuerdo y controles

| Pregunta | Acuerdo en reales | Controles correctos |
|---|---:|---:|
| Alcance concreto | 15/15 | 10/10 |
| Porque defiende el número | 1/15 | 10/10 |
| Alcance vacío | 15/15 | 10/10 |

La referencia constante sí/sí/no da 45/45 en reales y 0/30 en controles. Jev da 61/75 en el conjunto
etiquetado (81,3 %, frente a 60 % de esa referencia), pero ese agregado oculta el fallo de P2.
Para P2, el promedio de acierto entre sus dos polaridades es apenas 53,3 %.
Sobre las 62 reales completas, Jev emite 51 señales adversas de `porque`, cero de las otras dos
preguntas. Sólo 15 tienen referencia: no se atribuye exactitud a las otras 47.

## Dónde discrepa y qué puede significar

Todas las discrepancias son respuestas no en P2 donde Claude dijo sí:

| Medida | P(sí) de Jev |
|---|---:|
| `meta.toda_medida_declara_su_ambito` | 0.21 |
| `meta.donde_compone` | 0.47 |
| `meta.toda_medida_filtra_o_agrupa` | 0.27 |
| `simulacion.la_traza_no_tiene_huecos` | 0.46 |
| `meta.agrupar_no_agranda_la_relacion` | 0.44 |
| `meta.una_macro_equivale_a_su_expansion` | 0.25 |
| `meta.todo_umbral_declara_de_donde_sale` | 0.14 |
| `meta.ninguna_sombra_supera_su_cota` | 0.25 |
| `meta.el_diagnostico_no_publica_el_dominio` | 0.12 |
| `proceso.verificacion_vigente` | 0.14 |
| `meta.toda_medida_esta_ejercitada` | 0.39 |
| `proceso.sintaxis_valida_tras_edicion_masiva` | 0.22 |
| `proceso.verificador_sin_falsos_rojos` | 0.36 |
| `meta.el_caso_reclama_una_medida_que_existe` | 0.16 |

En `meta.toda_medida_declara_su_ambito`, la defensa dice que toda medida debe declarar dónde obliga;
eso justifica contractualmente cero ausencias, aunque no repita el numeral. En
`meta.todo_umbral_declara_de_donde_sale` ocurre lo mismo: ninguna ausencia de procedencia resulta
aceptable. Jev les asigna 0,21 y 0,14. En `meta.donde_compone` la defensa exige equivalencia de
filtros y testigos, que sostiene cero diferencias; Jev queda en 0,47.

**Interpretación, no explicación causal demostrada:** la formulación «ESE número y no otro» puede
inducir una exigencia demasiado literal para umbrales contractuales de cero. Además no se envió
la tubería de la medida: el modelo recibió sólo prosa, umbral y `segun`, y puede faltarle contexto.
No hay justificaciones textuales del modelo que permitan distinguir esas causas. No se cambiaron
las preguntas ni el umbral después de ver el juicio. Respecto de Claude son falsos negativos de
«defensa presente», equivalentes a falsas alarmas de defecto; no se prueba que Claude sea infalible.

## Cierre del ciclo en Oracle

`afirmacion_prosa.json` contiene 216 filas con `registro`, `medida`, `pregunta`, `respuesta` y
`probabilidad`. Esta última significa P(sí), no confianza en la respuesta elegida. `registro`
distingue originales de variantes con el mismo nombre de medida.

El proyecto aislado `proyecto-sensor/` declara la relación y una única medida,
`prosa.senales_de_prosa_deficiente`: cuenta respuestas no a P1/P2 o sí a P3 y exige cero para dar
verde. Su `alcance` declara procedencia probabilística, corte 0,5, falta de calibración y límites.
No transforma las señales en afirmaciones de que la prosa sea falsa.

El corpus se escribió antes de la medida: tres casos rojos, uno por rama, y un verde con las tres
respuestas favorables; son recortes de las respuestas observadas. Verifica el cableado, no la
exactitud semántica del sensor. El esquema del corpus y la aceptación pasan. Los cuatro juicios
individuales dan los colores esperados. `oracle juzgar` sobre todo el lote da **ROJO con 81
señales**: 30 en controles y 51 en textos originales. No son 81 medidas defectuosas.
Se conserva en `juzgar-lote.json`; comandos y códigos de salida en `verificaciones.json`.

Repetir el análisis y los juicios no consume API:

```bash
python3 tareas/20260922-190222-jev-prueba/analizar.py
python3 tools/corpus.py --proyecto tareas/20260922-190222-jev-prueba/proyecto-sensor
python3 tools/aceptacion.py --proyecto tareas/20260922-190222-jev-prueba/proyecto-sensor
python3 tools/cli.py juzgar --proyecto tareas/20260922-190222-jev-prueba/proyecto-sensor --con tareas/20260922-190222-jev-prueba/afirmacion_prosa.json --json
```

El último comando sale con código 1 porque hay señales rojas. `experimento.py` separa preparación
y corrida, rechaza sobrescribir el lote o repetir una pasada ya registrada y sólo toma la clave
del entorno; no guarda cabeceras. No hace falta volver a ejecutarlo para revisar los resultados.

## Límites de la conclusión

Son 15 textos reales de una sola base, un juez de IA y diez controles sintéticos fáciles con los
dos campos degradados a la vez. Las 75 respuestas etiquetadas no son 75 textos independientes.
No se probaron corrupción de un solo campo, defectos sutiles, otros idiomas, estabilidad entre
corridas, efectos de compartir lote ni calibración. Un pleno de 10/10 no garantiza sensibilidad
perfecta fuera de este lote. No se fijó un porcentaje mínimo de adopción: la decisión de no
adoptar se apoya en el desacuerdo extremo de P2, no en inventar un umbral de éxito retrospectivo.

El experimento pedido está completo. Una eventual segunda prueba necesita un diseño nuevo y una
referencia adjudicada; no queda implícita una autorización para desplegar esta medida.

## Segunda corrida — criterio explícito y tubería (2026-09-22, Salta)

**P1 coincide en 15/15 reales y atrapa 10/10 controles; P2 no se pudo evaluar.**
La nueva referencia independiente contiene 7 sí y 18 no. Jev reproduce los 25
juicios con el corte preestablecido P(sí) >= 0,5. Esta segunda corrida no repite
el fracaso anterior, pero tampoco valida una guarda productiva ni demuestra que
las probabilidades estén calibradas. No se incorporó ningún sensor al catálogo.

Los [artefactos v2](../tareas/20260922-220029-jev-porque-v2/analisis.json) están en
`tareas/20260922-220029-jev-porque-v2/`. Allí `CRITERIO.md` separa origen del valor
(P1) de elección frente a valores vecinos (P2), con ejemplos positivos y negativos
fijados antes de ambos juicios. Se envió íntegro como `state.description` en cada
solicitud. Los registros incluyen la tubería canónica, resumen, prosa y umbral,
exactamente como quedaron congelados en `lote.json`; las 25 entradas ciegas son
un subconjunto idéntico de ese lote. Se mantuvieron orden, mezcla, diez controles
sin marcar, seis lotes de doce y preguntas del protocolo. No se enviaron nombres
de medidas, etiquetas de control, expectativas ni respuestas de Claude.

### Referencia y trazabilidad

El usuario confirmó que una sesión limpia de Claude vio sólo `CRITERIO.md`,
`INSTRUCCIONES.md` y `registros.json`. La nota de tarea documenta esa delegación.
Se validaron antes de llamar los 25 IDs únicos, booleanos, justificaciones,
citas presentes en la prosa y P2 null. El archivo recibido no consigna versión
exacta ni fecha del juicio: quedan como datos no disponibles, sin inventarlos.
El operador leyó el juicio para validarlo; no es un operador ciego, y el criterio
no se ajustó tras esa lectura. `referencia-sellada.json` conserva el registro
previo a las llamadas y los hashes de los insumos. SHA-256 del juicio:
`afb4f78d0bd0a21eb18ce75aed00c2aa735599e68125e9e31456974e4c1cb574`.

Se ejecutó el lote completo previsto de 62 reales y 10 controles, con 73 respuestas:
72 de P1 y una de P2. **Las 25 entradas del juicio tienen umbral `<= 0`, con límite
numérico cero; P2 no aplica en las 25, su denominador es 0 y su acuerdo es no
estimable.** No se codificó null como no. Sólo `v003`, fuera de la referencia,
tiene límite 90: su P2 dio P(sí)=0,40, dato sin juicio con el cual evaluar acuerdo
o calibración. No se amplió la muestra después de ver los resultados.

### Acuerdo y controles

| P1: origen del valor | Acuerdo | Sí correctos | No correctos | Falsos sí / falsos no |
|---|---:|---:|---:|---:|
| Reales con referencia | 15/15 | 7 | 8 | 0 / 0 |
| Controles artificiales | 10/10 | 0 | 10 | 0 / 0 |
| Total con referencia | 25/25 | 7 | 18 | 0 / 0 |

Los controles también coinciden 10/10 con la expectativa negativa fijada antes
de la corrida. P1 es la única pregunta aplicable: no se atribuye un patrón de
dos respuestas acertadas a un registro cuya P2 no aplica. La regla constante
«no» daría 8/15 reales y 18/25 total; el acuerdo no se explica sólo por la clase
mayoritaria. Las otras 47 reales carecen de referencia y no reciben exactitud.
`comparaciones.json` conserva cada ID, medida, juicio y probabilidad.

### Calibración descriptiva de P(sí)

El Brier es el promedio de (P(sí) − juicio booleano)²; menor es mejor. La pérdida
logarítmica usa logaritmos naturales. Son mediciones respecto de Claude, no de
verdad humana. No se ajustó ningún calibrador sobre estos mismos datos.

| Conjunto | Brier | Pérdida logarítmica | P(sí) media | Frecuencia de sí | ECE |
|---|---:|---:|---:|---:|---:|
| 15 reales | 0,12209 | 0,41063 | 0,3760 | 0,4667 | 0,324 |
| 10 controles | 0,00122 | 0,03463 | 0,0340 | 0 | 0,034 |
| 25 combinados | 0,07374 | 0,26023 | 0,2392 | 0,2800 | 0,208 |

ECE es la diferencia absoluta entre probabilidad media y frecuencia observada,
ponderada por tamaño, en cinco intervalos fijos de ancho 0,2 (último cerrado en 1).
Esta partición descriptiva se eligió al analizar, no fue preregistrada como
criterio de aprobación. Los intervalos vacíos se omiten:

| P(sí), conjunto de 25 | n | P(sí) media | Fracción observada de sí |
|---|---:|---:|---:|
| [0; 0,2) | 12 | 0,0475 | 0 |
| [0,2; 0,4) | 6 | 0,2533 | 0 |
| [0,4; 0,6) | 6 | 0,5350 | 1 |
| [0,6; 0,8) | 1 | 0,6800 | 1 |

Hay separación binaria perfecta en esta muestra, pero probabilidades conservadoras:
los siete positivos reciben 0,50–0,68, los ocho negativos reales 0,09–0,33 y los
controles 0,02–0,04. Dos positivos (`v029`, `v033`) están exactamente en 0,50:
cuentan como sí por el corte ya fijado. Como sensibilidad descriptiva, usar > 0,5
bajaría el acuerdo real a 13/15; no se cambió el corte. La confianza en la clase
elegida promedia 0,676 en reales, frente a acuerdo observado 1. No hay errores
observados para evaluar su confianza. El Brier de un predictor constante «no»
sería 0,46667 en reales y 0,28 combinado; el predictor constante de prevalencia
estimada en estos mismos datos daría 0,24889 y 0,2016, respectivamente. Ninguna de
estas comparaciones convierte 25 etiquetas dependientes de un juez en una prueba
de calibración general. Los controles fáciles mejoran mucho el agregado.

### Costo y latencia

Se solicitó `typesafe/jev-1.13` por `/api/alpha/decisions`, con respuestas `noul`.
Las seis respuestas identifican `typesafe/jev-1.13-20260917`, proveedor TypeSafe.
Todas dieron HTTP 200; no hubo reintentos ni llamadas facturables adicionales.

| Solicitud | Respuestas | Segundos | USD (`usage.cost`) |
|---|---:|---:|---:|
| 1 | 13 | 1,209 | 0,000251580 |
| 2 | 12 | 1,444 | 0,000227724 |
| 3 | 12 | 1,391 | 0,000252168 |
| 4 | 12 | 0,774 | 0,000228228 |
| 5 | 12 | 1,443 | 0,000226674 |
| 6 | 12 | 1,243 | 0,000257292 |

**Total: US$ 0,001443666 = 0,1443666 centavos de dólar**, bajo el tope US$ 0,05;
7,503 s de peticiones secuenciales, incluida red. Costo informado por el proveedor,
no conciliación de factura. `corridas.json`, `solicitud-NN.json` y
`respuesta-cruda-NN.json` guardan costos, tiempos, solicitudes, respuestas y hashes.
La clave se tomó del entorno; no se imprimió ni se guardaron cabeceras.

### Interpretación y reproducción

La pregunta anterior de `porque` daba 1/15; la nueva P1 da 15/15. **No son la misma
pregunta ni la misma referencia**: también cambió el contexto enviado. El resultado
es compatible con que aclarar criterio y dar tubería resuelva la discrepancia,
pero no permite separar causalmente ambos cambios ni generalizar. Un juez de IA,
15 textos reales, controles sintéticos fáciles y una sola pasada justifican una
señal prometedora para P1, con revisión, no adopción automática. P2 sigue abierta
como capacidad sin evaluar; otro estudio requeriría umbrales no cero y referencia
independiente fijados antes de llamar. No se autorizan nuevas corridas por este informe.

Reproducción sin gasto:

```bash
python3 tareas/20260922-220029-jev-porque-v2/preparar.py --verificar
python3 tareas/20260922-220029-jev-porque-v2/verificar_paquete.py
python3 tareas/20260922-220029-jev-porque-v2/analizar.py
```

`correr.py correr` consume API y rechaza repetir una pasada completa o parcial;
no es necesario ejecutarlo para reproducir el análisis. El protocolo y sus hashes
se conservaron como diseño histórico; el estado efectivo de ejecución está en
`respuestas-guardadas.json` y en la tarea.

Verificación: `python3 tools/cli.py test` terminó con salida 0 y VERDE: 2401
unitarios OK y 1010/1010 mutantes de medidas muertos; también pasaron las cuatro
pruebas del paquete, la integridad congelada y `git diff --check`. Log de esta
pasada: `verificacion/oracle-test-v2.log`. La suite estándar omite mutación de
código. No se reejecutó `--todo`: el timeout de su línea base ya está documentado
en la tarea `20260922-221412-timeout-suite-mutacion`; no se declara verde ese nivel.
No hubo commits.
