# El repositorio mezcla el motor con relatos, planes y estudios sueltos

- ESTADO: ABIERTA
- PRIORIDAD: 75
- ETIQUETAS: oracle, repo, documentacion


## Lo medido (2026-09-23)

En la raíz hay **40 archivos `.md`** (planes `PLAN-*`, decisiones `DECISION-*`, relevos, relatos,
tutoriales) y carpetas que no son el motor: `estudios/` (64 entradas), `estudio/`, `observaciones/`,
más artefactos de build (`build/`, `oracle_metalenguaje.egg-info/`) que no deberían estar
versionados. Quien entra al repositorio de GitHub no distingue el motor de su bitácora.

Brian (2026-09-23): «dejarlo limpio, sin cosas extras que no sean del motor oracle, y dejar una
carpeta `vault-kb` con todos los relatos y textos sueltos en una wiki ordenada».

## La trampa: hay código que lee esos archivos

No es mover carpetas y listo. Medido con `git grep`: `nucleo/diagnostico.py`, `nucleo/medida.py`,
`nucleo/mutacion.py`, `tools/cli.py`, `tools/estudio.py`, `tools/mutar.py` y varios tests citan
`DECISION-*.md` o `estudios/MCP-CONTRATO.md`. Un test compara el contrato del MCP **palabra por
palabra** con el código. Mover sin mirar rompe la suite y el paquete.

## Qué hacer

1. **Inventario** de todo lo que no es motor, con tres columnas: qué es, quién lo referencia (código,
   tests, README, otros `.md`, tareas) y a dónde va.
2. **Qué es motor y se queda donde está**: `nucleo/`, `catalogos/`, `relaciones/`, `perfiles/`,
   `mutadores/`, `tools/`, `tests/`, `corpus/`, `diferencial/`, `ejemplo/`, `tareas/` (el tracker es
   parte del producto), `README.md`, `LICENSE`, `pyproject.toml`, `ESPECIFICACION.md`,
   `NOTAS-DE-RELEASE.md`. Discutir `DECISION-*`: son normativas y el código las cita; pueden ir a la
   wiki si se actualizan las referencias, o quedarse. Decidir, no suponer.
3. **`vault-kb/` como wiki ordenada** (Obsidian, igual que el de Jam): planes, estudios, relatos,
   relevos viejos, observaciones, postmortems. Con un índice por tema y por fecha, frontmatter y
   enlaces que resuelvan. Reusar las reglas que ya verifica `tools/vault.py` de Jam si sirven.
4. **Actualizar cada referencia** que el inventario encuentre, y agregar un test que falle si
   aparece un `.md` suelto nuevo en la raíz sin estar en la lista de lo que se queda.
5. **Sacar de git lo que es build** (`build/`, `*.egg-info/`) y agregarlo a `.gitignore`.
6. Mover con `git mv`, en commits chicos por tema, para que la historia de cada archivo siga.
7. Suite, `verificar_instalacion`, el tracker y los enlaces del README en verde después de cada paso.

## Diseño: cómo se desacopla el código de los documentos (Claude, 2026-09-23)

Medido con `git grep`: de las ~30 menciones de `DECISION-*` y `estudios/` en código y tests, casi
todas son **citas**, no dependencias. Hay que separar cuatro clases, porque cada una se resuelve
distinto:

1. **Citas por identificador** en comentarios y docstrings («ver DECISION-011», «corrección 6 de
   DECISION-007»). Son sanas: explican el porqué en el lugar del código. No se tocan. Lo único que
   hace falta es que el identificador **sea estable y exista**: un test que junte cada
   `DECISION-NNN` citado en el código y verifique que está en el registro de decisiones. La cita
   apunta a un id, nunca a una ruta, así que mover el archivo no la rompe.
2. **Mensajes que ve el usuario** que citan archivos del repo: `tools/mutar.py` imprime «(ver
   DECISION-011)» a alguien que instaló desde PyPI, donde ese archivo **no existe** (el wheel no
   trae los `.md`). Eso sí es un defecto. Un mensaje al usuario cita una URL absoluta o `oracle
   manual <tema>`, nunca un archivo del repositorio.
3. **Un documento normativo guardado como estudio**: `estudios/MCP-CONTRATO.md` es el contrato del
   producto, y hoy el mismo JSON vive dos veces —en `tools/mcp.py` y en el documento— sincronizado a
   mano y vigilado por un test. Lo óptimo es **una sola fuente**: el código (`HERRAMIENTAS`) es la
   verdad y el bloque del documento se **genera**, igual que `docs/manual.html` sale de
   `oracle manual --html`; el test pasa a comprobar que el documento está regenerado. Y el contrato
   se muda a `docs/`, que es documentación del producto, no bitácora.
4. **Herramientas que leen rutas fijas**: `tools/estudio.py` arma un paquete de estudio con tres
   `DECISION-*` por ruta. Que tome los documentos del registro de decisiones, no de una lista de
   rutas escrita a mano.

**Dónde viven las decisiones.** No en `vault-kb/`: las `DECISION-*` son el porqué del motor, el
código las cita y alguien que evalúa Oracle las necesita. Van a `docs/decisiones/`, con un índice
(id, título, fecha, estado). `vault-kb/` queda para la bitácora: planes cumplidos, estudios, relatos,
relevos viejos, postmortems.

**Los docstrings de tests que dicen «escrita contra `estudios/X/ENCARGO-AGY.md`»** son procedencia;
se actualizan a la ruta nueva dentro de `vault-kb/` al mover, o citan el id de la tarea, que no se
mueve nunca. Mejor lo segundo: la tarea es el identificador estable del trabajo.

## Avance

- 2026-09-23:
  - Se completó el inventario de todo lo que no es motor en [`INVENTARIO.md`](INVENTARIO.md), estructurado en tres columnas: qué es, quién lo referencia (con archivo y línea comprobados) y a dónde va (propuesta para Brian).
  - Se inspeccionaron directamente mediante lectura (`view_file`):
    - Las 11 decisiones normativas (`DECISION-001` a `DECISION-011`).
    - Los 6 planes históricos en raíz (`PLAN-LENGUAJE.md`, `PLAN-CORRECCION.md`, `PLAN-0.3.0.md`, `PLAN-0.6.0-MCP.md`, `PLAN-0.14-LO-QUE-FALTA.md`, `PLAN-IDE.md`).
    - Los 3 punteros de relevo en raíz (`RELEVO.md`, `RELEVO-PARA-CODEX.md`, `RELEVO-2026-09-10.md`).
    - Las guías y tutoriales en raíz (`ESCRIBIR-UNA-MEDIDA.md`, `ORACLE-TUTORIAL-PRACTICO.md`, `ORACLE-PARA-NOTEBOOKLM.md`).
    - El protocolo de agentes en raíz (`AGENTS.md`).
    - Estudios analizados: `estudios/MCP-CONTRATO.md`, `estudios/MCP-FALLAS.md`, `estudios/POSTMORTEM-BATALLA-NAVAL-AGY.md`, `estudios/AUTENTICIDAD-Y-TRANSCRIPCION.md`.
    - Planes de observación: `observaciones/README.md`, `observaciones/aceptacion.plan.json`.
    - Código fuente acoplado a rutas fijas: `tools/sintaxis.py` (`DOCUMENTOS_CON_SUPERFICIE`), `tools/estudio.py` (`documento_unico()` y `como_escribir()`), `tools/mcp_contrato.py` y `tests/test_mcp.py` (`MCP-CONTRATO.md`), `tools/mutar.py` (`DECISION-011`), y comentarios en `nucleo/diagnostico.py`, `nucleo/medida.py`, `nucleo/mutacion.py`, `tools/cli.py`.
  - Se documentaron en detalle los acoplamientos rígidos que romperían la suite si se mueven archivos sin adaptar el código.
  - El trabajo se realizó exclusivamente mediante lectura y edición de archivos; no se ejecutaron comandos de shell, no se hicieron commits y no se afirmaron verificaciones que no fueron corridas en este turno.

## Próximo paso

Revisión del inventario en [INVENTARIO.md](INVENTARIO.md) por Brian para definir:
1. Ubicación de `DECISION-*` (`docs/decisiones/` con índice normativo y test de existencia de IDs vs. `vault-kb/decisiones/`).
2. Aprobación del desacople de `estudios/MCP-CONTRATO.md` hacia `docs/mcp-contrato.md` generado desde `tools.mcp.HERRAMIENTAS`.
3. Destino de `ESCRIBIR-UNA-MEDIDA.md` y `ORACLE-TUTORIAL-PRACTICO.md` (y actualización de `tools/sintaxis.py` y `tools/estudio.py`).
4. Definición sobre `editores/` (permanencia como tooling de integración vs. reubicación).
5. Tras el acuerdo de destinos, ejecutar la mudanza mediante commits temáticos y atómicos con `git mv` en un entorno con permisos de ejecución.
