# El control del experimento: la misma batalla naval sin sugerir Oracle

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, experimento, agentes


## Por qué

El 2026-09-22 Brian corrió con agy un prompt que **sugiere** Oracle sin guiarlo, y el resultado
(`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280`) midió el juego de verdad: sensor propio,
11 medidas navales y una partida real de 130 tiros juzgada; Claude comprobó que tres mentiras
distintas en la evidencia caen con la medida correcta. Está anotado en
[`20260919-134424-naval-pm`](../20260919-134424-naval-pm/TAREA.md).

Falta la mitad que convierte eso en una medición y no en una anécdota: **la misma corrida sin la
frase que ofrece Oracle**. Sin control no se puede decir qué agrega Oracle ni qué cuesta, que es
justo lo que el postmortem del 18/09 no pudo demostrar en ninguna dirección.

## Los dos prompts

**A (con la oferta), el que ya se corrió:**

> Hacé una batalla naval jugable en HTML5, con la estructura que te parezca.
>
> Cuando la termines no me alcanza con que me digas que anda: quiero poder creerle al resultado.
> Mostrame cómo comprobás que las reglas del juego se cumplen de verdad, sobre una partida.
>
> Si te sirve, existe `pip install oracle-metalenguaje` (`oracle --help`). Usalo o no, como
> prefieras, y decime por qué.

**B (el control):** exactamente el mismo texto **sin el último párrafo**. No se agrega nada: la
diferencia entre A y B tiene que ser esa frase y nada más.

## Cómo correrlo

- Directorio vacío por corrida, fuera de los repos (`~/Dev/lab/naval-A-1`, `-A-2`, `-B-1`, `-B-2`).
- Mismo modelo y mismas opciones que la corrida que ya existe (agy, `--new-project`, sin más
  contexto); anotar modelo y fecha.
- **Dos corridas por rama**, porque con una sola no se distingue el efecto del azar del modelo.
- Guardar la respuesta final del agente y, si se puede, el registro de la sesión.

## Qué se mide (lo mismo en las cuatro)

1. **¿Se puede falsar?** Tomar la evidencia o el estado que produzca cada corrida y corromperla de
   tres maneras (un impacto registrado como agua, un agua como impacto, un tiro fuera del tablero).
   ¿Algo lo detecta? Es la pregunta central: en B habrá `assert` o comprobaciones dentro del mismo
   juego, y hay que ver si atrapan esas tres.
2. **Qué reglas quedan cubiertas**, listadas una por una, y cuáles no.
3. **Cuánto juego hay**: archivos, tamaño, qué funciona al abrirlo, qué falta (sonido, IA, colocación
   interactiva). Anotar lo que se ve, sin puntaje inventado.
4. **Qué costó**: turnos, tiempo y —si el registro lo dice— llamadas a herramientas, separando las
   que fueron al juego de las que fueron a la herramienta de verificación.
5. **Qué dijo el agente** sobre por qué eligió lo que eligió.

## Lo que el experimento NO puede decir

Con cuatro corridas y un solo modelo no se mide productividad en general. Lo que sí puede mostrar es
si, en el mismo pedido y con el mismo modelo, **el resultado sin Oracle resiste o no las tres
mentiras**. Si las resiste, Oracle aporta menos de lo que creemos acá y hay que decirlo; si no las
resiste, la diferencia está medida y no argumentada.

## Próximo paso

Brian corre B dos veces y A una más (ya hay una de A). Después, Claude o Codex aplican las tres
mentiras a las cuatro y escriben `vault-kb/estudios/NAVAL-CON-Y-SIN-ORACLE.md` con la tabla.

### Nota (2026-09-25 21:43:31 UTC)

2026-09-25 18:43: corridas lanzadas por Claude con agy 1.2.10 (modelo por omisión de agy), --new-project --mode accept-edits --print-timeout 3h, sin más contexto que el prompt, cada una en un directorio vacío: B-1 y después A-2 en ~/Dev/lab/naval-B-1 y naval-A-2 (agy1), B-2 en ~/Dev/lab/naval-B-2 (agy2). Los prompts son los de esta tarea, texto exacto; se guardan con la respuesta final en el scratchpad de la sesión y se copian acá al terminar. Diferencia con A-1: Brian la corrió a mano; ésta es no interactiva (-p).

### Nota (2026-09-25 21:52:33 UTC)

2026-09-25 18:51: el primer lanzamiento falló en 10 s sin crear nada: agy -p no puede pedir el permiso «command» y lo niega solo. Con OK de Brian, las tres corren dentro de un contenedor Docker (imagen agy-naval: python 3.13-slim + git, node, npm, curl, uv; red habilitada) con --dangerously-skip-permissions, montando sólo la carpeta vacía de la corrida, el binario de agy (sólo lectura) y una copia reflink de ~/.gemini por corrida. agy 1.2.11 (se actualizó solo entre el 1.2.10 del primer intento y éste). Diferencia a declarar en el estudio: A-1 corrió en el host, a mano; B-1, B-2 y A-2 en el contenedor, sin intervención.

### Nota (2026-09-25 22:00:17 UTC)

2026-09-25, ENCARGO del análisis (Codex, con shell), cuando termine A-2: las cuatro corridas están en ~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280 (A-1), ~/Dev/lab/naval-A-2, ~/Dev/lab/naval-B-1 y ~/Dev/lab/naval-B-2; las respuestas finales de B-1, B-2 y A-2 en el scratchpad (naval-*.respuesta) y se copian a esta carpeta. NO modificar las carpetas originales: trabajar sobre copias (cp -a a un temporal). Para cada corrida: (1) qué produce como evidencia o estado verificable; (2) aplicarle las tres mentiras —un impacto registrado como agua, un agua registrada como impacto, un tiro fuera del tablero— en lo que su propio mecanismo de comprobación mire (partida registrada, traza, estado), EJECUTANDO su verificación (tests, scripts, oracle) antes y después; si el mecanismo no mira ninguna partida registrada (sólo prueba el motor), decirlo y mostrar que la mentira no es representable o no se detecta; (3) reglas cubiertas una por una y cuáles no; (4) cuánto juego hay, sin puntaje inventado; (5) costo si hay registro; (6) qué dijo el agente sobre su elección. Escribir vault-kb/estudios/NAVAL-CON-Y-SIN-ORACLE.md con la tabla y lo que el experimento NO puede decir (sección de la tarea), y declarar las diferencias de método (A-1 en el host a mano; las otras en contenedor, no interactivas, agy 1.2.11).
