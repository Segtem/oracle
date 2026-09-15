# Informe de entrega — Hito 0.22.0 (campos de relaciones y evaluación unificada)

**Tarea**: `tareas/20260915-155654-campos`  
**Plan base**: `PLAN-0.22.0-CAMPOS.md`  
**Encargo**: `estudios/0.22.0-campos/ENCARGO-AGY.md`  

---

## 1. Resumen de lo implementado

Se completó íntegramente la implementación del hito 0.22.0, cubriendo:
1. La declaración explícita de campos literales (`CAMPOS_DE_RELACIONES`) en todos los emisores de relaciones del lenguaje del núcleo y herramientas.
2. El lector AST `campos_de_relaciones_declarados(raiz=None)` en `nucleo/relacion.py`, con verificación fail-closed estricta sin importar los módulos.
3. La declaración en formato canónico de las 6 relaciones de proceso leídas por el catálogo (`relaciones/corrida_mutacion.json`, `relaciones/archivo.json`, `relaciones/modulo.json`, `relaciones/alcanzable.json`, `relaciones/afirmacion.json`, `relaciones/hallazgo.json`).
4. El nuevo emisor y relación del lenguaje `campo_leido` en `nucleo/campo_leido.py`, con resolución de alias en fuentes y requerimientos condicionales, omitiendo nodos especiales `hecho` y `col`.
5. La medida universal `catalogos/meta/meta.toda_medida_lee_campos_que_existen.oracle`.
6. La función unificada de evaluación `evaluar_conjunto` en `nucleo/medida.py` que aísla fallos de `ErrorDeAlgebra` en el nuevo campo `Informe.no_juzgaron` sin abortar la corrida, junto con la actualización de `Informe.ok`, `Informe.texto()` e `Informe.a_json()`.
7. La adaptación de las herramientas del arnés (`tools/aceptacion.py`, `tools/juzgar.py`, `tools/mutar.py`, `tools/mutar_codigo.py`).
8. La creación de dos nuevas suites de pruebas exhaustivas: `tests/test_campos_de_relaciones.py` y `tests/test_no_juzgaron.py`.

Todo el desarrollo se realizó exclusivamente mediante herramientas de lectura y edición de archivos, sin invocar la shell, sin ejecutar tests ni suites de mutación, sin subagentes, sin red y sin commits, preservando la propiedad estricta de archivos y sin modificar tests existentes.

---

## 2. Detalle por componente

### A. Emisores del núcleo: `CAMPOS_DE_RELACIONES`
En cada archivo que define `RELACIONES_*` para relaciones del lenguaje, se incorporó un diccionario literal `CAMPOS_DE_RELACIONES = {"<relacion>": ("<campo1>", ...)}`:
- `nucleo/referente.py`: `referente_declarado` (5 campos), `referente_comparado` (5 campos).
- `nucleo/unidad.py`: `cantidad_comparada` (6 campos).
- `nucleo/diagnostico.py`: `campo_diagnostico` (4 campos).
- `tools/trazar.py`: `paso` (4 campos), `nodo` (4 campos), `producto` (4 campos).
- `tools/metamorficas.py`: `equivalencia` (7 campos).
- `nucleo/marco.py`: `caso` (12 campos), `medida_en_uso` (7 campos), `sombra` (6 campos), `relacion_documentada` (3 campos), `verbo_del_cli` (4 campos), `opcion_del_vocabulario` (4 campos), `mutador_excluido` (4 campos).
- `nucleo/medida.py`: `ancestro` (3 campos), `medida` (12 campos), `paso_de_medida` (7 campos), `fuente` (6 campos), `termino` (5 campos), `requiere` (4 campos), `dependencia_de_medida` (5 campos).
- `nucleo/relacion.py`: `relacion_declarada` (5 campos), `campo_declarado` (6 campos), `ambito_de_relacion` (3 campos).
- `nucleo/campo_leido.py`: `campo_leido` (5 campos: `medida`, `relacion`, `campo`, `origen`, `existe`).

Total: 26 relaciones del lenguaje con sus campos completamente declarados.

### B. Lector AST: `campos_de_relaciones_declarados` en `nucleo/relacion.py`
- Lee los archivos Python mediante análisis sintáctico de árboles (`ast.parse`) sin importar módulos ejecutables.
- Modo por defecto con la lista canónica de emisores conocidos, o recursivo si se pasa `raiz`.
- Valida estrictamente bajo filosofía fail-closed (`RelacionMalDeclarada`):
  * `CAMPOS_DE_RELACIONES` debe ser un `ast.Dict` literal.
  * Todas las claves deben ser literales de cadena (`ast.Constant(value=str)`).
  * Todos los valores deben ser `ast.Tuple` literales.
  * Cada tupla debe contener al menos un elemento y todos deben ser literales de cadena no vacíos.
  * No se permiten campos duplicados dentro de la tupla de una relación.
  * No se permiten relaciones duplicadas entre distintos archivos.
  * Cada relación declarada en `CAMPOS_DE_RELACIONES` debe coincidir exactamente con las relaciones presentes en `RELACIONES_*` del mismo archivo (sin relaciones sobrantes ni faltantes).

### C. Declaraciones de relaciones de proceso en `relaciones/`
Se crearon en formato canónico de datos JSON:
- `relaciones/corrida_mutacion.json`: 23 campos emitidos por `perfiles/python/mutacion_codigo.py`, con tipos `texto`, `entero`, `booleano` y unidades `ms` / `sin_unidad`.
- `relaciones/archivo.json`: campos `ruta` (texto) y `sintaxis_valida` (booleano) emitidos por `tools/observar.py`.
- `relaciones/modulo.json`: campos `nombre` (texto), `es_test` (booleano), `lineas` (entero) y `es_paquete_vacio` (booleano) emitidos por `perfiles/python/marco.py`.
- `relaciones/alcanzable.json`: campos `desde` (texto), `hasta` (texto) y `saltos` (entero) emitidos por el análisis de alcanzabilidad.
- `relaciones/afirmacion.json`: campos `id`, `texto`, `comando` y `alcance` (todos texto sin unidad), leídos por `proceso.afirmacion_declara_alcance.oracle`. Su alcance documenta que se deriva de lo que sus medidas leen, al carecer de emisor en este repositorio.
- `relaciones/hallazgo.json`: campos `verificador`, `objetivo` (texto) y `era_real` (booleano), leídos por `proceso.verificador_sin_falsos_rojos.oracle`. Su alcance documenta análogamente su procedencia.

### D. Relación del lenguaje `campo_leido` en `nucleo/campo_leido.py`
- Define `RELACIONES_DE_CAMPO_LEIDO = frozenset({"campo_leido"})`, `AMBITOS_DE_RELACIONES = {"campo_leido": "universal"}` y `CAMPOS_DE_RELACIONES = {"campo_leido": ("medida", "relacion", "campo", "origen", "existe")}`.
- Implementa `extraer_alias_de_medida(m)` para mapear alias a nombres de relaciones considerando:
  * Las fuentes en la tubería (`["de", rel, alias]`, uniones `["unir", ...]`).
  * Las entradas condicionales de requerimientos (`["filas", rel, alias, condicion]`).
- Implementa `_extraer_lecturas_de_arbol`: recorre recursivamente el AST canónico de la medida buscando nodos `["campo", alias, nombre]`. Ignora expresamente nodos `["hecho", alias]` y `["col", nombre]`.
- Función `hechos_de_campos_leidos(medidas, relaciones=None, raiz=None)`:
  * Si el alias no se resuelve, emite `relacion: ""`, `origen: "sin_declarar"`, `existe: False`.
  * Si la relación está en las relaciones del proyecto, `origen: "declarada"` y `existe` verifica si el campo está en `rel.todos_los_campos` (comunes o de variante).
  * Si la relación está en `campos_de_relaciones_declarados()`, `origen: "lenguaje"` y `existe` verifica si el campo está entre los declarados por el emisor.
  * En cualquier otro caso, `origen: "sin_declarar"`, `existe: False`.

### E. Medida `catalogos/meta/meta.toda_medida_lee_campos_que_existen.oracle`
- Superficie `.oracle` plana, forma `ninguno`, ámbito `universal`.
- Consulta: `de campo_leido c` con `donde c.origen != "sin_declarar" y c.existe == false`.
- Umbral: `<= 0 segun contrato`.
- Justificación `porque` y alcance `alcance` explican qué cubre y qué deja fuera (relaciones no declaradas y variantes no filtradas).

### F. Evaluación unificada `evaluar_conjunto` e `Informe` en `nucleo/medida.py`
- `evaluar_conjunto(medidas, evidencia, limites=None, registro=None) -> Informe`:
  * Itera sobre el conjunto de medidas.
  * Si evaluar una medida levanta `ErrorDeAlgebra`, registra `(m.id, str(e))` en una lista de no juzgados.
  * Para las medidas exitosas, agrega su `Veredicto`.
  * Devuelve un `Informe(veredictos=..., no_juzgaron=tuple(no_juzgados))`.
  * Preserva la función `evaluar` existente intacta.
- `Informe`:
  * Atributo `no_juzgaron: tuple[tuple[str, str], ...] = ()`.
  * Propiedad `ok`: devuelve `False` si `self.no_juzgaron` contiene elementos, aún si todos los veredictos emitidos son verdes.
  * Método `texto()`: lista una sección específica `NO PUDIERON JUZGAR (N)` con el id de cada medida y su motivo, diferenciándolas de fallas en veredictos o falta de evidencia.
  * Método `a_json()`: agrega el campo `"no_juzgaron": [{"id": mid, "motivo": motivo}, ...]`. Si está vacío, devuelve `[]`.

### G. Adaptación de herramientas del arnés
- **`tools/aceptacion.py`**:
  * Emite `**hechos_de_campos_leidos(catalogo.values(), relaciones)` en `evidencia_meta`.
  * Incluye la clase proxy `_MedidaSegura` para envolver el catálogo antes de pasarlo a `hechos_de_casos`, atrapando `ErrorDeAlgebra` y devolviendo un veredicto falso en lugar de abortar con traceback.
  * Evalúa cada caso del corpus con `evaluar_conjunto([catalogo[mid]], c["evidencia"])`; ante `no_juzgaron`, lo reporta limpiamente en `fallas` (`NO JUZGÓ <id>`) sin traceback.
  * Evalúa medidas meta e informe de sombra con `evaluar_conjunto`, registrando `no_juzgaron` en `fallas` salvo que la medida esté expresamente en sombra.
- **`tools/juzgar.py`**:
  * Emplea `evaluar_conjunto`. Si `informe.no_juzgaron` no está vacío, imprime `ERROR AL EVALUAR — «{mid}»: {motivo}` a `stderr` y termina con código `2`.
- **`tools/mutar.py`**:
  * Emplea `evaluar_conjunto`.
  * Añade `"campo_leido"` al conjunto de relaciones producidas por `tools/aceptacion.py` en `ARNESES_APARTE`.
  * En `_politicas_ok(informe)`, comprueba `if informe.no_juzgaron: return False` antes de revisar los veredictos.
- **`tools/mutar_codigo.py`**:
  * Emplea `evaluar_conjunto` e informa las medidas que no pudieron juzgar en la consola, manteniendo la política histórica de su código de salida.

---

## 3. Decisiones tomadas y rationale

1. **Ubicación de `campo_leido` en `nucleo/campo_leido.py`**:  
   El encargo permitía ubicarlo en `nucleo/unidad.py` o en un módulo nuevo. Se eligió crear `nucleo/campo_leido.py` debido a que `tests/test_unidad.py:99` afirma taxativamente `assertEqual(RELACIONES_DE_UNIDAD, frozenset({"cantidad_comparada"}))`. Modificar `RELACIONES_DE_UNIDAD` habría roto un test existente de Claude.

2. **Resolución de alias no encontrados en `campo_leido`**:  
   Si una lectura `["campo", alias, nombre]` usa un alias que no figura en ninguna fuente ni en requerimientos condicionales, se asigna `relacion: ""`, `origen: "sin_declarar"` y `existe: False`. Esto evita falsos verdes y documenta la imposibilidad de vincular la lectura a una relación conocida.

3. **Prevención de traceback en `hechos_de_casos`**:  
   La función `hechos_de_casos(catalogo, casos)` en `nucleo/marco.py` llama directamente a `catalogo[mid].evaluar(c["evidencia"]).ok`. Si la evidencia de un caso defectuoso carece de un campo leído por `mid`, el álgebra levanta `ErrorDeAlgebra`. Dado que `nucleo/marco.py` no debía ser editado fuera de `CAMPOS_DE_RELACIONES`, en `tools/aceptacion.py` se implementó `_MedidaSegura` envolviendo el catálogo. De este modo, ante `ErrorDeAlgebra`, `_MedidaSegura.evaluar` devuelve un objeto con `.ok = False`, reportando el caso sin dejar escapar la excepción.

4. **Tratamiento de `a_json()` en `Informe`**:  
   El encargo estipulaba que `a_json()` debía emitir `no_juzgaron` como lista de `{"id", "motivo"}`. Se serializa exactamente como lista de diccionarios `[{"id": mid, "motivo": motivo}, ...]`, garantizando compatibilidad con herramientas consumidoras de JSON.

---

## 4. Contradicciones con tests existentes

Se identificó una contradicción directa en:
- **`tests/test_medida.py:24-36`** (`ContratoMedidaTests.test_clasificacion_meta_valida_forma_y_contenido`):  
  Este test realiza una aserción estricta sobre `base.relaciones_del_lenguaje` contra un conjunto literal de 25 relaciones:
  ```python
  self.assertEqual(base.relaciones_del_lenguaje,
                   frozenset({"ancestro", "medida", "caso", "medida_en_uso",
                              "paso", "nodo", "producto", "equivalencia",
                              "paso_de_medida", "fuente", "termino", "requiere",
                              "dependencia_de_medida",
                              "campo_declarado", "relacion_declarada",
                              "referente_declarado", "referente_comparado",
                              "cantidad_comparada", "sombra",
                              "campo_diagnostico",
                              "relacion_documentada",
                              "verbo_del_cli",
                              "opcion_del_vocabulario",
                              "mutador_excluido", "ambito_de_relacion"}))
  ```
  Al crearse la relación del lenguaje `campo_leido` en `nucleo/campo_leido.py`, el conjunto descubierto por `relaciones_del_lenguaje_declaradas()` pasa de 25 a 26 elementos. En cumplimiento estricto de las reglas de propiedad del encargo ("Claude: ... y todo test existente. Si un test existente contradice el encargo, no editarlo: anotarlo en el informe con el nombre del test y por qué"), dicho archivo no fue modificado y se deja registrado para su correspondiente actualización en la ronda de Claude.

---

## 5. Nuevas suites de pruebas añadidas

1. **`tests/test_campos_de_relaciones.py`**:
   - Validación del lector `campos_de_relaciones_declarados()`.
   - Pruebas exhaustivas de rechazo sintáctico fail-closed: literal no dict, valores no tupla, elementos no cadena, campos repetidos en la tupla, relación vacía sin campos, relación duplicada entre archivos, campos declarados para relaciones ajenas al módulo, y relaciones en `RELACIONES_*` sin campos declarados.
   - Verificación de que las 26 relaciones del lenguaje tienen campos declarados.
   - Validación de cada emisor contra sus campos declarados (relaciones, referentes, unidades, diagnóstico, marco, medida, campo_leido).
   - Pruebas unitarias de `campo_leido`: lectura común y de variante en relaciones de proceso, relaciones del lenguaje, relaciones sin declarar, campos inexistentes, lecturas en `requiere` condicional y confirmación de que `hecho` y `col` no producen hechos.
   - Validación de `meta.toda_medida_lee_campos_que_existen.oracle`: verde sobre el catálogo real de Oracle y roja ante una medida artificial que lee campos inexistentes de `mutante`.

2. **`tests/test_no_juzgaron.py`**:
   - `evaluar_conjunto` con una medida válida y otra que levanta `ErrorDeAlgebra`.
   - `Informe.ok`, `Informe.texto()` e `Informe.a_json()` con y sin medidas en `no_juzgaron`.
   - Ejecución de `tools/aceptacion.py` sobre un proyecto temporal con caso con campo faltante: termina limpiamente con código 1 sin traceback.
   - Ejecución de `tools/juzgar.py` ante campo faltante: termina con código 2 reportando el error en `stderr`.
   - Función `_politicas_ok` de `tools/mutar.py`: devuelve `False` cuando `informe.no_juzgaron` contiene elementos.

---

## 6. Estado de verificación

En cumplimiento riguroso de las instrucciones del encargo, **no se ejecutó ningún comando en la shell ni se ejecutaron los tests ni herramientas de análisis dinámico**. La corrección fue verificada exclusivamente mediante inspección estática del código, análisis de AST, comprobación cruzada de contratos y consistencia de esquemas.
