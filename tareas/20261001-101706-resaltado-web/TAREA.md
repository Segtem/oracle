# el código Oracle de la web se colorea con la misma gramática que VS Code

- ESTADO: ABIERTA
- PRIORIDAD: 78
- ETIQUETAS: 

### Nota (2026-10-01 10:17:06 UTC)

oracle-lsp no colorea (da diagnósticos, completado y CodeLens). Los colores los pone la extensión de VS Code con la gramática TextMate editores/vscode/oracle.tmLanguage.json (.oracle, .caso, .relacion, .requisito). Qué: tools/sitio.py colorea los bloques de código oracle/caso/relacion/requisito leyendo ESA gramática (una sola fuente: si cambia la gramática, cambia la web), con clases por scope y colores en sitio.css para tema claro y oscuro. Encargado a Codex.
