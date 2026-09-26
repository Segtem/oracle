# La forma única del texto sólo se exige en oracle test: juzgar, el MCP, el LSP y los cargadores aceptan otra, y CRLF la elude

- ESTADO: CERRADA
- PRIORIDAD: 90
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 11:41:21 UTC)

2026-09-26, origen: AUDITORIA-3.md de una-sintaxis (Codex). DECISIÓN (Claude, con delegación de Brian): el invariante se exige en el único lugar por donde pasan todas las entradas, no en cada comando. (1) Los cargadores de fuentes de autoría de un proyecto (medidas y macros .oracle, casos .caso, relaciones .relacion; las funciones cargar_fuente_* y lo que use oracle test, juzgar, mutar, contexto y el MCP para leer el catálogo) rechazan un texto que no sea exactamente el del impresor (sin contar líneas de comentario), con un error que muestre el diff corto y «oracle formatear <ruta> --escribir». (2) El MCP, cuando recibe una medida como texto, exige lo mismo y devuelve el diff en el error. (3) El LSP no se rompe: publica un diagnóstico «fuera de la forma única» con la versión formateada. (4) CRLF: un fin de línea \r\n es error (el texto válido usa \n), y oracle formatear lo convierte a \n; lo mismo para un archivo sin salto final si el impresor lo termina con uno. (5) README:604-608 todavía presenta .json junto a la superficie y dice que ambos cargan por igual, en la sección para quien escribe medidas: dejar sólo la superficie y mencionar el JSON como formato de intercambio. (6) Los lectores de archivos .json se QUEDAN (intercambio y migración, decisión de una-sintaxis): no se tocan. (7) Tests: cada entrada (test, juzgar, MCP, LSP, cargadores) con un texto variante de las auditorías y con CRLF; y todo el repo tiene que seguir cargando (ya está formateado). Sin cambiar el significado de nada: sólo qué texto se acepta.

### Nota (2026-09-26 11:56:17 UTC)

Implementado: comparación compartida con el impresor en cargadores .oracle (medidas y macros), .caso y .relacion; lectura sin normalizar CRLF; error con diff corto e instrucción formatear. JSON conserva sus lectores. MCP rechaza texto variante; LSP diagnostica y muestra versión formateada; formatear convierte CRLF y falta de LF; README enseña superficie y reserva JSON para intercambio. Tests nuevos cubren variantes, CRLF y falta de LF en cargadores, MCP, LSP, test y juzgar. Evidencia ejecutada: python3 -m unittest discover -s tests -t .: 2635 tests OK; python3 tools/guia.py --escribir: 0 salidas actualizadas; python3 tools/sitio.py --escribir: rc 0; python3 tools/cli.py test --rapido: SINTAXIS OK, CIFRAS OK, VEREDICTO VERDE. No corrí la mutación ni hice commits. Tarea sigue ABIERTA.

## Próximo paso

Revisar el diff de esta implementación y decidir el cierre de la tarea; permanece ABIERTA y sin commit.

### Nota (2026-09-26 11:59:26 UTC)

2026-09-26, Claude: verificado en un proyecto temporal: juzgar rechaza una medida fuera de forma y una con CRLF (con diff), test también, formatear corrige ambas y juzgar queda verde. Unida. La mutación va en la ronda del corte.
