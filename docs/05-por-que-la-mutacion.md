# Por qué la mutación

Una medida que nada puede romper es decoración. La mutación es cómo se comprueba eso, en vez de
suponerlo.

Todo lo que sigue está copiado de corridas reales. El proyecto de juguete es el de
[De cero a un rojo](02-de-cero-a-un-rojo.md).

---

## El problema que resuelve

Escribís una regla. Pasa. ¿Y ahora?

Un test que pasa demuestra que el código hace **algo** compatible con lo que el test mira. No
demuestra que el test mire lo que importa. Con una regla es peor todavía: una medida sin filtro
marca todas las filas y **igual se pone roja** sobre un defecto — parece que funciona.

La pregunta que hay que poder contestar no es «¿pasa?», sino **«¿qué tendría que romperse para que
esto falle?»**. La mutación la contesta rompiendo la medida a propósito y exigiendo que tu corpus
lo note.

## Los siete mutantes

En el proyecto de juguete, con una sola medida y dos casos:

```
$ oracle test
mutantes de medida (medida × mutador): 7 · murieron 7 · sobrevivieron 0
  de los muertos: 7 por conducta (invirtió el veredicto, cambió testigos o cambió el valor)
detecciones evaluadas (mutante × caso): 14
```

Oracle rompió tu medida de siete maneras —le sacó el filtro, le aflojó el umbral, le dio vuelta un
comparador— y evaluó cada versión rota contra cada caso: 14 comprobaciones. Los siete murieron:
**algún caso tuyo notó cada rotura**.

«Murieron por conducta» significa que el mutante cambió algo observable: el veredicto, los testigos
o el valor. No alcanza con que reviente — un mutante que hace explotar el álgebra no demuestra que
tu corpus lo hubiera atrapado.

## Un sobreviviente, provocado a propósito

Borrá el caso verde y dejá sólo el rojo:

```
$ oracle test
mutantes de medida (medida × mutador): 7 · murieron 6 · sobrevivieron 1

  ✗ meta.toda_medida_esta_fijada                 1 (<= 0)
      → m=documento.nombre_sigue_la_convencion
  ✗ proceso.test_con_mutante_que_lo_mata         1 (<= 0)
      → m=documento.nombre_sigue_la_convencion·quitar_filtro

lo que el corpus NO fija — ningún caso detecta estas mutaciones:
  · mutar «quitar_filtro» en documento.nombre_sigue_la_convencion pasa inadvertido

Se tapa agregando un caso que SÍ lo note o declarando una equivalencia individual
demostrable; nunca debilitando el mutador. La polaridad y el borde también importan:
`quitar_filtro` suele pedir un verde; `aflojar_umbral`, un rojo junto al límite.
```

**Por qué sobrevive.** `quitar_filtro` borra el `donde`, así que la medida cuenta **todos** los
documentos en vez de los que violan la convención. Con un solo caso —donde el defecto existe— la
medida se pone roja de las dos formas: con filtro por la fila mala, sin filtro por todas. El caso
no distingue.

El caso verde es el que la distingue: con todos los nombres en convención, la medida **con** filtro
da cero y la rota da dos. Por eso hacen falta las dos polaridades, y no por simetría.

Fijate que la herramienta te dice cuál es el mutador y qué polaridad suele pedir. No dice sólo que
falta algo: dice qué.

## Lo que NO hay que hacer

> *Se tapa agregando un caso que SÍ lo note o declarando una equivalencia individual demostrable;
> **nunca debilitando el mutador**.*

Debilitar el mutador —sacarlo de la lista, ponerle una excepción— hace que el número suba y que la
medición valga menos. Es Goodhart otra vez, un nivel más arriba: el «100% de mutantes muertos»
pasa a ser el objetivo en vez del indicador.

## Aflojar el umbral no siempre se puede

Un ataque obvio a una medida molesta es correrle el umbral. Probalo:

```
umbral <= 1 segun contrato porque "…"
```

```
$ oracle test
CATÁLOGO INVÁLIDO — …/documento.nombre_sigue_la_convencion.oracle: línea 4, columna 5:
la macro ninguno no coincide con su plantilla declarada: se esperaba 0; llegó 1
```

**`ninguno` significa cero.** No es un nombre bonito para `<= 0`: es una macro con una plantilla, y
el lenguaje se niega a llamar «ninguno» a algo que tolera uno. Para aflojar hay que salir de la
macro y escribir la forma canónica — que es visible en cualquier revisión, y es el punto.

## La pregunta ante un sobreviviente

**«¿Por qué este cálculo no se observa?»**

A veces la respuesta es que falta un test. A veces —más seguido de lo que uno espera— es que el
cálculo no debería existir. Tres ejemplos de este repositorio, todos verificables en el historial:

**Código que sobraba** (`8f16903`). Una rama `if macros is not None else …` sobrevivió
a su mutante en `tools/medida.py`. Los cuatro llamadores pasaban `macros` siempre: la rama no la
usaba nadie. Se borró, en vez de escribirle un test que la mantuviera viva.

**Una equivalencia que no lo era** (`0f340f1`). El mutante de `sys.path.insert(0, RAIZ)` → `insert(1, …)`
parecía inobservable, y estuvo a punto de declararse equivalente. Buscar la razón escrita —que el
arnés exige— hizo aparecer el contraejemplo: **todo proyecto que consume Oracle tiene su propia
carpeta `catalogos/`**, así que corriendo la herramienta desde adentro de uno, con `insert(1)` se
importaría el catálogo del consumidor en vez del propio. Hay un test que lo reproduce.

**Un defecto real, no un test faltante** (`7591e88`). Un mutante `In → NotIn` sobrevivió en la línea
que marca `[EN SOMBRA]`. Al escribir el test para matarlo, el test falló contra el código: la marca
salía al final del bloque de testigos, a cinco renglones del id que ensombrece. Estaba mal puesta, y
lo mismo que no ponerla.

## Los dos niveles

| | qué muta | quién lo corre |
|---|---|---|
| **medidas** | el catálogo: quita filtros, afloja umbrales, invierte comparadores | `oracle test`, en tu proyecto |
| **código** | el Python de Oracle | sólo dentro de Oracle |

En tu proyecto ves el primero. El segundo es cómo Oracle se mide a sí mismo, y su regla es la misma:
un mutante de código que sobrevive es código que nada observa.

---

## Qué sigue

- [De cero a un rojo](02-de-cero-a-un-rojo.md) — si todavía no armaste el proyecto de juguete.
- [Conectar Oracle a un proyecto propio](07-conectar-a-un-proyecto-propio.md) — de dónde sale la
  evidencia observada.
- [ESPECIFICACION.md](../ESPECIFICACION.md) — la lista completa de mutadores.
