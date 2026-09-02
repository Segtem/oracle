# Decisión 011 — los mutadores tienen autor, y hasta hoy era uno solo

**Fecha:** 2026-09-02 · **Estado:** vigente

## El hecho

`tools/mutar.py` decía **715/715 mutantes muertos**. Ese número medía cobertura sobre **cinco
mutadores escritos por la misma persona que escribió las medidas y el corpus**, más los
estructurales, también suyos.

El problema no se ve desde adentro y no lo arregla escribir más casos: **un mutador que nadie
escribió no puede producir un sobreviviente.** El 100% acotaba menos de lo que parecía, y el
`README` lo declaraba como límite conocido sin hacer nada al respecto.

## Lo que se hizo

El mismo protocolo que ya había funcionado una vez, para el evaluador de referencia del diferencial
(`PLAN-LENGUAJE.md`, e.2): **otro autor, en aislamiento verificable.**

- Un directorio con **exactamente dos archivos**: `ESPECIFICACION.md` y un `CONTRATO.md` que define
  qué es un mutador y nada más.
- A esa copia de la especificación se le quitó **un párrafo**, el que enumera qué sitios muta la
  implementación existente. Leerlo lo habría llevado a proponer lo mismo. La redacción está
  declarada, y el lugar del párrafo lleva una nota diciendo qué se sacó y por qué.
- **No vio** `nucleo/mutacion.py`, ni el catálogo, ni un solo caso del corpus, ni los tests.

**No se le creyó la declaración: se auditó el registro.** Corrió tres comandos, los tres con ese
directorio como raíz, y no aparece ninguna ruta hacia afuera. Su declaración coincide con lo que
hizo. Está en `mutadores/PROCEDENCIA.md`, junto al contrato que leyó.

## El resultado, y por qué el del medio era el bueno

Se había escrito de antemano qué significaría cada resultado, para no interpretarlo después:

| si pasaba | qué habría querido decir |
|---|---|
| el corpus los mata a todos | miró algo, o propuso variantes de los cinco que ya estaban |
| ninguno aplica a ninguna medida | el contrato estaba mal escrito y midió comprensión del formato |
| algunos sobreviven | lo útil |

Escribió **24 mutadores**. Sobre el catálogo real: **179 mutantes aplicables, 142 muertos (79%)**,
37 sobrevivientes. De esos, 6 los rechazó el álgebra —no prueban nada sobre el corpus— y quedaron
**31 reales**.

### Tres eran huecos de verdad, y en medidas escritas ese mismo día

`alejar_limite_de_defecto` (mueve el límite interno de un predicado) y
`hacer_estricta_comparacion_interna` (`<=` → `<`) sobrevivían sobre
`meta.toda_opcion_del_vocabulario_declara_su_sentido` y
`meta.ninguna_sombra_envejece_sin_revisarse`. Sus docstrings lo habían **predicho** sin ver nada:
«omite casos cercanos al límite si el corpus sólo contiene anomalías grandes».

Era cierto: los casos tenían 4 palabras contra 22, y 244 días contra 90 — anomalías grandes y
ningún testigo **en** el límite. Se cerraron con dos casos al borde exacto: uno de 5 palabras y uno
de 91 días.

### Veintiocho eran un mutante equivalente, y se declara como tal

`convertir_conteo_en_existencia` cambia `contar` por `max(1)`: pierde la multiplicidad. Con
`umbral <= 0` —que es el umbral de **las 54 medidas** del catálogo— «contar al menos una» y «existe
alguna» son la misma afirmación, así que no debilita nada y no hay evidencia que pueda
distinguirlo.

Queda **excluido** del arnés, con la razón escrita en el código y no en un comentario suelto. Sobre
un catálogo con otro umbral sí debilitaría, y ahí habría que volver a incluirlo.

### Diecisiete no aplicaron a ninguna medida, y eso también es un dato

Cotas inferiores, agregados `max`/`min`/`promedio`, agrupamientos, productos. **Las 54 medidas del
catálogo tienen la misma forma: `umbral <= 0`.** El arnés de mutación tiene menos poder sobre este
catálogo del que el número sugiere, y no por un defecto del arnés: porque el catálogo es
monótonamente de una sola forma. Eso no se sabía antes de que alguien de afuera propusiera mutar lo
que acá nadie usa.

## La consecuencia que rompió algo, y estuvo bien que lo rompiera

Una biblioteca de políticas publica su número de mutantes y la certificación exige que coincida. Al
pasar de 5 mutadores a 28, la biblioteca de ejemplo dejó de certificar: publicaba 12 y el arnés
medía 16.

**Agregar mutadores invalida la certificación de toda biblioteca publicada**, y es correcto: una
biblioteca certificada contra 5 mutadores no está certificada contra 28. Se volvió a medir y se
republicó el número. Lo que no se hizo —y era la tentación— fue aflojar el chequeo.

## Lo que NO se hizo

No se descartó ningún mutador «que no valiera». La única exclusión es la equivalencia demostrada de
arriba. Descartar mutadores hasta volver al 100% habría sido exactamente el sastreo que este
proyecto persigue en otros lados: elegir el denominador después de ver el resultado.

## El costo, medido

Confirmar un sobreviviente cuesta una corrida COMPLETA de la suite: el arnés discrimina primero con
los módulos prioritarios y, si el mutante sobrevive a ésos, corre el resto para estar seguro. Con
1.033 tests eso son ~50 s por mutante sobreviviente, contra ~0,1 s por mutante que muere temprano.

Agregar 23 mutadores no cambió ese costo por mutante, pero sí multiplicó los mutantes: de 715 a 846
en la ronda de medidas. Y en la de código apareció un efecto de borde que conviene dejar dicho: la
línea base —la suite **sin mutar**— tarda 50,5 s contra un plazo por omisión de 60. Entra, pero bajo
carga se pasa, y un arnés que falla de a ratos es peor que uno lento: enseña a re-correr en vez de a
leer. Para `nucleo/mutacion.py` se corre con `--timeout 180`.

Eso NO se usó para tapar nada. Hubo dos timeouts en esta ronda y se arreglaron distinto, porque son
cosas distintas:

- uno era un mutante **indistinguible por conducta** —cambiaba `return {}` por `return None` en una
  rama cuyo llamador hace `or {}`—, así que el arnés caía a la suite entera para confirmarlo. Ahí
  aflojar el plazo habría tapado que faltaba un test. Se mató fijando el tipo de retorno en los
  tests prioritarios, que es donde tenía que morir;
- el otro era la línea base, que no dice nada sobre el corpus. Ése sí es presupuesto.

## Lo que queda abierto

- **Sigue habiendo dos autores, no muchos.** Un tercero encontraría cosas que estos dos no. El
  protocolo ahora está escrito y cuesta poco repetirlo.
- **El aislamiento se verifica leyendo un registro de comandos**, que es más de lo que hace casi
  nadie y menos que una garantía. Un autor que quisiera hacer trampa podría.
- **`convertir_conteo_en_existencia` está excluido por una equivalencia que hoy es cierta.** Si
  alguna vez entra al catálogo una medida con umbral distinto de `<= 0`, esa exclusión pasa a tapar
  un mutante real. No hay nada que lo avise.
