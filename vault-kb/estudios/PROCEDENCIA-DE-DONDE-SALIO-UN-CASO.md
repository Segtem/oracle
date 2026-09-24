# Inverificable no es infalsable

**Fecha:** 2026-09-07. **Estado:** medida escrita, en sombra sobre el propio corpus. Sin corte.

Sale de una pregunta que se le hizo a dos agentes después de publicar 0.8.1: si nada distingue una
corrida de una transcripción, ¿queda algo que se pueda comprobar sin fingir que se comprobó la
autenticidad? La respuesta de los dos, por caminos distintos, fue que **autenticidad no**, y las dos
señalaron lo mismo al pasar: los casos que dicen `observada` no dicen de dónde salieron.

## El hallazgo, contado

`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` es la medida que sostiene la afirmación más
cara del proyecto: que una medida no está fijada sólo con evidencia escrita a mano. Cuenta
`c.procedencia != "observada"`, y su `alcance` ya dice lo que no puede ver:

> «NO verifica que el commit exista, ni que la evidencia se corresponda con ese commit, ni que quien
> escribió `observada` haya observado algo. Un caso puede mentir en `procedencia` y esta medida no
> lo ve»

Eso está declarado y es correcto. Lo que **no** estaba declarado es la segunda mitad. Contado sobre
el corpus del propio Oracle, antes de tocar nada:

| | |
|---|---|
| casos que declaran `procedencia: observada` | **95** de 184 |
| de ésos, cuántos nombran un comando o un registro | **1** |
| qué declaran los otros 94 | `repo` y `commit` |

`repo` y `commit` sitúan un **árbol**: dicen dónde estaba escrito el código. No dicen que se haya
ejecutado, ni con qué salió, ni dónde quedó eso. Así que la afirmación de esos 94 casos no sólo es
inverificable —eso ya se sabía y está aceptado—: es **infalsable**, porque nadie sabe adónde ir a
contradecirla. Y son exactamente los casos sobre los que se apoya la medida de arriba.

**Las dos cosas no son lo mismo, y confundirlas es lo que dejó pasar esto meses.** Oracle no puede
verificar ninguna procedencia. Pero un caso que dice dónde quedó su registro se puede ir a mirar, y
uno que no lo dice, no.

## El precedente, que ya estaba adentro

El proyecto ya hizo este movimiento una vez, para los umbrales:

| | umbral | procedencia |
|---|---|---|
| la etiqueta | `segun` | `observada` |
| ¿se verifica? | no — «NO juzga si la etiqueta elegida es verdadera» | no — «un caso puede mentir en `procedencia`» |
| ¿se exige decir de dónde salió? | sí, `meta.todo_umbral_declara_de_donde_sale` | **no había nada** |

`segun` no verifica el número; obliga a decir de dónde salió, y `sin_declarar` es la ausencia
visible. La medida nueva es ese mismo movimiento, aplicado a la única procedencia que afirma algo
sobre el mundo.

## Qué se agregó

**`meta.todo_caso_observado_declara_de_donde_salio`** — si un caso declara `observada`, su `origen`
tiene que nombrar un `comando` o un `registro`. No verifica que existan: un caso puede declarar los
dos y mentir en los dos, y la medida lo dice en su `alcance`.

Para que el lenguaje pudiera verlo, la relación `caso` de `nucleo/marco.py` expone un campo nuevo,
`declara_de_donde_salio`. Antes exponía `procedencia` y nada de `origen`: ninguna medida podía
mirar si un caso observado decía dónde auditarlo.

**La sombra.** El corpus propio queda en **rojo 94**, declarado en `oracle.json` con fecha y motivo.
Se cierra de a un caso, escribiendo en cada `origen` el comando que lo produjo, y **sólo cuando
alguien pueda afirmar cuál fue**: rellenar los 94 de memoria sería inventar exactamente la
procedencia que la medida existe para hacer visible.

**Los consumidores ya cumplen**, y no por casualidad. Jam sale verde porque sus casos no declaran
`observada`. LyraGASP sale verde con sus dos casos observados porque el `origen` se lo escribió
`observar.py`: la herramienta de 0.8.1 ya hacía lo que esta medida ahora exige.

## Tres cosas que aparecieron haciéndola

**Un falso verde en el propio sensor de la medida.** `str(origen.get(campo, ""))` sobre un
`"comando": null` daba la cadena `"None"` —no vacía—, así que un caso que declaraba el campo en
nulo pasaba como si dijera de dónde salió. Lo encontró un test escrito para matarlo, no la lectura.
Es el mismo defecto que la medida persigue, cometido adentro.

**Declarar una sombra rompía el chequeo de CI.** El workflow exigía exactamente una línea `✗ meta.`,
y un rojo en sombra se imprime con `✗`. O sea: el mecanismo que existe para **no** tapar una deuda
rompía el chequeo que existe para que nada se tape. Ahora se cuentan dos números por separado —los
que tumban la corrida y los declarados en sombra— y los dos se fijan con su línea literal.

**La medida obligó a sus propios casos a cumplirla.** Los casos 483 y 484 declaran `observada`, así
que tienen que decir de dónde salieron; su `comando` nombra `tools/sondear_procedencia.py`, que
existe por eso. Un comando que nombra un script que no está en el repositorio sería el mismo puntero
a la nada que la medida persigue.

## Lo que esto NO es

No es autenticidad, y no acerca a ella. Un caso puede declarar un `registro` que no existe, o uno
que existe y describe otra corrida. Los dos agentes coincidieron —por caminos distintos— en que
toda comprobación barata de autenticidad es teatro: prohibir `cp`, exigir tiempo de CPU o mirar
`atime` se sortea con un script de dos líneas, y presentarlas como filtro produce el falso verde que
el proyecto persigue. Eso sigue igual que en 0.8.1, y el registro sigue diciendo
`autenticidad.comprobada: false`.

Lo que cambia es más chico y se puede afirmar entero: **de un caso observado ahora se puede exigir
que diga por dónde ir a contradecirlo.**

## Números

Corpus **186 casos** · suite **1381 tests** · mutación de medidas **915/915 sin sobrevivientes**
(eran 902; los 13 de la medida nueva mueren) · mutación de `tools/sondear_procedencia.py`
**17/17 sin sobrevivientes ni equivalentes declarados** · aceptación con **un rojo que tumba y uno
en sombra**, las cuatro comprobaciones de CI en verde · Jam **✓ 20 rojos y 3 verdes**, LyraGASP
**✓ 14 y 14**, los dos con la medida nueva en cero. Cifras y manual regenerados.

Sobre la primera ronda de mutación quedaron **cuatro sobrevivientes** en la sonda; tres eran
constructos que no compraban nada —`indent` y `ensure_ascii` sobre archivos temporales que sólo lee
un parser— y se **retiraron** en vez de declararse equivalentes. El cuarto era `sys.argv[1:]` sin
test, y ahora lo tiene.
