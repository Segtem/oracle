# Las guías que no se ejecutan se pudren: docs/02 ya muestra una salida vieja de oracle nueva

- ESTADO: CERRADA
- PRIORIDAD: 82
- ETIQUETAS: oracle, documentacion, flaqueza


## Por qué

2026-09-25. `docs/de-cero.md` se ejecuta entera en un test (`tools/guia.py`) y no puede quedar vieja.
Las demás guías no: la auditoría ejecutada de `guias-cli` corrigió a mano sus salidas, y horas después
`nueva-con-casos` cambió la salida de `oracle nueva` (ahora crea dos casos de andamio) y
`verde-diseno` cambió la de `juzgar`. `docs/02-de-cero-a-un-rojo.md:66` ya muestra la salida vieja.

## Qué hacer

Extender `tools/guia.py` a las guías con recorridos de comandos (`docs/02`, `docs/05`, `docs/07`,
`docs/13`), con la misma convención de bloques (`paso`, `salida`, `archivo=… incluir=…`), y un test
que las ejecute. Convertir los bloques de esas guías a esa convención y completar las salidas con la
corrida real. Si un paso ya no hace lo que dice la prosa (por ejemplo, `oracle nueva` ahora crea casos
de andamio), ajustar la prosa al comportamiento actual.

## Próximo paso

Si cambia un comando o un fixture de estas guías, ejecutar `python3 tools/guia.py` y regenerar sus salidas y el sitio antes de publicar.
