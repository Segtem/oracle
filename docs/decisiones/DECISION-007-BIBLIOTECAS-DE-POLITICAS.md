# Decisión 007 — bibliotecas de políticas: se adopta, con seis correcciones

**Fecha:** 2026-08-31 · **Estado:** aceptada la dirección, la primera versión sin construir
**Propuesta original:** `IDEA-BIBLIOTECAS-META-Y-TELEMETRIA.md` · **Prototipo:** rama
`propuesta-biblioteca` (`nucleo/biblioteca.py`, su ejemplo y sus tests)

## Lo que se adopta sin cambios

La propuesta acierta en cinco cosas que **no hay que diluir después**, y conviene fijarlas acá
porque son justo las que van a estar bajo presión:

1. **Datos solamente.** Descubrir una biblioteca lee metadata y un manifiesto en ruta fija; NO llama
   `EntryPoint.load()` ni importa un módulo ajeno. Conserva el invariante del proyecto: **cargar una
   medida nunca ejecuta Python.** Si un paquete trae sensores o escalares deja de ser una biblioteca
   de políticas y pasa a ser una extensión ejecutable, con otro tipo, otro comando y una confianza
   explícita comparable a `--confiar-escalares`. Mezclarlos haría que «instalar una regla» equivalga
   en silencio a ejecutar código de un tercero.
2. **`meta.*` no significa «oficial».** Una medida es meta por la relación que mide, no por quién la
   publicó. Una política global puede estar mal para un proyecto.
3. **Opt-in por proyecto**, igual que `catalogo_base` y los perfiles. Instalar no es activar.
4. **Dos bibliotecas con el mismo ID fallan cerrado.** Nunca gana «la última cargada».
5. **La certificación afirma hechos modestos**, no verdad: el paquete carga, declara sus límites,
   trae evidencia, no tiene conflictos. Nunca «esta política es correcta».

## Las seis correcciones

### 1. Una biblioteca sin número de mutación es un catálogo que nadie rompió

La propuesta pide, para certificar, «ejecutar el corpus propio y comprobar que no hay verdes
vacuos». Es poco, y este proyecto sabe por qué: un corpus que pasa demuestra que las medidas no se
contradicen con su propia evidencia, no que esa evidencia las ponga a prueba.

**Una biblioteca publica su número de `tools/mutar.py` o no se certifica.** Es el único dato que
distingue un catálogo probado de uno que nadie rompió, y es barato: son datos, corre en segundos.

### 2. `procedencia` cruza la frontera del paquete, y nadie miró qué significa ahí

Una biblioteca trae su corpus, y esos casos declaran `procedencia: observada` con
`origen: {repo, commit}` **de OTRO repositorio**. Cuando mi proyecto la carga,
`meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` evalúa los casos del tercero y me dice si
*sus* medidas están bien fijadas. ¿Es eso lo que quiero saber?

No es teórico. El 2026-08-30 un caso de este repo transcribió una huella **verdadera** que era de
`Brianholl/jam` y la declaró bajo `repo: "Segtem/oracle"` (corregido en `corpus/meta/428`). Una
observación cierta atribuida al repo equivocado. Con bibliotecas eso deja de ser un descuido y pasa
a ser la operación normal.

**Hay que decidir, antes de la primera versión:** una relación `caso` reificada gana un campo que
diga de qué biblioteca viene, y las medidas meta que evalúan el corpus deciden explícitamente si
miran sólo lo propio, sólo lo ajeno, o todo. Hoy la pregunta ni se puede formular.

> **Decidido el 2026-09-01 en [`DECISION-009`](DECISION-009-DE-QUIEN-ES-EL-CASO.md):** cada medida
> lo declara, y no es uniforme —dos miran sólo lo propio, dos miran todo—. La relación gana dos
> campos, `es_heredado` y `biblioteca`, porque el precedente de `es_heredada` era binario y esto no
> lo es. El código llega con el descubrimiento: hoy no existe ningún caso ajeno, así que el campo
> sería constante y su mutante sobreviviría.

### 3. Lo que hay que leer antes de instalar es el `alcance`, y no está en el flujo

El comando propuesto para inspeccionar es `oracle biblioteca listar`, con ID y versión. Eso no
alcanza para decidir. **Lo que determina si una política sirve para un proyecto es qué NO ve**, y
Oracle es la única herramienta del mundo que tiene esa información estructurada.

`listar` tiene que mostrar, por medida: el **umbral**, el `segun`, y el **`alcance` completo**. Es
el paso de revisión humana, y es el que justifica que estas políticas se distribuyan como datos
legibles y no como un binario.

### 4. Falta el modo sombra, y sin él nadie adopta una biblioteca

Adoptar un catálogo de políticas **te pone en rojo**. Ya pasó acá: las medidas universales dejaron a
un consumidor en rojo el primer día, y era correcto. Pero si la primera experiencia de instalar una
biblioteca es que el proyecto deja de compilar, no se instala una segunda vez.

**Una biblioteca se puede seleccionar en modo sombra:** se evalúa y se reporta, no falla. Con una
medida que cuente cuántas están en sombra, para que «lo tengo en sombra hace ocho meses» sea un
hecho visible y no una comodidad silenciosa.

> **Construido el 2026-09-01, y NO como característica de bibliotecas.** Al medir la mudanza de
> Jam y LyraGASP al Oracle publicado apareció que el problema no viene de una biblioteca: viene del
> **catálogo base**, que los dos ya activan con `catalogo_base: true`. Sus catálogos se escribieron
> antes de que `segun` existiera y antes de L−1, así que adoptar el Oracle de hoy los deja en rojo
> con 34 y 104 infracciones respectivamente. Ninguna es un defecto nuevo: están viejos.
>
> La sombra se declara entonces en `oracle.json` y vale para **cualquier** conjunto de políticas
> heredado, sea del catálogo base, de un perfil o de una biblioteca. Eso la desacopla de la
> corrección 2, que era lo que la bloqueaba.
>
> Tres medidas la vigilan, y ninguna puede ponerse en sombra a sí misma —sería apagar el único
> mecanismo que impide que apagar salga gratis—: `meta.toda_sombra_declara_desde_y_porque`,
> `meta.ninguna_sombra_ya_en_verde` y `meta.ninguna_sombra_sobre_una_medida_que_no_existe`.

### 5. Una biblioteca es también un vector para AFLOJAR, y eso no está nombrado

Alguien publica `meta.publicador.todo_umbral_declara_de_donde_sale` con el umbral en `<= 5` en vez
de `<= 0`. Se instala igual, se llama casi igual, y afloja el proyecto sin que nada avise.

El prefijo de publicador que la propuesta ya pide ayuda a **verlo**, no a impedirlo. La defensa real
es la corrección 3: si el listado muestra el umbral de cada medida instalada, un `<= 5` donde el
resto tiene `<= 0` salta a la vista. Sin eso, el prefijo sólo documenta de quién es la puerta.

### 6. Telemetría: sólo la fase 1, y el motivo no es la privacidad

La propuesta separa bien los cuatro problemas y recomienda el orden correcto. Se adopta **la fase 1
—diagnóstico local, sin red— y nada más**, y conviene decir el motivo verdadero: las fases 3 y 4 no
fallan por privacidad, fallan por **costo estructural**. Piden un servidor, una política de
retención y una superficie legal que nadie está en condiciones de sostener. Ese costo la propuesta
no lo cotiza.

> **Corregido el 2026-09-01.** Este párrafo decía que ese costo era desmedido «para un proyecto que
> es **privado a propósito** y cuya decisión de publicar está diferida y registrada con fecha».
> **Las dos cosas dejaron de ser ciertas**: el repositorio se abrió y `0.2.0` está en PyPI
> ([`DECISION-008`](DECISION-008-EL-REPOSITORIO-SE-ABRE.md)); y lo de «registrada con fecha» nunca
> lo fue —el archivo que se citaba no existió nunca—.
>
> **La conclusión no cambia y el argumento queda más limpio:** un servidor, una retención y una
> superficie legal son caros para cualquier proyecto de una persona, sea público o privado. Ser
> público no crea a quién rendirle cuentas de los datos; crea la posibilidad de tener usuarios, que
> es otra cosa.

La fase 2 —`oracle bug preparar`— se acepta cuando exista alguien más que el autor usando Oracle.

> **El criterio, hecho comprobable el 2026-09-01.** Antes decía «hoy no lo hay», que era verdad y
> dejaba de serlo sin que nadie se enterara: hoy Oracle se instala con una línea. La condición pasa
> a ser un hecho observable: **cuando alguien que no es el autor abra un issue o reporte un
> problema**. Las descargas de PyPI no sirven —cuentan espejos y CI, no personas— y las estrellas
> tampoco. Un issue es alguien que se topó con algo y se tomó el trabajo de escribirlo.

## Lo que NO se decide todavía

- **El nombre del comando.** `oracle biblioteca` compite con `oracle politica` y con `oracle pack`.
  Se decide al escribir la primera versión, con la CLI delante.
- **Si el manifiesto es TOML.** El prototipo usa TOML y el resto del proyecto usa JSON y la
  superficie infija. Tres formatos en un proyecto que presume de legibilidad merece una razón
  escrita, y no está escrita.
- **`oracle.lock`.** La idea es buena —volver falsable «este proyecto fue juzgado con estas
  políticas»— pero es la pieza que más se parece a construir un resolvedor propio. Va después de que
  exista una biblioteca de verdad, no antes.

## Estado del prototipo

`nucleo/biblioteca.py` (298 líneas), sus tests y un ejemplo completo viven en la rama
`propuesta-biblioteca`. **No está integrado y no se le corrió la mutación de código**, así que no se
sabe si aguanta la vara del núcleo. Esa medición es el primer paso de la implementación, no el
último: esta semana dos módulos se descartaron por 31 y 68 mutantes vivos.
