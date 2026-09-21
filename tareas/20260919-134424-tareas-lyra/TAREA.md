# LyraGASP organiza su trabajo pendiente en su propio tracker

- ESTADO: CERRADA
- PRIORIDAD: 85
- ETIQUETAS: lyragasp, proceso, tracker


## Por qué

Brian (2026-09-19): «debemos organizar las tareas de LyraGASP y Jam usando oracle tatr y que queden
en el repo; no podemos depender de la memoria de Claude o de Codex, ni de README.md o *.md dando
vueltas por ahí». Ver [`20260919-134424-relevo`](../20260919-134424-relevo/TAREA.md) para el
protocolo.

## Qué hacer (Codex), en `/home/workstation/Dev/games/unreal/LyraGASP`

1. `oracle tarea init` en la raíz de LyraGASP (la herramienta global `oracle` está en 0.27.0).
2. **Inventario del trabajo pendiente**, leyendo lo que hoy lo guarda: `RELEVO.md`, `AGENTS.md`,
   `docs/`, roadmaps, TODOs en `.md`, notas de estudio, y `git log` reciente. Por cada trabajo
   pendiente real, una tarea: `oracle tarea nueva "<título que diga el problema>" --prioridad <n>
   --etiqueta <…> --sufijo <corto>`, con un cuerpo que diga qué se sabe, dónde está la evidencia y
   `## Próximo paso`. No inventes trabajo: si algo es dudoso, una sola tarea «revisar X» con la cita.
3. **El arranque**: en el archivo de instrucciones del repo (`AGENTS.md` / `CLAUDE.md`), una sección
   corta que diga que el trabajo se retoma con `oracle tarea listar` y `oracle tarea ver <id>`, y
   que un relevo se deja anotando la tarea, no escribiendo otro `.md`.
4. Verificá con `oracle tarea revisar` y `oracle tarea hechos --git` que el tracker quede sano.

⚠ LyraGASP tiene trabajo de Brian SIN COMMITEAR (uassets, C++, `RELEVO.md`, `investigaciones/`, un caso del corpus nuevo). **No lo toques, no lo agregues a ningún commit**: `git add` sólo de `tareas/` y del archivo de instrucciones que edites. Si `RELEVO.md` está modificado sin commitear, leelo pero no lo edites; anotá en esta tarea lo que habría que cambiar.

Commits en LyraGASP, cada uno empezando con el ID de la tarea de LyraGASP que corresponda (la primera:
«<id>: el tracker del proyecto»). **No hagas push.** Al terminar, anotá en ESTA tarea de Oracle
(`cd /home/workstation/Dev/oracle && python3 tools/cli.py tarea anotar 20260919-134424-tareas-lyra
"…"`) cuántas tareas quedaron, las cinco más prioritarias y qué no pudiste decidir, y commiteá esa
nota en Oracle como `20260919-134424-tareas-lyra: inventario`. No la cierres: la cierra Claude después
de revisar.


### Nota (2026-09-19 14:05:33 UTC)

Inventario realizado en LyraGASP con Oracle 0.27.0: 28 tareas abiertas (27 pendientes/revisiones y 20260919-135921-tracker para la implantación). Se inicializó tareas/, se agregó el protocolo de retomar/anotar/Próximo paso/commits en CLAUDE.md y cada tarea tiene qué se sabe, evidencia y próximo paso único al final. La tarea de implantación contiene la matriz de fuentes y decisiones, incluidos descartes históricos: rendimiento 10 ms aceptado, altura/torso aceptados, test_extrae_curvas corregido en 44ae17da, Oracle actualizado a 0.27.0 y rediseno-impacto descartada en a302ca8a.
Las cinco más prioritarias del listado actual son: P100 20260919-135921-tracker (confirmar y verificar tracker); P95 20260919-140308-dedos (deformación visible); P94 20260919-140308-centrado (rifle bajo en cadera/hombro); P93 20260919-140308-recarga (recarga completa en pawn); P92 20260919-140308-foregrip (mano separada/offset fijo). Excluida la implantación, la quinta de producto es P90 20260919-140308-dano-red (revisar equipos/daño).
No pude decidir sin nueva evidencia o Brian: vigencia de deudas antiguas de equipos, inputs/efectos, firewall y mutación de sensores; malla/regiones exactas para ML Deformer tras cambiar al cuerpo entero y futuro ensamblado, más autorización de jeans con fragmentación visible; respaldo/LFS y deploy que Brian había diferido; segundo tipo de arma y alcance de traversal/interacciones/NPC. Son tareas de revisión/decisión, no causas inventadas ni compras autorizadas. La evidencia del 11 sobre dedos no equivale a piel sana, y la recarga de preview no equivale a aceptación en juego.
RELEVO.md fue leído sin editar: sus cambios siguen siendo de Brian. Después de su revisión habría que sustituir la agenda vieja por referencia al tracker y preservar la evidencia histórica; README también remite al relevo de BotOO. Se dejó 20260919-140309-relevos-viejos para hacerlo con alcance autorizado, pues esta tarea sólo permite tareas/ y el archivo de instrucciones. Los 82 archivos ajenos inventariados (assets, C++, RELEVO, investigaciones, corpus, tests y herramientas) conservaron exactamente sus SHA-256.
Verificación: oracle tarea revisar = 28 válidas; oracle tarea hechos --git y seguimiento --json completan la lectura. Al juzgar contra ejemplo/seguimiento-tareas, sólo archivos_confirmados_sin_cambios=29 está rojo (28 TAREA.md y README generado aún sin commit); las otras cinco medidas dan 0. CLAUDE.md pasa git diff --check y los 28 cuerpos pasan revisión de espacios y sección final. No se corrieron pruebas de gameplay para este cambio exclusivamente documental.
Bloqueo real: git add -- tareas/ CLAUDE.md en LyraGASP falló con fatal: Unable to create .git/index.lock: Read-only file system. También un diff general intentó crear temporal LFS bajo .git/lfs/tmp y falló por solo lectura; no se modificaron filtros ni assets. No se creó ningún commit ni se hizo push. Queda preparado el commit LyraGASP 20260919-135921-tracker: el tracker del proyecto y el de esta nota 20260919-134424-tareas-lyra: inventario. No cierro esta tarea: corresponde a Claude después de revisar.

### Nota (2026-09-19 14:06:03 UTC)

Confirmado también el bloqueo en Oracle: git add -- tareas/20260919-134424-tareas-lyra/TAREA.md falló con fatal: Unable to create /home/workstation/Dev/oracle/.git/index.lock: Read-only file system. El commit de la nota no pudo crearse; no se incorporó ningún cambio ajeno ni se hizo push.

## Próximo paso

Retomar con escritura habilitada en `.git` de LyraGASP y Oracle; el entorno actual no permite crear `.git/index.lock` en ninguno de los dos. El inventario está preparado y revisado, pero sin commits.

1. En LyraGASP, revisar `oracle tarea ver 20260919-135921-tracker` y confirmar sólo `tareas/` y `CLAUDE.md` con `20260919-135921-tracker: el tracker del proyecto`. No agregar assets, C++, RELEVO.md, investigaciones, corpus, tests ni herramientas de Brian. Mantener los hooks y no hacer push.
2. Ejecutar `oracle tarea revisar` y `oracle tarea hechos --git > /tmp/lyra-tareas-hechos.json`; desde Oracle juzgar con `python3 tools/cli.py juzgar --proyecto ejemplo/seguimiento-tareas --con /tmp/lyra-tareas-hechos.json`. Resolver el seguimiento pendiente sin incorporar cambios ajenos. Completar el cierre de la tarea local de implantación con su ID y commit `done` cuando corresponda.
3. Anotar aquí los hashes y veredictos finales; confirmar únicamente `tareas/20260919-134424-tareas-lyra/TAREA.md` como `20260919-134424-tareas-lyra: inventario` en Oracle. Si aparecen nuevos bloqueos, anotarlos y reemplazar este paso.
4. Dejar esta tarea de Oracle ABIERTA para que Claude revise el inventario y decida el cierre. Revisar con Brian las decisiones enumeradas en la nota; el siguiente pendiente de producto es `20260919-140308-dedos`. No editar RELEVO.md mientras contenga sus cambios sin commit.
