# Revisión final de agy — sólo lectura

Recibida el 2026-09-12. Se conserva el resultado del contraste; las discrepancias
documentales señaladas se corrigieron en el cierre de Codex. La sugerencia de un test adicional
de verbo desconocido fue preventiva: los mutantes de ese despacho ya fueron detectados en
ambas rondas. No se modificó ese test ni se declaró un defecto de runtime por esa sugerencia.

A continuación se presentan los hallazgos de la revisión de solo lectura, contrastando [`docs/12-tareas.md`](../../docs/12-tareas.md), [`vault-kb/planes/PLAN-0.16.0-TAREAS.md`](../../planes/PLAN-0.16.0-TAREAS.md), [`vault-kb/estudios/0.16.0-tareas/INFORME-AGY.md`](INFORME-AGY.md), [`tools/tareas.py`](../../tools/tareas.py) y las pruebas del CLI:

---

### 1. Discrepancias de Roadmap y alcance futuro (INFORME-AGY vs PLAN)

* **Ruta y líneas**: [`vault-kb/estudios/0.16.0-tareas/INFORME-AGY.md#L219-L224`](INFORME-AGY.md#L219-L224)
* **Discrepancia**: El informe final describe erróneamente P2 como *«Proyección indexada en base de datos local SQLite»* y P3 como *«Sincronización colaborativa y ganchos de integración con Git»*. En [`vault-kb/planes/PLAN-0.16.0-TAREAS.md#L119-L154`](../../planes/PLAN-0.16.0-TAREAS.md#L119-L154), el alcance real es:
  * **P2**: Captura de material (`anotar`, `adjuntar`), URLs con timestamp, búsqueda de texto y referencias entre tareas/notas/código, resumen de cantidades y diagnóstico de estado en Git (distinguir archivos versionados de locales no seguidos o ignorados).
  * **P3**: Sensor determinista de hechos de tareas/adjuntos y medidas de proyecto opcionales sobre integridad de referencias y cobertura de seguimiento.
  * SQLite y sincronización no forman parte de P2/P3 (la sincronización remota está explícitamente en *«Fuera de esta entrega»*, líneas 172-176).
* **Corrección propuesta**: Ajustar la Sección 7 de `INFORME-AGY.md` alineando los resúmenes de P2 y P3 con las definiciones de `vault-kb/planes/PLAN-0.16.0-TAREAS.md`.

---

### 2. Discrepancia en el conteo de tests y estado de archivos (INFORME-AGY vs árbol real)

* **Ruta y líneas**: [`vault-kb/estudios/0.16.0-tareas/INFORME-AGY.md#L17`](INFORME-AGY.md#L17), [`L122`](INFORME-AGY.md#L122), [`L124`](INFORME-AGY.md#L124), [`L142-L143`](INFORME-AGY.md#L142-L143)
* **Discrepancia**:
  1. `INFORME-AGY.md` consigna 22 tests en `tests/test_tareas.py` y 18 en `tests/test_tareas_revision.py`. El recuento verificado en el árbol congelado es **21** en `test_tareas.py` y **19** en `test_tareas_revision.py` (con la incorporación de `test_gitignore_del_proyecto_no_oculta_las_tareas`), totalizando 40.
  2. En la tabla de archivos modificados (L122), `pyproject.toml` figura como «Modificado», pero quedó sin diff final contra `HEAD`.
* **Corrección propuesta**: Actualizar en `INFORME-AGY.md` el desglose a 21 + 19 = 40 tests, y consignar `pyproject.toml` como «Sin diff final (se retiró el entrypoint extra y se preservó el archivo original)».

---

### 3. Opciones y banderas omitidas en la especificación CLI (`docs/12-tareas.md` vs `tools/tareas.py`)

* **Ruta y líneas**: [`docs/12-tareas.md#L87-L95`](../../docs/12-tareas.md#L87-L95) vs [`tools/tareas.py#L625-L638`](../../tools/tareas.py#L625-L638)
* **Discrepancia**:
  1. **`--json` en `nueva`**: La tabla de comandos omite `--json` en la fila de `oracle tarea nueva`. La opción está implementada ([`tools/tareas.py#L637`](../../tools/tareas.py#L637)), testeada en `test_nueva_salida_json_contiene_id_y_ruta` y documentada en la ayuda de consola ([`tools/tareas.py#L1011`](../../tools/tareas.py#L1011)).
  2. **Atajos cortos `-e` y `-t`**: La tabla documenta `--etiqueta` y `--texto`, pero no indica sus alias cortos `-e` y `-t` disponibles en `nueva` y `listar`.
  3. **Bandera común `--proyecto <ruta>`**: Los 7 subcomandos aceptan `--proyecto <ruta>` ([`tools/tareas.py#L562, L638, L715, L786, L869, L915, L961`](../../tools/tareas.py)), pero la tabla no lo explicita ni lista una columna/nota de opciones comunes.
* **Corrección propuesta**: En la tabla de la Sección 5 de `docs/12-tareas.md`:
  * En `nueva`: `<titulo> [--etiqueta/-e <etiqueta>]... [--prioridad <n>] [--sufijo <sufijo>] [--json] [--proyecto <ruta>]`
  * En `listar`: `[--cerradas] [--todas] [--etiqueta/-e <etiqueta>] [--texto/-t <palabra>] [--json] [--proyecto <ruta>]`
  * Añadir nota indicando que `--proyecto <ruta>` aplica a todos los subcomandos.

---

### 4. Archivos auxiliares tolerados sin documentar (`docs/12-tareas.md` vs `tools/tareas.py`)

* **Ruta y líneas**: [`docs/12-tareas.md#L95`](../../docs/12-tareas.md#L95) vs [`tools/tareas.py#L23`](../../tools/tareas.py#L23), [`L502-L506`](../../tools/tareas.py#L502-L506)
* **Discrepancia**: `vault-kb/planes/PLAN-0.16.0-TAREAS.md#L110` exige que *«README.md y archivos auxiliares documentados no se confunden con tareas rotas»*. La implementación define `ARCHIVOS_AUXILIARES_PERMITIDOS = frozenset({"README.md", "README", ".gitignore"})` y rechaza cualquier otro archivo suelto en `tareas/` como error con código 1. Sin embargo, `docs/12-tareas.md` no especifica qué archivos auxiliares están permitidos.
* **Corrección propuesta**: Añadir una breve aclaración en `docs/12-tareas.md` (Sección 1 o 5) indicando que los únicos archivos tolerados directamente en la raíz de `tareas/` son `README.md`, `README` y `.gitignore`; cualquier otro archivo suelto es auditado como anomalía.

---

### 5. Incompatibilidad de banderas mutuamente excluyentes (`docs/12-tareas.md` vs `tools/tareas.py`)

* **Ruta y líneas**: [`docs/12-tareas.md#L109-L117`](../../docs/12-tareas.md#L109-L117) vs [`tools/tareas.py#L718-L724`](../../tools/tareas.py#L718-L724), [`L789-L792`](../../tools/tareas.py#L789-L792)
* **Discrepancia**: Si el usuario combina `--cerradas` con `--todas` en `listar`, o `--ruta` con `--json` en `ver`, el runtime imprime error y sale con **código 1** (validación lógica de dominio posterior al parseo). `docs/12-tareas.md` distingue código 1 (dominio) y código 2 (sintaxis `argparse`), pero no menciona que estas parejas de banderas son mutuamente excluyentes.
* **Corrección propuesta**: Indicar explícitamente en la descripción de `listar` y `ver` en `docs/12-tareas.md` que `--cerradas`/`--todas` y `--ruta`/`--json` son mutuamente excluyentes.

---

### 6. Custodia de mutación en verbos desconocidos de `tarea` (`tests/test_cli.py`)

* **Ruta y líneas**: [`tests/test_cli.py#L1061-L1065`](../../tests/test_cli.py#L1061-L1065) vs [`tools/cli.py#L1033-L1034`](../../tools/cli.py#L1033-L1034)
* **Hallazgo / Riesgo de mutante sobreviviente**: Codex agregó `("tarea", ...)` en `test_ayudas_de_sustantivos_devuelven_cero` (L1048), pero en el test inmediatamente siguiente (`test_verbos_desconocidos_fallan_y_muestran_disponibles`, L1061) sólo se prueban `medida`, `caso` y `proyecto`.
  En [`tools/cli.py#L1033-L1034`](../../tools/cli.py#L1033-L1034), la rama:
  ```python
  if subcomando == "tarea" and resto and resto[0] not in verbos_aceptados("tarea"):
      return _verbo_desconocido("tarea", resto[0])
  ```
  podría dejar mutantes vivos si ninguna prueba general invoca un verbo inválido sobre `tarea` vía `cli.main`.
* **Corrección propuesta (para que Codex incorpore cuando desactive el congelamiento)**:
  En `tests/test_cli.py#L1065`, añadir la tupla:
  `("tarea", "borrar", ("init", "nueva", "listar", "ver", "cerrar", "reabrir", "revisar")),`
