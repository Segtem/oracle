# Tarea — `nucleo/sintaxis.py` nunca se mutó, y son 1026 líneas

Leé `DOCTRINA.md` primero. Es obligatorio.

## El problema, exacto

    archivo                     líneas   cambiadas en 3 días
    nucleo/sintaxis.py            1026                  1064

Es decir: **prácticamente todo el archivo es código nuevo**, y la mutación de código nunca corrió
sobre él. Es el lector, el parser, el impresor y el mapa de fuente de la superficie infija — o sea,
la mitad de lo que hoy hace que Oracle sea un lenguaje y no un formato de datos.

El precedente inmediato dice qué esperar. `nucleo/caso.py` —439 líneas, la otra superficie— se mutó
por primera vez ayer y dio **57 sobrevivientes de 193**: 38 constantes de posición, 9 comparadores de
borde, 8 booleanos y 2 retornos. Traducido: la superficie prometía decir «archivo, línea y columna» y
ningún test fijaba que la posición fuera la correcta. `sintaxis.py` es el doble de grande y tiene la
misma clase de código.

## Qué hay que hacer

    python tools/mutar_codigo.py --objetivo nucleo/sintaxis.py

hasta que dé **cero sobrevivientes**.

## Cómo se mata un mutante, y las cuatro respuestas posibles

Clasificá **cada** sobreviviente en una de estas cuatro, y poné el reparto en `INFORME.md`:

1. **Falta un test.** El caso normal. Escribilo.
2. **Es equivalente** —cambia el código sin cambiar la conducta—. Se declara en `equivalentes.json`
   **con su razón escrita**. La razón tiene que explicar por qué NINGÚN test podría distinguirlo, no
   por qué te resultó difícil. Declararlo sin razón es una excusa, y el proyecto lo dice así.
3. **El código sobra.** Si nada puede distinguirlo, puede que esa rama no haga falta. Borrar código
   muerto es mejor respuesta que un test.
4. **Es un BUG**: mirándolo descubrís que la versión mutada es la correcta. Decilo fuerte: es el
   hallazgo más valioso que puede salir de esto.

### Los mutantes de posición, que son la mayoría

Un mutante `1 → 2` en un cálculo de columna sobrevive a cualquier test que sólo verifique que hubo
error. Hay que **fijar la línea y la columna exactas**, y elegirlas en un borde: un error en la
primera columna no distingue `col` de `col + 1`.

`fragmento_de_error(error, texto)` arma el fragmento con el caret; un test que compara el fragmento
entero fija la posición sin escribir el número dos veces.

### Prohibido

- Aflojar cualquier verificación para que la ronda cierre: ni `--timeout` más alto para tapar algo,
  ni sacar un mutador, ni declarar equivalente lo que no lo es.
- Tocar `corpus/`. Si necesitás evidencia para un test, armala en un temporal.
- Tocar `vendor/`.

Usá `--manifiesto progreso.json` y `--reanudar`: las rondas tardan y no conviene repetir trabajo.

## Cómo sé que terminaste

1. `python tools/mutar_codigo.py --objetivo nucleo/sintaxis.py` con **cero sobrevivientes**, salida
   pegada en `INFORME.md`.
2. Las nueve verificaciones de `DOCTRINA.md` en verde.
3. El reparto de los sobrevivientes en las cuatro categorías.
4. Si encontraste un bug (categoría 4), su descripción arriba de todo en el informe.

Commiteá en tu worktree. No pushees.
