# Informe 0.19.0 — Consultas de Tareas en Español (TQL)

**Fecha:** 2026-09-15  
**Autor:** AGY (Antigravity)  
**Revisa y verifica:** Claude (Claude Code)  
**Encargo:** `estudios/0.19.0-tql/ENCARGO-AGY.md`  
**Plan base:** `PLAN-0.19.0-TQL.md`  
**Avance previo:** `estudios/0.19.0-tql/AVANCE-AGY.md`  

---

## 1. Declaración de Cumplimiento de Restricciones

- **Herramientas empleadas**: exclusivamente herramientas de lectura y edición de archivos (`view_file`, `write_to_file`, `replace_file_content`, `grep_search`, `list_dir`, `find_by_name`).
- **Restricciones respetadas estrictamente**:
  - NO se ejecutó ningún comando shell (`run_command` no fue invocado).
  - NO se ejecutaron suites de prueba ni herramientas de mutación por parte de AGY (la verificación y ejecución queda delegada íntegramente a Claude).
  - NO se invocaron subagentes ni herramientas de red.
  - NO se realizaron operaciones de Git ni commits.
  - NO se modificaron archivos fuera de la propiedad asignada a AGY (`tests/test_tareas_consulta_revision.py`, `README.md`, `NOTAS-DE-RELEASE.md`, `ESPECIFICACION.md`, `nucleo/`, `ejemplo/`, `tools/verificar_instalacion.py`, `tools/mutar_codigo.py`, `.github/`, `docs/manual.html` permanecen intactos).

---

## 2. El Lenguaje de Consultas (`tools/tareas_consulta.py`)

Se implementó el módulo puro `tools/tareas_consulta.py` sin dependencias de disco ni conocimiento de `sys.argv`, operando directamente sobre texto y objetos `tareas.Tarea`.

### 2.1. Representación Interna Elegida
Se optó por un **Árbol de Sintaxis Abstracta (AST)** tipado estáticamente:
- Clases base de nodos: `ASTNodo`, `ASTNodoBooleano`, `ASTNodoEntero`.
- Nodos booleanos:
  - `Etiqueta(nombre: str)`: comprueba pertenencia de etiqueta insensible a mayúsculas/minúsculas.
  - `Cualquiera()`: evalúa siempre a `True`.
  - `Etiquetada()`: evalúa a `True` si la tarea posee al menos una etiqueta.
  - `IdExacto(id_esperado: str)`: evalúa a `True` únicamente ante coincidencia exacta de ID canónico.
  - `Negacion(exp: ASTNodoBooleano)`: negación lógica `no`.
  - `ConectorLogico(operador: str, izq: ASTNodoBooleano, der: ASTNodoBooleano)`: conjunción `y` y disyunción `o`.
  - `Comparacion(operador: str, izq: ASTNodoEntero, der: ASTNodoEntero)`: comparaciones relacionales entre enteros (`<`, `<=`, `>`, `>=`, `==`, `!=`).
- Nodos enteros:
  - `Prioridad()`: evalúa al entero `tarea.prioridad`.
  - `EnteroLiteral(valor: int)`: constante entera con signo opcional.

### 2.2. Análisis Léxico y Columna Precisa
- `Tokenizador` procesa caracteres individuales manteniendo la columna basada en **caracteres Unicode**, no en bytes. Caracteres multibyte (como `ñ` o acentos en `:ñandú`) no desfasaron la posición del puntero de error.
- Normalización automática de nombres de etiqueta a minúsculas (`:Bug` normaliza a `:bug`), garantizando coincidencias case-insensitive en tiempo de evaluación.
- Reconocimiento de enteros con signo (`+42`, `-10`, `0`), palabras reservadas, comparadores verbales y simbólicos, e identificadores exactos según `ID_COMPLETO_RE`.

### 2.3. Gramática y Precedencia
Implementada mediante un parser descendente recursivo según la especificación:
1. Primarias: `:etiqueta`, `cualquiera`, `etiquetada`, `prioridad`, enteros, `id`, `[ consulta ]`, `no <primaria>`.
2. Comparaciones: `menor`, `hasta`, `mayor`, `desde`, `igual`, `distinto` (y variantes simbólicas).
3. Conjunción: `y` (asociativa a izquierda, precede a `o`).
4. Disyunción: `o` (asociativa a izquierda).

### 2.4. Chequeo Estático de Tipos al Compilar
A diferencia de evaluadores puramente dinámicos, la función `compilar(texto)` valida la consistencia de tipos en tiempo de compilación:
- Se rechaza con `ConsultaInvalida` cualquier consulta cuya raíz no sea un `ASTNodoBooleano` (ej. `prioridad` o `50` solos son rechazados antes de evaluar cualquier tarea).
- Los conectores `o`, `y` y `no` exigen operandos de tipo booleano.
- Los comparadores exigen operandos de tipo entero.

### 2.5. Diagnóstico Visual en 3 Líneas
La excepción `ConsultaInvalida` formatea el error exactamente como la especificación requiere:
```text
<consulta original>
<espacios>^
ERROR: <mensaje explicativo en español>
```

### 2.6. Inspección con `--explicar`
El método `Consulta.explicar()` produce una salida estructurada determinista con la lista de tokens identificados y la visualización jerárquica del AST compilado.

---

## 3. Integración en `tools/tareas.py`

### 3.1. `cmd_listar`
- **Argumento posicional**: `parser.add_argument("consulta", nargs="*", default=[])`. Las palabras se unen con espacios (`" ".join(parsed.consulta)`). Consulta vacía compila a `Cualquiera()`.
- **Compilación previa**: la consulta se compila antes de resolver o auditar el tracker. Ante un fallo sintáctico o de tipos, se emite el diagnóstico a `stderr` y se finaliza inmediatamente con **código 2** sin tocar disco.
- **Banderas de orden**:
  - `--por-id`: ordena las tareas exclusivamente por identificador en orden descendente (las más recientes primero).
  - `--invertir`: invierte el orden final resultante del listado.
  - La combinación `--por-id --invertir` produce orden por ID ascendente.
- **Opción `--explicar`**: compila la consulta, emite tokens y AST a `stdout` y finaliza con **código 0** sin exigir la existencia de `tareas/` ni listar tareas.

### 3.2. `cmd_desetiquetar` con `--consulta`
- Nueva opción `--consulta` / `-c`.
- **Exclusión mutua**: si se proporcionan identificadores explícitos junto con `--consulta`, se invoca `parser.error("no se pueden combinar identificadores explícitos con --consulta")`, finalizando con **código 2**.
- **Compilación anticipada**: si `--consulta` es inválida, se imprime el diagnóstico a `stderr` y se retorna **código 2** sin auditar ni modificar archivos.
- **Filtrado por estado y consulta**: evalúa la consulta sobre las tareas candidatas respetando el filtro de estado (por defecto solo abiertas, con `--cerradas` solo cerradas, o `--todas`).
- Preserva la auditoría previa, escrituras atómicas, formato de salida `ruta:línea` e idempotencia.

### 3.3. `cmd_init` con `--sin-readme`
- Nueva opción `--sin-readme`.
- Si se especifica, se crea el directorio `tareas/` sin generar `README.md`.
- Un tracker inicializado sin `README.md` es plenamente compatible con `oracle tarea revisar` (código 0).

### 3.4. Ayuda del CLI
- Se actualizó el texto emitido por `ayuda()` en `tools/tareas.py` documentando las nuevas opciones en `init`, `listar`, `desetiquetar` y `referencias`.

---

## 4. `referencias` sin Argumento en `tools/tareas_contexto.py`

- Se modificó el argumento `id` en `cmd_referencias` para ser opcional (`nargs="?"`).
- Si se omite:
  1. Se resuelve la raíz del tracker y su directorio `tareas/`.
  2. Se inspecciona si `Path.cwd()` se encuentra dentro de una carpeta de tarea (`raiz_tareas / <id>`) o de cualquiera de sus subdirectorios (ej. `tareas/<id>/notas`).
  3. Si se detecta una tarea válida en la jerarquía ascendente, se utiliza ese ID canónico.
  4. Si `cwd` está en la raíz del proyecto o fuera de cualquier tarea, se emite un error a `stderr` y se finaliza con **código 2** sin volcar trazas de excepción (`Traceback`).

---

## 5. Actualización del CLI Público (`tools/cli.py`)

- Se actualizó la línea de ayuda resumida de `oracle tarea referencias [id]` en `tools/cli.py` para reflejar la opcionalidad del identificador.

---

## 6. Documentación (`docs/12-tareas.md`)

- **Tabla de comandos y opciones**: actualizada con `[consulta]`, `--por-id`, `--invertir`, `--explicar` en `listar`; `--consulta` en `desetiquetar`; `[id]` en `referencias`; y `--sin-readme` en `init`.
- **Sección nueva «Lenguaje de consultas de tareas (TQL)»**:
  - Vocabulario y operadores en español (`o`, `y`, `no`, comparadores, palabras clave).
  - Precedencia y agrupamiento con `[...]`.
  - Sistema de tipos estático y errores en tiempo de compilación.
  - Diagnóstico visual de errores con código 2.
  - Uso de `--explicar`, `--por-id`, `--invertir` y `desetiquetar --consulta`.
- **Actualización de «Diferencias con tatr»**:
  - Se eliminó la afirmación de que Oracle no implementa un lenguaje de consultas propio.
  - Se detalló que TQL pasa a ser una diferencia de vocabulario en español y rigor semántico (verificación estática de tipos en compilación, etiquetas insensibles a mayúsculas/minúsculas).
  - Se incorporó la **tabla exhaustiva de equivalencias** de operadores, palabras clave y comandos entre `tatr` y Oracle TQL.

---

## 7. Batería de Pruebas (`tests/test_tareas_consulta.py`)

Se creó una suite completa con pruebas unitarias y de integración por CLI:
1. `TestTokenizador`:
   - Tokens básicos, palabras clave y comparadores verbales/simbólicos.
   - Etiquetas con caracteres Unicode (`:ñandú`), mayúsculas normalizadas.
   - Enteros con signo (`+42`, `-10`, `0`) e identificadores canónicos de tarea.
   - Conteo de columnas exacto en caracteres Unicode ante errores léxicos.
2. `TestCompiladorYPrecedencia`:
   - Consulta vacía y solo espacios equivalentes a `Cualquiera`.
   - Precedencia de `no` sobre `y` y `o`; precedencia de `y` sobre `o`.
   - Asociatividad a izquierda de conectores lógicos.
   - Alteración de precedencia mediante corchetes `[...]`.
   - Manejo de corchetes desbalanceados o tokens colgantes.
3. `TestChequeoDeTipos`:
   - Rechazo de raíces enteras (`50`, `prioridad`).
   - Rechazo de conectores lógicos sobre enteros (`:bug y 50`, `no 10`).
   - Rechazo de comparadores sobre booleanos (`:bug mayor 50`).
4. `TestEvaluacionEnMemoria`:
   - Coincidencias insensibles a mayúsculas en etiquetas.
   - Evaluación de `etiquetada` y `cualquiera`.
   - Evaluación de comparaciones numéricas de prioridad en todas las variantes.
   - Evaluación de coincidencia por ID exacto.
   - Salida del método `explicar()` (tokens y árbol sintáctico).
5. `TestCliListarConsulta`:
   - Filtrado con TQL en tareas abiertas, con `--cerradas` y con `--todas`.
   - Conjunción de TQL con negación y prioridad.
   - Consulta inválida sale con código 2 sin volcar trazas.
   - `--explicar` sale con código 0 en directorio vacío sin tracker.
   - Ordenamiento con `--por-id`, `--invertir` y su combinación.
6. `TestCliDesetiquetarConsulta`:
   - Desetiquetado masivo condicional según expresión TQL.
   - Incompatibilidad de `--consulta` con IDs explícitos (código 2).
   - Consulta inválida en `desetiquetar` sale con código 2 sin modificar ningún archivo.
7. `TestCliReferenciasCwdEInit`:
   - `referencias` sin ID invocado desde el directorio de la tarea y desde subdirectorios.
   - `referencias` sin ID invocado fuera de una tarea finaliza con código 2 sin trazas.
   - `init --sin-readme` crea el tracker sin `README.md` y audita con código 0 en `revisar`.

---

## 8. Verificación y Archivos Modificados

### Archivos de AGY creados o modificados:
- `tools/tareas_consulta.py` (Creado)
- `tools/tareas.py` (Modificado: `cmd_init`, `cmd_listar`, `cmd_desetiquetar`, `ayuda`)
- `tools/tareas_contexto.py` (Modificado: `cmd_referencias`)
- `tools/cli.py` (Modificado: ayuda de `referencias`)
- `docs/12-tareas.md` (Modificado: tabla de comandos, sección TQL, diferencias con tatr)
- `tests/test_tareas_consulta.py` (Creado)
- `estudios/0.19.0-tql/AVANCE-AGY.md` (Creado)
- `estudios/0.19.0-tql/INFORME-AGY.md` (Creado)

### Archivos de Claude respetados sin modificación:
- `tests/test_tareas_consulta_revision.py`
- `README.md`, `NOTAS-DE-RELEASE.md`, `ESPECIFICACION.md`, `nucleo/`, `ejemplo/`, `tools/verificar_instalacion.py`, `tools/mutar_codigo.py`, `.github/`, `docs/manual.html`.
