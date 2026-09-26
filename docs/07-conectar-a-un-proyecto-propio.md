# Conectar Oracle a un proyecto propio

[De cero a un rojo](02-de-cero-a-un-rojo.md) termina con un rojo honesto: toda tu evidencia era
`construida` a mano. Acá se cierra, escribiendo el sensor que produce evidencia **observada**.

Todo lo que sigue está copiado de una corrida real.

---

## La partición: el sensor no juzga

Oracle no lee tu mundo. Lee **filas**. Quien las produce es tuyo, y conviene partirlo en dos:

| | qué hace | cómo se prueba |
|---|---|---|
| **sensor** | decide, y nada más. Sin `open`, sin red, sin SDK | pasándole valores |
| **adaptador** | habla con el disco, la base o el motor. No decide nada | corriéndolo |

La razón no es estética. Un sensor que además abre archivos sólo se puede probar teniendo esos
archivos; separado, se prueba con strings. Y un adaptador que además decide esconde la decisión
donde nadie la revisa.

Es la misma partición que usan los dos consumidores reales de Oracle en producción:
- **Jam** (`~/Dev/jam`): plugin de Unreal Engine, 41 archivos de catálogo, 24 casos en corpus,
  11 fixtures diferenciales.
- **LyraGASP** (`~/Dev/games/unreal/LyraGASP`): proyecto de juego en Unreal Engine, 9 archivos de
  catálogo, 26 casos en corpus, 3 fixtures diferenciales.

Los dos migraron de un subtree de git al paquete publicado (`oracle-metalenguaje==0.3.3`) en PyPI.
Los detalles de qué se midió en cada uno están en [`docs/migracion/`](migracion/de-subtree-a-pypi.md).

## El sensor

Para reproducirlo desde una carpeta vacía, prepará el proyecto de biblioteca:

```bash paso
oracle init biblioteca
cd biblioteca
```

```text salida
Proyecto Oracle inicializado en ./biblioteca:
  · catalogos/
  · corpus/
  · diferencial/
  · relaciones/
  · oracle.json

Próximos pasos:
  1. Creá un caso:     oracle caso <grupo/id>
  2. Creá una medida:  oracle nueva <dominio.nombre>
  3. Verificá todo:    oracle test
```

```json archivo=oracle.json incluir=ejemplo/biblioteca-guia/oracle.json
```

```oracle archivo=catalogos/documento/documento.nombre_sigue_la_convencion.oracle incluir=ejemplo/biblioteca-guia/catalogos/documento/documento.nombre_sigue_la_convencion.oracle
```

```caso archivo=corpus/documento/001-un-nombre-fuera-de-convencion.caso incluir=ejemplo/biblioteca-guia/corpus/documento/001-un-nombre-fuera-de-convencion.caso
```

```caso archivo=corpus/documento/002-un-lote-en-convencion.caso incluir=ejemplo/biblioteca-guia/corpus/documento/002-un-lote-en-convencion.caso
```

```json archivo=relaciones/documento.json incluir=ejemplo/biblioteca-guia/relaciones/documento.json
```

Los cuatro documentos de prueba están en `docs-de-prueba/`:

```text archivo=docs-de-prueba/2026-08-31-GUIA-Convencion-v1.0.md incluir=ejemplo/biblioteca-guia/docs-de-prueba/2026-08-31-GUIA-Convencion-v1.0.md
```
```text archivo=docs-de-prueba/2026-09-01-INFORME-Primera-Medida-v1.0.md incluir=ejemplo/biblioteca-guia/docs-de-prueba/2026-09-01-INFORME-Primera-Medida-v1.0.md
```
```text archivo=docs-de-prueba/borrador.md incluir=ejemplo/biblioteca-guia/docs-de-prueba/borrador.md
```
```text archivo=docs-de-prueba/notas-finales.md incluir=ejemplo/biblioteca-guia/docs-de-prueba/notas-finales.md
```


`sensores/nombres.py` — no importa nada del sistema de archivos:

```python archivo=sensores/nombres.py incluir=ejemplo/biblioteca-guia/sensores/nombres.py
"""El SENSOR: puro. Decide si un nombre sigue la convención, y nada más."""
import re

CONVENCION = re.compile(r"^\d{4}-\d{2}-\d{2}-[A-Z]+-[A-Za-z0-9-]+-v\d+\.\d+\.md$")


def sigue_convencion(nombre: str) -> bool:
    return CONVENCION.fullmatch(nombre) is not None
```

Eso se testea con `assert sigue_convencion("borrador.md") is False`. No hace falta un disco.

## El adaptador

`mide_nombres.py` — camina la carpeta y emite filas en la superficie que Oracle lee:

```python archivo=mide_nombres.py incluir=ejemplo/biblioteca-guia/mide_nombres.py
"""El ADAPTADOR: habla con el disco y emite evidencia. No decide nada."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sensores.nombres import sigue_convencion

carpeta = Path(sys.argv[1])
print("documento: nombre, sigue_convencion")
for p in sorted(carpeta.glob("*.md")):
    print(f'    {json.dumps(p.name, ensure_ascii=False)}, '
          f'{"true" if sigue_convencion(p.name) else "false"}')
```

Fijate que **el adaptador no tiene ni un `if` sobre la convención**: pregunta y transcribe.

```bash paso
python3 mide_nombres.py docs-de-prueba
```

```text salida
documento: nombre, sigue_convencion
    "2026-08-31-GUIA-Convencion-v1.0.md", true
    "2026-09-01-INFORME-Primera-Medida-v1.0.md", true
    "borrador.md", false
    "notas-finales.md", false
```

## Medir el mundo real

```bash paso
oracle medida probar catalogos/documento/documento.nombre_sigue_la_convencion.oracle \
      --con "$(python3 mide_nombres.py docs-de-prueba)"
```

```text salida
ROJO   valor 2  (<= 0)

  testigos (2) — las filas que ofenden, no un resumen:
    {'d': {'nombre': 'borrador.md', 'sigue_convencion': False}}
    {'d': {'nombre': 'notas-finales.md', 'sigue_convencion': False}}

  alcance: no ve el contenido del documento, sólo su nombre; y no juzga si la convención en sí es buena
    de `documento` NO lee: nombre
```

Dos archivos que existen en el disco. Ésa es la diferencia entre una regla que probaste y una regla
que **encontró algo**.

La última línea la deriva Oracle sola: la relación declara `nombre`, y la medida no lo lee —filtra
por `sigue_convencion`—. No es un error; es información sobre qué parte del sensor está sin usar.

## Guardar lo que se observó

Un caso con `procedencia: observada` es evidencia que **pasó**, copiada tal cual:

```caso archivo=corpus/documento/003-la-biblioteca-real.caso incluir=ejemplo/biblioteca-guia/corpus/documento/003-la-biblioteca-real.caso
```

**`observada` es una afirmación sobre el pasado**, y Oracle no puede verificarla: el `alcance` de la
medida que la juzga lo dice sin vueltas — *«mira lo que el caso declara sobre sí mismo… Un caso
puede mentir en `procedencia` y esta medida no lo ve»*.

Por eso la regla práctica es al revés de lo que uno querría: **ante la duda, `construida`**. Es
honesto, y no cierra nada que no deba cerrarse.

Con ese caso, el proyecto cierra:

```bash paso
oracle test
```

```text salida
UNITARIOS: salteados (sólo aplican al propio Oracle)

CORPUS OK · 3 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 3 casos

catálogo: 40 medidas · corpus: 3 casos

  ROJO  001-un-nombre-fuera-de-convencion      documento.nombre_sigue_la_convencion  (valor 1)
  verde 002-un-lote-en-convencion              documento.nombre_sigue_la_convencion  (valor 0)
  ROJO  003-la-biblioteca-real                 documento.nombre_sigue_la_convencion  (valor 2)

defectos que se pusieron rojos: 2 · verdes correctos: 1 · sin evidencia esperada: 0 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:
  ✓ meta.el_caso_reclama_una_medida_que_existe          0 (<= 0)
  ✓ meta.el_caso_se_pone_como_debe                      0 (<= 0)
  ✓ meta.el_hueco_declarado_explica_por_que             0 (<= 0)
  ✓ meta.el_nivel_no_se_confunde_con_el_dominio         0 (<= 0)
  ✓ meta.la_medida_no_se_fija_solo_con_evidencia_fabricada        0 (<= 0)
  ✓ meta.ningun_campo_sin_unidad_declarada              0 (<= 0)
  ✓ meta.ningun_flotante_comparado_por_igualdad_en_un_filtro        0 (<= 0)
  ✓ meta.ningun_umbral_de_igualdad                      0 (<= 0)
  ✓ meta.ningun_umbral_flotante_de_igualdad             0 (<= 0)
  ✓ meta.ninguna_medida_sin_alcance                     0 (<= 0)
  ✓ meta.toda_cantidad_comparada_tiene_unidad_derivable        0 (<= 0)
  ✓ meta.toda_medida_de_ausencia_declara_requiere        0 (<= 0)
  ✓ meta.toda_medida_declara_su_ambito                  0 (<= 0)
  ✓ meta.toda_medida_filtra_o_agrupa                    0 (<= 0)
  ✓ meta.toda_medida_lee_campos_que_existen             0 (<= 0)
  ✓ meta.todo_caso_observado_declara_de_donde_salio        0 (<= 0)
  ✓ meta.todo_tanteo_explica_por_que                    0 (<= 0)
  ✓ meta.todo_umbral_declara_de_donde_sale              0 (<= 0)

ACEPTACIÓN ✓ — 2 defectos en rojo, 0 sin evidencia esperada, 1 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 9 · murieron 9 · sobrevivieron 0
  con 30 mutadores: 6 de quien escribió el lenguaje y 24 de otro autor (ver https://github.com/Segtem/oracle/blob/main/docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md)
  de los muertos: 9 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 27

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ⊘ proceso.codigo_con_mutante_que_lo_mata       SIN EVIDENCIA («mutante con m.tipo == "codigo"» vacía; no se midió)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)

MUTACIÓN DE CÓDIGO: salteada (sólo aplica al propio Oracle)

ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: VERDE (todas las verificaciones aplicables en regla)
```

## Funciones propias: `escalares.py`

Si tu dominio necesita una función que el álgebra no trae —una distancia, una norma, un desvío—, se
**declara** en `escalares.py` del proyecto:

```python
from oracle_metalenguaje import escalar

@escalar("desvio", "cm", unidades_argumentos=("cm", "cm"))
def desvio(a, b):
    return abs(a - b)
```

Se declara en vez de importarse suelta por el mismo motivo que un umbral lleva su defensa: lo que
no está declarado no se puede inventariar ni discutir. `oracle escalares` las lista.

Dos cosas que importan:

**Declarar la unidad de retorno Y las de los argumentos.** Sin las dos, la unidad del resultado no
se puede derivar y `meta.toda_cantidad_comparada_tiene_unidad_derivable` te lo marca. No es
burocracia: es lo que impide comparar centímetros contra grados.

**Ejecutarlas exige `--confiar-escalares`.** Oracle no corre código de un proyecto sin permiso
explícito, y cuando lo hace es en un **proceso aislado**: una función hostil no puede leer fuera del
proyecto, escribir fuera, abrir red ni lanzar procesos.

## El paquete instalado es otro proyecto (`DECISION-010`)

La migración de los dos consumidores reales sacó a la luz dos defectos sobre el paquete publicado:

### 1. El comando vs el paquete
- Si el proyecto sólo ejecuta comandos (`oracle test`, `oracle-corpus`), alcanza con `uv tool install oracle-metalenguaje`.
- Si algún script propio importa la biblioteca (`from oracle_metalenguaje import Motor` o `escalar`),
  necesita el paquete en su propio intérprete.
- Para el Python embebido de un motor como Unreal (el caso de Jam), no hay venv posible: se vendoriza
  el wheel publicado con `python3 -m pip install --target vendor/oracle-pkg --no-deps "oracle-metalenguaje==0.6.0"`.
  Medido en Jam: 2,3 MB y 183 archivos contra 3,5 MB y 284 del subtree original.

### 2. Aislamiento de escalares en layouts no estándar
`escalares.py` se ejecuta en un subproceso aislado con el entorno reemplazado. En 0.3.1, ese proceso
fijaba `PYTHONPATH = RAIZ_ORACLE`. En el repositorio eso apunta a la raíz; en un wheel instalado,
eso apuntaba al directorio del paquete mismo, dejando la fachada inalcanzable. Fuera de un venv, el
`from oracle_metalenguaje import escalar` fallaba con `ModuleNotFoundError`. En 0.3.2+ la ruta se
resuelve con `importlib.util.find_spec`.

### 3. La fachada no debe ocupar nombres ajenos
En 0.3.1 y 0.3.2, importar `oracle_metalenguaje` metía en `sys.modules` nombres de nivel superior
(`tools`, `nucleo`, `catalogos`, `perfiles`). Un consumidor con su propio paquete `tools/` moría al
importar con `ModuleNotFoundError: No module named 'tools.referencias'`. En 0.3.3 el alias de `tools`
se mudó fuera de la fachada, al propio paquete `tools/`.

### 4. Antes de borrar un subtree
Si venís de un subtree de git, comprobá antes de borrar que no tenga cambios locales:
```bash
git diff --name-only -- vendor/oracle       # tiene que dar vacío
git status --short -- vendor/oracle         # tiene que dar vacío
```
Borrar sin verificar pierde ediciones que no existen arriba. En Jam y LyraGASP se midió: cero
ediciones locales en ambos antes de migrar.

## Heredar un catálogo: la sombra y su envejecimiento

Cuando un proyecto conecta Oracle y declara `"catalogo_base": true`, pasa a ser juzgado por las 54
medidas universales. En proyectos existentes esto encuentra deudas reales de inmediato:
- En **Jam** aparecieron **104 infracciones** en 3 medidas (54 comparaciones sin unidad derivable,
  41 umbrales sin `segun`, 9 medidas con evidencia puramente fabricada).
- En **LyraGASP** aparecieron **34 infracciones** en las mismas 3 medidas (16 sin unidad, 9 sin
  `segun`, 9 sólo fabricadas).

Ninguno era un error de Oracle: eran omisiones reales del catálogo heredado que antes nadie medía.
La salida no es apagar la regla —eso volvería al verde que no significa nada— ni arreglar 104
defectos en el commit de la conexión. La solución es la **sombra** en `oracle.json`:

```json
{
  "sombra": {
    "meta.todo_umbral_declara_de_donde_sale": {
      "desde": "2026-09-01",
      "porque": "los umbrales son anteriores a `segun`; se completan de a uno"
    }
  }
}
```

La medida se evalúa, se reporta como `[EN SOMBRA]` y no tumba la corrida (`ACEPTACIÓN ✓`).

### La sombra envejece (dos medidas nuevas)

Una sombra sin fecha no se puede envejecer; una sin motivo no se puede discutir. Dos medidas
universales custodian que las sombras no se conviertan en excepciones permanentes:

1. **`meta.ninguna_sombra_envejece_sin_revisarse`**: cuenta los días desde la fecha declarada en
   `desde`. Si supera los **90 días**, la medida se pone roja.
2. **`meta.toda_sombra_declara_una_fecha_real`**: si la fecha no se puede leer (formato inválido) o
   está en el futuro (días negativos), la medida falla de inmediato.

Además, `meta.ninguna_sombra_ya_en_verde` prohíbe mantener en sombra una medida que ya pasa, y
`meta.ninguna_sombra_sobre_una_medida_que_no_existe` evita sombras huérfanas. Ninguna de estas cuatro
medidas puede ponerse en sombra a sí misma.

## Todo el contexto en un comando: `oracle contexto`

Para saber qué podés escribir en tu proyecto sin recorrer archivos ni memorizar esquemas:

```bash
oracle contexto
```

O en formato compacto (~1.600 tokens contra ~8.600 de correr los tres comandos que reemplaza):

```bash
oracle contexto --compacto
```

Reúne en una sola salida:
1. Lo que toda medida declara (`umbral ... segun ... porque ...`, `alcance ...`).
2. Las relaciones y campos disponibles en tu proyecto (derivados de tu evidencia).
3. Con qué se escribe: operadores (`agrupar`, `de`, `donde`, `resumen`, `unir`), comparadores,
   lógicos, agregados y escalares declaradas.
4. Las medidas que ya existen en el catálogo con sus puntos ciegos declarados.
5. La regla de orden: escribir el caso antes que la medida.

---

## Qué sigue

- [Por qué la mutación](05-por-que-la-mutacion.md) — dos autores, 30 mutadores en aislamiento y qué
  hacer cuando uno sobrevive.
- [docs/03-escribir-una-medida.md](03-escribir-una-medida.md) — la guía completa de autoría.
- [`docs/migracion/de-subtree-a-pypi.md`](migracion/de-subtree-a-pypi.md) — guía paso a paso de migración
  desde subtree a PyPI.
- [`DECISION-010`](decisiones/DECISION-010-EL-PAQUETE-INSTALADO-ES-OTRO-PROYECTO.md) — por qué el paquete
  instalado es otro proyecto y cómo se mide.
- [ESPECIFICACION.md](../ESPECIFICACION.md) — la referencia formal del lenguaje.
