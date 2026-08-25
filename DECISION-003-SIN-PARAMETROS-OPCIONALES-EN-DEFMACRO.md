# Decisión 003 — `defmacro` no tiene parámetros opcionales

**Estado:** revertida la capacidad el 2026-08-24 (commit `d2532fa`, que revierte `eb9ad40`).

## Contexto

`requiere` entró al lenguaje el 2026-08-24 para cerrar el falso verde de la ausencia: una medida
declara qué relaciones **necesita** para concluir, y el evaluador falla cerrado —`SIN EVIDENCIA`—
antes de medir si alguna falta. Es el espejo de `alcance`.

De las 30 medidas universales, **25 pasan por la macro `ninguno`** y **5 declaran `requiere`**. Esas
cinco están escritas a mano con `desde` en vez de con la macro, y el motivo parecía obvio: la
plantilla de `ninguno` no emite un nodo `requiere`, y agregárselo obligaría a las 25 a declarar uno.

De ahí salió el pedido: que `defmacro` acepte **parámetros opcionales con valor por defecto**, para
que `ninguno` pudiera emitir `requiere` sólo cuando el uso lo pasara. Se delegó, se implementó
(+23 líneas de núcleo en `nucleo/macro.py`, con sus tests) y se integró.

## Decisión

**Se revierte.** `defmacro` sigue teniendo aridad fija y sin valores por defecto.

## Por qué

### 1 · La cadena completa costaba mucho más que el primer eslabón

Los parámetros opcionales son el primero de tres eslabones. Para que `ninguno` emitiera `requiere`
de verdad hacían falta además:

- **splice** — `requiere` es variádico (`["requiere", "a", "b"]`, no `["requiere", ["a","b"]]`), así
  que una lista de relaciones tiene que **abrirse** dentro del nodo. `defmacro` sustituye `$`
  posición por posición y no sabe abrir nada.
- **omisión condicional** — un parámetro con valor por defecto emite igual el nodo. Para que una
  medida sin precondición no publique un `["requiere"]` vacío, la plantilla tiene que poder **no
  emitir** una rama.

Estimado en unas 50 a 70 líneas de núcleo para las dos, sobre las 23 ya gastadas. El
[plan](PLAN-LENGUAJE.md) publica la proporción de falsación —líneas de lenguaje contra líneas de
medida— como el costo declarado del proyecto, y esto la empeoraba sin agregar una sola medida.

### 2 · El caso real no necesita nada de eso — y se comprobó

Las cinco medidas que declaran `requiere` lo declaran **con una sola relación**, y en las cinco esa
relación es la misma que la medida ya recorre con `de`. Una macro puede emitir eso hoy, con **cero
líneas de núcleo**, reusando el parámetro `relacion` que ya recibe:

```json
["defmacro", "ninguno-si-hay",
  ["id", "relacion", "alias", "predicado", "porque", "alcance"],
  [],
  ["medida", ["$", "id"],
    ["desde", ["de", ["$", "relacion"], ["$", "alias"]], ["donde", ["$", "predicado"]]],
    ["resumen", "contar", 1],
    ["umbral", "<=", 0, ["$", "porque"]],
    ["requiere", ["$", "relacion"]],
    ["alcance", ["$", "alcance"]]]]
```

Verificado: expande y carga como `Medida` con `requiere == ("corrida",)`. Una macro **hermana** de
`ninguno`, declarada como datos en `nucleo/macros/`, cubre el caso entero sin tocar el expansor.

Que la solución barata existiera desde el principio y no se hubiera buscado es el error de
procedimiento acá, y no el de quien implementó lo que se le pidió.

### 3 · La regla propia del repositorio

**Nada entra al lenguaje hasta que una medida real lo necesite.** Ninguna de las 30 medidas
universales necesita un parámetro opcional; las cinco que motivaron el pedido se cubren con una macro
de aridad fija. Es el mismo disparador que retiró `con` y la unión izquierda, y el mismo que mantiene
afuera la composición de medidas ([`DECISION-002`](DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md)).

## Consecuencias

- `defmacro` sigue siendo lo más chico que sirve: aridad fija, sustitución posicional, sin defaults.
  Una macro que necesita dos formas se escribe como **dos macros**, que es más líneas de datos y
  menos líneas de núcleo — el intercambio que el proyecto declara buscar.
- Las cinco medidas con `requiere` siguen escritas a mano. No es deuda: son cinco, y ninguna repite a
  otra. La macro hermana se escribe cuando haya un patrón, no antes.
- Queda anotado que **el primer eslabón de una cadena se mide por la cadena entera**. Integrar los
  parámetros opcionales solos habría dejado núcleo muerto: una capacidad en el expansor que ninguna
  macro usa y que ningún test de medida ejercita.

## Qué evidencia revierte esta decisión

**Dos macros reales** —en el núcleo o en un proyecto consumidor— que sólo se puedan escribir
duplicando la plantilla entera por una sola rama variable, y donde la duplicación ya haya producido
una divergencia entre las dos copias.

Dos, no una: una macro duplicada es barata de mantener; dos que divergieron son la prueba de que la
duplicación no se sostiene. Y si entra, tiene que entrar **con splice y omisión condicional en el
mismo movimiento**: por separado, el primer eslabón no expresa ningún caso.
