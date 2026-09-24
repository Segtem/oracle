# Clasificación del contraste independiente, álgebra 0.8

Comando reproducido el 2026-09-24:

```bash
python3 estudios/0.26.0-codex/contrastar.py estudios/0.26.0-codex/entrega-2026-09-24/adaptado.py --json
```

Resultado: **285 comparaciones, 66 desacuerdos**. El adaptador sólo mueve el nodo `ambito`; no corrige semántica. Cada fila de la tabla final corresponde a un elemento del JSON, identificado por `origen` y `medida`. Las clases son: **1** hueco de especificación, **2** defecto del candidato y **3** defecto de la referencia. En los 66 casos: 52 de clase 1, 14 de clase 2 y 0 de clase 3. Son **tres causas**, no 66 hallazgos.

## Causas

### A. Relación de `requiere` ausente: clase 2, 14 desacuerdos

El candidato lanza `ErrorDeAlgebra` cuando la relación requerida ni siquiera es una clave del mapa de evidencia; la referencia devuelve `SIN EVIDENCIA`. **§2, párrafo del coefecto `requiere`**, decide: «si falta una relación, se corta fail-closed con `SIN EVIDENCIA`». El párrafo anterior también establece que una relación requerida vacía da ese valor. La ausencia de la clave es justamente una relación que falta, por lo que aquí se aparta el candidato. Su decisión 2 en `DECISIONES.md` explicita la lectura contraria. Afecta ocho comparaciones en mundos (dos medidas por cuatro mundos) y seis casos del corpus.

### B. `y`/`o` con más de dos operandos: clase 1, 49 desacuerdos

El candidato exige exactamente dos operandos; la referencia admite tres o más. **§3, «Acceso a los datos» y tabla de operadores**, nombra expresiones y predicados, pero no da gramática ni aridad de `y`/`o`. **§8, párrafo «Ausencia»**, sólo muestra un ejemplo de `y` binario; no cierra la forma general. Una lectura binaria estricta y una lectura variádica son defendibles. Las medidas canónicas publicadas incluyen, por ejemplo, `meta.donde_compone` con `o` de tres argumentos y `proceso.ronda_mutacion_concluyente` con `o` de cinco. Las 49 diferencias son rechazo de forma antes de evaluar filas; no prueban divergencias en la lógica de verdad.

### C. `max` de booleanos homogéneos: clase 1, 3 desacuerdos

`proceso.modulo_alcanzable` agrega `es_paquete_vacio` con `max`. El candidato considera comparables los booleanos homogéneos y sigue hasta `contar`; la referencia los rechaza como no ordenables. **§3, párrafo «Agregados»**, sólo exige a `min`/`max` «escalares homogéneos y comparables», sin precisar si `false < true` vale en el álgebra. **§0, párrafo de `MAYOR`**, usa expresamente «qué hace `min`/`max` con booleanos» como ejemplo de semántica que habría que decidir. Ambas lecturas son defendibles. En los casos 015, 024 y 116 el candidato da respectivamente 12, 1 y 0; la referencia levanta.

## Hueco anterior al adaptador: posición de `ambito`, clase 1

El contraste directo registrado en la tarea dio 274 desacuerdos; el adaptador de orden deja 66. **§0, párrafo de `MENOR`**, afirma que la forma canónica ganó el nodo opcional `ambito`. **§2, primer ejemplo y párrafos de forma canónica**, muestran seis elementos sin `ambito` y siete con `requiere` antes de `alcance`, pero nunca sitúan `ambito`. La referencia acepta `ambito` antes de `alcance`; el candidato lo espera después. Las dos lecturas son defendibles. Esta causa explica la reducción del contraste directo; no se vuelve a contar entre los 66 clasificados.

## Inventario exhaustivo de los 66 desacuerdos

`C` y `R` indican el veredicto del candidato y de la referencia. `error` significa `levanta: true`; `SE` significa `SIN EVIDENCIA`. El identificador completo de cada comparación es la pareja `origen` + `medida`.

| N.º | Origen | Medida | Clase / causa | C | R |
|---:|---|---|---|---|---|
| 1 | `mundo:todo-en-orden` | `simulacion.traza_sin_fallas_con_mutantes_de_codigo` | 2 / A | error | SE |
| 2 | `mundo:todo-en-orden` | `simulacion.corrida_con_mutantes_que_pasaron` | 2 / A | error | SE |
| 3 | `mundo:corrida-que-no-se-reproduce` | `simulacion.traza_sin_fallas_con_mutantes_de_codigo` | 2 / A | error | SE |
| 4 | `mundo:corrida-que-no-se-reproduce` | `simulacion.corrida_con_mutantes_que_pasaron` | 2 / A | error | SE |
| 5 | `mundo:presupuesto-agotado` | `simulacion.traza_sin_fallas_con_mutantes_de_codigo` | 2 / A | error | SE |
| 6 | `mundo:presupuesto-agotado` | `simulacion.corrida_con_mutantes_que_pasaron` | 2 / A | error | SE |
| 7 | `mundo:traza-con-un-hueco` | `simulacion.traza_sin_fallas_con_mutantes_de_codigo` | 2 / A | error | SE |
| 8 | `mundo:traza-con-un-hueco` | `simulacion.corrida_con_mutantes_que_pasaron` | 2 / A | error | SE |
| 9 | `caso:061-ausencia-sin-requiere` | `meta.toda_medida_de_ausencia_declara_requiere` | 1 / B | error | 1 |
| 10 | `caso:062-ausencia-cubierta-o-no-aplica` | `meta.toda_medida_de_ausencia_declara_requiere` | 1 / B | error | 0 |
| 11 | `caso:063-ausencia-sin-terminos-no-concluye` | `meta.toda_medida_de_ausencia_declara_requiere` | 1 / B | error | SE |
| 12 | `caso:075-las-dos-medidas-reales-de-unir-y-agrupar-declaran-requiere` | `meta.toda_medida_de_ausencia_declara_requiere` | 1 / B | error | 0 |
| 13 | `caso:100-donde-no-compone` | `meta.donde_compone` | 1 / B | error | 1 |
| 14 | `caso:101-donde-compone-bien` | `meta.donde_compone` | 1 / B | error | 0 |
| 15 | `caso:102-unir-no-conmuta` | `meta.unir_conmuta` | 1 / B | error | 1 |
| 16 | `caso:103-unir-conmuta-bien` | `meta.unir_conmuta` | 1 / B | error | 0 |
| 17 | `caso:106-macro-expande-distinto` | `meta.una_macro_equivale_a_su_expansion` | 1 / B | error | 1 |
| 18 | `caso:107-macro-equivale` | `meta.una_macro_equivale_a_su_expansion` | 1 / B | error | 0 |
| 19 | `caso:108-donde-compone-un-campo-por-vez` | `meta.donde_compone` | 1 / B | error | 3 |
| 20 | `caso:109-unir-conmuta-un-campo-por-vez` | `meta.unir_conmuta` | 1 / B | error | 3 |
| 21 | `caso:111-una-macro-equivale-a-su-expansion-un-campo-por-vez` | `meta.una_macro_equivale_a_su_expansion` | 1 / B | error | 3 |
| 22 | `caso:120-sintaxis-no-vuelve-igual` | `meta.sintaxis_ida_y_vuelta` | 1 / B | error | 1 |
| 23 | `caso:121-sintaxis-vuelve-exacta` | `meta.sintaxis_ida_y_vuelta` | 1 / B | error | 0 |
| 24 | `caso:122-sintaxis-revienta-al-leer` | `meta.sintaxis_ida_y_vuelta` | 1 / B | error | 1 |
| 25 | `caso:123-sintaxis-un-campo-por-vez` | `meta.sintaxis_ida_y_vuelta` | 1 / B | error | 3 |
| 26 | `caso:124-sintaxis-cubre-algebra-no-vuelve-igual` | `meta.sintaxis_cubre_algebra` | 1 / B | error | 1 |
| 27 | `caso:125-sintaxis-cubre-algebra-vuelve-exacta` | `meta.sintaxis_cubre_algebra` | 1 / B | error | 0 |
| 28 | `caso:126-sintaxis-cubre-algebra-un-campo-por-vez` | `meta.sintaxis_cubre_algebra` | 1 / B | error | 4 |
| 29 | `caso:127-sintaxis-casos-no-vuelve-igual` | `meta.sintaxis_casos_ida_y_vuelta` | 1 / B | error | 1 |
| 30 | `caso:128-sintaxis-casos-vuelve-exacta` | `meta.sintaxis_casos_ida_y_vuelta` | 1 / B | error | 0 |
| 31 | `caso:129-sintaxis-casos-generados-no-vuelve-igual` | `meta.sintaxis_casos_cubre_casos` | 1 / B | error | 1 |
| 32 | `caso:130-sintaxis-casos-generados-vuelve-exacta` | `meta.sintaxis_casos_cubre_casos` | 1 / B | error | 0 |
| 33 | `caso:131-sintaxis-casos-un-campo-por-vez` | `meta.sintaxis_casos_ida_y_vuelta` | 1 / B | error | 4 |
| 34 | `caso:132-sintaxis-casos-generados-un-campo-por-vez` | `meta.sintaxis_casos_cubre_casos` | 1 / B | error | 4 |
| 35 | `caso:409-flotante-comparado-por-igualdad-en-filtro` | `meta.ningun_flotante_comparado_por_igualdad_en_un_filtro` | 1 / B | error | 1 |
| 36 | `caso:410-flotante-comparado-por-desigualdad-en-filtro` | `meta.ningun_flotante_comparado_por_igualdad_en_un_filtro` | 1 / B | error | 1 |
| 37 | `caso:411-flotante-en-filtro-sin-ancestro-no-concluye` | `meta.ningun_flotante_comparado_por_igualdad_en_un_filtro` | 1 / B | error | SE |
| 38 | `caso:412-catalogo-real-sin-flotante-de-igualdad-en-filtro` | `meta.ningun_flotante_comparado_por_igualdad_en_un_filtro` | 1 / B | error | 0 |
| 39 | `caso:426-referente-sin-evidencia-no-concluye` | `meta.ninguna_evidencia_declara_un_referente_sin_huella` | 2 / A | error | SE |
| 40 | `caso:429-sin-comparacion-de-referente-no-concluye` | `meta.ninguna_evidencia_se_juzga_con_referente_vencido` | 2 / A | error | SE |
| 41 | `caso:439-sin-verbos-del-cli-no-concluye` | `meta.todo_verbo_del_cli_esta_en_la_ayuda` | 2 / A | error | SE |
| 42 | `caso:440-sin-opciones-del-vocabulario-no-concluye` | `meta.toda_opcion_del_vocabulario_declara_su_sentido` | 2 / A | error | SE |
| 43 | `caso:441-sin-opciones-del-vocabulario-el-manual-no-concluye` | `meta.todo_vocabulario_cerrado_esta_en_el_manual` | 2 / A | error | SE |
| 44 | `caso:452-sin-relaciones-documentadas-no-concluye` | `meta.toda_relacion_del_lenguaje_esta_en_la_referencia` | 2 / A | error | SE |
| 45 | `caso:475-medida-universal-depende-de-relacion-del-origen` | `meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias` | 1 / B | error | 1 |
| 46 | `caso:476-medidas-con-dependencias-de-ambito-compatible` | `meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias` | 1 / B | error | 0 |
| 47 | `caso:477-medida-universal-depende-por-requiere-de-relacion-del-origen` | `meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias` | 1 / B | error | 1 |
| 48 | `caso:478-la-cota-y-la-clasificacion-coinciden-sin-consultarse` | `meta.ninguna_medida_declara_un_ambito_mas_amplio_que_sus_dependencias` | 1 / B | error | 0 |
| 49 | `caso:485-la-ausencia-visible-no-volvia-de-una-macro` | `meta.sintaxis_ida_y_vuelta` | 1 / B | error | 3 |
| 50 | `caso:486-la-ausencia-visible-vuelve-de-las-tres-macros` | `meta.sintaxis_ida_y_vuelta` | 1 / B | error | 0 |
| 51 | `caso:488-agrupar-sin-agregados-no-volvia-de-la-superficie` | `meta.sintaxis_cubre_algebra` | 1 / B | error | 3 |
| 52 | `caso:489-agrupar-sin-agregados-vuelve-exacto` | `meta.sintaxis_cubre_algebra` | 1 / B | error | 0 |
| 53 | `caso:492-una-cota-con-holgura-esconde-el-progreso` | `meta.ninguna_cota_mas_alta_que_su_deuda` | 1 / B | error | 1 |
| 54 | `caso:493-la-cota-es-exactamente-la-deuda` | `meta.ninguna_cota_mas_alta_que_su_deuda` | 1 / B | error | 0 |
| 55 | `caso:495-dos-cotas-con-holgura-y-una-deuda-en-cero` | `meta.ninguna_cota_mas_alta_que_su_deuda` | 1 / B | error | 2 |
| 56 | `caso:500-un-campo-con-espacio-se-escribia-como-tabla` | `meta.sintaxis_casos_cubre_casos` | 1 / B | error | 2 |
| 57 | `caso:501-las-dos-formas-del-impresor-eligen-bien` | `meta.sintaxis_casos_cubre_casos` | 1 / B | error | 0 |
| 58 | `caso:015-racimo-inalcanzable` | `proceso.modulo_alcanzable` | 1 / C | 12 | error |
| 59 | `caso:016-timeout-contado-como-mutante-muerto` | `proceso.ronda_mutacion_concluyente` | 1 / B | error | 1 |
| 60 | `caso:017-error-de-arnes-contado-como-mutante-muerto` | `proceso.ronda_mutacion_concluyente` | 1 / B | error | 1 |
| 61 | `caso:019-ronda-sin-mutantes-declarada-verde` | `proceso.ronda_mutacion_concluyente` | 1 / B | error | 1 |
| 62 | `caso:024-una-variante-no-vacia-inalcanzable` | `proceso.modulo_alcanzable` | 1 / C | 1 | error |
| 63 | `caso:108-ronda-mutacion-concluyente` | `proceso.ronda_mutacion_concluyente` | 1 / B | error | 0 |
| 64 | `caso:111-ronda-mutacion-parcial-no-es-concluyente` | `proceso.ronda_mutacion_concluyente` | 1 / B | error | 1 |
| 65 | `caso:112-ronda-mutacion-completa-concluyente` | `proceso.ronda_mutacion_concluyente` | 1 / B | error | 0 |
| 66 | `caso:116-todo-el-nucleo-es-alcanzable` | `proceso.modulo_alcanzable` | 1 / C | 0 | error |
