# Relevo — 2026-09-06

## Actualización: corte local 0.7.0

El corte solicitado está preparado en el árbol, sin commit, push ni publicación. Distribución
`0.7.0`; álgebra `0.6` y sintaxis `0.2` conservadas por la regla de §0: el canal agrega una
herramienta, ningún nodo ni forma del lenguaje. El servidor MCP no se modificó; sólo se
actualizaron las expectativas de versión de sus tests.

Verificación independiente: 1266 tests OK, corpus 180, aceptación con la única medida meta roja
en valor 2 y la línea literal de CI intacta; mutación de `tools/reportar.py`, 19/19 sin
sobrevivientes, tiempos agotados, errores de arnés ni equivalentes declarados. Jam y LyraGASP
pasan con 23 y 26 casos, respectivamente, conservando tres sombras cada uno. La suite y la
mutación requieren permiso para el test que crea un temporal bajo `Path.home()`.

Se corrigió la identidad visual de `docs/reportar.html` y el contraste de los enlaces del pie
bajo el cursor: de 2,57:1 a un mínimo de página de 6,65:1. Se comprobaron 62 elementos con texto,
escritorio y teléfono, en reposo y bajo el cursor. La plantilla coincide con el reporte y el
impresor de `.caso`. README y manual HTML regenerados.

Wheel y sdist locales en `dist/`, versión 0.7.0; instalación limpia y ambos comandos pedidos OK.
El venv de prueba está en `/tmp/oracle-070-instalacion-7IeSN1/venv`. Las notas de release registran
los números y dos advertencias que no se ocultaron: una medida de mutación de medidas no juzga
la evidencia de mutación de código por falta de `detecciones_conductuales`, y setuptools advierte
sobre directorios de datos aunque se verificó que los 117 archivos se empaquetan íntegros.

El texto que sigue es el estado anterior al corte, conservado como contexto histórico.

---

Estado al cortar por falta de crédito. Escrito para que quien siga —persona o agente— no tenga que
reconstruir nada leyendo commits.

## Dónde está todo, ahora mismo

| | |
|---|---|
| **PyPI** | `0.6.0` publicada y verificada bit a bit contra el build local |
| **GitHub** | `main` en `8adfe74` · Releases `v0.5.0` y `v0.6.0` creadas · 0.6.0 es Latest |
| **El sitio** | `segtem.github.io/oracle` con inicio, **dónde entra**, **de cero** y el manual |
| **La versión en el repo** | **0.6.0**, y se queda ahí. Sube en el corte, no al empezar |
| **La suite** | 1266 tests, verde |

## Qué se está haciendo justo ahora

**codex está cerrando 0.7.0**, despachado con orden de trabajar solo hasta terminar. Su orden está
en el scratchpad de la sesión; lo que le pedí, en orden:

1. la plantilla de issue en `.github/ISSUE_TEMPLATE/` — **la mitad faltante del canal**;
2. documentar el canal en el README y en el sitio;
3. escribir el camino de promoción de issue a `.caso`;
4. las notas de release de 0.7.0.

Con tres reglas duras: **no subir la versión**, **no commitear ni pushear**, **no tocar el servidor
MCP**. Cuando termine, hay que leer su informe y verificar por cuenta propia antes de commitear —
las dos veces anteriores subió la versión por su cuenta y hubo que revertirla junto con los tests.

## 0.7.0 — el canal de reporte

**Hecho:** las cuatro decisiones (`estudios/CANAL-DE-REPORTE.md`), y `oracle reportar`, que mide
**19/19 sin sobrevivientes**.

La propiedad que custodia, comprobada corriéndola: **sin pedirlo explícitamente no sale un solo dato
del dominio**. La medida y la evidencia entran sólo con `--incluir-medida` o `--incluir-evidencia`.

**Falta:** lo que está haciendo codex.

## 0.8.0 — el umbral > 0 y el generador · `PLAN-0.8.0-UMBRAL.md`

Decidido, sin empezar. El catálogo base es **55 de 55 en `umbral <= 0`**: Oracle nunca ejerce el otro
camino de su propio lenguaje. No es teórico — por eso vivió meses la exclusión global de mutadores.
Y la misma ceguera está en `nucleo/generador.py`, que fabrica un `falso_verde` con una sola fila
asumiendo que rompe cualquier umbral.

**Lo que el plan prohíbe:** escribir una medida con umbral > 0 sólo para tener una. Si no aparece
una candidata legítima, el hallazgo es ése.

## 0.8.1 — que la evidencia venga del mundo · `PLAN-0.8.1-SENSOR.md`

Anotado. Hoy todo lo que Oracle demuestra es coherencia interna. El número es provisorio: si agrega
algo al lenguaje sube la menor por §0.

## Deudas vivas, que no están en ningún plan de versión

- **El ámbito `del_origen` de `meta.toda_medida_declara_su_ambito` es temporal** y nada registra
  cuándo debe volverse universal. Está anotado en `PLAN-0.5.0-AMBITO.md`. El precedente de que esto
  se olvida: `segun` lleva meses con 41 umbrales en sombra en un consumidor.
- **Jam tiene tres medidas universales en sombra.** No es deuda de Jam: son tres medidas de Oracle
  demasiado exigentes para el estado real de un consumidor.
- **LyraGASP tiene una medida que no puede juzgar** (`proceso.codigo_con_mutante_que_lo_mata` espera
  un campo `m.estado` que su evidencia no trae). Verificado contra 0.4.0: es previa, no la trajimos.

## Lo que aprendí en esta sesión y conviene no volver a aprender

**No editar el árbol mientras corre una ronda de mutación.** Lo hice cuatro veces. El arnés se
defiende —se niega a entregar un número— pero la corrida se pierde.

**`pgrep -f <patrón>` se matchea a sí mismo.** Un bucle de espera con el patrón adentro nunca
termina; me costó hora y media. El truco es `mutar_codigo[.]py`: los corchetes hacen que la línea de
comandos del propio bucle no coincida con su regex.

**Verificar lo que ya estabas mirando no es verificar.** El diagrama de `donde-entra.html` se
corrigió cuatro veces: el `<dt>` y no el `<h2>`; `color` y no `fill` —en SVG el texto sin `fill` es
negro, no toma `color`—; y coordenadas a ojo. Recién se cerró cuando el chequeo dejó de ser mirar y
pasó a ser un script que recorre las cajas y falla si un trazo atraviesa una.

**Un test que ejecuta una rama no es un test que la fija.** Dos veces escribí la entrada que corre
el código en vez de la que lo distingue de su mutante. El caso más claro: un acumulador cuyo valor
inicial sólo importa si el contenido ARRANCA con la corrida.

**Un equivalente genuino se borra, no se declara.** Pasó dos veces —`split(maxsplit)` bajo un `[0]`,
y un acumulador bajo un piso `max(3, ...)`—. Anotar un equivalente es aceptar para siempre un
mutante que nadie puede matar; sacar el constructo lo elimina.

## Sobre los agentes

- **agy** entregó todo lo que se le dio y respetó todos los frenos: paró cuando le dije que parara,
  no reclasificó cuando le dije que no, no inventó un caso observado.
- **codex** es fuerte en lo mecánico y paró dos veces ante un defecto real en vez de tocar
  producción, que es exactamente lo que se le pidió. Su falla repetida es subir la versión por su
  cuenta.
- **opencode falló 3 de 3** en tareas reales, incluida una completamente especificada. Sólo funcionó
  con un encargo de juguete. No usarlo para nada del proyecto.
