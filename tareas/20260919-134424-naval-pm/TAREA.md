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

Claude revisa estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md y las tareas derivadas 20260919-135054-test-alcance y 20260919-135054-primer-valor. Para completar la cronología pendiente, recuperar/exportar las sesiones originales del 2026-09-18 de la máquina/cuenta donde se usaron /c/holamundo/batalla_naval y /taller/batalla-naval: no están en los logs ni en el índice local de ~/.gemini. Con esos registros, contar llamadas/turnos, errores y ventanas de tiempo; el 60 % sigue sin verificar. Mantener ABIERTA para revisión.


Además, completar el commit desde un entorno con escritura en `.git` (aquí `git add` y `git commit` fallan al crear `index.lock`: Read-only file system). El trabajo está en el árbol, todavía sin commit. Incluir sólo estos archivos; no incluir el archivo ajeno `estudios/AURA-Y-ORACLE.md`:

```bash
git add estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md estudios/naval-pm tareas/20260919-134424-naval-pm/TAREA.md tareas/20260919-135054-test-alcance/TAREA.md tareas/20260919-135054-primer-valor/TAREA.md
git commit -m '20260919-134424-naval-pm: documentar postmortem naval con reproducciones y tareas'
```

No hacer push ni cerrar la tarea.

### Nota (2026-09-19 13:47:49 UTC)

Bloqueo parcial de evidencia histórica: no hay logs del 2026-09-18 en ~/.gemini/antigravity-cli/log/; búsqueda textual en ~/.gemini sin referencias a batalla naval ni 001-flota-completa. Continúo con inventario, ejecución de lógica y reproducción del veredicto en copia temporal. Los comandos, errores, tiempos y turnos históricos no se pueden afirmar sin recuperar la sesión original.

### Nota (2026-09-19 13:54:21 UTC)

Postmortem escrito en estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md con inventario SHA-256, arneses y salidas reproducibles en estudios/naval-pm/. Producto: 46.361 vs 79.807 bytes ejecutables; ambos pasan pruebas básicas de lógica y presentan límites de reinicio reproducidos. Oracle no midió reglas navales: caso estático de sintaxis; test --rapido verde incluso rompiendo JS en copia, test completo rojo con 4 mutantes sobrevivientes. Tareas creadas: 20260919-135054-test-alcance y 20260919-135054-primer-valor. Bloqueo histórico: sin sesiones originales no se pueden reconstruir comandos/errores/turnos ni verificar 60 %. Próximo paso actualizado para Claude y recuperación de logs. No se modificó el laboratorio; se mantiene ABIERTA y sin push.

### Nota (2026-09-19 13:55:01 UTC)

Bloqueo de entrega: git add y git commit fallaron con Unable to create .git/index.lock: Read-only file system. Este entorno permite editar el trabajo pero monta .git en sólo lectura; no se creó ningún commit ni se hizo push. Validaciones finales: tarea revisar OK (48 tareas), git diff --check limpio, enlaces locales válidos y SHA-256 del laboratorio sin cambios. Commit preparado: 20260919-134424-naval-pm: documentar postmortem naval con reproducciones y tareas. Existe un archivo ajeno no versionado estudios/AURA-Y-ORACLE.md; no incluirlo.
