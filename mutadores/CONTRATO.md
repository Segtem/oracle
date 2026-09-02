# Contrato: escribir mutadores de medidas

Leé `ESPECIFICACION.md`, que está al lado. Define qué es una medida y en qué forma de datos se
escribe. Este documento define lo único que falta: qué es un mutador y qué tiene que cumplir.

## Qué es un mutador

Una función que recibe una medida como dato y devuelve **otra medida, más débil**, o `None` si a esa
medida no se le puede aplicar.

```python
def mi_mutador(datos: list) -> list | None:
    ...
```

`datos` es la medida en su forma de dato, tal como la describe la especificación. No lo modifiques
en el lugar: devolvé una copia.

## Qué quiere decir «más débil»

La medida mutada tiene que **seguir siendo una medida válida** —la especificación dice qué la hace
válida— y tiene que ser **más fácil de aprobar** que la original: donde la original decía «esto está
mal», la mutada puede decir «esto está bien».

Un mutador que produce una medida que el álgebra rechaza no sirve: no prueba nada sobre el corpus,
sólo que el validador funciona.

## Para qué sirve, y por qué importa que sea difícil

Cada medida tiene casos de prueba escritos a mano que declaran «acá hay un defecto, la medida tiene
que dar rojo». Se toma la medida, se le aplica el mutador, y se vuelve a evaluar contra la misma
evidencia:

- si el caso pasa a **verde**, el mutador **murió**: los casos sí fijan ese aspecto de la medida;
- si el caso **sigue en rojo**, el mutador **sobrevivió**: los casos NO fijan ese aspecto. La medida
  se podría haber escrito de esa otra forma y nadie se habría dado cuenta.

**Un mutador que sobrevive es el producto valioso.** Encuentra un lugar donde las pruebas no están
mirando. Un mutador que muere siempre no enseña nada.

## Lo que se te pide

Escribí todos los mutadores que se te ocurran, en un solo archivo `mutadores.py`, cada uno con un
docstring en español que diga **qué debilita y por qué eso podría pasar inadvertido**.

Pensá el espacio completo antes de escribir: ¿de cuántas maneras distintas se puede debilitar una
medida sin que deje de ser una medida? Recorré la especificación buscando cada lugar donde una
decisión podría haber sido otra.

No te limites a los que creas que van a morir. Los que te parezcan «demasiado obvios» y los que te
parezcan «demasiado raros» entran igual: cuáles mueren y cuáles no es justamente lo que no sabés y
lo que se quiere averiguar.

## Restricción dura, y es la razón de todo esto

Este directorio contiene **exactamente dos archivos** y son todo lo que podés leer. No busques,
abras ni listes nada fuera de él — ni otro repositorio, ni una implementación existente, ni ejemplos
de mutadores de ningún proyecto, ni documentación en línea.

El motivo: ya existe un conjunto de mutadores escrito por otra persona, y el valor de lo que escribas
depende enteramente de que no lo hayas visto. Si mirás, el resultado se descarta entero — no porque
esté prohibido, sino porque deja de medir lo que se quería medir.

Al terminar, escribí `PROCEDENCIA.md` declarando: qué archivos leíste (todos), qué comandos
corriste, y si en algún momento miraste algo fuera de este directorio. Esa declaración es el
artefacto que importa; el código sin ella no sirve.
