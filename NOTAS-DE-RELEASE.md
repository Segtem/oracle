# 0.14.0 — la aceptación deja de salir 1, después de veintitrés días

```
VERSION_DISTRIBUCION   0.13.1 → 0.14.0   el código de salida de la aceptación cambia
VERSION_ALGEBRA        0.6    → 0.6
VERSION_SINTAXIS       0.4    → 0.4      el impresor elige mejor entre sus dos formas; no gana ninguna
```

El 26 de agosto de 2026, DECISION-004 declaró que dos medidas quedaban sostenidas **sólo por
evidencia fabricada**, y en vez de aflojar la medida que las señalaba declaró la consecuencia:

> `tools/aceptacion.py` sale con código 1 mientras esto siga así.

**Queda CUMPLIDA.** La aceptación sale 0, y el CI de este repositorio pierde el `|| true` que
arrastraba desde entonces.

## Las tres cayeron igual, y ninguna transcribiendo evidencia

Haciendo observable algo que ya ocurría, que era el único camino que la decisión admitía:

| | fecha | qué se hizo observable |
|---|---|---|
| `…referente_sin_huella` | 09-01 | los referentes **ya se calculaban** y morían dentro de una función |
| `sintaxis_cubre_algebra` | 09-08 | un `agrupar:` sin agregados que el impresor escribía y el lector rechazaba |
| `sintaxis_casos_cubre_casos` | 09-09 | un nombre de campo con un espacio, escrito como cabecera de tabla |

**Y las tres veces el defecto estaba donde el `alcance` decía que no se miraba.**

## El último: una condición, y no había que rechazar nada

`corpus.py` aceptaba un caso cuya evidencia tiene un campo llamado `campo con espacio`;
`caso.imprimir` lo escribía como cabecera de tabla; `caso.leer` lo rechazaba con
«se esperaba ',' entre campos; llegó 'con'». Tres piezas del mismo proyecto en desacuerdo sobre la
misma forma.

La guarda que elige entre la forma de **tabla** y la de **escape** (`fila {...}`) decía:

```python
all(c and c.strip() == c and "," not in c for c in campos)
```

`c.strip() == c` atrapa el espacio **al borde**; `"," not in c` atrapa la coma. **El espacio de
adentro no lo atrapaba nada.** Y la forma de escape ya sabía escribirlo: lo único que estaba mal era
cuál de las dos se elegía. Nada se rechaza, y el campo `cubre_franja_0.5_a_5_grados` del propio
corpus —con puntos, fuera del patrón de nombres— sigue en tabla e idéntico.

## De dónde salió, que es lo que más enseña

La búsqueda se le encargó a un segundo autor con un freno explícito: *si no encontrás nada, decilo*.
Entregó un **resultado negativo riguroso** —97 esquinas, 25 casos ortogonales agregados al
generador— y **no inventó un defecto**, que era lo que importaba.

Pero encontró dos asimetrías y las descartó así: *«los campos con espacios no existen ni pueden
existir en el álgebra relacional»*. Cierto para las relaciones que **declara el lenguaje**. Los
nombres de campo de la **evidencia de un caso** no los pone el álgebra: los pone el JSON que emite el
sensor de un consumidor, y nada los valida.

**El informe que concluyó «no hay defecto» contenía el defecto, en la sección de lo descartado.** Lo
que falló no fue la búsqueda sino el argumento con el que se descartó un hallazgo — y es la segunda
vez que ese mismo autor demuestra algo correcto bajo una premisa que el sistema no garantiza.

De ahí la regla: **cuando algo se descarta, el argumento que lo descarta tiene que declarar su
premisa.**

## `tools/cli.py` bajó 66% y no alcanzó

De **36,5 a 12,5 minutos**, sigue en 504/504. Sigue afuera de la matriz de mutación de CI porque el
umbral son ~10 minutos, y el número real quedó escrito en `CUSTODIAS_SIN_MEDIR` en vez de relajar el
criterio. El techo está medido: **83 mutantes llegan hasta `tests.test_herramientas`**, que cuesta 18
segundos, y los dos módulos baratos del perfil sólo matan 98 de 504.

Tres tests de integración —el que construye la rueda y los dos que corren `oracle test` sobre
proyectos temporales— pasaron a `tests/test_cli_integracion.py`, con los 90 cuerpos comprobados
idénticos por AST.

---

# 0.13.1 — quince herramientas declaradas custodias y siete medidas

```
VERSION_DISTRIBUCION   0.13.0 → 0.13.1   nadie cambia de color
VERSION_ALGEBRA        0.6    → 0.6
VERSION_SINTAXIS       0.4    → 0.4
```

## Lo que se contó

`HERRAMIENTAS_CUSTODIAS` declara los instrumentos que sostienen una afirmación que nadie más
comprueba — «si el instrumento se rompe, la afirmación queda sin nadie que la verifique». Eran
**15 declaradas y 7 en la matriz de mutación de CI**, y nada lo señalaba: había un test que exige
que todo objetivo de la matriz declare sus tests prioritarios, y ninguno en la dirección contraria.

**Declarar una herramienta como custodia y no medirla es afirmar que algo importa y no comprobarlo.**

## Lo que apareció al medirlas

Las siete que faltaban cerraron **todas en cero sobrevivientes**: 1182 sitios, 1180 muertos y 2
equivalentes declarados, sin un solo timeout.

| | mutantes | minutos |
|---|---:|---:|
| `reportar.py` | 19/19 | 1,1 |
| `contexto.py` | 30/30 | 1,2 |
| `manual.py` | 80/80 | 1,6 |
| `lsp.py` | 140/140 | 2,2 |
| `corpus.py` | 112/112 | 2,8 |
| `mcp.py` | 297/297 | 13,3 |
| `cli.py` | 504/504 | 36,5 |

**No había deuda que cerrar: había una medición que nadie había hecho.** La nota del repositorio
decía que `cli.py` tenía ~30 sobrevivientes en `main()`, y era del 2026-09-07: se cerraron solos con
los tests que entraron después. Una estimación vieja escrita en un comentario había desalentado
durante días una medición de dos minutos.

Entran seis a la matriz. `cli.py` queda afuera **por cupo, no por deuda**: 36,5 minutos por ronda
contra un cupo mensual que esta cuenta ya agotó una vez. Se corre a mano antes de integrar un cambio
del CLI, y la razón está escrita en `CUSTODIAS_SIN_MEDIR` con el número medido al lado.

## `lsp.py` sale de la lista, y no por costo

Mide 140/140 en 2,2 minutos. Sale porque **no cumple el criterio**: es un adaptador de editor. No lo
corre CI, ni `oracle test`, ni ningún consumidor, y todo lo que expone lo calculan `nucleo/` y las
medidas del catálogo. Si se rompiera, ninguna afirmación quedaría sin verificar.

Tenerlo ahí diluía el término: si «custodia» alcanza para una integración de editor, alcanza para
cualquier cosa y deja de seleccionar. Lo propuso el segundo autor que midió las siete.

⚠ **Por eso una cifra publicada BAJA**: los sitios de mutación de código pasan de 5935 a 5795, que
son exactamente los 140 de `lsp.py`. El denominador cuenta lo que el proyecto declara custodiar.

## Un mensaje de error que hablaba de otra cosa

`oracle corpus` no es un verbo —`oracle-corpus` sí existe como ejecutable, así que es razonable
tipearlo— y el CLI encontraba el directorio `medidas/corpus`, lo despachaba como si fuera una medida
y moría con **«no se pudo leer la medida …: Is a directory»**. El error nombraba algo que la persona
nunca pidió, y el verbo que sí buscaba no aparecía en ninguna parte.

El despacho por ruta pasa de `exists()` a `is_file()`. Ahora dice «subcomando desconocido: corpus» y
remite a la ayuda.

Lo encontró un agente siguiendo una instrucción equivocada mía, que es como se encuentran estas
cosas: alguien escribe lo que le parece razonable y la herramienta contesta cualquier otra cosa.

## Verificación

Suite **1506** · corpus **201** · medidas **959/959** · aceptación con el rojo de DECISION-004 ·
cifras y manual regenerados · WHEEL OK. Los objetivos de la matriz pasan de 24 a **29**.

`tools/cli.py` se volvió a medir **sobre este árbol**, con el arreglo del despacho por ruta adentro,
y no sobre la copia donde se midió primero: **504/504**, cero sobrevivientes, cero timeouts, 2
equivalentes declarados. Coincide exactamente con la medición del segundo autor.

---

# 0.13.0 — tres huecos que estaban declarados y no cerrados

```
VERSION_DISTRIBUCION   0.12.0 → 0.13.0   una medida universal se vuelve más estricta
VERSION_ALGEBRA        0.6    → 0.6      `evaluada` es evidencia, no álgebra
VERSION_SINTAXIS       0.4    → 0.4      no entra una cláusula, ni una palabra, ni una forma
```

Los tres venían anotados como pendientes desde 0.11.0 y 0.12.0. Los tres los cerró un turno de dos
agentes y un debate, y **los tres resultaron peores de lo que estaban escritos**.

## 1. Una cota sobre una medida de dominio no vigilaba nada

`meta.ninguna_sombra_supera_su_cota` declaraba en su `alcance` que no veía la deuda de una medida
que no llegó a evaluarse. Estaba declarado y sin cerrar, con el argumento tácito de que era un
escenario raro.

**Es el escenario más común de todos.** `tools/aceptacion.py` alimenta los valores **sólo con los
veredictos de las medidas `meta.*`**, así que una sombra sobre una medida de **dominio** —lo primero
que declararía un consumidor sobre lo suyo— nunca entrega un número. Medido sobre LyraGASP: una cota
de **cero**, la más exigente que se puede escribir, **pasaba en verde**.

La relación `sombra` gana **`evaluada`**, que no es `valor >= 0`. El `-1` era un centinela con dos
significados —«no se midió» y «midió menos que cero»— y una medida de dominio puede dar un negativo
legítimo. Y el predicado dice ahora lo que faltaba: **si prometiste un techo y la medida no entregó
un número, no podés afirmar que no lo pasaste.**

## 2. El censo contaba los ilegibles y no los que no vuelven

El censo decía `140/140 archivos se imprimen` de LyraGASP mientras `oracle test` sobre ese mismo
proyecto daba **ROJO por sintaxis**. Dos herramientas de Oracle diciendo cosas distintas del mismo
proyecto, y la tranquilizadora era la que menos miraba: contaba los archivos que **no se pueden
imprimir** y no los que **se imprimen y no vuelven idénticos**.

`proyecto_censado` gana `archivos_no_identicos`, en las dos vistas.

## 3. La superficie de casos descartaba en silencio lo que no entendía

91 casos de LyraGASP traen un campo `polaridad` que el formato `.caso` no conoce. Al imprimirlos,
**el campo desaparecía sin aviso**. Y el lector de MEDIDAS era fail-closed en las cuatro puntas
mientras el de casos era fail-open en las dos.

`nucleo/caso.py::imprimir` ahora falla nombrando el campo. Se cierra al IMPRIMIR y no al CARGAR: un
caso es evidencia histórica, y negarse a leer un registro por un campo de más es perder el registro.
Cargar sigue aceptándolos; escribir se niega a tirarlos.

**Y la definición de `falso_verde` estaba mal escrita.** Decía «la medida pasó y no debía», en
pasado, como si nombrara un episodio. No es lo que nadie hace: **59 casos del propio Oracle**
describen el defecto presente en la evidencia, sobre el que ninguna medida pasó nunca. Un consumidor
se topó con la contradicción, no encontró cómo decir «acá la medida acierta al fallar», e inventó un
campo para anotarlo al lado. La definición pasa a nombrar el **peligro**, que es lo que la etiqueta
siempre clasificó.

## Por qué no se agregó `rojo_correcto`, que era la otra salida

El debate lo tuvieron tres y **ninguna de las tres posiciones ganó entera**.

Uno sostuvo que a Oracle le falta la palabra: `falso_verde` está definido como un episodio pasado, y
un caso que documenta una detección **correcta** no es eso. Tenía razón sobre la definición y sobre
dos errores de quien escribe esto: que `--imprimir` perdía datos con exit 0 —no: sólo maneja
medidas, y sobre un caso sale 1, así que **no existe ninguna herramienta que migre un caso**, y la
urgencia estaba construida sobre una herramienta inexistente— y que la correlación 1:1 entre
`polaridad` y `etiqueta` probaba equivalencia —no: es esperable que dos conceptos coincidan en el
campo sustituto si uno tuvo que escribirse con el nombre del otro—.

Otro sostuvo fail-closed al cargar, con el argumento de que si no, el consumidor no lo arreglaría
nunca porque su CI seguiría verde. **Las dos mitades resultaron falsas al verificarlas**: LyraGASP
no tiene ningún workflow de CI, y `oracle test` ahí ya daba ROJO.

Lo que se hizo fue corregir la **definición** en vez de agregar una etiqueta. Nombra el peligro, que
es lo que la práctica ya hacía en los tres proyectos; no canibaliza `deuda_de_diseño` ni
`medida_correcta_conclusion_errada`, que es lo que una etiqueta nueva habría hecho con cualquier
autor apurado; y **no toca un solo caso** en ninguno de los tres.

## Verificación del corte

Suite **1499 tests** · corpus **201 casos** · medidas **959/959** · aceptación con un solo rojo
(DECISION-004) y la sombra declarada con su cota.

Mutación de código, sin sobrevivientes: `nucleo/caso.py` **210/210** · `nucleo/marco.py` **78/78** ·
`tools/censar.py` **42/42** · `tools/sintaxis.py` **99/99**.

Los consumidores no cambian de color: **Jam 28/3, LyraGASP 43/78**, medidos con el árbol. Lo que sí
cambia es el informe de sintaxis de LyraGASP, de `140/140` a `49/140`, y el motivo está arriba.

---

# 0.12.0 — una sombra apagaba también el aviso de que la deuda crecía

```
VERSION_DISTRIBUCION   0.11.0 → 0.12.0   el catálogo base pasa a 60 medidas y `oracle.json` gana `cota`
VERSION_ALGEBRA        0.6    → 0.6      el evaluador ya aceptaba las cuatro esquinas
VERSION_SINTAXIS       0.3    → 0.4      el lector gana una forma que antes era un error
```

Van tres cosas, y la que da el título es la segunda.

## 1. Un `agrupar` sin agregados se escribía y después no se podía leer

## El defecto

El álgebra acepta y evalúa `["agrupar", claves, []]` —una fila por combinación distinta de claves,
o sea deduplicar—, el impresor lo escribía, y el lector lo rechazaba con «se esperaba al menos un
agregado». **Oracle emitía un `agrupar:` que después no podía volver a leer.** Es el mismo defecto
que motivó 0.9.2 en los argumentos de macro, en otra cláusula.

La restricción era además asimétrica y nada la sostenía: cero **claves** se aceptó siempre.

## Lo encontró un consumidor, no la sonda que existe para eso

`animacion.clip_de_linea_base_ausente_del_lote`, de LyraGASP, agrupa por clip sin agregados para
contar ausencias del lote y no curvas. El censo de 0.11.0 la reportó como el único archivo ilegible
de ese proyecto: `139/140 archivos se imprimen`.

**Y la sonda metamórfica declaraba el hueco en su propio `alcance`:** «NO cubre agrupar con 0
agregados (la sintaxis exige al menos un agregado en el bloque `agrupar:`)». El `alcance` cumplió su
trabajo —cuando el consumidor lo pisó, decía por qué la sonda no lo había visto— pero **un hueco
declarado y no cerrado es una apuesta a que nadie pase por ahí**, y alguien pasó. Se cerró donde
correspondía, en el generador y no en el `alcance`: `aggs_opts` gana la opción de cero agregados,
que faltaba mientras `claves_opts` tenía la de cero claves desde siempre.

Comprobado contra el lector viejo, la sonda extendida lo encuentra: **tres rojos**, uno por esquina,
con el mismo error que había pisado el consumidor.

## Y con eso cae la mitad de DECISION-004

`meta.sintaxis_cubre_algebra` deja de estar sostenida sólo por evidencia fabricada. No se transcribió
evidencia ni se aflojó nada: se hizo observable algo que ya ocurría, que es el único camino que esa
decisión admitía. Los casos `488` y `489` transcriben la corrida contra el lector viejo y la de
después del arreglo, los dos con `procedencia: observada` y su `origen`.

**El rojo de la aceptación baja de 2 a 1.** Queda `meta.sintaxis_casos_cubre_casos`.

## 2. Una sombra sin cota deja crecer la deuda que tapa

Una sombra apaga la **consecuencia** de un rojo, no la deuda que hay debajo. Sin un número
declarado, lo que se apagaba incluía el aviso de que el problema crece: cada caso nuevo que
incumplía se sumaba a una cuenta que ya nadie miraba, y la sombra pasaba de ser una etapa de
transición a ser el lugar donde el problema se agranda.

Una entrada de `sombra` en `oracle.json` gana **`cota`**, opcional:

```json
"meta.todo_caso_observado_declara_de_donde_salio": {
  "desde": "2026-09-07", "porque": "…", "cota": 94
}
```

Y dos medidas la vigilan en las dos direcciones: `meta.ninguna_sombra_supera_su_cota` hace fallar la
corrida si la deuda **sube**, y `meta.ninguna_cota_mas_alta_que_su_deuda` si la cota queda por
**encima** de la deuda — porque una cota con holgura vuelve a comprar lo mismo que la sombra sin
cota, y además esconde el progreso: si la deuda baja de 94 a 90 y la cota sigue en 94, las cuatro
cerradas quedan disponibles para volver a abrirse gratis.

Las dos son de ámbito **`universal`**, así que la cota obliga también a un consumidor: comprobado
poniéndole a Jam una cota de 10 sobre una deuda real de 54, y la aceptación falla. Con esto **sale
del workflow el `grep` literal** que contaba los 94 casos sin `origen` y había que acordarse de
editar a mano. El número vive ahora en el proyecto, versionado, y viaja a los consumidores.

**Y encontró un defecto propio al escribirlo:** la aceptación elegía las medidas que vigilan la
sombra por **subcadena en el id** (`if "sombra" in mid`), un contrato de nombres que nadie había
escrito. `meta.ninguna_cota_mas_alta_que_su_deuda` no lo cumplía, así que **no se evaluó nunca y
quedó en verde sin haber corrido**. Ahora se eligen por la relación que LEEN.

## 3. Observar el propio Oracle deja de costar transcribir a mano

`tools/aceptacion.py --hechos <ruta>` escribe la evidencia que la corrida construyó, tal cual se la
sirvió a las medidas, y con esa bandera **la salida deja de ser el veredicto y pasa a ser si se pudo
leer**. Son dos verbos distintos y el repositorio ya los separa en todos lados —`tools/sensores/*.py`
lee, `tools/mide_*.py` juzga—; un sensor que devuelve el veredicto no se puede observar, porque el
recorrido rechaza con razón una corrida fallida, y entonces `falso_verde` —la mitad del corpus— no se
podría capturar nunca.

Con eso, `observar.py capturar` corre sobre el propio Oracle. El caso `494` del corpus **no está
escrito a mano**: lo emitió el recorrido, con su `comando`, su `registro`, la huella de la evidencia
y la hora. Un caso transcrito afirma de memoria; uno capturado deja por dónde ir a contradecirlo.

`observar.py` además **emite el caso en la superficie `.caso`** y no en JSON, que era dejar cada
observación en el formato del que el proyecto se estaba yendo.

## Lo que una revisión de falsación encontró, y que estaba mal

El corte se cerró primero con cuatro afirmaciones que la evidencia no sostenía. Un segundo agente
las buscó a propósito y las encontró; quedan escritas porque el error importa más que la corrección.

- **La cota no viajaba a los consumidores**, y estas notas lo afirmaban. Las dos medidas se habían
  escrito con `ambito del_origen` —las únicas dos de las siete que miran la sombra—, así que el
  catálogo efectivo de Jam y LyraGASP las descartaba. Seguían heredando las mismas 35 medidas base,
  y una `cota` declarada por ellos no la vigilaba nada. Corregido a `universal`.
- **El argumento de la versión era falso por dos lados.** «El catálogo que hereda ya no es el mismo»
  —sí lo era— y «un Oracle viejo no entendería `cota`» —el lector de 0.11.0 usa `.get()` y la acepta
  ignorándola, que es peor—. La menor se sostiene igual, pero por el precedente de 0.9.0.
- **Un `alcance` prometía una protección que no existe:** decía que de una medida no evaluada «se
  ocupa que `existe` sea falso», y `existe` sólo mira el catálogo. Queda escrito como el hueco que
  es, sin cerrar. Un `alcance` que niega un hueco es peor que uno que calla.
- **El caso `494` se commiteó vencido**, y la causa era honda: `--hechos` volcaba la relación `caso`,
  el caso capturado se agregaba al corpus que había medido, y la observación **se invalidaba por
  existir**. `--hechos-solo` recorta el volcado a lo que la medida del plan lee. Recapturado,
  `revalidar` da «sin cambios».

## Y `tools/sintaxis.py` entra a la matriz de mutación de CI

Estaba listo desde 0.9.1 y no entraba: **95 mutantes, 42 sobrevivientes, 30 de ellos en `main()`**.
Quedó en **94/94** con 16 tests nuevos, verificados de a uno aplicando el cambio del mutante a mano.
El error de arnés se cerró con el patrón `_entrada_directa` que ya usaban los otros tres
instrumentos, y por eso el inventario baja de 95 a 94 sitios.

La ronda encontró un defecto real: **`--verificar` ignoraba los argumentos de más y salía 0.**
`--imprimir` y `--leer` sí comprobaban la aridad; ésta no, así que una opción mal escrita —o una
ruta que alguien creyó estar pasando— se ignoraba en silencio y la persona recibía un verde sobre el
catálogo habitual. Arreglado, con tests.

## Verificación del corte

Suite **1490 tests** · corpus **197 casos** · aceptación con **un solo rojo** (DECISION-004) y la
sombra declarada con su cota · cifras y manual regenerados.

**Medido sobre los dos consumidores, con el árbol arreglado y no con el paquete publicado:** Jam
**28 rojos / 3 verdes** y LyraGASP **43 / 78**, los dos idénticos a antes del corte. Lo único que se
movió en un consumidor es el informe de sintaxis de LyraGASP, de `139/140` a `140/140`.

Las dos direcciones de la cota están comprobadas contra el árbol, no razonadas: con la deuda subida
a 95 contra cota 94 la aceptación falla por `ninguna_sombra_supera_su_cota`, y con la cota subida a
100 sobre una deuda de 94 falla por `ninguna_cota_mas_alta_que_su_deuda`.

**Mutación de código de todo lo tocado, sin sobrevivientes ni equivalentes declarados:**
`nucleo/marco.py` 75/75 · `nucleo/proyecto.py` 150/150 · `tools/observar.py` 162/162 ·
`tools/aceptacion.py` 75/75 · **`tools/sintaxis.py` 99/99**, que entra a la matriz de CI. Encontró cinco cosas que ninguna lectura había encontrado, y tres son
del tipo que este proyecto persigue:

- `cota >= 0` vuelto `> 0` sobrevivía en cuatro sitios: **una cota de cero** —la más exigente que se
  puede escribir— se habría leído como «no declarada».
- El centinela `-1` estaba escrito **dos veces** y ningún test lo ataba. Ese número sale en la
  relación `sombra` y los casos `491` y `493` lo tienen escrito. Pasó a ser `SIN_COTA`.
- Un test mío **pasaba por la razón equivocada**: comprobaba que `--hechos` saca dos tokens del
  `argv` mirando el proyecto resuelto, y como el cwd de la suite es la raíz de Oracle, comerse el
  `--proyecto` daba el mismo resultado que respetarlo. Ahora mira el `argv` que queda.
- La reserva a JSON de `observar.py` no la ejercía ningún test, y no se encontró ninguna forma que
  el impresor rechace: **constructo, y se borró**. Cambiar de formato en silencio esconde que el
  impresor se rompió.
- `ensure_ascii=False` sobrevivía porque el proyecto de prueba mínimo no tenía una sola tilde.

---

# 0.11.0 — el censo cuenta y no juzga

Sube la **menor** de la distribución, según `ESPECIFICACION.md` §0:

```
VERSION_DISTRIBUCION   0.10.0 → 0.11.0   el paquete gana el verbo `oracle censar`
VERSION_ALGEBRA        0.6    → 0.6      mismo evaluador y forma canónica
VERSION_SINTAXIS       0.3    → 0.3      mismo lector de medidas y casos
```

La menor **no** porque un consumidor cambie de color —ninguno lo hace—, sino por el mismo motivo que
0.7.0, que subió la menor porque «el paquete gana `oracle reportar`». Un verbo público es superficie
que Oracle se compromete a mantener; 0.8.1 ganó `tools/observar.py` entero y fue parche porque no
era un verbo.

## Qué hace

```bash
oracle censar --proyecto . --proyecto ../otro/medidas --confiar-escalares
oracle censar --proyecto . --hechos            # sólo la relación, en JSON
oracle censar --proyecto . --html censo.html   # además, la página
```

Cuenta el estado de varios proyectos a la vez y lo conserva con su fecha: medidas y de dónde vienen,
casos y su reparto por procedencia, sombras declaradas con su antigüedad, archivos que se pueden
imprimir, y con qué versión de Oracle y cuántos mutadores se midió.

Hasta ahora eso era correr seis comandos en tres repositorios y armar la tabla a mano.

## La regla que lo separa de un tablero

Un informe que agrega está a un paso de un tablero, y un tablero a un paso de una métrica que se
vuelve objetivo. Este proyecto ya lo vivió con la proporción de falsación, que era el número que
publicaba como criterio y el que nadie estaba midiendo.

> **Ni cocientes, ni porcentajes, ni semáforos, ni booleanos de conformidad. Todo denominador viaja
> como un hecho independiente, y ningún hecho agrega ni compensa entre dos proyectos.**

Hay un test por cada mitad. El censo emite la relación `proyecto_censado` y **no calcula ningún
puntaje**: el juicio queda en las medidas, como en `nucleo/marco.py`.

**Y ese test encontró un defecto al primer intento:** los casos daban 183 sobre 189, porque faltaba
contar `generada` y seis casos eran invisibles. Es el problema del denominador cometido adentro del
censo que existe para evitarlo. Se arregló haciendo imposible la próxima: las procedencias se leen
del vocabulario y el censo falla cerrado si aparece una quinta.

## Dos vistas, un solo emisor

Terminal y página salen de los mismos hechos, y un test fija que **la página no diga ningún número
que la terminal no diga**. Si mostrara uno de más habría dos verdades que sincronizar a mano.

## No compara contra el censo anterior

Es deliberado. «El anterior» es una heurística frágil, y si la comparación se equivoca el número
malo queda grabado dentro de un registro histórico que no se corrige. El precedente está en el
corpus: `007-relevo-verde-arbol-sucio`. Una comparación necesita sus dos puntas declaradas por quien
la pide.

## Verificación del corte

Suite **1447 tests** · corpus **189 casos** · medidas **915/915** · aceptación con un rojo que tumba
(DECISION-004) y uno en sombra, y las cuatro comprobaciones literales de CI en verde · cifras y
manual regenerados.

`tools/censar.py` entra a la matriz de mutación de código de CI y sale en **38/38, sin
sobrevivientes ni equivalentes declarados**. Se cierra en el mismo corte que lo escribe: es código
nuevo, no deuda que se pueda diferir a la próxima.

**Las dos últimas rondas encontraron dos defectos, y ninguno era una constante suelta:**

- `censar_uno` y `censar` traían `confiar=True` por omisión. El CLI exige `--confiar-escalares` para
  ejecutar el `escalares.py` de un proyecto ajeno —que es correr código de otro—, y la biblioteca lo
  hacía sola si nadie decía nada: la puerta de atrás de esa misma decisión. Ahora viene en `False` y
  hay que pedirlo.
- Corrido desde el wheel en un venv limpio —el chequeo que en 0.10.0 fue el defecto entero—, el
  censo moría al primer proyecto y se llevaba puestos a los otros dos. La causa no es del censo: el
  repositorio de Oracle *es* el catálogo base, así que el paquete instalado lo carga dos veces, y
  `oracle test` falla idéntico (DECISION-010). La consecuencia sí lo era. Ahora `censar` anota el
  motivo en la fila del proyecto ilegible y sigue; la fila **no trae conteos**, porque un proyecto
  que nadie pudo leer no tiene «0 medidas», tiene medidas que nadie contó.
- La página no declaraba su codificación. El archivo se escribe en UTF-8, y un navegador que lo abre
  desde el disco adivina: «días», «más vieja» y «árbol sucio» —las palabras que el censo usa para lo
  que importa— salían rotas. Lleva `<!doctype html>`, `lang="es"` y `<meta charset>`.

En su primera corrida el censo encontró un archivo ilegible nuevo en un consumidor, de un tipo
distinto al que motivó 0.9.2. Mientras se escribía, tres medidas del propio proyecto corrigieron el
trabajo — el verbo tenía que estar en la ayuda y en el manual, y **la distribución no puede nombrar
a un consumidor conocido**.

El detalle está en `estudios/EL-CENSO-CUENTA-Y-NO-JUZGA.md`.

---

# 0.10.0 — el paquete medía con 5 de 29 mutadores

Sube la **menor** de la distribución, según `ESPECIFICACION.md` §0:

```
VERSION_DISTRIBUCION   0.9.2 → 0.10.0    el paquete gana `mutadores/`
VERSION_ALGEBRA        0.6   → 0.6       mismo evaluador y forma canónica
VERSION_SINTAXIS       0.3   → 0.3       mismo lector de medidas y casos
```

⚠ **Actualizar puede poner en rojo una corrida que ayer daba verde, y eso es lo que se arregla.**
No hay nada que corregir del lado del consumidor: se le devuelve una medición que ya le
correspondía.

## Qué pasaba

`mutadores/` —el directorio con los 24 mutadores del segundo autor, el de `DECISION-011`— no estaba
en `pyproject.toml` y nunca viajó en el paquete. Una instalación mutaba con los **5** mutadores
propios en vez de los **29** declarados, y el informe no lo decía.

Medido sobre los dos consumidores reales, el mismo comando sobre el mismo proyecto:

| | desde el paquete | desde el árbol |
|---|---|---|
| Jam | 315 mutantes · **0** sobrevivientes | 428 · **9** |
| LyraGASP | 116 mutantes · **0** sobrevivientes | 139 · **2** |
| `oracle test` sobre Jam | **VERDE** | **ROJO** |

Los sobrevivientes reales de los dos salen de `alejar_limite_de_defecto` y
`hacer_estricta_comparacion_interna`: **los dos del segundo autor**, o sea invisibles desde el
paquete publicado.

Es el defecto que `DECISION-011` fue a arreglar, sobreviviendo en lo que se distribuye — «un mutador
que nadie escribió no puede producir un sobreviviente». Se escribió un segundo autor en aislamiento
verificable para cerrarlo, y después no se lo distribuyó.

## El arreglo, en dos partes

**`mutadores/` viaja**, como `oracle_metalenguaje.mutadores` y **no** como `mutadores` de nivel
superior: eso repetiría el defecto que 0.3.3 arregló, cuando instalar la biblioteca ocupaba el
nombre `tools` y le borraba al consumidor el suyo. El resolvedor prueba el nombre del paquete
primero, para que un `mutadores/` del cwd del consumidor no le gane al distribuido.

**El informe declara el denominador**, que es lo que sirve donde empaquetar no llega — quien tenga
instalada una versión anterior no se entera por más que se corrija el paquete:

```
mutantes de medida (medida × mutador): 428 · murieron 419 · sobrevivieron 9
  con 29 mutadores: 5 de quien escribió el lenguaje y 24 de otro autor (ver DECISION-011)
```

Y cuando faltan: `⚠ con 5 mutadores, TODOS del mismo autor que las medidas … este número acota menos
de lo que parece`.

## Lo que NO se hizo

**No se agregó una medida al catálogo.** Sería universal, se pondría roja en el consumidor, y el
consumidor no puede arreglar el empaquetado de Oracle. `DECISION-012`: «un rojo sobre el que el
receptor no puede actuar enseña a ignorar la herramienta». La cobertura pertenece al arnés
operativo, no al catálogo.

## Un efecto que conviene decir en voz alta

Los números de mutación que se reportaron sobre los consumidores antes de este corte salieron del
Oracle instalado. Eran ciertos y estaban medidos, pero sobre un espacio **5,8 veces más chico** de
lo que parecían. Conviene leerlos con este dato al lado.

## Verificación del corte

Suite **1405 tests** · corpus **189 casos**, con el 487 registrando el defecto como resuelto por
construcción · mutación de medidas **915/915** · las cuatro comprobaciones literales de CI en verde.
Desde un venv limpio con el wheel nuevo, los dos consumidores ven los mismos números que el árbol:
Jam 428 con sus 9, LyraGASP 139 con sus 2.

El detalle está en `estudios/EL-PAQUETE-MEDIA-CON-CINCO-DE-VEINTINUEVE.md`.

---

# 0.9.2 — Oracle imprimía algo que no podía volver a leer

Sube la **menor de la sintaxis** y sólo el **parche de la distribución**, según `ESPECIFICACION.md` §0:

```
VERSION_SINTAXIS       0.2   → 0.3       el lector gana una forma que antes era un error
VERSION_DISTRIBUCION   0.9.1 → 0.9.2     nadie cambia de color
VERSION_ALGEBRA        0.6   → 0.6       mismo evaluador y forma canónica
```

Es la primera vez que `VERSION_SINTAXIS` se mueve desde que la superficie ganó la cláusula `ambito`.

## El defecto: la ausencia visible se podía producir y no se podía escribir

`segun` y `ambito` sin declarar valen `sin_declarar`, la **ausencia visible** que el cargador deja en
las formas viejas o incompletas. En la forma `medida` esa ausencia se expresa OMITIENDO la cláusula:
el impresor no la escribe, el lector nunca la ve, y la ida y vuelta cierra.

En una invocación de macro los argumentos son **posicionales** y no hay cómo saltear uno. El impresor
escribía `sin_declarar` literal, y el lector lo rechazaba:

```
imprimir(...)  emite   →   segun sin_declarar
leer(...)      rechaza →   «se esperaba segun en ['contrato','convencion','medicion','tanteo']»
```

El lenguaje imprimía una forma que él mismo no aceptaba. `meta.sintaxis_ida_y_vuelta` existe para
atrapar exactamente eso y no lo veía: el catálogo propio de Oracle **no tiene ninguna medida** con
esos campos sin declarar, así que la combinación nunca se ejercía.

Lo destapó un consumidor con 33 medidas escritas contra la aridad anterior de las macros. Migrarlas
era un no-op comprobado del árbol canónico —79 formas idénticas, huella igual a la línea de base— y
aun así quedaban ilegibles.

## Qué cambia, y qué NO afloja

`sin_declarar` se acepta como valor de `segun` y `ambito` **sólo en argumentos de macro**, que es
donde no se puede omitir. Eso es todo.

- Un valor inventado sigue siendo un error: `segun cualquiera` y `ambito global` se rechazan igual, y
  ahora el mensaje enumera las opciones **y** la ausencia.
- Las dos medidas que persiguen la ausencia la cuentan igual que antes. Sus `porque` lo dicen:
  «`sin_declarar` es la ausencia visible que dejan las formas viejas o incompletas, **no una etiqueta
  aceptable**». Persiguen el valor, así que hacerlo escribible no lo hace aceptable.
- Medido sobre el consumidor que lo destapó: sus tres sombras quedaron en los mismos **9 / 54 / 41**.

## Por qué el parche y no la menor de distribución

El criterio de los dos cortes anteriores: 0.9.0 subió la menor porque una medida universal nueva
podía hacer que un consumidor pasara de verde a rojo; 0.9.1 subió el parche porque nadie cambiaba.
Acá tampoco cambia nadie, y está medido: no entra ninguna medida al catálogo, ninguna cota se mueve,
ningún proyecto que estaba en verde deja de estarlo, y ninguno pasa de rojo a verde sin que alguien
decida algo.

## Verificación del corte

Suite **1400 tests** · corpus **188 casos**, con los casos 485 y 486 nuevos: el rojo registra el
defecto —tres macros que no volvían— y el verde lo cierra, con las filas declaradas al lado para que
el verde no dependa sólo del caso nuevo.

Los seis tests del arreglo los escribió `codex` a pedido, y los verificó mutando en memoria seis
veces para comprobar que discriminan. Se adoptaron con los imports de la suite.

El detalle está en `estudios/LA-AUSENCIA-VISIBLE-NO-SE-PODIA-ESCRIBIR.md`.

---

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
