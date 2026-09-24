# Informe final agy — Encargo P0 y P1 (Oracle 0.16.0: tracker de tareas)

Fecha: 2026-09-11  
Responsable: agy; correcciones editoriales de Codex el 2026-09-12  
Rama/Workspace: `/home/workstation/Dev/oracle`  
Base: distribución 0.15.0 (sin cambio de versión en código)  
Destinatario: Codex / Equipo de Oracle  

---

## 1. Resumen ejecutivo

Se implementaron satisfactoriamente los tramos **P0** (contrato, formato de documento, identidad, descubrimiento y ejemplos de referencia) y **P1** (tracker local funcional con comandos CLI `oracle tarea init`, `nueva`, `listar`/`ls`, `ver`, `cerrar`, `reabrir` y `revisar`) según lo establecido en `vault-kb/estudios/0.16.0-tareas/ENCARGO-AGY.md` y `vault-kb/planes/PLAN-0.16.0-TAREAS.md`.

La implementación fue refinada a través de dos rondas de revisión coordinadas con Codex (`REVISION-CODEX.md`). En su estado final, los 40 tests unitarios y de integración específicos del tracker (21 en `tests/test_tareas.py` y 19 en `tests/test_tareas_revision.py`) se ejecutaron con resultado **100% verde** (`Ran 40 tests in 3.195s - OK`).

Siguiendo las directivas de coordinación:
- No se realizaron commits, push ni alteraciones de etiquetas Git.
- La versión permanece intacta en `0.15.0` (`nucleo/version.py`).
- No se lanzaron subagentes ni dependencias externas (uso exclusivo de biblioteca estándar de Python 3.11+).
- La ejecución de la suite global del repositorio, las pruebas de mutación y la validación del paquete/wheel quedan asignadas a la fase de cierre de Codex.

---

## 2. Conducta implementada y decisiones de arquitectura

### 2.1. Desacoplamiento total del catálogo de medidas
El tracker de tareas se diseñó para operar en directorios de proyecto sin acoplamiento a `catalogos/` ni evaluación de medidas o escalares. La función `resolver_raiz_tracker` resuelve la raíz del proyecto siguiendo la precedencia:
1. Ruta explícita pasada por argumento (`--proyecto <ruta>`).
2. Variable de entorno `$ORACLE_PROYECTO`.
3. Búsqueda ascendente desde el directorio de trabajo (`Path.cwd()`), deteniéndose al alcanzar la frontera de control de versiones (`.git`) o la raíz del sistema de archivos.

Esto permite inicializar y operar el tracker tanto en repositorios Oracle complejos como en carpetas independientes o con catálogos transitoriamente rotos.

### 2.2. Identidad canónica UTC y reserva concurrente de carpetas
- **Formato canónico**: `YYYYMMDD-HHMMSS[-slug][-n]`.
- Los identificadores se generan a partir de la fecha y hora UTC del sistema.
- **Reserva atómica (`crear_carpeta_tarea_atomica`)**: Para evitar condiciones de carrera entre procesos concurrentes (verificadas con tests multi-hilo), se utiliza `os.mkdir` atómico en un bucle secuencial (`candidato`, `candidato-1`, `candidato-2`, ...) capturando `FileExistsError`. No se emplean verificaciones previas con `exists()` ni nombres basados en PIDs que pudieran ser reutilizados o predecibles.

### 2.3. Seguridad y confinamiento de rutas
Se incorporaron comprobaciones de rutas y enlaces preexistentes. Estas comprobaciones no constituyen una garantía frente a otro proceso que sustituya rutas durante una operación:
- Rechazo inmediato de secuencias de escape (`..`, `/`, `\`, `\x00`) en identificadores o rutas (`validar_seguridad_id`).
- Confinamiento estricto (`asegurar_confinamiento` y `asegurar_confinamiento_archivo`): toda ruta resuelta mediante `resolve(strict=True)` debe ser descendiente estricta de la raíz `tareas/` resuelta (`relative_to`).
- Se auditan enlaces simbólicos en la raíz de tareas, en subcarpetas de tareas y en el archivo `TAREA.md`. Los enlaces simbólicos que apunten fuera del tracker son rechazados con código de error 1.
- Detección y diagnóstico claro para enlaces rotos y cíclicos, evitando caídas por excepciones no controladas.
- Apertura y creación exclusiva de archivos auxiliares (`tareas/README.md`) mediante `os.open` con banderas `os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW` para impedir que un enlace simbólico preexistente o roto permita escribir fuera del árbol del tracker.

### 2.4. Formato de documento y preservación byte-exacta
El archivo `TAREA.md` se compone de:
1. Encabezado H1 (`# Título`).
2. Bloque de metadatos estricto inmediatamente posterior (`- CLAVE: VALOR` contiguos). Campos requeridos: `ESTADO` (`ABIERTA` o `CERRADA`), `PRIORIDAD` (entero). Opcionales: `ETIQUETAS` (separadas por comas) y campos adicionales personalizados.
3. Línea en blanco separadora.
4. Cuerpo Markdown libre.

**Garantías de integridad y preservación**:
- **Aislamiento**: Las líneas dentro del cuerpo libre o dentro de bloques de código cercados (```` ``` ````) que contengan texto semejante a metadatos (como `- ESTADO: ABIERTA`) no interfieren con el parser de cabecera.
- **Inyección prevenida**: Los comandos de creación rechazan títulos o etiquetas con saltos de línea (`\n`, `\r`), impidiendo la inyección arbitraria de claves de metadatos.
- **Modificación quirúrgica (`actualizar_estado_tarea`)**: Al cerrar o reabrir, el archivo no se reescribe línea por línea. Se lee la secuencia de bytes en crudo, se ubica la posición exacta del valor del estado dentro de la línea de metadatos correspondiente (mediante coincidencia insensible a mayúsculas/minúsculas para tolerar estados normalizados) y se reemplaza exclusivamente el rango de bytes del estado objetivo (`ABIERTA` o `CERRADA`). Esto preserva:
  - Finales de línea originales (CRLF en Windows o LF en Linux).
  - Sangrías, espaciados alrededor de los dos puntos y tipo de viñeta (`-` o `*`).
  - Campos personalizados desconocidos.
  - La totalidad del cuerpo libre, imágenes y anexos.
  - El modo de permisos POSIX del archivo (`st_mode & 0o777`).
- **Escritura atómica**: La actualización se escribe a un archivo temporal contiguo con creación exclusiva (`tempfile.NamedTemporaryFile` en el mismo directorio) sincronizado con `os.fsync`, restaurando permisos antes de aplicar `os.replace`.

### 2.5. Interfaz de línea de comandos e integración en CLI
- Sustantivo `tarea` integrado en `tools/cli.py` (`VERBOS` y `ALIAS` con `ls -> listar`).
- Cada subcomando (`init`, `nueva`, `listar`, `ver`, `cerrar`, `reabrir`, `revisar`) utiliza una instancia dedicada de `argparse.ArgumentParser` configurada para no capturar escrituras en llamadas a ayuda (`--help` / `-h`) y para rechazar opciones no reconocidas.
- Soporte para ubicar opciones antes o después de argumentos posicionales (e.g. `oracle tarea nueva --etiqueta bug "Título"`).
- Se documentaron formalmente los códigos de retorno en `docs/12-tareas.md`:
  - **Código 0**: Éxito y operaciones sin cambios (idempotencia en cerrar/reabrir, listados vacíos, `--help`).
  - **Código 1**: Errores de dominio (tarea no encontrada, prefijo ambiguo, registro corrupto, infracción de confinamiento, errores del sistema de archivos).
  - **Código 2**: Errores de sintaxis en argumentos evaluados por `argparse` (opciones no reconocidas, valores faltantes).
- Se retiró el ejecutable independiente redundante `oracle-tarea` en `pyproject.toml`, unificando toda la invocación bajo `oracle tarea`.

---

## 3. Resoluciones aplicadas durante las revisiones de Codex

En coordinación con `vault-kb/estudios/0.16.0-tareas/REVISION-CODEX.md`, se abordaron las observaciones en dos etapas:

### Primera pasada (12 observaciones, verificadas inicialmente con 13 tests)
1. **Ayudas sin escritura**: Consulta de `--help` en `init` y demás verbos muestra la documentación y sale con código 0 sin tocar el disco.
2. **Rechazo de argumentos desconocidos**: Opciones como `listar --inventada` fallan con código 2 de `argparse`.
3. **Desacoplamiento de argumentos en `nueva`**: Opciones antes o después de posicionales se analizan inequívocamente con `argparse`; se eliminó la colisión cuando el valor de una etiqueta coincidía con el título.
4. **Preservación byte-exacta**: Reemplazo de estado localizado por offset de bytes, preservando terminaciones CRLF y formato exacto.
5. **Comprobaciones de confinamiento**: Verificación de escape en carpetas, archivos y raíz en todos los comandos del ciclo de vida.
6. **Validación contra inyección**: Prohibición de saltos de línea en títulos y etiquetas.
7. **Identidad canónica**: Exigencia del formato `YYYYMMDD-HHMMSS` en auditoría de directorios.
8. **Temporales seguros**: Reemplazo atómico con `tempfile` exclusivo en el mismo directorio.
9. **Reserva concurrente**: Manejo de concurrencia con `os.mkdir` secuencial.
10. **Eliminación de `oracle-tarea`**: Entrada retirada de `pyproject.toml`.
11. **Corrección de ejemplo KB**: Corrección de la explicación sobre el aislamiento de bytecode con `-B`.
12. **Búsqueda por prefijos**: Restricción estricta a prefijos sin desvíos silenciosos a sufijos.

### Segunda pasada (5 observaciones resueltas)
1. **README simbólico roto**: Apertura exclusiva con `O_CREAT | O_EXCL | O_NOFOLLOW` para impedir crear o escribir archivos a través de symlinks en `init`.
2. **Validación canónica en `ver`**: Se valida `ID_COMPLETO_RE` también ante coincidencias directas de nombre de carpeta, rechazando carpetas no conformes.
3. **Estados normalizados en minúsculas**: Búsqueda insensible a mayúsculas/minúsculas para el estado anterior al cerrar o reabrir.
4. **Traducción de errores de sistema de archivos**: Rutas a archivos pasadas a `init`, errores de permisos o datos con codificación no UTF-8 se diagnostican limpiamente sin tracebacks.
5. **Preservación de permisos y código 2**: Conservación de `st_mode & 0o777` en el reemplazo atómico y documentación del código 2 de `argparse` en `docs/12-tareas.md`.
6. *(Acción de Codex)*: Ajuste en `.gitignore` para permitir `tareas/**/TAREA.md` y adición del test 40 en `tests/test_tareas_revision.py`.

---

## 4. Inventario de archivos modificados y creados

| Archivo | Acción | Descripción |
|---|---|---|
| `docs/12-tareas.md` | Creado | Especificación técnica formal (P0), anatomía de `TAREA.md`, ciclo de vida, descubrimiento, identidad, ejemplos de especificación y códigos de retorno (0, 1 y 2). |
| `docs/README.md` | Modificado | Enlace al nuevo documento 12 en el índice de documentación. |
| `tools/tareas.py` | Creado | Módulo principal del tracker: lógica de dominio, parseo, actualización byte-exacta, confinamiento y subcomandos CLI. |
| `tools/cli.py` | Modificado | Integración de `tarea` en `VERBOS`, `ALIAS` (`ls`), despacho pre-catálogo y ayuda general. |
| `docs/manual.html` | Modificado | Regenerado tras actualizar las declaraciones de CLI. |
| `pyproject.toml` | Sin cambio neto | Se descartó el script de consola adicional; la interfaz es `oracle tarea`. |
| `tests/test_tareas.py` | Creado | 21 pruebas unitarias y de integración de agy con nombres que explicitan el fallo que previenen. |
| `vault-kb/estudios/0.16.0-tareas/AVANCE-AGY.md` | Modificado | Bitácora de seguimiento actualizada en cada hito y revisión. |
| `vault-kb/estudios/0.16.0-tareas/INFORME-AGY.md` | Creado | Este informe final de entrega. |

*(Nota: `tests/test_tareas_revision.py`, `.gitignore` y `tools/verificar_instalacion.py` fueron administrados y actualizados por Codex).*

---

## 5. Mediciones reales de ejecución

### 5.1. Ejecución de la suite específica de tareas
Comando ejecutado:
```bash
python3 -B -m unittest tests/test_tareas.py tests/test_tareas_revision.py -v
```

Resultado obtenido:
```text
Ran 40 tests in 3.195s

OK
```

Detalle de cobertura de las pruebas ejecutadas:
- **`tests/test_tareas.py` (21 tests)**:
  - `TestDescubrimientoYContrato`: inicialización, independencia de catálogos, precedencia de búsqueda y límite Git.
  - `TestListarVerYRevisar`: orden por prioridad descendente e ID ascendente, alias `ls`, flag `--ruta`, desambiguación de prefijos, lista vacía vs error de datos, auditoría `revisar`.
  - `TestMetadatosYPreservacion`: validación estricta de estado y prioridad entera, rechazo de duplicados, idempotencia al cerrar/reabrir, preservación byte-exacta del cuerpo y campos desconocidos.
  - `TestSeguridadYConfinamiento`: rechazo de caracteres de escape (`..`, `/`), rechazo de enlaces simbólicos hacia afuera del árbol de tareas.
- **`tests/test_tareas_revision.py` (19 tests)**:
  - Argumentos y CLI: ayudas sin escritura, opciones antes del título, rechazo de opciones desconocidas (código 2), argumentos iguales sin pérdida.
  - Confinamiento y enlaces: raíz simbólica, carpeta simbólica externa, archivo simbólico externo, enlaces rotos, README simbólico en `init`.
  - Concurrencia y solidez: creaciones concurrentes simultáneas (8 hilos), nombres de carpeta no canónicos, rechazo de inyecciones por saltos de línea, archivos UTF-8 corruptos sin traceback, destino archivo en `init`.
  - Integridad de datos: preservación de bytes ajenos al valor, actualización con estado previo en minúsculas, conservación de permisos POSIX (0640), regla de `.gitignore` para tareas.

### 5.2. Declaración de alcance de verificación
En estricto cumplimiento del protocolo acordado:
- Agy verificó y confirmó en verde los **40 tests de tareas**.
- La ejecución de la suite completa de Oracle, la verificación del paquete instalado (`python3 -B tools/verificar_instalacion.py`), el empaquetado del wheel y la mutación de métricas corresponden a la revisión final conducida por Codex.

---

## 6. Secuencia reproducible de prueba para Codex

Para verificar manualmente el flujo completo en un entorno temporal aislado sin alterar datos reales del repositorio:

```bash
# 1. Crear directorio temporal para el experimento
EXP_DIR=$(mktemp -d /tmp/oracle-tracker-test.XXXXXX)
cd "$EXP_DIR"

# 2. Inicializar el tracker de tareas (debe crear tareas/ y tareas/README.md)
python3 -B /home/workstation/Dev/oracle/tools/cli.py tarea init .
ls -la tareas/

# 3. Crear una nueva tarea con metadatos
CREACION=$(python3 -B /home/workstation/Dev/oracle/tools/cli.py tarea nueva \
    "Verificar sincronizacion de eventos" \
    --etiqueta bug \
    --etiqueta sensor \
    --prioridad 80 \
    --sufijo sinc-evento \
    --json)
echo "$CREACION"
ID_TAREA=$(echo "$CREACION" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
RUTA_TAREA=$(echo "$CREACION" | python3 -c "import sys, json; print(json.load(sys.stdin)['ruta'])")

# 4. Editar manualmente TAREA.md agregando notas, viñetas personalizadas y bloques de código
cat << 'EOF' >> "$RUTA_TAREA"

## Notas adicionales del ingeniero

- ASIGNADO: operador
* NOTA: Este campo usa asterisco como viñeta
Línea con sangría y espacios particulares.

```markdown
Ejemplo dentro de bloque cercado:
- ESTADO: ABIERTA
No debe alterar la cabecera real.
```
EOF

# 5. Listar las tareas abiertas (formato texto y JSON)
python3 -B /home/workstation/Dev/oracle/tools/cli.py tarea listar
python3 -B /home/workstation/Dev/oracle/tools/cli.py tarea ls --json

# 6. Inspeccionar la tarea (humano, ruta para editor y JSON)
python3 -B /home/workstation/Dev/oracle/tools/cli.py tarea ver "$ID_TAREA"
python3 -B /home/workstation/Dev/oracle/tools/cli.py tarea ver "$ID_TAREA" --ruta
python3 -B /home/workstation/Dev/oracle/tools/cli.py tarea ver "$ID_TAREA" --json

# 7. Cerrar la tarea (comprobar que sólo cambia ESTADO y se preserva el resto)
python3 -B /home/workstation/Dev/oracle/tools/cli.py tarea cerrar "$ID_TAREA"
grep "ESTADO:" "$RUTA_TAREA"
tail -n 12 "$RUTA_TAREA"

# 8. Reabrir la tarea y auditar el directorio
python3 -B /home/workstation/Dev/oracle/tools/cli.py tarea reabrir "$ID_TAREA"
python3 -B /home/workstation/Dev/oracle/tools/cli.py tarea revisar

# 9. Limpieza del directorio temporal
rm -rf "$EXP_DIR"
```

---

## 7. Delimitación y tramos pendientes

Agy entrega P0 y P1 para revisión de Codex. El cierre y la evidencia posterior se registran por separado; este informe no declara publicada la distribución 0.16.0.

Los siguientes tramos estipulados en `vault-kb/planes/PLAN-0.16.0-TAREAS.md` quedan reservados para fases subsiguientes:
- **P2**: Captura de notas, URLs y adjuntos; búsqueda, referencias, resumen y diagnóstico de cobertura en Git.
- **P3**: Sensor determinista de hechos de seguimiento y medidas opcionales de integridad, usando el lenguaje existente.
- **P4**: Uso propio con pendientes reales, tutorial, verificación completa y preparación del corte 0.16.0.
