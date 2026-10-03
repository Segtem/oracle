# Migrar consumidores a oracle-task y retirar trackertast de PyPI

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 

## Pedido

Migrar todos los repositorios que consumen `trackertast` a `oracle-task` y luego retirar el
proyecto anterior de PyPI. Pedido explícito del usuario el 2026-10-03; reemplaza la decisión
anterior de conservar el paquete publicado. No cambiar los IDs ni los datos de las tareas.

## Inventario y evidencia

- Repositorios locales afectados: Oracle, Oracle Factory, Oracle MCP, Commander, Jam,
  LyraGASP, Oracle Clue y el propio Oracle Task (directorio y remoto aún llamados trackertast).
- PyPI comprobado: oracle-task 0.2.0 publicado; wheel SHA256
  `a1e74360b5d32b6b2d03340bba74ab7ad5026faaaba291590329c52613c4be14`.
- Oracle Factory 0.1.0a1 y Oracle MCP 0.1.1 publicados dependen de trackertast==0.1.0.
  Necesitan nuevos releases: la metadata de una versión publicada es inmutable.
- El release GitHub v0.1.0 de Segtem/trackertast conserva wheel y sdist. La prueba de migración
  debe usar ese archivo histórico con hash para no depender de la futura disponibilidad en PyPI.
- Se conservan URLs válidas del repositorio Segtem/trackertast y referencias históricas.
- Jam incluye Oracle 0.38.1 vendorizado. No editarlo a mano: su alias opcional antiguo se
  actualizará reinstalando el nuevo Oracle después de publicarlo, como exige AGENTS.md de Jam.
- El borrado de PyPI, incluso tras publicar sucesores, romperá instalaciones de las versiones
  antiguas de Factory/MCP que fijaban trackertast. No se puede reescribir esa metadata.


## Avances y verificación

- Dependencias e imports migrados en Factory (0.1.0a2), MCP (0.1.2) y alias opcional Oracle
  (0.38.2). Commander fija oracle-task==0.2.0. Instrucciones Jam/LyraGASP y arquitectura Clue
  actualizadas. Factory implementado en rama y unido por fast-forward a main.
- Oracle: 2258 tests verdes. Mutación --alto de nucleo/version.py y tools/cli.py: 815/815
  muertos, 0 sobrevivientes, timeouts o errores de arnés; evidencia resumida adjunta.
- Oracle MCP: 156 tests verdes. Los fixtures ahora crean tareas con Oracle Task directamente.
- Factory: 23 tests y 11 comprobaciones Chromium; ejemplo completo desde wheel instalado,
  fuera del checkout y sin oracle/tasks globales. Twine valida sus dos artefactos y los de MCP.
- Wheel Oracle 0.38.2 en entorno nuevo con Oracle Task 0.2.0: alias tarea lee y anota el mismo
  ID sin módulo trackertast.
- Migración uv desde artefacto histórico GitHub v0.1.0 (hash fijado): datos e IDs intactos,
  ambos comandos leen/anotan/cierran/reabren y emiten hechos. No necesita trackertast en PyPI.
- Instalación global cambiada a oracle-task 0.2.0; también .venv de Commander, MCP y Oracle Task.
- LyraGASP: corpus de 194 casos, aceptación verde (sombras declaradas conservadas), 487 mutantes
  muertos sin sobrevivientes. Jam: tests pasan fuera del sandbox; relevo pendiente del push.
- Inventario: 22 repositorios locales revisados; sin cambios en snapshots/temporales/vendor.
  Los dos repositorios remotos Segtem/Segtem y Segtem/jamprotocol-deprecated no tienen
  referencias vigentes. La búsqueda GitHub indexada no se usa como prueba de exhaustividad.

## Publicación y retiro pendientes

No hay credenciales de publicación configuradas en las variables del entorno ni un navegador
con sesión disponible. El mantenedor publica los wheels/sdist preparados siguiendo el flujo
usado en releases anteriores. Después se verifican PyPI, instalaciones limpias y se actualiza
el Oracle vendorizado de Jam reinstalando el artefacto publicado, según AGENTS.md de Jam.

Borrar trackertast rompe la instalación de las versiones antiguas de Factory/MCP. El nuevo
código no puede cambiar esa metadata histórica. El retiro solicitado se hace después de
publicar/verificar los sucesores, con acceso a la cuenta PyPI.

## Próximo paso

Empujar los ocho repositorios y publicar tags/releases GitHub de Oracle 0.38.2, Factory
0.1.0a2 y MCP 0.1.2. El mantenedor sube esos artefactos a PyPI; comprobar las publicaciones,
actualizar el vendor de Jam y retirar trackertast desde la cuenta PyPI.
