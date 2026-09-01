# Plan 0.3.0 — bibliotecas de políticas y la documentación de punta a punta

**Escrito el 2026-08-31**, el día que el repositorio se abrió y `0.2.0` salió a PyPI.

Dos frentes que no se tocan entre sí, más una deuda de `0.2.0` que hay que pagar primero.

---

## 0. Antes de nada: `0.2.1`

**El servidor LSP no arranca sin proyecto.** `oracle-lsp` sale con código 1 si no resuelve uno.
Los editores lo invocan sin argumentos y le pasan la carpeta abierta: con una carpeta de proyecto
funciona, con un `.oracle` suelto se apaga y no hay diagnósticos — sólo una línea en un registro
que nadie mira.

Es el primer tropiezo posible de alguien que acaba de instalar el paquete, y `0.2.0` ya está
publicado y no se puede reemplazar.

**Lo que hay que hacer:** que el servidor sirva igual sin proyecto, dando lo que no depende de uno
—errores de sintaxis, medida mal declarada— y degradando sólo lo que sí: `SIN FIJAR`, el CodeLens
y el completado de ids del catálogo. Que lo diga en la respuesta de `initialize`, no en silencio.

Cambia el contrato del servidor: `Proyecto` pasa a ser opcional y hay que hilarlo por
`diagnosticar`, `completar` y `lentes`. Con tests para las dos situaciones y mutación en cero.

---

## 1. Bibliotecas de políticas

La dirección está aceptada en [`DECISION-007`](DECISION-007-BIBLIOTECAS-DE-POLITICAS.md), con
**seis correcciones sin aplicar**. Hay un prototipo en la rama `propuesta-biblioteca`
(`nucleo/biblioteca.py`, 298 líneas, más su ejemplo y sus tests).

Los cinco invariantes no se negocian. El primero por encima de todos: **descubrir una biblioteca
lee datos y NUNCA importa un módulo ajeno.** Cargar una medida no ejecuta Python, y una biblioteca
no puede ser la puerta por la que eso cambie.

### Las seis correcciones, en orden de dependencia

| | corrección | por qué primero o después |
|---|---|---|
| **1** | Una biblioteca publica su número de `tools/mutar.py` o no se certifica | independiente; se puede empezar por acá |
| **3** | `listar` muestra umbral, `segun` y **`alcance` completo** por medida | independiente, y es la defensa real de la 5 |
| **5** | Ver el aflojamiento — un `<= 5` donde el resto tiene `<= 0` | **depende de la 3**; sin el listado, el prefijo sólo documenta la puerta |
| **2** | `procedencia` cruzando la frontera del paquete | **la más difícil, y hay que decidirla antes de la primera versión** |
| **4** | Modo sombra: se evalúa y se reporta, no falla | depende de que exista la carga |
| **6** | Telemetría: **sólo la fase 1**, diagnóstico local, sin red | último |

### La corrección 2 es la que puede hundir el diseño

Una biblioteca trae su corpus, y esos casos declaran `procedencia: observada` con `origen: {repo,
commit}` **de otro repositorio**. Al cargarla, `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`
evalúa casos de un tercero y me informa si *sus* medidas están bien fijadas. Eso probablemente no
es lo que quiero saber.

No es hipotético: el 2026-08-30 un caso de este repo transcribió una huella verdadera de
`Brianholl/jam` y la declaró bajo `repo: "Segtem/oracle"` (corregido en `corpus/meta/428`). Con
bibliotecas, eso deja de ser un descuido y pasa a ser la operación normal.

**Decisión requerida antes de escribir la carga:** la relación `caso` gana un campo que diga de qué
biblioteca viene, y cada medida meta que evalúa el corpus declara si mira lo propio, lo ajeno o
todo. Hoy la pregunta ni se puede formular.

### Lo que `DECISION-007` dice y ya no es cierto

La corrección 6 justifica descartar las fases 3 y 4 de telemetría porque piden servidor y política
de retención «para un proyecto que es **privado a propósito** y cuya decisión de publicar está
diferida». Desde el 2026-08-31 el repositorio es público y está en PyPI
([`DECISION-008`](DECISION-008-EL-REPOSITORIO-SE-ABRE.md)).

**La conclusión no cambia** —el costo estructural sigue ahí— pero el argumento sí. Hay que
reescribir ese párrafo antes de aplicar la corrección 6, en vez de dejar una decisión sostenida por
un hecho que dejó de ser verdad.

Lo mismo con la fase 2 (`oracle bug preparar`), aceptada «cuando exista alguien más que el autor
usando Oracle». Ahora se puede instalar con una línea, así que esa condición puede cumplirse sin
que nadie avise. Conviene definir cómo se sabría.

---

## 2. La documentación de punta a punta

Hoy hay **2.203 líneas** en cuatro documentos —README, especificación, tutorial práctico, cómo
escribir una medida— y ninguno es un camino. Están escritos para quien ya sabe qué es esto.

### La regla que gobierna este frente

**Una sola fuente por documento.** El sitio no puede reescribir lo que ya existe: esta semana
corregimos tres copias de «está ejercitada» y dos de la extensión de VS Code. Duplicar la
documentación para que se vea linda es garantizar que se desincronice.

Por eso los `.md` canónicos **se mudan a `docs/`** y GitHub Pages los renderiza. `docs/index.html`
—la portada— se queda como está; Jekyll deja pasar los `.html`. Desde la raíz quedan enlaces, no
copias.

### El camino que falta

Ordenado por la pregunta que contesta, no por el tema:

1. **Qué problema resuelve** — Goodhart, y por qué una regla tiene que negarse. *(existe en el README)*
2. **Instalar y ver algo funcionando en cinco minutos** — `pip install`, `oracle init`, una medida, un rojo. *(falta como camino continuo)*
3. **Anatomía de una medida** — los cinco operadores, `umbral`/`segun`, `alcance`, testigos. *(existe disperso)*
4. **Escribir el primer caso** — polaridad, `etiqueta`, `procedencia`, por qué hacen falta las dos. *(parcial)*
5. **Por qué la mutación** — «una medida que nada puede romper es decoración», leído desde un sobreviviente real. *(falta)*
6. **Los cinco niveles** — de L−2 a L2, con un ejemplo de cada uno. *(existe en `DECISION-005`, no como guía)*
7. **Conectar Oracle a un proyecto propio** — sensor puro / adaptador, relaciones, escalares y su aislamiento. *(falta, y es lo que más se va a preguntar)*
8. **El editor** — instalar la extensión, qué muestra cada cosa. *(existe en `editores/README.md`)*
9. **Referencia** — la especificación, sin cambios. *(existe)*

Los pasos **2, 5 y 7** son los que hay que escribir de cero. El resto es reordenar y coser.

### Cómo se verifica que la documentación no miente

Éste es un proyecto sobre medidas: la documentación se somete a la misma vara.

- **Todo comando que aparezca se ejecuta**, en un venv limpio, desde el paquete de PyPI. Si un
  bloque de código no se corrió, no entra. Es exactamente lo que atrapó el
  `pip install oracle-metalenguaje` inventado en la portada, antes de publicarla.
- **Ningún enlace roto**, comprobado en los dos sentidos como se hizo con el README.
- **Ningún dato fabricado.** Las cifras se cuentan el día que se escriben y se dice cuándo.

---

## 3. Reparto

| quién | qué | por qué |
|---|---|---|
| **codex** | Bibliotecas: correcciones 1, 3 y 5, sobre el prototipo | El bloque de ingeniería más grande, y ya trabajó L−1 y L−2 |
| **agy** | Documentación: pasos 2, 5 y 7, más la mudanza a `docs/` | Trabajo de redacción, no toca el núcleo |
| **acá** | `0.2.1`, la corrección 2, integración y verificación | La 2 es una decisión de diseño, no una tarea |

### Las condiciones, que no son negociables

Vienen de esta historia, no de la desconfianza en general.

**Nada entra sin pasar el arnés.** `corpus.py`, `aceptacion.py` y `mutar.py` sobre lo tocado, con
el número escrito en el commit. Un cambio que no reporta su número no se integra.

**La evidencia no se fabrica.** El 2026-08-30 se cerraron dos rojos con casos que declaraban
`procedencia: observada` sobre filas que ninguna corrida produjo (revertidos; el incidente está en
`corpus/meta/420`). Un caso `observada` nombra una corrida que existió. Ante la duda: `construida`,
que es honesto y no cierra nada que no deba cerrarse.

**Un sobreviviente se mira antes de taparlo.** La pregunta es *por qué este cálculo no se observa*.
En las rondas de esta semana, 7 de 13 sobrevivientes terminaron en **borrar código**, no en escribir
tests.

**Lo que se decide se escribe donde se pueda leer.** El `CLAUDE.md` afirmó durante meses que una
decisión estaba «registrada con fecha en `COMPROMISOS.json`»; ese archivo nunca existió.

---

## 4. Lo que NO entra en 0.3.0

- **Marketplace de VS Code y Open VSX.** Diferido unos días por decisión del 2026-08-31. El `.vsix`
  del release funciona hoy y no necesita cuentas.
- **Los 114 mutantes vivos de `tools/medida.py`.** Deuda de la superficie de la CLI, anterior y
  declarada. Ésta fue además la primera ronda **completa** de ese módulo: las anteriores se cortaban
  cerca de los 120 sitios sin decirlo, así que la cifra vieja de «115 sitios · 67 vivos»
  subestimaba el tamaño real, que son 264 sitios.
- **Telemetría más allá de la fase 1.**
