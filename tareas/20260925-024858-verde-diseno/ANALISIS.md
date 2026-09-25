# Análisis de diseño sobre cuatro comportamientos en verde

Este documento analiza las cuatro preguntas de diseño planteadas en la tarea a partir de la auditoría de falsos verdes (`tareas/20260925-023140-auditoria-verde/HALLAZGOS.md:72-166`). Todas las afirmaciones técnicas y citas de archivo y línea corresponden a archivos inspeccionados directamente en el repositorio.

---

## 1. Sombra y veredictos `SIN EVIDENCIA` (Hallazgo 3)

### Qué pasa hoy
- **Mecanismo técnico**:
  - En `nucleo/medida.py:479-495`, el método `Medida.evaluar` verifica si faltan relaciones declaradas en `requiere`. Si falta alguna relación o condición requerida, aborta la evaluación de la tubería y retorna un veredicto especial:
    `Veredicto(id=self.id, valor=0, ok=False, ..., sin_evidencia=faltante)` (`nucleo/medida.py:493-495`).
  - La definición de `Veredicto` en `nucleo/medida.py:246-248` documenta su propósito explícito:
    *«Qué relación declarada como necesaria vino vacía. No es un rojo cualquiera: un rojo dice «el mundo está mal», y esto dice «no hay con qué mirar». `ok` sigue en False porque lo único inaceptable es que salga verde.»*
  - Sin embargo, en `Informe.perdona(v)` (`nucleo/medida.py:705-707`), el perdón de una medida en sombra se define como:
    `return not v.ok and v.id in self.en_sombra and not self.supera_su_cota(v)` (`nucleo/medida.py:707`).
    La función únicamente comprueba que `v.ok` sea `False`, que la medida esté en `self.en_sombra` y que no supere su cota. No verifica si el veredicto corresponde a una falla de datos (`v.sin_evidencia`).
  - En `Informe.supera_su_cota(v)` (`nucleo/medida.py:698-703`), se evalúa `valor > cota`. Como `v.valor == 0` (`nucleo/medida.py:493`), para cualquier cota no negativa (e.g. `cota: 94` como en `oracle.json:12`, o `cota: 0`), la comparación `0 > cota` es `False`. Si la sombra no declara cota (`cota is None`), retorna `False`. Por lo tanto, `supera_su_cota(v)` nunca se cumple para un `SIN EVIDENCIA`.
  - En consecuencia, `Informe.perdona(v)` devuelve `True`.
  - En `Informe.ok` (`nucleo/medida.py:710-713`), la propiedad retorna `True` si todos los veredictos satisfacen `v.ok or self.perdona(v)`.
  - En `tools/juzgar.py:348`, `cmd_juzgar` evalúa `return 0 if es_aprobado else 1` con `es_aprobado = informe.ok`. El proceso termina con código de salida `0` (**VERDE**).
  - En `oracle_metalenguaje/motor.py:194-201`, `Motor.evaluar` traslada el mismo `Informe` con `en_sombra=self._en_sombra`, produciendo `informe.ok == True`.
  - En `tools/aceptacion.py:222-223` (nivel L2), los veredictos con `v.id in en_sombra` se agregan a `ensombrecidas` y no a `fallas`, independientemente de si traen `sin_evidencia`.
- **Caso del corpus**:
  - No existe un caso en `corpus/` que combine explícitamente `sombra` con `sin_evidencia` (`tareas/20260925-023140-auditoria-verde/HALLAZGOS.md:92-94`).
  - El caso del corpus que fijó la necesidad de `SIN EVIDENCIA` ante la ausencia de datos es `corpus/proceso/043-ausencia-total-sale-verde.caso:1-21` (`proceso.modulo_con_consumidor`). Si una medida con `requiere` se declara en sombra en `oracle.json`, un sensor que no emita la relación requerida queda perdonado por la sombra y emite verde con código 0.

### Alternativas
1. **Alternativa 1.A: La sombra nunca perdona `SIN EVIDENCIA` (sombra estricta sobre defectos del mundo).**
   - Modificar `Informe.perdona(v)` en `nucleo/medida.py:707`:
     `return not v.ok and not v.sin_evidencia and v.id in self.en_sombra and not self.supera_su_cota(v)`.
   - Si una medida ensombrecida no recibió evidencia, `perdona(v)` retorna `False`, `Informe.ok` es `False`, y `oracle juzgar` / `Motor` devuelven código `1` (fallo).
2. **Alternativa 1.B: Tratar `SIN EVIDENCIA` como precondición insatisfecha (`no_juzgaron`).**
   - En `nucleo/medida.py:711-712`, hacer que `sin_evidencia` invalide `Informe.ok` como lo hace `self.no_juzgaron`, y en `tools/juzgar.py` retornar código 2 (error de entrada).
3. **Alternativa 1.C: Perdón explícito configurable en `oracle.json`.**
   - Añadir una propiedad `"perdona_sin_evidencia": true` en la declaración de sombra en `oracle.json` para que el perdón no ocurra por omisión.
4. **Alternativa 1.D: Mantener el comportamiento actual.**
   - Asumir que la sombra en CI inmuniza a la medida contra cualquier falla de ejecución (tanto datos faltantes como transgresiones de umbral).

### Qué rompería cada una
- **En Oracle**:
  - En `oracle.json:8-14`, la única sombra declarada es `meta.todo_caso_observado_declara_de_donde_salio` (con cota 94). Esta medida lee la relación `caso`, la cual siempre es emitida completa en L2 (`tools/aceptacion.py:188`). Por lo tanto, la Alternativa 1.A no rompe ninguna verificación actual en Oracle (`oracle test` o tests unitarios).
- **En Jam**:
  - Jam utiliza medidas en sombra (`ESPECIFICACION.md:339, 385`). Si en su integración continua un sensor falla y emite una relación requerida vacía, hoy `oracle juzgar` sale con código 0. Con 1.A o 1.B, esa corrida pasaría a fallar (código != 0), obligando a Jam a corregir la extracción del sensor o su pipeline.
- **En LyraGASP**:
  - LyraGASP cuenta con 43 medidas en sombra (`ESPECIFICACION.md:339`). Si LyraGASP realiza corridas parciales donde ciertas relaciones requeridas por medidas en sombra no se recolectan deliberadamente, 1.A o 1.B romperían esas corridas. Con 1.C o 1.D, mantendrían su comportamiento actual.

### Recomendación alineada con «fail-closed»
- **Recomendación: Alternativa 1.A.**
- **Razón**: La sombra se diseñó para dar tiempo a corregir deuda técnica en el código («apaga la consecuencia de un rojo», `tools/aceptacion.py:196-197`). Un veredicto `SIN EVIDENCIA` no es un rojo del mundo; expresa que el sensor no proveyó datos para mirar (`nucleo/medida.py:246-248`). Perdonar `sin_evidencia` convierte un sensor roto o no ejecutado en una aprobación silenciosa en CI, contradiciendo el principio de fallar cerrado.

---

## 2. Macros base `ninguno`, `peor` y `ninguno-par` sin `requiere` (Hallazgo 4)

### Qué pasa hoy
- **Mecanismo técnico**:
  - En `nucleo/macros/ninguno.oracle:4-12`, la macro expande a una medida con `de $relacion $alias`, `donde $predicado`, `resumen contar(1)`, `umbral <= 0`, sin emitir `requiere $relacion`.
  - En `nucleo/macros/peor.oracle:4-12`, la macro expande con `resumen max($expresion)` y `umbral <= $tolerancia`, sin emitir `requiere $relacion`.
  - En `nucleo/macros/ninguno-par.oracle:4-14`, la macro expande con `unir $relacion $aliasB`, `resumen contar(1)` y `umbral <= 0`, sin emitir `requiere $relacion`.
  - En contraste, `nucleo/macros/ninguno-requiere.oracle:4-13` incluye en su línea 10: `requiere $relacion`.
  - Si un sensor emite la relación vacía `{"rel": []}`:
    1. Al no haber `requiere`, `Medida.evaluar` (`nucleo/medida.py:480`) no detecta faltantes (`faltante = ""`).
    2. La tubería corre sobre 0 filas (`nucleo/medida.py:496`).
    3. En `ninguno` y `ninguno-par`, `contar(1)` sobre 0 filas retorna `0` (`nucleo/algebra.py:591-592`). La comparación `0 <= 0` evalúa a `True` (`ok=True`), otorgando un **VERDE** sobre una relación vacía.
    4. En `peor`, `max` sobre 0 filas retorna `0` (`nucleo/algebra.py:591-592`). Si la tolerancia es $\ge 0$, evalúa `0 <= tolerancia` (`True`) y emite **VERDE**.
- **Caso del corpus**:
  - `corpus/proceso/043-ausencia-total-sale-verde.caso:1-21`: Explica que una medida de ausencia sin `requiere` evaluaba sobre cero filas y salía verde ante la ausencia total de datos, lo que motivó incorporar el nodo `requiere` en el lenguaje (`ESPECIFICACION.md:1026-1034`). Pese a ello, las tres macros base originales no emiten `requiere`.

### Alternativas
1. **Alternativa 2.A: Modificar `ninguno`, `peor` y `ninguno-par` para que siempre emitan `requiere $relacion`.**
   - Agregar `requiere $relacion` en el cuerpo de las tres macros en `nucleo/macros/`.
2. **Alternativa 2.B: Mantener las macros base abiertas (sin `requiere`) y proveer la familia completa `-requiere`.**
   - Conservar `ninguno`, `peor` y `ninguno-par` tal como están, y añadir `peor-requiere` y `ninguno-par-requiere` al lado de `ninguno-requiere`.
3. **Alternativa 2.C: Regla de auditoría L2 en catálogo universal.**
   - Una medida meta que advierta si una medida expandida con macro carece de `requiere`, salvo que su `alcance` justifique explícitamente que la relación puede venir vacía.

### Qué rompería cada alternativa
- **Dilema semántico**:
  - En los proyectos existen dos clases de relaciones:
    1. *Relaciones de inventario/sujetos* (ej. `modulo`, `archivo`, `pieza`): Si vienen vacías (`[]`), no hubo qué medir y debe exigirse `requiere`.
    2. *Relaciones de infracciones/hallazgos* (ej. `violacion_estilo`, `colision`): Si el sensor sólo emite filas cuando encuentra anomalías, una corrida perfecta produce `[]`.
  - Si se aplica la **Alternativa 2.A**:
    - Cualquier medida que use `ninguno` sobre una relación donde `[]` representa «cero defectos» pasaría de **VERDE** a **`SIN EVIDENCIA`** (fallo de corrida).
    - **En Oracle**: Afectaría pruebas y medidas donde el estado correcto genera una lista vacía de infracciones.
    - **En Jam y LyraGASP**: Si tienen medidas `ninguno` sobre relaciones de defectos que sólo reportan filas ante problemas, la Alternativa 2.A rompería masivamente sus corridas limpias en CI.
  - Si se aplica la **Alternativa 2.B**:
    - No se rompe ninguna medida existente en Oracle, Jam o LyraGASP. La compatibilidad se preserva plenamente.

### Recomendación alineada con «fail-closed»
- **Recomendación: Alternativa 2.B combinada con la incorporación de `peor-requiere` y `ninguno-par-requiere`.**
- **Razón**: Imponer `requiere $relacion` dentro de `ninguno` imposibilitaría el uso de la macro para relaciones de infracciones puras donde `[]` es el estado válido esperado.
- La postura de diseño fail-closed es:
  1. Conservar `ninguno` para relaciones de infracciones donde `[]` es éxito.
  2. Ofrecer la familia homogénea de precondición: `ninguno-requiere`, `peor-requiere` y `ninguno-par-requiere`.
  3. Establecer en la documentación que si la relación representa el universo de entidades a evaluar, la directriz fail-closed obliga a usar la variante `-requiere`.

---

## 3. Agregados sobre cero filas dan 0 (Hallazgo 5)

### Qué pasa hoy
- **Mecanismo técnico**:
  - En `nucleo/algebra.py:580-593`:
    ```python
    def _agregar(op: str, valores: list) -> int | float:
        ...
        if not valores:
            return 0
    ```
  - La especificación activa en `ESPECIFICACION.md:802-803` (§3) define formalmente:
    *«Agregados: max, min, suma, promedio, contar. contar no evalúa la expresión: cuenta filas. Los agregados sobre cero filas dan 0.»*
  - En `diferencial/referencia/DECISIONES.md:30-31`, la implementación de referencia independiente ratifica:
    *«El agregado global sobre cero filas queda cubierto por resumen [dando 0].»*
  - **Consecuencia**:
    - Para `contar` y `suma`, 0 es el elemento neutro de la suma.
    - Para `promedio`, `max` y `min`, retornar 0 sobre colección vacía es una decisión de especificación.
    - Si una medida evalúa `resumen max(...)` con umbral `<= 0` (o `<= T` con $T \ge 0$), ante una tubería vacía `_agregar` retorna `0`, satisfaciendo `<= T` y emitiendo **VERDE**.
- **Caso del corpus**:
  - `corpus/proceso/043-ausencia-total-sale-verde.caso:10,20`: Cita que «el agregado sobre cero filas da 0 y el umbral `<= 0` lo lee como éxito... un agregado sobre cero filas es indistinguible de un agregado que dio cero, y sólo la medida sabe cuál de las dos cosas es».

### Alternativas
1. **Alternativa 3.A: Mantener la especificación vigente (`agregados sobre cero filas dan 0`).**
   - Preservar `nucleo/algebra.py:591-592` y delegar en `requiere` la protección ante ausencia de datos.
2. **Alternativa 3.B: Hacer que `max`, `min` y `promedio` levanten `ErrorDeAlgebra` sobre colecciones vacías.**
   - Mantener `contar([]) = 0` y `suma([]) = 0`, pero levantar excepción en `max([])`, `min([])` y `promedio([])`.
3. **Alternativa 3.C: Retornar infinitos ($-\infty$, $+\infty$).**
   - Descartada por contrato: `nucleo/algebra.py:126-136` y `ESPECIFICACION.md:527, 804-805` prohíben flotantes no finitos en el álgebra, clasificándolos como `ErrorDeAlgebra`.

### Qué rompería cada alternativa
- **Impacto crítico de la Alternativa 3.B sobre la macro `peor`**:
  - La macro canónica `peor` (`nucleo/macros/peor.oracle:6-9`) opera de la siguiente manera:
    ```
    de $relacion $alias
    donde $expresion > $tolerancia
    resumen max($expresion)
    umbral <= $tolerancia
    ```
  - Si un sistema evaluado cumple plenamente la regla y no tiene **ninguna infracción**, el paso `donde` filtra todas las filas y la tubería queda con **0 filas**.
  - Si `max([])` levantara `ErrorDeAlgebra`:
    ¡Toda medida basada en `peor` levantaría error (`no_juzgaron`, `nucleo/medida.py:807`) exactamente cuando el sistema no tenga violaciones!
    En otras palabras: **¡una medida `peor` jamás podría concluir en VERDE ante la ausencia de defectos!**
  - **En Oracle**: Rompería el álgebra de forma retroincompatible (cambio MAYOR en `VERSION_ALGEBRA`, `ESPECIFICACION.md:503`), rompería las suites de `diferencial/` (`tools/diferencial.py:59-60`) y anularía la macro `peor`.
  - **En Jam y LyraGASP**: Provocaría la rotura inmediata de todas las medidas basadas en `peor` o en resúmenes extremos sobre tuberías filtradas.

### Recomendación alineada con «fail-closed»
- **Recomendación: Alternativa 3.A (preservar la especificación: agregados sobre cero filas dan 0).**
- **Razón**: Devolver 0 en `max([])` no es un descuido, sino el engranaje necesario para que la cuantificación de violaciones con umbral de tolerancia (`peor`) funcione cuando hay 0 violaciones.
- Si se desea evitar que una medida dé verde porque *la relación del sensor* no vino o vino vacía, el mecanismo fail-closed del proyecto es el coefecto `requiere` sobre la relación antes de la tubería (`ESPECIFICACION.md:701-706, 1026-1030`), no alterar la semántica algebraica del `resumen`.

---

## 4. Medidas propias no aplicadas en `oracle juzgar` (Hallazgo 6)

### Qué pasa hoy
- **Mecanismo técnico**:
  - En `tools/juzgar.py:159`, al ejecutar `oracle juzgar` sin `--medida`, se evalúan sólo las que aplican a la evidencia:
    `medidas_a_evaluar = medidas_aplicables(catalogo.values(), evidencia)`.
  - En `tools/juzgar.py:162-164`, las medidas del catálogo propio cuyas relaciones no están en la evidencia se calculan como `faltantes` mediante `no_aplicadas(...)` (`nucleo/medida.py:849-850`).
  - En `tools/juzgar.py:170`, se devuelve `replace(informe, no_aplicadas=faltantes)`.
  - En `nucleo/medida.py:710-714`:
    ```python
    @property
    def ok(self) -> bool:
        if self.no_juzgaron:
            return False
        return bool(self.veredictos) and all(v.ok or self.perdona(v) for v in self.veredictos)
    ```
    `Informe.ok` **no consulta `self.no_aplicadas`**.
  - En `tools/juzgar.py:348`:
    `return 0 if es_aprobado else 1` (con `es_aprobado = informe.ok`).
  - Aunque `Informe.texto` (`nucleo/medida.py:762-763`) imprime la sección `NO SE APLICARON (M) — su relación no vino en la evidencia:`, si las medidas aplicadas dieron verde, el comando sale con código `0` (**VERDE global**).
  - En `oracle_metalenguaje/motor.py:190-201`, `Motor.evaluar` tiene el mismo comportamiento.
  - **Consecuencia**:
    Si un proyecto declara 30 medidas propias y el sensor sólo genera evidencia para 1 de ellas (que sale verde), `juzgar` sale 0. Una falla del sensor que omita el 97% de los datos termina reportando éxito en CI.
- **Caso del corpus / antecedente**:
  - `tareas/20260916-201124-juzgar-omite/TAREA.md:8-17`: Registró este comportamiento al recorrer la guía naval, donde una evidencia sin la relación `impacto` omitía la medida de hundimientos y salía 0. La tarea incorporó el listado visible de no aplicadas pero dejó asentado:
    *««No aplica porque no vino su relación» es exactamente el «no miré» que el lenguaje persigue. A decidir: listar las medidas del catálogo que no se aplicaron (texto y --json) y si una ausente cuenta como SIN EVIDENCIA para el código de salida. Cambia lo que un consumidor ve → MENOR.»* (`líneas 14-16`).

### Alternativas
1. **Alternativa 4.A: `no_aplicadas` invalida el veredicto en `oracle juzgar` (fail-closed incondicional).**
   - Si `informe.no_aplicadas` no está vacío, `es_aprobado = False` y el CLI finaliza con código 1.
2. **Alternativa 4.B: Convertir cada medida propia no aplicada en un veredicto `SIN EVIDENCIA`.**
   - Generar un veredicto `Veredicto(id=m.id, valor=0, ok=False, sin_evidencia="relación ausente")` para cada medida del catálogo propio cuyas relaciones no vinieron.
3. **Alternativa 4.C: Modo estricto por omisión con bandera explícita `--parcial` para corridas deliberadas.**
   - Por defecto, `oracle juzgar` falla (código 1) si hay medidas propias no aplicadas.
   - Si un pipeline desea deliberadamente evaluar sólo un subconjunto, debe autorizarlo explícitamente mediante `--parcial` o seleccionando medidas con `--medida <id>`.
4. **Alternativa 4.D: Mantener el comportamiento actual.**
   - Conservar la salida 0 y considerar `no_aplicadas` como advertencia puramente informativa.

### Qué rompería cada alternativa
- **En Oracle**:
  - `oracle test` corre con `tools/aceptacion.py` (no `tools/juzgar.py`), donde las medidas meta aplicables se evalúan directamente.
  - En los unitarios (`tests/test_juzgar.py:99-150`), los tests usan mayormente `--medida POLITICA_REFERENCIAS`, donde `no_aplicadas` es vacío (`tools/juzgar.py:157`).
- **En Jam y LyraGASP**:
  - Si Jam o LyraGASP utilizan pipelines de CI particionados (e.g. un job ejecuta un sensor de análisis estático y otro ejecuta un sensor de dinámica), cada job ejecuta `oracle juzgar` con evidencia que cubre únicamente una parte de su catálogo propio.
  - Las **Alternativas 4.A y 4.B romperían de inmediato todos los jobs particionados de Jam y LyraGASP**, haciendo que fallen por las medidas no aplicadas del otro job.
  - La **Alternativa 4.C** requiere subir la versión MENOR de la distribución (`VERSION_DISTRIBUCION`, como ya preveía `tareas/20260916-201124-juzgar-omite/TAREA.md:16`), pero brinda un mecanismo limpio (`--parcial`) para que los CI modulares continúen funcionando sin sorpresas.

### Recomendación alineada con «fail-closed»
- **Recomendación: Alternativa 4.C (fail-closed por defecto en corridas totales; bandera explícita `--parcial` para evidencia modular).**
- **Razón**: Emitir un código de salida 0 en CI cuando la gran mayoría de las medidas del proyecto no fueron alimentadas por la evidencia es la antítesis de la filosofía de Oracle. Fail-closed exige que una corrida sin parámetros evalúe el catálogo propio completo o falle si faltan datos; si un consumidor tiene una arquitectura de CI modular, debe declarar esa intención explícitamente con `--parcial` o `--medida`.

---

## Tabla comparativa de decisiones para Brian

| Punto | Situación hoy | Alternativa recomendada | Justificación fail-closed | Impacto de versión | Impacto en Jam / LyraGASP |
|---|---|---|---|---|---|
| **1. Sombra y `SIN EVIDENCIA`** | La sombra perdona si no supera la cota (`nucleo/medida.py:707`) | **1.A**: No perdonar nunca `sin_evidencia` | La sombra tolera deuda de código, no sensores rotos o ceguera de datos | MENOR (cambia semántica de `perdona`) | Falla en CI de Jam/LyraGASP si faltan relaciones requeridas |
| **2. Macros base sin `requiere`** | `ninguno`, `peor`, `ninguno-par` no emiten `requiere` | **2.B**: Mantener base abierta y proveer familia `-requiere` | Imponer `requiere` destruiría el uso de `ninguno` para relaciones de infracciones donde `[]` es éxito | PARCHE (nuevas macros) | Cero roturas en medidas existentes |
| **3. Agregados vacíos dan 0** | Dan 0 por especificación (`ESPECIFICACION.md:802`) | **3.A**: Mantener especificación; la guarda es `requiere` | Levantar error en `max([])` rompería la macro `peor` ante 0 violaciones | NINGUNO (conserva álgebra) | Cero roturas; preserva la macro `peor` |
| **4. Medidas no aplicadas en juzgar** | Se listan pero dan exit 0 (`tools/juzgar.py:348`) | **4.C**: Fallo por defecto; requerir `--parcial` para omisiones | Un CI no puede aprobar con éxito si el 90% de las medidas no corrieron | MENOR (nuevo flag `--parcial` y exit 1) | Requiere añadir `--parcial` en CI modular |
