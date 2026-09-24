# Inventario de artefactos fuera del motor de Oracle

Inventario elaborado para revisión de Brian antes de cualquier movimiento, renombramiento o borrado en el repositorio, en cumplimiento del punto 1 y del Próximo paso de [`TAREA.md`](TAREA.md).

> **Metodología y rigor de lectura:**
> - Elaborado exclusivamente mediante inspección y lectura directa de archivos en el worktree (`view_file`), sin invocar comandos de shell (`run_command`), sin commits y sin alterar ningún archivo del repositorio.
> - Toda afirmación sobre contenido, dependencias o citas está respaldada por la ruta y línea exacta comprobada en el código fuente o documentación.
> - Para los archivos que no fueron leídos directamente en su totalidad, no se afirma qué contienen; únicamente se registra su existencia y las referencias encontradas desde otros documentos o herramientas del repositorio.

---

## 1. Lo que es motor y se queda donde está

Conforme a la definición de [`TAREA.md`](TAREA.md#L29-L33), los siguientes directorios y archivos constituyen el motor de Oracle y permanecen en sus ubicaciones actuales:

- `nucleo/` (álgebra, parser, evaluador, marco, macros base, aislamiento)
- `catalogos/` (catálogo base de medidas universales)
- `relaciones/` (declaraciones formales de relaciones del metalenguaje)
- `perfiles/` (perfiles de plataforma, actualmente Python)
- `mutadores/` (los 29 mutadores del arnés)
- `tools/` (CLI unificado, evaluadores, sensores, arneses de mutación)
- `tests/` (suite de tests unitarios e integración)
- `corpus/` (casos de prueba y polaridades)
- `diferencial/` (implementación de referencia y fixtures diferenciales)
- `ejemplo/` (proyectos y sensores de ejemplo)
- `tareas/` (el tracker local es componente integral del producto)
- `docs/` (documentación oficial del producto: `docs/README.md`, `docs/13-primer-valor.md`, `docs/12-tareas.md`, etc.)
- `README.md`, `LICENSE`, `pyproject.toml`, `ESPECIFICACION.md`, `NOTAS-DE-RELEASE.md`

---

## 2. Inventario de artefactos no-motor (Tres Columnas)

| Qué es | Quién lo referencia (rutas y líneas comprobadas) | A dónde va (propuesta para revisión de Brian) |
|---|---|---|
| **Grupo A: Decisiones normativas (`DECISION-*.md`)** | | |
| `DECISION-001-RELACIONES-COMO-BOLSAS.md`<br>*(Leído: fundamenta por qué las relaciones son bolsas y no conjuntos)* | • [`README.md#L570`](../../README.md#L570) (tabla de decisiones)<br>• [`ESPECIFICACION.md#L17`](../../ESPECIFICACION.md#L17) (§0, justificación de cambios en 0.3)<br>• [`tools/estudio.py#L296`](../../tools/estudio.py#L296) (tupla `declarados`; `FileNotFoundError` si no existe)<br>• [`nucleo/medida.py#L10`](../../nucleo/medida.py#L10) (comentario de diseño) | `docs/decisiones/DECISION-001-RELACIONES-COMO-BOLSAS.md`<br>(con índice general en `docs/decisiones/README.md`). Alternativa: `vault-kb/decisiones/` |
| `DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md`<br>*(Leído: fundamenta el rechazo a componer medidas entre sí)* | • [`README.md#L571`](../../README.md#L571) (tabla de decisiones)<br>• [`tools/estudio.py#L297`](../../tools/estudio.py#L297) (tupla `declarados`; `FileNotFoundError` si no existe) | `docs/decisiones/DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md` |
| `DECISION-003-SIN-PARAMETROS-OPCIONALES-EN-DEFMACRO.md`<br>*(Leído: fundamenta por qué las macros no aceptan parámetros opcionales)* | • [`README.md#L572`](../../README.md#L572) (tabla de decisiones)<br>• [`tools/estudio.py#L299`](../../tools/estudio.py#L299) (tupla `declarados`; `FileNotFoundError` si no existe) | `docs/decisiones/DECISION-003-SIN-PARAMETROS-OPCIONALES-EN-DEFMACRO.md` |
| `DECISION-004-DOS-MEDIDAS-QUEDAN-SOSTENIDAS-POR-EVIDENCIA-GENERADA.md`<br>*(Leído: fundamenta la salida 1 de aceptación durante 23 días)* | • [`README.md#L573`](../../README.md#L573) (tabla de decisiones)<br>• [`ESPECIFICACION.md#L227`](../../ESPECIFICACION.md#L227) (crónica del corte 0.14.0)<br>• [`PLAN-0.14-LO-QUE-FALTA.md#L11`](../../vault-kb/planes/PLAN-0.14-LO-QUE-FALTA.md#L11) (balance histórico)<br>• [`estudios/MCP-FALLAS.md#L83`](../../vault-kb/estudios/MCP-FALLAS.md#L83) (antecedente en estudio) | `docs/decisiones/DECISION-004-DOS-MEDIDAS-QUEDAN-SOSTENIDAS-POR-EVIDENCIA-GENERADA.md` |
| `DECISION-005-CINCO-NIVELES-DE-REPRESENTACION.md`<br>*(Leído: formaliza la escala de niveles de L−2 a L2)* | • [`README.md#L574`](../../README.md#L574) (tabla de decisiones)<br>• [`docs/README.md#L13`](../../docs/README.md#L13) (enlace en el paso 6 del camino) | `docs/decisiones/DECISION-005-CINCO-NIVELES-DE-REPRESENTACION.md` |
| `DECISION-006-DE-DONDE-SALE-EL-NUMERO.md`<br>*(Leído: introduce el metadato `segun` en los umbrales)* | • [`README.md#L575`](../../README.md#L575) (tabla de decisiones) | `docs/decisiones/DECISION-006-DE-DONDE-SALE-EL-NUMERO.md` |
| `DECISION-007-BIBLIOTECAS-DE-POLITICAS.md`<br>*(Leído: formaliza la carga de bibliotecas de políticas locales)* | • [`README.md#L576`](../../README.md#L576) (tabla de decisiones)<br>• [`nucleo/diagnostico.py#L42`](../../nucleo/diagnostico.py#L42) (comentario punto 6)<br>• [`tools/cli.py#L380`](../../tools/cli.py#L380) (comentario de diseño)<br>• [`TAREA.md#L50`](TAREA.md#L50) (citado como ejemplo de cita sana) | `docs/decisiones/DECISION-007-BIBLIOTECAS-DE-POLITICAS.md` |
| `DECISION-008-EL-REPOSITORIO-SE-ABRE.md`<br>*(Leído: apertura del repositorio de privado a público)* | • [`README.md#L577`](../../README.md#L577) (tabla de decisiones) | `docs/decisiones/DECISION-008-EL-REPOSITORIO-SE-ABRE.md` |
| `DECISION-009-DE-QUIEN-ES-EL-CASO.md`<br>*(Leído: jurisprudencia de si una medida mira lo propio o todo)* | • [`README.md#L578`](../../README.md#L578) (tabla de decisiones) | `docs/decisiones/DECISION-009-DE-QUIEN-ES-EL-CASO.md` |
| `DECISION-010-EL-PAQUETE-INSTALADO-ES-OTRO-PROYECTO.md`<br>*(Leído: separación entre paquete wheel de PyPI y checkout)* | • [`README.md#L579`](../../README.md#L579) (tabla de decisiones)<br>• [`README.md#L626`](../../README.md#L626) (referencia en texto de arquitectura) | `docs/decisiones/DECISION-010-EL-PAQUETE-INSTALADO-ES-OTRO-PROYECTO.md` |
| `DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md`<br>*(Leído: autoría dual de los mutadores)* | • [`README.md#L580`](../../README.md#L580) (tabla de decisiones)<br>• [`nucleo/mutacion.py#L35`](../../nucleo/mutacion.py#L35) (comentario de autoría)<br>• [`tools/mutar.py#L85`](../../tools/mutar.py#L85) (`print("(ver DECISION-011)")`: defecto reportado en `TAREA.md#L54-L57`) | `docs/decisiones/DECISION-011-LOS-MUTADORES-TIENEN-AUTOR.md` |
| **Grupo B: Contrato normativo del MCP** | | |
| `estudios/MCP-CONTRATO.md`<br>*(Leído: especificación JSON de herramientas MCP)* | • [`README.md#L560`](../../README.md#L560) (enlace en sección Servidor MCP)<br>• [`tools/mcp_contrato.py#L22`](../../tools/mcp_contrato.py#L22) (script de sincronización)<br>• [`tests/test_mcp.py#L208`](../../tests/test_mcp.py#L208) (test compara bloque JSON palabra por palabra)<br>• [`PLAN-0.6.0-MCP.md#L4`](../../vault-kb/planes/PLAN-0.6.0-MCP.md#L4) (antecedente) | `docs/mcp-contrato.md`<br>(Documento normativo del producto; se desvincula de bitácora y se regenera desde `tools.mcp.HERRAMIENTAS`) |
| **Grupo C: Guías y tutoriales en la raíz** | | |
| `ESCRIBIR-UNA-MEDIDA.md`<br>*(Leído: tutorial de autoría de medidas)* | • [`README.md#L596`](../../README.md#L596) (enlace en sección de autoría)<br>• [`docs/README.md#L9`](../../docs/README.md#L9) (paso 3 del camino)<br>• [`tools/sintaxis.py#L185`](../../tools/sintaxis.py#L185) (tupla `DOCUMENTOS_CON_SUPERFICIE` — comprobado por `oracle test` en `tools/sintaxis.py#L196-202`; si falta falla con error)<br>• [`tools/estudio.py#L78`](../../tools/estudio.py#L78) (leído por `como_escribir()`) | `docs/escribir-una-medida.md`<br>(actualizando `tools/sintaxis.py` y `tools/estudio.py`) |
| `ORACLE-TUTORIAL-PRACTICO.md`<br>*(Leído: tutorial de programación con Oracle)* | • [`tools/sintaxis.py#L185`](../../tools/sintaxis.py#L185) (tupla `DOCUMENTOS_CON_SUPERFICIE` — verificado por `oracle test`; falla si no existe la ruta exacta) | `docs/tutorial-practico.md` (o `vault-kb/guias/` si se retira de la suite de sintaxis) |
| `ORACLE-PARA-NOTEBOOKLM.md`<br>*(Leído: compendio integral plano de 16.400 líneas generado el 2026-09-04)* | • [`ORACLE-TUTORIAL-PRACTICO.md#L3`](../../docs/tutorial-practico.md#L3) (mencionado como estudio complementario)<br>• Es el destino generado por `tools/estudio.py --archivo ORACLE-PARA-NOTEBOOKLM.md` ([`tools/estudio.py#L4`](../../tools/estudio.py#L4)) | `vault-kb/compendios/` o ignorarse en `.gitignore` si se genera a demanda |
| **Grupo D: Planes de trabajo históricos (`PLAN-*.md`)** | | |
| `PLAN-LENGUAJE.md`<br>*(Leído: plan fechado 2026-08-03 de transición a metalenguaje)* | • [`README.md#L34`](../../README.md#L34) (enlace en bloque de estado)<br>• `ORACLE-PARA-NOTEBOOKLM.md#L59` (cita histórica) | `vault-kb/planes/PLAN-LENGUAJE.md` |
| `PLAN-CORRECCION.md`<br>*(Leído: plan de corrección de auditorías P0–P3)* | • [`README.md#L588`](../../README.md#L588) (enlace en estado auditado)<br>• [`tools/estudio.py#L300`](../../tools/estudio.py#L300) (tupla `declarados`; `FileNotFoundError` si no existe) | `vault-kb/planes/PLAN-CORRECCION.md` |
| `PLAN-0.3.0.md`<br>*(Leído: plan fechado 2026-08-31 para bibliotecas y docs)* | • Archivo de planificación histórica | `vault-kb/planes/PLAN-0.3.0.md` |
| `PLAN-0.6.0-MCP.md`<br>*(Leído: plan fechado 2026-09-04 para servidor MCP)* | • [`estudios/MCP-FALLAS.md#L4`](../../vault-kb/estudios/MCP-FALLAS.md#L4) (referencia previa rectificada)<br>• [`estudios/MCP-FALLAS.md#L10`](../../vault-kb/estudios/MCP-FALLAS.md#L10) | `vault-kb/planes/PLAN-0.6.0-MCP.md` |
| `PLAN-0.14-LO-QUE-FALTA.md`<br>*(Leído: plan fechado 2026-09-09 tras corte 0.13.1)* | • [`estudios/AUTENTICIDAD-Y-TRANSCRIPCION.md#L3`](../../vault-kb/estudios/AUTENTICIDAD-Y-TRANSCRIPCION.md#L3) (cita en encabezado)<br>• [`tareas/20260919-134424-relevo/TAREA.md#L42`](../20260919-134424-relevo/TAREA.md#L42) (nota histórica) | `vault-kb/planes/PLAN-0.14-LO-QUE-FALTA.md` |
| `PLAN-IDE.md`<br>*(Leído: plan fechado 2026-08-27 para entorno LSP y clientes)* | • [`PLAN-0.14-LO-QUE-FALTA.md#L26`](../../vault-kb/planes/PLAN-0.14-LO-QUE-FALTA.md#L26) (mencionado como antecedente ya implementado) | `vault-kb/planes/PLAN-IDE.md` |
| **Grupo E: Relevos históricos en la raíz** | | |
| `RELEVO.md`<br>*(Leído: puntero de 2 líneas al tracker y AGENTS.md)* | • [`tareas/20260919-134424-relevo/TAREA.md#L13,L28`](../20260919-134424-relevo/TAREA.md#L13)<br>• [`NOTAS-DE-RELEASE.md#L13`](../../NOTAS-DE-RELEASE.md#L13) | `vault-kb/relevos/RELEVO.md` (o eliminarse si el tracker es la única fuente) |
| `RELEVO-PARA-CODEX.md`<br>*(Leído: puntero de 2 líneas al tracker y AGENTS.md)* | • [`tareas/20260919-134424-relevo/TAREA.md#L13,L28`](../20260919-134424-relevo/TAREA.md#L13) | `vault-kb/relevos/RELEVO-PARA-CODEX.md` (o eliminarse) |
| `RELEVO-2026-09-10.md`<br>*(Leído: puntero de 2 líneas al tracker y AGENTS.md)* | • [`tareas/20260919-134424-relevo/TAREA.md#L13,L28`](../20260919-134424-relevo/TAREA.md#L13)<br>• [`PLAN-0.14-LO-QUE-FALTA.md#L3`](../../vault-kb/planes/PLAN-0.14-LO-QUE-FALTA.md#L3) | `vault-kb/relevos/RELEVO-2026-09-10.md` (o eliminarse) |
| **Grupo F: Instrucciones para agentes en el repositorio** | | |
| `AGENTS.md`<br>*(Leído: protocolo de tareas, relevos y commits para agentes)* | • Punteros en `RELEVO.md#L1`, `RELEVO-PARA-CODEX.md#L1`, `RELEVO-2026-09-10.md#L1`<br>• [`NOTAS-DE-RELEASE.md#L13`](../../NOTAS-DE-RELEASE.md#L13)<br>• [`tareas/20260919-134424-relevo/TAREA.md#L18,L46`](../20260919-134424-relevo/TAREA.md#L18) | **Se queda en la raíz** (es el estándar de instrucción para agentes del entorno de trabajo) |
| **Grupo G: Estudios y análisis en `estudios/`** | | |
| `estudios/MCP-FALLAS.md`<br>*(Leído: análisis de 180 casos del corpus y diseño de MCP)* | • [`PLAN-0.6.0-MCP.md#L4,L13,L27`](../../vault-kb/planes/PLAN-0.6.0-MCP.md#L4) | `vault-kb/estudios/MCP-FALLAS.md` |
| `estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md`<br>*(Leído: postmortem sobre batalla naval y alcance de `oracle test`)* | • [`tareas/20260919-134424-naval-pm/TAREA.md`](../20260919-134424-naval-pm/TAREA.md)<br>• [`tareas/20260923-120207-ergonomia/TAREA.md#L19,L42`](../20260923-120207-ergonomia/TAREA.md#L19)<br>• [`NOTAS-DE-RELEASE.md#L28`](../../NOTAS-DE-RELEASE.md#L28) | `vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md` |
| `estudios/naval-pm/`<br>*(Contiene scripts de reproducción, inventario y salidas: `inventario.json`, `reproducir_oracle.py`, `probar_juegos.cjs`, `oracle-resultados.txt`, `juegos-resultados.txt`)* | • Referenciado en [`estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md#L15,L22,L31`](../../vault-kb/postmortems/POSTMORTEM-BATALLA-NAVAL-AGY.md#L15) | `vault-kb/postmortems/naval-pm/` |
| `estudios/AUTENTICIDAD-Y-TRANSCRIPCION.md`<br>*(Leído: estudio sobre límites de verificación de ejecuciones pasadas)* | • [`observaciones/README.md#L34`](../../observaciones/README.md#L34)<br>• [`PLAN-0.14-LO-QUE-FALTA.md#L12`](../../vault-kb/planes/PLAN-0.14-LO-QUE-FALTA.md#L12) | `vault-kb/estudios/AUTENTICIDAD-Y-TRANSCRIPCION.md` |
| `estudios/contrastar_autenticidad.py`<br>*(Identificado por referencia; script experimental)* | • Citado en [`estudios/AUTENTICIDAD-Y-TRANSCRIPCION.md#L18`](../../vault-kb/estudios/AUTENTICIDAD-Y-TRANSCRIPCION.md#L18) | `vault-kb/estudios/contrastar_autenticidad.py` |
| `estudios/0.26.0-codex/`<br>*(Identificado por referencia; entorno de contraste independiente: `README`, `CONTRATO`, `lanzar.sh`, `contrastar.py`)* | • Citado en [`tareas/20260915-201030-codex/TAREA.md#L19,L27,L31`](../20260915-201030-codex/TAREA.md#L19)<br>• [`ESPECIFICACION.md#L88`](../../ESPECIFICACION.md#L88) | `vault-kb/estudios/0.26.0-codex/` |
| `estudios/2026-09-10-validacion/`<br>*(Identificado por referencia; contiene `jam-tras-validacion.json`)* | • Citado en [`observaciones/README.md#L38`](../../observaciones/README.md#L38) | `vault-kb/estudios/2026-09-10-validacion/` |
| Resto de entradas en `estudios/`<br>*(64 entradas totales registradas en `TAREA.md#L11`; no leídas individualmente)* | • Bitácora general de investigaciones históricas | `vault-kb/estudios/` |
| **Grupo H: Planes y registros de observación (`observaciones/`)** | | |
| `observaciones/README.md`<br>*(Leído: instructivo para capturar observaciones con `tools/observar.py`)* | • Documenta el uso de `observaciones/aceptacion.plan.json` y `observaciones/jam-aceptacion.plan.json` | `vault-kb/observaciones/README.md` (o `ejemplo/observaciones/`) |
| `observaciones/aceptacion.plan.json`<br>*(Leído: plan de observación de aceptación de Oracle)* | • Referenciado en [`observaciones/README.md#L3`](../../observaciones/README.md#L3) | `vault-kb/observaciones/aceptacion.plan.json` (o `ejemplo/observaciones/`) |
| `observaciones/jam-aceptacion.plan.json`<br>*(Identificado por referencia en `observaciones/README.md#L3`)* | • Referenciado en [`observaciones/README.md#L3`](../../observaciones/README.md#L3) | `vault-kb/observaciones/jam-aceptacion.plan.json` (o `ejemplo/observaciones/`) |
| **Grupo I: Salidas de herramientas y artefactos de compilación** | | |
| `estudio/`<br>*(Salida generada por `tools/estudio.py` para NotebookLM)* | • Salida por omisión de `tools/estudio.py` ([`tools/estudio.py#L405`](../../tools/estudio.py#L405))<br>• Declarado en [`.gitignore#L4`](../../.gitignore#L4) | Ignorado en `.gitignore`; eliminar del árbol Git si estuviera versionado (`git rm -r --cached estudio/`) |
| `build/`<br>*(Artefactos de compilación de setuptools/wheel)* | • Declarado en [`.gitignore#L5`](../../.gitignore#L5)<br>• Señalado en [`TAREA.md#L12,L39`](TAREA.md#L12) | Ignorado en `.gitignore`; eliminar de Git si estuviera versionado (`git rm -r --cached build/`) |
| `*.egg-info/` (`oracle_metalenguaje.egg-info/`)<br>*(Metadatos de empaquetado generados por setuptools)* | • Declarado en [`.gitignore#L7`](../../.gitignore#L7)<br>• Señalado en [`TAREA.md#L12,L39`](TAREA.md#L12) | Ignorado en `.gitignore`; eliminar de Git si estuviera versionado (`git rm -r --cached oracle_metalenguaje.egg-info/`) |
| `dist/`<br>*(Paquetes generados para distribución)* | • Declarado en [`.gitignore#L6`](../../.gitignore#L6) | Ignorado en `.gitignore` |
| **Grupo J: Clientes de editor (`editores/`)** | | |
| `editores/README.md`, `editores/vscode/`, `editores/emacs/`<br>*(Leído `editores/README.md`: clientes livianos que conectan VS Code y Emacs al servidor `oracle-lsp`)* | • [`docs/README.md#L15`](../../docs/README.md#L15) (paso 8 del camino: "El editor")<br>• [`PLAN-IDE.md#L59`](../../vault-kb/planes/PLAN-IDE.md#L59) (plan de implementación LSP)<br>• [`NOTAS-DE-RELEASE.md#L183`](../../NOTAS-DE-RELEASE.md#L183) | **Decisión requerida de Brian**: pueden permanecer como herramientas de soporte del producto (tooling de edición junto a `tools/lsp.py`) o reubicarse si se busca un empaquetado separado. |

---

## 3. Puntos de Acoplamiento Crítico (Rompen la suite si se mueven sin actualizar código)

El análisis del código fuente identificó cuatro dependencias rígidas donde mover archivos rompería inmediatamente tests, herramientas o diagnósticos:

1. **`tools/sintaxis.py` (`DOCUMENTOS_CON_SUPERFICIE`, línea 185):**
   - Declara la tupla fija: `("ESCRIBIR-UNA-MEDIDA.md", "ORACLE-TUTORIAL-PRACTICO.md", "README.md", "ESPECIFICACION.md")`.
   - En líneas 196–202, `verificar_documentos()` comprueba que cada archivo exista en disco relativo a la raíz del repositorio. Si alguno no está, añade una falla: `f"{nombre}: declarado pero no está en el árbol"`.
   - `oracle test` ejecuta `verificar_documentos()` en [`tools/cli.py#L890`](../../tools/cli.py#L890), por lo que mover cualquiera de estos dos archivos sin actualizar `tools/sintaxis.py` pone la suite en **ROJO**.

2. **`tools/mcp_contrato.py` y `tests/test_mcp.py`:**
   - [`tools/mcp_contrato.py#L22`](../../tools/mcp_contrato.py#L22): Lee `RAIZ / "estudios" / "MCP-CONTRATO.md"`.
   - [`tests/test_mcp.py#L208`](../../tests/test_mcp.py#L208): En `test_tools_list_publica_las_tres_con_el_contrato_normativo_entero`, lee textualmente `(mcp.RAIZ / "estudios" / "MCP-CONTRATO.md")` y comprueba que el bloque JSON coincida palabra por palabra con `mcp.HERRAMIENTAS`.
   - Mover `MCP-CONTRATO.md` a `docs/` requiere actualizar ambas rutas simultáneamente.

3. **`tools/estudio.py` (`documento_unico()`, líneas 295–308):**
   - Declara una tupla de tuplas rígida:
     ```python
     declarados = (
         ("09-decision-relaciones-como-bolsas.md", "DECISION-001-RELACIONES-COMO-BOLSAS.md"),
         ("10-decision-sin-composicion.md", "DECISION-002-SIN-COMPOSICION-DE-MEDIDAS.md"),
         ("11-decision-sin-parametros-opcionales.md", "DECISION-003-SIN-PARAMETROS-OPCIONALES-EN-DEFMACRO.md"),
         ("12-plan-de-correccion.md", "PLAN-CORRECCION.md"),
     )
     ```
   - En líneas 302–305, verifica explícitamente `(RAIZ / origen).exists()`. Si falta alguno, levanta `FileNotFoundError("el paquete de estudio declara documentos que no están: ...")`.
   - Además, `como_escribir()` ([línea 78](../../tools/estudio.py#L78)) lee directamente `(RAIZ / "ESCRIBIR-UNA-MEDIDA.md")`.

4. **`tools/mutar.py` (línea 85):**
   - Imprime textualmente `print("... (ver DECISION-011)")` al usuario de consola, un archivo que no viaja en el wheel instalado desde PyPI.

---

## 4. Decisiones que corresponden a Brian

1. **Ubicación de `DECISION-*`:**
   - *Propuesta A (Recomendada en TAREA.md):* Mover a `docs/decisiones/` con un índice (`id`, título, fecha, estado), preservando las citas en código por identificador estable (`DECISION-NNN`) e incorporando un test que asegure que cada ID citado exista en dicho registro.
   - *Propuesta B:* Mover a `vault-kb/decisiones/` como parte de la wiki ordenada.
2. **Desacople de `estudios/MCP-CONTRATO.md`:**
   - Mover a `docs/mcp-contrato.md` como documento normativo del producto. El bloque JSON pasaría a generarse desde `tools.mcp.HERRAMIENTAS` (fuente única de verdad) y `tests/test_mcp.py` comprobaría que el documento esté regenerado.
3. **Destino de guías de autoría (`ESCRIBIR-UNA-MEDIDA.md` y `ORACLE-TUTORIAL-PRACTICO.md`):**
   - Si van a `docs/`, se actualiza `DOCUMENTOS_CON_SUPERFICIE` en `tools/sintaxis.py` y `como_escribir()` en `tools/estudio.py`.
4. **Clientes de editor en `editores/`:**
   - Confirmar si `editores/` se mantiene en el repositorio raíz como tooling de integración con editores (VS Code, Emacs) o si se traslada.
5. **Estructura de `vault-kb/`:**
   - Organizar las carpetas internas de la wiki en:
     - `vault-kb/planes/` (para los `PLAN-*.md`)
     - `vault-kb/estudios/` (para los análisis técnicos de `estudios/`)
     - `vault-kb/postmortems/` (para postmortems como el de batalla naval y sus reproducciones)
     - `vault-kb/observaciones/` (para planes y registros de corridas de observación)
     - `vault-kb/relevos/` (si se conservan los punteros históricos)

---

## Revisión de Claude (2026-09-23)

Contrastado contra el árbol. El mapa de acoplamientos (§3) es correcto y es lo más valioso del
inventario. Hay cuatro correcciones antes de usarlo:

- **Falta `DECISION-012-CADA-MEDIDA-DECLARA-DONDE-OBLIGA.md`.** Son 12 decisiones, no 11.
- **Faltan 12 de los 18 `PLAN-*.md` de la raíz.** No están `0.5.0-AMBITO`, `0.7.0-REPORTAR`,
  `0.8.0-UMBRAL`, `0.8.1-SENSOR`, `0.16.0-TAREAS`, `0.18.0-JUZGAR`, `0.19.0-TQL`, `0.21.0-MUTANTE`,
  `0.22.0-CAMPOS`, `0.26.0-ANTIJUNTA`, `LSP` ni `NIVELES-NEGATIVOS`. Antes de mover alguno hay que
  buscar quién lo cita (`rg -l 'PLAN-0.26.0'`).
- **`observaciones/` no va a `vault-kb/`: es evidencia del corpus.**
  `corpus/meta/494-la-cota-de-la-sombra-observada-por-el-recorrido.caso` la cita, igual que
  `tests/test_observar.py`, `tests/test_receta_observados.py`, `tools/sondear_procedencia.py` y
  `ejemplo/caso-observado/`. Se queda donde está, o se mueve junto con todas esas rutas.
- **`build/`, `dist/`, `estudio/` y `*.egg-info/` no están versionados** (`git ls-files` da 0). Ya
  los ignora `.gitignore`: no hace falta ningún `git rm --cached`.
- **`MCP-CONTRATO.md`: la generación ya existe** (`tools/mcp_contrato.py`, tarea `mcp-tokens`).
  Queda sólo mudarlo a `docs/` y actualizar las dos rutas del §3.2.
