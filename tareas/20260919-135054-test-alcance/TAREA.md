# Distinguir en oracle test la validación del corpus y la ausencia de medición del producto

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, ux

## Problema y evidencia

Derivada de 20260919-134424-naval-pm; ver [postmortem](../../estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md) y [reproducciones](../../estudios/naval-pm/oracle-resultados.txt).
Con Oracle 0.27.0, un catálogo propio vacío y un caso sobre una medida heredada de sintaxis reciben verde con `test --rapido`, aun destruyendo game.js en una copia temporal. El caso guarda booleanos; el comando valida ese corpus, no reejecuta el juego. Sin casos ni medidas propias, cmd_test emite explícitamente VERDE de proyecto vacío. Son dos escenarios diferentes.

## Resultado buscado

Que el resumen final permita reconocer qué se validó, qué se omitió y qué no se midió. No inferir cobertura del producto de la cantidad de medidas propias ni rechazar proyectos legítimos que sólo usan medidas heredadas.

## Alcance y aceptación

- Definir y documentar el estado del proyecto vacío (propuesta: advertencia/“sin medición”), separado de error de estructura y de corpus válido. Decidir explícitamente compatibilidad y códigos de salida para CI antes de cambiarlos.
- Mostrar en el veredicto de test que se verificaron medidas contra casos guardados; no que se volvió a ejecutar el comando de origen o el producto. Mantener visibles las omisiones de --rapido.
- Reproducir vacío, un caso con medida heredada, medidas propias con corpus válido y corpus inválido. Incluir el control donde cambia game.js y el caso no cambia: el resultado del corpus puede conservarse, su alcance debe quedar claro.
- Mantener la semántica de juzgar y su ausencia de medidas aplicables; no mezclarla con aceptación del corpus ni exigir sensores por una heurística de nombres de dominio.

## Próximo paso

Leer cmd_test en tools/cli.py y sus regresiones de proyectos externos/vacíos; proponer el texto y contrato de salida de los cuatro escenarios anteriores. Luego implementar con pruebas focalizadas y actualizar la documentación del veredicto. La evidencia no exige hacer rojo todo catálogo propio vacío.
