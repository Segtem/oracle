# Custodiar las sondas y dejar de matar por accidente

**2026-09-10 · continuación de 0.14.0**

## Las sondas que sostienen DECISION-004

`metamorficas.py` genera las esquinas que juzgan las dos medidas de sintaxis. La aceptación ya
salía 0 por defectos reales encontrados y corregidos, como explica
[El último rojo de DECISION-004](EL-ULTIMO-ROJO-DE-DECISION-004.md). Ese cierre no demostraba que el
generador conservaría las esquinas: perderlas en silencio podía dejar verdes las dos medidas.

Se incorporó a `HERRAMIENTAS_CUSTODIAS`, a `PRIORIDADES` y a la matriz de CI. Su módulo nuevo tiene
16 tests que fijan errores, color, valor, multiplicidad de testigos, transformaciones y contenido
de sondas. Una referencia legible, capturada del código publicado 0.14.0, fija las 97 medidas
candidatas y los 8 casos candidatos. No se regenera para acompañar al código: conserva identidad,
tipos y contenido, además de los tests independientes sobre grupos sin agregados y campos con
espacios, comas y tabulaciones.

No se declararon equivalentes nuevos. Se borraron decisiones redundantes bajo sus premisas:
las fuentes y pasos llegan validados por `Medida`; una unión anidada tiene `unir` en su raíz;
una conjunción validada tiene dos operandos; `contar` no evalúa la expresión. La inserción al inicio
de `sys.path` se expresa directamente, sin un índice numérico redundante. La entrada directa usa
el patrón de los otros instrumentos para no ejecutar el CLI al importarse.

Los contrastes individuales aplicaron cada mutante en copias del árbol. La primera ronda completa
cerró en **241 muertos y 1 sobreviviente de 242**, sin timeouts ni errores de arnés. El retorno de
la ayuda sobrevivía porque `SystemExit(None)` y `SystemExit(0)` salen ambos 0. Un test directo del
retorno falló al aplicar ese mutante a mano (1 fallo, 0 errores). La ronda completa posterior dio
**242/242**, sin sobrevivientes, timeouts, errores de arnés ni equivalentes declarados.

El instrumento también rechaza argumentos sobrantes con código 2 y ayuda en español, en lugar de
ignorarlos. El intento inicial de medirlo fuera del perfil expuso otro defecto: `mutar_codigo`
resolvía objetivos antes de su bloque de diagnóstico. Ahora informa ese error con su protocolo
humano o JSON, sin escapar como traceback.

## El CLI: el denominador viejo no probaba toda la conducta

El relevo ya advertía que 82 mutantes caían por referencias posicionales vencidas de equivalentes.
La premisa de uno de esos equivalentes era falsa: decía que ningún dato del diagnóstico podía
contener Unicode. Una instalación real en una ruta `oráculo` produce esa tilde en
`oracle.corriendo_desde`; el mutante de `ensure_ascii` la escapa. La forma JSON sigue parseando al
mismo objeto, pero la salida para lectura humana cambia. Se comprobó en una copia real y se agregó
un test con el diagnóstico real y una ruta de instalación con tilde, sin inventar un campo.

Se retiró esa declaración. Para la sangría se construye directamente el texto de dos espacios,
eliminando la cantidad numérica equivalente y conservando los bytes de salida. Con ambas entradas
fuera, las referencias vencidas ya no pueden hacerse pasar por discriminación del CLI.

El contraste de 509 sitios intermedios primero corrió los tests prioritarios de vigilar, biblioteca
y CLI; los que no distinguieron se probaron contra reportar, censar y manual. No se llamó
«sobreviviente de la suite» al resultado parcial. Muchos murieron con tests existentes que faltaban
en el perfil. Para los demás se fijaron los rechazos de reportar, el retorno y las opciones de
contexto, los formatos del manual y sus códigos. El test del límite de ilegibles comparaba contra
la propia constante mutada: se fijó el contrato de 10 visibles y 23 restantes para 33 entradas,
y la frontera de exactamente 10 sin anunciar cero restantes.

## Rendimiento medido

En la misma máquina, `tests.test_herramientas` pasó de **18,413 a 4,239 segundos**. Se trasladaron
los ocho tests de `ModoSombra` a `tests.test_sombras_integracion`; su AST es idéntico. El módulo
nuevo sigue en discovery y es prioridad de aceptación. No se desactivó ninguna sombra ni se quitó
una integración. La suite completa conserva ese trabajo: la mejora es que un mutante puede morir
antes de pagarlo.

El perfil de una integración localiza el costo en agrupaciones del evaluador sobre productos de
relaciones meta, con validación repetida de expresiones. No se cambió el núcleo: una optimización
que cacheara validaciones necesita justificar qué puede mutar en las expresiones y en el registro
de escalares. El perfil identifica trabajo repetido; no demuestra por sí solo esa inmutabilidad.

## Errores que ahora se pueden leer

- Diagnóstico rechaza otra bandera como destino y describe errores de escritura sin traceback.
- Convertir informa directorios, UTF-8 roto y formas inválidas de JSON, `.oracle` y `.caso`, con ruta
  y código 1. Conserva el fragmento de error de sintaxis cuando está disponible.
- Manual rechaza una bandera como destino de instalación. También rechaza un tema desconocido
  aunque se repita como destino: antes una condición especial lo borraba y devolvía 0. La premisa
  equivocada era que las opciones del manual ya se habían quitado de los argumentos posicionales;
  `sin_banderas_comunes` sólo quita las opciones comunes, no `--instalar-man`.
- El test de redacción de rutas usa un hogar temporal controlado. Conserva el solapamiento entre
  hogar y proyecto, sin exigir escribir en el hogar real de quien ejecuta la suite.

## Cierre completo del CLI

La ronda completa final dio **509/509 en 452,61 segundos** (7 min 33 s), sin sobrevivientes,
timeouts, errores de arnés ni equivalentes declarados. El perfil pone primero reportar: sus 21
tests tardaron 0,003 s localmente, sin contar el arranque del intérprete. CLI entra en CI por estar
por debajo de los ~10 minutos; no se cambió ese umbral. `CUSTODIAS_SIN_MEDIR` queda vacía y las
15 custodias están en la matriz.

Una ronda anterior se interrumpió tras 450 mutantes completados porque un test nuevo del despacho
podía entrar accidentalmente en `oracle test` bajo mutación y lanzar otra suite. **No cuenta como
ronda completa.** Se fijó también la prohibición de llamar a ese comando al pedir contexto: el
original pasó los 8 tests del grupo y el mutante aplicado a mano produjo 1 fallo, 0 errores, en
0,003 s. Después se repitió la ronda entera, que es la cifra de cierre anterior.

Manifiestos y salidas: [metamorficas](2026-09-10-custodias/metamorficas.json),
[CLI](2026-09-10-custodias/cli.json), [salida de metamorficas](2026-09-10-custodias/metamorficas.log)
y [salida del CLI](2026-09-10-custodias/cli.log). Las huellas identifican el código y soporte
medidos; los cambios posteriores de configuración de CI y documentación no se presentan como
parte de esas rondas. El nuevo test de custodia fija además que no se borren a la vez de ambas
listas para esconder su ausencia.

Las salidas conservan una limitación previa: `proceso.test_con_mutante_que_lo_mata`, que consume
campos de mutantes de medidas, no puede juzgar estas filas de mutación de código. No se agregó un
campo ficticio ni se ocultó el diagnóstico. Las tres medidas aplicables al protocolo de código
quedaron verdes; los manifiestos distinguen fallo de tests, timeout y error del arnés.

## Alcance

La mutación fija los operadores del mutador sobre estas fuentes y esta suite. No prueba ausencia
de cualquier defecto ni completa la gramática por enumeración universal. La referencia de sondas
protege las esquinas conocidas; un espacio que todavía no genera sigue requiriendo medición propia.
No cambió ninguna medida, umbral, clasificación antigua ni cota de sombras.
