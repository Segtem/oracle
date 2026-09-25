# Auditoría: dónde puede quedar todavía un falso verde en el núcleo

- ESTADO: CERRADA
- PRIORIDAD: 85
- ETIQUETAS: oracle, auditoria, flaqueza


## Qué hacer

Brian (2026-09-24): «sin puntos flojos». El álgebra 1.0 (tarea `algebra-10`) cierra cuatro falsos
verdes: predicados no booleanos, `null`, claves no validadas y testigos. Buscar los que quedan, en
`nucleo/` (álgebra, medida, proyecto, sintaxis, caso, relación) y en `tools/juzgar.py` y
`tools/aceptacion.py`: todo camino en que una medida, un caso o un proyecto puedan salir VERDE sin
haber medido lo que dicen medir. Por ejemplo: una excepción capturada que se vuelve verde, un valor
por omisión que pasa por medición, una relación vacía sin `requiere`, una comparación que coacciona
tipos. Cada hallazgo con archivo:línea, la entrada concreta que lo dispara y si ya lo cubre un test o
una medida meta. Descartar lo que no se pueda sostener con cita. En `HALLAZGOS.md`.

## Avance

Se completó la auditoría del núcleo y herramientas (`nucleo/` y `tools/`) y se volcaron 8 hallazgos respaldados con cita `archivo:línea`, entrada concreta que los dispara y estado de cobertura en `HALLAZGOS.md`:
1. `nucleo/medida.py:482-484`: `requiere` simple evalúa la verdad de la lista cruda sin llamar a `separar_clave`, por lo que una relación con solo cabecera `["clave", ...]` y 0 filas no activa `faltante` y da verde `<=` 0 en vez de `SIN EVIDENCIA`.
2. `nucleo/algebra.py:1063-1069`: `_unir_donde_indexado` admite tanto `int` como `str` vía `_clave_indexable`, silenciando el `ErrorDeAlgebra` que el camino ingenuo levanta por incompatibilidad de tipos escalares (`nucleo/algebra.py:372-374`), produciendo 0 filas y verde.
3. `nucleo/medida.py:705-707` y `tools/juzgar.py:340-348`: `Informe.perdona` no revisa `sin_evidencia`, perdonando como deuda de código una ausencia total de evidencia cuando la medida en sombra tiene cota >= 0.
4. `nucleo/macros/ninguno.oracle:4-12`, `peor.oracle:4-12`, `ninguno-par.oracle:4-14`: macros base de la biblioteca estándar emitidas sin cláusula `requiere`, dando verde con relación vacía.
5. `nucleo/algebra.py:591-592`: `_agregar` retorna `0` predeterminado para `max`, `min` y `promedio` ante listas vacías.
6. `tools/juzgar.py:159-170, 348`: medidas propias del proyecto no aplicadas por falta de relaciones en la evidencia no invalidan `Informe.ok` ni impiden que `juzgar` salga con código 0 (verde global).
7. `nucleo/marco.py:287-289`: `hechos_de_casos` fuerza `dio = esperado` si la medida no existe en el catálogo, dando falso verde en L2 para `meta.el_caso_se_pone_como_debe`.
8. `nucleo/algebra.py:793, 875-876`: `donde` y `sin` evalúan veracidad booleana de Python sin forzar tipo estricto `bool`.

### Nota (2026-09-25 02:48:12 UTC)

2026-09-25, Claude, verificado ejecutando el núcleo: CONFIRMADOS dos falsos verdes. (1) requiere con una relación que trae sólo la cabecera ["clave", ["id"]] y ningún hecho no sale SIN EVIDENCIA: con umbral <= 0 da VERDE (ok=True, valor 0). (2) unir … donde con == entre un número y un texto: el camino indexado no encuentra la pareja y da VERDE en silencio, cuando el mismo == en un donde suelto es ErrorDeAlgebra por tipos incompatibles. El 8 ya está en algebra-10. El 7 es deliberado y está documentado en nucleo/marco.py (de la falta se ocupa otra medida). 3 (la sombra perdona un sin_evidencia), 4 (las macros base sin requiere), 5 (agregados sobre cero filas dan 0, que dice la especificación) y 6 (medidas no aplicadas que no invalidan el veredicto) son preguntas de diseño, no defectos comprobados: van a Brian con recomendación.

### Nota (2026-09-25 21:42:20 UTC)

2026-09-25, ENCARGO ronda 2 (Codex, con shell): la ronda 1 (agy, sin shell) dejó 2 falsos verdes confirmados y arreglados, y las preguntas de diseño se decidieron en verde-diseno. Anoche apareció otro que nadie había listado (caso-silencioso): la aceptación delegaba el juicio de cada caso a una medida meta que sólo existe con catalogo_base, y con catalogo_base false el caso se descartaba en silencio y oracle test salía VERDE. El patrón a cazar: un camino de verificación que hace continue/pass/return temprano, o delega en algo opcional (catálogo base, políticas meta, sombra, --medida, --parcial, fixtures vencidos, casos sin medida, relaciones ausentes, escalares no confiadas), y termina en VERDE u OK sin haber mirado. Recorrer tools/cli.py cmd_test, tools/aceptacion.py, tools/mutar.py, tools/diferencial.py, tools/corpus.py, tools/juzgar.py, nucleo/medida.py, nucleo/marco.py, tools/cierre (ejemplo/seguimiento-tareas/cierre_medidas.py) y el MCP. Para cada sospecha: armar un proyecto mínimo en un directorio temporal y EJECUTAR; sólo es hallazgo si se reproduce. Por cada hallazgo reproducido: un test que falle, el arreglo mínimo en el lugar por donde pasan todos los caminos, y el test en verde. Lo que sea una decisión de diseño y no un defecto, se anota con la reproducción y una recomendación, sin arreglar. Registrar en tareas/<esta>/RONDA2.md cada sospecha con su comando de reproducción y el resultado (hallazgo / descartado y por qué).

### Nota (2026-09-25 21:56:06 UTC)

2026-09-25, Codex, ronda 2: un falso verde nuevo reproducido y corregido: oracle_juzgar del MCP daba ok=true con una medida propia no aplicada, mientras la CLI daba rojo. Test rojo antes y verde después en tests/test_auditoria_ronda2.py; criterio completo compartido en Informe.ok_completo. La sospecha SIN EVIDENCIA de aceptación se reprodujo, pero es decisión de diseño vigente (casos 029/030 de batalla naval y 006 de primer valor); no se cambió. Reproducciones y descartes en RONDA2.md. Suite completa: 2573 tests OK; tools/guia.py OK; tools/sitio.py --escribir OK; cli test --rapido VERDE tras actualizar cifras. Sin commits; tarea abierta.

## Próximo paso

Revisar con Brian la recomendación de `RONDA2.md` para declarar `sin_evidencia` como resultado esperado distinto del rojo medido en los casos que prueban `requiere`; decidir si se incorpora esa distinción al esquema de casos y a la aceptación.

### Nota (2026-09-25 21:59:50 UTC)

2026-09-25, Claude: ronda 2 revisada y unida (el falso verde del MCP, con test que fallaba antes). La pregunta de diseño de la fila 2 pasa a su propia tarea, sin-evidencia-esperada, porque cambia la sintaxis de los casos; mientras tanto la mutación cubre el riesgo. Entre las dos rondas quedaron cerrados cuatro falsos verdes (requiere con cabecera sola, unir con tipos, caso descartado sin catálogo base, MCP con medidas sin aplicar) y los caminos de continue/pass de aceptación, mutar, diferencial, corpus, juzgar, cierre y MCP quedaron recorridos con su reproducción en RONDA2.md.
