# Migrar Jam a Oracle desde PyPI

Leé primero [`de-subtree-a-pypi.md`](de-subtree-a-pypi.md): el procedimiento está ahí. Acá está sólo
lo que se **midió** de este repositorio el 2026-09-01, corriendo el Oracle de hoy contra
`~/Dev/jam/medidas`.

> ⚠️ **Este repo tenía 4 archivos con trabajo sin commitear del usuario** al medirlo. No corras
> `git stash`, `git clean`, `git checkout .` ni `git reset`. Si algo parece necesitarlo, preguntá.

## Lo que se midió

| | |
|---|---|
| ediciones locales en `vendor/oracle` | **ninguna** — el subtree se puede borrar sin perder nada |
| catálogo | 41 archivos · corpus 24 · fixtures diferenciales 11 |
| `oracle-corpus` con el Oracle de hoy | **CORPUS OK · 23 casos** |
| `oracle-aceptacion` con el Oracle de hoy | **sale 1**: 3 medidas en rojo, 104 infracciones |

`medidas/oracle.json` declara `"catalogo_base": true` y `"perfiles": ["python"]`.

## Tres deudas viejas que YA NO ESTÁN

El `CLAUDE.md` del usuario todavía las nombra, y al medir hoy resultaron cerradas. Si algo las
vuelve a mencionar, está desactualizado:

- ~~`medidas/corpus/scatter/004-coberturas-distintas.json` con el `id` desalineado~~ — `oracle-corpus`
  sale **0**.
- ~~`snap.al_ras`, `snap.comparte_cara` y `scatter.cobertura` sin `donde` ni `agrupar`~~ —
  `meta.toda_medida_filtra_o_agrupa` **no aparece** entre los rojos.
- ~~`medidas/diferencial/vault.json` vencido~~ — el corpus valida entero.

Lo que **no** se verificó en esta medición: si el corpus tiene casos `verde_correcto`. Sin verdes,
el mutador `quitar_filtro` sobrevive siempre y la mutación mide menos de lo que dice. Contalo con
`oracle-medida --listar` o mirando las etiquetas, y si sigue en cero, es la deuda que queda.

## Los tres rojos, y cuántas infracciones tapa cada sombra

| medida | infracciones | qué encontró |
|---|---|---|
| `meta.toda_cantidad_comparada_tiene_unidad_derivable` | **54** | comparaciones cuya unidad no se puede derivar: falta declarar los campos en `relaciones/` |
| `meta.todo_umbral_declara_de_donde_sale` | **41** | umbrales sin `segun`: son anteriores a que ese campo existiera |
| `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` | **9** | medidas cuyos casos son todos `construida` o `generada` |

Ninguno es una regresión: son medidas que el Oracle del subtree **no tenía**. Y el número grande
—54— no es casualidad: Jam tiene 41 archivos de catálogo, así que es el consumidor con más
superficie sin unidades declaradas.

## El bloque de sombra

Va en `medidas/oracle.json`. **Verificado corriendo la aceptación sobre una copia del proyecto**:
con esto sale `ACEPTACIÓN ✓ — 20 defectos en rojo, 3 verdes correctos, 0 huecos declarados sin
tapar`, salida **0**.

```json
{
  "esquema": "oracle.proyecto/v1",
  "catalogo_base": true,
  "perfiles": ["python"],
  "sombra": {
    "meta.toda_cantidad_comparada_tiene_unidad_derivable": {
      "desde": "2026-09-01",
      "porque": "54 comparaciones sin unidad derivable sobre 41 archivos de catálogo; declarar los campos en relaciones/ es trabajo por relación y no entra en el commit de la migración"
    },
    "meta.todo_umbral_declara_de_donde_sale": {
      "desde": "2026-09-01",
      "porque": "41 umbrales anteriores a que existiera `segun`; cada uno necesita que alguien diga de dónde salió el número, y completarlo adivinando sería peor que la falta"
    },
    "meta.la_medida_no_se_fija_solo_con_evidencia_fabricada": {
      "desde": "2026-09-01",
      "porque": "9 medidas fijadas sólo con evidencia construida; se cierran transcribiendo corridas reales de las sondas contra JamPlayground, que necesita el editor abierto"
    }
  }
}
```

## Lo que nombra `vendor/oracle` y hay que cambiar

| archivo | qué dice |
|---|---|
| `AGENTS.md:38` | explica que `vendor/oracle/` es un subtree |
| `AGENTS.md:43-45` | los tres comandos `python vendor/oracle/tools/…` |
| `AGENTS.md:53` | el `git subtree pull`, que se reemplaza por `uv tool upgrade` |
| `AGENTS.md:58` | «No edites `vendor/oracle/` a mano», que deja de aplicar |
| `AGENTS.md:167` | la misma advertencia en la tabla de errores |
| `RELEVO.md:541-546` | seis filas con comandos y cifras viejas; `RELEVO.md` se regenera con `python tools/relevo.py`, así que revisá si el generador es el que hay que tocar y no el archivo |

## Al terminar

```bash
oracle-corpus     --proyecto medidas
oracle-aceptacion --proyecto medidas --confiar-escalares   # tiene que salir 0
oracle-mutar      --proyecto medidas --confiar-escalares
oracle-diferencial --proyecto medidas --confiar-escalares
```

Jam tiene 11 fixtures diferenciales, así que `oracle-diferencial` sí tiene qué comparar — a
diferencia de LyraGASP. Actualizá `AGENTS.md` con lo que quedó, incluida la lista de sombras.
