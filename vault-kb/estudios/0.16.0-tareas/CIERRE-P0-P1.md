# Cierre de P0–P1 — tracker local de tareas

2026-09-12. Implementación de agy; revisión, pruebas independientes y cierre de Codex.
Base conservada: distribución 0.15.0, álgebra 0.6 y sintaxis 0.4.

## Resultado

P0 y P1 del [roadmap](../../planes/PLAN-0.16.0-TAREAS.md) están implementados y verificados en el
workspace. Una persona puede crear una tarea como carpeta con `TAREA.md`, editar su contexto,
guardar adjuntos al lado, listar por estado/etiqueta/texto, consultar por ID o prefijo inequívoco,
cerrar, reabrir y auditar registros. El cuerpo y los adjuntos se preservan al cambiar el estado.

La interfaz es `oracle tarea init|nueva|listar|ls|ver|cerrar|reabrir|revisar`. La
[guía](../../docs/12-tareas.md) explica el formato, los códigos de salida y cómo probarla desde
el checkout sin confundirla con un binario instalado anteriormente.

No se incorporaron dependencias, una base de datos ni un lenguaje de consultas. La herramienta
no carga el catálogo ni evalúa escalares al gestionar tareas. No hubo commits, push, cambios de
versión ni publicación. La entrega completa 0.16.0 requiere todavía P2–P4.

## Revisión e integración

- Agy implementó el módulo, el despacho CLI, 21 tests y la documentación. Codex añadió 19 tests
  independientes, un recorrido del wheel instalado y la cobertura de ayuda general en un test
  existente del CLI. Las 40 pruebas específicas están incluidas en la suite global.
- Se corrigieron errores reproducidos de argumentos, ayudas que escribían archivos, metadatos
  inyectados por saltos de línea, IDs inválidos, enlaces externos, codificación inválida,
  preservación de CRLF y permisos POSIX, y colisiones al crear carpetas concurrentemente.
- `.gitignore` ignoraba cualquier archivo llamado `TAREA.md`. Se ancló esa exclusión a la raíz
  (`/TAREA.md`) y se verificó con un repositorio temporal que los registros del tracker quedan
  disponibles para agregar a Git. Crear una tarea no equivale a versionarla.
- La prueba del paquete crea un proyecto con espacios y Unicode, catálogo inválido y escalares
  que fallarían si se ejecutaran; recorre el ciclo desde una subcarpeta y comprueba la
  preservación de notas y adjuntos. Se ejecuta fuera del checkout con el wheel recién instalado.
- A pedido del dueño, agy hizo una [revisión final de sólo lectura](REVISION-FINAL-AGY.md).
  Sus aclaraciones de opciones, auxiliares y banderas incompatibles se incorporaron a la guía.
  También se corrigieron conteos y descripciones de P2/P3 que su informe había consignado mal.

La [revisión inicial](REVISION-CODEX.md) y `revision-inicial.log` conservan los fallos encontrados;
no representan el estado final. Las sesiones de agy finalizaron y no queda trabajo en segundo plano.

## Verificación final

Comandos ejecutados con Python y `-B`. Los códigos y tiempos están en
[verificacion/resultados.json](verificacion/resultados.json), con stdout y stderr por paso.

| Comprobación | Resultado |
|---|---|
| `-m unittest discover -s tests -q` | 1576 tests, OK |
| `tools/corpus.py` | 203 casos, OK |
| `tools/aceptacion.py` | 115 defectos rechazados, 81 correctos aceptados; código 0 |
| `tools/mutar.py` | 959/959 mutantes de medida detectados |
| `tools/cifras.py --actualizar` | README actualizado; código 0 |
| `tools/cli.py manual --html` | Manual regenerado; código 0 |
| `tools/verificar_instalacion.py` | Wheel y recorrido del tracker instalado, OK |
| `tools/sondear_generador.py` | Código 0 |
| `tools/sondear_procedencia.py` | Código 0 |
| `tools/trazar.py` | Código 0 |
| Mutación completa de `tools/cli.py` | 527/527 detectadas; código 0 |

La primera ronda del CLI detectó 524 de 527 mutaciones. Las tres restantes afectaban la ayuda
general de `oracle tarea`: faltaba incluir ese sustantivo en la prueba que verifica ayuda sin
verbo, `--help` y retorno 0. Se amplió esa prueba, se repitió la verificación general y se corrió
una segunda ronda completa. No se editó el árbol durante ninguna ronda.

Comando de la segunda ronda:

```bash
python3 -B tools/mutar_codigo.py --objetivo tools/cli.py --timeout 120 \
  --manifiesto /tmp/oracle-0.16-cli-mutacion-final.json
```

La ronda final tiene cero supervivientes, cero timeouts, cero errores de arnés y cero equivalentes
declarados. Se conservan los manifiestos y logs de
[la primera ronda](verificacion/mutacion-cli-inicial.json) y
[la ronda final](verificacion/mutacion-cli-final.json).
[huellas.json](verificacion/huellas.json) registra el código y los tests de la verificación final;
las correcciones posteriores sólo afectan documentación y artefactos del estudio.

## Alcance pendiente

P2 agrega captura de notas/URLs/adjuntos, búsqueda, referencias, resumen y diagnóstico del
seguimiento en Git. P3 agrega hechos deterministas y medidas opcionales de integridad. P4 lleva
el tracker al uso propio, completa la custodia por mutación y prepara el corte de distribución.

Esta entrega verifica ejemplos construidos y archivos temporales; no migró material personal
del dueño ni pendientes históricos. La mutación de 527 sitios corresponde al CLI, no al módulo
nuevo `tools/tareas.py`: la mutación integral de ese módulo sigue pendiente. Las comprobaciones
de enlaces cubren rutas preexistentes y las pruebas de concurrencia cubren creación de tareas;
no afirman exclusión mutua con un editor externo ni protección frente a sustituciones hostiles
de rutas durante una operación. No se ejecutaron recorridos de consumidores Jam o LyraGASP.
