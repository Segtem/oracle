# el tutorial de batalla naval recrea el juego entero y recorre todo Oracle, requisitos y cambios incluidos

- ESTADO: CERRADA
- PRIORIDAD: 81
- ETIQUETAS: 

### Nota (2026-09-30 21:53:05 UTC)

Por qué: docs/de-cero.md (nueve misiones) arma la batalla naval entera desde una carpeta vacía y la juzga, pero se escribió antes de 0.35.0: no usa requisitos, oracle cobertura (--con), oracle cambios ni oracle requisito importar. Qué: 1) verificar que el tutorial recrea el juego ENTERO desde cero (todos los archivos de ejemplo/batalla-naval llegan por bloques incluir= y el test de la guía lo prueba); 2) sumar al recorrido las promesas del juego como requisitos, cobertura --con sobre la partida real, y oracle cambios atrapando una regla aflojada; 3) que siga siendo para alguien que recién empieza. Encargado a Codex.

### Nota (2026-09-30 22:05:06 UTC)

Completé el recorrido: seis requisitos navales cubren las once medidas y declaran la forma recta sin medir; la guía ejecuta cobertura y cobertura --con sobre la partida real, y cambios detecta un umbral aflojado con el mismo porque. Añadí bloques incluir para README y verificar_oraculo.py, adapté ese script para usar oracle instalado fuera del repo, y test_guia comprueba el inventario completo de archivos del ejemplo y sus destinos desde una carpeta vacía. El arnés admite sólo los comandos Git usados en el paso. Actualicé cifras generadas en README.md. Verificaciones: guia.py pasó; test_guia pasó (4); suite completa ejecutada, 2248 tests con 2 fallas por docs/de-cero.html desactualizado; oracle.py test VERDE ejecutado, ROJO sólo por esos unitarios, con cifras OK y mutación de código salteada. No regeneré HTML ni hice commits: Claude debe regenerar docs/de-cero.html y repetir los dos gates.

## Próximo paso

Cuando Claude regenere `docs/de-cero.html` al unir sus cambios, ejecutar `python3 -m unittest discover -s tests` y `python3 tools/oracle.py test VERDE`; si ambos pasan, cerrar esta tarea según el protocolo del repo.

### Nota (2026-09-30 22:15:37 UTC)

Unido por Claude: el test test_la_batalla_naval_entera_llega_por_incluir comprueba que todo archivo de ejemplo/batalla-naval llega a la guía por incluir=; guia.py acepta tres comandos git exactos para que oracle cambios tenga contra qué comparar (mutación de esas líneas 18/18). La guía suma seis requisitos, oracle cobertura (--con) sobre la partida real y oracle cambios atrapando tiros_sin_repeticion aflojado a <= 1 con el mismo porque. Suite 2248 OK, oracle test VERDE.
