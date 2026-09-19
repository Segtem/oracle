# ¿Se puede construir con Oracle un agente de videojuegos como Aura?

- ESTADO: ABIERTA
- PRIORIDAD: 60
- ETIQUETAS: oracle, investigacion, agentes


## La pregunta

Brian (2026-09-19): vio https://www.tryaura.dev/, un agente para construir videojuegos en Unreal y
Unity, y pregunta si Oracle sirve para construir algo parecido.

## Qué hacer (agy, con acceso a la web)

Investigación, **no código**. Escribí `estudios/AURA-Y-ORACLE.md` en Oracle:
1. **Qué es Aura**, con fuentes (su sitio, docs, demos, anuncios): qué hace, cómo se integra con el
   editor (plugin, MCP, API), qué modelo usa, qué verifica y qué no, precio y límites. Distinguí lo que
   dicen de lo que muestran.
2. **Qué hay alrededor**: otros agentes para motores de juego (MCP de Unreal y Unity, etc.) y qué
   hacen para no romper un proyecto.
3. **Dónde entraría Oracle**. Leé primero `README.md`, `ESPECIFICACION.md` §0-3, el MCP
   (`estudios/MCP-CONTRATO.md`) y cómo lo usan Jam (`~/Dev/jam/AGENTS.md`) y LyraGASP
   (`~/Dev/games/unreal/LyraGASP/docs/ORACLE.md`). Oracle no genera contenido: mide evidencia contra
   medidas declaradas, con alcance y falsación. La hipótesis a poner a prueba es que Oracle sería **el
   juez** de un agente así —lo que distingue «el agente dice que anduvo» de «se midió que anda»—, no el
   agente. Buscá también la hipótesis contraria.
4. **Un veredicto** en una página: viable o no, qué faltaría (en Oracle, en Jam, en sensores de
   Unreal), y los riesgos. Si surge trabajo concreto, listalo al final como tareas propuestas con su
   porqué; Claude las crea.

Sin shell: sólo lectura, edición y web. No toques código. Al final, en esta tarea, reemplazá
`## Próximo paso` con «Claude revisa `estudios/AURA-Y-ORACLE.md`».

## Próximo paso

agy lee esta tarea y la hace.
