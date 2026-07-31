# Oracle — documento integral para NotebookLM

Fuente única de estudio del metalenguaje Oracle: propósito, semántica, autoría, catálogo,
corpus, arquitectura, herramientas, historia, decisiones, auditoría y plan de corrección.

- Generado: `2026-07-31`
- Revisión de código base: `e096a3751fc9`
- Partes incluidas: `12`

> Nota de lectura: la auditoría y el plan conservan cifras y hallazgos históricos para
> explicar cómo evolucionó Oracle. Cuando una cifra histórica difiera del estado actual,
> prevalecen «Los números» y «Estado» de las primeras partes, generados desde el checkout
> vigente.

## Orden sugerido

Leé primero la esencia, el álgebra y los números. Después recorré el catálogo y el corpus;
son la teoría puesta a prueba. El diario, la auditoría y el plan explican las alternativas
descartadas, los defectos encontrados y las fronteras que todavía no puede cerrar el código.

---

<!-- fuente: 00-esencia.md -->

## oracle — qué es y por qué


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

### La esencia, mirada de cerca

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

#### Su naturaleza es negarse

No es un instrumento de medición: es un instrumento de **rechazo**. En este corte hay 2202 líneas de
núcleo y **106 negativas explícitas** (`raise`). No calcula calidad: **declina dejar pasar** lo que no
se puede sostener.

Un umbral sin defensa no se carga. Una medida sin `alcance` no se carga. Un campo ausente no da
`False`, levanta error. La igualdad exacta entre flotantes está prohibida, incluido el umbral final.
Un dominio sin defectos
declarados no genera fixture. Una medida que no discrimina se denuncia sola.

#### Lo que produce no es confianza: es confianza ACOTADA

El veredicto no es el producto — el **punto ciego** lo es. Un informe verde termina enumerando lo que
no miró, y eso es lo que lo hace usable: un «todo bien» sin su alcance no se puede accionar, porque no
se sabe sobre qué se está callando.

#### La asimetría, medida

De los 28 defectos reales del corpus: **25 falsos verdes, 2 falsos rojos y 1 conclusión causal
incorrecta pese a una medida correcta**. Ésa es la justificación empírica de cada decisión de
«negarse antes que permitir». Pero un falso rojo enseña a ignorar el verificador, y por eso pesa igual
de grave: en un solo día lo cometí tres veces.

#### El sujeto es el que construye, no lo construido

**33 de los 42 casos del corpus son sobre el propio trabajo**, no sobre el artefacto. Los 30 casos no
observacionales salieron a la luz por vías que no aceptan el verde nominal: 17 la mutación, 8 una persona, 4 la
casualidad y 1 una herramienta ajena. Oracle no es un juez de artefactos — es una prótesis para alguien
que escribe la herramienta y su test con la misma mano y no recuerda ayer.

#### El costo, dicho

**2202 líneas de lenguaje.** Contra las medidas universales escritas en él: **trece a uno**. Ésa es
la apuesta y ésa es la métrica: que los catálogos de los proyectos crezcan sin hacer crecer el
metalenguaje. Los catálogos externos no se incorporan al núcleo para mejorar artificialmente la
proporción.

Es la única medición del proyecto **que no se puede sastrear escribiendo más medidas** — escribir más
medidas es justamente lo que la mejora. Si en seis meses la proporción no se movió, el lenguaje no
valió la pena.

#### Y la historia lo dice mejor que el código

En el historial, **cerca de la mitad de los commits tienen por título la corrección de algo que yo
mismo había afirmado**: un criterio imposible de cumplir, un corpus al que le faltaba una polaridad, 53 tests en
verde conviviendo con 88 mutantes vivos, un concepto de juego metido en el núcleo, una guía que
describía un problema ya resuelto. El repositorio es, sobre todo, **el registro de un autor
equivocándose y siendo atrapado por lo que estaba construyendo**. Que eso sea legible es la única
prueba de que funciona.

### Tres influencias, y qué aporta cada una

| | Qué aporta |
|---|---|
| **SQL** | el álgebra: relaciones entran, relaciones salen — clausura sobre la evidencia |
| **GPSS** | la segunda fuente de evidencia: simulá el sistema y medí lo que emergió |
| **LISP** | la representación: la medida **es un dato** ⇒ el lenguaje se extiende desde adentro |

Los tres se necesitan. Sin el álgebra no compone. Sin la simulación sólo juzga lo estático. **Sin la
homoiconicidad el lenguaje tiene dueño** — y el dueño sería el LLM, que es exactamente el problema.

### El norte

**Todo el universo de problemas que tienen que ver con crear una herramienta.** Verificar lo que la
herramienta produce es una parte; las otras son saber qué NO cubre, si los tests la fijan, si el
corpus fija las medidas, si una afirmación de verde tiene detrás algo que se pueda reproducir, y si
la entrega a quien sigue deja todo eso en pie.

Una parte de ese universo es **la herramienta misma**, y por eso el marco se mide con sus propias
medidas: `meta.toda_medida_esta_ejercitada`, `meta.toda_medida_esta_fijada`,
`meta.el_caso_se_pone_como_debe`. Antes eso eran `if`s dentro de `tools/` — el veredicto sobre el
marco en código imperativo, mientras el resto del proyecto exige que los veredictos sean datos.

### Tres niveles, una sola representación

```
L0   evidencia            pieza(id, aabb) · mutante(id, apunta_a, murio) · evento(t, actor, qué)
L1   medidas              enunciados sobre L0
L2   medidas sobre medidas enunciados sobre L1
```

Lo que lo vuelve un metalenguaje no es tener L2: es que **L2 no necesita mecanismo propio**. Es L1
apuntado a L1.

### Lo que una medida declara, siempre

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

### Lo que NO es

- **No es un framework de tests.** `pytest` verifica *código*; esto verifica *artefactos producidos*
  y *el proceso que los produjo*.
- **No es un validador de esquema.** Que la evidencia esté bien formada no dice nada sobre si el
  mundo está bien. Forma y verdad son dos capas y no se tocan.
- **No es un linter.** Un linter lee la fuente; esto lee la salida.
- El pariente cercano es el mundo de los **evals**: medir salida generada contra criterios
  declarados, con corpus y etiquetas humanas. La diferencia es que acá **el punto ciego es ciudadano
  de primera clase**.

### Lo que un metalenguaje no da

**No da verdad.** Puede enunciar «esta medida no tiene defensa para su umbral». No puede decir si
0,5 cm es el número correcto.

**No saca de Goodhart por sí solo.** Vuelve las medidas inspeccionables, no correctas. Un conjunto de
medidas puede ser internamente impecable y colectivamente ciego, y ninguna cantidad de reflexión lo
detecta desde adentro. **Un verificador no se verifica a sí mismo.**

La salida son tres señales que no le preguntan al LLM: la **mutación** (mecánica, no opina), la
**prueba diferencial** contra una implementación independiente, y **una persona** que dice «esto está
mal» cuando el verde no se movió.

### La herramienta y el proyecto

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

**El motor no impone políticas.** Las medidas incluidas de `proceso`, `meta` y `simulacion` sirven
para proyectos construidos con un LLM —mutantes que sobreviven, afirmaciones sin alcance,
verificaciones vencidas, corridas irreproducibles—, pero sólo se cargan si el proyecto las pide con
`"catalogo_base": true`.

Los supuestos de plataforma no vienen implícitos. Para analizar imports con AST, mutar `.py` y
comprobar cachés de CPython, el proyecto lo declara:

```json
{
  "esquema": "oracle.proyecto/v1",
  "perfiles": ["python"],
  "catalogo_base": true
}
```

Sin `oracle.json`, se carga únicamente el catálogo del proyecto. Un perfil desconocido o repetido
falla cerrado. El propio Oracle activa el catálogo base y `python` explícitamente porque los usa para
autocertificarse; esa elección no se hereda a ningún consumidor.

Los dominios que estuvieron acá durante el desarrollo —geometría, vault, relevo, una cola, un
laberinto— se fueron a los proyectos que los usan. Eran instancias, y acumularlas era la tentación de
no abstraer.

### Estado

> **Estado auditado el 2026-07-31; P3 de embedding cerrado del lado de Oracle.** Los bypasses de simulación, baseline, caché,
> equivalentes y verdes vacuos tienen regresiones fail-closed; timeout y error del arnés son estados
> distintos de una muerte. P2.1 ya aísla la mutación de código en una copia, con bloqueo,
> subprocesos acotados y reanudación verificable. Ver
> `AUDITORIA-2026-07-30.md` y
> `PLAN-CORRECCION.md`.

**El paquete contiene los cinco componentes.** El corpus (42 casos), la especificación del álgebra,
el evaluador (`nucleo/`), **las medidas universales** dentro de `catalogos/` —como
archivos de datos, no como código—, el sensor de mutación y la prueba diferencial.

**¿Querés escribir una medida?** → `ESCRIBIR-UNA-MEDIDA.md`.
`python tools/medida.py --relaciones` te dice qué hechos hay para medir; `--nueva` crea el archivo.

Requiere Python 3.11 o posterior. Se puede usar desde el checkout o instalar sin dependencias:

```bash
python -m pip install .
oracle-medida --proyecto /ruta/al/proyecto --relaciones
```

El wheel instala sólo paquetes bajo `oracle_metalenguaje.*`; no ocupa los nombres genéricos
`nucleo`, `catalogos`, `perfiles` ni `tools`. Tampoco distribuye el corpus ni los fixtures de
autocertificación del checkout. Por eso un comando instalado fuera de un proyecto siempre requiere
`--proyecto` (o `ORACLE_PROYECTO`) y falla con un diagnóstico breve si no lo recibe.

Como biblioteca, la frontera pública es `oracle_metalenguaje`; el consumidor no necesita importar
`nucleo`, `catalogos`, `perfiles` ni `tools`:

```python
from oracle_metalenguaje import Motor

motor = Motor.desde_proyecto("/ruta/al/proyecto", confiar_escalares=True)
informe = motor.evaluar({"item": [{"id": "a", "valor": 4}]})
print(informe.ok, informe.texto())
```

`confiar_escalares=True` ejecuta el `escalares.py` del proyecto y por eso nunca es implícito. Cada
motor conserva sus propios límites y UDF: dos proyectos pueden declarar el mismo nombre sin
sobrescribirse. `Motor.desde_datos(...)` y `Motor.desde_medidas(...)` cubren catálogos mantenidos en
memoria. Si ninguna medida puede consumir las relaciones entregadas, la API levanta
`SinMedidasAplicables` en vez de fabricar un informe verde vacío.

Un host puede aportar perfiles reutilizables sin escribir dentro de la instalación. Cada raíz tiene
la forma `<raíz>/<perfil>/catalogos`; `oracle.json` sólo selecciona el nombre y no puede inventarse
una ruta con autoridad propia:

```python
motor = Motor.desde_proyecto(
    "/ruta/al/proyecto",
    raices_perfiles=("/ruta/a/perfiles-del-host",),
)
```

Una raíz ausente o symlink y un nombre presente en dos fuentes se rechazan en vez de elegir por
orden accidental.

```bash
python tools/medida.py --relaciones              # qué se puede medir, derivado de la evidencia real
python tools/corpus.py --resumen                 # el corpus está en regla
python tools/aceptacion.py                       # el corpus juzga al oráculo
python tools/diferencial.py --proyecto <proyecto-con-fixtures>  # referencia independiente
python tools/mutar.py                            # ¿el corpus ALCANZA para fijar las medidas?
python -m unittest discover -s tests -t . -q     # suite sin dependencias
python tools/verificar_instalacion.py             # wheel + Motor desde un cwd vacío
```

Oracle no conserva fixtures diferenciales propios en este repositorio. Ejecutar el diferencial sin
fixtures devuelve estado no-verde; el flujo temporal de un proyecto externo prueba el camino
positivo. Esto evita convertir «no había nada que comparar» en una certificación accidental.

27 defectos en rojo · 12 verdes correctos · 0 huecos abiertos · 2 casos resueltos conservados ·
1 límite humano.

<!-- cifras:inicio -->
339 tests · 129/129 mutantes de medida · **1131 sitios de mutación de código** (926 + 205 del motor Python).
<!-- cifras:fin -->

> **`tools/mutar_codigo.py` sale en VERDE.** El baseline histórico 503/616 quedó invalidado cuando
> cambió la arquitectura. El denominador vigente incluye núcleo y perfiles: 868/868 sitios de las
> doce particiones previas y 205/205 del motor Python: **1073/1073**, sin timeout, error de arnés ni equivalentes
> declarados. Cada ronda muta una copia, puede persistir progreso con
> `--manifiesto`/`--reanudar` y firma también sus tests y archivos de soporte.

#### Tres dominios, un álgebra

Es el criterio que decide si esto es general o si es una cosa disfrazada de otra:

| Dominio | Qué mide | Cómo se verifica |
|---|---|---|
| **proceso** | un agente construyendo herramientas: mutantes, afirmaciones, verificaciones vencidas | el corpus de fallas reales |
| **simulación** | corridas, trazas, presupuesto y reproducibilidad | contratos del runner y corpus de trazas |
| **demo externo** | items buenos/malos con una UDF propia | flujo temporal completo fuera del árbol de Oracle |

No se parecen en nada, y usan **los mismos operadores sin un solo adaptador**.

La prueba más limpia de que el álgebra cierra es el proyecto externo temporal de integración: define
su catálogo, corpus, fixtures y una UDF sin modificar Oracle, y completa autoría, aceptación,
diferencial, mutación de medidas y estudio. Lo único que cruza la frontera son hechos y declaraciones.

Esos archivos usan `oracle.diferencial/v1`. Guardan SHA-256 del emisor, las fuentes de referencia, el
catálogo canónico y la configuración; si alguno cambia, el fixture queda vencido antes de evaluarse.
`referencia_ok` es el acuerdo global independiente. `oracle_al_generar.por_medida` es una fotografía
individual para detectar regresiones compensadas: no se presentan como la misma clase de evidencia.

#### El bucle cerrado

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

#### Modo simulación: la segunda fuente de evidencia

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

#### Las dos polaridades del corpus

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

#### Dos oráculos, y ninguno alcanza solo

La ronda de mutación dejó algo a la vista: de 6 mutantes del núcleo, los 6 mueren con los tests, pero
**3 dejan la aceptación en verde**. El replay del corpus ejercita la *evaluación*; las reglas de
*declaración* —que un umbral traiga defensa, que el alcance no esté vacío— sólo las cubren los tests.
Hacen falta los dos, y conviene no confundir el verde de uno con el del otro.

#### Qué falta

- **Elegir una licencia.** El paquete, entry points y CI ya existen, pero la decisión legal no se
  infiere del código ni la toma el agente por el autor.
- **Un consumidor real independiente.** El proyecto externo sintético demuestra desacoplamiento
  técnico; la adopción por un proyecto no diseñado junto con Oracle sigue siendo evidencia externa,
  no algo que este repositorio pueda fabricar.
- **La frontera humana del caso `011`**: la medición puede exigir trazabilidad, pero una atribución
  causal no tiene un verificador mecánico genérico. `004` y `012` ya figuran como resueltos y no
  inflan la deuda abierta.

### Por qué el corpus va primero

Porque es lo único que se pierde. Un LLM no recuerda sus fallas entre sesiones, y si el corpus se
escribe *después* del framework, se escribe para que pase. Los casos que hay acá se capturaron el
mismo día en que ocurrieron, antes de existir nada que los midiera.

---

<!-- fuente: 01-el-algebra.md -->

## Especificación del álgebra

Versión `0.3`. **Escrita para ser rota**: el criterio de si sirve está al final, y es comprobable.

> **Qué cambió respecto de `0.1`, y por qué.** La implementación encontró dos cosas.
> **(a)** El acceso a datos pasó a ser **explícito** (`["campo", alias, nombre]`, `["hecho", alias]`)
> en vez de la forma corta `["penetracion", "a", "b"]` que publicaba la 0.1: si un string suelto
> significara «alias», un dato de texto que coincida con un alias cambiaría de sentido según el
> contexto. Es más verboso y no tiene casos raros.
> **(b)** Los operadores se incorporan sólo cuando los piden medidas reales. `con` y la unión
> izquierda se retiraron de la especificación activa al no alcanzar dos usuarios — ver §3.
> **(c)** La 0.3 resuelve la contradicción entre “conjunto” y la multiplicidad real: una relación es
> una **bolsa sin orden semántico**. La decisión completa está en
> [`DECISION-001-RELACIONES-COMO-BOLSAS.md`](DECISION-001-RELACIONES-COMO-BOLSAS.md).

Regla de diseño que gobierna todo el documento: **no se agrega un operador hasta que una segunda
medida lo necesite.** Es lo único que evita que esto se vuelva el proyecto que reemplaza al proyecto.

---

### 1. Hechos y relaciones (L0)

Un **hecho** es un registro de campos escalares. Una **relación** es una bolsa nombrada de hechos del
mismo tipo. La evidencia es un mapa de relaciones:

```json
{
  "pieza":   [{"id": "Muro_A", "x": 100, "y": 100, "ex": 200, "ey": 25}],
  "mutante": [{"id": "firma_por_id", "apunta_a": "funcion._orden_visual", "murio": false}]
}
```

Nada más. Sin objetos, sin punteros, sin nulos implícitos. El **sensor** que produce la evidencia es
específico de cada dominio y vive con el productor, no acá.

La multiplicidad cuenta y el orden de almacenamiento no. Dos apariciones idénticas son dos hechos:
`contar` devuelve 2, `suma` usa ambas y un producto conserva ambas. Oracle no deduplica porque no
puede inventar una identidad genérica; la unicidad, cuando importa, se produce o se mide con una
clave explícita.

### 2. Una medida es un dato

```json
["medida", "colocacion.interpenetracion",
  ["desde",
    ["unir", ["de", "pieza", "a"], ["de", "pieza", "b"]],
    ["donde", [">", ["penetracion", ["hecho", "a"], ["hecho", "b"]], 0]]],
  ["resumen", "max", ["penetracion", ["hecho", "a"], ["hecho", "b"]]],
  ["umbral", "<=", 0, "penetracion() ya descuenta la tolerancia de contacto"],
  ["alcance", "solape de AABB. NO ve la malla real, ni oclusión, ni si quedó flotando"]]
```

Una medida real, del catálogo que ya corre — sin `unir`, que todavía no tiene usuario:

```json
["medida", "proceso.test_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"], ["donde", ["==", ["campo", "m", "murio"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina…"],
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
defensas ni alcances: las dos primeras fallan al cargar y las dos últimas se miden en L2.

**Los testigos no se declaran.** Son las filas que sobrevivieron al último `donde`. Declararlos
aparte obliga a recorrer los datos dos veces y a mantener dos definiciones de lo mismo sincronizadas
a mano — el error concreto que motivó esta especificación (ver
[`004-testigos-duplicados`](corpus/proceso/)).

### 3. Los operadores

Cinco. Cada uno toma relaciones y devuelve una relación: **eso es la clausura**, y es lo que permite
que una medida consuma la salida de otra sin ningún caso especial.

| Operador | Forma | Qué hace |
|---|---|---|
| `de` | `["de", relación, alias]` | fuente |
| `donde` | `["donde", pred]` | filtra — **define los testigos** |
| `unir` | `["unir", izq, der]` | producto cartesiano |
| `agrupar` | `["agrupar", [claves], [nombre, agg, expr]]` | agrupa y agrega |
| `resumen` | `["resumen", agg, expr]` | colapsa a un escalar — **la medición** |

Agregados: `max`, `min`, `suma`, `promedio`, `contar`. `contar` **no evalúa la expresión**: cuenta
filas. Los agregados sobre cero filas dan `0`. `suma` y `promedio` aceptan números finitos y
booleanos como indicadores 0/1; `min` y `max` exigen escalares homogéneos y comparables. Un valor no
finito o una mezcla incompatible es error de álgebra, no un veredicto.

`desde` no es un operador: es la tubería que los encadena (`["desde", fuente, paso, paso, …]`).

#### Lenguaje activo: cinco operadores

La regla *no se agrega un operador hasta que una segunda medida lo necesite* aplica también a
**publicarlos**: un operador sin usuario es un operador sin verificar. Corren `de`, `donde`,
`resumen`, `unir` y `agrupar`.

| Operador | Estado |
|---|---|
| `unir` | ✅ entró con el catálogo de geometría: «pares de piezas que se clavan» es un producto |
| `agrupar` | ✅ entró con la AUSENCIA — ver §8 |

`con` y la unión izquierda no son promesas pendientes ni sintaxis aceptada: no tienen dos usuarios
reales y por eso una declaración que los use falla al cargar. Si aparecen esos usuarios, vuelven con
sus casos, semántica y mutantes; no como ramas dormidas.

Un grupo **no es un hecho**: es un resumen. Las filas que salen de `agrupar` no llevan alias —los
hechos se consumieron— sino columnas derivadas, que se leen con `["col", nombre]`. Ese accesor existía
desde el principio y recién acá encontró su usuario.

#### Acceso a los datos

Explícito siempre: `["campo", alias, nombre]` para un campo, `["hecho", alias]` para el hecho entero,
`["col", nombre]` para una columna derivada. Todo lo demás en posición de expresión es un **literal**.

Comparar contra un campo ausente **levanta un error**, no devuelve `False`: en una medida eso es casi
siempre un nombre mal escrito, y un `False` silencioso lo convertiría en un verde.

#### Funciones escalares

Los predicados de dominio (`penetracion`, `distancia`, `desvio_de_grilla`) entran como **funciones
escalares declaradas**, con nombre, aridad y unidad. Es el mecanismo de UDF de SQL, y es el escape
hatch honesto: evita inventar un lenguaje que sepa geometría.

Se **declaran**, no se importan sueltas: así aparecen en el inventario y se pueden contar y discutir
igual que los umbrales.

El contrato declarativo incluye un nombre con gramática cerrada, aridad mínima y máxima (o
variádica), unidad y procedencia. Una UDF externa sigue siendo **código Python con los mismos permisos
que Oracle**: sólo se activa con `--confiar-escalares`, durante una operación, y el registro anterior
se restaura al terminar o fallar. `--help`, `--relaciones`, `--nueva` y `--escalares` sin esa bandera
son modos de inspección: pueden mostrar archivos o el inventario base, pero no importan código del
proyecto.

### 4. Los tres niveles con un solo mecanismo

Como una medida es un hecho, `medida` es una relación más y las medidas sobre medidas son medidas
normales:

```json
["medida", "meta.umbral_sin_defensa",
  ["desde", ["de", "medida", "m"], ["donde", ["==", ["campo", "m", "porque"], ""]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un número que nadie puede discutir es una métrica esperando a volverse objetivo"],
  ["alcance", "ve si la defensa está VACÍA. NO ve si la defensa es mala, circular o mentirosa"]]
```

Ese `alcance` es el ejemplo de por qué el campo es obligatorio: la medida es útil y es
superficialísima, y decirlo evita que se lea como más de lo que es.

### 5. Modo simulación — ✅ IMPLEMENTADO

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

### 6. Fixtures diferenciales

El esquema vigente es `oracle.diferencial/v1`. Todo fixture declara su versión y una sección
`frescura` con cuatro huellas SHA-256: emisor, fuentes de referencia, catálogo canónico de las
medidas usadas y configuración del dominio. Las rutas son relativas a la raíz del proyecto o a su
padre inmediato; no se aceptan rutas absolutas ni ancestros arbitrarios. Si una huella actual no
coincide, el fixture está **vencido** y no se evalúa.

En el formato `escenarios`, `referencia_ok` conserva únicamente la respuesta global de la
implementación independiente. `oracle_al_generar.global_ok` y
`oracle_al_generar.por_medida` guardan la fotografía de Oracle al emitirlo. La primera comprueba el
acuerdo independiente del conjunto; la segunda detecta cambios individuales, incluso si dos errores
se compensan y el `AND` global permanece igual. Una fotografía individual no se presenta como una
referencia independiente.

La serialización es JSON canónico con orden estable, sin `NaN`; toda aleatoriedad deriva su semilla
de SHA-256 y cualquier repositorio temporal fija las fechas que intervienen en sus identificadores.
Regenerar dos veces con las mismas entradas debe producir exactamente los mismos bytes.

### 7. Criterio de aceptación de esta especificación

Comprobable, y si falla el diseño está mal:

1. una medida sobre **piezas** y una medida sobre **nodos de un grafo** usan los mismos operadores,
   sin adaptador;
2. una medida **sobre medidas** no introduce ninguna construcción nueva;
3. el corpus guarda los tres niveles con el mismo formato;
4. **todo caso del corpus que declara una medida se pone en rojo** con esa medida. El que quede verde
   señala lenguaje faltante o medida mal escrita, y hay que decir cuál. Los casos con
   estado `abierto` **siguen verdes a propósito**: son el hueco declarado, no una falla del
   evaluador. Los casos `resuelto` y `limite_humano` conservan memoria, pero no cuentan como deuda.

**Condición de parada:** si los casos del corpus no se ponen rojos con este juego chico de
operadores, se para y se rediseña — no se agregan operadores hasta que entren.

### 8. Preguntas abiertas

Escritas porque una especificación que finge no tener huecos es peor que una con huecos marcados.

**Las cuatro originales están cerradas**, y sólo una de ellas amplió el álgebra: la ausencia trajo
`agrupar`. El orden resultó ser un campo del hecho, la recursión salió del álgebra hacia el sensor, y
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

  Queda un límite, declarado en el `alcance` de la medida que lo usa: si la relación del lado derecho
  está **vacía**, no hay pares y por lo tanto no hay grupos. Sin resolver, y es honesto decirlo.
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
- **Igualdad de flotantes.** ✅ **RESUELTA negándose.** No hizo falta cambiar la forma de `umbral`:
  **la igualdad exacta sobre flotantes levanta un error**, tanto dentro de una expresión como en el
  umbral final. `0.1 + 0.2` no es `0.3`, y una medida que compare así diría verde sin que nadie se
  entere. Los umbrales y resultados numéricos también tienen que ser finitos y de tipos compatibles.

  La igualdad exacta sólo tiene sentido sobre cosas que se **cuentan** o se **nombran** —enteros,
  booleanos, textos—, y ahí sigue permitida. Sobre cosas que se **miden** hace falta una tolerancia,
  que es justamente lo que el lenguaje pide para todo umbral:

  ```json
  ["<=", ["cerca", a, b], tolerancia]
  ```

  Las comparaciones de ORDEN sobre flotantes siguen permitidas: una tolerancia *es* una comparación
  de orden.
- **Orden.** ✅ **RESUELTO: es un campo del hecho.** No puede ser una propiedad de la relación, porque
  L0 dice que una relación es una **bolsa sin orden semántico**. Entonces «consecutivos» es aritmética
  sobre el campo ordinal, y para eso alcanzó con declarar las escalares `mas` y `menos`.

  Ejemplo real: «la traza no tiene huecos» se expresa agrupando por corrida y comparando la cuenta de
  eventos contra el último instante — `["!=", ["col","registrados"], ["mas", ["col","ultimo"], 1]]`.
  Sin operador nuevo.

### 9. Presupuesto de evaluación

Una medida puede recibir evidencia hostil o simplemente demasiado grande. `LimitesAlgebra` forma
parte de la llamada de evaluación y acota tres amplificaciones: filas por relación, filas que puede
materializar un producto cartesiano y profundidad de una expresión. Los valores por defecto son
finitos; un consumidor puede elegir otros sin alterar un global compartido. Superar un límite es
`ErrorDeAlgebra`, nunca un veredicto verde ni una evaluación parcial.

Estos techos no son umbrales de una medida: protegen al evaluador y por eso no deciden nada sobre el
mundo medido.

### 10. Lo que esta versión deliberadamente no tiene

Sintaxis propia con parser (la forma de dato alcanza), transporte por red (cero consumidores remotos)
y optimizador. Los límites impiden una expansión no acotada; no vuelven eficiente una consulta grande.

---

<!-- fuente: 02-escribir-una-medida.md -->

## Escribir una medida

Esto existe para que **no haga falta pedirle permiso a nadie**. Todo el argumento del repositorio es
que quien ve un defecto pueda escribir la regla que lo atrapa; si para eso hay que saber cómo está
hecho el evaluador, el único que puede escribir reglas es quien lo escribió — y ese es exactamente el
problema que veníamos a resolver.

### El orden importa: primero el caso, después la medida

**Escribí el caso del corpus antes que la medida.** No es prolijidad:

- una medida escrita primero se escribe para pasar, no para atrapar;
- la herramienta puede decirte si tu medida está mal *formada*, pero **no puede saber qué quisiste
  decir**. Una condición invertida —que selecciona lo que está bien en vez de lo que ofende— pasa
  todas las comprobaciones automáticas. El caso es lo único que lo detecta.

```bash
# 1. el caso: la evidencia del defecto, y que se espera ROJO
#    (corpus/proceso/0NN-lo-que-paso.json — copiá uno que exista y cambialo)

# 2. mirá con qué contás
python tools/medida.py --relaciones     # los hechos y sus campos, derivados de la evidencia real
python tools/medida.py --escalares      # las funciones de dominio, operadores y agregados

# 3. la medida
python tools/medida.py --nueva colocacion.mi_regla
#    editás el archivo…
python tools/medida.py catalogos/colocacion/colocacion.mi_regla.json

# 4. que todo siga cerrando
python tools/aceptacion.py    # tu caso tiene que ponerse rojo
python tools/mutar.py         # y el corpus tiene que fijar tu medida
```

Si el proyecto declara funciones en `escalares.py`, los comandos que cargan o evalúan su catálogo
requieren `--confiar-escalares`. Esa bandera autoriza código Python con los mismos permisos del
proceso. `--relaciones` y `--escalares` sin la bandera son seguros: no ejecutan el archivo externo.

El id tiene una gramática cerrada: `dominio.nombre`, con segmentos en minúsculas ASCII, dígitos o
`_`. No se aceptan rutas ni `..`; el archivo se resuelve y confina debajo de `catalogos/` antes de
crear cualquier directorio.

### La forma corta: las macros

**26 de las 27 medidas del catálogo están escritas como macro.** Son azúcar que expande a la forma
canónica —`--expandir` te muestra en qué—, así que el evaluador, la mutación y el inventario no se
enteran de que existen.

```json
["ninguno", "proceso.test_con_mutante_que_lo_mata",
  "mutante", "m",
  ["==", ["campo", "m", "murio"], false],
  "un mutante que sobrevive es un test que no discrimina",
  "cuenta mutantes DECLARADOS. NO ve los que nadie escribió"]
```

| Macro | Para qué | Cuántas la usan |
|---|---|---|
| `ninguno` | ninguna fila debe cumplir el predicado | 22 |
| `ninguno-par` | lo mismo sobre PARES de la misma relación | 2 |
| `peor` | el peor caso de una expresión no pasa de una tolerancia | 2 |

**`peor` recibe la tolerancia una sola vez** y genera con ella el filtro y el umbral. Antes había que
escribirla dos veces y nada las mantenía juntas — era el caso `012` del corpus, cerrado por
construcción.

Las macros no son un embudo: si tu caso no encaja, la forma canónica sigue siendo válida.
`colocacion.interpenetracion` está escrita así porque une dos relaciones DISTINTAS.

### La forma canónica

```json
["medida", "dominio.nombre",
  ["desde", ["de", "relacion", "x"],
            ["donde", <lo que OFENDE>]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "por qué ese número y no otro"],
  ["alcance", "qué NO ve esta medida"]]
```

Cinco piezas, y dos son obligatorias por una razón:

- **`porque`** — un número que nadie puede discutir es una métrica esperando a volverse objetivo.
- **`alcance`** — un verde que no dice lo que no miró se lee como «está bien». Con esto, el informe
  termina enumerando sus propios puntos ciegos.

Y una que **no se declara**: los **testigos** son las filas que sobrevivieron al `donde`. No los
calculás aparte — si lo hicieras, tendrías la misma condición escrita dos veces y nada que las
mantenga sincronizadas.

### Tres ejemplos, de menor a mayor

#### 1. Contar lo que ofende

```json
["medida", "proceso.test_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"], ["donde", ["==", ["campo", "m", "murio"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina: pasa con el código roto"],
  ["alcance", "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los que nadie escribió"]]
```

El 90% de las medidas son así: filtrás lo malo, contás, y el umbral es `<= 0`.

#### 2. Medir una magnitud, no contar

```json
["medida", "snap.grilla",
  ["desde", ["de", "pieza", "a"],
            ["donde", [">", ["desvio_de_grilla", ["hecho", "a"], 100.0], 1.0]]],
  ["resumen", "max", ["desvio_de_grilla", ["hecho", "a"], 100.0]],
  ["umbral", "<=", 1.0, "por debajo de 1 cm el desvío no se ve"],
  ["alcance", "desvío del PIVOTE. NO ve si el pivote está bien puesto dentro de la malla"]]
```

Acá el valor es centímetros y no una cuenta, y eso dice más en el informe. **Escrita a mano, la
tolerancia aparece dos veces** —en el `donde` y en el `umbral`— y nada las mantiene juntas: era el
caso `012` del corpus. Por eso esta forma se escribe con la macro `peor`, que la recibe una sola vez.

#### 3. Comparar filas entre sí

```json
["medida", "vault.nombre_unico_en_el_vault",
  ["desde", ["unir", ["de", "documento", "a"], ["de", "documento", "b"]],
            ["donde", ["y", ["==", ["campo", "a", "nombre"], ["campo", "b", "nombre"]],
                            ["!=", ["campo", "a", "carpeta"], ["campo", "b", "carpeta"]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un wikilink apunta por NOMBRE y no por ruta: dos homónimos dejan el enlace a cara o cruz"],
  ["alcance", "NO ve nombres parecidos pero distintos, que confunden aunque no rompan un enlace"]]
```

`unir` hace el producto de una relación consigo misma. Es como se comparan cosas de a pares:
piezas que se clavan, documentos homónimos, las dos puntas de un relevo.

### Los errores que la herramienta sí te dice

| Qué pasa | Qué dice |
|---|---|
| falta la defensa del umbral | *el umbral `<= 0` no trae defensa* |
| falta `alcance` | *hay que declarar qué NO ve* |
| un campo mal escrito | *«>» sobre un valor ausente* — mirá `--relaciones` |
| nunca se pone roja | *una medida que no puede fallar no mide nada* |
| nunca se pone verde | *probablemente la condición esté invertida* |

Comparar contra un campo que no existe **es un error**, no un `False`. Un `False` silencioso
convertiría un nombre mal escrito en un verde, que es la peor falla posible acá.

### Lo que NO te puede decir

**Si la condición dice lo que quisiste decir.** Una medida que selecciona lo que está bien en vez de
lo que ofende pasa todas las comprobaciones: está bien formada, discrimina, y mide exactamente al
revés. La herramienta no lee intenciones.

Por eso el caso va primero. Y por eso `tools/mutar.py` existe: comprueba que el corpus **fije** tu
medida, o sea que si alguien la escribiera distinta, algún caso lo notaría.

### Si te falta un hecho

Si lo que querés medir no está en `--relaciones`, no se agrega acá: se agrega en el **sensor**, que
vive con el proyecto que produce los datos. El sensor produce hechos y
**no juzga**; el álgebra juzga y **no mira el mundo**. Mezclarlos es cómo se llega a un verificador
que nadie puede discutir.

---

<!-- fuente: 03-el-catalogo.md -->

## El catálogo de medidas

Cada medida es un **archivo de datos**, no código. Se muestran las dos formas: cómo está
escrita (a veces con una macro) y en qué se expande. Y los dos campos que este lenguaje
exige y ningún otro verificador pide: **la defensa del umbral** y **el punto ciego**.

### Dominio `meta` — mide el LENGUAJE mismo

#### meta.el_caso_reclama_una_medida_que_existe

- **mide sobre** la relación `caso`
- **umbral**: `<= 0`
- **por qué ese número**: un caso que apunta a una medida inexistente no fija nada y nadie se enteraría: pasaría por el corpus como si estuviera cubierto
- **qué NO ve**: ve el id que el caso RECLAMA. NO confunde esto con un hueco declarado —un caso sin medida no reclama nada— y NO ve si el id que existe es el adecuado para ese caso

Como está escrita:

```json
[
  "ninguno",
  "meta.el_caso_reclama_una_medida_que_existe",
  "caso",
  "c",
  ["y", ["==", ["campo", "c", "tiene_medida"], true], ["==", ["campo", "c", "medida_existe"], false]],
  "un caso que apunta a una medida inexistente no fija nada y nadie se enteraría: pasaría por el corpus como si estuviera cubierto",
  "ve el id que el caso RECLAMA. NO confunde esto con un hueco declarado —un caso sin medida no reclama nada— y NO ve si el id que existe es el adecuado para ese caso"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.el_caso_reclama_una_medida_que_existe",
  ["desde", ["de", "caso", "c"], ["donde", ["y", ["==", ["campo", "c", "tiene_medida"], true], ["==", ["campo", "c", "medida_existe"], false]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un caso que apunta a una medida inexistente no fija nada y nadie se enteraría: pasaría por el corpus como si estuviera cubierto"],
  ["alcance", "ve el id que el caso RECLAMA. NO confunde esto con un hueco declarado —un caso sin medida no reclama nada— y NO ve si el id que existe es el adecuado para ese caso"]
]
```

#### meta.el_caso_se_pone_como_debe

- **mide sobre** la relación `caso`
- **umbral**: `<= 0`
- **por qué ese número**: un caso del corpus es un defecto real observado: si la medida que lo reclama no se pone roja ahí, la medida está mal escrita o falta lenguaje. Y al revés, un caso correcto que se pone rojo es un falso rojo, que enseña a ignorar el verificador
- **qué NO ve**: compara el veredicto contra la polaridad declarada del caso. NO ve si el caso está bien etiquetado, ni si la evidencia que trae es la del defecto que dice traer

Como está escrita:

```json
[
  "ninguno",
  "meta.el_caso_se_pone_como_debe",
  "caso",
  "c",
  ["!=", ["campo", "c", "esperado_ok"], ["campo", "c", "dio_ok"]],
  "un caso del corpus es un defecto real observado: si la medida que lo reclama no se pone roja ahí, la medida está mal escrita o falta lenguaje. Y al revés, un caso correcto que se pone rojo es un falso rojo, que enseña a ignorar el verificador",
  "compara el veredicto contra la polaridad declarada del caso. NO ve si el caso está bien etiquetado, ni si la evidencia que trae es la del defecto que dice traer"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.el_caso_se_pone_como_debe",
  ["desde", ["de", "caso", "c"], ["donde", ["!=", ["campo", "c", "esperado_ok"], ["campo", "c", "dio_ok"]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un caso del corpus es un defecto real observado: si la medida que lo reclama no se pone roja ahí, la medida está mal escrita o falta lenguaje. Y al revés, un caso correcto que se pone rojo es un falso rojo, que enseña a ignorar el verificador"],
  ["alcance", "compara el veredicto contra la polaridad declarada del caso. NO ve si el caso está bien etiquetado, ni si la evidencia que trae es la del defecto que dice traer"]
]
```

#### meta.el_hueco_declarado_explica_por_que

- **mide sobre** la relación `caso`
- **umbral**: `<= 0`
- **por qué ese número**: un caso sin medida y sin explicación es un caso que alguien va a borrar por prolijidad, y con él se va la memoria de lo que el marco todavía no puede medir
- **qué NO ve**: ve que cada caso marcado explícitamente como hueco abierto tenga una explicación. NO juzga esa explicación ni confunde casos resueltos o límites humanos con trabajo pendiente

Como está escrita:

```json
[
  "ninguno",
  "meta.el_hueco_declarado_explica_por_que",
  "caso",
  "c",
  ["y", ["==", ["campo", "c", "tiene_medida"], false], ["==", ["campo", "c", "es_hueco_abierto"], true], ["==", ["campo", "c", "explica_el_hueco"], false]],
  "un caso sin medida y sin explicación es un caso que alguien va a borrar por prolijidad, y con él se va la memoria de lo que el marco todavía no puede medir",
  "ve que cada caso marcado explícitamente como hueco abierto tenga una explicación. NO juzga esa explicación ni confunde casos resueltos o límites humanos con trabajo pendiente"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.el_hueco_declarado_explica_por_que",
  ["desde", ["de", "caso", "c"], ["donde", ["y", ["==", ["campo", "c", "tiene_medida"], false], ["==", ["campo", "c", "es_hueco_abierto"], true], ["==", ["campo", "c", "explica_el_hueco"], false]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un caso sin medida y sin explicación es un caso que alguien va a borrar por prolijidad, y con él se va la memoria de lo que el marco todavía no puede medir"],
  ["alcance", "ve que cada caso marcado explícitamente como hueco abierto tenga una explicación. NO juzga esa explicación ni confunde casos resueltos o límites humanos con trabajo pendiente"]
]
```

#### meta.el_nivel_no_se_confunde_con_el_dominio

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: el dominio dice QUÉ se mide y el nivel dice SOBRE QUÉ; mezclarlos hace que una medida del mundo se archive como si fuera del lenguaje, y ahí deja de encontrarla quien la busca
- **qué NO ve**: compara el prefijo del nombre contra la relación de origen. NO ve si el dominio elegido es el correcto, ni si la medida mide lo que dice medir

Como está escrita:

```json
[
  "ninguno",
  "meta.el_nivel_no_se_confunde_con_el_dominio",
  "medida",
  "m",
  ["!=", ["campo", "m", "es_meta_por_el_nombre"], ["campo", "m", "es_meta_por_lo_que_mide"]],
  "el dominio dice QUÉ se mide y el nivel dice SOBRE QUÉ; mezclarlos hace que una medida del mundo se archive como si fuera del lenguaje, y ahí deja de encontrarla quien la busca",
  "compara el prefijo del nombre contra la relación de origen. NO ve si el dominio elegido es el correcto, ni si la medida mide lo que dice medir"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.el_nivel_no_se_confunde_con_el_dominio",
  ["desde", ["de", "medida", "m"], ["donde", ["!=", ["campo", "m", "es_meta_por_el_nombre"], ["campo", "m", "es_meta_por_lo_que_mide"]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "el dominio dice QUÉ se mide y el nivel dice SOBRE QUÉ; mezclarlos hace que una medida del mundo se archive como si fuera del lenguaje, y ahí deja de encontrarla quien la busca"],
  ["alcance", "compara el prefijo del nombre contra la relación de origen. NO ve si el dominio elegido es el correcto, ni si la medida mide lo que dice medir"]
]
```

#### meta.toda_medida_esta_ejercitada

- **mide sobre** la relación `medida_en_uso`
- **umbral**: `<= 0`
- **por qué ese número**: una medida que ningún caso ni fixture evalúa nunca es decoración: está en el catálogo, se cuenta en el informe, y no puede fallar porque nadie la corre
- **qué NO ve**: cuenta los casos del PROYECTO que la evalúan. NO exige nada de las medidas heredadas del catálogo base —de ésas responde oracle, con su propio corpus— ni ve si esos casos la ponen a prueba de verdad: para eso está la mutación

Como está escrita:

```json
[
  "ninguno",
  "meta.toda_medida_esta_ejercitada",
  "medida_en_uso",
  "m",
  ["y", ["==", ["campo", "m", "es_heredada"], false], ["==", ["campo", "m", "casos_que_la_evaluan"], 0]],
  "una medida que ningún caso ni fixture evalúa nunca es decoración: está en el catálogo, se cuenta en el informe, y no puede fallar porque nadie la corre",
  "cuenta los casos del PROYECTO que la evalúan. NO exige nada de las medidas heredadas del catálogo base —de ésas responde oracle, con su propio corpus— ni ve si esos casos la ponen a prueba de verdad: para eso está la mutación"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.toda_medida_esta_ejercitada",
  ["desde", ["de", "medida_en_uso", "m"], ["donde", ["y", ["==", ["campo", "m", "es_heredada"], false], ["==", ["campo", "m", "casos_que_la_evaluan"], 0]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una medida que ningún caso ni fixture evalúa nunca es decoración: está en el catálogo, se cuenta en el informe, y no puede fallar porque nadie la corre"],
  ["alcance", "cuenta los casos del PROYECTO que la evalúan. NO exige nada de las medidas heredadas del catálogo base —de ésas responde oracle, con su propio corpus— ni ve si esos casos la ponen a prueba de verdad: para eso está la mutación"]
]
```

#### meta.toda_medida_esta_fijada

- **mide sobre** la relación `medida_en_uso`
- **umbral**: `<= 0`
- **por qué ese número**: una medida propia con cero mutantes pasa vacuamente igual que una cuyos mutantes sobreviven: en ambos casos el catálogo la contiene pero la mutación no demuestra que esté fijada
- **qué NO ve**: exige al menos un mutante y ninguno vivo sólo cuando `debe_tener_mutantes` es verdadero. NO vuelve a exigirlos a medidas heredadas —responde su corpus de origen— ni a las evaluadas aparte, y NO ve los mutadores que nadie escribió

Como está escrita:

```json
[
  "ninguno",
  "meta.toda_medida_esta_fijada",
  "medida_en_uso",
  "m",
  ["y", ["==", ["campo", "m", "debe_tener_mutantes"], true], ["o", ["==", ["campo", "m", "mutantes"], 0], ["!=", ["campo", "m", "mutantes_vivos"], 0]]],
  "una medida propia con cero mutantes pasa vacuamente igual que una cuyos mutantes sobreviven: en ambos casos el catálogo la contiene pero la mutación no demuestra que esté fijada",
  "exige al menos un mutante y ninguno vivo sólo cuando `debe_tener_mutantes` es verdadero. NO vuelve a exigirlos a medidas heredadas —responde su corpus de origen— ni a las evaluadas aparte, y NO ve los mutadores que nadie escribió"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.toda_medida_esta_fijada",
  ["desde", ["de", "medida_en_uso", "m"], ["donde", ["y", ["==", ["campo", "m", "debe_tener_mutantes"], true], ["o", ["==", ["campo", "m", "mutantes"], 0], ["!=", ["campo", "m", "mutantes_vivos"], 0]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una medida propia con cero mutantes pasa vacuamente igual que una cuyos mutantes sobreviven: en ambos casos el catálogo la contiene pero la mutación no demuestra que esté fijada"],
  ["alcance", "exige al menos un mutante y ninguno vivo sólo cuando `debe_tener_mutantes` es verdadero. NO vuelve a exigirlos a medidas heredadas —responde su corpus de origen— ni a las evaluadas aparte, y NO ve los mutadores que nadie escribió"]
]
```

### Dominio `proceso` — mide el mundo

#### proceso.afirmacion_declara_alcance

- **mide sobre** la relación `afirmacion`
- **umbral**: `<= 0`
- **por qué ese número**: una afirmación de verde sin alcance declarado es una cifra, no algo verificable: se lee como «está bien» y sólo dice «no se rompió lo de antes»
- **qué NO ve**: ve si el campo está VACÍO. NO ve si el alcance escrito es honesto, completo ni pertinente

Como está escrita:

```json
[
  "ninguno",
  "proceso.afirmacion_declara_alcance",
  "afirmacion",
  "a",
  ["==", ["campo", "a", "alcance"], ""],
  "una afirmación de verde sin alcance declarado es una cifra, no algo verificable: se lee como «está bien» y sólo dice «no se rompió lo de antes»",
  "ve si el campo está VACÍO. NO ve si el alcance escrito es honesto, completo ni pertinente"
]
```

En qué se expande:

```json
[
  "medida",
  "proceso.afirmacion_declara_alcance",
  ["desde", ["de", "afirmacion", "a"], ["donde", ["==", ["campo", "a", "alcance"], ""]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una afirmación de verde sin alcance declarado es una cifra, no algo verificable: se lee como «está bien» y sólo dice «no se rompió lo de antes»"],
  ["alcance", "ve si el campo está VACÍO. NO ve si el alcance escrito es honesto, completo ni pertinente"]
]
```

#### proceso.arnes_con_bytecode_frio

- **mide sobre** la relación `corrida_mutacion`
- **umbral**: `<= 0`
- **por qué ese número**: CPython invalida el .pyc por (mtime, tamaño): mutar y restaurar dentro del mismo segundo deja a Python corriendo el bytecode mutado sobre el código ya restaurado
- **qué NO ve**: ve la corrida que lo declara. NO ve otras formas de caché: módulos ya importados en memoria, o un import hecho por otro test antes de la mutación

Como está escrita:

```json
[
  "ninguno",
  "proceso.arnes_con_bytecode_frio",
  "corrida_mutacion",
  "c",
  ["==", ["campo", "c", "bytecode_frio"], false],
  "CPython invalida el .pyc por (mtime, tamaño): mutar y restaurar dentro del mismo segundo deja a Python corriendo el bytecode mutado sobre el código ya restaurado",
  "ve la corrida que lo declara. NO ve otras formas de caché: módulos ya importados en memoria, o un import hecho por otro test antes de la mutación"
]
```

En qué se expande:

```json
[
  "medida",
  "proceso.arnes_con_bytecode_frio",
  ["desde", ["de", "corrida_mutacion", "c"], ["donde", ["==", ["campo", "c", "bytecode_frio"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "CPython invalida el .pyc por (mtime, tamaño): mutar y restaurar dentro del mismo segundo deja a Python corriendo el bytecode mutado sobre el código ya restaurado"],
  ["alcance", "ve la corrida que lo declara. NO ve otras formas de caché: módulos ya importados en memoria, o un import hecho por otro test antes de la mutación"]
]
```

#### proceso.modulo_alcanzable

- **mide sobre** la relación `modulo`
- **umbral**: `<= 0`
- **por qué ese número**: un módulo que no se alcanza desde ninguna entrada no lo va a ejecutar nadie, aunque tenga importadores: un racimo entero puede importarse entre sí y estar muerto
- **qué NO ve**: sigue los imports estáticos desde las entradas declaradas, y descuenta los `__init__.py` vacíos, que son marcadores de paquete. NO ve la carga dinámica —importlib, un plugin, un punto de entrada por configuración— así que un módulo vivo por esa vía sale marcado, y NO ve nada si la relación `alcanzable` está vacía

Como está escrita:

```json
[
  "medida",
  "proceso.modulo_alcanzable",
  ["desde", ["unir", ["de", "modulo", "m"], ["de", "alcanzable", "r"]], ["agrupar", [["modulo", ["campo", "m", "nombre"]]], [["veces_alcanzado", "suma", ["==", ["campo", "r", "hasta"], ["campo", "m", "nombre"]]], ["es_paquete_vacio", "max", ["campo", "m", "es_paquete_vacio"]]]], ["donde", ["y", ["==", ["col", "veces_alcanzado"], 0], ["==", ["col", "es_paquete_vacio"], false]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un módulo que no se alcanza desde ninguna entrada no lo va a ejecutar nadie, aunque tenga importadores: un racimo entero puede importarse entre sí y estar muerto"],
  ["alcance", "sigue los imports estáticos desde las entradas declaradas, y descuenta los `__init__.py` vacíos, que son marcadores de paquete. NO ve la carga dinámica —importlib, un plugin, un punto de entrada por configuración— así que un módulo vivo por esa vía sale marcado, y NO ve nada si la relación `alcanzable` está vacía"]
]
```

#### proceso.modulo_con_consumidor

- **mide sobre** la relación `modulo`
- **umbral**: `<= 0`
- **por qué ese número**: un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite
- **qué NO ve**: cuenta importadores que no son tests, agrupando por módulo. NO ve nada si la relación `importa` está vacía —sin pares no hay grupos— ni distingue un importador que usa el módulo de uno que lo importa y no lo llama

Como está escrita:

```json
[
  "medida",
  "proceso.modulo_con_consumidor",
  ["desde", ["unir", ["de", "modulo", "m"], ["de", "importa", "i"]], ["agrupar", [["modulo", ["campo", "m", "nombre"]]], [["importadores_reales", "suma", ["y", ["==", ["campo", "i", "b"], ["campo", "m", "nombre"]], ["==", ["campo", "i", "es_test"], false]]]]], ["donde", ["==", ["col", "importadores_reales"], 0]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite"],
  ["alcance", "cuenta importadores que no son tests, agrupando por módulo. NO ve nada si la relación `importa` está vacía —sin pares no hay grupos— ni distingue un importador que usa el módulo de uno que lo importa y no lo llama"]
]
```

#### proceso.ronda_mutacion_concluyente

- **mide sobre** la relación `corrida_mutacion`
- **umbral**: `<= 0`
- **por qué ese número**: sin mutantes no hay material; un timeout, un error del arnés o una línea base roja dejan la mutación inconclusa: ninguno demuestra que un mutante murió
- **qué NO ve**: ve los estados estructurados publicados por cada corrida. NO distingue por sí sola si un código no cero fue una aserción o un error: eso depende del protocolo explícito del runner

Como está escrita:

```json
[
  "ninguno",
  "proceso.ronda_mutacion_concluyente",
  "corrida_mutacion",
  "c",
  ["o", ["<=", ["campo", "c", "mutantes"], 0], ["==", ["campo", "c", "baseline_verde"], false], [">", ["campo", "c", "errores_arnes"], 0], [">", ["campo", "c", "timeouts"], 0]],
  "sin mutantes no hay material; un timeout, un error del arnés o una línea base roja dejan la mutación inconclusa: ninguno demuestra que un mutante murió",
  "ve los estados estructurados publicados por cada corrida. NO distingue por sí sola si un código no cero fue una aserción o un error: eso depende del protocolo explícito del runner"
]
```

En qué se expande:

```json
[
  "medida",
  "proceso.ronda_mutacion_concluyente",
  ["desde", ["de", "corrida_mutacion", "c"], ["donde", ["o", ["<=", ["campo", "c", "mutantes"], 0], ["==", ["campo", "c", "baseline_verde"], false], [">", ["campo", "c", "errores_arnes"], 0], [">", ["campo", "c", "timeouts"], 0]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "sin mutantes no hay material; un timeout, un error del arnés o una línea base roja dejan la mutación inconclusa: ninguno demuestra que un mutante murió"],
  ["alcance", "ve los estados estructurados publicados por cada corrida. NO distingue por sí sola si un código no cero fue una aserción o un error: eso depende del protocolo explícito del runner"]
]
```

#### proceso.sintaxis_valida_tras_edicion_masiva

- **mide sobre** la relación `archivo`
- **umbral**: `<= 0`
- **por qué ese número**: reescribir N archivos con una expresión regular puede romper la sintaxis, y comprobar que los N siguen parseando es una línea
- **qué NO ve**: ve archivos marcados como no parseables. NO ve el daño que SÍ parsea: una regex puede cambiar el significado de una línea sin romper la sintaxis

Como está escrita:

```json
[
  "ninguno",
  "proceso.sintaxis_valida_tras_edicion_masiva",
  "archivo",
  "a",
  ["==", ["campo", "a", "sintaxis_valida"], false],
  "reescribir N archivos con una expresión regular puede romper la sintaxis, y comprobar que los N siguen parseando es una línea",
  "ve archivos marcados como no parseables. NO ve el daño que SÍ parsea: una regex puede cambiar el significado de una línea sin romper la sintaxis"
]
```

En qué se expande:

```json
[
  "medida",
  "proceso.sintaxis_valida_tras_edicion_masiva",
  ["desde", ["de", "archivo", "a"], ["donde", ["==", ["campo", "a", "sintaxis_valida"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "reescribir N archivos con una expresión regular puede romper la sintaxis, y comprobar que los N siguen parseando es una línea"],
  ["alcance", "ve archivos marcados como no parseables. NO ve el daño que SÍ parsea: una regex puede cambiar el significado de una línea sin romper la sintaxis"]
]
```

#### proceso.test_con_mutante_que_lo_mata

- **mide sobre** la relación `mutante`
- **umbral**: `<= 0`
- **por qué ese número**: un mutante que sobrevive es un test que no discrimina: pasa con el código roto, así que su verde no significa nada
- **qué NO ve**: cuenta mutantes cuya muerte no fue demostrada: sobrevivientes, timeouts y errores del arnés conservan `murio=false`. NO ve los mutantes que nadie generó: una función sin ningún mutante apuntado da cero y sale verde

Como está escrita:

```json
[
  "ninguno",
  "proceso.test_con_mutante_que_lo_mata",
  "mutante",
  "m",
  ["==", ["campo", "m", "murio"], false],
  "un mutante que sobrevive es un test que no discrimina: pasa con el código roto, así que su verde no significa nada",
  "cuenta mutantes cuya muerte no fue demostrada: sobrevivientes, timeouts y errores del arnés conservan `murio=false`. NO ve los mutantes que nadie generó: una función sin ningún mutante apuntado da cero y sale verde"
]
```

En qué se expande:

```json
[
  "medida",
  "proceso.test_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"], ["donde", ["==", ["campo", "m", "murio"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina: pasa con el código roto, así que su verde no significa nada"],
  ["alcance", "cuenta mutantes cuya muerte no fue demostrada: sobrevivientes, timeouts y errores del arnés conservan `murio=false`. NO ve los mutantes que nadie generó: una función sin ningún mutante apuntado da cero y sale verde"]
]
```

#### proceso.verificacion_vigente

- **mide sobre** la relación `cambio`
- **umbral**: `<= 0`
- **por qué ese número**: un «corrió verde» es una foto con fecha; si después se tocó código vivo la foto es de otro código, y afirmarla es mentir
- **qué NO ve**: cuenta cambios marcados como código vivo. En v0.1 NO compara fechas ni sabe cuál verificación quedó vieja: cualquier cambio vivo la invalida. Hace falta comparar contra el commit de la verificación

Como está escrita:

```json
[
  "ninguno",
  "proceso.verificacion_vigente",
  "cambio",
  "c",
  ["==", ["campo", "c", "es_codigo_vivo"], true],
  "un «corrió verde» es una foto con fecha; si después se tocó código vivo la foto es de otro código, y afirmarla es mentir",
  "cuenta cambios marcados como código vivo. En v0.1 NO compara fechas ni sabe cuál verificación quedó vieja: cualquier cambio vivo la invalida. Hace falta comparar contra el commit de la verificación"
]
```

En qué se expande:

```json
[
  "medida",
  "proceso.verificacion_vigente",
  ["desde", ["de", "cambio", "c"], ["donde", ["==", ["campo", "c", "es_codigo_vivo"], true]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un «corrió verde» es una foto con fecha; si después se tocó código vivo la foto es de otro código, y afirmarla es mentir"],
  ["alcance", "cuenta cambios marcados como código vivo. En v0.1 NO compara fechas ni sabe cuál verificación quedó vieja: cualquier cambio vivo la invalida. Hace falta comparar contra el commit de la verificación"]
]
```

#### proceso.verificador_sin_falsos_rojos

- **mide sobre** la relación `hallazgo`
- **umbral**: `<= 0`
- **por qué ese número**: un falso rojo enseña a ignorar el verificador, y eso lo vuelve peor que no tener ninguno
- **qué NO ve**: ve hallazgos que YA fueron etiquetados como falsos. NO puede decidir sola si un hallazgo es real: alguien tuvo que mirarlo

Como está escrita:

```json
[
  "ninguno",
  "proceso.verificador_sin_falsos_rojos",
  "hallazgo",
  "h",
  ["==", ["campo", "h", "era_real"], false],
  "un falso rojo enseña a ignorar el verificador, y eso lo vuelve peor que no tener ninguno",
  "ve hallazgos que YA fueron etiquetados como falsos. NO puede decidir sola si un hallazgo es real: alguien tuvo que mirarlo"
]
```

En qué se expande:

```json
[
  "medida",
  "proceso.verificador_sin_falsos_rojos",
  ["desde", ["de", "hallazgo", "h"], ["donde", ["==", ["campo", "h", "era_real"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un falso rojo enseña a ignorar el verificador, y eso lo vuelve peor que no tener ninguno"],
  ["alcance", "ve hallazgos que YA fueron etiquetados como falsos. NO puede decidir sola si un hallazgo es real: alguien tuvo que mirarlo"]
]
```

### Dominio `simulacion` — mide el mundo

#### simulacion.corrida_reproducible

- **mide sobre** la relación `corrida`
- **umbral**: `<= 0`
- **por qué ese número**: una corrida que no se reproduce no puede ser material de corpus: mañana da otra cosa y el caso deja de significar algo. Sin determinismo la simulación no es evidencia, es una anécdota
- **qué NO ve**: compara dos ejecuciones con la MISMA semilla. NO ve si el resultado depende de algo de afuera —la hora, el orden de un diccionario, un archivo— que hoy casualmente no cambió

Como está escrita:

```json
[
  "ninguno",
  "simulacion.corrida_reproducible",
  "corrida",
  "c",
  ["==", ["campo", "c", "determinista"], false],
  "una corrida que no se reproduce no puede ser material de corpus: mañana da otra cosa y el caso deja de significar algo. Sin determinismo la simulación no es evidencia, es una anécdota",
  "compara dos ejecuciones con la MISMA semilla. NO ve si el resultado depende de algo de afuera —la hora, el orden de un diccionario, un archivo— que hoy casualmente no cambió"
]
```

En qué se expande:

```json
[
  "medida",
  "simulacion.corrida_reproducible",
  ["desde", ["de", "corrida", "c"], ["donde", ["==", ["campo", "c", "determinista"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una corrida que no se reproduce no puede ser material de corpus: mañana da otra cosa y el caso deja de significar algo. Sin determinismo la simulación no es evidencia, es una anécdota"],
  ["alcance", "compara dos ejecuciones con la MISMA semilla. NO ve si el resultado depende de algo de afuera —la hora, el orden de un diccionario, un archivo— que hoy casualmente no cambió"]
]
```

#### simulacion.la_traza_no_tiene_huecos

- **mide sobre** la relación `evento`
- **umbral**: `<= 0`
- **por qué ese número**: una traza con huecos describe otra corrida que la que ocurrió: si faltan pasos, cualquier cosa que se mida sobre ella habla de lo que se registró y no de lo que pasó
- **qué NO ve**: compara cuántos eventos hay contra el instante final, asumiendo que el tiempo arranca en cero y avanza de a uno. NO ve trazas donde varios eventos comparten instante, ni sabe si el que falta es importante

Como está escrita:

```json
[
  "medida",
  "simulacion.la_traza_no_tiene_huecos",
  ["desde", ["de", "evento", "e"], ["agrupar", [["corrida", ["campo", "e", "corrida"]]], [["registrados", "contar", 1], ["ultimo", "max", ["campo", "e", "t"]]]], ["donde", ["!=", ["col", "registrados"], ["mas", ["col", "ultimo"], 1]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una traza con huecos describe otra corrida que la que ocurrió: si faltan pasos, cualquier cosa que se mida sobre ella habla de lo que se registró y no de lo que pasó"],
  ["alcance", "compara cuántos eventos hay contra el instante final, asumiendo que el tiempo arranca en cero y avanza de a uno. NO ve trazas donde varios eventos comparten instante, ni sabe si el que falta es importante"]
]
```

#### simulacion.no_se_agoto_el_presupuesto

- **mide sobre** la relación `corrida`
- **umbral**: `<= 0`
- **por qué ese número**: una corrida que se quedó sin pasos no observó el sistema: observó el presupuesto. Cualquier conclusión que salga de ahí habla de la paciencia del que simuló, no de lo simulado
- **qué NO ve**: ve la clasificación producida por el contrato de terminación. NO ve si el presupuesto era razonable, ni si una corrida que terminó a tiempo lo hizo por el motivo correcto

Como está escrita:

```json
[
  "ninguno",
  "simulacion.no_se_agoto_el_presupuesto",
  "corrida",
  "c",
  ["==", ["campo", "c", "presupuesto_agotado"], true],
  "una corrida que se quedó sin pasos no observó el sistema: observó el presupuesto. Cualquier conclusión que salga de ahí habla de la paciencia del que simuló, no de lo simulado",
  "ve la clasificación producida por el contrato de terminación. NO ve si el presupuesto era razonable, ni si una corrida que terminó a tiempo lo hizo por el motivo correcto"
]
```

En qué se expande:

```json
[
  "medida",
  "simulacion.no_se_agoto_el_presupuesto",
  ["desde", ["de", "corrida", "c"], ["donde", ["==", ["campo", "c", "presupuesto_agotado"], true]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una corrida que se quedó sin pasos no observó el sistema: observó el presupuesto. Cualquier conclusión que salga de ahí habla de la paciencia del que simuló, no de lo simulado"],
  ["alcance", "ve la clasificación producida por el contrato de terminación. NO ve si el presupuesto era razonable, ni si una corrida que terminó a tiempo lo hizo por el motivo correcto"]
]
```

---

<!-- fuente: 04-el-corpus.md -->

## El corpus: los casos donde la medición dijo bien y no estaba bien

Son datos, no anécdotas: cada caso trae su evidencia en forma de relaciones, así que se
puede volver a juzgar. El corpus es el **criterio de aceptación** del resto: cuando hay
medidas, cada caso de defecto tiene que ponerse rojo y cada caso correcto, verde.

### Los números

| Etiqueta | Cuántos |
|---|---|
| falso_verde | 25 |
| verde_correcto | 12 |
| deuda_de_diseño | 2 |
| falso_rojo | 2 |
| medida_correcta_conclusion_errada | 1 |

| Cómo se detectó | Cuántos |
|---|---|
| mutacion | 17 |
| observacion | 12 |
| persona | 8 |
| accidente | 4 |
| herramienta_ajena | 1 |

**Cada caso registra cómo se detectó.** Una suite verde y una mutación, una persona o
un accidente son señales distintas; mezclarlas borraría justo la evidencia que el
corpus intenta conservar.

### 001-verde-acumulativo

**«489 tests OK» reportado cada turno: un número que sube y nunca significa más**

- etiqueta: `falso_verde` · se detectó por: `persona`
- medida que lo atrapa: `proceso.afirmacion_declara_alcance`
- de dónde salió: Brianholl/jam · todos

**Qué pasó.** El agente cerró cada entrega con un conteo de tests en verde. El conteo crece monótonamente y no distingue haber cubierto algo nuevo de haber agregado tests a lo ya cubierto. Se lee como «está bien» y sólo dice «no se rompió lo de antes».

**Qué se aprendió.** Una afirmación de verde sin alcance declarado no es una afirmación verificable: es una cifra. El alcance es lo que la vuelve discutible.

La evidencia, como relaciones:

```json
{
  "afirmacion": [{"id": "a1", "texto": "459 tests OK", "comando": "unittest discover", "alcance": ""}, {"id": "a2", "texto": "477 tests OK", "comando": "unittest discover", "alcance": ""}, {"id": "a3", "texto": "489 tests OK", "comando": "unittest discover", "alcance": ""}]
}
```

### 002-mutante-firma-por-id

**El test de orden de la firma pasaba con el código roto**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.test_con_mutante_que_lo_mata`
- de dónde salió: Brianholl/jam · 19d2593

**Qué pasó.** `firma()` debe ordenar los pines por POSICIÓN visual. Se mutó a ordenar por id y el test siguió en verde: en los datos del test el id «a» caía justo en el pin de arriba, así que los dos órdenes coincidían.

**Qué se aprendió.** Un test de ORDEN cuyos datos hacen coincidir dos órdenes distintos no comprueba nada. Los identificadores tienen que ir a propósito al revés que el criterio.

La evidencia, como relaciones:

```json
{
  "test": [{"id": "test_la_firma_sale_en_el_orden_en_que_se_ven_los_pines", "archivo": "tests/test_funcion.py", "cubre": "funcion._orden_visual"}]
  "mutante": [{"id": "orden_por_id", "apunta_a": "funcion._orden_visual", "cambio": "clave de sort: (y,x,id) -> id", "murio": false}]
}
```

### 003-mutante-fondo-nunca-ejercitado

**La regla que ignora la escenografía de fondo existía sin estar verificada**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.test_con_mutante_que_lo_mata`
- de dónde salió: Brianholl/jam · 535d476

**Qué pasó.** El catálogo filtra piezas descomunales (una SkySphere «contiene» todo y haría que cualquier cosa interpenetre). Se quitó el filtro y ningún test cayó: el generador de mundos nunca creaba una pieza de fondo.

**Qué se aprendió.** Una rama de código que ningún dato de prueba recorre es una creencia, no una regla. La cobertura de LÍNEAS no lo detecta si la línea se ejecuta y nunca cambia el resultado.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "sin_filtro_fondo", "apunta_a": "catalogo._vecinas", "cambio": "quitar el filtro es_fondo", "murio": false}]
  "generador": [{"id": "_mundo", "produce": "pieza", "cubre_caso_fondo": false}]
}
```

### 004-testigos-duplicados

**La medición y sus testigos recorrían los datos dos veces, con dos definiciones**

- etiqueta: `deuda_de_diseño` · se detectó por: `persona`
- medida que lo atrapa: `ninguna todavía`
- de dónde salió: Brianholl/jam · 535d476

**Qué pasó.** `INTERPENETRACION` declaraba `mide=penetracion_maxima` y `testigos=piezas_clavadas`: dos funciones que recorren lo mismo con la misma condición escrita dos veces. Nada garantiza que no se separen.

**Qué se aprendió.** Si el lenguaje obliga a escribir dos veces la misma condición, el lenguaje está mal. Los testigos no son un cálculo aparte: son el filtro.

**Resuelto.** 2026-07-29, por construcción: los testigos son las filas que sobrevivieron a la única tubería de la medida; ya no existe una segunda función donde repetir la condición.

La evidencia, como relaciones:

```json
{
  "declaracion": [{"medida": "colocacion.interpenetracion", "mide": "penetracion_maxima", "testigos": "piezas_clavadas", "condicion_repetida": true}]
}
```

### 005-mutante-yaw-sin-franja

**Aflojar el umbral de yaw de 0.5° a 5° no rompía ningún test**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.test_con_mutante_que_lo_mata`
- de dónde salió: Brianholl/jam · 535d476

**Qué pasó.** Los yaw generados daban desvíos de 0, 0.4 y 45 grados. Ninguno cae entre 0.5 y 5, que es la única franja donde los dos umbrales difieren.

**Qué se aprendió.** Para verificar un UMBRAL hacen falta datos en la franja donde ese umbral decide. Sin eso, el número podría ser cualquiera.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "umbral_yaw_flojo", "apunta_a": "catalogo.YAW", "cambio": "umbral <= 0.5 -> <= 5.0", "murio": false}]
  "generador": [{"id": "_snappeable", "produce": "pieza", "cubre_franja_0.5_a_5_grados": false}]
  "desvio_yaw_generado": [{"grados": 0.0}, {"grados": 0.4}, {"grados": 45.0}]
}
```

### 006-arnes-bytecode-viejo

**El arnés de mutación corría bytecode mutado sobre código restaurado**

- etiqueta: `falso_verde` · se detectó por: `accidente`
- medida que lo atrapa: `proceso.arnes_con_bytecode_frio`
- de dónde salió: Brianholl/jam · 535d476

**Qué pasó.** `max` y `min` ocupan lo mismo. CPython invalida el .pyc por (mtime, tamaño), y mutar/restaurar caía dentro del mismo segundo: Python siguió ejecutando el .pyc mutado con el .py ya restaurado. Los resultados reportados eran basura.

**Qué se aprendió.** El instrumento que mide la calidad de los tests también necesita ser verificado. Un arnés de mutación que no invalida el caché reporta al azar.

La evidencia, como relaciones:

```json
{
  "corrida_mutacion": [{"id": "c1", "mutantes": 6, "bytecode_frio": false, "resultado_confiable": false}]
}
```

### 007-relevo-verde-arbol-sucio

**El verificador de relevo daba verde con el código vivo modificado sin commitear**

- etiqueta: `falso_verde` · se detectó por: `accidente`
- medida que lo atrapa: `proceso.verificacion_vigente`
- de dónde salió: Brianholl/jam · 19d2593

**Qué pasó.** La regla comparaba el commit de la última verificación con motor contra HEAD. Como los cambios estaban en el árbol de trabajo y no commiteados, el diff salía vacío y la verificación se declaraba vigente.

**Qué se aprendió.** «Verde» es una foto con fecha. Si después se tocó el código —commiteado o no—, la foto es de otro código y afirmarla es mentir.

La evidencia, como relaciones:

```json
{
  "verificacion": [{"que": "motor", "commit": "15c4cae", "camino": "editor headless"}]
  "cambio": [{"archivo": "jam/api.py", "commiteado": false, "es_codigo_vivo": true}, {"archivo": "jam/funcion.py", "commiteado": false, "es_codigo_vivo": true}]
}
```

### 008-vault-falso-rojo

**El verificador del vault reportaba roto lo que estaba bien**

- etiqueta: `falso_rojo` · se detectó por: `accidente`
- medida que lo atrapa: `proceso.verificador_sin_falsos_rojos`
- de dónde salió: Brianholl/jam · f738f07

**Qué pasó.** Contaba como enlaces la barra escapada `\|` obligatoria dentro de tablas de Markdown, y los `[[ejemplos]]` escritos dentro de comillas invertidas en la guía.

**Qué se aprendió.** Un falso rojo es peor que no verificar: enseña a ignorar el verificador. Se arregla el verificador, nunca el documento.

La evidencia, como relaciones:

```json
{
  "hallazgo": [{"verificador": "vault", "objetivo": "tabla con \\|", "era_real": false}, {"verificador": "vault", "objetivo": "[[ejemplo]] en backticks", "era_real": false}]
}
```

### 009-modulo-sin-consumidor

**Módulos completos, testeados y que nadie importa**

- etiqueta: `falso_verde` · se detectó por: `persona`
- medida que lo atrapa: `proceso.modulo_con_consumidor`
- de dónde salió: Brianholl/jam · 535d476

**Qué pasó.** El agente criticó que `preview2d` estuviera entero con cero consumidores en `Source/`, y un turno después escribió `medida.py` y `catalogo.py` con tests en verde y ningún importador. El verde de los tests no distingue «funciona» de «se usa».

**Qué se aprendió.** Un test no es un consumidor: un módulo cuyos únicos importadores son sus propios tests está verde y no está en uso. Este caso pidió el operador `agrupar` durante dos días —la medida declaraba no poder distinguirlos— y con la ausencia expresable ya los distingue.

La evidencia, como relaciones:

```json
{
  "modulo": [{"nombre": "jam.preview2d", "tests": 9, "importadores": 0}, {"nombre": "jam.medida", "tests": 12, "importadores": 1}, {"nombre": "jam.catalogo", "tests": 12, "importadores": 1}]
  "importa": [{"a": "tests.test_medida", "b": "jam.medida", "es_test": true}, {"a": "tests.test_medida", "b": "jam.catalogo", "es_test": true}]
}
```

### 010-sed-desindenta

**Una edición en masa desindentó código y lo dejó sintácticamente roto**

- etiqueta: `falso_verde` · se detectó por: `herramienta_ajena`
- medida que lo atrapa: `proceso.sintaxis_valida_tras_edicion_masiva`
- de dónde salió: Brianholl/jam · 24d5e07

**Qué pasó.** `sed 's/^ *from src\./from oraculo./'` reescribió imports que estaban DENTRO de funciones y les comió la indentación. El daño no lo detectó ninguna comprobación propia: apareció porque un parser ajeno no pudo leer el archivo.

**Qué se aprendió.** Después de reescribir N archivos con una expresión regular hay que comprobar que los N siguen parseando. Es una línea y no estaba.

La evidencia, como relaciones:

```json
{
  "edicion_masiva": [{"herramienta": "sed", "archivos": 13, "verifico_sintaxis_despues": false}]
  "archivo": [{"ruta": "tests/test_winnability_h9.py", "sintaxis_valida": false}]
}
```

### 011-conclusion-errada-desvan

**Medición correcta, conclusión equivocada: «88% sin usar» era «88% no importable»**

- etiqueta: `medida_correcta_conclusion_errada` · se detectó por: `persona`
- medida que lo atrapa: `ninguna todavía`
- de dónde salió: Brianholl/jam · 24d5e07

**Qué pasó.** Se midió alcanzabilidad desde un punto de entrada y salió que 34 de 36 módulos no se alcanzaban. Se concluyó «desván, podalo». La causa real era que 25 de 34 no se podían IMPORTAR porque el código apuntaba al monorepo viejo. El número era cierto; la causa atribuida, no.

**Qué se aprendió.** Una medición correcta admite varias causas. El oráculo puede exigir que la conclusión nombre su medición; no puede validar la causa. Ese salto es humano y hay que dejarlo a la vista.

**Límite humano.** No hay forma mecánica genérica de validar una atribución causal. Oracle puede exigir trazabilidad entre conclusión y medición, pero una persona debe discutir el salto causal.

La evidencia, como relaciones:

```json
{
  "modulo": [{"nombre": "oraculo.mazes.spacegraph_channels", "alcanzable": false, "importable": false}, {"nombre": "oraculo.mazes.descriptors", "alcanzable": false, "importable": false}]
  "conclusion": [{"texto": "88% desván, podalo", "medicion": "alcanzabilidad", "causa_atribuida": "desuso", "causa_real": "imports rotos"}]
}
```

### 012-umbral-duplicado-en-filtro-y-umbral

**El umbral de dominio aparece dos veces en la misma medida y nada los mantiene juntos**

- etiqueta: `deuda_de_diseño` · se detectó por: `persona`
- medida que lo atrapa: `ninguna todavía`
- de dónde salió: Segtem/oracle · catálogo de geometría

**Qué pasó.** En `snap.grilla` el 1.0 cm está en el `donde` (que selecciona los testigos) y otra vez en el `umbral` (que trae su defensa escrita). Si alguien cambia uno y no el otro, la medida queda incoherente: reportaría testigos que el umbral perdona, o al revés.

**Qué se aprendió.** Un número que aparece dos veces puede divergir. Es el mismo defecto que los testigos duplicados del caso 004, en el otro extremo de la medida.

**Resuelto.** 2026-07-29, por construcción: la macro `peor` recibe la tolerancia UNA vez y genera con ella el filtro y el umbral. No hace falta comprobar que coincidan porque no hay dos copias. Se deja el caso como registro: la deuda existió y así se cerró.

La evidencia, como relaciones:

```json
{
  "declaracion": [{"medida": "snap.grilla", "umbral_en_filtro": 1.0, "umbral_declarado": 1.0, "coinciden": true}, {"medida": "snap.yaw", "umbral_en_filtro": 0.5, "umbral_declarado": 0.5, "coinciden": true}]
}
```

### 013-comparadores-del-algebra-sin-ejercitar

**53 tests en verde y cuatro de los seis comparadores del álgebra sin verificar**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.test_con_mutante_que_lo_mata`
- de dónde salió: Segtem/oracle · primera corrida de mutación de código

**Qué pasó.** El álgebra define seis comparadores. Los tests sólo ejercitaban `<=` y `>`, y por vías indirectas (a través de medidas). Cambiar `!=` por `==`, `<` por `<=`, `>` por `>=` o `>=` por `>` NO rompía ningún test. Lo mismo el formateo del informe: se había argumentado que «el informe es contrato» y nadie lo verificaba.

**Qué se aprendió.** Un conteo de tests no dice nada sobre qué fija. 53 tests verdes convivían con 88 mutantes vivos. Y los mutantes hay que GENERARLOS: si el autor elige cuáles escribir, elige los que sus tests ya atrapan.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "algebra.py:50:27:comparador", "apunta_a": "algebra._cmp", "murio": false}, {"id": "algebra.py:51:26:comparador", "apunta_a": "algebra._cmp", "murio": false}, {"id": "algebra.py:53:26:comparador", "apunta_a": "algebra._cmp", "murio": false}, {"id": "algebra.py:54:27:comparador", "apunta_a": "algebra._cmp", "murio": false}, {"id": "medida.py:52:73:constante", "apunta_a": "medida.Veredicto.linea", "murio": false}, {"id": "medida.py:53:53:comparador", "apunta_a": "medida.Veredicto.linea", "murio": false}]
  "corrida_mutacion": [{"id": "nucleo_primera", "mutantes": 242, "bytecode_frio": true, "resultado_confiable": true}]
}
```

### 014-mutador-dejo-un-archivo-mutado-al-ser-matado

**El mutador de código dejó un archivo del núcleo MUTADO en el árbol de trabajo**

- etiqueta: `falso_verde` · se detectó por: `accidente`
- medida que lo atrapa: `proceso.test_con_mutante_que_lo_mata`
- de dónde salió: Segtem/oracle · corrida de mutación cortada por timeout

**Qué pasó.** `tools/mutar_codigo.py` restaura cada archivo en un `finally`, y hay un test que lo comprueba: `test_restaura_el_archivo_EXACTAMENTE`. Pero el test sólo cubre el camino NORMAL. Una corrida se cortó por timeout —SIGTERM— y Python termina sin ejecutar el `finally`: `nucleo/mutacion_codigo.py` quedó en su forma mutada, con 71 líneas menos. El daño lo salvó `git checkout`, no la herramienta.

**Qué se aprendió.** Una herramienta que escribe sobre fuentes reales necesita red de seguridad ANTE TERMINACIÓN, no sólo ante excepción: `atexit` más manejadores de SIGTERM/SIGINT/SIGHUP. Y el test que la cubre tiene que MATAR un subproceso de verdad — probar el camino normal y llamarlo «se restaura siempre» es la misma clase de falso verde que el resto del corpus.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "mutacion_codigo.py:sin_manejador_de_señales", "apunta_a": "mutacion_codigo._restaurar_todo", "murio": false}]
  "test": [{"id": "test_restaura_el_archivo_EXACTAMENTE", "archivo": "tests/test_mutacion_codigo.py", "cubre": "el camino normal, no la terminación forzada"}]
}
```

### 015-racimo-inalcanzable

**Un racimo de módulos que se importan entre sí y nadie ejecuta**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.modulo_alcanzable`
- de dónde salió: Segtem/oracle · recursión

**Qué pasó.** Declarando una sola entrada, hay módulos que se importan unos a otros y aun así no se alcanzan desde ninguna. `proceso.modulo_con_consumidor` los daría por buenos: tienen importadores. Lo que no tienen es camino desde una entrada.

**Qué se aprendió.** «Tener importadores» y «ser alcanzable» son distintos, y hace falta el cierre TRANSITIVO para ver la diferencia. Se resolvió sin agregar un operador al álgebra: la alcanzabilidad es un HECHO que produce el sensor.

La evidencia, como relaciones:

```json
{
  "modulo": [{"nombre": "nucleo", "es_test": false, "lineas": 0, "es_paquete_vacio": true}, {"nombre": "nucleo.algebra", "es_test": false, "lineas": 232, "es_paquete_vacio": false}, {"nombre": "nucleo.dominio", "es_test": false, "lineas": 129, "es_paquete_vacio": false}, {"nombre": "nucleo.grafo", "es_test": false, "lineas": 52, "es_paquete_vacio": false}, {"nombre": "nucleo.macro", "es_test": false, "lineas": 109, "es_paquete_vacio": false}, {"nombre": "nucleo.marco", "es_test": false, "lineas": 146, "es_paquete_vacio": false}, {"nombre": "nucleo.medida", "es_test": false, "lineas": 225, "es_paquete_vacio": false}, {"nombre": "nucleo.mutacion", "es_test": false, "lineas": 170, "es_paquete_vacio": false}, {"nombre": "nucleo.mutacion_codigo", "es_test": false, "lineas": 269, "es_paquete_vacio": false}, {"nombre": "nucleo.proyecto", "es_test": false, "lineas": 129, "es_paquete_vacio": false}, {"nombre": "nucleo.simulacion", "es_test": false, "lineas": 115, "es_paquete_vacio": false}, {"nombre": "catalogos", "es_test": false, "lineas": 7, "es_paquete_vacio": false}, {"nombre": "catalogos.escalares", "es_test": false, "lineas": 37, "es_paquete_vacio": false}, {"nombre": "ejemplo", "es_test": false
  "importa": [{"a": "nucleo.dominio", "b": "nucleo.medida", "es_test": false}, {"a": "nucleo.marco", "b": "nucleo.grafo", "es_test": false}, {"a": "nucleo.medida", "b": "nucleo.algebra", "es_test": false}, {"a": "nucleo.medida", "b": "nucleo.macro", "es_test": false}, {"a": "nucleo.mutacion", "b": "nucleo.medida", "es_test": false}, {"a": "catalogos", "b": "catalogos.escalares", "es_test": false}, {"a": "catalogos.escalares", "b": "nucleo.algebra", "es_test": false}, {"a": "ejemplo.trabajo", "b": "nucleo.simulacion", "es_test": false}]
  "alcanzable": [{"desde": "nucleo.algebra", "hasta": "nucleo.algebra", "saltos": 0}]
}
```

### 016-timeout-contado-como-mutante-muerto

**Un timeout no demuestra que el test haya discriminado al mutante**

- etiqueta: `falso_verde` · se detectó por: `persona`
- medida que lo atrapa: `proceso.ronda_mutacion_concluyente`
- de dónde salió: Segtem/oracle · auditoría P0

**Qué pasó.** El arnés convertía cualquier ejecución no verde en mutante muerto. Una prueba colgada podía mejorar artificialmente el porcentaje de mutación.

**Qué se aprendió.** Muerte, timeout y error del arnés son resultados distintos; sólo una aserción fallida es evidencia discriminante.

La evidencia, como relaciones:

```json
{
  "corrida_mutacion": [{"id": "ronda-inconclusa", "mutantes": 3, "baseline_verde": true, "bytecode_frio": true, "tests_fallaron": 2, "errores_arnes": 0, "timeouts": 1}]
}
```

### 017-error-de-arnes-contado-como-mutante-muerto

**Un error del arnés no demuestra que un test haya discriminado**

- etiqueta: `falso_verde` · se detectó por: `persona`
- medida que lo atrapa: `proceso.ronda_mutacion_concluyente`
- de dónde salió: Segtem/oracle · auditoría P0

**Qué pasó.** Un ejecutable inexistente, un código de protocolo inesperado o una colección que no llegó a establecerse podían confundirse con un test que mató al mutante.

**Qué se aprendió.** El protocolo del runner es parte de la evidencia: un código desconocido deja la ronda inconclusa, nunca más verde.

La evidencia, como relaciones:

```json
{
  "corrida_mutacion": [{"id": "ronda-con-error", "mutantes": 3, "baseline_verde": true, "bytecode_frio": true, "tests_fallaron": 2, "errores_arnes": 1, "timeouts": 0}]
}
```

### 018-mutante-de-cache-borro-la-copia-del-proyecto

**Mutar el enumerador de caché hizo que la limpieza borrara la copia del proyecto**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.test_con_mutante_que_lo_mata`
- de dónde salió: Segtem/oracle · auditoría P0, ronda completa en copia temporal

**Qué pasó.** El mutante `nombre == '__pycache__'` a `!=` devolvió casi todas las entradas del repositorio como supuestos cachés. `limpiar_cache` confió en esa lista y borró la copia temporal antes de que el padre pudiera restaurar la fuente. El worktree real no fue tocado porque la ronda estaba aislada.

**Qué se aprendió.** Una lista de rutas no recibe autoridad de borrado por haber salido del enumerador. El punto de borrado vuelve a comprobar nombre exacto y confinamiento físico; como cada mutante cambia un solo sitio, las dos guardas no caen juntas.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "mutacion_codigo.py:enumerador_cache_sin_guarda", "apunta_a": "nucleo.mutacion_codigo.limpiar_cache", "murio": false}]
}
```

### 019-ronda-sin-mutantes-declarada-verde

**Una ronda sin ningún mutante podía terminar verde**

- etiqueta: `falso_verde` · se detectó por: `persona`
- medida que lo atrapa: `proceso.ronda_mutacion_concluyente`
- de dónde salió: Segtem/oracle · auditoría P0, revisión cruzada del cierre

**Qué pasó.** Con cero objetivos, cero sitios mutables o todos los sitios excluidos como equivalentes, la baseline pasaba y la CLI devolvía éxito: no había material que demostrara la calidad de los tests.

**Qué se aprendió.** Cero mutantes no significa que todos murieron. Sin material de mutación la ronda es inconclusa y debe salir con código distinto de cero.

La evidencia, como relaciones:

```json
{
  "corrida_mutacion": [{"id": "ronda-vacia", "mutantes": 0, "baseline_verde": true, "bytecode_frio": true, "tests_fallaron": 0, "errores_arnes": 0, "timeouts": 0}]
}
```

### 020-una-afirmacion-sin-alcance-alcanza

**Una sola afirmación sin alcance ya invalida el cierre**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.afirmacion_declara_alcance`
- de dónde salió: Segtem/oracle · mutación de medidas P1.1

**Qué pasó.** El mutante que aflojaba el umbral de cero a uno sobrevivía porque el caso histórico contenía tres afirmaciones defectuosas. Esta reducción demuestra que tolerar una sola sigue siendo un falso verde.

**Qué se aprendió.** El límite cero significa ninguno, no uno tolerable. Un único cierre sin alcance ya hace que la afirmación no sea verificable.

La evidencia, como relaciones:

```json
{
  "afirmacion": [{"id": "cierre", "texto": "todo está bien", "comando": "unittest", "alcance": ""}]
}
```

### 021-un-cambio-vivo-invalida-la-verificacion

**Un solo cambio de código vivo vuelve vieja la verificación**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.verificacion_vigente`
- de dónde salió: Segtem/oracle · mutación de medidas P1.1

**Qué pasó.** Aflojar el umbral de cero a uno pasaba inadvertido cuando el caso histórico traía dos archivos modificados. La unidad mínima del defecto es un único cambio vivo posterior a la verificación.

**Qué se aprendió.** La vigencia es estricta: después de cualquier cambio vivo hace falta una verificación nueva.

La evidencia, como relaciones:

```json
{
  "cambio": [{"archivo": "nucleo/medida.py", "commiteado": false, "es_codigo_vivo": true}]
}
```

### 022-un-falso-rojo-ya-rompe-el-verificador

**Un falso rojo basta para volver indigno de confianza al verificador**

- etiqueta: `falso_rojo` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.verificador_sin_falsos_rojos`
- de dónde salió: Segtem/oracle · mutación de medidas P1.1

**Qué pasó.** El caso original contenía dos falsos hallazgos y no distinguía un umbral que permitiera uno. El defecto mínimo sigue enseñando al usuario a ignorar la herramienta.

**Qué se aprendió.** El presupuesto aceptable de falsos rojos es cero; reducir el ruido no autoriza a conservar uno.

La evidencia, como relaciones:

```json
{
  "hallazgo": [{"verificador": "vault", "objetivo": "un enlace válido", "era_real": false}]
}
```

### 023-un-import-ajeno-no-es-consumidor

**Que exista otro import real no le da consumidor al módulo objetivo**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.modulo_con_consumidor`
- de dónde salió: Segtem/oracle · mutación de medidas P1.1

**Qué pasó.** Con un módulo huérfano y un import real dirigido a otro nombre, invertir la comparación entre destino y módulo hacía desaparecer el único testigo. El mismo caso fija que el umbral no puede tolerar un huérfano.

**Qué se aprendió.** Un import sólo cuenta para el módulo cuyo nombre aparece como destino; la mera existencia de actividad en el repositorio no prueba consumo.

La evidencia, como relaciones:

```json
{
  "modulo": [{"nombre": "objetivo", "tests": 1, "importadores": 0}]
  "importa": [{"a": "entrada", "b": "otro", "es_test": false}]
}
```

### 024-una-variante-no-vacia-inalcanzable

**La bolsa puede contener clasificaciones contradictorias del mismo módulo**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.modulo_alcanzable`
- de dónde salió: Segtem/oracle · mutación de medidas P1.1

**Qué pasó.** Una relación es una bolsa y no promete unicidad por nombre. Hay un módulo real inalcanzable y dos observaciones de otro nombre, una vacía y otra no vacía. `max` lo descuenta conservadoramente; cambiarlo por `min` agrega un falso testigo.

**Qué se aprendió.** Sin una restricción de unicidad declarada, el agregado debe conservar la política elegida. Además, un único módulo real inalcanzable ya viola el umbral cero.

La evidencia, como relaciones:

```json
{
  "modulo": [{"nombre": "real", "es_test": false, "lineas": 10, "es_paquete_vacio": false}, {"nombre": "ambiguo", "es_test": false, "lineas": 0, "es_paquete_vacio": true}, {"nombre": "ambiguo", "es_test": false, "lineas": 3, "es_paquete_vacio": false}]
  "alcanzable": [{"desde": "entrada", "hasta": "otro", "saltos": 1}]
}
```

### 101-mutantes-todos-muertos

**Los seis mutantes del núcleo murieron: el verde acá es correcto**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.test_con_mutante_que_lo_mata`
- de dónde salió: Brianholl/jam · sesión 2026-07-29

**Qué pasó.** Tras corregir los tests, la ronda de mutación del núcleo del oráculo mató los 6 mutantes. La medida tiene que decir verde, y si se le quita el filtro tiene que decir rojo.

**Qué se aprendió.** Un caso verde no es relleno: es lo único que prueba que el filtro filtra.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "M1_umbral_siempre_cumple", "apunta_a": "algebra._cmp", "murio": true}, {"id": "M2_donde_no_filtra", "apunta_a": "algebra.aplicar", "murio": true}, {"id": "M3_contar_da_cero", "apunta_a": "algebra.resumir", "murio": true}, {"id": "M4_campo_ausente_False", "apunta_a": "algebra.evaluar_expr", "murio": true}, {"id": "M5_sin_defensa", "apunta_a": "medida.de_datos", "murio": true}, {"id": "M6_sin_alcance", "apunta_a": "medida.de_datos", "murio": true}]
}
```

### 102-verificacion-vigente

**Después de recorrer el motor, los commits siguientes fueron sólo de documentación**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.verificacion_vigente`
- de dónde salió: Brianholl/jam · sesión 2026-07-29

**Qué pasó.** Se volvió a correr la verificación con motor y a partir de ahí sólo cambiaron documentos. `relevo.py` declaró la verificación vigente, y era cierto.

**Qué se aprendió.** La regla mira QUÉ cambió y no CUÁNTO: por eso los commits de documentación no invalidan una verificación, y eso es lo que la hace usable en vez de molesta.

La evidencia, como relaciones:

```json
{
  "verificacion": [{"que": "motor", "commit": "80373ea", "camino": "editor headless"}]
  "cambio": [{"archivo": "RELEVO.md", "commiteado": true, "es_codigo_vivo": false}, {"archivo": "Vault-kb/README.md", "commiteado": true, "es_codigo_vivo": false}]
}
```

### 103-vault-sin-falsos-rojos

**El verificador del vault, ya corregido, no reporta nada falso**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.verificador_sin_falsos_rojos`
- de dónde salió: Brianholl/jam · sesión 2026-07-29

**Qué pasó.** Tras arreglar los dos falsos positivos (la barra escapada de las tablas y los ejemplos en comillas invertidas), los hallazgos del verificador eran todos reales.

**Qué se aprendió.** Se arregla el verificador, no el documento. Y después hay que comprobar que sigue encontrando lo que sí está roto.

La evidencia, como relaciones:

```json
{
  "hallazgo": [{"verificador": "vault", "objetivo": "enlace a doc renombrado", "era_real": true}, {"verificador": "vault", "objetivo": "frontmatter sin `area`", "era_real": true}]
}
```

### 104-afirmacion-con-alcance

**La confirmación de Brian se registró con su alcance explícito**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.afirmacion_declara_alcance`
- de dónde salió: Brianholl/jam · sesión 2026-07-29

**Qué pasó.** Al cerrar la frontera de verificación se anotó que era un «todo funciona bien» GLOBAL y no gesto por gesto. La afirmación trae alcance, así que la medida dice verde.

**Qué se aprendió.** Declarar el alcance no es burocracia: es lo que permite que la afirmación siga siendo cierta cuando alguien la lea tres días después.

La evidencia, como relaciones:

```json
{
  "afirmacion": [{"id": "frontera", "texto": "Brian probó el editor y todo funciona", "comando": "editor GUI, a mano", "alcance": "global, no gesto por gesto; lo nuevo de Slate vuelve a nacer sin verificar"}, {"id": "motor", "texto": "8/8 tutoriales TODO VERDE", "comando": "verifica_ejemplos.py headless", "alcance": "carga y compilación de los tutoriales; no ejercita gestos de Slate"}]
}
```

### 105-arnes-con-cache-frio

**La segunda ronda de mutación limpió `__pycache__` entre cada mutante**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.arnes_con_bytecode_frio`
- de dónde salió: Brianholl/jam · sesión 2026-07-29

**Qué pasó.** Después de descubrir que el bytecode viejo falseaba los resultados, el arnés se rehízo limpiando el caché antes de cada corrida.

**Qué se aprendió.** El estado del bytecode sólo se publica para la mutación de código y después de comprobar cada frontera. La mutación de datos en memoria no emite un hecho de caché que no le aplica.

La evidencia, como relaciones:

```json
{
  "corrida_mutacion": [{"id": "nucleo_oracle", "mutantes": 6, "bytecode_frio": true, "rondas_cache_verificadas": 7}]
}
```

### 106-modulos-con-consumidor

**Los módulos del núcleo del oráculo sí tienen importadores**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.modulo_con_consumidor`
- de dónde salió: Brianholl/jam · sesión 2026-07-29

**Qué pasó.** Cada módulo del núcleo tiene al menos un importador que NO es un test: `algebra` lo importa `medida`, `medida` lo importan `mutacion` y `dominio`, `marco` lo importan las dos herramientas.

**Qué se aprendió.** La otra polaridad, y ahora con hechos de `importa` de verdad: sin ellos el verde era trivial porque sin pares no hay grupos que contar.

La evidencia, como relaciones:

```json
{
  "modulo": [{"nombre": "nucleo.algebra", "tests": 22, "importadores": 4}, {"nombre": "nucleo.medida", "tests": 20, "importadores": 5}, {"nombre": "nucleo.marco", "tests": 0, "importadores": 2}]
  "importa": [{"a": "nucleo.medida", "b": "nucleo.algebra", "es_test": false}, {"a": "nucleo.mutacion", "b": "nucleo.medida", "es_test": false}, {"a": "nucleo.dominio", "b": "nucleo.medida", "es_test": false}, {"a": "tools.aceptacion", "b": "nucleo.marco", "es_test": false}, {"a": "tools.mutar", "b": "nucleo.marco", "es_test": false}, {"a": "tests.test_nucleo", "b": "nucleo.algebra", "es_test": true}]
}
```

### 107-reruteo-sin-romper-sintaxis

**El re-ruteo cuidadoso dejó los 34 archivos parseando**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.sintaxis_valida_tras_edicion_masiva`
- de dónde salió: Brianholl/jam · sesión 2026-07-29

**Qué pasó.** Tras el `sed` que desindentó código, el trabajo se rehizo con un script que no ancla a principio de línea, y se comprobó el AST de cada archivo: ninguno quedó roto.

**Qué se aprendió.** Comprobar que los N archivos siguen parseando es una línea. La diferencia entre el caso 010 y este es esa línea.

La evidencia, como relaciones:

```json
{
  "edicion_masiva": [{"herramienta": "script python", "archivos": 34, "verifico_sintaxis_despues": true}]
  "archivo": [{"ruta": "oraculo/mazes/spacegraph.py", "sintaxis_valida": true}, {"ruta": "oraculo/tests/test_winnability_h9.py", "sintaxis_valida": true}]
}
```

### 108-ronda-mutacion-concluyente

**La ronda separó muertes válidas de incidentes del arnés**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.ronda_mutacion_concluyente`
- de dónde salió: Segtem/oracle · auditoría P0

**Qué pasó.** La línea base pasó y todos los subprocesos terminaron dentro del límite; los códigos de fallo declarados fueron las únicas ejecuciones contadas como mutantes muertos.

**Qué se aprendió.** Una ronda puede encontrar mutantes vivos y seguir siendo confiable; lo que la vuelve inconclusa es no saber qué ocurrió en una ejecución.

La evidencia, como relaciones:

```json
{
  "corrida_mutacion": [{"id": "ronda-concluyente", "mutantes": 3, "baseline_verde": true, "bytecode_frio": true, "tests_fallaron": 2, "errores_arnes": 0, "timeouts": 0}]
}
```

### 116-todo-el-nucleo-es-alcanzable

**Con las entradas reales declaradas, no hay módulo muerto**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.modulo_alcanzable`
- de dónde salió: Segtem/oracle · recursión

**Qué pasó.** Desde las entradas de verdad —las que importan las herramientas— se llega a todos los módulos. Los `__init__.py` vacíos no cuentan: son marcadores de paquete, y eso va como hecho.

**Qué se aprendió.** La otra polaridad, con el grafo de imports real del repositorio.

La evidencia, como relaciones:

```json
{
  "modulo": [{"nombre": "nucleo", "es_test": false, "lineas": 0, "es_paquete_vacio": true}, {"nombre": "nucleo.algebra", "es_test": false, "lineas": 232, "es_paquete_vacio": false}, {"nombre": "nucleo.dominio", "es_test": false, "lineas": 129, "es_paquete_vacio": false}, {"nombre": "nucleo.grafo", "es_test": false, "lineas": 52, "es_paquete_vacio": false}, {"nombre": "nucleo.macro", "es_test": false, "lineas": 109, "es_paquete_vacio": false}, {"nombre": "nucleo.marco", "es_test": false, "lineas": 146, "es_paquete_vacio": false}, {"nombre": "nucleo.medida", "es_test": false, "lineas": 225, "es_paquete_vacio": false}, {"nombre": "nucleo.mutacion", "es_test": false, "lineas": 170, "es_paquete_vacio": false}, {"nombre": "nucleo.mutacion_codigo", "es_test": false, "lineas": 269, "es_paquete_vacio": false}, {"nombre": "nucleo.proyecto", "es_test": false, "lineas": 129, "es_paquete_vacio": false}, {"nombre": "nucleo.simulacion", "es_test": false, "lineas": 115, "es_paquete_vacio": false}, {"nombre": "catalogos", "es_test": false, "lineas": 7, "es_paquete_vacio": false}, {"nombre": "catalogos.escalares", "es_test": false, "lineas": 37, "es_paquete_vacio": false}, {"nombre": "ejemplo", "es_test": false
  "importa": [{"a": "nucleo.dominio", "b": "nucleo.medida", "es_test": false}, {"a": "nucleo.marco", "b": "nucleo.grafo", "es_test": false}, {"a": "nucleo.medida", "b": "nucleo.algebra", "es_test": false}, {"a": "nucleo.medida", "b": "nucleo.macro", "es_test": false}, {"a": "nucleo.mutacion", "b": "nucleo.medida", "es_test": false}, {"a": "catalogos", "b": "catalogos.escalares", "es_test": false}, {"a": "catalogos.escalares", "b": "nucleo.algebra", "es_test": false}, {"a": "ejemplo.trabajo", "b": "nucleo.simulacion", "es_test": false}]
  "alcanzable": [{"desde": "nucleo.medida", "hasta": "nucleo.algebra", "saltos": 1}, {"desde": "nucleo.medida", "hasta": "nucleo.macro", "saltos": 1}, {"desde": "nucleo.medida", "hasta": "nucleo.medida", "saltos": 0}, {"desde": "nucleo.dominio", "hasta": "nucleo.algebra", "saltos": 2}, {"desde": "nucleo.dominio", "hasta": "nucleo.dominio", "saltos": 0}, {"desde": "nucleo.dominio", "hasta": "nucleo.macro", "saltos": 2}, {"desde": "nucleo.dominio", "hasta": "nucleo.medida", "saltos": 1}, {"desde": "nucleo.marco", "hasta": "nucleo.grafo", "saltos": 1}, {"desde": "nucleo.marco", "hasta": "nucleo.marco", "saltos": 0}, {"desde": "nucleo.mutacion", "hasta": "nucleo.algebra", "saltos": 2}, {"desde": "nucleo.mutacion", "hasta": "nucleo.macro", "saltos": 2}, {"desde": "nucleo.mutacion", "hasta": "nucleo.medida", "saltos": 1}, {"desde": "nucleo.mutacion", "hasta": "nucleo.mutacion", "saltos": 0}, {"desde": "nucleo.mutacion_codigo", "hasta": "nucleo.mutacion_codigo", "saltos": 0}, {"desde": "nucleo.proyecto", "hasta": "nucleo.proyecto", "saltos": 0}, {"desde": "nucleo.simulacion", "hasta": "nucleo.simulacion", "saltos": 0}, {"desde": "catalogos", "hasta": "catalogos", "saltos": 0}, {"desde": "catalogos", "has
}
```

### 301-simulador-que-ignora-la-semilla

**Un simulador que ignora la semilla no produce evidencia**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `simulacion.corrida_reproducible`
- de dónde salió: Segtem/oracle · ejemplo abstracto

**Qué pasó.** El simulador sortea sin usar la semilla: dos ejecuciones idénticas dan trazas distintas. El runner ejecuta cada corrida dos veces y lo marca.

**Qué se aprendió.** Una corrida irreproducible no es evidencia, es una anécdota. El runner lo COMPRUEBA en vez de que el simulador lo prometa.

La evidencia, como relaciones:

```json
{
  "corrida": [{"id": "roto·s1", "escenario": "roto", "semilla": 1, "pasos": 1, "razon": "completado", "determinista": false}, {"id": "roto·s2", "escenario": "roto", "semilla": 2, "pasos": 1, "razon": "completado", "determinista": false}]
  "evento": [{"corrida": "roto·s1", "t": 0, "actor": "x", "que": "azar:254156"}, {"corrida": "roto·s2", "t": 0, "actor": "x", "que": "azar:2192"}]
}
```

### 302-corridas-reproducibles

**El ejemplo de referencia es reproducible con cualquier semilla**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `simulacion.corrida_reproducible`
- de dónde salió: Segtem/oracle · ejemplo abstracto

**Qué pasó.** Tres semillas, cada una ejecutada dos veces: trazas idénticas.

**Qué se aprendió.** La otra polaridad. El determinismo se verifica en cada corrida, no se declara una vez.

La evidencia, como relaciones:

```json
{
  "corrida": [{"id": "alcanza·s1", "escenario": "alcanza", "semilla": 1, "pasos": 5, "razon": "completado", "determinista": true, "sobro": 15}, {"id": "alcanza·s2", "escenario": "alcanza", "semilla": 2, "pasos": 6, "razon": "completado", "determinista": true, "sobro": 14}, {"id": "alcanza·s3", "escenario": "alcanza", "semilla": 3, "pasos": 4, "razon": "completado", "determinista": true, "sobro": 16}]
}
```

### 303-el-presupuesto-no-alcanzo

**Un trabajo grande contra un presupuesto chico: la corrida no observa el sistema**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `simulacion.no_se_agoto_el_presupuesto`
- de dónde salió: Segtem/oracle · ejemplo abstracto

**Qué pasó.** 60 unidades de trabajo, rendimiento de hasta 2 por paso y 10 pasos de presupuesto: las tres corridas terminan por «tope» sin completar nada.

**Qué se aprendió.** Una corrida que se quedó sin pasos observó el presupuesto, no el sistema. Cualquier conclusión que salga de ahí habla de la paciencia del que simuló.

La evidencia, como relaciones:

```json
{
  "corrida": [{"id": "no-alcanza·s1", "escenario": "no-alcanza", "semilla": 1, "pasos": 10, "razon": "tope", "presupuesto_agotado": true, "determinista": true, "falto": 45}, {"id": "no-alcanza·s2", "escenario": "no-alcanza", "semilla": 2, "pasos": 10, "razon": "tope", "presupuesto_agotado": true, "determinista": true, "falto": 47}, {"id": "no-alcanza·s3", "escenario": "no-alcanza", "semilla": 3, "pasos": 10, "razon": "tope", "presupuesto_agotado": true, "determinista": true, "falto": 46}]
}
```

### 304-el-presupuesto-alcanzo

**Con presupuesto suficiente ninguna corrida se corta**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `simulacion.no_se_agoto_el_presupuesto`
- de dónde salió: Segtem/oracle · ejemplo abstracto

**Qué pasó.** Las tres corridas terminan por «completado» antes de agotar los 20 pasos.

**Qué se aprendió.** La otra polaridad: sin ella, aflojar el umbral de la medida pasaría inadvertido.

La evidencia, como relaciones:

```json
{
  "corrida": [{"id": "alcanza·s1", "escenario": "alcanza", "semilla": 1, "pasos": 5, "razon": "completado", "presupuesto_agotado": false, "determinista": true, "sobro": 15}, {"id": "alcanza·s2", "escenario": "alcanza", "semilla": 2, "pasos": 6, "razon": "completado", "presupuesto_agotado": false, "determinista": true, "sobro": 14}, {"id": "alcanza·s3", "escenario": "alcanza", "semilla": 3, "pasos": 4, "razon": "completado", "presupuesto_agotado": false, "determinista": true, "sobro": 16}]
}
```

### 305-traza-con-hueco

**Un simulador que no registra un paso deja la traza agujereada**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `simulacion.la_traza_no_tiene_huecos`
- de dónde salió: Segtem/oracle · orden

**Qué pasó.** La corrida ocurrió entera pero el instante 1 no quedó registrado: hay menos eventos que instantes, y nada en la traza lo delata a simple vista.

**Qué se aprendió.** El ORDEN es un campo del hecho, no una propiedad de la relación: una relación es un conjunto y los conjuntos no tienen orden. Por eso los huecos se detectan con aritmética sobre el campo ordinal, no con un operador nuevo.

La evidencia, como relaciones:

```json
{
  "corrida": [{"id": "alcanza·s1", "escenario": "alcanza", "semilla": 1, "pasos": 5, "razon": "completado", "determinista": true, "sobro": 15}, {"id": "alcanza·s2", "escenario": "alcanza", "semilla": 2, "pasos": 6, "razon": "completado", "determinista": true, "sobro": 14}]
  "evento": [{"corrida": "alcanza·s1", "t": 0, "actor": "trabajo", "que": "empieza", "falta": 8}, {"corrida": "alcanza·s1", "t": 2, "actor": "trabajo", "que": "avanza", "falta": 4}, {"corrida": "alcanza·s1", "t": 3, "actor": "trabajo", "que": "avanza", "falta": 3}, {"corrida": "alcanza·s1", "t": 4, "actor": "trabajo", "que": "avanza", "falta": 1}, {"corrida": "alcanza·s1", "t": 5, "actor": "trabajo", "que": "avanza", "falta": 0}, {"corrida": "alcanza·s2", "t": 0, "actor": "trabajo", "que": "empieza", "falta": 8}, {"corrida": "alcanza·s2", "t": 2, "actor": "trabajo", "que": "avanza", "falta": 6}, {"corrida": "alcanza·s2", "t": 3, "actor": "trabajo", "que": "avanza", "falta": 5}, {"corrida": "alcanza·s2", "t": 4, "actor": "trabajo", "que": "avanza", "falta": 3}, {"corrida": "alcanza·s2", "t": 5, "actor": "trabajo", "que": "avanza", "falta": 2}, {"corrida": "alcanza·s2", "t": 6, "actor": "trabajo", "que": "avanza", "falta": 0}]
}
```

### 306-traza-completa

**La traza del ejemplo registra todos sus instantes**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `simulacion.la_traza_no_tiene_huecos`
- de dónde salió: Segtem/oracle · orden

**Qué pasó.** Tantos eventos como instantes, del cero al último.

**Qué se aprendió.** La otra polaridad.

La evidencia, como relaciones:

```json
{
  "corrida": [{"id": "alcanza·s1", "escenario": "alcanza", "semilla": 1, "pasos": 5, "razon": "completado", "determinista": true, "sobro": 15}, {"id": "alcanza·s2", "escenario": "alcanza", "semilla": 2, "pasos": 6, "razon": "completado", "determinista": true, "sobro": 14}]
  "evento": [{"corrida": "alcanza·s1", "t": 0, "actor": "trabajo", "que": "empieza", "falta": 8}, {"corrida": "alcanza·s1", "t": 1, "actor": "trabajo", "que": "avanza", "falta": 7}, {"corrida": "alcanza·s1", "t": 2, "actor": "trabajo", "que": "avanza", "falta": 4}, {"corrida": "alcanza·s1", "t": 3, "actor": "trabajo", "que": "avanza", "falta": 3}, {"corrida": "alcanza·s1", "t": 4, "actor": "trabajo", "que": "avanza", "falta": 1}, {"corrida": "alcanza·s1", "t": 5, "actor": "trabajo", "que": "avanza", "falta": 0}, {"corrida": "alcanza·s2", "t": 0, "actor": "trabajo", "que": "empieza", "falta": 8}, {"corrida": "alcanza·s2", "t": 1, "actor": "trabajo", "que": "avanza", "falta": 7}, {"corrida": "alcanza·s2", "t": 2, "actor": "trabajo", "que": "avanza", "falta": 6}, {"corrida": "alcanza·s2", "t": 3, "actor": "trabajo", "que": "avanza", "falta": 5}, {"corrida": "alcanza·s2", "t": 4, "actor": "trabajo", "que": "avanza", "falta": 3}, {"corrida": "alcanza·s2", "t": 5, "actor": "trabajo", "que": "avanza", "falta": 2}, {"corrida": "alcanza·s2", "t": 6, "actor": "trabajo", "que": "avanza", "falta": 0}]
}
```

### 307-una-corrida-no-reproducible-alcanza

**Una corrida no reproducible basta para invalidar la evidencia**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `simulacion.corrida_reproducible`
- de dónde salió: Segtem/oracle · mutación de medidas P1.1

**Qué pasó.** El caso original tenía dos corridas no deterministas y permitía que el umbral mutado tolerase una. La evidencia mínima deja claro que no existe ese margen.

**Qué se aprendió.** La reproducibilidad es una condición de admisión individual: una sola corrida no determinista invalida su uso como evidencia.

La evidencia, como relaciones:

```json
{
  "corrida": [{"id": "roto·s1", "escenario": "roto", "semilla": 1, "pasos": 1, "razon": "completado", "determinista": false}]
}
```

### 308-una-corrida-agota-el-presupuesto

**Una sola corrida que termina por tope observó el presupuesto**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `simulacion.no_se_agoto_el_presupuesto`
- de dónde salió: Segtem/oracle · mutación de medidas P1.1

**Qué pasó.** Tres agotamientos mataban el umbral original pero no distinguían permitir uno. La reducción conserva exactamente el defecto relevante.

**Qué se aprendió.** El umbral cero no admite una corrida agotada: esa corrida habla del tope, no del sistema.

La evidencia, como relaciones:

```json
{
  "corrida": [{"id": "no-alcanza·s1", "escenario": "no-alcanza", "semilla": 1, "pasos": 10, "razon": "tope", "presupuesto_agotado": true, "determinista": true, "falto": 45}]
}
```

### 309-una-traza-con-un-hueco

**Una única traza agujereada ya invalida la ronda**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `simulacion.la_traza_no_tiene_huecos`
- de dónde salió: Segtem/oracle · mutación de medidas P1.1

**Qué pasó.** El fixture anterior contenía dos corridas con huecos. Una traza con los instantes 0 y 2 demuestra que permitir una corrida defectuosa también sería un falso verde.

**Qué se aprendió.** La continuidad se exige por corrida. Un solo grupo con menos registros que `ultimo + 1` alcanza para poner la medida en rojo.

La evidencia, como relaciones:

```json
{
  "evento": [{"corrida": "r1", "t": 0, "actor": "trabajo", "que": "empieza"}, {"corrida": "r1", "t": 2, "actor": "trabajo", "que": "termina"}]
}
```

---

<!-- fuente: 05-el-nucleo.md -->

## El núcleo, módulo por módulo

Los docstrings enteros: ahí vive el razonamiento y las decisiones descartadas, que es lo que no se puede reconstruir leyendo el código.

### `nucleo/algebra.py`

*593 líneas*

El álgebra: relaciones, expresiones y los operadores. Sin dependencias.

Una **fila de trabajo** es un mapa `alias → hecho`, más las columnas derivadas bajo la clave
reservada `_`. Toda operación toma filas y devuelve filas: eso es la clausura.

El lenguaje activo tiene cinco operadores: `de`, `donde`, `resumen`, `unir` y `agrupar`.

### `nucleo/diferencial.py`

*167 líneas*

Contrato de procedencia y frescura de los fixtures diferenciales.

Las huellas no prueban que una referencia sea correcta. Prueban algo más modesto y necesario: que
el fixture que se está releyendo fue generado con el emisor, la referencia, el catálogo y la
configuración que dice haber usado.

### `nucleo/dominio.py`

*151 líneas*

Un dominio verificado, declarado en vez de escrito.

Es la parte de «herramienta que crea herramientas». Incorporar un dominio con verificación suele
repetir la misma estructura:
armar el escenario, extraer los hechos, inyectar un defecto, correr la implementación de referencia,
comprobar las polaridades, escribir el fixture. Igual que las 22 medidas con la misma forma, eso se
declara.

### Qué declara un dominio

    Dominio(
        nombre     = "ejemplo",
        montar     = lambda defecto, i: …,  # arma el escenario n° i, con el defecto puesto o sin ninguno
        hechos     = lambda ctx: {...},   # el SENSOR: contexto → relaciones. No juzga.
        referencia = lambda ctx: bool,    # la implementación INDEPENDIENTE: ¿le parece bien?
        defectos   = ("nombre_roto", …),
    )

### Lo que se va: `espera()`

Los arneses a mano traían una función que decía, medida por medida, qué debería dar cada una. Eso
**reimplementa las medidas en Python**: dos definiciones de lo mismo que nadie mantiene sincronizadas
— el mismo defecto que los testigos duplicados del caso `004`.

Acá no existe. El fixture guarda sólo **los hechos y el veredicto de la referencia**, que es la única
información independiente que hay. La comprobación es global: *las medidas del dominio, todas juntas,
dan verde exactamente cuando la referencia da verde*. Reclamar granularidad por medida era inventar
información que la referencia no daba.

### La guarda de polaridad

Sin evidencia de los dos signos una medida no queda fijada: `aflojar_umbral` sólo lo detecta un caso
rojo, y quitarle el filtro sólo se nota si hay filas que no ofenden. Así que `generar` **se niega a
escribir** el fixture si alguna medida del dominio sale siempre igual. Eso lo comprobaban dos de los
instrumentos existentes; omitirla deja medidas sin fijar aunque el acuerdo global parezca correcto.

### `nucleo/fixtures.py`

*269 líneas*

Lector único y fail-closed de fixtures diferenciales versionados.

Los consumidores no deben conocer la forma física del fixture. Este módulo valida las dos formas
de ``oracle.diferencial/v1`` y las proyecta como evidencias o casos asociados a una medida. Así
``medida --relaciones``, la revisión, el diferencial y la mutación leen exactamente el mismo dato.

### `nucleo/grafo.py`

*52 líneas*

Cierre transitivo — del lado del SENSOR, no del álgebra.

La especificación tenía abierta la recursión: «alcanzable desde» no se expresa con los operadores, y
es la misma pared que hizo falta `WITH RECURSIVE` en SQL.

### La decisión: no entra al álgebra

Agregar un operador `cierre` habría sido meter recursión en un lenguaje que se mantiene chico a
propósito, con **un solo usuario** — justo lo que la regla del repositorio prohíbe. Y hay una salida
que además es más fiel a la doctrina: **la alcanzabilidad es un HECHO**, y producir hechos es trabajo
del sensor.

    alcanzable(desde, hasta, saltos)

El álgebra la mide como cualquier otra relación, sin saber nada de grafos. El sensor la calcula, y
oracle pone el ayudante para que ningún sensor tenga que reimplementar un BFS — que era el otro riesgo,
el de acumular la misma función en cada dominio.

No es una evasión: es la misma línea que separa al sensor del juez en todo lo demás. El sensor mira el
mundo y no opina; el álgebra opina y no mira el mundo.

### `nucleo/macro.py`

*109 líneas*

Macros: medidas que escriben medidas.

De las 27 medidas del catálogo, **22 tenían exactamente la misma forma**:

    ["desde", ["de", R, x], ["donde", P]] · ["resumen","contar",1] · ["umbral","<=",0, …]

La regla del repositorio decía que las macros se habilitan «cuando aparezca la quinta medida con la
misma forma». Aparecieron veintidós. Sin macro, escribir la medida 28 es la misma ceremonia que la 1,
y cambiar esa forma alguna vez serían 22 archivos.

### Por qué esto no cuesta inspeccionabilidad

Una macro **expande a los mismos datos**, igual que en LISP: la expansión ocurre antes de construir la
medida, así que el evaluador, la mutación, el inventario y el nivel L2 siguen viendo formas canónicas
y no se enteran de que hubo macro. `tools/medida.py --expandir` muestra el resultado.

### `peor` cierra una deuda de diseño

El caso `012` del corpus anotaba que en el patrón «`donde tol` → `max` → `umbral tol`» la tolerancia
aparecía **dos veces** y nada las mantenía juntas. La macro la recibe **una sola vez** y genera las
dos. La deuda desaparece por construcción, que es mejor que comprobarla.

### Las macros son azúcar, no un embudo

La forma canónica sigue siendo válida y hay medidas que no pasan por macro (`colocacion.interpenetracion`
une DOS relaciones distintas y resume por `max`). Un sistema de macros que obliga a todo a pasar por él
se vuelve una camisa de fuerza: si la forma no encaja, se escribe canónica y listo.

### `nucleo/marco.py`

*102 líneas*

Sensores del propio marco: hechos sobre los casos y sobre el uso de cada medida.

El norte de oracle es el universo de problemas de **crear una herramienta**, y una parte de ese
universo es la herramienta misma: si el corpus fija las medidas, si alguna quedó sin ejercitar, si un
caso reclama algo que no existe. Eso hasta ahora se decidía con `if`s dentro de `tools/` — o sea que
el veredicto sobre el marco estaba en código imperativo mientras el resto del proyecto exige que los
veredictos sean datos. Es el mismo pecado que un sensor que juzga, un nivel más arriba.

Acá se producen los hechos; el juicio queda en `catalogos/meta/`.

    caso(id, medida, tiene_medida, medida_existe, esperado_ok, dio_ok, explica_el_hueco)
    medida_en_uso(id, casos_que_la_evaluan, mutantes, mutantes_vivos)

### Por qué no hay nulos

Un caso sin medida usable **no tiene veredicto que comparar**. La tentación es poner `null` en
`esperado_ok`/`dio_ok`, y eso choca de frente con una decisión del álgebra: comparar contra un valor
ausente **levanta un error**, porque un `False` silencioso convierte un campo mal escrito en un verde.

Así que en esos casos los dos campos se igualan a propósito: la medida de coincidencia no tiene nada
que decir ahí, y de la falta se ocupa otra medida (`meta.el_caso_reclama_una_medida_que_existe`). Cada
pregunta a la medida que le corresponde, en vez de un nulo que todas tienen que esquivar.

Eso también es el síntoma de un hueco declarado del álgebra: la **ausencia** todavía no se expresa, y
hasta que `agrupar` exista se rodea así.

### `nucleo/medida.py`

*300 líneas*

La medida: un dato que se lee, se evalúa y se puede medir a su vez.

Forma canónica, tal como se guarda en `catalogos/`:

```json
["medida", "<id>",
  ["desde", ["de", "<relacion>", "<alias>"], ["donde", <pred>]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "<la defensa del número>"],
  ["alcance", "<qué NO ve>"]]
```

Dos campos son obligatorios y son la razón de ser del módulo: **`alcance`**, para que un informe en
verde no pueda decir «todo bien» a secas, y **la defensa del umbral**, para que el número se pueda
discutir. Una medida sin uno de los dos no se carga: falla al leerse, no al usarse.

Los **testigos no se declaran**: son las filas con las que terminó la tubería. Declararlos aparte
obliga a escribir la misma condición dos veces y a mantenerlas sincronizadas a mano — el caso
`004-testigos-duplicados` del corpus.

### `nucleo/mutacion.py`

*332 líneas*

Mutación de MEDIDAS — la prueba de si el corpus alcanza para fijarlas.

Si una medida es un dato, mutarla es transformar el dato: no se toca ningún archivo, no hay
`__pycache__` que invalidar y no hay forma de que el resultado dependa de bytecode viejo. Ésa es la
diferencia concreta entre esto y el `sed` a mano que produjo el caso `006` del corpus.

### Qué se está midiendo, exactamente

Para cada caso del corpus que declara una medida, el caso **espera rojo** (es un defecto real). Se
muta la medida y se vuelve a evaluar contra la misma evidencia:

  · si el caso pasa a **verde** ⇒ el mutante **murió**: el caso sí fija ese aspecto de la medida;
  · si el caso **sigue en rojo** ⇒ el mutante **sobrevivió**: el caso NO fija ese aspecto. Se podría
    escribir la medida de otra forma y el corpus no se daría cuenta.

Los sobrevivientes son la lista de lo que el corpus deja libre — y por lo tanto lo que puedo escribir
mal sin que nada me frene. Es el mismo argumento que la mutación de tests, un nivel más arriba.

El denominador se declara en `mutantes`: además de umbral y filtros completos, recorre fuentes,
expresiones, agregados y referencias de campo. La mutación del código Python es otro sensor,
`perfiles.python.mutacion_codigo`; no se mezcla con ésta porque su arnés y sus fallos posibles son
distintos.

### `nucleo/proyecto.py`

*381 líneas*

A qué proyecto se le mide. Oracle es la herramienta; el proyecto es de otro.

Las herramientas tenían la ruta del catálogo clavada en el propio repositorio, y eso las volvía
inútiles para cualquier otro: podías escribir medidas de tu dominio y no había forma de correrlas.
Una herramienta que sólo sabe medirse a sí misma no es multipropósito.

Un **proyecto** es cualquier directorio con esta forma. Nada más:

    <proyecto>/
      catalogos/     las medidas, agrupadas por dominio
      corpus/        los casos donde la medición dijo bien y no estaba bien
      diferencial/   los fixtures contra implementaciones independientes

Se resuelve en este orden, y el primero que aparece gana:

    --proyecto <ruta>        explícito
    $ORACLE_PROYECTO         para no repetirlo en cada comando
    el directorio actual     si tiene `catalogos/`
    el repositorio de oracle si no hay nada más — para que oracle pueda medirse a sí mismo

### `nucleo/simulacion.py`

*198 líneas*

Modo simulación — la segunda fuente de evidencia, y la mitad GPSS del asunto.

Hasta acá el oráculo consulta **hechos estáticos**: registros, artefactos, mutantes. GPSS hace
otra cosa: **corre el sistema y reporta lo que pasó**. Eso da una clase de evidencia que la primera
mitad no puede producir.

### No es otro oráculo: es otro sensor

Una traza es una relación. Los mismos operadores la miden, no hace falta un álgebra nueva:

    evento(corrida, t, actor, que, …)                          lo que fue pasando
    corrida(id, escenario, semilla, pasos, razon, determinista)  cómo terminó

El simulador **no juzga**. Devuelve hechos, igual que cualquier sensor. Lo que decide si el resultado
está bien son medidas declaradas, con su umbral y su punto ciego, como todas las demás.

### Por qué esta mitad importa

Es la más difícil de sastrear. Un umbral se afloja cambiando un número; **lo que emerge de correr el
sistema, no**. Una propiedad estática se cumple o no; una simulación te dice qué pasó *de verdad* con
un presupuesto finito y sin información perfecta.

Y produce el desacuerdo que más enseña: **«es posible» y «pasa» no son lo mismo.** Un resolvedor con
información perfecta contesta la primera; un proceso con recursos limitados contesta la segunda. Los
escenarios donde difieren son los que hay que mirar, y ningún oráculo de propiedad puede verlos.

El dominio es indiferente: una cola con servidores, un recorrido sobre una topología, o los turnos de
dos agentes trabajando un repositorio. Ninguno «gana» — todos **terminan por una razón**.

### Determinismo: el runner lo comprueba, no lo promete

Una corrida no reproducible no puede ser material de corpus: mañana da otra cosa y el caso deja de
significar algo. Así que **cada corrida se ejecuta dos veces con la misma semilla** y si las trazas no
son idénticas, `determinista` sale `false` — un hecho más, que juzga una medida. No es una promesa del
docstring: es evidencia.

---

<!-- fuente: 06-las-herramientas.md -->

## Las herramientas

Cada una existe por un motivo que está escrito en su encabezado. Varias nacieron de un defecto concreto del corpus.

### `tools/aceptacion.py`

*133 líneas*

La prueba de aceptación del marco: **el corpus juzga al oráculo, no al revés.**

    python tools/aceptacion.py [--proyecto <ruta>] [--confiar-escalares]

Criterio 4 de la especificación, ejecutable:

  · todo caso de defecto que **declara** una medida tiene que ponerse en **ROJO** con esa medida;
  · todo caso `verde_correcto` tiene que salir **VERDE**. Son la otra polaridad, y no son relleno:
    sin ellos `quitar_filtro` sobrevive siempre, porque contar sin filtro sólo da verde con la
    relación vacía. Un corpus de puros defectos deja las medidas flojas;
  · los casos sin medida distinguen `abierto`, `resuelto` y `limite_humano`; sólo los abiertos son
    deuda del marco y su número tiene que bajar;
  · y al final corre el nivel L2: las medidas del catálogo servidas **como relación**, medidas por
    una medida. Sin mecanismo nuevo — es lo que vuelve esto un metalenguaje.

Sale != 0 si algún caso que debía ponerse rojo salió verde.

### `tools/cifras.py`

*74 líneas*

Genera y comprueba las cifras técnicas publicadas en el README de Oracle.

### `tools/corpus.py`

*174 líneas*

Verificador del corpus — la primera regla del repositorio, y se aplica a sí mismo.

    python tools/corpus.py            → verifica (sale != 0 si algo está mal)
    python tools/corpus.py --resumen  → verifica y además cuenta qué mecanismo atrapa qué

Comprueba lo que se degrada solo:

  1. **el esquema** de cada caso, y que el `id` sea el nombre del archivo;
  2. **la forma de la evidencia**: un mapa de relación → filas de campos ESCALARES. Es el contrato
     L0 de la especificación, y si se afloja acá se afloja en todo el resto;
  3. **que ningún caso se caiga en silencio**: un caso sin medida declara si sigue abierto, quedó
     resuelto por construcción o documenta un límite humano no automatizable.

La 3 es la que importa. Los casos incómodos —los que el marco todavía no puede medir— son
justamente los que no hay que perder: son la lista de lo que falta.

### `tools/diferencial.py`

*164 líneas*

La prueba diferencial: el álgebra contra una implementación independiente.

    python tools/diferencial.py [--proyecto <ruta>] [--confiar-escalares]

Re-juzga la evidencia versionada con las medidas actuales, comprueba primero su procedencia y compara
por separado el acuerdo global con la referencia y la estabilidad de cada veredicto de Oracle.
Sale != 0 ante un fixture inválido, vencido o cualquier desacuerdo.

### `tools/ejecutar_suite_mutacion.py`

*78 líneas*

Runner `unittest` con un protocolo de salida inequívoco para mutación de código.

0 significa que la suite pasó; 1, que un test falló o terminó con una excepción; 2, que el arnés no
pudo establecer una suite (descubrimiento inválido, runner roto o cero tests). La línea base verde es
la que permite atribuir al mutante un error posterior dentro del código ejercitado.

### `tools/estudio.py`

*392 líneas*

Vuelca todo el repositorio a Markdown plano y autocontenido, para subirlo y estudiarlo.

    python tools/estudio.py [--proyecto <ruta>] [--destino estudio] [--confiar-escalares]
    python tools/estudio.py --archivo ORACLE-PARA-NOTEBOOKLM.md

Pensado para NotebookLM y parientes: ingieren **documentos planos**, no repositorios. Así que acá no
hay enlaces relativos, ni wikilinks, ni referencias a archivos que el lector no tiene. Cada documento
se explica solo.

Tres cosas que no son «copiar y pegar», y son la razón de que esto sea un generador y no una carpeta
mantenida a mano:

  1. **el catálogo y el corpus son JSON**, y crudos se leen mal. Acá salen como prosa y tablas, con la
     medida expandida a su forma canónica al lado de cómo está escrita.
  2. **los mensajes de commit tienen buena parte del «por qué»** — las correcciones, los mutantes que
     sobrevivieron, lo que se descubrió a mitad de camino. Si sólo se suben los documentos, se pierde
     justo lo que más sirve para entender por qué las cosas son como son.
  3. **los docstrings del núcleo tienen el razonamiento**, no el código. Van enteros.

### `tools/medida.py`

*268 líneas*

Escribir una medida sin pedirle permiso a nadie.

    python tools/medida.py --relaciones            qué hechos hay para medir, y sus campos
    python tools/medida.py --escalares             qué funciones de dominio se pueden usar
    python tools/medida.py --nueva dominio.nombre  crea el archivo con la forma puesta
    python tools/medida.py <archivo.json>          la revisa y la corre contra el corpus
    python tools/medida.py --expandir <archivo>     ve en qué forma canónica se convierte la macro

Para ejecutar `escalares.py` de otro proyecto hace falta `--confiar-escalares`. Ayuda,
`--relaciones`, `--nueva` y el inventario base de `--escalares` nunca ejecutan ese archivo.

Existe porque sin esto el lenguaje tiene dueño. Todo el argumento de este repositorio es que quien
ve un defecto pueda escribir la regla que lo atrapa; si para eso hay que escribir s-expresiones en
JSON a mano y adivinar qué relaciones existen, el único que puede hacerlo es quien escribió el
evaluador — y ahí volvemos al problema del principio.

`--relaciones` no es una lista mantenida a mano: sale de la evidencia que hay en el corpus y en los
fixtures. Si aparece un hecho nuevo, aparece acá solo.

### `tools/mutar.py`

*122 líneas*

Muta las medidas y mide el resultado CON LAS MEDIDAS. El bucle se cierra acá.

    python tools/mutar.py [--confiar-escalares]          → informe
    python tools/mutar.py --hechos [--confiar-escalares] → evidencia JSON

El sensor produce hechos y las políticas aplicables del catálogo pueden juzgarlos. Un proyecto
neutral no necesita importar esas políticas para obtener el resultado operativo de la mutación.

Sale != 0 si algún mutante sobrevivió, porque un mutante que sobrevive es un aspecto de la medida que
el corpus no fija.

### `tools/mutar_codigo.py`

*254 líneas*

Muta el CÓDIGO del núcleo y mide el resultado con las medidas del catálogo.

    python tools/mutar_codigo.py                 → informe
    python tools/mutar_codigo.py --hechos        → volcar la evidencia (JSON)
    python tools/mutar_codigo.py --timeout 90    → límite por ejecución de tests
    python tools/mutar_codigo.py --manifiesto progreso.json [--reanudar]

Cada ronda copia el proyecto a un directorio temporal y sólo muta esa copia. Un bloqueo impide dos
rondas sobre la misma raíz; timeout y señales terminan el grupo de procesos y limpian el aislamiento.

Sale 1 si algún mutante sobrevivió y 2 si la ronda fue inconclusa. Timeout, error del arnés y fallo de
tests son estados distintos; sólo el último demuestra que el mutante murió.

### `tools/sesion.py`

*15 líneas*

Frontera común entre errores de proyecto y los códigos de salida de los entry points.

### `tools/verificar_instalacion.py`

*160 líneas*

Construye el wheel y prueba la API pública desde un entorno y cwd aislados.

---

<!-- fuente: 07-el-diario.md -->

## El diario: por qué las cosas son como son

Los mensajes de commit, del más viejo al más nuevo. Acá vive buena parte del
razonamiento —y casi todas las correcciones—: qué se intentó, qué salió mal, qué mutante
sobrevivió, qué afirmación hubo que retirar. Leído en orden, es la historia de un autor
equivocándose y siendo atrapado por lo que estaba construyendo.

### 2026-07-29 — El corpus primero: 11 casos donde la medición dijo bien y no estaba bien

*commit 5d28f64*

oracle es un modo de estructurar el problema de construir herramientas con un
LLM. El problema tiene nombre —Goodhart— y con un LLM es estructural, no un
descuido: escribe la herramienta y su verificador con la misma mano, y no tiene
memoria entre sesiones, así que una regla escrita como consejo se lee y se
olvida. Tiene que negarse.

Este primer commit NO trae evaluador a propósito. Trae el corpus y la
especificación, en ese orden, porque el corpus es lo único que se pierde: un LLM
no recuerda sus fallas, y un corpus escrito después del framework se escribe para
que pase.

Los 11 casos salen de UNA sesión construyendo el plugin Jam, capturados el mismo
día en que ocurrieron. Cada uno trae la evidencia como relaciones, así que se
puede volver a juzgar cuando exista el evaluador.

Lo que dicen los números, que es la medición que justifica el repositorio:

    8 de 11   falsos verdes — el modo de falla dominante
    4         los vio una persona
    3         los atrapó la MUTACIÓN  ← el único mecanismo sistemático
    3         aparecieron de casualidad haciendo otra cosa
    1         lo detectó una herramienta ajena (un parser)

NINGUNO lo atrapó un verificador propio por diseño. El proyecto tenía 489 tests
en verde, un verificador de documentación y otro de entrega, y los 11 pasaron por
el costado. De ahí que la primera medida a escribir sea
`proceso.test_con_mutante_que_lo_mata`: tres casos la reclaman y la mutación es el
único detector que ya se pagó solo.

ESPECIFICACION.md fija el álgebra: hechos y relaciones (L0), la medida COMO DATO,
seis operadores con clausura, las funciones escalares como UDF, y el modo
simulación como segunda fuente de evidencia. Tres influencias y qué aporta cada
una: SQL el álgebra, GPSS la simulación, LISP la representación — sin la última el
lenguaje tiene dueño, y el dueño sería el LLM.

Trae también lo que NO tiene y sus preguntas abiertas sin maquillar: la ausencia
(anti-join) mete el concepto de nulo, la recursión no se expresa con los seis
operadores, la igualdad de flotantes es una trampa, y el orden no está resuelto.
Una especificación que finge no tener huecos es peor que una con huecos marcados.

`tools/corpus.py` es la primera regla del repo y se aplicó a sí misma: en su
primera corrida rechazó un caso MÍO por meter una lista dentro de un campo, que
viola el contrato L0. Se corrigió el caso —los desvíos pasaron a ser una relación
propia—, no el verificador.

Comprueba tres cosas: el esquema, que la evidencia sean filas de campos
escalares, y que ningún caso se caiga en silencio — si todavía no hay medida que
lo atrape, hay que decir por qué en `sin_medida_todavia`. Esa última es la que
importa: los casos que el marco no puede medir son la lista de lo que falta, y
son justo los que alguien borraría por prolijidad. Hoy hay dos.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — espec: el criterio 4 era imposible de cumplir como estaba escrito

*commit 7521100*

Decía «cada caso del corpus se pone en rojo». Pero dos de los once casos declaran
`sin_medida_todavia` —uno es un defecto del lenguaje, el otro una atribución
causal errada que no sé mecanizar—, así que con esa redacción el criterio no se
puede cumplir nunca y se convierte en algo que se ignora.

Corregido: todo caso que DECLARA una medida se pone en rojo con esa medida; los
que declaran hueco siguen verdes a propósito. Y se agrega la métrica que faltaba:
el número de casos sin medida tiene que BAJAR. Sin eso, declarar el hueco sería
una forma prolija de archivarlo.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — El evaluador: tres operadores, ocho medidas, y el corpus juzgando al oráculo

*commit 988bcfe*

Pasos 1 y 2. El álgebra de la especificación, implementada, y las medidas que el
corpus reclamaba — escritas como ARCHIVOS DE DATOS en `catalogos/`, no como
código, que es la tesis del repo puesta a prueba en su primer uso.

Se implementaron TRES de los seis operadores: `de`, `donde`, `resumen`. Son los
únicos que piden las ocho medidas que existen; ninguna necesita `unir`, `agrupar`
ni `con`. La regla del documento —«no se agrega un operador hasta que una segunda
medida lo necesite»— aplica también a implementarlos, porque un operador sin
usuario es un operador sin verificar. Los tres que faltan levantan un error que
dice su disparador, así que cuando hagan falta no hay que adivinar por qué no
están.

`tools/aceptacion.py` invierte quién juzga a quién: el corpus juzga al oráculo.
Los 9 casos que declaran una medida se ponen en ROJO; los 2 que declaran hueco
siguen verdes a propósito, y su número es una métrica del marco que tiene que
bajar. Y corre el nivel L2: el catálogo servido como relación y medido por una
medida, sin mecanismo nuevo — que es lo que vuelve esto un metalenguaje y no una
biblioteca.

El L2 disparó en la primera corrida, sobre mi propio catálogo: el `alcance` de
`proceso.modulo_con_consumidor` describía su límite con «SIN distinguir» y nunca
lo enunciaba en negativo. Ahí había una tentación que vale nombrar: retocar el
texto sólo para que pase el match de string habría sido Goodhart en miniatura. Se
reescribió de verdad, y quedó mejor redactado además de conforme.

Mutación con caché frío desde el arranque (la lección del caso 006): 6 mutantes,
los 6 mueren. Pero el resultado interesante es otro — TRES de ellos dejan la
aceptación en VERDE. El replay del corpus ejercita la evaluación; las reglas de
declaración (que el umbral traiga defensa, que el alcance no esté vacío) sólo las
cubren los tests. Son dos oráculos complementarios y ninguno alcanza solo: queda
escrito en el README para no confundir el verde de uno con el del otro.

32 tests en `unittest` puro. El repo sigue sin dependencias, ni de desarrollo: el
oráculo viejo de Jam tenía 13 archivos escritos para pytest sin pytest instalado y
0 tests corriendo durante 8 días. Y sí, `tests/` necesitó su `__init__.py` — el
mismo tropiezo, atajado en el primer intento.

La especificación pasa a 0.2 con dos correcciones que encontró la implementación:
el acceso a datos es explícito (`["campo", alias, nombre]`, `["hecho", alias]`)
porque un string suelto que signifique «alias» hace que un dato de texto cambie de
sentido según el contexto; y comparar contra un campo ausente levanta error en vez
de devolver False, porque un False silencioso convierte un nombre mal escrito en un
verde.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — El sensor de mutación, y lo que descubrió: al corpus le faltaba una polaridad

*commit f6360d2*

Paso 3. El sensor produce hechos y el álgebra los juzga: `tools/mutar.py` muta las
MEDIDAS y sus hechos `mutante(id, apunta_a, murio)` los mide una medida del
catálogo, `proceso.test_con_mutante_que_lo_mata`. El bucle se cierra: el marco se
mide con sus propias reglas.

Reordené respecto de lo que había escrito en el testigo, y lo digo en vez de
sustituirlo en silencio. Había prometido mutar CÓDIGO Python con su baile de
`__pycache__`. Pero si una medida es un dato, mutarla es transformar el dato: no se
toca ningún archivo, no hay `.pyc` que pueda quedar viejo, y el `bytecode_frio` de
la corrida es verdadero POR CONSTRUCCIÓN, no por precaución. Además contesta una
pregunta que nada más contestaba: ¿el corpus alcanza para fijar las medidas? La
mutación de código fuente sigue pendiente, con su motivo escrito.

Cuatro mutadores: aflojar el umbral, invertir el comparador, quitar el filtro y
negarlo. 28 mutantes (medida × mutador), 64 detecciones (mutante × caso).

EL HALLAZGO: la primera corrida dejó 10 sobrevivientes, casi todos de
`quitar_filtro`. Y mi propio consejo en la salida estaba MAL — decía «se tapa
agregando evidencia al caso». Con `contar` y umbral `<= 0`, una medida sin filtro
sólo da verde si la relación está vacía: agregar filas no mata ese mutante nunca.

Lo que faltaba era otra cosa. El corpus tenía SÓLO DEFECTOS, y eso deja las
medidas flojas — es lo mismo que evaluar un clasificador sólo con positivos. Hacía
falta la otra polaridad: evidencia real donde la medida DEBE decir verde. Se
agregaron 7 casos `verde_correcto`, todos observaciones de esta misma sesión, y con
ellos los 28 mutantes mueren.

Segundo error de análisis, también mío: la unidad estaba mal. Un mutante muere si
ALGÚN caso lo detecta, no si lo detecta cada uno — `quitar_filtro` no lo puede
notar un caso rojo y sí un verde; `aflojar_umbral`, al revés. Los hechos pasaron a
ser por (medida, mutador), con la traza por caso en la relación `deteccion`.

48 tests (16 nuevos, del sensor). Ronda de mutación sobre el sensor con caché
frío: 5 mutantes, los 5 mueren — incluido «murio = v.ok», que era exactamente el
bug de la primera versión. Y otra vez el patrón que ya está en el README: DOS de
esos cinco dejan `mutar.py` en verde. El sensor no sustituye a los tests; son
oráculos complementarios y ninguno alcanza solo.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — El catálogo de geometría: dos dominios, un álgebra, 1200 veredictos coincidiendo

*commit 8a4d24b*

Paso 4, que es el que decide si esto es general o si es una cosa disfrazada de
otra. `proceso` (un agente construyendo herramientas) y `geometría` (piezas en un
nivel) no se parecen en nada, y usan LOS MISMOS OPERADORES sin un solo adaptador.

`unir` entró al llegar su disparador —«pares de piezas que se clavan» es un
producto y ninguna medida de proceso lo necesitaba—, así que van cuatro operadores
de seis. Su modo `"izquierda"` sigue sin usuario: traería el concepto de NULO, que
es la peor verruga de SQL, y no hace falta para nada de lo que existe.

Cinco escalares de dominio declaradas (`penetracion`, `es_fondo`, `volumen`,
`desvio_de_grilla`, `desvio_de_paso`) y cuatro medidas: bounds, interpenetración,
snap a grilla y yaw. El hecho `pieza` es plano como manda L0: sin AABBs anidados.

LA VERIFICACIÓN, que es lo que importa: `tools/emitir_diferencial.py` vive en JAM y
usa sus oráculos escritos a mano —una implementación independiente que no comparte
una línea con este álgebra— para generar 300 mundos con su veredicto esperado.
`tools/diferencial.py` los re-juzga acá. 1200 veredictos, CERO desacuerdos. Lo
único que viaja entre los repos es un archivo de hechos: no hay dependencia en
tiempo de ejecución.

El emisor se niega a escribir el fixture si alguna medida no tiene las dos
polaridades, con al menos 10 casos de cada lado.

Y el catálogo de geometría hizo aparecer un mutante que el diseño no contemplaba.
En el patrón «donde tol → resumen max → umbral tol», quitar el filtro NO PUEDE
cambiar el veredicto: si nada supera la tolerancia el máximo sin filtrar sigue por
debajo, y si algo la supera sigue por encima. Es un mutante equivalente, y por lo
tanto imposible de matar comparando veredictos.

Pero sí cambia LOS TESTIGOS. Y los testigos son lo que una persona lee para
actuar, así que el informe también es contrato: el sensor ahora compara veredicto
Y testigos, y distingue las dos causas en el campo `como`.

Eso obliga a corregir algo que este repo afirmaba hace dos commits: dije que los
casos verdes eran «lo único que fija el filtro». Ya no es cierto — con la
comparación de testigos NINGÚN mutador del juego actual necesita un caso verde
(`aflojar_umbral` necesita uno ROJO, y el resto se detecta por los testigos en
cualquier polaridad). Los verdes siguen valiendo por otra razón: atajan una medida
que se pone roja con entrada correcta, que es el modo de falla del caso 008. La
corrección quedó escrita en el README y en el docstring del test que la afirmaba.

Caso 012 nuevo, deuda de diseño que trajo geometría: el umbral de dominio aparece
DOS VECES en la misma medida —en el `donde` que selecciona testigos y en el
`umbral` que trae su defensa— y nada los mantiene juntos. Es el mismo defecto que
los testigos duplicados del caso 004, en el otro extremo.

53 tests. 44 mutantes, 44 muertos (el corpus y el fixture se usan los dos como
material de mutación; antes las 4 medidas de geometría quedaban sin mutar y el
informe decía «todos murieron» dejándolas afuera).

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — Mutación de CÓDIGO: 53 tests en verde convivían con 88 mutantes vivos

*commit b57b8fa*

La otra mitad del paso 3, y la que atrapó 3 de los casos del corpus. `mutacion.py`
muta medidas, que son datos; esto muta el AST de archivos `.py` reales, que es más
caro y hace falta igual: un test que no discrimina sólo se ve rompiendo el código
que dice cubrir.

LOS MUTANTES SE GENERAN, NO SE DECLARAN. Es la decisión de diseño del módulo: si el
autor elige qué romper, elige —sin querer— lo que sus tests ya atrapan, que es el
sesgo del que este repositorio intenta salir. Un recorrido del AST no tiene
opinión. Cinco operadores: comparador, booleano, negación, constante y retorno.

El caché se limpia antes de CADA corrida de tests, y el `bytecode_frio` de la
corrida ya no es una promesa sino una consecuencia. Y cada mutante se restaura en
un `finally`: es lo único que separa esta herramienta de un destructor de repos.

QUÉ ENCONTRÓ, que es el punto: 242 mutantes, 88 vivos con 53 tests en verde.

  · CUATRO DE LOS SEIS COMPARADORES del álgebra no los ejercitaba nadie. Cambiar
    `!=` por `==`, `<` por `<=`, `>` por `>=` o `>=` por `>` no rompía un test.
    Sólo `<=` y `>` se usaban, y por vías indirectas.
  · el formateo del informe tampoco: dos commits atrás argumenté que «el informe
    también es contrato» y nunca lo verifiqué.
  · y el propio módulo nuevo no tenía tests — 57 de los 88 eran suyos.

Tras escribir lo que faltaba: 211/242, 31 vivos. 81 tests.

`tools/mutar_codigo.py` QUEDA EN ROJO, a propósito y con el número a la vista. Se
podrían declarar los 31 equivalentes en masa y pintar verde; eso sería exactamente
el Goodhart que perseguimos. Bajan escribiendo tests o declarando equivalentes de a
uno, en `equivalentes.json`, CON SU RAZÓN ESCRITA — un equivalente sin razón es una
excusa, igual que un umbral sin defensa.

Caso 013 nuevo: un conteo de tests no dice nada sobre qué fija. Es el mismo
argumento del caso 001 —el verde acumulativo— con evidencia dura por primera vez.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — Paso 5: el verificador del vault, re-expresado como seis medidas

*commit bb29ef2*

Tercer dominio, y el que cierra el argumento: proceso, geometría y ahora la
DOCUMENTACIÓN de un proyecto. Tres cosas que no se parecen en nada, los mismos
operadores, ningún adaptador.

`tools/vault.py` de Jam es un verificador escrito a mano: seis reglas en ramas
`if`, con los umbrales y los criterios enterrados en el código. Acá pasan a ser
seis medidas declaradas, cada una con su defensa escrita y su punto ciego — que es
lo que el original no tenía forma de decir. Por ejemplo: `vault.area_es_la_carpeta`
NO ve si el documento está en la carpeta correcta, sólo que su `area` diga dónde
está. Eso antes no estaba dicho en ningún lado.

Jam NO depende de oracle, y menos hoy: `relevo.py` es la herramienta que abre el
relevo de mañana. El patrón es el mismo que con geometría — Jam emite HECHOS
(`tools/emitir_hechos_vault.py`), oracle los juzga, y sólo viaja un archivo de
datos.

El emisor no se cree a sí mismo: copia el vault y el verificador a un temporal,
inyecta un defecto de cada tipo, corre `vault.py` de verdad ahí, y SE NIEGA A
ESCRIBIR si la conjunción de sus medidas no coincide con el veredicto del
verificador real. 42 veredictos, cero desacuerdos.

Y encontró un hueco con su propia regla: `vault.nombre_es_ascii` quedaba con 6
verdes y 0 rojos, porque no había defecto que la activara. Una medida con una sola
polaridad no fija nada — es la lección del sensor de mutación, y el emisor de
geometría ya la comprobaba mientras el de vault no. Se agregó el defecto que
faltaba y la misma guarda.

Total: 1242 veredictos diferenciales, 68/68 mutantes de medida, 81 tests.

Lo que NO se hizo, a propósito: reemplazar `vault.py`. Sigue en uso. El reemplazo
va cuando el diferencial lleve tiempo en verde, no el mismo día que se escribió.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — El relevo, re-expresado: cuatro dominios y una medida que sirvió en dos

*commit b679981*

Cierra el paso 5. `tools/relevo.py` —la herramienta que abre y cierra los turnos—
queda re-expresada como cinco medidas, y con eso van 23 medidas en cuatro dominios:
proceso, geometría, vault y relevo. Los mismos operadores en las cuatro, sin un
solo adaptador.

LO MÁS LIMPIO DEL COMMIT: `proceso.verificacion_vigente` se escribió para un caso
del corpus —el relevo que daba verde con el árbol sucio— y juzgó los hechos del
sensor de relevo SIN UNA SOLA MODIFICACIÓN. La misma medida, dos sensores, dos
dominios. Eso es la clausura del álgebra dejando de ser una promesa del documento.

`relevo.el_relevo_tiene_dos_puntas` es la primera medida que necesita `unir` fuera
de geometría: comparar las dos puntas entre sí es un producto de la relación
`agente` consigo misma.

La parte incómoda: las reglas de `relevo.py` dependen del estado de git —que el
commit de la verificación exista, sea antecesor de HEAD, y que no se haya tocado
código vivo desde entonces—, así que el diferencial MONTA UN REPOSITORIO DE VERDAD
por escenario. Ocho escenarios: sin defecto, y siete con un defecto cada uno,
incluidos los dos sabores de «código vivo tocado» (commiteado y sin commitear) que
fueron el caso 007 del corpus.

Y no se compara contra la CLI sino contra las FUNCIONES —`revisar_testigo` y
`verde_editor_vigente`— importadas y apuntadas a otra raíz. La CLI además corre los
tests y el vault, que en un repo de mentira fallarían por el motivo equivocado. Son
las mismas funciones que gobiernan el relevo real, no una copia.

1290 veredictos diferenciales con cero desacuerdos. 88/88 mutantes de medida. 81
tests. Cada defecto inyectado activa exactamente una medida.

Lo que NO se hizo, otra vez a propósito: reemplazar los verificadores. Los dos
originales siguen en uso. El reemplazo va cuando el diferencial lleve tiempo en
verde.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — vault: cuatro medidas que el modo sombra delató

*commit c940e03*

Migrar `tools/vault.py` de Jam a modo sombra —los dos veredictos calculados y
comparados— destapó que el verificador escrito a mano comprobaba CUATRO COSAS que
ninguna medida cubría: documentos sueltos en la raíz, carpetas fuera de la lista,
nombres duplicados entre carpetas, y frontmatter incompleto.

No se podía migrar sin eso, y es justamente para lo que sirve el modo sombra: no
te deja llamar «reemplazo» a algo que verifica menos.

`vault.nombre_unico_en_el_vault` usa `unir`: comparar cada documento con todos los
demás es un producto. Va siendo el tercer usuario del operador.

27 medidas. Diferencial 1358/1358 sobre 11 escenarios. 104/104 mutantes de medida.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — El camino de autoría: que el lenguaje deje de tener dueño

*commit 7a5c0df*

Era el hueco que quedaba, y el más importante: todo el argumento anti-Goodhart de
este repositorio es que quien ve un defecto pueda escribir la regla que lo atrapa.
Hasta ahora eso exigía escribir s-expresiones en JSON a mano y adivinar qué
relaciones existen, así que el único que podía hacerlo era quien escribió el
evaluador. En la práctica, el dueño del lenguaje seguía siendo el LLM.

`tools/medida.py`:

  --relaciones   los hechos disponibles y sus campos, DERIVADOS de la evidencia que
                 hay en el corpus y los fixtures. No es una lista mantenida a mano:
                 si aparece un hecho nuevo, aparece acá solo.
  --escalares    funciones de dominio con su unidad y su docstring, más
                 comparadores, agregados, accesores y operadores.
  --nueva id     crea el archivo con la forma puesta y los huecos en mayúsculas.
  <archivo>      la revisa, y la CORRE contra toda la evidencia que existe.

Lo último es lo que importa: una medida no se estrena a ciegas. La herramienta
dice cuántas veces se pone verde, cuántas roja, y muestra dos casos donde se pone
roja. Y avisa de los dos modos de no medir nada: «nunca se pone roja» (una medida
que no puede fallar) y «nunca se pone verde» (la condición está invertida).

`ESCRIBIR-UNA-MEDIDA.md` es la guía escrita para una persona: la forma, tres
ejemplos comentados de menor a mayor —contar, medir una magnitud, comparar filas
entre sí con `unir`—, y la tabla de qué te dice la herramienta ante cada error.

Y lo que NO te puede decir, que va antes que todo lo demás: si la condición dice lo
que quisiste decir. Una medida que selecciona lo que está BIEN en vez de lo que
ofende pasa todas las comprobaciones automáticas —está bien formada, discrimina, y
mide exactamente al revés—. Se probó y es así.

Por eso la guía empieza por el orden: PRIMERO EL CASO DEL CORPUS, DESPUÉS LA
MEDIDA. Una medida escrita primero se escribe para pasar, no para atrapar.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — Macros: 22 medidas eran la misma forma, y la regla decía que a la quinta

*commit f5250ab*

El disparador que la especificación pedía —«las macros se habilitan cuando aparezca
la quinta medida con la misma forma»— había sonado hace rato: de 27 medidas, 22
eran EXACTAMENTE `de→donde → resumen contar → umbral <= 0`. Escribir la medida 28
era la misma ceremonia que la 1, y cambiar esa forma alguna vez eran 22 archivos.

  ninguno       22   ninguna fila debe cumplir el predicado
  ninguno-par    2   lo mismo sobre PARES de la misma relación
  peor           2   el peor caso de una expresión no pasa de una tolerancia
  canónica       1   colocacion.interpenetracion, que une dos relaciones distintas

Las macros expanden ANTES de construir la medida, como en LISP: de ahí para adentro
el evaluador, la mutación, el inventario y el nivel L2 siguen viendo formas
canónicas y no se enteran. No se pierde inspeccionabilidad — `--expandir` muestra
el resultado, y `a_datos()` devuelve siempre la canónica, que es lo que muta el
sensor. Y no son un embudo: si la forma no encaja, se escribe canónica.

`peor` CIERRA UNA DEUDA POR CONSTRUCCIÓN. El caso 012 del corpus anotaba que la
tolerancia aparecía dos veces —en el filtro que define los testigos y en el umbral
que trae la defensa— sin nada que las mantuviera juntas. La macro la recibe una vez
y genera las dos. Mejor que comprobar que coincidan es que no haya dos copias.

La conversión de las 26 se verificó contra una FOTO de las formas canónicas
anteriores: el script abortaba si alguna expansión no reproducía exactamente lo de
antes. Después: corpus, aceptación, diferencial (1358) y mutación de medidas
(104/104) idénticos a antes de la conversión.

Y apareció un defecto GRAVE de otra herramienta, en el peor momento posible:

Una corrida de `tools/mutar_codigo.py` se cortó por timeout, y `SIGTERM` termina el
proceso SIN ejecutar el `finally` que restaura el archivo. `nucleo/mutacion_codigo.py`
quedó en su forma mutada, con 71 líneas menos, en el árbol de trabajo. Lo salvó
`git checkout`, no la herramienta. Y había un test que decía cubrir esto
—`test_restaura_el_archivo_EXACTAMENTE`— pero sólo probaba el camino normal.

Arreglado con `atexit` más manejadores de SIGTERM/SIGINT/SIGHUP y un registro de
archivos en vuelo. El test nuevo LANZA UN SUBPROCESO Y LO MATA a mitad; se comprobó
que discrimina quitando el manejador. Queda como caso 014 del corpus, porque es
exactamente la misma clase de falso verde que el resto: probar el camino feliz y
llamarlo «se restaura siempre».

21 casos. 95 tests.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — guía: el ejemplo 2 decía que la tolerancia va dos veces, y eso ya no es cierto

*commit 48d4877*

La macro `peor` cerró esa deuda al escribirse. Un documento que describe un
problema resuelto enseña a convivir con él.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — Modo simulación: la mitad GPSS, y el concepto de juego que se había metido en el núcleo

*commit 4203e16*

§5 de la especificación deja de ser una promesa. Las cuatro familias anteriores
consultan hechos estáticos; ésta corre el sistema y mide lo que emerge. Y no
necesita álgebra nueva, que era la apuesta: una traza es una relación.

    evento(corrida, t, actor, que, …)
    corrida(id, escenario, semilla, pasos, razon, determinista)

EL ERROR QUE HABÍA QUE CORREGIR, y me lo marcó Brian a mitad de camino: la primera
versión del contrato tenía `Corrida.gano: bool`. Eso es un concepto de JUEGO metido
adentro del núcleo, y viola la doctrina del propio repositorio — el sensor no juzga.
Un simulador de una cola de trabajo no «gana»: termina porque se agotó la ventana o
porque rechazó a alguien. Si eso está mal lo dice una MEDIDA.

La misma corrección, más chica, en el simulador de cola: «quedó gente esperando al
final» era una razón de terminación y pasó a ser un hecho del resumen (`quedaron`).
Una razón que juzga es un `if` escondido en un sensor.

El determinismo se COMPRUEBA: cada corrida se ejecuta dos veces con la misma semilla
y `determinista` es un hecho más, que juzga una medida. Una corrida irreproducible
no es evidencia, es una anécdota — y el runner no acepta la palabra del simulador.

Dos simuladores de referencia, en dominios que no se parecen:

  simuladores/cola.py       el caso canónico de GPSS: entidades que llegan, esperan
                            y las atiende alguien. Una caja, una cola de tareas, un
                            pipeline. NADIE gana.
  simuladores/laberinto.py  recorrer una topología con visión local y presupuesto
                            finito, más un BFS al lado.

El laberinto está por el desacuerdo que ningún oráculo de propiedad puede ver:
«EXISTE CAMINO» Y «SE LLEGA» NO SON LO MISMO. El BFS tiene información perfecta y
memoria infinita; el que camina, ni una ni la otra. Hay un escenario en el corpus
donde el BFS dice resoluble y las tres corridas terminan por «tope»: un oráculo de
propiedad daría verde.

5 medidas: dos neutrales (reproducibilidad, presupuesto agotado) y tres de dominio.
32 medidas en seis dominios. 31 casos de corpus, 10 nuevos y TODOS de corridas
reales — incluido un simulador roto a propósito que ignora la semilla, para observar
el no-determinismo en vez de inventarlo.

Y la lección de siempre, otra vez: al emitir los casos le di UNA SOLA POLARIDAD a
cada medida nueva, y `mutar.py` dejó 2 sobrevivientes. Los dos casos espejo los
cerraron. 124/124.

111 tests. Aceptación ✓. Diferencial 1358/1358.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — Un dominio verificado se DECLARA: la herramienta que crea herramientas

*commit 0d9bd52*

Brian marcó que el repo estaba acumulando instancias en vez de abstraer, y la
medición le da la razón: la repetición se había mudado. En las medidas la cerraron
las macros; en los INSTRUMENTOS seguía entera.

    510 líneas en tres arneses escritos a mano
    y dos son la misma estructura, función por función:
    DESTINO · MEDIDAS · hechos() · espera() · DEFECTOS · montar_y_romper() · main()

`nucleo/dominio.py` lo declara:

    Dominio(nombre, montar, hechos, referencia, defectos)

`montar` arma el escenario con el defecto puesto, `hechos` es el sensor —contexto a
relaciones, sin juzgar—, y `referencia` es la implementación independiente contra la
que se contrasta. De eso se deriva el fixture entero.

LO QUE SE VA, y es lo mejor del cambio: `espera()`. Cada arnés traía una función que
decía, medida por medida, qué debería dar cada una — o sea que REIMPLEMENTABA LAS
MEDIDAS EN PYTHON. Dos definiciones de lo mismo que nadie mantiene sincronizadas: el
mismo defecto que los testigos duplicados del caso 004, treinta líneas por dominio.

Ahora el fixture guarda sólo los hechos y el veredicto de la referencia, que es la
única información independiente que hay, y la comprobación es global: las medidas
juntas dan verde exactamente cuando la referencia da verde. Reclamar granularidad
por medida era inventar información que la referencia no daba.

`generar` SE NIEGA en tres casos, y ninguno es una promesa del docstring:

  · sin defectos declarados — sin evidencia roja ninguna medida queda fijada;
  · si el sensor y la referencia no coinciden — una de las dos miente y no se sabe cuál;
  · si a alguna medida le falta una polaridad. Eso lo comprobaban dos de los tres
    arneses; el tercero no, y por eso `vault.nombre_es_ascii` estuvo sin fijar.

El fixture declara QUÉ MEDIDAS usa en vez de deducirlas del prefijo del id: el
dominio `relevo` usa `proceso.verificacion_vigente`, que es compartida.

`tools/diferencial.py` entiende los dos formatos, así que los tres arneses se migran
de a uno sin romper nada. 118 tests, todo verde.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — Oracle deja de tener dominios: la herramienta y el proyecto se separan

*commit dab72cb*

Brian: «oracle tiene que ser multipropósito, una herramienta que crea herramientas
para el LLM… limpia oracle de casos particulares». Tenía razón, y había un
impedimento concreto antes de poder limpiar nada: LAS HERRAMIENTAS TENÍAN LA RUTA
DEL CATÁLOGO CLAVADA EN SU PROPIO REPOSITORIO — once ocurrencias en cinco archivos.
Una herramienta que sólo sabe medirse a sí misma no es multipropósito.

`nucleo/proyecto.py`: un proyecto es cualquier directorio con `catalogos/`,
`corpus/` y `diferencial/`. Se resuelve por `--proyecto`, por `$ORACLE_PROYECTO`,
por el directorio actual, y en último caso por el propio oracle — para que pueda
seguir midiéndose a sí mismo.

Y el CATÁLOGO BASE viene incluido: las medidas de `proceso`, `meta` y `simulacion`
valen para cualquiera que construya con un LLM, y se cargan junto a las del
proyecto. Que vengan de fábrica es la diferencia entre una herramienta y un
repositorio de ejemplos. Un id repetido entre los dos catálogos es un error, no una
sobrescritura silenciosa.

Un proyecto declara sus propias funciones escalares en `<proyecto>/escalares.py` y
las herramientas las registran solas: sin eso, una medida de dominio fallaba con
«no es escalar declarada» lejos de la causa.

QUÉ SE FUE:

  · `cola` y `laberinto` (+ `simuladores/`) — eran utilería para probar que la
    simulación es agnóstica del dominio. Un laberinto es un caso particular de
    querer hacer un juego con laberintos.
  · `geometria`, `vault` y `relevo` — junto con sus fixtures, a `jam/medidas/`,
    que es el proyecto que los usa.

Queda `ejemplo/trabajo.py`: un trabajo que consume un presupuesto. NO es un
dominio, es un banco de pruebas — deliberadamente abstracto, porque cualquier cosa
más concreta volvería a meter un caso particular en la herramienta. Existe sólo
para que las dos medidas neutrales de simulación tengan evidencia que las fije.

Verificado en las dos direcciones: oracle sobre sí mismo, y oracle apuntado al
proyecto de Jam —1358 veredictos diferenciales y 124/124 mutantes de medida sobre
un catálogo que ya no vive acá—.

Un test se rompió y estaba mal escrito: comparaba un NÚMERO absoluto de medidas
como macro, así que mover un dominio a su proyecto rompía un test que no tenía nada
que ver. Ahora compara la proporción.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — El nivel deja de confundirse con el dominio, y ahora se verifica

*commit 883ec9f*

Brian marcó que `catalogos/meta` no era un dominio sino un NIVEL, y que ahí había
dos ejes mezclados. Tenía razón, y encima había una medida mal archivada:
`meta.verificador_sin_falsos_rojos` mide sobre `hallazgo` —que es el mundo— y no
sobre `medida`. Es del dominio proceso; vuelve ahí.

Los dos ejes ahora se DERIVAN en vez de convenirse. `como_hechos` emite:

    dominio                    del prefijo del nombre
    es_meta_por_el_nombre      el nombre empieza con `meta.`
    es_meta_por_lo_que_mide    la relación de origen ES `medida`

Y que sean dos campos distintos es lo que permite comprobar que coincidan, en vez
de confiar en que alguien guardó el archivo en la carpeta correcta. Eso es la medida
nueva, `meta.el_nivel_no_se_confunde_con_el_dominio`, que es L2 legítima: mide sobre
`medida`.

Probada por la vía real: se archivó a propósito una medida del mundo con nombre
`meta.` y la aceptación se puso roja señalándola.

La convención pasó de estar escrita en un README a negarse sola.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-29 — mutar: entender el formato de dominio declarado

*commit aa0ec8a*

El fixture nuevo no trae expectativa por medida —eso reimplementaba las medidas en
Python— así que `mutar.py` se rompía al leerlo, y las medidas de un dominio migrado
habrían quedado sin fijar EN SILENCIO si el traceback no fuera ruidoso.

Con el formato nuevo la línea base es el veredicto ACTUAL de cada medida, y para
mutar es lo correcto: la pregunta no es «¿acierta?» sino «¿algún escenario nota que
la cambiaron?».

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-30 — El marco deja de juzgarse con `if`s: las reglas sobre sí mismo son medidas

*commit 10f9381*

El norte de oracle es el universo de problemas de crear una herramienta, y una
parte de ese universo es la herramienta misma. Pero el veredicto sobre el marco
estaba en código imperativo dentro de `tools/` —el mismo pecado que un sensor que
juzga, un nivel más arriba— mientras el resto del proyecto exige que los veredictos
sean datos.

`nucleo/marco.py` es el sensor del propio marco:

    caso(id, medida, tiene_medida, medida_existe, esperado_ok, dio_ok, explica_el_hueco)
    medida_en_uso(id, casos_que_la_evaluan, mutantes, mutantes_vivos)

Y cinco medidas nuevas en el nivel meta, dos de las cuales eran huecos declarados
que las herramientas calculaban y nadie enunciaba:

    meta.el_caso_se_pone_como_debe            era un `if` en aceptacion.py
    meta.el_caso_reclama_una_medida_que_existe
    meta.el_hueco_declarado_explica_por_que
    meta.toda_medida_esta_ejercitada          NADIE lo miraba
    meta.toda_medida_esta_fijada              lo calculaba mutar.py sin enunciarlo

`mutar.py` ya no decide con `if vivos: return 1`: el código de salida sale del
veredicto de las medidas.

TRES COSAS QUE APARECIERON AL CORRERLO, y las tres son el argumento del repo:

1. La regla del eje se me quedó corta. Decía «es meta si mide sobre `medida`», y
   alcanzaba para las dos medidas que había. Las nuevas miden sobre CASOS, que
   también son del lenguaje y no del mundo. Ahora hay un conjunto declarado
   —`medida`, `caso`, `medida_en_uso`— y la línea que sí se sostiene es: el
   catálogo y lo que lo fija son del lenguaje; mutantes, hallazgos y afirmaciones
   son del TRABAJO de construir, que es el dominio `proceso`.

2. `meta.el_caso_reclama_una_medida_que_existe` salió en FALSO ROJO en su primera
   corrida: señalaba los tres huecos declarados del corpus, que legítimamente no
   reclaman ninguna medida. Confundí «reclama una que no existe» con «no reclama
   ninguna». Un verificador que reporta roto lo que está bien es peor que ninguno
   —es el caso 008— y esta vez lo cometí yo.

3. `meta.toda_medida_esta_ejercitada` encontró un agujero REAL que yo mismo hice
   hace dos commits: al sacar los dominios particulares borré `corpus/simulacion/`
   y las dos medidas de simulación quedaron sin un solo caso que las evalúe. Nadie
   lo había notado. Repuestas con cuatro casos de corridas del ejemplo ABSTRACTO,
   con sus dos polaridades.

Y una decisión de diseño que vale anotar: un caso sin medida no tiene veredicto que
comparar, y la tentación era poner nulos. Eso choca con que el álgebra levante error
al comparar contra un ausente. Se resolvió sin nulos —cada pregunta a la medida que
le corresponde— y es otro síntoma del hueco de la AUSENCIA, que sigue esperando a
`agrupar`.

25 casos. 104 tests. Aceptación ✓ con el marco midiéndose a sí mismo.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-30 — meta: una medida heredada no la ejercita el proyecto que la hereda

*commit 39caf55*

`meta.toda_medida_esta_ejercitada` daba FALSO ROJO al apuntar la herramienta a otro
proyecto: señalaba las ocho medidas universales del catálogo base por no tener
casos, cuando el corpus que las fija vive en oracle y no en el proyecto.

Sólo se ve corriendo la herramienta en el contexto para el que existe. Un proyecto
responde por SUS medidas; de las heredadas responde oracle.

Es el tercer falso rojo del día, y los tres los cometí yo escribiendo la medida.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-30 — `agrupar`, y con él la AUSENCIA — sin traer nulos

*commit 45d6169*

Quinto operador de seis, y entró cuando sonó su disparador dos veces:
`proceso.modulo_con_consumidor` declaraba en su propio `alcance` no poder distinguir
un importador real de un test, y `nucleo/marco.py` tuvo que esquivar nulos por el
mismo motivo.

LA AUSENCIA ERA UNA PREGUNTA ABIERTA DE LA ESPECIFICACIÓN y se resolvió sin
`LEFT JOIN`. Un left join habría traído el concepto de NULO, que es la peor verruga
de SQL y que choca de frente con una decisión del álgebra: comparar contra un valor
ausente levanta error, porque un False silencioso convierte un campo mal escrito en
un verde.

El truco no necesitó nada nuevo: agrupar sobre el producto SIN filtrar y agregar con
`suma` sobre un predicado. Los booleanos suman 0 y 1, así que un grupo donde nada
casó da cero y sigue existiendo.

    ["unir", ["de","modulo","m"], ["de","importa","i"]],
    ["agrupar", [["modulo", ["campo","m","nombre"]]],
                [["reales","suma", ["y", …, ["==", ["campo","i","es_test"], false]]]]],
    ["donde", ["==", ["col","reales"], 0]]

Un grupo NO es un hecho: es un resumen. Las filas que salen no llevan alias —los
hechos se consumieron— sino columnas derivadas, que se leen con `["col", nombre]`.
Ese accesor existía desde el primer día y recién ahora encontró su usuario.

`proceso.modulo_con_consumidor` deja de declarar su ceguera y la cierra: distingue
un importador real de un test. El caso 009 del corpus la pidió durante dos días.

El caso verde (106) traía sólo hechos de `modulo` y ninguno de `importa`, así que su
verde era TRIVIAL: sin pares no hay grupos que contar. Ahora trae el grafo de
imports real del núcleo.

Queda un límite y va declarado en el alcance de la medida: si la relación del lado
derecho está vacía, no hay pares y no hay grupos. Sin resolver.

107 tests. Verificado por mutación: romper el agregado del grupo mata dos tests.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-30 — Orden y recursión: las dos resueltas, y ninguna agregó un operador

*commit 4854119*

Quedaban cuatro preguntas abiertas en la especificación. Con la ausencia del commit
anterior van tres cerradas, y las dos de hoy se cerraron SIN ampliar el álgebra —que
era el riesgo, porque un lenguaje que crece con cada caso deja de ser un lenguaje.

ORDEN: es un campo del hecho, no una propiedad de la relación. No puede ser lo
segundo, porque L0 dice que una relación es un CONJUNTO y los conjuntos no tienen
orden. Entonces «consecutivos» es aritmética sobre el campo ordinal, y alcanzó con
declarar dos escalares universales: `mas` y `menos`.

La medida que lo estrena —`simulacion.la_traza_no_tiene_huecos`— agrupa por corrida
y compara la cuenta de eventos contra el último instante. Para fijarla hay un
simulador roto a propósito que no registra un paso: se OBSERVA el hueco en vez de
inventar la evidencia.

RECURSIÓN: queda FUERA del álgebra. Un operador `cierre` habría sido meter recursión
en un lenguaje que se mantiene chico a propósito, y con un solo usuario — justo lo
que la regla prohíbe. La salida es más fiel a la doctrina: la alcanzabilidad es un
HECHO, y producir hechos es trabajo del sensor.

    alcanzable(desde, hasta, saltos)

`nucleo/grafo.py` pone el BFS para que ningún sensor lo reimplemente, que era el otro
riesgo. El álgebra la mide como cualquier relación, sin saber nada de grafos.

`proceso.modulo_alcanzable` es la medida nueva, y muestra por qué hacía falta: «tener
importadores» y «ser alcanzable» son cosas distintas. Un racimo de módulos que se
importan entre sí puede estar muerto, y `modulo_con_consumidor` lo daría por bueno.

DOS COSAS QUE APARECIERON AL CORRERLO:

1. Un bug real del sensor: `from . import escalares` no trae `module` —el nombre está
   en `names`— así que ese import quedaba invisible y `catalogos.escalares` salía «no
   alcanzable». Un falso rojo que sólo se ve mirando el resultado.

2. Los `__init__.py` vacíos salían marcados como muertos. Son marcadores de paquete,
   y eso es un HECHO, no un juicio: el sensor emite `es_paquete_vacio` y la medida
   decide. El sensor no excluye nada por su cuenta.

29 casos. 107 tests. De las cuatro preguntas abiertas queda una: la igualdad de
flotantes, que probablemente cambie la forma de `umbral`.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-30 — La igualdad de flotantes: resuelta negándose. Las cuatro preguntas, cerradas

*commit 8f9c207*

Era la última de las cuatro preguntas abiertas de la especificación, y la respuesta
no fue cambiar la forma de `umbral` como suponía el documento: fue PROHIBIR la
igualdad exacta sobre flotantes.

`0.1 + 0.2` no es `0.3`. Una medida que compare así diría verde sin que nadie se
entere, que es la peor falla posible acá. La igualdad exacta sólo tiene sentido sobre
cosas que se CUENTAN o se NOMBRAN —enteros, booleanos, textos— y ahí sigue
permitida. Sobre cosas que se MIDEN hace falta una tolerancia, y declararla es
justamente lo que el lenguaje pide para todo umbral:

    ["<=", ["cerca", a, b], tolerancia]

La escalar `cerca` es la salida declarada, y las comparaciones de ORDEN sobre
flotantes siguen permitidas: una tolerancia ES una comparación de orden.

No rompió nada: ninguna medida del catálogo comparaba un flotante con `==`, así que
la guarda entra sin migración. Verificado por mutación: quitarla mata dos tests.

Con esto las CUATRO preguntas abiertas quedan cerradas, y sólo UNA amplió el
álgebra:

    ausencia      → trajo `agrupar`
    orden         → es un campo del hecho, no una propiedad de la relación
    recursión     → salió del álgebra: `alcanzable` es un HECHO del sensor
    flotantes     → prohibida la igualdad exacta

Que tres de cuatro se cierren sin agregar operadores es la única prueba de que el
juego chico alcanzaba. Un lenguaje que crece con cada pregunta deja de ser un
lenguaje.

111 tests. Aceptación ✓.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-30 — dominio: la repetición va como segundo argumento de `montar`

*commit 5278ebf*

Antes se le mangleaba el nombre del defecto para pasar dos cosas por un parámetro.
Un dominio con azar usa `i` de semilla; uno determinista lo ignora.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-30 — Introspección: la esencia, la naturaleza, y el paquete para estudiarlo

*commit 2bddacb*

El README mostraba la ARQUITECTURA y no la NATURALEZA. Lo que quedó debajo de todos
los mecanismos, después de construirlo, es una sola frase:

    Ninguna afirmación vale por sí sola. Tampoco la que dice «esto está verificado».

Cada pieza resulta ser una respuesta a «¿por qué debería creerte?» sobre una clase
distinta de afirmación: «está bien» pide medida, umbral y punto ciego; «el test lo
cubre» pide un mutante que lo mate; «corrió verde» pide un commit y que nada haya
cambiado desde entonces; «esta medida sirve» pide un caso que la ponga roja Y uno que
la ponga verde; «el marco funciona» pide una medida que lo diga.

Y su naturaleza, medida y no supuesta: NO ES UN INSTRUMENTO DE MEDICIÓN, ES UNO DE
RECHAZO. En 1593 líneas de núcleo hay siete tipos de error declarados y 39 negativas
—16 en los 123 renglones del álgebra—. No calcula calidad: declina dejar pasar lo que
no se puede sostener.

Cuatro cosas más que los números dijeron y el README no:

  · lo que produce no es confianza sino confianza ACOTADA. El veredicto no es el
    producto: el punto ciego lo es.
  · la asimetría: 14 falsos verdes contra 1 falso rojo en el corpus. Ésa es la
    justificación empírica de «negarse antes que permitir». Pero un falso rojo enseña
    a ignorar el verificador, y en un solo día lo cometí tres veces.
  · el sujeto es el que construye, no lo construido: 20 de 29 casos son sobre el
    propio trabajo, y ninguno de los 16 defectos lo atrapó un verificador propio en el
    momento (8 la mutación, 5 una persona, 4 la casualidad, 1 una herramienta ajena).
  · la historia lo dice mejor que el código: de 23 commits, cerca de la mitad tienen
    por título la corrección de algo que yo mismo había afirmado.

`tools/estudio.py` vuelca todo a Markdown plano y autocontenido para subirlo a
NotebookLM: 10 documentos, sin enlaces relativos ni referencias a archivos que el
lector no tenga. Lo que no es copiar y pegar, y es la razón de que sea un generador:
el catálogo y el corpus son JSON y crudos se leen mal (salen como prosa y tablas, con
cada medida en sus dos formas); los mensajes de commit tienen buena parte del «por
qué»; y los docstrings del núcleo tienen el razonamiento, no el código.

Y al generarlo apareció que la proporción del README estaba MAL CONTADA: dije «treinta
a uno» de memoria cuando el catálogo tenía la mitad de las medidas de hoy. Son diez a
uno con el catálogo base y cinco a uno contando un proyecto real. Ahora los números
los mide el generador y el README lo dice, para que no vuelva a divergir — es la
segunda vez que afirmo esa proporción de memoria y la segunda que está mal.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-07-30 — Auditoría y refuerzo de las garantías de Oracle

*commit c60d4a3*



### 2026-07-30 — Cierra P0 del arnés de mutación

*commit 5861ed3*



### 2026-07-30 — Cierra P1: semántica, fixtures y proyectos externos

*commit 4b6ccdd*



### 2026-07-30 — Cierra P2.1 y P2.2 e inicia saneamiento P2.3

*commit 2057505*



### 2026-07-30 — Inicia baseline vigente de mutación de código

*commit 85e37c8*



### 2026-07-30 — Cierra mutacion del adaptador de proyecto

*commit 4b29f6b*



### 2026-07-30 — Cierra mutacion del modelo de medida

*commit 56a72b4*



### 2026-07-30 — Cierra mutacion de fixtures y medidas

*commit eefb6c2*



### 2026-07-30 — Cierra mutacion del algebra

*commit f0b06e1*



### 2026-07-30 — Cierra P2.3 y empaqueta Oracle

*commit 44c44ae*



### 2026-07-31 — Cierra autonomia de embedding P3

*commit 47989fc*



### 2026-07-31 — Fija el valor numerico en la mutacion

*commit ceab294*



### 2026-07-31 — Hace opt-in todas las politicas de Oracle

*commit e096a37*

---

<!-- fuente: 08-los-numeros.md -->

## Los números, y qué dicen

| Qué | Cuánto | Qué dice |
|---|---|---|
| líneas del núcleo | 2654 | el lenguaje |
| líneas de medidas escritas en él | 164 | lo escrito en el lenguaje |
| proporción | 16 a 1 | la apuesta: que el segundo crezca y el primero no |
| (contando sólo el catálogo base) | 19 a 1 | sin ningún proyecto que lo use |
| negativas en el núcleo (`raise`) | 150 | su naturaleza es rechazar, no medir |
| medidas | 18 | de las cuales 6 miden el lenguaje mismo |
| casos de corpus | 42 | fallas reales, con su evidencia |
| commits | 37 | cerca de la mitad corrigen una afirmación propia |

Si en seis meses la proporción no se movió, el lenguaje no valió la pena. Es la única
métrica del proyecto que no se puede sastrear escribiendo más medidas.

---

<!-- fuente: 09-decision-relaciones-como-bolsas.md -->

## Decisión 001 — las relaciones son bolsas

**Estado:** aceptada el 2026-07-30.

### Contexto

La especificación 0.2 llamaba “conjunto” a una relación, pero la representación y el evaluador
conservaban cada aparición de un hecho. No existía una identidad universal con la que deduplicar:
algunos dominios tienen `id`, otros usan claves compuestas y dos observaciones iguales pueden ser dos
eventos reales distintos. Deduplicar por el contenido completo también habría borrado multiplicidad
sin que el sensor lo pidiera.

### Decisión

Una relación de L0 es una **bolsa nombrada de hechos homogéneos**:

- la multiplicidad es parte de la evidencia;
- el orden de almacenamiento no es parte de la semántica;
- `de`, `donde`, `unir`, `agrupar`, los agregados y los testigos conservan la multiplicidad que les
  corresponde;
- si un dominio necesita unicidad, su sensor debe producirla o una medida debe comprobarla mediante
  una clave declarada; Oracle no inventa la identidad del hecho.

### Consecuencias

Dos hechos idénticos cuentan dos veces. Un producto multiplica multiplicidades y los agregados operan
sobre todas las apariciones. Esto coincide con el comportamiento anterior, que ahora queda fijado por
regresiones en vez de ser un accidente de usar listas.

La alternativa de conjunto se rechaza porque exigiría un contrato de identidad nuevo, específico de
cada relación. Si en el futuro hace falta deduplicar dentro del álgebra, deberá entrar como operador
explícito con su clave y con dos usuarios reales; no como normalización silenciosa.

---

<!-- fuente: 10-auditoria-tecnica.md -->

## Auditoría técnica de Oracle — 2026-07-30

### Dictamen de cierre

El motor de Oracle quedó **desacoplado del consumidor que le dio origen y verificablemente
genérico dentro de su contrato**. El núcleo consume relaciones de hechos, descubre perfiles físicos
sin registrar nombres conocidos y selecciona juezas por esquemas declarados, no por ids particulares.
El corpus conserva procedencia histórica como datos de regresión; no concede autoridad ni altera la
ejecución.

| Pregunta | Dictamen vigente |
|---|---|
| ¿Está completo? | Sí para el motor y su autocertificación: 319 tests, 129/129 mutantes de medida y 1073/1073 de código. La licencia y la adopción por un consumidor real independiente no son propiedades que el código pueda decidir. |
| ¿Está abstraído de su origen? | Sí en ejecución: no hay imports, rutas, perfiles ni juezas de aquel consumidor en el núcleo. Las referencias que quedan son evidencia histórica del corpus y esta auditoría. |
| ¿Funciona de forma genérica? | El flujo externo sintético demuestra catálogo, corpus, diferencial, UDF, mutación y estudio sin modificar Oracle. Falta evidencia social más fuerte: un consumidor real no codiseñado. |
| ¿Hay Goodhart hardcodeado? | No se encontraron verdes fijados, invariantes vacías, ids jueces privilegiados ni equivalentes masivos. Las políticas operativas restantes son constantes públicas con contratos mutacionales. |
| ¿Hay una puerta trasera? | No se encontró una puerta trasera. `escalares.py` ejecuta código externo sólo con `--confiar-escalares`, confinado físicamente y con restauración del registro. |

### Dictamen original conservado como línea base

Oracle es un **prototipo sólido, pero todavía no un oráculo confiable ni genérico de punta a
punta**. El álgebra está razonablemente separada de Jam; el catálogo, las herramientas y la evidencia
conservan supuestos de ese origen y existen caminos concretos para obtener un verde vacío,
autodeclarado o vencido.

| Pregunta | Dictamen |
|---|---|
| ¿Está completo? | No. Hay contratos incompletos, 31 mutantes de código vivos declarados y caminos principales rotos. |
| ¿Está abstraído de Jam? | El álgebra, bastante. El producto completo y su validación, todavía no. |
| ¿Funciona de forma genérica? | El núcleo puede reutilizarse sobre hechos planos, pero sólo fue probado dentro del ecosistema Jam/Python/LLM. |
| ¿Hay Goodhart hardcodeado? | Sí: hay afirmaciones de confianza fijadas a `True`, invariantes vacías y mutaciones dependientes de una escala elegida a mano. |
| ¿Hay una puerta trasera? | No se encontró evidencia de una puerta trasera maliciosa. Sí hay ejecución automática de código de proyectos y riesgos de integridad. |

Esta auditoría no invalida lo que Oracle ya consiguió. Distingue tres cosas que el informe anterior
mezclaba: que el código corra, que el diseño sea reusable y que un verde sea evidencia suficiente.

### Seguimiento posterior a la auditoría

Los hallazgos describen el commit auditado y se conservan como línea base. El worktree posterior
completó P0:

| Hallazgo | Estado posterior |
|---|---|
| A-01, campos certificados de simulación | Corregido en el worktree: colisiones rechazadas y 18 tests directos nuevos. |
| A-02, mutación sin línea base | Corregido en el worktree: una baseline roja levanta `LineaBaseFallida` antes de tocar fuentes. |
| A-03, confianza hardcodeada | Corregido para P0: caché comprobado antes y después, estados estructurados, timeout configurable, diagnóstico y equivalentes validados. Se eliminaron los veredictos de confianza autoproducidos y el estado de bytecode que no aplicaba a la mutación en memoria. La mutación automática sobre una copia en vez de fuentes activas sigue en P2. |
| A-04, verdes vacuos | Corregido en el worktree: ausencia, cero medidas/casos/mutantes y fixtures incompletos fallan de forma explícita. |

Después de P0 la suite tenía 190 tests verdes. Oracle conservaba 19 defectos en rojo, 12
verdes correctos, 3 huecos declarados y 48/48 mutantes de medida muertos; contra Jam conservaba 269
comparaciones diferenciales sin desacuerdo y 80/80 mutantes de medida muertos. La aceptación de Jam,
que no tiene corpus propio, ahora termina como `NO APLICABLE — SIN CASOS` con código distinto de cero.
El generador de estudio funciona sobre Oracle, pero `tools/estudio.py --proyecto .../jam/medidas`
todavía falla al validar `volumen` porque no registra las escalares del proyecto; resolverlo sin
ocultar la ejecución de UDF externas permanece en P1.

P1.1 reemplazó aquella cifra de mutación de medidas: el denominador ahora localiza sitios en fuentes,
expresiones, agregados y campos, además de los cuatro cambios gruesos originales. Sobre Oracle son
128 mutantes: la primera ronda mató 118 y expuso 10 vivos explícitos. Ocho reducciones al borde del
umbral y dos contraejemplos internos los cerraron sin debilitar el denominador; la ronda actual queda
en 128/128. El corpus tiene ahora 42 casos y aceptación conserva 27 defectos en rojo, 12 verdes
correctos y 3 huecos declarados. Contra Jam son 157 mutantes, 146 muertos y 11 vivos, mientras el
diferencial conserva 269 veredictos sin desacuerdo. La suite subió a 202 tests.

P1.2 cerró la frescura del diferencial con el esquema `oracle.diferencial/v1`: los fixtures llevan
SHA-256 del emisor, fuentes de referencia, catálogo canónico y configuración. El lector recalcula las
cuatro huellas y rechaza el fixture vencido. El acuerdo global con la referencia y los veredictos
individuales históricos son datos y salidas distintas; una regresión demuestra que intercambiar dos
medidas ya no se oculta detrás del mismo `AND`. Los emisores de Jam usan semilla SHA-256, Git con
fechas fijas y JSON canónico; dos regeneraciones consecutivas dieron archivos idénticos byte a byte.
Jam verifica 269 acuerdos globales y 1158 veredictos individuales; la suite de Oracle tiene 206 tests.

P1.3 cerró A-07 y el contrato operativo de proyectos. Un lector común valida y normaliza fixtures
`grupos` y `escenarios`; `--relaciones`, revisión y mutación consumen ese lector y la mutación exige
también frescura. Los ids de autoría usan una gramática cerrada y el destino se comprueba físicamente
debajo de `catalogos/`, incluida una regresión contra symlinks exteriores. Cada herramienta valida
las carpetas que usa. `estudio.py` usa el corpus externo y sólo ejecuta sus escalares con
`--confiar-escalares`. Una integración temporal recorre los siete comandos externos; la suite tiene
ahora 212 tests. Contra Jam, inventario y revisión funcionan, el diferencial conserva 269/1158 y la
mutación informa honestamente 146/157 con 11 vivos. La primera ejecución del vendor todavía dio el
verde obsoleto 80/80; sincronizar núcleo, herramientas y catálogo base eliminó esa divergencia.

P1.4 cerró la ejecución automática descrita en A-06. Todas las cargas externas ocurren dentro de
`main` y requieren `--confiar-escalares`; ayuda e inventarios tienen pruebas de ausencia de efectos
laterales. El registro queda aislado por proyecto y se restaura incluso ante error. El decorador fija
nombre, unidad, aridad y procedencia verificables, y no se siguen symlinks para encontrar el archivo.
La suite subió a 217 tests; la integración externa usa una UDF real para demostrar tanto el rechazo
sin confianza como el flujo explícitamente autorizado.

P2.1 cerró el riesgo operativo del mutador descrito en los riesgos medios. La API pública ya no
escribe objetivos activos: copia la raíz, mapea comando y fuentes, y verifica al final que los bytes
originales sigan iguales. Hay lock no bloqueante por raíz, reemplazo atómico dentro de la copia,
timeout y salida acotada por proceso, grupos de proceso terminados ante timeout/SIGTERM y handlers
instalados sólo durante la ronda. Un manifiesto con huellas de fuentes, motor y configuración permite
reanudar mutantes terminados y rechaza cambios o corrupción. Ocho regresiones nuevas elevan la suite
a 225 tests, incluida la terminación forzada de un nieto que ignora SIGTERM.

P2.2 cerró los acoplamientos particulares enumerados en los riesgos medios. El análisis AST, el
mutador de código Python y las medidas sobre imports/`.pyc` se movieron a `perfiles/python`, que sólo
se incorpora mediante `oracle.json`. El catálogo universal ya no contiene la razón `tope` ni la regla
normativa que exigía el token español `NO `. `ContratoTerminacion` clasifica razones aportadas por el
dominio; `ClasificacionMeta` acepta relaciones y prefijos adicionales; `LimitesAlgebra` impone techos
configurables y finitos a entradas, productos y profundidad. La suite alcanza 234 tests y la mutación
de medidas queda en 129/129.

Una revisión posterior encontró dos restos estructurales que la primera afirmación no había visto: el
número de perfiles estaba registrado en `nucleo.proyecto` y los CLI de mutación elegían medidas juezas
por ids concretos. Ahora los perfiles físicos se descubren por convención y se activan sólo desde
`oracle.json`; las juezas se derivan de sus relaciones declaradas. Además, los sensores de mutación de
medidas y de código publican nombres de relación distintos porque sus esquemas de corrida no coinciden.
Una regresión AST impide que `nucleo/` importe perfiles.

La mutación de código se repitió de forma particionada sobre copias temporales frescas, nunca sobre
este worktree. Los cambios descubiertos durante las rondas obligaron a repetir íntegramente cada
partición afectada. El baseline final cubre 616 sitios: 503 muertos reales y 113 vivos, sin timeout ni
error de arnés. Cada copia terminó con los 11 archivos de `nucleo/*.py` idénticos byte a byte a su
snapshot inicial y sin `__pycache__` local. Ninguno de estos cambios está incluido en el hash auditado
de la sección siguiente.

P2.3 invalidó este baseline histórico en vez de comparar números incompatibles. Tras mover el mutador
y los sensores Python a un perfil, y retirar redundancias de `proyecto`, `algebra` y la política del
runner, el alcance vigente es de 1073 sitios. Se añadió partición explícita por objetivo y prioridad
de tests seguida siempre por la suite completa. Doce particiones del núcleo y perfil cubren 868/868
sin equivalencias;
los sobrevivientes se cerraron con casos discriminantes. `proyecto` pasó de 43 muertos, 35 vivos y
2 errores de arnés en la exploración inicial a 79/79 concluyentes. Sus pruebas nuevas fijan selección,
configuración, confinamiento y el opt-in de código Python externo; también se eliminó el truncado fijo
de la huella del módulo. `medida` pasó de 76 muertos, 14 vivos y 7 errores de importación a 98/98;
la excepción de declaración ahora existe antes de construir la clasificación base y una prioridad
sin imports tempranos distingue fallos de inicialización sin confundirlos con el arnés. `fixtures`
pasó de 104/129 a 128/128: ocho pruebas nuevas fijan tipos anidados, bordes, consistencia y proyección,
y un default inobservable se retiró en vez de declararlo equivalente. `mutacion` pasó de 119/151 a
147/147; los IDs estructurales ahora prueban que cada ruta apunta al único escalar modificado, y se
cubrieron explícitamente `no` y `contar` agrupado. Cuatro sitios redundantes se retiraron. `algebra`
pasó de 208 muertos, 24 vivos y 9 errores de importación a 237/237: una prioridad sin import temprano
atribuye las roturas de inicialización al código, y diez contratos fijan límites, escalares, ausencia,
aridad, agregados y bordes. Cuatro sitios redundantes se retiraron. Además, el
manifiesto ahora firma las dependencias de la ronda: antes un cambio en los tests podía reutilizar
resultados viejos porque sólo se firmaban comando, objetivos y motor. La partición final del motor
Python cerró sus 205 sitios: 205/205 muertos, sin equivalencias, timeout ni error de arnés. El total
vigente es 1073/1073 y la suite actual tiene 319 pruebas. El paquete se construyó e instaló desde
`pyproject.toml`; declara Python >=3.11 y siete entry points. CI reproduce la suite, aceptación,
diferencial, mutación de medidas y las trece particiones de código.

**Baseline histórico 503/616, conservado sólo como evidencia de la auditoría inicial:**

| Archivo | Muertos | Total | Vivos |
|---|---:|---:|---:|
| `algebra.py` | 183 | 186 | 3 |
| `dominio.py` | 11 | 18 | 7 |
| `grafo.py` | 0 | 4 | 4 |
| `macro.py` | 18 | 21 | 3 |
| `marco.py` | 24 | 43 | 19 |
| `medida.py` | 69 | 80 | 11 |
| `mutacion.py` | 47 | 50 | 3 |
| `mutacion_codigo.py` | 94 | 140 | 46 |
| `proyecto.py` | 18 | 34 | 16 |
| `simulacion.py` | 39 | 40 | 1 |
| **Total** | **503** | **616** | **113** |

Al repetir la ronda durante P0 apareció un riesgo nuevo en la propia instrumentación: mutar el
predicado que enumera `__pycache__` hizo que la limpieza interpretara casi todas las rutas como caché
y borrara una copia temporal completa. El worktree real no estuvo expuesto. El punto de borrado ahora
revalida, de forma independiente, el nombre exacto y el confinamiento físico de cada ruta; dos
regresiones demuestran que ni un enumerador corrompido ni una ruta exterior reciben autoridad de
borrado. El incidente quedó registrado como caso `018` y refuerza que el aislamiento definitivo de
P2 no es una mejora cosmética.

La misma repetición encontró un segundo caso operativo: mutar el comparador que reconoce
`--proyecto` podía quitar también `--hechos` y `--timeout`, lanzar recursivamente otra ronda completa
y agotar el límite de 60 segundos. El estado nuevo lo clasificó como inconcluso, no como muerte. Una
regresión directa fija el parser y el runner se detiene en la primera discriminación; al repetir los
34 sitios de `proyecto.py`, ese mutante terminó como `tests_fallaron` y no quedó ningún timeout ni
error de arnés.

Una revisión cruzada posterior reprodujo otros cuatro bypasses antes del cierre: un objetivo symlink
podía llevar la escritura fuera de la raíz; un error de importación creado como `_FailedTest` salía
con el mismo código que una discriminación; un timeout de un equivalente desaparecía del cálculo de
la CLI; y una ronda con cero mutantes devolvía éxito. Los cuatro tienen regresiones y fallan cerrado.
También se prohibieron códigos de señal como supuestos fallos de tests y se validan formato,
unicidad y razones de `equivalentes.json` antes de convertirlo en mapa. El caso vacuo quedó registrado
como `019`.

### Estado auditado y alcance

- Repositorio: `/home/workstation/Dev/oracle`.
- Commit auditado: `2bddacb4731aacc08c71d052528893fd16a1fab4` (`main`).
- Proyecto de contraste: `/home/workstation/Dev/jam/medidas`.
- Copia vendorizada de Jam: split `5278ebf2f70906e8fe05b94668461ddfde3a2d3d`.
- El núcleo y las herramientas compartidas entre upstream y vendor eran iguales; Jam estaba un commit
  documental por detrás.
- Se revisaron código, catálogo, corpus, tests, historia Git, emisores diferenciales de Jam y la
  integración real `--proyecto`.
- No se volvió a ejecutar la ronda completa de `tools/mutar_codigo.py`: escribe temporalmente sobre
  fuentes reales. El número 31/242 se tomó del estado declarado por Oracle y por el relevo actual de
  Jam; el código que produce esa medición sí fue auditado.
- Jam tenía modificaciones locales ajenas a `vendor/oracle/` y `medidas/`. Las comprobaciones de la
  auditoría no editaron fuentes de Oracle ni archivos de Jam; este documento y el plan son los únicos
  cambios derivados de la revisión.

### Verificaciones ejecutadas

| Verificación | Resultado observado |
|---|---|
| `python -m unittest discover -s tests -t . -v` | 112 tests, todos verdes |
| `python tools/corpus.py --resumen` | 29 casos; esquema aceptado |
| `python tools/aceptacion.py` | 15 defectos rojos, 11 verdes correctos, 3 huecos declarados |
| `python tools/mutar.py` | 44/44 mutantes de medida muertos |
| `python tools/diferencial.py` en Oracle | falla: Oracle no contiene fixtures diferenciales |
| diferencial contra `jam/medidas` | 269 comparaciones globales, 0 desacuerdos |
| mutación de medidas contra `jam/medidas` | 80/80 mutantes muertos |
| aceptación contra `jam/medidas` | verde vacuo: 0 casos, 0 rojos, 0 verdes |
| `tools/medida.py --relaciones --proyecto .../jam/medidas` | falla con `KeyError: 'grupos'` |

Los resultados verdes prueban que los caminos ejercitados funcionan con el material actual. No
cierran los hallazgos siguientes.

### Hallazgos críticos

#### A-01 — Un simulador puede falsificar los hechos certificados por Oracle

**Severidad:** crítica para la integridad del modo simulación.

`nucleo/simulacion.py` calcula `id`, `escenario`, `semilla`, `pasos`, `razon` y `determinista`, pero
después expande `**a.resumen`. El resumen controlado por el simulador puede sobrescribir todos esos
campos. Del mismo modo, un evento puede sobrescribir el campo `corrida` que le asigna el runner.

Se reprodujo con dos ejecuciones diferentes. El simulador devolvió
`resumen={"determinista": True, "id": "falso"}` y un evento con `corrida="inyectada"`; la evidencia
final afirmó exactamente esos valores. Esto permite eludir las medidas de reproducibilidad,
presupuesto y continuidad de traza.

**Evidencia:** `nucleo/simulacion.py`, construcción de `corridas` y `eventos`, líneas 104–110. No hay
tests directos del módulo en la suite actual.

#### A-02 — La mutación de código puede dar verde si la suite original ya está roja

**Severidad:** crítica para la afirmación de que los tests fijan el código.

El mutador no ejecuta una línea base sobre el código original. Para cada mutante interpreta cualquier
código de salida distinto de cero como “mutante muerto”. Un `ImportError`, un fallo ambiental o una
suite que falla siempre puede matar todos los mutantes y producir el mensaje “Todos los mutantes
murieron”.

El comportamiento está fijado por el test
`test_si_los_tests_siempre_fallan_TODOS_mueren`; por lo tanto, no es sólo una posibilidad teórica.

**Evidencia:** `perfiles/python/mutacion_codigo.py`, líneas 216–242;
`tests/test_mutacion_codigo.py`, líneas 132–136; `tools/mutar_codigo.py`, líneas 60–80.

#### A-03 — `bytecode_frio` y `resultado_confiable` están hardcodeados

**Severidad:** crítica como caso directo de Goodhart autorreferencial.

`limpiar_cache` usa `shutil.rmtree(..., ignore_errors=True)`, incrementa el contador aunque el borrado
falle y no comprueba que el caché haya desaparecido. Aun así, la evidencia emite incondicionalmente:

```python
"bytecode_frio": True,
"resultado_confiable": True,
```

Se reprodujo con un `__pycache__` enlazado: la función reportó un borrado y el directorio seguía
existiendo. La medida `proceso.arnes_con_bytecode_frio` confía en el booleano producido por el mismo
sensor; `resultado_confiable` no es juzgado por ninguna medida.

**Evidencia:** `perfiles/python/mutacion_codigo.py`, líneas 207–213 y 263–268.

#### A-04 — La ausencia y el cero tienden a convertirse en verde

**Severidad:** alta, transversal al álgebra y las herramientas.

Una fuente usa `evidencia.get(relacion, [])`. Una relación ausente o mal escrita es indistinguible de
una relación presente sin filas. Con la forma predominante `contar <= 0`, el resultado es verde.

También se comprobaron estas invariantes vacías:

- `evaluar([], {})` produce un informe verde por `all([])`;
- una tubería `['desde']` carga y termina con cero filas;
- una medida con cero mutantes aplicables satisface `meta.toda_medida_esta_fijada`, porque sólo se
  comprueba que haya cero mutantes vivos;
- la aceptación de Jam devuelve éxito con cero casos;
- un fixture diferencial existente con cero medidas y cero escenarios no es rechazado por esquema o
  cardinalidad.

**Evidencia:** `nucleo/algebra.py`, líneas 146–147; `nucleo/medida.py`, líneas 164–176;
`catalogos/meta/meta.toda_medida_esta_fijada.json`; `tools/aceptacion.py`, líneas 38–105;
`tools/diferencial.py`, líneas 43–66.

### Hallazgos altos

#### A-05 — El diferencial es replay de una foto, no verificación independiente actual

Los fixtures guardan `referencia_ok`, pero no la fecha, el commit o hash de la referencia, el hash del
emisor ni el hash del catálogo. `tools/diferencial.py` relee el JSON; no ejecuta ni comprueba la
implementación de referencia actual. Un verificador manual puede cambiar y el fixture viejo seguir
verde.

En el formato `Dominio`, la comparación además es global: compara el `AND` de todas las medidas contra
un booleano. Dos medidas intercambiadas, una medida demasiado amplia o dos errores que se compensan
pueden mantener el acuerdo global. El cierre de Jam tampoco gatea diferencial y mutación de Oracle.

El emisor geométrico de Jam usa `hash((defecto, i))` como semilla. El hash de strings está salado por
proceso, por lo que regenerar el mismo fixture puede producir mundos distintos sin cambios de código.

**Evidencia:** `nucleo/dominio.py`, líneas 106–131; `tools/diferencial.py`, líneas 43–66;
`/home/workstation/Dev/jam/tools/emitir_diferencial.py`, línea 61.

#### A-06 — Apuntar a un proyecto ejecuta código de ese proyecto

`registrar_escalares` importa y ejecuta automáticamente `<proyecto>/escalares.py` mediante
`exec_module`. El proyecto también puede elegirse implícitamente por el directorio actual si contiene
`catalogos/`. Cinco herramientas hacen la carga antes de entrar a su `main`, incluso para operaciones
que sólo pretenden inspeccionar o mostrar ayuda.

Es una extensión UDF intencional, no una puerta trasera. Sin embargo, equivale a ejecución de código
arbitrario con los privilegios del usuario y la frontera de confianza no está advertida ni es opt-in.
El `escalares.py` actual de Jam sólo registra funciones matemáticas; no se encontró un payload.

**Evidencia:** `nucleo/proyecto.py`, líneas 73–86 y 93–115; carga temprana en `aceptacion.py`,
`diferencial.py`, `medida.py`, `mutar.py` y `mutar_codigo.py`.

#### A-07 — El camino de autoría no funciona contra el primer proyecto real

`tools/medida.py` sólo entiende fixtures antiguos con la clave `grupos`; los tres fixtures actuales de
Jam usan `escenarios`. Por eso el comando recomendado `--relaciones` falla con `KeyError`.

`--nueva` tiene otro problema: sólo exige que el id contenga un punto y usa el id crudo para construir
una ruta. Un id absoluto o con `../` puede crear un JSON fuera de `catalogos`. Para un proyecto externo,
el intento posterior de mostrar la ruta relativa a Oracle también puede fallar después de escribir.

**Evidencia:** `tools/medida.py`, líneas 52–63 y 102–115.

#### A-08 — Hay bypasses y contradicciones en la semántica del álgebra

- La especificación define una relación como conjunto; la implementación conserva duplicados. La
  semántica real es de bolsas y afecta conteos, sumas, promedios, productos y testigos.
- La igualdad exacta de flotantes se prohíbe dentro de expresiones, pero el umbral final usa `_cmp`
  directamente. Una medida puede declarar `umbral == 0.3` y obtener un falso rojo silencioso por
  redondeo.
- `aflojar_umbral` usa `GRANDE = 1e12`. Para un límite `<= 1e15`, la supuesta relajación cambia el
  umbral a `<= 1e12` y lo vuelve más estricto, matando artificialmente el mutante.
- La validación de una medida al cargarla es superficial: estructura, aridades y tipos se descubren al
  evaluar, a veces sólo si existe una fila que alcance la expresión.

**Evidencia:** `ESPECIFICACION.md`, sección 1; `nucleo/algebra.py`, líneas 146–147;
`nucleo/medida.py`, líneas 95–129; `nucleo/mutacion.py`, líneas 30–46.

### Riesgos medios y operativos

- Los equivalentes de mutación se excluyen por presencia del id aunque su razón sea una cadena vacía.
  No existe actualmente `equivalentes.json`, por lo que no hay exclusiones ocultas activas.
- El mutador escribe sobre fuentes reales sin bloqueo ni escritura atómica. Dos instancias concurrentes,
  `SIGKILL`, OOM o pérdida de energía pueden dejar código mutado. Instala manejadores globales de señal
  al importar el módulo y no aplica timeout ni límite de salida al subproceso de tests.
- `unir` materializa el producto cartesiano completo. No hay límites de tamaño, profundidad de
  expresiones o tiempo de simulación impuesto por Oracle; el `tope` sólo se pasa al simulador.
- Las relaciones de nivel meta están fijadas en código a `medida`, `caso` y `medida_en_uso`.
- El catálogo llamado universal contiene convenciones de CPython (`.pyc`), análisis de imports Python,
  la palabra española `tope` y la heurística textual `NO ` para reconocer un alcance.
- `como_hechos` deriva el dominio del prefijo del id y sólo observa la primera fuente de una unión.

### Completitud y generalidad

#### Lo que sí quedó abstraído

- `nucleo/` no importa Jam, Unreal ni BotOO.
- Los dominios geometría, vault y relevo viven en `jam/medidas`.
- Proyecto, catálogo y escalares pueden resolverse mediante `--proyecto`, `ORACLE_PROYECTO` o el
  directorio actual.
- La misma representación evaluó hechos de geometría, documentos y repositorios Git.
- El proyecto no tiene dependencias de terceros y los 112 tests actuales pasan.

#### Lo que todavía impide llamarlo genérico

- Jam es el único consumidor real y todos los dominios de prueba nacieron en el mismo proyecto, con el
  mismo autor y durante la misma sesión.
- Oracle nació como generalización conceptual del `Medida`/`Umbral`/`Veredicto` creado primero dentro
  de Jam. De los 29 casos del corpus, 18 declaran origen Jam y 11 Oracle.
- Jam conserva dos caminos declarativos: `jam.medida`/`jam.catalogo` y Oracle JSON. Sus tests dinámicos
  de geometría prueban el camino legado, no el núcleo Oracle.
- Los verificadores manuales de vault y relevo siguen siendo los productivos; quedan otros oráculos de
  Jam por reexpresar.
- `con` y el modo izquierdo de `unir` siguen sin implementar.
- El repositorio no declara versión mínima de Python, paquete instalable, CI, licencia ni release.
- Cola y laberinto se usaron durante el desarrollo, pero ya no permanecen como pruebas de regresión.
- No existe todavía un segundo proyecto independiente que pruebe el flujo completo de autoría,
  diferencial, corpus, mutación y entrega.

### Deriva documental observada

- El README habla en distintos lugares de 19 y 29 casos, 53, 81 y 112 tests, y resultados de
  diferenciales ya movidos a Jam.
- El docstring del álgebra todavía dice tres operadores aunque hay cinco implementados.
- `tools/medida.py --escalares` afirma que `agrupar` no tiene usuario.
- Dos de los tres “huecos sin tapar” (`004` y `012`) se describen en sus propios casos como resueltos
  por construcción; el informe sigue contándolos como huecos abiertos.
- Jam manda ejecutar `vendor/oracle/tools/estudio.py`, pero su subtree está un commit atrás y no contiene
  ese archivo.

### Revisión de puerta trasera

No se encontró evidencia de una puerta trasera activa en el árbol o el historial inspeccionado:

- no hay red, telemetría, descarga o persistencia;
- no hay `shell=True`, `eval`, pickle, marshal o YAML inseguro;
- no hay hooks Git activos, submódulos o symlinks versionados;
- no se encontraron claves, tokens o contraseñas;
- los subprocess se invocan con listas, no mediante un shell;
- no hay dependencias externas ni ejecutables privilegiados;
- el núcleo vendorizado en Jam coincide con upstream: no aparece una modificación oculta durante la
  extracción.

La ausencia de una backdoor detectable no vuelve segura la ejecución sobre proyectos no confiables:
`escalares.py` sigue siendo código Python ejecutado deliberadamente.

### Conclusión

Oracle ya demuestra una idea reusable: representar medidas como datos, exigir defensa y alcance, y
producir testigos con un álgebra común. Todavía no demuestra que sus propios verdes sean siempre
fail-closed. Antes de ampliar el lenguaje o reemplazar verificadores de Jam hay que corregir la cadena
de confianza: integridad del sensor, línea base de mutación, invariantes no vacías, frescura del
diferencial y frontera de ejecución de proyectos.

El orden de trabajo y sus criterios de salida están en [`PLAN-CORRECCION.md`](PLAN-CORRECCION.md).

---

<!-- fuente: 11-plan-de-correccion.md -->

## Plan de corrección de Oracle

Este plan parte de [`AUDITORIA-2026-07-30.md`](AUDITORIA-2026-07-30.md). Ordena el trabajo por cadena
de confianza: primero impedir verdes falsos; después estabilizar formatos y semántica; recién entonces
ampliar el lenguaje, migrar Jam o preparar una release.

### Reglas para ejecutar el plan

1. **Cada bypass entra primero como regresión roja.** El test o caso debe discriminar contra la versión
   actual antes de implementar el arreglo.
2. **Un fallo del arnés no es un mutante muerto.** Error ambiental, timeout y fallo de tests son estados
   distintos y se informan por separado.
3. **Cero evidencia no significa verde.** Se representa como error de contrato o estado “sin material”,
   nunca como éxito.
4. **No se declaran equivalentes en masa.** Cada equivalente lleva una razón no vacía y revisable.
5. **No se agregan operadores durante P0 y P1.** Primero se vuelve confiable lo que ya existe.
6. **Cada fase termina con Oracle y Jam verificados.** Los fixtures de Jam se regeneran sólo cuando el
   formato y la frescura estén definidos.

### P0 — hacer que “verde” sea confiable

#### P0.1 Proteger los hechos reservados de simulación

- [x] Agregar tests que reproduzcan la sobrescritura de `determinista`, `id`, `semilla`, `pasos`,
  `razon`, `escenario` y `corrida`.
- [x] Declarar conjuntos explícitos de campos reservados para `corrida` y `evento`.
- [x] Rechazar colisiones desde `Corrida.resumen` y desde cada evento; no resolverlas sólo cambiando el
  orden de `**`, porque eso escondería un simulador mal contratado.
- [x] Validar `pasos` como entero no negativo, `razon` como texto, ids de corrida únicos y campos L0
  escalares.
- [x] Añadir tests directos para `simulacion.py`, incluida una corrida no determinista real.

**Criterio de salida:** ningún dato controlado por el simulador puede sobrescribir un campo certificado
por el runner; los bypasses de la auditoría levantan `SimuladorMalContratado`.

#### P0.2 Exigir una línea base verde antes de mutar código

- [x] Ejecutar los tests una vez sobre las fuentes originales antes de generar mutantes.
- [x] Abortar con un error específico si la línea base está roja; no producir hechos `murio`.
- [x] Cambiar el test que hoy canoniza “si los tests siempre fallan, todos mueren”.
- [x] Separar en la evidencia `baseline_verde`, `tests_fallaron`, `error_arnes` y `timeout`.
- [x] Tratar fallos de importación/descubrimiento como error del arnés y detener la suite en la
  primera discriminación antes de que un camino posterior la convierta en timeout.
- [x] Derivar `resultado_confiable` de comprobaciones reales o eliminar el campo.
- [x] Incorporar timeout por mutante y conservar la salida del primer fallo para diagnóstico.

**Criterio de salida:** una suite originalmente roja nunca puede producir “todos los mutantes
murieron” ni un código de salida exitoso.

#### P0.3 Comprobar de verdad el caché y los equivalentes

- [x] Hacer que `limpiar_cache` falle si no puede borrar un caché o si éste sigue presente.
- [x] Emitir `bytecode_frio=True` sólo después de verificar el estado, no por construcción declarada.
- [x] Probar fallos de borrado y symlinks sin seguir ni borrar su destino.
- [x] Probar y definir qué ocurre si un caché reaparece durante la misma corrida.
- [x] Revalidar cada ruta en el punto de borrado para que un enumerador mutado no pueda borrar el
  proyecto ni una ruta exterior.
- [x] Confinar físicamente cada fuente antes de leerla o escribirla y rechazar objetivos symlink.
- [x] Rechazar equivalentes con razón vacía, id inexistente o id vencido.
- [x] Validar formato y unicidad de `equivalentes.json`; un incidente de un equivalente también
  invalida la ronda completa.
- [x] Hacer que una declaración equivalente inválida ponga la ronda en rojo.

**Criterio de salida:** no queda ningún booleano de confianza fijado incondicionalmente y una razón
vacía no puede sacar un mutante del denominador.

#### P0.4 Eliminar los verdes vacuos

- [x] Hacer que una relación ausente sea `ErrorDeAlgebra`; una relación presente y vacía debe poder
  representarse explícitamente.
- [x] Adaptar el verificador L0: una lista vacía es una relación válida; una clave ausente sigue siendo
  ausencia.
- [x] Validar al cargar una medida: tubería no vacía, primera fuente, operadores, aridades, resumen,
  umbral y tipos básicos.
- [x] Impedir que un catálogo o informe con cero medidas sea verde.
- [x] Impedir que aceptación con cero casos diga `ACEPTACIÓN ✓`; usar un estado no aplicable o error.
- [x] Impedir que una ronda de código con cero mutantes —incluidos todos equivalentes— salga verde.
- [x] Cambiar `meta.toda_medida_esta_fijada` para exigir `mutantes > 0` y
  `mutantes_vivos == 0`, con una política explícita para medidas heredadas.
- [x] Rechazar hechos mutantes sin `apunta_a` vigente o sin un `murio` booleano, para que una fila
  incompleta no cuente silenciosamente como mutante muerto.
- [x] Rechazar fixtures diferenciales sin medidas, sin escenarios, sin ambas polaridades o con
  `mundos` incoherente.

**Criterio de salida:** cero medidas, cero casos, cero mutantes y una relación mal escrita producen un
rechazo explícito, nunca verde.

#### Puerta P0

P0 termina sólo cuando:

- todos los bypasses A-01 a A-04 tienen regresiones que discriminan;
- la suite completa pasa;
- aceptación y mutación de medidas siguen funcionando sobre Oracle;
- una copia temporal ejecuta la mutación de código sin tocar el worktree real;
- el informe ya no contiene afirmaciones de confianza autoproducidas.

**Estado 2026-07-30:** puerta cumplida. La suite pasa, Oracle y Jam conservan sus verificaciones y el
baseline particionado cubrió 616 sitios en copias temporales restauradas byte a byte, sin rondas
inconclusas en el agregado final.

### P1 — estabilizar semántica, diferencial e integración externa

#### P1.1 Formalizar el contrato del álgebra

- [x] Decidir mediante una nota de diseño si una relación es conjunto o bolsa.
- [x] Si es bolsa, corregir especificación y explicar duplicados; si es conjunto, definir identidad y
  deduplicación determinista.
- [x] Prohibir `==` y `!=` exactos sobre flotantes también en el umbral final.
- [x] Validar números finitos y tipos compatibles en agregados y umbrales.
- [x] Sustituir `GRANDE = 1e12` por una mutación independiente de escala y agregar casos por encima y
  por debajo de ese orden de magnitud.
- [x] Ampliar la mutación de medidas a fuentes, expresiones, agregados y campos; documentar claramente
  el denominador cubierto.

**Criterio de salida:** duplicados y flotantes tienen una semántica única, probada y documentada;
“aflojar” nunca vuelve un umbral más estricto.

**Estado 2026-07-30:** P1.1 implementado. La especificación 0.3 fija relaciones como bolsas, el
umbral final comparte el contrato seguro de comparación, agregados y umbrales rechazan no finitos y
tipos incompatibles, y `aflojar_umbral` avanza una unidad o un flotante representable sin centinela de
escala. El denominador localizado pasó de 48 a 128 mutantes. Su primera ronda mató 118 y dejó diez
huecos; ocho reducciones de borde y dos casos internos los cerraron sin reducir el denominador, por
lo que Oracle queda en 128/128. Contra Jam, el mismo denominador produce 157 mutantes, 146 muertos y
11 vivos; la regeneración fresca de P1.2 confirmó que pertenecen a la cobertura de sus escenarios y
no a fixtures vencidos. Se mantienen explícitos para el siguiente bloque de integración.

#### P1.2 Versionar y dar frescura al diferencial

- [x] Definir una versión de esquema para fixtures.
- [x] Guardar huellas SHA-256 del emisor, fuentes de referencia, catálogo y configuración usada.
- [x] Rechazar o marcar como vencido un fixture cuya huella no coincide.
- [x] Distinguir en datos y salida “acuerdo global del conjunto” de “veredicto individual”.
- [x] Añadir una regresión donde dos medidas intercambiadas mantengan el `AND` global, para que el
  límite quede visible o sea corregido.
- [x] Reemplazar `hash()` por una semilla estable derivada con SHA-256 en Jam.
- [x] Hacer reproducible byte a byte la regeneración de fixtures.

**Criterio de salida:** cambiar una referencia o un emisor vence el fixture; regenerar dos veces sin
cambios produce el mismo archivo; el informe no llama veredictos individuales a comparaciones globales.

**Estado 2026-07-30:** P1.2 implementado. `oracle.diferencial/v1` firma emisor, referencia, catálogo
canónico y configuración; una diferencia vence el fixture antes de evaluarlo. Cada escenario separa
el acuerdo global independiente de la fotografía de veredictos individuales, incluida una regresión
de permutación compensada. Los tres fixtures de Jam se regeneraron dos veces con SHA-256 idénticos;
el cierre reporta 269 acuerdos globales y 1158 veredictos individuales estables. Los 11 mutantes de
medida vivos de Jam permanecen explícitos y no se confundieron con frescura.

#### P1.3 Reparar el camino de autoría y el contrato de proyecto

- [x] Extraer un lector común de fixtures que entienda formatos versionados `grupos` y `escenarios`.
- [x] Hacer funcionar `--relaciones`, revisión de una medida, diferencial y mutación contra
  `jam/medidas`.
- [x] Validar ids con una gramática cerrada y confinar toda ruta creada debajo de `catalogos/` después
  de resolverla.
- [x] Corregir la presentación de rutas para proyectos externos.
- [x] Hacer que `tools/estudio.py --proyecto` resuelva escalares externas mediante una confirmación
  explícita de confianza.
- [x] Validar estructura de proyecto según la herramienta: catálogo, corpus y/o diferencial requerido,
  en vez de aceptar siempre sólo `catalogos/`.
- [x] Crear un fixture de integración temporal que pruebe el flujo externo completo en tests.

**Criterio de salida:** todos los comandos documentados funcionan sobre Jam y sobre un proyecto mínimo
creado en un directorio temporal; ningún id puede escribir fuera del proyecto.

**Estado 2026-07-30:** P1.3 implementado. `nucleo/fixtures.py` es el único lector de ambos formatos y
también aplica frescura cuando lo consumen autoría o mutación. Jam completa inventario, revisión,
diferencial y mutación sin caminos especiales; un proyecto temporal recorre además corpus,
aceptación y estudio. Los ids siguen una gramática cerrada, el destino se confina físicamente y un
symlink exterior tiene regresión. Estudio carga UDF externas sólo con `--confiar-escalares`; P1.4
llevó luego ese opt-in y la carga dentro de `main` al resto de las herramientas. Al sincronizar el vendor
apareció la deriva que aún reportaba 80/80 con el mutador antiguo; actualizado, Jam vuelve a mostrar
el denominador real de 157, con 146 muertos y 11 vivos.

#### P1.4 Hacer explícita la frontera de confianza de las escalares

- [x] Mover la carga de `escalares.py` dentro de `main`, después de parsear argumentos; `--help` nunca
  debe ejecutar código del proyecto.
- [x] Exigir una confirmación o bandera explícita para cargar Python de un proyecto externo no marcado
  como confiable.
- [x] Documentar que una UDF tiene los mismos permisos que Oracle.
- [x] Aislar el registro por proyecto y declarar nombre, aridad y unidad verificables.
- [x] Evaluar un modo aislado para inspección que no ejecute UDF.

**Criterio de salida:** abrir ayuda o inventariar archivos no ejecuta código externo; toda ejecución de
UDF es explícita y está documentada como frontera de confianza.

**Estado 2026-07-30:** P1.4 implementado. Seis ayudas y los inventarios `--relaciones` y
`--escalares` tienen regresiones que demuestran ausencia de ejecución externa. Las operaciones que
cargan o evalúan un catálogo externo exigen `--confiar-escalares`; el registro se activa en un
contexto y se restaura siempre. Nombre, unidad, aridad y procedencia se validan al declarar, y un
`escalares.py` symlink o una inserción que evita `@escalar` falla cerrado. La integración temporal
usa una UDF real y sólo concede confianza en los cinco comandos que la necesitan.

#### Puerta P1

P1 termina sólo cuando:

- Oracle se verifica a sí mismo sin verdes vacíos;
- los tres fixtures de Jam son reproducibles y frescos;
- `--relaciones`, aceptación, diferencial y mutación funcionan sobre Jam;
- la suite contiene integración real de un proyecto externo temporal;
- upstream y `vendor/oracle` están sincronizados.

**Estado de la puerta P1:** cumplida. Oracle pasa 217 tests, aceptación y 128/128 mutantes de medida;
los fixtures reproducibles de Jam conservan 269 acuerdos globales y 1158 veredictos individuales.
El vendor ejecuta el mismo denominador y expone, sin pintarlos de verde, sus 11 mutantes vivos.

### P2 — robustez operativa y generalidad demostrada

#### P2.1 Aislar la mutación de código

- [x] Mutar una copia o worktree temporal, no las fuentes activas.
- [x] Añadir bloqueo de ejecución, restauración atómica y limpieza verificable.
- [x] Acotar tiempo y salida de cada subproceso.
- [x] Instalar manejadores de señal sólo durante una ronda, sin reemplazar los del proceso al importar.
- [x] Reanudar una ronda interrumpida con un manifiesto verificable.

**Criterio de salida:** SIGTERM, timeout, dos invocaciones concurrentes y un fallo de escritura no
alteran el worktree original ni dejan procesos huérfanos.

**Estado 2026-07-30:** P2.1 implementado. `correr()` valida los objetivos originales, copia el
proyecto y sólo entrega rutas de la copia al bucle mutante. Las escrituras internas usan
`os.replace`; un bloqueo estable por raíz rechaza una segunda ronda. Cada subproceso abre una sesión,
tiene timeout y captura drenada con límite; SIGTERM termina el grupo y los handlers se restauran al
salir. Un manifiesto atómico firma fuentes, motor y configuración, guarda cada mutante terminado y
reanuda sólo si todo sigue coincidiendo. Regresiones reales cubren SIGTERM sin hijo huérfano, lock
doble, escritura fallida, limpieza temporal, salida excesiva, nietos resistentes y
reanudación/corrupción. Suite: 225.

#### P2.2 Separar lo universal de los perfiles particulares

- [x] Mover CPython, `.pyc` y análisis AST de imports a un perfil Python optativo.
- [x] Reemplazar la razón literal `tope` por un contrato configurable de terminación.
- [x] Convertir la heurística `NO ` en una señal no normativa o en estructura declarada.
- [x] Volver extensible la clasificación de relaciones meta.
- [x] Añadir límites configurables para productos cartesianos, tamaño de entrada y profundidad.

**Criterio de salida:** el catálogo base no presupone Python, español ni el flujo de Jam; los perfiles
particulares se cargan explícitamente.

**Estado 2026-07-30:** P2.2 implementado. El AST de imports, las medidas de módulos/CPython y el
mutador de `.py` viven en `perfiles/python`; `oracle.json` es el único mecanismo que añade ese perfil
al catálogo universal. La terminación se clasifica mediante `ContratoTerminacion`, no mediante una
razón literal. Se retiró la medida que convertía el token español `NO ` en requisito normativo y
`ClasificacionMeta` permite ampliar relaciones/prefijos sin mutar globales. `LimitesAlgebra` acota por
evaluación filas de entrada, productos y profundidad, con techos finitos por defecto. Oracle pasa
234 tests, aceptación y 129/129 mutantes de medida.

**Refuerzo 2026-07-30:** el núcleo ya no enumera perfiles conocidos: descubre cualquier
`perfiles/<nombre>/catalogos` físico y sólo `oracle.json` lo activa. Las herramientas seleccionan
medidas juezas por las relaciones declaradas que pueden consumir, no por ids `proceso.*` incorporados
al código. `nucleo/` tiene una regresión que prohíbe imports hacia perfiles y quedó sin ejemplos de
dominios Jam en sus módulos.

#### P2.3 Cerrar deuda, empaquetar y probar independencia

- [x] Reemplazar el baseline vencido 503/616 y triar el denominador actual: test discriminante o
  equivalencia individual con razón revisada.
- [x] Reclasificar los casos `004` y `012` como resueltos sin contarlos como huecos abiertos; definir el
  estado honesto de `011`.
- [x] Implementar `con` y unión izquierda sólo si existen al menos dos usuarios reales; de lo contrario,
  retirarlos de la especificación activa.
- [x] Añadir `pyproject.toml`, versión mínima de Python, entry points y CI.
- [ ] Elegir y declarar la licencia (decisión legal del autor, no inferible del repositorio).
- [x] Generar y comprobar las cifras del README durante CI en vez de mantenerlas a mano.
- [x] Confirmar que Oracle no importa ni resuelve caminos legados de un consumidor; el corpus conserva
  procedencia histórica sólo como datos.
- [x] Validar el flujo completo con un proyecto externo sintético, catálogo y UDF propios.
- [ ] Obtener evidencia de un consumidor real que no haya sido diseñado junto con Oracle.

**Criterio de salida:** cero mutantes vivos no equivalentes, documentación generada y coherente, CI
reproduce las verificaciones y un consumidor independiente completa autoría, diferencial y mutación.

**Estado parcial 2026-07-30:** los casos `004` y `012` ya son memoria resuelta y `011` declara una
frontera humana; el corpus informa cero huecos abiertos. Al no existir dos usuarios reales, `con` y
la unión izquierda se retiraron de la especificación y del parser activos, con regresiones de rechazo.
Suite: 319. El alcance actual tiene 1073 sitios; `grafo`, `macro`, `marco`, `dominio`, `simulacion` y
el sensor Python de módulos suman 137/137, `diferencial` aporta 42/42, `proyecto` 79/79 y `medida`
98/98, `fixtures` 128/128, `mutacion` 147/147 y `algebra` 237/237: 868/868 ejecutados sin
equivalencias. La partición de proyecto añadió contratos de selección, configuración, confinamiento
y opt-in de código externo;
también retiró nueve constantes redundantes, incluido el truncado fijo de la huella del módulo. La de
medida fijó validación de la clasificación meta, inmutabilidad de sus cuatro datos públicos, salida
Unicode y derivación de relaciones; además movió su excepción antes del primer uso. La de fixtures
fijó cada nivel del esquema, consistencia de fotos y proyección a mutación, y retiró un default
inobservable. La del mutador de medidas fijó IDs/rutas estructurales, negación y conteo agrupado, y
retiró cuatro sitios redundantes. La de álgebra fijó límites, firmas escalares, ausencia, aridad,
agregados mixtos y bordes inclusivos; retiró cuatro sitios redundantes y convirtió nueve roturas de
inicialización en fallos atribuibles al código. La generalización posterior descubre perfiles sin
registro central, deriva juezas desde sus relaciones y separa los esquemas de corrida de los dos
sensores de mutación. Los 205 sitios vigentes de `perfiles/python/mutacion_codigo.py` cerraron
205/205 sin equivalencias, timeout ni error de arnés: el total queda en 1073/1073. El manifiesto firma
ahora también las fuentes de tests y soporte; cambiar la suite invalida la reanudación. El paquete se
construye desde `pyproject.toml`, declara Python >=3.11 y siete entry points; CI reproduce contratos,
comprueba las cifras derivables y ejecuta las trece particiones mutacionales. Siguen pendientes la
licencia y la evidencia —necesariamente externa— de un consumidor real independiente.

### Primer bloque de trabajo recomendado

El primer bloque debe ser pequeño y dejar una mejora verificable sin migrar formatos todavía:

1. ~~Añadir regresiones para colisiones de simulación y baseline rojo de mutación.~~ Hecho.
2. ~~Corregir ambos contratos.~~ Hecho.
3. ~~Eliminar `bytecode_frio=True` y `resultado_confiable=True` incondicionales.~~ Hecho.
4. ~~Añadir regresiones para cero medidas, cero mutantes y relación ausente.~~ Hecho.
5. ~~Corregir las invariantes vacías y actualizar las medidas meta.~~ Hecho.
6. ~~Ejecutar suite, corpus, aceptación y mutación de medidas.~~ Hecho.
7. ~~Ejecutar mutación de código en una copia temporal y registrar el nuevo baseline.~~ Hecho:
   503/616 muertos y 113 vivos; cero timeout/error de arnés en el agregado final y copias restauradas
   byte a byte.

No se debe empezar por `con`, por migrar verificadores de Jam ni por reducir en masa los mutantes vivos:
primero hay que asegurar que el instrumento que cuenta esos mutantes no pueda declarar confianza por
construcción.

### Bloque de cierre P0

P0 quedó cerrado sin saltar todavía a P1:

1. ~~Modelar por separado `tests_fallaron`, `error_arnes` y `timeout`, conservando salida
   diagnóstica.~~ Hecho.
2. ~~Imponer un timeout por mutante y demostrar que no se confunde con una muerte válida.~~ Hecho.
3. ~~Probar la reaparición de caché durante una ronda.~~ Hecho: una reaparición invalida la ronda
   antes de que la limpieza pueda ocultarla.
4. ~~Repetir la mutación completa en copia temporal y cerrar el baseline posterior a las regresiones
   dirigidas.~~ Hecho: 503/616, con 113 vivos explícitos y ninguna ejecución inconclusa.

El siguiente bloque recomendado es P1.1: formalizar semántica de bolsas/conjuntos, flotantes y
mutación independiente de escala antes de ampliar operadores o migrar formatos de Jam.

### P3 — autonomía de embedding

P2 cerró la independencia semántica: el núcleo ya no conoce Jam, Unreal ni nombres de perfiles o
juezas particulares. P3 separa otra pregunta que el flujo externo desde el checkout no contestaba:
si Oracle puede entrar como biblioteca en un proceso ajeno sin que el consumidor importe internals,
modifique `sys.path` o comparta estado mutable con otro proyecto.

#### Hallazgos que abren P3

- El wheel se construye sin dependencias y sus entry points pueden leer un proyecto externo desde un
  entorno aislado.
- El paquete instala nombres de primer nivel demasiado genéricos (`nucleo`, `catalogos`, `perfiles`,
  `tools`) y no publica una fachada estable: `nucleo/__init__.py` está vacío.
- Un consumidor embebido debe coordinar por su cuenta `Proyecto`, catálogos, escalares, límites,
  selección de medidas y evaluación.
- `ESCALARES` sigue siendo un registro global. El contexto de proyecto lo restaura al salir, pero dos
  motores concurrentes no poseen estado independiente.
- Las herramientas resuelven `PROY` desde `sys.argv` al importar, lo que mezcla biblioteca y CLI.
- El wheel incluye catálogos y perfiles, pero no el corpus de autocertificación: instalado sin
  `--proyecto`, `oracle-aceptacion` falla porque falta `corpus/`. Ese comportamiento debe ser una
  decisión, no un accidente de empaquetado.
- El catálogo base se inyecta siempre. Es una política útil, pero un proyecto debe poder declararla u
  omitirla explícitamente para evitar colisiones de relaciones.

#### P3.1 Fijar una fachada pública antes de migrar consumidores

- [x] Publicar `oracle_metalenguaje.Motor` como único punto de entrada recomendado para embedding.
- [x] Construir un motor desde una ruta de proyecto sin que el consumidor conozca módulos internos.
- [x] Evaluar evidencia seleccionando medidas por relaciones y devolver el `Informe` vigente.
- [x] Permitir límites por motor y confianza explícita de escalares externas.
- [x] Mantener compatibilidad temporal con los imports internos mientras se fija el contrato.
- [x] Probar la fachada desde un wheel instalado y un directorio de trabajo vacío.

**Criterio de salida:** un consumidor sólo importa `Motor`, entrega hechos y recibe un informe; no
inserta rutas ni importa `nucleo.*`, `catalogos.*`, `perfiles.*` o `tools.*`.

#### P3.2 Aislar estado y composición

- [x] Introducir `RegistroEscalares` por instancia y hacer que validación y evaluación reciban ese
  registro explícitamente.
- [x] Demostrar dos motores con UDF homónimas y distintas en el mismo proceso, sin contaminación.
- [x] Volver explícita la inclusión de las políticas base; un proyecto v1 neutral no las recibe si
  omite `catalogo_base`.
- [x] Permitir fuentes de perfiles adicionales sin modificar la instalación de Oracle.
- [x] Eliminar la resolución de `sys.argv` durante el import de herramientas; `main(argv)` construye
  su sesión después de parsear.

**Criterio de salida:** dos proyectos pueden cargarse y evaluarse intercalados o en paralelo sin que
catálogos, perfiles, UDF, límites o argumentos de uno alteren al otro.

#### P3.3 Namespace y recursos instalables

- [x] Mover la implementación bajo `oracle_metalenguaje/` o proporcionar una transición verificable
  que elimine los paquetes públicos genéricos.
- [x] Resolver recursos empaquetados con una raíz de paquete, no con la raíz amplia de
  `site-packages`.
- [x] Decidir si el corpus/diferencial de autocertificación se distribuyen o si los comandos instalados
  siempre exigen `--proyecto`; documentar y probar una sola semántica.
- [x] Probar wheel, entry points, recursos, proyecto sintético y dos motores desde fuera del checkout.

**Criterio de salida:** instalar Oracle no agrega paquetes genéricos al entorno, todos los recursos se
resuelven dentro de su distribución y ningún comando depende accidentalmente del checkout fuente.

#### Puerta P3

P3 termina sólo cuando:

- Jam puede integrar `Motor` sin conocer la disposición interna de Oracle;
- dos motores con proyectos y UDF diferentes coexisten sin estado compartido;
- el wheel se prueba desde un entorno limpio y fuera del checkout;
- la política de catálogos y perfiles es explícita;
- la suite, aceptación, diferencial y mutación conservan sus resultados;
- no se amplía el lenguaje ni se migra todavía ningún oráculo particular de Jam.

**Estado 2026-07-31:** P3 implementado del lado de Oracle. `oracle_metalenguaje.Motor` construye desde datos, medidas o
una ruta explícita; selecciona por relaciones, conserva límites por instancia y falla cerrado si no
hay juezas aplicables. `RegistroEscalares` viaja por validación y ejecución; dos proyectos con una UDF
homónima se construyen y evalúan concurrentemente sin tocar el registro global. La carga externa
sigue siendo opt-in y una escritura directa al global se rechaza. `oracle.json` acepta
`catalogo_base`; si falta, vale `false`, de modo que la configuración mínima no hereda políticas de
Oracle. Un smoke test construye el
wheel, lo inspecciona, lo instala en un venv limpio y usa sólo la fachada desde un cwd vacío. El wheel
publica exclusivamente `oracle_metalenguaje.*`; el puente `_compat` mantiene el checkout transitorio
sin instalar `nucleo`, `catalogos`, `perfiles` ni `tools` como paquetes de primer nivel. Las raíces externas de
perfiles las aporta el host —el proyecto sólo puede seleccionar nombres— y rechazan symlinks, rutas
ausentes y nombres ambiguos; el smoke del wheel usa una raíz externa real. Ninguna herramienta
resuelve ya proyecto ni argumentos al importarse: sus `main(argv)` crean la sesión después de
parsear, probado bajo un `sys.argv` anfitrión inválido. Una instalación no contiene el corpus ni los
fixtures diferenciales internos y por eso exige un proyecto explícito; la ausencia de fixtures sale
no-verde y sin traceback. El flujo temporal externo conserva la prueba diferencial positiva. La suite
cierra 339 tests, la mutación de medidas 129/129 y las particiones modificadas de `proyecto`, `Motor`
y `_compat` cierran 100/100, 22/22 y 5/5. Queda fuera de P3 sincronizar el vendor de Jam y migrar su
oráculo particular.

#### Cierre de independencia de dominio — 2026-07-31

El valor compatible anterior (`catalogo_base: true` cuando faltaba la clave) mantenía una política
implícita: cualquier proyecto externo incorporaba medidas de proceso, meta y simulación de Oracle.
Se eliminó. Ahora un proyecto sin `oracle.json`, o con la clave omitida, carga exclusivamente su
propio catálogo. Las políticas provistas por Oracle y los perfiles son capacidades opt-in; el propio
Oracle declara ambas porque las usa para autocertificarse, y cada consumidor debe tomar la misma
decisión de manera explícita.

La independencia se protege en tres niveles: una regresión construye un proyecto mínimo y comprueba
que no aparecen medidas heredadas; otra inspecciona los artefactos productivos y rechaza nombres de
consumidores o dominios conocidos; y el wheel se prueba desde un proyecto externo y un cwd vacío. El
corpus y los tests pueden conservar procedencia histórica de Jam: son evidencia de generalidad y no
se instalan ni participan del runtime de un host.
