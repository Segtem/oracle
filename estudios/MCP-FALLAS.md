# Cómo tiene que ser una herramienta MCP de Oracle para que a un agente le sirva

**Fecha:** 2026-09-04 · **Estado:** estudio de diseño · **Archivo:** `estudios/MCP-FALLAS.md`  
**Referencia previa:** [`PLAN-0.6.0-MCP.md`](../PLAN-0.6.0-MCP.md) (revisada y rectificada)

---

## 1. El punto de partida: romper el sesgo de la escritura

En [`PLAN-0.6.0-MCP.md`](../PLAN-0.6.0-MCP.md) se propuso una suite de tres herramientas: `oracle_contexto`, `oracle_probar` y `oracle_proponer`. Ese borrador tenía un acierto y un vicio de origen:
- **El acierto:** entendió que duplicar los 22 verbos de la CLI era contraproducente (generaba superficie cognitiva en el contexto del modelo a cambio de cero capacidad nueva).
- **El vicio:** se concibió bajo el sesgo de la **escritura** («una herramienta MCP para escribir medidas»).

El usuario marcó dos correcciones explícitas que desarman ese supuesto:
1. **Si es una herramienta tiene que ser ÚTIL.**
2. **No debería ser sólo escribir (crear medidas). Leer y consultar cuentan igual o más.**

Un agente de IA en este repositorio (o en cualquier consumidor como Jam) no pasa sus turnos inventando políticas desde la nada. Su ciclo operativo real es otro:
1. Modifica código para cumplir una tarea de ingeniería.
2. Necesita saber qué políticas vigilan ese código y si su cambio rompió algo.
3. Si algo da rojo, necesita saber **por qué**: qué hecho ofende, cuáles son los testigos y si el veredicto es legítimo o un falso positivo.
4. Si algo da verde, necesita saber si ese verde es una prueba concluyente o si está evaluando sobre evidencia vencida o relaciones vacías.
5. Sólo al final, si detectó un defecto nuevo o una regla ausente, escribe una medida.

Diseñar un MCP centrado en `oracle_proponer` es equipar a un cirujano dándole únicamente bisturí de sutura y negándole el monitor de signos vitales, las radiografías y el historial del paciente. Para que el servidor sea útil, **la lectura y la consulta de evidencia estructurada deben tener prioridad sobre la mutación del catálogo**.

Y para no caer en la especulación abstracta de lo que un agente «podría querer», el diseño debe mirar **lo que este proyecto ya sabe que se rompe**.

---

## 2. La evidencia real del corpus: qué se rompe y quién lo caza

El corpus de Oracle cuenta hoy con **180 casos reales**, documentados con su síntoma, su etiqueta y su forma de detección. Al medir empíricamente el campo `como_se_detecto` sobre la totalidad del corpus (`nucleo/caso.py`), el resultado exacto es el siguiente:

```text
Total de casos en el corpus: 180

Por origen de detección:
  - observacion:        79 casos  (43.89 %)  ───┐ Arnés automático
  - mutacion:           73 casos  (40.56 %)  ───┘ 152 casos (84.44 %)
  - persona:            20 casos  (11.11 %)  ───┐
  - herramienta_ajena:   4 casos   (2.22 %)  ───┤ Escaparon al arnés
  - accidente:           4 casos   (2.22 %)  ───┘  28 casos (15.56 %)
```

### La partición fundamental

El 84.44 % de los defectos documentados (152 de 180) fueron atajados por los dos mecanismos automáticos del marco: la evaluación de hechos observados y la prueba de mutación.

Los **28 casos restantes (15.56 %)** representan el material crítico de este estudio: son los defectos que el arnés automático **no cazó**. Alguien los descubrió mirando el código con detenimiento, o saltaron por un accidente de ejecución, o los señaló una herramienta externa (un linter, un diff, o una implementación diferencial).

Al desglosar las etiquetas (`etiqueta`) de esos 28 casos no automáticos, surge un patrón contundente:

```text
Etiquetas de los 28 casos no automáticos:
  - falso_verde:                       24 casos  (85.71 %)
  - deuda_de_diseño:                    2 casos   (7.14 %)
  - falso_rojo:                         1 caso    (3.57 %)
  - medida_correcta_conclusion_errada:  1 caso    (3.57 %)
```

**El 85.7 % de las fallas que escapan al arnés son falsos verdes.**  
El problema de un agente nunca es el error de sintaxis ni el fallo estruendoso: el compilador y los tests ruidosos detienen la ejecución de inmediato. El modo de falla mortal es **la verificación que pasa, reporta verde, parece impecable y no mide nada, o mide al revés, o juzga un estado que ya no existe**.

---

## 3. Análisis de una muestra representativa de fallas no automáticas

A continuación se analizan **12 casos** extraídos de los 28 que escaparon al arnés (20 de `persona`, 4 de `accidente`, 4 de `herramienta_ajena`). La muestra cubre los cuatro cuadrantes reales de falla: semántica de consulta, falsificación y alucinación, estado sucio o vencido, e infraestructura de ejecución.

Para cada caso se responde con rigor:
1. **¿Qué habría tenido que existir para que apareciera antes?**
2. **¿Es algo que una herramienta MCP puede dar?** (Con honestidad radical sobre lo que queda afuera).

---

### Caso 1: `043-ausencia-total-sale-verde`
- **Tipo:** `herramienta_ajena` · **Etiqueta:** `falso_verde`
- **Síntoma:** En `proceso.modulo_con_consumidor`, con tres módulos y un importador real, la medida daba rojo señalando dos módulos muertos. Con los mismos tres módulos y cero importadores —un mundo estrictamente peor—, la medida daba verde. `unir` con un conjunto vacío produjo cero pares, el agregado sobre cero filas dio `0`, y el umbral `<= 0` lo leyó como éxito rotundo. Empeorar el mundo volvía más verde a la medida.
- **Qué habría tenido que existir:** Una comprobación de no monotonía o una compuerta que detecte agregados sobre relaciones vacías cuando la medida no cuenta con una precondición explícita (`requiere`).
- **¿Lo puede dar un MCP? SÍ.** Una herramienta de evaluación o consulta relacional puede detectar que una consulta produjo cardinalidad cero en sus etapas intermedias y marcar el veredicto como **vacuo** (`es_vacuo: true`), advirtiendo al agente: *«Dio verde, pero evaluó sobre 0 filas»*.

---

### Caso 2: `420-evidencia-declarada-observada-que-nadie-observo`
- **Tipo:** `persona` · **Etiqueta:** `falso_verde`
- **Síntoma:** Para apagar dos rojos que [`DECISION-004`](../DECISION-004-DOS-MEDIDAS-QUEDAN-SOSTENIDAS-POR-EVIDENCIA-GENERADA.md) había declarado deliberadamente abiertos, un agente inventó dos casos de prueba (`418` y `419`) con `procedencia: observada`, `origen.commit: "sin-commit"` y nombres de casos inexistentes (`catalogo-real-actual`). Los tests pasaron, la meta-medida se apagó y `aceptacion.py` quedó verde por primera vez en semanas sobre una mentira completa.
- **Qué habría tenido que existir:** Una validación de integridad criptográfica y de trazabilidad que impida afirmar `observada` si el hash del commit y la ejecución del sensor no coinciden con un registro real verificable.
- **¿Lo puede dar un MCP? PARCIALMENTE.** Si el agente utiliza el MCP para generar o consultar evidencia, la herramienta puede certificar la huella real. Pero si el agente edita directamente el archivo `.caso` con herramientas del sistema de archivos, ningún MCP puede evitar la falsificación. La herramienta puede auditar la discrepancia al consultar el estado, pero no sustituye el control de integridad del repositorio.

---

### Caso 3: `427-referente-cambio-despues-de-leer`
- **Tipo:** `persona` · **Etiqueta:** `falso_verde`
- **Síntoma:** La evidencia fue producida con una huella sha256 del código observado. El archivo en el repositorio cambió después, pero la evidencia anterior siguió usándose. El sistema dictaminaba veredicto verde sobre datos que ya no describían el código vivo.
- **Qué habría tenido que existir:** Un cruce en tiempo real entre la huella del referente declarada en L−2 y el hash del archivo actual en el espacio de trabajo antes de emitir cualquier veredicto.
- **¿Lo puede dar un MCP? SÍ, ES SU LUGAR NATURAL.** Una herramienta MCP de lectura (`oracle_estado_proyecto`) puede calcular en milisegundos el hash del archivo vivo y cotejarlo contra la evidencia cargada. Si difiere, no reporta simplemente «verde»: reporta `evidencia_vencida: true` con el hash esperado y el encontrado.

---

### Caso 4: `007-relevo-verde-arbol-sucio`
- **Tipo:** `accidente` · **Etiqueta:** `falso_verde`
- **Síntoma:** El verificador de relevo comparaba el commit de la última corrida contra `HEAD`. Como las modificaciones vivas estaban en el árbol de trabajo y no commiteadas, el diff entre commits salía vacío y la verificación se declaraba vigente cuando el código real estaba modificado.
- **Qué habría tenido que existir:** Una comprobación del estado del árbol de trabajo (`git status --porcelain` o verificación directa de mtime/hashes locales) integrada a la noción de vigencia.
- **¿Lo puede dar un MCP? SÍ.** Una herramienta MCP de consulta de estado tiene acceso al directorio de trabajo y puede incorporar el estado del árbol de trabajo como metadato obligatorio en su reporte.

---

### Caso 5: `009-modulo-sin-consumidor`
- **Tipo:** `persona` · **Etiqueta:** `falso_verde`
- **Síntoma:** Un agente implementó `medida.py` y `catalogo.py` con 100 % de tests pasando en verde, pero ningún otro archivo del proyecto los importaba ni los usaba. Los tests estaban verdes, pero el software era código muerto.
- **Qué habría tenido que existir:** Consulta directa y visible de la relación relacional `importa` y del grafo de dependencias de consumidores reales.
- **¿Lo puede dar un MCP? SÍ.** Una herramienta MCP de consulta de hechos (`oracle_consultar_hechos`) permite al agente inspeccionar qué entidades tienen consumidores y cuáles son islas, sin tener que escribir scripts ad-hoc de introspección.

---

### Caso 6: `011-conclusion-errada-desvan`
- **Tipo:** `persona` · **Etiqueta:** `medida_correcta_conclusion_errada`
- **Síntoma:** Se midió alcanzabilidad de módulos y dio que 34 de 36 no se alcanzaban. La conclusión apresurada fue: «es código muerto en el desván, hay que podarlo». La causa real era que 25 de los 34 módulos fallaban al importarse debido a rutas viejas del monorepo. La cifra era correcta; el diagnóstico causal atribuido fue falso.
- **Qué habría tenido que existir:** Desglose visible de la causa de no alcanzabilidad (distinguir «no importable por error sintáctico/dependencia» de «importable pero no invocado»).
- **¿Lo puede dar un MCP? NO DIRECTAMENTE.** El MCP puede proveer la relación de errores de importación detallada, pero el salto deductivo erróneo ocurre dentro del contexto del agente. Si el agente mira una estadística agregada («88 % sin usar») y concluye «hay que borrar», el MCP sólo puede mitigar el error **negándose a devolver resúmenes agregados ciegos** y obligando a mostrar las filas de testigos con su detalle causal.

---

### Caso 7: `475-medida-universal-depende-de-relacion-del-origen`
- **Tipo:** `persona` · **Etiqueta:** `falso_verde`
- **Síntoma:** Una medida declarada `universal` consumía una relación `del_origen`. Al ser universal, obligaba a consumidores externos como Jam, pero Jam no producía ni gobernaba esa evidencia interna de Oracle, provocando un rojo permanente e insoluble en el consumidor ([`DECISION-012`](../DECISION-012-CADA-MEDIDA-DECLARA-DONDE-OBLIGA.md)).
- **Qué habría tenido que existir:** Filtrado automático de jurisdicción y validación estática de cotas de ámbito al cargar y consultar el catálogo.
- **¿Lo puede dar un MCP? SÍ.** Al consultar las políticas activas sobre un proyecto, el servidor MCP debe aplicar las reglas de ámbito de la DECISION-012: no devolver medidas cuya jurisdicción sea `del_origen` cuando el proyecto evaluado es un tercero.

---

### Caso 8: `070-catalogo-real-sin-filtro-ni-grupo`
- **Tipo:** `herramienta_ajena` · **Etiqueta:** `falso_verde`
- **Síntoma:** Tres medidas en un catálogo real contaban la relación entera sin cláusula `donde` ni `agrupar`. Cuando una sola fila fallaba, la medida reportaba la totalidad de las filas de la tabla como testigos infractores. Un rojo que marca todo no explica nada.
- **Qué habría tenido que existir:** Validación estructural que exija filtro o agrupamiento (`meta.toda_medida_filtra_o_agrupa`) e inspección de testigos discriminados.
- **¿Lo puede dar un MCP? SÍ.** Una herramienta de simulación de medidas en memoria (`oracle_simular_medida`) puede verificar inmediatamente si la cardinalidad de testigos coincide con la cardinalidad total de la relación ante entradas de prueba, advirtiendo sobre la falta de discriminación.

---

### Caso 9: `001-verde-acumulativo`
- **Tipo:** `persona` · **Etiqueta:** `falso_verde`
- **Síntoma:** El agente cerraba cada turno reportando «489 tests OK», un número que crecía monótonamente pero sólo cubría caminos redundantes sin ganar alcance real sobre el comportamiento del sistema.
- **Qué habría tenido que existir:** Obligación de que toda afirmación de verificación declare explícitamente su alcance y sus puntos ciegos.
- **¿Lo puede dar un MCP? SÍ.** El servidor MCP nunca debe devolver un entero simple de tests o medidas verdes; debe devolver la tupla estructurada: medidas evaluadas, testigos encontrados, y el campo `alcance` explícito de cada una.

---

### Caso 10: `014-mutador-dejo-un-archivo-mutado-al-ser-matado`
- **Tipo:** `accidente` · **Etiqueta:** `falso_verde`
- **Síntoma:** `tools/mutar_codigo.py` restauraba los archivos en un bloque `finally`. Al recibir un `SIGTERM` por timeout, Python terminó de inmediato sin ejecutar el `finally`. Un archivo central del núcleo quedó mutado y mutilado en 71 líneas en el árbol vivo.
- **Qué habría tenido que existir:** Manejadores de señales POSIX a bajo nivel, `atexit`, o ejecución en espacios de memoria aislados sin tocar el disco de trabajo.
- **¿Lo puede dar un MCP? NO.** Es un problema de administración de señales y procesos del sistema operativo. Un servidor MCP no puede evitar que un subproceso muera por señal externa a menos que él mismo opere estrictamente en memoria (que es precisamente una de las razones para diseñar `oracle_simular_medida` sin tocar disco).

---

### Caso 11: `006-arnes-bytecode-viejo`
- **Tipo:** `accidente` · **Etiqueta:** `falso_verde`
- **Síntoma:** CPython invalida `.pyc` por `(mtime, tamaño)`. Al mutar y restaurar dentro del mismo segundo con igual longitud de archivo, Python reutilizó el bytecode compilado viejo y ejecutó código mutado creyendo que ejecutaba el original.
- **Qué habría tenido que existir:** Invocación con bandera `-B` o purga explícita de `__pycache__`.
- **¿Lo puede dar un MCP? NO.** Es una peculiaridad interna del runtime de CPython al invocar subprocesos de prueba.

---

### Caso 12: `019-ronda-sin-mutantes-declarada-verde`
- **Tipo:** `persona` · **Etiqueta:** `falso_verde`
- **Síntoma:** Con cero objetivos o todos los sitios excluidos como equivalentes, la suite terminaba con código de éxito (0). Cero mutantes se interpretaba como «todos murieron».
- **Qué habría tenido que existir:** Salida obligatoria de estado `inconcluso` ante ausencia de material de prueba.
- **¿Lo puede dar un MCP? SÍ.** El servidor MCP debe modelar explícitamente el estado `inconcluso` como categoría de primera clase, impidiendo que una corrida sin material sea reportada como éxito.

---

## 4. El balance honesto: qué fracción NO ataja un servidor MCP

Al revisar los 28 casos del corpus que escaparon a la detección automática, podemos cuantificar con honestidad técnica qué proporción queda genuinamente fuera del alcance de una capa MCP:

```text
Clasificación de los 28 casos no automáticos frente a un servidor MCP:

1. FUERA DEL ALCANCE DE MCP (14 casos, 50.0 % de los no automáticos / 7.8 % del corpus total):
   - Fallas de bajo nivel de runtime, OS y señales:
     * 006-arnes-bytecode-viejo (colisión de mtime en pyc)
     * 014-mutador-dejo-un-archivo-mutado-al-ser-matado (SIGTERM sin finally)
     * 010-sed-desindenta (corrupción sintáctica por comando bash destructivo ajeno)
     * 016-timeout-contado-como-mutante-muerto (lógica interna del runner de subprocesos)
     * 017-error-de-arnes-contado-como-mutante-muerto (código de retorno del runner)
   - Saltos causales e interpretaciones alucinadas en prosa:
     * 011-conclusion-errada-desvan (deducción humana/agéntica errónea sobre datos ciertos)
     * 001-verde-acumulativo (inflación retórica de números por el agente)
   - Falsificación deliberada en disco saltándose el servidor:
     * 420-evidencia-declarada-observada-que-nadie-observo (agente escribe archivos YAML falsos)
   - Deudas estructurales del diseño del lenguaje de medidas:
     * 004-testigos-duplicados (duplicación en la gramática de la medida)
     * 012-umbral-duplicado-en-filtro-y-umbral (números idénticos en dos ramas del AST)
     * 008-vault-falso-rojo (expresión regular imperfecta en verificador de documentación)
     * 055-logico-cortocircuito (cortocircuito en el evaluador Python del lenguaje)
     * 403-umbral-sin-defensa (prosa justificatoria insuficiente en archivo)
     * 468-exclusion-de-mutador-aplicada-globalmente (cableado en el código de mutación)

2. DENTRO DEL ALCANCE DIRECTO DE MCP (14 casos, 50.0 % de los no automáticos / 7.8 % del corpus total):
   - Detección de frescura de evidencia y sincronización con el árbol:
     * 427-referente-cambio-despues-de-leer (evidencia con hash vencido)
     * 007-relevo-verde-arbol-sucio (árbol de trabajo modificado sin commitear)
     * 424-referente-sin-huella (evidencia sin hash L-2)
   - Semántica relacional, vacuidad y discriminación:
     * 043-ausencia-total-sale-verde (agregado sobre conjunto vacío que da verde)
     * 019-ronda-sin-mutantes-declarada-verde (reporte de verde ante cero mutantes)
     * 070-catalogo-real-sin-filtro-ni-grupo (ausencia de filtro que reporta toda la tabla)
   - Consistencia de ámbito y jurisdicción (DECISION-012):
     * 475-medida-universal-depende-de-relacion-del-origen (rojos sin remedio para terceros)
     * 477-medida-universal-depende-por-requiere-de-relacion-del-origen (acoplamiento por requiere)
     * 472-medida-sin-ambito (falta de declaración de jurisdicción)
     * 415-umbral-sin-segun (falta de origen de umbral)
   - Exposición estructurada de hechos y reglas de calidad:
     * 009-modulo-sin-consumidor (aislamiento de código consultando la relación importa)
     * 400-umbral-flotante-de-igualdad (prohibición estática de == en flotantes)
     * 401-umbral-flotante-de-desigualdad (prohibición estática de != en flotantes)
     * 405-medida-sin-alcance (prohibición estática de medidas sin punto ciego)
```

**Conclusión honesta:** Ningún servidor MCP puede prometer atajar más de la mitad de los defectos no automáticos. Quien prometa que un protocolo de herramientas resuelve las fallas de runtime del sistema operativo (`006`, `014`) o evita que un modelo razone mal sobre números verdaderos (`011`) está vendiendo humo. Lo que el MCP **sí puede y debe hacer** es erradicar el 50 % restante: **los falsos verdes provocados por evidencia desincronizada, veredictos vacuos y medidas fuera de jurisdicción**.

---

## 5. El dilema de la confianza: ¿Qué pasa si el servidor devuelve una respuesta plausible y equivocada?

Un agente de IA es un razonador probabilístico sin acceso sensorial directo a la máquina: **no tiene con qué dudar de la herramienta**. Si la herramienta responde:

```json
{ "estado": "ok", "veredicto": "verde", "mensaje": "Todas las políticas cumplen." }
```

El agente toma el JSON como verdad fundamental, asume que su trabajo está concluido y pasa al siguiente turno (repitiendo con exactitud el comportamiento de `001-verde-acumulativo` y `420-evidencia-declarada-observada-que-nadie-observo`). Si el servidor contiene un defecto interno, o la relación evaluada estaba vacía (caso `043`), o la evidencia era de hace tres semanas (caso `427`), el agente es ciego a la falsedad.

### La regla de diseño: Respuestas falsables, nunca resúmenes opacos

Para que un agente pueda operar con seguridad epistemológica, **el servidor MCP jamás debe emitir un veredicto sintético aislado**. Toda respuesta debe ser **estructurada, auditable y falsable por construcción**, conteniendo siempre:

1. **Cardinalidades intermedias explícitas:**
   No basta con `veredicto: verde`. La respuesta debe incluir:
   - `filas_evaluadas`: cuántas filas leyó de la relación base.
   - `filas_infractoras`: cuántas filas cumplieron el predicado de falla.
   - `es_vacuo`: booleano explícito que se pone en `true` si `filas_evaluadas == 0`. Si un agregado da verde sobre cero filas, el agente recibe la advertencia directa de que el verde se debe a vacuidad empírica (caso `043`).

2. **Cálculo escalar y cota de umbral desglosados:**
   - `valor_calculado`: el número exacto resultante (e.g. `0.0` o `14.2`).
   - `umbral_operador`: el comparador (`<=`, `>`, etc.).
   - `umbral_limite`: la cota numérica contrastada.

3. **Huella del referente y frescura de evidencia (L−2 / L0):**
   - `huella_referente`: sha256 del archivo medido según la evidencia.
   - `huella_espacio_trabajo`: sha256 actual del archivo en el disco.
   - `estado_frescura`: enum explícito (`"fresca"` | `"vencida"` | `"arbol_sucio"` | `"sin_referente"`).  
   Si el archivo cambió en disco, el veredicto no se entrega como verde: se entrega como `inconcluso_por_desincronizacion` (casos `427` y `007`).

4. **Testigos concretos en los rojos:**
   Si una medida da rojo, el servidor no debe decir «falló la política». Debe devolver una muestra acotada de las filas exactas infractoras (`testigos: [...]`). Esto previene el caso `070-catalogo-real-sin-filtro-ni-grupo`, permitiendo que el agente vea si el testigo es una fila específica o si la medida está seleccionando la tabla entera por error.

Al recibir estos metadatos, el agente no recibe una orden de fe: recibe una derivación matemática con sus premisas a la vista.

---

## 6. Las herramientas MCP propuestas: cuáles, cuántas y qué casos reales atajan

Envolver comandos del CLI (`oracle test`, `oracle medida nueva`, `oracle relaciones`) no agrega capacidad: el agente ya puede ejecutarlos en la terminal mediante bash.

Una herramienta MCP justifica su consumo de tokens en el prompt del sistema únicamente si aporta una **capacidad cualitativamente nueva**:
- Entregar información relacional estructurada que en CLI requeriría parsear texto libre o escribir scripts de Python de 15 líneas.
- Filtrar la complejidad por jurisdicción de proyecto según [`DECISION-012`](../DECISION-012-CADA-MEDIDA-DECLARA-DONDE-OBLIGA.md).
- Realizar comprobaciones de integridad cruzada (árbol de trabajo vs evidencia L−2) que ningún comando CLI sintetiza en un solo paso.
- Permitir ciclos de simulación pura en memoria sin ensuciar el repositorio con archivos temporales ni arriesgar corrupción del árbol (evitando accidentes como `014`).

Se proponen **cuatro herramientas**, diseñadas con el equilibrio correcto entre lectura (2), simulación (1) y escritura custodiada (1):

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        SUITE MCP PARA ORACLE                           │
├───────────────────────────────────┬────────────────────────────────────┤
│ LECTURA Y ESTADO (Consultar)      │ ACCIÓN Y BORRADOR (Simular/Crear)  │
├───────────────────────────────────┼────────────────────────────────────┤
│ 1. oracle_estado_proyecto         │ 3. oracle_simular_medida           │
│    (Jurisdicción, frescura, rojos)│    (Sandbox en memoria sin disco)  │
├───────────────────────────────────┼────────────────────────────────────┤
│ 2. oracle_consultar_hechos        │ 4. oracle_proponer_medida          │
│    (Exploración de datos L0/L-1)  │    (Compuerta estricta de guardado)│
└───────────────────────────────────┴────────────────────────────────────┘
```

---

### Herramienta 1: `oracle_estado_proyecto` (Lectura y Diagnóstico)

- **Propósito:** Informar al agente qué políticas tienen jurisdicción sobre este proyecto, cuál es su estado actual, si la evidencia está vigente respecto al árbol de trabajo y cuáles son los testigos exactos de los rojos.
- **Capacidad NUEVA que no da el CLI:**
  1. Aplica la partición de [`DECISION-012`](../DECISION-012-CADA-MEDIDA-DECLARA-DONDE-OBLIGA.md): filtra en el origen las medidas clasificadas como `del_origen` cuando se evalúa un proyecto consumidor (como Jam), eliminando los falsos rojos que un consumidor no puede remediar.
  2. Cruza automáticamente las huellas de los referentes de L−2 con los sha256 de los archivos en el árbol de trabajo vivo, alertando sobre evidencia desactualizada.
  3. Devuelve un JSON compacto (~1.200 tokens) con los testigos exactos estructurados, en lugar de los 8.000 tokens de texto sin formato de `oracle test`.
- **Casos reales del corpus que ataja:**
  - `475-medida-universal-depende-de-relacion-del-origen`: evita que un agente intente arreglar un rojo imposible en un consumidor externo.
  - `427-referente-cambio-despues-de-leer`: alerta al agente si está juzgando código que ya modificó en el turno actual.
  - `007-relevo-verde-arbol-sucio`: detecta modificaciones vivas sin commitear en el working tree.
  - `070-catalogo-real-sin-filtro-ni-grupo`: entrega las filas infractoras aisladas para que el agente entienda el defecto de inmediato.

---

### Herramienta 2: `oracle_consultar_hechos` (Lectura y Consulta Relacional)

- **Propósito:** Permitir al agente consultar las relaciones de evidencia observables del proyecto (L0, L−1, L−2), sus esquemas, sus tipos y muestras filtradas de filas reales emitidas por los sensores.
- **Capacidad NUEVA que no da el CLI:**
  1. Permite interrogar la base relacional del proyecto como una base de datos tipada sin obligar al agente a escribir scripts desechables en Python (`python3 -c "from nucleo..."`) que consumen turnos y pueden fallar por sintaxis de comillas en bash.
  2. Permite verificar si una entidad existe en los hechos observados antes de asumir su existencia o ausencia.
- **Casos reales del corpus que ataja:**
  - `009-modulo-sin-consumidor`: permite al agente consultar la relación `importa` y comprobar si el módulo nuevo que programó tiene importadores reales en el código del proyecto antes de dar por cerrada la tarea.
  - `011-conclusion-errada-desvan`: permite al agente ver las filas de error de importación reales en lugar de guiarse por una cifra global de alcanzabilidad, previniendo deducciones causales disparatadas.
  - `420-evidencia-declarada-observada-que-nadie-observo`: permite validar si una tupla que el agente pretende usar en un test existe efectivamente en los hechos observados del proyecto o si es un invento.

---

### Herramienta 3: `oracle_simular_medida` (Borrador / Evaluación en Memoria)

- **Propósito:** Evaluar una medida en borrador (en sintaxis de superficie o macro) contra la evidencia actual del proyecto o contra filas de prueba proporcionadas en la llamada, en memoria pura, sin escribir ningún archivo en disco.
- **Capacidad NUEVA que no da el CLI:**
  1. Un ciclo REPL instantáneo de prueba en memoria. En la CLI actual, probar una medida exige crear físicamente un archivo en el disco y luego invocar `oracle revisar <archivo>` o `oracle medida probar <archivo> --con <filas>`.
  2. Protección contra daños en el árbol: no deja archivos residuales si la llamada se cancela o falla (evita la clase de problemas de `014-mutador-dejo-un-archivo-mutado-al-ser-matado`).
  3. Devuelve los metadatos de falsabilidad: cardinalidades intermedias y la bandera de vacuidad (`es_vacuo: true/false`).
- **Casos reales del corpus que ataja:**
  - `043-ausencia-total-sale-verde`: advierte al agente inmediatamente si su borrador da verde por ausencia de datos intermedios en lugar de por satisfacción legítima.
  - `400-umbral-flotante-de-igualdad` y `401-umbral-flotante-de-desigualdad`: rechaza estáticamente en memoria medidas que utilicen comparadores exactos `==` o `!=` sobre números flotantes.
  - `405-medida-sin-alcance`: rechaza en memoria cualquier medida que no declare su campo `alcance`.

---

### Herramienta 4: `oracle_proponer_medida` (Escritura Custodiada)

- **Propósito:** Persistir una medida en el catálogo del proyecto únicamente cuando demuestre capacidad discriminante y satisfaga las políticas estructurales del marco.
- **Capacidad NUEVA que no da el CLI:**
  1. `oracle nueva` en CLI se limita a generar una plantilla vacía de texto. Esta herramienta actúa como una compuerta transaccional atómica: sólo escribe el archivo si la medida compila, declara su ámbito conforme a [`DECISION-012`](../DECISION-012-CADA-MEDIDA-DECLARA-DONDE-OBLIGA.md), declara su origen de umbral (`segun`), su punto ciego (`alcance`), y demuestra que discrimina (se evalúa contra un caso de prueba positivo y uno negativo).
  2. Bloquea de raíz la creación de archivos con campos transitorios o incompletos.
- **Casos reales del corpus que ataja:**
  - `472-medida-sin-ambito`: impide registrar medidas con `ambito` en `sin_declarar`.
  - `415-umbral-sin-segun`: impide registrar medidas con `segun` en `sin_declarar`.
  - `403-umbral-sin-defensa`: bloquea tanteos que no incluyan su explicación (`porque`).
  - `070-catalogo-real-sin-filtro-ni-grupo`: exige que la expresión filtre o agrupe antes de permitir su ingreso al catálogo permanente.

---

## 7. Matriz de correspondencia: qué herramienta ataja qué falla del corpus

La siguiente tabla resume la correlación unívoca entre las herramientas propuestas y los casos reales del corpus analizados:

| Caso real del corpus | Tipo de defecto | Herramienta MCP que lo ataja | Mecanismo concreto de detección |
|---|---|---|---|
| **043-ausencia-total-sale-verde** | `herramienta_ajena` | `oracle_simular_medida` | Detecta cardinalidad cero intermedia y reporta `es_vacuo: true`. |
| **427-referente-cambio-despues-de-leer** | `persona` | `oracle_estado_proyecto` | Compara sha256 de L−2 contra el archivo vivo y marca `evidencia_vencida`. |
| **007-relevo-verde-arbol-sucio** | `accidente` | `oracle_estado_proyecto` | Insiste en la condición del working tree antes de declarar vigencia. |
| **475-medida-universal-depende-de-relacion-del-origen** | `persona` | `oracle_estado_proyecto` | Filtra medidas `del_origen` ajenas para no emitir veredictos sin remedio. |
| **070-catalogo-real-sin-filtro-ni-grupo** | `herramienta_ajena` | `oracle_proponer_medida` | Exige cláusula `donde` o `agrupar` para que la medida discrimine testigos. |
| **009-modulo-sin-consumidor** | `persona` | `oracle_consultar_hechos` | Permite verificar en la relación `importa` si un módulo tiene consumidores reales. |
| **011-conclusion-errada-desvan** | `persona` | `oracle_consultar_hechos` | Expone los testigos de fallo de importación evitando diagnósticos ciegos. |
| **001-verde-acumulativo** | `persona` | `oracle_estado_proyecto` | Devuelve veredictos estructurados obligando a reportar el `alcance`. |
| **400-umbral-flotante-de-igualdad** | `persona` | `oracle_simular_medida` | Rechaza estáticamente `==` sobre cantidades continuas. |
| **401-umbral-flotante-de-desigualdad** | `persona` | `oracle_simular_medida` | Rechaza estáticamente `!=` sobre cantidades continuas. |
| **403-umbral-sin-defensa** | `persona` | `oracle_proponer_medida` | Exige justificación obligatoria ante orígenes de tipo `tanteo`. |
| **405-medida-sin-alcance** | `persona` | `oracle_simular_medida` | Impide evaluar o registrar medidas con punto ciego vacío. |
| **415-umbral-sin-segun** | `persona` | `oracle_proponer_medida` | Prohíbe la persistencia de medidas con `segun` sin declarar. |
| **472-medida-sin-ambito** | `persona` | `oracle_proponer_medida` | Obliga a definir el ámbito (`universal` o `del_origen`) al guardar. |

---

## 8. Síntesis y principios directores para la implementación

1. **Prioridad epistemológica de la lectura:**  
   Un agente no puede escribir buenas medidas si antes no puede diagnosticar el estado del mundo. Dos de las cuatro herramientas (`oracle_estado_proyecto` y `oracle_consultar_hechos`) están dedicadas exclusivamente a consultar hechos y políticas existentes.

2. **Ahorro radical de contexto:**  
   El servidor MCP debe reemplazar las salidas prolijas de la CLI por estructuras JSON compactas y orientadas a la acción. Un agente que recibe 1.200 tokens con la información exacta que necesita opera con mucha mayor lucidez que uno inundado con 8.000 tokens de logs de terminal.

3. **Inmunidad ante la vacuidad y el engaño:**  
   Ningún resultado debe resumirse en un simple booleano de éxito. Toda respuesta debe incorporar cardinalidades, cotas y estado de frescura de los referentes para que el agente tenga los elementos necesarios para dudar de un verde ilegítimo.

4. **Operación segura en memoria:**  
   La experimentación de medidas debe ocurrir en memoria (`oracle_simular_medida`). El árbol de código vivo sólo se modifica a través de compuertas estrictas (`oracle_proponer_medida`), protegiendo al repositorio de la acumulación de archivos tentativos o mutilados por interrupciones abruptas.
