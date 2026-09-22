# Postmortem de la batalla naval hecha por agy con Oracle y sin Oracle

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: oracle, postmortem, agentes


## Qué pasó

El 2026-09-18 Brian le pidió a agy (Gemini 3.8 Flash) el mismo juego de batalla naval dos veces: una
usando Oracle y otra sin. Todo está en `/home/workstation/Dev/lab/batalla_naval_test/`:
- `batalla_naval_con_oracle/` — con `oracle.json`, `catalogos/` (¡vacío!), `corpus/`, `diferencial/`,
  `tareas/` (una tarea) y el juego;
- `batalla_naval_sin_oracle/` — el juego sin Oracle, con audio, radar en canvas, más UX;
- `el_porque_de_agy.md` — la explicación que dio agy: ~60 % de su atención se fue en el ritual de
  Oracle (instalar, `init`, tareas, casos, `oracle test`, anotar) y la versión sin Oracle salió casi
  el doble de completa.
Los registros del CLI de agy de esos días están en `~/.gemini/antigravity-cli/log/` (los de fecha
2026-09-18; pueden estar en otra carpeta de `~/.gemini/`).

Brian: «pasó algo raro; quiero un postmortem y ver si se desprenden tareas para mejorar».

## Qué hacer (Codex)

Un postmortem **sin culpas y con evidencia**, en `estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md` de Oracle:
1. **Qué se construyó en cada versión**, medido (archivos, tamaño, funciones, qué reglas del juego
   cumple cada una). Corré los dos juegos si hace falta (son HTML; con node se puede cargar la
   lógica). ¿La versión con Oracle **midió algo del juego**? `catalogos/` está vacío: ¿qué verificó
   entonces `oracle test`, y qué decía su verde?
2. **Qué hizo agy con Oracle, paso a paso**, desde los logs: qué comandos, qué errores, cuánto tiempo
   o cuántos turnos se fueron en qué. Contrastá con lo que dice `el_porque_de_agy.md`: ¿es cierto?
3. **Por qué**: ¿Oracle se presentó como ritual obligatorio en vez de como herramienta?, ¿falta un
   camino corto para un proyecto nuevo?, ¿el verde vacío de un catálogo sin medidas debería ser rojo
   o una advertencia?, ¿la guía (`~/TestOracleEjemplo/GUIA22.md`, el README) empuja a eso?
4. **Tareas que se desprenden**: creálas en el tracker de Oracle (`python3 tools/cli.py tarea nueva …
   --sufijo <corto>`), cada una con la evidencia y `## Próximo paso`. Sólo las que el análisis
   sostiene.

No modifiques nada en `/home/workstation/Dev/lab/`. Commits en Oracle con
`20260919-134424-naval-pm: …`; al terminar, anotá en esta tarea el resumen y la lista de tareas
creadas. **No hagas push y no la cierres**: la revisa Claude.

## Próximo paso

Bloqueada en Brian. Las dos tareas que se desprendían ya están hechas y cerradas
(`test-alcance`, `primer-valor`). Lo único pendiente es la cronología (¿es cierto el «60 %» que dice
agy?), y para eso hacen falta las sesiones de agy del 2026-09-18: en esta máquina no están
(`~/.gemini/antigravity-cli/conversations` y `log/` saltan del 17 al 19) y las rutas que cita agy
(`/c/holamundo/…`) sugieren que el juego se hizo en otra. Si Brian las exporta, Codex completa la
cronología; si no, se cierra con ese hueco declarado.

### Nota (2026-09-22 20:06:08 UTC)

2026-09-22: réplica con 0.28.0 y un prompt que sugiere en vez de guiar (Brian corrió agy; resultado en ~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280). Esta vez SÍ midió el producto: 11 medidas sobre reglas navales, un sensor propio (js/trace.js) que exporta celda_barco, tiro y partida, y una partida real de 130 tiros juzgada con oracle juzgar — verde en 11 medidas, con la lista de lo que no miró. Comprobado por Claude: al corromper la evidencia, cada mentira cae con la medida correcta y salida 1 (impacto→agua: veracidad_impacto_negativo; agua→impacto: veracidad_impacto_positivo; tiro fuera: tiros_dentro_del_tablero). Debilidad honesta: su corpus tiene 2 casos y oracle test da ROJO por mutación, con 2 mutantes vivos que confunden fila con columna. Diferencia con el 18/09: entonces catalogos/ estaba vacío y el verde no medía nada del juego.
