# La implementación de referencia — qué vio y qué no

`evaluador.py` es una implementación independiente del álgebra, escrita para poblar la pata que
`vault-kb/planes/PLAN-LENGUAJE.md` (e.2) declaraba estructuralmente vacía. El requisito real de esa sección no es
«otro código»: es **otro autor**. Por eso lo que importa acá no es el código sino esta declaración.

## Procedencia

- **Autor:** Codex CLI (`gpt-5.5`, reasoning `xhigh`), invocado el 2026-08-24 desde un directorio
  aislado fuera de este repositorio.
- **Archivos que vio, y son todos:** `ESPECIFICACION.md`,
  `docs/decisiones/DECISION-001-RELACIONES-COMO-BOLSAS.md`, `docs/decisiones/DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md`, y un
  `CONTRATO.md` que fijaba únicamente la firma pública (`evaluar`, `ErrorDeAlgebra`) y las reglas
  duras ya publicadas en la especificación.
- **Lo que NO vio:** `nucleo/` completo —en particular `algebra.py` y `medida.py`—, los 391 tests,
  el corpus, los catálogos, las macros y cualquier fixture. El directorio de trabajo contenía sólo
  los cuatro archivos de arriba; la instrucción prohibía explícitamente leer fuera de él.
- **Sin tests provistos.** `test_evaluador.py` son los tests que escribió por su cuenta: parte del
  ejercicio era ver qué prueba alguien que sólo leyó la especificación.

## Por qué esta declaración es el artefacto, y no el código

Una implementación escrita mirando `nucleo/algebra.py` no es independiente de nada, y desde afuera
las dos se ven igual. Lo único que separa un diferencial real de uno decorativo es qué fuentes vio
el segundo autor, y eso no se puede verificar leyendo el resultado: hay que declararlo.

Se escribieron tres implementaciones independientes en paralelo (Codex, Agy y DeepSeek V4 Pro), con
el mismo material y la misma prohibición. Ésta es la que se versiona porque documentó más
ambigüedades de la especificación —siete, cada una citando la sección que quedó abierta, en
[`DECISIONES.md`](DECISIONES.md)— y porque no filtró excepciones fuera del contrato. Las otras dos
sirvieron para algo distinto y más valioso: donde las tres se dividen **entre sí**, lo que falla no
es una implementación, es la especificación.

## Qué encontró el diferencial, y qué clase de cosa es cada hallazgo

Sobre los 39 casos del corpus, las cuatro implementaciones coinciden en todo. Eso **no** es una
buena noticia: significa que el corpus no formula ninguna pregunta difícil. Los desacuerdos
aparecieron recién con sondas dirigidas a los rincones que los propios autores declararon ambiguos,
y se separan en tres clases que no hay que confundir:

1. **La especificación no decide** — las implementaciones independientes se dividen entre sí:
   `min`/`max` con `int` y `float` mezclados; `["==", <número>, <texto>]` (dos de tres devuelven un
   verde silencioso); el cortocircuito de `y`/`o`.
2. **`nucleo/` contra todas** — `["==", <float>, <int>]`: las tres lo permiten, `nucleo/` lo
   prohíbe. Acá `nucleo/` es el más seguro y el hueco es de la especificación, que prohíbe la
   igualdad entre flotantes sin decir qué pasa cuando un solo lado lo es.
3. **Bugs de contrato de las implementaciones** — excepciones crudas que se escapan de
   `ErrorDeAlgebra`, o formas de `agrupar` aceptadas de más.

Sólo la clase 3 es un defecto de la referencia. Las clases 1 y 2 son deuda de la especificación, y
son el producto que se buscaba: el diferencial no existe para tener dos evaluadores, sino para que
los desacuerdos digan dónde el documento no alcanzaba.

## Re-derivación contra el álgebra 0.7 (2026-09-15)

- **Autor:** Agy (Antigravity CLI, Gemini `gemini-3.8-flash-high`), en una conversación y un proyecto
  **nuevos** —`--new-project`, sin la conversación que implementó 0.21.0 en el núcleo—, con
  `workspaceDirs` confinado a un directorio temporal fuera de este repositorio (verificado en el log
  del CLI). Agy fue uno de los tres autores independientes de 2026-08-24.
- **Archivos que vio, y son todos:** `ESPECIFICACION.md` ya actualizada con el `requiere` con condición
  y las relaciones con variantes; `DECISION-001` y `DECISION-002`; esta implementación, sus tests y
  `DECISIONES.md`; y un `CONTRATO.md` con la firma pública (`evaluar`, `ErrorDeAlgebra`,
  `VERSION_ALGEBRA`) y las reglas. No se le dijo qué había cambiado.
- **Por qué no Codex:** el autor original quedó sin cuota hasta el 2026-09-19; el dueño eligió Agy
  aislado antes que esperar o usar un subagente de Claude, que escribió la especificación.
- **Sin ejecutar nada:** el modo sin interfaz le negó la shell, así que escribió `evaluador.py`,
  `test_evaluador.py` y `DECISIONES.md` sin correrlos; los tests los corrió Claude después, sin tocar el
  código.
- **Qué encontró:** dos puntos que la especificación no decidía, y en los dos el núcleo estaba mal
  (clase 1 que resultó también clase 2): la condición de `requiere` tiene que evaluarse en **todas** las
  filas, sin cortocircuito, para que el orden de la bolsa no cambie el veredicto; y un error de una
  condición no puede quedar tapado porque otra relación requerida venga vacía. El núcleo se corrigió y
  la especificación §2 ahora lo dice.

## Re-derivación contra el álgebra 0.8 (2026-09-16)

- **Autor:** Agy (Antigravity CLI), otra vez en una conversación y un proyecto **nuevos**
  —`--new-project`, sin la conversación que implementó `sin` en el núcleo—, con `workspaceDirs`
  confinado a un directorio temporal fuera de este repositorio (verificado en el log del CLI, que
  no nombra el repositorio una sola vez).
- **Archivos que vio, y son todos:** `ESPECIFICACION.md` ya con `sin` en §3 y §8; `DECISION-001` y
  `DECISION-002`; esta implementación, sus tests y `DECISIONES.md`; y el contrato de
  [`vault-kb/estudios/0.26.0-antijunta/referencia/`](../../vault-kb/estudios/0.26.0-antijunta/referencia/CONTRATO.md),
  con las huellas de la entrada al lado. No se le dijo qué había cambiado.
- **Sin ejecutar nada**, como en 0.7: escribió el código, 21 tests nuevos y nueve decisiones sin
  correrlos; los 41 tests los corrió Claude después, sin tocar el código, y pasaron.
- **Qué encontró:** su resumen está en `FIN-AGY.md`, junto al contrato. En los 10 mundos del
  fixture coincide con el núcleo en las 8 medidas, incluidas las tres que pasan por `sin`. Las
  sondas dirigidas a sus nueve decisiones nuevas dieron cuatro desacuerdos, de las tres clases:
  1. **El núcleo contra la especificación** — el núcleo aceptaba un `unir` a la derecha de `sin`;
     §3 dice `["de", relación, alias]`. Se corrigió el núcleo.
  2. **La especificación no decidía** — un alias repetido cuando no llega ninguna fila (el núcleo lo
     rechaza al validar, la referencia sólo al ver una fila), y un alias que coincide con una
     columna de `agrupar` (la referencia lo rechaza). §3 ahora decide los dos como el núcleo, y en
     esos dos rincones esta referencia queda en desacuerdo con el documento; ningún mundo del
     fixture pasa por ahí.
  3. **Anterior a 0.8** — un predicado que no da booleano: el núcleo lo toma por su verdad, la
     referencia levanta. Pasa igual con `donde`, así que no es de `sin`; es la tarea
     `20260916-202010-predicado-bool`.
