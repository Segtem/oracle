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

Sobre el catálogo real de entonces, 54 medidas:
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

Hoy el motor informa **30 mutadores activos** (6 propios + 24 del segundo autor).

## La mutación en tu medida

Reconstruí el proyecto de la guía anterior con estos archivos:

```bash paso
oracle init biblioteca
cd biblioteca
```

```text salida
Proyecto Oracle inicializado en ./biblioteca:
  · catalogos/
  · corpus/
  · diferencial/
  · relaciones/
  · oracle.json

Próximos pasos:
  1. Creá un caso:     oracle caso <grupo/id>
  2. Creá una medida:  oracle nueva <dominio.nombre>
  3. Verificá todo:    oracle test
```

```json archivo=oracle.json incluir=ejemplo/biblioteca-guia/oracle.json
```

```oracle archivo=catalogos/documento/documento.nombre_sigue_la_convencion.oracle incluir=ejemplo/biblioteca-guia/catalogos/documento/documento.nombre_sigue_la_convencion.oracle
```

```caso archivo=corpus/documento/001-un-nombre-fuera-de-convencion.caso incluir=ejemplo/biblioteca-guia/corpus/documento/001-un-nombre-fuera-de-convencion.caso
```

```caso archivo=corpus/documento/002-un-lote-en-convencion.caso incluir=ejemplo/biblioteca-guia/corpus/documento/002-un-lote-en-convencion.caso
```

```json archivo=relaciones/documento.json incluir=ejemplo/biblioteca-guia/relaciones/documento.json
```


En el proyecto de juguete, tu medida tiene una estructura simple: una sola fuente, un filtro
booleano, conteo y umbral `<= 0`. De los 30 mutadores del motor, **nueve** aplican a esa sintaxis
(los otros mutan uniones, agrupamientos, cotas o agregados que esa medida no usa):

```bash paso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 2 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 2 casos · 1 relaciones

catálogo: 40 medidas · corpus: 2 casos

  ROJO  001-un-nombre-fuera-de-convencion      documento.nombre_sigue_la_convencion  (valor 1)
  verde 002-un-lote-en-convencion              documento.nombre_sigue_la_convencion  (valor 0)

defectos que se pusieron rojos: 1 · verdes correctos: 1 · sin evidencia esperada: 0 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:
  ✓ meta.el_caso_reclama_una_medida_que_existe          0 (<= 0)
  ✓ meta.el_caso_se_pone_como_debe                      0 (<= 0)
  ✓ meta.el_hueco_declarado_explica_por_que             0 (<= 0)
  ✓ meta.el_nivel_no_se_confunde_con_el_dominio         0 (<= 0)
  ✗ meta.la_medida_no_se_fija_solo_con_evidencia_fabricada        1 (<= 0)
      → _={'medida': 'documento.nombre_sigue_la_convencion', 'casos': 2, 'no_observados': 2}
  ✓ meta.ningun_campo_sin_unidad_declarada              0 (<= 0)
  ✓ meta.ningun_flotante_comparado_por_igualdad_en_un_filtro        0 (<= 0)
  ✓ meta.ningun_umbral_de_igualdad                      0 (<= 0)
  ✓ meta.ningun_umbral_flotante_de_igualdad             0 (<= 0)
  ✓ meta.ninguna_medida_sin_alcance                     0 (<= 0)
  ✓ meta.toda_cantidad_comparada_tiene_unidad_derivable        0 (<= 0)
  ✓ meta.toda_medida_de_ausencia_declara_requiere        0 (<= 0)
  ✓ meta.toda_medida_declara_su_ambito                  0 (<= 0)
  ✓ meta.toda_medida_filtra_o_agrupa                    0 (<= 0)
  ✓ meta.toda_medida_lee_campos_que_existen             0 (<= 0)
  ✓ meta.todo_caso_observado_declara_de_donde_salio        0 (<= 0)
  ✓ meta.todo_tanteo_explica_por_que                    0 (<= 0)
  ✓ meta.todo_umbral_declara_de_donde_sale              0 (<= 0)

ACEPTACIÓN ✗ — 1 problema(s)
  · meta.la_medida_no_se_fija_solo_con_evidencia_fabricada: el marco no cumple su propia regla

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 9 · murieron 9 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 9 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 18

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ⊘ proceso.codigo_con_mutante_que_lo_mata       SIN EVIDENCIA («mutante con m.tipo == "codigo"» vacía; no se midió)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: ROJO (falló: aceptación)
```

Oracle rompió tu medida de nueve maneras —le sacó el filtro, le aflojó el umbral, le dio vuelta un
comparador— y evaluó cada versión rota contra cada caso: 18 comprobaciones. Los nueve murieron:
**algún caso tuyo notó cada rotura**.

«Murieron por conducta» significa que el mutante cambió algo observable: el veredicto, los testigos
o el valor. No alcanza con que reviente — un mutante que hace explotar el álgebra no demuestra que
tu corpus lo hubiera atrapado.

## Un sobreviviente, provocado a propósito

Borrá el caso verde y dejá sólo el rojo:

```bash paso
rm -f corpus/documento/002-un-lote-en-convencion.caso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 1 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 1 casos · 1 relaciones

catálogo: 40 medidas · corpus: 1 casos

  ROJO  001-un-nombre-fuera-de-convencion      documento.nombre_sigue_la_convencion  (valor 1)

defectos que se pusieron rojos: 1 · verdes correctos: 0 · sin evidencia esperada: 0 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:
  ✓ meta.el_caso_reclama_una_medida_que_existe          0 (<= 0)
  ✓ meta.el_caso_se_pone_como_debe                      0 (<= 0)
  ✓ meta.el_hueco_declarado_explica_por_que             0 (<= 0)
  ✓ meta.el_nivel_no_se_confunde_con_el_dominio         0 (<= 0)
  ✗ meta.la_medida_no_se_fija_solo_con_evidencia_fabricada        1 (<= 0)
      → _={'medida': 'documento.nombre_sigue_la_convencion', 'casos': 1, 'no_observados': 1}
  ✓ meta.ningun_campo_sin_unidad_declarada              0 (<= 0)
  ✓ meta.ningun_flotante_comparado_por_igualdad_en_un_filtro        0 (<= 0)
  ✓ meta.ningun_umbral_de_igualdad                      0 (<= 0)
  ✓ meta.ningun_umbral_flotante_de_igualdad             0 (<= 0)
  ✓ meta.ninguna_medida_sin_alcance                     0 (<= 0)
  ✓ meta.toda_cantidad_comparada_tiene_unidad_derivable        0 (<= 0)
  ✓ meta.toda_medida_de_ausencia_declara_requiere        0 (<= 0)
  ✓ meta.toda_medida_declara_su_ambito                  0 (<= 0)
  ✓ meta.toda_medida_filtra_o_agrupa                    0 (<= 0)
  ✓ meta.toda_medida_lee_campos_que_existen             0 (<= 0)
  ✓ meta.todo_caso_observado_declara_de_donde_salio        0 (<= 0)
  ✓ meta.todo_tanteo_explica_por_que                    0 (<= 0)
  ✓ meta.todo_umbral_declara_de_donde_sale              0 (<= 0)

ACEPTACIÓN ✗ — 1 problema(s)
  · meta.la_medida_no_se_fija_solo_con_evidencia_fabricada: el marco no cumple su propia regla

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 9 · murieron 8 · sobrevivieron 1
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 8 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 9

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✗ meta.toda_medida_esta_fijada                        1 (<= 0)
      → m=documento.nombre_sigue_la_convencion
  ⊘ proceso.codigo_con_mutante_que_lo_mata       SIN EVIDENCIA («mutante con m.tipo == "codigo"» vacía; no se midió)
  ✗ proceso.test_con_mutante_que_lo_mata                1 (<= 0)
      → m=documento.nombre_sigue_la_convencion·quitar_filtro

lo que el corpus NO fija — ningún caso detecta estas mutaciones:
  · mutar «quitar_filtro» en documento.nombre_sigue_la_convencion pasa inadvertido

Se tapa agregando un caso que SÍ lo note o declarando una equivalencia individual
demostrable; nunca debilitando el mutador. La polaridad y el borde también importan:
`quitar_filtro` suele pedir un verde; `aflojar_umbral`, un rojo junto al límite.

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: ROJO (falló: aceptación, mutación)
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

```oracle archivo=catalogos/documento/documento.nombre_sigue_la_convencion.oracle incluir=ejemplo/biblioteca-guia/catalogos/documento/medida-umbral-invalido.txt
```

```bash paso
oracle test
```

```text salida
CATÁLOGO INVÁLIDO — ./biblioteca/catalogos/documento/documento.nombre_sigue_la_convencion.oracle: línea 4, columna 5: la macro ninguno no coincide con su plantilla declarada: se esperaba 0; llegó 1
   4 |     umbral <= 1 segun contrato porque "la convención de nombres es lo que hace que el índice se pueda generar solo; un archivo fuera de convención lo rompe"
     |     ^

VEREDICTO: ROJO (catálogo no pudo cargarse)
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
- [DECISION-011](decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md) — el protocolo del segundo autor y
  los 24 mutadores en aislamiento.
- `mutadores/` — el contrato, la procedencia y el código del segundo autor.
- [ESPECIFICACION.md](../ESPECIFICACION.md) — la lista completa de mutadores del lenguaje.
