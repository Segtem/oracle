# Informe — Errores de la superficie de casos (.caso)

## Los seis tropiezos, antes y después

Base de prueba tomada como referencia:
```
caso 001-prueba:
    fecha: "2026-08-26"
    origen:
        repo: "test"
        commit: "local"
    titulo: "T"
    etiqueta: verde_correcto
    sintoma:
        S
    como_se_detecto: observacion
    medida: demo.mide
    evidencia:
        tarea: id, vencida
            "t-1", true
    leccion:
        L
```

### 1. Olvida el origen
- **Antes**: `línea 3, columna 5: se esperaba línea «origen:»; llegó 'titulo: "T"'`
- **Después**: `línea 3, columna 5: se esperaba línea «origen:»; llegó 'titulo: "T"'`

### 2. Etiqueta inventada (`etiqueta: rojo_feo`)
- **Antes**: ⚠ No fallaba al leer (cargaba el caso en silencio y fallaba recién en `oracle test`).
- **Después**: `línea 7, columna 15: se esperaba etiqueta en ['deuda_de_diseño', 'falso_rojo', 'falso_verde', 'medida_correcta_conclusion_errada', 'verde_correcto']; llegó 'rojo_feo'`

(Idem para `como_se_detecto: inventado` → `línea 10, columna 22: se esperaba como_se_detecto en ['accidente', 'herramienta_ajena', 'mutacion', 'observacion', 'persona']; llegó 'inventado'`).

### 3. Fila con menos columnas (`"t-1"`)
- **Antes**: `línea 14, columna 13: se esperaba 2 valores de fila; llegó '"t-1"'`
- **Después**: `línea 14, columna 13: la relación «tarea» declara 2 campos (id, vencida) y esta fila trae 1; llegó '"t-1"'`

### 4. Fila con más columnas (`"t-1", true, 9`)
- **Antes**: `línea 14, columna 13: se esperaba 2 valores de fila; llegó '"t-1", true, 9'`
- **Después**: `línea 14, columna 13: la relación «tarea» declara 2 campos (id, vencida) y esta fila trae 3; llegó '"t-1", true, 9'`

### 5. Olvida las comillas (`fecha: 2026-08-26`)
- **Antes**: `línea 2, columna 16: se esperaba fin de valor JSON; llegó '-08-26'`
- **Después**: `línea 2, columna 16: se esperaba texto entre comillas; llegó '-08-26'`

### 6. Campos sin coma (`tarea: id vencida`)
- **Antes**: `línea 14, columna 13: se esperaba 1 valores de fila; llegó '"t-1", true'` (el encabezado pasaba inadvertido tomando `id vencida` como un único campo, y el error caía tarde en la fila).
- **Después**: `línea 13, columna 19: se esperaba ',' entre campos; llegó 'vencida'` (señala la columna exacta donde falta la coma en el encabezado).

---

## Qué cambié, archivo por archivo

### `nucleo/caso.py`
1. Declaré `ETIQUETAS` y `DETECCIONES` como conjuntos inmutables (`frozenset`) en la cabecera del módulo, convirtiéndolo en la fuente única de verdad para el lector y las herramientas.
2. En `_json_valor`, reemplacé `"valor JSON"` y `"fin de valor JSON"` por `"texto entre comillas"` para indicar que los literales escalares ausentes de comillas necesitan comillas dobles.
3. En `_parsear_cabecera_relacion`, agregué la validación de comas entre nombres de campos (tanto para campos generales como para `clave(...)`), calculando la columna exacta del identificador que quedó sin separador.
4. En `_leer_evidencia`, modifiqué el reporte de discordancia de cantidad de columnas: ahora nombra la relación, enumera los campos declarados respetando singular y plural (`1 campo (id)` vs `N campos (...)`), y reporta cuántos valores trajo la fila.
5. En `_Parser.leer`, agregué la validación inmediata de `etiqueta` y `como_se_detecto` contra `ETIQUETAS` y `DETECCIONES`, señalando la columna exacta del valor no reconocido.

### `tools/corpus.py`
1. Removí la definición duplicada de `ETIQUETAS` y `DETECCIONES`, importándolas directamente desde `nucleo.caso`.
2. Actualicé `PLANTILLA` para usar valores válidos por defecto (`falso_verde` y `mutacion`), permitiendo que el andamiaje (`--nuevo`) genere casos válidos syntácticamente de entrada.

### `equivalentes.json`
1. Reapunté los 6 mutantes equivalentes de `nucleo/caso.py` a sus nuevas líneas tras las inserciones de código y documenté la razón del movimiento.

### `tests/test_sintaxis.py`
1. Actualicé los mensajes esperados en `SintaxisDeCasosTests` (`"fecha no JSON"`, `"fecha sin valor"`, `"origen valor no JSON"`, `"fila escape JSON roto"`, `"cantidad de valores"`).
2. Agregué nuevos casos en la tabla de pruebas para validar etiqueta inventada, `como_se_detecto` inventado, fecha sin comillas, campos sin coma (con y sin clave previa), y relación de un solo campo.
3. Agregué la clase `LosSeisTropiezosDeCasosFijanMensajeYPosicionTests` que fija de punta a punta cada uno de los 6 tropiezos con su mensaje, línea, columna y caret visual formateado por `fragmento_de_error`.

### `tests/test_herramientas.py`
1. Amplié `test_el_validador_del_corpus_no_reimplementa_la_regla` para verificar que `tools.corpus.ETIQUETAS` y `tools.corpus.DETECCIONES` son exactamente los mismos objetos que `nucleo.caso.ETIQUETAS` y `nucleo.caso.DETECCIONES`.

### `README.md`
1. Actualizado mediante `python tools/cifras.py --actualizar` para reflejar el nuevo conteo de tests (604) y líneas de lenguaje.

---

## Salidas reales de las verificaciones

### 1. `python -m unittest discover -s tests -t . -q`
```
----------------------------------------------------------------------
Ran 604 tests in 10.818s

OK
```

### 2. `python tools/cifras.py`
```
CIFRAS OK
  cifras: 604 tests · 547/547 mutantes de medida · **2413 sitios de mutación de código** (2208 + 205 del motor Python).
  escala: **5721 líneas de lenguaje** (`nucleo/`, código y macros) y **256 negativas explícitas** (`raise`). Contra las 37 medidas universales escritas en él (225 líneas): **25,4 a 1**. 29 de las 37 pasan por una macro.
  corpus: **104 casos**: 70 defectos y 34 verdes correctos. De los defectos, 67 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 65 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5721 líneas de lenguaje y **256 negativas explícitas** (`raise`).
  deteccion: Los 70 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 51 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### 3. `python tools/corpus.py`
```
CORPUS OK · 104 casos · esquema, evidencia L0 y trazabilidad en regla
```

### 4. `python tools/aceptacion.py`
```
  ROJO  108-donde-compone-un-campo-por-vez     meta.donde_compone  (valor 3)
  ROJO  109-unir-conmuta-un-campo-por-vez      meta.unir_conmuta  (valor 3)
  ROJO  110-agrupar-sin-claves-es-el-resumen-global-un-campo-por-vez meta.agrupar_sin_claves_es_el_resumen_global  (valor 2)
  ROJO  111-una-macro-equivale-a-su-expansion-un-campo-por-vez meta.una_macro_equivale_a_su_expansion  (valor 3)
  ROJO  120-sintaxis-no-vuelve-igual           meta.sintaxis_ida_y_vuelta  (valor 1)
  verde 121-sintaxis-vuelve-exacta             meta.sintaxis_ida_y_vuelta  (valor 0)
  ROJO  122-sintaxis-revienta-al-leer          meta.sintaxis_ida_y_vuelta  (valor 1)
  ROJO  123-sintaxis-un-campo-por-vez          meta.sintaxis_ida_y_vuelta  (valor 3)
  ROJO  124-sintaxis-cubre-algebra-no-vuelve-igual meta.sintaxis_cubre_algebra  (valor 1)
  verde 125-sintaxis-cubre-algebra-vuelve-exacta meta.sintaxis_cubre_algebra  (valor 0)
  ROJO  126-sintaxis-cubre-algebra-un-campo-por-vez meta.sintaxis_cubre_algebra  (valor 4)
  ROJO  127-sintaxis-casos-no-vuelve-igual     meta.sintaxis_casos_ida_y_vuelta  (valor 1)
  verde 128-sintaxis-casos-vuelve-exacta       meta.sintaxis_casos_ida_y_vuelta  (valor 0)
  ROJO  129-sintaxis-casos-generados-no-vuelve-igual meta.sintaxis_casos_cubre_casos  (valor 1)
  verde 130-sintaxis-casos-generados-vuelve-exacta meta.sintaxis_casos_cubre_casos  (valor 0)
  ROJO  131-sintaxis-casos-un-campo-por-vez    meta.sintaxis_casos_ida_y_vuelta  (valor 4)
  ROJO  132-sintaxis-casos-generados-un-campo-por-vez meta.sintaxis_casos_cubre_casos  (valor 4)
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
  ROJO  025-mutante-de-codigo-sobreviviente    proceso.codigo_con_mutante_que_lo_mata  (valor 1)
  ROJO  026-mutante-de-codigo-equivalente-no-cuenta-como-muerte-ni-sobreviviente proceso.codigo_con_mutante_que_lo_mata  (valor 1)
  ROJO  027-ronda-de-codigo-sin-mutantes-no-concluye proceso.codigo_con_mutante_que_lo_mata  (valor 0)
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
  verde 109-mutantes-de-codigo-todos-muertos   proceso.codigo_con_mutante_que_lo_mata  (valor 0)
  verde 110-mutante-de-codigo-equivalente-declarado-verde proceso.codigo_con_mutante_que_lo_mata  (valor 0)
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

### 5. `python tools/diferencial.py`
```
simulacion.json · 4 mundos · origen: implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md

  ✓ acuerdo global: 4 escenarios (1 verdes / 3 rojos) · 0 desacuerdos
  ✓ estabilidad individual: 3 medidas × 4 escenarios · 0 cambios


DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

### 6. `python tools/trazar.py`
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

### 7. `python tools/metamorficas.py`
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

### 8. `python tools/sintaxis.py --verificar`
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

### 9. `python tools/mutar.py`
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

### 10. `python tools/mutar_codigo.py --objetivo nucleo/caso.py`
```
mutantes: 206 · murieron 206 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 6
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

---

## Qué NO hice y por qué

1. **No cambié la gramática ni introduje operadores nuevos**: la estructura de los casos (`.caso`) se mantuvo idéntica.
2. **No agregué validaciones redundantes o duplicadas**: `tools/corpus.py` reutiliza las listas cerradas `ETIQUETAS` y `DETECCIONES` expuestas por `nucleo/caso.py`.
3. **No alteré la decodificación interna de filas tabulares JSON válidas**: `_valores_fila` sigue manejando el flujo de decodificación JSON para enteros, booleanos y cadenas sin modificar el formato de filas válidas.
4. **No aflojé ninguna aserción**: todos los tests previos y nuevos fijan posición exacta y mensaje específico sin comodines.

---

## Lo que descubrí que no me pediste

1. **La plantilla en `tools/corpus.py` creaba casos inválidos para el lector**: Al hacer que el lector rechace etiquetas inventadas de inmediato, `tools/corpus.py --nuevo` fallaba al intentar cargar el archivo generado porque `PLANTILLA` contenía los marcadores `ETIQUETA` y `COMO_SE_DETECTO` en mayúsculas. Se solucionó colocando valores válidos por defecto (`falso_verde` y `mutacion`), tal como hace `tools/medida.py` con su propia plantilla.
2. **Fragilidad de `equivalentes.json` ante inserciones de código**: Al declarar las constantes `ETIQUETAS` y `DETECCIONES` al principio de `nucleo/caso.py`, los 6 mutantes equivalentes declarados en `equivalentes.json` quedaron desfasados por número de línea. `mutar_codigo.py` y `test_herramientas.py` validan activamente que cada equivalente coincida exactamente con un nodo del AST, por lo que fue necesario reapuntar las líneas y documentar el movimiento.
