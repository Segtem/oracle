# Avance 0.26.0 — La anti-junta en el álgebra (`sin`)

**Fecha**: 2026-09-16  
**Tarea**: `tareas/20260916-151553-antijunta`  
**Plan**: `vault-kb/planes/PLAN-0.26.0-ANTIJUNTA.md`  
**Encargo**: `vault-kb/estudios/0.26.0-antijunta/ENCARGO-AGY.md`  
**Autor**: Agy  
**Revisor / Verificador**: Claude  

---

## 1. Análisis del problema y requerimientos

El álgebra de Oracle cuenta con `unir` (producto cartesiano) y `donde` (filtro), lo que permite afirmar «existe una fila de B que corresponde a esta fila de A». Sin embargo, carecía de un mecanismo canónico para expresar la aserción contraria: **ninguna fila de B corresponde a esta fila de A** (la anti-junta relacional).

Como consecuencia, diversas medidas del catálogo se veían forzadas a recurrir a contadores precalculados por sensores en Python para comparar contra cero (`commits_de_cierre`, `mutantes`, `casos_que_la_evaluan`, etc.), desplazando lógica fuera del lenguaje declarativo hacia el sensor.

El objetivo del hito 0.26.0 es incorporar el paso de tubería `sin` en el álgebra y en la superficie infija:
1. **Forma canónica**: `["sin", ["de", "<relación>", "<alias>"], <condición>]`.
2. **Superficie**: `sin <relación> <alias> donde <condición>`.
3. **Semántica rigurosa**:
   - Deja pasar cada fila de la tubería para la cual **ninguna** fila de la relación derecha satisface la condición.
   - La condición evalúa sobre `{**fila_izq, **fila_der}` (con acceso a los alias de la fila actual y al alias nuevo de la derecha).
   - El alias nuevo **no** se conserva en la salida (la fila resultante conserva la estructura de la izquierda).
   - **Sin cortocircuito**: la condición se evalúa contra **todas** las filas de la derecha; si cualquier evaluación levanta una excepción (por ejemplo, campo ausente o error del álgebra), la excepción se propaga de inmediato, garantizando la independencia del orden en la bolsa.
   - **Relación ausente**: levanta `ErrorDeAlgebra` con el mismo mensaje que `de` (`"la relación «...» no existe en la evidencia; una relación vacía se declara explícitamente como []"`).
   - **Relación vacía** (`[]`): pasan todas las filas de la izquierda.
   - **Alias repetido**: si el alias de la derecha colisiona con un alias activo en la tubería, es un error de validación (`"alias repetido"`).
   - **Presupuesto**: `|izquierda| × |derecha|` evaluaciones contra `LimitesAlgebra.producto_cartesiano`.
   - **Posterior a `agrupar`**: válido; la condición puede leer columnas derivadas con `col`.
4. **Actualización de versiones**:
   - `VERSION_ALGEBRA = "0.8"` (en `nucleo/version.py`).
   - `VERSION_SINTAXIS = "0.6"` (en `nucleo/version.py`).
5. **Inspección integral del AST**:
   - `nucleo/vocabulario.py`: incorporación de `"sin"` en `OPERADORES`.
   - `nucleo/unidad.py`: extracción de comparaciones en la condición de `sin` y resolución de unidades para campos del alias derecho.
   - `nucleo/campo_leido.py`: resolución del alias de `sin` para reportar lecturas en `campo_leido`.
   - `nucleo/medida.py`: registro en `_pasos_de`, `_fuentes_de_medida`, `_dependencias_de_medida` y `relaciones_de_medida`.
6. **Trazabilidad y medida meta**:
   - `tools/trazar.py`: registrar `"meta.sin_nunca_agrega_filas"` en `VIGILANTES`.
   - `catalogos/meta/meta.sin_nunca_agrega_filas.oracle`: verificar que `sin` nunca produzca más filas de las que entraron (`p.filas_despues > p.filas_antes`).
7. **Mutador**:
   - Implementar mutador en `mutadores/antijunta.py` que retire el paso `sin` de una medida conforme a `mutadores/CONTRATO.md`.
8. **Prueba de valor (Tracker de tareas)**:
   - Reescribir `seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre` con `sin`.
   - Eliminar `commits_de_cierre` y `commits_que_la_nombran` de `tools/tareas_hechos.py`, de `ejemplo/seguimiento-tareas/relaciones/tarea_seguimiento.json` y de `docs/12-tareas.md`.
   - Actualizar casos 023 y 024 de `ejemplo/seguimiento-tareas/corpus/` con hechos de `commit_seguimiento`.
9. **Tests unitarios exhaustivos**:
   - `tests/test_antijunta.py` cubriendo cada borde del plan y del álgebra.

---

## 2. Contradicción identificada con tests preexistentes

Siguiendo la instrucción de no editar tests existentes y documentar contradicciones:
- `tests/test_tareas_hechos_commits.py` (propiedad de Claude) contiene aserciones explícitas sobre `suya["commits_que_la_nombran"]` y `suya["commits_de_cierre"]` en los tests `test_los_commits_llegan_y_cada_tarea_cuenta_los_suyos` y `test_sin_git_la_relacion_viene_vacia_y_los_conteos_en_cero`.
- Dado que el encargo 0.26.0 exige inequívocamente **borrar** ambos campos de `tools/tareas_hechos.py`, `tests/test_tareas_hechos_commits.py` fallará con `KeyError: 'commits_que_la_nombran'` hasta que Claude actualice dichos tests en la fase de revisión/corte. Respetando la propiedad de archivos, este archivo no será modificado por Agy y queda registrado formalmente.

---

## 3. Plan de archivos y responsabilidades

| Archivo | Acción | Propiedad |
|---|---|---|
| `nucleo/algebra.py` | Modificar: validación y ejecución del paso `sin`, límites, traza, control de alias repetido | Agy |
| `nucleo/sintaxis.py` | Modificar: lectura, impresión e ida y vuelta de `sin <relación> <alias> donde <condición>` | Agy |
| `nucleo/version.py` | Modificar: `VERSION_ALGEBRA = "0.8"`, `VERSION_SINTAXIS = "0.6"` | Agy |
| `nucleo/vocabulario.py` | Modificar: agregar `"sin"` a `OPERADORES` con su explicación | Agy |
| `nucleo/unidad.py` | Modificar: extraer comparaciones y alias de `sin` en `comparaciones_de_medida` | Agy |
| `nucleo/campo_leido.py` | Modificar: resolver alias de `sin` en `extraer_alias_de_medida` | Agy |
| `nucleo/medida.py` | Modificar: registrar pasos y fuentes de `sin` en `_pasos_de`, `_fuentes_de_medida`, `relaciones_de_medida` | Agy |
| `tools/trazar.py` | Modificar: añadir `"meta.sin_nunca_agrega_filas"` a `VIGILANTES` | Agy |
| `catalogos/meta/meta.sin_nunca_agrega_filas.oracle` | Crear: medida que vigila que `sin` nunca agrande la relación | Agy |
| `mutadores/antijunta.py` | Crear: mutador `quitar_antijunta` según `mutadores/CONTRATO.md` | Agy |
| `mutadores/__init__.py` | Modificar: exportar `quitar_antijunta` | Agy |
| `ejemplo/seguimiento-tareas/catalogos/seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre.oracle` | Modificar: reescribir con `sin commit_seguimiento c donde c.tarea_nombrada == t.id y c.es_cierre == true` | Agy |
| `ejemplo/seguimiento-tareas/relaciones/tarea_seguimiento.json` | Modificar: eliminar `commits_que_la_nombran` y `commits_de_cierre` | Agy |
| `tools/tareas_hechos.py` | Modificar: eliminar cálculo y emisión de `commits_que_la_nombran` y `commits_de_cierre` | Agy |
| `docs/12-tareas.md` | Modificar: actualizar documentación de `tarea_seguimiento` y de la medida reescrita | Agy |
| `ejemplo/seguimiento-tareas/corpus/seguimiento/023-tarea-cerrada-sin-su-commit-de-cierre.caso` | Modificar: reescribir evidencia usando `commit_seguimiento` (falso verde) | Agy |
| `ejemplo/seguimiento-tareas/corpus/seguimiento/024-cada-cerrada-con-su-cierre.caso` | Modificar: reescribir evidencia usando `commit_seguimiento` (verde correcto) | Agy |
| `tests/test_antijunta.py` | Crear: suite de pruebas unitarias para el paso `sin`, álgebra, sintaxis, mutador y tracker | Agy |
| `vault-kb/estudios/0.26.0-antijunta/INFORME-AGY.md` | Crear: informe final con decisiones y notas | Agy |
