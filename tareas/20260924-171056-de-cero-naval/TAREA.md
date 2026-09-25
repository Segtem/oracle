# La página de cero enseña una medida suelta; falta la guía completa de una batalla naval en HTML5, paso a paso, para quien empieza a programar con un LLM

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: oracle, web, documentacion, guia


## Por qué

2026-09-24, Brian: `docs/de-cero.html` tiene que ser **la guía completa del ejemplo que venimos
haciendo**, una batalla naval en HTML5, paso por paso, para alguien que **recién empieza a programar**
y programa **con un LLM** («vibecoding»). Hoy la página enseña una sola medida
(`documento.nombre_sigue_la_convencion`), y la guía que existe es
`~/TestOracleEjemplo/GUIA22.md` (1171 líneas), que quedó desactualizada: se escribió contra 0.25.2 y
varias cosas cambiaron. Por ejemplo, la omisión silenciosa de `juzgar`, que 0.27 resolvió con
`NO SE APLICARON`; `mas()` en vez de `+`, que 0.30 resolvió; y la ergonomía de 0.29.

## Qué hacer

1. **El código completo del juego**, tomado de `~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280`
   (`index.html`, `css/`, `js/engine.js`, `trace.js`, `ui.js`, `audio.js`, `catalogos/naval/`,
   `corpus/naval/`, `verificar_oraculo.py`, `partida_real.json`), tal como está, dentro del repo en
   `ejemplo/batalla-naval/` para que la página lo enlace y un test lo corra. Brian dice que «le faltó
   más»: la guía lo dice y propone qué seguir, sin inventar que ya está.
2. **La guía, paso por paso**, para quien nunca programó:
   - qué es HTML5, CSS y JS lo justo para leer el juego;
   - cómo pedirle el juego a un LLM y qué revisar de lo que devuelve;
   - por qué el juego emite hechos (`celda_barco`, `tiro`, `partida`) en vez de validarse a sí mismo;
   - cómo escribir cada medida (colocación, turnos, hundimiento, final) en la superficie actual, con
     `a + 1` en vez de `mas(a, 1)`;
   - los casos rojo y verde, `oracle test`, la mutación y qué significa que un mutante sobreviva;
   - `oracle juzgar` sobre una partida real, qué dice `SIN MIRAR` y qué `NO SE APLICARON`;
   - qué le pasa a quien trabaja con un LLM: el postmortem de la batalla naval
     (`vault-kb/postmortems/`) como advertencia, con el verde que no medía nada.
3. **Todo verificable**: cada comando de la guía corre en un test (como `docs/13-primer-valor.md`),
   cada salida de terminal es de una corrida real, y `oracle test` del ejemplo es VERDE en CI.
4. **La página se ve bien en un teléfono** y conserva el estilo del sitio.

Base: GUIA22.md para el recorrido y el tono; naval-0280 para el código. Donde se contradigan, manda la
versión vigente de Oracle.

### Nota (2026-09-24 17:15:40 UTC)

2026-09-24, Brian: de-cero tiene que ser DE CERO, no un repo para bajar. La persona copia y pega y va creando el juego de a poco con oracle-metalenguaje: instala, oracle init, pega el primer HTML, lo abre, pega la primera medida, escribe su primer caso rojo, corre oracle test, lo ve fallar y lo arregla, y así hasta el juego entero. Cada paso es un bloque para copiar, lo que tiene que ver en la pantalla o la terminal, y qué hacer si ve otra cosa. El código en ejemplo/batalla-naval/ no es lo que se baja: es el respaldo que verifica la guía. Un test arma el juego pegando los bloques de la guía en orden, desde un directorio vacío, y corre oracle test después de cada paso; si un bloque de la página cambia, el test lo nota.

### Nota (2026-09-24 17:18:15 UTC)

2026-09-24, Brian: el corpus de naval-0280 está flojo. Medido: 11 medidas en catalogos/naval/ y 2 casos en corpus/naval/ (001-tiro-fuera-de-tablero y 002-tiro-valido), los dos de naval.tiros_dentro_del_tablero; las otras diez no tienen ningún caso. Para la guía: cada medida con al menos un caso rojo (el defecto que atrapa, sacado de una partida plausible) y uno verde, y la mutación de medidas con todos los mutantes muertos. Si un mutante sobrevive, se agrega el caso que lo mata. Y la guía lo enseña como lección: primero muestra que 11 medidas con 2 casos dan verde igual, corre la mutación, ve sobrevivir a los mutantes y escribe los casos que faltan. Es la diferencia entre un verde que mide y uno que decora.

### Nota (2026-09-24 17:20:23 UTC)

2026-09-24, Brian: la guía tiene que ser pedagógica: que plantee preguntas y dé soluciones, y que meta al lector en el pensamiento de Oracle. Forma de cada paso: primero una pregunta que el lector puede intentar contestar solo (¿qué tendría que ser cierto en una partida para que este tiro sea legal?, ¿qué partida pondría roja esta medida?, ¿qué no está mirando?), un espacio para pensarlo (un <details> plegado con la solución), y después la respuesta con el código. Las preguntas recorren el modo de pensar de Oracle: el producto emite hechos y no se juzga a sí mismo; una regla nombra el defecto, no la virtud; antes de la medida va el caso rojo; cada medida dice qué NO mira (alcance) y por qué ese número (porque); un verde sin casos que lo puedan romper es decoración; SIN MIRAR y NO SE APLICARON son parte de la respuesta, no letra chica. Cuando el lector trabaja con un LLM, la guía le enseña qué preguntarle y qué desconfiar de lo que devuelve.

### Nota (2026-09-25 03:30:29 UTC)

2026-09-25, Claude: la guía está escrita en docs/de-cero.md (se genera como de-cero.html, primera página de Empezar), en la rama t-web-diseno: qué es HTML/CSS/JS lo justo, cómo pedirle el juego a un LLM, por qué el juego cuenta hechos (celda_barco, tiro, partida, con una fila real de partida_real.json), la primera medida línea por línea, los casos, la mutación con la medición real de hoy (11 medidas y 2 casos: ROJO por mutación), cuatro medidas más (alternancia con t1.turno + 1, solapamiento, flota con requiere, veracidad con sin), juzgar una partida con SIN MIRAR y NO SE APLICARON, qué le falta al juego y cinco consejos para trabajar con un LLM. Faltan las salidas de terminal marcadas como pendientes, que salen de corridas reales cuando Codex deje ejemplo/batalla-naval en verde (punto 1 de esta tarea, encolado para las 01:40).

### Nota (2026-09-25 05:00:49 UTC)

Punto 1 y verificación del 3: copié naval-0280 a ejemplo/batalla-naval sin tocar el origen; cambié mas(...) por + en dos medidas, corregí enlaces file://, y declaré construidos los 2 casos originales porque no hay observación verificable. Agregué 31 casos .caso (003–033): rojo y verde de alternancia, límites de barcos, solapamiento, fin, flota, ganador, repetición, continuidad y veracidad de impactos. Los extras 023–028 cubren los cuatro bordes fila/columna; 029–030 fijan requiere ante relaciones vacías; 031 y 033 distinguen fila de turno en tiros repetidos; 032 fija el filtro de impacto positivo. Resultado: 33 casos, 19 rojos, 14 verdes; 209/209 mutantes muertos. verificar_oraculo.py ahora juzga partida_real.json guardada y falla si no detecta una infracción; tests/test_ejemplo_batalla_naval.py exige VERDE del ejemplo y juicio verde de la partida.

### Nota (2026-09-25 05:01:34 UTC)

Verificación final: python3 -m unittest discover -s tests: 2515 tests, OK; cd diferencial/referencia && python3 -m unittest: 48 tests, OK; python3 tools/cli.py test --rapido: VERDE; python3 tools/cli.py test --proyecto ejemplo/batalla-naval: VERDE, 209/209 mutantes muertos; python3 ejemplo/batalla-naval/verificar_oraculo.py: VERDE en 11 medidas y cuatro infracciones detectadas; python3 tools/cifras.py --actualizar ejecutado. tools/sitio.py no existe en este checkout. equivalentes.json no requirió cambios: no se movieron líneas referidas. Sin commits por .git de sólo lectura.

### Nota (2026-09-25 05:24:38 UTC)

2026-09-25, Codex: implementé tools/guia.py y tests/test_guia.py. El arnés arma batalla-naval desde una carpeta temporal vacía con los bloques archivo/incluir, ejecuta los 9 bloques bash paso en orden (uv tool install se saltea; oracle usa tools/cli.py), normaliza rutas y tiempos, compara las salidas y --escribir las actualiza. Completé las 9 salidas reales de docs/de-cero.md y regeneré docs/de-cero.html con tools/sitio.py --escribir. Desajuste confirmado: el paso 8 pedía juzgar hechos_partida.json, pero ese archivo sólo se mencionaba como descarga manual y no lo creaba ningún bloque; añadí el bloque archivo=hechos_partida.json incluir=ejemplo/batalla-naval/partida_real.json antes del comando, sin cambiar el comando ni la prosa. La partida juzgada da verde en 11 medidas; al quitar tiro, 7 quedan en NO SE APLICARON. Verificación: python3 tools/guia.py (9 pasos, 0 salidas viejas), python3 tools/sitio.py y python3 -m unittest discover -s tests (2533 tests, OK). Sin commits.

## Próximo paso

Claude: revisar docs/de-cero.html en un teléfono y ajustar el diseño si algún bloque o tabla desborda; después verificar python3 tools/guia.py y python3 tools/sitio.py antes de cerrar la tarea.
