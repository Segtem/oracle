# Corte 0.38.1

Fuente de los paquetes: commit `068f4e8308c1a9a4365c241382a8c696f5229a63`.
El commit de cierre sólo agrega evidencia y relevo en tareas; el código empaquetado no cambia.
Tag del corte: `v0.38.1`. Álgebra `1.0`, sintaxis `1.1`.

## Comprobaciones

- Suite del corte: 2258 tests, OK. Tras sumar el diagrama (sólo HTML/CSS/documentación), se repitieron 31 pruebas focalizadas: OK. Incluye un test que ejecuta seis comprobaciones JavaScript con Node v24.21.0 sin JIT para respetar el límite del arnés.
- `oracle test`: VERDE; su invocación normal omite mutación de código. La mutación se corrió aparte.
- Guías, generación del sitio, cifras y formato: comprobados por la suite; 35 páginas, 2155 enlaces/recursos locales sin destinos ni anclas rotos.
- Mutación de código con `--alto`: los tres módulos del perfil cambiados desde v0.38.0 completos (`nucleo/version.py`, `tools/guia.py`, `tools/sitio.py`), 420 sitios: 412 no equivalentes y 8 equivalentes existentes. Primer ensayo: 411 muertos y un timeout a 90 s. Reintento sólo de `nucleo/version.py:82:7:negacion` a 240 s: muerto. Unión: 412/412 muertos, ninguno pendiente. Los SHA-256 de las tres fuentes del manifiesto coinciden con el commit del corte. No es una mutación de todo el repositorio ni una única invocación concluyente.
- Primera tentativa de mutación detenida en baseline: V8 no podía reservar CodeRange bajo 1 GiB. El test usa `node --jitless`; se comprobó bajo ese mismo límite y se repitió la ronda.
- Wheel y sdist construidos con Python 3.13.15, build 1.6.1 y setuptools 84.0.0 desde `git archive` del commit fuente, sin archivos locales sueltos.
- `twine check --strict` 7.0.0: PASSED en ambos archivos.
- Verificación de instalación con Python 3.14: namespace, datos, nueve entry points, plantilla, CLI, API y LSP: WHEEL OK.
- El wheel exacto de dist se instaló además en un venv vacío fuera del checkout; versión 0.38.1, creación de plantilla sensor-prosa y oracle test: OK.

## Artefactos

En `dist/0.38.1/` (ignorados por Git), con hashes en `SHA256SUMS` de esta tarea:

- `oracle_metalenguaje-0.38.1-py3-none-any.whl`
- `oracle_metalenguaje-0.38.1.tar.gz`

La publicación en PyPI queda a cargo de Brian en la tarea `pypi-0-38-1`.
No se ejecutó ningún upload.
