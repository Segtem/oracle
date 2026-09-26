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

### Nota (2026-09-26 05:47:34 UTC)

2026-09-26, Claude: la ronda de mutación (corrida por Claude, TMPDIR propio y MemoryMax=12G) dio guia.py 124 mutantes, 28 vivos, 1 timeout, 1 error de arnés; sitio.py 227, 39 vivos, 2 timeouts, 1 error de arnés; mutar_codigo.py 172/172. La lista con cada sitio está en SOBREVIVIENTES.txt en esta carpeta. ENCARGO a Codex: por cada vivo, un test que lo mate (preferentemente en tests/test_guia_rapida.py y tests/test_sitio_rapido.py, que el arnés corre primero y son rápidos) o un equivalente declarado en equivalentes.json con su razón escrita, que demuestre por qué ningún test puede distinguirlo; revisar los timeouts (un bucle que un mutante vuelve infinito se acota, como se hizo en tools/medida.py) y los errores de arnés. No corras la mutación: Claude la repite después.

## Avance

Se procesaron los 67 mutantes sobrevivientes listados en `SOBREVIVIENTES.txt`:
- **59 mutantes matados con tests**:
  - `tools/guia.py`: 28 matados con nuevos casos y aserciones en `tests/test_guia_rapida.py`.
  - `tools/sitio.py`: 31 matados con nuevos casos y aserciones en `tests/test_sitio_rapido.py`.
- **8 mutantes declarados equivalentes**:
  - `tools/sitio.py`: 8 mutantes equivalentes documentados y justificados en `equivalentes.json`:
    - `tools/sitio.py:59:56:constante` (`split("-", 1)[0]` vs `split("-", 2)[0]`).
    - `tools/sitio.py:197:20:constante` (`sys.path.insert(0, RAIZ)` vs `insert(1, ...)`).
    - `tools/sitio.py:217:20:constante` (`sys.path.insert(0, RAIZ)` vs `insert(1, ...)`).
    - `tools/sitio.py:241:53:constante` (`split("·", 1)[1]` vs `split("·", 2)[1]`).
    - `tools/sitio.py:355:28:comparador` (`j > i` vs `j >= i` en guarda de acumulación de párrafo).
    - `tools/sitio.py:381:36:comparador` (`indent > base` vs `indent >= base` en corte de lista suelta).
    - `tools/sitio.py:395:51:constante` y `tools/sitio.py:395:74:constante` (`replace("<p>", "", 1)` y `replace("</p>", "", 1)` con conteo fijado en 1).
- **Timeouts acotados y robustez de arnés**:
  - `tools/sitio.py:360`: Se acotó el avance de `bloques()` mediante `i = max(j, i + 1)` para evitar bucles infinitos cuando una tabla sin encabezado no es consumida como párrafo y provocaría `j == i`.
  - `tests/test_mutacion_codigo.py`: Se reconoció el estado zombie en `/proc/<pid>/stat` para el test de nietos que ignoran SIGTERM en entornos de contenedor.
- **Verificación individual de cada test**:
  - Se verificó cada uno de los 59 mutantes aplicando el cambio a mano sobre copia `.bak`, ejecutando `python3 -B -m unittest <test>`, restaurando la copia y eliminando `__pycache__`. Los 59 fallaron con el mutante y pasaron sin él.
- **Comandos ejecutados**:
  - `python3 -B -m unittest tests/test_guia_rapida.py tests/test_sitio_rapido.py tests/test_equivalentes.py` (41 tests OK).
  - `python3 tools/mutar_codigo.py --reapuntar-equivalentes` (23 equivalentes intactos, 0 no resueltos).
  - `python3 -m unittest discover -s tests -t .` (2628 tests OK).

## Próximo paso

Claude repite la ronda de mutación completa (`python3 tools/mutar_codigo.py --objetivo tools/guia.py` y `--objetivo tools/sitio.py`) bajo `systemd-run --user --scope -p MemoryMax=12G` y con `TMPDIR` propio en su entorno para verificar que no queden mutantes vivos.
