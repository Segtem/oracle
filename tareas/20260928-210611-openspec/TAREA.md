# OpenSpec + Oracle: cuántos requisitos de una spec real se pueden medir de verdad

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle

### Nota (2026-09-28 21:19:02 UTC)

Experimento hecho (experimento/README.md). cli-validate: 31 escenarios reales → 19 medibles, 9 parciales, 3 prosa; 28/31 con medida. 32 medidas, aceptación ✓, mutación 651/651. CLI 1.13.2: 28 verdes, 4 rojas (issues sin ruta de archivo 11/16; texto del aviso de viñetas distinto; falta la nota de títulos; AGENTS.md que 1.x ya no genera). Destapó en Oracle: crash de segundo_autor._alias_referidos (arreglado con test) y que caso generar no cubre medidas con sin.

### Nota (2026-09-29 09:46:54 UTC)

2026-09-29, Brian: no se reportan los cuatro rojos a Fission-AI/OpenSpec. El experimento cumplió su objetivo: medir cuánto de una spec real es medible (31 escenarios, 19 medibles, 9 parciales, 3 prosa; por requisito 3 medidos y 9 en parte) y sacar de ahí tres mejoras para Oracle, ya publicadas en 0.35.0 (requisitos y oracle cobertura, oracle cambios, medida nueva --escenario) más el generador para medidas con sin.
