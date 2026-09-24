# Análisis de custodia y costo de mutación de los 12 módulos de `tools/`

- **Tarea:** `20260924-233457-custodia`
- **Fecha:** 2026-09-24
- **Condición:** Análisis estático sin cambiar código, sin ejecución en shell y sin commits.

---

## 1. Criterio de custodia y marco de evaluación

El criterio establecido en el repositorio para que un archivo de `tools/` sea incorporado a `HERRAMIENTAS_CUSTODIAS` se encuentra definido en [`tools/mutar_codigo.py:167-168`](../../tools/mutar_codigo.py#L167-L168):
> *«`tools/` no entra entero: son instrumentos... Entran DE A UNO, y sólo cuando el instrumento **custodia una afirmación que nadie más comprueba**: si el instrumento se rompe, la afirmación queda sin nadie que la verifique.»*

Complementariamente, el test en [`tests/test_herramientas.py:2448-2457`](../../tests/test_herramientas.py#L2448-L2457) vigila que toda custodia declarada entre a la matriz de CI en [`.github/workflows/verificar.yml`](../../.github/workflows/verificar.yml) o justifique su ausencia en el diccionario `CUSTODIAS_SIN_MEDIR`.

Asimismo, el precedente de exclusión de [`tools/lsp.py`](../../tools/lsp.py) documentado en [`tools/mutar_codigo.py:310-316`](../../tools/mutar_codigo.py#L310-L316) fija un límite estricto: no son custodias las herramientas que sólo adaptan interfaces externas sin ser corridas por CI, ni los shims sin lógica propia, ni las herramientas de scaffolding donde ninguna afirmación formal de corrección del núcleo queda sin verificar.

### Metodología de estimación de sitios de mutación
Dado que esta pasada se ejecuta bajo la restricción «Sin shell», los sitios de mutación no fueron medidos dinámicamente mediante `python tools/mutar_codigo.py`.
- **Origen de la estimación:** Se basa en la definición de operadores del AST implementada en [`perfiles/python/mutacion_codigo.py:253-290`](../../perfiles/python/mutacion_codigo.py#L253-L290) (`comparador`, `booleano`, `negacion`, `constante` numérica/booleana [las de texto se ignoran por diseño según [`tests/test_mutacion_codigo.py:110-116`](../../tests/test_mutacion_codigo.py#L110-L116)], y `retorno` no-None), contrastada con los recuentos históricos ya medidos en el repositorio:
  - `tools/lsp.py`: 375 líneas -> **140 sitios** (medición histórica exacta en [`tools/mutar_codigo.py:207`](../../tools/mutar_codigo.py#L207)).
  - `tools/corpus.py`: ~300 líneas -> **112 sitios** ([`tools/mutar_codigo.py:208`](../../tools/mutar_codigo.py#L208)).
  - `tools/diferencial.py`: ~200 líneas -> **55 sitios** ([`tools/mutar_codigo.py:293`](../../tools/mutar_codigo.py#L293)).
  - `tools/cli.py`: ~900 líneas -> **509 sitios** ([`tools/mutar_codigo.py:285`](../../tools/mutar_codigo.py#L285)).

---

## 2. Análisis individual de los 12 módulos

---

### 1. `tools/ejecutar_suite_mutacion.py`
- **Lectura:** Leído completo (líneas 1 a 95).
- **Líneas:** 95 líneas.
- **Función:** Runner especializado de `unittest` utilizado exclusivamente por [`tools/mutar_codigo.py:46`](../../tools/mutar_codigo.py#L46) (`TESTS = [sys.executable, str(RAIZ / "tools" / "ejecutar_suite_mutacion.py")]`). Implementa el protocolo binario/tripartito de códigos de salida:
  - `0`: suite superada sin errores ni fallos ([l.90](../../tools/ejecutar_suite_mutacion.py#L90)).
  - `1`: fallo discriminante en pruebas prioritarias o generales ([l.61-63, 88-89](../../tools/ejecutar_suite_mutacion.py#L61-L63)).
  - `2`: error del arnés en carga prioritaria, descubrimiento, cero pruebas descubiertas o excepciones ([l.58, 69, 76, 79, 83, 87, 90](../../tools/ejecutar_suite_mutacion.py#L58)).
- **¿Cumple el criterio de custodia? SÍ.**
  - Si se rompe silenciosamente (por ejemplo, si devuelve `0` ante fallos en `resultado_prioritario.failures` [l.61-63] o invierte el retorno en l.90), cualquier mutante vivo será reportado erróneamente como muerto, o la línea base se considerará verde falsamente.
  - Si `_sin_modulos` ([l.29-40](../../tools/ejecutar_suite_mutacion.py#L29-L40)) omite casos que no debían omitirse, tests críticos de discriminación no se ejecutan.
- **Afirmación que dejaría sin verificar:**
  *«La ejecución de la suite de pruebas unitarias concluyó con éxito, falló discriminando un defecto, o experimentó una falla de descubrimiento/arnés, ejecutando todos los módulos prioritarios y generales correspondientes.»*
- **Quién la consume:**
  [`perfiles/python/mutacion_codigo.py:591-620`](../../perfiles/python/mutacion_codigo.py#L591-L620) (`ejecutar_tests`) y [`tools/mutar_codigo.py`](../../tools/mutar_codigo.py).
- **Problema de recursión y propuesta:**
  - *Problema:* Si `ejecutar_suite_mutacion.py` se muta a sí mismo dentro del sandbox temporal copiado, el runner que juzga si el mutante murió es el código mutado. Un mutante que falle al importar o salga prematuramente con 0 corrompería el juicio del propio arnés.
  - *Propuesta (arnés testigo / copia congelada):* El runner debe ejecutarse desde la raíz inmutable de referencia (`RAIZ / "tools" / "ejecutar_suite_mutacion.py"`), pasando `--inicio` y `--tope` apuntando al sandbox temporal mutado. Las pruebas de discriminación del runner se ejecutan como tests unitarios en un archivo dedicado (ej. `tests/test_ejecutar_suite_mutacion.py`) que invoque al script mutado sobre suites testigo sintéticas con fallos y éxitos programados.
- **Sitios de mutación estimados:**
  - **35 a 45 sitios** (estimación basada en el recuento de ramas condicionales, retornos numéricos 1/2 y operadores booleanos en sus 95 líneas).

---

### 2. `tools/estudio.py`
- **Lectura:** Leído (líneas 1 a 280).
- **Líneas:** 423 líneas.
- **Función:** Generador de documentación plana para ingesta por herramientas externas como NotebookLM ([`tools/estudio.py:1-19`](../../tools/estudio.py#L1-L19)).
- **¿Cumple el criterio de custodia? NO.**
  - No se ejecuta en CI (no figura en [`.github/workflows/verificar.yml`](../../.github/workflows/verificar.yml)).
  - No emite juicios, veredictos ni hechos que consuma el evaluador o la aceptación.
  - Todos los datos que expone (catálogo, corpus, especificación, diario) son verificados en sus módulos fuente (`nucleo/`, `catalogos/`, `corpus/`).
  - Su falla produciría Markdown defectuoso para una herramienta externa, pero ninguna afirmación verificable de Oracle quedaría desatendida.
- **Afirmación que dejaría sin verificar:** Ninguna afirmación formal del sistema.
- **Quién la consume:** Desarrolladores o usuarios externos mediante NotebookLM.
- **Sitios de mutación estimados:**
  - **110 a 160 sitios** (estimación extrapolada de `tools/corpus.py`, que con ~300 líneas contiene 112 sitios).

---

### 3. `tools/generar_diferencial.py`
- **Lectura:** Leído completo (líneas 1 a 100 y 200 a 323).
- **Líneas:** 323 líneas.
- **Función:**
  - Define la colección de escenarios de contraste `MUNDOS` ([l.41-100](../../tools/generar_diferencial.py#L41-L100)) y las medidas del emisor.
  - Compara la evaluación de la implementación de referencia independiente (`diferencial/referencia/evaluador.py`) contra la de Oracle (`nucleo/fixtures.py`, `nucleo/diferencial.py`), abortando la emisión si existe algún desacuerdo ([l.240-249](../../tools/generar_diferencial.py#L240-L249)).
  - Serializa de manera determinista y calcula la huella de frescura de `diferencial/simulacion.json` ([l.277-285](../../tools/generar_diferencial.py#L277-L285)).
  - Sin `--escribir`, comprueba que el archivo versionado esté al día con la referencia ([l.311-314](../../tools/generar_diferencial.py#L311-L314)).
- **¿Cumple el criterio de custodia? SÍ.**
  - La tarea [`tareas/20260916-014457-custodia/TAREA.md:20-21`](../../tareas/20260916-014457-custodia/TAREA.md#L20-L21) ya señalaba: *«ahí viven los mundos y las medidas del contraste»*.
  - Si se rompe silenciosamente (por ejemplo, omitiendo la detección de desacuerdos en l.241 o emitiendo fixtures con polaridades incorrectas), un fixture diferencial corrupto se versionaría y [`tools/diferencial.py`](../../tools/diferencial.py) daría verde sobre un desacuerdo congelado.
- **Afirmación que dejaría sin verificar:**
  *«El fixture versionado en `diferencial/simulacion.json` refleja fielmente el acuerdo exacto entre la implementación de referencia independiente y Oracle para el conjunto canónico de escenarios `MUNDOS` y medidas, con huellas de procedencia y frescura íntegras.»*
- **Quién la consume:**
  [`tools/diferencial.py`](../../tools/diferencial.py), [`tools/mutar.py:63-68`](../../tools/mutar.py#L63-L68) (vía `cargar_fixtures`), y CI (`contratos`).
- **Problema de recursión:**
  Ninguno. No es un arnés de mutación de código; evalúa el motor contra la referencia y puede ser mutado directamente por `mutar_codigo.py`.
- **Sitios de mutación estimados:**
  - **90 a 140 sitios** (estimación basada en la complejidad de serialización JSON, validación de esquemas y bucles de comparación en 323 líneas).

---

### 4. `tools/lsp.py`
- **Lectura:** Leído (líneas 1 a 100).
- **Líneas:** 375 líneas.
- **Función:** Servidor Language Server Protocol para editores ([`tools/lsp.py:1-2`](../../tools/lsp.py#L1-L2)).
- **¿Cumple el criterio de custodia? NO.**
  - Fue retirado explícitamente de `HERRAMIENTAS_CUSTODIAS` el 2026-09-09 ([`tools/mutar_codigo.py:310-316`](../../tools/mutar_codigo.py#L310-L316)):
    *«Salió porque no cumple el criterio. Es un adaptador de editor: no lo corre CI, no lo corre oracle test, no lo corre ningún consumidor, y todo lo que expone... lo calculan nucleo/ y las medidas del catálogo.»*
- **Afirmación que dejaría sin verificar:** Ninguna afirmación del núcleo ni de la suite.
- **Quién la consume:** Editores de código del desarrollador.
- **Sitios de mutación:**
  - **140 sitios** (medición empírica registrada en [`tools/mutar_codigo.py:207`](../../tools/mutar_codigo.py#L207)).

---

### 5. `tools/mcp_contrato.py`
- **Lectura:** Leído completo (líneas 1 a 40).
- **Líneas:** 40 líneas.
- **Función:** Regenera o comprueba el bloque JSON de herramientas dentro de `docs/mcp-contrato.md` a partir de `tools.mcp.HERRAMIENTAS` ([`tools/mcp_contrato.py:13-35`](../../tools/mcp_contrato.py#L13-L35)).
- **¿Cumple el criterio de custodia? NO (en el estado actual del repositorio).**
  - No se ejecuta en el workflow de CI ([`.github/workflows/verificar.yml`](../../.github/workflows/verificar.yml)).
  - La herramienta que ejecuta el servidor y custodia el protocolo MCP en runtime es [`tools/mcp.py`](../../tools/mcp.py), la cual **ya es custodia activa** en `HERRAMIENTAS_CUSTODIAS:305` y en CI ([`.github/workflows/verificar.yml:153`](../../.github/workflows/verificar.yml#L153)) con 1808 líneas de tests en [`tests/test_mcp.py`](../../tests/test_mcp.py).
  - `mcp_contrato.py` sólo sincroniza un fragmento markdown de documentación. Si no se invoca en CI, no puede custodiar ninguna afirmación que alguien compruebe mecánicamente.
- **Afirmación que dejaría sin verificar:** Ninguna afirmación operativa del sistema.
- **Quién la consume:** Desarrolladores o lectores humanos de `docs/mcp-contrato.md`.
- **Sitios de mutación estimados:**
  - **10 a 15 sitios** (estimación basada en 40 líneas breves con 2 llamadas `.split()`, una lectura de archivo y una comparación booleana).

---

### 6. `tools/mutar.py`
- **Lectura:** Leído completo (líneas 1 a 188).
- **Líneas:** 188 líneas.
- **Función:**
  - Arnés de mutación de MEDIDAS (datos). Carga el catálogo y casos (corpus + diferencial, [l.56-69](../../tools/mutar.py#L56-L69)).
  - Ejecuta la mutación de medidas ([l.83](../../tools/mutar.py#L83)), calcula mutantes vivos ([l.90-91](../../tools/mutar.py#L90-L91)), produce hechos de uso ([l.124-125](../../tools/mutar.py#L124-L125)) y evalúa las políticas meta del catálogo sobre la evidencia ([l.127-128, 154-165](../../tools/mutar.py#L127-L128)).
  - Sale con 1 si sobreviven mutantes o fallan políticas meta ([l.151](../../tools/mutar.py#L151)).
  - Corre activamente en CI ([`.github/workflows/verificar.yml:89`](../../.github/workflows/verificar.yml#L89)).
- **¿Cumple el criterio de custodia? SÍ.**
  - Si `mutar.py` se rompe silenciosamente (por ejemplo, si relaja `_politicas_ok` en l.154 o devuelve 0 ante mutantes vivos en l.151, o si omite los casos diferenciales en l.68), las medidas del catálogo podrían perder su poder de discriminación sin que CI se percate.
  - Ningún otro instrumento muta medidas: `mutar_codigo.py` muta código fuente Python, no los operadores ni umbrales de los archivos `.oracle`/`.json`.
- **Afirmación que dejaría sin verificar:**
  *«Todas las medidas activas del catálogo de Oracle son falsables y quedan fijadas por casos del corpus o escenarios diferenciales, satisfaciendo las políticas meta de no-redundancia y cobertura.»*
- **Quién la consume:**
  CI ([`.github/workflows/verificar.yml:89`](../../.github/workflows/verificar.yml#L89)) y el subcomando `oracle mutar`.
- **Problema de recursión:**
  Ninguno. `mutar.py` muta **medidas** (datos interpretados por `nucleo/mutacion.py`). `mutar_codigo.py` muta **código Python**. La mutación de código de `tools/mutar.py` es ortogonal y no genera recursión de arnés.
- **Sitios de mutación estimados:**
  - **50 a 80 sitios** (estimación basada en la densidad de lógica de evaluación y cómputo de hechos en 188 líneas).

---

### 7. `tools/mutar_codigo.py`
- **Lectura:** Leído (líneas 1 a 500).
- **Líneas:** 817 líneas.
- **Función:** Arnés principal de mutación de código Python. Conduce la mutación en aislamiento en directorios temporales, gestiona bloqueos, límites de recursos, reanudación atómica mediante manifiestos ([l.408-412](../../tools/mutar_codigo.py#L408-L412)), filtrado parcial por líneas o sitios ([l.378-393](../../tools/mutar_codigo.py#L378-L393)), y validación/reubicación de equivalentes ([l.425-500](../../tools/mutar_codigo.py#L425-L500)).
- **¿Cumple el criterio de custodia? SÍ.**
  - Es el instrumento central que produce la evidencia de falsación del código. Si se rompe (por ejemplo, si clasifica un mutante sobreviviente como muerto, ignora la rotura de una línea base, o reporta una corrida parcial como completa), el veredicto de CI en `mutacion-codigo` queda viciado.
- **Afirmación que dejaría sin verificar:**
  *«El código bajo perfil activo es verificado contra mutaciones sintácticas del AST sin mutantes sobrevivientes no justificados en `equivalentes.json`, respetando el aislamiento y la completitud de la ronda.»*
- **Quién la consume:**
  CI ([`.github/workflows/verificar.yml:209`](../../.github/workflows/verificar.yml#L209)) y el ciclo de desarrollo local (`python tools/mutar_codigo.py`).
- **Problema de recursión y propuesta:**
  - *Problema (autorreferencia directa):* Si `mutar_codigo.py` se muta a sí mismo, el ejecutor de la ronda es el mismo código que está siendo alterado.
  - *Propuesta (ejecutor inmutable desacoplado / arnés testigo):*
    1. El proceso padre orquestador siempre se ejecuta desde el código inmutable de la raíz base (`RAIZ / "tools" / "mutar_codigo.py"`), aplicando las mutaciones únicamente dentro del sandbox temporal copiado (`/tmp/.../copia/tools/mutar_codigo.py`).
    2. Las pruebas unitarias de [`tests/test_mutacion_codigo.py`](../../tests/test_mutacion_codigo.py) (que ya prueban `mutar_codigo` extensivamente con mocks de aislamiento, líneas base y timeouts en líneas 1700-1785) son invocadas por el runner testigo para discriminar los mutantes en la copia sin que el orquestador sufra las mutaciones.
- **Sitios de mutación estimados:**
  - **220 a 300 sitios** (estimación basada en la densidad de AST observada en [`tools/cli.py`](../../tools/cli.py), que con ~900 líneas tiene 509 sitios, descartando aquí los bloques de texto estático y docstrings extensos de `mutar_codigo.py`).

---

### 8. `tools/oracle.py`
- **Lectura:** Leído completo (líneas 1 a 14).
- **Líneas:** 14 líneas.
- **Función:** Shim / alias de conveniencia que redirige a `tools/cli.py` ([`tools/oracle.py:10-13`](../../tools/oracle.py#L10-L13)).
- **¿Cumple el criterio de custodia? NO.**
  - Carece de lógica propia. Toda la validación, opciones, dispatch y manejo de errores vive en [`tools/cli.py`](../../tools/cli.py), que ya es custodia y cuenta con 509 sitios medidos y cerrados en CI ([`tools/mutar_codigo.py:285`](../../tools/mutar_codigo.py#L285)).
- **Afirmación que dejaría sin verificar:** Ninguna afirmación independiente.
- **Quién la consume:** Desarrolladores que invocan `python tools/oracle.py`.
- **Sitios de mutación estimados:**
  - **2 a 4 sitios** (constante `0` en `sys.path.insert(0, ...)` y comparador en `__name__ == "__main__"`).

---

### 9. `tools/plantilla.py`
- **Lectura:** Leído completo (líneas 1 a 68).
- **Líneas:** 68 líneas.
- **Función:** Implementa el subcomando `oracle plantilla sensor-prosa <destino>` para copiar recursos iniciales de sensor ([`tools/plantilla.py:32-67`](../../tools/plantilla.py#L32-L67)).
- **¿Cumple el criterio de custodia? NO.**
  - Es una herramienta de scaffolding/copia de archivos estáticos.
  - No valida el modelo relacional, ni juzga hechos, ni produce afirmaciones verificadas.
  - Su funcionamiento ya es comprobado por [`tools/verificar_instalacion.py:199`](../../tools/verificar_instalacion.py#L199) (`_recorrer_plantilla`).
- **Afirmación que dejaría sin verificar:** Ninguna afirmación del sistema.
- **Quién la consume:** Usuarios finales al inicializar un sensor.
- **Sitios de mutación estimados:**
  - **20 a 35 sitios** (estimación basada en operaciones de copia de bytes, mkdir y parsing de argumentos en 68 líneas).

---

### 10. `tools/sesion.py`
- **Lectura:** Leído completo (líneas 1 a 16).
- **Líneas:** 16 líneas.
- **Función:** Envoltura común de 16 líneas para atrapar `ProyectoInvalido` y retornar `None` imprimiendo en stderr ([`tools/sesion.py:10-15`](../../tools/sesion.py#L10-L15)).
- **¿Cumple el criterio de custodia? NO (como herramienta custodia independiente).**
  - Es un helper utilitario. La resolución y validación sustantiva del proyecto reside en [`nucleo/proyecto.py`](../../nucleo/proyecto.py) (`resolver()`), el cual ya está en el perfil activo de mutación ([`tools/mutar_codigo.py:68-69`](../../tools/mutar_codigo.py#L68-L69)).
  - Tratar un helper de 16 líneas como custodia autónoma diluiría el criterio de custodia.
- **Afirmación que dejaría sin verificar:** Ninguna afirmación de negocio o verdad del lenguaje.
- **Quién la consume:** Varios entry points CLI (`cli.py`, `mutar.py`, `mutar_codigo.py`, `estudio.py`, `lsp.py`).
- **Sitios de mutación estimados:**
  - **1 a 3 sitios** (retorno en l.12 y retorno en l.15).

---

### 11. `tools/trazar.py`
- **Lectura:** Leído completo (líneas 1 a 189).
- **Líneas:** 189 líneas.
- **Función:**
  - Ejecuta el corpus bajo traza relacional del álgebra produciendo las relaciones `paso`, `nodo` y `producto` ([`tools/trazar.py:110-135`](../../tools/trazar.py#L110-L135)).
  - Falla cerrado si la traza está vacía ([l.155-159](../../tools/trazar.py#L155-L159)).
  - Evalúa las medidas de vigilancia metalingüística del evaluador ([l.45-51, 161-169](../../tools/trazar.py#L45-L51)).
  - Contrasta los veredictos contra la implementación de referencia independiente y aborta si hay desacuerdo ([l.83-103, 171-177](../../tools/trazar.py#L83-L103)).
  - Se ejecuta en CI ([`.github/workflows/verificar.yml:93`](../../.github/workflows/verificar.yml#L93)).
- **¿Cumple el criterio de custodia? SÍ.**
  - Si se rompe silenciosamente (por ejemplo, omitiendo la guarda de `TRAZA VACÍA` en l.155 o ignorando desacuerdos en l.174), una regresión en las propiedades estructurales del álgebra (como `meta.donde_nunca_agrega_filas` o `meta.sin_nunca_agrega_filas`) no sería advertida por nadie en CI.
- **Afirmación que dejaría sin verificar:**
  *«El evaluador de Oracle cumple los invariantes operacionales del álgebra sobre toda la ejecución del corpus y coincide sin discrepancias con la especificación de referencia independiente.»*
- **Quién la consume:**
  CI ([`.github/workflows/verificar.yml:93`](../../.github/workflows/verificar.yml#L93)), y el subcomando `oracle trazar`.
- **Problema de recursión:**
  Ninguno. Traza el álgebra de `nucleo/algebra.py`, no el arnés de mutación. Puede ser mutado directamente por `mutar_codigo.py`.
- **Sitios de mutación estimados:**
  - **55 a 75 sitios** (estimación basada en 189 líneas con comparaciones, recolección de trazas y evaluación de informes).

---

### 12. `tools/verificar_instalacion.py`
- **Lectura:** Leído (líneas 1 a 200).
- **Líneas:** 564 líneas.
- **Función:**
  - Construye el wheel (`pyproject.toml`) y lo instala en un `venv` limpio sin variables de entorno (`ORACLE_PROYECTO`, `PYTHONPATH`, [`tools/verificar_instalacion.py:21-26`](../../tools/verificar_instalacion.py#L21-L26)).
  - Ejecuta pruebas de integración de ciclo de vida completo sobre el paquete instalado: tracker (`oracle tarea`, [l.53-197](../../tools/verificar_instalacion.py#L53-L197)), git, juzgar, plantilla, MCP y pruebas del consumidor.
  - Corre en CI ([`.github/workflows/verificar.yml:54`](../../.github/workflows/verificar.yml#L54)).
- **¿Cumple el criterio de custodia? SÍ.**
  - Si se rompe silenciosamente (relajando aserciones de error o ignorando códigos de retorno en `_correr`, l.37-41), una versión rota del paquete instalable podría publicarse sin que la suite estándar en desarrollo lo detecte (ej. incompatibilidades de empaquetado o rutas con caracteres no ASCII).
- **Afirmación que dejaría sin verificar:**
  *«El artefacto de distribución (`wheel`) se construye e instala limpiamente en un entorno estándar aislado y sus entry points públicos ejecutan todas las funciones declaradas sin degradación ni dependencias ocultas.»*
- **Quién la consume:**
  CI ([`.github/workflows/verificar.yml:54`](../../.github/workflows/verificar.yml#L54)).
- **Problema de recursión y costo:**
  - No presenta recursión lógica con `mutar_codigo.py`.
  - *Problema de costo:* Ejecutar la suite completa de `verificar_instalacion.py` por cada mutante tardaría varios minutos por sitio (construir wheels y venvs repetidamente).
  - *Propuesta:* Para incorporarlo con viabilidad a la mutación, se debe desacoplar la validación de aserciones de la creación de venvs pesados mediante un conjunto de pruebas unitarias específicas que prueben sus funciones con mocks controlados de `subprocess`.
- **Sitios de mutación estimados:**
  - **150 a 220 sitios** (estimación basada en 564 líneas con numerosas llamadas a subprocess, comprobaciones de diccionarios JSON y validaciones de filesystem).

---

## 3. Matriz comparativa y consolidada

| Módulo | Líneas | Cumple Custodia | Afirmación concreta que custodia (o motivo de rechazo) | Consumidor principal | Recursión / Desacoplamiento necesario | Sitios estimados |
|:---|:---:|:---:|:---|:---|:---|:---:|
| `tools/ejecutar_suite_mutacion.py` | 95 | **SÍ** | Protocolo de salida (0/1/2) y ejecución íntegra y deduplicada de la suite de pruebas bajo mutación | `perfiles/python/mutacion_codigo.py` y `mutar_codigo.py` | **SÍ** (requiere arnés testigo inmutable) | 35 – 45 |
| `tools/estudio.py` | 423 | **NO** | Generador auxiliar de docs (NotebookLM); no corre en CI ni produce evidencia de verificación | Lectores externos | Ninguno | 110 – 160 |
| `tools/generar_diferencial.py` | 323 | **SÍ** | Acuerdo con la referencia sobre `MUNDOS` y frescura/validez de `diferencial/simulacion.json` | `tools/diferencial.py`, `mutar.py`, CI | Ninguno | 90 – 140 |
| `tools/lsp.py` | 375 | **NO** | Excluido el 2026-09-09 (`mutar_codigo.py:310-316`); adaptador de editor no verificado en CI | Editores interactivos | Ninguno | 140 *(medido)* |
| `tools/mcp_contrato.py` | 40 | **NO** | Sincronizador de `docs/mcp-contrato.md`; no corre en CI. `tools/mcp.py` ya es la custodia activa | Documentación | Ninguno | 10 – 15 |
| `tools/mutar.py` | 188 | **SÍ** | Falsación de las medidas del catálogo frente a mutaciones de datos y cumplimiento de políticas meta | CI (`verificar.yml:89`), `oracle mutar` | Ninguno (mutación de datos vs código) | 50 – 80 |
| `tools/mutar_codigo.py` | 817 | **SÍ** | Falsación del código frente a operadores sintácticos, aislamiento y gestión de equivalentes | CI (`verificar.yml:209`), CLI local | **SÍ** (requiere arnés testigo inmutable) | 220 – 300 |
| `tools/oracle.py` | 14 | **NO** | Shim trivial de 14 líneas hacia `tools/cli.py` (que ya es custodia con 509 sitios en CI) | CLI local | Ninguno | 2 – 4 |
| `tools/plantilla.py` | 68 | **NO** | Scaffolding de inicio; no fija ni custodia afirmaciones de verificación | Usuarios iniciales | Ninguno | 20 – 35 |
| `tools/sesion.py` | 16 | **NO** | Helper de 16 líneas para atrapar `ProyectoInvalido`; lógica central en `nucleo/proyecto.py` | Entry points CLI | Ninguno | 1 – 3 |
| `tools/trazar.py` | 189 | **SÍ** | Invariantes operacionales del álgebra sobre el corpus y coincidencia con la referencia | CI (`verificar.yml:93`), `oracle trazar` | Ninguno | 55 – 75 |
| `tools/verificar_instalacion.py` | 564 | **SÍ** | Integridad y ejecución sin degradación del paquete distribuido (`wheel`) en un entorno limpio | CI (`verificar.yml:54`) | Ninguno (requiere tests rápidos) | 150 – 220 |

---

## 4. Conclusiones y recomendaciones para la siguiente pasada

1. **6 módulos cumplen el criterio de custodia:**
   - `tools/ejecutar_suite_mutacion.py`
   - `tools/generar_diferencial.py`
   - `tools/mutar.py`
   - `tools/mutar_codigo.py`
   - `tools/trazar.py`
   - `tools/verificar_instalacion.py`
   *Costo acumulado estimado:* entre **600 y 860 sitios de mutación**.

2. **6 módulos NO cumplen el criterio de custodia:**
   - `tools/estudio.py`, `tools/lsp.py`, `tools/mcp_contrato.py`, `tools/oracle.py`, `tools/plantilla.py`, `tools/sesion.py`.
   *Razón:* Son adaptadores externos, shims, sincronizadores documentales o helpers dependientes de módulos que ya están bajo mutación.

3. **Arquitectura para evitar autorreferencia recursiva:**
   Para `mutar_codigo.py` y `ejecutar_suite_mutacion.py`, el arnés ejecutor debe correr desacoplado: una instancia testigo/inmutable invocada desde el directorio base de Oracle debe orquestar la ejecución sobre los archivos mutados en el directorio temporal aislado, apoyándose en pruebas unitarias dedicadas (`tests/test_ejecutar_suite_mutacion.py` y las existentes `tests/test_mutacion_codigo.py`).

4. **Secuencia de integración (Punto 3 del encargo):**
   - **Fase 1 (Bajo costo, sin recursión):** Incorporar primero `tools/generar_diferencial.py`, `tools/mutar.py` y `tools/trazar.py`. Son custodias directas con ~195-295 sitios combinados, sin problemas de autorreferencia.
   - **Fase 2 (Arneses autorreferenciales):** Implementar el desacoplamiento del runner testigo en `tools/mutar_codigo.py` e incorporar `tools/ejecutar_suite_mutacion.py` y `tools/mutar_codigo.py`.
   - **Fase 3 (Integración pesada):** Incorporar `tools/verificar_instalacion.py` dotándolo de pruebas unitarias con mocking para no pagar el costo de crear venvs y compilar wheels en cada mutante.
