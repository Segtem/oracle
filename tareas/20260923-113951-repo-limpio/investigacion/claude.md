# Propuesta de Claude (agente nuevo, sin esta conversación)

Recomendaciones, en resumen (texto completo en la conversación del 2026-09-24; aquí lo que decide):

1. **DECISION-\*** → `docs/decisiones/` con índice (convención MADR/adr-tools). Actualizar
   `tools/estudio.py:296-299`, `tools/mutar.py:105` (mensaje «ver DECISION-011» → URL), enlaces de
   README 570-580 y 626, `docs/README.md:13`, `docs/05-por-que-la-mutacion.md:192`,
   `docs/07-conectar-a-un-proyecto-propio.md:280`, ESPECIFICACION y NOTAS-DE-RELEASE. Falta la 012 en
   la tabla del README. Sumar el test de ids citados.
2. **Guías** → `docs/03-escribir-una-medida.md` (la numeración de `docs/`) y `docs/tutorial-practico.md`.
   Actualizar `tools/sintaxis.py:185` (y su comentario de 179), `tools/estudio.py:78` y enlaces.
3. **editores/** se queda (precedente: rust-analyzer `editors/code`). Alternativa: repo aparte como
   `ruff-vscode`, sólo si llega al Marketplace con su propio ciclo.
4. **vault-kb/**: `README.md` (índice), `planes/` (18), `estudios/` (entero, estructura intacta). Sin
   `postmortems/` aparte: mover cambia rutas a cambio de nada. `observaciones/` se queda. Se
   **borran**: los 3 `RELEVO*` (punteros idénticos; la historia de git los conserva) y
   `ORACLE-PARA-NOTEBOOKLM.md` (generado, a `.gitignore`). `estudios/MCP-CONTRATO.md` va a `docs/`.

Hallazgos laterales: el README es la página de PyPI y enlaza con URLs absolutas a `blob/main/…`: la
página de 0.28.0 ya publicada va a dar 404 en lo que se mueva, sin arreglo. `verificar.yml` ignora
`**.md` y `docs/**`: una mudanza de documentos no dispara el CI. `ejemplo/sensor-prosa/diferencial/README.md`
viaja en el wheel y cita `estudios/JEV-COMO-SENSOR.md`. `oracle-estudio` instalado desde PyPI
probablemente no funcione (`RAIZ = parents[1]`), no se ejecutó.
