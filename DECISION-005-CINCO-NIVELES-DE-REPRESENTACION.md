# Decisión 005 — la numeración va de L−2 a L2, y se cierra en los dos extremos

**Fecha:** 2026-08-26 · **Estado:** vigente · **Alcance:** nomenclatura y hoja de ruta. Ningún
cambio de código sale de esta decisión; sale de las dos que la siguen.

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

## Lo que NO se decide, y hay que resolver construyendo

Queda abierta una lectura alternativa: que L−2 no sea un nivel **debajo** de L−1 sino un
**parámetro** de él —«a qué le apuntaste» como parte de la declaración del sensor—. Se elige
separarlos porque los dos modos de falla de arriba son independientes, pero si al construirlos
resulta que nunca se declaran por separado, entonces era uno solo y se colapsan. Eso se sabe
construyendo, no discutiendo, y esta decisión se revisa entonces.

## Lo que ya existe de los dos niveles de abajo

No son terreno virgen. Están habitados, resueltos de a uno en Python en vez de en el lenguaje:

| | ya se contesta acá |
|---|---|
| **L−1** | nada sistemático; sólo la prosa del `alcance` de cada medida |
| **L−2** | `fixture vencido: cambió referencia (fd9fca09… → 9a79cad1…)` en `nucleo/fixtures.py`; `proceso.verificacion_vigente`, que invalida un verde con el árbol sucio |

Y los dos campos que un caso ya declara caen uno en cada nivel: `origen: {repo, commit}` es L−2 y
`procedencia` es L−1. Los dos los tipea una persona y ninguno se verifica —el `alcance` de
`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` lo confiesa—. Es la misma situación en la
que estaba L2 antes de reificar el catálogo, y de ahí sale el orden del trabajo: **terminar L2
primero**, porque la maquinaria que lo vuelve expresable es la que después alcanza a L−1 y L−2.

## Cómo se sabe que un nivel está terminado

No por haber movido plomería, sino por poder escribir en el lenguaje —**sin tocar Python**— una
medida que hoy no se puede:

- **L2:** «ninguna medida compara un flotante con `==` DENTRO de un filtro» (la actual sólo mira el
  operador final del umbral, y su `alcance` lo declara) y «qué medidas usan `unir`».
- **L−1:** «ningún sensor entrega un campo cuya unidad no declara» y «ninguna medida lee un campo en
  una unidad distinta de la que el sensor emite».
- **L−2:** «ninguna evidencia se juzga contra un referente que cambió después de leerla».

Mientras esas medidas necesiten un campo nuevo escrito en Python, el nivel está a medias.
