# Migrar consumidores a oracle-task y archivar trackertast de PyPI

- ESTADO: CERRADA
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

## Publicación verificada y archivo confirmado

El mantenedor publicó los tres cortes. SHA256 de wheel y sdist coincide con los releases;
instalaciones nuevas de Oracle 0.38.2, Factory 0.1.0a2 y MCP 0.1.2 verificadas en Python 3.13,
sin módulo/distribución trackertast. Factory completó el ejemplo aislado. Jam reinstaló su
vendor desde PyPI 0.38.2, pasó 1448 tests y quedó empujado. Oracle/MCP globales usan ahora
los pins PyPI. Evidencia: resultados.json y notas de esta tarea.

El usuario archivó trackertast y lo confirmó el 2026-10-04 UTC. La API oficial PyPI Simple
1.4 devuelve project-status.status=archived y conserva la versión0.1.0. Este pedido reemplaza
el borrado anterior. El archivo señala que no habrá mantenimiento, pero no elimina paquetes
ni impide instalar versiones históricas. No queda un borrado pendiente. Evidencia adjunta:
trackertast-archive-status.json. Fuente de semántica: https://blog.pypi.org/posts/2025-01-30-archival/.


## Corte preparado

Los ocho repositorios están commiteados y empujados. Releases y tags publicados:

- [Oracle 0.38.2](https://github.com/Segtem/oracle/releases/tag/v0.38.2).
- [Oracle Factory 0.1.0a2](https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a2).
- [Oracle MCP 0.1.2](https://github.com/Segtem/oracle-mcp/releases/tag/v0.1.2).

Cada release tiene wheel, sdist y SHA256SUMS. Los archivos están también en `dist/` de su repo.
Oracle test dio VERDE; mutación de código de módulos cambiados comprobada aparte (815/815).
La web Factory publicada devuelve HTTP 200 y coincide byte por byte con main. CI de MCP,
Factory y Oracle Task dio éxito. Oracle/MCP globales usan los pins PyPI verificados,
junto con Oracle Task publicado; no queda trackertast en esos entornos.

Comandos del corte ya publicado por el mantenedor (registro histórico):

```bash
uv publish ~/Dev/oracle/dist/oracle_metalenguaje-0.38.2-py3-none-any.whl ~/Dev/oracle/dist/oracle_metalenguaje-0.38.2.tar.gz
uv publish ~/Dev/factory/dist/oracle_factory-0.1.0a2-py3-none-any.whl ~/Dev/factory/dist/oracle_factory-0.1.0a2.tar.gz
uv publish ~/Dev/oracle-mcp/dist/oracle_mcp-0.1.2-py3-none-any.whl ~/Dev/oracle-mcp/dist/oracle_mcp-0.1.2.tar.gz
```

### Nota (2026-10-03 23:46:03 UTC)

CI Oracle del commit del corte: 37162191846 exitoso, contratos Python 3.11 y 3.13 verdes. Tags GitHub y artefactos remotos presentes; Oracle test verde. Resta publicación PyPI del mantenedor, verificación de consumidores nuevos, renovación del vendor Jam y retiro final de trackertast.

### Nota (2026-10-04 00:48:53 UTC)

Publicación PyPI confirmada: Oracle 0.38.2, Factory 0.1.0a2 y MCP 0.1.2; SHA256 de wheel y sdist coincide con releases. Instalaciones nuevas Python 3.13 sin trackertast; Factory completa su ejemplo hasta cierre fixture. Oracle/MCP globales ahora instalados desde PyPI. Jam reinstalado desde PyPI 0.38.2, 1448 tests verdes, pendiente commit/push. Retiro de trackertast bloqueado por falta de acceso autenticado: no hay credenciales ni navegador disponible.

- Adjunto: [resultados.json](resultados.json)

### Nota (2026-10-04 01:07:49 UTC)

Jam actualizado y empujado en 0d4c339; relevo OK y pre-push sin aflojamiento de catálogo. No se empujó etiqueta de identidad histórica. MCP cerrado y empujado en 8aa4cd0. La web se revisó con agy1/agy2 en Factory 20261003-235610-web-rigurosa; 23 tests y 11 comprobaciones Chromium, recorrido desde PyPI por comandos extraídos de guía hasta cierre fixture. Nuevo producto propuesto en cuatro tareas, sin implementación de CLI no solicitada.

### Nota (2026-10-04 01:17:06 UTC)

Factory web publicada: https://segtem.github.io/oracle-factory/; Pages 37167107976 success y seis archivos HTTP 200 idénticos a main. Auditorías agy1/agy2, 23 tests y 11 comprobaciones Chromium, guía PyPI completa en Linux. Implementación/documentación empujadas; pendientes de producto y piloto humano registrados en Factory. Trackertast 0.1.0 sigue con HTTP 200 en PyPI; no se pudo retirar sin acceso autenticado.

### Nota (2026-10-04 01:26:46 UTC)

El usuario informó que archivó trackertast y pidió continuar. Se verifica en API PyPI Simple1.4: project-status.status=archived, versión0.1.0 conservada. Este pedido final reemplaza el borrado anterior: archivado no eliminado, instalación histórica conservada. Migración de consumidores y publicación verificadas completas; no queda acción de borrado pendiente.

- Adjunto: [trackertast-archive-status.json](trackertast-archive-status.json)

## Próximo paso

Ninguno. Consumidores migrados, cortes PyPI verificados y trackertast archivado según la decisión final del usuario. Se conservan los artefactos históricos instalables; no se solicita borrado.
