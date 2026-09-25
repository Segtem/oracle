# Las guías de docs/ pueden mostrar comandos u opciones que la CLI no tiene

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle, documentacion, flaqueza


## Qué hacer

Recorrer cada `.md` de `docs/` (no `vault-kb/`) y listar cada comando `oracle …` y cada opción que
muestra. Para cada uno, comprobar contra `tools/cli.py` y los módulos que despacha que existe y hace lo
que la guía dice. Listar los que no existen, cambiaron de nombre o de salida. Con archivo:línea de la
guía y del código. En `HALLAZGOS.md`.

## Avance

La auditoría estática anterior fue descartada porque contenía afirmaciones falsas. Se ejecutaron los comandos de las guías con `python3 tools/cli.py` del checkout en proyectos temporales; las discrepancias confirmadas están en `HALLAZGOS-EJECUTADOS.md`. Se corrigieron sólo las guías y se reemplazó `HALLAZGOS.md` por una referencia al informe ejecutado. No aparecieron defectos del código que requieran una tarea nueva.

Verificaciones: `python3 -m unittest discover -s tests` (2526 tests, OK), `python3 tools/cli.py test --rapido` (VERDE) y `python3 tools/cifras.py --actualizar` (ejecutado al final). `equivalentes.json` no contiene referencias a las líneas movidas de `docs/`.

### Nota (2026-09-25 05:37:24 UTC)

Auditoría ejecutada en proyectos temporales `/tmp/oracle-audit-guias`; fallas comprobadas en `HALLAZGOS-EJECUTADOS.md`, guías corregidas sin tocar código. Suite completa y test rápido en verde; cifras actualizadas.

### Nota de Claude (2026-09-25 03:28:26 UTC)

Los hallazgos 1 y 2 del informe anterior eran falsos; la repetición con shell confirmó esa observación. `oracle escalares` sí informa operadores y agregados.

## Próximo paso

Ninguno pendiente. Si una nueva versión cambia estos comandos, reabrir la tarea con una reproducción ejecutada.
