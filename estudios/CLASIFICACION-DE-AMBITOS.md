# Clasificación de ámbitos del catálogo base

**Fecha:** 2026-09-03 · **Estado:** entregable de análisis · **Contexto:** Plan 0.5.0

---

## 1. El criterio y las dos trampas

Hasta el Plan 0.5.0, «universal» significaba una sola cosa: residir físicamente en el directorio del
paquete de Oracle. Eso confundía **procedencia** con **jurisdicción**. Que una medida viaje empaquetada
no significa que sea pertinente para cualquier proyecto que consuma el catálogo base.

El quiebre empírico ocurrió cuando `meta.ninguna_exclusion_de_mutador_se_aplica_globalmente` puso a Jam en
rojo duro por una exclusión configurada en `nucleo/mutacion.py` de Oracle. Jam no tenía ninguna acción
posible en su propio repositorio para remediar ese veredicto; su única opción era abrir un issue aguas
arriba. Como fijó la `DECISION-009`: **un rojo sobre el que el receptor no puede actuar enseña a ignorar
la herramienta.**

Oracle 0.5.0 reifica el vocabulario cerrado `ambito` con dos opciones relativas al origen:

```text
universal    obliga a todo proyecto que seleccione el catálogo y aporte la evidencia
del_origen   obliga sólo cuando el proyecto evaluado es el dueño de la medida
```

El criterio para clasificar cada medida es estricto y unívoco:
**¿el proyecto que recibe el rojo tiene un remedio disponible en SU repositorio?**

Para aplicar este criterio con honestidad intelectual hay que sortear dos trampas frecuentes:
1. **El prefijo `meta.` no define el ámbito.** Por `DECISION-007`, `meta.` describe sobre qué nivel de
   representación habla el enunciado (L2 = medidas e instrumentos del marco), no quién es su dueño ni si
   es oficial o universal. Las medidas de `catalogos/meta/` se dividen naturalmente entre universales
   (reglas sobre la forma del catálogo del consumidor) y del origen (reglas sobre la fidelidad interna de
   Oracle).
2. **El sensor emisor no decide la jurisdicción.** Casi todas las relaciones L2 las computa el código de
   Oracle, incluso cuando corre dentro de Jam. Lo que decide es **de quién es la cosa descrita o su
   remedio**, no dónde se ejecuta el sensor.

---

## 2. Tabla de clasificación de las 55 medidas

| medida | ámbito | quién tiene el remedio | por qué |
|---|---|---|---|
| `meta.agrupar_no_agranda_la_relacion` | `del_origen` | Oracle | Si `agrupar` inventa filas en la traza, la falla está en el operador relacional de `nucleo/algebra.py`. |
| `meta.agrupar_sin_claves_es_el_resumen_global` | `del_origen` | Oracle | Evalúa la equivalencia algebraica sobre sondas; si discrepan, el defecto reside en el evaluador de Oracle. |
| `meta.donde_compone` | `del_origen` | Oracle | Verifica la composición matemática de filtros sobre sondas; si falla, el álgebra de Oracle no preserva la semántica. |
| `meta.donde_nunca_agrega_filas` | `del_origen` | Oracle | Si un filtro agrega filas en la traza, el evaluador de `donde` en `nucleo/algebra.py` tiene un bug. |
| `meta.el_caso_reclama_una_medida_que_existe` | `universal` | El proyecto evaluado | Si un caso referencia una medida inexistente, el proyecto corrige el caso o selecciona el catálogo faltante. |
| `meta.el_caso_se_pone_como_debe` | `universal` | El proyecto evaluado | Si un caso del corpus no arroja la polaridad esperada en este entorno, el proyecto repara su código o su medida. |
| `meta.el_diagnostico_no_publica_el_dominio` | `del_origen` | Oracle | La sanitización y redacción del diagnóstico se programa en `nucleo/diagnostico.py` de Oracle. |
| `meta.el_hueco_declarado_explica_por_que` | `universal` | El proyecto evaluado | Juzga sólo casos propios (`es_heredado == false`); el proyecto evaluado debe justificar sus propios huecos abiertos. |
| `meta.el_nivel_no_se_confunde_con_el_dominio` | `universal` | El proyecto evaluado | Si una medida propia usa el prefijo `meta.` sin medir el lenguaje, el proyecto renombra su medida en su catálogo. |
| `meta.la_medida_no_se_fija_solo_con_evidencia_fabricada` | `universal` | El proyecto evaluado | Juzga sólo casos propios; el proyecto evaluado debe aportar al menos un caso observado real para cada medida propia. |
| `meta.los_logicos_evaluan_todos_sus_operandos` | `del_origen` | Oracle | Si el evaluador cortocircuita `y` u `o`, es un defecto del motor de evaluación de AST en `nucleo/algebra.py`. |
| `meta.ningun_campo_sin_unidad_declarada` | `universal` | El proyecto evaluado | Si una relación declarada en el proyecto omitió la unidad de un campo, el proyecto la declara en `relaciones/`. |
| `meta.ningun_flotante_comparado_por_igualdad_en_un_filtro` | `universal` | El proyecto evaluado | Si una medida del proyecto compara flotantes con `==` o `!=` en un filtro, el proyecto corrige el predicado. |
| `meta.ningun_umbral_de_igualdad` | `universal` | El proyecto evaluado | Si una medida del proyecto define un umbral con `==`, el proyecto lo sustituye por una cota de orden (`<=`/`>=`). |
| `meta.ningun_umbral_flotante_de_igualdad` | `universal` | El proyecto evaluado | Si una medida del proyecto compara flotantes por igualdad exacta en el umbral, el proyecto agrega tolerancia. |
| `meta.ninguna_evidencia_declara_un_referente_sin_huella` | `universal` | El proyecto evaluado | Si un sensor emite evidencia sin huella de referente, el proyecto debe reparar la emisión de su sensor. |
| `meta.ninguna_evidencia_se_juzga_con_referente_vencido` | `universal` | El proyecto evaluado | Si un referente cambió de huella en el repositorio del proyecto, el proyecto debe regenerar la evidencia. |
| `meta.ninguna_exclusion_de_mutador_se_aplica_globalmente` | `del_origen` | Oracle | La lista `EXCLUSIONES_DE_MUTADORES` vive en `nucleo/mutacion.py` de Oracle y un consumidor no puede editarla. |
| `meta.ninguna_medida_sin_alcance` | `universal` | El proyecto evaluado | Si una medida propia omite declarar qué NO ve, el proyecto redacta el campo `alcance` en su archivo de medida. |
| `meta.ninguna_sombra_envejece_sin_revisarse` | `universal` | El proyecto evaluado | Si una sombra del proyecto supera los 90 días, el proyecto retira la sombra o resuelve la deuda en su código. |
| `meta.ninguna_sombra_sobre_una_medida_que_no_existe` | `universal` | El proyecto evaluado | Si la configuración de sombras referencia una medida eliminada o renombrada, el proyecto limpia su configuración. |
| `meta.ninguna_sombra_ya_en_verde` | `universal` | El proyecto evaluado | Si una medida ensombrecida ya da verde en el proyecto, el proyecto debe quitarla de su configuración de sombras. |
| `meta.sintaxis_casos_cubre_casos` | `del_origen` | Oracle | Evalúa reversibilidad sobre casos sintéticos generados; si falla, el defecto radica en `nucleo/caso.py` de Oracle. |
| `meta.sintaxis_casos_ida_y_vuelta` | `del_origen` | Oracle | Comprueba el isomorfismo del serializador de casos de Oracle; si pierde datos, la falla es de `nucleo/caso.py`. |
| `meta.sintaxis_cubre_algebra` | `del_origen` | Oracle | Evalúa reversibilidad sobre combinaciones sintéticas; si falla, el parser/printer de `nucleo/sintaxis.py` está roto. |
| `meta.sintaxis_ida_y_vuelta` | `del_origen` | Oracle | Comprueba si la serialización canónica de Oracle preserva AST y texto; si difieren, el defecto es de `nucleo/sintaxis.py`. |
| `meta.toda_cantidad_comparada_tiene_unidad_derivable` | `universal` | El proyecto evaluado | Si una medida compara valores sin unidad derivable, el proyecto declara la unidad en la relación o en la escalar. |
| `meta.toda_medida_de_ausencia_declara_requiere` | `universal` | El proyecto evaluado | Si una medida con patrón unir+agrupar no declara `requiere`, el proyecto agrega la relación requerida a la medida. |
| `meta.toda_medida_esta_ejercitada` | `universal` | El proyecto evaluado | Aplica sólo a medidas propias (`es_heredada == false`); el proyecto debe agregar un caso que evalúe su medida. |
| `meta.toda_medida_esta_fijada` | `universal` | El proyecto evaluado | Aplica a medidas propias con mutantes vivos; el proyecto debe incorporar casos al corpus que maten esos mutantes. |
| `meta.toda_medida_filtra_o_agrupa` | `universal` | El proyecto evaluado | Si una medida propia no tiene filtro ni agregación, el proyecto especifica qué hechos ofenden en su medida. |
| `meta.toda_opcion_del_vocabulario_declara_su_sentido` | `del_origen` | Oracle | Las opciones de vocabulario cerrado viven en `nucleo/vocabulario.py` de Oracle y sus sentidos los redacta Oracle. |
| `meta.toda_relacion_del_lenguaje_esta_en_la_referencia` | `del_origen` | Oracle | La documentación de las relaciones del lenguaje corresponde a la `ESPECIFICACION.md` publicada por Oracle. |
| `meta.toda_sombra_declara_desde_y_porque` | `universal` | El proyecto evaluado | Si una sombra en `oracle.json` omite fecha o motivo, el proyecto completa ambos campos en su configuración. |
| `meta.toda_sombra_declara_una_fecha_real` | `universal` | El proyecto evaluado | Si una sombra tiene una fecha mal formada o futura, el proyecto corrige la fecha en su configuración. |
| `meta.todo_tanteo_explica_por_que` | `universal` | El proyecto evaluado | Si una medida propia define su umbral por tanteo sin defensa en prosa, el proyecto redacta la justificación. |
| `meta.todo_umbral_declara_de_donde_sale` | `universal` | El proyecto evaluado | Si una medida propia tiene `segun: sin_declarar`, el proyecto asigna el origen del número en su archivo de medida. |
| `meta.todo_verbo_del_cli_esta_en_la_ayuda` | `del_origen` | Oracle | La correspondencia entre comandos y ayuda de `oracle --help` es responsabilidad de `tools/cli.py` de Oracle. |
| `meta.todo_vocabulario_cerrado_esta_en_el_manual` | `del_origen` | Oracle | El registro `VOCABULARIOS` forma parte de `tools/manual.py` en el árbol de código fuente de Oracle. |
| `meta.una_macro_equivale_a_su_expansion` | `del_origen` | Oracle | Verifica que el expansor de macros preserve la semántica evaluada; la corrección del mecanismo depende de Oracle. |
| `meta.unir_conmuta` | `del_origen` | Oracle | Si `unir A B` difiere de `unir B A`, el evaluador relacional de `nucleo/algebra.py` viola la conmutatividad. |
| `meta.unir_materializa_el_producto` | `del_origen` | Oracle | Si la salida de unir no equivale al producto de cardinalidades, el evaluador en `nucleo/algebra.py` pierde o duplica pares. |
| `proceso.afirmacion_declara_alcance` | `universal` | El proyecto evaluado | Si una afirmación de verificación del proyecto no declara alcance, el proyecto debe completar su delimitación. |
| `proceso.arnes_con_bytecode_frio` | `universal` | El proyecto evaluado | El proyecto evaluado debe garantizar que sus corridas de mutación invaliden el bytecode de Python antes de medir. |
| `proceso.codigo_con_mutante_que_lo_mata` | `universal` | El proyecto evaluado | Si sobrevive un mutante de código en el proyecto, el proyecto escribe un test para matarlo o lo declara equivalente. |
| `proceso.modulo_alcanzable` | `universal` | El proyecto evaluado | Si hay módulos inalcanzables desde las entradas del proyecto, el proyecto conecta dependencias o borra código muerto. |
| `proceso.modulo_con_consumidor` | `universal` | El proyecto evaluado | Si un módulo propio sólo es importado por tests, el proyecto lo integra al código de producción o lo retira. |
| `proceso.ronda_mutacion_concluyente` | `universal` | El proyecto evaluado | Si la ronda de mutación tiene timeouts o baseline fallido, el proyecto repara sus tests para que sea concluyente. |
| `proceso.sintaxis_valida_tras_edicion_masiva` | `universal` | El proyecto evaluado | Si una edición masiva dejó archivos del proyecto con sintaxis inválida, el proyecto corrige los archivos afectados. |
| `proceso.test_con_mutante_que_lo_mata` | `universal` | El proyecto evaluado | Si un mutante sobrevive sin detección conductual de los tests, el proyecto refuerza las aserciones de sus tests. |
| `proceso.verificacion_vigente` | `universal` | El proyecto evaluado | Si se modificó código vivo tras la última verificación, el proyecto reejecuta la verificación sobre el commit actual. |
| `proceso.verificador_sin_falsos_rojos` | `universal` | El proyecto evaluado | Si un verificador propio produjo hallazgos catalogados como falsos, el proyecto ajusta las reglas de su verificador. |
| `simulacion.corrida_reproducible` | `universal` | El proyecto evaluado | Si dos corridas con la misma semilla discrepan, el proyecto corrige el no determinismo en su simulación. |
| `simulacion.la_traza_no_tiene_huecos` | `universal` | El proyecto evaluado | Si la traza de eventos de la simulación tiene saltos temporales, el proyecto repara el emisor de traza o el modelo. |
| `simulacion.no_se_agoto_el_presupuesto` | `universal` | El proyecto evaluado | Si la simulación agota pasos sin converger, el proyecto incrementa el presupuesto o ajusta la convergencia. |

---

## 3. Resumen numérico y análisis de distribución

De las 55 medidas del catálogo base analizadas:

- **`universal`:** **37 medidas** (67.3 %)
- **`del_origen`:** **18 medidas** (32.7 %)

### Por qué esta proporción tiene sentido

Una distribución que arrojara 55 universales o 55 del origen delataría un colapso conceptual:

1. **Si todas fueran universales**, estaríamos ignorando la lección de `DECISION-009` y del incidente
   de Jam del 2026-09-03: estaríamos obligando a los consumidores a auditar la ayuda del CLI de Oracle,
   el registro de vocabularios en `manual.py`, la especificación de relaciones del marco, las exclusiones
   de mutadores del arnés, o la conmutatividad matemática del álgebra. El consumidor recibiría rojos
   sobre código ajeno que no puede tocar.
2. **Si todas fueran del origen**, estaríamos negando el propósito fundacional de Oracle como catálogo de
   políticas compartidas: ninguna de las guardas de calidad de catálogo (umbrales sin declarar, falta de
   alcance, filtros de igualdad en flotantes, ausencia de casos observados, sombras perpetuas) ni las
   políticas sobre el proceso de desarrollo y simulación viajarían hacia los proyectos que eligen
   incorporarlas.

La distribución observada refleja con exactitud la doble naturaleza que convive en el catálogo base:
- **37 políticas universales:** oráculos sobre cómo se escribe una medida rigurosa, cómo se fija un corpus,
  cómo se gobierna una sombra, cómo se declara una relación y cómo se verifica el código, la mutación y la
  simulación de un sistema. En todas ellas, si el proyecto consumidor infringe la regla, la solución está en
  sus manos (editar su medida, añadir un caso, borrar código muerto o limpiar su configuración).
- **18 pruebas del origen:** verificaciones de conformidad y fidelidad de la propia herramienta Oracle
  (propiedades algebraicas de los operadores relacionales, reversibilidad de los parsers e impresores,
  completitud de la ayuda y el manual, sanitización de diagnósticos y consistencia del registro de
  mutadores). En todas ellas, si la prueba falla, el defecto está en el código de Oracle y sólo los
  mantenedores de Oracle pueden repararlo.

---

## 4. Las que no están claras

A continuación se exponen con transparencia las cinco medidas cuya frontera entre `universal` y
`del_origen` genera tensiones legítimas, detallando el argumento de cada lado y la razón por la que
se adoptó la postura consignada en la tabla.

### 1. `meta.sintaxis_ida_y_vuelta`

- **Qué hace:** Para cada archivo de medida del catálogo (`catalogos/**/*.oracle` y `.json`), lee el
  archivo, lo formatea canónicamente con `sintaxis.imprimir`, lo vuelve a parsear con `sintaxis.leer` y lo
  reimprime. Comprueba que el AST releído sea idéntico al original (`releida == datos`) y que el texto
  reimpreso sea idéntico a la superficie (`reimpresa == superficie`).
- **Argumento para `universal`:** El sensor recorre las rutas físicas del proyecto evaluado
  (`proy.raiz / "catalogos"`). Si un autor en Jam escribe una medida usando una sintaxis extravagante,
  con indentación rota, claves fuera del orden estándar o literales mal formateados que el formateador
  canónico no puede estabilizar, el autor de Jam puede reformatear o corregir su archivo en su propio
  repositorio para adecuarse a la sintaxis canónica de Oracle.
- **Argumento para `del_origen` (adoptado):** La propiedad que se está midiendo no es la prolijidad del
  archivo en disco, sino la **reversibilidad del compilador de Oracle**. El sensor no compara el texto
  original con el formateado; compara si `leer(imprimir(datos)) == datos`. Si esa igualdad falla,
  significa que la herramienta generó una superficie sintáctica que luego ella misma malinterpreta o
  desfigura. Quien falló es el parser/printer de `nucleo/sintaxis.py`. El autor de Jam escribió una
  medida válida para el cargador; si la herramienta no puede garantizar la ida y vuelta canónica, Jam no
  puede reescribir la gramática de Oracle. Su única opción sería evitar una construcción válida por culpa
  de un bug del compilador. Por eso corresponde a `del_origen`.

### 2. `meta.sintaxis_casos_ida_y_vuelta`

- **Qué hace:** Análoga a la anterior, pero sobre los archivos de casos en `corpus/` usando
  `nucleo/caso.py`.
- **Argumento para `universal`:** Examina los archivos de casos locales del proyecto consumidor. Si un
  caso propio introduce estructuras en su evidencia que causan desacuerdos en la serialización, el
  proyecto podría reescribir o simplificar su caso en su carpeta `corpus/`.
- **Argumento para `del_origen` (adoptado):** Igual que con las medidas, evalúa si el serializador de
  casos de Oracle es un isomorfismo (preserva el JSON de almacenamiento y el texto canónico). Si un caso
  con evidencia válida pierde campos o altera tipos al imprimirse y releerse, el defecto está en
  `nucleo/caso.py`. Pedirle a Jam que arregle un caso que el cargador acepta pero que el printer rompe
  es trasladarle la deuda del compilador de Oracle. Corresponde a `del_origen`.

### 3. `meta.una_macro_equivale_a_su_expansion`

- **Qué hace:** Para cada caso y medida escrita mediante una macro, evalúa la medida y compara veredicto,
  valor y testigos contra la evaluación de su expansión canónica directa.
- **Argumento para `universal`:** Oracle contempla que los proyectos definan sus propias macros
  (`macros_del_proyecto(proy)`). Si Jam introduce una macro en su proyecto y esa macro expande a un
  plan de ejecución inconsistente o diverge de su especificación canónica, es Jam quien debe reparar la
  definición de su macro en su repositorio.
- **Argumento para `del_origen` (adoptado):** En la práctica actual, 19 de las 22 medidas del catálogo base
  que usan macros recurren a las macros estándar de Oracle (`peor`, `ninguno`, `ausencia`). El `porque` de la
  medida declara explícitamente el temor fundacional: «si alguna expandiera distinto de lo que su autor
  cree, todo lo escrito con ella mediría otra cosa en silencio». Si una macro estándar de Oracle expande
  divergiendo de su forma canónica al evaluarse con los casos del consumidor, el consumidor no puede
  modificar `nucleo/macro.py`. La medida audita la fidelidad del expansor del lenguaje más que la autoría
  del usuario.

### 4. `proceso.arnes_con_bytecode_frio`

- **Qué hace:** Evalúa si alguna corrida de mutación se ejecutó con bytecode caliente
  (`bytecode_frio == false`), lo que ocurre en CPython cuando un archivo se muta y restaura en el mismo
  segundo sin que el `mtime` del `.pyc` cambie.
- **Argumento para `del_origen`:** Si el proyecto evaluado utiliza el runner de mutación provisto por Oracle
  (en `tools/mutar_codigo.py` o `perfiles/python/mutacion_codigo.py`), la responsabilidad de esperar el
  segundo necesario o eliminar los archivos `.pyc` es del propio script provisto por Oracle. Si el arnés
  corre caliente, el consumidor siente que el arnés de Oracle vino fallado.
- **Argumento para `universal` (adoptado):** Es una política sobre el proceso de aseguramiento del código
  del proyecto evaluado. Si una corrida de mutación se realiza con bytecode caliente, los resultados de
  mutación del proyecto quedan desacreditados. El arnés que ejecuta la mutación en el CI o en el flujo local
  pertenece a la tubería de verificación del proyecto. El proyecto tiene a su disposición el remedio:
  configurar su ejecutor para invalidar el bytecode, limpiar caches o introducir el retardo adecuado.

### 5. `meta.el_diagnostico_no_publica_el_dominio`

- **Qué hace:** Ejecuta `oracle diagnostico` contra el proyecto actual y verifica que en ninguno de sus
  campos de salida aparezcan textos identificados como secretos del proyecto (nombres de archivo, rutas,
  raíz, home o nombres de medidas propias).
- **Argumento para `universal`:** Los secretos que se buscan son los del proyecto evaluado (`proy.raiz`,
  sus archivos y sus medidas). Si un proyecto utiliza una convención de nombres que coincide con
  identificadores del sistema o si su estructura causa colisiones, el proyecto podría revisar su
  configuración.
- **Argumento para `del_origen` (adoptado):** La redacción de rutas y la poda de claves de telemetría es
  un contrato taxativo del núcleo de Oracle (`nucleo/diagnostico.py`). Si un nuevo campo de telemetría
  agregado por Oracle se olvida de pasar por `redactar()` y publica el nombre del directorio del proyecto,
  el consumidor que corre `oracle diagnostico` no puede tocar `nucleo/diagnostico.py`. El rojo señala un
  agujero de seguridad en el comando de Oracle, y su remedio sólo puede programarse en el repositorio de
  Oracle.

---

## 5. Implicancias para las capas 2 y 3 del Plan 0.5.0

Esta clasificación proporciona la base concreta para completar la migración de las 55 medidas:

1. **Capa 2 (Carga y resolución de catálogos):**
   - Cuando un proyecto ajeno como Jam importe el catálogo base de Oracle, las **18 medidas** clasificadas
     como `del_origen` no se integrarán a su catálogo efectivo. Jam no volverá a sufrir rojos por decisiones
     de arnés, CLI o reversibilidad interna de Oracle.
   - Las **37 medidas** `universal` se cargarán plenamente y continuarán protegiendo la calidad de las
     medidas, sombras, casos y código de Jam.
2. **Capa 3 (Políticas sobre la declaración):**
   - Las 18 medidas `del_origen` requieren que sus relaciones de soporte (como `mutador_excluido`,
     `verbo_del_cli`, `opcion_del_vocabulario`, `relacion_documentada` y `campo_diagnostico`) declaren
     ámbito `del_origen`.
   - Esto permitirá que la meta-medida
     `meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias` compruebe mecánicamente que
     ninguna de estas 18 medidas intente declararse falsamente como universal, cerrando definitivamente la
     brecha de jurisdicción.
