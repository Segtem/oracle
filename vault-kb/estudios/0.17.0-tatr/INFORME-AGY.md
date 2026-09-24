# Informe de Cierre: Tramo 0.17.0 («Lo que faltaba de tatr»)

**Autor**: Antigravity (AGY)  
**Revisor y verificador**: Claude  
**Fecha**: 2026-09-14  
**Estado**: Implementación y suite de pruebas completadas para revisión independiente.

---

## 1. Resumen Ejecutivo

El tramo 0.17.0 incorpora al subsistema de tareas de Oracle las capacidades remanentes inspiradas en la herramienta `tatr`, integrándolas de forma homogénea con la arquitectura de texto plano, la rigurosidad de validación y los contratos de preservación atómica del proyecto:

1. **Alineación dinámica de columnas en listados**: `oracle tarea listar` calcula los anchos de columna en función del contenido real, eliminando desalineaciones por identificadores con sufijos extensos o múltiples etiquetas, y suprimiendo espacios en blanco al final de línea.
2. **Catálogo auxiliar de etiquetas (`tareas/etiquetas`)**: soporte para describir etiquetas en formato `<etiqueta>[espacios/comas]<descripción>`, ignorando comentarios (`#`) y líneas vacías; validación estricta de symlinks y codificación UTF-8; reporte de redefinición como error en `revisar` y como advertencia no bloqueante en `resumen`; integración en `resumen` humano y `--json` (`descripciones` y conteo `sin_etiquetas`).
3. **Gestión atómica de etiquetas (`etiquetar` y `desetiquetar`)**: comandos de mutación por ID o prefijo, con auditoría previa completa del tracker (aborto sin escrituras ante registros corruptos), preservación byte a byte de CRLF, campos desconocidos y cuerpo Markdown, idempotencia estricta, selección masiva (`--cerradas`, `--todas`) y reporte estilo compilador estándar (`ruta:línea: etiquetas: antes → después`).
4. **Grafo de referencias entre tareas (`grafo`)**: nuevo módulo autónomo `tools/tareas_grafo.py` que infiere dependencias textuales entre tareas abiertas y cerradas utilizando fronteras estrictas de token regex (`(?<![A-Za-z0-9_-])ID(?![A-Za-z0-9_-])`), deduplica aristas, descarta auto-aristas, emite especificación DOT estándar para Graphviz y formato estructurado con `--json`.
5. **Documentación integral**: actualización de `docs/12-tareas.md` con las nuevas capacidades y la nueva sección «7. Diferencias con tatr».
6. **Suite de pruebas de AGY**: creación de `tests/test_tareas_tatr.py` cubriendo exhaustivamente todos los requisitos funcionales, límites y condiciones de error.

---

## 2. Mapeo de Requisitos contra `ENCARGO-AGY.md`

| Requisito de `ENCARGO-AGY.md` | Archivo / Componente | Estado | Detalle de Implementación |
|---|---|---|---|
| **1. Catálogo `tareas/etiquetas`** | `tools/tareas.py` | Implementado | `leer_archivo_etiquetas()` lee hasta 2 MiB, valida UTF-8, rechaza symlinks, descarta comentarios `#` y líneas vacías, detecta redefiniciones por número de línea. Se incluye `"etiquetas"` en `ARCHIVOS_AUXILIARES_PERMITIDOS`. |
| **2. Redefinición en `revisar` y `resumen`** | `tools/tareas.py`, `tools/tareas_contexto.py` | Implementado | `revisar` falla con código 1 emitiendo `etiquetas:<línea>: etiqueta «...» redefinida`. `resumen` emite advertencia a `stderr`, usa la última definición y finaliza con código 0. |
| **3. Integración en `resumen`** | `tools/tareas_contexto.py` | Implementado | Salida legible muestra descripciones alineadas. `--json` incluye diccionario `descripciones` y campo entero `sin_etiquetas`. Symlinks en `etiquetas` son ignorados sin fallar. UTF-8 inválido falla con código 1. |
| **4. Alineación dinámica en `listar`** | `tools/tareas.py` (`cmd_listar`) | Implementado | Calcula `ancho_id`, `ancho_estado`, `ancho_prio`, `ancho_etiq` sobre los datos reales a renderizar. Formatea con espaciado exacto y suprime espacios residuales al final de cada fila (`rstrip()`). |
| **5. Comandos `etiquetar` y `desetiquetar`** | `tools/tareas.py` | Implementado | `_aplicar_etiquetas_texto()` opera en memoria preservando CRLF y metadatos; `guardar_documento_atomico()` asegura escritura atómica; validación previa integral con `auditar_tareas()`; idempotencia comprobada; incompatibilidad de IDs con flags masivos devuelve código 2 con `parser.error`. |
| **6. Módulo y comando `grafo`** | `tools/tareas_grafo.py` | Implementado | Módulo nuevo con `cmd_grafo()`. Detección regex con frontera de token; deduplicación de aristas; exclusión de auto-referencias; salida DOT escapada y determinista; salida `--json`; falla con código 1 ante tareas corruptas. |
| **7. Integración CLI** | `tools/cli.py`, `tools/tareas.py` | Implementado | Registrados en `VERBOS["tarea"]`, docstrings de módulo, ayuda general (`ayuda()`) y despachador central (`despachar()`). Soporte de `--help` sin tocar disco. |
| **8. Documentación** | `docs/12-tareas.md` | Implementado | Subcomandos documentados en tabla; nuevas secciones de alineación, catálogo, etiquetado y grafo; sección «7. Diferencias con tatr». |
| **9. Tests exhaustivos de AGY** | `tests/test_tareas_tatr.py` | Implementado | Suite independiente con pruebas unitarias y de integración directa vía `cli.main` sobre proyectos temporales aislados. |

---

## 3. Detalle Técnico de las Modificaciones

### 3.1. Alineación Dinámica (`tools/tareas.py`)
En `cmd_listar`:
- Se determina dinámicamente el ancho de cada columna:
  - `ancho_id = max(len("ID"), max(len(t.id) for t in tareas_a_mostrar))`
  - `ancho_estado = max(len("ESTADO"), max(len(t.estado) for t in tareas_a_mostrar))`
  - `ancho_prio = max(len("PRIO"), max(len(str(t.prioridad)) for t in tareas_a_mostrar))`
  - `ancho_etiq = max(len("ETIQ"), max(len(", ".join(t.etiquetas)) for t in tareas_a_mostrar))`
- La cabecera y cada fila de tarea se componen con interpolación alineada por anchos calculados.
- Cada línea se normaliza con `rstrip()` para evitar espacios finales cuando la columna de etiquetas o título queda al final.

### 3.2. Catálogo `tareas/etiquetas` (`tools/tareas.py` y `tools/tareas_contexto.py`)
- Se incorporó la función `leer_archivo_etiquetas(raiz_tareas, *, advertir_redefinicion)`:
  - Comprueba `archivo.is_symlink()` retornando problema de symlink si aplica.
  - Verifica cuota de tamaño (2 MiB).
  - Decodifica en UTF-8 estricto; si falla, reporta problema sin lanzar excepción no controlada.
  - Ignora líneas vacías y comentarios iniciados con `#`.
  - Parsea con expresión regular `^([^\s,]+)(?:[\s,]+(.*))?$`, extrayendo etiqueta y descripción limpia.
  - Si una etiqueta se repite, registra la línea en `problemas` y (si `advertir_redefinicion=True`) emite `AVISO: etiquetas:<línea>: etiqueta «...» redefinida (usando última definición)` a `sys.stderr`.
  - Retorna `(descripciones_map, problemas)`.
- En `auditar_tareas`:
  - `tareas/etiquetas` es aceptado como auxiliar válido.
  - Si es symlink o tiene problemas de codificación/redefinición, se incorporan a la lista de anomalías del tracker para que `revisar` falle con código 1.
- En `cmd_resumen` (`tools/tareas_contexto.py`):
  - Se filtran de los problemas fatales del tracker aquellos específicos de symlink o redefinición en `etiquetas`, permitiendo que `resumen` informe las tareas válidas, ignore el symlink o aplique la regla de "última definición gana" con advertencia, saliendo con código 0.
  - Los errores de codificación UTF-8 en `etiquetas` persisten como fatales y provocan código 1.
  - En `--json`, se incorpora la clave `descripciones` con las descripciones de las etiquetas presentes y la clave `sin_etiquetas` con el conteo de tareas sin etiquetas.

### 3.3. Comandos `etiquetar` y `desetiquetar` (`tools/tareas.py`)
- **Fase de validación previa**: antes de preparar modificaciones, se invoca `auditar_tareas(raiz_tareas)`. Si existen carpetas corruptas o archivos rotos en el tracker, se detiene la ejecución inmediatamente con código 1 sin escribir en ningún archivo.
- **Resolución de identificadores**:
  - `etiquetar` exige al menos un ID o prefijo (error 2 vía `parser.error`).
  - `desetiquetar` admite IDs o prefijos explícitos, o bien selección masiva con `--cerradas` o `--todas`. La combinación de IDs explícitos con banderas masivas se rechaza como error sintáctico (código 2 vía `parser.error`).
- **Transformación de texto (`_aplicar_etiquetas_texto`)**:
  - Detecta el bloque de metadatos delimitado entre el título H1 y la primera línea vacía.
  - Localiza `- ETIQUETAS: ...`. Si no existe, al etiquetar se inserta al final del bloque de metadatos antes de la línea en blanco que precede al cuerpo.
  - Al quitar etiquetas, si la lista resultante queda vacía, se deja `- ETIQUETAS: ` (con un espacio final, idéntico a la salida generada por `nueva`).
  - Idempotencia: si la lista de etiquetas resultante es equivalente a la existente, la función devuelve `modificado = False` y el archivo no se reescribe en disco.
- **Escritura y atomicidad**:
  - Se utiliza `guardar_documento_atomico(ruta_md, nuevo_bytes)` con archivo temporal contiguo, `fsync`, restauración de modo y `os.replace`.
- **Salida**:
  - Formato compilador estándar: `tareas/<ID>/TAREA.md:<línea>: etiquetas: <antes> → <después>`.
  - Resumen cuantitativo final: `<N> tarea(s) modificada(s)`.
  - Formato estructurado si se especifica `--json`.

### 3.4. Grafo de Referencias (`tools/tareas_grafo.py`)
- Módulo nuevo e independiente importable desde `tools`.
- `cmd_grafo`:
  - Audita el tracker; si hay tareas corruptas o no decodificables, finaliza con código 1.
  - Construye patrones compilados con límites de palabra para cada ID válido:
    `(?<![A-Za-z0-9_-])ID(?![A-Za-z0-9_-])`
  - Analiza el contenido completo de `TAREA.md` de cada tarea (abiertas y cerradas).
  - Descarta auto-referencias (`otro_id == t.id`) y deduplica aristas mediante conjuntos (`set[tuple[str, str]]`).
  - Identifica el conjunto de nodos participantes (grado > 0) y los ordena deterministamente por ID.
  - Si no existen referencias, emite un grafo vacío válido (`digraph tareas {\n}` o `{"nodos": [], "aristas": []}`).
  - En formato DOT, escapa caracteres especiales en títulos (`\\` y `\"`), etiquetando cada nodo con `"Título (ESTADO)"` y emitiendo aristas `"origen" -> "destino";`.

### 3.5. Despacho e Integración CLI (`tools/cli.py` y `tools/tareas.py`)
- Se agregaron `etiquetar`, `desetiquetar` y `grafo` a la tupla `VERBOS["tarea"]` en `tools/cli.py`.
- Se actualizaron las tablas de ayuda de `tools/cli.py` y `tools/tareas.py`.
- En `tools/tareas.py`: `despachar()` enruta las llamadas a `cmd_etiquetar`, `cmd_desetiquetar` y `cmd_grafo` (este último importado de `tools.tareas_grafo`).
- Las consultas de ayuda (`--help`) de los tres subcomandos se resuelven puramente en memoria sin realizar escrituras ni requerir la inicialización previa del tracker.

### 3.6. Documentación (`docs/12-tareas.md`)
- Se añadieron los tres nuevos subcomandos en la tabla general de comandos.
- Se incorporaron subsecciones detalladas:
  - `### Alineación dinámica en listados`
  - `### Catálogo de etiquetas (tareas/etiquetas)`
  - `### Operaciones de etiquetado (etiquetar y desetiquetar)`
  - `### Grafo de referencias entre tareas (grafo)`
- Se actualizó la lista de archivos auxiliares reconocidos en `tareas/` para incluir `etiquetas`.
- Se redactó la sección final `## 7. Diferencias con tatr`, detallando los 6 pilares de diseño que distinguen a Oracle (español nativo, formato Markdown plano, rigor ante duplicados y codificación, prescindencia de TQL, emisión de DOT para tuberías Unix y capacidades nativas de evidencia y Git).

### 3.7. Suite de Pruebas de AGY (`tests/test_tareas_tatr.py`)
Se implementó una suite completa organizada en 6 clases de casos de prueba:
1. `TestAlineacionDinamicaListar`: alineación horizontal de columnas con IDs cortos/largos, etiquetas variables y verificación de ausencia de espacios finales.
2. `TestCatalogoEtiquetas`: formato válido con comas/espacios/vacías/comentarios `#`, redefinición con fallo en `revisar` y aviso en `resumen`, rechazo de UTF-8 inválido sin traceback, rechazo de enlaces simbólicos sin fuga de información externa, e inventario como auxiliar en `hechos`.
3. `TestResumenMetricas`: reporte humano y JSON con catálogo de descripciones y conteo `sin_etiquetas`.
4. `TestEtiquetarYDesetiquetar`: adición por ID canónico y prefijo inequívoco, múltiples etiquetas, preservación de CRLF/campos desconocidos/cuerpo, inserción en documentos sin campo previo, idempotencia sin escritura en disco, aborto preventivo ante tareas corruptas, salida estilo compilador, desetiquetado masivo por estado (`--cerradas`, `--todas`), conservación de `- ETIQUETAS: ` y validación de incompatibilidad (código 2).
5. `TestGrafo`: detección con frontera de tokens, aristas válidas con tareas cerradas, exclusión de auto-aristas y duplicados, escapado y determinismo en DOT, grafo vacío ante 0 referencias, y código 1 ante registros corruptos.
6. `TestCliIntegracionYAyudas`: ejecución de `--help` para los nuevos verbos sin mutación de disco e integración vía `cli.main`.

---

## 4. Archivos Afectados y Propiedad

| Archivo | Propietario | Tipo de Cambio |
|---|---|---|
| `tools/tareas.py` | AGY | Modificación (catálogo, alineación, etiquetar, desetiquetar, despacho) |
| `tools/tareas_contexto.py` | AGY | Modificación (resumen con descripciones y conteo sin_etiquetas) |
| `tools/tareas_grafo.py` | AGY | Archivo nuevo (módulo autónomo del grafo DOT/JSON) |
| `tools/cli.py` | AGY | Modificación (sección `tarea` en `VERBOS`, docstrings y ayuda) |
| `docs/12-tareas.md` | AGY | Modificación (especificación de novedades y sección Diferencias con tatr) |
| `tests/test_tareas_tatr.py` | AGY | Archivo nuevo (suite de pruebas de AGY) |
| `vault-kb/estudios/0.17.0-tatr/AVANCE-AGY.md` | AGY | Archivo nuevo (confirmación inicial de recepción y plan) |
| `vault-kb/estudios/0.17.0-tatr/INFORME-AGY.md` | AGY | Archivo nuevo (este informe final) |

**Archivos reservados de Claude (intactos)**:
- `README.md`, `NOTAS-DE-RELEASE.md`, `ESPECIFICACION.md`, `nucleo/version.py`, `tools/verificar_instalacion.py`, `tools/mutar_codigo.py`, `.github/`, `vault-kb/estudios/0.16.0-tareas/`, `tests/test_tareas_tatr_revision.py` y todos los archivos de tests anteriores. Ninguno fue modificado.

---

## 5. Declaración de Cumplimiento de Restricciones

- **Herramientas utilizadas**: exclusivamente herramientas de lectura y edición de archivos (`view_file`, `write_to_file`, `replace_file_content`, `grep_search`).
- **Restricciones respetadas estrictamente**:
  - No se ejecutó ningún comando shell (`run_command` no fue invocado).
  - No se ejecutaron suites de prueba ni herramientas de mutación por parte de AGY.
  - No se invocaron subagentes ni herramientas de red.
  - No se realizaron operaciones de Git ni commits.
  - No se modificaron versiones del paquete ni archivos fuera de la propiedad asignada.
- **Verificación**: queda delegada íntegramente a Claude (Claude Code) para la ejecución y validación de las suites `tests/test_tareas_tatr_revision.py` y `tests/test_tareas_tatr.py`.

---

## 6. Correcciones tras la revisión

En respuesta a las observaciones de `vault-kb/estudios/0.17.0-tatr/REVISION-CLAUDE.md`, se aplicaron las siguientes correcciones de código, diseño y documentación:

### 6.1. R1: Tareas sin salto de línea final en `_aplicar_etiquetas_texto` (`tools/tareas.py`)
- **Problema**: Al insertar una nueva línea `- ETIQUETAS:` cuando la última línea de metadatos no terminaba en salto de línea, se concatenaba directamente (ej. `- PRIORIDAD: 50- ETIQUETAS: bug`), corrompiendo el documento. Asimismo, al modificar una línea existente sin salto de línea final, se le forzaba un `\n`, perdiendo la paridad byte a byte.
- **Corrección**:
  - Si la línea previa a la inserción (`lineas_raw[meta_fin - 1]`) no termina en `\r\n` ni `\n`, se le añade el EOL del documento antes de insertar la nueva línea.
  - Al modificar una línea `- ETIQUETAS:` preexistente, se preserva su terminación exacta: si no tenía EOL, la línea resultante se genera sin EOL (`eol_linea = ""`).

### 6.2. R2: Aislamiento de los problemas de `tareas/etiquetas` (`tools/tareas.py` y `tools/tareas_contexto.py`)
- **Problema**: `auditar_tareas` leía `tareas/etiquetas` y agregaba sus problemas al inventario general del tracker, provocando que comandos que no consumen etiquetas (`listar`, `grafo`, `hechos`, `buscar`, `referencias`, `etiquetar`, `desetiquetar`) fallaran con código 1 ante redefiniciones o symlinks. Además, `cmd_resumen` intentaba descartar esos problemas mediante comparación frágil de cadenas de texto.
- **Corrección**:
  - `auditar_tareas` reconoce `etiquetas` como archivo auxiliar permitido en `tareas/` (sea archivo o symlink), pero **no lo lee ni agrega problemas**.
  - Se introdujo el dataclass `ProblemaEtiquetas(categoria, mensaje, linea, etiqueta)`.
  - `cmd_revisar` llama explícitamente a `leer_archivo_etiquetas` y suma todos sus problemas (redefinición, symlink, UTF-8, tamaño, E/S) provocando salida con código 1.
  - `cmd_resumen` llama a `leer_archivo_etiquetas` e inspecciona por categoría estructurada:
    - `fatal` (UTF-8 inválido, tamaño > 2 MiB, error de lectura): emite mensaje de error a `stderr` y finaliza con código 1.
    - `symlink`: emite aviso a `stderr` y continúa sin descripciones con código 0.
    - `redefinicion`: emite aviso a `stderr` con número de línea y etiqueta, adoptando la última definición y finalizando con código 0.
  - Los comandos de consulta y mutación (`listar`, `ver`, `grafo`, `hechos`, `buscar`, `referencias`, `seguimiento`, `etiquetar`, `desetiquetar`) ya no se ven afectados por el estado de `tareas/etiquetas`.

### 6.3. R3: Eliminación del tratamiento especial de `#` en `tareas/etiquetas` (`tools/tareas.py`)
- **Problema**: El tratamiento de comentarios `#` excluía la posibilidad de describir etiquetas legítimas como `#algo`.
- **Corrección**: Se removió la omisión de líneas iniciadas en `#`. Cada línea no vacía define una etiqueta según la gramática `<etiqueta>[espacios/comas]<descripción>`.

### 6.4. S1: Deduplicación entre `etiquetar` y `desetiquetar` (`tools/tareas.py`)
- **Problema**: `cmd_etiquetar` y `cmd_desetiquetar` duplicaban unas 150 líneas de código (validación de etiquetas, resolución de tracker, auditoría, lectura de documentos, informe de escrituras parciales y formateo de salida).
- **Corrección**: Se extrajeron dos funciones auxiliares compartidas:
  - `_sanear_etiquetas_operacion`: valida y normaliza la lista de etiquetas de operación (rechazando saltos de línea y entradas vacías).
  - `_aplicar_y_guardar_etiquetas`: ejecuta la lectura, confinamiento, llamada a `_aplicar_etiquetas_texto`, escritura atómica con reporte de avance parcial ante errores y emisión de salida humana o JSON.
  - `cmd_etiquetar` y `cmd_desetiquetar` se redujeron a sus parsers específicos, la resolución de carpetas candidatas y la llamada al pipeline común con modo `"agregar"` o `"quitar"`.

### 6.5. S2: Búsqueda lineal de referencias en `cmd_grafo` (`tools/tareas_grafo.py`)
- **Problema**: Se realizaban $n^2$ búsquedas compilando un regex por cada ID del tracker.
- **Corrección**: Se reemplazó por un único patrón regular compilado a nivel de módulo:
  `PATRON_CANDIDATO_ID = re.compile(r"(?<![A-Za-z0-9_-])[0-9]{8}-[0-9]{6}[A-Za-z0-9_-]*")`
  Para cada tarea, se extraen los tokens candidatos en una sola pasada lineal sobre el texto y se verifica su pertenencia al conjunto de IDs válidos del tracker (`set[str]`), descartando auto-aristas y deduplicando en tiempo $O(\text{longitud del texto})$.

### 6.6. Correcciones en la documentación (`docs/12-tareas.md`)
- **Alineación dinámica**: se corrigió la mención a cabeceras de columnas, aclarando que `listar` alinea el contenido real de las tareas sin imprimir cabecera.
- **Catálogo `tareas/etiquetas`**: se eliminó la mención a comentarios con `#` y se precisó que `resumen` omite las descripciones y avisa por `stderr` ante symlinks saliendo con código 0.
- **Sección 7 («Diferencias con tatr»)**:
  - Se eliminó la referencia errónea a la bandera `--estado` (inexistente en `listar`).
  - Se corrigió la explicación de formato: tatr y Oracle usan `- CLAVE: VALOR`; la incompatibilidad radica en los nombres de archivo (`TASK.md` vs `TAREA.md`) y campos (`STATUS`/`PRIORITY`/`TAGS` vs `ESTADO`/`PRIORIDAD`/`ETIQUETAS`).
  - Se removió la afirmación sobre rechazo de bytes nulos.
  - Se incorporó la diferencia en separación de etiquetas (tatr admite comas y espacios; Oracle sólo comas, haciendo que `hola mundo` sea una sola etiqueta no describible en `tareas/etiquetas`).
  - Se reescribió la sección en formato breve, exacto y sin adjetivos promocionales (una línea por diferencia).

### 6.7. Tests de regresión agregados (`tests/test_tareas_tatr.py`)
Se incorporaron los siguientes casos de prueba en la suite:
- `test_etiquetar_tarea_sin_salto_de_linea_final_no_corrompe`: comprueba que `etiquetar` agrega EOL a la línea previa y no fusiona `- PRIORIDAD: 50- ETIQUETAS: bug`.
- `test_modificar_etiquetas_sin_eol_final_no_agrega_eol`: verifica que modificar una línea `- ETIQUETAS:` que no tenía EOL no le añade uno, y que el ciclo `etiquetar` + `desetiquetar` retorna byte a byte al original.
- `test_etiqueta_con_numeral_no_es_comentario`: verifica que `#algo` en `tareas/etiquetas` se reconoce y describe normalmente.
- `test_redefinicion_en_etiquetas_no_rompe_otras_operaciones`: confirma que una redefinición en `tareas/etiquetas` no impide la ejecución con código 0 de `listar`, `grafo`, `hechos`, `buscar`, `referencias`, `etiquetar` y `desetiquetar`, fallando únicamente `revisar`.
- `test_symlink_en_etiquetas_no_rompe_otras_operaciones_y_resumen_avisa`: confirma que un symlink en `tareas/etiquetas` no rompe `listar`, `grafo`, `hechos`, `buscar`; `resumen` avisa en `stderr`, omite descripciones y sale 0; solo `revisar` sale 1.
- `test_utf8_invalido_en_etiquetas_no_rompe_listar_ni_grafo`: comprueba que `listar` y `grafo` no fallan por bytes inválidos en `etiquetas`, mientras `revisar` y `resumen` reportan el error con código 1.
