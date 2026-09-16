# Resumen de Entrega — Álgebra 0.8

## 1. Cambios realizados

### `evaluador.py`
- **Versión del álgebra**: Se actualizó `VERSION_ALGEBRA = "0.8"` (proveniente de `"0.7"`), de acuerdo con la especificación vigente (§0, línea 39).
- **Operador de anti-junta `sin`**:
  - Se incorporó la función `_aplicar_sin(filas, paso, evidencia, escalares, limites)` que implementa la semántica completa de `sin` definida en §3 y §8.
  - En `_evaluar_desde`, se añadió el despacho del operador `"sin"` como paso válido de la tubería.
  - En `_evaluar_relacion`, se añadió `"sin"` al conjunto de operadores que solo pueden aparecer como paso de `desde`, levantando `ErrorDeAlgebra` si se intenta evaluar como fuente primaria o expresión de relación aislada.
  - Se implementaron las validaciones requeridas por §3:
    - Validación estricta de sintaxis: `["sin", ["de", relacion, alias], cond]` con nombres no vacíos.
    - Presencia de la relación derecha en `evidencia`: levanta `ErrorDeAlgebra(f"relacion ausente: {relacion}")` con precedencia, incluso si la lista de filas entrantes es vacía.
    - Límite de presupuesto de evaluación: `len(filas) * len(evidencia[relacion]) > limites.filas_materializadas` levanta `ErrorDeAlgebra("sin supera el limite de filas materializadas")`.
    - Detección de colisión de alias: si el alias de `sin` ya está presente en alguna fila entrante (sea como alias o columna derivada), levanta `ErrorDeAlgebra(f"alias duplicado en sin: {alias}")`, incluso si la relación derecha está vacía.
    - Relación vacía: si la relación derecha está vacía (`[]`) y no hay colisión ni presupuesto excedido, pasan todas las filas entrantes.
    - Evaluación sin cortocircuito: para cada fila entrante, `cond` se evalúa sobre todos los hechos de la relación derecha sin interrumpir el bucle al encontrar un hecho que cumpla (`cumple == True`), levantando `ErrorDeAlgebra` inmediatamente si cualquier fila produce un error o si el valor resultante no es de tipo `bool`.
    - Aislamiento del alias: las filas que pasan conservan la estructura original entrante (el alias de `sin` no escapa al resto de la tubería).
    - Compatibilidad con `agrupar`: las condiciones de `sin` pueden acceder a columnas derivadas mediante `["col", nombre]`.

### `test_evaluador.py`
- **Test de versión**: Se actualizó `test_version_algebra_es_0_7` a `test_version_algebra_es_0_8`, verificando `VERSION_ALGEBRA == "0.8"`.
- **Casos de prueba para `sin`**: Se agregaron 21 tests unitarios cubriendo la funcionalidad y todos los casos borde:
  - `test_sin_basico_filtra_filas_que_cumplen`: filtrado básico de anti-junta.
  - `test_sin_relacion_vacia_deja_pasar_todas_las_filas`: relación derecha `[]`.
  - `test_sin_relacion_ausente_levanta_error`: relación ausente en `evidencia`.
  - `test_sin_relacion_ausente_con_filas_entrantes_vacias_levanta_error`: relación ausente cuando la entrada tiene cero filas.
  - `test_sin_sin_cortocircuito_evalua_todas_las_filas`: ausencia de cortocircuito ante campos ausentes en hechos de la relación derecha en ambos órdenes de bolsa.
  - `test_sin_alias_duplicado_con_fila_entrante_levanta_error`: colisión de alias con fila entrante.
  - `test_sin_alias_duplicado_con_relacion_vacia_levanta_error`: colisión de alias con relación derecha vacía.
  - `test_sin_alias_nuevo_no_escapa_a_pasos_posteriores`: alias de `sin` no visible para pasos posteriores (`donde`).
  - `test_sin_despues_de_agrupar_con_col`: uso de `["col", ...]` en la condición tras `agrupar`.
  - `test_sin_despues_de_agrupar_alias_colisiona_con_columna`: colisión entre alias de `sin` y columna agrupada.
  - `test_sin_supera_limite_filas_materializadas`: excedente de `filas_materializadas`.
  - `test_sin_condicion_no_booleana_levanta_error`: retorno no booleano en la condición.
  - `test_sin_como_operador_fuente_o_relacion_invalido`: uso de `sin` como fuente de `desde` o dentro de `unir`.
  - `test_sin_sintaxis_invalida_levanta_error`: validación de formas mal estructuradas para `sin`.
  - `test_sin_con_funcion_escalar_y_hecho_entero`: UDFs y accesor `["hecho", alias]` dentro de la condición.
  - `test_sin_testigos_sin_donde_reflejan_filas_salientes_de_sin`: testigos cuando no hay `donde` en la tubería.
  - `test_sin_testigos_con_donde_anterior`: testigos definidos por `donde` previo a `sin`.
  - `test_sin_testigos_con_donde_posterior`: testigos definidos por `donde` posterior a `sin`.
  - `test_sin_preserva_multiplicidad_bolsa`: preservación de hechos duplicados de la bolsa de entrada.
  - `test_sin_multiple_en_cadena`: múltiples pasos `sin` consecutivos encadenados.

### `DECISIONES.md`
- Se actualizó la sección `Version del algebra vigente` a `0.8`.
- Se agregaron 9 decisiones de diseño nuevas documentando los puntos donde la especificación dejaba margen:
  1. `Paso de tuberia sin y no expresion de relacion aislada` (§3).
  2. `Forma estricta de la fuente en sin` (§3).
  3. `Verificacion de relacion ausente en sin con precedencia sobre filas vacias` (§3).
  4. `Deteccion de colision de alias en sin con relacion derecha vacia` (§3).
  5. `Evaluacion de la condicion de sin sin cortocircuito y con tipo booleano estricto` (§3).
  6. `Testigos y el operador sin` (§2, §3).
  7. `Acceso a columnas derivadas tras agrupar en la condicion de sin` (§3).
  8. `Presupuesto de producto cartesiano en sin` (§3, §9).
  9. `Aislamiento del alias nuevo de sin` (§3).

---

## 2. Decisiones nuevas registradas

1. **`sin` es estrictamente paso de tubería**: Solo puede figurar como paso en `desde[2:]`. En `_evaluar_relacion` levanta `ErrorDeAlgebra`.
2. **Fuente restringida a `["de", relacion, alias]`**: No se aceptan fuentes complejas ni relaciones anónimas en el segundo elemento de `sin`.
3. **Precedencia de ausencia de relación sobre filas vacías**: Si la relación no existe en la evidencia, falla con error de álgebra aunque no haya filas entrantes que filtrar.
4. **Colisión de alias obligatoria incluso con relación derecha vacía**: Si el alias de `sin` ya existe en una fila entrante, es error de álgebra sin importar si la relación derecha tiene o no hechos.
5. **Evaluación de condición sin cortocircuito en toda la relación**: Se recorren todos los hechos de la relación derecha sin cortar en el primer `True`. Cualquier fallo en cualquier hecho aborta la evaluación fail-closed.
6. **Contrato estricto de testigos**: `sin` no actualiza `ultimos_testigos`. Si hay un `donde`, los testigos provienen de él. Si no hay ningún `donde`, se devuelven las filas finales de `desde` tras `sin`.
7. **Acceso a columnas derivadas**: Tras `agrupar`, la condición de `sin` puede leer columnas agrupadas con `col` y hechos de la relación derecha con `campo` o `hecho`.
8. **Presupuesto materializado**: Se comprueba `len(filas) * len(relacion) > filas_materializadas` antes de evaluar hechos.
9. **Aislamiento del alias**: Las filas emitidas por `sin` son copias idénticas a las entrantes sin el alias del hecho derecho, permitiendo reutilizar el alias en pasos subsiguientes.

---

## 3. Estado de verificación

Siguiendo las restricciones estrictas del entorno (**NO shell, NO red, NO subagentes**):
- **No se ejecutaron comandos de shell** (tales como `python -m unittest` o `pytest`).
- El código fue verificado exclusivamente mediante análisis estático, inspección de tipos y contraste contra las cláusulas de `ESPECIFICACION.md` y `CONTRATO.md`.
