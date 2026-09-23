# Un patrón para que un proyecto use un modelo como sensor de su prosa, sin que Oracle dependa de él

- ESTADO: CERRADA
- PRIORIDAD: 72
- ETIQUETAS: oracle, sensores, metalenguaje, jev


## La decisión de diseño, primero

Oracle **no** va a llamar a un modelo ni a depender de una clave: hoy corre sin red y su veredicto es
reproducible, y eso es lo que lo hace creíble. Lo que puede llevar es el **patrón** para que un
proyecto lo haga por su cuenta, igual que los sensores de Unreal: el sensor vive afuera, Oracle
juzga lo que el sensor emite.

Sale de `20260922-190222-jev-prueba`: sobre `alcance`, un modelo barato acertó 15/15 y atrapó 10 de
10 controles de prosa vacía, por menos de un décimo de centavo. Hoy Oracle sólo comprueba que
`alcance` no esté **vacío**; que diga algo concreto no lo comprueba nadie.

## Qué hacer

1. **La relación declarada** `afirmacion_prosa` en `relaciones/`: `medida`, `pregunta`, `respuesta`
   (booleano), `probabilidad` (flotante, `sin_unidad`), `modelo`, `fecha`. Con su `alcance` diciendo
   qué NO ve: que la respuesta la produjo un modelo y no una persona.
2. **Una medida de ejemplo** —en `ejemplo/`, no en el catálogo que obliga a todos— que la juzgue:
   por ejemplo, ninguna medida con una afirmación adversa de alta probabilidad sobre su `alcance`.
   Con su corpus de las dos polaridades. En su `alcance`, sin vueltas: **estas filas las produjo un
   modelo probabilístico; el umbral de probabilidad es una decisión, no un hecho**.
3. **El sensor, afuera y opcional**: un script de ejemplo (`ejemplo/…/sensor_prosa.py`) que arme el
   lote desde un catálogo y llame a un modelo por HTTP, con la clave en el entorno. Que funcione con
   Jev por OpenRouter y que el proveedor sea un parámetro, no una dependencia. Reusar lo que ya
   escribió Codex en `tareas/20260922-190222-jev-prueba/`.
4. **Documentarlo** en `docs/` como lo que es: una forma de convertir prosa en hechos, con sus
   límites, y la advertencia de que un sensor probabilístico no es un juez.
5. **No tocar el catálogo que obliga**: ningún proyecto debería ponerse rojo por esto sin haberlo
   elegido.

## Cuándo entra

Cuando `jev-porque-v2` cierre, para que el patrón nazca sabiendo qué parte de la prosa se puede
delegar y cuál no. Corte candidato: 0.30.0.

## Avance

El patrón vive íntegramente en `ejemplo/sensor-prosa/`, con `catalogo_base: false`,
relación local y medida `del_origen`. No modifica el catálogo obligatorio.

- Corpus construido: 15 casos de ambas polaridades, bordes 0,2/0,8, filtros,
  señal intermedia y relación ausente/vacía. `requiere` rechaza ambas como SIN EVIDENCIA.
- Sensor opcional `sensor_prosa.py`: protocolo HTTP decisions/noul reutilizado de
  `jev-porque-v2`, con proveedor, modelo y nombre de variable de clave parametrizables.
  Prepara sin red; sólo `correr` consume API. Envía también tubería y resumen.
- Publica evidencia sólo al completar todos los lotes y validar todas las respuestas.
  Conserva respuestas y consumo informado; sin reintentos ni redirecciones.
  La zona 0,4–0,6 inclusive queda en `revision-humana.json` y produce salida 2.
- Documentación en `docs/14-sensor-prosa.md`, enlazada desde docs y el ejemplo:
  sensor probabilístico no es juez; cortes elegidos por el proyecto; calibración
  observada de `porque` con dos casos en 0,50; no extrapolarla a `alcance`.
- Sin diferencial semántico: no hay referencia independiente aplicable al ejemplo.
  La comparación ciega del estudio no se presenta como fixture universal.
- Siete pruebas offline del adaptador y de las polaridades del corpus. Ninguna
  llamada real al proveedor en esta entrega. No se hicieron commits.

### Nota (2026-09-22 22:16:08 UTC)

2026-09-22, revisión de Claude sobre la entrega de agy: la relación y el alcance están bien escritos, pero las dos ubicaciones estaban mal y una era seria. (1) afirmacion_prosa.json quedó en relaciones/, que son las relaciones que Oracle DISTRIBUYE a todos los proyectos: es lo mismo que hizo chocar a Jam con pieza. (2) ejemplo/oracle.json y ejemplo/catalogos/ convertían ejemplo/ —que es una carpeta de proyectos de ejemplo— en un proyecto. Todo se movió a ejemplo/sensor-prosa/, con catalogo_base en false. Además la medida se declaraba de ambito universal y pasó a del_origen: obliga a su proyecto, no a quien la herede. oracle test del ejemplo da ROJO sólo por falta de casos, que es el paso siguiente.

### Nota (2026-09-23 11:17:17 UTC)

Patrón completado en ejemplo/sensor-prosa: 15 casos construidos de ambas polaridades, bordes 0,2/0,8 y evidencia ausente/vacía; oracle test del ejemplo VERDE, 35/35 mutantes muertos. Sensor opcional adaptado del protocolo decisions/noul de jev-porque-v2, proveedor/modelo/variable de clave parametrizables, preparación sin red, lotes de 12 con tubería, validación estricta y publicación sólo completa. Zona 0,4–0,6 inclusive guardada para revisión humana con salida 2. Documentación docs/14-sensor-prosa.md enlazada: no es un juez, cortes por decisión del proyecto, calibración de porque 0,50–0,68 vs 0,09–0,33 con dos 0,50; sin extrapolarla a alcance. Sin diferencial semántico por falta de referencia independiente aplicable; motivo documentado. Pruebas offline del adaptador y suite estándar en verificación; ninguna llamada real ni commits. Cambios ajenos de timeout-suite-mutacion preservados.

### Nota (2026-09-23 11:20:50 UTC)

Verificación final completada: python3 tools/cli.py test --proyecto ejemplo/sensor-prosa sale 0 VERDE (15 casos; 6 defectos rojos y 9 verdes correctos; 35/35 mutantes muertos). python3 tools/cli.py test sale 0 VERDE: 2411 unitarios OK, corpus/sintaxis/aceptación/diferencial/autocertificación/cifras en regla y 1010/1010 mutantes de medidas muertos. Logs íntegros en verificacion/oracle-test-ejemplo.log y verificacion/oracle-test.log. Siete pruebas propias offline pasan; preparación de 62 medidas del catálogo completo sin red comprobada. Se corrigió la expectativa del caso vacío: requiere produce SIN EVIDENCIA, igual que relación ausente. README regenerado con herramientas del repo para reflejar cifras actuales, incluidas las modificaciones preexistentes de timeout-suite-mutacion. No se ejecutó --todo ni se declara verde su mutación de código: ese pendiente sigue en timeout-suite-mutacion. git diff --check OK. Sin llamadas reales ni commits.

## Próximo paso

El patrón está terminado y verificado con el ejemplo y la suite estándar en verde;
revisar los cambios para su integración cuando corresponda, sin hacer commits en
esta sesión. La adopción por un proyecto debe fijar sus cortes y registrar la
revisión humana de la zona intermedia. No hay llamadas a API pendientes para completar
este ejemplo. La mutación de código completa (`--todo`) sigue en la tarea existente
`20260922-221412-timeout-suite-mutacion`; continuar allí, sin atribuirle el verde
de la suite estándar registrado en esta tarea.
