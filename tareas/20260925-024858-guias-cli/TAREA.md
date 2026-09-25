# Las guías de docs/ pueden mostrar comandos u opciones que la CLI no tiene

- ESTADO: ABIERTA
- PRIORIDAD: 70
- ETIQUETAS: oracle, documentacion, flaqueza


## Qué hacer

Recorrer cada `.md` de `docs/` (no `vault-kb/`) y listar cada comando `oracle …` y cada opción que
muestra. Para cada uno, comprobar contra `tools/cli.py` y los módulos que despacha que existe y hace lo
que la guía dice. Listar los que no existen, cambiaron de nombre o de salida. Con archivo:línea de la
guía y del código. En `HALLAZGOS.md`.

## Próximo paso

La auditoría.
