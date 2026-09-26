# Una sola sintaxis para escribir Oracle: la superficie; el JSON canónico queda como formato interno

- ESTADO: ABIERTA
- PRIORIDAD: 90
- ETIQUETAS: oracle, sintaxis, una-sintaxis

### Nota (2026-09-26 02:34:37 UTC)

2026-09-26, DECISIÓN de Brian: una sola sintaxis. Hoy conviven cuatro maneras de escribir: la superficie (.oracle/.caso: Oracle, 58 medidas y 210 casos), el JSON canónico, el JSON con macros escrito a mano (Jam 41 medidas y 35 casos; LyraGASP 29 y 194) y, en expresiones, a + 1 junto a mas(a, 1) (5 usos). Las relaciones sólo existen en JSON. Un LLM aprende de ejemplos y ve dos idiomas. Qué queda: la SUPERFICIE es la única forma de escribir medidas, casos y relaciones; el JSON canónico sigue siendo el formato interno y de intercambio (es lo que muta la mutación, lo que mide L2 y lo que guarda el diferencial) y Oracle lo sigue leyendo, pero nadie lo escribe a mano. Subtareas: convertir-lote, relaciones-superficie, aritmetica-unica, oracle-a-superficie, meta-una-sintaxis, docs-una-sintaxis; y en los consumidores, una-sintaxis en Jam y en LyraGASP. Terminado cuando: los tres repos no tienen medidas, casos ni relaciones en JSON escrito a mano; la documentación sólo enseña la superficie (el JSON aparece únicamente donde se explica la forma canónica); y una medida meta lo vigila. Sale con sintaxis 0.8 (junto con espera: sin_evidencia) y una menor de distribución.

### Nota (2026-09-26 04:03:53 UTC)

2026-09-26, ENCARGO de auditoría (Codex, con shell, adversarial): ¿Oracle tiene hoy UNA sola sintaxis para escribir? Buscar en contra, EJECUTANDO. Para cada cosa que un autor escribe —medida, caso, relación, macro (defmacro), expresión, umbral, requiere, evidencia dentro de un caso, configuración del proyecto— listar TODAS las formas que Oracle acepta hoy (lector de superficie, lector JSON, formas funcionales como mas(), escapes como «fila {…}» en .caso, sinónimos de palabras clave, órdenes alternativos, mayúsculas) y, por cada una: si se enseña (docs, manual, plantillas, mensajes de error, oracle nueva/caso/relaciones --escribir, MCP, LSP, contexto), si se imprime (el impresor la produce) y si sólo se acepta por compatibilidad. Recorrer todos los puntos de entrada del paquete: CLI, MCP (tools/mcp.py), LSP (tools/lsp.py), oracle contexto, oracle manual, plantilla sensor-prosa, biblioteca nueva, perfiles empaquetados, ejemplos, docs y README. Distinguir tres categorías con evidencia: (a) sintaxis de ESCRITURA única, (b) formas que se aceptan al leer pero nadie produce ni enseña, (c) segundas formas que todavía se enseñan o se producen = hallazgo. Para (b) recomendar si conviene retirarlas (con el costo de compatibilidad) o dejarlas. Escribir el informe en tareas/<esta>/AUDITORIA.md con cada comando ejecutado y su salida recortada, y una tabla final. Sin cambiar código. Sin commits.

### Nota (2026-09-26 04:08:40 UTC)

Auditoría adversarial ejecutada y documentada en AUDITORIA.md. Hallazgos reproducidos: MCP acepta y enseña medida JSON; convertir imprime JSON; contexto muestra accesores AST; README presenta formatos dobles; macro admite dos cuerpos; caso acepta tabla y escape; relación acepta JSON incluso en .oracle. Sin cambios de código ni commits.

### Nota (2026-09-26 06:28:21 UTC)

Segunda auditoría adversarial completada y documentada en AUDITORIA-2.md. Verificado el cierre de las segundas formas previas (MCP, convertir, contexto, README, macros, mas/menos/por, col, .oracle con relación). Identificadas segundas formas nuevas (agrupar, donde encadenado, variantes .relacion, sintaxis version) y remanente editorial en docs/tutorial-practico.md:684.

### Nota (2026-09-26 11:34:12 UTC)

2026-09-26, ENCARGO de la TERCERA auditoría (Codex, con shell, adversarial): después de AUDITORIA.md (Codex) y AUDITORIA-2.md (agy) se cerraron macro-invocacion-unica, lectores-heredados, ensenanza-una-sintaxis y forma-unica-texto (el texto válido es exactamente el del impresor; oracle formatear). Repetí en contra, EJECUTANDO, cada prueba de las dos auditorías anteriores (cada fila de sus tablas y cada forma nueva de AUDITORIA-2) y decí si sigue abierta o cerrada. Después buscá formas NUEVAS: la pregunta es si existe CUALQUIER texto distinto del que escribe el impresor que Oracle acepte como medida, caso, relación o macro de un proyecto (por oracle test, juzgar, MCP, LSP, formatear, convertir), o cualquier lugar del paquete que enseñe o produzca otra forma. Probá especialmente los bordes del invariante: comentarios, líneas en blanco, espacios al final, tabs, CRLF, BOM, archivos sin salto final, y si el invariante corre también en juzgar/MCP/LSP o sólo en oracle test. Escribí tareas/<esta>/AUDITORIA-3.md con los comandos, las salidas recortadas y una tabla final (forma, estado, evidencia) y un veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 11:40:17 UTC)

Tercera auditoría adversarial ejecutada y documentada en AUDITORIA-3.md. Reproduje las variantes de AUDITORIA.md y AUDITORIA-2.md, hallé aceptación de texto no impreso fuera de oracle test, bypass CRLF de forma única y remanente editorial en README:604-608. Sin cambios de código ni commits.

### Nota (2026-09-26 11:59:39 UTC)

2026-09-26, ENCARGO de la CUARTA auditoría (Codex, con shell, adversarial): después de AUDITORIA-3.md se cerró forma-unica-entradas (la forma única se exige al cargar en test, juzgar, MCP y cargadores; el LSP la diagnostica; CRLF y el salto final faltante son error; README corregido). Repetí EN CONTRA, ejecutando, cada fila abierta de las tablas de AUDITORIA-2 y AUDITORIA-3 y decí si sigue abierta. Después buscá cualquier entrada que todavía acepte, como medida, caso, relación o macro de un proyecto, un texto de superficie distinto del que escribe el impresor (probá también oracle medida probar/revisar/expandir, caso generar, contexto, mutar, censar, biblioteca, estudio y los ejemplos empaquetados) y cualquier lugar del paquete que enseñe o produzca otra forma de escribir. El JSON de archivos .json se acepta por decisión como formato de intercambio: no lo cuentes como hallazgo salvo que algo lo enseñe como forma de escribir. Escribí tareas/<esta>/AUDITORIA-4.md con comandos, salidas recortadas, tabla final y un veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 12:11:35 UTC)

2026-09-26, Claude: AUDITORIA-4 (Codex) dio no por un solo punto: ESPECIFICACION enseñaba la línea «sintaxis MAYOR.MENOR» y que un .oracle viejo carga sin tocarlo. Al corregirlo apareció algo más grande: por la regla de la propia especificación (caso 3), que formas aceptadas pasen a ser error es MAYOR, así que esto no es la sintaxis 0.8 sino la 1.0; como 0.8 no se publicó, VERSION_SINTAXIS pasa a 1.0 y la crónica cuenta todo lo que entró. En la rama tsx1: la especificación reescrita (la versión la pide oracle.json, no el archivo; el texto válido es el del impresor). ENCARGO a Codex: los tests que fijan versiones 0.x a mano (fixtures de biblioteca con sintaxis 0.2, pruebas de compatibilidad que usan 1.0 como incompatible, la del encabezado de versión, test_requiere_orden) pasan a derivarse de VERSION_SINTAXIS o a usar versiones relativas (misma mayor y menor menor = compatible; otra mayor o menor mayor = incompatible), sin debilitar lo que prueban. Suite completa en verde, guía, sitio, test --rapido, cifras. Sin commits.

### Nota (2026-09-26 12:16:56 UTC)

2026-09-26, Codex: actualizado el manifiesto de biblioteca de ejemplo a sintaxis 1.0; las pruebas de compatibilidad usan VERSION_SINTAXIS y versiones relativas para distinguir compatible, menor futura y otra mayor; la prueba de forma única usa la versión vigente para que llegue a ese diagnóstico; test_requiere_orden deriva la versión del núcleo. Verificación: 190 tests focalizados OK; python3 -m unittest discover -s tests -t .: 2635 tests OK; python3 tools/guia.py --escribir: 0 salidas actualizadas; python3 tools/sitio.py --escribir: OK; python3 tools/cli.py test --rapido: VERDE; python3 tools/cifras.py --actualizar: OK. Sin commits.

### Nota (2026-09-26 12:20:22 UTC)

2026-09-26, ENCARGO de la QUINTA auditoría (Codex, con shell, adversarial): después de AUDITORIA-4 la sintaxis pasó a 1.0 y la especificación dejó de enseñar el encabezado de versión y la carga de grafías viejas. Repetí EN CONTRA, ejecutando, todo punto abierto de AUDITORIA-2, -3 y -4 y buscá cualquier texto de superficie distinto del impresor que alguna entrada acepte como medida, caso, relación o macro de un proyecto, y cualquier lugar del paquete (docs, especificación, manual, contexto, MCP, LSP, plantillas, ejemplos, mensajes de error, notas de release de esta versión) que enseñe o produzca otra forma de escribir. JSON en archivos .json: admitido como intercambio por decisión; no es hallazgo salvo que algo lo enseñe como forma de escribir. Escribí tareas/<esta>/AUDITORIA-5.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 12:25:24 UTC)

2026-09-26, quinta auditoría adversarial ejecutada en AUDITORIA-5.md. Hallazgos reproducidos: tools/sintaxis.py --leer acepta .oracle no canónico; ejemplo/caso-observado enseña y produce un caso JSON en corpus. Entradas principales ensayadas rechazan variantes. AUDITORIA-4.md no está en este checkout. Sin cambios de código ni commits.

## Próximo paso

Revisar AUDITORIA-5.md y corregir las dos segundas vías reproducidas: la entrada `tools/sintaxis.py --leer` para grafías no canónicas y la receta `ejemplo/caso-observado` que genera casos JSON; completar las notas de sintaxis 1.0 y volver a auditar.

### Nota (2026-09-26 12:35:06 UTC)

2026-09-26, Claude: AUDITORIA-5 (Codex) dio no por dos puntos, arreglados: tools/sintaxis.py --leer exige la forma única (lee sin convertir fines de línea y compara con el impresor, como los cargadores); la receta ejemplo/caso-observado escribe el caso en .caso con el impresor (antes lo escribía en JSON dentro de corpus/). Tests nuevos para los dos. AUDITORIA-4.md y -5.md, unidas a main.

### Nota (2026-09-26 12:35:18 UTC)

2026-09-26, ENCARGO de la SEXTA auditoría (Codex, con shell, adversarial): después de AUDITORIA-5 se arreglaron sintaxis.py --leer y la receta caso-observado. Repetí EN CONTRA, ejecutando, todo punto abierto de AUDITORIA-2 a -5 y buscá cualquier entrada que acepte, como medida, caso, relación o macro de un proyecto, un texto de superficie distinto del impresor, y cualquier lugar del paquete que enseñe o produzca otra forma de escribir (recetas, ejemplos y scripts de ejemplo/, herramientas de tools/, plantillas, docs, especificación, manual, contexto, MCP, LSP, mensajes de error). JSON en archivos .json: admitido como intercambio; no es hallazgo salvo que algo lo enseñe o produzca como forma de escribir una medida, un caso o una relación. Escribí tareas/<esta>/AUDITORIA-6.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.
