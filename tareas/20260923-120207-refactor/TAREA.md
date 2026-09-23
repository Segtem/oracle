# El código creció por capas y conviene una auditoría de lo que sobra

- ESTADO: ABIERTA
- PRIORIDAD: 60
- ETIQUETAS: oracle, refactor


## Lo medido

~600 KB de Python en `nucleo/` y `tools/`. Los más grandes: `tools/mcp.py` 85 KB,
`nucleo/sintaxis.py` 73 KB, `tools/cli.py` 60 KB, `nucleo/algebra.py` 51 KB, `nucleo/medida.py`
50 KB. Buena parte creció por entregas sucesivas de agentes distintos. Ya se vieron síntomas:
guardas redundantes que la mutación dejó vivas (0.26), valores por omisión que nadie usaba (0.27), el
mismo límite de memoria escrito en dos lugares (0.28), el contrato del MCP escrito dos veces.

## Qué hacer

1. Una auditoría de lo que sobra —duplicación, abstracciones con un solo uso, código muerto, ramas
   que la mutación no puede matar porque no importan—, con la cita de cada hallazgo.
2. **Nada de refactorizar a ciegas**: cada cambio con la suite y la mutación del módulo en verde
   antes y después. Un refactor que no se puede verificar no se hace.
3. Empezar por lo que además baja tokens o simplifica el MCP, para que esta tarea y
   [`mcp-tokens`](../20260923-120207-mcp-tokens/TAREA.md) no tiren para lados distintos.

### Nota (2026-09-23 23:13:56 UTC)

Completado sólo el punto 1: AUDITORIA.md documenta 9 duplicaciones comprobadas, con citas, ahorro neto y riesgos (126 líneas potenciales; MCP primero). Evidencia reproducible: python3 -B tareas/20260923-120207-refactor/verificar_auditoria.py; nueve comprobaciones OK y JSON MCP idéntico por bytes. Sin cambios en nucleo/ ni tools/, sin cambios de lenguaje, sin commits ni cierre. Suite y mutación de refactor no ejecutadas: quedan para el punto 2.

## Próximo paso

Revisar los nueve hallazgos de [AUDITORIA.md](AUDITORIA.md) y reproducir
`python3 -B tareas/20260923-120207-refactor/verificar_auditoria.py`.
El punto 1 está terminado. Cuando se autorice continuar con el punto 2, empezar
por M1 en `tools/mcp.py`, obteniendo suite y mutación del módulo en verde antes
y después del cambio. No iniciar refactors como parte de esta auditoría.
