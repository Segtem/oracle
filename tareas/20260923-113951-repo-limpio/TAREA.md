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

## Próximo paso

El inventario del punto 1, para revisión de Brian antes de mover nada.
