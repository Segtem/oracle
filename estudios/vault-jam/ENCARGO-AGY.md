# Encargo — la nota del DSL se vuelve un documento del vault de Jam

2026-09-16. Tarea [`20260916-151553-vault-jam`](../../tareas/20260916-151553-vault-jam/TAREA.md) del
tracker de Oracle. Trabajás en el repositorio de **Jam** (`/home/workstation/Dev/jam`); este archivo
vive en Oracle sólo porque ahí se lleva la tarea. Revisa y verifica Claude.

## El problema, medido

`Vault-kb/05-DSL/El DSL (Domain-Specific Language) de Jam.md` es una nota sin commitear del
2026-09-10: texto pegado, sin frontmatter, con un nombre fuera de la convención y en una carpeta que la
taxonomía no tiene. `tools/vault.py` da hoy **4 de 10 medidas en rojo**, las cuatro por esa nota:
`vault.area_es_la_carpeta`, `vault.carpeta_conocida`, `vault.frontmatter_completo` y
`vault.nombre_sigue_la_convencion`. Por eso el diferencial de Jam no se puede regenerar y `oracle
test` de Jam está rojo. Medido en una copia sin esa carpeta: todo verde.

El dueño decidió que la nota **se conserve** y se vuelva un documento del vault.

## Leer antes

- `AGENTS.md` de Jam (sos uno de los dos agentes que se turnan ahí).
- `Vault-kb/README.md` y `Vault-kb/00-Proceso/2026-07-29-GUIA-Convencion-Documentacion-Vault-v1.0.md`.
- `tools/vault.py`: `NOMBRE`, `OBLIGATORIOS`, `CARPETAS` y `verificar()`.
- Un par de documentos del vault para copiar la forma del frontmatter.
- La nota misma.

## Qué hay que entregar

1. **Un documento nuevo** con la convención del vault:
   - nombre `2026-09-10-<TIPO>-<Slug-En-ASCII>-v1.0.md` (la fecha es la de la nota), con un `TIPO` de
     los que acepta `NOMBRE` y el que mejor describa lo que la nota es;
   - frontmatter con todos los `OBLIGATORIOS` (`title`, `tipo`, `version`, `date`, `updated`, `area`),
     y los demás campos que usen los documentos parecidos (`status`, `tags`);
   - en una **carpeta que ya exista** en `CARPETAS`, con `area:` igual a esa carpeta. Elegí la que mejor
     le corresponda. **No agregues `05-DSL`** salvo que ninguna de las cinco encaje, y si lo hacés,
     argumentalo en el informe: una carpeta nueva es una categoría nueva de la taxonomía, y la
     taxonomía la decide el dueño.
2. **El contenido no se reescribe.** Va entero debajo del frontmatter, con un título `#` al principio.
   Podés sacar los espacios sobrantes al final de cada línea —vienen del pegado— y nada más.
3. **No borres la nota original** (no tenés shell): la borra Claude después de verificar.
4. Si algún documento del vault debería enlazar al nuevo, anotalo en el informe; no agregues enlaces.

## Propiedad y reglas

**Agy:** el documento nuevo dentro de `Vault-kb/`, y en Oracle
`estudios/vault-jam/INFORME-AGY.md` (al final, con el nombre elegido, la carpeta y por qué).

**Claude:** borrar la nota original, `tools/`, `medidas/`, y todo lo demás de los dos repositorios.

Sólo herramientas de lectura y edición: **NO shell, NO tests, NO subagentes, NO red, NO commits.** No
afirmes en el informe verificaciones que no corriste: las corre Claude.
