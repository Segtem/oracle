# oracle

**Un modo de estructurar el problema de construir herramientas con un LLM.**

No es una biblioteca de verificadores. Es un lenguaje para enunciar *medidas* sobre lo que un
generador produjo —y sobre el proceso que lo produjo— de forma que el generador no pueda convertir
el criterio de éxito en el objetivo.

El problema que resuelve tiene nombre: **Goodhart**. Cuando el que construye la herramienta es el
mismo que escribe su verificador, el verificador tiende a preguntar lo que la herramienta ya contesta
bien. Con un LLM el efecto es más fuerte, por dos razones estructurales:

- escribe la herramienta y su test **con la misma mano**, en el mismo acto;
- **no tiene memoria entre sesiones**: sólo existe lo que quedó en el repositorio. Una regla escrita
  como consejo se lee y se olvida. Tiene que **negarse**.

De ahí la forma de todo lo que hay acá: las reglas son programas que fallan, no documentos que
aconsejan.

## La esencia, mirada de cerca

Después de construirlo, lo que queda debajo de todos los mecanismos es una sola frase:

> **Ninguna afirmación vale por sí sola. Tampoco la que dice «esto está verificado».**

Cada pieza es una respuesta a *«¿por qué debería creerte?»* sobre una clase distinta de afirmación:

| La afirmación | Qué se le exige |
|---|---|
| «está bien» | contra qué medida, con qué umbral, y **qué no miró** |
| «el test lo cubre» | ¿qué mutante lo mata? |
| «corrió verde» | en qué commit, y ¿cambió el código desde entonces? |
| «esta medida sirve» | ¿qué caso la pone roja? ¿y qué caso la pone verde? |
| «el marco funciona» | ¿qué medida lo dice? |

### Su naturaleza es negarse

No es un instrumento de medición: es un instrumento de **rechazo**. En este corte hay 2202 líneas de
núcleo y **106 negativas explícitas** (`raise`). No calcula calidad: **declina dejar pasar** lo que no
se puede sostener.

Un umbral sin defensa no se carga. Una medida sin `alcance` no se carga. Un campo ausente no da
`False`, levanta error. La igualdad exacta entre flotantes está prohibida, incluido el umbral final.
Un dominio sin defectos
declarados no genera fixture. Una medida que no discrimina se denuncia sola.

### Lo que produce no es confianza: es confianza ACOTADA

El veredicto no es el producto — el **punto ciego** lo es. Un informe verde termina enumerando lo que
no miró, y eso es lo que lo hace usable: un «todo bien» sin su alcance no se puede accionar, porque no
se sabe sobre qué se está callando.

### La asimetría, medida

De los 28 defectos reales del corpus: **25 falsos verdes, 2 falsos rojos y 1 conclusión causal
incorrecta pese a una medida correcta**. Ésa es la justificación empírica de cada decisión de
«negarse antes que permitir». Pero un falso rojo enseña a ignorar el verificador, y por eso pesa igual
de grave: en un solo día lo cometí tres veces.

### El sujeto es el que construye, no lo construido

**33 de los 42 casos del corpus son sobre el propio trabajo**, no sobre el artefacto. Los 30 casos no
observacionales salieron a la luz por vías que no aceptan el verde nominal: 17 la mutación, 8 una persona, 4 la
casualidad y 1 una herramienta ajena. Oracle no es un juez de artefactos — es una prótesis para alguien
que escribe la herramienta y su test con la misma mano y no recuerda ayer.

### El costo, dicho

**2202 líneas de lenguaje.** Contra las medidas escritas en él: **trece a uno** si se cuenta sólo el
catálogo base, **seis a uno** contando las medidas de Jam. Ésa es la apuesta y ésa es la
métrica: que el segundo número crezca y el primero no.

*(El núcleo y el catálogo base los mide `python tools/estudio.py`; la razón con Jam usa el mismo
conteo directo de líneas. Dos veces los afirmé de memoria y las dos estaban mal — la proporción base
la dije «treinta a uno» cuando el catálogo tenía la mitad de las medidas que tiene hoy.)*

Es la única medición del proyecto **que no se puede sastrear escribiendo más medidas** — escribir más
medidas es justamente lo que la mejora. Si en seis meses la proporción no se movió, el lenguaje no
valió la pena.

### Y la historia lo dice mejor que el código

En el historial, **cerca de la mitad de los commits tienen por título la corrección de algo que yo
mismo había afirmado**: un criterio imposible de cumplir, un corpus al que le faltaba una polaridad, 53 tests en
verde conviviendo con 88 mutantes vivos, un concepto de juego metido en el núcleo, una guía que
describía un problema ya resuelto. El repositorio es, sobre todo, **el registro de un autor
equivocándose y siendo atrapado por lo que estaba construyendo**. Que eso sea legible es la única
prueba de que funciona.

## Tres influencias, y qué aporta cada una

| | Qué aporta |
|---|---|
| **SQL** | el álgebra: relaciones entran, relaciones salen — clausura sobre la evidencia |
| **GPSS** | la segunda fuente de evidencia: simulá el sistema y medí lo que emergió |
| **LISP** | la representación: la medida **es un dato** ⇒ el lenguaje se extiende desde adentro |

Los tres se necesitan. Sin el álgebra no compone. Sin la simulación sólo juzga lo estático. **Sin la
homoiconicidad el lenguaje tiene dueño** — y el dueño sería el LLM, que es exactamente el problema.

## El norte

**Todo el universo de problemas que tienen que ver con crear una herramienta.** Verificar lo que la
herramienta produce es una parte; las otras son saber qué NO cubre, si los tests la fijan, si el
corpus fija las medidas, si una afirmación de verde tiene detrás algo que se pueda reproducir, y si
la entrega a quien sigue deja todo eso en pie.

Una parte de ese universo es **la herramienta misma**, y por eso el marco se mide con sus propias
medidas: `meta.toda_medida_esta_ejercitada`, `meta.toda_medida_esta_fijada`,
`meta.el_caso_se_pone_como_debe`. Antes eso eran `if`s dentro de `tools/` — el veredicto sobre el
marco en código imperativo, mientras el resto del proyecto exige que los veredictos sean datos.

## Tres niveles, una sola representación

```
L0   evidencia            pieza(id, aabb) · mutante(id, apunta_a, murio) · evento(t, actor, qué)
L1   medidas              enunciados sobre L0
L2   medidas sobre medidas enunciados sobre L1
```

Lo que lo vuelve un metalenguaje no es tener L2: es que **L2 no necesita mecanismo propio**. Es L1
apuntado a L1.

## Lo que una medida declara, siempre

```
medición   un escalar del mundo
umbral     una comparación — con su DEFENSA escrita
testigos   las filas que ofenden  (no se calculan aparte: son las que pasaron el filtro)
alcance    qué NO ve esta medida  ← OBLIGATORIO
```

`alcance` es obligatorio porque un verificador que dice «TODO VERDE» enseña a confiar en él más de lo
que merece. Acá un informe en verde **termina enumerando lo que no miró**.

El umbral lleva su defensa por el mismo motivo: un número que nadie puede discutir es una métrica
esperando a volverse objetivo.

## Lo que NO es

- **No es un framework de tests.** `pytest` verifica *código*; esto verifica *artefactos producidos*
  y *el proceso que los produjo*.
- **No es un validador de esquema.** Que la evidencia esté bien formada no dice nada sobre si el
  mundo está bien. Forma y verdad son dos capas y no se tocan.
- **No es un linter.** Un linter lee la fuente; esto lee la salida.
- El pariente cercano es el mundo de los **evals**: medir salida generada contra criterios
  declarados, con corpus y etiquetas humanas. La diferencia es que acá **el punto ciego es ciudadano
  de primera clase**.

## Lo que un metalenguaje no da

**No da verdad.** Puede enunciar «esta medida no tiene defensa para su umbral». No puede decir si
0,5 cm es el número correcto.

**No saca de Goodhart por sí solo.** Vuelve las medidas inspeccionables, no correctas. Un conjunto de
medidas puede ser internamente impecable y colectivamente ciego, y ninguna cantidad de reflexión lo
detecta desde adentro. **Un verificador no se verifica a sí mismo.**

La salida son tres señales que no le preguntan al LLM: la **mutación** (mecánica, no opina), la
**prueba diferencial** contra una implementación independiente, y **una persona** que dice «esto está
mal» cuando el verde no se movió.

## La herramienta y el proyecto

Oracle **no tiene dominios**. Los dominios son de quien construye:

```
oracle/                        LA HERRAMIENTA
  nucleo/                      el álgebra, la medida, las macros, el dominio, la simulación
  perfiles/python/             AST, imports, mutación de `.py` y garantías de `.pyc`
  tools/                       los instrumentos
  catalogos/                   sólo medidas UNIVERSALES: proceso · meta · simulacion
  corpus/                      los casos donde la medición dijo bien y no estaba bien
  ejemplo/                     un banco de pruebas abstracto, no un dominio

<tu-proyecto>/                 TU PROYECTO
  oracle.json                  perfiles optativos activados de forma explícita
  catalogos/<dominio>/         tus medidas
  escalares.py                 tus funciones de dominio
  corpus/  diferencial/        tus casos y tus fixtures
```

Y las herramientas se apuntan:

```bash
python <oracle>/tools/diferencial.py --proyecto <tu-proyecto> --confiar-escalares
python <oracle>/tools/aceptacion.py  --proyecto <tu-proyecto> --confiar-escalares
python <oracle>/tools/mutar.py       --proyecto <tu-proyecto> --confiar-escalares
python <oracle>/tools/estudio.py --proyecto <tu-proyecto> --confiar-escalares
export ORACLE_PROYECTO=<tu-proyecto>     # para no repetirlo
```

Cada comando exige las carpetas que consume. Ninguno ejecuta un `escalares.py` externo salvo que se
confirme con `--confiar-escalares`: una UDF es código Python y tiene los permisos del proceso. Ayuda,
`--relaciones`, `--nueva` y `--escalares` sin confianza son inspecciones seguras; esta última muestra
el inventario base y avisa que omitió las UDF externas.

**El catálogo base viene incluido.** Las medidas de `proceso`, `meta` y `simulacion` valen para
cualquiera que construya con un LLM —mutantes que sobreviven, afirmaciones sin alcance, verificaciones
vencidas, corridas irreproducibles— y se cargan junto a las tuyas. Que vengan de fábrica es la
diferencia entre una herramienta y un repositorio de ejemplos.

Los supuestos de plataforma no vienen implícitos. Para analizar imports con AST, mutar `.py` y
comprobar cachés de CPython, el proyecto lo declara:

```json
{"esquema": "oracle.proyecto/v1", "perfiles": ["python"]}
```

Sin `oracle.json`, sólo se carga el catálogo universal. Un perfil desconocido o repetido falla
cerrado. El propio Oracle declara `python` porque usa ese perfil para probarse.

Los dominios que estuvieron acá durante el desarrollo —geometría, vault, relevo, una cola, un
laberinto— se fueron a los proyectos que los usan. Eran instancias, y acumularlas era la tentación de
no abstraer.

## Estado

> **Estado auditado el 2026-07-30; P2.2 cerrado.** Los bypasses de simulación, baseline, caché,
> equivalentes y verdes vacuos tienen regresiones fail-closed; timeout y error del arnés son estados
> distintos de una muerte. P2.1 ya aísla la mutación de código en una copia, con bloqueo,
> subprocesos acotados y reanudación verificable. Ver
> [`AUDITORIA-2026-07-30.md`](AUDITORIA-2026-07-30.md) y
> [`PLAN-CORRECCION.md`](PLAN-CORRECCION.md).

**El prototipo contiene los cinco componentes.** El [corpus](corpus/) (42 casos), la [especificación](ESPECIFICACION.md) del álgebra,
el evaluador (`nucleo/`), **las medidas universales** dentro de [`catalogos/`](catalogos/) —como
archivos de datos, no como código—, el sensor de mutación y la prueba diferencial.

**¿Querés escribir una medida?** → [`ESCRIBIR-UNA-MEDIDA.md`](ESCRIBIR-UNA-MEDIDA.md).
`python tools/medida.py --relaciones` te dice qué hechos hay para medir; `--nueva` crea el archivo.

```bash
python tools/medida.py --relaciones              # qué se puede medir, derivado de la evidencia real
python tools/corpus.py --resumen                 # el corpus está en regla
python tools/aceptacion.py                       # el corpus juzga al oráculo
python tools/diferencial.py                      # el álgebra vs una implementación independiente
python tools/mutar.py                            # ¿el corpus ALCANZA para fijar las medidas?
python -m unittest discover -s tests -t . -q     # 235 tests, cero dependencias
```

27 defectos en rojo · 12 verdes correctos · 0 huecos abiertos · 2 casos resueltos conservados ·
1 límite humano · **269 acuerdos globales de Jam
con referencias independientes y 1158 veredictos individuales estables** · 129/129 mutantes de
medida · 235 tests.

> **`tools/mutar_codigo.py` sigue saliendo en ROJO.** La mutación de medidas volvió a verde sin
> reducir el denominador: ocho casos mínimos fijaron los bordes de umbral y dos fijaron mutaciones
> internas. El baseline de código completo y particionado dejó 503/616 mutantes muertos y 113 vivos,
> sin timeout ni error de arnés. Las rondas actuales crean su propia copia automáticamente y pueden
> persistir progreso con `--manifiesto`/`--reanudar`.
> Se podrían declarar equivalentes en masa para
> pintar verde — y eso sería exactamente el Goodhart que este repositorio persigue. El número baja
> escribiendo tests o declarando equivalentes **de a uno y con su razón escrita**.

### Dos dominios, un álgebra

Es el criterio que decide si esto es general o si es una cosa disfrazada de otra:

| Dominio | Qué mide | Cómo se verifica |
|---|---|---|
| **proceso** | un agente construyendo herramientas: mutantes, afirmaciones, verificaciones vencidas | el corpus de fallas reales |
| **geometría** | piezas en un nivel: interpenetración, bounds, snap a grilla y yaw | 250 escenarios globales contra los oráculos escritos a mano de Jam |
| **vault** | la documentación de un proyecto: convención de nombres, coherencia del frontmatter, enlaces | 11 escenarios globales contra `tools/vault.py` de Jam |
| **relevo** | la entrega de un turno entre dos agentes: testigo completo, agentes conocidos, verificación reproducible | 8 escenarios globales contra `tools/relevo.py` |
| **cola** | un sistema con recursos limitados: rechazos, esperas — el caso canónico de GPSS | corridas reales de `simuladores/cola.py` |
| **laberinto** | recorrer una topología con información parcial y presupuesto finito | corridas reales, y la invariante de que nadie alcanza lo que no tiene camino |

No se parecen en nada, y usan **los mismos operadores sin un solo adaptador**.

La prueba más limpia de que el álgebra cierra: `proceso.verificacion_vigente` se escribió para un caso
del corpus, y **juzgó los hechos del sensor de relevo sin una sola modificación**. La misma medida, dos
sensores distintos, dominios distintos. La prueba diferencial
la genera Jam (`tools/emitir_diferencial.py`) con código que no comparte una línea con este álgebra;
lo único que viaja entre los repos es un archivo de hechos.

Esos archivos usan `oracle.diferencial/v1`. Guardan SHA-256 del emisor, las fuentes de referencia, el
catálogo canónico y la configuración; si alguno cambia, el fixture queda vencido antes de evaluarse.
`referencia_ok` es el acuerdo global independiente. `oracle_al_generar.por_medida` es una fotografía
individual para detectar regresiones compensadas: no se presentan como la misma clase de evidencia.

### El bucle cerrado

`tools/mutar.py` muta las **medidas** —que son datos, así que no se toca ningún archivo y no hay
`.pyc` que pueda quedar viejo— y produce hechos `mutante(id, apunta_a, murio)`. Esos hechos los juzga
**una medida del catálogo**, `proceso.test_con_mutante_que_lo_mata`. El sensor no dicta veredictos:
produce evidencia, y el álgebra la mide.

P1.1 amplió el denominador desde cuatro transformaciones gruesas a **128 mutantes localizados** sobre
umbral, filtros, fuentes, expresiones, agregados y campos. La primera ronda mató 118 y expuso diez
libertades que el anterior 48/48 no miraba. Ocho reducciones mínimas fijaron los límites justo en el
borde; otros dos casos fijaron el comparador interno de `proceso.modulo_con_consumidor` y el `max` de
`proceso.modulo_alcanzable`. P2.2 retiró una regla textual normativa y cambió el contrato de
terminación; el denominador actual mata **129/129**.

### Modo simulación: la segunda fuente de evidencia

Las primeras cuatro familias consultan **hechos estáticos**. `nucleo/simulacion.py` agrega la otra
mitad —la de GPSS—: **correr el sistema y medir lo que emerge**. Y no necesita álgebra nueva, porque
una traza es una relación:

```
evento(corrida, t, actor, que, …)                          lo que fue pasando
corrida(id, escenario, semilla, pasos, razon, presupuesto_agotado, determinista) cómo terminó
```

**El contrato no tiene ningún campo de veredicto.** La primera versión traía `gano: bool` y eso era
un concepto de juego metido adentro del núcleo: un simulador de una cola no «gana», termina por una
razón. Si esa razón está bien lo dice una medida. El dominio es indiferente — una cola con
servidores, un recorrido sobre una topología, o los turnos de dos agentes trabajando un repositorio.
Las razones siguen perteneciendo al dominio: `ContratoTerminacion` declara cuáles significan que el
presupuesto se agotó; el runner no contiene una razón literal privilegiada.

**El determinismo se comprueba, no se promete.** Cada corrida se ejecuta **dos veces** con la misma
semilla y `determinista` es un hecho más. Una corrida irreproducible no es evidencia: es una anécdota.

Y produce el desacuerdo que ningún oráculo de propiedad puede ver: **«existe» y «se llega» no son lo
mismo**. Un BFS con información perfecta dice que hay camino; un recorrido con visión local y
presupuesto finito termina por «tope». Los dos tienen razón, y el segundo es el que importa.

### Las dos polaridades del corpus

La primera corrida del sensor dejó 10 sobrevivientes, casi todos del mutador `quitar_filtro`. La
causa no era el código: **el corpus tenía sólo defectos**. Con `contar` y umbral `<= 0`, una medida
sin filtro sólo da verde si la relación está vacía, así que ningún caso de defecto puede notar que le
saquen el filtro. Hace falta la otra polaridad — evidencia real donde la medida **debe** decir verde.

Es lo mismo que evaluar un clasificador sólo con positivos. Hoy hay 12 casos `verde_correcto`.

**Corrección, dos pasos después.** Cuando el catálogo de geometría trajo el patrón
«`donde tol` → `resumen max` → `umbral tol`», aparecieron dos sobrevivientes que eran **mutantes
equivalentes**: quitar ese filtro no puede cambiar el veredicto nunca —si nada supera la tolerancia el
máximo sin filtrar sigue por debajo, y si algo la supera sigue por encima—. Sí cambia **los
testigos**.

De ahí que el sensor compare **veredicto Y testigos**: los testigos son lo que una persona lee para
actuar, así que el informe también es contrato. La ampliación de P1.1 volvió más precisa la regla:
`quitar_filtro` suele necesitar un verde, `aflojar_umbral` necesita un rojo junto al límite y las
mutaciones internas pueden necesitar combinaciones que ejerciten cada término. Los casos verdes son
además lo único que ataja una medida que se pone roja con entrada correcta, el modo de falla del caso
`008`.

**Las macros ya existen** — el disparador que la especificación pedía («cuando aparezca la quinta
medida con la misma forma») sonó con **22**. `ninguno`, `ninguno-par` y `peor` cubren 26 de las 27
medidas, expanden a la forma canónica, y `peor` cerró por construcción la deuda del umbral duplicado.

**El lenguaje activo tiene cinco operadores**: `de`, `donde`, `resumen`, `unir` y `agrupar`.
Cada uno entró al llegar su disparador. `con` y la unión izquierda se retiraron: sin dos usuarios
reales eran superficie ficticia, no capacidades.

**Las cuatro preguntas abiertas de la especificación están cerradas**, y sólo una amplió el álgebra:
la ausencia trajo `agrupar`. El orden resultó ser un campo del hecho; la recursión salió del álgebra
hacia el sensor (`alcanzable` es un hecho, no una consulta); y la igualdad exacta sobre flotantes se
resolvió **prohibiéndola** — `0.1 + 0.2` no es `0.3`, y una medida que compare así diría verde sin que
nadie se entere.

Con `agrupar` quedó resuelta la **ausencia** —«módulos que nadie usa de verdad»— y sin traer el
concepto de nulo: se agrupa sobre el producto sin filtrar y se suma un predicado, así que un grupo
donde nada casó da cero y sigue existiendo.

### Dos oráculos, y ninguno alcanza solo

La ronda de mutación dejó algo a la vista: de 6 mutantes del núcleo, los 6 mueren con los tests, pero
**3 dejan la aceptación en verde**. El replay del corpus ejercita la *evaluación*; las reglas de
*declaración* —que un umbral traiga defensa, que el alcance no esté vacío— sólo las cubren los tests.
Hacen falta los dos, y conviene no confundir el verde de uno con el del otro.

### Qué falta

- **Reemplazar de verdad los verificadores de Jam.** `vault.py` y `relevo.py` están re-expresados y
  verificados por diferencial, y **siguen en uso los originales**. El reemplazo va cuando el
  diferencial lleve tiempo en verde, no el mismo día en que se escribió — y menos `relevo.py`, que es
  la herramienta que abre y cierra los turnos.
- **Los 113 mutantes de código vivos**, de a uno: test discriminante o equivalencia individual con
  razón revisada.
- **Los 11 mutantes de medida vivos al aplicar el denominador P1.1 sobre Jam**: sus fixtures necesitan
  escenarios de borde y combinaciones discriminantes; no se corrigen debilitando el mutador.
- **La frontera humana del caso `011`**: la medición puede exigir trazabilidad, pero una atribución
  causal no tiene un verificador mecánico genérico. `004` y `012` ya figuran como resueltos y no
  inflan la deuda abierta.
- **Declarar los dos arneses que faltan** en el proyecto de Jam (`relevo`, `geometria`) con
  `nucleo.dominio`, como ya se hizo con `vault`.

## Por qué el corpus va primero

Porque es lo único que se pierde. Un LLM no recuerda sus fallas entre sesiones, y si el corpus se
escribe *después* del framework, se escribe para que pase. Los casos que hay acá se capturaron el
mismo día en que ocurrieron, antes de existir nada que los midiera.
