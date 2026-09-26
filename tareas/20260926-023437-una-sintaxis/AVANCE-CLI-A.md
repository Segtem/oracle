# Avance de Mutación — Lista A (tools/cli.py)

Tarea: `20260926-023437-una-sintaxis`  
Archivo de sobrevivientes asignado: `tareas/20260926-023437-una-sintaxis/SOBREVIVIENTES-CLI-A.txt`  
Archivo de tests creado: `tests/test_cli_convertir_mutacion.py`  
Archivo de equivalentes actualizado: `equivalentes.json`

---

## 1. Resumen

- **Total de mutantes analizados en Lista A**: 25
- **Mutantes matados con tests nuevos**: 23
- **Mutantes declarados equivalentes**: 2
- **Modificaciones en `tools/cli.py`**: Ninguna (archivo intacto).
- **Estado final de la suite**: 2670 tests pasando (`OK`).

---

## 2. Mutantes declarados equivalentes (2)

### 1. `tools/cli.py:738:74:constante`
- **Sitio**: `for base, subdirectorios, archivos in os.walk(directorio, followlinks=False):` → `followlinks=True`
- **Razón**:
  > En `tools/cli.py`, `followlinks=False` → `followlinks=True` en `_fuentes`. La función recorre en modo top-down y en la línea inmediatamente siguiente filtra `subdirectorios[:] = sorted(nombre for nombre in subdirectorios if not (Path(base) / nombre).is_symlink())`. Al eliminar in-place todos los enlaces simbólicos de `subdirectorios`, para cada directorio restante `islink(new_path)` en `os.walk` evalúa siempre a `False`. En consecuencia, la guarda interna `if followlinks or not islink(new_path):` de `os.walk` es invariablemente verdadera para cualquier elemento restante, sea `followlinks` verdadero o falso. Ninguna estructura de directorios ni archivos puede producir una diferencia de recorrido ni modificar los generadores devueltos.

### 2. `tools/cli.py:783:39:constante`
- **Sitio**: `temporal.unlink(missing_ok=True)` → `temporal.unlink(missing_ok=False)`
- **Razón**:
  > En `tools/cli.py`, `temporal.unlink(missing_ok=True)` → `missing_ok=False` en el bloque `finally` de `_reemplazar`. La variable `temporal` sólo deja de ser `None` si la llamada previa a `NamedTemporaryFile(..., delete=False)` creó exitosamente el archivo en el sistema de archivos. Ninguna instrucción posterior dentro del bloque `try` elimina dicho archivo (la llamada `os.link(temporal, destino)` crea un enlace duro adicional al mismo inodo y `origen.unlink()` elimina el archivo fuente de entrada, no el temporal). Por lo tanto, al alcanzar `finally`, el archivo apuntado por `temporal` siempre existe en disco. En un archivo existente, `unlink(missing_ok=True)` y `unlink(missing_ok=False)` ejecutan la misma operación y ninguno genera `FileNotFoundError`. Ningún flujo de ejecución alcanzable distingue ambos valores booleanos.

---

## 3. Mutantes matados (23)

Cada uno fue probado aplicando la mutación sobre `tools/cli.py`, borrando `__pycache__`, verificando que el test falla, restaurando desde copia de respaldo, borrando `__pycache__` y verificando que el test pasa en limpio.

| # | Mutante | Cambio | Test en `tests/test_cli_convertir_mutacion.py` |
|---|---|---|---|
| 1 | `tools/cli.py:720:8:retorno` | `return False` → `return None` | `test_mismo_arbol_distintos_tipos_devuelve_falso_no_none` |
| 2 | `tools/cli.py:766:7:booleano` | `or` ↔ `and` | `test_reemplazar_destino_existente_archivo_regular_falla_con_mensaje_preciso` |
| 3 | `tools/cli.py:782:11:comparador` | `IsNot` → `Is` | `test_reemplazar_exitoso_limpia_archivo_temporal` |
| 4 | `tools/cli.py:786:64:constante` | `False` → `True` | `test_convertir_lote_defecto_no_escribe` |
| 5 | `tools/cli.py:787:7:booleano` | `or` ↔ `and` | `test_convertir_lote_rechaza_archivo_regular_como_directorio` |
| 6 | `tools/cli.py:789:8:retorno` | `return 1` → `return None` | `test_convertir_lote_directorio_invalido_retorna_uno_no_none` |
| 7 | `tools/cli.py:789:15:constante` | `1` → `2` | `test_convertir_lote_directorio_invalido_retorna_uno_no_dos` |
| 8 | `tools/cli.py:801:15:booleano` | `or` ↔ `and` | `test_convertir_lote_rechaza_origen_que_es_enlace_simbolico` |
| 9 | `tools/cli.py:803:15:booleano` | `or` ↔ `and` | `test_convertir_lote_rechaza_destino_que_ya_existe_como_archivo_regular` |
| 10 | `tools/cli.py:807:15:booleano` | `and` ↔ `or` | `test_convertir_lote_solo_corpus_no_carga_macros` |
| 11 | `tools/cli.py:807:15:comparador` | `Eq` → `NotEq` | `test_convertir_lote_catalogo_carga_macros` |
| 12 | `tools/cli.py:807:39:comparador` | `Is` → `IsNot` | `test_convertir_lote_catalogo_requiere_macros_inicialmente_none` |
| 13 | `tools/cli.py:818:31:constante` | `1` → `2` | `test_convertir_lote_cuenta_exacta_no_convertibles` |
| 14 | `tools/cli.py:825:34:constante` | `False` → `True` | `test_cmd_convertir_defecto_no_escribe` |
| 15 | `tools/cli.py:864:8:retorno` | `return 1` → `return None` | `test_cmd_convertir_error_sintaxis_retorna_uno_no_none` |
| 16 | `tools/cli.py:864:15:constante` | `1` → `2` | `test_cmd_convertir_error_sintaxis_retorna_uno_no_dos` |
| 17 | `tools/cli.py:874:7:negacion` | se borra `not` | `test_cmd_formatear_ruta_relativa_a_raiz_proyecto` |
| 18 | `tools/cli.py:885:24:booleano` | `or` ↔ `and` | `test_cmd_formatear_directorio_ignora_carpeta_diferencial` |
| 19 | `tools/cli.py:888:12:retorno` | `return 1` → `return None` | `test_cmd_formatear_directorio_sin_archivos_retorna_uno_no_none` |
| 20 | `tools/cli.py:888:19:constante` | `1` → `2` | `test_cmd_formatear_directorio_sin_archivos_retorna_uno_no_dos` |
| 21 | `tools/cli.py:895:7:booleano` | `or` ↔ `and` | `test_cmd_formatear_archivo_extension_no_soportada_rechaza` |
| 22 | `tools/cli.py:897:8:retorno` | `return 1` → `return None` | `test_cmd_formatear_archivo_extension_invalida_retorna_uno_no_none` |
| 23 | `tools/cli.py:897:15:constante` | `1` → `2` | `test_cmd_formatear_archivo_extension_invalida_retorna_uno_no_dos` |

---

## 4. Comandos ejecutados

1. Lectura del estado de la tarea:
   ```bash
   python3 tools/cli.py tarea ver una-sintaxis
   ```

2. Instalación de dependencia de empaquetado en el entorno de pruebas:
   ```bash
   python3 -m pip install "setuptools>=68"
   ```

3. Verificación de tests de empaquetado y enlaces PyPI:
   ```bash
   python3 -B -m unittest tests.test_cli_integracion.EmpaquetadoCliTests.test_wheel_instalado_trae_datos_y_ejecuta_oracle_test tests.test_enlaces_pypi.EnlacesDePyPI.test_el_wheel_conserva_los_enlaces_del_readme
   ```

4. Verificación de la suite de equivalentes y herramientas tras actualizar `equivalentes.json`:
   ```bash
   python3 -B -m unittest tests/test_equivalentes.py tests/test_herramientas.py
   ```

5. Verificación individual de cada mutante de Lista A (aplicación a mano sobre `tools/cli.py`, corrida con `-B`, fallo verificado, restauración desde `.bak` y paso en verde):
   ```bash
   python3 /home/agy/.gemini/antigravity-cli/brain/a3d6598c-8e1d-420c-903f-93e14de3922f/scratch/verificar_mutantes.py
   ```

6. Verificación unitaria directa del nuevo archivo de pruebas:
   ```bash
   python3 -B -m unittest tests/test_cli_convertir_mutacion.py
   ```

7. Verificación de integridad de `tools/cli.py`:
   ```bash
   diff -u tools/cli.py.bak tools/cli.py
   ```

8. Ejecución completa final de la suite de pruebas:
   ```bash
   python3 -m unittest discover -s tests -t .
   ```
   Resultado: `Ran 2670 tests in 139.945s` — `OK`.
