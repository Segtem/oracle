# Avance 0.19.0 — Consultas de Tareas (TQL en Español)

**Fecha:** 2026-09-15  
**Autor:** AGY (Antigravity)  
**Revisa y verifica:** Claude (Claude Code)  
**Encargo:** `estudios/0.19.0-tql/ENCARGO-AGY.md`  
**Plan base:** `PLAN-0.19.0-TQL.md`  
**Tarea asociada:** `20260915-023750-tql`  

---

## 1. Representación Interna Elegida

Para el motor de consultas en `tools/tareas_consulta.py`, se opta por un **Árbol de Sintaxis Abstracta (AST)** fuertemente tipado en lugar de una pila o bytecode:

### 1.1. Justificación del diseño por AST
1. **Comprobación de tipos en compilación**:
   A diferencia de `tatr` (que aplaza la resolución de tipos a la evaluación de cada tarea en una máquina de pila y produce errores de ejecución tardíos), Oracle 0.19.0 exige verificación de tipos estática e inmediata durante `compilar(texto)`. En un AST, cada nodo calcula y valida su `.tipo` (`"booleano"` o `"entero"`) al instanciarse o en el paso de análisis sintáctico descendente recursivo.
2. **Diagnóstico con posición precisa**:
   Cada nodo y token retiene el índice de carácter inicial (`columna: int`, 0-indexed respecto al texto de la consulta). Esto permite que las fallas de tipo infieran la posición exacta del operador o primaria culpable, alineando el puntero `^` en caracteres Unicode (no bytes UTF-8).
3. **Explicación determinista (`--explicar`)**:
   El recorrido del AST genera una representación canónica entre paréntesis o prefija unívoca y predecible, desacoplada del orden de tareas o del estado del disco.

### 1.2. Nodos del AST y tipado

| Nodo | Tipo resultante | Tipos requeridos en operandos | Semántica de evaluación |
|---|---|---|---|
| `NodoCualquiera` | `booleano` | N/A | Siempre `True`. |
| `NodoEtiquetada` | `booleano` | N/A | `len(tarea.etiquetas) > 0`. |
| `NodoEtiqueta(etiqueta)` | `booleano` | N/A | `any(e.lower() == etiqueta.lower() for e in tarea.etiquetas)`. |
| `NodoId(id_esperado)` | `booleano` | N/A | `tarea.id == id_esperado` (coincidencia exacta, no prefijo). |
| `NodoPrioridad` | `entero` | N/A | `tarea.prioridad` (entero de la tarea). |
| `NodoEntero(valor)` | `entero` | N/A | Constante entera `valor`. |
| `NodoNo(operando)` | `booleano` | `operando: booleano` | `not operando.evaluar(tarea)`. |
| `NodoComparacion(izq, op, der)` | `booleano` | `izq: entero`, `der: entero` | Comparación aritmética (`<`, `<=`, `>`, `>=`, `==`, `!=`). Asociativa a izquierda. |
| `NodoY(izq, der)` | `booleano` | `izq: booleano`, `der: booleano` | Conjunción lógica en cortocircuito (`izq and der`). |
| `NodoO(izq, der)` | `booleano` | `izq: booleano`, `der: booleano` | Disyunción lógica en cortocircuito (`izq or der`). |

Una consulta sólo es válida si su nodo raíz es de tipo `booleano`. Un nodo raíz de tipo `entero` (como `prioridad` o `42` en soledad) es rechazado al compilar.

### 1.3. Tokenizador y formato de errores
- Tokenizador basado en caracteres: separa por espacios en blanco (`isspace()`), tratando `[` y `]` como delimitadores únicos e independientes.
- La columna se computa por conteo de caracteres Unicode, garantizando compatibilidad con acentos y caracteres no ASCII (`:ñandú`).
- Formato de error estándar de 3 líneas emitido por stderr:
  ```text
  <consulta>
  <espacios>^
  ERROR: <mensaje>
  ```

---

## 2. Plan de Archivos y Responsabilidades

### 2.1. Archivos propiedad de AGY

1. **`tools/tareas_consulta.py`** (Nuevo módulo):
   - Módulo puro de compilación y evaluación de consultas TQL.
   - Definición de `ConsultaInvalida(ValueError)`.
   - Función pública `compilar(texto: str) -> Consulta`.
   - Clase `Consulta` con métodos `evaluar(tarea: Tarea) -> bool` y `explicar() -> str`.

2. **`tools/tareas.py`** (Modificación):
   - `cmd_listar`:
     - Incorporación de argumentos posicionales `consulta` (`nargs="*"`, concatenados con espacio).
     - Banderas `--por-id`, `--invertir`, `--explicar`.
     - Compilación anticipada de la consulta; si falla, diagnóstico a stderr y salida código 2 sin leer tracker.
     - Si `--explicar`, imprime explicación de consulta compilada y finaliza con código 0 sin exigir tracker.
     - Ordenamiento por defecto (`-prioridad, id`), con `--por-id` (ID descendente, más nuevas primero) y `--invertir` (invierte el orden final).
   - `cmd_desetiquetar`:
     - Bandera `--consulta` (`-c`), excluyente con IDs posicionales explícitos (código 2).
     - Validación y compilación de consulta antes de cualquier mutación; si falla, código 2 sin escribir archivos.
   - `cmd_init`:
     - Bandera `--sin-readme`, omite la creación de `README.md` conservando la creación de `tareas/`.
   - `ayuda()`:
     - Actualización de textos de ayuda para `init`, `listar`, `desetiquetar` y `referencias`.

3. **`tools/tareas_contexto.py`** (Modificación):
   - `cmd_referencias`:
     - Argumento `id` ahora opcional (`nargs="?"`).
     - Si se omite, inspecciona `Path.cwd()`: si está dentro de `tareas/<id>` o un subdirectorio suyo, adopta ese ID canónico.
     - Si se omite y está fuera de una tarea, termina con código 2 y mensaje explícito a stderr sin volcar traceback.

4. **`tools/cli.py`** (Modificación):
   - Sincronización de ayuda contextual en `ayuda_tarea()`.

5. **`docs/12-tareas.md`** (Modificación):
   - Documentación completa del lenguaje de consultas TQL en español: gramática formal, tipos, precedencia, ejemplos y códigos de error.
   - Banderas nuevas de `listar` (`--por-id`, `--invertir`, `--explicar`), `desetiquetar --consulta`, `referencias` sin ID, e `init --sin-readme`.
   - Actualización de la sección «Diferencias con tatr» (TQL como diferencia de vocabulario y no de alcance; verificación estática de tipos; etiquetas case-insensitive).

6. **`tests/test_tareas_consulta.py`** (Nuevo archivo de pruebas):
   - Suite exhaustiva unitaria y de CLI para todas las capacidades y casos borde del encargo.

7. **`estudios/0.19.0-tql/INFORME-AGY.md`** (Nuevo informe de cierre):
   - Documentación técnica final sin afirmar pruebas no ejecutadas.

### 2.2. Archivos bajo custodia de Claude (No tocar)
- `tests/test_tareas_consulta_revision.py`
- `README.md`, `NOTAS-DE-RELEASE.md`, `ESPECIFICACION.md`
- `nucleo/`, `ejemplo/`, `tools/verificar_instalacion.py`, `tools/mutar_codigo.py`, `.github/`, `docs/manual.html`
- Tests existentes previos.
