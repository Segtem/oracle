# el tutorial de batalla naval recrea el juego entero y recorre todo Oracle, requisitos y cambios incluidos

- ESTADO: ABIERTA
- PRIORIDAD: 81
- ETIQUETAS: 

### Nota (2026-09-30 21:53:05 UTC)

Por qué: docs/de-cero.md (nueve misiones) arma la batalla naval entera desde una carpeta vacía y la juzga, pero se escribió antes de 0.35.0: no usa requisitos, oracle cobertura (--con), oracle cambios ni oracle requisito importar. Qué: 1) verificar que el tutorial recrea el juego ENTERO desde cero (todos los archivos de ejemplo/batalla-naval llegan por bloques incluir= y el test de la guía lo prueba); 2) sumar al recorrido las promesas del juego como requisitos, cobertura --con sobre la partida real, y oracle cambios atrapando una regla aflojada; 3) que siga siendo para alguien que recién empieza. Encargado a Codex.
