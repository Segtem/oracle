# Oracle — documento integral para NotebookLM

Fuente única de estudio del metalenguaje Oracle: propósito, semántica, autoría, catálogo,
corpus, arquitectura, herramientas, historia, decisiones, auditoría y plan de corrección.

- Generado: `2026-09-04`
- Revisión de código base: `ac83a0472921`
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


[**segtem.github.io/oracle**](https://segtem.github.io/oracle/) · [PyPI](https://pypi.org/project/oracle-metalenguaje/) · [0.6.0](https://github.com/Segtem/oracle/releases/tag/v0.6.0)

```bash
uv tool install oracle-metalenguaje
```

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
> **Hoy es un experimento.** La reificación mecánica del catálogo ya está hecha: de la forma canónica
> salen `medida`, `fuente`, `termino`, `requiere` y `paso_de_medida`, y tres medidas meta nuevas se
> escribieron sin tocar Python. El límite siguiente sigue abierto: ningún consumidor escribió todavía
> una medida meta que exija una relación que sus sensores no emitan. Ese disparador, no una fecha, está
> en [`PLAN-LENGUAJE.md`](https://github.com/Segtem/oracle/blob/main/PLAN-LENGUAJE.md).
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

### Instalación

Requiere Python 3.11 o posterior y **no tiene dependencias**: se instala offline, desde un archivo,
sin nada que resolver.

```bash
uv tool install oracle-metalenguaje
oracle --help
```

`uv tool install` crea un entorno aislado del Python del sistema y deja los nueve comandos en el
`PATH`. Es la forma recomendada porque en Arch, Debian 12+, Ubuntu 23.04+ y Fedora un `pip install` al Python del
sistema **falla** con `externally-managed-environment` (PEP 668) — la distribución protege su
Python, y hace bien.

Con `pip`, entonces, va en un entorno propio:

```bash
python3 -m venv venv && source venv/bin/activate
pip install oracle-metalenguaje
```

Y para probarlo sin instalar nada: `uvx --from oracle-metalenguaje oracle --help`.

El catálogo base viaja adentro, así que un proyecto nuevo ya tiene quién lo juzgue:

```bash
oracle init <tu-proyecto>
cd <tu-proyecto>
oracle nueva <dominio.nombre>
oracle test
```

`--confiar-escalares` hace falta sólo si tu proyecto declara funciones propias en `escalares.py`;
sin esa bandera, Oracle no ejecuta código de nadie.

#### Desde el repositorio

Para trabajar sobre el checkout —o para tomar algo que todavía no salió en un release—:

```bash
uv tool install .          # o: python -m pip install -e .
uvx --from . oracle --help # probarlo sin instalar nada
```

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
En este corte hay 9609 líneas de lenguaje y **395 negativas explícitas** (`raise`).
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
Los 101 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 73 la mutación, 20 una persona, 4 la casualidad, 4 una herramienta ajena.
<!-- deteccion:fin -->

Ninguna de esas vías le pregunta al que escribió el código. Oracle no es un juez de artefactos — es
una prótesis para alguien que escribe la herramienta y su test con la misma mano y no recuerda ayer.

#### El costo, dicho

<!-- escala:inicio -->
**9609 líneas de lenguaje** (`nucleo/`, código y macros) y **395 negativas explícitas** (`raise`). Contra las 57 medidas universales escritas en él (406 líneas): **23,7 a 1**. 50 de las 57 pasan por una macro.
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
pago empezó cuando entró la cuarta macro: no hizo falta sumar una rama de Python por forma.

El numerador cuenta `nucleo/macros/` junto con el `.py`, a propósito. Si contara sólo código,
mover Python a datos habría «mejorado» la proporción sin que el lenguaje encogiera un gramo — el
sastreo exacto contra el que esta medición existe.

#### La proporción no alcanza como criterio, y el proyecto es EXPERIMENTAL

Dos auditorías externas la hicieron disparar en contra tres cortes seguidos —16,2 → 18,0 → 18,2— y
la respuesta publicada fue reinterpretarla. El defecto es estructural: los catálogos externos no
entran al denominador, así que la adopción no la mueve; y migrar una política real de Python al
catálogo bajó el núcleo tres líneas sin mover la cifra.

Por eso se publica como **costo**, no como criterio de cierre. Sigue generada por `tools/cifras.py` y
el CI falla si vence, pero Oracle permanece experimental: no tiene fecha de corte, condición de
cierre ni tope de tamaño para el núcleo. La puerta fechada y el tope que existieron durante un día se
retiraron el 2026-08-24: medían un experimento como si ya fuera un producto.

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

### Cinco niveles, una sola representación

```
L2   medidas sobre medidas   enunciados sobre L1                        ✓ se escribe en el lenguaje
L1   medidas                 enunciados sobre L0                        ✓
L0   evidencia               pieza(id, aabb) · evento(t, actor, qué)    ✓
────────────────────────────────────────────────────────────────────────
L−1  qué lee el sensor       su alcance y las unidades de cada campo    ✓ integrado
L−2  qué leyó, y en qué      identidad y frescura del referente         ✓ integrado
────────────────────────────────────────────────────────────────────────
     el terreno              no es un nivel: no se representa
```

Cada nivel es una **representación**, nunca una cosa. L0 no es la escena: son filas. Y bajando vale
igual — L−1 no es el sensor, es lo que el sensor declara de sí mismo; el sensor es a L−1 lo que la
escena es a L0.

**Hacia arriba la torre se cierra en L2.** No porque falte trabajo: porque colapsa. Con el catálogo
reificado como una relación más, una medida sobre medidas sobre medidas se escribe idéntica a una
medida sobre medidas — mismos cinco operadores, misma álgebra. `meta.ninguna_medida_sin_alcance`
juzga las medidas del catálogo, **ella incluida**, y no hace falta un L3 para eso. Y no hay paradoja:
no es un predicado de verdad sobre sí misma, es un cómputo finito sobre una bolsa finita de filas.

Eso es lo que lo vuelve un metalenguaje: no tener L2, sino que **L2 no necesita mecanismo propio**.
Es L1 apuntado a L1.

**Hacia abajo la torre se cierra en L−2**, y ahí el motivo es otro: se acabó lo representable. L−1
pregunta cómo se hizo el mapa; L−2 pregunta si el territorio mapeado es el territorio del que habla
el veredicto. Debajo está el terreno, y lo único honesto que se puede hacer con él es declarar qué
no se miró — que es exactamente el trabajo de `alcance`, el único campo obligatorio del lenguaje.

#### Los dos de abajo ya están habitados

No son terreno virgen: fallan distinto y se arreglan distinto. Las ramas de cierre sacan al
lenguaje las respuestas que antes estaban caso por caso en Python.

| | falla así | ya se contesta acá |
|---|---|---|
| **L−1** | el sensor emite el AABB en centímetros y la medida lo espera en metros: fiel, y el verde miente | declaraciones y derivación integradas |
| **L−2** | el sensor leyó el asset del disco y el juego embarca la variante cocinada: todo cierto sobre otra cosa | `referente_declarado`, `referente_comparado` y la medida de frescura |

Los límites son parte del cierre: L−1 detecta unidades incompatibles pero no convierte ni inventa
equivalencias para escalares variádicas. L−2 no abre el referente ni demuestra que una huella le
pertenezca; compara la huella declarada al leer contra la declarada ahora.

Y los dos campos que un caso ya declara caen uno en cada nivel:

```
origen: {repo, commit}   ← L−2:  qué artefacto, en qué versión
procedencia: observada   ← L−1:  cómo se produjo esta fila
```

Los dos los tipea una persona y **ninguno se verifica**. El `alcance` de
`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` lo dice con todas las letras: *«NO verifica
que el commit exista, ni que la evidencia se corresponda con ese commit, ni que quien escribió
`observada` haya observado algo»*. Es la misma situación en la que estaba L2 antes de reificar el
catálogo, y por eso el orden del trabajo es terminar L2 primero: la maquinaria que lo vuelve
expresable es la que después alcanza a L−1 y L−2.

### Lo que una medida declara, siempre

```
medición   un escalar del mundo
umbral     una comparación — con `segun` y su DEFENSA escrita
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

Y el comando instalado se apunta:

```bash
oracle test --proyecto <tu-proyecto> --confiar-escalares
oracle relaciones --proyecto <tu-proyecto>
oracle revisar catalogos/<dominio>/<dominio.medida>.oracle --proyecto <tu-proyecto> --confiar-escalares
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

### Heredar un catálogo sin quedar en rojo el primer día

Activar `catalogo_base` te da medidas que ven cosas que las tuyas no veían, y por eso mismo te
pone en rojo. Es correcto —esos defectos estaban— pero si la primera experiencia de heredar un
catálogo es que el proyecto entero deja de pasar, no se hereda una segunda vez.

Una medida se puede poner **en sombra**: se evalúa, se reporta, y no hace fallar.

```json
{
  "esquema": "oracle.proyecto/v1",
  "catalogo_base": true,
  "sombra": {
    "meta.todo_umbral_declara_de_donde_sale": {
      "desde": "2026-09-01",
      "porque": "el catálogo se escribió antes de que `segun` existiera; se completa este mes"
    }
  }
}
```

**La sombra no silencia: declara.** Lo que se apaga es la consecuencia, no la medición — el conteo
y la antigüedad se imprimen en cada corrida, así que «lo tengo en sombra hace ocho meses» es un
hecho que se lee, no una comodidad que se olvida.

Y apagar no sale gratis. Cinco medidas vigilan la sombra misma, y **ninguna puede ponerse en sombra
a sí misma**. Tres exigen fecha y motivo, que la medida todavía dé rojo y que el id siga en el
catálogo. Las otras dos hacen envejecer la excepción: `meta.ninguna_sombra_envejece_sin_revisarse`
rechaza las de más de noventa días y `meta.toda_sombra_declara_una_fecha_real` rechaza una fecha
ilegible o futura.

Una biblioteca de políticas lleva esta misma idea fuera del catálogo base sin ejecutar código del
publicador: contiene datos, se activa por proyecto y dos ids iguales fallan cerrado. `oracle
biblioteca listar <ruta>` muestra por medida el umbral, `segun` y el `alcance` completo;
`oracle biblioteca verificar <ruta>` comprueba contenido, corpus y la cifra de mutación publicada.
Certifica esos hechos, no que la política sea correcta para un proyecto.

### Las decisiones, y por qué

Cada una registra una elección que costó discutir, con lo que se descartó y el motivo. Están en la
raíz porque son parte del proyecto, no documentación anexa: cuando algo del diseño parece
arbitrario, la respuesta suele estar acá.

| | |
|---|---|
| [001](https://github.com/Segtem/oracle/blob/main/DECISION-001-RELACIONES-COMO-BOLSAS.md) | Las relaciones son bolsas, no conjuntos |
| [002](https://github.com/Segtem/oracle/blob/main/DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md) | Una medida no compone con otra |
| [003](https://github.com/Segtem/oracle/blob/main/DECISION-003-SIN-PARAMETROS-OPCIONALES-EN-DEFMACRO.md) | Las macros no toman parámetros opcionales |
| [004](https://github.com/Segtem/oracle/blob/main/DECISION-004-DOS-MEDIDAS-QUEDAN-SOSTENIDAS-POR-EVIDENCIA-GENERADA.md) | Dos medidas quedan sostenidas por evidencia generada |
| [005](https://github.com/Segtem/oracle/blob/main/DECISION-005-CINCO-NIVELES-DE-REPRESENTACION.md) | Cinco niveles de representación: L−2 a L2 |
| [006](https://github.com/Segtem/oracle/blob/main/DECISION-006-DE-DONDE-SALE-EL-NUMERO.md) | De dónde sale el número: `segun` |
| [007](https://github.com/Segtem/oracle/blob/main/DECISION-007-BIBLIOTECAS-DE-POLITICAS.md) | Bibliotecas de políticas, con seis correcciones |
| [008](https://github.com/Segtem/oracle/blob/main/DECISION-008-EL-REPOSITORIO-SE-ABRE.md) | El repositorio se abre |
| [009](https://github.com/Segtem/oracle/blob/main/DECISION-009-DE-QUIEN-ES-EL-CASO.md) | De quién es el caso: cada medida declara si mira lo propio o todo |
| [010](https://github.com/Segtem/oracle/blob/main/DECISION-010-EL-PAQUETE-INSTALADO-ES-OTRO-PROYECTO.md) | El paquete instalado es otro proyecto, y hay que medirlo como tal |
| [011](https://github.com/Segtem/oracle/blob/main/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md) | Los mutadores tienen autor, y hasta hoy era uno solo |

### Estado

> **Estado auditado el 2026-07-31; P3 de embedding cerrado del lado de Oracle.** Los bypasses de simulación, baseline, caché,
> equivalentes y verdes vacuos tienen regresiones fail-closed; timeout y error del arnés son estados
> distintos de una muerte. P2.1 ya aísla la mutación de código en una copia, con bloqueo,
> subprocesos acotados y reanudación verificable. El detalle está en
> [`PLAN-CORRECCION.md`](https://github.com/Segtem/oracle/blob/main/PLAN-CORRECCION.md); las dos auditorías externas (Codex gpt-5.5 y
> DeepSeek, agosto 2026) se respondieron en el commit `c81a87c`, y su informe se retiró del
> árbol cuando dejó de tener puntos abiertos.

**El checkout reúne los componentes del experimento.** El [corpus](https://github.com/Segtem/oracle/tree/main/corpus/) (en formato de autoría `.caso` o almacenamiento `.json`), la [especificación](https://github.com/Segtem/oracle/blob/main/ESPECIFICACION.md) del álgebra,
el evaluador (`nucleo/`), **las medidas universales** dentro de [`catalogos/`](https://github.com/Segtem/oracle/tree/main/catalogos/) —como
archivos de datos (`.oracle` y `.json`), no como código—, el sensor de mutación y la prueba diferencial.

**¿Querés escribir una medida?** → [`ESCRIBIR-UNA-MEDIDA.md`](https://github.com/Segtem/oracle/blob/main/ESCRIBIR-UNA-MEDIDA.md).
`oracle relaciones` te dice qué hechos hay para medir; `oracle caso` crea el caso (`.caso`) y
`oracle nueva` crea la medida (`.oracle`). Ambos cargan superficie y JSON por igual.

**¿Vas a escribir una medida acá?** → `oracle contexto` junta en un solo lugar lo que hace falta:
las relaciones que hay con sus campos, con qué se escriben, qué declara toda medida sin excepción, y
las que ya existen para no repetirlas. `--compacto` da lo mismo en un quinto del texto, para pegarlo
en la ventana de un agente: en la medición de este corte, unos 1.600 tokens contra unos 8.600 de los
tres comandos que reemplaza.

**¿Querés la referencia del lenguaje?** → `oracle manual`, `oracle manual medidas`,
`man oracle-segun`, o
[la misma vista en el sitio](https://segtem.github.io/oracle/manual.html). No es un documento
escrito aparte: cada entrada sale de la declaración que el lenguaje ya tiene —los vocabularios
cerrados, las relaciones que emite sobre sí mismo, los verbos del comando—, así que no hay dónde
quede vieja. Lo único que sí podría envejecer —una opción sin explicar, un vocabulario fuera del
registro— lo miden `meta.toda_opcion_del_vocabulario_declara_su_sentido` y
`meta.todo_vocabulario_cerrado_esta_en_el_manual`.

El tema `medidas` enumera las 54 medidas universales y el `alcance` de cada una: qué NO autoriza a
concluir incluso cuando da verde.

La misma referencia sale en tres vistas de una sola fuente: la terminal, el sitio (`--html`) y
páginas de manual (`--man`). `oracle manual --instalar-man ~/.local/share/man` deja `oracle(1)` y
una `oracle-<tema>(7)` por tema, y a partir de ahí `man oracle-etiqueta` funciona sin red.

El wheel distribuye sus archivos bajo `oracle_metalenguaje.*`, pero la fachada todavía registra
`nucleo`, `catalogos` y `perfiles` como nombres de nivel superior para sostener imports absolutos del
núcleo. Ya no registra `tools` al importar la biblioteca: hacerlo le borraba al consumidor su propio
paquete. La colisión con los otros tres nombres sigue siendo posible y está declarada en
[`DECISION-010`](https://github.com/Segtem/oracle/blob/main/DECISION-010-EL-PAQUETE-INSTALADO-ES-OTRO-PROYECTO.md).

El wheel tampoco distribuye el corpus ni los fixtures de autocertificación del checkout. Por eso un
comando instalado fuera de un proyecto requiere `--proyecto` (o `ORACLE_PROYECTO`) y falla si no lo
recibe.

La misma decisión salió de dos consumidores reales, **Jam y LyraGASP**, que usan Oracle desde PyPI.
Encontraron dos defectos desde afuera: el subproceso de UDF no importaba la fachada en una instalación
con `pip install --target`, y la fachada ocupaba el paquete `tools` del consumidor. Los verificadores
anteriores daban verde en ambos casos. El verificador del wheel ahora ejerce tanto un venv como una
instalación vendorizada y los dos defectos se reinyectaron para comprobar que lo hacen fallar.

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
oracle test --proyecto <proyecto> --confiar-escalares  # secuencia completa del consumidor
python -m unittest discover -s tests -t . -q            # suite sin dependencias
python tools/cifras.py                                  # cifras publicadas vigentes
python tools/verificar_instalacion.py                   # wheel + CLI instalado desde un cwd vacío
```

<!-- corpus:inicio -->
**180 casos**: 109 defectos y 71 verdes correctos. De los defectos, 105 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 2 límite humano. Por etiqueta: 104 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño. Por procedencia: 94 observada, 80 construida, 6 generada y 0 sin declarar.
<!-- corpus:fin -->

<!-- cifras:inicio -->
1127 tests · 892/892 mutantes de medida · **5097 sitios de mutación de código** (4887 + 210 del motor Python).
<!-- cifras:fin -->

Los sitios de mutación de código son un denominador, no un resultado. Este README no publica una
ronda vigente sobre todo el denominador publicado arriba. El corte fechado que sí conserva, del 2026-08-25, cubrió
`nucleo/caso.py`: **193 mutantes, 136 muertos, 57 sobrevivientes, 0 timeouts y 0 errores de arnés**.
Además, el camino sin `--objetivo` conserva un timeout conocido; la medición válida se particiona por
objetivo. Ninguno de esos dos límites se convierte en «verde» por el resultado de mutación de medidas.

#### Tres dominios, un álgebra

Es el criterio que decide si esto es general o si es una cosa disfrazada de otra:

| Dominio | Qué mide | Cómo se verifica |
|---|---|---|
| **proceso** | un agente construyendo herramientas: mutantes, afirmaciones, verificaciones vencidas | el corpus de fallas reales |
| **simulación** | corridas, trazas, presupuesto y reproducibilidad | contratos del runner y corpus de trazas |
| **consumidores externos** | geometría, malla, física, recarga y ML deformer | Jam y LyraGASP desde PyPI |

No se parecen en nada, y usan **los mismos operadores sin un solo adaptador**.

La prueba temporal de integración define catálogo, corpus, fixtures y una UDF sin modificar Oracle,
y completa autoría, aceptación, diferencial, mutación de medidas y estudio. Jam y LyraGASP agregaron
la prueba que ese proyecto sintético no podía dar: ambos se conectaron sin tocar una línea de
`nucleo/algebra.py`. Lo único que cruza la frontera son hechos y declaraciones.

Esos archivos usan `oracle.diferencial/v1`. Guardan SHA-256 del emisor, las fuentes de referencia, el
catálogo canónico y la configuración; si alguno cambia, el fixture queda vencido antes de evaluarse.
`referencia_ok` es el acuerdo global independiente. `oracle_al_generar.por_medida` es una fotografía
individual para detectar regresiones compensadas: no se presentan como la misma clase de evidencia.

#### El bucle cerrado

`tools/mutar.py` muta las **medidas** —que son datos, así que no se toca ningún archivo y no hay
`.pyc` que pueda quedar viejo— y produce hechos `mutante(id, apunta_a, murio)`. Esos hechos los juzga
**una medida del catálogo**, `proceso.test_con_mutante_que_lo_mata`. El sensor no dicta veredictos:
produce evidencia, y el álgebra la mide.

Hasta el 2026-09-02 esos mutadores tenían el mismo autor que las medidas y el corpus. Un segundo autor,
aislado del repositorio y con acceso sólo a la especificación y al contrato, escribió **24**. En la
primera corrida el corpus mató **142 de 179 (79%)**; de los sobrevivientes salieron tres huecos reales,
cerrados con casos en el borde. También mostró un límite del catálogo: las 54 medidas universales usan
la misma forma de umbral, `<= 0`, y 17 de sus mutadores no aplicaron a ninguna.

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

Es lo mismo que evaluar un clasificador sólo con positivos. Hoy el corpus incluye la otra polaridad
como casos `verde_correcto`; la cantidad vigente está en el bloque generado de arriba.

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
`ninguno`, `ninguno-requiere`, `ninguno-par` y `peor` expanden a la forma canónica, y `peor` cerró
por construcción la deuda del umbral duplicado. La cobertura vigente sobre el catálogo universal está en
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

`ninguno`, `ninguno-requiere`, `ninguno-par` y `peor` viven en
[`nucleo/macros/`](https://github.com/Segtem/oracle/tree/main/nucleo/macros/) y se cargan por el mismo camino: son la biblioteca estándar del
lenguaje, no un privilegio del núcleo. Un proyecto suma las suyas en `<proyecto>/macros/` y no
necesita tocar nada de Oracle.

Tres decisiones que valen la pena:

- **Las guardas no traen evaluador nuevo.** `ninguno-par` exige que sus dos alias difieran, y una
  plantilla pura no lo expresa. La guarda se sustituye y la evalúa `evaluar_expr` **sobre una fila
  vacía**: una expresión sin accesores nunca toca la fila. De regalo hereda el contrato entero del
  álgebra, incluida la prohibición de igualdad exacta entre flotantes.
- **Una macro puede construir sobre otra**, acotada por `expansiones_maximas`. Negarlo obligaría a
  copiar el cuerpo, que es lo que la macro vino a evitar.
- **Un parámetro que la plantilla nunca usa no se carga.** Es la misma regla que
  `meta.toda_medida_esta_ejercitada`: lo que nadie ejercita es decoración.

**La superficie tiene seis cabezas de tubería.** `desde` la encabeza y no es un paso; los cinco que
ejecutan son `de`, `donde`, `resumen`, `unir` y `agrupar`. Cada uno entró al llegar su disparador.
`con` y la unión izquierda se retiraron: sin dos usuarios reales eran superficie ficticia, no
capacidades.

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

`defmacro` en datos, la reificación mecánica del catálogo, la decisión de no componer medidas, el
evaluador diferencial independiente y las ocho propiedades metamórficas ya están cerrados. Lo abierto
hoy es esto:

- **Adopción ajena.** Jam y LyraGASP consumen el paquete publicado y encontraron dos defectos, pero
  ambos se diseñaron junto con Oracle. Falta un proyecto que no haya compartido ese diseño.
- **El próximo límite de L2.** Ningún consumidor escribió una medida meta que necesite una relación
  nueva. Hasta que ocurra, no se sabe si la reificación alcanza fuera de las preguntas de este autor.
- **La frontera del paquete instalado.** La fachada todavía ocupa `nucleo`, `catalogos` y `perfiles`.
  Además, `oracle_metalenguaje/__init__.py` y `tools/__init__.py` tienen conducta pero están excluidos
  de la mutación de código junto con los `__init__.py` vacíos.
- **El denominador de mutación sigue teniendo autor.** Hay dos, no muchos. El mutador
  `convertir_conteo_en_existencia` está excluido porque con los 54 umbrales `<= 0` es equivalente;
  no hay una alarma que lo reincorpore si aparece otra forma de umbral.
- **La frontera humana del caso `011`.** La medición puede exigir trazabilidad, pero una atribución
  causal no tiene un verificador mecánico genérico. `004` y `012` están resueltos y no inflan la deuda.

### Por qué el corpus va primero

Porque es lo único que se pierde. Un LLM no recuerda sus fallas entre sesiones, y si el corpus se
escribe *después* del framework, se escribe para que pase. Los casos que hay acá se capturaron el
mismo día en que ocurrieron, antes de existir nada que los midiera.

---

<!-- fuente: 01-el-algebra.md -->

## Especificación del álgebra

Versión `0.6`, declarada de forma **legible por máquina** en `nucleo/version.py`
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
> **(d)** La 0.4 hace explícito de dónde sale cada umbral con el campo `segun`: medición,
> contrato, convención o tanteo.
> **(e)** La 0.5 permite que una escalar declare la unidad de cada argumento; una declaración vieja
> sigue cargando, pero su unidad no se considera derivable hasta completar ese dato.
> **(f)** La 0.6 permite declarar el `ambito` opcional de una medida; una medida vieja conserva
> `sin_declarar`, pero una implementación del álgebra completo tiene que conocer el nodo nuevo.

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
volver a verificarse. De `0.2` a `0.3` subió la menor (entraron `agrupar`, `requiere` y `clave`);
de `0.3` a `0.4` volvió a subir porque el umbral ganó `segun`.
De `0.4` a `0.5` subió porque `@escalar` ganó `unidades_argumentos`.
De `0.5` a `0.6` subió porque la forma canónica de una medida ganó el nodo opcional `ambito`.

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
la menor anterior se sigue leyendo idéntico. De `0.1` a `0.2` subió porque la superficie infija
ganó la cláusula `ambito`.

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

#### 1.1 Las relaciones que el lenguaje emite

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
| `requiere` | qué relaciones declara necesitar una medida para concluir | `nucleo/medida.py` |
| `caso` | cada caso del corpus: su polaridad, su `procedencia`, si su medida existe, y —desde `DECISION-009`— si es propio o de una biblioteca | `nucleo/marco.py` |
| `medida_en_uso` | cuántos casos evalúan cada medida y cuántos mutantes le sobreviven | `nucleo/marco.py` |
| `sombra` | qué medidas heredadas se miden pero todavía no obligan, desde cuándo, por qué y hace cuántos días | `nucleo/marco.py` |
| `relacion_documentada` | si cada relación del lenguaje está nombrada en esta especificación | `nucleo/marco.py` |
| `verbo_del_cli` | cada verbo que el comando acepta y si la ayuda lo nombra | `nucleo/marco.py` |
| `opcion_del_vocabulario` | cada opción de un vocabulario cerrado, con cuántas palabras la explican y si el manual la muestra | `nucleo/marco.py` |
| `mutador_excluido` | cada exclusión de mutador declarada, con su premisa, si algún autor ofrece el mutador y si el registro del arnés lo tiene | `nucleo/marco.py` |
| `relacion_declarada` · `campo_declarado` · `ambito_de_relacion` | las relaciones que un proyecto declara, sus campos con unidad y dónde obliga cada relación | `nucleo/relacion.py` |
| `cantidad_comparada` | cada comparación de una medida y si su unidad se puede derivar (L−1) | `nucleo/unidad.py` |
| `referente_declarado` · `referente_comparado` | la identidad y la frescura de aquello que se midió (L−2) | `nucleo/referente.py` |
| `equivalencia` | dos formas que deberían dar lo mismo, para las propiedades metamórficas | `tools/metamorficas.py` |
| `paso` · `producto` · `ancestro` | lo que una evaluación trazada produjo: cada paso, el tamaño del producto de un `unir`, y la ascendencia de un nodo | `nucleo/algebra.py` |
| `campo_diagnostico` | cada valor de texto del diagnóstico local y si contiene algo del dominio | `nucleo/diagnostico.py` |

**Ninguna de estas relaciones se declara en `relaciones/`.** Un proyecto que definiera una con el
mismo nombre estaría pisando una del lenguaje, y por eso los nombres se reservan.

#### 1.2 Los vocabularios cerrados, y el manual que sale de ellos

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

En la terminología de Shi, Zhang y Cui, *A Programming Paradigm for Spatiotemporal
Composability*, §3.2, `requiere` es un **coefecto**: una especificación de dependencias que se
contrasta contra el contexto disponible antes de ejecutar. Oracle toma sólo esa mitad declarativa.
No toma la reactividad del paper —clasificar cada cambio del contexto para activar y desactivar
componentes— porque la evidencia no cambia durante una evaluación; si falta una relación, se corta
fail-closed con `SIN EVIDENCIA`.

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

### 4. Los tres niveles con un solo mecanismo

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

### Instalación

Requiere Python 3.11 o posterior y no tiene dependencias de runtime. Desde el checkout de Oracle, la
forma principal de instalar el comando es:

```bash
uv tool install .
oracle --help
```

Para probarlo sin instalar:

```bash
uvx --from . oracle --help
```

Si no tenés `uv`, hace falta un entorno virtual. Un `pip install` al Python del sistema
**falla** en Arch, Debian 12+, Ubuntu 23.04+ y Fedora con `externally-managed-environment`, y
saltearse esa protección rompe paquetes del sistema:

```bash
python -m venv .venv && . .venv/bin/activate
python -m pip install -e .
oracle --help
```

Con `uv` no hace falta nada de esto, y además deja `oracle-lsp` en el PATH, que es lo que el
editor necesita para encontrarlo.

Después trabajás desde tu proyecto o lo pasás explícitamente:

```bash
oracle init <tu-proyecto>
oracle test --proyecto <tu-proyecto> --confiar-escalares
```

### El orden importa: primero el caso, después la medida

**Escribí el caso del corpus antes que la medida.** No es prolijidad:

- una medida escrita primero se escribe para pasar, no para atrapar;
- la herramienta puede decirte si tu medida está mal *formada*, pero **no puede saber qué quisiste
  decir**. Una condición invertida —que selecciona lo que está bien en vez de lo que ofende— pasa
  todas las comprobaciones automáticas. El caso es lo único que lo detecta.

```bash
# 1. el caso: la evidencia del defecto, y que se espera ROJO
#    (el andamio ya nace en superficie .caso, o copiá uno que exista)
oracle caso proceso/0NN-lo-que-paso   # crea corpus/proceso/0NN-lo-que-paso.caso

# 2. mirá con qué contás: el contexto de tu proyecto en un solo comando
oracle contexto           # relaciones, campos, escalares, operadores y medidas existentes
oracle contexto --compacto # lo mismo en un quinto del texto (~1.600 tokens vs ~8.600)
# (o por separado si sólo querés una parte: oracle relaciones / oracle escalares)

# 3. la medida: el andamio ya nace en superficie infija, y el catálogo lo carga tal cual
oracle nueva colocacion.mi_regla     # crea catalogos/colocacion/colocacion.mi_regla.oracle
oracle revisar catalogos/colocacion/colocacion.mi_regla.oracle

# 4. que todo siga cerrando
oracle test    # corpus, sintaxis, aceptación, diferencial si hay fixtures, y mutación de medidas
```

#### `oracle contexto`: el inventario vivo de tu proyecto

`oracle contexto` junta en una sola salida todo lo que hace falta para escribir una medida en el
proyecto donde estás parado:
1. Qué declara toda medida: `umbral <comparador> <número> segun <origen> porque "<defensa>"` y
   `alcance "<punto ciego>"`.
2. Las relaciones con sus campos y tipos derivados de la evidencia que existe.
3. Con qué se escribe: operadores (`agrupar`, `de`, `donde`, `resumen`, `unir`), comparadores,
   lógicos, agregados y escalares declaradas.
4. Las medidas que ya existen en el catálogo con lo que NO ven.
5. La regla de orden: escribir el caso antes que la medida.

Con `--compacto`, la misma salida se emite en un quinto del texto (~1.600 tokens contra ~8.600 de
correr los comandos que reemplaza).

**Por qué complementa esta guía en vez de acortarla:** este documento explica la semántica del
álgebra, el modelo homoicónico en JSON, las macros, los comparadores prohibidos (como la igualdad
flotante) y las reglas de diseño. `oracle contexto` no reemplaza esas explicaciones: entrega el
inventario concreto y vivo del proyecto para no tener que buscar campos o funciones a mano mientras
escribís.

#### Los dos formatos del catálogo y del corpus

El catálogo y el corpus cargan **superficie (`.oracle`, `.caso`) y `.json` por igual**: los
archivos en superficie no necesitan traducirse a nada para funcionar. El mismo id en los dos
formatos es un error que nombra los dos archivos — no gana ninguno, porque un ganador silencioso es
una divergencia esperando.

- `oracle caso <grupo/NNN-descripcion>`: crea el andamio del caso, ya en superficie `.caso`.
- `oracle nueva <dominio.nombre>`: crea el andamio de la medida, ya en superficie `.oracle`.
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
ejecuta en un trabajador separado: el proceso principal sólo recibe metadatos y resultados JSON.

Lo que ese confinamiento **sí** detiene: leer el CONTENIDO de archivos fuera del proyecto, escribir
fuera, abrir red, crear procesos y usar `ctypes`.

Lo que **no** detiene, y conviene saberlo antes de correr un `escalares.py` ajeno: **los metadatos
del sistema de archivos**. Una UDF puede preguntar si existe cualquier ruta, leer tamaños, permisos
y fechas, y devolver eso como resultado. No es un descuido — `os.stat` no emite ningún evento
auditable en CPython, así que el mecanismo no puede verlo — y está declarado en el docstring de
`nucleo/aislamiento/escalares.py` con un test que lo fija.

`--confiar-escalares` es opt-in por esto: la pregunta no es si el sandbox es perfecto, es si confiás
en ese archivo. Si una UDF necesita más autoridad de la que el confinamiento da, no pertenece a una
medida: generá ese dato antes y entregalo como evidencia.

`--relaciones` y `--escalares` sin la bandera son seguros: no ejecutan el archivo externo.

El id tiene una gramática cerrada: `dominio.nombre`, con segmentos en minúsculas ASCII, dígitos o
`_`. No se aceptan rutas ni `..`; el archivo se resuelve y confina debajo de `catalogos/` antes de
crear cualquier directorio.

### La forma corta: las macros

**La mayoría de las medidas del catálogo están escritas como macro.** Son azúcar que expande a la forma
canónica —`oracle expandir <archivo>` te muestra en qué—, así que el evaluador, la mutación y el inventario no se
enteran de que existen.

```oracle
ninguno proceso.test_con_mutante_que_lo_mata:
    relacion mutante
    alias m
    predicado m.detecciones_conductuales == 0 y m.rechazos_del_algebra == 0
    porque "un mutante que sobrevive es un test que no discrimina"
    segun contrato
    ambito universal
    alcance "cuenta mutantes DECLARADOS. NO ve los que nadie escribió"
```

| Macro | Para qué | Cuántas la usan |
|---|---|---|
| `ninguno` | ninguna fila debe cumplir el predicado | 29 |
| `ninguno-requiere` | lo mismo, declarando evidencia indispensable | 4 |
| `ninguno-par` | lo mismo sobre PARES de la misma relación | 0 |
| `peor` | el peor caso de una expresión no pasa de una tolerancia | 0 |

**`peor` recibe la tolerancia una sola vez** y genera con ella el filtro y el umbral:

```oracle
peor snap.grilla:
    relacion pieza
    alias a
    expresion desvio_de_grilla(hecho(a), 100.0)
    tolerancia 1.0
    porque "por debajo de 1 cm el desvío no se ve"
    segun convencion
    ambito universal
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
    umbral <= 0 segun contrato porque "por qué ese número y no otro"
    requiere relacion
    alcance "qué NO ve esta medida"
```

Las piezas obligatorias están por una razón:

- **`umbral` con `segun`** — el número declara de dónde sale: `medicion`, `contrato`, `convencion` o `tanteo`. La prosa de `porque` puede quedar vacía, salvo en un `tanteo`, donde sigue haciendo falta explicar qué se probó.
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
  ["umbral", "<=", 0, "por qué ese número y no otro", "contrato"],
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
    umbral <= 0 segun contrato porque "un mutante que sobrevive es un test que no discrimina: pasa con el código roto"
    alcance "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los que nadie escribió"
```

El 90% de las medidas son así: filtrás lo malo, contás, y el umbral es `<= 0` (un umbral `==` no se usa y está prohibido por `meta.ningun_umbral_de_igualdad`).

#### 2. Medir una magnitud, no contar

```oracle
medida snap.grilla:
    de pieza a
    donde desvio_de_grilla(hecho(a), 100.0) > 1.0
    resumen max(desvio_de_grilla(hecho(a), 100.0))
    umbral <= 1.0 segun convencion porque "por debajo de 1 cm el desvío no se ve"
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
    umbral <= 0 segun contrato porque "un wikilink apunta por NOMBRE y no por ruta: dos homónimos dejan el enlace a cara o cruz"
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

### Cuando la medida no es tuya

Dos cosas que aparecieron después de que este documento se escribiera, y que cambian qué hacés
cuando el rojo viene de una medida que no escribiste vos:

- **`oracle manual`** es la referencia del lenguaje armada de las declaraciones, no escrita aparte.
  Incluye los operadores, orígenes de umbral, etiquetas, relaciones explicadas y el tema `medidas`
  (`oracle manual medidas`), que lista las 54 medidas universales con qué NO ve cada una. Ofrece tres
  vistas de la misma fuente: en terminal, en HTML para el sitio (`--html`), o en formato de páginas
  de manual (`oracle manual --instalar-man <dir>` deja `man oracle(1)` y `man oracle-segun(7)`
  funcionando).
- **La sombra y su envejecimiento.** Si heredás un catálogo y sale rojo en algo real que hoy no vas
  a arreglar, no apagues la medida: declarala en sombra en `oracle.json`, con `desde` y `porque`. Se
  sigue midiendo e informando como `[EN SOMBRA]`, y no tumba la corrida. Los dos campos son
  obligatorios porque **la sombra ahora envejece**:
  - `meta.ninguna_sombra_envejece_sin_revisarse`: si la sombra tiene más de 90 días, la medida
    falla.
  - `meta.toda_sombra_declara_una_fecha_real`: si la fecha no se puede parsear o está en el futuro,
    falla.
  - `meta.ninguna_sombra_ya_en_verde`: prohíbe tener en sombra medidas que ya dan verde.
  - `meta.ninguna_sombra_sobre_una_medida_que_no_existe`: prohíbe sombras huérfanas.
  Ninguna de estas medidas puede ponerse en sombra a sí misma.

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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "agrupar colapsa: una fila por grupo, y los grupos no pueden ser más que las filas que los originaron. Si sale agrandando, está inventando grupos que ninguna fila sostiene, y un agregado sobre un grupo inventado es un número sin evidencia detrás", "contrato"],
  ["ambito", "del_origen"],
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "sin claves hay un solo grupo, así que agregar por grupo y agregar sobre todo tienen que dar el mismo número. Si no coinciden, `agrupar` pierde o inventa filas al colapsar, y todo agregado calculado sobre un grupo así es un número sin evidencia detrás. NO se exigen los mismos testigos, y no es una concesión: un grupo no es un hecho, los hechos se consumieron al agruparse, así que las dos formas señalan cosas distintas a propósito", "contrato"],
  ["ambito", "del_origen"],
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "filtrar por P y después por Q tiene que dejar exactamente las mismas filas que filtrar una vez por «P y Q»: son la misma pregunta escrita de dos maneras. Se exigen las tres coincidencias y no sólo el veredicto, porque las filas que sobreviven al último `donde` SON los testigos, y dos formas que dan el mismo número señalando filas distintas mandan a una persona a mirar el lugar equivocado", "contrato"],
  ["ambito", "del_origen"],
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "un filtro que agrega filas no es un filtro, y los testigos que publica no son los que sobrevivieron: el informe estaría nombrando filas que la medida nunca vio ofender", "contrato"],
  ["ambito", "del_origen"],
  ["alcance", "compara el conteo antes y después de cada `donde` sobre las evaluaciones que se trazaron. NO ve si las filas que quedaron son las correctas —sólo cuántas—, ni cubre una evaluación que no se corrió bajo traza. Si paso viene vacía no hay filtros que agranden la relación y verde es correcto; además trazar.py garantiza pasos trazados por construcción"]
]
```

#### meta.el_caso_reclama_una_medida_que_existe

- **mide sobre** la relación `caso`
- **umbral**: `<= 0`
- **por qué ese número**: un caso que apunta a una medida inexistente no fija nada y nadie se enteraría: pasaría por el corpus como si estuviera cubierto
- **qué NO ve**: mira todos los casos, propios y heredados, y ve el id que cada caso RECLAMA: un caso de biblioteca colgado puede señalar una selección incompleta del proyecto. NO confunde esto con un hueco declarado —un caso sin medida no reclama nada— y NO ve si el id que existe es el adecuado para ese caso. Si caso viene vacía no hay casos que reclamen medidas inexistentes y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar L2

Como está escrita:

```json
[
  "ninguno",
  "meta.el_caso_reclama_una_medida_que_existe",
  "caso",
  "c",
  ["y", ["==", ["campo", "c", "tiene_medida"], true], ["==", ["campo", "c", "medida_existe"], false]],
  "un caso que apunta a una medida inexistente no fija nada y nadie se enteraría: pasaría por el corpus como si estuviera cubierto",
  "contrato",
  "universal",
  "mira todos los casos, propios y heredados, y ve el id que cada caso RECLAMA: un caso de biblioteca colgado puede señalar una selección incompleta del proyecto. NO confunde esto con un hueco declarado —un caso sin medida no reclama nada— y NO ve si el id que existe es el adecuado para ese caso. Si caso viene vacía no hay casos que reclamen medidas inexistentes y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar L2"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.el_caso_reclama_una_medida_que_existe",
  ["desde", ["de", "caso", "c"], ["donde", ["y", ["==", ["campo", "c", "tiene_medida"], true], ["==", ["campo", "c", "medida_existe"], false]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un caso que apunta a una medida inexistente no fija nada y nadie se enteraría: pasaría por el corpus como si estuviera cubierto", "contrato"],
  ["ambito", "universal"],
  ["alcance", "mira todos los casos, propios y heredados, y ve el id que cada caso RECLAMA: un caso de biblioteca colgado puede señalar una selección incompleta del proyecto. NO confunde esto con un hueco declarado —un caso sin medida no reclama nada— y NO ve si el id que existe es el adecuado para ese caso. Si caso viene vacía no hay casos que reclamen medidas inexistentes y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar L2"]
]
```

#### meta.el_caso_se_pone_como_debe

- **mide sobre** la relación `caso`
- **umbral**: `<= 0`
- **por qué ese número**: un caso del corpus es un defecto real observado: si la medida que lo reclama no se pone roja ahí, la medida está mal escrita o falta lenguaje. Y al revés, un caso correcto que se pone rojo es un falso rojo, que enseña a ignorar el verificador
- **qué NO ve**: mira todos los casos, propios y heredados, y compara el veredicto contra la polaridad declarada: que un caso de biblioteca difiera en este entorno informa sobre este entorno. NO ve si el caso está bien etiquetado, ni si la evidencia que trae es la del defecto que dice traer. Si caso viene vacía no hay desacuerdos de polaridad y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar el nivel meta

Como está escrita:

```json
[
  "ninguno",
  "meta.el_caso_se_pone_como_debe",
  "caso",
  "c",
  ["!=", ["campo", "c", "esperado_ok"], ["campo", "c", "dio_ok"]],
  "un caso del corpus es un defecto real observado: si la medida que lo reclama no se pone roja ahí, la medida está mal escrita o falta lenguaje. Y al revés, un caso correcto que se pone rojo es un falso rojo, que enseña a ignorar el verificador",
  "contrato",
  "universal",
  "mira todos los casos, propios y heredados, y compara el veredicto contra la polaridad declarada: que un caso de biblioteca difiera en este entorno informa sobre este entorno. NO ve si el caso está bien etiquetado, ni si la evidencia que trae es la del defecto que dice traer. Si caso viene vacía no hay desacuerdos de polaridad y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar el nivel meta"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.el_caso_se_pone_como_debe",
  ["desde", ["de", "caso", "c"], ["donde", ["!=", ["campo", "c", "esperado_ok"], ["campo", "c", "dio_ok"]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un caso del corpus es un defecto real observado: si la medida que lo reclama no se pone roja ahí, la medida está mal escrita o falta lenguaje. Y al revés, un caso correcto que se pone rojo es un falso rojo, que enseña a ignorar el verificador", "contrato"],
  ["ambito", "universal"],
  ["alcance", "mira todos los casos, propios y heredados, y compara el veredicto contra la polaridad declarada: que un caso de biblioteca difiera en este entorno informa sobre este entorno. NO ve si el caso está bien etiquetado, ni si la evidencia que trae es la del defecto que dice traer. Si caso viene vacía no hay desacuerdos de polaridad y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar el nivel meta"]
]
```

#### meta.el_diagnostico_no_publica_el_dominio

- **mide sobre** la relación `campo_diagnostico`
- **umbral**: `<= 0`
- **por qué ese número**: el diagnóstico existe para pegarse en un issue público: un id de medida, un nombre de archivo o una ruta con el usuario adentro se comparten sin que nadie los mire dos veces, y no se pueden despublicar
- **qué NO ve**: recorre los valores de texto del diagnóstico y los compara contra lo que el proyecto sabe que es suyo —ids de medidas, nombres de archivos, la raíz y el home—. NO detecta un dato del dominio que no esté en esa lista, ni juzga si un campo nuevo debería estar; de eso responde quien lo agrega

Como está escrita:

```json
[
  "ninguno",
  "meta.el_diagnostico_no_publica_el_dominio",
  "campo_diagnostico",
  "d",
  ["==", ["campo", "d", "es_del_dominio"], true],
  "el diagnóstico existe para pegarse en un issue público: un id de medida, un nombre de archivo o una ruta con el usuario adentro se comparten sin que nadie los mire dos veces, y no se pueden despublicar",
  "contrato",
  "del_origen",
  "recorre los valores de texto del diagnóstico y los compara contra lo que el proyecto sabe que es suyo —ids de medidas, nombres de archivos, la raíz y el home—. NO detecta un dato del dominio que no esté en esa lista, ni juzga si un campo nuevo debería estar; de eso responde quien lo agrega"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.el_diagnostico_no_publica_el_dominio",
  ["desde", ["de", "campo_diagnostico", "d"], ["donde", ["==", ["campo", "d", "es_del_dominio"], true]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "el diagnóstico existe para pegarse en un issue público: un id de medida, un nombre de archivo o una ruta con el usuario adentro se comparten sin que nadie los mire dos veces, y no se pueden despublicar", "contrato"],
  ["ambito", "del_origen"],
  ["alcance", "recorre los valores de texto del diagnóstico y los compara contra lo que el proyecto sabe que es suyo —ids de medidas, nombres de archivos, la raíz y el home—. NO detecta un dato del dominio que no esté en esa lista, ni juzga si un campo nuevo debería estar; de eso responde quien lo agrega"]
]
```

#### meta.el_hueco_declarado_explica_por_que

- **mide sobre** la relación `caso`
- **umbral**: `<= 0`
- **por qué ese número**: un caso sin medida y sin explicación es un caso que alguien va a borrar por prolijidad, y con él se va la memoria de lo que el marco todavía no puede medir
- **qué NO ve**: mira sólo casos propios (`es_heredado == false`) y ve que cada caso marcado explícitamente como hueco abierto tenga una explicación; los huecos de una biblioteca responden ante su certificación. NO juzga esa explicación ni confunde casos resueltos o límites humanos con trabajo pendiente. Si caso viene vacía no hay huecos abiertos sin explicar y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción

Como está escrita:

```json
[
  "ninguno",
  "meta.el_hueco_declarado_explica_por_que",
  "caso",
  "c",
  ["y", ["==", ["campo", "c", "es_heredado"], false], ["==", ["campo", "c", "tiene_medida"], false], ["==", ["campo", "c", "es_hueco_abierto"], true], ["==", ["campo", "c", "explica_el_hueco"], false]],
  "un caso sin medida y sin explicación es un caso que alguien va a borrar por prolijidad, y con él se va la memoria de lo que el marco todavía no puede medir",
  "contrato",
  "universal",
  "mira sólo casos propios (`es_heredado == false`) y ve que cada caso marcado explícitamente como hueco abierto tenga una explicación; los huecos de una biblioteca responden ante su certificación. NO juzga esa explicación ni confunde casos resueltos o límites humanos con trabajo pendiente. Si caso viene vacía no hay huecos abiertos sin explicar y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.el_hueco_declarado_explica_por_que",
  ["desde", ["de", "caso", "c"], ["donde", ["y", ["==", ["campo", "c", "es_heredado"], false], ["==", ["campo", "c", "tiene_medida"], false], ["==", ["campo", "c", "es_hueco_abierto"], true], ["==", ["campo", "c", "explica_el_hueco"], false]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un caso sin medida y sin explicación es un caso que alguien va a borrar por prolijidad, y con él se va la memoria de lo que el marco todavía no puede medir", "contrato"],
  ["ambito", "universal"],
  ["alcance", "mira sólo casos propios (`es_heredado == false`) y ve que cada caso marcado explícitamente como hueco abierto tenga una explicación; los huecos de una biblioteca responden ante su certificación. NO juzga esa explicación ni confunde casos resueltos o límites humanos con trabajo pendiente. Si caso viene vacía no hay huecos abiertos sin explicar y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción"]
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
  "convencion",
  "universal",
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
  ["umbral", "<=", 0, "el dominio dice QUÉ se mide y el nivel dice SOBRE QUÉ; mezclarlos hace que una medida del mundo se archive como si fuera del lenguaje, y ahí deja de encontrarla quien la busca", "convencion"],
  ["ambito", "universal"],
  ["alcance", "compara el prefijo del nombre contra la relación de origen. NO ve si el dominio elegido es el correcto, ni si la medida mide lo que dice medir. Si medida viene vacía no hay medidas que confundan nivel con dominio y verde es correcto; además el catálogo evaluado contiene al menos las medidas meta por construcción"]
]
```

#### meta.la_medida_no_se_fija_solo_con_evidencia_fabricada

- **mide sobre** la relación `caso`
- **umbral**: `<= 0`
- **por qué ese número**: una medida cuyos casos son todos fabricados puede estar ajustada a los ejemplos que se escribieron para que pasara, y no a evidencia de algo que ocurrió; el límite es cero y no un margen porque un solo caso observado ya cambia la naturaleza de la fijación
- **qué NO ve**: mira sólo casos propios (`es_heredado == false`), porque la fijación de una biblioteca es responsabilidad de su certificación. De esos casos mira lo que declaran sobre sí mismos. NO verifica que el commit exista, ni que la evidencia se corresponda con ese commit, ni que quien escribió `observada` haya observado algo. Un caso puede mentir en `procedencia` y esta medida no lo ve

Como está escrita:

```json
[
  "medida",
  "meta.la_medida_no_se_fija_solo_con_evidencia_fabricada",
  ["desde", ["de", "caso", "c"], ["donde", ["y", ["==", ["campo", "c", "es_heredado"], false], ["==", ["campo", "c", "tiene_medida"], true]]], ["agrupar", [["medida", ["campo", "c", "medida"]]], [["casos", "contar", 1], ["no_observados", "suma", ["!=", ["campo", "c", "procedencia"], "observada"]]]], ["donde", ["==", ["col", "casos"], ["col", "no_observados"]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una medida cuyos casos son todos fabricados puede estar ajustada a los ejemplos que se escribieron para que pasara, y no a evidencia de algo que ocurrió; el límite es cero y no un margen porque un solo caso observado ya cambia la naturaleza de la fijación", "contrato"],
  ["ambito", "universal"],
  ["alcance", "mira sólo casos propios (`es_heredado == false`), porque la fijación de una biblioteca es responsabilidad de su certificación. De esos casos mira lo que declaran sobre sí mismos. NO verifica que el commit exista, ni que la evidencia se corresponda con ese commit, ni que quien escribió `observada` haya observado algo. Un caso puede mentir en `procedencia` y esta medida no lo ve"]
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "un operando que no se evaluó es un error que no se levantó. La especificación dice que comparar contra un campo ausente levanta error y no devuelve False, porque un False silencioso lo convierte en un verde; cortocircuitar el `y` deshace esa regla justo cuando el primer operando ya decidió, y encima la vuelve dependiente de los datos: la misma medida rota rompe con una evidencia y se esconde con otra", "contrato"],
  ["ambito", "del_origen"],
  ["alcance", "cuenta operandos evaluados contra los declarados en el AST, en cada `y` y cada `o` trazado. NO ve si el valor de cada operando es correcto, y no cubre una evaluación que se corrió sin traza. Si nodo viene vacía no hay cortocircuitos observados y verde es correcto; además trazar.py garantiza nodos trazados por construcción"]
]
```

#### meta.ningun_campo_sin_unidad_declarada

- **mide sobre** la relación `campo_declarado`
- **umbral**: `<= 0`
- **por qué ese número**: un campo cuya unidad no se declaró —ni una magnitud física ni un «sin unidad» explícito— permite que una medida compare magnitudes incompatibles en silencio
- **qué NO ve**: ve si cada campo de `campo_declarado` tiene `tiene_unidad` en false. NO juzga si la unidad declarada es la magnitud física correcta que emite el sensor

Como está escrita:

```json
[
  "ninguno",
  "meta.ningun_campo_sin_unidad_declarada",
  "campo_declarado",
  "c",
  ["==", ["campo", "c", "tiene_unidad"], false],
  "un campo cuya unidad no se declaró —ni una magnitud física ni un «sin unidad» explícito— permite que una medida compare magnitudes incompatibles en silencio",
  "contrato",
  "universal",
  "ve si cada campo de `campo_declarado` tiene `tiene_unidad` en false. NO juzga si la unidad declarada es la magnitud física correcta que emite el sensor"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ningun_campo_sin_unidad_declarada",
  ["desde", ["de", "campo_declarado", "c"], ["donde", ["==", ["campo", "c", "tiene_unidad"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un campo cuya unidad no se declaró —ni una magnitud física ni un «sin unidad» explícito— permite que una medida compare magnitudes incompatibles en silencio", "contrato"],
  ["ambito", "universal"],
  ["alcance", "ve si cada campo de `campo_declarado` tiene `tiene_unidad` en false. NO juzga si la unidad declarada es la magnitud física correcta que emite el sensor"]
]
```

#### meta.ningun_flotante_comparado_por_igualdad_en_un_filtro

- **mide sobre** la relación `ancestro`
- **umbral**: `<= 0`
- **por qué ese número**: un flotante literal comparado con `==` o `!=` dentro de un filtro exige exactitud binaria sobre una cantidad medida: 0.1 más 0.2 no da 0.3, así que el filtro puede aceptar o rechazar por cómo quedó el número en binario y no por el margen que la medida defiende. El límite es cero y no un margen porque una sola igualdad exacta ya vuelve arbitrario el corte
- **qué NO ve**: mira literales flotantes escritos en la forma canónica, cuando son operandos directos de `==` o `!=` y ese comparador está debajo de un `donde`. NO ve un flotante que llega por una escalar ni uno que sale de un campo, NO juzga igualdades exactas fuera de un filtro, y NO mira el umbral final, del que ya se ocupa `meta.ningun_umbral_flotante_de_igualdad`

Como está escrita:

```json
[
  "ninguno-requiere",
  "meta.ningun_flotante_comparado_por_igualdad_en_un_filtro",
  "ancestro",
  "a",
  ["y", ["==", ["campo", "a", "tipo"], "flotante"], ["o", ["==", ["campo", "a", "cabeza_padre"], "=="], ["==", ["campo", "a", "cabeza_padre"], "!="]], ["==", ["campo", "a", "cabeza_ancestro"], "donde"]],
  "un flotante literal comparado con `==` o `!=` dentro de un filtro exige exactitud binaria sobre una cantidad medida: 0.1 más 0.2 no da 0.3, así que el filtro puede aceptar o rechazar por cómo quedó el número en binario y no por el margen que la medida defiende. El límite es cero y no un margen porque una sola igualdad exacta ya vuelve arbitrario el corte",
  "contrato",
  "universal",
  "mira literales flotantes escritos en la forma canónica, cuando son operandos directos de `==` o `!=` y ese comparador está debajo de un `donde`. NO ve un flotante que llega por una escalar ni uno que sale de un campo, NO juzga igualdades exactas fuera de un filtro, y NO mira el umbral final, del que ya se ocupa `meta.ningun_umbral_flotante_de_igualdad`"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ningun_flotante_comparado_por_igualdad_en_un_filtro",
  ["desde", ["de", "ancestro", "a"], ["donde", ["y", ["==", ["campo", "a", "tipo"], "flotante"], ["o", ["==", ["campo", "a", "cabeza_padre"], "=="], ["==", ["campo", "a", "cabeza_padre"], "!="]], ["==", ["campo", "a", "cabeza_ancestro"], "donde"]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un flotante literal comparado con `==` o `!=` dentro de un filtro exige exactitud binaria sobre una cantidad medida: 0.1 más 0.2 no da 0.3, así que el filtro puede aceptar o rechazar por cómo quedó el número en binario y no por el margen que la medida defiende. El límite es cero y no un margen porque una sola igualdad exacta ya vuelve arbitrario el corte", "contrato"],
  ["requiere", "ancestro"],
  ["ambito", "universal"],
  ["alcance", "mira literales flotantes escritos en la forma canónica, cuando son operandos directos de `==` o `!=` y ese comparador está debajo de un `donde`. NO ve un flotante que llega por una escalar ni uno que sale de un campo, NO juzga igualdades exactas fuera de un filtro, y NO mira el umbral final, del que ya se ocupa `meta.ningun_umbral_flotante_de_igualdad`"]
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "un umbral `==` no tiene borde útil para la mutación: un caso pegado al límite no puede distinguir entre una igualdad exacta bien elegida y una tolerancia que faltó escribir como comparación de orden", "contrato"],
  ["ambito", "universal"],
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "un umbral `==` o `!=` sobre un flotante compara cantidades medidas con una exactitud que la representación no garantiza: 0.1+0.2 no es 0.3, y una igualdad exacta ahí es una falsedad silenciosa que se lee como verde. La comparación de orden con tolerancia (`cerca`) deja el margen a la vista y con su defensa", "contrato"],
  ["ambito", "universal"],
  ["alcance", "mira el operador y el tipo del valor final del umbral de cada medida. NO ve igualdades exactas dentro de expresiones o agregados — de ésas se ocupa el álgebra al evaluar — y NO juzga `==` sobre enteros, textos ni booleanos, que se comparan exacto"]
]
```

#### meta.ninguna_evidencia_declara_un_referente_sin_huella

- **mide sobre** la relación `referente_declarado`
- **umbral**: `<= 0`
- **por qué ese número**: una evidencia sin huella no se puede comparar después contra la declaración actual del referente: el sensor tiene que dejar una identidad comprobable desde el momento de la lectura
- **qué NO ve**: mira si cada declaración de `referente_declarado` trae `tiene_huella` en false. NO verifica que el referente exista, que la huella corresponda a él, que quien la escribió haya leído algo ni si sigue vigente; sólo exige la huella necesaria para una comparación posterior

Como está escrita:

```json
[
  "ninguno-requiere",
  "meta.ninguna_evidencia_declara_un_referente_sin_huella",
  "referente_declarado",
  "r",
  ["==", ["campo", "r", "tiene_huella"], false],
  "una evidencia sin huella no se puede comparar después contra la declaración actual del referente: el sensor tiene que dejar una identidad comprobable desde el momento de la lectura",
  "contrato",
  "universal",
  "mira si cada declaración de `referente_declarado` trae `tiene_huella` en false. NO verifica que el referente exista, que la huella corresponda a él, que quien la escribió haya leído algo ni si sigue vigente; sólo exige la huella necesaria para una comparación posterior"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ninguna_evidencia_declara_un_referente_sin_huella",
  ["desde", ["de", "referente_declarado", "r"], ["donde", ["==", ["campo", "r", "tiene_huella"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una evidencia sin huella no se puede comparar después contra la declaración actual del referente: el sensor tiene que dejar una identidad comprobable desde el momento de la lectura", "contrato"],
  ["requiere", "referente_declarado"],
  ["ambito", "universal"],
  ["alcance", "mira si cada declaración de `referente_declarado` trae `tiene_huella` en false. NO verifica que el referente exista, que la huella corresponda a él, que quien la escribió haya leído algo ni si sigue vigente; sólo exige la huella necesaria para una comparación posterior"]
]
```

#### meta.ninguna_evidencia_se_juzga_con_referente_vencido

- **mide sobre** la relación `referente_comparado`
- **umbral**: `<= 0`
- **por qué ese número**: un veredicto sólo habla del referente leído mientras la declaración actual conserve la misma huella; si cambió, la evidencia anterior ya no alcanza para juzgarlo
- **qué NO ve**: compara las dos huellas declaradas para cada identidad en `referente_comparado`. NO verifica que el referente exista, que una huella corresponda a su contenido ni que quien la declaró haya leído algo

Como está escrita:

```json
[
  "ninguno-requiere",
  "meta.ninguna_evidencia_se_juzga_con_referente_vencido",
  "referente_comparado",
  "r",
  ["!=", ["campo", "r", "huella_leida"], ["campo", "r", "huella_actual"]],
  "un veredicto sólo habla del referente leído mientras la declaración actual conserve la misma huella; si cambió, la evidencia anterior ya no alcanza para juzgarlo",
  "contrato",
  "universal",
  "compara las dos huellas declaradas para cada identidad en `referente_comparado`. NO verifica que el referente exista, que una huella corresponda a su contenido ni que quien la declaró haya leído algo"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ninguna_evidencia_se_juzga_con_referente_vencido",
  ["desde", ["de", "referente_comparado", "r"], ["donde", ["!=", ["campo", "r", "huella_leida"], ["campo", "r", "huella_actual"]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un veredicto sólo habla del referente leído mientras la declaración actual conserve la misma huella; si cambió, la evidencia anterior ya no alcanza para juzgarlo", "contrato"],
  ["requiere", "referente_comparado"],
  ["ambito", "universal"],
  ["alcance", "compara las dos huellas declaradas para cada identidad en `referente_comparado`. NO verifica que el referente exista, que una huella corresponda a su contenido ni que quien la declaró haya leído algo"]
]
```

#### meta.ninguna_exclusion_de_mutador_se_aplica_globalmente

- **mide sobre** la relación `mutador_excluido`
- **umbral**: `<= 0`
- **por qué ese número**: un mutador sacado del registro no corre sobre NINGUNA medida, ni siquiera donde la premisa no vale, y el denominador de mutación baja en silencio — medido: la biblioteca de ejemplo publicaba 16 mutantes certificados cuando eran 17. Los dos hechos se cruzan acá y no en el sensor porque hay dos maneras de que un mutador falte y sólo una es un defecto: que alguien lo filtre al construir el registro, o que su módulo no se distribuya. En un consumidor, «mutadores/» no viaja en el paquete y la ausencia no es culpa de nadie
- **qué NO ve**: ve que un mutador que algún autor declara siga estando en el registro del arnés. NO ve que la exclusión por medida esté bien implementada, NO ve que la premisa de la exclusión sea cierta, y NO ve nada sobre un mutador que esta instalación no distribuye

Como está escrita:

```json
[
  "ninguno",
  "meta.ninguna_exclusion_de_mutador_se_aplica_globalmente",
  "mutador_excluido",
  "m",
  ["y", ["==", ["campo", "m", "lo_ofrece_un_autor"], true], ["==", ["campo", "m", "esta_en_el_arnes"], false]],
  "un mutador sacado del registro no corre sobre NINGUNA medida, ni siquiera donde la premisa no vale, y el denominador de mutación baja en silencio — medido: la biblioteca de ejemplo publicaba 16 mutantes certificados cuando eran 17. Los dos hechos se cruzan acá y no en el sensor porque hay dos maneras de que un mutador falte y sólo una es un defecto: que alguien lo filtre al construir el registro, o que su módulo no se distribuya. En un consumidor, «mutadores/» no viaja en el paquete y la ausencia no es culpa de nadie",
  "contrato",
  "del_origen",
  "ve que un mutador que algún autor declara siga estando en el registro del arnés. NO ve que la exclusión por medida esté bien implementada, NO ve que la premisa de la exclusión sea cierta, y NO ve nada sobre un mutador que esta instalación no distribuye"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ninguna_exclusion_de_mutador_se_aplica_globalmente",
  ["desde", ["de", "mutador_excluido", "m"], ["donde", ["y", ["==", ["campo", "m", "lo_ofrece_un_autor"], true], ["==", ["campo", "m", "esta_en_el_arnes"], false]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un mutador sacado del registro no corre sobre NINGUNA medida, ni siquiera donde la premisa no vale, y el denominador de mutación baja en silencio — medido: la biblioteca de ejemplo publicaba 16 mutantes certificados cuando eran 17. Los dos hechos se cruzan acá y no en el sensor porque hay dos maneras de que un mutador falte y sólo una es un defecto: que alguien lo filtre al construir el registro, o que su módulo no se distribuya. En un consumidor, «mutadores/» no viaja en el paquete y la ausencia no es culpa de nadie", "contrato"],
  ["ambito", "del_origen"],
  ["alcance", "ve que un mutador que algún autor declara siga estando en el registro del arnés. NO ve que la exclusión por medida esté bien implementada, NO ve que la premisa de la exclusión sea cierta, y NO ve nada sobre un mutador que esta instalación no distribuye"]
]
```

#### meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: una medida no puede obligar a más proyectos que aquellos donde su evidencia tiene dueño. Si consume una relación que describe la instalación del origen —la configuración del arnés, el manual, la ayuda del CLI— su rojo sólo lo puede arreglar el origen, y declararla universal se lo manda a un consumidor que no tiene remedio. Es la contradicción que DECISION-012 vuelve falsable, y la única que se deriva sin leer prosa. No usa la macro «ninguno» porque cruza tres relaciones y la macro admite una sola fuente
- **qué NO ve**: cruza el ámbito declarado de cada medida con el de las relaciones que consume, por fuente y por requiere. NO demuestra que una medida universal sea realmente universal: no ve una suposición del origen escondida en un literal, ni una convención que sólo explica la prosa, ni —sobre todo— si el receptor tiene de verdad un remedio disponible. Detecta una contradicción derivable, no la pertinencia. Y sólo mira hacia lo ancho: declarar un ámbito más estrecho que las dependencias pierde cobertura y esta medida no lo señala

Como está escrita:

```json
[
  "medida",
  "meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias",
  ["desde", ["unir", ["unir", ["de", "medida", "m"], ["de", "dependencia_de_medida", "d"]], ["de", "ambito_de_relacion", "a"]], ["donde", ["y", ["==", ["campo", "m", "ambito"], "universal"], ["==", ["campo", "d", "medida"], ["campo", "m", "id"]], ["==", ["campo", "a", "relacion"], ["campo", "d", "relacion"]], ["==", ["campo", "a", "ambito"], "del_origen"]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una medida no puede obligar a más proyectos que aquellos donde su evidencia tiene dueño. Si consume una relación que describe la instalación del origen —la configuración del arnés, el manual, la ayuda del CLI— su rojo sólo lo puede arreglar el origen, y declararla universal se lo manda a un consumidor que no tiene remedio. Es la contradicción que DECISION-012 vuelve falsable, y la única que se deriva sin leer prosa. No usa la macro «ninguno» porque cruza tres relaciones y la macro admite una sola fuente", "contrato"],
  ["ambito", "del_origen"],
  ["alcance", "cruza el ámbito declarado de cada medida con el de las relaciones que consume, por fuente y por requiere. NO demuestra que una medida universal sea realmente universal: no ve una suposición del origen escondida en un literal, ni una convención que sólo explica la prosa, ni —sobre todo— si el receptor tiene de verdad un remedio disponible. Detecta una contradicción derivable, no la pertinencia. Y sólo mira hacia lo ancho: declarar un ámbito más estrecho que las dependencias pierde cobertura y esta medida no lo señala"]
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "un verde que no declara qué NO miró se lee como «está bien»: el informe termina enumerando los puntos ciegos de cada medida, y sin `alcance` esa enumeración queda muda justo donde más importa", "contrato"],
  ["ambito", "universal"],
  ["alcance", "ve si el `alcance` está VACÍO. NO impone una fórmula textual ni un idioma, y NO juzga si el punto ciego declarado es el correcto o el completo"]
]
```

#### meta.ninguna_sombra_envejece_sin_revisarse

- **mide sobre** la relación `sombra`
- **umbral**: `<= 0`
- **por qué ese número**: una sombra es una etapa de transición, y lo único que la distingue de apagar la medida es que alguien la vaya a sacar. Noventa días es un trimestre: tiempo de sobra para el arreglo que se pospuso, y poco para que el proyecto se acostumbre a no verla. El número lo eligió el equipo y no salió de medir nada — cambiarlo es una decisión, no la corrección de un error
- **qué NO ve**: cuenta días desde la fecha que la sombra declara. NO juzga si el motivo sigue siendo válido, ni si alguien la miró en el medio, ni si el arreglo avanzó; una sombra revisada ayer y una olvidada hace un año se ven igual si la fecha no cambió. Tampoco ve una fecha que no se pueda leer o que esté en el futuro: eso da días negativos y lo mide `meta.toda_sombra_declara_una_fecha_real`

Como está escrita:

```json
[
  "ninguno",
  "meta.ninguna_sombra_envejece_sin_revisarse",
  "sombra",
  "s",
  [">", ["campo", "s", "dias"], 90],
  "una sombra es una etapa de transición, y lo único que la distingue de apagar la medida es que alguien la vaya a sacar. Noventa días es un trimestre: tiempo de sobra para el arreglo que se pospuso, y poco para que el proyecto se acostumbre a no verla. El número lo eligió el equipo y no salió de medir nada — cambiarlo es una decisión, no la corrección de un error",
  "convencion",
  "universal",
  "cuenta días desde la fecha que la sombra declara. NO juzga si el motivo sigue siendo válido, ni si alguien la miró en el medio, ni si el arreglo avanzó; una sombra revisada ayer y una olvidada hace un año se ven igual si la fecha no cambió. Tampoco ve una fecha que no se pueda leer o que esté en el futuro: eso da días negativos y lo mide `meta.toda_sombra_declara_una_fecha_real`"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ninguna_sombra_envejece_sin_revisarse",
  ["desde", ["de", "sombra", "s"], ["donde", [">", ["campo", "s", "dias"], 90]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una sombra es una etapa de transición, y lo único que la distingue de apagar la medida es que alguien la vaya a sacar. Noventa días es un trimestre: tiempo de sobra para el arreglo que se pospuso, y poco para que el proyecto se acostumbre a no verla. El número lo eligió el equipo y no salió de medir nada — cambiarlo es una decisión, no la corrección de un error", "convencion"],
  ["ambito", "universal"],
  ["alcance", "cuenta días desde la fecha que la sombra declara. NO juzga si el motivo sigue siendo válido, ni si alguien la miró en el medio, ni si el arreglo avanzó; una sombra revisada ayer y una olvidada hace un año se ven igual si la fecha no cambió. Tampoco ve una fecha que no se pueda leer o que esté en el futuro: eso da días negativos y lo mide `meta.toda_sombra_declara_una_fecha_real`"]
]
```

#### meta.ninguna_sombra_sobre_una_medida_que_no_existe

- **mide sobre** la relación `sombra`
- **umbral**: `<= 0`
- **por qué ese número**: una sombra sobre un id que el catálogo no tiene no apaga nada: quedó de un renombre o de una medida que se fue, y su presencia sugiere una protección que no existe
- **qué NO ve**: compara contra el catálogo cargado. NO ve si el id está bien escrito ni sugiere a cuál se parecía

Como está escrita:

```json
[
  "ninguno",
  "meta.ninguna_sombra_sobre_una_medida_que_no_existe",
  "sombra",
  "s",
  ["==", ["campo", "s", "existe"], false],
  "una sombra sobre un id que el catálogo no tiene no apaga nada: quedó de un renombre o de una medida que se fue, y su presencia sugiere una protección que no existe",
  "contrato",
  "universal",
  "compara contra el catálogo cargado. NO ve si el id está bien escrito ni sugiere a cuál se parecía"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ninguna_sombra_sobre_una_medida_que_no_existe",
  ["desde", ["de", "sombra", "s"], ["donde", ["==", ["campo", "s", "existe"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una sombra sobre un id que el catálogo no tiene no apaga nada: quedó de un renombre o de una medida que se fue, y su presencia sugiere una protección que no existe", "contrato"],
  ["ambito", "universal"],
  ["alcance", "compara contra el catálogo cargado. NO ve si el id está bien escrito ni sugiere a cuál se parecía"]
]
```

#### meta.ninguna_sombra_ya_en_verde

- **mide sobre** la relación `sombra`
- **umbral**: `<= 0`
- **por qué ese número**: una medida en sombra que ya da verde no tiene nada que perdonar: dejarla apagada esconde que el proyecto podría estar exigiéndola, y convierte una etapa de transición en un estado permanente
- **qué NO ve**: ve el veredicto de esta corrida. NO ve si el verde es estable ni si vino de evidencia flaca, y NO puede saber si mañana vuelve a ponerse roja

Como está escrita:

```json
[
  "ninguno",
  "meta.ninguna_sombra_ya_en_verde",
  "sombra",
  "s",
  ["==", ["campo", "s", "dio_ok"], true],
  "una medida en sombra que ya da verde no tiene nada que perdonar: dejarla apagada esconde que el proyecto podría estar exigiéndola, y convierte una etapa de transición en un estado permanente",
  "contrato",
  "universal",
  "ve el veredicto de esta corrida. NO ve si el verde es estable ni si vino de evidencia flaca, y NO puede saber si mañana vuelve a ponerse roja"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.ninguna_sombra_ya_en_verde",
  ["desde", ["de", "sombra", "s"], ["donde", ["==", ["campo", "s", "dio_ok"], true]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una medida en sombra que ya da verde no tiene nada que perdonar: dejarla apagada esconde que el proyecto podría estar exigiéndola, y convierte una etapa de transición en un estado permanente", "contrato"],
  ["ambito", "universal"],
  ["alcance", "ve el veredicto de esta corrida. NO ve si el verde es estable ni si vino de evidencia flaca, y NO puede saber si mañana vuelve a ponerse roja"]
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "todo caso generado desde la forma de datos que acepta el corpus debe imprimirse, releerse y reimprimirse sin perder relaciones, valores JSON, prosa ni el nulo de medida", "contrato"],
  ["ambito", "del_origen"],
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "la superficie de casos es reversible sólo si cada caso publicado conserva el JSON de almacenamiento y el texto canónico al imprimirse, releerse y reimprimirse", "contrato"],
  ["ambito", "del_origen"],
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "toda medida aceptada por el álgebra dentro del espacio gramatical cubierto debe ser reversible: imprimirla y releerla produce exactamente el mismo AST JSON y el mismo texto canónico sin pérdida de información", "contrato"],
  ["ambito", "del_origen"],
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "la superficie infija es reversible sólo si el JSON de almacenamiento y el texto canónico sobreviven a la ida y vuelta sin cambio", "contrato"],
  ["ambito", "del_origen"],
  ["alcance", "comprueba las medidas publicadas del catálogo base y perfiles. NO preserva comentarios libres ni demuestra que otra superficie escrita a mano sea la más legible; sólo que la forma canónica impresa por la herramienta vuelve al mismo JSON y al mismo texto. Si equivalencia viene vacía no hay fallas de reversibilidad y verde es correcto; además metamorficas.py comprueba el catálogo por construcción"]
]
```

#### meta.toda_cantidad_comparada_tiene_unidad_derivable

- **mide sobre** la relación `cantidad_comparada`
- **umbral**: `<= 0`
- **por qué ese número**: una medida que compara cantidades cuya unidad no se puede derivar —porque una relación no declaró el campo o una escalar no declaró su unidad de retorno— no puede garantizar que las magnitudes comparadas sean compatibles
- **qué NO ve**: cree lo que la declaración dice y NO verifica que el sensor emita en esa unidad

Como está escrita:

```json
[
  "ninguno-requiere",
  "meta.toda_cantidad_comparada_tiene_unidad_derivable",
  "cantidad_comparada",
  "c",
  ["==", ["campo", "c", "es_derivable"], false],
  "una medida que compara cantidades cuya unidad no se puede derivar —porque una relación no declaró el campo o una escalar no declaró su unidad de retorno— no puede garantizar que las magnitudes comparadas sean compatibles",
  "contrato",
  "universal",
  "cree lo que la declaración dice y NO verifica que el sensor emita en esa unidad"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.toda_cantidad_comparada_tiene_unidad_derivable",
  ["desde", ["de", "cantidad_comparada", "c"], ["donde", ["==", ["campo", "c", "es_derivable"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una medida que compara cantidades cuya unidad no se puede derivar —porque una relación no declaró el campo o una escalar no declaró su unidad de retorno— no puede garantizar que las magnitudes comparadas sean compatibles", "contrato"],
  ["requiere", "cantidad_comparada"],
  ["ambito", "universal"],
  ["alcance", "cree lo que la declaración dice y NO verifica que el sensor emita en esa unidad"]
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
  ["umbral", "<=", 0, "el patrón `unir` más `agrupar` puede convertir una relación necesaria vacía en cero filas y después en verde; declarar `requiere` hace que la medida falle cerrado antes de agregar sobre nada", "contrato"],
  ["requiere", "termino"],
  ["ambito", "universal"],
  ["alcance", "detecta medidas cuya forma canónica contiene `unir` y `agrupar` pero ningún nodo `requiere`. NO demuestra que toda medida con ese patrón sea realmente de ausencia, ni que la relación requerida elegida sea la correcta"]
]
```

#### meta.toda_medida_declara_su_ambito

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: toda medida tiene que declarar dónde obliga: `sin_declarar` es la ausencia visible que dejan las formas viejas o incompletas durante la migración, no una declaración aceptable
- **qué NO ve**: ve que el campo `ambito` esté declarado y no en `sin_declarar`. NO juzga si el ámbito declarado es el correcto: esa segunda pregunta no la contesta ninguna medida

Como está escrita:

```json
[
  "ninguno",
  "meta.toda_medida_declara_su_ambito",
  "medida",
  "m",
  ["==", ["campo", "m", "ambito"], "sin_declarar"],
  "toda medida tiene que declarar dónde obliga: `sin_declarar` es la ausencia visible que dejan las formas viejas o incompletas durante la migración, no una declaración aceptable",
  "contrato",
  "del_origen",
  "ve que el campo `ambito` esté declarado y no en `sin_declarar`. NO juzga si el ámbito declarado es el correcto: esa segunda pregunta no la contesta ninguna medida"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.toda_medida_declara_su_ambito",
  ["desde", ["de", "medida", "m"], ["donde", ["==", ["campo", "m", "ambito"], "sin_declarar"]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "toda medida tiene que declarar dónde obliga: `sin_declarar` es la ausencia visible que dejan las formas viejas o incompletas durante la migración, no una declaración aceptable", "contrato"],
  ["ambito", "del_origen"],
  ["alcance", "ve que el campo `ambito` esté declarado y no en `sin_declarar`. NO juzga si el ámbito declarado es el correcto: esa segunda pregunta no la contesta ninguna medida"]
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "una medida que ningún caso ni fixture evalúa nunca es decoración: está en el catálogo, se cuenta en el informe, y no puede fallar porque nadie la corre", "contrato"],
  ["ambito", "universal"],
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "una medida propia con cero mutantes pasa vacuamente igual que una cuyos mutantes sobreviven: en ambos casos el catálogo la contiene pero la mutación no demuestra que esté fijada", "contrato"],
  ["ambito", "universal"],
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
  ["umbral", "<=", 0, "una medida sin `donde` ni `agrupar` mide la relación completa: puede ser válida como conteo bruto, pero en el catálogo de oráculos suele significar que faltó declarar qué hecho ofende", "convencion"],
  ["requiere", "termino"],
  ["ambito", "universal"],
  ["alcance", "mira la forma declarada y exige al menos un `donde` o un `agrupar`. NO juzga si el filtro discrimina bien, si el agrupamiento tiene la clave correcta ni si un conteo total fue intencional"]
]
```

#### meta.toda_opcion_del_vocabulario_declara_su_sentido

- **mide sobre** la relación `opcion_del_vocabulario`
- **umbral**: `<= 0`
- **por qué ese número**: un vocabulario cerrado es la parte del lenguaje que más se equivoca quien recién llega, porque los cinco nombres se parecen entre sí; una opción explicada en cinco palabras o menos no distingue de las otras cuatro, que es lo único que el lector necesita. El límite es cero: no hay opción que valga la pena tener y no valga la pena explicar
- **qué NO ve**: cuenta palabras, no las lee: NO juzga si la explicación es correcta ni si distingue de verdad. Y NO ve un vocabulario cerrado que no esté en el registro del manual — para eso está `meta.todo_vocabulario_cerrado_esta_en_el_manual`

Como está escrita:

```json
[
  "ninguno-requiere",
  "meta.toda_opcion_del_vocabulario_declara_su_sentido",
  "opcion_del_vocabulario",
  "o",
  ["<=", ["campo", "o", "palabras_del_sentido"], 5],
  "un vocabulario cerrado es la parte del lenguaje que más se equivoca quien recién llega, porque los cinco nombres se parecen entre sí; una opción explicada en cinco palabras o menos no distingue de las otras cuatro, que es lo único que el lector necesita. El límite es cero: no hay opción que valga la pena tener y no valga la pena explicar",
  "convencion",
  "del_origen",
  "cuenta palabras, no las lee: NO juzga si la explicación es correcta ni si distingue de verdad. Y NO ve un vocabulario cerrado que no esté en el registro del manual — para eso está `meta.todo_vocabulario_cerrado_esta_en_el_manual`"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.toda_opcion_del_vocabulario_declara_su_sentido",
  ["desde", ["de", "opcion_del_vocabulario", "o"], ["donde", ["<=", ["campo", "o", "palabras_del_sentido"], 5]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un vocabulario cerrado es la parte del lenguaje que más se equivoca quien recién llega, porque los cinco nombres se parecen entre sí; una opción explicada en cinco palabras o menos no distingue de las otras cuatro, que es lo único que el lector necesita. El límite es cero: no hay opción que valga la pena tener y no valga la pena explicar", "convencion"],
  ["requiere", "opcion_del_vocabulario"],
  ["ambito", "del_origen"],
  ["alcance", "cuenta palabras, no las lee: NO juzga si la explicación es correcta ni si distingue de verdad. Y NO ve un vocabulario cerrado que no esté en el registro del manual — para eso está `meta.todo_vocabulario_cerrado_esta_en_el_manual`"]
]
```

#### meta.toda_relacion_del_lenguaje_esta_en_la_referencia

- **mide sobre** la relación `relacion_documentada`
- **umbral**: `<= 0`
- **por qué ese número**: una relación que el lenguaje emite y la referencia no nombra es una superficie pública que nadie puede aprender a usar salvo leyendo el código; el límite es cero porque cada relación es una que alguien va a necesitar y no va a encontrar
- **qué NO ve**: comprueba que el NOMBRE aparezca en la referencia del propio Oracle. NO juzga si lo que dice de ella es correcto, si está actualizado ni si alcanza para usarla. En un proyecto consumidor la relación viene VACÍA y la medida sale SIN EVIDENCIA en vez de roja: documentar el lenguaje es responsabilidad de quien lo publica, no de quien lo usa

Como está escrita:

```json
[
  "ninguno-requiere",
  "meta.toda_relacion_del_lenguaje_esta_en_la_referencia",
  "relacion_documentada",
  "r",
  ["==", ["campo", "r", "nombrada_en_la_referencia"], false],
  "una relación que el lenguaje emite y la referencia no nombra es una superficie pública que nadie puede aprender a usar salvo leyendo el código; el límite es cero porque cada relación es una que alguien va a necesitar y no va a encontrar",
  "contrato",
  "del_origen",
  "comprueba que el NOMBRE aparezca en la referencia del propio Oracle. NO juzga si lo que dice de ella es correcto, si está actualizado ni si alcanza para usarla. En un proyecto consumidor la relación viene VACÍA y la medida sale SIN EVIDENCIA en vez de roja: documentar el lenguaje es responsabilidad de quien lo publica, no de quien lo usa"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.toda_relacion_del_lenguaje_esta_en_la_referencia",
  ["desde", ["de", "relacion_documentada", "r"], ["donde", ["==", ["campo", "r", "nombrada_en_la_referencia"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una relación que el lenguaje emite y la referencia no nombra es una superficie pública que nadie puede aprender a usar salvo leyendo el código; el límite es cero porque cada relación es una que alguien va a necesitar y no va a encontrar", "contrato"],
  ["requiere", "relacion_documentada"],
  ["ambito", "del_origen"],
  ["alcance", "comprueba que el NOMBRE aparezca en la referencia del propio Oracle. NO juzga si lo que dice de ella es correcto, si está actualizado ni si alcanza para usarla. En un proyecto consumidor la relación viene VACÍA y la medida sale SIN EVIDENCIA en vez de roja: documentar el lenguaje es responsabilidad de quien lo publica, no de quien lo usa"]
]
```

#### meta.toda_sombra_declara_desde_y_porque

- **mide sobre** la relación `sombra`
- **umbral**: `<= 0`
- **por qué ese número**: una sombra sin fecha no se puede envejecer y una sin motivo no se puede discutir: sin las dos, apagar un rojo sale gratis y deja de ser una decisión para pasar a ser una comodidad
- **qué NO ve**: ve si los dos campos están declarados. NO juzga si el motivo es bueno ni si la fecha es cierta, ni ve las medidas que deberían estar en sombra y no se pusieron

Como está escrita:

```json
[
  "ninguno",
  "meta.toda_sombra_declara_desde_y_porque",
  "sombra",
  "s",
  ["o", ["==", ["campo", "s", "declara_desde"], false], ["==", ["campo", "s", "declara_porque"], false]],
  "una sombra sin fecha no se puede envejecer y una sin motivo no se puede discutir: sin las dos, apagar un rojo sale gratis y deja de ser una decisión para pasar a ser una comodidad",
  "contrato",
  "universal",
  "ve si los dos campos están declarados. NO juzga si el motivo es bueno ni si la fecha es cierta, ni ve las medidas que deberían estar en sombra y no se pusieron"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.toda_sombra_declara_desde_y_porque",
  ["desde", ["de", "sombra", "s"], ["donde", ["o", ["==", ["campo", "s", "declara_desde"], false], ["==", ["campo", "s", "declara_porque"], false]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una sombra sin fecha no se puede envejecer y una sin motivo no se puede discutir: sin las dos, apagar un rojo sale gratis y deja de ser una decisión para pasar a ser una comodidad", "contrato"],
  ["ambito", "universal"],
  ["alcance", "ve si los dos campos están declarados. NO juzga si el motivo es bueno ni si la fecha es cierta, ni ve las medidas que deberían estar en sombra y no se pusieron"]
]
```

#### meta.toda_sombra_declara_una_fecha_real

- **mide sobre** la relación `sombra`
- **umbral**: `<= 0`
- **por qué ese número**: `meta.toda_sombra_declara_desde_y_porque` sólo ve que el campo no esté vacío, así que «cuando pueda» y «2027-12-01» pasan las dos. Una fecha que no se puede leer, o que todavía no llegó, deja a la sombra sin edad: no se la puede envejecer, y entonces la medida que la envejece nunca la va a encontrar
- **qué NO ve**: mira los días calculados, que salen negativos por dos motivos distintos: la fecha no se pudo leer, o está en el futuro. NO los distingue — el testigo trae la medida y los días, no la cadena original. Y NO juzga si una fecha legible es la verdadera: alguien puede escribir una de hace un mes sobre una sombra puesta hoy

Como está escrita:

```json
[
  "ninguno",
  "meta.toda_sombra_declara_una_fecha_real",
  "sombra",
  "s",
  ["<", ["campo", "s", "dias"], 0],
  "`meta.toda_sombra_declara_desde_y_porque` sólo ve que el campo no esté vacío, así que «cuando pueda» y «2027-12-01» pasan las dos. Una fecha que no se puede leer, o que todavía no llegó, deja a la sombra sin edad: no se la puede envejecer, y entonces la medida que la envejece nunca la va a encontrar",
  "contrato",
  "universal",
  "mira los días calculados, que salen negativos por dos motivos distintos: la fecha no se pudo leer, o está en el futuro. NO los distingue — el testigo trae la medida y los días, no la cadena original. Y NO juzga si una fecha legible es la verdadera: alguien puede escribir una de hace un mes sobre una sombra puesta hoy"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.toda_sombra_declara_una_fecha_real",
  ["desde", ["de", "sombra", "s"], ["donde", ["<", ["campo", "s", "dias"], 0]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "`meta.toda_sombra_declara_desde_y_porque` sólo ve que el campo no esté vacío, así que «cuando pueda» y «2027-12-01» pasan las dos. Una fecha que no se puede leer, o que todavía no llegó, deja a la sombra sin edad: no se la puede envejecer, y entonces la medida que la envejece nunca la va a encontrar", "contrato"],
  ["ambito", "universal"],
  ["alcance", "mira los días calculados, que salen negativos por dos motivos distintos: la fecha no se pudo leer, o está en el futuro. NO los distingue — el testigo trae la medida y los días, no la cadena original. Y NO juzga si una fecha legible es la verdadera: alguien puede escribir una de hace un mes sobre una sombra puesta hoy"]
]
```

#### meta.todo_tanteo_explica_por_que

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: un tanteo dice que el número se probó hasta que anduvo; sin prosa no queda nada auditable sobre por qué ése y no otro
- **qué NO ve**: ve sólo tanteos con defensa vacía. NO exige prosa a mediciones, contratos ni convenciones, y NO juzga si la explicación escrita alcanza

Como está escrita:

```json
[
  "ninguno",
  "meta.todo_tanteo_explica_por_que",
  "medida",
  "m",
  ["y", ["==", ["campo", "m", "segun"], "tanteo"], ["==", ["campo", "m", "porque"], ""]],
  "un tanteo dice que el número se probó hasta que anduvo; sin prosa no queda nada auditable sobre por qué ése y no otro",
  "contrato",
  "universal",
  "ve sólo tanteos con defensa vacía. NO exige prosa a mediciones, contratos ni convenciones, y NO juzga si la explicación escrita alcanza"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.todo_tanteo_explica_por_que",
  ["desde", ["de", "medida", "m"], ["donde", ["y", ["==", ["campo", "m", "segun"], "tanteo"], ["==", ["campo", "m", "porque"], ""]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un tanteo dice que el número se probó hasta que anduvo; sin prosa no queda nada auditable sobre por qué ése y no otro", "contrato"],
  ["ambito", "universal"],
  ["alcance", "ve sólo tanteos con defensa vacía. NO exige prosa a mediciones, contratos ni convenciones, y NO juzga si la explicación escrita alcanza"]
]
```

#### meta.todo_umbral_declara_de_donde_sale

- **mide sobre** la relación `medida`
- **umbral**: `<= 0`
- **por qué ese número**: todo umbral tiene que declarar de dónde salió su número: `sin_declarar` es la ausencia visible que dejan las formas viejas o incompletas, no una etiqueta aceptable
- **qué NO ve**: ve si la etiqueta `segun` quedó en `sin_declarar`. NO juzga si la etiqueta elegida es verdadera ni si el número está bien defendido

Como está escrita:

```json
[
  "ninguno",
  "meta.todo_umbral_declara_de_donde_sale",
  "medida",
  "m",
  ["==", ["campo", "m", "segun"], "sin_declarar"],
  "todo umbral tiene que declarar de dónde salió su número: `sin_declarar` es la ausencia visible que dejan las formas viejas o incompletas, no una etiqueta aceptable",
  "contrato",
  "universal",
  "ve si la etiqueta `segun` quedó en `sin_declarar`. NO juzga si la etiqueta elegida es verdadera ni si el número está bien defendido"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.todo_umbral_declara_de_donde_sale",
  ["desde", ["de", "medida", "m"], ["donde", ["==", ["campo", "m", "segun"], "sin_declarar"]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "todo umbral tiene que declarar de dónde salió su número: `sin_declarar` es la ausencia visible que dejan las formas viejas o incompletas, no una etiqueta aceptable", "contrato"],
  ["ambito", "universal"],
  ["alcance", "ve si la etiqueta `segun` quedó en `sin_declarar`. NO juzga si la etiqueta elegida es verdadera ni si el número está bien defendido"]
]
```

#### meta.todo_verbo_del_cli_esta_en_la_ayuda

- **mide sobre** la relación `verbo_del_cli`
- **umbral**: `<= 0`
- **por qué ese número**: un verbo que el comando acepta y la ayuda no nombra sólo lo encuentra quien lea el despacho; el límite es cero porque cada uno es una función que ya está escrita, probada y publicada, y que nadie va a usar
- **qué NO ve**: compara contra la ayuda de `oracle --help`, que es lo primero y muchas veces lo único que alguien lee. NO juzga si la descripción es clara ni si los argumentos están explicados, y NO ve un verbo que exista sin estar declarado en VERBOS

Como está escrita:

```json
[
  "ninguno-requiere",
  "meta.todo_verbo_del_cli_esta_en_la_ayuda",
  "verbo_del_cli",
  "v",
  ["==", ["campo", "v", "nombrado_en_la_ayuda"], false],
  "un verbo que el comando acepta y la ayuda no nombra sólo lo encuentra quien lea el despacho; el límite es cero porque cada uno es una función que ya está escrita, probada y publicada, y que nadie va a usar",
  "contrato",
  "del_origen",
  "compara contra la ayuda de `oracle --help`, que es lo primero y muchas veces lo único que alguien lee. NO juzga si la descripción es clara ni si los argumentos están explicados, y NO ve un verbo que exista sin estar declarado en VERBOS"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.todo_verbo_del_cli_esta_en_la_ayuda",
  ["desde", ["de", "verbo_del_cli", "v"], ["donde", ["==", ["campo", "v", "nombrado_en_la_ayuda"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un verbo que el comando acepta y la ayuda no nombra sólo lo encuentra quien lea el despacho; el límite es cero porque cada uno es una función que ya está escrita, probada y publicada, y que nadie va a usar", "contrato"],
  ["requiere", "verbo_del_cli"],
  ["ambito", "del_origen"],
  ["alcance", "compara contra la ayuda de `oracle --help`, que es lo primero y muchas veces lo único que alguien lee. NO juzga si la descripción es clara ni si los argumentos están explicados, y NO ve un verbo que exista sin estar declarado en VERBOS"]
]
```

#### meta.todo_vocabulario_cerrado_esta_en_el_manual

- **mide sobre** la relación `opcion_del_vocabulario`
- **umbral**: `<= 0`
- **por qué ese número**: el manual no es un documento aparte sino una vista de estas mismas declaraciones, y por eso no puede quedar viejo — salvo de una manera: que aparezca un vocabulario nuevo y nadie lo agregue al registro. Ésa es la única grieta, y es exactamente lo que mide esta medida
- **qué NO ve**: mira el registro `VOCABULARIOS` de `tools/manual.py`, no la salida del comando: NO ve si la sección se imprime rota. Y NO puede ver un vocabulario cerrado que no esté ni en el manual ni en el registro de hechos: eso lo atrapa el test que enumera los módulos del núcleo

Como está escrita:

```json
[
  "ninguno-requiere",
  "meta.todo_vocabulario_cerrado_esta_en_el_manual",
  "opcion_del_vocabulario",
  "o",
  ["==", ["campo", "o", "en_el_manual"], false],
  "el manual no es un documento aparte sino una vista de estas mismas declaraciones, y por eso no puede quedar viejo — salvo de una manera: que aparezca un vocabulario nuevo y nadie lo agregue al registro. Ésa es la única grieta, y es exactamente lo que mide esta medida",
  "contrato",
  "del_origen",
  "mira el registro `VOCABULARIOS` de `tools/manual.py`, no la salida del comando: NO ve si la sección se imprime rota. Y NO puede ver un vocabulario cerrado que no esté ni en el manual ni en el registro de hechos: eso lo atrapa el test que enumera los módulos del núcleo"
]
```

En qué se expande:

```json
[
  "medida",
  "meta.todo_vocabulario_cerrado_esta_en_el_manual",
  ["desde", ["de", "opcion_del_vocabulario", "o"], ["donde", ["==", ["campo", "o", "en_el_manual"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "el manual no es un documento aparte sino una vista de estas mismas declaraciones, y por eso no puede quedar viejo — salvo de una manera: que aparezca un vocabulario nuevo y nadie lo agregue al registro. Ésa es la única grieta, y es exactamente lo que mide esta medida", "contrato"],
  ["requiere", "opcion_del_vocabulario"],
  ["ambito", "del_origen"],
  ["alcance", "mira el registro `VOCABULARIOS` de `tools/manual.py`, no la salida del comando: NO ve si la sección se imprime rota. Y NO puede ver un vocabulario cerrado que no esté ni en el manual ni en el registro de hechos: eso lo atrapa el test que enumera los módulos del núcleo"]
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "una macro es azúcar: expande a la forma canónica ANTES de construir la medida, así que el evaluador no debería poder distinguir una de otra. Es la propiedad con más en juego del catálogo — diecinueve de veintidós medidas pasan por una macro, y si alguna expandiera distinto de lo que su autor cree, todo lo escrito con ella mediría otra cosa en silencio y sin que ningún caso lo notara", "contrato"],
  ["ambito", "del_origen"],
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "el producto cartesiano no tiene lado: cada fila lleva los dos alias, así que dar vuelta los operandos sólo cambia el orden en que salen las filas, y el orden de una bolsa no es parte del contrato. Si el veredicto, el valor o los testigos cambian al voltear, el operador está haciendo algo que depende de la posición y eso no es un producto", "contrato"],
  ["ambito", "del_origen"],
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
  "contrato",
  "del_origen",
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
  ["umbral", "<=", 0, "`unir` es el producto cartesiano y nada más: si sale un número distinto de |izquierda| × |derecha|, o perdió pares o los duplicó. Perderlos esconde ofensas y duplicarlos las cuenta dos veces — y con semántica de bolsas eso altera conteos, sumas y promedios sin ninguna alarma", "contrato"],
  ["ambito", "del_origen"],
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "una afirmación de verde sin alcance declarado es una cifra, no algo verificable: se lee como «está bien» y sólo dice «no se rompió lo de antes»", "contrato"],
  ["ambito", "universal"],
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "CPython invalida el .pyc por (mtime, tamaño): mutar y restaurar dentro del mismo segundo deja a Python corriendo el bytecode mutado sobre el código ya restaurado", "contrato"],
  ["ambito", "universal"],
  ["alcance", "ve la corrida que lo declara. NO ve otras formas de caché: módulos ya importados en memoria, o un import hecho por otro test antes de la mutación. Si corrida_mutacion viene vacía significa que no hubo corridas con bytecode caliente en la sesión y verde es correcto"]
]
```

#### proceso.codigo_con_mutante_que_lo_mata

- **mide sobre** la relación `mutante`
- **umbral**: `<= 0`
- **por qué ese número**: un mutante de código que sobrevive es una modificación sintáctica del núcleo que ningún test detecta: la suite completa pasa con el código alterado, lo que demuestra que los tests tienen un punto ciego y no están fijando ese comportamiento. El umbral tiene que ser cero porque tolerar sobrevivientes no declarados equivale a publicar como verificada una base de código cuyo comportamiento real no está garantizado. Un mutante equivalente declarado con su razón escrita no cuenta como sobreviviente porque documenta una decisión explícita, no una omisión de los tests
- **qué NO ve**: cuenta mutantes de código de la ronda cuyo estado fue «pasaron» sin estar declarados como equivalentes. NO ve los mutadores que nadie escribió ni los operadores que el perfil de mutación no contempla: un mutante que no existe no puede sobrevivir. Tampoco juzga por sí sola si la ronda fue concluyente —eso lo mide proceso.ronda_mutacion_concluyente— ni si el bytecode estaba frío. Si mutante viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—

Como está escrita:

```json
[
  "ninguno-requiere",
  "proceso.codigo_con_mutante_que_lo_mata",
  "mutante",
  "m",
  ["y", ["==", ["campo", "m", "estado"], "pasaron"], ["==", ["campo", "m", "equivalente_declarado"], false]],
  "un mutante de código que sobrevive es una modificación sintáctica del núcleo que ningún test detecta: la suite completa pasa con el código alterado, lo que demuestra que los tests tienen un punto ciego y no están fijando ese comportamiento. El umbral tiene que ser cero porque tolerar sobrevivientes no declarados equivale a publicar como verificada una base de código cuyo comportamiento real no está garantizado. Un mutante equivalente declarado con su razón escrita no cuenta como sobreviviente porque documenta una decisión explícita, no una omisión de los tests",
  "contrato",
  "universal",
  "cuenta mutantes de código de la ronda cuyo estado fue «pasaron» sin estar declarados como equivalentes. NO ve los mutadores que nadie escribió ni los operadores que el perfil de mutación no contempla: un mutante que no existe no puede sobrevivir. Tampoco juzga por sí sola si la ronda fue concluyente —eso lo mide proceso.ronda_mutacion_concluyente— ni si el bytecode estaba frío. Si mutante viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—"
]
```

En qué se expande:

```json
[
  "medida",
  "proceso.codigo_con_mutante_que_lo_mata",
  ["desde", ["de", "mutante", "m"], ["donde", ["y", ["==", ["campo", "m", "estado"], "pasaron"], ["==", ["campo", "m", "equivalente_declarado"], false]]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "un mutante de código que sobrevive es una modificación sintáctica del núcleo que ningún test detecta: la suite completa pasa con el código alterado, lo que demuestra que los tests tienen un punto ciego y no están fijando ese comportamiento. El umbral tiene que ser cero porque tolerar sobrevivientes no declarados equivale a publicar como verificada una base de código cuyo comportamiento real no está garantizado. Un mutante equivalente declarado con su razón escrita no cuenta como sobreviviente porque documenta una decisión explícita, no una omisión de los tests", "contrato"],
  ["requiere", "mutante"],
  ["ambito", "universal"],
  ["alcance", "cuenta mutantes de código de la ronda cuyo estado fue «pasaron» sin estar declarados como equivalentes. NO ve los mutadores que nadie escribió ni los operadores que el perfil de mutación no contempla: un mutante que no existe no puede sobrevivir. Tampoco juzga por sí sola si la ronda fue concluyente —eso lo mide proceso.ronda_mutacion_concluyente— ni si el bytecode estaba frío. Si mutante viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—"]
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
  ["umbral", "<=", 0, "un módulo que no se alcanza desde ninguna entrada no lo va a ejecutar nadie, aunque tenga importadores: un racimo entero puede importarse entre sí y estar muerto", "contrato"],
  ["requiere", "alcanzable"],
  ["ambito", "universal"],
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
  ["umbral", "<=", 0, "un módulo entero, con tests en verde y sin un solo importador REAL, está verde y no está en uso. Un test no es un consumidor: prueba que el módulo funciona, no que alguien lo necesite", "contrato"],
  ["requiere", "importa"],
  ["ambito", "universal"],
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "sin mutantes no hay material; un timeout, un error del arnés o una línea base roja dejan la mutación inconclusa: ninguno demuestra que un mutante murió", "contrato"],
  ["ambito", "universal"],
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "reescribir N archivos con una expresión regular puede romper la sintaxis, y comprobar que los N siguen parseando es una línea", "contrato"],
  ["ambito", "universal"],
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina: pasa con el código roto, así que su verde no significa nada. Cuenta como detección cualquiera de las tres formas en que un caso puede notarlo —invertir el veredicto, cambiar los testigos o cambiar el valor— porque las tres son contrato: los testigos son lo que una persona LEE para actuar, y el valor explica cuánto y no sólo de qué lado cayó. Un rechazo del álgebra tampoco deja al mutante vivo, pero es otra cosa y por eso se cuenta aparte: ahí ningún caso discriminó nada, el mutante ni siquiera llegó a evaluar", "contrato"],
  ["ambito", "universal"],
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "un «corrió verde» es una foto con fecha; si después se tocó código vivo la foto es de otro código, y afirmarla es mentir", "contrato"],
  ["ambito", "universal"],
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
  "contrato",
  "universal",
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
  ["umbral", "<=", 0, "un falso rojo enseña a ignorar el verificador, y eso lo vuelve peor que no tener ninguno", "contrato"],
  ["ambito", "universal"],
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
  "ninguno-requiere",
  "simulacion.corrida_reproducible",
  "corrida",
  "c",
  ["==", ["campo", "c", "determinista"], false],
  "una corrida que no se reproduce no puede ser material de corpus: mañana da otra cosa y el caso deja de significar algo. Sin determinismo la simulación no es evidencia, es una anécdota",
  "contrato",
  "universal",
  "compara dos ejecuciones con la MISMA semilla. NO ve si el resultado depende de algo de afuera —la hora, el orden de un diccionario, un archivo— que hoy casualmente no cambió. Si corrida viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—."
]
```

En qué se expande:

```json
[
  "medida",
  "simulacion.corrida_reproducible",
  ["desde", ["de", "corrida", "c"], ["donde", ["==", ["campo", "c", "determinista"], false]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una corrida que no se reproduce no puede ser material de corpus: mañana da otra cosa y el caso deja de significar algo. Sin determinismo la simulación no es evidencia, es una anécdota", "contrato"],
  ["requiere", "corrida"],
  ["ambito", "universal"],
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
  ["umbral", "<=", 0, "una traza con huecos describe otra corrida que la que ocurrió: si faltan pasos, cualquier cosa que se mida sobre ella habla de lo que se registró y no de lo que pasó", "convencion"],
  ["requiere", "evento"],
  ["ambito", "universal"],
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
  "ninguno-requiere",
  "simulacion.no_se_agoto_el_presupuesto",
  "corrida",
  "c",
  ["==", ["campo", "c", "presupuesto_agotado"], true],
  "una corrida que se quedó sin pasos no observó el sistema: observó el presupuesto. Cualquier conclusión que salga de ahí habla de la paciencia del que simuló, no de lo simulado",
  "contrato",
  "universal",
  "ve la clasificación producida por el contrato de terminación. NO ve si el presupuesto era razonable, ni si una corrida que terminó a tiempo lo hizo por el motivo correcto. Si corrida viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—."
]
```

En qué se expande:

```json
[
  "medida",
  "simulacion.no_se_agoto_el_presupuesto",
  ["desde", ["de", "corrida", "c"], ["donde", ["==", ["campo", "c", "presupuesto_agotado"], true]]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "una corrida que se quedó sin pasos no observó el sistema: observó el presupuesto. Cualquier conclusión que salga de ahí habla de la paciencia del que simuló, no de lo simulado", "contrato"],
  ["requiere", "corrida"],
  ["ambito", "universal"],
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
| falso_verde | 104 |
| verde_correcto | 71 |
| deuda_de_diseño | 2 |
| falso_rojo | 2 |
| medida_correcta_conclusion_errada | 1 |

| Cómo se detectó | Cuántos |
|---|---|
| observacion | 79 |
| mutacion | 73 |
| persona | 20 |
| herramienta_ajena | 4 |
| accidente | 4 |

| Procedencia | Cuántos |
|---|---|
| observada | 94 |
| construida | 80 |
| generada | 6 |

**Cada caso registra cómo se detectó.** Una suite verde y una mutación, una persona o
un accidente son señales distintas; mezclarlas borraría justo la evidencia que el
corpus intenta conservar.

### 049-donde-agrego-filas

**Un `donde` que devolvió más filas de las que recibió**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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

### 070-catalogo-real-sin-filtro-ni-grupo

**Tres medidas de un catálogo real contaban la relación entera**

- etiqueta: `falso_verde` · se detectó por: `herramienta_ajena`
- procedencia: `observada`
- medida que lo atrapa: `meta.toda_medida_filtra_o_agrupa`
- de dónde salió: Brianholl/jam · c1fc6e7

**Qué pasó.** En `c1fc6e7` (2026-08-09) el catálogo de un consumidor tenía tres medidas sin `donde` ni `agrupar`: `snap.al_ras`, `snap.comparte_cara` y `scatter.cobertura`. Las tres daban veredicto, y ninguna declaraba qué fila ofende. La consecuencia se midió sobre `scatter.cobertura` con tres filas y una mala: sin filtro devolvía las 3 como testigos, con filtro devuelve 1. Un rojo que señala todo no señala nada. En el mismo commit, `scatter.contencion` y `scatter.interpenetracion` sí tenían `donde`, y son las filas que la medida NO debe marcar.

**Qué se aprendió.** La medida no se escribió contra un ejemplo: se escribió y después encontró esto en un catálogo que llevaba meses en uso, escrito por alguien que sabía lo que hacía. Se arregló en `e2ce848` agregando el filtro. Que las dos medidas sanas del mismo commit estén en la evidencia no es adorno: sin ellas, quitarle el filtro a la medida sobrevive.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "snap.al_ras"}, {"id": "snap.comparte_cara"}, {"id": "scatter.cobertura"}, {"id": "scatter.contencion"}, {"id": "scatter.interpenetracion"}]
  "termino": [{"medida": "snap.al_ras", "cabeza": "desde"}, {"medida": "snap.al_ras", "cabeza": "unir"}, {"medida": "snap.al_ras", "cabeza": "de"}, {"medida": "snap.al_ras", "cabeza": "resumen"}, {"medida": "snap.al_ras", "cabeza": "umbral"}, {"medida": "snap.al_ras", "cabeza": "alcance"}, {"medida": "snap.comparte_cara", "cabeza": "desde"}, {"medida": "snap.comparte_cara", "cabeza": "unir"}, {"medida": "snap.comparte_cara", "cabeza": "de"}, {"medida": "snap.comparte_cara", "cabeza": "resumen"}, {"medida": "snap.comparte_cara", "cabeza": "umbral"}, {"medida": "snap.comparte_cara", "cabeza": "alcance"}, {"medida": "scatter.cobertura", "cabeza": "desde"}, {"medida": "scatter.cobertura", "cabeza": "de"}, {"medida": "scatter.cobertura", "cabeza": "resumen"}, {"medida": "scatter.cobertura", "cabeza": "umbral"}, {"medida": "scatter.cobertura", "cabeza": "alcance"}, {"medida": "scatter.contencion", "cabeza": "desde"}, {"medida": "scatter.contencion", "cabeza": "unir"}, {"medida": "scatter.contencion", "cabeza": "de"}, {"medida": "scatter.contencion", "cabeza": "donde"}, {"medida": "scatter.contencion", "cabeza": "resumen"}, {"medida": "scatter.contencion", "cabeza": "umbral"}, {"medida": "scatter.cont
}
```

### 071-catalogos-reales-sin-umbral-de-igualdad

**Ninguna medida escrita a mano en tres catálogos usa un umbral de igualdad**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ningun_umbral_de_igualdad`
- de dónde salió: Segtem/oracle · 4a4fce9

**Qué pasó.** Transcripción del comparador final de cuatro medidas reales, leídas de los catálogos tal como estaban: dos de `Brianholl/jam` en `535d518`, una de `Brianholl/LyraGASP` en `4a1ccb3` —expandida desde su forma `ninguno`, que canoniza a `<= 0`— y una de este repo. Las cuatro comparan por orden. Se buscó además el contraejemplo en la historia completa de los tres repos y no existe: ninguna medida commiteada usó nunca `==` ni `!=` como comparador de umbral.

**Qué se aprendió.** Un verde transcrito del mundo dice algo que un verde construido no puede decir: que la medida no da falsos rojos sobre las medidas que la gente escribió de verdad, incluidas las que llegan por macro y canonizan su umbral en la expansión.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "snap.al_ras", "comparador": "<="}, {"id": "scatter.cobertura", "comparador": "<="}, {"id": "recarga.root_motion_habilitado", "comparador": "<="}, {"id": "meta.ninguna_medida_sin_alcance", "comparador": "<="}]
}
```

### 072-un-umbral-flotante-real-que-compara-por-orden

**Un umbral flotante real, y compara por orden**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ningun_umbral_flotante_de_igualdad`
- de dónde salió: Brianholl/jam · 535d518

**Qué pasó.** `snap.al_ras` tiene umbral `<= 1.0`: es flotante de verdad, y por eso es la fila que importa. Satisface la mitad izquierda del filtro —el valor es flotante— y no la derecha —el comparador es de orden—, así que una medida que perdiera uno de los dos conjuntos la marcaría. Las otras tres filas son reales y no son flotantes. Leídas de `Brianholl/jam` en `535d518` y de `Brianholl/LyraGASP` en `4a1ccb3`.

**Qué se aprendió.** El caso construido para esta medida podía elegir sus filas; éste no, y aún así trajo el flotante que hacía falta. Un catálogo real de física y geometría tiene umbrales flotantes por necesidad — es el dominio el que los pone, no el ejemplo.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "snap.al_ras", "comparador": "<=", "umbral_es_flotante": true}, {"id": "scatter.cobertura", "comparador": "<=", "umbral_es_flotante": false}, {"id": "recarga.root_motion_habilitado", "comparador": "<=", "umbral_es_flotante": false}, {"id": "ml_deformer.malla_objetivo_fragmentada", "comparador": "<=", "umbral_es_flotante": false}]
}
```

### 073-defensas-y-alcances-reales-no-vacios

**Tres umbrales reales declaran de dónde sale el número**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.todo_umbral_declara_de_donde_sale`
- de dónde salió: Brianholl/jam · 535d518

**Qué pasó.** Tres medidas reales del catálogo migrado declaran `segun` con etiquetas del conjunto cerrado. La prosa puede discutirse, pero el origen del número ya no queda implícito.

**Qué se aprendió.** La migración manual no puede terminar con `sin_declarar` escondido en el catálogo real. Este caso fija un verde observado para que la regla no dependa sólo de ejemplos construidos.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "meta.el_nivel_no_se_confunde_con_el_dominio", "segun": "convencion", "porque": "el dominio dice QUÉ se mide y el nivel dice SOBRE QUÉ; mezclarlos hace que una medida del mundo se archive como si fuera del lenguaje, y ahí deja de encontrarla quien la busca"}, {"id": "proceso.verificacion_vigente", "segun": "contrato", "porque": "un «corrió verde» es una foto con fecha; si después se tocó código vivo la foto es de otro código, y afirmarla es mentir"}, {"id": "simulacion.corrida_reproducible", "segun": "contrato", "porque": "una corrida que no se reproduce no puede ser material de corpus: mañana da otra cosa y el caso deja de significar algo. Sin determinismo la simulación no es evidencia, es una anécdota"}]
}
```

### 074-alcances-reales-declaran-lo-que-no-ven

**Tres alcances reales, y los tres nombran su punto ciego**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ninguna_medida_sin_alcance`
- de dónde salió: Brianholl/jam · 535d518

**Qué pasó.** El `alcance` de tres medidas reales, transcrito entero: dos de `Brianholl/jam` en `535d518` y una de `Brianholl/LyraGASP` en `4a1ccb3`. Ninguno está vacío, y los tres nombran cosas concretas que la medida NO ve —la geometría dentro del AABB, la uniformidad dentro de la celda, las costuras de UV—.

**Qué se aprendió.** La medida sólo comprueba que el texto no esté vacío, y su propio `alcance` lo dice. Lo que este caso agrega es que sobre alcances reales —largos, escritos a mano, en dos idiomas de acentuación distintos— la medida no inventa un rojo.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "snap.al_ras", "alcance": "contacto de las caras sobre el eje solicitado. NO ve si las piezas comparten superficie en los otros dos ejes, ni la geometría real dentro del AABB. Si `pieza` u `objetivo` vienen vacías la medida NO concluye —lo declara en `requiere`— y sale SIN EVIDENCIA en vez de un verde que no miró nada"}, {"id": "scatter.cobertura", "alcance": "fracción de celdas con al menos un centro. NO ve uniformidad dentro de cada celda, distancias entre vecinos, patrones, orientación ni calidad visual. Si `cobertura_scatter` viene vacía la medida NO concluye —lo declara en `requiere`— y sale SIN EVIDENCIA en vez de verde"}, {"id": "ml_deformer.malla_objetivo_fragmentada", "alcance": "ve la cantidad de componentes conexas de la topologia fuente declarada, contadas sobre los triangulos. NO ve vertices huerfanos, NO ve si dos cascaras se tocan geometricamente sin compartir vertices, NO ve la malla de render ni sus LODs, NO ve costuras de UV o de normales"}]
}
```

### 075-las-dos-medidas-reales-de-unir-y-agrupar-declaran-requiere

**Las únicas dos medidas reales que usan `unir` con `agrupar` declaran `requiere`**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.toda_medida_de_ausencia_declara_requiere`
- de dónde salió: Segtem/oracle · 4a4fce9

**Qué pasó.** Barrí los tres catálogos —38 medidas de este repo, 41 de `Brianholl/jam` en `535d518`, 9 de `Brianholl/LyraGASP` en `4a1ccb3`, en las dos superficies— buscando el patrón que la medida persigue: `unir` junto con `agrupar`. Aparece exactamente dos veces, las dos acá, y las dos declaran `requiere`. La tercera fila es histórica y es la que discrimina: `snap.al_ras` en `Brianholl/jam` `c1fc6e7` usaba `unir` sin `agrupar` y sin `requiere` — cumple la mitad del filtro y no la otra, así que una medida a la que le falte un conjunto la marcaría.

**Qué se aprendió.** Que el patrón aparezca dos veces en 88 medidas dice algo sobre la medida: no está fijada por casualidad, está fijada por escasez. Y las dos apariciones son medidas meta de este repo, o sea que hoy la regla se cumple sola porque quien la escribió es quien escribe las únicas medidas a las que se aplica. Cuando un consumidor escriba la primera, ahí se sabrá si sirve.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "meta.toda_medida_de_ausencia_declara_requiere"}, {"id": "meta.toda_medida_filtra_o_agrupa"}, {"id": "snap.al_ras@c1fc6e7"}]
  "termino": [{"medida": "meta.toda_medida_de_ausencia_declara_requiere", "cabeza": "de"}, {"medida": "meta.toda_medida_de_ausencia_declara_requiere", "cabeza": "unir"}, {"medida": "meta.toda_medida_de_ausencia_declara_requiere", "cabeza": "agrupar"}, {"medida": "meta.toda_medida_de_ausencia_declara_requiere", "cabeza": "donde"}, {"medida": "meta.toda_medida_de_ausencia_declara_requiere", "cabeza": "resumen"}, {"medida": "meta.toda_medida_de_ausencia_declara_requiere", "cabeza": "umbral"}, {"medida": "meta.toda_medida_de_ausencia_declara_requiere", "cabeza": "requiere"}, {"medida": "meta.toda_medida_filtra_o_agrupa", "cabeza": "de"}, {"medida": "meta.toda_medida_filtra_o_agrupa", "cabeza": "unir"}, {"medida": "meta.toda_medida_filtra_o_agrupa", "cabeza": "agrupar"}, {"medida": "meta.toda_medida_filtra_o_agrupa", "cabeza": "donde"}, {"medida": "meta.toda_medida_filtra_o_agrupa", "cabeza": "resumen"}, {"medida": "meta.toda_medida_filtra_o_agrupa", "cabeza": "umbral"}, {"medida": "meta.toda_medida_filtra_o_agrupa", "cabeza": "requiere"}, {"medida": "snap.al_ras@c1fc6e7", "cabeza": "desde"}, {"medida": "snap.al_ras@c1fc6e7", "cabeza": "unir"}, {"medida": "snap.al_ras@c1fc6e7", "cabeza": "de"}, {"me
}
```

### 100-donde-no-compone

**Donde no compone**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
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
- procedencia: `observada`
- medida que lo atrapa: `meta.donde_compone`
- de dónde salió: Segtem/oracle · df8cdd2

**Qué pasó.** python tools/metamorficas.py

**Qué se aprendió.** Sin esta polaridad, quitar el filtro por `propiedad` sobrevivía: la medida se pondría roja por una equivalencia que no es la suya. Cada propiedad juzga sólo sus propios hechos.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "donde_compone", "caso": "049-donde-agrego-filas", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "donde_compone", "caso": "050-donde-filtra-como-debe", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "049-donde-agrego-filas", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 102-unir-no-conmuta

**Unir no conmuta**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
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
- procedencia: `observada`
- medida que lo atrapa: `meta.unir_conmuta`
- de dónde salió: Segtem/oracle · df8cdd2

**Qué pasó.** python tools/metamorficas.py

**Qué se aprendió.** Los dos orígenes conviven en la misma relación y el hecho lo declara. Importa: una propiedad comprobada sólo donde el catálogo casualmente la ejercita mide la coincidencia, no la propiedad.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "unir_conmuta", "caso": "061-ausencia-sin-requiere", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "unir_conmuta", "caso": "062-ausencia-cubierta-o-no-aplica", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "049-donde-agrego-filas", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 104-agrupar-sin-claves-difiere

**Agrupar sin claves difiere**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
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
- procedencia: `observada`
- medida que lo atrapa: `meta.agrupar_sin_claves_es_el_resumen_global`
- de dónde salió: Segtem/oracle · df8cdd2

**Qué pasó.** python tools/metamorficas.py

**Qué se aprendió.** Es el caso que impide endurecer la medida por prolijidad. Si alguien agregara `mismos_testigos` al predicado —para que las cuatro propiedades se parezcan— esta medida se pondría roja con el álgebra sana, y un falso rojo enseña a ignorar el verificador.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "049-donde-agrego-filas", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}, {"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "050-donde-filtra-como-debe", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}]
}
```

### 106-macro-expande-distinto

**Macro expande distinto**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
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
- procedencia: `observada`
- medida que lo atrapa: `meta.una_macro_equivale_a_su_expansion`
- de dónde salió: Segtem/oracle · df8cdd2

**Qué pasó.** python tools/metamorficas.py

**Qué se aprendió.** El alcance de esta propiedad tiene un hueco que conviene tener presente: si una macro expandiera SIEMPRE mal de la misma manera, las dos formas coincidirían igual y esta medida callaría. Comprueba que las dos formas sean la misma, no que la forma sea la correcta.

La evidencia, como relaciones:

```json
{
  "equivalencia": [{"propiedad": "una_macro_equivale_a_su_expansion", "caso": "049-donde-agrego-filas", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "una_macro_equivale_a_su_expansion", "caso": "050-donde-filtra-como-debe", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": true}, {"propiedad": "agrupar_sin_claves_es_el_resumen_global", "caso": "049-donde-agrego-filas", "origen": "catalogo", "evaluo": true, "error": "", "mismo_veredicto": true, "mismo_valor": true, "mismos_testigos": false}]
}
```

### 108-donde-compone-un-campo-por-vez

**donde_compone: cada campo del contrato falla por separado**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `construida`
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
- procedencia: `generada`
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
- procedencia: `generada`
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
- procedencia: `generada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `generada`
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
- procedencia: `generada`
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
- procedencia: `construida`
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
- procedencia: `generada`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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

**Un tanteo sin defensa queda sin explicación**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `construida`
- medida que lo atrapa: `meta.todo_tanteo_explica_por_que`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La cabecera estructural de la medida declara `segun` como `tanteo` y trae un `porque` vacío. La etiqueta dice que se probó hasta que anduvo, pero no deja nada auditable sobre por qué ese número y no otro.

**Qué se aprendió.** La prosa dejó de ser obligatoria para todos los umbrales, pero un `tanteo` sin explicación no compra nada: hay que decir qué se probó o por qué se aceptó el corte.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.umbral_tanteado_mudo", "segun": "tanteo", "porque": ""}]
}
```

### 404-umbral-con-defensa

**Un tanteo explicado no ofende**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.todo_tanteo_explica_por_que`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Dos medidas declaran `segun: tanteo` y traen `porque` no vacíos. La regla debe dejarlas pasar: existe algo que discutir, aunque la explicación no sea perfecta.

**Qué se aprendió.** El verde fija la polaridad contraria: la regla no exige una defensa perfecta, sólo que el tanteo no quede mudo. Si la condición se invierte, este caso se pone rojo.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.tanteo_con_defensa", "segun": "tanteo", "porque": "se probó contra tres corridas y éste fue el menor margen estable"}, {"id": "dominio.tanteo_con_otra_defensa", "segun": "tanteo", "porque": "la tolerancia se ajustó hasta dejar de cortar ruido"}]
}
```

### 405-medida-sin-alcance

**Una medida no declara qué NO ve**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `construida`
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
- procedencia: `construida`
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

### 407-medida-solo-con-evidencia-fabricada

**Una medida queda sostenida solo por casos fabricados**

- etiqueta: `falso_verde` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`
- de dónde salió: Segtem/oracle · sesion procedencia 2026-08-26

**Qué pasó.** Una medida queda reclamada por dos casos construidos y ningun caso observado. La medida puede estar bien escrita, pero su verde todavia no dice que haya atrapado algo que ocurrio fuera del ejemplo.

**Qué se aprendió.** Dos casos alcanzan para fijar polaridad y borde: si todos son no observados, la agrupacion por medida tiene que producir un testigo.

La evidencia, como relaciones:

```json
{
  "caso": [{"id": "403-umbral-sin-defensa", "medida": "dominio.regla_solo_fabricada", "tiene_medida": true, "procedencia": "construida", "es_heredado": false}, {"id": "404-umbral-con-defensa", "medida": "dominio.regla_solo_fabricada", "tiene_medida": true, "procedencia": "construida", "es_heredado": false}]
}
```

### 408-medida-con-evidencia-observada

**Un caso observado alcanza para que la medida no quede marcada como fabricada**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`
- de dónde salió: Segtem/oracle · sesion procedencia 2026-08-26

**Qué pasó.** `simulacion.corrida_reproducible` combina un caso observado con un caso construido, y el caso sin medida no debe formar un grupo propio aunque su procedencia no sea observada.

**Qué se aprendió.** La regla no exige que todos los casos propios sean observados: exige que no sean todos fabricados, y que los huecos sin medida no contaminen el agrupamiento.

La evidencia, como relaciones:

```json
{
  "caso": [{"id": "200-corrida-sin-ninguna-corrida", "medida": "simulacion.corrida_reproducible", "tiene_medida": true, "procedencia": "observada", "es_heredado": false}, {"id": "301-simulador-que-ignora-la-semilla", "medida": "simulacion.corrida_reproducible", "tiene_medida": true, "procedencia": "construida", "es_heredado": false}, {"id": "012-umbral-duplicado-en-filtro-y-umbral", "medida": "", "tiene_medida": false, "procedencia": "construida", "es_heredado": false}]
}
```

### 409-flotante-comparado-por-igualdad-en-filtro

**Un filtro compara un flotante literal con igualdad exacta**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ningun_flotante_comparado_por_igualdad_en_un_filtro`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** El literal flotante es operando directo de `==` y ese comparador vive dentro de un `donde`. La medida debe marcarlo aunque el valor concreto parezca inocente.

**Qué se aprendió.** La prohibición necesita ver tres cosas a la vez: tipo flotante, igualdad exacta como padre inmediato y pertenencia a un filtro. Si cualquiera se pierde, este caso deja de ponerse rojo.

La evidencia, como relaciones:

```json
{
  "ancestro": [{"medida": "dominio.filtro_con_igualdad_flotante", "ruta": "2.2.1.2", "ancestro": "2.2.1", "cabeza_ancestro": "==", "tipo": "flotante", "cabeza_padre": "==", "texto": "1.0"}, {"medida": "dominio.filtro_con_igualdad_flotante", "ruta": "2.2.1.2", "ancestro": "2.2", "cabeza_ancestro": "donde", "tipo": "flotante", "cabeza_padre": "==", "texto": "1.0"}]
}
```

### 410-flotante-comparado-por-desigualdad-en-filtro

**Un filtro compara un flotante literal con desigualdad exacta**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ningun_flotante_comparado_por_igualdad_en_un_filtro`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** El literal flotante es operando directo de `!=` dentro de un `donde`. La desigualdad exacta sobre una cantidad medida tiene el mismo problema que la igualdad: depende de representación, no de una tolerancia defendida.

**Qué se aprendió.** `==` y `!=` son dos ramas del mismo riesgo. Un caso por rama evita que una mutación deje media condición sin cubrir.

La evidencia, como relaciones:

```json
{
  "ancestro": [{"medida": "dominio.filtro_con_desigualdad_flotante", "ruta": "2.2.1.2", "ancestro": "2.2.1", "cabeza_ancestro": "!=", "tipo": "flotante", "cabeza_padre": "!=", "texto": "1.0"}, {"medida": "dominio.filtro_con_desigualdad_flotante", "ruta": "2.2.1.2", "ancestro": "2.2", "cabeza_ancestro": "donde", "tipo": "flotante", "cabeza_padre": "!=", "texto": "1.0"}]
}
```

### 411-flotante-en-filtro-sin-ancestro-no-concluye

**Sin relación `ancestro`, la medida no puede concluir**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ningun_flotante_comparado_por_igualdad_en_un_filtro`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** El sensor estructural entregó el término flotante pero no la clausura de ancestría. Sin esa relación, la medida no puede saber si el comparador está dentro de un `donde`.

**Qué se aprendió.** `requiere ancestro` no es decoración: sin esa precondición, un join vacío se leería como cero ofensas y la medida saldría verde sobre evidencia incompleta.

La evidencia, como relaciones:

```json
{
  "ancestro": []
}
```

### 412-catalogo-real-sin-flotante-de-igualdad-en-filtro

**Una fila real del catálogo no es un flotante de igualdad en filtro**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ningun_flotante_comparado_por_igualdad_en_un_filtro`
- de dónde salió: Segtem/oracle · 73f4cc0+worktree

**Qué pasó.** En el catálogo real, `meta.toda_medida_de_ausencia_declara_requiere` tiene un nodo `unir` dentro de su tubería. Esa fila prueba que `termino` y `ancestro` pueden estar presentes sin que haya una ofensa de flotante exacto.

**Qué se aprendió.** El verde no sale de relaciones vacías: hay un término y un ancestro reales, pero no cumplen tipo, padre ni ancestro de filtro. Quitar el filtro de la medida ya no pasa inadvertido.

La evidencia, como relaciones:

```json
{
  "ancestro": [{"medida": "meta.toda_medida_de_ausencia_declara_requiere", "ruta": "2.1", "ancestro": "2", "cabeza_ancestro": "desde", "tipo": "lista", "cabeza_padre": "desde", "texto": ""}, {"medida": "meta.toda_medida_de_ausencia_declara_requiere", "ruta": "2.1", "ancestro": "", "cabeza_ancestro": "medida", "tipo": "lista", "cabeza_padre": "desde", "texto": ""}, {"medida": "meta.toda_medida_filtra_o_agrupa", "ruta": "2.2.1.2.2", "ancestro": "2.2", "cabeza_ancestro": "donde", "tipo": "entero", "cabeza_padre": "==", "texto": "0"}]
}
```

### 413-campo-sin-unidad-declarada

**Un campo de una relación no declara unidad**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ningun_campo_sin_unidad_declarada`
- de dónde salió: Segtem/oracle · 73f4cc0+worktree

**Qué pasó.** Una relación entrega un campo con `tiene_unidad` en false (sin magnitud ni «sin unidad» explícito). Sin unidad declarada, una medida puede comparar números en unidades incompatibles en silencio.

**Qué se aprendió.** Un campo sin unidad no puede pasar desapercibido. La evidencia incluye una fila sana para que la medida no pase con un filtro vacío ni confunda ausencia de ofensa con ausencia de datos.

La evidencia, como relaciones:

```json
{
  "campo_declarado": [{"relacion": "sensor_roto", "campo": "distancia", "tipo": "flotante", "unidad": "", "tiene_unidad": false, "es_magnitud": false, "es_sin_unidad": false}, {"relacion": "sensor_roto", "campo": "id", "tipo": "texto", "unidad": "sin_unidad", "tiene_unidad": true, "es_magnitud": false, "es_sin_unidad": true}]
}
```

### 414-campo-con-unidad-declarada

**Los campos con magnitud o con «sin_unidad» explícito no ofenden**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ningun_campo_sin_unidad_declarada`
- de dónde salió: Segtem/oracle · 73f4cc0+worktree

**Qué pasó.** La relación real `pieza` declara magnitudes físicas (`cm`, `grados`) y campos sin magnitud física con `sin_unidad` explícito. Todos tienen `tiene_unidad` en true y la regla debe dar verde.

**Qué se aprendió.** El verde cubre las dos formas válidas de declarar unidad en L−1: magnitudes con dimensión física explícita y campos adimensionales con `sin_unidad`.

La evidencia, como relaciones:

```json
{
  "campo_declarado": [{"relacion": "pieza", "campo": "id", "tipo": "texto", "unidad": "sin_unidad", "tiene_unidad": true, "es_magnitud": false, "es_sin_unidad": true}, {"relacion": "pieza", "campo": "ox", "tipo": "flotante", "unidad": "cm", "tiene_unidad": true, "es_magnitud": true, "es_sin_unidad": false}, {"relacion": "pieza", "campo": "yaw", "tipo": "flotante", "unidad": "grados", "tiene_unidad": true, "es_magnitud": true, "es_sin_unidad": false}]
}
```

### 415-umbral-sin-segun

**Un umbral no declara de dónde sale el número**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `construida`
- medida que lo atrapa: `meta.todo_umbral_declara_de_donde_sale`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La relación `medida` trae `segun` en `sin_declarar`. Esa ausencia es visible para que una forma vieja o incompleta se ponga roja, no para aceptarla como categoría.

**Qué se aprendió.** La prosa puede existir y aun así faltar lo evaluable: `segun` contesta de dónde salió el número.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.umbral_sin_origen", "segun": "sin_declarar", "porque": "tiene prosa, pero no etiqueta"}]
}
```

### 416-umbral-con-segun

**Un umbral con origen declarado no ofende**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.todo_umbral_declara_de_donde_sale`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Las medidas declaran `segun` con etiquetas del conjunto cerrado. La regla debe dejarlas pasar aunque alguna no tenga prosa: la ausencia que mira es `sin_declarar`.

**Qué se aprendió.** La regla no exige defensa escrita ni juzga la calidad de la etiqueta: sólo falla cuando el origen del número quedó sin declarar.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.contrato_sin_prosa", "segun": "contrato", "porque": ""}, {"id": "dominio.convencion_con_prosa", "segun": "convencion", "porque": "la costumbre del dominio tolera ese margen"}]
}
```

### 417-tanteos-reales-explicados-o-ausentes

**El catálogo real no tiene tanteos mudos**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.todo_tanteo_explica_por_que`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La migración del catálogo base no produjo ningún `segun: tanteo`; los umbrales reales revisados quedaron como contrato o convención. Por eso la regla de tanteos no debe marcar el catálogo por ausencia de prosa.

**Qué se aprendió.** La regla específica para `tanteo` no reinstala la defensa obligatoria para todos. Si no hay tanteo, o si el origen es contrato/convención/medición, la medida no tiene que ofender.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "meta.toda_medida_filtra_o_agrupa", "segun": "convencion", "porque": "una medida sin `donde` ni `agrupar` mide la relación completa: puede ser válida como conteo bruto, pero en el catálogo de oráculos suele significar que faltó declarar qué hecho ofende"}, {"id": "simulacion.la_traza_no_tiene_huecos", "segun": "convencion", "porque": "una traza con huecos describe otra corrida que la que ocurrió: si faltan pasos, cualquier cosa que se mida sobre ella habla de lo que se registró y no de lo que pasó"}, {"id": "proceso.verificacion_vigente", "segun": "contrato", "porque": "un «corrió verde» es una foto con fecha; si después se tocó código vivo la foto es de otro código, y afirmarla es mentir"}]
}
```

### 420-evidencia-declarada-observada-que-nadie-observo

**Dos casos declararon `procedencia: observada` sobre filas que ninguna corrida produjo**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `observada`
- medida que lo atrapa: `ninguna todavía`
- de dónde salió: Segtem/oracle · fafeeb0

**Qué pasó.** Al implementar `segun`, el agente cerró de paso los dos rojos que `DECISION-004` había declarado imposibles de cerrar. Escribió `corpus/meta/418` y `419` con `procedencia: observada`, `como_se_detecto: observacion` y `origen.commit: "sin-commit"`, transcribiendo filas de `equivalencia` con los casos `catalogo-real-actual`, `catalogo-real-con-macros` y `corpus-real-actual`, todas con `origen: "catalogo"`. Ninguna de las tres existe: `tools/metamorficas.py` sigue reportando `sintaxis_cubre_algebra 94 (94 construidas, 0 del catálogo)` y `sintaxis_casos_cubre_casos 5 (5 construidas, 0 del catálogo)`. Los nombres se inventaron. Con eso `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` pasó de 2 a 0 y `aceptacion.py` se puso en verde por primera vez en semanas.

**Qué se aprendió.** Este caso estuvo tres días mal puesto y lo encontró el propio marco: se había etiquetado `falso_verde` nombrando a la medida meta, o sea afirmando «acá tiene que dar rojo», y da verde. `meta.el_caso_se_pone_como_debe` lo marcó el 2026-08-31. La etiqueta estaba bien —es un verde que miente— pero el caso no prueba una medida: documenta un hueco donde no hay ninguna. La medida no puede ver esto, y su propio `alcance` lo dice desde el día que se escribió: «NO verifica que el commit exista, ni que la evidencia se corresponda con ese commit, ni que quien escribió `observada` haya observado algo». Acá el alcance declarado dejó de ser prosa defensiva y describió el defecto exacto antes de que ocurriera. Lo que lo detectó fue una persona cruzando las filas transcritas contra una corrida real — el mismo cruce que ya se había hecho el 2026-08-27 con las once filas de las propiedades metamórficas, que sí existían. Un verde que aparece justo donde una decisión escrita dice que no puede aparecer merece que lo comprueben antes de festejarlo.

**Límite humano.** Ninguna medida atrapa esto, y no por descuido: la única candidata —`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`— da VERDE sobre esta misma evidencia, porque las filas falsas decían `observada` y eso es exactamente lo que ella lee. Su `alcance` lo declara desde el día que se escribió: «NO verifica que el commit exista, ni que la evidencia se corresponda con ese commit, ni que quien escribió `observada` haya observado algo». Lo detectó una persona cruzando las filas transcritas contra una corrida real de la herramienta que las produce. Ese cruce no se puede escribir como medida sin que Oracle sepa ejecutar el productor de cada relación, que es un mecanismo que no tiene.

La evidencia, como relaciones:

```json
{
  "caso": [{"id": "418-sintaxis-cubre-algebra-catalogo-real", "medida": "meta.sintaxis_cubre_algebra", "procedencia": "observada", "tiene_medida": true}, {"id": "419-sintaxis-casos-cubre-casos-corpus-real", "medida": "meta.sintaxis_casos_cubre_casos", "procedencia": "observada", "tiene_medida": true}, {"id": "124-sintaxis-cubre-algebra-no-vuelve-igual", "medida": "meta.sintaxis_cubre_algebra", "procedencia": "generada", "tiene_medida": true}, {"id": "125-sintaxis-cubre-algebra-vuelve-exacta", "medida": "meta.sintaxis_cubre_algebra", "procedencia": "generada", "tiene_medida": true}]
}
```

### 421-cantidad-comparada-sin-unidad-derivable

**Una medida compara una cantidad cuya unidad no se puede derivar**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_cantidad_comparada_tiene_unidad_derivable`
- de dónde salió: Segtem/oracle · l1-derivar

**Qué pasó.** Una medida compara un campo o escalar cuya unidad no fue declarada, por lo que `es_derivable` es false. Sin unidad derivable, una medida puede comparar magnitudes incompatibles en silencio.

**Qué se aprendió.** Una cantidad comparada sin unidad derivable no puede pasar desapercibida. La evidencia incluye una fila válida para que la medida no pase con un filtro vacío ni confunda ausencia de ofensa con ausencia de datos.

La evidencia, como relaciones:

```json
{
  "cantidad_comparada": [{"medida": "simulacion.roto", "unidad": "sin_declarar", "es_derivable": false}, {"medida": "simulacion.sana", "unidad": "cm", "es_derivable": true}]
}
```

### 422-cantidad-comparada-con-unidad-derivable

**Las medidas comparan cantidades con unidad derivable**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.toda_cantidad_comparada_tiene_unidad_derivable`
- de dónde salió: Segtem/oracle · l1-derivar

**Qué pasó.** Las comparaciones usan campos sin unidad física del proceso o agregados adimensionales (`contar`). Ambos tienen `es_derivable` en true y la regla debe dar verde.

**Qué se aprendió.** Cubre dos casos válidos observados en el catálogo propio: campos sin unidad física y conteos adimensionales.

La evidencia, como relaciones:

```json
{
  "cantidad_comparada": [{"medida": "simulacion.corrida_reproducible", "unidad": "sin_unidad", "es_derivable": true}, {"medida": "meta.ninguna_medida_sin_alcance", "unidad": "adimensional", "es_derivable": true}]
}
```

### 423-sin-cantidad-comparada-no-concluye

**Sin relación `cantidad_comparada`, la medida no puede concluir**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_cantidad_comparada_tiene_unidad_derivable`
- de dónde salió: Segtem/oracle · l1-derivar

**Qué pasó.** El sensor de unidades no entregó la relación `cantidad_comparada`. Sin esa relación, la medida no puede saber si las cantidades comparadas tienen unidades derivables y no debe concluir en verde.

**Qué se aprendió.** `requiere cantidad_comparada` no es decoración: sin esa precondición, una relación ausente se leería como cero ofensas y la medida saldría verde sobre evidencia vacía.

La evidencia, como relaciones:

```json
{
  "cantidad_comparada": []
}
```

### 424-referente-sin-huella

**Una evidencia declara un referente sin huella**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_evidencia_declara_un_referente_sin_huella`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La declaración identifica qué se leyó y cuándo, pero deja vacía la huella. Si después no hay una huella para comparar, una evidencia sobre una variante equivocada puede parecer vigente.

**Qué se aprendió.** La relación conserva la huella vacía como un hecho y la medida la pone en rojo. No hace falta ni corresponde abrir el referente desde Oracle.

La evidencia, como relaciones:

```json
{
  "referente_declarado": [{"que": "Content/Props/silla.uasset", "huella": "", "cuando": "2026-08-27T09:14:00", "tiene_huella": false}, {"que": "Content/Props/mesa.uasset", "huella": "sha256:abc", "cuando": "2026-08-27T09:14:01", "tiene_huella": true}]
}
```

### 425-referentes-con-huella

**Las evidencias declaran la huella de cada referente**

- etiqueta: `verde_correcto` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_evidencia_declara_un_referente_sin_huella`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Cada referente trae una huella declarada al momento de la lectura. La medida debe dejar pasar la relación aunque no pueda comprobar el contenido del archivo. Las filas son CONSTRUIDAS y salen de `tests/test_referente.py`: `sha256:abc` no es una huella, es un marcador de ocho caracteres. Se marcó `observada` por error al escribirlo y se corrigió el 2026-08-31 cruzándolo contra las corridas reales; ningún sensor de este repo produce todavía un `referente_declarado`.

**Qué se aprendió.** La regla sólo pide la huella declarada. La existencia, correspondencia y lectura efectiva quedan en el alcance explícito.

La evidencia, como relaciones:

```json
{
  "referente_declarado": [{"que": "Content/Props/mesa.uasset", "huella": "sha256:def", "cuando": "2026-08-27T09:14:01", "tiene_huella": true}, {"que": "Content/Props/silla.uasset", "huella": "sha256:abc", "cuando": "2026-08-27T09:14:00", "tiene_huella": true}]
}
```

### 426-referente-sin-evidencia-no-concluye

**Sin declaraciones de referente la medida no concluye**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_evidencia_declara_un_referente_sin_huella`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** El sensor no entregó la relación que la medida necesita. Si la medida agrega sobre esa ausencia, el cero puede parecer prueba de que ninguna evidencia quedó sin huella.

**Qué se aprendió.** El nodo `requiere referente_declarado` hace que la ausencia sea un no-veredicto. Este borde mata la mutación que lo quita y evita confundir cero filas con ningún referente sin huella.

La evidencia, como relaciones:

```json
{
  "otra_evidencia": [{"nombre": "sensor sin referente"}]
}
```

### 427-referente-cambio-despues-de-leer

**El referente cambió después de producir la evidencia**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_evidencia_se_juzga_con_referente_vencido`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La evidencia fue producida con una huella anterior y la declaración actual ya tiene otra. Sin comparar ambas, un veredicto sobre datos vencidos parece vigente.

**Qué se aprendió.** La comparación vive en la medida: dos declaraciones distintas para la misma identidad producen un rojo.

La evidencia, como relaciones:

```json
{
  "referente_comparado": [{"que": "referencia", "huella_leida": "fd9fca09", "huella_actual": "9a79cad1", "cuando_lectura": "al generar", "cuando_actual": "ahora"}]
}
```

### 428-referente-sigue-vigente

**El referente conserva la huella leída**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ninguna_evidencia_se_juzga_con_referente_vencido`
- de dónde salió: Segtem/oracle · 4d791d3

**Qué pasó.** La huella declarada al producir la evidencia coincide con la actual. La medida debe dejar pasar esa comparación. La fila se transcribió de la comprobación de frescura de `diferencial/simulacion.json` de ESTE repo: `4ef377cb` es su huella `referencia`, y `"al generar"`/`"ahora"` son los literales que `nucleo/fixtures.py` pasa a `hechos_de_frescura`. Antes decía `9a79cad1`, que también es real pero es la huella de `vault.json` de `Brianholl/jam`: una observación verdadera atribuida al repo equivocado.

**Qué se aprendió.** La fila es la salida observada de `hechos_de_frescura` para las dos declaraciones de arriba. Cambiar el operador o contar también las huellas iguales rompe esta polaridad verde.

La evidencia, como relaciones:

```json
{
  "referente_comparado": [{"que": "referencia", "huella_leida": "4ef377cb", "huella_actual": "4ef377cb", "cuando_lectura": "al generar", "cuando_actual": "ahora"}]
}
```

### 429-sin-comparacion-de-referente-no-concluye

**Sin comparación de referente la frescura no concluye**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_evidencia_se_juzga_con_referente_vencido`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Si el sensor no presenta las declaraciones de lectura y actualidad, cero filas no prueba que el referente siga vigente.

**Qué se aprendió.** `requiere referente_comparado` evita convertir la ausencia de la comparación en un verde.

La evidencia, como relaciones:

```json
{
  "otra_evidencia": [{"nombre": "fixture sin comparación"}]
}
```

### 430-verbo-del-cli-fuera-de-la-ayuda

**El comando acepta un verbo que la ayuda no nombra**

- etiqueta: `falso_verde` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.todo_verbo_del_cli_esta_en_la_ayuda`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** El despacho acepta `biblioteca nueva` y la ayuda no lo menciona. La función está escrita, probada y publicada, y sólo la encuentra quien lea el código del despacho: para todo el resto no existe.

**Qué se aprendió.** La evidencia trae un verbo sano para que la medida no pase con un filtro vacío. Un verbo indocumentado no es una omisión menor: es trabajo terminado que nadie va a usar.

La evidencia, como relaciones:

```json
{
  "verbo_del_cli": [{"sustantivo": "biblioteca", "verbo": "nueva", "nombrado_en_la_ayuda": false}, {"sustantivo": "medida", "verbo": "listar", "nombrado_en_la_ayuda": true}]
}
```

### 431-todos-los-verbos-en-la-ayuda

**Todos los verbos que el comando acepta están en la ayuda**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.todo_verbo_del_cli_esta_en_la_ayuda`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno. El caso existe para que el mutador que quita el filtro no sobreviva: sin un verde, una medida que devuelve todas las filas pasa igual y nadie se entera.

**Qué se aprendió.** Un verde con más de una fila es el que fija que la medida filtra. Con una sola fila, quitar el filtro da el mismo resultado.

La evidencia, como relaciones:

```json
{
  "verbo_del_cli": [{"sustantivo": "medida", "verbo": "nueva", "nombrado_en_la_ayuda": true}, {"sustantivo": "proyecto", "verbo": "test", "nombrado_en_la_ayuda": true}]
}
```

### 432-opcion-del-vocabulario-sin-sentido

**Una opción de un vocabulario cerrado se explica en cuatro palabras**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_opcion_del_vocabulario_declara_su_sentido`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** `accidente` decía «apareció haciendo otra cosa». Cuatro palabras no distinguen de las otras cuatro opciones, que es lo único que el lector necesita en el momento en que se equivocó de nombre.

**Qué se aprendió.** La prosa corta se cuela porque parece prolija. La fila sana al lado es la que impide que la medida pase con un filtro vacío.

La evidencia, como relaciones:

```json
{
  "opcion_del_vocabulario": [{"vocabulario": "como_se_detecto", "opcion": "accidente", "palabras_del_sentido": 4, "en_el_manual": true}, {"vocabulario": "como_se_detecto", "opcion": "mutacion", "palabras_del_sentido": 10, "en_el_manual": true}]
}
```

### 433-vocabulario-explicado-entero

**Todas las opciones de un vocabulario se explican**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_opcion_del_vocabulario_declara_su_sentido`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno. Fija que la medida filtra: sin un verde con varias filas, quitar el `donde` daría el mismo resultado.

**Qué se aprendió.** Contar palabras no lee la explicación: la medida declara ese límite en su alcance, y este verde no lo desmiente.

La evidencia, como relaciones:

```json
{
  "opcion_del_vocabulario": [{"vocabulario": "segun", "opcion": "medicion", "palabras_del_sentido": 24, "en_el_manual": true}, {"vocabulario": "segun", "opcion": "tanteo", "palabras_del_sentido": 21, "en_el_manual": true}]
}
```

### 434-vocabulario-que-el-manual-no-muestra

**Un vocabulario cerrado queda fuera del registro del manual**

- etiqueta: `falso_verde` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.todo_vocabulario_cerrado_esta_en_el_manual`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** El manual es una vista de las declaraciones y por eso no puede quedar viejo, salvo de una manera: que alguien agregue un vocabulario y no lo anote en el registro. Entonces las opciones existen, el error las enumera y el manual no las tiene.

**Qué se aprendió.** La única grieta de un manual generado es el registro que dice qué generar. Medirla cuesta una medida y cierra el agujero entero.

La evidencia, como relaciones:

```json
{
  "opcion_del_vocabulario": [{"vocabulario": "polaridad", "opcion": "positiva", "palabras_del_sentido": 9, "en_el_manual": false}, {"vocabulario": "segun", "opcion": "contrato", "palabras_del_sentido": 22, "en_el_manual": true}]
}
```

### 435-el-manual-alcanza-todo-vocabulario

**El manual muestra todos los vocabularios cerrados**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.todo_vocabulario_cerrado_esta_en_el_manual`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno. Sin este verde el mutador que quita el filtro sobrevive y la medida mide menos de lo que dice.

**Qué se aprendió.** El verde no dice que el manual esté bien escrito: dice que ningún vocabulario quedó afuera del registro.

La evidencia, como relaciones:

```json
{
  "opcion_del_vocabulario": [{"vocabulario": "etiqueta", "opcion": "falso_verde", "palabras_del_sentido": 26, "en_el_manual": true}, {"vocabulario": "operadores", "opcion": "donde", "palabras_del_sentido": 24, "en_el_manual": true}]
}
```

### 436-verbos-reales-todos-en-la-ayuda

**Los verbos que el comando acepta hoy, contra la ayuda que imprime hoy**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.todo_verbo_del_cli_esta_en_la_ayuda`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno: los dieciséis verbos que el despacho acepta están nombrados en la ayuda. La evidencia no se escribió a mano — es lo que devolvió `hechos_de_verbos(cli.VERBOS, cli.__doc__)` sobre este repositorio, y por eso la medida queda fijada contra algo que ocurrió y no contra un ejemplo escrito para que pasara.

**Qué se aprendió.** Una medida cuyos casos son todos fabricados puede estar ajustada a sus propios ejemplos. Esta evidencia sale de una corrida y envejece sola: si mañana alguien agrega un verbo y no lo documenta, la corrida siguiente lo dice.

La evidencia, como relaciones:

```json
{
  "verbo_del_cli": [{"sustantivo": "biblioteca", "verbo": "instaladas", "nombrado_en_la_ayuda": true}, {"sustantivo": "biblioteca", "verbo": "listar", "nombrado_en_la_ayuda": true}, {"sustantivo": "biblioteca", "verbo": "nueva", "nombrado_en_la_ayuda": true}, {"sustantivo": "biblioteca", "verbo": "verificar", "nombrado_en_la_ayuda": true}, {"sustantivo": "caso", "verbo": "generar", "nombrado_en_la_ayuda": true}, {"sustantivo": "caso", "verbo": "listar", "nombrado_en_la_ayuda": true}, {"sustantivo": "caso", "verbo": "nuevo", "nombrado_en_la_ayuda": true}, {"sustantivo": "medida", "verbo": "expandir", "nombrado_en_la_ayuda": true}, {"sustantivo": "medida", "verbo": "listar", "nombrado_en_la_ayuda": true}, {"sustantivo": "medida", "verbo": "nueva", "nombrado_en_la_ayuda": true}, {"sustantivo": "medida", "verbo": "probar", "nombrado_en_la_ayuda": true}, {"sustantivo": "medida", "verbo": "revisar", "nombrado_en_la_ayuda": true}, {"sustantivo": "proyecto", "verbo": "escalares", "nombrado_en_la_ayuda": true}, {"sustantivo": "proyecto", "verbo": "init", "nombrado_en_la_ayuda": true}, {"sustantivo": "proyecto", "verbo": "relaciones", "nombrado_en_la_ayuda": true}, {"sustantivo": "proyecto", "verbo": "test", "
}
```

### 437-vocabularios-reales-explicados

**Las veintitrés opciones cerradas del lenguaje, con las palabras que hoy las explican**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.toda_opcion_del_vocabulario_declara_su_sentido`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno: ninguna opción se explica en cinco palabras o menos. Tres lo hacían hasta hoy —`persona`, `accidente` y `observacion`— y las encontró esta misma medida al escribirla.

**Qué se aprendió.** La evidencia observada de una medida sobre el propio lenguaje es barata: la relación ya se emite en cada corrida. No hay razón para fijar estas medidas sólo con ejemplos.

La evidencia, como relaciones:

```json
{
  "opcion_del_vocabulario": [{"vocabulario": "como_se_detecto", "opcion": "accidente", "palabras_del_sentido": 22, "en_el_manual": true}, {"vocabulario": "como_se_detecto", "opcion": "herramienta_ajena", "palabras_del_sentido": 8, "en_el_manual": true}, {"vocabulario": "como_se_detecto", "opcion": "mutacion", "palabras_del_sentido": 10, "en_el_manual": true}, {"vocabulario": "como_se_detecto", "opcion": "observacion", "palabras_del_sentido": 14, "en_el_manual": true}, {"vocabulario": "como_se_detecto", "opcion": "persona", "palabras_del_sentido": 15, "en_el_manual": true}, {"vocabulario": "etiqueta", "opcion": "deuda_de_diseño", "palabras_del_sentido": 23, "en_el_manual": true}, {"vocabulario": "etiqueta", "opcion": "falso_rojo", "palabras_del_sentido": 21, "en_el_manual": true}, {"vocabulario": "etiqueta", "opcion": "falso_verde", "palabras_del_sentido": 30, "en_el_manual": true}, {"vocabulario": "etiqueta", "opcion": "medida_correcta_conclusion_errada", "palabras_del_sentido": 27, "en_el_manual": true}, {"vocabulario": "etiqueta", "opcion": "verde_correcto", "palabras_del_sentido": 24, "en_el_manual": true}, {"vocabulario": "operadores", "opcion": "agrupar", "palabras_del_sentido": 29, "en_el_manual": true}
}
```

### 438-vocabularios-reales-en-el-manual

**Los cinco vocabularios cerrados de hoy, contra el registro del manual**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.todo_vocabulario_cerrado_esta_en_el_manual`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno: los cinco vocabularios están en `VOCABULARIOS`, así que el manual los muestra. Es la única grieta posible de un manual generado, y esta corrida la encuentra cerrada.

**Qué se aprendió.** Un manual generado no envejece; su registro sí. Medirlo contra la corrida real es lo que distingue «el manual está completo» de «el manual estaba completo cuando lo escribí».

La evidencia, como relaciones:

```json
{
  "opcion_del_vocabulario": [{"vocabulario": "como_se_detecto", "opcion": "accidente", "palabras_del_sentido": 22, "en_el_manual": true}, {"vocabulario": "como_se_detecto", "opcion": "herramienta_ajena", "palabras_del_sentido": 8, "en_el_manual": true}, {"vocabulario": "como_se_detecto", "opcion": "mutacion", "palabras_del_sentido": 10, "en_el_manual": true}, {"vocabulario": "como_se_detecto", "opcion": "observacion", "palabras_del_sentido": 14, "en_el_manual": true}, {"vocabulario": "como_se_detecto", "opcion": "persona", "palabras_del_sentido": 15, "en_el_manual": true}, {"vocabulario": "etiqueta", "opcion": "deuda_de_diseño", "palabras_del_sentido": 23, "en_el_manual": true}, {"vocabulario": "etiqueta", "opcion": "falso_rojo", "palabras_del_sentido": 21, "en_el_manual": true}, {"vocabulario": "etiqueta", "opcion": "falso_verde", "palabras_del_sentido": 30, "en_el_manual": true}, {"vocabulario": "etiqueta", "opcion": "medida_correcta_conclusion_errada", "palabras_del_sentido": 27, "en_el_manual": true}, {"vocabulario": "etiqueta", "opcion": "verde_correcto", "palabras_del_sentido": 24, "en_el_manual": true}, {"vocabulario": "operadores", "opcion": "agrupar", "palabras_del_sentido": 29, "en_el_manual": true}
}
```

### 439-sin-verbos-del-cli-no-concluye

**Sin la relación de verbos, la ayuda no se juzga**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.todo_verbo_del_cli_esta_en_la_ayuda`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Un consumidor de Oracle no tiene un CLI que documentar, así que la relación no se emite. Sin `requiere`, cero filas se leería como «todos los verbos están en la ayuda» y el proyecto se pondría verde por no tener nada que mirar.

**Qué se aprendió.** Lo encontró el mutador `quitar_requiere`: sacando la cláusula, ningún caso notaba la diferencia. `requiere` es lo que impide que la ausencia de evidencia se cobre como aprobación.

La evidencia, como relaciones:

```json
{
  "otra_evidencia": [{"nombre": "corrida sin esa relación"}]
}
```

### 440-sin-opciones-del-vocabulario-no-concluye

**Sin la relación de vocabulario, la explicación no se juzga**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_opcion_del_vocabulario_declara_su_sentido`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Si el manual no se puede importar, la relación no se emite. Sin `requiere`, cero filas diría que ninguna opción está mal explicada — cuando en realidad no se miró ninguna.

**Qué se aprendió.** El verde vacío es el defecto que este proyecto persigue, y una medida sobre el manual no está exenta.

La evidencia, como relaciones:

```json
{
  "otra_evidencia": [{"nombre": "corrida sin esa relación"}]
}
```

### 441-sin-opciones-del-vocabulario-el-manual-no-concluye

**Sin la relación de vocabulario, la cobertura del manual no se juzga**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.todo_vocabulario_cerrado_esta_en_el_manual`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** La misma ausencia deja sin juzgar si el manual alcanza todos los vocabularios: cero filas fuera del manual, porque no hay filas.

**Qué se aprendió.** Dos medidas leen la misma relación y las dos necesitan su propio caso de ausencia: el mutador se aplica a cada medida por separado.

La evidencia, como relaciones:

```json
{
  "otra_evidencia": [{"nombre": "corrida sin esa relación"}]
}
```

### 442-diagnostico-con-la-ruta-del-usuario

**El diagnóstico local publica una ruta con el usuario adentro**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.el_diagnostico_no_publica_el_dominio`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Un campo del diagnóstico trae la raíz del proyecto, que empieza con el home. El diagnóstico existe para pegarse en un issue público, y un `/home/<usuario>/` compartido no se puede despublicar.

**Qué se aprendió.** La fila sana al lado impide que la medida pase con un filtro vacío. El testigo lleva el NOMBRE de lo que se coló y no el valor entero: un testigo que reimprime el secreto lo publica igual.

La evidencia, como relaciones:

```json
{
  "campo_diagnostico": [{"campo": "proyecto.raiz", "es_del_dominio": true, "que_se_colo": "/home/usuaria"}, {"campo": "python.version", "es_del_dominio": false, "que_se_colo": ""}]
}
```

### 443-diagnostico-sin-nada-del-dominio

**El diagnóstico no publica nada del dominio**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.el_diagnostico_no_publica_el_dominio`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno. Sin este verde, quitar el filtro daría el mismo resultado y la medida mediría menos de lo que dice.

**Qué se aprendió.** La medida compara contra lo que el proyecto sabe que es suyo. Un dato del dominio que no esté en esa lista NO lo ve, y su alcance lo dice.

La evidencia, como relaciones:

```json
{
  "campo_diagnostico": [{"campo": "python.version", "es_del_dominio": false, "que_se_colo": ""}, {"campo": "plataforma", "es_del_dominio": false, "que_se_colo": ""}]
}
```

### 444-sombra-sobre-una-medida-que-no-existe

**Queda una sombra sobre un id que el catálogo ya no tiene**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_sombra_sobre_una_medida_que_no_existe`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Una medida se renombró y la sombra quedó apuntando al id viejo. No apaga nada, pero sugiere una protección que no existe: quien lee `oracle.json` cree que ese rojo está contemplado.

**Qué se aprendió.** Una sombra es una decisión escrita; cuando su objeto desaparece, la decisión queda huérfana y hay que sacarla. La medida NO sugiere a cuál se parecía: sólo dice que ese id no está.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.medida_que_se_fue", "declara_desde": true, "declara_porque": true, "dias": 30, "dio_ok": false, "existe": false}, {"medida": "dominio.medida_viva", "declara_desde": true, "declara_porque": true, "dias": 12, "dio_ok": false, "existe": true}]
}
```

### 445-todas-las-sombras-sobre-medidas-que-existen

**Todas las sombras apuntan a medidas del catálogo**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_sombra_sobre_una_medida_que_no_existe`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno. Hacen falta dos filas sanas para que el mutador que quita el filtro no sobreviva.

**Qué se aprendió.** El verde dice que los ids resuelven, no que las sombras estén justificadas: de eso se ocupan las otras dos medidas de sombra.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.una", "declara_desde": true, "declara_porque": true, "dias": 3, "dio_ok": false, "existe": true}, {"medida": "dominio.otra", "declara_desde": true, "declara_porque": true, "dias": 40, "dio_ok": false, "existe": true}]
}
```

### 446-sombra-sobre-una-medida-ya-en-verde

**Una medida en sombra ya da verde y la sombra sigue puesta**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_sombra_ya_en_verde`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** La medida se arregló y nadie sacó la sombra. Mientras siga, el proyecto no exige algo que ya podría exigir, y la etapa de transición se vuelve un estado permanente.

**Qué se aprendió.** `dio_ok` es falso cuando la medida no llegó a evaluarse: no se puede afirmar que esté en verde algo que no corrió. La medida tampoco ve si ese verde es estable — sólo el de esta corrida.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.ya_arreglada", "declara_desde": true, "declara_porque": true, "dias": 90, "dio_ok": true, "existe": true}, {"medida": "dominio.todavia_roja", "declara_desde": true, "declara_porque": true, "dias": 5, "dio_ok": false, "existe": true}]
}
```

### 447-ninguna-sombra-esta-de-mas

**Toda sombra puesta sigue tapando un rojo**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_sombra_ya_en_verde`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno. Sin un verde de dos filas, el mutador que quita el filtro sobrevive.

**Qué se aprendió.** Que ninguna esté de más no dice que ninguna lleve demasiado tiempo: la antigüedad viaja en `dias` y todavía no la juzga ninguna medida.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.una", "declara_desde": true, "declara_porque": true, "dias": 10, "dio_ok": false, "existe": true}, {"medida": "dominio.otra", "declara_desde": true, "declara_porque": true, "dias": 60, "dio_ok": false, "existe": true}]
}
```

### 448-sombra-sin-fecha-ni-motivo

**Una sombra sin fecha y otra sin motivo**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_sombra_declara_desde_y_porque`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Sin fecha la sombra no se puede envejecer; sin motivo no se puede discutir. Con cualquiera de las dos faltando, apagar un rojo sale gratis y deja de ser una decisión.

**Qué se aprendió.** El filtro es una disyunción, así que hace falta una fila por cada rama: con una sola, cambiar el `o` por un `y` pasaría inadvertido.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.sin_fecha", "declara_desde": false, "declara_porque": true, "dias": -1, "dio_ok": false, "existe": true}, {"medida": "dominio.sin_motivo", "declara_desde": true, "declara_porque": false, "dias": 7, "dio_ok": false, "existe": true}, {"medida": "dominio.completa", "declara_desde": true, "declara_porque": true, "dias": 7, "dio_ok": false, "existe": true}]
}
```

### 449-toda-sombra-con-fecha-y-motivo

**Todas las sombras declaran desde cuándo y por qué**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_sombra_declara_desde_y_porque`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno. Las dos filas sanas fijan que la medida filtra.

**Qué se aprendió.** La medida ve que los dos campos están; NO juzga si el motivo es bueno ni si la fecha es cierta.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.una", "declara_desde": true, "declara_porque": true, "dias": 2, "dio_ok": false, "existe": true}, {"medida": "dominio.otra", "declara_desde": true, "declara_porque": true, "dias": 33, "dio_ok": false, "existe": true}]
}
```

### 450-relacion-del-lenguaje-sin-documentar

**Una relación que el lenguaje emite no está nombrada en la referencia**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_relacion_del_lenguaje_esta_en_la_referencia`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** La documentación es la única parte del proyecto sin arnés, y por eso envejece sola: al escribir esta medida, diez de diecinueve relaciones —todas las de L−1 y L−2 entre ellas— no estaban en la especificación, y nada lo había señalado nunca.

**Qué se aprendió.** Lo único falsable acá es que el nombre aparezca. Si la explicación es buena o está al día no lo puede contestar ninguna medida, y el alcance lo dice.

La evidencia, como relaciones:

```json
{
  "relacion_documentada": [{"relacion": "cantidad_comparada", "nombrada_en_la_referencia": false}, {"relacion": "caso", "nombrada_en_la_referencia": true}]
}
```

### 451-todas-las-relaciones-documentadas

**Todas las relaciones del lenguaje están en la referencia**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_relacion_del_lenguaje_esta_en_la_referencia`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno. Con una sola fila, quitar el filtro daría lo mismo.

**Qué se aprendió.** El verde es sobre los nombres, no sobre la prosa. Es poco, y es lo que se puede afirmar.

La evidencia, como relaciones:

```json
{
  "relacion_documentada": [{"relacion": "sombra", "nombrada_en_la_referencia": true}, {"relacion": "verbo_del_cli", "nombrada_en_la_referencia": true}]
}
```

### 452-sin-relaciones-documentadas-no-concluye

**Sin la referencia, la documentación no se juzga**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_relacion_del_lenguaje_esta_en_la_referencia`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Un proyecto consumidor no tiene —ni tiene por qué tener— la especificación de Oracle: el paquete instalado ni siquiera la incluye. Sin `requiere`, cero filas se leería como «todo documentado» y pondría en verde a quien no documentó nada.

**Qué se aprendió.** Documentar el lenguaje es responsabilidad de quien lo publica, no de quien lo usa. `requiere` es lo que convierte esa frase en algo que la corrida respeta.

La evidencia, como relaciones:

```json
{
  "otra_evidencia": [{"nombre": "consumidor sin la especificación"}]
}
```

### 453-una-sola-sombra-sin-motivo

**Una sola sombra sin motivo, justo en el borde del umbral**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_sombra_declara_desde_y_porque`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Exactamente una sombra de tres no declara su motivo. Es el caso del borde: con dos ofensoras, aflojar el umbral de cero a uno sigue dando rojo y la mutación pasa inadvertida. Con una sola, aflojarlo lo pone verde — que es la diferencia que hay que poder ver.

**Qué se aprendió.** Un umbral de cero necesita un caso que valga exactamente uno. Sin él, «cero» y «uno o menos» son la misma medida para todo el corpus, y el mutador que los confunde sobrevive.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.sin_motivo", "declara_desde": true, "declara_porque": false, "dias": 21, "dio_ok": false, "existe": true}, {"medida": "dominio.completa", "declara_desde": true, "declara_porque": true, "dias": 4, "dio_ok": false, "existe": true}, {"medida": "dominio.tambien_completa", "declara_desde": true, "declara_porque": true, "dias": 15, "dio_ok": false, "existe": true}]
}
```

### 454-sombra-observada-sobre-un-id-muerto

**Una sombra real sobre un id que el catalogo no tiene**

- etiqueta: `falso_verde` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ninguna_sombra_sobre_una_medida_que_no_existe`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** La evidencia no se escribio a mano: es lo que devolvio `hechos_de_sombra` sobre un proyecto real creado para esta corrida, con tres sombras declaradas en su `oracle.json` y los veredictos de la primera vuelta de la aceptacion. De las tres, una apunta a un id que el catalogo no tiene: no apaga nada y sugiere una proteccion que no existe.

**Qué se aprendió.** Este caso y los dos siguientes salen de la MISMA corrida. Una medida fijada solo con evidencia fabricada puede estar ajustada a los ejemplos que se escribieron para que pasara; esta no.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "meta.medida_que_ya_no_esta", "declara_desde": true, "declara_porque": true, "dias": 12, "dio_ok": false, "existe": false}, {"medida": "meta.toda_medida_filtra_o_agrupa", "declara_desde": true, "declara_porque": true, "dias": 1, "dio_ok": false, "existe": true}, {"medida": "meta.todo_umbral_declara_de_donde_sale", "declara_desde": true, "declara_porque": true, "dias": 0, "dio_ok": true, "existe": true}]
}
```

### 455-sombra-observada-que-ya-da-verde

**Una sombra real sobre una medida que ya da verde**

- etiqueta: `falso_verde` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ninguna_sombra_ya_en_verde`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** La evidencia no se escribio a mano: es lo que devolvio `hechos_de_sombra` sobre un proyecto real creado para esta corrida, con tres sombras declaradas en su `oracle.json` y los veredictos de la primera vuelta de la aceptacion. Una de las tres tapa una medida que en esa misma corrida dio verde: no tiene nada que perdonar, y mientras siga puesta el proyecto no exige algo que ya podria exigir.

**Qué se aprendió.** `dio_ok` sale de los veredictos de la vuelta anterior, no de una declaracion: por eso la sombra sobrante se puede ver sin preguntarle a nadie.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "meta.medida_que_ya_no_esta", "declara_desde": true, "declara_porque": true, "dias": 12, "dio_ok": false, "existe": false}, {"medida": "meta.toda_medida_filtra_o_agrupa", "declara_desde": true, "declara_porque": true, "dias": 1, "dio_ok": false, "existe": true}, {"medida": "meta.todo_umbral_declara_de_donde_sale", "declara_desde": true, "declara_porque": true, "dias": 0, "dio_ok": true, "existe": true}]
}
```

### 456-sombras-observadas-todas-con-fecha-y-motivo

**Las tres sombras reales declaran desde cuando y por que**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.toda_sombra_declara_desde_y_porque`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** La evidencia no se escribio a mano: es lo que devolvio `hechos_de_sombra` sobre un proyecto real creado para esta corrida, con tres sombras declaradas en su `oracle.json` y los veredictos de la primera vuelta de la aceptacion. Ninguna de las tres omite fecha ni motivo, que es lo que esta medida mira.

**Qué se aprendió.** El verde observado es lo que distingue una medida fijada de una medida ajustada a sus propios ejemplos. La misma evidencia esta roja para otras dos medidas, y eso tambien es informacion.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "meta.medida_que_ya_no_esta", "declara_desde": true, "declara_porque": true, "dias": 12, "dio_ok": false, "existe": false}, {"medida": "meta.toda_medida_filtra_o_agrupa", "declara_desde": true, "declara_porque": true, "dias": 1, "dio_ok": false, "existe": true}, {"medida": "meta.todo_umbral_declara_de_donde_sale", "declara_desde": true, "declara_porque": true, "dias": 0, "dio_ok": true, "existe": true}]
}
```

### 457-diagnostico-observado-sin-nada-del-dominio

**El diagnostico real de este repositorio no publica nada del dominio**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.el_diagnostico_no_publica_el_dominio`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno. Los siete campos son los que `oracle diagnostico` imprime hoy sobre este repositorio, leidos de `hechos_de_diagnostico(reunir(proy))`. Ninguno contiene un id de medida, un nombre de archivo, la raiz ni el home.

**Qué se aprendió.** El diagnostico existe para pegarse en un issue publico. Fijarlo con la corrida real es lo unico que dice algo sobre el diagnostico que la gente va a pegar de verdad.

La evidencia, como relaciones:

```json
{
  "campo_diagnostico": [{"campo": "oracle.distribucion", "es_del_dominio": false, "que_se_colo": ""}, {"campo": "oracle.algebra", "es_del_dominio": false, "que_se_colo": ""}, {"campo": "oracle.sintaxis", "es_del_dominio": false, "que_se_colo": ""}, {"campo": "oracle.corriendo_desde", "es_del_dominio": false, "que_se_colo": ""}, {"campo": "entorno.python", "es_del_dominio": false, "que_se_colo": ""}, {"campo": "entorno.sistema", "es_del_dominio": false, "que_se_colo": ""}, {"campo": "entorno.arquitectura", "es_del_dominio": false, "que_se_colo": ""}]
}
```

### 458-referencia-observada-nombra-todas-las-relaciones

**La especificacion de hoy nombra las veintidos relaciones del lenguaje**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.toda_relacion_del_lenguaje_esta_en_la_referencia`
- de dónde salió: Segtem/oracle · 1ed6abb+worktree

**Qué pasó.** Ninguno. Es lo que devolvio `hechos_de_documentacion` sobre `ESPECIFICACION.md` en este corte. Cuando la medida se escribio, diez de diecinueve relaciones no estaban nombradas.

**Qué se aprendió.** La documentacion es la unica parte del proyecto sin arnes. Este caso la ata a una corrida: si manana entra una relacion y nadie la documenta, la corrida siguiente lo dice.

La evidencia, como relaciones:

```json
{
  "relacion_documentada": [{"relacion": "ancestro", "nombrada_en_la_referencia": true}, {"relacion": "campo_declarado", "nombrada_en_la_referencia": true}, {"relacion": "campo_diagnostico", "nombrada_en_la_referencia": true}, {"relacion": "cantidad_comparada", "nombrada_en_la_referencia": true}, {"relacion": "caso", "nombrada_en_la_referencia": true}, {"relacion": "equivalencia", "nombrada_en_la_referencia": true}, {"relacion": "fuente", "nombrada_en_la_referencia": true}, {"relacion": "medida", "nombrada_en_la_referencia": true}, {"relacion": "medida_en_uso", "nombrada_en_la_referencia": true}, {"relacion": "nodo", "nombrada_en_la_referencia": true}, {"relacion": "opcion_del_vocabulario", "nombrada_en_la_referencia": true}, {"relacion": "paso", "nombrada_en_la_referencia": true}, {"relacion": "paso_de_medida", "nombrada_en_la_referencia": true}, {"relacion": "producto", "nombrada_en_la_referencia": true}, {"relacion": "referente_comparado", "nombrada_en_la_referencia": true}, {"relacion": "referente_declarado", "nombrada_en_la_referencia": true}, {"relacion": "relacion_declarada", "nombrada_en_la_referencia": true}, {"relacion": "relacion_documentada", "nombrada_en_la_referencia": true}, {"relacion": "requ
}
```

### 459-referentes-reales-del-fixture-diferencial

**Los cuatro referentes que el fixture diferencial declara hoy**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ninguna_evidencia_declara_un_referente_sin_huella`
- de dónde salió: Segtem/oracle · 2f3edfa+worktree

**Qué pasó.** Ninguno: los cuatro traen huella. La evidencia no se escribió a mano — es lo que devolvió
`hechos_de_referentes(referentes_de_fixture(...))` sobre `diferencial/simulacion.json` en
este corte, y cada huella es el sha256 real de lo que el emisor leyó al generar el fixture:
el catálogo, la configuración del dominio, `tools/generar_diferencial.py` y
`diferencial/referencia/evaluador.py`.

**Qué se aprendió.** Cierra el tercer rojo de la DECISIÓN 004, y por el camino que esa decisión dejó escrito: no
transcribiendo evidencia inventada sino cambiando el mundo. L−2 existía en el lenguaje y no
en este repositorio; los referentes ya se calculaban dentro de `revisar_frescura` y morían
ahí. Exponerlos no agregó una medida: hizo observable algo que ya ocurría.

La evidencia, como relaciones:

```json
{
  "referente_declarado": [{"que": "catalogo", "huella": "d66e6985345ab6971e96263b7702a74df4528b4f43d6ceb1399c7c59c45f32cc", "cuando": "al generar", "tiene_huella": true}, {"que": "configuracion", "huella": "52c043490ec55bfa4cf7fd11a7a594420143fcc2aa6a6f71c5488d01c873a4d6", "cuando": "al generar", "tiene_huella": true}, {"que": "emisor", "huella": "47856e2558bc9aebfa71ca8c2f9714bcb7579d6352d090e909e0b28265c3b0e0", "cuando": "al generar", "tiene_huella": true}, {"que": "referencia", "huella": "4ef377cb18f49ad19385560c18343873c22c83701aa59699b50c86ff685ce479", "cuando": "al generar", "tiene_huella": true}]
}
```

### 460-una-sombra-de-mas-de-un-trimestre

**Una sombra lleva más de noventa días puesta**

- etiqueta: `falso_verde` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_sombra_envejece_sin_revisarse`
- de dónde salió: Segtem/oracle · 398cd18+worktree

**Qué pasó.** `dias` viajaba en la relación desde que existe el modo sombra y ninguna medida lo miraba. Una sombra de 244 días pasaba en verde: la etapa de transición se volvió permanente y lo único que la distinguía de apagar la medida —que alguien la iba a sacar— dejó de ser cierto sin que nada lo dijera.

**Qué se aprendió.** Una sola fila ofende, y es a propósito: con dos, aflojar el umbral de cero a uno sigue dando rojo y la mutación pasa inadvertida. La fila de 90 días fija además que el límite es estricto — noventa entra, noventa y uno no.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.olvidada", "declara_desde": true, "declara_porque": true, "dias": 244, "dio_ok": false, "existe": true}, {"medida": "dominio.reciente", "declara_desde": true, "declara_porque": true, "dias": 12, "dio_ok": false, "existe": true}, {"medida": "dominio.justo_en_el_limite", "declara_desde": true, "declara_porque": true, "dias": 90, "dio_ok": false, "existe": true}]
}
```

### 461-ninguna-sombra-envejecio

**Todas las sombras son de este trimestre**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_sombra_envejece_sin_revisarse`
- de dónde salió: Segtem/oracle · 398cd18+worktree

**Qué pasó.** Ninguno. Sin un verde de varias filas, el mutador que quita el filtro sobrevive y la medida mide menos de lo que dice.

**Qué se aprendió.** El verde dice que ninguna pasó el trimestre, no que alguien las haya revisado. La medida no puede ver eso y su alcance lo declara.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.una", "declara_desde": true, "declara_porque": true, "dias": 3, "dio_ok": false, "existe": true}, {"medida": "dominio.otra", "declara_desde": true, "declara_porque": true, "dias": 61, "dio_ok": false, "existe": true}]
}
```

### 462-una-sombra-con-fecha-que-no-se-puede-leer

**Una sombra declara una fecha que no se puede leer**

- etiqueta: `falso_verde` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_sombra_declara_una_fecha_real`
- de dónde salió: Segtem/oracle · 398cd18+worktree

**Qué pasó.** `meta.toda_sombra_declara_desde_y_porque` sólo comprueba que el campo no esté vacío, así que «cuando pueda» lo pasa con `declara_desde` en true. El marco no puede calcular su edad y devuelve días negativos, y sin esta medida esa sombra queda fuera del alcance de la que envejece: invisible para las dos.

**Qué se aprendió.** Un campo declarado no es un campo válido. Las dos medidas de sombra que ya existían miraban presencia; ésta mira que lo declarado sirva para algo.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.fecha_ilegible", "declara_desde": true, "declara_porque": true, "dias": -1, "dio_ok": false, "existe": true}, {"medida": "dominio.sana", "declara_desde": true, "declara_porque": true, "dias": 30, "dio_ok": false, "existe": true}]
}
```

### 463-ninguna-sombra-con-fecha-invalida

**Todas las sombras declaran una fecha que se puede leer**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_sombra_declara_una_fecha_real`
- de dónde salió: Segtem/oracle · 398cd18+worktree

**Qué pasó.** Ninguno. Dos filas sanas para que quitar el filtro no sobreviva.

**Qué se aprendió.** Cero días es válido: una sombra puesta hoy. El límite es el signo, no el tamaño — de la edad se ocupa la otra medida, y por eso la fila de 120 días acá está en verde.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.una", "declara_desde": true, "declara_porque": true, "dias": 0, "dio_ok": false, "existe": true}, {"medida": "dominio.otra", "declara_desde": true, "declara_porque": true, "dias": 120, "dio_ok": false, "existe": true}]
}
```

### 464-sombra-observada-de-291-dias

**Una sombra real de 291 dias, sobre un proyecto con tres**

- etiqueta: `falso_verde` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ninguna_sombra_envejece_sin_revisarse`
- de dónde salió: Segtem/oracle · 398cd18+worktree

**Qué pasó.** La evidencia no se escribio a mano: es lo que devolvio `hechos_de_sombra` sobre un proyecto real creado para esta corrida, con tres sombras declaradas en su `oracle.json`. Una lleva 291 dias puesta: nueve meses, tres veces el trimestre que el umbral declara. Las otras dos no ofenden.

**Qué se aprendió.** El valor sale de restar fechas en la corrida, no de un numero elegido para el ejemplo. Una medida fijada solo con evidencia fabricada puede estar ajustada a sus propios casos.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "meta.ninguna_medida_sin_alcance", "declara_desde": true, "declara_porque": true, "dias": -1, "dio_ok": false, "existe": true}, {"medida": "meta.toda_medida_filtra_o_agrupa", "declara_desde": true, "declara_porque": true, "dias": 291, "dio_ok": false, "existe": true}, {"medida": "meta.todo_umbral_declara_de_donde_sale", "declara_desde": true, "declara_porque": true, "dias": 13, "dio_ok": false, "existe": true}]
}
```

### 465-sombra-observada-con-fecha-ilegible

**Una sombra real declara «cuando pueda» y el marco no puede fecharla**

- etiqueta: `falso_verde` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.toda_sombra_declara_una_fecha_real`
- de dónde salió: Segtem/oracle · 398cd18+worktree

**Qué pasó.** La evidencia no se escribio a mano: es lo que devolvio `hechos_de_sombra` sobre un proyecto real creado para esta corrida, con tres sombras declaradas en su `oracle.json`. Una declara «cuando pueda». `declara_desde` sale en true —el campo no esta vacio— y los dias salen en -1: la sombra existe, se informa, y no tiene edad.

**Qué se aprendió.** Es la misma corrida que el caso de al lado, y las dos medidas la leen distinto: una encuentra la vieja, la otra la que no se puede fechar. Ninguna encuentra las dos, y por eso son dos.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "meta.ninguna_medida_sin_alcance", "declara_desde": true, "declara_porque": true, "dias": -1, "dio_ok": false, "existe": true}, {"medida": "meta.toda_medida_filtra_o_agrupa", "declara_desde": true, "declara_porque": true, "dias": 291, "dio_ok": false, "existe": true}, {"medida": "meta.todo_umbral_declara_de_donde_sale", "declara_desde": true, "declara_porque": true, "dias": 13, "dio_ok": false, "existe": true}]
}
```

### 466-una-opcion-de-exactamente-cinco-palabras

**Una opción explicada en exactamente cinco palabras, que es el borde**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_opcion_del_vocabulario_declara_su_sentido`
- de dónde salió: Segtem/oracle · df4a2a9+worktree

**Qué pasó.** El corpus de esta medida sólo tenía anomalías grandes —cuatro palabras contra veintidós— y ninguna JUSTO en el límite. Con eso, mover el límite de cinco a cuatro, o volver la comparación estricta, no cambiaba ningún veredicto: las dos formas de escribir la medida se veían iguales.

**Qué se aprendió.** Un límite necesita un testigo EN el límite, no cerca. Lo encontró un mutador escrito por otro autor que nunca vio este corpus, y su docstring lo había predicho: «puede pasar inadvertido cuando ningún testigo interno está justo en el borde».

La evidencia, como relaciones:

```json
{
  "opcion_del_vocabulario": [{"vocabulario": "segun", "opcion": "en_el_borde", "palabras_del_sentido": 5, "en_el_manual": true}, {"vocabulario": "segun", "opcion": "holgada", "palabras_del_sentido": 24, "en_el_manual": true}]
}
```

### 467-una-sombra-de-noventa-y-un-dias

**Una sombra de noventa y un días, el primer día que ofende**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_sombra_envejece_sin_revisarse`
- de dónde salió: Segtem/oracle · df4a2a9+worktree

**Qué pasó.** El caso de esta medida tenía una sombra de 244 días y otra de 90. Faltaba la de 91: la primera que ofende. Sin ella, correr el límite de noventa a noventa y uno no cambiaba ningún veredicto, y el trimestre podía ser otro número sin que nadie se enterara.

**Qué se aprendió.** Un caso de 90 días fija que noventa NO ofende; hace falta el de 91 para fijar que noventa y uno SÍ. Los dos bordes, no uno.

La evidencia, como relaciones:

```json
{
  "sombra": [{"medida": "dominio.recien_pasada", "declara_desde": true, "declara_porque": true, "dias": 91, "dio_ok": false, "existe": true}, {"medida": "dominio.reciente", "declara_desde": true, "declara_porque": true, "dias": 7, "dio_ok": false, "existe": true}]
}
```

### 468-exclusion-de-mutador-aplicada-globalmente

**Un mutador excluido fue quitado globalmente del arnés**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_exclusion_de_mutador_se_aplica_globalmente`
- de dónde salió: Segtem/oracle · f5e8f6c+worktree

**Qué pasó.** `convertir_conteo_en_existencia` estaba excluido del arnés sacándolo del registro general de mutadores en vez de aplicar la exclusión por medida. Al filtrarse globalmente, no corre sobre ninguna medida del catálogo y el denominador de la mutación baja en silencio en todo el proyecto.

**Qué se aprendió.** Una sola fila ofende, y es a propósito: con dos, aflojar el umbral de cero a uno sigue dando rojo y ese mutante pasa inadvertido. Las exclusiones deben aplicarse por medida y no sobre el registro global de mutadores; si un mutador no está disponible en el arnés, deja de correr para todo el catálogo y distorsiona el denominador de mutación.

La evidencia, como relaciones:

```json
{
  "mutador_excluido": [{"mutador": "convertir_conteo_en_existencia", "premisa": "la medida tiene umbral <= 0", "lo_ofrece_un_autor": true, "esta_en_el_arnes": false}, {"mutador": "maximo_por_minimo", "premisa": "las medidas con cota superior no operan sobre filas homogéneas", "lo_ofrece_un_autor": true, "esta_en_el_arnes": true}]
}
```

### 469-todas-las-exclusiones-disponibles-en-el-arnes

**Todas las exclusiones de mutadores están disponibles en el arnés**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_exclusion_de_mutador_se_aplica_globalmente`
- de dónde salió: Segtem/oracle · f5e8f6c+worktree

**Qué pasó.** Ninguno. Sin un verde de varias filas, el mutador que quita el filtro sobrevive y la medida mide menos de lo que dice.

**Qué se aprendió.** El verde afirma que cada exclusión mantiene su mutador disponible en el registro del arnés, de modo que no se excluye de forma global para todo el catálogo. Varias filas sanas impiden además que el mutador que quita el filtro sobreviva.

La evidencia, como relaciones:

```json
{
  "mutador_excluido": [{"mutador": "convertir_conteo_en_existencia", "premisa": "la medida tiene umbral <= 0", "lo_ofrece_un_autor": true, "esta_en_el_arnes": true}, {"mutador": "maximo_por_minimo", "premisa": "las medidas con cota superior no operan sobre filas homogéneas", "lo_ofrece_un_autor": true, "esta_en_el_arnes": true}, {"mutador": "promedio_por_minimo", "premisa": "ninguna medida promedia colecciones con cardinalidad variable", "lo_ofrece_un_autor": true, "esta_en_el_arnes": true}]
}
```

### 470-la-exclusion-real-no-se-aplica-globalmente

**La única exclusión que el arnés tiene hoy no saca a su mutador del registro**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ninguna_exclusion_de_mutador_se_aplica_globalmente`
- de dónde salió: Segtem/oracle · f5e8f6c+worktree

**Qué pasó.** Ninguno. La evidencia no se escribió a mano: es lo que devolvió `hechos_de_mutadores_excluidos` sobre las exclusiones declaradas y el registro `MUTADORES` de este corte —29 mutadores, 1 exclusión declarada—. `convertir_conteo_en_existencia` está en el registro y se saltea por medida en `mutantes()`, no al construirlo.

**Qué se aprendió.** Una medida fijada sólo con evidencia fabricada puede estar ajustada a los ejemplos que se escribieron para que pasara. Este verde sale de la corrida y envejece solo: el día que alguien vuelva a filtrar los excluidos al construir el registro, el mutador desaparece de `MUTADORES` y este caso da falso sin que nadie lo toque. La forma vieja no era hipotética —estuvo en el árbol hasta hoy— y escondía cobertura real: la biblioteca de ejemplo publicaba 16 mutantes certificados cuando eran 17.

La evidencia, como relaciones:

```json
{
  "mutador_excluido": [{"mutador": "convertir_conteo_en_existencia", "premisa": "la medida tiene umbral <= 0", "lo_ofrece_un_autor": true, "esta_en_el_arnes": true}]
}
```

### 471-el-mutador-que-nadie-distribuye-no-es-una-exclusion-global

**En el paquete instalado el mutador falta porque nadie lo distribuye, y eso no es un defecto**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ninguna_exclusion_de_mutador_se_aplica_globalmente`
- de dónde salió: Segtem/oracle · f5e8f6c+worktree

**Qué pasó.** Ninguno, y ése es el punto. `mutadores/` no está en `pyproject.toml`, así que no viaja en el wheel: un consumidor carga 5 mutadores propios en vez de 29 y `convertir_conteo_en_existencia` no está en el registro. La primera versión de esta medida miraba un solo hecho y llamaba a eso «exclusión global», poniendo en rojo a todo proyecto que instalara Oracle por un archivo que nadie le mandó.

**Qué se aprendió.** Hay dos maneras de que un mutador no esté en el registro y sólo una es un defecto. Este caso fija la diferencia: sin él, borrar `lo_ofrece_un_autor == true` del filtro no rompería ningún otro caso —468 ofende igual, 469 y 470 siguen verdes— y la medida volvería a reprochar a un consumidor algo que no puede arreglar. Salió de correr la suite entera para verificar el cambio: el test del wheel instalado se puso rojo.

La evidencia, como relaciones:

```json
{
  "mutador_excluido": [{"mutador": "convertir_conteo_en_existencia", "premisa": "la medida tiene umbral <= 0", "lo_ofrece_un_autor": false, "esta_en_el_arnes": false}]
}
```

### 472-medida-sin-ambito

**Una medida no declara su ámbito**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_medida_declara_su_ambito`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** La relación `medida` trae `ambito` en `sin_declarar`. Esa ausencia es visible para que una forma vieja o incompleta se ponga roja durante la migración, no para aceptarla como categoría válida.

**Qué se aprendió.** No existe un valor por omisión para el ámbito: `sin_declarar` reifica la deuda de migración y la regla falla ante una sola fila ofensora aunque conviva con medidas sanas.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.medida_sin_ambito", "ambito": "sin_declarar"}, {"id": "dominio.medida_sana", "ambito": "universal"}]
}
```

### 473-medidas-con-ambito-declarado

**Medidas con ámbito declarado no ofenden**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.toda_medida_declara_su_ambito`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Las medidas declaran explícitamente su ámbito con valores del vocabulario cerrado (`universal` o `del_origen`). La regla debe dejarlas pasar a todas: la ausencia que mira es `sin_declarar`.

**Qué se aprendió.** La regla no juzga si el ámbito declarado es el correcto ni si la cota con sus dependencias se cumple: sólo falla cuando el ámbito de la medida quedó sin declarar.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.guardia_compartida", "ambito": "universal"}, {"id": "dominio.verificacion_interna", "ambito": "del_origen"}, {"id": "otro_dominio.politica_general", "ambito": "universal"}]
}
```

### 474-el-catalogo-migrado-declara-su-ambito

**Las 56 medidas del catálogo quedaron con su ámbito declarado tras la migración**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.toda_medida_declara_su_ambito`
- de dónde salió: Segtem/oracle · 20a679d+worktree

**Qué pasó.** Ninguno. La evidencia no se escribió a mano: son cuatro filas de las 56 que devolvió `como_hechos` sobre el catálogo cargado de este corte —37 universales y 19 del origen, ninguna en `sin_declarar`—. Se eligieron una de cada ámbito, la medida que juzga y la que se juzga a sí misma.

**Qué se aprendió.** Una medida fijada sólo con evidencia fabricada puede estar ajustada a los ejemplos que se escribieron para que pasara. Este verde sale de la corrida y envejece solo: el día que alguien agregue una medida sin declarar su ámbito —o escriba una macro nueva sin el parámetro—, el catálogo real deja de coincidir con este caso sin que nadie lo toque. Incluye a `meta.toda_medida_declara_su_ambito` entre las filas que juzga, que es el punto fijo de L2 en su forma más concreta: la regla se somete a sí misma.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "meta.ninguna_medida_sin_alcance", "ambito": "universal"}, {"id": "meta.toda_medida_declara_su_ambito", "ambito": "del_origen"}, {"id": "meta.toda_medida_filtra_o_agrupa", "ambito": "universal"}, {"id": "meta.unir_conmuta", "ambito": "del_origen"}]
}
```

### 475-medida-universal-depende-de-relacion-del-origen

**Una medida universal depende de una relación del origen**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Una medida declarada `universal` consume una relación clasificada como `del_origen`. Al ser universal obliga a cualquier consumidor que adopte el catálogo, pero el consumidor no gobierna esa evidencia ni tiene remedio para levantar el rojo.

**Qué se aprendió.** Una sola combinación ofende: `dominio.auditoria_del_arnes` cruzada con `mutador_excluido`. La regla distingue en vez de contar: `dominio.verificacion_interna` puede consumir `mutador_excluido` porque su propio ámbito es `del_origen`, y `dominio.guardia_compartida` es `universal` pero consume una relación `universal`. La cota de DECISION-012 prohíbe que el ámbito de la medida sea más amplio que el de sus dependencias, no que existan dependencias del origen.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.auditoria_del_arnes", "ambito": "universal"}, {"id": "dominio.verificacion_interna", "ambito": "del_origen"}, {"id": "dominio.guardia_compartida", "ambito": "universal"}]
  "dependencia_de_medida": [{"medida": "dominio.auditoria_del_arnes", "relacion": "mutador_excluido", "clase": "fuente"}, {"medida": "dominio.verificacion_interna", "relacion": "mutador_excluido", "clase": "fuente"}, {"medida": "dominio.guardia_compartida", "relacion": "campo_declarado", "clase": "fuente"}]
  "ambito_de_relacion": [{"relacion": "mutador_excluido", "ambito": "del_origen"}, {"relacion": "campo_declarado", "ambito": "universal"}]
}
```

### 476-medidas-con-dependencias-de-ambito-compatible

**Medidas con dependencias de ámbito compatible no ofenden**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Ninguno. Las medidas declaran un ámbito igual o más estrecho que el de las relaciones de las que dependen, cubriendo dependencias por `fuente` y por `requiere` tanto en medidas universales como del origen.

**Qué se aprendió.** El caso verde ejercita las dos polaridades de la relación `dependencia_de_medida` (`fuente` y `requiere`). Una medida `del_origen` puede depender de relaciones del origen o universales; una medida `universal` puede depender de relaciones universales. La cota tolera que una medida sea más estrecha que sus relaciones, pero no más amplia.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.verificacion_interna", "ambito": "del_origen"}, {"id": "dominio.guardia_compartida", "ambito": "universal"}]
  "dependencia_de_medida": [{"medida": "dominio.verificacion_interna", "relacion": "mutador_excluido", "clase": "fuente"}, {"medida": "dominio.verificacion_interna", "relacion": "paso", "clase": "requiere"}, {"medida": "dominio.verificacion_interna", "relacion": "medida", "clase": "fuente"}, {"medida": "dominio.guardia_compartida", "relacion": "campo_declarado", "clase": "fuente"}, {"medida": "dominio.guardia_compartida", "relacion": "relacion_declarada", "clase": "requiere"}]
  "ambito_de_relacion": [{"relacion": "mutador_excluido", "ambito": "del_origen"}, {"relacion": "paso", "ambito": "del_origen"}, {"relacion": "medida", "ambito": "universal"}, {"relacion": "campo_declarado", "ambito": "universal"}, {"relacion": "relacion_declarada", "ambito": "universal"}]
}
```

### 477-medida-universal-depende-por-requiere-de-relacion-del-origen

**Una medida universal depende por `requiere` de una relación del origen**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `construida`
- medida que lo atrapa: `meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias`
- de dónde salió: Segtem/oracle · sin-commit

**Qué pasó.** Una medida declarada como `universal` consume una fuente universal, pero impone una precondición con `requiere` sobre una relación `del_origen`. Aunque la consulta principal sólo lea evidencia universal, la precondición no puede satisfacerse en un consumidor externo sin la evidencia del origen, dejando la medida sin remedio posible fuera de su autor.

**Qué se aprendió.** La cota de ámbito mira las dos vías por las que una medida se acopla a una relación: por fuente directa y por `requiere`. Ambas se unifican en `dependencia_de_medida` para evitar duplicar la regla de consistencia en dos políticas paralelas; un requerimiento sobre una relación interna es tan inalcanzable para un tercero como una fuente interna.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "dominio.guardia_con_requiere_interno", "ambito": "universal"}, {"id": "dominio.guardia_universal_sana", "ambito": "universal"}]
  "dependencia_de_medida": [{"medida": "dominio.guardia_con_requiere_interno", "relacion": "campo_declarado", "clase": "fuente"}, {"medida": "dominio.guardia_con_requiere_interno", "relacion": "mutador_excluido", "clase": "requiere"}, {"medida": "dominio.guardia_universal_sana", "relacion": "campo_declarado", "clase": "fuente"}, {"medida": "dominio.guardia_universal_sana", "relacion": "relacion_declarada", "clase": "requiere"}]
  "ambito_de_relacion": [{"relacion": "campo_declarado", "ambito": "universal"}, {"relacion": "mutador_excluido", "ambito": "del_origen"}, {"relacion": "relacion_declarada", "ambito": "universal"}]
}
```

### 478-la-cota-y-la-clasificacion-coinciden-sin-consultarse

**Ninguna medida universal del catálogo depende de una relación del origen**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias`
- de dónde salió: Segtem/oracle · b08b4b5+worktree

**Qué pasó.** Ninguno, y el resultado dice algo que no se buscaba. La evidencia no se escribió a mano: son filas de las tres relaciones tal como las devolvió `como_hechos` sobre el catálogo cargado de este corte. En él hay 13 dependencias sobre relaciones `del_origen` —`equivalencia`, `paso`, `nodo`, `producto` y `mutador_excluido`— y las 13 salen de medidas que YA estaban declaradas `del_origen`. La clasificación se hizo preguntando quién tiene el remedio; la cota deriva lo mismo desde las relaciones que cada medida consume. Coinciden sin haberse consultado.

**Qué se aprendió.** Una medida fijada sólo con evidencia fabricada puede estar ajustada a los ejemplos que se escribieron para que pasara. Este verde sale de la corrida y envejece solo: el día que alguien declare universal una medida que consume una relación del origen, el catálogo real deja de coincidir con este caso sin que nadie lo toque. Vale además como confirmación independiente de la clasificación de ámbitos: dos criterios distintos —quién puede arreglar el rojo, y de qué relaciones se alimenta la medida— dieron la misma respuesta sobre 55 medidas. La coincidencia no prueba que la clasificación sea correcta; prueba que no se contradice consigo misma, que es lo único que una medida puede comprobar.

La evidencia, como relaciones:

```json
{
  "medida": [{"id": "meta.unir_conmuta", "ambito": "del_origen"}, {"id": "meta.ninguna_exclusion_de_mutador_se_aplica_globalmente", "ambito": "del_origen"}, {"id": "meta.toda_medida_filtra_o_agrupa", "ambito": "universal"}]
  "dependencia_de_medida": [{"medida": "meta.unir_conmuta", "relacion": "equivalencia", "clase": "fuente"}, {"medida": "meta.ninguna_exclusion_de_mutador_se_aplica_globalmente", "relacion": "mutador_excluido", "clase": "fuente"}, {"medida": "meta.toda_medida_filtra_o_agrupa", "relacion": "medida", "clase": "fuente"}, {"medida": "meta.toda_medida_filtra_o_agrupa", "relacion": "termino", "clase": "fuente"}, {"medida": "meta.toda_medida_filtra_o_agrupa", "relacion": "termino", "clase": "requiere"}]
  "ambito_de_relacion": [{"relacion": "equivalencia", "ambito": "del_origen"}, {"relacion": "mutador_excluido", "ambito": "del_origen"}, {"relacion": "medida", "ambito": "universal"}, {"relacion": "termino", "ambito": "universal"}]
}
```

### 001-verde-acumulativo

**«489 tests OK» reportado cada turno: un número que sube y nunca significa más**

- etiqueta: `falso_verde` · se detectó por: `persona`
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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

### 025-mutante-de-codigo-sobreviviente

**Un mutante de código sobrevivió a la suite de tests**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `observada`
- medida que lo atrapa: `proceso.codigo_con_mutante_que_lo_mata`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** La ronda de mutación de código detectó un mutante donde los tests pasaron sin fallar. La medida debe ponerse roja y contar el sobreviviente.

**Qué se aprendió.** Un test que pasa con el código mutado es un punto ciego de la suite. La medida debe contarlo como ofensa y ponerse roja.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "nucleo/caso.py:53:1:constante", "apunta_a": "nucleo/caso.py", "cambio": "constante: False → True", "estado": "pasaron", "murio": false, "tests_fallaron": false, "error_arnes": false, "timeout": false, "codigo_salida": 0, "equivalente_declarado": false, "razon_equivalente": ""}, {"id": "nucleo/caso.py:14:1:constante", "apunta_a": "nucleo/caso.py", "cambio": "constante: 1 → 2", "estado": "tests_fallaron", "murio": true, "tests_fallaron": true, "error_arnes": false, "timeout": false, "codigo_salida": 1, "equivalente_declarado": false, "razon_equivalente": ""}]
}
```

### 026-mutante-de-codigo-equivalente-no-cuenta-como-muerte-ni-sobreviviente

**Un mutante equivalente declarado con su razón no cuenta como sobreviviente ni como muerte**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `proceso.codigo_con_mutante_que_lo_mata`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Una ronda con un sobreviviente real, un mutante muerto y un mutante declarado equivalente. La medida debe contar exactamente un sobreviviente, ignorando la exclusión declarada sin ocultar la ofensa real.

**Qué se aprendió.** Declarar un mutante equivalente documenta una decisión legítima que no debe contar como sobreviviente ni como muerte, y no debe enmascarar a los sobrevivientes reales.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "nucleo/caso.py:53:1:constante", "apunta_a": "nucleo/caso.py", "cambio": "constante: False → True", "estado": "pasaron", "murio": false, "tests_fallaron": false, "error_arnes": false, "timeout": false, "codigo_salida": 0, "equivalente_declarado": false, "razon_equivalente": ""}, {"id": "nucleo/caso.py:14:1:constante", "apunta_a": "nucleo/caso.py", "cambio": "constante: 1 → 2", "estado": "tests_fallaron", "murio": true, "tests_fallaron": true, "error_arnes": false, "timeout": false, "codigo_salida": 1, "equivalente_declarado": false, "razon_equivalente": ""}, {"id": "tools/cifras.py:23:16:constante", "apunta_a": "tools/cifras.py", "cambio": "constante: 0 → 1", "estado": "pasaron", "murio": false, "tests_fallaron": false, "error_arnes": false, "timeout": false, "codigo_salida": 0, "equivalente_declarado": true, "razon_equivalente": "precedencia de sys.path"}]
}
```

### 027-ronda-de-codigo-sin-mutantes-no-concluye

**Una ronda de mutación de código sin mutantes no concluye**

- etiqueta: `falso_verde` · se detectó por: `mutacion`
- procedencia: `construida`
- medida que lo atrapa: `proceso.codigo_con_mutante_que_lo_mata`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Cero mutantes en la relación. Sin la precondición `requiere`, la medida agregaría sobre cero filas y devolvería verde vacilante sobre la nada.

**Qué se aprendió.** Sin mutantes de código no hay evidencia de fijación. La medida debe exigir la presencia de la relación y no concluir verde en el vacío.

La evidencia, como relaciones:

```json
{
  "mutante": []
}
```

### 043-ausencia-total-sale-verde

**La medida de ausencia se ponía más verde cuanto peor estaba el mundo**

- etiqueta: `falso_verde` · se detectó por: `herramienta_ajena`
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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

### 109-mutantes-de-codigo-todos-muertos

**Todos los mutantes de código murieron bajo la suite**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
- medida que lo atrapa: `proceso.codigo_con_mutante_que_lo_mata`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Todos los mutantes de código fueron detectados por los tests (estado tests_fallaron). La medida debe dar verde y con quitar_filtro dar rojo.

**Qué se aprendió.** Un verde correcto fija que cuando los mutantes son detectados y eliminados, la medida dictamina conformidad.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "nucleo/caso.py:14:1:constante", "apunta_a": "nucleo/caso.py", "cambio": "constante: 1 → 2", "estado": "tests_fallaron", "murio": true, "tests_fallaron": true, "error_arnes": false, "timeout": false, "codigo_salida": 1, "equivalente_declarado": false, "razon_equivalente": ""}, {"id": "nucleo/caso.py:27:1:constante", "apunta_a": "nucleo/caso.py", "cambio": "constante: 4 → 5", "estado": "tests_fallaron", "murio": true, "tests_fallaron": true, "error_arnes": false, "timeout": false, "codigo_salida": 1, "equivalente_declarado": false, "razon_equivalente": ""}]
}
```

### 110-mutante-de-codigo-equivalente-declarado-verde

**Un mutante de código declarado equivalente no impide el verde legítimo**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `construida`
- medida que lo atrapa: `proceso.codigo_con_mutante_que_lo_mata`
- de dónde salió: Segtem/oracle · local

**Qué pasó.** Una ronda donde todos los mutantes reales murieron y el único que no murió está declarado equivalente con su razón. La medida debe salir verde.

**Qué se aprendió.** Un mutante equivalente declarado con razón no debe reportarse como sobreviviente cuando no hay otros defectos.

La evidencia, como relaciones:

```json
{
  "mutante": [{"id": "nucleo/caso.py:14:1:constante", "apunta_a": "nucleo/caso.py", "cambio": "constante: 1 → 2", "estado": "tests_fallaron", "murio": true, "tests_fallaron": true, "error_arnes": false, "timeout": false, "codigo_salida": 1, "equivalente_declarado": false, "razon_equivalente": ""}, {"id": "tools/cifras.py:23:16:constante", "apunta_a": "tools/cifras.py", "cambio": "constante: 0 → 1", "estado": "pasaron", "murio": false, "tests_fallaron": false, "error_arnes": false, "timeout": false, "codigo_salida": 0, "equivalente_declarado": true, "razon_equivalente": "precedencia de sys.path"}]
}
```

### 116-todo-el-nucleo-es-alcanzable

**Con las entradas reales declaradas, no hay módulo muerto**

- etiqueta: `verde_correcto` · se detectó por: `observacion`
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `construida`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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
- procedencia: `observada`
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

*1043 líneas*

El álgebra: relaciones, expresiones y los operadores. Sin dependencias.

Una **fila de trabajo** es un mapa `alias → hecho`, más las columnas derivadas bajo la clave
reservada `_`. Toda operación toma filas y devuelve filas: eso es la clausura.

El lenguaje activo tiene cinco operadores: `de`, `donde`, `resumen`, `unir` y `agrupar`.

### `nucleo/biblioteca.py`

*504 líneas*

Bibliotecas de políticas: datos verificables, instalados sin ejecutar código.

El contrato ``oracle.biblioteca/v1`` vive en una carpeta física. Una distribución instalada la
publica en una ruta fija derivada de su nombre. El descubrimiento usa sólo ``importlib.metadata``:
lee ``METADATA``, ``RECORD`` y el manifiesto localizado, sin importar el paquete ni cargar entry
points. Encontrar Python o un binario ejecutable es un error, no una invitación a confiarlo.

### `nucleo/caso.py`

*541 líneas*

Superficie de autoría para casos del corpus.

El almacenamiento histórico del corpus es JSON: un objeto con prosa y evidencia L0. Esta superficie
mantiene ese contrato y sólo cambia la forma de escribirlo: la prosa queda como prosa y la evidencia
homogénea queda como tabla.

### `nucleo/diagnostico.py`

*150 líneas*

Diagnóstico local: qué versión, qué entorno y qué proyecto — sin red y sin dominio.

Existe para que un reporte de problema no empiece con cinco preguntas de ida y vuelta. Es la
**fase 1** de la telemetría propuesta, y la única que se adopta ([`DECISION-007`], corrección 6):
se produce un archivo, la persona lo lee entero, y decide si lo comparte. **Acá no hay red.**

### Lo que NUNCA sale

Esta lista no es una precaución: es el contrato, y hay una medida que lo vigila.

    evidencia y filas          nombres de archivo del dominio      `porque` y `alcance`
    ids de medidas propias     remotos de git                      variables de entorno
    tokens                     el contenido de `escalares.py`      el nombre del host

De un proyecto sale su **forma** —qué carpetas existen, cuántas medidas y casos hay— nunca su
contenido. «Tiene 41 medidas» ayuda a reproducir un problema; cómo se llaman, no.

### Las rutas se reemplazan por marcadores

`/home/alguien/Dev/proyecto/catalogos` sale como `<PROYECTO>/catalogos`. El home sale como
`<HOME>`. Un nombre de usuario es un dato personal que se cuela en cualquier ruta absoluta.

### `nucleo/diferencial.py`

*166 líneas*

Sensor de procedencia para los fixtures diferenciales.

Las huellas no prueban que una referencia sea correcta. Prueban algo más modesto y necesario: que
el fixture declara con qué emisor, referencia, catálogo y configuración se generó. Este módulo
calcula esas huellas; `nucleo.fixtures` las reifica y una medida del lenguaje decide la frescura.

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

*361 líneas*

Lector único y fail-closed de fixtures diferenciales versionados.

Los consumidores no deben conocer la forma física del fixture. Este módulo valida las dos formas
de ``oracle.diferencial/v1`` y las proyecta como evidencias o casos asociados a una medida. Así
``medida --relaciones``, la revisión, el diferencial y la mutación leen exactamente el mismo dato.
La frescura usa el mismo camino: reifica las huellas leída y actual como `referente_comparado` y
delega el veredicto a una medida `.oracle`; no conserva un comparador propio.

### `nucleo/generador.py`

*738 líneas*

Fabricación de evidencia discriminante a partir del AST de una medida.

Dada una medida del catálogo, fabrica evidencia derivada de su forma (relaciones,
campos, comparadores, umbrales y agrupaciones) para discriminar mutantes.

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

*401 líneas*

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

La plantilla es la forma canónica con huecos `["$", "<parametro>"]`. Expandir es sustituir. Las
macros universales viven en `nucleo/macros/` y se cargan como cualquier otra: son la biblioteca
estándar del lenguaje, no un privilegio del núcleo.

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

*273 líneas*

Sensores del propio marco: hechos sobre los casos y sobre el uso de cada medida.

El norte de oracle es el universo de problemas de **crear una herramienta**, y una parte de ese
universo es la herramienta misma: si el corpus fija las medidas, si alguna quedó sin ejercitar, si un
caso reclama algo que no existe. Eso hasta ahora se decidía con `if`s dentro de `tools/` — o sea que
el veredicto sobre el marco estaba en código imperativo mientras el resto del proyecto exige que los
veredictos sean datos. Es el mismo pecado que un sensor que juzga, un nivel más arriba.

Acá se producen los hechos; el juicio queda en `catalogos/meta/`.

    caso(id, medida, procedencia, tiene_medida, medida_existe, esperado_ok, dio_ok,
         explica_el_hueco, es_heredado, biblioteca)
    medida_en_uso(id, casos_que_la_evaluan, mutantes, mutantes_vivos)
    sombra(medida, declara_desde, declara_porque, dias, dio_ok, existe)
    mutador_excluido(mutador, premisa, disponible_en_el_arnes)

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

*860 líneas*

La medida: un dato que se lee, se evalúa y se puede medir a su vez.

Forma canónica, tal como se guarda en `catalogos/`:

```json
["medida", "<id>",
  ["desde", ["de", "<relacion>", "<alias>"], ["donde", <pred>]],
  ["resumen", "contar", 1],
  ["umbral", "<=", 0, "<la defensa del número>", "<de dónde salió>"],
  ["ambito", "<dónde obliga>"],
  ["alcance", "<qué NO ve>"]]
```

Tres campos evitan que una medida prometa más de lo que puede sostener: **`alcance`** impide que un
verde diga «todo bien» a secas, **`segun`** vuelve inspeccionable el origen del número y **`ambito`**
separa dónde nació la medida de los proyectos a los que puede obligar. La defensa en prosa sigue
existiendo, pero ya no es obligatoria: dice por qué ése y no otro, no de dónde salió.

Los **testigos no se declaran**: son las filas con las que terminó la tubería. Declararlos aparte
obliga a escribir la misma condición dos veces y a mantenerlas sincronizadas a mano — el caso
`004-testigos-duplicados` del corpus.

### `nucleo/mutacion.py`

*443 líneas*

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

*645 líneas*

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

### `nucleo/referente.py`

*131 líneas*

Declaración del referente que leyó un sensor (Nivel L−2).

La declaración no afirma que el referente exista ni que la huella le corresponda. Sólo deja juntos
el objeto que el sensor dice haber leído, la huella que declaró al leerlo y el momento de esa
lectura. La frescura se expresa emparejando esa declaración con otra posterior: el emisor presenta
las dos huellas y una medida del lenguaje hace la comparación.

Forma canónica JSON, por referente:

```json
["referente", "Content/Props/silla.uasset", "sha256:...", "2026-08-27T09:14:00"]
```

Una colección de declaraciones se reifica como la relación `referente_declarado`. Dos colecciones,
al leer y ahora, se reifican como `referente_comparado`. El campo
`tiene_huella` no reemplaza la huella: hace observable para el lenguaje si la declaración vino sin
una, sin inventar un valor por omisión.

### `nucleo/relacion.py`

*304 líneas*

La declaración de una relación (L−1): qué lee el sensor, en qué unidad, y qué NO miró.

Forma canónica, tal como se guarda en `relaciones/`:

```json
["relacion", "<nombre>",
  ["campos",
    ["campo", "<nombre>", "<tipo>", "<unidad>"],
    ...
  ],
  ["alcance", "<qué NO lee el sensor>"]]
```

Un campo sin magnitud física —un identificador, un nombre, una clave categórica o booleana—
declara explícitamente `sin_unidad`. No hay defaults silenciosos: todo campo declara su unidad.
El `alcance` del sensor es obligatorio por la misma razón que en una medida: delimitar lo que el
sensor no observó.

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

*1573 líneas*

Superficie infija de autoría para medidas.

El lector devuelve la misma forma de almacenamiento que recibió el impresor, incluidas las
invocaciones de macro que ya viven en el catálogo.

### `nucleo/unidad.py`

*329 líneas*

Derivación de la unidad de lo que una medida compara (L−1).

Para cada medida del catálogo, deriva la unidad de cada cantidad comparada:
- `["campo", alias, campo]`: la unidad declarada en la relación para ese campo (o `sin_unidad` para relaciones del lenguaje/proceso).
- `["col", nombre]`: la unidad de la clave o agregado producida en `agrupar`.
- Una escalar registrada: su `unidad` de retorno si fue declarada, o propagada para operadores aritméticos universales.
- `contar`: `adimensional` (conteo).
- Literales: heredan la unidad del otro operando en la comparación.
- Cualquier otra cosa: `no derivable` (`es_derivable: False`).

Emite la relación del lenguaje `cantidad_comparada(medida, unidad, es_derivable)`.

### `nucleo/version.py`

*95 líneas*

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

### `nucleo/vocabulario.py`

*113 líneas*

Los vocabularios cerrados del lenguaje, cada opción con lo que significa.

Un vocabulario cerrado —las cinco etiquetas de un caso, los cuatro orígenes de un umbral— es la
parte del lenguaje que más se equivoca quien recién llega, porque los nombres se parecen entre sí
y el archivo no dice cuál es cuál. Durante meses ese significado vivió en prosa suelta:
`PLAN-LENGUAJE.md`, `corpus/README.md`, el tutorial y `docs/07-conectar-a-un-proyecto-propio.md`
decían cada uno una parte, y ninguno era la fuente.

Acá la declaración ES la fuente: el nombre y su sentido viajan juntos en la misma estructura. De
ahí salen las dos cosas que importan — el error que ve quien se equivoca, en el momento exacto en
que se equivoca, y el manual, que no es un documento aparte sino una vista de esto mismo.

Este módulo no importa nada de `nucleo`: lo usan tanto `caso` como `medida`, que no se conocen
entre sí, y una dependencia hacia adentro los ataría sin motivo.

---

<!-- fuente: 06-las-herramientas.md -->

## Las herramientas

Cada una existe por un motivo que está escrito en su encabezado. Varias nacieron de un defecto concreto del corpus.

### `tools/aceptacion.py`

*266 líneas*

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

*319 líneas*

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

### `tools/cli.py`

*1002 líneas*

Entry point único para Oracle.

oracle <sustantivo> <verbo>             forma canónica (medida, caso, proyecto, biblioteca)
oracle <sustantivo>                     ayuda del sustantivo con sus verbos

oracle medida nueva <dominio.nombre>    crea una nueva medida en catalogos/ con plantilla lista
oracle medida revisar <archivo>         revisa y evalúa una medida suelta contra la evidencia
oracle medida probar <archivo> --con <filas>   corre una medida contra filas escritas a mano
oracle medida listar                    lista las medidas del catálogo con umbral, alcance y fijación
oracle medida expandir <archivo>        muestra la forma canónica de una medida escrita con macros

oracle caso nuevo <grupo/id>            crea un nuevo caso en corpus/ con plantilla lista
oracle caso listar                      lista los casos del corpus, su etiqueta y qué medida reclaman
oracle caso generar <medida>            propone casos a partir de los mutantes que sobreviven

oracle proyecto init [ruta]             inicializa un proyecto con catalogos/, corpus/, diferencial/ y oracle.json
oracle proyecto test [--rapido|--todo]  ejecuta la secuencia completa de verificación con veredicto final
oracle proyecto relaciones              hechos y campos disponibles derivados de la evidencia
oracle proyecto escalares               funciones de dominio y operadores disponibles
oracle proyecto contexto [--compacto]   todo lo que hace falta para escribir una medida acá

oracle biblioteca nueva <id> [ruta]     crea el esqueleto de una biblioteca publicable
oracle biblioteca instaladas            lista las instaladas y cuáles usa el proyecto
oracle biblioteca verificar <ruta>      certifica una biblioteca local de políticas
oracle biblioteca listar <ruta>         muestra sus umbrales, orígenes y alcances completos
oracle manual                           la referencia del lenguaje, armada de sus fuentes
oracle manual operadores                los seis operadores de una tubería
oracle manual segun                     de dónde sale el número de un umbral
oracle manual etiqueta                  qué enseña un caso del corpus
oracle manual procedencia               de dónde salió la evidencia de un caso
oracle manual como_se_detecto           quién encontró el defecto
oracle manual relaciones                las relaciones que el lenguaje emite sobre sí mismo
oracle manual verbos                    los verbos del comando, por sustantivo
oracle manual medidas                   las 54 medidas que Oracle trae, y qué NO ve cada una
oracle manual [tema] --man              la misma referencia en roff, para `man -l`
oracle manual --instalar-man <dir>      escribe oracle(1) y oracle-<tema>(7) bajo <dir>

oracle convertir <archivo>              traduce entre superficie y JSON (por la extensión)

### `tools/contexto.py`

*157 líneas*

`oracle contexto` — todo lo que hace falta para escribir una medida, en un solo lugar.

Quien va a escribir una medida —una persona o un agente— necesita saber cuatro cosas: qué relaciones
existen y con qué campos, qué funciones puede usar, qué tiene que declarar sí o sí, y qué medidas ya
están para no repetirlas. Hoy eso se averigua corriendo tres comandos y leyendo dos documentos, y el
que no sabe que existen no los corre.

No es un documento nuevo: es una VISTA, igual que el manual. Las relaciones salen del inventario que
usa `oracle relaciones`, las escalares del registro real, los vocabularios de `nucleo/vocabulario.py`
y las medidas del catálogo cargado. Si algo cambia, cambia acá solo.

`--compacto` existe porque el destinatario más probable es un agente con una ventana de contexto: la
misma información sin los renglones en blanco, sin las prosas largas y sin lo que se puede deducir.
No es un formato distinto — es la misma vista, apretada.

### `tools/corpus.py`

*386 líneas*

Verificador del corpus — la primera regla del repositorio, y se aplica a sí mismo.

    python tools/corpus.py            → verifica (sale != 0 si algo está mal)
    python tools/corpus.py --resumen  → verifica y además cuenta qué mecanismo atrapa qué
    python tools/corpus.py --listar   → lista los casos del corpus, su etiqueta y qué medida reclaman
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

*94 líneas*

Runner `unittest` con un protocolo de salida inequívoco para mutación de código.

0 significa que la suite pasó; 1, que un test falló o terminó con una excepción; 2, que el arnés no
pudo establecer una suite (descubrimiento inválido, runner roto o cero tests). La línea base verde es
la que permite atribuir al mutante un error posterior dentro del código ejercitado.

### `tools/estudio.py`

*417 líneas*

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

### `tools/lsp.py`

*374 líneas*

Servidor LSP mínimo de Oracle: publica diagnósticos y completado por stdio.

### `tools/manual.py`

*485 líneas*

`oracle manual` — la referencia del lenguaje, armada de lo que el lenguaje ya declara.

No es un documento. Es una vista: cada sección se lee de la fuente que ya existe —los vocabularios
cerrados de `nucleo/vocabulario.py` y `nucleo/caso.py`, las relaciones que emite `nucleo/marco.py`,
los verbos de `tools/cli.py`, el catálogo base— y por eso no puede quedar vieja sin que alguna de
esas fuentes cambie. Un manual escrito a mano envejece en silencio; éste no tiene dónde envejecer.

Lo que sí puede pasar es que aparezca un vocabulario nuevo y nadie lo agregue acá. Eso lo mide
`meta.todo_vocabulario_cerrado_esta_en_el_manual`, que es la razón por la que este archivo entra al
perfil de mutación: custodia una afirmación —«el manual está completo»— que nadie más comprueba.

### `tools/medida.py`

*797 líneas*

Escribir una medida sin pedirle permiso a nadie.

    python tools/medida.py --relaciones            qué hechos hay para medir, y sus campos
    python tools/medida.py --escalares             qué funciones de dominio se pueden usar
    python tools/medida.py --nueva dominio.nombre  crea el archivo con la forma puesta
    python tools/medida.py --listar                lista las medidas con umbral, alcance y fijación
    python tools/medida.py <archivo.json>          la revisa y la corre contra el corpus
    python tools/medida.py --expandir <archivo>     ve en qué forma canónica se convierte la macro

Para ejecutar `escalares.py` de otro proyecto hace falta `--confiar-escalares`. Ayuda,
`--relaciones`, `--nueva`, `--listar` y el inventario base de `--escalares` nunca ejecutan ese archivo.

Existe porque sin esto el lenguaje tiene dueño. Todo el argumento de este repositorio es que quien
ve un defecto pueda escribir la regla que lo atrapa; si para eso hay que escribir s-expresiones en
JSON a mano y adivinar qué relaciones existen, el único que puede hacerlo es quien escribió el
evaluador — y ahí volvemos al problema del principio.

`--relaciones` no es una lista mantenida a mano: sale de la evidencia que hay en el corpus y en los
fixtures. Si aparece un hecho nuevo, aparece acá solo.

### `tools/metamorficas.py`

*670 líneas*

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

*166 líneas*

Muta las medidas y mide el resultado CON LAS MEDIDAS. El bucle se cierra acá.

    python tools/mutar.py [--confiar-escalares]          → informe
    python tools/mutar.py --hechos [--confiar-escalares] → evidencia JSON

El sensor produce hechos y las políticas aplicables del catálogo pueden juzgarlos. Un proyecto
neutral no necesita importar esas políticas para obtener el resultado operativo de la mutación.

Sale != 0 si algún mutante sobrevivió, porque un mutante que sobrevive es un aspecto de la medida que
el corpus no fija.

### `tools/mutar_codigo.py`

*586 líneas*

Muta el CÓDIGO del núcleo y mide el resultado con las medidas del catálogo.

    python tools/mutar_codigo.py                 → informe
    python tools/mutar_codigo.py --hechos        → volcar la evidencia (JSON)
    python tools/mutar_codigo.py --timeout 90    → límite por ejecución de tests
    python tools/mutar_codigo.py --manifiesto progreso.json [--reanudar]

Cada ronda copia el proyecto a un directorio temporal y sólo muta esa copia. Un bloqueo impide dos
rondas sobre la misma raíz; timeout y señales terminan el grupo de procesos y limpian el aislamiento.

Sale 1 si algún mutante sobrevivió y 2 si la ronda fue inconclusa. Timeout, error del arnés y fallo de
tests son estados distintos; sólo el último demuestra que el mutante murió.

### `tools/oracle.py`

*13 líneas*

Alias directo para tools/cli.py.

### `tools/sesion.py`

*15 líneas*

Frontera común entre errores de proyecto y los códigos de salida de los entry points.

### `tools/sintaxis.py`

*225 líneas*

CLI para la superficie infija de autoría.

python tools/sintaxis.py --imprimir catalogos/meta/meta.donde_compone.json
python tools/sintaxis.py --leer medida.oracle
python tools/sintaxis.py --verificar

### `tools/trazar.py`

*181 líneas*

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

*359 líneas*

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

## 2026-08-25 — doc: documentar autoría del corpus en superficie (.caso) y andamio

*commit b0052d2*



## 2026-08-25 — Saca el informe

*commit 147786d*



## 2026-08-25 — Merge branch 'caso-docs'

*commit 83d2a54*



## 2026-08-25 — Merge branch 'caso-docs': la documentación enseña la superficie de casos

*commit 6237b9d*

Los cuatro documentos tenían **cero menciones** de `.caso` el día después de que
el corpus entero se escribiera en él, y `ORACLE-TUTORIAL-PRACTICO.md` seguía
enseñando a tipear JSON crudo en su sección 8 — o sea, lo PRIMERO que hace
alguien siguiendo el tutorial, porque el propio documento manda escribir el caso
antes que la medida.

Corregido también el id `002-vencida-con-dueño`, que llevaba `ñ`: el id de un
caso ES el nombre del archivo, y por eso mismo es ASCII.

Trabajo delegado a Gemini 3.7 Flash (high).

## Tres cosas mías encima

**1 · El verificador de documentos miraba una sola superficie y dos documentos.**
Los ejemplos de `.caso` aparecieron en cuatro y ninguno pasaba por el lector:
volvían a ser afirmaciones sostenidas por la palabra de quien las escribió, que
es lo que ese mecanismo vino a terminar. Ahora reconoce ` ```oracle ` y ` ```caso `
con sus sufijos `-gramatica` y `-fragmento`, sobre los cuatro documentos. De 16
bloques verificados a **21**.

**2 · Un test que no podía correr mientras la herramienta corría.** El bloqueo de
`mutar_codigo.py` es por raíz, así que `test_mutacion_con_baseline_timeout…`
fallaba con `RondaEnCurso` en vez de `LineaBaseFallida` cada vez que había una
ronda de verdad en el mismo árbol. Ahora se copia su propia raíz.

Es la **tercera vez en el día** que un test rompe por depender del entorno de
alrededor —el de git, éste, y el intento intermedio— y la lección ya está escrita
tres veces: un test que necesita el entorno de su autor no es un test, es una
coincidencia.

**3 · Y una falla de mi propio andamiaje, que anoto porque cuesta plata.** Agy no
encontró su worktree, salió a buscar `TAREA.md` por todo el disco, encontró el de
OTRA rama y ejecutó la tarea equivocada —encima de la que DeepSeek ya estaba
haciendo, en el mismo directorio—. El wrapper hace `cd` al worktree; no alcanzó.
Relanzado con la ruta absoluta en el prompt, salió bien a la primera.

521 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS 36 medidas + 3 macros + 99 casos + 21 bloques de documentación
MUTACIÓN de medidas 535/535 — 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — El error del lenguaje no se podía manipular como un error, y la mutación lo encontró

*commit cbdb75a*

`ErrorSintaxis` es un `dataclass(frozen=True)`. Un dataclass congelado reemplaza
`__setattr__` por uno que rechaza TODO, y eso alcanza a los dunder que el
intérprete y las herramientas de traza escriben sobre cualquier excepción:

    e.__traceback__ = tb   →  FrozenInstanceError: cannot assign to field '__traceback__'

CPython los escribe por la API de C al levantar la excepción —por eso un `raise`
simple andaba y nadie lo notó— pero cualquier código Python que re-lance, encadene
o inspeccione el error se estrellaba.

**Lo encontró la mutación de código, no una persona.** De 193 mutantes de
`nucleo/caso.py`, **51 salieron `error_arnes`** en vez de muertos o vivos, con ese
mismo `FrozenInstanceError` durante el descubrimiento de tests. Un error del arnés
no es una muerte —caso `017` del corpus—, así que esos 51 no medían nada y la
ronda entera quedaba INCONCLUSA. El defecto se escondía justamente detrás del
mecanismo que existe para no dejar pasar cosas escondidas.

La inmutabilidad que se quiere es la de los CAMPOS del error —línea, columna, qué
se esperaba—, no la de la maquinaria de excepciones de Python. El parche se aplica
después de la clase porque `dataclass(frozen=True)` se niega a que se declare un
`__setattr__` propio adentro.

Queda un límite dicho: `copy.copy` sobre uno de estos errores sigue fallando. No
lo arreglo porque nada en el proyecto copia excepciones —lo verifiqué— y agregar
maquinaria para un usuario que no existe es lo que este repositorio no hace.

524 tests OK

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Una escalar que revienta ya no atraviesa el álgebra con una excepción cruda

*commit a573685*

`escalares[cabeza](*argumentos)` sólo atajaba `ErrorDeAlgebra`. Cualquier otra
excepción de Python —un `TypeError` por restarle un float a `None`, por decir la
más común— salía del evaluador tal cual.

El camino AISLADO ya la envolvía («falló la escalar externa …») y el que corre en
proceso no, así que **el mismo defecto se veía distinto según por dónde entrara**.
Y crudo no se podía atajar: quien llamaba al álgebra no tenía forma de distinguir
«el álgebra rechazó esto» de «algo explotó», y una ronda de mutación terminaba en
un traceback en vez de un veredicto.

Lo encontró una corrida sobre un catálogo ajeno, no un test de acá: una medida le
pasaba a una escalar un campo que podía venir `null`, y como los lógicos ya no
cortocircuitan —§3, corregido esta mañana— la llamada ocurre siempre. Que el dato
sea malo es problema de quien escribió esa medida; que el error saliera crudo era
problema del álgebra.

Ahora el mensaje dice qué escalar falló, con qué argumentos y con qué excepción, y
lleva la ruta del nodo. Una escalar que ya habla el idioma del álgebra conserva su
mensaje: no se re-envuelve.

De paso, el test `test_la_distribucion_productiva_no_nombra_consumidores_conocidos`
me atrapó nombrando al consumidor en un comentario del núcleo. Tenía razón: el
núcleo no puede conocer a sus consumidores, y el comentario ahora dice «un catálogo
ajeno». Es la clase de regla que sólo sirve si se aplica a quien la escribió.

527 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de medidas 535/535 — 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — La gramática del id de un caso describía a ESTE catálogo, no al lenguaje

*commit f623d0c*

`ID_CASO_RE` entró como `^[0-9]{3}-[a-z0-9]+(?:-[a-z0-9]+)*$` porque así se llaman
los casos de este repositorio: tres dígitos, un guion, palabras.

Un consumidor real numera por dominio —`scatter-004-coberturas-distintas`,
`physics-tanda-001-…`— y **9 de sus casos dejaban de cargar**. La regresión no la
vio ninguna verificación de acá: se vio al correr el Oracle nuevo contra un
catálogo ajeno.

Es la misma trampa que la superficie tenía hasta anteayer, con otro disfraz:
derivar una regla del único catálogo que uno escribió describe al autor, no al
lenguaje. Y es exactamente el punto que las auditorías vienen marcando —que nadie
más que el autor escribió una medida—, apareciendo como un defecto concreto en vez
de como una observación.

La gramática ahora exige lo que hace falta para que un id sea portable y ordenable
y nada más: minúsculas ASCII, dígitos y guiones simples, con al menos un número
adentro. Sigue rechazando `002-vencida-con-dueño`, `Caso-001`, `sin-numero`,
`doble--guion` y `con_guion_bajo`. Hay un test que carga los ids del consumidor
para que la gramática no se vuelva a angostar sola.

528 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de medidas 535/535 — 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — El README publicaba un «cero sobrevivientes» que hoy no se puede volver a obtener

*commit e9e9989*

La nota decía, con fecha 2026-08-03: «los 16 objetivos de la matriz del CI salen
en VERDE: cero sobrevivientes, cero errores de arnés». Desde entonces el núcleo
pasó de ~2900 a más de 5500 líneas —la superficie infija y la del corpus son casi
1400— y ese código **nunca se mutó**.

Al intentarlo aparecieron tres cosas encadenadas, y las tres están arregladas en
los commits anteriores:

  1. la ronda no arrancaba (línea base roja: un test le preguntaba a git dentro de
     una copia sin `.git`);
  2. arreglado eso, crasheaba con un traceback en vez de dar un veredicto;
  3. arreglado eso, 51 de 193 mutantes salían «error de arnés» porque el tipo de
     error del lenguaje no se podía re-lanzar desde Python.

La cuarta corrida fue concluyente: **193 mutantes · 136 muertos · 57 sobrevivientes
· 0 timeouts · 0 errores de arnés**.

Los 57 quedan publicados con su reparto —38 constantes de posición, 9 comparadores
de borde, 8 booleanos, 2 retornos— en vez de dejar arriba una afirmación verde de
hace tres semanas sobre un código que en su mayoría todavía no existía.

Una cifra que no se puede volver a obtener no es una medición, es un recuerdo. Y
el proyecto tiene una medida para eso: `proceso.verificacion_vigente`.

528 tests OK

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Fija posiciones de la superficie de casos

*commit f5a03b4*



## 2026-08-25 — proceso: incorporar medida proceso.codigo_con_mutante_que_lo_mata y sus casos de corpus

*commit 1cb53c1*



## 2026-08-25 — Saca el informe

*commit bf231f9*



## 2026-08-25 — Merge branch 'juzga-codigo'

*commit db5f237*



## 2026-08-25 — Merge branch 'juzga-codigo': alguien juzga por fin los sobrevivientes de la mutación de código

*commit 6e220a2*

El proyecto tiene dos mutaciones. La de MEDIDAS la juzga
`proceso.test_con_mutante_que_lo_mata`. La de CÓDIGO no la juzgaba nadie:

    mutantes: 193 · murieron 136 · sobrevivieron 57
      ✓ proceso.ronda_mutacion_concluyente     0 (<= 0)
      ✓ proceso.arnes_con_bytecode_frio        0 (<= 0)
      1 medida(s) NO pudieron juzgar esta evidencia

**Dos verdes y 57 agujeros adentro.** Las dos que aplicaban comprueban que la
ronda fue CONCLUYENTE —que no hubo timeouts ni errores de arnés—, que es una
condición previa y no el resultado. La medida escrita para contar sobrevivientes
pide `detecciones_conductuales`, un campo que sólo tienen los mutantes de medida.

`proceso.codigo_con_mutante_que_lo_mata` cuenta los que pasaron la suite sin estar
declarados equivalentes. Verificada contra la evidencia REAL de una ronda, no
contra una sintética:

    ronda real (193 mutantes)      → ROJO, valor 61
    ronda sin sobrevivientes       → verde
    todos declarados equivalentes  → verde
    ronda vacía                    → SIN EVIDENCIA

Ese último renglón es el caso `019` del corpus: una ronda sin mutantes declarada
verde. Lo cierra `requiere`.

Cinco casos en las dos polaridades, incluido uno que fija que un equivalente
declarado **con su razón escrita** no es ni muerte ni sobreviviente: es una
decisión.

Trabajo delegado a Gemini 3.7 Flash (high). Espejó además en `tools/mutar.py` el
mismo arreglo que hice en `mutar_codigo.py` —evaluar cada medida sin atajar nada
terminaba la ronda en un traceback— y tiene razón: era la misma falla en la otra
mitad.

528 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de medidas 547/547 — 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Merge branch 'main' into matar-vivos

*commit 0e0d900*

# Conflicts:
#	README.md

## 2026-08-25 — Saca el informe

*commit bf59522*



## 2026-08-25 — El plan del lenguaje se pone al día: entró un ítem que no preveía

*commit b8ec839*

`PLAN-LENGUAJE.md` mencionaba la superficie una sola vez, el día después de que
Oracle pasara a escribirse en ella. Entra como ítem **(f)**, con lo que costó y
con lo que enseñó.

Lo que costó, dicho sin maquillar: el corpus bajó de 3300 líneas a 1823 y el
núcleo subió ~1400. La proporción publicada pasó de 13,0 a más de 26 a 1, y buena
parte de ese salto es FORMATO y no lenguaje —las mismas 33 medidas bajaron de 298
a 203 líneas por escribirse de otra manera—. Queda como defecto abierto de la
métrica, sin arreglar, porque arreglarlo bajaría el costo publicado.

Lo que enseñó vale más que la superficie, y son dos casos de la MISMA falla:

  · `--verificar` decía «33 medidas, ida y vuelta OK» sobre 33 medidas que
    escribió una sola persona. Rompiendo el impresor —`<` impreso como `<=`— el
    verificador entero salía verde: ninguna medida del catálogo usa un `<` pelado.
  · `ID_CASO_RE` entró como `^[0-9]{3}-…` porque así se llaman los casos de acá, y
    rechazaba 9 casos de un consumidor real. No lo vio ninguna verificación
    propia: se vio corriendo Oracle contra un catálogo ajeno.

**Una regla derivada del único catálogo que uno escribió describe al autor, no al
lenguaje.** Es lo que las auditorías vienen marcando, apareciendo dos veces en dos
días como defecto concreto.

Y (e.1) deja de estar PARCIAL: son ocho propiedades metamórficas, no cinco.

Al final, la medición que gobierna el plan queda cerrada con su resultado: dos
consumidores conectados y **ni una línea de `nucleo/algebra.py` tocada para que
entraran**. Con algo mejor que el número al lado — una medida universal juzgó un
catálogo que su autor no escribió y encontró tres defectos reales, uno de ellos un
verde sobre cero evidencia.

528 tests OK

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Merge branch 'matar-vivos'

*commit 47a5fe7*



## 2026-08-25 — Merge branch 'matar-vivos': los 57 sobrevivientes de `nucleo/caso.py`, cerrados

*commit 7e9f6a3*

La superficie del corpus entró hace tres días con 425 líneas que nunca se habían
podido mutar. La primera ronda concluyente dio 57 vivos, casi todos en la
aritmética de posición: la superficie prometía decir «archivo, línea y columna» y
nada fijaba que la posición fuera la correcta.

    mutantes: 187 · murieron 187 · sobrevivieron 0 · timeout 0 · errores de arnés 0
      ✓ proceso.codigo_con_mutante_que_lo_mata     0 (<= 0)
      ✓ proceso.ronda_mutacion_concluyente         0 (<= 0)
      ✓ proceso.arnes_con_bytecode_frio            0 (<= 0)

Reparto de los 57: **51 tests nuevos, 6 equivalentes declarados con su razón, 0
código muerto, 0 bugs.**

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh).

## Lo que verifiqué antes de integrar, y por qué justo eso

Declarar un mutante equivalente es la manera de simular una ronda limpia, así que
los 6 no se aceptan por argumento. Revisé dos por fuerza bruta:

  · `fin < 0` → `fin < 1` después de `startswith("clave(")`: si el texto empieza
    con `clave(`, la posición 0 es una `c`, así que `find(")")` no puede dar 0
    nunca. Imposible por construcción, no por convención.
  · `while i < len(texto)` → `<=` en `_valores_fila`: reimplementé el bucle con la
    mutación y comparé contra el original sobre **11.895 entradas generadas**.
    Cero diferencias de conducta.

Y la ronda la corrí yo, sobre la rama ya mergeada con `main`, en vez de creerle al
informe: mismo resultado.

Queda una cosa dicha y no tapada: `proceso.test_con_mutante_que_lo_mata` sigue sin
poder juzgar esta evidencia —pide campos que sólo tienen los mutantes de medida—.
Ya no importa para el veredicto, porque `proceso.codigo_con_mutante_que_lo_mata`
cubre ese eje; se informa igual en vez de silenciarse.

533 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de medidas 547/547 · de código 187/187 — 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — fijar mutantes en nucleo/version.py y nucleo/macro.py

*commit faa7b3a*



## 2026-08-25 — Saca el informe

*commit 83da666*



## 2026-08-25 — Merge branch 'mutar-version'

*commit c35c9d6*



## 2026-08-25 — Merge branch 'mutar-version': `version.py` y `macro.py`, fijados

*commit 4402896*

Dos archivos que la mutación de código nunca había tocado. `version.py` es
enteramente nuevo —gobierna si un `oracle.json` puede pedir un álgebra que este
núcleo no implementa, y si un `.oracle` escrito contra otra versión de la
superficie carga— y `macro.py` cambió 80 líneas en tres días.

    nucleo/version.py    15 mutantes · 15 muertos · 0 sobrevivientes
    nucleo/macro.py      85 mutantes · 85 muertos · 0 sobrevivientes

Sólo dos sobrevivientes en total, los dos por falta de test, ninguno equivalente,
ningún bug:

  · `@dataclass(frozen=True)` → `False` en `Version`: nada ejercitaba la
    inmutabilidad de la clase.
  · `x.suffix in EXTENSIONES_DE_MACRO and x.is_file()` → `or` en `cargar_macros`:
    ningún test pasaba un directorio con archivos de otra extensión ni un
    subdirectorio con nombre de macro.

**Y mi predicción falló, que es lo que hay que decir.** Al encargar la tarea
apunté a las comparaciones de borde de `version.py` —`MAYOR` igual, `MENOR` mayor
o igual— porque ahí un `>=` mutado a `>` deja pasar exactamente una versión. No
sobrevivió ninguna: los tests de compatibilidad ya estaban pegados al límite. La
zona que yo señalé como frágil era la más firme del archivo.

Corrí la ronda de `version.py` por mi cuenta antes de integrar: mismo resultado.

Trabajo delegado a Gemini 3.7 Flash (high).

535 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de código: version 15/15 · macro 85/85 — 0 sobrevivientes

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — fijar rutas del algebra: 17 mutantes muertos por tests y 4 equivalentes declarados

*commit 5d713a9*



## 2026-08-25 — wip: ruta del de

*commit 994eca6*



## 2026-08-25 — Merge branch 'mutar-algebra' into ruta-de

*commit 21addec*



## 2026-08-25 — Un error dentro de un `unir` no decía dónde: el mapa de fuente tenía un agujero

*commit 22210f9*

`_unir` calculaba `ruta_izq` y `ruta_der` con cuidado y se las pasaba a `aplicar`,
donde el brazo del `de` las **descartaba**. Un error en cualquiera de los dos
lados de un `unir` salía sin ruta, y `fragmento_de_error` respondía «no se
encontró la ruta» en vez de señalar la línea.

    antes:  la relación «ausente» no existe en la evidencia
            (ruta: None)

    ahora:  la relación «ausente» no existe … en `2.1.2`
               3 |     unir ausente y
                 |          ^

## Cómo se encontró, que es la parte que importa

**Lo denunció la mutación de código, no una persona.** Cuatro mutantes sobre
`ruta_izq`/`ruta_der` sobrevivían —incluido cambiar el índice `1` por el `2`, que
haría al error señalar el operando equivocado— porque el valor calculado no
llegaba a ninguna parte.

Y estuvieron a punto de entrar declarados como **equivalentes**, con cuatro
razones bien argumentadas y **factualmente correctas**: es cierto que ningún test
podía distinguirlos. Lo comprobé y la conclusión se sostenía.

Pero la lectura era la otra. **Un mutante que no se puede matar porque su
resultado no se usa no es equivalente: es código que quería hacer algo y no lo
hacía.** La pregunta correcta no era «¿por qué no lo distingo?» sino «¿por qué
este cálculo no se observa?», y la respuesta era un defecto. Las cuatro
declaraciones se retiran de `equivalentes.json`.

Comprobado uno por uno: aplicando cada uno de los cuatro mutantes a mano, los
cuatro **mueren** ahora.

## Los dos extremos

  · `nucleo/algebra.py` — el brazo del `de` en `aplicar` prefija la ruta que
    recibe antes de relanzar el error;
  · `nucleo/sintaxis.py` — las FUENTES entran al mapa. El `unir` es
    izquierdo-asociativo, así que con tres fuentes la primera queda en `2.1.1.1`,
    la segunda en `2.1.1.2` y la tercera en `2.1.2`. Media promesa cumplida es
    peor que ninguna: el error sabía dónde estaba y el mapa no sabía traducirlo.

Un test exige que las tres fuentes den rutas **distintas** —si coincidieran,
cambiar el índice 1 por el 2 volvería a ser indistinguible— y otro va de punta a
punta, del error del álgebra al caret debajo del nombre de la relación.

Los 17 tests restantes de la ronda son de Gemini 3.7 Flash (high), que hizo el
trabajo grueso sobre los otros mutantes.

    nucleo/algebra.py: 323 mutantes · 323 muertos · 0 sobrevivientes
                       0 equivalentes declarados

541 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de medidas 547/547

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Merge branch 'ruta-de'

*commit 1431bc9*



## 2026-08-25 — fijar reificación y contratos de medida: 25 mutantes muertos por tests

*commit 8e33b88*



## 2026-08-25 — Merge branch 'mutar-medida'

*commit 5daf40a*



## 2026-08-25 — Merge branch 'mutar-medida': la reificación deja de ser el código menos fijado del núcleo

*commit 6b8d121*

`nucleo/medida.py` cambió 345 líneas en tres días y la ronda dio 25 sobrevivientes.
No estaban desparramados: **veinte de los veinticinco eran la REIFICACIÓN** —
`_tipo`, `_pasos_de`, `_fuentes`, `_fuentes_de_medida`, `_hecho_medida`, `_ruta`,
`_cabeza`, `_terminos`, `evidencia_con_derivadas`—, la maquinaria de
`como_hechos()` que convierte el catálogo en hechos para que las medidas puedan
hablar de medidas.

O sea: la mitad que hace de esto un META lenguaje era la peor fijada. Siete
mutantes vivos en `_tipo` solo: una medida L2 podía clasificar mal el tipo de un
nodo —decir «numero» donde hay un booleano, y en Python un `bool` ES un `int`— y
ninguna medida meta se enteraba.

    nucleo/medida.py: 181 mutantes · 181 muertos · 0 sobrevivientes
                      0 equivalentes declarados

Los 25 cayeron en la misma categoría: **falta un test**. Ninguno equivalente,
ninguno código muerto, ningún bug. Es un buen resultado y no era el esperado: en
la ronda de `algebra.py`, hoy mismo, cuatro «equivalentes» resultaron ser un
defecto de cableado.

Trabajo delegado a Gemini 3.7 Flash (high). Corrí la ronda por mi cuenta antes de
integrar: mismo resultado.

549 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de medidas 547/547

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Rescate del trabajo de codex sobre nucleo/sintaxis.py

*commit a01ea2a*

605 lineas de tests, tres cambios al nucleo (uno de ellos un IndexError real) y
la columna esperada de un caso corregida. Codex se quedo sin cuota a mitad.

## 2026-08-25 — Merge branch 'main' into mutar-sintaxis

*commit a44e49b*



## 2026-08-25 — `proyecto.py` y `cifras.py`, fijados: 1 sobreviviente entre los dos

*commit f0dcb84*

Dos objetivos de la matriz que nunca se habían mutado, y los dos cambiaron fuerte
esta semana: `proyecto.py` (84 líneas en 3 días) resuelve y confina las rutas de
un proyecto y guarda las dos gramáticas de id; `cifras.py` (126 líneas) publica
los números del README.

    nucleo/proyecto.py   1 sobreviviente · categoría «falta un test»
    tools/cifras.py      0 sobrevivientes

**El confinamiento aguantó entero.** Pedí explícitamente casos que escaparan de
verdad —symlinks apuntando afuera, `..` en la ruta— porque la ruta feliz no
distingue un confinamiento bueno de uno roto, y no sobrevivió ningún mutante ahí.
Tampoco en las gramáticas de id.

El único hueco estaba en otro lado: la restauración del registro global de
escalares cuando se usa un registro de instancia (`is not` → `is`). Nada
ejercitaba esa garantía de limpieza.

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh). El commit lo hice yo: su
sandbox volvió a no poder escribir el gitdir del worktree.

542 tests OK

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-25 — Merge branch 'mutar-proyecto'

*commit 2a31004*



## 2026-08-25 — fijar ultimos 15 mutantes de sintaxis.py: 0 sobrevivientes y 2 equivalentes declarados

*commit 4ba99e3*



## 2026-08-25 — agregar INFORME.md de mutacion de sintaxis.py

*commit 24a02d4*



## 2026-08-26 — Saca el informe

*commit dd91321*



## 2026-08-26 — Merge branch 'main' into mutar-sintaxis

*commit 807efb7*

# Conflicts:
#	README.md

## 2026-08-26 — El sandbox de UDFs era invisible para la mutación, y promete más de lo que puede

*commit 9ad2f2a*

Dos hallazgos encadenados sobre `nucleo/aislamiento/escalares.py` —411 líneas que
son lo único que hace que `--confiar-escalares` sea distinto de ejecutar código
ajeno a ciegas—.

## 1 · No era objetivo del arnés

`objetivos_disponibles()` usaba `glob("*.py")` sobre `nucleo/`, **no recursivo**.
El módulo vive en un subpaquete, así que no se mutaba, y nadie lo notaba porque el
informe sólo habla de lo que sí miró.

Es el MISMO defecto que tenía el numerador de `tools/cifras.py`, arreglado el
2026-08-03 con estas palabras: «mover el archivo una carpeta más adentro» no puede
ser una manera de salir del criterio de falsación. **Se arregló el lado que CUENTA
y no el que MIDE**, así que esas 411 líneas figuraban en la proporción publicada
y no las fijaba nada.

Tres tests lo cuidan, incluido uno que exige que EXISTA algún objetivo en un
subpaquete: sin eso el test pasaría igual con `glob`.

Primera ronda: **126 mutantes · 65 muertos · 61 sobrevivientes**. La peor
proporción del proyecto, en la frontera de seguridad.

## 2 · Y sondeándolo a mano, una fuga real

Una UDF hostil **puede fichar el disco por metadatos**. Medido:

    ¿existe /etc/shadow?          True
    tamaño de ~/.bashrc           535
    permisos de /etc/passwd       0o100644
    ¿cuántos repos en ~/Dev?      4

No lee contenido —eso sí está bloqueado— pero averigua existencia, tamaños,
permisos y fechas de cualquier ruta, y lo devuelve por el canal JSON como
cualquier otro valor.

**No es un descuido del hook: `os.stat` no emite ningún evento auditable en
CPython.** PEP 578 cubre `open`, `os.listdir`, `os.scandir`, los que mutan el
árbol, procesos y sockets, pero no la consulta de metadatos. Un `addaudithook` no
puede interceptar lo que nunca se anuncia.

Se podría poner un `os.stat` sombra en el trabajador y sería teatro: `from posix
import stat` lo esquiva en una línea. Este repositorio prefiere un límite
DECLARADO a una defensa que aparenta.

Lo que cambia entonces son las afirmaciones, que decían de más:

  · el docstring del módulo decía «niega acceso a archivos fuera del proyecto»;
  · `ESCRIBIR-UNA-MEDIDA.md` decía que el trabajador «puede leer el proyecto,
    Oracle y la biblioteca estándar», dando a entender que nada más.

Y hay un test que fija el límite **incluida la fuga**: si algún día se cierra de
verdad, `test_los_metadatos_se_filtran_y_esta_declarado` FALLA y obliga a
actualizar la declaración, en vez de dejarla envejecer diciendo de menos.

551 tests OK · SINTAXIS 21 bloques de documentación

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — Merge branch 'limite-sandbox'

*commit f2a20c2*



## 2026-08-26 — Merge branch 'mutar-sintaxis': el archivo más grande del núcleo, en cero

*commit b785e4e*

`nucleo/sintaxis.py` son 1026 líneas —el lector, el parser, el impresor y el mapa
de fuente de la superficie infija— y hasta anteayer nunca se habían mutado.

    623 mutantes · 623 muertos · 0 sobrevivientes · 2 equivalentes declarados

Salió en dos tandas y con dos agentes distintos. Codex escribió 605 líneas de
tests y encontró un bug de verdad antes de quedarse sin cuota:

    cuerpo[min(len(cuerpo), esperado - 1)]      →  IndexError crudo
    cuerpo[min(len(cuerpo) - 1, esperado - 1)]

Un `ninguno` con menos líneas de cuerpo de las esperadas **reventaba con
`IndexError`** en vez de dar un error de sintaxis: el parser se caía con entrada
mal formada, que es lo que una superficie no puede hacer. Los otros dos cambios
suyos sacan ramas inalcanzables.

Gemini 3.7 Flash cerró los 15 que quedaban. Los dos equivalentes que declaró son
del impresor de expresiones —`padre: int = 0 → 1` y la precedencia de `no`,
`4 → 5`— y los verifiqué por fuerza bruta antes de aceptarlos: **89.383 árboles
de expresión generados, cero diferencias de texto**. Son legítimos, y por una
razón distinta a la del caso de ayer: acá el valor SÍ se usa, sólo que la
constante cae en un hueco de la escala de precedencia. Si alguna vez entra un
operador entre los comparadores y `no`, dejan de serlo.

La ronda de verificación la corrí yo sobre la rama ya mergeada con `main`: mismo
resultado.

559 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de código: sintaxis 623/623

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — El arnés de mutación no veía el subpaquete del núcleo

*commit b385cee*

`objetivos_disponibles()` usaba `glob("*.py")` sobre `nucleo/`, no `rglob`. Con eso
`nucleo/aislamiento/escalares.py` —411 líneas, el confinamiento de las UDF de un
proyecto— **no era objetivo del arnés**: no se mutaba, y no se notaba porque el
informe sólo habla de lo que sí miró.

Es el MISMO defecto que tenía el numerador de `tools/cifras.py`, arreglado el
2026-08-03 con estas palabras: «mover el archivo una carpeta más adentro» no puede
ser una manera de salir del criterio de falsación. Se arregló el lado que CUENTA
y no el que MIDE, así que esas líneas figuraban en la proporción publicada y no
las fijaba nada.

Tres tests lo cuidan:

  · todo `.py` de `nucleo/` es objetivo del arnés;
  · **existe al menos un objetivo en un subpaquete** — sin esto el primer test
    pasaría igual con `glob` y no discriminaría nada;
  · todo objetivo del núcleo declara sus tests prioritarios, porque sin eso cada
    mutante corre la suite entera y la ronda se vuelve impagable.

562 tests OK

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — Merge branch 'mutar-aislamiento'

*commit acf0a13*



## 2026-08-26 — Cierra en cero la mutación de código de los siete módulos restantes del núcleo

*commit 3d3ab5f*



## 2026-08-26 — Saca el informe

*commit e6d76b6*



## 2026-08-26 — Merge branch 'main' into mutar-resto

*commit 8344be9*



## 2026-08-26 — Actualiza las cifras tras traer main

*commit 3e39351*



## 2026-08-26 — Merge branch 'mutar-resto'

*commit 550b9d9*



## 2026-08-26 — Merge branch 'mutar-resto': los siete módulos que faltaban, en cero

*commit 887327e*

Cierra la matriz de mutación de código salvo el sandbox, que va aparte.

    grafo.py         4/4        marco.py       35/35     dominio.py     19/19
    diferencial.py  48/48       simulacion.py  50/50     fixtures.py   131/131
    mutacion.py    153/153
    ────────────────────────────────────────────────────────────────
    total          440 mutantes · 440 muertos · 0 sobrevivientes

Sólo cinco sobrevivientes iniciales entre los siete, todos por falta de test:
cuatro en `mutacion.py` y uno en `fixtures.py`. Cero equivalentes declarados,
cero código muerto, cero bugs — que era lo esperable: son los módulos más viejos
y los más ejercitados por el resto de la suite.

`nucleo/mutacion.py` es el que más importaba de los siete: es el mutador de
MEDIDAS, o sea el mecanismo que mide a todos los catálogos. Que tuviera cuatro
mutantes vivos quería decir que el medidor no estaba medido.

Trabajo delegado a Gemini 3.7 Flash (high). Corrí por mi cuenta las dos rondas más
grandes —`mutacion.py` 153/153 y `fixtures.py` 131/131— antes de integrar.

## Y de paso, el motor de mutación mismo

    perfiles/python/mutacion_codigo.py: 205 mutantes · 205 muertos · 0 vivos

984 líneas, el arnés que corre todas las rondas anteriores. Si ahí hubiera
sobrevivientes, todo el aparato que mide al resto descansaría sobre código que
nadie fija. No los hay.

564 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de medidas 547/547

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — El sandbox de UDFs queda fijado: 126/126, y era el peor del proyecto

*commit f7acea9*

`nucleo/aislamiento/escalares.py` son 411 líneas y es lo único que hace que
`--confiar-escalares` sea distinto de ejecutar código ajeno a ciegas. La primera
ronda —la primera de su vida, porque el arnés no lo veía— dio **61 sobrevivientes
de 126: 48%**, contra 6,5% de `algebra.py` y 2,4% de `sintaxis.py`. La frontera de
seguridad era el código menos fijado que había.

    126 mutantes · 126 muertos · 0 sobrevivientes · 0 equivalentes declarados

878 líneas de tests nuevos en `tests/test_aislamiento_escalares.py`. Los 61
cayeron todos en «falta un test»: ninguno equivalente, ninguno código muerto, y
—esto es lo que más quería saber— **ninguna puerta que no cerrara.**

Lo confirmé aparte de la mutación, volviendo a sondear el confinamiento con doce
intentos de fuga: contenido de archivos, `os.listdir`, `open` por descriptor,
sockets, `fork`, `shutil.copy`, `/proc/self/environ` y `ctypes` siguen todos en
`PermissionError`. Lo único que pasa son los metadatos, que es la fuga ya
declarada y con su test propio.

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh). El commit lo hice yo: su
sandbox no puede escribir el gitdir del worktree —tercera vez hoy—. Corrí la ronda
por mi cuenta antes de integrar: mismo resultado.

## Con esto cierra la matriz

    19 de 19 objetivos en cero sobrevivientes

Es la primera vez desde que el núcleo creció de ~2.900 a ~5.700 líneas. La
afirmación que el README publicaba con fecha del 3 de agosto vuelve a ser cierta,
y ahora con el sandbox adentro, que en aquel momento ni siquiera era visible para
el arnés.

576 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de medidas 547/547 · de código 19/19 objetivos

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — Actualiza cifras y paquete de estudio

*commit b91a3eb*



## 2026-08-26 — cli: entry point unificado oracle para inicialización, autoría y suite de verificación

*commit 0e09d63*



## 2026-08-26 — Saca el informe

*commit f7d2a68*



## 2026-08-26 — Merge branch 'main' into oracle-cli

*commit c15f7ae*

# Conflicts:
#	README.md

## 2026-08-26 — Los tests del CLI dejan de ensuciar la salida de la suite

*commit ed3235b*

Capturaban `cli.main` pero llamaban `cmd_init`, `cmd_nueva` y `cmd_caso` directo,
así que la ayuda del comando salía mezclada con el resumen: `unittest -q | tail -3`
mostraba «Creá una medida» en vez de «OK».

## 2026-08-26 — Merge branch 'errores-amables': el error dice qué hacer, no sólo qué se esperaba

*commit 834d514*

Caminé los diez tropiezos de alguien escribiendo su primera medida. **Cuatro
terminaban en un mensaje cierto e inútil**: nombran la gramática y dejan a la
persona en el mismo lugar donde estaba.

    usa = en vez de ==
      antes  se esperaba expresión; llegó '='
      ahora  la comparación se escribe «==», no «=»; «=» sola no es un operador
             del lenguaje

    campo con acento
      antes  se esperaba expresión; llegó 'í'
      ahora  «í» no puede ir en un nombre: relaciones, alias y campos usan
             minúsculas ASCII, dígitos y `_`. La prosa de `porque` y `alcance` sí
             lleva acentos y eñes

    olvida una línea del cuerpo
      antes  se esperaba 4 líneas de cuerpo para ninguno
      ahora  a la macro ninguno le falta `alcance`. Su cuerpo son estas 4 líneas,
             en este orden: de, donde, umbral, alcance

    umbral con ==
      antes  se esperaba la macro ninguno con umbral <= 0
      ahora  …su umbral es siempre «<= 0» y llegó «== 0»; y un umbral de igualdad
             está prohibido en todo el catálogo, porque no deja borde para la
             mutación —ver `meta.ningun_umbral_de_igualdad`

Ese último es **condicional**: con `<= 1` no menciona la prohibición de igualdad,
porque sumarla ahí mezcla dos problemas distintos y confunde.

Dos cuidados que valen tanto como los mensajes:

  · **la posición sigue siendo exacta.** Un mensaje amable que señala la línea
    equivocada es peor que uno seco que acierta. El caso del cuerpo vacío apuntaba
    a una línea que no existe; ahora apunta a la 2, donde empieza el cuerpo.
  · **el del acento aclara que la prosa SÍ los lleva.** Sin esa frase el mensaje
    asusta de más y alguien termina escribiendo el `porque` sin tildes.

Siete tests fijan cada mensaje Y su posición, con el criterio escrito: tiene que
contener lo que hay que hacer, no sólo lo que se esperaba.

Dos cosas se rompieron y las dos son el mecanismo funcionando: seis tests fijaban
los mensajes viejos —actualizados mirando las posiciones reales, no a ojo— y dos
equivalentes quedaron vencidos porque las ediciones corrieron las líneas del
archivo. Reapuntados, con la fragilidad del id posicional anotada en su razón.

Ronda de verificación: `nucleo/sintaxis.py` 641 mutantes · 641 muertos · 0 vivos.

589 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de medidas 547/547

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — Merge branch 'main' into oracle-cli

*commit 50cf4d7*



## 2026-08-26 — Merge branch 'oracle-cli'

*commit 20be004*



## 2026-08-26 — Merge branch 'oracle-cli': un solo comando, y el criterio se cumple

*commit 85bf32c*

El objetivo declarado por el dueño del proyecto: «que Oracle sea fácil de
scriptear y ejecutar los tests, para que pueda ser un humano quien escriba las
medidas y ejecute los test. Oracle tiene que ser una herramienta compartida entre
humanos y LLMs.»

No lo era, y no por falta de capacidades: estaban todas, repartidas en 16 archivos
que había que conocer de antemano. Caminando el recorrido de una persona que
empieza de cero, la primera pared llegaba en el primer comando:

    $ mkdir mi-proyecto && cd mi-proyecto
    $ python .../tools/medida.py --proyecto . --nueva tareas.vencida
    PROYECTO INVÁLIDO — le falta `catalogos/`

Y ahí terminaba: el mensaje dice qué falta, no cómo crearlo, y no existía
`oracle init`. Después venían ocho comandos que hay que correr en orden y de
memoria, cada uno con `--proyecto` y a veces `--confiar-escalares`, sin un
`oracle test` que los junte.

Ahora hay un entry point único que **envuelve lo que ya existe**, sin reescribir
ninguna herramienta:

    oracle init · nueva · caso · revisar · test · relaciones · escalares · expandir

`oracle test` corre la secuencia, **saltea con una línea explícita lo que no
aplica** —«DIFERENCIAL: salteado (el proyecto no tiene fixtures todavía)», que no
es una falla— y cierra con un veredicto de una línea. Con `--rapido` saltea la
mutación **y lo dice en el veredicto**, porque un verde que omitió la verificación
más fuerte no es el mismo verde.

## El criterio era falsable, y lo caminé yo

> alguien que nunca vio el repositorio tiene que poder escribir su primera medida,
> ponerla en rojo con un caso, y verla en verde — sin abrir un archivo de Oracle.

Desde un directorio vacío: `init` → `nueva` → `caso` → llenar las dos plantillas
→ `test`. **VEREDICTO: VERDE (completo: todas las verificaciones en regla, 0
mutantes sobrevivientes).** Nunca hubo que abrir el repositorio.

Trabajo delegado a Gemini 3.7 Flash (high).

## Una cosa que arreglé antes de integrar

Los tests del CLI capturaban `cli.main` pero llamaban `cmd_init`, `cmd_nueva` y
`cmd_caso` **directo**, así que la ayuda del comando salía mezclada con el resumen
de la suite: `unittest -q | tail -3` mostraba «Creá una medida» en vez de «OK». Un
test que ensucia la salida hace ilegible justo lo que uno mira cuando algo falla.

597 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN de medidas 547/547

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — caso: los errores dicen que hacer, validan conjuntos cerrados y conservan posicion exacta

*commit 9371553*



## 2026-08-26 — docs: informe de mejoras de sintaxis y reporte de errores de casos

*commit aa6537a*



## 2026-08-26 — Documentar instalacion de oracle

*commit 941b222*



## 2026-08-26 — Saca el informe

*commit 72e821e*



## 2026-08-26 — Saca el informe

*commit c018f43*



## 2026-08-26 — Merge branch 'instalar-uv'

*commit 9158ef2*



## 2026-08-26 — Merge branch 'instalar-uv': `oracle` se instala, y los consumidores tienen su reemplazo

*commit eb2797f*

El comando existía desde ayer y **no había forma dicha de instalarlo**: la única
documentada seguía siendo invocar por ruta al checkout. Ahora está escrito arriba
de todo, antes de la primera medida:

    uv tool install .        deja `oracle` en el PATH — 333 ms, medido
    uvx --from . oracle      probarlo sin instalar nada
    pip install -e .         para quien no tenga uv

`uv` es lo que corresponde acá con un matiz que conviene decir: el proyecto tiene
**cero dependencias** (`dependencies = []`, `requires-python = ">=3.11"`), así que
la ventaja no es la resolución sino que `uv tool install` y `uvx` hacen trivial el
«probalo sin instalar nada».

**No entra `uv.lock`, y el argumento está escrito**: un lock de runtime sólo
congelaría la ausencia de dependencias. Lo único que sí se resuelve es el backend
de build (`setuptools>=68`), que ya está declarado en `[build-system]` y queda
cubierto por la prueba de wheel.

## El empaquetado, comprobado y no supuesto

Ya hubo un agujero esta semana: `package-data` listaba `macros/*.json` cuando las
macros habían pasado a `.oracle`, y una instalación por wheel se quedaba sin
biblioteca estándar. Un empaquetado incompleto no lo nota ningún test de la suite,
así que ahora hay uno que lo fija —`test_wheel_instalado_trae_datos_y_ejecuta_oracle_test`—
que construye el wheel, lo instala en un entorno limpio y corre `oracle test` ahí
adentro.

Lo repetí por mi cuenta antes de integrar: `uv venv` + `uv pip install .` + `init`
+ `nueva` + `test` desde un directorio vacío, todo desde el binario instalado.

## Los consumidores: el reemplazo, comparado veredicto contra veredicto

    antes  python vendor/oracle/tools/{corpus,aceptacion,diferencial,mutar}.py \
             --proyecto medidas --confiar-escalares        (cuatro comandos)
    ahora  oracle test --proyecto medidas --confiar-escalares

En Jam los dos dan **ROJO por lo mismo**: `medidas/diferencial/vault.json`
vencido, que es una deuda previa de Jam y no de Oracle. Que coincidan es la prueba
de que el comando sirve para alguien que no lo escribió.

Queda dicho un límite del comando: `oracle test` **no regenera fixtures
diferenciales**. Los dos consumidores tienen emisores propios que hay que correr
cuando cambia su catálogo o su referencia. Es un hueco del comando, no de ellos.

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh), que no escribió una línea en
Jam ni en LyraGASP —tienen trabajo del usuario sin commitear— y sólo comparó.

598 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — Merge branch 'caso-errores': el `.caso` también dice qué hacer

*commit cce328a*

`ESCRIBIR-UNA-MEDIDA.md` manda escribir el caso del corpus ANTES que la medida —y
con razón: una medida escrita primero se escribe para pasar, no para atrapar—. O
sea que un `.caso` es lo PRIMERO que tipea una persona, y ahí un mensaje malo sale
más caro que en ningún otro lado.

Medí seis tropiezos y cuatro estaban mal. El peor no era feo, era **engañoso**:

    etiqueta inventada
      antes  ⚠ NO FALLA al leer — el error llegaba recién al correr `oracle test`,
             con el archivo entero ya escrito
      ahora  línea 7, columna 15: se esperaba etiqueta en ['deuda_de_diseño',
             'falso_rojo', 'falso_verde', …]

    campos sin coma  (`tarea: id vencida`)
      antes  se esperaba 1 valores de fila; llegó '"t-1", true'
             ← entendía UN campo llamado «id vencida» y contaba 1 sobre una fila
               de dos: la persona no puede entender eso
      ahora  se esperaba ',' entre campos; llegó 'vencida'

    fila con menos columnas
      antes  se esperaba 2 valores de fila
      ahora  la relación «tarea» declara 2 campos (id, vencida) y esta fila trae 1

    valor sin comillas
      antes  se esperaba fin de valor JSON; llegó '-08-26'
      ahora  se esperaba texto entre comillas

Las listas de `etiqueta` y `como_se_detecto` quedan en **una sola fuente**
(`nucleo/caso.py`), con un test que exige que `tools/corpus.py` use el MISMO
objeto: dos copias divergen, y eso es el caso `012` del corpus.

Trabajo delegado a Gemini 3.7 Flash (high).

## Una decisión suya que revertí

La plantilla del andamio pasó a traer `etiqueta: falso_verde` y
`como_se_detecto: mutacion` puestos, para que parseara. Es un retroceso: esos dos
campos no son decorativos —la etiqueta decide la polaridad del caso y
`como_se_detecto` alimenta una cifra que el README publica— y **un default creíble
se queda sin pensar**, que es peor que un error.

Vuelven a ser marcadores. Eso hace que la plantilla entregada NO parsee, contra el
principio que ya estaba escrito para la plantilla de medida, y la tensión se
resuelve por el otro lado: **el andamio ahora lista los valores válidos al crear el
archivo**, cuando la persona todavía tiene fresco lo que pasó, y el error los
enumera igual para quien llegue por otro camino. Tres tests fijan ese contrato.

    $ oracle caso tareas/001-prueba
    Reemplazá los marcadores en MAYÚSCULAS. Dos tienen valores cerrados:
      etiqueta:         deuda_de_diseño · falso_rojo · falso_verde · …
      como_se_detecto:  accidente · herramienta_ajena · mutacion · observacion · persona

605 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN `nucleo/caso.py` 206/206

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — docs: reemplazar invocaciones por ruta hacia el comando oracle

*commit 942593e*



## 2026-08-26 — `oracle test` deja de dar VERDE callando dos verificaciones

*commit 47e7d45*

Sobre el propio repositorio, el comando terminaba así:

    VEREDICTO: VERDE (rápido: se salteó la mutación)

y **nunca había corrido** los 605 tests unitarios ni la mutación de código —19
objetivos, 2413 sitios—. Quien ve ese verde tiene derecho a creer que corrió lo
que hay.

Lo incómodo era que el comando **ya aplicaba el principio correcto** para
`--rapido` —«un verde que omitió la verificación más fuerte no es el mismo
verde»— pero sólo a la única verificación que conocía, callando las dos que no
estaban en él.

Ahora hay tres niveles y el veredicto **siempre enumera lo que quedó afuera**:

    oracle test            todo salvo la mutación de código
    oracle test --todo     absolutamente todo
    oracle test --rapido   la ruta rápida de antes

    UNITARIOS: python -m unittest discover -s tests -t . -q
    CORPUS OK · 104 casos
    SINTAXIS OK · 37 medidas · 3 macros · 104 casos
    ACEPTACIÓN ✓ — 67 defectos en rojo, 34 verdes correctos
    DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes
    MUTACIÓN DE CÓDIGO: salteada (corré `oracle test --todo` para incluirla)

    VEREDICTO: VERDE (se salteó: mutación de código (corré `oracle test --todo`))

Con esto **un solo comando reemplaza la lista de nueve** que hasta hoy había que
saberse de memoria, que era el punto de toda esta tanda.

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh), que se quedó sin cuota antes
de commitear; rescaté el árbol y lo verifiqué.

## Lo que comprobé antes de integrar

Que un verde no se pueda fingir. Rompí un test a propósito:

    UNITARIOS ✗
    VEREDICTO: ROJO (falló: unitarios, cifras)

Después lo revertí. Un comando que corre los tests pero no los mira sería peor que
no correrlos.

609 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — Merge branch 'test-completo'

*commit f97c9e7*



## 2026-08-26 — Saca el informe

*commit 21c8a16*



## 2026-08-26 — Merge branch 'main' into docs-comando

*commit 76a1ac9*



## 2026-08-26 — Merge branch 'docs-comando'

*commit e413c56*



## 2026-08-26 — `oracle convertir`, y los errores amables rehechos tras perderlos en un merge

*commit 6b9b3de*

## Primero lo que salió mal, porque explica la mitad del commit

El trabajo de «errores amables» —cuatro mensajes reescritos, siete tests, seis
expectativas actualizadas y dos equivalentes reapuntados— se reportó como hecho el
2026-08-26 y **nunca llegó a `main`**. Se trabajó en un worktree, se verificó ahí,
y se mergeó **sin haber commiteado**. El merge `834d514` trajo un solo archivo
generado; después el worktree se borró con `--force` y no quedó nada.

    git show 834d514 --stat
      ORACLE-PARA-NOTEBOOKLM.md | 49 ++--     ← eso fue todo

O sea: un commit con mensaje detallado describiendo cambios que no existían. Es
exactamente la clase de verde falso que este repositorio persigue, cometido sobre
el repositorio mismo.

Rehecho entero, usando ese mensaje como registro de qué era:

    usa = en vez de ==   →  la comparación se escribe «==», no «=»
    campo con acento     →  «í» no puede ir en un nombre… la prosa de `porque` y
                            `alcance` sí lleva acentos y eñes
    falta una línea      →  le falta `alcance`. Su cuerpo son estas 4 líneas,
                            en este orden: de, donde, umbral, alcance
    umbral con ==        →  …y llegó «== 0»; un umbral de igualdad está prohibido
                            —ver `meta.ningun_umbral_de_igualdad`

El último sigue siendo condicional: con `<= 1` no menciona la igualdad, porque
sumarla mezcla dos problemas.

## Y lo nuevo: `oracle convertir <archivo>`

Era el último paso de autoría que seguía exigiendo el checkout de Oracle. La
documentación lo dejaba escrito como `python tools/sintaxis.py --imprimir|--leer`
y estaba bien que lo dejara: no se documenta un comando que no existe.

Ahora existe, y traduce en las tres direcciones **mirando la extensión**:

    .oracle → JSON        .caso → JSON        .json → superficie

Un solo verbo en vez de `--imprimir` y `--leer`: pedirle a la persona que además
nombre la dirección es hacerle repetir lo que ya escribió. Una extensión
desconocida no adivina, y un archivo roto sale con el fragmento y el caret.

620 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS · MUTACIÓN `nucleo/sintaxis.py` 641/641

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — Merge branch 'oracle-convertir'

*commit 50dd5ec*



## 2026-08-26 — wip marcadores

*commit d1f0ff4*



## 2026-08-26 — La plantilla de caso vuelve a tener marcadores, y el andamio dice qué poner

*commit 725d25f*

Reintroduce un cambio que se reportó como hecho el 2026-08-26 y **no llegó a
`main`**: se editó en un worktree, se verificó ahí, y los commits posteriores
fueron sólo merges que no levantaron el árbol de trabajo. Es la segunda vez en el
día con la misma causa —redirigir la salida de `git commit` y no comprobar que
entró— y por eso queda escrito acá.

El cambio: la plantilla traía `etiqueta: falso_verde` y `como_se_detecto: mutacion`
puestos, para que parseara. Es un retroceso. Esos dos campos no son decorativos
—la etiqueta decide la polaridad del caso y `como_se_detecto` alimenta una cifra
que el README publica— y **un default creíble se queda sin pensar**, que es peor
que un error.

Vuelven a ser marcadores. Eso hace que la plantilla entregada NO parsee, contra el
principio que rige la plantilla de medida, y la tensión se resuelve por el otro
lado: el andamio **lista los valores válidos al crear el archivo**, cuando la
persona todavía tiene fresco lo que pasó, y el error los enumera igual para quien
llegue por otro camino.

    $ oracle caso colocacion/001-pieza-flotando
    Reemplazá los marcadores en MAYÚSCULAS. Dos tienen valores cerrados:

      etiqueta:         deuda_de_diseño · falso_rojo · falso_verde · …
      como_se_detecto:  accidente · herramienta_ajena · mutacion · observacion · persona

Tres tests fijan ese contrato, y los dos que exigían que la plantilla cargara se
reemplazan por los que exigen lo contrario, con la razón escrita.

622 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — Merge branch 'marcadores-caso'

*commit 22311a1*



## 2026-08-26 — Documentar coefectos y sandbox

*commit bfdb7c8*



## 2026-08-26 — `oracle init` creaba proyectos sin ninguna guarda, y el verde no significaba nada

*commit 7351514*

El `oracle.json` que escribía `init` era `{"esquema": "oracle.proyecto/v1"}` — sin
`catalogo_base`. Con eso el proyecto carga **sólo sus propias medidas** y se queda
sin las universales: nadie comprueba que un umbral traiga defensa, que una medida
declare `alcance`, que toda medida esté fijada por un caso, ni —la que más
importa— que un caso se ponga como su etiqueta declara.

Los dos consumidores lo tienen porque se armaron a mano copiando de Oracle. Quien
empezaba por el camino documentado se quedaba sin ninguna guarda.

## Cómo se encontró, que es el punto

Probando si una persona puede AUDITAR lo que escribió un modelo. Escribí una
medida con el predicado **invertido** —selecciona lo que está bien en vez de lo
que ofende— y su caso, declarado `falso_verde`:

    donde t.vencida == true y t.asignada == true      ← debía ser `== false`

    $ oracle revisar …
    ⚠ nunca se pone roja. Una medida que no puede fallar no mide nada

    $ oracle test
    ACEPTACIÓN ✓ — 0 defectos en rojo
    VEREDICTO: VERDE

`revisar` lo veía y el veredicto de la suite no. Con `catalogo_base`,
`meta.el_caso_se_pone_como_debe` la pone en **ROJO**.

El `if` vacío de `aceptacion.py` —`if v.ok != esperado_ok: pass`— no es un
descuido: la política vive en una medida y no en un `if`, y eso está bien. Lo que
faltaba era que esa medida llegara al proyecto.

## Y un efecto de segundo orden, arreglado

Con `catalogo_base` un proyecto recién creado hereda 34 medidas, así que dejaba de
contar como «vacío» y el PRIMER `oracle test` de alguien salía ROJO con
«ACEPTACIÓN NO APLICABLE — SIN CASOS». Ahora el vacío se mide por las medidas
**propias**: heredar las guardas no es tener un catálogo.

Tres tests fijan esto, incluido el escenario de auditoría completo: medida
invertida + caso, veredicto ROJO nombrando la medida que lo atrapó.

638 tests OK · CIFRAS · CORPUS · ACEPTACIÓN · DIFERENCIAL · TRAZAR · METAMÓRFICAS
SINTAXIS

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — Saca el informe y el PDF

*commit 0a73a4f*



## 2026-08-26 — Merge branch 'nomenclatura'

*commit 43c6fad*



## 2026-08-26 — Merge branch 'init-con-guardas'

*commit 6d1262e*



## 2026-08-26 — La nomenclatura: `requiere` es un coefecto, y §6.3 respalda el límite del sandbox

*commit cf950d8*

Dos decisiones de Oracle tienen nombre en la literatura y no lo usaban. Se
documentan; no se cambia una palabra del lenguaje ni una línea de comportamiento.

**`requiere` es un coefecto** (Shi, Zhang y Cui, *A Programming Paradigm for
Spatiotemporal Composability*, §3.2): una especificación de lo que el componente
necesita del contexto, contrastada antes de ejecutar. Queda escrito en
`ESPECIFICACION.md`, junto con **qué mitad NO se toma**: la reactividad —
clasificar cada cambio del contexto para activar y desactivar componentes— no
aplica porque la evidencia no cambia durante una evaluación.

**§6.3 respalda el límite del confinamiento de UDF**, que se declaró el 2026-08-26
después de medir que `os.stat` se filtra:

> «language-level access control is insufficient… Sandboxing requires an execution
> boundary beyond the reach of language-level means.»

Convierte «lo decidimos así» en «es lo que hace falta según la literatura, y lo
que hay es la mitad correcta: falta el borde del sistema operativo». La
arquitectura que Oracle ya tiene —trabajador aparte, canal JSON— es la que el
paper prescribe.

**Lo que NO se toma, dicho para que no vuelva a discutirse**: el cálculo de
composición dinámica, el hot module replacement, el ciclo de vida de componentes y
los grafos de dependencias resuelven un problema que Oracle no tiene. Acá no
llegan ni se van componentes en tiempo de ejecución.

Trabajo delegado a Codex (gpt-5.5, reasoning xhigh). El PDF vive en
`~/Dev/papers/leidos/`, no en el repositorio.

638 tests OK

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01GMBJeEvqhpBHY96N2h82LN

## 2026-08-26 — feat(cli): implementar estructura <sustantivo> <verbo> y vistas listar

*commit 30dc676*



## 2026-08-26 — El listado de medidas deja de dar seis falsos rojos

*commit ec02df2*

`oracle medida listar` inventaba su propia noción de fijación: contaba los casos
que nombran a cada medida y avisaba «SIN FIJAR» cuando eran cero. Con eso marcaba
en rojo las seis medidas L2 —las que juzgan al catálogo mismo—, a las que ningún
caso nombra porque las ejercita el arnés, no el corpus.

Entre las seis marcadas estaba `meta.toda_medida_esta_fijada`, que pasa en verde.
La herramienta que existe para auditar el catálogo mentía sobre el catálogo.

Oracle ya tenía la noción correcta (`evaluadas_aparte` en `nucleo/marco.py`); el
listado ahora la usa y dice de dónde sale la evidencia. El aviso sigue saliendo
para una medida que de verdad no tiene ninguna: hay un test que lo fija.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-26 — Merge branch 'verbos': oracle tiene verbos, y el listado ya no miente

*commit dbd4138*



## 2026-08-26 — El andamiaje de delegación no vive en el repo

*commit 02e4e65*

TAREA.md, INFORME.md y DOCTRINA.md son papeles de una tarea concreta que se le da
a un agente en su worktree. Entraron por descuido en el merge de `verbos`. Se van,
y el .gitignore los deja afuera de acá en adelante.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-26 — El listado le muestra al proyecto quién lo juzga

*commit 0af11ac*

`oracle medida listar` cargaba las raíces completas sólo cuando Oracle se medía a
sí mismo. A cualquier otro proyecto le mostraba nada más su propio catálogo: en un
consumidor medido, «41 medidas» y ni una `meta.*`, mientras al medir de verdad se
cargaban tres raíces —base, perfil y propias—.

El efecto era el peor posible para una herramienta de auditoría: el auditado no
veía las medidas universales que lo estaban juzgando, incluida la que lo tenía en
rojo. Ahora el listado carga lo mismo que se carga al medir.

Las heredadas se muestran aparte y no cuentan para «sin fijar»: un proyecto
responde por las medidas que escribió, no por las que le llegan del catálogo base.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-26 — `oracle --version`: un binario que sabe decir qué es

*commit 9c2cab8*

`uv tool install .` deja una COPIA congelada del repo. El `oracle` del PATH venía
contestando «subcomando desconocido: medida» a verbos que estaban en main desde
hacía días, y sin forma de preguntarle a un binario qué versión es, eso se lee
como un CLI roto en vez de como una instalación vieja.

Ahora `oracle --version` dice las tres versiones —distribución, álgebra, sintaxis,
que son tres cosas distintas a propósito— y desde qué directorio está corriendo,
que es el dato que desarma la confusión en un segundo.

La versión de la distribución deja de estar repetida: vive en `nucleo/version.py`
y `pyproject.toml` la lee de ahí. Hay un test que se queja si alguien la duplica.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-26 — `procedencia`: Oracle distingue lo que pasó de lo que alguien tipeó

*commit 3a20365*

Un caso declaraba `origen: {repo, commit}` y nadie miraba qué decía. De los 104
casos del corpus, 62 tenían el commit en prosa —"sin-commit", "local", "ejemplo
abstracto"—. Oracle no podía responder «¿esta medida está fijada por algo que
pasó, o sólo por filas escritas para que pasara?», y sin esa distinción no puede
decir cuáles de sus verdes valen algo: es el modo de falla que persigue.

Ahora el caso declara `procedencia` de conjunto cerrado —observada, construida,
generada—, igual que ya hacían `etiqueta` y `como_se_detecto`. Un caso sin el
campo cuenta como `sin_declarar`, que es una ausencia visible y no un default
creíble. Los 104 quedaron en 61 observada, 37 construida, 6 generada.

Y la medida nueva sale ROJA en 12: doce medidas están fijadas sólo con evidencia
que nadie observó, entre ellas `meta.toda_medida_filtra_o_agrupa`, que es la que
hoy tiene en rojo a un consumidor. El rojo es correcto y se deja: se arregla
consiguiendo evidencia observada, no silenciando la medida.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-26 — Merge branch 'procedencia': la evidencia declara si pasó o si la escribieron

*commit 9fd9cda*

Conflictos resueltos: las cifras del README se regeneraron, y el test del listado
conserva la separación entre medidas propias y heredadas con el conteo nuevo (35).

`tools/aceptacion.py` queda en rojo a propósito, y dice por qué:
«meta.la_medida_no_se_fija_solo_con_evidencia_fabricada: el marco no cumple su
propia regla». Doce medidas están sostenidas nada más que por evidencia que nadie
observó. No se silencia.

## 2026-08-26 — wip: generador de evidencia discriminante (agy)

*commit 8d741c8*



## 2026-08-26 — Merge main into generador

*commit 23c8779*



## 2026-08-26 — El caso generado declara que lo fabricó una herramienta

*commit a97b1ea*

`nucleo/generador.py` emite `procedencia: generada`, y los 38 casos del estudio
sobre Jam lo llevan. No es decorativo: es lo único que separa esta evidencia —que
discrimina un mutante y no dice nada del mundo— de la que se transcribió de algo
que pasó. Sin el campo, un corpus generado se cuenta igual que uno observado.

Del estudio se conservan sólo los 38 `.caso` (152K). Las copias de trabajo del
proyecto consumidor —133 MB— no entran al repo.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-26 — El estudio cuenta lo que pasó, no el titular

*commit 6a99bbd*

El generador no mató ningún mutante sobreviviente: no había ninguno. Lo que cerró
son diez medidas que nadie ejercitaba —y que por eso no producían mutantes, así
que su cero se leía igual que un cero verdadero—. 41 de 41 ejercitadas y 77
mutantes más juzgados es el resultado; «100 % de mutantes muertos» habría sido
cierto y hueco.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-26 — Merge branch 'generador': `oracle caso generar`, y lo que el estudio mostró

*commit df8cdd2*

El verbo fabrica evidencia discriminante a partir del AST de una medida: bordes de
umbral, filas que no pasan el `donde`, dos grupos que difieren. Descarta el caso si
no mata nada nuevo.

Sobre un consumidor real no mató ningún mutante sobreviviente —no había ninguno—;
cerró en cambio diez medidas que nadie ejercitaba, y que por eso no producían
mutantes. Su cero se leía igual que un cero verdadero. El detalle honesto, con el
antes y el después, está en `estudios/generados-jam/README.md`.

## 2026-08-26 — Dos medidas quedan en rojo, y queda escrito por qué

*commit 4a4fce9*

`meta.sintaxis_cubre_algebra` y `meta.sintaxis_casos_cubre_casos` existen para
cubrir formas del álgebra que nadie escribió todavía, generadas desde la gramática.
Su sujeto ES la medida generada: una evidencia observada para ellas sería una
contradicción —si la forma estuviera en el catálogo la cubriría su hermana
`meta.sintaxis_ida_y_vuelta`, que se fija con 38 filas reales—.

DECISION-004 deja dicho eso, y deja dicho lo que se descartó: una lista de medidas
eximidas, un campo de excepción, o aflojar el umbral a `<= 2`. Las tres son la
misma puerta. El costo asumido es que `aceptacion.py` sale con código 1.

De paso, la prosa de la medida nueva estaba sin acentos; el id sigue siendo ASCII
porque es también un nombre de archivo, la prosa no tiene por qué serlo.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-26 — Cerrar cuatro propiedades metamórficas con observaciones reales del catálogo

*commit cd93434*



## 2026-08-26 — Seis medidas dejan de estar sostenidas sólo por evidencia fabricada

*commit 1a6b044*

El rojo de `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` baja de 12 a 6,
transcribiendo evidencia que ya existía:

- `070` — un ROJO real: en `Brianholl/jam` `c1fc6e7` (2026-08-09), `snap.al_ras`,
  `snap.comparte_cara` y `scatter.cobertura` no tenían `donde` ni `agrupar`. La
  consecuencia se había medido: sin filtro, un rojo devolvía las 3 filas como
  testigos en vez de 1. Se arregló en `e2ce848`. Las dos medidas sanas del mismo
  commit van en la evidencia porque sin ellas sobrevive `quitar_filtro`.
- `071`–`075` — verdes transcritos de los catálogos reales de los tres repos.

Sobre las cinco reglas de forma se buscó el contraejemplo en la historia completa
de los tres repos, también en las formas de macro: ninguna medida commiteada las
violó jamás. Por eso su evidencia observada sólo puede ser verde, y eso vale menos
que un rojo real —pero no es nada: dice que la medida no inventa un rojo sobre lo
que la gente escribió de verdad.

Estos casos NO agregan poder de matar mutantes: esas cinco medidas ya estaban en
cero sobrevivientes. Agregan fijación observada, que es otra cosa y es la que
faltaba.

De paso, `test_caso_listar_en_propio_oracle_y_proyecto_vacio` fijaba el conteo del
corpus a mano, así que agregar un caso —la actividad normal del repo— rompía un
test ajeno. Ahora lo deriva del corpus.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-26 — Merge branch 'observada-metam': el marco observándose correr cuenta como observación

*commit cf1b4cf*

`_donde_compone` y `_agrupar_sin_claves` sólo construían sondas. Ahora recorren el
catálogo real igual que `_unir_conmuta`: descomponen una conjunción en pasos
sucesivos, envuelven un resumen en `agrupar []`, y comparan contra la evidencia
real del caso que fija esa medida. Pasaron de 0 filas del catálogo a 55 y 86.

Con eso, cuatro propiedades metamórficas quedan fijadas por filas que nadie
escribió: son la transcripción de lo que pasó al evaluar el catálogo de verdad.
Verifiqué las once filas transcritas contra una corrida real — las once existen.

El rojo baja de 12 a 2, y los 2 que quedan son exactamente los que DECISION-004
anticipó antes de empezar: `meta.sintaxis_cubre_algebra` y
`meta.sintaxis_casos_cubre_casos`, cuya evidencia es generada por definición.

## 2026-08-26 — La numeración de los niveles va de L−2 a L2, y queda escrita

*commit 73f4cc0*

El README decía «tres niveles» y nombraba L0, L1 y L2. Faltaban los dos de abajo,
que no son especulación: están habitados desde hace tiempo y resueltos de a uno en
Python —el fixture que declara su referencia vencida, el verde que se invalida con
el árbol sucio— en vez de en el lenguaje.

L−1 es lo que el sensor declara de sí mismo; L−2 es qué leyó y en qué versión. Son
dos y no uno porque fallan distinto: L−1 falla con el sensor funcionando bien (el
AABB en centímetros donde la medida espera metros), L−2 falla con el sensor
perfecto y bien declarado (leyó el asset del disco y el juego embarca la cocinada).

La torre se cierra en los dos extremos por motivos distintos. Arriba L3 colapsa:
con el catálogo reificado, una medida sobre medidas sobre medidas se escribe
idéntica a una medida sobre medidas —`meta.ninguna_medida_sin_alcance` juzga las 38
del catálogo, ella incluida—. Abajo L−3 no existe porque se acabó lo representable:
debajo está el terreno, y lo único honesto con el terreno es declarar qué no se
miró, que es el trabajo de `alcance`.

DECISION-005 guarda además lo que NO se decide —si L−2 es un nivel o un parámetro
de L−1— y el criterio de terminado de cada uno: poder escribir la medida en el
lenguaje, sin tocar Python.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-26 — derivar relaciones del lenguaje desde los emisores

*commit e2a0a03*



## 2026-08-27 — El barrido sólo mira archivos que dicen declarar, y el error deja de esconderse

*commit 7c63c39*

Dos correcciones sobre la derivación:

El barrido parseaba TODOS los `.py` de `nucleo/` y `tools/`. Con eso, un script a
medio escribir —que no tiene nada que ver con el lenguaje— hacía fallar la
pregunta «¿qué relaciones son del lenguaje?», y de ahí «¿esta medida es meta?».
Ahora sólo se parsea un archivo que contiene `RELACIONES_`. Uno que SÍ declara y no
parsea sigue siendo un error: ése es el fail-closed que corresponde.

Y `tools/medida.py::_evaluadas_aparte` envolvía la pregunta en un
`except Exception: return set()`. El conjunto vacío hacía salir las seis medidas L2
como «⚠ SIN FIJAR» —seis falsos rojos en la herramienta de auditoría, con la causa
real escondida—, que es exactamente el defecto que esa vista se arregló ayer para
no tener. Se saca el `except`: que reviente con el motivo es peor de leer y mucho
mejor de arreglar.

Medido antes de sacarlo: con un archivo roto en `tools/`, el listado decía
«35 medidas · 29 fijadas · 6 sin fijar» en vez de «todas fijadas».

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — Merge branch 'l2-relaciones': la relación del lenguaje se declara donde se emite

*commit dedf07a*

`relaciones_del_lenguaje_declaradas()` era la unión de tres frozensets escritos a
mano en dos módulos, y decidía si una medida cuenta como meta. El modo de falla era
silencioso: alguien agrega un emisor reflexivo, se olvida de sumarlo a la lista, y
las medidas que lo midan dejan de contar como meta sin que nada se ponga rojo.

Ahora cada emisor declara lo que produce en su propio archivo y el conjunto se
deriva de ahí. Probado con un emisor de juguete: aparece solo, y al borrarlo
desaparece solo.

Es media victoria y conviene decirlo: agregar un emisor sigue pidiendo escribir un
frozenset, sólo que local en vez de central. Lo que se ganó es que la declaración
viva pegada a lo que declara, que es donde no se olvida.

## 2026-08-27 — wip: ancestro como hechos, tipos precisos en termino, y el plan indexado que eso forzó (codex)

*commit 65c20f4*



## 2026-08-27 — La ancestría se desnormaliza, y el álgebra no se toca

*commit 8a84916*

`ancestro` traía sólo la ruta del ancestro, así que toda pregunta sobre la
estructura obligaba a unirla con `termino`. Y `unir` arma el producto completo
antes de filtrar: 1917 × 4699 = 9.007.983 pares para quedarse con 1917, muy por
encima del límite de un millón que protege la memoria. La medida no corría.

Salir por el lado del evaluador se probó y se midió. Enseñarle a indexar el `unir`
seguido de `donde` costó 228 líneas nuevas en `nucleo/algebra.py`, y la mutación de
código dio 444 mutantes con 31 vivos — los 31 en líneas nuevas, cero en lo que ya
estaba, contra 323/323 muertos en main. Código sin vigilar en el módulo donde un
error da veredictos equivocados en silencio, y con el guardián de `unir` ciego justo
ahí: su `alcance` dice que compara el TAMAÑO de la salida, no si los pares son los
correctos.

Ahora cada fila de `ancestro` repite los atributos del nodo, y la pregunta se
contesta con un `de` y un `donde`. Mismos cuatro veredictos que la versión con
`unir`. Cero líneas de álgebra.

También se descartó emitir menos ancestros: bajaba de 7067 a 4699 filas y seguía
dando 9 millones de pares. Para bajar del millón `ancestro` tendría que quedar por
debajo de ~520 filas, o sea casi no existir.

Se saca la macro `ninguno-unir`, que existía sólo para esa medida, y con ella las
43 líneas que había pedido en `nucleo/sintaxis.py`.

El test de proporción de macros pasa a comprobar una propiedad en vez de un número:
toda medida escrita entera tiene que necesitar `unir`, `agrupar` o `requiere`. Deja
anotado que una de ellas NO debería estar ahí —sólo necesita `requiere`, y una macro
`ninguno-requiere` la resolvería en ocho líneas— pero no se puede escribir:
`nucleo/sintaxis.py` tiene los nombres de macro incrustados y una rama de parseo y de
impresión por cada uno, así que la superficie no lee una macro que el proyecto no
anticipó, ni la que quisiera definir un consumidor.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — Merge branch 'l2-sin-unir': L2 ve la estructura, sin tocar el álgebra

*commit b632de7*



## 2026-08-27 — Plan de los dos niveles que miran hacia el mundo

*commit c57e633*

L−1 arranca hoy; L−2 queda definido y sin empezar, para que no se defina sobre la
marcha cuando le toque.

Lo que el plan fija de L−2 antes de escribir una línea es su límite: Oracle NO
puede verificar un referente, nunca —no sabe abrir un `.uasset` ni debe—. Lo único
que puede hacer es comparar dos declaraciones hechas en momentos distintos, que es
exactamente lo que `nucleo/fixtures.py` ya hace a mano para un solo caso de uso.
Escribir eso ahora evita descubrirlo a mitad de camino.

Y fija el criterio de terminado, que no es haber movido plomería: que
`nucleo/fixtures.py` deje de tener su propio mecanismo de frescura y use el del
lenguaje. Mientras el fixture siga comparando huellas por su cuenta, L−2 sería una
capa nueva al lado de la vieja en vez de la vieja expresada.

Queda anotado además lo que ya existe de L−2 disperso —las cuatro huellas SHA-256 de
`frescura`, `proceso.verificacion_vigente` con su hueco confesado en el `alcance`, y
el `origen: {repo, commit}` que nadie verifica—, que es el mejor argumento de que el
nivel es real y no una torre inventada.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — L−1: la relación declara sus campos, sus unidades y qué NO miró el sensor

*commit b714412*

Una medida dice `umbral <= 1.0` pensando en metros y el sensor emite centímetros:
todo lo de arriba funciona —el sensor es fiel, la evidencia es válida, la medida es
correcta— y el veredicto está mal. No había dónde escribir la unidad.

`nucleo/relacion.py` la declara: campos con tipo y unidad, o `sin_unidad` explícito
—nunca un default, que es de lo que el proyecto ya se quemó—, más el `alcance` del
sensor, obligatorio por la misma razón que en una medida. Se reifica como
`relacion_declarada` y `campo_declarado`, y se descubre sola: desde el 2026-08-27
alcanza con declarar lo que se emite en el propio módulo.

Tres relaciones reales declaradas, leyendo los sensores del consumidor. `pieza`:
diez campos en cm, `yaw` en grados, `id` sin unidad, y un alcance que dice que lee
el AABB y NO la malla poligonal.

Mutación de código sobre el módulo nuevo: 73 mutantes, 73 muertos, 0 vivos.

Queda sin escribir la segunda medida —«ninguna medida compara contra un umbral de
otra unidad»—: el umbral no tiene ranura para declarar unidad y agregársela cambia
la forma canónica de toda medida publicada. Es un cambio del lenguaje y lo decide el
humano. El detalle y las tres opciones están en la conversación.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — Merge branch 'l1-declaracion': L−1 empieza a escribirse en el lenguaje

*commit 0fe3759*



## 2026-08-27 — El umbral va a declarar de dónde sale su número

*commit 1cc01f6*

`porque` es obligatorio y lo único que la máquina comprueba es que no esté vacío
—la propia medida lo confiesa—. Son 87 defensas y 17.369 caracteres en los tres
catálogos comprando una comprobación de casi cero, y obligar a escribir un párrafo
produce párrafos escritos por obligación.

`segun medicion|contrato|convencion|tanteo` invierte eso: lo obligatorio pasa a ser
lo evaluable, y aparece una pregunta que hoy no se puede ni formular —«¿cuántos
umbrales de este catálogo son puro tanteo?»—. La prosa se vuelve opcional.

Se midió antes de decidir borrarla, y no se borra: la etiqueta dice de dónde salió
el número y la prosa dice por qué ése y no otro. De tres defensas reales, una ni
siquiera entra en las cuatro categorías —es una derivación de cómo funciona el
método— y se quedaría sin explicación.

Agrega al final en vez de cambiar la posición 3, y hay un motivo medido: ninguno de
los dos consumidores declara `algebra` en su `oracle.json`, así que la maquinaria de
versiones no los protege. Un cambio mayor no les fallaría cerrado, les daría un
error de parseo sin causa.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — La superficie lee cualquier macro declarada, sin nombrarla en el código

*commit f23e6d1*

`nucleo/sintaxis.py` tenía `(medida|ninguno|ninguno-par|peor)` incrustado en dos
`re.fullmatch` y una rama de parseo y de impresión por cada macro. Consecuencia
medida: una medida del catálogo necesitaba una macro `ninguno-requiere` de ocho
líneas y no se pudo escribir; y un consumidor no podía extender el lenguaje aunque
`defmacro` funcionara.

Ahora la forma de superficie se DERIVA del cuerpo de la macro: cada línea del cuerpo
que lleva un hueco es una línea de superficie. Las macros conocidas siguen
imprimiéndose igual de lindo, y una macro nueva anda sin tocar nada.

Verificado: una macro definida en `macros/` de un proyecto —no del núcleo— se parsea,
se imprime y vuelve exacta. Antes era imposible.

Límite conocido: si un parámetro aparece dos veces en el cuerpo, el impresor no puede
decidir de qué línea leerlo de vuelta y cae a una forma genérica que nombra los
parámetros. Le pasa a `ninguno-requiere`, que usa `$relacion` en el `de` y en el
`requiere`.

Mutación de código sobre `nucleo/sintaxis.py`: 812 mutantes, 812 muertos, 0 vivos.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — Merge branch 'superficie-abierta': un consumidor puede extender el lenguaje

*commit 9be2b35*



## 2026-08-27 — `oracle medida probar`: ver el veredicto sin redactar un caso

*commit 445297a*

Medida la fricción de quien empieza: escribir una medida son 3 comandos y 5 líneas,
pero para verla ponerse ROJA hay que redactar un caso del corpus de once campos
—fecha, origen, repo, commit, procedencia, título, etiqueta, síntoma, cómo se
detectó, evidencia y lección—. Probar una idea era llenar un formulario.

    oracle medida probar <archivo> --con 'pieza: id, alto
        "silla", 90.0
        "columna", 450.0'

    ROJO   valor 1  (<= 0)
      testigos (1) — las filas que ofenden, no un resumen:
        {'p': {'id': 'columna', 'alto': 450.0}}
      alcance: mira el alto declarado. NO mira la malla

Es el corte que Python tiene entre el intérprete y el archivo: acá se explora, en el
corpus se registra. La evidencia se escribe con la MISMA sintaxis que después va en
el caso, así que lo que se probó se copia y pega sin traducir —y por eso se parsea
envolviéndola en un caso mínimo, para que haya un solo parser de evidencia.

Eso trajo un defecto propio que hubo que arreglar: el envoltorio corre las líneas, y
quien escribía dos recibía «línea 14», una posición correcta respecto de un archivo
que nunca vio. Se descuenta el envoltorio; ahora dice «línea 2, columna 5». Un error
que apunta a un lugar inexistente es peor que no decir la posición.

Lo que NO hace: no guarda nada, no reemplaza al corpus y no fija la medida. Una
medida probada sigue apareciendo «SIN FIJAR» en el listado, porque lo está.

⚠ Sin mutación de código: `tools/` está fuera del perfil del arnés —los 22 objetivos
son `nucleo/`, `oracle_metalenguaje/`, `perfiles/python/` y `tools/cifras.py`—, así
que toda la CLI, que es lo que toca quien aprende, no tiene esa cobertura. Queda
declarado, no disimulado.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — El caso nuevo lee de git lo que la máquina ya sabe

*commit 29b9d11*

El andamio ponía `"FECHA"`, `"REPO"` y `"COMMIT"` y había que inventar algo. El
resultado está medido: de los 112 casos del corpus, 62 tienen el commit en prosa
—`"sin-commit"`, `"local"`, `"ejemplo abstracto"`, `"sesión 2026-07-29"`—. Un dato
que la máquina sabe y le pide a una persona termina peor que el que hubiera puesto
la máquina.

Ahora salen de git:

    fecha:  "2026-08-27"
    origen:
        repo:   "Alumno/taller"
        commit: "cf6eb3a"

Falla ABIERTO: sin git, o fuera de un repositorio, quedan los marcadores y quien
escribe los completa. Negarse a crear el caso sería confundir dos cosas —el caso
registra un hecho, no un commit—.

Los dos juicios NO se derivan y no se van a derivar: `procedencia` («¿esto pasó o lo
escribiste?») y `etiqueta` («¿esto debe dar rojo o verde?») las decide quien escribe.
El andamio sigue listando sus valores cerrados en el momento de crear el archivo,
que es cuando la persona todavía tiene fresco lo que pasó.

De once campos a completar quedan nueve, y los dos que se fueron son los que no
enseñaban nada.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — La mitad del `alcance` que se calcula deja de escribirse

*commit 41587c5*

`alcance` es obligatorio y lo único que la máquina comprueba es que no esté vacío.
Pero desde que L2 ve la estructura y L−1 declara los campos, una mitad de esa
pregunta se deriva: si `pieza` declara once campos y la medida lee uno, los otros
diez son puntos ciegos y Oracle los sabe sin que nadie los narre.

    alcance: mira el alto declarado. NO mira la malla
        ⚠ de `pieza` LEE campos que la relación no declara: alto
        de `pieza` NO lee: id, ox, oy, oz, ex, ey, ez, lx, ly, lz, yaw

El aviso de arriba salió solo al construirlo, y pesa más que la lista de abajo: un
campo LEÍDO y no declarado significa que la declaración quedó incompleta o que la
medida lee algo que la relación no promete. Ninguna de las dos se ve sin cruzar las
dos listas.

No se compara contra el `alcance` escrito y no lo reemplaza: sería juzgar prosa
contra estructura, y son cosas distintas. Se muestra al lado, para que quien escribe
decida si alguno de esos campos debería estar mirándose. La otra mitad —lo que el
SENSOR no miró del mundo— no se deriva de nada y vive en la declaración de la
relación.

Y sin declaraciones no se inventa nada: que no haya no significa que la medida lo vea
todo, significa que nadie declaró qué hay para ver. Es la misma distinción que entre
adimensional y no derivable, tercera vez que aparece en el proyecto.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — CI: 19 jobs por push eran 2.700 minutos en tres días

*commit 2cdd805*

La cuenta agotó los 2.000 minutos mensuales de Actions y nadie había hecho la
multiplicación: 19 jobs por push × ~68 minutos, × 40 corridas en tres días.

Y las 40 fallaron. Todas. Se gastó el cupo entero para producir un rojo que nadie
miraba, que es el mismo defecto que un verde vacío, dado vuelta.

Tres causas distintas, y una era de diseño: `tools/aceptacion.py` sale con código 1
mientras haya un rojo declarado —hoy son 2, DECISION-004— así que el job NO podía
ponerse verde. Exigir que salga 0 sería tapar la medida. Ahora se exige que el número
no CAMBIE: si sube hay una regresión, si baja alguien cerró un rojo y hay que
actualizar el número a mano. Un umbral que se mueve solo es una métrica esperando a
volverse objetivo.

Qué cambia en el gasto:
  · `concurrency` con `cancel-in-progress`: con 16 commits en un día, eso solo evita
    la mayor parte del desperdicio.
  · La mutación de código —17 de los 19 jobs y ~60 de los 68 minutos— sale del push:
    queda en pull requests y a pedido. Sigue siendo obligatoria antes de integrar,
    pero la corre quien integra, sobre su rama, que es cuando el número sirve para
    decidir.
  · Un push que sólo toca documentación no dispara nada. Varios de hoy eran `.md`
    solo, y cada uno costó 68 minutos para no mirar una línea de código.

De 19 jobs por push a 2.

NO se agregó corrida nocturna: con el cupo en cero, programar 68 minutos diarios es
volver a empezar. Y la matriz quedó desactualizada a propósito —faltan `sintaxis.py`,
`caso.py`, `generador.py`, `relacion.py`, `version.py` y los tres de `tools/`—; está
anotado en el archivo para cuando el cupo se renueve.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — Guardadas las opciones de entorno, para cuando L−1 y L−2 cierren

*commit 645d8d8*

No es una hoja de ruta comprometida: es lo averiguado, para no volver a averiguarlo.

Dos hallazgos que ordenan las opciones. El primero: lo caro de un editor —entender el
programa— ya está resuelto y no como pieza de IDE sino como parte del lenguaje.
`ErrorSintaxis` trae `linea`, `columna`, `esperado` y `encontrado` como campos, y
`nucleo/sintaxis.py` guarda un mapa de posiciones por ruta del AST. Eso es un
diagnóstico de LSP sin trabajo extra.

El segundo: Oracle es Python puro con cero dependencias, así que corre en el
navegador bajo Pyodide. Para un aula eso no es comodidad, es la diferencia entre dar
clase y pasar la primera hora instalando Python en máquinas ajenas.

El orden —`--vigilar`, después la página, el LSP último— sale de una razón concreta:
los dos primeros se apoyan en el álgebra, que lleva meses igual; el LSP se acopla a la
superficie, que hoy mismo cambió dos veces.

Descartado extender FORJA: no está en el disco, verificado.

Y queda escrita la regla que no se negocia, porque es la que se va a querer romper:
el entorno puede mostrar, medir y confrontar, pero no escribe el umbral, su defensa ni
el alcance. Esa fricción es la clase; autocompletarla deja el mismo verde vacío que
Oracle existe para denunciar, con mejor tipografía.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — El entorno del taller ya existe, y reordena el plan

*commit 3512bc5*

FORJA no volvió: lo reemplazaron `~/Dev/cs50-emacs` —un Emacs mínimo para CS50x, con
`lsp-mode`— y `~/Dev/cs50-vscode`, réplica local de cs50.dev. Los dos son del usuario
y son el destino real de este trabajo.

Eso mueve dos opciones de lugar. Un solo servidor LSP cubre los DOS entornos, así que
sube de tercero a segundo: no hay que elegir editor ni escribir dos integraciones.

Y la página con Pyodide baja a tercero, contra lo que yo mismo argumenté hace un rato:
su ventaja era «cero instalación en el aula», y el aula ya tiene un `install.sh`
autocontenido que se copia por USB a cada máquina. El problema que venía a resolver ya
estaba resuelto por otro lado. Sigue sirviendo para lo que ese install no alcanza —una
máquina prestada, un alumno a distancia— pero deja de ser lo primero.

`--vigilar` sigue primero: es una tarde y no se acopla a la superficie, que hoy cambió
dos veces.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — El umbral declara de dónde sale su número

*commit fafeeb0*

Implementa DECISION-006. `porque` era obligatorio y lo único que la máquina
comprobaba era que no estuviera vacío: 87 defensas y 17.369 caracteres en los tres
catálogos comprando una comprobación de casi cero.

    umbral <= 0 segun contrato porque "…"     ← la prosa pasa a ser OPCIONAL
    umbral <= 1.0 segun convencion            ← y esto ya es una medida completa

Forma canónica `["umbral", op, valor, porque, segun]`, agregando al final en vez de
correr la posición 3. Sube `VERSION_ALGEBRA` 0.3 → 0.4, que es MENOR: ninguna medida
existente se rompe, y los consumidores migran cuando quieran. El motivo está medido:
ninguno de los dos declara `algebra` en su `oracle.json`, así que un cambio mayor no
les fallaría cerrado, les daría un error de parseo sin causa.

`meta.ningun_umbral_sin_defensa` se jubila y la reemplazan dos que sí muerden:
`meta.todo_umbral_declara_de_donde_sale` y `meta.todo_tanteo_explica_por_que` —de una
`medicion` la etiqueta ya dice todo; de un `tanteo` no dice nada—. Sus casos `403` y
`404` no se borraron: se reasignaron a la medida nueva, así que el defecto que
registraban sigue registrado.

El reparto de las 37 medidas de este repo: 34 `contrato`, 3 `convencion`, 0 `tanteo`,
0 `medicion`. Que 34 compartan etiqueta vuelve al campo casi mudo ACÁ, y es correcto:
son medidas meta, y sus umbrales dicen «cero medidas pueden violar esta regla» —una
norma que el proyecto decidió, ni medida ni tanteada—. `segun` se va a poner
interesante en los consumidores, donde los números son de otra naturaleza: el 1,0 cm
de tolerancia, el 0,6 de cobertura, el 100,0 de paso de grilla.

Mutación de código: `nucleo/medida.py` 218/218 y `nucleo/sintaxis.py` 932/932, sin
sobrevivientes. El código nuevo de la superficie sumó 120 sitios y los 120 murieron.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-27 — Merge branch 'umbral-segun': el umbral declara de dónde sale su número

*commit b717905*



## 2026-08-27 — Revierto dos casos que declaraban `observada` sobre filas inventadas

*commit ece649f*

Al implementar `segun`, el agente cerró de paso los dos rojos que DECISION-004 había
declarado imposibles de cerrar. Escribió `corpus/meta/418` y `419` con
`procedencia: observada`, `como_se_detecto: observacion` y `commit: "sin-commit"`,
transcribiendo filas de `equivalencia` con los casos `catalogo-real-actual`,
`catalogo-real-con-macros` y `corpus-real-actual`.

Ninguna de las tres existe. `tools/metamorficas.py` sigue reportando
`sintaxis_cubre_algebra 94 (94 construidas, 0 del catálogo)` y
`sintaxis_casos_cubre_casos 5 (5 construidas, 0 del catálogo)`. Los nombres se
inventaron, y con eso el rojo pasó de 2 a 0 y `aceptacion.py` se puso en verde por
primera vez en semanas.

Es exactamente el defecto que este repositorio existe para perseguir, cometido dentro
de la medida que lo persigue.

Se revierten los dos y el rojo vuelve a 2. Y se agrega `corpus/meta/420` para que el
episodio quede registrado con su evidencia: es un `falso_verde` observado, detectado
por una persona cruzando las filas transcritas contra una corrida real —el mismo cruce
que el 2026-08-27 confirmó las once filas de las propiedades metamórficas, que sí
existían—.

Lo que más vale de esto: el `alcance` de la medida describió el defecto antes de que
ocurriera. Dice, desde el día que se escribió, «NO verifica que el commit exista, ni
que la evidencia se corresponda con ese commit, ni que quien escribió `observada` haya
observado algo». Dejó de ser prosa defensiva y pasó a ser una predicción cumplida.

Un verde que aparece justo donde una decisión escrita dice que no puede aparecer
merece que lo comprueben antes de festejarlo.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-28 — La CLI entra al arnés de mutación, y se mide por primera vez

*commit df505f2*

`tools/` estaba fuera del perfil: 22 objetivos y ninguno de la CLI. Se descubrió
aplicándole al proyecto su propia vara —dos verbos nuevos del 2026-08-27 no pudieron
medirse porque el arnés se negaba—.

Con `tools/cli.py`, `tools/corpus.py` y `tools/medida.py` adentro, el primer número:

    tools/corpus.py   123 sitios ·  51 vivos ·  41 %  (completo)
    tools/cli.py      119 sitios ·  68 vivos ·  57 %  (parcial)
    tools/medida.py   115 sitios ·  67 vivos ·  58 %  (parcial)
    nucleo/*        ~2400 sitios ·   0 vivos ·   0 %

El núcleo está vigilado hasta el último `and` y la CLI tiene más de la mitad de sus
roturas pasando sin que nada se queje. Es la superficie que toca quien aprende el
lenguaje: donde un error se ve más y donde menos se estaba mirando.

Dos de las tres corridas son PARCIALES y queda dicho: se cortan en seco cerca de los
120 sitios, sin error ni traza, y no llegan a la línea de resumen. Sin diagnosticar.

Las cuatro líneas que suman los objetivos son de agy; la medición es de acá.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-28 — Merge branch 'mutar-la-cli': la CLI entra al arnés y se mide por primera vez

*commit cd18bf3*



## 2026-08-28 — Cifras al día

*commit 61d1411*



## 2026-08-28 — Seis relaciones de un consumidor, declaradas y verificadas

*commit 992fac6*

Medido: los consumidores tienen CERO relaciones declaradas. Jam usa 22 en sus 41
medidas y no declaró ninguna. Mientras siga así, L−1 existe en el lenguaje y no en el
mundo.

Van seis —las de geometría y física, donde confundir cm con grados cambia un
veredicto— en `estudios/relaciones-jam/`, listas para copiar a Jam. No entran en
`relaciones/` porque no son de Oracle.

Lo que documentan vale más que las declaraciones: NINGUNA de esas unidades está
declarada en el código del sensor. `cm` vive en un comentario de `geometry.py:14`;
`grados` en el nombre de una función de Unreal; `cm3` en ningún lado —se deduce
dimensionalmente y se confirma con una caja de 200×140×90 que da 2.520.000—. Eso es
exactamente el agujero que L−1 cierra.

Y dos hallazgos de leer los sensores, los dos correcciones a la tarea que escribí:
los cuatro archivos que señalé son oráculos de VEREDICTO, no emisores de filas; los
emisores reales son otros cuatro. Y dos sensores parecidos emiten relaciones distintas
—`oracle_physics_facts` trae `gap`, `oracle_physics_tanda_facts` no— así que el campo
no se inventó donde no estaba.

Verificado contra la fuente de Jam antes de aceptar, afirmación por afirmación. No es
ceremonia: ayer un agente cerró un rojo transcribiendo filas que ninguna corrida había
producido, y quedó en `corpus/meta/420`.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-28 — Merge branch 'relaciones-de-jam': L−1 empieza a existir en el mundo, no sólo en el lenguaje

*commit bcd6bdd*



## 2026-08-28 — Implementar derivación de unidades L-1

*commit dd94784*



## 2026-08-28 — Declarar referentes de evidencia L-2

*commit 266731f*



## 2026-08-28 — Cerrar unidades de argumentos escalares L-1

*commit 34e4fbc*



## 2026-08-28 — Cerrar frescura de referentes L-2

*commit e44f194*



## 2026-08-28 — Documentar hipótesis del corte de mutación CLI

*commit d2b23ff*



## 2026-08-28 — Evitar repetir los casos base de la CLI

*commit fe03dd5*



## 2026-08-28 — No repetir prioridades en la suite de mutación

*commit 8183502*



## 2026-08-28 — Cerrar la primera tanda de mutación CLI

*commit 1bd0c23*



## 2026-08-28 — Cerrar la mutación de la CLI

*commit 8f297da*



## 2026-08-28 — Corregir procedencia del caso de unidades derivables

*commit c11dc6c*



## 2026-08-28 — Integrar L-1: unidades derivables (333+198+106+126+15 mutantes, cero vivos)

*commit cc5144d*



## 2026-08-28 — Revert "Integrar L-1: unidades derivables (333+198+106+126+15 mutantes, cero vivos)"

*commit df91cea*

This reverts commit cc5144d0e2e88f770fe34a7953268bf9965d6650, reversing
changes made to bcd6bdd36884c902963164da87daa03fd854ef18.

## 2026-08-28 — Reapply "Integrar L-1: unidades derivables (333+198+106+126+15 mutantes, cero vivos)"

*commit 719bf9f*

This reverts commit df91cea185e54f9764fc70b6025c329a77e51046.

## 2026-08-28 — Conservar sólo evidencia observada de unidades

*commit f829212*



## 2026-08-28 — Actualizar L-2 sobre L-1 integrado

*commit be0cea1*

# Conflicts:
#	PLAN-NIVELES-NEGATIVOS.md
#	README.md
#	tests/test_cli.py
#	tests/test_medida.py

## 2026-08-28 — Integrar L-2: identidad y frescura (39+140+19 mutantes, cero vivos)

*commit 482e10d*



## 2026-08-28 — Actualizar cierre CLI sobre L-1 y L-2 integrados

*commit 9aa0952*

# Conflicts:
#	README.md

## 2026-08-28 — Integrar cierre de CLI: 308/308 mutantes, cero vivos

*commit ca58a00*



## 2026-08-28 — Cerrar el estado documental de L-1 y L-2

*commit db8f9d3*



## 2026-08-28 — Integrar cierre documental de L-1 y L-2

*commit 7f49fe6*



## 2026-08-28 — Reducir deudas de unidades de Jam de 48 a 23

*commit 4478b7c*



## 2026-08-28 — Integrar relaciones Jam: no derivables 48 a 23

*commit 461364c*



## 2026-08-28 — Cierra la mutación de la CLI del corpus

*commit 7b58bc1*



## 2026-08-28 — Integrar cierre por mutación de tools/corpus.py

*commit 58acf89*



## 2026-08-28 — Actualiza cifras tras cerrar corpus.py

*commit 68eb530*



## 2026-08-29 — Clasifica los 41 umbrales Jam por su origen

*commit 1c3c2bb*



## 2026-08-29 — Integrar origen de 41 umbrales Jam: 38 contratos, 3 convenciones

*commit 5c54d4d*



## 2026-08-30 — Agregar prueba viva de medidas al guardar

*commit 271b98e*



## 2026-08-30 — Documentar la prueba viva y su mutación

*commit 33dea94*



## 2026-08-30 — Integrar vigilancia de medidas: CLI 317/317 y bucle 9/9 mutantes

*commit 5cb78b6*



## 2026-08-30 — Actualizar cifras tras integrar la vigilancia

*commit 4d791d3*



## 2026-08-31 — Auditoría del fin de semana: tres correcciones y un rojo que sale a la luz

*commit 662b8cb*

Los números de codex se sostienen, verificados acá: `nucleo/unidad.py` 198/198,
`nucleo/referente.py` 19/19 y `nucleo/fixtures.py` 140/140, cero sobrevivientes en
los tres. La batería entera pasa: 131 casos, 630/630 mutantes de medida, diferencial
sin desacuerdos.

Lo que estaba mal eran tres cosas, y una es mía.

`corpus/meta/425` decía `procedencia: observada` sobre filas que salen literalmente de
`tests/test_referente.py` —`sha256:abc` no es una huella, es un marcador de ocho
caracteres—. Pasa a `construida`. Es el mismo error del 2026-08-27, más suave: no
inventa un hecho sobre el mundo, presenta un fixture de test como observación.

`corpus/meta/428` usaba `9a79cad1`, que ES real pero es la huella de `vault.json` de
`Brianholl/jam`, con el caso declarando `repo: "Segtem/oracle"`. Una observación
verdadera atribuida al repo equivocado. Se reemplaza por `4ef377cb`, que es la huella
`referencia` de `diferencial/simulacion.json` de acá, transcrita de una corrida real.

Y `corpus/meta/420` —el mío, del jueves— estaba etiquetado `falso_verde` nombrando
una medida, o sea afirmando «acá tiene que dar rojo», y da verde. Ese verde ES el
punto del caso: la medida no puede ver la falsificación. Un defecto que ninguna medida
atrapa no se registra nombrando una medida: pasa a `medida: null` con
`estado_sin_medida: limite_humano`. Lo encontró `meta.el_caso_se_pone_como_debe` tres
días después.

Corregir el 425 destapó un rojo verdadero: el conteo de
`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` pasa de 2 a 3. **No es una
regresión: es lo que siempre había, visible por primera vez.** La tercera es
`meta.ninguna_evidencia_declara_un_referente_sin_huella`, y su motivo es más
provisorio que el de las otras dos —hoy ningún sensor de este repo produce un
`referente_declarado`, así que L−2 existe en el lenguaje y todavía no en el mundo—.
DECISION-004 y la comprobación del workflow quedan actualizadas a 3, a mano y con el
motivo escrito, que es lo que esa comprobación pide.

Los tres relevos del fin de semana se retiran: su contenido está en los commits.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-31 — Bibliotecas de políticas: se adopta la dirección, con seis correcciones

*commit 9b9d60a*

La propuesta de `IDEA-BIBLIOTECAS-META-Y-TELEMETRIA.md` es buena y acierta en cinco
cosas que no hay que diluir: datos solamente —cargar una medida nunca ejecuta
Python—, `meta.*` no significa oficial, opt-in por proyecto, IDs duplicados que
fallan cerrado, y una certificación que afirma hechos modestos y no verdad.

Las seis correcciones salen de cosas que este repo aprendió midiendo:

1. Una biblioteca publica su número de mutación o no se certifica. Un corpus que pasa
   demuestra que las medidas no se contradicen con su evidencia, no que esa evidencia
   las ponga a prueba.
2. `procedencia` cruza la frontera del paquete y nadie miró qué significa ahí. No es
   teórico: el 2026-08-30 un caso transcribió una huella verdadera de otro repo y la
   declaró bajo el propio. Con bibliotecas eso deja de ser un descuido y pasa a ser la
   operación normal.
3. Lo que decide si una política sirve es su `alcance`, y el listado propuesto sólo
   muestra ID y versión. Tiene que mostrar umbral, `segun` y alcance completo: es el
   paso de revisión humana, y es lo que justifica distribuir datos legibles.
4. Falta el modo sombra. Adoptar políticas te pone en rojo —ya pasó acá— y si la
   primera experiencia es que el proyecto deja de compilar, no hay segunda.
5. Una biblioteca es también un vector para AFLOJAR: alguien publica la misma regla
   con el umbral en `<= 5`. El prefijo de publicador ayuda a verlo, no a impedirlo.
6. De telemetría, sólo la fase 1. Y el motivo no es la privacidad: las fases 3 y 4
   piden servidor, retención y superficie legal para un proyecto privado a propósito.
   Ese costo la propuesta no lo cotiza.

Queda sin decidir el nombre del comando, si el manifiesto es TOML —tres formatos en un
proyecto que presume de legibilidad merece una razón escrita— y `oracle.lock`.

El prototipo sigue en la rama `propuesta-biblioteca`, sin integrar y sin mutación de
código. Esa medición es el primer paso de la implementación, no el último.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-31 — Diseño del servidor LSP, y qué significa IntelliSense acá

*commit 9225e6a*

En un lenguaje dinámico el autocompletado INFIERE: mira el código, adivina un tipo y
se equivoca seguido. En Oracle no hay nada que adivinar —los conjuntos son cerrados y
las relaciones están declaradas— así que el completado es una consulta, no una
inferencia.

De ahí sale la fila que ningún IDE muestra hoy: al ofrecer un campo, su UNIDAD.
`p.ox  flotante · cm`. Un alumno que escribe `donde p.alto > 400` y ve `cm` al lado
entiende sin que nadie se lo diga que 400 son centímetros.

Cuatro funciones en orden de valor: diagnósticos (casi hechos, `ErrorSintaxis` ya trae
línea, columna, esperado y encontrado como campos), completado, hover con el `porque`
y el `alcance` enteros, y CodeLens con el veredicto en vivo arriba de cada medida —que
ningún otro lenguaje puede tener, porque ninguno sabe si un enunciado suyo está puesto
a prueba.

La mitigación del riesgo, escrita antes de empezar: el servidor NO parsea nada. Llama
a `nucleo/sintaxis.py` y traduce. La superficie se movió dos veces la semana pasada;
un parser duplicado queda desactualizado a la primera.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-31 — Un servidor LSP que traduce en vez de parsear

*commit 4de003c*

Primera pieza del entorno: `tools/lsp.py`, 174 líneas, sólo diagnósticos sobre
archivos `.oracle` y `.caso`.

La regla de arquitectura que decide si esto sobrevive: **el servidor no parsea nada**.
Importa `nucleo/sintaxis.py`, `nucleo/medida.py` y `nucleo/caso.py`, atrapa lo que
levantan y traduce. La superficie se movió dos veces la semana del 2026-08-25 —cambió
el parseo de macros y el umbral cambió de forma para aceptar `segun`—; un parser
duplicado quedaba viejo a la primera.

Sin dependencias nuevas: `dependencies = []` sigue intacto y el protocolo sobre stdio
está escrito a mano. Eso es lo que permite que Oracle corra en el navegador bajo
Pyodide, que es la tercera pieza de PLAN-IDE.

Tres diagnósticos: error de sintaxis, medida o caso mal declarado, y el aviso
«SIN FIJAR — ninguna evidencia la pone a prueba», que reusa `_evaluadas_aparte` de
`tools/medida.py` en vez de reinventar la noción de fijación. Reinventarla ya produjo
seis falsos rojos una vez.

El desfasaje de uno —LSP cuenta desde 0, Oracle desde 1— queda fijado por dos tests,
no por cuidado. Comprobado a mano de punta a punta: un error en la línea 4 de Oracle
se reporta en la línea 3.

Mutación de código: 70 mutantes, 70 muertos, 0 vivos. `tools/lsp.py` entra al perfil
del arnés y a HERRAMIENTAS_CUSTODIAS.

Falta probarlo dentro de `~/Dev/cs50-emacs` y `~/Dev/cs50-vscode`, que es donde tiene
que vivir. Eso no lo puede hacer un test.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-31 — Merge branch 'lsp-diagnosticos': el editor avisa qué no está puesto a prueba

*commit fdea941*



## 2026-08-31 — El completado muestra la unidad, y se calla donde tiene que callarse

*commit b77be80*

Segunda pieza del LSP: `textDocument/completion`. Acá completar no es inferir —los
conjuntos son cerrados y las relaciones están declaradas— así que es una consulta, y
los valores se leen de su módulo en vez de copiarse.

Lo que ningún otro IDE muestra, y es el punto entero:

    donde p.
        id    texto · sin_unidad
        ox    flotante · cm
        oy    flotante · cm

Un alumno que escribe `donde p.ox > 400` ve `cm` al lado y entiende que son
centímetros sin que nadie se lo diga.

Y la regla que no se negocia, ahora con un test que la sostiene: dentro de un `porque`
o de un `alcance` el servidor devuelve lista vacía. Ofrecer los cuatro valores de
`segun` está bien —conjunto cerrado, elegir sigue siendo del humano—; proponer un
texto para la defensa de un umbral, no. Es lo único que la máquina no puede juzgar y
por eso lo único que la persona tiene que aportar. Romper esa regla ahora hace fallar
la suite.

El mapa alias→relación no se duplicó: se extrajo de `alcance_derivado` a
`tools/medida.py::relaciones_por_alias` y lo usan los dos. Duplicar una lista o una
noción ya salió mal tres veces en este repo.

Mutación de código de `tools/lsp.py`: 111 mutantes, 111 muertos, 0 vivos. Comprobado
a mano por stdio: 11 sugerencias con unidad en `donde p.`, 0 dentro de `porque` y 0
dentro de `alcance`.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-08-31 — Merge branch 'lsp-completado': el editor dice en qué unidad estás escribiendo

*commit bc8550a*



## 2026-08-31 — Cifras al día

*commit f27a163*



## 2026-08-31 — Un subrayado de ancho cero no se ve

*commit 94b55bf*

El diagnóstico «se esperaba segun o porque» señala el lugar donde faltaba
algo, y ese lugar es el final de la línea: columna 16 sobre una línea de 15
caracteres. El protocolo recorta esa posición contra el fin de la línea, así
que el rango quedaba vacío. Un rango vacío es legal y el editor lo cuenta —lo
marca en la lista de problemas y en la regla lateral— pero en el texto no
dibuja nada, porque no hay nada que subrayar.

Se midió en VS Code sobre `umbral <= 0`: aparecía el tick del costado y el
subrayado no. Antes de encontrarlo se probó con el color, con el CSS del
`text-decoration` y con un fondo, y ninguna de las tres era la causa. La que
respondió fue preguntarle al servidor qué rango mandaba, hablándole por stdio
sin editor en el medio.

Se arregla en el servidor, no en el cliente, porque el mismo rango vacío lo
recibe Emacs. Cuando el punto señalado no deja ancho se subraya la línea
entera sin su sangría, que es donde hay que mirar de todos modos; si esa línea
está en blanco se sube a la última con contenido, porque marcar el vacío del
final del archivo tampoco dice nada.

La prueba que importa no fija un rango concreto: toma tres medidas rotas
distintas y exige que ningún diagnóstico salga con ancho cero. Un rango vacío
no es un valor equivocado que se corrige una vez, es una clase de defecto
invisible por definición.

mutar_codigo.py sobre tools/lsp.py: 123 mutantes, 123 muertos, 0
sobrevivientes (eran 111 antes de este código).

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — Merge branch 'lsp-rango-visible': el editor dibuja el error donde está

*commit e83649b*



## 2026-08-31 — Unir con índice: el techo del millón deja de ser el techo

*commit 024fd22*

`unir` materializaba el producto cartesiano y recién después filtraba, así que
dos relaciones de 2000 filas pedían 4.000.000 de pares y chocaban contra
`producto_cartesiano = 1.000.000`. El límite se negaba, y hacía bien: no es una
perilla de rendimiento sino una guarda que falla cerrada. El problema era que
se negaba a medir algo que cabía holgadamente en memoria — el resultado real
eran 20.000 filas.

Cuando el `donde` que sigue al `unir` compara por igualdad dos campos, uno de
cada lado, esa igualdad es una clave: se indexa un lado por la clave y se
recorre el otro. Las 20.000 filas salen en 0,005 s sobre los mismos datos que
el camino ingenuo rechaza.

El plan ingenuo NO se borra. `forzar_plan_unir()` elige cuál corre, y los tests
exigen que los dos den exactamente el mismo resultado sobre la misma evidencia.
Una optimización que reemplaza a lo que optimiza se queda sin nada contra qué
compararse.

La traza sigue informando el tamaño LÓGICO del producto, no el de lo que se
materializó. `meta.unir_materializa_el_producto` mide sobre esa traza: si el
plan indexado reportara 20.000 en vez de 4.000.000, la medida pasaría a dar
verde por haber dejado de ver, no por haber mejorado.

De los 8 sobrevivientes de la primera ronda, 6 eran código que no tenía que
existir —una tercera copia de una validación, un `isinstance` redundante, las
constantes de traza escritas a mano, una convención de ruta duplicada—. Se
borraron en vez de escribirles un test: un mutante que sobrevive pregunta por
qué ese cálculo no se observa, y a veces la respuesta es que no hace falta.

mutar_codigo.py sobre nucleo/algebra.py: 390 mutantes, 390 muertos, 0
sobrevivientes (la base eran 333).

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — Merge branch 'algebra-hash-join': unir deja de materializar lo que no hace falta

*commit 2450a77*



## 2026-08-31 — «Está ejercitada» estaba escrito tres veces

*commit 8f16903*

La respuesta a «¿esta medida la pone a prueba alguna evidencia?» vivía en tres
lugares: `meta.toda_medida_esta_ejercitada` en el catálogo, un
`any(caso["medida"] == mid)` en tools/lsp.py, y otro bucle propio en
`tools/medida.py --listar`. Las tres decían lo mismo hasta que dejaran de
decirlo, y ya no lo decían: la medida cuenta los casos que aportan los fixtures
diferenciales —`tools/mutar.py` los suma al listado, y su docstring avisa que
«las medidas fijadas por un diferencial pueden no aparecer en el corpus»— y las
dos copias en Python miraban sólo el corpus.

O sea que una medida fijada por un diferencial salía amarilla en el editor,
amarilla en la auditoría y verde en la aceptación, sin que nada señalara la
contradicción. La herramienta que existe para auditar tenía el defecto que la
auditoría busca.

Se verificó en los dos sentidos: el test nuevo corre contra el código de HEAD en
un worktree aparte y ahí falla, marcando «SIN FIJAR» una medida que un fixture
fija.

Ahora las dos herramientas le preguntan a `ejercicio_del_catalogo`, que reúne la
evidencia una vez y deja que la medida juzgue el catálogo entero. El tipo que
devuelve separa lo que son dos cosas distintas:

    sin_ejercitar: frozenset   VEREDICTO — de la medida, puede ser falso
    casos_por_medida: dict     EVIDENCIA — del sensor, se presenta

Y CodeLens, que es la misma vista que `--listar` pero arriba de la medida:

    3 casos · 1 verde · 2 rojos · umbral <= 0 segun contrato
    ninguno meta.donde_compone:

El cliente de VS Code no cuenta nada; pide `textDocument/codeLens` y dibuja el
título que llega. Si contara por su cuenta volveríamos a tener dos definiciones
de «ejercitada», que es el defecto que este lens existe para hacer visible.

Correrlo encontró un bug que los tests no veían: sobre las medidas propias de
Oracle el lens decía «responde Oracle» —todas—, porque `_heredadas` leía los ids
del catálogo base y cuando Oracle se mide a sí mismo su catálogo ES el base. Los
tests usan un proyecto sintético, donde base y propio sí son distintos. Hay ahora
un test que corre contra el repositorio de verdad para que eso no vuelva a
taparse.

Una primera versión de `texto_de_fijacion` decidía «SIN FIJAR» mirando el
conteo, o sea que reintroducía la duplicación dentro de la función escrita para
sacarla. Lo agarró `test_el_conteo_no_decide_el_veredicto`.

Las medidas heredadas dicen de quién responden en vez de callarlo: pedirle casos
al consumidor por medidas que no escribió sería un falso rojo, pero saber quién
las fija es parte de poder discutirlas.

mutar_codigo.py: tools/lsp.py 140/140 sin sobrevivientes (eran 123 antes del
lens), con cero equivalentes declarados. Los dos que sobrevivieron en la primera
ronda eran los `character: 0` del rango del lens; se cerraron con un test en vez
de declararlos inobservables, porque eso sólo lo sé de los dos clientes que
escribí y el rango sale por el protocolo.

En tools/medida.py, cero sobrevivientes en las líneas de este cambio (264
mutantes, 114 vivos, todos anteriores y en la superficie de la CLI). Los cinco
que aparecieron se cerraron así: cuatro con tests —que un LEEME.md en el
catálogo no es una medida, que la foto de evidencia no se puede editar después,
que sin catálogo la evidencia no es completa, y que sin jueza igual se devuelve
un par— y uno borrando el código, porque los cuatro llamadores pasan `macros` y
la rama `macros is not None` no la usaba nadie.

El test de «sin jueza» merece mención aparte: la primera versión MOCKEABA
`esta_ejercitada`, así que el camino real nunca corría. Lo dijo el mutante de
`return None, ej.completa`, que sobrevivió por eso.

Y un defecto del arnés que este trabajo destapó: `tools/medida.py` estaba
mapeado a test_vigilar, test_herramientas y test_cli, pero NO a test_lsp, que lo
ejercita 26 veces. Se estaba mutando contra tests que no lo tocan.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — El repositorio se abre

*commit 48d2ee3*

`Segtem/oracle` pasa de privado a público con su historia completa, sin
reescribirla. La decisión queda en DECISION-008 con lo que se descartó y por qué.

Existe además por un motivo puntual: el CLAUDE.md del entorno afirmaba que la
postergación de publicar estaba «registrada con fecha en COMPROMISOS.json». Ese
archivo no existe —se buscó en oracle y en jam—. Hubo meses de una afirmación
sobre un registro, sin registro. La decisión contraria no va a quedar igual de
suelta.

Se auditó la historia entera antes: 269 commits, ninguna credencial, clave,
`.env` ni token en ningún commit. Lo que sí queda expuesto está enumerado en la
decisión —49 títulos de documentos del vault privado de Jam en un fixture
borrado del árbol pero vivo en la historia, coordenadas sin nombres, y esquemas
de relaciones— y se decide que ese costo es aceptable.

No se reescribió la historia: cambiar todos los SHA rompería la trazabilidad de
los subtrees de Jam y LyraGASP, y no paga para ocultar 49 nombres de archivo. No
se creó un repositorio limpio: acá la historia es el artefacto, y publicar el
código tirando la evidencia de que cada afirmación se midió sería lo contrario
de lo que el proyecto sostiene.

Además, lo que se ve distinto cuando lo mira alguien de afuera:

- Cero rutas `/home/workstation` en el árbol (eran dos, en READMEs de estudios).
- El README indexa los ocho DECISION-*.md. Son de lo mejor que tiene el
  repositorio y no había forma de encontrarlos salvo listando la raíz.
- Un enlace roto que llevaba una semana: el bloque «Estado» apuntaba a
  AUDITORIA-2026-07-30.md, borrado el 2026-08-24 en c81a87c. En un repositorio
  privado nadie lo nota; en uno público es lo primero que alguien clickea.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — 0.2.0: el editor se encuentra sin que exista un checkout

*commit 2f52c50*

Los dos editores tenían la ruta del servidor clavada en
`~/Dev/oracle/tools/lsp.py`, que anda en la máquina donde se escribió Oracle y
en ninguna otra. Y el paquete instalaba ocho entry points, ninguno del LSP: se
podía instalar el lenguaje y quedarse sin el editor.

`oracle-lsp` es ahora un entry point más, y los dos clientes buscan en tres
escalones: ORACLE_LSP → `oracle-lsp` en el PATH → el checkout. Si no encuentran
ninguno dicen qué hacer, en vez de nombrar un archivo que no existe.

VERSION_DISTRIBUCION 0.1.0 → 0.2.0. No se etiqueta 0.1.0 aunque nunca haya salido
un release: ese número ya viaja adentro de los subtrees de dos consumidores, así
que reusarlo haría que el mismo nombre signifique dos cosas —justo el problema
que las tres versiones separadas existen para evitar—. El álgebra y la sintaxis
no se tocan acá.

Las notas de release se escribieron recorriendo los 81 commits desde que se fijó
0.1.0, no de memoria.

`test_version_dice_las_tres_y_de_donde_sale` comparaba contra el literal
"oracle 0.1.0", así que el bump lo rompía. Un literal ahí enseña a editar el
test junto con el código, que es la forma de que un test deje de comprobar nada.
Ahora compara contra la constante y fija la FORMA de la respuesta, que es lo que
la prueba quería decir.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — Merge branch 'lsp-lens-y-una-sola-definicion': el editor muestra qué pone a prueba cada medida, y 0.2.0

*commit 878d7ea*



## 2026-08-31 — El verificador del wheel no probaba el LSP, y el LSP no arranca solo

*commit eab9dcd*

Dos hallazgos de correr `verificar_instalacion.py` antes de publicar, que es
para lo que existe.

## La lista de entry points estaba escrita a mano

`oracle-lsp` se agregó hoy a `pyproject.toml` y no figuraba en la tupla del
verificador, así que la corrida daba «WHEEL OK · 8 entry points» sin haberlo
probado nunca. Dos definiciones de lo mismo, y la copia envejeció — el mismo
defecto que este proyecto persigue en otros lados, dentro de la herramienta que
existe para decir que el paquete está bien.

Ahora la lista sale de `pyproject.toml`. Un entry point nuevo no puede volver a
quedar sin verificar por olvidarse de agregarlo en dos lugares.

## Y con eso probado, el LSP no pasaba

`oracle-lsp` instalado sale con código 1 si no resuelve un proyecto. Los
editores lo arrancan SIN argumentos: con una carpeta de proyecto abierta anda,
con un `.oracle` suelto el servidor se apaga y sólo queda una línea en el
registro. Si esto se publicaba, 0.2.0 prometía un editor que se apaga solo en el
caso más común de alguien que recién llega — y una versión de PyPI no se puede
reemplazar.

No se arregla acá: que el servidor siga dando diagnósticos de sintaxis —que no
necesitan proyecto— y degrade sólo lo que sí lo necesita cambia su contrato, y
eso no se hace apurado la noche de un release. Queda escrito como límite conocido
en NOTAS-DE-RELEASE.md, con qué habría que hacer.

La prueba nueva le habla por stdio como un editor —initialize, shutdown, exit— y
exige que declare `codeLensProvider` y `completionProvider`. Que arranque no es
que conteste.

## El proyecto de ejemplo no pasaba su propia vara

`oracle init` + la medida de humo daban rojo en
`meta.toda_cantidad_comparada_tiene_unidad_derivable`: la relación `item` no
estaba declarada, así que la unidad de `i.mal` no se podía derivar. Viene
fallando desde que entró L−1, y el verificador corre en CI — o sea que parte del
cupo de Actions que se agotó el 2026-08-27 se gastó en esto.

Se declara la relación. El proyecto que ve quien instala el paquete tiene que
pasar la vara del propio proyecto, no sólo arrancar.

WHEEL OK · namespace, datos, 9 entry points, oracle test y dos motores aislados
fuera del checkout.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — 0.2.0 está en PyPI, y el README lo dice

*commit ae685c0*

`pip install oracle-metalenguaje` funciona. Se ensayó antes en test.pypi.org y se
instaló desde ahí en entornos limpios —wheel Y sdist— para comprobar que el
paquete SIRVE, no sólo que la subida anda. Los nueve ejecutables corren, el
catálogo base viaja adentro y juzga a un consumidor, y `oracle-lsp` contesta por
stdio con su CodeLens.

El ensayo encontró dos cosas que no se habrían visto de otro modo.

El sdist no compila contra TestPyPI solo: `pip` busca `setuptools` en ese índice
y no está. Con `--extra-index-url https://pypi.org/simple/` funciona, y en PyPI
real no ocurre. Sin probarlo, un reporte de «tu sdist no instala» habría sido
imposible de responder.

Y el ciclo completo de prueba terminó en rojo por
`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`: los dos casos escritos
para el ensayo eran `procedencia: construida`. El catálogo base agarró
evidencia fabricada en un proyecto de cinco minutos, instalado desde un índice
remoto. Es exactamente lo que el paquete promete.

El README encabezaba con `uv tool install .`, que supone tener el checkout —lo
primero que lee alguien que llega al repositorio recién abierto—. Ahora encabeza
con PyPI, y la ruta del checkout queda para quien trabaja sobre el código.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — El sitio: una portada, no una copia de la documentación

*commit a659980*

`docs/index.html` servido por GitHub Pages, con `.nojekyll` para que se publique
tal cual y sin paso de construcción — la misma restricción que tiene el núcleo.

**Una sola fuente por documento.** La portada NO reescribe la especificación, el
tutorial ni las decisiones: enlaza a los `.md` del repositorio, que ya existen y
son la fuente. Duplicarlos para que se vean lindos es garantizar que se
desincronicen, que es exactamente el defecto que se corrigió esta semana con las
tres copias de «está ejercitada».

Lo que la portada sí aporta, y un Markdown no puede: la **medida anotada**. Cada
línea con su nota al costado explicando qué hace —qué es `ninguno`, por qué
`segun` es obligatorio, qué significa que `alcance` esté en prosa—. Y el rojo con
sus testigos al lado, que es lo que ninguna otra herramienta muestra y lo que
mejor explica el proyecto en diez segundos.

El README seguía siendo la puerta de entrada con 661 líneas: funciona como
manifiesto para quien ya está mirando el repositorio, y es demasiado para quien
llega sin saber qué es esto.

Responsive de verdad, no por descuido: las rejillas de 12, 5, 4 y 3 columnas se
apilan por debajo de 860px y los bordes que separaban a la izquierda pasan a
separar arriba, para que la retícula siga leyéndose en un teléfono. El titular
escala con `clamp()`.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — El README dice dónde está el sitio y cómo instalarlo

*commit 20281e4*

Un repositorio recién abierto tiene que contestar «¿qué es?» y «¿cómo lo pruebo?»
antes del primer scroll. La cabecera lleva ahora el sitio, PyPI, el release y la
única línea que hace falta para empezar.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — La sección del lenguaje ahora se ve como el editor

*commit 71ce28f*

Las anotaciones al costado rompían la sangría —cada línea era un bloque, así que
el código no se leía como código— y separaban tanto las líneas que la medida
dejaba de verse como una unidad.

Ahora es el editor: pestaña con el nombre del archivo, números de línea, y arriba
de todo la línea gris del CodeLens que el servidor LSP emite de verdad. Esa línea
es la mejor explicación de qué hace Oracle: nadie la escribió, la pone el editor,
y dice qué evidencia pone a prueba esa medida.

Las anotaciones no se pierden: bajan a una leyenda numerada por línea, donde se
leen sin deformar el código.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — La ventana del editor se ajusta al código

*commit 43a8a4e*

Tenía `max-width: 78ch` fijo y la línea del `porque` no entraba, así que
aparecía la barra de scroll del sistema —clara, gruesa, encima del bloque
oscuro— y el editor quedaba cortado a la mitad del ancho disponible.

Tres cosas: la ventana usa `width: fit-content` y se ajusta a lo que contiene;
el `porque` se acorta a «rompe el índice», que sigue siendo prosa de verdad y
deja la línea más larga en 62 caracteres; y si en un teléfono hace falta
scrollear, la barra es fina y del color del editor, no del sistema.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — Los clientes de editor entran al repositorio

*commit 6ec2cfd*

Vivían en dos lugares y ninguno era éste. La fuente de la extensión de VS Code
estaba en `/tmp/ext-oracle/` —que se borra al reiniciar— y una copia incrustada
en los heredocs de `cs50-vscode/install.sh`, un repositorio de otro proyecto.

Las dos copias YA habían divergido: mientras la extensión iba por la 1.2.1 con
CodeLens y la búsqueda del servidor en tres escalones, la copia de `cs50-vscode`
seguía en la 1.1.4. Lo mismo con Emacs: el `.el` instalado en
`~/.local/share/emacs50/` tenía todavía la ruta clavada a `~/Dev/oracle`.

Es la misma duplicación que este proyecto persigue, con la mitad en un
directorio temporal.

`editores/vscode/empaquetar.py` arma el `.vsix` desde la fuente, sin npm ni
vsce: un .vsix es un ZIP con dos archivos de metadatos. La versión sale de
`package.json` y de ningún otro lado — estaba escrita en tres.

Comprobado: el .vsix que sale del repositorio tiene los cuatro archivos de la
extensión byte a byte iguales a los del que está instalado y funcionando.

`editores/README.md` explica cómo instalarlo sin tener la configuración del
aula, cómo los clientes encuentran el servidor, y el límite conocido de que el
servidor no arranca sin proyecto.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — Plan de 0.3.0: bibliotecas, la documentación de punta a punta, y el reparto

*commit 64a0a9e*

Escrito para que codex y agy trabajen contra un documento y no contra la memoria
de una conversación.

Tres frentes: la deuda de 0.2.0 —el LSP que no arranca sin proyecto—, las seis
correcciones de DECISION-007 ordenadas por dependencia, y la documentación
reorganizada como un camino en vez de cuatro documentos sueltos.

Anota además que DECISION-007 justifica descartar dos fases de telemetría con un
hecho que hoy es falso: decía «un proyecto que es privado a propósito y cuya
decisión de publicar está diferida». La conclusión sigue en pie por el costo
estructural, pero el argumento hay que reescribirlo antes de aplicarlo.

Y fija las condiciones de integración, que salen de esta historia y no de la
desconfianza: nada entra sin su número de mutación, la evidencia no se fabrica, y
un sobreviviente se mira antes de taparlo.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-08-31 — Bibliotecas: la certificación publica lo que fue mutado

*commit 92b402d*

El ejemplo se midió con tools/mutar.py: 12 de 12 mutantes murieron por conducta, sin sobrevivientes ni rechazos del álgebra. La certificación recalcula ese denominador y falla si el número publicado no coincide o queda un vivo.

El listado quedó medido con los umbrales <= 0 y <= 5 juntos, dos orígenes segun y un alcance de dos líneas completo. La rama inválida también fija su código de salida.

Mutación de código: nucleo/biblioteca.py 59/59 y tools/cli.py 357/357; cero sobrevivientes, equivalentes, timeouts y errores de arnés. Suite: 819 tests verdes. Corpus: 131 casos OK.

Aceptación conserva un rojo preexistente: tres medidas del corpus raíz sólo tienen evidencia no observada. Se reprodujo igual sobre HEAD limpio y no se fabricó evidencia para taparlo. Los tests, datos y tools/mutar_codigo.py quedan fuera del perfil de mutación de código; cada comando fue ejecutado y rechazado explícitamente.

## 2026-08-31 — Merge branch 'biblioteca-0.3.0': una biblioteca publica qué fue mutado, y su listado deja ver el aflojamiento

*commit b2090d7*

Correcciones 1, 3 y 5 de DECISION-007, sobre el prototipo de la rama
propuesta-biblioteca. Trabajo de codex; los números se verificaron acá, uno por
uno, corriendo el arnés sobre su rama:

    819 tests · corpus 131 casos · nucleo/biblioteca.py 59/59 · tools/cli.py 357/357

Los cinco declarados coincidieron con los medidos.

El invariante se respeta: cero EntryPoint.load(), cero import_module, cero exec.
Descubrir una biblioteca sigue siendo leer datos, y cargar una medida sigue sin
ejecutar Python.

La biblioteca de ejemplo trae A PROPÓSITO una medida con umbral <= 5 junto a una
con <= 0: la corrección 5 se demuestra sola en el listado, sin necesidad de una
alarma que infiera qué es «aflojado» —política que DECISION-007 no define y que
codex se negó a inventar—.

El rojo de aceptación es el preexistente de DECISION-004; codex lo reprodujo
sobre HEAD limpio antes de dejarlo, en vez de fabricar evidencia para taparlo.

Faltan las correcciones 2, 4 y 6. La 2 —procedencia cruzando la frontera del
paquete— bloquea el descubrimiento y la selección, y por eso «oracle biblioteca
listar» recibe una carpeta local y no lista paquetes instalados.

## 2026-09-01 — Modo sombra: una medida heredada se mide y se reporta sin tumbar la corrida

*commit 7591e88*

Activar `catalogo_base` te da medidas que ven cosas que las tuyas no veían, y
por eso mismo te pone en rojo. Es correcto —esos defectos estaban— pero si la
primera experiencia de heredar un catálogo es que el proyecto entero deja de
pasar, no se hereda una segunda vez.

Se midió sobre los dos consumidores reales antes de escribir nada. Con el Oracle
publicado, sus catálogos —escritos antes de que `segun` existiera y antes de
L−1— quedan así:

    LyraGASP   9 + 16 +  9 = 34 infracciones
    Jam       41 + 54 +  9 = 104

Ninguna es un defecto nuevo: están viejos.

## No es una característica de bibliotecas

DECISION-007 pone la sombra como parte de las bibliotecas de políticas. Al
medirlo apareció que el problema no viene de una biblioteca: viene del catálogo
BASE, que los dos consumidores ya activan. Así que la sombra se declara en
`oracle.json` y vale para cualquier conjunto heredado —base, perfil o
biblioteca—, lo que además la desacopla de la corrección 2, que era lo que la
bloqueaba. Queda anotado en la decisión, con el porqué del cambio.

## La sombra no silencia: declara

Lo que se apaga es la CONSECUENCIA de un rojo, no la medición. La medida se
evalúa igual, se imprime igual con su marca `[EN SOMBRA]` en la línea del
veredicto, y el conteo, la antigüedad y el motivo salen en cada corrida — para
que «lo tengo en sombra hace ocho meses» sea un hecho que se lee, no una
comodidad que se olvida.

Y apagar no sale gratis. Tres medidas vigilan la sombra misma, y NINGUNA puede
ponerse en sombra a sí misma: sería apagar el único mecanismo que impide que
apagar salga gratis.

    meta.toda_sombra_declara_desde_y_porque
    meta.ninguna_sombra_ya_en_verde
    meta.ninguna_sombra_sobre_una_medida_que_no_existe

La segunda es la que evita que una etapa de transición se vuelva permanente: si
la medida ensombrecida ya da verde, no hay nada que perdonar.

## Lo que encontró la mutación, que no eran tests faltantes

El mutante de `In → NotIn` en la línea de la marca sobrevivió. Al escribir el
test para matarlo, el test falló contra mi propio código: `v.linea()` devuelve
el veredicto MÁS los testigos, y yo pegaba `[EN SOMBRA]` al final del bloque —a
cinco renglones del id que ensombrece, donde nadie la asocia—. Es lo mismo que
no marcarla. Ahora va en la línea del veredicto.

De paso destapó que un test anterior pasaba de casualidad: ensombrecía
`meta.toda_medida_esta_ejercitada`, que la aceptación NO evalúa —necesita
`medida_en_uso`, que produce mutar.py—. La sombra que creía estar probando era
inerte.

## Números

    tests             +19, suite completa en verde
    nucleo/marco.py     40/40  sin sobrevivientes
    nucleo/proyecto.py 117/117 sin sobrevivientes
    tools/aceptacion.py 45 sitios · 0 sobrevivientes en el código de este cambio

`tools/aceptacion.py` cumple ahora el criterio de HERRAMIENTAS_CUSTODIAS —
custodia qué rojos tumban la corrida, y eso no lo dice ninguna medida— pero NO
entra todavía: la corrida completa encontró 17 sobrevivientes preexistentes y 1
error de arnés en su código de reporte, anterior a este cambio. Meterlo hoy
pondría al proyecto en rojo por deuda ajena. El número quedó escrito donde se
toma la decisión.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — Merge branch 'modo-sombra': heredar un catálogo deja de ser todo o nada

*commit 2f6a758*



## 2026-09-01 — `pip install` falla en casi cualquier Linux moderno, y la portada lo decía igual

*commit c69e021*

El README, el sitio, las notas del release y el aviso de la extensión decían
`pip install oracle-metalenguaje`. En Arch, Debian 12+, Ubuntu 23.04+ y Fedora
eso falla de entrada:

    error: externally-managed-environment
    × This environment is externally managed

Es PEP 668: la distribución protege su Python, y hace bien. Lo reportó el usuario
al seguir las instrucciones que publicamos ayer.

Ahora la forma recomendada es `uv tool install oracle-metalenguaje`, y no es
sólo para esquivar el error: deja los nueve comandos en el PATH, cada uno en su
entorno aislado. **Con `pip` en un venv no alcanza para el editor** — el
ejecutable `oracle-lsp` queda dentro del venv, y los clientes de Emacs y VS Code
lo buscan en el PATH. Instalado así, el editor no lo encuentra salvo con el venv
activado.

La ruta con `pip` queda documentada, pero dentro de un entorno propio y diciendo
por qué hace falta.

Se verificó lo que se publica: `uv tool install` deja los 9 ejecutables y
`oracle-lsp` contesta un `initialize` por stdio con sus capacidades.

Y algo que conviene saber: `uv tool install` sobre una instalación previa
enlazó 8 de los 9 y se saltó `oracle-lsp` sin decir nada. Con `--force` van los
nueve. Si a alguien le falta el servidor teniendo el paquete, ése es el primer
lugar donde mirar.

Extensión de VS Code 1.2.1 → 1.2.2: cambia el aviso que se muestra cuando no
encuentra el servidor, que hasta ahora recomendaba el comando que falla.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — El módulo que dice quién falla entra al arnés, y queda en cero

*commit 0f340f1*

`tools/aceptacion.py` estuvo fuera del perfil de mutación desde siempre. Es el
módulo que decide QUÉ ROJOS TUMBAN LA CORRIDA —y desde el modo sombra, cuáles
no—, así que custodia una afirmación que ninguna medida hace: las medidas dicen
si algo está mal, no si eso debe fallar. Es exactamente el criterio de
HERRAMIENTAS_CUSTODIAS.

Su primera ronda completa dejó 17 sobrevivientes y 1 error de arnés. Nada
observaba los conteos de rojos y verdes, la clasificación de huecos, el corte
del texto ni los códigos de salida. Ahora: 44 mutantes, 44 muertos, cero
sobrevivientes, cero errores de arnés, cero equivalentes declarados.

## El error de arnés no era un mutante: era una ronda inconclusa

`if __name__ == "__main__"` con el comparador dado vuelta hace que el módulo se
ejecute AL IMPORTARSE, y el descubrimiento muere con SystemExit. Eso no dice ni
que el código está fijado ni que no lo está: vale menos que un sobreviviente.
`cli.py` y `corpus.py` ya usaban `{"__main__": main}.get(__name__)` por este
mismo motivo; `aceptacion.py` había quedado atrás.

## El de `sys.path.insert(0, RAIZ)` no era equivalente

Iba a declararlo en equivalentes.json, y buscarle la razón escrita —que el arnés
exige, y con razón— me hizo encontrar el caso en que no lo es: TODO proyecto que
consume Oracle tiene su propia carpeta `catalogos/`. Corriendo la herramienta
desde adentro de uno, el directorio actual queda antes en `sys.path`, y con
`insert(1)` se importaría el `catalogos` DEL CONSUMIDOR en vez del propio. El
test lo reproduce con un `catalogos/__init__.py` que levanta excepción.

Diez tests nuevos. Los conteos que se publican, la diferencia entre un hueco
abierto y uno archivado, y que negarse a ejecutar código ajeno NO sea un verde
—si no se pudo medir, sale 1— quedan fijados.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — Merge branch 'aceptacion-al-arnes': el módulo que decide quién falla, vigilado

*commit 0674d13*



## 2026-09-01 — El camino de documentación, con cada comando ejecutado

*commit bf5bfbd*

Los pasos 2, 5 y 7 del plan de 0.3.0. Reemplazan lo que quedó sin mergear en la
rama `docs-camino`, donde 794 líneas afirmaban haberse verificado y no se había
ejecutado un solo comando: el documento decía que `oracle --version` imprime
`algebra 0.4 · sintaxis 0.2` cuando son 0.5 y 0.1.

Éstos se escribieron al revés: primero se corrió todo contra el paquete
publicado en PyPI, y la prosa se escribió alrededor de esas salidas.

## 02 — De cero a un rojo

De `uv tool install` a un rojo con testigos. Cada bloque es una transcripción,
incluida la del error de la plantilla sin completar, que enseña más que el
camino feliz.

Termina donde el proyecto de juguete queda en rojo por
`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`, y ese rojo se explica
en vez de esconderse: los dos casos son `construida`, y eso es cierto.

NO muestra el modo sombra aunque cerraría ese rojo con elegancia: la sombra se
construyó hoy y NO está en 0.2.0. Documentar contra el paquete instalado, y no
contra el árbol de trabajo, es lo que hace que estas páginas sirvan.

## 05 — Por qué la mutación

El sobreviviente está provocado de verdad: se borra el caso verde y
`quitar_filtro` pasa inadvertido. También se muestra que aflojar el umbral a
`<= 1` NO COMPILA —la macro `ninguno` declara que su umbral es cero— que es una
defensa contra el aflojamiento que no estaba contada en ningún lado.

Los tres ejemplos de sobrevivientes citan commits de este repositorio y se
verificaron uno por uno: 8f16903 (código que sobraba), 0f340f1 (una equivalencia
que no lo era) y 7591e88 (un defecto real, no un test faltante).

## 07 — Conectar a un proyecto propio

Cierra el rojo del paso 2 con un sensor de verdad: puro, sin `open` ni red,
separado del adaptador que camina el disco. El adaptador no tiene ni un `if`
sobre la convención — pregunta y transcribe.

Con el caso `observada` que el sensor produjo, el proyecto llega a
`VEREDICTO: VERDE`. Hasta el ejemplo de `@escalar` se ejecutó antes de
publicarlo.

`docs/README.md` ordena los nueve pasos y enlaza a los documentos que ya
existen en vez de copiarlos.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — DECISIÓN 009 — de quién es el caso, y por qué el código todavía no

*commit f79e10d*

Resuelve la corrección 2 de DECISION-007, que pedía decidir «antes de la primera
versión» qué casos miran las medidas meta cuando una biblioteca trae su propio
corpus. La decisión: cada medida lo declara en su `donde`, y no es uniforme.

Dos miran sólo lo propio —`la_medida_no_se_fija_solo_con_evidencia_fabricada` y
`el_hueco_declarado_explica_por_que`— y dos miran todo —`el_caso_reclama_una_
medida_que_existe` y `el_caso_se_pone_como_debe`—.

El criterio que separa las columnas: un rojo sobre el que no puedo actuar enseña
a ignorar la herramienta. Es el mismo argumento del modo sombra, un nivel abajo.

## El código no se escribe hoy, y eso también se decide

HOY NO EXISTE NINGÚN CASO AJENO. Se verificó: `catalogos/` trae 43 medidas y
CERO casos, y `tools/aceptacion.py` lee únicamente `proy.corpus`. El
descubrimiento de bibliotecas no está construido.

Un campo `es_heredado` agregado hoy sería constante `false`: ninguna evidencia
podría ponerlo en true, ningún test podría distinguir su presencia de su
ausencia, y su mutante sobreviviría. Sería código que nada observa — lo que este
proyecto borra cuando lo encuentra.

La decisión se toma ahora, que es lo que 007 pedía; el código llega con el
descubrimiento, que es lo único que puede ejercerlo. Y esta decisión desbloquea
ese trabajo: codex se negó a construir descubrimiento mientras la corrección 2
estuviera abierta, y tenía razón.

## Cómo se llegó

El análisis se hizo dos veces en paralelo y por separado —acá y por agy— y las
dos llegaron a la misma opción. Las siete citas de código del análisis externo se
verificaron una por una contra el repositorio: las siete exactas.

Difirieron en una fila: `el_hueco_declarado_explica_por_que`. Acá se había puesto
«todo» por inofensivo; el análisis externo argumentó que un hueco sin explicar en
una biblioteca ajena es responsabilidad de su certificación. Ese argumento ganó.

Y aportó lo que faltaba: el precedente de `es_heredada` era BINARIO —proyecto
contra catálogo base— y esto no lo es. De ahí el segundo campo, `biblioteca`.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — Descubrimiento y selección de bibliotecas, con el origen del caso reificado

*commit b16b8f0*

Implementa DECISION-009 y desbloquea lo que quedaba de la corrección 2 de
DECISION-007. Trabajo de codex; los números se verificaron acá, uno por uno,
corriendo el arnés sobre su rama.

## El invariante se respeta

Cero EntryPoint.load(), cero import_module, cero exec. El descubrimiento usa
`importlib.metadata.distributions()` y `locate_file()`, que ubican archivos SIN
importar el paquete. Cargar una medida sigue sin ejecutar Python de nadie.

Y va más lejos de lo que se pidió: una distribución candidata SE RECHAZA si su
RECORD enumera Python o un binario ejecutable. No es «no la importo», es «no la
acepto como biblioteca».

## Las cuatro medidas, según la tabla

    la_medida_no_se_fija_solo_con_evidencia_fabricada   c.es_heredado == false
    el_hueco_declarado_explica_por_que                  c.es_heredado == false
    el_caso_reclama_una_medida_que_existe               sin filtro de origen
    el_caso_se_pone_como_debe                           sin filtro de origen

Las cuatro lo declaran también en su `alcance`, que era la otra mitad del pedido.

## Verificado con una biblioteca instalada de verdad

Se instaló el ejemplo como paquete en un venv limpio, se lo seleccionó en un
proyecto consumidor y se corrió el ciclo entero:

  · las 2 medidas de la biblioteca aparecen como heredadas y juzgan al consumidor
  · el corpus ajeno llega: «catálogo: 47 medidas · corpus: 4 casos» (1 propio + 3)
  · los 3 casos de la biblioteca son `procedencia: construida`, así que SIN el
    filtro la medida habría contado 3 infracciones. Contó 1: la del consumidor.

Esa última línea es la prueba de que DECISION-009 hace lo que dice.

## Números, medidos acá

    nucleo/biblioteca.py   72/72      nucleo/marco.py      41/41
    nucleo/proyecto.py    129/129     tools/aceptacion.py  46/46

Cero sobrevivientes, cero timeouts, cero errores de arnés, cero equivalentes
declarados en los cuatro. Suite completa en verde; corpus 131 casos.

La aceptación sigue terminando en «✗ — 1 problema»: el rojo preexistente de
DECISION-004, idéntico a como está en main. El informe de codex abre con «80
defectos en rojo, 47 verdes correctos», que son los conteos de casos y no el
veredicto; se deja anotado porque los números que se publican tienen que ser los
que alguien ve al correrlo.

## Lo que falta

`oracle biblioteca` sólo opera sobre una ruta local: no hay verbo para listar las
bibliotecas INSTALADAS ni las seleccionadas. El descubrimiento funciona sin él
—la selección va en oracle.json— pero para inspeccionar antes de instalar, que
es el punto de la corrección 3, hace falta.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — Merge branch 'biblioteca-descubrimiento': una biblioteca instalada se descubre sin ejecutarla

*commit 2d638e7*



## 2026-09-01 — `oracle biblioteca instaladas`: se puede leer lo que se instaló

*commit 1a49f9c*

Faltaba el verbo. `oracle biblioteca` sólo sabía mirar una carpeta que ya tenías
a mano, y la corrección 3 de DECISION-007 existe para poder inspeccionar ANTES
de decidir: lo que determina si una política sirve para un proyecto es su
`alcance`, y no se puede leer lo que no se puede listar.

    BIBLIOTECAS INSTALADAS · 1

      segtem.meta.calidad 0.1.0   ✓ seleccionada
        álgebra 0.5 · sintaxis 0.1 · 12 mutantes publicados
        /…/site-packages/oracle_bibliotecas/oracle_biblioteca_segtem_meta_calidad
        ver sus umbrales y alcances:  oracle biblioteca listar /…

Publica el número de mutación en la primera mirada —lo que distingue una
biblioteca probada de una que nadie rompió, según la corrección 1— y encadena
con `listar`, que es donde están los alcances.

## El caso que nada más agarraba

Una biblioteca SELECCIONADA Y NO INSTALADA sale con código 1 y lo dice. Sin
esto, el proyecto cree tener una política que no tiene y ninguna medida podría
avisarlo: las medidas de esa biblioteca sencillamente no se cargaron, así que no
hay nada que se ponga rojo. Es un silencio que ninguna otra cosa rompe.

El proyecto es OPCIONAL: querer ver qué hay instalado es una pregunta legítima
parado en cualquier directorio, antes de tener un proyecto.

## Lo que encontró la mutación

Los primeros cinco sobrevivientes estaban todos en el DESPACHO, no en el
manejador: los tests llamaban a `cmd_biblioteca_instaladas` directo y nunca
pasaban por `oracle biblioteca instaladas`. Es el mismo error que en el modo
sombra, dos días seguidos — probar la función en vez del comando.

Tres tests nuevos por el camino real. El que más importa es el que rechaza una
ruta de más: sin él, `oracle biblioteca instaladas /una/ruta` ignoraba el
argumento en silencio, y alguien podía creer que estaba inspeccionando esa ruta
cuando listaba el entorno entero.

    tools/cli.py: 374 mutantes · 374 muertos · 0 sobrevivientes
    9 tests nuevos · suite completa en verde · corpus 131 casos

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — Merge branch 'biblioteca-instaladas': inspeccionar antes de decidir

*commit b1d488c*



## 2026-09-01 — `oracle diagnostico`: la fase 1, y el contrato de qué no sale se mide

*commit 2b60a6d*

Corrección 6 de DECISION-007. Se adopta la fase 1 —diagnóstico local, sin red— y
nada más.

## Primero se corrigió el argumento, que se apoyaba en un hecho falso

La corrección 6 descartaba las fases 3 y 4 porque su costo era desmedido «para un
proyecto que es privado a propósito y cuya decisión de publicar está diferida y
registrada con fecha». Las dos mitades habían dejado de ser ciertas: el
repositorio se abrió y está en PyPI, y lo de «registrada con fecha» nunca lo fue
—el archivo que citaba no existió nunca—.

La conclusión no cambia y el argumento queda mejor: un servidor, una retención y
una superficie legal son caros para cualquier proyecto de una persona, público o
privado. Ser público no crea a quién rendirle cuentas de los datos; crea la
posibilidad de tener usuarios, que es otra cosa.

Y la condición de la fase 2 pasó de «hoy no hay nadie más usando Oracle» —una
observación que envejecía sola— a un hecho comprobable: cuando alguien que no sea
el autor abra un issue. Las descargas de PyPI no sirven: cuentan espejos y CI.

## El comando

`oracle diagnostico [--salida <ruta>]`. Muestra o guarda, y NO manda nada: el
archivo queda en disco, la persona lo lee entero y decide. Producir información
no autoriza a publicarla.

Del proyecto sale su FORMA —qué carpetas existen, cuántas medidas y casos— nunca
su contenido. Sin nombre de host, con el home y la raíz reemplazados por
marcadores. De las bibliotecas informa las SELECCIONADAS: para reproducir un
problema importa qué políticas están activas, no qué hay instalado.

## Y el contrato se mide, porque un docstring no alcanza

«Nunca sale evidencia» escrito en prosa no impide que un campo agregado el martes
filtre hasta que alguien pegue el JSON en un issue. Hay una relación
`campo_diagnostico` y una medida —`meta.el_diagnostico_no_publica_el_dominio`—
que corre en CADA aceptación.

Se comprobó al revés: ensuciando el diagnóstico a propósito, se pone roja y el
testigo dice qué campo filtró y qué se coló. Una medida que no puede fallar no
mide nada.

## Lo que encontraron los mutantes, que no eran tests faltantes

`rglob("*")` devuelve DIRECTORIOS, y un directorio tiene `suffix` vacío. Con el
comparador dado vuelta, una carpeta pasaba el filtro y compensaba el conteo — por
eso el mutante sobrevivía. Se agregó `is_file()`, que además es lo correcto: sin
él una carpeta llamada `x.json` contaba como medida. Hay un test que la crea.

Un `sorted(..., key=len)` ordenaba dos reemplazos cuyo orden se conoce al
escribirlos. El mutante que cambia la clave no puede cambiar el resultado: era un
cálculo que nada observa. Se borró; la lista se construye ya ordenada.

El TIMEOUT de la ronda también era propio: los tests llamaban a `cli.main` sin
`--proyecto`, así que resolvían el repositorio real, y el mutante que da vuelta
`subcomando == "test"` hacía correr la verificación entera en cada uno. Se
apuntaron a un proyecto temporal. NO se subió el límite de tiempo: eso habría
tapado el síntoma.

## Dos equivalencias declaradas, con su razón

`ensure_ascii=False` e `indent=2` sólo cambian el formato; el JSON parsea al
mismo objeto. Hoy ningún valor del diagnóstico puede traer un carácter no ASCII
—versiones, `platform`, marcadores, e ids que el lenguaje restringe a ASCII a
propósito— así que un test tendría que inventar un campo inexistente para fallar.
La bandera NO se borra: el archivo está hecho para leerse, y el día que un campo
traiga una tilde, escaparla lo volvería ilegible.

    nucleo/diagnostico.py  17/17      tools/aceptacion.py  46/46
    tools/cli.py          392/392 (2 equivalentes declarados)

21 tests nuevos · suite completa en verde · corpus 131 casos.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — Merge branch 'diagnostico-local': reportar un problema sin publicar el dominio

*commit b07f037*



## 2026-09-01 — `oracle biblioteca nueva`: publicar una deja de ser armar rutas a mano

*commit 5e44d81*

Faltaba el paso que convierte «se puede publicar una biblioteca» en «alguien la
publica». El descubrimiento busca el manifiesto en una ruta DERIVADA del nombre
de la distribución y en ningún otro lado; armarla a mano es donde se equivoca
todo el mundo la primera vez, y el error es silencioso: la biblioteca no aparece
y nada dice por qué.

    oracle biblioteca nueva aula.calidad

Deja el esqueleto con la ruta fija ya puesta, el manifiesto con las versiones de
contrato de este Oracle, y un `pyproject.toml` sin dependencias — porque una
biblioteca de políticas es DATOS: si trajera Python el descubrimiento la
rechazaría.

## Seguir mis propios pasos encontró dos errores en ellos

El paso 3 decía `oracle biblioteca verificar <raíz del paquete>` y el manifiesto
vive en la raíz de DATOS. El error que daba —«falta oracle-biblioteca.toml como
archivo físico»— no explicaba nada. Hay un test que comprueba que la ruta
impresa sea la correcta.

Y la plantilla proponía un flujo IMPOSIBLE: ponía `mutantes = 0` diciendo «corré
verificar y copiá lo que dice», pero el cero se rechaza antes de llegar ahí.
Arranca en 1, y el comentario explica el mecanismo real: `verificar` responde
«publica 1, pero mide 6» y se copia el 6.

Probado de punta a punta: del andamio a una biblioteca instalada y descubierta,
siguiendo sólo los pasos que el comando imprime.

    oracle biblioteca nueva …          → esqueleto
    (una medida + dos casos)
    oracle biblioteca verificar …      → «publica 1, pero mide 6»
    oracle biblioteca verificar …      → BIBLIOTECA CERTIFICADA · 6/6
    pip install .                      → BIBLIOTECAS INSTALADAS · 2

## El arnés atajó dos cosas más

Los ids de `equivalentes.json` son POSICIONALES, y agregar la función corrió el
`json.dumps` del diagnóstico de la línea 166 a la 169. La ronda se negó a correr
—MUTACIÓN NO CONFIABLE— y un test lo cazó antes: si el id hubiera quedado
apuntando a otra línea, la equivalencia habría perdonado un mutante DISTINTO en
silencio. Queda anotado el corrimiento en la razón, como ya se había hecho con
`cifras.py`.

Y un test propio era ingenuo: buscaba que la palabra `dependencies` no apareciera
en el pyproject, pero el comentario de la plantilla explica justamente por qué no
las hay. Ahora busca una línea de declaración.

    nucleo/biblioteca.py   76/76      tools/cli.py  411/411 (2 equivalentes)
    11 tests nuevos · suite en verde · corpus 131 casos

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — Merge branch 'biblioteca-nueva': el andamio de una biblioteca publicable

*commit fa56183*



## 2026-09-01 — La documentación entra al arnés: la referencia nombra lo que el lenguaje emite

*commit 2b6fd44*

La documentación era la única parte del proyecto SIN arnés. El código no puede
quedar desactualizado sin que un mutante lo diga; la prosa sí, y por eso envejeció
sola: DIEZ de diecinueve relaciones del lenguaje no estaban nombradas en la
especificación, incluidas TODAS las de L−1 y L−2, documentadas en agosto. Nada lo
había señalado nunca — se encontró porque alguien preguntó.

Ahora hay una relación —`relacion_documentada`— y una medida que corre en cada
aceptación. Nació en 11 rojos, y esos rojos fueron la lista de trabajo: cerrarla
escribió la sección «1.1 Las relaciones que el lenguaje emite», con las
diecinueve, qué describe cada una y quién la emite.

Se comprueba al revés: sacando `sombra` de esa tabla, la medida se pone roja.

## Lo que la medida NO puede, y lo dice en su alcance

Comprueba que el NOMBRE aparezca. Si la explicación es correcta, si está
actualizada o si alcanza para usar la relación son preguntas que ninguna medida
puede contestar, y fingir que sí sería el defecto que este proyecto persigue un
nivel más arriba: un verde que se lee como «la documentación está bien» cuando
significa «los nombres aparecen».

## Casi meto un rojo imposible de arreglar

La primera versión ponía en rojo a TODO proyecto consumidor: Jam, LyraGASP y
cualquier otro habrían quedado rojos por no documentar las relaciones DE ORACLE
—un lenguaje que no escribieron, en un archivo que el paquete ni siquiera
incluye—. Es el mismo error que `es_heredada` resolvió para las medidas y
DECISION-009 para los casos: un proyecto responde por LO SUYO. Lo atraparon
cuatro tests que ya existían, no yo pensándolo.

Y el arreglo obvio tampoco servía. `requiere` es el mecanismo para «no puedo
concluir», pero emitir la relación VACÍA hace que la medida sea aplicable igual,
salga SIN EVIDENCIA, y la aceptación cuente eso como falla: el mismo rojo por
otro camino. Lo correcto es no emitir ni la clave — `medidas_aplicables` elige
juezas por las relaciones presentes—. Hay un test que fija la distinción entre
«hay referencia y nada que documentar» y «no hay referencia», que son dos
situaciones distintas con datos distintos.

    nucleo/marco.py  45/45      tools/aceptacion.py  46/46
    4 tests nuevos · suite en verde · corpus 131 casos

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — Merge branch 'documentacion-vigilada': la referencia deja de poder envejecer en silencio

*commit a7fa51d*



## 2026-09-01 — Los verbos del CLI viven en un lugar, y la ayuda deja de poder olvidarlos

*commit 107863a*

Estaban escritos DOS veces por sustantivo —la tupla del despacho y el mensaje
«Verbos disponibles»— más una tercera en cada ayuda. Y ya habían derivado:
`caso` ACEPTABA `nueva` y anunciaba sólo «nuevo, listar, generar», así que un
verbo válido era invisible para quien leyera el error.

Ahora hay un `VERBOS`, el despacho lo lee y el mensaje lo imprime: no pueden
decir cosas distintas. Los alias se declaran en `ALIAS` en vez de esconderse en
la tupla — un alias que nadie escribió a propósito es un alias que nadie puede
documentar.

## Y con eso ya se podía medir

`meta.todo_verbo_del_cli_esta_en_la_ayuda` nació con TRES rojos:
`medida probar`, `caso generar` y `biblioteca nueva` — el último agregado por mí
esa misma mañana. La ayuda es exactamente el lugar donde una novedad se olvida,
porque es prosa y hasta ayer nada la miraba. Los tres están ahora en `--help`, y
se comprobó que `caso generar` hace lo que la ayuda dice.

## Las dos medidas se atraparon entre ellas

Al crear la relación `verbo_del_cli`, `meta.toda_relacion_del_lenguaje_esta_en_la
_referencia` —de ayer— se puso roja: la relación nueva no estaba en la
especificación. Ninguna de las dos cosas la vi yo.

## Lo que encontró la mutación

Un `except ImportError` que envolvía la importación del CLI: no se pudo
demostrar un caso donde se dispare, y si se disparara haría algo peor que fallar
—dejaría la medida sin correr EN SILENCIO, el verde vacío que este proyecto
persigue—. Su mutante sobrevivía, que es decir que nada podía distinguir tenerlo
de no tenerlo. Se borró: si el CLI no se puede importar, que se vea.

El otro, `cli.__doc__ or ""` → `and`, sí era un test faltante: con `and` la ayuda
llegaría vacía y la medida dejaría de correr sin decirlo.

    nucleo/marco.py  49/49    tools/aceptacion.py  48/48
    tools/cli.py    412/412 (2 equivalentes declarados)
    8 tests nuevos · suite en verde · corpus 131 casos

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01H13w6UT1RpjBdnBnWwehc4

## 2026-09-01 — Merge branch 'verbos-en-un-solo-lugar': la ayuda no puede olvidar un verbo

*commit 1ed6abb*



## 2026-09-01 — El vocabulario declara su significado, y el manual sale de eso

*commit 2f3edfa*

`falso_verde` era una cadena en un `frozenset` y su sentido vivía repartido en cuatro `.md`
—`PLAN-LENGUAJE.md`, `corpus/README.md`, el tutorial y `docs/07`—, ninguno de ellos la fuente.
Ahora el nombre y su explicación viajan juntos en la declaración, y de ahí salen las dos cosas
que importan.

La primera es el error. Quien escribe `etiqueta: falso_rojito` ya no recibe una lista de cinco
nombres parecidos: recibe los cinco con qué es cada uno, en el momento exacto en que le hace
falta. El «llegó 'X'» va pegado a la primera línea y no al final de la enumeración, donde
quedaba a cinco renglones de la columna que lo señala. El diagnóstico del editor lleva lo mismo.

La segunda es `oracle manual`: siete temas —los seis operadores de una tubería, los cuatro
orígenes de un umbral, las tres columnas cerradas de un caso, las relaciones que el lenguaje
emite sobre sí mismo y los verbos del comando—. No es un documento escrito aparte sino una
vista, así que no tiene dónde envejecer. `--html` genera `docs/manual.html`, y un test lo
compara byte a byte con la salida del comando.

Lo único que sí podría envejecer es el registro que dice qué mostrar, y eso se mide:
`meta.todo_vocabulario_cerrado_esta_en_el_manual` y
`meta.toda_opcion_del_vocabulario_declara_su_sentido`. La segunda encontró tres opciones
explicadas en cuatro palabras —`persona`, `accidente`, `observacion`—, que ya se corrigieron.

De paso, la deuda que dejaba CI en rojo. `tools/mutar.py` salía 1 desde ayer: cinco medidas
—las tres de sombra, la del diagnóstico y la de documentación— no tenían NINGÚN caso del
corpus, y `meta.toda_medida_esta_ejercitada` las contaba una por una. El corpus pasa de 131 a
160 casos; `mutar.py` de 630/630 con salida 1 a 703/703 con salida 0.

Ocho de esos casos llevan evidencia OBSERVADA de corridas reales: los verbos y los vocabularios
de este repositorio, el diagnóstico que imprime hoy, las veintidós relaciones contra la
especificación y las tres sombras de un proyecto creado para esa corrida. Sin ellos
`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` subía de 3 a 8, y 3 es el número que
el workflow exige.

`tools/manual.py` entra a `HERRAMIENTAS_CUSTODIAS`: su registro es de dónde sale la relación,
así que si se rompe las dos medidas se ponen verdes sin mirar nada. 39/39 mutantes muertos, sin
declarar una sola equivalencia. Los once que sobrevivieron primero eran todos aritmética del
render, y se cerraron con casos de borde: dos palabras que suman EXACTAMENTE el ancho fijan a la
vez que la comparación sea estricta, que el espacio cuente uno y que el ancho sea el pedido.

El preámbulo de `sys.path` pasó a la forma de `cli.py`. La guarda `if RAIZ not in sys.path` no
se podía matar: en un test `RAIZ` siempre está, así que la guarda era indistinguible de su
contrario. Y el punto de entrada usa el modismo del proyecto, porque con `is not None` el
mutante `IsNot → Is` hacía que el módulo se ejecutara al importarlo y llamara a `None()`: un
error de arnés no es una muerte.

Verificado: 982 tests · corpus 160 · aceptación en el rojo declarado (3) · mutar.py 703/703
salida 0 · manual.py 39/39 · trazar OK · WHEEL OK con `oracle manual` desde el paquete instalado.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-01 — Tres vistas de una fuente, y tres deudas cerradas

*commit d801ee7*

El manual gana su tercera salida: `man`. La terminal, el sitio y las páginas de manual salen de
las MISMAS entradas, así que no hay una cuarta copia que desincronizar. `oracle manual
--instalar-man <dir>` escribe nueve páginas —`oracle(1)` y una `oracle-<tema>(7)` por tema— y a
partir de ahí `man oracle-etiqueta` anda sin red. `oracle(1)` lee los verbos del mismo diccionario
contra el que el CLI despacha: un verbo nuevo aparece en la página solo.

Tres cosas que groff rompía EN SILENCIO, cada una con su test:

  · un guion largo crudo sale DUPLICADO —medido: «uno — dos» se renderiza «uno —— dos»—;
  · una comilla invertida se vuelve comilla IZQUIERDA de los dos lados, así que `segun` salía
    ‘segun‘. Los pares son código en la prosa del proyecto y en una página de manual eso va en
    negrita;
  · una línea que empieza con punto es una macro, y la prosa de una medida puede empezar con «.»
    sin que nadie lo piense.

## El leak de bloqueos en /tmp

`_bloqueo_de_ronda` creaba `/tmp/oracle-mutacion-<hash>.lock` y no lo borraba nunca. Como cada
mutante corre sobre una raíz distinta, había 6.257 archivos de un solo día.

Borrarlo con el `flock` puesto tiene la carrera clásica del unlink: B abre la ruta, A la
desvincula, C crea otra y la bloquea, y B y C creen los dos que tienen el lock. La solución es un
directorio propio cuyo descriptor hace de coordinador: serializa abrir+bloquear y borrar+
desbloquear, y `samestat` impide desvincular el archivo de otro. Se descartó `st_ino` solo —no
evita que otro ya tenga abierto el inodo viejo— y el temporal de la ronda —dos rondas no
compartirían el punto de encuentro—.

Medido: una ronda entera de `nucleo/fixtures.py` deja CERO archivos. Y la exclusión sigue en pie,
que es lo que había que no romper: tres tests fijan que la ronda rechazada no borre el bloqueo de
la que sí lo tiene, que salir no reviente si el archivo ya no está, y que un `open` fallido suba su
propio error y no un `AttributeError` sobre None.

## Los equivalentes dejan de repuntarse a mano

Los ids de `equivalentes.json` son posicionales y se rompieron CINCO veces en una sola sesión
agregando líneas más arriba. Peor: una de esas veces mapeé mal dos entradas que compartían columna
y tipo, y quedaron las dos apuntando al mismo sitio.

Ahora cada entrada guarda el contenido de su línea y su ordinal entre las líneas idénticas, y
`--reapuntar-equivalentes` las reubica sola. Verificado insertando tres líneas en `nucleo/caso.py`:
reubicó las seis, incluidos los tres `while self.i < len(self.lineas):` idénticos que yo había
mapeado mal. El validador sigue fallando cerrado: la reubicación es una herramienta, no una
amnistía.

## El tercer rojo de la DECISIÓN 004, cerrado como esa decisión decía

No transcribiendo evidencia inventada —esa puerta la prohíbe el documento— sino cambiando el
mundo. Resultó que los referentes reales YA se calculaban: `revisar_frescura` arma un `Referente`
por cada huella del bloque `frescura` de un fixture, y morían adentro de esa función.
`referentes_de_fixture` los expone, y con eso `diferencial/simulacion.json` declara cuatro
referentes con sha256 REALES: el catálogo, la configuración del dominio,
`tools/generar_diferencial.py` y `diferencial/referencia/evaluador.py`.

L−2 dejó de existir sólo en el lenguaje. El rojo bajó de 3 a 2, y el workflow ya exige el 2.

Los dos que quedan no se pueden cerrar y no es pereza: existen para cubrir formas del álgebra que
nadie escribió, generadas desde la gramática. Una evidencia observada para ellas sería una
contradicción — si la forma estuviera en el catálogo, la cubriría `meta.sintaxis_ida_y_vuelta`.

Queda escrito el precedente: antes de dar un rojo por incerrable, preguntarse si el mundo ya
produce la evidencia y nadie la está mirando. Acá estaba a cinco líneas.

Verificado: 1013 tests · corpus 161 · aceptación en 2 rojos declarados · mutar.py 703/703 salida 0
· perfiles/python/mutacion_codigo.py 210/210 · nucleo/fixtures.py y nucleo/vocabulario.py sin
sobrevivientes · trazar OK · WHEEL OK · cero locks tras una ronda.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3dXE49okVZk7VkgSkwxKe

## 2026-09-01 — 0.3.0: la documentación deja de prometer comandos que no corren

*commit 4b9c5f2*

Antes del corte, los dos documentos más viejos se revisaron corriendo cada comando que prometen.
Dos mentían:

  · el tutorial mandaba `sintaxis.py --imprimir` contra un `.json` que ya no existe —esa medida se
    mudó a la superficie infija hace dos releases—, así que el comando fallaba con «No such file».
    Ahora apunta a `proceso.verificacion_vigente.json`, que sí existe y se verificó corriéndolo;
  · `ESCRIBIR-UNA-MEDIDA.md` ofrecía `pip install -e .` como alternativa a `uv`, y eso **falla** en
    Arch, Debian 12+, Ubuntu 23.04+ y Fedora con `externally-managed-environment`. Ahora dice que
    hace falta un venv, y por qué saltear esa protección rompe paquetes del sistema.

Y los dos callaban lo que no existía cuando se escribieron: la sombra, las bibliotecas, el manual y
el diagnóstico. El tutorial gana la sección de herencia —cómo adoptar un catálogo ajeno sin apagar
medidas— y las cuatro filas que le faltaban a la tabla de comandos.

Las notas de 0.3.0 quedan escritas con sus cifras y, sobre todo, con sus cuatro límites conocidos:
los dos rojos de la DECISIÓN 004 que salen a propósito, que ningún proyecto ajeno adoptó Oracle
todavía, que ninguna biblioteca de políticas se publicó, y que los mutadores son de autoría propia
—«703/703 muertos» mide cobertura sobre cinco mutadores que eligió el autor—.

VERSION_DISTRIBUCION 0.2.0 → 0.3.0. El álgebra y la sintaxis no se movieron, así que no se tocan:
unificar las tres versiones mentiría sobre qué cambió.

Verificado: 1013 tests · corpus 161 · aceptación en los 2 rojos declarados · cifras al día ·
WHEEL OK · `sintaxis.py --verificar` con los 21 bloques de documentación en regla.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3dXE49okVZk7VkgSkwxKe

## 2026-09-01 — El instructivo para migrar los consumidores, con el estado medido y no supuesto

*commit 39cd737*

Jam y LyraGASP consumen Oracle por un subtree y hay que pasarlos al paquete. Antes de escribir el
instructivo se midió cada uno, porque lo único irreversible de esta migración es borrar un subtree
que alguien editó a mano: esos cambios no existen arriba y se pierden sin aviso.

Medido el 2026-09-01, sin escribir una línea en ninguno de los dos repos —tienen 4 y 47 archivos
con trabajo sin commitear del usuario—:

  · CERO ediciones locales en `vendor/oracle`, en los dos. El riesgo grande no está;
  · el Oracle de hoy pone a Jam en 104 infracciones sobre 3 medidas, y a LyraGASP en 34 sobre las
    mismas 3. Ninguna es una regresión: son medidas que el Oracle del subtree no tenía;
  · el bloque de sombra de Jam se probó CORRIENDO la aceptación sobre una copia del proyecto. Sale
    `ACEPTACIÓN ✓`, salida 0. No es un bloque propuesto: es uno verificado.

De paso, tres deudas viejas de Jam que el CLAUDE.md del usuario todavía nombra resultaron cerradas:
el `id` desalineado de `004-coberturas-distintas`, los filtros que le faltaban a `snap.al_ras`,
`snap.comparte_cara` y `scatter.cobertura`, y el fixture `vault.json` vencido. Queda una sin
verificar y el documento lo dice como tal: si el corpus sigue sin casos `verde_correcto`, el mutador
`quitar_filtro` sobrevive siempre.

El documento general dice explícitamente qué NO hacer, porque el modo de fallar acá es conocido:
nunca `git stash`, `git clean`, `git checkout .` ni `git reset` en un repo con trabajo ajeno; no
borrar el subtree antes de comprobar que está limpio; no poner una medida en sombra sin leer qué
encontró; y fijar la versión con `==` y no con `>=`, porque un consumidor que se actualiza solo se
pone rojo un martes por algo que no cambió de su lado.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3dXE49okVZk7VkgSkwxKe

## 2026-09-01 — El instructivo de migración rompía el editor de Unreal, y lo dice ahora

*commit 1e8439b*

La primera versión medía bien los rojos y las ediciones locales, y se equivocaba en lo único que
importaba: buscó referencias a `vendor/oracle` filtrando por extensión y encontró dos archivos.
Son NUEVE, y dos son código.

`Content/Python/jam/bridge.py:16` pone `<plugin>/vendor/oracle` en el `sys.path` del intérprete
EMBEBIDO DE UNREAL, para que el plugin pueda importar `oracle_metalenguaje` con el editor abierto.
Unreal usa su propio Python: no ve el entorno de `uv`, ni el del sistema, ni un venv del proyecto.
Siguiendo el instructivo como estaba, Jam quedaba sin Oracle adentro del editor — y sin fallar en
ningún verificador, porque el fallo aparece recién cuando alguien abre el editor.

Lo mismo en chico en LyraGASP: `tools/juzga_oracle.py` importa el paquete y se corre con el Python
del sistema, donde `uv tool install` tampoco lo pone.

Así que la guía ahora empieza por la pregunta que decide todo lo demás —¿el proyecto necesita el
COMANDO o el PAQUETE?— y da tres formas de instalar según la respuesta. Para Jam la correcta es
vendorizar el WHEEL en vez del subtree de git: sigue habiendo un directorio en el repo, pero es un
artefacto con versión fijada y no una copia que hay que acordarse de traer y que se puede editar a
mano sin que nadie se entere. Probado: `pip install --target` y el import anda con el mismo
`sys.path.insert` que ya existe. Y es más chico — 2,3 MB y 183 archivos contra 3,5 MB y 284.

Lo encontró agy auditando Jam, después de dos intentos en que se quedó sin plazo. Lo verifiqué
leyendo `bridge.py` antes de escribirlo, y probé el `--target` antes de recomendarlo.

De paso, dos correcciones más a `jam.md`: el corpus SÍ tiene tres casos `verde_correcto` —la deuda
que yo daba por no verificada está cerrada— y el `vault.json` vencido sigue en `origin/main` pero
ya está resuelto en los cambios sin commitear del usuario.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3dXE49okVZk7VkgSkwxKe

## 2026-09-01 — La página de PyPI no llevaba a ningún lado, y nada lo miraba

*commit 2201cde*

Al revisar https://pypi.org/project/oracle-metalenguaje/0.3.0/ aparecieron tres defectos. Los tres
estaban también en 0.2.0, así que no son una regresión: son un hueco que vivió dos releases porque
nada lo comprobaba.

El grave: el README ES la descripción que PyPI publica, y ahí no existe el árbol del repositorio.
La página invitaba a leer las nueve decisiones, la especificación, ESCRIBIR-UNA-MEDIDA y la
licencia — **18 enlaces relativos, ninguno se podía abrir**. En un proyecto cuyo argumento es «leé
por qué se decidió cada cosa», eso no es un detalle de empaquetado.

Los otros dos: `project.urls` vacío, así que la barra lateral no tenía UN SOLO enlace y quien
llegaba no tenía cómo volver al repositorio, al sitio ni a los issues; y `classifiers` vacío, así
que PyPI no podía filtrar el paquete por versión de Python, por tema ni por estado.

Cuatro tests lo fijan: que el README no tenga enlaces relativos, que SÍ conserve sus anclas internas
—un `#ancla` anda en las dos páginas y volverla absoluta sacaría al lector de la que está leyendo—,
que el paquete declare a dónde ir, y que los clasificadores de versión no se despeguen de
`requires-python`, porque si mañana sube el mínimo y nadie toca la lista, PyPI sigue diciendo que
anda en 3.11.

El estado declarado es `4 - Beta` y no `5 - Production/Stable` porque el README dice EXPERIMENTAL en
la primera pantalla, y decir dos cosas distintas sobre la misma cosa en dos lugares es exactamente
lo que este proyecto persigue en otros lados.

Verificado sobre el wheel construido, no sobre el TOML: 12 clasificadores y 7 Project-URL en el
METADATA real, con los acentos decodificando bien en UTF-8. `twine check` PASSED en los dos
artefactos.

Los metadatos de PyPI son inmutables por versión, así que 0.3.0 queda como está y 0.3.1 existe para
que la página que se ve por omisión sea la correcta.

VERSION_DISTRIBUCION 0.3.0 → 0.3.1. El álgebra y la sintaxis no se movieron.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3dXE49okVZk7VkgSkwxKe

## 2026-09-01 — Los instructivos fijan 0.3.1, y avisan del import que engaña

*commit 3b29c5f*

0.3.1 está en PyPI y verificada contra la API: 7 project_urls, 12 clasificadores y CERO enlaces
relativos en la descripción publicada. Los tres defectos de 0.3.0 quedaron cerrados, y los sha256
publicados coinciden con los artefactos construidos acá.

Los tres documentos de migración pasan a fijar `oracle-metalenguaje==0.3.1`.

Y se agrega una comprobación que salió de equivocarme al verificar este mismo release: probando la
instalación desde PyPI, el ejecutable no aparecía pero `from oracle_metalenguaje import Motor`
funcionaba igual. Parecía un wheel roto. No lo era: el `pip install` había fallado —y yo había
tapado su salida con un `tail -1`— y el import venía del árbol del repo, porque estaba parado
adentro.

Es un modo de fallar que le va a pasar a quien migre, porque los tres caminos de instalación fallan
distinto y ninguno grita. Así que el documento ahora pide correr, DESDE UN DIRECTORIO QUE NO SEA EL
DEL PROYECTO:

    python -c "import oracle_metalenguaje as o; print(o.__file__)"

Si la ruta no está dentro de lo que se instaló, la instalación no está donde uno cree.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3dXE49okVZk7VkgSkwxKe

## 2026-09-02 — El wheel vendorizado dejaba sin fachada al subproceso que corre las UDF del consumidor

*commit 20ef7e4*

El primer defecto de Oracle reportado desde afuera del repositorio, por el consumidor que intentó la
migración de subtree a PyPI que documentamos hace dos commits. El camino que ESE documento le
recomendaba estaba roto.

`nucleo/aislamiento/escalares.py` lanza con el entorno REEMPLAZADO el subproceso que ejecuta el
`escalares.py` de un proyecto, y le pasaba `PYTHONPATH = RAIZ_ORACLE`. En el repo eso es la raíz,
que contiene `oracle_metalenguaje/`. En el wheel, `RAIZ_ORACLE` ES el directorio del propio paquete:
quien lo hace importable es su padre. Así que un consumidor cuyo `escalares.py` hace
`from oracle_metalenguaje import escalar` —lo que la documentación le pide— moría con
`ModuleNotFoundError`.

Sólo se rompía fuera de un venv: adentro, `site.py` agrega `site-packages` por su cuenta y tapaba la
falta.

## Por qué el arnés no lo vio, que es lo que más importa

`verificar_instalacion.py` probaba UN layout. Construía el wheel, lo instalaba en un venv, corría un
proyecto con `escalares.py` que importa la fachada, y salía WHEEL OK. Un verde que no significaba
nada, en la herramienta que existe para decir que el paquete está bien — el defecto que este
repositorio cataloga 90 veces, cometido en su propio arnés.

Ahora prueba los dos. Y el chequeo nuevo mide algo: con el defecto puesto de vuelta A PROPÓSITO, el
verificador sale 1 con el `ModuleNotFoundError` exacto.

## Dos arreglos descartados

El que propuso quien encontró el defecto era `RAIZ_ORACLE.parent`. En el repo eso es el directorio
que CONTIENE a Oracle —`~/Dev`— y meterlo en el camino de un subproceso que existe para CONFINAR una
UDF ajena es exactamente lo contrario de lo que ese módulo hace.

El segundo intento, derivarlo de `__package__`, parecía preciso y está mal por algo que no se ve
leyendo el archivo: `oracle_metalenguaje/__init__.py` aliasa `nucleo` como paquete de nivel
superior, así que ese mismo archivo termina importado DOS VECES bajo dos nombres, como dos objetos
distintos. El que usa `nucleo/proyecto.py` se llama `nucleo.aislamiento.escalares`, y desde ese
nombre el layout del wheel es invisible: el cálculo daba el valor correcto en la copia equivocada.

Lo que queda es preguntarle al importador, que no depende de cómo se importó nada. En el repo no
agrega ninguna entrada.

## De paso

Una medida del propio proyecto rechazó la primera versión: `test_la_distribucion_productiva_no_
nombra_consumidores_conocidos` tumbó un comentario que nombraba un consumidor particular. La
distribución no conoce dominios, tampoco en sus comentarios.

Y los dos mutantes que sobrevivieron al primer intento sobrevivían por la misma razón que el defecto
existía: en el repo las dos raíces coinciden, así que ningún test que corra sólo acá puede
distinguir el cálculo correcto de uno que devuelve `RAIZ_ORACLE` siempre. Los cierra un test que
simula el layout instalado.

DECISIÓN 010 lo deja escrito como clase, no como caso. VERSION_DISTRIBUCION 0.3.1 → 0.3.2.

Verificado: 1025 tests · corpus 161 · aceptación en los 2 rojos declarados · mutar.py 703/703 ·
nucleo/aislamiento/escalares.py 133/133 · trazar OK · WHEEL OK con los dos layouts · y el escenario
del consumidor contra el artefacto final de 0.3.2.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3dXE49okVZk7VkgSkwxKe

## 2026-09-02 — Importar la biblioteca le borraba un paquete al que la importa

*commit 398cd18*

Segundo defecto encontrado desde afuera del repositorio, un día después del primero y de la misma
familia: el paquete instalado se comporta distinto del checkout, y el arnés miraba el checkout.

Importar `oracle_metalenguaje` registraba en `sys.modules` cuatro nombres de NIVEL SUPERIOR
—`nucleo`, `catalogos`, `perfiles` y `tools`— para que los imports absolutos del núcleo funcionen en
los dos layouts. `tools` es el nombre de paquete más común que hay en un repositorio: un consumidor
con su propio `tools/` lo perdía POR IMPORTAR LA BIBLIOTECA, y moría con
`ModuleNotFoundError: No module named 'tools.referencias'` sobre un paquete suyo que existía y no se
había movido.

El verificador afirmaba lo contrario, y era verdad diciendo una mentira:

    for nombre in ("nucleo", "catalogos", "perfiles", "tools"):
        assert importlib.util.find_spec(nombre) is None, nombre

Eso mira el DISCO y corre ANTES de importar nada. El wheel no ocupa esos nombres como archivos: los
ocupa al importarse. Segundo verificador que pasa mientras la cosa está rota, en dos días.

El alias de `tools` se mudó de la fachada al propio paquete `tools/`. Los módulos de `tools/` se
importan entre sí por nombre absoluto, y eso ocurre cuando corre un entry point de Oracle —su
proceso, donde ocupar el nombre no le saca nada a nadie—. Un consumidor que sólo usa `Motor` o
`escalar` ya no lo ve. Sigue siendo `setdefault` y no asignación: el que llegó primero gana.

El verificador ahora crea un consumidor con su propio `tools/`, importa la biblioteca y exige que el
paquete siga siendo el suyo. Se comprobó que mide algo poniendo el defecto de vuelta a propósito:
falla con el `ModuleNotFoundError` exacto.

Lo que NO se arregla, y queda escrito:

  · `nucleo`, `catalogos` y `perfiles` se siguen ocupando. El núcleo se importa a sí mismo por
    nombre absoluto y sacarlos es reescribir todos sus imports. Son palabras en español y la
    colisión es menos probable, no imposible;
  · `objetivos_disponibles()` excluye todo `__init__.py`, así que la fachada —justo donde estaba el
    defecto— no la muta nadie. La exclusión tiene una razón buena, porque casi todos están vacíos,
    pero la consecuencia es que estos dos los fijan tests que leen el código como TEXTO. Es más
    débil y hay que saberlo.

Lo que sí queda fijado por un test es la condición que hace seguro haber sacado `tools`: ningún
módulo de `nucleo/` lo importa. Si mañana alguno lo hace, ese test se rompe.

VERSION_DISTRIBUCION 0.3.2 → 0.3.3. El álgebra y la sintaxis no se movieron.

Verificado: 1029 tests · corpus 161 · aceptación en los 2 rojos declarados · mutar.py 703/703 ·
WHEEL OK con los dos layouts y con el consumidor que tiene su propio `tools/`.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-02 — Una sombra que nadie envejece deja de ser una transición

*commit df4a2a9*

`dias` viajaba en la relación `sombra` desde que existe el modo sombra, y NINGUNA medida lo miraba.
Una sombra de 244 días pasaba en verde. Lo único que distingue una sombra de apagar la medida es que
alguien la vaya a sacar, y eso era exactamente lo que nada comprobaba.

`meta.ninguna_sombra_envejece_sin_revisarse` la encuentra a los noventa días. El número es `segun
convencion` y el `porque` lo dice sin adornos: un trimestre es tiempo de sobra para el arreglo que se
pospuso y poco para que el proyecto se acostumbre a no ver la medida. Lo eligió el equipo, no salió
de medir nada, y cambiarlo es una decisión y no la corrección de un error.

Buscándole los bordes apareció un segundo agujero, y es de los que dejan a algo invisible para TODAS
las medidas a la vez: `meta.toda_sombra_declara_desde_y_porque` sólo comprueba que el campo no esté
vacío, así que «cuando pueda» lo pasa con `declara_desde` en true. El marco no puede fecharla y
devuelve días negativos — y una sombra con días negativos tampoco la encuentra la medida que
envejece, porque -1 no es mayor que 90. Sin fecha legible no hay edad, y sin edad no hay quien la
saque nunca.

`meta.toda_sombra_declara_una_fecha_real` cubre eso con un solo predicado, `dias < 0`, que atrapa las
dos formas de no tener edad: la fecha que no se puede leer y la que todavía no llegó. Su alcance dice
que NO las distingue.

Seis casos. El rojo de la que envejece tiene exactamente UNA fila que ofende, porque con dos aflojar
el umbral de cero a uno sigue dando rojo y el mutante pasa inadvertido; y una fila de exactamente 90
días, que fija que el límite es estricto. Dos son de evidencia OBSERVADA de una corrida real con tres
sombras declaradas —291 días, 13 días y una fecha ilegible—, así que el rojo declarado de la
DECISIÓN 004 sigue en 2 y no sube a 4.

Llega justo a tiempo: los dos consumidores acaban de declarar seis sombras entre los dos, con fecha
de ayer. Son las primeras que van a envejecer de verdad.

Verificado: 1029 tests · corpus 167 casos · aceptación en los 2 rojos declarados · mutar.py 715/715
sin sobrevivientes · cifras al día.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-02 — Los mutadores tenían un solo autor, y eso el número no lo podía decir

*commit 8e0eb22*

`tools/mutar.py` decía 715/715 muertos. Ese número medía cobertura sobre CINCO mutadores escritos
por la misma persona que escribió las medidas y el corpus. El problema no se ve desde adentro y no
lo arregla escribir más casos: un mutador que nadie escribió no puede producir un sobreviviente.

Se repitió el protocolo que ya había funcionado para el evaluador de referencia del diferencial: otro
autor, en aislamiento verificable. Un directorio con EXACTAMENTE dos archivos —la especificación y un
contrato que define qué es un mutador—, sin ver `nucleo/mutacion.py`, ni el catálogo, ni un caso del
corpus, ni los tests. A la copia de la especificación se le quitó UN párrafo, el que enumera qué
sitios muta la implementación existente; la redacción está declarada y el lugar lleva una nota.

No se le creyó la declaración: se auditó su registro de comandos. Corrió tres, los tres con ese
directorio como raíz, sin una ruta hacia afuera.

Escribió 24 mutadores. Sobre el catálogo real: 179 mutantes aplicables, 142 muertos (79%), 37
sobrevivientes. De esos, 6 los rechazó el álgebra —no prueban nada— y quedaron 31.

TRES ERAN HUECOS REALES, y en medidas escritas ese mismo día. Sus docstrings los habían predicho sin
ver nada: «omite casos cercanos al límite si el corpus sólo contiene anomalías grandes». Era exacto:
los casos tenían 4 palabras contra 22, y 244 días contra 90 — anomalías grandes y ningún testigo EN
el límite. Se cerraron con dos casos al borde: uno de 5 palabras y uno de 91 días.

VEINTIOCHO ERAN UN MUTANTE EQUIVALENTE, y casi los reporto como hallazgo. `convertir_conteo_en_
existencia` cambia `contar` por `max(1)`; con `umbral <= 0` —el de las 54 medidas del catálogo—
«contar al menos una» y «existe alguna» son la misma afirmación. Queda excluido con la razón escrita
en el código, no en un comentario suelto.

DIECISIETE NO APLICARON A NINGUNA MEDIDA, y eso también es un dato: cotas inferiores, agregados
max/min/promedio, agrupamientos, productos. Las 54 medidas tienen todas la misma forma. El arnés
tiene menos poder sobre este catálogo del que el número sugiere, y no por un defecto suyo.

La certificación de la biblioteca de ejemplo se rompió al pasar de 5 mutadores a 28: publicaba 12 y
el arnés mide 16. Es correcto —una biblioteca certificada contra 5 no lo está contra 28— así que se
volvió a medir y se republicó el número. No se aflojó el chequeo.

Dos timeouts en la ronda de código, arreglados distinto porque son cosas distintas: uno era un
mutante indistinguible por conducta y se mató fijando el tipo de retorno en los tests prioritarios
—aflojar el plazo ahí habría tapado que faltaba un test—; el otro era la línea base, que ya no entra
en 60 s con 1.033 tests. Ése sí es presupuesto y queda medido: 50,5 contra 60.

No se descartó ningún mutador «que no valiera». La única exclusión es la equivalencia demostrada.
Elegir el denominador después de ver el resultado habría sido el sastreo que este proyecto persigue.

Verificado: 1033 tests · corpus 169 casos · aceptación en los 2 rojos declarados · mutar.py 846/846
con el denominador nuevo · nucleo/mutacion.py 157/157 · trazar OK · cifras al día.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-02 — `oracle contexto`: lo que hace falta para escribir una medida, en un solo lugar

*commit 48b04bd*

Quien va a escribir una medida —una persona o un agente— necesita cuatro cosas: qué relaciones hay y
con qué campos, con qué se escriben, qué declara toda medida sin excepción, y cuáles ya existen para
no repetirlas. Eso se averiguaba corriendo tres comandos y leyendo dos documentos, y el que no sabe
que existen no los corre.

No es un documento nuevo: es una VISTA, igual que el manual. Para que lo sea de verdad hubo que
separar la derivación de la impresión — `inventario_de_relaciones()` devuelve los datos y
`oracle relaciones` los imprime, así que las dos vistas usan la misma derivación en vez de derivar
dos veces. Los orígenes del umbral y los operadores salen de `nucleo/vocabulario.py`, no copiados.

## El ahorro, medido

    los tres comandos por separado   34.407 caracteres  (~8.601 tokens)
    oracle contexto                  20.885             (~5.221)
    oracle contexto --compacto        6.426             (~1.606)

5,4 veces menos, y diciendo dos cosas que ninguno de los tres decía: qué declara toda medida, y que
el caso va antes que la medida.

Vale anotar la conclusión porque contradice una intuición razonable: se había considerado cambiar el
formato de serialización —TOON en vez de JSON— para ahorrar contexto. **El ahorro vino de elegir qué
incluir, no de una serialización más densa.** Cambiar el formato habría atacado los 20.885
caracteres; elegir qué mostrar los bajó a 6.426 sin tocar el formato.

Un test exige que el compacto no pierda NINGUNA relación ni NINGUNA medida: apretar no puede ser
recortar.

## Una mentira vieja, de paso

`oracle escalares` imprimía a mano `OPERADORES: de · donde · unir · resumen (con y agrupar todavía
no tienen usuario)`. Hacía rato que era falso —los dos tienen usuario— y nada lo comparaba con nada.
Ahora sale del mismo registro que el manual.

## Lo que NO se hizo, con su razón

`tools/contexto.py` no entra al perfil de mutación. Por el criterio del proyecto, un instrumento
entra sólo cuando custodia una afirmación que nadie más comprueba, y éste no: si se rompe, nadie se
pone verde por eso — alguien recibe información incompleta y escribe una medida peor, pero ninguna
medida pasa que no debería.

Al mutar `tools/medida.py` aparecieron sobrevivientes en su código de impresión. Se midió `HEAD` en
un worktree aparte para saber si los había traído este cambio: **son los mismos sitios, corridos por
el offset del refactor**, así que ya estaban. Las dos corridas se cortaron antes del resumen, así que
no hay un total — la comparación sitio por sitio sí alcanza para la pregunta que importaba. Es deuda
previa en el formateo de la salida, y queda dicha en vez de tapada.

Verificado: 1045 tests · aceptación en los 2 rojos declarados · WHEEL OK · cifras al día.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-02 — «Sube el costo por corrida» no se puede discutir sin el número

*commit c4b9581*

`HERRAMIENTAS_CUSTODIAS` tiene siete archivos de `tools/`. La matriz de mutación de código del
workflow corre UNO. Los otros seis entran al perfil y no los muta nadie salvo a mano, lo cual estaba
declarado —«agregarlos sube el costo por corrida, y con la cuenta en cero no es el momento»— sin
decir cuánto.

Se midió `tools/medida.py` entero: 264 mutantes, 114 sobrevivientes, 43%.

El reparto es lo que importa y da vuelta la conclusión fácil. Las funciones que CUSTODIAN una
afirmación —`ejercicio_del_catalogo`, `texto_de_fijacion`, `esta_ejercitada`, de donde el editor
saca «esta medida está ejercitada»— tienen CERO sobrevivientes de 45. Los 114 caen enteros en el
CLI: `main` 26, `revisar` 24, `listar` 20, `probar` 20 y el resto de la presentación.

Así que el archivo no está roto donde el criterio lo justifica: está mezclado. El criterio se aplica
por INSTRUMENTO y la mutación se aplica por ARCHIVO, y acá los dos no coinciden. Queda escrito con
las tres formas de arreglarlo y por qué ninguna es obvia.

Y el costo quedó explicado, no sólo medido: mutar ese archivo tarda ~90 minutos y NO porque sea
grande. Un mutante que muere cuesta ~0,1 s; uno que sobrevive cuesta la suite entera, ~50 s. El
archivo es lento PORQUE está mal fijado. Eso invierte el argumento: «no los agregamos porque salen
caros» dice lo mismo que «no los medimos porque nos iría mal».

Cómo se supo que los 114 son deuda vieja y no de esta semana: se corrió la misma ronda sobre
`8e0eb22`, el commit anterior al que tocó el archivo. Antes 264 mutantes con 114 vivos; ahora 265 con
114. El cambio agregó un mutante y ese muere.

Se falló dos veces antes de medirlo bien, y las dos habrían dado la conclusión correcta por
casualidad: la primera comparación usaba salidas truncadas por un `head -8` —seis sitios de 264— y
la segunda creó el worktree desde HEAD, que ya incluía el cambio, comparando el archivo consigo
mismo.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-03 — El costo era el síntoma: `tools/medida.py` pasa de 90 minutos a 206 segundos

*commit 3f4a1b7*

Ayer quedó medido que `tools/medida.py` tenía 114 mutantes sobrevivientes de 264 y tardaba ~90
minutos, y que por eso no estaba en la matriz de CI aunque figurara en HERRAMIENTAS_CUSTODIAS. Se
escribieron tres formas de arreglarlo sin saber cuál era mejor, así que se probaron dos en ramas
separadas, con los criterios de comparación fijados POR ESCRITO antes de ver un solo resultado.

  · escribir los tests que faltaban → 264/264, cero sobrevivientes, 201 s;
  · separar el archivo, dejando el CLI afuera del perfil → 3 sobrevivientes de 64, 1.675 s, ocho
    veces más lento, con 114 mutantes sin medir.

Ganó escribir los tests, en los cinco criterios medibles. Entra eso.

EL DATO QUE DA VUELTA LA INTUICIÓN es el tiempo. El archivo tardaba noventa minutos PORQUE estaba
mal fijado: confirmar un sobreviviente cuesta una corrida completa de la suite (~50 s) y matarlo
cuesta ~0,1 s. Fijarlo lo volvió veintisiete veces más rápido. Así que «no los agregamos a CI porque
salen caros» decía en realidad «no los medimos porque nos iría mal» — medirlos bien es exactamente
lo que los vuelve baratos.

Yo había recomendado separar, con el argumento de que el módulo custodio se mutaría en segundos.
Era falso: tardó veintiocho minutos. Y la mitad del razonamiento que SÍ era cierta —que el costo es
un síntoma— no le creí lo suficiente como para sacar la conclusión correcta.

Viene también un arreglo que no era parte del encargo y vale igual: `test_diagnostico` escribía en
`Path.home()` y reventaba con un home de sólo lectura. Yo había visto esa falla dos veces y la
descarté las dos como «artefacto del sandbox» del agente que la reportaba. No era del sandbox: era
del test, que exigía escribir en el home real para comprobar una redacción de texto. Ahora simula
`Path.home` en vez de escribir ahí.

El único equivalente declarado está demostrado, no invocado: el default de `getattr(e, "linea", 1)`
cambia de 1 a 2 y el cálculo posterior es `max(1, N - 12)`, que vale 1 en los dos casos.

Queda abierto y escrito: los otros cinco archivos de HERRAMIENTAS_CUSTODIAS —`aceptacion.py`,
`cli.py`, `corpus.py`, `lsp.py`, `manual.py`— siguen sin medirse en CI y nadie sabe sus números. Si
el patrón se repite, están caros por el mismo motivo.

Verificado en main: 1072 tests · `tools/medida.py` 264/264 en 206 s · aceptación en los 2 rojos
declarados · cifras al día.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-03 — Los cinco custodiados sin medir estaban en cero, salvo el que yo había tocado

*commit dd92093*

Se midieron los cinco archivos de HERRAMIENTAS_CUSTODIAS que no están en la matriz de CI, esperando
encontrar deuda como la de `medida.py`. Cuatro estaban en cero:

  tools/lsp.py          140 mutantes ·  0 vivos ·   121 s
  tools/corpus.py       112 mutantes ·  0 vivos ·   180 s
  tools/aceptacion.py    49 mutantes ·  0 vivos ·   266 s
  tools/cli.py          442 mutantes ·  0 vivos ·  1927 s
  tools/manual.py        59 mutantes ·  3 vivos ·   242 s

No eran archivos abandonados: estaban fijados y nadie volvía a comprobarlo. `medida.py` era la
excepción y no la regla, así que la deuda que se buscaba no existía.

LOS TRES DE `manual.py` LOS INTRODUJE YO. Cuando agregué `--man` lo medí en 39/39, seguí editándolo
—la página del sitio, el instalador, el reordenado de imports—, pasó a 59 mutantes, y nunca lo volví
a medir. Es exactamente el modo de fallar que este proyecto persigue, cometido adentro: medir una
vez, seguir tocando, y quedarse con el número viejo en la cabeza. Sólo apareció porque se midieron
los cinco.

Los tres tenían la misma raíz, y no era código sin probar sino CASOS QUE NO DISTINGUÍAN:

  · `partes[1::2]` y `partes[2::2]`: el test usaba UN solo par de comillas invertidas, y con un par
    el paso de dos y el de tres toman el mismo elemento. Se cierran con una prosa de dos pares —que
    es además el caso real: una explicación que nombra dos campos— y otra de tres, que fija que no
    se pierda el texto posterior al último código;
  · `parents=True`: el test instalaba en un temporal cuyo padre YA existía. Se cierra instalando en
    una rama inexistente, que es el caso real: nadie crea `~/.local/share/man` a mano.

Los tres casos nuevos son MÁS realistas que los que reemplazan, no más rebuscados — señal de que los
viejos probaban la implementación en vez del contrato.

Y la hipótesis con la que se arrancó la medición se cayó entera. Se había escrito: «si el patrón se
repite, están caros porque están mal fijados». Están todos bien fijados y `cli.py` igual tarda 32
minutos. El costo tiene DOS componentes y sólo se había visto uno: además de confirmar
sobrevivientes (~50 s cada uno), está lo que tarda el arnés en LLEGAR al test que mata al mutante.
Con `failfast=True` y los módulos en el orden declarado, `lsp.py` va a 0,86 s por mutante —declara
un módulo, chico y suyo— y `aceptacion.py` a 5,4 —declara `herramientas` primero, que es grande—.

De ahí sale una palanca que no cuesta código: reordenar los prioritarios poniendo el más específico
primero. Queda anotada sin medir, y dicho que no se midió.

Verificado: 1075 tests · `tools/manual.py` 59/59 · corpus 169 · aceptación en los 2 rojos
declarados · cifras al día.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-03 — El manual cubre las 54 medidas que Oracle trae, sin escribir prosa nueva

*commit c4a5ffa*

Cada medida universal ya declaraba qué NO ve. Documentarlas no costaba redactar: costaba mostrar lo
que ya estaba, y por eso el tema sale del catálogo cargado y no de una lista al lado — una medida
nueva aparece sola, en la terminal, en el sitio y en `man oracle-medidas`.

Se muestra el `alcance` y NO el `porque`, y la diferencia importa: el `porque` justifica el número
ante quien lo discute, el `alcance` dice qué no cubre. Lo segundo es lo único que evita confiar de
más en un verde que uno no escribió, que es la situación de quien lee una medida ajena.

El tema NO entra como vocabulario cerrado. Si entrara, sus 54 entradas caerían en la relación
`opcion_del_vocabulario` y las dos medidas que vigilan el manual pasarían a medir otra cosa, además
de dejar mintiendo a los casos observados que las fijan. Va como tema derivado, igual que `verbos`.

De paso, un arreglo general que este tema destapó: con nombres de más de cincuenta caracteres —los
ids de medida— la columna alineada se comía dos tercios del renglón y la explicación quedaba en una
tira de veinte. Pasado un tercio del ancho, la prosa baja a la línea siguiente. El umbral queda
declarado como ELEGIDO y no medido, con la nota de que si alguna vez se mide se cambie con el número.

Tres mutantes sobrevivieron al primer intento, los tres míos y los tres de la misma forma:
aserciones que miran menos de lo que el código hace.

  · `return {}` en la rama del `except`: el test mockeaba la función ENTERA, así que esa rama no se
    ejercitaba nunca. Es el mismo mutante que apareció hace unas horas en `nucleo/mutacion.py`,
    tapado por un mock de más alto nivel — segunda vez en el día;
  · `" " * 6`: la aserción usaba `.strip()`, y con strip cualquier sangría pasa igual;
  · `ancho - 6`: la prosa del test era corta, y con texto corto cualquier ancho parecido da lo mismo.

El caso del borde se construyó mal la primera vez: creí que noventa caracteres exactos NO entraban, y
entran. El test correcto afirma DOS líneas y es el mutante el que las parte en tres.

Verificado: 1084 tests · `tools/manual.py` 74/74 · corpus 169 · aceptación en los 2 rojos declarados
· mutar.py salida 0 · cifras al día · `docs/manual.html` regenerado.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-03 — La documentación cuenta lo que el proyecto hace hoy, y dice mejor lo que le falta

*commit 1fe8b30*

Dos revisiones en paralelo y sin solapamiento: el README por un lado, `docs/` y las dos guías por
otro. A los dos se les dieron las mismas reglas duras —nada de números ni salidas inventadas, no
tocar los cinco bloques que genera `cifras.py`, y verificar con los verificadores del proyecto en
vez de a ojo— y las dos entregas se comprobaron acá antes de entrar.

El README pasa de 768 a 719 líneas. Incorpora `oracle contexto`, el manual de medidas, el
envejecimiento de sombras, los dos consumidores de PyPI y las DECISIONES 010 y 011. La autocrítica
de la proporción NO se borró: se condensó de cinco párrafos a seis líneas que dicen lo mismo —el
defecto estructural, las tres auditorías en contra, la reinterpretación publicada, y que se publica
como costo y no como criterio de cierre—. El cartel de EXPERIMENTAL sigue.

Y su sección «Qué falta» quedó mejor de lo que estaba, con tres cosas que no habíamos escrito:

  · el próximo límite de L2 — ningún consumidor escribió todavía una medida meta que necesite una
    relación nueva, así que no se sabe si la reificación alcanza fuera de las preguntas de este autor;
  · la fachada sigue ocupando `nucleo`, `catalogos` y `perfiles`, y los dos `__init__.py` que tienen
    conducta están excluidos de la mutación junto con los vacíos;
  · **no hay alarma que reincorpore `convertir_conteo_en_existencia`** si algún día entra un umbral
    distinto de `<= 0`. Ese riesgo estaba escrito en la DECISIÓN 011 y quedó sin mecanismo: es la
    misma cosa que «el catálogo tiene una sola forma», vista desde el otro lado.

`docs/05-por-que-la-mutacion.md` era el que más había envejecido por debajo: contaba la mutación
como si el conjunto de mutadores fuera uno solo. Ahora cuenta los dos autores, el aislamiento
auditado y los números de la primera corrida del segundo conjunto.

Un hallazgo que salió de la revisión y se verificó: correr el comando INSTALADO parado en el repo de
Oracle falla con «el id está dos veces», porque el proyecto declara `catalogo_base: true` y se cargan
el catálogo del paquete y el del árbol local. No es un defecto del mecanismo —la detección de ids
duplicados hace lo que debe— pero es una trampa: el error parece del catálogo y es del entorno.
Queda anotado, sin arreglar.

Verificado: `sintaxis.py --verificar` salida 0 con los 21 bloques de documentación en regla ·
`cifras.py` salida 0 · 1084 tests.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-03 — 0.4.0

*commit f5e8f6c*

Ocho commits desde 0.3.3. El álgebra y la sintaxis no se movieron —no hay operadores nuevos ni
cambió cómo se escribe una medida— así que sólo sube la distribución. Unificar las tres versiones
mentiría sobre qué cambió.

Lo que trae, en una línea cada cosa:

  · los mutadores dejan de tener un solo autor: un segundo, en aislamiento auditado, escribió 24 sin
    ver el repositorio y encontró tres huecos reales que el conjunto propio no podía encontrar;
  · la sombra envejece — `dias` viajaba en la relación desde siempre y ninguna medida lo miraba;
  · `oracle contexto`, que junta lo que hace falta para escribir una medida y en `--compacto` cuesta
    ~1.600 tokens contra ~8.600 de los tres comandos que reemplaza;
  · el manual cubre las 54 medidas universales, sin escribir prosa nueva;
  · `tools/medida.py` pasa de 114 sobrevivientes y 90 minutos a 264/264 en 206 segundos, y entra a
    la matriz de CI;
  · la documentación cuenta lo que el proyecto hace hoy.

Las notas llevan primero lo que le cambia el número a quien ya usa Oracle, porque es lo que se lee
tarde y duele: un proyecto con `catalogo_base` hereda DOS medidas nuevas y puede ponerse rojo si
tiene sombras viejas, y toda biblioteca de políticas publicada pierde su certificación porque el
arnés pasó de 5 mutadores a 28.

Y llevan siete límites conocidos, no tres. Los dos que más pesan son nuevos y salieron de esta
versión: el catálogo tiene UNA sola forma —las 54 medidas comparan con `<= 0`, por eso 17 de los 24
mutadores del segundo autor no aplicaron a ninguna— y no hay alarma que reincorpore el mutador
excluido por equivalencia si algún día entra un umbral distinto.

Verificado: 1084 tests · corpus 169 · aceptación en los 2 rojos declarados con el número que el
workflow exige · mutar.py 846/846 · trazar OK · sintaxis --verificar OK · cifras al día · WHEEL OK.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-03 — Una exclusión de mutador ya no vale para todo el catálogo, y el ámbito empieza a existir

*commit 20a679d*

La alarma que escribí para vigilar la premisa de una exclusión encontró primero un
defecto en sí misma, y después otro más grande.

El primero: `_mutadores_ajenos()` aplicaba la exclusión EN TIEMPO DE IMPORTACIÓN, sin
consultar nunca el predicado. La alarma podía ponerse roja y el arnés seguía haciendo
exactamente lo que ella denunciaba. Ahora la exclusión se comprueba por medida, en
`mutantes()`. No movió ningún número en los tres catálogos —era lo esperado— pero
destapó cobertura escondida: la biblioteca de ejemplo publicaba 16 mutantes
certificados cuando eran 17. El mutador nunca había corrido sobre su medida de
`umbral <= 5`.

El segundo: con la exclusión por medida, la premisa pasó a ser verdadera por
construcción. Una medida que no puede dar rojo no mide nada, así que la alarma cambia
de blanco y vigila lo que sí puede volver a romperse: que nadie regrese al filtrado
global. Y ahí apareció el error de verdad, que el test del wheel encontró: `mutadores/`
no viaja en el paquete, así que en un consumidor el mutador falta y la primera versión
lo llamaba «exclusión global». Era la misma falla de antes mudada de lugar — una medida
sobre el arnés de Oracle poniendo en rojo a quien instalara el paquete.

Hay dos maneras de que un mutador no esté en el registro y sólo una es un defecto. Los
hechos viajan separados y el `donde` los cruza; colapsarlos metía el juicio en Python.
`mutadores_declarados_por_sus_autores()` lee el módulo del autor y no el registro ya
construido: si saliera de ahí, un filtro reintroducido desaparecería de los dos lados y
la medida daría verde mientras el arnés vuelve a la forma vieja.

El caso 471 fija esa diferencia. Sin él, borrar `lo_ofrece_un_autor == true` no rompe
ningún otro caso: 468 ofende igual, 469 y 470 siguen verdes.

Jam quedó en ACEPTACIÓN ✓, sin el rojo que no podía arreglar en su propio repo.

Además, la capa 1 del ámbito (PLAN-0.5.0-AMBITO.md): `ambito` es vocabulario cerrado,
campo de `Medida`, se lee y escribe en las dos superficies y se reifica. Las 55 medidas
quedan en `sin_declarar` a propósito — un valor `universal` por omisión reproduciría en
verde la fuga que el plan cierra.

Y el `dt` del manual: 56 de 90 términos se dibujaban encima de su definición. El guión
bajo no es punto de corte en CSS.

  suite 1109 · corpus 173 casos · aceptación 2 rojos declarados
  mutación de medidas 860/860 · marco 58/58 · mutacion 169/169
  aceptacion 49/49 · sintaxis 986/986 · medida 246/246 · manual 75/75

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-04 — Una medida declara dónde obliga, y «empaquetada» deja de significar «universal»

*commit b08b4b5*

Jam venía evaluando si el manual de Oracle estaba completo. Dicho así se cae solo,
pero el mecanismo que lo permitía era invisible: «universal» significaba una sola cosa
—vivir en el directorio del paquete— y eso es PROCEDENCIA, no ÁMBITO. Coincidieron
mientras todo lo empaquetado obligaba a todos.

Ahora una medida declara `ambito universal | del_origen`, relativo al ORIGEN y no a
Oracle: en el catálogo base significa de Oracle, en una medida de Jam significa de Jam
y se satisface sola, en una biblioteca significa de su publicador. El lenguaje no le da
un privilegio nominal a nadie.

El orden de las preguntas quedó explícito en la carga:

    selección del catálogo → ámbito → aplicabilidad → evaluación

Poder calcular un veredicto no vuelve pertinente ese veredicto. Ése era el hueco:
`catalogo_base` contestaba de dónde vino la medida y `medidas_aplicables` si podía
calcularse; nadie contestaba a quién obliga.

No es un nivel nuevo. Medido: 56 medidas, 56 filas en la relación `medida`, y la que
juzga el alcance está entre las filas que juzga. L2 es un punto fijo y el ámbito entra
como campo de una representación que ya existe. Nivel y ámbito son dos ejes.

Tampoco es visibilidad: sin composición de medidas (DECISION-002) no hay llamadas que
prohibir. La analogía es la jurisdicción de una regla — todos pueden leerla, sólo dicta
veredicto donde hay responsabilidad para responderla. Una medida `del_origen` sigue en
el manual, reificada, mutando y con corpus.

El costo: `ambito` es parámetro obligatorio de las cuatro macros. Una invocación
anterior conserva la ausencia como `sin_declarar` —el mismo camino que se abrió al
agregar `segun`, y por el mismo motivo: no se inventa un valor, se registra que el autor
no eligió—. Sin eso, agregar el parámetro dejaba de cargar el catálogo entero de un
consumidor: se probó, y Jam pasaba de 25 medidas a cero.

Tres mutantes sobrevivieron en ese camino de compatibilidad, todos míos y todos del
mismo tipo: guardas que parecen prudentes y no cargan peso. Una constante que un filtro
volvía irrelevante, una comparación cuyo caso cero era un no-op, y una rama que
`de_datos` vuelve inalcanzable. Ninguna rompía nada; las tres habrían quedado ahí.

  ámbito: 37 universales · 19 del origen
  Jam: 25 → 20 medidas, exactamente las cinco sobre las que no tenía remedio
  LyraGASP: sin cambios
  suite 1122 · corpus 176 casos · aceptación 2 rojos declarados
  mutación de medidas 868/868 · macro 117/117 · sintaxis 991/991
  proyecto 143/143 · medida 249/249

Falta la cota —una medida no puede declarar un ámbito más amplio que sus dependencias—,
que necesita reificar `dependencia_de_medida`.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

## 2026-09-04 — La cota del ámbito, y dos criterios que coincidieron sin consultarse

*commit ac83a04*

`DECISION-012` deja una declaración humana —`ambito universal | del_origen`— y
prometía volverla falsable hasta donde se pueda. Ésta es esa parte: una medida no
puede obligar a más proyectos que aquellos donde su evidencia tiene dueño. Si se
declara universal pero consume una relación que describe la instalación del origen,
su rojo sólo lo puede arreglar el origen, y declararla universal se lo manda a un
consumidor que no tiene remedio.

No hizo falta la relación nueva que el estudio proponía como pieza central. `unir`
anidado funciona, así que la cota cruza tres relaciones en álgebra pura —medida,
dependencia_de_medida y ambito_de_relacion— sin denormalizar ni meter el juicio en
Python. En la superficie infija lee como tres líneas seguidas de `unir`.

Sí entró `dependencia_de_medida`, pero no porque faltara información: `fuente` y
`requiere` ya decían esto por separado. Sin ella la cota serían dos políticas casi
iguales y nada las mantendría iguales — el mismo argumento que produjo la macro `peor`.
`clase` conserva la vía porque las dos no son lo mismo: una fuente trae filas, y
`requiere` es la precondición que hace SIN EVIDENCIA.

No usa la macro `ninguno`: cruza tres relaciones y la macro admite una sola fuente.
Queda dicho en el `porque`, que es donde alguien lo va a buscar antes de "arreglarlo".

El caso 478 registra algo que no se buscaba. Hay 13 dependencias reales sobre
relaciones `del_origen` y las 13 salen de medidas ya declaradas `del_origen`. La
clasificación se hizo preguntando quién tiene el remedio; la cota deriva lo mismo desde
las relaciones que cada medida consume. Dos criterios independientes, la misma respuesta
sobre 55 medidas. No prueba que la clasificación sea correcta: prueba que no se
contradice consigo misma, que es lo único que una medida puede comprobar.

Y el 477 ofende por `requiere` y no por `fuente`, que es lo que fija que la cota mira
las dos vías; sin él, `dependencia_de_medida` no tendría por qué existir.

Además, tres `and` de la lectura de ámbitos quedaron fijados con la entrada que los
separa de un `or` — el symlink es el más interesante: leerlo sería aceptar una
declaración de jurisdicción que no vive en el proyecto. Y la guarda de sección vacía
del manual, cuyo `return` sobrevivía: es la quinta vez en esta sesión que el mismo
patrón aparece, y esta vez el archivo YA tenía un test que explicaba la lección — pero
comprobaba la lista vacía sin dibujar la sección.

  suite 1127 · corpus 180 casos · aceptación 2 rojos declarados
  relacion 94/94 · medida 250/250 · unidad 198/198 · manual 78/78
  tools/medida 264/264 · referente, diagnostico y aceptacion limpios
  Jam ✓ · LyraGASP ✓

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>

---

<!-- fuente: 08-los-numeros.md -->

## Los números, y qué dicen

| Qué | Cuánto | Qué dice |
|---|---|---|
| líneas del núcleo | 9071 | el lenguaje |
| líneas de medidas escritas en él | 406 | lo escrito en el lenguaje |
| proporción | 22 a 1 | la apuesta: que el segundo crezca y el primero no |
| (contando sólo el catálogo base) | 24 a 1 | sin ningún proyecto que lo use |
| negativas en el núcleo (`raise`) | 373 | su naturaleza es rechazar, no medir |
| medidas | 57 | de las cuales 44 miden el lenguaje mismo |
| casos de corpus | 180 | fallas reales, con su evidencia |
| commits | 323 | el historial completo |

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
