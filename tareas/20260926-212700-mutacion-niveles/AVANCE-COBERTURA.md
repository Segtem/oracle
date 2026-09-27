# Avance: Cobertura de Mutantes en el Arnés de Suite y Rastreo (`tools/ejecutar_suite_mutacion.py`)

**Fecha**: 2026-09-27  
**Tarea**: `20260926-212700-mutacion-niveles`  
**Autor**: agy2 (en contenedor de worktree)  
**Lista procesada**: `tareas/20260926-212700-mutacion-niveles/SOBREVIVIENTES-COBERTURA.txt`  
**Archivo de tests**: `tests/test_ejecutar_suite_cobertura.py`  

---

## 1. Resumen del encargo y resultados

Se completó el encargo asignado sobre los 29 mutantes (26 VIVO y 3 TIEMPO) identificados en `tools/ejecutar_suite_mutacion.py` tras la primera corrida real de `--alto`.

- **Total de mutantes analizados**: 29
- **Mutantes eliminados (MUERTOS)**: 29 de 29 (100%)
- **Sobrevivientes restantes**: 0
- **Equivalentes declarados en `equivalentes.json`**: 0 (todos los mutantes resultaron ser distinguibles mediante pruebas de caja negra y contratos de comportamiento).
- **Código sobrante detectado**: Ninguno (todas las ramas y condiciones analizadas cumplen funciones indispensables de aislamiento, formato, fallback para entornos sin `sys.monitoring` o manejo de errores).
- **Tests rápidos para mutantes de tipo TIEMPO**: Los 3 mutantes TIEMPO (mutantes 10, 11 y 12) ahora fallan de inmediato (< 0.05 s) por aserciones directas de tipo, excepciones esperadas o contratos de retorno, eliminando cuelgues o timeouts.

---

## 2. Lectura y análisis línea por línea de `tools/ejecutar_suite_mutacion.py`

Se leyó detalladamente cada línea del archivo para comprender las causas de supervivencia original:

1. **Líneas 31–36 (`_RastreadorCobertura.__init__`, bloque `else`)**:
   - Descubrimiento por omisión cuando `objetivos` es vacío: recorre `self.tope.rglob("*.py")` excluyendo directorios `"tests"`, `".git"` y `"__pycache__"`.
   - Causa de supervivencia: los tests anteriores siempre pasaban una lista explícita de `objetivos`, por lo que el bloque `else` nunca se ejercitaba.
   - Eliminación: `test_descubrimiento_por_omision_filtra_directorios_excluidos` verifica la inclusión de módulos normales y la exclusión de carpetas restringidas.

2. **Líneas 39–41 (`_RastreadorCobertura.__init__`, detección de `sys.monitoring`)**:
   - Verifica `hasattr(sys, "monitoring") and hasattr(sys.monitoring, "COVERAGE_ID")`.
   - Causa de supervivencia: no se probaba la condición cuando `sys.monitoring` carece de `COVERAGE_ID`.
   - Eliminación: `test_deteccion_monitoring_requiere_coverage_id` prueba con un namespace de monitoring sin `COVERAGE_ID`, asegurando que `usando_monitoring` sea `False`.

3. **Líneas 49–58 (`_RastreadorCobertura.activar`, callback de línea `sys.monitoring`)**:
   - Callback `_line_cb`: valida `rel is not None and self.test_actual[0] is not None`, registra `line_number` bajo `rel` y retorna `sys.monitoring.DISABLE`.
   - Causa de supervivencia y timeouts:
     - Mutantes 6, 7, 8: no había tests que ejecutaran código fuera de la lista de archivos seguidos o fuera del ciclo de vida de un test.
     - Mutantes 9 y 10: reemplazaban índice `0` por `1` en `self.test_actual`, lo que provocaba `IndexError` no atrapado durante la ejecución masiva de la suite completa, colgando el arnés en bucles de manejo de excepciones (TIEMPO).
     - Mutante 11: retornaba `None` en vez de `sys.monitoring.DISABLE`, haciendo que el callback se invocara en cada línea de todo el intérprete y la stdlib (TIEMPO por lentitud masiva).
   - Eliminación: `test_line_cb_monitoring_filtro_y_registro` comprueba directamente que `_line_cb` filtre archivos no seguidos, ignore ejecuciones sin test activo, registre líneas y tests activos, y retorne exactamente `sys.monitoring.DISABLE`.

4. **Líneas 60–69 (`_RastreadorCobertura.activar`, callback fallback `sys.settrace`)**:
   - Rama alternativa cuando `usando_monitoring` es `False`.
   - Causa de supervivencia: en Python 3.12+ `usando_monitoring` es siempre `True`, por lo que el camino `sys.settrace` nunca era ejecutado. Mutante 12 daba TIEMPO porque `event != "line"` trazaba llamadas y retornos con un overhead inmenso.
   - Eliminación: `test_fallback_sys_settrace` fuerza `usando_monitoring = False` y verifica el comportamiento de `_trace` ante eventos `'line'` vs otros, frames ajenos y frames seguidos, asegurando que retorne la función de traza misma.

5. **Líneas 70–78 (`_RastreadorCobertura.desactivar`)**:
   - Apaga eventos con `sys.monitoring.set_events(self.tool_id, 0)` y libera el id de herramienta.
   - Causa de supervivencia: ningún test comprobaba el argumento exacto (`0`) enviado a `set_events`.
   - Eliminación: `test_desactivar_monitoring_apaga_eventos_con_cero` inspecciona que se llame con `0` y nunca con `1`.

6. **Líneas 80–84 (`_RastreadorCobertura.fijar_test`)**:
   - Asigna `self.test_actual[0] = test_id`.
   - Eliminación: `test_fijar_test_asigna_indice_cero` verifica la asignación y longitud de la lista.

7. **Líneas 85–94 (`_RastreadorCobertura.serializar` y `guardar`)**:
   - `serializar`: transforma conjuntos en listas ordenadas y claves en cadenas.
   - `guardar`: crea directorios con `parents=True, exist_ok=True` y escribe JSON formateado con `indent=1` y `ensure_ascii=False`.
   - Eliminación: `test_serializar_retorna_diccionario_ordenado`, `test_guardar_crea_directorios_padres_recursivamente`, `test_guardar_acepta_directorio_existente`, `test_guardar_formato_indentacion` y `test_guardar_preserva_caracteres_no_ascii`.

8. **Líneas 124–133 (`_correr_suite`)**:
   - Subclase `CoberturaRunner` con `_makeResult` retornando `CoberturaResult`, y ejecución con `verbosity=1, failfast=True`.
   - Eliminación: `test_correr_suite_con_rastreador_retorna_resultado_con_verbosidad_1` y `test_cobertura_result_fija_y_limpia_test_actual`.

9. **Líneas 194–196 (`main`, bloque `finally`)**:
   - `if rastreador and args.guardar_cobertura: rastreador.guardar(...)`.
   - Mutante 29 cambia `and` a `or`. Si el rastreador falló al crearse, `rastreador` es `None` y `or` intentaba invocar `None.guardar()`, rompiendo el manejo de error.
   - Eliminación: `test_main_guardar_cobertura_sin_rastreador_por_error_inicial`.

---

## 3. Matriz de verificación mutante por mutante

Cada mutante fue aplicado individualmente sobre `tools/ejecutar_suite_mutacion.py` (usando `mutar_fuente`), limpiando los directorios `__pycache__`, ejecutando `python3 -B -m unittest tests/test_ejecutar_suite_cobertura.py`, comprobando el fallo/error esperado, y restaurando el archivo original.

| N° | Tipo orig. | ID del Mutante | Operador y mutación | Veredicto | Test que lo mata y diagnóstico |
|---|---|---|---|---|---|
| 1 | VIVO | `tools/ejecutar_suite_mutacion.py:32:19:booleano` | `and ↔ or` | **MUERTO** | `FAIL: test_descubrimiento_por_omision_filtra_directorios_excluidos` (incluye `tests/test_algo.py`) |
| 2 | VIVO | `tools/ejecutar_suite_mutacion.py:32:19:comparador` | `NotIn → In` | **MUERTO** | `FAIL: test_descubrimiento_por_omision_filtra_directorios_excluidos` (excluye `modulo.py`) |
| 3 | VIVO | `tools/ejecutar_suite_mutacion.py:32:46:comparador` | `NotIn → In` | **MUERTO** | `FAIL: test_descubrimiento_por_omision_filtra_directorios_excluidos` (excluye `modulo.py`) |
| 4 | VIVO | `tools/ejecutar_suite_mutacion.py:32:72:comparador` | `NotIn → In` | **MUERTO** | `FAIL: test_descubrimiento_por_omision_filtra_directorios_excluidos` (excluye `modulo.py`) |
| 5 | VIVO | `tools/ejecutar_suite_mutacion.py:39:33:booleano` | `and ↔ or` | **MUERTO** | `FAIL: test_deteccion_monitoring_requiere_coverage_id` (`usando_monitoring` evalúa a `True`) |
| 6 | VIVO | `tools/ejecutar_suite_mutacion.py:51:19:booleano` | `and ↔ or` | **MUERTO** | `FAIL: test_line_cb_monitoring_filtro_y_registro` (`mapa` registra claves `None` o ejecuciones sin test) |
| 7 | VIVO | `tools/ejecutar_suite_mutacion.py:51:19:comparador` | `IsNot → Is` | **MUERTO** | `FAIL: test_line_cb_monitoring_filtro_y_registro` (`rel is None` descarta archivos seguidos) |
| 8 | VIVO | `tools/ejecutar_suite_mutacion.py:51:39:comparador` | `IsNot → Is` | **MUERTO** | `FAIL: test_line_cb_monitoring_filtro_y_registro` (descarta líneas cuando hay test activo) |
| 9 | VIVO | `tools/ejecutar_suite_mutacion.py:52:102:constante` | `0 → 1` | **MUERTO** | `ERROR: test_cobertura_result_fija_y_limpia_test_actual` (`IndexError: list index out of range` en callback) |
| 10 | **TIEMPO** | `tools/ejecutar_suite_mutacion.py:51:56:constante` | `0 → 1` | **MUERTO** | `ERROR: test_cobertura_result_fija_y_limpia_test_actual` (`IndexError` inmediato en guarda de callback, < 0.05s) |
| 11 | **TIEMPO** | `tools/ejecutar_suite_mutacion.py:56:16:retorno` | `return sys.monitoring.DISABLE → return None` | **MUERTO** | `FAIL: test_line_cb_monitoring_filtro_y_registro` (verifica que retorno sea `DISABLE` y no `None`, < 0.05s) |
| 12 | **TIEMPO** | `tools/ejecutar_suite_mutacion.py:61:19:comparador` | `Eq → NotEq` | **MUERTO** | `FAIL: test_fallback_sys_settrace` (verifica que evento `'line'` registre y evento `'call'` no, < 0.05s) |
| 13 | VIVO | `tools/ejecutar_suite_mutacion.py:63:23:booleano` | `and ↔ or` | **MUERTO** | `FAIL: test_fallback_sys_settrace` (`KeyError` o registro de `None` en frame ajeno) |
| 14 | VIVO | `tools/ejecutar_suite_mutacion.py:63:23:comparador` | `In → NotIn` | **MUERTO** | `ERROR: test_fallback_sys_settrace` (`KeyError: '/ruta/ajena.py'` al buscar en dict) |
| 15 | VIVO | `tools/ejecutar_suite_mutacion.py:63:59:comparador` | `IsNot → Is` | **MUERTO** | `FAIL: test_fallback_sys_settrace` (no registra cuando test activo no es `None`) |
| 16 | VIVO | `tools/ejecutar_suite_mutacion.py:65:109:constante` | `0 → 1` | **MUERTO** | `ERROR: test_fallback_sys_settrace` (`IndexError: list index out of range` en trace) |
| 17 | VIVO | `tools/ejecutar_suite_mutacion.py:63:76:constante` | `0 → 1` | **MUERTO** | `ERROR: test_fallback_sys_settrace` (`IndexError: list index out of range` en guarda) |
| 18 | VIVO | `tools/ejecutar_suite_mutacion.py:66:16:retorno` | `return _trace → return None` | **MUERTO** | `FAIL: test_fallback_sys_settrace` (retorno de `trace_fn` es `None` en lugar de la función) |
| 19 | VIVO | `tools/ejecutar_suite_mutacion.py:73:56:constante` | `0 → 1` | **MUERTO** | `FAIL: test_desactivar_monitoring_apaga_eventos_con_cero` (se invoca `set_events(tid, 1)`) |
| 20 | VIVO | `tools/ejecutar_suite_mutacion.py:86:8:retorno` | `return <algo> → return None` | **MUERTO** | `FAIL: test_guardar_formato_indentacion` (serializar devuelve `None`) |
| 21 | VIVO | `tools/ejecutar_suite_mutacion.py:81:25:constante` | `0 → 1` | **MUERTO** | `ERROR: test_cobertura_result_fija_y_limpia_test_actual` (`IndexError` al asignar en índice 1) |
| 22 | VIVO | `tools/ejecutar_suite_mutacion.py:92:34:constante` | `True → False` | **MUERTO** | `ERROR: test_guardar_crea_directorios_padres_recursivamente` (`FileNotFoundError` sin `parents`) |
| 23 | VIVO | `tools/ejecutar_suite_mutacion.py:92:49:constante` | `True → False` | **MUERTO** | `ERROR: test_guardar_acepta_directorio_existente` (`FileExistsError` sin `exist_ok`) |
| 24 | VIVO | `tools/ejecutar_suite_mutacion.py:93:61:constante` | `1 → 2` | **MUERTO** | `FAIL: test_guardar_formato_indentacion` (indentación difiere: 2 espacios vs 1 espacio) |
| 25 | VIVO | `tools/ejecutar_suite_mutacion.py:93:77:constante` | `False → True` | **MUERTO** | `FAIL: test_guardar_preserva_caracteres_no_ascii` (caracteres no ASCII son escapados como `\u00f3`) |
| 26 | VIVO | `tools/ejecutar_suite_mutacion.py:126:12:retorno` | `return <algo> → return None` | **MUERTO** | `ERROR: test_cobertura_result_fija_y_limpia_test_actual` (`AttributeError: 'NoneType' object has no attribute 'startTest'`) |
| 27 | VIVO | `tools/ejecutar_suite_mutacion.py:130:8:retorno` | `return <algo> → return None` | **MUERTO** | `FAIL: test_cobertura_result_fija_y_limpia_test_actual` (retorno de `_correr_suite` es `None`) |
| 28 | VIVO | `tools/ejecutar_suite_mutacion.py:130:41:constante` | `1 → 2` | **MUERTO** | `FAIL: test_correr_suite_con_rastreador_retorna_resultado_con_verbosidad_1` (`showAll` es `True`, `dots` es `False`) |
| 29 | VIVO | `tools/ejecutar_suite_mutacion.py:195:11:booleano` | `and ↔ or` | **MUERTO** | `ERROR: test_main_guardar_cobertura_sin_rastreador_por_error_inicial` (`AttributeError: 'NoneType' object has no attribute 'guardar'`) |

---

## 4. Archivos modificados o creados

- **Creado**: `tests/test_ejecutar_suite_cobertura.py` (14 tests unitarios enfocados y rápidos, tiempo de ejecución ~0.05 s).
- **Creado**: `tareas/20260926-212700-mutacion-niveles/AVANCE-COBERTURA.md` (este informe).
- **Sin modificaciones en el código bajo prueba**: `tools/ejecutar_suite_mutacion.py` no fue alterado; conservó intacto su código original tras cada verificación con `.bak`.
- **Sin commits**: Ningún commit fue realizado, en estricto cumplimiento de la consigna.

---

## 5. Verificación de la suite completa

- **Comando**: `python3 -B -m unittest discover -s tests`
- **Resultado**: `Ran 2736 tests in 135.800s, OK`.
- **Estado**: 100% en verde.
- **Suite específica nueva**: `python3 -B -m unittest tests/test_ejecutar_suite_cobertura.py` (Ran 14 tests in 0.049s, OK).

---

## 6. Próximo paso

Esperar la finalización del encargo de `SOBREVIVIENTES-RUNNER.txt` (`tests/test_mutacion_runner_paralelo.py`) para consolidar la ronda de mutación de nivel `--alto`.

