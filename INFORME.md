# Informe de ejecución — Documentación del corpus en superficie

## Qué cambié, archivo por archivo, y por qué

- **`ORACLE-TUTORIAL-PRACTICO.md`**:
  - **Sección 0**: se actualizó la definición de superficie para abarcar tanto medidas (`.oracle`) como casos (`.caso`).
  - **Sección 7**: se reemplazaron los ejemplos en JSON crudo por su superficie canónica `.caso` (`001-verde-acumulativo`, `102-verificacion-vigente`, `004-testigos-duplicados`), generados con la herramienta. Se explicó que la superficie es cómo se escribe y el JSON cómo se guarda.
  - **Sección 8**:
    - Se actualizó el árbol de directorios de ejemplo mostrando `001-vencida-sin-nadie.caso` y `002-vencida-con-dueno.caso` junto a `tareas.vencida_sin_dueno.oracle`.
    - Se escribieron los dos casos de ejemplo de la sección 8.5 en superficie canónica `.caso`.
    - Se corrigió el id con `ñ` (`002-vencida-con-dueño` → `002-vencida-con-dueno`) en todos lados, explicitando en una línea que los identificadores son nombres de archivo y exigen caracteres ASCII para prevenir divergencias por normalización Unicode NFC contra NFD.
  - **Sección 9**: se incorporó `tools/corpus.py --nuevo <grupo/NNN-descripcion>` en la tabla de comandos y se actualizaron las referencias de formatos para medidas (`.oracle` y `.json`) y casos (`.caso` y `.json`).
  - **Sección 11**: se actualizó la definición de «superficie infija» en el glosario para incluir `.caso`.

- **`ESCRIBIR-UNA-MEDIDA.md`**:
  - Se explicitó que el sistema carga superficie (`.oracle` y `.caso`) y `.json` por igual sin paso de traducción.
  - En el flujo de arranque se actualizó el paso 1 para invocar el andamio existente: `python tools/corpus.py --nuevo proceso/0NN-lo-que-paso` (crea `corpus/proceso/0NN-lo-que-paso.caso`).
  - Se actualizó la sección de formatos para describir tanto el catálogo como el corpus, documentando `tools/corpus.py --nuevo` y las reglas de id ASCII para casos (`NNN-descripcion`).

- **`README.md`**:
  - En el mapa de estructura se aclaró que `catalogos/` y `corpus/` alojan archivos `.oracle`/`.caso` (autoría) y `.json` (almacenamiento).
  - En la sección de componentes se explicitó la coexistencia de ambos formatos y se sumó la referencia a `tools/corpus.py --nuevo`.

- **`ESPECIFICACION.md`**:
  - En §0 («La superficie tiene su propia versión») se aclaró que la regla de autoría en superficie y almacenamiento en JSON rige para medidas (`.oracle`) y casos (`.caso`), cargándose ambos sin traducción.
  - En §7 (criterio de aceptación 3) se aclaró que el corpus admite superficie `.caso` para autoría o `.json` para almacenamiento.

- **`corpus/README.md`**:
  - En la sección «Cómo se agrega un caso» se documentó el comando `python tools/corpus.py --nuevo <grupo/NNN-descripcion>` para generar el andamio en superficie `.caso`.

- **`ORACLE-PARA-NOTEBOOKLM.md`**:
  - Regenerado mediante `python tools/estudio.py --archivo ORACLE-PARA-NOTEBOOKLM.md` a partir de las fuentes actualizadas.

## Comandos que generaron cada bloque de caso

Todos los bloques cercados ```caso incluidos en la documentación se generaron ejecutando las herramientas del repositorio:

1. Bloque `001-verde-acumulativo` (en `ORACLE-TUTORIAL-PRACTICO.md` §7):
```bash
python -c 'from nucleo.caso import cargar_fuente_caso, imprimir; print(imprimir(cargar_fuente_caso("corpus/proceso/001-verde-acumulativo.caso")), end="")'
```

2. Bloque `102-verificacion-vigente` (en `ORACLE-TUTORIAL-PRACTICO.md` §7):
```bash
python -c 'from nucleo.caso import cargar_fuente_caso, imprimir; print(imprimir(cargar_fuente_caso("corpus/proceso/102-verificacion-vigente.caso")), end="")'
```

3. Bloque `004-testigos-duplicados` (en `ORACLE-TUTORIAL-PRACTICO.md` §7):
```bash
python -c 'from nucleo.caso import cargar_fuente_caso, imprimir; print(imprimir(cargar_fuente_caso("corpus/proceso/004-testigos-duplicados.json")), end="")'
```

4. Bloque `001-vencida-sin-nadie` (en `ORACLE-TUTORIAL-PRACTICO.md` §8.5):
```bash
python -c 'from nucleo.caso import leer, imprimir; print(imprimir(leer("""caso 001-vencida-sin-nadie:
    fecha: "2026-07-31"
    origen:
        repo: "mi-proyecto"
        commit: "ejemplo"
    titulo: "Una tarea vencida hace tres días y sin asignar"
    etiqueta: falso_verde
    sintoma:
        El tablero mostraba todo en orden porque nadie miraba las tareas sin dueño.
    como_se_detecto: persona
    medida: tareas.vencida_sin_dueno
    evidencia:
        tarea: id, vencida, asignada, dias_vencida
            "t1", true, false, 3
    leccion:
        Una tarea vencida sin dueño no aparece en ningún filtro habitual del tablero.
""")), end="")'
```

5. Bloque `002-vencida-con-dueno` (en `ORACLE-TUTORIAL-PRACTICO.md` §8.5):
```bash
python -c 'from nucleo.caso import leer, imprimir; print(imprimir(leer("""caso 002-vencida-con-dueno:
    fecha: "2026-07-31"
    origen:
        repo: "mi-proyecto"
        commit: "ejemplo"
    titulo: "Vencida pero con alguien encima — no debe dar rojo"
    etiqueta: verde_correcto
    sintoma:
        Una tarea vencida CON dueño asignado no es el defecto que esta medida busca.
    como_se_detecto: observacion
    medida: tareas.vencida_sin_dueno
    evidencia:
        tarea: id, vencida, asignada, dias_vencida
            "t2", true, true, 1
    leccion:
        Sin este caso, quitarle el filtro `asignada` a la medida no lo notaría nadie.
""")), end="")'
```

## Salida real de las verificaciones

### 1. `python -m unittest discover -s tests -t . -q`
```
----------------------------------------------------------------------
Ran 519 tests in 9.633s

OK
```

### 2. `python tools/cifras.py`
```
CIFRAS OK
  cifras: 519 tests · 535/535 mutantes de medida · **2261 sitios de mutación de código** (2056 + 205 del motor Python).
  escala: **5545 líneas de lenguaje** (`nucleo/`, código y macros) y **254 negativas explícitas** (`raise`). Contra las 36 medidas universales escritas en él (218 líneas): **25,4 a 1**. 29 de las 36 pasan por una macro.
  corpus: **99 casos**: 67 defectos y 32 verdes correctos. De los defectos, 64 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 62 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5545 líneas de lenguaje y **254 negativas explícitas** (`raise`).
  deteccion: Los 67 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 48 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### 3. `python tools/corpus.py`
```
CORPUS OK · 99 casos · esquema, evidencia L0 y trazabilidad en regla
```

### 4. `python tools/aceptacion.py`
```
  ROJO  055-logico-cortocircuito               meta.los_logicos_evaluan_todos_sus_operandos  (valor 1)
  verde 056-logico-evalua-todo                 meta.los_logicos_evaluan_todos_sus_operandos  (valor 0)
  ROJO  057-un-solo-cortocircuito              meta.los_logicos_evaluan_todos_sus_operandos  (valor 1)
  ROJO  061-ausencia-sin-requiere              meta.toda_medida_de_ausencia_declara_requiere  (valor 1)
  verde 062-ausencia-cubierta-o-no-aplica      meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  063-ausencia-sin-terminos-no-concluye  meta.toda_medida_de_ausencia_declara_requiere  (valor 1)
  ROJO  064-medida-sin-filtro-ni-grupo         meta.toda_medida_filtra_o_agrupa  (valor 1)
  verde 065-medida-filtra-o-agrupa             meta.toda_medida_filtra_o_agrupa  (valor 0)
  ROJO  066-filtro-sin-terminos-no-concluye    meta.toda_medida_filtra_o_agrupa  (valor 1)
  ROJO  067-umbral-de-igualdad                 meta.ningun_umbral_de_igualdad  (valor 1)
  verde 068-umbral-de-orden                    meta.ningun_umbral_de_igualdad  (valor 0)
  ROJO  069-filtro-no-toma-terminos-ajenos     meta.toda_medida_filtra_o_agrupa  (valor 1)
  ROJO  049-donde-agrego-filas                 meta.donde_nunca_agrega_filas  (valor 1)
  verde 050-donde-filtra-como-debe             meta.donde_nunca_agrega_filas  (valor 0)
  ROJO  051-agrupar-invento-un-grupo           meta.agrupar_no_agranda_la_relacion  (valor 1)
  verde 052-agrupar-colapsa-como-debe          meta.agrupar_no_agranda_la_relacion  (valor 0)
  ROJO  053-unir-perdio-un-par                 meta.unir_materializa_el_producto  (valor 1)
  verde 054-unir-materializa-el-producto       meta.unir_materializa_el_producto  (valor 0)
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

defectos que se pusieron rojos: 64 · verdes correctos: 32 · huecos declarados: 0
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

ACEPTACIÓN ✓ — 64 defectos en rojo, 32 verdes correctos, 0 huecos declarados sin tapar
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
evaluaciones trazadas: 87
hechos: 174 pasos · 330 nodos lógicos · 11 productos

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
equivalencias comprobadas: 325
  agrupar_sin_claves_es_el_resumen_global        5 (5 construidas, 0 del catálogo)
  donde_compone                                  1 (1 construidas, 0 del catálogo)
  sintaxis_casos_cubre_casos                     5 (5 construidas, 0 del catálogo)
  sintaxis_casos_ida_y_vuelta                   99 (0 construidas, 99 del catálogo)
  sintaxis_cubre_algebra                        94 (94 construidas, 0 del catálogo)
  sintaxis_ida_y_vuelta                         36 (0 construidas, 36 del catálogo)
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
medidas convertidas: 36
macros convertidas: 3
casos convertidos: 99
ida JSON: OK
vuelta texto: OK
caracteres: JSON 135414 · superficie 132861
puntuación: JSON 24219 (17,9%) · superficie 9906 (7,5%)
bloques de documentación: 16 verificados · 8 declarados como gramática o fragmento
```

### 9. `python tools/mutar.py`
```
mutantes de medida (medida × mutador): 535 · murieron 535 · sobrevivieron 0
  de los muertos: 412 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 123 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1864

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)
```

## Qué NO hice y por qué

- **No toqué código (`.py`), medidas (`.oracle`), casos (`.caso`) ni archivos JSON (`.json`)**:
  La consigna prohíbe tocar código o fixtures existentes para no entrar en conflicto con otras ramas activas. Todos los cambios se limitaron a la documentación (`.md`).
- **No toqué `PLAN-LENGUAJE.md` ni los `DECISION-*.md`**:
  Se preservaron intactos según las restricciones explícitas de `TAREA.md`.
- **No inventé sintaxis para los casos**:
  Cada bloque de caso se validó y formateó a través de las funciones canónicas `nucleo.caso.imprimir` y `nucleo.caso.leer`, comprobando el ida y vuelta exacto.
- **No toqué `vendor/` ni ejecuté comandos destructivos de git** (`git clean`, `git reset --hard`, `git push`, etc.).

## Hallazgos y observaciones

1. **Andamio de casos ya implementado**:
   La tarea pedía verificar si existía un andamio para crear casos en superficie antes de inventar uno o mandar a copiar archivos. En `tools/corpus.py` ya se encontraba implementado el comando `python tools/corpus.py --nuevo <grupo/NNN-descripcion>`, que crea la plantilla en formato `.caso` dentro de `corpus/<grupo>/<NNN-descripcion>.caso`. Se incorporó en todos los documentos pertinentes (`ESCRIBIR-UNA-MEDIDA.md`, `ORACLE-TUTORIAL-PRACTICO.md`, `README.md` y `corpus/README.md`).

2. **Verificación de bloques en `tools/sintaxis.py`**:
   `tools/sintaxis.py --verificar` comprueba que los bloques cercados con ```oracle correspondan a medidas canónicas verificables. Los bloques de caso etiquetados con ```caso mantienen coherencia sintáctica sin interferir con el verificador de medidas AST del metalenguaje, validándose su roundtrip mediante `nucleo.caso`.
