# Migrar LyraGASP a Oracle desde PyPI

Leé primero [`de-subtree-a-pypi.md`](de-subtree-a-pypi.md): el procedimiento está ahí. Acá está sólo
lo que se **midió** de este repositorio el 2026-09-01, corriendo el Oracle de hoy contra
`~/Dev/games/unreal/LyraGASP/medidas`.

> ⚠️ **Este repo tenía 47 archivos con trabajo sin commitear del usuario** al medirlo, todos dentro
> de `medidas/` (medidas y casos de `ml_deformer` y `recarga`, varios con evidencia real). No corras
> `git stash`, `git clean`, `git checkout .` ni `git reset`. Si algo parece necesitarlo, preguntá.

## Lo que se midió

| | |
|---|---|
| ediciones locales en `vendor/oracle` | **ninguna** — el subtree se puede borrar sin perder nada |
| catálogo | 9 archivos · corpus 26 · fixtures diferenciales 3 |
| `oracle-corpus` con el Oracle de hoy | **CORPUS OK · 26 casos** |
| `oracle-aceptacion` con el Oracle de hoy | **sale 1**: 3 medidas en rojo, 34 infracciones |

`medidas/oracle.json` declara `"catalogo_base": true` y `"perfiles": []`.

## Los tres rojos, y cuántas infracciones tapa cada sombra

| medida | infracciones | qué encontró |
|---|---|---|
| `meta.toda_cantidad_comparada_tiene_unidad_derivable` | **16** | comparaciones cuya unidad no se puede derivar: falta declarar los campos en `relaciones/` |
| `meta.todo_umbral_declara_de_donde_sale` | **9** | umbrales sin `segun`: son anteriores a que ese campo existiera |
| `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` | **9** | medidas cuyos casos son todos `construida` o `generada` |

Ninguno es una regresión: son medidas que el Oracle del subtree **no tenía**.

## El bloque de sombra

Va en `medidas/oracle.json`. Verificado sobre una copia: con esto la aceptación sale **0**.

```json
{
  "esquema": "oracle.proyecto/v1",
  "catalogo_base": true,
  "perfiles": [],
  "sombra": {
    "meta.toda_cantidad_comparada_tiene_unidad_derivable": {
      "desde": "2026-09-01",
      "porque": "16 comparaciones sin unidad derivable; hay que declarar los campos de las relaciones de UE en relaciones/, y se hace por relación, no de golpe"
    },
    "meta.todo_umbral_declara_de_donde_sale": {
      "desde": "2026-09-01",
      "porque": "9 umbrales anteriores a que existiera `segun`; cada uno necesita que alguien diga de dónde salió el número, y eso no se completa adivinando"
    },
    "meta.la_medida_no_se_fija_solo_con_evidencia_fabricada": {
      "desde": "2026-09-01",
      "porque": "9 medidas fijadas sólo con evidencia construida; se cierran corriendo los sensores contra los assets reales con el editor abierto, que es trabajo con Unreal y no de escritorio"
    }
  }
}
```

**La tercera es la que más pronto se puede cerrar** y conviene decirlo: este repo ya tiene casos con
evidencia real (`008-default-slot-real`, `010-region-pelvis-rigida-real`, …), así que el camino está
abierto — falta hacerlo para las nueve.

## Ojo: hay un script que IMPORTA el paquete

`tools/juzga_oracle.py:11-15` pone `vendor/oracle` en su `sys.path` y después hace
`from oracle_metalenguaje import Motor`. Se corre con el Python del sistema, así que
`uv tool install` **no** se lo da: instala en un entorno aislado que expone los ejecutables y nada
más. Para ese script hace falta la forma **(b)** de la guía general:

```bash
uv venv && uv pip install "oracle-metalenguaje==0.3.2"
.venv/bin/python tools/juzga_oracle.py …
```

Y ahí las tres líneas del `sys.path.insert` se BORRAN: con el paquete instalado, el import anda solo.

`medidas/escalares.py` también importa `oracle_metalenguaje`, y ése **no es problema**: lo ejecuta
Oracle en un subproceso aislado con su propio intérprete, donde el paquete siempre está.

A diferencia de Jam, LyraGASP **no tiene** código que corra dentro del Python embebido de Unreal, así
que no hace falta vendorizar el wheel.

## Lo que nombra `vendor/oracle` y hay que cambiar

| archivo | qué dice |
|---|---|
| `tools/juzga_oracle.py:11-15` | **CÓDIGO**: el `sys.path.insert`, que se borra |
| `docs/ORACLE.md:3` | explica que `vendor/oracle/` es un subtree — hay que reescribir la sección |
| `docs/ORACLE.md:14-16` | los tres comandos `python vendor/oracle/tools/…` |
| `docs/ORACLE.md:26` | la sección «No edites `vendor/oracle/` a mano», que deja de aplicar |
| `docs/ORACLE.md:31` | el `git subtree pull`, que se reemplaza por `uv pip install` con la versión nueva |

No hay CI que lo referencie.

## Al terminar

```bash
oracle-corpus     --proyecto medidas
oracle-aceptacion --proyecto medidas --confiar-escalares   # tiene que salir 0
oracle-mutar      --proyecto medidas --confiar-escalares
```

Y actualizá `docs/ORACLE.md` con lo que quedó, incluida la lista de sombras y por qué está cada una.
