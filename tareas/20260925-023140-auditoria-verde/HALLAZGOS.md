# Auditoría de falsos verdes en el núcleo y herramientas de Oracle

Esta auditoría releva los caminos del núcleo (`nucleo/`: álgebra, medida, proyecto, sintaxis, caso, relación, macro, marco) y herramientas (`tools/juzgar.py`, `tools/aceptacion.py`) donde una medida, un caso o un proyecto pueden resultar en un veredicto VERDE sin haber medido efectivamente lo que declaran medir.

Cada hallazgo documenta la ubicación exacta (`archivo:línea`), el mecanismo técnico, la entrada concreta que lo dispara y el estado de su cobertura en tests o medidas meta.

---

## 1. `nucleo/medida.py:482-484`: `requiere` simple no usa `separar_clave` y confunde la cabecera con datos

- **Ubicación**: `nucleo/medida.py:480-484` (en contraste con `nucleo/medida.py:486-488` y `nucleo/algebra.py:701,710`).
- **Mecanismo**:
  Al evaluar las precondiciones de evidencia en `Medida.evaluar`, si una entrada de `requiere` es un nombre simple de relación (`isinstance(entrada, str)`), el código comprueba:
  ```python
  if not faltante and not evidencia.get(entrada):
      faltante = entrada
  ```
  A diferencia de la rama condicional (`nucleo/medida.py:487`) donde se llama a `_clave, filas = separar_clave(...)`, la rama simple evalúa la verdad booleana de la lista cruda (`not evidencia.get(entrada)`).
  Si la evidencia contiene una relación con cabecera de clave primaria pero sin filas (por ejemplo `[["clave", ["id"]]]`), la lista tiene longitud 1 (`truthy`). Por tanto, `faltante` permanece vacío (`""`).
  Luego, la ejecución continúa hacia la tubería en `nucleo/medida.py:496`. Al ejecutarse `_de` (`nucleo/algebra.py:701,710`), éste sí llama a `separar_clave`, dejando `filas = []`. La tubería produce 0 testigos. El resumen `contar` devuelve `0`. Frente a un umbral `<= 0`, la comparación `0 <= 0` resulta `True` y la medida concluye en **VERDE** (`ok=True`), en lugar de abortar con veredicto `SIN EVIDENCIA`.
  Esto contradice la intención explícita documentada en `nucleo/medida.py:472-473` («si falta con qué, no hay veredicto que dar. Medir igual produciría el agregado sobre cero filas —que es 0— y un umbral `<= 0` lo leería como verde»).
- **Entrada concreta que lo dispara**:
  ```python
  medida = Medida.de_datos([
      "medida", "ejemplo.vacio",
      ["desde", ["de", "item", "i"]],
      ["resumen", "contar", 1],
      ["umbral", "<=", 0, "razon", "segun"],
      ["requiere", "item"],
      ["alcance", "alcance"],
  ])
  evidencia = {"item": [["clave", ["id"]]]}
  ```
  Produce `Veredicto(ok=True, valor=0)` (FALSO VERDE) en vez de `Veredicto(ok=False, sin_evidencia="item")`.
- **Cobertura**:
  No cubierto. En `tests/test_medida.py:413` sólo se prueba `evidencia = {}` o listas vacías `[]` sin elemento `["clave", ...]`. Ninguna medida meta revisa este caso de borde.

---

## 2. `nucleo/algebra.py:1063-1069`: `_unir_donde_indexado` oculta la incompatibilidad de tipos entre `int` y `str`

- **Ubicación**: `nucleo/algebra.py:1023-1033` y `nucleo/algebra.py:1063-1069` (frente a `nucleo/algebra.py:372-374`).
- **Mecanismo**:
  El optimizador de consultas `_unir_donde_indexado` reemplaza el producto cartesiano ingenuo por una indexación en `dict` cuando detecta `unir` + `donde` de igualdad por clave. Para construir el índice usa `_clave_indexable(valor)`, que valida:
  ```python
  if isinstance(valor, bool) or not isinstance(valor, (int, str)):
      raise ErrorDeAlgebra(...)
  ```
  `_clave_indexable` permite indistintamente enteros y textos.
  Si la tabla izquierda tiene `{"id": 1}` (`int`) y la derecha `{"id": "1"}` (`str`):
  - En el plan ingenuo (`_unir` + `_donde`), para cada par se invoca `comparar("==", 1, "1")`. En `nucleo/algebra.py:372-374` se verifica `if familia_a != familia_b: raise ErrorDeAlgebra("«==» recibió tipos incompatibles: numero y texto")`, levantando excepción.
  - En el plan indexado (activo por defecto), la clave `"1"` se indexa en un diccionario. Al buscar la clave entera `1`, `indice.get(1)` no encuentra coincidencia (en Python `1 in {"1": ...}` es `False`), no levanta error de tipos y devuelve 0 filas (`salida = []`).
  - Al dar 0 filas, un resumen `contar` con umbral `<= 0` evalúa `0 <= 0` y emite **VERDE**.
  El docstring de `_clave_indexable` (`nucleo/algebra.py:1027-1028`) declara: «Un plan que calla un error que el otro plan da no es una optimización: es otra semántica». Sin embargo, la incompatibilidad entre `int` y `str` cruzados no fue contemplada.
- **Entrada concreta que lo dispara**:
  ```python
  tuberia = [
      ["desde", ["unir", ["de", "izq", "a"], ["de", "der", "b"]]],
      ["donde", ["==", ["campo", "a", "id"], ["campo", "b", "id"]]],
  ]
  evidencia = {
      "izq": [{"id": 1}],
      "der": [{"id": "1"}],
  }
  ```
  Con `algebra.forzar_plan_unir(False)` lanza `ErrorDeAlgebra`. Con `algebra.forzar_plan_unir(True)` (por defecto) devuelve `[]` silenciosamente y da verde ante un umbral `<= 0`.
- **Cobertura**:
  No cubierto. En `tests/test_algebra.py:595-603` sólo se comprueban valores inválidos aislados `(None, 1.5, True)`. No se prueba la disparidad de tipos entre lados. La medida meta `meta.unir_materializa_el_producto` sólo vigila el tamaño lógico reportado, no la coherencia semántica entre ambos planes.

---

## 3. `nucleo/medida.py:705-707` y `tools/juzgar.py:340-348`: La sombra perdona veredictos `sin_evidencia`

- **Ubicación**: `nucleo/medida.py:705-707`, `nucleo/medida.py:246-248`, y `tools/juzgar.py:340-348`.
- **Mecanismo**:
  Cuando una medida falla por ausencia de datos requeridos, `Medida.evaluar` devuelve un veredicto con `valor=0`, `ok=False` y `sin_evidencia=faltante` (`nucleo/medida.py:493`).
  En `nucleo/medida.py:246-248` se establece:
  `# Qué relación declarada como necesaria vino vacía. No es un rojo cualquiera: un rojo dice «el mundo está mal», y esto dice «no hay con qué mirar». ok sigue en False porque lo único inaceptable es que salga verde.`
  Sin embargo, en `Informe.perdona(v)` (`nucleo/medida.py:707`):
  ```python
  def perdona(self, v) -> bool:
      return not v.ok and v.id in self.en_sombra and not self.supera_su_cota(v)
  ```
  No se valida que `v.sin_evidencia` esté vacío.
  Al tener `v.valor == 0`, si la medida en sombra tiene declarada una cota `>= 0` (por ejemplo `cota: 5` o `cota: 0`), `supera_su_cota(v)` evalúa `0 > cota` (`False`), por lo que `perdona(v)` devuelve `True`.
  En consecuencia:
  1. `Informe.ok` (`nucleo/medida.py:713`) retorna `True`.
  2. `tools/juzgar.py:348` evalúa `es_aprobado = informe.ok` y finaliza con código de retorno `0` (**VERDE** por sombra perdonada).
  Una falla de extracción de datos del sensor termina siendo perdonada como si fuera una deuda de código dentro de cota, violando la regla de que la ausencia de evidencia nunca debe producir verde.
- **Entrada concreta que lo dispara**:
  Un proyecto con `oracle.json` que declare en sombra una medida con `cota: 5`, y una ejecución de `oracle juzgar` donde la evidencia no incluya la relación requerida por dicha medida.
- **Cobertura**:
  No cubierto. Ningún test evalúa la interacción entre `sin_evidencia` y `en_sombra`. En `tools/aceptacion.py:209-211` el arnés L2 revisa `no_juzgaron` (errores de álgebra), pero en `tools/juzgar.py` el caso `sin_evidencia` en sombra sale con código de salida 0.

---

## 4. `nucleo/macros/ninguno.oracle:4-12`, `peor.oracle:4-12`, `ninguno-par.oracle:4-14`: Macros base sin `requiere`

- **Ubicación**: `nucleo/macros/ninguno.oracle:4-12`, `nucleo/macros/peor.oracle:4-12`, `nucleo/macros/ninguno-par.oracle:4-14` (en contraste con `nucleo/macros/ninguno-requiere.oracle:10`).
- **Mecanismo**:
  Las macros base estándar `ninguno`, `peor` y `ninguno-par` expanden a definiciones de medida que no contienen la directiva `requiere $relacion`.
  Si un sensor falla y emite la relación vacía `{"rel": []}`:
  1. Al no haber `requiere`, `Medida.evaluar` no activa la guarda de evidencia faltante (`faltante = ""`).
  2. La tubería evalúa sobre cero filas.
  3. En `ninguno` y `ninguno-par`, `contar(1)` produce `0`. Con umbral `<= 0`, evalúa `0 <= 0` -> **VERDE**.
  4. En `peor`, `_agregar("max", [])` produce `0` (ver Hallazgo 5). Con umbral `<= $tolerancia` (si tolerancia `>= 0`), evalúa `0 <= tolerancia` -> **VERDE**.
  La medida declara evaluar una relación pero aprueba silenciosamente cuando la relación está vacía.
- **Entrada concreta que lo dispara**:
  Medida expandida con `ninguno`:
  ```
  ninguno(regla.limpieza, items, i, i.sucio == true, "limpio", "contrato", "universal", "alcance")
  ```
  evaluada contra `evidencia = {"items": []}`. Resultado: `Veredicto(ok=True, valor=0)`.
- **Cobertura**:
  El problema motivó la creación de `nucleo/macros/ninguno-requiere.oracle:10`, pero las tres macros base originales permanecen en la biblioteca estándar sin requerir la relación.

---

## 5. `nucleo/algebra.py:591-592`: `_agregar` retorna `0` en agregados extremos y promedios sobre colecciones vacías

- **Ubicación**: `nucleo/algebra.py:580-593`.
- **Mecanismo**:
  La función `_agregar` aplica agregaciones comprobando tipos y finitud. Sin embargo, en las líneas 591-592 establece:
  ```python
  if not valores:
      return 0
  ```
  Para `contar` y `suma`, el elemento neutro 0 tiene sentido matemático. Para `max`, `min` y `promedio`:
  - El promedio de un conjunto vacío no es cero (indefinido / división por cero).
  - El máximo o mínimo de un conjunto vacío no es cero.
  Si una medida calcula `resumen max(...)` o `resumen promedio(...)` sobre una tubería cuyas filas resultan vacías:
  `_agregar` retorna `0` de forma predeterminada. Si la medida tiene umbral `<= 0` (o `<= c` con `c >= 0`), la condición se cumple artificialmente y emite **VERDE**.
- **Entrada concreta que lo dispara**:
  Tubería que produce 0 filas con `["resumen", "max", ["campo", "a", "severidad"]]` y umbral `<= 0`.
  `_agregar("max", [])` retorna `0`, satisfaciendo `<= 0` con veredicto `ok=True`.
- **Cobertura**:
  No cubierto. No existe test que exija error o distinción de ausencia de filas en `max([])` o `promedio([])`.

---

## 6. `tools/juzgar.py:159-170, 348` y `nucleo/medida.py:710-714`: Medidas propias no aplicadas no invalidan el veredicto del proyecto

- **Ubicación**: `nucleo/medida.py:694-696, 710-714` y `tools/juzgar.py:159-170, 328, 348`.
- **Mecanismo**:
  Al ejecutar `oracle juzgar` sobre un proyecto:
  `tools/juzgar.py:159` filtra `medidas_a_evaluar = medidas_aplicables(catalogo.values(), evidencia)`.
  Las medidas propias del proyecto cuyas relaciones no están presentes en la evidencia se acumulan en `faltantes` (`tools/juzgar.py:162-164`) y se asignan a `informe.no_aplicadas`.
  En `nucleo/medida.py:710-714`:
  ```python
  @property
  def ok(self) -> bool:
      if self.no_juzgaron:
          return False
      return bool(self.veredictos) and all(v.ok or self.perdona(v) for v in self.veredictos)
  ```
  `Informe.ok` sólo exige que haya al menos un veredicto y que todos los evaluados estén en verde (o perdonados). No comprueba que `self.no_aplicadas` esté vacío.
  En `tools/juzgar.py:348`:
  `return 0 if es_aprobado else 1` (donde `es_aprobado = informe.ok`).
  Si un proyecto define 30 medidas propias y el sensor extrae sólo 1 relación (cuya medida resulta verde) omitiendo las 29 restantes, `juzgar` imprime las 29 en la sección `NO SE APLICARON`, pero concluye:
  `VEREDICTO: verde en 1 medidas` y sale con código `0` (**VERDE global**).
  En un pipeline de integración continua, una falla grave del sensor que omita el 90% de las relaciones resulta en salida exitosa 0.
- **Entrada concreta que lo dispara**:
  Ejecutar `oracle juzgar` en un proyecto con medidas declaradas, pasando un `hechos.json` que contiene únicamente una relación auxiliar que da verde, omitiendo las relaciones del resto de las medidas del proyecto.
- **Cobertura**:
  Verificado en el código. `Informe.no_aplicadas` sólo se formatea en `lineas_no_aplicadas()` para visualización; no altera la propiedad `ok` ni el código de retorno.

---

## 7. `nucleo/marco.py:287-289`: `hechos_de_casos` fuerza `dio = esperado` si la medida no existe en el catálogo

- **Ubicación**: `nucleo/marco.py:287-289`.
- **Mecanismo**:
  Al construir la relación meta `caso` para juzgar el corpus en el nivel L2:
  ```python
  if existe:
      try:
          dio = catalogo[mid].evaluar(c["evidencia"]).ok
      except ErrorDeAlgebra:
          dio = not esperado
  else:
      # nada que comparar: se igualan y de la falta se ocupa otra medida (ver el docstring)
      dio = esperado
  ```
  Si un caso declara una medida que no existe en el catálogo (`mid not in catalogo`), `hechos_de_casos` fuerza `dio = esperado`.
  Al medir el marco con `meta.el_caso_se_pone_como_debe` (cuyo predicado busca `c.esperado_ok != c.dio_ok`), este caso resulta en igualdad y por tanto sale **VERDE** (no produce testigo de discrepancia).
  Aunque `tools/aceptacion.py:130-132` intercepta esto con una comprobación imperativa previa (`fallas.append(...)`), cualquier herramienta o consulta del metalenguaje que evalúe `meta.el_caso_se_pone_como_debe` directamente sobre los hechos de casos recibe un falso verde para los casos con medidas ausentes.
- **Entrada concreta que lo dispara**:
  Caso en el corpus con `"medida": "inexistente.foo"`.
  `hechos_de_casos` emite `esperado_ok == dio_ok`.
- **Cobertura**:
  Reconocido como decisión deliberada en `nucleo/marco.py:19-25` ante la falta de un operador de ausencia en el álgebra. Mitigado sólo en `tools/aceptacion.py:130-132` fuera de la evaluación algebraica.

---

## 8. `nucleo/algebra.py:793, 875-876`: `donde` y `sin` usan *truthiness* de Python en lugar de exigir estrictamente tipo `bool`

- **Ubicación**: `nucleo/algebra.py:793` y `nucleo/algebra.py:875-876` (en contraste con `nucleo/medida.py:312-314`).
- **Mecanismo**:
  En `nucleo/algebra.py:875-876`:
  ```python
  if op == "donde":
      ruta_expr = (*ruta, 1) if ruta is not None else None
      return [f for f in filas if evaluar_expr(
          paso[1], f, limites, registro=escalares, ruta=ruta_expr)]
  ```
  Y en `_sin` (`nucleo/algebra.py:793`):
  ```python
  if evaluar_expr(condicion, fila_combinada, limites, registro=registro, ruta=ruta_cond):
      hubo_coincidencia = True
  ```
  `evaluar_expr` no valida que el valor devuelto sea estrictamente de tipo `bool`. Python evalúa la expresión con reglas de *truthiness*:
  - Cadenas no vacías (`"false"`, `"0"`), enteros distintos de cero (`1`, `-1`), etc., evalúan a verdadero.
  - El entero `0`, flotante `0.0` o cadena vacía `""`, evalúan a falso.
  En cambio, `_cumple` en `nucleo/medida.py:312-314` para condiciones de `requiere` sí exige:
  `if type(valor) is not bool: raise ErrorDeAlgebra(...)`.
  Esta falta de verificación en el evaluador de expresiones de `donde` y `sin` permite que predicados mal construidos (por ejemplo acceder a un campo escalar numérico o textual creyendo que es booleano) filtren o conserven filas silenciosamente, culminando en un falso verde.
- **Entrada concreta que lo dispara**:
  Paso `["donde", ["campo", "a", "estado"]]` donde el campo `estado` contiene cadenas de texto (ej. `"activo"`). Pasa el filtro sin error de tipo.
- **Cobertura**:
  Identificado en `TAREA.md` como uno de los cuatro puntos a cerrar en el álgebra 1.0; no cubierto ni validado en la versión actual (0.8) del álgebra.
