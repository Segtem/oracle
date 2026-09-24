# Corte 0.30.0

- ESTADO: CERRADA
- PRIORIDAD: 90
- ETIQUETAS: oracle, release


Cortar 0.30.0 con lo cerrado desde 0.29.0: `aritmetica` (sintaxis 0.7: `a + 1`, `t1.turno-1`),
`repo-limpio` (el repo queda en el motor: `docs/decisiones/`, `vault-kb/`) y `web-028` (la web al
día; se une a `main` junto con el corte para que la página y PyPI salgan juntas). Mutación de lo
tocado, notas, crónica, cifras al final, build limpio, tag y release; Brian sube a PyPI. Después,
los consumidores (LyraGASP, Jam, commander) directo a 0.30.0, medidos antes de cambiar el número.

## Próximo paso

Brian sube a PyPI con `uvx twine upload dist/oracle_metalenguaje-0.30.0*`; Claude verifica y sube los consumidores.

### Nota (2026-09-24 19:13:28 UTC)

2026-09-24: cortado. Tag v0.30.0 y release https://github.com/Segtem/oracle/releases/tag/v0.30.0, wheel bc424bb2… y sdist 862eafdf…, build en worktree limpio, verificar_instalacion WHEEL OK. La web se publicó con el push. Falta que Brian suba a PyPI; después los consumidores.
