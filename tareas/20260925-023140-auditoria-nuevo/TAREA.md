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

## Avance

Auditoría completada y documentada en `HALLAZGOS.md`. Se realizó la inspección estática del recorrido de un usuario nuevo (humano o LLM) instalando desde PyPI (`oracle-metalenguaje`), analizando el código (`tools/cli.py`, `tools/medida.py`, `tools/corpus.py`, `tools/juzgar.py`, `tools/tareas.py`, `tools/manual.py`, `nucleo/proyecto.py`, `nucleo/sintaxis.py`, `nucleo/vocabulario.py`) y la documentación (`docs/02-de-cero-a-un-rojo.md`, `docs/03-escribir-una-medida.md`, `docs/13-primer-valor.md`).

Se detectaron 15 hallazgos con archivo:línea y su arreglo mínimo:
1. `tools/cli.py:125`: `oracle --help` omite `oracle manual`.
2. `tools/cli.py:119, 186`: `oracle --help` y `oracle proyecto --help` omiten `oracle contexto`.
3. `tools/cli.py:116`: `oracle medida` omite el subcomando `probar` en la ayuda general.
4. `tools/cli.py:1085`: `oracle test --help` ejecuta la suite de tests en vez de mostrar ayuda.
5. `tools/cli.py:591-593`: `oracle init` sugiere crear medida antes que el caso, violando la regla metodológica y provocando rojo en `oracle test`.
6. `tools/cli.py:566`: `oracle init` no crea la carpeta `relaciones/` requerida por `docs/02`.
7. `nucleo/proyecto.py:658-660`: error críptico sobre "autocertificación" al invocar `test` o `juzgar` fuera de un proyecto.
8. `docs/02-de-cero-a-un-rojo.md:71-84`: plantilla desincronizada (omite `ambito AMBITO` obligatorio y desfasa número de línea de error de `segun`).
9. `tools/medida.py:287`: mensaje de `oracle medida nueva` omite alertar sobre `SEGUN` y `AMBITO`.
10. `tools/manual.py:40-47`: `oracle manual ambito` arroja tema desconocido pese a ser un vocabulario cerrado obligatorio.
11. `docs/03-escribir-una-medida.md:105-106`: remite a scripts de desarrollo inexistentes en PyPI (`tools/sintaxis.py`) en vez de `oracle convertir`.
12. `tools/corpus.py:59`: `# procedencia:` comentado en plantilla de caso provoca casos `"sin_declarar"` y fallas en medidas meta.
13. `tools/corpus.py:163`: `oracle caso nuevo` no orienta sobre la polaridad de etiquetas ni sugiere `oracle manual etiqueta`.
14. `tools/juzgar.py:264-266`: `oracle juzgar` no informa qué relaciones espera el catálogo cuando no hay medidas aplicables.
15. `tools/tareas.py:58-63`: errores de argumentos en subcomandos de `oracle tarea` se emiten en inglés por delegación directa a `argparse`.

## Próximo paso

Revisión humana de `HALLAZGOS.md` y priorización para la implementación de las correcciones mínimas en código y documentación, iniciando por las inconsistencias de mayor fricción (plantilla de `docs/02`, soporte de `ambito` en `manual.py`, ayuda en `oracle test` y mensaje de proyecto ausente en `nucleo/proyecto.py`).

### Nota (2026-09-25 02:46:54 UTC)

2026-09-25, Claude, verificado ejecutando la CLI: CIERTOS 1 y 2 (oracle --help no menciona manual ni contexto), 4 (oracle test --help NO muestra ayuda: corre la verificación), 6 (init no crea relaciones/), 7 (instalado desde PyPI, oracle test fuera de un proyecto dice «esta instalación no incluye el proyecto de autocertificación», que no le dice nada a quien llega), 9 (medida nueva omite SEGUN y AMBITO en su instrucción) y 10 (no hay tema manual ambito). FALSO en 8: los valores de ambito que cita (unidad, integracion, sistema, contrato, aceptacion) no existen; son universal y del_origen, y la plantilla ya los muestra en un comentario. El resto (3, 5, 11–15) no se verificó; se comprueba antes de implementar.
