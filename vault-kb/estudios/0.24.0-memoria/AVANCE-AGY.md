# Avance 0.24.0 — Tope de memoria por ejecución en mutación de código

Fecha: 2026-09-16  
Tarea: `tareas/20260915-112728-memoria`  
Encargo: `vault-kb/estudios/0.24.0-memoria/ENCARGO-AGY.md`  

---

## 1. Análisis del problema y decisiones de diseño

1. **Problema**:
   - `tools/mutar_codigo.py` acota tiempo y volumen de salida, pero no memoria.
   - Ciertos mutantes (p. ej. bucles de generación de tokens en `tokenizar`) consumen toda la memoria RAM de la máquina antes de agotar el timeout, provocando que el OOM-killer del sistema operativo liquide la ronda o procesos del entorno.
   - Un mutante que agota su memoria asignada produce `MemoryError` en Python (código de salida 1), lo que constituye una detección por fallo de tests (`tests_fallaron=True`, mutante muerto), no un timeout ni un error de arnés.

2. **Aplicación del tope en `perfiles/python/mutacion_codigo.py`**:
   - Se incorpora `LIMITE_MEMORIA_PREDETERMINADO = 4000 * 1024 * 1024` (4000 MiB en bytes).
   - En `ejecutar_tests`:
     * Se agrega el parámetro `limite_memoria: int | None = None` (en bytes, `None` = sin tope).
     * Se valida: si no es `None`, debe ser un entero (`int`, excluyendo `bool`) mayor o igual a 0. Si es `0`, se normaliza a `None` (0 desactiva). Valores negativos o tipos incorrectos levantan `ValueError`.
     * Se aplica en el hijo mediante `preexec_fn` usando `resource.setrlimit(resource.RLIMIT_AS, (limite_memoria, limite_memoria))`.
     * El proceso padre no altera sus propios límites.
     * Se preserva el grupo de procesos (`start_new_session=True`), la terminación limpia por grupo (`_terminar_proceso`) y la lectura acotada de salida (`_leer_acotado`).
   - En `_ejecutar_ronda`:
     * Se propaga `limite_memoria` hacia `ejecutar_tests`.
   - En `_correr_en_raiz`:
     * Acepta `limite_memoria: int | None = LIMITE_MEMORIA_PREDETERMINADO`.
     * Ejecuta la línea base con dicho límite: si el límite es demasiado bajo para los tests no mutados, falla de inmediato con `LineaBaseFallida` antes de generar mutantes.
     * Ejecuta cada mutante con el mismo límite.
   - En `correr`:
     * Acepta `limite_memoria: int | None = LIMITE_MEMORIA_PREDETERMINADO`.
     * Incluye `"limite_memoria": limite_memoria` en `_identidad_ronda` junto a `limite_salida`, de modo que el manifiesto registre la configuración y evite reanudar con cotas distintas.

3. **CLI en `tools/mutar_codigo.py`**:
   - Se añade el argumento `--limite-memoria-mb` (tipo `int`, por omisión `4000`, `0` para desactivar).
   - Validación: si es menor que 0, levanta `ValueError` (atrapado e informado como corrida no confiable).
   - Conversión a bytes: `limite_memoria = args.limite_memoria_mb * 1024 * 1024 if args.limite_memoria_mb > 0 else None`.
   - Se pasa `limite_memoria=limite_memoria` a `correr()`.

4. **Nuevos tests en `tests/test_mutacion_codigo.py`**:
   - Comprobar que el límite restringe efectivamente al proceso hijo (un comando que asigna más memoria que el tope falla con código 1 `tests_fallaron`, y pasa con código 0 sin tope).
   - Comprobar que un mutante que excede memoria se computa como muerto (`murio=True`, `tests_fallaron=True`, `timeout=False`, `error_arnes=False`).
   - Comprobar que la línea base corre bajo el mismo límite y aborta con `LineaBaseFallida` si lo excede.
   - Comprobar que `limite_memoria=0` desactiva el límite.
   - Comprobar que valores inválidos (negativos, flotantes, booleanos) se rechazan con `ValueError`.
   - Pruebas dimensionadas de forma independiente a la RAM física (usando reservas virtuales moderadas de ~200-300 MiB contra un tope de 50-100 MiB).

---

## 2. Plan de archivos

### Archivos a crear
- `vault-kb/estudios/0.24.0-memoria/AVANCE-AGY.md` (este archivo)
- `vault-kb/estudios/0.24.0-memoria/INFORME-AGY.md` (al finalizar)

### Archivos a modificar
- `perfiles/python/mutacion_codigo.py`: soporte de `resource.setrlimit`, parámetros `limite_memoria`, validaciones, propagación en línea base/mutantes e identidad de ronda.
- `tools/mutar_codigo.py`: argumento `--limite-memoria-mb`, validación y conversión a bytes.
- `tests/test_mutacion_codigo.py`: incorporación de nueva clase de pruebas `LimiteMemoriaTests` al final del archivo, sin modificar ningún test preexistente.
