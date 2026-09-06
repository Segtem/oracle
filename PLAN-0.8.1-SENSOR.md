# Plan 0.8.1 — que la evidencia venga del mundo

**Fecha:** 2026-09-05 · **Estado:** anotado, sin empezar
**El número es provisorio:** si esto agrega algo al lenguaje —una relación, una forma de declarar
frescura— sube la menor por `ESPECIFICACION.md` §0. Se decide en el corte, no ahora.

## Lo que Oracle prueba hoy, y lo que no

Todo lo que Oracle demuestra hoy es sobre **coherencia interna**: que un catálogo está bien escrito,
que sus medidas discriminan, que su corpus las fija. Nada de eso dice que el proyecto medido esté
bien, y hay tres hechos que lo muestran desde ángulos distintos:

- **LyraGASP declara en cada caso que su evidencia es sintética.** Nadie corrió los sensores contra
  los assets reales con el editor abierto. Sus medidas prueban que el catálogo es coherente — no que
  los assets del proyecto estén bien.
- **Jam tiene tres medidas universales en sombra**, y una de ellas es
  `la_medida_no_se_fija_solo_con_evidencia_fabricada`. Se mide, se informa, y no tumba la corrida.
- **El tutorial del sitio lo dice en su última línea**: mientras la evidencia se escriba a mano,
  esto prueba que el catálogo es coherente, no que el proyecto esté bien.

Los tres son el mismo hecho: **falta el sensor**.

## Por qué esto es más grande que un verbo nuevo

Un sensor no es código que Oracle pueda escribir por su cuenta. Vive en el dominio del consumidor,
lee cosas reales —un asset de Unreal, un árbol de archivos, una corrida— y produce filas. Oracle ya
tiene la mitad: `L−1` declara qué lee un sensor y con qué unidades, `L−2` declara qué leyó y si
sigue fresco. Lo que falta es que alguien lo conecte y que la evidencia **venga de ahí**.

El patrón ya está descrito en los consumidores: el sensor va partido en dos —una parte pura que se
testea sin abrir el editor, y un adaptador que habla con el motor y escribe la evidencia—. Eso es
diseño, no invención.

## Lo que hay que decidir

1. **¿Qué demuestra 0.8.1?** No alcanza con «hay un sensor». Tiene que quedar un caso con
   `procedencia: observada` cuya evidencia haya salido de una corrida real, y que hoy no exista.
2. **¿Qué pasa con las sombras de Jam?** Si la evidencia real entra, ¿se pueden apagar? ¿O revelan
   que esas tres medidas piden algo que un consumidor no puede dar todavía?
3. **¿Cómo se comprueba que una evidencia es realmente observada?** Hoy es una declaración y nadie
   la verifica — el propio `alcance` de la medida que la vigila lo admite. `L−2` tiene la huella y
   la frescura; la pregunta es si eso alcanza para distinguir una corrida de una transcripción.

## Lo que no hay que hacer

**Declarar `observada` una evidencia transcrita a mano.** Es la mentira más barata del proyecto y la
que nadie puede detectar. Si el sensor no corre, la evidencia es `construida` y se dice.
