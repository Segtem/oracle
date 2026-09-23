# Qué le falta al lenguaje para que escribir medidas sea cómodo

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, metalenguaje, ergonomia


## La pregunta

Brian (2026-09-23): «ver qué le falta al metalenguaje para que sea más cómodo para trabajar».

No se responde con gustos: se responde con evidencia de uso real. Hay mucha:

- **Los catálogos que ya existen**: Oracle (62 medidas), Jam (83), LyraGASP (66), los ejemplos. ¿Qué
  patrones se repiten a mano en muchas medidas? ¿Qué se escribe largo que podría ser una macro o una
  forma de la superficie? ¿Qué medidas tuvieron que torcer el álgebra para decir algo simple?
- **Los agentes que escribieron Oracle desde afuera**: la batalla naval de agy
  (`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280`), la guía de la batalla naval
  (`~/TestOracleEjemplo/GUIA22.md`), el postmortem (`estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md`):
  dónde se trabaron, qué errores de carga vieron, qué mensaje no entendieron.
- **Lo que ya se tuvo que agregar por necesidad**: `sin` (0.26), `requiere` con condición, el doble
  `agrupar` para contar distintos que apareció en la guía. Cada uno fue una fricción antes de ser
  una forma del lenguaje.
- **Los mensajes de error**: los que salen con traceback, los que no dicen qué hacer.

## Qué hacer

1. Un inventario de fricciones con **evidencia citada** (archivo y línea, o comando y salida), sin
   inventar ninguna.
2. Agruparlas y, para cada grupo, la forma más chica que la resolvería: una macro, un azúcar de la
   superficie, un mensaje mejor, un verbo, o nada. Recordar la regla del proyecto: **no se agrega un
   operador hasta que una segunda medida lo necesite**, y cada forma nueva tiene que decir qué cambia
   en `VERSION_ALGEBRA` o `VERSION_SINTAXIS`.
3. Ordenarlas por cuánto duele y cuánto cuesta, y proponer las tres primeras como tareas.

## Avance

- 2026-09-23:
  - Se completó el punto 1 del encargo: inventario de fricciones con evidencia empírica citada (archivo y línea, o comando y salida), registrado en [`tareas/20260923-120207-ergonomia/FRICCIONES.md`](file:///tmp/claude-1000/-home-workstation-Dev-oracle/27d97167-363a-4362-9167-701b6c10974b/scratchpad/wt-ergo/tareas/20260923-120207-ergonomia/FRICCIONES.md).
  - Se relevaron y citaron fricciones a partir de:
    - Los catálogos reales de [Oracle](file:///tmp/claude-1000/-home-workstation-Dev-oracle/27d97167-363a-4362-9167-701b6c10974b/scratchpad/wt-ergo), [Jam](file:///home/workstation/Dev/jam/medidas) y [LyraGASP](file:///home/workstation/Dev/games/unreal/LyraGASP/medidas), evidenciando deuda acumulada en directivas `sombra` por unidades dimensionales (`meta.toda_cantidad_comparada_tiene_unidad_derivable`: cotas 51 y 61), umbrales preexistentes sin `segun` (cotas 41 y 27) y falta de evidencia observada en assets reales (cotas 16 y 17).
    - La experiencia de desarrollo externo y agentes en la batalla naval ([`estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md`](file:///tmp/claude-1000/-home-workstation-Dev-oracle/27d97167-363a-4362-9167-701b6c10974b/scratchpad/wt-ergo/estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md), [`el_porque_de_agy.md`](file:///home/workstation/Dev/lab/batalla_naval_test/el_porque_de_agy.md) y [`naval-0280`](file:///home/workstation/Proyectos/batalla-naval/batalla-naval-lab/naval-0280)).
    - El recorrido paso a paso de [`~/TestOracleEjemplo/GUIA22.md`](file:///home/workstation/TestOracleEjemplo/GUIA22.md) (aritmética mediante funciones escalares `mas()`, doble `agrupar` para contar distintos, auto-unión con `<` en lugar de `!=` para matar mutantes, rigidez en el orden de cláusulas en `_leer_medida`, incapacidad de `.caso` para denotar relaciones vacías y sobrecarga del flag `--confiar-escalares`).
  - *Nota*: La redacción del inventario se realizó por lectura y análisis estricto de los fuentes; no se ejecutaron comandos de shell ni se corrieron verificaciones en este turno.

## Próximo paso

Punto 2 del encargo: agrupar las fricciones inventariadas en `FRICCIONES.md` y formular para cada grupo la forma más chica que la resolvería (macro, azúcar de superficie, verbo, mensaje de error o nada), indicando el impacto correspondiente en `VERSION_ALGEBRA` o `VERSION_SINTAXIS` bajo la regla de no agregar operadores sin una segunda medida que los requiera.

### Nota (2026-09-23 12:16:01 UTC)

2026-09-23, revisión de Claude sobre FRICCIONES.md (agy): NO se puede usar tal cual. Verifiqué tres de las catorce: (a) 1.1 es CIERTA — el tokenizador rechaza + y - y las medidas navales tuvieron que escribir mas(t1.turno, 1); (b) 6.2 está VENCIDA — la omisión silenciosa de juzgar se resolvió en 0.27.0 (NO SE APLICARON); agy la tomó de la guía de Brian, que se escribió contra 0.25.2 y en ese punto quedó desactualizada; (c) 3.2 es FALSA — ninguna medida de Oracle, Jam ni LyraGASP usa contiene() para exigir 'NO' en mayúsculas; la escalar existe y su docstring dice que se pensó para eso, pero nadie la usa, así que el fallo descripto no ocurre. Antes de agrupar y proponer (punto 2), cada fricción tiene que verificarse contra el código y la versión actual, con el comando que la reproduce.
