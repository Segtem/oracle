# Propuesta: armar casos observados desde JSON sin transcribir filas

- ESTADO: CERRADA
- PRIORIDAD: 65
- ETIQUETAS: ergonomia, propuesta

## Alcance propuesto

Derivada de [ergonomia](../20260923-120207-ergonomia/VERIFICACION.md), entrada 5.2, grupo 2. Es una propuesta: no se implementó en la auditoría.

Jam y LyraGASP tienen respectivamente 16 y 17 medidas sin evidencia observada. La CLI ofrece nuevo/listar/generar, pero no un recorrido directo desde JSON del sensor a caso observado. El impresor actual convierte 1000 filas sin pérdida: no hace falta otra sintaxis.

Proponer primero una receta ejecutable que lea una captura, reciba metadatos de origen, medida y etiqueta del autor y guarde el caso como JSON o use caso.imprimir. No inferir procedencia ni reejecutar automáticamente comandos declarados en origen. No prometer que una receta elimina la necesidad de correr sensores en Unreal ni que puede reconstruir las 94 procedencias históricas de Oracle.

## Aceptación propuesta

- Recorrido con captura real disponible y procedencia identificable, sin transcribir filas.
- Conversión sin pérdida de evidencia, incluyendo relaciones vacías; metadatos y polaridad decididos explícitamente.
- Verificación del caso con herramientas existentes. No crear un verbo nuevo antes de demostrar que la receta no alcanza.
- VERSION_ALGEBRA 0.8 y VERSION_SINTAXIS 0.6 no cambian.

### Nota (2026-09-23 17:43:54 UTC)

Propuesta derivada de ergonomia 5.2: deudas 16/17 verificadas y round-trip de 1000 filas correcto. Sólo se escribió alcance y aceptación; sin implementación ni commits.

### Nota (2026-09-23 22:55:22 UTC)

Implementada la receta mínima en ejemplo/caso-observado/convertir.py y README.md, enlazada desde observaciones/README.md. Captura real: observaciones/2026-09-09-aceptacion/evidencia.json; metadatos originales copiados explícitamente, sin afirmar una corrida nueva. Se guarda JSON íntegro sin ejecutar comandos de origen ni inferir procedencia, medida o etiqueta. Prueba previa sin receta: 5 tests ejecutados, 9 fallos incluidos subtests. Tras implementar: 5 tests verdes, cubriendo captura real, mil filas, relaciones vacías, duplicados, tipos, claves, metadatos obligatorios y no sobrescritura. Recorrido literal del README verificado con cargar_fuente_caso, corpus.verificar y medida.evaluar: valor 0, ok=True. Suite completa: python3 -m unittest discover -s tests, 2427 tests en 86.469 s, OK. Cifras regeneradas con python3 tools/cifras.py --actualizar y verificadas: CIFRAS OK. git diff --check limpio. Álgebra 0.8 y sintaxis 0.6 intactas; sin commits ni cambios al corpus histórico. No sustituye sensores Unreal ni reconstruye procedencias. Aceptación completa.

## Próximo paso

Ninguno: tarea completa y CERRADA. Receta, regresiones, suite completa y cifras verificadas; sin commits por instrucción del usuario.
