# Oracle — documento integral para NotebookLM

Fuente única de estudio del metalenguaje Oracle: propósito, semántica, autoría, catálogo,
corpus, arquitectura, herramientas, historia, decisiones, auditoría y plan de corrección.

- Generado: `2026-08-25`
- Revisión de código base: `e73b9d4c6d35`
- Partes incluidas: `13`

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

---

> ## Estado: `EXPERIMENTAL` → `METALENGUAJE`
>
> **Hoy es un experimento**, y el metalenguaje es el destino, no la descripción. Falta bastante para
> llegar: la reflexión sobre el catálogo sigue fijada en Python —L2 tiene mecanismo propio, que es
> justo lo que un metalenguaje no debería necesitar—, y el camino está desglosado en
> `PLAN-LENGUAJE.md`.
>
> **No hay fecha de corte, ni condición de cierre, ni tope de tamaño.** Las hubo por un rato, en
> respuesta a dos auditorías externas que midieron a Oracle con la vara de un producto adoptable —
> vara que este README las invitó a usar. Se retiraron el 2026-08-24: un experimento no se gobierna
> con plazos, se gobierna con disparadores, y el de la reificación está escrito en el plan.
>
> Lo que **no** cambió es la exigencia hacia adentro: toda medida sigue declarando qué NO ve, todo
> umbral sigue trayendo su defensa, y la mutación sigue teniendo que terminar en cero sobrevivientes.
> Ser experimental es un estado del proyecto, no un permiso para aflojar sus propias reglas.

---

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

No es un instrumento de medición: es un instrumento de **rechazo**. No calcula calidad: **declina
dejar pasar** lo que no se puede sostener.

<!-- negativas:inicio -->
En este corte hay 5545 líneas de lenguaje y **254 negativas explícitas** (`raise`).
<!-- negativas:fin -->

Un umbral sin defensa no se carga. Una medida sin `alcance` no se carga. Un campo ausente no da
`False`, levanta error. La igualdad exacta entre flotantes está prohibida, incluido el umbral final.
Un dominio sin defectos
declarados no genera fixture. Una medida que no discrimina se denuncia sola.

#### Lo que produce no es confianza: es confianza ACOTADA

El veredicto no es el producto — el **punto ciego** lo es. Un informe verde termina enumerando lo que
no miró, y eso es lo que lo hace usable: un «todo bien» sin su alcance no se puede accionar, porque no
se sabe sobre qué se está callando.

#### La asimetría, medida

La composición está contada más abajo; el reparto es abrumadoramente de un lado: los
falsos verdes son más de diez veces los falsos rojos. Ésa es la justificación empírica de cada decisión de
«negarse antes que permitir». Pero un falso rojo enseña a ignorar el verificador, y por eso pesa igual
de grave: en un solo día lo cometí tres veces.

#### El sujeto es el que construye, no lo construido

<!-- deteccion:inicio -->
Los 67 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 48 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
<!-- deteccion:fin -->

Ninguna de esas vías le pregunta al que escribió el código. Oracle no es un juez de artefactos — es
una prótesis para alguien que escribe la herramienta y su test con la misma mano y no recuerda ayer.

#### El costo, dicho

<!-- escala:inicio -->
**5545 líneas de lenguaje** (`nucleo/`, código y macros) y **254 negativas explícitas** (`raise`). Contra las 36 medidas universales escritas en él (218 líneas): **25,4 a 1**. 29 de las 36 pasan por una macro.
<!-- escala:fin -->

Ésa es la apuesta y ésa es la métrica: que los catálogos de los proyectos crezcan sin hacer crecer el
metalenguaje. Los catálogos externos no se incorporan al núcleo para mejorar artificialmente la
proporción.

> **La proporción es sensible al FORMATO, y eso es un defecto de la métrica.** El 2026-08-25 pasó
> de **16,8 a 24,7** sin que el lenguaje ganara una capacidad ni las medidas perdieran una regla:
> el catálogo se pasó de JSON compacto a la superficie infija y las mismas 33 medidas bajaron de
> 298 líneas a 203. El efecto compone en las dos direcciones a la vez —tener sintaxis suma 900
> líneas al numerador Y acorta el denominador—, así que **el número de hoy no se compara con el de
> ayer**. Es de la misma familia que el hallazgo de `indent=2`, que infló la proporción
> reformateando archivos: mientras el denominador se cuente en LÍNEAS, cambiar cómo se escribe una
> medida mueve la cifra sin que cambie nada de lo que la cifra dice medir. Queda anotado como
> defecto abierto y no se arregla acá: cualquier arreglo bajaría el costo publicado, y una métrica
> no se cambia en el movimiento en que su resultado incomoda.

Es la única medición del proyecto **que no se puede sastrear escribiendo más medidas** — escribir más
medidas es justamente lo que la mejora. Es una cifra sobre el **costo**, no un veredicto: qué se
concluye de ella está en la sección de abajo, y la respuesta corta es «menos de lo que este párrafo
llegó a afirmar».

**Y la proporción no se mueve.** Fue 16,2 antes de `defmacro`, subió a 18,2, y volvió a 16,2. Ni
mejoró ni empeoró: después de meses de trabajo está donde empezó, y las dos veces que se movió fue
por escribir código de núcleo o por escribir medidas universales — nunca por un consumidor.

El corte anterior publicaba «2202 líneas» y «trece a uno» escritos a mano; los valores reales ya eran
2654 y 16,2 a 1, y nada lo detectó, porque el criterio de falsación declarado del proyecto era
justamente el número que no estaba bajo medición. Desde entonces lo genera `tools/cifras.py` y el CI
falla si vence.

Después, `defmacro` empeoró la proporción desde 16,2 — y el plan había predicho que la iba a
**bajar**, porque las tres macros salían del núcleo. Salieron, pero el mecanismo que las reemplaza
—declaración, guardas, registro, expansión acotada— pesa más que las tres funciones que borró. El
pago no es este corte: es que la macro número cuatro ya no cuesta ni una línea de núcleo.

El numerador cuenta `nucleo/macros/*.json` junto con el `.py`, a propósito. Si contara sólo código,
mover Python a datos habría «mejorado» la proporción sin que el lenguaje encogiera un gramo — el
sastreo exacto contra el que esta medición existe.

#### La proporción no alcanza como criterio, y el proyecto es EXPERIMENTAL

Dos auditorías externas coincidieron: como criterio de falsación, la proporción no puede hacer el
trabajo. **Disparó en contra tres cortes seguidos** —16,2 → 18,0 → 18,2— y la respuesta publicada fue
reinterpretarla. Después volvió a 16,2, y eso no la rehabilita: volvió porque se escribieron más
medidas universales, que es el único mecanismo que la mueve hacia abajo.

El problema es estructural y son dos: es inmune a la adopción —los catálogos externos no entran a su
denominador, así que ningún consumidor puede moverla— y es inmune a la migración: al mover una
política real de Python al catálogo, el núcleo bajó tres líneas y la cifra no se movió, porque lo que
queda en Python es código de sensor y eso no puede migrar nunca.

**Pero el error de fondo no era la métrica: era publicarla como criterio.** «Si en seis meses la
proporción no se movió, el lenguaje no valió la pena» es una afirmación de producto, y esto no es un
producto. Es un experimento, y por eso:

> **Oracle está en estado EXPERIMENTAL.** No tiene fecha de corte, ni condición de cierre, ni tope de
> tamaño para el núcleo. Le falta bastante para ser un metalenguaje —la reflexión sobre el catálogo
> sigue fijada en Python, ver `PLAN-LENGUAJE.md`— y ése es el estado declarado,
> no un déficit contra un plazo.

Hubo una puerta de abandono prerregistrada, escrita el 2026-08-24 en respuesta a las auditorías, con
plazo al 2027-01-29 y consecuencia escrita. **Se retiró el mismo día**, junto con el tope de núcleo
que la acompañaba: ese tope era un número inventado —el tamaño de ese momento más cien líneas— y
Oracle no lo necesitaba para nada. Poner plazos y consecuencias a un experimento es tratarlo como lo
que todavía no es, y las auditorías lo midieron con esa vara porque el README las invitó a hacerlo.

Lo que **sí** queda de esa discusión, porque no depende de ningún plazo: la proporción sigue
publicándose y sigue generada por `tools/cifras.py`, con el CI fallando si vence. Es una cifra sobre
el costo, no un veredicto sobre el proyecto — y leerla como veredicto fue el error que corrigió esta
sección.

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
requiere   qué NECESITA ver para concluir  ← opcional
alcance    qué NO ve esta medida  ← OBLIGATORIO
```

`alcance` es obligatorio porque un verificador que dice «TODO VERDE» enseña a confiar en él más de lo
que merece. Acá un informe en verde **termina enumerando lo que no miró**.

El umbral lleva su defensa por el mismo motivo: un número que nadie puede discutir es una métrica
esperando a volverse objetivo.

`requiere` es el espejo de `alcance`, y entró porque declarar un hueco no es cerrarlo. Un agregado
sobre cero filas da `0`, que es indistinguible de un agregado que dio cero: la medida de ausencia
salía **verde justo cuando el mundo estaba peor** —ningún importador, ningún par, ningún grupo—.
Cuando una relación declarada acá viene vacía, el veredicto es `SIN EVIDENCIA`: no es verde y
tampoco es un rojo del mundo, porque no se midió nada.

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
  catalogos/                   sólo medidas UNIVERSALES: proceso · meta · simulacion (.oracle y .json)
  corpus/                      los casos donde la medición dijo bien y no estaba bien (.caso y .json)
  ejemplo/                     un banco de pruebas abstracto, no un dominio

<tu-proyecto>/                 TU PROYECTO
  oracle.json                  perfiles optativos activados de forma explícita
  catalogos/<dominio>/         tus medidas (.oracle y .json)
  escalares.py                 tus funciones de dominio
  corpus/  diferencial/        tus casos (.caso y .json) y tus fixtures
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

**El paquete contiene los cinco componentes.** El corpus (42 casos, en formato de autoría `.caso` o almacenamiento `.json`), la especificación del álgebra,
el evaluador (`nucleo/`), **las medidas universales** dentro de `catalogos/` —como
archivos de datos (`.oracle` y `.json`), no como código—, el sensor de mutación y la prueba diferencial.

**¿Querés escribir una medida?** → `ESCRIBIR-UNA-MEDIDA.md`.
`python tools/medida.py --relaciones` te dice qué hechos hay para medir; `tools/corpus.py --nuevo` crea el caso (`.caso`) y `tools/medida.py --nueva` crea la medida (`.oracle`). Ambos cargan superficie y JSON por igual.

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

<!-- corpus:inicio -->
**99 casos**: 67 defectos y 32 verdes correctos. De los defectos, 64 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 62 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
<!-- corpus:fin -->

<!-- cifras:inicio -->
519 tests · 535/535 mutantes de medida · **2261 sitios de mutación de código** (2056 + 205 del motor Python).
<!-- cifras:fin -->

> **Baseline restaurado el 2026-08-03 sobre el denominador vigente.** Los 16 objetivos de la matriz
> del CI —uno por job, que es como se mide— salen en **VERDE**: cero sobrevivientes, cero errores de
> arnés, **un equivalente declarado** con su razón en `equivalentes.json`. Cada
> ronda muta una copia, puede persistir progreso con `--manifiesto`/`--reanudar` y firma también sus
> tests y archivos de soporte.
>
> El camino en un solo proceso —`mutar_codigo.py` sin `--objetivo`— deja **un timeout**: el mutante
> que apaga `start_new_session` no cuelga un test, los enlentece a todos, y el presupuesto de 60 s se
> agota antes de llegar a la aserción que lo mata. Con `--objetivo` la priorización la corre primero
> y muere. Se documenta en vez de maquillarse: **un timeout no mata a nadie** (caso `016` del corpus),
> así que ese eje se mide particionado y se dice cuál de las dos corridas es la que vale.
>
> Llegar acá exigió corregir lo que hacía **inmedible** al código, no reclasificar veredictos. La
> ronda venía con **158 errores de arnés**: trabajo en tiempo de import —constantes de módulo
> validadas al construirse, `@escalar` corriendo al importar los tests— hacía que un mutante rompiera
> el *descubrimiento* de la suite, y el arnés reportaba «error» donde había un test capaz de matarlo.
> Con eso corregido, 158 → **0**. La tentación era contar un `ImportError` como muerte; habría
> acreditado cobertura real por el motivo equivocado y el hueco seguiría ahí.

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
medida con la misma forma») sonó con veintidós, cuando los dominios de instancia todavía vivían acá.
`ninguno`, `ninguno-par` y `peor` expanden a la forma canónica, y `peor` cerró por construcción la
deuda del umbral duplicado. La cobertura vigente sobre el catálogo universal está en
la cifra de escala; las medidas que no encajan se escriben canónicas y listo.

**Y las macros se declaran EN DATOS.** Hasta el corte anterior `MACROS` era un diccionario de
funciones de Python: las medidas eran datos, pero los **medios de abstracción** no, así que un
proyecto que quería una forma propia tenía que editar el núcleo de Oracle. El dueño del lenguaje era
quien podía editar ese archivo — o sea, el LLM. Ahora una macro es un archivo con la misma forma para
las que trae Oracle y para las que escribe cualquiera:

```json
["defmacro", "todos-cumplen",
  ["id", "relacion", "alias", "predicado", "porque", "alcance"],
  [],
  ["medida", ["$", "id"],
    ["desde", ["de", ["$", "relacion"], ["$", "alias"]],
     ["donde", ["no", ["$", "predicado"]]]],
    ["resumen", "contar", 1],
    ["umbral", "<=", 0, ["$", "porque"]],
    ["alcance", ["$", "alcance"]]]]
```

`ninguno`, `ninguno-par` y `peor` viven en `nucleo/macros/` y se cargan por el
mismo camino: son la biblioteca estándar del lenguaje, no un privilegio del núcleo. Un proyecto suma
las suyas en `<proyecto>/macros/` y no necesita tocar nada de Oracle.

Tres decisiones que valen la pena:

- **Las guardas no traen evaluador nuevo.** `ninguno-par` exige que sus dos alias difieran, y una
  plantilla pura no lo expresa. La guarda se sustituye y la evalúa `evaluar_expr` **sobre una fila
  vacía**: una expresión sin accesores nunca toca la fila. De regalo hereda el contrato entero del
  álgebra, incluida la prohibición de igualdad exacta entre flotantes.
- **Una macro puede construir sobre otra**, acotada por `expansiones_maximas`. Negarlo obligaría a
  copiar el cuerpo, que es lo que la macro vino a evitar.
- **Un parámetro que la plantilla nunca usa no se carga.** Es la misma regla que
  `meta.toda_medida_esta_ejercitada`: lo que nadie ejercita es decoración.

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

El camino de «formato de datos con buenas defensas» a «lenguaje» está desglosado en
`PLAN-LENGUAJE.md`: `defmacro` en datos, reificación mecánica del catálogo, la
decisión sobre composición, y el diferencial propio que hoy está estructuralmente vacío.

- ~~**Elegir una licencia.**~~ **HECHO.** MIT, en `LICENSE` y en los metadatos del
  paquete (`License-Expression: MIT`, con el archivo incluido en el wheel): un tercero puede
  identificar los permisos automáticamente y redistribuirlo.
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

Versión `0.3`, declarada de forma **legible por máquina** en `nucleo/version.py`
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
> [`DECISION-001-RELACIONES-COMO-BOLSAS.md`](DECISION-001-RELACIONES-COMO-BOLSAS.md).

Regla de diseño que gobierna todo el documento: **no se agrega un operador hasta que una segunda
medida lo necesite.** Es lo único que evita que esto se vuelva el proyecto que reemplaza al proyecto.

---

### 0. La versión del lenguaje

La versión es un dato, no una frase. Vive en `nucleo/version.py` como `VERSION_ALGEBRA`, con la
forma `MAYOR.MENOR` (dos enteros). Sin una regla que diga qué cambio sube qué parte, el número es
decorativo; con ella, la incompatibilidad se detecta en vez de descubrirse.

**`MENOR` sube** cuando el álgebra **gana** algo sin cambiar el significado de lo que ya valía: un
nodo opcional nuevo (`requiere`), un operador nuevo (`agrupar`, `unir`), un agregado nuevo, una
escalar declarada nueva, una relación de traza nueva. Quien no usa lo nuevo queda exactamente igual;
quien *implementa el álgebra completo* —una referencia independiente— quedó incompleto y tiene que
volver a verificarse. De `0.2` a `0.3` subió la menor (entraron `agrupar`, `requiere` y `clave`).

**`MAYOR` sube** cuando cambia el **significado o el contrato** de algo que ya existía: la semántica
de un operador (qué hace `min`/`max` con booleanos), la forma canónica de una medida, una validación
que hacía cargar lo que ahora se rechaza, o quitar/renombrar un operador. Eso rompe a todo
consumidor, use o no la parte cambiada. De `0.3` a `1.0`, y la menor vuelve a `0`.

**Cómo se comprueba.** El núcleo publica lo que implementa. Un proyecto puede declarar en
`oracle.json` la versión que necesita (`"algebra": "0.3"`); si no es compatible, la carga falla
cerrado con un mensaje que dice cuál hay y cuál se pidió, y quien no la declara sigue funcionando.
La compatibilidad es la del párrafo anterior: misma `MAYOR` y `MENOR` al menos tan nueva como la
pedida. Una implementación de referencia, en cambio, declara contra qué versión se escribió y el
arnés del diferencial la compara con la del núcleo antes de emitir un fixture: la referencia se fija
a una versión **exacta**, porque un agregado puede no romper a un consumidor y sí a un evaluador que
no conoce el nodo nuevo.

#### La superficie tiene su propia versión

La superficie infija declara la suya, `VERSION_SINTAXIS`, con la misma forma `MAYOR.MENOR` y la
misma maquinaria (`parsear`, `compatible`, `VersionInvalida`). La regla aplica a las medidas
(`.oracle`) y a los casos del corpus (`.caso`): la superficie es cómo se escribe y el JSON es cómo
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
la menor anterior se sigue leyendo idéntico.

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
de sintaxis (`"sintaxis": "0.1"`) con la misma regla que pide la del álgebra.

---

### 1. Hechos y relaciones (L0)

Un **hecho** es un registro de campos escalares. Una **relación** es una bolsa nombrada de hechos del
mismo tipo. La evidencia es un mapa de relaciones:

```json
{
  "pieza":   [{"id": "Muro_A", "x": 100, "y": 100, "ex": 200, "ey": 25}],
  "mutante": [{"id": "firma_por_id", "apunta_a": "funcion._orden_visual",
               "detecciones_conductuales": 0, "rechazos_del_algebra": 0}]
}
```

Nada más. Sin objetos, sin punteros, sin nulos implícitos. El **sensor** que produce la evidencia es
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

La clave es **opcional** y se valida **antes de medir**, fail-closed: si dos hechos repiten la clave
declarada, la evaluación levanta un error que nombra la clave responsable y la fila que la viola — no
un veredicto verde, no un error genérico. Un campo de la clave ausente en un hecho también es error:
una identidad a medias no se puede comprobar, y un nulo implícito la dejaría sin comprobar en
silencio. Sin el nodo, la relación es exactamente la bolsa de siempre, y la multiplicidad intencional
sigue siendo expresable sin declarar nada.

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

**La forma canónica admite un nodo opcional `requiere`, y va antes de `alcance`:**

```json
["medida", "<id>", <tubería>, <resumen>, <umbral>,
  ["requiere", "<relación>", …],
  ["alcance", "<qué NO ve>"]]
```

Es el espejo de `alcance`: uno declara qué NO ve la medida, el otro **qué NECESITA ver para
concluir**. Si alguna de las relaciones listadas viene vacía, la evaluación no mide: devuelve
`SIN EVIDENCIA`, que no es verde y tampoco es un rojo del mundo. Existe porque el álgebra no puede
expresarlo —un agregado sobre cero filas da `0` y un umbral `<= 0` lo lee como éxito— y la ausencia
total salía verde justo cuando el mundo estaba peor; el caso completo está en §8.

Una medida sin el nodo se comporta exactamente como antes y su forma canónica **no cambia**: son seis
elementos, no siete. Un evaluador tiene que aceptar las dos longitudes.

Una medida real, del catálogo que ya corre — sin `unir`, que todavía no tiene usuario:

```json
["medida", "proceso.test_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"],
    ["donde", ["y", ["==", ["campo", "m", "detecciones_conductuales"], 0],
                    ["==", ["campo", "m", "rechazos_del_algebra"], 0]]]],
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
defensas ni alcances: las dos primeras fallan al cargar, y las dos últimas fallan al cargar **y**
además quedan reificadas como medidas de L2 (§4).

**Los testigos no se declaran.** Son las filas que sobrevivieron al último `donde`. Declararlos
aparte obliga a recorrer los datos dos veces y a mantener dos definiciones de lo mismo sincronizadas
a mano — el error concreto que motivó esta especificación (ver
[`004-testigos-duplicados`](corpus/proceso/)).

### 3. Los operadores

Cinco. Cuatro toman relaciones y devuelven una relación: **eso es la clausura**, y es lo que permite
encadenarlos en cualquier orden sin un solo caso especial. `resumen` es el que la rompe a propósito,
porque colapsa a un escalar: por eso va último y una sola vez, y por eso **la clausura es sobre
filas, no sobre medidas**.

Conviene decirlo fuerte, porque la versión corta de esta frase engañaba: una medida termina en un
escalar y un umbral, y ahí se acaba. **Ninguna medida puede consumir los testigos ni el veredicto de
otra**, y eso no es una limitación pendiente sino una decisión tomada y registrada en
[`DECISION-002`](DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md). Las preguntas que esa decisión deja
afuera —«¿qué medidas comparten testigos?»— se responden en L2, midiendo el catálogo como relación.

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
["medida", "meta.ningun_umbral_sin_defensa",
  ["desde", ["de", "medida", "m"], ["donde", ["==", ["campo", "m", "porque"], ""]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un número que nadie puede discutir es una métrica esperando a volverse objetivo"],
  ["alcance", "ve si la defensa está VACÍA. NO ve si la defensa es mala, circular o mentirosa"]]
```

Ese `alcance` es el ejemplo de por qué el campo es obligatorio: la medida es útil y es
superficialísima, y decirlo evita que se lea como más de lo que es.

Tres reglas que antes eran `raise` de `nucleo/medida.py` quedaron reificadas así, como medidas del
catálogo base: `meta.ningun_umbral_sin_defensa`, `meta.ninguna_medida_sin_alcance` y
`meta.ningun_umbral_flotante_de_igualdad`. Las dos primeras conservan el `raise` de carga además de
la medida — son contratos fail-closed, y la medida las vuelve inspeccionables y discutibles —; la
tercera sólo vive en la medida y en `algebra.comparar`, porque un umbral `== 3.14` está bien formado
y su rechazo es un juicio, no un contrato. La distinción completa está en `INFORME.md`.

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
3. el corpus guarda los tres niveles con el mismo formato (en superficie `.caso` para autoría o `.json` para almacenamiento);
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

**La superficie es cómo se escribe; el JSON es cómo se guarda.** Este documento enseña a
escribir medidas y casos directamente en su superficie de autoría (`.oracle` y `.caso`), que el
sistema carga por igual sin paso de traducción.

### El orden importa: primero el caso, después la medida

**Escribí el caso del corpus antes que la medida.** No es prolijidad:

- una medida escrita primero se escribe para pasar, no para atrapar;
- la herramienta puede decirte si tu medida está mal *formada*, pero **no puede saber qué quisiste
  decir**. Una condición invertida —que selecciona lo que está bien en vez de lo que ofende— pasa
  todas las comprobaciones automáticas. El caso es lo único que lo detecta.

```bash
# 1. el caso: la evidencia del defecto, y que se espera ROJO
#    (el andamio ya nace en superficie .caso, o copiá uno que exista)
python tools/corpus.py --nuevo proceso/0NN-lo-que-paso   # crea corpus/proceso/0NN-lo-que-paso.caso

# 2. mirá con qué contás
python tools/medida.py --relaciones     # los hechos y sus campos, derivados de la evidencia real
python tools/medida.py --escalares      # las funciones de dominio, operadores y agregados

# 3. la medida: el andamio ya nace en superficie infija, y el catálogo lo carga tal cual
python tools/medida.py --nueva colocacion.mi_regla     # crea catalogos/colocacion/colocacion.mi_regla.oracle
python tools/medida.py catalogos/colocacion/colocacion.mi_regla.oracle

# 4. que todo siga cerrando
python tools/aceptacion.py    # tu caso tiene que ponerse rojo
python tools/mutar.py         # y el corpus tiene que fijar tu medida
```

#### Los dos formatos del catálogo y del corpus

El catálogo y el corpus cargan **superficie (`.oracle`, `.caso`) y `.json` por igual**: los
archivos en superficie no necesitan traducirse a nada para funcionar. El mismo id en los dos
formatos es un error que nombra los dos archivos — no gana ninguno, porque un ganador silencioso es
una divergencia esperando.

- `python tools/corpus.py --nuevo <grupo/NNN-descripcion>`: crea el andamio del caso, ya en superficie `.caso`.
- `python tools/medida.py --nueva <dominio.nombre>`: crea el andamio de la medida, ya en superficie `.oracle`.
- `python tools/sintaxis.py --imprimir <archivo.json>`: pasa una medida vieja a la superficie.
- `python tools/sintaxis.py --leer <archivo.oracle>`: el camino inverso para medidas, si alguna vez lo necesitás.

El id tiene gramática cerrada y **ASCII**: `dominio.nombre` para medidas y `NNN-descripcion` para
casos (minúsculas, dígitos y `_`/`-`). No es que el proyecto no sea en español —la prosa de
`porque` y de `alcance` lo es entera—: es que el id es también un nombre de archivo, y en Unicode
`dueño` puede ser dos secuencias de bytes distintas que se dibujan idénticas (NFC contra NFD). Dos
ids que nadie puede distinguir mirando son una divergencia silenciosa, y eso se cierra por
gramática.

#### Frontera de confianza

Si el proyecto declara funciones en `escalares.py`, los comandos que cargan o evalúan su catálogo
requieren `--confiar-escalares`. Esa bandera autoriza cargar código Python externo, pero Oracle lo
ejecuta en un trabajador separado: el proceso principal sólo recibe metadatos y resultados JSON. El
trabajador puede leer el proyecto, Oracle y la biblioteca estándar; sólo puede escribir dentro del
proyecto, no puede abrir red ni crear procesos. Si una UDF necesita más autoridad, no pertenece a una
medida: generá ese dato antes y entregalo como evidencia.

`--relaciones` y `--escalares` sin la bandera son seguros: no ejecutan el archivo externo.

El id tiene una gramática cerrada: `dominio.nombre`, con segmentos en minúsculas ASCII, dígitos o
`_`. No se aceptan rutas ni `..`; el archivo se resuelve y confina debajo de `catalogos/` antes de
crear cualquier directorio.

### La forma corta: las macros

**La mayoría de las medidas del catálogo están escritas como macro.** Son azúcar que expande a la forma
canónica —`python tools/medida.py --expandir <archivo>` te muestra en qué—, así que el evaluador, la mutación y el inventario no se
enteran de que existen.

```oracle
ninguno proceso.test_con_mutante_que_lo_mata:
    de mutante m
    donde m.detecciones_conductuales == 0 y m.rechazos_del_algebra == 0
    umbral <= 0 porque "un mutante que sobrevive es un test que no discrimina"
    alcance "cuenta mutantes DECLARADOS. NO ve los que nadie escribió"
```

| Macro | Para qué | Cuántas la usan |
|---|---|---|
| `ninguno` | ninguna fila debe cumplir el predicado | 26 |
| `ninguno-par` | lo mismo sobre PARES de la misma relación | 2 |
| `peor` | el peor caso de una expresión no pasa de una tolerancia | 2 |

**`peor` recibe la tolerancia una sola vez** y genera con ella el filtro y el umbral:

```oracle
peor snap.grilla:
    de pieza a
    expresion desvio_de_grilla(hecho(a), 100.0)
    tolerancia 1.0
    umbral <= 1.0 porque "por debajo de 1 cm el desvío no se ve"
    alcance "desvío del PIVOTE. NO ve si el pivote está bien puesto dentro de la malla"
```

Antes había que escribir la tolerancia dos veces y nada las mantenía juntas — era el caso `012` del corpus, cerrado por
construcción.

Las macros no son un embudo: si tu caso no encaja, la forma canónica sigue siendo válida.
`colocacion.interpenetracion` está escrita así porque une dos relaciones DISTINTAS.

### La forma canónica

```oracle-gramatica
medida dominio.nombre:
    de relacion x
    donde <lo que OFENDE>
    resumen contar(1)
    umbral <= 0 porque "por qué ese número y no otro"
    requiere relacion
    alcance "qué NO ve esta medida"
```

Las piezas obligatorias están por una razón:

- **`umbral` con `porque`** — un número que nadie puede discutir es una métrica esperando a volverse objetivo. Un umbral de igualdad (`==`) no se usa y está prohibido.
- **`alcance`** — un verde que no dice lo que no miró se lee como «está bien». Con esto, el informe
  termina enumerando sus propios puntos ciegos.
- **`requiere`** — declara qué relaciones de evidencia son indispensables para concluir. Si una relación requerida viene vacía o falta, la evaluación no emite un verde espurio sino `SIN EVIDENCIA`.

Y una que **no se declara**: los **testigos** son las filas que sobrevivieron al `donde`. No los
calculás aparte — si lo hicieras, tendrías la misma condición escrita dos veces y nada que las
mantenga sincronizadas. Tampoco se permite componer medidas entre sí (`DECISION-002`): cada medida
es una unidad de juicio aislada sobre evidencia directa.

### El formato de almacenamiento: por qué JSON

La superficie infija es cómo un humano la escribe, pero el archivo en `catalogos/` se guarda como una
lista JSON. Por ejemplo, la forma canónica anterior se almacena así:

```json
["medida", "dominio.nombre",
  ["desde", ["de", "relacion", "x"],
            ["donde", ["==", ["campo", "x", "activo"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "por qué ese número y no otro"],
  ["requiere", "relacion"],
  ["alcance", "qué NO ve esta medida"]]
```

¿Por qué almacenar una medida como JSON y no como texto plano? Porque **es homoicónico: el JSON es directamente el árbol de sintaxis abstracta (AST)**. Al ser una estructura de datos estándar y pura:
- Las medidas pueden inspeccionarse, mutarse y validarse mecánicamente sin requerir un parser complejo en cada etapa.
- **Las medidas pueden hablar de medidas**: es el nivel **L2** del proyecto. El propio catálogo de medidas se convierte en una relación (`medida_en_uso`), y se puede juzgar con el mismo álgebra de siempre (por ejemplo, verificando que ninguna medida use umbrales de igualdad flotante o que todas declaren su defensa y alcance).

### Tres ejemplos, de menor a mayor

#### 1. Contar lo que ofende

```oracle
medida proceso.test_con_mutante_que_lo_mata:
    de mutante m
    donde m.detecciones_conductuales == 0 y m.rechazos_del_algebra == 0
    resumen contar(1)
    umbral <= 0 porque "un mutante que sobrevive es un test que no discrimina: pasa con el código roto"
    alcance "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los que nadie escribió"
```

El 90% de las medidas son así: filtrás lo malo, contás, y el umbral es `<= 0` (un umbral `==` no se usa y está prohibido por `meta.ningun_umbral_de_igualdad`).

#### 2. Medir una magnitud, no contar

```oracle
medida snap.grilla:
    de pieza a
    donde desvio_de_grilla(hecho(a), 100.0) > 1.0
    resumen max(desvio_de_grilla(hecho(a), 100.0))
    umbral <= 1.0 porque "por debajo de 1 cm el desvío no se ve"
    alcance "desvío del PIVOTE. NO ve si el pivote está bien puesto dentro de la malla"
```

Acá el valor es centímetros y no una cuenta, y eso dice más en el informe. **Escrita a mano en forma canónica, la
tolerancia aparece dos veces** —en el `donde` y en el `umbral`— y nada las mantiene juntas: era el
caso `012` del corpus. Por eso esta forma se escribe habitualmente con la macro `peor`, que la recibe una sola vez.

#### 3. Comparar filas entre sí

```oracle
medida vault.nombre_unico_en_el_vault:
    de documento a
    unir documento b
    donde a.nombre == b.nombre y a.carpeta != b.carpeta
    resumen contar(1)
    umbral <= 0 porque "un wikilink apunta por NOMBRE y no por ruta: dos homónimos dejan el enlace a cara o cruz"
    alcance "NO ve nombres parecidos pero distintos, que confunden aunque no rompan un enlace"
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

#### meta.agrupar_no_agranda_la_relacion

- **mide sobre** la relación `paso`
- **umbral**: `<= 0`
- **por qué ese número**: agrupar colapsa: una fila por grupo, y los grupos no pueden ser más que las filas que los originaron. Si sale agrandando, está inventando grupos que ninguna fila sostiene, y un agregado sobre un grupo inventado es un número sin evidencia detrás
- **qué NO ve**: compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.agrupar_no_agranda_la_relacion",
  "paso",
  "p",
  ["y", ["==", ["campo", "p", "operador"], "agrupar"], [">", ["campo", "p", "filas_despues"], ["campo", "p", "filas_antes"]]],
  "agrupar colapsa: una fila por grupo, y los grupos no pueden ser más que las filas que los originaron. Si sale agrandando, está inventando grupos que ninguna fila sostiene, y un agregado sobre un grupo inventado es un número sin evidencia detrás",
  "compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.agrupar_no_agranda_la_relacion",
  ["desde", ["de", "paso", "p"], ["donde", ["y", ["==", ["campo", "p", "operador"], "agrupar"], [">", ["campo", "p", "filas_despues"], ["campo", "p", "filas_antes"]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "agrupar colapsa: una fila por grupo, y los grupos no pueden ser más que las filas que los originaron. Si sale agrandando, está inventando grupos que ninguna fila sostiene, y un agregado sobre un grupo inventado es un número sin evidencia detrás"],
  ["alcance", "compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción"]
]
```

#### meta.agrupar_sin_claves_es_el_resumen_global

- **mide sobre** la relación `equivalencia`
- **umbral**: `<= 0`
- **por qué ese número**: sin claves hay un solo grupo, así que agregar por grupo y agregar sobre todo tienen que dar el mismo número. Si no coinciden, `agrupar` pierde o inventa filas al colapsar, y todo agregado calculado sobre un grupo así es un número sin evidencia detrás. NO se exigen los mismos testigos, y no es una concesión: un grupo no es un hecho, los hechos se consumieron al agruparse, así que las dos formas señalan cosas distintas a propósito
- **qué NO ve**: compara las dos formas para los cinco agregados, sobre una sonda construida. NO compara testigos —difieren por diseño— ni cubre `agrupar` CON claves, donde la equivalencia no aplica porque hay más de un grupo. Si equivalencia viene vacía no hay desacuerdos observados y verde es correcto; además metamorficas.py construye las sondas por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.agrupar_sin_claves_es_el_resumen_global",
  "equivalencia",
  "e",
  ["y", ["==", ["campo", "e", "propiedad"], "agrupar_sin_claves_es_el_resumen_global"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false]]],
  "sin claves hay un solo grupo, así que agregar por grupo y agregar sobre todo tienen que dar el mismo número. Si no coinciden, `agrupar` pierde o inventa filas al colapsar, y todo agregado calculado sobre un grupo así es un número sin evidencia detrás. NO se exigen los mismos testigos, y no es una concesión: un grupo no es un hecho, los hechos se consumieron al agruparse, así que las dos formas señalan cosas distintas a propósito",
  "compara las dos formas para los cinco agregados, sobre una sonda construida. NO compara testigos —difieren por diseño— ni cubre `agrupar` CON claves, donde la equivalencia no aplica porque hay más de un grupo. Si equivalencia viene vacía no hay desacuerdos observados y verde es correcto; además metamorficas.py construye las sondas por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.agrupar_sin_claves_es_el_resumen_global",
  ["desde", ["de", "equivalencia", "e"], ["donde", ["y", ["==", ["campo", "e", "propiedad"], "agrupar_sin_claves_es_el_resumen_global"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "sin claves hay un solo grupo, así que agregar por grupo y agregar sobre todo tienen que dar el mismo número. Si no coinciden, `agrupar` pierde o inventa filas al colapsar, y todo agregado calculado sobre un grupo así es un número sin evidencia detrás. NO se exigen los mismos testigos, y no es una concesión: un grupo no es un hecho, los hechos se consumieron al agruparse, así que las dos formas señalan cosas distintas a propósito"],
  ["alcance", "compara las dos formas para los cinco agregados, sobre una sonda construida. NO compara testigos —difieren por diseño— ni cubre `agrupar` CON claves, donde la equivalencia no aplica porque hay más de un grupo. Si equivalencia viene vacía no hay desacuerdos observados y verde es correcto; además metamorficas.py construye las sondas por construcción"]
]
```

#### meta.donde_compone

- **mide sobre** la relación `equivalencia`
- **umbral**: `<= 0`
- **por qué ese número**: filtrar por P y después por Q tiene que dejar exactamente las mismas filas que filtrar una vez por «P y Q»: son la misma pregunta escrita de dos maneras. Se exigen las tres coincidencias y no sólo el veredicto, porque las filas que sobreviven al último `donde` SON los testigos, y dos formas que dan el mismo número señalando filas distintas mandan a una persona a mirar el lugar equivocado
- **qué NO ve**: compara las dos formas sobre una sonda construida con filas que pasan cada filtro y filas que no. NO cubre predicados con UDF ni con `o` anidado, y no dice nada sobre el catálogo publicado: hoy ninguna medida usa dos `donde`, así que esta propiedad se comprueba antes de tener usuario. Si equivalencia viene vacía no hay fallas de composición y verde es correcto; además metamorficas.py construye las sondas por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.donde_compone",
  "equivalencia",
  "e",
  ["y", ["==", ["campo", "e", "propiedad"], "donde_compone"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false]]],
  "filtrar por P y después por Q tiene que dejar exactamente las mismas filas que filtrar una vez por «P y Q»: son la misma pregunta escrita de dos maneras. Se exigen las tres coincidencias y no sólo el veredicto, porque las filas que sobreviven al último `donde` SON los testigos, y dos formas que dan el mismo número señalando filas distintas mandan a una persona a mirar el lugar equivocado",
  "compara las dos formas sobre una sonda construida con filas que pasan cada filtro y filas que no. NO cubre predicados con UDF ni con `o` anidado, y no dice nada sobre el catálogo publicado: hoy ninguna medida usa dos `donde`, así que esta propiedad se comprueba antes de tener usuario. Si equivalencia viene vacía no hay fallas de composición y verde es correcto; además metamorficas.py construye las sondas por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.donde_compone",
  ["desde", ["de", "equivalencia", "e"], ["donde", ["y", ["==", ["campo", "e", "propiedad"], "donde_compone"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "filtrar por P y después por Q tiene que dejar exactamente las mismas filas que filtrar una vez por «P y Q»: son la misma pregunta escrita de dos maneras. Se exigen las tres coincidencias y no sólo el veredicto, porque las filas que sobreviven al último `donde` SON los testigos, y dos formas que dan el mismo número señalando filas distintas mandan a una persona a mirar el lugar equivocado"],
  ["alcance", "compara las dos formas sobre una sonda construida con filas que pasan cada filtro y filas que no. NO cubre predicados con UDF ni con `o` anidado, y no dice nada sobre el catálogo publicado: hoy ninguna medida usa dos `donde`, así que esta propiedad se comprueba antes de tener usuario. Si equivalencia viene vacía no hay fallas de composición y verde es correcto; además metamorficas.py construye las sondas por construcción"]
]
```

#### meta.donde_nunca_agrega_filas

- **mide sobre** la relación `paso`
- **umbral**: `<= 0`
- **por qué ese número**: un filtro que agrega filas no es un filtro, y los testigos que publica no son los que sobrevivieron: el informe estaría nombrando filas que la medida nunca vio ofender
- **qué NO ve**: compara el conteo antes y después de cada `donde` sobre las evaluaciones que se trazaron. NO ve si las filas que quedaron son las correctas —sólo cuántas—, ni cubre una evaluación que no se corrió bajo traza. Si paso viene vacía no hay filtros que agranden la relación y verde es correcto; además trazar.py garantiza pasos trazados por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.donde_nunca_agrega_filas",
  "paso",
  "p",
  ["y", ["==", ["campo", "p", "operador"], "donde"], [">", ["campo", "p", "filas_despues"], ["campo", "p", "filas_antes"]]],
  "un filtro que agrega filas no es un filtro, y los testigos que publica no son los que sobrevivieron: el informe estaría nombrando filas que la medida nunca vio ofender",
  "compara el conteo antes y después de cada `donde` sobre las evaluaciones que se trazaron. NO ve si las filas que quedaron son las correctas —sólo cuántas—, ni cubre una evaluación que no se corrió bajo traza. Si paso viene vacía no hay filtros que agranden la relación y verde es correcto; además trazar.py garantiza pasos trazados por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.donde_nunca_agrega_filas",
  ["desde", ["de", "paso", "p"], ["donde", ["y", ["==", ["campo", "p", "operador"], "donde"], [">", ["campo", "p", "filas_despues"], ["campo", "p", "filas_antes"]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un filtro que agrega filas no es un filtro, y los testigos que publica no son los que sobrevivieron: el informe estaría nombrando filas que la medida nunca vio ofender"],
  ["alcance", "compara el conteo antes y después de cada `donde` sobre las evaluaciones que se trazaron. NO ve si las filas que quedaron son las correctas —sólo cuántas—, ni cubre una evaluación que no se corrió bajo traza. Si paso viene vacía no hay filtros que agranden la relación y verde es correcto; además trazar.py garantiza pasos trazados por construcción"]
]
```

#### meta.el_caso_reclama_una_medida_que_existe

- **mide sobre** la relación `caso`
- **umbral**: `<= 0`
- **por qué ese número**: un caso que apunta a una medida inexistente no fija nada y nadie se enteraría: pasaría por el corpus como si estuviera cubierto
- **qué NO ve**: ve el id que el caso RECLAMA. NO confunde esto con un hueco declarado —un caso sin medida no reclama nada— y NO ve si el id que existe es el adecuado para ese caso. Si caso viene vacía no hay casos que reclamen medidas inexistentes y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar L2

Como está escrita:

```json
[
  "ninguno",
  "meta.el_caso_reclama_una_medida_que_existe",
  "caso",
  "c",
  ["y", ["==", ["campo", "c", "tiene_medida"], true], ["==", ["campo", "c", "medida_existe"], false]],
  "un caso que apunta a una medida inexistente no fija nada y nadie se enteraría: pasaría por el corpus como si estuviera cubierto",
  "ve el id que el caso RECLAMA. NO confunde esto con un hueco declarado —un caso sin medida no reclama nada— y NO ve si el id que existe es el adecuado para ese caso. Si caso viene vacía no hay casos que reclamen medidas inexistentes y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar L2"
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
  ["alcance", "ve el id que el caso RECLAMA. NO confunde esto con un hueco declarado —un caso sin medida no reclama nada— y NO ve si el id que existe es el adecuado para ese caso. Si caso viene vacía no hay casos que reclamen medidas inexistentes y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar L2"]
]
```

#### meta.el_caso_se_pone_como_debe

- **mide sobre** la relación `caso`
- **umbral**: `<= 0`
- **por qué ese número**: un caso del corpus es un defecto real observado: si la medida que lo reclama no se pone roja ahí, la medida está mal escrita o falta lenguaje. Y al revés, un caso correcto que se pone rojo es un falso rojo, que enseña a ignorar el verificador
- **qué NO ve**: compara el veredicto contra la polaridad declarada del caso. NO ve si el caso está bien etiquetado, ni si la evidencia que trae es la del defecto que dice traer. Si caso viene vacía no hay desacuerdos de polaridad y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar el nivel meta

Como está escrita:

```json
[
  "ninguno",
  "meta.el_caso_se_pone_como_debe",
  "caso",
  "c",
  ["!=", ["campo", "c", "esperado_ok"], ["campo", "c", "dio_ok"]],
  "un caso del corpus es un defecto real observado: si la medida que lo reclama no se pone roja ahí, la medida está mal escrita o falta lenguaje. Y al revés, un caso correcto que se pone rojo es un falso rojo, que enseña a ignorar el verificador",
  "compara el veredicto contra la polaridad declarada del caso. NO ve si el caso está bien etiquetado, ni si la evidencia que trae es la del defecto que dice traer. Si caso viene vacía no hay desacuerdos de polaridad y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar el nivel meta"
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
  ["alcance", "compara el veredicto contra la polaridad declarada del caso. NO ve si el caso está bien etiquetado, ni si la evidencia que trae es la del defecto que dice traer. Si caso viene vacía no hay desacuerdos de polaridad y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar el nivel meta"]
]
```

#### meta.el_hueco_declarado_explica_por_que

- **mide sobre** la relación `caso`
- **umbral**: `<= 0`
- **por qué ese número**: un caso sin medida y sin explicación es un caso que alguien va a borrar por prolijidad, y con él se va la memoria de lo que el marco todavía no puede medir
- **qué NO ve**: ve que cada caso marcado explícitamente como hueco abierto tenga una explicación. NO juzga esa explicación ni confunde casos resueltos o límites humanos con trabajo pendiente. Si caso viene vacía no hay huecos abiertos sin explicar y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.el_hueco_declarado_explica_por_que",
  "caso",
  "c",
  ["y", ["==", ["campo", "c", "tiene_medida"], false], ["==", ["campo", "c", "es_hueco_abierto"], true], ["==", ["campo", "c", "explica_el_hueco"], false]],
  "un caso sin medida y sin explicación es un caso que alguien va a borrar por prolijidad, y con él se va la memoria de lo que el marco todavía no puede medir",
  "ve que cada caso marcado explícitamente como hueco abierto tenga una explicación. NO juzga esa explicación ni confunde casos resueltos o límites humanos con trabajo pendiente. Si caso viene vacía no hay huecos abiertos sin explicar y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción"
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
  ["alcance", "ve que cada caso marcado explícitamente como hueco abierto tenga una explicación. NO juzga esa explicación ni confunde casos resueltos o límites humanos con trabajo pendiente. Si caso viene vacía no hay huecos abiertos sin explicar y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción"]
]
```

#### meta.el_nivel_no_se_confunde_con_el_dominio

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: el dominio dice QUÉ se mide y el nivel dice SOBRE QUÉ; mezclarlos hace que una medida del mundo se archive como si fuera del lenguaje, y ahí deja de encontrarla quien la busca
- **qué NO ve**: compara el prefijo del nombre contra la relación de origen. NO ve si el dominio elegido es el correcto, ni si la medida mide lo que dice medir. Si medida viene vacía no hay medidas que confundan nivel con dominio y verde es correcto; además el catálogo evaluado contiene al menos las medidas meta por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.el_nivel_no_se_confunde_con_el_dominio",
  "medida",
  "m",
  ["!=", ["campo", "m", "es_meta_por_el_nombre"], ["campo", "m", "es_meta_por_lo_que_mide"]],
  "el dominio dice QUÉ se mide y el nivel dice SOBRE QUÉ; mezclarlos hace que una medida del mundo se archive como si fuera del lenguaje, y ahí deja de encontrarla quien la busca",
  "compara el prefijo del nombre contra la relación de origen. NO ve si el dominio elegido es el correcto, ni si la medida mide lo que dice medir. Si medida viene vacía no hay medidas que confundan nivel con dominio y verde es correcto; además el catálogo evaluado contiene al menos las medidas meta por construcción"
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
  ["alcance", "compara el prefijo del nombre contra la relación de origen. NO ve si el dominio elegido es el correcto, ni si la medida mide lo que dice medir. Si medida viene vacía no hay medidas que confundan nivel con dominio y verde es correcto; además el catálogo evaluado contiene al menos las medidas meta por construcción"]
]
```

#### meta.los_logicos_evaluan_todos_sus_operandos

- **mide sobre** la relación `nodo`
- **umbral**: `<= 0`
- **por qué ese número**: un operando que no se evaluó es un error que no se levantó. La especificación dice que comparar contra un campo ausente levanta error y no devuelve False, porque un False silencioso lo convierte en un verde; cortocircuitar el `y` deshace esa regla justo cuando el primer operando ya decidió, y encima la vuelve dependiente de los datos: la misma medida rota rompe con una evidencia y se esconde con otra
- **qué NO ve**: cuenta operandos evaluados contra los declarados en el AST, en cada `y` y cada `o` trazado. NO ve si el valor de cada operando es correcto, y no cubre una evaluación que se corrió sin traza. Si nodo viene vacía no hay cortocircuitos observados y verde es correcto; además trazar.py garantiza nodos trazados por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.los_logicos_evaluan_todos_sus_operandos",
  "nodo",
  "n",
  ["!=", ["campo", "n", "evaluados"], ["campo", "n", "declarados"]],
  "un operando que no se evaluó es un error que no se levantó. La especificación dice que comparar contra un campo ausente levanta error y no devuelve False, porque un False silencioso lo convierte en un verde; cortocircuitar el `y` deshace esa regla justo cuando el primer operando ya decidió, y encima la vuelve dependiente de los datos: la misma medida rota rompe con una evidencia y se esconde con otra",
  "cuenta operandos evaluados contra los declarados en el AST, en cada `y` y cada `o` trazado. NO ve si el valor de cada operando es correcto, y no cubre una evaluación que se corrió sin traza. Si nodo viene vacía no hay cortocircuitos observados y verde es correcto; además trazar.py garantiza nodos trazados por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.los_logicos_evaluan_todos_sus_operandos",
  ["desde", ["de", "nodo", "n"], ["donde", ["!=", ["campo", "n", "evaluados"], ["campo", "n", "declarados"]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un operando que no se evaluó es un error que no se levantó. La especificación dice que comparar contra un campo ausente levanta error y no devuelve False, porque un False silencioso lo convierte en un verde; cortocircuitar el `y` deshace esa regla justo cuando el primer operando ya decidió, y encima la vuelve dependiente de los datos: la misma medida rota rompe con una evidencia y se esconde con otra"],
  ["alcance", "cuenta operandos evaluados contra los declarados en el AST, en cada `y` y cada `o` trazado. NO ve si el valor de cada operando es correcto, y no cubre una evaluación que se corrió sin traza. Si nodo viene vacía no hay cortocircuitos observados y verde es correcto; además trazar.py garantiza nodos trazados por construcción"]
]
```

#### meta.ningun_umbral_de_igualdad

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: un umbral `==` no tiene borde útil para la mutación: un caso pegado al límite no puede distinguir entre una igualdad exacta bien elegida y una tolerancia que faltó escribir como comparación de orden
- **qué NO ve**: mira sólo el operador final del umbral de cada medida. NO ve igualdades dentro de filtros o agregados, ni decide si `!=` es una política válida para un dominio concreto. Si medida viene vacía significa que no hay medidas en el catálogo que ofendan la regla y verde es correcto; además el catálogo evaluado contiene al menos las medidas meta por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.ningun_umbral_de_igualdad",
  "medida",
  "m",
  ["==", ["campo", "m", "comparador"], "=="],
  "un umbral `==` no tiene borde útil para la mutación: un caso pegado al límite no puede distinguir entre una igualdad exacta bien elegida y una tolerancia que faltó escribir como comparación de orden",
  "mira sólo el operador final del umbral de cada medida. NO ve igualdades dentro de filtros o agregados, ni decide si `!=` es una política válida para un dominio concreto. Si medida viene vacía significa que no hay medidas en el catálogo que ofendan la regla y verde es correcto; además el catálogo evaluado contiene al menos las medidas meta por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ningun_umbral_de_igualdad",
  ["desde", ["de", "medida", "m"], ["donde", ["==", ["campo", "m", "comparador"], "=="]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un umbral `==` no tiene borde útil para la mutación: un caso pegado al límite no puede distinguir entre una igualdad exacta bien elegida y una tolerancia que faltó escribir como comparación de orden"],
  ["alcance", "mira sólo el operador final del umbral de cada medida. NO ve igualdades dentro de filtros o agregados, ni decide si `!=` es una política válida para un dominio concreto. Si medida viene vacía significa que no hay medidas en el catálogo que ofendan la regla y verde es correcto; además el catálogo evaluado contiene al menos las medidas meta por construcción"]
]
```

#### meta.ningun_umbral_flotante_de_igualdad

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: un umbral `==` o `!=` sobre un flotante compara cantidades medidas con una exactitud que la representación no garantiza: 0.1+0.2 no es 0.3, y una igualdad exacta ahí es una falsedad silenciosa que se lee como verde. La comparación de orden con tolerancia (`cerca`) deja el margen a la vista y con su defensa
- **qué NO ve**: mira el operador y el tipo del valor final del umbral de cada medida. NO ve igualdades exactas dentro de expresiones o agregados — de ésas se ocupa el álgebra al evaluar — y NO juzga `==` sobre enteros, textos ni booleanos, que se comparan exacto

Como está escrita:

```json
[
  "ninguno",
  "meta.ningun_umbral_flotante_de_igualdad",
  "medida",
  "m",
  ["y", ["==", ["campo", "m", "umbral_es_flotante"], true], ["o", ["==", ["campo", "m", "comparador"], "=="], ["==", ["campo", "m", "comparador"], "!="]]],
  "un umbral `==` o `!=` sobre un flotante compara cantidades medidas con una exactitud que la representación no garantiza: 0.1+0.2 no es 0.3, y una igualdad exacta ahí es una falsedad silenciosa que se lee como verde. La comparación de orden con tolerancia (`cerca`) deja el margen a la vista y con su defensa",
  "mira el operador y el tipo del valor final del umbral de cada medida. NO ve igualdades exactas dentro de expresiones o agregados — de ésas se ocupa el álgebra al evaluar — y NO juzga `==` sobre enteros, textos ni booleanos, que se comparan exacto"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ningun_umbral_flotante_de_igualdad",
  ["desde", ["de", "medida", "m"], ["donde", ["y", ["==", ["campo", "m", "umbral_es_flotante"], true], ["o", ["==", ["campo", "m", "comparador"], "=="], ["==", ["campo", "m", "comparador"], "!="]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un umbral `==` o `!=` sobre un flotante compara cantidades medidas con una exactitud que la representación no garantiza: 0.1+0.2 no es 0.3, y una igualdad exacta ahí es una falsedad silenciosa que se lee como verde. La comparación de orden con tolerancia (`cerca`) deja el margen a la vista y con su defensa"],
  ["alcance", "mira el operador y el tipo del valor final del umbral de cada medida. NO ve igualdades exactas dentro de expresiones o agregados — de ésas se ocupa el álgebra al evaluar — y NO juzga `==` sobre enteros, textos ni booleanos, que se comparan exacto"]
]
```

#### meta.ningun_umbral_sin_defensa

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: un número que nadie puede discutir es una métrica esperando a volverse objetivo: el `porque` es lo que hace que un verde sea accionable y no una orden que se obedece sin leer
- **qué NO ve**: ve si la defensa del umbral está VACÍA. NO ve si la defensa es mala, circular o mentirosa — juzgar la calidad de una justificación es otra regla, no ésta

Como está escrita:

```json
[
  "ninguno",
  "meta.ningun_umbral_sin_defensa",
  "medida",
  "m",
  ["==", ["campo", "m", "porque"], ""],
  "un número que nadie puede discutir es una métrica esperando a volverse objetivo: el `porque` es lo que hace que un verde sea accionable y no una orden que se obedece sin leer",
  "ve si la defensa del umbral está VACÍA. NO ve si la defensa es mala, circular o mentirosa — juzgar la calidad de una justificación es otra regla, no ésta"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ningun_umbral_sin_defensa",
  ["desde", ["de", "medida", "m"], ["donde", ["==", ["campo", "m", "porque"], ""]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un número que nadie puede discutir es una métrica esperando a volverse objetivo: el `porque` es lo que hace que un verde sea accionable y no una orden que se obedece sin leer"],
  ["alcance", "ve si la defensa del umbral está VACÍA. NO ve si la defensa es mala, circular o mentirosa — juzgar la calidad de una justificación es otra regla, no ésta"]
]
```

#### meta.ninguna_medida_sin_alcance

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: un verde que no declara qué NO miró se lee como «está bien»: el informe termina enumerando los puntos ciegos de cada medida, y sin `alcance` esa enumeración queda muda justo donde más importa
- **qué NO ve**: ve si el `alcance` está VACÍO. NO impone una fórmula textual ni un idioma, y NO juzga si el punto ciego declarado es el correcto o el completo

Como está escrita:

```json
[
  "ninguno",
  "meta.ninguna_medida_sin_alcance",
  "medida",
  "m",
  ["==", ["campo", "m", "alcance"], ""],
  "un verde que no declara qué NO miró se lee como «está bien»: el informe termina enumerando los puntos ciegos de cada medida, y sin `alcance` esa enumeración queda muda justo donde más importa",
  "ve si el `alcance` está VACÍO. NO impone una fórmula textual ni un idioma, y NO juzga si el punto ciego declarado es el correcto o el completo"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ninguna_medida_sin_alcance",
  ["desde", ["de", "medida", "m"], ["donde", ["==", ["campo", "m", "alcance"], ""]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un verde que no declara qué NO miró se lee como «está bien»: el informe termina enumerando los puntos ciegos de cada medida, y sin `alcance` esa enumeración queda muda justo donde más importa"],
  ["alcance", "ve si el `alcance` está VACÍO. NO impone una fórmula textual ni un idioma, y NO juzga si el punto ciego declarado es el correcto o el completo"]
]
```

#### meta.sintaxis_casos_cubre_casos

- **mide sobre** la relación `equivalencia`
- **umbral**: `<= 0`
- **por qué ese número**: todo caso generado desde la forma de datos que acepta el corpus debe imprimirse, releerse y reimprimirse sin perder relaciones, valores JSON, prosa ni el nulo de medida
- **qué NO ve**: comprueba casos sintéticos derivados de la forma L0 de un caso: relación ausente, relación presente vacía, una a tres relaciones, filas homogéneas y heterogéneas, clave declarada y no declarada, textos, enteros, floats, true, false, null, el texto "null", prosa con backticks, comillas y saltos de línea, y un caso con `medida: null`. NO cubre objetos anidados ni listas como valores de campo porque L0 los rechaza, ni comprueba que una medida reclamada exista. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py genera las sondas por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.sintaxis_casos_cubre_casos",
  "equivalencia",
  "e",
  ["y", ["==", ["campo", "e", "propiedad"], "sintaxis_casos_cubre_casos"], ["o", ["==", ["campo", "e", "evaluo"], false], ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false], ["!=", ["campo", "e", "error"], ""]]],
  "todo caso generado desde la forma de datos que acepta el corpus debe imprimirse, releerse y reimprimirse sin perder relaciones, valores JSON, prosa ni el nulo de medida",
  "comprueba casos sintéticos derivados de la forma L0 de un caso: relación ausente, relación presente vacía, una a tres relaciones, filas homogéneas y heterogéneas, clave declarada y no declarada, textos, enteros, floats, true, false, null, el texto \"null\", prosa con backticks, comillas y saltos de línea, y un caso con `medida: null`. NO cubre objetos anidados ni listas como valores de campo porque L0 los rechaza, ni comprueba que una medida reclamada exista. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py genera las sondas por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.sintaxis_casos_cubre_casos",
  ["desde", ["de", "equivalencia", "e"], ["donde", ["y", ["==", ["campo", "e", "propiedad"], "sintaxis_casos_cubre_casos"], ["o", ["==", ["campo", "e", "evaluo"], false], ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false], ["!=", ["campo", "e", "error"], ""]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "todo caso generado desde la forma de datos que acepta el corpus debe imprimirse, releerse y reimprimirse sin perder relaciones, valores JSON, prosa ni el nulo de medida"],
  ["alcance", "comprueba casos sintéticos derivados de la forma L0 de un caso: relación ausente, relación presente vacía, una a tres relaciones, filas homogéneas y heterogéneas, clave declarada y no declarada, textos, enteros, floats, true, false, null, el texto \"null\", prosa con backticks, comillas y saltos de línea, y un caso con `medida: null`. NO cubre objetos anidados ni listas como valores de campo porque L0 los rechaza, ni comprueba que una medida reclamada exista. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py genera las sondas por construcción"]
]
```

#### meta.sintaxis_casos_ida_y_vuelta

- **mide sobre** la relación `equivalencia`
- **umbral**: `<= 0`
- **por qué ese número**: la superficie de casos es reversible sólo si cada caso publicado conserva el JSON de almacenamiento y el texto canónico al imprimirse, releerse y reimprimirse
- **qué NO ve**: comprueba los casos publicados del corpus, en `.caso` y en `.json`. NO demuestra que la plantilla sea suficiente para escribir cualquier caso ni valida el significado de la evidencia; sólo que la forma canónica de caso vuelve al mismo JSON y al mismo texto. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py recorre el corpus por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.sintaxis_casos_ida_y_vuelta",
  "equivalencia",
  "e",
  ["y", ["==", ["campo", "e", "propiedad"], "sintaxis_casos_ida_y_vuelta"], ["o", ["==", ["campo", "e", "evaluo"], false], ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false], ["!=", ["campo", "e", "error"], ""]]],
  "la superficie de casos es reversible sólo si cada caso publicado conserva el JSON de almacenamiento y el texto canónico al imprimirse, releerse y reimprimirse",
  "comprueba los casos publicados del corpus, en `.caso` y en `.json`. NO demuestra que la plantilla sea suficiente para escribir cualquier caso ni valida el significado de la evidencia; sólo que la forma canónica de caso vuelve al mismo JSON y al mismo texto. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py recorre el corpus por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.sintaxis_casos_ida_y_vuelta",
  ["desde", ["de", "equivalencia", "e"], ["donde", ["y", ["==", ["campo", "e", "propiedad"], "sintaxis_casos_ida_y_vuelta"], ["o", ["==", ["campo", "e", "evaluo"], false], ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false], ["!=", ["campo", "e", "error"], ""]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "la superficie de casos es reversible sólo si cada caso publicado conserva el JSON de almacenamiento y el texto canónico al imprimirse, releerse y reimprimirse"],
  ["alcance", "comprueba los casos publicados del corpus, en `.caso` y en `.json`. NO demuestra que la plantilla sea suficiente para escribir cualquier caso ni valida el significado de la evidencia; sólo que la forma canónica de caso vuelve al mismo JSON y al mismo texto. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py recorre el corpus por construcción"]
]
```

#### meta.sintaxis_cubre_algebra

- **mide sobre** la relación `equivalencia`
- **umbral**: `<= 0`
- **por qué ese número**: toda medida aceptada por el álgebra dentro del espacio gramatical cubierto debe ser reversible: imprimirla y releerla produce exactamente el mismo AST JSON y el mismo texto canónico sin pérdida de información
- **qué NO ve**: comprueba medidas sintéticas generadas exhaustivamente sobre combinaciones de la gramática del álgebra (fuentes de y unir encadenados hasta 3 niveles, donde con 6 comparadores, accesores campo/hecho/col, literales true/false/null/números/textos, expresiones lógicas y/o/no anidadas, agrupar con 0 a 2 claves y 1 a 2 agregados, 5 agregados de resumen, 0 a 2 relaciones en requiere y umbrales escalares). NO cubre agrupar con 0 agregados (la sintaxis exige al menos un agregado en el bloque agrupar:), árboles de unir no lineales o con ramas derechas no atómicas, expresiones de profundidad mayor a 5 ni UDFs registradas externamente. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py genera las sondas por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.sintaxis_cubre_algebra",
  "equivalencia",
  "e",
  ["y", ["==", ["campo", "e", "propiedad"], "sintaxis_cubre_algebra"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false], ["!=", ["campo", "e", "error"], ""]]],
  "toda medida aceptada por el álgebra dentro del espacio gramatical cubierto debe ser reversible: imprimirla y releerla produce exactamente el mismo AST JSON y el mismo texto canónico sin pérdida de información",
  "comprueba medidas sintéticas generadas exhaustivamente sobre combinaciones de la gramática del álgebra (fuentes de y unir encadenados hasta 3 niveles, donde con 6 comparadores, accesores campo/hecho/col, literales true/false/null/números/textos, expresiones lógicas y/o/no anidadas, agrupar con 0 a 2 claves y 1 a 2 agregados, 5 agregados de resumen, 0 a 2 relaciones en requiere y umbrales escalares). NO cubre agrupar con 0 agregados (la sintaxis exige al menos un agregado en el bloque agrupar:), árboles de unir no lineales o con ramas derechas no atómicas, expresiones de profundidad mayor a 5 ni UDFs registradas externamente. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py genera las sondas por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.sintaxis_cubre_algebra",
  ["desde", ["de", "equivalencia", "e"], ["donde", ["y", ["==", ["campo", "e", "propiedad"], "sintaxis_cubre_algebra"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false], ["!=", ["campo", "e", "error"], ""]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "toda medida aceptada por el álgebra dentro del espacio gramatical cubierto debe ser reversible: imprimirla y releerla produce exactamente el mismo AST JSON y el mismo texto canónico sin pérdida de información"],
  ["alcance", "comprueba medidas sintéticas generadas exhaustivamente sobre combinaciones de la gramática del álgebra (fuentes de y unir encadenados hasta 3 niveles, donde con 6 comparadores, accesores campo/hecho/col, literales true/false/null/números/textos, expresiones lógicas y/o/no anidadas, agrupar con 0 a 2 claves y 1 a 2 agregados, 5 agregados de resumen, 0 a 2 relaciones en requiere y umbrales escalares). NO cubre agrupar con 0 agregados (la sintaxis exige al menos un agregado en el bloque agrupar:), árboles de unir no lineales o con ramas derechas no atómicas, expresiones de profundidad mayor a 5 ni UDFs registradas externamente. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py genera las sondas por construcción"]
]
```

#### meta.sintaxis_ida_y_vuelta

- **mide sobre** la relación `equivalencia`
- **umbral**: `<= 0`
- **por qué ese número**: la superficie infija es reversible sólo si el JSON de almacenamiento y el texto canónico sobreviven a la ida y vuelta sin cambio
- **qué NO ve**: comprueba las medidas publicadas del catálogo base y perfiles. NO preserva comentarios libres ni demuestra que otra superficie escrita a mano sea la más legible; sólo que la forma canónica impresa por la herramienta vuelve al mismo JSON y al mismo texto. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py comprueba el catálogo por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.sintaxis_ida_y_vuelta",
  "equivalencia",
  "e",
  ["y", ["==", ["campo", "e", "propiedad"], "sintaxis_ida_y_vuelta"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false], ["!=", ["campo", "e", "error"], ""]]],
  "la superficie infija es reversible sólo si el JSON de almacenamiento y el texto canónico sobreviven a la ida y vuelta sin cambio",
  "comprueba las medidas publicadas del catálogo base y perfiles. NO preserva comentarios libres ni demuestra que otra superficie escrita a mano sea la más legible; sólo que la forma canónica impresa por la herramienta vuelve al mismo JSON y al mismo texto. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py comprueba el catálogo por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.sintaxis_ida_y_vuelta",
  ["desde", ["de", "equivalencia", "e"], ["donde", ["y", ["==", ["campo", "e", "propiedad"], "sintaxis_ida_y_vuelta"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false], ["!=", ["campo", "e", "error"], ""]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "la superficie infija es reversible sólo si el JSON de almacenamiento y el texto canónico sobreviven a la ida y vuelta sin cambio"],
  ["alcance", "comprueba las medidas publicadas del catálogo base y perfiles. NO preserva comentarios libres ni demuestra que otra superficie escrita a mano sea la más legible; sólo que la forma canónica impresa por la herramienta vuelve al mismo JSON y al mismo texto. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py comprueba el catálogo por construcción"]
]
```

#### meta.toda_medida_de_ausencia_declara_requiere

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: el patrón `unir` más `agrupar` puede convertir una relación necesaria vacía en cero filas y después en verde; declarar `requiere` hace que la medida falle cerrado antes de agregar sobre nada
- **qué NO ve**: detecta medidas cuya forma canónica contiene `unir` y `agrupar` pero ningún nodo `requiere`. NO demuestra que toda medida con ese patrón sea realmente de ausencia, ni que la relación requerida elegida sea la correcta

Como está escrita:

```json
[
  "medida",
  "meta.toda_medida_de_ausencia_declara_requiere",
  ["desde", ["unir", ["de", "medida", "m"], ["de", "termino", "t"]], ["agrupar", [["medida", ["campo", "m", "id"]]], [["usa_unir", "suma", ["y", ["==", ["campo", "t", "medida"], ["campo", "m", "id"]], ["==", ["campo", "t", "cabeza"], "unir"]]], ["usa_agrupar", "suma", ["y", ["==", ["campo", "t", "medida"], ["campo", "m", "id"]], ["==", ["campo", "t", "cabeza"], "agrupar"]]], ["declara_requiere", "suma", ["y", ["==", ["campo", "t", "medida"], ["campo", "m", "id"]], ["==", ["campo", "t", "cabeza"], "requiere"]]]]], ["donde", ["y", [">", ["col", "usa_unir"], 0], [">", ["col", "usa_agrupar"], 0], ["==", ["col", "declara_requiere"], 0]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "el patrón `unir` más `agrupar` puede convertir una relación necesaria vacía en cero filas y después en verde; declarar `requiere` hace que la medida falle cerrado antes de agregar sobre nada"],
  ["requiere", "termino"],
  ["alcance", "detecta medidas cuya forma canónica contiene `unir` y `agrupar` pero ningún nodo `requiere`. NO demuestra que toda medida con ese patrón sea realmente de ausencia, ni que la relación requerida elegida sea la correcta"]
]
```

#### meta.toda_medida_esta_ejercitada

- **mide sobre** la relación `medida_en_uso`
- **umbral**: `<= 0`
- **por qué ese número**: una medida que ningún caso ni fixture evalúa nunca es decoración: está en el catálogo, se cuenta en el informe, y no puede fallar porque nadie la corre
- **qué NO ve**: cuenta los casos del PROYECTO que la evalúan. NO exige nada de las medidas heredadas del catálogo base —de ésas responde oracle, con su propio corpus— ni ve si esos casos la ponen a prueba de verdad: para eso está la mutación. Si medida_en_uso viene vacía no hay medidas sin ejercitar y verde es correcto; además contiene una fila por medida cargada por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.toda_medida_esta_ejercitada",
  "medida_en_uso",
  "m",
  ["y", ["==", ["campo", "m", "es_heredada"], false], ["==", ["campo", "m", "casos_que_la_evaluan"], 0]],
  "una medida que ningún caso ni fixture evalúa nunca es decoración: está en el catálogo, se cuenta en el informe, y no puede fallar porque nadie la corre",
  "cuenta los casos del PROYECTO que la evalúan. NO exige nada de las medidas heredadas del catálogo base —de ésas responde oracle, con su propio corpus— ni ve si esos casos la ponen a prueba de verdad: para eso está la mutación. Si medida_en_uso viene vacía no hay medidas sin ejercitar y verde es correcto; además contiene una fila por medida cargada por construcción"
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
  ["alcance", "cuenta los casos del PROYECTO que la evalúan. NO exige nada de las medidas heredadas del catálogo base —de ésas responde oracle, con su propio corpus— ni ve si esos casos la ponen a prueba de verdad: para eso está la mutación. Si medida_en_uso viene vacía no hay medidas sin ejercitar y verde es correcto; además contiene una fila por medida cargada por construcción"]
]
```

#### meta.toda_medida_esta_fijada

- **mide sobre** la relación `medida_en_uso`
- **umbral**: `<= 0`
- **por qué ese número**: una medida propia con cero mutantes pasa vacuamente igual que una cuyos mutantes sobreviven: en ambos casos el catálogo la contiene pero la mutación no demuestra que esté fijada
- **qué NO ve**: exige al menos un mutante y ninguno vivo sólo cuando `debe_tener_mutantes` es verdadero. NO vuelve a exigirlos a medidas heredadas —responde su corpus de origen— ni a las evaluadas aparte, y NO ve los mutadores que nadie escribió. Si medida_en_uso viene vacía no hay medidas sin fijar y verde es correcto; además contiene una fila por medida cargada por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.toda_medida_esta_fijada",
  "medida_en_uso",
  "m",
  ["y", ["==", ["campo", "m", "debe_tener_mutantes"], true], ["o", ["==", ["campo", "m", "mutantes"], 0], ["!=", ["campo", "m", "mutantes_vivos"], 0]]],
  "una medida propia con cero mutantes pasa vacuamente igual que una cuyos mutantes sobreviven: en ambos casos el catálogo la contiene pero la mutación no demuestra que esté fijada",
  "exige al menos un mutante y ninguno vivo sólo cuando `debe_tener_mutantes` es verdadero. NO vuelve a exigirlos a medidas heredadas —responde su corpus de origen— ni a las evaluadas aparte, y NO ve los mutadores que nadie escribió. Si medida_en_uso viene vacía no hay medidas sin fijar y verde es correcto; además contiene una fila por medida cargada por construcción"
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
  ["alcance", "exige al menos un mutante y ninguno vivo sólo cuando `debe_tener_mutantes` es verdadero. NO vuelve a exigirlos a medidas heredadas —responde su corpus de origen— ni a las evaluadas aparte, y NO ve los mutadores que nadie escribió. Si medida_en_uso viene vacía no hay medidas sin fijar y verde es correcto; además contiene una fila por medida cargada por construcción"]
]
```

#### meta.toda_medida_filtra_o_agrupa

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: una medida sin `donde` ni `agrupar` mide la relación completa: puede ser válida como conteo bruto, pero en el catálogo de oráculos suele significar que faltó declarar qué hecho ofende
- **qué NO ve**: mira la forma declarada y exige al menos un `donde` o un `agrupar`. NO juzga si el filtro discrimina bien, si el agrupamiento tiene la clave correcta ni si un conteo total fue intencional

Como está escrita:

```json
[
  "medida",
  "meta.toda_medida_filtra_o_agrupa",
  ["desde", ["unir", ["de", "medida", "m"], ["de", "termino", "t"]], ["agrupar", [["medida", ["campo", "m", "id"]]], [["operadores_estructurales", "suma", ["y", ["==", ["campo", "t", "medida"], ["campo", "m", "id"]], ["o", ["==", ["campo", "t", "cabeza"], "donde"], ["==", ["campo", "t", "cabeza"], "agrupar"]]]]]], ["donde", ["==", ["col", "operadores_estructurales"], 0]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una medida sin `donde` ni `agrupar` mide la relación completa: puede ser válida como conteo bruto, pero en el catálogo de oráculos suele significar que faltó declarar qué hecho ofende"],
  ["requiere", "termino"],
  ["alcance", "mira la forma declarada y exige al menos un `donde` o un `agrupar`. NO juzga si el filtro discrimina bien, si el agrupamiento tiene la clave correcta ni si un conteo total fue intencional"]
]
```

#### meta.una_macro_equivale_a_su_expansion

- **mide sobre** la relación `equivalencia`
- **umbral**: `<= 0`
- **por qué ese número**: una macro es azúcar: expande a la forma canónica ANTES de construir la medida, así que el evaluador no debería poder distinguir una de otra. Es la propiedad con más en juego del catálogo — diecinueve de veintidós medidas pasan por una macro, y si alguna expandiera distinto de lo que su autor cree, todo lo escrito con ella mediría otra cosa en silencio y sin que ningún caso lo notara
- **qué NO ve**: compara cada medida escrita por macro contra su expansión canónica, con la evidencia real de sus casos de corpus. NO ve las macros sin ningún caso que las use, ni una expansión que sea consistentemente equivocada: si la macro siempre expande mal de la misma manera, las dos formas coinciden y esta medida calla

Como está escrita:

```json
[
  "ninguno",
  "meta.una_macro_equivale_a_su_expansion",
  "equivalencia",
  "e",
  ["y", ["==", ["campo", "e", "propiedad"], "una_macro_equivale_a_su_expansion"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false]]],
  "una macro es azúcar: expande a la forma canónica ANTES de construir la medida, así que el evaluador no debería poder distinguir una de otra. Es la propiedad con más en juego del catálogo — diecinueve de veintidós medidas pasan por una macro, y si alguna expandiera distinto de lo que su autor cree, todo lo escrito con ella mediría otra cosa en silencio y sin que ningún caso lo notara",
  "compara cada medida escrita por macro contra su expansión canónica, con la evidencia real de sus casos de corpus. NO ve las macros sin ningún caso que las use, ni una expansión que sea consistentemente equivocada: si la macro siempre expande mal de la misma manera, las dos formas coinciden y esta medida calla"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.una_macro_equivale_a_su_expansion",
  ["desde", ["de", "equivalencia", "e"], ["donde", ["y", ["==", ["campo", "e", "propiedad"], "una_macro_equivale_a_su_expansion"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una macro es azúcar: expande a la forma canónica ANTES de construir la medida, así que el evaluador no debería poder distinguir una de otra. Es la propiedad con más en juego del catálogo — diecinueve de veintidós medidas pasan por una macro, y si alguna expandiera distinto de lo que su autor cree, todo lo escrito con ella mediría otra cosa en silencio y sin que ningún caso lo notara"],
  ["alcance", "compara cada medida escrita por macro contra su expansión canónica, con la evidencia real de sus casos de corpus. NO ve las macros sin ningún caso que las use, ni una expansión que sea consistentemente equivocada: si la macro siempre expande mal de la misma manera, las dos formas coinciden y esta medida calla"]
]
```

#### meta.unir_conmuta

- **mide sobre** la relación `equivalencia`
- **umbral**: `<= 0`
- **por qué ese número**: el producto cartesiano no tiene lado: cada fila lleva los dos alias, así que dar vuelta los operandos sólo cambia el orden en que salen las filas, y el orden de una bolsa no es parte del contrato. Si el veredicto, el valor o los testigos cambian al voltear, el operador está haciendo algo que depende de la posición y eso no es un producto
- **qué NO ve**: compara `unir A B` contra `unir B A` sobre una sonda construida y sobre las medidas reales que usan `unir`, con la evidencia de sus casos. NO ve `unir` anidados de más de dos lados ni el costo: dos formas equivalentes pueden materializar el mismo producto con presupuestos muy distintos. Si equivalencia viene vacía no hay fallas de conmutatividad y verde es correcto; además metamorficas.py construye las sondas por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.unir_conmuta",
  "equivalencia",
  "e",
  ["y", ["==", ["campo", "e", "propiedad"], "unir_conmuta"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false]]],
  "el producto cartesiano no tiene lado: cada fila lleva los dos alias, así que dar vuelta los operandos sólo cambia el orden en que salen las filas, y el orden de una bolsa no es parte del contrato. Si el veredicto, el valor o los testigos cambian al voltear, el operador está haciendo algo que depende de la posición y eso no es un producto",
  "compara `unir A B` contra `unir B A` sobre una sonda construida y sobre las medidas reales que usan `unir`, con la evidencia de sus casos. NO ve `unir` anidados de más de dos lados ni el costo: dos formas equivalentes pueden materializar el mismo producto con presupuestos muy distintos. Si equivalencia viene vacía no hay fallas de conmutatividad y verde es correcto; además metamorficas.py construye las sondas por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.unir_conmuta",
  ["desde", ["de", "equivalencia", "e"], ["donde", ["y", ["==", ["campo", "e", "propiedad"], "unir_conmuta"], ["o", ["==", ["campo", "e", "mismo_veredicto"], false], ["==", ["campo", "e", "mismo_valor"], false], ["==", ["campo", "e", "mismos_testigos"], false]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "el producto cartesiano no tiene lado: cada fila lleva los dos alias, así que dar vuelta los operandos sólo cambia el orden en que salen las filas, y el orden de una bolsa no es parte del contrato. Si el veredicto, el valor o los testigos cambian al voltear, el operador está haciendo algo que depende de la posición y eso no es un producto"],
  ["alcance", "compara `unir A B` contra `unir B A` sobre una sonda construida y sobre las medidas reales que usan `unir`, con la evidencia de sus casos. NO ve `unir` anidados de más de dos lados ni el costo: dos formas equivalentes pueden materializar el mismo producto con presupuestos muy distintos. Si equivalencia viene vacía no hay fallas de conmutatividad y verde es correcto; además metamorficas.py construye las sondas por construcción"]
]
```

#### meta.unir_materializa_el_producto

- **mide sobre** la relación `producto`
- **umbral**: `<= 0`
- **por qué ese número**: `unir` es el producto cartesiano y nada más: si sale un número distinto de |izquierda| × |derecha|, o perdió pares o los duplicó. Perderlos esconde ofensas y duplicarlos las cuenta dos veces — y con semántica de bolsas eso altera conteos, sumas y promedios sin ninguna alarma
- **qué NO ve**: compara el tamaño de la salida contra el producto de los dos lados. NO ve si los pares que armó son los correctos ni en qué orden salieron; un `unir` que devuelve la cantidad justa de pares equivocados pasa. Si producto viene vacía no hay productos defectuosos y verde es correcto; además trazar.py garantiza productos trazados por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.unir_materializa_el_producto",
  "producto",
  "u",
  ["!=", ["campo", "u", "salida"], ["por", ["campo", "u", "izquierda"], ["campo", "u", "derecha"]]],
  "`unir` es el producto cartesiano y nada más: si sale un número distinto de |izquierda| × |derecha|, o perdió pares o los duplicó. Perderlos esconde ofensas y duplicarlos las cuenta dos veces — y con semántica de bolsas eso altera conteos, sumas y promedios sin ninguna alarma",
  "compara el tamaño de la salida contra el producto de los dos lados. NO ve si los pares que armó son los correctos ni en qué orden salieron; un `unir` que devuelve la cantidad justa de pares equivocados pasa. Si producto viene vacía no hay productos defectuosos y verde es correcto; además trazar.py garantiza productos trazados por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.unir_materializa_el_producto",
  ["desde", ["de", "producto", "u"], ["donde", ["!=", ["campo", "u", "salida"], ["por", ["campo", "u", "izquierda"], ["campo", "u", "derecha"]]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "`unir` es el producto cartesiano y nada más: si sale un número distinto de |izquierda| × |derecha|, o perdió pares o los duplicó. Perderlos esconde ofensas y duplicarlos las cuenta dos veces — y con semántica de bolsas eso altera conteos, sumas y promedios sin ninguna alarma"],
  ["alcance", "compara el tamaño de la salida contra el producto de los dos lados. NO ve si los pares que armó son los correctos ni en qué orden salieron; un `unir` que devuelve la cantidad justa de pares equivocados pasa. Si producto viene vacía no hay productos defectuosos y verde es correcto; además trazar.py garantiza productos trazados por construcción"]
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
- **qué NO ve**: ve la corrida que lo declara. NO ve otras formas de caché: módulos ya importados en memoria, o un import hecho por otro test antes de la mutación. Si corrida_mutacion viene vacía significa que no hubo corridas con bytecode caliente en la sesión y verde es correcto

Como está escrita:

```json
[
  "ninguno",
  "proceso.arnes_con_bytecode_frio",
  "corrida_mutacion",
  "c",
  ["==", ["campo", "c", "bytecode_frio"], false],
  "CPython invalida el .pyc por (mtime, tamaño): mutar y restaurar dentro del mismo segundo deja a Python corriendo el bytecode mutado sobre el código ya restaurado",
  "ve la corrida que lo declara. NO ve otras formas de caché: módulos ya importados en memoria, o un import hecho por otro test antes de la mutación. Si corrida_mutacion viene vacía significa que no hubo corridas con bytecode caliente en la sesión y verde es correcto"
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
  ["alcance", "ve la corrida que lo declara. NO ve otras formas de caché: módulos ya importados en memoria, o un import hecho por otro test antes de la mutación. Si corrida_mutacion viene vacía significa que no hubo corridas con bytecode caliente en la sesión y verde es correcto"]
]
```

#### proceso.modulo_alcanzable

- **mide sobre** la relación `modulo`
- **umbral**: `<= 0`
- **por qué ese número**: un módulo que no se alcanza desde ninguna entrada no lo va a ejecutar nadie, aunque tenga importadores: un racimo entero puede importarse entre sí y estar muerto
- **qué NO ve**: sigue los imports estáticos desde las entradas declaradas, y descuenta los `__init__.py` vacíos, que son marcadores de paquete. NO ve la carga dinámica —importlib, un plugin, un punto de entrada por configuración— así que un módulo vivo por esa vía sale marcado, y si `alcanzable` viene vacía la medida NO concluye: lo declara en `requiere` y sale SIN EVIDENCIA en vez de verde

Como está escrita:

```json
[
  "medida",
  "proceso.modulo_alcanzable",
  ["desde", ["unir", ["de", "modulo", "m"], ["de", "alcanzable", "r"]], ["agrupar", [["modulo", ["campo", "m", "nombre"]]], [["veces_alcanzado", "suma", ["==", ["campo", "r", "hasta"], ["campo", "m", "nombre"]]], ["es_paquete_vacio", "max", ["campo", "m", "es_paquete_vacio"]]]], ["donde", ["y", ["==", ["col", "veces_alcanzado"], 0], ["==", ["col", "es_paquete_vacio"], false]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un módulo que no se alcanza desde ninguna entrada no lo va a ejecutar nadie, aunque tenga importadores: un racimo entero puede importarse entre sí y estar muerto"],
  ["requiere", "alcanzable"],
  ["alcance", "sigue los imports estáticos desde las entradas declaradas, y descuenta los `__init__.py` vacíos, que son marcadores de paquete. NO ve la carga dinámica —importlib, un plugin, un punto de entrada por configuración— así que un módulo vivo por esa vía sale marcado, y si `alcanzable` viene vacía la medida NO concluye: lo declara en `requiere` y sale SIN EVIDENCIA en vez de verde"]
]
```

#### proceso.modulo_con_consumidor

- **mide sobre** la relación `modulo`
- **umbral**: `<= 0`
- **por qué ese número**: un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite
- **qué NO ve**: cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama

Como está escrita:

```json
[
  "medida",
  "proceso.modulo_con_consumidor",
  ["desde", ["unir", ["de", "modulo", "m"], ["de", "importa", "i"]], ["agrupar", [["modulo", ["campo", "m", "nombre"]]], [["importadores_reales", "suma", ["y", ["==", ["campo", "i", "b"], ["campo", "m", "nombre"]], ["==", ["campo", "i", "es_test"], false]]]]], ["donde", ["==", ["col", "importadores_reales"], 0]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite"],
  ["requiere", "importa"],
  ["alcance", "cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama"]
]
```

#### proceso.ronda_mutacion_concluyente

- **mide sobre** la relación `corrida_mutacion`
- **umbral**: `<= 0`
- **por qué ese número**: sin mutantes no hay material; un timeout, un error del arnés o una línea base roja dejan la mutación inconclusa: ninguno demuestra que un mutante murió
- **qué NO ve**: ve los estados estructurados publicados por cada corrida. NO distingue por sí sola si un código no cero fue una aserción o un error: eso depende del protocolo explícito del runner. Si corrida_mutacion viene vacía significa que no hubo rondas de mutación inconclusas y verde es correcto

Como está escrita:

```json
[
  "ninguno",
  "proceso.ronda_mutacion_concluyente",
  "corrida_mutacion",
  "c",
  ["o", ["<=", ["campo", "c", "mutantes"], 0], ["==", ["campo", "c", "baseline_verde"], false], [">", ["campo", "c", "errores_arnes"], 0], [">", ["campo", "c", "timeouts"], 0]],
  "sin mutantes no hay material; un timeout, un error del arnés o una línea base roja dejan la mutación inconclusa: ninguno demuestra que un mutante murió",
  "ve los estados estructurados publicados por cada corrida. NO distingue por sí sola si un código no cero fue una aserción o un error: eso depende del protocolo explícito del runner. Si corrida_mutacion viene vacía significa que no hubo rondas de mutación inconclusas y verde es correcto"
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
  ["alcance", "ve los estados estructurados publicados por cada corrida. NO distingue por sí sola si un código no cero fue una aserción o un error: eso depende del protocolo explícito del runner. Si corrida_mutacion viene vacía significa que no hubo rondas de mutación inconclusas y verde es correcto"]
]
```

#### proceso.sintaxis_valida_tras_edicion_masiva

- **mide sobre** la relación `archivo`
- **umbral**: `<= 0`
- **por qué ese número**: reescribir N archivos con una expresión regular puede romper la sintaxis, y comprobar que los N siguen parseando es una línea
- **qué NO ve**: ve archivos marcados como no parseables. NO ve el daño que SÍ parsea: una regex puede cambiar el significado de una línea sin romper la sintaxis. Si archivo viene vacía significa que no se detectaron archivos con sintaxis rota tras la edición masiva y verde es correcto

Como está escrita:

```json
[
  "ninguno",
  "proceso.sintaxis_valida_tras_edicion_masiva",
  "archivo",
  "a",
  ["==", ["campo", "a", "sintaxis_valida"], false],
  "reescribir N archivos con una expresión regular puede romper la sintaxis, y comprobar que los N siguen parseando es una línea",
  "ve archivos marcados como no parseables. NO ve el daño que SÍ parsea: una regex puede cambiar el significado de una línea sin romper la sintaxis. Si archivo viene vacía significa que no se detectaron archivos con sintaxis rota tras la edición masiva y verde es correcto"
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
  ["alcance", "ve archivos marcados como no parseables. NO ve el daño que SÍ parsea: una regex puede cambiar el significado de una línea sin romper la sintaxis. Si archivo viene vacía significa que no se detectaron archivos con sintaxis rota tras la edición masiva y verde es correcto"]
]
```

#### proceso.test_con_mutante_que_lo_mata

- **mide sobre** la relación `mutante`
- **umbral**: `<= 0`
- **por qué ese número**: un mutante que sobrevive es un test que no discrimina: pasa con el código roto, así que su verde no significa nada. Cuenta como detección cualquiera de las tres formas en que un caso puede notarlo —invertir el veredicto, cambiar los testigos o cambiar el valor— porque las tres son contrato: los testigos son lo que una persona LEE para actuar, y el valor explica cuánto y no sólo de qué lado cayó. Un rechazo del álgebra tampoco deja al mutante vivo, pero es otra cosa y por eso se cuenta aparte: ahí ningún caso discriminó nada, el mutante ni siquiera llegó a evaluar
- **qué NO ve**: cuenta mutantes que ningún caso observó, de ninguna de las cuatro maneras. NO ve los mutantes que nadie generó: una medida sin ningún mutador aplicable da cero y sale verde. Tampoco distingue un mutante equivalente —imposible de matar— de uno que el corpus todavía no fija; esa diferencia hay que declararla a mano

Como está escrita:

```json
[
  "ninguno",
  "proceso.test_con_mutante_que_lo_mata",
  "mutante",
  "m",
  ["y", ["==", ["campo", "m", "detecciones_conductuales"], 0], ["==", ["campo", "m", "rechazos_del_algebra"], 0]],
  "un mutante que sobrevive es un test que no discrimina: pasa con el código roto, así que su verde no significa nada. Cuenta como detección cualquiera de las tres formas en que un caso puede notarlo —invertir el veredicto, cambiar los testigos o cambiar el valor— porque las tres son contrato: los testigos son lo que una persona LEE para actuar, y el valor explica cuánto y no sólo de qué lado cayó. Un rechazo del álgebra tampoco deja al mutante vivo, pero es otra cosa y por eso se cuenta aparte: ahí ningún caso discriminó nada, el mutante ni siquiera llegó a evaluar",
  "cuenta mutantes que ningún caso observó, de ninguna de las cuatro maneras. NO ve los mutantes que nadie generó: una medida sin ningún mutador aplicable da cero y sale verde. Tampoco distingue un mutante equivalente —imposible de matar— de uno que el corpus todavía no fija; esa diferencia hay que declararla a mano"
]
```

En qué se expande:

```json
[
  "medida",
  "proceso.test_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"], ["donde", ["y", ["==", ["campo", "m", "detecciones_conductuales"], 0], ["==", ["campo", "m", "rechazos_del_algebra"], 0]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina: pasa con el código roto, así que su verde no significa nada. Cuenta como detección cualquiera de las tres formas en que un caso puede notarlo —invertir el veredicto, cambiar los testigos o cambiar el valor— porque las tres son contrato: los testigos son lo que una persona LEE para actuar, y el valor explica cuánto y no sólo de qué lado cayó. Un rechazo del álgebra tampoco deja al mutante vivo, pero es otra cosa y por eso se cuenta aparte: ahí ningún caso discriminó nada, el mutante ni siquiera llegó a evaluar"],
  ["alcance", "cuenta mutantes que ningún caso observó, de ninguna de las cuatro maneras. NO ve los mutantes que nadie generó: una medida sin ningún mutador aplicable da cero y sale verde. Tampoco distingue un mutante equivalente —imposible de matar— de uno que el corpus todavía no fija; esa diferencia hay que declararla a mano"]
]
```

#### proceso.verificacion_vigente

- **mide sobre** la relación `cambio`
- **umbral**: `<= 0`
- **por qué ese número**: un «corrió verde» es una foto con fecha; si después se tocó código vivo la foto es de otro código, y afirmarla es mentir
- **qué NO ve**: cuenta cambios marcados como código vivo. En v0.1 NO compara fechas ni sabe cuál verificación quedó vieja: cualquier cambio vivo la invalida. Hace falta comparar contra el commit de la verificación. Si cambio viene vacía significa que no hubo cambios recientes, por lo que la verificación sigue vigente

Como está escrita:

```json
[
  "ninguno",
  "proceso.verificacion_vigente",
  "cambio",
  "c",
  ["==", ["campo", "c", "es_codigo_vivo"], true],
  "un «corrió verde» es una foto con fecha; si después se tocó código vivo la foto es de otro código, y afirmarla es mentir",
  "cuenta cambios marcados como código vivo. En v0.1 NO compara fechas ni sabe cuál verificación quedó vieja: cualquier cambio vivo la invalida. Hace falta comparar contra el commit de la verificación. Si cambio viene vacía significa que no hubo cambios recientes, por lo que la verificación sigue vigente"
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
  ["alcance", "cuenta cambios marcados como código vivo. En v0.1 NO compara fechas ni sabe cuál verificación quedó vieja: cualquier cambio vivo la invalida. Hace falta comparar contra el commit de la verificación. Si cambio viene vacía significa que no hubo cambios recientes, por lo que la verificación sigue vigente"]
]
```

#### proceso.verificador_sin_falsos_rojos

- **mide sobre** la relación `hallazgo`
- **umbral**: `<= 0`
- **por qué ese número**: un falso rojo enseña a ignorar el verificador, y eso lo vuelve peor que no tener ninguno
- **qué NO ve**: ve hallazgos que YA fueron etiquetados como falsos. NO puede decidir sola si un hallazgo es real: alguien tuvo que mirarlo. Si hallazgo viene vacía significa que el verificador no reportó nada, por lo que el mundo está limpio de falsos rojos

Como está escrita:

```json
[
  "ninguno",
  "proceso.verificador_sin_falsos_rojos",
  "hallazgo",
  "h",
  ["==", ["campo", "h", "era_real"], false],
  "un falso rojo enseña a ignorar el verificador, y eso lo vuelve peor que no tener ninguno",
  "ve hallazgos que YA fueron etiquetados como falsos. NO puede decidir sola si un hallazgo es real: alguien tuvo que mirarlo. Si hallazgo viene vacía significa que el verificador no reportó nada, por lo que el mundo está limpio de falsos rojos"
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
  ["alcance", "ve hallazgos que YA fueron etiquetados como falsos. NO puede decidir sola si un hallazgo es real: alguien tuvo que mirarlo. Si hallazgo viene vacía significa que el verificador no reportó nada, por lo que el mundo está limpio de falsos rojos"]
]
```

### Dominio `simulacion` — mide el mundo

#### simulacion.corrida_reproducible

- **mide sobre** la relación `corrida`
- **umbral**: `<= 0`
- **por qué ese número**: una corrida que no se reproduce no puede ser material de corpus: mañana da otra cosa y el caso deja de significar algo. Sin determinismo la simulación no es evidencia, es una anécdota
- **qué NO ve**: compara dos ejecuciones con la MISMA semilla. NO ve si el resultado depende de algo de afuera —la hora, el orden de un diccionario, un archivo— que hoy casualmente no cambió. Si corrida viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—.

Como está escrita:

```json
[
  "medida",
  "simulacion.corrida_reproducible",
  ["desde", ["de", "corrida", "c"], ["donde", ["==", ["campo", "c", "determinista"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una corrida que no se reproduce no puede ser material de corpus: mañana da otra cosa y el caso deja de significar algo. Sin determinismo la simulación no es evidencia, es una anécdota"],
  ["requiere", "corrida"],
  ["alcance", "compara dos ejecuciones con la MISMA semilla. NO ve si el resultado depende de algo de afuera —la hora, el orden de un diccionario, un archivo— que hoy casualmente no cambió. Si corrida viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—."]
]
```

#### simulacion.la_traza_no_tiene_huecos

- **mide sobre** la relación `evento`
- **umbral**: `<= 0`
- **por qué ese número**: una traza con huecos describe otra corrida que la que ocurrió: si faltan pasos, cualquier cosa que se mida sobre ella habla de lo que se registró y no de lo que pasó
- **qué NO ve**: compara cuántos eventos hay contra el instante final, asumiendo que el tiempo arranca en cero y avanza de a uno. NO ve trazas donde varios eventos comparten instante, ni sabe si el que falta es importante. Si evento viene vacío la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—.

Como está escrita:

```json
[
  "medida",
  "simulacion.la_traza_no_tiene_huecos",
  ["desde", ["de", "evento", "e"], ["agrupar", [["corrida", ["campo", "e", "corrida"]]], [["registrados", "contar", 1], ["ultimo", "max", ["campo", "e", "t"]]]], ["donde", ["!=", ["col", "registrados"], ["mas", ["col", "ultimo"], 1]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una traza con huecos describe otra corrida que la que ocurrió: si faltan pasos, cualquier cosa que se mida sobre ella habla de lo que se registró y no de lo que pasó"],
  ["requiere", "evento"],
  ["alcance", "compara cuántos eventos hay contra el instante final, asumiendo que el tiempo arranca en cero y avanza de a uno. NO ve trazas donde varios eventos comparten instante, ni sabe si el que falta es importante. Si evento viene vacío la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—."]
]
```

#### simulacion.no_se_agoto_el_presupuesto

- **mide sobre** la relación `corrida`
- **umbral**: `<= 0`
- **por qué ese número**: una corrida que se quedó sin pasos no observó el sistema: observó el presupuesto. Cualquier conclusión que salga de ahí habla de la paciencia del que simuló, no de lo simulado
- **qué NO ve**: ve la clasificación producida por el contrato de terminación. NO ve si el presupuesto era razonable, ni si una corrida que terminó a tiempo lo hizo por el motivo correcto. Si corrida viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—.

Como está escrita:

```json
[
  "medida",
  "simulacion.no_se_agoto_el_presupuesto",
  ["desde", ["de", "corrida", "c"], ["donde", ["==", ["campo", "c", "presupuesto_agotado"], true]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una corrida que se quedó sin pasos no observó el sistema: observó el presupuesto. Cualquier conclusión que salga de ahí habla de la paciencia del que simuló, no de lo simulado"],
  ["requiere", "corrida"],
  ["alcance", "ve la clasificación producida por el contrato de terminación. NO ve si el presupuesto era razonable, ni si una corrida que terminó a tiempo lo hizo por el motivo correcto. Si corrida viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—."]
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
| falso_verde | 62 |
| verde_correcto | 32 |
| deuda_de_diseño | 2 |
| falso_rojo | 2 |
| medida_correcta_conclusion_errada | 1 |

| Cómo se detectó | Cuántos |
|---|---|
| mutacion | 48 |
| observacion | 32 |
| persona | 12 |
| accidente | 4 |
| herramienta_ajena | 3 |

**Cada caso registra cómo se detectó.** Una suite verde y una mutación, una persona o
un accidente son señales distintas; mezclarlas borraría justo la evidencia que el
corpus intenta conservar.

### 049-donde-agrego-filas

**Un `donde` que devolvió más filas de las que recibió**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.donde_nunca_agrega_filas`
- de dónde salió: Segtem/oracle · c81a87c

**Qué pasó.** La traza de la evaluación registró un `donde` con 3 filas de entrada y 4 de salida. Un filtro que agrega filas no filtró: los testigos que publica la medida no son los que sobrevivieron al predicado, así que el informe nombra filas que nunca se demostró que ofendieran.

**Qué se aprendió.** Es la primera propiedad metamórfica de PLAN-LENGUAJE (e.1) enunciada como medida en vez de como test en Python. La diferencia no es qué se verifica sino dónde vive la regla: como medida entra a la mutación, al corpus y al inventario de puntos ciegos, y sale del núcleo.

La evidencia, como relaciones:

```json
{
  "paso": [{"t": 0, "operador": "de", "filas_antes": 0, "filas_despues": 3}, {"t": 1, "operador": "donde", "filas_antes": 3, "filas_despues": 4}]
}
```

### 050-donde-filtra-como-debe

**Un `donde` que reduce, y un `de` que puebla**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.donde_nunca_agrega_filas`
- de dónde salió: Segtem/oracle · c81a87c

**Qué pasó.** La tubería normal: `de` puebla desde cero —y por eso crece, que es correcto y la medida no lo mira— y cada `donde` reduce o deja igual. Un `donde` que no descarta nada tampoco es una falla: la evidencia podía ofender entera.

**Qué se aprendió.** Sin esta polaridad, quitar el filtro de operador o negarlo sobrevivían: la medida se pondría roja en cada `de`, que siempre agrega filas. La propiedad es sobre `donde`, no sobre la tubería.

La evidencia, como relaciones:

```json
{
  "paso": [{"t": 0, "operador": "de", "filas_antes": 0, "filas_despues": 3}, {"t": 1, "operador": "donde", "filas_antes": 3, "filas_despues": 2}, {"t": 2, "operador": "donde", "filas_antes": 2, "filas_despues": 2}]
}
```

### 051-agrupar-invento-un-grupo

**`agrupar` devolvió más grupos que filas de entrada**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.agrupar_no_agranda_la_relacion`
- de dónde salió: Segtem/oracle · c81a87c

**Qué pasó.** Cuatro filas entraron a `agrupar` y salieron cinco grupos. Un grupo es un resumen de filas: no puede haber más grupos que filas que los originen. Si sale agrandando, hay al menos un grupo que ninguna fila sostiene, y todo agregado calculado sobre él es un número sin evidencia detrás.

**Qué se aprendió.** El caso 043 mostró que un agregado sobre cero filas es indistinguible de uno que dio cero. Éste es el otro extremo del mismo problema: un agregado sobre un grupo inventado tampoco se distingue de uno legítimo mirando sólo el número.

La evidencia, como relaciones:

```json
{
  "paso": [{"t": 0, "operador": "unir", "filas_antes": 0, "filas_despues": 4}, {"t": 1, "operador": "agrupar", "filas_antes": 4, "filas_despues": 5}]
}
```

### 052-agrupar-colapsa-como-debe

**`agrupar` colapsa filas en grupos**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.agrupar_no_agranda_la_relacion`
- de dónde salió: Segtem/oracle · c81a87c

**Qué pasó.** Seis filas colapsan en dos grupos, y un `agrupar` sobre dos filas ya agrupadas devuelve dos: colapsar a la misma cantidad es legítimo cuando cada fila es su propio grupo.

**Qué se aprendió.** La igualdad tiene que pasar. Un umbral que exigiera reducción estricta daría falso rojo cada vez que las claves de agrupación son únicas, que es un caso común y correcto.

La evidencia, como relaciones:

```json
{
  "paso": [{"t": 0, "operador": "unir", "filas_antes": 0, "filas_despues": 6}, {"t": 1, "operador": "agrupar", "filas_antes": 6, "filas_despues": 2}, {"t": 2, "operador": "agrupar", "filas_antes": 2, "filas_despues": 2}]
}
```

### 053-unir-perdio-un-par

**`unir` devolvió menos pares que el producto**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.unir_materializa_el_producto`
- de dónde salió: Segtem/oracle · c81a87c

**Qué pasó.** Tres filas por cuatro son doce pares, y `unir` devolvió once. Perder un par esconde una ofensa: si la fila que faltaba era la que disparaba el predicado, la medida sale verde sin haber mirado el mundo entero.

**Qué se aprendió.** Este defecto se escapó de la primera versión de la instrumentación, y por un motivo que vale más que el defecto: el hecho se anotaba DENTRO de `_unir`, leyendo su propia variable antes del `return`. Un sensor que se lee a sí mismo no audita la frontera — cualquier cosa que pase entre esa línea y el punto de uso queda fuera de la medición. Se movió al punto donde el operador devuelve.

La evidencia, como relaciones:

```json
{
  "producto": [{"izquierda": 3, "derecha": 4, "salida": 11}]
}
```

### 054-unir-materializa-el-producto

**`unir` devuelve exactamente el producto**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.unir_materializa_el_producto`
- de dónde salió: Segtem/oracle · c81a87c

**Qué pasó.** El producto completo, y los dos casos borde que importan: un lado vacío da cero pares. Es exactamente el mecanismo del falso verde de la ausencia (caso 043) visto desde el álgebra, y acá es el comportamiento correcto — lo que estaba mal era la medida que leía ese cero como un mundo en orden.

**Qué se aprendió.** Los bordes con cero tienen que salir verdes acá y rojos allá, y no es contradicción: `unir` hace bien su trabajo devolviendo cero pares, y la medida de ausencia hacía mal el suyo concluyendo desde esa nada. Por eso el arreglo fue `requiere` y no tocar `unir`.

La evidencia, como relaciones:

```json
{
  "producto": [{"izquierda": 3, "derecha": 4, "salida": 12}, {"izquierda": 2, "derecha": 0, "salida": 0}, {"izquierda": 0, "derecha": 5, "salida": 0}]
}
```

### 055-logico-cortocircuito

**Un `y` que evaluó un solo operando de dos**

- etiqueta: `falso_verde` · se detectó por: `herramienta_ajena`
- medida que lo atrapa: `meta.los_logicos_evaluan_todos_sus_operandos`
- de dónde salió: Segtem/oracle · c81a87c

**Qué pasó.** `all()`/`any()` sobre generadores cortan apenas el resultado está decidido, así que un campo mal escrito dentro de un `y` nunca se evaluaba y devolvía un False silencioso. La especificación dice en §3 que comparar contra un campo ausente levanta error justamente porque un False silencioso lo convierte en un verde.

**Qué se aprendió.** El defecto lo encontró el diferencial: dos de tres implementaciones independientes, escritas sólo desde la especificación, evaluaban todos los operandos. Y era peor que un verde fijo: dependía de los datos, así que la misma medida rota levantaba el error con una evidencia y lo escondía con otra.

La evidencia, como relaciones:

```json
{
  "nodo": [{"cabeza": "y", "declarados": 2, "evaluados": 1}, {"cabeza": "o", "declarados": 2, "evaluados": 1}]
}
```

### 056-logico-evalua-todo

**Los lógicos evalúan todos sus operandos**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.los_logicos_evaluan_todos_sus_operandos`
- de dónde salió: Segtem/oracle · c81a87c

**Qué pasó.** Cada `y` y cada `o` evaluó tantos operandos como declara su AST, sin importar que el primero ya decidiera el resultado.

**Qué se aprendió.** Se paga evaluando de más en predicados grandes, y el presupuesto de §9 ya acota esa amplificación. Una medida que se apoya en el cortocircuito para no romperse está rota: lo que el cortocircuito le ahorraba era el error.

La evidencia, como relaciones:

```json
{
  "nodo": [{"cabeza": "y", "declarados": 2, "evaluados": 2}, {"cabeza": "o", "declarados": 3, "evaluados": 3}, {"cabeza": "y", "declarados": 1, "evaluados": 1}]
}
```

### 057-un-solo-cortocircuito

**Un único `y` cortocircuitado, pegado al umbral**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.los_logicos_evaluan_todos_sus_operandos`
- de dónde salió: Segtem/oracle · c81a87c

**Qué pasó.** Una sola evaluación en toda la corrida dejó un operando sin evaluar: dos declarados, uno evaluado. El resto de los nodos lógicos está sano. Es el borde exacto del umbral —un ofensor contra `<= 0`— y es la forma en que este defecto aparece en la realidad: no como una implementación que cortocircuita siempre, sino como una expresión donde los datos hicieron que el primer operando decidiera.

**Qué se aprendió.** El umbral es `<= 0` y no admite tolerancia, porque un solo operando sin evaluar es un error sin levantar. Sin este caso, aflojar el umbral a `<= 1` sobrevivía —la mutación lo reportó— y con esa escritura la medida dejaría pasar exactamente el caso que motivó escribirla. Un mutante de umbral sólo lo mata un caso pegado al límite: la polaridad no alcanza, hace falta el borde.

La evidencia, como relaciones:

```json
{
  "nodo": [{"cabeza": "y", "declarados": 2, "evaluados": 1}, {"cabeza": "y", "declarados": 2, "evaluados": 2}, {"cabeza": "o", "declarados": 3, "evaluados": 3}]
}
```

### 061-ausencia-sin-requiere

**Una medida de ausencia usa `unir` y `agrupar` sin precondición**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.toda_medida_de_ausencia_declara_requiere`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La forma de la medida contiene el patrón que puede convertir una relación necesaria vacía en cero filas, pero no declara `requiere`. Si el sensor de esa relación falla y devuelve una lista vacía, la medida puede concluir verde desde la ausencia de evidencia.

**Qué se aprendió.** El defecto no está en `unir` ni en `agrupar`: esos operadores hacen exactamente lo declarado. La medida que usa ese patrón debe declarar qué relación necesita para no agregar sobre nada.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.ausencia_sin_requiere"}]
  "termino": [{"medida": "dominio.ausencia_sin_requiere", "cabeza": "unir"}, {"medida": "dominio.ausencia_sin_requiere", "cabeza": "agrupar"}, {"medida": "dominio.ausencia_sin_requiere", "cabeza": "donde"}]
}
```

### 062-ausencia-cubierta-o-no-aplica

**El patrón de ausencia pasa cuando declara `requiere`, y los patrones parciales no cuentan**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.toda_medida_de_ausencia_declara_requiere`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Una medida con `unir` y `agrupar` trae el nodo `requiere`; otra usa sólo `unir`; otra usa sólo `agrupar`. Ninguna debe marcarse como ausencia sin precondición.

**Qué se aprendió.** La regla es deliberadamente estrecha: no todo `unir` pide precondición, y no todo `agrupar` expresa ausencia. El rojo nace sólo cuando aparecen los dos y falta el nodo `requiere`.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.ausencia_cubierta"}, {"id": "dominio.solo_union"}, {"id": "dominio.solo_agrupa"}]
  "termino": [{"medida": "dominio.ausencia_cubierta", "cabeza": "unir"}, {"medida": "dominio.ausencia_cubierta", "cabeza": "agrupar"}, {"medida": "dominio.ausencia_cubierta", "cabeza": "requiere"}, {"medida": "dominio.solo_union", "cabeza": "unir"}, {"medida": "dominio.solo_union", "cabeza": "donde"}, {"medida": "dominio.solo_agrupa", "cabeza": "agrupar"}]
}
```

### 063-ausencia-sin-terminos-no-concluye

**Sin relación `termino`, la regla de ausencia no puede concluir**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.toda_medida_de_ausencia_declara_requiere`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** El sensor estructural no entregó ningún término. Una regla que mide la forma del catálogo no debe ponerse verde cuando no recibió la forma que necesita mirar.

**Qué se aprendió.** Este caso fija el `requiere` de la propia medida meta: quitarlo vuelve al falso verde sobre cero filas.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.sin_estructura"}]
  "termino": []
}
```

### 064-medida-sin-filtro-ni-grupo

**Una medida cuenta la relación entera**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.toda_medida_filtra_o_agrupa`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La forma estructural de la medida no contiene `donde` ni `agrupar`. Está contando todo lo que entra, sin declarar qué condición separa una ofensa de una fila normal.

**Qué se aprendió.** La forma mínima de una medida que señala defectos necesita un filtro o un agrupamiento que fabrique la condición observable.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.conteo_bruto"}]
  "termino": [{"medida": "dominio.conteo_bruto", "cabeza": "de"}, {"medida": "dominio.conteo_bruto", "cabeza": "resumen"}, {"medida": "dominio.conteo_bruto", "cabeza": "umbral"}]
}
```

### 065-medida-filtra-o-agrupa

**`donde` y `agrupar` bastan por separado como operadores estructurales**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.toda_medida_filtra_o_agrupa`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Una medida filtra con `donde` y otra resume con `agrupar`. La regla no exige ambos operadores: cualquiera de los dos demuestra que la medida no se limita a contar la entrada completa.

**Qué se aprendió.** El verde cubre las dos polaridades internas de la regla: un filtro directo y un agrupamiento. Si la disyunción se endurece por error, este caso se pone rojo.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.filtra"}, {"id": "dominio.agrupa"}]
  "termino": [{"medida": "dominio.filtra", "cabeza": "de"}, {"medida": "dominio.filtra", "cabeza": "donde"}, {"medida": "dominio.agrupa", "cabeza": "de"}, {"medida": "dominio.agrupa", "cabeza": "agrupar"}]
}
```

### 066-filtro-sin-terminos-no-concluye

**La regla de filtro o agrupamiento no concluye sin `termino`**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.toda_medida_filtra_o_agrupa`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La evidencia trae medidas, pero la relación que describe su forma viene vacía. Una medida sobre estructura no puede tomar ese vacío como prueba de que todo está en orden.

**Qué se aprendió.** Este caso mata el mutante que quita `requiere`: sin la precondición, la agregación sobre cero filas saldría verde.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.sin_terminos"}]
  "termino": []
}
```

### 067-umbral-de-igualdad

**Un umbral final usa igualdad exacta**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.ningun_umbral_de_igualdad`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La cabecera estructural de la medida declara `comparador` igual a `==`. Ese umbral no deja borde operativo para fijar la medida con mutación de umbral.

**Qué se aprendió.** La prohibición no depende del valor concreto del límite: el problema es el operador final de umbral.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.igualdad_exacta", "comparador": "=="}]
}
```

### 068-umbral-de-orden

**Los umbrales de orden no son igualdad exacta**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.ningun_umbral_de_igualdad`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Dos medidas usan comparadores de orden. La regla debe dejarlas pasar y no confundir una cota con una igualdad exacta.

**Qué se aprendió.** El caso verde mata la mutación que quita el filtro: contar la relación completa ya no sería cero.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.cota_superior", "comparador": "<="}, {"id": "dominio.cota_inferior", "comparador": ">"}]
}
```

### 069-filtro-no-toma-terminos-ajenos

**Una medida sin filtro no se salva por el `donde` de otra**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.toda_medida_filtra_o_agrupa`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** El catálogo trae una medida que no filtra ni agrupa y otra que sí filtra. La regla debe señalar la primera; no puede contar el operador estructural de una medida vecina como si perteneciera a la ofensa.

**Qué se aprendió.** El vínculo entre `medida` y `termino` es parte de la regla, no un detalle de eficiencia. Si se invierte, el valor puede seguir siendo rojo pero el testigo cambia de medida.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.conteo_bruto"}, {"id": "dominio.filtra"}]
  "termino": [{"medida": "dominio.conteo_bruto", "cabeza": "de"}, {"medida": "dominio.conteo_bruto", "cabeza": "resumen"}, {"medida": "dominio.filtra", "cabeza": "de"}, {"medida": "dominio.filtra", "cabeza": "donde"}]
}
```

### 100-donde-no-compone

**Donde no compone**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.donde_compone`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Filtrar por P y después por Q dejó filas distintas que filtrar una vez por «P y Q». El veredicto y el valor coincidieron y los testigos no: las dos formas cuentan lo mismo señalando filas distintas, así que una persona que actúe sobre el informe va a mirar el lugar equivocado.

**Qué se aprendió.** Por eso la propiedad exige las tres coincidencias y no sólo el número. Las filas que sobreviven al último `donde` SON los testigos —no se declaran aparte— y un `y` que ignora su segundo operando produce exactamente este síntoma: mismo conteo, otras filas.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "donde_compone", "caso": "c", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}, {"propiedad": "unir_conmuta", "caso": "c", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 101-donde-compone-bien

**Donde compone bien**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.donde_compone`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Las dos formas del filtro coinciden en veredicto, valor y testigos. La segunda fila es de otra propiedad y no coincide en testigos: está para fijar que el filtro por `propiedad` filtre de verdad.

**Qué se aprendió.** Sin esta polaridad, quitar el filtro por `propiedad` sobrevivía: la medida se pondría roja por una equivalencia que no es la suya. Cada propiedad juzga sólo sus propios hechos.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "donde_compone", "caso": "c", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "c", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 102-unir-no-conmuta

**Unir no conmuta**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.unir_conmuta`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Voltear los operandos de `unir` cambió el valor y los testigos. El producto cartesiano no tiene lado: si el resultado depende de cuál operando va primero, el operador está haciendo algo posicional y eso no es un producto.

**Qué se aprendió.** El defecto que produce esto es asimétrico —recortar el resultado según el tamaño del lado izquierdo—, y por eso un mutante simétrico no lo revela: quitarle la misma fila a las dos formas las deja coincidiendo. Una propiedad de conmutatividad sólo la rompe un defecto que distinga los lados.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "unir_conmuta", "caso": "c", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": false, "mismos_testigos": false}, {"propiedad": "donde_compone", "caso": "c", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 103-unir-conmuta-bien

**Unir conmuta bien**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.unir_conmuta`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Las dos formas coinciden, tanto sobre la sonda construida como sobre una medida real del catálogo con la evidencia de su caso.

**Qué se aprendió.** Los dos orígenes conviven en la misma relación y el hecho lo declara. Importa: una propiedad comprobada sólo donde el catálogo casualmente la ejercita mide la coincidencia, no la propiedad.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "unir_conmuta", "caso": "c", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "unir_conmuta", "caso": "real", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 104-agrupar-sin-claves-difiere

**Agrupar sin claves difiere**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.agrupar_sin_claves_es_el_resumen_global`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Agrupar sin claves y agregar sobre todo dieron números distintos. Sin claves hay un solo grupo, así que los dos caminos tienen que llegar al mismo valor; si no, `agrupar` pierde o inventa filas al colapsar y todo agregado calculado sobre ese grupo es un número sin evidencia detrás.

**Qué se aprendió.** El caso trae `mismos_testigos` en falso además del valor, y eso NO es lo que la medida juzga: los testigos difieren siempre en esta propiedad, porque un grupo no es un hecho. La medida mira veredicto y valor, y este caso la pone roja por el valor.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "c", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": false, "mismos_testigos": false}]
}
```

### 105-agrupar-sin-claves-coincide

**Agrupar sin claves coincide**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.agrupar_sin_claves_es_el_resumen_global`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Las dos formas coinciden en veredicto y valor, y NO coinciden en testigos. Eso es lo correcto y es la polaridad que lo fija: `agrupar` consume los hechos, así que la forma agrupada señala un grupo y la directa señala las filas originales.

**Qué se aprendió.** Es el caso que impide endurecer la medida por prolijidad. Si alguien agregara `mismos_testigos` al predicado —para que las cuatro propiedades se parezcan— esta medida se pondría roja con el álgebra sana, y un falso rojo enseña a ignorar el verificador.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "c", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}, {"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "otro-agregado", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 106-macro-expande-distinto

**Macro expande distinto**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.una_macro_equivale_a_su_expansion`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Una medida escrita por macro dio un veredicto distinto que su expansión canónica. Es la falla con más alcance posible del catálogo: diecinueve de veintidós medidas pasan por una macro, así que una expansión equivocada haría que casi todo el catálogo midiera otra cosa, en silencio.

**Qué se aprendió.** Ninguna otra verificación lo vería. La mutación muta la forma canónica —mutar la expansión llega más lejos que mutar la invocación— así que una macro que expande mal produce mutantes de algo que no es lo que el autor escribió, y todos mueren igual.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "una_macro_equivale_a_su_expansion", "caso": "un-caso-real", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": false, "mismos_testigos": true}]
}
```

### 107-macro-equivale

**Macro equivale**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.una_macro_equivale_a_su_expansion`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Dos medidas escritas por macro coinciden con su expansión canónica en veredicto, valor y testigos, sobre la evidencia real de sus casos.

**Qué se aprendió.** El alcance de esta propiedad tiene un hueco que conviene tener presente: si una macro expandiera SIEMPRE mal de la misma manera, las dos formas coincidirían igual y esta medida callaría. Comprueba que las dos formas sean la misma, no que la forma sea la correcta.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "una_macro_equivale_a_su_expansion", "caso": "uno", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "una_macro_equivale_a_su_expansion", "caso": "otro", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 108-donde-compone-un-campo-por-vez

**donde_compone: cada campo del contrato falla por separado**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.donde_compone`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Tres equivalencias de la misma propiedad, cada una fallando en UN solo campo del contrato: una difiere sólo en el veredicto, otra sólo en el valor, otra sólo en los testigos. Las tres tienen que contarse como ofensa, y por separado.

**Qué se aprendió.** La mutación pidió este caso y explica por qué: con un predicado que es un `o` de tres comparaciones sobre tres campos distintos, sustituir un campo por otro pasa inadvertido mientras todos los casos tengan los tres campos con el mismo valor. Diecisiete mutantes sobrevivían por eso. Aislar un campo por fila es lo que vuelve distinguibles a los tres, y es el mismo patrón que el caso `057`: la polaridad no alcanza cuando lo que hay que fijar es un borde.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "donde_compone", "caso": "solo-veredicto", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "donde_compone", "caso": "solo-valor", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": false, "mismos_testigos": true}, {"propiedad": "donde_compone", "caso": "solo-testigos", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 109-unir-conmuta-un-campo-por-vez

**unir_conmuta: cada campo del contrato falla por separado**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.unir_conmuta`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Tres equivalencias de la misma propiedad, cada una fallando en UN solo campo del contrato: una difiere sólo en el veredicto, otra sólo en el valor, otra sólo en los testigos. Las tres tienen que contarse como ofensa, y por separado.

**Qué se aprendió.** La mutación pidió este caso y explica por qué: con un predicado que es un `o` de tres comparaciones sobre tres campos distintos, sustituir un campo por otro pasa inadvertido mientras todos los casos tengan los tres campos con el mismo valor. Diecisiete mutantes sobrevivían por eso. Aislar un campo por fila es lo que vuelve distinguibles a los tres, y es el mismo patrón que el caso `057`: la polaridad no alcanza cuando lo que hay que fijar es un borde.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "unir_conmuta", "caso": "solo-veredicto", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "unir_conmuta", "caso": "solo-valor", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": false, "mismos_testigos": true}, {"propiedad": "unir_conmuta", "caso": "solo-testigos", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 110-agrupar-sin-claves-es-el-resumen-global-un-campo-por-vez

**agrupar_sin_claves_es_el_resumen_global: cada campo del contrato falla por separado**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.agrupar_sin_claves_es_el_resumen_global`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Tres equivalencias de la misma propiedad, cada una fallando en UN solo campo del contrato: una difiere sólo en el veredicto, otra sólo en el valor, otra sólo en los testigos. Las tres tienen que contarse como ofensa, y por separado.

**Qué se aprendió.** La mutación pidió este caso y explica por qué: con un predicado que es un `o` de tres comparaciones sobre tres campos distintos, sustituir un campo por otro pasa inadvertido mientras todos los casos tengan los tres campos con el mismo valor. Diecisiete mutantes sobrevivían por eso. Aislar un campo por fila es lo que vuelve distinguibles a los tres, y es el mismo patrón que el caso `057`: la polaridad no alcanza cuando lo que hay que fijar es un borde.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "solo-veredicto", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "solo-valor", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": false, "mismos_testigos": true}, {"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "solo-testigos", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 111-una-macro-equivale-a-su-expansion-un-campo-por-vez

**una_macro_equivale_a_su_expansion: cada campo del contrato falla por separado**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.una_macro_equivale_a_su_expansion`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Tres equivalencias de la misma propiedad, cada una fallando en UN solo campo del contrato: una difiere sólo en el veredicto, otra sólo en el valor, otra sólo en los testigos. Las tres tienen que contarse como ofensa, y por separado.

**Qué se aprendió.** La mutación pidió este caso y explica por qué: con un predicado que es un `o` de tres comparaciones sobre tres campos distintos, sustituir un campo por otro pasa inadvertido mientras todos los casos tengan los tres campos con el mismo valor. Diecisiete mutantes sobrevivían por eso. Aislar un campo por fila es lo que vuelve distinguibles a los tres, y es el mismo patrón que el caso `057`: la polaridad no alcanza cuando lo que hay que fijar es un borde.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "una_macro_equivale_a_su_expansion", "caso": "solo-veredicto", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "una_macro_equivale_a_su_expansion", "caso": "solo-valor", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": false, "mismos_testigos": true}, {"propiedad": "una_macro_equivale_a_su_expansion", "caso": "solo-testigos", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 120-sintaxis-no-vuelve-igual

**Sintaxis no vuelve igual**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.sintaxis_ida_y_vuelta`
- de dónde salió: Segtem/oracle · b250e6c

**Qué pasó.** Una medida convertida a la superficie infija y de vuelta a JSON dejó de coincidir en testigos. El texto se lee lindo y la medida ya no es la misma: la superficie está perdiendo información en el camino.

**Qué se aprendió.** Es la propiedad que sostiene toda la apuesta de la sintaxis. El JSON canónico es el almacenamiento —de él dependen la mutación, las macros, la reificación y las huellas de los fixtures— y una superficie que no vuelva exacta no es una forma de escribir lo mismo: es otra cosa parecida. Por eso la ida y vuelta se comprueba sobre TODO el catálogo y no sobre un ejemplo.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_ida_y_vuelta", "caso": "una-medida-con-agrupar", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}, {"propiedad": "sintaxis_ida_y_vuelta", "caso": "c", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 121-sintaxis-vuelve-exacta

**Sintaxis vuelve exacta**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.sintaxis_ida_y_vuelta`
- de dónde salió: Segtem/oracle · b250e6c

**Qué pasó.** Tres medidas vuelven exactas: una canónica, una escrita por macro y una con `requiere`. Las tres formas de almacenamiento sobreviven la ida y vuelta sin cambio.

**Qué se aprendió.** Las tres están a propósito. Una superficie que sólo conserve la forma canónica serviría para 7 de las 29 medidas: el resto se escribe con la macro `ninguno`, y `requiere` es un nodo opcional que un lector distraído puede tragarse sin avisar.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_ida_y_vuelta", "caso": "canonica", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_ida_y_vuelta", "caso": "por-macro", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_ida_y_vuelta", "caso": "con-requiere", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 122-sintaxis-revienta-al-leer

**Sintaxis revienta al leer**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.sintaxis_ida_y_vuelta`
- de dónde salió: Segtem/oracle · b250e6c

**Qué pasó.** La conversión no falló en comparar: falló en leer. El campo `error` trae el tipo de excepción y los tres campos de coincidencia vienen en falso porque no hubo nada que comparar.

**Qué se aprendió.** Sin este caso, sustituir la comparación de `error` por cualquier otro campo pasaba inadvertido: es la cuarta rama del predicado y la única que distingue «volvió distinto» de «no volvió». Un lector que revienta y un lector que devuelve otra cosa son dos defectos, y el informe tiene que poder decir cuál de los dos fue.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_ida_y_vuelta", "caso": "no-parsea", "origen": "catalogo", "evaluo": true, "error": "ErrorDeSintaxis", "mismo_veredicto": false, "mismo_valor": false, "mismos_testigos": false}]
}
```

### 123-sintaxis-un-campo-por-vez

**Cada campo del contrato de la ida y vuelta falla por separado**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.sintaxis_ida_y_vuelta`
- de dónde salió: Segtem/oracle · b250e6c

**Qué pasó.** Tres conversiones fallando en UN solo campo cada una: una difiere sólo en el veredicto, otra sólo en el valor, otra sólo en los testigos. Las tres son ofensas y hay que contarlas por separado.

**Qué se aprendió.** Cuarta vez que la mutación pide este caso, y ya es un patrón del proyecto: cuando un predicado es un `o` de comparaciones sobre campos distintos, sustituir un campo por otro pasa inadvertido mientras todos los casos traigan los campos con el mismo valor. La polaridad no alcanza; hay que aislar cada rama. Lo mismo pasó en `057`, en `060` y en `108`–`111`.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_ida_y_vuelta", "caso": "solo-veredicto", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_ida_y_vuelta", "caso": "solo-valor", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": false, "mismos_testigos": true}, {"propiedad": "sintaxis_ida_y_vuelta", "caso": "solo-testigos", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 124-sintaxis-cubre-algebra-no-vuelve-igual

**Sintaxis generada no vuelve igual**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.sintaxis_cubre_algebra`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Una medida generada a partir de la gramática del álgebra difiere en su AST al volver de la superficie infija: la superficie está perdiendo información o alterando la estructura del operador.

**Qué se aprendió.** La completitud del metalenguaje exige que cualquier construcción válida para el evaluador sea reversible en la sintaxis infija. Si una construcción válida muta o falla al imprimirse, la superficie no es un reflejo fiel del álgebra sino un dialecto restringido.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_cubre_algebra", "caso": "meta_gen.expr_profunda", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_cubre_algebra", "caso": "meta_gen.f_de_req0_umb_lte_0", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_ida_y_vuelta", "caso": "catalogo_ok", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 125-sintaxis-cubre-algebra-vuelve-exacta

**Sintaxis generada vuelve exacta**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.sintaxis_cubre_algebra`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Tres medidas generadas por gramática (una con unir encadenado, una con agrupar multiclave y una con predicados anidados) sobreviven la ida y vuelta canónica sin perder veredicto ni valor.

**Qué se aprendió.** Comprobar la reversibilidad sobre medidas sintéticas derivadas de la gramática extiende la garantía de la superficie más allá de las medidas escritas en el catálogo base.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_cubre_algebra", "caso": "meta_gen.f_unir3_req2_umb_lte_0", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_cubre_algebra", "caso": "meta_gen.grp_c2_a2_max_min", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_cubre_algebra", "caso": "meta_gen.expr_profunda_5", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_ida_y_vuelta", "caso": "catalogo_ok", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 126-sintaxis-cubre-algebra-un-campo-por-vez

**Cada campo del contrato de sintaxis_cubre_algebra falla por separado**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.sintaxis_cubre_algebra`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Cuatro equivalencias de la propiedad sintaxis_cubre_algebra fallando en UN solo campo del contrato: veredicto, valor, testigos o error.

**Qué se aprendió.** Aislar cada campo del contrato en filas separadas es indispensable para matar los mutantes de sustitución en disyunciones lógicas.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_cubre_algebra", "caso": "solo-veredicto", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_cubre_algebra", "caso": "solo-valor", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": false, "mismos_testigos": true}, {"propiedad": "sintaxis_cubre_algebra", "caso": "solo-testigos", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}, {"propiedad": "sintaxis_cubre_algebra", "caso": "solo-error", "origen": "construido", "evaluo": false, "error": "ErrorSintaxis", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 127-sintaxis-casos-no-vuelve-igual

**Sintaxis de casos no vuelve igual**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.sintaxis_casos_ida_y_vuelta`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Un caso del corpus se imprime y se relee, pero vuelve con el nulo convertido en texto. La herramienta de sintaxis declara verde una superficie que ya no representa el mismo caso.

**Qué se aprendió.** El corpus también es superficie publicada. Si un caso cambia de datos al pasar por el impresor, después las medidas se fijan contra otra evidencia.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "corpus/meta/ejemplo.caso", "origen": "corpus", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "corpus/meta/otro.caso", "origen": "corpus", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 128-sintaxis-casos-vuelve-exacta

**Sintaxis de casos vuelve exacta**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.sintaxis_casos_ida_y_vuelta`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Tres casos del corpus conservan datos y texto canónico al imprimirse y releerse: uno con relación vacía, uno con clave declarada y uno con filas heterogéneas.

**Qué se aprendió.** La ida y vuelta de casos tiene que mirar las formas incómodas del corpus, no sólo la tabla homogénea común.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "relacion-vacia", "origen": "corpus", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "clave-declarada", "origen": "corpus", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "filas-heterogeneas", "origen": "corpus", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 129-sintaxis-casos-generados-no-vuelve-igual

**Sintaxis de casos generados no vuelve igual**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.sintaxis_casos_cubre_casos`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Un caso construido desde la forma de datos pierde una relación presente y vacía. El corpus real puede no tener justo esa combinación mañana, pero la superficie la acepta y debe conservarla.

**Qué se aprendió.** La completitud de la sintaxis de casos no puede depender de que el corpus real justo tenga todos los bordes. Las sondas generadas fijan las formas que el lector y el impresor prometen aceptar.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_casos_cubre_casos", "caso": "902-generado-2-relaciones", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_cubre_casos", "caso": "901-generado-1-relaciones", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "corpus-ok", "origen": "corpus", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 130-sintaxis-casos-generados-vuelve-exacta

**Sintaxis de casos generados vuelve exacta**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.sintaxis_casos_cubre_casos`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Casos sintéticos con relación ausente, relación vacía, tres relaciones y `medida: null` sobreviven la ida y vuelta canónica sin cambiar.

**Qué se aprendió.** Generar casos desde la forma L0 amplía la garantía de reversibilidad a bordes que no conviene esperar a que aparezcan por accidente en el corpus.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_casos_cubre_casos", "caso": "900-generado-relacion-ausente", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_cubre_casos", "caso": "902-generado-2-relaciones", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_cubre_casos", "caso": "903-generado-3-relaciones", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_cubre_casos", "caso": "904-generado-sin-medida", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "corpus-ok", "origen": "corpus", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 131-sintaxis-casos-un-campo-por-vez

**Sintaxis de casos fija un campo por vez**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.sintaxis_casos_ida_y_vuelta`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Cada campo que la medida de ida y vuelta mira puede fallar solo. Si la medida confundiera `evaluo`, `mismo_veredicto`, `mismo_valor` o `mismos_testigos`, alguno de estos bordes quedaría sin detectar.

**Qué se aprendió.** Una medida con una disyunción larga necesita casos que aíslen cada término. Si dos campos fallan siempre juntos, el corpus no fija cuál estaba escrito.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "no-evaluo", "origen": "corpus", "evaluo": false, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "json-no-vuelve", "origen": "corpus", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "texto-no-vuelve", "origen": "corpus", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": false, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_ida_y_vuelta", "caso": "testigos-no-vuelven", "origen": "corpus", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 132-sintaxis-casos-generados-un-campo-por-vez

**Sintaxis de casos generados fija un campo por vez**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `meta.sintaxis_casos_cubre_casos`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Cada campo que la medida de completitud generada mira puede fallar solo. La propiedad no queda fijada si todos los rojos fallan por el mismo campo.

**Qué se aprendió.** La completitud generada también se fija con polaridad fina: no alcanza con un único caso rojo que mezcle todos los motivos de falla.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "sintaxis_casos_cubre_casos", "caso": "no-evaluo", "origen": "construido", "evaluo": false, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_cubre_casos", "caso": "json-no-vuelve", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": false, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_cubre_casos", "caso": "texto-no-vuelve", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": false, "mismos_testigos": true}, {"propiedad": "sintaxis_casos_cubre_casos", "caso": "testigos-no-vuelven", "origen": "construido", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 400-umbral-flotante-de-igualdad

**Un umbral final compara un flotante con igualdad exacta**

- etiqueta: `falso_verde` · se detectó por: `persona`
- medida que lo atrapa: `meta.ningun_umbral_flotante_de_igualdad`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La cabecera estructural de la medida declara un umbral `==` sobre un valor flotante. La igualdad exacta entre cantidades medidas es una falsedad silenciosa: 0.1+0.2 no es 0.3, y una medida así diría verde sin que nadie se enterara.

**Qué se aprendió.** El defecto no está en que el valor sea un número, sino en el operador final: sobre un flotante, `==` y `!=` no tienen borde operativo y hay que pedir una comparación de orden con tolerancia.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.umbral_flotante_igual", "umbral_es_flotante": true, "comparador": "=="}]
}
```

### 401-umbral-flotante-de-desigualdad

**Un umbral final compara un flotante con desigualdad exacta**

- etiqueta: `falso_verde` · se detectó por: `persona`
- medida que lo atrapa: `meta.ningun_umbral_flotante_de_igualdad`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La cabecera estructural de la medida declara un umbral `!=` sobre un valor flotante. La desigualdad exacta sufre el mismo vicio de representación que la igualdad: es la negación de una falsedad silenciosa, y por eso también se prohíbe.

**Qué se aprendió.** La regla cubre las dos igualdades exactas —`==` y `!=`— y no sólo una: una tolerancia mal escrita como `!=` es tan peligrosa como una igualdad mal escrita como `==`.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.umbral_flotante_distinto", "umbral_es_flotante": true, "comparador": "!="}]
}
```

### 402-umbral-flotante-de-orden-y-entero

**El orden sobre flotantes y la igualdad sobre enteros no ofenden**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.ningun_umbral_flotante_de_igualdad`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Una medida compara un flotante con una cota de orden (`<=`) y otra compara un entero con igualdad exacta (`==`). Ninguna de las dos es igualdad exacta sobre un flotante, y la regla debe dejarlas pasar.

**Qué se aprendió.** El verde cubre las dos maneras de no caer en el defecto: una tolerancia (orden sobre flotante) y una igualdad sobre algo que se cuenta o se nombra (entero). Si la disyunción se endurece, este caso se pone rojo.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.cota_flotante", "umbral_es_flotante": true, "comparador": "<="}, {"id": "dominio.igualdad_entera", "umbral_es_flotante": false, "comparador": "=="}]
}
```

### 403-umbral-sin-defensa

**Un umbral final no declara su defensa**

- etiqueta: `falso_verde` · se detectó por: `persona`
- medida que lo atrapa: `meta.ningun_umbral_sin_defensa`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La cabecera estructural de la medida trae un `porque` vacío. Un número que nadie puede discutir es una métrica esperando a volverse objetivo: sin defensa, el verde es una orden y no una conclusión.

**Qué se aprendió.** La regla mira la VACUIDAD de la defensa, no su calidad. Juzgar si una defensa es buena, circular o mentirosa es otra regla; ésta sólo asegura que exista algo que discutir.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.umbral_mudo", "porque": ""}]
}
```

### 404-umbral-con-defensa

**Un umbral con defensa no ofende**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.ningun_umbral_sin_defensa`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Dos medidas traen `porque` no vacíos. La regla debe dejarlas pasar: existe algo que discutir, aunque no sea la mejor defensa posible.

**Qué se aprendió.** El verde fija la polaridad contraria: la regla no exige una defensa perfecta, sólo una defensa presente. Si la condición se invierte, este caso se pone rojo.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.con_defensa", "porque": "un número que se puede discutir"}, {"id": "dominio.con_otra_defensa", "porque": "la tolerancia sale del desvío medido"}]
}
```

### 405-medida-sin-alcance

**Una medida no declara qué NO ve**

- etiqueta: `falso_verde` · se detectó por: `persona`
- medida que lo atrapa: `meta.ninguna_medida_sin_alcance`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La cabecera estructural de la medida trae un `alcance` vacío. Un verde que no declara su punto ciego se lee como «está bien», y el informe termina sin poder enumerar lo que no miró.

**Qué se aprendió.** La regla mira la VACUIDAD del alcance, no su contenido. No impone una fórmula textual ni un idioma; sólo exige que exista un punto ciego declarado.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.verde_absoluto", "alcance": ""}]
}
```

### 406-medida-con-alcance

**Una medida con alcance declarado no ofende**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `meta.ninguna_medida_sin_alcance`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Dos medidas declaran `alcance` no vacíos, incluso en otro idioma. La regla debe dejarlas pasar: el punto ciego está declarado, no importa cómo esté redactado.

**Qué se aprendió.** El verde fija que el alcance no impone una fórmula textual ni un idioma. La regla exige presencia, no redacción; endurecerla a un formato cerraría medidas válidas.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.con_alcance", "alcance": "NO ve la malla real"}, {"id": "dominio.con_alcance_ajeno", "alcance": "Blind spots are documented elsewhere"}]
}
```

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
  "mutante": [{"id": "orden_por_id", "apunta_a": "funcion._orden_visual", "cambio": "clave de sort: (y,x,id) -> id", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}]
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
  "mutante": [{"id": "sin_filtro_fondo", "apunta_a": "catalogo._vecinas", "cambio": "quitar el filtro es_fondo", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}]
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
  "mutante": [{"id": "umbral_yaw_flojo", "apunta_a": "catalogo.YAW", "cambio": "umbral <= 0.5 -> <= 5.0", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}]
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
  "mutante": [{"id": "algebra.py:50:27:comparador", "apunta_a": "algebra._cmp", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}, {"id": "algebra.py:51:26:comparador", "apunta_a": "algebra._cmp", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}, {"id": "algebra.py:53:26:comparador", "apunta_a": "algebra._cmp", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}, {"id": "algebra.py:54:27:comparador", "apunta_a": "algebra._cmp", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}, {"id": "medida.py:52:73:constante", "apunta_a": "medida.Veredicto.linea", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}, {"id": "medida.py:53:53:comparador", "apunta_a": "medida.Veredicto.linea", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}]
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
  "mutante": [{"id": "mutacion_codigo.py:sin_manejador_de_señales", "apunta_a": "mutacion_codigo._restaurar_todo", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}]
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
  "mutante": [{"id": "mutacion_codigo.py:enumerador_cache_sin_guarda", "apunta_a": "nucleo.mutacion_codigo.limpiar_cache", "detecciones_conductuales": 0, "rechazos_del_algebra": 0}]
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

### 043-ausencia-total-sale-verde

**La medida de ausencia se ponía más verde cuanto peor estaba el mundo**

- etiqueta: `falso_verde` · se detectó por: `herramienta_ajena`
- medida que lo atrapa: `proceso.modulo_con_consumidor`
- de dónde salió: Segtem/oracle · 515c723

**Qué pasó.** Con tres módulos y UN importador real, `proceso.modulo_con_consumidor` salía roja y señalaba los dos módulos muertos. Con los mismos tres módulos y NINGÚN importador —el mundo estrictamente peor— salía verde. `unir` con un lado vacío no produce pares, sin pares no hay grupos, el agregado sobre cero filas da 0 y el umbral `<= 0` lo lee como éxito. La medida no era monótona: empeorar el mundo la mejoraba.

**Qué se aprendió.** El `alcance` de la medida ya declaraba este hueco —«NO ve nada si la relación `importa` está vacía»— y declararlo lo volvía visible sin cerrarlo: la especificación llamaba RESUELTA a la ausencia y admitía el caso abierto tres líneas después. No es expresable con los cinco operadores: sin join no hay correlación, y DECISION-002 prohíbe que una medida consuma la salida de otra. Se cerró con `requiere`, el espejo de `alcance`: uno declara qué NO ve la medida, el otro qué NECESITA ver, y el evaluador falla cerrado antes de medir. La lección general es que un agregado sobre cero filas es indistinguible de un agregado que dio cero, y sólo la medida sabe cuál de las dos cosas es.

La evidencia, como relaciones:

```json
{
  "modulo": [{"nombre": "jam.a", "tests": 4, "importadores": 0}, {"nombre": "jam.b", "tests": 7, "importadores": 0}, {"nombre": "jam.c", "tests": 2, "importadores": 0}]
  "importa": []
}
```

### 044-sin-grafo-de-alcance-sale-verde

**Sin grafo de alcance, «todo módulo es alcanzable»**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `proceso.modulo_alcanzable`
- de dónde salió: Segtem/oracle · 515c723

**Qué pasó.** El sensor que produce la relación `alcanzable` falló y devolvió cero filas —no declaró entradas, o el análisis de imports se rompió—. `proceso.modulo_alcanzable` salía verde con tres módulos que nadie puede ejecutar: sin pares no hay grupos, el conteo da 0 y el umbral `<= 0` lo aprueba. El mismo defecto que `043`, en la otra medida que usa el patrón de ausencia, y lo encontró el mutador `quitar_requiere` como sobreviviente: la medida tenía la precondición pero ningún caso la fijaba.

**Qué se aprendió.** Un sensor que falla en silencio es indistinguible de un mundo en orden cuando la medida agrega sobre cero filas. Declarar `requiere` no alcanza si ningún caso lo fija: el mutador es lo que convierte la precondición en algo verificado y no sólo en algo escrito. Toda medida que use el patrón de ausencia —`unir` más `agrupar` sobre un predicado— necesita las dos cosas, la precondición y su caso.

La evidencia, como relaciones:

```json
{
  "modulo": [{"nombre": "jam.entrada", "es_test": false, "lineas": 40, "es_paquete_vacio": false}, {"nombre": "jam.medio", "es_test": false, "lineas": 25, "es_paquete_vacio": false}, {"nombre": "jam.hoja", "es_test": false, "lineas": 12, "es_paquete_vacio": false}]
  "alcanzable": []
}
```

### 058-rechazo-del-algebra-no-es-deteccion

**Un mutante que el álgebra rechaza no lo discriminó ningún caso**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.test_con_mutante_que_lo_mata`
- de dónde salió: Segtem/oracle · a694954

**Qué pasó.** Sustituir un campo por otro del mismo alias pero de otro tipo produce una comparación incomparable: el mutante levanta `ErrorDeAlgebra` antes de evaluar nada. No queda vivo —no hay riesgo de que pase inadvertido— pero tampoco lo discriminó ningún caso: ni siquiera llegó a producir un veredicto que comparar. Contarlo junto a las muertes conductuales publica una capacidad de detección que el corpus no tiene, y así el 129/129 declaraba 100% cuando lo conductual era 105.

**Qué se aprendió.** El caso es verde porque ninguno de los tres quedó sin observar, y eso es lo correcto: la medida denuncia sobrevivientes, no rechazos. Pero es el caso que fija la SEGUNDA condición del predicado. La mutación lo pidió: sin él, cambiar `rechazos_del_algebra` por `detecciones_conductuales` en la segunda comparación pasaba inadvertido, porque ningún caso tenía un mutante con rechazos y cero conducta. Es también el caso que sólo existe porque la política salió de Python: mientras `murio` era un booleano calculado en el sensor, esta distinción no era un hecho que un caso pudiera fijar.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "d.x·campo:2.2.1.1.1.2:n→s", "apunta_a": "d.x", "cambio": "campo:n→s", "detecciones_conductuales": 0, "rechazos_del_algebra": 3}, {"id": "d.x·quitar_filtro", "apunta_a": "d.x", "cambio": "quitar_filtro", "detecciones_conductuales": 2, "rechazos_del_algebra": 0}, {"id": "d.x·aflojar_umbral", "apunta_a": "d.x", "cambio": "aflojar_umbral", "detecciones_conductuales": 1, "rechazos_del_algebra": 1}]
}
```

### 059-clave-declarada-en-un-caso

**Una relación que declara su clave sigue midiéndose igual**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- medida que lo atrapa: `proceso.test_con_mutante_que_lo_mata`
- de dónde salió: Segtem/oracle · 6fec96a

**Qué pasó.** Un sensor que sabe cuál es la identidad de sus hechos puede declararla: `["clave", ["id"]]` a la cabeza de la relación. La evidencia sigue siendo L0 y la medida no se entera — el nodo no es un hecho, no se cuenta, no llega a los testigos y no cambia ningún veredicto. Este caso lo fija de punta a punta, desde la validación del corpus hasta el veredicto.

**Qué se aprendió.** El mecanismo de claves nació sin poder usarse en un caso: `tools/corpus.py` rechazaba el nodo como «no es un hecho», porque el validador del corpus y el del álgebra son dos lecturas del mismo contrato. Es el caso `012` otra vez —la misma regla escrita dos veces diverge— y se cerró haciendo que el corpus llame a `separar_clave` en vez de reimplementarla. Un mecanismo que el corpus no puede expresar es un mecanismo que este proyecto no puede fijar, y todo lo demás acá se fija con casos.

La evidencia, como relaciones:

```json
{
  "mutante": [["clave", ["id"]], {"id": "d.x·quitar_filtro", "apunta_a": "d.x", "cambio": "quitar_filtro", "detecciones_conductuales": 2, "rechazos_del_algebra": 0}, {"id": "d.x·negar_filtro", "apunta_a": "d.x", "cambio": "negar_filtro", "detecciones_conductuales": 1, "rechazos_del_algebra": 0}]
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
  "mutante": [{"id": "M1_umbral_siempre_cumple", "apunta_a": "algebra._cmp", "detecciones_conductuales": 1, "rechazos_del_algebra": 0}, {"id": "M2_donde_no_filtra", "apunta_a": "algebra.aplicar", "detecciones_conductuales": 1, "rechazos_del_algebra": 0}, {"id": "M3_contar_da_cero", "apunta_a": "algebra.resumir", "detecciones_conductuales": 1, "rechazos_del_algebra": 0}, {"id": "M4_campo_ausente_False", "apunta_a": "algebra.evaluar_expr", "detecciones_conductuales": 1, "rechazos_del_algebra": 0}, {"id": "M5_sin_defensa", "apunta_a": "medida.de_datos", "detecciones_conductuales": 1, "rechazos_del_algebra": 0}, {"id": "M6_sin_alcance", "apunta_a": "medida.de_datos", "detecciones_conductuales": 1, "rechazos_del_algebra": 0}]
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

### 200-corrida-sin-ninguna-corrida

**Corrida sin ninguna corrida**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `simulacion.corrida_reproducible`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Cero corridas registradas. Sin `requiere`, la medida agrega sobre cero filas, da 0 y el umbral `<= 0` lo lee como «todas las corridas son reproducibles» — cuando no hubo ninguna. El determinismo de un conjunto vacío no es una propiedad que valga la pena afirmar.

**Qué se aprendió.** Que una simulación no haya corrido y que haya corrido bien dan el mismo número, y sólo la medida sabe cuál de las dos cosas es. `requiere` lo cierra: sin corridas no se concluye.

La evidencia, como relaciones:

```json
{
  "corrida": []
}
```

### 201-presupuesto-sin-ninguna-corrida

**Presupuesto sin ninguna corrida**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `simulacion.no_se_agoto_el_presupuesto`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Cero corridas. Sin `requiere`, «ninguna corrida agotó su presupuesto» sale verde sobre la nada, y esa afirmación es la que después justifica confiar en lo que la simulación mostró.

**Qué se aprendió.** Es el mismo hueco que `200` en otra medida sobre la misma relación. Que las dos lo tengan no lo hace menos grave: significa que toda conclusión sobre esa simulación descansaba en dos verdes vacuos.

La evidencia, como relaciones:

```json
{
  "corrida": []
}
```

### 202-traza-sin-ningun-evento

**Traza sin ningun evento**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- medida que lo atrapa: `simulacion.la_traza_no_tiene_huecos`
- de dónde salió: Segtem/oracle · acfca07

**Qué pasó.** Cero eventos. Sin `requiere`, la medida reporta «la traza no tiene huecos» sobre una traza que no existe. Es el caso más claro de los tres: una traza vacía no es una traza completa, es la ausencia de traza.

**Qué se aprendió.** Lo encontró una medida meta que hoy es imposible de escribir sin la reificación —`meta.medida_de_ausencia_sin_requiere`, en un prototipo— y se nos había pasado a dos auditorías externas y a mí. El patrón `agrupar` sobre una relación vacía produce cero grupos, y cero grupos con umbral `<= 0` es verde.

La evidencia, como relaciones:

```json
{
  "evento": []
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

*857 líneas*

El álgebra: relaciones, expresiones y los operadores. Sin dependencias.

Una **fila de trabajo** es un mapa `alias → hecho`, más las columnas derivadas bajo la clave
reservada `_`. Toda operación toma filas y devuelve filas: eso es la clausura.

El lenguaje activo tiene cinco operadores: `de`, `donde`, `resumen`, `unir` y `agrupar`.

### `nucleo/caso.py`

*439 líneas*

Superficie de autoría para casos del corpus.

El almacenamiento histórico del corpus es JSON: un objeto con prosa y evidencia L0. Esta superficie
mantiene ese contrato y sólo cambia la forma de escribirlo: la prosa queda como prosa y la evidencia
homogénea queda como tabla.

### `nucleo/diferencial.py`

*192 líneas*

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

*282 líneas*

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

*328 líneas*

Macros: medidas que escriben medidas — y que ahora se declaran EN DATOS.

### Por qué cambió

Hasta este corte `MACROS` era un diccionario de funciones de Python acá adentro. O sea: las medidas
eran datos, pero **los medios de abstracción no**. Un proyecto que quería una forma propia tenía que
editar el núcleo de Oracle, y eso contradice de frente lo que el repositorio afirma de sí mismo — que
sin homoiconicidad el lenguaje tiene dueño, y que el dueño sería el LLM. El dueño *era* quien podía
editar este archivo.

Ahora una macro es un archivo de datos, con la misma forma para las que trae Oracle y para las que
escribe un proyecto:

```json
["defmacro", "<nombre>",
  ["<parametro>", ...],
  [["guarda", <expresion>, "<mensaje>"], ...],
  <plantilla>]
```

La plantilla es la forma canónica con huecos `["$", "<parametro>"]`. Expandir es sustituir. Las tres
macros universales —`ninguno`, `ninguno-par`, `peor`— viven en `nucleo/macros/` y se cargan como
cualquier otra: son la biblioteca estándar del lenguaje, no un privilegio del núcleo.

### Las guardas no traen evaluador nuevo

`ninguno-par` exige que sus dos alias difieran, y una plantilla pura no sabe expresar eso. La guarda
se sustituye primero y se evalúa después con `evaluar_expr` del álgebra sobre una **fila vacía**: una
expresión sin accesores nunca toca la fila, así que el mecanismo ya existía. De regalo hereda todo el
contrato del álgebra — comparación entre familias incompatibles, prohibición de igualdad exacta entre
flotantes, límites de profundidad.

### Esto no cuesta inspeccionabilidad

Una macro **expande a los mismos datos**, igual que en LISP: la expansión ocurre antes de construir la
medida, así que el evaluador, la mutación, el inventario y el nivel L2 siguen viendo formas canónicas
y no se enteran de que hubo macro. `tools/medida.py --expandir` muestra el resultado.

### Las macros son azúcar, no un embudo

La forma canónica sigue siendo válida y hay medidas que no pasan por macro. Un sistema de macros que
obliga a todo a pasar por él se vuelve una camisa de fuerza: si la forma no encaja, se escribe
canónica y listo.

### `nucleo/marco.py`

*118 líneas*

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

*620 líneas*

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

*348 líneas*

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

*449 líneas*

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

### `nucleo/sintaxis.py`

*988 líneas*

Superficie infija de autoría para medidas.

El lector devuelve la misma forma de almacenamiento que recibió el impresor, incluidas las
invocaciones de macro que ya viven en el catálogo.

### `nucleo/version.py`

*89 líneas*

La versión del álgebra y de la superficie que implementa este núcleo, legible por máquina.

`ESPECIFICACION.md` decía «Versión 0.3» en prosa y el núcleo no la conocía: cada extensión del
lenguaje apagaba un pedazo del diferencial en silencio, porque la implementación de referencia
estaba escrita contra una versión anterior y nadie lo comprobaba. Este módulo es el lugar único
donde los datos viven. De acá los leen los consumidores:

- `nucleo/proyecto.py`, para saber si un proyecto pide una versión compatible con la que hay;
- `tools/generar_diferencial.py`, para saber si la referencia se escribió contra esta versión;
- `nucleo/medida.py` y `nucleo/macro.py`, para comprobar que un `.oracle` guardado no declare una
  sintaxis que este núcleo ya no lee igual.

La regla sobre qué cambio sube qué parte de cada número está en `ESPECIFICACION.md` §0. Acá sólo
vive la maquinaria de comparar y de fallar cerrado: un `None` o un `False` silencioso es la forma en
que un defecto se disfraza de verde.

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

*315 líneas*

Genera y comprueba las cifras publicadas en el README de Oracle.

Un número escrito a mano en la prosa es una afirmación sin medida: nadie lo ejercita, así que no
puede fallar. Este archivo existe para que no queden. Cada bloque `<!-- <nombre>:inicio -->` del
README lo produce una función de acá, y `main()` sin `--actualizar` falla si alguno venció.

La deriva no es hipotética: el corte anterior publicaba «2202 líneas de núcleo», «106 negativas» y
una proporción de «trece a uno» cuando ya iban 2654, 150 y 16,2. La proporción era además el número
que el proyecto publicaba como criterio de falsación, y el que nadie estaba midiendo — las dos cosas
a la vez. Desde el 2026-08-24 ya no es un criterio sino una cifra de costo (el proyecto está en
estado EXPERIMENTAL, sin condición de cierre), pero sigue custodiada acá por el mismo motivo por el
que se empezó a generar: una cifra publicada a mano es una afirmación que nadie ejercita.

### `tools/corpus.py`

*255 líneas*

Verificador del corpus — la primera regla del repositorio, y se aplica a sí mismo.

    python tools/corpus.py            → verifica (sale != 0 si algo está mal)
    python tools/corpus.py --resumen  → verifica y además cuenta qué mecanismo atrapa qué
    python tools/corpus.py --nuevo meta/999-caso-nuevo
                                      → crea un caso nuevo en superficie

Comprueba lo que se degrada solo:

  1. **el esquema** de cada caso, y que el `id` sea el nombre del archivo;
  2. **la forma de la evidencia**: un mapa de relación → filas de campos ESCALARES. Es el contrato
     L0 de la especificación, y si se afloja acá se afloja en todo el resto;
  3. **que ningún caso se caiga en silencio**: un caso sin medida declara si sigue abierto, quedó
     resuelto por construcción o documenta un límite humano no automatizable.

La 3 es la que importa. Los casos incómodos —los que el marco todavía no puede medir— son
justamente los que no hay que perder: son la lista de lo que falta.

### `tools/diferencial.py`

*165 líneas*

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

*413 líneas*

Vuelca todo el repositorio a Markdown plano y autocontenido, para subirlo y estudiarlo.

    python tools/estudio.py [--proyecto <ruta>] [--destino estudio] [--confiar-escalares]
    python tools/estudio.py --archivo ORACLE-PARA-NOTEBOOKLM.md

Pensado para NotebookLM y parientes: ingieren **documentos planos**, no repositorios. Así que acá no
hay enlaces relativos, ni wikilinks, ni referencias a archivos que el lector no tiene. Cada documento
se explica solo.

Tres cosas que no son «copiar y pegar», y son la razón de que esto sea un generador y no una carpeta
mantenida a mano:

  1. **el catálogo y el corpus son datos**, y crudos se leen mal. Acá salen como prosa y tablas, con
     la medida expandida a su forma canónica al lado de cómo está escrita.
  2. **los mensajes de commit tienen buena parte del «por qué»** — las correcciones, los mutantes que
     sobrevivieron, lo que se descubrió a mitad de camino. Si sólo se suben los documentos, se pierde
     justo lo que más sirve para entender por qué las cosas son como son.
  3. **los docstrings del núcleo tienen el razonamiento**, no el código. Van enteros.

### `tools/generar_diferencial.py`

*182 líneas*

Emite los fixtures `oracle.diferencial/v1` desde la implementación de referencia.

    python tools/generar_diferencial.py            → comprueba que lo versionado esté al día
    python tools/generar_diferencial.py --escribir → reescribe los fixtures

Quién decide `referencia_ok` es `diferencial/referencia/evaluador.py`, escrito por otro autor que
nunca vio `nucleo/` (ver `diferencial/referencia/PROCEDENCIA.md`). Oracle no se copia a sí mismo: si
las dos implementaciones ya discrepan al generar, **no se emite el fixture**, porque un fixture que
nace en desacuerdo congela el desacuerdo en vez de exponerlo.

Regenerar dos veces con las mismas entradas produce exactamente los mismos bytes: la serialización es
JSON canónico con orden estable y sin `NaN`.

### `tools/medida.py`

*271 líneas*

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

### `tools/metamorficas.py`

*558 líneas*

Propiedades metamórficas: dos caminos que tienen que dar lo mismo.

    python tools/metamorficas.py            → informe
    python tools/metamorficas.py --hechos   → evidencia JSON

Una propiedad metamórfica no dice cuál es el resultado correcto: dice que **dos formas distintas de
escribir la misma medida tienen que coincidir**. Por eso atrapa defectos que nadie imaginó — no hace
falta saber la respuesta, sólo que los dos caminos lleguen al mismo lugar.

`PLAN-LENGUAJE.md` §(e.1) enumeró cinco. Una ya vive como medida sobre la traza
(`meta.donde_nunca_agrega_filas`); las demás son equivalencias, y una equivalencia no se lee de una
traza: hay que **correr las dos formas y comparar**. Eso es lo que hace este sensor.

### Por qué algunas formas se construyen acá y no salen del catálogo

Medido el 2026-08-24 sobre las medidas publicadas: **cero** usan dos `donde`, **cero** usan
`agrupar` sin claves, dos usan `unir` y la mayoría están escritas por macro. Así que dos de las
propiedades no tienen ningún material real contra el cual comprobarse.

Comprobarlas sólo donde el catálogo casualmente las ejercita sería medir la coincidencia, no la
propiedad: el día que alguien escriba la primera medida con dos `donde`, la propiedad tendría que
haber estado vigente desde antes. Así que el sensor **construye** las formas que el catálogo no
tiene, y cada hecho declara su `origen` —`catalogo` o `construido`— para que la medida que lo juzga
no pueda confundir una cosa con la otra.

El sensor produce HECHOS y no juzga: si una equivalencia que falla es aceptable lo dice una medida.

### `tools/mutar.py`

*153 líneas*

Muta las medidas y mide el resultado CON LAS MEDIDAS. El bucle se cierra acá.

    python tools/mutar.py [--confiar-escalares]          → informe
    python tools/mutar.py --hechos [--confiar-escalares] → evidencia JSON

El sensor produce hechos y las políticas aplicables del catálogo pueden juzgarlos. Un proyecto
neutral no necesita importar esas políticas para obtener el resultado operativo de la mutación.

Sale != 0 si algún mutante sobrevivió, porque un mutante que sobrevive es un aspecto de la medida que
el corpus no fija.

### `tools/mutar_codigo.py`

*324 líneas*

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

### `tools/sintaxis.py`

*214 líneas*

CLI para la superficie infija de autoría.

python tools/sintaxis.py --imprimir catalogos/meta/meta.donde_compone.json
python tools/sintaxis.py --leer medida.oracle
python tools/sintaxis.py --verificar

### `tools/trazar.py`

*174 líneas*

El evaluador como sensor de sí mismo: corre el corpus bajo traza y mide lo que el álgebra hizo.

    python tools/trazar.py            → informe
    python tools/trazar.py --hechos   → evidencia JSON

Oracle no puede evaluarse a sí mismo —recorrer un AST es recursión, y la recursión salió del álgebra
a propósito (`ESPECIFICACION.md` §8)— pero sí puede **juzgarse ejecutándose**. Es la doctrina del
proyecto aplicada al evaluador: el sensor produce hechos, el álgebra los mide, y acá el sensor es el
evaluador.

Lo que cambia con esto no es qué se verifica, sino DÓNDE vive la regla. «`donde` nunca agrega filas»
como test en Python es una afirmación que nadie muta y que no aparece en ningún inventario. Como
medida entra a la mutación, al corpus, al inventario de umbrales y al de puntos ciegos, igual que
cualquier otra — y sale del núcleo, que es la única dirección en la que la proporción mejora sin
sastrearla.

El punto ciego que esto tendría si se dejara solo: las medidas las evaluaría el mismo evaluador que
vigilan, y un defecto podría taparse a sí mismo. Por eso cada propiedad se juzga DOS veces —con
`nucleo/` y con `diferencial/referencia/evaluador.py`, escrito por otro autor que nunca vio el
núcleo— y un desacuerdo entre las dos hace fallar la corrida. No es una garantía absoluta: si las dos
implementaciones comparten el mismo malentendido, las dos callan igual. Es lo que un diferencial
puede dar.

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



### 2026-07-31 — Genera el estudio integral de Oracle

*commit d4ca54b*



### 2026-07-31 — Repara el CI: diferencial/ vacío, setuptools en 3.13, timeout flaky

*commit c558c4f*

`diferencial/` se quedó vacío tras dab72cb (los dominios se mudaron a
jam/medidas/) pero al ser un directorio vacío git no lo trackeaba, así que
en un checkout limpio `tools/mutar.py` fallaba con "falta diferencial/".
Se agrega `.gitkeep`.

`verificar_instalacion.py` usaba `pip wheel --no-build-isolation`, que
exige setuptools ya instalado en el intérprete. Las imágenes de Python 3.13
de actions/setup-python ya no lo traen preinstalado (las de 3.11 sí),
así que fallaba solo en esa versión. Se saca la bandera: el build aislado
además refleja mejor lo que vive un consumidor real.

`test_timeout_mata_tambien_un_nieto_que_ignora_SIGTERM` usaba timeout=0.2s,
insuficiente para arrancar dos intérpretes anidados bajo la carga de un
runner de GitHub Actions — el nieto no llegaba a escribir su pid antes de
que el harness disparara el timeout. Se sube a 1.5s.

Los tres bloqueaban el CI de main en el 100% de las corridas desde que se
agregó — y main es lo que Jam trae con `git subtree pull`.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### 2026-07-31 — Tapa el mutante que sobrevivía en marco.py: esperado_ok sin ejercitar

*commit 8424743*

El único test de hechos_de_casos nunca pasaba por la rama existe=True —
todos sus casos usaban una medida inexistente o None, donde
`dio = esperado` se autoiguala aunque el `==` de la línea 37 se mute a
`!=`. El mutador (ya corriendo en CI tras el fix anterior) lo encontró:
nucleo/marco.py:37 comparador Eq→NotEq sobrevivía.

Se agrega un caso con una medida real (falsa, vía stub) para pinchar la
polaridad: etiqueta que coincide vs. que no coincide, con dio_ok fijo e
independiente. cifras.py actualiza el README con el nuevo conteo de tests.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### 2026-07-31 — Agrega tutorial práctico de sintaxis, complementario al estudio integral

*commit ff1be61*

ORACLE-PARA-NOTEBOOKLM.md es el volcado integral (filosofía, especificación,
auditoría, historia). Este es distinto a propósito: aprender haciendo, de
menor a mayor complejidad, con ejemplos reales verificados contra el
evaluador — tanto del propio catálogo como del catálogo de geometría de Jam
en producción. Incluye un proyecto de punta a punta armado desde cero.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

### 2026-08-14 — Tres ítems del plan de lenguaje: cifras medidas, defmacro en datos, composición rechazada

*commit 515c723*

Trabajo del 2026-08-03 que había quedado sin commitear. Verificado entero antes
de entrar: 391 tests, aceptación 27 rojos / 12 verdes / 0 huecos, mutación de
medidas 129/129, y la matriz de mutación de código 16/16 en VERDE — 1230
mutantes muertos más el equivalente declarado, que son los 1231 sitios que el
README publica.

(d) Ninguna cifra tipeada a mano
`tools/cifras.py` genera cinco bloques del README y el CI falla si vencen.
Encontró cuatro derivas que nadie había detectado, y la peor es la que define al
proyecto: el README publicaba «2202 líneas / 106 raise / trece a uno» cuando los
valores reales eran 2654 / 150 / 16,2. El criterio de falsación declarado era
justamente el número que no estaba bajo medición. Otra afirmación —«sale en
VERDE, 1073/1073»— había sobrevivido a un cambio de denominador: el caso 021 del
corpus, cometido sobre el propio README.

Dos afirmaciones sin respaldo mecánico posible se borraron por decisión de Brian.
Una de ellas estaba replicada en `tools/estudio.py`, que la inyectaba en el
paquete de estudio: sacarla sólo del README la habría dejado publicándose.

`tools/cifras.py` entra a la matriz de mutación, y con la regla escrita en
HERRAMIENTAS_CUSTODIAS: los instrumentos entran de a uno y sólo cuando custodian
una afirmación que nadie más comprueba. Mutar `tools/` entero habría sumado 559
sitios de plumbing de CLI cuyo veredicto vive en `nucleo/`.

(a) defmacro en datos
Las tres macros salen de Python a `nucleo/macros/*.json`. El criterio se cumple
—una macro nueva no cuesta núcleo— pero la proporción EMPEORÓ, de 16,2 a 18,0, y
el plan había predicho lo contrario: el mecanismo que las reemplaza pesa más que
las tres funciones que borró. Queda publicado así, sin maquillar.

El numerador cuenta los `.json` junto con el `.py` a propósito: contando sólo
código, mover Python a datos habría «mejorado» la proporción sin que el lenguaje
encogiera un gramo — el sastreo exacto contra el que esta medición existe.

(c) Composición de medidas — RECHAZADA
DECISION-002. Una medida no puede consumir el resultado, los testigos ni el
veredicto de otra. No es costo: es el modo de falla que Oracle existe para
evitar, porque permite que las medidas se cubran entre sí y vuelve el `alcance`
incomprobable a mano. Lo importante no es el rechazo sino que una ausencia pasó
a ser una decisión, con su disparador de reversión escrito: dos medidas reales
en un proyecto consumidor que no se puedan expresar sin composición.

PLAN-LENGUAJE.md deja los dos ítems que faltan: (e.1) propiedades metamórficas y
(b) reificación mecánica del catálogo, que es lo que justifica la palabra
«metalenguaje» — hoy L2 tiene mecanismo propio y se llama `marco.py`.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Responde las dos auditorías externas: licencia, diferencial poblado y puerta de abandono

*commit c81a87c*

Dos auditorías independientes (Codex gpt-5.5 y DeepSeek, agosto 2026) coincidieron en
cuatro bloqueantes. Este commit los cierra y agrega los hallazgos que aparecieron al
hacerlo.

### Licencia (bloqueante en las dos)

MIT en LICENSE y en los metadatos del paquete. Verificado en el wheel:
`License-Expression: MIT` con el archivo incluido, así que un tercero puede identificar
los permisos automáticamente y redistribuirlo.

### El diferencial ya no está vacío

`diferencial/` contenía un `.gitkeep` de 0 bytes: la única de las tres «señales externas»
que podía romper el círculo de autoría estaba estructuralmente vacía.

Se escribieron tres implementaciones independientes del álgebra —Codex, Agy y DeepSeek V4
Pro— en directorios aislados, sólo con ESPECIFICACION.md y las dos DECISION, sin acceso a
`nucleo/`. Se versiona la de Codex en `diferencial/referencia/`, con PROCEDENCIA.md
declarando qué archivos vio: eso es el artefacto, porque desde afuera una implementación
independiente y una que espió se ven igual.

`tools/generar_diferencial.py` emite el fixture y se NIEGA a emitirlo si la referencia y
Oracle ya discrepan — un fixture que nace en desacuerdo congela el desacuerdo.

Sobre los 39 casos del corpus las cuatro implementaciones coinciden en todo, y eso no es
tranquilizador: el corpus no hace ninguna pregunta difícil. Los desacuerdos aparecieron
con 26 sondas dirigidas a los rincones que los propios autores declararon ambiguos, y se
separan en tres clases: la especificación no decide (las independientes se dividen entre
sí), `nucleo/` contra todas, y bugs de contrato de las implementaciones.

### El cortocircuito de `y`/`o` — un falso verde en el evaluador publicado

`all()`/`any()` sobre generadores cortocircuitan, así que un campo mal escrito dentro de
un `y` devolvía un False silencioso: exactamente el verde que §3 prohíbe, tres líneas
debajo del `raise` que existe para levantarlo. Y dependía de los datos — la misma medida
rota rompía con una evidencia y se escondía con otra.

Medido antes de tocar nada: 0 de 39 casos del corpus cambian de veredicto. El arreglo sólo
afecta a medidas rotas.

### `requiere`: el falso verde de la ausencia, cerrado

`unir` con un lado vacío no produce pares, sin pares no hay grupos, el agregado sobre cero
filas da 0 y un umbral `<= 0` lo lee como éxito. La medida más fuerte —«un módulo que
nadie importa»— salía VERDE justo cuando el mundo estaba peor. No es expresable con los
cinco operadores, y DECISION-002 prohíbe componer medidas.

Entra `["requiere", <relación>]`, nodo opcional y espejo de `alcance`: uno declara qué NO
ve la medida, el otro qué NECESITA ver. Fail-closed antes de medir, con veredicto
SIN EVIDENCIA. El álgebra queda intacta y las medidas sin `requiere` no cambian de forma
canónica, así que no se corren sus rutas de mutación.

El mutador `quitar_requiere` lo pone en el denominador: dejó un sobreviviente en
`proceso.modulo_alcanzable` —tenía la precondición y ningún caso la fijaba— y lo tapó el
caso 044.

### La puerta de abandono prerregistrada

Oracle exige umbral, defensa y testigo a toda afirmación, y no tenía ninguno para sí
mismo. Su criterio declarado —la proporción— ya disparó en contra tres cortes seguidos
(16,2 → 18,0 → 18,2) y la respuesta publicada fue reinterpretarlo. Y aunque no se
reinterpretara, es inmune a la adopción: los catálogos externos no entran a su
denominador, así que ningún consumidor puede mejorarla.

`COMPROMISOS.json` prerregistra la condición como dato, y la juzgan dos medidas: si al
2027-01-29 no hay dos consumidores independientes, se archiva el DSL y se conserva el
protocolo `caso + porque + alcance + testigos`.
`meta.cumplimiento_declarado_sin_respaldo` cierra la salida barata: para apagar la puerta
hay que escribir un número que alcance el umbral, no un `true`. El CI las corre.

No impide editar el archivo. Convierte cambiar de criterio en un commit fechado y visible
en vez de un párrafo que reinterpreta el anterior.

Al agregarlas, `meta.el_nivel_no_se_confunde_con_el_dominio` se puso roja y señaló las dos
por nombre: se llamaban `meta.` y su relación no estaba declarada como del lenguaje. Se
corrigió declarando `compromiso` reflexiva — describe al proyecto que mide, no al mundo
medido.

### Informe mutacional y deriva documental

`murio` y `murio_por_conducta` dejan de ser lo mismo: 24 de los 129 mutantes morían sólo
porque el álgebra los rechaza con una excepción, sin que ningún caso los discriminara.
El informe publica las dos cifras.

`tools/cifras.py` custodia ahora `estudio/00-esencia.md`, que ya tenía las marcas y nadie
las miraba; un documento declarado que no existe es error, para que borrar el archivo no
sea la manera de librarse de la medición. Corregida la deriva «26 de 27» → «15 de 18» en
cuatro documentos y la contradicción 17,6 / 18,0 en PLAN-LENGUAJE.

### Verificación

403 tests OK · CIFRAS OK · CORPUS OK (48 casos)
ACEPTACIÓN 31 defectos en rojo, 14 verdes correctos, 0 huecos sin tapar
DIFERENCIAL 4 acuerdos globales con referencia independiente
MUTACIÓN 155/155 — 131 por conducta, 24 rechazados por el álgebra
COMPROMISOS en plazo, faltan 158 días

La proporción quedó en 16,4 a 1. Subió a 18,2 por los arreglos al núcleo y bajó a 16,4 al
sumar las dos medidas de la puerta: con un denominador de 20 medidas, dos archivos la
mueven un 10%. Como criterio de falsación es demasiado sensible para significar algo, que
es precisamente por qué la puerta no depende de ella.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — El evaluador como sensor de sí mismo: las propiedades del álgebra, escritas en el álgebra

*commit a694954*

Oracle no puede evaluarse a sí mismo —recorrer un AST es recursión, y la recursión salió
del álgebra a propósito (§8), igual que DECISION-002 sacó la composición— así que el
bootstrap clásico no se completa nunca. Pero sí puede juzgarse ejecutándose, que es la
doctrina del proyecto aplicada al evaluador: el sensor produce hechos, el álgebra los mide,
y acá el sensor es el evaluador.

### La traza

`nucleo/algebra.py` emite tres relaciones bajo el contexto `trazar()`, apagado por omisión
y con costo de una lectura de ContextVar cuando lo está:

    paso(t, operador, filas_antes, filas_despues)
    nodo(cabeza, declarados, evaluados)
    producto(izquierda, derecha, salida)

### Las cuatro propiedades, como medidas y no como tests

Las de `PLAN-LENGUAJE` (e.1) nunca se habían implementado. Ahora son catálogo:

    meta.donde_nunca_agrega_filas
    meta.agrupar_no_agranda_la_relacion
    meta.unir_materializa_el_producto
    meta.los_logicos_evaluan_todos_sus_operandos

Lo que cambia no es qué se verifica sino dónde vive la regla. Como test en Python son
afirmaciones que nadie muta y que no figuran en ningún inventario. Como medidas entran a la
mutación, al corpus y al inventario de puntos ciegos igual que cualquier otra.

`tools/trazar.py` corre el corpus bajo traza y las evalúa. Entra al CI.

### Que muerdan, verificado inyectando el defecto

Una propiedad que no puede fallar no verifica nada, y acá el riesgo es concreto porque el
sensor vive dentro de lo que audita. Con cada defecto inyectado por separado:

    cortocircuito en `y`/`o`      → los_logicos_evaluan_todos_sus_operandos
    `donde` duplica una fila      → donde_nunca_agrega_filas
    `unir` pierde un par          → unir_materializa_el_producto
    `agrupar` inventa un grupo    → agrupar_no_agranda_la_relacion

y ninguna roja con el álgebra sana.

La tercera no mordía en el primer intento, y el motivo vale más que el defecto: el hecho se
anotaba DENTRO de `_unir`, leyendo su propia variable antes del `return`, así que cualquier
cosa entre esa línea y el punto de uso quedaba fuera de la medición. Un sensor que se lee a
sí mismo no audita la frontera. Se movió al punto donde el operador devuelve.

### Nueve casos de corpus

Ocho de las cuatro medidas en ambas polaridades, más `057`, que la mutación pidió
explícitamente: `aflojar_umbral` sobrevivía porque ningún caso caía pegado al límite. Un
mutante de umbral sólo lo mata un caso en el borde — la polaridad no alcanza.

Al escribirlos apareció un agujero que preexiste a este cambio: `tools/mutar.py` exime del
denominador a toda medida con prefijo `meta.`, y las cuatro nuevas heredaron la exención
gratis. Los casos las meten igual; la exención en bloque sigue abierta y merece su propio
trabajo.

### Escala

    mutantes de medida  155 → 203   (171 por conducta, 32 rechazados por el álgebra)
    corpus               48 → 57 casos
    proporción         16,4 → 14,0 a 1

La proporción se movió en la dirección buena, y hay que decir por qué con precisión: NO
porque el núcleo encogiera. El núcleo creció 59 líneas de instrumentación; el denominador
creció más, en proporción. Es el mecanismo que el README ya reconoce —escribir medidas
mejora la cifra—, no la demostración de que la apuesta paga.

La demostración de verdad sería borrar Python al escribir la medida que lo reemplaza. Acá
no había Python que borrar: estas propiedades nunca se habían implementado. Queda como la
prueba pendiente.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Primera migración real: la política de mutación sale de Python al catálogo

*commit b2c9ec7*

`nucleo/mutacion.py` abre diciendo, textual: «Devuelve EVIDENCIA (relaciones), no un
informe… un sensor no juzga, produce hechos». Veinte líneas más abajo juzgaba:

    if v.ok != esperado_ok:            murio, como = True, "invirtio_el_veredicto"
    elif huella cambió:                murio, como = True, "cambio_los_testigos"
    elif valor cambió:                 murio, como = True, "cambio_el_valor"
    except Exception:                  murio, como = True, f"error:{...}"

`murio` no es un hecho: es una política sobre cuatro observaciones. La prueba de que lo
era es que Codex la auditó como política —contar un rechazo del álgebra como muerte infla
el puntaje— y corregirla exigió editar Python.

### Qué se movió

El sensor publica ahora las cuatro observaciones crudas por detección
(`invirtio_el_veredicto`, `cambio_los_testigos`, `cambio_el_valor`,
`rechazado_por_el_algebra`) y por mutante los dos conteos que resumen a las cuatro
(`detecciones_conductuales`, `rechazos_del_algebra`). Ningún campo dictamina.

Quién sobrevive lo decide `proceso.test_con_mutante_que_lo_mata`, que además tiene que
defender el criterio: la justificación que era un comentario de Python es ahora su
`porque`, donde es obligatoria, aparece en el inventario de umbrales y se puede discutir.

### Lo que la mutación pidió, y sólo era pedible después de migrar

Con la política adentro de Python, «rechazado por el álgebra» no era un hecho que un caso
pudiera fijar. Al volverse hecho, el mutador `campo:rechazos_del_algebra→
detecciones_conductuales` quedó vivo: ningún caso tenía un mutante con rechazos y cero
conducta. Lo tapa `058`, que existe porque la política salió de Python.

### El resultado honesto: la proporción NO se movió

    nucleo/mutacion.py   356 → 348
    nucleo/marco.py      102 → 107   (validar dos enteros es más largo que un booleano)
    núcleo total        3079 → 3076   (−3 líneas)
    proporción          14,0 → 14,0   (sin cambio)

Ésta era la prueba pendiente que el commit anterior dejó planteada —«la demostración de
verdad sería borrar Python al escribir la medida que lo reemplaza»— y salió negativa.

El motivo es estructural y vale más que el número. Lo que quedó en Python es código de
SENSOR: observar si el veredicto cambió, si los testigos cambiaron, si hubo excepción.
Eso no puede migrar nunca, porque producir hechos es por definición trabajo del sensor.
Lo único que puede migrar son los JUICIOS, y un juicio en Python es un if/elif de cuatro
líneas mientras la medida que lo reemplaza son siete líneas de JSON.

Es decir: cada migración quita menos del numerador de lo que agrega al denominador. La
proporción mejora, pero por el mecanismo que el README ya reconoce —escribir más medidas—
y no por el que la apuesta declara: que los catálogos crezcan sin que crezca el núcleo.

Sumado a que los catálogos externos tampoco entran al denominador, la proporción no puede
demostrar lo que dice demostrar: ni la adopción la mueve, ni la migración la mueve. Es
evidencia adicional para el hallazgo 12 de la auditoría de DeepSeek, y una razón más para
que la puerta de abandono no dependa de esa cifra.

### Verificación

408 tests OK · CIFRAS OK · CORPUS OK (58 casos)
ACEPTACIÓN 36 rojos, 19 verdes · DIFERENCIAL ✓ · COMPROMISOS ✓ · TRAZAR ✓
MUTACIÓN 206/206 — 174 por conducta, 32 rechazados por el álgebra

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Cambia la consecuencia de la puerta: congelar el núcleo en vez de archivar el DSL

*commit a110606*

Archivar el metalenguaje y quedarse sólo con el protocolo era la propuesta de la auditoría
de Codex. Se descarta por decisión del autor: la tesis se considera viable y la
consecuencia es desproporcionada para lo medido.

La puerta conserva su condición, su fecha y su testigo; cambia sólo qué pasa si no se
cumple. Cero líneas nuevas en `nucleo/` hasta que haya un consumidor independiente —
arreglar un defecto no cuenta como agregar capacidad. Se corta la escalada de compromiso,
no el proyecto.

La alternativa descartada queda registrada en `COMPROMISOS.json` junto con el motivo, para
que dentro de seis meses se pueda juzgar la decisión y no sólo el resultado. Una puerta sin
consecuencia vuelve a ser la nota al pie que la proporción ya era.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Cierra las contradicciones de §3 y la deriva que dejó la migración

*commit 0e3c715*

### La clausura decía dos cosas incompatibles

`ESPECIFICACION.md` §3 abría con «Cada uno toma relaciones y devuelve una relación» y su
propia tabla, seis líneas abajo, decía que `resumen` colapsa a un escalar. Y afirmaba que
la clausura «permite que una medida consuma la salida de otra», que es exactamente lo que
`DECISION-002` prohíbe. Las dos las señalaron las auditorías (Codex 12, DeepSeek 10) y
seguían en pie.

Reescrita: cuatro operadores cierran sobre filas, `resumen` la rompe a propósito, y la
clausura es sobre filas y no sobre medidas. Que ninguna medida consuma a otra no es una
limitación pendiente sino una decisión registrada.

### Deriva que introdujo la migración anterior

Sacar `murio` del sensor dejó el ejemplo canónico de la especificación, del manual y del
tutorial mostrando un campo que ya no existe. Actualizados los tres.

`estudio/` es generado, así que se regeneró en vez de parchearlo — y ahí apareció que
`tools/estudio.py` referenciaba `AUDITORIA-2026-07-30.md`, archivo que se movió fuera del
repositorio y dejó la referencia colgando: el documento integral no se podía generar. La
lista de documentos del paquete pasa a declararse explícita, un declarado que falta es
error y no un salto silencioso, y entran los dos que faltaban: `DECISION-002` y
`COMPROMISOS.json`.

408 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · COMPROMISOS · TRAZAR
MUTACIÓN 206/206

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — La traza se contrasta con la implementación independiente, no consigo misma

*commit be9725b*

Las cuatro propiedades del álgebra las evaluaba el mismo evaluador que vigilan: un defecto
en `donde` podía tapar la medida que vigila `donde`. Era el punto ciego que el commit que
las introdujo dejó declarado y sin cerrar.

`tools/trazar.py` juzga ahora cada propiedad DOS veces —con `nucleo/` y con
`diferencial/referencia/evaluador.py`, escrito por otro autor que nunca vio el núcleo— y un
desacuerdo entre las dos hace fallar la corrida. Una referencia que revienta también cuenta
como desacuerdo: no se aprueba por incomparecencia.

No es una garantía absoluta y el docstring lo dice: si las dos implementaciones comparten el
mismo malentendido, las dos callan igual. Es lo que un diferencial puede dar.

Tres tests fijan que la comprobación pueda fallar, que es lo único que la hace valer:
acuerdo sobre la traza real, desacuerdo denunciado con `exit != 0`, y referencia rota
contada como desacuerdo.

411 tests OK · las siete verificaciones en verde

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — La exención del denominador de mutación deja de salir del prefijo del id

*commit 0caf4c2*

`tools/mutar.py` marcaba como «evaluada aparte» a toda medida cuyo id empieza con `meta.`, y
eso hacía dos cosas a la vez: acreditarla como ejercitada y sacarla del denominador de
mutación. Una clase entera de medidas quedaba fuera por una convención de nombre en vez de
por una propiedad comprobable. Lo noté cuando escribí cuatro medidas meta nuevas y heredaron
la exención gratis sin que nada avisara.

### Las dos preguntas se separan

«¿Alguien la ejercita?» y «¿debe tener mutantes?» no son la misma pregunta, y confundirlas
era el agujero. Ahora:

- **ejercitada**: la acredita un arnés que declare producir las relaciones que la medida lee.
  `tools/mutar.py` declara qué produce cada uno —aceptación, compromisos, trazar y él mismo—
  y la pertenencia se computa, no se nombra.
- **debe tener mutantes**: si algún caso del corpus la declara. Es donde la mutación puede
  correr y significar algo. Sin casos no hay nada que mutar, y de que nadie la ejercite se
  ocupa `meta.toda_medida_esta_ejercitada`.

Seis medidas meta entran al contrato que antes las eximía, con entre 8 y 14 mutantes cada
una: las cuatro propiedades de la traza y las dos de la puerta de abandono.

Declarar `tools/mutar.py` entre los arneses no es autoindulgencia: produce `medida_en_uso` y
juzga esos hechos al final de su propia corrida. Sin declararlo, las dos medidas que miran
esa relación salían «sin ejercitar» estándolo ahí mismo — un falso rojo, y un falso rojo
enseña a ignorar el verificador.

### Procedencia

Salió de delegar la tarea a un agente externo, que se quedó sin tiempo y dejó andamiaje de
depuración. Su dirección —derivar la exención de `relaciones_del_lenguaje`— la agrandaba en
vez de cerrarla: las cuatro medidas de la traza también leen relaciones del lenguaje. Se
descartó y se hizo por el otro camino.

413 tests OK · las siete verificaciones en verde · mutación 206/206

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Custodiar `estudio/` rompía el CI: era un archivo gitignoreado

*commit fa1662e*

`tools/cifras.py` pasó a custodiar `estudio/00-esencia.md` hace unos commits, y `estudio/`
está en `.gitignore` desde antes: es un artefacto que genera `tools/estudio.py`. En un
checkout limpio —el CI— el archivo no existe y `cifras.py` reventaba con FileNotFoundError.

Las siete verificaciones locales no podían verlo, porque la carpeta existe en el disco de
quien la generó. Apareció revisando el trabajo de un agente delegado, no corriendo tests.

Custodiar un generado además no sirve: una cifra vencida ahí es síntoma de que venció la
fuente, y la fuente —el README— ya está bajo custodia. Se arregla regenerando, no vigilando
la copia. La capacidad multi-documento y el «un declarado que falta es error» se conservan
para documentos versionados.

`test_solo_se_custodian_documentos_versionados` le pregunta a git si sigue cada documento de
la lista, y convierte esta clase de error en imposible en vez de en recordable.

414 tests OK · las siete verificaciones en verde

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Aisla la ejecucion de UDF externas en un trabajador separado

*commit ba9f2ff*

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh).

### 2026-08-24 — Merge branch 'trabajo-udf' into auditorias-externas-codex-deepseek

*commit 6fec96a*

## Conflicts:
##	README.md

### 2026-08-24 — Integra el aislamiento de UDF y cierra el sastreo por subpaquete que destapó

*commit 35e34b0*

### El aislamiento (trabajo de Codex, verificado aparte)

`escalares_del_proyecto()` ya no importa el `escalares.py` del proyecto en el proceso de
Oracle: registra proxies que hablan por JSON con un trabajador separado, con entorno mínimo
y una auditoría fail-closed.

Lo verifiqué con un ataque propio, distinto del que trae su test — cinco intentos, incluidos
dos que su test no cubría:

    leer un centinela fuera del proyecto   → bloqueado
    escribir fuera del proyecto            → bloqueado (y el archivo no aparece)
    lanzar un proceso                      → bloqueado
    abrir un socket                        → bloqueado
    listar /etc                            → bloqueado

Y el control que decide si sirve, porque un aislamiento que bloquea todo es una función
rota: una UDF legítima sigue funcionando, incluso leyendo un archivo DE ADENTRO del
proyecto, dentro de una evaluación real, y el registro se restaura al salir.

### El sastreo que destapó

`tools/cifras.py` contaba el núcleo con `glob("*.py")`, no recursivo: las 411 líneas del
aislamiento quedaban fuera del numerador Y fuera de la mutación de código por vivir una
carpeta más adentro. Codex lo declaró en su informe —siguió la restricción de archivos que
le di— así que no fue sigiloso, pero el efecto es un cuarto vector de sastreo: mover un
módulo a `nucleo/<subpaquete>/` lo sacaba del criterio de falsación del proyecto.

El conteo pasa a ser recursivo y el módulo entra a los objetivos de mutación del CI. La
proporción sube de 13,9 a **15,8 a 1**, que es la cifra honesta: el numerador incluye ahora
lo que antes se escondía. El numerador ya contaba `nucleo/macros/*.json` por este mismo
motivo; sólo faltaba que valiera para los `.py`.

`test_un_subpaquete_de_nucleo_cuenta_como_lenguaje` vuelve imposible la clase de error.

### Un falso rojo, de paso

`test_la_copia_temporal_se_elimina_al_terminar` comparaba el listado de `/tmp` compartido, y
fallaba si CUALQUIER otro proceso estaba mutando a la vez — pasó, con agentes corriendo en
paralelo. Ahora redirige el temporal a una carpeta propia. Un test que depende de que nadie
más use la máquina es un falso rojo esperando.

416 tests OK · las siete verificaciones en verde

Co-Authored-By: Codex (gpt-5.5) <noreply@openai.com>
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Claves de unicidad declarables por relacion

*commit f03953f*

Trabajo delegado a DeepSeek V4 Pro 0813.

### 2026-08-24 — Merge branch 'trabajo-claves' into auditorias-externas-codex-deepseek

*commit a58d49e*

## Conflicts:
##	INFORME.md
##	README.md

### 2026-08-24 — Integra las claves de unicidad y las hace usables desde el corpus

*commit d36a24e*

### El mecanismo (trabajo de DeepSeek V4 Pro 0813, verificado aparte)

Una relación puede encabezarse con `["clave", [<campo>, …]]` y la unicidad se comprueba
antes de medir, fail-closed. Verificado con pruebas propias, distintas de las suyas:

    sin clave                    → la bolsa cuenta duplicados, conducta idéntica a la de antes
    ids únicos                   → mide normal
    id duplicado                 → ErrorDeAlgebra nombrando la clave, la fila y con cuál chocó
    campo de la clave ausente    → error, no un nulo silencioso
    valor de clave no escalar    → error
    clave compuesta (id, t)      → la multiplicidad intencional sigue expresable
    el nodo no cuenta como hecho → una relación con 1 hecho más el nodo mide 1

`DECISION-001` no se revierte: una relación sigue siendo una bolsa y la unicidad es opcional.

### El hueco que traía, y por qué importaba

`tools/corpus.py` rechazaba un caso que declarara una clave —«no es un hecho»— porque su
validador L0 es una segunda lectura del mismo contrato que el del álgebra. No fue culpa del
agente: `tools/` no estaba entre sus archivos asignados.

Pero la consecuencia era que el mecanismo no se podía fijar con casos, y en este proyecto
todo lo demás se fija con casos. Se cerró haciendo que el corpus llame a `separar_clave` en
vez de reimplementarla, con un test que falla si alguien vuelve a escribir la regla dos
veces — es el caso `012` del corpus, la misma regla en dos lugares divergiendo.

`059` la ejercita de punta a punta: validación del corpus, evaluación y veredicto.

436 tests OK · las siete verificaciones en verde · mutación 206/206

Co-Authored-By: DeepSeek V4 Pro <noreply@deepseek.com>
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Merge branch 'auditorias-externas-codex-deepseek'

*commit 4e5cf65*



### 2026-08-24 — Reescribe la puerta: el repo queda privado, así que la condición vieja era incumplible

*commit 31c0afe*

El 2026-08-24 se decidió mantener Oracle PRIVADO y diferir la publicación. Eso volvió
imposible la condición prerregistrada —«dos consumidores independientes al 2027-01-29»—:
nadie puede usar lo que no puede encontrar, clonar ni forkear, así que la puerta habría
salido roja con certeza y no por la razón que decía medir. Una condición incumplible por
construcción no mide nada.

Se reemplaza HOY, con cinco meses de plazo y sin conocer el resultado, que es la única
ventana en que un prerregistro vale algo. Hacerlo en enero al verla roja habría sido
exactamente la reinterpretación que esta puerta existe para impedir.

### La condición nueva

    Al 2027-01-29: los catálogos de los consumidores suman ≥ 80 medidas (hoy 47)
    y `nucleo/` no superó las 3658 líneas.

Es **la apuesta declarada del proyecto** —«que los catálogos crezcan sin hacer crecer el
metalenguaje»— y hasta ahora nada la medía: los catálogos externos no entran al denominador
de la proporción, así que ningún consumidor podía moverla (hallazgo 12 de DeepSeek). Las dos
mitades cuentan y basta que falle una: un catálogo que crece a costa de un núcleo que crece
más no demuestra la tesis, la contradice.

### El número deja de escribirse a mano

Era el agujero de la versión anterior: `observado` y `cumplido` los tipeaba una persona, así
que la puerta detectaba la fecha pero no detectaba que la condición se cumpliera. Servía sólo
para el lado de fallar.

Ahora el compromiso declara DÓNDE mirar y `tools/compromisos.py` cuenta: los archivos de los
catálogos consumidores declarados y las líneas del núcleo, estas últimas con la misma función
que publica las cifras del README —dos lecturas del mismo número divergen—. Una fuente
declarada que no existe es un error y no un cero: un cero silencioso haría que «borré el
proyecto» y «el proyecto no creció» dieran lo mismo. Y un compromiso medible que además traiga
`observado` escrito no carga: el declarado ganaría sin que nadie lo note.

La medida juzga lo OBSERVADO y ya no el `cumplido` declarado.

### Lo que se perdió, dicho

La prueba de TRANSFERENCIA — la que distingue «general» de «sobreajustado a su autor», y la
que las dos auditorías piden. La condición nueva NO la reemplaza: mide otra cosa, más barata.
Por eso la decisión de publicar queda como un segundo compromiso con su propia fecha, y la
condición original queda en `historial` con el motivo del cambio, para que se pueda juzgar la
decisión y no sólo el resultado.

### Deriva del README, de paso

Decía «la proporción viene empeorando, dos veces seguidas» y publicaba 16,2 → 18,0 → 18,2
cuando hoy está en 16,2 otra vez. La prosa quedó vieja respecto de su propia cifra. Corregido
con lo que de verdad pasó: subió, volvió, y está donde empezó — y las dos veces que se movió
fue por escribir núcleo o por escribir medidas universales, nunca por un consumidor.

440 tests OK · las siete verificaciones en verde · mutación 213/213 · corpus 60 casos

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Escribe el disparador de la reificación y corrige el orden del plan

*commit 1cdf8ab*

### El disparador

(b) —la reificación, lo que justificaría la palabra «metalenguaje»— queda **congelado tras un
disparador** en vez de pendiente:

> Suena cuando alguien —no el autor— quiere escribir una medida meta que hoy exige editar
> Python.

Es la regla que gobierna el álgebra desde el principio, aplicada al metalenguaje: no se
agrega reflexión hasta que una segunda pregunta meta la necesite, y la necesite un consumidor.
Todavía no sonó: los dos consumidores suman 47 medidas —geometría, malla, física, scatter,
recarga, ML deformer— y ninguna es meta. El límite lo detectamos desde adentro; nadie chocó
contra él.

### La deuda, medida

Lo que L2 ve de una medida son nueve campos que `como_hechos()` eligió a mano. La demostración
la dio el trabajo del propio día: **`requiere` se agregó el 2026-08-24, cambia veredictos,
tiene su mutador — y L2 no lo ve.** No se puede preguntar qué medidas declaran una
precondición sin agregar un campo en Python.

Y hay un segundo mecanismo propio que la sección no nombraba:
`ClasificacionMeta.relaciones_del_lenguaje` es un `frozenset` escrito a mano que el 2026-08-24
pasó de 3 entradas a 7 en dos ediciones del núcleo. La reificación tiene que cubrirlo o queda
la mitad del problema: una relación debería ser del lenguaje porque quien la produce lo
declara, no porque figure en una lista.

### El impedimento formal

`COMPROMISOS.json` fija un tope de 3658 líneas de núcleo; hay 3558. Quedan 100 líneas y la
reificación no entra. La puerta prohíbe hacer esto, y es exactamente para lo que se escribió.

### El orden global estaba viejo en cuatro puntos

- **(e.2)** figuraba como pendiente y el último: está HECHO desde el 2026-08-24, y antes que
  (e.1) contra lo que el orden predecía.
- **(e.1)** figuraba como pendiente: está PARCIAL, y con el detalle honesto — de las cinco
  propiedades listadas hay UNA implementada; entraron otras tres que la lista no tenía porque
  las pidió la traza y no la teoría.
- **(b)** pasa a congelado tras disparador.
- La proporción decía «hoy 18,0 a 1» cuando el README publicaba 16,2.

Esa última línea deja de copiar el número: este documento se declara un registro fechado y
copiar la cifra viva ya le costó dos derivas —llegó a publicar 17,6 y 18,0 a la vez—. Queda
el movimiento, que sí es historia: subió y volvió, y las dos veces se movió por escribir
núcleo o medidas universales. Nunca por un consumidor.

440 tests OK · las siete verificaciones en verde

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Retira la puerta de abandono: el proyecto se declara EXPERIMENTAL → METALENGUAJE

*commit acfca07*

La puerta prerregistrada del 2026-08-24 —plazo, condición de cierre y tope de núcleo—
se retira entera el mismo día. El motivo no es que fuera incómoda: es que estaba mal
dirigida.

### El error de fondo

El README publicaba «si en seis meses la proporción no se movió, el lenguaje no valió la
pena». Eso es una afirmación de PRODUCTO, y Oracle no es un producto: es un experimento al
que le falta bastante para ser un metalenguaje. Las dos auditorías lo midieron con la vara
de algo adoptable porque este README las invitó a usar esa vara, y la puerta fue un parche
sobre el exceso en vez de una corrección del exceso.

El tope de núcleo era además un número inventado —el tamaño de ese momento más cien
líneas—. Oracle no lo necesitaba para nada.

### Lo que se retira

    COMPROMISOS.json                                  el prerregistro entero
    tools/compromisos.py                              su sensor
    meta.compromiso_vencido_sin_cumplir               las dos medidas que lo juzgaban
    meta.cumplimiento_declarado_sin_respaldo
    corpus/meta/045..048, 060                         sus cinco casos
    el paso del CI                                    y `compromiso` como relación del lenguaje

Y la afirmación de producto, que estaba en tres lugares además del README: hardcodeada en
`tools/estudio.py`, en el docstring de `tools/cifras.py` y en el de `escala()`. La cifra
sigue publicándose y sigue custodiada por el CI —una cifra escrita a mano es una afirmación
que nadie ejercita— pero deja de presentarse como veredicto: es el COSTO.

### Lo que se declara

    Estado: EXPERIMENTAL → METALENGUAJE

Arriba de todo en el README y en el encabezado del plan. El metalenguaje es el destino, no
la descripción: L2 todavía tiene mecanismo propio en Python, y el camino está en
`PLAN-LENGUAJE.md` con un disparador por ítem en vez de una fecha.

Lo que NO se afloja, y queda dicho: toda medida sigue declarando qué no ve, todo umbral
sigue trayendo su defensa, y la mutación sigue teniendo que terminar en cero sobrevivientes.
Ser experimental es un estado del proyecto, no un permiso para relajar sus reglas.

### Un equivalente vencido, de paso

Borrar `tools/compromisos.py` y editar el docstring de `cifras.py` corrió las líneas, y el
único equivalente declarado —identificado por `archivo:línea:columna`— quedó apuntando al
vacío. Hizo fallar dos tests en vez de pasar inadvertido: el mecanismo de frescura
funcionando. Reapuntado, con la fragilidad del id posicional anotada en su razón.

432 tests OK · CIFRAS · CORPUS (55 casos) · ACEPTACIÓN · DIFERENCIAL · TRAZAR
MUTACIÓN 182/182 — 150 por conducta, 32 rechazados por el álgebra

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Las cuatro propiedades metamorficas que faltaban de (e.1)

*commit 5164c05*



### 2026-08-24 — Reificacion mecanica del catalogo: L2 deja de depender de campos elegidos a mano

*commit 87096aa*

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh).

### 2026-08-24 — Cinco medidas declaran que necesitan evidencia para concluir

*commit fd43b2b*

Trabajo delegado a Agy (parcial: 5 de 18).

### 2026-08-24 — Merge branch 'meta-metamorficas'

*commit 1c1ed31*

## Conflicts:
##	README.md
##	nucleo/medida.py
##	tests/test_medida.py

### 2026-08-24 — Merge branch 'meta-ausencia'

*commit 7a765d4*



### 2026-08-24 — La referencia independiente vuelve a estar al día, y el diferencial dice qué se le escapó

*commit b250e6c*

### El síntoma

Agregar `requiere` a tres medidas de simulación dejó el fixture diferencial vencido, y no se
podía regenerar: la implementación de referencia rechazaba la medida con «debe tener seis
elementos». Extender el lenguaje había invalidado el contraste, en silencio.

### La raíz, que era peor

`ESPECIFICACION.md` §2 documentaba la forma canónica con seis elementos y NO mencionaba
`requiere`. La referencia no podía saberlo porque le faltaba la fuente: **se extendió el
lenguaje sin actualizar el documento que lo define.**

Documentado §2, incluido que un evaluador tiene que aceptar las dos longitudes.

### La re-derivación, sin ver el núcleo

Se delegó a Codex con acceso ÚNICAMENTE a la especificación y las dos decisiones — sin
decirle cuál era el nodo faltante, para que el ejercicio probara si el documento alcanzaba.

Alcanzó, y encontró CUATRO divergencias más que nadie había notado:

    ["requiere", …]        no lo aceptaba          ← la única que se sabía
    ["clave", […]]         lo rechazaba como hecho ← entró con las claves de unicidad
    límites de §9          no los implementaba
    `min`/`max` con bool   los ordenaba, y §3 dice que sólo son indicadores en suma/promedio

O sea que cada extensión del lenguaje venía apagando un pedazo del diferencial sin que nada
avisara. El contraste llevaba cuatro agujeros y publicaba «0 desacuerdos».

### Un defecto de los cargadores, encontrado al integrar

La referencia nueva usa `@dataclass`, y `tools/trazar.py` y `tools/generar_diferencial.py`
la cargaban con `spec_from_file_location` sin registrarla en `sys.modules` — que es lo que
`@dataclass` necesita para resolver sus anotaciones. Las dos herramientas reventaban con un
AttributeError que no dice nada.

Es un defecto de los cargadores, no de la referencia: una implementación escrita por otro
autor puede usar cualquier cosa del lenguaje, y el cargador no puede exigirle que se limite
a lo que hoy funciona por casualidad.

### Los tres mutantes que faltaban

`quitar_requiere` sobrevivía en las tres medidas de simulación: se les agregó la precondición
sin los casos que la fijan. `200`, `201` y `202` los tapan, cada uno con la relación vacía.

El de la traza lo había encontrado una medida meta que hoy es imposible de escribir sin la
reificación, y se les había pasado a dos auditorías externas y a mí.

434 tests OK · CORPUS 79 casos · MUTACIÓN 345/345 · las siete verificaciones en verde

Co-Authored-By: Codex (gpt-5.5) <noreply@openai.com>
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Superficie de autoria infija: lector, impresor y la ida y vuelta como propiedad

*commit 1d98b87*

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh).

### 2026-08-24 — Las 18 medidas declaran que hacen con la relacion vacia

*commit 835bcc2*

Trabajo delegado a Agy (gemini-3.7-flash-high).

### 2026-08-24 — Las 18 medidas declaran qué hacen con la relación vacía, y la garantía se vuelve cierta

*commit 28ed73f*

Una medida cuya relación de entrada viene vacía agrega sobre cero filas, da 0, y un umbral
`<= 0` lo lee como éxito. Quedaban 18 sin declarar qué significaba ese verde.

### No eran 18 bugs, y la distinción es la correcta

Ninguna necesitaba `requiere`, y el motivo es preciso: en el patrón `unir` + `agrupar`, una
relación SECUNDARIA vacía suprime el producto y oculta violaciones de una relación primaria
que SÍ tiene hechos — ahí el verde es falso. En un `ninguno` sobre una fuente única, vacío
significa que no existe ningún hecho infractor, y verde es vacuamente correcto.

Las 18 declaran ahora ese comportamiento en su `alcance`, que es lo que faltaba: no el
arreglo de una conducta, sino que la conducta dejara de ser tácita.

### Pero la garantía que declaraban era falsa

Los `alcance` nuevos agregaban «además `trazar.py` garantiza pasos trazados por construcción».
Lo probé: con la traza vacía, `trazar.py` publicaba cuatro verdes y **terminaba en 0**. Nadie
se enteraba. Un `alcance` existe para declarar qué NO ve la medida — uno que tranquiliza es
exactamente lo contrario.

Se arregló por el lado correcto: haciendo la garantía verdadera en vez de borrar la frase.
`tools/trazar.py` y `tools/metamorficas.py` fallan cerrado si no observaron ni un hecho.

    TRAZA VACÍA — no se observó ni un hecho de: nodo, paso, producto.
    Una corrida sin traza no es un álgebra sana: es un álgebra que no se miró.

Es el mismo defecto que las 18 medidas venían a declarar, un nivel más arriba: los arneses
que producen la evidencia tenían el problema que sus medidas describían.

440 tests OK · las siete verificaciones en verde · mutación 380/380

Co-Authored-By: Agy (gemini-3.7-flash-high) <noreply@google.com>
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Tres reglas del lenguaje pasan de raise a medida

*commit f7ea9fa*

Trabajo delegado a DeepSeek V4 Pro 0813.

### 2026-08-24 — Merge branch 'reglas-en-el-lenguaje'

*commit 9d2f8e9*



### 2026-08-24 — Tres reglas del lenguaje salen de Python y pasan a ser medidas

*commit 58d0aff*

Oracle dice ser un metalenguaje. Tener L2 no alcanza: lo que lo vuelve metalenguaje es que
sus propias reglas estén escritas en él. `nucleo/medida.py` tenía 16 `raise` con la gramática
del lenguaje en código imperativo — el mismo pecado que el proyecto ya corrigió dos veces.

### La distinción, que era todo el trabajo

    contrato de CARGA   qué es una medida BIEN FORMADA     se queda en Python, fail-closed
    POLÍTICA            qué es una medida ACEPTABLE        puede ser medida

Migraron tres, cada una con su corpus en las dos polaridades:

    meta.ningun_umbral_flotante_de_igualdad
    meta.ningun_umbral_sin_defensa
    meta.ninguna_medida_sin_alcance

### La tensión, y cómo se resolvió

Una política evaluada como medida corre DESPUÉS de cargar, así que durante un rato existiría
una medida sin punto ciego declarado. Se planteó sin resolver, con tres salidas posibles, y
la respuesta separa por modo de fallo:

- **`porque` y `alcance`**: se conserva el `raise` Y se agrega la medida. Son datos
  INCOMPLETOS — soltar el `raise` dejaría existir una medida a medias. La medida no reemplaza
  al contrato: lo vuelve inspeccionable, con su propio alcance y dentro de la mutación.
- **igualdad sobre flotantes**: se suelta el `raise`. Un umbral `== 0.3` es un dato COMPLETO y
  bien formado; su fallo ocurre después, en la comparación, donde `algebra.comparar` ya frena.

Y quedó descartada, con el mejor argumento del informe, la salida de «que el cargador consulte
al catálogo»: las medidas que validan medidas se cargan con el mismo cargador, y una medida L2
sólo juzga medidas YA cargadas — así que una medida sin `alcance` nunca llegaría a ser juzgada.
El bucle no se cierra, se muerde la cola.

### Verificado aparte, y resultó una mejora

Que soltar el `raise` deje la regla igual de cerrada:

    ["umbral","==",0.3]  carga ✓ · EVALUAR frena
    ["umbral","!=",1.0]  carga ✓ · EVALUAR frena
    ["umbral","<=",0.3]  carga ✓ · evalúa ✓        (orden: legal)
    ["umbral","==",0]    carga ✓ · EVALUAR frena   sobre datos flotantes

El último es lo interesante: el chequeo viejo miraba el LITERAL del umbral, así que `== 0`
contra datos flotantes se le escapaba. Moverlo a la comparación no aflojó la regla — la
extendió.

Y la medida atrapa lo que el `raise` dejó de atrapar: con una medida de umbral `== 0.5` en el
catálogo, `meta.ningun_umbral_flotante_de_igualdad` se pone roja y la nombra como testigo.

443 tests OK · las siete verificaciones en verde

Co-Authored-By: DeepSeek V4 Pro <noreply@deepseek.com>
Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

### 2026-08-24 — Mapa de fuente: el error del algebra dice donde, y la ruta se traduce a linea

*commit e9d7ee3*

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh).

### 2026-08-24 — defmacro acepta parametros opcionales con valor por defecto

*commit eb9ad40*

Trabajo delegado a Agy (gemini-3.7-flash-high).

### 2026-08-24 — Merge branch 'lang-macrorequiere'

*commit 4077e7c*

## Conflicts:
##	README.md

### 2026-08-24 — Revert "Merge branch 'lang-macrorequiere'"

*commit d2532fa*

This reverts commit 4077e7c9ae433835dcc3a9c8dee2f3df44fa0bc6, reversing
changes made to e9d7ee31a4b6561fa32f5d8d6d7ed97d29e496d7.

### 2026-08-24 — El algebra declara su version, y la incompatibilidad se detecta

*commit dbf7a4d*

Trabajo delegado a DeepSeek V4 Pro 0813.

### 2026-08-24 — Merge branch 'lang-version'

*commit 3c59e84*

El álgebra pasa a declarar su versión, y la incompatibilidad se detecta en vez
de manifestarse como un desacuerdo silencioso.

Un lenguaje que no dice qué versión de sí mismo implementa no puede tener
implementaciones independientes: el consumidor no sabe contra qué escribió, y
la referencia diferencial envejece sin avisar. Eso ya pasó cuatro veces —
`requiere`, `clave`, los límites de §9 y los booleanos de `min`/`max` entraron
al núcleo mientras la referencia seguía publicando «0 desacuerdos».

`nucleo/version.py` fija `VERSION_ALGEBRA` y la regla, escrita en
`ESPECIFICACION.md §0`:

  - MENOR sube cuando el álgebra GANA algo sin cambiarle el sentido a nada
    existente. Una referencia escrita contra una menor vieja sigue siendo
    correcta en lo que cubre, pero está incompleta: tiene que re-verificarse.
  - MAYOR sube cuando cambia el significado o el contrato de algo que ya
    estaba. Ahí la referencia vieja es incorrecta, no incompleta.

Dos comprobaciones, las dos fail-closed:

  - `oracle.json` puede pedir una versión del álgebra. Pedir una menor futura
    o una mayor distinta no carga el proyecto; no pedir nada sigue cargando.
  - `comprobar_version_referencia` exige que la implementación de referencia
    declare `VERSION_ALGEBRA`. No declararla es un error, no un silencio.

Trabajo delegado a DeepSeek V4 Pro 0813, verificado acá.

### 2026-08-24 — DECISION-003: `defmacro` se queda sin parametros opcionales, y esta vez con razon escrita

*commit 9633057*

El revert `d2532fa` salió con el mensaje por defecto de git, que dice qué se
deshizo y no dice por qué. En un repositorio donde el diario se genera de los
mensajes de commit, eso es una ausencia, no un detalle de forma.

La razón, ahora medida en vez de estimada:

  - `requiere` es variádico y `defmacro` no sabe abrir listas. Los parámetros
    opcionales (+23 líneas de núcleo, ya integradas) eran el primer eslabón de
    tres: faltaban splice y omisión condicional, unas 50-70 líneas más.
  - Pero las CINCO medidas universales que declaran `requiere` lo declaran con
    UNA sola relación, y en las cinco es la misma que la medida ya recorre con
    `de`. Eso una macro lo emite hoy, con CERO líneas de núcleo, reusando el
    parámetro `relacion` que ya recibe. Comprobado: expande y carga como
    `Medida` con `requiere == ("corrida",)`.

Así que no era caro-pero-necesario: era caro y no hacía falta. El error de
procedimiento fue no buscar la salida barata antes de delegar la cara.

Queda anotado lo que generaliza: **el primer eslabón de una cadena se mide por
la cadena entera**. Integrarlo solo deja núcleo muerto — una capacidad del
expansor que ninguna macro usa y que ningún test de medida ejercita.

Disparador de reversión, con la misma vara que DECISION-002: dos macros reales
que sólo se puedan escribir duplicando la plantilla entera por una rama, y donde
la duplicación ya haya producido una divergencia entre las copias. Y si entra,
entra con splice y omisión condicional en el mismo movimiento.

El documento entra al paquete de estudio (`tools/estudio.py`), que exige que
todo lo declarado exista, y queda enlazado desde el ítem (a) del plan.

456 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
MUTACIÓN 406/406 — 1477 detecciones, 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

### 2026-08-24 — docs: ensenar superficie infija primero en guia y tutorial

*commit b6b2027*

Reescribe ESCRIBIR-UNA-MEDIDA.md y ORACLE-TUTORIAL-PRACTICO.md con enfoque
superficie-primero:
  - Los ejemplos se presentan en la superficie infija de autoría.
  - El formato JSON queda documentado como formato de almacenamiento (AST),
    explicando su homoiconicidad y soporte para nivel L2.
  - Se documenta el pasaje bidireccional con tools/sintaxis.py (--imprimir y --leer).
  - Se regenera ORACLE-PARA-NOTEBOOKLM.md con tools/estudio.py.

456 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
MUTACIÓN 406/406 — 1477 detecciones, 0 sobrevivientes

### 2026-08-24 — Saca el informe de la rama

*commit 235a360*



### 2026-08-24 — Haz .oracle formato de catalogo

*commit 9578c76*



### 2026-08-24 — Saca el informe de la rama

*commit 1e5dc05*



### 2026-08-24 — Merge branch 'sup-primeraclase'

*commit 151ad8c*



### 2026-08-24 — Una gramática de id, y la documentación deja de creerse a sí misma

*commit 6361fef*

Tres huecos que salieron al hacer de la superficie infija un formato real. Los
tres son de la misma familia: una afirmación que nadie ejercitaba.

### 1 · El id tenía DOS gramáticas

`ID_MEDIDA_RE` gobernaba la creación de un archivo (`ruta_de_medida_nueva`) y la
superficie aceptaba `\S+`, cualquier cosa sin espacios. Así:

    tareas.vencida_sin_dueño   →  la superficie lo leía sin una queja
                               →  `--nueva` se negaba a crearlo

Un catálogo podía guardar ids que la propia herramienta no sabe escribir. Ahora
la gramática es una sola y se comprueba en los dos lados: al leer la superficie
y al construir la `Medida`, así que escribir el JSON a mano tampoco la saltea.

Y queda escrita la razón del ASCII, que no es que el proyecto no sea en español
—la prosa de `porque` y `alcance` lo es entera— sino que un id es también un
NOMBRE DE ARCHIVO:

    "dueño"  →  b'due\xc3\xb1o'    (ñ precompuesta, NFC)
    "dueño"  →  b'duen\xcc\x83o'   (n + tilde combinante, NFD)

Se dibujan idénticos y son distintos para Python, para git y para un `dict`.
macOS normaliza a NFD al escribir y Linux no toca nada, así que el mismo
catálogo clonado en dos máquinas puede tener dos ids que nadie distingue
mirando. Se cierra por gramática y no por normalización: normalizar es aceptar
la ambigüedad y después elegir por el autor. Un test lo demuestra en vez de
afirmarlo.

Las 83 medidas de los tres catálogos —Oracle, Jam y LyraGASP— ya cumplían la
gramática, así que exigirla no rompió a nadie.

### 2 · Una medida nueva nace en la superficie

`--nueva` entregaba una plantilla de JSON con corchetes anidados. El formato en
el que se autoriza a alguien a escribir es el primer mensaje que da el lenguaje,
y ese mensaje era «tu trabajo es anidar corchetes». Ahora crea un `.oracle` que
el catálogo carga tal cual, y un test carga la plantilla entregada: una
plantilla que no parsea manda contra la pared a la primera persona que la usa.

### 3 · La documentación afirmaba estar verificada, y no lo estaba

`ORACLE-TUTORIAL-PRACTICO.md` dice en su encabezado que todos sus ejemplos
fueron verificados contra el código vigente. Lo sostenía la palabra de quien
escribió el documento. Ahora `--verificar` lo comprueba: cada bloque ```oracle
tiene que leer Y volver idéntico a lo que imprime la herramienta —parsear no
alcanza, porque un ejemplo que lee pero no es canónico enseña una forma que la
herramienta no produce—.

Los bloques que NO son medidas completas se declaran, y la declaración es el
punto: ```oracle-gramatica para las plantillas con `<placeholders>`,
```oracle-fragmento para las líneas sueltas que enseñan un operador por vez.
8 declarados, 16 verificados. Un documento declarado que no está en el árbol es
un error, no un salto.

De paso, los documentos quedan al día con `.oracle` como formato de catálogo: ya
no mandan a traducir a JSON, porque no hace falta.

472 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS 33 medidas + 16 bloques de documentación
MUTACIÓN 406/406 — 1477 detecciones, 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — `defmacro` se escribe en la superficie, y la biblioteca estándar se guarda ahí

*commit 4214bf3*

La otra mitad del lenguaje. La superficie infija cubría las medidas y dejaba
afuera las macros: `nucleo/macros/` se escribía en JSON crudo, con
`["$", "nombre"]` para cada parámetro. Una sintaxis que cubre una mitad no es la
sintaxis del lenguaje.

Ahora las tres macros base se leen así, y así se guardan:

    defmacro ninguno-par(id, relacion, aliasA, aliasB, predicado, porque, alcance):
        guarda $aliasA != $aliasB "los dos alias de «ninguno-par» tienen que ser distintos"
        medida $id:
            de $relacion $aliasA
            unir $relacion $aliasB
            donde $predicado
            resumen contar(1)
            umbral <= 0 porque $porque
            alcance $alcance

`$x` es un hueco y es atómico —`$x.campo` no se acepta, porque un hueco no es un
campo—. La plantilla se imprime con el mismo impresor que cualquier medida, que
es lo correcto: la plantilla de una macro ES una medida con agujeros.

`--verificar` recorre ahora las macros además del catálogo, y `cargar_macros` lee
los dos formatos con la misma regla que el catálogo: el mismo nombre en `.json` y
en `.oracle` es un error, no gana ninguno.

Trabajo delegado a DeepSeek V4 Pro 0813 para la superficie y los nueve tests;
portado a mano porque `tools/sintaxis.py` se había partido en núcleo y CLI
mientras tanto. Cuatro cosas mías encima:

## 1 · El error tenía que leerse al derecho

`ErrorSintaxis` forzaba «se esperaba X» en todo, y salía «se esperaba parámetro
«sobra» que la plantilla nunca usa» — que se lee al revés de lo que pasó. Un
error que hay que descifrar es un error que no sirve. Ahora hay un modo literal
para los diagnósticos que no son «faltó algo en esta posición»:

    línea 1, columna 61: la macro declara el parámetro «sobra» y la plantilla nunca lo usa
    línea 3, columna 12: «$inventado» no es un parámetro de la macro

## 2 · El numerador perdía las macros al cambiarles el formato

`tools/cifras.py` contaba `nucleo/macros/*.json`. Pasarlas a `.oracle` las sacó
del numerador sin una queja: la proporción publicada habría bajado por un
renombre. Es el mismo sastreo contra el que la medición existe, con otra ropa
—ya había pasado con `indent=2` en los catálogos—. El inventario de formatos es
UNO y vive en `nucleo/macro.py`; un directorio de macros vacío ahora es un error
en vez de un numerador más chico.

El test que lo cuida tampoco fija nombres de archivo: fijar
`{"ninguno.json", "peor.json"}` a mano habría hecho fallar el test POR EL
RENOMBRE, no por lo que dice medir.

## 3 · `pyproject.toml` no habría empaquetado la biblioteca estándar

`["macros/*.json"]`. Una instalación por wheel se quedaba sin `ninguno`, y cada
medida escrita con ella fallaría después con «una medida es [...]», culpando al
archivo equivocado. Comprobado sobre el wheel construido, no supuesto.

## 4 · Se restauró el fragmento con caret

El puerto trajo la versión de `fragmento_de_error` anterior al mapa de fuente, y
un `.oracle` roto perdía el `^`. Un test lo agarró.

La proporción sube de 15,9 a **16,8 a 1**. Tener sintaxis cuesta, y el número lo
dice: es el precio de que alguien pueda escribir una medida sin anidar corchetes.

484 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS 33 medidas + 3 macros + 16 bloques de documentación
MUTACIÓN 406/406 — 1477 detecciones, 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — El catálogo universal se escribe en el lenguaje: 31 de 33 medidas en superficie

*commit 39b54d5*

Hasta acá la superficie infija existía y no era la sintaxis de nada: una sola
medida estaba escrita en ella. Un lenguaje cuyo propio catálogo no está escrito
en él no tiene sintaxis, tiene un traductor.

31 de las 33 medidas universales pasan a `.oracle`. Se ven así:

    ninguno meta.ningun_umbral_de_igualdad:
        de medida m
        donde m.comparador == "=="
        umbral <= 0 porque "un umbral `==` no tiene borde útil para la mutación…"
        alcance "mira sólo el operador final del umbral de cada medida…"

**Dos se dejan en `.json` a propósito, y hay un test que lo exige.** Si migraran
todas, el camino `.json` de `cargar_catalogo` dejaría de correrse en el catálogo
real y sólo lo tocarían los temporales de la suite; el día que se rompiera, se
enterarían Jam o LyraGASP —que guardan sus 50 medidas en `.json`— y no este
repositorio.

## Diez tests apuntaban al formato sin querer

`catalogos/meta/meta.donde_compone.json` escrito a mano en el test. Al migrar
fallaron los diez POR EL RENOMBRE, no por lo que dicen medir. Se agrega
`ruta_de_medida(mid)` —la medida por su id, en el formato en que esté— y los
tests que leían con `json.loads` pasan al lector común. Un test que se cae
cuando cambia el formato de almacenamiento está acoplado a él sin querer.

## Y la proporción se movió sola, que es lo importante de este commit

**16,8 → 24,7** sin que el lenguaje ganara una capacidad ni las medidas
perdieran una regla. Las mismas 33 medidas bajaron de 298 líneas a 203, porque
la superficie es más compacta que el JSON compacto.

Es la misma familia que el hallazgo de `indent=2`, que infló la proporción
reformateando archivos: **mientras el denominador se cuente en LÍNEAS, cambiar
cómo se escribe una medida mueve la cifra sin que cambie nada de lo que la cifra
dice medir.** Y acá compone en las dos direcciones a la vez — tener sintaxis
suma ~900 líneas al numerador Y acorta el denominador.

Queda publicado en el README como defecto ABIERTO de la métrica, y no se
arregla en este commit a propósito: cualquier arreglo bajaría el costo
publicado, y una métrica no se cambia en el mismo movimiento en que su resultado
incomoda. El número de hoy no se compara con el de ayer, y el README lo dice.

487 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS 33 medidas + 3 macros + 16 bloques de documentación
MUTACIÓN 406/406 — 1477 detecciones, 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Agrega superficie de casos del corpus

*commit 5219e6e*



## 2026-08-25 — La superficie declara su versión, como ya hace el álgebra

*commit 40dcb8b*



## 2026-08-25 — La superficie deja de creerle al catálogo: una propiedad sobre el álgebra generada

*commit 9a3d779*

`--verificar` decía «33 medidas, ida y vuelta OK» y eso probaba que la superficie
anda sobre LO QUE HAY ESCRITO — 33 medidas de un solo autor. No probaba que ande
sobre lo que el álgebra ACEPTA. Las construcciones que a ese autor no se le
ocurrieron nunca pasaron por el impresor.

`meta.sintaxis_cubre_algebra` cierra eso: un generador derivado de la gramática
—no una lista escrita a mano, que es el mismo problema una capa más arriba—
produce 94 medidas válidas y exige que imprimir, releer y reimprimir dé
exactamente lo mismo. Cubre `unir` encadenado hasta tres niveles, los seis
comparadores, los tres accesores, `y`/`o`/`no` anidados hasta profundidad 5,
`agrupar` con 0-2 claves y 1-2 agregados, los cinco agregados de `resumen`,
`requiere` con 0-2 relaciones, y los literales. Lo que NO cubre está escrito en
su `alcance`, que es donde va.

## Lo que encontró, reproducido acá antes de integrarlo

Rompiendo el impresor a propósito —que `<` se imprima como `<=`—:

    tools/sintaxis.py --verificar        33 medidas + 3 macros · ida OK · exit 0
    meta.sintaxis_ida_y_vuelta           ✓ verde
    meta.sintaxis_cubre_algebra          ✗ ROJO — 13 violaciones

**El aparato entero de verificación de la superficie era ciego a eso**, porque
ninguna medida del catálogo usa un `<` pelado en un `donde`. El agujero tenía
exactamente el tamaño de «las construcciones que nadie escribió», que es el modo
de falla que este repositorio existe para no tener y que ya había aparecido en el
diferencial vacío.

Tres casos de corpus en vez de dos, y la razón es buena: la medida disyunta sobre
cuatro condiciones, así que un solo rojo con todo fallando junto deja vivos cuatro
mutantes de reemplazo de campo. El caso `126` aísla cada rama —la misma lección
que los casos 108-111 y 123.

Trabajo delegado a Gemini 3.7 Flash (high). El experimento de rotura lo reproduje
por mi cuenta antes de integrar: no lo tomé de su informe.

488 tests OK · CIFRAS · CORPUS (93 casos) · ACEPTACIÓN · DIFERENCIAL · TRAZAR
METAMÓRFICAS 213 equivalencias · SINTAXIS 34 medidas + 3 macros + 16 bloques
MUTACIÓN 441/441 — 1582 detecciones, 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Saca el informe de la rama

*commit 2a0c2b9*



## 2026-08-25 — Merge branch 'sup-version': la superficie declara su versión

*commit 762d84c*

`.oracle` dejó de ser un formato de tránsito: 31 medidas universales y la
biblioteca estándar entera viven en él. La ida y vuelta que comprueba
`--verificar` dice que el lector y el impresor de HOY están de acuerdo entre sí;
no dice nada sobre un archivo escrito ayer. Es el hueco que el álgebra cerró
hace cuatro commits, abierto un nivel más arriba.

`VERSION_SINTAXIS = "0.1"`, con la misma maquinaria que el álgebra. Un `.oracle`
puede abrir con `sintaxis MAYOR.MENOR`; no declarar nada sigue cargando —los 35
archivos de hoy no declaran— y declarar una incompatible falla cerrado nombrando
las dos versiones. `oracle.json` también puede pedirla.

## La pregunta difícil, y la respuesta es buena

Pedí que defendiera si hacen falta DOS versiones —lector e impresor— porque no
envejecen igual. La respuesta es una sola, y el argumento se sostiene: **un
archivo viejo se LEE; el impresor no lo toca.** No existe el escenario que da
miedo («cambió cómo se imprime y el lector viejo no entiende») porque si el
impresor produce una forma que el lector de este núcleo no acepta, `--verificar`
revienta en el commit que lo cambió; y frente a un lector de otro núcleo, lo que
decide es la versión que el ARCHIVO declara, no el impresor que lo escribió.

Trabajo delegado a DeepSeek V4 Pro 0813.

## Dos cosas mías encima

**1 · Un fail-open al lado de dos fail-closed.** `cargar_fuente_medida` y
`cargar_macros` rechazaban una sintaxis futura, pero `tools/sintaxis.py --leer`
la traducía en silencio y con exit 0:

    $ python tools/sintaxis.py --leer futuro.oracle     # declaraba «sintaxis 9.0»
    ["ninguno","tareas.mide",…]
    exit=0

El lector puro no juzga —está bien y está defendido en su docstring—, pero esa
rama del CLI también carga. Una puerta abierta al lado de dos cerradas es peor
que ninguna: enseña a confiar. Hay un test que exige que las tres puertas den el
mismo veredicto sobre el mismo archivo.

**2 · Dos tests fijaban «33» y «34» a mano** y se cayeron al mergear con la
medida nueva de la rama anterior — por el conteo, no por lo que dicen medir. Es
el mismo error que tenía `--verificar` con su `== 29`, que en este repositorio ya
tiene nombre. Ahora se cuentan.

502 tests OK · CIFRAS · CORPUS (93 casos) · ACEPTACIÓN · DIFERENCIAL · TRAZAR
METAMÓRFICAS 213 equivalencias · SINTAXIS 34 medidas + 3 macros + 16 bloques
MUTACIÓN 441/441 — 1582 detecciones, 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Saca el informe de la rama

*commit 45a159f*



## 2026-08-25 — Merge branch 'sup-corpus': el corpus se escribe en una superficie, no en JSON a mano

*commit 90e975b*

`ESCRIBIR-UNA-MEDIDA.md` dice —con razón— «escribí el caso del corpus ANTES que
la medida», porque una medida escrita primero se escribe para pasar, no para
atrapar. O sea: lo PRIMERO que escribía un autor seguía siendo JSON crudo. La
superficie infija había arreglado el segundo paso y dejado el primero como
estaba.

Y el corpus no es un detalle: el README lo llama lo único que se pierde si no se
captura el mismo día.

    caso 309-una-traza-con-un-hueco:
        fecha: "2026-07-30"
        origen:
            repo: "Segtem/oracle"
            commit: "mutación de medidas P1.1"
        titulo: "Una única traza agujereada ya invalida la ronda"
        etiqueta: falso_verde
        sintoma:
            El fixture anterior contenía dos corridas con huecos. …
        como_se_detecto: mutacion
        medida: simulacion.la_traza_no_tiene_huecos
        evidencia:
            evento: corrida, t, actor, que
                "r1", 0, "trabajo", "empieza"
                "r1", 2, "trabajo", "termina"
        leccion:
            La continuidad se exige por corrida. …

**3300 líneas → 1823.** La tabla era el diseño correcto porque las 121 relaciones
del corpus tienen filas homogéneas — pero eso es un accidente del corpus, no una
regla del lenguaje: el álgebra dice que una relación es una BOLSA y admite filas
heterogéneas a propósito (`DECISION-001`). Si la tabla las obligara a compartir
claves, la superficie quedaría MENOS expresiva que el almacenamiento, que fue un
bug real hoy mismo con la `ñ` en un id. La salida de escape es `fila { … }`, una
por hecho, y tiene su test.

También sobreviven las dos distinciones que el corpus necesita y que un formato
tabular pierde solo: una relación **presente y vacía** no es una relación
**ausente**, y una relación puede declarar su `clave` en el encabezado
(`pieza: clave(id); id, v`).

Como el catálogo, **dos casos quedan en `.json` a propósito**: si migraran todos,
el camino `.json` sólo lo tocarían los temporales de la suite, y el día que se
rompiera se enterarían Jam o LyraGASP —que escriben su corpus en JSON— y no este
repositorio.

## La verificación que importa

No confié en la ida y vuelta del código nuevo. Comparé los 90 casos migrados
contra su JSON **original tomado de git**, campo por campo:

    idénticos al original: 90 · distintos: 0

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh).

Los tres casos que la rama de la propiedad metamórfica agregó mientras tanto los
migré yo, con la misma comprobación de ida y vuelta antes de borrar el original.

510 tests OK · CIFRAS · CORPUS (93 casos: 91 `.caso` + 2 `.json`) · ACEPTACIÓN
DIFERENCIAL · TRAZAR · METAMÓRFICAS · SINTAXIS
MUTACIÓN 441/441 — 1582 detecciones, 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Agrega red de sintaxis para casos

*commit 8ee635c*



## 2026-08-25 — Saca el informe

*commit 7f35302*



## 2026-08-25 — La mutación de código no corría, y la ronda que sí arrancó terminó en un traceback

*commit e451401*

Dos fallas del arnés, encontradas al lanzar la primera ronda sobre `nucleo/caso.py`
—425 líneas que entraron ayer y nunca se habían mutado—.

## 1 · La línea base salía roja, así que NINGUNA ronda era posible

    MUTACIÓN NO CONFIABLE — LineaBaseFallida

La causa la puse yo esta mañana: `test_solo_se_custodian_documentos_versionados`
le pregunta a git qué documentos están versionados. El arnés copia el proyecto a
un temporal **sin `.git`**, a propósito, y ahí git no contesta «no»: contesta un
error de entorno. El test lo leía como falla.

Es el caso `017` del corpus con otro traje —un error del arnés no es una muerte—
y significa que el README publicaba «16 objetivos del CI en VERDE, cero
sobrevivientes» sobre una ronda que hoy no se podía reproducir.

Tres intentos de arreglo fallaron por lo mismo: dependían del árbol de alrededor.
Lo que quedó:

- **la comprobación fuerte se mudó del test a `tools/cifras.py`**, que corre en el
  árbol real y en la secuencia de verificación. Un documento custodiado que git no
  sigue devuelve 1 y lo dice. Sin repositorio no afirma nada, que no es lo mismo
  que afirmar que está todo bien.
- **el test que queda arma su propio repositorio git en un temporal.** Un test que
  necesita el entorno de su autor no es un test, es una coincidencia.

## 2 · Y con la línea base verde, la ronda crasheó

`mutar_codigo.py:262` evaluaba cada medida aplicable sin atajar nada. Un mutante
de código y uno de medida son las dos cosas `mutante`, pero no tienen los mismos
campos: el de código no trae `detecciones_conductuales`, y `medidas_aplicables`
filtra por RELACIÓN presente, no por campo. Así, una medida escrita para la
mutación de MEDIDAS se declaraba aplicable y reventaba dentro del `donde`.

Resultado: **traceback de Python después de una hora de trabajo**, con el informe
a medio imprimir. Su propio contrato dice «sale 1 si algún mutante sobrevivió y 2
si la ronda fue inconclusa»; un traceback no es ninguno de los dos. La herramienta
que juzga a todas las demás era la única que no sabía informar su propio fracaso.

Ahora una medida que no puede juzgar esa evidencia se declara y se cuenta.

## Lo que la ronda alcanzó a decir antes de morir

**59 mutantes VIVOS sobre 185**, todos en `nucleo/caso.py`. Agrupados: aritmética
de línea y columna (`1 → 2`), comparadores de borde (`Lt → LtE`, `GtE → Gt`) y
`and ↔ or` en las validaciones. Traducido: la superficie del corpus promete decir
«archivo, línea y columna» y ningún test fija que la posición sea la correcta.
Queda como el trabajo siguiente, con la ronda ya reproducible.

511 tests OK

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Merge branch 'caso-red': el corpus recibe la red que ya tenía el catálogo

*commit e73b9d4*

La superficie de casos entró ayer y quedó sin la mitad de la infraestructura que
protege a la otra. La tabla, comparada:

                                    medidas (.oracle)      casos (.caso)
    --verificar los recorre         sí                     NO, cero
    metamórfica de ida y vuelta     sí                     no existía
    completitud sobre lo generado   sí                     no existía
    gramática del id                sí, al leer y cargar   ninguna
    andamio                         --nueva                no existía

Las cinco filas quedan en «sí»:

- `--verificar` cuenta ahora **36 medidas, 3 macros y 99 casos**. Antes ignoraba
  el 70% de los archivos que esa superficie gobierna.
- dos medidas nuevas: `meta.sintaxis_casos_ida_y_vuelta` sobre el corpus real y
  `meta.sintaxis_casos_cubre_casos` sobre casos generados.
- `ID_CASO_RE`, al lado de `ID_MEDIDA_RE`. El id de un caso es **más** un nombre
  de archivo que el de una medida —`tools/corpus.py` exige que coincidan— y no
  tenía gramática: `002-vencida-con-dueño` cargaba sin una queja. Misma razón
  escrita al lado de la constante: NFC contra NFD.
- `tools/corpus.py --nuevo <grupo/NNN-descripcion>` crea el andamio en `.caso`.

## El experimento de rotura, que es lo que decide si esto sirve

Rompiendo el impresor de casos —que el texto `"null"` se imprima como el nulo
JSON—:

    meta.sintaxis_casos_ida_y_vuelta   ✓ verde   (99 casos del corpus real)
    meta.sintaxis_casos_cubre_casos    ✗ ROJO    (5 violaciones)

El corpus real, entero, era ciego: ningún caso de los 99 tiene el texto `"null"`
en un campo. Es el mismo resultado que dio el generador de medidas hace dos
commits, y por la misma razón — lo que nadie escribió, nadie lo prueba.

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh).

519 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR
METAMÓRFICAS 325 equivalencias · SINTAXIS 36 medidas + 3 macros + 99 casos
MUTACIÓN de medidas 535/535 — 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

---

<!-- fuente: 08-los-numeros.md -->

## Los números, y qué dicen

| Qué | Cuánto | Qué dice |
|---|---|---|
| líneas del núcleo | 5111 | el lenguaje |
| líneas de medidas escritas en él | 218 | lo escrito en el lenguaje |
| proporción | 23 a 1 | la apuesta: que el segundo crezca y el primero no |
| (contando sólo el catálogo base) | 26 a 1 | sin ningún proyecto que lo use |
| negativas en el núcleo (`raise`) | 232 | su naturaleza es rechazar, no medir |
| medidas | 36 | de las cuales 24 miden el lenguaje mismo |
| casos de corpus | 99 | fallas reales, con su evidencia |
| commits | 98 | el historial completo |

**Estado: EXPERIMENTAL**, y el destino declarado es un metalenguaje. No hay fecha de corte
ni condición de cierre. La proporción de arriba es una cifra sobre el COSTO, no un
veredicto: es la única que no se puede sastrear escribiendo más medidas, y eso la hace
útil para mirar, no para dictaminar.

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

### Consecuencia registrada después (2026-08-24)

La cláusula «su sensor debe producirla o una medida debe comprobarla» tenía un hueco: la carga de
unicidad recaía en cada sensor, y un duplicado accidental inflaba `contar`, `suma` y los testigos sin
alarma. Se cubre con una **clave de unicidad declarable por relación**, un nodo opcional
`["clave", [<campo>, …]]` a la cabeza de la lista de hechos. No es un operador ni una normalización
silenciosa — la bolsa no cambia—: es un contrato que el sensor declara y Oracle valida **antes de
medir**, fail-closed, nombrando la clave y la fila que la viola. Sin el nodo, cero cambios de
conducta; la multiplicidad intencional sigue siendo expresable sin declarar nada.

---

<!-- fuente: 10-decision-sin-composicion.md -->

## Decisión 002 — las medidas no componen

**Estado:** rechazada la composición el 2026-08-03.

### Contexto

El álgebra cierra sobre **filas**: `de`, `donde`, `unir` y `agrupar` toman filas y devuelven filas, y
`resumen` las colapsa en un escalar. Esa clausura es lo que permite escribir tres dominios que no se
parecen en nada con los mismos operadores y sin un solo adaptador.

Pero **no cierra sobre medidas**. Una medida termina en un escalar y un umbral, y ahí se acaba: no hay
forma de que una medida consuma los testigos o el veredicto de otra. Eso deja preguntas naturales sin
escribir —«¿qué medidas comparten testigos?», «¿qué medida se pone roja siempre que esta otra se pone
roja?»— y obliga a que el nivel L2 se apoye en hechos que produce Python (`nucleo/marco.py`) en vez de
en el álgebra.

Una auditoría del 2026-08-03 lo señaló como el hueco de diseño más visible del proyecto: el álgebra
tiene clausura sobre la evidencia pero no sobre lo que enuncia sobre ella.

### Decisión

**La composición de medidas no entra al lenguaje.** Una medida no puede tomar como fuente el
resultado, los testigos ni el veredicto de otra medida.

### Por qué se rechaza, y no es por costo

No es una decisión de implementación diferida: el mecanismo sería barato. Se rechaza porque **es el
modo de falla que Oracle existe para evitar**.

Componer medidas permite que las medidas **se cubran entre sí**. Una medida que consume los testigos
de otra hereda su punto ciego sin declararlo, y el `alcance` —que es obligatorio justamente para que
un verde no se pueda leer como «todo bien»— deja de ser comprobable a mano: habría que recorrer la
cadena entera para saber qué no se miró. El README lo dice de la única forma que importa:

> Un conjunto de medidas puede ser internamente impecable y colectivamente ciego, y ninguna cantidad
> de reflexión lo detecta desde adentro.

La composición hace ese estado **más fácil de alcanzar y más difícil de ver**. Un conjunto de medidas
que se apoyan unas en otras produce mucho verde con poca evidencia independiente, que es exactamente
la forma que toma Goodhart cuando el que escribe la herramienta escribe también su verificador.

Hay además una razón de procedimiento, y en este repositorio pesa: **nada entra al lenguaje hasta que
una medida real lo necesite**. Hoy ninguna de las 18 medidas universales lo necesita. `con` y la unión
izquierda se retiraron por no alcanzar ese disparador, y la composición no está ni cerca de
alcanzarlo.

### Consecuencias

- El álgebra sigue cerrando sobre filas y no sobre medidas. Es una limitación **declarada**, no una
  ausencia por olvido — que es la única diferencia que importa entre las dos cosas.
- El nivel L2 sigue necesitando que alguien reifique el catálogo como hechos. Hoy eso lo hace
  `nucleo/marco.py` en Python, y ese acoplamiento es el problema que ataca el ítem (b) del
  [plan](PLAN-LENGUAJE.md) — **reificación mecánica, no composición**. Son dos caminos distintos para
  el mismo síntoma, y se elige el que no permite que las medidas se cubran entre sí.
- Una pregunta que hoy sólo se contestaría componiendo se contesta produciendo un **hecho nuevo** con
  un sensor, y midiéndolo con el álgebra que ya existe. Es más trabajo y deja la evidencia a la vista,
  que es el intercambio buscado.

### Qué evidencia revierte esta decisión

**Dos medidas reales, en un proyecto consumidor, que no se puedan expresar sin composición**, y cuya
ausencia quede registrada como hueco declarado en el corpus de ese proyecto.

Dos, no una: es el mismo disparador que aplicaron `con` y la unión izquierda, y que no alcanzaron.
Jam es el primer candidato con derecho a producir ese caso, porque es el primer consumidor que no se
diseñó junto con Oracle.

Si alguna vez entra, tiene que entrar con una regla que hoy no existe: **una medida compuesta debe
declarar el alcance acumulado de su cadena**, no sólo el propio. Sin eso, el `alcance` deja de
significar lo que significa hoy.

---

<!-- fuente: 11-decision-sin-parametros-opcionales.md -->

## Decisión 003 — `defmacro` no tiene parámetros opcionales

**Estado:** revertida la capacidad el 2026-08-24 (commit `d2532fa`, que revierte `eb9ad40`).

### Contexto

`requiere` entró al lenguaje el 2026-08-24 para cerrar el falso verde de la ausencia: una medida
declara qué relaciones **necesita** para concluir, y el evaluador falla cerrado —`SIN EVIDENCIA`—
antes de medir si alguna falta. Es el espejo de `alcance`.

De las 30 medidas universales, **25 pasan por la macro `ninguno`** y **5 declaran `requiere`**. Esas
cinco están escritas a mano con `desde` en vez de con la macro, y el motivo parecía obvio: la
plantilla de `ninguno` no emite un nodo `requiere`, y agregárselo obligaría a las 25 a declarar uno.

De ahí salió el pedido: que `defmacro` acepte **parámetros opcionales con valor por defecto**, para
que `ninguno` pudiera emitir `requiere` sólo cuando el uso lo pasara. Se delegó, se implementó
(+23 líneas de núcleo en `nucleo/macro.py`, con sus tests) y se integró.

### Decisión

**Se revierte.** `defmacro` sigue teniendo aridad fija y sin valores por defecto.

### Por qué

#### 1 · La cadena completa costaba mucho más que el primer eslabón

Los parámetros opcionales son el primero de tres eslabones. Para que `ninguno` emitiera `requiere`
de verdad hacían falta además:

- **splice** — `requiere` es variádico (`["requiere", "a", "b"]`, no `["requiere", ["a","b"]]`), así
  que una lista de relaciones tiene que **abrirse** dentro del nodo. `defmacro` sustituye `$`
  posición por posición y no sabe abrir nada.
- **omisión condicional** — un parámetro con valor por defecto emite igual el nodo. Para que una
  medida sin precondición no publique un `["requiere"]` vacío, la plantilla tiene que poder **no
  emitir** una rama.

Estimado en unas 50 a 70 líneas de núcleo para las dos, sobre las 23 ya gastadas. El
[plan](PLAN-LENGUAJE.md) publica la proporción de falsación —líneas de lenguaje contra líneas de
medida— como el costo declarado del proyecto, y esto la empeoraba sin agregar una sola medida.

#### 2 · El caso real no necesita nada de eso — y se comprobó

Las cinco medidas que declaran `requiere` lo declaran **con una sola relación**, y en las cinco esa
relación es la misma que la medida ya recorre con `de`. Una macro puede emitir eso hoy, con **cero
líneas de núcleo**, reusando el parámetro `relacion` que ya recibe:

```json
["defmacro", "ninguno-si-hay",
  ["id", "relacion", "alias", "predicado", "porque", "alcance"],
  [],
  ["medida", ["$", "id"],
    ["desde", ["de", ["$", "relacion"], ["$", "alias"]], ["donde", ["$", "predicado"]]],
    ["resumen", "contar", 1],
    ["umbral", "<=", 0, ["$", "porque"]],
    ["requiere", ["$", "relacion"]],
    ["alcance", ["$", "alcance"]]]]
```

Verificado: expande y carga como `Medida` con `requiere == ("corrida",)`. Una macro **hermana** de
`ninguno`, declarada como datos en `nucleo/macros/`, cubre el caso entero sin tocar el expansor.

Que la solución barata existiera desde el principio y no se hubiera buscado es el error de
procedimiento acá, y no el de quien implementó lo que se le pidió.

#### 3 · La regla propia del repositorio

**Nada entra al lenguaje hasta que una medida real lo necesite.** Ninguna de las 30 medidas
universales necesita un parámetro opcional; las cinco que motivaron el pedido se cubren con una macro
de aridad fija. Es el mismo disparador que retiró `con` y la unión izquierda, y el mismo que mantiene
afuera la composición de medidas ([`DECISION-002`](DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md)).

### Consecuencias

- `defmacro` sigue siendo lo más chico que sirve: aridad fija, sustitución posicional, sin defaults.
  Una macro que necesita dos formas se escribe como **dos macros**, que es más líneas de datos y
  menos líneas de núcleo — el intercambio que el proyecto declara buscar.
- Las cinco medidas con `requiere` siguen escritas a mano. No es deuda: son cinco, y ninguna repite a
  otra. La macro hermana se escribe cuando haya un patrón, no antes.
- Queda anotado que **el primer eslabón de una cadena se mide por la cadena entera**. Integrar los
  parámetros opcionales solos habría dejado núcleo muerto: una capacidad en el expansor que ninguna
  macro usa y que ningún test de medida ejercita.

### Qué evidencia revierte esta decisión

**Dos macros reales** —en el núcleo o en un proyecto consumidor— que sólo se puedan escribir
duplicando la plantilla entera por una sola rama variable, y donde la duplicación ya haya producido
una divergencia entre las dos copias.

Dos, no una: una macro duplicada es barata de mantener; dos que divergieron son la prueba de que la
duplicación no se sostiene. Y si entra, tiene que entrar **con splice y omisión condicional en el
mismo movimiento**: por separado, el primer eslabón no expresa ningún caso.

---

<!-- fuente: 12-plan-de-correccion.md -->

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
- [x] Elegir y declarar la licencia — MIT, en `LICENSE` y en `pyproject.toml` (verificado en el wheel).
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
