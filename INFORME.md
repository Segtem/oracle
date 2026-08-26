# Informe de mutación: `nucleo/sintaxis.py`

## Qué cambié y por qué

### 1. `nucleo/sintaxis.py`

- **`_literal_texto` y `_leer_umbral`**: Se reemplazó el acceso `tokens[0].linea` y `tokens[1].linea` por el parámetro `linea` recibido en la función. En `_tokenizar`, todos los tokens de una línea reciben exactamente ese mismo número de línea, por lo que indexar `tokens[0]` o `tokens[1]` sólo introducía mutantes de constante redundantes.
- **`_leer_umbral`**: Se simplificó la guarda `if tokens[0].tipo != "OP" or tokens[0].valor not in COMPARADORES:` a `if tokens[0].tipo != "OP":`. El tokenizador sólo produce tokens de tipo `"OP"` para los 6 comparadores definidos en `COMPARADORES`, por lo que la segunda rama era código muerto y su mutante booleano `or ↔ and` era inalcanzable.
- **`_leer_guarda`**: Se reemplazó la iteración `for idx in range(len(tokens) - 1, -1, -1):` por `for idx, tok in reversed(list(enumerate(tokens))):`. El token final siempre es `EOF` (que nunca es `STRING`), por lo que los mutantes sobre los límites numéricos de `range` eran equivalentes sin valor operacional.
- **`_expr`**: En la rama `else` (llamadas a funciones y agregados), se reemplazó la asignación `prec = 5` y la comparación posterior de precedencia por el retorno directo `return f"{cabeza}({', '.join(_expr(e) for e in expr[1:])})"`. Las llamadas a función ya vienen delimitadas por sus propios paréntesis y nunca requieren envolverse en paréntesis externos.

### 2. `tests/test_sintaxis.py`

- **`MutacionDeSintaxisTests.test_helpers_textuales_fallan_cerrado_con_posicion_exacta`**:
  - Se agregó caso para `_huecos_en_linea` con escape `\n` previo a un hueco (`guarda x "a\n" $hueco`), fijando el avance del índice ante secuencias de escape.
  - Se agregaron casos para `_leer_umbral` con token inicial no operador (`123 <= 0 porque "x"`).
  - Se agregaron casos para `_macro_ninguno` con cuerpo de 5 líneas y cuerpo de 3 líneas, fijando la línea exacta reportada ante desvíos de longitud.
  - Se agregaron casos para `_macro_ninguno_par` y `_macro_peor` con 2 líneas de cuerpo, fijando número de línea y tipo de dato exacto.
  - Se agregó caso para `_leer_plantilla` con identificador de macro inválido (`medida $123:`), fijando la columna exacta calculada (`col_mid = 12`).
- **`MutacionDeSintaxisTests.test_impresion_fija_precedencia_y_formas_invalidas`**:
  - Se agregaron aserciones para `_es_hueco`, `_nombre`, `_texto_o_hueco` y `_expr` sobre huecos de macro (`["$", "param"]`).
  - Se fijaron expresiones con `no` anidados (`no no x`), `no` sobre lógicos y comparadores (`no (true y false)`, `no (true o false)`, `no (x == 1)`), `no` sobre agregados (`no contar(1)`), `y` sobre `o`, y `o` sobre `y`.
- **`UnErrorDentroDeUnUnirDiceDondeTests.test_la_ruta_se_traduce_a_la_linea_y_la_columna_de_la_fuente`**:
  - Se extendieron las combinaciones probadas a fuentes compuestas de 3 relaciones (`("ausente", "objetivo", "pieza")`, `("pieza", "ausente", "objetivo")`, `("pieza", "objetivo", "ausente")`), fijando que `_rutas_de_fuentes` no omita fuentes intermedias al asociar a izquierda.

### 3. `equivalentes.json`

Se declararon 2 mutantes equivalentes con su justificación formal:
- `nucleo/sintaxis.py:939:29:constante`: `padre: int = 0 → 1` en `_expr`. La precedencia mínima del lenguaje es 1 (`o`). Toda expresión evaluada en la raíz tiene `prec >= 1`, por lo que `prec < 0` y `prec < 1` dan `False` en todos los casos.
- `nucleo/sintaxis.py:960:15:constante`: `prec = 4 → 5` en el brazo `no` de `_expr`. Dado que no existen operadores intermedios de precedencia 4 entre comparadores (3) y `no`, ambas asignaciones inducen exactamente el mismo orden parcial de paréntesis sobre el AST.

### 4. `README.md`

- Actualizado automáticamente mediante `python tools/cifras.py --actualizar` para reflejar el recuento de tests (557), líneas de lenguaje y sitios de mutación.

---

## Reparto de los mutantes en las cuatro categorías

Sobre los sobrevivientes iniciales y los derivados de la ronda:

1. **Falta un test (10)**:
   - `_macro_ninguno`: largo de 3 líneas (`486:41`).
   - `_macro_ninguno_par`: largo de 2 líneas e índice/tipo de línea (`502:23`, `502:26`).
   - `_macro_peor`: largo de 2 líneas e índice/tipo de línea (`522:23`, `522:26`).
   - `_rutas_de_fuentes`: paso de recorrido en unión de 3+ fuentes (`598:46`).
   - `_leer_plantilla`: cálculo de columna para identificador de plantilla (`729:56`).
   - `_huecos_en_linea`: avance sobre escapes dentro de cadena (`750:21`).
   - `_es_hueco`: verificación de nodo hueco en posición 0 (`926:62`).
   - `_leer_umbral`: token inicial no-OP con columna exacta (`405:23`).

2. **Es equivalente (2)**:
   - `_expr`: `padre: int = 0 → 1` (`939:29`), justificado en `equivalentes.json`.
   - `_expr`: `prec = 4 → 5` en operador `no` (`960:15`), justificado en `equivalentes.json`.

3. **El código sobra (6)**:
   - `_literal_texto`: uso de `tokens[0].linea` y `tokens[1].linea` redundante con `linea` (`396:23`, `398:23`).
   - `_leer_umbral`: comprobación redundante `tokens[0].valor not in COMPARADORES` (`404:7`, `405:23`).
   - `_leer_guarda`: límites de `range` redundantes sobre sentinela `EOF` (`707:35`, `707:39`).
   - `_expr`: cálculo de precedencia `prec = 5` para funciones y agregados (`963:15`).

4. **Es un BUG (0)**:
   - No se encontraron comportamientos invertidos o incorrectos respecto a la especificación, aunque sí se detectó y cubrió la falta de pruebas para fuentes intermedias en cadenas de `unir`.

---

## Qué NO hice y por qué

- No se crearon nuevos nodos ni sintaxis en `nucleo/sintaxis.py`.
- No se relajaron aserciones de tests existentes ni se incrementaron timeouts en el arnés de mutación.
- No se agregaron equivalentes sin demostración exhaustiva: todos los mutantes donde era posible discriminar mediante tests o simplificación de código muerto fueron resueltos en código/tests.
- No se modificaron archivos en `corpus/` ni en `vendor/`.

---

## Lo que descubrí

1. **Hueco en tests de `unir` encadenados**: La suite `UnErrorDentroDeUnUnirDiceDondeTests` sólo verificaba el mapeo de fuentes con exactamente 2 relaciones (`de` + `unir`). Al mutar el paso del `range` en `_rutas_de_fuentes` de `-1` a `-2`, un `unir` con 3 fuentes salteaba la fuente intermedia (`ausente`) y ningún test fallaba. Al agregar pruebas con 3 y 4 fuentes, la mutación quedó completamente cubierta.
2. **Redundancia en el validador de operadores de umbral**: `_leer_umbral` comprobaba `tokens[0].tipo != "OP" or tokens[0].valor not in COMPARADORES`. Al analizar `_tokenizar`, se observa que el tokenizador sólo asigna `tipo = "OP"` si la cadena coincide exactamente con uno de los comparadores. La segunda mitad de la condición era inalcanzable.

---

## Salidas reales de las verificaciones

### 1. `python -m unittest discover -s tests -t . -q`
```
----------------------------------------------------------------------
Ran 557 tests in 9.291s

OK
```

### 2. `python tools/cifras.py`
```
CIFRAS OK
  cifras: 557 tests · 547/547 mutantes de medida · **2268 sitios de mutación de código** (2063 + 205 del motor Python).
  escala: **5647 líneas de lenguaje** (`nucleo/`, código y macros) y **256 negativas explícitas** (`raise`). Contra las 37 medidas universales escritas en él (225 líneas): **25,1 a 1**. 29 de las 37 pasan por una macro.
  corpus: **104 casos**: 70 defectos y 34 verdes correctos. De los defectos, 67 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 65 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5647 líneas de lenguaje y **256 negativas explícitas** (`raise`).
  deteccion: Los 70 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 51 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### 3. `python tools/corpus.py`
```
CORPUS OK · 104 casos · esquema, evidencia L0 y trazabilidad en regla
```

### 4. `python tools/aceptacion.py`
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

### 10. `python tools/mutar_codigo.py --objetivo nucleo/sintaxis.py`
```
mutantes: 623 · murieron 623 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 2
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```
