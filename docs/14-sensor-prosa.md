# Un modelo como sensor de prosa

Un sensor probabilístico no es un juez. El patrón de
[`ejemplo/sensor-prosa/`](../ejemplo/sensor-prosa/) convierte respuestas de un modelo
en filas de `afirmacion_prosa`; Oracle juzga esas filas de manera reproducible y sin
red. Ni las filas ni un verde de Oracle certifican la verdad del texto.

El ejemplo es un proyecto separado: `catalogo_base: false`, relación local y medida
con `ambito del_origen`. No incorpora políticas al catálogo obligatorio, no requiere
claves para probarlo y no obliga a quienes lo hereden. Adoptarlo requiere una decisión
del proyecto consumidor.

## Qué mide y qué queda afuera

La medida cuenta señales adversas sobre `alcance`: `alcance_vacio` con respuesta
verdadera y P(sí) ≥ 0,8, o `alcance_concreto` con respuesta falsa y P(sí) ≤ 0,2.
Una sola señal basta para rojo. `probabilidad` siempre significa P(sí), incluso
cuando `respuesta` es falsa; no significa confianza en la respuesta elegida.

**El umbral de probabilidad es una decisión del proyecto, no un hecho.** Los valores
0,2 y 0,8 ilustran una política de señales fuertes; el experimento no los validó como
cortes universales. Son diferentes del `--corte-si` usado para codificar el booleano
(default 0,5) y de la zona de revisión (default 0,4–0,6, inclusive). El proyecto debe
revisar juntos estos parámetros y su medida. Cambiar el corte del sensor no cambia
los umbrales escritos en la medida.

Un verde sólo significa que no se encontró una señal adversa fuerte en las filas
entregadas. Una relación vacía o ausente no aporta la evidencia requerida y queda
como SIN EVIDENCIA. La medida no detecta omisiones parciales, respuestas inventadas,
prosa falsa o contradicciones entre el booleano y la probabilidad. El corpus incluye
algunas combinaciones incoherentes deliberadas para fijar ambos filtros; el sensor
normal deriva el booleano de P(sí). No se evalúa `porque` en este ejemplo.

## Calibración y revisión humana

La [segunda corrida del estudio](../vault-kb/estudios/JEV-COMO-SENSOR.md) cambió la pregunta
sobre `porque` e incluyó la tubería completa: obtuvo acuerdo 15/15 en las medidas
reales y 10/10 en controles con la referencia ciega. Los **sí quedaron entre 0,50 y
0,68; los no, entre 0,09 y 0,33; dos sí quedaron exactamente en 0,50**. Esa separación
angosta no da margen para automatizar un umbral fijo. La pregunta sobre valores
vecinos no se pudo evaluar en la muestra: todos sus umbrales eran cero.

Estas cifras pertenecen a `porque_origen`, no son una calibración de los cortes de
`alcance` del ejemplo. Muestran por qué tampoco corresponde convertir una buena
coincidencia en autoridad para juzgar prosa. La primera corrida sobre alcance fue
pequeña (15 reales); ninguna de las dos prueba generalización a otros proyectos.

**La zona del medio va a revisión humana.** El sensor guarda las filas entre 0,4 y
0,6 inclusive en `revision-humana.json` y termina con código 2 si hay alguna. También
conserva esas filas en `hechos.json`: quitarlas escondería evidencia. Aunque Oracle
dé verde con esos hechos, la revisión sigue pendiente. La persona revisa la prosa,
la medida completa y la respuesta; registra su decisión en la tarea del proyecto.
Un rojo fuerte también exige revisar la señal; no autoriza al modelo a corregir ni
rechazar la prosa por sí solo. Fuera de la zona media tampoco hay garantía de verdad.

## Preparar y ejecutar por separado

Desde la raíz del checkout, preparar un lote no usa red ni lee una clave:

```bash
python3 ejemplo/sensor-prosa/sensor_prosa.py preparar \
  --catalogo ejemplo/sensor-prosa/catalogos \
  --salida /tmp/prosa-preparada
oracle test --proyecto ejemplo/sensor-prosa
```

El catálogo puede ser otro directorio de medidas `.oracle` o canónicas JSON;
`--catalogo` se puede repetir. Se cargan medidas con macros estándar; los catálogos
que requieren macros privadas necesitan adaptar este ejemplo. No se importan
escalares externas ni se ejecuta el producto. Cada registro contiene alcance,
porque, umbral, origen del umbral, tubería y resumen, reutilizando el armado de
[`preparar.py`](../tareas/20260922-220029-jev-porque-v2/preparar.py).

Sólo `correr` consume API y envía esa prosa al proveedor. Primero revisá el lote y
el costo previsto; el siguiente comando hace una corrida nueva:

```bash
# OPENROUTER_API_KEY debe estar definida en el entorno, nunca en un archivo del repo.
python3 ejemplo/sensor-prosa/sensor_prosa.py correr \
  --catalogo ejemplo/sensor-prosa/catalogos \
  --proveedor https://openrouter.ai/api/alpha/decisions \
  --modelo typesafe/jev-1.13 \
  --clave-entorno OPENROUTER_API_KEY \
  --revision 0.4 0.6 --corte-si 0.5 \
  --salida /tmp/prosa-corrida
oracle juzgar --proyecto ejemplo/sensor-prosa \
  --con /tmp/prosa-corrida/hechos.json
```

El proveedor es una URL HTTPS parametrizable con el contrato `decisions/noul`
usado por [`correr.py`](../tareas/20260922-220029-jev-porque-v2/correr.py):
`model`, `state`, `questions` en la solicitud; `model` y `answers` con probabilidades
`noul` en la respuesta. No es un adaptador genérico de chat: otro protocolo requiere
adaptar `enviar`/`solicitud`/`convertir`. Se usa sólo la biblioteca estándar de Python,
sin añadir dependencias a Oracle. El modelo efectivo y la fecha UTC de cada lote
quedan en las filas. Las respuestas guardadas conservan también el consumo que
informe el proveedor. No hay límite monetario automático; el lote usa 12 medidas
por solicitud y el catálogo elegido determina cuántas solicitudes se hacen.

El directorio de salida debe ser nuevo. Se guardan configuración, lote, solicitudes
y respuestas; la clave sólo va en el encabezado HTTP. No hay redirecciones ni
reintentos automáticos. Si falla el transporte, el formato, la cobertura de preguntas
o una probabilidad, termina con código 1 sin publicar `hechos.json` de una corrida
parcial. Revisá los artefactos y el consumo del proveedor antes de repetir una
corrida. Código 0 indica preparación completa o corrida sin filas en la zona media;
código 2 indica corrida completa con revisión pendiente, no un veredicto semántico.

## Qué prueba el ejemplo

El corpus es construido, no son respuestas observadas de un modelo: cubre ambas
polaridades, bordes, filtros, falta de relación y relación vacía. La mutación verifica
la sensibilidad de la política sobre esas filas. Las pruebas del adaptador simulan
HTTP y comprueban validación, revisión humana y fallas parciales sin llamadas reales.

No se añade un diferencial semántico: no hay una referencia independiente para
certificar estos textos. Copiar el juicio del mismo modelo como «referencia» sería
circular. El estudio conserva la comparación ciega limitada que sí se midió; no se
la presenta como un fixture universal del sensor de alcance. Una adopción necesita
su propio corpus observado y referencias humanas independientes.
