# Plan 0.8.1 — que la evidencia venga del mundo

**Fecha:** 2026-09-05 · **Estado:** recorrido reusable entregado y medido el 2026-09-07; sin corte
**El número es provisorio:** si esto agrega algo al lenguaje —una relación, una forma de declarar
frescura— sube la menor por `ESPECIFICACION.md` §0. Se decide en el corte, no ahora.

## Lo que Oracle prueba hoy, y lo que no

**Revisión:** [`estudios/SENSOR-0.8.1-PRIMERA-CORRIDA.md`](estudios/SENSOR-0.8.1-PRIMERA-CORRIDA.md).
LyraGASP ya tenía sensores y casos que narraban lecturas reales; sus 26 casos no declaraban
`procedencia`. No corresponde llamarlos a todos sintéticos ni reclasificarlos sin repetir la lectura.

Todo lo que Oracle demuestra hoy es sobre **coherencia interna**: que un catálogo está bien escrito,
que sus medidas discriminan, que su corpus las fija. Nada de eso dice que el proyecto medido esté
bien, y hay tres hechos que lo muestran desde ángulos distintos:

- **El corpus de LyraGASP no bastaba para certificar el estado actual de sus assets.** Mezclaba
  casos sintéticos con narraciones de lecturas reales, sin `procedencia` explícita. No era correcto
  deducir que nadie había corrido un sensor, pero tampoco certificaba frescura actual.
- **Jam tiene tres medidas universales en sombra**, y una de ellas es
  `la_medida_no_se_fija_solo_con_evidencia_fabricada`. Se mide, se informa, y no tumba la corrida.
- **El tutorial del sitio lo dice en su última línea**: mientras la evidencia se escriba a mano,
  esto prueba que el catálogo es coherente, no que el proyecto esté bien.

Los tres señalan el mismo límite: **coherencia del catálogo no equivale a evidencia actual del mundo**.

## Por qué esto es más grande que un verbo nuevo

Un sensor no es código que Oracle pueda escribir por su cuenta. Vive en el dominio del consumidor,
lee cosas reales —un asset de Unreal, un árbol de archivos, una corrida— y produce filas. Oracle ya
tiene la mitad: `L−1` declara qué lee un sensor y con qué unidades, `L−2` declara qué leyó y si
sigue fresco. Lo que falta es que alguien lo conecte y que la evidencia **venga de ahí**.

El patrón ya está descrito en los consumidores: el sensor va partido en dos —una parte pura que se
testea sin abrir el editor, y un adaptador que habla con el motor y escribe la evidencia—. Eso es
diseño, no invención.

## Lo que hay que decidir

1. **¿Qué demuestra 0.8.1?** No alcanza con «hay un sensor». Tiene que quedar un caso con
   `procedencia: observada` cuya evidencia haya salido de una corrida real, y que hoy no exista.
2. **¿Qué pasa con las sombras de Jam?** Si la evidencia real entra, ¿se pueden apagar? ¿O revelan
   que esas tres medidas piden algo que un consumidor no puede dar todavía?
3. **¿Cómo se comprueba que una evidencia es realmente observada?** Hoy es una declaración y nadie
   la verifica — el propio `alcance` de la medida que la vigila lo admite. `L−2` tiene la huella y
   la frescura; la pregunta es si eso alcanza para distinguir una corrida de una transcripción.

## Lo que no hay que hacer

**Declarar `observada` una evidencia transcrita a mano.** Es la mentira más barata del proyecto y la
que nadie puede detectar. Si el sensor no corre, la evidencia es `construida` y se dice.

## Primer recorrido y decisiones

1. Se ejecutó el adaptador existente del dataset de LyraGASP contra archivos reales: 37 clips
   declarados, 37 FBX presentes y 0 ground truth. Se conservó un caso nuevo observado, su JSON
   íntegro y el registro en el consumidor. No se abrió Unreal ni se juzgó calidad.
2. Jam conserva sus tres sombras: observar este dataset no observa su geometría ni declara sus
   unidades o el origen de sus umbrales. Lyra baja de 9 a 8 medidas sin observación; tampoco se
   apaga su sombra global. Su aceptación pasa con 27 casos; Jam mantiene 23.
3. Las seis huellas leídas y revalidadas están estables. L−2 detecta una diferencia, pero dos
   declaraciones falsas iguales pasan: no prueba autenticidad ni que una corrida haya ocurrido.

Distribución 0.8.0, álgebra 0.6 y sintaxis 0.2 conservadas. El experimento usa el lenguaje existente,
sin ampliar sus contratos.

## El recorrido reusable, entregado

`tools/observar.py` convierte la captura y la revalidación en un procedimiento que cualquier
consumidor puede correr con un plan suyo. Detalle y medición en
[`estudios/OBSERVAR-0.8.1-RECORRIDO.md`](estudios/OBSERVAR-0.8.1-RECORRIDO.md).

Lo que responde a las tres decisiones de arriba, sin cambiar ninguna:

1. **Qué demuestra.** Un caso `procedencia: observada` sale de una corrida que la herramienta
   ejecutó, con la evidencia conservada byte a byte y la expectativa —etiqueta, y opcionalmente el
   valor— declarada en el plan ANTES de correr. Si el resultado discrepa, no se escribe nada.
2. **Las sombras siguen.** Observar archivos no declara unidades ni explica el origen de un umbral.
   Ninguna sombra de Jam ni de Lyra se apaga por esto.
3. **La frescura no es autenticidad.** El registro y el informe llevan `autenticidad.comprobada:
   false` escrito con su motivo, y dos controles del test fijan el límite: huellas distintas dan
   rojo 1, dos declaraciones falsas iguales dan verde 0.

Sigue sin haber corte de 0.8.1: una herramienta nueva sube la distribución cuando alguien decida
cortar, por §0, y esa decisión no se toma al empezar el trabajo.
