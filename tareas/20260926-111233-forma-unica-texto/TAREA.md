# El lector acepta varias escrituras que dan el mismo árbol: que el texto válido sea exactamente el que escribe el impresor

- ESTADO: ABIERTA
- PRIORIDAD: 88
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 11:12:33 UTC)

2026-09-26, origen: AUDITORIA-2.md de una-sintaxis (agy), verificado por Claude ejecutando: el lector acepta con el MISMO árbol agregado antes o después de clave en agrupar, «sintaxis 0.8» opcional al inicio, 1e-3 y 0.001, nombres de variante con y sin comillas, los campos de origen: en cualquier orden, y (según agy) clave(t) con y sin «;». 384 de 427 archivos de Oracle ya son texto por texto la salida del impresor; los otros 43 difieren en líneas en blanco o en paréntesis de claridad. DECISIÓN (Claude, con delegación de Brian), en lugar de perseguir variantes una por una, un invariante como gofmt: (1) todo .oracle, .caso y .relacion de un proyecto tiene que ser EXACTAMENTE imprimir(leer(texto)), comparando sin las líneas de comentario. La capa SINTAXIS de oracle test falla con un diff corto por archivo y el comando que lo arregla. (2) oracle formatear <ruta> [--escribir] reescribe a la forma del impresor CONSERVANDO los comentarios (líneas # completas) en su lugar; sin --escribir sólo informa. (3) El impresor pone paréntesis alrededor de un «y» anidado en un «o» (claridad; la precedencia no cambia y el árbol tampoco). (4) Formatear los 43 archivos de Oracle y ejemplos y comprobar que ningún árbol canónico cambia. (5) docs/tutorial-practico.md:684 todavía dice que el catálogo carga .oracle igual que .json: corregir. (6) oracle convertir ya escribe en la forma del impresor; los consumidores quedan canónicos al convertir. Va en la sintaxis 0.8. Tests: el invariante sobre un proyecto con cada variante de la auditoría (tiene que fallar) y sobre Oracle (verde).

### Nota (2026-09-26 11:27:11 UTC)

Implementado invariante de forma única para .oracle/.caso/.relacion, diff y comando formatear con preservación de comentarios; impresor parentiza y dentro de o; 42 archivos de ejemplos normalizados con árbol idéntico comprobado; tutorial corregido. Ejecutado: suite completa 2597 tests OK; guia.py --escribir (0 salidas); sitio.py --escribir (4 páginas); cifras.py --actualizar (README actualizado); cli.py test --rapido VERDE con SINTAXIS OK. No se corrió mutación ni se hicieron commits.

## Próximo paso

Revisar el diff de esta implementación y decidir la integración; mantener la tarea ABIERTA hasta esa revisión.
