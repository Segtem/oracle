### 1. Las 12 `DECISION-*.md` de la raíz

- **Recomendación:** Mover a [`docs/decisiones/`](../../../docs) con un índice normativo (`docs/decisiones/README.md`) y un test en la suite que verifique la existencia de cada ID citado en el código.
- **Mejor alternativa:** Dejarlas en la raíz del repositorio.
- **Por qué:** Son Architecture Decision Records (ADRs) vigentes que definen los invariantes del motor (álgebra, bolsas, autoría de mutadores, ámbitos). No viajan en el wheel de PyPI ([`pyproject.toml#L60-L97`](../../../pyproject.toml#L60-L97)), pero son consultadas por evaluadores y enlazadas por [`docs/index.html#L188`](../../../docs/index.html#L188) y [`README.md#L562-L581`](../../../README.md#L562-L581). Moverlas a `vault-kb/` las degradaría erróneamente a notas o bitácora histórica. Ponerlas en `docs/decisiones/` sigue la convención estándar de proyectos Python públicos y despeja la raíz.
- **Qué actualizar para que nada se rompa:**
  1. [`tools/estudio.py#L296-L300`](../../../tools/estudio.py#L296-L300): actualizar las tuplas de `declarados` con `docs/decisiones/...` para evitar `FileNotFoundError` en línea 304.
  2. [`README.md#L570-L581`](../../../README.md#L570-L581): actualizar los enlaces relativos e incorporar la fila de `DECISION-012` (ausente hoy).
  3. [`docs/README.md#L13`](../../../docs/README.md#L13): actualizar el enlace relativo de `DECISION-005` a `decisiones/DECISION-005-...`.
  4. [`tools/mutar.py#L105`](../../../tools/mutar.py#L105): cambiar `(ver DECISION-011)` por una URL a GitHub o tema del manual, ya que el usuario de PyPI no tiene el archivo local.

---

### 2. `ESCRIBIR-UNA-MEDIDA.md` y `ORACLE-TUTORIAL-PRACTICO.md`

- **Recomendación:** Mover ambos a [`docs/`](../../../docs) (`docs/escribir-una-medida.md` y `docs/tutorial-practico.md`).
- **Mejor alternativa:** Mover `ESCRIBIR-UNA-MEDIDA.md` a `docs/` y enviar `ORACLE-TUTORIAL-PRACTICO.md` a `vault-kb/guias/`.
- **Por qué:** Son guías de autoría didácticas para humanos y agentes. Contienen bloques de código ` ```oracle ` que [`tools/sintaxis.py#L185`](../../../tools/sintaxis.py#L185) testea en cada corrida. Mantenerlos en la raíz dispersa la documentación pública (`docs/02-de-cero-a-un-rojo.md`, etc.). Colocarlos en `docs/` unifica todo el material formativo en la carpeta que GitHub Pages y los enlaces de `docs/README.md` estructuran.
- **Qué actualizar para que nada se rompa:**
  1. [`tools/sintaxis.py#L185`](../../../tools/sintaxis.py#L185): cambiar `DOCUMENTOS_CON_SUPERFICIE` por las nuevas rutas relativas. Si no se actualiza, [`tools/sintaxis.py#L201`](../../../tools/sintaxis.py#L201) pone `oracle test` en **ROJO** (`declarado pero no está en el árbol`).
  2. [`tools/estudio.py#L78`](../../../tools/estudio.py#L78): en `como_escribir()`, cambiar `RAIZ / "ESCRIBIR-UNA-MEDIDA.md"` por `RAIZ / "docs" / "escribir-una-medida.md"`.
  3. [`README.md#L596`](../../../README.md#L596) y [`docs/README.md#L9`](../../../docs/README.md#L9): actualizar los enlaces relativos.

---

### 3. `editores/` (clientes VS Code y Emacs)

- **Recomendación:** Mantener [`editores/`](../../../editores) en la raíz del repositorio.
- **Mejor alternativa:** Mover a `tools/editores/`.
- **Por qué:** `oracle-lsp` es un comando oficial expuesto en [`pyproject.toml#L51`](../../../pyproject.toml#L51). Los clientes de `editores/` son su complemento directo y se empaquetan sin npm ni vsce mediante [`editores/vscode/empaquetar.py`](../../../editores/vscode/empaquetar.py) para publicarse en los releases de GitHub. En proyectos con LSP propio (Zig, Ruff, Lean) es convención mantener carpetas de primer nivel para clientes de editor. No viaja en el wheel de PyPI (no está en `packages`). Moverlo a `tools/editores/` ensuciaría el paquete importable Python `oracle_metalenguaje.tools` con JavaScript y Elisp.
- **Qué actualizar para que nada se rompa:**
  - Si se queda en `editores/`: nada; preserva [`docs/README.md#L15`](../../../docs/README.md#L15) y [`editores/README.md`](../../../editores/README.md).
  - Si se mueve a `tools/editores/`: actualizar [`docs/README.md#L15`](../../../docs/README.md#L15) y verificar exclusiones en `pyproject.toml`.

---

### 4. `vault-kb/` (estructura, contenidos y borrados)

- **Recomendación:**
  - **Estructura:** tres subcarpetas: `vault-kb/planes/`, `vault-kb/estudios/` y `vault-kb/postmortems/`.
  - **Qué va ahí:**
    - Los 18 `PLAN-*.md` van a `vault-kb/planes/` (planes históricos ya ejecutados).
    - El contenido de `estudios/` (63 entradas históricas: scripts, validaciones, etc.) va a `vault-kb/estudios/`.
    - `POSTMORTEM-BATALLA-NAVAL-AGY.md` y la carpeta `naval-pm/` van a `vault-kb/postmortems/`.
    - **Excepción crítica:** `estudios/MCP-CONTRATO.md` **NO** va a `vault-kb/`; debe mudarse a `docs/mcp-contrato.md` porque es la especificación normativa del servidor MCP.
    - **`observaciones/` SE QUEDA en la raíz:** no va a `vault-kb/` porque es evidencia del corpus referenciada por `corpus/meta/494-la-cota-de-la-sombra-observada-por-el-recorrido.caso`, `tests/test_observar.py` y `ejemplo/caso-observado/`.
  - **Qué se borra en vez de moverse:**
    - Los 3 relevos sueltos (`RELEVO.md`, `RELEVO-PARA-CODEX.md`, `RELEVO-2026-09-10.md`): son punteros efímeros que contradicen el protocolo de [`AGENTS.md`](../../../AGENTS.md#L19) (*«Nunca dejes el relevo en un .md suelto»*). Se borran con `git rm`.
    - `ORACLE-PARA-NOTEBOOKLM.md`: es un compendio derivado de 16.400 líneas generado a demanda por `tools/estudio.py`. Se elimina de git y se asegura en `.gitignore`.
- **Mejor alternativa:** Mover los 3 `RELEVO*.md` a `vault-kb/relevos/` si se deseara preservación forense estricta.
- **Por qué:** Separa tajantemente el producto vivo de su bitácora. La wiki aloja la memoria técnica para agentes y mantenedores, sin mezclar contratos vigentes ni fixtures de prueba.
- **Qué actualizar para que nada se rompa:**
  1. [`tools/estudio.py#L300`](../../../tools/estudio.py#L300): actualizar `PLAN-CORRECCION.md` a `vault-kb/planes/PLAN-CORRECCION.md`.
  2. [`README.md#L34,L560,L588`](../../../README.md): actualizar los enlaces a `PLAN-LENGUAJE.md`, `PLAN-CORRECCION.md` y cambiar `estudios/MCP-CONTRATO.md` por `docs/mcp-contrato.md`.
  3. [`tools/mcp_contrato.py#L26`](../../../tools/mcp_contrato.py#L26) y [`tests/test_mcp.py#L208`](../../../tests/test_mcp.py#L208): cambiar la ruta fija `estudios/MCP-CONTRATO.md` a `docs/mcp-contrato.md`.
