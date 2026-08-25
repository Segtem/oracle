# Informe: Ronda de mutación en `nucleo/algebra.py`

## Hallazgos y supuestos falsos de la tarea

1. **Supuesto falso sobre `unir`**: En `TAREA.md` se planteó que los 4 mutantes de rutas en `_unir` (líneas 672 y 673: `(*ruta, 1)` / `(*ruta, 2)`) hacían que un error señalara el operando derecho en vez del izquierdo. Esto es falso en la arquitectura actual: los operandos de `unir` están confinados a `FUENTES = ("de", "unir")`. La función `_de` no recibe `ruta` y cualquier fallo al cargar hechos o validar unicidad eleva un `ErrorDeAlgebra` con `self._ruta = None`. `_unir` tampoco evalúa expresiones ni captura excepciones para prefijar rutas. En consecuencia, las variables `ruta_izq` y `ruta_der` son inertes y ningún test de caja negra ni blanca puede observar su mutación. Se clasificaron como **mutantes equivalentes** y se registraron formalmente en `equivalentes.json` con su fundamentación técnica.
2. **Corrección de las rutas en `agrupar` y `resumir`**: A diferencia de `unir`, las rutas calculadas en `_agrupar` (`(*ruta, 1, posicion, 1)` para claves y `(*ruta, 2, posicion, 2)` para agregados) y en `resumir` (`(*ruta, 2)` con base predeterminada `(3,)`) sí se propagan a `evaluar_expr`. Los 9 mutantes que afectaban a estos operadores sobrevivían únicamente por falta de tests que fijaran la tupla exacta `ruta_indices` y distinguieran la posición 0 de la 1.

---

## Clasificación de los 21 mutantes sobrevivientes

- **Categoría 1 (Falta un test): 17 mutantes**
  - `nucleo/algebra.py:38:8:retorno` — `ErrorDeAlgebra.ruta_indices` devolvía `None`.
  - `nucleo/algebra.py:48:12:retorno` — `prefijar_ruta(None)` devolvía `None` en lugar de `self`.
  - `nucleo/algebra.py:50:8:retorno` — `prefijar_ruta(tupla)` devolvía `None` en lugar de `self`.
  - `nucleo/algebra.py:54:8:retorno` — `descartar_ruta()` devolvía `None` en lugar de `self`.
  - `nucleo/algebra.py:68:11:comparador` — `_normalizar_ruta` con `if ruta == ""` (`Eq → NotEq`).
  - `nucleo/algebra.py:69:12:retorno` — `_normalizar_ruta` retornando `()` (`return <algo> → return None`).
  - `nucleo/algebra.py:81:11:comparador` — `_normalizar_ruta` con `if indice < 0` (`Lt → LtE`, rechazaba el índice 0).
  - `nucleo/algebra.py:81:20:constante` — `_normalizar_ruta` con `if indice < 0` (`0 → 1`, rechazaba el índice 0).
  - `nucleo/algebra.py:708:27:constante` — `_agrupar` cálculo de ruta de claves `(*ruta, 1, posicion, 1)` primer `1 → 2`.
  - `nucleo/algebra.py:708:40:constante` — `_agrupar` cálculo de ruta de claves `(*ruta, 1, posicion, 1)` segundo `1 → 2`.
  - `nucleo/algebra.py:709:8:comparador` — `_agrupar` guarda `if (ruta is not None)` (`IsNot → Is`).
  - `nucleo/algebra.py:710:30:constante` — `_agrupar` cálculo de ruta de agregados `(*ruta, 2, posicion, 2)` primer `2 → 3`.
  - `nucleo/algebra.py:710:43:constante` — `_agrupar` cálculo de ruta de agregados `(*ruta, 2, posicion, 2)` segundo `2 → 3`.
  - `nucleo/algebra.py:711:8:comparador` — `_agrupar` guarda `if (ruta is not None)` (`IsNot → Is`).
  - `nucleo/algebra.py:862:44:constante` — `resumir` ruta predeterminada `ruta: tuple = (3,)` (`3 → 4`).
  - `nucleo/algebra.py:870:24:constante` — `resumir` cálculo `ruta_expr = (*ruta, 2)` (`2 → 3`).
  - `nucleo/algebra.py:870:30:comparador` — `resumir` guarda `if ruta is not None else None` (`IsNot → Is`).

- **Categoría 2 (Es equivalente): 4 mutantes**
  - `nucleo/algebra.py:672:29:comparador` — `_unir` cálculo `ruta_izq`: `IsNot → Is`.
  - `nucleo/algebra.py:672:23:constante` — `_unir` cálculo `ruta_izq`: `1 → 2`.
  - `nucleo/algebra.py:673:29:comparador` — `_unir` cálculo `ruta_der`: `IsNot → Is`.
  - `nucleo/algebra.py:673:23:constante` — `_unir` cálculo `ruta_der`: `2 → 3`.

- **Categoría 3 (El código sobra): 0 mutantes.**
- **Categoría 4 (Es un bug): 0 mutantes.**

---

## Cambios por archivo

1. `tests/test_algebra.py`:
   - Se añadió la clase `RutasDeErrorDelAlgebraTests` con 4 tests exhaustivos:
     - `test_propiedades_y_manipulacion_de_ruta_en_error_de_algebra`: prueba `ruta_indices`, `ruta`, encadenamiento y retorno de `prefijar_ruta`, `descartar_ruta` y `con_ruta_actual`.
     - `test_normalizacion_de_rutas_cadena_vacia_cero_y_errores`: prueba rutas con cadena vacía `""`, índice `0`, tuplas con `0`, cadenas con `0`, y rechazo fail-closed de índices negativos o tipos inválidos.
     - `test_agrupar_propaga_la_ruta_exacta_de_claves_y_agregados`: prueba errores en claves (posición 0 y posición 1), errores en agregados (posición 0 y posición 1), verificando `ruta_indices` y `ruta` exactos, así como llamadas directas con `ruta=None`.
     - `test_resumir_propaga_la_ruta_predeterminada_y_personalizada`: prueba que `resumir` asocie `(3, 2)` por omisión, `(7, 2)` con ruta explícita y `None` cuando `ruta=None`.
2. `equivalentes.json`:
   - Se añadieron las declaraciones de equivalencia con justificación técnica para los 4 mutantes de `_unir`.
3. `README.md`:
   - Actualizado mediante `python tools/cifras.py --actualizar` para sincronizar los totales tras la adición de tests.

---

## Qué NO hice y por qué

- No modifiqué la firma ni la lógica de `_de` o `aplicar` para forzar la propagación de rutas a las fuentes de `unir`: ninguna medida real del catálogo lo requiere y la Regla 4 de `DOCTRINA.md` prohíbe explícitamente agregar capacidades al lenguaje sin necesidad concreta.
- No toqué `vendor/`, `catalogos/` ni `corpus/`.
- No aflojé ninguna aserción ni modifiqué configuraciones del arnés.

---

## Salidas reales de las verificaciones

### 1. `python tools/mutar_codigo.py --objetivo nucleo/algebra.py`

```
mutantes: 318 · murieron 318 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 4
  ✓ proceso.codigo_con_mutante_que_lo_mata       valor 0 (<= 0)
  ✓ proceso.ronda_mutacion_concluyente           valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio              valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: [==, [campo, m, detecciones_conductuales], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

### 2. `python -m unittest discover -s tests -t . -q`

```
----------------------------------------------------------------------
Ran 539 tests in 9.925s

OK
```

### 3. `python tools/cifras.py`

```
CIFRAS OK
  cifras: 539 tests · 547/547 mutantes de medida · **2263 sitios de mutación de código** (2058 + 205 del motor Python).
  escala: **5606 líneas de lenguaje** (`nucleo/`, código y macros) y **255 negativas explícitas** (`raise`). Contra las 37 medidas universales escritas en él (225 líneas): **24,9 a 1**. 29 de las 37 pasan por una macro.
  corpus: **104 casos**: 70 defectos y 34 verdes correctos. De los defectos, 67 deben ponerse en rojo · 0 huecos abiertos · 2 resueltos conservados · 1 límite humano. Por etiqueta: 65 falsos verdes, 2 falsos rojos, 1 conclusión causal incorrecta pese a una medida correcta y 2 deudas de diseño.
  negativas: En este corte hay 5606 líneas de lenguaje y **255 negativas explícitas** (`raise`).
  deteccion: Los 70 casos no observacionales salieron a la luz por vías que no aceptan el verde nominal: 51 la mutación, 12 una persona, 4 la casualidad, 3 una herramienta ajena.
```

### 4. `python tools/corpus.py`

```
CORPUS OK · 104 casos · esquema, evidencia L0 y trazabilidad en regla
```

### 5. `python tools/aceptacion.py`

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

### 6. `python tools/diferencial.py`

```
simulacion.json · 4 mundos · origen: implementación independiente (Codex gpt-5.5) escrita sólo desde ESPECIFICACION.md

  ✓ acuerdo global: 4 escenarios (1 verdes / 3 rojos) · 0 desacuerdos
  ✓ estabilidad individual: 3 medidas × 4 escenarios · 0 cambios


DIFERENCIAL ✓ — 4 acuerdos globales con referencias independientes · 12 veredictos individuales estables
```

### 7. `python tools/trazar.py`

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

### 8. `python tools/metamorficas.py`

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

### 9. `python tools/sintaxis.py --verificar`

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

### 10. `python tools/mutar.py`

```
mutantes de medida (medida × mutador): 547 · murieron 547 · sobrevivieron 0
  de los muertos: 422 por conducta (invirtió el veredicto, cambió testigos o cambió el valor) · 125 rechazados por el álgebra sin evaluar
detecciones evaluadas (mutante × caso): 1924

juzgado por las medidas del catálogo:
  ✓ meta.toda_medida_esta_ejercitada                    0 (<= 0)
  ✓ meta.toda_medida_esta_fijada                        0 (<= 0)
  ✓ proceso.test_con_mutante_que_lo_mata                0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.codigo_con_mutante_que_lo_mata: «==» sobre un valor ausente: [==, [campo, m, estado], pasaron] en `2.2.1.1`
```
