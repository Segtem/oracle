# Cierre P3 — hechos del tracker y políticas optativas

2026-09-12. Implementación conjunta de agy y Codex; revisión y verificación final de Codex.
Distribución conservada en 0.15.0; álgebra 0.6 y sintaxis 0.4.

## Entrega

`oracle tarea hechos [--git] [--proyecto RUTA]` emite JSON determinista a stdout, sin escribir
archivos ni cargar catálogos. Expone cinco relaciones: lectura, tareas, archivos, referencias
y omisiones. Separa metadatos declarados, existencia observada y referencias no comprobadas;
la consulta Git es optativa y distingue índice, HEAD y cambios pendientes.

El [contrato y tutorial](../../docs/12-tareas.md) documentan campos y límites. El
[proyecto de ejemplo](../../ejemplo/seguimiento-tareas/README.md) aporta tres políticas optativas:
referencias locales presentes, archivos confirmados sin cambios y lectura sin omisiones.
Incluye relaciones, alcances, defensas y 20 casos construidos de ambas polaridades.
No cambia las condiciones universales para cerrar tareas ni el álgebra o el servidor MCP.

El consumidor `ejemplo/seguimiento-tareas/evaluar.py --con ARCHIVO.json` usa la API pública
`Medida.evaluar` y muestra veredictos y testigos. La ruta JSON no se pasa a `medida probar --con`,
que recibe texto de evidencia en superficie. Esa confusión inicial del encargo se corrigió.

## Coordinación y revisión

Agy implementó el extractor, su integración y 24 tests. Codex escribió las políticas, otros
24 tests de revisión e integración y el recorrido del wheel instalado. Agy recibió reproducciones
independientes y corrigió su entrega; ambas sesiones terminaron con código 0.

Se corrigieron pérdida de apariciones repetidas, enlaces multilínea omitidos sin aviso,
esquemas HTTPS en mayúsculas, cierres incorrectos de bloques de código, normalización de rutas
antes de detectar enlaces simbólicos, errores de permisos confundidos con ausencia y lecturas
centrales sin límite previo. Un fixture de definición Markdown también estaba mal construido.
Codex completó las variantes de rutas absolutas con `..`, directorios de tarea simbólicos y
el inventario de directorios adjuntos simbólicos. La suite general encontró además que faltaba
`hechos` en la ayuda general: se corrigió, regeneró el manual y repitió toda la secuencia.

Se conservan los hallazgos en [la revisión](REVISION-P3-CODEX.md), los logs iniciales en
`verificacion-p3/revision-inicial.log` y `revision-ampliada.log`, y el fallo de ayuda en
`verificacion-p3/unitarios-ayuda-incompleta.stderr`. Son fallos históricos corregidos.

## Verificación final

Los doce comandos terminaron con código 0. [Resultados y tiempos](verificacion-p3/resultados.json)
y stdout/stderr por comando están en `verificacion-p3/`.

| Comprobación | Resultado |
|---|---|
| Suite general | 1679 tests, OK; incluye 48 añadidos en P3 |
| Corpus propio | 203 casos, OK |
| Corpus del ejemplo | 20 casos construidos, OK |
| Mutación de políticas del ejemplo | 52/52 detectadas: 44 por conducta y 8 rechazadas por el álgebra |
| Mutación de medidas propias | 959/959 detectadas |
| Aceptación | Código 0 |
| Cifras y manual | Regenerados, código 0 |
| Wheel instalado | Ciclo P1–P3 fuera del checkout, código 0 |
| Generador, procedencia y traza | Código 0 |

El recorrido instalado comprueba dos extracciones idénticas, evalúa las tres políticas sobre un
repositorio temporal confirmado y luego introduce un enlace roto construido: la política de
referencias falla y muestra el destino como testigo. Los commits de prueba pertenecen a ese
repositorio temporal. Las [huellas](verificacion-p3/huellas.json) identifican el código Python
y todos los archivos del ejemplo verificados. Después sólo se editaron documentos de cierre.

## Límites y siguiente tramo

El lector soporta una parte documentada de Markdown, no CommonMark completo. Registra omisiones
de sintaxis reconocida pero no resuelta. `completa` significa ausencia de esas omisiones dentro
del alcance soportado; no certifica contenido remoto ni autenticidad. No visita URLs ni lee el
contenido binario de adjuntos. Un `TAREA.md` central mayor a 2 MiB o simbólico causa error; un
adjunto Markdown grande se incluye en el inventario y se omite de la lectura. No se promete
una instantánea atómica frente a ediciones concurrentes.

La verificación utiliza ejemplos construidos. La mutación completa del código Python nuevo
del tracker sigue pendiente para P4: los 52 mutantes de aquí son de políticas, y la ronda
527/527 de P0–P1 sólo corresponde al CLI de aquel cierre. P4 incluye uso propio, material real
cuando esté disponible y preparación del corte 0.16.0. No hubo cambio de versión, publicación,
commit ni push de los cambios de Oracle.
