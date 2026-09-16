# Encargo 0.26.0 — la anti-junta en el álgebra

2026-09-16. Tarea [`20260916-151553-antijunta`](../../tareas/20260916-151553-antijunta/TAREA.md). Plan
aprobado por el dueño: [PLAN-0.26.0-ANTIJUNTA.md](../../PLAN-0.26.0-ANTIJUNTA.md). Revisa, mide y
corta Claude.

## Leer antes

- El plan entero.
- `ESPECIFICACION.md` §2 (la tubería: `desde`, `de`, `unir`, `donde`, `agrupar`; y el párrafo de
  `requiere` sin cortocircuito, que es el modelo de la regla de evaluación de `sin`).
- `nucleo/algebra.py`: `FUENTES`, `aplicar`, `_de`, `_unir`, `_unir_donde_indexado`, `_agrupar`,
  `_validar_paso`, `_validar_fuente`, `validar_tuberia`, `desde`, `_anotar` y `LimitesAlgebra`.
- `nucleo/sintaxis.py`: cómo se leen e imprimen `donde` y `agrupar` en la superficie (búsqueda por
  `"donde"`), y la regla de ida y vuelta.
- `nucleo/vocabulario.py` (`OPERADORES`), `nucleo/unidad.py` y `nucleo/campo_leido.py` (los dos
  recorren el árbol de una medida y tienen que conocer el paso nuevo), `nucleo/medida.py`
  (`relaciones_de_fuente`, `como_hechos` y las relaciones que emite por cada paso).
- `tools/trazar.py` y las medidas de traza de `catalogos/meta/` (`meta.donde_nunca_agrega_filas`,
  `meta.agrupar_no_agranda_la_relacion`): el modelo de la medida nueva.
- `mutadores/CONTRATO.md` y un par de mutadores existentes: el modelo del mutador nuevo.
- `tools/tareas_hechos.py` (`commits_de_cierre`, `commits_que_la_nombran`) y
  `ejemplo/seguimiento-tareas/` (la medida, la relación declarada, su corpus y su sombra).

## Qué hay que entregar

1. **`sin` en el álgebra** (`nucleo/algebra.py`), con exactamente la semántica del plan: filas de la
   tubería para las que ninguna fila de la relación cumple la condición; la condición ve la fila
   actual y el alias nuevo; el alias nuevo no queda en la salida; relación ausente = el mismo error
   que `de`; relación vacía = pasan todas; **sin cortocircuito** —se evalúan todas las filas de la
   derecha antes de decidir, y si alguna levanta, levanta—; alias repetido = error de validación;
   presupuesto `|izq| × |der|` contra `producto_cartesiano`; y la anotación de traza del paso.
2. **`sin` en la superficie** (`nucleo/sintaxis.py`): `sin <relación> <alias> donde <condición>`
   como un paso más, con lectura, impresión e ida y vuelta.
3. **`VERSION_ALGEBRA = "0.8"` y `VERSION_SINTAXIS = "0.6"`** en `nucleo/version.py`.
   `VERSION_DISTRIBUCION` la sube Claude.
4. **Todo lo que recorre el árbol** conoce el paso: `nucleo/unidad.py`, `nucleo/campo_leido.py` (el
   alias de `sin` es una lectura de campo de esa relación) y las relaciones que emite
   `nucleo/medida.py` por cada paso y cada fuente.
5. **`sin` en `OPERADORES`** de `nucleo/vocabulario.py`, con su explicación.
6. **La medida de traza** `catalogos/meta/meta.sin_nunca_agrega_filas.oracle`, con lo que `trazar`
   tenga que anotar para que exista.
7. **Un mutador** en `mutadores/` que quite el paso `sin` (o lo vuelva inocuo), según su contrato.
8. **La prueba de valor**: `ejemplo/seguimiento-tareas/catalogos/seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre.oracle`
   reescrita con `sin` sobre `commit_seguimiento`, y `commits_de_cierre` y `commits_que_la_nombran`
   **borrados** de `tools/tareas_hechos.py`, de `ejemplo/seguimiento-tareas/relaciones/tarea_seguimiento.json`
   y de `docs/12-tareas.md`. Los casos 023 y 024 del ejemplo usan esos campos: reescribilos para que
   la medida nueva los juzgue con `commit_seguimiento`, conservando su etiqueta.
9. **Tests** en `tests/test_antijunta.py` (nuevo): cada borde del plan, la superficie ida y vuelta, el
   alias que no queda en la salida, el presupuesto, y la medida del tracker reescrita.

## Propiedad

**Agy:** `nucleo/algebra.py`, `nucleo/sintaxis.py`, `nucleo/vocabulario.py`, `nucleo/unidad.py`,
`nucleo/campo_leido.py`, `nucleo/medida.py` (en lo que pide este encargo), `nucleo/version.py` (las dos
líneas de álgebra y sintaxis), `tools/trazar.py`, `catalogos/meta/meta.sin_nunca_agrega_filas.oracle`,
`mutadores/`, `tools/tareas_hechos.py`, `ejemplo/seguimiento-tareas/` entero, `docs/12-tareas.md`,
`tests/test_antijunta.py` (nuevo), y en `estudios/0.26.0-antijunta/` sus `AVANCE-AGY.md` (primero) e
`INFORME-AGY.md` (al final).

**Claude:** `diferencial/` —la referencia la re-deriva otra conversación de agy, aislada, que no puede
ver `nucleo/`—, `tools/generar_diferencial.py`, `corpus/`, `ESPECIFICACION.md`, `NOTAS-DE-RELEASE.md`,
`README.md`, `VERSION_DISTRIBUCION`, `docs/` salvo `12-tareas.md`, `.github/`, y **todo test existente**.
Si un test existente contradice el encargo, no lo edites: anotalo en el informe con su nombre y por qué.

## Reglas

Sólo herramientas de lectura y edición: **NO shell, NO tests, NO subagentes, NO red, NO commits.** En
el informe no afirmes verificaciones que no corriste —no vas a poder correr ninguna, y está bien: las
corre Claude—. La última vez siete de diez tests se escribieron contra atributos que no existen:
**antes de usar un nombre en un test, buscalo en el código.**
