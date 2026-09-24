# Informe de Implementación: el MCP de Oracle al día (0.27.0)

**Tarea:** [`20260916-210604-mcp-027`](../../tareas/20260916-210604-mcp-027/TAREA.md)  
**Fecha:** 2026-09-16  
**Autor:** Agente Antigravity (agy)  
**Directorio de trabajo:** `/tmp/claude-1000/-home-workstation-Dev-oracle/27d97167-363a-4362-9167-701b6c10974b/scratchpad/wt-027`

---

## 1. Resumen Ejecutivo

Se implementaron las tres capacidades requeridas para actualizar el servidor `oracle-mcp` al estado de Oracle 0.27.0:

1. **Soporte de sombras en `oracle_evaluar`**: Incorporación de la clave obligatoria `sombra` (`null` si no está en sombra o si fue evaluada en memoria; diccionario con `desde`, `porque`, `cota` y `perdona` si está en sombra), reutilizando la lógica canónica de `Informe.supera_su_cota` de `nucleo/medida.py`. El esquema migró a `oracle.mcp/evaluacion/v2`.
2. **Nueva herramienta `oracle_juzgar`**: Juicio completo de evidencias JSON contra el catálogo efectivo del proyecto fijado al arranque (con o sin `ids`), aplicando sombras, cotas y reporte de medidas del catálogo propio no aplicadas. Esquema `oracle.mcp/juzgar/v1` protegido con `_evaluacion_estable`.
3. **Nueva herramienta `oracle_tareas` (sólo lectura)**: Consulta del tracker local (`tareas/`) para agentes sin shell, soportando las acciones `listar` (abiertas, cerradas, etiquetas), `ver` (por id o prefijo), `buscar` (texto en tareas y notas) y `hechos` (relaciones para evaluación). Esquema `oracle.mcp/tareas/v1`. Falla con `TRACKER_AUSENTE` si no existe la carpeta `tareas/`. Se excluyen deliberadamente las operaciones de escritura para no romper la correspondencia atómica con commits de Git.
4. **Contrato normativo y documentación**: Actualización completa del bloque JSON en `docs/mcp-contrato.md` (idéntico a `mcp.HERRAMIENTAS`), incorporación de prosa explicativa, ampliación de la tabla de códigos de error de dominio y adición de la sección de MCP en `README.md`.
5. **Batería de pruebas unitarias**: Creación de `tests/test_mcp_027.py` cubriendo exhaustivamente todas las ramas requeridas.

---

## 2. Detalle de Archivos Modificados y Creados

### `tools/juzgar.py` (Refactorización)
- Se extrajo la función pura:
  ```python
  def juzgar_evidencia(
      proy: Proyecto,
      evidencia: dict,
      ids: tuple[str, ...] | list[str] = (),
  ) -> Informe:
  ```
  Esta función resuelve el catálogo efectivo, evalúa la evidencia, calcula sombras y cotas desde `oracle.json`, recopila `no_aplicadas` para medidas propias y levanta `MedidaDesconocida` o `MedidaNoAplicable` si se solicitaron `ids` específicos con problemas.
- `cmd_juzgar` fue adaptado para consumir `juzgar_evidencia`, preservando exactamente su salida de texto en stdout/stderr y sus códigos de salida de proceso (0 si pasa o está en sombra dentro de cota; 1 si falla o no aplica ninguna medida; 2 si hay error de sintaxis o argumentos).

### `tools/tareas.py`, `tools/tareas_contexto.py`, `tools/tareas_hechos.py` (Refactorización)
- En `tools/tareas.py`: Se extrajeron `filtrar_tareas` y `leer_tarea(raiz_tareas: Path, id_o_prefijo: str) -> Tarea`, permitiendo su reutilización tanto por `cmd_listar` y `cmd_ver` como por el servidor MCP.
- En `tools/tareas_contexto.py`: Se extrajo `buscar_en_tracker(raiz: Path, texto_buscado: str) -> dict[str, Any]`, utilizada por `cmd_buscar` y `oracle_tareas`.
- En `tools/tareas_hechos.py`: Se reutilizó la función existente `extraer_hechos(raiz: Path, *, con_git: bool = False) -> dict[str, list[dict[str, Any]]]`.

### `tools/mcp.py` (Ampliación del Servidor)
- **`HERRAMIENTA_EVALUAR`**:
  - `outputSchema` migrado a `oracle.mcp/evaluacion/v2`.
  - Agregado campo obligatorio `sombra` a `required` y su especificación con `oneOf` (`null` o diccionario con `desde`, `porque`, `cota` y `perdona`).
- **`HERRAMIENTA_JUZGAR`**:
  - Declarada con esquema `oracle.mcp/juzgar/v1`.
  - Validación estricta de argumentos en `_validar_juzgar`.
  - Implementación en `juzgar_para_mcp` con contexto `_evaluacion_estable`.
  - Manejo de excepciones mapeando `MedidaDesconocida` a `_error_id_ausente` (`MEDIDA_DESCONOCIDA` o `MEDIDA_NO_EFECTIVA`) y `MedidaNoAplicable` a `MEDIDA_NO_APLICABLE`.
  - Inclusión de advertencia explicativa y `ok: false` cuando ninguna medida aplica a la evidencia.
- **`HERRAMIENTA_TAREAS`**:
  - Declarada con esquema `oracle.mcp/tareas/v1`.
  - Validación de acciones (`listar`, `ver`, `buscar`, `hechos`) en `_validar_tareas`.
  - Implementación en `tareas_para_mcp`, validando existencia de `tareas/` (`TRACKER_AUSENTE`), auditoría de registros (`TRACKER_INVALIDO`), búsqueda de prefijos únicos (`TAREA_NO_ENCONTRADA`, `ID_AMBIGUO`) y textos no vacíos (`ARGUMENTOS_INVALIDOS`).
- **`HERRAMIENTAS` y `Servidor`**:
  - `HERRAMIENTAS` registra las 5 herramientas en orden normativo: `[HERRAMIENTA_CATALOGO, HERRAMIENTA_EVALUAR, HERRAMIENTA_DESAFIAR, HERRAMIENTA_JUZGAR, HERRAMIENTA_TAREAS]`.
  - `Servidor._resultado_herramienta` despacha cada una de las 5 herramientas.

### `docs/mcp-contrato.md` (Contrato Normativo)
- Actualizado el bloque normativo entre `<!-- herramientas-json:inicio -->` y `<!-- herramientas-json:fin -->` para que sea idéntico en estructura, claves y tipos a `HERRAMIENTAS` de `tools/mcp.py`.
- Actualizada la sección `## Decisión` formalizando las 5 herramientas y las preguntas que atienden.
- Agregada prosa descriptiva de `sombra` en `oracle_evaluar` (v2), de `oracle_juzgar` y de `oracle_tareas`.
- Agregados los nuevos códigos de dominio a la tabla de errores:
  - `MEDIDA_NO_APLICABLE`
  - `TRACKER_AUSENTE`
  - `TRACKER_INVALIDO`
  - `TAREA_NO_ENCONTRADA`
  - `ID_AMBIGUO`
- Actualizada la tabla de exclusión de CLI explicando por qué las operaciones de escritura del tracker no se exponen vía MCP.

### `README.md`
- Se incorporó la sección `## Servidor MCP (sólo lectura)` describiendo el propósito y nombrando las cinco herramientas expuestas por `oracle-mcp`.

### `tests/test_mcp_027.py` (Nuevas Pruebas Unitarias)
- Se implementó una batería de tests unitarios dividida en:
  - `ContratoNormativoTests`: Comprueba que `MCP-CONTRATO.md` contenga las 5 herramientas y que coincida exactamente con `mcp.HERRAMIENTAS`.
  - `EvaluarSombrasTests`: Comprueba medidas sin sombra (`null`), medidas en memoria (`null`), sombras sin cota (perdona rojo, no perdona verde ni sin evidencia), sombras con cota (dentro de cota perdona, fuera de cota no perdona).
  - `JuzgarMcpTests`: Juicio sin ids con reporte de `no_aplicadas`, juicio con ids específicos, errores por id inexistente (`MEDIDA_DESCONOCIDA`), error por relación faltante (`MEDIDA_NO_APLICABLE`), advertencia cuando no aplica ninguna medida, despacho JSON-RPC.
  - `TareasMcpTests`: Falla con `TRACKER_AUSENTE`, listado de abiertas/cerradas/etiqueta, ver tarea por id/prefijo y fallos por inexistente o ambiguo, búsqueda de texto y fallos por texto vacío, hechos relacionales y despacho JSON-RPC.

---

## 3. Decisiones de Diseño

1. **Cálculo de perdón de sombra sin duplicación**:
   En `tools/mcp.py`, el cálculo de si una sombra perdona una medida se realiza instanciando `Informe(cotas=cotas_de_sombra(...), en_sombra=...)` y llamando a su método `supera_su_cota(v)`. De este modo, la regla:
   - Valor numérico no booleano `<=` cota $\rightarrow$ perdona.
   - Valor numérico `>` cota $\rightarrow$ no perdona.
   - Valor no numérico o booleano $\rightarrow$ no perdona.
   - Sin cota $\rightarrow$ siempre perdona si el estado es `rojo`.
   - Estado `verde` o `sin_evidencia` $\rightarrow$ `perdona` es `False`.
   se evalúa directamente con el núcleo, garantizando consistencia absoluta con `oracle juzgar`.

2. **Invariabilidad de `estado`**:
   El estado devuelto sigue siendo estrictamente `"verde"`, `"rojo"` o `"sin_evidencia"`. La sombra no altera la realidad observada, sólo indica en `sombra.perdona` si la política del proyecto asume o tolera dicha deuda.

3. **Sólo lectura en `oracle_tareas`**:
   Se respetó la decisión de diseño de que las modificaciones del tracker (`nueva`, `anotar`, `cerrar`, `etiquetar`) pertenecen al flujo de commits en consola. Exponer escrituras por MCP sin confirmación atómica en Git causaría que `oracle tarea hechos --git` detecte discrepancias y ponga en rojo el proyecto.

4. **Preservación de la interfaz CLI**:
   Las funciones CLI `cmd_juzgar`, `cmd_listar`, `cmd_ver`, `cmd_buscar` y `cmd_hechos` no sufrieron cambios en su comportamiento observable ni en sus firmas de subcomandos.

---

## 4. Contradicciones con Tests Existentes

En estricto cumplimiento con la directiva:
> *"No edites tests existentes: si uno contradice lo que pide este encargo, anotalo en el informe."*

Se identificó la siguiente contradicción en `tests/test_mcp.py`:

- **`tests/test_mcp.py::EvaluarTests` (líneas 240–259)**:
  El método auxiliar `_contenido` define la expectativa de salida para `oracle_evaluar` fijada en 0.7.0:
  ```python
  "esquema": "oracle.mcp/evaluacion/v1"
  ```
  y no incluye la clave `sombra`.
  
  Dado que el encargo 0.27.0 exige que `oracle_evaluar` migre su esquema a `oracle.mcp/evaluacion/v2` y añada la clave obligatoria `sombra` (incluso con valor `null` si no está en sombra), las aserciones de `EvaluarTests` en `tests/test_mcp.py` que comprueban contra `v1` sin `sombra` divergirán del nuevo comportamiento productivo.
  
  Conforme a las instrucciones, **`tests/test_mcp.py` no fue modificado**. Esta actualización de fixtures y aserciones queda reservada para la fase de release.

---

## 5. Verificaciones y Restricciones Operativas

De acuerdo con las reglas del encargo:
> *"Sólo herramientas de lectura y edición; NO shell, NO tests, NO subagentes, NO red, NO commits. ... sin afirmar verificaciones que no corriste."*

Se deja constancia explícita de que:
- **No se ejecutó ningún comando en el shell**, no se corrió `pytest`, `unittest` ni el intérprete de `python`.
- **No se utilizó la red** ni herramientas externas.
- **No se realizaron commits en Git**.
- La corrección sintáctica, la consistencia de tipos y la adhesión al contrato fueron verificadas exclusivamente mediante inspección estática del código, trazabilidad de referencias y validación cruzada con las interfaces del repositorio.
