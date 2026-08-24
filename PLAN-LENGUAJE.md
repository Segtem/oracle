# Plan: de formato de datos a lenguaje

Instantánea del 2026-08-03. Los valores salen de `tools/cifras.py`, pero **acá están copiados a
mano**: este documento es un registro fechado, no una fuente. Las cifras vivas están en el README,
que sí falla en CI cuando vencen.

> **Estado: `EXPERIMENTAL` → `METALENGUAJE`.** Este documento describe el camino, no una promesa con
> fecha. No hay plazo ni condición de cierre: los ítems se hacen cuando algo los pide, y el
> disparador de cada uno está escrito con el ítem. Ver el estado completo en el README.

| | |
|---|---|
| lenguaje | 2944 líneas (`nucleo/`, código y macros) · 171 `raise` |
| medidas universales | 18 (164 líneas) · 15 por macro |
| **proporción** | **18,0 a 1** (era 16,2 antes de `defmacro`) |
| corpus | 42 casos · 27 defectos en rojo · 12 verdes correctos |
| tests | 391 · mutantes de medida 129/129 |
| mutación de código | **1231 sitios · 16/16 objetivos en VERDE** · 1 equivalente declarado |

La auditoría que originó este plan encontró que Oracle es real —el álgebra tiene dientes, la mutación
de medidas cierra el bucle, la aceptación corre— pero **no es un metalenguaje todavía**. Las medidas
son datos; los medios de abstracción y la reflexión sobre el catálogo siguen siendo Python del
núcleo. Eso es lo que arreglan (a) y (b).

Los cinco ítems, en el orden recomendado de aplicación.

---

## (d) Ninguna cifra tipeada a mano — HECHO

**Cerrado el 2026-08-03**, en tres partes.

### 1 · Las cifras del README salen de `tools/cifras.py`

Pasó de un bloque a cinco (`cifras`, `escala`, `corpus`, `negativas`, `deteccion`); el CI falla si
alguno vence. Corrigió cuatro derivas que nadie había detectado:

- «2202 líneas / 106 `raise` / trece a uno» → los valores reales ya eran 2654 / 150 / 16,2. Era el
  criterio de falsación declarado del proyecto, y era el número que no estaba bajo medición.
- «las macros cubren 26 de las 27 medidas» → eran 18 medidas, 15 por macro.
- «`mutar_codigo.py` sale en VERDE — 1073/1073» contra 1131 sitios: la afirmación de verde sobrevivió
  al cambio de denominador. El caso `021` del corpus cometido sobre el propio README.
- «17 la mutación, 8 una persona, 4 la casualidad, 1 una herramienta ajena» **era correcta y
  computable**: `como_se_detecto` ya era un campo estructurado y nadie lo estaba computando.

Las dos afirmaciones sin respaldo mecánico posible se **borraron** por decisión de Brian: el «33 de
los 42 casos son sobre el propio trabajo» (no hay campo que lo sostenga y clasificarlo era inventar
datos sobre 42 hechos reales) y el «cerca de la mitad de los commits». La segunda estaba **replicada
en `tools/estudio.py`**, que la inyectaba en el paquete de estudio generado; sacarla sólo del README
la habría dejado publicándose.

### 2 · `tools/` en la matriz, con criterio

Mutar `tools/` entero sumaba 559 sitios (+47% de denominador) de plumbing de CLI cuyo veredicto vive
en `nucleo/`. Entró sólo `tools/cifras.py`, con la regla escrita en `HERRAMIENTAS_CUSTODIAS`: entran
**de a uno**, y sólo cuando el instrumento **custodia una afirmación que nadie más comprueba**.

### 3 · El baseline, restaurado — y lo que costó

**Los 16 objetivos de la matriz salen en VERDE**: 0 sobrevivientes, 0 errores de arnés, 1 equivalente
declarado. Pero la primera ronda completa dio **158 errores de arnés** y 23 sobrevivientes.

Los 158 no eran un problema de taxonomía sino de **testabilidad**: trabajo en tiempo de import hacía
que un mutante rompiera el *descubrimiento* de la suite, y el arnés reportaba «error» donde había un
test capaz de matarlo. Cuatro fuentes, encontradas de a una:

| Fuente | Mutantes |
|---|---|
| `MEDIDA = Medida.de_datos(...)` a nivel de módulo en `test_dominio.py` | 139 |
| `import catalogos` vía `oracle_metalenguaje/__init__.py` y `tools/*` en dos tests | 11 |
| `CLASIFICACION_META_BASE = ClasificacionMeta()` al importar | 7 |
| `LIMITES_PREDETERMINADOS = LimitesAlgebra()` al importar | 1 |

**158 → 0.** El diagnóstico inicial estuvo mal en la proporción: se presentó `LIMITES_PREDETERMINADOS`
como la causa principal y explicaba 1 de 158.

**Se rechazó contar un `ImportError` como muerte.** Habría acreditado cobertura real por el motivo
equivocado: si mañana alguien saca el import del tope, el mutante revive y ningún test falla. La
cobertura habría dependido de un efecto colateral de import, no de una aserción. El «tercer estado»
que se había reservado para ese caso **queda descartado por evidencia** y no se escribe.

### Lo que enseñó, más allá del número

- **La mutación encontró lo que 372 tests en verde no veían**, dos veces: el defecto de import y ocho
  libertades sin fijar en `macro.py`.
- **Un test puede pasar por la razón equivocada.** `test_sin_parametros_no_pasa` existía y pasaba,
  pero con una plantilla con huecos la lista vacía fallaba por otro motivo. Sólo lo vio la mutación.
- **Dos bugs propios aparecieron por verificar el camino del CI en vez de asumirlo**, y los dos
  habrían roto el pipeline entero en el primer push: `tools/cifras.py` sin entrada en `PRIORIDADES`
  (`KeyError`), y un `equivalentes.json` global que hacía fallar los 15 jobs restantes de la matriz.
  Los dos tienen ahora su regresión.
- **La sonda barata antes que la ronda cara.** Comprobar «¿se registran escalares al descubrir la
  suite?» toma un segundo; la ronda que contesta lo mismo toma ochenta minutos. Las dos primeras se
  gastaron antes de aprender eso.

### Nota operativa

`tools/mutar_codigo.py` **no tolera nada corriendo en paralelo**: dos de sus tests inspeccionan el
estado global de `/tmp` y el candado de ronda, así que cualquier otra cosa que toque el repo durante
la corrida produce falsos rojos (`RondaEnCurso`, copia temporal no eliminada). Van en serie, o en CI.

Y el eje se mide **particionado**: en un solo proceso queda un timeout —el mutante que apaga
`start_new_session` enlentece todos los tests que matan subprocesos y agota el presupuesto antes de
llegar a la aserción que lo mata—. Con `--objetivo` la priorización lo mata. Un timeout no es una
muerte, así que se dice cuál de las dos corridas vale en vez de elegir la que queda mejor.


---

## (a) `defmacro` en datos — HECHO

**Cerrado el 2026-08-03.** Las tres macros universales salieron del núcleo y viven en
[`nucleo/macros/`](nucleo/macros/) como datos; `nucleo/macro.py` conserva sólo el expansor. Un
proyecto declara las suyas en `<proyecto>/macros/` y no toca nada de Oracle.

**El criterio de éxito se cumplió tal como estaba escrito**: `ninguno`, `ninguno-par` y `peor` se
expresaron en la forma nueva, ninguna necesitó una excepción en Python, y la aceptación, la mutación
de medidas y los tests siguen en verde. `tests/test_macro.py::ProyectoDeclaraLasSuyasTests`
demuestra el camino completo de punta a punta con un proyecto temporal.

**La predicción de este plan sobre la proporción estuvo mal.** Decía «saca líneas del núcleo, así que
la proporción mejora». Fue de 16,2 a **18,0**: el mecanismo que reemplaza a las tres funciones
—declaración, guardas, registro, expansión acotada— pesa más que lo que borró. El pago no es este
corte; es que la macro número cuatro ya no cuesta núcleo. Queda anotado como error de estimación, no
corregido a posteriori.

Y una trampa que hubo que cerrar en el camino: el numerador ahora cuenta `nucleo/macros/*.json` junto
con el `.py`. Contando sólo código, mover Python a datos habría «mejorado» la proporción sin que el
lenguaje encogiera un gramo.

### Lo que encontró la mutación de código, que los tests no

Los tests pasaban en verde con un defecto de diseño adentro. `mutar_codigo.py --objetivo
nucleo/macro.py` dio **RONDA INCONCLUSA: 80 mutantes · 30 muertos · 12 vivos · 38 errores de arnés**.

La causa de los 38 era la implementación misma: la biblioteca estándar se cargaba **al importar el
módulo**, así que un mutante que rompía `Macro.de_datos` hacía fallar el *descubrimiento* de los
tests. El arnés reportaba «error», no «muerte» — el caso `017` del corpus, provocado por el diseño
nuevo. Con carga perezosa (`_base()`) esos mutantes volvieron a un lugar donde un test puede matarlos:
la segunda ronda dio **0 errores de arnés**.

De los 11 sobrevivientes restantes:

- **uno ya estaba muerto** por un test agregado entre las dos rondas (la cadena del diagnóstico de
  bucle: saber que hubo torre no sirve si no dice cuál);
- **dos eran una rama muerta** —`if len(datos) > 1` en el mensaje de guarda, inalcanzable porque la
  aridad ya se comprobó y ninguna macro tiene cero parámetros—. Se borró la rama en vez de declararla
  equivalente: una rama que nada puede ejercitar no se documenta, se saca;
- **los ocho restantes eran tests que faltaban**: inmutabilidad de `Macro`, plantilla vacía o que no
  es lista, la cuenta en el error de aridad, qué nombra el mensaje de una guarda incumplida, la lista
  de directorios en `cargar_macros`, y una cabeza no hasheable en `es_macro`.

Ninguno de los ocho era un bug de comportamiento hoy. Todos eran libertades que el código tenía y
nadie estaba fijando — que es exactamente lo que la mutación existe para mostrar.

El último sobreviviente enseñó algo aparte: `test_sin_parametros_no_pasa` **existía y pasaba**, pero
usaba una plantilla con huecos, así que una lista de parámetros vacía fallaba igual por otro motivo
(«usa huecos que no son parámetros»). El test verificaba una excepción que no era la suya. Un test
que pasa por la razón equivocada es un falso verde con forma de cobertura, y sólo lo vio la mutación.

**Cierre: `nucleo/macro.py` mata 80/80** — sin timeout, sin error de arnés y sin un solo equivalente
declarado.

### Nota operativa para el resto del plan

`tools/mutar_codigo.py` **no tolera nada corriendo en paralelo**: dos de sus tests inspeccionan el
estado global de `/tmp` y el candado de ronda, así que cualquier otra cosa que toque el repo durante
la corrida produce falsos rojos (`RondaEnCurso`, copia temporal no eliminada). Las 15 particiones de
(d) van en serie, o en CI aislado — nunca en paralelo local.

<details>
<summary>El diseño, como quedó</summary>

### La forma, como quedó

```json
["defmacro", "<nombre>",
  ["<parametro>", ...],
  [["guarda", <expresion>, "<mensaje>"], ...],
  <plantilla>]
```

La plantilla es la forma canónica con huecos `["$", "<parametro>"]`; expandir es sustituir. `["$", …]`
es el único constructor nuevo del lenguaje.

### Cómo quedaron las decisiones

| Decisión | Cómo se resolvió |
|---|---|
| Dónde viven | `nucleo/macros/` la biblioteca estándar; `<proyecto>/macros/` las del proyecto, con el mismo confinamiento anti-symlink que el resto |
| Guardas | `["guarda", expr, mensaje]`, sustituidas y evaluadas por `evaluar_expr` **sobre una fila vacía** — cero evaluador nuevo, y hereda el contrato entero del álgebra |
| Torres | permitidas y acotadas por `expansiones_maximas` (nuevo límite en `LimitesAlgebra`) |
| Forma de `defmacro` | cinco elementos fijos; sin guardas se escribe `[]`, igual que una relación vacía en el álgebra |

Fallas cerradas que quedaron fijadas por tests: hueco no declarado, parámetro que la plantilla nunca
usa, nombre que tapa una palabra del lenguaje, nombre declarado dos veces, guarda mal formada, aridad
incorrecta, y una instalación sin biblioteca estándar —`rglob` sobre un directorio ausente devuelve
vacío, así que sin guarda el lenguaje se quedaba sin `ninguno` **en silencio**—.

**El riesgo que este plan anotaba quedó cubierto:** una macro no puede esconder un umbral sin defensa,
porque `Medida.de_datos` valida **después** de expandir, no antes.

</details>

---

## (b) Reificación mecánica del catálogo — HECHO

**Cerrado el 2026-08-24.** `como_hechos()` sigue devolviendo una lista de hechos `medida` para no
romper consumidores existentes, pero esa lista ahora transporta las demás relaciones derivadas de la
forma canónica del catálogo: `fuente`, `termino`, `requiere` y `paso_de_medida`. `medidas_aplicables`
y `Medida.evaluar` despliegan esas relaciones antes de seleccionar o ejecutar una medida, así que
`tools/aceptacion.py` pudo empezar a evaluar medidas nuevas sobre la estructura sin editar la
herramienta.

La desviación frente al boceto de abajo es deliberada: el plan llamaba `paso` a la relación
estructural, pero `paso` ya existe como traza runtime del álgebra, con campos `filas_antes` y
`filas_despues`. Mezclar ambos esquemas haría que las medidas metamórficas de `tools/trazar.py`
leyeran pasos declarados como si fueran pasos ejecutados. La estructura del catálogo usa
`paso_de_medida`; para las medidas nuevas alcanzó con `termino`, que recorre todos los nodos y
escalares de `Medida.a_datos()`.

El criterio falsable se cumplió con tres medidas nuevas escritas como datos:
`meta.toda_medida_de_ausencia_declara_requiere`, `meta.toda_medida_filtra_o_agrupa` y
`meta.ningun_umbral_de_igualdad`. Las tres tienen corpus en las dos polaridades y la mutación de
medidas queda en 246/246 muertos.

**El problema, exacto.** `nucleo/marco.py:98`, `hechos_de_uso()` es una función Python que emite los
hechos `medida_en_uso` con los campos que Python eligió. El README dice que «L2 no necesita mecanismo
propio»; **L2 tiene mecanismo propio y se llama `marco.py`**. Para hacer una pregunta nueva sobre las
medidas —«¿cuál tiene el umbral más flojo?», «¿qué medidas comparten relación de entrada?»— no se
puede escribir una medida: hay que agregar un campo en Python primero.

### Forma propuesta

Un recorrido genérico de la estructura de cada medida, que emite relaciones derivadas mecánicamente:

```
medida(id, agregado, comparador, umbral, tiene_defensa, alcance, dominio, es_heredada)
paso(medida, indice, operador)
fuente(medida, relacion, alias)
termino(medida, ruta, cabeza)        un hecho por nodo de expresión
```

Lo que **sí** debe seguir produciendo `marco.py` es lo que no está en la estructura sino en el uso:
`casos_que_la_evaluan`, `mutantes`, `mutantes_vivos`. Eso son hechos sobre el mundo, no sobre la
forma, y necesitan un productor con razón.

### Criterio de éxito — y es falsable

**Escribir una medida meta nueva sin tocar una línea de Python.** Candidatas:

- `meta.ningun_umbral_sin_defensa` — hoy lo impone una excepción al cargar; como medida se vuelve
  inspeccionable y aparece en el informe con su alcance.
- `meta.toda_medida_filtra_o_agrupa` — una medida sin `donde` ni `agrupar` mide la relación entera,
  que casi siempre es un error de autoría.
- `meta.ninguna_relacion_se_mide_una_sola_vez` — detecta evidencia de la que sólo cuelga una medida.

Si alguna de las tres se escribe como archivo de datos y corre, (b) está hecho. Si hace falta agregar
un campo en `marco.py` para cualquiera de ellas, no.

**Riesgo a vigilar:** el recorrido genérico es superficie nueva en el núcleo (~60 líneas) contra los
campos elegidos a mano que borra (~40). A corto plazo la proporción no mejora; el pago está en que la
pregunta meta número 20 no cueste Python.

### El disparador — escrito el 2026-08-24, y todavía no sonó

Esto NO se hace hasta que suene. La regla que gobierna el álgebra desde el principio —«no se agrega
un operador hasta que una segunda medida lo necesite»— aplica igual acá: **no se agrega reflexión
hasta que una segunda pregunta meta la necesite, y la necesite un consumidor.**

> **Suena cuando alguien —no el autor— quiere escribir una medida meta que hoy exige editar Python.**

Hasta hoy no sonó nunca, y conviene ser preciso sobre quién detectó el límite: lo detectamos desde
adentro. Los dos consumidores suman 47 medidas —geometría, malla, física, scatter, recarga, ML
deformer— y **ninguna es meta**. Nadie chocó contra esto todavía.

### La deuda, medida el 2026-08-24

Lo que L2 ve de una medida son nueve campos que `como_hechos()` eligió a mano: `id`, `dominio`,
`relacion`, `umbral_op`, `umbral_valor`, `porque`, `alcance`, `es_meta_por_el_nombre`,
`es_meta_por_lo_que_mide`. Todo lo demás de la estructura es invisible.

La demostración más clara la dio el propio trabajo del día: **`requiere` se agregó al lenguaje el
2026-08-24, cambia veredictos, tiene su propio mutador — y L2 no lo ve.** No se puede escribir
`meta.toda_medida_de_ausencia_declara_requiere` sin agregar un campo en Python primero. Lo mismo con
«¿qué medidas usan `unir`?» o «¿cuántos filtros tiene?».

Y hay un segundo mecanismo propio que la sección de arriba no nombraba:
`ClasificacionMeta.relaciones_del_lenguaje` en `nucleo/medida.py` es un `frozenset` escrito a mano.
El 2026-08-24 pasó de 3 entradas a 7 en dos ediciones de Python —`compromiso` primero, después
`paso`, `nodo` y `producto`—: cada relación reflexiva nueva cuesta una edición del núcleo. La
reificación tiene que cubrir también esto, o la mitad del problema queda en pie: una relación
debería ser del lenguaje porque **quien la produce lo declara**, no porque figure en una lista.

### No hay impedimento formal, y es a propósito

Hubo un momento —el 2026-08-24— en que un compromiso prerregistrado le ponía tope al tamaño del
núcleo y esto no entraba. Ese tope se retiró junto con la puerta entera: era un número inventado y
Oracle está en estado **EXPERIMENTAL**, sin fecha de corte ni condición de cierre.

Así que lo único que frena la reificación es el criterio, no una regla: **nadie la pidió todavía.**
Eso es más débil que un tope y es lo correcto — un experimento no se gobierna con plazos, se gobierna
con disparadores.

---

## (c) Composición de medidas — HECHO (rechazada)

**Cerrado el 2026-08-03** en
[`DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md`](DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md), con la
convención que ya usaba `DECISION-001`. Lo importante no es el rechazo: es que **una ausencia pasó a
ser una decisión**, con su disparador de reversión escrito.

El álgebra cierra sobre filas, no sobre medidas. Que una medida consuma los testigos de otra daría
clausura real y es tentador — y es **exactamente el modo de falla que el proyecto existe para
evitar**: permite que las medidas se cubran entre sí, y un conjunto internamente impecable y
colectivamente ciego deja de ser detectable incluso desde afuera.

Además choca con la regla propia del repositorio: nada entra al lenguaje hasta que una medida real lo
necesite. Hoy **ninguna** de las 18 lo necesita.

**Qué evidencia cambiaría la decisión:** dos medidas reales, en un proyecto consumidor —Jam es el
candidato—, que no se puedan expresar sin composición y cuya ausencia deje un hueco declarado en el
corpus. Dos, no una: es el mismo disparador que usaron `con` y la unión izquierda, que se retiraron
por no alcanzarlo.

Lo importante es que hoy es una **ausencia**, y debe pasar a ser una **decisión**.

---

## (e) El diferencial vacío — la pata que no rutea por vos

**El problema, exacto.** El README nombra tres señales que no le preguntan al LLM. Auditadas para
Oracle mismo: el **diferencial no tiene fixtures propios** (cero, por decisión declarada), la
**persona sos vos** —que también escribiste el corpus y los prompts— y la **mutación** corre sobre
cuatro mutadores que elegiste vos (`nucleo/mutacion.py:97`). «129/129 muertos» mide cobertura sobre un
espacio de mutación de autoría propia: un mutador que nadie escribió no puede producir un
sobreviviente.

No es que la arquitectura anti-Goodhart no sirva — es mejor que lo típico. Pero **angosta el cierre,
no lo rompe**, y el README debería decirlo así.

### e.1 — Metamórfico primero (barato, inmediato)

Propiedades que deben valer sin importar la implementación, verificables sobre la evidencia que ya
existe:

- `donde P` seguido de `donde Q` ≡ `donde ["y", P, Q]`
- `contar` después de `donde` ≤ `contar` antes
- `unir A B` ≡ `unir B A` salvo renombre de alias
- `agrupar` sin claves ≡ el resumen global
- toda medida por macro ≡ su expansión canónica escrita a mano

Esto no necesita una segunda implementación y ataja una clase entera de errores. Es lo primero.

### e.2 — Segunda implementación de verdad

El requisito real no es «otro código», es **otro autor**. Una implementación escrita por el mismo
modelo en la misma sesión, mirando `nucleo/algebra.py`, no es independiente de nada.

Operacionalmente: un evaluador mínimo del álgebra (~200 líneas) escrito **sólo a partir de
`ESPECIFICACION.md`**, por un agente que nunca ve `nucleo/`. Es verificable como restricción: se
declara qué archivos vio. Mejor todavía en otro lenguaje, porque impide compartir un camino de código
por accidente.

Producto: los fixtures `oracle.diferencial/v1` que hoy no existen, poblando `diferencial/`. Eso cierra
la pata estructuralmente vacía.

**Cómo sabemos que falló:** si la segunda implementación coincide en el 100% desde la primera corrida,
casi seguro no es independiente — miró algo que no debía.

---

## Orden y criterio global

1. ~~**(d)**~~ **HECHO el 2026-08-03.** Baseline restaurado; 158 errores de arnés → 0.
2. ~~**(c)**~~ **HECHO el 2026-08-03.** Rechazada y registrada en `DECISION-002`.
3. ~~**(a)** — `defmacro`.~~ **HECHO el 2026-08-03.** Criterio cumplido; la proporción subió en vez
   de bajar (ver arriba).
4. ~~**(e.2)** — segunda implementación.~~ **HECHO el 2026-08-24**, y antes que (e.1) contra lo que
   este orden predecía. Tres implementaciones independientes escritas sólo desde `ESPECIFICACION.md`,
   por agentes que nunca vieron `nucleo/`; la de Codex quedó versionada en `diferencial/referencia/`
   con su procedencia declarada. `diferencial/` dejó de estar vacío.

   Encontró lo que tenía que encontrar: sobre los 39 casos del corpus las cuatro implementaciones
   coincidían en todo —**el corpus no hace ninguna pregunta difícil**— y los desacuerdos aparecieron
   recién con 26 sondas dirigidas a los rincones que los propios autores declararon ambiguos. Uno de
   esos desacuerdos era un defecto real de `nucleo/`: los lógicos cortocircuitaban, así que un campo
   mal escrito dentro de un `y` devolvía un `False` silencioso — el verde que §3 prohíbe.

5. **(e.1)** — propiedades metamórficas. **PARCIAL al 2026-08-24**, y conviene el detalle:
   de las cinco listadas arriba está implementada **una** —«`contar` después de `donde` ≤ `contar`
   antes», como `meta.donde_nunca_agrega_filas`—. Las otras cuatro siguen pendientes: la composición
   de dos `donde`, la conmutatividad de `unir`, `agrupar` sin claves ≡ el resumen global, y la
   equivalencia de una macro con su expansión canónica.

   A cambio entraron tres que esta lista no tenía, porque las pidió la traza y no la teoría:
   `agrupar_no_agranda_la_relacion`, `unir_materializa_el_producto` y
   `los_logicos_evaluan_todos_sus_operandos`. Las cuatro se verificaron inyectando el defecto que
   cada una debe atrapar, y las juzgan las DOS implementaciones: un desacuerdo hace fallar la corrida.

6. **(b)** — reificación. **Congelado tras un disparador** (ver arriba). Es el más caro, es el que
   justifica la palabra «metalenguaje», y nadie lo pidió todavía: los dos consumidores suman 47
   medidas y ninguna es meta.

### La medición que gobierna todo esto

**La proporción — la cifra viva está en el README, no acá.** Este documento es un registro fechado y
copiar el número otra vez sería garantizarle una tercera deriva: ya publicó 17,6 y 18,0 a la vez.

Lo que sí se puede fijar es el movimiento, porque ya ocurrió: (a) la subió —contra lo que este plan
predecía—, y al 2026-08-24 había vuelto a donde estaba antes de `defmacro`. **Ni mejoró ni empeoró**,
y las dos veces que se movió fue por escribir núcleo o por escribir medidas universales. Nunca por un
consumidor, y ahí está el problema: el movimiento real llegaría cuando **los catálogos crezcan sin
que crezca el núcleo**, y eso esta métrica no lo puede ver — los catálogos externos no entran a su
denominador. Tampoco lo ve la migración: mover una política real de Python al catálogo bajó el núcleo
tres líneas y la cifra no se movió.

Por eso desde el 2026-08-24 esta proporción **no es un criterio de falsación**: es una cifra sobre el
costo. El proyecto está en estado EXPERIMENTAL y no tiene criterio de cierre — ver el README.

Y ahí está el experimento que importa: **Jam es el primer consumidor que no se diseñó junto con
Oracle.** El criterio es mecánico y no admite interpretación —

> si conectar Jam exige tocar `nucleo/algebra.py`, la apuesta está perdiendo.

Anotar la proporción antes de empezar con Jam y volver a mirarla después. Es la única medición del
proyecto que no se puede sastrear escribiendo más medidas.
