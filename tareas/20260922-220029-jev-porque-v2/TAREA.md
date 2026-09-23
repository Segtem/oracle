# El porque no se pudo juzgar: la pregunta estaba mal y al modelo le faltaba la medida

- ESTADO: ABIERTA
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

## Próximo paso

Entregar `paquete-ciego-claude.zip` a Claude en una sesión nueva y sin acceso al
repositorio ni a los resultados anteriores. La solicitud exacta está en
`ciego/INSTRUCCIONES.md`; no entregar esta tarea ni `clave-operador.json` al juez.
Guardar su `juicio-ciego-claude.json`, versión, fecha, declaración de exposición
previa y SHA-256 antes de cualquier llamada a Jev. Éste es el bloqueo actual:
falta ese juicio independiente; Codex se detiene aquí por instrucción del usuario.

Una vez recibido, validar IDs completos, booleanos, justificaciones y P2 null
cuando no aplica; implementar la corrida con el criterio íntegro y `lote.json`,
sin enviar claves ni el juicio. Respetar `protocolo.json` (tope USD 0,05), guardar
solicitudes/respuestas y costos, comparar por pregunta y controles, y publicar la
segunda corrida en `estudios/JEV-COMO-SENSOR.md`, incluso si falla. La muestra
real no permite estimar acuerdo de P2: los 15 umbrales son cero. No cambiarla a
posteriori para ocultar ese límite. Revalidar artefactos con
`python3 tareas/20260922-220029-jev-porque-v2/preparar.py --verificar`.

### Nota (2026-09-23 00:03:25 UTC)

2026-09-22, Claude, dos observaciones antes del juicio: (1) NO puedo ser yo el juez ciego de esta segunda corrida: hice el juicio de la primera, conozco sus resultados (alcance 15/15, porque 1/15), el diseño y qué son los controles; las propias INSTRUCCIONES piden una sesión nueva sin acceso a nada de eso. Lo delegué a un agente limpio, sin esta conversación, que sólo lee CRITERIO.md, INSTRUCCIONES.md y registros.json. (2) Las 25 entradas del lote tienen umbral <= 0, así que la pregunta P2 (por qué ese valor y no uno vecino) no se puede evaluar en esta corrida: queda 'no aplica' en las 25. Es un límite del catálogo de Oracle, que casi no tiene umbrales distintos de cero; si se quiere probar P2 hay que traer prosa de un proyecto con umbrales numéricos (LyraGASP y Jam tienen varios) o construir controles con umbral distinto de cero.
