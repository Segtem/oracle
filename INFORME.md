# Informe de tarea: Documentación superficie-primero

## Qué cambié, archivo por archivo, y por qué

### 1. `ESCRIBIR-UNA-MEDIDA.md`
- Se reescribió el documento con enfoque **superficie infija primero**. Se incluyó explícitamente la regla rectora: *«La superficie infija es cómo se escribe; el JSON es cómo se guarda.»*.
- Todos los ejemplos de medidas que se presentaban en formato JSON anidado pasaron a la superficie infija canónica y a macros (`ninguno`, `peor`, `ninguno-par`).
- Se conservó la explicación del formato JSON como almacenamiento, detallando su homoiconicidad (el JSON es el AST directo del lenguaje) y cómo esto habilita el nivel **L2** (medidas que juzgan medidas).
- Se documentó cómo traducir entre formatos con `python tools/sintaxis.py --imprimir <archivo.json>` y `python tools/sintaxis.py --leer <archivo.oracle>`.
- Se preservaron todos los principios innegociables: obligación de `umbral` con defensa escrita (`porque`), `alcance`, cláusula `requiere` para evitar falsos verdes ante ausencia de evidencia, prohibición de umbrales `==`, e imposibilidad de componer medidas (`DECISION-002`).

### 2. `ORACLE-TUTORIAL-PRACTICO.md`
- Se reescribió el tutorial completo para enseñar a escribir medidas en la superficie infija desde la sección 0 hasta la 8.
- Se incorporó la regla rectora al inicio: *«La superficie infija es cómo se escribe; el JSON es cómo se guarda.»*.
- Se reemplazaron todas las definiciones de sintaxis de los cinco operadores (`de`, `donde`, `unir`, `agrupar`, `resumen`), accesores de campos (`a.volumen`, `hecho(a)`, `col(reales)`) y macros (`ninguno`, `peor`, `ninguno-par`) por bloques en la superficie infija de autoría.
- Cada bloque de código fue generado y verificado contra `tools/sintaxis.py`.
- Se actualizó la tabla de comandos en la sección 9 incorporando las opciones `--imprimir`, `--leer` y `--verificar` de `tools/sintaxis.py`.

### 3. `ORACLE-PARA-NOTEBOOKLM.md`
- Se regeneró el paquete de estudio integral mediante `python tools/estudio.py --archivo ORACLE-PARA-NOTEBOOKLM.md`, incorporando las actualizaciones de `ESCRIBIR-UNA-MEDIDA.md`.

---

## Comandos que generaron cada bloque de código de la superficie

Todos los bloques de superficie infija incluidos en la documentación fueron generados por la herramienta `tools/sintaxis.py` y verificados en ida y vuelta (`leer` -> `imprimir`).

### Bloques de `ESCRIBIR-UNA-MEDIDA.md`

1. **Macro `ninguno` (`proceso.test_con_mutante_que_lo_mata`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["ninguno", "proceso.test_con_mutante_que_lo_mata", "mutante", "m", ["y", ["==", ["campo", "m", "detecciones_conductuales"], 0], ["==", ["campo", "m", "rechazos_del_algebra"], 0]], "un mutante que sobrevive es un test que no discrimina", "cuenta mutantes DECLARADOS. NO ve los que nadie escribió"]""")), end="")'
```

2. **Macro `peor` (`snap.grilla`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["peor", "snap.grilla", "pieza", "a", ["desvio_de_grilla", ["hecho", "a"], 100.0], 1.0, "por debajo de 1 cm el desvío no se ve", "desvío del PIVOTE. NO ve si el pivote está bien puesto dentro de la malla"]""")), end="")'
```

3. **Forma canónica 1 (`proceso.test_con_mutante_que_lo_mata`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["medida", "proceso.test_con_mutante_que_lo_mata", ["desde", ["de", "mutante", "m"], ["donde", ["y", ["==", ["campo", "m", "detecciones_conductuales"], 0], ["==", ["campo", "m", "rechazos_del_algebra"], 0]]]], ["resumen", "contar", 1], ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina: pasa con el código roto"], ["alcance", "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los que nadie escribió"]]""")), end="")'
```

4. **Forma canónica 2 (`snap.grilla`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["medida", "snap.grilla", ["desde", ["de", "pieza", "a"], ["donde", [">", ["desvio_de_grilla", ["hecho", "a"], 100.0], 1.0]]], ["resumen", "max", ["desvio_de_grilla", ["hecho", "a"], 100.0]], ["umbral", "<=", 1.0, "por debajo de 1 cm el desvío no se ve"], ["alcance", "desvío del PIVOTE. NO ve si el pivote está bien puesto dentro de la malla"]]""")), end="")'
```

5. **Forma canónica 3 (`vault.nombre_unico_en_el_vault`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["medida", "vault.nombre_unico_en_el_vault", ["desde", ["unir", ["de", "documento", "a"], ["de", "documento", "b"]], ["donde", ["y", ["==", ["campo", "a", "nombre"], ["campo", "b", "nombre"]], ["!=", ["campo", "a", "carpeta"], ["campo", "b", "carpeta"]]]]], ["resumen", "contar", 1], ["umbral", "<=", 0, "un wikilink apunta por NOMBRE y no por ruta: dos homónimos dejan el enlace a cara o cruz"], ["alcance", "NO ve nombres parecidos pero distintos, que confunden aunque no rompan un enlace"]]""")), end="")'
```

### Bloques de `ORACLE-TUTORIAL-PRACTICO.md`

1. **Ejemplo canónico introductorio (`proceso.test_con_mutante_que_lo_mata`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["medida", "proceso.test_con_mutante_que_lo_mata", ["desde", ["de", "mutante", "m"], ["donde", ["y", ["==", ["campo", "m", "detecciones_conductuales"], 0], ["==", ["campo", "m", "rechazos_del_algebra"], 0]]]], ["resumen", "contar", 1], ["umbral", "<=", 0, "un mutante que sobrevive es un test que no discrimina: pasa igual con el código roto"], ["alcance", "cuenta mutantes DECLARADOS que sobrevivieron. NO ve los mutadores que nadie escribió"]]""")), end="")'
```

2. **`unir` (`vault.nombre_unico_en_el_vault`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["medida", "vault.nombre_unico_en_el_vault", ["desde", ["unir", ["de", "documento", "a"], ["de", "documento", "b"]], ["donde", ["y", ["==", ["campo", "a", "nombre"], ["campo", "b", "nombre"]], ["!=", ["campo", "a", "carpeta"], ["campo", "b", "carpeta"]]]]], ["resumen", "contar", 1], ["umbral", "<=", 0, "porque"], ["alcance", "alcance"]]""")), end="")'
```

3. **`agrupar` (`proceso.modulo_con_consumidor`)**:
```bash
python tools/sintaxis.py --imprimir perfiles/python/catalogos/proceso/proceso.modulo_con_consumidor.json
```

4. **Macro `ninguno` (`proceso.test_con_mutante_que_lo_mata`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["ninguno", "proceso.test_con_mutante_que_lo_mata", "mutante", "m", ["y", ["==", ["campo", "m", "detecciones_conductuales"], 0], ["==", ["campo", "m", "rechazos_del_algebra"], 0]], "un mutante que sobrevive es un test que no discrimina", "cuenta mutantes DECLARADOS. NO ve los que nadie escribió"]""")), end="")'
```

5. **Macro `peor` (`snap.grilla`) y su expansión canónica**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["peor", "snap.grilla", "pieza", "a", ["desvio_de_grilla", ["hecho", "a"], 100.0], 1.0, "por debajo de 1 cm el desvío no se ve y no produce juntas visibles en una pieza de 4 m", "desvío del PIVOTE respecto de la grilla. NO ve si el pivote está donde debería dentro de la malla"]""")), end="")'
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["medida", "snap.grilla", ["desde", ["de", "pieza", "a"], ["donde", [">", ["desvio_de_grilla", ["hecho", "a"], 100.0], 1.0]]], ["resumen", "max", ["desvio_de_grilla", ["hecho", "a"], 100.0]], ["umbral", "<=", 1.0, "por debajo de 1 cm el desvío no se ve y no produce juntas visibles en una pieza de 4 m"], ["alcance", "desvío del PIVOTE respecto de la grilla. NO ve si el pivote está donde debería dentro de la malla"]]""")), end="")'
```

6. **Macro `ninguno-par` (`tareas.misma_persona_sobrecargada_el_mismo_dia`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["ninguno-par", "tareas.misma_persona_sobrecargada_el_mismo_dia", "tarea", "a", "b", ["y", ["==", ["campo", "a", "dueno"], ["campo", "b", "dueno"]], ["==", ["campo", "a", "vence"], ["campo", "b", "vence"]], ["!=", ["campo", "a", "id"], ["campo", "b", "id"]]], "dos tareas del mismo día para la misma persona compiten por las mismas horas", "ve coincidencia de fecha y dueño. NO ve cuánto dura cada tarea ni si el día alcanza igual"]""")), end="")'
```

7. **Ejemplo 5.2 (`snap.yaw`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["peor", "snap.yaw", "pieza", "a", ["desvio_de_paso", ["campo", "a", "yaw"], 90.0], 0.5, "medio grado en una pieza de 4 m da ~3 cm en la punta: el límite donde una junta se abre a la vista", "sólo el YAW contra su paso. NO ve pitch ni roll, ni si la pieza mira al lado correcto"]""")), end="")'
```

8. **Ejemplo 5.3 (`colocacion.interpenetracion`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["medida", "colocacion.interpenetracion", ["desde", ["unir", ["de", "pieza", "a"], ["de", "vecina", "b"]], ["donde", ["y", ["no", ["es_fondo", ["hecho", "b"]]], [">", ["penetracion", ["hecho", "a"], ["hecho", "b"]], 0]]]], ["resumen", "max", ["penetracion", ["hecho", "a"], ["hecho", "b"]]], ["umbral", "<=", 0, "`penetracion` ya descuenta la tolerancia de contacto: tocarse da 0 y clavarse da >0"], ["alcance", "solape de AABB entre piezas de escala comparable. NO ve la malla real, oclusión visual, ni si la pieza quedó flotando"]]""")), end="")'
```

9. **Ejemplo 5.4 (`snap.comparte_cara`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["medida", "snap.comparte_cara", ["desde", ["unir", ["de", "pieza", "a"], ["de", "objetivo", "b"]]], ["resumen", "min", ["solape_lateral_minimo", ["hecho", "a"], ["hecho", "b"]]], ["umbral", ">", 1.0, "el solape lateral debe superar la tolerancia de 1 cm: tocar una arista o estar en diagonal no cuenta"], ["alcance", "solape de AABB en los dos ejes laterales. NO ve cuánto de la cara real de la malla coincide"]]""")), end="")'
```

10. **Ejemplo 5.5 (`simulacion.la_traza_no_tiene_huecos`)**:
```bash
python tools/sintaxis.py --imprimir catalogos/simulacion/simulacion.la_traza_no_tiene_huecos.json
```

11. **Ejemplo 5.6 (`meta.toda_medida_esta_fijada`)**:
```bash
python tools/sintaxis.py --imprimir catalogos/meta/meta.toda_medida_esta_fijada.json
```

12. **Proyecto end-to-end (`tareas.vencida_sin_dueño`)**:
```bash
python -c 'import json; from tools.sintaxis import imprimir; print(imprimir(json.loads("""["ninguno", "tareas.vencida_sin_dueño", "tarea", "t", ["y", ["==", ["campo", "t", "vencida"], true], ["==", ["campo", "t", "asignada"], false]], "una tarea vencida sin dueño no la va a hacer nadie: el atraso queda invisible hasta que alguien la busca a mano", "ve sólo el par vencida+sin-dueño. NO ve si la persona asignada realmente puede resolverla, ni cuán vencida está"]""")), end="")'
```

---

## Salida real de cada verificación

### 1. `python -m unittest discover -s tests -t . -q`
```
----------------------------------------------------------------------
Ran 456 tests in 9.075s

OK
```

### 2. `python tools/cifras.py`
```
CIFRAS OK
  cifras: 456 tests · 406/406 mutantes de medida · **1404 sitios de mutación de código** (1199 + 205 del motor Python).
  escala: **3933 líneas de lenguaje** (`nucleo/`, código y macros) y **206 negativas explícitas** (`raise`). Contra las 33 medidas universales escritas en él (302 líneas): **13,0 a 1**. 26 de las 33 pasan por una macro.
  corpus: **90 casos**: 61 defectos y 29 verdes correctos. De los defectos, 58 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 56 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 3933 líneas de lenguaje y **206 negativas explícitas** (`raise`).
  deteccion: Los 61 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 42 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### 3. `python tools/corpus.py`
```
CORPUS OK · 90 casos · esquema, evidencia L0 y trazabilidad en regla
```

### 4. `python tools/aceptacion.py`
```
  ROJO  060-sin-evidencia                      meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
  ROJO  061-ausencia-que-no-declara-requiere   meta.toda_medida_de_ausencia_declara_requiere  (valor 1)
  verde 062-ausencia-con-requiere              meta.toda_medida_de_ausencia_declara_requiere  (valor 0)
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

### 5. `python tools/diferencial.py`
```
simulacion.json · 4 mundos · origen: implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md

  ✓ acuerdo global: 4 escenarios (1 verdes / 3 rojos) · 0 desacuerdos
  ✓ estabilidad individual: 3 medidas × 4 escenarios · 0 cambios


DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

### 6. `python tools/trazar.py`
```
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

### 7. `python tools/metamorficas.py`
```
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

### 8. `python tools/sintaxis.py --verificar`
```
medidas convertidas: 33
ida JSON: OK
vuelta texto: OK
caracteres: JSON 24430 · superficie 23859
puntuación: JSON 3409 (14,0%) · superficie 910 (3,8%)
```
*(Nota: ver sección de descubrimientos sobre el código de salida).*

### 9. `python tools/mutar.py`
```
mutantes de medida (medida × mutador): 406 · murieron 406 · sobrevivieron 0
  de los muertos: 327 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 79 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1477

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)
```

---

## Qué NO hice y por qué

1. **No toqué ningún archivo de código (`.py`) ni catálogos JSON:** `TAREA.md` prohíbe explícitamente modificar código Python o datos JSON de catálogo para no pisar otras ramas activas.
2. **No toqué `README.md`, `ESPECIFICACION.md` ni `PLAN-LENGUAJE.md`:** La tarea los designó explícitamente como fuera de alcance.
3. **No inventé sintaxis de superficie:** Cada bloque utilizado es parseable por `tools/sintaxis.py` y genera el AST canónico exacto.

---

## Lo que descubrí que no me pediste

1. **Hardcodeo de cantidad de medidas en `tools/sintaxis.py`:**
   En `tools/sintaxis.py`, línea 819:
   ```python
   ok = informe["json_igual"] and informe["texto_igual"] and informe["medidas"] == 29
   ```
   La función `_rutas_catalogo()` busca tanto en `catalogos/` (29 medidas) como en `perfiles/*/catalogos/` (4 medidas), sumando un total de 33 medidas. Aunque la conversión ida y vuelta da `OK` para las 33 medidas (`ida JSON: OK`, `vuelta texto: OK`), el script sale con código de error `1` porque espera `== 29` en lugar de `== len(informe["filas"])` (o 33). Como la consigna prohíbe tocar código `.py`, se deja documentado.

2. **Gramática de identificadores restringida a ASCII:**
   El lexer de `tools/sintaxis.py` usa `IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")`. Si en un ejemplo de tutorial o medida se usa una tilde o `ñ` en un campo (por ejemplo `a.dueño`), el parser falla con `se esperaba expresión; llegó 'ñ'`. Por ello, en el tutorial se utilizó `a.dueno` para el acceso a campos dentro de expresiones.
