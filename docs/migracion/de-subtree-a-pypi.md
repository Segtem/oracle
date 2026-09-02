# Migrar un consumidor de `vendor/oracle` (subtree) al paquete de PyPI

Vale para cualquier proyecto que hoy consuma Oracle por un subtree de git. Los dos casos concretos
—medidos el 2026-09-01— están en [`jam.md`](jam.md) y [`lyragasp.md`](lyragasp.md); leé primero el
que te toque, porque trae el estado real de ese repo.

## Por qué

El subtree fue la forma correcta mientras Oracle no se publicaba. Ahora se instala
(`oracle-metalenguaje` en PyPI) y el subtree cuesta lo que cuesta: hay que acordarse de traerlo,
duplica ~9.000 líneas en cada consumidor, y **editarlo a mano lo separa del upstream en silencio**.

## Antes de tocar nada: lo único que puede perder trabajo

Un subtree editado a mano tiene cambios que **no existen arriba**, y borrarlo los pierde sin aviso.
Comprobalo, y si esto no da vacío **PARÁ y avisá**:

```bash
git diff --name-only -- vendor/oracle       # tiene que ser vacío
git status --short -- vendor/oracle         # tiene que ser vacío
```

> El 2026-09-01 se midió en los dos consumidores: **cero** ediciones locales en ambos. Si en tu
> corrida da distinto, el repo cambió desde entonces y este documento ya no describe tu situación.

También comprobá que el árbol de trabajo no tenga cambios sin commitear que no sean tuyos. Este
documento **nunca** te pide `git stash`, `git clean`, `git checkout .` ni `git reset`: si algo de
eso parece necesario, es que hay que preguntar, no ejecutar.

## Los pasos

### 1 · Instalar Oracle

```bash
uv tool install oracle-metalenguaje
oracle --version          # tiene que decir 0.3.0 o más
```

`uv tool install` es lo recomendado y no es capricho: en Arch, Debian 12+, Ubuntu 23.04+ y Fedora un
`pip install` al Python del sistema **falla** con `externally-managed-environment`, y saltear esa
protección rompe paquetes del sistema. Además deja `oracle-lsp` en el PATH, que es lo que el editor
necesita para encontrarlo.

Si `oracle-lsp` no aparece, `uv tool install --force oracle-metalenguaje`: hubo un caso medido en el
que enlazó 8 de los 9 ejecutables sin decir nada.

### 2 · Cambiar las invocaciones

| antes | ahora |
|---|---|
| `python vendor/oracle/tools/corpus.py --proyecto medidas` | `oracle-corpus --proyecto medidas` |
| `python vendor/oracle/tools/aceptacion.py --proyecto medidas` | `oracle-aceptacion --proyecto medidas` |
| `python vendor/oracle/tools/mutar.py --proyecto medidas` | `oracle-mutar --proyecto medidas` |
| `python vendor/oracle/tools/diferencial.py --proyecto medidas` | `oracle-diferencial --proyecto medidas` |
| `python vendor/oracle/tools/medida.py …` | `oracle-medida …` |
| `python vendor/oracle/tools/estudio.py …` | `oracle-estudio …` |
| la secuencia completa | `oracle test --proyecto medidas --confiar-escalares` |

`--confiar-escalares` sigue haciendo falta donde ya hacía falta: ejecuta el `escalares.py` del
proyecto, que es código, y por eso nunca es implícito. Desde 0.2.0 corre en un proceso aislado.

Podés evitar repetir `--proyecto` con `export ORACLE_PROYECTO=medidas`.

### 3 · Sacar el subtree

```bash
git rm -r --cached vendor/oracle
rm -rf vendor/oracle
```

Y actualizar todo lo que lo nombraba: los `.md` del proyecto, CI, scripts. Cada archivo está listado
en el documento de tu proyecto.

### 4 · Declarar la sombra ANTES de correr

Acá está el punto delicado. El Oracle de hoy trae medidas que el del subtree no tenía, así que el
proyecto va a salir rojo en cosas **reales** que nadie va a arreglar en el mismo commit de la
migración. Apagar la medida sería volver al verde que no significa nada. La sombra es la tercera
opción: la medida se evalúa, se informa con `[EN SOMBRA]` y **no tumba la corrida**.

En `oracle.json` del proyecto:

```json
{
  "sombra": {
    "meta.todo_umbral_declara_de_donde_sale": {
      "desde": "2026-09-01",
      "porque": "los umbrales del catálogo son anteriores a `segun`; se completan de a uno"
    }
  }
}
```

`desde` y `porque` son **obligatorios**: una sombra sin fecha no se puede envejecer y una sin motivo
no se puede discutir. Escribí un motivo de verdad — «para que pase» no es un motivo, y alguien
(probablemente vos) va a leerlo en tres meses.

**Una sombra no es una excepción permanente.** La lista de tu proyecto está en su documento, con
cuántas infracciones tapa cada una.

### 5 · Verificar

```bash
oracle-corpus     --proyecto medidas
oracle-aceptacion --proyecto medidas --confiar-escalares    # tiene que salir 0
oracle-mutar      --proyecto medidas --confiar-escalares
```

La aceptación **con las sombras puestas** tiene que salir 0. Si sale 1, hay un rojo que no está
contemplado: leelo, no lo agregues a la sombra sin entenderlo.

## Lo que NO hay que hacer

- **No borrar `vendor/oracle` antes de comprobar que no tiene ediciones locales.** Es lo único
  irreversible de todo esto.
- **No poner en sombra una medida sin leer qué encontró.** La sombra existe para posponer un
  arreglo, no para no mirarlo.
- **No fijar la versión con `>=`.** Un consumidor que se actualiza solo se pone rojo un martes por
  algo que no cambió de su lado. Fijá `oracle-metalenguaje==0.3.0` y subí a propósito.
