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

## Próximo paso

El análisis del punto 1 y 2.
