# Propuesta: armar casos observados desde JSON sin transcribir filas

- ESTADO: ABIERTA
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

## Próximo paso

Revisar la propuesta en ergonomia y seleccionar una captura real disponible para probar la receta; no inventar metadatos ni convertir casos construidos en observados.
