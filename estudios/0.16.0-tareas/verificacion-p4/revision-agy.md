# Informe de revisión de solo lectura — Hito P4 (`PLAN-0.16.0-TAREAS.md`)

Este informe presenta los resultados de la revisión estática y de solo lectura sobre la documentación de usuario y los módulos de implementación del subsistema de tareas. No se ejecutaron comandos de shell, ni tests, ni subagentes, ni se realizaron escrituras en el árbol de trabajo.

---

## 1. Alcance revisado

- **Documentación y tutoriales**:
  - [`docs/12-tareas.md`](file:///home/workstation/Dev/oracle/docs/12-tareas.md): tutorial del ciclo completo (P1 + P2 + P3), tabla de subcomandos, anatomía de `TAREA.md`, especificación de hechos relacionales y códigos de salida.
  - [`ejemplo/seguimiento-tareas/README.md`](file:///home/workstation/Dev/oracle/ejemplo/seguimiento-tareas/README.md): instrucciones de consumo, arnés [`evaluar.py`](file:///home/workstation/Dev/oracle/ejemplo/seguimiento-tareas/evaluar.py), catálogo de políticas y casos de corpus.
- **Implementación**:
  - [`tools/tareas.py`](file:///home/workstation/Dev/oracle/tools/tareas.py): resolución de raíz, parseo de metadatos y comandos centrales P1 (`init`, `nueva`, `listar`, `ver`, `cerrar`, `reabrir`, `revisar`).
  - [`tools/tareas_contexto.py`](file:///home/workstation/Dev/oracle/tools/tareas_contexto.py): comandos P2 (`anotar`, `adjuntar`, `buscar`, `referencias`, `resumen`).
  - [`tools/tareas_git.py`](file:///home/workstation/Dev/oracle/tools/tareas_git.py): diagnóstico de seguimiento y cobertura de Git.
  - [`tools/tareas_hechos.py`](file:///home/workstation/Dev/oracle/tools/tareas_hechos.py): extracción y clasificación de hechos relacionales P3.

---

## 2. Hallazgos y discrepancias concretas

### Hallazgo 1: Archivo de origen inexistente en el paso 3 del tutorial
- **Nivel de certeza**: Comprobado por lectura.
- **Detalle**: En [`docs/12-tareas.md#L233-L234`](file:///home/workstation/Dev/oracle/docs/12-tareas.md#L233-L234), el paso 3 indica:
  ```bash
  # 3. Adjuntar una captura o registro de error local
  oracle tarea adjuntar 20260912-120000 /tmp/captura_sensor.png
  ```
  Sin embargo, el archivo `/tmp/captura_sensor.png` no ha sido creado en ningún paso previo ni se incluye una instrucción para generarlo. En [`tools/tareas_contexto.py#L423-L426`](file:///home/workstation/Dev/oracle/tools/tareas_contexto.py#L423-L426), `cmd_adjuntar` consulta el archivo con `os.lstat(origen)`: si no existe en disco, aborta de inmediato con:
  ```text
  ERROR: no se pudo consultar el archivo de origen: [Errno 2] No such file or directory: '/tmp/captura_sensor.png'
  ```
  y código de salida `1`. Quien siga el tutorial paso a paso encontrará una falla en este punto.
- **Reproducción propuesta**:
  1. Ejecutar secuencialmente los pasos 1 y 2 del tutorial en un proyecto limpio.
  2. Ejecutar el paso 3 tal como está redactado sin crear `/tmp/captura_sensor.png`.
  3. Comprobar que el comando falla con código de salida `1`.
- **Propuesta de corrección**: Agregar una instrucción previa en el tutorial (ej. `touch /tmp/captura_sensor.png` o `echo "volcado" > /tmp/captura_sensor.png`).

---

### Hallazgo 2: Omisión de inicialización previa (`init`) al ejercitar en un proyecto nuevo
- **Nivel de certeza**: Comprobado por lectura.
- **Detalle**: El tutorial introduce la sección indicando: *"Para ejercitar el flujo completo de captura, consulta y extracción de hechos sin alterar proyectos reales..."* ([`docs/12-tareas.md#L220`](file:///home/workstation/Dev/oracle/docs/12-tareas.md#L220)) y arranca de inmediato con `# 1. Crear una tarea nueva: oracle tarea nueva ...`. Si un usuario sigue esa consigna ubicándose en un directorio vacío temporal (ej. `mkdir /tmp/prueba && cd /tmp/prueba`), el comando `oracle tarea nueva` falla con:
  ```text
  ERROR: no se encontró ningún tracker de tareas (`tareas/`). Usá `oracle tarea init` para crearlo.
  ```
  y código `1`, debido a que `cmd_nueva` ([`tools/tareas.py#L659`](file:///home/workstation/Dev/oracle/tools/tareas.py#L659)) llama a `resolver_raiz_tracker` con `permitir_crear=False`.
- **Reproducción propuesta**:
  1. Crear un directorio vacío y posicionarse en él (`mkdir /tmp/sandbox && cd /tmp/sandbox`).
  2. Ejecutar directamente el paso 1: `oracle tarea nueva "Desincronización de eventos en sensor" --etiqueta bug --etiqueta sensor --sufijo sinc`.
  3. Se observa el rechazo con código `1` por falta de `tareas/`.
- **Propuesta de corrección**: Incluir un paso previo explícito (`# 0. Inicializar el tracker: oracle tarea init`).

---

### Hallazgo 3: Búsqueda de referencias devuelve cero coincidencias en el tutorial
- **Nivel de certeza**: Comprobado por lectura.
- **Detalle**: En el paso 5 del tutorial ([`docs/12-tareas.md#L239-L241`](file:///home/workstation/Dev/oracle/docs/12-tareas.md#L239-L241)), se ejecuta:
  ```bash
  # 5. Rastrear en qué archivos de código o tareas se menciona el ID de esta tarea
  oracle tarea referencias 20260912-120000
  ```
  `cmd_referencias` resuelve el prefijo al ID canónico `20260912-120000-sinc` y busca menciones textuales en los archivos del proyecto. La plantilla inicial de `TAREA.md` no escribe su propio identificador en el texto y los pasos anteriores no crearon archivos de código que lo citen. En consecuencia, el comando emite:
  ```text
  No se encontraron referencias para «20260912-120000-sinc».
  ```
  Aunque la operación finaliza con código `0` según contrato, a nivel didáctico puede desconcertar si se espera ver coincidencias.
- **Reproducción propuesta**: Ejecutar los pasos 1 a 4 e invocar el paso 5; constatar que la salida reporta cero referencias.
- **Propuesta de corrección**: Aclarar brevemente en el comentario del tutorial que en este punto no habrá menciones externas salvo que se simule una en un archivo de código o nota.

---

### Hallazgo 4: Discrepancia en el nombre del archivo de hechos entre el tutorial y el ejemplo
- **Nivel de certeza**: Comprobado por lectura.
- **Detalle**: En [`docs/12-tareas.md#L249`](file:///home/workstation/Dev/oracle/docs/12-tareas.md#L249), el paso 8 redirige a `/tmp/hechos-tracker.json`:
  ```bash
  oracle tarea hechos --git > /tmp/hechos-tracker.json
  ```
  En cambio, en [`ejemplo/seguimiento-tareas/README.md#L20-L21`](file:///home/workstation/Dev/oracle/ejemplo/seguimiento-tareas/README.md#L20-L21) y [`#L30`](file:///home/workstation/Dev/oracle/ejemplo/seguimiento-tareas/README.md#L30), tanto la extracción como la invocación de `evaluar.py` utilizan `/tmp/hechos-tareas.json`:
  ```bash
  oracle tarea hechos --proyecto /ruta/al/proyecto --git > /tmp/hechos-tareas.json
  python3 ejemplo/seguimiento-tareas/evaluar.py --con /tmp/hechos-tareas.json
  ```
- **Propuesta de corrección**: Estandarizar la ruta a `/tmp/hechos-tareas.json` en [`docs/12-tareas.md#L249`](file:///home/workstation/Dev/oracle/docs/12-tareas.md#L249) para que coincida directamente con el script consumidor documentado en la línea 159.

---

### Hallazgo 5: Tratamiento asimétrico de excepciones (`ValueError`) en `cmd_hechos` frente a `cmd_seguimiento`
- **Nivel de certeza**: Hipótesis fundamentada por análisis estático comparativo de código.
- **Detalle**: En [`tools/tareas_git.py#L155`](file:///home/workstation/Dev/oracle/tools/tareas_git.py#L155), `cmd_seguimiento` envuelve la llamada con:
  ```python
  try:
      ...
  except (tareas.TareaError, OSError, ValueError) as e:
  ```
  En cambio, en [`tools/tareas_hechos.py#L834`](file:///home/workstation/Dev/oracle/tools/tareas_hechos.py#L834), `cmd_hechos` únicamente captura:
  ```python
  except (TareaError, OSError) as e:
  ```
  Si `tareas_git.seguimiento(raiz)` propaga un `ValueError` (por ejemplo, en [`tools/tareas_git.py#L86`](file:///home/workstation/Dev/oracle/tools/tareas_git.py#L86) si `raiz.relative_to(repo)` falla debido a una configuración no canónica de Git worktrees o enlaces donde `raiz` no quede como subruta de `repo`), `cmd_seguimiento` lo maneja de forma limpia con mensaje de error y código `1`, mientras que `cmd_hechos` emitiría un traceback no capturado.
- **Reproducción propuesta**: Invocar `oracle tarea hechos --git` sobre una raíz que no pertenezca jerárquicamente a la ruta devuelta por `git rev-parse --show-toplevel`.
- **Propuesta de corrección**: Añadir `ValueError` a la cláusula `except` de `cmd_hechos` en [`tools/tareas_hechos.py#L834`](file:///home/workstation/Dev/oracle/tools/tareas_hechos.py#L834), o asegurar que `tareas_git.seguimiento` capture `ValueError` internamente y lo relance como `TareaError`.

---

## 3. Conclusión del relevamiento

Salvo los puntos señalados en el flujo del tutorial y la asimetría menor de excepciones, la especificación de `docs/12-tareas.md`, el catálogo de políticas de `ejemplo/seguimiento-tareas/` y la implementación en los cuatro módulos Python mantienen coherencia estricta en formatos, tipos y códigos de salida (0, 1 y 2). El árbol permanece congelado e intacto para la fase de mutación y uso propio coordinada por Codex.
