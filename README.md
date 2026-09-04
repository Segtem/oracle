# oracle

[**segtem.github.io/oracle**](https://segtem.github.io/oracle/) · [PyPI](https://pypi.org/project/oracle-metalenguaje/) · [0.3.3](https://github.com/Segtem/oracle/releases/tag/v0.3.3)

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

## Instalación

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

### Desde el repositorio

Para trabajar sobre el checkout —o para tomar algo que todavía no salió en un release—:

```bash
uv tool install .          # o: python -m pip install -e .
uvx --from . oracle --help # probarlo sin instalar nada
```

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
En este corte hay 9582 líneas de lenguaje y **395 negativas explícitas** (`raise`).
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
Los 99 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 73 la mutación, 18 una persona, 4 la casualidad, 4 una herramienta ajena.
<!-- deteccion:fin -->

Ninguna de esas vías le pregunta al que escribió el código. Oracle no es un juez de artefactos — es
una prótesis para alguien que escribe la herramienta y su test con la misma mano y no recuerda ayer.

### El costo, dicho

<!-- escala:inicio -->
**9582 líneas de lenguaje** (`nucleo/`, código y macros) y **395 negativas explícitas** (`raise`). Contra las 56 medidas universales escritas en él (397 líneas): **24,1 a 1**. 50 de las 56 pasan por una macro.
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

### La proporción no alcanza como criterio, y el proyecto es EXPERIMENTAL

Dos auditorías externas la hicieron disparar en contra tres cortes seguidos —16,2 → 18,0 → 18,2— y
la respuesta publicada fue reinterpretarla. El defecto es estructural: los catálogos externos no
entran al denominador, así que la adopción no la mueve; y migrar una política real de Python al
catálogo bajó el núcleo tres líneas sin mover la cifra.

Por eso se publica como **costo**, no como criterio de cierre. Sigue generada por `tools/cifras.py` y
el CI falla si vence, pero Oracle permanece experimental: no tiene fecha de corte, condición de
cierre ni tope de tamaño para el núcleo. La puerta fechada y el tope que existieron durante un día se
retiraron el 2026-08-24: medían un experimento como si ya fuera un producto.

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

## Cinco niveles, una sola representación

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

### Los dos de abajo ya están habitados

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

## Lo que una medida declara, siempre

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

## Heredar un catálogo sin quedar en rojo el primer día

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

## Las decisiones, y por qué

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

## Estado

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
**176 casos**: 107 defectos y 69 verdes correctos. De los defectos, 103 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 2 límite humano. Por etiqueta: 102 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño. Por procedencia: 93 observada, 77 construida, 6 generada y 0 sin declarar.
<!-- corpus:fin -->

<!-- cifras:inicio -->
1122 tests · 868/868 mutantes de medida · **5096 sitios de mutación de código** (4886 + 210 del motor Python).
<!-- cifras:fin -->

Los sitios de mutación de código son un denominador, no un resultado. Este README no publica una
ronda vigente sobre todo el denominador publicado arriba. El corte fechado que sí conserva, del 2026-08-25, cubrió
`nucleo/caso.py`: **193 mutantes, 136 muertos, 57 sobrevivientes, 0 timeouts y 0 errores de arnés**.
Además, el camino sin `--objetivo` conserva un timeout conocido; la medición válida se particiona por
objetivo. Ninguno de esos dos límites se convierte en «verde» por el resultado de mutación de medidas.

### Tres dominios, un álgebra

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

### El bucle cerrado

`tools/mutar.py` muta las **medidas** —que son datos, así que no se toca ningún archivo y no hay
`.pyc` que pueda quedar viejo— y produce hechos `mutante(id, apunta_a, murio)`. Esos hechos los juzga
**una medida del catálogo**, `proceso.test_con_mutante_que_lo_mata`. El sensor no dicta veredictos:
produce evidencia, y el álgebra la mide.

Hasta el 2026-09-02 esos mutadores tenían el mismo autor que las medidas y el corpus. Un segundo autor,
aislado del repositorio y con acceso sólo a la especificación y al contrato, escribió **24**. En la
primera corrida el corpus mató **142 de 179 (79%)**; de los sobrevivientes salieron tres huecos reales,
cerrados con casos en el borde. También mostró un límite del catálogo: las 54 medidas universales usan
la misma forma de umbral, `<= 0`, y 17 de sus mutadores no aplicaron a ninguna.

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

### Dos oráculos, y ninguno alcanza solo

La ronda de mutación dejó algo a la vista: de 6 mutantes del núcleo, los 6 mueren con los tests, pero
**3 dejan la aceptación en verde**. El replay del corpus ejercita la *evaluación*; las reglas de
*declaración* —que un umbral traiga defensa, que el alcance no esté vacío— sólo las cubren los tests.
Hacen falta los dos, y conviene no confundir el verde de uno con el del otro.

### Qué falta

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

## Por qué el corpus va primero

Porque es lo único que se pierde. Un LLM no recuerda sus fallas entre sesiones, y si el corpus se
escribe *después* del framework, se escribe para que pase. Los casos que hay acá se capturaron el
mismo día en que ocurrieron, antes de existir nada que los midiera.
