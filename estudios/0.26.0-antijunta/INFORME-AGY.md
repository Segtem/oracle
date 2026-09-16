# Informe de implementación: 0.26.0 — la anti-junta en el álgebra

**Fecha:** 2026-09-16  
**Tarea:** `tareas/20260916-151553-antijunta`  
**Plan:** `PLAN-0.26.0-ANTIJUNTA.md`  
**Autor:** Agente Agy  

---

## 1. Resumen de lo implementado

Se completaron todos los puntos encomendados bajo la propiedad estricta asignada a Agy:

1. **`VERSION_ALGEBRA` y `VERSION_SINTAXIS`** (`nucleo/version.py`):
   - `VERSION_ALGEBRA` se incrementó de `"0.7"` a `"0.8"`.
   - `VERSION_SINTAXIS` se incrementó de `"0.5"` a `"0.6"`.
   - `VERSION_DISTRIBUCION` se preservó intacta para que Claude la suba a `0.26.0`.

2. **Vocabulario de operadores** (`nucleo/vocabulario.py`):
   - Se añadió `"sin"` al diccionario `OPERADORES` con su definición canónica: descarta las filas para las que existe al menos una coincidencia en la relación nombrada según la condición, conservando únicamente las columnas y alias del lado izquierdo.

3. **Operador `sin` en el álgebra** (`nucleo/algebra.py`):
   - Función auxiliar `_alias_de_fuente`: extrae el conjunto de alias introducidos por una fuente (`de` o `unir`).
   - Función evaluadora `_sin(paso, filas, evidencia, limites, registro, *, ruta)`:
     - Valida que la fuente derecha sea válida (`FUENTES`).
     - Evalúa la relación derecha vía `aplicar(fuente_der, ...)`. Si la relación no existe en la evidencia, falla con el mensaje canónico de `_de` (`la relación «...» no existe en la evidencia; una relación vacía se declara explícitamente como []`), incluso si las filas de la izquierda vienen vacías.
     - Si la relación derecha viene vacía (`[]`), todas las filas de la izquierda sobreviven.
     - Presupuesto cartesiano: comprueba `len(filas) * len(filas_der) > limites.producto_cartesiano` y levanta `ErrorDeAlgebra("producto cartesiano...")`.
     - Alias repetido: detecta si el alias derecho colisiona con los alias activos en las filas de la izquierda y levanta `ErrorDeAlgebra("«sin» con alias repetido: ...")`.
     - **Sin cortocircuito**: para cada fila izquierda se evalúan todas las filas derechas; si alguna evaluación levanta excepción, ésta se propaga sin silenciarse aunque otra fila derecha haya coincidido previamente.
     - Salida: las filas que sobreviven conservan exclusivamente sus alias y columnas izquierdas (o derivadas en caso de venir de `agrupar`). El alias derecho se descarta.
   - En `_validar_paso`: se agregó validación del operador `"sin"`, comprobando longitud 3, validación de fuente, no colisión con `alias_activos`, y validación de la expresión de cruce.
   - En `validar_tuberia`: se realiza seguimiento de `alias_activos` a lo largo de la tubería (reseteándose ante `agrupar`), validando estáticamente colisiones de alias en pasos `sin`.
   - En `aplicar`: despacho de `op == "sin"` hacia `_sin(...)`.
   - Traza: `desde()` registra automáticamente hechos de la relación `paso` con `operador="sin"`, `filas_antes` y `filas_despues`.

4. **Sintaxis infija** (`nucleo/sintaxis.py`):
   - Lectura: `_leer_medida` reconoce `sin <relación> <alias> donde <condición>` dentro del bloque de pasos, registrando ubicaciones para mapeo de errores y emitiendo el nodo AST `["sin", ["de", relacion, alias], condicion]`.
   - Impresión: `_imprimir_pasos` formatea pasos `sin` como `    sin <relación> <alias> donde <condición>`.
   - Análisis de plantillas: `_tipos_en_plantilla` visita el nodo `sin` asignando rol `"fuente"` a la fuente derecha y `"expr"` a la condición.
   - Garantía de ida y vuelta: texto -> AST -> texto produce paridad de caracteres.

5. **Inspección del árbol en submódulos**:
   - `nucleo/unidad.py`: `_extraer_comparaciones_de_paso` reconoce `op == "sin"` y extrae comparaciones de `paso[2]`. `comparaciones_de_medida` incorpora temporalmente los alias de la fuente de `sin` para derivar correctamente la unidad de los campos de la relación derecha sin filtrarlos hacia pasos posteriores.
   - `nucleo/campo_leido.py`: `extraer_alias_de_medida` inspecciona los pasos `sin` en `medida.tuberia[2:]` y registra la correspondencia alias -> relación, permitiendo que las lecturas de campos de la relación derecha sean clasificadas adecuadamente.
   - `nucleo/medida.py`: `relaciones_de_medida` incluye las relaciones provenientes de fuentes en pasos `sin`, asegurando que `medidas_aplicables` no seleccione la medida si la evidencia carece de dicha relación. Asimismo, `_fuentes_de_medida` emite hechos de la relación `fuente` para los pasos `sin`, que son reflejados consecuentemente en `_dependencias_de_medida`.

6. **Medida de vigilancia de traza** (`tools/trazar.py` y `catalogos/meta/`):
   - Se añadió `"meta.sin_nunca_agrega_filas"` al conjunto `VIGILANTES` en `tools/trazar.py`.
   - Se creó `catalogos/meta/meta.sin_nunca_agrega_filas.oracle`, que vigila que todo paso con `operador == "sin"` cumpla `filas_despues <= filas_antes` sobre la relación `paso`.

7. **Mutador de anti-junta** (`mutadores/antijunta.py` y `mutadores/__init__.py`):
   - Se implementó `quitar_antijunta(datos: list) -> list | None`, que elimina los pasos `sin` de la tubería de la medida sin mutar el objeto original, conforme a `mutadores/CONTRATO.md`.
   - Se exportó en `mutadores/__init__.py`. Se mantuvo intacto `mutadores/segundo_autor.py` para no perturbar el inventario de autoría ajena de Codex.

8. **Prueba de valor y limpieza en el tracker**:
   - `ejemplo/seguimiento-tareas/catalogos/seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre.oracle`: reescrita en sintaxis infija canónica utilizando `sin commit_seguimiento c donde c.tarea_nombrada == t.id y c.es_cierre == true`.
   - `tools/tareas_hechos.py`: se eliminó la inicialización y el bucle de acumulación de `commits_que_la_nombran` y `commits_de_cierre` en `tarea_seguimiento`.
   - `ejemplo/seguimiento-tareas/relaciones/tarea_seguimiento.json`: se eliminaron las declaraciones de los campos `commits_que_la_nombran` y `commits_de_cierre`.
   - `docs/12-tareas.md`: se actualizaron las secciones 2 y 5 eliminando los campos retirados y documentando la verificación mediante anti-junta.
   - `ejemplo/seguimiento-tareas/corpus/seguimiento/`: se reescribieron los casos `023-tarea-cerrada-sin-su-commit-de-cierre.caso` y `024-cada-cerrada-con-su-cierre.caso` incorporando evidencia en `commit_seguimiento` y retirando los campos borrados de `tarea_seguimiento`.

9. **Suite de pruebas** (`tests/test_antijunta.py`):
   - Archivo nuevo que contiene pruebas unitarias exhaustivas para todos los casos de borde del álgebra, sintaxis, ida y vuelta, inspecciones de AST, mutador y evaluación de la medida reescrita sobre los casos 023 y 024.

---

## 2. Decisiones de diseño y justificación

1. **Forma canónica del paso en el AST**:
   `["sin", ["de", relacion, alias], condicion]`
   *Justificación:* Mantiene consistencia con `unir`, que alberga fuentes internamente (`["unir", f1, f2]`). Esto permite que la fuente derecha sea tratada por la maquinaria de fuentes existente (`aplicar(fuente, ...)`), posibilitando en el futuro generalizaciones sin alterar la estructura canónica.

2. **Alcance de los alias de la derecha**:
   El alias de la fuente en `sin` existe únicamente para la evaluación de la condición de cruce. Las filas que sobreviven conservan exclusivamente los alias y columnas del lado izquierdo. En consecuencia:
   - Los pasos posteriores de la tubería no pueden referenciar el alias derecho de `sin`.
   - En `nucleo/unidad.py`, el mapa de alias se enriquece con el alias de `sin` exclusivamente para analizar las comparaciones de ese paso, evitando filtraciones a pasos subsiguientes.

3. **Evaluación estricta sin cortocircuito**:
   En `_sin`, el bucle que evalúa `condicion` itera sobre **todas** las filas de la relación derecha sin realizar un `break` anticipado cuando encuentra coincidencia. Si la evaluación sobre cualquier fila derecha falla (por ejemplo, por error de álgebra o acceso inválido), la excepción se propaga. Esto garantiza determinismo independientemente del orden de la bolsa relacional.

4. **Preservación de `mutadores/segundo_autor.py`**:
   `mutadores/segundo_autor.py` documenta formalmente 24 mutadores creados por Codex bajo `mutadores/PROCEDENCIA.md`. Añadir mutadores allí alteraría las afirmaciones de `tests/test_mutacion.py` respecto al recuento exacto de mutadores ajenos. Por ende, se creó el módulo independiente `mutadores/antijunta.py`, exportando la función a través de `mutadores/__init__.py`.

5. **Formato de superficie de la medida reescrita**:
   La medida `seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre` se escribió usando la forma canónica `medida ...:`, dado que la macro `ninguno` está concebida para un único paso `donde` y no admite pasos de tubería adicionales en su plantilla.

---

## 3. Contradicciones y advertencias para Claude

> [!WARNING] Contradicción con tests existentes en `tests/test_tareas_hechos_commits.py`
> Al eliminar `commits_que_la_nombran` y `commits_de_cierre` de `tools/tareas_hechos.py` y `ejemplo/seguimiento-tareas/relaciones/tarea_seguimiento.json` (mandato explícito del encargo para demostrar el valor de la anti-junta), el test existente `tests/test_tareas_hechos_commits.py` fallará con `KeyError` al intentar consultar dichos campos:
> - Línea 60: `self.assertEqual(suya["commits_que_la_nombran"], 1)`
> - Línea 61: `self.assertEqual(suya["commits_de_cierre"], 1)`
> - Línea 78: `self.assertEqual(suya["commits_de_cierre"], 0)`
>
> Siguiendo estrictamente las reglas del proyecto ("no edites tests existentes (anotá contradicciones en el informe)"), **Agy no modificó `tests/test_tareas_hechos_commits.py`**. Le corresponde a Claude actualizar o remover esas aserciones al revisar e integrar la tarea.

---

## 4. Estado de verificación

Siguiendo las restricciones operativas impuestas (NO shell, NO ejecución de tests, NO subagentes, NO red, NO commits):
- **No se ejecutó ningún comando ni suite de tests en la terminal.**
- Todas las verificaciones se realizaron mediante análisis estático minucioso del código fuente, trazado manual de flujo de datos y verificación cruzada de identificadores contra los módulos preexistentes.
