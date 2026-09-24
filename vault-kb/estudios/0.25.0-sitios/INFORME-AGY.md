# Informe 0.25.0 — Filtro de sitios y declaración de ronda parcial

**Fecha**: 2026-09-16  
**Tarea**: `tareas/20260915-201030-sitios`  
**Encargo**: `vault-kb/estudios/0.25.0-sitios/ENCARGO-AGY.md`  
**Autor**: Agy  
**Revisor / Verificador**: Claude  

---

## 1. Resumen de lo implementado

En este hito se implementó la capacidad de realizar corridas acotadas y rápidas de mutación de código en `tools/mutar_codigo.py` y `perfiles/python/mutacion_codigo.py` mediante filtros por rango de líneas (`--lineas`) y por identificador de sitio (`--sitio`), garantizando a la vez que una ronda filtrada se declare como **parcial** en su evidencia y sea rechazada como evidencia de release por las medidas del catálogo de proceso.

### Archivos modificados y creados (todos dentro de la propiedad de Agy):
1. `relaciones/corrida_mutacion.json`: Añadidos campos `parcial` (`booleano`, `sin_unidad`) y `total_sitios` (`entero`, `sin_unidad`).
2. `perfiles/python/mutacion_codigo.py`:
   - Declarado `CAMPOS_DE_RELACIONES = {"corrida_mutacion": (...)}` con los 25 campos de la relación.
   - Parámetro `parcial: bool` en `_identidad_ronda` para aislar manifiestos de rondas parciales y completas.
   - Parámetro `filtro_sitios` en `_correr_en_raiz` y `correr`.
   - Cálculo de `total_sitios` y validación de `ids_vigentes` para equivalentes sobre el inventario completo **antes** de filtrar.
   - Filtrado de sitios por callable o colección; validación de no-vacío (`ValueError` si ningún sitio califica).
   - Emisión de `"parcial": es_parcial` y `"total_sitios": total_sitios` en `corrida_mutacion[0]`.
3. `tools/mutar_codigo.py`:
   - Docstring del módulo actualizado con ejemplos y explicación de rondas parciales.
   - Función auxiliar `parsear_rango_lineas` (valida formato `A-B` o `A`, `1 <= A <= B`).
   - Argumentos CLI `--lineas` y `--sitio` (repetibles, `metavar="A-B"` y `metavar="ID"`).
   - En `_ejecutar`: construcción del predicado `filtro_sitios` (unión de criterios).
   - Anuncio destacado en la **primera línea de la salida** de la terminal si la ronda es parcial.
   - Aviso explícito en el **resumen** (`*** RESUMEN: RONDA PARCIAL (X de Y sitios) ***`).
   - Mensaje de cierre diferenciado: advierte que una ronda parcial con 0 vivos **no demuestra que los tests fijen el módulo completo**.
4. `catalogos/proceso/proceso.ronda_mutacion_concluyente.oracle`:
   - Cláusula `donde` actualizada con `c.parcial == true o ...`.
   - Textos de `porque` y `alcance` actualizados.
5. `corpus/proceso/`:
   - Actualizados casos `016`, `017`, `019`, `108` incorporando `, parcial` en la cabecera de `corrida_mutacion` y `, false` en la fila de datos.
   - Creado `111-ronda-mutacion-parcial-no-es-concluyente.caso` (`etiqueta: falso_verde`, polaridad que rechaza la ronda parcial).
   - Creado `112-ronda-mutacion-completa-concluyente.caso` (`etiqueta: verde_correcto`, polaridad que aprueba la ronda completa).
6. `tests/test_mutacion_codigo.py`:
   - Incorporada la clase `FiltroSitiosTests` al final del archivo con 9 tests unitarios exhaustivos.
7. `vault-kb/estudios/0.25.0-sitios/AVANCE-AGY.md` e `INFORME-AGY.md`.

---

## 2. Decisiones de diseño y arquitectura

### A. Semántica de combinación y validación de filtros
- **Unión de criterios**: Si se pasan varios `--lineas` y varios `--sitio`, un mutante es seleccionado si coincide con cualquiera de los rangos O con cualquiera de los IDs especificados.
- **Formato flexible pero estricto en `--lineas`**: Se acepta tanto un rango `10-25` como una línea individual `42` (interpretada como `42-42`). Se rechazan rangos invertidos (`25-10`), líneas no positivas (`0-10`) y textos no numéricos.
- **Validación de `--sitio`**: Se exige al menos 4 componentes (`archivo:linea:col:op`) para detectar tempranamente errores tipográficos.
- **Filtro con cero coincidencias**: Si los filtros no seleccionan ningún sitio dentro de los objetivos resueltos, `_correr_en_raiz` levanta `ValueError("el filtro de sitios no seleccionó ningún sitio de mutación en los objetivos")`. En `_ejecutar` esto es capturado, imprime `MUTACIÓN NO CONFIABLE — ValueError` y termina con **código de salida 2**. Esto impide cualquier falso verde por filtros vacíos.

### B. Mínima alteración en `perfiles/python/mutacion_codigo.py` (auto-mutación)
- `mutacion_codigo.py` es evaluado por el arnés de mutación propio de Oracle (227 mutantes). Cada línea o rama condicional adicional corre el riesgo de introducir ramas equivalentes o difíciles de matar.
- Por ello, la lógica añadida se mantuvo en menos de 15 líneas:
  - Descubrimiento intacto.
  - `total_sitios = sum(len(s) for s in sitios_por_ruta.values())`.
  - Validación de equivalentes contra `ids_vigentes` **antes** del filtrado (ver punto C).
  - Filtrado en un bucle simple `sitios_por_ruta[ruta] = [s for s in sitios if criterio(s)]`.
  - Inclusión directa de `"parcial"` y `"total_sitios"` en el retorno estructurado.

### C. Validación de equivalentes vs. filtrado de sitios
- `_correr_en_raiz` verifica que no existan declaraciones de equivalentes vencidas mediante:
  `ids_vencidos = set(equivalentes) - ids_vigentes`.
- **Decisión crucial**: Si `ids_vigentes` se calculaba *después* del filtrado de sitios, cualquier equivalente declarado en una línea fuera del rango filtrado (por ejemplo, equivalente en línea 80 cuando se pasa `--lineas 10-20`) era considerado erróneamente como un "equivalente vencido" (`EquivalenteInvalido`), abortando la ronda.
- **Solución**: `ids_vigentes` y `total_sitios` se calculan a partir de todos los sitios de los objetivos descubiertos. Luego se aplica el filtrado a `sitios_por_ruta`. Así, los equivalentes válidos de otras líneas del archivo no causan falsas alarmas, y sólo se ejecutan/reportan aquellos equivalentes que caen dentro del subconjunto filtrado.

### D. Identidad de ronda y manifiesto
- `_identidad_ronda` incorpora `"parcial": parcial`. Esto garantiza que el hash de identidad de una ronda parcial sea distinto al de una ronda completa sobre el mismo objetivo, impidiendo que una ronda completa reanude erróneamente un manifiesto parcial o viceversa.

### E. Medidas del catálogo: División de responsabilidades
- El encargo pedía revisar `proceso.ronda_mutacion_concluyente.oracle` y `proceso.codigo_con_mutante_que_lo_mata.oracle`.
- **`proceso.ronda_mutacion_concluyente`**: Es el lugar arquitectónicamente correcto para juzgar la validez de una corrida de mutación. Se le añadió `c.parcial == true` a su condición `donde`. De este modo, si la evidencia contiene una ronda parcial, la medida la detecta como no concluyente y genera un hallazgo/violación (`resumen contar(1) > 0`).
- **`proceso.codigo_con_mutante_que_lo_mata`**: No se modificó. La relación `mutante` no contiene el campo `parcial` (pertenece a `corrida_mutacion`), y forzar un `unir` o un `requiere` acoplaría innecesariamente la medida de mutantes individuales con el estado de la corrida, rompiendo los casos unitarios del corpus que ejercitan la medida de mutantes en forma aislada (sin emitir `corrida_mutacion`). Además, el propio `alcance` preexistente de `codigo_con_mutante_que_lo_mata` ya lo documenta explícitamente:
  *«Tampoco juzga por sí sola si la ronda fue concluyente —eso lo mide proceso.ronda_mutacion_concluyente— ni si el bytecode estaba frío.»*
- Por ende, la custodia de la completitud de la ronda queda centralizada y limpia en `proceso.ronda_mutacion_concluyente`.

### F. Casos del corpus y regla de ausencia del álgebra de Oracle
- En el álgebra de Oracle (`nucleo/algebra.py`), una comparación de igualdad (`==`) sobre un campo ausente (`None`) no produce falso ni cortocircuita: produce `ErrorDeAlgebra: «==» sobre un valor ausente`.
- Al agregarse `c.parcial == true` a la medida `proceso.ronda_mutacion_concluyente`, todos los casos preexistentes del corpus que evalúan dicha medida (`016`, `017`, `019`, `108`) requerían tener la columna `parcial` en su tabla `corrida_mutacion`. Se les agregó `, parcial` con valor `false`.
- Se crearon los casos `111` (falso verde: ronda parcial que pretende ser concluyente) y `112` (verde correcto: ronda completa sin incidentes).

---

## 3. Dudas y notas para la revisión de Claude

1. **Mensajes de terminal**:
   - Se implementó el anuncio de ronda parcial en la primera línea de la salida (`*** RONDA PARCIAL DE MUTACIÓN (filtro: ...) ***`), en el resumen posterior a las ejecuciones, y en el cierre ("Todos los mutantes probados murieron, pero la ronda fue PARCIAL: se probaron X de Y sitios. Esto NO demuestra que los tests fijen el módulo completo."). Claude puede verificar si el fraseo y formato coinciden con las preferencias de estilo del CLI.
2. **Código de salida de `tools/mutar_codigo.py` en ronda parcial sin sobrevivientes**:
   - Tal como se razonó en el encargo y en el avance, una ronda parcial donde todos los mutantes evaluados mueren devuelve código de salida `0` en el CLI para permitir iteraciones rápidas al desarrollador mientras escribe tests. Sin embargo, la evaluación del catálogo (`proceso.ronda_mutacion_concluyente`) marca `✗` en la salida y fallaría en cualquier verificación formal de release (`oracle juzgar` / pipelines de CI). Si el filtro no selecciona ningún sitio, sale con código `2`.
3. **Casos del corpus**:
   - Se verificó que los casos 111 y 112 cumplan la sintaxis de `.caso`, con polaridades `falso_verde` y `verde_correcto`, vocabulario cerrado válido (`como_se_detecto: persona` y `observacion`), y los campos requeridos.

---

## 4. Declaración de verificación

De acuerdo con las reglas estrictas del encargo (sólo herramientas de lectura y edición, sin shell, sin ejecución de tests, sin subagentes, sin red, sin commits):
**Agy NO ejecutó la suite de tests ni comandos de terminal en esta sesión.** Toda la consistencia sintáctica, lógica y de esquemas fue verificada analíticamente mediante revisión estática de código y trazabilidad cruzada de archivos. La ejecución de la suite de tests y la validación final quedan delegadas a Claude.
