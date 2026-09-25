# La huella de un directorio de procedencia contaba el estado local de las herramientas, y un fixture recién generado salía vencido en otro checkout

- ESTADO: CERRADA
- PRIORIDAD: 85
- ETIQUETAS: oracle, flaqueza, diferencial

### Nota (2026-09-25 22:16:18 UTC)

2026-09-25: medido al subir Jam a 0.31.0. El fixture vault.json regenerado en un worktree limpio daba DIFERENCIAL verde ahí y vencido en ~/Dev/jam, mismo commit: la fuente de referencia Vault-kb/ es un directorio, y nucleo/diferencial.py lo recorría con rglob incluyendo .obsidian/workspace.json, que Git ignora y Obsidian reescribe al abrir el vault. Arreglo: al recorrer un directorio se ignoran las entradas ocultas y __pycache__; un oculto nombrado a mano como fuente se sigue contando. ESPECIFICACION §6 lo dice; tests/test_huella_estado_local.py falla sin el arreglo. Los fixtures de Oracle no cambian de huella. Consecuencia para consumidores: al subir a la versión con esto, un fixture cuya fuente sea un directorio con archivos ocultos versionados (el .obsidian/*.json de Jam) cambia de huella una vez y hay que regenerarlo.
