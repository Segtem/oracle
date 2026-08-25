# Informe de mutación: `nucleo/version.py` y `nucleo/macro.py`

## Qué cambié, archivo por archivo, y por qué

- `tests/test_herramientas.py`:
  - Se agregó el test `test_version_es_inmutable` dentro de `VersionDelAlgebra` para comprobar que la clase `Version` es inmutable y levanta `dataclasses.FrozenInstanceError` al intentar reasignar sus atributos `mayor` o `menor`. Esto mató el mutante `nucleo/version.py:37:18:constante` (`frozen=True` → `frozen=False`).
  - Se agregó la aserción `self.assertFalse(compatible(parsear("0.9"), parsear("1.0")))` en `test_compatible_exige_la_misma_mayor_y_menor_al_menos_pedida` para fijar el borde simétrico donde la versión requerida tiene menor número mayor que la disponible.

- `tests/test_macro.py`:
  - Se agregó el test `test_cargar_macros_ignora_archivos_sin_extension_declarada_y_subdirectorios` dentro de `DeclaracionTests` para comprobar que `cargar_macros` filtra y sólo carga archivos regulares con extensión `.json` o `.oracle`, descartando archivos sin extensión de macro (como `.txt`) y subdirectorios (incluso si tienen sufijos `.json` o `.oracle`). Esto mató el mutante `nucleo/macro.py:253:22:booleano` (`and` ↔ `or`).

- `README.md`:
  - Actualizado automáticamente mediante `python tools/cifras.py --actualizar` para reflejar el nuevo recuento de tests (535 tests en lugar de 533).

---

## Reparto de los sobrevivientes encontrados

Se detectaron inicialmente 2 sobrevivientes (1 en `version.py` y 1 en `macro.py`), ambos clasificados como falta de test y resueltos agregando las aserciones correspondientes:

1. **Falta un test (2 sobrevivientes)**:
   - `nucleo/version.py:37:18:constante` (`@dataclass(frozen=True)` → `False`). Ningún test ejercitaba la inmutabilidad de la clase de datos `Version`. Resuelto con `test_version_es_inmutable` en `tests/test_herramientas.py`.
   - `nucleo/macro.py:253:22:booleano` (`x.suffix in EXTENSIONES_DE_MACRO and x.is_file()` → `or`). Ningún test pasaba un directorio con archivos de extensiones no macro ni con subdirectorios que simularan extensiones de macro. Resuelto con `test_cargar_macros_ignora_archivos_sin_extension_declarada_y_subdirectorios` en `tests/test_macro.py`.
2. **Es equivalente (0)**: Ninguno. No fue necesario declarar equivalentes en `equivalentes.json`.
3. **El código sobra (0)**: Ninguno. Todo el código mutado es necesario y quedó cubierto.
4. **Es un BUG (0)**: Ninguno. La conducta original del código era la esperada por el diseño.

---

## Salida real de cada verificación de DOCTRINA.md

### 1. `python -m unittest discover -s tests -t . -q`
```
----------------------------------------------------------------------
Ran 535 tests in 16.491s

OK
```

### 2. `python tools/cifras.py`
```
CIFRAS OK
  cifras: 535 tests · 547/547 mutantes de medida · **2263 sitios de mutación de código** (2058 + 205 del motor Python).
  escala: **5606 líneas de lenguaje** (`nucleo/`, código y macros) y **255 negativas explícitas** (`raise`). Contra las 37 medidas universales escritas en él (225 líneas): **24,9 a 1**. 29 de las 37 pasan por una macro.
  corpus: **104 casos**: 70 defectos y 34 verdes correctos. De los defectos, 67 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 65 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5606 líneas de lenguaje y **255 negativas explícitas** (`raise`).
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

---

## Salidas de mutación de código de los objetivos

### `python tools/mutar_codigo.py --objetivo nucleo/version.py`
```
objetivos: nucleo/version.py

     ·  nucleo/version.py:45:8:retorno                       retorno: return <algo> → return None
     ·  nucleo/version.py:37:18:constante                    constante: True → False
     ·  nucleo/version.py:50:7:negacion                      negacion: se borra el `not`
     ·  nucleo/version.py:53:7:comparador                    comparador: Is → IsNot
     ·  nucleo/version.py:56:4:retorno                       retorno: return <algo> → return None
     ·  nucleo/version.py:56:31:constante                    constante: 1 → 2
     ·  nucleo/version.py:56:48:constante                    constante: 2 → 3
     ·  nucleo/version.py:61:4:retorno                       retorno: return <algo> → return None
     ·  nucleo/version.py:66:4:retorno                       retorno: return <algo> → return None
     ·  nucleo/version.py:72:7:comparador                    comparador: Is → IsNot
     ·  nucleo/version.py:76:7:negacion                      negacion: se borra el `not`
     ·  nucleo/version.py:89:4:retorno                       retorno: return <algo> → return None
     ·  nucleo/version.py:89:11:booleano                     booleano: and ↔ or
     ·  nucleo/version.py:89:11:comparador                   comparador: Eq → NotEq
     ·  nucleo/version.py:89:52:comparador                   comparador: LtE → Lt

mutantes: 15 · murieron 15 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

### `python tools/mutar_codigo.py --objetivo nucleo/macro.py`
```
objetivos: nucleo/macro.py

     ·  nucleo/macro.py:79:7:booleano                        booleano: and ↔ or
     ·  nucleo/macro.py:79:7:negacion                        negacion: se borra el `not`
     ·  nucleo/macro.py:79:37:negacion                       negacion: se borra el `not`
     ·  nucleo/macro.py:81:4:retorno                         retorno: return <algo> → return None
     ·  nucleo/macro.py:85:4:retorno                         retorno: return <algo> → return None
     ·  nucleo/macro.py:85:11:booleano                       booleano: and ↔ or
     ·  nucleo/macro.py:85:53:comparador                     comparador: Eq → NotEq
     ·  nucleo/macro.py:85:58:constante                      constante: 0 → 1
     ·  nucleo/macro.py:90:7:negacion                        negacion: se borra el `not`
     ·  nucleo/macro.py:93:11:comparador                     comparador: NotEq → Eq
     ·  nucleo/macro.py:93:24:constante                      constante: 2 → 3
     ·  nucleo/macro.py:95:36:constante                      constante: 1 → 2
     ·  nucleo/macro.py:105:7:negacion                       negacion: se borra el `not`
     ·  nucleo/macro.py:106:8:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:108:22:constante                     constante: 1 → 2
     ·  nucleo/macro.py:109:11:comparador                    comparador: NotIn → In
     ·  nucleo/macro.py:111:8:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:112:4:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:124:11:booleano                      booleano: and ↔ or
     ·  nucleo/macro.py:124:11:negacion                      negacion: se borra el `not`
     ·  nucleo/macro.py:124:42:comparador                    comparador: NotEq → Eq
     ·  nucleo/macro.py:124:56:constante                     constante: 5 → 6
     ·  nucleo/macro.py:124:61:comparador                    comparador: NotEq → Eq
     ·  nucleo/macro.py:124:67:constante                     constante: 0 → 1
     ·  nucleo/macro.py:130:11:comparador                    comparador: Is → IsNot
     ·  nucleo/macro.py:133:11:comparador                    comparador: In → NotIn
     ·  nucleo/macro.py:137:11:booleano                      booleano: and ↔ or
     ·  nucleo/macro.py:137:11:negacion                      negacion: se borra el `not`
     ·  nucleo/macro.py:137:47:negacion                      negacion: se borra el `not`
     ·  nucleo/macro.py:141:11:comparador                    comparador: NotEq → Eq
     ·  nucleo/macro.py:144:11:booleano                      booleano: and ↔ or
     ·  nucleo/macro.py:144:11:negacion                      negacion: se borra el `not`
     ·  nucleo/macro.py:144:46:negacion                      negacion: se borra el `not`
     ·  nucleo/macro.py:147:11:negacion                      negacion: se borra el `not`
     ·  nucleo/macro.py:152:15:booleano                      booleano: and ↔ or
     ·  nucleo/macro.py:152:15:negacion                      negacion: se borra el `not`
     ·  nucleo/macro.py:152:47:comparador                    comparador: NotEq → Eq
     ·  nucleo/macro.py:152:62:constante                     constante: 3 → 4
     ·  nucleo/macro.py:152:67:comparador                    comparador: NotEq → Eq
     ·  nucleo/macro.py:152:74:constante                     constante: 0 → 1
     ·  nucleo/macro.py:155:26:constante                     constante: 2 → 3
     ·  nucleo/macro.py:156:40:constante                     constante: 1 → 2
     ·  nucleo/macro.py:156:51:constante                     constante: 2 → 3
     ·  nucleo/macro.py:174:8:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:178:11:comparador                    comparador: NotEq → Eq
     ·  nucleo/macro.py:178:24:constante                     constante: 1 → 2
     ·  nucleo/macro.py:181:76:constante                     constante: 1 → 2
     ·  nucleo/macro.py:182:50:constante                     constante: 1 → 2
     ·  nucleo/macro.py:190:15:negacion                      negacion: se borra el `not`
     ·  nucleo/macro.py:195:45:constante                     constante: 1 → 2
     ·  nucleo/macro.py:197:8:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:115:18:constante                     constante: True → False
     ·  nucleo/macro.py:204:8:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:207:11:comparador                    comparador: In → NotIn
     ·  nucleo/macro.py:226:7:comparador                     comparador: Eq → NotEq
     ·  nucleo/macro.py:238:8:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:240:8:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:249:34:comparador                    comparador: Is → IsNot
     ·  nucleo/macro.py:250:7:booleano                       booleano: and ↔ or
     ·  nucleo/macro.py:250:7:comparador                     comparador: Eq → NotEq
     ·  nucleo/macro.py:250:27:constante                     constante: 1 → 2
     ·  nucleo/macro.py:250:56:constante                     constante: 0 → 1
     ·  nucleo/macro.py:251:34:constante                     constante: 0 → 1
     ·  nucleo/macro.py:253:22:booleano                      booleano: and ↔ or
     ·  nucleo/macro.py:253:22:comparador                    comparador: In → NotIn
     ·  nucleo/macro.py:259:4:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:264:4:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:272:7:negacion                       negacion: se borra el `not`
     ·  nucleo/macro.py:276:4:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:292:7:comparador                     comparador: Is → IsNot
     ·  nucleo/macro.py:294:4:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:298:7:comparador                     comparador: Is → IsNot
     ·  nucleo/macro.py:299:8:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:300:7:negacion                       negacion: se borra el `not`
     ·  nucleo/macro.py:302:4:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:306:4:retorno                        retorno: return <algo> → return None
     ·  nucleo/macro.py:306:12:booleano                      booleano: and ↔ or
     ·  nucleo/macro.py:307:33:constante                     constante: 0 → 1
     ·  nucleo/macro.py:307:46:comparador                    comparador: In → NotIn
     ·  nucleo/macro.py:307:52:constante                     constante: 0 → 1
     ·  nucleo/macro.py:320:12:booleano                      booleano: and ↔ or
     ·  nucleo/macro.py:323:11:negacion                      negacion: se borra el `not`
     ·  nucleo/macro.py:324:12:retorno                       retorno: return <algo> → return None
     ·  nucleo/macro.py:325:28:constante                     constante: 0 → 1
     ·  nucleo/macro.py:326:31:constante                     constante: 0 → 1

mutantes: 85 · murieron 85 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

---

## Qué NO hice y por qué

- No se declararon mutantes equivalentes en `equivalentes.json`: ambos sobrevivientes eran defectos de cobertura de tests reales (faltaban pruebas de inmutabilidad y de filtrado de archivos no-macro / subdirectorios).
- No se modificó el código de producción en `nucleo/version.py` ni `nucleo/macro.py`: la lógica existente era correcta y completa, y no contenía ramas muertas ni código redundante.
- No se modificó `corpus/` ni `vendor/`.
- No se modificaron mutadores ni timeouts en los arneses de mutación.

---

## Lo que descubrí que no me pediste

1. Al agregar tests, `tools/cifras.py` falla deliberadamente si el bloque de cifras en `README.md` no se sincroniza con la nueva cantidad de tests (pasó de 533 a 535 tests). Correr `python tools/cifras.py --actualizar` actualizó el README y restauró la verificación en verde.
2. Al ejecutar `mutar_codigo.py` con `--reanudar` luego de modificar archivos en `tests/`, el mecanismo de aislamiento y frescura detecta inmediatamente la invalidación del manifiesto (`ManifiestoInvalido: el manifiesto pertenece a otras fuentes, motor o configuración`), impidiendo falsos verdes por reutilización de manifiestos obsoletos.
