# Decisión 005 — la numeración va de L−2 a L2, y se cierra en los dos extremos

**Fecha:** 2026-08-26 · **Estado:** vigente, comprobada por L−1 y L−2 el 2026-08-28 ·
**Alcance:** nomenclatura y límites de la torre.

## Lo que se decide

Los niveles de representación de Oracle se numeran **L−2, L−1, L0, L1, L2**. El cero está donde
estaba —la evidencia—, los positivos suben hacia los enunciados y los negativos bajan hacia el
mundo. No hay L3 y no hay L−3, y las dos ausencias tienen motivos distintos.

```
L2   medidas sobre medidas   enunciados sobre L1
L1   medidas                 enunciados sobre L0
L0   evidencia               filas
L−1  qué lee el sensor       su alcance y las unidades de cada campo
L−2  qué leyó, y en qué      identidad y frescura del referente
     el terreno              no es un nivel
```

## La regla que sostiene la numeración

**Un nivel es una representación, nunca una cosa.** L0 no es la escena: son filas. Bajando vale
igual y es lo que más se presta a confusión: L−1 **no es el sensor**, es lo que el sensor declara de
sí mismo. El sensor es a L−1 lo que la escena es a L0 — la cosa, no el nivel. Un nivel que no se
puede escribir no es un nivel de este proyecto; es un componente.

## Por qué no hay L3

Colapsa, no falta. Con el catálogo reificado como una relación más, una medida sobre medidas sobre
medidas se escribe **idéntica** a una medida sobre medidas: mismas cinco operaciones, misma álgebra,
la misma relación `medida`. Medido el 2026-08-26: el catálogo tiene 38 medidas y
`meta.ninguna_medida_sin_alcance` juzga las 38, **ella incluida**. Ya es L2 y L3 a la vez.

Tampoco hay paradoja de autorreferencia, y conviene dejar escrito por qué antes de que alguien la
busque: la medida no es un predicado de verdad sobre sí misma. No pregunta «¿soy verdadera?»,
pregunta «¿cuántas filas de esta relación tienen el `alcance` vacío?», y ella es una de las filas.
Es un cómputo finito sobre una bolsa finita. Tarski no se entera.

## Por qué no hay L−3

Se acabó lo representable. L−1 pregunta cómo se hizo el mapa; L−2 pregunta si el territorio mapeado
es el territorio del que habla el veredicto. Debajo está el terreno, y lo único honesto que Oracle
puede hacer con él es declarar qué no miró — que es el trabajo de `alcance`, el único campo
obligatorio del lenguaje. Un «L−3» sería el terreno con nombre de nivel, y eso es precisamente la
confusión que la regla de arriba existe para evitar.

## Por qué L−1 y L−2 son dos y no uno

Fallan distinto y se arreglan distinto.

- **L−1 falla con el sensor funcionando bien.** Emite el AABB en centímetros y la medida lo espera
  en metros. Todo lo que reporta es fiel a lo que leyó, y el verde miente. Se arregla declarando
  unidad y alcance por campo.
- **L−2 falla con el sensor perfecto y bien declarado.** Leyó el asset del disco; el juego embarca
  la variante cocinada. Todo cierto, sobre una cosa que no es la del veredicto. Se arregla con
  identidad y frescura del referente — un hash, una versión.

## Lo que la construcción resolvió

La lectura alternativa era que L−2 no fuese un nivel **debajo** de L−1 sino un **parámetro** suyo.
La implementación mostró que no colapsan: `cantidad_comparada` deriva unidades mientras
`referente_declarado` y `referente_comparado` presentan identidad y frescura por separado. Los dos
modos de falla son independientes y se pueden medir sin acoplar sus declaraciones.

## Lo que existe en los dos niveles de abajo

Los dos niveles quedaron expresados en el lenguaje:

| | ya se contesta acá |
|---|---|
| **L−1** | relaciones con unidad y alcance, más `cantidad_comparada` para derivar la unidad que una medida compara |
| **L−2** | `referente_declarado`, `referente_comparado` y medidas que exigen huella y comparan frescura |

Los límites siguen a la vista. L−1 no convierte unidades ni inventa equivalencias para escalares
variádicas. L−2 no verifica que un referente exista ni que una huella corresponda a su contenido:
compara dos declaraciones; recalcular la huella le corresponde al sensor.

## Cómo se sabe que un nivel está terminado

No por haber movido plomería, sino por poder escribir en el lenguaje —**sin tocar Python**— una
medida que hoy no se puede:

- **L2:** «ninguna medida compara un flotante con `==` DENTRO de un filtro» (la actual sólo mira el
  operador final del umbral, y su `alcance` lo declara) y «qué medidas usan `unir`».
- **L−1:** «ningún sensor entrega un campo cuya unidad no declara» y «ninguna medida lee un campo en
  una unidad distinta de la que el sensor emite».
- **L−2:** «ninguna evidencia se juzga contra un referente que cambió después de leerla».

Las medidas de L−1 y L−2 ya se escriben con esas relaciones sin agregar un comparador Python propio;
ésa es la comprobación de cierre. Extender sensores o declarar nuevas relaciones amplía cobertura,
pero no abre otro nivel ni cambia el mecanismo.
