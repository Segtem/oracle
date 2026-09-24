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

### Nota (2026-09-23 23:18:07 UTC)

Implementados M1–M7 y N1–N2. Auditoría previa y suite previa: OK (2427 tests). rg de usos y parches, incluidos alias, no encontró consumidores que parcheen caso._fallar, caso._indentada ni caso.IND: habilitado N2; IND conservado. M1–M5 usan deepcopy; M6 conserva partition, comentario, raise from e y orden de captura; M7 conserva posición dentro del contexto y macros calculadas, sin extraer la carga distinta de catalogo_para_mcp. Agregado verificar_auditoria.py --despues: SHA256 esperado y estructuras mutables independientes OK; comparación directa con JSON previo también idéntica por bytes. El comando requerido python3 tools/mcp_contrato.py --check fallaba por import relativo sin paquete; ajustado el arranque al patrón de otros CLI para aceptar archivo y módulo. Ambos --check pasan. Suite posterior en curso. Sin mutación de módulos ni commits; tarea abierta.

### Nota (2026-09-23 23:19:45 UTC)

La primera suite posterior detectó equivalentes vencidos por el corrimiento de líneas en caso.py (5 fallos y 4 errores, todos derivados de seis ids posicionales). Reapuntados sólo esos seis ids en equivalentes.json mediante correspondencia de líneas idénticas entre HEAD y el archivo actual: 132→109, 283→260, 306→283 (dos sitios), 341→318 y 358→335. Texto, ordinal, tipo, columna y razones conservados; no se ejecutó mutación. Suite completa repetida para verificar la corrección. Verificador --despues ejercitado también con un cambio de bytes y un alias mutable temporal en memoria: rechaza ambos.

### Nota (2026-09-23 23:21:20 UTC)

Verificación final: python3 -m unittest discover -s tests OK, 2427 tests en 86,692 s; python3 tools/mcp_contrato.py --check y modo módulo OK; verificar_auditoria.py --despues OK con SHA256 ba56e283a38179e3fdcfe9391bd3096fb96e33f6149edfdcdf8d8442db0ddbac, 11.648 bytes idénticos a la captura previa y sin alias mutables. Orden exterior de capturas comprobado por AST; resto del AST de caso intacto fuera de las tres extracciones e imports. python3 tools/cifras.py --actualizar ejecutado al final: README.md actualizado. git diff --stat -- tools/mcp.py nucleo/caso.py: 123 inserciones y 255 borrados, reducción neta 132 frente a 126 previstas; las seis adicionales son separadores vacíos retirados en caso.py. El ajuste del arranque de mcp_contrato agrega cuatro líneas netas aparte; equivalentes.json sólo reapunta ids. Sin cambios del lenguaje, sin commits ni ejecución de rondas de mutación de módulos. La mutación antes/después queda a cargo del usuario por instrucción expresa; no se cierra la tarea.

## Próximo paso

El usuario ejecutará y registrará aquí la mutación de código antes/después de
`tools/mcp.py` y `nucleo/caso.py`, usando sus resultados previos y este árbol
refactorizado. Revisar esa evidencia antes de decidir el cierre; la tarea queda
ABIERTA y sin commits. M1–M7 y N1–N2 están implementados, la suite completa y el
contrato pasan y las cifras están actualizadas. Para reproducir la comprobación
del JSON usar `python3 -B tareas/20260923-120207-refactor/verificar_auditoria.py --despues`.

### Nota (2026-09-24 02:03:44 UTC)

2026-09-23, Claude: mutación de código antes y después, en copias aisladas con tope de 12 GB. tools/mcp.py: 386/386 → 363/363 muertos; nucleo/caso.py: 210/210 → 203/203 (con 6 equivalentes declarados, reapuntados). Cero vivos antes y después: el refactor no abre ningún hueco que la suite no vea.
