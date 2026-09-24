# Cierre 0.22.0 — toda medida lee campos que existen, y lo que no se pudo juzgar se informa igual

2026-09-15. Tarea [`20260915-155654-campos`](../../tareas/20260915-155654-campos/TAREA.md).
Plan [vault-kb/planes/PLAN-0.22.0-CAMPOS.md](../../planes/PLAN-0.22.0-CAMPOS.md), aprobado por el dueño. Implementó agy;
revisó, corrigió y verificó Claude. La publicación en PyPI queda a cargo del dueño.

## Qué se entregó

1. **Los campos de lo que emite Oracle.** `CAMPOS_DE_RELACIONES` junto a cada emisor de las 26 relaciones
   del lenguaje, leído sin importar los módulos por `campos_de_relaciones_declarados()`, que falla cerrado
   ante un literal que no entiende; un test compara cada declaración con las filas emitidas.
2. **Relaciones de proceso declaradas.** `corrida_mutacion`, `archivo`, `modulo`, `alcanzable`,
   `importa`, `cambio`, `afirmacion` y `hallazgo`, en `relaciones/`.
3. **`campo_leido`** (`nucleo/campo_leido.py`): una fila por cada campo que lee una medida, con su
   relación, su origen y si existe.
4. **`meta.toda_medida_lee_campos_que_existen`**, universal, con los casos 504, 505 y el observado 506.
5. **`evaluar_conjunto` e `Informe.no_juzgaron`**, usados por la aceptación, `oracle juzgar`, `mutar` y
   `mutar_codigo`: la aceptación ya no termina en traceback ante un campo ausente.

## Recorrido

1. La tarea salió de 0.21.0: una medida se declaraba aplicable por el nombre de la relación aunque
   leyera campos que la evidencia no traía.
2. Medido antes del plan: nadie leía un campo inexistente de una relación declarada; el defecto real
   estaba en relaciones de proceso sin declarar y en las del lenguaje, cuyos campos sólo conocía el
   emisor. El dueño eligió que la regla cubra declaradas y emitidas por Oracle, y una sola forma de
   informar lo que no se pudo juzgar.
3. [Encargo](ENCARGO-AGY.md) a agy. El primer lanzamiento cortó por falta de capacidad del servidor sin
   tocar nada; una cadena con reintentos entregó en el primer intento ([avance](AVANCE-AGY.md),
   [informe](INFORME-AGY.md)).
4. [Revisión](REVISION-CLAUDE.md): los tests de revisión, escritos antes de leer la entrega, pasaron. Se
   corrigieron tests de la entrega escritos contra una API que no existe, un envoltorio que abría un
   falso verde en el corpus, lectores duplicados, el módulo nuevo fuera del arnés, dos relaciones de
   proceso que el plan dejaba sin declarar (lo mostró el volcado real de `campo_leido`) y la falta de un
   caso observado.

## Verificación final

- Mutación de código, una ronda por objetivo en copias aisladas ([logs](verificacion/)):

  | objetivo | murieron |
  |---|--:|
  | `nucleo/medida.py` | 311/312 |
  | `nucleo/relacion.py` | 169/169 |
  | `tools/juzgar.py` | 113/113 |
  | `nucleo/marco.py` | 78/79 |
  | `tools/aceptacion.py` | 76/78 |
  | `nucleo/campo_leido.py` | 24/24 |

  Lo que la mutación encontró está en la [revisión](REVISION-CLAUDE.md) (R9–R11): los vivos de
  `aceptacion.py` eran código que se borró; los de `marco.py` y `medida.py` tienen test, verificado
  aplicando el mutante a mano; `relacion.py` y `campo_leido.py` se repitieron después de corregir. Ningún
  equivalente nuevo.

- Suite completa en verde (2146 tests); aceptación ✓ (118 defectos en rojo, 83 verdes correctos); CI de `c743b7c` verde.
- `campo_leido` sobre el catálogo de Oracle: 160 lecturas, 131 del lenguaje y 29 de declaradas, todas
  existentes.
- `tools/mutar.py` y `tools/mutar_codigo.py` cambiaron pero no son objetivos del arnés de mutación
  («fuera del perfil activo»); sus cambios los fijan tests.

## Tareas abiertas que deja

- `20260915-201030-diferencial`, `20260915-201030-vigente`: diferencial y especificación.
- `20260915-155111-ambito`, `20260915-155111-exigentes`: deudas del catálogo universal.
- `20260915-155111-consumidores`: LyraGASP y Jam siguen en 0.17.0.
- `20260915-213158-sitio`: el sitio quedó en 0.8 y no muestra el tracker.
- Las demás abiertas del tracker (`oracle tarea ls`).
