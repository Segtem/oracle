# Jev de TypeSafe AI y Oracle: Modelos «System One» de decisión rápida frente al juicio determinista

**Fecha:** 2026-09-22  
**Autor:** Antigravity (asistente técnico en pair programming)  
**Estado:** Estudio de investigación para la tarea `20260922-185116-jev`  
**Lecturas previas requeridas:** `README.md`, `ESPECIFICACION.md` §0–§3, `estudios/MCP-CONTRATO.md`, `estudios/AURA-Y-ORACLE.md`.

---

## 1. Qué es Jev (y confirmación del nombre real)

### 1.1 Confirmación de nombre, creador y fuentes
La consulta inicial de Brian (2026-09-22) refería de oído a **«JEV, de TypeSage IA»**. La contrastación contra fuentes públicas arrojó los siguientes hechos:

1. **El nombre real de la empresa es TypeSafe AI** ([typesafe.ai](https://typesafe.ai/)).  
   El término «TypeSage» no corresponde a ninguna empresa ni producto de inteligencia artificial con ese perfil; las coincidencias encontradas corresponden a errores fonéticos, discusiones sobre tipado estricto (*type-safe* en Java/TypeScript) o marcas postales francesas históricas.
2. **El nombre real del producto es Jev** (no son siglas ni acrónimo en mayúsculas).  
   Fue nombrado en homenaje al economista británico del siglo XIX **William Stanley Jevons**, célebre por formular la **Paradoja de Jevons** (la observación de que el aumento en la eficiencia con la que se utiliza un recurso tiende a incrementar, en lugar de disminuir, la tasa global de consumo de dicho recurso). La premisa fundacional de TypeSafe AI es que si el costo y la latencia de tomar decisiones algorítmicas se reducen en varios órdenes de magnitud, el software demandará millones de decisiones automatizadas por segundo.
3. **Fundadores y equipo:**  
   TypeSafe AI fue fundada en 2024 en San Francisco por **Diogo Almeida** (CEO, ex investigador de OpenAI y coautor de los trabajos pioneros en RLHF, *InstructGPT* y GPT-4), **Erik Gafni** y **Sasha Sheng**.
4. **Anuncio y lanzamiento:**  
   La empresa emergió del modo sigilo (*stealth*) y lanzó el modelo Jev el **15 de septiembre de 2026** bajo un esquema de acceso temprano con lista de espera (*limited early access* administrado en `console.typesafe.ai`).
5. **Fuentes primarias y de referencia verificadas:**
   - Sitio oficial y consola: `https://typesafe.ai` y `https://console.typesafe.ai`.
   - Documentación conceptual: `https://docs.typesafe.ai/concepts/system-one`.
   - Endpoint de API pública: `https://api.typesafe.ai/v1/systemone`.
   - Registros de integración de mercado: OpenRouter (`typesafe/jev-latest` y `jev-1.13`), Vercel AI Gateway, Cloudflare Workers AI y paquetes en PyPI (`typesafe-sdk`) y npm (`@typesafe-ai/sdk`).

---

### 1.2 El problema que dice resolver y la arquitectura «System One»
La tesis técnica de TypeSafe AI parte de una crítica directa al estado de la industria de la inteligencia artificial entre 2023 y 2026: **el abuso de modelos de lenguaje autorregresivos (LLMs) gigantes para tareas de decisión en software**.

Para explicar su arquitectura, apelan a la distinción cognitiva formulada por Daniel Kahneman (*Thinking, Fast and Slow*):
- **Sistema 2:** Pensamiento deliberativo, analítico, lento y secuencial (razonamiento profundo, escritura de ensayos, derivaciones matemáticas complejas). Es el dominio natural de los LLMs tradicionales (*frontier models* como GPT-4 o Claude 3.5 Sonnet), que predicen el mundo token por token con latencias de 1 a 10 segundos.
- **Sistema 1:** Juicio intuitivo, rápido, directo y automático (reconocer un peligro, categorizar un objeto, reaccionar a un estímulo).

TypeSafe argumenta que la gran mayoría de las integraciones de IA en sistemas de backend no requieren creatividad, conversación ni redacción de párrafos, sino **decisiones operativas instantáneas**: enrutar un reclamo, detectar una anomalía, clasificar la severidad de un incidente o evaluar si una entrada cumple un criterio. Someter esas operaciones a un LLM autorregresivo introduce sobrecostos masivos, latencias intolerables eインestabilidad por alucinaciones de sintaxis (JSON roto).

#### Arquitectura interna:
1. **Sin generación de texto libre ni decodificación secuencial:**  
   Jev es arquitectónicamente incapaz de emitir prosa o código. No predice el siguiente token de izquierda a derecha.
2. **Muestreo paralelo en una sola pasada (*Parallel Sampling Architecture*):**  
   Recibe como entrada un estado de programa no estructurado (`state`) y un diccionario de preguntas tipadas (`questions`). El modelo procesa el contexto y evalúa todas las preguntas simultáneamente en un único pase hacia adelante (*forward pass*), devolviendo todos los resultados en paralelo.
3. **Entrenamiento RLCD (*Reinforcement Learning for Calibrated Decisions*):**  
   A diferencia del RLHF clásico (que optimiza el modelo para satisfacer preferencias humanas conversacionales y tiende a inducir respuestas complacientes y sobreconfiadas), el entrenamiento RLCD ajusta los pesos de la red para calibrar estrictamente las probabilidades estadísticas. Si Jev asigna un 0.85 a una condición, la distribución empírica de aciertos sobre conjuntos de prueba se aproxima efectivamente al 85%.

#### Primitivas tipadas de salida:
Jev no devuelve esquemas JSON arbitrarios ni anidados. Su interfaz se restringe rígidamente a tres tipos de datos primitivos:
- **`Noul`:** Juicio binario (sí/no o verdadero/falso). Se devuelve como un valor flotante continuo entre `0.0` y `1.0` que representa la probabilidad bayesiana calibrada de que la proposición sea verdadera. No incluye un campo de confianza separado, pues el número en sí mismo es la probabilidad estimada.
- **`Choice`:** Selección categórica exclusiva entre un conjunto discreto de opciones predefinidas (admite hasta 255 alternativas). Devuelve la opción ganadora (`choice`), la distribución de probabilidades de cada opción candidata y un escalar de confianza global (`confidence`).
- **`Score`:** Puntuación dentro de una escala ordinal normalizada (de 2 a 10 niveles descriptivos, por ejemplo de «Baja» a «Crítica»). Devuelve un número flotante interpolado y una métrica de confianza.

---

### 1.3 Cómo se integra, qué necesita para correr, precio y límites

#### Modelo de integración y SDKs
La comunicación se realiza a través de un único endpoint HTTP POST:
```http
POST https://api.typesafe.ai/v1/systemone
Authorization: Bearer <TYPESAFE_API_KEY>
Content-Type: application/json
```

El SDK oficial para Python (`typesafe-sdk`) ilustra el patrón canónico de invocación:
```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

client = TypeSafeClient()

ticket = "Socorro: el servidor de pagos arrojó error 500 y se cancelaron 4 órdenes."

respuesta = client.system_one(
    state=ticket,
    questions={
        "es_urgente": Noul(instructions="¿El mensaje reporta una falla que interrumpe operaciones?"),
        "area": Choice(
            instructions="¿A qué equipo debe derivarse?",
            criteria={
                "facturacion": "Pagos, transacciones, cobros fallidos",
                "infraestructura": "Caídas de servidores, red, timeouts",
                "ventas": "Consultas comerciales y cotizaciones",
            },
        ),
        "severidad": Score(
            instructions="Gravedad operativa del problema reportado",
            criteria=["Leve", "Moderada", "Crítica"],
        ),
    },
)

# Acceso tipado a resultados
prob_urgente = respuesta.answers["es_urgente"].noul          # float [0.0 - 1.0]
area_elegida = respuesta.answers["area"].choice               # str
confianza = respuesta.answers["area"].confidence             # float [0.0 - 1.0]
```

En TypeScript/JavaScript opera análogamente mediante `@typesafe-ai/sdk` consumiendo funciones como `noul()`, `choice()` y `score()`.

#### Requisitos y entorno de ejecución
- **SaaS cerrado:** Jev no es un modelo de pesos abiertos (*open weights*). No se puede descargar para correr localmente en ONNX, llama.cpp ni PyTorch en hardware propio.
- **Dependencia de red:** Exige conexión de red permanente hacia la infraestructura en la nube de TypeSafe AI (o a través de intermediarios como OpenRouter o Vercel AI Gateway).
- **Acceso:** Limitado por lista de espera (*waitlist*) sujeta a aprobación en consola.

#### Precios y métricas de rendimiento
- **Costo de entrada:** **$0.042 USD por cada millón de tokens de entrada** ($42 USD por cada 1.000 millones de tokens).
- **Costo de salida:** **Gratuito / no tarifado** (*unmetered*). TypeSafe publicita la salida como «demasiado barata para medirla», dado que la carga devuelta consiste exclusivamente en escalares numéricos y cadenas breves correspondientes a las primitivas tipadas.
- **Latencia:** Rango medido entre **70 ms y 500 ms** para el lote completo de preguntas en paralelo, en contraste con los 2.000 ms a 15.000 ms habituales en llamadas con cadenas de pensamiento (*chain-of-thought*) en modelos de frontera.
- **Eficiencia comparada:** La empresa afirma que es hasta **200 veces más rápido** y **400 veces más económico** que un LLM convencional para tareas de clasificación.

---

### 1.4 Lo que dicen frente a lo que muestran: la «verificación» bajo la lupa
TypeSafe promociona a Jev como una solución de «verificación automatizada de código y estados de software». Al examinar críticamente la documentación y las especificaciones técnicas frente a la retórica publicitaria, se evidencia una brecha que es indispensable marcar:

| Qué dice el material promocional | Qué muestra la documentación y el comportamiento real |
|---|---|
| *«Elimina por completo las alucinaciones en decisiones de software.»* | La eliminación de alucinaciones aplica **únicamente a la forma sintáctica**. Jev garantiza por construcción tipada que el campo devuelto será un valor perteneciente a la unión de tipos definida (no emitirá texto inesperado ni romperá un parser JSON). Sin embargo, el contenido semántico sigue siendo **estadístico y aproximado**: el modelo puede clasificar erróneamente un ticket o subestimar un incidente. |
| *«Decisiones con probabilidades calibradas que reemplazan la necesidad de supervisión.»* | RLCD reduce el desvío de sobreconfianza, pero una probabilidad de 0.9 sigue reconociendo formalmente una tasa de error del 10%. Tratar un `noul: 0.9` como un veredicto booleano determinista equivale a absorber un 10% de falsos verdes o falsos rojos de forma silenciosa. |
| *«Inspecciona el estado del programa.»* | El parámetro `state` recibe una cadena de texto plana o un documento no estructurado. Jev no interactúa con el runtime de ejecución, no inspecciona la memoria del proceso, no analiza árboles de sintaxis abstracta (AST) ni evalúa precondiciones matemáticas; sólo lee el volcado de texto proporcionado por quien invoca la API. |
| *«Reemplaza a los LLMs en el ciclo de software.»* | Jev sólo puede emitir tres primitivas escalares planas. No puede generar planes de acción, no compone estructuras jerárquicas complejas y no explica el porqué causal de su determinación (carece de explicabilidad simbólica). |

---

## 2. Qué hay alrededor en el ecosistema

El lanzamiento de Jev en septiembre de 2026 catalizó una discusión en la industria sobre la dicotomía entre dos enfoques para estructurar decisiones de inteligencia artificial: **modelos especializados no generativos** frente a **mecanismos de restricción sintáctica sobre modelos generativos**.

```
                         ┌────────────────────────────────────────────────────────┐
                         │      DECISIONES Y ESTRUCTURACIÓN MEDIANTE IA           │
                         └───────────────────────────┬────────────────────────────┘
                                                     │
                     ┌───────────────────────────────┴───────────────────────────────┐
                     ▼                                                               ▼
       ┌───────────────────────────┐                                   ┌───────────────────────────┐
       │   MODELOS SYSTEM ONE      │                                   │   CONSTRAINED DECODING    │
       │   (Sin autorregresión)    │                                   │   (Sobre LLMs estándar)   │
       └─────────────┬─────────────┘                                   └─────────────┬─────────────┘
                     │                                                               │
        ┌────────────┴────────────┐                                     ┌────────────┴────────────┐
        ▼                         ▼                                     ▼                         ▼
  ┌───────────┐             ┌───────────┐                         ┌───────────┐             ┌───────────┐
  │    Jev    │             │   Laya    │                         │ Outlines  │             │Instructor │
  │ (TypeSafe)│             │  (Convai) │                         │  (dottxt) │             │ (Pydantic)│
  └───────────┘             └───────────┘                         └───────────┘             └───────────┘
```

### 2.1 Laya (Convai Innovations) y OpenJev: la contrapartida de código abierto
Pocas semanas después del debut de TypeSafe, surgieron alternativas en el mismo paradigma:
1. **Laya (Convai Innovations, septiembre 2026):**  
   Motor de inferencia rápida *System One* publicado bajo licencia de código abierto. Al igual que Jev, omite la generación secuencial token a token y entrena cabezales de evaluación paralela sobre modelos base compactos (de 1B a 3B de parámetros) para responder consultas tipadas de clasificación y puntaje con probabilidades calibradas.
2. **OpenJev:**  
   Proyecto impulsado por la comunidad open source que busca emular la interfaz de Jev extrayendo logits normalizados en un único paso de decodificación desde modelos instruccionales congelados (ej. Llama-3-8B), sin requerir re-entrenamiento con RLCD, aunque con una calibración probabilística significativamente más pobre.

**Diferencia clave con Jev:** Jev es una plataforma SaaS propietaria y cerrada que ofrece alta calibración mediante RLCD centralizado; Laya y OpenJev priorizan la soberanía de datos y el despliegue local o desconectado en centros de datos propios.

### 2.2 Outlines (dottxt) y SGLang: decodificación restringida previa (*Pre-generation constraint*)
**Outlines** no entrena un modelo nuevo. Opera sobre LLMs autorregresivos convencionales (a través de vLLM, llama.cpp o Hugging Face) interceptando el bucle de muestreo de tokens:
- Construye un autómata finito determinista (FSM) o una gramática formal a partir de un esquema Pydantic, un JSON Schema o una expresión regular.
- En cada paso de generación, calcula una máscara de logits que fuerza a cero la probabilidad de cualquier token que no cumpla la gramática.

**Diferencia clave con Jev:** Outlines garantiza un 100% de cumplimiento estructural sin reintentos, pero **sigue pagando el costo y la latencia de la autorregresión**: si la respuesta requiere 50 tokens, el modelo ejecutará 50 pasos secuenciales en la GPU (cientos o miles de milisegundos), cobrando el precio estándar por token generado. Jev descarta la autorregresión por completo y resuelve la consulta en una sola pasada.

### 2.3 Instructor y PydanticAI: validación posterior y reintentos (*Post-generation validation*)
Bibliotecas como **Instructor** operan como capas adaptadoras sobre APIs cerradas de modelos de frontera (OpenAI, Anthropic, Gemini):
- Solicitan al modelo una salida formateada (usando *Tool Calling* o *JSON Mode*).
- Validan la carga útil devuelta contra esquemas Pydantic.
- Si el modelo produce un tipo inválido o un campo ausente, atrapan la excepción y ejecutan llamadas de reintento inyectando el mensaje de error en el contexto hasta que la salida valide o se agote el presupuesto.

**Diferencia clave con Jev:** Instructor es universal y agnóstico al proveedor, pero introduce variabilidad en la latencia (que puede triplicarse si hay fallos y reintentos) y no ofrece probabilidades bayesianas calibradas sobre las decisiones tomadas; sólo fuerza que el texto resultante pueda deserializarse en un objeto Python.

### 2.4 Clasificadores clásicos de NLP y Cross-Encoders (Cohere Classify, SetFit, DeBERTa)
El mundo de la clasificación tradicional mediante representaciones semánticas (*embeddings*) y modelos tipo bi-encoder o cross-encoder:
- **Diferencia clave con Jev:** Los clasificadores tradicionales requieren típicamente conjuntos de entrenamiento anotados (*fine-tuning*) o ejemplos de disparo (*few-shot*) emparejados con espacios vectoriales estáticos. No aceptan instrucciones dinámicas en lenguaje natural arbitrarias para múltiples preguntas heterogéneas evaluadas concurrentemente en una misma llamada.

---

## 3. Dónde tocaría a Oracle

Para analizar rigurosamente el impacto de una tecnología como Jev en Oracle, es obligatorio repasar los principios de arquitectura documentados en `README.md`, `ESPECIFICACION.md` (§0–§3) y `estudios/MCP-CONTRATO.md`:

- **La regla de oro del núcleo:** *«Conectar un consumidor no debe exigir tocar `nucleo/`»*. Oracle se instala offline, sin dependencias externas, en Python 3.11+, y su núcleo es álgebra relacional pura.
- **Confianza acotada y negación:** Oracle no calcula calidades abstractas; declina dejar pasar lo que no puede sostener. Toda medida exige `umbral` con defensa (`segun`) y `alcance` obligatorio (declarando qué NO vio).
- **Fail-closed:** Si falta evidencia declarada en `requiere`, el resultado es `SIN EVIDENCIA`, no un verde complaciente.

Examinemos las tres interrogantes por separado:

---

### 3.1 ¿Oracle la usaría adentro?
La pregunta exige discriminar entre las cuatro áreas internas del marco: **álgebra**, **mutación**, **tracker** y **sensores**.

#### A. En el álgebra (`nucleo/algebra.py`): NO rotundo
El álgebra de Oracle es un sistema formal cerrado compuesto por seis operadores (`de`, `donde`, `unir`, `sin`, `agrupar`, `resumen`). Opera sobre relaciones L0 que son bolsas de hechos con campos escalares. Sus propiedades no negociables son:
1. **Determinismo absoluto:** Correr la misma evidencia contra el mismo catálogo produce exactamente el mismo veredicto, el mismo escalar y los mismos testigos.
2. **Cómputo finito y exacto:** La especificación prohíbe incluso la igualdad exacta entre números flotantes cuando son resultados de agregados continuos; cada umbral se defiende y valida formalmente.
3. **Cero dependencias externas:** Corre en microsegundos en CPU sin red.

Integrar Jev dentro del álgebra —por ejemplo, permitiendo que un nodo `donde` invoque una consulta probabilística para decidir si una fila pasa el filtro— **dinamitaría las garantías fundamentales del metalenguaje**. El álgebra dejaría de ser un cómputo determinista sobre datos para convertirse en un evaluador estocástico dependiente de los pesos de una red neuronal ajena. Además, introduciría dependencias de red hacia una API externa, destruyendo la portabilidad offline del paquete.

#### B. En la mutación (`tools/mutar.py` y arnés de mutación): NO
El sistema de mutación de Oracle descansa sobre el principio de que **los mutantes son mecánicos y no opinan** (`DECISION-011`):
- Los 29 mutadores de medidas aplican transformaciones puramente sintácticas sobre la estructura de datos canónica (reemplazar operadores lógicos, invertir comparadores, omitir filtros, aflojar umbrales).
- La efectividad del corpus se mide conductualmente: un mutante «muere» si y sólo si un caso real del corpus invierte el veredicto, altera el valor escalar o modifica la lista de testigos.
- Incorporar a Jev para «evaluar» si un mutante es razonable o para descartar mutantes equivalentes reintroduciría el sesgo del observador: una inteligencia artificial decidiendo qué regla de prueba es válida, incurriendo exactamente en la trampa de Goodhart que el proyecto fue concebido para erradicar.

#### C. En el tracker (`oracle tarea`): NO en el núcleo
El subsistema de seguimiento de tareas (`tareas/`, `nucleo/tareas.py`) es una herramienta de registro local en texto plano (Markdown) inspirado en *tatr*, versionado junto al código en Git.
- Podría argumentarse que Jev sería útil para tareas periféricas de conveniencia (por ejemplo, autocompletar etiquetas o categorizar la urgencia de una nota mediante llamadas a `Choice`).
- Sin embargo, incorporar esa capacidad al código base del CLI violaría el requisito de independencia y funcionamiento sin red.
- Más aún: el tracker de Oracle ya expone sus registros como evidencia relacional a través del comando `oracle tarea hechos`. La coherencia del seguimiento (ej. que no haya tareas cerradas sin commit, o que no haya referencias rotas) se valida mediante **medidas deterministas de Oracle escritas en lenguaje `.oracle`**, no mediante apreciaciones heurísticas de un clasificador.

#### D. En los sensores (L0): SÍ, pero viviendo en el espacio del consumidor
La arquitectura de cinco niveles de Oracle (`README.md`, `DECISION-005`) establece una frontera tajante entre el mundo real y el metalenguaje:

```
L2   medidas sobre medidas    enunciados sobre L1                        ✓
L1   medidas deterministas    enunciados sobre L0 (álgebra pura)         ✓
L0   evidencia relacional     hecho(id, escalares...)                     ✓
──────────────────────────────────────────────────────────────────────────
L−1  qué lee el sensor        alcance del sensor y unidades de campos    ✓
L−2  qué leyó y en qué        identidad, commit y frescura del referente ✓
──────────────────────────────────────────────────────────────────────────
     el terreno               el mundo real (no es un nivel)
```

Un **sensor** no vive en `nucleo/`; vive en el proyecto consumidor. Cuando el terreno observado consiste en datos cualitativos o lenguaje natural no estructurado (como el buzón de soporte de un producto, la transcripción de un chat o los reportes de incidentes de un sistema), **Jev es un instrumento ideal para construir un sensor L0**:
1. El sensor del consumidor toma el texto del terreno y ejecuta llamadas a Jev.
2. Jev procesa el texto a 100 ms y devuelve primitivas tipadas (`noul`, `choice`, `score`).
3. El sensor traduce esas respuestas en filas limpias de una relación L0:
   ```json
   {
     "clasificacion_incidente": [
       {"id": "INC-801", "urgencia_prob": 0.94, "categoria": "seguridad", "severidad": 3.0}
     ]
   }
   ```
4. **Oracle evalúa esa evidencia en L1 de forma determinista:**
   ```oracle
   medida auditoria.incidente_grave_requiere_escalamiento
   desde de clasificacion_incidente inc
   donde inc.categoria == "seguridad" y inc.urgencia_prob >= 0.90 y inc.severidad > 2.0
   resumen contar 1
   umbral <= 0 segun contrato "incidentes criticos de seguridad deben escalarse de inmediato"
   alcance "Audita el enrutamiento sobre los escalares provistos por el sensor. NO verifica la veracidad de la inferencia de Jev ni si el incidente fue real."
   ```

**A costa de qué:**  
El costo es epistemológico y queda perfectamente delimitado por los niveles inferiores:
- En **L−1**, la relación debe declarar que sus campos provienen de una inferencia estadística y su `alcance` debe explicitar que la veracidad de la inferencia no está garantizada.
- En **L−2**, se deben conservar las huellas (SHA-256 del texto de entrada, identificador y versión del modelo Jev) como referente de frescura para que la evidencia sea reproducible.

---

### 3.2 ¿La juzgaría desde afuera?
Este es el papel natural y más potente de Oracle respecto a tecnologías como Jev, replicando exactamente el enfoque adoptado con Aura en `estudios/AURA-Y-ORACLE.md`: **Oracle como el tribunal determinista e independiente que juzga los resultados producidos por un motor de IA**.

Cuando un sistema de producción adopta Jev, su atractivo comercial (milisegundos de respuesta y costo marginal cero en salida) conducirá inevitablemente a que el software tome miles de decisiones automáticas por minuto sin intervención humana. Aquí reaparece con virulencia la **Ley de Goodhart**:
- Si el sistema se apoya ciegamente en que las decisiones con probabilidad calibrada > 0.8 son «seguras», el modelo optimizará localmente su calibración RLCD, pero el 20% de error residual provocará fallos sistemáticos agregados.
- Jev puede decidir que 50 transacciones sospechosas son «legítimas» de forma individual porque cada una tiene un `noul: 0.75`; pero la combinación relacional de esas 50 transacciones apuntando a una misma cuenta bancaria en menos de diez minutos es un fraude evidente.

#### El rol de Oracle como auditor externo
Jev toma las micro-decisiones; los sensores del sistema vuelcan el historial de decisiones tomadas a un registro de hechos JSON; y **Oracle actúa como compuerta de aseguramiento y CI**:

```
 ┌──────────────────────┐        ┌──────────────────────┐        ┌──────────────────────┐
 │     TERRENO REAL     │───────▶│    MOTOR JEV (S1)    │───────▶│ ACCIÓN EN PRODUCCIÓN │
 │ (Entrada no estruct) │        │ (Decisión rápida S1) │        │ (Enrutamiento/pago)  │
 └──────────────────────┘        └──────────┬───────────┘        └──────────────────────┘
                                            │
                                            ▼ (Registra decisiones)
                                 ┌──────────────────────┐
                                 │     SENSOR L0        │
                                 │ (Volcado a hechos)   │
                                 └──────────┬───────────┘
                                            │
                                            ▼ (Evidencia relacional)
                                 ┌──────────────────────┐
                                 │  TRIBUNAL ORACLE     │
                                 │  - Álgebra L1 / L2   │
                                 │  - Servidor MCP      │
                                 │  - Rechazo fail-close│
                                 └──────────┬───────────┘
                                            │
                                            ▼ (Veredicto y testigos)
                                 ┌──────────────────────┐
                                 │ ALERTA DE COMPLIANCE │
                                 │ VERDE / ROJO + ALCANCE│
                                 └──────────────────────┘
```

A través de la herramienta `oracle_juzgar` expuesta por el servidor MCP de sólo lectura (`estudios/MCP-CONTRATO.md`), un pipeline automatizado puede enviar la evidencia de la última hora de operación. Oracle verificará:
- **Invariantes relacionales:** ¿Hay decisiones contradictorias emitidas sobre un mismo sujeto dentro de una ventana temporal?
- **Cotas de sombra y límites operativos:** ¿La tasa de rechazos o derivaciones hacia un departamento superó la capacidad física del equipo humano?
- **Ausencia de complacencia:** Gracias al operador `requiere`, si el sensor no emitió registros de auditoría, Oracle emitirá `SIN EVIDENCIA` e impedirá que el pipeline asuma un falso verde.

---

### 3.3 ¿Compite con Oracle?
**La respuesta es un NO categórico.** No compiten, no se sustituyen y no resuelven el mismo problema. Pertenecen a familias conceptuales completamente ortogonales dentro de la ingeniería de software:

| Dimensión | Jev (TypeSafe AI) | Oracle (`oracle-metalenguaje`) |
|---|---|---|
| **Naturaleza fundamental** | Modelo de inferencia estadística probabilística (*System 1*). | Metalenguaje determinista y simbólico de medición y rechazo. |
| **Sustrato matemático** | Redes neuronales profundas entrenadas por optimización de gradiente y RLCD. | Álgebra relacional de seis operadores clausurados sobre bolsas finitas de hechos. |
| **Espacio de entrada** | Datos no estructurados (texto en lenguaje natural, strings arbitrarios). | Evidencia estructurada en relaciones nombradas de tuplas escalares homogéneas. |
| **Forma de salida** | Primitivas tipadas probabilísticas (`Noul` [0–1], `Choice`, `Score`) con confianza estimada. | Veredicto binario (`VERDE` / `ROJO` / `SIN EVIDENCIA`), medición escalar, umbral defendido, testigos ofensores y **alcance explícito**. |
| **Actitud ante el error** | Minimización de pérdida estadística. Tolera una tasa de error residual esperada. | **Fail-closed.** Ante un campo ausente, una unidad incompatible o falta de evidencia, detiene la ejecución. |
| **Puntos ciegos** | No declara qué no miró. Asume que el contexto provisto es suficiente. | **El alcance (`alcance`) es obligatorio.** Un veredicto verde enumera explícitamente lo que no inspeccionó. |
| **Resistencia a Goodhart** | Susceptible. Si se usa su score de confianza como criterio de éxito, el modelo optimiza para el evaluador. | Diseñado específicamente contra Goodhart mediante mutación de medidas, corpus de falsación y pruebas diferenciales. |
| **Entorno de ejecución** | SaaS propietario en la nube (dependencia de API HTTP externa y credenciales). | Paquete Python puro (3.11+), offline, sin dependencias externas, local e integrable en CI. |

#### Qué hace mejor Jev que Oracle:
1. **Comprensión de lenguaje natural desestructurado:** Jev puede interpretar un párrafo ambiguo, identificar tono emocional o extraer intención categórica en 100 ms. Oracle es totalmente incapaz de leer prosa o interpretar texto no tabular; requiere que los hechos hayan sido convertidos previamente en números y cadenas discretas por un sensor.
2. **Generalización ante variaciones lingüísticas imprevistas:** Jev absorbe sinónimos, faltas de ortografía o giros idiomáticos sin requerir una regla escrita a mano para cada variación.

#### Qué hace peor Jev que Oracle:
1. **Garantía determinista de invariantes:** Jev no puede garantizar que una regla lógica se cumpla el 100% de las veces. Sus juicios son aproximaciones probabilísticas.
2. **Composición relacional de hechos:** Jev no tiene capacidad de unir entidades heterogéneas (`unir`), calcular ausencias relacionales mediante anti-juntas (`sin`) ni realizar agregaciones particionadas (`agrupar`).
3. **Honestidad epistemológica:** Jev no tiene el concepto de límite de visión ni de punto ciego; Oracle convierte la declaración de ignorancia en el artefacto central de su entrega.

---

## 4. Veredicto en una página y tareas propuestas

### 4.1 Veredicto
**Jev representa una evolución saludable y madura en el ecosistema de IA aplicada al software:** abandonar la fantasía de utilizar LLMs generativos autorregresivos pesados para resolver problemas que sólo exigen clasificación rápida y tipada. Al adoptar el paradigma «System One» y entrenar para calibración probabilística con RLCD en lugar de complacencia humana con RLHF, TypeSafe AI reduce drásticamente latencias y costos en operaciones rutinarias de enrutamiento y filtrado.

Sin embargo, **abaratar y acelerar las decisiones probabilísticas en un factor de 400 no resuelve el problema de la verdad en el software: lo vuelve más urgente.**

Cuando un sistema reemplaza código determinista por miles de micro-inferencias estadísticas por minuto, el riesgo de degradación silenciosa y la ley de Goodhart se multiplican. Ninguna red neuronal, por calibrada que esté, puede ser su propio auditor.

La relación óptima entre ambas tecnologías es de **complementariedad estricta en capas separadas**:
1. **Jev en el terreno / sensores (L0):** Extrae orden a partir del caos del lenguaje natural y emite hechos estructurados con probabilidades calibradas.
2. **Oracle en el juicio / compuerta (L1 / L2):** Sostiene las reglas invariantes del sistema, evalúa los hechos de forma determinista y rechaza cualquier estado que vulnere las cotas de seguridad del negocio, obligando a declarar qué parte del mundo quedó fuera de la vista.

---

### 4.2 Tareas propuestas para el tracker de Oracle
Para que Claude las evalúe y cree formalmente en el tracker de Oracle, se proponen las siguientes iniciativas técnicas:

1. **`sensor-systemone-l0-contrato`**  
   *Por qué:* A medida que los proyectos consumidores de Oracle integren modelos «System One» (como Jev o Laya) para procesar texto libre, se requiere un patrón arquitectónico estándar de sensor L0 en Python. La tarea consiste en documentar y especificar el esquema de relación canónico en `relaciones/` para capturar inferencias probabilísticas (campos requeridos: `decision_id`, `probabilidad_calibrada`, `confianza`, `latencia_ms`, más los metadatos L−2 de huella de prompt y versión del modelo).
2. **`meta-medida-comparacion-probabilistica`**  
   *Por qué:* Las medidas que juzguen evidencia producida por modelos probabilísticos tenderán a comparar probabilidades (flotantes entre 0 y 1). Es necesario incorporar una medida meta en el catálogo de proceso que vigile que ningún proyecto escriba umbrales con igualdad exacta sobre salidas de modelos estadísticos y que toda regla que filtre por confianza declare obligatoriamente en su `alcance` el margen de error residual del modelo clasificador.
3. **`estudio-auditoria-decisiones-mcp`**  
   *Por qué:* Demostrar empíricamente cómo un servicio en producción que utiliza Jev para clasificar transacciones o enrutar eventos puede invocar periódicamente a `oracle_juzgar` mediante el protocolo MCP para auditar la salud relacional de su base de decisiones, deteniendo el flujo ante la detección de anomalías agregadas.
