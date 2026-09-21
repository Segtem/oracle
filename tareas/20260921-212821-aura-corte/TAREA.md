# El primer corte de un Aura propio: un agente que coloca en Unreal y Oracle lo juzga

- ESTADO: CERRADA
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

## Avance

- Se inspeccionó el repositorio de Jam (`~/Dev/jam/Content/Python/jam/`, `~/Dev/jam/tools/experiments/`, `~/Dev/jam/medidas/`, `~/Dev/jam/tareas/`), el contexto del entorno (`~/CLAUDE.md`, `~/Dev/jam/AGENTS.md`, `~/Dev/jam/RELEVO.md`) y el estudio previo (`estudios/AURA-Y-ORACLE.md`).
- Se redactó el plan de implementación completo y sin código en [`estudios/AURA-PROPIO-CORTE-1.md`](../../estudios/AURA-PROPIO-CORTE-1.md) cubriendo los cinco puntos requeridos:
  1. El ciclo completo de 7 pasos: pedido, colocación provisional (`jam:preview`), sonda headless en `JamPlayground` (`-ExecCmds`), extracción de hechos L0 a `Saved/Oracle/escena.json`, evaluación determinista vía MCP/CLI, corrección geométrica guiada por testigos numéricos ante ROJO y confirmación final ante VERDE.
  2. Diagnóstico archivo por archivo en Jam (`jam/place.py`, `jam/snap.py`, `jam/ue.py`, `jam/geometry.py`, `jam/oracle_shadow.py`, sondas en `tools/experiments/`, catálogos en `medidas/catalogos/geometria/` y `physics/`, y el tracker en `tareas/`). Se identificaron las 6 medidas existentes que sirven tal cual (`colocacion.interpenetracion`, `colocacion.bounds`, `snap.al_ras`, `snap.comparte_cara`, `snap.grilla`, `physics.apoyado`) y las faltantes (`colocacion.tanda_sin_interpenetracion`, `colocacion.asentada_en_terreno`, `colocacion.zona_permitida`, más la formalización de esquemas en `medidas/relaciones/`).
  3. El primer escenario de prueba acotado y medible: colocación de dos cubos estándar de 100 cm contra un muro de 400×20×200 cm, con inyección de penetración y desvío de contacto (ROJO con testigos concretos), ajuste guiado por deltas y resolución final en VERDE.
  4. Definición del agente ejecutor: Claude Code o Codex en terminal host sin orquestadores intermedios, identificando la herramienta faltante del lado de Unreal (un script/interfaz CLI headless parametrizable `jam_colocar` para spawnear y emitir hechos fuera de Slate).
  5. Análisis de riesgos (latencia de arranque de UE, Goodhart de 1º y 2º orden, falsos positivos por AABB en mallas no convexas) y exclusión explícita de Godot y Unity para fases posteriores junto con sus respectivos sensores.
- No se corrieron comandos de shell ni verificaciones dinámicas (se respetó estrictamente la restricción de sólo lectura y edición).

## Próximo paso

Claude crea en los trackers correspondientes las tareas concretas que se desprenden del plan:

1. **En Jam (`~/Dev/jam`):**
   - `sonda-escena-l0`: Crear `tools/experiments/sonda_colocacion_aura.py` y la función en `jam/ue.py` para extraer y serializar las relaciones L0 (`pieza`, `vecina`, `asentamiento`) a `Saved/Oracle/escena.json` desde `JamPlayground` headless.
   - `herramienta-colocar-cli`: Exponer un comando headless parametrizable (`tools/jam_colocar.py` o similar) para instanciar actores con tag `jam:preview` y aplicar transformaciones/snap sin interacción manual en Slate.
   - `relaciones-colocacion-l0`: Declarar los esquemas formales en `medidas/relaciones/` (`pieza.json`, `vecina.json`, `asentamiento.json`) para cerrar la sombra `meta.toda_cantidad_comparada_tiene_unidad_derivable` (cota 54).
   - `medida-colocacion-tanda`: Implementar en `medidas/catalogos/geometria/` la medida `colocacion.tanda_sin_interpenetracion` con su corpus y mutación para evaluar lotes de $N$ piezas entre sí.
   - `escenario-corte-1-colocacion`: Arnés de integración que ejerza el bucle del escenario 1 (dos cubos y muro en `JamPlayground`), forzando el paso ROJO → VERDE.

2. **En Oracle (`~/Dev/oracle`):**
   - `mcp-juzgar-ruta-evidencia`: Extender `oracle_juzgar` en `tools/mcp.py` para aceptar una ruta de archivo local en disco (`ruta_evidencia`) como alternativa a enviar la carga útil JSON en memoria por RPC.
   - `medida-requiere-colocacion`: Verificar que todas las medidas de colocación exijan `requiere` para fallar cerrado (`SIN EVIDENCIA`) ante volcados vacíos.

### Revisión de Claude (2026-09-21)

Plan aceptado, con una excepción: **`mcp-juzgar-ruta-evidencia` se descarta.** Que `oracle_juzgar`
reciba una ruta contradice el contrato del MCP (`estudios/MCP-CONTRATO.md`): ninguna herramienta
acepta rutas por llamada, para que una instrucción dentro de un archivo medido no pueda ampliar lo
que el servidor lee. El agente lee el JSON y lo pasa por valor. Las cinco tareas de Jam se crearon en
el tracker de Jam, con el sufijo que propone el plan; `medida-requiere-colocacion` es de Jam también
(sus medidas viven ahí) y va dentro de `medida-colocacion-tanda`.
