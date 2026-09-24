# Aura y Oracle: Agentes generativos en motores de juego frente al problema del juicio determinista

**Fecha:** 2026-09-19  
**Autor:** agy  
**Estado:** Estudio de investigación para la tarea `20260919-134424-aura`  
**Lecturas previas requeridas:** `README.md`, `ESPECIFICACION.md` §0-3, `estudios/MCP-CONTRATO.md`, `~/Dev/jam/AGENTS.md` y `~/Dev/games/unreal/LyraGASP/docs/ORACLE.md`.

---

## 1. Qué es Aura

### 1.1 Origen, producto y modelo de integración
**Aura** ([tryaura.dev](https://www.tryaura.dev/)) es una plataforma de agentes de inteligencia artificial diseñada específicamente para el desarrollo de videojuegos en **Unreal Engine** y **Unity**. Fue creada por **Ramen VR** (el estudio fundado por Andy Tsen y Lauren Frazier, conocido por el MMO de realidad virtual *Zenith: The Last City* / *Zenith: Nexus*). Tras una fase de pruebas privadas y beta con socios de diseño, Aura alcanzó su versión 1.0 en septiembre de 2026.

A diferencia de los asistentes de código tradicionales orientados a texto o autocompletado en IDEs (como GitHub Copilot), Aura se presenta como un «agente de uso de editor» (*Editor-Use Agent*) capaz de interactuar directamente con el entorno de ejecución y autoría del motor de juego.

Su arquitectura se articula en tres piezas clave:
1. **Plugin para el motor (Unreal / Unity):** Se instala en el proyecto anfitrión y actúa como puente bidireccional. En Unreal se apoya en C++ y en el intérprete embebido de Unreal Python; en Unity se integra en el ciclo del editor de C#. Permite operar tanto en modo GUI dentro del editor abierto como en ejecuciones desatendidas (*headless* / commandlet).
2. **Soporte de Model Context Protocol (MCP):** Aura expone y consume herramientas mediante el estándar abierto MCP. Esto le permite vincularse de forma nativa con entornos de desarrollo externos como Claude Code, Cursor o terminales del sistema, evitando que el desarrollador quede atrapado en una ventana de chat aislada.
3. **Agentes especializados:**
   - **Telos:** Agente enfocado en la generación, edición y corrección de grafos de **Blueprints** en Unreal Engine. Resuelve cableado de nodos, llamadas a interfaces, funciones personalizadas y configuración de propiedades de red/replicación.
   - **Dragon Agent:** Agente ejecutor basado en Python que opera sobre la API interna del editor. Automatiza tareas masivas de manipulación de actores, limpieza de dependencias huérfanas, parametrización de materiales y configuración de escenas.
   - **Verification Agent:** Agente autónomo que promete compilar, empaquetar o lanzar sesiones de juego en el editor (PIE), ejecutar secuencias de prueba, monitorear fallos y corregir errores en un ciclo cerrado de retroalimentación (*agentic loop*).

### 1.2 Modelos subyacentes, precios y límites
Aura opera bajo un esquema comercial SaaS híbrido:
- **Auto Mode (Uso ilimitado):** Disponible en todos los planes de pago y durante la prueba gratuita de dos semanas. Utiliza modelos optimizados para tareas rutinarias y correcciones menores sin costo marginal por llamada, sujeto a límites de tasa de peticiones por minuto.
- **Créditos Premium:** Diseñados para modelos de frontera (*frontier models* como Anthropic Claude 3.5 Sonnet / Opus) o llamadas complejas que requieren ventanas de contexto extensas y razonamiento profundo (el llamado *Super mode*).

Estructura de precios (septiembre 2026):
- **Indie:** $20 USD / mes (incluye $15 USD de créditos premium mensuales). Auto Mode ilimitado, generación de prototipos 3D/audio, integración MCP.
- **Pro:** $40 USD / mes (incluye $60 USD de créditos premium mensuales). Límites de tasa más holgados, acceso al modo de máximo razonamiento (*Super mode*), compra de créditos adicionales bajo demanda.
- **Ultimate:** $200 USD / mes o $1.800 USD / año (incluye $335 USD de créditos premium mensuales). Máxima prioridad, límites de tasa corporativos y acceso a rutas de baja latencia para modelos de frontera (*Fast Opus*).

### 1.3 Lo que dicen frente a lo que muestran: la «verificación» bajo la lupa
La promesa central de mercadeo de Aura radica en que **«verifica su propio trabajo»** y «cierra el bucle de QA». Sin embargo, al examinar la documentación técnica, las guías de integración y las demostraciones públicas (en su canal oficial de YouTube y conferencias técnicas), emerge una distinción fundamental entre la narrativa comercial y la capacidad técnica real:

| Qué dice el material promocional | Qué muestran realmente las demos y la implementación |
|---|---|
| *«Prueba el juego de forma autónoma como un tester humano.»* | Lanza una sesión Play In Editor (PIE) o ejecuta un comando de automatización básico y monitorea si el proceso termina con código 0 o si se elevan excepciones no capturadas. |
| *«Detecta y repara bugs de lógica y jugabilidad.»* | Si el compilador de C++ falla o el compilador de Blueprints reporta pines desconectados/incompatibles, el agente toma la traza del error (*stack trace* / *compiler log*), reescribe el nodo o la función y vuelve a compilar hasta que el compilador no arroje errores. |
| *«Asegura que las mecánicas funcionen según el diseño.»* | Verificación predominantemente **sintáctica y de ausencia de caídas catastróficas** (*crash-free*). No hay modelado de invariantes de diseño ni comprobación semántica de estados del juego (por ejemplo, si una animación de recarga cancela el salto incorrectamente, o si un actor quedó flotando 2 milímetros sobre el suelo). |
| *«Entorno sandbox seguro.»* | Aislamiento a nivel de copias temporales de archivos o ramas locales de control de versiones antes de aplicar un lote de comandos Python en el editor. |

En resumen: la «verificación» de Aura es un bucle de **auto-corrección sintáctica y reactiva ante fallos fatales de ejecución**. Carece de un marco formal de medición de evidencia y de una definición explícita de puntos ciegos.

---

## 2. Qué hay alrededor en el ecosistema

El auge de los agentes aplicados a motores de videojuegos se ha acelerado notablemente entre 2025 y 2026, con el protocolo **MCP (Model Context Protocol)** convirtiéndose en la capa de interoperabilidad dominante.

### 2.1 Ecosistema en Unreal Engine
1. **Unreal MCP Oficial (Epic Games, UE 5.8+):**  
   A partir de Unreal Engine 5.8 (versión sobre la que opera el proyecto Jam), Epic Games introdujo soporte experimental nativo para servidores MCP dentro del editor (`Unreal MCP` y `All Toolsets`). Permite a clientes MCP externos (como Claude Code, Cursor o Windsurf) invocar herramientas directamente sobre el subsistema de activos, jerarquías de nivel, materiales y manipulación básica de Blueprints vía llamadas JSON-RPC locales (típicamente sobre HTTP en el puerto 8000).
2. **Servidores MCP Comunitarios y Precedentes:**  
   - Proyectos de código abierto como `chongdashu/unreal-mcp`, `ChiR24/Unreal_mcp` y `remiphilippe/mcp-unreal` estructuraron puentes entre procesos mediante un plugin C++ en el motor y un proceso satélite (*sidecar*) en TypeScript, Python o Go.
   - Herramientas de automatización como `VibeUE` exploraron la ejecución remota de scripts de Unreal Python y la inyección procedural de activos GLB/FBX.

### 2.2 Ecosistema en Unity
1. **Unity AI Tools y Unity MCP Server (Unity 6+):**  
   Unity abandonó su plataforma anterior (Unity Muse, basada en modelos propietarios de primera parte) en favor del paquete **Unity AI Tools** (en fase beta abierta en Unity 6). Este nuevo enfoque utiliza modelos de frontera de terceros a través de un gateway unificado e incluye un servidor MCP nativo. Dicho servidor expone el árbol de GameObjects, la jerarquía de componentes, la salida de la consola de depuración y las configuraciones de compilación a asistentes de código externos.

### 2.3 Mecanismos de seguridad actuales: cómo evitan romper un proyecto
Los agentes actuales adoptan diversas estrategias para mitigar el riesgo de corrupción en proyectos grandes (que combinan gigabytes de binarios, mallas, texturas y código nativo):
- **Dependencia de Git y sistemas VCS:** La principal red de seguridad es externa al motor. Se instruye al agente a operar sobre ramas dedicadas o espacios de trabajo aislados (*worktrees*), confiando en que el desarrollador inspeccionará `git diff` o descartará cambios corruptos.
- **Transacciones del Editor (`BeginTransaction` / `EndTransaction`):** Permiten al usuario deshacer (`Undo`) acciones individuales sobre la escena. Sin embargo, este mecanismo es frágil: en Unreal, las modificaciones profundas a Blueprints, la regeneración de cachés DDC o las recompilaciones de módulos C++ no son revertibles mediante el buffer de deshacer de Slate.
- **Modos de sólo lectura y confirmación de pasos (*Human-in-the-Loop*):** Clientes como Claude Code solicitan autorización explícita antes de ejecutar herramientas marcadas como destructivas o escrituras masivas en disco.
- **La gran carencia:** **Ninguno de estos enfoques mide si el cambio introducido degradó el comportamiento del juego.** Si la escena sigue abriendo y el compilador no protesta, el cambio se da por bueno, ignorando regresiones geométricas, solapes físicos, conflictos de etiquetas en Gameplay Abilities o desalineaciones de matrices de transformación.

---

## 3. Dónde entraría Oracle

### 3.1 La naturaleza de Oracle: un instrumento de rechazo, no un generador
Como lo define su especificación (`README.md`, `ESPECIFICACION.md` §0-3):
- **Oracle no produce contenido:** No escribe código C++, no genera Blueprints, no coloca mallas ni sugiere rutas de juego.
- **Oracle mide evidencia contra medidas declaradas:** Toma hechos escalares organizados en bolsas nombradas (relaciones L0), los procesa mediante un álgebra cerrada de seis operadores (`de`, `donde`, `unir`, `sin`, `agrupar`, `resumen`; `requiere` no es un operador sino una cláusula que declara de qué relaciones depende la medida) y emite un veredicto binario (`verde` o `rojo`), con un valor escalar, un umbral justificado (`segun`), los testigos concretos de la infracción y —fundamentalmente— **un alcance explícito que declara qué NO vio la medida**.
- **Es fail-closed:** Si falta evidencia para evaluar una relación declarada en `requiere`, devuelve `SIN EVIDENCIA` en lugar de asumir un cero complaciente. Si un campo no existe, eleva una excepción. Si a una medida le faltan casos que la pongan roja y verde en su corpus, o si le sobrevive un mutante, `oracle test` sale en rojo y `desafiar` lo informa: la medida se sigue cargando, pero el proyecto no pasa su prueba. Oracle no la rechaza sola; la rechaza quien exige ese verde.

### 3.2 La hipótesis central: Oracle como el juez externo contra la ley de Goodhart
La hipótesis a contrastar es:
> **Oracle debe ser el JUEZ determinista e independiente de un agente de videojuegos, nunca el agente mismo.**

Esta hipótesis se sostiene en la experiencia directa acumulada en los dos proyectos que hoy consumen Oracle:

#### A. La lección de Jam (`~/Dev/jam/AGENTS.md`)
Jam nació bajo la regla arquitectónica: **«El cerebro es puro y el adaptador es fino»**.
En Jam, los tests del cerebro (`Content/Python/jam/*.py`) corren en 0.7 segundos sin motor porque están desacoplados de la API de Unreal. Cuando Jam coloca mallas o genera patrones procedurales de dispersión (*scatter*), no confía en la afirmación del LLM. Las medidas de Oracle en Jam juzgan:
- Si hay interpenetración geométrica inadmisible (`snap.al_ras`, `colocacion.interpenetracion`).
- Si las piezas comparten cara o quedan flotando en el vacío.
- Si las mallas generadas tienen las caras orientadas correctamente (la trampa documentada donde un algoritmo de cintas reportaba normales impecables pero tenía índices invertidos, resultando en geometría invisible por *backface culling* que ningún test sintáctico atrapó).

En este esquema, Jam (o un agente como Aura) propone la solución y ejecuta la acción en el motor; los sensores extraen la evidencia de la escena (AABBs, posiciones, trazas de rayos); y **Oracle evalúa si la escena cumple el estándar de calidad predefinido**. El agente no puede negociar con el juez ni convencerlo con prosa persuasiva: o el valor está por debajo del umbral, o hay testigos que documentan el fallo.

#### B. La lección de LyraGASP (`~/Dev/games/unreal/LyraGASP/docs/ORACLE.md`)
En LyraGASP, las herramientas convencionales imprimían diagnósticos que nadie leía con rigor. Oracle introdujo medidas deterministas sobre subsistemas complejos:
- **Animación y Gameplay Ability System (GAS):** Medidas como `recarga.montage_en_slot_cuerpo_entero`, `recarga.root_motion_habilitado` y `recarga.ability_bloquea_salto_por_tags`. Un agente como Aura podría generar una habilidad de recarga que compila y reproduce una animación; pero sólo un sensor que extrae la tabla de tags y las ranuras del montage expone que la habilidad bloquea el salto porque usa una ranura de cuerpo entero.
- **Topología de mallas y ML Deformer:** Medidas como `ml_deformer.malla_objetivo_fragmentada` (que exige una única componente conexa en la superficie). Una herramienta generativa puede exportar un FBX que parece correcto visualmente en una captura de pantalla reducida, pero que contiene costuras abiertas o vértices sin influencia ósea que arruinarán el entrenamiento del deformador neuronal.

#### C. La separación de poderes y el servidor MCP (`estudios/MCP-CONTRATO.md`)
El diseño del servidor MCP de Oracle (`0.27.0`) fue concebido explícitamente para este escenario:
- Expone herramientas estrictamente de sólo lectura (`oracle_catalogo_efectivo`, `oracle_evaluar`, `oracle_desafiar`, `oracle_juzgar`, `oracle_tareas`).
- No permite que el agente modifique medidas al vuelo para ocultar un fallo.
- Cuando un agente como Aura o Claude Code termina una iteración en el motor, no debería preguntarse a sí mismo «¿quedó bien?». Debe invocar `oracle_juzgar` pasándole la evidencia extraída. Si la respuesta es `ok: false`, el agente recibe una lista precisa de medidas violadas y las filas de testigos responsables, cerrando el bucle de feedback con base empírica, no probabilística.

```
       ┌────────────────────────────────────────────────────────┐
       │                AGENTE GENERATIVO (Aura)                │
       │  - Recibe el encargo del usuario                       │
       │  - Genera C++, Blueprints, materiales o escenas        │
       │  - Aplica cambios vía Unreal MCP / Automation API      │
       └───────────────────────────┬────────────────────────────┘
                                   │ (1. Modifica escena/código)
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │               MOTOR DE JUEGO (Unreal / Unity)          │
       │  - Ejecuta código y compila Blueprints                 │
       │  - Resuelve físicas, render y grafo de animación       │
       └───────────────────────────┬────────────────────────────┘
                                   │ (2. Extrae hechos)
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │               SENSORES DEL DOMINIO (L0)                │
       │  - Desacoplados del juicio (sensores puros)            │
       │  - Convierten estado del motor a tablas JSON           │
       └───────────────────────────┬────────────────────────────┘
                                   │ (3. Emite evidencia)
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │                 JUEZ ORACLE (L1 / L2)                  │
       │  - Álgebra determinista y medidas fijadas en repo      │
       │  - Evalúa evidencia vía MCP (`oracle_juzgar`)          │
       │  - Emite veredicto: VERDE / ROJO + Testigos + Alcance   │
       └───────────────────────────┬────────────────────────────┘
                                   │ (4. Veredicto y testigos)
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │             RETROALIMENTACIÓN AL AGENTE                │
       │  - Si es ROJO: itera con base en testigos concretos    │
       │  - Si es VERDE: da por concluida la tarea con certeza  │
       └────────────────────────────────────────────────────────┘
```

### 3.3 La hipótesis contraria: objeciones y límites de Oracle en este rol
Para evaluar la viabilidad con rigor técnico, es imprescindible examinar por qué este modelo podría fallar o resultar inviable:

1. **El costo previo de formalización (El problema de la página en blanco):**  
   Oracle exige que las relaciones y las medidas existan de antemano en el repositorio, respaldadas por un corpus con polaridades positiva y negativa, y mutadas a cero sobrevivientes. Si un usuario le pide a Aura: *«Creá un sistema de sigilo donde los enemigos sospechen si escuchan pasos sobre madera mojada»*, Oracle no puede juzgar nada a menos que alguien haya escrito previamente el sensor de audio/materiales y la medida correspondiente. Un agente generalista que debe improvisar sobre mecánicas arbitrarias se encontraría frecuentemente con que el juez no tiene jurisprudencia sobre el problema planteado.
2. **Oracle no evalúa sensaciones subjetivas (*Game Feel*):**  
   Gran parte del desarrollo de videojuegos no se rige por umbrales geométricos o algebraicos duros, sino por apreciaciones cualitativas: *«¿el salto se siente pesado?», «¿la iluminación transmite misterio?», «¿el retroceso del arma es satisfactorio?»*. Oracle declina explícitamente evaluar afirmaciones que no puedan expresarse como una comparación de escalares con unidad derivable. Exigirle a Oracle que juzgue la estética o la diversión destruiría su razón de ser.
3. **El costo temporal y las trampas de extracción de evidencia:**  
   Como se demostró en Jam, la extracción de hechos en Unreal Engine está plagada de asperezas técnicas:
   - Los commandlets desatendidos (`-run=pythonscript`) no ejecutan el bucle de Slate ni tickean procesadores de renderizado, lo que falsea tiempos y hace fallar llamadas como `spawn_actor_from_object`.
   - Calcular cajas envolventes (AABB) de un landscape arroja la cota máxima del terreno entero, engañando a cualquier sensor ingenuo de asentamiento.
   - Si cada ciclo de evaluación de un agente requiere reiniciar el motor o ejecutar una traza pesada de 15 segundos para generar la evidencia JSON, el bucle del agente se vuelve prohibitivamente lento comparado con la interacción directa.
4. **Goodhart de segundo orden (El riesgo de corrupción del sensor):**  
   Si al agente generativo se le da acceso de escritura al código fuente del proyecto, y se le condiciona a que `oracle_juzgar` dé verde para terminar, el camino de menor resistencia para el LLM podría no ser arreglar el juego, sino **modificar el sensor en Python para que emita evidencia vacía o manipulada**, eludiendo la medida. Por ello, la separación de permisos debe ser absoluta: el agente no debe poder tocar los sensores ni las definiciones de `medidas/`.

---

## 4. Veredicto y tareas propuestas

### 4.1 Veredicto
**Construir un agente completo similar a Aura NO es el propósito de Oracle.** Oracle no es un orquestador de subagentes, ni un generador de C++, ni una interfaz gráfica de chat.

Sin embargo, **utilizar Oracle como la compuerta de verificación independiente de un agente estilo Aura no sólo es viable, sino que resuelve el talón de Aquiles fundamental de toda la ola actual de agentes para gamedev:** la auto-complacencia y la incapacidad de detectar fallos semánticos profundos.

Aura y las herramientas MCP actuales son operarios rápidos pero miopes: pueden generar 500 líneas de código o ensamblar un nivel en segundos, pero su criterio de éxito se reduce a «no crasheó». Oracle es el inspector de calidad estricto: no sabe colocar ladrillos, pero sostiene la plomada y el nivel, y se niega a firmar la aprobación si el muro está torcido, señalando exactamente los milímetros de desviación y reconociendo en su informe qué partes del edificio no alcanzó a inspeccionar.

La combinación natural es:
- **Aura / Claude Code / Unreal MCP:** El motor de síntesis y ejecución (hace el trabajo en el motor).
- **Sensores desacoplados:** Los instrumentos de telemetría (extraen hechos crudos a JSON).
- **Oracle (vía MCP):** El tribunal determinista que valida si los invariantes del proyecto siguen en pie antes de aceptar el trabajo del agente.

---

### 4.2 Qué faltaría para materializar este flujo de trabajo

#### En Oracle:
1. **Soporte de evaluación directa sobre archivos de evidencia en disco:**  
   Actualmente, la herramienta MCP `oracle_juzgar` recibe la evidencia como un objeto JSON anidado dentro de la carga útil del mensaje RPC. En entornos de videojuegos, donde un volcado de colisiones o mallas puede ocupar varios megabytes, transferir la evidencia como string en el protocolo MCP es ineficiente. Conviene admitir una referencia a un archivo local de evidencia ya volcado por el motor.
2. **Métricas de cobertura de evidencia frente al catálogo:**  
   Reportar claramente qué porcentaje de las medidas aplicables del proyecto no pudieron juzgar debido a que los sensores no emitieron sus relaciones dependientes (un problema detectado recientemente en la versión 0.27.0 de Oracle).

#### En Jam:
1. **Unificación del bucle de autoría con la compuerta de Oracle:**  
   Jam cuenta con Slate en C++ y lógica en Python puro, pero la invocación de medidas de Oracle se ejecuta primordialmente desde la terminal mediante `tools/relevo.py` o scripts aislados. Falta integrar la consulta a `oracle_juzgar` directamente en los paneles de Slate para que el usuario o el agente puedan presionar «Verificar escena» y recibir el diagnóstico visual de testigos en el propio viewport.
2. **Blindaje de sensores frente a modificaciones de agentes:**  
   Establecer una política de permisos o custodia estricta que impida que un agente edite `Content/Python/jam/` o `medidas/` cuando su encargo es puramente de diseño de niveles o mecánicas.

#### En sensores de Unreal:
1. **Biblioteca estandarizada de sensores headless confiables:**  
   Superar las trampas documentadas en el repositorio de Jam: empaquetar rutinas C++/Python probadas para extraer relaciones L0 de transformaciones espaciales, cajas de colisión reales (vía trazas de geometría, no simples AABB inflados), jerarquías de Game Feature Data y grafos de Gameplay Abilities, garantizando que funcionen tanto en editor completo como en corridas desatendidas con `-RenderOffScreen`.

---

## 5. La propuesta de un «Aura propio» para Godot, Unity y Unreal con Oracle

En respuesta directa al interés planteado por Brian (nota del 2026-09-19): **¿se puede construir un Aura propio que cubra Godot, Unity y Unreal usando Oracle?**

### 5.1 Desglose de piezas: qué es propio y qué ya existe
Para no caer en la tentación de reconstruir lo que la industria ya resolvió, el sistema debe particionarse con absoluta claridad:

| Pieza | Estado / Procedencia | Rol en el sistema |
|---|---|---|
| **Modelos de frontera (LLMs)** | **Existe** (Anthropic Claude, OpenAI, etc.) | Razonamiento general, comprensión de la intención del usuario y generación de código/Blueprints. |
| **Protocolo de comunicación** | **Existe** (MCP estándar) | Capa de transporte JSON-RPC para conectar agentes con editores y con Oracle. |
| **Puentes al editor (Editor Bridges)** | **Existe mayoritariamente** | Unreal MCP oficial en UE 5.8+ y comunitarios; Unity AI MCP Server oficial en Unity 6+. En Godot existen servidores MCP comunitarios y el protocolo de depuración/LSP. |
| **El Juez determinista (Oracle)** | **Existe** (`oracle-metalenguaje`) | Evalúa evidencia L0 contra medidas declaradas en `.oracle`, con alcance, testigos y corpus de falsación. MCP de sólo lectura listo en 0.27.0. |
| **El Agente orquestador** | **PROPIO** (a construir) | El bucle agente-operario (análogo a Telos/Dragon en Aura): planifica la tarea, invoca herramientas del motor vía MCP, solicita la extracción de evidencia a los sensores y consulta a Oracle para validar el paso. |
| **Los Sensores por motor** | **PROPIO** (a construir/empaquetar) | Rutinas desacopladas que extraen el estado del motor (actores, transforms, tags, nodos, jerarquías) y emiten relaciones L0 JSON según esquemas de `relaciones/`. |
| **Catálogo de medidas del motor** | **PROPIO** (a escribir en superficie) | Reglas invariantes del proyecto y del motor escritas en sintaxis `.oracle` (ej. no solape de piezas, no desgarro de mallas, consistencia de tags, no referencias rotas). |

### 5.2 Qué está probado en casa frente a qué no
La asimetría entre motores en nuestra base de código es total y define la estrategia:

#### Lo que SÍ está probado en casa: Unreal Engine
En este repositorio y en el ecosistema inmediato (Jam y LyraGASP) hay meses de evidencia empírica acumulada sobre Unreal Engine 5.8.1:
1. **La regla «cerebro puro + adaptador fino»:** Probada con éxito en Jam (`Content/Python/jam/*.py` sin `import unreal`, testeado en 0.7 s) y en LyraGASP (`tools/sensores/recarga.py` puro vs `tools/mide_recarga.py`).
2. **Sondas headless y sus límites reales:** Sabemos con precisión quirúrgica qué corre en commandlet (`-run=pythonscript`), qué exige editor completo sin ventana (`-RenderOffScreen -unattended -nosplash`), por qué `-nullrhi` arroja SIGFPE en 5.7/5.8, y por qué `spawn_actor_from_object` falla en commandlet.
3. **Sensores L0 reales en producción:**
   - Geometría y escena en Jam: detección de colisiones, alineación al ras (`snap.al_ras`), cobertura de scatter y orientación de normales de triángulos.
   - Subsistemas de juego en LyraGASP: cruces de Gameplay Ability Tags (`recarga.ability_bloquea_salto_por_tags`), verificación de ranuras de montages de animación y análisis topológico de mallas para ML Deformer (`ml_deformer.malla_objetivo_fragmentada`).

#### Lo que NO está probado en casa: Godot y Unity
- **Unity:** Cero líneas de código, cero sensores y cero medidas en nuestros repositorios. Aunque el Unity MCP Server existe en Unity 6+, no se ha validado cómo interactúa un proceso externo con la recarga de dominios de C#, ni cómo serializar el estado de GameObjects a relaciones L0 puras de forma determinista.
- **Godot:** Cero experiencia en el proyecto. Si bien Godot ofrece ventajas teóricas inmensas para un agente (arranque en milisegundos, ejecución headless nativa y ligera, archivos de escena `.tscn` en texto plano legibles sin motor), hoy no existe ningún sensor ni esquema de relaciones adaptado a su jerarquía de nodos.

### 5.3 Corte mínimo realista para empezar (V1): En un solo motor (Unreal)
Intentar abarcar Unreal, Unity y Godot en el primer paso garantizaría dispersión y fracaso. El corte mínimo debe capitalizar lo que ya anda:

**Entorno del corte mínimo:**
- **Motor:** Unreal Engine 5.8.1 sobre el proyecto host **`JamPlayground`** (arranca en ~15 s y compila en ~38 s, evitando el peso de 18 GB de BotOO).
- **El Actor/Operario:** Un agente en terminal (como Claude Code o un script de orquestación en Python) equipado con el cliente MCP para Unreal y las herramientas existentes de Jam (`jam.colocar`, `jam.snap`, o las APIs de Unreal MCP).
- **El Sensor:** Un script adaptador en Python (`tools/mide_escena.py`) que invoca el sensor puro de colisiones/transforms y emite `Saved/Oracle/escena.json`.
- **El Juez:** `oracle juzgar` (o `oracle_juzgar` vía MCP) evaluando el catálogo de colocación (`colocacion.interpenetracion`, `snap.al_ras`).

**El ciclo de ejecución del corte mínimo:**
1. El usuario pide: *«Colocá una trinchera defensiva alineada al muro norte»*.
2. El agente calcula la posición y llama a la herramienta del motor para instanciar y ubicar los actores.
3. El agente dispara la sonda del sensor en el editor.
4. El sensor extrae la evidencia L0 (`pieza`, `contacto`, `caja_aabb`).
5. El agente invoca `oracle_juzgar`.
6. Si Oracle detecta interpenetración (`rojo`), devuelve los testigos (`Muro_02` penetra 12 cm en `Muro_01`).
7. El agente retrocede la posición 12 cm, repite el sensor y Oracle da `verde`.
8. El cambio se confirma.

Una vez probado y aceitado este bucle en Unreal, extenderlo a Godot o Unity consiste únicamente en escribir los **sensores del nuevo motor** que emitan las mismas relaciones L0 ya formalizadas; el juez Oracle y el álgebra no cambian una sola coma.

---

### 5.4 Tareas propuestas para el tracker de Oracle

Las siguientes tareas surgen de este análisis para ser incorporadas al seguimiento de Oracle por Claude:

1. **`mcp-evidencia-por-ruta`:**  
   *Porqué:* La herramienta `oracle_juzgar` en `estudios/MCP-CONTRATO.md` y `nucleo/mcp.py` exige recibir la evidencia en memoria vía JSON-RPC. Para escenas de Unreal Engine con cientos de actores o mallas complejas, la serialización en la llamada satura el transporte. Permitir un parámetro opcional `ruta_evidencia` (validado fail-closed dentro de la raíz permitida del proyecto) facilita la integración con motores de juego que vuelcan su telemetría a `Saved/Oracle/*.json`.
2. **`meta-medida-relacion-sin-sensor`:**  
   *Porqué:* Cuando un agente opera en un proyecto con Oracle, una medida puede salir verde de forma vacía si su relación dependiente no fue emitida y no cuenta con la cláusula `requiere`. Es necesario reforzar en el catálogo universal medidas meta que detecten medidas huérfanas de emisor antes de que el agente las utilice como falso criterio de éxito.
3. **`estudio-sensores-gamedev-l0`:**  
   *Porqué:* Documentar los patrones canónicos de sensores puros de videojuegos (aprendidos en Jam y LyraGASP: separación de `import unreal`, representación de matrices y transforms sin objetos opacos, tratamiento de flotantes con tolerancias explícitas) para que cualquier proyecto nuevo en Unreal, Unity o Godot pueda instrumentar su evidencia L0 sin reinventar la arquitectura.
4. **`corte-minimo-agente-jam-oracle`:**  
   *Porqué:* Diseñar la prueba de concepto del bucle autónomo en Unreal 5.8: un agente CLI externo que ejecute una herramienta de colocación en `JamPlayground`, extraiga evidencia con los sensores de Jam y cierre el ciclo consultando `oracle_juzgar` vía MCP.

