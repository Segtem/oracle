# La web no muestra nada de lo que Oracle ganó desde 0.26

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, web, documentacion


## El hueco

La página publicada (`docs/index.html`, GitHub Pages) se regenera en cifras en cada corte, pero su
contenido se quedó atrás. Nada de lo que entró desde 0.26 está explicado ahí:

- **el álgebra dice «ninguna»** (`sin`, 0.26);
- **una sombra perdona hasta su cota**, y `juzgar` nombra lo que no se aplicó (0.27);
- **el MCP**, con sus cinco herramientas de sólo lectura y el porqué (0.27);
- **retomar es leer una tarea**: el tracker como relevo, la búsqueda por sufijo y `CIERRA CON` (0.28);
- **`oracle test` dice lo que no midió** (`SIN MEDICIÓN`, 0.28);
- **el camino corto a la primera medida real** (`docs/13-primer-valor.md`);
- **Jev**: un modelo como sensor de la prosa, con lo medido (10/10 controles, 15/15 con un juez
  ciego, centavos) y sus límites; y cómo lo usa alguien desde PyPI cuando cierre
  [`jev-pypi`](../20260923-113127-jev-pypi/TAREA.md).

## Qué hacer

1. Un apartado por tema, corto, con un ejemplo que se pueda copiar y su salida real. Nada de
   promesas: cada cifra sale de una corrida que se pueda repetir.
2. **Un apartado propio para Jev**, que explique la división que hace que valga: el sensor produce
   hechos, la medida juzga; Oracle no llama a ningún modelo; la calibración medida y la zona del
   medio que va a revisión humana.
3. Que la página no dependa de este repo desordenado: se escribe después de
   [`repo-limpio`](../20260923-113951-repo-limpio/TAREA.md) si esa tarea cambia rutas, para no enlazar lo que se va a mover.
4. Comprobar enlaces y cifras con lo que ya existe (`tools/cifras.py`, el test que compara la página
   con el manual).

## Avance

- Elaborado el inventario completo en [`INVENTARIO.md`](INVENTARIO.md), sin mover, borrar ni renombrar ningún archivo del repo, trabajando exclusivamente con lectura y edición de archivos (sin shell ni commits).
- Analizado `docs/index.html` (466 líneas) sección por sección y su mecanismo de actualización automática en `tools/cifras.py`.
- Documentadas las 7 brechas mayores desde 0.26 sustentadas con rutas y líneas exactas:
  1. Anti-junta `sin ... donde ...` (`NOTAS-DE-RELEASE.md`, `nucleo/vocabulario.py`).
  2. Cotas de sombra (`SUPERA SU COTA`) y no aplicadas (`NO SE APLICARON`) en `oracle juzgar` (`NOTAS-DE-RELEASE.md`, `tools/juzgar.py`, `nucleo/medida.py`).
  3. Servidor MCP de sólo lectura con cinco herramientas y su fundamento (`tools/mcp.py`, `docs/mcp-contrato.md`).
  4. El tracker como relevo determinista, búsqueda por sufijo y `CIERRA CON` (`NOTAS-DE-RELEASE.md`, `docs/12-tareas.md`, `AGENTS.md`).
  5. `oracle test` honesto con `ALCANCE`, `PRODUCTO` y `VEREDICTO: SIN MEDICIÓN` (`tools/cli.py`, `NOTAS-DE-RELEASE.md`).
  6. Ruta mínima de primer valor (`docs/13-primer-valor.md`, `ejemplo/primer-valor/`).
  7. Jev como sensor probabilístico de prosa, separación hechos/juicio, calibración medida, zona media a revisión humana y plantilla PyPI (`docs/14-sensor-prosa.md`, `vault-kb/estudios/JEV-COMO-SENSOR.md`, `tareas/20260923-113127-jev-pypi/TAREA.md`, `ejemplo/sensor-prosa/README.md`).
- Analizada la dependencia con `repo-limpio` (`tareas/20260923-113951-repo-limpio/TAREA.md`) para no enlazar rutas sujetas a mudanza.
- Diseñado el índice propuesto de 12 bloques para la nueva portada de `docs/index.html`.
- No se ejecutaron verificaciones de suite ni herramientas por la restricción expresa de operar sin shell.

## Próximo paso

Revisión por parte de Brian del inventario y del índice propuesto en [`INVENTARIO.md`](INVENTARIO.md); tras su aprobación y la confirmación de rutas de `repo-limpio`, redactar las secciones de `docs/index.html` y verificar con `tools/cifras.py` y `tests/test_manual.py`.
