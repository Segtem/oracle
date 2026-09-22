# Jev como sensor de prosa de Oracle

Fecha: 2026-09-22. Tarea: `20260922-190222-jev-prueba`.

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
