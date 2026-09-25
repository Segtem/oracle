# guia.py y sitio.py quedaron fuera de la mutación, pero custodian que la documentación publicada sea real

- ESTADO: ABIERTA
- PRIORIDAD: 60
- ETIQUETAS: oracle, mutacion


## Por qué

2026-09-25. `perfil-mutacion` dejó fuera `tools/guia.py` y `tools/sitio.py` porque «sus salidas se
comprueban por separado». Por el criterio de `HERRAMIENTAS_CUSTODIAS` (si se rompe, una afirmación
queda sin nadie que la verifique) son custodios: si `guia.py` deja de comparar salidas, la guía
publicada puede mentir en silencio. Es el mismo caso de `cifras.py`, que está dentro.

## Qué hacer

Sumarlos a la mutación con tests rápidos que no ejecuten la guía entera por mutante (una guía mínima
de dos pasos como fixture, funciones puras para el reemplazo de salidas y la conversión de Markdown),
y matar los vivos.

## Próximo paso

Codex, después del corte 0.31.0.
