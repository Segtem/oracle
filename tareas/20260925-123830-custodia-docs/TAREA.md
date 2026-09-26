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

### Nota (2026-09-26 02:22:44 UTC)

2026-09-26, ENCARGO a Codex: sacar tools/guia.py y tools/sitio.py de FUERA_TOOLS en tools/mutar_codigo.py (son custodios: guia.py decide si una salida publicada es real, y sitio.py calcula los datos del juego —mutantes, matriz de detección, el donde canónico— y los enlaces). Mutarlos con el arnés (python3 tools/mutar_codigo.py --objetivo tools/guia.py y lo mismo para sitio.py, en una copia con TMPDIR propio y bajo systemd-run --user --scope -p MemoryMax=12G como indica docs/mutacion-memoria.md), y por cada sobreviviente: un test que lo mate, o un equivalente declarado con su razón en equivalentes.json. Terminar con 0 vivos en los dos y la suite en verde. Sin commits.
