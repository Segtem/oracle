# Informe de entrega - Hito 0.21.0 (mutante y variantes)

**Tarea**: `tareas/20260915-155111-mutante`  
**Plan base**: `PLAN-0.21.0-MUTANTE.md`  
**Encargo**: `estudios/0.21.0-mutante/ENCARGO-AGY.md`  

---

## 1. Resumen de lo implementado

Se completó la implementación íntegra del hito 0.21.0, cubriendo la generalización de `requiere` con condiciones booleanas, la admisión de múltiples líneas `requiere` en la superficie de autoría `.oracle`, la incorporación de variantes en declaraciones de relaciones, la creación de la relación unificada `mutante.json` con variantes `medida` y `codigo`, la actualización de los sensores productores de hechos de mutación y la reescritura en forma plana de las dos medidas del catálogo `proceso`.

Todo el desarrollo se realizó exclusivamente mediante herramientas de lectura y edición de archivos, sin invocar shell, sin ejecutar tests ni herramientas de mutación, sin subagentes, sin red y sin commits, respetando la propiedad estricta de archivos.

---

## 2. Detalle por componente

### A. `nucleo/medida.py` (`requiere` con condición y hechos)
- **Forma canónica de AST**: Se amplió `Medida.de_datos` para admitir entradas condicionales `["filas", relacion, alias, condicion]`, además de los nombres de relación simples.
- **Validación al cargar**:
  * Formato exacto de 4 elementos para entradas condicionales.
  * Validación de identificadores de relación y alias con `NOMBRE_RELACION_RE` y `NOMBRE_CAMPO_RE`.
  * Verificación de no repetición: ninguna relación puede aparecer más de una vez en `requiere` (sea simple o condicional).
  * Validación de expresión mediante `validar_expr` con límites y registro.
  * Restricción booleana: se valida que la condición sea una expresión que devuelva booleano (comparadores `<`, `<=`, `>`, `>=`, `==`, `!=`, operadores lógicos `y`, `o`, `no`, literales booleanos o escalares registradas).
  * Validación de alias ajeno: se inspecciona recursivamente la condición asegurando que cualquier acceso a `campo` o `hecho` referencie únicamente el alias declarado para la relación, y rechazando el uso de `col`.
- **Semántica en `Medida.evaluar`**:
  * Si la relación no está presente o su lista de filas está vacía, se emite veredicto con `sin_evidencia` (`"{relacion} sin filas con {_expr(condicion)}"`), `valor=0` y `ok=False`.
  * Si hay filas, se evalúa la condición para cada fila bajo el entorno `{alias: fila}` usando `evaluar_expr`.
  * Si la evaluación de un campo no existe en la fila al comparar, `evaluar_expr` propaga `ErrorDeAlgebra` sin atraparlo ni considerarlo `False`.
  * Si ninguna fila satisface la condición, se emite `sin_evidencia` describiendo relación y condición.
- **Conservación canónica en `a_datos`**: Devuelve la tupla `self.requiere` completa, idéntica a la recibida. Las medidas sin `requiere` no emiten el nodo, y las medidas sin condición mantienen su estructura histórica.
- **Hechos de catálogo**:
  * En `_requiere_de`: cada fila suma la columna `con_condicion` (`False` para requerimientos simples de nombre, `True` para condicionales), preservando `medida`, `indice` y `relacion`.
  * En `_dependencias_de_medida`: las dependencias que provienen de `fuente` suman `"con_condicion": False`, y las que provienen de `requiere` preservan su valor `con_condicion` correspondiente.

### B. `nucleo/sintaxis.py` (Superficie infija `.oracle`)
- **Lector**:
  * Se implementó `_leer_linea_requiere` capaz de distinguir entre listas de nombres (`requiere a, b`) y requerimientos con condición (`requiere <relacion> <alias> donde <condicion>`). La condición se analiza con `_leer_expr_en` enlazando las ubicaciones de diagnóstico.
  * Se implementó un bucle en la lectura del cuerpo de la medida para acumular renglones consecutivos que inicien con `requiere `, combinándolos en orden en un único nodo `["requiere", *entradas]` en la posición canónica 5.
  * Las rutas de diagnóstico de `ambito` y `alcance` se mantienen intactas en `(6,)` y `(7,)` respectivamente (o `(5,)` y `(6,)` si no hay `requiere`).
  * `_tipos_en_plantilla` fue adaptado para reconocer entradas condicionales `["filas", rel, alias, cond]`.
- **Impresor**:
  * En `_lineas_medida`: se emite primero la línea consolidada con todos los nombres requeridos simples (si los hay), seguida de una línea por cada requerimiento condicional en su orden canónico (`requiere <rel> <alias> donde <expr>`).
  * Se garantiza el round-trip exacto (`leer(imprimir(datos)) == datos`).

### C. `nucleo/relacion.py` (Relaciones con variantes)
- **Dataclass `Variante`**: Representa `["variante", valor, *campos]`.
- **Dataclass `Relacion`**:
  * Se añadieron los atributos `variantes: tuple[Variante, ...] = ()` y `discriminante: str = ""`.
  * Propiedad `todos_los_campos`: expone una tupla unificada de campos comunes y campos de todas las variantes, deduplicando por nombre para búsquedas y auditorías.
  * `Relacion.de_datos`: acepta 4 elementos (sin variantes) o 5 elementos (con variantes en posición 3, antes de `alcance`).
  * Validación de reglas semánticas:
    1. El discriminante debe ser un campo común previamente declarado.
    2. El discriminante debe tener tipo `"texto"`.
    3. El bloque `variantes` debe contener al menos una variante.
    4. Los valores de variante deben ser textos no vacíos y únicos.
    5. Cada variante debe declarar al menos un campo.
    6. Ningún campo de variante puede duplicar un campo común.
    7. No puede haber campos repetidos dentro de una misma variante.
    8. Si un campo con el mismo nombre aparece en distintas variantes, debe compartir exactamente el mismo `tipo` y la misma `unidad`.
- **Hechos `hechos_de_relaciones`**:
  * `relacion_declarada`: incluye la columna `variantes: int` (conteo de variantes, 0 si no tiene).
  * `campo_declarado`: incluye la columna `variante: str` (`""` para campos comunes, el valor de la variante para campos específicos).

### D. `nucleo/unidad.py` y `tools/medida.py` (Consultas de campos)
- En `nucleo/unidad.py` (`derivar_unidad_nodo`): busca en `relaciones[rel_nombre].todos_los_campos` antes de evaluar relaciones de proceso/lenguaje, lo que permite deducir la unidad física de campos pertenecientes a variantes.
- En `tools/medida.py` (`_puntos_ciegos`): utiliza `declaradas[relacion].todos_los_campos` para calcular los campos leídos vs. declarados y campos no leídos, evitando falsas alarmas de puntos ciegos o campos no declarados sobre variantes.

### E. `relaciones/mutante.json`
- Se creó la declaración canónica para la relación `mutante` con discriminante `tipo`:
  * Campos comunes: `id` (texto), `apunta_a` (texto), `cambio` (texto), `tipo` (texto).
  * Variante `medida`: `detecciones_conductuales` (entero), `rechazos_del_algebra` (entero).
  * Variante `codigo`: `murio` (booleano), `estado` (texto), `tests_fallaron` (booleano), `error_arnes` (booleano), `timeout` (booleano), `codigo_salida` (entero), `equivalente_declarado` (booleano), `razon_equivalente` (texto).
  * Todos con unidad `sin_unidad` y con `alcance` declarando lo que el sensor no observa.

### F. Productores de mutantes
- `nucleo/mutacion.py`: Se agregó `"tipo": "medida"` en la construcción de los hechos por mutante en `por_mutante.setdefault`.
- `perfiles/python/mutacion_codigo.py`:
  * Se agregó `"tipo": "codigo"` en la construcción de las filas de mutantes.
  * En `_cargar_reanudacion`, se incorporó `"tipo"` al conjunto de campos requeridos y se valida explícitamente `fila["tipo"] == "codigo"`, rechazando manifiestos sin tipo.

### G. Catálogo `proceso`
- `catalogos/proceso/proceso.test_con_mutante_que_lo_mata.oracle`:
  * Reescriba en sintaxis plana `medida`.
  * Filtro `donde m.tipo == "medida"` seguido de la condición de detecciones conductuales y rechazos del álgebra.
  * Cláusula `requiere mutante m donde m.tipo == "medida"`.
  * Alcance actualizado indicando que ante una relación `mutante` vacía o sin mutantes de medida, la medida no concluye y sale `SIN EVIDENCIA`.
- `catalogos/proceso/proceso.codigo_con_mutante_que_lo_mata.oracle`:
  * Reescriba en sintaxis plana `medida`.
  * Filtro `donde m.tipo == "codigo"` seguido del predicado de estado y equivalencia declarada.
  * Cláusula `requiere mutante m donde m.tipo == "codigo"`.
  * Alcance actualizado indicando que ante una relación `mutante` vacía o sin mutantes de código, la medida no concluye y sale `SIN EVIDENCIA`.

### H. Tests unitarios nuevos
- `tests/test_requiere_con_condicion.py`:
  * Pruebas de carga, forma canónica, rechazos de formas inválidas (alias, relación repetida, alias ajeno, referencias a `col`, condición no booleana, sintaxis truncada).
  * Evaluación con relación ausente, relación vacía, filas de otro tipo, filas que cumplen y filas con campos ausentes (verificando que levanta `ErrorDeAlgebra`).
  * Verificación de hechos generados con columna `con_condicion`.
  * Round-trip de superficie `.oracle` con 0, 1 y varias líneas `requiere`.
- `tests/test_relacion_variantes.py`:
  * Pruebas de round-trip con y sin variantes en `Relacion`.
  * Rechazo individual de cada regla de variantes (discriminante inválido/no común/no texto, variantes vacías, valor repetido/vacío, variante sin campos, repetición de campo común, repetición dentro de variante, discordancia de tipo o unidad para un mismo nombre).
  * Aceptación de mismo nombre en distintas variantes con tipos y unidades idénticos.
  * Generación de hechos `relacion_declarada` y `campo_declarado` con variantes.
  * Derivación de unidad para campos de variantes en `nucleo/unidad.py`.
  * Validación de `relaciones/mutante.json`.
  * Evaluación de las medidas de `proceso` sobre evidencias mezcladas y disjuntas.

---

## 3. Contradicciones detectadas en tests existentes

Siguiendo la instrucción de no editar tests existentes y documentar cualquier contradicción detectada:

- **`tests/test_medida.py:150-151` (`test_como_hechos_incluye_requiere`)**:
  ```python
  self.assertEqual(hechos.por_relacion["requiere"],
                   [{"medida": "d.con_requiere", "indice": 0, "relacion": "marca"}])
  ```
  Este test asume la estructura anterior de la relación `requiere` sin la columna booleana `con_condicion`. El encargo 0.21.0 §1 establece:
  > *«Hechos: las filas de `requiere` y de `dependencia_de_medida` que salen de `requiere` suman la columna `con_condicion` (booleano). No quitar ni renombrar columnas existentes.»*
  
  Por tanto, el test existente falla ante la nueva columna `"con_condicion": False` que `test_mutante_revision.py:84-85` y la especificación exigen. El test no fue modificado por ser propiedad de Claude.

---

## 4. Estado de verificación

De acuerdo a las directivas del encargo, no se invocó ningún comando shell ni se ejecutaron los tests ni herramientas de análisis dinámico. Toda la verificación se basó en análisis estático de código, correspondencia exacta de firmas y contratos con `tests/test_mutante_revision.py` y validación cuidadosa de la gramática y el AST.
