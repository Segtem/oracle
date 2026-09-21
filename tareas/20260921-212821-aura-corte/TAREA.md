# El primer corte de un Aura propio: un agente que coloca en Unreal y Oracle lo juzga

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, agentes, unreal, aura


## Por qué

Brian quiere un Aura propio para Godot, Unity y Unreal usando Oracle. La investigación
([`20260919-134424-aura`](../20260919-134424-aura/TAREA.md), `estudios/AURA-Y-ORACLE.md`) concluye
que Oracle sería el **juez**, no el agente, y propone empezar por un solo motor: Unreal sobre
JamPlayground, donde ya existen Jam (sensor puro + adaptador), sondas headless y medidas de colocación.

## Qué hacer (agy, sin shell)

Un plan de implementación concreto en `estudios/AURA-PROPIO-CORTE-1.md`, verificable, **sin código**:
1. **El ciclo**: pedido → el agente coloca con las herramientas de Jam → sonda del sensor en
   JamPlayground (headless, `-ExecCmds`, ver `~/CLAUDE.md` y `~/Dev/jam/AGENTS.md`) → hechos JSON →
   `oracle juzgar` / `oracle_juzgar` por MCP → si rojo, corregir con los testigos → verde → confirmar.
2. **Qué ya existe y qué falta**, archivo por archivo: leé `~/Dev/jam/Content/Python/jam/`,
   `~/Dev/jam/tools/experiments/`, `~/Dev/jam/medidas/` (catálogos y relaciones de colocación) y el
   tracker de Jam (`~/Dev/jam/tareas/`). Nombrá las medidas de Jam que servirían de juez tal como
   están, y las que faltan.
3. **El primer escenario de prueba**, chico y medible (por ejemplo, colocar N piezas sin
   interpenetración contra un muro): qué pide el usuario, qué hechos salen, qué medida decide, cuál es
   el rojo y cuál el verde.
4. **Quién es el agente en el corte 1**: Claude Code o Codex con el MCP de Oracle y las herramientas
   de Jam, no un orquestador nuevo. Decí qué herramienta del lado de Unreal le falta (si le falta).
5. **Riesgos y lo que queda fuera** (Godot y Unity van después; cuándo y con qué sensores).

Al final, reemplazá `## Próximo paso` con las tareas concretas que se desprenden (Claude las crea en
el tracker que corresponda: Oracle o Jam).

## Próximo paso

agy lee esta tarea y escribe el plan.
