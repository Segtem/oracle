# el LSP no conoce las escalares del proyecto

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: oracle

### Nota (2026-09-29 19:09:50 UTC)

tools/lsp.py no ejecuta nunca medidas/escalares.py del proyecto: en un consumidor con escalares propias (LyraGASP, Jam) una medida que las usa debería salir como error en el editor, y el aviso de medido_por de los .requisito se calla (el catálogo no carga y _ids_del_catalogo devuelve None). Hace falta decidir cómo se confía desde un editor (una opción del servidor, como --confiar-escalares en el MCP). Verificarlo primero en el editor.
