# caso generar no fabrica evidencia para medidas con sin

- ESTADO: CERRADA
- PRIORIDAD: 60
- ETIQUETAS: oracle

### Nota (2026-09-28 21:19:05 UTC)

En el experimento de OpenSpec (tareas/20260928-210611-openspec/experimento) cubrió 18 de 32 medidas: las 14 con un paso sin quedaron sin caso y hubo que escribirlas en corpus.py (romper una corrida quitando las filas de la relación negada). El generador debería derivar eso del AST igual que hace con donde.

### Nota (2026-09-29 05:07:26 UTC)

Hecho. El generador fabrica casos para medidas con sin: (1) salvar_con_parejas arma, por cada paso sin, la fila que cumple su condición copiando el valor real de cada clave del join (igualdad entre campos) y juntando todos los contiene de un campo; (2) fabricar_filas da a cada clave de un sin un texto único en toda fila, para que la ofensora y la limpia no compartan pareja ni difieran de tipo (el álgebra 1.0 rechaza == entre número y texto); (3) un verde nuevo, salvada: la fila que ofendería salvada por su pareja más una limpia sin pareja (si hay donde), que mata quitar_antijunta, quitar_filtro y aflojar el donde; (4) para toda medida con requiere, un caso con esa relación vacía y espera: sin_evidencia, que mata quitar_requiere y quitar_requisitos_de_evidencia. Sobre las 32 medidas del experimento de OpenSpec con el corpus borrado: 29 con casos (antes 18) y 16 con todos sus mutantes muertos; las 11 con sin salen todas (antes ninguna). Mutación de las líneas nuevas: 94, sin sobrevivientes tras sacar guardas que el álgebra ya garantiza y arreglar dos defectos que encontró (medida sin donde; auto-igualdad). oracle test VERDE, 2179 tests. Deuda vieja aparte: la ronda completa de nucleo/generador.py daba 400 sobrevivientes de 573 en v0.35.0; ahora 88 de 683, todos en código anterior. Va a la tarea nueva.
