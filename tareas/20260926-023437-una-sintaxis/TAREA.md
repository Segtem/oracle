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

### Nota (2026-09-26 12:35:06 UTC)

2026-09-26, Claude: AUDITORIA-5 (Codex) dio no por dos puntos, arreglados: tools/sintaxis.py --leer exige la forma única (lee sin convertir fines de línea y compara con el impresor, como los cargadores); la receta ejemplo/caso-observado escribe el caso en .caso con el impresor (antes lo escribía en JSON dentro de corpus/). Tests nuevos para los dos. AUDITORIA-4.md y -5.md, unidas a main.

### Nota (2026-09-26 12:35:18 UTC)

2026-09-26, ENCARGO de la SEXTA auditoría (Codex, con shell, adversarial): después de AUDITORIA-5 se arreglaron sintaxis.py --leer y la receta caso-observado. Repetí EN CONTRA, ejecutando, todo punto abierto de AUDITORIA-2 a -5 y buscá cualquier entrada que acepte, como medida, caso, relación o macro de un proyecto, un texto de superficie distinto del impresor, y cualquier lugar del paquete que enseñe o produzca otra forma de escribir (recetas, ejemplos y scripts de ejemplo/, herramientas de tools/, plantillas, docs, especificación, manual, contexto, MCP, LSP, mensajes de error). JSON en archivos .json: admitido como intercambio; no es hallazgo salvo que algo lo enseñe o produzca como forma de escribir una medida, un caso o una relación. Escribí tareas/<esta>/AUDITORIA-6.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 12:39:48 UTC)

2026-09-26, sexta auditoría adversarial documentada en AUDITORIA-6.md. Confirmé corregidas las dos vías de AUDITORIA-5 con ejecución. Hallazgos: LSP codeLens interpreta medidas fuera de forma única; caso-observado/README aún indica destino .json; docs/14-sensor-prosa enseña catálogos JSON; ayuda de tools/medida.py aún usa archivo.json. Sin cambios de código ni commits.

## Próximo paso

Revisar AUDITORIA-11.md (veredicto: «una sola sintaxis de escritura: sí») y proceder al cierre de la tarea `una-sintaxis`.

### Nota (2026-09-26 12:54:05 UTC)

2026-09-26, Claude: AUDITORIA-6 (Codex) dio no por cuatro puntos, arreglados: codeLens del LSP devuelve [] si el texto está fuera de la forma única (test que falla sin el arreglo); README de caso-observado dice <id>.caso; docs/14-sensor-prosa ya no ofrece catálogos JSON; la ayuda y el comentario de tools/medida.py dicen .oracle. Un test viejo del LSP le pasaba una línea en blanco tras un comentario (fuera de forma) y se ajustó. AUDITORIA-6.md, unida a main.

### Nota (2026-09-26 12:54:05 UTC)

2026-09-26, ENCARGO de la SÉPTIMA auditoría (Codex, con shell, adversarial): después de AUDITORIA-6 se arreglaron codeLens, caso-observado/README, docs/14-sensor-prosa y la ayuda de tools/medida.py. Repetí EN CONTRA, ejecutando, todo punto abierto de AUDITORIA-2 a -6 y buscá cualquier entrada que acepte, como medida, caso, relación o macro de un proyecto, un texto de superficie distinto del impresor (incluidas vistas del editor: diagnósticos, lentes, completado, hover), y cualquier lugar del paquete que enseñe o produzca otra forma de escribir (recetas, ejemplos y scripts de ejemplo/, herramientas de tools/, plantillas, docs, sitio generado, especificación, manual, contexto, MCP, LSP, mensajes de error y --help). JSON en archivos .json: admitido como intercambio; no es hallazgo salvo que algo lo enseñe o produzca como forma de escribir una medida, un caso o una relación. Escribí tareas/<esta>/AUDITORIA-7.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 13:12:09 UTC)

2026-09-26, Claude: AUDITORIA-7 (Codex) dio no por tres puntos, arreglados: (1) el impresor de casos fija el orden de origen (tipo, repo, commit, plan, cuando_utc, comando, registro, evidencia_sha256, estado; otros campos después, alfabéticos), que es el que ya tenía todo el corpus: 0 archivos a reformatear; (2) el plan de ejemplo de tools/observar.py apunta a una medida .oracle; (3) verificar_instalacion escribe la medida y la relación de prueba con los impresores (.oracle, .relacion). Al correr verificar_instalacion desde un clon limpio apareció un defecto que la auditoría no vio: package-data de la plantilla sensor-prosa seguía con globs .json, así que el wheel salía sin sus 15 casos ni su relación; y su README importaba nucleo.caso, que sólo existe en el repo. Arreglados; WHEEL OK.

### Nota (2026-09-26 13:12:09 UTC)

2026-09-26, ENCARGO de la OCTAVA auditoría (Codex, con shell, adversarial): después de AUDITORIA-7 se fijó el orden de origen en el impresor de casos, observar enseña .oracle, verificar_instalacion escribe superficie y el wheel lleva los .caso/.relacion de la plantilla. Repetí EN CONTRA, ejecutando, todo punto abierto de AUDITORIA-2 a -7. Buscá además, como clase: (a) cualquier otro campo de medida, caso o relación cuyo orden o disposición deje dos textos distintos que el impresor devuelva tal cual (dos canónicos para el mismo contenido); (b) cualquier entrada que acepte, como medida, caso, relación o macro de un proyecto, un texto distinto del impresor; (c) cualquier lugar del paquete —incluido el wheel construido con uv build y lo que instala oracle plantilla— que enseñe o produzca otra forma de escribir. JSON en archivos .json: admitido como intercambio; no es hallazgo salvo que algo lo enseñe o produzca como forma de escribir una medida, un caso o una relación. Escribí tareas/<esta>/AUDITORIA-8.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 13:23:13 UTC)

2026-09-26, Claude: AUDITORIA-8 (Codex) dio no por dos cosas. (1) El manual (CLI y HTML) enseñaba la resta «también sin espacios (a-b)», que el cargador rechaza: corregido, dice que se escribe con un espacio a cada lado. (2) Casos que sólo difieren en el orden de relaciones, columnas o claves de objetos pasaban los dos como canónicos. DECISIÓN (Claude, por delegación): no es una segunda grafía sino otro árbol. Forma única quiere decir un texto por árbol; ese orden es orden de lectura que elige quien escribe (evento: corrida, t, actor, que) y el impresor lo conserva, como gofmt conserva el orden de campos de un literal. Ordenarlo alfabéticamente desordenaría la lectura de todos los corpus. La excepción es origen, metadato, que desde AUDITORIA-7 tiene orden fijo. Quedó escrito en ESPECIFICACION.md, en la sección de la versión de la superficie.

### Nota (2026-09-26 13:23:13 UTC)

2026-09-26, ENCARGO de la NOVENA auditoría (Codex, con shell, adversarial): después de AUDITORIA-8 el manual enseña la resta con espacios y ESPECIFICACION.md define forma única como UN TEXTO POR ÁRBOL: el orden de relaciones, columnas y claves de objetos (salvo origen) es parte del árbol y no cuenta como hallazgo; sí cuenta cualquier par de textos distintos que den el MISMO árbol (mismo JSON, orden incluido) y carguen los dos. Repetí EN CONTRA, ejecutando, todo punto abierto de AUDITORIA-2 a -8, y buscá: (a) dos textos distintos con el mismo árbol que el cargador acepte; (b) cualquier entrada que acepte, como medida, caso, relación o macro de un proyecto, un texto distinto del impresor; (c) cualquier lugar del paquete —incluidos el wheel construido con uv build, lo que instala oracle plantilla, el manual, contexto, la ayuda de cada comando, el sitio en docs/ y los mensajes de error— que enseñe o produzca una forma que el cargador rechaza o que no sea la superficie. JSON en archivos .json: intercambio admitido; no es hallazgo salvo que algo lo enseñe o produzca como forma de escribir. Escribí tareas/<esta>/AUDITORIA-9.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 13:33:23 UTC)

2026-09-26, Claude: AUDITORIA-9 (Codex) dio no por un solo punto: una línea de comentario agregada da otro texto con el mismo árbol y carga. DECISIÓN (Claude, por delegación): los comentarios se quedan —un lenguaje que no se puede comentar es peor, y gofmt hace la misma excepción—, pero la regla pública lo dice: ESPECIFICACION.md define la forma única como un texto por árbol sin contar las líneas que empiezan con # (después de la sangría), y aclara que no existe el comentario al final de una línea con código (verificado: el lector lo rechaza). La ayuda de formatear dice «las líneas # no cuentan y se conservan». Sin otros hallazgos: el resto de la tabla quedó cerrado o fuera de la definición.

### Nota (2026-09-26 13:33:23 UTC)

2026-09-26, ENCARGO de la DÉCIMA auditoría (Codex, con shell, adversarial): la definición pública vigente está en ESPECIFICACION.md (sección de la versión de la superficie): forma única = UN TEXTO POR ÁRBOL SIN CONTAR LAS LÍNEAS DE COMENTARIO COMPLETAS; el orden de relaciones, columnas y claves (salvo origen) es parte del árbol. Agregar o quitar líneas # NO es hallazgo. Repetí EN CONTRA, ejecutando, todo punto abierto de AUDITORIA-2 a -9, y buscá: (a) dos textos distintos, fuera de líneas de comentario completas, con el mismo árbol (mismo JSON, orden incluido), que el cargador acepte; (b) cualquier entrada que acepte, como medida, caso, relación o macro de un proyecto, un texto distinto del impresor fuera de esas líneas; (c) cualquier lugar del paquete —wheel construido con uv build, oracle plantilla, manual, contexto, ayuda de cada comando, sitio en docs/, mensajes de error— que enseñe o produzca una forma que el cargador rechace o que no sea la superficie; (d) si la definición pública, tal como está escrita, contradice lo que el código hace. JSON en .json: intercambio admitido; no es hallazgo salvo que algo lo enseñe o produzca como forma de escribir. Escribí tareas/<esta>/AUDITORIA-10.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 13:41:54 UTC)

2026-09-26, Claude: AUDITORIA-10 (Codex) dio no por un solo punto editorial: la nota de release 0.30.0 (y docs/notas.html) mostraba t1.turno-1 como escritura válida. La nota es historia y no se reescribe; se le agregó una aclaración en línea: desde sintaxis 1.0 (0.32.0) el guion se lee igual pero se escribe t1.turno - 1. Barrí además NOTAS-DE-RELEASE.md y docs/notas/ buscando mas(, menos(, por(, col(, encabezado sintaxis y unidades entre corchetes: lo demás es historia contada como historia («hasta 0.29.0 había que escribir mas(…)»).

### Nota (2026-09-26 13:41:54 UTC)

2026-09-26, ENCARGO de la UNDÉCIMA auditoría (Codex, con shell, adversarial): mismo criterio que la décima (definición pública en ESPECIFICACION.md: un texto por árbol sin contar líneas de comentario completas; el orden de relaciones, columnas y claves salvo origen es parte del árbol). Texto histórico (crónica de la especificación, notas de release de versiones publicadas) es hallazgo SÓLO si presenta como vigente una forma que hoy se rechaza sin decir que cambió. Repetí EN CONTRA, ejecutando, todo punto abierto de AUDITORIA-2 a -10, y buscá: (a) dos textos distintos, fuera de líneas de comentario completas, con el mismo árbol, que el cargador acepte; (b) cualquier entrada que acepte, como medida, caso, relación o macro de un proyecto, un texto distinto del impresor fuera de esas líneas; (c) cualquier lugar del paquete —wheel construido con uv build, oracle plantilla, manual, contexto, ayuda de cada comando, sitio en docs/, mensajes de error— que enseñe o produzca una forma que el cargador rechace o que no sea la superficie; (d) contradicciones entre la definición pública y el código. JSON en .json: intercambio admitido. Escribí tareas/<esta>/AUDITORIA-11.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 13:57:50 UTC)

2026-09-26, Undécima auditoría adversarial finalizada y documentada en AUDITORIA-11.md. Se reejecutaron todas las variantes de AUDITORIA-2 a -10, se comprobó la aclaración de t1.turno-1 en NOTAS-DE-RELEASE.md y docs/notas.html, empaquetado de wheel con uv build e instalación en venv limpio de /tmp, plantilla sensor-prosa con oracle test VERDE, y validación estricta en cargadores, CLI, MCP y LSP. Veredicto: una sola sintaxis de escritura: sí.

### Nota (2026-09-26 13:58:50 UTC)

2026-09-26, Claude: la undécima auditoría la hizo agy (Docker) porque Codex llegó a su límite de uso a mitad de la corrida. Veredicto: «una sola sintaxis de escritura: sí». Verifiqué a mano tres de sus afirmaciones (sin LF final, resta sin espacios y JSON dentro de un .oracle: los tres rechazados por cargar_fuente_medida). Pendiente antes del corte: una confirmación independiente de Codex cuando vuelva a tener cupo, porque el «sí» es de un solo auditor.

### Nota (2026-09-26 16:14:59 UTC)

2026-09-26, ENCARGO de la DUODÉCIMA auditoría (Codex, con shell, adversarial): confirmación INDEPENDIENTE del «sí» de AUDITORIA-11, que hizo agy. No la tomes como cierta: tu trabajo es refutarla. Mismo criterio público (ESPECIFICACION.md, sección de la versión de la superficie): forma única = un texto por árbol sin contar líneas de comentario completas; el orden de relaciones, columnas y claves salvo origen es parte del árbol; texto histórico es hallazgo sólo si presenta como vigente una forma que hoy se rechaza. Repetí EN CONTRA, ejecutando, todo punto de AUDITORIA-2 a -11, y buscá: (a) dos textos distintos, fuera de líneas de comentario completas, con el mismo árbol, que el cargador acepte; (b) cualquier entrada que acepte, como medida, caso, relación o macro de un proyecto, un texto distinto del impresor fuera de esas líneas; (c) cualquier lugar del paquete —wheel construido con uv build, oracle plantilla, manual, contexto, ayuda de cada comando, sitio en docs/, mensajes de error— que enseñe o produzca una forma que el cargador rechace o que no sea la superficie; (d) contradicciones entre la definición pública y el código. JSON en .json: intercambio admitido. Escribí tareas/<esta>/AUDITORIA-12.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 16:26:11 UTC)

2026-09-26, Claude: AUDITORIA-12 (Codex, confirmación independiente del «sí» de agy) dio no por un punto: la especificación permite líneas # completas en las tres superficies, pero el lector de .relacion las rechazaba (y con él cargador, formatear y LSP). Se arregló el código, no la especificación: relacion.leer ignora las líneas # como ya hacían sintaxis y caso. Test que falla sin el arreglo (carga, formatear conserva los comentarios, LSP sin diagnósticos). nucleo/relacion.py se vuelve a mutar.

### Nota (2026-09-26 16:26:11 UTC)

2026-09-26, ENCARGO de la DECIMOTERCERA auditoría (Codex, con shell, adversarial): igual que la duodécima (mismo criterio público, mismos cuatro frentes a-d, todo punto de AUDITORIA-2 a -12 repetido en contra), después de que .relacion pasó a admitir líneas # completas. Contrastá además, superficie por superficie (.oracle, .caso, .relacion, macros), CADA afirmación de la definición pública de ESPECIFICACION.md contra lo que hace el código. Escribí tareas/<esta>/AUDITORIA-13.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 16:37:26 UTC)

2026-09-26, Claude: AUDITORIA-13 (Codex) dio no por un punto: en .caso, una línea # dentro de la prosa (sintoma) entraba como texto y dentro de origen o evidencia cortaba el bloque (30 de 66 posiciones fallaban). DECISIÓN (Claude): la regla es léxica, como en .oracle y .relacion: una línea cuyo primer carácter no blanco es # es comentario en cualquier lugar. El parser de casos las descarta antes de leer y guarda el número real de cada línea para los errores; el impresor se niega a escribir una línea de prosa que empiece con # (ningún corpus de los cuatro repos la tiene). Test: un comentario en cada una de las posiciones de un caso real deja el mismo árbol, carga, y formatear lo conserva; falla sin el arreglo (4 fallas, 11 errores). ESPECIFICACION.md lo dice. nucleo/caso.py se vuelve a mutar.

### Nota (2026-09-26 16:37:27 UTC)

2026-09-26, ENCARGO de la DECIMOCUARTA auditoría (Codex, con shell, adversarial): igual que la decimotercera (mismo criterio público, mismos cuatro frentes, todo punto de AUDITORIA-2 a -13 repetido en contra, y cada afirmación de la definición pública contrastada superficie por superficie). La regla de comentarios es ahora explícitamente léxica en las cuatro superficies (.oracle, macros, .caso, .relacion): probá, por INSERCIÓN EXHAUSTIVA en cada posición de un archivo real de cada superficie, que una línea # completa no cambia el árbol, carga, formatear la conserva y el LSP no diagnostica. Escribí tareas/<esta>/AUDITORIA-14.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 16:48:02 UTC)

2026-09-26, Claude: AUDITORIA-14 (Codex) dio no por un solo punto, y dijo no haber encontrado ninguna segunda grafía de superficie cargable: tools/sondear_procedencia.py escribía sus casos temporales como .json. Ahora los escribe en .caso con el impresor, y cargar_casos los lee con la forma única incluida. Barrí tools/ y nucleo/ buscando otros productores de medidas, casos o relaciones en JSON: sólo quedan oracle.json (configuración), informes y un chequeo de medida.py que no pisa un borrador .json existente.

### Nota (2026-09-26 16:48:02 UTC)

2026-09-26, ENCARGO de la DECIMOQUINTA auditoría (Codex, con shell, adversarial): igual que la decimocuarta (mismo criterio público, los cuatro frentes, inserción exhaustiva de comentarios en las cuatro superficies, todo punto de AUDITORIA-2 a -14 repetido en contra). Incluí además, como productor, cualquier script de tools/, ejemplo/ o perfiles/ que escriba una medida, un caso, una relación o una macro, aunque sea en un temporal. Escribí tareas/<esta>/AUDITORIA-15.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 17:04:20 UTC)

2026-09-26, Claude: la decimoquinta la hizo agy porque Codex agotó su cupo semanal (vuelve el 2026-09-30). Veredicto: «una sola sintaxis de escritura: sí» (680/680 inserciones de comentario en 11 archivos de las cuatro superficies, ningún productor JSON, wheel y plantilla verdes). Como en la undécima agy dijo sí y Codex encontró después tres defectos (comentarios en .relacion, comentarios en bloques de .caso, un productor JSON interno), se pide una confirmación independiente a agy2.

### Nota (2026-09-26 17:04:20 UTC)

2026-09-26, ENCARGO de la DECIMOSEXTA auditoría (agy2, con shell, adversarial): confirmación INDEPENDIENTE del «sí» de AUDITORIA-15. Tu trabajo es refutarlo. Mismo criterio público (ESPECIFICACION.md, sección de la versión de la superficie). Las tres últimas auditorías que dieron no encontraron cosas que la anterior había declarado cerradas: (1) comentarios # dentro de bloques (prosa, origen, evidencia, variantes); (2) una herramienta interna que escribía casos en JSON a un temporal; (3) el wheel sin los archivos de la plantilla. Buscá DEFECTOS DE ESA FORMA: posiciones, herramientas y archivos que la auditoría anterior no probó. Además los cuatro frentes: (a) dos textos distintos fuera de líneas # con el mismo árbol, que carguen; (b) una entrada que acepte un texto distinto del impresor; (c) un lugar del paquete que enseñe o produzca una forma que el cargador rechace o que no sea la superficie; (d) contradicciones entre la definición pública y el código. Escribí tareas/<esta>/AUDITORIA-16.md con comandos, salidas recortadas, tabla final y veredicto de una línea: «una sola sintaxis de escritura: sí» o «no, porque …». Sin cambiar código. Sin commits.

### Nota (2026-09-26 17:17:01 UTC)

2026-09-26, Claude: AUDITORIA-16 (agy2, confirmación independiente) también dio «una sola sintaxis de escritura: sí»: 870/870 inserciones de comentario en archivos y posiciones que la decimoquinta no había probado (guarda, sin, unir, resuelto, limite_humano, espera), 120 comentarios con caracteres especiales, ningún productor JSON, 26 variantes no canónicas rechazadas en las cuatro superficies, wheel y plantilla verdes. Dos «sí» seguidos después de cinco rondas de arreglos. Cuando Codex vuelva (2026-09-30) conviene una auditoría más de Codex, que fue el que encontró los últimos defectos; no bloquea el corte.
