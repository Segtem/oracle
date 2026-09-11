# Plan — lo que le falta a Oracle después de 0.13.1

> Continuación del 2026-09-10: [trabajo y verificaciones](RELEVO-2026-09-10.md).
> El estado que sigue se conserva como antecedente fechado.

## Balance al 2026-09-11

| Frente | Estado actual |
|---|---|
| CLI en CI y custodia de las sondas | Cerrado: 15 custodias en la matriz; CLI 509/509 y metamórficas 242/242, sin sobrevivientes ni timeouts. |
| DECISION-004 | Cerrada en 0.14.0 con defectos reales; aceptación conserva código 0. |
| Autenticidad | Estudio y experimento terminados. La autenticidad sigue sin estar comprobada; una custodia externa requeriría otra premisa de autoridad. |
| Consumidores | Plan de aceptación de Jam capturado y revalidado. Quedan observaciones propias del consumidor, incluida la malla del caso 018; LyraGASP queda fuera de este trabajo. |
| Los 94 orígenes | Irrecuperables, bajo sombra y cota; no se reclasificaron. |

La mejora de rendimiento también quedó medida: resolver el contexto una vez por expresión ahorró
16,2 % en la reproducción del escenario de sombras; no se extrapola a toda la suite. El perfil del
álgebra bajó su ronda de 383,70 a 140,83 s y conservó 390/390. La verificación completa del relevo
terminó en código 0, incluidos 1536 tests y 959/959 mutantes de medidas.

El dueño autorizó el corte **distribución 0.15.0**, manteniendo álgebra 0.6 y sintaxis 0.4,
por los cambios de códigos de salida del CLI. El argumento y el contenido del corte están en
[las notas de release](NOTAS-DE-RELEASE.md). La publicación en PyPI queda a su cargo.

Los planes generales conservan historia: `--vigilar` y el servidor LSP ya están implementados,
aunque `PLAN-IDE.md` todavía los describa como futuros. Una interfaz web sigue siendo una opción,
no un compromiso. El próximo avance de accesibilidad debe partir de fricción observada al escribir
y usar medidas; el plan de Jam no demuestra por sí solo adopción ni clausura de sus dependencias.

## Antecedente al 2026-09-09

**Escrito el 2026-09-09**, con el árbol en `0.13.1`, CI verde y PyPI publicado.

Cinco cosas quedan abiertas. **No son del mismo tipo**, y confundirlas es lo que hace que una lista
de pendientes envejezca: dos esperan que aparezca algo, dos esperan trabajo en repos ajenos, y una
sola tiene camino claro. El plan las separa por eso.

## Lo que el proyecto dice de sí mismo hoy

```
✗ meta.la_medida_no_se_fija_solo_con_evidencia_fabricada   1
✗ meta.todo_caso_observado_declara_de_donde_salio         94  [EN SOMBRA, cota 94]
```

14 custodias declaradas, **una** fuera de la matriz de mutación de CI.

---

## Fase 1 — `cli.py` entra a la matriz · *camino claro*

**Estado:** medida en **504/504**, cero sobrevivientes. No es deuda: es **costo**, 36,5 minutos por
ronda porque su perfil corre cuatro módulos de tests en serie.

**Qué hacer:** reordenar su entrada en `PRIORIDADES`. El criterio ya está escrito en
`tools/mutar_codigo.py`: *un mutante cuesta lo que tarde el arnés en LLEGAR al test que lo mata*, así
que el módulo más específico va adelante. El precedente es `tools/contexto.py`, que pasó de **858 a
56 segundos** con ese solo cambio, y `tools/mcp.py`, que hizo lo mismo.

**Criterio de terminado:** la ronda baja de ~10 minutos **sin perder mutantes** — sigue en 504/504 —
y `cli.py` entra a la matriz. Con eso `CUSTODIAS_SIN_MEDIR` queda **vacía por primera vez**.

**Riesgo:** que reordenar no alcance porque el costo esté en un test lento y no en el orden. En ese
caso el hallazgo es *cuál* test, y eso también sirve.

---

## Fase 2 — la última de DECISION-004 · *espera que aparezca algo*

**Estado:** `meta.sintaxis_casos_cubre_casos` sostenida por 3 casos `generada`. Es el último rojo que
tumba la corrida, desde el 2026-08-26.

**Cómo cayó su gemela**, y es el único camino que la decisión admite: `meta.sintaxis_cubre_algebra`
salió de la lista el 2026-09-08 **no transcribiendo evidencia sino cambiando el mundo** — apareció un
defecto real en la superficie de medidas (`agrupar` sin agregados), y la corrida que lo encontró es
evidencia observada legítima.

**Qué hacer:** buscar el defecto equivalente en la superficie de CASOS, con el mismo método que
encontró el de medidas: **probar la frontera entre lo que L0 acepta y lo que la superficie sabe
escribir**. Si hay una forma que L0 admite y `.caso` no puede escribir —o que escribe y no vuelve—,
ahí está.

**Ya comprobado y descartado (2026-09-09):** el `alcance` declara no cubrir objetos anidados ni
listas «porque L0 los rechaza». **Es cierto**: `corpus.py` los rechaza con
`no es escalar (dict) — L0 no admite anidamiento`. Ese hueco se midió y se sostiene.

**Riesgo real:** que no haya defecto. Entonces la respuesta honesta es que la deuda sigue, no
inventar uno. Un resultado negativo bien medido cierra la búsqueda, no la deuda.

---

## Fase 3 — autenticidad · *pregunta de investigación*

**Estado:** nada distingue una corrida de una transcripción. Cada observación lo declara: *«dos
declaraciones falsas iguales pasan igual que dos verdaderas»*. Es el piso sobre el que se apoya
`procedencia: observada`, la única procedencia que afirma algo sobre el mundo.

**Qué NO hacer:** firmar la observación con una clave del propio proyecto. Eso prueba que Oracle la
escribió, no que el sensor corrió.

**Qué explorar, en orden de cuánto compra:**

1. **Algo que sólo una corrida real puede producir.** Un valor que el que transcribe no pueda
   conocer de antemano: la huella de los archivos **en el momento de leerlos**, tomada por el propio
   sensor y no por el recorrido.
2. **Un desafío externo.** Que quien pide la observación entregue un dato imprevisible que el sensor
   tenga que incorporar a su salida.
3. **Aceptar el límite y acotarlo mejor.** Si lo anterior no compra nada, decir con precisión qué
   sí prueba una observación capturada —que ESTA evidencia existió con ESTOS referentes en ESTE
   momento— y dejar de sugerir más.

**Criterio de terminado:** un estudio con una recomendación y su contraargumento. **No código**, a
menos que la recomendación sea barata y clara.

---

## Fase 4 — los consumidores · *repos ajenos, decide el dueño*

- **Jam:** 23 casos sin procedencia declarada; el caso `018` necesita una malla degenerada que sólo
  se ve abriendo el editor.
- **LyraGASP:** 26 sin declarar. Está en verde y trabajando sobre MetaHuman: no se toca ahora.
- **`observar.py` sigue conectado sólo al trabajo del propio Oracle.** Que observar sea barato *para
  un consumidor* es lo que haría que sus casos nuevos nazcan con comando y registro probados.

---

## Fase 5 — los 94 `origen` · *cerrada como irrecuperable*

No se cierran hacia atrás sin inventar: el árbol contra el que corrieron ya no existe, así que
re-correr hoy da otros números y no prueba nada. La cota los tiene en 94 y una medida hace fallar la
corrida si suben. **Esto no es una tarea pendiente: es una deuda declarada y acotada**, y conviene
dejar de listarla como si alguien fuera a hacerla.

---

## El orden

**1 → 2 → 3.** La primera cierra una lista; la segunda puede cerrar el último rojo del proyecto; la
tercera decide qué significa la palabra más cargada del lenguaje. La cuarta espera decisión del
dueño y la quinta ya está cerrada como lo que es.
