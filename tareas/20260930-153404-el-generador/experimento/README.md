# El generador busca y encoge evidencia

**Pregunta.** Partiendo de un corpus vacío, ¿cuánto de cada medida fija la evidencia que fabrica el
generador de reglas fijas, y cuánto más fija una búsqueda determinista que perturba esa evidencia
hasta que la medida y el mutante discrepan, y después la encoge?

**Por qué.** Las reglas derivan la evidencia de la forma de la medida y no cubren todas las formas.
La búsqueda viene de las pruebas basadas en propiedades (buscar un contraejemplo y encogerlo), sin
azar y sin modelo: la evidencia de un defecto se fabrica por perturbación determinista.

## Método

`linea_base.py` recorre las medidas propias de cada proyecto y, sin ningún caso previo, cuenta los
mutantes que mata lo que fabrican las reglas (`fabricar_candidatos`) y, con `--busqueda`, lo que
agrega `buscar_candidatos`. `sobrevivientes.py` clasifica lo que dejan vivo las reglas.

La búsqueda (`nucleo/generador.py`):

1. **Semillas:** la evidencia que proponen las reglas —aunque no cumpla la polaridad que buscaba— y
   la de los casos del corpus de esa medida, con toda relación que la medida lee presente.
2. **Vecinos**, en un orden fijo: cambiar un campo por un literal de la medida, por el valor de
   otro campo de la fila, por ±1, 0, el opuesto, el doble más uno, el texto vacío o el booleano
   contrario; duplicar una fila; quitarla. Anchura primero, hasta dos cambios, con un presupuesto
   de 3000 evaluaciones por mutante.
3. **Criterio:** el de `correr`: la medida original y el mutante dan `ok` distinto, y la original no
   está sin evidencia. La etiqueta del caso es la que la original le da.
4. **Encoger:** quitar filas y llevar cada valor a 0, `""` o `false` mientras la discrepancia se
   mantenga igual.

## Resultado (2026-09-30, corpus vacío)

| proyecto | medidas | mutantes | reglas | reglas + búsqueda | no posibles | tiempo |
|---|---|---|---|---|---|---|
| experimento OpenSpec | 32 | 651 | 526 (80,8 %) | **610 (93,7 %)** | 3 → 0 | 5,7 s |
| LyraGASP | 29 | 487 | 373 (76,6 %) | **433 (88,9 %)** | 6 → 0 | 158 s |
| Jam | 41 | 449 | 344 (76,6 %) | 353 (78,6 %) | 9 → 0 | 3,3 s |
| Oracle | 64 | 1111 | 755 (68,0 %) | **932 (83,9 %)** | 10 → 0 | 7,5 s |

Lo que dejaban vivo las reglas: 94 mutantes de campo, 67 de expresión, 24 de rama de disyunción y
6 de umbral o agregado. Los de campo son el caso típico: un campo cambiado por otro sobrevive si
las filas fabricadas tienen el mismo valor en los dos, y la búsqueda lo separa poniendo un valor
distinto.

## Límites

- **Jam casi no mejora.** Sus escalares esperan geometría del dominio; con un corpus vacío no hay
  de dónde sacarla, y un `0.0` inventado las hace fallar. Con corpus, `oracle caso generar` usa los
  casos de la medida como semilla, que es el uso real.
- **LyraGASP es lento** (158 s): cada evaluación cruza al proceso aislado de sus escalares.
- **Los tipos no se validan.** Oracle no compara la evidencia con los tipos declarados de la
  relación, y las reglas ya ponen textos donde comparan dos campos entre sí; el encogido conserva el
  tipo de la semilla, así que un campo numérico puede quedar `""`. Respetar el `.relacion` cuando
  existe es el paso siguiente.
- **Encoger no busca el mínimo global**: saca filas y simplifica valores de a uno, en orden fijo.
- Toda la evidencia buscada es `procedencia: generada`: sube la mutación, no el respaldo real.
