# Encargo para agy — el MCP de Oracle al día (0.27.0)

Tarea: [`20260916-210604-mcp-027`](../../tareas/20260916-210604-mcp-027/TAREA.md). Leé la tarea
entera, `estudios/MCP-CONTRATO.md`, `tools/mcp.py`, `tools/juzgar.py`, `tests/test_mcp.py` y
`tests/test_juzgar_cota_y_ausentes.py` antes de tocar nada.

Trabajás en **este directorio** (un worktree de la rama `v027`). Nada fuera de él.

## Reglas

- Sólo herramientas de lectura y edición. **NO shell, NO tests, NO subagentes, NO red, NO commits.**
- No edites tests existentes: si uno contradice lo que pide este encargo, anotalo en el informe.
- Tests nuevos, sí: `tests/test_mcp_027.py`. Usá sólo APIs que hayas leído en el código; no inventes
  nombres.
- Escribí `estudios/0.27.0-mcp/AVANCE-AGY.md` a medida que avanzás y, al final,
  `estudios/0.27.0-mcp/INFORME-AGY.md` con lo hecho, las decisiones y las contradicciones, sin
  afirmar verificaciones que no corriste.

## Contexto

`oracle-mcp` publica tres herramientas de sólo lectura. Su contrato normativo es
`estudios/MCP-CONTRATO.md`: el bloque JSON entre `<!-- herramientas-json:inicio -->` y
`<!-- herramientas-json:fin -->` tiene que ser **idéntico** a `HERRAMIENTAS` de `tools/mcp.py` (un
test lo compara). Toda herramienta nueva o cambiada va en los dos lugares, y el contrato explica su
porqué en prosa, como las otras tres.

El contrato se llama «consultar, evaluar y falsar sin escribir» y así sigue: **todo lo nuevo es de
sólo lectura** (`readOnlyHint: true`, `destructiveHint: false`, `idempotentHint: true`,
`openWorldHint: false`) y no escribe ningún archivo.

## Lo que hay que hacer

### 1. `oracle_evaluar` sabe de sombras

El resultado gana una clave obligatoria `sombra`: `null` si la medida no está en sombra en el
`oracle.json` del proyecto; si lo está,
`{"desde": str, "porque": str, "cota": int | null, "perdona": bool}`. `perdona` es verdadero sólo si
la medida dio rojo y la sombra lo perdona: sin cota, siempre; con cota, sólo si el valor es un número
y no la supera. Es la misma regla que `Informe.supera_su_cota` en `nucleo/medida.py` — **reusala**,
no la copies. Una medida evaluada por texto (`formato`) nunca está en sombra: `sombra` es `null`.

`estado` no cambia (sigue siendo `verde`, `rojo` o `sin_evidencia`): la sombra no cambia lo que la
medida vio, cambia la consecuencia. El esquema pasa a `oracle.mcp/evaluacion/v2`.

### 2. Una herramienta nueva: `oracle_juzgar`

Lo mismo que `oracle juzgar --con`, sobre una evidencia pasada por valor.

- Entrada: `{"evidencia": {...}, "ids": [..]}`; `ids` es opcional, con el mismo patrón de id que
  `oracle_evaluar`, sin repetidos.
- Salida, esquema `oracle.mcp/juzgar/v1`:
  `esquema`, `oracle_version`, `proyecto`, `entrada_sha256`, `ok` (bool), `medidas` (lista de
  `{id, estado, valor, umbral, sombra, testigos, testigos_omitidos, alcance}`, con `estado`,
  `sombra` y el tope de testigos iguales a `oracle_evaluar`), `no_aplicadas` (lista de
  `{id, faltan}`), `no_juzgaron` (lista de `{id, motivo}`) y `advertencias`.
- Mismas reglas que el CLI: catálogo **efectivo**, sombras y cotas de `oracle.json`, las no
  aplicadas sólo del catálogo propio; `ok` falso si ninguna medida aplica (con una advertencia que
  lo diga), y si un id pedido no existe o no aplica, error como `oracle_evaluar` con un id ausente.
- **No dupliques la lógica de `tools/juzgar.py`.** Extraé de `cmd_juzgar` una función
  `juzgar_evidencia(proy, evidencia, ids=()) -> Informe` (con las sombras, las cotas y
  `no_aplicadas` ya puestas) que usen el CLI y el MCP. El CLI tiene que seguir dando exactamente la
  misma salida y los mismos códigos: `tests/test_juzgar*.py` no se tocan.
- Con la misma estabilidad que `oracle_evaluar` ante un proyecto que cambia durante la llamada
  (`_evaluacion_estable`).

### 3. Una herramienta nueva: `oracle_tareas` (sólo lectura)

Para que un agente sin shell lea el tracker del proyecto (`tareas/`).

- Entrada: `{"accion": "listar" | "ver" | "buscar" | "hechos", ...}`:
  - `listar`: opcional `estado` (`"ABIERTA"` o `"CERRADA"`) y `etiqueta`;
  - `ver`: `id` obligatorio (un id o un prefijo único, como el CLI);
  - `buscar`: `texto` obligatorio;
  - `hechos`: opcional `git` (bool, por omisión `false`): las relaciones de `oracle tarea hechos`.
- Salida, esquema `oracle.mcp/tareas/v1`: `esquema`, `oracle_version`, `proyecto`, `accion` y
  `resultado`, con la misma información que el `--json` del verbo del CLI correspondiente.
  Reusá las funciones de `tools/tareas*.py`; si un verbo sólo existe como `cmd_*` que imprime,
  extraé la parte que calcula y dejá que el `cmd_*` la use, sin cambiar su salida.
- Un proyecto sin `tareas/` da un error `TRACKER_AUSENTE`, no una lista vacía.
- **Nada que escriba**: ni `nueva`, ni `anotar`, ni `cerrar`, ni `etiquetar`. El contrato dice por
  qué: una tarea creada o cerrada sin su commit deja el tracker en rojo, y el commit no se hace por
  MCP.

### 4. Tests y documentos

- `tests/test_mcp_027.py`: las tres cosas de arriba, con las dos ramas de cada regla (en sombra y
  no, dentro y fuera de la cota, con y sin `ids`, cada acción de `oracle_tareas`, tracker ausente).
- `estudios/MCP-CONTRATO.md`: el bloque JSON y la prosa de lo nuevo.
- `README.md`: la sección del MCP nombra las cinco herramientas.

## Lo que no hace falta

- No toques `nucleo/`: todo lo que necesitás ya está (`Informe`, `no_aplicadas`,
  `cotas_de_sombra`).
- No subas versiones ni escribas notas de release: eso lo hace Claude.
