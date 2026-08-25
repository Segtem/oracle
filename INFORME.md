# Informe de implementación: Medida para juzgar sobrevivientes de mutación de código

## 1. Resumen

Se implementó en el catálogo de proceso la medida `proceso.codigo_con_mutante_que_lo_mata` en sintaxis canónica de superficie `.oracle` para juzgar los sobrevivientes resultantes de la ronda de mutación de código (`tools/mutar_codigo.py`).

Hasta este cambio, `tools/mutar_codigo.py` evaluaba las medidas aplicables pero sólo existían medidas que auditaban la concluyencia operativa de la ronda (`proceso.ronda_mutacion_concluyente`, `proceso.arnes_con_bytecode_frio`) y una medida de mutación de medidas (`proceso.test_con_mutante_que_lo_mata`, que fallaba con `ErrorDeAlgebra` por campos ausentes). Por ende, una ronda con 57 mutantes de código vivos cerraba reportando únicamente tildes verdes. Con la nueva medida, la presencia de mutantes de código sobrevivientes no declarados como equivalentes se dictamina en rojo como ofensa contra el umbral `<= 0`.

Se agregaron 5 casos de prueba al corpus en formato `.caso` cubriendo ambas polaridades (rojos y verdes correctos), aislando mutantes equivalentes declarados y verificando la precondición `requiere mutante`. Todas las 9 herramientas de verificación del repositorio quedaron en verde, y la mutación de medidas (`tools/mutar.py`) cerró con **0 sobrevivientes sobre 547 mutantes**.

---

## 2. Detalle de cambios archivo por archivo

### `catalogos/proceso/proceso.codigo_con_mutante_que_lo_mata.oracle`
Nueva medida de catálogo en sintaxis canónica:
```oracle
medida proceso.codigo_con_mutante_que_lo_mata:
    de mutante m
    donde m.estado == "pasaron" y m.equivalente_declarado == false
    resumen contar(1)
    umbral <= 0 porque "un mutante de código que sobrevive es una modificación sintáctica del núcleo que ningún test detecta: la suite completa pasa con el código alterado, lo que demuestra que los tests tienen un punto ciego y no están fijando ese comportamiento. El umbral tiene que ser cero porque tolerar sobrevivientes no declarados equivale a publicar como verificada una base de código cuyo comportamiento real no está garantizado. Un mutante equivalente declarado con su razón escrita no cuenta como sobreviviente porque documenta una decisión explícita, no una omisión de los tests"
    requiere mutante
    alcance "cuenta mutantes de código de la ronda cuyo estado fue «pasaron» sin estar declarados como equivalentes. NO ve los mutadores que nadie escribió ni los operadores que el perfil de mutación no contempla: un mutante que no existe no puede sobrevivir. Tampoco juzga por sí sola si la ronda fue concluyente —eso lo mide proceso.ronda_mutacion_concluyente— ni si el bytecode estaba frío. Si mutante viene vacía la medida NO concluye —lo declara en requiere, y sale SIN EVIDENCIA en vez de verde—"
```
- **Filtro**: `m.estado == "pasaron" y m.equivalente_declarado == false`. Detecta mutantes donde la suite de tests no falló y que no tienen justificación explícita de equivalencia.
- **Resumen y Umbral**: `contar(1)` con umbral `<= 0` defendido en prosa.
- **Precondición `requiere mutante`**: Evita que una ronda sin mutantes concluya falsamente verde sobre el vacío (falla cerrada / sin evidencia).
- **Alcance**: Define con precisión los límites de lo observado y lo que queda fuera.

### `corpus/proceso/025-mutante-de-codigo-sobreviviente.caso`
Caso de defecto (`falso_verde` / rojo) con 1 mutante sobreviviente real (`estado: "pasaron"`, `equivalente_declarado: false`) y 1 mutante muerto (`estado: "tests_fallaron"`). Fija la detección de mutantes no cazados por la suite.

### `corpus/proceso/026-mutante-de-codigo-equivalente-no-cuenta-como-muerte-ni-sobreviviente.caso`
Caso de defecto (`falso_verde` / rojo) con 1 sobreviviente real, 1 mutante muerto y 1 mutante declarado equivalente (`equivalente_declarado: true`). Fija que el mutante equivalente no se cuenta como sobreviviente, pero tampoco enmascara al sobreviviente real (valor = 1).

### `corpus/proceso/027-ronda-de-codigo-sin-mutantes-no-concluye.caso`
Caso de defecto (`falso_verde` / rojo) con relación `mutante:` vacía. Fija el nodo `requiere mutante` (matando el mutador `quitar_requiere` al producir `sin_evidencia="mutante"`).

### `corpus/proceso/109-mutantes-de-codigo-todos-muertos.caso`
Caso verde (`verde_correcto`) con 2 mutantes muertos (`estado: "tests_fallaron"`, `murio: true`). Fija que cuando todos los mutantes mueren, la medida evalúa a 0 (verde).

### `corpus/proceso/110-mutante-de-codigo-equivalente-declarado-verde.caso`
Caso verde (`verde_correcto`) con 1 mutante muerto y 1 mutante declarado equivalente con su razón. Fija que la presencia de un equivalente declarado legítimo no tiñe de rojo una ronda sana.

### `tools/mutar.py`
Se incorporó el manejo de `ErrorDeAlgebra` al evaluar las medidas aplicables del catálogo al cierre de la ronda de mutación de medidas, exactamente de la misma manera en que ya lo hacía `tools/mutar_codigo.py`. Como `medidas_aplicables` filtra por nombre de relación (`mutante`) y no por campos presentes, una medida escrita para juzgar código (`proceso.codigo_con_mutante_que_lo_mata`) que corre contra evidencia de mutación de medidas (que no provee `estado`) levanta `ErrorDeAlgebra`. El arnés ahora ataja `ErrorDeAlgebra`, acumula la medida en `no_juzgaron` informando el motivo y evalúa las políticas restantes sin abortar la ronda.

### `README.md`
Actualizado automáticamente mediante `python tools/cifras.py --actualizar` reflejando:
- 37 medidas universales (225 líneas)
- 104 casos de corpus (70 defectos, 34 verdes)
- 547 mutantes de medida fijados con 0 sobrevivientes.

---

## 3. Demostración de la medida en acción

### Demostración 1: Evaluación directa ante un mutante sobreviviente (ROJO)
Al evaluar `proceso.codigo_con_mutante_que_lo_mata` contra una evidencia con un mutante vivo:

```
$ python -c '
from nucleo.medida import cargar
from pathlib import Path
m = cargar(Path("catalogos/proceso/proceso.codigo_con_mutante_que_lo_mata.oracle"))
evidencia_roja = {
    "mutante": [
        {"id": "s1", "apunta_a": "a.py", "cambio": "c1", "estado": "pasaron", "equivalente_declarado": False},
        {"id": "s2", "apunta_a": "a.py", "cambio": "c2", "estado": "tests_fallaron", "equivalente_declarado": False},
    ]
}
v = m.evaluar(evidencia_roja)
print(f"  {v.linea()}")
'
  ✗ proceso.codigo_con_mutante_que_lo_mata              1 (<= 0)
      → m=s1
```

### Demostración 2: Ronda de código con 0 sobrevivientes (`nucleo/version.py`) (VERDE)
```
$ python tools/mutar_codigo.py --objetivo nucleo/version.py
objetivos: nucleo/version.py

     ·  nucleo/version.py:16:13:constante                    constante: 1 → 2
     ·  nucleo/version.py:17:13:constante                    constante: 2 → 3
     ·  nucleo/version.py:18:13:constante                    constante: 3 → 4
     ·  nucleo/version.py:35:16:comparador                   comparador: Is → IsNot
     ·  nucleo/version.py:39:19:comparador                   comparador: NotIn → In
     ·  nucleo/version.py:46:11:booleano                     booleano: and ↔ or
     ·  nucleo/version.py:46:11:negacion                     negacion: se borra el `not`
     ·  nucleo/version.py:46:33:negacion                     negacion: se borra el `not`
     ·  nucleo/version.py:47:8:retorno                       retorno: return <algo> → return None
     ·  nucleo/version.py:49:11:comparador                   comparador: NotEq → Eq
     ·  nucleo/version.py:53:11:comparador                   comparador: Lt → LtE
     ·  nucleo/version.py:55:11:booleano                     booleano: and ↔ or
     ·  nucleo/version.py:55:11:comparador                   comparador: Eq → NotEq
     ·  nucleo/version.py:55:35:comparador                   comparador: Lt → LtE

mutantes: 14 · murieron 14 · sobrevivieron 0 · timeout 0 · errores de arnés 0 · equivalentes declarados: 0
  ✓ proceso.ronda_mutacion_concluyente         valor 0 (<= 0)
  ✓ proceso.codigo_con_mutante_que_lo_mata     valor 0 (<= 0)
  ✓ proceso.arnes_con_bytecode_frio            valor 0 (<= 0)

  1 medida(s) NO pudieron juzgar esta evidencia — la relación estaba, los campos no:
    · proceso.test_con_mutante_que_lo_mata: «==» sobre un valor ausente: ['==', ['campo', 'm', 'detecciones_conductuales'], 0] en `2.2.1.1`

Todos los mutantes murieron: los tests fijan el código del núcleo.
```

---

## 4. Salidas reales de la suite de 9 verificaciones

### 1. `python -m unittest discover -s tests -t . -q`
```
----------------------------------------------------------------------
Ran 528 tests in 9.345s

OK
```

### 2. `python tools/cifras.py`
```
CIFRAS OK
  cifras: 528 tests · 547/547 mutantes de medida · **2263 sitios de mutación de código** (2058 + 205 del motor Python).
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

## 5. Lo que no se hizo y por qué

1. **No se modificó `nucleo/caso.py` ni sus tests**: Conforme a la consigna, otra rama está matando sus 57 mutantes vivos.
2. **No se declararon mutantes equivalentes artificiales**: Los casos del corpus utilizan fixtures sintéticas representativas para aislar las propiedades de la medida sin alterar `equivalentes.json`.
3. **No se alteró `tools/mutar_codigo.py`**: La evidencia emitida por dicha herramienta (`mutante` con `estado` y `equivalente_declarado`) contenía todos los campos necesarios para escribir la medida de forma limpia.
