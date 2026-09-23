# Inventario de fricciones del metalenguaje Oracle

Este inventario documenta las fricciones ergonómicas reales encontradas al escribir y mantener medidas en Oracle. Cada entrada cuenta con evidencia empírica directa (archivo y línea, o comando y salida) proveniente de los proyectos activos (Oracle (`/tmp/claude-1000/-home-workstation-Dev-oracle/27d97167-363a-4362-9167-701b6c10974b/scratchpad/wt-ergo`), Jam (`~/Dev/jam/medidas`), LyraGASP (`~/Dev/games/unreal/LyraGASP/medidas`)), la guía de batalla naval (`~/TestOracleEjemplo/GUIA22.md`), el postmortem (`estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md`) y los proyectos del laboratorio naval (naval-0280 (`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280`) y batalla_naval_test (`~/Dev/lab/batalla_naval_test`)).

---

## 1. Expresiones y cálculo aritmético

### 1.1. Ausencia de operadores aritméticos infijos (`+`, `-`, `*`) en la superficie `.oracle`
- **Problema**: En la superficie infija `.oracle`, las expresiones de filtrado o transformación no soportan operadores aritméticos estándar como `+` o `-`. Para comparar cantidades consecutivas o desplazamientos ordinales, el autor se ve obligado a utilizar llamadas funcionales prefijas como `mas(a, b)` o `menos(a, b)`.
- **Evidencia citada**:
  - `naval.alternancia_turnos.oracle` (`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280/catalogos/naval/naval.alternancia_turnos.oracle:4`):
```oracle
donde t2.turno == mas(t1.turno, 1) y t1.tirador == t2.tirador
```
  - `naval.turnos_sin_huecos.oracle` (`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280/catalogos/naval/naval.turnos_sin_huecos.oracle:6`):
```oracle
donde registrados != mas(ultimo, 1)
```
  - `nucleo/sintaxis.py` (`nucleo/sintaxis.py:208-251`): En el tokenizador `_tokenizar`, únicamente se reconocen comparadores (`==`, `!=`, `<=`, `>=`, `<`, `>`), lógicos (`y`, `o`, `no`), identificadores y llamadas con paréntesis. Cualquier caracter aritmético (`+`, `-`, `*`, `/`) no reconocido cae en `_fallar(linea, col, "expresión", c)` (`nucleo/sintaxis.py:251`), arrojando `ErrorSintaxis: se esperaba expresión; llegó +`.
  - `catalogos/escalares.py` (`catalogos/escalares.py:16-42`): Se tuvieron que registrar funciones escalares explícitas `@escalar("mas")`, `@escalar("menos")` y `@escalar("por")` para suplir la falta de operaciones elementales.

### 1.2. Necesidad de auto-unión con `<` en lugar de `!=` para no inflar conteos en la mutación
- **Problema**: Al unir una relación consigo misma para buscar pares incompatibles o solapados, el uso natural de `a.id != b.id` produce dos filas por cada par `(a, b)` y `(b, a)`. Esto hace que el valor mínimo de infracción sea 2, lo cual permite que el mutador de medidas `aflojar_umbral` (que sustituye `<= 0` por `<= 1`) sobreviva. El autor está forzado a recordar que debe usar `a.id < b.id`, requiriendo un campo con orden total artificial.
- **Evidencia citada**:
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:671-705`):
    > *«El detalle que parece cosmético y no lo es: `a.barco < b.barco` en vez de `!=`. Con `!=` cada superposición aparece dos veces —(a,b) y (b,a)— así que el valor mínimo de un defecto es 2, y el mutador `aflojar_umbral` que cambia `<= 0` por `<= 1` sobrevive: el rojo sigue siendo rojo. Con `<` el par se cuenta una sola vez, el valor es 1, y aflojar el umbral a 1 lo pone verde — el mutante muere.»*
  - `naval.tiros_sin_repeticion.oracle` (`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280/catalogos/naval/naval.tiros_sin_repeticion.oracle:4`):
```oracle
donde t1.tirador == t2.tirador y t1.turno < t2.turno y t1.fila == t2.fila y t1.columna == t2.columna
```

---

## 2. Álgebra relacional y transformaciones

### 2.1. Doble `agrupar` obligatorio para contar elementos distintos (distinct count)
- **Problema**: El álgebra relacional no tiene un agregado o cuantificador de distintos directo (`contar_distintos` o `contar(distinto x)`). La única forma de resolverlo es concatenar dos pasos `agrupar` seguidos: el primero proyecta y deduplica las combinaciones de claves, y el segundo realiza el agregado sobre esas filas proyectadas. Esto produce una duplicación verbosa de claves y mutantes adicionales que obligan a ejercitar múltiples ejes espaciales.
- **Evidencia citada**:
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:794-822`):
    > *«El álgebra no tiene un `contar distintos`, pero no lo necesita: dos `agrupar` seguidos hacen lo mismo. El primero deja una fila por celda tocada; el segundo cuenta esas filas por barco.»*
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
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:908-913`):
    > *«Ese tercero no es relleno. Sin él sobreviven dos mutantes que cambian `clave celda_x = i.x` por `i.y` o por `i.barco`... Contar celdas distintas trae su propia obligación: ejercitar los dos ejes.»*
  - `TAREA.md` (`tareas/20260923-120207-ergonomia/TAREA.md:21-23`): Lo identifica expresamente como fricción previa.

### 2.2. Macros base (`ninguno` y `ninguno-par`) cerradas e incompatibles con `requiere` o filtros compuestos
- **Problema**: La macro estándar `ninguno` (`nucleo/macros/ninguno.oracle:4-11`) y `ninguno-par` (`nucleo/macros/ninguno-par.oracle:4-14`) tienen parámetros fijos y una plantilla rígida. Si una medida de invariante (`umbral <= 0`) necesita declarar una cláusula `requiere` para evitar falsos verdes ante evidencia vacía, o necesita pasos `sin` intermedios, no puede utilizar `ninguno`. Debe reescribirse completa como una definición canónica de 10 a 12 líneas.
- **Evidencia citada**:
  - `nucleo/macros/ninguno.oracle` (`nucleo/macros/ninguno.oracle:4-11`):
```oracle
defmacro ninguno(id, relacion, alias, predicado, porque, segun, ambito, alcance):
    medida $id:
        de $relacion $alias
        donde $predicado
        resumen contar(1)
        umbral <= 0 segun $segun porque $porque
        ambito $ambito
        alcance $alcance
```
  - En `naval-0280` (`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280/catalogos/naval/`): Medidas como `naval.flota_reglamentaria.oracle` (`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280/catalogos/naval/naval.flota_reglamentaria.oracle:1-12`) o `naval.turnos_sin_huecos.oracle` (`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280/catalogos/naval/naval.turnos_sin_huecos.oracle:1-12`) debieron escribirse en sintaxis expandida únicamente para incluir `requiere celda_barco` o `requiere tiro`.

---

## 3. Estructura gramatical y rigidez de autoría

### 3.1. Rigidez posicional estricta en el orden de las cláusulas de una medida
- **Problema**: El parser superficial de `.oracle` impone una secuencia fija invariable para las cláusulas de una medida. Si una cláusula aparece fuera del orden predeterminado (por ejemplo, declarar `requiere` antes de `resumen` o antes de `umbral`), el parser falla inmediatamente con error de sintaxis en lugar de aceptar las cláusulas declarativas en cualquier orden lógico.
- **Evidencia citada**:
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:843-844`):
    > *«⚠️ El orden importa: `requiere` va DESPUÉS de `umbral`, no antes de `resumen`. Si lo ponés arriba, el catálogo no carga.»*
  - `nucleo/sintaxis.py` (`nucleo/sintaxis.py:1224-1255`) (`_leer_medida`):
    El código ejecuta secuencialmente:
    1. `resumen = _leer_resumen(...)` (L1226 (`nucleo/sintaxis.py:1226`))
    2. `_leer_umbral(...)` (L1232 (`nucleo/sintaxis.py:1232`))
    3. `while ... startswith("requiere "):` (L1237 (`nucleo/sintaxis.py:1237`))
    4. `if ... startswith("ambito "):` (L1247 (`nucleo/sintaxis.py:1247`))
    5. `if ... startswith("alcance "):` (L1254 (`nucleo/sintaxis.py:1254`))
    Cualquier alteración en este orden lanza `_fallar(...)`.

### 3.2. Fragilidad en la exigencia de mayúsculas ("NO") en la prosa de `alcance`
- **Problema**: El marco exige que toda medida declare qué aspecto de la realidad omite o no verifica. Sin embargo, la verificación meta comprueba mecánicamente que la cadena contenga el token exacto `"NO"` en mayúsculas. Un redactor que escribe `"no ve..."` o `"no contempla..."` en minúsculas activa un fallo en el nivel L2.
- **Evidencia citada**:
  - `catalogos/escalares.py` (`catalogos/escalares.py:55-60`):
```python
@escalar("contiene")
def contiene(texto, aguja) -> bool:
    """¿`aguja` aparece en `texto`? Sensible a mayúsculas a propósito: se usa para exigir que un
    `alcance` enuncie algo en negativo («NO ve…»), y ahí las mayúsculas son la señal."""
    return str(aguja) in str(texto)
```
  - `nucleo/medida.py` (`nucleo/medida.py:408-410`):
```python
if not (isinstance(alcance, list) and len(alcance) == 2 and alcance[0] == "alcance"
        and isinstance(alcance[1], str) and alcance[1].strip()):
    raise MedidaMalDeclarada(f"{mid}: falta `alcance` — hay que declarar qué NO ve")
```

---

## 4. Metadatos, relaciones y deuda acumulada en sombras

### 4.1. Falta de superficie infija para relaciones (`relaciones/` en JSON crudo)
- **Problema**: Las relaciones relacionales y sus campos no tienen una sintaxis superficial propia en `.oracle`. Se declaran obligatoriamente en JSON mediante listas anidadas con etiquetas como `["relacion", ..., ["campos", ["campo", ...]], ["alcance", ...]]`.
- **Evidencia citada**:
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:234-251`):
    > *«Las relaciones se escriben en JSON (no tienen superficie infija todavía). Acá las escribís a mano; más abajo está el atajo.»*
```json
["relacion", "barco",
  ["campos",
    ["campo", "id", "texto", "sin_unidad"],
    ["campo", "x", "entero", "celdas"],
    ...
  ],
  ["alcance", "lee la flota tal como quedo en el estado del juego..."]]
```

### 4.2. Deuda masiva acumulada por la exigencia de unidades dimensionales
- **Problema**: La medida meta `meta.toda_cantidad_comparada_tiene_unidad_derivable` exige que toda comparación numérica posea unidades compatibles declaradas en `relaciones/`. Como declarar esto en JSON para catálogos extensos representa un alto costo de autoría, los proyectos reales terminan encubriendo la regla bajo la directiva `sombra` de `oracle.json` con cotas fijadas para evitar que el CI falle.
- **Evidencia citada**:
  - `Dev/jam/medidas/oracle.json` (`~/Dev/jam/medidas/oracle.json:8-12`):
```json
"meta.toda_cantidad_comparada_tiene_unidad_derivable": {
  "desde": "2026-09-01",
  "porque": "54 comparaciones sin unidad derivable sobre 41 archivos de catálogo... El 2026-09-22 bajó a 51 al declarar vecina y asentamiento...",
  "cota": 51
}
```
  - `LyraGASP/medidas/oracle.json` (`~/Dev/games/unreal/LyraGASP/medidas/oracle.json:6-10`):
```json
"meta.toda_cantidad_comparada_tiene_unidad_derivable": {
  "desde": "2026-09-01",
  "porque": "16 comparaciones sin unidad derivable; hay que declarar los campos de las relaciones de UE en relaciones/, y se hace por relación, no de golpe. Medido el 2026-09-19: hoy son 61...",
  "cota": 61
}
```

### 4.3. Deuda acumulada por umbrales preexistentes sin cláusula `segun`
- **Problema**: La incorporación tardía de la cláusula obligatoria `segun` (para distinguir si el umbral proviene de `contrato`, `convencion`, `medicion` o `tanteo`) dejó decenas de medidas históricas en catálogo con `"sin_declarar"`, requiriendo sombras de larga duración.
- **Evidencia citada**:
  - `Dev/jam/medidas/oracle.json` (`~/Dev/jam/medidas/oracle.json:13-17`): Cota de 41 umbrales sin declarar en Jam.
  - `LyraGASP/medidas/oracle.json` (`~/Dev/games/unreal/LyraGASP/medidas/oracle.json:11-15`): Cota de 27 umbrales sin declarar en LyraGASP.
  - `Dev/jam/medidas/catalogos/vault/vault.enlace_resuelve.json` (`~/Dev/jam/medidas/catalogos/vault/vault.enlace_resuelve.json:8`):
```json
"sin_declarar",
```
  - `LyraGASP/medidas/catalogos/recarga/recarga.montage_en_slot_cuerpo_entero.json` (`~/Dev/games/unreal/LyraGASP/medidas/catalogos/recarga/recarga.montage_en_slot_cuerpo_entero.json:8`):
```json
"sin_declarar",
```

---

## 5. Casos de prueba, corpus y evidencia observada

### 5.1. Incapacidad de la superficie `.caso` para representar relaciones vacías
- **Problema**: En la sintaxis `.caso`, no existe una notación para declarar que una relación requerida fue emitida pero no contiene filas (p. ej. `impacto: []`). La convención adoptada es omitir la relación por completo del bloque `evidencia:`. Esto genera confusión, ya que omisión física se confunde con ausencia estructural.
- **Evidencia citada**:
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:877`):
    > *«(La superficie `.caso` no sabe escribir una relación vacía: se omite y listo.)»*
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:868-875`) (`corpus/partida/007-sin-disparos.caso`):
```
etiqueta: falso_verde
medida: partida.hundido_sin_impactos_suficientes
evidencia:
    barco: id, x, y, x_fin, y_fin, eslora, hundido
        "destructor", 2, 2, 2, 4, 3, true
```
    (Omite la relación `impacto` por completo para verificar la cláusula `requiere impacto`).

### 5.2. Transcripción manual tediosa de evidencia real a casos observados
- **Problema**: Para cumplir con `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`, el autor debe transformar volcados JSON generados por el sensor del producto (`partida.json`) a casos estructurados con metadatos de procedencia (`origen`, `repo`, `commit`, `comando`, `registro`). La sintaxis `.caso` resulta inmanejable para tablas grandes, obligando al usuario a escribir scripts auxiliares en Python que generan casos en JSON.
- **Evidencia citada**:
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:585-620`):
    > *«Transcribir partida.json a mano a la superficie .caso es tedioso y es justo donde uno se equivoca. Pero el corpus acepta casos en JSON además de .caso, así que un script de veinte líneas lo arma. Guardalo como ~/TestOracleEjemplo/caso_observado.py...»*
  - `Dev/jam/medidas/oracle.json` (`~/Dev/jam/medidas/oracle.json:18-22`): Cota de 16 medidas en Jam fijadas únicamente con evidencia fabricada.
  - `LyraGASP/medidas/oracle.json` (`~/Dev/games/unreal/LyraGASP/medidas/oracle.json:16-20`): Cota de 17 medidas en LyraGASP fijadas únicamente con evidencia fabricada.
  - `wt-ergo/oracle.json` (`oracle.json:9-14`): 94 casos del propio Oracle en sombra porque declaran sólo `repo` y `commit` sin `comando` o `registro`.

### 5.3. Limitación del generador de casos (`oracle caso generar`) ante restricciones complejas de dominio
- **Problema**: El generador sintáctico de casos analiza mutantes sobrevivientes e intenta sintetizar filas numéricas mínimas. Cuando la medida involucra restricciones relacionales complejas (p. ej. coordenadas geométricas disjuntas que compartan proyecciones), el generador se rinde y exige que el usuario diseñe manualmente casos con configuraciones sutiles.
- **Evidencia citada**:
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:711-716`):
```
generación no posible: flota.dos_barcos_en_la_misma_celda: no se pudo fabricar verde_correcto con contar y umbral <= 0; la evidencia propuesta da valor 4, verde=False. Hace falta evidencia del dominio — no se escribió ningún archivo
```

---

## 6. CLI, entorno de ejecución y experiencia de agentes

### 6.1. Contagio omnipresente del flag `--confiar-escalares`
- **Problema**: En el momento en que un proyecto incorpora un archivo `escalares.py`, prácticamente todos los comandos de inspección y prueba (`test`, `juzgar`, `revisar`, `medida listar`, `caso generar`) se niegan a operar sin la opción explícita `--confiar-escalares`, aun si la medida que se examina no invoca ninguna función escalar externa.
- **Evidencia citada**:
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:964-971`):
    > *«Desde que `escalares.py` existe, todo lo que carga el catálogo necesita la bandera, aunque la medida que tocás no use ninguna escalar: `test`, `juzgar`, `revisar`, `medida listar` y `caso generar`. Sin ella se niegan, y te lo dicen: ESCALARES EXTERNAS NO EJECUTADAS...»*
  - `~/Dev/jam/AGENTS.md`:
    Todos los comandos documentados exigen la bandera de forma repetitiva:
```bash
oracle-aceptacion  --proyecto medidas --confiar-escalares
oracle-diferencial --proyecto medidas --confiar-escalares
oracle-mutar       --proyecto medidas --confiar-escalares
oracle-estudio     --proyecto medidas --confiar-escalares
oracle test        --proyecto medidas --confiar-escalares
```
  - `Dev/jam/tools/relevo.py` (`~/Dev/jam/tools/relevo.py:170`):
```python
["oracle-diferencial", "--proyecto", "medidas", "--confiar-escalares"]
```

### 6.2. Omisión silenciosa en `oracle juzgar` cuando la evidencia no incluye una relación
- **Problema**: `oracle juzgar` determina la aplicabilidad de una medida si las relaciones que lee están presentes como claves en el JSON de hechos. Si un sensor no emite una relación (por ejemplo, porque la lista está vacía y se omitió la clave en el serializador), las medidas asociadas no se evalúan, no aparecen en el reporte y no se marcan como error ni advertencia; simplemente disminuye el denominador `N de N` de medidas juzgadas.
- **Evidencia citada**:
  - `GUIA22.md` (`~/TestOracleEjemplo/GUIA22.md:560-566`):
    > *«⚠️ Un límite que conviene saber desde ya: una medida «aplica» si la evidencia trae su relación. Si el archivo no trae la relación `impacto`, las medidas que la leen no se juzgan y no aparecen en la lista — el veredicto dice «N de N» contando sólo las que aplicaron. Contá las líneas. (En Oracle es la tarea abierta `juzgar-omite`...)»*

### 6.3. Sobrecarga de proceso ("Ceremony & Overhead") para agentes y desarrolladores
- **Problema**: La exigencia de formalizar tareas, inicializar estructuras, escribir casos formales con ambas polaridades, matar mutantes y satisfacer medidas metalingüísticas genera una barrera de entrada elevada. Un agente externo con presupuesto de contexto acotado tiende a quedar atrapado en el ritual de proceso, recurriendo a casos triviales o medidas heredadas de proceso para conseguir un veredicto verde formal sin llegar a medir la lógica real del producto.
- **Evidencia citada**:
  - `POSTMORTEM-BATALLA-NAVAL-AGY.md` (`estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md:7-9`):
    > *«La versión con Oracle no midió reglas de batalla naval: guardó un caso sobre sintaxis de archivos, sin sensor del juego ni medidas propias. Con el checkout actual, su `oracle test --rapido` da verde aunque se destruya el JavaScript...»*
  - `Dev/lab/batalla_naval_test/el_porque_de_agy.md` (`~/Dev/lab/batalla_naval_test/el_porque_de_agy.md:11-22`):
    > *«Aproximadamente el 60% de la atención y llamadas a herramientas del agente se consumieron en interactuar con el entorno de Oracle: 1. Instalar la herramienta CLI... 2. Inicializar la estructura... 3. Gestionar tareas... 4. Redactar el caso formal con su sintaxis... 5. Ejecutar y depurar las verificaciones... 6. Registrar anotaciones...»*
  - `tareas/20260919-135054-primer-valor/TAREA.md` (`tareas/20260919-135054-primer-valor/TAREA.md:10-14`):
    > *«El README abre con init → nueva → test y “ya tiene quién lo juzgue”; la guía GUIA22 explica correctamente sensores y límites, pero su recorrido completo tiene 1.171 líneas y cuatro medidas.»*
