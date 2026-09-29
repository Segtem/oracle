# el LSP diagnostica y completa los .requisito

- ESTADO: CERRADA
- PRIORIDAD: 60
- ETIQUETAS: oracle

### Nota (2026-09-29 16:22:01 UTC)

Hecho. tools/lsp.py diagnostica .requisito (forma única, id igual al archivo, lectura) y avisa en la línea de medido_por cuando nombra una medida que no existe, lo mismo que oracle cobertura y meta.el_requisito_nombra_medidas_que_existen pero mientras se escribe; si el catálogo no carga, no inventa el aviso. Completa ids de medida después de medido_por. De paso: los editores sólo registraban .oracle y .caso, así que .relacion nunca le llegaba al LSP aunque éste la diagnosticara; VS Code y Emacs registran ahora .relacion y .requisito, y la gramática resalta requisito, texto, fuente, medido_por y sin_medir. 5 tests nuevos; tools/lsp.py está fuera de la mutación con razón declarada. oracle test VERDE, 2205 tests.
