# Revisión P3 — hallazgos resueltos

Estado final: corregidos y verificados. Ver [CIERRE-P3.md](CIERRE-P3.md). Se conserva a
continuación el encargo de corrección original, que no representa pendientes actuales.

2026-09-12. Corrida inicial conjunta: 30 tests,1 fallo de tu fixture. Corrida independiente
ampliada: 19 tests,6 fallos reproducidos. Codex conserva los logs; no editar sus tests.

1. Tu fixture escribe `- Definición no resuelta: [clave1]: destino.txt`, que no es una definición
   Markdown. Cambiar el fixture a una definición real `[clave1]: destino.txt` al inicio de línea;
   no ampliar el parser a prosa sólo para satisfacer el test. Contemplar definición sin espacios
   tras colon (`[clave]:destino`) y omitirla claramente cuando no se resuelva.
2. Deduplicás por (ruta,línea,destino), perdiendo dos apariciones iguales en la misma línea.
   Conservar una fila POR APARICIÓN. Evitar duplicar el autolink dentro de un enlace inline mediante
   posiciones/spans, no colapsando destinos independientes.
3. `[nota](\nausente.txt)` desaparece con completa=true. Resolverlo o declarar omisión de sintaxis
   multilínea. Lo mismo cuando se reconoce un inicio de enlace pero no se puede terminar su parseo.
4. `HTTPS://...` aceptado por anotar pasa a no_admitida. Clasificar esquema sin distinguir caja y
   preservar texto original. Autolinks idem.
5. Una línea ```no-es-cierre dentro de código se toma por cierre. Un cierre sólo tiene espacios
   después de la cerca (y mismo tipo/tamaño mínimo). No convertir contenido de código en referencias.
6. CRÍTICO: `puente/../parece-local.txt` con puente simbólico se normaliza antes de comprobar los
   componentes, elimina el symlink y da presente. Inspeccionar componentes originales, incluidos
   los que .. cancelaría, sin seguir enlaces ni acceder fuera del proyecto. Un componente archivo
   seguido por /.. tampoco es un directorio válido. No usar resolve() para atravesar links.
7. CRÍTICO: permisos denegados se convierten en ausente por is_symlink/lexists que silencian E/S.
   Usar lstat explícito: sólo FileNotFoundError/NotADirectoryError prueban ausencia; PermissionError
   y otros OSError deben fallar con código1, sin JSON parcial ni traceback.
8. Respetar límite antes de auditar/hashear TAREA.md: auditar_tareas lee documentos enteros antes
   del límite actual. Hacer prechequeo acotado de centrales y rechazar con código1 un TAREA.md
   central mayor a2MiB o simbólico (aunque el link apunte dentro). Adjuntos Markdown grandes
   siguen como omisiones. Documentar esta distinción; no hacer lecturas ilimitadas silenciosas.

Corrección de integración de Codex: `medida probar --con` recibe texto en superficie, NO ruta JSON.
El encargo ya se corrigió. El consumidor real es `ejemplo/seguimiento-tareas/evaluar.py --con ARCHIVO`,
escrito por Codex y basado en Medida.evaluar. Corregir documentación/informe, sin modificar ese script.

Revisar literales escapados `\[texto](destino)` para no confundirlos con enlaces. No prometer
CommonMark completo ni seguridad/cobertura exhaustiva; declarar los límites reales de la gramática.
No agregar dependencias ni cambios de álgebra. Sólo tus archivos; sin shell, tests ni otros agentes.
Actualizar avance e informe tras corregir. Codex ejecuta pruebas y verifica wheel/políticas.
