# El trabajador de escalares se lanza con sys.executable, que en un Python embebido (Unreal) no es Python

- ESTADO: ABIERTA
- PRIORIDAD: 90
- ETIQUETAS: oracle

## Por qué

Lo encontró Jam (tarea `oracle-escalares-embebido`, 2026-09-29): dentro de Unreal, la sombra de
Oracle no evaluaba ningún dominio (`EscalaresInvalidas: el trabajador de escalares emitió datos
inválidos`). `TrabajadorEscalares.iniciar` lanzaba `[sys.executable, "-B", "-m", …]`, y en el Python
embebido de Unreal `sys.executable` es `UnrealEditor` (medido con una sonda). Fuera de un anfitrión
no pasaba nada, por eso ningún test lo veía.

## Criterio de hecho

El intérprete se elige (`ORACLE_PYTHON`, `sys.executable`/`sys._base_executable` si son Python,
`python3` del PATH, o negarse con el remedio); un test de punta a punta con un anfitrión que no es
Python levanta el trabajador real; la mutación del módulo no deja vivos; y en Jam,
`verifica_oracle_shadow.py` en VERDE con todos los dominios evaluados.

### Nota (2026-09-30 00:53:12 UTC)

Verificación del corte 0.36.2 (38c1ed4): oracle test VERDE (2219 tests, 1026/1026 mutantes de medida); mutación de nucleo/aislamiento/escalares.py completo 141/141 (un timeout por carga, re-corrido con más plazo: muere). verificar_instalacion desde clon limpio: WHEEL OK. sha256 wheel f6943411608baae513cb55c2b02bccb6d0027508dd6b5d3a0203537aca987325 · sdist 240bc99b786ca33f7a94b8c55898dd5a4b8a77437f7b6638799715a96ff1f109. Probado sobre Jam antes del pin (wheel local en vendor/, bridge.py fija ORACLE_PYTHON al python3 de Unreal): verifica_oracle_shadow en BotOO TODO VERDE, 24 evaluaciones y 0 'NO EVALUÓ' (antes: ningún dominio evaluaba); Jam oracle test con 0.36.2 las mismas cifras (28/9/3, 1099, 458/458), cobertura 16 en parte, cambios sin errores. Falta: que Brian publique en PyPI.

### Nota (2026-09-30 02:23:43 UTC)

Revisado por Claude: arreglo en nucleo/aislamiento/escalares.py (ORACLE_PYTHON, luego sys.executable o sys._base_executable si son un Python, luego python3 del PATH; si no, error con el remedio). oracle test VERDE, 2219 tests; CI verde en 38c1ed4 y 611b6f5. El wheel de dist/ trae el escalares.py del tag v0.36.2 y, instalado limpio, da oracle cobertura en LyraGASP (10) y Jam (16). Release de GitHub creado. Falta: que Brian suba a PyPI, verificar sha256 y pasar los consumidores.
