# Avance 0.17.0 — Lo que faltaba de tatr (AGY)

Fecha: 2026-09-14
Responsable: Agente Antigravity (AGY)
Revisa y verifica: Claude (Claude Code)

---

## 1. Confirmación de recepción

Se ha recibido y leído íntegramente el encargo en `estudios/0.17.0-tatr/ENCARGO-AGY.md`, junto con:
- `PLAN-0.16.0-TAREAS.md`
- `docs/12-tareas.md`
- `tools/tareas.py`
- `tools/tareas_contexto.py`
- `tools/tareas_hechos.py`
- `tools/tareas_git.py`
- `tools/cli.py` (registro de verbos, ayuda y despacho de `tarea`)
- `tests/test_tareas_tatr_revision.py` (suite de revisión independiente preparada por Claude)

Se asumen las reglas del tramo:
- Uso exclusivo de herramientas de lectura y edición.
- Sin comandos de shell, sin ejecución de tests, sin subagentes, sin acceso a red y sin commits.
- Respeto estricto de la propiedad de archivos: no se modifican archivos asignados a Claude ni tests preexistentes.
- Redacción honesta del informe final sin afirmar verificaciones o ejecuciones no realizadas.

---

## 2. Plan de archivos y responsabilidades

### Archivos de código y herramientas (propiedad de AGY)

1. **`tools/tareas.py`**:
   - Agregar `"etiquetas"` a `ARCHIVOS_AUXILIARES_PERMITIDOS`.
   - Implementar función auxiliar `leer_archivo_etiquetas(raiz_tareas, *, advertir_redefinicion)` para parsear `tareas/etiquetas` (`<etiqueta>[espacios/comas]<descripción>`), ignorar líneas vacías, normalizar case-insensitive, controlar symlinks, tamaño máximo (2 MiB) y decodificación UTF-8.
   - Actualizar `auditar_tareas`: auditar `tareas/etiquetas` si está presente, reportando redefiniciones con formato `etiquetas:<línea>`, symlinks y errores de UTF-8 como problemas que devuelven código 1.
   - Actualizar `cmd_listar`: cálculo dinámico de anchos de columna (`id`, `estado`, `prioridad`, `etiquetas`), asegurando alineación vertical con IDs de cualquier longitud y sin espacios sobrantes al final de línea (`.rstrip()`).
   - Implementar `cmd_etiquetar` y `cmd_desetiquetar`:
     - Validación previa total: parseo de argumentos `--etiqueta` (repetible y con comas), resolución de IDs (completos y prefijos inequívocos) o masivo por estado (`--cerradas`, `--todas` para `desetiquetar`), validación de integridad (ante registros rotos falla con 1 sin escribir ningún archivo).
     - Modificación atómica: edición exclusiva de la línea `- ETIQUETAS:` en el bloque de metadatos preservando el resto byte a byte (CRLF/LF, sangrías, campos adicionales, cuerpo). Inserción al final del bloque de metadatos si no existe la clave. Formateo de última etiqueta removida idéntico a `nueva` (`- ETIQUETAS: `).
     - Idempotencia: tareas sin cambios no modifican su `mtime`.
     - Salida tipo compilador (`tareas/<id>/TAREA.md:<línea>: etiquetas: ... → ...`) y conteo de tareas modificadas. Soporte de salida `--json`.
   - Actualizar `ayuda()` y `despachar()` para incluir `etiquetar`, `desetiquetar` y `grafo`.

2. **`tools/tareas_contexto.py`**:
   - Actualizar `cmd_resumen`:
     - Invocar `leer_archivo_etiquetas` (advirtiendo redefiniciones por stderr sin cambiar código de salida).
     - Presentar descripciones de etiquetas junto a sus cantidades en salida humana.
     - Contabilizar y reportar tareas `sin_etiquetas` (equivalente de tatr `UNTAGGED`).
     - En salida `--json`: incorporar `descripciones` por etiqueta (`null` si no tiene) y `sin_etiquetas`, preservando intactos los campos preexistentes (`total`, `estados`, `etiquetas`).

3. **`tools/tareas_grafo.py`** (nuevo módulo):
   - Crear el módulo con `cmd_grafo(argv, args)` con soporte para `--json` y `--proyecto`.
   - Auditoría previa de tareas (`auditar_tareas`); si hay registros rotos falla con código 1.
   - Extracción determinista de aristas entre tareas válidas basadas en la presencia del ID canónico completo en el contenido de `TAREA.md`, con límite estricto de token `(?<![A-Za-z0-9_-])ID(?![A-Za-z0-9_-])`.
   - Sin autoaristas y sin aristas duplicadas.
   - Selección de nodos: únicamente tareas que participen en al menos una arista (salvo grafo sin aristas que emite grafo vacío válido).
   - Generación determinista de salida DOT (ordenado por origen y destino, escapando comillas y barras invertidas en títulos) y formato JSON (`nodos` y `aristas`).

4. **`tools/cli.py`**:
   - Incorporar `etiquetar`, `desetiquetar` y `grafo` a `VERBOS["tarea"]`.
   - Actualizar docstring y texto de `ayuda()` general y `ayuda_tarea()`.

5. **`tools/tareas_hechos.py` y `tools/tareas_git.py`**:
   - Verificar y garantizar que `tareas/etiquetas` se reconozca como archivo auxiliar (mediante `ARCHIVOS_AUXILIARES_PERMITIDOS` en `tools.tareas`).

### Documentación

6. **`docs/12-tareas.md`**:
   - Actualizar tabla general de subcomandos con `etiquetar`, `desetiquetar` y `grafo`.
   - Documentar el archivo `tareas/etiquetas` con ejemplos y especificación de formato.
   - Documentar las operaciones `etiquetar` y `desetiquetar` (reglas de concurrencia, no transaccionalidad entre documentos, idempotencia).
   - Documentar `grafo`, el formato DOT generado y su uso en pipeline con Graphviz (`oracle tarea grafo | dot -Tsvg -o grafo.svg`).
   - Agregar la sección «Diferencias con tatr» detallando nombres, incompatibilidad de formato, rechazo estricto de duplicados, TQL fuera de alcance, emisión de DOT sin renderizado, y capacidades de captura/adjuntos/Git/hechos ausentes en tatr.

### Tests y memoria de trabajo

7. **`tests/test_tareas_tatr.py`** (nuevo archivo de tests):
   - Escribir batería completa de tests unitarios y de integración según lo solicitado en el encargo 6:
     - Alineación de columnas en `listar` con IDs cortos y largos, sin espacios finales.
     - Archivo `tareas/etiquetas`: formatos válidos, líneas vacías, redefiniciones en `revisar` y `resumen`, errores de UTF-8, enlaces simbólicos, clasificación auxiliar en `revisar` y `hechos`.
     - `resumen` con descripciones y `sin_etiquetas` (humano y JSON).
     - `etiquetar` y `desetiquetar`: IDs explícitos, prefijos inequívocos, masivo por estado, incompatibilidad de IDs con flags de estado, preservación de CRLF y campos adicionales, inserción de línea ausente, idempotencia y atomisimo previo ante registros rotos.
     - `grafo`: fronteras de token, autoaristas, duplicados, tareas cerradas, escapado de comillas y barras, determinismo, salida JSON y grafo vacío.
     - Ayuda de nuevos verbos sin efectos colaterales.

8. **`estudios/0.17.0-tatr/INFORME-AGY.md`**:
   - Informe final estructurado con el balance de cambios, detalle de implementación y notas técnicas para la revisión de Claude.
