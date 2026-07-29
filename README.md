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

**Paso 2 de 5.** Están el [corpus](corpus/) (11 casos), la [especificación](ESPECIFICACION.md) del
álgebra, el evaluador (`nucleo/`) y 8 medidas en [`catalogos/`](catalogos/) — **como archivos de
datos, no como código**.

```bash
python tools/corpus.py --resumen                 # el corpus está en regla
python tools/aceptacion.py                       # el corpus juzga al oráculo
python -m unittest discover -s tests -t . -q     # 32 tests, cero dependencias
```

Los 9 casos que declaran una medida **se ponen en rojo**; los 2 con hueco declarado siguen verdes a
propósito y su número tiene que bajar. Corre además el nivel L2: el catálogo servido como relación y
medido por una medida, sin ningún mecanismo nuevo.

**Tres de los seis operadores están implementados** (`de`, `donde`, `resumen`): son los únicos que
piden las medidas que existen. Los otros levantan un error que dice su disparador.

### Dos oráculos, y ninguno alcanza solo

La ronda de mutación dejó algo a la vista: de 6 mutantes del núcleo, los 6 mueren con los tests, pero
**3 dejan la aceptación en verde**. El replay del corpus ejercita la *evaluación*; las reglas de
*declaración* —que un umbral traiga defensa, que el alcance no esté vacío— sólo las cubren los tests.
Hacen falta los dos, y conviene no confundir el verde de uno con el del otro.

### Qué falta

- **Paso 3 — el sensor de mutación**: producir hechos `mutante(id, apunta_a, murio)` del repo vivo,
  con caché frío. Es lo que hace que `proceso.test_con_mutante_que_lo_mata` muerda sobre código real
  en vez de sobre evidencia guardada.
- **Paso 4 — el catálogo de geometría**, que es el que prueba que el álgebra es general y el que
  dispara `unir`.
- **Paso 5 — cablearlo**: que los verificadores escritos a mano de Jam se re-expresen como medidas.

## Por qué el corpus va primero

Porque es lo único que se pierde. Un LLM no recuerda sus fallas entre sesiones, y si el corpus se
escribe *después* del framework, se escribe para que pase. Los casos que hay acá se capturaron el
mismo día en que ocurrieron, antes de existir nada que los midiera.
