# Avance agy — Encargo P2 (Oracle 0.16.0: captura y consultas de contexto)

Fecha: 2026-09-12  
Responsable: agy  
Rama/Workspace: `/home/workstation/Dev/oracle`  
Base: distribución 0.15.0, álgebra 0.6, sintaxis 0.4.

---

## 1. Confirmación de recepción del encargo

Se recibe formalmente el encargo de continuación **P2** establecido en `estudios/0.16.0-tareas/ENCARGO-P2-AGY.md`.
Se asumen los compromisos y delimitaciones:
- Implementación de los nuevos verbos de captura y contexto: `anotar`, `adjuntar`, `buscar`, `referencias`, `resumen`.
- Integración en `tools/tareas.py` del despacho para el verbo `seguimiento` llamando mediante import local a `tools.tareas_git.cmd_seguimiento(argv, args)` (módulo desarrollado en paralelo por Codex).
- Integración en `tools/cli.py` (registro de nuevos verbos en `VERBOS`, ayudas de CLI y despacho sin cargar catálogos).
- Creación de la suite de pruebas de comportamiento `tests/test_tareas_contexto.py` invocando el CLI público sobre proyectos temporales.
- Actualización de la documentación en `docs/12-tareas.md` incorporando la especificación de los comandos P2 y el recorrido/tutorial práctico.
- Respeto estricto del modo de ejecución: sin comandos shell (`run_command`), sin ejecución de tests por agy, sin subagentes, sin cambios de versión y sin commits ni push.
- Entrega final en `estudios/0.16.0-tareas/INFORME-P2-AGY.md` declarando que la ejecución de pruebas queda bajo la custodia de Codex.

---

## 2. Inventario de archivos asignados a agy

- `estudios/0.16.0-tareas/AVANCE-P2-AGY.md`: Bitácora viva de este tramo (creado).
- `tools/tareas_contexto.py`: Módulo núcleo de contexto (nuevo):
  - `cmd_anotar`: Incorporación de notas de texto, URLs validadas y marcas temporales al cuerpo de `TAREA.md` sin descarga remota y con preservación exacta de bytes y permisos.
  - `cmd_adjuntar`: Copia atómica y exclusiva de archivos regulares hacia la carpeta de la tarea (máx. 20 MiB salvo `--permitir-grande`), soporte Unicode y espacios, enlace relativo Markdown con URLs saneadas y reversión limpia ante fallos.
  - `cmd_buscar`: Búsqueda literal case-insensitive en documentos y notas/adjuntos de texto del tracker (límite 2 MiB, extensiones de texto explícitas, reporte de omisiones de binarios/tamaño/enlaces).
  - `cmd_referencias`: Rastreo de menciones textuales del ID canónico en tareas y código fuente del proyecto, excluyendo directorios ignorados (`.git`, `.venv`, `node_modules`, etc.).
  - `cmd_resumen`: Censo y agregación de tareas por estado y etiquetas a partir de registros válidos sin escrituras residuales.
- `tools/tareas.py`: Integración de verbos en el despacho y delegación de `seguimiento` a `tools.tareas_git.cmd_seguimiento`.
- `tools/cli.py`: Declaración de verbos en `VERBOS["tarea"]` y ayuda general.
- `docs/12-tareas.md`: Documentación formal de contratos P2, extensiones soportadas, límites y tutorial completo.
- `tests/test_tareas_contexto.py`: Batería exhaustiva de pruebas unitarias y de integración de contexto (nuevo).
- `estudios/0.16.0-tareas/INFORME-P2-AGY.md`: Informe de entrega final (nuevo).

---

## 3. Plan de trabajo del tramo

1. [x] Recepción del encargo y creación de `AVANCE-P2-AGY.md`.
2. [x] Implementación de `tools/tareas_contexto.py` con todas las validaciones de seguridad, límites y formato (`anotar`, `adjuntar`, `buscar`, `referencias`, `resumen`).
3. [x] Integración en `tools/tareas.py` (`despachar` y `ayuda` para `anotar`, `adjuntar`, `buscar`, `referencias`, `resumen` y `seguimiento` vía import local diferido a `tools.tareas_git`).
4. [x] Integración en `tools/cli.py` (`VERBOS["tarea"]` ampliado y ayuda general actualizada).
5. [x] Implementación de `tests/test_tareas_contexto.py` con 23 pruebas de CLI de comportamiento exhaustivas en temporales.
6. [x] Actualización de `docs/12-tareas.md` con contratos formales, códigos, límites y tutorial completo paso a paso.
7. [x] Redacción inicial de `estudios/0.16.0-tareas/INFORME-P2-AGY.md`.
8. [x] Atención integral de observaciones de revisión de Codex (`REVISION-P2-CODEX.md`):
   - `buscar`: comprobación de archivo regular antes de abrir, omisión limpia de archivos especiales (FIFOs, sockets, dispositivos) sin bloqueos (`O_NONBLOCK`).
   - `buscar`: lectura unificada y acotada con `EXTENSIONES_TEXTO_ADMITIDAS` (incorporando `.oracle` y permitiendo archivos sin extensión).
   - `buscar`: recorrido recursivo de subdirectorios de tareas reportando omisiones de symlinks y repositorios anidados.
   - `referencias`: auditoría previa con `auditar_tareas` (código 1 ante registros corruptos) y manejo de errores en `os.walk` mediante `onerror`.
   - `buscar` y `referencias`: emisión en consola humana de la lista de archivos omitidos incluso ante cero resultados.
   - `anotar`: preservación exacta de sangría y espacios sin `strip()` en texto y marca; captura segura de `OSError` en creación de temporales en la frontera pública.
   - `adjuntar`: control de tamaño acumulado por bloques durante la copia (abortando y revirtiendo si el archivo crece por encima de 20 MiB); escape de barras invertidas antes que corchetes; rechazo explícito de nombres con saltos de línea o caracteres de control.
   - `resumen`: conservación de mayúsculas/minúsculas originales en etiquetas, deduplicando por tarea.
   - `test_tareas_contexto.py`: importación de `shutil` y aportación de argumentos posicionales obligatorios en `test_opciones_desconocidas_devuelven_codigo_2`.
9. [x] Actualización final de `estudios/0.16.0-tareas/INFORME-P2-AGY.md`.
