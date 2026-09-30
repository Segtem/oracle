# la web al día con 0.37.0 y 0.38.0

- ESTADO: CERRADA
- PRIORIDAD: 80
- ETIQUETAS: 

### Nota (2026-09-30 21:53:05 UTC)

Por qué: el sitio (docs/, generado con tools/sitio.py) no cuenta nada de 0.37.0 ni 0.38.0 fuera de las notas y docs/openspec.md: respaldo real, cambios con sensores, cobertura --con, requisito importar, el generador que busca. Qué: revisar docs/index.html (portada), docs/README.md (el camino), como-funciona.md y 07-conectar-a-un-proyecto-propio.md y sumar lo nuevo donde un lector lo busca, sin inflar. Toda salida de comando en una guía la escribe tools/guia.py --escribir, no a mano. Encargado a agy1.

## Avance

Se incorporaron las novedades de las versiones 0.37.0 y 0.38.0 en los puntos de entrada clave de la documentación y el sitio web:
- `docs/README.md`: se actualizaron las entradas de la tabla de navegación para destacar `oracle cambios` vigilando sensores en `07-conectar`, el respaldo real en `05-por-que-la-mutacion`, y el flujo de `oracle requisito importar` junto a `oracle cobertura --con` en `openspec.md`. Además, en «Lo que no es un documento», se sumaron descripciones precisas de `oracle cobertura`, `oracle cambios` y `oracle caso generar`.
- `docs/como-funciona.md`: se sumó la explicación de `oracle cobertura --con` para juzgar evidencia contra requisitos declarados; se documentó el significado del `respaldo real` al lado de los mutantes muertos y la búsqueda/reducción de casos con `oracle caso generar`; en «Lo que Oracle no hace» se destacó que `oracle cambios` evita aflojar reglas o sensores en silencio.
- `docs/07-conectar-a-un-proyecto-propio.md`: se explicitó el rol del `respaldo real` tras la salida de `oracle test`, conectando el caso observado con la resistencia a defectos reales; se agregó la sección «Vigilar lo que alimenta a las medidas: `oracle cambios`» documentando el campo `"sensores"` en `oracle.json` y la regla de que quitar rutas es un error; se sumó el enlace a `OpenSpec y Oracle` en «Qué sigue».
- `docs/index.html`: se incorporaron el respaldo real y `oracle caso generar` en la sección de mutación; se documentaron `oracle cambios`, `oracle requisito importar` y `oracle cobertura --con` en la sección de agentes; se actualizó la tarjeta de conectar proyectos y se sumó el recorrido de `OpenSpec y Oracle`.
- Páginas HTML regeneradas con `python3 tools/sitio.py --escribir`: `docs/documentacion.html`, `docs/como-funciona.html`, `docs/07-conectar-a-un-proyecto-propio.html`.
- Verificación: `python3 tools/cifras.py` (cifras OK) y `python3 -m unittest tests.test_sitio tests.test_guia` (10 tests en verde, 0 salidas desactualizadas).

## Próximo paso

Revisar visualmente las páginas generadas y dar por cerrada la tarea.

### Nota (2026-09-30 22:15:37 UTC)

Unido por Claude, con una corrección: cambios no dice si una escalar «se relajó», dice que cambió. La afirmación de la guía 07 (respaldo real 7 de 9 por el caso observado 003) se verificó contra su salida real.
