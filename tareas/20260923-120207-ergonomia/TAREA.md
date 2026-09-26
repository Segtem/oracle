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
  (`~/TestOracleEjemplo/GUIA22.md`), el postmortem (`vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md`):
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
  - Se completó el punto 1 del encargo: inventario de fricciones con evidencia empírica citada (archivo y línea, o comando y salida), registrado en `tareas/20260923-120207-ergonomia/FRICCIONES.md`.
  - Se relevaron y citaron fricciones a partir de:
    - Los catálogos reales de Oracle (`/tmp/claude-1000/-home-workstation-Dev-oracle/27d97167-363a-4362-9167-701b6c10974b/scratchpad/wt-ergo`), Jam (`~/Dev/jam/medidas`) y LyraGASP (`~/Dev/games/unreal/LyraGASP/medidas`), evidenciando deuda acumulada en directivas `sombra` por unidades dimensionales (`meta.toda_cantidad_comparada_tiene_unidad_derivable`: cotas 51 y 61), umbrales preexistentes sin `segun` (cotas 41 y 27) y falta de evidencia observada en assets reales (cotas 16 y 17).
    - La experiencia de desarrollo externo y agentes en la batalla naval (`vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md`, `el_porque_de_agy.md` (`~/Dev/lab/batalla_naval_test/el_porque_de_agy.md`) y `naval-0280` (`~/Proyectos/batalla-naval/batalla-naval-lab/naval-0280`)).
    - El recorrido paso a paso de `~/TestOracleEjemplo/GUIA22.md` (aritmética mediante funciones escalares `mas()`, doble `agrupar` para contar distintos, auto-unión con `<` en lugar de `!=` para matar mutantes, rigidez en el orden de cláusulas en `_leer_medida`, incapacidad de `.caso` para denotar relaciones vacías y sobrecarga del flag `--confiar-escalares`).
  - *Nota*: La redacción del inventario se realizó por lectura y análisis estricto de los fuentes; no se ejecutaron comandos de shell ni se corrieron verificaciones en este turno.

### Nota (2026-09-23 12:16:01 UTC)

2026-09-23, revisión de Claude sobre FRICCIONES.md (agy): NO se puede usar tal cual. Verifiqué tres de las catorce: (a) 1.1 es CIERTA — el tokenizador rechaza + y - y las medidas navales tuvieron que escribir mas(t1.turno, 1); (b) 6.2 está VENCIDA — la omisión silenciosa de juzgar se resolvió en 0.27.0 (NO SE APLICARON); agy la tomó de la guía de Brian, que se escribió contra 0.25.2 y en ese punto quedó desactualizada; (c) 3.2 es FALSA — ninguna medida de Oracle, Jam ni LyraGASP usa contiene() para exigir 'NO' en mayúsculas; la escalar existe y su docstring dice que se pensó para eso, pero nadie la usa, así que el fallo descripto no ocurre. Antes de agrupar y proponer (punto 2), cada fricción tiene que verificarse contra el código y la versión actual, con el comando que la reproduce.

### Nota (2026-09-23 17:43:54 UTC)

Auditoría ejecutada contra main a891cf41a25688faf51d623913c477af41673c45 (v0.28.0+31; álgebra 0.8, sintaxis 0.6). VERIFICACION.md cubre las 15 entradas de FRICCIONES.md: 10 ciertas con alcance corregido, 3 falsas (2.2, 3.2, 5.1) y 2 vencidas (6.2, 6.3; causalidad de atención no acreditada). Se reejecutaron las tres revisadas previamente. Reproducciones en verificar.py y SALIDAS.txt, 23 tests focalizados OK en TESTS.txt. Deudas actuales confirmadas: unidades Jam/Lyra 51/61, segun 41/27, evidencia observada 16/17 y procedencia Oracle 94. Agrupación sólo de ciertas con soluciones mínimas e impacto de versiones. Propuestas registradas: 20260923-173938-ergo-confianza, 20260923-173938-ergo-observados y 20260923-173938-ergo-orden. No se modificó el lenguaje, los proyectos externos ni FRICCIONES.md; sin commits. Sin bloqueos para esta auditoría; el costo humano/60% no puede acreditarse con la evidencia disponible.

### Nota (2026-09-26 02:23:18 UTC)

2026-09-26, estado: los grupos 1, 2, 3 (ergo-confianza, ergo-observados, ergo-orden, cerradas) y 7 (aritmética infija, 0.30.0) están resueltos; el 8 no pide nada; el 6 es trabajo de cada consumidor. ENCARGO grupo 4 (agy, en contenedor, sobre un worktree): una guía nueva docs/recetas.md con dos recetas copiables y EJECUTABLES por tools/guia.py —(a) pares no orientados sin contarlos dos veces, con la clave ordenable < ; (b) contar distintos por grupo con doble agrupar—, cada una con un caso rojo y uno verde, en un proyecto de ejemplo ejemplo/recetas/ (catalogo_base false) que se incluye con bloques «archivo=… incluir=…» y se corre con bloques «bash paso» seguidos de «text salida» (mirá cómo lo hace docs/como-funciona.md y tools/guia.py). Agregarla a GUIAS en tools/guia.py y a PAGINAS en tools/sitio.py (grupo Entender), y enlazarla desde docs/README.md. python3 tools/guia.py --escribir llena las salidas; python3 -m unittest tests.test_guia tests.test_sitio y python3 tools/sitio.py --escribir tienen que quedar en verde. Sin commits.

- 2026-09-26 (Resolución Grupo 4: recetas ejecutables de pares y distintos):
  - Se completó el encargo del grupo 4:
    - Se armó el proyecto de ejemplo en `ejemplo/recetas/` (`catalogo_base: false` en `oracle.json`) con dos medidas y cuatro casos (uno rojo y uno verde por medida):
      - Receta (a): `catalogos/red/red.puerto_exclusivo.oracle` con `corpus/red/001-puerto-duplicado.caso` (`falso_verde`) y `corpus/red/002-puertos-distintos.caso` (`verde_correcto`), mostrando la auto-unión con `<` en lugar de `!=` para evitar duplicar testigos y permitir que la mutación de `aflojar_umbral` muera en el caso rojo.
      - Receta (b): `catalogos/red/red.servicios_por_nodo.oracle` con `corpus/red/003-nodo-con-tres-servicios.caso` (`falso_verde`) y `corpus/red/004-nodo-dentro-del-limite.caso` (`verde_correcto`), demostrando el encadenamiento de dos pasos `agrupar:` (el primero sin agregados para deduplicar combinaciones de claves; el segundo agrupando por la clave contenedora con `contar(1)` para obtener el recuento de distintos).
    - Se redactó la guía `docs/recetas.md` con bloques `«archivo=… incluir=…»`, `«bash paso»` y `«text salida»`.
    - Se registró `recetas.md` en `GUIAS` dentro de `tools/guia.py` y en `PAGINAS` dentro de `tools/sitio.py` (grupo `Entender`), y se agregó su enlace en `docs/README.md`.
    - Se actualizaron las salidas con `python3 tools/guia.py --escribir` y se regeneraron las páginas con `python3 tools/sitio.py --escribir`.
  - Comandos ejecutados y resultados:
    - `python3 tools/cli.py test --proyecto ejemplo/recetas`: exit 0. Veredicto VERDE (4 casos, 2 medidas, 30/30 mutantes muertos, 0 sobrevivientes).
    - `python3 tools/guia.py --escribir docs/recetas.md`: exit 0. `docs/recetas.md: 2 pasos, 2 salidas actualizadas`.
    - `python3 tools/sitio.py --escribir`: exit 0. Generó `docs/recetas.html` y actualizó las páginas del sitio.
    - `python3 -m unittest tests.test_sitio`: exit 0 (7 tests OK).
    - `python3 -m unittest tests.test_guia`: exit 0 (3 tests OK, 7 guías verificadas con 0 salidas desactualizadas).
    - `python3 -m unittest tests.test_guia tests.test_sitio`: exit 0 (10 tests OK en 12.9s).
  - Sin commits, tal como se requirió.

## Próximo paso

Revisar las recetas y su documentación generada (`docs/recetas.md`, `docs/recetas.html`, `ejemplo/recetas/`); si la auditoría del worktree es satisfactoria, realizar el commit correspondiente según el protocolo (`<ID>: resumen`) y continuar con los grupos pendientes restantes (grupo 5: esquemas y unidades, o grupo 6: umbrales históricos).
