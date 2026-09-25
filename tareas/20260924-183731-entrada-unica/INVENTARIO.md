# Inventario de caminos de entrada a Oracle

Este inventario releva los cinco documentos analizados en la auditoría (§2.3) más la nueva guía `docs/de-cero.md` (batalla naval), con el objetivo de unificar la entrada a Oracle sin perder contenido valioso. Siguiendo el requerimiento estricto del protocolo, cada afirmación sobre lo que enseña un documento está respaldada por su cita textual entre comillas y su número de línea.

---

## 1. Qué enseña cada documento

### 1.1 `docs/02-de-cero-a-un-rojo.md`

Este documento enseña a recorrer el ciclo de desarrollo guiado por Oracle desde la instalación hasta obtener un fallo respaldado por evidencia y mutaciones en un proyecto de biblioteca:

1. **Instalación y versionado en tres contratos independientes:**
   - Enseña a instalar mediante uv: línea 14: `"uv tool install oracle-metalenguaje"`.
   - Enseña la semántica de las tres versiones reportadas por la herramienta: líneas 25-27: `"Tres versiones porque son tres contratos distintos, y envejecen por separado. La del paquete sube cuando se arregla una herramienta; la del **álgebra** cuando cambia qué significa una medida; la de la **sintaxis** cuando cambia cómo se escribe."`.
   - Enseña la razón técnica de preferir uv sobre pip frente a PEP 668 y el descubrimiento de LSP: líneas 29-33: `"> **Por qué uv y no pip.** En Arch, Debian 12+, Ubuntu 23.04+ y Fedora, pip install al Python del sistema falla con externally-managed-environment (PEP 668)... Pero para el editor eso **no alcanza**: los clientes de Emacs y VS Code buscan oracle-lsp en el PATH, y dentro de un venv sólo se ve con el venv activado."`.

2. **Inicialización y advertencia de proyecto vacío:**
   - Enseña a inicializar un proyecto: línea 38: `"$ oracle init biblioteca"`.
   - Enseña la herencia del catálogo base: líneas 51-52: `"Tres carpetas y un archivo. oracle.json viene con \"catalogo_base\": true: tu proyecto hereda las medidas universales de Oracle, que van a juzgar **tus** medidas."`.
   - Enseña que un proyecto sin mediciones no equivale a un verde validado: líneas 54-55: `"Un proyecto vacío conserva código de salida 0 para CI, con una advertencia: todavía no hay casos para verificar ni una medición del producto. No equivale a un corpus validado:"`.
   - Muestra la salida correspondiente: línea 59: `"VEREDICTO: SIN MEDICIÓN (advertencia: proyecto vacío: 0 medidas propias, 0 casos, 0 fixtures diferenciales)"`.

3. **Estructura y validación sintáctica de una medida:**
   - Enseña a crear una medida con andamio de plantilla: línea 65: `"$ oracle nueva documento.nombre_sigue_la_convencion"` y línea 69: `"La plantilla viene con los huecos en mayúsculas:"`.
   - Enseña los errores sintácticos de la plantilla sin completar: línea 84: `"✗ línea 5, columna 23: se esperaba segun en ['contrato', 'convencion', 'medicion', 'tanteo']; llegó 'SEGUN'"`.
   - Enseña el significado riguroso del origen del umbral: líneas 99-101: `"**segun no es decoración.** Dice de dónde salió el número, de un conjunto cerrado. Acá es contrato porque el cero no se midió: es una regla que alguien decidió. Si fuera un umbral puesto a ojo sería tanteo, y entonces la explicación pasa a ser obligatoria."`.
   - Enseña el concepto de punto ciego obligatorio: líneas 103-104: `"**alcance tampoco.** Es qué NO mira. Sin eso, un verde se lee como «está todo bien» cuando en realidad significa «está bien lo poco que miré»."`.
   - Enseña que una regla que no falla no mide: líneas 116-117: `"⚠ nunca se pone roja. Una medida que no puede fallar no mide nada — hace falta evidencia donde el defecto exista. Agregá un caso al corpus con esa evidencia."` y líneas 120-121: `"Está bien declarada **y la herramienta te avisa que todavía no sirve**. Es la primera vez que vas a ver la tesis del proyecto: una regla que nada puede romper es decoración."`.

4. **Prueba interactiva de la medida antes de escribir un caso formal:**
   - Enseña a probar la medida con filas directas por terminal: líneas 126-129: `"$ oracle medida probar catalogos/documento/documento.nombre_sigue_la_convencion.oracle \\ --con 'documento: nombre, sigue_convencion \"2026-08-31-GUIA-Convencion-v1.0.md\", true \"notas finales.md\", false'"` y línea 130: `"ROJO valor 1 (<= 0)"`.
   - Enseña qué constituye un rojo en Oracle y el rol de los testigos: líneas 138-139: `"**Eso es un rojo de Oracle.** No dice «falló la verificación»: dice el valor medido (1), contra qué se lo comparó (<= 0), **qué fila exacta lo produjo**, y qué no estaba mirando."`.
   - Enseña el valor argumentativo del testigo: línea 141: `"Un rojo sin testigos te obliga a creerle. Con testigos se puede discutir — y a veces la equivocada resulta ser la medida."`.

5. **Construcción de casos en el corpus y polaridades:**
   - Enseña la definición de caso: línea 146: `"Un caso es evidencia guardada que **pone a prueba la medida**."`.
   - Enseña a crear el andamio del caso: línea 149: `"$ oracle caso documento/001-un-nombre-fuera-de-convencion"`.
   - Enseña los valores cerrados obligatorios de los metadatos: líneas 155-157: `"etiqueta: deuda_de_diseño · falso_rojo · falso_verde · medida_correcta_conclusion_errada · verde_correcto"`, `"procedencia: construida · generada · observada"` y `"como_se_detecto: accidente · herramienta_ajena · mutacion · observacion · persona"`.
   - Enseña la exigencia de dos casos de distinta polaridad: línea 160: `"Escribí **dos**, uno de cada polaridad:"` (con `falso_verde` en línea 165 y `verde_correcto` en línea 175).
   - Enseña por qué la polaridad positiva es indispensable frente a mutaciones: líneas 182-184: `"**Los dos hacen falta, y no por simetría.** Sin el rojo, la medida nunca falla. Sin el verde, el mutador que le *quita el filtro* sobrevive: una medida sin donde marca todo, y si nunca viste un caso donde no debía marcar nada, no lo notás."`.

6. **Mutación de medidas y políticas universales de aceptación:**
   - Enseña qué evalúa la mutación de medidas en `oracle test`: líneas 204-206: `"**Los siete mutantes son el punto.** Oracle rompió tu medida de siete maneras distintas —le sacó el filtro, le aflojó el umbral, le dio vuelta un comparador— y comprobó que tus dos casos lo notaran. Los siete murieron: tus casos la fijan."`.
   - Enseña que las medidas universales juzgan el proyecto del usuario: línea 214: `"Ésas no son tus medidas: son las universales que heredaste, juzgándote."` (fallando `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` y `meta.toda_cantidad_comparada_tiene_unidad_derivable` en líneas 211-212).

7. **Declaración del sensor (nivel L-1) y alcance de las relaciones:**
   - Enseña a subsanar la falta de unidades declarando la relación en JSON: líneas 219-220: `"La segunda dice que comparaste un campo cuya **unidad** nadie declaró. Falta decir qué produce el sensor:"` y líneas 222-228 (el JSON con tipos y unidades).
   - Enseña que la relación y el sensor también declaran su alcance: líneas 230-231: `"Fijate que **la relación también declara su alcance**: la medida dice qué no mira, el sensor dice hasta dónde llega."`.
   - Enseña la inspección de relaciones: línea 234: `"$ oracle relaciones"`.
   - Enseña el uso de `oracle contexto`: líneas 243-245: `"Si en cualquier momento querés ver las relaciones, campos, escalares y medidas de tu proyecto en una sola salida, oracle contexto (o oracle contexto --compacto) reúne todo en un solo lugar."`.

8. **Honestidad del rojo por evidencia fabricada:**
   - Enseña por qué el marco penaliza la evidencia puramente construida: líneas 256-258: `"**Oracle acaba de atraparte inventando evidencia**, en un proyecto de cinco minutos. No es un falso positivo: es la diferencia entre «probé que mi regla funciona sobre casos que yo mismo diseñé» y «probé que atrapa algo que pasó de verdad»."`.
   - Enseña cómo cerrarlo legítimamente: líneas 260-261: `"Para cerrarlo hace falta evidencia observada: correr un sensor sobre documentos reales y guardar lo que devolvió. Hasta entonces el rojo es honesto y conviene dejarlo a la vista."`.

---

### 1.2 `docs/03-escribir-una-medida.md`

Este documento es la guía técnica de autoría del lenguaje y diseño de medidas, orientada a dotar de autonomía a quien detecta un defecto:

1. **Principio de autonomía y dualidad de representación:**
   - Enseña el propósito del metalenguaje: líneas 3-6: `"Esto existe para que **no haga falta pedirle permiso a nadie**. Todo el argumento del repositorio es que quien ve un defecto pueda escribir la regla que lo atrapa; si para eso hay que saber cómo está hecho el evaluador, el único que puede escribir reglas es quien lo escribió — y ese es exactamente el problema que veníamos a resolver."`.
   - Enseña la equivalencia entre superficie infija y almacenamiento: líneas 8-10: `"**La superficie es cómo se escribe; el JSON es cómo se guarda.** Este documento enseña a escribir medidas y casos directamente en su superficie de autoría (.oracle y .caso), que el sistema carga por igual sin paso de traducción."`.

2. **Instalación técnica y ejecución desde el checkout:**
   - Enseña los requisitos de runtime: línea 14: `"Requiere Python 3.11 o posterior y no tiene dependencias de runtime."`.
   - Enseña las alternativas de instalación: línea 18: `"uv tool install ."`, línea 25: `"uvx --from . oracle --help"` y línea 33: `"python -m venv .venv && . .venv/bin/activate"`.
   - Enseña a pasar el proyecto explícito: línea 45: `"oracle test --proyecto <tu-proyecto> --confiar-escalares"`.

3. **La regla metodológica de orden (el caso antes que la medida):**
   - Enseña la precedencia estricta del caso: línea 50: `"**Escribí el caso del corpus antes que la medida.** No es prolijidad:"`.
   - Enseña el riesgo de escribir primero la medida: línea 52: `"- una medida escrita primero se escribe para pasar, no para atrapar;"`.
   - Enseña la incapacidad de la herramienta de inferir intenciones: líneas 53-55: `"- la herramienta puede decirte si tu medida está mal *formada*, pero **no puede saber qué quisiste decir**. Una condición invertida —que selecciona lo que está bien en vez de lo que ofende— pasa todas las comprobaciones automáticas. El caso es lo único que lo detecta."`.

4. **Flujo de cuatro pasos apoyado en `oracle contexto`:**
   - Enseña la secuencia operativa: líneas 60-72: caso (`oracle caso`), contexto (`oracle contexto`), medida (`oracle nueva`, `oracle revisar`), verificación (`oracle test`).
   - Enseña los cinco componentes de `oracle contexto`: líneas 77-85: 1. Declaración de umbral, origen y defensa; 2. Relaciones, campos y tipos; 3. Operadores, comparadores y escalares; 4. Medidas existentes con sus alcances; 5. Regla de orden.
   - Enseña la eficiencia en tokens de la bandera `--compacto`: líneas 87-88: `"Con --compacto, la misma salida se emite en un quinto del texto (~1.600 tokens contra ~8.600 de correr los comandos que reemplaza)."`.
   - Enseña por qué el comando no reemplaza la guía: líneas 90-94: `"este documento explica la semántica del álgebra, el modelo homoicónico en JSON, las macros, los comparadores prohibidos (como la igualdad flotante) y las reglas de diseño. oracle contexto no reemplaza esas explicaciones: entrega el inventario concreto y vivo del proyecto para no tener que buscar campos o funciones a mano mientras escribís."`.

5. **Carga simultánea de formatos y restricción ASCII en identificadores:**
   - Enseña que superficie y JSON coexisten y colisionan si comparten id: líneas 98-101: `"El catálogo y el corpus cargan **superficie (.oracle, .caso) y .json por igual**: los archivos en superficie no necesitan traducirse a nada para funcionar. El mismo id en los dos formatos es un error que nombra los dos archivos — no gana ninguno, porque un ganador silencioso es una divergencia esperando."`.
   - Enseña las herramientas de traducción bidireccional: líneas 105-106: `"python tools/sintaxis.py --imprimir <archivo.json>"` y `"python tools/sintaxis.py --leer <archivo.oracle>"`.
   - Enseña la justificación técnica de restringir los IDs a ASCII para evitar problemas de normalización Unicode (NFC vs NFD): líneas 108-113: `"El id tiene gramática cerrada y **ASCII**: dominio.nombre para medidas y NNN-descripcion para casos... en Unicode dueño puede ser dos secuencias de bytes distintas que se dibujan idénticas (NFC contra NFD). Dos ids que nadie puede distinguir mirando son una divergencia silenciosa, y eso se cierra por gramática."`.

6. **Frontera de confianza y confinamiento de escalares (UDF):**
   - Enseña la bandera de confianza y el aislamiento en subproceso: líneas 117-119: `"Si el proyecto declara funciones en escalares.py, los comandos que cargan o evalúan su catálogo requieren --confiar-escalares. Esa bandera autoriza cargar código Python externo, pero Oracle lo ejecuta en un trabajador separado: el proceso principal sólo recibe metadatos y resultados JSON."`.
   - Enseña los límites precisos del sandbox (lo que sí detiene): líneas 121-122: `"Lo que ese confinamiento **sí** detiene: leer el CONTENIDO de archivos fuera del proyecto, escribir fuera, abrir red, crear procesos y usar ctypes."`.
   - Enseña los límites que el sandbox no detiene (metadatos del sistema de archivos y `os.stat`): líneas 124-128: `"Lo que **no** detiene, y conviene saberlo antes de correr un escalares.py ajeno: **los metadatos del sistema de archivos**. Una UDF puede preguntar si existe cualquier ruta, leer tamaños, permisos y fechas, y devolver eso como resultado. No es un descuido — os.stat no emite ningún evento auditable en CPython, así que el mecanismo no puede verlo..."`.
   - Enseña el criterio de diseño de datos vs UDFs: líneas 130-132: `"Si una UDF necesita más autoridad de la que el confinamiento da, no pertenece a una medida: generá ese dato antes y entregalo como evidencia."`.

7. **Uso y expansión de macros:**
   - Enseña el concepto de macro como azúcar sintáctico: líneas 142-144: `"**La mayoría de las medidas del catálogo están escritas como macro.** Son azúcar que expande a la forma canónica —oracle expandir <archivo> te muestra en qué—, así que el evaluador, la mutación y el inventario no se enteran de que existen."`.
   - Enseña el inventario de macros (`ninguno`, `ninguno-requiere`, `ninguno-par`, `peor`): líneas 158-163.
   - Enseña cómo `peor` consolida la tolerancia en un único lugar: línea 164: `"**peor recibe la tolerancia una sola vez** y genera con ella el filtro y el umbral"` y líneas 178-179: `"Antes había que escribir la tolerancia dos veces y nada las mantenía juntas — era el caso 012 del corpus, cerrado por construcción."`.

8. **Forma canónica, homoiconicidad y nivel L2:**
   - Enseña la gramática formal canónica: líneas 187-194 (`medida`, `de`, `donde`, `resumen`, `umbral`, `requiere`, `alcance`).
   - Enseña la regla del `requiere` para relaciones indispensables: líneas 201-202: `"requiere — declara qué relaciones de evidencia son indispensables para concluir. Si una relación requerida viene vacía o falta, la evaluación no emite un verde espurio sino SIN EVIDENCIA."`.
   - Enseña por qué los testigos no se declaran aparte y no hay composición: líneas 203-206: `"Y una que **no se declara**: los **testigos** son las filas que sobrevivieron al donde. No los calculás aparte — si lo hicieras, tendrías la misma condición escrita dos veces y nada que las mantenga sincronizadas. Tampoco se permite componer medidas entre sí (DECISION-002)..."`.
   - Enseña la homoiconicidad del JSON y el nivel L2 (medidas juzgando medidas): líneas 222-226: `"Porque **es homoicónico: el JSON es directamente el árbol de sintaxis abstracta (AST)**... Las medidas pueden hablar de medidas: es el nivel **L2** del proyecto. El propio catálogo de medidas se convierte en una relación (medida_en_uso), y se puede juzgar con el mismo álgebra de siempre..."`.
   - Enseña que los umbrales de igualdad están prohibidos: línea 240: `"(un umbral == no se usa y está prohibido por meta.ningun_umbral_de_igualdad)"`.
   - Enseña el operador `unir` para producto cartesiano de una relación consigo misma: línea 269: `"unir hace el producto de una relación consigo misma. Es como se comparan cosas de a pares: piezas que se clavan, documentos homónimos, las dos puntas de un relevo."`.

9. **Diagnóstico de errores y límites de la verificación:**
   - Enseña que acceder a un campo inexistente es error y no `False`: líneas 282-284: `"Comparar contra un campo que no existe **es un error**, no un False. Un False silencioso convertiría un nombre mal escrito en un verde, que es la peor falla posible acá."`.
   - Enseña que la herramienta no juzga intenciones: líneas 287-289: `"**Si la condición dice lo que quisiste decir.** Una medida que selecciona lo que está bien en vez de lo que ofende pasa todas las comprobaciones... La herramienta no lee intenciones."`.

10. **Consulta del manual, sombras y envejecimiento:**
    - Enseña `oracle manual` y la instalación de páginas de manual UNIX: líneas 299-304: `"oracle manual es la referencia del lenguaje armada de las declaraciones... oracle manual --instalar-man <dir> deja man oracle(1) y man oracle-segun(7) funcionando"`.
    - Enseña la política de medidas en sombra y su vencimiento a 90 días: líneas 305-315: `"Si heredás un catálogo y sale rojo en algo real que hoy no vas a arreglar, no apagues la medida: declarala en sombra en oracle.json, con desde y porque... meta.ninguna_sombra_envejece_sin_revisarse: si la sombra tiene más de 90 días, la medida falla... meta.ninguna_sombra_ya_en_verde: prohíbe tener en sombra medidas que ya dan verde."`.

11. **Separación arquitectónica entre sensor y álgebra:**
    - Enseña la división de responsabilidades: líneas 319-322: `"Si lo que querés medir no está en --relaciones, no se agrega acá: se agrega en el **sensor**, que vive con el proyecto que produce los datos. El sensor produce hechos y **no juzga**; el álgebra juzga y **no mira el mundo**. Mezclarlos es cómo se llega a un verificador que nadie puede discutir."`.

---

### 1.3 `docs/13-primer-valor.md`

Este documento enseña la ruta mínima para conectar un producto ejecutable real con Oracle y verificarlo de extremo a extremo sin rituales accesorios:

1. **Aclaración de confusiones iniciales frecuentes:**
   - Enseña a no confundir validar el catálogo con certificar el código del producto: línea 27: `"1. **Confundir la verificación de medidas con la certificación del producto.** Correr oracle test y ver una pantalla verde significa únicamente que el catálogo y el corpus son consistentes entre sí; no significa que el código fuente de la aplicación haya sido ejecutado ni que sus reglas de negocio funcionen."`.
   - Enseña que el subsistema de tareas es independiente del evaluador: línea 28: `"2. **Confundir el tracker con el motor de medición.** El subsistema oracle tarea es un gestor documental local en Git. Es completamente optativo: no hace falta inicializar tareas ni escribir bitácoras para formular medidas sobre un producto."`.

2. **Ruta mínima de 5 pasos:**
   - Enseña las etapas de la ruta de primer valor: líneas 30-35: `"1. Elegir una regla concreta del producto. 2. Extraer hechos observables estructurados (nivel L0). 3. Escribir una medida y casos de ambas polaridades en el catálogo propio. 4. Validar el catálogo con oracle test. 5. Juzgar una corrida real del producto con oracle juzgar."`.
   - Enseña la ubicación del ejemplo de referencia: línea 37: `"El ejemplo completo y reproducible se encuentra en el repositorio bajo ejemplo/primer-valor/"`.

3. **Extracción de hechos (L0) desde un sensor de producto:**
   - Enseña la regla de negocio elegida (colocación en Batalla Naval): línea 45: `"> **Regla de colocación:** Toda celda ocupada por un barco debe ubicarse dentro de la cuadrícula de 10×10 (coordenadas de fila y columna entre 0 y 9)."`.
   - Enseña cómo el producto debe emitir hechos estructurados en JSON: línea 49: `"Oracle no inspecciona el DOM ni adivina el estado interno del juego: el producto debe emitir hechos observables estructurados en formato JSON (una tabla o relación de filas)."`.
   - Enseña la pureza descriptiva de los hechos: línea 65: `"Cada hecho es un dato puro: no hay juicios de valor en el JSON, sólo hechos del mundo (nivel L0)."`.

4. **Configuración de proyecto aislado de reglas de dominio:**
   - Enseña a desactivar el catálogo base con `"catalogo_base": false`: línea 76: `"\"catalogo_base\": false,"`.
   - Enseña el motivo para apagarlo en etapas iniciales: líneas 81-83: `"> Si tu proyecto recién comienza y busca verificar reglas de negocio propias, podés fijar \"catalogo_base\": false para concentrarte exclusivamente en tus medidas de dominio sin evaluar políticas de proceso universales heredadas."`.

5. **Escritura de la medida orientada al defecto:**
   - Enseña el enfoque negativo de las medidas: línea 86: `"En Oracle, las medidas se enuncian buscando **lo que ofende** (el defecto), no lo que está bien:"`.
   - Enseña la medida canónica `colocacion.dentro_del_tablero`: líneas 89-97 (con `donde`, `umbral <= 0 segun contrato`, `requiere celda_ocupada` y `alcance`).

6. **Fijación de la medida mediante el corpus y mutación:**
   - Enseña el caso rojo (`falso_verde`): líneas 123-139: caso `001-desborde-tablero`, que mata el mutante `aflojar_umbral`.
   - Enseña el caso verde (`verde_correcto`): líneas 153-171: caso `002-colocacion-valida`, que mata el mutante `quitar_filtro`.
   - Enseña por qué dos casos no alcanzan para matar todos los mutantes de una condición compuesta: líneas 175-178: `"Los dos casos anteriores no alcanzan: dejaban seis mutantes vivos. El corpus incluye también fila -1, columna -1, columna 10 y una relación vacía (celda_ocupada: sin filas). Este último queda ROJO aunque el valor sea 0 porque incumple requiere. Los seis casos son construidos; sin-commit evita atribuirles un commit ficticio."`.

7. **Validación del catálogo con `oracle test`:**
   - Enseña la invocación del comando: línea 186: `"oracle test --proyecto ejemplo/primer-valor"`.
   - Enseña a interpretar el alcance del veredicto verde: líneas 230-231: `"> Este veredicto verde indica que **el catálogo satisface las verificaciones aplicables y los casos presentes**. No certifica en absoluto el estado del código del juego en este momento."`.

8. **Evaluación de corridas reales con `oracle juzgar`:**
   - Enseña a juzgar una corrida con defecto y comprobar el código de salida 1: líneas 244-250 (ejecución del script con `--defecto` y llamada a `oracle juzgar`), con salida en línea 256: `"VEREDICTO: 1 de 1 medidas en rojo"` y línea 259: `"Oracle rechaza la corrida y señala exactamente el testigo infractor: fila: 10."`.
   - Enseña a juzgar una corrida corregida y comprobar el código de salida 0: líneas 267-274, con salida en línea 276: `"✓ colocacion.dentro_del_tablero 0 (<= 0)"` e impresión explícita de `SIN MIRAR` (líneas 278-280).

9. **Clarificaciones conceptuales:**
   - Enseña la diferencia entre evidencia guardada y evidencia viva: líneas 288-291: `"- Los archivos en corpus/ (001-desborde-tablero.caso, etc.) son **evidencia histórica guardada** para comprobar las medidas... - Los archivos generados por el sensor (/tmp/hechos-*.json) son **evidencia viva de una corrida particular**."`.
   - Enseña cuándo usar un simple `assert` y cuándo aporta valor Oracle: líneas 295-300: `"- **Basta un assert** cuando estás programando una comprobación interna rápida en una función... o en una prueba unitaria clásica donde el mismo desarrollador escribe el código y el test. - **Aporta Oracle** cuando: 1. **Hay riesgo de Goodhart:** Quien escribe el código (por ejemplo, un LLM o agente) tiende a adaptar el test para que dé verde; en Oracle las medidas están desacopladas y custodiadas por mutación obligatoria. 2. **Se necesita explicitar el punto ciego:** Un assert que pasa produce silencio; una medida de Oracle que pasa concluye enumerando su alcance... 3. **Auditoría de artefactos en caja negra:** Querés evaluar la validez de los datos producidos por un proceso sin acoplarte a cómo está implementado el generador por dentro."`.
   - Enseña nuevamente la independencia del subsistema de tareas: línea 303: `"La gestión de tareas (oracle tarea init, oracle tarea nueva, etc.) no es un requisito previo para usar medidas ni para juzgar hechos."`.

---

### 1.4 `docs/tutorial-practico.md`

Este documento es el tutorial exhaustivo de programación con Oracle, orientado a enseñar el lenguaje combinando teoría de álgebra de datos con ejemplos de producción:

1. **Definición de Oracle y propósito del tutorial:**
   - Enseña la orientación práctica del texto: líneas 4-8: `"Este es distinto a propósito: es un tutorial — aprender haciendo, de lo más simple a lo más compuesto, con ejemplos reales tomados del propio repositorio y de un proyecto que ya lo usa en producción (Jam, un plugin de Unreal Engine)... este documento responde «¿cómo escribo la primera medida, y la segunda, y la que necesita algo más complicado?»."`.
   - Enseña qué es Oracle como lenguaje de datos: líneas 20-24: `"Oracle es un **lenguaje de datos** (no una biblioteca de funciones) para escribir medidas: reglas que toman hechos sobre lo que se construyó, calculan un número, lo comparan contra un umbral, y si el umbral se viola, señalan exactamente qué filas lo violaron. Las medidas y los casos se escriben en una superficie legible y se guardan como JSON —son datos, no código— y por eso se pueden inspeccionar, mutar, contar y medir con las mismas herramientas que mide cualquier otra cosa."`.

2. **El modelo mental de tres niveles y el veredicto acotado:**
   - Enseña la jerarquía L0, L1 y L2: líneas 34-36: `"L0 evidencia los HECHOS crudos"`, `"L1 medidas enunciados SOBRE L0"` y `"L2 medidas enunciados SOBRE L1"`.
   - Enseña que L2 no requiere mecanismos especiales: líneas 39-42: `"Lo importante: **L2 no necesita mecanismos nuevos**. Una medida (L1) es un dato, así que el catálogo de medidas es una relación más... y se puede medir con el mismo álgebra que mide piezas o eventos. Ese es el sentido de «metalenguaje»: no hay una capa especial para «medir la medición»."`.
   - Enseña qué produce una medida: líneas 51-54: `"Una medida no produce \"verdad\": produce un **veredicto acotado** — un número, si pasó o no, las filas que lo explican (testigos), y una declaración explícita de qué NO mira (alcance). Ningún veredicto se presenta sin su alcance: por diseño, Oracle no permite escribir una medida que diga «todo bien» sin decir también qué no miró."`.

3. **Anatomía formal y reglas de validación:**
   - Enseña la plantilla canónica: líneas 62-74 (con `medida`, `de`, `unir`, `donde`, `agrupar`, `resumen`, `umbral`, `requiere`, `alcance`).
   - Enseña las tres reglas duras de validación: líneas 89-91: `"1. Una medida sin defensa del umbral no carga, y una medida sin alcance no carga."`, `"2. Un umbral de igualdad (==) está prohibido."`, `"3. Si una medida declara requiere <relacion>, la relación no puede faltar ni venir vacía. Si no hay evidencia requerida, la evaluación devuelve SIN EVIDENCIA y no un verde espurio."`.
   - Enseña que los testigos son exactamente el filtro del `donde`: líneas 131-135: `"los testigos no se declaran aparte. Los testigos —las filas que se muestran cuando la medida da rojo, para que alguien pueda mirar el defecto— son exactamente las filas que sobrevivieron al último donde. No hay una segunda función que las calcule, porque escribir la misma condición dos veces es exactamente cómo se desincroniza"`.
   - Enseña la prohibición de composición de medidas (`DECISION-002`): línea 137: `"Tampoco hay composición de medidas (DECISION-002): una medida no puede invocar el resultado de otra medida. Cada medida juzga hechos directos del dominio."`.

4. **Los cinco operadores del álgebra y sus reglas estrictas:**
   - Enseña la clausura de relaciones: líneas 141-143: `"Toda la sintaxis sale de combinar **cinco operadores**. Cada uno toma filas (o hace de fuente) y devuelve filas: esa clausura es lo que permite encadenarlos sin casos especiales."` (`de`, `donde`, `unir`, `agrupar`, `resumen` en líneas 148-152).
   - Enseña los tres accesores de datos: líneas 178-183 (`campo` como `a.volumen`, `hecho` como `hecho(a)`, `col` como `col(reales)`).
   - Enseña que el tipo booleano no es numérico: líneas 196-197: `"bool no es número. true == 1 da error acá, aunque en Python valga. Sólo suma y promedio tratan un booleano como indicador 0/1, y de forma explícita."`.
   - Enseña la prohibición estricta de igualdad sobre números de punto flotante: líneas 198-201: `"Igualdad exacta sobre flotantes está PROHIBIDA, tanto en una expresión como en el umbral final. x == 3.0 no carga. La razón: 0.1 + 0.2 != 0.3 en punto flotante, y una medida que compare así puede decir verde sin que nadie se entere."`.
   - Enseña la tipificación estricta en comparaciones: líneas 202-203: `"Los dos lados de una comparación tienen que ser del mismo tipo. Comparar un número contra texto es error de álgebra, no false."`.
   - Enseña que el agregado `contar` no evalúa su argumento: líneas 213-214: `"contar es especial: **no evalúa la expresión**, sólo cuenta filas — por eso la convención es escribir resumen contar(1) (el 1 es un relleno que nunca se mira)."`.
   - Enseña el comportamiento del producto cartesiano con `unir`: líneas 226-233 (manejo de pares duplicados y reflexivos `a == b`).
   - Enseña a expresar la ausencia sin usar valores `null`: líneas 237-253: `"agrupar — cómo se expresa la AUSENCIA sin usar null... resuelve algo que en SQL pide un LEFT JOIN con nulos — y acá **no hay nulos**... El truco: se agrupa sobre el PRODUCTO sin filtrar primero, y se agrega con suma sobre un predicado booleano... Sin necesitar un concepto de nulo."`.
   - Enseña la desaparición de los alias tras agrupar: líneas 262-264: `"Después de agrupar, las filas ya NO tienen los alias originales (m, i desaparecen: se consumieron en el resumen). Las claves y agregados derivados se leen directamente por su nombre o con col(nombre)."`.

5. **Macros y resolución del caso histórico 012:**
   - Enseña las macros del lenguaje (`ninguno`, `ninguno-par`, `peor`): líneas 277-280.
   - Enseña cómo `peor` soluciona la desincronización de tolerancias del caso 012: líneas 311-315: `"Fijate el problema que resuelve peor: escrita a mano, la tolerancia (1.0) aparecería DOS veces — una en el donde que filtra («¿superó 1 cm?») y otra en el umbral («¿el peor caso está por debajo de 1 cm?») — y nada garantiza que sigan sincronizadas si alguien cambia una y no la otra. Ese fue un defecto real del proyecto (caso 012 del corpus). peor recibe la tolerancia **una sola vez** y genera las dos apariciones desde ahí."`.
   - Enseña que la forma canónica sigue siendo válida cuando las macros no encajan: líneas 350-352: `"Las macros no son un embudo... Si tu caso no encaja en ninguna macro, la forma canónica sigue siendo 100% válida. El ejemplo de colocacion.interpenetracion en §5.3 usa unir sobre DOS relaciones distintas (pieza y vecina) y no tiene macro que lo cubra"`.

6. **Seis ejemplos reales de producción:**
   - Enseña seis patrones reales: líneas 358-452:
     - 5.1 Conteo simple: `proceso.test_con_mutante_que_lo_mata` (línea 362).
     - 5.2 Magnitud con UDF: `peor snap.yaw` usando `desvio_de_paso` (línea 368).
     - 5.3 Comparación de relaciones distintas con `unir`: `colocacion.interpenetracion` (línea 386).
     - 5.4 `unir` sin `donde` resumiendo con `min` y umbral `>`: `snap.comparte_cara` (línea 406).
     - 5.5 `agrupar` y aritmética ordinal con `mas`: `simulacion.la_traza_no_tiene_huecos` (línea 419) y líneas 433-435: `"mas es una escalar del núcleo (+1) — así se expresa aritmética sobre un campo ordinal (t), porque una relación es una bolsa sin orden: «consecutivo» se vuelve aritmética sobre el campo, no una propiedad implícita del almacenamiento."`.
     - 5.6 Nivel L2: medida sobre medidas: `meta.toda_medida_esta_fijada` juzgando la relación `medida_en_uso` (líneas 440-452).

7. **Creación y registro de funciones escalares (UDF) en Python:**
   - Enseña a definir UDFs con `@escalar` declarando tipo y unidad: líneas 462-484: funciones `volumen`, `desvio_de_grilla` y `penetracion`.
   - Enseña los límites de conocimiento del álgebra: líneas 458-460: `"El álgebra no sabe geometría, ni de grillas, ni de nada de un dominio particular — a propósito. Lo que sí sabe hacer es llamar funciones **declaradas**, con nombre, aridad y unidad..."`.
   - Enseña los requisitos de seguridad y la bandera `--confiar-escalares`: líneas 496-499: `"Es **código Python con los mismos permisos que el proceso**. Por eso ninguna herramienta la ejecuta salvo que se pase explícitamente --confiar-escalares."`.

8. **Metodología del corpus, taxonomía de etiquetas y casos sin medida:**
   - Enseña la primera regla del repositorio: línea 505: `"La primera regla del repositorio: el caso del corpus se escribe ANTES que la medida."`.
   - Enseña las cinco etiquetas posibles: líneas 567-574: `falso_verde`, `falso_rojo`, `verde_correcto`, `deuda_de_diseño`, `medida_correcta_conclusion_errada`.
   - Enseña la necesidad matemática de `verde_correcto`: líneas 577-581: `"Con contar y umbral <= 0, una medida sin la evidencia positiva **siempre puede pasar vaciando la relación** — quitarle el filtro a una medida sólo se nota si hay filas que NO ofenden y que deberían seguir dando verde... Es lo mismo que evaluar un clasificador únicamente con ejemplos positivos."`.
   - Enseña los estados para casos que no tienen medida asignada (`abierto`, `resuelto`, `limite_humano`): líneas 585-593, e ilustra el caso histórico `004-testigos-duplicados` resuelto por construcción del lenguaje en líneas 596-616.

9. **Desarrollo de un proyecto completo y uso como biblioteca:**
   - Enseña a construir un proyecto de gestión de tareas desde cero: líneas 622-725.
   - Enseña la regla ASCII para nombres de archivos y normalización NFC/NFD: líneas 727-729.
   - Enseña el rol complementario de `oracle contexto`: líneas 741-746: `"Por qué oracle contexto complementa este tutorial en vez de acortarlo: este tutorial enseña a pensar una medida... oracle contexto no explica nada de eso: da la fotografía viva y concreta del proyecto en el que estás trabajando."`.
   - Enseña a evaluar hechos desde código Python con la clase `Motor`: líneas 754-761: `"from oracle_metalenguaje import Motor ... motor = Motor.desde_proyecto(\"mi-proyecto\") ... informe = motor.evaluar(...) ... print(informe.ok)"`.

10. **Catálogo de comandos CLI, políticas de sombra, errores frecuentes y glosario:**
    - Enseña la tabla exhaustiva de comandos de Oracle: líneas 768-788.
    - Enseña la configuración de medidas en sombra y su envejecimiento vigilado a 90 días: líneas 797-824.
    - Enseña la tabla de diagnósticos y soluciones de errores frecuentes: líneas 830-844.
    - Enseña un glosario completo con 16 definiciones formales: líneas 850-867.

---

### 1.5 `docs/de-cero.html`

Este documento es una página web visual y editorial que enseña el flujo de trabajo en 9 pasos interactivos mediante el ejemplo de un runner de pruebas de software:

1. **Presentación editorial y promesa técnica:**
   - Enseña la meta en 60 líneas de código y dos correcciones automáticas: líneas 222-224: `"Nueve pasos hasta un proyecto verde. Al final son 60 líneas, y dos de las cosas que vas a ver son la herramienta corrigiéndote. Todo lo que sigue es la salida textual de correr esto con 0.6.0."`.

2. **Paso 1: Instalación y desacoplamiento de versiones:**
   - Enseña la instalación y versionado: líneas 231-237: `"$ uv tool install oracle-metalenguaje"`, `"$ oracle --version"` y la nota explicativa: `"Cero dependencias. Son dos versiones distintas a propósito: lo que una medida significa no envejece igual que cómo se escribe."`.

3. **Paso 2: Inicialización e impacto del catálogo base:**
   - Enseña a crear el proyecto: línea 245: `"$ oracle proyecto init"`.
   - Enseña el alcance del catálogo base heredado: líneas 248-251: `"Desde este momento <strong>34 medidas ya te obligan</strong>. Vienen del catálogo base y juzgan cómo escribís las tuyas: que declaren su umbral, de dónde salió el número, y qué no miran. No son 57 —ése es el catálogo entero— porque 20 sólo obligan a Oracle y no viajan a tu proyecto."`.

4. **Paso 3: El caso antes que la medida y el problema del lazo cerrado:**
   - Enseña a escribir el caso primero: línea 265: `"$ oracle caso nuevo pruebas/001-paso-sin-afirmar"`.
   - Enseña la justificación metodológica: líneas 260-263: `"Es el orden que importa y el que cuesta respetar. Si la medida se escribe primero, el caso termina diciendo lo que la medida ya hace: no la prueba, la describe. El defecto de este ejemplo es el problema del lazo cerrado en miniatura: <strong>una prueba que pasó sin afirmar nada.</strong> Pasa igual con la función borrada."`.
   - Enseña que el caso existe antes que la regla: líneas 280-281: `"La medida que el caso reclama todavía no existe, y está bien: el caso describe el defecto, no la regla."`.

5. **Paso 4: Declaración de la medida:**
   - Enseña a redactar la medida `pruebas.ninguna_pasa_sin_afirmar`: líneas 291-300 (con macro `ninguno`, `de prueba p`, `donde p.paso == true y p.aserciones == 0`, `umbral <= 0 segun contrato`, `alcance`).
   - Enseña el rol del filtro y la obligatoriedad del alcance: líneas 301-303: `"El donde selecciona lo que ofende, no lo que está bien. Y el alcance es obligatorio: sin él, un verde se lee como «está todo bien», y ninguna medida ve todo."`.

6. **Paso 5: Detección temprana de condiciones unilaterales con `oracle revisar`:**
   - Enseña a revisar la medida aislada: línea 311: `"$ oracle revisar catalogos/pruebas/pruebas.ninguna_pasa_sin_afirmar.oracle"`.
   - Enseña la advertencia emitida cuando la medida no puede ponerse en verde: líneas 321-322: `"⚠ nunca se pone verde. Probablemente la condición esté invertida: el donde tiene que seleccionar lo que OFENDE, no lo que está bien."`.
   - Enseña por qué una regla que siempre falla es inválida: líneas 323-325: `"La medida está bien: lo que falta es un caso verde. Sin él nadie comprobó que la medida sepa no dispararse — y una regla que siempre da rojo tampoco mide."`.

7. **Paso 6: Incorporación del caso verde:**
   - Enseña a escribir el caso `002-todas-afirman` con etiqueta `verde_correcto`: líneas 332-343.
   - Enseña la discriminación precisa del predicado: líneas 344-345: `"La tercera fila tiene cero aserciones y no ofende: falló, y eso ya se ve. Lo que la medida persigue es el par «pasó y no afirmó»."`.

8. **Paso 7: Freno del catálogo base a la evidencia fabricada y sin unidades:**
   - Enseña la salida de `oracle test`: líneas 353-363: reporta 11 mutantes muertos, 0 vivos, pero veredicto ROJO por fallas en aceptación: `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` y `meta.toda_cantidad_comparada_tiene_unidad_derivable`.
   - Enseña la causa del bloqueo: líneas 364-366: `"La mutación ya está en cero: los dos casos fijan la medida. Lo que falta es lo que el catálogo base exige de cualquiera — que al menos un caso venga de una corrida real, y que la cantidad que comparás tenga unidad declarada."`.

9. **Paso 8: Declaración de unidades y alcance de la relación:**
   - Enseña a declarar la estructura en `relaciones/prueba.json`: líneas 374-382 (tipos y unidades `aserciones`, `sin_unidad`).
   - Enseña por qué comparar sin unidades es deficiente y el alcance del sensor: líneas 383-385: `"Comparar p.aserciones == 0 sin decir que se miden aserciones es comparar un número con otro número. La relación también declara su punto ciego: el sensor tampoco ve todo."`.

10. **Paso 9: Veredicto VERDE y síntesis de archivos:**
    - Enseña la confirmación final de `oracle test`: líneas 393-404: aceptación en verde, mutación en cero y políticas meta superadas.
    - Enseña el balance del proyecto: líneas 405-409: 5 archivos (`.oracle`, 2 `.caso`, `relaciones/prueba.json`, `oracle.json`) sumando 60 líneas en total.

11. **Epílogo: Lo que el verde dice y lo que no dice:**
    - Enseña qué certifica el verde: líneas 417-419: `"Dice que hay una regla escrita, que un defecto real la pone en rojo, que un caso sano la deja en verde, y que los once mutantes de esa regla mueren contra esos dos casos: no se puede reescribir la medida de otra forma sin que el corpus lo note."`.
    - Enseña qué NO certifica el verde: líneas 420-423: `"No dice que tus pruebas estén bien. La medida cuenta aserciones; una aserción que siempre es verdadera cuenta igual que una que discrimina. Eso está escrito en su alcance, y es lo primero que hay que leer de una medida que no escribiste."`.
    - Enseña el siguiente paso real hacia el sensor vivo: líneas 424-426: `"El siguiente paso real no es escribir más medidas: es conectar el sensor. Mientras la evidencia se escriba a mano, esto prueba que el catálogo es coherente — no que tu proyecto esté bien."`.

---

### 1.6 `docs/de-cero.md`

Este documento es la nueva guía didáctica que enseña a verificar un desarrollo completo de software (Batalla Naval en el navegador) programado en colaboración con un modelo de lenguaje (LLM), utilizando Oracle como árbitro independiente:

1. **Destinatario y premisa fundamental:**
   - Enseña el perfil del lector: líneas 3-5: `"Esta guía es para alguien que recién empieza a programar y programa con un modelo de lenguaje: le pedís el código, lo probás y seguís. Vamos a hacer una batalla naval que corre en el navegador y, sobre todo, vamos a responder una pregunta que el juego solo no puede contestar: **¿cumple las reglas?**"`.
   - Enseña que no se requiere experiencia previa en programación: líneas 7-8: `"No hace falta saber programar. Hace falta paciencia para leer lo que el modelo te devuelve y ganas de preguntar «¿cómo sé que esto está bien?»."`.
   - Enseña el compromiso de veracidad de la guía: líneas 10-12: `"El recorrido y las explicaciones están escritos. Las salidas de terminal marcadas como *pendiente* se completan con corridas reales cuando el ejemplo ejemplo/batalla-naval/ quede verde en el repositorio (tarea de-cero-naval). Ninguna salida de esta guía se escribe a mano."`.

2. **Alcance del juego y catálogo de reglas:**
   - Enseña qué se va a construir: líneas 16-18: `"Un juego de batalla naval en un tablero de 10 por 10. Cada jugador tiene cinco barcos: un portaaviones de 5 casillas, un acorazado de 4, un crucero de 3, un submarino de 3 y un destructor de 2. En total, 17 casillas por flota. Se dispara por turnos y gana quien hunde toda la flota del otro."`.
   - Enseña el papel del catálogo de Oracle: líneas 20-21: `"Y al lado del juego, un **catálogo de reglas** escritas en Oracle que miran cada partida y dicen si se respetaron, con la prueba en la mano cuando no."`.

3. **Arquitectura web elemental y rol del sensor:**
   - Enseña el reparto de responsabilidades en la web (`index.html`, `css/…`, `js/…`): líneas 25-32.
   - Enseña cuál es el archivo clave del cliente: líneas 33-34: `"Del JavaScript nos importa un archivo: el que **cuenta lo que pasó** en la partida. Lo vemos más abajo."`.

4. **Interacción con el modelo de lenguaje y el problema del lazo cerrado:**
   - Enseña el prompt preciso para solicitar el juego: líneas 40-45.
   - Enseña la brecha entre que un juego funcione y que sea correcto: líneas 47-49: `"Cuando te devuelva el código, abrí index.html en el navegador y jugá una partida. Si anda, **todavía no sabés si está bien**. Sabés que anda. Son cosas distintas, y el resto de la guía es sobre esa diferencia."` y línea 51: `"## El problema: un juego que anda no es un juego correcto"`.
   - Enseña el sesgo de confirmación al pedir tests al mismo modelo: líneas 61-63: `"Si le pedís al mismo modelo que escriba el juego y también los tests, los tests van a confirmar lo que el modelo ya creía. Por eso las reglas van **aparte**, en un lenguaje hecho para eso, y miran lo que el juego hizo, no lo que el juego cree que hizo."`.
   - Enseña el incidente histórico real del agente engañado por un falso verde: líneas 65-67: `"Esto pasó de verdad. Un agente construyó una batalla naval «con Oracle» y oracle test dio verde. El catálogo estaba vacío: el verde validaba la sintaxis de un archivo, no el juego. Está contado en [Por qué Oracle](por-que.html). Desde entonces, un proyecto sin medidas sale sin medición, no verde."`.

5. **El sensor: que el juego cuente lo que pasó sin juzgar:**
   - Enseña la función del sensor: líneas 71-73: `"La idea central: **el juego no se juzga a sí mismo, cuenta lo que pasó.** Mientras se juega, un archivo anota cada hecho en filas planas, sin opinar. En el ejemplo ese archivo es js/trace.js, y anota tres cosas:"`.
   - Enseña las tres relaciones del juego (`celda_barco`, `tiro`, `partida`): líneas 75-80.
   - Enseña el formato JSON resultante: líneas 81-89.
   - Enseña la instrucción exacta a darle al modelo: líneas 91-93: `"Si trabajás con un modelo, **pedile esto explícitamente**: «agregá un registro que anote cada casilla de barco, cada tiro y el resultado final, y que lo descargue como JSON». Es lo que después vas a juzgar."`.

6. **Instalación y primera regla:**
   - Enseña los comandos de inicio: líneas 100-103: `"uv tool install oracle-metalenguaje"`, `"oracle init reglas-naval"`, `"oracle test"`.
   - Enseña la salida esperada en proyecto vacío: líneas 106-107: `"Un proyecto recién creado sale **sin medición**: todavía no hay ninguna regla, y Oracle no lo disfraza de verde."`.
   - Enseña la medida `naval.barcos_dentro_del_tablero`: líneas 113-120.
   - Enseña el significado pedagógico de cada elemento: líneas 124-131 (`ninguno`, `de`, `donde`, `umbral <= 0 segun contrato`, `ambito universal`, `alcance`).

7. **El rol de los casos y la mutación:**
   - Enseña a probar la regla antes de confiar en ella con casos rojo y verde: líneas 135-138.
   - Enseña qué es un mutante: líneas 144-147: `"Oracle no se conforma con que tus casos pasen. Debilita cada regla a propósito: afloja el umbral de 0 a 1, invierte una comparación, le quita el filtro. A cada versión debilitada la llama **mutante**. Si algún caso nota la diferencia, el mutante muere. Si ninguno la nota, esa parte de la regla no la está cuidando nadie."`.
   - Enseña la experiencia real con 11 reglas y 2 casos: líneas 149-152: `"El juego del ejemplo llegó con **11 reglas y 2 casos**. Medido el 2026-09-25, su oracle test salió **rojo por mutación**: la mayoría de los mutantes sobrevivían, porque dos casos no alcanzan para fijar once reglas. Un verde con dos casos habría sido otra vez el verde que no mide nada."`.
   - Enseña la fórmula de cobertura de mutantes: líneas 153-155: `"La cuenta es simple: cada regla necesita al menos un caso que la ponga roja cerca del borde y uno verde, para que aflojarla o dejarla sin filtro se note."`.

8. **Variedad de reglas y operadores avanzados:**
   - Enseña a comparar filas consecutivas con `unir` y aritmética: líneas 164-173: medida `naval.alternancia_turnos` usando `unir tiro t2` y `t2.turno == t1.turno + 1`.
   - Enseña el no solapamiento: líneas 178-180: `naval.barcos_sin_solapamiento`.
   - Enseña el uso de `agrupar` y `requiere`: líneas 181-185: `"naval.flota_reglamentaria usa agrupar para contar las casillas de cada jugador y exige exactamente 17. Además dice requiere celda_barco: si el juego no mandó ninguna casilla, la regla no sale verde, sale **sin evidencia**. Cero barcos no es una flota correcta, es un registro roto."`.
   - Enseña el operador `sin` para verificar ausencia: líneas 186-198: medida `naval.veracidad_impacto_positivo` usando:
     línea 192: `"sin celda_barco c donde c.jugador == t.receptor y c.fila == t.fila y c.columna == t.columna"`.
   - Enseña el inventario de las 11 reglas de la flota: líneas 200-203.

9. **Evaluación de partidas reales y retroalimentación con el LLM:**
   - Enseña a juzgar hechos reales con `oracle juzgar`: línea 210: `"oracle juzgar --con hechos_partida.json"`.
   - Enseña la interpretación de los bloques del informe: líneas 216-219: `"- **SIN MIRAR** junta los alcance de las reglas que se aplicaron: lo que el verde no garantiza."` y `"- **NO SE APLICARON** lista las reglas cuya relación no vino en el archivo. Si el juego se olvidó de anotar los tiros, las reglas de tiros no te dan un verde de regalo: aparecen acá."`.
   - Enseña a usar los testigos para corregir al modelo: líneas 221-224: `"Si una regla sale roja, el veredicto trae **testigos**: las filas exactas que ofendieron. Con eso le volvés a hablar al modelo: «el tiro del turno 14 se marcó como impacto y no había barco en esa casilla; corregilo»."`.

10. **Extensiones del juego y cinco consejos prácticos:**
    - Enseña tres reglas futuras pendientes: líneas 229-232 (continuidad de barcos, comprobación completa de hundimiento, IA sin visión oculta).
    - Enseña cinco consejos para programar con LLMs: líneas 238-243: 1. Que el juego cuente lo que pasa en filas planas; 2. No pedir reglas y código en la misma pasada; 3. Probar cada regla con caso rojo y verde; 4. Leer el alcance; 5. Devolver al modelo los testigos.

---

## 2. Qué se repite entre documentos

Al cruzar los seis textos surgen conceptos, explicaciones y patrones que se reiteran de forma total o parcial:

1. **«La superficie es cómo se escribe; el JSON es cómo se guarda» y homoiconicidad:**
   - `docs/03-escribir-una-medida.md`: línea 8: `"**La superficie es cómo se escribe; el JSON es cómo se guarda.**"`, y líneas 222-223: `"Porque **es homoicónico: el JSON es directamente el árbol de sintaxis abstracta (AST)**"`.
   - `docs/tutorial-practico.md`: línea 18: `"**La superficie es cómo se escribe; el JSON es cómo se guarda.**"`, y línea 95: `"En el disco (dentro de catalogos/), la medida se guarda como una lista JSON homoicónica que representa su AST directamente"`.
   - `docs/02-de-cero-a-un-rojo.md`: líneas 222-228 y `docs/de-cero.html`: líneas 374-382 muestran la estructura JSON homoicónica en disco para las declaraciones de relaciones.

2. **La regla metodológica estricta: el caso del corpus se escribe antes que la medida:**
   - `docs/03-escribir-una-medida.md`: línea 50: `"**Escribí el caso del corpus antes que la medida.** No es prolijidad:"`.
   - `docs/tutorial-practico.md`: línea 505: `"**La primera regla del repositorio: el caso del corpus se escribe ANTES que la medida.**"`.
   - `docs/de-cero.html`: líneas 260-261: `"Es el orden que importa y el que cuesta respetar. Si la medida se escribe primero, el caso termina diciendo lo que la medida ya hace: no la prueba, la describe."`.
   - `docs/de-cero.md`: línea 135: `"Una regla nueva puede estar mal escrita y dar verde siempre. Por eso, **antes** de usarla, se prueba con dos ejemplos que vos armás"`.
   - `docs/13-primer-valor.md`: línea 109: `"Una medida sin casos es una intención sin comprobar: podría estar invertida y pasar sin ser detectada."`.
   - `docs/02-de-cero-a-un-rojo.md`: líneas 116-121: `"Una medida que no puede fallar no mide nada — hace falta evidencia donde el defecto exista."`.

3. **La necesidad de dos polaridades en el corpus (`falso_verde` y `verde_correcto`) para matar mutantes:**
   - `docs/02-de-cero-a-un-rojo.md`: línea 160: `"Escribí **dos**, uno de cada polaridad:"` y líneas 182-184: `"Sin el rojo, la medida nunca falla. Sin el verde, el mutador que le *quita el filtro* sobrevive: una medida sin donde marca todo"`.
   - `docs/03-escribir-una-medida.md`: línea 280: `"nunca se pone verde | *probablemente la condición esté invertida*"` y líneas 291-292: `"comprueba que el corpus **fije** tu medida"`.
   - `docs/13-primer-valor.md`: línea 138 (`falso_verde`), línea 153 (`verde_correcto`) y líneas 171: `"Mata el mutante quitar_filtro"`.
   - `docs/tutorial-practico.md`: línea 540: `"Y uno **verde_correcto** — la otra polaridad, igual de necesaria:"` y líneas 577-581: `"Con contar y umbral <= 0, una medida sin la evidencia positiva **siempre puede pasar vaciando la relación**... Es lo mismo que evaluar un clasificador únicamente con ejemplos positivos."`.
   - `docs/de-cero.html`: líneas 323-324: `"La medida está bien: lo que falta es un caso verde. Sin él nadie comprobó que la medida sepa no dispararse"` y línea 364: `"La mutación ya está en cero: los dos casos fijan la medida."`.
   - `docs/de-cero.md`: líneas 136-137: `"uno donde tiene que ponerse **roja** (un barco en la fila 10) y otro donde tiene que quedar **verde** (todos dentro)."` y líneas 153-155: `"cada regla necesita al menos un caso que la ponga roja cerca del borde y uno verde, para que aflojarla o dejarla sin filtro se note."`.

4. **El rol obligatorio de `alcance` y de la justificación `umbral ... segun ... porque ...`:**
   - Presente de forma unánime en los seis documentos:
     - `docs/02-de-cero-a-un-rojo.md`: líneas 99-104.
     - `docs/03-escribir-una-medida.md`: líneas 198-200.
     - `docs/13-primer-valor.md`: líneas 100-103.
     - `docs/tutorial-practico.md`: líneas 84-87.
     - `docs/de-cero.html`: líneas 301-303.
     - `docs/de-cero.md`: líneas 127-132.
   - En todos se reitera la advertencia: sin `alcance`, un veredicto verde se malinterpreta como «está todo bien».

5. **Los testigos como filas que sobrevivieron al filtro del `donde` (sin cálculo por duplicado):**
   - `docs/02-de-cero-a-un-rojo.md`: línea 132: `"testigos (1) — las filas que ofenden, no un resumen:"`.
   - `docs/03-escribir-una-medida.md`: líneas 203-205: `"los **testigos** son las filas que sobrevivieron al donde. No los calculás aparte — si lo hicieras, tendrías la misma condición escrita dos veces y nada que las mantenga sincronizadas."`.
   - `docs/tutorial-practico.md`: líneas 131-135: `"Los testigos... son exactamente las filas que sobrevivieron al último donde. No hay una segunda función que las calcule, porque escribir la misma condición dos veces es exactamente cómo se desincroniza"`.
   - `docs/de-cero.md`: línea 221: `"el veredicto trae **testigos**: las filas exactas que ofendieron."`.

6. **Instalación con `uv tool install oracle-metalenguaje` y desacoplamiento de versiones:**
   - `docs/02-de-cero-a-un-rojo.md`: línea 14 y líneas 19-23.
   - `docs/03-escribir-una-medida.md`: línea 18 (`uv tool install .`).
   - `docs/de-cero.html`: líneas 231-235.
   - `docs/de-cero.md`: línea 100.
   - Tanto `docs/02-de-cero-a-un-rojo.md` como `docs/de-cero.html` explican la separación entre versión del paquete, versión del álgebra y versión de la sintaxis.

7. **El catálogo base y la regla de no admitir evidencia puramente fabricada:**
   - `docs/02-de-cero-a-un-rojo.md`: línea 211: `"✗ meta.la_medida_no_se_fija_solo_con_evidencia_fabricada 1 (<= 0)"` y línea 256: `"Oracle acaba de atraparte inventando evidencia"`.
   - `docs/de-cero.html`: línea 356: `"meta.la_medida_no_se_fija_solo_con_evidencia_fabricada"` y línea 365: `"que al menos un caso venga de una corrida real"`.

8. **La macro `ninguno` como azúcar sintáctico predominante:**
   - Explicada y ejemplificada en:
     - `docs/02-de-cero-a-un-rojo.md`: líneas 72-79 y 92-97.
     - `docs/03-escribir-una-medida.md`: líneas 146-155.
     - `docs/tutorial-practico.md`: líneas 284-292 y 668-676.
     - `docs/de-cero.html`: líneas 291-300.
     - `docs/de-cero.md`: líneas 114-120.

9. **La distinción entre validar el catálogo (`oracle test`) y juzgar una corrida del producto (`oracle juzgar`):**
   - `docs/13-primer-valor.md`: línea 27: `"Correr oracle test y ver una pantalla verde significa únicamente que el catálogo y el corpus son consistentes entre sí; no significa que el código fuente de la aplicación haya sido ejecutado ni que sus reglas de negocio funcionen."`, y paso a `oracle juzgar` en líneas 247 y 270.
   - `docs/de-cero.md`: líneas 65-67 (anécdota del catálogo vacío) y llamada a `oracle juzgar --con hechos_partida.json` en línea 210.
   - `docs/de-cero.html`: líneas 424-426: `"El siguiente paso real no es escribir más medidas: es conectar el sensor. Mientras la evidencia se escriba a mano, esto prueba que el catálogo es coherente — no que tu proyecto esté bien."`.

---

## 3. Qué sólo está en un documento (contenido exclusivo)

Cada documento posee elementos únicos que no aparecen en ninguno de los otros cinco:

### Exclusivo en `docs/02-de-cero-a-un-rojo.md`
1. **Prueba rápida al vuelo de medidas sin crear archivos de caso:**
   - Es el único texto que enseña el comando interactivo para pasar evidencia en línea de comandos: líneas 126-129: `"$ oracle medida probar catalogos/documento/documento.nombre_sigue_la_convencion.oracle \\ --con 'documento: nombre, sigue_convencion \"2026-08-31-GUIA-Convencion-v1.0.md\", true \"notas finales.md\", false'"`.
2. **Explicación explícita de las tres versiones del banner:**
   - Es el único que desglosa puntualmente las tres versiones (paquete, álgebra y sintaxis): líneas 19-23 y 25-27: `"Tres versiones porque son tres contratos distintos, y envejecen por separado. La del paquete sube cuando se arregla una herramienta; la del **álgebra** cuando cambia qué significa una medida; la de la **sintaxis** cuando cambia cómo se escribe."` (`de-cero.html` sólo muestra dos en su texto: álgebra y sintaxis).
3. **Dominio temático de biblioteca y nombres de archivo:**
   - Es el único que utiliza como caso pedagógico la nomenclatura de documentos Markdown en un vault (`documento.nombre_sigue_la_convencion`, líneas 65, 92-96).

### Exclusivo en `docs/03-escribir-una-medida.md`
1. **Frontera de confianza y auditoría del sandbox de escalares:**
   - Es el único documento que detalla cómo Oracle ejecuta UDFs en un proceso trabajador aislado (líneas 118-119), qué detiene exactamente (líneas 121-122) y el punto ciego de `os.stat` sobre metadatos del filesystem (líneas 124-128: `"os.stat no emite ningún evento auditable en CPython, así que el mecanismo no puede verlo — y está declarado en el docstring de nucleo/aislamiento/escalares.py con un test que lo fija."`).
2. **Justificación formal de IDs en ASCII estricto por colisión de normalización Unicode:**
   - Es el único que explica por qué los identificadores no admiten caracteres especiales, contrastando formas de normalización de Unicode: líneas 110-113: `"en Unicode dueño puede ser dos secuencias de bytes distintas que se dibujan idénticas (NFC contra NFD). Dos ids que nadie puede distinguir mirando son una divergencia silenciosa, y eso se cierra por gramática."`.
3. **Generación e instalación de páginas de manual UNIX (`man`):**
   - Es el único que enseña a instalar páginas `man` en el sistema: líneas 302-304: `"oracle manual --instalar-man <dir> deja man oracle(1) y man oracle-segun(7) funcionando"`.
4. **Métricas cuantitativas de adopción de macros en el catálogo:**
   - Es el único que presenta el conteo real de uso de macros: líneas 158-163 (tabla con 29 usos de `ninguno`, 4 de `ninguno-requiere`, 0 de `ninguno-par` y 0 de `peor`).
5. **Métricas comparativas de tokens de `oracle contexto`:**
   - Es el único que mide el ahorro en tokens para LLMs y editores: línea 64 y líneas 87-88: `"~1.600 tokens vs ~8.600"`.

### Exclusivo en `docs/13-primer-valor.md`
1. **Criterio formal: «¿Cuándo basta un assert y cuándo aporta Oracle?»:**
   - Es el único documento que analiza formalmente la conveniencia de Oracle frente a `assert` basándose en: 1. Riesgo de Goodhart en código asistido por LLMs; 2. Explicitud del punto ciego (`alcance`); 3. Auditoría en caja negra de artefactos: líneas 295-300.
2. **Separación explícita del tracker (`oracle tarea`):**
   - Es el único documento que advierte explícitamente no confundir el gestor de tareas documental con el motor de medición: línea 28: `"Confundir el tracker con el motor de medición. El subsistema oracle tarea es un gestor documental local en Git. Es completamente optativo"` y línea 303: `"La gestión de tareas... no es un requisito previo para usar medidas ni para juzgar hechos."`.
3. **Inicio deliberado con `"catalogo_base": false`:**
   - Es el único documento que recomienda explícitamente apagar el catálogo base en proyectos iniciales para verificar reglas de negocio puras sin verse bloqueado por políticas meta universales: líneas 81-83.
4. **Ejemplo ejecutable en Python (`colocador.py`) con comprobación de códigos de salida:**
   - Es el único que acompaña un script en Python invocable por terminal con banderas `--defecto` y `--exportar`, demostrando el código de salida 1 en fallo y 0 en éxito: líneas 244-273.
5. **Caso con relación vacía para probar incumplimiento de `requiere`:**
   - Es el único que incluye un caso donde la relación viene sin filas (`006-sin-celdas`, línea 177) para demostrar que la evaluación queda en ROJO con valor 0 por violar el contrato de `requiere` (línea 205).

### Exclusivo en `docs/tutorial-practico.md`
1. **Modelado de AUSENCIA sin valores nulos (`null`) mediante `agrupar`:**
   - Es el único documento que explica cómo resolver una consulta equivalente a un `LEFT JOIN` sin nulos mediante el producto cartesiano, agrupación y suma sobre predicados booleanos: líneas 237-253.
2. **Detalle sintáctico de los accesores del AST:**
   - Es el único que formaliza la tabla de equivalencias entre superficie y AST JSON para `campo` (`["campo", "a", "volumen"]`), `hecho` (`["hecho", "a"]`) y `col` (`["col", "reales"]`): líneas 178-183.
3. **Ejemplos del plugin Jam (Unreal Engine) y funciones geométricas de dominio:**
   - Es el único que incluye funciones UDF trigonométricas y de cálculo de volumen y penetración AABB (`volumen`, `desvio_de_grilla`, `penetracion` en líneas 462-484; `snap.yaw` en línea 368; `colocacion.interpenetracion` en línea 386; `snap.comparte_cara` en línea 406).
4. **Taxonomía de estados para casos sin medida:**
   - Es el único que categoriza los defectos sin regla activa en `abierto`, `resuelto` (por construcción de lenguaje) y `limite_humano` (líneas 585-593), y rescata el caso histórico `004-testigos-duplicados` (líneas 596-616).
5. **Oracle como biblioteca de Python (`Motor.desde_proyecto`):**
   - Es el único que muestra cómo integrar Oracle en un script de Python mediante la API de la clase `Motor`: líneas 754-761.
6. **Aritmética ordinal sobre relaciones con el operador `mas`:**
   - Es el único que presenta el operador núcleo `mas` (`mas(ultimo, 1)`) para validar secuencias temporales en bolsas sin orden: líneas 426 y 433-435.
7. **Comandos de gestión de bibliotecas y diagnóstico:**
   - Es el único que documenta los comandos `oracle biblioteca instaladas`, `oracle biblioteca verificar <ruta>`, `oracle biblioteca listar <ruta>` y `oracle diagnostico` en su tabla general: líneas 782-785.
8. **Glosario terminológico exhaustivo:**
   - Es el único que proporciona una tabla formal con 16 definiciones de conceptos nucleares: líneas 850-867.

### Exclusivo en `docs/de-cero.html`
1. **Formato web, diseño editorial y visualizador de código de editor:**
   - Es el único recurso maquetado en HTML/CSS responsivo con paleta de colores OKLCH, tipografías Archivo y JetBrains Mono, navegación superior y renderizado que simula pestañas de editor con numeración de líneas (`.pestana`, `.lineas`): líneas 15-203.
2. **Ejemplo pedagógico de runner de pruebas y conteo de aserciones:**
   - Es el único texto que utiliza la verificación de pruebas unitarias sin aserciones como caso de estudio (`pruebas/001-paso-sin-afirmar.caso`, `pruebas.ninguna_pasa_sin_afirmar.oracle` sobre la relación `prueba(nombre, aserciones, paso)`): líneas 265-279 y 289-300.
3. **Desglose cuantitativo del catálogo base (34 vs 57 medidas):**
   - Es el único que aclara cuántas medidas del catálogo base aplican al usuario (34) y cuántas quedan restringidas internamente a Oracle (20): líneas 248-251: `"Desde este momento <strong>34 medidas ya te obligan</strong>... No son 57 —ése es el catálogo entero— porque 20 sólo obligan a Oracle y no viajan a tu proyecto."`.
4. **Métrica de proyecto mínimo en 60 líneas de código:**
   - Es el único que sintetiza la estructura completa de un proyecto validado en exactamente 5 archivos y 60 líneas de código: líneas 405-409.

### Exclusivo en `docs/de-cero.md`
1. **Enfoque pedagógico centrado en programación asistida por LLMs:**
   - Es el único documento diseñado desde su título y bajada para guiar a un usuario que programa con IA («Tu primer juego con un LLM, y cómo saber si está bien», líneas 1, 3-8, 36-49).
2. **Anécdota del agente engañado por un falso verde en catálogo vacío:**
   - Es el único documento que relata el caso real donde un agente creyó verificar un juego naval obteniendo verde con un catálogo vacío: líneas 65-67: `"Esto pasó de verdad. Un agente construyó una batalla naval «con Oracle» y oracle test dio verde. El catálogo estaba vacío... Desde entonces, un proyecto sin medidas sale sin medición, no verde."`.
3. **Arquitectura web con sensor JavaScript del lado del cliente (`js/trace.js`):**
   - Es el único donde el sensor se ejecuta en el navegador web del usuario y permite descargar la evidencia directamente en un archivo JSON al concluir la partida: líneas 25-34, 71-80 y 81-89.
4. **Sintaxis y uso del operador `sin` para verificar ausencia:**
   - Es el único documento de los seis que enseña la sintaxis del operador `sin`: líneas 186-198, con la medida `naval.veracidad_impacto_positivo`:
     línea 192: `"sin celda_barco c donde c.jugador == t.receptor y c.fila == t.fila y c.columna == t.columna"`.
5. **Sección del reporte `NO SE APLICARON`:**
   - Es el único que explica la sección del veredicto que lista medidas cuyas relaciones requeridas no vinieron en la evidencia suministrada: líneas 218-219: `"- **NO SE APLICARON** lista las reglas cuya relación no vino en el archivo. Si el juego se olvidó de anotar los tiros, las reglas de tiros no te dan un verde de regalo: aparecen acá."`.
6. **Ciclo de retroalimentación entregando testigos al modelo de lenguaje:**
   - Es el único que articula el flujo de reparación con LLMs pasando las filas ofensivas: líneas 221-224: `"Si una regla sale roja, el veredicto trae **testigos**: las filas exactas que ofendieron. Con eso le volvés a hablar al modelo: «el tiro del turno 14 se marcó como impacto y no había barco en esa casilla; corregilo»."`, y línea 243: `"5. **Cuando algo sale rojo, pasale al modelo los testigos**, no una descripción vaga."`.
7. **El catálogo de 11 reglas de la Batalla Naval:**
   - Es el único que describe el conjunto completo de 11 reglas de lógica del juego naval (líneas 160-203).
8. **Los cinco consejos para colaborar con modelos:**
   - Es el único que formaliza las 5 directivas metodológicas para programar con modelos de lenguaje: líneas 238-243.

---

## 4. Conclusión para la unificación del camino de entrada

1. **La guía de entrada única debe ser `docs/de-cero.md`:** Su enfoque pedagógico centrado en la interacción humano-LLM y el desarrollo de un producto tangible en el navegador resuelve la principal confusión advertida en `docs/13-primer-valor.md`: separar la verificación interna del catálogo de la medición del producto vivo.
2. **Elementos indispensables a preservar e incorporar como referencias enlazadas:**
   - La frontera de confianza y auditoría del sandbox de escalares de `docs/03-escribir-una-medida.md`.
   - La justificación formal de por qué los IDs son ASCII (evitar colisiones NFC/NFD) de `docs/03-escribir-una-medida.md`.
   - La distinción formal de cuándo basta un `assert` y cuándo aporta Oracle de `docs/13-primer-valor.md`.
   - El modelado de ausencia sin `null` usando `agrupar` de `docs/tutorial-practico.md`.
   - La taxonomía de estados para casos sin medida (`abierto`, `resuelto`, `limite_humano`) y el glosario de `docs/tutorial-practico.md`.
   - El desglose de comandos interactivos (`oracle medida probar --con`) de `docs/02-de-cero-a-un-rojo.md`.
