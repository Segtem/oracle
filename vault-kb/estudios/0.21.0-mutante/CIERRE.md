# Cierre 0.21.0 — `mutante` con variantes y `requiere` con condición

2026-09-15. Tarea [`20260915-155111-mutante`](../../tareas/20260915-155111-mutante/TAREA.md).
Plan [vault-kb/planes/PLAN-0.21.0-MUTANTE.md](../../planes/PLAN-0.21.0-MUTANTE.md), aprobado por el dueño. Implementó agy;
revisó, corrigió y verificó Claude; la referencia del diferencial la re-derivó agy aislado. La
publicación en PyPI queda a cargo del dueño.

## Qué se entregó

1. **Relaciones con variantes** (`nucleo/relacion.py`): un nodo opcional `variantes` declara qué campos
   trae cada clase de fila según un campo discriminante común de tipo texto. Hechos `variante` y
   `variantes`; unidades y puntos ciegos encuentran los campos de variante.
2. **`requiere` con condición** (`nucleo/medida.py`, `nucleo/sintaxis.py`):
   `["filas", <relación>, <alias>, <condición>]`, en la superficie `requiere mutante m donde …` en su
   propia línea. SIN EVIDENCIA si no hay filas que cumplan; todas las condiciones en todas las filas se
   evalúan antes de decidir. Ninguna medida existente cambia.
3. **`mutante`** declarada en `relaciones/mutante.json` con las variantes `medida` y `codigo`; los dos
   productores emiten `tipo`; las dos medidas de `proceso` filtran por `tipo` y piden filas de su tipo.
4. **Versiones**: álgebra 0.6 → 0.7, sintaxis 0.4 → 0.5, distribución 0.20.0 → 0.21.0.

## Recorrido

1. La tarea salió de mirar los logs de mutación de 0.19.0 y 0.20.0: «NO pudieron juzgar» en cada ronda.
2. El dueño eligió una relación común; medido por ejecución, eso abría un falso verde en `requiere` y
   pedía declarar campos por tipo. Consultado de nuevo, eligió extender el lenguaje. Medido otra vez:
   las 20 medidas con `requiere` filtran violaciones con `donde`, así que un `requiere` «sobre las filas
   filtradas» las pasaba a SIN EVIDENCIA; el plan lo diseñó como `requiere` con condición propia.
3. [Encargo](ENCARGO-AGY.md) a agy, [avance](AVANCE-AGY.md) e [informe](INFORME-AGY.md). Claude escribió
   `tests/test_mutante_revision.py` y el corpus antes de leer la entrega; los tests pasaron sobre ella.
4. [Revisión](REVISION-CLAUDE.md): la condición recorría el nodo `clave`, un resultado no booleano
   pasaba, los nombres simples ganaban una validación que subía la MAYOR, y `tools/mutar.py` contaba un
   SIN EVIDENCIA como política incumplida (CI de `5040565` en rojo).
5. Referencia independiente: Codex quedó sin cuota; el dueño eligió agy en una conversación y un
   proyecto nuevos, aislado. Encontró dos puntos que la especificación no decidía y en los que el
   núcleo estaba mal (cortocircuito entre filas y entre entradas de `requiere`).

## Verificación final

- Mutación de código, una ronda por objetivo en copias aisladas ([logs](verificacion/)):

  | objetivo | muertos |
  |---|--:|
  | `nucleo/sintaxis.py` | 1050/1050 |
  | `nucleo/medida.py` | 311/316 |
  | `tools/medida.py` | 263/263 |
  | `perfiles/python/mutacion_codigo.py` | 211/211 |
  | `nucleo/unidad.py` | 198/198 |
  | `nucleo/mutacion.py` | 182/182 |
  | `nucleo/relacion.py` | 149/149 |

  Los cinco vivos de la ronda final de `medida.py`: tres sitios de código redundante —una comprobación
  de forma que la construcción de `requiere` ya garantiza, un `idx` sin uso y un `elif` que sólo podía
  recibir `["filas", …]`— que se borraron; dos con test nuevo, verificados aplicando el mutante a mano.
  Las rondas anteriores dejaron treinta sobrevivientes más en `medida.py` (4 y 15) y
  `relacion.py` (11), todos cubiertos o borrados antes de las finales (detalle en la [revisión](REVISION-CLAUDE.md)). Ningún
  equivalente nuevo.

- Suite completa en verde; `tools/aceptacion.py` ✓ con 502 y 503 en rojo; `tools/sintaxis.py --verificar`
  OK; `python tools/mutar.py` sale 0; diferencial regenerado y de acuerdo.
- LyraGASP (64 medidas) y Jam (81) cargan con el núcleo nuevo, y las 4 medidas de Jam con `requiere`
  dan el mismo SIN EVIDENCIA ante evidencia vacía.

## Tareas abiertas que deja

- `20260915-155654-campos`: una medida se declara aplicable por relación aunque lea campos ausentes.
- `20260915-155111-ambito`, `20260915-155111-exigentes`: deudas del catálogo universal.
- `20260915-155111-consumidores`: LyraGASP y Jam siguen en 0.17.0.
- `20260915-155111-sombra`, `20260915-155111-equivalente`, `20260915-155111-relevo`,
  `20260915-023924-ci-tareas`, `20260915-010452-commits`, `20260915-112728-memoria`,
  `20260915-010453-sufijo`.
