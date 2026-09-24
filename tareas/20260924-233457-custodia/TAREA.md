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

## Próximo paso

Fase 1 de incorporación (punto 3): sumar a `HERRAMIENTAS_CUSTODIAS` en `tools/mutar_codigo.py`, `PRIORIDADES` y `.github/workflows/verificar.yml` los tres módulos directos sin autorreferencia (`generar_diferencial.py`, `mutar.py` y `trazar.py`), medir su mutación y escribir los tests necesarios para matar los mutantes que sobrevivan.

### Nota (2026-09-24 23:48:59 UTC)

2026-09-24, revisión de Claude: agy también escribió un ANALISIS.md y una nota dentro de 20260916-014457-custodia, que está CERRADA; se revirtió: la historia cerrada no se reescribe. Las cifras de sitios son estimaciones (sin shell); la Fase 1 las mide.
