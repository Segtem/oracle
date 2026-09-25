# Batalla naval con y sin la oferta de Oracle

Estudio del encargo de `20260922-200806-naval-control`, ejecutado el 2026-09-25. La variable del prompt es el último párrafo de A, que ofrece `oracle-metalenguaje`; B lo omite. Las cuatro carpetas originales quedaron intactas. Copié cada corrida a `/tmp/naval-control-analisis.37aGY9/` y ejecuté las pruebas y mutaciones allí. Para A-2 tomé una segunda copia tras su salida 0.

## Resultado observado

| Corrida | Evidencia que produjo | Base ejecutada en la copia | Impacto anotado como agua | Agua anotada como impacto | Tiro fuera del tablero |
| --- | --- | --- | --- | --- | --- |
| A-1, con oferta | `partida_real.json`: 130 tiros, 34 celdas de barco, resultado final; 11 medidas Oracle | `oracle juzgar --con partida_real.json`: verde en 11 | Rechazado, `naval.veracidad_impacto_negativo`, salida 1 | Rechazado, `naval.veracidad_impacto_positivo`, salida 1 | Rechazado, `naval.tiros_dentro_del_tablero`, salida 1 |
| A-2, con oferta | `partida_js_hechos.json`: 98 tiros y 34 celdas; también `partida_hechos.json`: 94 tiros desde el simulador Python; 12 medidas Oracle | `oracle juzgar` sobre ambos JSON: verde en 12. `oracle test --rapido`: 12 casos rojos y 12 verdes aceptados | Rechazado en JSON de JS, `batalla_naval.falso_agua`, salida 1 | Rechazado, `batalla_naval.falso_tocado`, salida 1 | Rechazado, `batalla_naval.sin_disparos_fuera_de_tablero`, salida 1 |
| B-1, sin oferta | Partida construida por `run-verification.js`, con `moveHistory` en memoria; no exporta una partida | `npm run verify`: salida 0, 37 movimientos; `npm test`: salida 0 | **No detectado** al cambiar `moveHistory[].result`: `npm run verify` siguió en 0 | **No detectado** en `moveHistory`: salida 0 | **No detectado** al cambiar `moveHistory[].r` a 10: salida 0 |
| B-2, sin oferta | Partida simulada de 105 tiros con `board.attacks` y `game.history` en memoria; no exporta partida | `npm run verify-match`: salida 0; `npm test`: 14 pruebas pasaron | **Detectado en estado** al cambiar `board.attacks`: salida 1; **no detectado en `game.history`**: salida 0 | **Detectado en estado**: salida 1; **no detectado en historial**: salida 0 | **Detectado en estado**: salida 1; **no detectado en historial**: salida 0 |

En A-1 y A-2 cambié **un campo de un tiro existente** en cada JSON, sin alterar las demás filas. En A-1 los turnos mutados fueron 4, 0 y 0; en A-2 (evidencia del motor JS), 9, 1 y 1. Para B-1 inserté la alteración en el script copiado inmediatamente después de `game.attack`, antes de que continuaran sus `check`: el script compara el resultado devuelto y el tablero contra expectativas codificadas, pero sólo lee `moveHistory` al final para mostrar su longitud. El verde de B-1 no prueba que el historial sea veraz.

Para B-2 inserté cada alteración inmediatamente después de `game.attack` y antes de `GameAuditor.auditGameInvariants`. Al convertir un impacto del tablero en `miss`, reportó “había un barco allí” y discrepancia de conteos; al convertir agua en `hit`, reportó que no correspondía a un barco y discrepancia de conteos; con la clave `(10,0)` reportó coordenada inválida. Repetí las tres alteraciones en `game.history`, que es la traza que conserva los eventos: las tres ejecuciones terminaron en 0 porque el auditor sólo usa ese historial para comprobar alternancia de tiradores. Así, B-2 **sí** inspecciona el estado vivo de una partida, pero su historial de resultados y coordenadas puede mentir sin disparar esas comprobaciones.

## Reglas cubiertas y huecos

La tabla indica qué comprobé que evalúa el mecanismo ejecutado, no toda propiedad que el motor pueda implementar. `S` significa medida sobre evidencia exportada; `E`, aserción o auditoría sobre estado del juego; `P`, prueba de un caso del motor. `—` indica que no encontré esa comprobación en la verificación ejecutada.

| Regla | A-1 | A-2 | B-1 | B-2 |
| --- | --- | --- | --- | --- |
| Casillas de barcos dentro de 10×10 | S | S | E/P | E/P |
| Cinco barcos con tamaños 5, 4, 3, 3, 2 | S: exige 17 celdas por bando, **no** composición | S: tamaños permitidos y conteo por barco, **no** exige exactamente esa flota | E/P: cinco barcos y 17 celdas de la flota creada | E/P: cinco barcos, tamaño por tipo y 17 celdas |
| Barcos sin solapamiento | S | S | P; la partida usa posiciones fijas | E/P |
| Barcos rectos y contiguos | — | — | P para colocación válida; no auditoría independiente de la partida | P para colocación; no auditoría de geometría independiente |
| Tiros dentro del tablero | S | S | P de rechazo por el motor; no inspecciona historial | E/P sobre `board.attacks`; no sobre historial |
| Tiros sin repetición | S | S | E/P en el motor; no inspecciona historial | E/P sobre tablero; no sobre historial |
| Impacto y agua fieles a la posición rival | S, positivo y negativo | S, `tocado` y `agua`; no cruza `hundido` como resultado de tiro | E: compara resultados devueltos con plan fijo para J1; no inspecciona historial | E: compara `board.attacks` con barcos; no compara `history[].result` |
| Hundimiento sólo tras todos los impactos | — en las 11 medidas | S por banderas y conteos de barcos; no recalcula la secuencia completa | E/P en motor | E/P en tablero |
| Alternancia de turnos | S | — en las 12 medidas | E/P en motor | E/P; usa tiradores de `game.history` |
| Turnos sin huecos | S por cantidad y máximo, no orden completo | — | — sobre historial | — sobre historial |
| Sin tiros tras terminar | S comparando turno con `turno_final` | S leyendo `efectuado_post_fin`, sin reconstruir el instante real | E/P: rechaza nuevos ataques | P del motor; auditoría en vivo no recorre eventos posteriores |
| Ganador respaldado por 17 impactos | S sobre contador declarado | S: exige al menos 17 en contador declarado | E/P sobre estado del motor | E/P sobre estado del tablero |

Dos límites transversales importan: los sensores y motores producen los hechos que luego se comprueban; un veredicto verde no acredita que una partida de navegador haya sido presenciada por una fuente externa. En A-2 varias medidas dependen de campos ya calculados (`impactos_recibidos`, `efectuado_post_fin`, `impactos_a_cpu`), y en A-1 la composición y geometría no quedan acreditadas por contar 17 celdas. En B-1 la “partida real” del script es una secuencia planeada contra un rival IA, no una partida de usuario preservada como evidencia. En B-2 la simulación usa semilla fija, pero el historial puede diferir del tablero sin aviso del auditor.

## Producto y ejecución

| Corrida | Archivos y tamaño de la carpeta original | Juego y carencias observables en código/ejecución |
| --- | --- | --- |
| A-1 | 23 archivos, 131 441 bytes | HTML/CSS/JS, motor, IA, colocación manual y automática, audio Web Audio, panel y exportación de traza. Se ejecutó el juicio de su partida JSON; no se completó una partida manual en navegador en este análisis. |
| A-2 | 48 archivos de fuente/datos, 186 201 bytes (sin `__pycache__`) | HTML/CSS/JS, colocación manual/aleatoria, IA, audio, auditor web, simulador Python y dos partidas JSON. Ejecuté el verificador Python en la copia **tras sustituir su ruta rígida `/work` por la de la copia**; terminó con sus seis mutantes detectados. La ruta rígida impide ejecutar ese script tal cual desde otra carpeta. No se completó partida manual en navegador. |
| B-1 | 12 archivos, 107 413 bytes | HTML/CSS/JS, colocación manual/aleatoria, IA y audio; 9 pruebas declaradas en el archivo de test (Node reporta un archivo de pruebas que pasó). La verificación de partida terminó con 37 movimientos. Sin archivo de traza exportado ni comprobación de veracidad de `moveHistory`. |
| B-2 | 9 archivos, 100 330 bytes | HTML/CSS/JS, colocación manual/aleatoria, IA y audio; 14 pruebas y simulación de 105 tiros en la ejecución propia (la respuesta del agente muestra **102**, cifra que no reproduje). Auditor web y de estado. Sin partida exportada ni contraste entre historial y tablero. |

La interfaz y sus controles están presentes en el código y en los README. Intenté abrir A-1, B-1 y B-2 con Chromium headless desde un servidor local; Chromium salió `-5` por `crashpad`/`setsockopt: Operation not permitted`. Por eso no afirmo que haya comprobado visualmente el flujo de abrir y jugar, el sonido ni la IA desde el navegador. Sí ejecuté los motores y verificadores indicados.

## Costo y elección de los agentes

| Corrida | Tiempo/registro disponible | Elección explicada por el agente |
| --- | --- | --- |
| A-1 | Corrida manual en host del 2026-09-22; no hay aquí tiempo ni conteo de llamadas comparables | El README dice que eligió Oracle para separar juego y juicio, expresar reglas relacionales y declarar el alcance de cada medida. |
| A-2 | Log: 18:56:28–19:05:34, **9 min 6 s**; DB de sesión: 89 pasos de agente y 88 llamadas a herramientas | Respuesta final: eligió Oracle porque las pruebas dentro del mismo código pueden compartir supuestos; construyó catálogo, corpus y juego. El registro muestra mucho trabajo inicial con `oracle manual`, `oracle juzgar`, sintaxis y fuentes de Oracle antes de escribir el simulador y la UI. |
| B-1 | Log: 18:51:33–18:56:27, **4 min 54 s**; DB: 29 pasos de agente y 28 llamadas | Respuesta final: separó motor, interfaz y audio para ejecutar la misma lógica en Node y navegador; propuso pruebas y una simulación con aserciones. No explicó una decisión sobre Oracle: el prompt B no lo ofrecía. |
| B-2 | Log: 18:51:53–18:55:20, **3 min 27 s**; DB: 24 pasos de agente y 23 llamadas | Respuesta final: eligió un motor independiente del DOM, `GameAuditor`, pruebas y simulación paso a paso. Tampoco habla de Oracle. |

En los registros de B-1 y B-2 se ven cinco ejecuciones de tests o verificación de partida en cada una, además de escrituras del juego, ajustes y pruebas de servicio/sintaxis. En A-2 se ven consultas, pruebas, catálogo y corpus Oracle, y también construcción del juego. Una llamada puede mezclar preparación, juego y verificación; no asigno un tiempo por categoría que los registros no miden. No encontré registro comparable de A-1. La comparación de tiempo es además imperfecta porque A-2 y B-2 corrieron en paralelo parcialmente.

## Alcance de la comparación

A-1 fue manual en el host; A-2, B-1 y B-2 corrieron sin intervención dentro de Docker con `agy 1.2.11`, `--new-project --mode accept-edits -p --dangerously-skip-permissions`, copia aislada de la configuración y red habilitada. El primer intento sin ese permiso falló antes de crear producto. A-1 usó Oracle 0.28.0 según su tarea anterior; para este análisis ejecuté `oracle 0.30.0` en las copias. Las verificaciones que informo son las que yo repetí, no las capturas de las respuestas finales.

En estas cuatro salidas, ofrecer Oracle produjo dos expedientes JSON que las tres mentiras alteradas no pudieron pasar. Sin la oferta, B-1 no juzgó su historial y B-2 auditó el tablero vivo pero no la fidelidad de su traza. Esa es una diferencia concreta de **superficie de evidencia y de comprobación**, no una medición general de productividad ni una prueba causal aislada de que Oracle sea la única forma de obtenerla. Son cuatro corridas de un modelo bajo métodos que no fueron idénticos y la partida de navegador no se ensayó manualmente aquí. Una réplica más fuerte preservaría la partida de las B como archivo y haría que un juez independiente la lea, con las mismas condiciones de ejecución para A y B.
