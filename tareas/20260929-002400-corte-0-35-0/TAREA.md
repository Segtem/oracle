# corte 0.35.0

- ESTADO: CERRADA
- PRIORIDAD: 90
- ETIQUETAS: oracle

### Nota (2026-09-29 00:27:12 UTC)

Build desde clon limpio (uv build) y verificar_instalacion OK. sha256 wheel ed3f0a763c014ab4c26b5f2b07cae1fdb7ec9080cc215124c09f1b3628cf181d · sdist 92aa495c155bdb4b46aa1c53cc7ee1fd0bfc2428fe0581e3f7c18e1662181460. Mutación del corte: nueve módulos, 1400 mutantes, sin sobrevivientes, tres equivalentes declarados. oracle test VERDE, 2168 tests.

### Nota (2026-09-29 00:43:42 UTC)

Publicado en PyPI por Brian; sha256 del wheel y del sdist coinciden con los locales. Instalación limpia desde PyPI: oracle 0.35.0 (sintaxis 1.1), oracle cobertura y oracle test VERDE sobre el experimento de OpenSpec. Consumidores medidos antes de subir el pin, mismas cifras que con 0.34.0: LyraGASP a0fd5ff (78/116, 580, 487/487, suite 151; el commit del pin d3406ad salió sin ID por un sufijo mal tipeado, explicado en su done), Jam 171eb51 (28/4/3, 1099, 448/448, suite 1428), commander 92e7705 (sin medidas propias). Herramienta global 0.35.0 con trackertast 0.1.0. oracle-mcp sigue fijando 0.34.0 en su propio entorno.
