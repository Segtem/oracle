# Cierre P4 — tracker verificado y corte preparado

2026-09-13. P0–P4 implementados y verificados con participación de agy y revisión de Codex.
La distribución instalada para las pruebas conserva **0.15.0**, con álgebra **0.6** y sintaxis **0.4**.

## Entrega y uso propio

Oracle incorpora una carpeta por tarea, Markdown editable, notas, URLs con marcas, adjuntos,
búsqueda, referencias, resumen y diagnóstico de seguimiento en Git. `oracle tarea ls` es alias
de `listar`. El sensor `hechos` alimenta tres políticas optativas escritas en el lenguaje existente.
El [contrato y tutorial](../../docs/12-tareas.md) y los cierres [P0–P1](CIERRE-P0-P1.md),
[P2](CIERRE-P2.md) y [P3](CIERRE-P3.md) describen el recorrido completo.

Se registraron tres pendientes reales del roadmap en `tareas/`: mutación, uso propio y preparación
del corte. Sus notas enlazan decisiones y evidencia existentes. El recorrido de uso propio creó,
anotó, adjuntó, buscó, consultó referencias y cerró una tarea con el CLI. No se migraron capturas
ni videos personales; el tutorial y los defectos de las políticas usan material construido.

## Correcciones y custodia

La revisión de agy y las reproducciones de Codex fijaron preservación de documentos y modos ante
fallos de escritura, reserva exclusiva de archivos, errores de rollback, límites de lectura y
copia, separadores Unicode, nombres no representables directamente en UTF-8 y errores de Git.
El extractor distingue escapes de Markdown, títulos, rutas codificadas y destinos que exigen
un directorio, y declara omisiones cuando no puede resolver la sintaxis que reconoce.

Los cuatro módulos custodian la integridad del registro y las afirmaciones consumidas por políticas.
Quedan declarados en `HERRAMIENTAS_CUSTODIAS`, con perfiles prioritarios y jobs en la matriz de CI.
Las rondas oficiales usan la suite completa, `--timeout 120`, copias frías y árboles sin ediciones
durante cada ronda. No se declararon equivalentes ni se contaron timeouts como detecciones.
Los tiempos medidos quedan por debajo del criterio aproximado de diez minutos por objetivo.
No se ejecutó GitHub Actions; estos resultados corresponden a la máquina local.

| Objetivo | Detectados / total | Tiempo |
|---|---:|---:|
| `tools/tareas.py` | 263/263 | 204,794 s |
| `tools/tareas_contexto.py` | 197/197 | 177,609 s |
| `tools/tareas_git.py` | 44/44 | 172,027 s |
| `tools/tareas_hechos.py` | 258/258 | 258,140 s |

Total: **762/762**, cero sobrevivientes, timeouts, errores de arnés o equivalentes.
Los [comandos de las tres primeras rondas](verificacion-p4/rondas-integradas.json) y
[la ronda final del extractor](verificacion-p4/final-hechos/resultado.json) conservan sus códigos
y duraciones. Sus manifiestos identifican fuentes y dependencias. El primer registro también
incluye un diagnóstico histórico del extractor de 255/258, reemplazado por su ronda final.
Después de medir los otros tres módulos sólo se añadió una prueba del extractor y se adelantó
su gramática dentro del módulo de tests; sus fuentes de runtime permanecieron idénticas.

## Verificación del corte

Los trece pasos de la [secuencia final](verificacion-p4/cierre/resultados.json) terminaron con
código 0. Las salidas y errores se conservan junto a ese registro; las
[huellas finales](verificacion-p4/cierre/huellas.json) identifican el código y el ejemplo verificados.

| Comprobación | Resultado |
|---|---|
| Suite completa | 1852 tests, OK; 49,493 s de tests |
| Corpus propio y de políticas | 203 y 20 casos, OK |
| Aceptación propia | 115 defectos en rojo, 81 verdes correctos, 0 huecos sin tapar |
| Mutación de medidas propias | 959/959 |
| Mutación de políticas optativas | 52/52: 44 por conducta, 8 rechazadas por el álgebra |
| Cifras y manual | Regenerados |
| Instalación del wheel | WHEEL OK, API y tracker fuera del checkout |
| Sondas del generador y procedencia; traza | Código 0 |
| Aceptación de Jam con este checkout, sólo lectura | 28 defectos, 3 verdes correctos, 0 huecos sin tapar |

El [tutorial literal](verificacion-p4/cierre/tutorial-literal.sh) se extrajo sin cambiar comandos
de `docs/12-tareas.md` y se ejecutó con `bash -e -o pipefail` desde otro wheel nuevo y un entorno
virtual independiente, con cwd fuera del checkout. Construcción, instalación y recorrido dieron
código 0; [comandos y resultados](verificacion-p4/cierre/tutorial-resultados.json),
[salida](verificacion-p4/cierre/tutorial-final.stdout) y
[huellas del wheel y tutorial](verificacion-p4/cierre/tutorial-entorno.json).
El verificador del wheel comprueba también las políticas sobre un Git temporal confirmado y
un enlace roto construido con su testigo. Los commits de esa prueba son del repositorio temporal.

Después de esta secuencia sólo se actualizaron documentos de cierre y las tareas propias.
Las tres tareas quedaron cerradas con notas de evidencia mediante el CLI. La auditoría y las
políticas de referencias presentes y lectura sin omisiones pasaron; los
[resultados de uso propio](verificacion-p4/cierre/uso-propio-resultados.json) registran los comandos.
La política de archivos confirmados salió 1 y mostró los archivos todavía sin incorporar a Git,
como corresponde al estado real de este árbol.


## Límites y propuesta de versión

El extractor soporta la gramática parcial documentada; no afirma soporte completo de CommonMark.
La ausencia de omisiones se refiere a ese alcance. No descarga URLs, no certifica autenticidad
y no garantiza una instantánea frente a escritores concurrentes. El reemplazo atómico protege
cada documento; no es una transacción entre la copia de un adjunto y su nota ni un bloqueo entre
procesos. Git conserva la historia cuando el dueño incorpora y confirma los archivos: crearlos
mediante Oracle no los confirma automáticamente.

Propuesta concreta: **distribución 0.16.0**, **álgebra 0.6**, **sintaxis 0.4**. La menor de distribución
introduce la superficie pública `oracle tarea`, su formato persistente y el sensor de seguimiento,
siguiendo el precedente de nuevas herramientas de ESPECIFICACION.md §0. Las políticas usan nodos,
operadores y gramática existentes, y son optativas; no se modifican las versiones del lenguaje.
Texto preparado para el corte:

> La distribución sube de 0.15.0 a 0.16.0 al incorporar `oracle tarea`: registros en carpetas con
> Markdown, captura y consulta de contexto, seguimiento frente a Git y hechos para políticas
> optativas. Álgebra 0.6 y sintaxis 0.4 se conservan: no cambia la lectura ni la evaluación de
> archivos `.oracle` o `.caso`, ni se incorporan operadores o formas canónicas.

La preparación de P4 está terminada; aplicar la versión, integrar los cambios y publicar son
pasos del corte que todavía no se ejecutaron. No hubo commit ni push de estos cambios.

## Corte autorizado — 2026-09-13

El dueño confirmó 0.16.0 y autorizó commit, push, tag y release; PyPI queda a su cargo.
Se aplica distribución 0.16.0 conservando álgebra 0.6 y sintaxis 0.4. La evidencia anterior
conserva el número con el que se ejecutó; la [verificación del corte](../2026-09-13-corte-0.16.0/README.md)
registra las comprobaciones posteriores al cambio de versión.
