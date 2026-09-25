# Cada corte tarda horas porque se muta el módulo entero aunque haya cambiado una línea

- ESTADO: CERRADA
- PRIORIDAD: 70
- ETIQUETAS: oracle, mutacion


## Por qué

[la auditoría](../20260924-174258-auditoria/AUDITORIA.md) §2.7: sólo `nucleo/sintaxis.py` tarda cerca de dos horas por corte, y ya hubo cortes por memoria.

## Qué hacer

Un modo de mutación incremental, que muta sólo los sitios de las líneas cambiadas desde el último
tag, para los cortes. La corrida completa se reserva para `--todo`. Sin bajar el criterio de muerte, y
con el informe diciendo qué se mutó y qué no.

**Quién:** Codex.

## Próximo paso

Diseñar cómo se mapean las líneas cambiadas a los sitios de mutación.

### Nota (2026-09-25 12:12:13 UTC)

2026-09-25, Claude con la delegación de Brian: DESCARTADA. Mutar sólo las líneas cambiadas es una ronda parcial, y Brian decidió el 2026-09-24 que la ronda de release es completa (mutacion-lenta, propuesta 4). El costo por mutante se midió y es intrínseco (mutacion-lenta/DESGLOSE.md).
