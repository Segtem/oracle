# Auditoría: qué traba a quien llega nuevo a Oracle desde PyPI, humano o LLM

- ESTADO: ABIERTA
- PRIORIDAD: 80
- ETIQUETAS: oracle, auditoria, flaqueza


## Qué hacer

Brian (2026-09-24): «terminar con una mejor versión de Oracle sin puntos flojos». Leer Oracle como
alguien que lo instala desde PyPI sin conocerlo —un humano o un LLM— y recorrer lo que haría:
`oracle --help`, `oracle init`, escribir la primera medida (`docs/02-de-cero-a-un-rojo.md`,
`docs/03-escribir-una-medida.md`, `docs/13-primer-valor.md`), el primer caso, `oracle test`, `oracle
juzgar`, el tracker. Listar cada lugar donde se trabaría: un mensaje de error que no dice qué hacer,
un paso de la guía que no coincide con el código, un término sin explicar, una opción que falta en la
ayuda. Cada hallazgo con archivo:línea y la forma más chica de arreglarlo. En `HALLAZGOS.md`.

## Próximo paso

La auditoría.
