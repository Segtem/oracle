# Informe de implementación: comando unificado `oracle`

## Qué cambié y por qué

- `tools/cli.py` (nuevo): entry point unificado `oracle`. Envuelve las herramientas existentes sin reimplementar su lógica interna. Provee los subcomandos `init`, `nueva`, `caso`, `revisar`, `test`, `relaciones`, `escalares`, `expandir` y `--help`. Maneja la resolución de proyectos, banderas globales (`--proyecto`, `--confiar-escalares`, `--rapido`) y ejecuta `oracle test` discriminando verificaciones aplicables, verificaciones salteadas y fallas reales, terminando con un veredicto de una sola línea y código de salida honesto.
- `tools/oracle.py` (nuevo): alias directo que invoca `tools.cli.main()` para ejecución directa por script.
- `pyproject.toml`: registro del script de consola `oracle = "oracle_metalenguaje.tools.cli:main"` en `[project.scripts]`.
- `tools/sintaxis.py`: ajuste en `_rutas_macros` para no asumir que todo proyecto tiene un directorio `nucleo/macros` físico, permitiendo que proyectos externos sin macros corran la verificación de sintaxis de sus catálogos y corpus sin fallar por ruta inexistente.
- `tools/medida.py`: actualización del mensaje orientador en `nueva()` para sugerir `oracle revisar <archivo>` en vez de la invocación larga por ruta `python tools/medida.py --proyecto ...`.
- `tools/corpus.py`: actualización del mensaje orientador en `nuevo()` para sugerir `oracle test` en vez de `python tools/corpus.py --proyecto ...`.
- `tools/verificar_instalacion.py`: inclusión de `oracle` en la tupla de `entry_points` verificados en el wheel empaquetado.
- `tests/test_cli.py` (nuevo): suite de regresiones para el comando unificado: `oracle --help`, `oracle init` con aceptación por `oracle test`, discriminación de «no aplica» vs «falla» en `diferencial`, comportamiento de `--rapido` informando en el veredicto que se omitió la mutación, validación de identificadores en `nueva` y `caso`, fail-closed ante `escalares.py` no confiado, y ejecución como subproceso.
- `README.md`: actualización automática de la cifra de tests (572) vía `python tools/cifras.py --actualizar`.

---

## Salidas reales de las verificaciones de DOCTRINA.md

### 1. `python -m unittest discover -s tests -t . -q`

```
Proyecto Oracle inicializado en /tmp/tmppdydgu61:
  · catalogos/
  · corpus/
  · diferencial/
  · oracle.json

Próximos pasos:
  1. Creá una medida:  oracle nueva <dominio.nombre>
  2. Creá un caso:     oracle caso <grupo/id>
  3. Verificá todo:    oracle test
Proyecto Oracle inicializado en /tmp/tmp9fvoxpsi:
  · catalogos/
  · corpus/
  · diferencial/
  · oracle.json

Próximos pasos:
  1. Creá una medida:  oracle nueva <dominio.nombre>
  2. Creá un caso:     oracle caso <grupo/id>
  3. Verificá todo:    oracle test
creada: catalogos/demo/demo.sola.oracle

Reemplazá RELACION, CAMPO y los dos textos en MAYÚSCULAS. Después:
  oracle revisar catalogos/demo/demo.sola.oracle
Proyecto Oracle inicializado en /tmp/tmpe8dlv8ru:
  · catalogos/
  · corpus/
  · diferencial/
  · oracle.json

Próximos pasos:
  1. Creá una medida:  oracle nueva <dominio.nombre>
  2. Creá un caso:     oracle caso <grupo/id>
  3. Verificá todo:    oracle test
Proyecto Oracle inicializado en /tmp/tmp9ew52947:
  · catalogos/
  · corpus/
  · diferencial/
  · oracle.json

Próximos pasos:
  1. Creá una medida:  oracle nueva <dominio.nombre>
  2. Creá un caso:     oracle caso <grupo/id>
  3. Verificá todo:    oracle test
creada: catalogos/demo/demo.prueba.oracle

Reemplazá RELACION, CAMPO y los dos textos en MAYÚSCULAS. Después:
  oracle revisar catalogos/demo/demo.prueba.oracle
creado: corpus/demo/001-rojo.caso

Reemplazá los marcadores en MAYÚSCULAS. Después:
  oracle test
Proyecto Oracle inicializado en /tmp/tmppu5m2119:
  · catalogos/
  · corpus/
  · diferencial/
  · oracle.json

Próximos pasos:
  1. Creá una medida:  oracle nueva <dominio.nombre>
  2. Creá un caso:     oracle caso <grupo/id>
  3. Verificá todo:    oracle test
----------------------------------------------------------------------
Ran 572 tests in 9.419s

OK
```

### 2. `python tools/cifras.py`

```
CIFRAS OK
  cifras: 572 tests · 547/547 mutantes de medida · **2394 sitios de mutación de código** (2189 + 205 del motor Python).
  escala: **5674 líneas de lenguaje** (`nucleo/`, código y macros) y **256 negativas explícitas** (`raise`). Contra las 37 medidas universales escritas en él (225 líneas): **25,2 a 1**. 29 de las 37 pasan por una macro.
  corpus: **104 casos**: 70 defectos y 34 verdes correctos. De los defectos, 67 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 65 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5674 líneas de lenguaje y **256 negativas explícitas** (`raise`).
  deteccion: Los 70 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 51 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### 3. `python tools/corpus.py`

```
CORPUS OK · 104 casos · esquema, evidencia L0 y trazabilidad en regla
```

### 4. `python tools/aceptacion.py`

```
catálogo: 37 medidas · corpus: 104 casos

  ROJO  049-donde-agrego-filas                 meta.donde_nunca_agrega_filas  (valor 1)
  verde 050-donde-filtra-como-debe             meta.donde_nunca_agrega_filas  (valor 0)
  ROJO  051-agrupar-invento-un-grupo           meta.agrupar_no_agranda_la_relacion  (valor 1)
  verde 052-agrupar-colapsa-como-debe          meta.agrupar_no_agranda_la_relacion  (valor 0)
  ROJO  053-unir-perdio-un-par                 meta.unir_materializa_el_producto  (valor 1)
  verde 054-unir-materializa-el-producto       meta.unir_materializa_el_producto  (valor 0)
  ROJO  055-logico-cortocircuito               meta.los_logicos_evaluan_todos_sus_operandos  (valor 1)
  verde 056-logico-evalua-todo                 meta.los_logicos_evaluan_todos_sus_operandos  (valor 0)
  ROJO  057-un-solo-cortocircuito              meta.los_logicos_evaluan_todos_sus_operandos  (valor 1)
  ROJO  061-ausencia-sin-requiere              meta.toda_medida_de_ausencia_declara_requiere  (valor 1)
  verde 062-ausencia-cubierta-o-no-aplica      meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  063-ausencia-sin-terminos-no-concluye  meta.toda_medida_de_ausencia_declara_requiere  (valor 1)
  ROJO  064-medida-sin-filtro-ni-grupo         meta.toda_medida_filtra_o_agrupa  (valor 1)
  verde 065-medida-filtra-o-agrupa             meta.toda_medida_filtra_o_agrupa  (valor 0)
  ROJO  066-filtro-sin-terminos-no-concluye    meta.toda_medida_filtra_o_agrupa  (valor 1)
  ROJO  068-umbral-de-orden                    meta.ningun_umbral_de_igualdad  (valor 1)
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

---

## Recorrido completo desde un directorio vacío en `/tmp`

El siguiente recorrido reproduce íntegramente la experiencia de un usuario que nunca vio el repositorio, desde un directorio temporal vacío `/tmp/recorrido-oracle-humano`, sin abrir ni consultar el código interno de Oracle.

### 1. Inicializar el proyecto

```
$ oracle init
Proyecto Oracle inicializado en /tmp/recorrido-oracle-humano:
  · catalogos/
  · corpus/
  · diferencial/
  · oracle.json

Próximos pasos:
  1. Creá una medida:  oracle nueva <dominio.nombre>
  2. Creá un caso:     oracle caso <grupo/id>
  3. Verificá todo:    oracle test
```

### 2. Pedir ayuda

```
$ oracle --help
Oracle — metalenguaje para medir evidencia, alcance y mutación.

Uso:
  oracle init [ruta]                      Inicializa un proyecto nuevo
  oracle nueva <dominio.nombre>          Crea una medida con plantilla lista para editar
  oracle caso <grupo/id>                 Crea un caso de prueba en el corpus
  oracle revisar <archivo>               Revisa y evalúa una medida suelta
  oracle test [--rapido]                 Ejecuta la secuencia completa de verificación
  oracle relaciones                      Muestra las relaciones y campos observados
  oracle escalares                       Muestra las funciones escalares y operadores
  oracle expandir <archivo>              Muestra la forma canónica de una macro
  oracle --help                          Muestra esta ayuda

Banderas comunes:
  --proyecto <ruta>      Ruta al proyecto (por defecto: directorio actual o $ORACLE_PROYECTO)
  --confiar-escalares    Autoriza la ejecución de funciones en `escalares.py`
  --rapido               En `oracle test`, saltea la mutación de medidas
```

### 3. Verificar el proyecto vacío

```
$ oracle test
CORPUS OK · 0 casos · esquema y evidencia L0 en regla
SINTAXIS: salteado (sin medidas ni casos todavía)
ACEPTACIÓN: salteado (sin medidas ni casos todavía)
DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)
MUTACIÓN: salteada (sin medidas todavía)

VEREDICTO: VERDE (proyecto vacío: 0 medidas, 0 casos)
```

### 4. Crear una medida nueva

```
$ oracle nueva tareas.vencida
creada: catalogos/tareas/tareas.vencida.oracle

Reemplazá RELACION, CAMPO y los dos textos en MAYÚSCULAS. Después:
  oracle revisar catalogos/tareas/tareas.vencida.oracle
```

Se edita `catalogos/tareas/tareas.vencida.oracle` con la regla de dominio:
```oracle
ninguno tareas.vencida:
    de tarea t
    donde t.vencida == true
    umbral <= 0 porque "ninguna tarea puede quedar vencida sin atender"
    alcance "NO ve tareas archivadas ni futuras"
```

### 5. Crear el caso de prueba para el defecto

```
$ oracle caso tareas/001-tarea-vencida
creado: corpus/tareas/001-tarea-vencida.caso

Reemplazá los marcadores en MAYÚSCULAS. Después:
  oracle test
```

Se edita `corpus/tareas/001-tarea-vencida.caso` con la evidencia del defecto:
```caso
caso 001-tarea-vencida:
    fecha: "2026-08-26"
    origen:
        repo: "mi-proyecto"
        commit: "local"
    titulo: "Tarea vencida detectada"
    etiqueta: falso_verde
    sintoma:
        Una tarea vencida no fue alertada.
    como_se_detecto: persona
    medida: tareas.vencida
    evidencia:
        tarea: vencida
            true
    leccion:
        Toda tarea vencida debe activar la alarma.
```

### 6. Revisar la medida suelta contra el corpus existente (pone en rojo)

```
$ oracle revisar catalogos/tareas/tareas.vencida.oracle
✓ bien declarada: tareas.vencida   (forma: ninguno)
    umbral   <= 0
    porque   ninguna tarea puede quedar vencida sin atender
    alcance  NO ve tareas archivadas ni futuras

contra la evidencia que hay: 0 verde · 1 rojo · 0 error

  se pone roja con «001-tarea-vencida»:
    ✗ tareas.vencida                                      1 (<= 0)
      → t={'vencida': True}

⚠ nunca se pone verde. Probablemente la condición esté invertida: el `donde` tiene
  que seleccionar lo que OFENDE, no lo que está bien.
```

### 7. Agregar el caso de polaridad positiva para fijar la medida

```
$ oracle caso tareas/002-tarea-al-dia
creado: corpus/tareas/002-tarea-al-dia.caso

Reemplazá los marcadores en MAYÚSCULAS. Después:
  oracle test
```

Se edita `corpus/tareas/002-tarea-al-dia.caso` con la evidencia de tarea en fecha:
```caso
caso 002-tarea-al-dia:
    fecha: "2026-08-26"
    origen:
        repo: "mi-proyecto"
        commit: "local"
    titulo: "Tarea en fecha correcta"
    etiqueta: verde_correcto
    sintoma:
        La tarea está al día y la medición debe dar verde.
    como_se_detecto: observacion
    medida: tareas.vencida
    evidencia:
        tarea: vencida
            false
    leccion:
        Aporta la polaridad positiva para fijar la medida.
```

### 8. Revisar la medida discriminando ambas polaridades

```
$ oracle revisar catalogos/tareas/tareas.vencida.oracle
✓ bien declarada: tareas.vencida   (forma: ninguno)
    umbral   <= 0
    porque   ninguna tarea puede quedar vencida sin atender
    alcance  NO ve tareas archivadas ni futuras

contra la evidencia que hay: 1 verde · 1 rojo · 0 error

  se pone roja con «001-tarea-vencida»:
    ✗ tareas.vencida                                      1 (<= 0)
      → t={'vencida': True}

✓ discrimina: hay evidencia que la pone roja y evidencia que la pone verde.
  Para que quede fijada, agregá al corpus un caso de cada polaridad.
```

### 9. Ejecutar `oracle test --rapido` (omite mutación)

```
$ oracle test --rapido
CORPUS OK · 2 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 2 casos

catálogo: 1 medidas · corpus: 2 casos

  ROJO  001-tarea-vencida                      tareas.vencida  (valor 1)
  verde 002-tarea-al-dia                       tareas.vencida  (valor 0)

defectos que se pusieron rojos: 1 · verdes correctos: 1 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 1 defectos en rojo, 1 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

MUTACIÓN: salteada por --rapido

VEREDICTO: VERDE (rápido: se salteó la mutación)
```

### 10. Ejecutar `oracle test` completo (con mutación de medidas)

```
$ oracle test
CORPUS OK · 2 casos · esquema, evidencia L0 y trazabilidad en regla

SINTAXIS OK · 1 medidas · 0 macros · 2 casos

catálogo: 1 medidas · corpus: 2 casos

  ROJO  001-tarea-vencida                      tareas.vencida  (valor 1)
  verde 002-tarea-al-dia                       tareas.vencida  (valor 0)

defectos que se pusieron rojos: 1 · verdes correctos: 1 · huecos declarados: 0

nivel meta — el marco medido con sus propias medidas:

ACEPTACIÓN ✓ — 1 defectos en rojo, 1 verdes correctos, 0 huecos declarados sin tapar

DIFERENCIAL: salteado (el proyecto no tiene fixtures en diferencial/ todavía)

mutantes de medida (medida × mutador): 7 · murieron 7 · sobrevivieron 0
  de los muertos: 7 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 0 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 14

sin políticas meta activas — se informa sólo el resultado operativo

VEREDICTO: VERDE (completo: todas las verificaciones en regla, 0 mutantes sobrevivientes)
```

### 11. Explorar hechos y escalares con los comandos auxiliares

```
$ oracle relaciones
RELACIONES que se pueden medir hoy:

  tarea
      vencida                      bool
      · aparece en: 001-tarea-vencida, 002-tarea-al-dia

Un hecho nuevo se agrega desde su SENSOR, no acá: el sensor produce, el álgebra juzga.

$ oracle escalares
FUNCIONES ESCALARES declaradas (el mecanismo de UDF):

  cerca/2
      Distancia absoluta entre dos cantidades. Es el reemplazo de la igualdad exacta.
  contiene/2
      ¿`aguja` aparece en `texto`? Sensible a mayúsculas a propósito: se usa para exigir que un
  mas/2
      Suma. Es aritmética sobre cantidades medidas, igual que `mas`: no es de ningún dominio.
  menos/2
      
  por/2
      Producto. Aritmética sobre cantidades medidas, igual que `mas`: no es de ningún dominio.

COMPARADORES: == != < <= > >=
LÓGICOS: y  o  no
AGREGADOS: contar max min promedio suma
ACCESORES: ["campo", alias, nombre] · ["hecho", alias] · ["col", nombre]
OPERADORES: de · donde · unir · resumen   (con y agrupar todavía no tienen usuario)
```

---

## Qué NO hice y por qué

1. **No toqué `nucleo/` ni alteré el álgebra**: la tarea es de superficie de uso y empaquetamiento, no de lenguaje. El motor semántico permaneció inalterado.
2. **No toqué `catalogos/` ni `corpus/` ni `vendor/`**: se preservaron todos los archivos existentes.
3. **No rompí los entry points existentes**: `oracle-aceptacion`, `oracle-corpus`, `oracle-diferencial`, `oracle-estudio`, `oracle-medida`, `oracle-mutar` y `oracle-mutar-codigo` siguen funcionando de forma idéntica; `oracle` se sumó como entrada primaria.
4. **No reimplementé verificadores ni algoritmos de mutación**: `oracle test` llama a `corpus.verificar`, `sintaxis.verificar_catalogo`, `aceptacion._ejecutar`, `diferencial._ejecutar` y `mutar._ejecutar`.

---

## Hallazgos y discrepancias no solicitadas

1. **Falta de `macros/` en proyectos externos en `sintaxis.py`**: `tools/sintaxis.py` llamaba incondicionalmente a `(raiz / "nucleo" / "macros").iterdir()`. En cualquier proyecto externo (que no tiene `nucleo/macros`), `sintaxis.py --verificar` reventaba con `FileNotFoundError`. Se ajustó `_rutas_macros` para buscar `nucleo/macros` si existe, luego `macros/` si existe, o devolver lista vacía en caso contrario.
2. **Proyecto vacío recién inicializado y `aceptacion.py`**: `tools/aceptacion.py` aborta con `ACEPTACIÓN NO APLICABLE — SIN CASOS` devolviendo código de salida 1 cuando el corpus está vacío. Sin embargo, para un proyecto nuevo recién creado con `oracle init`, `oracle test` debe dar verde indicando que el proyecto está limpio y sin medidas rotas. `tools/cli.py` maneja este caso base de proyecto vacío sin enmascarar errores cuando sí existen medidas sin casos.
