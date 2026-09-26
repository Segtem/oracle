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

### Nota (2026-09-26 02:22:44 UTC)

2026-09-26, ENCARGO a Codex: sacar tools/guia.py y tools/sitio.py de FUERA_TOOLS en tools/mutar_codigo.py (son custodios: guia.py decide si una salida publicada es real, y sitio.py calcula los datos del juego —mutantes, matriz de detección, el donde canónico— y los enlaces). Mutarlos con el arnés (python3 tools/mutar_codigo.py --objetivo tools/guia.py y lo mismo para sitio.py, en una copia con TMPDIR propio y bajo systemd-run --user --scope -p MemoryMax=12G como indica docs/mutacion-memoria.md), y por cada sobreviviente: un test que lo mate, o un equivalente declarado con su razón en equivalentes.json. Terminar con 0 vivos en los dos y la suite en verde. Sin commits.

### Nota (2026-09-26 02:29:33 UTC)

Implementé la entrada de tools/guia.py y tools/sitio.py en HERRAMIENTAS_CUSTODIAS, PRIORIDADES y la matriz de .github/workflows/verificar.yml; los saqué de FUERA_TOOLS. Extraje reemplazar_salidas como función pura y agregué tests rápidos de una guía mínima de dos pasos, conversión Markdown, enlaces y datos reales del juego. Reapunté con --reapuntar-equivalentes un ID desplazado en tools/mutar_codigo.py. Ejecuté python3 -m unittest tests.test_guia_rapida tests.test_sitio_rapido -q: 11 tests OK; python3 tools/ejecutar_suite_mutacion.py: 2587 tests OK (120,885 s); git diff --check: OK. Preparé la copia /tmp/oracle-custodia-docs-hje2dl84/repo y TMPDIR /tmp/oracle-custodia-docs-hje2dl84/tmp. Intenté ambos comandos systemd-run --user --scope -p MemoryMax=12G env TMPDIR=... python3 tools/mutar_codigo.py --objetivo tools/guia.py y tools/sitio.py; los dos salieron 1 antes de iniciar el arnés: Failed to connect to user scope bus via local transport: Operation not permitted. No hay conteo de sobrevivientes ni equivalentes nuevos; no se cumplió todavía el objetivo de 0 vivos. No hice commits ni cerré la tarea.

## Próximo paso

En un entorno donde `systemd-run --user --scope` pueda conectar con el bus de usuario, actualizar la copia con estos cambios y ejecutar las dos rondas completas con `TMPDIR` propio y `MemoryMax=12G`. Por cada sobreviviente, agregar un test que lo mate o declarar su equivalencia razonada en `equivalentes.json`; repetir hasta obtener 0 vivos en ambos módulos y volver a correr la suite. El bloqueo actual es el rechazo del bus de usuario (`Operation not permitted`) antes de iniciar el arnés.
