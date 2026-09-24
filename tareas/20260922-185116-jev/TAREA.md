# JEV de TypeSage: qué es y qué haría Oracle con una tecnología así

- ESTADO: CERRADA
- PRIORIDAD: 60
- ETIQUETAS: oracle, investigacion, agentes


## La pregunta

Brian (2026-09-22): investigar **JEV, de TypeSage IA**, y cómo Oracle usaría una tecnología de ese
estilo. El nombre viene de oído: lo primero es confirmar qué es y cómo se escribe de verdad (empresa,
producto, siglas), y decir con qué fuentes se confirmó. Si resulta que no existe con ese nombre,
decirlo y nombrar lo más parecido que sí exista, sin inventar.

## Qué hacer (investigación, con web; sin código)

Escribir `estudios/JEV-Y-ORACLE.md`:

1. **Qué es**, con fuentes citadas (sitio, documentación, papers, demos, anuncios). Qué problema dice
   resolver, cómo se integra, qué necesita para correr, precio y límites. Separar **lo que dicen** de
   **lo que muestran**: si promete verificar algo, mirar qué verifica exactamente y contra qué.
2. **Qué hay alrededor**: dos o tres alternativas del mismo estilo, y en qué se diferencian.
3. **Dónde tocaría a Oracle.** Leer antes `README.md`, `ESPECIFICACION.md` §0-§3 y
   `estudios/MCP-CONTRATO.md`. Contestar las tres por separado, porque son distintas:
   - **¿Oracle la usaría adentro?** ¿Para qué parte —sensores, álgebra, mutación, tracker— y a costa
     de qué? Recordar la regla: conectar un consumidor no debe exigir tocar `nucleo/`.
   - **¿La juzgaría desde afuera?** Es el papel que ya se le dio en
     `estudios/AURA-Y-ORACLE.md` (desde el 2026-09-23 en `~/Dev/commander/docs/`): Oracle como juez determinista de
     lo que produce otra herramienta.
   - **¿Compite con Oracle?** Si hace lo mismo, decirlo derecho, con qué hace mejor y qué peor.
4. **Un veredicto en una página** y, si sale trabajo concreto, listarlo al final como tareas
   propuestas con su porqué. Claude las crea; no crear tareas desde acá.

No afirmar nada que no esté en una fuente citada. Si algo no se puede confirmar, escribirlo como
pregunta abierta.

## Avance

- **Identidad real confirmada (2026-09-22):**
  - Empresa: **TypeSafe AI** (San Francisco, fundada en 2024 por Diogo Almeida —coautor de RLHF, *InstructGPT* y GPT-4 en OpenAI—, Erik Gafni y Sasha Sheng). Fuente: `typesafe.ai`.
  - Producto: **Jev** (nombrado en honor al economista William Stanley Jevons y su paradoja sobre el incremento en el consumo tras la eficiencia). Lanzado el 15 de septiembre de 2026 en acceso temprano limitado (*waitlist* en `console.typesafe.ai`).
  - No es «TypeSage» (error fonético común) ni siglas en mayúsculas.
- **Naturaleza técnica:**
  - Modelo de decisión «System One» (basado en la distinción de Daniel Kahneman entre pensamiento rápido e intuitivo vs analítico lento).
  - No genera texto ni usa decodificación autorregresiva token por token. Evalúa un estado plano (`state`) contra un mapa de preguntas (`questions`) en un único pase hacia adelante en paralelo (*parallel sampling*).
  - Entrenado con RLCD (*Reinforcement Learning for Calibrated Decisions*) para calibración probabilística en vez de complacencia conversacional humana.
  - Primitivas tipadas de salida: `Noul` (probabilidad bayesiana continua entre 0.0 y 1.0), `Choice` (selección categórica entre hasta 255 opciones con distribución y confianza) y `Score` (escala normalizada ordinal/interpolada con confianza).
  - Costo: $0.042 USD / 1M tokens de entrada; salida gratuita (*unmetered*). Latencia: 70 a 500 ms.
  - API: HTTP POST único en `https://api.typesafe.ai/v1/systemone` y SDKs (`typesafe-sdk`, `@typesafe-ai/sdk`). Modelo SaaS cerrado y dependiente de red; no disponible como pesos abiertos.
- **Ecosistema y alternativas:**
  - Modelos System One sin autorregresión: *Laya* (Convai Innovations, septiembre 2026, open source) y *OpenJev*.
  - Decodificación restringida sobre LLMs generativos: *Outlines* (FSM a nivel de logits) e *Instructor* (validación Pydantic post-generación con reintentos).
  - Clasificadores tradicionales: *Cohere Classify*, *SetFit*, cross-encoders DeBERTa.
- **Relación con Oracle:**
  - **¿Adentro?**: NO en álgebra, mutación ni tracker (destruiría el determinismo, la clausura exacta, la portabilidad offline sin dependencias y la regla de no tocar `nucleo/`). SÍ como implementación de sensores L0 desacoplados en el dominio de consumidores que observan texto no estructurado.
  - **¿Desde afuera?**: Rol central (análogo a Aura en `estudios/AURA-Y-ORACLE.md`). Oracle actúa como tribunal determinista independiente y fail-closed vía MCP (`oracle_juzgar`) para auditar la coherencia global y contener la ley de Goodhart ante el aluvión de micro-decisiones probabilísticas que la paradoja de Jevons fomenta.
  - **¿Compite?**: NO. Son categorías disjuntas: inferencia estadística probabilística sobre lenguaje natural vs metalenguaje determinista de rechazo sobre álgebra relacional de hechos escalares con alcance obligatorio.
- **Entregable:**
  - Estudio completo documentado en [`estudios/JEV-Y-ORACLE.md`](../../estudios/JEV-Y-ORACLE.md), con veredicto estructurado y 3 tareas propuestas para el tracker: `sensor-systemone-l0-contrato`, `meta-medida-comparacion-probabilistica` y `estudio-auditoria-decisiones-mcp`.

## Próximo paso

Revisar `estudios/JEV-Y-ORACLE.md` y evaluar la creación de las tres tareas propuestas (`sensor-systemone-l0-contrato`, `meta-medida-comparacion-probabilistica` y `estudio-auditoria-decisiones-mcp`) en el tracker de Oracle para dar cierre a esta investigación.

### Nota (2026-09-22 18:59:04 UTC)

2026-09-22, revisión de Claude. Comprobado por mí: typesafe.ai responde, su página docs.typesafe.ai/concepts/system-one se titula «System One - TypeSafe AI», y el paquete typesafe-sdk existe en PyPI (0.7.1, autor TypeSafe AI). El nombre que Brian recordaba («TypeSage») era el error y el informe lo corrige bien. NO verificado: OpenRouter no lista hoy ningún modelo con 'jev' ni 'typesafe' en su id, así que esa integración queda como afirmación sin confirmar; tampoco verifiqué fundadores, fechas ni cifras de precio y latencia. Sobre las tres tareas propuestas: NO se crean. Las dos primeras son especulativas —no hay todavía un consumidor de Oracle que use un modelo así—, y Oracle no agrega nada hasta que un segundo usuario real lo pida; además, comparar flotantes por igualdad ya lo vigilan meta.ningun_umbral_de_igualdad y meta.ningun_flotante_comparado_por_igualdad_en_un_filtro. La tercera es un estudio sin usuario. El valor de esta investigación es la conclusión: Jev es un sensor (produce hechos del lenguaje natural, con probabilidad calibrada) y Oracle es el juez; si algún día un consumidor mete un modelo así, esa es la forma, y este estudio es el antecedente.
