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

## Los mutadores tienen autor (`DECISION-011`)

Hasta esta versión, `tools/mutar.py` decía **715/715 mutantes muertos**. Ese 100% medía cobertura
sobre cinco mutadores propios (`aflojar_umbral`, `invertir_comparador`, `quitar_filtro`,
`quitar_requiere`, `negar_filtro`), más los estructurales, todos escritos por la misma persona que
escribió las medidas y el corpus.

El problema no se ve desde adentro: **un mutador que nadie escribió no puede producir un
sobreviviente.** El 100% era un indicador sobre un conjunto cerrado y complaciente.

La corrección fue metodológica: **otro autor, en aislamiento verificable.**
- En un directorio con dos archivos (`ESPECIFICACION.md` y `CONTRATO.md`), con el párrafo que
  enumeraba los sitios de mutación existentes tachado para no inducir las mismas respuestas.
- El segundo autor no vio `nucleo/mutacion.py`, ni el catálogo, ni un solo caso del corpus, ni los
  tests. Se auditó su registro de comandos (`mutadores/PROCEDENCIA.md`): tres comandos dentro de ese
  directorio y ninguna lectura hacia afuera.
- Escribió **24 mutadores** (`mutadores/segundo_autor.py`).

Sobre el catálogo real de 54 medidas universales:
- Generaron **179 mutantes aplicables**.
- El corpus mató **142 en la primera corrida (79%)**.
- De los 37 sobrevivientes, 6 los rechazó el álgebra y quedaron **31 reales**.
- **Tres eran huecos de verdad** en medidas escritas ese mismo día: `alejar_limite_de_defecto` y
  `hacer_estricta_comparacion_interna` sobrevivieron sobre
  `meta.toda_opcion_del_vocabulario_declara_su_sentido` y `meta.ninguna_sombra_envejece_sin_revisarse`.
  Los casos tenían anomalías grandes (4 palabras contra 22; 244 días contra 90) y ningún testigo en
  el borde exacto. Se cerraron con dos casos en el límite: uno de 5 palabras y uno de 91 días.
- **Veintiocho eran un mutante equivalente**: `convertir_conteo_en_existencia` cambia `contar` por
  `max(1)`. Con `umbral <= 0` —el umbral de las 54 medidas del catálogo— «contar al menos una» y
  «existe alguna» son la misma afirmación. Queda excluido del arnés con su razón declarada en
  código.
- **Diecisiete no aplicaron a ninguna medida**, porque el catálogo universal usa monótonamente
  `umbral <= 0`.

Hoy el motor tiene **28 mutadores activos** (5 propios + 23 del segundo autor).

## La mutación en tu medida

En el proyecto de juguete, tu medida tiene una estructura simple: una sola fuente, un filtro
booleano, conteo y umbral `<= 0`. De los 28 mutadores del motor, **siete** aplican a esa sintaxis
(los otros mutan uniones, agrupamientos, cotas o agregados que esa medida no usa):

```
$ oracle test
mutantes de medida (medida × mutador): 7 · murieron 7 · sobrevivieron 0
  de los muertos: 7 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
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
  de los muertos: 6 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 7

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✗ meta.toda_medida_esta_fijada                        1 (<= 0)
      → m=documento.nombre_sigue_la_convencion
  ✗ proceso.test_con_mutante_que_lo_mata                1 (<= 0)
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

La consecuencia real ya ocurrió: al pasar de 5 a 28 mutadores (`DECISION-011`), la biblioteca de
ejemplo dejó de certificar porque publicaba 12 mutantes y el arnés nuevo medía 16. Agregar
mutadores **invalida la certificación** de bibliotecas existentes, y es correcto: una biblioteca
certificada contra 5 mutadores no está certificada contra 28. No se aflojó el chequeo; se
re-midió y se re-certificó.

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
| **código** | el Python de Oracle | sólo dentro de Oracle (`tools/mutar_codigo.py`) |

En tu proyecto ves el primero. El segundo es cómo Oracle se mide a sí mismo, y su regla es la misma:
un mutante de código que sobrevive es código que nada observa.

El costo está medido: confirmar un sobreviviente cuesta una corrida completa de la suite (~50 s),
porque el arnés corre los módulos prioritarios primero y el resto si sobrevive. Mutar `nucleo/mutacion.py`
pide `--timeout 180`: la línea base tarda 50,5 s contra el plazo por omisión de 60 s.

---

## Qué sigue

- [De cero a un rojo](02-de-cero-a-un-rojo.md) — si todavía no armaste el proyecto de juguete.
- [Conectar Oracle a un proyecto propio](07-conectar-a-un-proyecto-propio.md) — de dónde sale la
  evidencia observada.
- [DECISION-011](../DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md) — el protocolo del segundo autor y
  los 24 mutadores en aislamiento.
- `mutadores/` — el contrato, la procedencia y el código del segundo autor.
- [ESPECIFICACION.md](../ESPECIFICACION.md) — la lista completa de mutadores del lenguaje.
