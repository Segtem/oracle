# Plan 0.8.0 — el umbral mayor que cero, y el generador que lo ignora

**Fecha:** 2026-09-05 · **Estado:** corte local 0.8.0 verificado el 2026-09-06; sin commit ni publicación
**Sale de:** `estudios/EL-UMBRAL-MAYOR-QUE-CERO.md`, y de un defecto real que ya causó.

**Revisión contra el código actual:** [`estudios/UMBRAL-0.8.0-REVISION.md`](estudios/UMBRAL-0.8.0-REVISION.md).
El corte 0.7.0 está en `f57b67f`. Este corte sube la distribución a 0.8.0; conserva álgebra 0.6
y sintaxis 0.2 por §0. El inventario de once sitios ya fue revisado; el generador ahora comprueba la
polaridad, amplifica conteos simples de cota superior cuando corresponde y se niega explícitamente
cuando no puede fabricar un caso válido. La edad de las sombras ya publica una magnitud con
`peor` y tolerancia 90, sin cambiar su identidad ni su juicio. La sonda del generador alimenta
`meta.el_caso_se_pone_como_debe`, tiene casos de corpus y corre en CI. Los cuatro puntos del plan
quedan implementados o declarados con su argumento en la revisión. Las notas explican el cambio
de valor de la medida; wheel y sdist están construidos y la instalación limpia fue comprobada.

## La ceguera, medida

El censo previo al cambio del 2026-09-06 encontró **54 de 54 medidas base en `umbral <= 0`**, más las tres del
perfil Python, también en cero. Ninguna usa resumen `max` al expandirse. Los números de 55 y de
una invocación propia de `peor` del borrador no se sostienen contra este árbol.

El lenguaje **permite** el otro camino: el verbo `medida` no restringe el umbral, y hay consumidores
que lo usan (`snap.al_ras <= 1.0`, `snap.grilla <= 1.0`, `snap.yaw <= 0.5`) y una biblioteca de
ejemplo (`meta.segtem.todo_umbral_declara_origen`, `<= 5`). Pero **el catálogo que Oracle publica
no lo recorría**, así que su propio corpus no lo medía. La migración de la edad de las sombras
rompe esa premisa: ahora hay una medida base con `max` y `<= 90`, y 53 con `<= 0`.

Y eso no es una preocupación teórica: **ya produjo un defecto**. La exclusión global del mutador
`convertir_conteo_en_existencia` se apoyaba en la premisa «todas las medidas del catálogo tienen
umbral <= 0». Vivió meses sin que nada la contradijera, porque el catálogo base nunca la
contradecía. Cuando por fin se comprobó contra un consumidor, la premisa era falsa — y la exclusión
estaba escondiendo cobertura real: una biblioteca publicaba 16 mutantes certificados cuando eran 17.

## La misma ceguera, un nivel más adentro

Antes de este avance, `nucleo/generador.py` proponía un candidato `falso_verde` con una sola fila
ofensora, asumiendo que `count == 1` rompía el umbral. Con `contar <= 5`, el candidato salía verde
estando etiquetado como rojo. `evaluar_utilidad` lo descartaba antes de escribir, pero sin explicar
que la fabricación no había logrado la polaridad: no llegaba un caso inválido al corpus, sí se
ocultaba el límite del generador bajo un mensaje de «ruido».

O sea: la herramienta que propone casos está rota exactamente para las medidas que Oracle nunca
escribió. Las dos cosas se sostienen mutuamente, y por eso van juntas en la misma versión.

## Lo que 0.8.0 tiene que dejar

1. **Al menos una medida propia con umbral > 0**, y no de adorno: elegida porque su dominio es una
   magnitud y no una cardinalidad. El estudio propone una candidata; la elección se justifica o se
   cambia, pero el camino queda vivo en el corpus del propio Oracle.

2. **El generador deja de asumir el cero.** Tiene que fabricar evidencia que rompa *el umbral que la
   medida declara*, no un umbral supuesto. Y si no puede —porque el umbral es una magnitud y no un
   conteo—, tiene que decirlo en vez de producir un caso que se contradice a sí mismo.

3. **Una medida que vigile la suposición.** Es lo que faltó las dos veces: nada detectaba que un
   sitio del código asumiera `umbral == 0`. El estudio inventarió once lugares; la pregunta es cuál
   de esos es comprobable desde el álgebra y cuál sólo desde el código.

4. **El resto del inventario, triado.** De los once sitios que el estudio encontró, tres están
   marcados como bombas silenciosas y el resto como correctos o sesgados. Cada uno se cierra o se
   declara, con su argumento.

## La regla que ordena la distinción

Del estudio, y conviene tenerla a mano al escribir la medida nueva:

| | el número va en el FILTRO | el número va en el UMBRAL |
|---|---|---|
| tipo | oráculo de ausencia de defectos | cota de magnitud |
| resumen | `contar` | `max` · `min` · `promedio` |
| unidad | cardinalidad: cuántas filas ofenden | magnitud del dominio: cm, grados, segundos |
| umbral | **`<= 0`** — ningún defecto tolerable | **`<= K`** — la magnitud extrema no debe pasar K |
| si K > 0 | concesión por comodidad | especificación del contrato |

Un umbral > 0 sobre un `contar` casi siempre es una concesión disfrazada. Sobre un `max` es el
contrato. La medida nueva de Oracle tiene que ser del segundo tipo, o no vale la pena.

## Lo que este plan NO debe hacer

**Escribir una medida con umbral > 0 sólo para tener una.** Una medida que existe para ejercer un
camino del lenguaje y no para medir algo que importa es exactamente la clase de decoración que este
proyecto rechaza en todo lo demás. Si no aparece una candidata legítima, el hallazgo es ése y hay
que decirlo, no fabricar una.

**Aflojar el generador para que no se queje.** Si no puede fabricar un rojo creíble para una medida,
la respuesta correcta es negarse y decir por qué — no producir un caso que el corpus va a aceptar y
que no prueba nada.
