# Avance: oracle formatear como chequeo, código de salida y ayuda al día

Tarea: `20260926-235409-formatear-chequeo`
Fecha: 2026-09-27

## Resumen de cambios realizados

Se completó íntegramente el encargo de la nota del 2026-09-27:

1. **`oracle formatear` como chequeo en CI:**
   - En `_formatear_uno` de `tools/cli.py`, si un archivo requiere formato y no se pasó `--escribir`, imprime el diff, muestra la sugerencia `oracle formatear <ruta> --escribir` y retorna código de salida `1`.
   - Si todos los archivos ya tienen forma única, retorna `0` (`ya tiene forma única`).
   - Al invocar sobre un directorio, `cmd_formatear` propaga el código máximo (`max(codigos)`), saliendo con `1` si al menos un archivo requiere formato, y con `0` si todos ya están normalizados o fueron escritos exitosamente.
   - Cualquier error de lectura, parseo o sintaxis continúa retornando `1` e informándose con `✗`.

2. **Sin sugerencia redundante con `--escribir`:**
   - Cuando se pasa `--escribir`, `_formatear_uno` muestra el diff y `escrito`, omitiendo la línea de sugerencia `oracle formatear <ruta> --escribir`. Retorna `0` tras escribir exitosamente.

3. **Ayuda de `convertir --a-superficie`:**
   - En la función `ayuda()` de `tools/cli.py`, la línea correspondiente ahora dice:
     `oracle convertir <directorio> --a-superficie [--escribir]  Migra medidas, casos y relaciones JSON con ida y vuelta exacta`

4. **Documentación:**
   - En `docs/03-escribir-una-medida.md`, se documentó el uso de `oracle formatear` como chequeo de CI (código de salida 1 si requiere formato, 0 si ya tiene forma única) y el comportamiento limpio con `--escribir`.
   - En `docs/como-funciona.md`, se regeneró el bloque de salida mediante `python3 tools/guia.py --escribir docs/como-funciona.md`.
   - Se regeneró el sitio HTML mediante `python3 tools/sitio.py --escribir` (`docs/03-escribir-una-medida.html` y `docs/como-funciona.html`).
   - Se actualizaron las cifras en `README.md` mediante `python3 tools/cifras.py --actualizar` (2123 tests, 7948 sitios de mutación).

## Tests y verificación

1. **Tests que fallaron sin el cambio:**
   - Se adaptaron aserciones previas en `tests/test_forma_unica_texto.py` (`cli.cmd_formatear` esperando 1 en chequeo y ausencia de sugerencia con `--escribir`) y en `tests/test_cli_formatear_mutacion.py`.
   - Se agregaron 6 pruebas unitarias nuevas en `tests/test_cli_formatear_mutacion.py`:
     - `test_formatear_sin_escribir_sale_uno_si_requiere_formato`
     - `test_formatear_sin_escribir_sale_cero_si_tiene_forma_unica`
     - `test_formatear_con_escribir_sale_cero_y_no_imprime_sugerencia`
     - `test_formatear_directorio_sin_escribir_sale_uno_si_alguno_requiere_formato`
     - `test_formatear_directorio_con_escribir_sale_cero_si_pudo_escribir`
     - `test_ayuda_convertir_incluye_relaciones`
   - Se ejecutaron los tests contra el código sin modificar y fallaron con `AssertionError: 0 != 1`, confirmando que discriminan el comportamiento.
   - Tras aplicar los cambios en `tools/cli.py`, pasaron los 55 tests de `test_forma_unica_texto.py` y `test_cli_formatear_mutacion.py`.

2. **Equivalentes y guías:**
   - `python3 tools/mutar_codigo.py --reapuntar-equivalentes`: 25 intactos.
   - `python3 -m unittest tests/test_equivalentes.py`: 7 tests OK.
   - `python3 tools/guia.py`: los 7 archivos de guía verificados (salidas al día).

3. **Suite entera:**
   - `python3 -m unittest discover tests`: 2123 tests OK en 112 s.
   - `python3 tools/cli.py test --rapido`: VEREDICTO VERDE.
   - `python3 tools/cli.py test`: VEREDICTO VERDE (unitarios OK, catálogo OK, corpus OK, aceptación OK, diferencial OK, mutación de medidas 1018/1018 muertos).
