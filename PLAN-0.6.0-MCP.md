# Plan 0.6.0 — una herramienta MCP para escribir medidas

**Fecha:** 2026-09-04 · **Estado:** propuesta, sin empezar
**Sale de:** `estudios/MCP-FALLAS.md` (la evidencia) y `estudios/MCP-CONTRATO.md` (el contrato),
escritos en paralelo y sin verse.

## Primero, lo que se descartó, que es mío

La primera versión de este plan ponía el peso en una compuerta de escritura: `oracle_proponer`
guardaría una medida sólo si venía con evidencia que la pone en rojo y evidencia que la pone en
verde. Se descarta, por dos razones que no son de gusto.

**La primera la midió el estudio de las fallas.** El corpus tiene 180 casos; 152 los cazó el arnés
automático y **28 se le escaparon**. De esos 28, la compuerta de escritura ataja **cero**: ninguno es
«un agente guardó una medida sin probarla». El 85,7% son falsos verdes —evidencia desincronizada,
veredictos vacuos, jurisdicción equivocada— y todos ocurren al LEER, no al escribir.

**La segunda la señaló el estudio del contrato**, y es la conclusión que yo mismo tenía escrita sin
sacarla: las dos evidencias pueden haber sido fabricadas para repetir exactamente el error de la
medida. Entonces la compuerta no autoriza a llamarla buena — y guardar después de ella convierte
evidencia insuficiente en apariencia de aprobación, que es peor que no tener compuerta.

Queda el experimento, sin la escritura y sin la promesa.

## La partición que ordena todo

Del estudio de las fallas, medido sobre los 28 casos que el arnés no cazó:

| | casos | |
|---|---|---|
| **fuera del alcance de un MCP** | 14 | fallas de runtime y señales, saltos causales del propio modelo, falsificación deliberada en disco, deudas de diseño del lenguaje |
| **al alcance** | 14 | evidencia desincronizada, veredictos vacuos, jurisdicción, reglas de forma |

**Ningún servidor puede prometer más de la mitad.** Quien diga que un protocolo de herramientas
resuelve un `SIGTERM` sin `finally`, o evita que un modelo razone mal sobre números verdaderos, está
vendiendo humo. Lo que sí puede hacer es erradicar la otra mitad.

## La regla que los dos estudios encontraron por separado

**Un agente no tiene con qué dudar de la herramienta.** Si el servidor contesta
`{"veredicto": "verde"}`, lo toma como verdad y sigue.

De ahí sale la regla, y no es negociable:

> **Fallo cerrado y respuestas falsables. Nunca una lista vacía, nunca un verde, nunca un resumen
> opaco.** Un catálogo ilegible produce un error, no un cero.

Toda respuesta lleva sus premisas a la vista: cardinalidades intermedias (`filas_evaluadas`,
`filas_infractoras`, `es_vacuo`), el cálculo desglosado (valor, comparador, cota), la frescura
(huella declarada contra huella en disco, y un estado explícito), y testigos concretos en los rojos.
El agente no recibe una orden de fe: recibe una derivación con sus premisas.

**Esta regla ya se validó, antes de escribir una línea del servidor.** El 2026-09-04, buscando cómo
tenía que ser el MCP, se encontró que `oracle contexto` le decía a los dos consumidores «LAS 0
MEDIDAS QUE YA EXISTEN» teniendo 41 y 9 — un `except Exception: return []` se tragaba el fallo de
cargar sus escalares. Es exactamente el modo de falla que la regla prohíbe, en la herramienta que
existe para asistir a un agente. Está arreglado (commit `20a2ded`).

## Las tres herramientas

Sólo lectura. El proyecto se fija al arrancar el proceso; ninguna acepta una ruta por llamada y
ninguna crea, modifica ni borra archivos.

Tres es el corte que conserva tres preguntas distintas. Con dos habría que mezclar la evaluación
barata con la ronda de mutación cara, y sus resultados parecerían tener la misma fuerza. Con cuatro
aparece una herramienta de escritura o se parte el catálogo en índice y detalle, que es obligar al
modelo a elegir entre dos nombres para una misma pregunta.

### `oracle_catalogo_efectivo` — ¿qué me obliga, y por qué?

Sale de `catalogo_efectivo`, la función que 0.5.0 dejó llamable: aplica el filtro de ámbito. La
capacidad nueva no es «listar medidas en JSON» —eso ya se hace por consola— sino **exponer la
selección de jurisdicción con la procedencia conservada**.

Su rechazo más importante distingue dos cosas que un agente confunde:

- `MEDIDA_NO_EFECTIVA` — existe en una fuente seleccionada, pero su ámbito no obliga acá.
- `MEDIDA_DESCONOCIDA` — no aparece en ninguna fuente seleccionada.

«No existe» invita a crear un duplicado; «no tiene jurisdicción acá» enseña que el archivo ya tiene
dueño.

### `oracle_evaluar` — ¿qué hace esta medida con esta evidencia?

Una medida del catálogo o uuna escrita entera en memoria; nunca una ruta, porque aceptar rutas la
vuelve otra ortografía de un comando que ya existe y abre lecturas fuera de la raíz.

### `oracle_desafiar` — ¿qué parte de este candidato no está fijada?

El lazo completo en memoria: reúne los casos, comprueba que el original reproduzca lo esperado,
exige las dos polaridades, muta y separa cambio conductual de rechazo del álgebra. **Nada toca el
disco.**

Su conclusión más fuerte se llama `todos_detectados_por_conducta` — no `correcta`, no `aprobada`, no
`lista_para_guardar`. Significa exactamente «estos mutadores, escritos por estos autores, fueron
discriminados por estas evidencias», y nada más. Y no acepta `procedencia`: una llamada no puede
convertir evidencia fabricada en evidencia observada.

## Cómo se verifica el servidor

La prueba entra por stdin y observa stdout, stderr, código de salida y sistema de archivos: llamar a
las funciones del adaptador no fija el contrato de transporte. Un corpus de conversaciones JSON-RPC
completas fija los bytes, y la mutación del módulo demuestra que esos casos fallan cuando el
adaptador altera una afirmación.

La afirmación que custodia, y que nadie más comprueba: **que lo que el servidor le dice a un agente
sea lo que Oracle sabe**. Concretamente, si una mutación que reemplaza `catalogo_efectivo` por
`catalogos_a_cargar`, o que traga una excepción, deja el corpus MCP en verde, el servidor no está
verificado.

Esa mutación no es hipotética: es el defecto que vivió en `tools/contexto.py` hasta hoy.

## Deuda que este plan hereda

`tools/contexto.py` **no está en el perfil de mutación**, y por eso su `return []` silencioso vivió
sin que nada lo señalara. Custodia la afirmación «esto es lo que hay en tu proyecto», sobre la que un
agente construye todo lo demás. Entra en `HERRAMIENTAS_CUSTODIAS` o se explica por qué no.
