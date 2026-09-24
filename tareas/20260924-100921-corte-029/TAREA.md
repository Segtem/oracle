# Corte 0.29.0

- ESTADO: CERRADA
- PRIORIDAD: 90
- ETIQUETAS: oracle, release


Cortar 0.29.0 con lo cerrado desde 0.28.0: `ergo-orden`, `ergo-confianza`, `ergo-observados`,
`init-ayuda`, `timeout-suite-mutacion`, `refactor`, `mcp-tokens`, `jev-pypi` (plantilla
sensor-prosa) y lo que haya del patrón Jev. Mutación de lo tocado, notas, crónica, cifras al final,
build limpio, tag y release; Brian sube a PyPI.

### Nota (2026-09-24 11:37:26 UTC)

Guardia de ayuda de tools/cli.py (1087-1102): agregados dos tests en tests/test_cli.py. El primero exige int 0 exacto en las seis ramas; el segundo exige que proyecto nuevo --help siga como verbo desconocido. Verificación individual de los siete mutantes VIVO mediante copias en memoria del módulo: los seis return 0→None y el and→or fallan con esos tests. Suite completa: python3 -B -m unittest discover -s tests -t . -q, 2432 tests OK (90,583 s). El arnés mutar_codigo.py --lineas 1087-1102 quedó inconcluso antes de mutar por timeout de línea base, incluso con --timeout-base 180 --timeout 120. No se modificó tools/cli.py ni equivalentes.json; sin commits.

## Próximo paso

Continuar el corte 0.29.0: completar la verificación de los demás cambios y preparar notas, crónica, cifras y build limpio antes del tag y release.

### Nota (2026-09-24 13:36:52 UTC)

2026-09-24: cortado. Tag v0.29.0 y release https://github.com/Segtem/oracle/releases/tag/v0.29.0 con wheel (sha256 ec5b9c72…) y sdist (f103849b…), construidos en un worktree limpio; verificar_instalacion WHEEL OK. Falta que Brian suba a PyPI.
