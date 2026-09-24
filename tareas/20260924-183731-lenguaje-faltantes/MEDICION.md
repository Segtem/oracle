# Medición de formas faltantes en catálogos y corpus

Fecha de medición: 2026-09-24.  
Encargo: punto 1 de [TAREA.md](TAREA.md#L17-L19) («Medir primero: en los catálogos de Oracle, Jam, LyraGASP y commander, cuántas medidas usan el doble `agrupar` para contar distintos, cuántos casos rodean la relación vacía y cuántas medidas calculan una proporción con un rodeo. Con archivo:línea»).  
Regla del proyecto: «no se agrega un operador hasta que una segunda medida lo necesite» ([TAREA.md:12-13](TAREA.md#L12-L13); [AUDITORIA.md:71-73](../20260924-174258-auditoria/AUDITORIA.md#L71-L73)).

---

## 0. Catálogos examinados y disponibilidad

1. **Oracle (catálogos y ejemplos del worktree)**:
   - `catalogos/meta/` y `perfiles/python/catalogos/proceso/` ([tools/sintaxis.py:33-37](../../tools/sintaxis.py#L33-L37)).
   - `ejemplo/primer-valor/` ([ejemplo/primer-valor/corpus/colocacion/006-sin-celdas.caso](../../ejemplo/primer-valor/corpus/colocacion/006-sin-celdas.caso)).
   - `ejemplo/seguimiento-tareas/catalogos/` ([ejemplo/seguimiento-tareas/oracle.json:1-14](../../ejemplo/seguimiento-tareas/oracle.json#L1-L14)).
   - `ejemplo/sensor-prosa/catalogos/` ([ejemplo/sensor-prosa/oracle.json:1-6](../../ejemplo/sensor-prosa/oracle.json#L1-L6)).
2. **Jam (copia de consumidor)**:
   - Ubicación: `Jam medidas/`.
   - Estado: 41 archivos de catálogo ([oracle.json:10](Jam: medidas/oracle.json#L10)), basados predominantemente en expansiones de macros como `ninguno` ([catalogos/vault/vault.enlace_resuelve.json:1-11](Jam: medidas/catalogos/vault/vault.enlace_resuelve.json#L1-L11)).
3. **LyraGASP (copia de consumidor)**:
   - Ubicación: `LyraGASP medidas/`.
   - Estado: 27 medidas históricas ([oracle.json:13](LyraGASP: medidas/oracle.json#L13)), estructuradas con `ninguno` ([catalogos/recarga/recarga.montage_en_slot_cuerpo_entero.json:1-11](LyraGASP: medidas/catalogos/recarga/recarga.montage_en_slot_cuerpo_entero.json#L1-L11)).
4. **Commander**:
   - **No disponible / No leído**: no fue copiado a `(copia de consumidor)`. El intento de lectura sobre `consumidores/commander/oracle.json` falló por archivo inexistente (*no such file or directory*). Siguiendo la regla de no afirmar sobre lo no leído, no se asume su contenido.

---

## 1. Conteo de distintos por grupo mediante doble `agrupar`

### Pregunta
¿Cuántas medidas usan el doble `agrupar` para contar distintos?

### Resultado
- **0 medidas reales en producción**.
- **1 único uso pedagógico/didáctico en documentación externa** (`GUIA22.md`).

### Evidencia
1. **El caso histórico documentado**:
   - En la guía pedagógica de la batalla naval (`GUIA22.md:794-822`), citada en el inventario de fricciones ([FRICCIONES.md:40-54](../20260923-120207-ergonomia/FRICCIONES.md#L40-L54)), se documentó la necesidad de encadenar dos pasos `agrupar` para contar casillas tocadas por barco:
     ```oracle
     agrupar:
         clave nave = b.id
         clave celdas_del_barco = b.eslora
         clave marcado_hundido = b.hundido
         clave celda_x = i.x
         clave celda_y = i.y
     agrupar:
         clave nave = nave
         clave celdas_del_barco = celdas_del_barco
         clave marcado_hundido = marcado_hundido
         agregado celdas_tocadas = contar(1)
     ```
   - La auditoría de ergonomía determinó que se trataba de un requerimiento acotado a dicho ejemplo: «La duplicación de claves del ejemplo por barco es real... La propuesta de distintos sólo tiene un patrón por barco demostrado: no cumple la regla para agregar un agregado» ([VERIFICACION.md:58-69](../20260923-120207-ergonomia/VERIFICACION.md#L58-L69); [VERIFICACION.md:248](../20260923-120207-ergonomia/VERIFICACION.md#L248)).
2. **Catálogos de Oracle**:
   - En `catalogos/meta/` y `perfiles/python/catalogos/proceso/`: ninguna medida contiene doble `agrupar`. De hecho, el sensor de propiedades metamórficas registra explícitamente: «cero usan agrupar sin claves» ([tools/metamorficas.py:16-17](../../tools/metamorficas.py#L16-L17)).
   - La única medida de proceso que agrupa es `proceso.modulo_con_consumidor` ([perfiles/python/catalogos/proceso/proceso.modulo_con_consumidor.oracle:4-6](../../perfiles/python/catalogos/proceso/proceso.modulo_con_consumidor.oracle#L4-L6)), y lo hace con un solo `agrupar` agrupando por módulo con un agregado condicional `suma(...)`.
   - En `ejemplo/seguimiento-tareas/` ([catalogos/](../../ejemplo/seguimiento-tareas/)): 3 medidas usan plantillas de macro `ninguno` o `ninguno-requiere` y 1 usa anti-junta `sin` ([seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre.oracle:4](../../ejemplo/seguimiento-tareas/catalogos/seguimiento.toda_tarea_cerrada_tiene_su_commit_de_cierre.oracle#L4)); ninguna agrupa.
   - En `ejemplo/sensor-prosa/`: la medida `prosa.alcance_sin_afirmacion_adversa` ([catalogos/prosa/prosa.alcance_sin_afirmacion_adversa.oracle:1-9](../../ejemplo/sensor-prosa/catalogos/prosa/prosa.alcance_sin_afirmacion_adversa.oracle#L1-L9)) filtra directamente con `donde` y `resumen contar(1)` sin agrupar.
3. **Catálogos de consumidores (Jam y LyraGASP)**:
   - En `consumidores/jam-medidas/`: 41 medidas leídas en JSON; todas usan macros estándar `ninguno` o `ninguno-par` ([catalogos/vault/vault.enlace_resuelve.json:1-6](Jam: medidas/catalogos/vault/vault.enlace_resuelve.json#L1-L6)), sin pasos de agrupación múltiple.
   - En `consumidores/lyragasp-medidas/`: 27 medidas leídas en JSON; todas usan macros estándar ([catalogos/recarga/recarga.montage_en_slot_cuerpo_entero.json:1-6](LyraGASP: medidas/catalogos/recarga/recarga.montage_en_slot_cuerpo_entero.json#L1-L6)), sin pasos de agrupación.

---

## 2. Casos que rodean la relación vacía (`.caso` vacía)

### Pregunta
¿Cuántos casos rodean la relación vacía por limitaciones de la superficie `.caso`?

### Resultado
- **0 casos reales en producción**.
- **1 único caso didáctico histórico con rodeo** (`GUIA22.md:868-875`).
- **Hallazgo clave**: la premisa de que «`.caso` no puede escribir una relación vacía» es **falsa**. El parser y el impresor de `.caso` ya soportan relaciones vacías desde agosto de 2026.

### Evidencia
1. **Falsación de la limitación**:
   - En [AUDITORIA.md:68](../20260924-174258-auditoria/AUDITORIA.md#L68) y [TAREA.md:10-11](TAREA.md#L10-L11) se asume que «`.caso` no puede escribir una relación vacía».
   - Sin embargo, la auditoría ergonómica previa ya había demostrado que la afirmación era falsa ([VERIFICACION.md:149-160](../20260923-120207-ergonomia/VERIFICACION.md#L149-L160)):
     > *«FALSA: .caso representa relaciones vacías... Código: `nucleo/caso.py:_lineas_relacion` (rama sin hechos, 178–179), `_Parser._leer_evidencia`. Debe omitirse el encabezado de campos, no la relación. `git log -S 'if not hechos:' -- nucleo/caso.py` remite a `5219e6e` (25/08, incorporación de la superficie), anterior a la guía. Se clasifica falsa, no como una corrección posterior de 0.28.0. No se necesita `impacto: []` como forma nueva.»*
   - El código en [nucleo/caso.py:178-179](../../nucleo/caso.py#L178-L179) contempla:
     ```python
     if not hechos:
         return [f"{sangria}{relacion}:"]
     ```
   - El test unitario `test_una_relacion_presente_y_vacia_no_es_una_relacion_ausente` en `tests/test_sintaxis.py` ([VERIFICACION.md:21-24](../20260923-120207-ergonomia/VERIFICACION.md#L21-L24); [SALIDAS.txt:93-110](../20260923-120207-ergonomia/SALIDAS.txt#L93-L110)) valida que una relación con solo su nombre e indentación se relee como `{'impacto': []}`.
2. **Uso real en el repositorio propio**:
   - En el corpus de primer valor, el caso `006-sin-celdas.caso` ([ejemplo/primer-valor/corpus/colocacion/006-sin-celdas.caso:14](../../ejemplo/primer-valor/corpus/colocacion/006-sin-celdas.caso#L14)) escribe la relación vacía directamente y de forma natural:
     ```yaml
     evidencia:
         celda_ocupada:
     ```
3. **El rodeo histórico en la guía**:
   - El único caso documentado que rodeó la relación vacía fue `007-sin-disparos.caso` en `GUIA22.md:868-875` ([FRICCIONES.md:173-181](../20260923-120207-ergonomia/FRICCIONES.md#L173-L181)), donde el redactor creyó erróneamente el mito documentado en `GUIA22.md:877` (*«(La superficie .caso no sabe escribir una relación vacía: se omite y listo)»*) y omitió la relación por completo para poner a prueba `requiere`.
   - En los corpus de Jam y LyraGASP no se encontraron casos que omitan una relación presente por incapacidad sintáctica de `.caso`.

---

## 3. Medidas que calculan una proporción con un rodeo (falta de `/`)

### Pregunta
¿Cuántas medidas calculan una proporción con un rodeo porque no existe `/`?

### Resultado
- **0 medidas en los catálogos examinados**.

### Evidencia
1. **Estado del metalenguaje**:
   - En las funciones escalares ([catalogos/escalares.py:16-42](../../catalogos/escalares.py#L16-L42)) existen `@escalar("mas")`, `@escalar("menos")` y `@escalar("por")`, pero **no** existe división (`dividido`, `entre`, `/`).
   - En la sintaxis infija introducida en 0.7/0.30 (`tareas/20260924-111317-aritmetica/`), se incorporaron los operadores infijos `+`, `-`, `*`, pero no `/`.
   - En [AUDITORIA.md:69](../20260924-174258-auditoria/AUDITORIA.md#L69) se señala que `/` «es lo primero que un LLM escribe para una proporción».
2. **Revisión de medidas en Oracle, Jam y LyraGASP**:
   - **Oracle base**:
     - Las medidas siguen el principio de evaluación de defectos discretos (`umbral <= 0 segun contrato porque ...` con `resumen contar(1)`).
     - Donde se juzgan tasas o señales (como en `prosa.alcance_sin_afirmacion_adversa.oracle:3`), el sensor entrega el valor ya normalizado como probabilidad flotante (`probabilidad >= 0.8`), comparándose directamente sin cociente algebraico.
     - En el cálculo de proporciones del propio proyecto (la proporción líneas de núcleo vs. líneas de medidas para el README), el cálculo se realiza fuera del metalenguaje, en Python ([tools/cifras.py:121](../../tools/cifras.py#L121): `proporcion = f"{lineas_nucleo / lineas_medidas:.1f}"`).
   - **Jam**:
     - Las 41 medidas evaluadas ([oracle.json:10](Jam: medidas/oracle.json#L10)) se limitan a invariantes booleanas y conteos de infracciones unitarias ([catalogos/vault/vault.enlace_resuelve.json:6](Jam: medidas/catalogos/vault/vault.enlace_resuelve.json#L6)). Ninguna realiza multiplicación cruzada o rodeos aritméticos para simular divisiones.
   - **LyraGASP**:
     - Las 27 medidas evaluadas ([oracle.json:13](LyraGASP: medidas/oracle.json#L13)) evalúan presencia de configuraciones indebidas en slots y montajes ([catalogos/recarga/recarga.montage_en_slot_cuerpo_entero.json:6](LyraGASP: medidas/catalogos/recarga/recarga.montage_en_slot_cuerpo_entero.json#L6)). Ninguna calcula razones o proporciones.

---

## 4. Resumen y conclusión para el Punto 2

| Forma analizada | Usos reales en catálogos | Casos/usos didácticos | Califica para azúcar sintáctico (regla: $\ge 2$ usos reales) |
|---|:---:|:---:|:---:|
| **Doble `agrupar` para contar distintos** | **0** | 1 (`GUIA22.md:794-822`) | **NO** (falta segundo uso real en catálogo de producción) |
| **Rodeo por relación vacía en `.caso`** | **0** | 1 (`GUIA22.md:868-875`) | **NO** (la sintaxis ya lo soporta: `nucleo/caso.py:178-179`, `006-sin-celdas.caso:14`) |
| **Rodeo de proporción por falta de `/`** | **0** | 0 | **NO** (ninguna medida en producción calcula proporciones) |

### Dictamen
Ninguna de las tres formas investigadas cumple la regla del proyecto («no se agrega un operador hasta que una segunda medida lo necesite», [TAREA.md:12-13](TAREA.md#L12-L13)).
- El doble `agrupar` sólo existe en un tutorial teórico de batalla naval y no en los catálogos reales de Oracle, Jam o LyraGASP.
- La incapacidad de `.caso` para escribir relaciones vacías quedó demostrada como un mito documental de `GUIA22.md`; el lenguaje ya lo soporta sin cambios.
- La división `/` es una expectativa de autoría teórica señalada en la auditoría, sin ninguna medida que hoy la demande o la emule con rodeos.
