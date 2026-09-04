# Decisión 012 — cada medida declara dónde obliga, y «empaquetada» deja de significar «universal»

**Fecha:** 2026-09-03 · **Estado:** vigente

## El hecho y el hueco

Hasta hoy, «universal» significaba una sola cosa: residir físicamente en el directorio empaquetado de
Oracle. Eso describe **procedencia**, no **ámbito**. Ambas nociones coincidieron de hecho mientras
todas las políticas publicadas por Oracle en su catálogo base obligaban por igual a cualquier
proyecto que las incorporase.

Esa coincidencia se rompió el 2026-09-03. Una medida sobre `EXCLUSIONES_DE_MUTADORES`
(`meta.ninguna_exclusion_de_mutador_se_aplica_globalmente`) puso a **Jam en rojo**, y era el único
rojo duro que Jam tenía en todo su catálogo. Jam no tenía ningún remedio disponible en su propio
repositorio: la lista de exclusiones vive en `nucleo/mutacion.py`, dentro del árbol de código de
Oracle. Para apagar ese rojo, Jam no podía hacer nada por sí mismo: su única alternativa era pedir un
cambio aguas arriba o acostumbrarse a convivir con una alerta encendida.

El principio ya estaba formulado en [`DECISION-009`](DECISION-009-DE-QUIEN-ES-EL-CASO.md): **un rojo
sobre el que el receptor no puede actuar enseña a ignorar la herramienta.** Un veredicto sin remedio
destruye la autoridad del sistema entero y acostumbra al usuario a desoír las alarmas legítimas.

El hueco era conceptual: Oracle creía contestar tres preguntas y en realidad sólo contestaba dos.
Sabía de dónde vino una medida (el catálogo base, los perfiles, las bibliotecas o el proyecto local) y
sabía si había hechos suficientes para calcularla (`medidas_aplicables`). Pero **nadie contestaba
para qué proyecto obliga**. Poder calcular un veredicto no vuelve pertinente ese veredicto. Ése es el
hueco que esta decisión cierra.

## Lo que se decide

Cada medida declara explícitamente su ámbito mediante un vocabulario cerrado de dos valores,
relativo al **origen** y no a Oracle:

```text
ambito universal     obliga a todo proyecto que seleccione el catálogo y aporte la evidencia
ambito del_origen    obliga sólo cuando el proyecto evaluado es el dueño de la medida
```

La relatividad al origen evita cualquier asimetría nominal en el lenguaje:
- En una medida del catálogo base, `del_origen` significa que obliga únicamente a Oracle.
- En una medida escrita dentro de Jam, `del_origen` significa que obliga a Jam, y la condición se
  satisface sola por identidad directa.
- En una biblioteca de políticas publicada, `del_origen` significa que obliga a su publicador al
  auditarse o certificarse, y no a los consumidores que la incorporen en sus proyectos.

Oracle no gana un privilegio nominal en el lenguaje: no hay un valor `de_oracle` ni una excepción
cableada en Python. La procedencia identifica quién emitió la medida; el ámbito declara la relación
admitida entre ese emisor y el proyecto evaluado para que la política entre en vigor.

## El orden de las preguntas

El proceso de carga respeta ahora la jerarquía lógica de las decisiones:

```text
selección del catálogo  →  ámbito  →  aplicabilidad por relaciones  →  evaluación
     qué acepté             dónde obliga          si puede calcularse            qué dio
```

1. **Selección del catálogo:** el proyecto evaluado decide qué colecciones de políticas incorpora
   (`catalogo_base`, perfiles, bibliotecas o medidas locales).
2. **Ámbito:** el cargador descarta aquellas medidas seleccionadas cuyo ámbito no abarca al proyecto
   evaluado. Una medida `del_origen` entra al catálogo efectivo sólo si origen y destino coinciden
   lógicamente.
3. **Aplicabilidad por relaciones:** sobre las medidas que sobrevivieron al filtro de ámbito,
   `medidas_aplicables` determina si el proyecto aportó las relaciones requeridas para su cálculo.
4. **Evaluación:** el motor relacional evalúa la expresión, compara contra el umbral y emite el
   veredicto.

La identidad de origen entre emisor y evaluado es **lógica** —el identificador de proyecto, de
biblioteca, de perfil o del catálogo base— y no una igualdad accidental de rutas en el disco. Como se
comprobó en [`DECISION-010`](DECISION-010-EL-PAQUETE-INSTALADO-ES-OTRO-PROYECTO.md), el repositorio y
el paquete instalado tienen layouts distintos; atar la jurisdicción a la forma de las rutas
quebraría la identidad en wheels y entornos vendorizados. La ruta sirve para diagnosticar colisiones
de archivos, no para definir jurisdicción.

## Por qué NO es un nivel nuevo

La tentación inmediata era interpretar esta distinción como la apertura de un nivel nuevo en la torre
de representación. No lo es.

Verificado el 2026-09-03: el catálogo tiene 55 medidas, la relación `medida` reifica exactamente 55
filas, y la meta-medida `meta.ninguna_medida_sin_alcance` está entre las filas que juzga, **ella
incluida**. L2 es un punto fijo. Como ya resolvió
[`DECISION-005`](DECISION-005-CINCO-NIVELES-DE-REPRESENTACION.md) al descartar L3: «colapsa, no
falta». Una afirmación sobre el ámbito de una medida se formula con la misma álgebra sobre la misma
relación `medida` que ya existe.

Un nivel nuevo aparece únicamente cuando surge una representación nueva en el mundo (evidencia en L0,
declaración del sensor en L−1, identidad del referente en L−2). El ámbito no trae ninguna
representación nueva: entra como un **campo** de la representación de medidas que ya teníamos, junto a
`alcance`, `segun` y `umbral_op`.

Nivel y ámbito son dos ejes ortogonales, sin función de uno al otro:
- El nivel responde **sobre qué representación habla el enunciado** (evidencia empírica, metadatos de
  sensores o forma de las medidas).
- El ámbito responde **a qué proyecto alcanza la obligación**.

Las dos especies conviven en L2. Una regla que exige que toda medida declare su alcance habla de L1 y
es universal: cualquier proyecto que escriba medidas debe hacerlo con rigor. Una regla que juzga las
exclusiones de mutadores del arnés de Oracle también es reflexiva sobre el marco, pero es `del_origen`.
A la inversa, una medida L1 de un dominio específico puede ser estrictamente local. Pretender que L2
equivalga a «interno» apagaría las guardas de calidad que deben viajar; pretender que L2 equivalga a
«universal» reproduciría el rojo de Jam.

## Por qué NO es visibilidad ni ocultamiento

El vocabulario tradicional de los lenguajes de programación (`public`, `private`, `protected`) resulta
engañoso aquí.

En un lenguaje de programación, la visibilidad gobierna **quién puede nombrar o llamar a una pieza**.
En Oracle, la composición de medidas fue expresamente rechazada en
[`DECISION-002`](DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md): ninguna medida puede llamar a otra,
consumir sus testigos o heredar su veredicto. No hay llamadas que prohibir, ni jerarquía de clases que
justifique un modificador `protected`.

La analogía correcta es la **jurisdicción de una regla**: todos pueden leerla, pero sólo dicta
veredicto donde existe responsabilidad para responderla.

Y `del_origen` **no es ocultamiento**:
- Una medida `del_origen` sigue publicada e indexada en el manual.
- Sigue reificada como fila en la relación `medida` cuando Oracle se evalúa a sí mismo.
- Sigue sujeta a la ronda de mutación de catálogo.
- Sigue teniendo casos que fijan su comportamiento en el corpus.

Lo único que no hace es dictar veredicto sobre un proyecto tercero.

## El resultado medido

La clasificación de las 55 medidas del catálogo base arrojó una partición precisa:
- **37 universales** (67.3 %)
- **18 del origen** (32.7 %)

Al aplicar este filtro sobre Jam, el resultado fue exacto: de las 25 medidas que concluían antes sobre
su repositorio, ahora concluyen **exactamente 20**. El ámbito le retiró a Jam **exactamente cinco
medidas**, y ninguna otra:

1. `meta.el_diagnostico_no_publica_el_dominio`
2. `meta.ninguna_exclusion_de_mutador_se_aplica_globalmente`
3. `meta.toda_opcion_del_vocabulario_declara_su_sentido`
4. `meta.todo_verbo_del_cli_esta_en_la_ayuda`
5. `meta.todo_vocabulario_cerrado_esta_en_el_manual`

El contraste muestra qué estaba midiendo el sistema: Jam venía evaluando si el manual de Oracle estaba
completo, si las opciones del compilador declaraban su sentido o si los verbos de la CLI coincidían con
la ayuda.

Las otras 13 medidas clasificadas como `del_origen` nunca habían llegado a concluir sobre Jam: operan
sobre relaciones producidas por sondas sintéticas (como conmutatividad de `unir`, reversibilidad del
serializador o equivalencia de macros) que un consumidor no emite en su evidencia. En esas 13 medidas,
declarar el ámbito sólo hizo explícito lo que `medidas_aplicables` ya hacía por omisión de relaciones.

## El costo, la migración y la falta de omisión creíble

Esta decisión tuvo un costo contractual directo: `ambito` pasó a ser un **parámetro obligatorio** en
las cuatro macros del lenguaje (`peor`, `ninguno`, `ninguno-requiere` y `ninguno-par`).

No existe un valor por omisión creíble:
- Suponer `universal` reproduciría exactamente la fuga que abrió este trabajo, dejando que nuevas
  medidas internas vuelvan a obligar silenciosamente a terceros.
- Suponer `del_origen` apagaría en silencio las guardas de calidad que sí deben viajar y proteger el
  catálogo del consumidor.

El costo real fue la migración de los catálogos existentes. Para no invalidar la carga del catálogo
completo de un consumidor al actualizar la versión, el cargador y las macros conservan la ausencia
como el estado transitorio `sin_declarar`. Es el mismo camino que se abrió al agregar `segun`, y por el
mismo motivo: no se inventa un valor arbitrario, sino que se registra honestamente que el autor no
eligió.

A partir de allí, la medida de presencia `meta.toda_medida_declara_su_ambito` se lo reclama en rojo.
Sin este escalón de migración, introducir el parámetro obligatorio rompía la carga de cualquier
proyecto consumidor antes de permitirle clasificar sus propias medidas. Hay que contarlo con claridad:
es la parte incómoda de cambiar un contrato base, y es la que más fácilmente se olvida una vez que el
árbol vuelve a estar verde.

## La asimetría aceptada

El sistema asume una asimetría deliberada frente al error de declaración:
- **Mentir hacia lo amplio** perjudica al consumidor al imponerle un veredicto ajeno sin remedio. Por
  eso debe fallar ante toda contradicción derivable mecánicamente.
- **Declarar un ámbito demasiado estrecho** retiene una política en su autor original. Pierde
  cobertura compartida, pero no impone un rojo sin remedio a ningún tercero.

La contradicción hacia lo amplio se combate con verificación automática; la estrechez se discute
editorialemente con revisión humana y evidencia externa. Oracle vuelve falsable la declaración; no la
convierte mágicamente en verdad.

## Lo que la decisión NO puede prometer

Que una medida se declare `universal` en su archivo no demuestra que realmente lo sea.

La cota mecánica que se incorpora —la meta-medida
`meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias`— detecta una contradicción
derivable y nada más: verifica que una medida no sea más amplia que sus dependencias directas.

La herramienta no puede prometer nada más allá de esa cota. No puede descubrir una suposición
escondida en un literal, ni una convención explicada sólo en prosa, ni —sobre todo— si el receptor
tiene de verdad un remedio disponible. La declaración sigue siendo una afirmación humana sobre
jurisdicción; el marco comprueba su consistencia relacional, pero no sustituye el juicio de pertinencia
ni garantiza que el rojo sea accionable.
