# Motor.desde_proyecto juzga con otro catálogo que oracle test

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, bug

Medido el 2026-09-15 (P0 de 0.18.0): con `catalogo_base: true`, `Motor.desde_proyecto` carga 57 medidas y `catalogo_efectivo` 37; las 20 de más son `del_origen`. Además `Motor` ignora las sombras de `oracle.json`. LyraGASP (`tools/juzga_oracle.py`) y Jam (`oracle_shadow.py`) usan esa fachada. Ver [REVISION-CLAUDE.md](../../estudios/0.18.0-juzgar/REVISION-CLAUDE.md).
