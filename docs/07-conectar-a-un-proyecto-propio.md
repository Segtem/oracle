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

Es la misma partición que usan los dos consumidores reales de Oracle: `sensores/*.py` puro,
`mide_*.py` como adaptador.

## El sensor

`sensores/nombres.py` — no importa nada del sistema de archivos:

```python
"""El SENSOR: puro. Decide si un nombre sigue la convención, y nada más."""
import re

CONVENCION = re.compile(r"^\d{4}-\d{2}-\d{2}-[A-Z]+-[A-Za-z0-9-]+-v\d+\.\d+\.md$")


def sigue_convencion(nombre: str) -> bool:
    return CONVENCION.fullmatch(nombre) is not None
```

Eso se testea con `assert sigue_convencion("borrador.md") is False`. No hace falta un disco.

## El adaptador

`mide_nombres.py` — camina la carpeta y emite filas en la superficie que Oracle lee:

```python
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

```
$ python3 mide_nombres.py docs-de-prueba
documento: nombre, sigue_convencion
    "2026-08-31-GUIA-Convencion-v1.0.md", true
    "2026-09-01-INFORME-Primera-Medida-v1.0.md", true
    "borrador.md", false
    "notas finales.md", false
```

## Medir el mundo real

```
$ oracle medida probar catalogos/documento/documento.nombre_sigue_la_convencion.oracle \
      --con "$(python3 mide_nombres.py docs-de-prueba)"
ROJO   valor 2  (<= 0)

  testigos (2) — las filas que ofenden, no un resumen:
    {'d': {'nombre': 'borrador.md', 'sigue_convencion': False}}
    {'d': {'nombre': 'notas finales.md', 'sigue_convencion': False}}

  alcance: no ve el contenido del documento, sólo su nombre; y no juzga si la convención en sí es buena
    de `documento` NO lee: nombre
```

Dos archivos que existen en el disco. Ésa es la diferencia entre una regla que probaste y una regla
que **encontró algo**.

La última línea la deriva Oracle sola: la relación declara `nombre`, y la medida no lo lee —filtra
por `sigue_convencion`—. No es un error; es información sobre qué parte del sensor está sin usar.

## Guardar lo que se observó

Un caso con `procedencia: observada` es evidencia que **pasó**, copiada tal cual:

```
caso 003-la-biblioteca-real:
    fecha: "2026-09-01"
    origen:
        repo: "aula/biblioteca"
        commit: "sin-commit"
    procedencia: observada
    titulo: "Dos archivos de la carpeta real están fuera de convención"
    etiqueta: falso_verde
    sintoma:
        Corriendo el sensor sobre docs-de-prueba/ aparecieron dos nombres fuera de convención
        que nadie había notado: `borrador.md` y `notas finales.md`.
    como_se_detecto: herramienta_ajena
    medida: documento.nombre_sigue_la_convencion
    evidencia:
        documento: nombre, sigue_convencion
            "2026-08-31-GUIA-Convencion-v1.0.md", true
            …
    leccion:
        La evidencia observada es la que el sensor devolvió, copiada tal cual. Si se la edita para
        que quede prolija deja de ser observada.
```

**`observada` es una afirmación sobre el pasado**, y Oracle no puede verificarla: el `alcance` de la
medida que la juzga lo dice sin vueltas — *«mira lo que el caso declara sobre sí mismo… Un caso
puede mentir en `procedencia` y esta medida no lo ve»*.

Por eso la regla práctica es al revés de lo que uno querría: **ante la duda, `construida`**. Es
honesto, y no cierra nada que no deba cerrarse.

Con ese caso, el proyecto cierra:

```
$ oracle test
CORPUS OK · 3 casos · esquema, evidencia L0 y trazabilidad en regla

  ROJO  001-un-nombre-fuera-de-convencion  documento.nombre_sigue_la_convencion  (valor 1)
  verde 002-un-lote-en-convencion          documento.nombre_sigue_la_convencion  (valor 0)
  ROJO  003-la-biblioteca-real             documento.nombre_sigue_la_convencion  (valor 2)

ACEPTACIÓN ✓ — 2 defectos en rojo, 1 verdes correctos, 0 huecos declarados sin tapar
mutantes de medida (medida × mutador): 7 · murieron 7 · sobrevivieron 0

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

---

## Qué sigue

- [Por qué la mutación](05-por-que-la-mutacion.md) — qué hacer cuando un mutante sobrevive.
- [ESCRIBIR-UNA-MEDIDA.md](../ESCRIBIR-UNA-MEDIDA.md) — la guía larga de cómo se escribe una.
- [ESPECIFICACION.md](../ESPECIFICACION.md) — la referencia del lenguaje.
