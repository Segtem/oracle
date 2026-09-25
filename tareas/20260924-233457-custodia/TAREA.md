# Los arneses que verifican a Oracle no están bajo mutación: mutar, mutar_codigo y generar_diferencial quedan fuera del perfil

- ESTADO: ABIERTA
- PRIORIDAD: 88
- ETIQUETAS: oracle, mutacion, flaqueza


## Por qué

2026-09-24. En los cortes 0.29.0 y 0.30.0 la mutación rechazó como «fuera del perfil activo» módulos
que cambiaron. El perfil muta `nucleo/`, `perfiles/python/`, `oracle_metalenguaje/` y la lista
`HERRAMIENTAS_CUSTODIAS` de `tools/mutar_codigo.py`, cuyo criterio es: se muta lo que, si se rompiera,
dejaría alguna afirmación sin verificar. Quedan fuera 12 módulos de `tools/`:
`ejecutar_suite_mutacion.py`, `estudio.py`, `generar_diferencial.py`, `lsp.py`, `mcp_contrato.py`,
`mutar.py`, `mutar_codigo.py`, `oracle.py`, `plantilla.py`, `sesion.py`, `trazar.py` y
`verificar_instalacion.py`. Según ese mismo criterio, `mutar.py` (mutación de medidas),
`mutar_codigo.py` y `ejecutar_suite_mutacion.py` (mutación de código), `generar_diferencial.py`
(el diferencial) y `mcp_contrato.py` (el control del contrato) parecen custodios: si se rompen, un
verde de mutación o de diferencial deja de significar lo que dice. `lsp.py` salió a propósito el
2026-09-09 (ver el comentario de la lista).

## Qué hacer

1. Para cada uno de los 12: ¿cumple el criterio? Con la afirmación concreta que dejaría sin verificar
   y quién la consume. Si un arnés no puede mutarse a sí mismo sin recursión, decir cómo se lo
   verifica y proponer la forma (una copia congelada del arnés que mute a la actual, un arnés
   testigo…).
2. Costo estimado: sitios de mutación de cada uno (`tools/mutar_codigo.py` puede contarlos).
3. Después, en otra pasada: sumarlos a la lista y matar lo que sobreviva.

## Avance

2026-09-24. Se completó el análisis de los puntos 1 y 2 en `ANALISIS.md`:
- Se revisaron los 12 módulos de `tools/` contra el criterio de custodia de `tools/mutar_codigo.py:167-168`.
- 6 cumplen el criterio: `ejecutar_suite_mutacion.py`, `generar_diferencial.py`, `mutar.py`, `mutar_codigo.py`, `trazar.py` y `verificar_instalacion.py` (costo conjunto estimado: 600–860 sitios).
- 6 no lo cumplen: `estudio.py`, `lsp.py`, `mcp_contrato.py`, `oracle.py`, `plantilla.py` y `sesion.py` (adaptadores, shims, generadores de documentación o helpers).
- Para los arneses autorreferenciales (`ejecutar_suite_mutacion.py` y `mutar_codigo.py`), se definió la arquitectura de desacoplamiento con arnés testigo inmutable desde la raíz base y tests unitarios específicos para evitar recursión.

### Nota (2026-09-24 23:48:59 UTC)

2026-09-24, revisión de Claude: agy también escribió un ANALISIS.md y una nota dentro de 20260916-014457-custodia, que está CERRADA; se revirtió: la historia cerrada no se reescribe. Las cifras de sitios son estimaciones (sin shell); la Fase 1 las mide.

### Nota (2026-09-25 00:32:15 UTC)

Fase 1 completada sin commits: mutar.py, generar_diferencial.py y trazar.py incorporados a HERRAMIENTAS_CUSTODIAS, PRIORIDADES y matriz de CI; tests/test_herramientas.py fija su presencia. Sitios AST reales: 48, 110 y 34 (192 total). Rondas completas con timeout 300: 47/47, 109/109 y 33/33 mutantes ejecutados muertos, cero vivos, cero timeouts y cero errores de arnés; un equivalente por archivo en sys.path.insert(0, RAIZ) documentado en equivalentes.json. Nueve tests directos agregados en tests/test_custodia_fase1.py. Logs y manifiestos en esta carpeta. Suite completa: 2453 tests OK; oracle test --rapido: VERDE tras actualizar README con cifras.py.

### Nota (2026-09-25 01:55:00 UTC)

Fase 2 (diseño sin código) completada en `DISENO-FASE2.md`:
- Análisis de autorreferencia: se documentó detalladamente por qué ni `tools/ejecutar_suite_mutacion.py` ni `tools/mutar_codigo.py` pueden juzgar a sus propios mutantes sin corromper el veredicto (falsos verdes si retornan 0, falsas rondas inconclusas si retornan 2 o crashean, o bloqueos flock en `_bloqueo_de_ronda`).
- Arquitectura de desacoplamiento en dos niveles: arnés testigo inmutable congelado desde la raíz base (`RAIZ / "tools" / "ejecutar_suite_mutacion.py"`) con `--tope` y `--inicio` apuntando al sandbox temporal; suites testigo sintéticas programadas en `tests/test_ejecutar_suite_mutacion.py` que comprueban códigos 0, 1 y 2 en entornos aislados; y tests unitarios directos con mocks para la orquestación de `tools/mutar_codigo.py` (`tests/test_mutar_codigo_custodia.py`).
- Mapeo exhaustivo de «qué rompe»: análisis por archivo, línea y operador AST para ambos módulos, identificando los tests específicos que matan cada mutante y los mutantes equivalentes anticipados en `sys.path.insert(0, ...)`.
- Costo estimado conjunto: 255 a 345 sitios AST (~35-45 en `ejecutar_suite_mutacion.py` y ~220-300 en `mutar_codigo.py`). Con el arnés testigo y tests prioritarios directos, el tiempo estimado de corrida pasa de ~3 horas a menos de 75 segundos.

### Nota (2026-09-25 02:54:53 UTC)

Fase 2 implementada sin commits: el runner testigo se ejecuta desde la raíz y carga tests de la copia; --solo-prioridad limita las rondas de los dos arneses a sus suites testigo. Ambos entraron en HERRAMIENTAS_CUSTODIAS, PRIORIDADES, matriz CI y test_herramientas. Mutación completa: ejecutar_suite_mutacion.py 44/44 muertos, mutar_codigo.py 167/167 muertos más 1 equivalente documentado en equivalentes.json, cero vivos, timeouts o errores de arnés. Evidencia con rutas relativas: tareas/20260924-233457-custodia/fase2-runner.json y fase2-mutador.json; manifiestos y stderr en la misma carpeta. Suite completa 2506 tests OK: fase2-suite-completa.log. python3 tools/cli.py test --rapido VERDE: fase2-test-rapido.log. python3 tools/cifras.py --actualizar aplicado: fase2-cifras.log. Logs archivados con rutas normalizadas relativas, sin /tmp. Queda Fase 3 verificar_instalacion.py; tarea ABIERTA.

## Próximo paso

Implementar la Fase 3 para `tools/verificar_instalacion.py`: definir sus tests directos, incorporarlo a HERRAMIENTAS_CUSTODIAS, PRIORIDADES y la matriz CI, ejecutar su ronda completa y matar los vivos o justificar equivalentes; después repetir suite completa, `test --rapido` y `cifras.py --actualizar`. Mantener la tarea ABIERTA hasta completar esa fase.
