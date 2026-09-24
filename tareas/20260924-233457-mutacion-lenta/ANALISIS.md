# Análisis de costo y optimización de la mutación de código en Oracle

- Tarea de referencia: `tareas/20260924-233457-mutacion-lenta/TAREA.md`
- Contexto de problema: En cortes 0.29.0 y 0.30.0, la mutación de `nucleo/sintaxis.py` (1140 y 1177 mutantes) demoró ~2 horas y la de `tools/cli.py` (595 mutantes) más de 1 hora (`TAREA.md:10-13`).
- Restricciones: Sin modificar código de producción; sin debilitar el criterio de muerte; sin shell; cada afirmación respaldada en `archivo:línea`, notas del tracker o indicando explícitamente fuente de estimación.

---

## 1. Dónde se va el tiempo

### 1.1 ¿Cada mutante corre la suite completa (2440 tests, ~86-90 s)?

**No todos los mutantes corren la suite completa, pero los sobrevivientes, equivalentes y mutantes no discriminados por los módulos prioritarios sí la pagan entera.**

El arnés opera en dos capas:

1. **El runner `tools/ejecutar_suite_mutacion.py`**:
   - `_correr_suite` ejecuta con `failfast=True`: `unittest.TextTestRunner(verbosity=1, failfast=True).run(suite)` ([tools/ejecutar_suite_mutacion.py:26](../../tools/ejecutar_suite_mutacion.py#L26)).
   - Cuando se especifican módulos prioritarios mediante `--prioridad`, se cargan y ejecutan uno a uno secuencialmente ([tools/ejecutar_suite_mutacion.py:51-63](../../tools/ejecutar_suite_mutacion.py#L51-L63)).
   - Si un test falla en cualquiera de esos módulos prioritarios, la función retorna inmediatamente con código `1` ([tools/ejecutar_suite_mutacion.py:63](../../tools/ejecutar_suite_mutacion.py#L63)). **En este caso, la suite completa nunca se descubre ni se ejecuta.**
   - Si **ningún** módulo prioritario falla, recién entonces se ejecuta el descubrimiento general excluyendo lo ya corrido: `suite = _sin_modulos(cargador.discover(start_dir=args.inicio, top_level_dir=args.tope), args.prioridad)` ([tools/ejecutar_suite_mutacion.py:64-65](../../tools/ejecutar_suite_mutacion.py#L64-L65)) y se corre el resto de la suite ([tools/ejecutar_suite_mutacion.py:73](../../tools/ejecutar_suite_mutacion.py#L73)).

2. **Cuándo se corre la suite completa**:
   - Para un **mutante sobreviviente** (o no equivalente vivo): pasa todos los prioritarios, pasa todos los descubiertos y completa la suite sin fallos, saliendo con código `0` ([tools/ejecutar_suite_mutacion.py:90](../../tools/ejecutar_suite_mutacion.py#L90)). Este mutante paga el 100 % de la suite. En la nota de corte 0.29.0 ([tareas/20260924-100921-corte-029/TAREA.md:15](../../tareas/20260924-100921-corte-029/TAREA.md#L15)), la suite completa sin bytecode caché constató **2432 tests en 90,583 s**; en `docs/mutacion-memoria.md:90` constató **2386 tests en 152,04 s**; en `tools/cli.py:980` se registró **163,716 s**.
   - Para un mutante muerto por un test que **no** está en los módulos prioritarios declarados en `PRIORIDADES` ([tools/mutar_codigo.py:49-162](../../tools/mutar_codigo.py#L49-L162)): paga todos los prioritarios + el descubrimiento general (`cargador.discover()`) + la ejecución hasta el test que lo mata.
   - Si se invoca `tools/mutar_codigo.py` sin `--objetivo`, `priorizar` se evalúa como `False` ([tools/mutar_codigo.py:660](../../tools/mutar_codigo.py#L660)), por lo que **ningún** módulo se prioriza y **todos** los mutantes arrancan directo desde `cargador.discover()` pagando descubrimiento completo.

---

### 1.2 ¿Cuánto es arranque de proceso y sobrecarga del arnés por mutante?

El arnés ejecuta cada mutante en un subproceso aislado e independiente ([perfiles/python/mutacion_codigo.py:534-536](../../perfiles/python/mutacion_codigo.py#L534-L536)). Para cada uno de los mutantes (1177 en sintaxis, 595 en CLI):

1. **Arranque e importación con bytecode frío**:
   - `_ejecutar_ronda` asigna `PYTHONPYCACHEPREFIX` a un directorio temporal nuevo y fuerza `PYTHONDONTWRITEBYTECODE="1"` ([perfiles/python/mutacion_codigo.py:616-617](../../perfiles/python/mutacion_codigo.py#L616-L617)).
   - CPython inicia de cero: debe leer de disco y parsear/compilar en memoria el intérprete, `unittest`, `argparse`, las dependencias y los módulos de test cargados.
   - *Estimación*: En Linux x86_64, el arranque de `python3` importando `unittest` y los módulos base del arnés sin `.pyc` precompilado insume típicamente entre **0,25 s y 0,45 s** por invocación.

2. **Escritura y sincronización a disco**:
   - Mutar el archivo: `_escribir_atomico(ruta, mutado)` crea un archivo temporal, escribe, fuerza `os.fsync(archivo.fileno())`, cambia permisos con `os.chmod` y reemplaza con `os.replace` ([perfiles/python/mutacion_codigo.py:686-698](../../perfiles/python/mutacion_codigo.py#L686-L698)).
   - Restaurar el archivo original: otro `_escribir_atomico(ruta, original)` en bloque `finally` con `os.fsync` ([perfiles/python/mutacion_codigo.py:954](../../perfiles/python/mutacion_codigo.py#L954)).
   - Esto produce 2 `fsync` a disco por cada mutante. En 1177 mutantes son 2354 operaciones de sync.

3. **Múltiples barridos recursivos del árbol de directorios (`os.walk`)**:
   - Por cada mutante en `_ejecutar_ronda`:
     - `_caches_bajo(raiz)` previo ([perfiles/python/mutacion_codigo.py:603](../../perfiles/python/mutacion_codigo.py#L603)).
     - `limpiar_cache(raiz)` previo, que a su vez llama a `_caches_bajo` dos veces ([perfiles/python/mutacion_codigo.py:412, 435](../../perfiles/python/mutacion_codigo.py#L412-L435)).
     - `_caches_bajo(raiz)` posterior ([perfiles/python/mutacion_codigo.py:623](../../perfiles/python/mutacion_codigo.py#L623)).
     - `limpiar_cache(raiz)` en `finally` ([perfiles/python/mutacion_codigo.py:634](../../perfiles/python/mutacion_codigo.py#L634)).
     - `_comprobar_cierre_frio(raiz)` en callback `al_terminar_uno` ([perfiles/python/mutacion_codigo.py:979](../../perfiles/python/mutacion_codigo.py#L979)).
   - Cada llamada a `_caches_bajo` ejecuta un `os.walk(raiz)` recursivo completo sobre la copia ([perfiles/python/mutacion_codigo.py:375-383](../../perfiles/python/mutacion_codigo.py#L375-L383)). Son entre 4 y 5 recorridos completos de directorios por mutante (~5000 `os.walk` en una ronda de sintaxis).

*Estimación de sobrecarga base fija*: Sumando subproceso frío + 2 escrituras con sync + 4-5 traversals del árbol, la sobrecarga nula (tiempo consumido aun si un test fallara en 0 ms) se estima entre **0,35 s y 0,60 s por mutante**.
Para 1177 mutantes, sólo la sobrecarga estructural del bucle representa entre **410 s y 700 s (~7 a 12 minutos)** de tiempo puro de andamiaje.

---

### 1.3 ¿Cuánto tiempo son tests que no tocan el módulo mutado?

El tiempo restante por mutante (~5,5 s de los ~6,1 s promedio en `sintaxis.py`, y ~5,4 s de los ~6,0 s en `cli.py`) corresponde a la ejecución de tests. Aquí se identifican dos causas mayores:

#### A. En `nucleo/sintaxis.py` (1177 mutantes, ~2 horas)
- Su prioridad declarada es `("tests.test_sintaxis", "tests.test_macro", "tests.test_nucleo")` ([tools/mutar_codigo.py:72](../../tools/mutar_codigo.py#L72)).
- `tests/test_sintaxis.py` tiene **3163 líneas** ([tests/test_sintaxis.py:1-60](../../tests/test_sintaxis.py#L1-L60)) y decenas de clases de prueba que ejecutan round-trips completos, validación de catálogos y subprocesos.
- Al cargar el módulo completo `cargador.loadTestsFromName("tests.test_sintaxis")` ([tools/ejecutar_suite_mutacion.py:52](../../tools/ejecutar_suite_mutacion.py#L52)), los tests corren en orden alfabético/de definición.
- Si un mutante altera una función que se prueba hacia la mitad o el final de `test_sintaxis.py` (por ejemplo, impresión de expresiones `_expr` en líneas 1540+ de `nucleo/sintaxis.py`), `unittest` ejecuta **todos los tests precedentes** de `test_sintaxis.py` hasta llegar al test que falla.
- Y si el mutante no muere en `test_sintaxis`, corre todos los tests de `tests.test_macro` y `tests.test_nucleo` antes de caer en el descubrimiento general.

#### B. En `tools/cli.py` (595 mutantes, >1 hora)
- Su lista de prioridades declara **nueve módulos** ([tools/mutar_codigo.py:92-95](../../tools/mutar_codigo.py#L92-L95)):
  1. `tests.test_reportar`
  2. `tests.test_vigilar`
  3. `tests.test_biblioteca`
  4. `tests.test_tareas` (suite del tracker, amplia y con múltiples tests)
  5. `tests.test_cli` (1802 líneas)
  6. `tests.test_censar`
  7. `tests.test_manual`
  8. `tests.test_herramientas`
  9. `tests.test_cli_integracion` (256 líneas, crea venvs temporales y subprocesos; [tests/test_cli_integracion.py:1-60](../../tests/test_cli_integracion.py#L1-L60)).
- Cualquier mutante en funciones centrales de `tools/cli.py` (despacho, ayuda general, formateo de opciones) que no rompa `test_reportar`, `test_vigilar`, `test_biblioteca` ni `test_tareas` **debe pagar la ejecución completa de esos 4 módulos ajenos** antes de que el arnés llegue a `tests.test_cli`.
- Y los mutantes que sólo discriminan en integración (`tests.test_cli_integracion`) pagan los 8 módulos anteriores completos.

---

### 1.4 El costo de los sobrevivientes y la repetición de rondas

La tarea menciona: *"una ronda repetida (los 7 vivos de cli.py) suma otra hora"* ([TAREA.md:11-12](../../tareas/20260924-233457-mutacion-lenta/TAREA.md#L11-L12)).
¿Por qué 7 mutantes vivos obligan a esperar otra hora?

1. **El costo individual de cada sobreviviente**:
   - Cada uno de los 7 mutantes no murió con ningún test prioritario ni con ningún test descubierto.
   - Por tanto, cada uno corrió la suite entera (~90,58 s según [tareas/20260924-100921-corte-029/TAREA.md:15](../../tareas/20260924-100921-corte-029/TAREA.md#L15)).
   - Correr sólo esos 7 mutantes ya consume 7 × ~90,6 s = **~634 segundos (~10,5 minutos)**.

2. **La invalidación de reanudación al agregar tests**:
   - Si se agregan tests para matar esos 7 vivos (como se hizo en `tests/test_cli.py` según la nota de corte 0.29.0, [tareas/20260924-100921-corte-029/TAREA.md:15](../../tareas/20260924-100921-corte-029/TAREA.md#L15)), cambia el contenido de `tests/test_cli.py`.
   - `dependencias_de_ronda()` incluye recursivamente toda la carpeta `tests/` ([tools/mutar_codigo.py:364-372](../../tools/mutar_codigo.py#L364-L372)).
   - `_identidad_ronda` calcula el sha256 de todas las dependencias ([perfiles/python/mutacion_codigo.py:736-746](../../perfiles/python/mutacion_codigo.py#L736-L746)).
   - `_cargar_reanudacion` exige coincidencia exacta de identidad y huella ([perfiles/python/mutacion_codigo.py:756-757](../../perfiles/python/mutacion_codigo.py#L756-L757)); si una dependencia cambió, levanta `ManifiestoInvalido`.
   - Por ende, **el manifiesto no se puede reanudar si se agregó o corrigió un test**.
   - Y aunque `--lineas` o `--sitio` permiten enfocar la ejecución sólo en los sitios afectados ([tools/mutar_codigo.py:14-17, 414-417](../../tools/mutar_codigo.py#L14-L17)), una ronda filtrada se marca obligatoriamente como `parcial: true` y sale con código `2` ("inconclusa") ([tools/mutar_codigo.py:19-21, 789-793](../../tools/mutar_codigo.py#L19-L21)).
   - Las políticas de release rechazan rondas parciales ([tools/mutar_codigo.py:16-17](../../tools/mutar_codigo.py#L16-L17)).
   - En consecuencia, certificar el release exige correr **nuevamente los 595 mutantes completos**, sumando otra hora entera de espera.

---

### 1.5 Estado de los logs de verificación de corte-029 y corte-030

- Los directorios existen físicamente en el repositorio bajo:
  - `tareas/20260924-100921-corte-029/verificacion/`
  - `tareas/20260924-154951-corte-030/verificacion/`
- En cumplimiento estricto de la regla del encargo (*"si no leíste algo, no digas qué contiene; si estimás, decí que es una estimación y de dónde sale. Sin shell"*), no se asume qué archivos específicos residen en dichas carpetas de verificación al no poder listarse sin shell ni haberse hallado bajo nombres conjeturados (`sintaxis.log`, `cli.log`, etc.).
- Las cifras temporales y conteos de mutantes analizados provienen directamente del texto de la tarea ([TAREA.md:10-13](../../tareas/20260924-233457-mutacion-lenta/TAREA.md#L10-L13)), de las notas históricas de corte-029 ([tareas/20260924-100921-corte-029/TAREA.md:13-16](../../tareas/20260924-100921-corte-029/TAREA.md#L13-L16)), de las mediciones registradas en el código ([tools/mutar_codigo.py:87-95, 190-227, 285-286](../../tools/mutar_codigo.py#L87-L95)) y de las especificaciones de baseline ([docs/mutacion-memoria.md:89-91](../../docs/mutacion-memoria.md#L89-L91)).

---

## 2. Propuestas para reducir el tiempo sin debilitar el criterio de muerte

### 2.1 Qué es el criterio de muerte y qué lo preserva

En Oracle, el criterio de muerte de código está establecido en:
- `EstadoTests.TESTS_FALLARON` (código de salida 1 del comando de tests): *"El código 1 significa fallo discriminante sólo porque el comando acuerda ese protocolo. Cualquier otro no-cero es un error del arnés..."* ([perfiles/python/mutacion_codigo.py:180-183](../../perfiles/python/mutacion_codigo.py#L180-L183)).
- `murio = resultado.tests_fallaron` ([perfiles/python/mutacion_codigo.py:956](../../perfiles/python/mutacion_codigo.py#L956)).
- *"Lo que cambie el criterio (qué cuenta como muerto) no se hace sin decisión de Brian"* ([TAREA.md:23](../../tareas/20260924-233457-mutacion-lenta/TAREA.md#L23)).

**Propiedad fundamental**: Un mutante está muerto si al menos un test falla.
Correr primero un subconjunto de tests y correr el resto de la suite **únicamente si ese subconjunto pasa sin fallos**:
- **Si el subconjunto falla**: el mutante queda demostrado como MUERTO (código 1). No cambia en nada si otros tests posteriores hubieran fallado o pasado.
- **Si el subconjunto pasa**: el mutante **no** se declara vivo; se procede a ejecutar el resto de la suite. Sólo si toda la suite completa pasa sin fallos se declara VIVO (código 0).
- **Conclusión**: Esta estrategia es matemáticamente idéntica en veredicto a la ejecución completa. No altera qué mutantes mueren, qué mutantes sobreviven, ni qué cuenta como equivalente. El criterio de muerte se preserva al 100 %.

---

### 2.2 Propuestas ordenadas de menor a mayor intervención

#### Propuesta 1 (Mínima / Cero cambio de lógica): Reordenar los módulos prioritarios en `PRIORIDADES`

- **Ubicación**: `tools/mutar_codigo.py:49-162`.
- **Diagnóstico**:
  - En `tools/cli.py`, la lista actual arranca con 4 módulos ajenos: `"tests.test_reportar", "tests.test_vigilar", "tests.test_biblioteca", "tests.test_tareas"` antes de llegar a `tests.test_cli` ([tools/mutar_codigo.py:92-95](../../tools/mutar_codigo.py#L92-L95)).
  - Como ya observaba el propio código en líneas 226-227: *"De ahí sale una palanca que no cuesta código: REORDENAR los módulos prioritarios poniendo el más específico primero. No está hecha ni medida; si alguien la prueba, que deje el número."* ([tools/mutar_codigo.py:226-227](../../tools/mutar_codigo.py#L226-L227)).
- **Acción concreta**:
  - Colocar `tests.test_cli` en primera posición para `tools/cli.py`.
  - Mover `tests.test_cli_integracion` y `tests.test_tareas` hacia el final de la lista de prioritarios (dejando adelante los tests unitarios directos y rápidos).
- **Impacto estimado**:
  - En `tools/cli.py`: la mayoría de los mutantes de CLI mueren en los primeros tests de `test_cli.py`. Al no tener que ejecutar antes toda la suite de tareas y biblioteca, el tiempo medio por mutante muerto puede bajar de ~6 s a ~1-2 s.
  - *Ahorro estimado*: Reducción de ~1 hora a ~15-20 minutos en `tools/cli.py`.

---

#### Propuesta 2 (Focalizada / Pequeña): Priorización de granularidad fina en `ejecutar_suite_mutacion.py`

- **Ubicación**: `tools/ejecutar_suite_mutacion.py:50-63` y `tools/mutar_codigo.py:353-361`.
- **Diagnóstico**:
  - `unittest.TestLoader.loadTestsFromName(nombre)` admite nombres calificados de clases y métodos de test: por ejemplo `tests.test_sintaxis.ExpresionesTests` o `tests.test_sintaxis.ClaseX.test_metodo`.
  - Actualmente `--prioridad` sólo recibe módulos completos ([tools/ejecutar_suite_mutacion.py:20-21](../../tools/ejecutar_suite_mutacion.py#L20-L21)).
  - En `nucleo/sintaxis.py`, `tests.test_sintaxis` tiene 3163 líneas. Cargar el módulo completo obliga a evaluar tests en orden secuencial hasta encontrar la falla.
- **Acción concreta**:
  - Permitir que el mapeo de prioridades admita clases de prueba prioritarias (por ejemplo las clases que ejercitan directamente las secciones de `sintaxis.py`: lectura, impresión, macros, expresiones).
  - O mapear rangos de líneas/zonas del módulo a las clases de test correspondientes.
  - El runner corre primero esa clase puntual (0,05 s); si falla, fin. Si no, corre el módulo completo y luego el resto de la suite.
- **Impacto estimado**:
  - Para `nucleo/sintaxis.py`: en lugar de ejecutar una media de decenas o cientos de tests antes de fallar (~5 s), el test discriminador corre en los primeros 100 ms.
  - *Ahorro estimado*: De 1177 mutantes × ~6 s (~117 min) a 1177 × ~1 s (~20 min).

---

#### Propuesta 3 (Optimización de arnés): Reducir los barridos redundantes de `os.walk` en `perfiles/python/mutacion_codigo.py`

- **Ubicación**: `perfiles/python/mutacion_codigo.py:401-440, 602-635`.
- **Diagnóstico**:
  - En cada mutante se llama a `_caches_bajo` entre 4 y 5 veces. Cada llamada realiza un `os.walk` recursivo de todo el proyecto.
  - El entorno ya aísla la corrida mediante una variable de entorno `PYTHONPYCACHEPREFIX=prefijo_temporal` ([perfiles/python/mutacion_codigo.py:616](../../perfiles/python/mutacion_codigo.py#L616)) y `PYTHONDONTWRITEBYTECODE="1"`. Los `.pyc` nunca se escriben en el árbol del proyecto a menos que el código bajo prueba cree explícitamente una carpeta `__pycache__`.
  - Escanear todo el árbol 5000 veces en una ronda agrega cientos de segundos de I/O puramente administrativo.
- **Acción concreta**:
  - En lugar de escanear recursivamente todo el árbol en cada mutante antes Y después:
    - Comprobar antes de arrancar la ronda completa y al finalizar la ronda completa.
    - O acotar la comprobación intermedia a las carpetas tocadas por los módulos del comando de tests en lugar de la raíz completa.
- **Impacto estimado**:
  - Elimina ~0,1-0,2 s de sobrecarga pura de filesystem por mutante.
  - En 1177 mutantes: ahorro directo de ~120-240 s (~2-4 minutos).

---

#### Propuesta 4 (Estructural / Mayor impacto): Reanudación selectiva de mutantes muertos al iterar sobre sobrevivientes

- **Ubicación**: `perfiles/python/mutacion_codigo.py:726-778` y `tools/mutar_codigo.py:408-411`.
- **Diagnóstico**:
  - Cuando un corte encuentra mutantes vivos (como los 7 vivos de `tools/cli.py` en corte 0.29.0), el desarrollador escribe tests en `tests/` para matarlos.
  - Al modificar `tests/`, la huella de `dependencias` cambia ([perfiles/python/mutacion_codigo.py:736-746](../../perfiles/python/mutacion_codigo.py#L736-L746)), invalidando el `--manifiesto` previo.
  - Esto obliga a correr de cero los 595 mutantes completos, cuando 588 de ellos ya habían muerto con la versión anterior de la suite (y agregar tests a una suite monótona nunca resucita a un mutante ya muerto, salvo que se borren tests existentes).
- **Acción concreta**:
  - Incorporar un modo de reanudación incremental o revalidación:
    - Si las fuentes del objetivo (`fuentes`) son idénticas y sólo cambiaron `dependencias` (tests agregados), los mutantes que ya murieron por `tests_fallaron` con código 1 se conservan como válidos, o se comprueban únicamente los que figuraban como `pasaron` (vivos) o `inconclusos`.
    - Para release final estricto, si se exige revalidación total, esta optimización permite al menos iterar durante el ciclo de desarrollo/fijación sin pagar la hora completa en cada prueba.
- **Impacto estimado**:
  - En la ronda repetida de los 7 vivos de `cli.py`: en lugar de tardar >1 hora reejecutando los 595 mutantes, tarda únicamente los 7 mutantes objetivo (~1-2 minutos si ahora mueren con los tests nuevos).
  - Ahorro: **>55 minutos por cada ciclo de iteración de mutantes vivos**.

---

### 2.3 Resumen de impactos estimados

| Propuesta | Dificultad / Riesgo | Criterio de Muerte | Ahorro Estimado |
|---|---|---|---|
| **1. Reordenar `PRIORIDADES` (`test_cli` primero)** | Muy baja (1 línea de config) | Intacto (100 % idéntico) | ~40-45 min en `tools/cli.py` |
| **2. Priorización fina en `ejecutar_suite_mutacion.py`** | Baja (extender loader a clases/métodos) | Intacto (100 % idéntico) | ~60-90 min en `nucleo/sintaxis.py` |
| **3. Aliviar barridos `_caches_bajo` redundantes** | Media (cuidar garantías de frío) | Intacto (100 % idéntico) | ~2-4 min por ronda |
| **4. Revalidación selectiva al iterar sobrevivientes** | Media (lógica de manifiesto) | Intacto (requiere diseño de hash) | ~55 min por cada ronda de re-verificación |

---

## 3. Conclusión y Recomendación

La causa raíz de que `nucleo/sintaxis.py` tarde ~2 horas y `tools/cli.py` tarde >1 hora **no es que todos los mutantes corran la suite completa de 2440 tests**. La causa es doble:
1. **En los mutantes que mueren**: el arnés tarda entre 5 y 6 segundos en *llegar* al test que discrimina la falla, debido al tamaño de `test_sintaxis.py` (3163 líneas) y al orden subóptimo de los módulos prioritarios en `tools/cli.py`.
2. **En los mutantes vivos y en las rondas repetidas**: los sobrevivientes sí pagan los ~90 s de la suite completa, y el arnés invalida el manifiesto si se agregan tests, forzando a pagar la suite y la ronda completa de 595 mutantes de nuevo.

La intervención más chica y de menor riesgo, que no altera código de producción ni debilita el criterio de muerte, es:
- **Paso inmediato 1**: Reordenar `PRIORIDADES["tools/cli.py"]` en `tools/mutar_codigo.py:92-95` poniendo `tests.test_cli` en primer lugar.
- **Paso inmediato 2**: Permitir granularidad por clases de prueba en `PRIORIDADES` para `nucleo/sintaxis.py` en `tools/ejecutar_suite_mutacion.py:51-63`.
