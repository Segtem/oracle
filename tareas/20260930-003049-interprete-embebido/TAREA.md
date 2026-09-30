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
