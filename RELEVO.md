# Relevo — 2026-09-07

## Para Claude: empezar acá

**Corte 0.8.1 hecho, commiteado y empujado, con autorización explícita del usuario.** El árbol
declara distribución `0.8.1`, álgebra `0.6` y sintaxis `0.2`; el argumento está en
`ESPECIFICACION.md` §0 y las notas en `NOTAS-DE-RELEASE.md`.

Los tres trabajos que estaban sin commitear —el corte 0.8.0, el experimento del sensor y el
recorrido reusable— entraron en **un solo commit** sobre `f57b67f`, y conviene saber por qué: los
archivos compartidos (`nucleo/version.py`, `ESPECIFICACION.md` §0, `NOTAS-DE-RELEASE.md`,
`README.md`, la matriz de CI y `tools/mutar_codigo.py`) mezclan las tres tandas **en los mismos
hunks**. Partirlo en tres habría exigido inventar contenidos intermedios que nunca existieron, y
dos de esos commits no habrían pasado su propia suite. El mensaje del commit enumera las tres
tandas y el `git status` de cada una está descrito abajo.

**Lo que NO se hizo:** subir a PyPI. Los artefactos están construidos y verificados en `dist/`
(0.8.1) y el comando queda listo abajo; **lo ejecuta el usuario**.

### Orden de lectura

1. `NOTAS-DE-RELEASE.md` — qué entra en 0.8.1 y qué NO empieza a demostrar.
2. `estudios/OBSERVAR-0.8.1-RECORRIDO.md` — la herramienta, qué se le encontró al experimento
   anterior, y el defecto que encontró un ataque y la mutación no.
3. `tools/observar.py` — el docstring describe el formato del plan; es la referencia.
4. `PLAN-0.8.1-SENSOR.md` — las tres decisiones y cómo quedaron respondidas.

### Qué es 0.8.1

`tools/observar.py`, con dos verbos: `capturar` y `revalidar`. Ejecuta el sensor **del consumidor**
como otro proceso, conserva su salida **byte a byte**, se niega ante una lectura vacía o inestable y
ante un referente que cambia durante la corrida, y compara el resultado contra la expectativa
**declarada en el plan antes de correr**. La polaridad la dictamina `meta.el_caso_se_pone_como_debe`,
no un `if` de la herramienta. **No agrega nada al lenguaje.**

### Lo que NO demuestra, y hay que seguir diciendo

**La autenticidad no se comprueba, y ninguna huella la comprueba.** Medido con ataques reales: un
«sensor» que no lee nada, uno que le agrega filas inventadas a una lectura real, y un `cp` de un
JSON escrito a mano **pasan los tres**, y salen con `autenticidad.comprobada: false`. De un caso
`observada` NO se puede deducir que alguien midió el mundo; se puede deducir que un programa corrió,
que su salida se conservó sin tocar y que no cambió entre dos lecturas seguidas.

**El defecto que encontró el ataque, y la lección que dejó.** El control de estabilidad comparaba
las dos lecturas ya parseadas con el `==` de Python, donde `True == 1`. Un sensor que emitía `true`
y después `1` pasaba —bytes y tipos distintos— y el caso salía como observación de algo no
reproducible. Los **146 mutantes del archivo estaban muertos** mientras el defecto seguía ahí: la
mutación pregunta «¿algún test nota si cambio esta línea?», y esto vivía en el *significado* de `==`
sobre datos parseados. **Cero sobrevivientes no es cero defectos.** Lo encontró `codex` atacando;
`agy`, leyendo el mismo archivo con cuatro preguntas dirigidas, no lo encontró.

### Números del corte

| | |
|---|---|
| suite | **1353 tests**, verde |
| corpus | **184 casos** |
| aceptación | 1 medida meta roja, línea literal de CI intacta |
| mutación de medidas | **902/902** |
| mutación de `tools/observar.py` | **146 · 146 muertos · 0 sobrevivientes · 0 equivalentes declarados**, medido después del arreglo |
| `trazar.py` · `sondear_generador.py` · `cifras.py` | verdes y vigentes |
| `verificar_instalacion.py` | WHEEL OK, 10 entry points |
| Jam | 23 casos, sombras 9 / 54 / 41 — sin cambios |
| LyraGASP | 28 casos, 14 rojos y 14 verdes, sombras 8 / 16 / 9 |

### Lo que queda pendiente

- **Subir a PyPI.** `dist/` tiene el wheel y el sdist de 0.8.1 verificados contra el árbol. El
  comando está al final de este relevo. **No se ejecutó.**
- **Crear la release de GitHub** `v0.8.1`, como se hizo con 0.5.0 y 0.6.0.
- **LyraGASP sigue sin commitear.** Sus agregados nuestros son de dos turnos y su árbol tiene 45
  renglones de trabajo ajeno. **No se commiteó nada ahí**; hace falta decisión del usuario sobre qué
  entra. Jam no se tocó en ningún turno.
- **Nada autentica una corrida.** Sigue sin haber forma de distinguirla de una transcripción.
- **No se abrió el editor.** Los sensores que necesitan Unreal siguen sin correrse, los 37 ground
  truth siguen ausentes, y las sombras de unidades y origen de umbrales no se mueven por esto.

### Cómo subir a PyPI

```bash
cd /home/workstation/Dev/oracle
python3 -m twine check dist/oracle_metalenguaje-0.8.1*
python3 -m twine upload dist/oracle_metalenguaje-0.8.1*
```

Sube **sólo** los dos archivos de 0.8.1: `dist/` conserva artefactos de cortes anteriores y un
`upload dist/*` intentaría resubirlos.

### Comprobaciones para retomar

```bash
python3 -B -m unittest discover -s tests -q
python3 tools/corpus.py --proyecto . --resumen
python3 tools/aceptacion.py --proyecto .
python3 tools/aceptacion.py --proyecto /home/workstation/Dev/jam/medidas --confiar-escalares
python3 tools/aceptacion.py --proyecto /home/workstation/Dev/games/unreal/LyraGASP/medidas --confiar-escalares
python3 tools/mutar_codigo.py --objetivo tools/observar.py
```

Esperados: Oracle 184 casos y **1** medida meta roja; Jam 23 y Lyra 28, los dos en **0** conservando
tres sombras cada uno. CI exige exactamente:

```text
la_medida_no_se_fija_solo_con_evidencia_fabricada        2 (<= 0)
```

⚠ **Una ronda de mutación tarda ~40 minutos y toma un bloqueo sobre la raíz.** No edites el árbol
mientras corre. Y ojo con `pgrep -f <patrón>`: **se matchea a sí mismo**, y con el truco de los
corchetes igual matchea si tu propia línea de comandos menciona el archivo sin corchetes. Pasó dos
veces en este turno: una ronda leyó una copia anterior de los tests y reportó un sobreviviente que
ya estaba muerto, y otra vez creí que había una ronda viva cuando no la había.

### Sobre LyraGASP y su Oracle

⚠ **NO consume Oracle por subtree.** No existe `vendor/` en ese repositorio. Según su propio
`docs/ORACLE.md`, usa un venv de `uv` con **`oracle-metalenguaje==0.3.3` desde PyPI**, fijado con
`==` a propósito. El `CLAUDE.md` de la máquina dice «subtree en `vendor/oracle`» y **está
desactualizado para este consumidor** (Jam sí usa subtree).

La consecuencia: hasta que 0.8.1 esté en PyPI **y** alguien suba ese pin, el recorrido no corre
desde el Oracle instalado de Lyra. Se corre desde el árbol de trabajo, apuntando con rutas:

```bash
cd /home/workstation/Dev/oracle
python3 tools/observar.py revalidar \
  --plan     <LyraGASP>/medidas/observaciones/dataset-ml-deformer.plan.json \
  --registro <LyraGASP>/medidas/observaciones/2026-09-07-dataset/registro.json
```

Lo agregado en LyraGASP, sin commitear: el plan y la carpeta `2026-09-07-dataset/` (este turno), el
caso `018-…json` (este turno), y del turno anterior el caso `017-…json` y
`medidas/observaciones/2026-09-06-dataset/`. Se comprobó contra el `arbol` que guarda el registro
del turno anterior: desde entonces sólo aparecieron esos dos casos y esa carpeta, y no desapareció
nada.

### Límites y autorizaciones

- El servidor MCP **no se modificó**; sólo las expectativas de versión de sus tests, como en 0.7.0.
- La autorización ejecutada fue: commit y push de Oracle. **PyPI lo sube el usuario.**
- No desactivar sombras ni reclasificar evidencia vieja para mejorar cifras. No se hizo.
- Si aparece un equivalente real, retirar el constructo, no declararlo. Se retiraron tres.
- `ask-agy` es el wrapper de Gemini, no `ask-gemini`. `ask-opencode` sólo con Go
  (`OPENCODE_MODEL=opencode-go/...`); su predeterminado es OpenRouter.
- **`ask-codex` con un encargo adversario fue lo más rentable de este turno.** Encontró el único
  defecto real; la lectura conceptual de `agy` no encontró nada. Si algo tiene una promesa cara,
  conviene pedir que la ataquen antes que pedir que la lean.

## Avance actual: primer recorrido real del plan del sensor

El usuario pidió seguir con `PLAN-0.8.1-SENSOR.md`. Se ejecutó el sensor existente de dataset de
LyraGASP sobre archivos reales, sin abrir Unreal: 37 clips declarados, 37 FBX presentes y 0 ground
truth. La medida correspondiente dio rojo 37. Con autorización se agregaron cinco archivos nuevos
al consumidor: el caso observado 017 y `medidas/observaciones/2026-09-06-dataset/` con evidencia,
registro, registrador del experimento y README. No se tocaron sus archivos existentes ni assets.
La corrida fue el 2026-09-07 00:42:45 UTC; la carpeta usa el día local de Salta, 2026-09-06.

Lyra pasa corpus y aceptación con 27 casos, 13 rojos esperados y 14 verdes. Sus pendientes de
evidencia observada bajan de 9 a 8, sin quitar ninguna sombra. Jam mantiene 23 casos y sus sombras
9/54/41. Oracle mantiene 184 y la línea literal de los dos pendientes declarados. Pasan los cuatro
tests del sensor/adaptador y 9/9 mutantes de la medida de ground truth, por conducta; el caso nuevo
detecta seis y no sustituye los bordes sintéticos. No se repitió la suite completa de Oracle en
este avance: su código no cambió y la última medición sigue siendo la del corte de abajo.

La evidencia del caso coincide exactamente con el JSON emitido. Se comprobaron sus huellas y seis
referentes estables. Un control construido confirma el límite: huellas distintas dan rojo 1, dos
declaraciones falsas iguales dan verde 0. L−2 compara declaraciones, no autentica una corrida.
El sensor sólo consultó presencia de FBX/ABC; no leyó ni certificó sus contenidos.

Detalle y siguientes pasos en `estudios/SENSOR-0.8.1-PRIMERA-CORRIDA.md`. El registrador conservado
es un experimento local, no una herramienta general con su código fijado. Queda propuesto un camino
reutilizable de captura/revalidación del consumidor. No se inició la parte que requiere el editor,
no se arreglaron los ground truth y no se hizo corte, commit, push o publicación. Las versiones
siguen en 0.8.0 / 0.6 / 0.2 y el servidor MCP sigue intacto.

## Estado del corte anterior: 0.7.0 en commit, corte local 0.8.0 verificado

El usuario autorizó el commit del corte: `f57b67f`, «Corte 0.7.0: canal de reporte verificado y
documentado». No se hizo push ni se publicó. El corte de 0.8.0 queda sin commitear:
`nucleo/generador.py` comprueba la polaridad, amplifica conteos simples según su umbral y explica
la negativa cuando la propuesta no sirve, sin escribir archivos. Distribución subió a 0.8.0;
álgebra 0.6 y sintaxis 0.2 se conservan con argumento en §0: cambia la fórmula distribuida de una
medida, no la interpretación de una misma fórmula. Las notas explican el cambio de conteos a días.

El estado detallado y el inventario revisado están en `estudios/UMBRAL-0.8.0-REVISION.md`.
El generador tiene 22 pruebas; los 22 sitios de mutación de los controles nuevos quedaron muertos.
Esto no afirma que el generador histórico entero esté fijado.

La medida de edad de las sombras usa ahora `peor` con tolerancia 90 días: conserva identidad,
polaridad y testigos, pero informa la edad máxima incumplida, no el conteo. Sin incumplimientos,
informa cero. Tiene seis casos y cierra 9/9 mutantes. `tools/sondear_generador.py` ejecuta cinco
sondas, publica 17 comprobaciones y las juzga con `meta.el_caso_se_pone_como_debe`. Corre en CI,
tiene 11 tests y su mutación completa cierra 27/27, sin sobrevivientes ni equivalentes declarados.
Los casos 479–482 custodian ambos recorridos; el 482 registra la ejecución del programa sobre
entradas construidas, no una observación de un dominio externo.

Verificación final: **1295 tests OK, corpus 184, mutación de medidas 902/902** (750 por conducta,
152 rechazos del álgebra). Aceptación conserva los dos pendientes declarados y la línea literal de
CI intacta; Jam y LyraGASP pasan con 23 y 26 casos y tres sombras cada uno. Cifras y manual regenerados.

Se retiraron constructos equivalentes de la nueva sonda. También se eliminó el valor por defecto
imposible de las coordenadas de `ErrorSintaxis` en `tools/medida.py` y su declaración histórica en
`equivalentes.json`; los tres sitios afectados cierran 3/3 en mutación dirigida. No se midió otra
vez todo ese archivo. La plantilla ahora orienta hacia `peor` cuando el dominio es una magnitud.

El corte repitió suite, corpus, aceptaciones y mutaciones de medidas y sonda con los números
anteriores. Wheel y sdist en `dist/`, 0.8.0; sus 121 archivos de código y datos coinciden con el
árbol. Instalación limpia en `/tmp/oracle-080-instalacion-0T6lTR/venv`: versión, ayuda de reportar,
sonda empaquetada y medida de sombras comprobadas. `tools/verificar_instalacion.py` pasa también
los diez ejecutables, datos y motores aislados. Persisten los avisos de setuptools sobre directorios
de datos, pero el contenido fue verificado. No se tocó el servidor MCP.

Gemini (`ask-agy`) dio una segunda lectura conceptual de versiones y compatibilidad; no es una
verificación de código. OpenCode Go leyó los archivos pero agotó cuatro minutos sin informe; no
se cuenta como aprobación. Detalle en la revisión. El inventario de once sitios está triado;
permanecen declarados el límite de monotonía de `max`/`min`, el contrato de agregados vacíos y la
falta de fabricación general de magnitudes. No son capacidades implementadas.

Queda la autorización de commit/publicación que corresponda. El plan del sensor se inició después
de este corte; su avance y sus límites están en el encabezado de este relevo.

## Actualización: corte local 0.7.0

El corte solicitado quedó en `f57b67f`, sin push ni publicación. Distribución
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
