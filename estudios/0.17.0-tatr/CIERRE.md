# Cierre 0.17.0 — lo que faltaba de tatr

2026-09-14. Implementó agy; revisó, corrigió y verificó Claude. El dueño autorizó el corte 0.17.0
y la publicación en PyPI queda a su cargo.

## Qué se entregó

`oracle tarea etiquetar`, `desetiquetar` (con modo masivo por estado), `grafo` (DOT o JSON, sin
escribir archivos ni invocar Graphviz), el archivo auxiliar `tareas/etiquetas` con descripciones
y conteo de tareas sin etiquetas en `resumen`, columnas calculadas en `listar`, la sección del
tracker en el README (y por lo tanto en PyPI) y «Diferencias con tatr» en `docs/12-tareas.md`.
TQL sigue fuera de alcance, como decidió el plan de 0.16.0.

## Recorrido

1. [Encargo](ENCARGO-AGY.md) → [avance](AVANCE-AGY.md) → entrega de agy.
2. Claude escribió `tests/test_tareas_tatr_revision.py` contra el encargo antes de leer el código.
   La primera entrega pasaba 21 de 22; el que fallaba mostró que una redefinición en
   `tareas/etiquetas` rompía `resumen`.
3. [Revisión](REVISION-CLAUDE.md), con reproducciones: `etiquetar` sobre un `TAREA.md` sin salto
   de línea final dejaba `- PRIORIDAD: 50- ETIQUETAS: bug` y salía 0; los problemas del archivo de
   etiquetas rompían `listar`, `grafo`, `hechos` y `buscar`; comentarios `#` no pedidos; ~150 líneas
   duplicadas entre `etiquetar` y `desetiquetar`; búsqueda n² en `grafo`; afirmaciones falsas en la
   documentación (`listar --estado`, bytes nulos, cabeceras de `listar`, tatr con YAML).
4. Ronda de correcciones de agy ([informe, sección 6](INFORME-AGY.md)). Todo reproducido de nuevo
   y en verde. Claude corrigió dos afirmaciones más sobre tatr en «Diferencias con tatr».
5. Mutación. La primera ronda dejó sobrevivientes en `tareas_grafo.py` (4) y `tareas.py`. Se
   resolvieron así, sin declarar equivalentes:
   - **Borrando** lo que no tenía comportamiento observable: `frozen`, `linea` y `etiqueta` de
     `ProblemaEtiquetas`; el parámetro `advertir_redefinicion`, que nadie usaba; la rama de
     `listar` que imprimía distinto sin etiquetas (ahora los anchos salen de `zip`); condiciones
     redundantes y el `return` inalcanzable de `_aplicar_etiquetas_texto`; la normalización del
     espacio tras `ETIQUETAS:` en `quitar`, que `agregar` no hacía; el segundo chequeo de saltos
     de línea en las etiquetas; el chequeo de `TAREA.md` ausente que la auditoría ya garantiza.
   - **Con tests** donde el comportamiento es real: códigos exactos de `grafo` sin tracker y con
     lectura fallida, borde de 2 MiB, error de lectura del archivo de etiquetas, formato exacto de
     `listar`, fin de línea del documento al insertar, `ETIQUETAS` como primer metadato, línea
     informada al insertar, título sin metadatos ni EOL, línea en blanco antes del título,
     saltos de línea en etiquetas y rechazo al releer una tarea.
   - `tests.test_tareas_tatr*` pasaron al frente de las prioridades de `tareas.py` y
     `tareas_contexto.py`: el orden no cambia el resultado, sólo mata antes a los mutantes nuevos.

## Verificación final

| Módulo | Muertos | Vivos | Timeouts | Errores de arnés |
|---|--:|--:|--:|--:|
| `tools/tareas.py` | 368 | 0 | 0 | 0 |
| `tools/tareas_hechos.py` | 258 | 0 | 0 | 0 |
| `tools/tareas_contexto.py` | 202 | 0 | 0 | 0 |
| `tools/tareas_git.py` | 44 | 0 | 0 | 0 |
| `tools/tareas_grafo.py` | 14 | 0 | 0 | 0 |
| **Total** | **886** | **0** | **0** | **0** |

Sin equivalentes declarados.

Cómo corrieron las rondas oficiales, con `estudios/0.17.0-tatr/medir_tracker.py` (suite completa,
tests del tramo al frente de las prioridades): `tareas_grafo` sobre el checkout; `tareas`,
`tareas_contexto`, `tareas_git` y `tareas_hechos` en paralelo, cada una sobre una copia idéntica
del árbol (sin `.git`) y con su propio `TMPDIR`. La mutación admite una sola ronda por raíz, y un
primer intento en paralelo con `/tmp` compartido se descartó entero: `test_observar` revisa
`oracle-observar-*` en el temporal global, así que dos suites simultáneas se contaminaban y un
mutante podía figurar muerto por la suite vecina. Cada `manifiesto.json` registra su raíz y la huella
de sus dependencias. Evidencia en [verificacion/](verificacion/).

- Suite completa: 1920 tests en verde.
- `tools/verificar_instalacion.py`: `WHEEL OK`, con un recorrido nuevo sobre el wheel instalado
  fuera del checkout: `etiquetar` + `desetiquetar` vuelven el documento byte a byte,
  `tareas/etiquetas` aparece en `resumen` y `revisar` lo acepta, y `grafo` encuentra la mención.
- `tools/cifras.py` sin deriva; `docs/manual.html` regenerado; `twine check` de wheel y sdist.
- Uso propio: `oracle tarea desetiquetar` quitó `en-curso` de la tarea cerrada
  `20260912-223232-mutacion-tracker`; `revisar` OK.

## Límites que quedan

- Una mención textual no es una dependencia declarada; `grafo` sólo mira `TAREA.md`.
- Oracle separa etiquetas sólo por comas: `hola mundo` es una etiqueta y no se puede describir
  en `tareas/etiquetas`.
- `etiquetar`/`desetiquetar` no son transaccionales entre documentos; un fallo de E/S a mitad
  informa cuáles quedaron escritos.
