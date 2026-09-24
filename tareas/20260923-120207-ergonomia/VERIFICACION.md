# Verificación de las fricciones de autoría

Fecha: 2026-09-23. Fuente del encargo: [TAREA.md](TAREA.md), incluida la revisión del 23/09; inventario auditado: [FRICCIONES.md](FRICCIONES.md), conservado sin editar.

## Corte y método

- Checkout y `main`: `a891cf41a25688faf51d623913c477af41673c45`.
- `git describe --tags --always`: `v0.28.0-31-ga891cf4`.
- Distribución **0.28.0**, `VERSION_ALGEBRA = "0.8"`, `VERSION_SINTAXIS = "0.6"`.
- Hay **15 entradas**, no 14 como dice la nota de revisión. Se verificaron las 15, incluidas las tres ya revisadas. Se confirman sus resultados: 1.1 cierta, 3.2 falsa, 6.2 vencida.
- **Cierta**: el comportamiento central se reproduce hoy; se explicitan las exageraciones que la prueba no sostiene. **Vencida**: el problema histórico concreto ya tiene solución integrada. **Falsa**: un contraejemplo invalida la afirmación o la evidencia citada no demuestra el problema atribuido. “Falsa” no significa que toda frase de la entrada sea falsa.
- No se infiere costo humano a partir de contar líneas, cotas o errores. Las deudas se midieron ejecutando las medidas meta actuales sobre los catálogos y corpus actuales, con el contexto de escalares de cada proyecto. Una cota de configuración sola no prueba el valor actual.
- El arnés sólo escribe dentro de temporales y lee los proyectos externos. La reproducción naval copia el laboratorio; no altera el juego original. No se modificó el lenguaje ni se hicieron commits.

Reproducir desde la raíz:

```bash
python3 tareas/20260923-120207-ergonomia/verificar.py
python3 -m unittest -v \
  tests.test_juzgar_cota_y_ausentes.NoAplicadasTests \
  tests.test_sintaxis.SintaxisDeCasosTests.test_una_relacion_presente_y_vacia_no_es_una_relacion_ausente \
  tests.test_test_alcance tests.test_primer_valor \
  tests.test_generador.TestUmbralDeclarado
```

El primer comando terminó con **exit 0**. Cada bloque numerado de [verificar.py](verificar.py) ejecuta la reproducción correspondiente; [SALIDAS.txt](SALIDAS.txt) conserva stdout/stderr, incluidos errores esperados y códigos de cada CLI. El segundo terminó con **23 tests, OK**, exit 0; salida íntegra en [TESTS.txt](TESTS.txt). Las rutas temporales y la duración pueden variar. El arnés requiere las copias externas citadas por el inventario; no es una suite portable ni una implementación del lenguaje.

## Resultado por entrada

### 1.1 — CIERTA: aritmética infija ausente

**Reproducción:** bloque 1.1 del arnés; mismo filtro con `a.x + 1`, `a.x - 1`, `a.x * 2` y control `mas(a.x, 1)`.

```text
ErrorSintaxis: línea 3, columna 15: se esperaba expresión; llegó '+'
ErrorSintaxis: línea 3, columna 15: se esperaba expresión; llegó '-'
ErrorSintaxis: línea 3, columna 15: se esperaba expresión; llegó '*'
['donde', ['>', ['mas', ['campo', 'a', 'x'], 1], 0]]
naval.alternancia_turnos.oracle:4: donde t2.turno == mas(t1.turno, 1) y t1.tirador == t2.tirador
naval.turnos_sin_huecos.oracle:6: donde registrados != mas(ultimo, 1)
```

**Código:** `nucleo/sintaxis.py:_tokenizar`, `_Expr`; `catalogos/escalares.py:mas/menos/por`. La prueba verifica operadores binarios, no niega la existencia de literales negativos. Hay dos medidas reales para suma; no se extrapola esa demanda a toda una familia aritmética nueva.

### 1.2 — CIERTA: pares simétricos inflan el conteo

**Reproducción:** bloque 1.2; dos filas con identificadores distintos y misma celda, más control de celdas diferentes. Se obtiene el mutante real `aflojar_umbral` de `nucleo.mutacion.mutantes`.

```text
!= rojo: valor=2, original.ok=False, aflojar_umbral.ok=False
!= verde: valor=0, original.ok=True, aflojar_umbral.ok=True
< rojo: valor=1, original.ok=False, aflojar_umbral.ok=True
< verde: valor=0, original.ok=True, aflojar_umbral.ok=True
```

**Código:** `nucleo/algebra.py:desde`, `nucleo/mutacion.py`; `docs/decisiones/DECISION-001-RELACIONES-COMO-BOLSAS.md`. Con `!=` el mutante sobrevive a ambas polaridades; con `<` muere. La multiplicidad es semántica deliberada de bolsas. Usar `<` exige una clave comparable que distinga el par; el ejemplo ya tiene identificadores de barcos, no demuestra que siempre haya que inventar un campo artificial.

### 2.1 — CIERTA, acotada: falta contar distintos por grupo directamente

**Reproducción:** bloque 2.1; catálogo de agregados, intento de `contar_distintos(a.x)` y doble agrupación de tres filas, dos de ellas repetidas.

```text
AGREGADOS = ['contar', 'max', 'min', 'promedio', 'suma']
MedidaMalDeclarada: demo.prueba: agregado desconocido: «contar_distintos» (hay ['contar', 'max', 'min', 'promedio', 'suma'])
doble agrupar: 2 ({'_': {'grupo': 'A', 'distintos': 2}},)
```

**Código:** `nucleo/algebra.py:AGREGADOS`, validación de agregados y `desde`; `nucleo/sintaxis.py:_leer_agregado`. La duplicación de claves del ejemplo por barco es real. “La única forma” es demasiado amplio: un conteo global puede deduplicar con un solo `agrupar` y terminar con `resumen contar(1)`. La cantidad de mutantes o la necesidad de casos en ambos ejes no constituye por sí sola un defecto del álgebra.

### 2.2 — FALSA como impedimento general para requiere o filtros compuestos

**Reproducción:** bloque 2.2; expansión y evaluación de las tres macros base con una conjunción, intento de agregar `requiere` a `ninguno` y lectura completa de las dos medidas navales citadas.

```text
macros: ['ninguno', 'ninguno-par', 'ninguno-requiere', 'peor']
ninguno requiere= () filtro compuesto valor= 1
ninguno-requiere requiere= ('dato',) filtro compuesto valor= 1
ninguno-par requiere= () filtro compuesto valor= 1
ErrorSintaxis: línea 7, columna 1: la macro ninguno lleva exactamente 5 líneas de cuerpo (de, donde, umbral, ambito, alcance) y llegaron 6
```

**Código:** `nucleo/macros/ninguno-requiere.oracle:4`, `nucleo/sintaxis.py:_leer_macro_por_plantilla`, `nucleo/macro.py:expandir`; `docs/decisiones/DECISION-003-SIN-PARAMETROS-OPCIONALES-EN-DEFMACRO.md`.

La rigidez de **esa** plantilla es cierta, pero ya existe una hermana para exigir la relación recorrida. Las macros admiten predicados compuestos. Además, `naval.flota_reglamentaria` y `naval.turnos_sin_huecos` tienen `agrupar` y agregados propios: **no** están expandidas “únicamente para incluir requiere”. Ninguna de esas macros es una tubería arbitraria con `sin`; esa restricción sigue existiendo, pero no justifica el diagnóstico general ni parámetros opcionales. No se propone trabajo a partir de esta entrada falseada.

### 3.1 — CIERTA: requiere tiene una posición fija

**Reproducción:** bloque 3.1; insertar la misma cláusula antes de `resumen`, antes de `umbral` y después de `umbral`.

```text
requiere antes de resumen
ErrorSintaxis: línea 4, columna 5: se esperaba línea «resumen»; llegó 'requiere dato'
requiere antes de umbral
ErrorSintaxis: línea 5, columna 5: se esperaba línea «umbral»; llegó 'requiere dato'
requiere antes de ambito
('dato',)
```

**Código:** `nucleo/sintaxis.py:_leer_medida`, especialmente 1226–1268. Es una restricción de escritura reproducible; no se propone reordenar pasos de tubería, cuyo orden sí tiene significado.

### 3.2 — FALSA: no se exige NO en mayúsculas

**Reproducción:** bloque 3.2; cargar `alcance "no ve otros datos"`, ejecutar la medida meta real y buscar invocaciones de `contiene` tanto en JSON como en `.oracle` en los tres catálogos.

```text
alcance= no ve otros datos ; meta.ok= True
Oracle usos contiene: []
Jam usos contiene: []
LyraGASP usos contiene: []
```

(Las rutas completas figuran en la salida.) **Código:** `catalogos/meta/meta.ninguna_medida_sin_alcance.oracle` sólo busca texto vacío; `nucleo/medida.py:de_datos` exige texto no vacío. El docstring de la escalar no es una llamada. Confirma la revisión previa.

### 4.1 — CIERTA: no hay superficie declarativa de relaciones

**Reproducción:** bloque 4.1; cargar un archivo `dato.oracle` con `relacion dato:` y luego con JSON canónico.

```text
RelacionMalDeclarada: …/dato.oracle: JSON inválido — Expecting value: line 1 column 1 (char 0)
JSON dentro de .oracle: ['relacion', 'dato', ['campos', ['campo', 'x', 'entero', 'celdas']], ['alcance', 'no ve otros datos']]
```

**Código:** `nucleo/relacion.py:54,313–325`. Matiz: las extensiones `.oracle` y `.relacion` **sí** se admiten, pero todas pasan por `json.loads`; cambiar el sufijo no da sintaxis nueva. No es cierto que deba escribirse todo a mano: `oracle relaciones --escribir` ya genera borradores en `relaciones-por-revisar/` (`tools/medida.py`, `CARPETA_POR_REVISAR`). Eso reduce autoría de JSON; no constituye una superficie infija.

### 4.2 — CIERTA como deuda; causalidad no demostrada

**Reproducción:** bloques de Jam/LyraGASP; `hechos_de_unidades` sobre catálogo y relaciones efectivos, seguido de la medida meta vigente.

```text
Jam:      cota=51 valor=51 ok=False
LyraGASP: cota=61 valor=61 ok=False
```

**Código:** `nucleo/unidad.py:hechos_de_unidades`; `catalogos/meta/meta.toda_cantidad_comparada_tiene_unidad_derivable.oracle`; ambas configuraciones externas. Son comparaciones sin unidad derivable, no 112 relaciones faltantes. La prueba confirma la deuda y que sombra no deja de medirla. No demuestra que la causa sea escribir JSON; también faltan decisiones de dominio y unidades de escalares. Una nueva sintaxis no decidiría esas unidades.

### 4.3 — CIERTA como deuda de migración

**Reproducción:** mismos bloques; ejecutar `meta.todo_umbral_declara_de_donde_sale` sobre `como_hechos(cat.values())` y leer los dos ejemplos citados.

```text
Jam:      cota=41 valor=41 ok=False
vault.enlace_resuelve segun= sin_declarar
LyraGASP: cota=27 valor=27 ok=False
recarga.montage_en_slot_cuerpo_entero segun= sin_declarar
```

**Código:** `nucleo/medida.py:SEGUN_SIN_DECLARAR`, `de_datos`; medida meta homónima. `segun` no es obligatorio para que cargue un archivo histórico: la compatibilidad le asigna `sin_declarar` y la política lo señala. El trabajo pendiente es justificar 68 umbrales, no inventar otra cláusula.

### 5.1 — FALSA: .caso representa relaciones vacías

**Reproducción:** bloque 5.1; imprimir y releer un caso con `{'impacto': []}`. Además pasó el test `test_una_relacion_presente_y_vacia_no_es_una_relacion_ausente`.

```text
    evidencia:
        impacto:
relectura evidencia= {'impacto': []}
```

**Código:** `nucleo/caso.py:_lineas_relacion` (rama sin hechos, 178–179), `_Parser._leer_evidencia`. Debe omitirse el encabezado de campos, **no la relación**. `git log -S 'if not hechos:' -- nucleo/caso.py` remite a `5219e6e` (25/08, incorporación de la superficie), anterior a la guía. Se clasifica falsa, no como una corrección posterior de 0.28.0. No se necesita `impacto: []` como forma nueva.

### 5.2 — CIERTA, acotada: falta un recorrido directo desde captura a caso observado

**Reproducción:** bloques 5.2; medir deuda actual, consultar los verbos públicos y convertir un caso de 1000 filas con `caso.imprimir`/`caso.leer`.

```text
Jam:      meta.la_medida_no_se_fija_solo_con_evidencia_fabricada cota=16 valor=16 ok=False
LyraGASP: meta.la_medida_no_se_fija_solo_con_evidencia_fabricada cota=17 valor=17 ok=False
meta.todo_caso_observado_declara_de_donde_salio valor=94 ok=False
1000 filas: leer(imprimir(datos)) == datos: True
oracle caso: nuevo, listar, generar
```

**Código:** `tools/cli.py:cmd_caso*`, `nucleo/caso.py:imprimir`, `cargar_fuente_caso`; `nucleo/marco.py:hechos_de_casos`. No existe un verbo de importar una captura observada entre los verbos actuales. Sigue siendo necesario armar los metadatos y asociar la medida/polaridad. Es falso que la superficie sea incapaz de manejar tablas grandes o que haya que transcribirlas: el impresor hace la conversión sin pérdida. La deuda no prueba que los usuarios tengan capturas disponibles: Jam/LyraGASP mencionan sensores y editor abierto; las 94 procedencias históricas de Oracle no pueden inventarse a posteriori.

### 5.3 — CIERTA: el generador no resuelve toda restricción de dominio

**Reproducción:** bloque 5.3 extrae de GUIA22 la medida exacta de superposición, la carga en un proyecto temporal y llama `generar_caso`, que usa el CLI.

```text
generación no posible: flota.dos_barcos_en_la_misma_celda: no se pudo fabricar verde_correcto con contar y umbral <= 0; la evidencia propuesta da valor 4, verde=False. Hace falta evidencia del dominio — no se escribió ningún archivo
exit= 1 archivos corpus= []
```

**Código:** `nucleo/generador.py:fabricar_filas`, `fabricar_candidatos`, `generar_caso`; tests de `TestUmbralDeclarado`. Coincide con la salida citada. Es una limitación real del generador, con rechazo seguro y diagnóstico útil; no prueba la necesidad de un solucionador general ni de un operador nuevo.

### 6.1 — CIERTA para los comandos que cargan el catálogo

**Reproducción:** bloque 6.1; proyecto temporal con medidas que no usan escalares y un `escalares.py` que sólo contiene un comentario. Se invocan los cinco comandos citados con argumentos completos.

| Comando sin confianza | Exit | Resultado |
|---|---:|---|
| `test --rapido` | 1 | `ESCALARES EXTERNAS NO EJECUTADAS`; veredicto rojo |
| `juzgar --con hechos.json` | 2 | `ESCALARES EXTERNAS NO EJECUTADAS` |
| `revisar catalogos/demo.oracle` | 1 | `ESCALARES EXTERNAS NO EJECUTADAS` |
| `medida listar` | 1 | `ESCALARES EXTERNAS NO EJECUTADAS` |
| `caso generar demo.prueba` | 1 | traceback `EscalaresNoConfiables` |
| `medida listar --confiar-escalares` | 0 | muestra las dos medidas |
| `caso listar` | 0 | `CORPUS: 0 casos en corpus` |

**Código:** `nucleo/proyecto.py:escalares_del_proyecto` (494), `tools/cli.py`, `tools/corpus.py:generar`. La existencia del archivo dispara la exigencia sin inspeccionar si se usa una función. No afecta a absolutamente todos los comandos. El traceback de `caso generar` es un hallazgo adicional reproducido dentro del mismo recorrido. No se propone eliminar el consentimiento para ejecutar Python externo.

### 6.2 — VENCIDA: juzgar ya nombra las medidas propias no aplicadas

**Reproducción:** bloque 6.2; dos medidas propias, evidencia para una sola. Pasaron también los cuatro tests de `NoAplicadasTests` (CLI texto/JSON y Motor).

```text
exit=0
NO SE APLICARON (1) — su relación no vino en la evidencia:
  · demo.prueba: falta dato
```

Si ninguna aplica, el control anterior da exit 1 y `SIN MEDIDAS APLICABLES`. **Código:** `tools/juzgar.py`, `nucleo/medida.py:Informe`; `ESPECIFICACION.md`, corte 0.27.0. La corrección informa las omitidas, no convierte toda omisión parcial en fallo. Confirma la revisión previa; no reabrirla.

### 6.3 — VENCIDA en sus problemas de entrada y alcance; causalidad falsa/no acreditada

**Reproducción:** bloque 6.3; repetir el experimento del postmortem en una copia del laboratorio con código intacto, `game.js` roto y sin el caso. Pasaron `tests.test_test_alcance` y `tests.test_primer_valor`.

```text
conservado / game.js roto: exit=0
ALCANCE: verificación de medidas contra casos guardados del corpus.
PRODUCTO: sin nueva medición; la aceptación no reejecuta los comandos de origen ni el producto. El resultado no certifica su estado actual.
VEREDICTO: VERDE (se salteó: mutación de medidas (--rapido))
sin casos: exit=0
VEREDICTO: SIN MEDICIÓN (advertencia: proyecto vacío: 0 medidas propias, 0 casos, 0 fixtures diferenciales)
```

**Código y documentación:** `tools/cli.py:cmd_test`, `docs/13-primer-valor.md`, `ejemplo/primer-valor`, `ESPECIFICACION.md`, corte 0.28.0. Las tareas `test-alcance` y `primer-valor`, consultadas por CLI, están CERRADAS e integradas. El verde de un corpus conservado sigue siendo posible con producto roto; ahora declara exactamente ese límite, por diseño.

El postmortem **niega** que haya evidencia para el 60 % de atención o para atribuir causalmente el resultado al ritual de Oracle. No se puede reproducir atención humana con un test del parser ni deducirla de la comparación de juegos. Las obligaciones de esta sesión en AGENTS.md no convierten el tracker en requisito del lenguaje. No queda acreditada una fricción general adicional que justifique cambios; no se agrupa esta entrada como cierta.

## Agrupación exclusiva de las ciertas y forma mínima

Quedan **10 ciertas (varias con alcance corregido), 3 falsas y 2 vencidas**. Las cinco descartadas son 2.2, 3.2, 5.1, 6.2 y 6.3. Las estimaciones de dolor/costo siguientes son juicio de priorización, no mediciones de productividad.

Versiones de referencia: álgebra **0.8**, sintaxis **0.6**. “Sin cambio” significa conservar ambas; puede haber una entrega de distribución. Una extensión compatible de superficie sube la menor de sintaxis a **0.7** si fuera la siguiente; no se suma una versión por cada propuesta. Ningún grupo exige hoy un operador algebraico nuevo.

| Orden | Grupo y entradas ciertas | Forma más chica propuesta | Dolor / costo | Impacto de versión |
|---:|---|---|---|---|
| 1 | Invocación y diagnóstico, 6.1 | Receta de un wrapper **local del proyecto** que pase explícitamente proyecto y confianza a cada comando; corregir en CLI el traceback de `caso generar` para dar el mismo mensaje breve que el resto. No persistir confianza implícita global. | Alto: cinco rutas afectadas / bajo | Álgebra 0.8, sintaxis 0.6, sin cambio. |
| 2 | Captura a corpus, 5.2 | Receta ejecutable corta: leer el JSON del sensor, añadir metadatos aportados por el autor, elegir medida y etiqueta, guardar JSON o usar `caso.imprimir`. Sin volver a escribir filas ni ejecutar automáticamente el comando de origen. Sólo proponer un verbo si esa receta resulta insuficiente al probarla. | Alto: 16/17 medidas pendientes más deuda histórica distinta / bajo para autoría; obtener observaciones puede ser costoso | Ambas sin cambio: formatos y evaluación existentes. |
| 3 | Ubicación de metadatos, 3.1 | Error contextual que diga «requiere va después de umbral y antes de ambito/alcance», mostrando la línea correcta. Conserva el orden; resuelve el bloqueo de diagnóstico, no promete escritura libre. | Medio / muy bajo | Ambas sin cambio. Aceptar nuevos órdenes, si se pidiera después, sería sintaxis 0.7, álgebra igual. |
| 4 | Pares y distintos, 1.2 + 2.1 | Dos recetas copiables con controles: clave ordenable `<` para pares no orientados y doble `agrupar` para distintos por grupo. Una macro local de aridad fija sólo cuando dos medidas repitan realmente la misma plantilla. | Medio / bajo | Ambas sin cambio. No cambiar multiplicidad de `unir` ni agregar `contar_distintos` con un único usuario demostrado. |
| 5 | Esquemas y unidades, 4.1 + 4.2 | Para bajar deuda ahora, usar borradores existentes de `relaciones --escribir` y completar unidades/alcance por relación. Eso no elimina JSON. Para resolver específicamente escribir relaciones sin JSON, la mínima extensión sería un lector superficial que traduzca nombre, campos, tipos, unidades y alcance al mismo AST, sin inferir unidades. No implementar ambas vías por anticipado. | Alto en deuda; costo bajo de andamiaje, medio de decisiones de dominio; medio/alto para nueva superficie | Borradores/migración: ambas iguales. Superficie nueva: sintaxis 0.7 y álgebra 0.8; requiere compatibilidad y round-trip, no nuevo operador. |
| 6 | Umbrales históricos, 4.3 | Revisar la procedencia de cada umbral y completar `segun` en los datos; reducir cotas sólo después de medir. Ninguna macro puede adivinar contrato/convención/medición/tanteo. | Alto en volumen, bajo por edición pero decisión humana necesaria | Ambas sin cambio. |
| 7 | Suma ordinal, 1.1 | Si se prioriza quitar la notación prefija, azúcar **sólo para `+` binario**, traducido a la llamada `mas` ya existente; fijar precedencia y conservar la resolución normal de escalares. No agregar `-`, `*`, `/` por simetría sin segundos usos verificados. | Medio: dos medidas concretas / medio (parser, impresor, mapa, compatibilidad) | Sintaxis 0.7; álgebra 0.8 si es exactamente la llamada existente. No crear un primitivo aritmético nuevo bajo el nombre de azúcar. |
| 8 | Generación geométrica, 5.3 | Nada en el lenguaje ni solucionador general. Conservar el rechazo seguro; escribir el pequeño caso de dominio verde y rojo a partir de la receta de pares. | Localizado / bajo para el ejemplo; muy alto un solver general | Ambas sin cambio. |

La propuesta de suma satisface dos consumidores concretos. La de distintos sólo tiene un patrón por barco demostrado: no cumple la regla para agregar un agregado. Las macros hermanas existentes resuelven el caso básico de `requiere`; no se propone revertir la decisión 003. Una nueva sintaxis de relaciones mejora escritura, pero no se presenta como cura automática de las 112 comparaciones sin unidad.

## Tres propuestas registradas, sin implementación

1. [20260923-173938-ergo-confianza](../20260923-173938-ergo-confianza/TAREA.md): wrapper explícito y diagnóstico de confianza sin traceback.
2. [20260923-173938-ergo-observados](../20260923-173938-ergo-observados/TAREA.md): receta de captura JSON a caso observado con metadatos reales.
3. [20260923-173938-ergo-orden](../20260923-173938-ergo-orden/TAREA.md): explicar dónde mover `requiere`.

Son propuestas abiertas, no implementaciones autorizadas en este trabajo. Los grupos restantes quedan como alternativas pendientes de priorización en la tarea ergonomia. No se crean duplicados de las tareas ya cerradas ni trabajo para las afirmaciones falsas. Las correcciones al inventario y a la guía externa se señalan aquí; no se modifican sus fuentes históricas.
