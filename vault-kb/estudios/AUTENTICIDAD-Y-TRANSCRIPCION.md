# Una relectura correcta no demuestra una ejecución pasada

**2026-09-10 · fase 3 de PLAN-0.14-LO-QUE-FALTA**

## Resultado y premisa

Recomendación: conservar `autenticidad.comprobada: false` y explicar la distinción entre
coherencia, relectura actual e historia. El recorrido permite comprobar la coherencia del registro
con su evidencia y sus referentes declarados, y ejecutar hoy el sensor para comparar resultados.
Eso no demuestra por sí solo quién produjo los bytes guardados ni cuándo los produjo.

**Premisa del resultado:** el adversario puede escribir el registro y acceder a los mismos
referentes que Oracle. No tiene que romper una huella criptográfica: puede construir los datos y
sus huellas juntos. Este estudio no supone que pueda modificar una custodia externa independiente.

## Qué se midió

El experimento reproducible está en [contrastar_autenticidad.py](contrastar_autenticidad.py).
Se ejecuta desde cualquier directorio con `python3 -B <ruta>/contrastar_autenticidad.py`.
Usa el consumidor temporal de `tests.test_observar.Consumidor`; no toca ningún corpus real.

1. Captura una ejecución real y conserva sus bytes de evidencia.
2. Sustituye solamente `correr_sensor` por una transcripción de esos bytes y de su salida.
   Construye otro registro mediante `capturar`, con los mismos validadores y huellas reales.
3. Retira la sustitución y ejecuta `revalidar` sobre el registro construido.

El resultado es dos ejecuciones sustituidas, captura aceptada, relectura real `sin_cambios: true`
y `autenticidad.comprobada: false`. La comprobación individual distingue así dos historias que el
verificador no puede distinguir. Es un **experimento construido**, no un caso observado del dominio
ni una reclasificación de evidencia vieja.

La conclusión alcanza a este recorrido y a esta autoridad del adversario. Se midió una pareja de
historias con el consumidor mínimo; no se midieron otros sensores, sistemas de custodia ni ataques
contra firmas o funciones de huella. No se estima pequeño ninguno de esos espacios sin medir.

## Las tres posibilidades del plan

**Huella tomada por el sensor al leer.** Bajo la premisa de que el sensor ejecutado es confiable,
puede vincular mejor la evidencia con los bytes que leyó y reducir una carrera entre lectura y
recorrido posterior. Bajo la premisa del adversario anterior, éste conoce esos bytes y puede
calcular esa misma huella sin ejecutar el sensor. No prueba historia. No se implementó ni midió
una modificación del sensor; ésta es una consecuencia del modelo de autoridad, no una cifra de
resistencia observada.

**Desafío externo imprevisible.** Bajo la premisa de que el desafío todavía no es conocido, impide
preparar de antemano una transcripción que lo incluya. Si después el autor puede construir tanto
la respuesta como la evidencia, incorporar el desafío no demuestra que ejecutó el sensor. Una
custodia independiente que ejecute código identificado y conserve desafío, respuesta y tiempos
cambia esa premisa. No se descarta: requiere otra autoridad y otro modelo operativo, que este
experimento no evalúa.

**Acotar la afirmación actual.** Es la opción recomendada para el recorrido local. Las huellas
vinculan archivos declarados; la revalidación compara con una ejecución actual. Ni siquiera la frase
«esta evidencia existió en este momento» debe atribuirse a un registro editable como certificación
independiente de fecha: el momento también está declarado por la misma autoridad.

Una firma con una clave del propio proyecto demuestra autoría bajo confianza en esa clave.
No demuestra que el autor ejecutó el sensor: puede firmar la transcripción del experimento.

## Contraargumento

Aceptar el límite no satisface a quien necesita acreditar una ejecución ante terceros. Una
custodia independiente sí puede aportar una garantía que Oracle local no tiene. Por eso la
recomendación no es declarar inútil la autenticidad: es mantener honesta la afirmación disponible y
pedir un caso de uso con autoridad y adversario explícitos antes de incorporar infraestructura.
El estudio cierra la pregunta de implementación inmediata, no promete haber resuelto esa garantía.
