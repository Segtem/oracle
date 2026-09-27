# Avance: Eliminación de sobrevivientes del Runner Paralelo (SOBREVIVIENTES-RUNNER.txt)

**Fecha**: 2026-09-27  
**Tarea**: `20260926-212700-mutacion-niveles`  
**Autor**: agy (en contenedor de worktree)

---

## 1. Resumen de lo actuado

Se abordó la lista completa de 30 mutantes sobrevivientes de `tareas/20260926-212700-mutacion-niveles/SOBREVIVIENTES-RUNNER.txt` en `perfiles/python/mutacion_codigo.py` (28 `VIVO` y 2 `TIEMPO`).

1. **Nueva suite de tests**: Se creó [tests/test_mutacion_runner_paralelo.py](file:///work/tests/test_mutacion_runner_paralelo.py) con 25 tests unitarios rápidos y deterministas que cubren y matan cada uno de los mutantes alcanzables.
2. **Verificación manual rigurosa**: Cada uno de los 25 mutantes fue probado individualmente aplicando la mutación en [perfiles/python/mutacion_codigo.py](file:///work/perfiles/python/mutacion_codigo.py) (previa copia a `.bak`), purgando los directorios `__pycache__`, ejecutando el test correspondiente con `python3 -B -m unittest`, comprobando el fallo esperado (`FAIL` o `ERROR`), restaurando el código original y comprobando el paso a verde.
3. **Muerte de mutantes TIEMPO**: Los 2 mutantes con etiqueta `TIEMPO` en la línea 1236 (`and ↔ or` y `Is → IsNot`) colgaban o demoraban las corridas por fallback a ejecuciones completas o sobreescritura de cobertura. Se diseñaron tests rápidos (< 0.5s) que ejercitan los flujos exactos de carga y preservación del mapa de cobertura, logrando que el mutante falle de forma inmediata.
4. **Identificación de código que sobra**: Se identificaron 5 mutantes que provienen de código redundante/muerto, los cuales —siguiendo la instrucción del encargo— **no se declararon en equivalentes.json**, sino que se documentan a continuación para que Claude proceda a eliminarlos.
5. **No se modificó código de producción**: [perfiles/python/mutacion_codigo.py](file:///work/perfiles/python/mutacion_codigo.py) y demás archivos del perfil permanecen intactos.
6. **Suite completa en verde**: `python3 -B -m unittest discover -s tests` ejecutó los 2747 tests del repositorio (2722 previos + 25 nuevos) en 137.894s con resultado `OK`.

---

## 2. Detalle de los 30 mutantes de SOBREVIVIENTES-RUNNER.txt

### Grupo 1: `_comando_para_tests_seleccionados` (5 mutantes VIVO)

| # | Mutante | Operador | Cambio | Test en `test_mutacion_runner_paralelo.py` | Resultado verificación manual |
|---|---|---|---|---|---|
| 1 | `611:11:comparador` | comparador | `Lt → LtE` | `test_611_comparador_lt_a_lte` | `ERROR: IndexError: list index out of range` al recibir `--inicio` al final. |
| 2 | `611:17:constante` | constante | `1 → 2` | `test_611_constante_1_a_2` | `FAIL: AssertionError: '--inicio' not found` al evaluar `idx + 2 < len(cmd)` falso. |
| 3 | `603:11:comparador` | comparador | `In → NotIn` | `test_603_comparador_in_a_notin` | `FAIL: AssertionError: '/usr/local/bin/python3' != 'tools/ejecutar_suite_mutacion.py'`. |
| 4 | `612:53:constante` | constante | `1 → 2` | `test_612_constante_1_a_2` | `FAIL: AssertionError: 'otro' != 'tests'` al saltar un argumento de más. |
| 5 | `613:19:constante` | constante | `0 → 1` | `test_613_constante_0_a_1` | `FAIL: AssertionError: 'tools/ejecutar_...' != '/usr/local/bin/python3'`. |

---

### Grupo 2: `_correr_en_raiz` (14 mutantes VIVO)

*Nota sobre arquitectura*: `_correr_en_raiz` (líneas 915-1113) es la función secuencial previa a la introducción del paralelismo en `correr()`. Aunque `correr()` ya no la invoca directamente (ejecuta su propio bucle de trabajadores en copias aisladas), los mutantes fueron cubiertos y verificados con tests dedicados para garantizar cobertura total de la función:

| # | Mutante | Operador | Cambio | Test en `test_mutacion_runner_paralelo.py` | Resultado verificación manual |
|---|---|---|---|---|---|
| 6 | `941:28:negacion` | negacion | se borra `not` | `test_941_negacion_se_borra_not` | `ERROR: EquivalenteInvalido` con razón válida de string. |
| 7 | `956:76:comparador` | comparador | `In → NotIn` | `test_956_comparador_in_a_notin` | `FAIL: AssertionError` (filtra inversamente los sitios). |
| 8 | `959:11:comparador` | comparador | `Eq → NotEq` | `test_959_comparador_eq_a_noteq` | `ERROR: ValueError` al seleccionar 1 sitio válido (`sum != 0`). |
| 9 | `959:60:constante` | constante | `0 → 1` | `test_959_constante_0_a_1` | `ERROR: ValueError` al seleccionar 1 sitio válido (`sum == 1`). |
| 10 | `962:28:comparador` | comparador | `In → NotIn` | `test_962_comparador_in_a_notin` | `FAIL: AssertionError: False is not true` al ejecutar comando unitario del runner. |
| 11 | `975:23:constante` | constante | `0 → 1` | `test_975_constante_0_a_1` | `FAIL: AssertionError: 3 != 2` en `rondas_ejecutadas`. |
| 12 | `990:35:booleano` | booleano | `and ↔ or` | `test_990_booleano_and_a_or` | `FAIL: AssertionError: False is not true` con claves de línea string en JSON. |
| 13 | `1029:41:comparador` | comparador | `In → NotIn` | `test_1029_comparador_in_a_notin` | `FAIL: AssertionError` en la lista de `mutante_equivalente`. |
| 14 | `1036:15:booleano` | booleano | `and ↔ or` | `test_1036_booleano_and_a_or` | `FAIL: AssertionError: 'm.py:2:4:retorno' != ''` en `primer_inconcluso_id`. |
| 15 | `1051:39:negacion` | negacion | se borra `not` | `test_1051_negacion_se_borra_not` | `FAIL: AssertionError: 'm.py:2:15:constante' unexpectedly found in [...]`. |
| 16 | `1066:26:constante` | constante | `False → True` | `test_1066_constante_false_a_true` | `FAIL: AssertionError: True is not false` en `primer_fallo_salida_truncada`. |
| 17 | `1080:30:constante` | constante | `False → True` | `test_1080_constante_false_a_true` | `FAIL: AssertionError: True is not false` en `primer_inconcluso_salida_truncada`. |
| 18 | `1095:40:constante` | constante | `1 → 2` | `test_1095_constante_1_a_2` | `FAIL: AssertionError: 3 != 2` en `rondas_cache_verificadas`. |
| 19 | `1094:33:constante` | constante | `1 → 2` | `test_1094_constante_1_a_2` | `FAIL: AssertionError: 3 != 2` en `rondas_ejecutadas`. |

---

### Grupo 3: `correr` (6 mutantes: 4 VIVO y 2 TIEMPO)

| # | Mutante | Operador | Cambio | Test en `test_mutacion_runner_paralelo.py` | Resultado verificación manual |
|---|---|---|---|---|---|
| 21 | `1128:7:booleano` | booleano | `and ↔ or` | `test_1128_booleano_and_a_or` | `FAIL: AssertionError: ValueError not raised` con `paralelo=True`. |
| 22 | `1200:75:constante` | constante | `1 → 2` | `test_1200_constante_1_a_2` | `FAIL: AssertionError: 2 != 1` en llamadas a `_copiar_proyecto` con 0 pendientes. |
| 26 | `1221:15:comparador` | comparador | `Is → IsNot` | `test_1221_comparador_is_a_isnot` | `ERROR: LineaBaseFallida` al no inyectar `--guardar-cobertura` con `mapa=None`. |
| 27 | `1236:15:booleano` (TIEMPO) | booleano | `and ↔ or` | `test_1236_booleano_and_a_or_tiempo` | `FAIL: AssertionError: False is not true` en 0.465s (no cuelga). |
| 28 | `1236:15:comparador` (TIEMPO) | comparador | `Is → IsNot` | `test_1236_comparador_is_a_isnot_tiempo` | `FAIL: AssertionError: False is not true` en 0.271s (no cuelga). |
| 29 | `1272:47:booleano` | booleano | `and ↔ or` | `test_1272_booleano_and_a_or` | `FAIL: AssertionError: False is not true` al buscar líneas por clave string en el mapa. |

---

### Grupo 4: Código que sobra (5 mutantes)

Siguiendo el protocolo del encargo: *"si el sobreviviente viene de código que sobra, decilo en AVANCE en vez de declararlo (lo borra Claude)"*. Ninguno de estos se declaró en `equivalentes.json`:

1. **`1201:11:comparador` (`Lt → LtE`)**: en línea 1201 (`if n_trabajadores < 1:`).
2. **`1201:28:constante` (`1 → 2`)**: en línea 1201 (`if n_trabajadores < 1:`).
3. **`1202:29:constante` (`1 → 2`)**: en línea 1202 (`n_trabajadores = 1`).
   - *Diagnóstico*: En la línea 1200 se calcula `n_trabajadores = min(paralelo, len(pendientes)) if pendientes else 1`. Dado que `paralelo >= 1` es validado obligatoriamente en la línea 1128, y si `pendientes` no es vacío `len(pendientes) >= 1`, el valor resultante de la línea 1200 es **siempre estrictamente mayor o igual a 1**.
   - La guarda de las líneas 1201-1202:
     ```python
     if n_trabajadores < 1:
         n_trabajadores = 1
     ```
     es código defensivo muerto e inalcanzable. Con `LtE` o `1 → 2` en el comparador, en `n_trabajadores == 1` entra al bloque y reasigna `n_trabajadores = 1` (operación identidad sin efecto observable). Con `1 → 2` en la línea 1202 jamás se ejecuta.
   - *Acción recomendada*: Claude puede borrar las líneas 1201 y 1202.

4. **`1230:44:constante` (`True → False`)**: en línea 1230 (`permitir_cache_preexistente=True`).
   - *Diagnóstico*: En `correr()`, la ejecución de la línea base se realiza sobre el directorio `copia_0`, creado por `_copiar_proyecto(raiz, copia_0)`. `_copiar_proyecto` ignora explícitamente `shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo")`. Por lo tanto, en `copia_0` **es físicamente imposible que exista caché preexistente**. La comprobación `_caches_bajo(raiz)` siempre devuelve una lista vacía, de modo que `permitir_cache_preexistente=True` y `permitir_cache_preexistente=False` ejecutan exactamente el mismo código y jamás lanzan `CacheNoLimpio`. Además, el valor predeterminado de este parámetro en `_ejecutar_ronda` es `False`.
   - *Acción recomendada*: Claude puede eliminar el argumento `permitir_cache_preexistente=True,` de la llamada en la línea 1230.

5. **`1441:4:retorno` (`return <algo> → return None`)**: en línea 1441 (`return rastreador.serializar()` dentro de `construir_mapa_cobertura`).
   - *Diagnóstico*: La función `construir_mapa_cobertura` (líneas 1433-1442) quedó como un prototipo no integrado. En la arquitectura actual, la cobertura se recolecta a través de `ejecutar_suite_mutacion.py` con `--guardar-cobertura` durante la línea base en `correr()`. Ningún módulo del proyecto ni herramienta en `tools/` invoca a `construir_mapa_cobertura`. Además, la función contiene un `NameError` latente en la línea 1438 (`cargador = unittest.TestLoader()`, ya que `unittest` no está importado en `mutacion_codigo.py`), lo que confirma que nunca fue ejecutada.
   - *Acción recomendada*: Claude puede borrar la función completa `construir_mapa_cobertura` (líneas 1433-1442).

---

## 3. Verificación de la suite

```bash
$ python3 -B -m unittest tests/test_mutacion_runner_paralelo.py
.........................
----------------------------------------------------------------------
Ran 25 tests in 1.742s

OK

$ python3 -B tools/cifras.py
CIFRAS OK
  cifras: 2747 tests · 1018/1018 mutantes de medida · 9422 sitios de mutación de código (9129 + 293 del motor Python).

$ python3 -B -m unittest discover -s tests
...
Ran 2747 tests in 137.894s

OK
```

No se realizaron commits.
