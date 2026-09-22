# Dos relaciones con el mismo nombre hacen caer oracle test con un traceback

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle, errores, relaciones


## Qué pasó

2026-09-22, en Jam: agy declaró `medidas/relaciones/pieza.json`, y Oracle ya distribuye una relación
`pieza` (idéntica campo por campo). `oracle test --proyecto medidas` terminó con un traceback de
Python: `nucleo.relacion.RelacionMalDeclarada: la relación «pieza» está dos veces: …/site-packages/
oracle_metalenguaje/relaciones/pieza.json y …/jam/medidas/relaciones/pieza.json`.

El mensaje es claro, pero sale como traceback en vez de como un error del proyecto con salida 2, y
no dice qué hacer. Un agente lo lee como un crash de Oracle.

## Qué hacer

1. `oracle test` (y `juzgar`, `revisar`, el MCP) atrapan `RelacionMalDeclarada` al cargar relaciones
   y la informan como `PROYECTO INVÁLIDO — …` con salida 2, sin traceback.
2. Cuando el choque es con una relación que distribuye Oracle, el mensaje dice que ya existe y que el
   proyecto la usa tal cual (o la renombra), en vez de sólo «está dos veces».
3. Un test por cada verbo.

### Nota (2026-09-22 22:02:55 UTC)

Tests primero: cuatro regresiones públicas fallaron antes del cambio (test, juzgar, medida revisar y MCP). Implementada validación temprana y traducción de RelacionMalDeclarada a ProyectoInvalido; duplicados de Oracle conservan ambas rutas y explican eliminar la copia o renombrar la relación propia y sus referencias. Las cuatro regresiones pasan. Suite completa en ejecución; sin commits.

### Nota (2026-09-22 22:05:57 UTC)

Regresión ampliada a 7 tests: cuatro fronteras públicas, duplicados locales, catálogo base desactivado y JSON malformado. MCP mantiene su transporte vivo (exit 0) y responde isError/PROYECTO_INVALIDO; los tres verbos CLI salen con 2. Ajustadas expectativas previas del error de proyecto y de su huella en MCP. Validación de revisar ubicada en cmd_revisar para no acoplar sus pruebas de presentación. Se conserva prioridad de errores de escalares. La primera suite reveló esas incompatibilidades, ya corregidas; 57 tests focalizados finales pasan. README regenerado con tools/cifras.py --actualizar (2401 tests y cifras del código actual). Corridas completas finales en ejecución.

### Nota (2026-09-22 22:06:46 UTC)

Suite completa final: python3 -m unittest discover -s tests -t . -q terminó con exit 0, 2401 tests en 84.045 s, OK. Evidencia guardada en verificacion/unitarios.log; 57 focalizados en verificacion/focalizados.log y las cuatro regresiones antes de implementar en verificacion/regresiones-antes.log. No se requiere juicio a ciegas en esta tarea.

### Nota (2026-09-22 22:07:27 UTC)

Verificación final adicional: python3 tools/cli.py test terminó con exit 0 y VEREDICTO: VERDE; unitarios 2401 OK, corpus/aceptación/diferencial/trazabilidad/metamórficas/cifras en regla y 1010/1010 mutantes de medida muertos. Log: verificacion/oracle-test.log. Este nivel estándar omite mutación de código (--todo), como declara su salida. git diff --check limpio. Implementación terminada; no se hicieron commits ni escrituras en .git. Queda abierta para revisión y cierre posterior en un entorno con Git escribible.

## Próximo paso

Revisar el diff y la evidencia en `verificacion/`. La implementación y las verificaciones están
terminadas: 2401 unitarios OK y `python3 tools/cli.py test` VERDE. No hay juicio a ciegas pendiente.
Cuando se habilite escritura en Git y se autoricen commits, registrar el cambio y cerrar la tarea
siguiendo el protocolo. En esta sesión no hacer commits: `.git` es de sólo lectura.
