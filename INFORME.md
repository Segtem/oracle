# Informe

## Diseño escrito antes de implementar

La superficie propuesta queda así:

- `caso <id>:` es el encabezado.
- Los campos escalares usan `clave: valor`.
- `sintoma`, `leccion` y los textos largos opcionales quedan como bloque de prosa indentado.
- `evidencia:` contiene relaciones.
- Una relación homogénea se escribe como `relacion: campo, campo` y una fila por hecho.
- Una clave declarada va en el encabezado de la relación: `relacion: clave(id); campo, campo`.
- Una relación presente con cero filas se escribe como `relacion:` sin filas.
- La salida de escape para relaciones heterogéneas es `fila { ... }`, una fila JSON por hecho.

### corpus/meta/121-sintaxis-vuelve-exacta.json

```caso
caso 121-sintaxis-vuelve-exacta:
    fecha: "2026-08-24"
    origen:
        repo: "Segtem/oracle"
        commit: "b250e6c"
    titulo: "Sintaxis vuelve exacta"
    etiqueta: verde_correcto
    sintoma:
        Tres medidas vuelven exactas: una canónica, una escrita por macro y una con `requiere`. Las tres formas de almacenamiento sobreviven la ida y vuelta sin cambio.
    como_se_detecto: observacion
    medida: meta.sintaxis_ida_y_vuelta
    evidencia:
        equivalencia: propiedad, caso, origen, evaluo, error, mismo_veredicto, mismo_valor, mismos_testigos
            "sintaxis_ida_y_vuelta", "canonica", "catalogo", true, "", true, true, true
            "sintaxis_ida_y_vuelta", "por-macro", "catalogo", true, "", true, true, true
            "sintaxis_ida_y_vuelta", "con-requiere", "catalogo", true, "", true, true, true
    leccion:
        Las tres están a propósito. Una superficie que sólo conserve la forma canónica serviría para 7 de las 29 medidas: el resto se escribe con la macro `ninguno`, y `requiere` es un nodo opcional que un lector distraído puede tragarse sin avisar.
```

## Qué cambié

- `nucleo/caso.py`: agregué lector, impresor, rutas y carga común para `.json` y `.caso`. El lector usa `ErrorSintaxis` y `fragmento_de_error`, distingue relación ausente de relación presente vacía, conserva `clave` y usa `fila { ... }` como escape para relaciones heterogéneas.
- `tools/corpus.py`: dejó de hacer `rglob("*.json")`; ahora enumera `rutas_de_corpus` y carga cada archivo con `cargar_fuente_caso`.
- `tools/aceptacion.py`: carga casos con `cargar_casos`.
- `tools/mutar.py`: carga casos con `cargar_casos` antes de sumar fixtures diferenciales.
- `tools/trazar.py`: carga casos con `cargar_casos`.
- `tools/metamorficas.py`: carga casos con `cargar_casos`.
- `tools/medida.py`: carga evidencia del corpus con `cargar_casos` y, al listar relaciones, separa la `clave` con `separar_clave` antes de iterar filas.
- `tools/estudio.py`: usa `cargar_casos` y `rutas_de_corpus` para la prosa y los números del paquete de estudio.
- `tools/cifras.py`: `_casos_del_corpus()` usa `cargar_casos`; después corrí `python tools/cifras.py --actualizar`.
- `tests/test_sintaxis.py`: agregué tests de ida/vuelta de casos, lector dual real, id duplicado entre formatos, relación heterogénea, relación vacía presente y diagnóstico de `.caso` mal formado con archivo, línea, columna y fragmento.
- `tests/test_herramientas.py`: el reparto del corpus cuenta `rutas_de_corpus`, no `*.json`.
- `tools/mutar_codigo.py`: agregué prioridades para `nucleo/caso.py`, porque ahora entra al denominador de mutación de código.
- `equivalentes.json`: actualicé el id posicional del equivalente de `tools/cifras.py`; el sitio sigue siendo el mismo `sys.path.insert`.
- `README.md`: actualizado por `tools/cifras.py --actualizar` con los números nuevos.
- `corpus/meta/067-umbral-de-igualdad.json` y `corpus/proceso/004-testigos-duplicados.json`: quedaron en JSON a propósito para ejercitar el lector viejo sobre el corpus real.
- `corpus/**/*.caso`: 88 casos migrados a la superficie nueva. La lista exacta:
  - `corpus/meta/049-donde-agrego-filas.caso`
  - `corpus/meta/050-donde-filtra-como-debe.caso`
  - `corpus/meta/051-agrupar-invento-un-grupo.caso`
  - `corpus/meta/052-agrupar-colapsa-como-debe.caso`
  - `corpus/meta/053-unir-perdio-un-par.caso`
  - `corpus/meta/054-unir-materializa-el-producto.caso`
  - `corpus/meta/055-logico-cortocircuito.caso`
  - `corpus/meta/056-logico-evalua-todo.caso`
  - `corpus/meta/057-un-solo-cortocircuito.caso`
  - `corpus/meta/061-ausencia-sin-requiere.caso`
  - `corpus/meta/062-ausencia-cubierta-o-no-aplica.caso`
  - `corpus/meta/063-ausencia-sin-terminos-no-concluye.caso`
  - `corpus/meta/064-medida-sin-filtro-ni-grupo.caso`
  - `corpus/meta/065-medida-filtra-o-agrupa.caso`
  - `corpus/meta/066-filtro-sin-terminos-no-concluye.caso`
  - `corpus/meta/068-umbral-de-orden.caso`
  - `corpus/meta/069-filtro-no-toma-terminos-ajenos.caso`
  - `corpus/meta/100-donde-no-compone.caso`
  - `corpus/meta/101-donde-compone-bien.caso`
  - `corpus/meta/102-unir-no-conmuta.caso`
  - `corpus/meta/103-unir-conmuta-bien.caso`
  - `corpus/meta/104-agrupar-sin-claves-difiere.caso`
  - `corpus/meta/105-agrupar-sin-claves-coincide.caso`
  - `corpus/meta/106-macro-expande-distinto.caso`
  - `corpus/meta/107-macro-equivale.caso`
  - `corpus/meta/108-donde-compone-un-campo-por-vez.caso`
  - `corpus/meta/109-unir-conmuta-un-campo-por-vez.caso`
  - `corpus/meta/110-agrupar-sin-claves-es-el-resumen-global-un-campo-por-vez.caso`
  - `corpus/meta/111-una-macro-equivale-a-su-expansion-un-campo-por-vez.caso`
  - `corpus/meta/120-sintaxis-no-vuelve-igual.caso`
  - `corpus/meta/121-sintaxis-vuelve-exacta.caso`
  - `corpus/meta/122-sintaxis-revienta-al-leer.caso`
  - `corpus/meta/123-sintaxis-un-campo-por-vez.caso`
  - `corpus/meta/400-umbral-flotante-de-igualdad.caso`
  - `corpus/meta/401-umbral-flotante-de-desigualdad.caso`
  - `corpus/meta/402-umbral-flotante-de-orden-y-entero.caso`
  - `corpus/meta/403-umbral-sin-defensa.caso`
  - `corpus/meta/404-umbral-con-defensa.caso`
  - `corpus/meta/405-medida-sin-alcance.caso`
  - `corpus/meta/406-medida-con-alcance.caso`
  - `corpus/proceso/001-verde-acumulativo.caso`
  - `corpus/proceso/002-mutante-firma-por-id.caso`
  - `corpus/proceso/003-mutante-fondo-nunca-ejercitado.caso`
  - `corpus/proceso/005-mutante-yaw-sin-franja.caso`
  - `corpus/proceso/006-arnes-bytecode-viejo.caso`
  - `corpus/proceso/007-relevo-verde-arbol-sucio.caso`
  - `corpus/proceso/008-vault-falso-rojo.caso`
  - `corpus/proceso/009-modulo-sin-consumidor.caso`
  - `corpus/proceso/010-sed-desindenta.caso`
  - `corpus/proceso/011-conclusion-errada-desvan.caso`
  - `corpus/proceso/012-umbral-duplicado-en-filtro-y-umbral.caso`
  - `corpus/proceso/013-comparadores-del-algebra-sin-ejercitar.caso`
  - `corpus/proceso/014-mutador-dejo-un-archivo-mutado-al-ser-matado.caso`
  - `corpus/proceso/015-racimo-inalcanzable.caso`
  - `corpus/proceso/016-timeout-contado-como-mutante-muerto.caso`
  - `corpus/proceso/017-error-de-arnes-contado-como-mutante-muerto.caso`
  - `corpus/proceso/018-mutante-de-cache-borro-la-copia-del-proyecto.caso`
  - `corpus/proceso/019-ronda-sin-mutantes-declarada-verde.caso`
  - `corpus/proceso/020-una-afirmacion-sin-alcance-alcanza.caso`
  - `corpus/proceso/021-un-cambio-vivo-invalida-la-verificacion.caso`
  - `corpus/proceso/022-un-falso-rojo-ya-rompe-el-verificador.caso`
  - `corpus/proceso/023-un-import-ajeno-no-es-consumidor.caso`
  - `corpus/proceso/024-una-variante-no-vacia-inalcanzable.caso`
  - `corpus/proceso/043-ausencia-total-sale-verde.caso`
  - `corpus/proceso/044-sin-grafo-de-alcance-sale-verde.caso`
  - `corpus/proceso/058-rechazo-del-algebra-no-es-deteccion.caso`
  - `corpus/proceso/059-clave-declarada-en-un-caso.caso`
  - `corpus/proceso/101-mutantes-todos-muertos.caso`
  - `corpus/proceso/102-verificacion-vigente.caso`
  - `corpus/proceso/103-vault-sin-falsos-rojos.caso`
  - `corpus/proceso/104-afirmacion-con-alcance.caso`
  - `corpus/proceso/105-arnes-con-cache-frio.caso`
  - `corpus/proceso/106-modulos-con-consumidor.caso`
  - `corpus/proceso/107-reruteo-sin-romper-sintaxis.caso`
  - `corpus/proceso/108-ronda-mutacion-concluyente.caso`
  - `corpus/proceso/116-todo-el-nucleo-es-alcanzable.caso`
  - `corpus/simulacion/200-corrida-sin-ninguna-corrida.caso`
  - `corpus/simulacion/201-presupuesto-sin-ninguna-corrida.caso`
  - `corpus/simulacion/202-traza-sin-ningun-evento.caso`
  - `corpus/simulacion/301-simulador-que-ignora-la-semilla.caso`
  - `corpus/simulacion/302-corridas-reproducibles.caso`
  - `corpus/simulacion/303-el-presupuesto-no-alcanzo.caso`
  - `corpus/simulacion/304-el-presupuesto-alcanzo.caso`
  - `corpus/simulacion/305-traza-con-hueco.caso`
  - `corpus/simulacion/306-traza-completa.caso`
  - `corpus/simulacion/307-una-corrida-no-reproducible-alcanza.caso`
  - `corpus/simulacion/308-una-corrida-agota-el-presupuesto.caso`
  - `corpus/simulacion/309-una-traza-con-un-hueco.caso`

## Lecturas de corpus revisadas

- `tools/corpus.py`: sí leía corpus; actualizado.
- `tools/aceptacion.py`: sí leía corpus; actualizado.
- `tools/mutar.py`: sí leía corpus; actualizado.
- `tools/trazar.py`: sí leía corpus; actualizado.
- `tools/metamorficas.py`: sí leía corpus; actualizado.
- `tools/medida.py`: sí leía corpus; actualizado.
- `tools/estudio.py`: sí leía corpus; actualizado.
- `tools/cifras.py`: sí leía corpus para cifras publicadas; actualizado.
- `tools/diferencial.py`: no leía `corpus/`; sólo lee `diferencial/*.json`, así que no correspondía tocarlo.

## Salidas de verificación

### `python -m unittest discover -s tests -t . -q`

```text
----------------------------------------------------------------------
Ran 495 tests in 9.122s

OK
```

### `python tools/cifras.py`

```text
CIFRAS OK
  cifras: 495 tests · 406/406 mutantes de medida · **2226 sitios de mutación de código** (2021 + 205 del motor Python).
  escala: **5445 líneas de lenguaje** (`nucleo/`, código y macros) y **247 negativas explícitas** (`raise`). Contra las 33 medidas universales escritas en él (203 líneas): **26,8 a 1**. 26 de las 33 pasan por una macro.
  corpus: **90 casos**: 61 defectos y 29 verdes correctos. De los defectos, 58 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 56 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5445 líneas de lenguaje y **247 negativas explícitas** (`raise`).
  deteccion: Los 61 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 42 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### `python tools/corpus.py`

```text
CORPUS OK · 90 casos · esquema, evidencia L0 y trazabilidad en regla
```

### `python tools/aceptacion.py`

```text
catálogo: 33 medidas · corpus: 90 casos

  ROJO  049-donde-agrego-filas                 meta.donde_nunca_agrega_filas  (valor 1)
  verde 050-donde-filtra-como-debe             meta.donde_nunca_agrega_filas  (valor 0)
  ROJO  051-agrupar-invento-un-grupo           meta.agrupar_no_agranda_la_relacion  (valor 1)
  verde 052-agrupar-colapsa-como-debe          meta.agrupar_no_agranda_la_relacion  (valor 0)
  ROJO  053-unir-perdio-un-par                 meta.unir_materializa_el_producto  (valor 1)
  verde 054-unir-materializa-el-producto       meta.unir_materializa_el_producto  (valor 0)
  ROJO  055-logico-cortocircuito               meta.los_logicos_evaluan_todos_sus_operandos  (valor 2)
  verde 056-logico-evalua-todo                 meta.los_logicos_evaluan_todos_sus_operandos  (valor 0)
  ROJO  057-un-solo-cortocircuito              meta.los_logicos_evaluan_todos_sus_operandos  (valor 1)
  ROJO  061-ausencia-sin-requiere              meta.toda_medida_de_ausencia_declara_requiere  (valor 1)
  verde 062-ausencia-cubierta-o-no-aplica      meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  063-ausencia-sin-terminos-no-concluye  meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  064-medida-sin-filtro-ni-grupo         meta.toda_medida_filtra_o_agrupa  (valor 1)
  verde 065-medida-filtra-o-agrupa             meta.toda_medida_filtra_o_agrupa  (valor 0)
  ROJO  066-filtro-sin-terminos-no-concluye    meta.toda_medida_filtra_o_agrupa  (valor 0)
  ROJO  067-umbral-de-igualdad                 meta.ningun_umbral_de_igualdad  (valor 1)
  verde 068-umbral-de-orden                    meta.ningun_umbral_de_igualdad  (valor 0)
  ROJO  069-filtro-no-toma-terminos-ajenos     meta.toda_medida_filtra_o_agrupa  (valor 1)
  ROJO  100-donde-no-compone                   meta.donde_compone  (valor 1)
  verde 101-donde-compone-bien                 meta.donde_compone  (valor 0)
  ROJO  102-unir-no-conmuta                    meta.unir_conmuta  (valor 1)
  verde 103-unir-conmuta-bien                  meta.unir_conmuta  (valor 0)
  ROJO  104-agrupar-sin-claves-difiere         meta.agrupar_sin_claves_es_el_resumen_global  (valor 1)
  verde 105-agrupar-sin-claves-coincide        meta.agrupar_sin_claves_es_el_resumen_global  (valor 0)
  ROJO  106-macro-expande-distinto             meta.una_macro_equivale_a_su_expansion  (valor 1)
  verde 107-macro-equivale                     meta.una_macro_equivale_a_su_expansion  (valor 0)
  ROJO  108-donde-compone-un-campo-por-vez     meta.donde_compone  (valor 3)
  ROJO  109-unir-conmuta-un-campo-por-vez      meta.unir_conmuta  (valor 3)
  ROJO  110-agrupar-sin-claves-es-el-resumen-global-un-campo-por-vez meta.agrupar_sin_claves_es_el_resumen_global  (valor 2)
  ROJO  111-una-macro-equivale-a-su-expansion-un-campo-por-vez meta.una_macro_equivale_a_su_expansion  (valor 3)
  ROJO  120-sintaxis-no-vuelve-igual           meta.sintaxis_ida_y_vuelta  (valor 1)
  verde 121-sintaxis-vuelve-exacta             meta.sintaxis_ida_y_vuelta  (valor 0)
  ROJO  122-sintaxis-revienta-al-leer          meta.sintaxis_ida_y_vuelta  (valor 1)
  ROJO  123-sintaxis-un-campo-por-vez          meta.sintaxis_ida_y_vuelta  (valor 3)
  ROJO  400-umbral-flotante-de-igualdad        meta.ningun_umbral_flotante_de_igualdad  (valor 1)
  ROJO  401-umbral-flotante-de-desigualdad     meta.ningun_umbral_flotante_de_igualdad  (valor 1)
  verde 402-umbral-flotante-de-orden-y-entero  meta.ningun_umbral_flotante_de_igualdad  (valor 0)
  ROJO  403-umbral-sin-defensa                 meta.ningun_umbral_sin_defensa  (valor 1)
  verde 404-umbral-con-defensa                 meta.ningun_umbral_sin_defensa  (valor 0)
  ROJO  405-medida-sin-alcance                 meta.ninguna_medida_sin_alcance  (valor 1)
  verde 406-medida-con-alcance                 meta.ninguna_medida_sin_alcance  (valor 0)
  ROJO  001-verde-acumulativo                  proceso.afirmacion_declara_alcance  (valor 3)
  ROJO  002-mutante-firma-por-id               proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  003-mutante-fondo-nunca-ejercitado     proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  005-mutante-yaw-sin-franja             proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  006-arnes-bytecode-viejo               proceso.arnes_con_bytecode_frio  (valor 1)
  ROJO  007-relevo-verde-arbol-sucio           proceso.verificacion_vigente  (valor 2)
  ROJO  008-vault-falso-rojo                   proceso.verificador_sin_falsos_rojos  (valor 2)
  ROJO  009-modulo-sin-consumidor              proceso.modulo_con_consumidor  (valor 3)
  ROJO  010-sed-desindenta                     proceso.sintaxis_valida_tras_edicion_masiva  (valor 1)
  ROJO  013-comparadores-del-algebra-sin-ejercitar proceso.test_con_mutante_que_lo_mata  (valor 6)
  ROJO  014-mutador-dejo-un-archivo-mutado-al-ser-matado proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  015-racimo-inalcanzable                proceso.modulo_alcanzable  (valor 12)
  ROJO  016-timeout-contado-como-mutante-muerto proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  017-error-de-arnes-contado-como-mutante-muerto proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  018-mutante-de-cache-borro-la-copia-del-proyecto proceso.test_con_mutante_que_lo_mata  (valor 1)
  ROJO  019-ronda-sin-mutantes-declarada-verde proceso.ronda_mutacion_concluyente  (valor 1)
  ROJO  020-una-afirmacion-sin-alcance-alcanza proceso.afirmacion_declara_alcance  (valor 1)
  ROJO  021-un-cambio-vivo-invalida-la-verificacion proceso.verificacion_vigente  (valor 1)
  ROJO  022-un-falso-rojo-ya-rompe-el-verificador proceso.verificador_sin_falsos_rojos  (valor 1)
  ROJO  023-un-import-ajeno-no-es-consumidor   proceso.modulo_con_consumidor  (valor 1)
  ROJO  024-una-variante-no-vacia-inalcanzable proceso.modulo_alcanzable  (valor 1)
  ROJO  043-ausencia-total-sale-verde          proceso.modulo_con_consumidor  (valor 0)
  ROJO  044-sin-grafo-de-alcance-sale-verde    proceso.modulo_alcanzable  (valor 0)
  verde 058-rechazo-del-algebra-no-es-deteccion proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 059-clave-declarada-en-un-caso         proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 101-mutantes-todos-muertos             proceso.test_con_mutante_que_lo_mata  (valor 0)
  verde 102-verificacion-vigente               proceso.verificacion_vigente  (valor 0)
  verde 103-vault-sin-falsos-rojos             proceso.verificador_sin_falsos_rojos  (valor 0)
  verde 104-afirmacion-con-alcance             proceso.afirmacion_declara_alcance  (valor 0)
  verde 105-arnes-con-cache-frio               proceso.arnes_con_bytecode_frio  (valor 0)
  verde 106-modulos-con-consumidor             proceso.modulo_con_consumidor  (valor 0)
  verde 107-reruteo-sin-romper-sintaxis        proceso.sintaxis_valida_tras_edicion_masiva  (valor 0)
  verde 108-ronda-mutacion-concluyente         proceso.ronda_mutacion_concluyente  (valor 0)
  verde 116-todo-el-nucleo-es-alcanzable       proceso.modulo_alcanzable  (valor 0)
  ROJO  200-corrida-sin-ninguna-corrida        simulacion.corrida_reproducible  (valor 0)
  ROJO  201-presupuesto-sin-ninguna-corrida    simulacion.no_se_agoto_el_presupuesto  (valor 0)
  ROJO  202-traza-sin-ningun-evento            simulacion.la_traza_no_tiene_huecos  (valor 0)
  ROJO  301-simulador-que-ignora-la-semilla    simulacion.corrida_reproducible  (valor 2)
  verde 302-corridas-reproducibles             simulacion.corrida_reproducible  (valor 0)
  ROJO  303-el-presupuesto-no-alcanzo          simulacion.no_se_agoto_el_presupuesto  (valor 3)
  verde 304-el-presupuesto-alcanzo             simulacion.no_se_agoto_el_presupuesto  (valor 0)
  ROJO  305-traza-con-hueco                    simulacion.la_traza_no_tiene_huecos  (valor 2)
  verde 306-traza-completa                     simulacion.la_traza_no_tiene_huecos  (valor 0)
  ROJO  307-una-corrida-no-reproducible-alcanza simulacion.corrida_reproducible  (valor 1)
  ROJO  308-una-corrida-agota-el-presupuesto   simulacion.no_se_agoto_el_presupuesto  (valor 1)
  ROJO  309-una-traza-con-un-hueco             simulacion.la_traza_no_tiene_huecos  (valor 1)

defectos que se pusieron rojos: 58 · verdes correctos: 29 · huecos declarados: 0
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

ACEPTACIÓN ✓ — 58 defectos en rojo, 29 verdes correctos, 0 huecos declarados sin tapar
```

### `python tools/diferencial.py`

```text
simulacion.json · 4 mundos · origen: implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md

  ✓ acuerdo global: 4 escenarios (1 verdes / 3 rojos) · 0 desacuerdos
  ✓ estabilidad individual: 3 medidas × 4 escenarios · 0 cambios


DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

### `python tools/trazar.py`

```text
evaluaciones trazadas: 78
hechos: 156 pasos · 266 nodos lógicos · 11 productos

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

### `python tools/metamorficas.py`

```text
equivalencias comprobadas: 115
  agrupar_sin_claves_es_el_resumen_global        5 (5 construidas, 0 del catálogo)
  donde_compone                                  1 (1 construidas, 0 del catálogo)
  sintaxis_ida_y_vuelta                         33 (0 construidas, 33 del catálogo)
  una_macro_equivale_a_su_expansion             60 (0 construidas, 60 del catálogo)
  unir_conmuta                                  16 (1 construidas, 15 del catálogo)

juzgado por las medidas aplicables:
  ✓ meta.agrupar_sin_claves_es_el_resumen_global        0 (<= 0)
  ✓ meta.donde_compone                                  0 (<= 0)
  ✓ meta.sintaxis_ida_y_vuelta                          0 (<= 0)
  ✓ meta.una_macro_equivale_a_su_expansion              0 (<= 0)
  ✓ meta.unir_conmuta                                   0 (<= 0)
```

### `python tools/sintaxis.py --verificar`

```text
medidas convertidas: 33
macros convertidas: 3
ida JSON: OK
vuelta texto: OK
caracteres: JSON 25455 · superficie 24697
puntuación: JSON 3864 (15,2%) · superficie 952 (3,9%)
bloques de documentación: 16 verificados · 8 declarados como gramática o fragmento
```

### `python tools/mutar.py`

```text
mutantes de medida (medida × mutador): 406 · murieron 406 · sobrevivieron 0
  de los muertos: 327 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 79 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1477

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)
```

## Qué no hice

- No toqué `catalogos/` ni medidas.
- No toqué `vendor/`.
- No toqué `nucleo/version.py` ni `ESPECIFICACION.md §0`.
- No agregué propiedades metamórficas sobre sintaxis.
- No cambié contenido de `sintoma`, `leccion` ni `etiqueta`; la conversión fue ida/vuelta por datos.
- No eliminé el lector JSON del corpus: quedaron dos casos reales en `.json`.
- No cambié `tools/diferencial.py` porque no lee `corpus/`.

## Lo que encontré

- `tools/medida.py --relaciones` trataba el nodo `["clave", ...]` como fila al inventariar campos. No se veía porque no se estaba corriendo sobre la superficie nueva; quedó corregido usando `separar_clave`.
- El equivalente de `tools/cifras.py` volvió a mostrar que los ids posicionales de mutación son frágiles: sacar un import muerto cambió la línea del mismo sitio.
- Agregar un archivo nuevo bajo `nucleo/` lo mete en mutación de código; por eso hubo que declarar prioridades en `tools/mutar_codigo.py`.
- Los números publicados se movieron: ahora son 5445 líneas de lenguaje, 247 `raise`, proporción 26,8 a 1 y 495 tests.

### corpus/proceso/059-clave-declarada-en-un-caso.json

```caso
caso 059-clave-declarada-en-un-caso:
    fecha: "2026-08-24"
    origen:
        repo: "Segtem/oracle"
        commit: "6fec96a"
    titulo: "Una relación que declara su clave sigue midiéndose igual"
    etiqueta: verde_correcto
    sintoma:
        Un sensor que sabe cuál es la identidad de sus hechos puede declararla: `["clave", ["id"]]` a la cabeza de la relación. La evidencia sigue siendo L0 y la medida no se entera — el nodo no es un hecho, no se cuenta, no llega a los testigos y no cambia ningún veredicto. Este caso lo fija de punta a punta, desde la validación del corpus hasta el veredicto.
    como_se_detecto: observacion
    medida: proceso.test_con_mutante_que_lo_mata
    evidencia:
        mutante: clave(id); id, apunta_a, cambio, detecciones_conductuales, rechazos_del_algebra
            "d.x·quitar_filtro", "d.x", "quitar_filtro", 2, 0
            "d.x·negar_filtro", "d.x", "negar_filtro", 1, 0
    leccion:
        El mecanismo de claves nació sin poder usarse en un caso: `tools/corpus.py` rechazaba el nodo como «no es un hecho», porque el validador del corpus y el del álgebra son dos lecturas del mismo contrato. Es el caso `012` otra vez —la misma regla escrita dos veces diverge— y se cerró haciendo que el corpus llame a `separar_clave` en vez de reimplementarla. Un mecanismo que el corpus no puede expresar es un mecanismo que este proyecto no puede fijar, y todo lo demás acá se fija con casos.
```

### corpus/proceso/116-todo-el-nucleo-es-alcanzable.json

```caso
caso 116-todo-el-nucleo-es-alcanzable:
    fecha: "2026-07-30"
    origen:
        repo: "Segtem/oracle"
        commit: "recursión"
    titulo: "Con las entradas reales declaradas, no hay módulo muerto"
    etiqueta: verde_correcto
    sintoma:
        Desde las entradas de verdad —las que importan las herramientas— se llega a todos los módulos. Los `__init__.py` vacíos no cuentan: son marcadores de paquete, y eso va como hecho.
    como_se_detecto: observacion
    medida: proceso.modulo_alcanzable
    evidencia:
        modulo: nombre, es_test, lineas, es_paquete_vacio
            "nucleo", false, 0, true
            "nucleo.algebra", false, 232, false
            "nucleo.dominio", false, 129, false
            "nucleo.grafo", false, 52, false
            "nucleo.macro", false, 109, false
            "nucleo.marco", false, 146, false
            "nucleo.medida", false, 225, false
            "nucleo.mutacion", false, 170, false
            "nucleo.mutacion_codigo", false, 269, false
            "nucleo.proyecto", false, 129, false
            "nucleo.simulacion", false, 115, false
            "catalogos", false, 7, false
            "catalogos.escalares", false, 37, false
            "ejemplo", false, 0, true
            "ejemplo.trabajo", false, 50, false
        importa: a, b, es_test
            "nucleo.dominio", "nucleo.medida", false
            "nucleo.marco", "nucleo.grafo", false
            "nucleo.medida", "nucleo.algebra", false
            "nucleo.medida", "nucleo.macro", false
            "nucleo.mutacion", "nucleo.medida", false
            "catalogos", "catalogos.escalares", false
            "catalogos.escalares", "nucleo.algebra", false
            "ejemplo.trabajo", "nucleo.simulacion", false
        alcanzable: desde, hasta, saltos
            "nucleo.medida", "nucleo.algebra", 1
            "nucleo.medida", "nucleo.macro", 1
            "nucleo.medida", "nucleo.medida", 0
            "nucleo.dominio", "nucleo.algebra", 2
            "nucleo.dominio", "nucleo.dominio", 0
            "nucleo.dominio", "nucleo.macro", 2
            "nucleo.dominio", "nucleo.medida", 1
            "nucleo.marco", "nucleo.grafo", 1
            "nucleo.marco", "nucleo.marco", 0
            "nucleo.mutacion", "nucleo.algebra", 2
            "nucleo.mutacion", "nucleo.macro", 2
            "nucleo.mutacion", "nucleo.medida", 1
            "nucleo.mutacion", "nucleo.mutacion", 0
            "nucleo.mutacion_codigo", "nucleo.mutacion_codigo", 0
            "nucleo.proyecto", "nucleo.proyecto", 0
            "nucleo.simulacion", "nucleo.simulacion", 0
            "catalogos", "catalogos", 0
            "catalogos", "catalogos.escalares", 1
            "catalogos", "nucleo.algebra", 2
            "ejemplo.trabajo", "ejemplo.trabajo", 0
            "ejemplo.trabajo", "nucleo.simulacion", 1
    leccion:
        La otra polaridad, con el grafo de imports real del repositorio.
```
