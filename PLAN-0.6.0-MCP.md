# Plan 0.6.0 — una herramienta MCP para escribir medidas

**Fecha:** 2026-09-04 · **Estado:** propuesta, sin empezar

## Lo que NO hay que construir

Una herramienta por verbo del CLI. Hoy son 22 verbos repartidos en 5 sustantivos, y envolverlos uno
a uno no le da a un agente nada que no tenga: ya puede correr `oracle medida nueva` por consola. Lo
único que agregaría es superficie —22 descripciones que competir en el contexto— a cambio de cero
capacidad nueva.

El transporte tampoco es el problema. `tools/lsp.py` ya escribe JSON-RPC a mano sobre stdio con
enmarcado `Content-Length`, sin una sola dependencia. Copiar ese patrón es trabajo conocido.

## Lo que sí falta, y sale de esta sesión

Un agente que escribe una medida produce algo **plausible**. El modo de falla no es el error de
sintaxis —eso el cargador ya lo rechaza— sino la medida que carga, corre, da verde y no mide nada.
Tres ejemplos medidos, todos de hoy:

- La alarma del umbral se escribió con una premisa **globalmente falsa**; parecía correcta y puso en
  rojo a un consumidor sin remedio.
- Al arreglarla, la premisa pasó a ser verdadera **por construcción**: la medida ya no podía dar
  rojo por ningún motivo legítimo. Una medida que no puede fallar no mide.
- Tres guardas que escribí yo —una constante que un filtro volvía irrelevante, una comparación cuyo
  caso cero era un no-op, una rama inalcanzable— pasaron todos los tests y las cazó la mutación.

El patrón es siempre el mismo: **pasa las comprobaciones que corriste, no las que importan**. Un
agente no corre la mutación porque tarda, y sin mutación una medida verde no dice nada.

## La forma propuesta: tres herramientas, no veintidós

### `oracle_contexto`

Qué mide este proyecto, en la forma compacta que ya existe (`tools/contexto.py`, ~1.600 tokens
contra ~8.600 de los tres comandos que reemplaza). Es lo primero que un agente necesita y hoy tiene
que reconstruirlo leyendo archivos.

Con el ámbito de 0.5.0 esta respuesta por fin es **correcta**: enumera las medidas que obligan a
ESTE proyecto, no todo lo que viaja en el paquete.

### `oracle_probar`

Evalúa una medida **en borrador** contra evidencia dada, sin escribir nada en el repositorio.
Devuelve veredicto, valor y testigos.

Es el lazo que hoy no existe: escribir, probar, corregir. Sin él un agente tiene que crear el
archivo para poder probarlo, y entonces el repositorio se llena de intentos.

### `oracle_proponer` — acá está la política

Guarda una medida **sólo si viene con evidencia que la pone en rojo y evidencia que la pone en
verde**.

No es «exigir que exista un caso»: es exigir que la medida **discrimine**. Una medida que no puede
dar rojo no mide nada, y es un defecto que ya nos pasó hoy, no una hipótesis. El agente tiene que
mostrar las dos polaridades antes de que el archivo exista.

Lo que esto fuerza, y es el punto: **describir el defecto antes de escribir la regla que lo caza**.
Es el orden que el proyecto ya practica en el corpus y que nada obligaba.

## Lo que hay que decidir antes de escribir código

1. **¿La compuerta es demasiado estricta?** Bloquea el trabajo exploratorio: a veces se escribe una
   medida para ver qué encuentra. Alternativa: `oracle_proponer` guarda igual pero marca la medida
   como no fijada, y una medida meta la reclama. Más blando, y el proyecto ya tiene el mecanismo
   —es lo que hace `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada`—.

2. **¿El MCP escribe o sólo lee?** Un servidor de sólo lectura —contexto y probar— es mucho más
   chico, no puede romper nada y ya captura la mayor parte del valor. Escribir es lo que trae la
   política, pero también el riesgo.

3. **¿Cómo se verifica el propio servidor?** La vara del proyecto es corpus y mutación. Un servidor
   MCP es código de herramienta: entra en `HERRAMIENTAS_CUSTODIAS` sólo si custodia una afirmación
   que nadie más comprueba. Hay que decidir cuál es esa afirmación antes de escribirlo.

## Lo que no promete

Nada de esto impide que un agente escriba una medida mala. Una medida puede discriminar entre dos
evidencias fabricadas para ella y seguir sin decir nada del mundo — es exactamente lo que
`procedencia: observada` existe para distinguir, y ninguna herramienta puede comprobar que alguien
haya mirado de verdad.
