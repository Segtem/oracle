# Cierre 0.19.0 — consultas de tareas en español

2026-09-15. Tarea [`20260915-023750-tql`](../../tareas/20260915-023750-tql/TAREA.md).
Implementó agy; revisó, corrigió y verificó Claude. El dueño eligió TQL como siguiente tarea y el
vocabulario en español; la publicación en PyPI queda a su cargo.

## Qué se entregó

Los cuatro puntos de la tarea:

1. **Lenguaje de consultas** (`tools/tareas_consulta.py`): gramática de tatr (`src/query.c`) con
   `y`/`o`/`no`, `[ ]`, `cualquiera`/`etiquetada`/`prioridad`, `:etiqueta`, enteros, ID exacto y
   `menor`/`hasta`/`mayor`/`desde`/`igual`/`distinto`. AST tipado: los errores de tipo se rechazan al
   compilar, con la consulta y un `^`. `listar <consulta>` y `desetiquetar --consulta`.
2. **Orden de `listar`**: `--por-id` (más nuevas primero, como `tatr ls -id`) e `--invertir` (como `-a`);
   además `--explicar`, equivalente de `tatr ls -debug`.
3. **`referencias` sin ID** dentro de la carpeta de una tarea o un subdirectorio.
4. **`init --sin-readme`**.

## Recorrido

1. Antes del plan se leyó el código de tatr —léxico, parser, evaluación, `ls`, `task_sorter`— para no
   copiar el README: así salieron el `-id` descendente y la comparación de etiquetas.
2. [Plan](../../PLAN-0.19.0-TQL.md) y [encargo](ENCARGO-AGY.md). Claude escribió
   `tests/test_tareas_consulta_revision.py` antes de leer la entrega; pasó entero sobre ella.
3. [Revisión](REVISION-CLAUDE.md): la entrega agregaba comparadores simbólicos, un `-c`, código sin
   conducta y dos formatos de error, y su documentación atribuía a tatr cosas que no tiene. Corregido
   por Claude, con tests que fijan lo corregido.

## Verificación final

- Mutación de código, una ronda por objetivo en copias aisladas ([logs](verificacion/)):
  - `tools/tareas_consulta.py`: **99/99**, con un equivalente declarado —la columna de la consulta
    vacía, que nada lee—.
  - `tools/tareas_contexto.py`: **212/212**.
  - `tools/tareas.py`: **380/381**. El sobreviviente es `listar --explicar` devolviendo `None` en vez
    de 0, que el CLI también convierte en código 0. Lo mata un test en proceso, agregado con la ronda
    ya en marcha y verificado aplicando el mutante a mano.
- Las rondas anteriores dejaron sobrevivientes que se cubrieron antes de estas: el `explicar` de seis
  nodos sin fijar; un `frozen=True` sin conducta, retirado; `referencias` sin ID desde una carpeta
  oculta con `TAREA.md`; y una rama de error inalcanzable —«operador infijo inesperado», a la que no
  llega ninguna de las 16 104 consultas de hasta cuatro tokens del vocabulario—, que se borró.
- Un mutante de `tokenizar` que no avanza agregaba tokens hasta agotar la RAM de la máquina, y el
  sistema mató las rondas. Se corrieron con `ulimit -v`; el arreglo en el arnés queda como tarea.

- Suite completa: 2051 tests en verde.
- `tools/verificar_instalacion.py`: `WHEEL OK`, con una consulta en español y una consulta de tipo
  inválido (código 2 con su posición) desde el wheel.
- `tools/cifras.py` sin deriva (2051 tests · 7187 sitios de mutación de código).

## Tareas abiertas que deja

- `20260915-010454-motor`: la fachada `Motor` con otra selección y sin sombras.
- `20260915-023924-ci-tareas`: CI no corre cuando sólo cambia `tareas/`.
- `20260915-010452-commits`: los commits como hechos del tracker.
- `20260915-010453-sufijo`: `tarea nueva` arma un ID largo con el título.
- `20260915-112728-memoria`: `mutar_codigo` no limita la memoria de un mutante (se midió en esta ronda).
