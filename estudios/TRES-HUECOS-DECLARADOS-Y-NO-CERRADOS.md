# Tres huecos declarados y no cerrados

**2026-09-09 · corte 0.13.0**

Los tres estaban escritos como pendientes. Los tres se cerraron el mismo día. Y los tres resultaron
**peores de lo que su propia declaración decía** — que es el hallazgo, más que los arreglos.

## El patrón

Un `alcance` que declara un hueco cumple una función real: cuando alguien lo pisa, ya está escrito
por qué no se lo vio. Eso pasó con el `agrupar` de 0.9.2 y funcionó.

Pero declarar un hueco también **congela una estimación de su tamaño**, y esa estimación nunca se
vuelve a medir. Las tres veces la estimación estaba mal, siempre en la misma dirección:

| hueco | lo que decía la declaración | lo que era |
|---|---|---|
| la cota no comprobable | un borde raro | **el escenario más común**: una cota sobre una medida de dominio |
| el censo cuenta ilegibles | «archivos que se imprimen» | el número **sólo llegaba a 140 porque se descartaba un campo** |
| campos desconocidos | pérdida silenciosa | además, la **definición de `falso_verde` era falsa** |

## 1. La cota que no vigilaba nada

`meta.ninguna_sombra_supera_su_cota` declaraba no ver la deuda de una medida que no se evaluó. El
escenario parecía exótico. No lo es: `tools/aceptacion.py` alimenta los valores **sólo con los
veredictos de las medidas `meta.*`**, así que una sombra sobre una medida de **dominio** —lo primero
que declararía un consumidor sobre lo suyo— nunca entrega un número.

Medido sobre LyraGASP, con una cota de **cero** sobre `animacion.clip_de_linea_base_ausente_del_lote`:

```
✓ meta.ninguna_sombra_supera_su_cota   0 (<= 0)
ACEPTACIÓN ✓
```

La cota más exigente que existe, sobre el caso más natural, en verde.

El arreglo tiene dos partes. La relación gana `evaluada`, que **no es `valor >= 0`**: el `-1` era un
centinela con dos significados —«no se midió» y «midió menos que cero»— y una medida de dominio
puede dar un negativo legítimo. Y el predicado dice ahora lo que faltaba: **si prometiste un techo y
la medida no entregó un número, no podés afirmar que no lo pasaste.**

## 2. Dos herramientas de Oracle en desacuerdo sobre el mismo proyecto

```
censo:        sintaxis 140/140 archivos se imprimen
oracle test:  VEREDICTO: ROJO (falló: sintaxis)
```

El censo contaba los archivos que **no se pueden imprimir** y no los que **se imprimen y no vuelven
idénticos**. Son dos fallas distintas y se informaba una. La tranquilizadora era la que menos miraba.

## 3. La superficie descartaba en silencio, y la definición estaba mal

91 casos de un consumidor traen un campo `polaridad` que `.caso` no conoce, y el impresor lo tiraba
sin decir nada. La asimetría de fondo:

| | MEDIDAS | CASOS |
|---|---|---|
| superficie de texto | fail-closed | fail-closed |
| carga de JSON | fail-closed | **fail-open** |
| `imprimir` | fail-closed | **descarte silencioso** |

Se cerró al **imprimir** y no al **cargar**. Un caso es evidencia histórica: negarse a leer un
registro por un campo de más es perder el registro, no protegerse de él. Cargar sigue aceptándolos;
escribir se niega a tirarlos.

### Y abajo había otra cosa

`polaridad` decía `rojo_correcto` en 27 casos, una palabra que Oracle no tiene. La primera lectura
—«es vestigial, dice lo mismo que `etiqueta`»— era falsa: los valores difieren. La segunda —«se
perderían 27 distinciones semánticas»— también: `polaridad` es una función **1:1** de `etiqueta`, sin
una excepción, así que no transporta información.

Y la tercera lectura, que es la correcta, invalida a las dos: **la correlación 1:1 no prueba
equivalencia**. Es esperable que dos conceptos coincidan en el campo sustituto si uno tuvo que
escribirse usando el nombre del otro. Alguien quiso decir «acá la medida acierta al fallar», no
encontró cómo, y anotó su intención al lado.

Fuimos a ver si a Oracle le faltaba la palabra. La definición de `falso_verde` decía **«la medida
pasó y no debía»**, en pasado, como si nombrara un episodio. Pero **59 casos `construida` del propio
Oracle** describen el defecto presente en la evidencia —«el literal flotante es operando directo de
`==`»— sobre el que ninguna medida pasó nunca.

**No faltaba una palabra: sobraba una definición que nadie cumplía, incluido Oracle.** Se corrigió la
definición para nombrar el peligro. Agregar `rojo_correcto` habría canibalizado `deuda_de_diseño` y
`medida_correcta_conclusion_errada` —cualquier autor apurado habría elegido la etiqueta genérica— y
habría obligado a tocar casos en tres proyectos. Corregir la definición no toca ninguno.

## El efecto que nadie previó

Cerrar el 3 movió el número del 2. Con el impresor fail-closed, los 91 archivos de LyraGASP dejan de
«imprimirse y no volver» y pasan a **no imprimirse**:

```
antes:    140/140 archivos se imprimen · 91 se imprimen y no vuelven idénticos
después:   49/140 archivos se imprimen ·  0 se imprimen y no vuelven idénticos
```

Se lee como una regresión y es lo contrario: el `140/140` sólo era cierto porque Oracle descartaba
un campo. La deuda no desapareció, cambió de columna, y la columna nueva es la que no miente.

Eso obligó a una comprobación incómoda: **¿el contador recién agregado quedó muerto?** Se probaron
siete formas de que un caso imprima y no vuelva igual —flotantes, orden de claves, enteros grandes,
nulos, saltos de línea— y ninguna lo logra: la superficie falla antes. El contador se queda igual, y
por un motivo distinto del original: **un consumidor nunca corre las sondas metamórficas de Oracle**,
así que es lo único que se lo diría si algún día vuelve a pasar.

## La regla que queda

Un hueco declarado no es un hueco medido. La declaración envejece con una estimación de su tamaño
que nadie vuelve a revisar, y las tres veces la estimación estaba corta.

**Cuando se declara un hueco, conviene declarar también qué se midió para creer que es chico.** Si
no se midió nada, eso también es un dato — y es el que dice que la apuesta se hizo a ciegas.
