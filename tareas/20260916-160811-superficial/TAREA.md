# El tracker no avisa cuando la historia de git es superficial y cuenta commits de menos

- ESTADO: ABIERTA
- PRIORIDAD: 65
- ETIQUETAS: oracle, tracker, ci


Medido el 2026-09-16 en el CI del corte 0.25.2: `actions/checkout@v4` clona con `fetch-depth: 1`, y
`oracle tarea hechos --git` emitió un solo `commit_seguimiento`. La política
`seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre` contó 30 tareas cerradas sin su `done`
(localmente, 5). El número salió mal y nada dijo por qué: parecía deuda del tracker.

Arreglado el síntoma en los dos workflows con `fetch-depth: 0`. Falta la causa: una historia
superficial es evidencia incompleta, y el emisor tiene que declararlo como omisión
(`git rev-parse --is-shallow-repository` en `tools/tareas_git`), para que la lectura quede roja en
vez de contar de menos en silencio.
