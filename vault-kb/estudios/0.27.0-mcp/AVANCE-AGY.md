# Avance de agy — el MCP de Oracle al día (0.27.0)

## Estado actual: Completado (redacción de informe final)

### Lectura previa completada
- [x] `tareas/20260916-210604-mcp-027/TAREA.md`
- [x] `docs/mcp-contrato.md`
- [x] `tools/mcp.py`
- [x] `tools/juzgar.py`
- [x] `tests/test_mcp.py`
- [x] `tests/test_juzgar_cota_y_ausentes.py`
- [x] `nucleo/medida.py` (`Informe.supera_su_cota`, `Veredicto`)
- [x] `nucleo/proyecto.py` (`configuracion`, `cotas_de_sombra`, `SIN_COTA`)
- [x] `tools/tareas*.py` (`tareas.py`, `tareas_contexto.py`, `tareas_hechos.py`)
- [x] `README.md`

### Tareas ejecutadas
1. [x] **Refactorización de `tools/juzgar.py`**:
   - Extraída función pura `juzgar_evidencia(proy, evidencia, ids=()) -> Informe` respetando catálogo efectivo, sombras, cotas y medidas no aplicadas.
   - Definidas excepciones `MedidaDesconocida` y `MedidaNoAplicable` para preservar exactamente la salida de consola y códigos de retorno (0, 1, 2) de `cmd_juzgar`.
2. [x] **Refactorización de `tools/tareas*.py`**:
   - Extraídas `filtrar_tareas` y `leer_tarea(raiz_tareas, id_o_prefijo)` en `tools/tareas.py`, manteniendo el comportamiento de `cmd_listar` y `cmd_ver`.
   - Extraída `buscar_en_tracker(raiz, texto_buscado)` en `tools/tareas_contexto.py`.
   - Reutilizada `extraer_hechos(raiz, con_git=...)` de `tools/tareas_hechos.py`.
3. [x] **Ampliación de `tools/mcp.py`**:
   - `oracle_evaluar`: añade clave obligatoria `sombra` (`null` si no está en sombra o evaluada en memoria; objeto con `desde`, `porque`, `cota`, `perdona` si lo está, reutilizando `Informe.supera_su_cota`). Esquema migrado a `oracle.mcp/evaluacion/v2`.
   - `oracle_juzgar`: nueva herramienta de sólo lectura (esquema `oracle.mcp/juzgar/v1`) con `_evaluacion_estable`, reutilizando `juzgar_evidencia`.
   - `oracle_tareas`: nueva herramienta de sólo lectura (esquema `oracle.mcp/tareas/v1`) que atiende acciones `listar`, `ver`, `buscar`, `hechos`. Falla con `TRACKER_AUSENTE` si no existe `tareas/`.
   - Registradas las 5 herramientas en `HERRAMIENTAS` y despachadas en `Servidor._resultado_herramienta`.
4. [x] **Actualización de `docs/mcp-contrato.md`**:
   - Bloque normativo JSON entre `<!-- herramientas-json:inicio -->` y `<!-- herramientas-json:fin -->` actualizado con las 5 herramientas en idéntico orden y formato que en Python.
   - Sección `## Decisión` actualizada a 5 herramientas.
   - Prosa explicativa agregada para `sombra` en `oracle_evaluar` (v2), `oracle_juzgar` y `oracle_tareas`.
   - Códigos de error agregados a la tabla de errores (`MEDIDA_NO_APLICABLE`, `TRACKER_AUSENTE`, `TRACKER_INVALIDO`, `TAREA_NO_ENCONTRADA`, `ID_AMBIGUO`).
   - Tabla de exclusión de CLI actualizada explicando por qué las escrituras del tracker no se exponen vía MCP.
5. [x] **Actualización de `README.md`**:
   - Agregada sección `## Servidor MCP (sólo lectura)` nombrando y describiendo las cinco herramientas.
6. [x] **Creación de `tests/test_mcp_027.py`**:
   - Batería de pruebas unitarias que cubren:
     - `ContratoNormativoTests`: correspondencia exacta entre `MCP-CONTRATO.md` y `HERRAMIENTAS`.
     - `EvaluarSombrasTests`: sombras con y sin cota, dentro y fuera de cota, verdes y sin evidencia, evaluación en memoria, esquema v2.
     - `JuzgarMcpTests`: con y sin `ids`, medidas no aplicadas, ids desconocidos/no aplicables, advertencias ante evidencia vacía, estabilidad y JSON-RPC.
     - `TareasMcpTests`: tracker ausente, listar (abierta/cerrada/etiqueta), ver (id/prefijo/ambiguo/inexistente), buscar (texto/vacío), hechos y JSON-RPC.
7. [x] **Redacción de `vault-kb/estudios/0.27.0-mcp/INFORME-AGY.md`**:
   - Documentación exhaustiva de lo realizado, arquitectura, decisiones y registro de contradicciones con tests existentes (sin afirmar corridas no ejecutadas).
