# Avance agy — Encargo P3 (Oracle 0.16.0: evidencia del tracker propio)

Fecha: 2026-09-12  
Responsable: agy  
Rama/Workspace: `/home/workstation/Dev/oracle`  
Base: distribución 0.15.0, álgebra 0.6, sintaxis 0.4.

---

## 1. Confirmación de recepción del encargo

Se recibe formalmente el encargo de continuación **P3** establecido en `estudios/0.16.0-tareas/ENCARGO-P3-AGY.md` y las observaciones de revisión de Codex en `estudios/0.16.0-tareas/REVISION-P3-CODEX.md`.
Se asumen los compromisos y delimitaciones:
- Implementación del nuevo verbo `hechos`: `oracle tarea hechos [--git] [--json] [--proyecto RUTA]`.
- Emisión directa a stdout del objeto JSON relacional estructurado (relación → lista de filas), consumible por `ejemplo/seguimiento-tareas/evaluar.py --con ARCHIVO.json`.
- Integración en `tools/tareas.py` (despacho por import local diferido de `tools.tareas_hechos.cmd_hechos(argv, args)` y ayuda) y en `tools/cli.py` (registro en `VERBOS["tarea"]`).
- Creación y endurecimiento de `tools/tareas_hechos.py` con todas las extracciones de hechos, inventario de archivos, análisis de enlaces Markdown y clasificación de referencias.
- Creación de la suite de pruebas de comportamiento `tests/test_tareas_hechos.py` (24 tests en 5 clases de prueba) invocando el CLI público sobre proyectos temporales.
- Documentación técnica del contrato relacional, relaciones, claves, límites de gramática y ejemplos en `docs/12-tareas.md`.
- Respeto estricto del modo de ejecución: sin comandos de shell (`run_command`), sin ejecución de tests por agy, sin subagentes, sin cambios de versión y sin commits ni push.
- Respeto de los archivos propiedad de Codex (`ejemplo/seguimiento-tareas/`, `tests/test_tareas_p3_revision.py`, `tools/verificar_instalacion.py` y suites previas).
- Entrega final en `estudios/0.16.0-tareas/INFORME-P3-AGY.md` documentando la implementación real sin inventar verificaciones.

---

## 2. Inventario de archivos asignados a agy

- `estudios/0.16.0-tareas/AVANCE-P3-AGY.md`: Bitácora viva de este tramo (actualizado).
- `tools/tareas_hechos.py`: Módulo núcleo de extracción de hechos relacionales (nuevo):
  - `lectura_seguimiento`: `{esquema: "oracle.tareas.hechos/v1", completa: bool, git: "no_solicitado"|"sin_repositorio"|"comprobado", head: str}`.
  - `tarea_seguimiento`: `{id, titulo, estado_declarado, prioridad_declarada, ruta, sha256_documento}`.
  - `archivo_seguimiento`: `{tarea_id, ruta, clase: "documento"|"adjunto"|"auxiliar", tipo: "regular"|"enlace"|"especial"|"ausente", tamano_bytes: int, existe: bool, git_comprobado: bool, en_indice: bool, en_head: bool, ignorado: bool, indice: str, trabajo: str}`.
  - `referencia_seguimiento`: `{tarea_id, origen, linea: int, destino_declarado, clase: "local"|"remota"|"ancla"|"no_admitida", estado: "presente"|"ausente"|"fuera_del_proyecto"|"no_comprobado"}`.
  - `omision_seguimiento`: `{ruta, linea: int, motivo: str}`.
- `tools/tareas.py`: Despacho diferido de `hechos` en `despachar()` y actualización de `ayuda()`.
- `tools/cli.py`: Declaración de `hechos` en `VERBOS["tarea"]`.
- `docs/12-tareas.md`: Sección P3 con especificación formal del contrato relacional, claves, reglas de extracción, límites y uso con redirección shell.
- `tests/test_tareas_hechos.py`: Suite de pruebas unitarias y de integración de hechos sobre proyectos temporales (nuevo, 24 tests).
- `estudios/0.16.0-tareas/INFORME-P3-AGY.md`: Informe final de entrega (nuevo).

---

## 3. Plan de trabajo del tramo y resoluciones de revisión

1. [x] Recepción del encargo y creación de `AVANCE-P3-AGY.md`.
2. [x] Implementación inicial de `tools/tareas_hechos.py`.
3. [x] Integración en `tools/tareas.py` y `tools/cli.py`.
4. [x] Implementación de la suite de pruebas `tests/test_tareas_hechos.py`.
5. [x] Actualización de `docs/12-tareas.md`.
6. [x] Atención de las observaciones de revisión de Codex (`REVISION-P3-CODEX.md`):
   - [x] Punto 1: Corrección de definición real al inicio de línea (`[clave]: destino`) y soporte sin espacios (`[clave]:destino`).
   - [x] Punto 2: Conservación de una fila por aparición en `referencia_seguimiento`, evitando colapsar destinos repetidos en la misma línea.
   - [x] Punto 3: Registro de omisión explícita y `completa=false` ante sintaxis multilínea o enlaces incompletos (`[nota](\nausente.txt)`).
   - [x] Punto 4: Clasificación case-insensitive de esquemas `http`/`https` (`HTTPS://...`), preservando texto original del destino.
   - [x] Punto 5: Cierre de bloque cercado exige exclusivamente espacios tras la cerca, impidiendo que ```` ```no-es-cierre ```` cierre el bloque.
   - [x] Punto 6: Inspección componente a componente de referencias locales sin normalizar con `resolve()`; detección de symlinks en componentes previos a `..` (`puente/../parece-local.txt`), y clasificación de archivos seguidos de `/..` como no directorios (`ausente`).
   - [x] Punto 7: Manejo estricto de E/S con `_lstat_seguro`: sólo `FileNotFoundError` o `NotADirectoryError` indican ausencia; `PermissionError` aborta con código 1 sin JSON parcial.
   - [x] Punto 8: Prechequeo acotado de documentos centrales `TAREA.md` (fallo con código 1 si supera 2 MiB o es symlink); adjuntos Markdown grandes se omiten sin abortar.
   - [x] Punto 31: Documentación de `ejemplo/seguimiento-tareas/evaluar.py --con ARCHIVO` como consumidor real.
   - [x] Punto 35: Literales escapados `\[texto](destino)` no se extraen como enlaces; declaración de límites reales de gramática.
7. [x] Actualización final de `estudios/0.16.0-tareas/INFORME-P3-AGY.md`.
