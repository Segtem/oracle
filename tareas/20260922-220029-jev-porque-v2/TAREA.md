# El porque no se pudo juzgar: la pregunta estaba mal y al modelo le faltaba la medida

- ESTADO: CERRADA
- PRIORIDAD: 75
- ETIQUETAS: oracle, sensores, jev, experimento


## De dónde sale

`20260922-190222-jev-prueba` (cerrada): con 216 respuestas por US$ 0,00088, Jev atrapó **10 de 10**
controles de prosa vacía y coincidió **15/15** en las dos preguntas sobre `alcance`. En `porque`
coincidió **1 de 15**, y el análisis mostró dos causas probables, ninguna de ellas «el modelo no
sirve»:

1. **La pregunta estaba mal formulada.** «¿El `porque` explica por qué ESE número y no otro?» es
   injusta para un umbral contractual de cero: esas defensas justifican la REGLA («ninguna ausencia
   es aceptable»), y de ahí se sigue el cero. Claude las dio por buenas; Jev pidió que el texto
   defendiera el número. Los dos criterios son defendibles, así que la pregunta no distinguía nada.
2. **Al modelo le faltaba la medida.** Recibió prosa, umbral y `segun`, pero no la tubería. Sin saber
   qué mide, no puede juzgar si la defensa corresponde.

Además, las 14 discrepancias tuvieron probabilidad entre 0,12 y 0,47: el modelo **nunca afirmó con
confianza**, dudó. Esa calibración es parte del resultado.

## Qué hacer (Codex)

1. **Reescribir la pregunta**, separándola en dos que sí se puedan contestar:
   - ¿La defensa dice de dónde sale el número, o sólo por qué la regla importa?
   - Para un umbral distinto de cero: ¿la defensa explica por qué ese valor y no uno vecino?
   Dejar escrito el criterio con dos ejemplos de cada lado **antes** de correr nada.
2. **Mandar también la tubería** de la medida (forma canónica o superficie), no sólo la prosa.
3. **Juicio a ciegas primero**: Claude vuelve a responder la muestra con las preguntas nuevas, sin ver
   nada del modelo. Pedírselo y esperar; no inventarlo.
4. Mismos controles rojos, mezclados y sin marcar, y las mismas cifras: acuerdo, controles, costo.
5. Escribir el resultado en `estudios/JEV-COMO-SENSOR.md`, como segunda corrida, **incluso si vuelve
   a fallar**: un segundo fracaso con la pregunta arreglada es la conclusión de que esa prosa no se
   delega, y eso cierra el tema.

La clave sigue en `$OPENROUTER_API_KEY`; gastar centavos y anotar el costo.


### Nota (2026-09-22 22:12:14 UTC)

Preparación v2 lista sin llamadas a modelos (costo USD 0). CRITERIO.md fija dos preguntas y dos ejemplos por polaridad para cada una. preparar.py conserva las 62 medidas y los 10 controles anteriores, añade tubería/resumen y mezcla con ids nuevos. paquete-ciego-claude.zip contiene sólo criterio, instrucciones, 15 reales + 10 controles sin marcar y plantilla vacía; no contiene clave ni resultados. Las 15 reales son de umbral cero: P2 no aplica y su acuerdo no será estimable; sólo una medida no cero queda fuera de la muestra, limitación fijada antes del juicio. Cuatro pruebas del paquete pasan y oracle test da VERDE con 2401 unitarios OK y 1010/1010 mutantes de medida muertos; verificación adicional --todo en curso. Bloqueo deliberado: falta juicio independiente de Claude en sesión nueva, pedido por la tarea; no se inventó ni se lanzó Jev. Se conservaron los cambios ajenos preexistentes y no se hicieron commits.

### Nota (2026-09-22 22:14:12 UTC)

Verificación final: 4/4 pruebas del paquete, integridad SHA-256 y git diff --check OK. oracle test sale 0: 2401 tests OK (83,193 s), corpus/sintaxis/aceptación/diferencial/autocertificación verdes y 1010/1010 mutantes de medida muertos. oracle test --todo sale 1: sus 2401 unitarios también pasan (82,645 s), pero la línea base de mutación de código expira a los 60 s (LineaBaseFallida; 1235 tests alcanzados). No es verde completo de --todo y no se generó evidencia válida de mutación de código. Logs íntegros en verificacion/oracle-test.log y oracle-test-todo.log. Se registra pendiente separado timeout-suite-mutacion; no se alteró el arnés fuera del alcance de preparar el juicio ciego. Paquete listo, gasto cero, sin commits.

### Nota (2026-09-23 00:03:25 UTC)

2026-09-22, Claude, dos observaciones antes del juicio: (1) NO puedo ser yo el juez ciego de esta segunda corrida: hice el juicio de la primera, conozco sus resultados (alcance 15/15, porque 1/15), el diseño y qué son los controles; las propias INSTRUCCIONES piden una sesión nueva sin acceso a nada de eso. Lo delegué a un agente limpio, sin esta conversación, que sólo lee CRITERIO.md, INSTRUCCIONES.md y registros.json. (2) Las 25 entradas del lote tienen umbral <= 0, así que la pregunta P2 (por qué ese valor y no uno vecino) no se puede evaluar en esta corrida: queda 'no aplica' en las 25. Es un límite del catálogo de Oracle, que casi no tiene umbrales distintos de cero; si se quiere probar P2 hay que traer prosa de un proyecto con umbrales numéricos (LyraGASP y Jam tienen varios) o construir controles con umbral distinto de cero.

### Nota (2026-09-23 00:09:43 UTC)

Segunda corrida ejecutada con CRITERIO.md íntegro y los 72 registros congelados con tubería; los 25 del juicio son subconjunto idéntico. Referencia validada y SHA-256 afb4f78d0bd0a21eb18ce75aed00c2aa735599e68125e9e31456974e4c1cb574 sellado antes de llamadas; sesión limpia confirmada por usuario, versión exacta y fecha del juicio no constan. Jev typesafe/jev-1.13-20260917: P1 15/15 reales (7 sí, 8 no), controles 10/10, total 25/25. P2 no evaluable: las 25 entradas tienen umbral <= 0, límite cero; única respuesta no cero en lote completo (v003, 0,40) sin referencia. Seis HTTP 200, 73 respuestas, sin reintentos: USD 0,001443666 (0,1443666 centavos), 7,503 s. Calibración descriptiva: Brier reales 0,122093 y total 0,073744; ECE 0,324 y 0,208, seis positivos cerca de 0,5 y dos exactamente en el corte. No adopción automática. Informe publicado como segunda corrida en estudios/JEV-COMO-SENSOR.md; solicitudes, respuestas, costos y análisis reproducible guardados. Suite estándar python3 tools/cli.py test salida 0 VERDE, 2401 unitarios OK y 1010/1010 mutantes de medidas; 4/4 pruebas de paquete e integridad OK. No se repitió --todo ni se declara verde su mutación de código: timeout previo sigue en timeout-suite-mutacion. Sin commits.

## Próximo paso

La segunda corrida y su informe están completos; revisar el resultado en
`estudios/JEV-COMO-SENSOR.md` y cerrar administrativamente esta tarea cuando
corresponda, sin lanzar nuevas llamadas ni hacer commits en esta sesión.
No queda pendiente una comparación de P2 con este lote: su denominador es cero.
La mutación de código completa sigue pendiente por el timeout ya registrado en
`20260922-221412-timeout-suite-mutacion`; continuar allí el arreglo del arnés
y su verificación, sin confundir el verde de la suite estándar con `--todo`.

### Nota (2026-09-23 00:11:11 UTC)

2026-09-22, revisión de Claude: comprobé la comparación por mi cuenta y da lo que informa Codex — 15/15 en las reales, 10/10 controles, y usa el juicio ciego comiteado. Pero la separación es angosta y hay que decirlo: los 'sí' caen entre 0,50 y 0,68, los 'no' entre 0,09 y 0,33, y DOS de los sí están exactamente en 0,50. Con un corte en 0,5 esos dos se deciden por el redondeo; con 0,55 se pierden dos verdaderos. O sea: la señal existe y el orden es correcto, pero no hay margen para un umbral fijo. Si esto se usa alguna vez, el umbral es una decisión del proyecto y la zona 0,4-0,6 debería mandarse a revisión humana en vez de decidirse sola. La conclusión de fondo cambia respecto de la primera corrida: el problema era la pregunta y la falta de la tubería, no el modelo.
