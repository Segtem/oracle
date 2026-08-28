# Seis relaciones de Jam, declaradas (2026-08-28)

Entregable para **copiar a `~/Dev/jam/medidas/relaciones/`** cuando el usuario quiera. No son
relaciones de Oracle y por eso no están en `relaciones/`: `tools/aceptacion.py` sólo lee ese
directorio, así que esto no cambia el nivel meta de este repo.

## Por qué existen

Medido el 2026-08-28: **los consumidores tienen cero relaciones declaradas.** Jam usa 22 relaciones
distintas en sus 41 medidas y no declaró ninguna; LyraGASP tampoco. Mientras siga así, L−1 existe en
el lenguaje y no en el mundo.

Se declararon seis —no las 22— eligiendo aquellas donde una confusión de centímetros, grados o
centímetros cúbicos puede cambiar un veredicto:

| | campos | unidades |
|---|---:|---|
| `pieza` | 11 | cm · grados · sin_unidad |
| `objetivo` | 12 | cm · grados · sin_unidad |
| `instancia` | 11 | cm · grados · sin_unidad |
| `asentada` | 14 | cm · grados · sin_unidad |
| `solido_malla` | 3 | cm3 · sin_unidad |
| `cobertura_scatter` | 3 | sin_unidad |

## El agujero que esto documenta

**Ninguna de esas unidades está declarada en el código del sensor.** Todas se dedujeron leyendo la
fuente, y cada deducción quedó anotada con su origen:

- `cm` para posiciones y extensiones: `geometry.py:14` lo dice en un comentario —
  `AABB = namedtuple("AABB", "origin extent")   # origin, extent: Vec3, en cm`. Un comentario, no una
  declaración: nada lo comprueba y nada lo propaga a la fila emitida.
- `grados` para `yaw`: sale de `get_actor_rotation().yaw` de Unreal.
- `cm3` para `volumen_orientado`: **la más débil, y está marcada como tal**. No hay unidad escrita en
  `oracle_malla_facts.py`; se deduce dimensionalmente y se confirma con un experimento del propio
  repo —una caja de 200×140×90 da volumen orientado 2.520.000, que es exactamente cm×cm×cm—.

Eso es precisamente lo que L−1 viene a cerrar: hoy la unidad vive en un comentario, en el nombre de
una función de Unreal, o en la cabeza de quien escribió el sensor.

## Dos hallazgos de leer los sensores

1. **Los cuatro archivos que la tarea señalaba no eran los emisores.** `oracle_placement.py`,
   `oracle_snap.py`, `oracle_physics.py` y `oracle_reemplazo.py` son oráculos de *veredicto*:
   devuelven estados y decisiones, no filas L0 con nombre de relación. Las filas salen de `_plano` en
   `oracle_shadow.py`, de `oracle_scatter_facts.py`, `oracle_physics_tanda_facts.py` y
   `oracle_malla_facts.py`. Leer sólo los cuatro señalados habría producido declaraciones
   incompletas.
2. **Dos sensores parecidos emiten relaciones distintas.** `oracle_physics_facts` emite
   `asentamiento` y ahí sí existe `gap`; `oracle_physics_tanda_facts` emite `asentada` y **no** lo
   emite. Verificado: 0 menciones de `gap` en el segundo archivo. El campo no se inventó en
   `asentada`.

## Verificado antes de aceptar

Las seis cargan con `nucleo.relacion.cargar_relaciones`. Las afirmaciones sobre los sensores se
comprobaron contra la fuente de Jam, una por una: los cuatro emisores existen, `asentada` no trae
`gap`, y el comentario de `cm` está en `geometry.py:14`. La comprobación no es ceremonia: el
2026-08-27 un agente cerró un rojo transcribiendo filas que ninguna corrida había producido, y quedó
registrado en `corpus/meta/420`.
