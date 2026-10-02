# Ordenar el índice de releases y completar metadatos de la web

- ESTADO: ABIERTA
- PRIORIDAD: 35
- ETIQUETAS:

### Nota (2026-10-02 10:32:03 UTC)

Detectado en revisión con agy2: NOTAS-DE-RELEASE.md usa # para cada versión, por lo que el índice lateral enumera subtítulos repetidos y no versiones (hay una tabla principal útil). Cambiar jerarquía coordinando tools/cifras.py y tests que reconocen títulos. También evaluar description/canonical en páginas generadas, indicar sección activa en cabecera y navegación entre decisiones. Son mejoras posteriores, sin bloquear 0.38.1.

## Próximo paso

Ajustar la jerarquía de títulos de releases junto con el índice generado y verificar que cada versión aparezca en el menú lateral.
