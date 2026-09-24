Se ha creado exclusivamente el archivo [`tests/test_tareas_errores.py`](file:///home/workstation/Dev/oracle/tests/test_tareas_errores.py) para cubrir los sobrevivientes de mutación identificados en `/tmp/oracle-p4-r2-tareas/hechos.json` correspondientes a los comandos P1 (`tools/tareas.py` desde la línea 470 hasta el final), sin ejecutar comandos de shell, sin lanzar tests ni mutación, y sin modificar ningún otro archivo del repositorio.

---

### Resumen de Pruebas Implementadas en [`tests/test_tareas_errores.py`](file:///home/workstation/Dev/oracle/tests/test_tareas_errores.py)

El archivo contiene 43 pruebas directas en proceso aisladas con sandboxes temporales y captura de `stdout`/`stderr` mediante `_callado`, aplicando `unittest.mock.patch` estrictamente en las fronteras de E/S del sistema operativo y validando códigos de salida exactos (`1` ante errores y `0` en casos positivos):

1. **`TestErroresRaizYDirectorio` (10 tests)**:
   - Exigencia de código exacto `1` ante fallo de resolución de raíz (`resolver_raiz_tracker`) en [`cmd_init`](file:///home/workstation/Dev/oracle/tools/tareas.py#L482-L490), [`cmd_nueva`](file:///home/workstation/Dev/oracle/tools/tareas.py#L575-L579), [`cmd_listar`](file:///home/workstation/Dev/oracle/tools/tareas.py#L642-L646), [`cmd_ver`](file:///home/workstation/Dev/oracle/tools/tareas.py#L710-L714), [`cmd_cerrar`](file:///home/workstation/Dev/oracle/tools/tareas.py#L789-L793), [`cmd_reabrir`](file:///home/workstation/Dev/oracle/tools/tareas.py#L835-L839) y [`cmd_revisar`](file:///home/workstation/Dev/oracle/tools/tareas.py#L881-L885).
   - Detección y rechazo estricto con código `1` cuando el directorio `tareas/` es un enlace simbólico (`raiz_tareas.is_symlink()`) en `cmd_init` (L493) y `cmd_nueva` (L582).
   - Rechazo estricto con código `1` cuando `README.md` es un enlace simbólico en `cmd_init` (L507).

2. **`TestErroresEntradaNueva` (6 tests)**:
   - Rechazo con código `1` ante título vacío (`""`) o compuesto exclusivamente por espacios en blanco (L558-L561).
   - Rechazo con código `1` ante títulos que contengan saltos de línea LF (`\n`) o CR (`\r`) (L562-L564).
   - Rechazo con código `1` ante etiquetas que contengan saltos de línea LF (`\n`) o CR (`\r`) (L568-L570).

3. **`TestErroresIOYArchivo` (11 tests)**:
   - Fallo de E/S en `raiz_tareas.mkdir` en `cmd_init` retornando exactamente `1` (L501-L504).
   - Fallo de E/S en `os.open` de `README.md` en `cmd_init` retornando exactamente `1` (L526-L528).
   - Fallo de E/S en `crear_carpeta_tarea_atomica` en `cmd_nueva` retornando exactamente `1` (L592-L595).
   - Fallo de E/S en `Path.write_text` en `cmd_nueva` retornando exactamente `1` (L606-L609).
   - Incompatibilidad de banderas `--ruta` y `--json` en `cmd_ver` retornando exactamente `1` (L706-L708).
   - Tarea no encontrada por ID o prefijo inexistente en `cmd_ver` retornando exactamente `1` (L718-L721).
   - Carpeta candidata sin `TAREA.md` en `cmd_ver` retornando exactamente `1` (L724-L727).
   - Enlace simbólico de `TAREA.md` que escapa del confinamiento (`RutaInsegura`) en `cmd_ver` retornando exactamente `1` (L729-L732).
   - Fallo de E/S en `Path.read_bytes` en `cmd_ver` retornando exactamente `1` (L735-L738).
   - Bytes no UTF-8 en `TAREA.md` (`UnicodeDecodeError`) en `cmd_ver` retornando exactamente `1` (L741-L747).
   - Metadatos mal formados (`TareaInvalida`) en `cmd_ver` retornando exactamente `1` (L750-L753).

4. **`TestErroresActualizarEstado` (8 tests)**:
   - En `cmd_cerrar`: ID inexistente (L797-L800), carpeta sin `TAREA.md` (L803-L805), symlink fuera de confinamiento (L808-L811), y excepciones `TareaInvalida` u `OSError` propagadas desde [`actualizar_estado_tarea`](file:///home/workstation/Dev/oracle/tools/tareas.py#L814-L817), todas retornando exactamente `1`.
   - En `cmd_reabrir`: ID inexistente (L843-L846), carpeta sin `TAREA.md` (L849-L851), symlink fuera de confinamiento (L854-L857), y excepciones `TareaInvalida` u `OSError` propagadas desde [`actualizar_estado_tarea`](file:///home/workstation/Dev/oracle/tools/tareas.py#L860-L863), todas retornando exactamente `1`.

5. **`TestCasosPositivosComandos` (3 tests)**:
   - Idempotencia de `cmd_init` ante re-ejecución donde `README.md` ya existe (`FileExistsError` capturado limpiamente en L524), retornando `0`.
   - Filtrado positivo con `cmd_listar --cerradas` (tanto en salida humana como `--json`), retornando `0` y excluyendo tareas abiertas (L663-L666, L692).
   - Emisión limpia de la ruta absoluta con `cmd_ver --ruta`, retornando `0` sin volcado extra de metadatos (L756-L757).

6. **`TestErroresRevisar` (3 tests)**:
   - Auditoría fallida en modo humano emitiendo a `stderr` y retornando exactamente `1` (L901-L906).
   - Auditoría fallida en modo JSON (`--json`) emitiendo `ok: false` y retornando exactamente `1` (L891-L898).
   - Auditoría limpia en modo humano y modo JSON emitiendo `ok: true` y retornando exactamente `0` (L897, L908-L909).

7. **`TestDespachoYMain` (8 tests)**:
   - Subcomandos de ayuda en [`despachar`](file:///home/workstation/Dev/oracle/tools/tareas.py#L963-L968) (`""`, `"-h"`, `"--help"`, `"help"`) retornando `0`.
   - Verbo desconocido en `despachar` emitiendo error y retornando exactamente `1` (L1005-L1006).
   - Captura y traducción de `TareaError` y `OSError` a código `1` para los cinco verbos P2 (`anotar`, `adjuntar`, `buscar`, `referencias`, `resumen`) en `despachar` (L983-L997).
   - Delegación transparente y preservación del código de salida para `seguimiento` y `hechos` en `despachar` (L998-L1003).
   - Subcomandos y banderas de ayuda en [`main`](file:///home/workstation/Dev/oracle/tools/tareas.py#L1009-L1014) retornando `0`.
   - Invocación de `main` con `argv=None` consumiendo `sys.argv[1:]` ante ayuda, comandos válidos y verbos desconocidos (L1010).
   - Invocación de `main` con lista `argv` explícita pasando verbo y argumentos correctos a `despachar` (L1015-L1017).

---
El entorno queda preparado para que Codex ejecute la suite completa y la siguiente ronda diagnóstica de mutación.
