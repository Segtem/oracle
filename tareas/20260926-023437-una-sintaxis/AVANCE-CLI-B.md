# Avance Mutación tools/cli.py — Lista B

Se procesaron los 33 mutantes de la **LISTA B** (`tareas/20260926-023437-una-sintaxis/SOBREVIVIENTES-CLI-B.txt`), correspondientes a las líneas de `formatear`, `test` y el despacho de argumentos en `main` de `tools/cli.py`.

## Resumen

- **Total de mutantes analizados:** 33
- **Matados con nuevos tests:** 29 (en `tests/test_cli_formatear_mutacion.py`)
- **Declarados equivalentes:** 4 (en `equivalentes.json` con su justificación técnica)
- **Estado de la suite completa (`unittest discover`):** 2676 tests OK (VERDE)
- **Estado de `tools/cli.py`:** Sin modificaciones respecto al código base original.

---

## Mutantes Declarados Equivalentes (4)

Se incorporaron a `equivalentes.json` las siguientes 4 declaraciones:

1. **`tools/cli.py:903:50:booleano`**
   - **Línea:** `for linea in original.splitlines() if linea.strip() and not linea.lstrip().startswith("#"))`
   - **Cambio:** `and ↔ or` dentro de la comprensión que alimenta a `any(linea.lstrip().startswith("defmacro ") ...)`.
   - **Ordinal:** 1
   - **Razón:** En `tools/cli.py`, `linea.strip() and not linea.lstrip().startswith("#")` → `linea.strip() or not linea.lstrip().startswith("#")` dentro de `any(linea.lstrip().startswith("defmacro ") for linea in original.splitlines() if ...)`. Para cualquier línea donde el predicado original daba `False`: o bien la línea es vacía (en cuyo caso `"".startswith("defmacro ")` es `False`), o bien comienza con `#` (en cuyo caso tras desindentar empieza con `#` y no puede empezar con `defmacro `, dando `False`). La inclusión de resultados `False` adicionales en `any(...)` no altera su valor de verdad para ninguna entrada posible. La condición produce idéntico valor booleano en todo texto.

2. **`tools/cli.py:1156:60:constante`**
   - **Línea:** `f"{informe_sintaxis.get('relaciones', 0)} relaciones")`
   - **Cambio:** `0 → 1` en el valor por defecto de `.get('relaciones', 0)`.
   - **Ordinal:** 1
   - **Razón:** En `tools/cli.py`, `f"{informe_sintaxis.get('relaciones', 0)} relaciones"` → `get('relaciones', 1)`. La variable `informe_sintaxis` es el diccionario devuelto por `tools/sintaxis.verificar_catalogo(proy.raiz)`, que en su línea 200 define explícitamente `"relaciones": len(filas_relaciones)`. Al estar la clave `'relaciones'` invariablemente presente en el diccionario (con valor entero >= 0), `dict.get('relaciones', ...)` devuelve siempre el valor asociado a la clave y jamás evalúa el valor por defecto. Cambiar el valor por defecto de 0 a 1 es inobservable en cualquier ejecución.

3. **`tools/cli.py:1160:56:constante`**
   - **Línea:** `f"{informe_sintaxis.get('relaciones', 0)} relaciones")`
   - **Cambio:** `0 → 1` en la rama `else` de `proy.es_el_propio_oracle`.
   - **Ordinal:** 2
   - **Razón:** En `tools/cli.py`, `f"{informe_sintaxis.get('relaciones', 0)} relaciones"` → `get('relaciones', 1)` en la rama `else` de `proy.es_el_propio_oracle`. Idéntico caso al documentado en `tools/cli.py:1156:60:constante`: `informe_sintaxis` procede de `tools/sintaxis.verificar_catalogo`, que siempre incluye la clave `'relaciones'`, por lo que el valor por defecto nunca es utilizado.

4. **`tools/cli.py:1591:128:constante`**
   - **Línea:** `if len(args) not in (1, 2) or any(a.startswith("--") and a != "--escribir" for a in args) or args.count("--escribir") > 1:`
   - **Cambio:** `args.count("--escribir") > 1` → `args.count("--escribir") > 2`.
   - **Ordinal:** 1
   - **Razón:** En `tools/cli.py`, `args.count("--escribir") > 1` → `args.count("--escribir") > 2` en el subcomando `formatear` de `main`. La única combinación donde ambos umbrales difieren es `args == ["--escribir", "--escribir"]` (`len == 2`, `count == 2`): con `> 1` la guarda de la línea 1591 evalúa a `True`, imprime `uso: oracle formatear <ruta> [--escribir]` y devuelve 1; con `> 2` supera esa guarda pero en la línea 1594 `rutas = [a for a in args if a != "--escribir"]` evalúa a lista vacía `[]`, activando la guarda inmediata `if len(rutas) != 1:` que imprime exactamente el mismo mensaje de uso y devuelve 1. Para todo otro argumento, si `len not in (1, 2)` la primera condición cortocircuita en ambos, y si `len == 1` el conteo nunca supera 1. La salida, diagnóstico y código de retorno son idénticos para cualquier lista de argumentos.

---

## Mutantes Matados por Tests (29)

Se implementaron en el nuevo archivo `tests/test_cli_formatear_mutacion.py`:

| # | Id del mutante | Operador / Cambio | Test que lo mata |
|---|---|---|---|
| 1 | `tools/cli.py:901:19:booleano` | `and ↔ or` | `test_mutante_901_19_booleano_medida_con_macro_resuelve_macro` |
| 2 | `tools/cli.py:901:19:comparador` | `Eq → NotEq` | `test_mutante_901_19_comparador_formatear_macro_no_invoca_macros_del_proyecto` |
| 3 | `tools/cli.py:903:68:negacion` | se borra `not` | `test_mutante_903_68_negacion_formatear_macro_no_invoca_macros_del_proyecto` |
| 4 | `tools/cli.py:904:46:booleano` | `and ↔ or` | `test_mutante_904_46_booleano_formatear_caso_no_invoca_macros_del_proyecto` |
| 5 | `tools/cli.py:904:46:comparador` | `Eq → NotEq` | `test_mutante_904_46_comparador_medida_con_macro_recibe_macros` |
| 6 | `tools/cli.py:904:75:negacion` | se borra `not` | `test_mutante_904_75_negacion_medida_con_macro_recibe_macros` |
| 7 | `tools/cli.py:908:12:retorno` | `return 0 → return None` | `test_mutante_908_12_retorno_formatear_forma_unica_devuelve_cero` |
| 8 | `tools/cli.py:908:19:constante` | `0 → 1` | `test_mutante_908_19_constante_formatear_forma_unica_devuelve_cero` |
| 9 | `tools/cli.py:923:8:retorno` | `return 1 → return None` | `test_mutante_923_8_retorno_formatear_error_devuelve_uno` |
| 10 | `tools/cli.py:923:15:constante` | `1 → 2` | `test_mutante_923_15_constante_formatear_error_devuelve_uno` |
| 11 | `tools/cli.py:995:15:constante` | `1 → 2` | `test_mutante_995_15_constante_cmd_test_desformateado_devuelve_uno` |
| 12 | `tools/cli.py:1590:36:comparador` | `NotEq → Eq` | `test_mutante_1590_36_comparador_main_formatear_acepta_argumentos_distintos_de_rapido` |
| 13 | `tools/cli.py:1591:11:booleano` | `and ↔ or` | `test_mutante_1591_11_booleano_main_formatear_rechaza_repetir_escribir_con_ruta` |
| 14 | `tools/cli.py:1591:11:comparador` | `NotIn → In` | `test_mutante_1591_11_comparador_main_formatear_uno_o_dos_argumentos_no_falla_uso` |
| 15 | `tools/cli.py:1591:29:constante` | `1 → 2` | `test_mutante_1591_29_constante_main_formatear_un_argumento_valido` |
| 16 | `tools/cli.py:1591:32:constante` | `2 → 3` | `test_mutante_1591_32_constante_main_formatear_dos_argumentos_con_escribir` |
| 17 | `tools/cli.py:1591:42:booleano` | `and ↔ or` | `test_mutante_1591_42_booleano_main_formatear_argumento_posicional_no_es_rechazado_por_flag` |
| 18 | `tools/cli.py:1591:65:comparador` | `NotEq → Eq` | `test_mutante_1591_65_comparador_main_formatear_acepta_flag_escribir` |
| 19 | `tools/cli.py:1591:101:comparador` | `Gt → GtE` | `test_mutante_1591_101_comparador_main_formatear_permite_un_escribir` |
| 20 | `tools/cli.py:1593:12:retorno` | `return 1 → return None` | `test_mutante_1593_12_retorno_main_formatear_sin_argumentos_retorna_uno` |
| 21 | `tools/cli.py:1593:19:constante` | `1 → 2` | `test_mutante_1593_19_constante_main_formatear_sin_argumentos_retorna_uno` |
| 22 | `tools/cli.py:1594:36:comparador` | `NotEq → Eq` | `test_mutante_1594_36_comparador_main_formatear_extrae_ruta_no_escribir` |
| 23 | `tools/cli.py:1595:11:comparador` | `NotEq → Eq` | `test_mutante_1595_11_comparador_main_formatear_con_una_ruta_continua` |
| 24 | `tools/cli.py:1595:25:constante` | `1 → 2` | `test_mutante_1595_25_constante_main_formatear_con_una_ruta_continua` |
| 25 | `tools/cli.py:1597:12:retorno` | `return 1 → return None` | `test_mutante_1597_12_retorno_main_formatear_solo_escribir_retorna_uno` |
| 26 | `tools/cli.py:1597:19:constante` | `1 → 2` | `test_mutante_1597_19_constante_main_formatear_solo_escribir_retorna_uno` |
| 27 | `tools/cli.py:1598:8:retorno` | `return <algo> → None` | `test_mutante_1598_8_retorno_main_formatear_retorna_codigo_de_cmd_formatear` |
| 28 | `tools/cli.py:1598:41:constante` | `0 → 1` | `test_mutante_1598_41_constante_main_formatear_usa_indice_cero_de_rutas` |
| 29 | `tools/cli.py:1598:54:comparador` | `In → NotIn` | `test_mutante_1598_54_comparador_main_formatear_sin_escribir_no_modifica_archivo` |

---

## Verificación de Mutantes

Cada uno de los 29 mutantes fue verificado aplicando a mano la mutación sobre `tools/cli.py`, borrando `__pycache__`, ejecutando el test con `python3 -B -m unittest`, comprobando que falla bajo la mutación, restaurando `tools/cli.py` desde el respaldo limpio, borrando `__pycache__` y comprobando que pasa en limpio.

Resultado de la verificación automatizada:
`¡ÉXITO TOTAL! Los 29 mutantes fueron verificados rigurosamente: Cada test falló con su mutante y pasó sin él.`

---

## Comandos Corridos

```bash
# Instalación de setuptools para tests de empaquetado/rueda en el contenedor
python3 -m pip install "setuptools>=68"

# Verificación de los tests nuevos contra código base limpio
python3 -B -m unittest tests.test_cli_formatear_mutacion

# Verificación de consistencia y vigencia de equivalentes.json
python3 -B -m unittest tests.test_equivalentes tests.test_mutar_codigo_custodia

# Verificación cruzada mutante por mutante (falla con mutante, pasa limpio)
python3 scratch/verificar_mutantes.py

# Verificación de que tools/cli.py no quedó modificado
diff -u tools/cli.py tools/cli.py.bak

# Limpieza de archivos auxiliares y __pycache__
rm tools/cli.py.bak
find . -name "__pycache__" -exec rm -rf {} +

# Suite completa de tests del proyecto
python3 -m unittest discover -s tests -t .
```
