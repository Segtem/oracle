# Notas de release

Una sección por versión, de la más nueva a la más vieja. Las anteriores a 0.20 están en
[docs/notas/anteriores-a-0.20.md](docs/notas/anteriores-a-0.20.md).

<!-- notas_indice:inicio -->
| versión | qué trae |
|---|---|
| [0.31.0](#0310--un-verde-que-no-midió-nada-ya-no-sale-verde) | un verde que no midió nada ya no sale verde |
| [0.30.0](#0300--escribí-la-aritmética-como-la-pensás) | escribí la aritmética como la pensás |
| [0.29.0](#0290--un-modelo-como-sensor-de-la-prosa-y-un-lenguaje-que-avisa-mejor) | un modelo como sensor de la prosa, y un lenguaje que avisa mejor |
| [0.28.0](#0280--retomar-es-leer-una-tarea) | retomar es leer una tarea |
| [0.27.0](#0270--una-sombra-perdona-hasta-su-cota-y-el-mcp-se-pone-al-día) | una sombra perdona hasta su cota, y el MCP se pone al día |
| [0.26.0](#0260--el-álgebra-puede-decir-ninguna) | el álgebra puede decir «ninguna» |
| [0.25.2](#0252--el-verificador-del-diferencial-fijado-y-los-dos-consumidores-en-verde) | el verificador del diferencial, fijado; y los dos consumidores en verde |
| [0.25.1](#0251--borradores-de-las-relaciones-que-faltan-declarar-sin-fabricar-un-verde) | borradores de las relaciones que faltan declarar, sin fabricar un verde |
| [0.25.0](#0250--mutar-unos-sitios-sin-poder-confundirlo-con-una-verificación-completa) | mutar unos sitios sin poder confundirlo con una verificación completa |
| [0.24.0](#0240--ningún-mutante-se-come-la-máquina-y-el-tracker-se-lee-de-un-vistazo) | ningún mutante se come la máquina, y el tracker se lee de un vistazo |
| [0.23.1](#0231--el-diferencial-ejercita-lo-que-el-álgebra-agregó-y-compara-el-veredicto-entero) | el diferencial ejercita lo que el álgebra agregó, y compara el veredicto entero |
| [0.23.0](#0230--declarar-el-ámbito-deja-de-ser-cosa-de-oracle) | declarar el ámbito deja de ser cosa de Oracle |
| [0.22.0](#0220--toda-medida-lee-campos-que-existen-y-un-campo-ausente-se-informa-igual-en-todas-partes) | toda medida lee campos que existen, y un campo ausente se informa igual en todas partes |
| [0.21.0](#0210--mutante-es-una-relación-con-variantes-y-requiere-puede-pedir-filas-de-una) | `mutante` es una relación con variantes, y `requiere` puede pedir filas de una |
| [0.20.0](#0200--motor-juzga-con-el-mismo-catálogo-y-las-mismas-sombras-que-oracle-test) | `Motor` juzga con el mismo catálogo y las mismas sombras que `oracle test` |
| 0.19.0 y anteriores | en [docs/notas/anteriores-a-0.20.md](docs/notas/anteriores-a-0.20.md) |
<!-- notas_indice:fin -->

# 0.31.0 — un verde que no midió nada ya no sale verde

```
VERSION_DISTRIBUCION   0.30.0 → 0.31.0   álgebra 1.0, verdes vacíos cerrados, la web nueva
VERSION_ALGEBRA        0.8    → 1.0
VERSION_SINTAXIS       0.7    → 0.7
```

## El álgebra 1.0

Sube la **mayor** del álgebra porque hay medidas que antes daban otro resultado, a veces verde:

- **Los testigos son las filas que salen de la tubería completa**, no las de un paso intermedio.
- **`donde`, `sin`, `requiere` condicional, `y`, `o` y `no` exigen un booleano.** `donde 1` o
  `donde "sí"` eran verdad por accidente; ahora son un error con su ubicación.
- **Las claves se validan en toda la evidencia recibida**, también en relaciones que la medida no
  lee, y **un `null` explícito se rechaza**: si un dato no se pudo decidir, se dice con un campo
  booleano aparte (`x_decidible`), no con un hueco que cada comparación interpreta a su modo.
- **Una relación con cabecera `clave` y cero hechos es vacía** para `requiere`: antes la cabecera
  sola alcanzaba para que `requiere` la diera por presente.
- **`unir … donde` da el mismo resultado y el mismo error con índice que sin él**, con la misma
  ubicación (`en 2.2.1`). Antes, con claves booleanas el índice fallaba donde el producto unía, y sus
  errores de tipos no decían en qué paso ocurrían.

⚠️ **Si tu evidencia trae `null`, no subas sin migrar.** Oracle te dice qué relación, qué fila y
qué campo. LyraGASP y Jam siguen en 0.30.0 hasta migrar.

## Los caminos a un verde vacío, cerrados

- **Una medida propia sin casos pone rojo `oracle test`** (`MEDIDAS SIN CASOS ✗`) y se nombra.
  Antes, nueve medidas sin ningún caso daban VERDE.
- **`oracle nueva` crea la medida con un caso rojo y uno verde de andamio**, y `oracle test` dice
  `ANDAMIO ✗` mientras sigan sin evidencia real.
- **Una sombra perdona un rojo dentro de su cota, nunca un `SIN EVIDENCIA`.**
- **`oracle juzgar` falla si una medida propia no se aplicó.** `--parcial` pide explícitamente una
  corrida modular; `--json` conserva `no_aplicadas`.
- Macros nuevas **`peor-requiere`** y **`ninguno-par-requiere`**, junto a `ninguno-requiere`: si la
  relación es el universo que se evalúa, la variante `-requiere` impide un verde sin sujetos.
- Los agregados sobre cero filas siguen dando `0`, y ahora está escrito: la guarda es `requiere`.

## La mutación se vigila a sí misma

- **Los seis arneses que custodian la mutación entran a la mutación** (`mutar`,
  `generar_diferencial`, `trazar`, `ejecutar_suite_mutacion`, `mutar_codigo`,
  `verificar_instalacion`). El runner congelado de la raíz juzga siempre, así que un arnés mutado
  no puede declararse verde.
- **El perfil declara qué queda fuera de la mutación y por qué**, y falla si aparece un módulo sin
  declarar. `oracle test --todo` lo informa.
- **El arnés publicaba `null` como código de salida** cuando no hubo proceso que terminara, y álgebra
  1.0 lo rechaza: las medidas de proceso no podían juzgar la corrida. Ahora publica `-1`. Lo encontró
  la ronda de mutación de este mismo corte.

## Quien llega nuevo

- Catorce fricciones de quien llega desde PyPI, corregidas: la ayuda lleva al manual,
  `oracle test --help` no corre nada, y `oracle nueva --help`, `medida nueva --help` y
  `caso generar -h` muestran la ayuda en vez de leer la bandera como un id. `oracle nueva` ya no
  puede quedar en un bucle sin fin buscando números libres para sus casos.
- **Las guías se ejecutan.** `tools/guia.py` arma cada recorrido desde una carpeta vacía pegando los
  bloques en orden y compara cada salida con la real: `de-cero`, `02`, `05`, `07` y `13`. Una guía
  que envejece pone roja la suite.
- **La web nueva**: [segtem.github.io/oracle](https://segtem.github.io/oracle/), con varias páginas,
  la documentación renderizada dentro del sitio, escenas en pixel art y la guía «de cero» de una
  batalla naval para quien empieza con un LLM.
- **`ejemplo/batalla-naval/`**: el juego de esa guía, con 11 medidas y 33 casos que las fijan.

## La especificación contesta más

Ocho preguntas en las que el núcleo y la implementación de referencia coincidían sin que el texto lo
dijera quedan escritas, y las divergencias entre los dos se resolvieron con el álgebra 1.0.

# 0.30.0 — escribí la aritmética como la pensás

```
VERSION_DISTRIBUCION   0.29.0 → 0.30.0   aritmética infija, el repo en el motor y la web al día
VERSION_ALGEBRA        0.8    → 0.8
VERSION_SINTAXIS       0.6    → 0.7
```

## `a + 1`, como lo escribe un modelo

Un LLM escribe `t2.turno == t1.turno + 1`. Hasta 0.29.0 el lector lo rechazaba y había que escribir
`mas(t1.turno, 1)`. Ahora la superficie acepta `+`, `-` y `*`, con la precedencia de siempre,
asociación a izquierda y paréntesis, y los lee como las escalares `mas`, `menos` y `por` que ya
existían. **La forma canónica no cambia**: `a + 1` produce exactamente `["mas", a, 1]`, así que ninguna
medida cambia de significado y el álgebra sigue en 0.8.

- **Dentro de una expresión el guion es siempre resta**, también sin espacios: `t1.turno-1` es
  `menos(t1.turno, 1)` y no un campo llamado `turno-1`, que es como lo escribe un modelo. Los nombres
  de macro con guion (`ninguno-requiere`) siguen valiendo en los encabezados.
- Los literales negativos siguen siendo números: `a.x > -1`, `a.x - -1`.
- `/`, `%` y `^` no existen, y el error lo dice con la alternativa: declarar una escalar y llamarla
  por su nombre.

## El repositorio es el motor

La raíz tenía el motor mezclado con doce decisiones, dieciocho planes, tres relevos, un compendio
generado de 16 000 líneas y más de sesenta entradas en `estudios/`. Tres modelos (Codex, agy y Claude) propusieron a ciegas
dónde va cada cosa y coincidieron en todo salvo en una carpeta:

- Las **decisiones** están en [`docs/decisiones/`](docs/decisiones/README.md), con índice, y un test
  falla si el código o la documentación citan una `DECISION-NNN` que no existe.
- Las **guías** (`docs/03-escribir-una-medida.md`, `docs/tutorial-practico.md`) y el **contrato del
  MCP** (`docs/mcp-contrato.md`) están en `docs/`.
- Los **planes, estudios y postmortems** están en [`vault-kb/`](vault-kb/README.md), una wiki de
  Obsidian.
- Los relevos y el compendio para NotebookLM se borraron: el tracker es el relevo y el compendio se
  genera.
- `oracle mutar` mandaba a leer «DECISION-011», un archivo que el paquete instalado no trae; ahora da
  la URL.

Los enlaces de la página de PyPI de versiones anteriores a lo que se movió dan 404: GitHub no
redirige un archivo movido.

## La web

[segtem.github.io/oracle](https://segtem.github.io/oracle/) muestra lo que Oracle es hoy: la
anti-junta, las cotas de sombra, el MCP medido en tres clientes, el tracker como relevo, `oracle test`
honesto, el primer valor, Jev con sus límites y la aritmética infija. Cada salida de terminal de la
página es de una corrida guardada en la tarea `web-028`.

## Verificación

- Suite completa en verde (2440 tests); `oracle test` VERDE con 1010/1010 mutantes de medida; cifras
  al día ([log](tareas/20260924-154951-corte-030/verificacion/oracle-test.log)).
- Mutación de código de lo tocado desde 0.29.0, en rondas paralelas bajo un techo de systemd de
  12 GB, sin vivos: `nucleo/sintaxis.py` 1177/1177, `tools/cli.py` 595/595,
  `tools/metamorficas.py` 242/242, `tools/sintaxis.py` 99/99, `tools/manual.py` 84/84 y
  `nucleo/vocabulario.py` 1/1 ([logs](tareas/20260924-154951-corte-030/verificacion/)).
- `tools/estudio.py`, `tools/mutar.py` y `tools/mcp_contrato.py` cambiaron sus rutas y **no se
  mutaron**: están fuera del perfil de mutación de código. Los cubre la suite, con un test nuevo que
  falla si se cita una decisión que no existe.

## Cómo se hizo

Codex (gpt-6-sol) implementó la aritmética, la mudanza del repositorio y la web. Codex, agy y Claude
investigaron a ciegas el orden del repositorio. Claude encontró que `t1.turno-1` se leía como un
campo y lo devolvió a Codex, revisó cada entrega y cortó.

# 0.29.0 — un modelo como sensor de la prosa, y un lenguaje que avisa mejor

```
VERSION_DISTRIBUCION   0.28.0 → 0.29.0   el patrón del sensor de prosa, ergonomía y un MCP medido
VERSION_ALGEBRA        0.8    → 0.8
VERSION_SINTAXIS       0.6    → 0.6
```

## Un modelo como sensor, nunca como juez

Hay reglas de un catálogo que viven en prosa: si un `alcance` dice de verdad qué no mira, o si un
`porque` defiende el número. Ninguna medida determinista puede leer eso. El patrón nuevo deja que un
modelo lo lea **como sensor**: emite hechos (`afirmacion_prosa`: qué texto, qué pregunta, qué
respondió, con qué probabilidad) y Oracle los juzga como cualquier otro hecho. Oracle no llama a
ningún modelo ni abre la red: el sensor es un programa del proyecto, opcional, que se corre aparte.

- **`oracle plantilla sensor-prosa <destino>`** copia el patrón a un directorio nuevo: la relación, una
  medida de ejemplo, un corpus de 15 casos y `sensor_prosa.py`, que usa sólo la biblioteca estándar y
  recibe el proveedor, el modelo y la variable de la clave como parámetros. Se prueba entero sin red
  ni clave. Explicado en `docs/14-sensor-prosa.md`.
- **Lo medido con Jev (TypeSafe AI) y dónde no alcanza.** Separa bien la prosa real de la vacía
  (10/10 controles) y coincidió 15/15 con un juez ciego en si el `porque` defiende el número. En los
  pilotos de Jam y LyraGASP, con criterios más finos, el acuerdo bajó (síntoma 9/15, con el modelo
  indulgente en los nueve desacuerdos). Por eso lo que cae en la zona media (0,4–0,6) no se decide:
  va a `revision-humana.json` y el sensor sale con código 2.

## El lenguaje avisa mejor

- **`requiere` fuera de lugar dice dónde va**: después de `umbral`, antes de `ambito` o `alcance`.
- **`caso generar` sin `--confiar-escalares`** explica por qué no ejecutó el `escalares.py` del
  proyecto en vez de terminar en un traceback; el README trae un wrapper `oracle-local` para un
  proyecto cuyo `escalares.py` ya se revisó.
- **Una captura del sensor se vuelve un caso observado** con la receta de `ejemplo/caso-observado/`:
  metadatos explícitos, evidencia copiada sin transcribir, sin verbo nuevo.
- **Dos relaciones con el mismo nombre** son un `PROYECTO INVÁLIDO` con instrucciones (salida 2), no
  un traceback.
- **`oracle init --help`** muestra la ayuda. Antes creaba un proyecto en una carpeta llamada `--help`;
  lo mismo en los demás verbos que reciben una ruta.

## El MCP, medido en tres clientes

`oracle_tareas listar` ya no devuelve los cuerpos (−87 %) y las descripciones son más cortas. El
contrato de `docs/mcp-contrato.md` se genera desde el código (`tools/mcp_contrato.py --check`).
Qué ve el modelo en cada cliente, medido con marcas aleatorias en cada parte de la respuesta:
ninguno recibe `outputSchema`; Claude Code ve sólo `structuredContent`, agy sólo el texto y Codex los
dos. Por eso se conservan las dos copias: quitar cualquiera deja ciego a un cliente.

## La especificación, leída por un tercer autor

Codex escribió una implementación del álgebra 0.8 desde cero, aislado, con la especificación y sin
ver la referencia. El contraste encontró tres preguntas que el texto no contestaba y que ahora
contesta con lo que el núcleo ya hacía: `ambito` va después de `requiere` y antes de `alcance`;
`y`/`o` aceptan dos o más operandos; `min`/`max` aceptan booleanos homogéneos, con `false < true`.
La tercera escondía un defecto de la **referencia** del diferencial, que rechazaba esos booleanos
aunque el núcleo los aceptaba; está corregido. Ninguna versión sube: el lenguaje no cambió, se
escribió. Detalle en `vault-kb/estudios/0.26.0-codex/entrega-2026-09-24/`.

## Mantenimiento

- **Nueve duplicaciones borradas** (132 líneas en `tools/mcp.py` y `nucleo/caso.py`), comprobadas
  por AST antes de tocarlas, con el anuncio del MCP idéntico por bytes y sin mutantes vivos antes ni
  después.
- **`oracle test --todo`** le da a la línea base de la mutación 240 s (medida en 164 s) y conserva 60 s
  por mutante: antes la base se cortaba con el mismo plazo que un mutante.

## Verificación

- Suite completa en verde (2432 tests); `oracle test` VERDE con 1010/1010 mutantes de medida; cifras
  al día ([log](tareas/20260924-100921-corte-029/verificacion/oracle-test.log)).
- Mutación de código de lo tocado desde 0.28.0, en rondas paralelas bajo un techo de systemd de
  12 GB, sin vivos: `nucleo/sintaxis.py` 1140/1140, `tools/cli.py` 595/595, `tools/mcp.py` 363/363,
  `perfiles/python/mutacion_codigo.py` 234/234, `nucleo/caso.py` 203/203, `nucleo/relacion.py`
  171/171, `nucleo/proyecto.py` 152/152 y `tools/juzgar.py` 107/107
  ([logs](tareas/20260924-100921-corte-029/verificacion/)). La primera ronda de `tools/cli.py` dejó
  7 vivos en la guarda de `--help` de `init-ayuda`: ningún test exigía el `0` exacto de esas ramas.
  Dos tests nuevos los matan y la ronda repetida dio 595/595.
- `tools/mcp_contrato.py`, `tools/mutar_codigo.py`, `tools/plantilla.py` y
  `tools/verificar_instalacion.py` también cambiaron pero **no se mutaron**: están fuera del perfil de
  mutación de código, que los rechaza como objetivo. Los cubre la suite.

## Cómo se hizo

Codex (gpt-6-astra y gpt-6-sol) implementó el patrón de prosa, su distribución, la ergonomía, el
refactor, el timeout y `init --help`. agy investigó Jev, inventarió las fricciones del lenguaje y
escribió la primera versión de la relación de prosa. Claude corrió el juicio a ciegas y la medición
del MCP en tres clientes, revisó cada entrega —una relación mal ubicada, un inventario con
afirmaciones falsas, ejemplos inventados— y cortó.

# 0.28.0 — retomar es leer una tarea

```
VERSION_DISTRIBUCION   0.27.0 → 0.28.0   el tracker como relevo, oracle test honesto y el tope de memoria
VERSION_ALGEBRA        0.8    → 0.8
VERSION_SINTAXIS       0.6    → 0.6
```

## El tracker es el relevo

El estado del trabajo vivía repartido entre la memoria de cada agente, `RELEVO.md`, planes y `.md`
sueltos. Ahora vive en las tareas: se retoma con `oracle tarea listar` y `oracle tarea ver <id>`, y
cada tarea termina con una sola sección `## Próximo paso`. El protocolo está en `AGENTS.md`, los
`RELEVO*.md` quedaron en un puntero, y LyraGASP y Jam tienen su propio tracker.

- **Una tarea se encuentra por su sufijo.** `oracle tarea ver multimalla` resuelve
  `20260919-140308-multimalla`; si el sufijo es ambiguo, lo dice con la lista, y si no existe, sugiere
  el más parecido («¿quisiste decir …?»). Salió de un agente que declaró inexistente una tarea que
  existía porque adivinó mal la marca de tiempo del id. El MCP lo hereda.
- **Una tarea declara con qué medidas se cierra**: `- CIERRA CON: recarga.montaje, dedos.flexion`.
  `oracle tarea hechos` lo emite como `tarea_cierre_medida`, y la política
  `seguimiento.toda_tarea_cerrada_cumple_medidas_de_cierre` pone rojo una tarea CERRADA cuyas medidas
  no existen o no están verdes en la aceptación (`aceptacion_medida`, que emite
  `ejemplo/seguimiento-tareas/cierre_medidas.py`). Sin `CIERRA CON`, una tarea sigue siendo válida.

## `oracle test` dice lo que no midió

El postmortem de una batalla naval hecha por un agente con Oracle encontró un verde que no medía
nada del juego: el catálogo estaba vacío y el verde validaba un caso por su sintaxis. Ahora:

- Cada corrida termina con `ALCANCE` (medidas contra casos guardados) y `PRODUCTO` (sin nueva
  medición: no reejecuta el producto ni certifica su estado actual).
- Un proyecto sin medidas propias, sin casos ni fixtures sale `VEREDICTO: SIN MEDICIÓN` —con salida
  0, para no romper un CI recién creado— en vez de VERDE.
- **Un camino corto a la primera medida real** (`docs/13-primer-valor.md`, `ejemplo/primer-valor/`):
  del producto a un hecho exportado, a una medida y a `oracle juzgar`, probado de punta a punta.

## Memoria de la mutación

Cuatro rondas en paralelo podían sumar 16 GB: el tope por mutante era 4000 MiB por proceso, trece
veces lo que la suite necesita. La línea base completa midió **742,51 MiB de memoria virtual
máxima**; el tope baja a **1024 MiB** (37,9 % de margen), en un solo lugar —estaba duplicado entre
el perfil y el CLI—, y
`docs/mutacion-memoria.md` dice cuántas rondas lanzar según la memoria disponible y cómo ponerlas
bajo un techo común de systemd. Las rondas de este corte corrieron así.

## Verificación

- Suite completa en verde (2394 tests); `oracle test` VERDE; cifras al día; `verificar_instalacion` WHEEL OK.
- Mutación de código de lo tocado, en cinco rondas paralelas bajo un techo de systemd de 12 GB y con el
  tope nuevo de 1024 MiB, sin cortes de memoria: `tools/cli.py` 539/539, `tools/tareas_hechos.py`
  271/271, `perfiles/python/mutacion_codigo.py` 232/232 y `tools/tareas.py` 392 de 393 —el vivo era
  el borde exacto del umbral de similitud de las sugerencias; un test con similitud 0,6 lo mata—
  ([logs](tareas/20260922-114811-corte-028/verificacion/)).
- El ejemplo del tracker (`ejemplo/seguimiento-tareas`) con la política nueva: VERDE, 33 casos,
  109/109 mutantes de medida.

## Cómo se hizo

Codex (gpt-6-astra) implementó `buscar-sufijo`, `test-alcance`, `cierre-medidas` y `memoria`, y
verificó `primer-valor`, que escribió agy. agy diseñó `cierre-medidas`. Claude revisó cada entrega
—corrigió la sintaxis del diseño, la salida documentada del recorrido y un paso que faltaba—, unió y
cortó.

# 0.27.0 — una sombra perdona hasta su cota, y el MCP se pone al día

```
VERSION_DISTRIBUCION   0.26.0 → 0.27.0   juzgar honesto, historia superficial y el MCP
VERSION_ALGEBRA        0.8    → 0.8
VERSION_SINTAXIS       0.6    → 0.6
```

## `oracle juzgar` y `Motor`

- **La sombra perdona hasta su cota.** Hasta acá la cota sólo la hacía cumplir una meta-medida de
  `oracle test`; `oracle juzgar` perdonaba igual un 4 que un 30. Ahora, por encima de la cota —o sin
  un número que comparar— el rojo vuelve, marcado `SUPERA SU COTA N`, y `--json` trae
  `supera_su_cota`. Lo encontró el CI de 0.25.2, que contó 30 donde la cota decía 4 y salió verde en
  ese punto.
- **Lo que no se aplicó, se nombra.** Una medida del catálogo propio cuya relación no vino en la
  evidencia no se evalúa y no cuenta en el veredicto, pero ahora aparece en `NO SE APLICARON`, con la
  relación que le faltó, y en `no_aplicadas` del `--json`. Antes el veredicto decía «1 de 3» y la
  cuarta no existía. Las heredadas no se listan: juzgan el catálogo, no la evidencia. Lo encontró la
  guía de la batalla naval.
- `Motor.evaluar` hace las dos cosas, con el mismo `Informe`.

⚠ Un proyecto con una sombra por encima de su cota pasa de verde a rojo en `oracle juzgar` y en
`Motor`. Es el cambio buscado.

## El tracker

`oracle tarea hechos --git` sobre un clon superficial declara la omisión (`.git`) y deja la lectura
incompleta, en vez de contar commits de menos en silencio. Probado sobre un clon de profundidad 1 de
este repositorio: la lectura sale roja y la política de cierres, 31 contra una cota de 4.

## El MCP

`oracle-mcp` no cambiaba desde 0.7.0. Ahora:

- **`oracle_evaluar`** (esquema `v2`) trae `sombra`: `null`, o `desde`, `porque`, `cota` y `perdona`,
  que es la misma pregunta que decide `ok` en `oracle juzgar`.
- **`oracle_juzgar`**, nueva: una evidencia contra el catálogo efectivo, con sombras, cotas y las no
  aplicadas. Comparte `juzgar_evidencia` con el CLI.
- **`oracle_tareas`**, nueva: `listar`, `ver`, `buscar` y `hechos` del tracker. Un proyecto sin
  `tareas/` es `TRACKER_AUSENTE`, no una lista vacía.

Las cinco siguen siendo de sólo lectura, y el contrato (`docs/mcp-contrato.md`) dice por qué:
los falsos verdes de un agente ocurren al leer, y en el tracker crear o cerrar una tarea sólo vale
junto con su commit.

## Verificación

- Suite completa en verde (2364 tests); `oracle test` VERDE: corpus 212 casos, aceptación ✓ con 120
  defectos en rojo y 85 verdes correctos, diferencial ✓, mutación de medidas 1010/1010; sintaxis y
  cifras al día; `verificar_instalacion` WHEEL OK.
- Mutación de código de lo tocado, sin sobrevivientes: `tools/juzgar.py` 107/107,
  `tools/tareas.py` 384/384, `tools/tareas_contexto.py` 212/212, `tools/tareas_git.py` 53/53,
  `tools/tareas_hechos.py` 271/271, `nucleo/medida.py` 340/340, `nucleo/proyecto.py` 152/152,
  `oracle_metalenguaje/motor.py` 27/27. `tools/mcp.py` dio 373 de 385 en la ronda completa; los 12
  vivos —y 6 más de los otros módulos— eran valores por omisión que nadie usaba, una rama muerta y
  bordes sin test (uno de seguridad: nada fijaba que `oracle_juzgar` no confiara en `escalares.py`
  por omisión). Después de cerrarlos, el código nuevo del MCP da 69/69 en ronda parcial
  ([logs](vault-kb/estudios/0.27.0-mcp/verificacion/)).
- Consumidores con un wheel de 0.27.0 antes de publicarlo: LyraGASP y Jam VERDE con las mismas
  cifras que en 0.26.0. Sus tres sombras son medidas `meta` dentro de su cota, así que `Motor` —que
  los dos usan— no les cambia el color.
- El CI de 0.26.0 quedó rojo por las cifras del README, regeneradas antes de los dos últimos cambios
  de ese corte; el código era el mismo. Acá se regeneran al final.

## Cómo se hizo

Claude hizo `juzgar`, `Motor` y el tracker. El MCP lo implementó agy
(`vault-kb/estudios/0.27.0-mcp/`); Claude escribió 24 tests de revisión antes de leer la entrega. La entrega
armaba mal el `Informe` de la sombra —toda evaluación de una medida en sombra fallaba— y la
refactorización de `juzgar` convertía un error de evaluación en «sin medidas aplicables»; un test que
ya existía lo atrapó. Las dos cosas se corrigieron, junto con siete tests de la entrega que tenían
fixtures equivocadas.

# 0.26.0 — el álgebra puede decir «ninguna»

```
VERSION_DISTRIBUCION   0.25.2 → 0.26.0   la anti-junta, y lo que la acompaña
VERSION_ALGEBRA        0.7    → 0.8      un paso nuevo: sin
VERSION_SINTAXIS       0.5    → 0.6      una cláusula nueva: sin … donde …
```

## `sin`

El álgebra sabía decir «hay una fila de B que corresponde a esta de A» (`unir` + `donde`) y no sabía
decir lo contrario. Cinco medidas lo necesitaban y lo resolvían con un conteo calculado en Python,
fuera del alcance del diferencial, de la mutación de medidas y del propio catálogo. Ahora es un paso:

```
medida seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre:
    de tarea_seguimiento t
    donde t.estado_declarado == "CERRADA"
    sin commit_seguimiento c donde c.tarea_nombrada == t.id y c.es_cierre == true
    resumen contar(1)
    …
```

Deja pasar cada fila para la que **ninguna** fila de la relación cumple la condición, y la deja tal
como llegó: el alias nuevo sólo existe dentro de la condición. Los bordes, en §3:

- relación vacía → pasan todas; relación **ausente** → el mismo error que `de`, aunque no llegue
  ninguna fila;
- sin cortocircuito: la condición se evalúa contra todas las filas, y un error en cualquiera es un
  error de la medida;
- alias repetido → error al validar la medida, no al ver los datos;
- presupuesto: el mismo límite de producto cartesiano que `unir`;
- después de `agrupar` la condición lee las columnas con `col`.

Lo acompañan `meta.sin_nunca_agrega_filas` sobre la traza (con sus dos casos, 507 y 508), el mutador
propio `quitar_antijunta` (los mutadores pasan de 29 a 30) y la entrada en el vocabulario y el manual.

## La prueba de valor

`seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre` se reescribió con `sin`, y el emisor del
tracker **dejó de emitir** `commits_de_cierre` y `commits_que_la_nombran` en `tarea_seguimiento`.
Sobre la historia real da lo mismo que daba el conteo: **4**, las mismas cuatro tareas, dentro de su
sombra. Las otras cuatro medidas con conteos del sensor quedan como tarea aparte.

⚠ Quien leía esos dos campos de `oracle tarea hechos` tiene que cruzar con `commit_seguimiento`.

## La referencia, re-derivada

agy, en un proyecto nuevo y confinado a un directorio fuera del repositorio, llevó
`diferencial/referencia/` a 0.8 leyendo sólo la especificación, sin que se le dijera qué había
cambiado. Sus 41 tests pasan sin tocar su código. El fixture del diferencial suma un mundo y tres
medidas que pasan por `sin` —directa, después de `agrupar` y con una condición que levanta detrás de
una fila que corresponde—: **10 mundos × 8 medidas, en acuerdo**.

Las sondas a sus nueve decisiones nuevas dieron cuatro desacuerdos:

- el núcleo aceptaba un `unir` a la derecha de `sin`, y §3 no: **se corrigió el núcleo**;
- un alias repetido cuando no llega ninguna fila, y un alias igual a una columna de `agrupar`: la
  especificación no decidía; **§3 ahora decide**, como el núcleo;
- un predicado que no da booleano: el núcleo lo toma por su verdad y la referencia levanta. Es
  anterior a 0.8 y pasa igual con `donde`: tarea `20260916-202010-predicado-bool`.

## Lo demás

- **`oracle test` ya no termina con un traceback** cuando una medida no puede evaluar su propio caso
  (un campo mal escrito, por ejemplo): la mutación saltea ese caso y la aceptación lo sigue
  informando. Lo encontró la guía de la batalla naval, recorrida de punta a punta con 0.25.2.
- **El alcance derivado cuenta la relación de un `sin`**: `oracle revisar` y `oracle_evaluar` del
  MCP decían qué campos NO lee la medida sin nombrar la relación de la anti-junta.
- **CI juzga el tracker con la historia entera** (`fetch-depth: 0`): con el clon superficial la
  política de cierres contaba 30 en vez de 4.
- **El estudio de Codex apunta a 0.8.**
- Tareas nuevas, de lo que salió en el camino: `superficial` (el tracker no avisa si la historia es
  superficial), `cota-juzgar` (`juzgar` perdona una sombra por encima de su cota),
  `juzgar-omite` (`juzgar` no nombra las medidas cuya relación no vino) y `predicado-bool`.

## Verificación

- Suite completa en verde (2302 tests); `oracle test` VERDE: corpus 212 casos, aceptación ✓ con 120
  defectos en rojo y 85 verdes correctos, diferencial ✓ (10 mundos × 8 medidas), mutación de medidas
  1010/1010; sintaxis y cifras al día; `verificar_instalacion` WHEEL OK.
- Mutación de código de lo tocado, sin sobrevivientes: `nucleo/sintaxis.py` 1138/1138,
  `nucleo/algebra.py` 426/426, `nucleo/medida.py` 326/326, `nucleo/unidad.py` 207/207,
  `nucleo/mutacion.py` 190/190, `nucleo/campo_leido.py` 28/28, `tools/tareas_hechos.py` 270/270,
  `tools/medida.py` 302/302. La primera ronda dejó 31 vivos, casi todos guardas redundantes que la
  entrega agregó sobre datos ya validados y bordes sin test; los dos últimos se cerraron con rondas
  parciales sobre su sitio ([logs](vault-kb/estudios/0.26.0-antijunta/verificacion/)).
- La política de cierres del tracker, escrita con `sin`, da 4 sobre la historia real, como el
  conteo en Python que reemplaza.
- Consumidores con un wheel de 0.26.0 antes de publicarlo: LyraGASP VERDE (66 medidas, 190 casos,
  76/114, diferencial 580, 466/466) y Jam VERDE (83 medidas, 31 casos, 28/3, diferencial 1099,
  428/428), iguales a 0.25.1.

## Cómo se hizo

agy implementó `sin` en el núcleo, la superficie, la traza y la reescritura del tracker; Claude
escribió 17 tests de revisión antes de leer la entrega (pasaron sin cambios), corrigió dos tests de
la entrega que usaban una API que no existe, movió el mutador —agy lo había dejado en la carpeta de
los de otros autores, donde nadie lo cargaba— y escribió §3, el corpus, los mundos y el corte. La
referencia la re-derivó otra instancia de agy, aislada.

# 0.25.2 — el verificador del diferencial, fijado; y los dos consumidores en verde

```
VERSION_DISTRIBUCION   0.25.1 → 0.25.2   el informe del diferencial fijado y medido en CI
VERSION_ALGEBRA        0.7    → 0.7
VERSION_SINTAXIS       0.5    → 0.5
```

## El que comprueba el acuerdo, comprobado

`tools/diferencial.py` es quien dice si Oracle y la implementación independiente coinciden. Declarado
custodia en 0.24.0, dio **57 mutantes y 32 sobrevivientes**, todos en lo que imprime y en con qué
código sale: la marca ✓/✗, las cuentas, cuántas fallas lista y los `return`. Un informe que dice ✓
con un desacuerdo, o sale 0 con fallas, es el falso verde que el diferencial existe para evitar,
contado por su propio verificador.

- `tests/test_diferencial_informe.py` fija cada rama del informe —estructura, sin fixtures, fixtures
  ilegibles y vencidos, acuerdo y desacuerdo en escenarios y en grupos, los topes de 5 y de 20— y
  los tres códigos de `main`.
- El `if __name__` pasa al patrón `_entrada_directa` y `sys.path` se arma sin constante: eran el error
  de arnés y un sobreviviente más.
- Ronda después: **55/55**, en tres minutos. Sale de `CUSTODIAS_SIN_MEDIR` y **entra a la matriz de
  mutación de CI**.

## Lo demás

- **La crónica de `ESPECIFICACION.md` §0 va en un solo orden**, del corte más nuevo al más viejo.
  Tenía tres a la vez. Se movieron sólo bloques enteros, y un test falla si se vuelve a mezclar.
- **El estudio de Codex** (`vault-kb/estudios/0.26.0-codex/`): el contrato de aislamiento, versionado; un
  lanzador que arma un directorio fuera del repositorio sólo con la especificación y frena si Codex
  no tiene cuota; y un contraste que compara el veredicto entero de dos implementaciones sobre los
  mundos del diferencial y todo el corpus (248 comparaciones). Codex todavía no tiene cuota.

## Los dos consumidores, en verde

Subidos a 0.25.1 con el mismo resultado que en 0.24.0. Y los dos quedaron con su suite entera:

- **Jam** vuelve a **VERDE** por primera vez en semanas. Su rojo —`vault.json` vencido, que figuraba
  como deuda del dominio— lo causaba una nota sin commitear en `Vault-kb/05-DSL/`, fuera de las
  reglas del propio vault. Se volvió un documento del vault sin cambiar su contenido; `oracle test`
  da VERDE (diferencial 1099 acuerdos) y su suite 1240 sin fallas.
- **LyraGASP**: su test de extracción de curvas comparaba distinguiendo mayúsculas, y Unreal no lo
  hace —su propio sensor ya lo sabía—. Su suite queda en 148 sin fallas.

## Verificación

- Suite completa en verde (2242 tests); aceptación ✓ con 119 defectos en rojo y 84 verdes correctos;
  diferencial ✓; sintaxis y cifras al día; mutación de medidas 994/994; `verificar_instalacion`
  WHEEL OK.
- Mutación de código de `tools/diferencial.py`: **55/55**
  ([log](vault-kb/estudios/0.25.2-informe/verificacion/)).
- Consumidores con 0.25.1 instalado desde PyPI: LyraGASP VERDE y su suite 148 sin fallas; Jam VERDE y
  su suite 1240 sin fallas.

## Cómo se hizo

Claude cerró `informe` y `cronica`; la nota del vault de Jam la convirtió agy
(`vault-kb/estudios/vault-jam/`) y la verificó Claude. Este corte se hizo desde un worktree limpio de `main`,
mientras agy trabaja en la anti-junta del álgebra 0.8 en el árbol principal.

# 0.25.1 — borradores de las relaciones que faltan declarar, sin fabricar un verde

```
VERSION_DISTRIBUCION   0.25.0 → 0.25.1   oracle relaciones --escribir
VERSION_ALGEBRA        0.7    → 0.7
VERSION_SINTAXIS       0.5    → 0.5
```

Los dos consumidores conocidos tapan con sombra `meta.toda_cantidad_comparada_tiene_unidad_derivable`
—60 comparaciones en LyraGASP, 54 en Jam— con la misma razón: declarar las relaciones «se hace por
relación, no de golpe». Ninguno declara una sola: no tienen carpeta `relaciones/`, y sin relaciones
declaradas no hay unidades que derivar.

**`oracle relaciones --escribir`** deja un borrador de cada relación que la evidencia trae y el
proyecto no declara, en `relaciones-por-revisar/`:

- **Escribe sólo lo que se puede saber mirando la evidencia**: el tipo de cada campo, y `sin_unidad`
  para los textos y los booleanos, que no tienen magnitud.
- **Deja vacío lo que no se puede saber**: la unidad de cada número —puede ser una cuenta,
  centímetros o segundos— y el alcance, que sólo lo sabe quien escribió el sensor.
- **No cambia lo que el proyecto carga.** El lector no mira esa carpeta. Mover un borrador a
  `relaciones/` sin completarlo hace fallar la carga con el campo que falta.
- **No pisa nada**: ni una relación ya declarada ni un borrador que ya existe. Un campo con tipos
  mezclados o con un nombre que el lector no acepta se informa y no se escribe.

La primera versión de esta herramienta declaraba directo y escribía `sin_unidad` en todo. Sobre
LyraGASP bajaba la deuda de **60 a 0**, afirmando que medidas en centímetros no tenían unidad: eso no
es pagar una deuda, es fabricar un verde, y la propia declaración de una relación dice «no hay
defaults silenciosos». Con los borradores, completar uno y moverlo baja la deuda por lo que de verdad
se decidió —en la prueba, de 60 a 58—, y el guardián de cotas avisa enseguida que la sombra del
consumidor quedó más alta que su deuda.

## Verificación

- Suite completa en verde (2223 tests); aceptación ✓ con 119 defectos en rojo y 84 verdes correctos;
  sintaxis, diferencial y cifras al día; `verificar_instalacion` WHEEL OK.
- Mutación de código ([logs](vault-kb/estudios/0.25.1-declarar/verificacion/)): `tools/medida.py` **296/296**
  y `tools/cli.py` **539/539**. La primera ronda de `tools/medida.py` dejó siete vivos, todos en el
  código nuevo: dos en la rama de evidencia ilegible, que no tenía test; uno en un contador que se
  llevaba aparte y nadie leía, que se borró; tres en cómo se escribe el borrador, que no cambiaban
  nada y se borraron; y uno que pedía un test para la carpeta ya creada.
- Probado sobre una copia de LyraGASP: 21 borradores, el proyecto cargó igual que antes (la deuda
  siguió en 60); un borrador movido sin completar hizo fallar la carga con el campo que faltaba; uno
  completado y movido bajó la deuda a 58, y `meta.ninguna_cota_mas_alta_que_su_deuda` avisó que la
  sombra quedó más alta que la deuda.

## Cómo se hizo

Tarea `20260916-035758-declarar`, que salió del estudio de las tres sombras que los dos consumidores
comparten (`vault-kb/estudios/TRES-MEDIDAS-QUE-TODOS-PONEN-EN-SOMBRA.md`). La escribió Claude.

# 0.25.0 — mutar unos sitios sin poder confundirlo con una verificación completa

```
VERSION_DISTRIBUCION   0.24.0 → 0.25.0   rondas parciales declaradas, y los commits como hechos
VERSION_ALGEBRA        0.7    → 0.7
VERSION_SINTAXIS       0.5    → 0.5
```

## Rondas parciales

`--objetivo` aceptaba archivos enteros y nada más fino. Cada simplificación de unas pocas líneas
obligaba a relanzar la ronda completa del archivo —una hora en los grandes— o a aplicar el mutante a
mano sobre una copia, que no queda registrado como ronda. En el corte 0.21.0 pasó tres veces; la
noche del 15 al 16 de septiembre, cuatro más.

- **`--lineas a-b` y `--sitio <id>`**, repetibles y combinables. Un filtro que no selecciona ningún
  sitio es un error con código 2, no una ronda vacía en verde.
- **La ronda se declara parcial** en la primera línea del informe, en el resumen, en la evidencia
  (`parcial`, y `total_sitios` con el denominador real, calculado antes de filtrar) y en el código de
  salida: **2**, el de ronda inconclusa. Con 0, quien mire sólo `$?` no podría distinguirla de una
  verificación completa.
- **`proceso.ronda_mutacion_concluyente` la rechaza**: una ronda parcial no demuestra que los tests
  fijen el módulo, por más que no sobreviva nadie.
- El filtro también entra en la identidad de la ronda, así que reanudar un manifiesto no mezcla una
  parcial con una completa.

## Los commits, como hechos del tracker

`oracle tarea hechos --git` emite `commit_seguimiento`: una fila por commit alcanzable desde HEAD con
lo que su asunto declara —si nombra una tarea, cuál, si existe, en qué estado está y si el resumen es
exactamente `done`—. Sin repositorio la relación viene vacía y no se inventa nada.

Con eso, el proyecto de ejemplo gana tres políticas escritas en el lenguaje: ningún commit nombra una
tarea inexistente, toda tarea cerrada tiene su commit de cierre, y ningún `done` deja la tarea
abierta. El catálogo distribuido no cambia.

**El límite que la tarea quería medir:** el álgebra **no tiene anti-junta**. «Una tarea que ningún
commit nombra» no se puede escribir uniendo dos relaciones, así que el tracker cuenta
(`commits_que_la_nombran`, `commits_de_cierre`) y la medida compara contra cero. Es la división de
siempre —el sensor observa, el lenguaje juzga—, pero acá no fue una elección.

Sobre la historia real de Oracle: 459 commits, 87 nombran tarea, **ninguno** nombra una inexistente y
4 tareas cerradas no tienen su `done` —tres anteriores a la convención y una con la firma pegada en
el asunto—. Queda declarado con sombra y cota 4.

## Verificación

- Suite completa en verde (2206 tests); aceptación ✓ con 119 defectos en rojo y 84 verdes correctos;
  corpus 210 casos; diferencial ✓ (9 mundos × 5 medidas); sintaxis y cifras al día;
  `verificar_instalacion` WHEEL OK.
- Mutación de medidas: 994/994. Mutación de código de `perfiles/python/mutacion_codigo.py`:
  **232/232**. La primera ronda dio 231 de 233; los dos vivos estaban en cómo se guarda que una ronda
  fue parcial, y se cerraron antes de esta ([logs](vault-kb/estudios/0.25.0-sitios/verificacion/)).
- Rondas parciales corridas de verdad sobre `nucleo/version.py` (15 sitios): `--lineas 43-56` mutó 3
  y salió 2; `--sitio nucleo/version.py:51:8:retorno` mutó 1 y salió 2; la ronda completa, 15/15 y
  salió 0; un filtro sin sitios salió 2 con su mensaje.
- `tools/mutar_codigo.py` cambió y no es objetivo del arnés («fuera del perfil activo»); lo fijan sus
  tests.
- Los dos consumidores no emiten `corrida_mutacion`, así que el campo nuevo no les pide nada.
- Del corte anterior: la ronda completa de `tools/tareas.py` terminó en **388/389**; el único vivo es
  el borde del sufijo que ya tenía su test en 0.24.0.

## Cómo se hizo

Las rondas parciales las implementó agy (tarea `20260915-201030-sitios`; encargo, avance e informe en
`vault-kb/estudios/0.25.0-sitios/`), y Claude revisó, corrigió y midió: el detalle está en
[REVISION-CLAUDE.md](vault-kb/estudios/0.25.0-sitios/REVISION-CLAUDE.md). Los commits como hechos
(`20260915-010452-commits`) los escribió Claude.

# 0.24.0 — ningún mutante se come la máquina, y el tracker se lee de un vistazo

```
VERSION_DISTRIBUCION   0.23.1 → 0.24.0   tope de memoria en el arnés, y seis deudas cerradas
VERSION_ALGEBRA        0.7    → 0.7
VERSION_SINTAXIS       0.5    → 0.5
```

## El tope de memoria

`tools/mutar_codigo.py` limitaba el tiempo y la salida de cada mutante, pero no su memoria. Medido el
2026-09-15 mutando `tools/tareas_consulta.py`: el mutante `not in` → `in` de la línea 65 deja a
`tokenizar` sin avanzar y agrega tokens sin fin; hasta el timeout de 300 s se come la RAM de la
máquina, y el sistema mató la ronda dos veces arrastrando procesos ajenos. Desde entonces cada ronda
se corría con `ulimit -v` puesto a mano desde afuera, que no estaba escrito en ninguna parte.

- **`--limite-memoria-mb`**, 4000 por omisión, `0` desactiva. El tope se aplica en el proceso hijo
  con `resource.setrlimit(RLIMIT_AS)`; el arnés no toca el suyo.
- **Un mutante que excede el tope está muerto**: sale con `MemoryError`, que es un fallo de tests. No
  es un timeout ni un error de arnés, así que la ronda sigue siendo concluyente.
- **La línea base corre con el mismo tope**, para que un tope demasiado bajo se vea antes de mutar.
- **El tope se recorta al máximo heredado.** Pedir más de lo que dejó un `ulimit -v` de afuera hacía
  fallar `setrlimit` adentro del hijo, y la ronda entera moría con «Exception occurred in
  preexec_fn», que no dice nada. Lo encontró la primera ronda real.
- El tope viaja en la identidad de la ronda: dos rondas con topes distintos no son la misma ronda al
  reanudar.

## Lo demás que cierra el corte

- **El tracker se lee de un vistazo.** Sin `--sufijo`, el ID derivaba del título hasta 40 caracteres
  —y el ID entero es el prefijo de cada commit de esa tarea—. Ahora son 16, cortados en una palabra
  entera. Y CI tiene un workflow propio del tracker: `verificar.yml` ignora `**.md` y un `TAREA.md`
  es un `.md`, así que un push que sólo tocaba `tareas/` no disparaba nada.
- **El sitio dice la verdad.** La portada publicaba «oracle 0.8.0 · 41 medidas · 131 casos» ocho
  cortes después, escrito a mano. Las tres cifras salen ahora de `tools/cifras.py`, que corre en CI,
  y el tracker tiene su sección: qué es, la forma tatr, el lenguaje de consultas y la guía.
- **§0 abre diciendo en qué versiones está el lenguaje**, con un test que lo compara contra
  `nucleo/version.py`. Había que deducirlo del último párrafo de una crónica de veinte cortes.
- **`oracle juzgar` deja de repetir la regla de la sombra**, que `Informe` sabe desde 0.20.0.
- **Los fixtures de dominio guardan el veredicto entero** (`ok`, valor y si levantó), como el
  diferencial de Oracle desde 0.23.1. Los ya emitidos siguen valiendo.
- **El equivalente declarado en 0.19.0 se borró**, que es la regla escrita del proyecto: un
  equivalente genuino se saca, no se anota.

## Verificación

- Suite completa en verde (2182 tests); aceptación ✓ con 118 defectos en rojo y 83 verdes correctos;
  diferencial ✓ (9 mundos × 5 medidas); sintaxis y cifras al día; `verificar_instalacion` WHEEL OK.
- Mutación de medidas: 984/984. Mutación de código, una ronda por objetivo en copias aisladas y **sin
  `ulimit` de afuera**, que es como se prueba el tope nuevo ([logs](vault-kb/estudios/0.24.0-memoria/verificacion/)):

  | objetivo | murieron |
  |---|--:|
  | `nucleo/medida.py` | 313/313 |
  | `perfiles/python/mutacion_codigo.py` | 227/227 |
  | `nucleo/fixtures.py` | 205/205 |
  | `tools/juzgar.py` | 105/105 |
  | `tools/tareas_consulta.py` | 99/99 |
  | `tools/cifras.py` | 58/58 |
  | `nucleo/dominio.py` | 19/19 |
  | `nucleo/version.py` | 15/15 |

  La ronda de `tools/tareas.py` —la más grande del repositorio— seguía corriendo al cortar: hasta ese
  punto llevaba **un solo vivo**, el borde exacto del sufijo nuevo (un slug de 16 caracteres), que ya
  tiene su test y se verificó aplicando el mutante a mano. Su número completo va en el próximo corte.
- `tools/diferencial.py` se declara custodia con su número medido (57 mutantes, 24 muertos, 32
  sobrevivientes, 1 error de arnés) y queda en `CUSTODIAS_SIN_MEDIR` con la tarea que lo cierra: la
  deuda es previa y entrar hoy a la matriz pondría el CI en rojo por tests que faltan desde antes.
- Los dos consumidores, con el Oracle 0.17.0 que corren hoy: LyraGASP `oracle test` VERDE; Jam sigue
  en su ROJO previo por `vault.json`. Las seis sombras que declaran quedaron con cota.

## Cómo se hizo

El tope de memoria lo implementó agy (tarea `20260915-112728-memoria`, encargo y entrega en
`vault-kb/estudios/0.24.0-memoria/`); Claude revisó, corrigió lo que no corría y lo midió: el detalle está en
[REVISION-CLAUDE.md](vault-kb/estudios/0.24.0-memoria/REVISION-CLAUDE.md). Las otras seis tareas salieron del
tracker por prioridad.

# 0.23.1 — el diferencial ejercita lo que el álgebra agregó, y compara el veredicto entero

```
VERSION_DISTRIBUCION   0.23.0 → 0.23.1   fixtures que guardan el veredicto, no sólo el ok
VERSION_ALGEBRA        0.7    → 0.7
VERSION_SINTAXIS       0.5    → 0.5
```

El álgebra `0.7` agregó `requiere` con condición y relaciones con variantes, y la implementación de
referencia se re-derivó contra esa versión. Pero los cuatro mundos del diferencial no usaban nada de
eso: el fixture decía «de acuerdo» sin que la referencia pasara una sola vez por lo nuevo. Es el
agujero que documenta `b250e6c`: cada extensión del lenguaje apaga un pedazo del diferencial si nadie
agrega mundos.

- **Cinco mundos nuevos**, con evidencia de `mutante` mezclando sus dos variantes: filas que cumplen
  la condición de `requiere`, ninguna que la cumpla, la relación vacía, y —el que importa— una
  variante sin el campo que la condición lee, detrás de una fila que sí lo tiene. Si alguna de las
  dos implementaciones cortocircuitara al primer acierto, una levantaría y la otra no. Ninguna lo
  hace: es la decisión que 0.21.0 tomó leyendo, y ahora está contrastada.
- **El fixture compara el veredicto entero**: `ok`, el `valor` con que salió y si la evaluación
  levantó. Un rojo, un SIN EVIDENCIA y un error se veían iguales en un booleano, y pasar de uno a
  otro no se detectaba.
- **Un fixture puede traer escritas sus medidas** (`medidas_declaradas`), para contrastar formas del
  álgebra que ninguna medida publicada usa. Las dos del contraste no entran al catálogo y no obligan
  a nadie.

Las dos formas del veredicto conviven a propósito: la corta es lo único que afirmaron los fixtures
anteriores —y los que siguen emitiendo los consumidores—, así que reclamarles la larga los habría
invalidado a todos sin que nada hubiera cambiado.

## Verificación

- Suite completa en verde (2163 tests); aceptación ✓ con 118 defectos en rojo y 83 verdes correctos;
  `verificar_instalacion` WHEEL OK; sintaxis y cifras al día.
- Diferencial: 9 mundos × 5 medidas, referencia y Oracle de acuerdo en el `ok`, en el valor y en
  cuándo levantar. Mutación de medidas: 984/984.
- Mutación de código de `nucleo/fixtures.py`: 205 mutantes, 203 muertos en la primera ronda. De los
  dos vivos, uno era un `return False` que un `assertFalse` no distingue de `None` —ahora lo fija un
  `assertIs`— y el otro un valor de recuperación que nadie miraba, que se borró. Los dos verificados
  a mano aplicando el mutante.
- `tools/diferencial.py` cambió y **no** es objetivo del arnés: no está en `HERRAMIENTAS_CUSTODIAS`
  ni declarado en `CUSTODIAS_SIN_MEDIR`. Lo fijan sus tests; queda la tarea
  `20260916-014457-custodia` para decidir si entra.

## Cómo se hizo

Tarea `20260915-201030-diferencial`. El dueño decidió que las medidas del contraste vivan junto a los
mundos y no en el catálogo distribuido, y que el fixture compare el veredicto entero. El contraste no
encontró ningún desacuerdo: en los nueve mundos, las dos implementaciones coinciden en el `ok`, en el
valor y en cuándo levantar. Queda abierta la tarea `20260916-014153-veredictos`: los fixtures de los
consumidores siguen guardando sólo el `ok`.

# 0.23.0 — declarar el ámbito deja de ser cosa de Oracle

```
VERSION_DISTRIBUCION   0.22.0 → 0.23.0   la medida del ámbito obliga a todos
VERSION_ALGEBRA        0.7    → 0.7
VERSION_SINTAXIS       0.5    → 0.5
```

`meta.toda_medida_declara_su_ambito` se declaraba a sí misma `del_origen` desde 0.5.0. Era deliberado:
si hubiera sido universal, los consumidores se habrían puesto en rojo al instante por medidas escritas
antes de que la cláusula existiera. El propio plan de 0.5.0 avisaba que era la clase de decisión
temporal que se vuelve permanente por olvido, y que nada registraba cuándo debía terminar.

- **La medida pasa a `universal`.** Una medida sin `ambito` es un rojo en cualquier proyecto que
  seleccione el catálogo, no sólo en Oracle.
- **Los consumidores ya no tienen ninguna.** Antes del corte, las 27 medidas de LyraGASP y las 41 de
  Jam declararon su ámbito, todas `universal`: ninguna juzga la instalación de su origen, y lo propio
  de cada repo vive en el sensor, no en la medida. Los catálogos de Oracle y del ejemplo ya estaban
  en cero.
- **Nada más cambia.** `sin_declarar` se sigue leyendo y escribiendo igual; lo que cambia es a quién
  le reclama la medida que lo persigue.

Un consumidor que actualice con medidas sin `ambito` va a ver un rojo nuevo, y el remedio es
declararlo: `universal` si la regla obliga a todo proyecto que aporte esa evidencia, `del_origen` si
juzga la instalación de quien la escribió.

## Verificación

- Suite completa en verde (2146 tests); aceptación ✓ con 118 defectos en rojo y 83 verdes correctos;
  sintaxis y diferencial al día; `verificar_instalacion` WHEEL OK.
- Mutación de medidas: 984/984. No hay ronda de mutación de código: el corte no toca `nucleo/` ni
  `tools/` más allá del número de versión.
- Con este árbol, las medidas sin ámbito son cero en los cuatro catálogos medidos: Oracle (58),
  `ejemplo/seguimiento-tareas` (3), LyraGASP (27) y Jam (41).
- Los dos consumidores, con el Oracle 0.17.0 que corren hoy y su ámbito ya declarado: LyraGASP
  `oracle test` VERDE (corpus 190, aceptación 76 rojos y 114 verdes); Jam sigue en el mismo ROJO
  previo, sólo por `medidas/diferencial/vault.json`, cuyo emisor no corre por una deuda de su
  dominio. Los demás diferenciales de los dos se re-emitieron porque cambió el texto de sus
  catálogos.

## Cómo se hizo

Tarea `20260915-155111-ambito`, que existía justamente porque el plan de 0.5.0 dejó la deuda escrita.
Se midió primero: 0 medidas sin ámbito en Oracle y en el ejemplo, 27 de 27 en LyraGASP y 41 de 41 en
Jam. El dueño eligió declararlas y recién después promover la medida, en vez de anotar el paso con
fecha y cota. Cada medida se leyó para decidir su ámbito; el criterio quedó en los commits de cada
consumidor.

# 0.22.0 — toda medida lee campos que existen, y un campo ausente se informa igual en todas partes

```
VERSION_DISTRIBUCION   0.21.0 → 0.22.0   campos de las relaciones y medidas que no pudieron juzgar
VERSION_ALGEBRA        0.7    → 0.7
VERSION_SINTAXIS       0.5    → 0.5
```

Una medida se declaraba aplicable por el nombre de la relación aunque leyera un campo que la evidencia
no trae, y nada lo decía antes de evaluar. Al evaluar, cada herramienta lo trataba distinto: `mutar` y
`mutar_codigo` lo listaban aparte, `juzgar` salía 2 y la aceptación terminaba en traceback.

- **Los campos de lo que emite Oracle se conocen.** Cada emisor declara los de sus relaciones en
  `CAMPOS_DE_RELACIONES`, al lado de la relación, y un test los compara con las filas que produce. Las
  relaciones de proceso que el catálogo lee —`corrida_mutacion`, `archivo`, `modulo`, `alcanzable`,
  `importa`, `cambio`, `afirmacion`, `hallazgo`— pasan a estar declaradas en `relaciones/`.
- **`campo_leido`** tiene una fila por cada campo que lee una medida, con su relación, si esa relación
  es declarada, del lenguaje o sin declarar, y si el campo existe.
  `meta.toda_medida_lee_campos_que_existen` no admite un campo inexistente en una relación cuyos campos
  se conocen. Una relación sin declarar de un consumidor no se juzga.
- **Lo que no se pudo juzgar se informa en un solo lugar.** El álgebra sigue levantando ante un campo
  ausente —no es `False`—, pero al evaluar un conjunto de medidas el núcleo deja las que no juzgaron en
  `Informe.no_juzgaron`, con su motivo. La aceptación, `juzgar`, `mutar` y `mutar_codigo` lo leen de ahí.

Medido antes del cambio: ninguna medida de Oracle, LyraGASP ni Jam lee hoy un campo inexistente en una
relación con campos conocidos; los consumidores leen 121 campos de 39 relaciones sin declarar, que la
regla no juzga.

## Verificación

## Cómo se hizo

Tarea `20260915-155654-campos`. El dueño decidió el alcance de la regla —las relaciones declaradas y las
que emite Oracle, no las sin declarar de un consumidor— y que el álgebra siga levantando ante un campo
ausente, con una sola forma de informarlo. Implementó agy (el primer lanzamiento cortó por falta de
capacidad del servidor; el segundo entregó). Claude revisó con tests escritos antes de leer la entrega y
corrigió: los tests que acompañaban la entrega usaban una API que no existe y se reescribieron; un
envoltorio en la aceptación hacía que un caso que no se podía juzgar contara como fijado; había lectores
duplicados; y el plan dejaba sin declarar dos relaciones de proceso que el volcado real mostró leídas.

## Verificación

- Mutación de código ([logs](vault-kb/estudios/0.22.0-campos/verificacion/)): `nucleo/medida.py` 311/312,
  `nucleo/relacion.py` 169/169, `tools/juzgar.py` 113/113, `nucleo/marco.py` 78/79, `tools/aceptacion.py`
  76/78 y `nucleo/campo_leido.py` 24/24. Los dos vivos de `aceptacion.py` eran la rama por la que la
  sombra perdonaba una medida que no pudo juzgar, y se borró; los de `marco.py` y `medida.py` tienen test,
  verificado aplicando el mutante a mano. `relacion.py` (33 errores de arnés en la primera ronda, por un
  test que armaba una relación al importarse) y `campo_leido.py` (guardas redundantes, borradas) se
  repitieron después de corregir. Ningún equivalente nuevo.
- Suite completa en verde (2146 tests); `tools/aceptacion.py` ✓ con 118 defectos en rojo y 83 verdes
  correctos; los casos 504 (falso verde), 505 y el observado 506 salen como deben.
- Sobre el catálogo de Oracle, `campo_leido` emite 160 lecturas —131 de relaciones del lenguaje, 29 de
  declaradas— y todas nombran un campo que existe.
- [Plan](vault-kb/planes/PLAN-0.22.0-CAMPOS.md), [encargo](vault-kb/estudios/0.22.0-campos/ENCARGO-AGY.md),
  [revisión](vault-kb/estudios/0.22.0-campos/REVISION-CLAUDE.md) y [cierre](vault-kb/estudios/0.22.0-campos/CIERRE.md).

Álgebra y sintaxis no cambian: `campo_leido` es una relación de hechos, como `sombra` o `verbo_del_cli`.
La publicación en PyPI la realiza el dueño.

---

# 0.21.0 — `mutante` es una relación con variantes, y `requiere` puede pedir filas de una

```
VERSION_DISTRIBUCION   0.20.0 → 0.21.0   relación mutante con variantes
VERSION_ALGEBRA        0.6    → 0.7      requiere con condición, relaciones con variantes
VERSION_SINTAXIS       0.4    → 0.5      requiere <relación> <alias> donde <condición>
```

La relación `mutante` la producían dos herramientas con campos incompatibles —la mutación de medidas
y la de código—, y el catálogo de Oracle tenía dos medidas universales sobre ella. El lenguaje no
cortocircuita `y`/`o` y levanta al comparar un campo ausente, así que cada ronda de mutación terminaba
con una medida que «NO pudo juzgar» la evidencia de la otra.

- **Relaciones con variantes.** Una declaración en `relaciones/` puede decir qué campos trae cada
  clase de fila según un campo discriminante. `mutante` se declara con `tipo` y dos variantes,
  `medida` y `codigo`, y los dos productores emiten `tipo`.
- **`requiere` con condición.** `requiere mutante m donde m.tipo == "codigo"` sale `SIN EVIDENCIA` si
  no hay filas de ese tipo. No es el filtro de la medida: las 20 medidas con `requiere` que existían
  filtran violaciones con `donde`, y un `requiere` sobre las filas filtradas las habría pasado a todas
  a `SIN EVIDENCIA`. Ninguna medida existente cambia.
- **Las dos medidas de `proceso`** filtran primero por `tipo` y piden filas de su tipo. Sin la
  condición, una ronda de medidas le prestaba evidencia a la medida de código, que contaba cero y
  salía verde sobre una ronda que nunca ocurrió: casos `502` y `503`.

## Cómo se hizo

Tarea `20260915-155111-mutante`. El dueño eligió la relación común después de ver lo que costaba, y
aprobó el `requiere` con condición cuando la medición mostró que «`requiere` sobre las filas filtradas»
habría pasado a SIN EVIDENCIA las 20 medidas que ya lo usaban. Implementó agy; Claude revisó con tests
escritos antes de leer la entrega y corrigió cuatro defectos (la condición recorría el nodo `clave`, un
resultado no booleano pasaba, una validación nueva subía la MAYOR, y `tools/mutar.py` contaba un SIN
EVIDENCIA como política incumplida).

La referencia independiente del diferencial la re-derivó **agy en una conversación nueva y aislada**,
con sólo la especificación y las decisiones (Codex, el autor original, sin cuota). Encontró dos puntos
que la especificación no decidía y en los que el núcleo estaba mal: la condición de `requiere` se
evalúa en todas las filas y en todas las entradas antes de decidir, para que el orden de la bolsa no
cambie el veredicto. Se corrigió el núcleo y §2 lo dice.

## Verificación

- Mutación de código ([logs](vault-kb/estudios/0.21.0-mutante/verificacion/)): `nucleo/sintaxis.py` 1050/1050,
  `nucleo/medida.py` 311/316, `tools/medida.py` 263/263, `perfiles/python/mutacion_codigo.py` 211/211,
  `nucleo/unidad.py` 198/198, `nucleo/mutacion.py` 182/182 y `nucleo/relacion.py` 149/149. De los cinco
  vivos de `medida.py`, tres eran código redundante y se borró; los otros dos tienen test, verificado
  aplicando el mutante a mano. Ningún equivalente nuevo.
- Suite completa en verde; `tools/aceptacion.py` ✓ con los casos 502 y 503 en rojo;
  `tools/sintaxis.py --verificar` OK; `python tools/mutar.py` sale 0.
- Referencia independiente re-derivada contra 0.7 (21 tests) y diferencial regenerado: referencia y
  Oracle de acuerdo en 4 mundos × 3 medidas.
- LyraGASP y Jam cargan con el núcleo nuevo y sus medidas no cambian de veredicto.
- [Plan](vault-kb/planes/PLAN-0.21.0-MUTANTE.md), [encargo](vault-kb/estudios/0.21.0-mutante/ENCARGO-AGY.md),
  [revisión](vault-kb/estudios/0.21.0-mutante/REVISION-CLAUDE.md), [cierre](vault-kb/estudios/0.21.0-mutante/CIERRE.md) y
  [procedencia de la referencia](diferencial/referencia/PROCEDENCIA.md).

Un proyecto que declara `"algebra": "0.6"` sigue cargando. La publicación en PyPI la realiza el dueño.

---

# 0.20.0 — `Motor` juzga con el mismo catálogo y las mismas sombras que `oracle test`

```
VERSION_DISTRIBUCION   0.19.0 → 0.20.0   veredicto de la fachada Motor
VERSION_ALGEBRA        0.6    → 0.6
VERSION_SINTAXIS       0.4    → 0.4
```

LyraGASP y Jam juzgan su evidencia con la fachada pública `Motor.desde_proyecto`, y esa fachada no
juzgaba igual que `oracle test` sobre el mismo proyecto:

| proyecto | `Motor` en 0.19.0 | catálogo efectivo | sombras ignoradas |
|---|--:|--:|--:|
| LyraGASP `medidas/` | 84 | 64 | 3 |
| Jam `medidas/` | 101 | 81 | 3 |

- **Catálogo.** Cargaba con `catalogos_a_cargar`: con `catalogo_base`, las 20 medidas `del_origen`
  de Oracle —reglas sobre el propio Oracle— también juzgaban al consumidor. Ahora carga
  `catalogo_efectivo`, la selección de `oracle test` y `oracle juzgar`.
- **Sombra.** Ignoraba la `sombra` de `oracle.json`: una medida heredada en sombra y en rojo ponía
  `informe.ok` en falso. `Informe` suma `en_sombra`: la medida se sigue midiendo y se marca
  `[EN SOMBRA]`, su rojo no tumba `ok`, el veredicto dice cuántos perdonó y `a_json()` agrega
  `en_sombra` por medida.

Los consumidores no cambian una línea: con 0.20.0, `Motor` carga 64 medidas en LyraGASP y 81 en Jam,
las mismas que su catálogo efectivo, con sus tres sombras. `Motor.desde_datos` y `desde_medidas` no
tienen proyecto y siguen sin sombras.

## Verificación

- Suite: 2055 tests en verde, con tests escritos antes del arreglo que fallaban sobre 0.19.0.
- Mutación de código ([logs](vault-kb/estudios/0.20.0-motor/verificacion/)): `oracle_metalenguaje/motor.py`
  23/23 y `nucleo/medida.py` 260/261. El sobreviviente contaba como «rojo perdonado» una medida
  verde en sombra; lo mata un test agregado con la ronda terminada y verificado aplicando el mutante
  a mano.
- `tools/verificar_instalacion.py`: `WHEEL OK` con la versión 0.20.0.
- Medido sobre los proyectos reales de LyraGASP y Jam con el checkout: `Motor` carga 64 y 81
  medidas, iguales a su catálogo efectivo, con tres sombras cada uno.
- Tarea [`20260915-010454-motor`](tareas/20260915-010454-motor/TAREA.md), con lo medido y el diseño.

Álgebra y sintaxis no cambian. La publicación en PyPI la realiza el dueño.

---

---

Las notas de 0.19.0 y anteriores siguen en [docs/notas/anteriores-a-0.20.md](docs/notas/anteriores-a-0.20.md).
