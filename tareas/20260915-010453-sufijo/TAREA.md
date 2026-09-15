# tarea nueva no arma un sufijo largo con el título

- ESTADO: ABIERTA
- PRIORIDAD: 40
- ETIQUETAS: oracle, bug

Sin `--sufijo`, `oracle tarea nueva` deriva el sufijo del título (hasta 40 caracteres): la tarea de 0.18.0 salió `20260915-010206-juzgar-evidencia-real-desde-el-cli-0-18` y hubo que rehacer dos commits. En tatr el ID es fecha-hora con un sufijo corto opcional. Decidir el comportamiento por defecto (sin sufijo, o uno corto) y cambiar el contrato de `docs/12-tareas.md` con sus tests.
