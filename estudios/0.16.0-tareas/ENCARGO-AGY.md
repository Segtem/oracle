# Encargo a agy — primera entrega del tracker de Oracle

Fecha: 2026-09-11. Autor: Codex, por pedido explícito del dueño de planear 0.16.0 y poner a agy
a implementar un tracker inspirado en tatr, adaptado al sistema de Oracle.

## Trabajo asignado

Leé `PLAN-0.16.0-TAREAS.md` e implementá P0 y P1 de punta a punta en este checkout:
`/home/workstation/Dev/oracle`. No te quedes en una propuesta. El entregable es código, contrato,
ejemplos, tests y verificación local. P2–P4 quedan para una asignación posterior.

La experiencia buscada es carpetas + Markdown + CLI pequeño: `oracle tarea init`, `nueva`,
`listar` (alias `ls`), `ver`, `cerrar`, `reabrir`, `revisar`. Seguí el contrato del roadmap.
Un usuario puede editar `TAREA.md` y copiar adjuntos por su cuenta; la herramienta debe volver a
leerlos, preservar el texto y detectar datos inválidos. No debe exigir un catálogo sano para usar
el tracker. No confundas archivos creados con archivos ya registrados en Git.

## Contexto y propiedad de archivos

Leé el registro `VERBOS`/`ALIAS` y el despacho de `tools/cli.py`, `tools/manual.py`,
`nucleo/proyecto.py`, `pyproject.toml`, los tests de CLI/manual/instalación y los relevos.
El estado vigente lo fija `nucleo/version.py` (0.15.0) y el estudio del corte 2026-09-11;
algunos encabezados de README y RELEVO son históricos y no deben tomarse por estado vigente.

Podés crear `tools/tareas.py`, un módulo de datos separado si hace falta, tests enfocados y
`docs/12-tareas.md`; integrar CLI, manual, empaquetado y verificaciones donde corresponda.
Codex no editará esos archivos mientras trabajes. Codex mantiene el roadmap y este encargo:
si necesitás ajustar una decisión, explicá el motivo y la premisa en el informe.

Todo el código, mensajes, comentarios, docstrings y documentos propios se escribe en español.
Usá Python 3.11+ y biblioteca estándar. Implementación propia del diseño; no copies código de tatr.
No agregues dependencias, no modifiques el álgebra ni la sintaxis y no cambies el servidor MCP.
No hagas commit, push, tag ni publicación; no subas versiones. No edites otros repositorios.
No toques LyraGASP. No lances otros agentes.

## Verificación y conducta ante problemas

- Primero escribí `estudios/0.16.0-tareas/AVANCE-AGY.md` con que recibiste el encargo, el primer paso
  y los archivos que vas a tocar. Actualizalo al terminar cada bloque; un proceso vivo no demuestra
  que esté avanzando.
- Tests de conducta, con docstring que nombre el fallo que evitan: preservación del cuerpo al
  cerrar/reabrir, metadatos duplicados o falsos dentro del cuerpo, IDs simultáneos, rutas fuera del
  tracker, ambigüedad, proyecto explícito/subcarpeta, lista vacía versus datos inválidos.
- Probá los comandos por el CLI público y el paquete instalado. No te conformes con tests que
  llamen sólo a funciones internas. `--help`, `--json` y errores tienen que ser consistentes.
- Corré la suite completa, corpus y aceptación; regenerá las cifras y el manual si cambia su
  fuente y verificá el wheel. Consultá los comandos reales en el relevo y en los scripts.
- Si una comprobación falla, diagnosticá y arreglá dentro del alcance. No debilites asserts,
  medidas, sombras, umbrales o mutadores. Conservá por separado los fallos y los reintentos.
- No edites durante una ronda de mutación. La revisión final de custodias y mutación del corte
  figura en P4; no afirmes que P1 completó verificaciones que no ejecutaste.
- Ante un bloqueo del entorno, registrá comando, error y qué falta; no inventes resultados.

Terminá con `estudios/0.16.0-tareas/INFORME-AGY.md`: conducta implementada, decisiones, archivos,
comandos y resultados medidos, limitaciones y siguiente tramo. Dejá una secuencia reproducible
para que Codex revise crear → editar → listar → ver → cerrar → reabrir, sin alterar datos reales.
