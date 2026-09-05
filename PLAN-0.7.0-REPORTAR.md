# Plan 0.7.0 — cómo alguien dice que Oracle no le alcanzó

**Fecha:** 2026-09-05 · **Estado:** propuesta, sin empezar

## La pregunta

Alguien usa Oracle y se topa con un límite: una medida que no puede escribir, un verde que sabe
falso, un operador que le falta, un rojo que no entiende. ¿Por dónde lo dice, de forma que sirva
para arreglarlo después?

La respuesta fácil es un issue de GitHub. Es también la que pierde casi todo: un issue es prosa
libre, envejece sin que nada lo note, y no se puede medir. Este proyecto ya rechazó esa forma para
todo lo demás.

## Lo que ya existe y nadie está usando para esto

**El corpus es exactamente ese canal, y ya está construido.** Un caso registra, con estructura:

```
sintoma            qué se vio
etiqueta           qué clase de falla es: falso_verde, falso_rojo, deuda_de_diseño…
como_se_detecto    persona · accidente · herramienta_ajena · observacion · mutacion
procedencia        observada · construida · generada
medida             sobre qué regla
evidencia          las filas exactas
leccion            qué queda fijado
```

Un usuario que encuentra una limitación tiene que decir, naturalmente: **qué esperaba, qué pasó, y
cómo se dio cuenta**. Son tres de esos campos. La estructura ya está pensada para esto; lo que falta
es el camino.

Y hay una asimetría que vale la pena mirar: de los 180 casos del corpus, **28 los encontró alguien
mirando** —`persona`, `accidente`, `herramienta_ajena`— contra 152 del arnés automático. Ese 15,6 %
es precisamente lo que un reporte externo aportaría, y hoy sólo entra si el que mira tiene commit en
el repositorio.

## Las tres formas, y lo que cada una cuesta

### Un caso que no compila todavía

El reporte ES un caso del corpus, con una etiqueta nueva —`limite_reportado`— y sin exigir que la
medida exista. Se escribe en la superficie `.caso` que el proyecto ya lee.

Lo bueno: entra por la puerta que el proyecto ya tiene, se puede medir, y quien lo escribe queda
obligado a decir cómo lo detectó. Lo incómodo: le pide a un usuario que aprenda una sintaxis para
quejarse, que es exactamente cuando menos ganas tiene de aprender nada.

### Un verbo que arma el caso

`oracle reportar` toma lo que el usuario tiene a mano —la medida, la evidencia, el veredicto que le
pareció mal— y escribe el archivo. El usuario contesta preguntas, no aprende una gramática.

Lo bueno: convierte una queja en evidencia estructurada sin pedirle nada al que reporta. Lo
incómodo: hay que decidir qué hace con el archivo. Escribirlo en su repo no lo hace llegar a nadie.

### Una herramienta MCP que lo recolecta

El servidor de 0.6.0 ya sabe evaluar y desafiar. Un agente que topa con un límite podría emitirlo
con el contexto entero —la medida, la evidencia, el veredicto, la versión— sin que una persona
transcriba nada.

Lo bueno: el reporte más completo posible, y automático. Lo incómodo, y es serio: **el servidor de
0.6.0 es de sólo lectura por diseño**, y esto lo cambia. Cualquier cosa que escriba o envíe rompe
esa propiedad, que costó descartar una compuerta entera para conservarla.

## Lo que hay que decidir antes de escribir código

1. **¿A dónde va el reporte?** Un archivo en el repo del que reporta no llega. Un issue automático
   necesita credenciales. Un endpoint necesita un servidor y una política de datos. Ninguna de las
   tres es gratis, y la elección decide todo lo demás.

2. **¿Qué pasa con lo que el reporte arrastra?** Una evidencia real trae rutas, nombres de archivos,
   ids de dominio y a veces prosa del negocio. `oracle diagnostico` ya enfrentó esto y tiene una
   medida que lo vigila —`meta.el_diagnostico_no_publica_el_dominio`—. Un reporte que sale del
   repositorio del usuario tiene el mismo problema, más grande.

3. **¿Un reporte es un caso, o aspira a serlo?** Un caso del corpus está fijado: tiene medida,
   evidencia y veredicto esperado. Un reporte puede ser sólo «esto no me dejó expresar lo que
   quería», que no tiene medida ni evidencia. Si entra al corpus como caso, ¿qué le pasa a las
   medidas meta que exigen que todo caso reclame una medida existente?

4. **¿Quién decide que un reporte es válido?** Aceptarlos todos llena el corpus de ruido; filtrarlos
   a mano no escala. Y hay una tentación clara que conviene nombrar ahora: usar un modelo para
   triarlos, que es pedirle al generador que juzgue lo que se le reporta.

## Lo que este plan NO debería hacer

**Convertir el reporte en una promesa.** Que alguien reporte un límite no obliga a nadie a
arreglarlo, y decir lo contrario es la clase de compromiso que envejece mal. El canal sirve si
convierte una queja en evidencia; que además se atienda es otra decisión, de otro nivel.

**Romper la sólo-lectura del servidor por comodidad.** Si el camino elegido pasa por MCP, eso es un
cambio de contrato y merece su propia decisión escrita, no un parámetro nuevo.
