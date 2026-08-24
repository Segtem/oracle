# La implementación de referencia — qué vio y qué no

`evaluador.py` es una implementación independiente del álgebra, escrita para poblar la pata que
`PLAN-LENGUAJE.md` (e.2) declaraba estructuralmente vacía. El requisito real de esa sección no es
«otro código»: es **otro autor**. Por eso lo que importa acá no es el código sino esta declaración.

## Procedencia

- **Autor:** Codex CLI (`gpt-5.5`, reasoning `xhigh`), invocado el 2026-08-24 desde un directorio
  aislado fuera de este repositorio.
- **Archivos que vio, y son todos:** `ESPECIFICACION.md`,
  `DECISION-001-RELACIONES-COMO-BOLSAS.md`, `DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md`, y un
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
