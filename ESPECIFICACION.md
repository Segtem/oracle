# Especificación del álgebra

La versión vigente está en la primera línea de §0, declarada de forma **legible por máquina** en `nucleo/version.py`
(`VERSION_ALGEBRA`). Esta prosa la cita, no la define: la define el dato, y la regla de qué cambio
sube qué parte del número está en §0. **Escrita para ser rota**: el criterio de si sirve está al
final, y es comprobable.

> **Qué cambió respecto de `0.1`, y por qué.** La implementación encontró dos cosas.
> **(a)** El acceso a datos pasó a ser **explícito** (`["campo", alias, nombre]`, `["hecho", alias]`)
> en vez de la forma corta `["penetracion", "a", "b"]` que publicaba la 0.1: si un string suelto
> significara «alias», un dato de texto que coincida con un alias cambiaría de sentido según el
> contexto. Es más verboso y no tiene casos raros.
> **(b)** Los operadores se incorporan sólo cuando los piden medidas reales. `con` y la unión
> izquierda se retiraron de la especificación activa al no alcanzar dos usuarios — ver §3.
> **(c)** La 0.3 resuelve la contradicción entre “conjunto” y la multiplicidad real: una relación es
> una **bolsa sin orden semántico**. La decisión completa está en
> [`docs/decisiones/DECISION-001-RELACIONES-COMO-BOLSAS.md`](docs/decisiones/DECISION-001-RELACIONES-COMO-BOLSAS.md).
> **(d)** La 0.4 hace explícito de dónde sale cada umbral con el campo `segun`: medición,
> contrato, convención o tanteo.
> **(e)** La 0.5 permite que una escalar declare la unidad de cada argumento; una declaración vieja
> sigue cargando, pero su unidad no se considera derivable hasta completar ese dato.
> **(f)** La 0.6 permite declarar el `ambito` opcional de una medida; una medida vieja conserva
> `sin_declarar`, pero una implementación del álgebra completo tiene que conocer el nodo nuevo.

Regla de diseño que gobierna todo el documento: **no se agrega un operador hasta que una segunda
medida lo necesite.** Es lo único que evita que esto se vuelva el proyecto que reemplaza al proyecto.

---

## 0. La versión del lenguaje

La versión es un dato, no una frase. Vive en `nucleo/version.py` como `VERSION_ALGEBRA`, con la
forma `MAYOR.MENOR` (dos enteros). Sin una regla que diga qué cambio sube qué parte, el número es
decorativo; con ella, la incompatibilidad se detecta en vez de descubrirse.

La distribución se versiona aparte como `VERSION_DISTRIBUCION`, con `MAYOR.MENOR.PARCHE`, porque
también cambia cuando cambia una herramienta sin cambiar el lenguaje.

**Versiones vigentes: álgebra `1.0`, sintaxis `0.8`, distribución `0.31.1`.**

Esa línea es lo primero que necesita quien va a implementar el álgebra sin ver el núcleo, y hasta
0.23.2 no estaba: había que deducirla del último párrafo de una crónica de veinte cortes, varios de
los cuales dicen «`VERSION_ALGEBRA` queda en `0.6`». Lo reclamó el autor de la implementación de
referencia en [`DECISIONES.md`](diferencial/referencia/DECISIONES.md). No envejece a mano: un test la
compara contra `nucleo/version.py`, y si alguien sube una versión y no toca esta línea, la suite se
pone en rojo.

Lo que sigue es la **crónica**: un párrafo por corte, con el argumento de por qué subió lo que subió.
Se queda acá, y no en las notas de release, porque es lo que vuelve discutible la regla de más abajo
—un número sin su argumento no se puede auditar—. Va del corte más nuevo al más viejo, y un test lo
comprueba. Para saber en qué versión está el lenguaje no hace falta recorrerla: está en la línea de
arriba.

**Sintaxis 0.8 (2026-09-26): `VERSION_SINTAXIS` sube de `0.7` a `0.8`.** Un caso de defecto
puede declarar `espera: sin_evidencia` después de `etiqueta` en `.caso`, o
`"espera": "sin_evidencia"` en JSON. Es el único valor admitido y no vale con
`verde_correcto`. La aceptación exige ese resultado exacto; un caso de defecto sin el campo
exige un rojo medido. El impresor conserva el campo. La declaración de relaciones gana la
superficie `.relacion`: campos tipados en líneas, unidad obligatoria para números, variantes y
alcance explícito; el JSON canónico sigue cargando. Sube la menor por estas escrituras nuevas;
el álgebra queda en `1.0` y la distribución en `0.31.1` hasta el próximo corte.

**Corte 0.31.1 (2026-09-26): `VERSION_DISTRIBUCION` sube de `0.31.0` a `0.31.1`.** Cierra dos
caminos que daban verde sin haber mirado y dos imprecisiones de `juzgar`. Un caso que no sale como declara su etiqueta tumba la
aceptación también sin catálogo base: antes el juicio lo daba sólo una medida meta del catálogo
base, y con `catalogo_base: false` el caso se descartaba en silencio. El `oracle_juzgar` del MCP ya no
aprueba con una medida propia sin aplicar: juzga con el mismo criterio que la CLI. `oracle juzgar`
acepta la cabecera `["clave", …]` de §1 y no cuenta un SIN EVIDENCIA entre las medidas en rojo. La
huella de un directorio de procedencia ignora las entradas ocultas y `__pycache__` (§6): dos checkouts
del mismo commit daban huellas distintas. Sube el **parche**: son correcciones; el álgebra y la
sintaxis no cambian. Cierra `caso-silencioso`, `auditoria-verde`, `huella-estado-local`,
`prosa-deuda`, `entrada-unica` y `notas-indice`.

**Corte 0.31.0 (2026-09-25): `VERSION_DISTRIBUCION` sube de `0.30.0` a `0.31.0`.** Sale el
álgebra 1.0 (párrafo siguiente) y se cierran los caminos a un verde que no midió nada: una medida
propia sin casos pone rojo `oracle test` y se nombra; `oracle nueva` crea la medida con un caso rojo
y uno verde de andamio, y el verde no llega mientras sigan siendo andamio. Desde `verde-diseno`, una
sombra perdona
un rojo dentro de su cota, pero nunca un `SIN EVIDENCIA`: falta la relación necesaria para
juzgar. Las macros `ninguno`, `ninguno-par` y `peor` siguen abiertas: una relación de
infracciones vacía puede significar éxito. Se agregan `ninguno-par-requiere` y
`peor-requiere` a `ninguno-requiere`. **Si la relación es el universo a evaluar, se usa la
variante `-requiere`** para impedir un verde sin sujetos. Los agregados sobre cero filas
siguen dando `0`, también `max`, `min` y `promedio`; la guarda de existencia es `requiere`,
no el agregado. `oracle juzgar` sin selección falla con código 1 si alguna medida propia
no se aplicó; `--parcial` permite explícitamente una corrida modular y `--medida` selecciona
un subconjunto. `--json` conserva `no_aplicadas` y refleja el resultado en `ok`.
Los seis arneses que custodian la mutación entran ellos mismos a la mutación, el perfil declara qué
queda afuera y por qué, y las cinco guías con comandos se ejecutan en la suite. Dos arreglos salen
de la propia ronda de mutación del corte: el arnés publicaba `null` como código de salida y las
medidas de proceso no podían juzgar la corrida (ahora `-1`), y la unión indexada daba error con
claves booleanas donde el producto ingenuo unía, y sus errores no decían en qué paso (ahora da el
mismo resultado y el mismo mensaje que el producto). Sube la **menor**: `VERSION_ALGEBRA` sube a `1.0` y cambian salidas de la CLI.
Cierra `algebra-10` en el núcleo (los consumidores migran sus `null` antes de subir),
`medida-sin-casos`, `verde-diseno`, `nueva-con-casos`, `auditoria-nuevo`, `huecos-spec`, `custodia`,
`perfil-mutacion`, `guias-cli`, `guias-ejecutables`, `web-diseno` y `de-cero-naval`.

**Álgebra 1.0 (2026-09-25): `VERSION_ALGEBRA` sube de `0.8` a `1.0`.** Cambia el
significado de medidas existentes: los testigos son las filas finales de `desde`; `donde`,
`sin`, `requiere` condicional y cada operando de `y`, `o`, `no` exigen un booleano; antes de medir
se validan las claves de toda la evidencia recibida y se rechaza cualquier campo `null` explícito.
Una relación con cabecera `clave` y cero hechos es vacía para `requiere`. La unión indexada
aplica el mismo error de tipos incompatibles que la comparación ordinaria. Sube la **mayor**
porque estas entradas antes podían dar un resultado diferente, incluso verde. Distribución y
sintaxis conservan sus versiones.

**Corte 0.30.0 (2026-09-24): `VERSION_DISTRIBUCION` sube de `0.29.0` a `0.30.0`.** Sale la sintaxis
0.7 (párrafo siguiente): un LLM escribe `a + 1` o `t1.turno-1` y Oracle lo lee como `mas`/`menos`, sin
cambiar la forma canónica. El repositorio queda en el motor: las decisiones en `docs/decisiones/`, las
guías y el contrato del MCP en `docs/`, los planes y estudios en `vault-kb/`; `oracle mutar` ya no
manda a leer un archivo que el paquete instalado no trae. Sube la **menor** por la sintaxis nueva.
`VERSION_ALGEBRA` queda en `0.8`. Cierra `aritmetica`, `repo-limpio` y `web-028`.

**Sintaxis 0.7 (2026-09-24): `VERSION_SINTAXIS` sube de `0.6` a `0.7`.** La superficie
acepta `a + b`, `a - b` y `a * b` con precedencia usual, asociación a izquierda y paréntesis;
`-` siempre es resta dentro de una expresión, aun sin espacios (`t1.turno-1`, `a.x-a.y`). Los
nombres de macro con guion siguen válidos en encabezados. El
lector los traduce a las escalares existentes `mas`, `menos` y `por`. Los literales negativos
siguen siendo números y el impresor conserva las llamadas funcionales. Sube la **menor** porque
se agregan escrituras sin cambiar ningún árbol canónico ni su significado. `VERSION_ALGEBRA`
queda en `0.8`; sale con la distribución `0.30.0`.

**Corte 0.29.0 (2026-09-24): `VERSION_DISTRIBUCION` sube de `0.28.0` a `0.29.0`.** Un modelo puede
leer la prosa del catálogo como sensor, nunca como juez: `oracle plantilla sensor-prosa` copia a un
proyecto la relación `afirmacion_prosa`, una medida de ejemplo, un corpus y un sensor opcional que
Oracle no invoca. El lenguaje avisa mejor (`requiere` fuera de lugar, escalares no confiadas,
relaciones duplicadas, `init --help`), el MCP deja de devolver cuerpos al listar tareas y su contrato
se genera desde el código, y `oracle test --todo` separa el plazo de la línea base del de cada
mutante. Sube la **menor**: hay un verbo nuevo (`plantilla`) y cambian salidas de la CLI.
`VERSION_ALGEBRA` queda en `0.8` y `VERSION_SINTAXIS` en `0.6`. Cierra `jev-pypi`, `sensor-prosa`,
`relacion-duplicada`, `ergo-orden`, `ergo-confianza`, `ergo-observados`, `init-ayuda`,
`timeout-suite-mutacion`, `mcp-tokens`, `refactor` y `codex`: un tercer autor, sin ver la
referencia, encontró tres preguntas que el texto no contestaba —dónde va `ambito`, la aridad de
`y`/`o`, `min`/`max` sobre booleanos—, y ahora están escritas con lo que el núcleo ya hacía.

**Corte 0.28.0 (2026-09-22): `VERSION_DISTRIBUCION` sube de `0.27.0` a `0.28.0`.** Retomar el
trabajo pasa a ser leer una tarea: el tracker encuentra una tarea por su sufijo y sugiere la más
parecida cuando un id no existe, y una tarea puede declarar con qué medidas se cierra —`CIERRA CON:`—,
con una política que cruza ese criterio con los veredictos de la aceptación. `oracle test` dice qué
verificó y que no midió el producto, y un proyecto vacío sale `SIN MEDICIÓN` en vez de VERDE. El tope
de memoria por mutante baja de 4000 a 1024 MiB. Sube la **menor**: el tracker gana un campo y una
relación, y la salida de `oracle test` cambia. `VERSION_ALGEBRA` queda en `0.8` y `VERSION_SINTAXIS`
en `0.6`. Cierra `buscar-sufijo`, `test-alcance`, `primer-valor`, `cierre-medidas` y `memoria`.

**Corte 0.27.0 (2026-09-16): `VERSION_DISTRIBUCION` sube de `0.26.0` a `0.27.0`.** `oracle juzgar`
y la fachada `Motor` perdonan una sombra sólo hasta su cota —por encima, o sin un número que
comparar, el rojo vuelve— y nombran las medidas del catálogo propio que no se aplicaron porque su
relación no vino en la evidencia. El tracker declara como omisión una historia de git superficial. Y
el servidor MCP se pone al día: `oracle_evaluar` informa la sombra, y entran `oracle_juzgar` y
`oracle_tareas`, las dos de sólo lectura. Sube la **menor**: un proyecto con una sombra por encima
de su cota cambia de color, y el paquete gana dos herramientas públicas. `VERSION_ALGEBRA` queda en
`0.8` y `VERSION_SINTAXIS` en `0.6`. Cierra las tareas `20260916-160811-cota-juzgar`,
`20260916-201124-juzgar-omite`, `20260916-160811-superficial` y `20260916-210604-mcp-027`.

**Corte 0.26.0 (2026-09-16): `VERSION_DISTRIBUCION` sube de `0.25.2` a `0.26.0`, `VERSION_ALGEBRA`
de `0.7` a `0.8` y `VERSION_SINTAXIS` de `0.5` a `0.6`.** El álgebra gana la anti-junta: un paso
`["sin", ["de", relación, alias], condición]`, que en la superficie se escribe
`sin <relación> <alias> donde <condición>` y deja pasar las filas que **ninguna** fila de la otra
relación cumple (§3). Sube la **menor** del álgebra porque entra un nodo nuevo y todo lo que valía
significa lo mismo; sube la de la sintaxis por la cláusula nueva; y sube la menor de la distribución
porque un proyecto que la use no carga en 0.25. La prueba de valor: la política del tracker «toda
tarea cerrada tiene su commit de cierre» se escribe ahora en la medida, y el emisor dejó de contar
por ella. La referencia del diferencial se re-derivó contra 0.8 en aislamiento, y las sondas a sus
decisiones dejaron dos rincones que §3 ahora decide. Cierra las tareas `20260916-151553-antijunta` y
`20260916-200751-traceback-mutar`.

**Corte 0.25.2 (2026-09-16): `VERSION_DISTRIBUCION` sube de `0.25.1` a `0.25.2`.** El informe de
`oracle diferencial` queda fijado por tests y su verificador entra a la matriz de mutación de CI
(55/55); la crónica de este párrafo en adelante va en un solo orden, y un test lo comprueba; y el
repositorio gana el estudio con el que Codex va a escribir, de cero, una implementación
independiente del álgebra. Sube el **parche**: nada de lo que un proyecto carga o juzga cambia, y
nadie cambia de color. `VERSION_ALGEBRA` queda en `0.7` y `VERSION_SINTAXIS` en `0.5`. Cierra las
tareas `20260916-035324-informe` y `20260916-151553-cronica`.

**Corte 0.25.1 (2026-09-16): `VERSION_DISTRIBUCION` sube de `0.25.0` a `0.25.1`.**
`oracle relaciones --escribir` deja en `relaciones-por-revisar/` un borrador de cada relación que la
evidencia trae y el proyecto no declara, con lo único que se puede saber mirándola —el tipo de cada
campo, y `sin_unidad` para textos y booleanos— y la unidad de cada número y el alcance vacíos. Sube el
**parche**: el lector no mira esa carpeta, así que nada de lo que un proyecto carga cambia y nadie
cambia de color. `VERSION_ALGEBRA` queda en `0.7` y `VERSION_SINTAXIS` en `0.5`. Cierra la tarea
`20260916-035758-declarar`.

**Corte 0.25.0 (2026-09-16): `VERSION_DISTRIBUCION` sube de `0.24.0` a `0.25.0`.** El arnés de
mutación puede mutar un rango de líneas (`--lineas`) o sitios sueltos (`--sitio`), y una ronda así se
declara **parcial**: lo dice en la primera línea del informe, lo guarda en la evidencia (`parcial` y
`total_sitios`, campos nuevos de `corrida_mutacion`), sale con código 2 —el de ronda inconclusa— y
`proceso.ronda_mutacion_concluyente` la rechaza. Sube la **menor** porque una medida universal cambia
lo que acepta —una ronda parcial ya no cuenta como concluyente— y porque la relación gana dos campos
que la evidencia anterior no tiene. Ningún consumidor conocido emite `corrida_mutacion`: esa evidencia
es de la mutación del propio Oracle, que en un consumidor se saltea. Además entra `commit_seguimiento`
con tres políticas nuevas en el proyecto de ejemplo, que no toca el catálogo distribuido.
`VERSION_ALGEBRA` queda en `0.7` y `VERSION_SINTAXIS` en `0.5`: no entra un nodo, un operador, un
agregado, una escalar ni una relación del lenguaje, y el lector no gana palabras. Cierra las tareas
`20260915-201030-sitios` y `20260915-010452-commits`.

**Corte 0.24.0 (2026-09-16): `VERSION_DISTRIBUCION` sube de `0.23.1` a `0.24.0`.** El arnés de
mutación le pone tope de memoria a cada ejecución de tests (`--limite-memoria-mb`, 4000 por omisión,
`0` desactiva), aplicado en el proceso hijo y recortado al máximo que heredó: un mutante que se queda
sin memoria muere con `MemoryError`, que es un fallo de tests, y ya no se lleva puesta la máquina ni
la ronda. Sube la **menor** y no el parche porque el paquete gana una capacidad que antes había que
poner a mano desde afuera con `ulimit -v`, y porque cambia lo que una ronda mide: un mutante que
antes agotaba el tiempo —o mataba al sistema— ahora muere y la ronda queda concluyente. El corte trae
además el sufijo corto del tracker, la portada que publica su versión y sus cifras medidas, el
workflow propio del tracker en CI, §0 con las versiones vigentes, `juzgar` sin su copia de la regla
de la sombra y los fixtures de dominio con el veredicto entero. `VERSION_ALGEBRA` queda en `0.7` y
`VERSION_SINTAXIS` en `0.5`: no entra un nodo, un operador, un agregado, una escalar ni una relación,
y el lector no gana palabras. Cierra las tareas `20260915-112728-memoria`, `20260915-023924-ci-tareas`,
`20260915-201030-vigente`, `20260915-155111-sombra`, `20260915-010453-sufijo`,
`20260915-155111-equivalente` y `20260915-213158-sitio`.

**Corte 0.23.1 (2026-09-16): `VERSION_DISTRIBUCION` sube de `0.23.0` a `0.23.1`.** El fixture
diferencial puede guardar el veredicto entero —`ok`, `valor` y si la evaluación levantó— y traer
escritas las medidas que usa y no están en ningún catálogo (§6); con eso el diferencial de Oracle
pasa a contrastar `requiere` con condición y evidencia de una relación con variantes, que entraron en
el álgebra `0.7` y que ningún mundo ejercitaba. Sube el **parche** y no la menor: nadie cambia de
color. Las dos formas del veredicto valen, ningún fixture existente deja de validar —los trece de los
dos consumidores conocidos siguen en la forma corta y siguen en verde—, no entra ninguna medida al
catálogo y ninguna cota se mueve. `VERSION_ALGEBRA` queda en `0.7` y `VERSION_SINTAXIS` en `0.5`: no
entra un nodo, un operador, un agregado, una escalar ni una relación, y el lector no gana palabras.
Cierra la tarea `20260915-201030-diferencial`.

**Corte 0.23.0 (2026-09-15): `VERSION_DISTRIBUCION` sube de `0.22.0` a `0.23.0`.**
`meta.toda_medida_declara_su_ambito` pasa de `del_origen` a `universal`: el ámbito se le exige a todo
proyecto que seleccione el catálogo, no sólo a Oracle. Sube la **menor** por el mismo criterio que
0.9.0 —una medida universal puede volver rojo a un consumidor que actualiza sin usar nada nuevo—, y
acá el rojo es cierto: una medida sin `ambito` lo recibe. Los dos consumidores conocidos declararon
sus 68 medidas antes del corte, así que salen en cero, pero eso es un hecho de sus catálogos y no una
garantía. `VERSION_ALGEBRA` queda en `0.7` y `VERSION_SINTAXIS` en `0.5`: no entra un nodo, un
operador, un agregado, una escalar ni una relación, el lector no gana palabras, y `sin_declarar` se
sigue leyendo y escribiendo igual —lo que cambia es a quién obliga la medida que lo persigue—. Cierra
la tarea `20260915-155111-ambito`, abierta desde el plan de 0.5.0.

**Corte 0.22.0 (2026-09-15): `VERSION_DISTRIBUCION` sube de `0.21.0` a `0.22.0`.** La menor agrega
una relación del lenguaje (`campo_leido`), una medida universal (`meta.toda_medida_lee_campos_que_existen`),
la declaración de los campos de lo que emite el núcleo (`CAMPOS_DE_RELACIONES`, §1.1), ocho relaciones de
proceso declaradas y un campo nuevo en `Informe` (`no_juzgaron`, §3). `VERSION_ALGEBRA` queda en `0.7` y
`VERSION_SINTAXIS` en `0.5`: `campo_leido` es una relación de hechos como `sombra` o `verbo_del_cli`, el
álgebra sigue levantando ante un campo ausente y ninguna forma canónica ni palabra de la superficie
cambia. Cierra la tarea `20260915-155654-campos`.

**Corte 0.21.0 (2026-09-15): `VERSION_DISTRIBUCION` sube de `0.20.0` a `0.21.0`, `VERSION_ALGEBRA`
de `0.6` a `0.7` y `VERSION_SINTAXIS` de `0.4` a `0.5`.** El álgebra sube la **menor**: una entrada de
`requiere` puede llevar condición y la declaración de una relación gana `variantes` (§1.3, §2); lo que
ya valía significa lo mismo —una medida sin condición conserva su forma canónica y su veredicto, y los
nombres simples de `requiere` siguen cargando con la regla de `0.6`—. La sintaxis sube la **menor**
porque el lector gana `requiere <relación> <alias> donde <condición>` y varias líneas `requiere`
seguidas; un `.oracle` anterior se lee idéntico. `mutante` pasa a ser una relación declarada con dos
variantes y las dos medidas de `proceso` filtran por `tipo`. La implementación de referencia del
diferencial se re-derivó contra `0.7` con otro autor aislado (`diferencial/referencia/PROCEDENCIA.md`).
Cierra la tarea `20260915-155111-mutante`.

**Corte 0.20.0 (2026-09-15): `VERSION_DISTRIBUCION` sube de `0.19.0` a `0.20.0`.** La menor
cambia el contrato de la fachada pública: `Motor.desde_proyecto` selecciona con `catalogo_efectivo`
—con `catalogo_base`, las medidas `del_origen` de Oracle ya no juzgan al consumidor— y aplica la
`sombra` de `oracle.json`, así que el mismo proyecto recibe el mismo veredicto por `Motor`, por
`oracle test` y por `oracle juzgar`. `Informe` suma `en_sombra` (vacío por defecto): `ok` no cuenta
los rojos en sombra, `texto()` los marca y `a_json()` informa `en_sombra` por medida. Cierra la tarea
`20260915-010454-motor`. `VERSION_ALGEBRA` queda en `0.6` y `VERSION_SINTAXIS` en `0.4`.

**Corte 0.19.0 (2026-09-15): `VERSION_DISTRIBUCION` sube de `0.18.1` a `0.19.0`.** La menor
agrega a la superficie de `oracle tarea` un lenguaje de consultas —`listar <consulta>`,
`desetiquetar --consulta`— con contrato propio: gramática de tatr en español, tipos verificados al
compilar y código 2 para una consulta inválida; además `listar --explicar/--por-id/--invertir`,
`referencias` sin ID dentro de una tarea e `init --sin-readme`. El lenguaje de consultas de tareas
es del tracker, no del metalenguaje: `VERSION_ALGEBRA` queda en `0.6` y `VERSION_SINTAXIS` en `0.4`.

**Corte 0.18.1 (2026-09-15): `VERSION_DISTRIBUCION` sube de `0.18.0` a `0.18.1`.** Sube la
**revisión**: `oracle juzgar` cumple el código de salida que ya declaraba 0.18.0 —2 para una
evidencia que no se puede consultar— en vez de terminar en traceback. No cambia ningún contrato,
álgebra ni sintaxis.

**Corte 0.18.0 (2026-09-15): `VERSION_DISTRIBUCION` sube de `0.17.0` a `0.18.0`.** La menor
agrega el verbo público `oracle juzgar` (`oracle proyecto juzgar`), con un contrato de salida propio:
0 verde, 1 rojo fuera de sombra o ninguna medida aplicable, 2 entrada o proyecto inválidos; `--json`
suma `en_sombra` por medida. Se retira `ejemplo/seguimiento-tareas/evaluar.py`. `VERSION_ALGEBRA`
queda en `0.6` y `VERSION_SINTAXIS` en `0.4`: el verbo selecciona con `catalogo_efectivo` y evalúa
con el álgebra existente, sin nodos, operadores ni gramática nuevos. La fachada
`Motor.desde_proyecto` sigue cargando con `catalogos_a_cargar` y no aplica sombras; queda registrado
como tarea `20260915-010454-motor`.

**Corte 0.17.0 (2026-09-14): `VERSION_DISTRIBUCION` sube de `0.16.0` a `0.17.0`.** La menor
agrega verbos a la superficie pública `oracle tarea` (`etiquetar`, `desetiquetar`, `grafo`) y un
archivo auxiliar al formato persistente (`tareas/etiquetas`); `resumen --json` suma
`descripciones` y `sin_etiquetas` sin quitar campos. `VERSION_ALGEBRA` queda en `0.6` y
`VERSION_SINTAXIS` en `0.4`: el tracker no toca el núcleo, ni la lectura o evaluación de
archivos `.oracle` y `.caso`.

**Corte 0.16.0 (2026-09-13): `VERSION_DISTRIBUCION` sube de `0.15.0` a `0.16.0`.** La menor
incorpora la superficie pública `oracle tarea`: registros en carpetas con Markdown, captura y
consulta de contexto, seguimiento frente a Git y hechos para políticas optativas. Se agrega un
formato persistente y comandos nuevos, siguiendo el precedente de herramientas de 0.7.0.
`VERSION_ALGEBRA` queda en `0.6` y `VERSION_SINTAXIS` en `0.4`: las políticas usan nodos, operadores
y gramática existentes; no cambia la lectura ni la evaluación de archivos `.oracle` o `.caso`,
ni se incorporan formas canónicas. El tracker no impone condiciones nuevas al catálogo universal.

**Corte 0.15.0 (2026-09-11): `VERSION_DISTRIBUCION` sube de `0.14.0` a `0.15.0`.** Sube la
**menor** porque cambia el contrato de salida de herramientas: `diagnostico --salida --rapido`
antes escribía un archivo llamado `--rapido` y salía 0; ahora rechaza la falta de destino y sale 1.
`tools/metamorficas.py` también pasa de ignorar argumentos desconocidos con éxito a rechazarlos
con código 2. Que sean correcciones de entradas erróneas no elimina el cambio observable por una
automatización. Las custodias nuevas, los mensajes y el rendimiento por sí solos no exigirían una
menor. `VERSION_ALGEBRA` queda en `0.6`: no cambia ningún nodo, operador ni significado; resolver
límites y registro una vez por expresión conserva la validación de cada nodo en cada fila.
`VERSION_SINTAXIS` queda en `0.4`: no cambia la gramática ni las formas canónicas, y los archivos
`.oracle` y `.caso` se leen y se escriben igual que antes.

**Corte 0.14.0 (2026-09-09): `VERSION_DISTRIBUCION` sube de `0.13.1` a `0.14.0`.** Sube la
**menor**, y por un motivo que no había aparecido antes: **`tools/aceptacion.py` deja de salir con
código 1**. Salía 1 a propósito desde el 2026-08-26, declarado en DECISION-004, y esa decisión queda
**CUMPLIDA** después de veintitrés días.

El código de salida de la aceptación es superficie: es lo que un CI ajeno lee para decidir si
integrar. Un consumidor que hoy tolera el 1 —con un `|| true`, como lo hacía el CI de este mismo
repositorio— va a seguir pasando, pero uno que lo trate como fallo **cambia de comportamiento**. Que
el cambio sea de rojo a verde no lo vuelve compatible: sigue siendo un contrato de salida que se
mueve, y ésa es la línea de la menor.

`VERSION_ALGEBRA` queda en `0.6` y `VERSION_SINTAXIS` en `0.4`. El impresor de casos elige mejor
entre sus dos formas —tabla y escape— pero **no gana ni pierde ninguna**: un `.caso` válido antes lo
sigue siendo, y todo lo que ya se escribía se escribe idéntico. Lo que cambió es cuál de las dos
formas se elige para un nombre de campo con un espacio adentro, que antes se escribía en una tabla
que el lector no podía volver a partir.

**Corte 0.13.1 (2026-09-09): `VERSION_DISTRIBUCION` sube de `0.13.0` a `0.13.1`.** Sube el
**parche**: nadie cambia de color y no entra ni sale una medida del catálogo. `oracle <directorio>`
deja de despacharse como si fuera una medida —era un mensaje de error que hablaba de otra cosa— y
seis herramientas ya declaradas como custodias entran a la matriz de mutación de CI. Las dos
versiones del lenguaje quedan quietas: `VERSION_ALGEBRA` en `0.6` y `VERSION_SINTAXIS` en `0.4`.

**Una cifra publicada BAJA en este corte, y no es una regresión:** los sitios de mutación de código
pasan de 5935 a 5795. Son exactamente los 140 de `tools/lsp.py`, que salió de
`HERRAMIENTAS_CUSTODIAS`. El denominador cuenta lo que el proyecto declara custodiar, así que sacar
una herramienta de esa lista lo achica — y achicarlo es correcto cuando lo que salió no custodiaba
nada.

**Corte 0.13.0 (2026-09-09): `VERSION_DISTRIBUCION` sube de `0.12.0` a `0.13.0`.** Sube la
**menor** por el mismo motivo que 0.9.0: `meta.ninguna_sombra_supera_su_cota` es de ámbito
`universal` y **se vuelve más estricta** — una cota que no se pudo comprobar cuenta igual que una
incumplida—, y una regla universal más exigente es parte del contrato que cualquier implementación
tiene que sostener. Hoy ningún consumidor cambia de color porque ninguno declara cota; la regla que
heredan sí cambió, y ésa es la línea que 0.9.0 trazó.

`VERSION_ALGEBRA` queda en `0.6`: no entra un nodo, un operador, un agregado ni una escalar.
`evaluada` es un campo de una relación —evidencia— y no del álgebra.

**`VERSION_SINTAXIS` queda en `0.4`, y vale escribir por qué**, porque `nucleo/caso.py::imprimir`
se volvió más estricto y eso podría leerse como que la superficie se movió. No se movió: un archivo
`.caso` válido antes sigue siéndolo, y el impresor produce exactamente el mismo texto para todo lo
que ya imprimía. Lo que se achicó es el **dominio de entrada del impresor**, no el lenguaje. No
entra una cláusula, ni una palabra, ni una forma. La regla que separa los dos casos: la sintaxis
sube cuando cambia el conjunto de archivos que el proyecto puede LEER o ESCRIBIR, no cuando cambia
qué estructuras en memoria acepta una función.

**Un efecto sobre un consumidor que hay que decir sin adornarlo:** el informe de sintaxis de
LyraGASP pasa de `140/140 archivos se imprimen` a `49/140`. Va a leerse como que Oracle empeoró. Lo
que pasó es que el número anterior era falso: sólo llegaba a 140 porque el impresor descartaba en
silencio un campo que 91 de sus casos declaran. Su veredicto ya era ROJO antes y sigue ROJO; lo que
cambió es que ahora dice la verdad sobre por qué.

**Corte 0.12.0 (2026-09-08): `VERSION_SINTAXIS` sube de `0.3` a `0.4` y `VERSION_DISTRIBUCION` de
`0.11.0` a `0.12.0`.** Van tres cosas y cada una mueve una parte distinta.

**La sintaxis** gana una forma que antes era un error: un bloque `agrupar:` con cero agregados.
Sube la **menor de la sintaxis** por el caso 1 de la regla de abajo —una forma que antes no se
aceptaba—; por sí sola habría sido sólo parche de la distribución, porque nadie cambia de color: la
medida del consumidor que lo destapó siempre se cargó y siempre midió lo mismo; lo que no se podía
era volver a escribirla. Su aceptación quedó idéntica, y lo que se movió fue el informe de sintaxis,
de `139/140` a `140/140`.

Es **el mismo defecto que 0.9.2, en otra cláusula**: el impresor emitía algo que el lector no podía
leer. El álgebra acepta y evalúa `["agrupar", claves, []]` —da una fila por combinación distinta de
claves, o sea deduplicar—, el impresor lo escribía, y el lector lo rechazaba con «se esperaba al
menos un agregado». La restricción era además asimétrica: cero **claves** se aceptó siempre.

Y esta vez la sonda que existe para encontrarlo **declaraba el hueco en su propio `alcance`**: «NO
cubre agrupar con 0 agregados (la sintaxis exige al menos un agregado)». El `alcance` cumplió su
trabajo —cuando el consumidor lo pisó, decía por qué la sonda no lo había visto— pero un hueco
declarado y no cerrado es una apuesta a que nadie pase por ahí, y alguien pasó. El generador cubre
ahora las cuatro esquinas, y comprobado contra el lector viejo, las encuentra: tres rojos.
`VERSION_ALGEBRA` queda en `0.6`: no entra un nodo, un operador, un agregado, una escalar ni una
relación de traza, y el evaluador ya aceptaba las cuatro esquinas.

**Lo que sube la menor de la distribución** es que el catálogo base pasa de 58 a **60 medidas
universales** y `oracle.json` gana un campo declarable: `cota` en una entrada de `sombra`. Una
sombra apaga la consecuencia de un rojo; sin cota, apagarla también compraba que la deuda creciera.
Con la cota, `meta.ninguna_sombra_supera_su_cota` hace fallar la corrida si la deuda sube y
`meta.ninguna_cota_mas_alta_que_su_deuda` si la cota queda por encima — las dos direcciones que
antes vigilaba un `grep` literal en el workflow, que salió.

Sube la menor por el **mismo motivo que 0.9.0**: las dos medidas son de ámbito `universal`, así que
**obligan también a los consumidores**, y una medida universal nueva es parte del contrato que
cualquier implementación tiene que sostener. Hoy ninguno se mueve —Jam 28/3, LyraGASP 43/78,
idénticos— porque ninguno declara cota; pero el día que la declaren, se les hace cumplir.

⚠ **El primer intento de este párrafo estaba mal y lo encontró una revisión de falsación.** Las dos
medidas se habían escrito con ámbito `del_origen` —las únicas dos de las siete que miran la sombra—,
así que el catálogo efectivo de un consumidor las descartaba: seguían siendo las mismas 35 medidas
base de antes, y una `cota` declarada por Jam o LyraGASP no la vigilaba nada. Y el argumento que
justificaba la menor era falso por dos lados: el catálogo heredado SÍ era el mismo, y un Oracle
0.11.0 acepta una clave `cota` sin quejarse —el lector usa `.get()` y la ignora—, que es peor que
rechazarla. Corregido el ámbito, el mecanismo existe de verdad y la menor se sostiene por el
precedente que ya estaba escrito, no por uno inventado para el caso.

**Corte 0.11.0 (2026-09-08): `VERSION_DISTRIBUCION` sube de `0.10.0` a `0.11.0`.** El paquete gana
el verbo `oracle censar`, que cuenta el estado de varios proyectos a la vez y lo conserva con su
fecha, en terminal o como página.

Sube la **menor**, y conviene decir por cuál de los dos motivos: **no** porque un consumidor cambie
de color —ninguno lo hace, no entra ninguna medida al catálogo ni se mueve ninguna cota—, sino por
el mismo motivo que 0.7.0, que subió la menor porque «el paquete gana `oracle reportar`». Un verbo
público es superficie nueva que Oracle ofrece y se compromete a mantener, y eso es más que una
herramienta suelta: 0.8.1 ganó `tools/observar.py` entero y fue parche porque no era un verbo.

`VERSION_ALGEBRA` queda en `0.6` y `VERSION_SINTAXIS` en `0.3`: el censo emite una relación de
hechos como cualquier sensor, y no agrega un nodo, un operador, un agregado ni una escalar al
lenguaje.

**Corte 0.10.0 (2026-09-07): `VERSION_DISTRIBUCION` sube de `0.9.2` a `0.10.0`.** El paquete gana
`mutadores/`, que no viajaba: hasta 0.9.2 una instalación mutaba con los **5** mutadores propios en
vez de los **29** declarados, y no lo decía.

Sube la **menor**, y es el caso más claro del criterio hasta ahora: **los consumidores cambian de
color, y esta vez de verdad**. Jam pasa de «0 sobrevivientes» a **9** y LyraGASP de 0 a **2**; los
dos pasan de VERDE a ROJO al actualizar sin haber tocado una línea. En 0.9.0 la menor subió por un
cambio de color que era *posible*; acá está medido en los dos consumidores conocidos.

Que la exigencia ya existiera y el paquete no la aplicara explica por qué corresponde hacerlo, no
por qué podría esconderse en un parche: un parche dice «actualizá sin mirar», y esto pone en rojo
una corrida que ayer daba verde. `VERSION_ALGEBRA` queda en `0.6` y `VERSION_SINTAXIS` en `0.3`: no
entra un nodo, un operador, un agregado, una escalar ni una relación, y el lector no gana palabras.

**Corte 0.9.2 (2026-09-07): `VERSION_SINTAXIS` sube de `0.2` a `0.3` y `VERSION_DISTRIBUCION` de
`0.9.1` a `0.9.2`.** El lector gana una forma que antes era un error: `sin_declarar` como valor de
los argumentos `segun` y `ambito` de una invocación de macro. Sube la **menor de la sintaxis** por
el caso 1 de la regla de abajo —una palabra que antes no se aceptaba— y sólo el **parche de la
distribución**, porque nadie cambia de color: no entra ninguna medida al catálogo, ninguna cota se
mueve, y las dos medidas que persiguen la ausencia la siguen contando exactamente igual. Medido
sobre el consumidor que lo destapó: sus tres sombras quedaron en los mismos 9 / 54 / 41.

El defecto que corrige es del propio lenguaje, y vale escribirlo: **el impresor emitía algo que el
lector no podía leer.** En la forma `medida` la ausencia se expresa OMITIENDO la cláusula, así que
nunca se escribe y siempre dio la vuelta; en una invocación de macro los argumentos son posicionales
y no hay cómo saltearla, así que el impresor escribía `sin_declarar` literal y el lector lo
rechazaba. Ninguna medida lo veía porque el catálogo propio de Oracle no tiene ninguna medida con
esos campos sin declarar. `VERSION_ALGEBRA` queda en `0.6`: no entra un nodo, un operador, un
agregado, una escalar ni una relación de traza, y la forma canónica ya admitía los dos valores.

**Corte 0.9.1 (2026-09-07): `VERSION_DISTRIBUCION` sube de `0.9.0` a `0.9.1`.** `oracle test`
informa los archivos que el impresor no pudo procesar en vez de morir con un traceback en el
primero. Sube el **parche** y no la menor, y la diferencia con el corte anterior es exactamente el
criterio: 0.9.0 subió la menor porque una medida universal nueva podía hacer que un consumidor
pasara de verde a rojo. Acá nadie cambia de color —un proyecto con todo imprimible seguía y sigue
en verde; uno con un archivo ilegible ya salía distinto de cero, sólo que por una excepción sin
atrapar—. Lo que cambia es qué se puede leer cuando ya estaba rojo, y que las etapas siguientes
ahora se ejecutan. `VERSION_ALGEBRA` queda en `0.6` y `VERSION_SINTAXIS` en `0.2`: no entra un
nodo, un operador, un agregado, una escalar ni una relación, el lector no gana palabras, y un
`.oracle` o un `.caso` se leen y se evalúan igual antes y después.

**Corte 0.9.0 (2026-09-07): `VERSION_DISTRIBUCION` sube de `0.8.1` a `0.9.0`.** El catálogo
universal distribuido gana `meta.todo_caso_observado_declara_de_donde_salio`, y la relación `caso`
del marco gana el campo `declara_de_donde_salio` que esa medida mira. Sube la **menor** y no el
parche por la razón que separa las dos: la medida es de ámbito universal, así que **obliga también a
los consumidores**, y uno que actualice sin usar nada nuevo puede pasar de verde a rojo. Los dos
consumidores conocidos salen en cero, pero eso es un hecho de sus corpus, no una garantía del corte.
`VERSION_ALGEBRA` queda en `0.6`: no entra un nodo, un operador, un agregado, una escalar ni una
relación de traza, y un campo nuevo en una relación que el propio marco emite no cambia lo que una
implementación de referencia tiene que implementar. `VERSION_SINTAXIS` queda en `0.2`: el lector no
gana palabras y un `.oracle` o un `.caso` se leen y se evalúan igual antes y después.

**Corte 0.8.1 (2026-09-07): `VERSION_DISTRIBUCION` sube de `0.8.0` a `0.8.1`.** El paquete gana
`tools/observar.py`, el recorrido que ejecuta el sensor de un consumidor y conserva su corrida como
un caso con `procedencia: observada`. `VERSION_ALGEBRA` queda en `0.6` y `VERSION_SINTAXIS` en
`0.2`: la herramienta **usa** el lenguaje existente —`Referente`, `hechos_de_frescura` y dos medidas
meta que ya se distribuían— y no agrega un nodo, un operador, un agregado, una escalar, una relación
ni una palabra del lector, ni cambia el significado de ninguno. Un `.oracle` o un `.caso` se leen y
se evalúan exactamente igual antes y después del corte.

**Corte 0.8.0 (2026-09-06): `VERSION_DISTRIBUCION` sube de `0.7.0` a `0.8.0`.** El generador
comprueba la polaridad y respeta cotas de conteos simples, se incorpora su sonda de custodia y la
medida de antigüedad de sombras pasa de contar incumplimientos a publicar su edad máxima en días.
`VERSION_ALGEBRA` queda en `0.6`: cambia la fórmula de un archivo del catálogo usando `peor` y
`max` existentes, no la semántica del evaluador, los nodos admitidos ni la forma canónica. El mismo
archivo de medida se evalúa igual antes y después; es el catálogo distribuido el que contiene una
fórmula distinta. `VERSION_SINTAXIS` queda en `0.2`: no cambia el lector ni las formas aceptadas
de `.oracle` o `.caso`. El cambio observable de valor de la medida se documenta en las notas del
corte: conservar polaridad y testigos no significa conservar el número publicado.

**Corte 0.7.0 (2026-09-06): `VERSION_DISTRIBUCION` sube de `0.6.0` a `0.7.0`.** El paquete gana
`oracle reportar` y el canal documentado de reporte. `VERSION_ALGEBRA` queda en `0.6`: no se agrega
ningún nodo, operador, agregado, escalar ni relación de traza, ni cambia el significado de los
existentes. `VERSION_SINTAXIS` queda en `0.2`: el lector no gana palabras ni cláusulas y sigue
aceptando las mismas formas de `.oracle` y `.caso` con el mismo significado.

**`MENOR` sube** cuando el álgebra **gana** algo sin cambiar el significado de lo que ya valía: un
nodo opcional nuevo (`requiere`), un operador nuevo (`agrupar`, `unir`), un agregado nuevo, una
escalar declarada nueva, una relación de traza nueva. Quien no usa lo nuevo queda exactamente igual;
quien *implementa el álgebra completo* —una referencia independiente— quedó incompleto y tiene que
volver a verificarse. De `0.2` a `0.3` subió la menor (entraron `agrupar`, `requiere` y `clave`);
de `0.3` a `0.4` volvió a subir porque el umbral ganó `segun`.
De `0.4` a `0.5` subió porque `@escalar` ganó `unidades_argumentos`.
De `0.5` a `0.6` subió porque la forma canónica de una medida ganó el nodo opcional `ambito`.
De `0.6` a `0.7` subió porque una entrada de `requiere` puede llevar condición y la declaración de
una relación ganó `variantes` (§1.3, §2).

**`MAYOR` sube** cuando cambia el **significado o el contrato** de algo que ya existía: la semántica
de un operador (qué hace `min`/`max` con booleanos), la forma canónica de una medida, una validación
que hacía cargar lo que ahora se rechaza, o quitar/renombrar un operador. Eso rompe a todo
consumidor, use o no la parte cambiada. De `0.3` a `1.0`, y la menor vuelve a `0`.

**Cómo se comprueba.** El núcleo publica lo que implementa. Un proyecto puede declarar en
`oracle.json` la versión que necesita (`"algebra": "0.6"`); si no es compatible, la carga falla
cerrado con un mensaje que dice cuál hay y cuál se pidió, y quien no la declara sigue funcionando.
La compatibilidad es la del párrafo anterior: misma `MAYOR` y `MENOR` al menos tan nueva como la
pedida. Una implementación de referencia, en cambio, declara contra qué versión se escribió y el
arnés del diferencial la compara con la del núcleo antes de emitir un fixture: la referencia se fija
a una versión **exacta**, porque un agregado puede no romper a un consumidor y sí a un evaluador que
no conoce el nodo nuevo.

### La superficie tiene su propia versión

La superficie infija declara la suya, `VERSION_SINTAXIS`, con la misma forma `MAYOR.MENOR` y la
misma maquinaria (`parsear`, `compatible`, `VersionInvalida`). La regla aplica a las medidas
(`.oracle`), a los casos del corpus (`.caso`) y a las relaciones (`.relacion`): la superficie es cómo se escribe y el JSON es cómo
se guarda, cargándose ambos por igual. La distinción que importa es entre el **lector** y el
**impresor**, y no envejecen igual: un archivo `.oracle` o `.caso` viejo se **lee**; el
impresor no lo toca. Por eso **una sola versión alcanza**, y alcanza porque la comparación es
asimétrica —el archivo declara contra qué se escribió y el núcleo declara qué implementa—:

- un archivo viejo leído por un núcleo nuevo es compatible si la mayor coincide y la menor del
  núcleo es al menos la declarada;
- un archivo nuevo —que usa una palabra nueva— leído por un núcleo viejo falla cerrado, porque el
  núcleo declara una menor anterior a la que el archivo pide.

No hacen falta dos números: la ida y vuelta lector↔impresor es un invariante interno que
`sintaxis.py --verificar` comprueba, y el impresor sólo cambia en dos casos —o el lector aprende una
forma nueva (MENOR), o deja de aceptar una que ya se publicaba (MAYOR)—.

**`MENOR` sube** cuando el lector **gana** una forma sin cambiar el significado de lo que ya valía:
una palabra nueva que antes era un error de sintaxis, un separador nuevo. Un archivo escrito contra
la menor anterior se sigue leyendo idéntico. De `0.1` a `0.2` subió porque la superficie infija
ganó la cláusula `ambito`. De `0.4` a `0.5` subió porque el lector ganó `requiere <relación> <alias>
donde <condición>` y varias líneas `requiere` seguidas.

**`MAYOR` sube** cuando el lector **cambia** lo que ya aceptaba: una forma que hoy se lee pasa a
significar otra cosa, o pasa a ser un error de lectura. Eso rompe a todo archivo que la use.

Casos concretos:

1. **Agregar una palabra nueva que antes era un error de sintaxis** → **MENOR**. Quien no la usa no
   se entera; un archivo viejo sigue cargando.
2. **Cambiar cómo se imprime algo sin cambiar qué se acepta al leer** → **no sube nada**. El archivo
   viejo se lee igual porque el lector no cambió, y el que el impresor reescribe lo sigue leyendo un
   lector viejo porque la forma impresa ya era aceptada. (Si el cambio de impresión mete una forma
   que el lector tiene que aprender, es el caso 1, MENOR; si hace que una forma ya publicada deje de
   leerse, es MAYOR.)
3. **Que una forma que hoy se acepta pase a ser un error** → **MAYOR**. Un archivo que la use deja
   de cargar.

Un `.oracle` puede declarar contra qué versión se escribió, con una primera línea
`sintaxis MAYOR.MENOR`. Es opcional —los archivos de hoy no la declaran y siguen cargando— y es
parte de la superficie, no un comentario pegado arriba. Declarar una versión incompatible falla
cerrado al cargar, con un mensaje que dice las dos versiones. `oracle.json` puede pedir una versión
de sintaxis (`"sintaxis": "0.2"`) con la misma regla que pide la del álgebra.

---

## 1. Hechos y relaciones (L0)

Un **hecho** es un registro de campos escalares. Una **relación** es una bolsa nombrada de hechos del
mismo tipo. La evidencia es un mapa de relaciones:

```json
{
  "pieza":   [{"id": "Muro_A", "x": 100, "y": 100, "ex": 200, "ey": 25}],
  "mutante": [{"id": "firma_por_id", "apunta_a": "funcion._orden_visual", "tipo": "medida",
               "detecciones_conductuales": 0, "rechazos_del_algebra": 0}]
}
```

Nada más. Sin objetos, sin punteros, sin nulos implícitos ni explícitos: un campo `null` en cualquier
hecho de la evidencia recibida se rechaza al cargar, aun si la medida no usa esa relación. El **sensor** que produce la evidencia es
específico de cada dominio y vive con el productor, no acá.

La multiplicidad cuenta y el orden de almacenamiento no. Dos apariciones idénticas son dos hechos:
`contar` devuelve 2, `suma` usa ambas y un producto conserva ambas. Oracle no deduplica porque no
puede inventar una identidad genérica.

Un dominio que SÍ conoce su identidad puede **declarar una clave de unicidad** para una relación,
poniendo a la cabeza de su lista de hechos un nodo `["clave", [<campo>, …]]`:

```json
{
  "pieza": [["clave", ["id"]],
             {"id": "Muro_A", "x": 100}, {"id": "Muro_B", "x": 300}]
}
```

La clave es **opcional** y se valida en **todas las relaciones de la evidencia recibida antes de medir**, incluso las que la medida no consulta, fail-closed: si dos hechos repiten la clave
declarada, la evaluación levanta un error que nombra la clave responsable y la fila que la viola — no
un veredicto verde, no un error genérico. Un campo de la clave ausente en un hecho también es error:
una identidad a medias no se puede comprobar, y un nulo implícito la dejaría sin comprobar en
silencio. Sin el nodo, la relación es exactamente la bolsa de siempre, y la multiplicidad intencional
sigue siendo expresable sin declarar nada.
La fila informada se numera desde cero entre los hechos, sin contar el nodo `clave`.

### 1.1 Las relaciones que el lenguaje emite

Casi toda la evidencia la produce un sensor del dominio. Pero hay relaciones que **produce el
propio marco**, sobre sí mismo: son las que hacen posible L2 —medidas sobre medidas— y las que
permiten que un veredicto sobre el catálogo sea un dato y no un `if` escondido en `tools/`.

Se distinguen porque `catalogos/meta/` las consume y ningún proyecto las declara. La lista es
derivable —`relaciones_del_lenguaje_declaradas()` la calcula leyendo los emisores— y hay una
medida, `meta.toda_relacion_del_lenguaje_esta_en_la_referencia`, que exige que cada una aparezca
acá. Esta sección no puede envejecer en silencio.

| relación | qué describe | quién la emite |
|---|---|---|
| `medida` | cada medida del catálogo, reificada: su comparador, umbral, `segun`, `alcance` | `nucleo/medida.py` |
| `termino` · `fuente` · `paso_de_medida` · `nodo` | las piezas de una medida vistas como árbol: sus términos, de dónde saca filas, cada paso de la tubería y cada nodo lógico | `nucleo/medida.py` |
| `dependencia_de_medida` | cada relación de la que una medida depende y por qué vía (`fuente` o `requiere`); une las dos para que una política sobre dependencias se escriba una vez | `nucleo/medida.py` |
| `requiere` | qué relaciones declara necesitar una medida para concluir, y si la entrada lleva condición (`con_condicion`) | `nucleo/medida.py` |
| `caso` | cada caso del corpus: su polaridad, su `procedencia`, si su medida existe, y —desde `DECISION-009`— si es propio o de una biblioteca | `nucleo/marco.py` |
| `medida_en_uso` | cuántos casos evalúan cada medida y cuántos mutantes le sobreviven | `nucleo/marco.py` |
| `sombra` | qué medidas heredadas se miden pero todavía no obligan, desde cuándo, por qué y hace cuántos días | `nucleo/marco.py` |
| `relacion_documentada` | si cada relación del lenguaje está nombrada en esta especificación | `nucleo/marco.py` |
| `verbo_del_cli` | cada verbo que el comando acepta y si la ayuda lo nombra | `nucleo/marco.py` |
| `opcion_del_vocabulario` | cada opción de un vocabulario cerrado, con cuántas palabras la explican y si el manual la muestra | `nucleo/marco.py` |
| `mutador_excluido` | cada exclusión de mutador declarada, con su premisa, si algún autor ofrece el mutador y si el registro del arnés lo tiene | `nucleo/marco.py` |
| `relacion_declarada` · `campo_declarado` · `ambito_de_relacion` | las relaciones que un proyecto declara, cuántas variantes tienen, sus campos con unidad y la variante a la que pertenece cada uno, y dónde obliga cada relación | `nucleo/relacion.py` |
| `cantidad_comparada` | cada comparación de una medida y si su unidad se puede derivar (L−1) | `nucleo/unidad.py` |
| `campo_leido` | cada campo que lee una medida: de qué relación, si esa relación es declarada, del lenguaje o sin declarar, y si el campo existe en ella | el emisor que declara `campo_leido` |
| `referente_declarado` · `referente_comparado` | la identidad y la frescura de aquello que se midió (L−2) | `nucleo/referente.py` |
| `equivalencia` | dos formas que deberían dar lo mismo, para las propiedades metamórficas | `tools/metamorficas.py` |
| `paso` · `producto` · `ancestro` | lo que una evaluación trazada produjo: cada paso, el tamaño del producto de un `unir`, y la ascendencia de un nodo | `nucleo/algebra.py` |
| `campo_diagnostico` | cada valor de texto del diagnóstico local y si contiene algo del dominio | `nucleo/diagnostico.py` |

**Ninguna de estas relaciones se declara en `relaciones/`.** Un proyecto que definiera una con el
mismo nombre estaría pisando una del lenguaje, y por eso los nombres se reservan.

Sus **campos** los declara cada emisor al lado de la relación, en un mapa literal
`CAMPOS_DE_RELACIONES` que se lee sin ejecutar el módulo (desde la distribución 0.22.0). Un test compara
cada declaración con las filas que el emisor produce, así que no puede envejecer en silencio. Con eso,
los campos de toda relación que Oracle emite se conocen igual que los de una relación declarada (§1.3).

### 1.2 Los vocabularios cerrados, y el manual que sale de ellos

Cinco campos del lenguaje admiten un conjunto cerrado de valores: los seis operadores de una
tubería, el `segun` de un umbral, y la `etiqueta`, la `procedencia` y el `como_se_detecto` de un
caso. Es la parte que más se equivoca quien recién llega, porque los nombres se parecen entre sí.

Cada opción **declara su significado junto a su nombre** —`nucleo/vocabulario.py` y
`nucleo/caso.py`—, y de esa única fuente salen las dos cosas que importan:

- el error que ve quien escribe un valor inválido, en el momento exacto en que se equivoca, con
  las opciones y qué es cada una;
- `oracle manual`, que no es un documento aparte sino una **vista** de esas declaraciones. La
  misma salida en `--html` es la página del sitio, y en `--man` son páginas de manual: tres vistas
  de una sola fuente, ninguna escrita a mano.

Un manual generado no puede quedar viejo, salvo por una grieta: que aparezca un vocabulario y nadie
lo anote en el registro que dice qué mostrar. Eso lo mide
`meta.todo_vocabulario_cerrado_esta_en_el_manual`; que ninguna opción quede sin explicar lo mide
`meta.toda_opcion_del_vocabulario_declara_su_sentido`.

### 1.3 Relaciones declaradas y sus variantes

Una relación que produce un sensor **se puede declarar** en `relaciones/`: su nombre, sus campos con
tipo y unidad, y qué no lee el sensor. La declaración no filtra evidencia; es de lo que salen
`relacion_declarada` y `campo_declarado`, la derivación de unidades y los puntos ciegos de una medida.

La forma de autoría es un archivo `.relacion`:

```relacion
relacion corrida:
    id: texto
    pasos: entero pasos
    alcance "no ve el estado interno del simulador"
```

Cada campo ocupa una línea `nombre: tipo unidad` para `entero` y `flotante`, que exigen una
unidad sin corchetes, incluso `sin_unidad` cuando el número no expresa una magnitud. Para `texto`
y `booleano` se escribe sólo `nombre: tipo`: se cargan con `sin_unidad` y cualquier unidad escrita
es un error. Los corchetes en una declaración de campo son un error de sintaxis.
`alcance "…"` es obligatorio al final. La forma canónica equivalente, que sigue siendo válida
como entrada JSON, es:

```json
["relacion", "corrida",
  ["campos", ["campo", "id", "texto", "sin_unidad"], ["campo", "pasos", "entero", "pasos"]],
  ["alcance", "no ve el estado interno del simulador"]]
```

En el árbol canónico, un campo es `["campo", <nombre>, <tipo>, <unidad>]`, con `tipo` en `texto`,
`entero`, `flotante` o `booleano`.

**Variantes** (álgebra `0.7`). Una misma relación puede traer filas de clases distintas con campos
distintos: `mutante` la producen la mutación de medidas y la de código. Un nodo opcional
`variantes`, entre `campos` y `alcance`, declara qué campos trae cada clase según el valor de un campo
**discriminante**:

```relacion
relacion mutante:
    id: texto
    tipo: texto
    variantes por tipo:
        medida:
            detecciones_conductuales: entero sin_unidad
        codigo:
            murio: booleano
    alcance "observa resultados de mutación; no ve la traza completa"
```

Los valores simples de variante se escriben como nombres; valores con otros caracteres se
escriben como textos entre comillas. El árbol canónico correspondiente tiene un nodo opcional
`variantes` entre `campos` y `alcance`:

```json
["relacion", "mutante",
  ["campos", ["campo", "id", "texto", "sin_unidad"], ["campo", "apunta_a", "texto", "sin_unidad"],
             ["campo", "cambio", "texto", "sin_unidad"], ["campo", "tipo", "texto", "sin_unidad"]],
  ["variantes", "tipo",
    ["variante", "medida", ["campo", "detecciones_conductuales", "entero", "sin_unidad"], …],
    ["variante", "codigo", ["campo", "estado", "texto", "sin_unidad"], …]],
  ["alcance", "…"]]
```

- El discriminante es un campo común de tipo `texto`, y hay al menos una variante.
- Los valores de variante son textos no vacíos y no se repiten.
- Cada variante declara al menos un campo, y un campo de variante no repite uno común ni se repite
  dentro de su variante.
- El mismo nombre en dos variantes exige el mismo tipo y la misma unidad: un campo significa lo mismo
  donde aparezca.
- Una relación sin `variantes` conserva su forma de cuatro elementos.

`campo_declarado` trae una fila por campo y por variante, con `variante` vacía para los comunes;
`relacion_declarada` dice cuántas variantes tiene la relación.

**Toda medida lee campos que existen.** `campo_leido` tiene una fila por cada `["campo", alias, nombre]`
de una medida, con la relación del alias —resuelta por las fuentes y por las entradas con condición de
`requiere`—, su `origen` (`declarada`, `lenguaje` o `sin_declarar`) y si el campo `existe` en ella.
`meta.toda_medida_lee_campos_que_existen` no admite ninguna lectura de un campo inexistente en una
relación declarada o del lenguaje. Una relación sin declarar de un consumidor no se juzga: sin
declaración, Oracle no sabe qué campos trae. `["hecho", alias]` y `["col", nombre]` no son lecturas de
campo.

Las variantes **no relajan** la regla del campo ausente: una medida sobre una variante filtra primero
por el discriminante —un `donde` propio, antes del de las violaciones— y pide filas de su variante en
`requiere` (§2). Si comparara un campo de otra variante, levantaría error, como con cualquier campo que
la fila no trae.

## 2. Una medida es un dato

```json
["medida", "colocacion.interpenetracion",
  ["desde",
    ["unir", ["de", "pieza", "a"], ["de", "pieza", "b"]],
    ["donde", [">", ["penetracion", ["hecho", "a"], ["hecho", "b"]], 0]]],
  ["resumen", "max", ["penetracion", ["hecho", "a"], ["hecho", "b"]]],
  ["umbral", "<=", 0, "penetracion() ya descuenta la tolerancia de contacto"],
  ["alcance", "solape de AABB. NO ve la malla real, ni oclusión, ni si quedó flotando"]]
```

**La forma canónica admite `requiere` y `ambito` opcionales, en ese orden antes de `alcance`:**

```json
["medida", "<id>", <tubería>, <resumen>, <umbral>,
  ["requiere", "<relación>", …],
  ["ambito", "del_origen"],
  ["alcance", "<qué NO ve>"]]
```

Por ejemplo, con ambos nodos: `["medida", "ejemplo.con_ambito", ["desde", ["de", "pieza", "p"]], ["resumen", "contar", 1], ["umbral", "==", 1, "una pieza"], ["requiere", "pieza"], ["ambito", "del_origen"], ["alcance", "sólo cuenta piezas declaradas"]]`. Si falta `requiere`, `ambito` sigue inmediatamente al `umbral`.

Los valores admitidos para `ambito` son `"universal"`, `"del_origen"` y `"sin_declarar"`.
El último también es el valor asumido cuando se omite el nodo.
Si `umbral` incluye `segun`, sus valores admitidos son `"medicion"`, `"contrato"`,
`"convencion"`, `"tanteo"` y `"sin_declarar"`.

Es el espejo de `alcance`: uno declara qué NO ve la medida, el otro **qué NECESITA ver para
concluir**. Si alguna de las relaciones listadas viene vacía (también cuando sólo trae la cabecera `clave` y ningún hecho), la evaluación no mide: devuelve
`SIN EVIDENCIA`, que no es verde y tampoco es un rojo del mundo. Existe porque el álgebra no puede
expresarlo —un agregado sobre cero filas da `0` y un umbral `<= 0` lo lee como éxito— y la ausencia
total salía verde justo cuando el mundo estaba peor; el caso completo está en §8.
En `requiere`, una relación omitida del mapa de evidencia equivale a una relación presente con `[]`.

En la terminología de Shi, Zhang y Cui, *A Programming Paradigm for Spatiotemporal
Composability*, §3.2, `requiere` es un **coefecto**: una especificación de dependencias que se
contrasta contra el contexto disponible antes de ejecutar. Oracle toma sólo esa mitad declarativa.
No toma la reactividad del paper —clasificar cada cambio del contexto para activar y desactivar
componentes— porque la evidencia no cambia durante una evaluación; si falta una relación, se corta
fail-closed con `SIN EVIDENCIA`.

Una medida sin el nodo se comporta exactamente como antes y su forma canónica **no cambia**: son seis
elementos, no siete. Un evaluador tiene que aceptar las dos longitudes.

**Una entrada de `requiere` puede llevar condición** (álgebra `0.7`). Cada elemento después de
`"requiere"` es un nombre de relación, como hasta ahora, o una entrada
`["filas", <relación>, <alias>, <condición>]`:

```json
["requiere", "pieza", ["filas", "mutante", "m", ["==", ["campo", "m", "tipo"], "codigo"]]]
```

La entrada con condición da `SIN EVIDENCIA` si la relación viene vacía **o** si ninguna de sus filas
cumple la condición. La condición es una expresión booleana con las reglas de un `donde`: sólo usa
su alias, y comparar un campo ausente **levanta error** —no es `False`, igual que en un `donde`—.
Una relación no puede aparecer dos veces en `requiere`, con condición o sin ella.
Todas las condiciones se evalúan **en todas las filas y en todas las entradas antes de decidir**:
un campo ausente levanta aunque otra fila ya cumpla, y aunque otra relación requerida venga vacía.
Sin eso el veredicto dependería del orden de almacenamiento de la bolsa (`DECISION-001`) o del orden
en que se escribió `requiere`. Si nada levanta, la primera entrada sin evidencia, en orden, es la que
nombra el `SIN EVIDENCIA`. (Lo dejó abierto la primera redacción de esta sección; lo decidió la
implementación de referencia independiente al re-derivarse contra `0.7`.)

Existe por las relaciones con variantes (§1.3). La condición **no es el filtro de la medida**, y
confundirlos rompe el lenguaje: en toda medida `ninguno` el `donde` selecciona las violaciones, así
que cero filas filtradas es su verde, no una falta de evidencia. Medido el 2026-09-15: las veinte
medidas con `requiere` que existían filtraban con `donde`, y un `requiere` sobre las filas filtradas
las habría pasado a todas de verde a `SIN EVIDENCIA`. Lo que una medida sobre una variante necesita
es otra cosa: que haya filas **de su variante**. Sin eso, una ronda de mutación de medidas le presta
evidencia a la medida de mutación de código, que filtra por su tipo, cuenta cero y sale verde sobre
una ronda que nunca ocurrió ([`502`](corpus/proceso/), y el espejo en `503`).

En la superficie, cada entrada con condición va en su propia línea, después de la de nombres si la
hay; las líneas `requiere` seguidas forman un solo nodo, en orden:

```
requiere pieza
requiere mutante m donde m.tipo == "codigo"
```

Una medida real, del catálogo que ya corre — sin `unir`, que todavía no tiene usuario:

```json
["medida", "proceso.test_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"],
    ["donde", ["==", ["campo", "m", "tipo"], "medida"]],
    ["donde", ["y", ["==", ["campo", "m", "detecciones_conductuales"], 0],
                    ["==", ["campo", "m", "rechazos_del_algebra"], 0]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina…"],
  ["requiere", ["filas", "mutante", "m", ["==", ["campo", "m", "tipo"], "medida"]]],
  ["alcance", "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los que nadie escribió…"]]
```

Listas anidadas, serializable a JSON. De eso salen cuatro cosas que si no serían mecanismos aparte:

1. el **corpus** puede guardar medidas, no sólo evidencia;
2. el **inventario** de umbrales y de puntos ciegos es una consulta sobre las medidas;
3. la **mutación** es una transformación de datos, no un `sed` sobre archivos;
4. las **macros** (una medida que escribe medidas) no necesitan permiso del diseñador del lenguaje.

La mutación de medidas cubre un denominador explícito: umbral y filtros completos; cada fuente que
puede sustituirse por otra relación nombrada en la misma medida; comparadores, lógicos y booleanos de
expresiones; un agregado alternativo por sitio; y referencias de campo sustituibles dentro del mismo
alias o espacio derivado. Los ids incluyen la ruta JSON del sitio. No muta nombres de UDF, aridades,
defensas ni alcances: las dos primeras fallan al cargar, y las dos últimas fallan al cargar **y**
además quedan reificadas como medidas de L2 (§4).

**Los testigos no se declaran.** Son las filas finales de la tubería `desde` completa, después de `donde`, `sin` y `agrupar` si los hay; son las filas que aportan al resumen. Declararlos
aparte obliga a recorrer los datos dos veces y a mantener dos definiciones de lo mismo sincronizadas
a mano — el error concreto que motivó esta especificación (ver
[`004-testigos-duplicados`](corpus/proceso/)).

## 3. Los operadores

Seis. Cinco toman relaciones y devuelven una relación: **eso es la clausura**, y es lo que permite
encadenarlos en cualquier orden sin un solo caso especial. `resumen` es el que la rompe a propósito,
porque colapsa a un escalar: por eso va último y una sola vez, y por eso **la clausura es sobre
filas, no sobre medidas**.

Conviene decirlo fuerte, porque la versión corta de esta frase engañaba: una medida termina en un
escalar y un umbral, y ahí se acaba. **Ninguna medida puede consumir los testigos ni el veredicto de
otra**, y eso no es una limitación pendiente sino una decisión tomada y registrada en
[`DECISION-002`](docs/decisiones/DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md). Las preguntas que esa decisión deja
afuera —«¿qué medidas comparten testigos?»— se responden en L2, midiendo el catálogo como relación.

| Operador | Forma | Qué hace |
|---|---|---|
| `de` | `["de", relación, alias]` | fuente |
| `donde` | `["donde", pred]` | filtra filas según un predicado booleano |
| `unir` | `["unir", fuente_izq, fuente_der]` | producto cartesiano de fuentes `de` o `unir` anidadas |
| `sin` | `["sin", ["de", relación, alias], cond]` | anti-junta: deja las filas que **ninguna** fila de la relación cumple |
| `agrupar` | `["agrupar", [[nombre, expr], …], [[nombre, agg, expr], …]]` | agrupa y agrega |
| `resumen` | `["resumen", agg, expr]` | colapsa a un escalar — **la medición** |

Agregados: `max`, `min`, `suma`, `promedio`, `contar`. `contar` **no evalúa la expresión**: cuenta
filas. Los agregados sobre cero filas dan `0`. `suma` y `promedio` aceptan números finitos y
booleanos como indicadores 0/1; `min` y `max` exigen escalares homogéneos y comparables, incluidos booleanos homogéneos con `false < true`. Un valor no
finito o una mezcla incompatible es error de álgebra, no un veredicto.

Los predicados de `donde`, `sin` y `requiere` condicional deben evaluar a `bool`.
También cada operando de `y`, `o` y `no` debe ser `bool`; un número, texto o `null`
produce `ErrorDeAlgebra`, nunca una conversión por veracidad. `y` y `o` evalúan todos
sus operandos. En una igualdad de `unir … donde`, el camino indexado conserva los mismos
errores de tipos incompatibles que el producto con `donde` ordinario.

`desde` no es un operador: es la tubería que los encadena (`["desde", fuente, paso, paso, …]`).
Su fuente inicial sólo puede ser `de` o `unir`; cada lado de `unir` también debe ser una fuente
`de` o `unir`, nunca una sub-tubería `desde`. `resumen` sólo ocupa el nodo de la medida posterior
a la tubería; no es un paso de `desde`.

En `agrupar`, tanto las claves como los agregados son listas de entradas. Las claves pueden ser
`[]`: si entran filas, todas forman un único grupo. Si no entra ninguna fila, salen cero grupos,
incluso con cero claves; no se crea una fila sintética con agregados en `0`.

### Lenguaje activo: seis operadores

La regla *no se agrega un operador hasta que una segunda medida lo necesite* aplica también a
**publicarlos**: un operador sin usuario es un operador sin verificar. Corren `de`, `donde`,
`resumen`, `unir`, `sin` y `agrupar`.

| Operador | Estado |
|---|---|
| `unir` | ✅ entró con el catálogo de geometría: «pares de piezas que se clavan» es un producto |
| `agrupar` | ✅ entró con la AUSENCIA — ver §8 |
| `sin` | ✅ entró en `0.8`: cinco medidas contaban la ausencia con un sensor en Python — ver §8 |

`con` y la unión izquierda no son promesas pendientes ni sintaxis aceptada: no tienen dos usuarios
reales y por eso una declaración que los use falla al cargar. Si aparecen esos usuarios, vuelven con
sus casos, semántica y mutantes; no como ramas dormidas.

`sin` sólo puede aparecer como paso posterior a la fuente inicial de `desde`, nunca como fuente
inicial ni como lado de `unir`. Para cada fila que llega, evalúa `cond` contra **cada**
fila de la relación —la condición ve los alias y las columnas de la fila que llega, más el alias
nuevo— y la deja pasar sólo si **ninguna** la cumple. La salida conserva la fila tal como llegó: el
alias nuevo existe sólo dentro de la condición y un paso posterior no puede leerlo. Los bordes:

- **Relación vacía** (`[]`): no hay con qué corresponder, así que pasan todas las filas.
- **Relación ausente** de la evidencia: el mismo error que `de`, aunque no llegue ninguna fila. Una
  anti-junta sobre algo que no se trajo no puede dar verde por omisión.
- **Sin cortocircuito**: `cond` se evalúa contra **todas** las filas de la relación antes de decidir.
  Si una evaluación es error, la medida es error, aunque otra fila ya hubiera correspondido: el orden
  de la bolsa no puede cambiar el veredicto.
- **Alias repetido**: si el alias nuevo ya lo introdujo la tubería —en su fuente o en un `unir`—,
  es error de álgebra. Es un error **de la medida**, no de los datos: se rechaza aunque no llegue
  ninguna fila. Después de `agrupar` la fila no tiene alias, así que no hay con qué chocar: una
  columna se lee con `col` y un alias con `campo`, y el mismo nombre no es ambiguo.
- **La derecha es una relación nombrada**, `["de", relación, alias]`; un `unir` en ese lugar es
  error de álgebra.
- **Presupuesto**: `|filas que llegan| × |relación|` evaluaciones, contra el mismo límite de producto
  cartesiano que `unir` (§9).
- **Después de `agrupar`**: vale igual; la condición lee las columnas con `["col", nombre]`.

Un grupo **no es un hecho**: es un resumen. Las filas que salen de `agrupar` no llevan alias —los
hechos se consumieron— sino columnas derivadas, que se leen con `["col", nombre]`. Ese accesor existía
desde el principio y recién acá encontró su usuario.

### Acceso a los datos

Explícito siempre: `["campo", alias, nombre]` para un campo, `["hecho", alias]` para el hecho entero,
`["col", nombre]` para una columna derivada. Todo lo demás en posición de expresión es un **literal**.

Comparar contra un campo ausente **levanta un error**, no devuelve `False`: en una medida eso es casi
siempre un nombre mal escrito, y un `False` silencioso lo convertiría en un verde.

Los operadores lógicos `y` y `o` aceptan dos o más operandos: `["y", a, b, c]` es una forma válida.
Evalúan todos sus operandos, sin cortocircuito, incluso si uno ya determina el resultado.
La negación lógica `no` acepta exactamente un operando: `["no", expr]`.

Al evaluar un conjunto de medidas, ese error **no corta la corrida ni se pierde**: el núcleo deja la
medida entre las que **no pudieron juzgar**, con su motivo, aparte de los rojos y de los `SIN
EVIDENCIA`. Un informe con alguna medida que no juzgó no es verde. Cada herramienta decide qué hace con
eso según su contrato —la aceptación y la mutación de medidas lo cuentan como falla, `oracle juzgar`
sale 2—, pero todas lo leen del mismo lugar (desde la distribución 0.22.0). La sombra no lo tapa: apaga
la consecuencia de un rojo, y una medida que no pudo juzgar no dio un rojo del mundo, tiene un defecto.

### Funciones escalares

Los predicados de dominio (`penetracion`, `distancia`, `desvio_de_grilla`) entran como **funciones
escalares declaradas**, con nombre, aridad, unidad de retorno y unidad de cada argumento. Es el
mecanismo de UDF de SQL, y es el escape
hatch honesto: evita inventar un lenguaje que sepa geometría.

Se **declaran**, no se importan sueltas: así aparecen en el inventario y se pueden contar y discutir
igual que los umbrales.

El contrato declarativo incluye un nombre con gramática cerrada, aridad mínima y máxima (o
variádica), unidad de retorno, `unidades_argumentos` y procedencia. `sin_unidad` se escribe de forma
explícita para un hecho entero o un texto; omitir la tupla conserva compatibilidad de carga pero deja
la cantidad como `sin_declarar` en L−1. Una UDF externa sigue siendo **código Python con los mismos permisos
que Oracle**: sólo se activa con `--confiar-escalares`, durante una operación, y el registro anterior
se restaura al terminar o fallar. `--help`, `--relaciones`, `--nueva` y `--escalares` sin esa bandera
son modos de inspección: pueden mostrar archivos o el inventario base, pero no importan código del
proyecto.

## 4. Los tres niveles con un solo mecanismo

Como una medida es un hecho, `medida` es una relación más y las medidas sobre medidas son medidas
normales:

```json
["medida", "meta.todo_tanteo_explica_por_que",
  ["desde", ["de", "medida", "m"],
    ["donde", ["y", ["==", ["campo", "m", "segun"], "tanteo"], ["==", ["campo", "m", "porque"], ""]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "si un número es tanteo, decir por qué todavía importa", "contrato"],
  ["alcance", "ve sólo tanteos sin explicación. NO juzga si la explicación alcanza"]]
```

Ese `alcance` es el ejemplo de por qué el campo es obligatorio: la medida es útil y es
superficialísima, y decirlo evita que se lea como más de lo que es.

Tres reglas que antes eran `raise` de `nucleo/medida.py` quedaron reificadas así, como medidas del
catálogo base: `meta.todo_umbral_declara_de_donde_sale`, `meta.ninguna_medida_sin_alcance` y
`meta.ningun_umbral_flotante_de_igualdad`. Las dos primeras conservan el `raise` de carga además de
la medida — son contratos fail-closed, y la medida las vuelve inspeccionables y discutibles —; la
tercera sólo vive en la medida y en `algebra.comparar`, porque un umbral `== 3.14` está bien formado
y su rechazo es un juicio, no un contrato. La distinción completa está en `INFORME.md`.

## 5. Modo simulación — ✅ IMPLEMENTADO

La segunda fuente de evidencia. En vez de consultar hechos estáticos, se corre el sistema y se
observan los hechos que emergen:

```
evento(corrida, t, actor, que, …)
corrida(id, escenario, semilla, pasos, razon, determinista)
```

**No es otro sistema.** Una traza es una relación, y las mismas operaciones la miden sin cambio
alguno. La simulación es un *productor de hechos*, no un segundo oráculo.

Dos reglas del contrato, y las dos salieron de equivocarse primero:

- **ningún campo de veredicto.** La primera versión tenía `gano: bool`, que es un concepto de un
  dominio metido adentro del núcleo. Una corrida termina por una `razon`; si esa razón es aceptable lo
  decide una medida. Lo mismo con «quedó gente en la cola»: es un hecho del resumen, no una razón.
- **el determinismo se comprueba.** Cada corrida se ejecuta dos veces con la misma semilla y
  `determinista` es un hecho. Una corrida irreproducible no puede ser material de corpus.

Importa porque es la mitad más resistente a Goodhart: un umbral se afloja cambiando un número; lo que
emerge de correr el sistema, no. Y produce el desacuerdo que la primera mitad no puede ver: **«existe»
y «se llega» no son lo mismo.**

## 6. Fixtures diferenciales

El esquema vigente es `oracle.diferencial/v1`. Todo fixture declara su versión y una sección
`frescura` con cuatro huellas SHA-256: emisor, fuentes de referencia, catálogo canónico de las
medidas usadas y configuración del dominio. Las rutas son relativas a la raíz del proyecto o a su
padre inmediato; no se aceptan rutas absolutas ni ancestros arbitrarios. Si una huella actual no
coincide, el fixture está **vencido** y no se evalúa. Al recorrer una fuente que es un directorio, no
se cuentan las entradas ocultas (las que empiezan con `.`) ni `__pycache__`: las escriben el editor
o el intérprete al abrirlo, y con ellas dos checkouts del mismo commit daban huellas distintas. Un
archivo oculto nombrado a mano como fuente sí se cuenta.

En el formato `escenarios`, `referencia_ok` conserva únicamente la respuesta global de la
implementación independiente. `oracle_al_generar.global_ok` y
`oracle_al_generar.por_medida` guardan la fotografía de Oracle al emitirlo. La primera comprueba el
acuerdo independiente del conjunto; la segunda detecta cambios individuales, incluso si dos errores
se compensan y el `AND` global permanece igual. Una fotografía individual no se presenta como una
referencia independiente.

Un veredicto guardado es un booleano o, desde la distribución `0.23.1`, un mapa con `ok`, el `valor`
con que salió —`"SIN EVIDENCIA"` cuando una relación de `requiere` no aportó filas— y `levanta`
cuando la evaluación levantó `ErrorDeAlgebra`. Las dos formas valen: la corta es lo único que
afirmaron los fixtures anteriores, y reclamarles lo que no declararon los volvería inválidos sin que
nada haya cambiado. La larga distingue tres veredictos que en un booleano se ven iguales —un rojo,
un SIN EVIDENCIA y un error—, y por eso un cambio entre ellos sí se detecta. El mensaje del error no
entra: dos implementaciones independientes lo redactan distinto, y compararlo volvería contrato a la
redacción.

Un fixture puede además traer `medidas_declaradas`: la forma canónica de las medidas que usa y que no
están en ningún catálogo. Existen para contrastar formas del álgebra que ninguna medida publicada
usa; sin ellas, esas formas esperan a que alguien escriba una medida real que las use, que es esperar
por la razón equivocada. No entran en la huella del catálogo —firmarlas con lo que el propio fixture
dice sería una huella que se comprueba a sí misma—: las cubre la huella del emisor donde están
escritas.

La serialización es JSON canónico con orden estable, sin `NaN`; toda aleatoriedad deriva su semilla
de SHA-256 y cualquier repositorio temporal fija las fechas que intervienen en sus identificadores.
Regenerar dos veces con las mismas entradas debe producir exactamente los mismos bytes.

## 7. Criterio de aceptación de esta especificación

Comprobable, y si falla el diseño está mal:

1. una medida sobre **piezas** y una medida sobre **nodos de un grafo** usan los mismos operadores,
   sin adaptador;
2. una medida **sobre medidas** no introduce ninguna construcción nueva;
3. el corpus guarda los tres niveles con el mismo formato (en superficie `.caso` para autoría o `.json` para almacenamiento);
4. **todo caso del corpus que declara una medida se pone en rojo** con esa medida. El que quede verde
   señala lenguaje faltante o medida mal escrita, y hay que decir cuál. Los casos con
   estado `abierto` **siguen verdes a propósito**: son el hueco declarado, no una falla del
   evaluador. Los casos `resuelto` y `limite_humano` conservan memoria, pero no cuentan como deuda.

**Condición de parada:** si los casos del corpus no se ponen rojos con este juego chico de
operadores, se para y se rediseña — no se agregan operadores hasta que entren.

## 8. Preguntas abiertas

Escritas porque una especificación que finge no tener huecos es peor que una con huecos marcados.

**Las cuatro originales están cerradas**, y sólo una de ellas amplió el álgebra: la ausencia trajo
`agrupar` (y, en `0.8`, `sin`; ver abajo). El orden resultó ser un campo del hecho, la recursión salió del álgebra hacia el sensor, y
la igualdad de flotantes se resolvió prohibiéndola. Que tres de cuatro se cierren sin agregar
operadores es la única prueba de que el juego chico alcanzaba.

- **Ausencia.** ✅ **RESUELTA, y sin nulos.** «Módulo sin ningún importador REAL» parecía pedir un
  anti-join, y un `LEFT JOIN` habría metido el concepto de nulo —la peor verruga de SQL—. La solución
  no necesitó operador nuevo más allá de `agrupar`: se agrupa sobre el producto **sin filtrar** y se
  agrega con `suma` sobre un predicado. Los booleanos suman 0 y 1, así que **un grupo donde nada casó
  da cero y sigue existiendo**:

  ```json
  ["unir", ["de","modulo","m"], ["de","importa","i"]],
  ["agrupar", [["modulo", ["campo","m","nombre"]]],
              [["reales","suma", ["y", ["==", ["campo","i","b"], ["campo","m","nombre"]],
                                       ["==", ["campo","i","es_test"], false]]]]],
  ["donde", ["==", ["col","reales"], 0]]
  ```

  Quedaba un límite, y era peor de lo que la palabra «límite» sugiere: si la relación del lado
  derecho está **vacía**, no hay pares, no hay grupos, el agregado sobre cero filas da `0` y un
  umbral `<= 0` lo lee como éxito. La medida **se ponía más verde cuanto peor estaba el mundo** —con
  un importador señalaba los módulos muertos; con ninguno, verde—. Declararlo en el `alcance` lo
  volvía visible sin cerrarlo, y esta sección lo llamaba RESUELTO tres líneas después de admitirlo
  (ver [`043-ausencia-total-sale-verde`](corpus/proceso/)).

  **Cerrado con `requiere`, y no con un operador.** No era expresable con los cinco: sin join no hay
  correlación, y `DECISION-002` prohíbe que una medida consuma la salida de otra. `["requiere",
  <relación>, …]` es un nodo opcional de la medida y el espejo exacto de `alcance` —uno declara qué
  NO ve, el otro qué NECESITA ver—; el evaluador comprueba la precondición **antes** de medir y
  emite `SIN EVIDENCIA`, que no es verde ni un rojo del mundo. El álgebra queda intacta.

  El caso general que esto expone: **un agregado sobre cero filas es indistinguible de un agregado
  que dio cero**, y sólo la medida sabe cuál de las dos cosas es.

  **En `0.8` la anti-junta entra como operador: `sin`** (§3). El truco de `agrupar` alcanzaba para
  una medida y no para las cinco que la necesitaban: las demás delegaban el conteo a un sensor en
  Python —`commits_de_cierre`, `mutantes`, `casos_que_la_evaluan`…— para comparar contra cero, y un
  conteo fuera del lenguaje no lo contrasta el diferencial, no lo toca la mutación de medidas y el
  catálogo no puede decir qué cuenta. Con `sin`, «ninguna fila de B corresponde a esta de A» se
  escribe en la medida. Sigue sin haber nulos: la fila sale como llegó o no sale.
- **Recursión.** ✅ **RESUELTA, y fuera del álgebra.** «Alcanzable desde» no se expresa con los
  operadores, y es la pared que hizo falta `WITH RECURSIVE` en SQL. Un operador `cierre` habría sido
  recursión en un lenguaje que se mantiene chico a propósito, con **un solo usuario**. La salida es
  más fiel a la doctrina: **la alcanzabilidad es un HECHO**, y producir hechos es trabajo del sensor.

  ```
  alcanzable(desde, hasta, saltos)
  ```

  El álgebra la mide como cualquier otra relación, sin saber nada de grafos. `nucleo/grafo.py` pone el
  BFS para que ningún sensor tenga que reimplementarlo — que era el otro riesgo, acumular la misma
  función en cada dominio. No es una evasión: es la misma línea que separa el sensor del juez en todo
  lo demás.
- **Igualdad de flotantes.** ✅ **RESUELTA negándose — y la prohibición ahora es L2.** El `raise`
  de carga que prohibía `==` sobre flotante en el umbral final se retiró: una medida con `== 0.3`
  está bien formada y se carga. El juicio de que es una mala idea vive en dos lugares: `algebra.comparar`
  sigue fallando cerrado al EVALUAR (la medida no puede producir un verde), y la política
  `meta.ningun_umbral_flotante_de_igualdad` la vuelve inspeccionable en L2, con su `porque`, su
  `alcance`, casos de corpus en las dos polaridades y la mutación probándola.

  La igualdad exacta sólo tiene sentido sobre cosas que se **cuentan** o se **nombran** —enteros,
  booleanos, textos—, y ahí sigue permitida. Sobre cosas que se **miden** hace falta una tolerancia,
  que es justamente lo que el lenguaje pide para todo umbral:

  ```json
  ["<=", ["cerca", a, b], tolerancia]
  ```

  Las comparaciones de ORDEN sobre flotantes siguen permitidas: una tolerancia *es* una comparación
  de orden.
  Tanto `==` como `!=` sobre un flotante levantan error al evaluar, aunque el otro operando sea
  entero. La prohibición vale para expresiones y para el umbral final.
- **Orden.** ✅ **RESUELTO: es un campo del hecho.** No puede ser una propiedad de la relación, porque
  L0 dice que una relación es una **bolsa sin orden semántico**. Entonces «consecutivos» es aritmética
  sobre el campo ordinal, y para eso alcanzó con declarar las escalares `mas` y `menos`.

  Ejemplo real: «la traza no tiene huecos» se expresa agrupando por corrida y comparando la cuenta de
  eventos contra el último instante — `["!=", ["col","registrados"], ["mas", ["col","ultimo"], 1]]`.
  Sin operador nuevo.

## 9. Presupuesto de evaluación

Una medida puede recibir evidencia hostil o simplemente demasiado grande. `LimitesAlgebra` forma
parte de la llamada de evaluación y acota filas por relación (`filas_por_relacion = 100_000`),
filas que puede materializar un producto cartesiano (`producto_cartesiano = 1_000_000`),
profundidad de una expresión (`profundidad_expresion = 64`) y expansiones de macros
(`expansiones_maximas = 16`). Un consumidor puede elegir otros valores sin alterar un global
compartido. Superar un límite es
`ErrorDeAlgebra`, nunca un veredicto verde ni una evaluación parcial.

Estos techos no son umbrales de una medida: protegen al evaluador y por eso no deciden nada sobre el
mundo medido.

## 10. Lo que esta versión deliberadamente no tiene

Sintaxis propia con parser (la forma de dato alcanza), transporte por red (cero consumidores remotos)
y optimizador. Los límites impiden una expansión no acotada; no vuelven eficiente una consulta grande.
