# 0.9.1 — una herramienta que se cae no informa nada

Sube únicamente el parche, según `ESPECIFICACION.md` §0:

```
VERSION_DISTRIBUCION   0.9.0 → 0.9.1     `oracle test` informa en vez de morir
VERSION_ALGEBRA        0.6   → 0.6       mismo evaluador y forma canónica
VERSION_SINTAXIS       0.2   → 0.2       mismo lector de medidas y casos
```

Parche y no menor, y la diferencia con 0.9.0 es el mismo criterio aplicado al revés: aquél subió la
menor porque una medida universal nueva podía hacer que un consumidor pasara de verde a rojo. Acá
**nadie cambia de color**. Un proyecto con todo imprimible seguía y sigue en verde; uno con un
archivo ilegible ya salía distinto de cero, sólo que por una excepción sin atrapar.

## Qué pasaba

`oracle test --proyecto <consumidor>` moría con un traceback:

```
ValueError: la macro ninguno lleva 8 argumento(s) y recibió 6
```

La **primera** excepción del impresor se llevaba la corrida entera. No se informaba ni uno de los
archivos que no se pudieron procesar, y las cuatro etapas siguientes —aceptación, diferencial,
mutación, veredicto— no se ejecutaban. Un consumidor con un archivo roto no recibía un informe con
un problema: **no recibía informe**.

Medido contra un consumidor real: 33 de sus 41 medidas, escritas contra una aridad anterior de las
macros `ninguno`, `peor` y `ninguno-par`. Cargan y evalúan bien —su corpus, su aceptación, su
mutación y su diferencial pasaban—; lo que no se podía era imprimirlas. No es una regresión: se
reproduce idéntico instalando 0.5.0, 0.8.1 y 0.9.0 en entornos limpios.

## Qué hace ahora

`_fila_verificacion` y `_fila_verificacion_caso` devuelven una fila que declara lo que pasó, con dos
campos nuevos —`imprimio` y `error`—, y `verificar_catalogo` los junta en `ilegibles`. `oracle test`
los informa primero, con nombre y motivo, recortando a diez y diciendo cuántos faltan:

```
SINTAXIS ✗ — 33 de 64 archivo(s) no se pudieron imprimir
  · catalogos/espacio/espacio.ganable.json — ValueError: la macro ninguno lleva 8 argumento(s) y recibió 6
  … y 23 más
```

**Las dos fallas de sintaxis se dicen distinto, a propósito.** «No coincidió la ida y vuelta» afirma
que la superficie pierde información; «no se pudo imprimir» dice que no hubo superficie que
comparar. Usar la misma frase manda a buscar el defecto al lugar equivocado. Es la distinción que el
núcleo ya hace con `Veredicto.sin_evidencia` y la que la relación `equivalencia` modela con su campo
`error`.

## Lo que NO cambia

**El código de salida sigue siendo distinto de cero.** Lo que no se pudo verificar no se da por
bueno. El precedente aplicable es `SIN EVIDENCIA` —que la aceptación cuenta como falla— y no el de
las sombras, que exigen una declaración deliberada con fecha y motivo en `oracle.json`: el arnés
nunca decide solo que algo pase a sombra.

**No se agrega ninguna medida al catálogo.** Sería universal, se pondría roja en el consumidor, y el
consumidor **no puede arreglarla**: sus medidas son árboles válidos que el cargador acepta; quien no
puede imprimirlas es el impresor de Oracle. `DECISION-012` lo dice — «un rojo sobre el que el
receptor no puede actuar enseña a ignorar la herramienta».

## Verificación del corte

Suite **1394 tests** · corpus **186 casos** · mutación de medidas **915/915 sin sobrevivientes** ·
mutación de `tools/cli.py` **500/500 sin sobrevivientes**, con los dos equivalentes declarados
reapuntados tras correrse de línea · aceptación con un rojo que tumba y uno en sombra, y las cuatro
comprobaciones literales de CI en verde.

Se midió también `tools/sintaxis.py`, que no estaba en el perfil de mutación: **95 mutantes, 52
muertos, 42 sobrevivientes, 1 error de arnés, 2353 segundos**. NO entra al perfil en este corte,
porque los 42 son deuda anterior —**30 en `main()`**, el plumbing del CLI, y **cero** en el código
nuevo—, y meterlo pondría al proyecto en rojo por algo ajeno a este cambio. Queda en `PRIORIDADES`
con el número escrito, como se hizo con `aceptacion.py`. El error de arnés es propio y quedó
anotado: mutar `if __name__ == "__main__"` hace que el módulo corra `main()` al importarse y rompa
el descubrimiento de tests.

El detalle está en `estudios/UNA-HERRAMIENTA-QUE-SE-CAE-NO-INFORMA.md`.

---

# 0.9.0 — un caso observado tiene que decir por dónde ir a contradecirlo

Este corte agrega una medida al catálogo universal y un campo a una relación del marco. Sube
únicamente la distribución, y sube la **menor** y no el parche, según `ESPECIFICACION.md` §0:

```
VERSION_DISTRIBUCION   0.8.1 → 0.9.0     el catálogo universal gana una medida que obliga
VERSION_ALGEBRA        0.6   → 0.6       mismo evaluador y forma canónica
VERSION_SINTAXIS       0.2   → 0.2       mismo lector de medidas y casos
```

La menor y no el parche porque la medida es de **ámbito universal**: obliga también a los
consumidores, y uno que actualice sin usar nada nuevo puede pasar de verde a rojo. Los dos
consumidores conocidos salen en cero, y eso es un hecho de sus corpus, no una garantía de este
corte.

## Inverificable no es infalsable

`procedencia: observada` es la única procedencia que afirma algo sobre el mundo, y Oracle no puede
verificarla. Eso ya estaba declarado, y sigue igual. Lo que no estaba declarado es la otra mitad,
contada sobre el corpus del propio Oracle antes de tocar nada:

| | |
|---|---|
| casos que declaran `observada` | **95** de 184 |
| de ésos, cuántos nombran un comando o un registro | **1** |
| qué declaran los otros 94 | `repo` y `commit` |

`repo` y `commit` sitúan un **árbol**: dicen dónde estaba escrito el código, no que se haya
ejecutado, ni con qué salió, ni dónde quedó eso. La afirmación de esos 94 casos no sólo es
inverificable: es **infalsable**, porque nadie sabe adónde ir a contradecirla. Y son exactamente los
casos sobre los que se apoya `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`, la medida que
sostiene que una medida no está fijada sólo con evidencia escrita a mano.

## `meta.todo_caso_observado_declara_de_donde_salio`

Si un caso declara `observada`, su `origen` tiene que nombrar un `comando` o un `registro`. **No
verifica que existan**: un caso puede declarar los dos y mentir en los dos, y la medida lo dice en
su `alcance`. Es el mismo movimiento que `segun` hizo con los umbrales —no verifica el número,
obliga a decir de dónde salió— aplicado a la procedencia.

Para que el lenguaje pudiera mirarlo, la relación `caso` de `nucleo/marco.py` gana el campo
`declara_de_donde_salio`. Antes exponía `procedencia` y nada de `origen`: ninguna medida podía ver
si un caso observado decía dónde auditarlo.

**Esto no es autenticidad y no acerca a ella.** Sigue sin haber forma de distinguir una corrida de
una transcripción, y toda comprobación barata de autenticidad —prohibir `cp`, exigir tiempo de CPU,
mirar `atime`— se sortea con un script de dos líneas. `observar.py` sigue escribiendo
`autenticidad.comprobada: false`. Lo que cambia es más chico y se puede afirmar entero: de un caso
observado ahora se puede exigir que diga por dónde ir a contradecirlo.

## La sombra sobre el propio corpus

Oracle queda en **rojo 94**, declarado en su `oracle.json` con fecha y motivo. Se cierra de a un
caso, escribiendo en cada `origen` el comando que lo produjo, y **sólo cuando alguien pueda afirmar
cuál fue**: rellenar los 94 de memoria sería inventar la procedencia que la medida existe para hacer
visible.

Los consumidores ya cumplen, y no por casualidad. Jam sale verde porque sus casos no declaran
`observada`; LyraGASP sale verde con sus dos casos observados porque el `origen` se lo escribió
`observar.py` — la herramienta de 0.8.1 ya hacía lo que esta medida ahora exige.

## Tres cosas que aparecieron haciéndolo, y que no se ocultan

**Un falso verde en el sensor de la propia medida.** `str(origen.get(campo, ""))` sobre un
`"comando": null` daba la cadena `"None"` —no vacía—, así que un caso que declaraba el campo en nulo
pasaba como si dijera de dónde salió. Lo encontró un test escrito para matarlo, no la lectura del
código. Es el mismo defecto que la medida persigue, cometido adentro.

**Declarar una sombra rompía el chequeo de CI.** El workflow exigía exactamente una línea `✗ meta.`
y un rojo en sombra se imprime con `✗`: el mecanismo que existe para **no** tapar una deuda rompía
el chequeo que existe para que nada se tape. Ahora se cuentan dos números por separado —los que
tumban la corrida y los declarados en sombra— y los dos se fijan con su línea literal.

**La medida obligó a sus propios casos a cumplirla.** Los casos 483 y 484 declaran `observada`, así
que tienen que decir de dónde salieron; su `comando` nombra `tools/sondear_procedencia.py`, que
existe por eso. Un comando que nombra un script ausente del repositorio sería el mismo puntero a la
nada que la medida persigue.

## Verificación del corte

Corpus **186 casos** · suite **1381 tests** · mutación de medidas **915/915 sin sobrevivientes**
(eran 902) · mutación de `tools/sondear_procedencia.py` **17/17, sin sobrevivientes ni equivalentes
declarados** · aceptación con **un rojo que tumba y uno en sombra**, y las cuatro comprobaciones
literales de CI en verde · Jam **✓ 20 rojos y 3 verdes**, LyraGASP **✓ 14 y 14**, los dos con la
medida nueva en cero. Cifras y manual regenerados.

Sobre la primera ronda de mutación de la sonda quedaron **cuatro sobrevivientes**. Tres eran
`indent` y `ensure_ascii` sobre archivos temporales que sólo lee un parser: constructos que no
compran nada, y se **retiraron** en vez de declararse equivalentes. El cuarto era `sys.argv[1:]` sin
test, y ahora lo tiene.

El detalle está en `estudios/PROCEDENCIA-DE-DONDE-SALIO-UN-CASO.md`.

---

# 0.8.1 — la evidencia observada tiene un recorrido, y ese recorrido se puede romper

Este corte agrega una herramienta y no toca el lenguaje. Sube únicamente la distribución, según
`ESPECIFICACION.md` §0:

```
VERSION_DISTRIBUCION   0.8.0 → 0.8.1     el paquete gana `tools/observar.py`
VERSION_ALGEBRA        0.6   → 0.6       mismo evaluador y forma canónica
VERSION_SINTAXIS       0.2   → 0.2       mismo lector de medidas y casos
```

Un `.oracle` y un `.caso` se leen y se evalúan exactamente igual antes y después. La herramienta
**usa** el lenguaje que ya se distribuía —`Referente`, `hechos_de_frescura`, la medida de referente
vencido y la de polaridad del caso— y no agrega ni cambia ninguno.

## Qué hace `tools/observar.py`

Oracle no tiene sensores: viven en el consumidor, que es el único que sabe leer su dominio. Lo que
faltaba era el recorrido alrededor de una corrida, y es lo que entra acá:

```bash
python tools/observar.py capturar  --plan <plan.json> --destino <carpeta>
python tools/observar.py revalidar --plan <plan.json> --registro <registro.json>
```

`capturar` ejecuta el sensor del consumidor **como otro proceso** —no importa su código—, dos veces,
y sólo escribe si las dos lecturas coinciden, si las relaciones que el plan declara traen filas, si
ningún referente cambió durante la corrida y si el resultado coincide con la expectativa **escrita
en el plan antes de correr**. Entonces conserva tres archivos: la evidencia **byte a byte como la
emitió el sensor**, un registro y el caso, con `procedencia: observada` y esa evidencia incorporada
íntegra. Ante una discordancia no escribe nada y deja la lectura rechazada sin borrar.

La polaridad no la decide un `if` de la herramienta: se arma el caso y lo juzga
`meta.el_caso_se_pone_como_debe`, la misma medida que usa la aceptación.

Todo lo que el plan declara es **relativo a su raíz**, y una ruta absoluta se rechaza al leerlo. Lo
que sólo vale en una máquina —la raíz absoluta, el intérprete, el argv real— queda en un bloque
`maquina` que `revalidar` no usa. `espera.valor` es opcional a propósito: el número que dio una
corrida es de esa corrida, no un contrato del recorrido.

## Lo que este corte NO empieza a demostrar

`revalidar` compara lo que se registró contra lo que se lee hoy, y separa tres cosas que es fácil
confundir: la **observación histórica** —que lee y nunca corrige—, la **frescura** de los referentes
y la **autenticidad**, que **no comprueba**. Cada registro y cada informe llevan escrito
`autenticidad.comprobada: false` con el motivo: las huellas comparan una declaración contra una
relectura, y dos declaraciones falsas iguales pasan igual que dos verdaderas.

En concreto, y medido: un «sensor» que no lee nada del mundo, uno que le agrega filas inventadas a
una lectura real, y un `cp` de un JSON escrito a mano **pasan los tres**, y salen con
`autenticidad.comprobada: false`. Quien use esta herramienta no puede deducir de un caso `observada`
que alguien haya medido el mundo; puede deducir que un programa corrió, que su salida se conservó
sin tocar y que no cambió entre dos lecturas seguidas.

## Un defecto que la mutación no podía encontrar

El control de estabilidad comparaba las dos lecturas **ya parseadas**, con el `==` de Python, donde
`True == 1` y `1 == 1.0`. Un sensor que emitía `true` en una corrida y `1` en la otra pasaba el
control con bytes y tipos distintos, y el caso salía como observación de algo no reproducible.

Lo encontró un ataque adversario, no la mutación: los 146 mutantes del archivo estaban muertos
cuando el defecto seguía ahí. La mutación pregunta «¿algún test nota si cambio esta línea?»; el
defecto vivía en el **significado de `==`** sobre datos parseados. **Cero sobrevivientes no es cero
defectos.**

La comparación ahora es sobre la **forma canónica** —valor y tipo—, no sobre los bytes: reordenar
las claves de un objeto sigue sin ser un cambio, y las dos corridas escriben en rutas distintas que
un sensor podría incluir en su salida. Dos casos nuevos de la suite fijan las dos caras.

## Verificación del corte

**1353 tests OK · corpus 184 · mutación de medidas 902/902 · mutación de `tools/observar.py`
146/146 sin sobrevivientes, sin timeouts, sin errores de arnés y sin equivalentes declarados.** La
aceptación conserva su única medida meta roja y la línea literal que CI exige. Los dos consumidores
conocidos pasan: Jam con 23 casos y LyraGASP con 28, conservando sus tres sombras cada uno.

`tools/observar.py` entra a `HERRAMIENTAS_CUSTODIAS` y a la matriz de mutación de CI: custodia que
un caso `procedencia: observada` haya salido de una corrida, y nadie más lo comprueba —`corpus.py`
valida la forma del caso y `aceptacion.py` su polaridad—.

Se retiraron tres constructos equivalentes (`shutil.rmtree(…, ignore_errors=True)` sobre un temporal
que siempre existe): un equivalente genuino se borra, no se declara. `equivalentes.json` no cambió.

Wheel y sdist en `dist/`, versión 0.8.1. Sus **119 archivos de código y datos coinciden byte a byte
con el árbol**. Instalación limpia en un venv vacío fuera del checkout: `oracle 0.8.1`, álgebra
`0.6`, y el recorrido **corre desde el paquete instalado** —`python -m
oracle_metalenguaje.tools.observar capturar`— cargando sus dos medidas meta del catálogo empaquetado
y produciendo la misma evidencia que el árbol de trabajo.

Primer uso real: el sensor de dataset de LyraGASP, 37 clips declarados, 37 FBX presentes y 0 ground
truth, con la evidencia y el caso conservados en ese repositorio. Detalle en
`estudios/OBSERVAR-0.8.1-RECORRIDO.md`.

# 0.8.0 — el generador tiene que romper el umbral que la medida declara

Este corte deja de tratar el cero como umbral implícito del generador y ejerce una magnitud real
en el catálogo propio. Sube únicamente la distribución, según `ESPECIFICACION.md` §0:

```
VERSION_DISTRIBUCION   0.7.0 → 0.8.0     herramientas y catálogo distribuidos
VERSION_ALGEBRA        0.6   → 0.6       mismo evaluador y forma canónica
VERSION_SINTAXIS       0.2   → 0.2       mismo lector de medidas y casos
```

El generador y una fórmula del catálogo cambian; el lenguaje no gana nodos ni formas y no cambia
el significado de un operador. Una misma medida se sigue leyendo y evaluando igual. La fórmula
distribuida de antigüedad de sombras sí es distinta, con el cambio observable explicado abajo.

## Fabricar una propuesta no demuestra su polaridad

Antes, la heurística proponía una sola fila ofensora como `falso_verde`: para `contar <= 5` daba
verde. El filtro de utilidad ya descartaba esa propuesta antes de escribir, pero escondía el
motivo bajo «ruido». No se comprobó que el defecto escribiera casos inválidos en el corpus.

Ahora `fabricar_candidatos` evalúa las propuestas antes de entregarlas. Para conteos simples con
cota superior amplifica la evidencia: seis filas para `<= 5`, cinco para `< 5`, respetando el
presupuesto de filas y volviendo a evaluar. No aplica esa regla a máximos, uniones o agrupaciones.
Si una propuesta no alcanza la polaridad o carece de evidencia requerida, explica la negativa.

`oracle caso generar` conserva «ruido» si no quedan mutantes por matar. Si quedan y no puede
fabricar evidencia válida, sale con código 1, explica el límite y no escribe archivos. Quien
automatice el comando debe contemplar esa negativa; quien use la función interna debe contemplar
`GeneracionNoPosible`. El generador no se convirtió en un sintetizador general de magnitudes.

## La antigüedad se publica en días

`meta.ninguna_sombra_envejece_sin_revisarse` conserva su identificador, el contrato de revisión a
90 días y el ámbito universal. Ahora usa la macro existente `peor`, con tolerancia 90. La polaridad
y los testigos se conservan, pero **el valor deja de ser cantidad de incumplimientos y pasa a ser
la edad máxima incumplida, en días**. Con sombras de 91 y 244 días publica 244, no 2.

Sin sombras vencidas publica cero y ningún testigo: no informa la edad máxima de sombras recientes.
No se añade `requiere`, porque no tener sombras es correcto. Los consumidores de `valor`, umbral,
unidad o expansión de esta medida deben actualizar sus expectativas; no alcanza con comprobar que
el color no cambió. Las series históricas de conteos y edades no son comparables sin distinguir
la versión del catálogo. Las versiones de álgebra y sintaxis no detectan cambios de catálogo.

Los casos 479 y 480 fijan edades distintas y ausencia de sombras. La plantilla de medidas orienta
hacia `oracle manual peor` cuando el dominio es una magnitud, sin elegir una tolerancia por el autor.

## La suposición queda bajo custodia

`python tools/sondear_generador.py` ejecuta cinco sondas y publica 17 comprobaciones de entrega y
polaridad. Las juzga la medida existente `meta.el_caso_se_pone_como_debe`, con campos existentes;
no se agrega una relación al lenguaje. Negarse siempre, entregar una lista vacía o sólo rojos no
puede pasar. La sonda corre en CI y su código entra en la matriz de mutación.

El caso 481 reproduce la contradicción histórica con evidencia construida. El 482 registra la
ejecución del programa sobre esas entradas construidas: observa el programa, no un dominio externo.
No sustituye el trabajo pendiente de obtener evidencia del mundo en el plan del sensor.

## Verificación y límites del corte

La implementación pasó **1295 tests**, **184 casos** y **902/902 mutantes de medidas**: 750 por
conducta y 152 rechazados por el álgebra. La edad de sombras cierra 9/9; la nueva sonda, 27/27
mutantes de código, sin sobrevivientes, tiempos agotados, errores de arnés ni equivalentes declarados.
Los controles nuevos de `fabricar_candidatos` cierran 22/22 en mutación dirigida: no es una
certificación de todo el generador histórico.

Se retiraron constructos equivalentes de la sonda y los valores por defecto imposibles de las
coordenadas de `ErrorSintaxis` en `tools/medida.py`, junto con su declaración histórica. Los tres
sitios de coordenadas afectados cierran 3/3 en mutación dirigida; no se repitió todo ese archivo.

La aceptación conserva exactamente los dos pendientes declarados y la línea literal exigida por CI:

```
la_medida_no_se_fija_solo_con_evidencia_fabricada        2 (<= 0)
```

Es una única medida meta roja, por `meta.sintaxis_cubre_algebra` y
`meta.sintaxis_casos_cubre_casos`, y la aceptación sale con código 1. Jam pasa con 23 casos y
LyraGASP con 26; ambos conservan tres sombras y salen con código 0. Los informes de mutación
siguen avisando cuando una medida no puede juzgar la evidencia del otro arnés por campos ausentes.

El inventario de once sitios quedó revisado, no borrado: siguen declarados los límites de monotonía
de `max`/`min`, el cero de agregados vacíos y la fabricación no general de magnitudes. No se cambió
la semántica ni la procedencia de los mutadores ajenos para ocultarlos. El servidor MCP no se tocó.

Con la distribución en 0.8.0 se repitieron suite, corpus, aceptación propia y de consumidores,
mutación de medidas y mutación de la sonda, conservando los números anteriores. Se regeneraron
las cifras y el manual HTML. Wheel y sdist se construyeron con
`uvx --from build pyproject-build --wheel --sdist`: los 121 archivos de código y datos de ambos
coinciden byte a byte con el árbol. Setuptools conserva sus avisos sobre directorios de datos no
declarados como paquetes; la comprobación confirma que están incluidos.

El wheel instalado en un venv limpio fuera del repositorio devuelve `oracle 0.8.0`, álgebra `0.6`
y sintaxis `0.2`; ejecuta `oracle reportar --help`, las 17 comprobaciones de la sonda y la medida
de sombras con valor 244 y con ausencia de sombras. La verificación amplia de instalación pasa
los diez ejecutables, los datos y los motores aislados. No se publicó en PyPI ni se hizo push.

---

# 0.7.0 — cuando Oracle no alcanza, el límite ya tiene por dónde entrar

Este corte agrega un canal público de reporte sin convertir a Oracle en emisor de datos ni al issue
en evidencia del corpus. En el corte sube únicamente la distribución:

```
VERSION_DISTRIBUCION   0.6.0 → 0.7.0     el paquete y sus ejecutables
VERSION_ALGEBRA        0.6   → 0.6       lo que una medida SIGNIFICA
VERSION_SINTAXIS       0.2   → 0.2       cómo se ESCRIBE
```

La distribución sube porque el paquete incorpora `oracle reportar` y su canal documentado.
El álgebra no sube: no agrega nodos, operadores, agregados, escalares ni relaciones de traza, y no
cambia la semántica existente. La sintaxis tampoco sube: el lector de `.oracle` y `.caso` no aprende
palabras ni cláusulas y sigue aceptando las mismas formas con el mismo significado. Es la regla de
`ESPECIFICACION.md` §0.

## `oracle reportar`: preparar no es publicar

`oracle reportar` pregunta qué se quiso expresar o medir, qué ocurrió en cambio y cómo se detectó.
Con eso y el diagnóstico existente arma un artefacto Markdown estructurado que se puede leer en la
terminal o guardar con `--salida`. No abre un issue, no usa la red, no recibe credenciales y no llama
«reportado» a un archivo que sólo quedó guardado localmente.

La salida automática se construye desde la misma lista positiva de `oracle diagnostico`. Una medida
y una evidencia sólo entran mediante `--incluir-medida` y `--incluir-evidencia`, respectivamente;
sin esas opciones no sale ningún dato del dominio. Las rutas conocidas se redactan también en la
prosa y en los anexos explícitos, pero eso no permite prometer que un texto libre carezca de secretos.
Por eso la salida se muestra completa antes del único acto de publicación: copiarla a mano.

El módulo quedó incorporado a la custodia de mutación el día en que se escribió: **19/19 mutantes
rechazados, cero sobrevivientes**.

## Del artefacto al issue, sin perder la estructura

La nueva plantilla «Reporte de límite» recibe el artefacto completo tal cual. Sus campos conservan
los nombres que comparten con un `.caso`: `sintoma`, `como_se_detecto`, `medida` y `evidencia`; el
reporte suma `diagnostico` y separa dentro del síntoma lo esperado de lo ocurrido. El README y el
sitio explican el comando, las inclusiones explícitas, la revisión previa y que el destino es
público.

No se agregó un canal privado ni publicación automática. Si un hallazgo no puede reducirse y
anonimizarse para un issue público, 0.7.0 no tiene un destino seguro para recibirlo.

## Un issue aspira a ser un caso; todavía no lo es

La guía de promoción deja el borde operativo escrito. Un mantenedor reproduce el comportamiento,
sostiene el juicio semántico sobre qué debía ocurrir y convierte lo observado en evidencia L0. El
caso necesita los campos del esquema y un mapa no vacío de relaciones a filas escalares. Puede
nombrar una medida existente o declarar `medida: null` junto con
`estado_sin_medida: abierto` y una explicación en `sin_medida_todavia`; inventar un id no reemplaza
una capacidad ausente.

`tools/corpus.py` rechaza la forma inválida y la aceptación comprueba la medida y la polaridad. Si
nadie puede reproducir el reporte, no se fabrica evidencia: el issue puede conservar la conversación
o cerrarse como no reproducible, pero no entra al corpus ni cambia sus conteos.

## Recibido no significa prometido

**Abrir un reporte registra un límite; no promete diagnóstico, prioridad, fecha ni arreglo.** El
canal separa deliberadamente recibir una observación, demostrarla como caso y decidir cualquier
cambio de producto.

El servidor MCP no participa y conserva íntegro el contrato de sólo lectura de 0.6.0: ninguna
herramienta MCP escribe archivos, publica reportes ni transmite datos.

## Verificación del corte

El corte local de 0.7.0 pasa **1266 tests** y el corpus conserva **180 casos** con esquema,
evidencia L0 y trazabilidad en regla. La aceptación mantiene exactamente los dos rojos declarados en
`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`:

```
meta.la_medida_no_se_fija_solo_con_evidencia_fabricada        2 (<= 0)
```

La aceptación sale con código 1 por esa única medida meta en rojo: los dos pendientes son
`meta.sintaxis_cubre_algebra` y `meta.sintaxis_casos_cubre_casos`. Jam pasa con 23 casos (20 rojos
esperados y 3 verdes correctos); LyraGASP, con 26 (12 y 14). Ambos conservan sus tres sombras
declaradas y salen con código 0.

La mutación de `tools/reportar.py` confirma 19 muertos, cero sobrevivientes, cero tiempos agotados,
cero errores del arnés y cero equivalentes declarados. Conserva una advertencia explícita:
`proceso.test_con_mutante_que_lo_mata` no puede juzgar esa evidencia porque falta
`detecciones_conductuales`; las tres medidas que juzgan la mutación de código dan verde.

La plantilla coincide con los encabezados emitidos por `oracle reportar` y con los nombres del
impresor de `.caso`. La revisión del sitio corrigió la paleta y las reglas de 2 px de la página
nueva para usar la identidad existente y reglas de 3 px. También corrigió sus enlaces del pie,
que al pasar el cursor daban 2,57:1 contra el fondo oscuro. La comprobación en Chromium recorre los
62 elementos con texto contra su propio fondo, a 1280 y 390 px y con los enlaces en reposo y bajo
el cursor: contraste mínimo 6,65:1, sin desborde horizontal. La página no contiene texto SVG.

El wheel y el sdist se construyen localmente; una instalación del wheel en un venv limpio fuera
del repositorio devuelve `oracle 0.7.0`, álgebra `0.6`, sintaxis `0.2`, y ejecuta
`oracle reportar --help`. Los 117 archivos de código y datos empaquetados coinciden byte a byte
con el árbol. Setuptools advierte sobre directorios de datos no declarados como paquetes; la
comprobación del contenido confirma que están incluidos. No se publicó en PyPI.

Se regeneraron las cifras del README (1266 tests y 5502 sitios de mutación de código) y el manual
HTML; el manual ya coincidía con su generador.

---

# 0.6.0 — Oracle contesta por MCP, y la respuesta lleva sus premisas

Nueve commits desde `0.5.0`. Sube únicamente la distribución:

```
VERSION_DISTRIBUCION   0.5.0 → 0.6.0     el paquete y sus ejecutables
VERSION_ALGEBRA        0.6   → 0.6       lo que una medida SIGNIFICA
VERSION_SINTAXIS       0.2   → 0.2       cómo se ESCRIBE
```

## Las tres versiones: qué sube y por qué

- **Distribución (`0.5.0 → 0.6.0`)**: sube porque el paquete incorpora el servidor
  `oracle-mcp`, sus tres herramientas, su contrato y sus pruebas de punta a punta.
- **Álgebra (`0.6`)**: no sube. MCP consulta, evalúa y desafía medidas mediante el álgebra que ya
  existía; no agrega un nodo, operador, agregado, escalar ni relación de traza a la forma canónica.
- **Sintaxis (`0.2`)**: no sube. El lector no aprende ninguna palabra, cláusula ni separación
  nueva, y ninguna forma aceptada cambia de significado o deja de aceptarse.

## Resumen de los commits del corte

- Se documentó que actualizar Oracle puede vencer un fixture diferencial y exigir regenerarlo
  antes de mutar (`5de7f21`).
- `oracle contexto` dejó de convertir un catálogo ilegible en «cero medidas», pasó a usar el
  catálogo efectivo y quedó enteramente bajo mutación (`20a2ded`, `4743b3e`).
- Dos estudios independientes fijaron el alcance, los fallos y el contrato MCP; se descartó con
  evidencia la compuerta de escritura propuesta originalmente (`3f14ec3`, `824fc1b`).
- Se implementaron en orden el transporte y las tres herramientas de sólo lectura, cerrando la
  ronda de `tools/mcp.py` en 297/297 (`ada8e01`, `61f89b0`, `50e02d8`).
- El sitio ganó una explicación de dónde entra Oracle y de los límites que ningún servidor puede
  prometer (`f3954ce`).

Oracle gana un servidor MCP de **sólo lectura** para que un agente pueda preguntarle qué mide un
proyecto sin parsear salidas pensadas para personas:

- **`oracle_catalogo_efectivo`** enumera qué medidas obligan en la raíz fijada y de dónde salen;
  al pedir ids devuelve además sus premisas, umbral, ámbito y fijación, y distingue una medida
  desconocida de una conocida que no tiene jurisdicción en ese proyecto.
- **`oracle_evaluar`** evalúa contra evidencia JSON una medida del catálogo o un texto `.oracle` o
  JSON recibido en memoria. Devuelve por separado `verde`, `rojo` y `sin_evidencia`, con valor,
  umbral, alcance derivado, testigos y advertencias; no acepta rutas.
- **`oracle_desafiar`** reproduce los casos verdes y rojos de una medida y recién entonces ejecuta
  sus mutantes. Informa discordancias, rechazos del álgebra y sobrevivientes sin convertir «todos
  detectados por esta evidencia» en una aprobación semántica.

Las tres operan sobre la raíz fijada al arrancar el servidor. **El servidor no escribe nada**: no
guarda medidas ni evidencias, no modifica el proyecto y no persiste los candidatos recibidos en
memoria. Las **16 conversaciones JSON-RPC** de las tres herramientas están en
[`estudios/MCP-CONVERSACIONES.md`](estudios/MCP-CONVERSACIONES.md), capturadas contra el servidor
real.

## Por qué NO hay una herramienta que guarde medidas

La primera propuesta tenía una: guardaría una medida sólo si venía con evidencia que la pone en rojo
y evidencia que la pone en verde. Se descartó por dos razones medidas, no de gusto.

El corpus tiene 180 casos. **152 los cazó el arnés automático y 28 se le escaparon**, y de esos 28 la
compuerta de escritura ataja **cero**: ninguno es «alguien guardó una medida sin probarla». El
**85,7 %** son falsos verdes, y ocurren al LEER.

Y las dos evidencias que la compuerta exigiría pueden haber sido fabricadas para repetir exactamente
el error de la medida. Entonces no autoriza a llamarla buena — y guardar después de ella convierte
evidencia insuficiente en apariencia de aprobación.

## La regla que ordena todo el servidor

**Un agente no tiene con qué dudar de la herramienta.** Si el servidor contesta
`{"veredicto": "verde"}`, lo toma como verdad y sigue.

> **Fallo cerrado y respuestas falsables. Nunca una lista vacía, nunca un verde suelto, nunca un
> resumen opaco.** Un catálogo ilegible produce un error, no un cero.

O, como quedó escrito en los fixtures de aceptación: **«no pude mirar» y «miré y no hay nada» son
afirmaciones distintas y jamás deben viajar por el mismo canal.**

Esa regla se validó antes de escribir una línea del servidor. Buscando cómo tenía que ser el MCP se
encontró que `oracle contexto` le decía a los dos consumidores conocidos «LAS 0 MEDIDAS QUE YA
EXISTEN» teniendo 41 y 9 medidas propias: un `except Exception: return []` se tragaba el fallo de
cargar sus escalares, y el defecto vivió meses. Está arreglado, y `tools/contexto.py` entró al perfil
de mutación —donde su primera medición dio 20 sobrevivientes de 30—.

## Lo que ningún servidor puede prometer

De esos 28 casos que el arnés no cazó, **14 quedan fuera del alcance de cualquier protocolo de
herramientas**: fallas de runtime y señales, saltos causales del propio modelo, falsificación
deliberada en disco, y deudas de diseño del lenguaje. Prometer más es vender humo. Lo que el
servidor sí puede es erradicar la otra mitad.

## Los dos rechazos que le enseñan algo a un agente

```
MEDIDA_NO_EFECTIVA   existe en una fuente seleccionada, pero su ámbito no obliga acá
MEDIDA_DESCONOCIDA   no aparece en ninguna fuente seleccionada
```

«No existe» invita a crear un duplicado; «no tiene jurisdicción acá» enseña que el archivo ya tiene
dueño. La distinción sólo es posible gracias al ámbito de 0.5.0.

## El transporte no es el del LSP

MCP sobre stdio usa **un objeto JSON-RPC UTF-8 por línea, sin cabeceras**. `tools/lsp.py` es buen
precedente en cuatro decisiones —biblioteca estándar, despachador explícito, respuestas compactas,
stdout reservado al protocolo— pero **su enmarcado `Content-Length` no se copia**. Y `stdout` queda
sólo para el protocolo: una línea humana suelta corrompe el canal.

## Verificación del servidor

`tools/mcp.py` entró al perfil de mutación **el mismo día que se escribió**, antes de construir la
segunda herramienta. Su primera medición fue la peor del proyecto: **154 mutantes, 60 sobrevivientes,
53 minutos**. Dos cosas que aparecieron ahí no eran deuda cosmética:

- **los códigos de error JSON-RPC no los fijaba nada** — el servidor podía devolver `-32601` donde
  correspondía `-32602` y pasar la suite entera, y un cliente despacha por ese número;
- **las anotaciones que el servidor publica sobre sí mismo** —`readOnlyHint`, `destructiveHint`—
  tampoco. Todo el diseño se apoya en que es de sólo lectura, y esa promesa vivía en constantes que
  nadie comprobaba.

La ronda final cerró en **297/297 mutantes rechazados, cero sobrevivientes**. El corte pasó 1243
tests, el corpus de 180 casos y la aceptación con exactamente los dos rojos declarados en
`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`. Jam y LyraGASP siguieron en aceptación.
El wheel 0.6.0 se instaló además en un entorno limpio: `oracle --version` publicó las tres versiones
esperadas y el paquete expuso `oracle-mcp` como ejecutable.

---

# 0.5.0 — una medida declara dónde obliga, y «empaquetada» deja de significar «universal»

Tres commits desde `0.4.0`. Suben la distribución, el álgebra y la sintaxis:

```
VERSION_DISTRIBUCION   0.4.0 → 0.5.0     el paquete que se instala
VERSION_ALGEBRA        0.5   → 0.6       lo que una medida SIGNIFICA
VERSION_SINTAXIS       0.1   → 0.2       cómo se ESCRIBE
```

## Las tres versiones: qué sube y por qué

Cada número responde a una regla fija de `ESPECIFICACION.md` §0 para que la compatibilidad se
detecte en vez de descubrirse:

- **Distribución (`0.4.0 → 0.5.0`)**: el paquete que se instala. Sube porque incorpora el soporte
  de ámbito en la carga, las nuevas meta-medidas y los arreglos al arnés de mutación y al manual.
- **Álgebra (`0.5 → 0.6`)**: sube la versión MENOR porque el álgebra gana un nodo opcional nuevo
  (`ambito`) sin alterar la semántica de lo que ya existía. Quien no lo usa sigue evaluándose igual;
  pero quien implementa el álgebra completa —una referencia independiente— queda incompleto y debe
  actualizarse para reconocer el nuevo nodo.
- **Sintaxis (`0.1 → 0.2`)**: sube la versión MENOR porque el lector de la superficie infija
  (`.oracle`) aprende una cláusula nueva (`ambito universal | del_origen`) que antes era un error de
  sintaxis. Un archivo `.oracle` viejo escrito contra 0.1 se sigue leyendo idéntico.

## ⚠ Nota de migración: el ámbito es obligatorio en las macros

`ambito` es ahora un **parámetro obligatorio** en las cuatro macros del lenguaje (`ninguno`,
`ninguno-par`, `ninguno-requiere` y `peor`).

### Cómo migrar en concreto

En cada medida escrita con macros en tu catálogo, agregá la línea `ambito universal` o
`ambito del_origen` entre el `umbral` (o el `requiere`) y el `alcance`:

```oracle
ninguno mi_dominio.mi_politica:
    de mi_relacion r
    donde r.estado == "invalido"
    umbral <= 0 segun contrato porque "el estado debe ser valido"
    ambito universal
    alcance "comprueba la validez de los estados registrados"
```

Si la medida usa la macro `ninguno-requiere`:

```oracle
ninguno-requiere mi_dominio.otra_politica:
    de mi_relacion r
    requiere mi_precondicion p
    umbral <= 0 segun contrato porque "..."
    ambito universal
    alcance "..."
```

### El catálogo existente sigue cargando sin tocar nada

Para no invalidar el catálogo entero de un consumidor al actualizar la versión, el cargador y las
macros conservan la ausencia de la cláusula como el estado transitorio `sin_declarar`. Es el mismo
camino que se abrió cuando se incorporó `segun`: no se inventa un valor por omisión arbitrario, sino
que se registra honestamente que el autor todavía no eligió.

Sin este escalón de migración, introducir el parámetro obligatorio rompía la carga de cualquier
proyecto consumidor antes de permitirle clasificar sus propias medidas. Se probó qué pasaba sin él, y
Jam pasaba de 25 medidas a cero.

### Pero `sin_declarar` NO es una declaración aceptable

`sin_declarar` es sólo la ausencia visible que dejan las formas anteriores durante la transición. La
nueva medida de presencia `meta.toda_medida_declara_su_ambito` lo reclama en rojo.

Hoy esa meta-medida se declara a sí misma `del_origen` —por eso un consumidor que actualiza a 0.5.0 no
se pone en rojo todavía—. Pero esto es **TEMPORAL**: está registrado en el plan que debe volverse
`universal` cuando los proyectos consumidores hayan migrado sus catálogos. Declararla hoy `del_origen`
evita teñir de rojo un árbol ajeno en el primer minuto, pero el estado final exige la declaración y la
medida pasará a ser universal para que ningún catálogo conserve medidas sin ámbito explícito.

### El criterio para elegir: ¿de quién es el remedio?

No existe un valor por omisión creíble: asumir `universal` reproduciría la fuga de obligar a terceros
en falso, y asumir `del_origen` apagaría en silencio guardas de calidad que sí deben viajar. Al migrar
una medida, el criterio para decidir es directo:

> **¿El proyecto que recibe el rojo tiene un remedio disponible en SU repositorio?**

- **`ambito universal`**: si quien recibe el veredicto en rojo puede corregir el problema tocando su
  propio código, sus datos o su configuración. Obliga a todo proyecto que incorpore el catálogo y
  aporte la evidencia.
- **`ambito del_origen`**: si el fallo sólo puede corregirse modificando el repositorio del autor de
  la medida (su arnés de pruebas, su manual, su empaquetado o su código fuente). Obliga únicamente
  cuando el proyecto evaluado es el mismo que publicó la política.

## ⚠ Nota de migración: los fixtures diferenciales se vencen al actualizar

Un fixture del diferencial fija la huella del catálogo contra el que se generó. La reificación de
una medida ahora incluye `ambito`, así que **la huella cambia aunque el catálogo del proyecto sea
byte a byte idéntico**. Un fixture que incluya el catálogo reificado en su mundo se va a declarar
vencido al actualizar a 0.5.0, y `oracle-mutar` se niega a correr mientras haya uno vencido — la
mutación queda bloqueada hasta regenerarlo.

Eso es el mecanismo de frescura haciendo su trabajo, no un defecto: una referencia se fija a una
versión exacta porque un agregado puede no romper a un consumidor y sí a un evaluador que no conoce
el nodo nuevo.

Se regenera con el emisor del dominio, no a mano. Regenerar **vuelve a comprobar el acuerdo** con la
implementación de referencia; si discrepan, falla. Medido al actualizar un consumidor: de sus once
fixtures se venció **uno solo** —el del dominio que incluye el catálogo reificado—, la regeneración
cambió una única línea (la huella) y el diferencial volvió con 1099 acuerdos globales contra
referencias independientes y 4298 veredictos individuales estables.

La consecuencia práctica: al actualizar, corré el diferencial **antes** que la mutación. El fixture
vencido no dice que algo esté mal; dice que todavía nadie comprobó que siga estando bien.

## Por qué: un rojo sin remedio enseña a ignorar la herramienta

Hasta hoy, «universal» significaba una sola cosa: residir físicamente en el directorio empaquetado de
Oracle (`catalogos/`). Eso describe **procedencia**, no **ámbito**. Ambas nociones coincidieron de
hecho mientras todas las políticas que Oracle empaquetaba obligaban por igual a cualquier proyecto que
las adoptase.

Esa coincidencia se quebró cuando una medida sobre la configuración interna del arnés de Oracle
(`meta.ninguna_exclusion_de_mutador_se_aplica_globalmente`, que vigila `EXCLUSIONES_DE_MUTADORES`) puso
en rojo a Jam. Era el único rojo duro que Jam tenía en todo su catálogo, y Jam no tenía ningún
remedio disponible en su propio repositorio: la lista de exclusiones vive en `nucleo/mutacion.py`,
dentro del árbol de Oracle. Para apagar esa alerta, Jam no podía hacer nada por sí mismo.

`DECISION-009` ya formulaba el principio: **un rojo sobre el que el receptor no puede actuar enseña a
ignorar la herramienta.** Un veredicto sin remedio destruye la autoridad del sistema entero y entrena
al usuario a desoír las alarmas legítimas.

El hueco era conceptual: Oracle creía responder tres preguntas y sólo respondía dos. Sabía de dónde
vino una medida (catálogo base, perfiles, bibliotecas o local) y si había hechos para calcularla
(`medidas_aplicables`). Pero **nadie contestaba a quién obliga**. Poder calcular un veredicto no vuelve
pertinente ese veredicto.

Ahora el ámbito es explícito y relativo al **origen**, no a Oracle:
- En una medida del catálogo base, `del_origen` significa que sólo obliga a Oracle.
- En una medida escrita dentro de Jam, `del_origen` significa que obliga a Jam y se satisface sola.
- En una biblioteca de políticas, `del_origen` obliga a su publicador al auditarse o certificarse, no a
  los consumidores que la instalen.

Oracle no tiene ningún privilegio nominal en el lenguaje. El orden de las preguntas queda explícito en
la carga:

```text
selección del catálogo → ámbito → aplicabilidad por relaciones → evaluación
```

No es un nivel nuevo (L2 es un punto fijo: el catálogo tiene 56 medidas, 56 filas en `medida`, y la regla
que juzga el alcance está entre las filas que juzga; nivel y ámbito son ortogonales). Tampoco es
visibilidad (`private` no aplica donde no hay llamadas entre medidas por `DECISION-002`): la analogía
es la jurisdicción de una regla. Una medida `del_origen` sigue en el manual, sigue reificada en L2, sigue
mutando y sigue teniendo casos de corpus; sólo no dicta veredicto donde no hay responsabilidad para
responderla.

## El efecto medido sobre los catálogos

La clasificación de las 56 medidas del catálogo base arrojó una partición exacta:
- **37 universales**
- **19 del origen**

Sobre Jam, el resultado fue inmediato: de las 25 medidas que antes concluían sobre su repositorio,
ahora concluyen **exactamente 20**. El ámbito le retiró a Jam **exactamente cinco medidas**, aquellas
sobre las que no tenía remedio:

1. `meta.todo_vocabulario_cerrado_esta_en_el_manual` (evaluaba si el manual de Oracle estaba completo)
2. `meta.el_diagnostico_no_publica_el_dominio`
3. `meta.ninguna_exclusion_de_mutador_se_aplica_globalmente`
4. `meta.toda_opcion_del_vocabulario_declara_su_sentido`
5. `meta.todo_verbo_del_cli_esta_en_la_ayuda`

Jam quedó en ACEPTACIÓN ✓, libre de un veredicto ajeno que no le correspondía. Las otras medidas
clasificadas como `del_origen` operan sobre relaciones producidas por sondas sintéticas (como la
conmutatividad de `unir` o la reversibilidad del serializador) que un consumidor no emite en su
evidencia; en ellas, el ámbito hizo explícito lo que antes quedaba omitido por falta de evidencia.
LyraGASP se mantuvo sin cambios (✓).

## La cota del ámbito y dos criterios que coincidieron sin consultarse

Una declaración humana no basta si no puede contrastarse. Se incorporó la meta-medida
`meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias`: una medida no puede obligar a
más proyectos que aquellos donde su evidencia tiene dueño. Si se declara `universal` pero consume una
relación que describe la instalación del origen, su fallo sólo lo puede resolver el origen y declararla
universal se lo traslada a un consumidor que no tiene remedio.

La cota cruza tres relaciones en álgebra pura mediante `unir` anidado —`medida`, `dependencia_de_medida`
y `ambito_de_relacion`—, sin relaciones ad-hoc denormalizadas ni lógica de juicio en Python.

La reificación de `dependencia_de_medida` unifica las dos vías por las que una medida se ata a una
relación: `fuente` (de donde extrae filas) y `requiere` (la precondición que produce `SIN EVIDENCIA`).
El caso 477 del corpus ofende precisamente por `requiere`, confirmando que vigilar sólo las fuentes
dejaba una vía abierta.

El caso 478 confirmó una coincidencia notable: en el catálogo base hay 13 dependencias reales sobre
relaciones `del_origen`, y las 13 provienen de medidas que ya habían sido clasificadas a mano como
`del_origen` preguntándose quién tenía el remedio. Dos criterios enteramente independientes —el juicio
editorial humano sobre la responsabilidad del remedio y la derivación mecánica desde las relaciones
consumidas— dieron exactamente la misma respuesta sobre las 55 medidas. No prueba que la clasificación
sea correcta: prueba que no se contradice consigo misma, que es lo único que una medida puede comprobar.

## Lo que la cota NO promete

La cota automática detecta una contradicción derivable —una medida universal que consume relaciones
del origen— y **nada más**:
- **No demuestra que una medida universal sea realmente universal.** No puede detectar una suposición
  del origen escondida en el valor de un literal, ni una convención asumida en el código que sólo se
  menciona en la prosa.
- **No demuestra que el receptor tenga de verdad un remedio disponible en su repositorio.**

El marco asume una asimetría deliberada: mentir hacia lo amplio perjudica a terceros con rojos
inaccionables, y por eso se combate con verificación automática estricta. Declarar un ámbito demasiado
estrecho sólo retiene una política en su autor original; pierde cobertura compartida, pero no impone un
rojo sin remedio a nadie. La estrechez se discute con revisión humana y evidencia externa. Oracle vuelve
falsable la consistencia de la declaración; no sustituye el discernimiento sobre la pertinencia.

## Arreglos en el arnés y en el manual

- **Exclusión de mutadores por medida:** `_mutadores_ajenos()` aplicaba la exclusión en tiempo de
  importación globalmente, sin consultar el predicado. La exclusión se evalúa ahora por medida en
  `mutantes()`. No alteró los números en los catálogos principales, pero destapó cobertura oculta: la
  biblioteca de ejemplo certificaba 16 mutantes cuando eran 17 (el mutador de `umbral <= 5` nunca había
  corrido).
- **Alarma sobre mutadores en el paquete instalado:** Al comprobarse la exclusión por medida, la
  alarma sobre su premisa pasó a ser verdadera por construcción. Se reorientó a vigilar que nadie vuelva
  al filtrado global, y allí se descubrió que `mutadores/` no viaja en el wheel: un consumidor instalado
  carece del módulo y la versión inicial lo confundía con una exclusión global. Ahora
  `mutadores_declarados_por_sus_autores()` lee el módulo del autor y no el registro ya construido
  (caso 471).
- **Manual en HTML:** En `oracle manual --html`, 56 de 90 términos `<dt>` se dibujaban superpuestos a
  su definición porque los navegadores no consideran el guión bajo como punto de corte de línea en CSS.
  Se corrigió el estilo.
- **Simbología y enlaces en el arnés:** La lectura de ámbitos descarta symlinks para no admitir
  declaraciones de jurisdicción que apunten fuera del repositorio evaluado. Además, se eliminaron
  guardas y retornos muertos en la sección vacía del manual y en el cargador de ámbitos.

## Las cifras de este corte

```
1127 tests · 180 casos del corpus · 56 medidas (37 universales · 19 del origen)
relacion 94/94 · medida 250/250 · unidad 198/198 · manual 78/78
tools/medida 264/264 · referente, diagnostico y aceptacion limpios
aceptación: 2 rojos declarados (DECISION-004)
Jam ✓ · LyraGASP ✓
```

## Límites conocidos

- **Los dos rojos de `DECISION-004` siguen a propósito.** `oracle test` sale con código 1.
- **La medida `meta.toda_medida_declara_su_ambito` es temporalmente `del_origen`.** Se mantiene así
  para permitir la migración de los consumidores sin teñir sus árboles de rojo, pero debe promoverse a
  `universal`.
- **La cota de ámbito sólo vigila hacia lo amplio.** Una medida declarada `del_origen` que podría ser
  `universal` no genera ningún aviso automático; su pertinencia sigue dependiendo de la revisión humana.
- **El catálogo base sigue anclado en `<= 0`.** 56 de 56 medidas comparan contra cero.

---

# 0.4.0 — el manual se explica solo, la sombra envejece, y los mutadores dejan de tener un solo autor

Ocho commits desde `0.3.3`. El álgebra y la sintaxis no se movieron: no hay operadores nuevos ni
cambió cómo se escribe una medida, así que sólo sube la distribución.

```
VERSION_DISTRIBUCION   0.3.3 → 0.4.0     el paquete que se instala
VERSION_ALGEBRA        0.5               lo que una medida SIGNIFICA (sin cambios)
VERSION_SINTAXIS       0.1               cómo se ESCRIBE (sin cambios)
```

## ⚠ Dos cosas que le cambian el número a un proyecto que ya usa Oracle

**Si tu proyecto declara `"catalogo_base": true`, hereda dos medidas nuevas** —
`meta.ninguna_sombra_envejece_sin_revisarse` y `meta.toda_sombra_declara_una_fecha_real` — y pueden
ponerlo en rojo si tiene sombras viejas o con fechas ilegibles. Es el mecanismo funcionando: son
sombras que ya estaban mal y nadie las miraba. Se pueden poner en sombra a su vez, con fecha y
motivo.

**Si publicaste una biblioteca de políticas, su certificación deja de valer.** El arnés pasó de 5
mutadores a 28, así que el número de mutantes que tu manifiesto declara ya no coincide. Hay que
volver a medir y republicar: una biblioteca certificada contra 5 mutadores no está certificada
contra 28.

## Los mutadores tienen autor, y hasta ahora era uno solo

`tools/mutar.py` decía 715/715 muertos. Ese 100% medía cobertura sobre cinco mutadores escritos por
la misma persona que escribió las medidas y el corpus, y el problema no se ve desde adentro: **un
mutador que nadie escribió no puede producir un sobreviviente.**

Se repitió el protocolo del evaluador de referencia: otro autor, en aislamiento verificable, con un
directorio de dos archivos y sin ver el repositorio. Escribió 24 mutadores. El corpus mató el 79% en
la primera corrida, y de los que sobrevivieron **tres eran huecos reales** —en medidas escritas ese
mismo día— que sus docstrings habían predicho sin ver nada: «omite casos cercanos al límite si el
corpus sólo contiene anomalías grandes».

No se le creyó la declaración de aislamiento: se auditó su registro de comandos. Está en
`mutadores/PROCEDENCIA.md`, junto al contrato que leyó. Detalle en `DECISION-011`.

## La sombra envejece

`dias` viajaba en la relación desde que existe el modo sombra y ninguna medida lo miraba: una sombra
de 244 días pasaba en verde. Lo único que distingue una sombra de apagar la medida es que alguien la
vaya a sacar, y eso era justo lo que nada comprobaba.

Buscándole los bordes apareció un segundo agujero: `toda_sombra_declara_desde_y_porque` sólo mira que
el campo no esté vacío, así que «cuando pueda» pasaba — y una sombra sin fecha legible tampoco la
encontraba la medida que envejece. Era invisible para las tres a la vez.

## `oracle contexto`

Todo lo que hace falta para escribir una medida en un proyecto, en un solo lugar: las relaciones con
sus campos, con qué se escribe, qué declara toda medida sin excepción, y las que ya existen para no
repetirlas. Derivado del proyecto, no escrito a mano.

`--compacto` da lo mismo en un quinto del texto: **~1.600 tokens contra ~8.600** de correr los tres
comandos que reemplaza — y dice dos cosas que ninguno de los tres decía. El ahorro vino de elegir
qué incluir, no de comprimir el formato.

## El manual cubre las 54 medidas

Cada medida universal ya declaraba qué NO ve, así que documentarlas no costó prosa nueva. Sale del
catálogo cargado, en las tres vistas: terminal, sitio y `man oracle-medidas`.

## El costo de la mutación era un síntoma

`tools/medida.py` tenía 114 mutantes sobrevivientes y tardaba ~90 minutos, y por eso no estaba en la
matriz de CI. Se probaron dos arreglos en ramas separadas, con los criterios fijados por escrito
antes de ver resultados: escribir los tests ganó, y el archivo quedó en **264/264 y 206 segundos**.

Tardaba noventa minutos PORQUE estaba mal fijado: confirmar un sobreviviente cuesta una corrida
completa de la suite, matarlo cuesta ~0,1 s. Así que «no lo agregamos a CI porque sale caro» decía
en realidad «no lo medimos porque nos iría mal». Ya está en la matriz.

Se midieron después los otros cinco archivos custodiados que tampoco estaban en CI: cuatro en cero, y
tres sobrevivientes en `manual.py` que había introducido quien agregó `--man` sin volver a medir.

## Las cifras de este corte

```
1084 tests · 169 casos del corpus · 54 medidas universales
846/846 mutantes de medida · 4928 sitios de mutación de código
28 mutadores: 5 propios + 23 de un segundo autor
aceptación: 2 rojos declarados (DECISION-004)
```

## Límites conocidos

- **Los dos rojos de `DECISION-004` siguen a propósito.** `oracle test` sale con código 1.
- **El catálogo tiene una sola forma:** las 54 medidas comparan con `<= 0`. Por eso 17 de los 24
  mutadores del segundo autor no aplicaron a ninguna, y por eso `convertir_conteo_en_existencia`
  está excluido por equivalencia. **No hay alarma que lo reincorpore** si algún día entra un umbral
  distinto.
- **Siguen siendo dos autores de mutadores, no muchos.**
- **Ningún consumidor escribió todavía una medida meta que necesite una relación nueva**, así que no
  se sabe si la reificación alcanza fuera de las preguntas de este autor.
- **La fachada ocupa `nucleo`, `catalogos` y `perfiles`** como nombres de nivel superior, y los dos
  `__init__.py` que tienen conducta están fuera de la mutación junto con los vacíos.
- **Los dos consumidores que usan Oracle desde PyPI se diseñaron junto con él.** Falta uno que no.
- **Correr el comando instalado parado en el repo de Oracle falla** con «el id está dos veces»: se
  cargan el catálogo del paquete y el del árbol local. El error parece del catálogo y es del entorno.

---

# 0.3.3 — importar la biblioteca le borraba un paquete al que la importa

Segundo defecto encontrado desde afuera del repositorio, un día después del primero y de la misma
familia: el paquete instalado se comporta distinto del checkout, y el arnés miraba el checkout.

## Qué se rompía

Importar `oracle_metalenguaje` registraba en `sys.modules` cuatro nombres de NIVEL SUPERIOR
—`nucleo`, `catalogos`, `perfiles` y `tools`— para que los imports absolutos del núcleo funcionen
en los dos layouts.

`tools` es el nombre de paquete más común que hay en un repositorio. Un consumidor con su propio
`tools/` lo perdía **por importar la biblioteca**, y moría con
`ModuleNotFoundError: No module named 'tools.referencias'` sobre un paquete suyo que existía y no se
había movido.

## Por qué el arnés no lo vio, otra vez

`tools/verificar_instalacion.py` afirmaba justo lo contrario:

```python
for nombre in ("nucleo", "catalogos", "perfiles", "tools"):
    assert importlib.util.find_spec(nombre) is None, nombre
```

Eso mira el disco y corre **antes** de importar nada. Era verdad y decía una mentira: el wheel no
ocupa esos nombres como archivos, los ocupa al importarse.

## El arreglo

El alias de `tools` se mudó de la fachada al propio paquete `tools/`. Se registra cuando corre un
entry point de Oracle —su proceso, donde ocupar el nombre no le saca nada a nadie— y no cuando un
consumidor importa `Motor` o `escalar`.

El verificador ahora crea un consumidor con su propio `tools/`, importa la biblioteca y exige que el
paquete siga siendo el suyo. Se comprobó que el chequeo mide algo poniendo el defecto de vuelta a
propósito: falla con el `ModuleNotFoundError` exacto.

## El riesgo que queda, dicho

`nucleo`, `catalogos` y `perfiles` **se siguen ocupando**: el núcleo se importa a sí mismo por nombre
absoluto y sacarlos es reescribir todos sus imports. Son palabras en español y la colisión es menos
probable, pero no imposible. Es `setdefault`, así que quien ya cargó el suyo lo conserva —y entonces
se rompe Oracle, no él—.

Queda fijado por un test lo que hace seguro haber sacado `tools`: **ningún módulo de `nucleo/` lo
importa**. Si mañana alguno lo hace, ese test se rompe.

Detalle y lo que no se arregla, en `DECISION-010`.

---

# 0.3.2 — el wheel vendorizado dejaba sin fachada al subproceso que corre tus UDF

Un solo defecto, encontrado por el primer consumidor que intentó la migración de subtree a PyPI. Es
el primer defecto de Oracle reportado desde afuera del repositorio.

## Qué se rompía

`nucleo/aislamiento/escalares.py` lanza el subproceso que ejecuta el `escalares.py` de un proyecto
con el entorno **reemplazado**, y le pasaba `PYTHONPATH = RAIZ_ORACLE`. En el repo eso es la raíz,
que contiene `oracle_metalenguaje/`. En el wheel, `RAIZ_ORACLE` **es el directorio del propio
paquete**: quien lo hace importable es su padre.

Así que un consumidor cuyo `escalares.py` hace `from oracle_metalenguaje import escalar` —lo que la
documentación le pide— moría con `ModuleNotFoundError: oracle_metalenguaje`.

**Sólo se rompía fuera de un venv.** Adentro, `site.py` agrega `site-packages` por su cuenta y
tapaba la falta. Afecta a quien vendoriza el wheel con `pip install --target`, que es lo que hace un
consumidor cuyo intérprete es de otro —uno embebido dentro de una aplicación anfitriona— y no puede
crear un venv.

## Por qué el arnés no lo vio

`tools/verificar_instalacion.py` probaba **un solo layout**: construía el wheel, lo instalaba en un
venv, corría un proyecto con `escalares.py` que importa la fachada, y salía `WHEEL OK`. Un verde que
no significaba nada, en la herramienta que existe para decir que el paquete está bien.

Ahora prueba los dos. Y se comprobó que el chequeo nuevo **mide algo**: con el defecto puesto de
vuelta a propósito, el verificador sale 1 con el `ModuleNotFoundError` exacto.

## El arreglo, y los dos que se descartaron

Se le pregunta al importador —`importlib.util.find_spec("oracle_metalenguaje")`— en vez de calcular
la ruta. En el repo **no agrega ninguna entrada**, porque las dos raíces coinciden.

- Se descartó `RAIZ_ORACLE.parent`, que era lo obvio: en el repo eso es el directorio que CONTIENE a
  Oracle, y meterlo en el camino de un subproceso que existe para confinar una UDF ajena es lo
  contrario de aislar.
- Se descartó derivarlo de `__package__`: `oracle_metalenguaje/__init__.py` aliasa `nucleo` como
  paquete de nivel superior, así que ese archivo termina importado **dos veces bajo dos nombres,
  como dos objetos distintos**, y desde el que se usa el layout del wheel es invisible.

Está escrito en [`DECISION-010`](https://github.com/Segtem/oracle/blob/main/DECISION-010-EL-PAQUETE-INSTALADO-ES-OTRO-PROYECTO.md).

## De paso

Una medida del propio proyecto rechazó la primera versión del arreglo:
`test_la_distribucion_productiva_no_nombra_consumidores_conocidos` tumbó un comentario que nombraba
un consumidor particular. La distribución no conoce dominios, tampoco en sus comentarios.

## Actualizar

```bash
uv tool upgrade oracle-metalenguaje      # o el `pip install --target` con ==0.3.2
```

Si vendorizás el wheel, **0.3.2 es el mínimo**: en 0.3.1 ese camino no carga las UDF del proyecto.

---

# 0.3.1 — la página de PyPI no llevaba a ningún lado

Sólo metadatos de empaquetado. El lenguaje, el álgebra y la sintaxis no se movieron.

Al revisar la página publicada de 0.3.0 aparecieron tres cosas, las tres presentes también en 0.2.0
—así que no eran una regresión, eran un hueco que nadie había mirado—:

- **18 enlaces relativos rotos** en la descripción. El README es la descripción que PyPI publica, y
  ahí no existe el árbol del repositorio: la página invitaba a leer las nueve decisiones, la
  especificación y la licencia, y ninguna se podía abrir. Ahora son absolutos.
- **`project.urls` vacío.** La barra lateral no tenía un solo enlace: quien llegaba a PyPI no tenía
  cómo volver al repositorio, al sitio ni a los issues. Ahora hay siete.
- **`classifiers` vacío.** PyPI no podía filtrar el paquete por versión de Python, por tema ni por
  estado. Ahora hay doce, y el estado —`4 - Beta`— coincide con lo que el README dice en la primera
  pantalla, que es lo mínimo que se le puede pedir a dos declaraciones sobre la misma cosa.

Nada de esto lo detectaba nada, y por eso vivió dos releases. Ahora lo fijan cuatro tests: que el
README no tenga enlaces relativos, que sí conserve sus anclas internas, que el paquete declare a
dónde ir, y que los clasificadores de versión no se despeguen de `requires-python`.

**Los metadatos de PyPI son inmutables por versión**, así que la página de 0.3.0 queda como está.
Este release existe para que la que se ve por omisión sea la correcta.

---

# 0.3.0 — el lenguaje se explica solo, y hereda sin mentir

**30 commits** desde `0.2.0`. Nada del álgebra cambió, así que sólo se mueve la distribución.

```
VERSION_DISTRIBUCION   0.2.0 → 0.3.0     el paquete que se instala
VERSION_ALGEBRA        0.5               lo que una medida SIGNIFICA (sin cambios)
VERSION_SINTAXIS       0.1               cómo se ESCRIBE (sin cambios)
```

## El vocabulario cerrado declara su significado

`falso_verde` era una cadena en un `frozenset` y qué significaba vivía en cuatro `.md` distintos,
ninguno de ellos la fuente. Ahora el nombre y su explicación viajan juntos en la declaración, y de
ahí salen dos cosas.

La primera es el error. Quien escribe `etiqueta: falso_rojito` ya no recibe cinco nombres parecidos:
recibe los cinco **con qué es cada uno**, en el momento exacto en que le hace falta. El diagnóstico
del editor lleva lo mismo.

La segunda es `oracle manual`: la referencia del lenguaje en tres vistas —terminal, sitio (`--html`)
y páginas de manual (`--man`)— armadas de la **misma** fuente. `oracle manual --instalar-man <dir>`
deja `oracle(1)` y una `oracle-<tema>(7)` por tema, y a partir de ahí `man oracle-etiqueta` anda sin
red. Un manual generado no puede quedar viejo; la única grieta es el registro que dice qué generar,
y eso lo mide `meta.todo_vocabulario_cerrado_esta_en_el_manual`.

## Heredar un catálogo sin quedar en rojo el primer día: la sombra

Un proyecto que adopta un catálogo ajeno sale rojo en cosas reales que nadie va a arreglar hoy.
Apagar la medida es volver al verde que no significa nada. La sombra es la tercera opción: la medida
se evalúa, se informa con `[EN SOMBRA]` y no tumba la corrida. `desde` y `porque` son obligatorios
—una sombra sin fecha no se puede envejecer, una sin motivo no se puede discutir— y tres medidas la
vigilan. **Ninguna de esas tres se puede poner en sombra a sí misma.**

## Bibliotecas de políticas

Un catálogo se puede publicar y consumir. Se descubren por `importlib.metadata` **sin importarlas**,
y una distribución cuyo `RECORD` liste Python o un ejecutable se **rechaza**: una biblioteca de
políticas es datos. La adopción es explícita, proyecto por proyecto, en `oracle.json`.

## La documentación entra al arnés

Tres cosas que antes podían envejecer en silencio y ahora se miden: que cada relación que el
lenguaje emite esté nombrada en la especificación, que cada verbo que el comando acepta esté en la
ayuda —había tres que no—, y que cada opción de un vocabulario cerrado se explique.

## Un rojo declarado menos

`DECISION-004` bajó de 3 a 2, y por el camino que ella misma dejaba escrito: no transcribiendo
evidencia inventada sino cambiando el mundo. Los referentes de L−2 **ya se calculaban** dentro de
`revisar_frescura` y morían ahí; exponerlos hizo observable algo que ya ocurría. Los dos que quedan
no se pueden cerrar y la decisión explica por qué.

## Arreglos

- `oracle-lsp` publica CodeLens, y un diagnóstico nunca tiene ancho cero (con ancho cero el editor
  no dibuja nada y el error existe pero no se ve).
- El arnés de mutación dejaba un `.lock` por raíz en `/tmp` y no lo borraba nunca: había 6.257
  archivos de un solo día. Ahora un directorio coordinador serializa abrir/bloquear y borrar/
  desbloquear, así que una ronda entera deja **cero** — sin romper la exclusión, que era lo
  delicado.
- Los ids de `equivalentes.json` son posicionales y se rompían con cualquier línea agregada más
  arriba. Ahora cada entrada guarda el contenido de su línea y su ordinal, y
  `--reapuntar-equivalentes` los reubica sola. El validador sigue fallando cerrado.

## Las cifras de este corte

```
1013 tests · 161 casos del corpus · 52 medidas universales
703/703 mutantes de medida · 4894 sitios de mutación de código
aceptación: 2 rojos declarados (DECISION-004)
```

## Límites conocidos

- **Las dos medidas de `DECISION-004` siguen en rojo, a propósito.** `oracle test` y
  `tools/aceptacion.py` salen con código 1. No es una regresión: es un rojo verdadero que se lee en
  vez de taparse.
- **La adopción por un proyecto ajeno sigue siendo evidencia que este repo no puede fabricar.** El
  proyecto externo sintético demuestra desacoplamiento técnico, no adopción.
- **Ninguna biblioteca de políticas se publicó todavía.** El mecanismo está y se certificó contra
  una biblioteca real instalada; falta que exista una publicada.
- **Los mutadores son de autoría propia.** «703/703 muertos» mide cobertura sobre cinco mutadores
  elegidos por el autor: un mutador que nadie escribió no puede producir un sobreviviente.

---

# 0.2.0 — el primer release público

Primer release etiquetado de Oracle, y el primero con el repositorio abierto. **81 commits** desde
que se fijó `0.1.0`.

`0.1.0` no se etiqueta: ese número ya viaja adentro de los subtrees de dos consumidores, así que
volver a usarlo haría que el mismo nombre signifique dos cosas distintas —justo el problema que
las tres versiones separadas existen para evitar—.

```
VERSION_DISTRIBUCION   0.1.0 → 0.2.0     el paquete que se instala
VERSION_ALGEBRA        0.4   → 0.5       lo que una medida SIGNIFICA
VERSION_SINTAXIS       0.1               cómo se ESCRIBE (sin cambios)
```

## Cinco niveles de representación

El lenguaje dejó de hablar sólo de evidencia y medidas. Ahora nombra los cinco niveles
(`DECISION-005`):

| | |
|---|---|
| **L−2** | identidad y frescura del referente: si lo que se midió sigue siendo lo mismo |
| **L−1** | declaración del sensor: unidades y alcance de lo que produce |
| **L0** | las filas de evidencia |
| **L1** | las medidas |
| **L2** | medidas sobre medidas |

L−1 y L−2 se cerraron con `nucleo/unidad.py`, `nucleo/referente.py` y `nucleo/fixtures.py`, los
tres con mutación sin sobrevivientes.

## La superficie infija

Una medida se escribe y se lee en un formato legible, y el catálogo lo carga **tal cual**: no hay
paso de traducción. El JSON sigue siendo válido y los dos conviven.

```
ninguno meta.ningun_umbral_de_igualdad:
    de medida m
    donde m.comparador == "=="
    umbral <= 0 segun contrato porque "…"
    alcance "…"
```

## El umbral declara de dónde sale su número

`segun` es obligatorio y cerrado: `medicion`, `contrato`, `convencion` o `tanteo`. Un umbral sin
procedencia era un número puesto a ojo con cara de dato (`DECISION-006`).

## Editor: un servidor LSP para Emacs y VS Code

El mismo servidor, sin dependencias de npm ni de pip.

- **Diagnósticos**: error de sintaxis, medida mal declarada, y `SIN FIJAR` sobre las medidas que
  ninguna evidencia pone a prueba.
- **Completado** con la **unidad** del campo — `flotante · cm`, que es lo que ningún otro editor
  muestra.
- **CodeLens**: arriba de cada medida, qué la pone a prueba y con qué umbral.

`oracle-lsp` es ahora un entry point del paquete, así que el editor lo encuentra sin que exista
ningún checkout. Los clientes lo buscan en `ORACLE_LSP` → `oracle-lsp` en el `PATH` → el checkout.

## `unir` con índice: el techo del millón deja de ser el techo

`unir` materializaba el producto cartesiano y recién después filtraba, así que dos relaciones de
2.000 filas pedían 4.000.000 de pares y chocaban contra el límite. Cuando el `donde` que sigue
compara por igualdad dos campos, esa igualdad es una clave: se indexa un lado y se recorre el
otro. **20.000 filas en 0,005 s** sobre los datos que el camino ingenuo rechaza.

El plan ingenuo no se borró: `forzar_plan_unir()` elige cuál corre, y los tests exigen que los dos
den el mismo resultado. Una optimización que reemplaza a lo que optimiza se queda sin nada contra
qué compararse.

## La CLI

`oracle init`, `oracle nueva`, `oracle caso`, `oracle test`, `oracle revisar`, `oracle relaciones`,
`oracle escalares`, `oracle expandir`, `oracle medida probar --con` y `--vigilar`. La CLI entró al
arnés de mutación: **317/317 mutantes muertos**.

## Aislamiento de escalares

`escalares.py` de un proyecto se ejecuta en un **proceso aislado**: una función hostil no puede
leer fuera del proyecto, escribir fuera, abrir red ni lanzar procesos. Sigue exigiendo
`--confiar-escalares`.

## Correcciones que vale la pena nombrar

- **Un subrayado de ancho cero no se ve.** El servidor mandaba el rango del error apuntando al
  final de la línea; el editor lo recortaba y quedaba vacío. Se arregló en el servidor, que es
  donde lo arregla también para Emacs.
- **«Está ejercitada» estaba escrito tres veces** —en el LSP, en `--listar` y como medida—, y las
  tres copias en Python compartían el mismo punto ciego: no miraban los fixtures diferenciales.
  Ahora las herramientas se lo preguntan a `meta.toda_medida_esta_ejercitada`, que es donde el
  reclamo está escrito.

## Decisiones registradas en este ciclo

- `DECISION-004` — dos medidas quedan sostenidas por evidencia generada
- `DECISION-005` — cinco niveles de representación
- `DECISION-006` — de dónde sale el número
- `DECISION-007` — bibliotecas de políticas
- `DECISION-008` — el repositorio se abre

## Límites conocidos

**El servidor LSP necesita un proyecto.** `oracle-lsp` sale con código 1 si no resuelve uno
—`oracle.json` en el directorio de trabajo, o `--proyecto` explícito—. Los editores lo arrancan
sin argumentos y le pasan la carpeta abierta: con una carpeta de proyecto abierta funciona, con un
`.oracle` suelto el servidor se apaga y no hay diagnósticos, dejando sólo una línea en el registro.
Se descubrió verificando el wheel antes de publicar. Lo correcto es que el servidor siga dando
diagnósticos de sintaxis —que no necesitan proyecto— y degrade sólo lo que sí lo necesita; eso
cambia el contrato del servidor y va en la próxima versión, no en un arreglo apurado.

**`tools/medida.py` tiene 114 mutantes vivos.** Es la superficie de la CLI y la deuda es anterior
a esta versión. Ésta es además la primera ronda COMPLETA de ese módulo: las anteriores se cortaban
cerca de los 120 sitios sin decirlo, así que la cifra vieja de «115 sitios · 67 vivos» subestimaba
el tamaño real, que son 264 sitios.

## Estado

Sigue siendo **`EXPERIMENTAL`**. Abrir el repositorio no es declarar que está terminado: la
reflexión sobre el catálogo sigue fijada en Python, que es justo lo que un metalenguaje no
debería necesitar. El camino está en `PLAN-LENGUAJE.md`.

## Instalación

```bash
uv tool install oracle-metalenguaje

oracle init mi-proyecto
```

Con `pip` va en un entorno propio (`python3 -m venv venv && source venv/bin/activate`): en Arch,
Debian 12+, Ubuntu 23.04+ y Fedora, instalar al Python del sistema falla con
`externally-managed-environment` (PEP 668).

También desde el repositorio (`pip install git+https://github.com/Segtem/oracle.git`) o, sin red,
desde el `.whl` adjunto a este release.

Python ≥ 3.11. **Sin dependencias** — se instala offline, desde el archivo.
