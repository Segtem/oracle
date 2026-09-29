# oracle cobertura y oracle cambios revientan en un proyecto con escalares propias

- ESTADO: ABIERTA
- PRIORIDAD: 90
- ETIQUETAS: oracle

### Nota (2026-09-29 19:09:50 UTC)

Encontrado el 2026-09-29 al adoptar requisitos en LyraGASP: oracle cobertura --proyecto medidas termina en una traza (MedidaMalDeclarada: «es_propiedad_bloqueo_directo» no es … escalar declarada) porque carga el catálogo sin registrar medidas/escalares.py, y no acepta --confiar-escalares. tools/cambios.py carga igual. El experimento de OpenSpec no tenía escalares propias, por eso no apareció. Los dos consumidores reales (LyraGASP y Jam) las tienen.

### Nota (2026-09-29 19:44:24 UTC)

Arreglado: tools/cobertura.py y tools/cambios.py registran las escalares del proyecto con escalares_del_proyecto y aceptan --confiar-escalares; sin la bandera y con escalares.py cortan con «ESCALARES EXTERNAS NO EJECUTADAS — … repetí con --confiar-escalares» y salen con 1, como los demás comandos. Probado sobre LyraGASP: 10 requisitos, 1 medido y 9 en parte. Tests nuevos con un proyecto con escalares propias. Mutación completa: cobertura 20/20, cambios 56/56 (+1 eq), cli 761/761 (+1 eq). oracle test VERDE, 2207 tests. Sale en 0.36.1.
