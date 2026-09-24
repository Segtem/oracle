# Roadmap 0.19.0 — consultas de tareas (TQL en español) y lo que faltaba de tatr

Fecha: 2026-09-15. Base: distribución 0.18.1, álgebra 0.6, sintaxis 0.4.
Tarea: [`20260915-023750-tql`](../../tareas/20260915-023750-tql/TAREA.md). Implementa agy; revisa, mide y
corta Claude. Encargo: [vault-kb/estudios/0.19.0-tql/ENCARGO-AGY.md](../estudios/0.19.0-tql/ENCARGO-AGY.md).

## El problema

`oracle tarea` cubre casi todo tatr, pero no lo que tatr usa para trabajar con muchas tareas: un
lenguaje de consultas. Hoy `listar` filtra por **una** etiqueta y por texto, y `desetiquetar` sólo
por estado. Tampoco hay orden alternativo en `listar`, `referencias` exige el ID aunque uno esté
parado en la carpeta de la tarea, e `init` siempre crea el README.

TQL quedó fuera en 0.16.0 a propósito. El dueño decidió traerlo **con vocabulario en español**,
coherente con el resto del CLI.

## Lo que se toma de tatr, medido en su código (`src/query.c`, 2026-09-15)

- Tokens: `[` y `]` sueltos; el resto se corta en blancos y corchetes.
- Primarias: `:etiqueta`, `[ expr ]`, `not <primaria>`, `any`, `tagged`, `priority`, un HUID literal
  (igualdad exacta con el ID) y un entero con signo.
- Precedencia: `not` sobre una primaria; comparaciones entre enteros, encadenadas a izquierda;
  `and` antes que `or`. El resultado tiene que ser booleano.
- Consulta vacía equivale a `any`. `-debug` imprime tokens y opcodes.
- Errores: la consulta, un `^` bajo el token, y el mensaje.

## Lo que Oracle hace distinto, a propósito

| tatr | Oracle 0.19.0 | por qué |
|---|---|---|
| `and` `or` `not` | `y` `o` `no` | vocabulario del CLI |
| `any` `tagged` `priority` | `cualquiera` `etiquetada` `prioridad` | ídem |
| `lt` `le` `gt` `ge` `eq` `ne` | `menor` `hasta` `mayor` `desde` `igual` `distinto` | se leen: `prioridad desde 50` |
| error de tipo al evaluar cada tarea | error de tipo **al compilar**, antes de leer tareas | los tipos de las primarias son fijos: no hace falta esperar a una tarea |
| etiquetas distinguen mayúsculas | no distinguen | igual que `listar --etiqueta` y `etiquetar` |
| `.tag` como forma vieja de `:tag` | no existe | no hay nada que conservar |

## Entregas

1. **`tools/tareas_consulta.py`**: léxico, parser, verificación de tipos y evaluación. Puro: no lee
   archivos ni conoce el CLI.
2. **`listar <consulta>`** (posicional, las palabras se unen con un espacio como en tatr), combinable
   con `--etiqueta`, `--texto`, `--cerradas`/`--todas`; `--explicar` muestra tokens y la forma
   compilada sin listar; `--por-id` (más nuevas primero, como `tatr ls -id`) y `--invertir` (como `-a`).
3. **`desetiquetar --consulta "<expr>"`**, excluyente con IDs explícitos, respetando el estado como
   el modo masivo actual.
4. **`referencias` sin argumento** dentro de la carpeta de una tarea.
5. **`init --sin-readme`**.

## Fuera de alcance

- Consultas sobre el estado (`abierta`/`cerrada`) o el texto dentro del lenguaje: siguen siendo
  banderas, como en tatr.
- Aceptar también el vocabulario de tatr: el dueño eligió sólo español.
- Cambios en `hechos`, álgebra o sintaxis de Oracle.

## Criterios de salida del corte

Suite completa verde; tests del lenguaje de ambos lados (agy y revisión independiente escrita antes
de leer el código); mutación de `tareas_consulta.py` y de los módulos que cambien, sin sobrevivientes
ni equivalentes; `verificar_instalacion` con una consulta desde el wheel; CI verde; «Diferencias con
tatr» actualizada; notas, especificación y cifras al día. Commits con el ID de la tarea.
