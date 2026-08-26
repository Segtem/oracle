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

---

> ## Estado: `EXPERIMENTAL` → `METALENGUAJE`
>
> **Hoy es un experimento**, y el metalenguaje es el destino, no la descripción. Falta bastante para
> llegar: la reflexión sobre el catálogo sigue fijada en Python —L2 tiene mecanismo propio, que es
> justo lo que un metalenguaje no debería necesitar—, y el camino está desglosado en
> [`PLAN-LENGUAJE.md`](PLAN-LENGUAJE.md).
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

No es un instrumento de medición: es un instrumento de **rechazo**. No calcula calidad: **declina
dejar pasar** lo que no se puede sostener.

<!-- negativas:inicio -->
En este corte hay 5674 líneas de lenguaje y **256 negativas explícitas** (`raise`).
<!-- negativas:fin -->

Un umbral sin defensa no se carga. Una medida sin `alcance` no se carga. Un campo ausente no da
`False`, levanta error. La igualdad exacta entre flotantes está prohibida, incluido el umbral final.
Un dominio sin defectos
declarados no genera fixture. Una medida que no discrimina se denuncia sola.

### Lo que produce no es confianza: es confianza ACOTADA

El veredicto no es el producto — el **punto ciego** lo es. Un informe verde termina enumerando lo que
no miró, y eso es lo que lo hace usable: un «todo bien» sin su alcance no se puede accionar, porque no
se sabe sobre qué se está callando.

### La asimetría, medida

La composición está [contada más abajo](#estado); el reparto es abrumadoramente de un lado: los
falsos verdes son más de diez veces los falsos rojos. Ésa es la justificación empírica de cada decisión de
«negarse antes que permitir». Pero un falso rojo enseña a ignorar el verificador, y por eso pesa igual
de grave: en un solo día lo cometí tres veces.

### El sujeto es el que construye, no lo construido

<!-- deteccion:inicio -->
Los 70 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 51 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
<!-- deteccion:fin -->

Ninguna de esas vías le pregunta al que escribió el código. Oracle no es un juez de artefactos — es
una prótesis para alguien que escribe la herramienta y su test con la misma mano y no recuerda ayer.

### El costo, dicho

<!-- escala:inicio -->
**5674 líneas de lenguaje** (`nucleo/`, código y macros) y **256 negativas explícitas** (`raise`). Contra las 37 medidas universales escritas en él (225 líneas): **25,2 a 1**. 29 de las 37 pasan por una macro.
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

### La proporción no alcanza como criterio, y el proyecto es EXPERIMENTAL

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
> sigue fijada en Python, ver [`PLAN-LENGUAJE.md`](PLAN-LENGUAJE.md)— y ése es el estado declarado,
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

## Estado

> **Estado auditado el 2026-07-31; P3 de embedding cerrado del lado de Oracle.** Los bypasses de simulación, baseline, caché,
> equivalentes y verdes vacuos tienen regresiones fail-closed; timeout y error del arnés son estados
> distintos de una muerte. P2.1 ya aísla la mutación de código en una copia, con bloqueo,
> subprocesos acotados y reanudación verificable. Ver
> [`AUDITORIA-2026-07-30.md`](AUDITORIA-2026-07-30.md) y
> [`PLAN-CORRECCION.md`](PLAN-CORRECCION.md).

**El paquete contiene los cinco componentes.** El [corpus](corpus/) (42 casos, en formato de autoría `.caso` o almacenamiento `.json`), la [especificación](ESPECIFICACION.md) del álgebra,
el evaluador (`nucleo/`), **las medidas universales** dentro de [`catalogos/`](catalogos/) —como
archivos de datos (`.oracle` y `.json`), no como código—, el sensor de mutación y la prueba diferencial.

**¿Querés escribir una medida?** → [`ESCRIBIR-UNA-MEDIDA.md`](ESCRIBIR-UNA-MEDIDA.md).
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
**104 casos**: 70 defectos y 34 verdes correctos. De los defectos, 67 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 65 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
<!-- corpus:fin -->

<!-- cifras:inicio -->
589 tests · 547/547 mutantes de medida · **2394 sitios de mutación de código** (2189 + 205 del motor Python).
<!-- cifras:fin -->

> **Baseline restaurado el 2026-08-03 sobre el denominador vigente.** Los 16 objetivos de la matriz
> del CI —uno por job, que es como se mide— salen en **VERDE**: cero sobrevivientes, cero errores de
> arnés, **un equivalente declarado** con su razón en [`equivalentes.json`](equivalentes.json). Cada
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

> ⚠️ **Esa foto es del 2026-08-03 y hoy no vale. Medido el 2026-08-25.** El núcleo creció de ~2900
> a más de 5500 líneas —la superficie infija y la del corpus son casi 1400 de ellas— y ese código
> **nunca se había mutado**. Cuando se intentó, aparecieron tres cosas, en este orden:
>
> 1. **La ronda no arrancaba.** La línea base salía roja porque un test le preguntaba a git, y el
>    arnés copia el proyecto sin `.git` a propósito. Ninguna ronda era reproducible, así que el
>    «cero sobrevivientes» de arriba no se podía volver a obtener.
> 2. **Con eso arreglado, la ronda crasheaba** con un traceback de Python en vez de un veredicto: su
>    contrato dice «1 si sobrevivió alguno, 2 si fue inconclusa», y un traceback no es ninguno.
> 3. **Con eso arreglado, 51 de 193 mutantes salían «error de arnés»** —no muertos, no vivos— porque
>    `ErrorSintaxis` es un `dataclass(frozen=True)` y eso congelaba también `__traceback__`: el tipo
>    de error del lenguaje no se podía re-lanzar desde Python.
>
> Recién la cuarta corrida fue concluyente, y dijo lo que había que decir:
> **193 mutantes · 136 muertos · 57 sobrevivientes · 0 timeouts · 0 errores de arnés**, todos en
> `nucleo/caso.py`. Son 38 constantes de posición, 9 comparadores de borde, 8 booleanos y 2 retornos
> — o sea: la superficie promete decir «archivo, línea y columna» y nada fija que la posición sea la
> correcta.
>
> Se deja escrito así, con el número feo a la vista, porque la alternativa era dejar arriba una
> afirmación verde de hace tres semanas sobre un código que en su mayoría todavía no existía. **Una
> cifra que no se puede volver a obtener no es una medición, es un recuerdo.**

### Tres dominios, un álgebra

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
medida con la misma forma») sonó con veintidós, cuando los dominios de instancia todavía vivían acá.
`ninguno`, `ninguno-par` y `peor` expanden a la forma canónica, y `peor` cerró por construcción la
deuda del umbral duplicado. La cobertura vigente sobre el catálogo universal está en
[la cifra de escala](#el-costo-dicho); las medidas que no encajan se escriben canónicas y listo.

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

`ninguno`, `ninguno-par` y `peor` viven en [`nucleo/macros/`](nucleo/macros/) y se cargan por el
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

### Dos oráculos, y ninguno alcanza solo

La ronda de mutación dejó algo a la vista: de 6 mutantes del núcleo, los 6 mueren con los tests, pero
**3 dejan la aceptación en verde**. El replay del corpus ejercita la *evaluación*; las reglas de
*declaración* —que un umbral traiga defensa, que el alcance no esté vacío— sólo las cubren los tests.
Hacen falta los dos, y conviene no confundir el verde de uno con el del otro.

### Qué falta

El camino de «formato de datos con buenas defensas» a «lenguaje» está desglosado en
[`PLAN-LENGUAJE.md`](PLAN-LENGUAJE.md): `defmacro` en datos, reificación mecánica del catálogo, la
decisión sobre composición, y el diferencial propio que hoy está estructuralmente vacío.

- ~~**Elegir una licencia.**~~ **HECHO.** MIT, en [`LICENSE`](LICENSE) y en los metadatos del
  paquete (`License-Expression: MIT`, con el archivo incluido en el wheel): un tercero puede
  identificar los permisos automáticamente y redistribuirlo.
- **Un consumidor real independiente.** El proyecto externo sintético demuestra desacoplamiento
  técnico; la adopción por un proyecto no diseñado junto con Oracle sigue siendo evidencia externa,
  no algo que este repositorio pueda fabricar.
- **La frontera humana del caso `011`**: la medición puede exigir trazabilidad, pero una atribución
  causal no tiene un verificador mecánico genérico. `004` y `012` ya figuran como resueltos y no
  inflan la deuda abierta.

## Por qué el corpus va primero

Porque es lo único que se pierde. Un LLM no recuerda sus fallas entre sesiones, y si el corpus se
escribe *después* del framework, se escribe para que pase. Los casos que hay acá se capturaron el
mismo día en que ocurrieron, antes de existir nada que los midiera.
