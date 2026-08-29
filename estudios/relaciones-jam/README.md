# Once relaciones de Jam, declaradas (2026-08-28)

Entregable para **copiar a `~/Dev/jam/medidas/relaciones/`** cuando el usuario quiera. No son
relaciones de Oracle y por eso no están en `relaciones/`: `tools/aceptacion.py` sólo lee ese
directorio, así que esto no cambia el nivel meta de este repo.

## Por qué existen

Medido el 2026-08-28: **los consumidores tienen cero relaciones declaradas.** Jam usa 22 relaciones
distintas en sus 41 medidas y no declaró ninguna; LyraGASP tampoco. Mientras siga así, L−1 existe en
el lenguaje y no en el mundo.

La primera tanda declaró seis —no las 22— eligiendo aquellas donde una confusión de centímetros,
grados o centímetros cúbicos puede cambiar un veredicto:

| | campos | unidades |
|---|---:|---|
| `pieza` | 11 | cm · grados · sin_unidad |
| `objetivo` | 12 | cm · grados · sin_unidad |
| `instancia` | 11 | cm · grados · sin_unidad |
| `asentada` | 14 | cm · grados · sin_unidad |
| `solido_malla` | 3 | cm3 · sin_unidad |
| `cobertura_scatter` | 3 | sin_unidad |

La segunda tanda partió de una medición real de las 41 medidas de Jam: **89 cantidades comparadas,
41 derivables y 48 no derivables**. Declaró las cinco relaciones que más no derivables cubrían:

| | cantidades que pasó a derivables | unidad física | emisor real |
|---|---:|---|---|
| `documento` | 10 | ninguna | `tools/emitir_hechos_vault.py:67-95` |
| `reemplazo` | 5 | cm | `Content/Python/jam/oracle_reemplazo_facts.py:6-16` |
| `agente` | 4 | ninguna | `tools/emitir_hechos_relevo.py:158-163` |
| `espacio` | 3 | ninguna | `Content/Python/jam/oracle_espacio_facts.py:74-82` |
| `asentamiento` | 3 | cm | `Content/Python/jam/oracle_physics_facts.py:6-28` |

Después de cargarlas con el productor de L−1, la misma corrida quedó en **66 derivables y 23 no
derivables**: la tanda bajó el rojo visible en 25, sin modificar Jam.

La medición queda reproducible desde la raíz de Oracle:

```bash
python estudios/relaciones-jam/medir.py /home/workstation/Dev/jam
```

Los 23 restantes explican por qué se detuvo acá en vez de declarar las 16 relaciones faltantes de
un saque: 14 aparecen en relaciones ya declaradas y dependen de escalares de Jam que todavía no
declaran `unidades_argumentos`; otras 9 corresponden, una por cantidad, a `cara_malla`,
`superficie_malla`, `testigo_campo`, `testigo_seccion`, `verificacion`, `conteo_scatter`,
`spline_modular`, `junta_spline` y `enlace`. Ninguna declaración de relación puede cerrar las
primeras 14 por sí sola.

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
- `cm` para `reemplazo.d_*` y `asentamiento.gap`: ambos emisores restan exclusivamente orígenes y
  semi-extensiones de `geometry.AABB`; la fuente sigue siendo el comentario de `geometry.py:14`, no
  una declaración ejecutable. El objetivo de reemplazo se forma desde el mismo AABB en
  `reemplazar.py:25-32`. `documento`, `agente` y `espacio` sólo publican textos, booleanos y
  conteos, y por eso se declararon explícitamente `sin_unidad`.

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

Las once cargan con `nucleo.relacion.cargar_relaciones`. Las cinco nuevas se cruzaron además contra
filas producidas por los emisores reales: los conjuntos de campos coincidieron exactamente para
`documento`, `reemplazo`, `agente`, `espacio` y `asentamiento`. Las afirmaciones anteriores sobre
los sensores también se comprobaron contra la fuente de Jam, una por una: los emisores existen,
`asentada` no trae `gap`, y el comentario de `cm` está en `geometry.py:14`. La comprobación no es
ceremonia: el 2026-08-27 un agente cerró un rojo transcribiendo filas que ninguna corrida había
producido, y quedó registrado en `corpus/meta/420`.

Agy hizo una clasificación independiente y reprodujo tanto el orden `10 + 5 + 4 + 3 + 3` como el
piso de 14 deudas escalares. No editó producción, relaciones ni tests; la medición final y las
corridas de emisores se ejecutaron desde esta rama.
