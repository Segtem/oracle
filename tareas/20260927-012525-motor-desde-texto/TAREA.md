# La API de Python recibe medidas escritas en JSON: falta Motor.desde_texto con la forma única

- ESTADO: CERRADA
- PRIORIDAD: 85
- ETIQUETAS: oracle

### Nota (2026-09-27 01:25:25 UTC)

2026-09-27, pregunta de Brian: ¿están corregidas las múltiples entradas que usa un LLM? Revisado: archivos (test, juzgar, medida probar, revisar), MCP, LSP, contexto y Motor.desde_proyecto exigen la forma única; Motor.desde_datos recibe medidas como listas JSON en memoria y NO hay constructor que reciba texto, así que un modelo que usa Python escribe la medida en JSON sin pasar por la superficie ni el impresor. Las 16 auditorías no lo marcaron porque el encargo admitía JSON de intercambio. ENCARGO (agy2, en contenedor, en su worktree): (1) Motor.desde_texto(textos: Iterable[str], *, macros de la biblioteca estándar, registro, limites como desde_datos): cada texto es una medida o macro en superficie .oracle; se lee con el lector de nucleo.sintaxis y se exige la forma única igual que los cargadores (nucleo.forma.error_forma contra el impresor, sin contar líneas #; CRLF y falta de salto final son error); un texto fuera de forma levanta ErrorDeMotor con el diff. (2) Docstring de desde_datos: es la API programática sobre el árbol canónico (lo que ya se guardó o generó un programa), no una forma de escribir medidas. (3) README.md (sección de la API) y docs/tutorial-practico.md: enseñar desde_texto para medidas escritas, desde_proyecto para un proyecto; desde_datos sólo como árbol canónico. (4) Tests en tests/test_motor_desde_texto.py: carga una medida canónica; rechaza doble espacio, CRLF, sin salto final, mas(a, b); acepta líneas #; la medida cargada evalúa igual que desde_datos con el mismo árbol. Restricciones: python3 -B; no toques tools/mutar_codigo.py ni perfiles/; suite entera verde; si el sitio queda vencido corré python3 tools/sitio.py --escribir y python3 tools/cifras.py --actualizar. Sin commits. Al terminar escribí tareas/<esta>/AVANCE.md.

### Nota (2026-09-27 01:38:09 UTC)

Implementado Motor.desde_texto con validación de forma única, tests en tests/test_motor_desde_texto.py, docs actualizadas y cifras al día. Suite de 2709 tests en verde.

## Próximo paso

Revisar los cambios realizados en el worktree y, cuando se habilite la realización de commits, realizar el commit de cierre `20260927-012525-motor-desde-texto: done` con la tarea marcada CERRADA.

### Nota (2026-09-27 01:42:19 UTC)

2026-09-27, Claude: revisado e incorporado. agy2 agregó Motor.desde_texto (10 tests), el docstring de desde_datos y la documentación en README y tutorial-practico; verifiqué el ejemplo del README (rojo con valor 12). Cambio de Claude sobre esa entrega: el bloque leer → versión → forma única estaba escrito cuatro veces (cargador de medidas, cargador de macros y dos en desde_texto); ahora es UNA función, nucleo.forma.datos_en_forma_unica, que usan los dos cargadores y el Motor, así que una grafía que no carga en un lado no carga en ninguno. desde_texto quedó en una sola pasada (macros primero). El MCP y tools/sintaxis.py --leer siguen con su propio bloque porque tienen mensajes de error con contrato propio y tests. Suite 2709 OK. Pendiente: mutar motor.py, nucleo/forma.py, medida.py y macro.py en el próximo corte (con mutacion-niveles).
