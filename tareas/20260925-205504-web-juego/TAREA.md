# La web: manual en la estética pixel, cómo funciona Oracle con rigor, y la batalla naval de cero como un juego que enseña

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: oracle, documentacion, web

### Nota (2026-09-25 21:22:52 UTC)

2026-09-25: hecho y publicado — el manual con la estética del sitio; «Cómo funciona Oracle» (docs/como-funciona.md) con cada salida ejecutada por guia.py, incluido un paso «bash paso falla»; la guía de la batalla naval como juego (assets/guia.js): nueve misiones con objetivo y XP, nueve predicciones cuya respuesta un test ata al veredicto real de la salida, la pregunta hecho-u-opinión, el tablero que evalúa la forma canónica real de naval.barcos_dentro_del_tablero, y la cacería con los 18 mutantes y la matriz de detección que calcula nucleo.mutacion al generar la página (8 vivos con 005, 4 con 006, 0 con los cinco: igual que las salidas de la guía). Probado en Chromium headless por CDP (script en el scratchpad, no en el repo: CI no tiene navegador) y sin desborde a 400 px. Sale de acá la tarea caso-silencioso (cerrada). Antes del próximo corte: mutar tools/aceptacion.py, tools/juzgar.py, nucleo/medida.py y tools/manual.py, que cambiaron; guia.js y el CSS no tienen mutación.
