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

## Próximo paso

Codex escribe las preguntas nuevas y los ejemplos de cada lado, y pide el juicio a ciegas de Claude.
