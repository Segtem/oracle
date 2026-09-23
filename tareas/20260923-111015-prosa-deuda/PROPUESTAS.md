# Propuestas de reescritura de defensas de umbral insuficientes

Este documento contiene las propuestas de reescritura para subsanar la deuda de prosa en las defensas de umbral (`porque`), identificadas a partir de la segunda corrida del juez ciego en `tareas/20260922-220029-jev-porque-v2/` (`comparaciones.json` y `juicio-ciego-claude.json`).

## Desglose de los 18 registros marcados insuficientes

El experimento a ciegas evaluó un lote de 25 registros opacos contra el criterio P1 (origen del valor). De ellos, 18 fueron marcados como insuficientes (`claude=false`):

1. **10 controles sintéticos** (`control=true`): registros degradados a propósito por el arnés experimental con fórmulas vacías («Porque sí.», «Es lo razonable.», «Es lo que corresponde.», «Porque se decidió así.», «Es el número adecuado.»). No son medidas con prosa defectuosa en el catálogo: de hecho, cinco de sus medidas base ya contaban con defensas genuinas aprobadas (`claude=true`) en la misma corrida, y las otras cinco coinciden con las medidas reales examinadas abajo.
2. **8 medidas reales del catálogo** (`control=false` y `claude=false`): medidas auténticas de Oracle cuya prosa original explicaba el perjuicio, el costo o la conveniencia, pero no enunciaba la regla universal, fuente o cálculo del cual se deduce estrictamente el valor del umbral (`<= 0`).

A continuación se presentan las 8 propuestas de redacción sobre las medidas reales para revisión de Brian y Claude. Ninguna medida del catálogo ha sido modificada.

---

## 1. `meta.toda_medida_filtra_o_agrupa`

- **Registro de prueba:** `v005` (anterior `r023`)
- **Archivo:** `catalogos/meta/meta.toda_medida_filtra_o_agrupa.oracle`
- **Tubería:**
  ```oracle
  medida meta.toda_medida_filtra_o_agrupa:
      de medida m
      unir termino t
      agrupar:
          clave medida = m.id
          agregado operadores_estructurales = suma(t.medida == m.id y (t.cabeza == "donde" o t.cabeza == "agrupar"))
      donde operadores_estructurales == 0
      resumen contar(1)
      umbral <= 0 segun convencion
  ```
- **Umbral y origen:** `<= 0 segun convencion`
- **Alcance:** *«mira la forma declarada y exige al menos un `donde` o un `agrupar`. NO juzga si el filtro discrimina bien, si el agrupamiento tiene la clave correcta ni si un conteo total fue intencional»*
- **Texto anterior:**
  > «una medida sin `donde` ni `agrupar` mide la relación completa: puede ser válida como conteo bruto, pero en el catálogo de oráculos suele significar que faltó declarar qué hecho ofende»
- **Dictamen del juez ciego (`claude: false`, P(sí) = 0.26):**
  *«La defensa concede que la forma puede ser valida como conteo bruto y solo afirma que «suele significar» un olvido: no enuncia ninguna exigencia de que toda medida declare un `donde` o un `agrupar`, ni ninguna fuente del limite.»*
- **Análisis:**
  La defensa anterior era dubitativa: concedía validez al conteo bruto y sugería que la ausencia «suele significar» un olvido. Sin embargo, la convención formal de este catálogo es estricta: un oráculo tiene por misión discriminar hechos infractores o resumir agregados estructurados; medir la relación bruta completa sin ningún `donde` ni `agrupar` no es admisible en el catálogo publicado.
  *(Nota para revisión: Si el proyecto deseara admitir conteos brutos intencionales en el catálogo sin filtros dummy, habría que **revisar el umbral** o introducir una distinción en el operador; bajo la convención actual, la regla universal exige que toda medida filtre o agrupe).*
- **Texto propuesto:**
  > «Toda medida del catálogo debe discriminar qué hecho ofende mediante al menos un filtro o una agregación: medir la relación completa sin `donde` ni `agrupar` no es una aserción de oráculo aceptable; ninguna medida sin discriminar es admisible, por lo que el límite es cero.»

---

## 2. `meta.toda_medida_esta_ejercitada`

- **Registro de prueba:** `v017` (anterior `r061`)
- **Archivo:** `catalogos/meta/meta.toda_medida_esta_ejercitada.oracle`
- **Tubería:**
  ```oracle
  ninguno meta.toda_medida_esta_ejercitada:
      de medida_en_uso m
      donde m.es_heredada == false y m.casos_que_la_evaluan == 0
      umbral <= 0 segun contrato
  ```
- **Umbral y origen:** `<= 0 segun contrato`
- **Alcance:** *«cuenta los casos del PROYECTO que la evalúan. NO exige nada de las medidas heredadas del catálogo base —de ésas responde oracle, con su propio corpus— ni ve si esos casos la ponen a prueba de verdad: para eso está la mutación. Si medida_en_uso viene vacía no hay medidas sin ejercitar y verde es correcto; además contiene una fila por medida cargada por construcción»*
- **Texto anterior:**
  > «una medida que ningún caso ni fixture evalúa nunca es decoración: está en el catálogo, se cuenta en el informe, y no puede fallar porque nadie la corre»
- **Dictamen del juez ciego (`claude: false`, P(sí) = 0.27):**
  *«Describe el perjuicio de una medida que nadie ejecuta (es decoracion, no puede fallar), pero no enuncia la exigencia de que toda medida propia sea evaluada por al menos un caso ni otra regla que fije el limite.»*
- **Análisis:**
  Expone vívidamente la consecuencia perjudicial (la medida es «decoración»), pero omite la cláusula contractual de universalidad: el contrato exige que el 100 % de las medidas propias posea cobertura ejecutada por casos. De la regla de que toda medida propia debe tener al menos un caso evaluador se deriva que la cantidad de medidas con 0 casos evaluadores debe ser cero.
- **Texto propuesto:**
  > «Toda medida propia del catálogo debe ser evaluada por al menos un caso del corpus: una medida que ningún caso ni fixture evalúa nunca no puede fallar y no aporta garantía; ninguna medida propia sin ejercitar es admisible en el catálogo, por lo que el límite es cero.»

---

## 3. `meta.el_diagnostico_no_publica_el_dominio`

- **Registro de prueba:** `v030` (anterior `r059`)
- **Archivo:** `catalogos/meta/meta.el_diagnostico_no_publica_el_dominio.oracle`
- **Tubería:**
  ```oracle
  ninguno meta.el_diagnostico_no_publica_el_dominio:
      de campo_diagnostico d
      donde d.es_del_dominio == true
      umbral <= 0 segun contrato
  ```
- **Umbral y origen:** `<= 0 segun contrato`
- **Alcance:** *«recorre los valores de texto del diagnóstico y los compara contra lo que el proyecto sabe que es suyo —ids de medidas, nombres de archivos, la raíz y el home—. NO detecta un dato del dominio que no esté en esa lista, ni juzga si un campo nuevo debería estar; de eso responde quien lo agrega»*
- **Texto anterior:**
  > «el diagnóstico existe para pegarse en un issue público: un id de medida, un nombre de archivo o una ruta con el usuario adentro se comparten sin que nadie los mire dos veces, y no se pueden despublicar»
- **Dictamen del juez ciego (`claude: false`, P(sí) = 0.20):**
  *«Describe el perjuicio de publicar datos del dominio y su irreversibilidad, pero no enuncia la exigencia de que ningun campo del diagnostico contenga datos propios ni otra regla que derive el limite.»*
- **Análisis:**
  Explica por qué compartir datos del dominio es peligroso e irreversible, pero no formula la exigencia de que ningún campo puede contenerlos. La regla contractual exige fuga cero: no se tolera ningún campo con `es_del_dominio == true`.
- **Texto propuesto:**
  > «Ningún campo del diagnóstico puede contener datos del dominio del proyecto (rutas locales, nombres de archivo o identificadores propios): el diagnóstico está diseñado para compartirse íntegro en issues públicos, por lo que la tolerancia a filtraciones es estrictamente cero.»

---

## 4. `simulacion.la_traza_no_tiene_huecos`

- **Registro de prueba:** `v044` (anterior `r024`)
- **Archivo:** `catalogos/simulacion/simulacion.la_traza_no_tiene_huecos.oracle`
- **Tubería:**
  ```oracle
  medida simulacion.la_traza_no_tiene_huecos:
      de evento e
      agrupar:
          clave corrida = e.corrida
          agregado registrados = contar(1)
          agregado ultimo = max(e.t)
      donde registrados != mas(ultimo, 1)
      resumen contar(1)
      umbral <= 0 segun convencion
  ```
- **Umbral y origen:** `<= 0 segun convencion`
- **Alcance:** *«compara cuántos eventos hay contra el instante final, asumiendo que el tiempo arranca en cero y avanza de a uno. NO ve trazas donde varios eventos comparten instante, ni sabe si el que falta es importante. Si evento viene vacío la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—.»*
- **Texto anterior:**
  > «una traza con huecos describe otra corrida que la que ocurrió: si faltan pasos, cualquier cosa que se mida sobre ella habla de lo que se registró y no de lo que pasó»
- **Dictamen del juez ciego (`claude: false`, P(sí) = 0.26):**
  *«Explica por que una traza con huecos invalida lo que se mida sobre ella, es decir el perjuicio, pero no enuncia ninguna exigencia sobre cuantas trazas con huecos se admiten ni fuente del limite.»*
- **Análisis:**
  Argumenta el perjuicio epistemológico sobre la simulación, pero no la convención matemática del conteo: el tiempo simulado avanza discretamente de a un paso desde $t=0$, por lo que la cantidad exacta de eventos en una corrida completa hasta $t_{\max}$ debe ser $t_{\max} + 1$. Ninguna corrida discontinua es aceptable.
- **Texto propuesto:**
  > «Toda corrida bajo simulación debe registrar una secuencia temporal continua: con tiempo discreto desde t=0 en pasos unitarios, la cantidad de eventos registrados debe ser exactamente max(t) + 1; ninguna corrida con pasos omitidos o huecos temporales es admisible, luego el límite es cero.»

---

## 5. `proceso.verificador_sin_falsos_rojos`

- **Registro de prueba:** `v053` (anterior `r068`)
- **Archivo:** `catalogos/proceso/proceso.verificador_sin_falsos_rojos.oracle`
- **Tubería:**
  ```oracle
  ninguno proceso.verificador_sin_falsos_rojos:
      de hallazgo h
      donde h.era_real == false
      umbral <= 0 segun contrato
  ```
- **Umbral y origen:** `<= 0 segun contrato`
- **Alcance:** *«ve hallazgos que YA fueron etiquetados como falsos. NO puede decidir sola si un hallazgo es real: alguien tuvo que mirarlo. Si hallazgo viene vacía significa que el verificador no reportó nada, por lo que el mundo está limpio de falsos rojos»*
- **Texto anterior:**
  > «un falso rojo enseña a ignorar el verificador, y eso lo vuelve peor que no tener ninguno»
- **Dictamen del juez ciego (`claude: false`, P(sí) = 0.09):**
  *«Describe el dano que causa un falso rojo, que es importancia, sin enunciar cuantos se admiten ni de donde sale el limite.»*
- **Análisis:**
  Es el caso paradigmático citado en `TAREA.md`: explica la gravedad del daño, pero no enuncia que bajo el contrato del verificador no se admite ningún falso rojo ya catalogado como tal.
- **Texto propuesto:**
  > «Todo hallazgo reportado por el verificador debe corresponder a un defecto real: un falso rojo enseña a ignorar las alarmas; bajo el contrato del verificador, ningún hallazgo confirmado como falso (`era_real == false`) es admisible, por lo que el umbral es estrictamente cero.»

---

## 6. `meta.el_caso_reclama_una_medida_que_existe`

- **Registro de prueba:** `v055` (anterior `r070`)
- **Archivo:** `catalogos/meta/meta.el_caso_reclama_una_medida_que_existe.oracle`
- **Tubería:**
  ```oracle
  ninguno meta.el_caso_reclama_una_medida_que_existe:
      de caso c
      donde c.tiene_medida == true y c.medida_existe == false
      umbral <= 0 segun contrato
  ```
- **Umbral y origen:** `<= 0 segun contrato`
- **Alcance:** *«mira todos los casos, propios y heredados, y ve el id que cada caso RECLAMA: un caso de biblioteca colgado puede señalar una selección incompleta del proyecto. NO confunde esto con un hueco declarado —un caso sin medida no reclama nada— y NO ve si el id que existe es el adecuado para ese caso. Si caso viene vacía no hay casos que reclamen medidas inexistentes y verde es correcto; además el arnés de aceptación exige un corpus no vacío por construcción antes de evaluar L2»*
- **Texto anterior:**
  > «un caso que apunta a una medida inexistente no fija nada y nadie se enteraría: pasaría por el corpus como si estuviera cubierto»
- **Dictamen del juez ciego (`claude: false`, P(sí) = 0.20):**
  *«Explica la consecuencia de un caso que apunta a una medida inexistente, pero no formula ninguna exigencia de universalidad ni fuente del valor.»*
- **Análisis:**
  Indica la consecuencia negativa (no fija nada y pasa inadvertido), pero no formula el requisito universal de integridad referencial del corpus: todo caso que apunte a una medida debe resolver a una medida presente.
- **Texto propuesto:**
  > «Todo caso del corpus que declare una medida debe vincular a un id existente en el catálogo: un caso con referencia inexistente no fija nada y falsea la cobertura; ninguna referencia rota o caso colgado es admisible en el corpus, de modo que el límite es cero.»

---

## 7. `proceso.verificacion_vigente`

- **Registro de prueba:** `v056` (anterior `r060`)
- **Archivo:** `catalogos/proceso/proceso.verificacion_vigente.json`
- **Tubería:**
  ```json
  [
    "ninguno",
    "proceso.verificacion_vigente",
    "cambio",
    "c",
    ["==", ["campo", "c", "es_codigo_vivo"], true],
    ...
  ]
  ```
- **Umbral y origen:** `<= 0 segun contrato`
- **Alcance:** *«cuenta cambios marcados como código vivo. En v0.1 NO compara fechas ni sabe cuál verificación quedó vieja: cualquier cambio vivo la invalida. Hace falta comparar contra el commit de la verificación. Si cambio viene vacía significa que no hubo cambios recientes, por lo que la verificación sigue vigente»*
- **Texto anterior:**
  > «un «corrió verde» es una foto con fecha; si después se tocó código vivo la foto es de otro código, y afirmarla es mentir»
- **Dictamen del juez ciego (`claude: false`, P(sí) = 0.33):**
  *«Expone el perjuicio —afirmar una verificacion vieja es mentir— sin enunciar ninguna regla sobre cuantos cambios de codigo vivo se admiten ni fuente del limite.»*
- **Análisis:**
  Describe el perjuicio de afirmar una verificación obsoleta («es mentir»), pero omite la regla estricta de caducidad: la vigencia de una verificación exige que no haya mediado ninguna modificación sobre código vivo tras la corrida. Un solo cambio invalida la aserción.
- **Texto propuesto:**
  > «Toda afirmación de verificación sólo es válida sobre el código exacto que se evaluó: cualquier modificación posterior sobre código vivo invalida la foto; ningún cambio en código vivo es admisible sin repetir la verificación, por lo que la tolerancia es cero.»

---

## 8. `proceso.sintaxis_valida_tras_edicion_masiva`

- **Registro de prueba:** `v058` (anterior `r063`)
- **Archivo:** `catalogos/proceso/proceso.sintaxis_valida_tras_edicion_masiva.oracle`
- **Tubería:**
  ```oracle
  ninguno proceso.sintaxis_valida_tras_edicion_masiva:
      de archivo a
      donde a.sintaxis_valida == false
      umbral <= 0 segun contrato
  ```
- **Umbral y origen:** `<= 0 segun contrato`
- **Alcance:** *«ve archivos marcados como no parseables. NO ve el daño que SÍ parsea: una regex puede cambiar el significado de una línea sin romper la sintaxis. Si archivo viene vacía significa que no se detectaron archivos con sintaxis rota tras la edición masiva y verde es correcto»*
- **Texto anterior:**
  > «reescribir N archivos con una expresión regular puede romper la sintaxis, y comprobar que los N siguen parseando es una línea»
- **Dictamen del juez ciego (`claude: false`, P(sí) = 0.14):**
  *«Argumenta el riesgo de la edicion masiva y la conveniencia de la comprobacion («es una línea»), sin enunciar que ningun archivo roto sea admisible ni dar fuente o calculo del limite.»*
- **Análisis:**
  Argumenta el riesgo de una regex y el costo ínfimo de comprobar («es una línea»), pero no la regla de admisibilidad: en el repositorio resultante de una transformación masiva, el 100 % de los archivos modificados debe parsear; ningún archivo con sintaxis rota es tolerable.
- **Texto propuesto:**
  > «Todo archivo modificado tras una edición masiva debe conservar sintaxis válida y parsear sin errores: reescribir con expresiones regulares puede corromper el árbol sintáctico; ningún archivo con sintaxis rota es admisible en el proyecto, luego el límite es cero.»

---

## Apéndice: Verificación de los 10 controles sintéticos

Para mayor claridad de la revisión, se detallan los 10 registros que completaron los 18 casos con `claude=false`:

| ID lote v2 | Medida real asociada | Texto evaluado en el ciego | Motivo del control |
|---|---|---|---|
| `v010` | `meta.toda_medida_declara_su_ambito` | *«Es lo razonable.»* | Prosa vacía artificial. Su texto real en el catálogo (`v046`) **dio SÍ** (`claude=true`, P(sí)=0.59). |
| `v015` | `meta.el_diagnostico_no_publica_el_dominio` | *«Porque sí.»* | Prosa vacía artificial. Su texto real se analiza arriba (`v030`). |
| `v019` | `meta.el_caso_reclama_una_medida_que_existe` | *«Es lo que corresponde.»* | Prosa vacía artificial. Su texto real se analiza arriba (`v055`). |
| `v021` | `meta.una_macro_equivale_a_su_expansion` | *«Es lo razonable.»* | Prosa vacía artificial. Su texto real en el catálogo (`v029`) **dio SÍ** (`claude=true`, P(sí)=0.50). |
| `v026` | `proceso.verificacion_vigente` | *«Porque sí.»* | Prosa vacía artificial. Su texto real se analiza arriba (`v056`). |
| `v040` | `proceso.sintaxis_valida_tras_edicion_masiva` | *«Porque se decidió así.»* | Prosa vacía artificial. Su texto real se analiza arriba (`v058`). |
| `v051` | `simulacion.la_traza_no_tiene_huecos` | *«Porque se decidió así.»* | Prosa vacía artificial. Su texto real se analiza arriba (`v044`). |
| `v064` | `meta.todo_umbral_declara_de_donde_sale` | *«Es el número adecuado.»* | Prosa vacía artificial. Su texto real en el catálogo (`v052`) **dio SÍ** (`claude=true`, P(sí)=0.51). |
| `v068` | `meta.ninguna_sombra_supera_su_cota` | *«Es lo que corresponde.»* | Prosa vacía artificial. Su texto real en el catálogo (`v024`) **dio SÍ** (`claude=true`, P(sí)=0.55). |
| `v072` | `meta.agrupar_no_agranda_la_relacion` | *«Es el número adecuado.»* | Prosa vacía artificial. Su texto real en el catálogo (`v065`) **dio SÍ** (`claude=true`, P(sí)=0.68). |

Como se observa, no existen 18 medidas del catálogo con prosa deficiente en este lote, sino exactamente **8 medidas reales**. Los 10 controles fueron señuelos negativos del arnés experimental.
