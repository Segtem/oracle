# Verificación del corte 0.16.0 — 2026-09-13

El dueño autorizó versión, commit, push, tag y release. PyPI queda a su cargo.
Se aplica distribución 0.16.0; álgebra permanece en 0.6 y sintaxis en 0.4.
Los tres valores literales de los tests MCP se actualizan al número anunciado,
conservando sus comparaciones. `resultados.json` registra la secuencia del corte.

El script del corte reescribió `NOTAS-DE-RELEASE.md` con la sección 0.16.0 sola y borró el
historial de 0.1.0 a 0.15.0. Se restauró antes del commit: la sección nueva va arriba, separada
con `---`, y el diff contra 0.15.0 solo agrega líneas. Ningún test ni herramienta lee ese
archivo, así que la secuencia de `resultados.json` sigue valiendo.
