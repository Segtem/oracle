# Canal de reporte para 0.7.0

**Fecha:** 2026-09-05  
**Estado:** diseño decidido; sin implementación

## Decisión

El reporte se prepara localmente y **va a un issue público de `Segtem/oracle`, publicado a mano por
quien reporta**. El issue es la bandeja de entrada; el corpus sigue siendo el único lugar donde el
hallazgo se vuelve evidencia del proyecto. Por eso un reporte **aspira a ser un caso, pero todavía
no lo es**.

Oracle no envía el reporte, no abre el issue mediante una API y no recibe credenciales. Hace lo que
ya hace `oracle diagnostico`: produce un artefacto local, muestra todo lo que propone compartir y
deja la decisión de publicarlo en la persona. La transferencia al issue es copiar y pegar ese
artefacto desde el navegador. Ese acto conserva un borde que ya existe y ya tiene una razón: producir
información no autoriza a publicarla.

La validez semántica para entrar al corpus la decide una persona responsable del repositorio, después
de que las herramientas hayan decidido todo lo que sí pueden decidir mecánicamente. Un modelo puede
ayudar a ordenar o a redactar; no puede rechazar el reporte ni promoverlo al corpus.

Abrir el issue registra que alguien encontró un límite. No promete diagnóstico, prioridad, fecha ni
arreglo.

## Por qué hace falta abrir la entrada

La contribución que hoy queda detrás del permiso de commit no es hipotética. Se verificó el corpus
actual con:

```console
$ python tools/corpus.py --resumen
CORPUS OK · 180 casos · esquema, evidencia L0 y trazabilidad en regla

casos: 180

por cómo se detectó:
  79  observacion
  73  mutacion
  20  persona
   4  herramienta_ajena
   4  accidente
```

Con la partición del plan, los hallazgos de `persona`, `herramienta_ajena` y `accidente` suman
`20 + 4 + 4 = 28`; `observacion` y `mutacion` suman `79 + 73 = 152`. Los 28 son el 15,6 % de los
180 casos, redondeado a una decimal. Ésa es la clase de aporte que el canal externo tiene que dejar
entrar sin conceder acceso de escritura al repositorio.

## 1. El destino es un issue manual, no un buzón nuevo

El issue público resuelve la parte que un archivo local no puede resolver: llega al lugar donde se
mantiene Oracle, tiene una URL que se puede referenciar y permite que otra persona agregue una
reproducción o convierta el hallazgo en un caso. No se adopta, sin embargo, el issue de prosa libre
que criticaba el plan. El cuerpo que Oracle prepara conserva estructura y separa como mínimo:

- qué se esperaba;
- qué ocurrió;
- cómo se detectó;
- el diagnóstico reproducible que sea seguro publicar;
- y, cuando existan, la medida, el veredicto y la evidencia candidata.

Así el issue transporta una candidatura estructurada; no reemplaza al corpus ni se convierte en una
segunda base de verdad. Que un issue envejezca no degrada silenciosamente una medida, porque sólo los
casos promovidos fijan el catálogo y participan de sus conteos.

La preparación local debe tener el mismo contrato operativo de `oracle diagnostico`: salida por
pantalla o a una ruta elegida explícitamente, lectura completa antes de compartir y ninguna red. El
archivo local, si la persona decide guardarlo, es sólo una escala. No es el destino y Oracle no debe
confundir «escrito» con «reportado».

Esta elección pierde cosas reales:

- Frente a declarar como destino un archivo en el repositorio del usuario, pierde un canal privado
  que viajaría junto al código y conservaría todo su contexto. Se acepta la pérdida porque ese
  archivo no notifica a Oracle y conserva exactamente la barrera actual: sólo llega si alguien con
  acceso lo traslada. El archivo local de esta decisión es una vista previa, no otro destino.
- Frente a crear el issue automáticamente, pierde un envío de un paso y algunos reportes quedarán
  preparados pero nunca publicados. A cambio, la CLI no administra tokens, no actúa bajo la identidad
  del usuario y no salta la revisión que protege datos del dominio. Las credenciales quedan en el
  navegador y en GitHub, donde ya pertenecen.
- Frente a un punto de recepción propio, pierde una cola privada, ingestión uniforme y automatización bajo
  control de Oracle. A cambio, no crea un servidor, retención, borrado, control de abuso ni una nueva
  responsabilidad sobre datos ajenos. Ese costo estructural ya fue la razón para detener la
  telemetría después de su fase local en
  [`DECISION-007`](../DECISION-007-BIBLIOTECAS-DE-POLITICAS.md).

El issue manual tampoco permite reportar en secreto. Ésa es una limitación deliberada de 0.7.0, no
una propiedad que convenga esconder. Si un hallazgo no puede hacerse público aun después de reducirlo
y anonimizarlo, este canal no puede recibirlo; resolver reportes privados requeriría precisamente la
política de datos que esta decisión evita.

## 2. El diagnóstico se reutiliza; su garantía no se estira hasta la evidencia

El reporte lleva por omisión sólo dos clases de contenido. La primera es la explicación que la
persona escribió para publicar: expectativa, resultado y forma de detección. La segunda es el
diagnóstico generado con la lista positiva que ya usa `oracle diagnostico`: versiones, plataforma,
forma del proyecto, bibliotecas seleccionadas y perfiles, sin contenido del dominio.

La evidencia, los ids de medidas propias, los nombres de archivo y cualquier fragmento adicional son
**optativos y de inclusión explícita**. Oracle no debe recorrer el proyecto y adjuntarlos por
conveniencia. Si la persona los agrega, forman parte de la vista previa completa y las rutas conocidas
se reemplazan por `<PROYECTO>` y `<HOME>` antes de mostrarla. La publicación sigue siendo manual.

`meta.el_diagnostico_no_publica_el_dominio` sirve sin cambios para el subdocumento de diagnóstico. Su
sensor recorre los textos generados y los compara con la lista que hoy le entrega la aceptación:
raíz, home e ids del catálogo. Además, el diagnóstico se construye desde una lista cerrada de campos;
esa combinación hace falsable su contrato. Los nombres de archivo que no coincidan con esos ids ya
muestran por qué esa garantía no se puede generalizar.

No alcanza para certificar el reporte entero. La prosa «el cliente ACME quedó sin saldo» puede ser
sensible sin coincidir con ninguna ruta ni id conocido. Una credencial secreta, un identificador del negocio o un
valor de una fila puede ser secreto sin que Oracle sepa que lo es. Extender el mismo buscador y llamar
«seguro» al resultado produciría un falso verde especialmente grave: probaría sólo que no apareció
ninguna aguja conocida.

Por eso hay tres defensas distintas y ninguna suplanta a las otras: lista positiva para el diagnóstico
automático, exclusión por omisión de evidencia y contenido del proyecto, y revisión humana de la
salida completa antes del acto de publicar. Una futura medida del reporte podría vigilar las dos
primeras propiedades estructurales; no podría afirmar que la prosa libre carece de secretos. Ese
límite debe quedar en su `alcance`, no disimulado con heurísticas.

## 3. El reporte aspira a ser un caso

No se agrega `limite_reportado` a las etiquetas del corpus. Una etiqueta de caso expresa la relación
entre un veredicto y lo que debía ocurrir; «reportado» expresa el estado de una entrada. Mezclar
polaridad con ciclo de vida permitiría contar como evidencia algo que nadie reprodujo.

El borde actual ya distingue mejor de lo que supone el plan. Un caso puede declarar `medida: null`
si además declara `estado_sin_medida: abierto` y explica `sin_medida_todavia`.
`meta.el_caso_reclama_una_medida_que_existe` tampoco exige que todo caso tenga medida: filtra sólo
los hechos con `tiene_medida == true` y `medida_existe == false`. Un hueco explícito no reclama un id
y por eso no pone esa medida meta en rojo. Si el reporte inventara un id inexistente, sí la pondría
en rojo; la representación correcta de una capacidad ausente es el nulo explicado, no un nombre
plausible.

Lo que no se puede omitir es la evidencia. Para comprobar el borde se creó fuera del repositorio un
proyecto temporal con un caso completo salvo por `medida: null` y `evidencia: {}`. El caso declaraba
el estado `abierto` y explicaba por qué todavía no había medida. La corrida real fue:

```console
$ python tools/corpus.py --proyecto "$tmp_reporte"
CORPUS: 1 problema(s)
  · 999-limite-reportado.json: `evidencia` tiene que ser un mapa de relación → filas, y no estar vacío
```

Por lo tanto una frase como «el lenguaje no me dejó expresar esto» no es un caso hoy, aunque sea un
reporte legítimo. Forzarla a entrar exigiría fabricar evidencia o aflojar el contrato L0 para todo el
corpus. Ninguna de las dos cosas mejora el hallazgo.

La promoción ocurre recién cuando alguien puede escribir un caso con la forma vigente: síntoma,
etiqueta que fija el veredicto esperado, forma de detección, evidencia L0 no vacía y una medida
existente o un hueco abierto explicado. Entonces `tools/corpus.py` valida la forma y la aceptación
aplica las medidas meta. El issue queda como procedencia y conversación; el `.caso` es la evidencia
duradera. Un reporte que nunca alcance ese umbral puede seguir siendo información útil en el issue,
pero no altera el catálogo, sus porcentajes ni su estado de fijación.

## 4. La máquina admite; una persona promueve

«Reporte válido» tiene dos bordes que no conviene colapsar. Para llegar al issue basta que la persona
decida publicar la observación estructurada. No se exige que Oracle ya esté de acuerdo: ése sería el
juicio que el reporte viene a pedir. El ruido de esa bandeja no entra por arrastre al corpus.

Para llegar al corpus, las herramientas rechazan todo lo mecánicamente decidible: sintaxis, campos,
evidencia L0, ids inventados, huecos sin explicar y desacuerdo entre etiqueta y evaluación. Después
queda una pregunta que el arnés no puede contestar: si lo esperado por el caso era verdad en el
dominio. Esa decisión la toma una persona responsable al aceptar la incorporación al repositorio.

El trabajo humano no desaparece; se concentra en el único juicio que no puede automatizarse. La
escala viene de permitir que quien reporta u otra persona haga la reproducción y proponga el caso,
mientras la integración continua repite las comprobaciones mecánicas. No hace falta filtrar manualmente cada observación
antes de recibirla, y tampoco se rebaja el corpus para que recibir sea barato. Si nadie completa la
reproducción o nadie puede sostener la verdad esperada, el reporte no se promueve. Eso no lo vuelve
falso ni crea una deuda prometida: sólo dice que todavía no es evidencia del corpus.

Usar un modelo como juez semántico sería circular. Muchos reportes van a señalar precisamente una
medida o una formulación producida por un modelo; pedirle a otro modelo que decida si el reclamo
merece existir es pedirle al generador que juzgue lo que se le reporta. También sesgaría la entrada a
favor de los problemas que el vocabulario actual ya sabe reconocer, que son justamente los que menos
necesitan el canal. Un modelo sí puede resumir, señalar campos faltantes, proponer una anonimización,
agrupar posibles duplicados o bosquejar un `.caso`; cada resultado queda como sugerencia visible. No
puede cerrar por inválido, ocultar, fijar prioridad ni promover al corpus.

## El servidor MCP no participa

0.7.0 no agrega una herramienta MCP de reporte ni hace que una herramienta existente escriba un
archivo, abra un issue o envíe datos. El servidor de 0.6.0 sigue siendo de sólo lectura por diseño.
Aunque MCP podría capturar más contexto y evitar la transcripción, hacerlo escribir o transmitir
rompería ese contrato y reabriría la compuerta de escritura que se descartó para conservarlo.

Si más adelante se quiere reportar por MCP, hace falta una decisión separada que cambie explícitamente
el contrato de autoridad, describa el consentimiento y vuelva a evaluar la superficie de datos. No
es un parámetro nuevo de esta decisión.

## Consecuencia

El camino queda único y legible: Oracle prepara localmente; la persona revisa y publica un issue; las
herramientas determinan si existe una candidatura de caso bien formada; una persona decide la verdad
que la máquina no conoce; el corpus, y sólo el corpus, conserva lo que quedó demostrado. En ninguno
de esos pasos «recibido» significa «lo vamos a arreglar».
