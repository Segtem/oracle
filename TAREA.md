# Tarea — `oracle <sustantivo> <verbo>`, como docker, y el listado que falta

Leé `DOCTRINA.md` primero. Es obligatorio.

## De dónde sale el pedido

El dueño del proyecto preguntó si Oracle podría tener verbos como los tiene Docker. La respuesta es
que sí y que además **resuelve un hueco real y medido**: hoy no hay forma de ver un catálogo. Para
auditar diez medidas hay que abrir diez archivos.

Eso importa por el objetivo declarado: que una persona pueda **auditar** lo que escribió un modelo.

## Cómo está hoy

    oracle init · nueva · caso · revisar · test · relaciones · escalares · expandir · convertir

Nueve verbos planos, y mezclados: `nueva` y `caso` crean cosas, `revisar` y `test` juzgan,
`relaciones` y `escalares` listan. No se ve qué se puede hacer con qué.

## Lo que hay que construir

La estructura `oracle <sustantivo> <verbo>`, **conservando los verbos planos de hoy como atajo**.
Docker hace exactamente eso: `docker container run` es la forma canónica y `docker run` sigue
andando. La forma larga es para descubrir; la corta es para el camino de todos los días.

Un reparto posible, y podés discutirlo con argumento:

    oracle medida nueva <id>        (hoy `nueva`)
    oracle medida revisar <arch>    (hoy `revisar`)
    oracle medida listar            ← NUEVO
    oracle medida expandir <arch>   (hoy `expandir`)

    oracle caso nuevo <grupo/id>    (hoy `caso`)
    oracle caso listar              ← NUEVO

    oracle proyecto init [ruta]     (hoy `init`)
    oracle proyecto test            (hoy `test`)
    oracle proyecto relaciones      (hoy `relaciones`)
    oracle proyecto escalares       (hoy `escalares`)

    oracle convertir <arch>         (queda plano: no es de ningún sustantivo)

**Y `oracle medida` a secas, sin verbo, lista los verbos de ese sustantivo.** Es lo que hace
descubrible la estructura, y es la mitad del valor de esto.

### Los dos listados, que son lo nuevo de verdad

**`oracle medida listar`** es la vista de auditoría. Tiene que dejar juzgar sin abrir archivos: el
id, el umbral con su comparador, y algo del `alcance`. Pensá qué necesita ver alguien que revisa
diez medidas que escribió un modelo y decidí el formato con ese criterio; explicalo en el informe.

Dos cosas que sí o sí tiene que poder mostrar, porque son las que delatan una medida floja:

  · **cuáles no están fijadas por ningún caso** — una medida que ningún caso ejercita no mide nada, y
    hoy eso sólo se descubre corriendo la mutación;
  · **cuántos casos fijan cada una**.

**`oracle caso listar`**: id, etiqueta, qué medida reclama. Y marcar los que **no reclaman ninguna**
—los huecos declarados—, que ya son un concepto del proyecto.

Salida legible por una persona. Si te parece que hace falta `--json` para que la consuma un script,
agregalo y decilo; si te parece que no hace falta todavía, tampoco lo agregues: nada entra hasta que
alguien lo necesite.

## Cuidados

- **No rompas nada de lo que ya anda.** Los nueve verbos planos siguen funcionando igual, y los dos
  consumidores llaman `--proyecto medidas --confiar-escalares`. Hay tests que lo fijan.
- **No dupliques lógica.** `oracle medida nueva` y `oracle nueva` tienen que llamar a la misma
  función, no a dos copias.
- **`oracle <sustantivo>` sin verbo no es un error**: es la ayuda de ese sustantivo, y devuelve 0.
  Un verbo que no existe sí es error, y el mensaje tiene que decir cuáles hay.
- **Los tests del CLI no deben ensuciar la salida de la suite.** Usá el helper `_callado` de
  `tests/test_cli.py`. Ya pasó una vez que `unittest -q | tail -3` mostrara la ayuda en vez de «OK».
- No toques `nucleo/` salvo que sea imprescindible, y si lo es, explicá por qué.
- No toques `corpus/` ni `catalogos/`.
- No toques `vendor/`.

## Cómo sé que terminaste

1. Las dos formas andan, con la salida de ambas pegada en `INFORME.md`.
2. `oracle medida listar` sobre el propio Oracle —37 medidas— y sobre un proyecto recién creado.
   Pegá las dos: una vista de auditoría que sólo sirve con 37 medidas y no con 2 está mal pensada.
3. `oracle medida listar` marca las medidas que ningún caso fija. **Comprobalo creando una a
   propósito** en un proyecto de `/tmp`, y pegá la salida.
4. Las nueve verificaciones de `DOCTRINA.md` en verde.

Commiteá en tu worktree. No pushees.
