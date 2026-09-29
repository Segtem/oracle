# el LSP no conoce las escalares del proyecto

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: oracle

### Nota (2026-09-29 19:09:50 UTC)

tools/lsp.py no ejecuta nunca medidas/escalares.py del proyecto: en un consumidor con escalares propias (LyraGASP, Jam) una medida que las usa debería salir como error en el editor, y el aviso de medido_por de los .requisito se calla (el catálogo no carga y _ids_del_catalogo devuelve None). Hace falta decidir cómo se confía desde un editor (una opción del servidor, como --confiar-escalares en el MCP). Verificarlo primero en el editor.

### Nota (2026-09-29 19:48:08 UTC)

Reproducción: agregué test con escalares.py y medida que usa es_grande; antes del arreglo falló (severity 1 frente a aviso 2). Implementé --confiar-escalares en tools/lsp.py, registro aislado durante toda la sesión y aviso único sin confianza; VS Code y Emacs exponen opciones booleanas desactivadas por omisión. Tests de protocolo cubren diagnóstico .oracle, medido_por .requisito, completado de .caso/.requisito y lentes con y sin confianza. Ejecutado: python3 -m unittest tests.test_lsp -q (53 OK); python3 -m unittest discover -s tests -t . (2208 OK, en corrida secuencial); python3 tools/cifras.py --actualizar y python3 tools/cifras.py (CIFRAS OK); python3 tools/cli.py test (VEREDICTO VERDE). También node --check, json.tool, Emacs batch con defcustom activo y git diff --check: correctos. Primera corrida simultánea de suite y CLI falló por interferencia de directorio temporal y cifras aún vencidas; repetí secuencialmente y pasó. Sin commit; tarea sigue ABIERTA.

## Próximo paso

Revisar el diff de este worktree y probar el ajuste en una sesión real de VS Code y Emacs con un proyecto que tenga `escalares.py` antes de integrarlo.

### Nota (2026-09-29 19:52:20 UTC)

Revisión de Claude antes de unir. Codex hizo la base bien: --confiar-escalares al arrancar oracle-lsp, el contexto de escalares envolviendo todo el servidor, opciones en VS Code y Emacs y tests de los cuatro caminos. Dos ajustes: (1) sin confianza, Codex reemplazaba TODOS los diagnósticos de .oracle, .requisito y .caso por el aviso, con lo que un consumidor perdía errores de forma que no dependen de escalares; ahora la lectura y la forma única se diagnostican siempre, el aviso reemplaza sólo construir la medida (en su encabezado) y el control de medido_por (en su línea), y un .caso no cambia. (2) oracle.confiarEscalares en VS Code tiene scope machine: un repositorio no puede encenderla desde su .vscode/settings.json y hacer que el editor ejecute su escalares.py; en Emacs el defcustom no declara :safe, así que un .dir-locals.el pide confirmación. Test nuevo de la forma sin confianza. tests/test_lsp 54 OK; oracle test VERDE. Sale en 0.36.1.
