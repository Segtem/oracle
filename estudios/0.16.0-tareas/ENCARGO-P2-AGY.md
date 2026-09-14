# Encargo P2 a agy — captura y consultas

2026-09-12. El dueño autorizó continuar y usar agy. Implementar este tramo ahora, conservando
la entrega P0–P1 existente y los cambios sin commit. Leer roadmap, guía, cierre P0–P1 y código.

## Propiedad y coordinación

Agy puede editar `tools/tareas_contexto.py` (nuevo), `tools/tareas.py`, `tools/cli.py`,
`tests/test_tareas_contexto.py` (nuevo), `docs/12-tareas.md` y sus propios registros P2.
Codex implementa `tools/tareas_git.py`, `tests/test_tareas_git.py`,
`tests/test_tareas_p2_revision.py` y amplía `tools/verificar_instalacion.py`. No tocar esos archivos.
No modificar tests anteriores para acomodarlos a cambios de conducta.

Usar sólo herramientas de lectura/escritura/edición. NO ejecutar comandos de shell ni tests:
en esta sesión headless no pueden solicitar permisos y Codex ejecutará todos los comandos.
No lanzar agentes, no editar otros repositorios, no usar red, no cambiar versiones ni dependencias,
no hacer commit/push. Español, Python 3.11+, biblioteca estándar. No iniciar mutación.

Primero escribir `AVANCE-P2-AGY.md` en este directorio, confirmando recepción y archivos.
Al terminar escribir `INFORME-P2-AGY.md` con implementación y límites, indicando honestamente
que los tests quedan para ejecución por Codex. No inventar cifras ni resultados.

## Contrato de comandos

Integrar verbos en VERBOS, ayuda y despacho sin cargar catálogo. Todos aceptan --proyecto,
--json y --help sin escrituras; rechazan argumentos desconocidos y preservan códigos P1.
En `tareas.despachar`, integrar `seguimiento` llamando mediante import local a
`tools.tareas_git.cmd_seguimiento(argv, args)`; Codex provee esa función.

Crear módulo de contexto con comandos:

- `anotar ID [TEXTO] [--url URL] [--marca TEXTO]`: exige texto o URL. URL opcional sólo http/https
  absoluta, sin controles ni espacios; conservarla exactamente (incluido ?t= de YouTube).
  --marca es una posición del recurso aportada por la persona, como 01:32, y exige --url.
  Añadir al cuerpo una entrada con fecha UTC de captura, texto, URL y marca sin descargar nada.
  Preservar todos los bytes anteriores y permisos del documento; reemplazo atómico.
- `adjuntar ID ARCHIVO [--permitir-grande]`: copiar archivo regular explícito, conservar original
  y nombre Unicode/espacios. Rechazar enlaces de origen, directorios, archivos especiales,
  destino existente (incluidos enlaces rotos), nombre TAREA.md o escape del tracker. Máximo
  predeterminado 20 MiB; archivos mayores requieren --permitir-grande, sin imponer LFS.
  Copiar por bloques, creación exclusiva. Registrar enlace Markdown relativo con destino URL
  escapado para espacios/paréntesis/#; escapar también etiqueta visible. Si falla la copia o
  registro, retirar sólo el destino creado por esta operación, sin modificar documento/original.
  JSON de éxito: objeto con id, ruta (adjunto absoluto), documento (TAREA.md absoluto).
- `buscar TEXTO`: búsqueda literal sin distinguir mayúsculas en documentos y adjuntos de texto
  del tracker. JSON {coincidencias: [{ruta, linea, texto}], omitidos: [{ruta, motivo}]} con rutas
  relativas a raíz del proyecto, líneas desde1, orden estable. No ejecutar archivos ni seguir
  enlaces. Documentar extensiones de texto admitidas y límite2MiB por archivo, informar omisiones
  de binarios/tamaño/enlaces. Cero coincidencias éxito. Datos de tarea rotos/error de lectura
  producen código1, no se disfrazan de resultado vacío.
- `referencias ID`: buscar menciones del ID COMPLETO resuelto en texto de tareas, notas y código
  bajo la raíz del proyecto. Misma estructura JSON que buscar, más id y tipo="mencion_textual".
  Coincidir ID con límites para no atribuir ID-copia a ID. Las menciones no son dependencias
  declaradas. No introducir sintaxis de dependencias en este tramo.
  Excluir .git, .hg, .svn, .venv, venv, node_modules, __pycache__, build y dist, sin atravesar
  enlaces ni repositorios anidados. Documentar alcance, extensiones y omisiones. Un error de
  lectura no puede silenciarse. No leer todo video ni binario en memoria.
- `resumen`: auditar registros y derivar JSON {total, estados: {ABIERTA, CERRADA}, etiquetas: {...}}.
  Contar cada tarea una sola vez por etiqueta, ordenar estable, no escribir cache. Registros
  inválidos hacen fallar la consulta. Vacío devuelve total0.

Reutilizar validación P1 de raíz, IDs y documentos; no duplicar parser de TAREA.md.
Comprobar confinamiento también de archivos. Evitar que auxiliares temporales propios queden
como tareas o adjuntos corruptos. No prometer protección ante un editor concurrente o sustitución
hostil de rutas: sí preservar y no sobrescribir datos preexistentes en las operaciones normales.

## Pruebas y documentación

Escribir tests de comportamiento vía CLI público con temporales; Codex los ejecuta. Cubrir
preservación de notas/URL/marca, copia exacta/original intacto/colisiones, límites, rutas con
espacios Unicode, búsqueda de nota adjunta, referencias en código sin confundir sufijos, resumen,
errores y ayuda sin escribir. Evitar tests que sólo reproduzcan detalles internos.

Actualizar guía con tutorial: nueva → anotar URL/marca → adjuntar captura → buscar → referencias
→ resumen → seguimiento. Aclarar que URL conserva referencia, no contenido remoto. La descripción
detallada de seguimiento la agrega Codex. Manual y cifras los regenera Codex al cerrar.
