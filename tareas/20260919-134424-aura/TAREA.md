# ¿Se puede construir con Oracle un agente de videojuegos como Aura?

- ESTADO: CERRADA
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

Claude revisa `estudios/AURA-Y-ORACLE.md`.

### Nota (2026-09-19 13:49:12 UTC)

2026-09-19, Brian: la idea es hacer un Aura propio para Godot, Unity y Unreal usando Oracle. La investigación tiene que responder eso: qué partes serían propias (el agente, los sensores por motor, el puente al editor) y cuáles ya existen; qué sería Oracle ahí (juez de cada cambio del agente, con medidas por motor escritas en superficie); qué ya está probado en casa (Jam en Unreal: sensor puro + adaptador, sondas headless; LyraGASP) y qué no (Godot y Unity: cero). Un corte mínimo realista para empezar, en un solo motor.

### Nota (2026-09-19 14:15:17 UTC)

2026-09-19, revisión rápida de Claude: el veredicto (Oracle como juez, no como agente; primer corte en Unreal sobre JamPlayground) es sólido. Hay que corregir §3.1: los operadores son de, donde, unir, sin, agrupar y resumen (requiere no es un operador) y 'si le sobreviven mutantes el sistema la rechaza' exagera. Los datos de §1 sobre Aura (estudio, agentes, fechas) vienen de la web y no se verificaron contra las fuentes citadas.

### Nota (2026-09-24 00:51:34 UTC)

2026-09-23, Claude: corregido §3.1 de estudios/AURA-Y-ORACLE.md — los seis operadores son de, donde, unir, sin, agrupar y resumen (requiere es cláusula), y la mutación o la falta de polaridades ponen rojo oracle test, no rechazan la medida. Queda sin verificar §1 (datos de Aura tomados de la web).

### Nota (2026-09-24 00:57:58 UTC)

2026-09-23, Brian: Aura es un proyecto aparte, ~/Dev/commander, que consume oracle-metalenguaje desde PyPI. Los dos estudios (AURA-Y-ORACLE, AURA-PROPIO-CORTE-1) se mudaron a commander/docs/; la verificación de §1 sigue allá como tarea «fuentes» y el bucle del corte 1 como «corte-1». Las piezas del motor siguen en el tracker de Jam.
