# Cierre P2 — captura, consultas y seguimiento en Git

2026-09-12. Implementación conjunta de agy y Codex; revisión y verificación final de Codex.
Distribución conservada en 0.15.0; álgebra 0.6 y sintaxis 0.4.

## Entrega

P2 del [roadmap](../../planes/PLAN-0.16.0-TAREAS.md) está implementado y verificado en el workspace:

| Comando | Conducta |
|---|---|
| `oracle tarea anotar ID [TEXTO] --url URL --marca 01:32` | Añade texto, referencia y marca aportada, con fecha UTC de captura; no descarga contenido. Texto o URL son suficientes. |
| `oracle tarea adjuntar ID ARCHIVO` | Copia sin sobrescribir, conserva origen/nombre y registra enlace relativo; más de 20 MiB exige `--permitir-grande`. |
| `oracle tarea buscar TEXTO` | Busca literalmente en documentos y adjuntos de texto, incluidas subcarpetas; informa omisiones y fallos. |
| `oracle tarea referencias ID` | Localiza menciones del ID exacto en tareas, notas y código del proyecto; no las interpreta como dependencias. |
| `oracle tarea resumen` | Deriva cantidades por estado y etiqueta, sin caché ni base de datos. |
| `oracle tarea seguimiento` | Distingue existencia local, pertenencia al índice y presencia en HEAD, además de ignorados y cambios pendientes. |

Todos los comandos admiten `--proyecto`, `--json` y ayuda sin escrituras. Se integraron en el
CLI y el manual. La [guía](../../docs/12-tareas.md) documenta formatos, límites, errores y un
tutorial. El binario de una instalación anterior requiere reinstalación; desde el checkout se
puede usar `python3 -B tools/cli.py tarea ...`.

## Coordinación y correcciones

Agy recibió el [encargo P2](ENCARGO-P2-AGY.md), implementó captura/consultas y escribió 28 tests.
Codex implementó el diagnóstico de Git con 11 tests, añadió 16 pruebas independientes de P2
y amplió la comprobación del wheel instalado. Las sesiones de agy terminaron con código 0;
no quedó un agente trabajando en segundo plano.

La revisión reprodujo bloqueo de búsqueda ante un FIFO, pérdida de sangría en notas, aceptación
de tareas corruptas en referencias, omisión de errores de lectura y una exclusión incorrecta
de repositorios anidados. Se corrigieron esos casos y se comprobó además lectura acotada,
recursión en notas, preservación de permisos, reversión ante documento inválido, enlaces rotos,
nombres Unicode y límites de tamaño. Los tests de permisos usan fallos reales del filesystem.

Codex corrigió también URLs sin host o con puerto inválido y la traducción de errores al enumerar
el tracker. Dos tests de agy tenían problemas propios: posicionales ausentes al probar opciones
desconocidas y una expectativa incorrecta de escape Markdown; se corrigieron conservando la
conducta exigida. Una simulación de fallo de lectura se sustituyó por permisos reales al cambiar
el mecanismo de apertura del código.

El diagnóstico Git se probó con un repositorio padre y un proyecto en una subcarpeta con espacios
y Unicode. Cubre archivos ignorados, borrados locales, retirados del índice, nombres con saltos,
variables Git heredadas y lectura que no altera bytes ni fecha del índice. Que una ruta figure
en HEAD no afirma que sus cambios actuales estén confirmados; el informe separa ambas cosas.

## Verificación final

La evidencia está en [verificacion-p2/resultados.json](verificacion-p2/resultados.json), con
stdout/stderr de cada comando. Se conserva la primera revisión fallida en
[revision-inicial.log](verificacion-p2/revision-inicial.log) y el fallo intermedio por manual
desactualizado en `unitarios-manual-desactualizado.stderr`. El manual se regeneró y se repitió
la secuencia completa sobre el código final.

| Comprobación | Resultado final |
|---|---|
| Suite `unittest discover -s tests -q` | 1631 tests, OK; incluye 95 del tracker (40 previos y 55 de P2) |
| Corpus | 203 casos, OK |
| Aceptación | 115 defectos rechazados y 81 casos correctos aceptados; código 0 |
| Mutación de medidas | 959/959 detectadas |
| Cifras y manual | Regenerados, código 0 |
| Wheel instalado | Ciclo P1 y P2 fuera del checkout, con catálogo inválido y sin ejecutar escalares; código 0 |
| Generador, procedencia y traza | Código 0 en los tres comandos |

El recorrido instalado crea nota/URL/marca, adjunta una imagen, busca la nota, encuentra una
mención en código, resume y comprueba Git antes de agregar, después de agregar al índice y
después de un commit construido en un repositorio temporal. Esos commits de prueba no afectan
el repositorio de Oracle. Las [huellas](verificacion-p2/huellas.json) identifican los archivos
Python verificados; las ediciones posteriores al recorrido sólo afectan documentación del cierre.

## Límites y siguiente entrega

La URL guarda la referencia, no el contenido remoto. Buscar tiene un límite de 2 MiB por archivo
y extensiones documentadas; informa los archivos omitidos. Referencias son menciones textuales.
Copiar un adjunto y registrar su enlace son dos operaciones: una interrupción puede dejar una
copia sin registrar. No se afirma exclusión mutua con editores ni otros procesos.

La verificación usa ejemplos construidos; no se migró material personal ni se visitaron URLs.
La mutación completa del código nuevo de tareas/contexto/Git sigue pendiente para P4. Los 527
mutantes del cierre P0–P1 pertenecen a aquella revisión del CLI, no se presentan como una ronda
nueva sobre P2. No se ejecutaron consumidores Jam o LyraGASP en este tramo.

Sigue P3: emitir hechos deterministas y medidas opcionales de integridad usando el lenguaje
actual. P4 incluye uso propio y preparación del corte. No se cambió la versión ni se publicaron
paquetes, ni se hicieron commits o push de los cambios de Oracle.
