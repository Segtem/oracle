# revisión del tutorial de batalla naval por alguien que empieza de cero

- ESTADO: CERRADA
- PRIORIDAD: 79
- ETIQUETAS: 

### Nota (2026-09-30 21:53:05 UTC)

Por qué: que una guía pase su test no dice que alguien nuevo la pueda seguir. Qué: seguir docs/de-cero.md al pie de la letra en un contenedor limpio (imagen agy-naval, carpeta vacía, sin el repo de Oracle), instalando oracle-metalenguaje==0.38.0 desde PyPI, y anotar cada lugar donde se trabó, dudó o vio otra cosa que la guía dice, citando la línea de la guía. No edita la guía. Encargado a agy2.

### Nota (2026-09-30 22:15:37 UTC)

agy2 siguió la guía (con los archivos incluidos, como en el sitio) en un contenedor vacío con oracle-metalenguaje==0.38.0 de PyPI: armó el juego entero y llegó a juzgar una partida (11 medidas verdes); informe en INFORME-agy2.md, 5 citas con número de línea verificadas por script. Arreglado en la guía: crear corpus/naval y catalogos/naval (oracle init no las crea); mover hechos_partida.json de Descargas a la carpeta del proyecto; qué hace el python3 -c del paso 8. No se tocó: versión sin fijar en la instalación (la guía sigue la última), ruta absoluta que imprime oracle init (la salida se normaliza), terminales sin escritorio (fuera del público), los 26 casos del paso 7 a mano (es el punto de la misión).
