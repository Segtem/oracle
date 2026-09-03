# El ámbito de las medidas

## La pregunta no es dónde está el archivo

Hoy «universal» reúne dos afirmaciones distintas: que una medida **viaja** en el paquete y que esa
medida **obliga** a cualquier proyecto que active el catálogo base. La primera es procedencia; la
segunda es ámbito. Que ambas hayan coincidido hasta ahora explica el mecanismo actual, pero no lo
justifica.

La diferencia aparece cuando el rojo tiene dueño. `meta.toda_medida_filtra_o_agrupa` consume la
forma de las medidas del catálogo que se está evaluando. Si encuentra una infracción en una medida
de Jam, Jam puede cambiar esa medida. En cambio,
`meta.ninguna_exclusion_de_mutador_se_apoya_en_una_premisa_falsa` consume una decisión del arnés de
Oracle: la exclusión vive en `nucleo/mutacion.py`. Aunque el hecho se calcule contra el catálogo del
consumidor, el consumidor no puede reparar la exclusión sin cambiar Oracle. El criterio ya está
escrito en `DECISION-009-DE-QUIEN-ES-EL-CASO.md`: **un rojo sobre el que el receptor no puede actuar
enseña a ignorar la herramienta**.

Hay tres preguntas, no una:

| pregunta | mecanismo que corresponde |
|---|---|
| ¿de dónde vino la medida? | procedencia del catálogo: proyecto, catálogo base, perfil o biblioteca |
| ¿para qué proyecto obliga? | ámbito de la medida |
| ¿hay hechos con los que puede calcularse? | relaciones requeridas y `medidas_aplicables` |

`catalogo_base`, los perfiles y las bibliotecas contestan la primera pregunta: el proyecto eligió
qué políticas incorporar. `medidas_aplicables` contesta la tercera: si están presentes las
relaciones de entrada, la medida se puede evaluar. Ninguna de las dos contesta la segunda. **Poder
calcular un veredicto no vuelve pertinente ese veredicto.** Ése es el hueco.

## Las cuatro familias

### Declaración explícita en la medida

Es la única familia que puede expresar directamente la intención. El ámbito es parte de lo que una
medida afirma, igual que el umbral, `segun`, `requiere` y `alcance`; por eso corresponde que esté en
la forma de la medida y que aparezca al reificarla como un hecho.

Su ventaja principal no es sintáctica sino de responsabilidad. Al leer una medida se puede saber si
pretende obligar al proyecto que la recibió o sólo al proyecto que la publica. El cargador no tiene
que adivinarlo por el nombre, la ruta ni el sensor que produjo la evidencia. Además, una declaración
viaja intacta por los cuatro orígenes que Oracle ya admite: catálogo local, catálogo base, perfil y
biblioteca.

La desventaja es la de toda declaración semántica: se puede mentir. Escribir `ambito universal` no
demuestra que un consumidor pueda actuar sobre el rojo. Pero ése no es un defecto exclusivo de este
campo. `segun medicion` tampoco demuestra que alguien haya medido, y `procedencia observada` no
demuestra que alguien haya observado. La respuesta de Oracle no ha sido esconder esas afirmaciones,
sino volverlas datos, medir las contradicciones que sí son mecánicamente visibles y declarar el
resto como límite.

El vocabulario de tres valores sugerido —`universal | del_proyecto | de_oracle`— tiene un problema:
mezcla una relación con un nombre propio. `de_oracle` resuelve este caso, pero obliga a agregar
`de_la_biblioteca` cuando una política publicada sólo audite la instalación de su publicador. Y
`del_proyecto` es ambiguo: puede significar el proyecto evaluado o el proyecto que escribió la
medida.

La distinción mínima y general es relativa al origen:

```text
ambito universal       obliga a todo proyecto que seleccione el catálogo y aporte la evidencia
ambito del_origen      obliga sólo cuando el proyecto evaluado es el dueño de la medida
```

En una medida del catálogo base, `del_origen` significa de Oracle. En una medida escrita dentro de
Jam, significa de Jam y se satisface naturalmente. En una biblioteca significa de su publicador, no
de cualquier consumidor que la instale. Así Oracle no gana un privilegio nominal en el lenguaje.
La procedencia identifica al origen; el ámbito declara la relación admitida entre ese origen y el
destino.

No debería haber un valor creíble por omisión. Suponer `universal` reproduce exactamente la fuga que
abre este estudio; suponer `del_origen` apaga en silencio las guardas que hoy sí deben viajar. Una
migración puede reificar temporalmente `sin_declarar`, como hizo `segun`, y dejar que una medida lo
ponga en rojo. El estado final debe exigir la declaración.

### Convención de directorio

Separar `catalogos/meta/` de `catalogos/interno/` mejora la lectura humana, pero no alcanza como
mecanismo. `meta` ya tiene un significado decidido: una medida es meta por la relación que mide, no
por quién la publicó. Las dos especies de este problema son meta. Mudarlas a directorios distintos
haría que la jerarquía de archivos intentara expresar a la vez **nivel** y **ámbito**.

Además, el cargador recorre hoy el catálogo de manera recursiva. Para que `catalogos/interno/`
tuviera efecto habría que enseñarle una excepción de rutas; entonces el ámbito seguiría siendo
binario y por ubicación, sólo que con un nombre nuevo. Una medida copiada o movida cambiaría de
jurisdicción sin que cambiara su declaración. Las bibliotecas y los perfiles necesitarían repetir la
misma convención, y L2 no podría verla si la ruta se descarta al cargar.

El directorio puede quedar como **vista editorial**: agrupar lo interno para que una persona lo
encuentre. Si se adopta, una medida meta podría comprobar que la carpeta coincide con la declaración.
Pero la carpeta no debe decidir qué corre. La fuente de verdad tiene que sobrevivir a un wheel, a
una biblioteca y a un cambio de layout; `DECISION-010` ya mostró por qué la identidad lógica no se
puede apoyar en una forma particular del disco.

### Derivarlo de las relaciones consumidas

Ésta es la alternativa más elegante y la que más merece conservarse, aunque no como autoridad
única. Oracle ya sabe derivar todas las fuentes directas de una medida: `fuente` reifica los `de` de
la tubería y `requiere` reifica las relaciones sin las cuales la medida no concluye. Si cada relación
declarara su ámbito, el ámbito mínimo de una medida sería la intersección de los ámbitos de sus
dependencias. Una sola dependencia `del_origen` impediría declarar universal a su consumidora.

Aplicado al caso, `mutador_excluido` debería declarar que describe configuración cuyo remedio es del
origen Oracle. La medida que la consume no podría presentarse como universal. En cambio, `medida`,
`termino` y `fuente` describen el catálogo del proyecto evaluado; las reglas sobre cómo está escrita
**su** medida sí pueden ser universales.

Hay que precisar qué se deriva. No alcanza con preguntar qué repositorio contiene el emisor. Casi
todas las relaciones de L2 las emite código de Oracle, también cuando Oracle corre dentro de Jam.
Por ese criterio, tanto `medida` como `mutador_excluido` serían «de Oracle», y se perderían las
guardas universales sobre el catálogo del consumidor. Tampoco alcanza con preguntar si la relación
está presente: `hechos_de_mutadores_excluidos` la produce hoy durante la aceptación de un consumidor.
La presencia prueba calculabilidad; no prueba quién puede reparar el hallazgo.

Lo que una relación debe declarar es **de quién es la cosa descrita o su remedio**, no dónde vive el
sensor. Esa metadata sería especialmente valiosa para `verbo_del_cli`, `opcion_del_vocabulario` y
otras relaciones del lenguaje: obliga a decidir si describen el contrato que recibe un consumidor o
la instalación que sólo Oracle mantiene.

La derivación sola todavía es incompleta. Una medida puede consumir la relación universal `medida`
y filtrar por un id exclusivo de Oracle, o imponer una convención editorial que sólo este
repositorio eligió. Ninguna propiedad de la fuente revela esa intención. También puede ser
deliberadamente más estrecha que todas sus entradas. Por eso las relaciones dan un **límite
comprobable** —una medida no puede ser más amplia que sus dependencias—, pero no siempre dan el
ámbito exacto.

Hay además relaciones con propiedad mezclada. `caso` contiene filas propias y heredadas, y
`DECISION-009` resolvió que el `donde` de cada medida decide cuáles mira. Etiquetar toda la relación
como propia descartaría usos válidos sobre casos ajenos; etiquetarla toda como universal no detecta
una política que adjudica al consumidor el defecto de una biblioteca. Derivar el ámbito exacto
exigiría interpretar la semántica del predicado, que es justamente el juicio que se quería sacar de
Python. Otra vez, la relación permite encontrar contradicciones gruesas; la medida sigue teniendo
que declarar su intención.

### Los cinco niveles de representación

El ámbito no está latente en L−2…L2. `DECISION-005` insiste en que un nivel es una representación,
nunca una cosa. Los niveles contestan **sobre qué representación habla el enunciado**: evidencia,
declaración del sensor, identidad del referente o medidas reificadas. El ámbito contesta **a qué
proyecto alcanza el enunciado**.

Las dos especies que hoy conviven en `catalogos/meta/` pueden estar en el mismo nivel y tener ámbitos
distintos. Una regla sobre `medida` es L2 y puede ser universal; una regla sobre una decisión interna
del arnés también es reflexiva y puede ser `del_origen`. A la inversa, una medida L1 de un dominio
puede ser estrictamente local. No hay una función de nivel a ámbito.

Hacer que L2 significara «interno» rompería además una pieza central del proyecto: las medidas meta
que protegen el catálogo de un consumidor dejarían de viajar. Hacer que L2 significara «universal»
reproduciría el problema actual. Los cinco niveles son un eje; el ámbito es otro. La consecuencia
útil de `DECISION-005` no es reutilizar su numeración, sino aplicar su regla: el ámbito debe ser una
representación escrita y reificable, no una propiedad supuesta de la cosa o de su carpeta.

## La elección

Oracle debería adoptar **declaración explícita relativa al origen**, custodiada por una derivación
desde las relaciones. No es un compromiso a mitad de camino: cada parte responde una pregunta que
la otra no puede responder.

La medida declara `universal` o `del_origen`. El cargador conserva además la procedencia que hoy usa
para reunir catálogos, en vez de reducirla a un `dict[id, Medida]` que ya no recuerda de dónde vino
cada entrada. El destino es el proyecto que se está evaluando. Una medida `del_origen` sólo entra en
el catálogo efectivo cuando origen y destino coinciden; una universal entra si su catálogo fue
seleccionado. Después, y no antes, `medidas_aplicables` decide si existen sus relaciones de entrada.

El orden importa:

```text
selección del catálogo  →  ámbito  →  aplicabilidad por relaciones  →  evaluación
qué acepté                  dónde obliga   si puede calcularse             qué dio
```

La identidad de origen debe ser lógica —proyecto, id de biblioteca, perfil o catálogo base de
Oracle—, no igualdad accidental de rutas. En el repo y en el paquete instalado el mismo origen tiene
layouts distintos. La ruta sigue sirviendo para diagnosticar un archivo repetido; no debe definir la
jurisdicción de una política.

Esto también corrige el lenguaje del manual. `catalogo_universal()` no debería llamar universal a
todo lo que carga del directorio empaquetado: debería enumerar como universales sólo las medidas que
lo declaran. Las internas pueden seguir siendo visibles en el inventario de Oracle. Ámbito no es
secreto.

## Qué mantiene honesta la declaración

Hacen falta dos controles distintos. El primero es de presencia:
`meta.toda_medida_declara_su_ambito` detecta `sin_declarar` durante la migración, del mismo modo que
`meta.todo_umbral_declara_de_donde_sale` detecta un `segun` ausente. Cuando la sintaxis lo vuelva
obligatorio, la medida sigue teniendo valor documental: convierte el contrato de carga en un hecho
visible y discutible, como ya ocurre con `alcance`.

El segundo es el que comprueba honestidad hasta donde se puede comprobar mecánicamente:

```text
meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias
```

Para escribirla sin esconder el juicio en Python hacen falta tres hechos reificados: el ámbito de
cada medida, sus dependencias directas —tanto fuentes como `requiere`— y el ámbito declarado de cada
relación. La medida une esos hechos y cuenta la contradicción concreta: una medida `universal` que
depende de una relación `del_origen`. Con dos valores no hace falta inventar una jerarquía numérica;
el par incompatible se escribe en el `donde`.

Conviene reificar una sola relación `dependencia_de_medida(medida, relacion, clase)`, donde `clase`
sea `fuente` o `requiere`, en vez de escribir dos políticas casi iguales. Eso no compone medidas:
es reificación mecánica de la declaración, exactamente el camino que `DECISION-002` conserva para
L2. La meta-medida consume hechos, no veredictos ni testigos de otra medida.

Su `alcance` tendría que decir algo incómodo y exacto: **detecta una declaración más amplia que una
dependencia conocida; no demuestra que toda medida universal sea realmente universal**. No puede
descubrir una suposición de Oracle escondida en un literal, una convención exclusiva explicada sólo
en prosa ni, sobre todo, que el receptor tenga de verdad un remedio disponible. Una prueba sobre un
proyecto ajeno puede aportar evidencia de portabilidad y debería formar parte de la certificación de
un catálogo universal, pero tampoco prueba por sí sola que el rojo sea accionable.

La asimetría es aceptable y útil. Mentir hacia lo amplio perjudica al consumidor y debe fallar ante
toda contradicción derivable. Declarar un ámbito demasiado estrecho pierde cobertura, pero no impone
un rojo sin remedio; se discute con evidencia externa y revisión humana. Oracle vuelve falsable la
declaración, no la convierte mágicamente en verdad.

## Por qué esto merece `DECISION-012`

Sí. No es el traslado de un archivo ni una excepción para una medida nueva. Cambia qué significa
que una medida viaje en el paquete, agrega una dimensión a la forma declarativa, obliga a conservar
procedencia al cargar, altera qué entra al catálogo efectivo y corrige lo que el manual llama
universal. También fija una regla para bibliotecas futuras. Es una decisión de lenguaje y de
ejecución, con alternativas plausibles que conviene no volver a discutir desde cero.

El título y la apertura propuestos, en el registro de las decisiones vigentes, son:

> # Decisión 012 — cada medida declara dónde obliga, y «empaquetada» deja de significar «universal»
>
> **Fecha:** 2026-09-03 · **Estado:** propuesta
>
> ## El hecho
>
> El catálogo base usa una sola decisión de carga para contestar dos preguntas distintas: qué
> medidas viajan con Oracle y cuáles obligan al proyecto que lo consume. Por eso una regla sobre
> cómo está escrito el catálogo de Jam y una regla sobre una exclusión de
> `nucleo/mutacion.py` llegan por el mismo camino, aunque sólo la primera tenga remedio en Jam. La
> ubicación declara procedencia; no declara jurisdicción. Un rojo que sólo puede corregirse aguas
> arriba no es una guarda universal: es una obligación enviada al proyecto equivocado.

## La comparación con `public`, `private`, `protected` y los namespaces

La comparación sirve para una intuición concreta: una frontera importante debe estar declarada y la
herramienta debe hacerla cumplir. También sirve la idea de namespace para identificar el origen sin
depender de la ruta física. En ese sentido, hacer explícito el ámbito evita que una pieza interna se
publique por accidente como si fuera parte del contrato de todos.

Pero `private` es un nombre engañoso para este caso. En un lenguaje de programación, la visibilidad
controla quién puede nombrar o llamar una pieza. Oracle no tiene composición de medidas por decisión
expresa de `DECISION-002`: una medida no llama otra, no consume su veredicto y no hereda sus
testigos. Acá no hay llamadas que prohibir. El ámbito decide **en qué proyecto se evalúa una
política**, no qué otra medida puede acceder a ella.

Tampoco hay un equivalente útil de `protected`: no existe una jerarquía de subclases ni una noción
de descendiente con acceso privilegiado. Y `meta.` se parece a un namespace sólo como clasificación
temática. `DECISION-007` ya fijó que `meta.*` no significa «oficial»; por la misma razón no puede
significar «privado» ni «universal».

Finalmente, lo interno no debe quedar oculto. Una medida `del_origen` puede y debe seguir apareciendo
reificada cuando Oracle se mide a sí mismo, ser inspeccionable en el manual interno y estar sujeta a
mutación y corpus. Lo único que no hace es obligar a Jam o a LyraGASP. La analogía más cercana no es
la privacidad de un método, sino la **jurisdicción de una regla**: todos pueden leerla, pero sólo
dicta un veredicto donde existe responsabilidad para responderlo.
