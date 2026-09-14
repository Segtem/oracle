# Avance agy — Encargo P0 y P1 (Oracle 0.16.0: tracker de tareas)

Fecha de inicio: 2026-09-11.
Responsable: agy.
Base: checkout `/home/workstation/Dev/oracle`, distribución 0.15.0, álgebra 0.6, sintaxis 0.4.

## 1. Recepción del encargo

Se recibe el encargo documentado en `estudios/0.16.0-tareas/ENCARGO-AGY.md` y definido en `PLAN-0.16.0-TAREAS.md`.
El trabajo consiste en implementar de punta a punta los tramos **P0** (contrato mínimo, ejemplos, especificación de formato, identidad y descubrimiento) y **P1** (tracker local usable desde el CLI: `oracle tarea init`, `nueva`, `listar`/`ls`, `ver`, `cerrar`, `reabrir`, `revisar`, integración en CLI, tests exhaustivos y verificación).

Restricciones estrictas observadas:
- No cambiar versiones (`nucleo/version.py` permanece en 0.15.0).
- No realizar commits ni push ni tags.
- No lanzar otros agentes / subagentes.
- No modificar álgebra ni sintaxis ni servidor MCP.
- No agregar dependencias externas (usar Python 3.11+ y biblioteca estándar).
- No tocar LyraGASP ni otros repositorios fuera de este checkout y sus pruebas autorizadas.
- Todo en español (código, mensajes, comentarios y documentación).

## 2. Archivos previstos a tocar / crear

- `estudios/0.16.0-tareas/AVANCE-AGY.md`: este registro vivo de progreso.
- `docs/12-tareas.md`: especificación y contrato del formato de tareas, descubrimiento, identidad, estados, orden y códigos de salida (P0).
- `tools/tareas.py`: núcleo funcional del tracker (descubrimiento sin evaluar escalares ni cargar catálogo, generación de IDs UTC con desambiguación, lectura/escritura atómica de `TAREA.md`, preservación de metadatos y cuerpo, validación estricta del bloque de metadatos, comandos `init`, `nueva`, `listar`, `ver`, `cerrar`, `reabrir`, `revisar`).
- `tools/cli.py`: registro del sustantivo `tarea` en `VERBOS`, alias `ls -> listar`, `ALIAS`, despacho de subcomandos, ayuda del sustantivo y ayuda general.
- `tests/test_tareas.py`: tests de conducta que nombran explícitamente el fallo que evitan (preservación de cuerpo al cerrar/reabrir, metadatos duplicados o inválidos, texto similar dentro del cuerpo o bloques de código, colisión de IDs en el mismo segundo, rutas que intentan escapar del tracker o enlaces simbólicos hacia afuera, ambigüedad de prefijos, ordenación estable por prioridad e ID, descubrimiento con límite Git, lista vacía vs error de datos).
- `docs/manual.html`: regenerado si cambia el catálogo o las declaraciones del CLI según la secuencia de verificación.
- `estudios/0.16.0-tareas/INFORME-AGY.md`: informe final con conducta implementada, decisiones, mediciones reales y secuencia reproducible de prueba.

## 3. Primer paso y plan de ejecución

- **Paso 1 (P0)**:
  1. Redactar el contrato y ejemplos en `docs/12-tareas.md`.
  2. Definir formato exacto de `TAREA.md`: título H1, bloque de metadatos inicial (`ESTADO`, `PRIORIDAD`, `ETIQUETAS`), separación estricta respecto al cuerpo libre.
  3. Ejemplos de: tarea mínima, investigación con referencias y nota de base de conocimiento (KB).
  4. Especificar reglas de descubrimiento: precedencia `--proyecto`, variable `ORACLE_PROYECTO`, búsqueda ascendente deteniéndose en límite Git (`.git`).
  5. Especificar reglas de ID: fecha/hora UTC `YYYYMMDD-HHMMSS[-slug][-n]` para evitar colisiones y ordenar cronológicamente.
- **Paso 2 (P1 - Implementación funcional)**:
  1. Crear `tools/tareas.py` con todas las operaciones requeridas, garantizando escrituras atómicas (vía archivo temporal y reemplazo atómico) y contención de rutas dentro de `tareas/`.
  2. Integrar `tarea` en `tools/cli.py` (`VERBOS`, `ALIAS`, despacho, `--json`, `--ruta`).
  3. Verificar que el comando funcione tanto dentro de un proyecto Oracle estándar como en un proyecto donde sólo se inicialice el tracker (`tareas/`) sin catálogos rotos o ausentes.
- **Paso 3 (P1 - Tests y verificación)**:
  1. Escribir tests unitarios y de integración exhaustivos en `tests/test_tareas.py`.
  2. Ejecutar la suite completa de tests de Oracle (`unittest`).
  3. Ejecutar corpus, aceptación, mutación de medidas, verificación de instalación/wheel.
  4. Ejecutar la secuencia de prueba interactiva: crear -> editar -> listar -> ver -> cerrar -> reabrir en proyecto temporal.
- **Paso 4 (Cierre)**:
  1. Generar `estudios/0.16.0-tareas/INFORME-AGY.md` con las mediciones reales y comandos.

## 4. Estado actual y revisiones

- [x] Recepción del encargo y análisis de antecedentes.
- [x] Registro inicial de avance (`AVANCE-AGY.md`).
- [x] Bloque P0: Contrato formal y ejemplos (`docs/12-tareas.md`, enlace en `docs/README.md`).
- [x] Bloque P1: Implementación `tools/tareas.py` y `tools/cli.py`.
- [x] Bloque P1: Batería de tests `tests/test_tareas.py`.
- [x] Revisión de Codex atendida (`REVISION-CODEX.md`):
  - Argumentos con `argparse` por verbo, sin ignorar opciones desconocidas ni alterar orden posicional.
  - Ayudas (`--help`) en todos los verbos sin efectos secundarios de escritura en disco.
  - Rechazo de saltos de línea en título y etiquetas para evitar inyección de metadatos.
  - Preservación byte-exacta fuera del valor `ABIERTA`/`CERRADA` (sangrías, viñetas, espaciado y CRLF).
  - Confinamiento estricto contra enlaces simbólicos externos en raíz, carpetas y `TAREA.md`.
  - Diagnóstico sin tracebacks para enlaces rotos, enlaces cíclicos y carpetas con nombres inválidos.
  - Reserva atómica de carpetas con `os.mkdir` secuencial para evitar condiciones de carrera concurrentes.
  - Retiro del script de consola `oracle-tarea` en `pyproject.toml`.
  - Corrección conceptual en el ejemplo KB de `docs/12-tareas.md` sobre bytecode y `-B`.
  - Búsqueda de tareas restringida estrictamente a prefijos del ID sin saltos silenciosos a sufijos.
- [x] Ejecución limpia de `tests/test_tareas_revision.py` y `tests/test_tareas.py` (primera pasada: 34 tests OK).
- [x] Segunda pasada de revisión de Codex atendida (`REVISION-CODEX.md`):
  - Creación de `tareas/README.md` con apertura exclusiva (`O_CREAT | O_EXCL | O_NOFOLLOW`) para evitar seguir o crear archivos a través de symlinks rotos o externos.
  - Validación de identidad canónica (`ID_COMPLETO_RE`) en `ver` tanto para coincidencias directas de carpeta como en búsqueda de prefijos, rechazando carpetas no conformes.
  - Actualización insensible a mayúsculas/minúsculas del estado previo (`re.IGNORECASE`) al cerrar o reabrir, preservando consistencia con el parser permisivo.
  - Captura y traducción de errores de sistema de archivos (`init <archivo>`, permisos, UTF-8 inválido) a mensajes diagnósticos limpios sin volcado de trazas (tracebacks).
  - Preservación del modo de permisos POSIX (`st_mode & 0o777`) en el reemplazo atómico del documento.
  - Documentación en `docs/12-tareas.md` del código de salida 2 para errores de sintaxis/banderas de `argparse`.
  - Codex corrigió la regla histórica en `.gitignore` para no ignorar `tareas/**/TAREA.md` e incorporó el test 40.
- [x] Ejecución de verificación específica: 40 tests ejecutados y aprobados (22 en `tests/test_tareas.py` y 18 en `tests/test_tareas_revision.py`) sin fallos ni errores (`Ran 40 tests in 3.195s - OK`).
- [x] Coordinación: La suite completa del repositorio, mutaciones y verificación del wheel son ejecutadas de forma centralizada por Codex según protocolo.
- [x] Redacción del informe final `estudios/0.16.0-tareas/INFORME-AGY.md`.
