# Auditoría: dónde puede quedar todavía un falso verde en el núcleo

- ESTADO: ABIERTA
- PRIORIDAD: 85
- ETIQUETAS: oracle, auditoria, flaqueza


## Qué hacer

Brian (2026-09-24): «sin puntos flojos». El álgebra 1.0 (tarea `algebra-10`) cierra cuatro falsos
verdes: predicados no booleanos, `null`, claves no validadas y testigos. Buscar los que quedan, en
`nucleo/` (álgebra, medida, proyecto, sintaxis, caso, relación) y en `tools/juzgar.py` y
`tools/aceptacion.py`: todo camino en que una medida, un caso o un proyecto puedan salir VERDE sin
haber medido lo que dicen medir. Por ejemplo: una excepción capturada que se vuelve verde, un valor
por omisión que pasa por medición, una relación vacía sin `requiere`, una comparación que coacciona
tipos. Cada hallazgo con archivo:línea, la entrada concreta que lo dispara y si ya lo cubre un test o
una medida meta. Descartar lo que no se pueda sostener con cita. En `HALLAZGOS.md`.

## Próximo paso

La auditoría.
