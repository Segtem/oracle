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

## Tres influencias, y qué aporta cada una

| | Qué aporta |
|---|---|
| **SQL** | el álgebra: relaciones entran, relaciones salen — clausura sobre la evidencia |
| **GPSS** | la segunda fuente de evidencia: simulá el sistema y medí lo que emergió |
| **LISP** | la representación: la medida **es un dato** ⇒ el lenguaje se extiende desde adentro |

Los tres se necesitan. Sin el álgebra no compone. Sin la simulación sólo juzga lo estático. **Sin la
homoiconicidad el lenguaje tiene dueño** — y el dueño sería el LLM, que es exactamente el problema.

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

## Estado

**Los cinco pasos, hechos.** El [corpus](corpus/) (19 casos), la [especificación](ESPECIFICACION.md) del álgebra,
el evaluador (`nucleo/`), **27 medidas en cuatro dominios** dentro de [`catalogos/`](catalogos/) —como
archivos de datos, no como código—, el sensor de mutación y la prueba diferencial.

**¿Querés escribir una medida?** → [`ESCRIBIR-UNA-MEDIDA.md`](ESCRIBIR-UNA-MEDIDA.md).
`python tools/medida.py --relaciones` te dice qué hechos hay para medir; `--nueva` crea el archivo.

```bash
python tools/medida.py --relaciones              # qué se puede medir, derivado de la evidencia real
python tools/corpus.py --resumen                 # el corpus está en regla
python tools/aceptacion.py                       # el corpus juzga al oráculo
python tools/diferencial.py                      # el álgebra vs una implementación independiente
python tools/mutar.py                            # ¿el corpus ALCANZA para fijar las medidas?
python -m unittest discover -s tests -t . -q     # 53 tests, cero dependencias
```

10 defectos en rojo · 7 verdes correctos · 3 huecos declarados · **1200 veredictos de geometría
coincidiendo con una implementación independiente** · 44/44 mutantes de medida · **211/242 mutantes
de código** · 81 tests.

> **`tools/mutar_codigo.py` sale en ROJO a propósito, y el número está a la vista.** 31 mutantes
> siguen vivos: código del núcleo que ningún test fija. Se podrían declarar equivalentes en masa para
> pintar verde — y eso sería exactamente el Goodhart que este repositorio persigue. El número baja
> escribiendo tests o declarando equivalentes **de a uno y con su razón escrita**.

### Dos dominios, un álgebra

Es el criterio que decide si esto es general o si es una cosa disfrazada de otra:

| Dominio | Qué mide | Cómo se verifica |
|---|---|---|
| **proceso** | un agente construyendo herramientas: mutantes, afirmaciones, verificaciones vencidas | el corpus de fallas reales |
| **geometría** | piezas en un nivel: interpenetración, bounds, snap a grilla y yaw | 1200 veredictos contra los oráculos escritos a mano de Jam |
| **vault** | la documentación de un proyecto: convención de nombres, coherencia del frontmatter, enlaces | 42 veredictos contra `tools/vault.py` de Jam, con un defecto inyectado de cada tipo |
| **relevo** | la entrega de un turno entre dos agentes: testigo completo, agentes conocidos, verificación reproducible | 48 veredictos contra `tools/relevo.py`, sobre repositorios git montados para cada escenario |

No se parecen en nada, y usan **los mismos operadores sin un solo adaptador**.

La prueba más limpia de que el álgebra cierra: `proceso.verificacion_vigente` se escribió para un caso
del corpus, y **juzgó los hechos del sensor de relevo sin una sola modificación**. La misma medida, dos
sensores distintos, dominios distintos. La prueba diferencial
la genera Jam (`tools/emitir_diferencial.py`) con código que no comparte una línea con este álgebra;
lo único que viaja entre los repos es un archivo de hechos.

### El bucle cerrado

`tools/mutar.py` muta las **medidas** —que son datos, así que no se toca ningún archivo y no hay
`.pyc` que pueda quedar viejo— y produce hechos `mutante(id, apunta_a, murio)`. Esos hechos los juzga
**una medida del catálogo**, `proceso.test_con_mutante_que_lo_mata`. El sensor no dicta veredictos:
produce evidencia, y el álgebra la mide.

Hoy: **44 mutantes, 44 muertos** (el corpus y el fixture diferencial se usan los dos como material de
mutación). Un sobreviviente sería un aspecto de la medida que nada fija, y por lo tanto algo que se
podría escribir mal sin que nada frene.

### Las dos polaridades del corpus

La primera corrida del sensor dejó 10 sobrevivientes, casi todos del mutador `quitar_filtro`. La
causa no era el código: **el corpus tenía sólo defectos**. Con `contar` y umbral `<= 0`, una medida
sin filtro sólo da verde si la relación está vacía, así que ningún caso de defecto puede notar que le
saquen el filtro. Hace falta la otra polaridad — evidencia real donde la medida **debe** decir verde.

Es lo mismo que evaluar un clasificador sólo con positivos. De ahí los 7 casos `verde_correcto`.

**Corrección, dos pasos después.** Cuando el catálogo de geometría trajo el patrón
«`donde tol` → `resumen max` → `umbral tol`», aparecieron dos sobrevivientes que eran **mutantes
equivalentes**: quitar ese filtro no puede cambiar el veredicto nunca —si nada supera la tolerancia el
máximo sin filtrar sigue por debajo, y si algo la supera sigue por encima—. Sí cambia **los
testigos**.

De ahí que el sensor compare **veredicto Y testigos**: los testigos son lo que una persona lee para
actuar, así que el informe también es contrato. Y con ese cambio hay que corregir lo de arriba:
**ningún mutador del juego actual necesita un caso verde** — `aflojar_umbral` necesita uno ROJO, y el
resto se detecta por los testigos en cualquiera de las dos polaridades. Los casos verdes siguen
valiendo por otra razón: son lo único que ataja una medida que se pone roja con entrada correcta, que
es el modo de falla del caso `008`.

**Las macros ya existen** — el disparador que la especificación pedía («cuando aparezca la quinta
medida con la misma forma») sonó con **22**. `ninguno`, `ninguno-par` y `peor` cubren 26 de las 27
medidas, expanden a la forma canónica, y `peor` cerró por construcción la deuda del umbral duplicado.

**Cuatro de los seis operadores están implementados**: `de`, `donde`, `resumen`, y `unir` — que entró
al llegar su disparador, porque «pares de piezas que se clavan» es un producto y ninguna medida de
proceso lo necesitaba. `con` y `agrupar` siguen levantando un error que dice cuál sería el suyo.

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
- **Los 31 mutantes de código vivos**, de a uno.
- **Los 3 huecos declarados del corpus**: dos son defectos del lenguaje (`004` testigos duplicados,
  `012` umbral duplicado) y uno no tiene forma mecánica conocida (`011`).
- **El modo simulación** (§5 de la especificación) sigue sin un solo usuario.
- **Los dos huecos declarados del corpus** (`004`, `011`, `012`): dos son defectos del lenguaje y uno
  no tiene forma mecánica conocida. Su número es una métrica y tiene que bajar.

## Por qué el corpus va primero

Porque es lo único que se pierde. Un LLM no recuerda sus fallas entre sesiones, y si el corpus se
escribe *después* del framework, se escribe para que pase. Los casos que hay acá se capturaron el
mismo día en que ocurrieron, antes de existir nada que los midiera.
