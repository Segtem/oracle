# Informe de entrega — Hito 0.24.0 (límite de memoria en el arnés de mutación)

**Tarea**: `tareas/20260915-112728-memoria`  
**Encargo**: `estudios/0.24.0-memoria/ENCARGO-AGY.md`  

---

## 1. Resumen de lo implementado

Se completó íntegramente la implementación del hito 0.24.0 para limitar el consumo de memoria en la ejecución de mutantes y líneas base del arnés de mutación:

1. **Límite de memoria por subproceso en `perfiles/python/mutacion_codigo.py`**:
   - Se importó condicionalmente el módulo estándar `resource` (`try: import resource except ImportError: resource = None`) para entornos POSIX.
   - Se definió la constante `LIMITE_MEMORIA_PREDETERMINADO = 4000 * 1024 * 1024` (4000 MiB expresados en bytes).
   - `ejecutar_tests` incorpora el parámetro `limite_memoria: int | None = None`. Valida exhaustivamente que el argumento sea entero no negativo (`None` representa sin límite, `0` desactiva el límite; booleanos, negativos y tipos no enteros levantan `ValueError`).
   - El límite se aplica en el proceso hijo vía `subprocess.Popen(..., preexec_fn=_aplicar_limites, start_new_session=True)`, invocando `resource.setrlimit(resource.RLIMIT_AS, (limite_memoria, limite_memoria))`.
   - Se documentó en la función que un mutante que exceda el tope termina con `MemoryError` (código de salida 1), lo que clasifica como `EstadoTests.TESTS_FALLARON` y cuenta como mutante muerto (`murio = True`), distinguiéndose de `timeout` y de `error_arnes`.

2. **Propagación completa en el arnés de mutación**:
   - `_ejecutar_ronda`: recibe `limite_memoria: int | None = None` y lo pasa a `ejecutar_tests`.
   - `_identidad_ronda`: incorpora el campo `"limite_memoria": limite_memoria` junto con `"limite_salida"`, `"timeout"`, etc.
   - `_correr_en_raiz`: recibe `limite_memoria: int | None = LIMITE_MEMORIA_PREDETERMINADO`, valida la entrada, y la propaga tanto a la ejecución de la línea base como a cada una de las rondas de los mutantes. Si la línea base excede la memoria asignada, aborta inmediatamente levantando `LineaBaseFallida`.
   - `correr`: expone `limite_memoria: int | None = LIMITE_MEMORIA_PREDETERMINADO`, lo valida, lo incluye en la identidad de la ronda y lo delega a `_correr_en_raiz`.

3. **Interfaz de línea de comandos en `tools/mutar_codigo.py`**:
   - Se incorporó la constante `LIMITE_MEMORIA_MB_PREDETERMINADO = 4000`.
   - En `argumentos()` se agregó la opción `--limite-memoria-mb` (tipo `int`, predeterminado 4000, ayuda indicando que 0 desactiva).
   - En `_ejecutar()`, se valida que `args.limite_memoria_mb >= 0` (valores negativos levantan `ValueError`, que es atrapado por el manejador de la herramienta retornando código de salida 2 sin traceback, emitiendo JSON bajo `--hechos` o mensaje en `stderr`).
   - Se realiza la conversión de MiB a bytes (`args.limite_memoria_mb * 1024 * 1024` si es mayor a cero, o `None` si es 0) y se pasa a `correr(..., limite_memoria=limite_memoria)`.

4. **Batería de pruebas en `tests/test_mutacion_codigo.py`**:
   - Se añadió la clase `LimiteMemoriaTests` al final del archivo, conteniendo 9 métodos de test que cubren exhaustivamente todos los requisitos de verificación.

---

## 2. Decisiones tomadas y rationale

1. **Uso de `resource.RLIMIT_AS` en lugar de límites de RSS física o cgroups**:
   - `RLIMIT_AS` limita el tamaño total del espacio de direcciones virtuales del proceso (`virtual memory`).
   - En sistemas operativos Linux/POSIX, las asignaciones grandes (`bytearray`, buffers grandes, etc.) solicitan espacio de direccionamiento virtual al kernel vía `mmap` o `brk`. Si la solicitud excede `RLIMIT_AS`, el kernel falla de inmediato con `ENOMEM`, haciendo que CPython levante `MemoryError` instantáneamente sin necesidad de paginar ni tocar RAM física real.
   - Esto permite escribir pruebas deterministas, veloces (del orden de milisegundos) e inmunes a máquinas de CI con poca memoria o sin swap.

2. **Aplicación en el subproceso hijo mediante `preexec_fn`**:
   - `subprocess.Popen` con `start_new_session=True` ejecuta `os.setsid()` en el hijo tras `fork`, creando un nuevo grupo de procesos y sesión.
   - `preexec_fn` se invoca en el proceso hijo inmediatamente antes de `execve`. De este modo:
     * El proceso padre retiene inalterados sus límites de recursos (`resource.getrlimit(resource.RLIMIT_AS)` es idéntico antes y después).
     * El límite rige exclusivamente para el subproceso de prueba y cualquier proceso descendiente generado por éste.
     * No interfiere con el aislamiento de sesión ni con el envío de señales por grupo de procesos (`os.killpg`).

3. **Convención de `MemoryError` como fallo discriminante (código 1 / `TESTS_FALLARON`)**:
   - En CPython, cuando una excepción `MemoryError` no es capturada en el script de prueba, el intérprete imprime el traceback en `stderr` y finaliza con código de salida 1.
   - Dado que el arnés tiene configurado `CODIGOS_FALLO_PREDETERMINADOS = frozenset({1})`, un código 1 se mapea a `EstadoTests.TESTS_FALLARON`.
   - Esto es conceptualmente exacto: el mutante alteró el código de forma tal que provocó una falla de ejecución en los tests; por ende, el mutante fue detectado y murió (`murio = True`). No constituye un `timeout` (no consumió el tiempo de pared límite) ni un `error_arnes` (que se reserva para señales externas o fallos estructurales del arnés).

4. **Identidad de ronda y esquemas de relaciones**:
   - `_identidad_ronda` genera el diccionario de parámetros operacionales que identifica la ronda en los manifiestos de reanudación. Se añadió `"limite_memoria": limite_memoria` de forma análoga a `"limite_salida"` y `"timeout"`.
   - Se verificó el esquema `relaciones/corrida_mutacion.json`: este esquema define exclusivamente métricas observadas a posteriori (`timeouts`, `errores_arnes`, `tiempo_ms`, `bytecode_frio`, etc.) y no parámetros de configuración operacional del invocador (no tiene `timeout` ni `limite_salida`). Por lo tanto, no requirió cambios de esquema.

---

## 3. Archivos modificados y creados

- **`estudios/0.24.0-memoria/AVANCE-AGY.md`**: Plan inicial de trabajo y decisiones de diseño (creado).
- **`perfiles/python/mutacion_codigo.py`**:
  - Importación condicional de `resource`.
  - Constante `LIMITE_MEMORIA_PREDETERMINADO`.
  - Soporte y validación de `limite_memoria` en `ejecutar_tests`, `_ejecutar_ronda`, `_identidad_ronda`, `_correr_en_raiz` y `correr`.
- **`tools/mutar_codigo.py`**:
  - Constante `LIMITE_MEMORIA_MB_PREDETERMINADO`.
  - Opción `--limite-memoria-mb` en `argumentos()`.
  - Validación y conversión a bytes en `_ejecutar()`.
  - Documentación del docstring actualizada.
- **`tests/test_mutacion_codigo.py`**:
  - Incorporación de la clase `LimiteMemoriaTests` al final del archivo (líneas 1212-1483).
- **`estudios/0.24.0-memoria/INFORME-AGY.md`**: Informe final de entrega (creado).

---

## 4. Tests nuevos en `tests/test_mutacion_codigo.py`

La clase `LimiteMemoriaTests` incorpora las siguientes pruebas:

1. `test_constantes_limite_memoria`:
   - Verifica que `mc.LIMITE_MEMORIA_PREDETERMINADO` equivale exactamente a 4000 MiB en bytes (`4000 * 1024 * 1024 = 4_194_304_000`).
   - Verifica que `mutar_codigo.LIMITE_MEMORIA_MB_PREDETERMINADO` es `4000`.

2. `test_limite_memoria_limita_al_hijo_y_se_ejecuta_en_el_hijo`:
   - Aplica un tope de 100 MiB y un subproceso que intenta reservar 300 MiB (`bytearray(300 * 1024 * 1024)`).
   - Verifica que el subproceso falla con `EstadoTests.TESTS_FALLARON`, `codigo_salida == 1`, `murio == True`, y `MemoryError` en su salida.
   - Comprueba que el proceso padre mantiene inalterado su `resource.getrlimit(resource.RLIMIT_AS)` antes y después de la invocación.
   - Comprueba que sin límite (`limite_memoria=None`), la misma asignación pasa exitosamente con código 0.
   - Verifica que el subproceso opera bajo `start_new_session=True` corriendo en su propio grupo de procesos (`os.getpgrp() != hijo_pgrp`).

3. `test_mutante_que_excede_memoria_cuenta_como_muerto_no_timeout_ni_error`:
   - Ejecuta una ronda con un objetivo y un comando de test que sólo intenta reservar 300 MiB cuando el archivo en disco difiere de la fuente original (es decir, en el mutante).
   - La línea base pasa limpia (`baseline_verde = True`).
   - El mutante intenta reservar 300 MiB bajo un tope de 100 MiB: muere con código 1 y el arnés lo registra como `murio = True`, `tests_fallaron = True`, `timeout = False`, `error_arnes = False`.
   - En el resumen de la corrida se constata `muertos == mutantes`, `timeouts == 0` y `errores_arnes == 0`.

4. `test_linea_base_usa_el_mismo_tope_y_falla_si_lo_excede`:
   - Ejecuta una ronda donde el comando de test siempre reserva 300 MiB.
   - Con un tope de 100 MiB, la línea base falla inmediatamente levantando `LineaBaseFallida`.
   - Se comprueba que `ctx.exception.resultado.estado` es `TESTS_FALLARON` con código 1 y que el archivo fuente original permanece intacto.

5. `test_limite_memoria_cero_desactiva_tope`:
   - Verifica que pasar `limite_memoria=0` desactiva el límite tanto en `ejecutar_tests` directo como a través de `correr` completo, permitiendo que una asignación de 300 MiB pase sin error.

6. `test_limite_memoria_invalido_se_rechaza`:
   - Verifica que valores no válidos (`-1`, `-1024`, `True`, `False`, `1.5`, `"1024"`, `[1024]`) levantan `ValueError` en `ejecutar_tests`, en `_correr_en_raiz` y en `correr`.

7. `test_identidad_ronda_declara_limite_memoria`:
   - Comprueba que `_identidad_ronda` incluye `"limite_memoria"` con su valor numérico cuando está activo, y como `None` cuando está desactivado.

8. `test_cli_limite_memoria_mb_parseo_y_valores`:
   - Verifica el parseo de `--limite-memoria-mb` en `tools.mutar_codigo.argumentos`: default (4000), explícito (2048) y desactivación (0).

9. `test_cli_limite_memoria_mb_propagacion_a_correr`:
   - Mediante mock de `mutar_codigo.correr`, comprueba la conversión exacta a bytes y la propagación de `limite_memoria` para:
     * Sin bandera (usa default 4000 MB -> `4000 * 1024 * 1024` bytes).
     * `--limite-memoria-mb 2048` (pasa `2048 * 1024 * 1024` bytes).
     * `--limite-memoria-mb 0` (pasa `None`).

10. `test_cli_limite_memoria_mb_negativo_se_rechaza`:
    - Verifica que pasar un valor negativo (`--limite-memoria-mb -1`) hace que `main()` termine con código 2 sin invocar `correr`.
    - Verifica que sin `--hechos` emite mensaje descriptivo en `stderr`.
    - Verifica que con `--hechos` emite un documento JSON con `error_mutacion` de tipo `ValueError`.

---

## 5. Contradicciones y notas sobre tests preexistentes

- **`test_la_politica_operativa_predeterminada_es_unica_y_explicita` (`tests/test_mutacion_codigo.py:913-924`)**:
  Este test existente realiza aserciones puntuales sobre un conjunto predefinido de constantes (`TIMEOUT_PREDETERMINADO`, `LIMITE_SALIDA_PREDETERMINADO`, etc.).
  Siguiendo la regla estricta: *"no edites tests existentes (anotá contradicciones en el informe)"*, el test existente no fue modificado. La validación de la nueva constante `LIMITE_MEMORIA_PREDETERMINADO` se ubicó en `test_constantes_limite_memoria`.

---

## 6. Estado de verificación

En cumplimiento estricto de las reglas operativas indicadas:
- **NO se ejecutó ningún comando en la shell** (`run_command`).
- **NO se ejecutaron tests automáticos ni suites de mutación**.
- **NO se utilizaron subagentes ni conexiones de red**.
- **NO se realizaron commits**.
- Todo el código fue inspeccionado y validado de manera estática y analítica.
