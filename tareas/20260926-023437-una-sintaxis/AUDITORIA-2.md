# Auditoría adversarial de la sintaxis de escritura (Segunda ronda)

2026-09-26. Alcance: este checkout de Oracle en `/work`. No se modificó código ni se realizaron commits. Se ejecutaron todas las pruebas sobre este checkout. El CLI se corrió como `python3 tools/cli.py` y los módulos del núcleo se importaron desde `/work`. Cuando un comando externo no estuvo disponible en el sistema (por ejemplo, `rg` devolvió `bash: line 1: rg: command not found`), se declaró expresamente y la búsqueda equivalente se ejecutó con `find`, `grep` o scripts directos de Python.

---

## 1. Veredicto de la segunda auditoría

Las tres tareas intermedias (`macro-invocacion-unica`, `lectores-heredados`, `ensenanza-una-sintaxis`) **cerraron exitosamente los hallazgos críticos de la primera auditoría**:
1. **MCP**: Se cerró la entrada JSON de medidas; `_ESQUEMA_MEDIDA` ahora exige `{"formato": {"const": "oracle"}}`, `_medida_en_memoria` rechaza JSON con error explícito `MEDIDA_INVALIDA`, y `docs/mcp-contrato.md` enseña exclusivamente `oracle`.
2. **`oracle convertir`**: Ya no traduce de superficie a JSON; rechaza `.oracle` y `.caso` con error `esperaba una medida .json para convertir a superficie`, funcionando exclusivamente como herramienta de migración hacia la superficie.
3. **`oracle contexto`**: La sección `## CON QUÉ SE ESCRIBE` enseña únicamente superficie (`p.x`, `a + b`, `p`, `x`) y eliminó los accesores JSON de AST (`["campo", ...]`) y las funciones aritméticas (`mas/menos/por`).
4. **README y guías**: `README.md` y `docs/03-escribir-una-medida.md` presentan `.oracle`, `.caso` y `.relacion` como las únicas formas de escritura de autoría, relegando JSON a intercambio y migración.
5. **Invocación de macros**: La forma de argumentos (`relacion/alias/predicado/...`) fue eliminada y ahora arroja `ErrorSintaxis` con la reescritura sugerida; el impresor genera consistentemente la forma de plantilla (`de/donde/umbral/...`).
6. **Aritmética funcional y accesores**: `mas(a, b)`, `menos(a, b)`, `por(a, b)` y `col(p)` son ahora errores de sintaxis en el lector de superficie con mensajes correctivos directos («escribí a + b», «escribí p en vez de col(p)»).
7. **Relación en `.oracle`**: Cargar una relación JSON en un archivo `.oracle` ahora arroja `RelacionMalDeclarada: una relación se escribe en .relacion`.
8. **Plantilla sensor-prosa**: La receta de `ejemplo/sensor-prosa/README.md` referencia correctamente `013-vacio-favorable.caso`.

**Sin embargo, la auditoría en contra detectó hallazgos abiertos y segundas formas NUEVAS:**
- **Remanente editorial en documentación**: `docs/tutorial-practico.md:684` aún enseña textualmente: *«el catálogo carga `.oracle` igual que `.json`, así que no hay paso de traducción»*, y comentarios internos en `tools/medida.py:59` y `nucleo/macro.py:288-290` conservan la formulación histórica.
- **Segundas formas sintácticas nuevas comprobadas**:
  - `agrupar:` admite `agregado` antes de `clave` e intercalaciones arbitrarias; el impresor las normaliza forzando todas las `clave` primero y luego los `agregado`.
  - Múltiples filtros `donde` encadenados en el pipeline (`donde ... / donde ...`) conviven con el operador conjuntivo `y` (`donde ... y ...`), con árboles AST distintos pero idéntica evaluación.
  - En `.relacion`, los nombres de rama en `variantes por` aceptan identificadores entrecomillados (`"inicio":`) o sin comillas (`inicio:`), imprimiéndose siempre sin comillas.
  - En evidencia `.caso` con `fila {...}`, `clave(...)` se acepta tanto con punto y coma (`clave(t);`) como sin él (`clave(t)`).
  - La primera línea de un archivo `.oracle` admite opcionalmente `sintaxis <versión>`, coexistiendo archivos con y sin versión.
  - En `origen:` de `.caso`, los campos se aceptan en cualquier orden.
  - `ambito` es opcional en `medida`, pero obligatorio en invocación de macros salvo `sin_declarar`.
  - Notación científica (`1e-3`) es aceptada en expresiones por el tokenizador numérico y reformateada a decimal por el impresor.
- **Formatos duales persistentes para lectura de intercambio**:
  - Los cargadores `cargar_fuente_medida`, `cargar_fuente_caso` y `cargar_fuente_relacion` siguen aceptando archivos `.json` en disco (decisión explícita de arquitectura para intercambio y migración).
  - La evidencia dentro de `.caso` sigue aceptando tabla y escape `fila {...}` (reconocido como necesario para filas heterogéneas).

---

## 2. Re-ejecución de los 17 puntos de la auditoría anterior

### Punto 1. Tarea de auditoría
- **Comando**: `python3 tools/cli.py tarea ver una-sintaxis`
- **Salida recortada**:
  ```
  ID:        20260926-023437-una-sintaxis
  Título:    Una sola sintaxis para escribir Oracle: la superficie; el JSON canónico queda como formato interno
  Estado:    ABIERTA
  Prioridad: 90
  Etiquetas: oracle, sintaxis, una-sintaxis
  ```

### Punto 2. Localización de archivos del núcleo
- **Comando**: `rg --files nucleo | rg 'sintaxis|caso|relacion|macro|proyecto'`
  - **Incidencia de ejecución**: `bash: line 1: rg: command not found`. `rg` no está instalado en el entorno.
  - **Comando alternativo ejecutado**: `find nucleo -type f | grep -E 'sintaxis|caso|relacion|macro|proyecto'`
- **Salida recortada**:
  ```
  nucleo/sintaxis.py
  nucleo/relacion.py
  nucleo/proyecto.py
  nucleo/macro.py
  nucleo/caso.py
  nucleo/macros/peor.oracle
  nucleo/macros/ninguno.oracle
  ...
  ```

### Punto 3. Sonda sobre superficie de medida y expresiones
- **Comando**: Sonda Python ejecutada con `nucleo.sintaxis.leer` y `imprimir` sobre variantes de `medida demo.prueba:`:
  ```bash
  python3 - <<'PY'
  from nucleo.sintaxis import leer, imprimir, ErrorSintaxis
  base = """medida demo.prueba:
      de pieza p
      resumen contar(1)
      umbral <= 0 segun contrato porque "razon"
      alcance "limite"
  """
  variantes = {
      "base": base,
      "MAYUS": base.replace("medida demo.prueba:", "MEDIDA demo.prueba:"),
      "umbral porque sin segun": base.replace('umbral <= 0 segun contrato porque "razon"', 'umbral <= 0 porque "razon"'),
      "umbral segun sin porque": base.replace('umbral <= 0 segun contrato porque "razon"', 'umbral <= 0 segun contrato'),
      "umbral porque antes de segun": base.replace('umbral <= 0 segun contrato porque "razon"', 'umbral <= 0 porque "razon" segun contrato'),
      "requiere lista": base.replace('    alcance "limite"', '    requiere pieza, modulo\n    alcance "limite"'),
      "requiere repetido": base.replace('    alcance "limite"', '    requiere pieza\n    requiere modulo\n    alcance "limite"'),
      "requiere despues alcance": base + '    requiere pieza\n',
      "funcion mas": base.replace("resumen contar(1)", "resumen contar(mas(1, 2))"),
      "infijo mas": base.replace("resumen contar(1)", "resumen contar(1 + 2)"),
      "col acceso": base.replace("resumen contar(1)", "resumen contar(col(p))"),
  }
  for n, c in variantes.items():
      try:
          print(f"{n}: OK -> {imprimir(leer(c)).splitlines()[-2:]}")
      except Exception as e:
          print(f"{n}: ERROR {type(e).__name__}: {str(e)[:80]}")
  PY
  ```
- **Salida recortada**:
  ```
  base: OK -> ['    umbral <= 0 segun contrato porque "razon"', '    alcance "limite"']
  MAYUS: ERROR ErrorSintaxis: línea 1, columna 1: se esperaba encabezado «medida|macro declarada <id>:»; llegó
  umbral porque sin segun: OK -> ['    umbral <= 0 porque "razon"', '    alcance "limite"']
  umbral segun sin porque: OK -> ['    umbral <= 0 segun contrato', '    alcance "limite"']
  umbral porque antes de segun: ERROR ErrorSintaxis: línea 4, columna 32: se esperaba fin de línea; llegó 'segun'
  requiere lista: OK -> ['    requiere pieza, modulo', '    alcance "limite"']
  requiere repetido: OK -> ['    requiere pieza, modulo', '    alcance "limite"']
  requiere despues alcance: ERROR ErrorSintaxis: línea 6, columna 5: se esperaba fin de medida; llegó 'requiere pieza'
  funcion mas: ERROR ErrorSintaxis: línea 3, columna 20: escribí a + b
  infijo mas: OK -> ['    umbral <= 0 segun contrato porque "razon"', '    alcance "limite"']
  col acceso: ERROR ErrorSintaxis: línea 3, columna 20: escribí p en vez de col(p)
  ```
  *(También se probaron `menos(1, 2)` arrojando `escribí a - b` y `por(1, 2)` arrojando `escribí a * b`).*
- **Estado**: `mas`, `menos`, `por` y `col(p)` están **CERRADAS**.

### Punto 4. Sonda Medida y MCP
- **Comando**:
  ```bash
  python3 - <<'PY'
  import json
  from nucleo.sintaxis import leer
  from nucleo.medida import Medida
  from nucleo.macro import macros_base
  import tools.mcp as mcp

  base = """medida demo.prueba:
      de pieza p
      resumen contar(1)
      umbral <= 0 segun contrato porque "razon"
      alcance "limite"
  """
  print("tools.mcp._ESQUEMA_MEDIDA formato:", mcp._ESQUEMA_MEDIDA["oneOf"][1]["properties"]["formato"])
  macros = macros_base()
  m_ora = mcp._medida_en_memoria({"texto": base, "formato": "oracle"}, macros)
  print("MCP oracle OK:", m_ora.id)
  try:
      mcp._medida_en_memoria({"texto": json.dumps(leer(base)), "formato": "json"}, macros)
  except Exception as e:
      print("MCP json ERROR:", type(e).__name__, str(e)[:90])
  PY
  ```
- **Salida recortada**:
  ```
  tools.mcp._ESQUEMA_MEDIDA formato: {'const': 'oracle'}
  MCP oracle OK: demo.prueba
  MCP json ERROR: ErrorHerramienta MEDIDA_INVALIDA — el texto Oracle de la medida no se entiende: línea 1, columna 1: se esperaba encabezado «medida|macro declarada <id>:»
  ```
- **Estado**: **CERRADA**. MCP ya no admite `formato: json`.

### Punto 5. Sonda sobre superficie de casos
- **Comando**: Sonda sobre `corpus/meta/049-donde-agrego-filas.caso` probando tabla, escape `fila {...}`, mayúsculas, orden de campos y carga JSON:
  ```bash
  python3 - <<'PY'
  from pathlib import Path
  import tempfile, json
  from nucleo.caso import leer, imprimir, cargar_fuente_caso

  texto = Path("corpus/meta/049-donde-agrego-filas.caso").read_text(encoding="utf-8")
  c1 = leer(texto)
  print("tabla OK, igual=", c1 == leer(imprimir(c1)), "impresor_fila=", "fila {" in imprimir(c1))

  # Sustitución por filas heterogéneas
  hetero = """caso 999-demo:
      fecha: "2026-08-24"
      origen:
          repo: "Segtem/oracle"
          commit: "c81a87c"
      procedencia: observada
      titulo: "demo"
      etiqueta: falso_verde
      sintoma:
          sintoma
      como_se_detecto: mutacion
      medida: meta.donde_nunca_agrega_filas
      evidencia:
          paso:
              fila {"a": 1}
              fila {"b": 2}
      leccion:
          leccion
  """
  ch = leer(hetero)
  print("heterogeneo OK, impresor_fila=", "fila {" in imprimir(ch))

  try:
      leer(texto.replace("caso 049-donde-agrego-filas:", "CASO 049-donde-agrego-filas:"))
  except Exception as e:
      print("MAYUS ERROR:", str(e)[:60])

  with tempfile.TemporaryDirectory() as td:
      pj = Path(td) / "049.json"
      pj.write_text(json.dumps(c1), encoding="utf-8")
      print("cargar_fuente_caso JSON OK id=", cargar_fuente_caso(pj)["id"])
  PY
  ```
- **Salida recortada**:
  ```
  tabla OK, igual= True impresor_fila= False
  heterogeneo OK, impresor_fila= True
  MAYUS ERROR: línea 1, columna 1: se esperaba encabezado «caso <id>:»
  cargar_fuente_caso JSON OK id= 049-donde-agrego-filas
  ```
- **Estado**: **ABIERTA / DOCUMENTADA**. `imprimir` produce `fila {...}` ante datos heterogéneos y tabla en datos regulares. El cargador JSON sigue operativo para intercambio histórico.

### Punto 6. Sonda de relaciones y extensión `.oracle`
- **Comando**:
  ```bash
  python3 - <<'PY'
  import tempfile, json
  from pathlib import Path
  from nucleo.relacion import leer, imprimir, cargar_fuente_relacion

  rel_texto = "relacion pieza:\n    x: entero sin_unidad\n    alcance \"x\"\n"
  ast = leer(rel_texto)
  with tempfile.TemporaryDirectory() as td:
      p_json = Path(td) / "x.json"
      p_oracle = Path(td) / "x.oracle"
      p_rel = Path(td) / "x.relacion"
      p_json.write_text(json.dumps(ast), encoding="utf-8")
      p_oracle.write_text(json.dumps(ast), encoding="utf-8")
      p_rel.write_text(rel_texto, encoding="utf-8")
      print("x.relacion OK:", cargar_fuente_relacion(p_rel)[1])
      print("x.json OK:", cargar_fuente_relacion(p_json)[1])
      try:
          cargar_fuente_relacion(p_oracle)
      except Exception as e:
          print("x.oracle ERROR:", type(e).__name__, str(e)[:70])
  PY
  ```
- **Salida recortada**:
  ```
  x.relacion OK: pieza
  x.json OK: pieza
  x.oracle ERROR: RelacionMalDeclarada /tmp/.../x.oracle: una relación se escribe en .relacion
  ```
- **Estado**: **CERRADA**. El archivo `.oracle` con contenido de relación JSON ahora falla explícitamente.

### Punto 7. Invocación de macro: plantilla vs argumentos
- **Comando**:
  ```bash
  python3 - <<'PY'
  from nucleo.sintaxis import leer, imprimir
  from nucleo.macro import macros_base

  m_base = macros_base()
  plantilla = """ninguno demo.x:
      de pieza p
      donde p.x == 1
      umbral <= 0 segun contrato porque "razon"
      ambito sin_declarar
      alcance "limite"
  """
  argumentos = """ninguno demo.x:
      relacion pieza
      alias p
      predicado p.x == 1
      porque "razon"
      segun contrato
      ambito sin_declarar
      alcance "limite"
  """
  ast_p = leer(plantilla, macros=m_base)
  print("plantilla OK; impresor:\n" + imprimir(ast_p, macros=m_base).strip())
  try:
      leer(argumentos, macros=m_base)
  except Exception as e:
      print("argumentos ERROR:\n" + str(e)[:110])
  PY
  ```
- **Salida recortada**:
  ```
  plantilla OK; impresor:
  ninguno demo.x:
      de pieza p
      donde p.x == 1
      umbral <= 0 segun contrato porque "razon"
      ambito sin_declarar
      alcance "limite"
  argumentos ERROR:
  línea 2, columna 5: la invocación de macro se escribe con las cláusulas de su plantilla:
  ninguno demo.x:
      de pie
  ```
- **Estado**: **CERRADA**. La forma de argumentos se rechaza con error de sintaxis y el impresor emite la forma de plantilla.

### Punto 8. Cargadores de archivos temporales
- **Comando**: Verificado en Punto 4, Punto 5 y Punto 6:
  - `cargar_fuente_medida(json)`: OK (intercambio)
  - `cargar_fuente_caso(json)`: OK (intercambio)
  - `cargar_fuente_relacion(json)`: OK (intercambio)
  - `cargar_fuente_relacion(oracle)`: ERROR (`RelacionMalDeclarada`)
- **Estado**: Archivos `.oracle` para relaciones **CERRADA**. Archivos `.json` de intercambio conservados deliberadamente.

### Punto 9. Ayuda del CLI y manuales
- **Comandos**:
  - `python3 tools/cli.py --help | grep convertir`
  - `python3 tools/cli.py manual aritmetica | head -15`
  - `python3 tools/cli.py manual macros | head -10`
- **Salidas recortadas**:
  - `--help`: `oracle convertir <archivo> Convierte medidas JSON a superficie`
  - `manual aritmetica`: `ARITMETICA — aritmética infija de expresiones: a + b, a - b, a * b, (a + b) * c, -1` (no enseña funciones `mas/menos/por`).
  - `manual macros`: Enseña las 6 macros base.
- **Estado**: **CERRADA**.

### Punto 10. `oracle convertir`
- **Comando**:
  ```bash
  python3 - <<'PY'
  import tempfile, subprocess
  from pathlib import Path
  with tempfile.TemporaryDirectory() as td:
      p = Path(td)
      (p / "catalogos").mkdir(); (p / "corpus").mkdir()
      m_ora = p / "catalogos/demo.prueba.oracle"; m_ora.write_text("medida demo.prueba:\n    de pieza p\n    resumen contar(1)\n    umbral <= 0 segun contrato porque \"r\"\n    alcance \"a\"\n")
      m_json = p / "catalogos/demo.prueba.json"; m_json.write_text('["medida", "demo.prueba", ["desde", ["de", "pieza", "p"]], ["resumen", "contar", 1], ["umbral", "<=", 0, "r", "contrato"], ["alcance", "a"]]')
      c_caso = p / "corpus/001-demo.caso"; c_caso.write_text("caso 001-demo:\n")

      r1 = subprocess.run(["python3", "tools/cli.py", "convertir", str(m_ora), "--proyecto", td], capture_output=True, text=True)
      print("convertir .oracle rc:", r1.returncode, "stdout:", r1.stdout.strip())
      r2 = subprocess.run(["python3", "tools/cli.py", "convertir", str(m_json), "--proyecto", td], capture_output=True, text=True)
      print("convertir .json rc:", r2.returncode, "head stdout:", r2.stdout.splitlines()[0])
      r3 = subprocess.run(["python3", "tools/cli.py", "convertir", str(c_caso), "--proyecto", td], capture_output=True, text=True)
      print("convertir .caso rc:", r3.returncode, "stdout:", r3.stdout.strip())
  PY
  ```
- **Salida recortada**:
  ```
  convertir .oracle rc: 1 stdout: ✗ /tmp/.../catalogos/demo.prueba.oracle: esperaba una medida .json para convertir a superficie
  convertir .json rc: 0 head stdout: medida demo.prueba:
  convertir .caso rc: 1 stdout: ✗ /tmp/.../corpus/001-demo.caso: esperaba una medida .json para convertir a superficie
  ```
- **Estado**: **CERRADA**. `convertir` solo admite `.json` de entrada y genera superficie. No imprime JSON.

### Punto 11. Generadores CLI (`init`, `nueva`, `caso nuevo`, `relaciones --escribir`)
- **Comando**: Probados en entorno temporal.
- **Salida recortada**:
  - `oracle init`: crea `oracle.json`
  - `oracle nueva demo.prueba`: crea `catalogos/demo/demo.prueba.oracle` con plantilla `ninguno`.
  - `oracle caso nuevo demo/001-prueba`: crea `corpus/demo/001-prueba.caso`.
  - `oracle relaciones --escribir`: genera borrador `relaciones-por-revisar/auditoria_prueba.relacion`.
- **Estado**: Toda creación genera superficie `.oracle`, `.caso` y `.relacion`.

### Punto 12. `oracle contexto --compacto`
- **Comando**: `python3 tools/cli.py contexto --compacto | grep -A 8 "## CON QUÉ SE ESCRIBE"`
- **Salida recortada**:
  ```
  ## CON QUÉ SE ESCRIBE
    operadores:  agrupar · de · desde · donde · resumen · sin · unir
    comparadores: == != < <= > >=
    lógicos:      y  o  no
    agregados:    contar max min promedio suma
    accesores:    p.x (campo) · p (fila del alias) · x (columna agrupada)
    aritmética:   a + b · a - b · a * b · (a + b) * c
    escalares:
      cerca/2
      contiene/2
  ```
- **Estado**: **CERRADA**. Eliminados los accesores JSON y las funciones `mas/menos/por`.

### Punto 13. Revisión de documentos y guías
- **Comando**: Inspección de `docs/mcp-contrato.md`, `README.md`, `docs/03-escribir-una-medida.md`, `ejemplo/sensor-prosa/README.md`, `docs/tutorial-practico.md`.
- **Salida recortada**:
  - `docs/mcp-contrato.md:1076`: `{"texto": ..., "formato": "oracle"} carga una medida enteramente en memoria.` (JSON eliminado).
  - `README.md:375`: `Las medidas, los casos y las relaciones se escriben en superficie (.oracle, .caso, .relacion). Oracle lee JSON como formato de intercambio y para migrar fuentes anteriores.`
  - `docs/03-escribir-una-medida.md:98`: `Escribí medidas en .oracle, casos en .caso y relaciones en .relacion. Oracle también lee JSON como formato de intercambio...`
  - `ejemplo/sensor-prosa/README.md:18`: Referencia actualizada a `013-vacio-favorable.caso`.
  - **HALLAZGO NUEVO**: `docs/tutorial-practico.md:684`: `Y la guardás tal cual: el catálogo carga .oracle igual que .json, así que no hay paso de traducción.`
- **Estado**: Hallazgos anteriores **CERRADOS**. Nuevo hallazgo en `docs/tutorial-practico.md:684` **ABIERTA**.

### Punto 14. LSP y MCP
- **Comando**: Inspección de `tools/lsp.py` y `tools/mcp.py`.
- **Salida recortada**:
  - `tools/lsp.py:83-86`: LSP solo diagnostica `.caso` y `.oracle`.
  - `tools/mcp.py:67, 848`: MCP sólo admite formato `oracle`.
- **Estado**: **CERRADA**.

### Punto 15. Censo de extensiones de archivos
- **Comando**:
  ```bash
  python3 - <<'PY'
  from collections import Counter
  from pathlib import Path
  dirs = ["catalogos", "corpus", "relaciones", "perfiles", "ejemplo", "nucleo/macros"]
  archivos = [f for d in dirs for f in Path(d).rglob("*") if f.is_file() and f.suffix in {".json", ".oracle", ".caso", ".relacion"}]
  print(dict(Counter(f.suffix[1:] for f in archivos)))
  PY
  ```
- **Salida recortada**:
  `{'oracle': 96, 'caso': 321, 'relacion': 23, 'json': 14}`
  Los 14 archivos `.json` son exclusivamente `oracle.json` de proyectos, fixtures de hechos y metadatos.
- **Estado**: No hay medidas, casos ni relaciones de autoría en `.json`.

### Punto 16. Configuración `oracle.json`
- **Comando**:
  ```bash
  python3 - <<'PY'
  import tempfile, json
  from pathlib import Path
  from nucleo.proyecto import Proyecto, configuracion, ProyectoInvalido
  with tempfile.TemporaryDirectory() as td:
      p = Path(td)
      print("ausente:", configuracion(Proyecto(p)))
      oj = p / "oracle.json"
      oj.write_text('{"esquema": "oracle.proyecto/v1"}')
      print("basico:", configuracion(Proyecto(p)))
      oj.write_text('{"ESQUEMA": "oracle.proyecto/v1"}')
      try:
          configuracion(Proyecto(p))
      except Exception as e:
          print("mayus ERROR:", type(e).__name__, str(e)[:60])
  PY
  ```
- **Salida recortada**:
  ```
  ausente: ConfiguracionProyecto(perfiles=(), catalogo_base=False, bibliotecas=(), sombra=())
  basico: ConfiguracionProyecto(perfiles=(), catalogo_base=False, bibliotecas=(), sombra=())
  mayus ERROR: ProyectoInvalido `oracle.json` debe declarar esquema 'oracle.proyecto/v1'
  ```
- **Estado**: Única sintaxis de configuración JSON validada.

### Punto 17. Medida meta y tests editoriales
- **Comandos**:
  - `cat catalogos/meta/meta.se_escribe_en_superficie.oracle`
  - `python3 -m unittest tests/test_ensenanza_una_sintaxis.py`
- **Salida recortada**:
  ```
  ...
  Ran 3 tests in 0.035s
  OK
  ```
- **Estado**: **CERRADA**. Los tests automatizan la custodia de lo enseñado en CLI, MCP y docs.

---

## 3. Búsqueda y ejecución de segundas formas NUEVAS

Se exploraron y ejecutaron sondas adversariales en puntos no testeados en la primera auditoría:

### 1. `agrupar:` orden de `clave` y `agregado`
- **Prueba**:
  ```bash
  python3 - <<'PY'
  from nucleo.sintaxis import leer, imprimir
  base = """medida demo.prueba:
      de pieza p
      agrupar:
          agregado a = contar(1)
          clave c = p.id
      resumen contar(1)
      umbral <= 0 segun contrato porque "r"
      alcance "a"
  """
  ast = leer(base)
  print("agregado antes de clave OK:", ast[2])
  print("impresor reordena:\n" + imprimir(ast).strip())
  PY
  ```
- **Salida recortada**:
  ```
  agregado antes de clave OK: ['desde', ['de', 'pieza', 'p'], ['agrupar', [['c', ['campo', 'p', 'id']]], [['a', 'contar', 1]]]]
  impresor reordena:
  medida demo.prueba:
      de pieza p
      agrupar:
          clave c = p.id
          agregado a = contar(1)
  ...
  ```
- **Hallazgo**: `nucleo.sintaxis._leer_medida` (líneas 1238-1246) admite `clave` y `agregado` en cualquier orden relativo o intercalados. Sin embargo, el impresor (`_lineas_agrupar`) siempre emite todas las `clave` primero y luego los `agregado`.
- **Estado**: **NUEVA / ABIERTA**.

### 2. Múltiples cláusulas `donde` encadenadas vs operador conjuntivo `y`
- **Prueba**:
  ```bash
  python3 - <<'PY'
  from nucleo.sintaxis import leer, imprimir
  from nucleo.medida import Medida
  m_dos_donde = """medida demo.prueba:
      de pieza p
      donde p.x == 1
      donde p.y == 2
      resumen contar(1)
      umbral <= 0 segun contrato porque "r"
      alcance "a"
  """
  m_y = """medida demo.prueba:
      de pieza p
      donde p.x == 1 y p.y == 2
      resumen contar(1)
      umbral <= 0 segun contrato porque "r"
      alcance "a"
  """
  print("dos donde AST:", leer(m_dos_donde)[2])
  print("y AST:", leer(m_y)[2])
  v1 = Medida.de_datos(leer(m_dos_donde)).evaluar({"pieza": [{"x": 1, "y": 2}]})
  v2 = Medida.de_datos(leer(m_y)).evaluar({"pieza": [{"x": 1, "y": 2}]})
  print("evaluacion identica:", v1.ok == v2.ok and v1.valor == v2.valor)
  PY
  ```
- **Salida recortada**:
  ```
  dos donde AST: ['desde', ['de', 'pieza', 'p'], ['donde', ['==', ['campo', 'p', 'x'], 1]], ['donde', ['==', ['campo', 'p', 'y'], 2]]]
  y AST: ['desde', ['de', 'pieza', 'p'], ['donde', ['y', ['==', ['campo', 'p', 'x'], 1], ['==', ['campo', 'p', 'y'], 2]]]]
  evaluacion identica: True
  ```
- **Hallazgo**: La gramática permite encadenar N líneas `donde` consecutivas como pasos de tubería (`['donde', ...]`), produciendo el mismo filtrado lógico que un solo `donde` con operadores `y`. El impresor preserva ambas estructuras.
- **Estado**: **NUEVA / ABIERTA**.

### 3. Ramas de `variantes por` en `.relacion` (identificador entrecomillado vs sin comillas)
- **Prueba**:
  ```bash
  python3 - <<'PY'
  from nucleo.relacion import leer, imprimir
  rel_sin = """relacion evento:
      tipo: texto
      variantes por tipo:
          inicio:
              hora: texto
      alcance "ve eventos"
  """
  rel_con = """relacion evento:
      tipo: texto
      variantes por tipo:
          "inicio":
              hora: texto
      alcance "ve eventos"
  """
  print("arboles identicos:", leer(rel_sin) == leer(rel_con))
  print("impresor de ambos:\n" + imprimir(leer(rel_con)).strip())
  PY
  ```
- **Salida recortada**:
  ```
  arboles identicos: True
  impresor de ambos:
  relacion evento:
      tipo: texto
      variantes por tipo:
          inicio:
              hora: texto
      alcance "ve eventos"
  ```
- **Hallazgo**: `nucleo/relacion.py:365-372` parsea el valor de la variante aceptando tanto nombres sin comillas (`inicio:`) como cadenas JSON entre comillas (`"inicio":`). El impresor emite sin comillas para identificadores.
- **Estado**: **NUEVA / ABIERTA**.

### 4. Encabezado de versión de superficie (`sintaxis 0.8`) opcional
- **Prueba**:
  ```bash
  python3 - <<'PY'
  from nucleo.sintaxis import leer_con_mapa
  base = "medida demo.prueba:\n    de pieza p\n    resumen contar(1)\n    umbral <= 0 segun contrato porque \"r\"\n    alcance \"a\"\n"
  l1 = leer_con_mapa(base)
  l2 = leer_con_mapa("sintaxis 0.8\n" + base)
  print("sin sintaxis version:", l1.version, "con sintaxis version:", l2.version)
  PY
  ```
- **Salida recortada**:
  `sin sintaxis version: None con sintaxis version: 0.8`
- **Hallazgo**: La sintaxis de autoría `.oracle` admite opcionalmente como primera línea `sintaxis <version>`. Es una forma alternativa válida en la superficie.
- **Estado**: **NUEVA / ABIERTA**.

### 5. `clave(...)` en evidencia `.caso` con o sin punto y coma
- **Prueba**:
  ```bash
  python3 - <<'PY'
  from nucleo.caso import leer
  c_puntoycoma = """caso 001-demo:
      fecha: "2026-08-24"
      origen:
          repo: "Segtem/oracle"
          commit: "c81a87c"
      titulo: "demo"
      etiqueta: falso_verde
      sintoma:
          sintoma
      como_se_detecto: mutacion
      medida: meta.donde_nunca_agrega_filas
      evidencia:
          paso: clave(t);
              fila {"t": 0}
      leccion:
          leccion
  """
  c_sin = c_puntoycoma.replace("paso: clave(t);", "paso: clave(t)")
  print("con ';' OK:", leer(c_puntoycoma)["evidencia"])
  print("sin ';' OK:", leer(c_sin)["evidencia"])
  PY
  ```
- **Salida recortada**:
  ```
  con ';' OK: {'paso': [['clave', ['t']], {'t': 0}]}
  sin ';' OK: {'paso': [['clave', ['t']], {'t': 0}]}
  ```
- **Hallazgo**: Al usar la forma de escape `fila {...}`, la cabecera `relacion: clave(...)` es aceptada con `;` final o sin él.
- **Estado**: **NUEVA / ABIERTA**.

### 6. Orden de claves en el bloque `origen:` de `.caso`
- **Prueba**:
  ```bash
  python3 - <<'PY'
  from nucleo.caso import leer
  c_base = """caso 001-demo:
      fecha: "2026-08-24"
      origen:
          repo: "Segtem/oracle"
          commit: "c81a87c"
      titulo: "demo"
      etiqueta: falso_verde
      sintoma:
          sintoma
      como_se_detecto: mutacion
      medida: meta.donde_nunca_agrega_filas
      evidencia:
          paso: t
              0
      leccion:
          leccion
  """
  c_rev = c_base.replace('repo: "Segtem/oracle"\n        commit: "c81a87c"',
                         'commit: "c81a87c"\n        repo: "Segtem/oracle"')
  print("orden original origen:", leer(c_base)["origen"])
  print("orden invertido origen:", leer(c_rev)["origen"])
  PY
  ```
- **Salida recortada**:
  ```
  orden original origen: {'repo': 'Segtem/oracle', 'commit': 'c81a87c'}
  orden invertido origen: {'commit': 'c81a87c', 'repo': 'Segtem/oracle'}
  ```
- **Hallazgo**: A diferencia de los campos principales del caso (cuyo orden es rígido), las claves dentro de `origen:` admiten cualquier orden y claves adicionales, reflejándose en el diccionario.
- **Estado**: **NUEVA / ABIERTA**.

### 7. Remanente editorial en `docs/tutorial-practico.md:684`
- **Prueba**:
  ```bash
  python3 -c 'from pathlib import Path; lines = Path("docs/tutorial-practico.md").read_text().splitlines(); print(lines[683])'
  ```
- **Salida**:
  `Y la guardás tal cual: el catálogo carga .oracle igual que .json, así que no hay paso de traducción.`
- **Hallazgo**: La tarea `ensenanza-una-sintaxis` auditó y corrigió `README.md`, `docs/03-escribir-una-medida.md` y `docs/mcp-contrato.md`, pero omitió `docs/tutorial-practico.md:684`, que sigue enseñando al lector que el catálogo carga `.oracle` igual que `.json`.
- **Estado**: **NUEVA / ABIERTA**.

---

## 4. Tabla de inventario

| Forma | Estado | Evidencia |
|---|---|---|
| **Medida en `.json` (entrada MCP)** | **cerrada** | `_ESQUEMA_MEDIDA` restringe a `{"formato": {"const": "oracle"}}`; enviar `formato: json` a `_medida_en_memoria` levanta `ErrorHerramienta MEDIDA_INVALIDA`. |
| **`oracle convertir` produciendo JSON** | **cerrada** | `tools/cli.py:cmd_convertir` falla con `rc 1` si se le pasa `.oracle` o `.caso`: `esperaba una medida .json para convertir a superficie`. Solo traduce de JSON hacia superficie. |
| **Accesores AST JSON en `oracle contexto`** | **cerrada** | `tools/cli.py contexto --compacto` emite `accesores: p.x (campo) · p (fila del alias) · x (columna agrupada)`. `["campo", ...]` fue suprimido. |
| **Aritmética funcional en `oracle contexto`** | **cerrada** | `## CON QUÉ SE ESCRIBE` en `contexto` sólo muestra `a + b · a - b · a * b · (a + b) * c`. Las entradas `mas/2, menos/2, por/2` fueron eliminadas de la lista de escalares. |
| **Presentación dual en README.md** | **cerrada** | `README.md:375-376` declara explícitamente: «Las medidas, los casos y las relaciones se escriben en superficie (.oracle, .caso, .relacion). Oracle lee JSON como formato de intercambio y para migrar fuentes anteriores». |
| **Presentación dual en `docs/03`** | **cerrada** | `docs/03-escribir-una-medida.md:98` declara `.oracle`, `.caso` y `.relacion` como formatos de autoría y relega JSON a intercambio. |
| **Invocación de macro por argumentos** | **cerrada** | `nucleo.sintaxis.leer` sobre cuerpo con `relacion/alias/predicado/...` arroja `ErrorSintaxis: la invocación de macro se escribe con las cláusulas de su plantilla`. |
| **Producción de macro por impresor** | **cerrada** | `nucleo.sintaxis.imprimir` genera la forma plantilla (`de/donde/umbral/ambito/alcance`). |
| **Llamadas a `mas()`, `menos()`, `por()`** | **cerrada** | `nucleo.sintaxis._primario` levanta `ErrorSintaxis: escribí a + b`, `escribí a - b`, `escribí a * b`. |
| **Llamada a `col(p)`** | **cerrada** | `nucleo.sintaxis._primario` levanta `ErrorSintaxis: escribí p en vez de col(p)`. |
| **Relación JSON en archivo `.oracle`** | **cerrada** | `nucleo.relacion.cargar_fuente_relacion` levanta `RelacionMalDeclarada: una relación se escribe en .relacion`. |
| **Ruta a `.json` en plantilla sensor-prosa** | **cerrada** | `ejemplo/sensor-prosa/README.md:18` lee `corpus/prosa/013-vacio-favorable.caso` usando `nucleo.caso.leer`. |
| **Evidencia en `.caso`: escape `fila {...}`** | **abierta** | `nucleo/caso.py:195` produce `fila {...}` cuando las filas son heterogéneas o los campos no forman tabla; `_Parser` acepta tanto tabla como `fila {...}`. Reconocido y documentado en manual y especificación como escape por heterogeneidad de datos. |
| **Lector de medidas `.json` en disco** | **abierta** | `cargar_fuente_medida` acepta archivos `.json` para compatibilidad e intercambio. Conservado por decisión arquitectónica. |
| **Lector de casos `.json` en disco** | **abierta** | `cargar_fuente_caso` acepta archivos `.json` para intercambio histórico. |
| **Lector de relaciones `.json` en disco** | **abierta** | `cargar_fuente_relacion` acepta archivos `.json` para intercambio. |
| **`defmacro` en archivo `.json`** | **abierta** | `nucleo/macro.py:291` mantiene `EXTENSIONES_DE_MACRO = (".json", ".oracle")`. |
| **Umbral `segun` y `porque` opcionales** | **abierta** | `_leer_umbral` acepta omitir `segun` o `porque`, pero rechaza `porque` antes de `segun`. |
| **`requiere` en una línea vs múltiples** | **abierta** | `_leer_medida` agrupa múltiples líneas `requiere` consecutivas; el impresor las colapsa en una sola línea para nombres simples. |
| **`agrupar:` orden relativo de `clave` y `agregado`** | **nueva** | `_leer_medida` acepta `agregado` antes de `clave` o intercalados; `imprimir` normaliza colocando siempre `clave` antes que `agregado`. |
| **`donde` encadenado vs operador `y`** | **nueva** | La superficie permite escribir múltiples líneas `donde` en la tubería o un solo `donde` con `y`; evalúan idéntico y el impresor preserva ambas. |
| **Variantes entrecomilladas en `.relacion`** | **nueva** | `_lineas_relacion` y `leer` en `relacion.py` aceptan ramas entrecomilladas (`"inicio":`) o sin comillas (`inicio:`); el impresor emite sin comillas para identificadores. |
| **Encabezado `sintaxis <versión>` opcional** | **nueva** | La primera línea de `.oracle` admite `sintaxis 0.8` opcionalmente sin alterar la validez del archivo. |
| **`clave(...)` con o sin `;` en escape de `.caso`** | **nueva** | `_parsear_cabecera_relacion` en `nucleo/caso.py` acepta `paso: clave(t);` y `paso: clave(t)` cuando va seguido de `fila {...}`. |
| **Orden de campos en `origen:` de `.caso`** | **nueva** | `_leer_origen` acepta cualquier orden de claves (`repo`, `commit`, etc.). |
| **`ambito` opcional en `medida`** | **nueva** | `ambito` es opcional en `medida` (ausente da `ambito: sin_declarar`), mientras que en macros plantilla es obligatorio declararlo. |
| **Notación científica en literales numéricos** | **nueva** | `NUMERO_RE` acepta `1e-3` en expresiones; `imprimir` formatea a notación decimal fija (`0.001`). |
| **Espaciado en encabezado `medida <id>:`** | **nueva** | `ENCABEZADO_RE` acepta múltiples espacios en `medida   demo.prueba:`; el impresor normaliza a un único espacio. |
| **Enseñanza dual en `docs/tutorial-practico.md:684`** | **nueva** | Línea 684 afirma erróneamente: *«el catálogo carga `.oracle` igual que `.json`, así que no hay paso de traducción»*. |
