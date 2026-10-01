# el código Oracle de la web se colorea con la misma gramática que VS Code

- ESTADO: CERRADA
- PRIORIDAD: 78
- ETIQUETAS: 

### Nota (2026-10-01 10:17:06 UTC)

oracle-lsp no colorea (da diagnósticos, completado y CodeLens). Los colores los pone la extensión de VS Code con la gramática TextMate editores/vscode/oracle.tmLanguage.json (.oracle, .caso, .relacion, .requisito). Qué: tools/sitio.py colorea los bloques de código oracle/caso/relacion/requisito leyendo ESA gramática (una sola fuente: si cambia la gramática, cambia la web), con clases por scope y colores en sitio.css para tema claro y oscuro. Encargado a Codex.

### Nota (2026-10-01 10:28:19 UTC)

tools/sitio.py lee la gramática TextMate de VS Code al generar y colorea oracle, caso, relacion y requisito por prioridad de patrones y capturas, con HTML escapado. docs/assets/sitio.css define tokens para tema claro y oscuro. Agregué test de una medida pequeña y actualicé los ocho IDs de equivalentes.json movidos por las nuevas líneas. Regeneré el sitio; la suite completa pasó (2250 tests).

### Nota (2026-10-01 10:33:24 UTC)

Verificación final: python3 tools/guia.py --escribir (0 salidas actualizadas), python3 tools/sitio.py --escribir (sin páginas pendientes), python3 -m unittest discover -s tests (2250 tests, OK), python3 tools/oracle.py test (VEREDICTO: VERDE; mutación de código salteada). No se hizo commit.

## Próximo paso

Revisar el diff de esta tarea para su eventual versionado; no queda implementación pendiente.
