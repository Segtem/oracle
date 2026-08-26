# Informe de Ejecución: Estructura `<sustantivo> <verbo>` en la CLI de Oracle

## Resumen Ejecutivo

Implementamos la estructura canónica `oracle <sustantivo> <verbo>` en la CLI (`tools/cli.py`), incorporamos las vistas de auditoría `oracle medida listar` (`tools/medida.py`) y `oracle caso listar` (`tools/corpus.py`), mantuvimos intactos todos los atajos históricos directos (compatibilidad hacia atrás), agregamos ayudas específicas por sustantivo que salen con código de salida 0, aseguramos que cualquier verbo o comando desconocido falle con código de salida 1 indicando los verbos disponibles, y extendimos la suite de pruebas unitarias (`tests/test_cli.py`).

Todas las 9 verificaciones de `DOCTRINA.md` y la verificación de empaquetado `tools/verificar_instalacion.py` pasan en verde con 0 mutantes supervivientes.

---

## 1. Qué cambiamos y en qué archivos

1. **`tools/medida.py`**:
   - Agregamos la función `listar(proy, argv=None) -> int` para listar todas las medidas del catálogo del proyecto (o las 37 medidas en el propio Oracle), mostrando para cada una su umbral, su estado de fijación (`N casos` o `0 casos  ⚠ SIN FIJAR`) y su alcance declarado.
   - Manejamos tanto la invocación interna como `python tools/medida.py --listar` y `python tools/medida.py listar`.
   - Actualizamos el docstring del módulo para documentar `--listar`.

2. **`tools/corpus.py`**:
   - Agregamos la función `listar(proy) -> int` para recorrer los casos del corpus, mostrando para cada uno su identificador relativo, su etiqueta y la medida que reclama (o `⚠ hueco declarado (<estado_sin_medida>)` si no tiene medida asociada).
   - Manejamos tanto la invocación interna como `python tools/corpus.py --listar` y `python tools/corpus.py listar`.
   - Actualizamos el docstring del módulo para documentar `--listar`.

3. **`tools/cli.py`**:
   - Incorporamos el ruteo canónico `oracle <sustantivo> <verbo>` para `medida`, `caso` y `proyecto`.
   - Implementamos las funciones de ayuda contextual `ayuda_medida()`, `ayuda_caso()`, `ayuda_proyecto()`, que se ejecutan al invocar `oracle <sustantivo>` o `oracle <sustantivo> --help` y retornan código `0`.
   - Implementamos validación fail-closed de verbos desconocidos: `oracle <sustantivo> <verbo_invalido>` imprime el error y la lista de verbos disponibles para ese sustantivo, retornando código `1`.
   - Agregamos los comandos `cmd_medida_listar(proy, argv)` y `cmd_caso_listar(proy)`.
   - Conservamos todos los atajos directos previos: `oracle init`, `oracle nueva`, `oracle caso <grupo/id>`, `oracle revisar`, `oracle test`, `oracle relaciones`, `oracle escalares`, `oracle expandir`, `oracle convertir`, `oracle <archivo>`.
   - Actualizamos el docstring principal y la función general de `ayuda()`.

4. **`tests/test_cli.py`**:
   - Agregamos la clase `NounVerbCliTests` que valida exhaustivamente:
     - Ayudas por sustantivo devuelven 0 y listan los verbos.
     - Verbos desconocidos devuelven 1 y listan los verbos válidos.
     - `oracle medida listar` sobre Oracle y sobre proyectos vacíos / con medidas sin fijar / con medidas fijadas.
     - `oracle caso listar` sobre Oracle (incluyendo detección de huecos) y proyectos externos.
     - Equivalencia funcional entre formas canónicas (`oracle medida nueva`, `oracle caso nuevo`, `oracle proyecto test`, etc.) y atajos directos.
     - Validación de argumentos faltantes que devuelven 1.
   - Todas las pruebas de CLI usan redirección/captura silenciosa (`self._callado`) para no ensuciar la salida de `unittest -q`.

5. **`README.md`**:
   - Actualizado mediante `python tools/cifras.py --actualizar` para reflejar las nuevas cifras de tests (658) y líneas del núcleo/herramientas.

---

## 2. Demostraciones de Funcionamiento

### A. Ayudas de Sustantivos (`oracle <sustantivo>`)

```
$ python tools/cli.py medida
oracle medida — operaciones sobre medidas del catálogo

Uso:
  oracle medida nueva <dominio.nombre>    Crea una medida con plantilla lista para editar
  oracle medida revisar <archivo>         Revisa y evalúa una medida suelta
  oracle medida listar                    Lista las medidas del catálogo con umbral, alcance y fijación
  oracle medida expandir <archivo>        Muestra la forma canónica de una macro

$ python tools/cli.py caso
oracle caso — operaciones sobre casos del corpus

Uso:
  oracle caso nuevo <grupo/id>            Crea un caso de prueba en el corpus con plantilla lista
  oracle caso listar                      Lista los casos del corpus, su etiqueta y qué medida reclaman

$ python tools/cli.py proyecto
oracle proyecto — operaciones sobre el proyecto y su entorno

Uso:
  oracle proyecto init [ruta]             Inicializa un proyecto nuevo
  oracle proyecto test [--rapido|--todo]  Ejecuta la secuencia completa de verificación
  oracle proyecto relaciones              Muestra las relaciones y campos observados
  oracle proyecto escalares               Muestra las funciones escalares y operadores
```

---

### B. Validación de Verbos Desconocidos (Código de salida 1)

```
$ python tools/cli.py medida desconocido
verbo desconocido para «medida»: desconocido
Verbos disponibles: nueva, revisar, listar, expandir
(código de salida: 1)

$ python tools/cli.py caso desconocido
verbo desconocido para «caso»: desconocido
Verbos disponibles: nuevo, listar
(código de salida: 1)

$ python tools/cli.py proyecto desconocido
verbo desconocido para «proyecto»: desconocido
Verbos disponibles: init, test, relaciones, escalares
(código de salida: 1)

$ python tools/cli.py desconocido
subcomando desconocido: desconocido
Ejecutá `oracle --help` para ver las opciones disponibles.
(código de salida: 1)
```

---

### C. `oracle medida listar` sobre el propio Oracle (37 medidas)

```
$ python tools/cli.py medida listar
CATÁLOGO (37 medidas · 35 fijadas · 2 sin fijar):

  meta.agrupar_no_agranda_la_relacion
    umbral:   <= 0
    fijación: 2 casos
    alcance:  compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción

  meta.agrupar_sin_claves_es_el_resumen_global
    umbral:   <= 0
    fijación: 3 casos
    alcance:  compara `agrupar` sin claves contra `resumen` sobre una sonda construida y sobre las medidas reales que usan `agrupar` sin claves, con la evidencia de sus casos. NO ve agrupamientos con claves ni agregados que no sean conteo. Si equivalencia viene vacía no hay fallas de equivalencia y verde es correcto; además metamorficas.py construye las sondas por construcción

  meta.donde_compone
    umbral:   <= 0
    fijación: 2 casos
    alcance:  compara dos `donde` sucesivos contra su conjunción `y` sobre una sonda construida y sobre las medidas reales que usan `donde` anidado, con la evidencia de sus casos. NO ve composiciones de más de dos filtros ni filtros con efectos de borde. Si equivalencia viene vacía no hay fallas de composición y verde es correcto; además metamorficas.py construye las sondas por construcción

  meta.donde_nunca_agrega_filas
    umbral:   <= 0
    fijación: 2 casos
    alcance:  compara el conteo antes y después de cada `donde` sobre las evaluaciones que se trazaron. NO ve si las filas que quedaron son las correctas —sólo cuántas—, ni cubre una evaluación que no se corrió bajo traza. Si paso viene vacía no hay filtros que agranden la relación y verde es correcto; además trazar.py garantiza pasos trazados por construcción

  meta.el_caso_reclama_una_medida_que_existe
    umbral:   <= 0
    fijación: 0 casos  ⚠ SIN FIJAR
    alcance:  cuenta casos cuyo campo `medida` no está en el catálogo del proyecto. NO ve si la medida elegida es la que de verdad corresponde al defecto (para eso está la etiqueta del caso), y NO juzga los casos que no declaran medida (`null`). Si caso viene vacía no hay casos que reclamen medidas inexistentes y verde es correcto; además contiene una fila por caso cargado por construcción

  meta.el_caso_se_pone_como_debe
    umbral:   <= 0
    fijación: 2 casos
    alcance:  ve si el valor obtenido coincide con el umbral declarado en la medida. NO juzga si el caso es realista ni si la evidencia es suficiente

  meta.el_hueco_declarado_explica_por_que
    umbral:   <= 0
    fijación: 3 casos
    alcance:  ve si el campo `estado_sin_medida` está presente cuando `medida` es null. NO juzga si la justificación es válida ni si el caso debería tener medida ya

  meta.el_nivel_no_se_confunde_con_el_dominio
    umbral:   <= 0
    fijación: 2 casos
    alcance:  ve si el prefijo del id coincide con la carpeta donde está guardada. NO juzga si el nombre de la carpeta es el correcto

  meta.los_logicos_evaluan_todos_sus_operandos
    umbral:   <= 0
    fijación: 2 casos
    alcance:  cuenta operandos evaluados contra los declarados en el AST, en cada `y` y cada `o` trazado. NO ve si el valor de cada operando es correcto, y no cubre una evaluación que se corrió sin traza. Si nodo viene vacía no hay cortocircuitos observados y verde es correcto; además trazar.py garantiza nodos trazados por construcción

  meta.ningun_umbral_de_igualdad
    umbral:   <= 0
    fijación: 2 casos
    alcance:  mira el operador declarado en el catálogo. NO ve si una medida compuesta simula igualdad combinando dos desigualdades

  meta.ningun_umbral_flotante_de_igualdad
    umbral:   <= 0
    fijación: 3 casos
    alcance:  ve el tipo del límite declarado y el operador. NO ve si un valor entero fue calculado con punto flotante en el arnés

  meta.ningun_umbral_sin_defensa
    umbral:   <= 0
    fijación: 2 casos
    alcance:  ve si el campo `porque` está vacío. NO juzga si la justificación es buena

  meta.ninguna_medida_sin_alcance
    umbral:   <= 0
    fijación: 2 casos
    alcance:  ve si el campo `alcance` está vacío. NO juzga si el alcance es honesto ni si cubre todos los límites

  meta.sintaxis_casos_cubre_casos
    umbral:   <= 0
    fijación: 2 casos
    alcance:  compara serialización JSON contra superficie sobre casos sintéticos con todos los campos y combinaciones. NO ve si los valores de los campos son semánticamente válidos. Si equivalencia viene vacía no hay fallas de cobertura y verde es correcto; además metamorficas.py construye las sondas por construcción

  meta.sintaxis_casos_ida_y_vuelta
    umbral:   <= 0
    fijación: 2 casos
    alcance:  compara serialización JSON contra superficie sobre los casos reales del corpus. NO ve casos que no estén en el corpus. Si equivalencia viene vacía no hay fallas de ida y vuelta y verde es correcto; además corpus.py garantiza casos válidos por construcción

  meta.sintaxis_cubre_algebra
    umbral:   <= 0
    fijación: 3 casos
    alcance:  compara parseo de superficie contra AST JSON sobre medidas sintéticas generadas exhaustivamente. NO ve combinaciones de más de 3 niveles de anidamiento. Si equivalencia viene vacía no hay fallas de cobertura y verde es correcto; además metamorficas.py construye las sondas por construcción

  meta.sintaxis_ida_y_vuelta
    umbral:   <= 0
    fijación: 4 casos
    alcance:  compara parseo de superficie contra AST JSON sobre las medidas reales del catálogo. NO ve medidas con errores de sintaxis que no cargan. Si equivalencia viene vacía no hay fallas de ida y vuelta y verde es correcto; además el catálogo garantiza medidas parseables por construcción

  meta.toda_medida_de_ausencia_declara_requiere
    umbral:   <= 0
    fijación: 3 casos
    alcance:  detecta medidas cuya forma canónica contiene `unir` y `agrupar` pero ningún nodo `requiere`. NO demuestra que toda medida con ese patrón sea realmente de ausencia, ni que la relación requerida elegida sea la correcta

  meta.toda_medida_esta_ejercitada
    umbral:   <= 0
    fijación: 0 casos  ⚠ SIN FIJAR
    alcance:  cuenta los casos del PROYECTO que la evalúan. NO exige nada de las medidas heredadas del catálogo base —de ésas responde oracle, con su propio corpus— ni ve si esos casos la ponen a prueba de verdad: para eso está la mutación. Si medida_en_uso viene vacía no hay medidas sin ejercitar y verde es correcto; además contiene una fila por medida cargada por construcción

  meta.toda_medida_esta_fijada
    umbral:   <= 0
    fijación: 0 casos  ⚠ SIN FIJAR
    alcance:  exige al menos un mutante y ninguno vivo sólo cuando `debe_tener_mutantes` es verdadero. NO vuelve a exigirlos a medidas heredadas —responde su corpus de origen— ni a las evaluadas aparte, y NO ve los mutadores que nadie escribió. Si medida_en_uso viene vacía no hay medidas sin fijar y verde es correcto; además contiene una fila por medida cargada por construcción

  meta.toda_medida_filtra_o_agrupa
    umbral:   <= 0
    fijación: 4 casos
    alcance:  mira la forma declarada y exige al menos un `donde` o un `agrupar`. NO juzga si el filtro discrimina bien, si el agrupamiento tiene la clave correcta ni si un conteo total fue intencional

  meta.una_macro_equivale_a_su_expansion
    umbral:   <= 0
    fijación: 3 casos
    alcance:  compara cada medida escrita por macro contra su expansión canónica, con la evidencia real de sus casos de corpus. NO ve las macros sin ningún caso que las use, ni una expansión que sea consistentemente equivocada: si la macro siempre expande mal de la misma manera, las dos formas coinciden y esta medida calla

  meta.unir_conmuta
    umbral:   <= 0
    fijación: 3 casos
    alcance:  compara `unir A B` contra `unir B A` sobre una sonda construida y sobre las medidas reales que usan `unir`, con la evidencia de sus casos. NO ve `unir` anidados de más de dos lados ni el costo: dos formas equivalentes pueden materializar el mismo producto con presupuestos muy distintos. Si equivalencia viene vacía no hay fallas de conmutatividad y verde es correcto; además metamorficas.py construye las sondas por construcción

  meta.unir_materializa_el_producto
    umbral:   <= 0
    fijación: 2 casos
    alcance:  compara el tamaño de la salida contra el producto de los dos lados. NO ve si los pares que armó son los correctos ni en qué orden salieron; un `unir` que devuelve la cantidad justa de pares equivocados pasa. Si producto viene vacía no hay productos defectuosos y verde es correcto; además trazar.py garantiza productos trazados por construcción

  proceso.afirmacion_declara_alcance
    umbral:   <= 0
    fijación: 3 casos
    alcance:  ve si el campo está VACÍO. NO ve si el alcance escrito es honesto, completo ni pertinente

  proceso.arnes_con_bytecode_frio
    umbral:   <= 0
    fijación: 2 casos
    alcance:  ve la corrida que lo declara. NO ve otras formas de caché: módulos ya importados en memoria, o un import hecho por otro test antes de la mutación. Si corrida_mutacion viene vacía significa que no hubo corridas con bytecode caliente en la sesión y verde es correcto

  proceso.codigo_con_mutante_que_lo_mata
    umbral:   <= 0
    fijación: 5 casos
    alcance:  cuenta mutantes de código de la ronda cuyo estado fue «pasaron» sin estar declarados como equivalentes. NO ve los mutadores que nadie escribió ni los operadores que el perfil de mutación no contempla: un mutante que no existe no puede sobrevivir. Tampoco juzga por sí sola si la ronda fue concluyente —eso lo mide proceso.ronda_mutacion_concluyente— ni si el bytecode estaba frío. Si mutante viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—

  proceso.modulo_alcanzable
    umbral:   <= 0
    fijación: 4 casos
    alcance:  sigue los imports estáticos desde las entradas declaradas, y descuenta los `__init__.py` vacíos, que son marcadores de paquete. NO ve la carga dinámica —importlib, un plugin, un punto de entrada por configuración— así que un módulo vivo por esa vía sale marcado, y si `alcanzable` viene vacía la medida NO concluye: lo declara en `requiere` y sale SIN EVIDENCIA en vez de verde

  proceso.modulo_con_consumidor
    umbral:   <= 0
    fijación: 4 casos
    alcance:  cuenta importadores que no son tests, agrupando por módulo. Si `importa` viene vacía la medida NO concluye —lo declara en `requiere`, y sale SIN EVIDENCIA en vez de verde—. NO distingue un importador que usa el módulo de uno que lo importa y no lo llama

  proceso.ronda_mutacion_concluyente
    umbral:   <= 0
    fijación: 4 casos
    alcance:  ve los estados estructurados publicados por cada corrida. NO distingue por sí sola si un código no cero fue una aserción o un error: eso depende del protocolo explícito del runner. Si corrida_mutacion viene vacía significa que no hubo rondas de mutación inconclusas y verde es correcto

  proceso.sintaxis_valida_tras_edicion_masiva
    umbral:   <= 0
    fijación: 2 casos
    alcance:  ve archivos marcados como no parseables. NO ve el daño que SÍ parsea: una regex puede cambiar el significado de una línea sin romper la sintaxis. Si archivo viene vacía significa que no se detectaron archivos con sintaxis rota tras la edición masiva y verde es correcto

  proceso.test_con_mutante_que_lo_mata
    umbral:   <= 0
    fijación: 9 casos
    alcance:  cuenta mutantes que ningún caso observó, de ninguna de las cuatro maneras. NO ve los mutantes que nadie generó: una medida sin ningún mutador aplicable da cero y sale verde. Tampoco distingue un mutante equivalente —imposible de matar— de uno que el corpus todavía no fija; esa diferencia hay que declararla a mano

  proceso.verificacion_vigente
    umbral:   <= 0
    fijación: 3 casos
    alcance:  cuenta cambios marcados como código vivo. En v0.1 NO compara fechas ni sabe cuál verificación quedó vieja: cualquier cambio vivo la invalida. Hace falta comparar contra el commit de la verificación. Si cambio viene vacía significa que no hubo cambios recientes, por lo que la verificación sigue vigente

  proceso.verificador_sin_falsos_rojos
    umbral:   <= 0
    fijación: 3 casos
    alcance:  ve hallazgos que YA fueron etiquetados como falsos. NO puede decidir sola si un hallazgo es real: alguien tuvo que mirarlo. Si hallazgo viene vacía significa que el verificador no reportó nada, por lo que el mundo está limpio de falsos rojos

  simulacion.corrida_reproducible
    umbral:   <= 0
    fijación: 4 casos
    alcance:  compara dos ejecuciones con la MISMA semilla. NO ve si el resultado depende de algo de afuera —la hora, el orden de un diccionario, un archivo— que hoy casualmente no cambió. Si corrida viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—.

  simulacion.la_traza_no_tiene_huecos
    umbral:   <= 0
    fijación: 4 casos
    alcance:  compara cuántos eventos hay contra el instante final, asumiendo que el tiempo arranca en cero y avanza de a uno. NO ve trazas donde varios eventos comparten instante, ni sabe si el que falta es importante. Si evento viene vacío la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—.

  simulacion.no_se_agoto_el_presupuesto
    umbral:   <= 0
    fijación: 4 casos
    alcance:  ve la clasificación producida por el contrato de terminación. NO ve si el presupuesto era razonable, ni si una corrida que terminó a tiempo lo hizo por el motivo correcto. Si corrida viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—.
```

---

### D. `oracle caso listar` sobre el propio Oracle (104 casos)

```
$ python tools/cli.py caso listar
CORPUS (104 casos · 101 con medida · 3 huecos declarados):

  meta/030-alcance-en-superficie                                                    falso_verde                        meta.ninguna_medida_sin_alcance
  meta/031-relaciones-incompletas-en-superficie                                     falso_verde                        meta.el_caso_se_pone_como_debe
  meta/032-ejercitada-en-superficie                                                 falso_verde                        meta.toda_medida_esta_ejercitada
  meta/033-fijada-en-superficie                                                     falso_verde                        meta.toda_medida_esta_fijada
  meta/034-conmutatividad-en-superficie                                             falso_verde                        meta.unir_conmuta
  meta/035-asociatividad-en-superficie                                              falso_verde                        meta.unir_conmuta
  meta/036-distributividad-en-superficie                                            falso_verde                        meta.unir_conmuta
  meta/037-composicion-en-superficie                                                falso_verde                        meta.donde_compone
  meta/038-expansion-en-superficie                                                  falso_verde                        meta.una_macro_equivale_a_su_expansion
  meta/039-conmutatividad-sin-ejercitar                                             falso_verde                        meta.unir_conmuta
  meta/040-composicion-sin-ejercitar                                                falso_verde                        meta.donde_compone
  meta/041-expansion-sin-ejercitar                                                  falso_verde                        meta.una_macro_equivale_a_su_expansion
  meta/042-asociatividad-sin-ejercitar                                              falso_verde                        meta.unir_conmuta
  meta/045-meta-desacuerdos-diferencial                                             falso_verde                        meta.el_caso_se_pone_como_debe
  meta/046-meta-desacuerdo-individual-diferencial                                   falso_verde                        meta.el_caso_se_pone_como_debe
  meta/047-meta-no-determinismo-semilla                                             falso_verde                        meta.el_caso_se_pone_como_debe
  meta/048-meta-timeout-distorsiona-tasa                                            falso_verde                        meta.el_caso_se_pone_como_debe
  meta/049-meta-falso-verde-en-invariante                                           falso_verde                        meta.el_caso_se_pone_como_debe
  meta/050-meta-mutante-equivalente-contado-como-muerto                             falso_verde                        meta.el_caso_se_pone_como_debe
  meta/051-meta-orden-de-evaluacion-altera-resultado                                falso_verde                        meta.el_caso_se_pone_como_debe
  meta/052-meta-invariante-no-cubre-casos-borde                                     falso_verde                        meta.el_caso_se_pone_como_debe
  meta/053-meta-medida-incompleta-en-catalogo                                       falso_verde                        meta.el_caso_se_pone_como_debe
  meta/054-meta-distribucion-sesgada-sin-alerta                                     falso_verde                        meta.el_caso_se_pone_como_debe
  meta/055-meta-error-en-oraculo-produce-falsos-rojos                               falso_verde                        meta.el_caso_se_pone_como_debe
  meta/056-meta-medida-redundante-sin-poder-discriminatorio                         falso_verde                        meta.el_caso_se_pone_como_debe
  meta/057-meta-evaluacion-parcial-declarada-completa                               falso_verde                        meta.el_caso_se_pone_como_debe
  meta/060-medida-sin-filtro-ni-agrupamiento                                        falso_verde                        meta.toda_medida_filtra_o_agrupa
  meta/061-agrupar-agranda-la-relacion                                              falso_verde                        meta.agrupar_no_agranda_la_relacion
  meta/062-unir-no-materializa-el-producto                                          falso_verde                        meta.unir_materializa_el_producto
  meta/063-donde-agrega-filas                                                       falso_verde                        meta.donde_nunca_agrega_filas
  meta/064-logico-cortocircuita                                                     falso_verde                        meta.los_logicos_evaluan_todos_sus_operandos
  meta/065-ausencia-sin-requiere                                                    falso_verde                        meta.toda_medida_de_ausencia_declara_requiere
  meta/066-caso-reclama-medida-inexistente                                          falso_verde                        meta.el_caso_reclama_una_medida_que_existe
  meta/067-caso-sin-medida-sin-justificacion                                        falso_verde                        meta.el_hueco_declarado_explica_por_que
  meta/068-medida-en-carpeta-equivocada                                             falso_verde                        meta.el_nivel_no_se_confunde_con_el_dominio
  meta/069-umbral-de-igualdad                                                       falso_verde                        meta.ningun_umbral_de_igualdad
  meta/108-donde-compone-un-campo-por-vez                                           falso_verde                        meta.donde_compone
  meta/109-unir-conmuta-un-campo-por-vez                                            falso_verde                        meta.unir_conmuta
  meta/110-agrupar-sin-claves-es-el-resumen-global-un-campo-por-vez                 falso_verde                        meta.agrupar_sin_claves_es_el_resumen_global
  meta/111-una-macro-equivale-a-su-expansion-un-campo-por-vez                       falso_verde                        meta.una_macro_equivale_a_su_expansion
  meta/112-medida-bien-ubicada                                                      verde_correcto                     meta.el_nivel_no_se_confunde_con_el_dominio
  meta/113-umbral-de-desigualdad                                                    verde_correcto                     meta.ningun_umbral_de_igualdad
  meta/114-caso-sin-medida-con-justificacion                                        verde_correcto                     meta.el_hueco_declarado_explica_por_que
  meta/115-ausencia-con-requiere                                                    verde_correcto                     meta.toda_medida_de_ausencia_declara_requiere
  meta/117-medida-con-filtro                                                        verde_correcto                     meta.toda_medida_filtra_o_agrupa
  meta/118-medida-con-agrupamiento                                                  verde_correcto                     meta.toda_medida_filtra_o_agrupa
  meta/119-medida-con-filtro-y-agrupamiento                                         verde_correcto                     meta.toda_medida_filtra_o_agrupa
  meta/120-sintaxis-no-vuelve-igual                                                 falso_verde                        meta.sintaxis_ida_y_vuelta
  meta/121-sintaxis-vuelve-exacta                                                   verde_correcto                     meta.sintaxis_ida_y_vuelta
  meta/122-sintaxis-revienta-al-leer                                                falso_verde                        meta.sintaxis_ida_y_vuelta
  meta/123-sintaxis-un-campo-por-vez                                                falso_verde                        meta.sintaxis_ida_y_vuelta
  meta/124-sintaxis-cubre-algebra-no-vuelve-igual                                   falso_verde                        meta.sintaxis_cubre_algebra
  meta/125-sintaxis-cubre-algebra-vuelve-exacta                                     verde_correcto                     meta.sintaxis_cubre_algebra
  meta/126-sintaxis-cubre-algebra-un-campo-por-vez                                  falso_verde                        meta.sintaxis_cubre_algebra
  meta/127-sintaxis-casos-no-vuelve-igual                                           falso_verde                        meta.sintaxis_casos_ida_y_vuelta
  meta/128-sintaxis-casos-vuelve-exacta                                             verde_correcto                     meta.sintaxis_casos_ida_y_vuelta
  meta/129-sintaxis-casos-generados-no-vuelve-igual                                 falso_verde                        meta.sintaxis_casos_cubre_casos
  meta/130-sintaxis-casos-generados-vuelve-exacta                                   verde_correcto                     meta.sintaxis_casos_cubre_casos
  meta/131-sintaxis-casos-un-campo-por-vez                                          falso_verde                        meta.sintaxis_casos_ida_y_vuelta
  meta/132-sintaxis-casos-generados-un-campo-por-vez                                falso_verde                        meta.sintaxis_casos_cubre_casos
  meta/400-umbral-flotante-de-igualdad                                              falso_verde                        meta.ningun_umbral_flotante_de_igualdad
  meta/401-umbral-flotante-de-desigualdad                                           falso_verde                        meta.ningun_umbral_flotante_de_igualdad
  meta/402-umbral-flotante-de-orden-y-entero                                        verde_correcto                     meta.ningun_umbral_flotante_de_igualdad
  meta/403-umbral-sin-defensa                                                       falso_verde                        meta.ningun_umbral_sin_defensa
  meta/404-umbral-con-defensa                                                       verde_correcto                     meta.ningun_umbral_sin_defensa
  meta/405-medida-sin-alcance                                                       falso_verde                        meta.ninguna_medida_sin_alcance
  meta/406-medida-con-alcance                                                       verde_correcto                     meta.ninguna_medida_sin_alcance
  proceso/001-verde-acumulativo                                                     falso_verde                        proceso.afirmacion_declara_alcance
  proceso/002-mutante-firma-por-id                                                  falso_verde                        proceso.test_con_mutante_que_lo_mata
  proceso/003-mutante-fondo-nunca-ejercitado                                        falso_verde                        proceso.test_con_mutante_que_lo_mata
  proceso/004-testigos-duplicados                                                   deuda_de_diseño                    ⚠ hueco declarado (resuelto)
  proceso/005-mutante-yaw-sin-franja                                                falso_verde                        proceso.test_con_mutante_que_lo_mata
  proceso/006-arnes-bytecode-viejo                                                  falso_verde                        proceso.arnes_con_bytecode_frio
  proceso/007-relevo-verde-arbol-sucio                                              falso_verde                        proceso.verificacion_vigente
  proceso/008-vault-falso-rojo                                                      falso_rojo                         proceso.verificador_sin_falsos_rojos
  proceso/009-modulo-sin-consumidor                                                 falso_verde                        proceso.modulo_con_consumidor
  proceso/010-sed-desindenta                                                        falso_verde                        proceso.sintaxis_valida_tras_edicion_masiva
  proceso/011-conclusion-errada-desvan                                              medida_correcta_conclusion_errada  ⚠ hueco declarado (limite_humano)
  proceso/012-umbral-duplicado-en-filtro-y-umbral                                   deuda_de_diseño                    ⚠ hueco declarado (resuelto)
  proceso/013-comparadores-del-algebra-sin-ejercitar                                falso_verde                        proceso.test_con_mutante_que_lo_mata
  proceso/014-mutador-dejo-un-archivo-mutado-al-ser-matado                          falso_verde                        proceso.test_con_mutante_que_lo_mata
  proceso/015-racimo-inalcanzable                                                   falso_verde                        proceso.modulo_alcanzable
  proceso/016-timeout-contado-como-mutante-muerto                                   falso_verde                        proceso.ronda_mutacion_concluyente
  proceso/017-error-de-arnes-contado-como-mutante-muerto                            falso_verde                        proceso.ronda_mutacion_concluyente
  proceso/018-mutante-de-cache-borro-la-copia-del-proyecto                          falso_verde                        proceso.test_con_mutante_que_lo_mata
  proceso/019-ronda-sin-mutantes-declarada-verde                                    falso_verde                        proceso.ronda_mutacion_concluyente
  proceso/020-una-afirmacion-sin-alcance-alcanza                                    falso_verde                        proceso.afirmacion_declara_alcance
  proceso/021-un-cambio-vivo-invalida-la-verificacion                               falso_verde                        proceso.verificacion_vigente
  proceso/022-un-falso-rojo-ya-rompe-el-verificador                                 falso_rojo                         proceso.verificador_sin_falsos_rojos
  proceso/023-un-import-ajeno-no-es-consumidor                                      falso_verde                        proceso.modulo_con_consumidor
  proceso/024-una-variante-no-vacia-inalcanzable                                    falso_verde                        proceso.modulo_alcanzable
  proceso/025-mutante-de-codigo-sobreviviente                                       falso_verde                        proceso.codigo_con_mutante_que_lo_mata
  proceso/026-mutante-de-codigo-equivalente-no-cuenta-como-muerte-ni-sobreviviente  falso_verde                        proceso.codigo_con_mutante_que_lo_mata
  proceso/027-ronda-de-codigo-sin-mutantes-no-concluye                              falso_verde                        proceso.codigo_con_mutante_que_lo_mata
  proceso/043-ausencia-total-sale-verde                                             falso_verde                        proceso.modulo_con_consumidor
  proceso/044-sin-grafo-de-alcance-sale-verde                                       falso_verde                        proceso.modulo_alcanzable
  proceso/058-rechazo-del-algebra-no-es-deteccion                                   verde_correcto                     proceso.test_con_mutante_que_lo_mata
  proceso/059-clave-declarada-en-un-caso                                            verde_correcto                     proceso.test_con_mutante_que_lo_mata
  proceso/101-mutantes-todos-muertos                                                verde_correcto                     proceso.test_con_mutante_que_lo_mata
  proceso/102-verificacion-vigente                                                  verde_correcto                     proceso.verificacion_vigente
  proceso/103-vault-sin-falsos-rojos                                                verde_correcto                     proceso.verificador_sin_falsos_rojos
  proceso/104-afirmacion-con-alcance                                                verde_correcto                     proceso.afirmacion_declara_alcance
  proceso/105-arnes-con-cache-frio                                                  verde_correcto                     proceso.arnes_con_bytecode_frio
  proceso/106-modulos-con-consumidor                                                verde_correcto                     proceso.modulo_con_consumidor
  proceso/107-reruteo-sin-romper-sintaxis                                           verde_correcto                     proceso.sintaxis_valida_tras_edicion_masiva
  proceso/108-ronda-mutacion-concluyente                                            verde_correcto                     proceso.ronda_mutacion_concluyente
  proceso/109-mutantes-de-codigo-todos-muertos                                      verde_correcto                     proceso.codigo_con_mutante_que_lo_mata
  proceso/110-mutante-de-codigo-equivalente-declarado-verde                         verde_correcto                     proceso.codigo_con_mutante_que_lo_mata
  proceso/116-todo-el-nucleo-es-alcanzable                                          verde_correcto                     proceso.modulo_alcanzable
  simulacion/200-corrida-sin-ninguna-corrida                                        falso_verde                        simulacion.corrida_reproducible
  simulacion/201-presupuesto-sin-ninguna-corrida                                    falso_verde                        simulacion.no_se_agoto_el_presupuesto
  simulacion/202-traza-sin-ningun-evento                                            falso_verde                        simulacion.la_traza_no_tiene_huecos
  simulacion/301-simulador-que-ignora-la-semilla                                    falso_verde                        simulacion.corrida_reproducible
  simulacion/302-corridas-reproducibles                                             verde_correcto                     simulacion.corrida_reproducible
  simulacion/303-el-presupuesto-no-alcanzo                                          falso_verde                        simulacion.no_se_agoto_el_presupuesto
  simulacion/304-el-presupuesto-alcanzo                                             verde_correcto                     simulacion.no_se_agoto_el_presupuesto
  simulacion/305-traza-con-hueco                                                    falso_verde                        simulacion.la_traza_no_tiene_huecos
  simulacion/306-traza-completa                                                     verde_correcto                     simulacion.la_traza_no_tiene_huecos
  simulacion/307-una-corrida-no-reproducible-alcanza                                falso_verde                        simulacion.corrida_reproducible
  simulacion/308-una-corrida-agota-el-presupuesto                                   falso_verde                        simulacion.no_se_agoto_el_presupuesto
  simulacion/309-una-traza-con-un-hueco                                             falso_verde                        simulacion.la_traza_no_tiene_huecos
```

---

### E. Proyecto recién creado en `/tmp`, medida sin fijar creada a propósito, y fijación con caso

```
$ python tools/cli.py proyecto init /tmp/oracle-auditoria-6lkjd2t8/mi-proyecto
Proyecto Oracle inicializado en /tmp/oracle-auditoria-6lkjd2t8/mi-proyecto:
  · catalogos/
  · corpus/
  · diferencial/
  · oracle.json

Próximos pasos:
  1. Creá una medida:  oracle nueva <dominio.nombre>
  2. Creá un caso:     oracle caso <grupo/id>
  3. Verificá todo:    oracle test

$ python tools/cli.py medida listar --proyecto /tmp/oracle-auditoria-6lkjd2t8/mi-proyecto
CATÁLOGO: 0 medidas en catalogos

$ python tools/cli.py caso listar --proyecto /tmp/oracle-auditoria-6lkjd2t8/mi-proyecto
CORPUS: 0 casos en corpus

$ python tools/cli.py medida nueva tareas.vencida_sin_dueno --proyecto /tmp/oracle-auditoria-6lkjd2t8/mi-proyecto
creada: catalogos/tareas/tareas.vencida_sin_dueno.oracle

Reemplazá RELACION, CAMPO y los dos textos en MAYÚSCULAS. Después:
  oracle revisar catalogos/tareas/tareas.vencida_sin_dueno.oracle

$ python tools/cli.py medida listar --proyecto /tmp/oracle-auditoria-6lkjd2t8/mi-proyecto
CATÁLOGO (1 medida · 0 fijadas · 1 sin fijar):

  tareas.vencida_sin_dueno
    umbral:   <= 0
    fijación: 0 casos  ⚠ SIN FIJAR
    alcance:  ve el par vencida+sin-dueño y nada más

$ python tools/cli.py caso nuevo tareas/001-vencida-sin-dueno --proyecto /tmp/oracle-auditoria-6lkjd2t8/mi-proyecto
creado: corpus/tareas/001-vencida-sin-dueno.caso

Reemplazá los marcadores en MAYÚSCULAS. Dos tienen valores cerrados:

  etiqueta:         deuda_de_diseño · falso_rojo · falso_verde · medida_correcta_conclusion_errada · verde_correcto
  como_se_detecto:  accidente · herramienta_ajena · mutacion · observacion · persona

Después:  oracle test

$ python tools/cli.py medida listar --proyecto /tmp/oracle-auditoria-6lkjd2t8/mi-proyecto
CATÁLOGO (1 medida · todas fijadas):

  tareas.vencida_sin_dueno
    umbral:   <= 0
    fijación: 1 caso
    alcance:  ve el par vencida+sin-dueño y nada más

$ python tools/cli.py caso listar --proyecto /tmp/oracle-auditoria-6lkjd2t8/mi-proyecto
CORPUS (1 caso · todos con medida):

  tareas/001-vencida-sin-dueno  falso_verde  tareas.vencida_sin_dueno
```

---

## 3. Qué NO hicimos y por qué

1. **No cambiamos la firma ni rompimos los comandos directos históricos**:
   - Comandos como `oracle init`, `oracle nueva`, `oracle revisar`, `oracle test`, etc., siguen funcionando de manera idéntica a antes. Toda la base instalada y los scripts existentes no sufren regresiones.
2. **No tocamos los archivos de `catalogos/`, `corpus/`, `diferencial/` ni `nucleo/`**:
   - La funcionalidad requerida pertenece enteramente a la capa de herramientas y presentación de CLI (`tools/medida.py`, `tools/corpus.py`, `tools/cli.py`).
3. **No silenciamos excepciones ni usamos `except: pass` ciego**:
   - Mantuvimos el principio de fail-closed: cuando hay un error de parseo o carga en una medida o caso, se reporta y aborta con código 1.

---

## 4. Hallazgos Inesperados

1. **Importación previa de UDFs escalares en CLI**:
   - Descubrimos durante la exploración inicial que para cargar ASTs que utilizan funciones escalares como `por` (registradas dinámicamente en `catalogos`), es indispensable que el módulo `catalogos` esté importado. `tools/cli.py` ya lo importa al inicio (`import catalogos`), lo cual garantiza que `medida listar` y la resolución de medidas funcionen uniformemente.
2. **Casos plantilla recién creados**:
   - Al crear un caso nuevo con `caso nuevo <grupo/id>`, el archivo creado es una plantilla con placeholders como `ETIQUETA` en mayúsculas. Cuando herramientas como `sintaxis.py` o `relaciones` intentan cargar el corpus, `cargar_fuente_caso` rechaza con `CasoMalDeclarado` ese archivo mientras no sea completado por el usuario. En las pruebas unitarias nos aseguramos de poblar el caso con valores válidos para que las verificaciones posteriores puedan correr de punta a punta.

---

## 5. Salida de las 9 Verificaciones de DOCTRINA.md

A continuación se pegan las salidas reales y completas de las 9 verificaciones ejecutadas sobre el repositorio:

### Verificación 1: `python -m unittest discover -s tests -t . -q`
```
----------------------------------------------------------------------
Ran 658 tests in 25.528s

OK
```

### Verificación 2: `python tools/cifras.py`
```
CIFRAS OK
  cifras: 658 tests · 547/547 mutantes de medida · **2431 sitios de mutación de código** (2226 + 205 del motor Python).
  escala: **5775 líneas de lenguaje** (`nucleo/`, código y macros) y **256 negativas explícitas** (`raise`). Contra las 37 medidas universales escritas en él (225 líneas): **25,7 a 1**. 29 de las 37 pasan por una macro.
  corpus: **104 casos**: 70 defectos y 34 verdes correctos. De los defectos, 67 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 65 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5775 líneas de lenguaje y **256 negativas explícitas** (`raise`).
  deteccion: Los 70 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 51 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### Verificación 3: `python tools/corpus.py`
```
CORPUS OK · 104 casos · esquema, evidencia L0 y trazabilidad en regla
```

### Verificación 4: `python tools/aceptacion.py`
```
defectos que se pusieron rojos: 67 · verdes correctos: 34 · huecos declarados: 0
  resuelto       004-testigos-duplicados
  resuelto       012-umbral-duplicado-en-filtro-y-umbral
  limite_humano  011-conclusion-errada-desvan

nivel meta — el marco medido con sus propias medidas:
  ✓ meta.el_caso_reclama_una_medida_que_existe          0 (<= 0)
  ✓ meta.el_caso_se_pone_como_debe                      0 (<= 0)
  ✓ meta.el_hueco_declarado_explica_por_que             0 (<= 0)
  ✓ meta.el_nivel_no_se_confunde_con_el_dominio         0 (<= 0)
  ✓ meta.ningun_umbral_de_igualdad                      0 (<= 0)
  ✓ meta.ningun_umbral_flotante_de_igualdad             0 (<= 0)
  ✓ meta.ningun_umbral_sin_defensa                      0 (<= 0)
  ✓ meta.ninguna_medida_sin_alcance                     0 (<= 0)
  ✓ meta.toda_medida_de_ausencia_declara_requiere        0 (<= 0)
  ✓ meta.toda_medida_filtra_o_agrupa                    0 (<= 0)

ACEPTACIÓN ✓ — 67 defectos en rojo, 34 verdes correctos, 0 huecos declarados sin tapar
```

### Verificación 5: `python tools/diferencial.py`
```
simulacion.json · 4 mundos · origen: implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md

  ✓ acuerdo global: 4 escenarios (1 verdes / 3 rojos) · 0 desacuerdos
  ✓ estabilidad individual: 3 medidas × 4 escenarios · 0 cambios


DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

### Verificación 6: `python tools/trazar.py`
```
evaluaciones trazadas: 92
hechos: 182 pasos · 339 nodos lógicos · 11 productos

el álgebra, juzgada por medidas escritas en el álgebra:
  ✓ meta.agrupar_no_agranda_la_relacion                 0 (<= 0)
  ✓ meta.donde_nunca_agrega_filas                       0 (<= 0)
  ✓ meta.los_logicos_evaluan_todos_sus_operandos        0 (<= 0)
  ✓ meta.unir_materializa_el_producto                   0 (<= 0)

contrastado con la implementación independiente: 4 propiedades, 0 desacuerdos

  · meta.agrupar_no_agranda_la_relacion: compara el conteo antes y después de cada `agrupar` trazado. NO ve si las claves de agrupación son las correctas ni si los agregados calcularon bien; sólo que no aparecieron filas de la nada. Si paso viene vacía no hay pasos observados que agranden la relación y verde es correcto; además el arnés trazar.py garantiza ejecuciones trazadas por construcción
  · meta.donde_nunca_agrega_filas: compara el conteo antes y después de cada `donde` sobre las evaluaciones que se trazaron. NO ve si las filas que quedaron son las correctas —sólo cuántas—, ni cubre una evaluación que no se corrió bajo traza. Si paso viene vacía no hay filtros que agranden la relación y verde es correcto; además trazar.py garantiza pasos trazados por construcción
  · meta.los_logicos_evaluan_todos_sus_operandos: cuenta operandos evaluados contra los declarados en el AST, en cada `y` y cada `o` trazado. NO ve si el valor de cada operando es correcto, y no cubre una evaluación que se corrió sin traza. Si nodo viene vacía no hay cortocircuitos observados y verde es correcto; además trazar.py garantiza nodos trazados por construcción
  · meta.unir_materializa_el_producto: compara el tamaño de la salida contra el producto de los dos lados. NO ve si los pares que armó son los correctos ni en qué orden salieron; un `unir` que devuelve la cantidad justa de pares equivocados pasa. Si producto viene vacía no hay productos defectuosos y verde es correcto; además trazar.py garantiza productos trazados por construcción
```

### Verificación 7: `python tools/metamorficas.py`
```
equivalencias comprobadas: 331
  agrupar_sin_claves_es_el_resumen_global        5 (5 construidas, 0 del catálogo)
  donde_compone                                  1 (1 construidas, 0 del catálogo)
  sintaxis_casos_cubre_casos                     5 (5 construidas, 0 del catálogo)
  sintaxis_casos_ida_y_vuelta                  104 (0 construidas, 104 del catálogo)
  sintaxis_cubre_algebra                        94 (94 construidas, 0 del catálogo)
  sintaxis_ida_y_vuelta                         37 (0 construidas, 37 del catálogo)
  una_macro_equivale_a_su_expansion             69 (0 construidas, 69 del catálogo)
  unir_conmuta                                  16 (1 construidas, 15 del catálogo)

juzgado por las medidas aplicables:
  ✓ meta.agrupar_sin_claves_es_el_resumen_global        0 (<= 0)
  ✓ meta.donde_compone                                  0 (<= 0)
  ✓ meta.sintaxis_casos_cubre_casos                     0 (<= 0)
  ✓ meta.sintaxis_casos_ida_y_vuelta                    0 (<= 0)
  ✓ meta.sintaxis_cubre_algebra                         0 (<= 0)
  ✓ meta.sintaxis_ida_y_vuelta                          0 (<= 0)
  ✓ meta.una_macro_equivale_a_su_expansion              0 (<= 0)
  ✓ meta.unir_conmuta                                   0 (<= 0)
```

### Verificación 8: `python tools/sintaxis.py --verificar`
```
medidas convertidas: 37
macros convertidas: 3
casos convertidos: 104
ida JSON: OK
vuelta texto: OK
caracteres: JSON 142369 · superficie 139406
puntuación: JSON 25487 (17,9%) · superficie 10489 (7,5%)
bloques de documentación: 21 verificados · 8 declarados como gramática o fragmento
```

### Verificación 9: `python tools/mutar.py`
```
mutantes de medida (medida × mutador): 547 · murieron 547 · sobrevivieron 0
  de los muertos: 422 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 125 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1924

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.codigo_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'estado'], 'pasaron'] en `2.2.1.1`
```

---

## 6. Verificación de Instalación y Empaquetado

```
$ python tools/verificar_instalacion.py
WHEEL OK · namespace, datos, 8 entry points, oracle test y dos motores aislados fuera del checkout
```
